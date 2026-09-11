"""Deterministic offline experiment runs for the NeuroFly Phase 3A slice.

This module is an orchestration boundary only.  Stimulus geometry, Level P
encoding, graph selection, and LIF equations remain in their existing
modules.  An :class:`ExperimentRunner` composes those components and returns
an immutable, replayable result with an explicit telemetry profile.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any

import numpy as np

from neurofly.malecns.sensory import LoomingSample, LoomingStimulus
from neurofly.sensory_encoder import LevelPEncoderConfig, encode_level_p
from neurofly.simulation import (
    GRAPH_SCOPE_ID,
    READOUT_TYPE,
    DeliveredSynapticEvent,
    LIFConfig,
    LIFSimulator,
    SimulationGraph,
    SimulationResult,
    SpikeEvent,
    build_phase2b_graph,
)
from neurofly.trajectory_characterization import (
    LoomingTrajectoryScenario,
    PathwayCondition,
    apply_pathway_condition,
    sample_looming_trajectory,
)

EXPERIMENT_SCHEMA_VERSION = "experiment_run_v1"
TELEMETRY_PROFILE_VALIDATION_V1 = "VALIDATION_TELEMETRY_V1"
VALIDATION_STATUS_NOT_EVALUATED = "NOT_EVALUATED"
_TIME_TOLERANCE_MS = 1e-9


class ExperimentError(RuntimeError):
    """Base class for explicit experiment configuration and run failures."""


class ExperimentConfigurationError(ExperimentError):
    """An experiment configuration is malformed or incompatible."""


class ExperimentExecutionError(ExperimentError):
    """The production pipeline could not complete an experiment."""


class ExperimentReplayError(ExperimentError):
    """Two supposedly identical deterministic runs differ."""


def _finite(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise ExperimentConfigurationError(f"{field_name} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ExperimentConfigurationError(f"{field_name} must be finite.") from None
    if not math.isfinite(result):
        raise ExperimentConfigurationError(f"{field_name} must be finite.")
    return result


def _identifier(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ExperimentConfigurationError(f"{field_name} must be a non-empty string.")
    return value


def _integral_steps(duration_ms: float, dt_ms: float) -> int:
    ratio = duration_ms / dt_ms
    nearest = round(ratio)
    if not math.isclose(ratio, nearest, rel_tol=0.0, abs_tol=1e-9):
        raise ExperimentConfigurationError(
            "duration_ms must be an integral number of dt_ms steps."
        )
    if nearest <= 0:
        raise ExperimentConfigurationError("duration_ms must contain a step.")
    return int(nearest)


def _sha256_json(value: Any) -> str:
    try:
        serialized = json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ExperimentError(
            "value is not deterministically JSON serializable"
        ) from exc
    return hashlib.sha256(serialized).hexdigest()


def _event_to_dict(event: SpikeEvent | DeliveredSynapticEvent) -> dict[str, Any]:
    if isinstance(event, SpikeEvent):
        return {
            "time_ms": event.time_ms,
            "step": event.step,
            "body_id": event.body_id,
            "node_index": event.node_index,
            "neuron_type": event.neuron_type,
        }
    return {
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


def _tuple_float(values: Any, field_name: str) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError):
        raise ExperimentExecutionError(f"{field_name} is not numeric.") from None
    if not all(math.isfinite(value) for value in result):
        raise ExperimentExecutionError(f"{field_name} contains non-finite values.")
    return result


@dataclass(frozen=True, slots=True)
class TelemetrySpec:
    """Explicit selected-output policy for one experiment result.

    The validation profile always retains the two DNp01 state trajectories,
    population spike summaries, stimulus/encoder series, and event summaries.
    ``selected_visual_body_ids`` optionally adds full state telemetry for
    named visual bodies without serializing all 311 visual trajectories.
    """

    profile_id: str = TELEMETRY_PROFILE_VALIDATION_V1
    selected_visual_body_ids: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        _identifier(self.profile_id, "profile_id")
        if self.profile_id != TELEMETRY_PROFILE_VALIDATION_V1:
            raise ExperimentConfigurationError(
                f"Unsupported telemetry profile {self.profile_id!r}."
            )
        try:
            body_ids = tuple(self.selected_visual_body_ids)
        except TypeError:
            raise ExperimentConfigurationError(
                "selected_visual_body_ids must be an iterable of integers."
            ) from None
        if any(
            isinstance(body_id, bool) or not isinstance(body_id, int) or body_id <= 0
            for body_id in body_ids
        ):
            raise ExperimentConfigurationError(
                "selected_visual_body_ids must contain positive integer body IDs."
            )
        if len(set(body_ids)) != len(body_ids):
            raise ExperimentConfigurationError(
                "selected_visual_body_ids must not contain duplicates."
            )
        object.__setattr__(self, "selected_visual_body_ids", tuple(sorted(body_ids)))

    @classmethod
    def validation_profile(
        cls, *, selected_visual_body_ids: Iterable[int] = ()
    ) -> TelemetrySpec:
        return cls(selected_visual_body_ids=tuple(selected_visual_body_ids))

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "selected_visual_body_ids": list(self.selected_visual_body_ids),
            "includes": {
                "stimulus_features": True,
                "encoder_drives": True,
                "population_spike_summaries": True,
                "dnp01_state": True,
                "spike_events": True,
                "delivered_event_summaries": True,
            },
        }


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Immutable complete scientific configuration for one offline run."""

    schema_version: str
    experiment_id: str
    candidate_identifier: str
    candidate_version: int
    dataset: str
    source_endpoint: str
    circuit_integrity: tuple[tuple[str, str], ...]
    graph_scope_id: str
    stimulus: LoomingStimulus
    duration_ms: float
    dt_ms: float
    encoder_config: LevelPEncoderConfig
    lif_config: LIFConfig
    telemetry: TelemetrySpec = field(default_factory=TelemetrySpec.validation_profile)
    pathway_condition: PathwayCondition = PathwayCondition.COMBINED
    validation_protocol_id: str | None = None
    validation_protocol_version: str | None = None
    validation_protocol_sha256: str | None = None
    validation_status: str = VALIDATION_STATUS_NOT_EVALUATED

    def __post_init__(self) -> None:
        _identifier(self.schema_version, "schema_version")
        if self.schema_version != EXPERIMENT_SCHEMA_VERSION:
            raise ExperimentConfigurationError(
                f"Unsupported schema_version {self.schema_version!r}."
            )
        _identifier(self.experiment_id, "experiment_id")
        _identifier(self.candidate_identifier, "candidate_identifier")
        _identifier(self.dataset, "dataset")
        _identifier(self.source_endpoint, "source_endpoint")
        _identifier(self.graph_scope_id, "graph_scope_id")
        if isinstance(self.candidate_version, bool) or not isinstance(
            self.candidate_version, int
        ):
            raise ExperimentConfigurationError("candidate_version must be an integer.")
        if not isinstance(self.stimulus, LoomingStimulus):
            raise ExperimentConfigurationError("stimulus must be a LoomingStimulus.")
        if not isinstance(self.encoder_config, LevelPEncoderConfig):
            raise ExperimentConfigurationError(
                "encoder_config must be a LevelPEncoderConfig."
            )
        if not isinstance(self.lif_config, LIFConfig):
            raise ExperimentConfigurationError("lif_config must be a LIFConfig.")
        if not isinstance(self.telemetry, TelemetrySpec):
            raise ExperimentConfigurationError("telemetry must be a TelemetrySpec.")
        if not isinstance(self.pathway_condition, PathwayCondition):
            raise ExperimentConfigurationError("pathway_condition is unsupported.")
        duration = _finite(self.duration_ms, "duration_ms")
        dt = _finite(self.dt_ms, "dt_ms")
        if duration <= 0.0:
            raise ExperimentConfigurationError("duration_ms must be greater than zero.")
        if dt <= 0.0:
            raise ExperimentConfigurationError("dt_ms must be greater than zero.")
        _integral_steps(duration, dt)
        if not math.isclose(
            self.lif_config.dt_ms, dt, rel_tol=0.0, abs_tol=_TIME_TOLERANCE_MS
        ):
            raise ExperimentConfigurationError(
                "Experiment dt_ms must match LIFConfig.dt_ms."
            )
        if self.graph_scope_id != GRAPH_SCOPE_ID:
            raise ExperimentConfigurationError(
                "Experiment graph_scope_id must be the Phase 2B graph scope."
            )
        if self.lif_config.graph_scope_id != self.graph_scope_id:
            raise ExperimentConfigurationError(
                "LIFConfig graph scope does not match ExperimentConfig."
            )
        if self.validation_status != VALIDATION_STATUS_NOT_EVALUATED:
            raise ExperimentConfigurationError(
                "Phase 3A does not evaluate empirical validation status."
            )
        protocol_fields = (
            self.validation_protocol_id,
            self.validation_protocol_version,
            self.validation_protocol_sha256,
        )
        if any(value is None for value in protocol_fields) and not all(
            value is None for value in protocol_fields
        ):
            raise ExperimentConfigurationError(
                "validation protocol ID, version, and hash must be supplied together."
            )
        if self.validation_protocol_id is not None:
            _identifier(self.validation_protocol_id, "validation_protocol_id")
            _identifier(self.validation_protocol_version, "validation_protocol_version")
            _identifier(self.validation_protocol_sha256, "validation_protocol_sha256")
        try:
            integrity = tuple(self.circuit_integrity)
        except TypeError:
            raise ExperimentConfigurationError(
                "circuit_integrity must contain (path, sha256) pairs."
            ) from None
        normalized_integrity: list[tuple[str, str]] = []
        for entry in integrity:
            if not isinstance(entry, (tuple, list)) or len(entry) != 2:
                raise ExperimentConfigurationError(
                    "circuit_integrity must contain (path, sha256) pairs."
                )
            path, digest = entry
            _identifier(path, "circuit_integrity path")
            _identifier(digest, "circuit_integrity sha256")
            normalized_integrity.append((path, digest))
        if len({path for path, _ in normalized_integrity}) != len(normalized_integrity):
            raise ExperimentConfigurationError(
                "circuit_integrity paths must be unique."
            )
        object.__setattr__(self, "duration_ms", duration)
        object.__setattr__(self, "dt_ms", dt)
        object.__setattr__(
            self, "circuit_integrity", tuple(sorted(normalized_integrity))
        )

    @classmethod
    def from_contract(
        cls,
        *,
        experiment_id: str,
        circuit_contract: Any,
        stimulus: LoomingStimulus,
        duration_ms: float,
        encoder_config: LevelPEncoderConfig,
        lif_config: LIFConfig,
        telemetry: TelemetrySpec | None = None,
        pathway_condition: PathwayCondition = PathwayCondition.COMBINED,
        validation_protocol_id: str | None = None,
        validation_protocol_version: str | None = None,
        validation_protocol_sha256: str | None = None,
    ) -> ExperimentConfig:
        """Create a config while copying validated source identity explicitly."""

        candidate = getattr(circuit_contract, "candidate", None)
        provenance = getattr(circuit_contract, "provenance", None)
        integrity = getattr(circuit_contract, "integrity", None)
        if candidate is None or provenance is None or integrity is None:
            raise ExperimentConfigurationError(
                "circuit_contract must expose candidate, provenance, and integrity."
            )
        return cls(
            schema_version=EXPERIMENT_SCHEMA_VERSION,
            experiment_id=experiment_id,
            candidate_identifier=candidate.identifier,
            candidate_version=candidate.version,
            dataset=provenance.dataset,
            source_endpoint=provenance.endpoint,
            circuit_integrity=tuple(integrity.sha256_by_file),
            graph_scope_id=lif_config.graph_scope_id,
            stimulus=stimulus,
            duration_ms=duration_ms,
            dt_ms=lif_config.dt_ms,
            encoder_config=encoder_config,
            lif_config=lif_config,
            telemetry=(
                TelemetrySpec.validation_profile() if telemetry is None else telemetry
            ),
            pathway_condition=pathway_condition,
            validation_protocol_id=validation_protocol_id,
            validation_protocol_version=validation_protocol_version,
            validation_protocol_sha256=validation_protocol_sha256,
        )

    @property
    def steps(self) -> int:
        return _integral_steps(self.duration_ms, self.dt_ms)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "experiment_id": self.experiment_id,
            "candidate": {
                "identifier": self.candidate_identifier,
                "version": self.candidate_version,
                "dataset": self.dataset,
            },
            "source": {
                "endpoint": self.source_endpoint,
                "circuit_integrity": [list(entry) for entry in self.circuit_integrity],
            },
            "graph_scope_id": self.graph_scope_id,
            "stimulus": self.stimulus.to_dict(),
            "duration_ms": self.duration_ms,
            "dt_ms": self.dt_ms,
            "encoder": self.encoder_config.to_dict(),
            "neural": self.lif_config.to_dict(),
            "telemetry": self.telemetry.to_dict(),
            "pathway_condition": self.pathway_condition.value,
            "validation_protocol": (
                {
                    "id": self.validation_protocol_id,
                    "version": self.validation_protocol_version,
                    "sha256": self.validation_protocol_sha256,
                }
                if self.validation_protocol_id is not None
                else None
            ),
            "validation_status": self.validation_status,
        }

    @property
    def sha256(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True, slots=True)
