"""Deterministic Phase 2C sensitivity probes for the Phase 2B simulator.

This module constructs explicitly synthetic population-drive fixtures.  It
does not derive drive from a stimulus, perform biological calibration, or
change the validated Phase 2B graph and coupling semantics.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

import numpy as np

from neurofly.simulation import (
    READOUT_TYPE,
    ExternalDriveSchedule,
    LIFConfig,
    LIFSimulator,
    SimulationConfigurationError,
    SimulationGraph,
    SimulationResult,
)

BENCHMARK_SCHEMA_VERSION = "phase2c_sensitivity_v1"
SYNTHETIC_FIXTURE_ID = "synthetic_population_step_drive_v1"
PROVENANCE_CLASSIFICATION = "NEUROFLY_SYNTHETIC_BENCHMARK"


class SensitivityBenchmarkError(ValueError):
    """A Phase 2C fixture, sweep, or result violates its narrow contract."""


class SensitivityScenario(StrEnum):
    """Supported synthetic population-drive probes."""

    ZERO = "ZERO"
    LC4_ONLY = "LC4_ONLY"
    LPLC2_ONLY = "LPLC2_ONLY"
    COMBINED = "COMBINED"


def _finite(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise SensitivityBenchmarkError(f"{field_name} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise SensitivityBenchmarkError(f"{field_name} must be finite.") from None
    if not math.isfinite(result):
        raise SensitivityBenchmarkError(f"{field_name} must be finite.")
    return result


def _integral_steps(value_ms: float, dt_ms: float, field_name: str) -> int:
    ratio = value_ms / dt_ms
    nearest = round(ratio)
    if not math.isclose(ratio, nearest, rel_tol=0.0, abs_tol=1e-9):
        raise SensitivityBenchmarkError(
            f"{field_name} must be an integral number of dt steps; ratio={ratio!r}."
        )
    return int(nearest)


@dataclass(frozen=True, slots=True)
class SensitivityPoint:
    """One explicitly supplied synthetic parameter point.

    Drive amplitudes and ``k_syn_mv_per_contact`` are model-only values.  They
    are neither MaleCNS measurements nor calibrated biological parameters.
    """

    identifier: str
    scenario: SensitivityScenario
    k_syn_mv_per_contact: float
    lc4_drive_mveq: float
    lplc2_drive_mveq: float
    dt_ms: float = 0.1
    drive_onset_ms: float = 0.0
    drive_duration_ms: float = 1.0
    total_duration_ms: float = 10.0
    fixture_id: str = SYNTHETIC_FIXTURE_ID

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not self.identifier:
            raise SensitivityBenchmarkError("identifier must be a non-empty string.")
        if not isinstance(self.fixture_id, str) or not self.fixture_id:
            raise SensitivityBenchmarkError("fixture_id must be a non-empty string.")
        if not isinstance(self.scenario, SensitivityScenario):
            raise SensitivityBenchmarkError("unsupported sensitivity scenario.")

        numeric_names = (
            "k_syn_mv_per_contact",
            "lc4_drive_mveq",
            "lplc2_drive_mveq",
            "dt_ms",
            "drive_onset_ms",
            "drive_duration_ms",
            "total_duration_ms",
        )
        for name in numeric_names:
            object.__setattr__(self, name, _finite(getattr(self, name), name))

        if self.k_syn_mv_per_contact <= 0:
            raise SensitivityBenchmarkError(
                "k_syn_mv_per_contact must be greater than zero."
            )
        if self.lc4_drive_mveq < 0 or self.lplc2_drive_mveq < 0:
            raise SensitivityBenchmarkError(
                "synthetic drive amplitudes must be non-negative."
            )
        if self.dt_ms <= 0:
            raise SensitivityBenchmarkError("dt_ms must be greater than zero.")
        if self.drive_onset_ms < 0:
            raise SensitivityBenchmarkError("drive_onset_ms cannot be negative.")
        if self.drive_duration_ms <= 0:
            raise SensitivityBenchmarkError(
                "drive_duration_ms must be greater than zero."
            )
        if self.total_duration_ms <= 0:
            raise SensitivityBenchmarkError(
                "total_duration_ms must be greater than zero."
            )
        if self.drive_onset_ms + self.drive_duration_ms > self.total_duration_ms:
            raise SensitivityBenchmarkError(
                "drive interval must fit within total_duration_ms."
            )

        _integral_steps(self.drive_onset_ms, self.dt_ms, "drive_onset_ms")
        _integral_steps(self.drive_duration_ms, self.dt_ms, "drive_duration_ms")
        _integral_steps(self.total_duration_ms, self.dt_ms, "total_duration_ms")
        try:
            LIFConfig(
                k_syn_mv_per_contact=self.k_syn_mv_per_contact,
                dt_ms=self.dt_ms,
            )
        except SimulationConfigurationError as exc:
            raise SensitivityBenchmarkError(
                f"parameter point is incompatible with Phase 2B: {exc}"
            ) from exc

        if self.scenario is SensitivityScenario.ZERO:
            if self.lc4_drive_mveq != 0 or self.lplc2_drive_mveq != 0:
                raise SensitivityBenchmarkError("ZERO requires both drives to be zero.")
        elif self.scenario is SensitivityScenario.LC4_ONLY:
            if self.lc4_drive_mveq <= 0 or self.lplc2_drive_mveq != 0:
                raise SensitivityBenchmarkError(
                    "LC4_ONLY requires positive LC4 drive and zero LPLC2 drive."
                )
        elif self.scenario is SensitivityScenario.LPLC2_ONLY:
            if self.lplc2_drive_mveq <= 0 or self.lc4_drive_mveq != 0:
                raise SensitivityBenchmarkError(
                    "LPLC2_ONLY requires positive LPLC2 drive and zero LC4 drive."
                )
        elif self.scenario is SensitivityScenario.COMBINED and (
            self.lc4_drive_mveq <= 0 or self.lplc2_drive_mveq <= 0
        ):
            raise SensitivityBenchmarkError(
                "COMBINED requires positive LC4 and LPLC2 drives."
            )

    @property
    def steps(self) -> int:
        return _integral_steps(self.total_duration_ms, self.dt_ms, "total_duration_ms")

    @property
    def onset_step(self) -> int:
        return _integral_steps(self.drive_onset_ms, self.dt_ms, "drive_onset_ms")

    @property
    def duration_steps(self) -> int:
        return _integral_steps(self.drive_duration_ms, self.dt_ms, "drive_duration_ms")

    def to_dict(self) -> dict[str, Any]:
        return {
            "identifier": self.identifier,
            "scenario": self.scenario.value,
            "k_syn_mv_per_contact": self.k_syn_mv_per_contact,
            "lc4_drive_mveq": self.lc4_drive_mveq,
            "lplc2_drive_mveq": self.lplc2_drive_mveq,
            "dt_ms": self.dt_ms,
            "drive_onset_ms": self.drive_onset_ms,
            "drive_duration_ms": self.drive_duration_ms,
            "total_duration_ms": self.total_duration_ms,
            "fixture_id": self.fixture_id,
            "provenance_classification": PROVENANCE_CLASSIFICATION,
        }


@dataclass(frozen=True, slots=True)
class SensitivitySweep:
    """A validated, deterministically ordered bounded set of parameter points."""

    points: tuple[SensitivityPoint, ...]

    def __post_init__(self) -> None:
        try:
            points = tuple(self.points)
        except TypeError:
            raise SensitivityBenchmarkError("points must be iterable.") from None
        if not points:
            raise SensitivityBenchmarkError("parameter sweep cannot be empty.")
        if any(not isinstance(point, SensitivityPoint) for point in points):
            raise SensitivityBenchmarkError(
                "parameter sweep entries must be SensitivityPoint values."
            )
        identifiers = [point.identifier for point in points]
        if len(identifiers) != len(set(identifiers)):
            raise SensitivityBenchmarkError(
                "parameter-point identifiers must be unique."
            )
        object.__setattr__(self, "points", tuple(sorted(points, key=_point_sort_key)))


def _point_sort_key(point: SensitivityPoint) -> tuple[Any, ...]:
    return (
        point.scenario.value,
        point.dt_ms,
        point.k_syn_mv_per_contact,
        point.lc4_drive_mveq,
        point.lplc2_drive_mveq,
        point.drive_onset_ms,
        point.drive_duration_ms,
        point.total_duration_ms,
        point.identifier,
    )


@dataclass(frozen=True, slots=True)
class DNp01Response:
    """Per-body DNp01 model observables; responses are never averaged."""

    body_id: int
    side: str | None
    first_spike_time_ms: float | None
    spike_count: int
    peak_membrane_mv: float
    peak_synaptic_mveq: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "body_id": self.body_id,
            "side": self.side,
            "first_spike_time_ms": self.first_spike_time_ms,
            "spike_count": self.spike_count,
            "peak_membrane_mv": self.peak_membrane_mv,
            "peak_synaptic_mveq": self.peak_synaptic_mveq,
        }


@dataclass(frozen=True, slots=True)
class SensitivityRunSummary:
    """Compact model-observable summary for one synthetic benchmark run."""

    parameter_point: SensitivityPoint
    configuration_sha256: str
    candidate_identifier: str
    candidate_version: int
    graph_scope_id: str
    simulation_model_id: str
    simulation_model_version: str
    lc4_spike_count: int
    lplc2_spike_count: int
    lc4_first_spike_time_ms: float | None
    lplc2_first_spike_time_ms: float | None
    delivered_event_count: int
    delivered_model_increment_sum_mveq: float
    first_delivery_time_ms: float | None
    dnp01_responses: tuple[DNp01Response, ...]
    deterministic_replay_verified: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
            "parameter_point": self.parameter_point.to_dict(),
            "configuration_sha256": self.configuration_sha256,
            "candidate_identifier": self.candidate_identifier,
            "candidate_version": self.candidate_version,
            "graph_scope_id": self.graph_scope_id,
            "simulation_model_id": self.simulation_model_id,
            "simulation_model_version": self.simulation_model_version,
            "lc4_spike_count": self.lc4_spike_count,
            "lplc2_spike_count": self.lplc2_spike_count,
            "lc4_first_spike_time_ms": self.lc4_first_spike_time_ms,
            "lplc2_first_spike_time_ms": self.lplc2_first_spike_time_ms,
            "delivered_event_count": self.delivered_event_count,
            "delivered_model_increment_sum_mveq": (
                self.delivered_model_increment_sum_mveq
            ),
            "first_delivery_time_ms": self.first_delivery_time_ms,
            "dnp01_responses": [
                response.to_dict() for response in self.dnp01_responses
            ],
            "deterministic_replay_verified": self.deterministic_replay_verified,
            "provenance_classification": PROVENANCE_CLASSIFICATION,
        }


@dataclass(frozen=True, slots=True)
class SensitivitySweepResult:
    """Deterministically ordered in-memory Phase 2C benchmark product."""

    candidate_identifier: str
    candidate_version: int
    graph_scope_id: str
    simulation_model_id: str
    simulation_model_version: str
    runs: tuple[SensitivityRunSummary, ...]
    by_identifier: Mapping[str, SensitivityRunSummary] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        runs = tuple(self.runs)
        if any(not isinstance(run, SensitivityRunSummary) for run in runs):
            raise SensitivityBenchmarkError(
                "sweep result entries must be SensitivityRunSummary values."
            )
        identifiers = [run.parameter_point.identifier for run in runs]
        if not runs or len(identifiers) != len(set(identifiers)):
            raise SensitivityBenchmarkError(
                "sweep result requires unique, non-empty parameter points."
            )
        if (
            tuple(sorted(runs, key=lambda run: _point_sort_key(run.parameter_point)))
            != runs
        ):
            raise SensitivityBenchmarkError(
                "sweep result runs must use deterministic parameter order."
            )
        if any(
            run.candidate_identifier != self.candidate_identifier
            or run.candidate_version != self.candidate_version
            or run.graph_scope_id != self.graph_scope_id
            or run.simulation_model_id != self.simulation_model_id
            or run.simulation_model_version != self.simulation_model_version
            for run in runs
        ):
            raise SensitivityBenchmarkError("sweep result metadata is inconsistent.")
        object.__setattr__(self, "runs", runs)
        object.__setattr__(
            self,
            "by_identifier",
            MappingProxyType({run.parameter_point.identifier: run for run in runs}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
            "candidate_identifier": self.candidate_identifier,
            "candidate_version": self.candidate_version,
            "graph_scope_id": self.graph_scope_id,
            "simulation_model_id": self.simulation_model_id,
            "simulation_model_version": self.simulation_model_version,
            "deterministic_policy": "deterministic_replay_required",
            "provenance_classification": PROVENANCE_CLASSIFICATION,
            "runs": [run.to_dict() for run in self.runs],
        }


def build_synthetic_drive_schedule(
    graph: SimulationGraph, point: SensitivityPoint
) -> ExternalDriveSchedule:
    """Broadcast one synthetic step fixture without deriving sensory input."""
    _validate_graph(graph)
    if not isinstance(point, SensitivityPoint):
        raise SensitivityBenchmarkError("point must be a SensitivityPoint.")
    provenance_id = f"{point.fixture_id}:{point.identifier}"
    if point.scenario is SensitivityScenario.ZERO:
        return ExternalDriveSchedule.zeros(point.steps, provenance_id=provenance_id)

    onset = point.onset_step
    stop = onset + point.duration_steps
    values_by_type = {
        "LC4": point.lc4_drive_mveq,
        "LPLC2": point.lplc2_drive_mveq,
    }
    values_by_body_id: dict[int, tuple[float, ...]] = {}
    for node in graph.nodes:
        amplitude = values_by_type.get(node.type or "", 0.0)
        if amplitude == 0.0:
            continue
        values_by_body_id[node.body_id] = tuple(
            amplitude if onset <= step < stop else 0.0 for step in range(point.steps)
        )
    return ExternalDriveSchedule.from_body_ids(
        values_by_body_id,
        steps=point.steps,
        provenance_id=provenance_id,
    )


def run_sensitivity_point(
    graph: SimulationGraph, point: SensitivityPoint
) -> SensitivityRunSummary:
    """Run and exactly replay one synthetic parameter point."""
    _validate_graph(graph)
    schedule = build_synthetic_drive_schedule(graph, point)
    config = LIFConfig(
        k_syn_mv_per_contact=point.k_syn_mv_per_contact,
        dt_ms=point.dt_ms,
        input_drive_provenance_id=point.fixture_id,
    )
    dnp01_body_ids = tuple(
        node.body_id for node in graph.nodes if node.type == READOUT_TYPE
    )
    simulator = LIFSimulator(graph, config)
    first = simulator.run(schedule, record_body_ids=dnp01_body_ids)
    replay = simulator.run(schedule, record_body_ids=dnp01_body_ids)
    _validate_result_dimensions(first, point, dnp01_body_ids)
    _validate_result_dimensions(replay, point, dnp01_body_ids)
    if not _results_are_exactly_equal(first, replay):
        raise SensitivityBenchmarkError(
            f"deterministic replay failed for {point.identifier!r}."
        )
    return _summarize(graph, point, config, first)


def run_sensitivity_sweep(
    graph: SimulationGraph, sweep: SensitivitySweep
) -> SensitivitySweepResult:
    """Run a bounded parameter sweep in deterministic point order."""
    _validate_graph(graph)
    if not isinstance(sweep, SensitivitySweep):
        raise SensitivityBenchmarkError("sweep must be a SensitivitySweep.")
    runs = tuple(run_sensitivity_point(graph, point) for point in sweep.points)
    first = runs[0]
    return SensitivitySweepResult(
        candidate_identifier=graph.candidate_identifier,
        candidate_version=graph.candidate_version,
        graph_scope_id=graph.graph_scope_id,
        simulation_model_id=first.simulation_model_id,
        simulation_model_version=first.simulation_model_version,
        runs=runs,
    )


def _validate_graph(graph: SimulationGraph) -> None:
    if not isinstance(graph, SimulationGraph):
        raise SensitivityBenchmarkError("graph must be a SimulationGraph.")
    graph.validate_phase2b_scope()


def _validate_result_dimensions(
    result: SimulationResult,
    point: SensitivityPoint,
    dnp01_body_ids: tuple[int, ...],
) -> None:
    expected_state_shape = (point.steps + 1, len(dnp01_body_ids))
    expected_interval_shape = (point.steps, len(dnp01_body_ids))
    if result.body_ids != dnp01_body_ids:
        raise SensitivityBenchmarkError("result DNp01 body ordering is inconsistent.")
    if result.membrane_mv.shape != expected_state_shape:
        raise SensitivityBenchmarkError("result membrane dimensions are inconsistent.")
    if result.synaptic_mveq.shape != expected_state_shape:
        raise SensitivityBenchmarkError("result synaptic dimensions are inconsistent.")
    if result.external_drive_mveq.shape != expected_interval_shape:
        raise SensitivityBenchmarkError(
            "result external-drive dimensions are inconsistent."
        )
    if result.incoming_coupling_mveq.shape != expected_interval_shape:
        raise SensitivityBenchmarkError(
            "result incoming-coupling dimensions are inconsistent."
        )
    if np.any(result.external_drive_mveq != 0.0):
        raise SensitivityBenchmarkError("DNp01 received prohibited direct drive.")


def _results_are_exactly_equal(
    first: SimulationResult, second: SimulationResult
) -> bool:
    arrays_equal = all(
        np.array_equal(getattr(first, name), getattr(second, name))
        for name in (
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


def _first_spike_time(result: SimulationResult, neuron_type: str) -> float | None:
    times = [
        event.time_ms for event in result.spikes if event.neuron_type == neuron_type
    ]
    return min(times) if times else None


def _configuration_sha256(
    graph: SimulationGraph, point: SensitivityPoint, config: LIFConfig
) -> str:
    payload = {
        "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
        "candidate_identifier": graph.candidate_identifier,
        "candidate_version": graph.candidate_version,
        "graph_scope_id": graph.graph_scope_id,
        "circuit_integrity": dict(graph.circuit_integrity),
        "point": point.to_dict(),
        "simulation_config": config.to_dict(),
    }
    serialized = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _summarize(
    graph: SimulationGraph,
    point: SensitivityPoint,
    config: LIFConfig,
    result: SimulationResult,
) -> SensitivityRunSummary:
    spike_counts = Counter(event.neuron_type for event in result.spikes)
    dnp01_responses = []
    for body_id, side in zip(result.body_ids, result.neuron_sides):
        index = result.body_ids.index(body_id)
        dnp01_responses.append(
            DNp01Response(
                body_id=body_id,
                side=side,
                first_spike_time_ms=result.first_spike_time_ms_by_body_id[body_id],
                spike_count=sum(event.body_id == body_id for event in result.spikes),
                peak_membrane_mv=float(np.max(result.membrane_mv[:, index])),
                peak_synaptic_mveq=float(np.max(result.synaptic_mveq[:, index])),
            )
        )
    first_delivery = (
        min(event.delivery_time_ms for event in result.delivered_events)
        if result.delivered_events
        else None
    )
    return SensitivityRunSummary(
        parameter_point=point,
        configuration_sha256=_configuration_sha256(graph, point, config),
        candidate_identifier=graph.candidate_identifier,
        candidate_version=graph.candidate_version,
        graph_scope_id=graph.graph_scope_id,
        simulation_model_id=config.model_id,
        simulation_model_version=config.model_version,
        lc4_spike_count=spike_counts["LC4"],
        lplc2_spike_count=spike_counts["LPLC2"],
        lc4_first_spike_time_ms=_first_spike_time(result, "LC4"),
        lplc2_first_spike_time_ms=_first_spike_time(result, "LPLC2"),
        delivered_event_count=len(result.delivered_events),
        delivered_model_increment_sum_mveq=sum(
            event.event_increment_mV_eq for event in result.delivered_events
        ),
        first_delivery_time_ms=first_delivery,
        dnp01_responses=tuple(dnp01_responses),
        deterministic_replay_verified=True,
    )


__all__ = [
    "BENCHMARK_SCHEMA_VERSION",
    "DNp01Response",
    "PROVENANCE_CLASSIFICATION",
    "SYNTHETIC_FIXTURE_ID",
    "SensitivityBenchmarkError",
    "SensitivityPoint",
    "SensitivityRunSummary",
    "SensitivityScenario",
    "SensitivitySweep",
    "SensitivitySweepResult",
    "build_synthetic_drive_schedule",
    "run_sensitivity_point",
    "run_sensitivity_sweep",
]
