"""Deterministic Phase 2B leaky integrate-and-fire simulation core.

This module is deliberately a narrow execution boundary for the validated
NeuroFly candidate.  It consumes an already prepared external drive and never
derives sensory input from stimuli, columns, or connectome annotations.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

import numpy as np

from neurofly.malecns.models import (
    CANDIDATE,
    MALECNS_DATASET,
    NEUPRINT_ENDPOINT,
    NeuronRecord,
)

MODEL_ID = "lif_filtered_synapse"
MODEL_VERSION = "phase2b_v1"
GRAPH_SCOPE_ID = "direct_visual_to_dnp01_v1"
PHASE7F_READOUT_SCOPE_ID = "phase7f_two_dnp01_readouts_v1"
SIGN_POLICY_ID = "direct_visual_dnp01_depolarizing_assumption_v1"
EXTERNAL_DRIVE_SEMANTICS = "voltage_equivalent_mV_eq_v1"
VISUAL_TYPES = ("LC4", "LPLC2")
READOUT_TYPE = "DNp01"
EXPECTED_NODE_COUNT = 313
EXPECTED_EDGE_COUNT = 311
EXPECTED_EDGE_COUNTS = {"LC4": 126, "LPLC2": 185}


class SimulationError(RuntimeError):
    """Base class for explicit Phase 2B validation and execution failures."""


class SimulationConfigurationError(SimulationError):
    """The LIF configuration violates the dimensional or timing contract."""


class SimulationGraphError(SimulationError):
    """The simulation view is not a valid Phase 2B graph."""


class SimulationInputError(SimulationError):
    """Caller-supplied input or initial state is malformed or unsafe."""


def _finite_float(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise SimulationConfigurationError(f"{field_name} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise SimulationConfigurationError(f"{field_name} must be finite.") from None
    if not math.isfinite(result):
        raise SimulationConfigurationError(f"{field_name} must be finite.")
    return result


def _positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise SimulationGraphError(f"{field_name} must be a positive integer.")
    return value


def _validate_step_ratio(value_ms: float, dt_ms: float, field_name: str) -> int:
    ratio = value_ms / dt_ms
    nearest = round(ratio)
    if not math.isclose(ratio, nearest, rel_tol=0.0, abs_tol=1e-9):
        raise SimulationConfigurationError(
            f"{field_name} must be an integral number of dt steps; ratio={ratio!r}."
        )
    return int(nearest)


@dataclass(frozen=True, slots=True)
class LIFConfig:
    """Explicit dimensional and provenance-bearing M1 configuration.

    The numerical defaults are published Drosophila modelling priors selected
    in Phase 2A.  ``k_syn_mv_per_contact`` is intentionally required: it is a
    NeuroFly calibration parameter and has no biological default.
    """

    k_syn_mv_per_contact: float
    model_id: str = MODEL_ID
    model_version: str = MODEL_VERSION
    graph_scope_id: str = GRAPH_SCOPE_ID
    sign_policy_id: str = SIGN_POLICY_ID
    external_drive_semantics: str = EXTERNAL_DRIVE_SEMANTICS
    input_drive_provenance_id: str = "caller_supplied_v1"
    baseline_policy: str = "zero"
    stochastic_policy: str = "deterministic"
    dt_ms: float = 0.1
    tau_m_ms: float = 20.0
    tau_s_ms: float = 5.0
    rest_mv: float = -52.0
    reset_mv: float = -52.0
    threshold_mv: float = -45.0
    refractory_ms: float = 2.2
    delay_ms: float = 1.8

    def __post_init__(self) -> None:
        for name in (
            "model_id",
            "model_version",
            "graph_scope_id",
            "sign_policy_id",
            "external_drive_semantics",
            "input_drive_provenance_id",
            "baseline_policy",
            "stochastic_policy",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise SimulationConfigurationError(
                    f"{name} must be a non-empty string."
                )

        numeric_names = (
            "k_syn_mv_per_contact",
            "dt_ms",
            "tau_m_ms",
            "tau_s_ms",
            "rest_mv",
            "reset_mv",
            "threshold_mv",
            "refractory_ms",
            "delay_ms",
        )
        numeric: dict[str, float] = {}
        for name in numeric_names:
            numeric[name] = _finite_float(getattr(self, name), name)
            object.__setattr__(self, name, numeric[name])

        if numeric["dt_ms"] <= 0:
            raise SimulationConfigurationError("dt_ms must be greater than zero.")
        if numeric["tau_m_ms"] <= 0:
            raise SimulationConfigurationError("tau_m_ms must be greater than zero.")
        if numeric["tau_s_ms"] <= 0:
            raise SimulationConfigurationError("tau_s_ms must be greater than zero.")
        if numeric["refractory_ms"] < 0:
            raise SimulationConfigurationError("refractory_ms cannot be negative.")
        if numeric["delay_ms"] < 0:
            raise SimulationConfigurationError("delay_ms cannot be negative.")
        if numeric["k_syn_mv_per_contact"] <= 0:
            raise SimulationConfigurationError(
                "k_syn_mv_per_contact must be greater than zero."
            )
        if numeric["threshold_mv"] <= numeric["reset_mv"]:
            raise SimulationConfigurationError(
                "threshold_mv must be greater than reset_mv."
            )
        if self.model_id != MODEL_ID:
            raise SimulationConfigurationError(
                f"Unsupported model_id {self.model_id!r}; expected {MODEL_ID!r}."
            )
        if self.graph_scope_id not in {GRAPH_SCOPE_ID, PHASE7F_READOUT_SCOPE_ID}:
            raise SimulationConfigurationError(
                f"Unsupported graph_scope_id {self.graph_scope_id!r}."
            )
        if self.sign_policy_id != SIGN_POLICY_ID:
            raise SimulationConfigurationError(
                f"Unsupported sign_policy_id {self.sign_policy_id!r}."
            )
        if self.external_drive_semantics != EXTERNAL_DRIVE_SEMANTICS:
            raise SimulationConfigurationError(
                f"Unsupported external_drive_semantics "
                f"{self.external_drive_semantics!r}."
            )
        if self.baseline_policy != "zero":
            raise SimulationConfigurationError(
                "Phase 2B only implements the explicit zero baseline policy."
            )
        if self.stochastic_policy != "deterministic":
            raise SimulationConfigurationError(
                "Phase 2B only implements deterministic stochastic_policy."
            )
        _validate_step_ratio(self.delay_ms, self.dt_ms, "delay_ms")
        _validate_step_ratio(self.refractory_ms, self.dt_ms, "refractory_ms")

    @classmethod
    def published_prior(
        cls, *, k_syn_mv_per_contact: float, **overrides: Any
    ) -> LIFConfig:
        """Construct the named Phase 2A prior set with an explicit ``k_syn``."""
        return cls(k_syn_mv_per_contact=k_syn_mv_per_contact, **overrides)

    @property
    def delay_steps(self) -> int:
        return _validate_step_ratio(self.delay_ms, self.dt_ms, "delay_ms")

    @property
    def refractory_steps(self) -> int:
        return _validate_step_ratio(self.refractory_ms, self.dt_ms, "refractory_ms")

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_version": self.model_version,
            "graph_scope_id": self.graph_scope_id,
            "sign_policy_id": self.sign_policy_id,
            "external_drive_semantics": self.external_drive_semantics,
            "input_drive_provenance_id": self.input_drive_provenance_id,
            "baseline_policy": self.baseline_policy,
            "stochastic_policy": self.stochastic_policy,
            "dt_ms": self.dt_ms,
            "tau_m_ms": self.tau_m_ms,
            "tau_s_ms": self.tau_s_ms,
            "rest_mv": self.rest_mv,
            "reset_mv": self.reset_mv,
            "threshold_mv": self.threshold_mv,
            "refractory_ms": self.refractory_ms,
            "delay_ms": self.delay_ms,
            "delay_steps": self.delay_steps,
            "refractory_steps": self.refractory_steps,
            "k_syn_mv_per_contact": self.k_syn_mv_per_contact,
        }


@dataclass(frozen=True, slots=True)
class SimulationEdge:
    """One active chemical edge with structural and model fields separated."""

    edge_index: int
    source_index: int
    target_index: int
    source_body_id: int
    target_body_id: int
    source_type: str
    target_type: str
    structural_weight: int
    model_sign: int = 1

    def __post_init__(self) -> None:
        for name in ("edge_index", "source_index", "target_index"):
            if (
                isinstance(getattr(self, name), bool)
                or not isinstance(getattr(self, name), int)
                or getattr(self, name) < 0
            ):
                raise SimulationGraphError(f"{name} must be a non-negative integer.")
        _positive_int(self.source_body_id, "source_body_id")
        _positive_int(self.target_body_id, "target_body_id")
        _positive_int(self.structural_weight, "structural_weight")
        if isinstance(self.model_sign, bool) or self.model_sign != 1:
            raise SimulationGraphError(
                "Phase 2B active visual edges require explicit model_sign=+1."
            )
        if self.source_type not in VISUAL_TYPES or self.target_type != READOUT_TYPE:
            raise SimulationGraphError(
                "Active Phase 2B edges must be LC4/LPLC2 -> DNp01."
            )

    def event_increment(self, k_syn_mv_per_contact: float) -> float:
        gain = _finite_float(k_syn_mv_per_contact, "k_syn_mv_per_contact")
        if gain <= 0:
            raise SimulationConfigurationError(
                "k_syn_mv_per_contact must be greater than zero."
            )
        increment = float(self.model_sign * gain * self.structural_weight)
        if not math.isfinite(increment):
            raise SimulationConfigurationError("model event increment must be finite.")
        return increment

    def to_dict(self, *, k_syn_mv_per_contact: float | None = None) -> dict[str, Any]:
        result = {
            "edge_index": self.edge_index,
            "source_index": self.source_index,
            "target_index": self.target_index,
            "source_body_id": self.source_body_id,
            "target_body_id": self.target_body_id,
            "source_type": self.source_type,
            "target_type": self.target_type,
            "structural_weight": self.structural_weight,
            "model_sign": self.model_sign,
        }
        if k_syn_mv_per_contact is not None:
            result["event_increment_mV_eq"] = self.event_increment(k_syn_mv_per_contact)
        return result


@dataclass(frozen=True, slots=True)
class SimulationGraph:
    """Immutable simulation view derived from, but separate from, a contract."""

    candidate_identifier: str
    candidate_version: int
    dataset: str
    graph_scope_id: str
    nodes: tuple[NeuronRecord, ...]
    edges: tuple[SimulationEdge, ...]
    circuit_integrity: tuple[tuple[str, str], ...] = ()
    node_index_by_body_id: Mapping[int, int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        nodes = tuple(self.nodes)
        edges = tuple(self.edges)
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "edges", edges)
        if (
            not isinstance(self.candidate_identifier, str)
            or not self.candidate_identifier
        ):
            raise SimulationGraphError("candidate_identifier must be non-empty.")
        if isinstance(self.candidate_version, bool) or not isinstance(
            self.candidate_version, int
        ):
            raise SimulationGraphError("candidate_version must be an integer.")
        if self.dataset != MALECNS_DATASET:
            raise SimulationGraphError(
                "Simulation graph dataset must be male-cns:v1.0."
            )
        if self.graph_scope_id not in {GRAPH_SCOPE_ID, PHASE7F_READOUT_SCOPE_ID}:
            raise SimulationGraphError("Simulation graph scope is unsupported.")
        for node in nodes:
            if (
                isinstance(node.body_id, bool)
                or not isinstance(node.body_id, int)
                or node.body_id <= 0
            ):
                raise SimulationGraphError(
                    "Simulation graph node body IDs must be positive integers."
                )
            if node.dataset != self.dataset:
                raise SimulationGraphError(
                    "Simulation graph node dataset does not match graph dataset."
                )
        body_ids = [node.body_id for node in nodes]
        if len(body_ids) != len(set(body_ids)):
            raise SimulationGraphError("Simulation graph contains duplicate body IDs.")
        object.__setattr__(
            self,
            "node_index_by_body_id",
            MappingProxyType(
                {body_id: index for index, body_id in enumerate(body_ids)}
            ),
        )
        edge_indices = [edge.edge_index for edge in edges]
        if edge_indices != list(range(len(edges))):
            raise SimulationGraphError(
                "Simulation edge indices must be contiguous and deterministic."
            )
        for edge in edges:
            if edge.source_index >= len(nodes) or edge.target_index >= len(nodes):
                raise SimulationGraphError(
                    "Simulation edge index is outside graph nodes."
                )
            source = nodes[edge.source_index]
            target = nodes[edge.target_index]
            if (
                edge.source_body_id != source.body_id
                or edge.target_body_id != target.body_id
            ):
                raise SimulationGraphError(
                    "Simulation edge body/index linkage mismatch."
                )
            if edge.source_type != source.type or edge.target_type != target.type:
                raise SimulationGraphError(
                    "Simulation edge type/index linkage mismatch."
                )
        object.__setattr__(self, "circuit_integrity", tuple(self.circuit_integrity))

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def body_ids(self) -> tuple[int, ...]:
        return tuple(node.body_id for node in self.nodes)

    @property
    def neuron_types(self) -> tuple[str | None, ...]:
        return tuple(node.type for node in self.nodes)

    @property
    def neuron_sides(self) -> tuple[str | None, ...]:
        return tuple(node.soma_side for node in self.nodes)

    def validate_phase2b_scope(self) -> None:
        if self.candidate_identifier != CANDIDATE.identifier:
            raise SimulationGraphError("Simulation graph candidate is unsupported.")
        if self.candidate_version != CANDIDATE.version:
            raise SimulationGraphError(
                "Simulation graph candidate version is unsupported."
            )
        if self.node_count != EXPECTED_NODE_COUNT:
            raise SimulationGraphError(
                f"Phase 2B graph requires {EXPECTED_NODE_COUNT} nodes; "
                f"got {self.node_count}."
            )
        counts = {neuron_type: 0 for neuron_type in (*VISUAL_TYPES, READOUT_TYPE)}
        for node in self.nodes:
            if node.type not in counts:
                raise SimulationGraphError(f"Unexpected node type {node.type!r}.")
            counts[node.type] += 1
        if counts != {"LC4": 126, "LPLC2": 185, "DNp01": 2}:
            raise SimulationGraphError(f"Unexpected Phase 2B node counts: {counts!r}.")
        if self.edge_count != EXPECTED_EDGE_COUNT:
            raise SimulationGraphError(
                f"Phase 2B graph requires {EXPECTED_EDGE_COUNT} edges; "
                f"got {self.edge_count}."
            )
        edge_counts = {neuron_type: 0 for neuron_type in VISUAL_TYPES}
        seen: set[tuple[int, int]] = set()
        for edge in self.edges:
            if edge.source_type not in edge_counts or edge.target_type != READOUT_TYPE:
                raise SimulationGraphError(
                    "Phase 2B graph contains an edge outside visual -> DNp01."
                )
            edge_counts[edge.source_type] += 1
            pair = (edge.source_body_id, edge.target_body_id)
            if pair in seen:
                raise SimulationGraphError("Phase 2B graph contains duplicate edges.")
            seen.add(pair)
        if edge_counts != EXPECTED_EDGE_COUNTS:
            raise SimulationGraphError(
                f"Unexpected Phase 2B edge counts: {edge_counts!r}."
            )

    def validate_phase7f_readout_scope(self) -> None:
        """Two pinned DNp01 LIF nodes, with no dormant sensory graph edges."""

        if (
            self.candidate_identifier != CANDIDATE.identifier
            or self.candidate_version != CANDIDATE.version
            or self.graph_scope_id != PHASE7F_READOUT_SCOPE_ID
            or self.node_count != 2
            or self.edge_count != 0
            or {(node.body_id, node.type, node.soma_side) for node in self.nodes}
            != {(10001, READOUT_TYPE, "R"), (10010, READOUT_TYPE, "L")}
        ):
            raise SimulationGraphError("Phase 7F readout graph identity mismatch.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_identifier": self.candidate_identifier,
            "candidate_version": self.candidate_version,
            "dataset": self.dataset,
            "graph_scope_id": self.graph_scope_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "circuit_integrity": dict(self.circuit_integrity),
            "edges": [edge.to_dict() for edge in self.edges],
        }


def build_phase2b_graph(circuit_contract: Any) -> SimulationGraph:
    """Build and strictly validate the 311-edge Phase 2B view."""
    if getattr(circuit_contract, "candidate", None) != CANDIDATE:
        raise SimulationGraphError("CircuitContract candidate does not match Phase 2B.")
    provenance = getattr(circuit_contract, "provenance", None)
    if provenance is None:
        raise SimulationGraphError("CircuitContract provenance is required.")
    if getattr(provenance, "dataset", None) != MALECNS_DATASET:
        raise SimulationGraphError("CircuitContract dataset is not male-cns:v1.0.")
    if getattr(provenance, "endpoint", None) != NEUPRINT_ENDPOINT:
        raise SimulationGraphError("CircuitContract endpoint is not official neuPrint.")
    nodes = tuple(circuit_contract.neurons)
    node_index_by_body_id = {node.body_id: index for index, node in enumerate(nodes)}
    if len(node_index_by_body_id) != len(nodes):
        raise SimulationGraphError("CircuitContract contains duplicate node body IDs.")
    contract_index = getattr(circuit_contract, "node_index_by_body_id", None)
    if contract_index is not None and dict(contract_index) != node_index_by_body_id:
        raise SimulationGraphError(
            "CircuitContract body-ID/node-index mapping is inconsistent."
        )

    active_edges: list[SimulationEdge] = []
    for edge in circuit_contract.connections:
        if edge.source_type not in VISUAL_TYPES or edge.target_type != READOUT_TYPE:
            continue
        if edge.dataset != MALECNS_DATASET:
            raise SimulationGraphError("Active edge dataset is not male-cns:v1.0.")
        source_index = node_index_by_body_id.get(edge.source_body_id)
        target_index = node_index_by_body_id.get(edge.target_body_id)
        if source_index is None or target_index is None:
            raise SimulationGraphError("Active edge endpoint is absent from contract.")
        source = nodes[source_index]
        target = nodes[target_index]
        if source.type != edge.source_type or target.type != edge.target_type:
            raise SimulationGraphError("Active edge type does not match contract node.")
        active_edges.append(
            SimulationEdge(
                edge_index=len(active_edges),
                source_index=source_index,
                target_index=target_index,
                source_body_id=edge.source_body_id,
                target_body_id=edge.target_body_id,
                source_type=edge.source_type,
                target_type=edge.target_type,
                structural_weight=edge.structural_weight,
                model_sign=1,
            )
        )
    active_edges.sort(key=lambda edge: (edge.source_index, edge.target_index))
    active_edges = [
        SimulationEdge(
            edge_index=index,
            source_index=edge.source_index,
            target_index=edge.target_index,
            source_body_id=edge.source_body_id,
            target_body_id=edge.target_body_id,
            source_type=edge.source_type,
            target_type=edge.target_type,
            structural_weight=edge.structural_weight,
            model_sign=edge.model_sign,
        )
        for index, edge in enumerate(active_edges)
    ]
    integrity = tuple(
        getattr(getattr(circuit_contract, "integrity", None), "sha256_by_file", ())
    )
    graph = SimulationGraph(
        candidate_identifier=circuit_contract.candidate.identifier,
        candidate_version=circuit_contract.candidate.version,
        dataset=circuit_contract.provenance.dataset,
        graph_scope_id=GRAPH_SCOPE_ID,
        nodes=nodes,
        edges=tuple(active_edges),
        circuit_integrity=integrity,
    )
    graph.validate_phase2b_scope()
    return graph


def _normalize_values(values: Any, label: str) -> tuple[float, ...]:
    if isinstance(values, (str, bytes)):
        raise SimulationInputError(
            f"{label} must be a one-dimensional numeric sequence."
        )
    if isinstance(values, np.ndarray):
        if values.ndim != 1:
            raise SimulationInputError(f"{label} must be one-dimensional.")
        sequence = values.tolist()
    elif isinstance(values, Sequence):
        sequence = list(values)
    else:
        raise SimulationInputError(
            f"{label} must be a one-dimensional numeric sequence."
        )
    normalized: list[float] = []
    for index, value in enumerate(sequence):
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise SimulationInputError(f"{label}[{index}] must be finite.") from None
        if not math.isfinite(number):
            raise SimulationInputError(f"{label}[{index}] must be finite.")
        normalized.append(number)
    return tuple(normalized)


def _normalize_target_mapping(
    values: Mapping[Any, Any], *, steps: int | None, label: str
) -> tuple[int, tuple[tuple[int, tuple[float, ...]], ...]]:
    if not isinstance(values, Mapping):
        raise SimulationInputError(f"{label} must be a mapping.")
    if steps is not None and (
        isinstance(steps, bool) or not isinstance(steps, int) or steps < 0
    ):
        raise SimulationInputError("steps must be a non-negative integer.")
    normalized = []
    inferred_steps = steps
    for target, raw_values in values.items():
        if isinstance(target, bool) or not isinstance(target, int):
            raise SimulationInputError(f"{label} targets must be integer IDs/indices.")
        series = _normalize_values(raw_values, f"{label}[{target}]")
        if inferred_steps is None:
            inferred_steps = len(series)
        if len(series) != inferred_steps:
            raise SimulationInputError(
                f"{label} values must all have exactly {inferred_steps} steps."
            )
        normalized.append((target, series))
    if inferred_steps is None:
        raise SimulationInputError(
            f"{label} requires explicit steps when no targets are supplied."
        )
    if inferred_steps < 0:
        raise SimulationInputError("steps cannot be negative.")
    return int(inferred_steps), tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class ExternalDriveSchedule:
    """Deterministic piecewise-constant caller-supplied input schedule."""

    steps: int
    by_body_id: tuple[tuple[int, tuple[float, ...]], ...] = ()
    by_node_index: tuple[tuple[int, tuple[float, ...]], ...] = ()
    provenance_id: str = "caller_supplied_v1"

    def __post_init__(self) -> None:
        if (
            isinstance(self.steps, bool)
            or not isinstance(self.steps, int)
            or self.steps < 0
        ):
            raise SimulationInputError("steps must be a non-negative integer.")
        if not isinstance(self.provenance_id, str) or not self.provenance_id:
            raise SimulationInputError("provenance_id must be non-empty.")
        try:
            body_entries = self._validate_entries(self.by_body_id, "by_body_id")
            node_entries = self._validate_entries(self.by_node_index, "by_node_index")
        except TypeError:
            raise SimulationInputError(
                "drive entries must be iterable (target, one-dimensional values)."
            ) from None
        object.__setattr__(self, "by_body_id", body_entries)
        object.__setattr__(self, "by_node_index", node_entries)

    def _validate_entries(
        self,
        entries: Iterable[tuple[int, tuple[float, ...]]],
        label: str,
    ) -> tuple[tuple[int, tuple[float, ...]], ...]:
        normalized: list[tuple[int, tuple[float, ...]]] = []
        seen: set[int] = set()
        for target, values in entries:
            if isinstance(target, bool) or not isinstance(target, int):
                raise SimulationInputError(f"{label} targets must be integers.")
            if target in seen:
                raise SimulationInputError(f"Duplicate {label} target {target}.")
            seen.add(target)
            series = _normalize_values(values, f"{label}[{target}]")
            if len(series) != self.steps:
                raise SimulationInputError(
                    f"{label}[{target}] must contain exactly {self.steps} steps."
                )
            normalized.append((target, series))
        return tuple(sorted(normalized))

    @classmethod
    def from_body_ids(
        cls,
        values: Mapping[int, Any],
        *,
        steps: int | None = None,
        provenance_id: str = "caller_supplied_v1",
    ) -> ExternalDriveSchedule:
        inferred_steps, normalized = _normalize_target_mapping(
            values, steps=steps, label="body_id drive"
        )
        return cls(
            steps=inferred_steps,
            by_body_id=normalized,
            provenance_id=provenance_id,
        )

    @classmethod
    def from_node_indices(
        cls,
        values: Mapping[int, Any],
        *,
        steps: int | None = None,
        provenance_id: str = "caller_supplied_v1",
    ) -> ExternalDriveSchedule:
        inferred_steps, normalized = _normalize_target_mapping(
            values, steps=steps, label="node_index drive"
        )
        return cls(
            steps=inferred_steps,
            by_node_index=normalized,
            provenance_id=provenance_id,
        )

    @classmethod
    def zeros(
        cls, steps: int, *, provenance_id: str = "caller_supplied_zero_v1"
    ) -> ExternalDriveSchedule:
        return cls(steps=steps, provenance_id=provenance_id)

    def to_matrix(
        self, graph: SimulationGraph, *, allow_model_readout_drive: bool = False
    ) -> np.ndarray:
        matrix = np.zeros((self.steps, graph.node_count), dtype=np.float64)
        targeted_indices: set[int] = set()
        for body_id, values in self.by_body_id:
            node_index = graph.node_index_by_body_id.get(body_id)
            if node_index is None:
                raise SimulationInputError(
                    f"Unknown body ID in external drive: {body_id}."
                )
            targeted_indices.add(node_index)
            matrix[:, node_index] = values
        for node_index, values in self.by_node_index:
            if node_index < 0 or node_index >= graph.node_count:
                raise SimulationInputError(
                    f"Unknown node index in external drive: {node_index}."
                )
            if node_index in targeted_indices:
                raise SimulationInputError(
                    f"Node index {node_index} is targeted more than once."
                )
            targeted_indices.add(node_index)
            matrix[:, node_index] = values
        for node_index, node in enumerate(graph.nodes):
            if (
                not allow_model_readout_drive
                and node.type == READOUT_TYPE
                and np.any(matrix[:, node_index] != 0.0)
            ):
                raise SimulationInputError(
                    "Direct external drive to DNp01 is not allowed in normal mode."
                )
        matrix.setflags(write=False)
        return matrix


@dataclass(frozen=True, slots=True)
class SpikeEvent:
    """A fixed-step threshold event timestamped at the interval end."""

    time_ms: float
    step: int
    body_id: int
    node_index: int
    neuron_type: str


@dataclass(frozen=True, slots=True)
class DeliveredSynapticEvent:
    """A delivered event retaining structural and model coupling separately."""

    delivery_time_ms: float
    delivery_step: int
    source_body_id: int
    target_body_id: int
    source_index: int
    target_index: int
    structural_weight: int
    model_sign: int
    event_increment_mV_eq: float


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """In-memory deterministic telemetry for one Phase 2B run.

    ``membrane_mv`` and ``synaptic_mveq`` contain boundary states at
    ``times_ms``. ``external_drive_mveq`` and ``incoming_coupling_mveq`` contain
    the values applied/delivered during each interval starting at the matching
    step. Arrays are read-only views.
    """

    times_ms: np.ndarray
    body_ids: tuple[int, ...]
    neuron_types: tuple[str | None, ...]
    neuron_sides: tuple[str | None, ...]
    membrane_mv: np.ndarray
    synaptic_mveq: np.ndarray
    external_drive_mveq: np.ndarray
    incoming_coupling_mveq: np.ndarray
    spikes: tuple[SpikeEvent, ...]
    delivered_events: tuple[DeliveredSynapticEvent, ...]
    first_spike_time_ms_by_body_id: Mapping[int, float | None]
    metadata: Mapping[str, Any]

    @property
    def steps(self) -> int:
        return int(self.external_drive_mveq.shape[0])

    @property
    def dnp01_first_spike_time_ms(self) -> Mapping[int, float | None]:
        return MappingProxyType(
            {
                body_id: self.first_spike_time_ms_by_body_id.get(body_id)
                for body_id, neuron_type in zip(self.body_ids, self.neuron_types)
                if neuron_type == READOUT_TYPE
            }
        )

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "metadata": dict(self.metadata),
            "body_ids": list(self.body_ids),
            "neuron_types": list(self.neuron_types),
            "neuron_sides": list(self.neuron_sides),
            "steps": self.steps,
            "spike_count": len(self.spikes),
            "spikes": [
                {
                    "time_ms": event.time_ms,
                    "step": event.step,
                    "body_id": event.body_id,
                    "node_index": event.node_index,
                    "neuron_type": event.neuron_type,
                }
                for event in self.spikes
            ],
            "dnp01_first_spike_time_ms": dict(self.dnp01_first_spike_time_ms),
        }


def _as_schedule(
    external_drive: ExternalDriveSchedule | Mapping[int, Any] | np.ndarray | None,
    *,
    steps: int | None,
    graph: SimulationGraph,
) -> ExternalDriveSchedule:
    if steps is not None and (
        isinstance(steps, bool) or not isinstance(steps, int) or steps < 0
    ):
        raise SimulationInputError("steps must be a non-negative integer.")
    if external_drive is None:
        if steps is None:
            raise SimulationInputError(
                "steps is required when external_drive is absent."
            )
        return ExternalDriveSchedule.zeros(steps)
    if isinstance(external_drive, ExternalDriveSchedule):
        if steps is not None and steps != external_drive.steps:
            raise SimulationInputError(
                f"steps={steps} does not match external-drive "
                f"steps={external_drive.steps}."
            )
        return external_drive
    if isinstance(external_drive, Mapping):
        schedule = ExternalDriveSchedule.from_body_ids(external_drive, steps=steps)
        return schedule
    if isinstance(external_drive, np.ndarray):
        if external_drive.ndim != 2:
            raise SimulationInputError(
                "Array external_drive must have shape (steps, node_count)."
            )
        inferred_steps = int(external_drive.shape[0])
        if steps is not None and steps != inferred_steps:
            raise SimulationInputError(
                f"steps={steps} does not match external-drive steps={inferred_steps}."
            )
        if external_drive.shape[1] != graph.node_count:
            raise SimulationInputError(
                "Array external_drive must have one column per graph node."
            )
        try:
            finite = np.isfinite(external_drive).all()
        except TypeError:
            raise SimulationInputError(
                "external_drive must contain only finite numeric values."
            ) from None
        if not finite:
            raise SimulationInputError(
                "external_drive must contain only finite values."
            )
        body_values = {
            node.body_id: external_drive[:, index].tolist()
            for index, node in enumerate(graph.nodes)
            if np.any(external_drive[:, index] != 0.0)
        }
        return ExternalDriveSchedule.from_body_ids(
            body_values,
            steps=inferred_steps,
            provenance_id="caller_supplied_array_v1",
        )
    raise SimulationInputError(
        "external_drive must be an ExternalDriveSchedule, body-ID mapping, or "
        "(steps, node_count) NumPy array."
    )


def _initial_values(
    values: Mapping[int, Any] | None,
    *,
    graph: SimulationGraph,
    default: float,
    field_name: str,
) -> np.ndarray:
    state = np.full(graph.node_count, default, dtype=np.float64)
    if values is None:
        return state
    if not isinstance(values, Mapping):
        raise SimulationInputError(f"{field_name} must be a body-ID mapping.")
    for body_id, value in values.items():
        if isinstance(body_id, bool) or not isinstance(body_id, int):
            raise SimulationInputError(f"{field_name} body IDs must be integers.")
        index = graph.node_index_by_body_id.get(body_id)
        if index is None:
            raise SimulationInputError(f"Unknown body ID in {field_name}: {body_id}.")
        try:
            state[index] = float(value)
        except (TypeError, ValueError):
            raise SimulationInputError(
                f"{field_name}[{body_id}] must be finite."
            ) from None
        if not math.isfinite(state[index]):
            raise SimulationInputError(f"{field_name}[{body_id}] must be finite.")
    return state


class LIFSimulator:
    """Run the deterministic M1 model on an explicit simulation graph."""

    def __init__(
        self,
        graph: SimulationGraph,
        config: LIFConfig,
    ) -> None:
        if not isinstance(graph, SimulationGraph):
            raise SimulationGraphError("graph must be a SimulationGraph.")
        if not isinstance(config, LIFConfig):
            raise SimulationConfigurationError("config must be an LIFConfig.")
        if graph.graph_scope_id == PHASE7F_READOUT_SCOPE_ID:
            graph.validate_phase7f_readout_scope()
        else:
            graph.validate_phase2b_scope()
        if config.graph_scope_id != graph.graph_scope_id:
            raise SimulationConfigurationError(
                "Configuration graph_scope_id does not match simulation graph."
            )
        self.graph = graph
        self.config = config

    def run(
        self,
        external_drive: ExternalDriveSchedule
        | Mapping[int, Any]
        | np.ndarray
        | None = None,
        *,
        steps: int | None = None,
        record_body_ids: Iterable[int] | None = None,
        initial_v_mv: Mapping[int, Any] | None = None,
        initial_s_mveq: Mapping[int, Any] | None = None,
        allow_model_readout_drive: bool = False,
    ) -> SimulationResult:
        schedule = _as_schedule(external_drive, steps=steps, graph=self.graph)
        if allow_model_readout_drive:
            if self.graph.graph_scope_id != PHASE7F_READOUT_SCOPE_ID:
                raise SimulationInputError(
                    "Phase 7F DNp01 model drive requires the two-readout graph."
                )
            if (
                schedule.provenance_id
                != "phase7f_edge_routed_exploratory_model_drive_v1"
            ):
                raise SimulationInputError(
                    "Direct DNp01 model drive requires Phase 7F provenance."
                )
            if (
                any(body_id not in (10001, 10010) for body_id, _ in schedule.by_body_id)
                or schedule.by_node_index
            ):
                raise SimulationInputError(
                    "Phase 7F model drive may target only the two DNp01 body IDs."
                )
        drive = schedule.to_matrix(
            self.graph, allow_model_readout_drive=allow_model_readout_drive
        )
        record_indices = self._record_indices(record_body_ids)
        v = _initial_values(
            initial_v_mv,
            graph=self.graph,
            default=self.config.rest_mv,
            field_name="initial_v_mv",
        )
        s = _initial_values(
            initial_s_mveq,
            graph=self.graph,
            default=0.0,
            field_name="initial_s_mveq",
        )
        if np.any(~np.isfinite(v)) or np.any(~np.isfinite(s)):
            raise SimulationInputError("Initial state must contain only finite values.")

        steps = schedule.steps
        times = np.arange(steps + 1, dtype=np.float64) * self.config.dt_ms
        membrane = np.empty((steps + 1, len(record_indices)), dtype=np.float64)
        synaptic = np.empty((steps + 1, len(record_indices)), dtype=np.float64)
        incoming = np.zeros((steps, len(record_indices)), dtype=np.float64)
        membrane[0] = v[record_indices]
        synaptic[0] = s[record_indices]

        refractory_remaining = np.zeros(self.graph.node_count, dtype=np.int64)
        events: dict[int, list[SimulationEdge]] = defaultdict(list)
        spikes: list[SpikeEvent] = []
        delivered_events: list[DeliveredSynapticEvent] = []
        first_spike: dict[int, float | None] = {
            node.body_id: None for node in self.graph.nodes
        }
        outgoing: dict[int, tuple[SimulationEdge, ...]] = defaultdict(tuple)
        outgoing_lists: dict[int, list[SimulationEdge]] = defaultdict(list)
        for edge in self.graph.edges:
            outgoing_lists[edge.source_index].append(edge)
        outgoing = {
            source: tuple(
                sorted(edges, key=lambda edge: (edge.target_index, edge.edge_index))
            )
            for source, edges in outgoing_lists.items()
        }

        exp_m = math.exp(-self.config.dt_ms / self.config.tau_m_ms)
        exp_s = math.exp(-self.config.dt_ms / self.config.tau_s_ms)
        leak_drive_factor = 1.0 - exp_m
        if math.isclose(
            self.config.tau_s_ms,
            self.config.tau_m_ms,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            filtered_factor = (self.config.dt_ms / self.config.tau_m_ms) * exp_m
        else:
            filtered_factor = (
                self.config.tau_s_ms
                / (self.config.tau_s_ms - self.config.tau_m_ms)
                * (exp_s - exp_m)
            )

        for step in range(steps):
            delivery = sorted(
                events.pop(step, []),
                key=lambda edge: (
                    edge.source_index,
                    edge.target_index,
                    edge.edge_index,
                ),
            )
            incoming_all = np.zeros(self.graph.node_count, dtype=np.float64)
            for edge in delivery:
                increment = edge.event_increment(self.config.k_syn_mv_per_contact)
                s[edge.target_index] += increment
                incoming_all[edge.target_index] += increment
                delivered_events.append(
                    DeliveredSynapticEvent(
                        delivery_time_ms=step * self.config.dt_ms,
                        delivery_step=step,
                        source_body_id=edge.source_body_id,
                        target_body_id=edge.target_body_id,
                        source_index=edge.source_index,
                        target_index=edge.target_index,
                        structural_weight=edge.structural_weight,
                        model_sign=edge.model_sign,
                        event_increment_mV_eq=increment,
                    )
                )

            can_integrate = refractory_remaining == 0
            old_s = s.copy()
            s *= exp_s
            next_v = v.copy()
            next_v[can_integrate] = (
                self.config.rest_mv
                + (v[can_integrate] - self.config.rest_mv) * exp_m
                + drive[step, can_integrate] * leak_drive_factor
                + old_s[can_integrate] * filtered_factor
            )
            next_v[~can_integrate] = self.config.reset_mv
            refractory_remaining[~can_integrate] -= 1

            if not np.isfinite(s).all() or not np.isfinite(next_v).all():
                raise SimulationError(
                    "Simulation state became non-finite; reduce drive or parameters."
                )

            thresholded = np.flatnonzero(
                can_integrate & (next_v >= self.config.threshold_mv)
            )
            spike_step = step + 1
            spike_time_ms = spike_step * self.config.dt_ms
            for node_index in thresholded.tolist():
                node = self.graph.nodes[node_index]
                spikes.append(
                    SpikeEvent(
                        time_ms=spike_time_ms,
                        step=spike_step,
                        body_id=node.body_id,
                        node_index=node_index,
                        neuron_type=node.type or "",
                    )
                )
                if first_spike[node.body_id] is None:
                    first_spike[node.body_id] = spike_time_ms
                next_v[node_index] = self.config.reset_mv
                refractory_remaining[node_index] = self.config.refractory_steps
                for edge in outgoing.get(node_index, ()):
                    events[spike_step + self.config.delay_steps].append(edge)

            v = next_v
            membrane[spike_step] = v[record_indices]
            synaptic[spike_step] = s[record_indices]
            incoming[step] = incoming_all[record_indices]

        return SimulationResult(
            times_ms=_readonly(times),
            body_ids=tuple(self.graph.nodes[index].body_id for index in record_indices),
            neuron_types=tuple(
                self.graph.nodes[index].type for index in record_indices
            ),
            neuron_sides=tuple(
                self.graph.nodes[index].soma_side for index in record_indices
            ),
            membrane_mv=_readonly(membrane),
            synaptic_mveq=_readonly(synaptic),
            external_drive_mveq=_readonly(np.asarray(drive[:, record_indices])),
            incoming_coupling_mveq=_readonly(incoming),
            spikes=tuple(spikes),
            delivered_events=tuple(delivered_events),
            first_spike_time_ms_by_body_id=MappingProxyType(dict(first_spike)),
            metadata=MappingProxyType(
                {
                    "model_id": self.config.model_id,
                    "model_version": self.config.model_version,
                    "graph_scope_id": self.graph.graph_scope_id,
                    "candidate_identifier": self.graph.candidate_identifier,
                    "candidate_version": self.graph.candidate_version,
                    "dataset": self.graph.dataset,
                    "endpoint": NEUPRINT_ENDPOINT,
                    "circuit_integrity": dict(self.graph.circuit_integrity),
                    "config": self.config.to_dict(),
                    "dt_ms": self.config.dt_ms,
                    "k_syn_mv_per_contact": self.config.k_syn_mv_per_contact,
                    "delay_ms": self.config.delay_ms,
                    "sign_policy_id": self.config.sign_policy_id,
                    "baseline_policy": self.config.baseline_policy,
                    "stochastic_policy": self.config.stochastic_policy,
                    "input_drive_provenance_id": schedule.provenance_id,
                    "steps": steps,
                    "record_body_ids": [
                        self.graph.nodes[index].body_id for index in record_indices
                    ],
                }
            ),
        )

    def _record_indices(self, record_body_ids: Iterable[int] | None) -> np.ndarray:
        if record_body_ids is None:
            return np.arange(self.graph.node_count, dtype=np.int64)
        try:
            body_ids = tuple(record_body_ids)
        except TypeError:
            raise SimulationInputError("record_body_ids must be iterable.") from None
        if any(
            isinstance(body_id, bool) or not isinstance(body_id, int)
            for body_id in body_ids
        ):
            raise SimulationInputError("record_body_ids must contain integer IDs.")
        if len(body_ids) != len(set(body_ids)):
            raise SimulationInputError("record_body_ids must not contain duplicates.")
        indices: list[int] = []
        for body_id in body_ids:
            index = self.graph.node_index_by_body_id.get(body_id)
            if index is None:
                raise SimulationInputError(f"Unknown body ID to record: {body_id}.")
            indices.append(index)
        return np.asarray(indices, dtype=np.int64)


def _readonly(array: np.ndarray) -> np.ndarray:
    result = np.asarray(array, dtype=np.float64)
    result.setflags(write=False)
    return result


__all__ = [
    "EXTERNAL_DRIVE_SEMANTICS",
    "GRAPH_SCOPE_ID",
    "LIFConfig",
    "LIFSimulator",
    "MODEL_ID",
    "MODEL_VERSION",
    "SIGN_POLICY_ID",
    "SimulationEdge",
    "SimulationError",
    "SimulationGraph",
    "SimulationGraphError",
    "SimulationConfigurationError",
    "SimulationInputError",
    "SimulationResult",
    "SpikeEvent",
    "DeliveredSynapticEvent",
    "ExternalDriveSchedule",
    "build_phase2b_graph",
]