class BodyTelemetry:
    """Selected boundary/state telemetry for one body ID."""

    body_id: int
    neuron_type: str | None
    soma_side: str | None
    times_ms: tuple[float, ...]
    membrane_mv: tuple[float, ...]
    synaptic_mveq: tuple[float, ...]
    external_drive_mveq: tuple[float, ...]
    incoming_coupling_mveq: tuple[float, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "body_id": self.body_id,
            "neuron_type": self.neuron_type,
            "soma_side": self.soma_side,
            "times_ms": list(self.times_ms),
            "membrane_mv": list(self.membrane_mv),
            "synaptic_mveq": list(self.synaptic_mveq),
            "external_drive_mveq": list(self.external_drive_mveq),
            "incoming_coupling_mveq": list(self.incoming_coupling_mveq),
        }


@dataclass(frozen=True, slots=True)
class PopulationSpikeSummary:
    """Population activity summary retaining each body's first-spike time."""

    neuron_type: str
    body_count: int
    bodies_that_spike: int
    total_spike_count: int
    first_population_spike_time_ms: float | None
    first_spike_time_ms_by_body_id: tuple[tuple[int, float | None], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "neuron_type": self.neuron_type,
            "body_count": self.body_count,
            "bodies_that_spike": self.bodies_that_spike,
            "total_spike_count": self.total_spike_count,
            "first_population_spike_time_ms": self.first_population_spike_time_ms,
            "first_spike_time_ms_by_body_id": [
                {"body_id": body_id, "time_ms": time_ms}
                for body_id, time_ms in self.first_spike_time_ms_by_body_id
            ],
        }


