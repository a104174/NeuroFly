"""Deterministic comparison of completed NeuroFly experiment artifacts.

This module compares NeuroFly model runs with other NeuroFly model runs.  It
does not compare simulations with experimental data, fit parameters, rank
outcomes, or align trajectories.  Pointwise metrics are available only when
the persisted simulation time bases are exactly equal; otherwise the result
is summary-only.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Any

from neurofly.experiment_artifacts import (
    LoadedExperimentArtifact,
    load_experiment_artifact,
)
from neurofly.experiments import ExperimentResult

COMPARISON_SCHEMA_VERSION = "experiment_comparison_v1"
VALIDATION_STATUS_NOT_EVALUATED = "NOT_EVALUATED"
_EXPECTED_DNP01_IDS = (10001, 10010)
_VISUAL_TYPES = ("LC4", "LPLC2")


class ExperimentComparisonError(RuntimeError):
    """Base error for deterministic experiment comparisons."""


class ComparisonConfigurationError(ExperimentComparisonError):
    """The comparison policy is malformed or unsupported."""


class ComparisonCompatibility(StrEnum):
    """Scientific comparability of two valid model artifacts."""

    EXACT_REPLAY_EQUIVALENT = "EXACT_REPLAY_EQUIVALENT"
    DIRECT_MODEL_COMPARISON = "DIRECT_MODEL_COMPARISON"
    SUMMARY_ONLY_COMPARISON = "SUMMARY_ONLY_COMPARISON"
    INCOMPATIBLE = "INCOMPATIBLE"


def _identifier(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ComparisonConfigurationError(f"{field_name} must be a non-empty string.")
    return value


def _canonical_json(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ExperimentComparisonError(
            "comparison result is not deterministically JSON serializable"
        ) from exc


def _sha256_json(value: Any) -> str:
    return sha256(_canonical_json(value)).hexdigest()


def _delta_b_minus_a(value_a: float, value_b: float) -> float:
    return value_b - value_a


def _optional_delta(value_a: float | None, value_b: float | None) -> float | None:
    if value_a is None or value_b is None:
        return None
    return _delta_b_minus_a(value_a, value_b)


def _timing_semantics(value_a: float | None, value_b: float | None) -> str:
    if value_a is None and value_b is None:
        return "NONE_BOTH"
    if value_a is None:
        return "B_ONLY"
    if value_b is None:
        return "A_ONLY"
    return "NUMERIC_DELTA"


def _peak(values: tuple[float, ...]) -> float:
    if not values:
        raise ExperimentComparisonError("cannot compute a peak from an empty series.")
    return max(values)


def _trajectory_error(
    values_a: tuple[float, ...], values_b: tuple[float, ...]
) -> tuple[float, float]:
    if len(values_a) != len(values_b) or not values_a:
        raise ExperimentComparisonError(
            "trajectory arrays are not pointwise compatible."
        )
    squared = 0.0
    maximum = 0.0
    for value_a, value_b in zip(values_a, values_b, strict=True):
        difference = abs(value_b - value_a)
        maximum = max(maximum, difference)
        squared += difference * difference
    return maximum, math.sqrt(squared / len(values_a))


def _recursive_differences(
    value_a: Any,
    value_b: Any,
    path: str,
    excluded_paths: frozenset[str],
) -> list["ConfigurationDifference"]:
    if path in excluded_paths:
        return []
    if isinstance(value_a, dict) and isinstance(value_b, dict):
        differences: list[ConfigurationDifference] = []
        for key in sorted(set(value_a) | set(value_b)):
            child_path = f"{path}.{key}" if path else str(key)
            if key not in value_a or key not in value_b:
                differences.append(
                    ConfigurationDifference(
                        path=child_path,
                        value_a=value_a.get(key),
                        value_b=value_b.get(key),
                    )
                )
            else:
                differences.extend(
                    _recursive_differences(
                        value_a[key], value_b[key], child_path, excluded_paths
                    )
                )
        return differences
    if value_a != value_b:
        return [ConfigurationDifference(path=path, value_a=value_a, value_b=value_b)]
    return []


@dataclass(frozen=True, slots=True)
class ExperimentComparisonConfig:
    """Fixed comparison policy; no alignment or optimization knobs exist."""

    schema_version: str = COMPARISON_SCHEMA_VERSION
    source_policy: str = "same_source_direct_only_v1"
    telemetry_policy: str = "common_selected_bodies_v1"
    time_base_policy: str = "exact_pointwise_time_base_only_v1"
    event_policy: str = "exact_sequence_only_v1"

    def __post_init__(self) -> None:
        _identifier(self.schema_version, "schema_version")
        if self.schema_version != COMPARISON_SCHEMA_VERSION:
            raise ComparisonConfigurationError(
                f"unsupported comparison schema {self.schema_version!r}."
            )
        expected = {
            "source_policy": "same_source_direct_only_v1",
            "telemetry_policy": "common_selected_bodies_v1",
            "time_base_policy": "exact_pointwise_time_base_only_v1",
            "event_policy": "exact_sequence_only_v1",
        }
        for name, expected_value in expected.items():
            value = _identifier(getattr(self, name), name)
            if value != expected_value:
                raise ComparisonConfigurationError(
                    f"unsupported {name} {value!r}; expected {expected_value!r}."
                )

    def to_dict(self) -> dict[str, str]:
        return {
            "schema_version": self.schema_version,
            "source_policy": self.source_policy,
            "telemetry_policy": self.telemetry_policy,
            "time_base_policy": self.time_base_policy,
            "event_policy": self.event_policy,
        }


@dataclass(frozen=True, slots=True)
class ConfigurationDifference:
    """One directional configuration difference; values are B minus A context."""

    path: str
    value_a: Any
    value_b: Any

    def __post_init__(self) -> None:
        _identifier(self.path, "configuration difference path")

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "value_a": self.value_a,
            "value_b": self.value_b,
        }


@dataclass(frozen=True, slots=True)
class TelemetryCompatibility:
    """Coverage and time-base result for selected persisted telemetry."""

    dense_trajectory_comparable: bool
    same_time_base: bool
    dt_ms_a: float
    dt_ms_b: float
    duration_ms_a: float
    duration_ms_b: float
    sample_count_a: int
    sample_count_b: int
    common_body_ids: tuple[int, ...]
    missing_body_ids_in_a: tuple[int, ...]
    missing_body_ids_in_b: tuple[int, ...]
    reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "dense_trajectory_comparable": self.dense_trajectory_comparable,
            "same_time_base": self.same_time_base,
            "dt_ms_a": self.dt_ms_a,
            "dt_ms_b": self.dt_ms_b,
            "duration_ms_a": self.duration_ms_a,
            "duration_ms_b": self.duration_ms_b,
            "sample_count_a": self.sample_count_a,
            "sample_count_b": self.sample_count_b,
            "common_body_ids": list(self.common_body_ids),
            "missing_body_ids_in_a": list(self.missing_body_ids_in_a),
            "missing_body_ids_in_b": list(self.missing_body_ids_in_b),
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class TrajectoryMetrics:
    """Pointwise directional errors for one selected body's trajectories."""

    body_id: int
    sample_count: int
    max_abs_membrane_difference_mv: float
    rms_membrane_difference_mv: float
    max_abs_synaptic_difference_mveq: float
    rms_synaptic_difference_mveq: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "body_id": self.body_id,
            "sample_count": self.sample_count,
            "max_abs_membrane_difference_mv": self.max_abs_membrane_difference_mv,
            "rms_membrane_difference_mv": self.rms_membrane_difference_mv,
            "max_abs_synaptic_difference_mveq": self.max_abs_synaptic_difference_mveq,
            "rms_synaptic_difference_mveq": self.rms_synaptic_difference_mveq,
        }


