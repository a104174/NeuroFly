"""Deterministic Phase 2F end-to-end looming trajectory characterization.

This module runs the production stimulus geometry, Level P E1 encoder, and
Phase 2B LIF simulator with explicitly synthetic benchmark parameters.  It is
an operating-regime probe, not a calibration or biological validation layer.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import Counter
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

import numpy as np

from neurofly.malecns.sensory import LoomingSample, LoomingStimulus
from neurofly.sensory_encoder import (
    LevelPEncoderConfig,
    LevelPEncodingResult,
    encode_level_p,
)
from neurofly.simulation import (
    READOUT_TYPE,
    ExternalDriveSchedule,
    LIFConfig,
    LIFSimulator,
    SimulationConfigurationError,
    SimulationGraph,
    SimulationResult,
)

BENCHMARK_SCHEMA_VERSION = "phase2f_trajectory_characterization_v1"
PROVENANCE_CLASSIFICATION = "NEUROFLY_SYNTHETIC_BENCHMARK"
FIXTURE_POLICY_ID = "explicit_synthetic_looming_trajectory_v1"


class TrajectoryCharacterizationError(ValueError):
    """A Phase 2F scenario, parameter point, or result is invalid."""


class PathwayCondition(StrEnum):
    """External-drive pathways retained after production E1 encoding."""

    ZERO = "ZERO"
    LC4_ONLY = "LC4_ONLY"
    LPLC2_ONLY = "LPLC2_ONLY"
    COMBINED = "COMBINED"


class OperatingRegime(StrEnum):
    """NeuroFly benchmark terminology, not biological behavior states."""

    R0 = "R0_NO_VISUAL_SPIKES"
    R1 = "R1_VISUAL_SPIKES_DNP01_SUBTHRESHOLD"
    R2 = "R2_ONE_DNP01_THRESHOLD"
    R3 = "R3_BOTH_DNP01_THRESHOLD"
    R4 = "R4_REPEATED_DNP01_SPIKES"


def _finite(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise TrajectoryCharacterizationError(f"{field_name} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise TrajectoryCharacterizationError(f"{field_name} must be finite.") from None
    if not math.isfinite(result):
        raise TrajectoryCharacterizationError(f"{field_name} must be finite.")
    return result


def _identifier(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise TrajectoryCharacterizationError(
            f"{field_name} must be a non-empty string."
        )
    return value


def _integral_steps(value_ms: float, dt_ms: float, field_name: str) -> int:
    ratio = value_ms / dt_ms
    nearest = round(ratio)
    if not math.isclose(ratio, nearest, rel_tol=0.0, abs_tol=1e-9):
        raise TrajectoryCharacterizationError(
            f"{field_name} must be an integral number of dt steps; ratio={ratio!r}."
        )
    return int(nearest)


def _sha256_json(value: Any) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


@dataclass(frozen=True, slots=True)
class LoomingTrajectoryScenario:
    """One explicit physical stimulus fixture and pre-collision time window."""

    identifier: str
    stimulus: LoomingStimulus
    sample_duration_ms: float
    fixture_policy_id: str = FIXTURE_POLICY_ID

    def __post_init__(self) -> None:
        _identifier(self.identifier, "identifier")
        _identifier(self.fixture_policy_id, "fixture_policy_id")
        if not isinstance(self.stimulus, LoomingStimulus):
            raise TrajectoryCharacterizationError("stimulus must be a LoomingStimulus.")
        duration = _finite(self.sample_duration_ms, "sample_duration_ms")
        if duration <= 0.0:
            raise TrajectoryCharacterizationError(
                "sample_duration_ms must be greater than zero."
            )
        collision_s = self.stimulus.time_to_collision_s
        if collision_s is not None and duration / 1000.0 > collision_s:
            raise TrajectoryCharacterizationError(
                "sample duration cannot extend past stimulus collision."
            )
        object.__setattr__(self, "sample_duration_ms", duration)

    def to_dict(self) -> dict[str, Any]:
        return {
            "identifier": self.identifier,
            "stimulus": self.stimulus.to_dict(),
            "sample_duration_ms": self.sample_duration_ms,
            "fixture_policy_id": self.fixture_policy_id,
            "provenance_classification": PROVENANCE_CLASSIFICATION,
        }


@dataclass(frozen=True, slots=True)
class TrajectoryBenchmarkPoint:
    """One explicit, non-calibrated end-to-end characterization point."""

    identifier: str
    trajectory: LoomingTrajectoryScenario
    pathway_condition: PathwayCondition
    encoder_config: LevelPEncoderConfig
    k_syn_mv_per_contact: float
    dt_ms: float

    def __post_init__(self) -> None:
        _identifier(self.identifier, "identifier")
        if not isinstance(self.trajectory, LoomingTrajectoryScenario):
            raise TrajectoryCharacterizationError(
                "trajectory must be a LoomingTrajectoryScenario."
            )
        if not isinstance(self.pathway_condition, PathwayCondition):
            raise TrajectoryCharacterizationError("unsupported pathway condition.")
        if not isinstance(self.encoder_config, LevelPEncoderConfig):
            raise TrajectoryCharacterizationError(
                "encoder_config must be a LevelPEncoderConfig."
            )
        k_syn = _finite(self.k_syn_mv_per_contact, "k_syn_mv_per_contact")
        dt_ms = _finite(self.dt_ms, "dt_ms")
        if k_syn <= 0.0:
            raise TrajectoryCharacterizationError(
                "k_syn_mv_per_contact must be greater than zero."
            )
        if dt_ms <= 0.0:
            raise TrajectoryCharacterizationError("dt_ms must be greater than zero.")
        _integral_steps(self.trajectory.sample_duration_ms, dt_ms, "sample_duration_ms")
        try:
            LIFConfig.published_prior(
                k_syn_mv_per_contact=k_syn,
                dt_ms=dt_ms,
                input_drive_provenance_id=PROVENANCE_CLASSIFICATION,
            )
        except SimulationConfigurationError as exc:
            raise TrajectoryCharacterizationError(str(exc)) from exc
        object.__setattr__(self, "k_syn_mv_per_contact", k_syn)
        object.__setattr__(self, "dt_ms", dt_ms)

    @property
    def steps(self) -> int:
        return _integral_steps(
            self.trajectory.sample_duration_ms, self.dt_ms, "sample_duration_ms"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "identifier": self.identifier,
            "trajectory": self.trajectory.to_dict(),
            "pathway_condition": self.pathway_condition.value,
            "encoder_config": self.encoder_config.to_dict(),
            "k_syn_mv_per_contact": self.k_syn_mv_per_contact,
            "dt_ms": self.dt_ms,
            "provenance_classification": PROVENANCE_CLASSIFICATION,
        }

    @property
    def sha256(self) -> str:
        return _sha256_json(self.to_dict())


def _point_sort_key(point: TrajectoryBenchmarkPoint) -> tuple[Any, ...]:
    stimulus = point.trajectory.stimulus
    return (
        point.trajectory.identifier,
        point.pathway_condition.value,
        point.dt_ms,
        point.encoder_config.lc4_gain_mv_eq,
        point.encoder_config.lplc2_gain_mv_eq,
        point.encoder_config.omega_half_rad_per_s,
        point.encoder_config.theta_half_rad,
        point.k_syn_mv_per_contact,
        stimulus.object_radius_m,
        stimulus.initial_distance_m,
        stimulus.approach_velocity_m_s,
        point.identifier,
    )


@dataclass(frozen=True, slots=True)
class TrajectoryBenchmarkSuite:
    """A non-empty, deterministically ordered bounded point collection."""

    points: tuple[TrajectoryBenchmarkPoint, ...]

    def __post_init__(self) -> None:
        try:
            points = tuple(self.points)
        except TypeError:
            raise TrajectoryCharacterizationError("points must be iterable.") from None
        if not points:
            raise TrajectoryCharacterizationError("benchmark suite cannot be empty.")
        if any(not isinstance(point, TrajectoryBenchmarkPoint) for point in points):
            raise TrajectoryCharacterizationError(
                "suite entries must be TrajectoryBenchmarkPoint values."
            )
        identifiers = [point.identifier for point in points]
        if len(identifiers) != len(set(identifiers)):
            raise TrajectoryCharacterizationError(
                "benchmark point identifiers must be unique."
            )
        object.__setattr__(self, "points", tuple(sorted(points, key=_point_sort_key)))


@dataclass(frozen=True, slots=True)
class StimulusPointSummary:
    """Geometry at one selected sample time."""

    time_ms: float
    theta_rad: float
    angular_expansion_velocity_rad_per_s: float

    def to_dict(self) -> dict[str, float]:
        return {
            "time_ms": self.time_ms,
            "theta_rad": self.theta_rad,
            "angular_expansion_velocity_rad_per_s": (
                self.angular_expansion_velocity_rad_per_s
            ),
        }


@dataclass(frozen=True, slots=True)
class StimulusTrajectorySummary:
    """Model/environment geometry; none of these fields is neural activity."""

    object_radius_m: float
    initial_distance_m: float
    approach_velocity_m_s: float
    collision_time_s: float | None
    sample_duration_ms: float
    sample_count: int
    final_sample_time_ms: float
    selected_points: tuple[StimulusPointSummary, ...]
    peak_theta_rad: float
    peak_theta_time_ms: float
    peak_absolute_expansion_velocity_rad_per_s: float
    peak_absolute_expansion_velocity_time_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_radius_m": self.object_radius_m,
            "initial_distance_m": self.initial_distance_m,
            "approach_velocity_m_s": self.approach_velocity_m_s,
            "collision_time_s": self.collision_time_s,
            "sample_duration_ms": self.sample_duration_ms,
            "sample_count": self.sample_count,
            "final_sample_time_ms": self.final_sample_time_ms,
            "selected_points": [point.to_dict() for point in self.selected_points],
            "peak_theta_rad": self.peak_theta_rad,
            "peak_theta_time_ms": self.peak_theta_time_ms,
            "peak_absolute_expansion_velocity_rad_per_s": (
                self.peak_absolute_expansion_velocity_rad_per_s
            ),
            "peak_absolute_expansion_velocity_time_ms": (
                self.peak_absolute_expansion_velocity_time_ms
            ),
        }


@dataclass(frozen=True, slots=True)
class EncoderChannelSummary:
    """One E1 feature/drive trace and compact bounded-normalization summary."""

    neuron_type: str
    normalized_feature: tuple[float, ...]
    external_drive_mv_eq: tuple[float, ...]
    first_nonzero_drive_time_ms: float | None
    peak_normalized_feature: float
    normalization_headroom: float
    peak_drive_mv_eq: float
    peak_drive_time_ms: float
    nonzero_interval_fraction: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "neuron_type": self.neuron_type,
            "normalized_feature": list(self.normalized_feature),
            "external_drive_mv_eq": list(self.external_drive_mv_eq),
            "first_nonzero_drive_time_ms": self.first_nonzero_drive_time_ms,
            "peak_normalized_feature": self.peak_normalized_feature,
            "normalization_headroom": self.normalization_headroom,
            "peak_drive_mv_eq": self.peak_drive_mv_eq,
            "peak_drive_time_ms": self.peak_drive_time_ms,
            "nonzero_interval_fraction": self.nonzero_interval_fraction,
        }


@dataclass(frozen=True, slots=True)
class VisualPopulationSummary:
    """Compact visual-neuron threshold/spike observables by biological type."""

    neuron_type: str
    body_count: int
    bodies_that_spike: int
    total_spike_count: int
    first_population_spike_time_ms: float | None
    last_body_first_spike_time_ms: float | None
    median_body_first_spike_time_ms: float | None
    distinct_first_spike_times_ms: tuple[float, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "neuron_type": self.neuron_type,
            "body_count": self.body_count,
            "bodies_that_spike": self.bodies_that_spike,
            "total_spike_count": self.total_spike_count,
            "first_population_spike_time_ms": self.first_population_spike_time_ms,
            "last_body_first_spike_time_ms": self.last_body_first_spike_time_ms,
            "median_body_first_spike_time_ms": self.median_body_first_spike_time_ms,
            "distinct_first_spike_times_ms": list(self.distinct_first_spike_times_ms),
        }


@dataclass(frozen=True, slots=True)
class DNp01TrajectorySummary:
    """Per-body readout telemetry retaining real graph asymmetry."""

    body_id: int
    side: str | None
    incoming_active_edge_count: int
    incoming_structural_weight: int
    delivered_event_count: int
    delivered_model_increment_sum_mveq: float
    peak_filtered_synaptic_state_mveq: float
    peak_membrane_mv: float
    first_spike_time_ms: float | None
    total_spike_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "body_id": self.body_id,
            "side": self.side,
            "incoming_active_edge_count": self.incoming_active_edge_count,
            "incoming_structural_weight": self.incoming_structural_weight,
            "delivered_event_count": self.delivered_event_count,
            "delivered_model_increment_sum_mveq": (
                self.delivered_model_increment_sum_mveq
            ),
            "peak_filtered_synaptic_state_mveq": (
                self.peak_filtered_synaptic_state_mveq
            ),
            "peak_membrane_mv": self.peak_membrane_mv,
            "first_spike_time_ms": self.first_spike_time_ms,
            "total_spike_count": self.total_spike_count,
        }


@dataclass(frozen=True, slots=True)
class TemporalChainSummary:
    """Simulator-relative timing; it excludes unmodelled visual latency."""

    stimulus_start_time_ms: float
    lc4_first_nonzero_drive_time_ms: float | None
    lplc2_first_nonzero_drive_time_ms: float | None
    lc4_first_spike_time_ms: float | None
    lplc2_first_spike_time_ms: float | None
    first_delivered_event_time_ms: float | None
    dnp01_first_spike_times_ms: tuple[tuple[int, float | None], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "stimulus_start_time_ms": self.stimulus_start_time_ms,
            "lc4_first_nonzero_drive_time_ms": (self.lc4_first_nonzero_drive_time_ms),
            "lplc2_first_nonzero_drive_time_ms": (
                self.lplc2_first_nonzero_drive_time_ms
            ),
            "lc4_first_spike_time_ms": self.lc4_first_spike_time_ms,
            "lplc2_first_spike_time_ms": self.lplc2_first_spike_time_ms,
            "first_delivered_event_time_ms": self.first_delivered_event_time_ms,
            "dnp01_first_spike_times_ms": [
                {"body_id": body_id, "first_spike_time_ms": time_ms}
                for body_id, time_ms in self.dnp01_first_spike_times_ms
            ],
        }


@dataclass(frozen=True, slots=True)
class TrajectoryCharacterizationResult:
    """Compact deterministic Phase 2F result, separate from SimulationResult."""

    benchmark_point: TrajectoryBenchmarkPoint
    configuration_sha256: str
    encoding_sha256: str
    candidate_identifier: str
    candidate_version: int
    graph_scope_id: str
    simulation_model_id: str
    simulation_model_version: str
    stimulus: StimulusTrajectorySummary
    encoder_channels: tuple[EncoderChannelSummary, ...]
    visual_populations: tuple[VisualPopulationSummary, ...]
    dnp01_responses: tuple[DNp01TrajectorySummary, ...]
    temporal_chain: TemporalChainSummary
    operating_regime: OperatingRegime
    deterministic_replay_verified: bool
    result_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        payload = self.to_dict(include_result_sha256=False)
        object.__setattr__(self, "result_sha256", _sha256_json(payload))

    def to_dict(self, *, include_result_sha256: bool = True) -> dict[str, Any]:
        result = {
            "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
            "benchmark_point": self.benchmark_point.to_dict(),
            "configuration_sha256": self.configuration_sha256,
            "encoding_sha256": self.encoding_sha256,
            "candidate_identifier": self.candidate_identifier,
            "candidate_version": self.candidate_version,
            "graph_scope_id": self.graph_scope_id,
            "simulation_model_id": self.simulation_model_id,
            "simulation_model_version": self.simulation_model_version,
            "stimulus": self.stimulus.to_dict(),
            "encoder_channels": [
                channel.to_dict() for channel in self.encoder_channels
            ],
            "visual_populations": [
                population.to_dict() for population in self.visual_populations
            ],
            "dnp01_responses": [
                response.to_dict() for response in self.dnp01_responses
            ],
            "temporal_chain": self.temporal_chain.to_dict(),
            "operating_regime": self.operating_regime.value,
            "deterministic_replay_verified": self.deterministic_replay_verified,
            "provenance_classification": PROVENANCE_CLASSIFICATION,
        }
        if include_result_sha256:
            result["result_sha256"] = self.result_sha256
        return result


@dataclass(frozen=True, slots=True)
class TrajectoryBenchmarkSuiteResult:
    """Deterministically ordered in-memory characterization product."""

    runs: tuple[TrajectoryCharacterizationResult, ...]
    by_identifier: MappingProxyType = field(init=False, repr=False)

    def __post_init__(self) -> None:
        runs = tuple(self.runs)
        if not runs:
            raise TrajectoryCharacterizationError("suite result cannot be empty.")
        identifiers = [run.benchmark_point.identifier for run in runs]
        if len(identifiers) != len(set(identifiers)):
            raise TrajectoryCharacterizationError(
                "suite result identifiers must be unique."
            )
        sorted_runs = tuple(
            sorted(runs, key=lambda run: _point_sort_key(run.benchmark_point))
        )
        if sorted_runs != runs:
            raise TrajectoryCharacterizationError(
                "suite results must use deterministic point order."
            )
        object.__setattr__(self, "runs", runs)
        object.__setattr__(
            self,
            "by_identifier",
            MappingProxyType(
                {run.benchmark_point.identifier: run for run in self.runs}
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
            "provenance_classification": PROVENANCE_CLASSIFICATION,
            "runs": [run.to_dict() for run in self.runs],
        }


def sample_looming_trajectory(
    scenario: LoomingTrajectoryScenario, *, dt_ms: float
) -> tuple[LoomingSample, ...]:
    """Sample a fixture on neural-step boundaries over ``[0, duration)``."""
    if not isinstance(scenario, LoomingTrajectoryScenario):
        raise TrajectoryCharacterizationError(
            "scenario must be a LoomingTrajectoryScenario."
        )
    dt_ms = _finite(dt_ms, "dt_ms")
    if dt_ms <= 0.0:
        raise TrajectoryCharacterizationError("dt_ms must be greater than zero.")
    steps = _integral_steps(scenario.sample_duration_ms, dt_ms, "sample_duration_ms")
    if steps <= 0:
        raise TrajectoryCharacterizationError(
            "sample duration must contain at least one simulation interval."
        )
    samples = tuple(
        scenario.stimulus.sample(step * dt_ms / 1000.0) for step in range(steps)
    )
    if any(sample.collided for sample in samples):
        raise TrajectoryCharacterizationError(
            "trajectory sampling produced a terminal collision sample."
        )
    return samples


def apply_pathway_condition(
    encoding: LevelPEncodingResult,
    graph: SimulationGraph,
    condition: PathwayCondition,
) -> ExternalDriveSchedule:
    """Mask E1 populations without changing the biological simulation graph."""
    if not isinstance(encoding, LevelPEncodingResult):
        raise TrajectoryCharacterizationError(
            "encoding must be a LevelPEncodingResult."
        )
    if not isinstance(graph, SimulationGraph):
        raise TrajectoryCharacterizationError("graph must be a SimulationGraph.")
    graph.validate_phase2b_scope()
    if not isinstance(condition, PathwayCondition):
        raise TrajectoryCharacterizationError("unsupported pathway condition.")
    source = dict(encoding.schedule.by_body_id)
    if set(source) != {
        node.body_id for node in graph.nodes if node.type in {"LC4", "LPLC2"}
    }:
        raise TrajectoryCharacterizationError(
            "encoded schedule does not target the complete visual population."
        )
    active_types = {
        PathwayCondition.ZERO: frozenset(),
        PathwayCondition.LC4_ONLY: frozenset({"LC4"}),
        PathwayCondition.LPLC2_ONLY: frozenset({"LPLC2"}),
        PathwayCondition.COMBINED: frozenset({"LC4", "LPLC2"}),
    }[condition]
    zeros = (0.0,) * encoding.schedule.steps
    by_body_id = {
        node.body_id: source[node.body_id] if node.type in active_types else zeros
        for node in graph.nodes
        if node.type in {"LC4", "LPLC2"}
    }
    return ExternalDriveSchedule.from_body_ids(
        by_body_id,
        steps=encoding.schedule.steps,
        provenance_id=(f"{encoding.schedule.provenance_id}:pathway={condition.value}"),
    )


def _results_equal(first: SimulationResult, second: SimulationResult) -> bool:
    arrays_equal = all(
        np.array_equal(getattr(first, field_name), getattr(second, field_name))
        for field_name in (
            "times_ms",
            "membrane_mv",
            "synaptic_mveq",
            "external_drive_mveq",
            "incoming_coupling_mveq",
        )
    )
    return (
        arrays_equal
        and first.body_ids == second.body_ids
        and first.neuron_types == second.neuron_types
        and first.neuron_sides == second.neuron_sides
        and first.spikes == second.spikes
        and first.delivered_events == second.delivered_events
        and dict(first.first_spike_time_ms_by_body_id)
        == dict(second.first_spike_time_ms_by_body_id)
        and dict(first.metadata) == dict(second.metadata)
    )


def _stimulus_summary(
    scenario: LoomingTrajectoryScenario,
    samples: tuple[LoomingSample, ...],
) -> StimulusTrajectorySummary:
    times_ms = tuple(sample.time_s * 1000.0 for sample in samples)
    theta = tuple(sample.angular_size_rad for sample in samples)
    omega = tuple(float(sample.angular_expansion_velocity_rad_s) for sample in samples)
    indices = tuple(dict.fromkeys((0, len(samples) // 2, len(samples) - 1)))
    selected = tuple(
        StimulusPointSummary(times_ms[index], theta[index], omega[index])
        for index in indices
    )
    peak_theta_index = max(range(len(theta)), key=theta.__getitem__)
    peak_omega_index = max(range(len(omega)), key=lambda index: abs(omega[index]))
    stimulus = scenario.stimulus
    return StimulusTrajectorySummary(
        object_radius_m=stimulus.object_radius_m,
        initial_distance_m=stimulus.initial_distance_m,
        approach_velocity_m_s=stimulus.approach_velocity_m_s,
        collision_time_s=stimulus.time_to_collision_s,
        sample_duration_ms=scenario.sample_duration_ms,
        sample_count=len(samples),
        final_sample_time_ms=times_ms[-1],
        selected_points=selected,
        peak_theta_rad=theta[peak_theta_index],
        peak_theta_time_ms=times_ms[peak_theta_index],
        peak_absolute_expansion_velocity_rad_per_s=abs(omega[peak_omega_index]),
        peak_absolute_expansion_velocity_time_ms=times_ms[peak_omega_index],
    )


def _channel_summary(
    neuron_type: str,
    normalized: tuple[float, ...],
    drive: tuple[float, ...],
    sample_times_s: tuple[float, ...],
) -> EncoderChannelSummary:
    peak_index = max(range(len(drive)), key=drive.__getitem__)
    nonzero = [index for index, value in enumerate(drive) if value > 0.0]
    peak_normalized = max(normalized)
    return EncoderChannelSummary(
        neuron_type=neuron_type,
        normalized_feature=normalized,
        external_drive_mv_eq=drive,
        first_nonzero_drive_time_ms=(
            sample_times_s[nonzero[0]] * 1000.0 if nonzero else None
        ),
        peak_normalized_feature=peak_normalized,
        normalization_headroom=1.0 - peak_normalized,
        peak_drive_mv_eq=drive[peak_index],
        peak_drive_time_ms=sample_times_s[peak_index] * 1000.0,
        nonzero_interval_fraction=len(nonzero) / len(drive),
    )


def _visual_summary(
    graph: SimulationGraph, result: SimulationResult, neuron_type: str
) -> VisualPopulationSummary:
    body_ids = tuple(node.body_id for node in graph.nodes if node.type == neuron_type)
    spike_count_by_body = Counter(
        spike.body_id for spike in result.spikes if spike.neuron_type == neuron_type
    )
    first_times = tuple(
        float(result.first_spike_time_ms_by_body_id[body_id])
        for body_id in body_ids
        if result.first_spike_time_ms_by_body_id[body_id] is not None
    )
    return VisualPopulationSummary(
        neuron_type=neuron_type,
        body_count=len(body_ids),
        bodies_that_spike=len(first_times),
        total_spike_count=sum(spike_count_by_body.values()),
        first_population_spike_time_ms=min(first_times) if first_times else None,
        last_body_first_spike_time_ms=max(first_times) if first_times else None,
        median_body_first_spike_time_ms=(
            float(statistics.median(first_times)) if first_times else None
        ),
        distinct_first_spike_times_ms=tuple(sorted(set(first_times))),
    )


def _dnp01_summaries(
    graph: SimulationGraph, result: SimulationResult
) -> tuple[DNp01TrajectorySummary, ...]:
    responses = []
    for node in graph.nodes:
        if node.type != READOUT_TYPE:
            continue
        body_id = node.body_id
        index = result.body_ids.index(body_id)
        incoming_edges = tuple(
            edge for edge in graph.edges if edge.target_body_id == body_id
        )
        delivered = tuple(
            event
            for event in result.delivered_events
            if event.target_body_id == body_id
        )
        responses.append(
            DNp01TrajectorySummary(
                body_id=body_id,
                side=node.soma_side,
                incoming_active_edge_count=len(incoming_edges),
                incoming_structural_weight=sum(
                    edge.structural_weight for edge in incoming_edges
                ),
                delivered_event_count=len(delivered),
                delivered_model_increment_sum_mveq=sum(
                    event.event_increment_mV_eq for event in delivered
                ),
                peak_filtered_synaptic_state_mveq=float(
                    np.max(result.synaptic_mveq[:, index])
                ),
                peak_membrane_mv=float(np.max(result.membrane_mv[:, index])),
                first_spike_time_ms=result.first_spike_time_ms_by_body_id[body_id],
                total_spike_count=sum(
                    spike.body_id == body_id for spike in result.spikes
                ),
            )
        )
    return tuple(responses)


def classify_operating_regime(
    visual_populations: tuple[VisualPopulationSummary, ...],
    dnp01_responses: tuple[DNp01TrajectorySummary, ...],
) -> OperatingRegime:
    """Classify threshold behavior using explicit Phase 2F terminology."""
    if sum(population.total_spike_count for population in visual_populations) == 0:
        return OperatingRegime.R0
    if any(response.total_spike_count > 1 for response in dnp01_responses):
        return OperatingRegime.R4
    spiking_dnp01 = sum(response.total_spike_count > 0 for response in dnp01_responses)
    if spiking_dnp01 == 0:
        return OperatingRegime.R1
    if spiking_dnp01 == 1:
        return OperatingRegime.R2
    return OperatingRegime.R3


def _configuration_sha256(
    graph: SimulationGraph,
    point: TrajectoryBenchmarkPoint,
    lif_config: LIFConfig,
) -> str:
    return _sha256_json(
        {
            "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
            "point": point.to_dict(),
            "simulation_config": lif_config.to_dict(),
            "candidate_identifier": graph.candidate_identifier,
            "candidate_version": graph.candidate_version,
            "graph_scope_id": graph.graph_scope_id,
            "circuit_integrity": dict(graph.circuit_integrity),
            "body_ids": list(graph.body_ids),
        }
    )


def run_trajectory_characterization(
    graph: SimulationGraph, point: TrajectoryBenchmarkPoint
) -> TrajectoryCharacterizationResult:
    """Run and exactly replay one production-path trajectory benchmark."""
    if not isinstance(graph, SimulationGraph):
        raise TrajectoryCharacterizationError("graph must be a SimulationGraph.")
    graph.validate_phase2b_scope()
    if not isinstance(point, TrajectoryBenchmarkPoint):
        raise TrajectoryCharacterizationError(
            "point must be a TrajectoryBenchmarkPoint."
        )
    samples = sample_looming_trajectory(point.trajectory, dt_ms=point.dt_ms)
    encoding = encode_level_p(
        samples=samples,
        graph=graph,
        config=point.encoder_config,
        dt_ms=point.dt_ms,
        stimulus_identity=point.trajectory.identifier,
    )
    schedule = apply_pathway_condition(encoding, graph, point.pathway_condition)
    lif_config = LIFConfig.published_prior(
        k_syn_mv_per_contact=point.k_syn_mv_per_contact,
        dt_ms=point.dt_ms,
        input_drive_provenance_id=schedule.provenance_id,
    )
    simulator = LIFSimulator(graph, lif_config)
    result = simulator.run(schedule)
    replay = simulator.run(schedule)
    if not _results_equal(result, replay):
        raise TrajectoryCharacterizationError(
            f"deterministic replay failed for {point.identifier!r}."
        )
    if any(
        node.type == READOUT_TYPE
        and np.any(
            result.external_drive_mveq[:, graph.node_index_by_body_id[node.body_id]]
            != 0.0
        )
        for node in graph.nodes
    ):
        raise TrajectoryCharacterizationError("DNp01 received prohibited drive.")

    applied_by_body_id = dict(schedule.by_body_id)
    first_lc4_body_id = next(node.body_id for node in graph.nodes if node.type == "LC4")
    first_lplc2_body_id = next(
        node.body_id for node in graph.nodes if node.type == "LPLC2"
    )
    encoder_channels = (
        _channel_summary(
            "LC4",
            encoding.lc4_normalized,
            applied_by_body_id[first_lc4_body_id],
            encoding.sample_times_s,
        ),
        _channel_summary(
            "LPLC2",
            encoding.lplc2_normalized,
            applied_by_body_id[first_lplc2_body_id],
            encoding.sample_times_s,
        ),
    )
    visual_populations = (
        _visual_summary(graph, result, "LC4"),
        _visual_summary(graph, result, "LPLC2"),
    )
    dnp01_responses = _dnp01_summaries(graph, result)
    first_delivery = (
        min(event.delivery_time_ms for event in result.delivered_events)
        if result.delivered_events
        else None
    )
    temporal_chain = TemporalChainSummary(
        stimulus_start_time_ms=0.0,
        lc4_first_nonzero_drive_time_ms=encoder_channels[0].first_nonzero_drive_time_ms,
        lplc2_first_nonzero_drive_time_ms=(
            encoder_channels[1].first_nonzero_drive_time_ms
        ),
        lc4_first_spike_time_ms=visual_populations[0].first_population_spike_time_ms,
        lplc2_first_spike_time_ms=(
            visual_populations[1].first_population_spike_time_ms
        ),
        first_delivered_event_time_ms=first_delivery,
        dnp01_first_spike_times_ms=tuple(
            (response.body_id, response.first_spike_time_ms)
            for response in dnp01_responses
        ),
    )
    return TrajectoryCharacterizationResult(
        benchmark_point=point,
        configuration_sha256=_configuration_sha256(graph, point, lif_config),
        encoding_sha256=encoding.encoding_sha256,
        candidate_identifier=graph.candidate_identifier,
        candidate_version=graph.candidate_version,
        graph_scope_id=graph.graph_scope_id,
        simulation_model_id=lif_config.model_id,
        simulation_model_version=lif_config.model_version,
        stimulus=_stimulus_summary(point.trajectory, samples),
        encoder_channels=encoder_channels,
        visual_populations=visual_populations,
        dnp01_responses=dnp01_responses,
        temporal_chain=temporal_chain,
        operating_regime=classify_operating_regime(visual_populations, dnp01_responses),
        deterministic_replay_verified=True,
    )


def run_trajectory_suite(
    graph: SimulationGraph, suite: TrajectoryBenchmarkSuite
) -> TrajectoryBenchmarkSuiteResult:
    """Run a bounded Phase 2F suite in deterministic order."""
    if not isinstance(suite, TrajectoryBenchmarkSuite):
        raise TrajectoryCharacterizationError(
            "suite must be a TrajectoryBenchmarkSuite."
        )
    graph.validate_phase2b_scope()
    return TrajectoryBenchmarkSuiteResult(
        tuple(run_trajectory_characterization(graph, point) for point in suite.points)
    )


__all__ = [
    "BENCHMARK_SCHEMA_VERSION",
    "FIXTURE_POLICY_ID",
    "PROVENANCE_CLASSIFICATION",
    "DNp01TrajectorySummary",
    "EncoderChannelSummary",
    "LoomingTrajectoryScenario",
    "OperatingRegime",
    "PathwayCondition",
    "StimulusPointSummary",
    "StimulusTrajectorySummary",
    "TemporalChainSummary",
    "TrajectoryBenchmarkPoint",
    "TrajectoryBenchmarkSuite",
    "TrajectoryBenchmarkSuiteResult",
    "TrajectoryCharacterizationError",
    "TrajectoryCharacterizationResult",
    "VisualPopulationSummary",
    "apply_pathway_condition",
    "classify_operating_regime",
    "run_trajectory_characterization",
    "run_trajectory_suite",
    "sample_looming_trajectory",
]