def _population_summary(
    graph: SimulationGraph, result: SimulationResult, neuron_type: str
) -> PopulationSpikeSummary:
    body_ids = tuple(node.body_id for node in graph.nodes if node.type == neuron_type)
    counts = Counter(
        event.body_id for event in result.spikes if event.neuron_type == neuron_type
    )
    first = tuple(
        (body_id, result.first_spike_time_ms_by_body_id.get(body_id))
        for body_id in body_ids
    )
    observed = tuple(time for _, time in first if time is not None)
    return PopulationSpikeSummary(
        neuron_type=neuron_type,
        body_count=len(body_ids),
        bodies_that_spike=len(observed),
        total_spike_count=sum(counts.values()),
        first_population_spike_time_ms=min(observed) if observed else None,
        first_spike_time_ms_by_body_id=first,
    )


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    """Immutable selected telemetry and provenance for one completed run."""

    result_schema_version: str
    config: ExperimentConfig
    config_sha256: str
    encoding_sha256: str
    external_drive_provenance_id: str
    candidate_identifier: str
    candidate_version: int
    dataset: str
    circuit_integrity: tuple[tuple[str, str], ...]
    graph_scope_id: str
    simulation_model_id: str
    simulation_model_version: str
    stimulus_samples: tuple[LoomingSample, ...]
    times_ms: tuple[float, ...]
    stimulus_theta_rad: tuple[float, ...]
    stimulus_dtheta_dt_rad_s: tuple[float, ...]
    lc4_normalized: tuple[float, ...]
    lplc2_normalized: tuple[float, ...]
    lc4_drive_mv_eq: tuple[float, ...]
    lplc2_drive_mv_eq: tuple[float, ...]
    population_spike_summaries: tuple[PopulationSpikeSummary, ...]
    selected_body_telemetry: tuple[BodyTelemetry, ...]
    spike_events: tuple[SpikeEvent, ...]
    delivered_events: tuple[DeliveredSynapticEvent, ...]
    delivered_event_summaries: tuple[tuple[int, int, float, tuple[float, ...]], ...]
    dnp01_first_spike_time_ms: tuple[tuple[int, float | None], ...]
    deterministic_replay_verified: bool
    validation_status: str
    execution_metadata: Mapping[str, Any] = field(default_factory=dict)
    result_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        if self.result_schema_version != EXPERIMENT_SCHEMA_VERSION:
            raise ExperimentExecutionError("unsupported experiment result schema.")
        if not isinstance(self.config, ExperimentConfig):
            raise ExperimentExecutionError("result config must be an ExperimentConfig.")
        if self.config_sha256 != self.config.sha256:
            raise ExperimentExecutionError("result/config identity mismatch.")
        _identifier(
            self.external_drive_provenance_id,
            "external_drive_provenance_id",
        )
        if self.validation_status != VALIDATION_STATUS_NOT_EVALUATED:
            raise ExperimentExecutionError(
                "Phase 3A results are not validation results."
            )
        object.__setattr__(self, "stimulus_samples", tuple(self.stimulus_samples))
        if len(self.stimulus_samples) != self.config.steps:
            raise ExperimentExecutionError("stimulus sample count is inconsistent.")
        if not all(
            isinstance(sample, LoomingSample) for sample in self.stimulus_samples
        ):
            raise ExperimentExecutionError(
                "stimulus_samples must be LoomingSample values."
            )
        object.__setattr__(
            self, "execution_metadata", MappingProxyType(dict(self.execution_metadata))
        )
        for name in (
            "times_ms",
            "stimulus_theta_rad",
            "stimulus_dtheta_dt_rad_s",
            "lc4_normalized",
            "lplc2_normalized",
            "lc4_drive_mv_eq",
            "lplc2_drive_mv_eq",
        ):
            values = _tuple_float(getattr(self, name), name)
            object.__setattr__(self, name, values)
        if len(self.times_ms) != self.config.steps + 1:
            raise ExperimentExecutionError(
                "result time boundary count is inconsistent."
            )
        for name in (
            "stimulus_theta_rad",
            "stimulus_dtheta_dt_rad_s",
            "lc4_normalized",
            "lplc2_normalized",
            "lc4_drive_mv_eq",
            "lplc2_drive_mv_eq",
        ):
            if len(getattr(self, name)) != self.config.steps:
                raise ExperimentExecutionError(f"{name} step count is inconsistent.")
        object.__setattr__(self, "circuit_integrity", tuple(self.circuit_integrity))
        object.__setattr__(
            self, "population_spike_summaries", tuple(self.population_spike_summaries)
        )
        object.__setattr__(
            self, "selected_body_telemetry", tuple(self.selected_body_telemetry)
        )
        object.__setattr__(self, "spike_events", tuple(self.spike_events))
        object.__setattr__(self, "delivered_events", tuple(self.delivered_events))
        object.__setattr__(
            self, "delivered_event_summaries", tuple(self.delivered_event_summaries)
        )
        object.__setattr__(
            self, "dnp01_first_spike_time_ms", tuple(self.dnp01_first_spike_time_ms)
        )
        object.__setattr__(self, "result_sha256", _sha256_json(self.to_dict(False)))

    def _body_telemetry_dict(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.selected_body_telemetry]

    def to_dict(self, include_result_sha256: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "result_schema_version": self.result_schema_version,
            "config": self.config.to_dict(),
            "config_sha256": self.config_sha256,
            "encoding_sha256": self.encoding_sha256,
            "external_drive_provenance_id": self.external_drive_provenance_id,
            "candidate": {
                "identifier": self.candidate_identifier,
                "version": self.candidate_version,
                "dataset": self.dataset,
            },
            "circuit_integrity": [list(entry) for entry in self.circuit_integrity],
            "graph_scope_id": self.graph_scope_id,
            "simulation_model": {
                "id": self.simulation_model_id,
                "version": self.simulation_model_version,
            },
            "stimulus_samples": [sample.to_dict() for sample in self.stimulus_samples],
            "times_ms": list(self.times_ms),
            "stimulus_theta_rad": list(self.stimulus_theta_rad),
            "stimulus_dtheta_dt_rad_s": list(self.stimulus_dtheta_dt_rad_s),
            "lc4_normalized": list(self.lc4_normalized),
            "lplc2_normalized": list(self.lplc2_normalized),
            "lc4_drive_mv_eq": list(self.lc4_drive_mv_eq),
            "lplc2_drive_mv_eq": list(self.lplc2_drive_mv_eq),
            "population_spike_summaries": [
                item.to_dict() for item in self.population_spike_summaries
            ],
            "selected_body_telemetry": self._body_telemetry_dict(),
            "spike_events": [_event_to_dict(event) for event in self.spike_events],
            "delivered_events": [
                _event_to_dict(event) for event in self.delivered_events
            ],
            "delivered_event_summaries": [
                {
                    "target_body_id": body_id,
                    "event_count": count,
                    "event_increment_sum_mV_eq": total,
                    "delivery_times_ms": list(times),
                }
                for body_id, count, total, times in self.delivered_event_summaries
            ],
            "dnp01_first_spike_time_ms": [
                {"body_id": body_id, "time_ms": time_ms}
                for body_id, time_ms in self.dnp01_first_spike_time_ms
            ],
            "deterministic_replay_verified": self.deterministic_replay_verified,
            "validation_status": self.validation_status,
        }
        if include_result_sha256:
            result["result_sha256"] = self.result_sha256
        return result

    def to_manifest_dict(self) -> dict[str, Any]:
        """Return a small deterministic manifest without full trajectories."""

        return {
            "manifest_schema_version": "experiment_manifest_v1",
            "experiment_id": self.config.experiment_id,
            "config": self.config.to_dict(),
            "config_sha256": self.config_sha256,
            "result_sha256": self.result_sha256,
            "encoding_sha256": self.encoding_sha256,
            "external_drive_provenance_id": self.external_drive_provenance_id,
            "candidate": {
                "identifier": self.candidate_identifier,
                "version": self.candidate_version,
                "dataset": self.dataset,
            },
            "circuit_integrity": [list(entry) for entry in self.circuit_integrity],
            "graph_scope_id": self.graph_scope_id,
            "simulation_model": {
                "id": self.simulation_model_id,
                "version": self.simulation_model_version,
            },
            "steps": self.config.steps,
            "duration_ms": self.config.duration_ms,
            "dt_ms": self.config.dt_ms,
            "telemetry_profile": self.config.telemetry.to_dict(),
            "population_spike_summaries": [
                item.to_dict() for item in self.population_spike_summaries
            ],
            "dnp01_first_spike_time_ms": [
                {"body_id": body_id, "time_ms": time_ms}
                for body_id, time_ms in self.dnp01_first_spike_time_ms
            ],
            "delivered_event_summaries": [
                {
                    "target_body_id": body_id,
                    "event_count": count,
                    "event_increment_sum_mV_eq": total,
                    "delivery_times_ms": list(times),
                }
                for body_id, count, total, times in self.delivered_event_summaries
            ],
            "deterministic_replay_verified": self.deterministic_replay_verified,
            "validation_status": self.validation_status,
            "execution_metadata": dict(self.execution_metadata),
        }

    def write_manifest(self, path: str | Path) -> Path:
        """Write an explicitly requested small manifest using atomic replace."""

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.tmp")
        payload = json.dumps(
            self.to_manifest_dict(),
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            indent=2,
        )
        try:
            temporary.write_text(payload + "\n", encoding="utf-8")
            os.replace(temporary, destination)
        except OSError as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise ExperimentExecutionError(
                f"could not write experiment manifest {destination!s}"
            ) from exc
        return destination