@dataclass(frozen=True, slots=True)
class PopulationComparison:
    """LC4 or LPLC2 population summary with directional deltas."""

    neuron_type: str
    body_count_a: int
    body_count_b: int
    total_spike_count_a: int
    total_spike_count_b: int
    total_spike_count_difference: int
    first_population_spike_time_ms_a: float | None
    first_population_spike_time_ms_b: float | None
    first_population_spike_time_difference_ms: float | None
    first_population_spike_timing_status: str
    peak_normalized_feature_a: float
    peak_normalized_feature_b: float
    peak_normalized_feature_difference: float
    peak_drive_mv_eq_a: float
    peak_drive_mv_eq_b: float
    peak_drive_difference_mv_eq: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "neuron_type": self.neuron_type,
            "body_count_a": self.body_count_a,
            "body_count_b": self.body_count_b,
            "total_spike_count_a": self.total_spike_count_a,
            "total_spike_count_b": self.total_spike_count_b,
            "total_spike_count_difference": self.total_spike_count_difference,
            "first_population_spike_time_ms_a": self.first_population_spike_time_ms_a,
            "first_population_spike_time_ms_b": self.first_population_spike_time_ms_b,
            "first_population_spike_time_difference_ms": (
                self.first_population_spike_time_difference_ms
            ),
            "first_population_spike_timing_status": (
                self.first_population_spike_timing_status
            ),
            "peak_normalized_feature_a": self.peak_normalized_feature_a,
            "peak_normalized_feature_b": self.peak_normalized_feature_b,
            "peak_normalized_feature_difference": (
                self.peak_normalized_feature_difference
            ),
            "peak_drive_mv_eq_a": self.peak_drive_mv_eq_a,
            "peak_drive_mv_eq_b": self.peak_drive_mv_eq_b,
            "peak_drive_difference_mv_eq": self.peak_drive_difference_mv_eq,
        }


