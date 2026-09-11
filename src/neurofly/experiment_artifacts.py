"""Portable, integrity-checked artifacts for completed Phase 3A runs.

Artifacts are deliberately transparent UTF-8 JSON/JSONL files.  This module
only serializes and validates :mod:`neurofly.experiments` output; it does not
rerun a stimulus, encoder, graph builder, or simulator while loading.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any

from neurofly.experiments import (
    VALIDATION_STATUS_NOT_EVALUATED,
    BodyTelemetry,
    ExperimentConfig,
    ExperimentError,
    ExperimentResult,
    ExperimentRunner,
    PopulationSpikeSummary,
    TelemetrySpec,
)
from neurofly.malecns.sensory import LoomingSample, LoomingStimulus, VisualPoint
from neurofly.simulation import DeliveredSynapticEvent, SpikeEvent

ARTIFACT_SCHEMA_VERSION = "experiment_artifact_v1"
TELEMETRY_FILE_SCHEMA = "experiment_telemetry_v1"
SPIKE_EVENT_SCHEMA = "experiment_spike_event_v1"
DELIVERED_EVENT_SCHEMA = "experiment_delivered_event_v1"
SUMMARY_FILE_SCHEMA = "experiment_summary_v1"
MANIFEST_SCHEMA_VERSION = "experiment_artifact_manifest_v1"

MANIFEST_FILENAME = "manifest.json"
TELEMETRY_FILENAME = "telemetry.json"
SPIKES_FILENAME = "spikes.jsonl"
DELIVERED_EVENTS_FILENAME = "delivered_events.jsonl"
SUMMARY_FILENAME = "summary.json"
_PAYLOAD_FILENAMES = (
    TELEMETRY_FILENAME,
    SPIKES_FILENAME,
    DELIVERED_EVENTS_FILENAME,
    SUMMARY_FILENAME,
)
_EXPECTED_DNP01_IDS = frozenset({10001, 10010})


class ExperimentArtifactError(RuntimeError):
    """Base error for portable experiment-artifact operations."""


class ArtifactSchemaError(ExperimentArtifactError):
    """The artifact schema or one of its records is invalid."""


class ArtifactIntegrityError(ExperimentArtifactError):
    """A required artifact file or manifest digest does not validate."""


class ArtifactExportError(ExperimentArtifactError):
    """An artifact could not be finalized atomically."""


class ArtifactReplayError(ExperimentArtifactError):
    """A persisted artifact could not be reproduced exactly."""


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value}")


def _json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ArtifactSchemaError("value is not deterministic JSON") from exc


def _sha256_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ArtifactIntegrityError(
            f"could not read artifact file {path.name}"
        ) from exc
    return digest.hexdigest()


def _identifier(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ArtifactSchemaError(f"{field_name} must be a non-empty string.")
    return value


def _sha256_identifier(value: Any, field_name: str) -> str:
    _identifier(value, field_name)
    if len(value) != 64:
        raise ArtifactSchemaError(f"{field_name} must be a SHA-256 hex digest.")
    try:
        int(value, 16)
    except ValueError:
        raise ArtifactSchemaError(
            f"{field_name} must be a SHA-256 hex digest."
        ) from None
    return value


def _finite(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise ArtifactSchemaError(f"{field_name} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ArtifactSchemaError(f"{field_name} must be finite.") from None
    if not math.isfinite(result):
        raise ArtifactSchemaError(f"{field_name} must be finite.")
    return result


def _required_keys(record: dict[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - record.keys())
    unexpected = sorted(record.keys() - expected)
    if missing or unexpected:
        raise ArtifactSchemaError(
            f"invalid {label} fields: missing={missing!r}, unexpected={unexpected!r}"
        )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), parse_constant=_reject_json_constant
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise ArtifactIntegrityError(f"malformed {label}: {exc}") from None
    if not isinstance(value, dict):
        raise ArtifactSchemaError(f"{label} must be a JSON object.")
    return value


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    raise ArtifactIntegrityError(
                        f"blank line in {label} at line {line_number}"
                    )
                try:
                    value = json.loads(line, parse_constant=_reject_json_constant)
                except (json.JSONDecodeError, ValueError) as exc:
                    raise ArtifactIntegrityError(
                        f"malformed {label} at line {line_number}: {exc}"
                    ) from None
                if not isinstance(value, dict):
                    raise ArtifactSchemaError(
                        f"{label} line {line_number} must be an object."
                    )
                records.append(value)
    except (OSError, UnicodeError) as exc:
        raise ArtifactIntegrityError(f"could not read {label}: {exc}") from None
    return records


def _write_bytes(path: Path, value: bytes) -> str:
    try:
        with path.open("wb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise ArtifactExportError(f"could not write {path.name}") from exc
    return _sha256_bytes(value)


def _write_json(path: Path, value: Any) -> str:
    return _write_bytes(path, _json_bytes(value) + b"\n")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> str:
    payload = b"".join(_json_bytes(record) + b"\n" for record in records)
    return _write_bytes(path, payload)


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _reject_credentials(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True)
    if "NEUPRINT_APPLICATION_CREDENTIALS" in text:
        raise ArtifactSchemaError("artifact must not contain neuPrint credentials.")


def _as_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ArtifactSchemaError(f"{field_name} must be an integer.")
    return value


def _as_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ArtifactSchemaError(f"{field_name} must be boolean.")
    return value


def _sample_to_dict(sample: LoomingSample) -> dict[str, Any]:
    return sample.to_dict()


def _sample_from_dict(value: Any) -> LoomingSample:
    if not isinstance(value, dict):
        raise ArtifactSchemaError("stimulus samples must be objects.")
    expected = {
        "time_s",
        "distance_m",
        "time_to_collision_s",
        "angular_size_rad",
        "angular_expansion_velocity_rad_s",
        "center",
        "approaching",
        "collided",
    }
    _required_keys(value, expected, "stimulus sample")
    center = value["center"]
    if not isinstance(center, dict):
        raise ArtifactSchemaError("stimulus sample center must be an object.")
    _required_keys(center, {"azimuth_rad", "elevation_rad"}, "sample center")
    try:
        time_s = _finite(value["time_s"], "sample.time_s")
        distance_m = _finite(value["distance_m"], "sample.distance_m")
        collision_s = (
            None
            if value["time_to_collision_s"] is None
            else _finite(value["time_to_collision_s"], "sample.time_to_collision_s")
        )
        angular_size = _finite(value["angular_size_rad"], "sample.angular_size_rad")
        expansion = (
            None
            if value["angular_expansion_velocity_rad_s"] is None
            else _finite(
                value["angular_expansion_velocity_rad_s"],
                "sample.angular_expansion_velocity_rad_s",
            )
        )
        azimuth = _finite(center["azimuth_rad"], "center.azimuth_rad")
        elevation = _finite(center["elevation_rad"], "center.elevation_rad")
        return LoomingSample(
            time_s=value["time_s"] if isinstance(value["time_s"], int) else time_s,
            distance_m=(
                value["distance_m"]
                if isinstance(value["distance_m"], int)
                else distance_m
            ),
            time_to_collision_s=(
                value["time_to_collision_s"]
                if isinstance(value["time_to_collision_s"], int)
                else collision_s
            ),
            angular_size_rad=(
                value["angular_size_rad"]
                if isinstance(value["angular_size_rad"], int)
                else angular_size
            ),
            angular_expansion_velocity_rad_s=(
                value["angular_expansion_velocity_rad_s"]
                if isinstance(value["angular_expansion_velocity_rad_s"], int)
                else expansion
            ),
            center=VisualPoint(
                azimuth_rad=(
                    center["azimuth_rad"]
                    if isinstance(center["azimuth_rad"], int)
                    else azimuth
                ),
                elevation_rad=(
                    center["elevation_rad"]
                    if isinstance(center["elevation_rad"], int)
                    else elevation
                ),
            ),
            approaching=_as_bool(value["approaching"], "sample.approaching"),
            collided=_as_bool(value["collided"], "sample.collided"),
        )
    except (TypeError, ValueError, RuntimeError) as exc:
        raise ArtifactSchemaError(f"invalid stimulus sample: {exc}") from None


def _stimulus_from_dict(value: Any) -> LoomingStimulus:
    if not isinstance(value, dict):
        raise ArtifactSchemaError("config stimulus must be an object.")
    _required_keys(
        value,
        {"object_radius_m", "approach_velocity_m_s", "initial_distance_m", "center"},
        "config stimulus",
    )
    center = value["center"]
    if not isinstance(center, dict):
        raise ArtifactSchemaError("config stimulus center must be an object.")
    _required_keys(center, {"azimuth_rad", "elevation_rad"}, "config center")
    try:
        object_radius = _finite(value["object_radius_m"], "object_radius_m")
        velocity = _finite(value["approach_velocity_m_s"], "approach_velocity_m_s")
        initial_distance = _finite(value["initial_distance_m"], "initial_distance_m")
        azimuth = _finite(center["azimuth_rad"], "azimuth_rad")
        elevation = _finite(center["elevation_rad"], "elevation_rad")
        return LoomingStimulus(
            object_radius_m=(
                value["object_radius_m"]
                if isinstance(value["object_radius_m"], int)
                else object_radius
            ),
            approach_velocity_m_s=(
                value["approach_velocity_m_s"]
                if isinstance(value["approach_velocity_m_s"], int)
                else velocity
            ),
            initial_distance_m=(
                value["initial_distance_m"]
                if isinstance(value["initial_distance_m"], int)
                else initial_distance
            ),
            center=VisualPoint(
                azimuth_rad=(
                    center["azimuth_rad"]
                    if isinstance(center["azimuth_rad"], int)
                    else azimuth
                ),
                elevation_rad=(
                    center["elevation_rad"]
                    if isinstance(center["elevation_rad"], int)
                    else elevation
                ),
            ),
        )
    except (TypeError, ValueError, RuntimeError) as exc:
        raise ArtifactSchemaError(f"invalid config stimulus: {exc}") from None


def _encoder_from_dict(value: Any):
    from neurofly.sensory_encoder import LevelPEncoderConfig

    if not isinstance(value, dict):
        raise ArtifactSchemaError("config encoder must be an object.")
    expected = {
        "encoder_id",
        "encoder_version",
        "lc4_gain_mv_eq",
        "lplc2_gain_mv_eq",
        "omega_half_rad_per_s",
        "theta_half_rad",
        "normalization_policy",
        "baseline_policy",
        "negative_feature_policy",
        "population_policy",
        "laterality_policy",
        "latency_policy",
        "filter_policy",
        "stochastic_policy",
    }
    _required_keys(value, expected, "config encoder")
    try:
        return LevelPEncoderConfig(
            encoder_id=value["encoder_id"],
            encoder_version=value["encoder_version"],
            lc4_gain_mv_eq=_finite(value["lc4_gain_mv_eq"], "lc4_gain_mv_eq"),
            lplc2_gain_mv_eq=_finite(value["lplc2_gain_mv_eq"], "lplc2_gain_mv_eq"),
            omega_half_rad_per_s=_finite(
                value["omega_half_rad_per_s"], "omega_half_rad_per_s"
            ),
            theta_half_rad=_finite(value["theta_half_rad"], "theta_half_rad"),
            normalization_policy=value["normalization_policy"],
            baseline_policy=value["baseline_policy"],
            negative_feature_policy=value["negative_feature_policy"],
            population_policy=value["population_policy"],
            laterality_policy=value["laterality_policy"],
            latency_policy=value["latency_policy"],
            filter_policy=value["filter_policy"],
            stochastic_policy=value["stochastic_policy"],
        )
    except (TypeError, ValueError, RuntimeError) as exc:
        raise ArtifactSchemaError(f"invalid config encoder: {exc}") from None


def _lif_from_dict(value: Any):
    from neurofly.simulation import LIFConfig

    if not isinstance(value, dict):
        raise ArtifactSchemaError("config neural model must be an object.")
    expected = {
        "model_id",
        "model_version",
        "graph_scope_id",
        "sign_policy_id",
        "external_drive_semantics",
        "input_drive_provenance_id",
        "baseline_policy",
        "stochastic_policy",
        "dt_ms",
        "tau_m_ms",
        "tau_s_ms",
        "rest_mv",
        "reset_mv",
        "threshold_mv",
        "refractory_ms",
        "delay_ms",
        "delay_steps",
        "refractory_steps",
        "k_syn_mv_per_contact",
    }
    _required_keys(value, expected, "config neural model")
    try:
        config = LIFConfig(
            model_id=value["model_id"],
            model_version=value["model_version"],
            graph_scope_id=value["graph_scope_id"],
            sign_policy_id=value["sign_policy_id"],
            external_drive_semantics=value["external_drive_semantics"],
            input_drive_provenance_id=value["input_drive_provenance_id"],
            baseline_policy=value["baseline_policy"],
            stochastic_policy=value["stochastic_policy"],
            dt_ms=_finite(value["dt_ms"], "dt_ms"),
            tau_m_ms=_finite(value["tau_m_ms"], "tau_m_ms"),
            tau_s_ms=_finite(value["tau_s_ms"], "tau_s_ms"),
            rest_mv=_finite(value["rest_mv"], "rest_mv"),
            reset_mv=_finite(value["reset_mv"], "reset_mv"),
            threshold_mv=_finite(value["threshold_mv"], "threshold_mv"),
            refractory_ms=_finite(value["refractory_ms"], "refractory_ms"),
            delay_ms=_finite(value["delay_ms"], "delay_ms"),
            k_syn_mv_per_contact=_finite(
                value["k_syn_mv_per_contact"], "k_syn_mv_per_contact"
            ),
        )
    except (TypeError, ValueError, RuntimeError) as exc:
        raise ArtifactSchemaError(f"invalid config neural model: {exc}") from None
    if (
        value["delay_steps"] != config.delay_steps
        or value["refractory_steps"] != config.refractory_steps
    ):
        raise ArtifactSchemaError("neural step counts do not match neural timings.")
    return config


def _telemetry_spec_from_dict(value: Any) -> TelemetrySpec:
    if not isinstance(value, dict):
        raise ArtifactSchemaError("config telemetry must be an object.")
    expected = {"profile_id", "selected_visual_body_ids", "includes"}
    _required_keys(value, expected, "config telemetry")
    includes = value["includes"]
    if not isinstance(includes, dict):
        raise ArtifactSchemaError("config telemetry includes must be an object.")
    _required_keys(
        includes,
        {
            "stimulus_features",
            "encoder_drives",
            "population_spike_summaries",
            "dnp01_state",
            "spike_events",
            "delivered_event_summaries",
        },
        "telemetry includes",
    )
    if not all(
        _as_bool(item, f"telemetry includes {key}") for key, item in includes.items()
    ):
        raise ArtifactSchemaError("telemetry includes must be boolean.")
    selected_visual_body_ids = value["selected_visual_body_ids"]
    if not isinstance(selected_visual_body_ids, list):
        raise ArtifactSchemaError("selected_visual_body_ids must be a list.")
    return TelemetrySpec(
        profile_id=value["profile_id"],
        selected_visual_body_ids=tuple(
            _as_int(item, "selected_visual_body_id")
            for item in selected_visual_body_ids
        ),
    )


def _config_from_dict(value: Any) -> ExperimentConfig:
    if not isinstance(value, dict):
        raise ArtifactSchemaError("manifest config must be an object.")
    expected = {
        "schema_version",
        "experiment_id",
        "candidate",
        "source",
        "graph_scope_id",
        "stimulus",
        "duration_ms",
        "dt_ms",
        "encoder",
        "neural",
        "telemetry",
        "pathway_condition",
        "validation_protocol",
        "validation_status",
    }
    _required_keys(value, expected, "manifest config")
    candidate = value["candidate"]
    source = value["source"]
    if not isinstance(candidate, dict) or not isinstance(source, dict):
        raise ArtifactSchemaError("manifest candidate/source must be objects.")
    _required_keys(candidate, {"identifier", "version", "dataset"}, "config candidate")
    _required_keys(source, {"endpoint", "circuit_integrity"}, "config source")
    integrity = source["circuit_integrity"]
    if not isinstance(integrity, list):
        raise ArtifactSchemaError("config source circuit_integrity must be a list.")
    integrity_pairs: list[tuple[str, str]] = []
    for entry in integrity:
        if not isinstance(entry, list) or len(entry) != 2:
            raise ArtifactSchemaError("config source integrity entries must be pairs.")
        integrity_pairs.append((entry[0], entry[1]))
    protocol = value["validation_protocol"]
    if protocol is not None:
        if not isinstance(protocol, dict):
            raise ArtifactSchemaError("validation_protocol must be an object or null.")
        _required_keys(protocol, {"id", "version", "sha256"}, "validation protocol")
    try:
        from neurofly.trajectory_characterization import PathwayCondition

        return ExperimentConfig(
            schema_version=value["schema_version"],
            experiment_id=value["experiment_id"],
            candidate_identifier=candidate["identifier"],
            candidate_version=_as_int(candidate["version"], "candidate.version"),
            dataset=candidate["dataset"],
            source_endpoint=source["endpoint"],
            circuit_integrity=tuple(integrity_pairs),
            graph_scope_id=value["graph_scope_id"],
            stimulus=_stimulus_from_dict(value["stimulus"]),
            duration_ms=_finite(value["duration_ms"], "duration_ms"),
            dt_ms=_finite(value["dt_ms"], "dt_ms"),
            encoder_config=_encoder_from_dict(value["encoder"]),
            lif_config=_lif_from_dict(value["neural"]),
            telemetry=_telemetry_spec_from_dict(value["telemetry"]),
            pathway_condition=PathwayCondition(value["pathway_condition"]),
            validation_protocol_id=None if protocol is None else protocol["id"],
            validation_protocol_version=(
                None if protocol is None else protocol["version"]
            ),
            validation_protocol_sha256=(
                None if protocol is None else protocol["sha256"]
            ),
            validation_status=value["validation_status"],
        )
    except (TypeError, ValueError, RuntimeError, KeyError) as exc:
        raise ArtifactSchemaError(f"invalid manifest config: {exc}") from None


def _body_telemetry_from_dict(value: Any, steps: int) -> BodyTelemetry:
    if not isinstance(value, dict):
        raise ArtifactSchemaError("selected body telemetry must be an object.")
    expected = {
        "body_id",
        "neuron_type",
        "soma_side",
        "times_ms",
        "membrane_mv",
        "synaptic_mveq",
        "external_drive_mveq",
        "incoming_coupling_mveq",
    }
    _required_keys(value, expected, "selected body telemetry")
    body_id = _as_int(value["body_id"], "body_id")
    times = tuple(_finite(item, "body times_ms") for item in value["times_ms"])
    membrane = tuple(_finite(item, "body membrane_mv") for item in value["membrane_mv"])
    synaptic = tuple(
        _finite(item, "body synaptic_mveq") for item in value["synaptic_mveq"]
    )
    drive = tuple(
        _finite(item, "body external_drive_mveq")
        for item in value["external_drive_mveq"]
    )
    incoming = tuple(
        _finite(item, "body incoming_coupling_mveq")
        for item in value["incoming_coupling_mveq"]
    )
    if (
        len(times) != steps + 1
        or len(membrane) != steps + 1
        or len(synaptic) != steps + 1
    ):
        raise ArtifactSchemaError("selected state telemetry boundary count is invalid.")
    if len(drive) != steps or len(incoming) != steps:
        raise ArtifactSchemaError("selected interval telemetry count is invalid.")
    return BodyTelemetry(
        body_id=body_id,
        neuron_type=value["neuron_type"],
        soma_side=value["soma_side"],
        times_ms=times,
        membrane_mv=membrane,
        synaptic_mveq=synaptic,
        external_drive_mveq=drive,
        incoming_coupling_mveq=incoming,
    )


def _spike_from_dict(value: dict[str, Any]) -> SpikeEvent:
    expected = {
        "schema",
        "event_type",
        "time_ms",
        "step",
        "body_id",
        "node_index",
        "neuron_type",
    }
    _required_keys(value, expected, "spike event")
    if value["schema"] != SPIKE_EVENT_SCHEMA or value["event_type"] != "spike":
        raise ArtifactSchemaError("invalid spike event schema/type.")
    return SpikeEvent(
        time_ms=_finite(value["time_ms"], "spike.time_ms"),
        step=_as_int(value["step"], "spike.step"),
        body_id=_as_int(value["body_id"], "spike.body_id"),
        node_index=_as_int(value["node_index"], "spike.node_index"),
        neuron_type=value["neuron_type"],
    )


def _delivered_from_dict(value: dict[str, Any]) -> DeliveredSynapticEvent:
    expected = {
        "schema",
        "event_type",
        "delivery_time_ms",
        "delivery_step",
        "source_body_id",
        "target_body_id",
        "source_index",
        "target_index",
        "structural_weight",
        "model_sign",
        "event_increment_mV_eq",
    }
    _required_keys(value, expected, "delivered event")
    if (
        value["schema"] != DELIVERED_EVENT_SCHEMA
        or value["event_type"] != "delivered_synaptic_event"
    ):
        raise ArtifactSchemaError("invalid delivered-event schema/type.")
    return DeliveredSynapticEvent(
        delivery_time_ms=_finite(value["delivery_time_ms"], "delivery_time_ms"),
        delivery_step=_as_int(value["delivery_step"], "delivery_step"),
        source_body_id=_as_int(value["source_body_id"], "source_body_id"),
        target_body_id=_as_int(value["target_body_id"], "target_body_id"),
        source_index=_as_int(value["source_index"], "source_index"),
        target_index=_as_int(value["target_index"], "target_index"),
        structural_weight=_as_int(value["structural_weight"], "structural_weight"),
        model_sign=_as_int(value["model_sign"], "model_sign"),
        event_increment_mV_eq=_finite(
            value["event_increment_mV_eq"], "event_increment_mV_eq"
        ),
    )


def _summary_from_dict(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ArtifactSchemaError("summary must be an object.")
    expected = {
        "schema",
        "config_sha256",
        "result_sha256",
        "encoding_sha256",
        "external_drive_provenance_id",
        "validation_status",
        "deterministic_replay_verified",
        "population_spike_summaries",
        "delivered_event_summaries",
        "dnp01_first_spike_time_ms",
        "counts",
    }
    _required_keys(value, expected, "summary")
    if value["schema"] != SUMMARY_FILE_SCHEMA:
        raise ArtifactSchemaError("unsupported summary schema.")
    for field_name in (
        "population_spike_summaries",
        "delivered_event_summaries",
        "dnp01_first_spike_time_ms",
    ):
        if not isinstance(value[field_name], list):
            raise ArtifactSchemaError(f"summary {field_name} must be a list.")
    return value


def _telemetry_from_result(result: ExperimentResult) -> dict[str, Any]:
    def series(name: str, units: str, values: tuple[float, ...]) -> dict[str, Any]:
        return {
            "name": name,
            "units": units,
            "sample_count": len(values),
            "values": list(values),
        }

    return {
        "schema": TELEMETRY_FILE_SCHEMA,
        "time_unit": "ms",
        "dt_ms": result.config.dt_ms,
        "start_time_ms": 0.0,
        "sample_count": result.config.steps,
        "boundary_count": len(result.times_ms),
        "interval_convention": (
            "state boundaries at times_ms; interval values apply over [t_n,t_n+dt_ms)"
        ),
        "times_ms": list(result.times_ms),
        "stimulus_samples": [
            _sample_to_dict(sample) for sample in result.stimulus_samples
        ],
        "series": {
            "stimulus_theta_rad": series(
                "stimulus_theta_rad", "rad", result.stimulus_theta_rad
            ),
            "stimulus_dtheta_dt_rad_s": series(
                "stimulus_dtheta_dt_rad_s", "rad/s", result.stimulus_dtheta_dt_rad_s
            ),
            "lc4_normalized": series(
                "lc4_normalized", "unitless", result.lc4_normalized
            ),
            "lplc2_normalized": series(
                "lplc2_normalized", "unitless", result.lplc2_normalized
            ),
            "lc4_drive_mv_eq": series(
                "lc4_drive_mv_eq", "mV_eq", result.lc4_drive_mv_eq
            ),
            "lplc2_drive_mv_eq": series(
                "lplc2_drive_mv_eq", "mV_eq", result.lplc2_drive_mv_eq
            ),
        },
        "selected_body_telemetry": [
            item.to_dict() for item in result.selected_body_telemetry
        ],
    }


def _spike_records(result: ExperimentResult) -> list[dict[str, Any]]:
    return [
        {
            "schema": SPIKE_EVENT_SCHEMA,
            "event_type": "spike",
            "time_ms": event.time_ms,
            "step": event.step,
            "body_id": event.body_id,
            "node_index": event.node_index,
            "neuron_type": event.neuron_type,
        }
        for event in result.spike_events
    ]


def _delivered_records(result: ExperimentResult) -> list[dict[str, Any]]:
    return [
        {
            "schema": DELIVERED_EVENT_SCHEMA,
            "event_type": "delivered_synaptic_event",
            "delivery_time_ms": event.delivery_time_ms,
            "delivery_step": event.delivery_step,
            "source_body_id": event.source_body_id,
            "target_body_id": event.target_body_id,
            "source_index": event.source_index,
            "target_index": event.target_index,
            "structural_weight": event.structural_weight,
            "model_sign": event.model_sign,
            "event_increment_mV_eq": event.event_increment_mV_eq,
        }
        for event in result.delivered_events
    ]


def _summary_from_result(result: ExperimentResult) -> dict[str, Any]:
    return {
        "schema": SUMMARY_FILE_SCHEMA,
        "config_sha256": result.config_sha256,
        "result_sha256": result.result_sha256,
        "encoding_sha256": result.encoding_sha256,
        "external_drive_provenance_id": result.external_drive_provenance_id,
        "validation_status": result.validation_status,
        "deterministic_replay_verified": result.deterministic_replay_verified,
        "population_spike_summaries": [
            item.to_dict() for item in result.population_spike_summaries
        ],
        "delivered_event_summaries": [
            {
                "target_body_id": body_id,
                "event_count": count,
                "event_increment_sum_mV_eq": total,
                "delivery_times_ms": list(times),
            }
            for body_id, count, total, times in result.delivered_event_summaries
        ],
        "dnp01_first_spike_time_ms": [
            {"body_id": body_id, "time_ms": time_ms}
            for body_id, time_ms in result.dnp01_first_spike_time_ms
        ],
        "counts": {
            "steps": result.config.steps,
            "boundary_samples": len(result.times_ms),
            "selected_body_count": len(result.selected_body_telemetry),
            "spike_events": len(result.spike_events),
            "delivered_events": len(result.delivered_events),
        },
    }


def _manifest_base(
    result: ExperimentResult, file_records: dict[str, Any]
) -> dict[str, Any]:
    config = result.config
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": _sha256_bytes(
            _json_bytes(
                {
                    "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                    "config_sha256": result.config_sha256,
                    "result_sha256": result.result_sha256,
                    "files": file_records,
                }
            )
        ),
        "experiment_id": config.experiment_id,
        "experiment_schema_version": config.schema_version,
        "config": config.to_dict(),
        "config_sha256": result.config_sha256,
        "result_schema_version": result.result_schema_version,
        "result_sha256": result.result_sha256,
        "encoding_sha256": result.encoding_sha256,
        "external_drive_provenance_id": result.external_drive_provenance_id,
        "candidate": {
            "identifier": result.candidate_identifier,
            "version": result.candidate_version,
            "dataset": result.dataset,
        },
        "source": {
            "endpoint": config.source_endpoint,
            "circuit_integrity": [list(entry) for entry in result.circuit_integrity],
        },
        "graph_scope_id": result.graph_scope_id,
        "encoder": {
            "id": config.encoder_config.encoder_id,
            "version": config.encoder_config.encoder_version,
            "config_sha256": config.encoder_config.sha256,
        },
        "neural_model": {
            "id": result.simulation_model_id,
            "version": result.simulation_model_version,
        },
        "telemetry_profile": config.telemetry.to_dict(),
        "empirical_protocol": (
            {
                "id": config.validation_protocol_id,
                "version": config.validation_protocol_version,
                "sha256": config.validation_protocol_sha256,
            }
            if config.validation_protocol_id is not None
            else None
        ),
        "validation_status": result.validation_status,
        "deterministic_policy": {
            "stochastic_policy": config.lif_config.stochastic_policy,
            "encoder_stochastic_policy": config.encoder_config.stochastic_policy,
            "rendering_time_used": False,
        },
        "units": {
            "time": "ms",
            "stimulus_theta": "rad",
            "stimulus_dtheta_dt": "rad/s",
            "normalized_features": "unitless",
            "external_drive": "mV_eq",
            "membrane": "mV",
            "filtered_synaptic_state": "mV_eq",
            "structural_weight": "MaleCNS_contact_count",
            "model_increment": "mV_eq",
        },
        "files": file_records,
        "counts": {
            "steps": result.config.steps,
            "boundary_samples": len(result.times_ms),
            "selected_body_count": len(result.selected_body_telemetry),
            "spike_events": len(result.spike_events),
            "delivered_events": len(result.delivered_events),
        },
        "execution_metadata": dict(result.execution_metadata),
    }


@dataclass(frozen=True, slots=True)
class LoadedExperimentArtifact:
    """Immutable offline artifact representation."""

    path: Path
    artifact_id: str
    manifest: MappingProxyType
    result: ExperimentResult
    file_sha256: tuple[tuple[str, str], ...]

    @property
    def config(self) -> ExperimentConfig:
        return self.result.config

    def inspection_dict(self) -> dict[str, Any]:
        return {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "artifact_id": self.artifact_id,
            "experiment_id": self.config.experiment_id,
            "config_sha256": self.result.config_sha256,
            "result_sha256": self.result.result_sha256,
            "candidate": {
                "identifier": self.result.candidate_identifier,
                "version": self.result.candidate_version,
                "dataset": self.result.dataset,
            },
            "graph_scope_id": self.result.graph_scope_id,
            "encoder": self.config.encoder_config.to_dict(),
            "neural_model": self.config.lif_config.to_dict(),
            "telemetry_profile": self.config.telemetry.to_dict(),
            "duration_ms": self.config.duration_ms,
            "dt_ms": self.config.dt_ms,
            "spike_events": len(self.result.spike_events),
            "delivered_events": len(self.result.delivered_events),
            "dnp01_first_spike_time_ms": [
                {"body_id": body_id, "time_ms": time_ms}
                for body_id, time_ms in self.result.dnp01_first_spike_time_ms
            ],
            "validation_status": self.result.validation_status,
            "file_sha256": [list(entry) for entry in self.file_sha256],
        }


def artifact_directory(root: str | Path, result: ExperimentResult) -> Path:
    """Return the conventional ignored derived path for a result."""

    return Path(root) / result.config_sha256


def export_experiment_artifact(
    result: ExperimentResult, destination: str | Path
) -> Path:
    """Atomically export one result; an existing target is never overwritten."""

    if not isinstance(result, ExperimentResult):
        raise ArtifactExportError("result must be an ExperimentResult.")
    output = Path(destination)
    if output.exists():
        raise ArtifactExportError(
            f"artifact output already exists: {output}. "
            "Existing artifacts are immutable."
        )
    staging: Path | None = None
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
        telemetry = _telemetry_from_result(result)
        spikes = _spike_records(result)
        delivered = _delivered_records(result)
        summary = _summary_from_result(result)
        _reject_credentials(telemetry)
        _reject_credentials(spikes)
        _reject_credentials(delivered)
        _reject_credentials(summary)
        file_records: dict[str, Any] = {
            TELEMETRY_FILENAME: {
                "schema": TELEMETRY_FILE_SCHEMA,
                "sha256": _write_json(staging / TELEMETRY_FILENAME, telemetry),
                "bytes": 0,
                "records": 1,
            },
            SPIKES_FILENAME: {
                "schema": SPIKE_EVENT_SCHEMA,
                "sha256": _write_jsonl(staging / SPIKES_FILENAME, spikes),
                "bytes": 0,
                "records": len(spikes),
            },
            DELIVERED_EVENTS_FILENAME: {
                "schema": DELIVERED_EVENT_SCHEMA,
                "sha256": _write_jsonl(staging / DELIVERED_EVENTS_FILENAME, delivered),
                "bytes": 0,
                "records": len(delivered),
            },
            SUMMARY_FILENAME: {
                "schema": SUMMARY_FILE_SCHEMA,
                "sha256": _write_json(staging / SUMMARY_FILENAME, summary),
                "bytes": 0,
                "records": 1,
            },
        }
        for filename in _PAYLOAD_FILENAMES:
            file_records[filename]["bytes"] = (staging / filename).stat().st_size
        manifest = _manifest_base(result, file_records)
        manifest["manifest_sha256"] = _sha256_bytes(_json_bytes(manifest))
        _reject_credentials(manifest)
        _write_json(staging / MANIFEST_FILENAME, manifest)
        # Validate the complete staged directory before it becomes visible.
        load_experiment_artifact(staging)
        os.replace(staging, output)
    except ExperimentArtifactError:
        raise
    except (OSError, ValueError, TypeError) as exc:
        raise ArtifactExportError(
            f"could not export artifact to {output}: {exc}"
        ) from None
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
    return output


def _validate_manifest(manifest: dict[str, Any]) -> None:
    expected = {
        "manifest_schema_version",
        "artifact_schema_version",
        "artifact_id",
        "experiment_id",
        "experiment_schema_version",
        "config",
        "config_sha256",
        "result_schema_version",
        "result_sha256",
        "encoding_sha256",
        "external_drive_provenance_id",
        "candidate",
        "source",
        "graph_scope_id",
        "encoder",
        "neural_model",
        "telemetry_profile",
        "empirical_protocol",
        "validation_status",
        "deterministic_policy",
        "units",
        "files",
        "counts",
        "execution_metadata",
        "manifest_sha256",
    }
    _required_keys(manifest, expected, "manifest")
    if manifest["manifest_schema_version"] != MANIFEST_SCHEMA_VERSION:
        raise ArtifactSchemaError("unsupported artifact manifest schema.")
    if manifest["artifact_schema_version"] != ARTIFACT_SCHEMA_VERSION:
        raise ArtifactSchemaError("unsupported artifact schema.")
    digest = manifest["manifest_sha256"]
    without_digest = dict(manifest)
    without_digest.pop("manifest_sha256")
    if digest != _sha256_bytes(_json_bytes(without_digest)):
        raise ArtifactIntegrityError("manifest SHA-256 does not match its contents.")
    _sha256_identifier(manifest["artifact_id"], "manifest.artifact_id")
    _identifier(manifest["experiment_id"], "manifest.experiment_id")
    _identifier(
        manifest["experiment_schema_version"], "manifest.experiment_schema_version"
    )
    _identifier(manifest["result_schema_version"], "manifest.result_schema_version")
    _sha256_identifier(manifest["config_sha256"], "manifest.config_sha256")
    _sha256_identifier(manifest["result_sha256"], "manifest.result_sha256")
    _sha256_identifier(manifest["encoding_sha256"], "manifest.encoding_sha256")
    for field_name in (
        "external_drive_provenance_id",
        "graph_scope_id",
    ):
        _identifier(manifest[field_name], f"manifest.{field_name}")
    candidate = manifest["candidate"]
    if not isinstance(candidate, dict):
        raise ArtifactSchemaError("manifest.candidate must be an object.")
    _required_keys(
        candidate, {"identifier", "version", "dataset"}, "manifest candidate"
    )
    _identifier(candidate["identifier"], "manifest candidate.identifier")
    _as_int(candidate["version"], "manifest candidate.version")
    _identifier(candidate["dataset"], "manifest candidate.dataset")
    source = manifest["source"]
    if not isinstance(source, dict):
        raise ArtifactSchemaError("manifest.source must be an object.")
    _required_keys(source, {"endpoint", "circuit_integrity"}, "manifest source")
    _identifier(source["endpoint"], "manifest source.endpoint")
    if not isinstance(source["circuit_integrity"], list):
        raise ArtifactSchemaError("manifest source.circuit_integrity must be a list.")
    for entry in source["circuit_integrity"]:
        if (
            not isinstance(entry, list)
            or len(entry) != 2
            or not isinstance(entry[0], str)
            or not isinstance(entry[1], str)
        ):
            raise ArtifactSchemaError(
                "manifest source.circuit_integrity entries must be string pairs."
            )
        _identifier(entry[0], "manifest source.circuit_integrity path")
        _sha256_identifier(entry[1], "manifest source.circuit_integrity sha256")
    encoder = manifest["encoder"]
    if not isinstance(encoder, dict):
        raise ArtifactSchemaError("manifest.encoder must be an object.")
    _required_keys(encoder, {"id", "version", "config_sha256"}, "manifest encoder")
    for field_name in ("id", "version"):
        _identifier(encoder[field_name], f"manifest encoder.{field_name}")
    _sha256_identifier(encoder["config_sha256"], "manifest encoder.config_sha256")
    neural_model = manifest["neural_model"]
    if not isinstance(neural_model, dict):
        raise ArtifactSchemaError("manifest.neural_model must be an object.")
    _required_keys(neural_model, {"id", "version"}, "manifest neural_model")
    _identifier(neural_model["id"], "manifest neural_model.id")
    _identifier(neural_model["version"], "manifest neural_model.version")
    telemetry_profile = manifest["telemetry_profile"]
    if not isinstance(telemetry_profile, dict):
        raise ArtifactSchemaError("manifest.telemetry_profile must be an object.")
    _required_keys(
        telemetry_profile,
        {"profile_id", "selected_visual_body_ids", "includes"},
        "manifest telemetry_profile",
    )
    deterministic_policy = manifest["deterministic_policy"]
    if not isinstance(deterministic_policy, dict):
        raise ArtifactSchemaError("manifest.deterministic_policy must be an object.")
    _required_keys(
        deterministic_policy,
        {"stochastic_policy", "encoder_stochastic_policy", "rendering_time_used"},
        "manifest deterministic_policy",
    )
    _identifier(
        deterministic_policy["stochastic_policy"],
        "manifest deterministic_policy.stochastic_policy",
    )
    _identifier(
        deterministic_policy["encoder_stochastic_policy"],
        "manifest deterministic_policy.encoder_stochastic_policy",
    )
    _as_bool(
        deterministic_policy["rendering_time_used"],
        "manifest deterministic_policy.rendering_time_used",
    )
    units = manifest["units"]
    if not isinstance(units, dict):
        raise ArtifactSchemaError("manifest.units must be an object.")
    expected_units = {
        "time",
        "stimulus_theta",
        "stimulus_dtheta_dt",
        "normalized_features",
        "external_drive",
        "membrane",
        "filtered_synaptic_state",
        "structural_weight",
        "model_increment",
    }
    _required_keys(units, expected_units, "manifest units")
    for field_name in expected_units:
        _identifier(units[field_name], f"manifest.units.{field_name}")
    if not isinstance(manifest["execution_metadata"], dict):
        raise ArtifactSchemaError("manifest.execution_metadata must be an object.")
    if not isinstance(manifest["counts"], dict):
        raise ArtifactSchemaError("manifest.counts must be an object.")
    _required_keys(
        manifest["counts"],
        {
            "steps",
            "boundary_samples",
            "selected_body_count",
            "spike_events",
            "delivered_events",
        },
        "manifest counts",
    )
    for field_name in manifest["counts"]:
        if _as_int(manifest["counts"][field_name], f"manifest.counts.{field_name}") < 0:
            raise ArtifactSchemaError(
                f"manifest.counts.{field_name} cannot be negative."
            )
    protocol = manifest["empirical_protocol"]
    if protocol is not None:
        if not isinstance(protocol, dict):
            raise ArtifactSchemaError(
                "manifest.empirical_protocol must be an object or null."
            )
        _required_keys(
            protocol, {"id", "version", "sha256"}, "manifest empirical_protocol"
        )
        for field_name in ("id", "version"):
            _identifier(
                protocol[field_name], f"manifest empirical_protocol.{field_name}"
            )
        _sha256_identifier(protocol["sha256"], "manifest empirical_protocol.sha256")
    if manifest["validation_status"] != VALIDATION_STATUS_NOT_EVALUATED:
        raise ArtifactSchemaError("artifact validation status is not NOT_EVALUATED.")
    if not isinstance(manifest["files"], dict):
        raise ArtifactSchemaError("manifest.files must be an object.")
    if set(manifest["files"]) != set(_PAYLOAD_FILENAMES):
        raise ArtifactSchemaError(
            "manifest.files does not match required payload files."
        )
    _reject_credentials(manifest)


def _validate_files(path: Path, manifest: dict[str, Any]) -> None:
    for filename in _PAYLOAD_FILENAMES:
        record = manifest["files"][filename]
        if not isinstance(record, dict):
            raise ArtifactSchemaError(
                f"manifest file record {filename} must be an object."
            )
        _required_keys(
            record, {"schema", "sha256", "bytes", "records"}, f"file {filename}"
        )
        expected_schema = {
            TELEMETRY_FILENAME: TELEMETRY_FILE_SCHEMA,
            SPIKES_FILENAME: SPIKE_EVENT_SCHEMA,
            DELIVERED_EVENTS_FILENAME: DELIVERED_EVENT_SCHEMA,
            SUMMARY_FILENAME: SUMMARY_FILE_SCHEMA,
        }[filename]
        if record["schema"] != expected_schema:
            raise ArtifactSchemaError(f"unsupported file schema for {filename}.")
        _sha256_identifier(record["sha256"], f"{filename}.sha256")
        if _as_int(record["records"], f"{filename}.records") < 0:
            raise ArtifactSchemaError(f"{filename}.records cannot be negative.")
        if _as_int(record["bytes"], f"{filename}.bytes") < 0:
            raise ArtifactSchemaError(f"{filename}.bytes cannot be negative.")
        file_path = path / filename
        if not file_path.is_file():
            raise ArtifactIntegrityError(f"missing required artifact file: {filename}")
        actual_digest = _sha256_file(file_path)
        if actual_digest != record["sha256"]:
            raise ArtifactIntegrityError(f"SHA-256 mismatch for {filename}.")
        if file_path.stat().st_size != _as_int(record["bytes"], f"{filename}.bytes"):
            raise ArtifactIntegrityError(f"byte-count mismatch for {filename}.")


def _series(
    telemetry: dict[str, Any], name: str, units: str, steps: int
) -> tuple[float, ...]:
    series = telemetry["series"].get(name)
    if not isinstance(series, dict):
        raise ArtifactSchemaError(f"telemetry series {name} is missing.")
    _required_keys(
        series, {"name", "units", "sample_count", "values"}, f"series {name}"
    )
    if series["name"] != name or series["units"] != units:
        raise ArtifactSchemaError(f"telemetry series {name} has wrong semantics.")
    values = tuple(_finite(item, name) for item in series["values"])
    if series["sample_count"] != len(values) or len(values) != steps:
        raise ArtifactSchemaError(f"telemetry series {name} has wrong length.")
    return values


def _load_result(path: Path, manifest: dict[str, Any]) -> ExperimentResult:
    config = _config_from_dict(manifest["config"])
    if config.sha256 != manifest["config_sha256"]:
        raise ArtifactIntegrityError("manifest config SHA-256 does not match config.")
    if config.experiment_id != manifest["experiment_id"]:
        raise ArtifactSchemaError("manifest experiment ID does not match config.")
    if manifest["experiment_schema_version"] != config.schema_version:
        raise ArtifactSchemaError("manifest experiment schema does not match config.")
    if manifest["graph_scope_id"] != config.graph_scope_id:
        raise ArtifactSchemaError("manifest graph scope does not match config.")
    candidate = manifest["candidate"]
    if (
        candidate["identifier"] != config.candidate_identifier
        or candidate["version"] != config.candidate_version
        or candidate["dataset"] != config.dataset
    ):
        raise ArtifactIntegrityError(
            "manifest candidate identity does not match config."
        )
    source = manifest["source"]
    if (
        source["endpoint"] != config.source_endpoint
        or tuple(sorted(tuple(entry) for entry in source["circuit_integrity"]))
        != config.circuit_integrity
    ):
        raise ArtifactIntegrityError("manifest source identity does not match config.")
    encoder = manifest["encoder"]
    if (
        encoder["id"] != config.encoder_config.encoder_id
        or encoder["version"] != config.encoder_config.encoder_version
        or encoder["config_sha256"] != config.encoder_config.sha256
    ):
        raise ArtifactIntegrityError("manifest encoder identity does not match config.")
    neural_model = manifest["neural_model"]
    if (
        neural_model["id"] != config.lif_config.model_id
        or neural_model["version"] != config.lif_config.model_version
    ):
        raise ArtifactIntegrityError(
            "manifest neural-model identity does not match config."
        )
    if manifest["telemetry_profile"] != config.telemetry.to_dict():
        raise ArtifactIntegrityError(
            "manifest telemetry profile does not match config."
        )
    expected_protocol = (
        None
        if config.validation_protocol_id is None
        else {
            "id": config.validation_protocol_id,
            "version": config.validation_protocol_version,
            "sha256": config.validation_protocol_sha256,
        }
    )
    if manifest["empirical_protocol"] != expected_protocol:
        raise ArtifactIntegrityError(
            "manifest empirical protocol does not match config."
        )
    if manifest["validation_status"] != config.validation_status:
        raise ArtifactIntegrityError(
            "manifest validation status does not match config."
        )
    telemetry = _read_json(path / TELEMETRY_FILENAME, TELEMETRY_FILENAME)
    _required_keys(
        telemetry,
        {
            "schema",
            "time_unit",
            "dt_ms",
            "start_time_ms",
            "sample_count",
            "boundary_count",
            "interval_convention",
            "times_ms",
            "stimulus_samples",
            "series",
            "selected_body_telemetry",
        },
        "telemetry",
    )
    if telemetry["schema"] != TELEMETRY_FILE_SCHEMA or telemetry["time_unit"] != "ms":
        raise ArtifactSchemaError("unsupported telemetry schema or time unit.")
    steps = config.steps
    _finite(telemetry["dt_ms"], "telemetry.dt_ms")
    _finite(telemetry["start_time_ms"], "telemetry.start_time_ms")
    _as_int(telemetry["sample_count"], "telemetry.sample_count")
    _as_int(telemetry["boundary_count"], "telemetry.boundary_count")
    if (
        telemetry["dt_ms"] != config.dt_ms
        or telemetry["start_time_ms"] != 0.0
        or telemetry["sample_count"] != steps
        or telemetry["interval_convention"]
        != "state boundaries at times_ms; interval values apply over [t_n,t_n+dt_ms)"
    ):
        raise ArtifactSchemaError("telemetry timing does not match config.")
    if not isinstance(telemetry["times_ms"], list):
        raise ArtifactSchemaError("telemetry times_ms must be a list.")
    if not isinstance(telemetry["stimulus_samples"], list):
        raise ArtifactSchemaError("telemetry stimulus_samples must be a list.")
    if not isinstance(telemetry["series"], dict):
        raise ArtifactSchemaError("telemetry series must be an object.")
    if not isinstance(telemetry["selected_body_telemetry"], list):
        raise ArtifactSchemaError("telemetry selected_body_telemetry must be a list.")
    times = tuple(_finite(item, "times_ms") for item in telemetry["times_ms"])
    if len(times) != steps + 1 or telemetry["boundary_count"] != len(times):
        raise ArtifactSchemaError("telemetry boundary count is invalid.")
    expected_times = tuple(index * config.dt_ms for index in range(steps + 1))
    if times != expected_times:
        raise ArtifactIntegrityError("telemetry time base does not match config dt.")
    samples = tuple(_sample_from_dict(item) for item in telemetry["stimulus_samples"])
    if len(samples) != steps:
        raise ArtifactSchemaError("telemetry stimulus sample count is invalid.")
    if any(
        sample.collided or sample.angular_expansion_velocity_rad_s is None
        for sample in samples
    ):
        raise ArtifactSchemaError(
            "artifact contains a collision or terminal stimulus sample."
        )
    if any(
        not math.isclose(sample.time_s * 1000.0, time_ms, rel_tol=0.0, abs_tol=1e-12)
        for sample, time_ms in zip(samples, times[:-1], strict=True)
    ):
        raise ArtifactIntegrityError("stimulus sample times do not match telemetry.")
    theta = _series(telemetry, "stimulus_theta_rad", "rad", steps)
    omega = _series(telemetry, "stimulus_dtheta_dt_rad_s", "rad/s", steps)
    if theta != tuple(float(sample.angular_size_rad) for sample in samples):
        raise ArtifactIntegrityError("theta telemetry does not match stimulus samples.")
    if omega != tuple(
        float(sample.angular_expansion_velocity_rad_s) for sample in samples
    ):
        raise ArtifactIntegrityError(
            "expansion telemetry does not match stimulus samples."
        )
    lc4_norm = _series(telemetry, "lc4_normalized", "unitless", steps)
    lplc2_norm = _series(telemetry, "lplc2_normalized", "unitless", steps)
    lc4_drive = _series(telemetry, "lc4_drive_mv_eq", "mV_eq", steps)
    lplc2_drive = _series(telemetry, "lplc2_drive_mv_eq", "mV_eq", steps)
    bodies = tuple(
        _body_telemetry_from_dict(item, steps)
        for item in telemetry["selected_body_telemetry"]
    )
    if set(telemetry["series"]) != {
        "stimulus_theta_rad",
        "stimulus_dtheta_dt_rad_s",
        "lc4_normalized",
        "lplc2_normalized",
        "lc4_drive_mv_eq",
        "lplc2_drive_mv_eq",
    }:
        raise ArtifactSchemaError("telemetry contains an unexpected series.")
    if any(item.times_ms != times for item in bodies):
        raise ArtifactIntegrityError(
            "body telemetry time base does not match telemetry."
        )
    body_ids = {item.body_id for item in bodies}
    if len(body_ids) != len(bodies):
        raise ArtifactSchemaError("selected body telemetry contains duplicate IDs.")
    if not _EXPECTED_DNP01_IDS <= body_ids:
        raise ArtifactSchemaError("both DNp01 bodies must be persisted.")
    if body_ids != set(_EXPECTED_DNP01_IDS) | set(
        config.telemetry.selected_visual_body_ids
    ):
        raise ArtifactSchemaError("selected body telemetry does not match profile.")
    for item in bodies:
        if item.body_id in _EXPECTED_DNP01_IDS and item.neuron_type != "DNp01":
            raise ArtifactSchemaError("DNp01 telemetry has an incorrect neuron type.")
        if item.body_id not in _EXPECTED_DNP01_IDS and item.neuron_type not in {
            "LC4",
            "LPLC2",
        }:
            raise ArtifactSchemaError("visual telemetry has an incorrect neuron type.")
    spikes = tuple(
        _spike_from_dict(item)
        for item in _read_jsonl(path / SPIKES_FILENAME, SPIKES_FILENAME)
    )
    delivered = tuple(
        _delivered_from_dict(item)
        for item in _read_jsonl(
            path / DELIVERED_EVENTS_FILENAME, DELIVERED_EVENTS_FILENAME
        )
    )
    for event in spikes:
        if event.neuron_type not in {"LC4", "LPLC2", "DNp01"}:
            raise ArtifactSchemaError("spike event has an unsupported neuron type.")
        if (
            event.step < 1
            or event.step > steps
            or not math.isclose(
                event.time_ms, times[event.step], rel_tol=0.0, abs_tol=1e-12
            )
        ):
            raise ArtifactIntegrityError("spike event timing does not match time base.")
    for event in delivered:
        if event.target_body_id not in _EXPECTED_DNP01_IDS:
            raise ArtifactSchemaError("delivered event targets a non-DNp01 body.")
        if event.source_body_id == event.target_body_id:
            raise ArtifactSchemaError("delivered event cannot be self-directed.")
        if event.delivery_step < 0 or event.delivery_step >= steps:
            raise ArtifactIntegrityError("delivered event step is outside the run.")
        if not math.isclose(
            event.delivery_time_ms,
            times[event.delivery_step],
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ArtifactIntegrityError(
                "delivered event timing does not match time base."
            )
        if event.model_sign != 1 or event.structural_weight <= 0:
            raise ArtifactSchemaError("delivered event coupling fields are invalid.")
        expected_increment = (
            config.lif_config.k_syn_mv_per_contact * event.structural_weight
        )
        if event.event_increment_mV_eq != expected_increment:
            raise ArtifactIntegrityError(
                "delivered model increment does not match config."
            )
    summary = _summary_from_dict(_read_json(path / SUMMARY_FILENAME, SUMMARY_FILENAME))
    expected_file_records = {
        TELEMETRY_FILENAME: 1,
        SPIKES_FILENAME: len(spikes),
        DELIVERED_EVENTS_FILENAME: len(delivered),
        SUMMARY_FILENAME: 1,
    }
    for filename, expected_records in expected_file_records.items():
        if manifest["files"][filename]["records"] != expected_records:
            raise ArtifactIntegrityError(
                f"manifest record count mismatch for {filename}."
            )
    population_summaries = tuple(
        _population_summary_from_dict(item)
        for item in summary["population_spike_summaries"]
    )
    event_summaries = tuple(
        _event_summary_from_dict(item) for item in summary["delivered_event_summaries"]
    )
    dnp_first_values: list[tuple[int, float | None]] = []
    for item in summary["dnp01_first_spike_time_ms"]:
        if not isinstance(item, dict):
            raise ArtifactSchemaError("DNp01 first-spike records must be objects.")
        _required_keys(item, {"body_id", "time_ms"}, "DNp01 first-spike record")
        dnp_first_values.append(
            (
                _as_int(item["body_id"], "dnp01 body_id"),
                item["time_ms"]
                if item["time_ms"] is None
                else _finite(item["time_ms"], "dnp01 time_ms"),
            )
        )
    dnp_first = tuple(dnp_first_values)
    counts = summary["counts"]
    if not isinstance(counts, dict):
        raise ArtifactSchemaError("summary counts must be an object.")
    _required_keys(
        counts,
        {
            "steps",
            "boundary_samples",
            "selected_body_count",
            "spike_events",
            "delivered_events",
        },
        "summary counts",
    )
    expected_counts = {
        "steps": steps,
        "boundary_samples": steps + 1,
        "selected_body_count": len(bodies),
        "spike_events": len(spikes),
        "delivered_events": len(delivered),
    }
    for key, expected_value in expected_counts.items():
        if counts.get(key) != expected_value:
            raise ArtifactIntegrityError(f"summary count mismatch for {key}.")
        if manifest["counts"].get(key) != expected_value:
            raise ArtifactIntegrityError(f"manifest count mismatch for {key}.")
    if (
        summary["config_sha256"] != manifest["config_sha256"]
        or summary["result_sha256"] != manifest["result_sha256"]
    ):
        raise ArtifactIntegrityError("summary identity does not match manifest.")
    if summary["encoding_sha256"] != manifest["encoding_sha256"]:
        raise ArtifactIntegrityError(
            "summary encoder identity does not match manifest."
        )
    if (
        summary["external_drive_provenance_id"]
        != manifest["external_drive_provenance_id"]
    ):
        raise ArtifactIntegrityError(
            "summary input provenance does not match manifest."
        )
    _as_bool(
        summary["deterministic_replay_verified"],
        "summary deterministic_replay_verified",
    )
    if summary["validation_status"] != VALIDATION_STATUS_NOT_EVALUATED:
        raise ArtifactSchemaError("summary validation status is not NOT_EVALUATED.")
    if len(population_summaries) != 2 or {
        item.neuron_type for item in population_summaries
    } != {"LC4", "LPLC2"}:
        raise ArtifactSchemaError("population summaries must contain LC4 and LPLC2.")
    expected_population_counts = {"LC4": 126, "LPLC2": 185}
    spike_by_type = {
        neuron_type: tuple(
            event for event in spikes if event.neuron_type == neuron_type
        )
        for neuron_type in ("LC4", "LPLC2")
    }
    for population in population_summaries:
        if population.body_count != expected_population_counts[population.neuron_type]:
            raise ArtifactIntegrityError(
                f"population body count mismatch for {population.neuron_type}."
            )
        population_events = spike_by_type[population.neuron_type]
        if population.total_spike_count != len(population_events):
            raise ArtifactIntegrityError(
                f"population spike count mismatch for {population.neuron_type}."
            )
        first_times = tuple(
            time
            for _, time in population.first_spike_time_ms_by_body_id
            if time is not None
        )
        if population.bodies_that_spike != len(first_times):
            raise ArtifactIntegrityError(
                f"population first-spike count mismatch for {population.neuron_type}."
            )
        if population.first_population_spike_time_ms != (
            min(first_times) if first_times else None
        ):
            raise ArtifactIntegrityError(
                f"population first-spike summary mismatch for {population.neuron_type}."
            )
    if len(event_summaries) != 2 or {item[0] for item in event_summaries} != set(
        _EXPECTED_DNP01_IDS
    ):
        raise ArtifactSchemaError(
            "delivered-event summaries must contain both DNp01 bodies."
        )
    for target_body_id, count, total, delivery_times in event_summaries:
        target_events = tuple(
            event for event in delivered if event.target_body_id == target_body_id
        )
        if count != len(target_events) or total != sum(
            event.event_increment_mV_eq for event in target_events
        ):
            raise ArtifactIntegrityError(
                f"delivered-event summary mismatch for DNp01 {target_body_id}."
            )
        if delivery_times != tuple(event.delivery_time_ms for event in target_events):
            raise ArtifactIntegrityError(
                f"delivered-event timing summary mismatch for DNp01 {target_body_id}."
            )
    expected_dnp_first = tuple(
        (
            body_id,
            next(
                (event.time_ms for event in spikes if event.body_id == body_id),
                None,
            ),
        )
        for body_id in sorted(_EXPECTED_DNP01_IDS)
    )
    if dnp_first != expected_dnp_first:
        raise ArtifactIntegrityError("DNp01 first-spike summary does not match events.")
    result = ExperimentResult(
        result_schema_version=manifest["result_schema_version"],
        config=config,
        config_sha256=manifest["config_sha256"],
        encoding_sha256=manifest["encoding_sha256"],
        external_drive_provenance_id=manifest["external_drive_provenance_id"],
        candidate_identifier=manifest["candidate"]["identifier"],
        candidate_version=_as_int(
            manifest["candidate"]["version"], "candidate.version"
        ),
        dataset=manifest["candidate"]["dataset"],
        circuit_integrity=tuple(
            tuple(entry) for entry in manifest["source"]["circuit_integrity"]
        ),
        graph_scope_id=manifest["graph_scope_id"],
        simulation_model_id=manifest["neural_model"]["id"],
        simulation_model_version=manifest["neural_model"]["version"],
        stimulus_samples=samples,
        times_ms=times,
        stimulus_theta_rad=theta,
        stimulus_dtheta_dt_rad_s=omega,
        lc4_normalized=lc4_norm,
        lplc2_normalized=lplc2_norm,
        lc4_drive_mv_eq=lc4_drive,
        lplc2_drive_mv_eq=lplc2_drive,
        population_spike_summaries=population_summaries,
        selected_body_telemetry=bodies,
        spike_events=spikes,
        delivered_events=delivered,
        delivered_event_summaries=event_summaries,
        dnp01_first_spike_time_ms=dnp_first,
        deterministic_replay_verified=_as_bool(
            summary["deterministic_replay_verified"], "deterministic_replay_verified"
        ),
        validation_status=summary["validation_status"],
        execution_metadata=manifest["execution_metadata"],
    )
    if result.result_sha256 != manifest["result_sha256"]:
        raise ArtifactIntegrityError(
            "reconstructed result SHA-256 does not match manifest."
        )
    return result


def _population_summary_from_dict(value: Any) -> PopulationSpikeSummary:
    if not isinstance(value, dict):
        raise ArtifactSchemaError("population summary must be an object.")
    expected = {
        "neuron_type",
        "body_count",
        "bodies_that_spike",
        "total_spike_count",
        "first_population_spike_time_ms",
        "first_spike_time_ms_by_body_id",
    }
    _required_keys(value, expected, "population summary")
    first = tuple(
        (
            _as_int(item["body_id"], "population body_id"),
            None
            if item["time_ms"] is None
            else _finite(item["time_ms"], "population time_ms"),
        )
        for item in value["first_spike_time_ms_by_body_id"]
    )
    return PopulationSpikeSummary(
        neuron_type=value["neuron_type"],
        body_count=_as_int(value["body_count"], "population body_count"),
        bodies_that_spike=_as_int(
            value["bodies_that_spike"], "population bodies_that_spike"
        ),
        total_spike_count=_as_int(
            value["total_spike_count"], "population total_spike_count"
        ),
        first_population_spike_time_ms=(
            None
            if value["first_population_spike_time_ms"] is None
            else _finite(
                value["first_population_spike_time_ms"],
                "first_population_spike_time_ms",
            )
        ),
        first_spike_time_ms_by_body_id=first,
    )


def _event_summary_from_dict(value: Any) -> tuple[int, int, float, tuple[float, ...]]:
    if not isinstance(value, dict):
        raise ArtifactSchemaError("delivered-event summary must be an object.")
    expected = {
        "target_body_id",
        "event_count",
        "event_increment_sum_mV_eq",
        "delivery_times_ms",
    }
    _required_keys(value, expected, "delivered-event summary")
    return (
        _as_int(value["target_body_id"], "target_body_id"),
        _as_int(value["event_count"], "event_count"),
        _finite(value["event_increment_sum_mV_eq"], "event_increment_sum_mV_eq"),
        tuple(_finite(item, "delivery_time_ms") for item in value["delivery_times_ms"]),
    )


def load_experiment_artifact(path: str | Path) -> LoadedExperimentArtifact:
    """Load and validate an artifact without network access or simulation."""

    root = Path(path)
    if not root.is_dir():
        raise ArtifactIntegrityError(f"artifact directory does not exist: {root}")
    names = {entry.name for entry in root.iterdir()}
    expected_names = {MANIFEST_FILENAME, *_PAYLOAD_FILENAMES}
    if names != expected_names:
        raise ArtifactIntegrityError(
            "artifact files differ: "
            f"expected={sorted(expected_names)!r}, actual={sorted(names)!r}"
        )
    manifest = _read_json(root / MANIFEST_FILENAME, MANIFEST_FILENAME)
    _validate_manifest(manifest)
    _validate_files(root, manifest)
    result = _load_result(root, manifest)
    if result.config_sha256 != manifest["config_sha256"]:
        raise ArtifactIntegrityError("loaded config identity mismatch.")
    artifact_identity = _sha256_bytes(
        _json_bytes(
            {
                "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                "config_sha256": manifest["config_sha256"],
                "result_sha256": manifest["result_sha256"],
                "files": manifest["files"],
            }
        )
    )
    if artifact_identity != manifest["artifact_id"]:
        raise ArtifactIntegrityError("artifact identity does not match manifest.")
    return LoadedExperimentArtifact(
        path=root,
        artifact_id=artifact_identity,
        manifest=_freeze(manifest),
        result=result,
        file_sha256=tuple(
            (filename, manifest["files"][filename]["sha256"])
            for filename in _PAYLOAD_FILENAMES
        ),
    )


def _replay_mismatches(
    expected: ExperimentResult, actual: ExperimentResult
) -> tuple[str, ...]:
    mismatches: list[str] = []
    if expected.config_sha256 != actual.config_sha256:
        mismatches.append("config identity")
    if expected.stimulus_samples != actual.stimulus_samples:
        mismatches.append("stimulus samples")
    if (
        expected.lc4_normalized != actual.lc4_normalized
        or expected.lplc2_normalized != actual.lplc2_normalized
        or expected.lc4_drive_mv_eq != actual.lc4_drive_mv_eq
        or expected.lplc2_drive_mv_eq != actual.lplc2_drive_mv_eq
    ):
        mismatches.append("encoder drive")
    if expected.spike_events != actual.spike_events:
        mismatches.append("visual/spike events")
    if expected.delivered_events != actual.delivered_events:
        mismatches.append("delivered events")
    expected_dnp = tuple(
        item for item in expected.selected_body_telemetry if item.neuron_type == "DNp01"
    )
    actual_dnp = tuple(
        item for item in actual.selected_body_telemetry if item.neuron_type == "DNp01"
    )
    if expected_dnp != actual_dnp:
        mismatches.append("DNp01 telemetry")
    if expected.result_sha256 != actual.result_sha256:
        mismatches.append("result digest")
    return tuple(mismatches)


def replay_experiment_artifact(
    path: str | Path, circuit_contract: Any
) -> ExperimentResult:
    """Rerun a loaded artifact with an explicitly supplied local contract."""

    artifact = load_experiment_artifact(path)
    try:
        actual = ExperimentRunner(circuit_contract).run(artifact.config)
    except ExperimentError as exc:
        raise ArtifactReplayError(f"artifact replay could not execute: {exc}") from None
    mismatches = _replay_mismatches(artifact.result, actual)
    if mismatches:
        raise ArtifactReplayError(
            "artifact replay differs in: " + ", ".join(mismatches)
        )
    return actual


def inspect_experiment_artifact(path: str | Path) -> dict[str, Any]:
    """Return a compact offline inspection dictionary."""

    return load_experiment_artifact(path).inspection_dict()


def _main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Inspect a NeuroFly experiment artifact."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser("inspect-artifact")
    inspect.add_argument("path", type=Path)
    args = parser.parse_args()
    if args.command == "inspect-artifact":
        print(
            json.dumps(inspect_experiment_artifact(args.path), indent=2, sort_keys=True)
        )
        return 0
    return 2


if (
    __name__ == "__main__"
):  # pragma: no cover - exercised through subprocess smoke tests
    raise SystemExit(_main())


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "TELEMETRY_FILE_SCHEMA",
    "SPIKE_EVENT_SCHEMA",
    "DELIVERED_EVENT_SCHEMA",
    "SUMMARY_FILE_SCHEMA",
    "ExperimentArtifactError",
    "ArtifactSchemaError",
    "ArtifactIntegrityError",
    "ArtifactExportError",
    "ArtifactReplayError",
    "LoadedExperimentArtifact",
    "artifact_directory",
    "export_experiment_artifact",
    "load_experiment_artifact",
    "replay_experiment_artifact",
    "inspect_experiment_artifact",
]