def _simulation_results_equal(
    first: SimulationResult, second: SimulationResult
) -> bool:
    if first.body_ids != second.body_ids:
        return False
    if first.neuron_types != second.neuron_types:
        return False
    if first.neuron_sides != second.neuron_sides:
        return False
    if (
        first.spikes != second.spikes
        or first.delivered_events != second.delivered_events
    ):
        return False
    if dict(first.first_spike_time_ms_by_body_id) != dict(
        second.first_spike_time_ms_by_body_id
    ):
        return False
    return all(
        np.array_equal(getattr(first, name), getattr(second, name))
        for name in (
            "times_ms",
            "membrane_mv",
            "synaptic_mveq",
            "external_drive_mveq",
            "incoming_coupling_mveq",
        )
    )


def _recorded_body_ids(
    graph: SimulationGraph, telemetry: TelemetrySpec
) -> tuple[int, ...]:
    dnp_ids = {node.body_id for node in graph.nodes if node.type == READOUT_TYPE}
    visual_by_id = {
        node.body_id: node for node in graph.nodes if node.type in {"LC4", "LPLC2"}
    }
    unknown = set(telemetry.selected_visual_body_ids) - set(visual_by_id)
    if unknown:
        raise ExperimentConfigurationError(
            f"telemetry selected unknown/non-visual body IDs: {sorted(unknown)}"
        )
    requested = dnp_ids | set(telemetry.selected_visual_body_ids)
    return tuple(node.body_id for node in graph.nodes if node.body_id in requested)