@dataclass(frozen=True, slots=True)
class DNp01Comparison:
    """Independent comparison for one of the two validated DNp01 bodies."""

    body_id: int
    total_spike_count_a: int
    total_spike_count_b: int
    total_spike_count_difference: int
    first_spike_time_ms_a: float | None
    first_spike_time_ms_b: float | None
    first_spike_time_difference_ms: float | None
    first_spike_timing_status: str
    peak_membrane_mv_a: float
    peak_membrane_mv_b: float
    peak_membrane_difference_mv: float
    peak_synaptic_mveq_a: float
    peak_synaptic_mveq_b: float
    peak_synaptic_difference_mveq: float
    delivered_event_count_a: int
    delivered_event_count_b: int
    delivered_event_count_difference: int
    model_increment_sum_mveq_a: float
    model_increment_sum_mveq_b: float
    model_increment_sum_difference_mveq: float
    trajectory_metrics: TrajectoryMetrics | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "body_id": self.body_id,
            "total_spike_count_a": self.total_spike_count_a,
            "total_spike_count_b": self.total_spike_count_b,
            "total_spike_count_difference": self.total_spike_count_difference,
            "first_spike_time_ms_a": self.first_spike_time_ms_a,
            "first_spike_time_ms_b": self.first_spike_time_ms_b,
            "first_spike_time_difference_ms": self.first_spike_time_difference_ms,
            "first_spike_timing_status": self.first_spike_timing_status,
            "peak_membrane_mv_a": self.peak_membrane_mv_a,
            "peak_membrane_mv_b": self.peak_membrane_mv_b,
            "peak_membrane_difference_mv": self.peak_membrane_difference_mv,
            "peak_synaptic_mveq_a": self.peak_synaptic_mveq_a,
            "peak_synaptic_mveq_b": self.peak_synaptic_mveq_b,
            "peak_synaptic_difference_mveq": self.peak_synaptic_difference_mveq,
            "delivered_event_count_a": self.delivered_event_count_a,
            "delivered_event_count_b": self.delivered_event_count_b,
            "delivered_event_count_difference": self.delivered_event_count_difference,
            "model_increment_sum_mveq_a": self.model_increment_sum_mveq_a,
            "model_increment_sum_mveq_b": self.model_increment_sum_mveq_b,
            "model_increment_sum_difference_mveq": (
                self.model_increment_sum_difference_mveq
            ),
            "trajectory_metrics": (
                None
                if self.trajectory_metrics is None
                else self.trajectory_metrics.to_dict()
            ),
        }


