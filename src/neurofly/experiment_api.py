"""Read-only, transport-neutral application views of NeuroFly artifacts.

Phase 4A deliberately stops at a Python application boundary.  The service
loads integrity-checked Phase 3B artifacts and translates them into stable,
JSON-safe DTOs; it never runs the simulator, mutates an artifact, or changes
Phase 3C comparison semantics.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from neurofly.experiment_artifacts import (
    ARTIFACT_SCHEMA_VERSION,
    ArtifactIntegrityError,
    ArtifactSchemaError,
    ExperimentArtifactError,
    LoadedExperimentArtifact,
    load_experiment_artifact,
)
from neurofly.experiment_comparison import (
    ExperimentComparisonError,
    ExperimentComparisonResult,
    compare_experiment_artifacts,
)

APPLICATION_API_SCHEMA_VERSION = "experiment_api_v1"
TIMELINE_INTERVAL_SEMANTICS = "step_values_apply_on_[t_n,t_n+dt)"
_DNP01_IDS = (10001, 10010)
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_RANGE_TOLERANCE_MS = 1e-12


class ExperimentApiError(RuntimeError):
    """Base error for the read-only application boundary."""


class ArtifactStoreError(ExperimentApiError):
    """The configured artifact store cannot be read safely."""


class InvalidArtifactIdError(ArtifactStoreError):
    """An artifact identifier is not a canonical SHA-256 identity."""


class ArtifactNotFoundError(ArtifactStoreError):
    """No artifact with the requested identity exists below the store root."""


class ArtifactPathError(ArtifactStoreError):
    """An artifact path would escape the configured read-only root."""


class CorruptedArtifactError(ArtifactStoreError):
    """An artifact failed the production Phase 3B integrity/schema loader."""


class UnsupportedArtifactError(ArtifactStoreError):
    """An artifact uses a schema version this application boundary rejects."""


class BodyTelemetryUnavailableError(ExperimentApiError):
    """The requested body was not persisted in the selected artifact."""


class InvalidRangeError(ExperimentApiError):
    """A timeline range is invalid or is not aligned to simulation samples."""


class ComparisonUnavailableError(ExperimentApiError):
    """The requested artifact comparison could not be constructed."""


def _finite(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise ExperimentApiError(f"{field_name} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ExperimentApiError(f"{field_name} must be finite.") from None
    if not math.isfinite(result):
        raise ExperimentApiError(f"{field_name} must be finite.")
    return result


def _json_safe(value: Any) -> Any:
    """Copy a value into ordinary JSON-native containers and scalars."""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ExperimentApiError("JSON payload contains a non-finite float.")
        return value
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    raise ExperimentApiError(
        f"JSON payload contains unsupported value type {type(value).__name__}."
    )


def _freeze_json(value: Any) -> Any:
    """Recursively freeze nested DTO metadata without exposing writable state."""

    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze_json(item) for key, item in value.items()}
        )
    if isinstance(value, (tuple, list)):
        return tuple(_freeze_json(item) for item in value)
    return value


def _json_text(value: Any) -> str:
    try:
        return json.dumps(
            _json_safe(value),
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise ExperimentApiError("could not serialize application payload") from exc


def _peak(values: tuple[float, ...], field_name: str) -> float:
    if not values:
        raise ExperimentApiError(f"{field_name} cannot be empty.")
    return max(values)


def _body_map(artifact: LoadedExperimentArtifact) -> dict[int, Any]:
    return {item.body_id: item for item in artifact.result.selected_body_telemetry}


@dataclass(frozen=True, slots=True)
class FreeParameterSummary:
    """The five currently free NeuroFly model quantities."""

    lc4_gain_mv_eq: float
    lplc2_gain_mv_eq: float
    omega_half_rad_per_s: float
    theta_half_rad: float
    k_syn_mv_per_contact: float

    def to_dict(self) -> dict[str, float]:
        return {
            "lc4_gain_mv_eq": self.lc4_gain_mv_eq,
            "lplc2_gain_mv_eq": self.lplc2_gain_mv_eq,
            "omega_half_rad_per_s": self.omega_half_rad_per_s,
            "theta_half_rad": self.theta_half_rad,
            "k_syn_mv_per_contact": self.k_syn_mv_per_contact,
        }


@dataclass(frozen=True, slots=True)
class PopulationSummary:
    """One independent LC4 or LPLC2 population summary."""

    neuron_type: str
    body_count: int
    bodies_that_spike: int
    total_spike_count: int
    first_spike_time_ms: float | None
    peak_normalized_feature: float
    peak_drive_mveq: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "neuron_type": self.neuron_type,
            "body_count": self.body_count,
            "bodies_that_spike": self.bodies_that_spike,
            "total_spike_count": self.total_spike_count,
            "first_spike_time_ms": self.first_spike_time_ms,
            "peak_normalized_feature": self.peak_normalized_feature,
            "peak_drive_mveq": self.peak_drive_mveq,
        }


@dataclass(frozen=True, slots=True)
class DNp01Summary:
    """One independent DNp01 body summary."""

    body_id: int
    neuron_type: str
    soma_side: str | None
    total_spike_count: int
    first_spike_time_ms: float | None
    peak_membrane_mv: float
    peak_synaptic_state_mveq: float
    delivered_event_count: int
    model_increment_sum_mveq: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "body_id": self.body_id,
            "neuron_type": self.neuron_type,
            "soma_side": self.soma_side,
            "total_spike_count": self.total_spike_count,
            "first_spike_time_ms": self.first_spike_time_ms,
            "peak_membrane_mv": self.peak_membrane_mv,
            "peak_synaptic_state_mveq": self.peak_synaptic_state_mveq,
            "delivered_event_count": self.delivered_event_count,
            "model_increment_sum_mveq": self.model_increment_sum_mveq,
        }


@dataclass(frozen=True, slots=True)
class ExperimentSummary:
    """Stable JSON-safe summary of one integrity-checked artifact."""

    artifact_id: str
    experiment_config_id: str
    experiment_config_sha256: str
    result_id: str
    artifact_schema_version: str
    dataset: str
    candidate_identifier: str
    candidate_version: int
    source_endpoint: str
    circuit_integrity: tuple[tuple[str, str], ...]
    graph_scope_id: str
    encoder_id: str
    encoder_version: str
    neural_model_id: str
    neural_model_version: str
    pathway_condition: str
    duration_ms: float
    dt_ms: float
    validation_status: str
    telemetry_profile: Mapping[str, Any]
    free_parameters: FreeParameterSummary
    lc4: PopulationSummary
    lplc2: PopulationSummary
    dnp01: tuple[DNp01Summary, ...]

    def to_dict(self) -> dict[str, Any]:
        return _json_safe(
            {
                "schema": APPLICATION_API_SCHEMA_VERSION,
                "kind": "experiment_summary",
                "artifact_id": self.artifact_id,
                "experiment_config_id": self.experiment_config_id,
                "experiment_config_sha256": self.experiment_config_sha256,
                "result_id": self.result_id,
                "artifact_schema_version": self.artifact_schema_version,
                "dataset": self.dataset,
                "candidate": {
                    "identifier": self.candidate_identifier,
                    "version": self.candidate_version,
                },
                "source": {
                    "endpoint": self.source_endpoint,
                    "circuit_integrity": [
                        list(item) for item in self.circuit_integrity
                    ],
                },
                "graph_scope_id": self.graph_scope_id,
                "encoder": {"id": self.encoder_id, "version": self.encoder_version},
                "neural_model": {
                    "id": self.neural_model_id,
                    "version": self.neural_model_version,
                },
                "pathway_condition": self.pathway_condition,
                "duration_ms": self.duration_ms,
                "dt_ms": self.dt_ms,
                "validation_status": self.validation_status,
                "telemetry_profile": dict(self.telemetry_profile),
                "free_parameters": self.free_parameters.to_dict(),
                "populations": {
                    "LC4": self.lc4.to_dict(),
                    "LPLC2": self.lplc2.to_dict(),
                },
                "dnp01": [item.to_dict() for item in self.dnp01],
            }
        )

    def to_json(self) -> str:
        return _json_text(self.to_dict())


def _population_summary(
    artifact: LoadedExperimentArtifact, neuron_type: str
) -> PopulationSummary:
    result = artifact.result
    summary_by_type = {
        item.neuron_type: item for item in result.population_spike_summaries
    }
    summary = summary_by_type[neuron_type]
    if neuron_type == "LC4":
        normalized = result.lc4_normalized
        drive = result.lc4_drive_mv_eq
    else:
        normalized = result.lplc2_normalized
        drive = result.lplc2_drive_mv_eq
    return PopulationSummary(
        neuron_type=neuron_type,
        body_count=summary.body_count,
        bodies_that_spike=summary.bodies_that_spike,
        total_spike_count=summary.total_spike_count,
        first_spike_time_ms=summary.first_population_spike_time_ms,
        peak_normalized_feature=_peak(normalized, f"{neuron_type} normalized feature"),
        peak_drive_mveq=_peak(drive, f"{neuron_type} drive"),
    )


def _dnp_summary(artifact: LoadedExperimentArtifact, body_id: int) -> DNp01Summary:
    result = artifact.result
    body = _body_map(artifact).get(body_id)
    if body is None:
        raise BodyTelemetryUnavailableError(
            f"DNp01 body {body_id} is not persisted in artifact {artifact.artifact_id}."
        )
    event_summaries = {
        target: (count, total)
        for target, count, total, _times in result.delivered_event_summaries
    }
    first_spikes = dict(result.dnp01_first_spike_time_ms)
    return DNp01Summary(
        body_id=body_id,
        neuron_type=body.neuron_type or "DNp01",
        soma_side=body.soma_side,
        total_spike_count=sum(
            event.body_id == body_id for event in result.spike_events
        ),
        first_spike_time_ms=first_spikes[body_id],
        peak_membrane_mv=_peak(body.membrane_mv, f"DNp01 {body_id} membrane"),
        peak_synaptic_state_mveq=_peak(
            body.synaptic_mveq, f"DNp01 {body_id} synaptic state"
        ),
        delivered_event_count=event_summaries[body_id][0],
        model_increment_sum_mveq=event_summaries[body_id][1],
    )


def _summary_from_artifact(artifact: LoadedExperimentArtifact) -> ExperimentSummary:
    config = artifact.config
    encoder = config.encoder_config
    lif = config.lif_config
    return ExperimentSummary(
        artifact_id=artifact.artifact_id,
        experiment_config_id=config.experiment_id,
        experiment_config_sha256=artifact.result.config_sha256,
        result_id=artifact.result.result_sha256,
        artifact_schema_version=ARTIFACT_SCHEMA_VERSION,
        dataset=artifact.result.dataset,
        candidate_identifier=artifact.result.candidate_identifier,
        candidate_version=artifact.result.candidate_version,
        source_endpoint=config.source_endpoint,
        circuit_integrity=artifact.result.circuit_integrity,
        graph_scope_id=artifact.result.graph_scope_id,
        encoder_id=encoder.encoder_id,
        encoder_version=encoder.encoder_version,
        neural_model_id=lif.model_id,
        neural_model_version=lif.model_version,
        pathway_condition=config.pathway_condition.value,
        duration_ms=config.duration_ms,
        dt_ms=config.dt_ms,
        validation_status=artifact.result.validation_status,
        telemetry_profile=_freeze_json(config.telemetry.to_dict()),
        free_parameters=FreeParameterSummary(
            lc4_gain_mv_eq=encoder.lc4_gain_mv_eq,
            lplc2_gain_mv_eq=encoder.lplc2_gain_mv_eq,
            omega_half_rad_per_s=encoder.omega_half_rad_per_s,
            theta_half_rad=encoder.theta_half_rad,
            k_syn_mv_per_contact=lif.k_syn_mv_per_contact,
        ),
        lc4=_population_summary(artifact, "LC4"),
        lplc2=_population_summary(artifact, "LPLC2"),
        dnp01=tuple(_dnp_summary(artifact, body_id) for body_id in _DNP01_IDS),
    )


@dataclass(frozen=True, slots=True)
class BodyTelemetryView:
    """Persisted state telemetry for one body, with no fabricated fields."""

    artifact_id: str
    body_id: int
    neuron_type: str | None
    soma_side: str | None
    times_ms: tuple[float, ...]
    step_times_ms: tuple[float, ...]
    membrane_mv: tuple[float, ...]
    synaptic_state_mveq: tuple[float, ...]
    external_drive_mveq: tuple[float, ...]
    incoming_coupling_mveq: tuple[float, ...]
    spike_times_ms: tuple[float, ...]

    def to_dict(self) -> dict[str, Any]:
        return _json_safe(
            {
                "schema": APPLICATION_API_SCHEMA_VERSION,
                "kind": "body_telemetry",
                "artifact_id": self.artifact_id,
                "body_id": self.body_id,
                "neuron_type": self.neuron_type,
                "soma_side": self.soma_side,
                "time_unit": "ms",
                "times_ms": self.times_ms,
                "step_times_ms": self.step_times_ms,
                "interval_semantics": TIMELINE_INTERVAL_SEMANTICS,
                "membrane_unit": "mV",
                "membrane_mv": self.membrane_mv,
                "synaptic_state_unit": "mV_eq",
                "synaptic_state_mveq": self.synaptic_state_mveq,
                "external_drive_unit": "mV_eq",
                "external_drive_mveq": self.external_drive_mveq,
                "incoming_coupling_unit": "mV_eq",
                "incoming_coupling_mveq": self.incoming_coupling_mveq,
                "spike_times_ms": self.spike_times_ms,
            }
        )

    def to_json(self) -> str:
        return _json_text(self.to_dict())


def _body_view(
    artifact: LoadedExperimentArtifact,
    body_id: int,
    boundary_indices: range | None = None,
    step_indices: range | None = None,
    spike_start_ms: float | None = None,
    spike_end_ms: float | None = None,
) -> BodyTelemetryView:
    body = _body_map(artifact).get(body_id)
    if body is None:
        raise BodyTelemetryUnavailableError(
            f"body {body_id} telemetry is unavailable in artifact "
            f"{artifact.artifact_id}."
        )
    if boundary_indices is None:
        boundary = range(len(body.times_ms))
    else:
        boundary = boundary_indices
    if step_indices is None:
        steps = range(len(body.external_drive_mveq))
    else:
        steps = step_indices
    boundary_tuple = tuple(boundary)
    step_tuple = tuple(steps)
    spikes = tuple(
        event.time_ms
        for event in artifact.result.spike_events
        if event.body_id == body_id
        and (spike_start_ms is None or event.time_ms >= spike_start_ms)
        and (spike_end_ms is None or event.time_ms < spike_end_ms)
    )
    return BodyTelemetryView(
        artifact_id=artifact.artifact_id,
        body_id=body.body_id,
        neuron_type=body.neuron_type,
        soma_side=body.soma_side,
        times_ms=tuple(body.times_ms[index] for index in boundary_tuple),
        step_times_ms=tuple(artifact.result.times_ms[index] for index in step_tuple),
        membrane_mv=tuple(body.membrane_mv[index] for index in boundary_tuple),
        synaptic_state_mveq=tuple(
            body.synaptic_mveq[index] for index in boundary_tuple
        ),
        external_drive_mveq=tuple(
            body.external_drive_mveq[index] for index in step_tuple
        ),
        incoming_coupling_mveq=tuple(
            body.incoming_coupling_mveq[index] for index in step_tuple
        ),
        spike_times_ms=spikes,
    )


@dataclass(frozen=True, slots=True)
class ExperimentTimeline:
    """Exact neural-time timeline; step features are not interpolated."""

    artifact_id: str
    dt_ms: float
    duration_ms: float
    start_ms: float
    end_ms: float
    times_ms: tuple[float, ...]
    step_times_ms: tuple[float, ...]
    theta_rad: tuple[float, ...]
    angular_expansion_velocity_rad_s: tuple[float, ...]
    lc4_normalized_feature: tuple[float, ...]
    lplc2_normalized_feature: tuple[float, ...]
    lc4_drive_mveq: tuple[float, ...]
    lplc2_drive_mveq: tuple[float, ...]
    selected_body_telemetry: tuple[BodyTelemetryView, ...]

    def to_dict(self) -> dict[str, Any]:
        return _json_safe(
            {
                "schema": APPLICATION_API_SCHEMA_VERSION,
                "kind": "experiment_timeline",
                "artifact_id": self.artifact_id,
                "time_unit": "ms",
                "dt_ms": self.dt_ms,
                "duration_ms": self.duration_ms,
                "start_ms": self.start_ms,
                "end_ms": self.end_ms,
                "times_ms": self.times_ms,
                "step_times_ms": self.step_times_ms,
                "interval_semantics": TIMELINE_INTERVAL_SEMANTICS,
                "theta_unit": "rad",
                "theta_rad": self.theta_rad,
                "angular_expansion_velocity_unit": "rad/s",
                "angular_expansion_velocity_rad_s": (
                    self.angular_expansion_velocity_rad_s
                ),
                "lc4_normalized_feature": self.lc4_normalized_feature,
                "lplc2_normalized_feature": self.lplc2_normalized_feature,
                "drive_unit": "mV_eq",
                "lc4_drive_mveq": self.lc4_drive_mveq,
                "lplc2_drive_mveq": self.lplc2_drive_mveq,
                "selected_body_telemetry": [
                    item.to_dict() for item in self.selected_body_telemetry
                ],
            }
        )

    def to_json(self) -> str:
        return _json_text(self.to_dict())


@dataclass(frozen=True, slots=True)
class SpikeEventView:
    """Transport representation of one persisted spike event."""

    time_ms: float
    body_id: int
    node_index: int
    neuron_type: str
    step: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "time_ms": self.time_ms,
            "body_id": self.body_id,
            "node_index": self.node_index,
            "neuron_type": self.neuron_type,
            "step": self.step,
        }


@dataclass(frozen=True, slots=True)
class DeliveredEventView:
    """Transport representation of one delivered model synaptic event."""

    delivery_time_ms: float
    source_body_id: int
    target_body_id: int
    structural_weight: int
    model_sign: int
    event_increment_mveq: float
    delivery_step: int
    source_index: int
    target_index: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "delivery_time_ms": self.delivery_time_ms,
            "source_body_id": self.source_body_id,
            "target_body_id": self.target_body_id,
            "structural_weight": self.structural_weight,
            "model_sign": self.model_sign,
            "event_increment_mV_eq": self.event_increment_mveq,
            "delivery_step": self.delivery_step,
            "source_index": self.source_index,
            "target_index": self.target_index,
        }


@dataclass(frozen=True, slots=True)
class ExperimentEvents:
    """All persisted spike and delivered-event records for one artifact."""

    artifact_id: str
    spike_events: tuple[SpikeEventView, ...]
    delivered_events: tuple[DeliveredEventView, ...]

    def to_dict(self) -> dict[str, Any]:
        return _json_safe(
            {
                "schema": APPLICATION_API_SCHEMA_VERSION,
                "kind": "experiment_events",
                "artifact_id": self.artifact_id,
                "spike_events": [item.to_dict() for item in self.spike_events],
                "delivered_events": [item.to_dict() for item in self.delivered_events],
                "spike_event_count": len(self.spike_events),
                "delivered_event_count": len(self.delivered_events),
            }
        )

    def to_json(self) -> str:
        return _json_text(self.to_dict())


def _events_from_artifact(artifact: LoadedExperimentArtifact) -> ExperimentEvents:
    return ExperimentEvents(
        artifact_id=artifact.artifact_id,
        spike_events=tuple(
            SpikeEventView(
                time_ms=event.time_ms,
                body_id=event.body_id,
                node_index=event.node_index,
                neuron_type=event.neuron_type,
                step=event.step,
            )
            for event in artifact.result.spike_events
        ),
        delivered_events=tuple(
            DeliveredEventView(
                delivery_time_ms=event.delivery_time_ms,
                source_body_id=event.source_body_id,
                target_body_id=event.target_body_id,
                structural_weight=event.structural_weight,
                model_sign=event.model_sign,
                event_increment_mveq=event.event_increment_mV_eq,
                delivery_step=event.delivery_step,
                source_index=event.source_index,
                target_index=event.target_index,
            )
            for event in artifact.result.delivered_events
        ),
    )


@dataclass(frozen=True, slots=True)
class ComparisonSummary:
    """Transport view preserving the complete Phase 3C comparison semantics."""

    comparison_id: str
    comparison_schema_version: str
    artifact_a_id: str
    artifact_b_id: str
    compatibility_class: str
    source_model_compatible: bool
    configuration_differences: tuple[Mapping[str, Any], ...]
    source_model_differences: tuple[Mapping[str, Any], ...]
    telemetry: Mapping[str, Any]
    pathway: Mapping[str, Any]
    visual_populations: tuple[Mapping[str, Any], ...]
    dnp01: tuple[Mapping[str, Any], ...]
    events: Mapping[str, Any]
    limitations: tuple[str, ...]
    empirical_validation_status: str

    @classmethod
    def from_result(cls, result: ExperimentComparisonResult) -> ComparisonSummary:
        payload = result.to_dict()
        frozen = _freeze_json(payload)
        return cls(
            comparison_id=result.comparison_sha256,
            comparison_schema_version=result.comparison_schema_version,
            artifact_a_id=result.artifact_a_id,
            artifact_b_id=result.artifact_b_id,
            compatibility_class=result.compatibility.value,
            source_model_compatible=not result.source_model_differences,
            configuration_differences=tuple(frozen["configuration_differences"]),
            source_model_differences=tuple(frozen["source_model_differences"]),
            telemetry=frozen["telemetry"],
            pathway=frozen["pathway"],
            visual_populations=tuple(frozen["visual_populations"]),
            dnp01=tuple(frozen["dnp01"]),
            events=frozen["events"],
            limitations=tuple(frozen["limitations"]),
            empirical_validation_status=result.empirical_validation_status,
        )

    def to_dict(self) -> dict[str, Any]:
        return _json_safe(
            {
                "schema": APPLICATION_API_SCHEMA_VERSION,
                "kind": "comparison_summary",
                "comparison_id": self.comparison_id,
                "comparison_schema_version": self.comparison_schema_version,
                "artifact_a_id": self.artifact_a_id,
                "artifact_b_id": self.artifact_b_id,
                "compatibility_class": self.compatibility_class,
                "source_model_compatible": self.source_model_compatible,
                "configuration_differences": self.configuration_differences,
                "source_model_differences": self.source_model_differences,
                "telemetry": self.telemetry,
                "pathway": self.pathway,
                "visual_populations": self.visual_populations,
                "dnp01": self.dnp01,
                "events": self.events,
                "limitations": self.limitations,
                "empirical_validation_status": self.empirical_validation_status,
            }
        )

    def to_json(self) -> str:
        return _json_text(self.to_dict())


def _aligned_index(
    value_ms: float, times_ms: tuple[float, ...], field_name: str
) -> int:
    for index, sample_time in enumerate(times_ms):
        if math.isclose(
            value_ms, sample_time, rel_tol=0.0, abs_tol=_RANGE_TOLERANCE_MS
        ):
            return index
    raise InvalidRangeError(
        f"{field_name}={value_ms!r} is not aligned to the stored simulation time grid."
    )


def _range_indices(
    artifact: LoadedExperimentArtifact,
    start_ms: float | None,
    end_ms: float | None,
) -> tuple[float, float, int, int]:
    result = artifact.result
    try:
        start = 0.0 if start_ms is None else _finite(start_ms, "start_ms")
        end = result.config.duration_ms if end_ms is None else _finite(end_ms, "end_ms")
    except ExperimentApiError as exc:
        raise InvalidRangeError(str(exc)) from exc
    if start < 0.0 or end > result.config.duration_ms or start >= end:
        raise InvalidRangeError(
            "timeline range must satisfy 0 <= start_ms < end_ms <= duration_ms."
        )
    start_index = _aligned_index(start, result.times_ms, "start_ms")
    end_index = _aligned_index(end, result.times_ms, "end_ms")
    if start_index >= end_index:
        raise InvalidRangeError("timeline range must contain at least one step.")
    return start, end, start_index, end_index


def _timeline_from_artifact(
    artifact: LoadedExperimentArtifact,
    start_ms: float | None = None,
    end_ms: float | None = None,
) -> ExperimentTimeline:
    start, end, start_index, end_index = _range_indices(artifact, start_ms, end_ms)
    result = artifact.result
    boundary_indices = range(start_index, end_index + 1)
    step_indices = range(start_index, end_index)
    step_times = tuple(result.times_ms[index] for index in step_indices)
    body_views = tuple(
        _body_view(
            artifact,
            body.body_id,
            boundary_indices=boundary_indices,
            step_indices=step_indices,
            spike_start_ms=start,
            spike_end_ms=end,
        )
        for body in result.selected_body_telemetry
    )
    return ExperimentTimeline(
        artifact_id=artifact.artifact_id,
        dt_ms=result.config.dt_ms,
        duration_ms=result.config.duration_ms,
        start_ms=start,
        end_ms=end,
        times_ms=tuple(result.times_ms[index] for index in boundary_indices),
        step_times_ms=step_times,
        theta_rad=tuple(result.stimulus_theta_rad[index] for index in step_indices),
        angular_expansion_velocity_rad_s=tuple(
            result.stimulus_dtheta_dt_rad_s[index] for index in step_indices
        ),
        lc4_normalized_feature=tuple(
            result.lc4_normalized[index] for index in step_indices
        ),
        lplc2_normalized_feature=tuple(
            result.lplc2_normalized[index] for index in step_indices
        ),
        lc4_drive_mveq=tuple(result.lc4_drive_mv_eq[index] for index in step_indices),
        lplc2_drive_mveq=tuple(
            result.lplc2_drive_mv_eq[index] for index in step_indices
        ),
        selected_body_telemetry=body_views,
    )


def _load_error(path: Path, error: ExperimentArtifactError) -> ExperimentApiError:
    message = f"artifact {path.name!r} failed Phase 3B validation: {error}"
    if isinstance(error, ArtifactSchemaError) and "unsupported" in str(error).lower():
        return UnsupportedArtifactError(message)
    if isinstance(error, ArtifactIntegrityError):
        return CorruptedArtifactError(message)
    return CorruptedArtifactError(message)


class ExperimentArtifactStore:
    """Read-only artifact discovery and DTO service under one explicit root."""

    def __init__(self, root: str | Path) -> None:
        configured = Path(root)
        if not configured.exists() or not configured.is_dir():
            raise ArtifactStoreError(f"artifact root is not a directory: {configured}")
        self._root = configured.resolve()

    @property
    def root(self) -> Path:
        return self._root

    def _children(self) -> tuple[Path, ...]:
        try:
            entries = tuple(sorted(self._root.iterdir(), key=lambda item: item.name))
        except OSError as exc:
            raise ArtifactStoreError(
                f"could not enumerate artifact root {self._root}"
            ) from exc
        children: list[Path] = []
        for entry in entries:
            if entry.is_symlink():
                raise ArtifactPathError(
                    f"symlink artifact entry is not allowed: {entry.name}"
                )
            if not entry.is_dir():
                continue
            resolved = entry.resolve()
            try:
                resolved.relative_to(self._root)
            except ValueError:
                raise ArtifactPathError(
                    f"artifact entry escapes configured root: {entry.name}"
                ) from None
            children.append(entry)
        return tuple(children)

    def _load_directory(self, path: Path) -> LoadedExperimentArtifact:
        try:
            internal_entries = tuple(path.iterdir())
        except OSError as exc:
            raise ArtifactStoreError(
                f"could not enumerate artifact {path.name!r}"
            ) from exc
        if any(entry.is_symlink() for entry in internal_entries):
            raise ArtifactPathError(
                f"symlink inside artifact is not allowed: {path.name!r}"
            )
        try:
            return load_experiment_artifact(path)
        except ExperimentArtifactError as exc:
            raise _load_error(path, exc) from exc

    def _all_loaded(self) -> tuple[LoadedExperimentArtifact, ...]:
        loaded: list[LoadedExperimentArtifact] = []
        seen: set[str] = set()
        for child in self._children():
            artifact = self._load_directory(child)
            if artifact.artifact_id in seen:
                raise ArtifactStoreError(
                    "duplicate artifact identity below configured root: "
                    f"{artifact.artifact_id}"
                )
            seen.add(artifact.artifact_id)
            loaded.append(artifact)
        return tuple(sorted(loaded, key=lambda item: item.artifact_id))

    @staticmethod
    def _validate_identity(identity: str, field_name: str) -> str:
        if not isinstance(identity, str) or _SHA256_RE.fullmatch(identity) is None:
            raise InvalidArtifactIdError(
                f"{field_name} must be a lowercase 64-character SHA-256 identity."
            )
        return identity

    @staticmethod
    def _validate_id(artifact_id: str) -> str:
        return ExperimentArtifactStore._validate_identity(artifact_id, "artifact_id")

    def discover_artifact_ids(self) -> tuple[str, ...]:
        return tuple(item.artifact_id for item in self._all_loaded())

    def _get_loaded(self, artifact_id: str) -> LoadedExperimentArtifact:
        identity = self._validate_id(artifact_id)
        for artifact in self._all_loaded():
            if artifact.artifact_id == identity:
                return artifact
        raise ArtifactNotFoundError(f"artifact not found: {identity}")

    def _get_by_result_identity(
        self, identity: str, *, field_name: str, attribute: str
    ) -> LoadedExperimentArtifact:
        value = self._validate_identity(identity, field_name)
        for artifact in self._all_loaded():
            if getattr(artifact.result, attribute) == value:
                return artifact
        raise ArtifactNotFoundError(f"{field_name} not found: {value}")

    def list_experiments(self) -> tuple[ExperimentSummary, ...]:
        return tuple(_summary_from_artifact(item) for item in self._all_loaded())

    def list_artifacts(self) -> tuple[ExperimentSummary, ...]:
        """Alias emphasizing that this API lists persisted artifacts only."""

        return self.list_experiments()

    def list_experiment_summaries(self) -> tuple[ExperimentSummary, ...]:
        return self.list_experiments()

    def get_experiment(self, artifact_id: str) -> ExperimentSummary:
        return _summary_from_artifact(self._get_loaded(artifact_id))

    def get_experiment_summary(self, artifact_id: str) -> ExperimentSummary:
        return self.get_experiment(artifact_id)

    def get_experiment_by_config_id(self, config_sha256: str) -> ExperimentSummary:
        artifact = self._get_by_result_identity(
            config_sha256,
            field_name="config_sha256",
            attribute="config_sha256",
        )
        return _summary_from_artifact(artifact)

    def get_experiment_by_result_id(self, result_sha256: str) -> ExperimentSummary:
        artifact = self._get_by_result_identity(
            result_sha256,
            field_name="result_sha256",
            attribute="result_sha256",
        )
        return _summary_from_artifact(artifact)

    def get_timeline(
        self,
        artifact_id: str,
        *,
        start_ms: float | None = None,
        end_ms: float | None = None,
    ) -> ExperimentTimeline:
        return _timeline_from_artifact(self._get_loaded(artifact_id), start_ms, end_ms)

    def get_experiment_timeline(
        self,
        artifact_id: str,
        *,
        start_ms: float | None = None,
        end_ms: float | None = None,
    ) -> ExperimentTimeline:
        return self.get_timeline(artifact_id, start_ms=start_ms, end_ms=end_ms)

    def get_body_telemetry(self, artifact_id: str, body_id: int) -> BodyTelemetryView:
        if isinstance(body_id, bool) or not isinstance(body_id, int):
            raise BodyTelemetryUnavailableError("body_id must be an integer.")
        return _body_view(self._get_loaded(artifact_id), body_id)

    def get_events(self, artifact_id: str) -> ExperimentEvents:
        return _events_from_artifact(self._get_loaded(artifact_id))

    def get_spike_events(self, artifact_id: str) -> tuple[SpikeEventView, ...]:
        return self.get_events(artifact_id).spike_events

    def get_delivered_events(self, artifact_id: str) -> tuple[DeliveredEventView, ...]:
        return self.get_events(artifact_id).delivered_events

    def get_comparison(
        self, artifact_a_id: str, artifact_b_id: str
    ) -> ComparisonSummary:
        artifact_a = self._get_loaded(artifact_a_id)
        artifact_b = self._get_loaded(artifact_b_id)
        try:
            result = compare_experiment_artifacts(artifact_a, artifact_b)
        except ExperimentComparisonError as exc:
            raise ComparisonUnavailableError(str(exc)) from exc
        return ComparisonSummary.from_result(result)

    def compare(self, artifact_a_id: str, artifact_b_id: str) -> ComparisonSummary:
        return self.get_comparison(artifact_a_id, artifact_b_id)


__all__ = [
    "APPLICATION_API_SCHEMA_VERSION",
    "TIMELINE_INTERVAL_SEMANTICS",
    "ExperimentApiError",
    "ArtifactStoreError",
    "InvalidArtifactIdError",
    "ArtifactNotFoundError",
    "ArtifactPathError",
    "CorruptedArtifactError",
    "UnsupportedArtifactError",
    "BodyTelemetryUnavailableError",
    "InvalidRangeError",
    "ComparisonUnavailableError",
    "FreeParameterSummary",
    "PopulationSummary",
    "DNp01Summary",
    "ExperimentSummary",
    "BodyTelemetryView",
    "ExperimentTimeline",
    "SpikeEventView",
    "DeliveredEventView",
    "ExperimentEvents",
    "ComparisonSummary",
    "ExperimentArtifactStore",
]