def _event_summaries(
    graph: SimulationGraph, events: tuple[DeliveredSynapticEvent, ...]
) -> tuple[tuple[int, int, float, tuple[float, ...]], ...]:
    summaries = []
    for node in graph.nodes:
        if node.type != READOUT_TYPE:
            continue
        target_events = tuple(
            event for event in events if event.target_body_id == node.body_id
        )
        summaries.append(
            (
                node.body_id,
                len(target_events),
                float(sum(event.event_increment_mV_eq for event in target_events)),
                tuple(event.delivery_time_ms for event in target_events),
            )
        )
    return tuple(summaries)


def _body_telemetry(
    graph: SimulationGraph,
    result: SimulationResult,
    body_ids: tuple[int, ...],
) -> tuple[BodyTelemetry, ...]:
    telemetry = []
    for body_id in body_ids:
        index = result.body_ids.index(body_id)
        node = graph.nodes[graph.node_index_by_body_id[body_id]]
        telemetry.append(
            BodyTelemetry(
                body_id=body_id,
                neuron_type=node.type,
                soma_side=node.soma_side,
                times_ms=_tuple_float(result.times_ms, f"body {body_id} times_ms"),
                membrane_mv=_tuple_float(
                    result.membrane_mv[:, index], f"body {body_id} membrane_mv"
                ),
                synaptic_mveq=_tuple_float(
                    result.synaptic_mveq[:, index], f"body {body_id} synaptic_mveq"
                ),
                external_drive_mveq=_tuple_float(
                    result.external_drive_mveq[:, index],
                    f"body {body_id} external_drive_mveq",
                ),
                incoming_coupling_mveq=_tuple_float(
                    result.incoming_coupling_mveq[:, index],
                    f"body {body_id} incoming_coupling_mveq",
                ),
            )
        )
    return tuple(telemetry)