@dataclass(frozen=True, slots=True)
class EventComparison:
    """Event counts and exact-sequence checks without artificial event pairing."""

    total_spike_event_count_a: int
    total_spike_event_count_b: int
    total_spike_event_count_difference: int
    total_delivered_event_count_a: int
    total_delivered_event_count_b: int
    total_delivered_event_count_difference: int
    spike_event_sequences_equal: bool
    delivered_event_sequences_equal: bool
    event_pairing_policy: str = "exact_sequence_only_v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_spike_event_count_a": self.total_spike_event_count_a,
            "total_spike_event_count_b": self.total_spike_event_count_b,
            "total_spike_event_count_difference": (
                self.total_spike_event_count_difference
            ),
            "total_delivered_event_count_a": self.total_delivered_event_count_a,
            "total_delivered_event_count_b": self.total_delivered_event_count_b,
            "total_delivered_event_count_difference": (
                self.total_delivered_event_count_difference
            ),
            "spike_event_sequences_equal": self.spike_event_sequences_equal,
            "delivered_event_sequences_equal": self.delivered_event_sequences_equal,
            "event_pairing_policy": self.event_pairing_policy,
        }


@dataclass(frozen=True, slots=True)
class ExperimentComparisonResult:
    """Immutable, directional comparison report for artifacts A and B."""

    comparison_schema_version: str
    comparison_config: ExperimentComparisonConfig
    artifact_a_id: str
    artifact_b_id: str
    config_a_sha256: str
    config_b_sha256: str
    result_a_sha256: str
    result_b_sha256: str
    compatibility: ComparisonCompatibility
    configuration_differences: tuple[ConfigurationDifference, ...]
    source_model_differences: tuple[ConfigurationDifference, ...]
    telemetry: TelemetryCompatibility
    pathway_condition_a: str
    pathway_condition_b: str
    visual_populations: tuple[PopulationComparison, ...]
    dnp01: tuple[DNp01Comparison, ...]
    events: EventComparison
    limitations: tuple[str, ...]
    empirical_validation_status: str = VALIDATION_STATUS_NOT_EVALUATED
    comparison_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        if self.comparison_schema_version != COMPARISON_SCHEMA_VERSION:
            raise ComparisonConfigurationError("unsupported comparison schema.")
        if not isinstance(self.comparison_config, ExperimentComparisonConfig):
            raise ComparisonConfigurationError("comparison_config is invalid.")
        _identifier(self.artifact_a_id, "artifact_a_id")
        _identifier(self.artifact_b_id, "artifact_b_id")
        _identifier(self.config_a_sha256, "config_a_sha256")
        _identifier(self.config_b_sha256, "config_b_sha256")
        _identifier(self.result_a_sha256, "result_a_sha256")
        _identifier(self.result_b_sha256, "result_b_sha256")
        if self.empirical_validation_status != VALIDATION_STATUS_NOT_EVALUATED:
            raise ComparisonConfigurationError(
                "Phase 3C comparisons remain NOT_EVALUATED."
            )
        if tuple(item.body_id for item in self.dnp01) != _EXPECTED_DNP01_IDS:
            raise ComparisonConfigurationError(
                "comparison must retain DNp01 bodies 10001 and 10010 separately."
            )
        if tuple(item.neuron_type for item in self.visual_populations) != _VISUAL_TYPES:
            raise ComparisonConfigurationError(
                "comparison must retain LC4 and LPLC2 separately."
            )
        object.__setattr__(
            self, "configuration_differences", tuple(self.configuration_differences)
        )
        object.__setattr__(
            self, "source_model_differences", tuple(self.source_model_differences)
        )
        object.__setattr__(self, "visual_populations", tuple(self.visual_populations))
        object.__setattr__(self, "dnp01", tuple(self.dnp01))
        object.__setattr__(self, "limitations", tuple(self.limitations))
        object.__setattr__(
            self,
            "comparison_sha256",
            _sha256_json(self.to_dict(include_comparison_sha256=False)),
        )

    def to_dict(self, *, include_comparison_sha256: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "comparison_schema_version": self.comparison_schema_version,
            "comparison_config": self.comparison_config.to_dict(),
            "artifact_a_id": self.artifact_a_id,
            "artifact_b_id": self.artifact_b_id,
            "config_a_sha256": self.config_a_sha256,
            "config_b_sha256": self.config_b_sha256,
            "result_a_sha256": self.result_a_sha256,
            "result_b_sha256": self.result_b_sha256,
            "compatibility": self.compatibility.value,
            "configuration_differences": [
                item.to_dict() for item in self.configuration_differences
            ],
            "source_model_differences": [
                item.to_dict() for item in self.source_model_differences
            ],
            "telemetry": self.telemetry.to_dict(),
            "pathway": {
                "condition_a": self.pathway_condition_a,
                "condition_b": self.pathway_condition_b,
                "different": self.pathway_condition_a != self.pathway_condition_b,
            },
            "visual_populations": [item.to_dict() for item in self.visual_populations],
            "dnp01": [item.to_dict() for item in self.dnp01],
            "events": self.events.to_dict(),
            "limitations": list(self.limitations),
            "empirical_validation_status": self.empirical_validation_status,
        }
        if include_comparison_sha256:
            result["comparison_sha256"] = self.comparison_sha256
        return result

    def to_json(self) -> str:
        """Return a deterministic JSON comparison summary."""

        return _canonical_json(self.to_dict()).decode("utf-8")