class ExperimentRunner:
    """Compose the validated contract, encoder, and deterministic LIF core."""

    def __init__(self, circuit_contract: Any) -> None:
        try:
            graph = build_phase2b_graph(circuit_contract)
            graph.validate_phase2b_scope()
            source_endpoint = getattr(
                getattr(circuit_contract, "provenance", None), "endpoint", None
            )
            _identifier(source_endpoint, "circuit provenance endpoint")
        except Exception as exc:
            raise ExperimentConfigurationError(
                "could not construct the validated Phase 2B graph"
            ) from exc
        self.graph = graph
        self.source_endpoint = source_endpoint

    def _validate_config(self, config: ExperimentConfig) -> None:
        if not isinstance(config, ExperimentConfig):
            raise ExperimentConfigurationError("config must be an ExperimentConfig.")
        if config.candidate_identifier != self.graph.candidate_identifier:
            raise ExperimentConfigurationError(
                "candidate identifier does not match graph."
            )
        if config.candidate_version != self.graph.candidate_version:
            raise ExperimentConfigurationError(
                "candidate version does not match graph."
            )
        if config.dataset != self.graph.dataset:
            raise ExperimentConfigurationError("dataset does not match graph.")
        if config.source_endpoint != self.source_endpoint:
            raise ExperimentConfigurationError(
                "source endpoint does not match the circuit contract."
            )
        if config.graph_scope_id != self.graph.graph_scope_id:
            raise ExperimentConfigurationError("graph scope does not match graph.")
        if tuple(config.circuit_integrity) != tuple(
            sorted(self.graph.circuit_integrity)
        ):
            raise ExperimentConfigurationError(
                "circuit integrity does not match the graph source snapshot."
            )
        _recorded_body_ids(self.graph, config.telemetry)

    def run(self, config: ExperimentConfig) -> ExperimentResult:
        """Run one complete production pipeline and verify an exact replay."""

        self._validate_config(config)
        scenario = LoomingTrajectoryScenario(
            identifier=config.experiment_id,
            stimulus=config.stimulus,
            sample_duration_ms=config.duration_ms,
        )
        try:
            samples = sample_looming_trajectory(scenario, dt_ms=config.dt_ms)
            encoding = encode_level_p(
                samples=samples,
                graph=self.graph,
                config=config.encoder_config,
                dt_ms=config.dt_ms,
                stimulus_identity=config.experiment_id,
            )
            schedule = apply_pathway_condition(
                encoding, self.graph, config.pathway_condition
            )
            record_ids = _recorded_body_ids(self.graph, config.telemetry)
            simulator = LIFSimulator(self.graph, config.lif_config)
            first = simulator.run(schedule, record_body_ids=record_ids)
            replay = simulator.run(schedule, record_body_ids=record_ids)
        except ExperimentError:
            raise
        except Exception as exc:
            raise ExperimentExecutionError(
                "experiment pipeline execution failed"
            ) from exc
        if not _simulation_results_equal(first, replay):
            raise ExperimentReplayError("deterministic experiment replay failed.")
        if schedule.to_matrix(self.graph)[
            :,
            [
                index
                for index, node in enumerate(self.graph.nodes)
                if node.type == READOUT_TYPE
            ],
        ].any():
            raise ExperimentExecutionError("normal experiment drive targeted DNp01.")
        applied_by_body_id = dict(schedule.by_body_id)
        first_lc4 = next(
            node.body_id for node in self.graph.nodes if node.type == "LC4"
        )
        first_lplc2 = next(
            node.body_id for node in self.graph.nodes if node.type == "LPLC2"
        )
        dnp_ids = tuple(
            node.body_id for node in self.graph.nodes if node.type == READOUT_TYPE
        )
        dnp_first = tuple(
            (body_id, first.first_spike_time_ms_by_body_id.get(body_id))
            for body_id in dnp_ids
        )
        return ExperimentResult(
            result_schema_version=EXPERIMENT_SCHEMA_VERSION,
            config=config,
            config_sha256=config.sha256,
            encoding_sha256=encoding.encoding_sha256,
            external_drive_provenance_id=schedule.provenance_id,
            candidate_identifier=self.graph.candidate_identifier,
            candidate_version=self.graph.candidate_version,
            dataset=self.graph.dataset,
            circuit_integrity=self.graph.circuit_integrity,
            graph_scope_id=self.graph.graph_scope_id,
            simulation_model_id=config.lif_config.model_id,
            simulation_model_version=config.lif_config.model_version,
            stimulus_samples=samples,
            times_ms=_tuple_float(first.times_ms, "times_ms"),
            stimulus_theta_rad=tuple(sample.angular_size_rad for sample in samples),
            stimulus_dtheta_dt_rad_s=tuple(
                float(sample.angular_expansion_velocity_rad_s) for sample in samples
            ),
            lc4_normalized=encoding.lc4_normalized,
            lplc2_normalized=encoding.lplc2_normalized,
            lc4_drive_mv_eq=tuple(applied_by_body_id[first_lc4]),
            lplc2_drive_mv_eq=tuple(applied_by_body_id[first_lplc2]),
            population_spike_summaries=tuple(
                _population_summary(self.graph, first, neuron_type)
                for neuron_type in ("LC4", "LPLC2")
            ),
            selected_body_telemetry=_body_telemetry(self.graph, first, record_ids),
            spike_events=first.spikes,
            delivered_events=first.delivered_events,
            delivered_event_summaries=_event_summaries(
                self.graph, first.delivered_events
            ),
            dnp01_first_spike_time_ms=dnp_first,
            deterministic_replay_verified=True,
            validation_status=config.validation_status,
        )


def run_experiment(circuit_contract: Any, config: ExperimentConfig) -> ExperimentResult:
    """Convenience wrapper for one deterministic offline experiment."""

    return ExperimentRunner(circuit_contract).run(config)


def verify_replay(first: ExperimentResult, second: ExperimentResult) -> bool:
    """Require exact equality of two scientifically meaningful run results."""

    if not isinstance(first, ExperimentResult) or not isinstance(
        second, ExperimentResult
    ):
        raise ExperimentReplayError("verify_replay requires ExperimentResult values.")
    if first.result_sha256 != second.result_sha256:
        raise ExperimentReplayError(
            "experiment result digests differ; deterministic replay failed."
        )
    return True


__all__ = [
    "EXPERIMENT_SCHEMA_VERSION",
    "TELEMETRY_PROFILE_VALIDATION_V1",
    "VALIDATION_STATUS_NOT_EVALUATED",
    "ExperimentError",
    "ExperimentConfigurationError",
    "ExperimentExecutionError",
    "ExperimentReplayError",
    "TelemetrySpec",
    "ExperimentConfig",
    "BodyTelemetry",
    "PopulationSpikeSummary",
    "ExperimentResult",
    "ExperimentRunner",
    "run_experiment",
    "verify_replay",
]