def _source_model_identity(result: ExperimentResult) -> dict[str, Any]:
    config = result.config
    return {
        "candidate.identifier": result.candidate_identifier,
        "candidate.version": result.candidate_version,
        "dataset": result.dataset,
        "source.endpoint": config.source_endpoint,
        "source.circuit_integrity": [list(entry) for entry in config.circuit_integrity],
        "graph_scope_id": result.graph_scope_id,
        "encoder.id": config.encoder_config.encoder_id,
        "encoder.version": config.encoder_config.encoder_version,
        "neural_model.id": config.lif_config.model_id,
        "neural_model.version": config.lif_config.model_version,
    }


def _configuration_differences(
    result_a: ExperimentResult, result_b: ExperimentResult
) -> tuple[ConfigurationDifference, ...]:
    config_a = result_a.config.to_dict()
    config_b = result_b.config.to_dict()
    excluded = frozenset(
        {
            "schema_version",
            "experiment_id",
            "candidate",
            "source",
            "graph_scope_id",
            "encoder.encoder_id",
            "encoder.encoder_version",
            "neural.model_id",
            "neural.model_version",
            "neural.graph_scope_id",
        }
    )
    return tuple(_recursive_differences(config_a, config_b, "", excluded))


def _source_model_differences(
    result_a: ExperimentResult, result_b: ExperimentResult
) -> tuple[ConfigurationDifference, ...]:
    return tuple(
        _recursive_differences(
            _source_model_identity(result_a),
            _source_model_identity(result_b),
            "",
            frozenset(),
        )
    )


def _body_map(result: ExperimentResult) -> dict[int, Any]:
    return {item.body_id: item for item in result.selected_body_telemetry}


def _telemetry_compatibility(
    result_a: ExperimentResult,
    result_b: ExperimentResult,
    *,
    source_compatible: bool = True,
) -> TelemetryCompatibility:
    bodies_a = set(_body_map(result_a))
    bodies_b = set(_body_map(result_b))
    common = tuple(sorted(bodies_a & bodies_b))
    missing_in_a = tuple(sorted(bodies_b - bodies_a))
    missing_in_b = tuple(sorted(bodies_a - bodies_b))
    same_time_base = (
        result_a.times_ms == result_b.times_ms
        and result_a.config.dt_ms == result_b.config.dt_ms
        and result_a.config.duration_ms == result_b.config.duration_ms
    )
    reasons: list[str] = []
    if not source_compatible:
        reasons.append("source_or_model_mismatch: dense metrics blocked")
    if not same_time_base:
        reasons.append(
            "time_base_mismatch: pointwise trajectory metrics omitted; no interpolation"
        )
    if missing_in_a or missing_in_b:
        reasons.append("telemetry_coverage_mismatch: common bodies only")
    return TelemetryCompatibility(
        dense_trajectory_comparable=source_compatible
        and same_time_base
        and all(body_id in common for body_id in _EXPECTED_DNP01_IDS),
        same_time_base=same_time_base,
        dt_ms_a=result_a.config.dt_ms,
        dt_ms_b=result_b.config.dt_ms,
        duration_ms_a=result_a.config.duration_ms,
        duration_ms_b=result_b.config.duration_ms,
        sample_count_a=result_a.config.steps,
        sample_count_b=result_b.config.steps,
        common_body_ids=common,
        missing_body_ids_in_a=missing_in_a,
        missing_body_ids_in_b=missing_in_b,
        reason="; ".join(reasons) if reasons else None,
    )


def _trajectory_metrics(
    body_id: int,
    result_a: ExperimentResult,
    result_b: ExperimentResult,
    telemetry: TelemetryCompatibility,
) -> TrajectoryMetrics | None:
    if not telemetry.dense_trajectory_comparable:
        return None
    bodies_a = _body_map(result_a)
    bodies_b = _body_map(result_b)
    if body_id not in bodies_a or body_id not in bodies_b:
        return None
    body_a = bodies_a[body_id]
    body_b = bodies_b[body_id]
    if body_a.times_ms != body_b.times_ms:
        return None
    membrane_max, membrane_rms = _trajectory_error(
        body_a.membrane_mv, body_b.membrane_mv
    )
    synaptic_max, synaptic_rms = _trajectory_error(
        body_a.synaptic_mveq, body_b.synaptic_mveq
    )
    return TrajectoryMetrics(
        body_id=body_id,
        sample_count=len(body_a.times_ms),
        max_abs_membrane_difference_mv=membrane_max,
        rms_membrane_difference_mv=membrane_rms,
        max_abs_synaptic_difference_mveq=synaptic_max,
        rms_synaptic_difference_mveq=synaptic_rms,
    )


def _population_summary_map(result: ExperimentResult) -> dict[str, Any]:
    return {item.neuron_type: item for item in result.population_spike_summaries}


def _population_comparison(
    result_a: ExperimentResult, result_b: ExperimentResult, neuron_type: str
) -> PopulationComparison:
    summaries_a = _population_summary_map(result_a)
    summaries_b = _population_summary_map(result_b)
    summary_a = summaries_a[neuron_type]
    summary_b = summaries_b[neuron_type]
    if neuron_type == "LC4":
        normalized_a = result_a.lc4_normalized
        normalized_b = result_b.lc4_normalized
        drive_a = result_a.lc4_drive_mv_eq
        drive_b = result_b.lc4_drive_mv_eq
    else:
        normalized_a = result_a.lplc2_normalized
        normalized_b = result_b.lplc2_normalized
        drive_a = result_a.lplc2_drive_mv_eq
        drive_b = result_b.lplc2_drive_mv_eq
    first_a = summary_a.first_population_spike_time_ms
    first_b = summary_b.first_population_spike_time_ms
    return PopulationComparison(
        neuron_type=neuron_type,
        body_count_a=summary_a.body_count,
        body_count_b=summary_b.body_count,
        total_spike_count_a=summary_a.total_spike_count,
        total_spike_count_b=summary_b.total_spike_count,
        total_spike_count_difference=summary_b.total_spike_count
        - summary_a.total_spike_count,
        first_population_spike_time_ms_a=first_a,
        first_population_spike_time_ms_b=first_b,
        first_population_spike_time_difference_ms=_optional_delta(first_a, first_b),
        first_population_spike_timing_status=_timing_semantics(first_a, first_b),
        peak_normalized_feature_a=_peak(normalized_a),
        peak_normalized_feature_b=_peak(normalized_b),
        peak_normalized_feature_difference=_delta_b_minus_a(
            _peak(normalized_a), _peak(normalized_b)
        ),
        peak_drive_mv_eq_a=_peak(drive_a),
        peak_drive_mv_eq_b=_peak(drive_b),
        peak_drive_difference_mv_eq=_delta_b_minus_a(_peak(drive_a), _peak(drive_b)),
    )


def _dnp_first_map(result: ExperimentResult) -> dict[int, float | None]:
    return dict(result.dnp01_first_spike_time_ms)


def _dnp_spike_count(result: ExperimentResult, body_id: int) -> int:
    return sum(event.body_id == body_id for event in result.spike_events)


def _event_summary_map(
    result: ExperimentResult,
) -> dict[int, tuple[int, float, tuple[float, ...]]]:
    return {
        body_id: (count, increment_sum, delivery_times)
        for body_id, count, increment_sum, delivery_times in (
            result.delivered_event_summaries
        )
    }


def _dnp_comparison(
    result_a: ExperimentResult,
    result_b: ExperimentResult,
    body_id: int,
    telemetry: TelemetryCompatibility,
) -> DNp01Comparison:
    bodies_a = _body_map(result_a)
    bodies_b = _body_map(result_b)
    body_a = bodies_a[body_id]
    body_b = bodies_b[body_id]
    first_a = _dnp_first_map(result_a)[body_id]
    first_b = _dnp_first_map(result_b)[body_id]
    event_a = _event_summary_map(result_a)[body_id]
    event_b = _event_summary_map(result_b)[body_id]
    spike_count_a = _dnp_spike_count(result_a, body_id)
    spike_count_b = _dnp_spike_count(result_b, body_id)
    return DNp01Comparison(
        body_id=body_id,
        total_spike_count_a=spike_count_a,
        total_spike_count_b=spike_count_b,
        total_spike_count_difference=spike_count_b - spike_count_a,
        first_spike_time_ms_a=first_a,
        first_spike_time_ms_b=first_b,
        first_spike_time_difference_ms=_optional_delta(first_a, first_b),
        first_spike_timing_status=_timing_semantics(first_a, first_b),
        peak_membrane_mv_a=_peak(body_a.membrane_mv),
        peak_membrane_mv_b=_peak(body_b.membrane_mv),
        peak_membrane_difference_mv=_delta_b_minus_a(
            _peak(body_a.membrane_mv), _peak(body_b.membrane_mv)
        ),
        peak_synaptic_mveq_a=_peak(body_a.synaptic_mveq),
        peak_synaptic_mveq_b=_peak(body_b.synaptic_mveq),
        peak_synaptic_difference_mveq=_delta_b_minus_a(
            _peak(body_a.synaptic_mveq), _peak(body_b.synaptic_mveq)
        ),
        delivered_event_count_a=event_a[0],
        delivered_event_count_b=event_b[0],
        delivered_event_count_difference=event_b[0] - event_a[0],
        model_increment_sum_mveq_a=event_a[1],
        model_increment_sum_mveq_b=event_b[1],
        model_increment_sum_difference_mveq=event_b[1] - event_a[1],
        trajectory_metrics=_trajectory_metrics(body_id, result_a, result_b, telemetry),
    )


def _event_comparison(
    result_a: ExperimentResult, result_b: ExperimentResult
) -> EventComparison:
    return EventComparison(
        total_spike_event_count_a=len(result_a.spike_events),
        total_spike_event_count_b=len(result_b.spike_events),
        total_spike_event_count_difference=len(result_b.spike_events)
        - len(result_a.spike_events),
        total_delivered_event_count_a=len(result_a.delivered_events),
        total_delivered_event_count_b=len(result_b.delivered_events),
        total_delivered_event_count_difference=len(result_b.delivered_events)
        - len(result_a.delivered_events),
        spike_event_sequences_equal=result_a.spike_events == result_b.spike_events,
        delivered_event_sequences_equal=result_a.delivered_events
        == result_b.delivered_events,
    )


def _compatibility(
    artifact_a: LoadedExperimentArtifact,
    artifact_b: LoadedExperimentArtifact,
    configuration_differences: tuple[ConfigurationDifference, ...],
    source_model_differences: tuple[ConfigurationDifference, ...],
    telemetry: TelemetryCompatibility,
) -> tuple[ComparisonCompatibility, tuple[str, ...]]:
    limitations: list[str] = []
    if source_model_differences:
        limitations.append(
            "source_or_model_identity_mismatch: direct trajectory comparison is "
            "not permitted"
        )
        if telemetry.reason:
            limitations.append(telemetry.reason)
        return ComparisonCompatibility.SUMMARY_ONLY_COMPARISON, tuple(limitations)
    if (
        artifact_a.result.config_sha256 == artifact_b.result.config_sha256
        and artifact_a.result.result_sha256 == artifact_b.result.result_sha256
    ):
        if artifact_a.artifact_id == artifact_b.artifact_id:
            return ComparisonCompatibility.EXACT_REPLAY_EQUIVALENT, ()
        limitations.append("same_result_identity_with_distinct_artifact_identity")
        return ComparisonCompatibility.EXACT_REPLAY_EQUIVALENT, tuple(limitations)
    if artifact_a.result.config_sha256 == artifact_b.result.config_sha256:
        limitations.append(
            "same_config_identity_result_mismatch: deterministic replay output differs"
        )
        return ComparisonCompatibility.INCOMPATIBLE, tuple(limitations)
    if not telemetry.dense_trajectory_comparable:
        if telemetry.reason:
            limitations.append(telemetry.reason)
        return ComparisonCompatibility.SUMMARY_ONLY_COMPARISON, tuple(limitations)
    if telemetry.reason:
        limitations.append(telemetry.reason)
    if not configuration_differences:
        limitations.append("only_run_identity_or_non_model_metadata_differs")
    return ComparisonCompatibility.DIRECT_MODEL_COMPARISON, tuple(limitations)


def _coerce_loaded(
    value: str | Path | LoadedExperimentArtifact,
) -> LoadedExperimentArtifact:
    if isinstance(value, LoadedExperimentArtifact):
        return value
    return load_experiment_artifact(value)


def compare_experiment_artifacts(
    artifact_a: str | Path | LoadedExperimentArtifact,
    artifact_b: str | Path | LoadedExperimentArtifact,
    comparison_config: ExperimentComparisonConfig | None = None,
) -> ExperimentComparisonResult:
    """Compare two valid artifacts directionally as ``B - A``."""

    policy = (
        ExperimentComparisonConfig() if comparison_config is None else comparison_config
    )
    if not isinstance(policy, ExperimentComparisonConfig):
        raise ComparisonConfigurationError("comparison_config is invalid.")
    loaded_a = _coerce_loaded(artifact_a)
    loaded_b = _coerce_loaded(artifact_b)
    result_a = loaded_a.result
    result_b = loaded_b.result
    configuration_differences = _configuration_differences(result_a, result_b)
    source_model_differences = _source_model_differences(result_a, result_b)
    telemetry = _telemetry_compatibility(
        result_a,
        result_b,
        source_compatible=not source_model_differences,
    )
    compatibility, limitations = _compatibility(
        loaded_a,
        loaded_b,
        configuration_differences,
        source_model_differences,
        telemetry,
    )
    return ExperimentComparisonResult(
        comparison_schema_version=COMPARISON_SCHEMA_VERSION,
        comparison_config=policy,
        artifact_a_id=loaded_a.artifact_id,
        artifact_b_id=loaded_b.artifact_id,
        config_a_sha256=result_a.config_sha256,
        config_b_sha256=result_b.config_sha256,
        result_a_sha256=result_a.result_sha256,
        result_b_sha256=result_b.result_sha256,
        compatibility=compatibility,
        configuration_differences=configuration_differences,
        source_model_differences=source_model_differences,
        telemetry=telemetry,
        pathway_condition_a=result_a.config.pathway_condition.value,
        pathway_condition_b=result_b.config.pathway_condition.value,
        visual_populations=tuple(
            _population_comparison(result_a, result_b, neuron_type)
            for neuron_type in _VISUAL_TYPES
        ),
        dnp01=tuple(
            _dnp_comparison(result_a, result_b, body_id, telemetry)
            for body_id in _EXPECTED_DNP01_IDS
        ),
        events=_event_comparison(result_a, result_b),
        limitations=limitations,
    )


def inspect_comparison(result: ExperimentComparisonResult) -> dict[str, Any]:
    """Return the JSON-ready deterministic comparison summary."""

    if not isinstance(result, ExperimentComparisonResult):
        raise ExperimentComparisonError("result must be an ExperimentComparisonResult.")
    return result.to_dict()


def _main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare two NeuroFly experiment artifacts offline."
    )
    parser.add_argument("artifact_a", type=Path)
    parser.add_argument("artifact_b", type=Path)
    args = parser.parse_args()
    comparison = compare_experiment_artifacts(args.artifact_a, args.artifact_b)
    print(json.dumps(comparison.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by CLI smoke tests
    raise SystemExit(_main())


__all__ = [
    "COMPARISON_SCHEMA_VERSION",
    "VALIDATION_STATUS_NOT_EVALUATED",
    "ComparisonCompatibility",
    "ExperimentComparisonError",
    "ComparisonConfigurationError",
    "ExperimentComparisonConfig",
    "ConfigurationDifference",
    "TelemetryCompatibility",
    "TrajectoryMetrics",
    "PopulationComparison",
    "DNp01Comparison",
    "EventComparison",
    "ExperimentComparisonResult",
    "compare_experiment_artifacts",
    "inspect_comparison",
]
