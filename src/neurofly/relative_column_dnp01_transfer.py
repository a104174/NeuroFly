"""Phase 7F: four exploratory sensory states routed to two DNp01 models.

MaleCNS counts select edges only. They never enter the transfer equation.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from neurofly.malecns.contract import load_circuit_contract
from neurofly.relative_column_assignment import (
    BODY_IDENTITIES,
    BODY_IDS,
    DEFAULT_SOURCE_ROOT,
    canonical_json_bytes,
    sha256_bytes,
)
from neurofly.relative_column_sensory_artifacts import (
    ARTIFACT_SCHEMA_VERSION as SENSORY_ARTIFACT_SCHEMA,
)
from neurofly.relative_column_sensory_artifacts import (
    LoadedRelativeColumnSensoryArtifact,
)
from neurofly.relative_column_sensory_dynamics import SENSORY_STATE_RESULT_SCHEMA
from neurofly.simulation import (
    EXTERNAL_DRIVE_SEMANTICS,
    PHASE7F_READOUT_SCOPE_ID,
    SIGN_POLICY_ID,
    ExternalDriveSchedule,
    LIFConfig,
    LIFSimulator,
    SimulationGraph,
)

CONFIG_SCHEMA = "relative_column_sensory_to_dnp01_config_v1"
RESULT_SCHEMA = "relative_column_sensory_to_dnp01_result_v1"
MODEL_ID = "exploratory_edge_routed_model_drive_v1"
EXPERIMENT_ID = "phase7f_four_body_sensory_to_dnp01_v1"
EXPECTED_SENSORY_ARTIFACT_ID = (
    "09a3d3ddc02c81bb5ea229bf48b76811123ebd2e20cfce17f45e72442dcb8b15"
)
DRIVE_PROVENANCE_ID = "phase7f_edge_routed_exploratory_model_drive_v1"
REFERENCE_K_MVEQ_PER_STATE = 1.0
SENSITIVITY_K = (0.0, 0.5, 1.0, 2.0, 4.0)
TARGET_IDENTITIES = (
    {"body_id": 10001, "neuron_type": "DNp01", "side": "R"},
    {"body_id": 10010, "neuron_type": "DNp01", "side": "L"},
)
EXPECTED_ROUTES = (
    (11498, 10010, 2),
    (12032, 10010, 62),
    (14465, 10001, 21),
    (16128, 10001, 65),
)
CONDITION_SPECS = (
    (
        "reference_bilateral_expansion",
        "left_expand_33_29",
        "right_expand_23_09",
        "both",
        1.0,
    ),
    ("k_zero", "left_expand_33_29", "right_expand_23_09", "both", 0.0),
    ("no_sources", "left_expand_33_29", "right_expand_23_09", "none", 1.0),
    ("lc4_only", "left_expand_33_29", "right_expand_23_09", "LC4", 1.0),
    ("lplc2_only", "left_expand_33_29", "right_expand_23_09", "LPLC2", 1.0),
    ("left_lplc2_disk", "left_lplc2_11498_18_04", None, "both", 1.0),
    ("right_translated_disk", None, "right_translate_23_11", "both", 1.0),
    ("sensitivity_k_0_5", "left_expand_33_29", "right_expand_23_09", "both", 0.5),
    ("sensitivity_k_2", "left_expand_33_29", "right_expand_23_09", "both", 2.0),
    ("sensitivity_k_4", "left_expand_33_29", "right_expand_23_09", "both", 4.0),
)


class SensoryToDNp01Error(ValueError):
    """Input, route, or time identity is not the bounded Phase 7F contract."""


@dataclass(frozen=True, slots=True)
class Route:
    source_body_id: int
    target_body_id: int
    structural_weight: int
    source_type: str
    side: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_body_id": self.source_body_id,
            "target_body_id": self.target_body_id,
            "structural_weight": self.structural_weight,
            "source_type": self.source_type,
            "side": self.side,
            "weight_semantics": "STRUCTURAL_COUNT_ROUTING_METADATA_ONLY",
        }


def _finite_nonnegative(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SensoryToDNp01Error(f"{name} must be finite and nonnegative.")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise SensoryToDNp01Error(f"{name} must be finite and nonnegative.")
    return number


def validated_routes(contract: Any) -> tuple[Route, ...]:
    """Require all four exact pinned chemical observations and six identities."""

    if (
        getattr(getattr(contract, "provenance", None), "dataset", None)
        != "male-cns:v1.0"
    ):
        raise SensoryToDNp01Error("routing dataset must be male-cns:v1.0.")
    identities = {node.body_id: node for node in contract.neurons}
    for item in (*BODY_IDENTITIES, *TARGET_IDENTITIES):
        node = identities.get(item["body_id"])
        if node is None or (node.type, node.soma_side) != (
            item["neuron_type"],
            item["side"],
        ):
            raise SensoryToDNp01Error("six-body routing identity mismatch.")
    expected_pairs = {(source, target) for source, target, _ in EXPECTED_ROUTES}
    found = [
        edge
        for edge in contract.connections
        if edge.source_body_id in BODY_IDS and edge.target_body_id in (10001, 10010)
    ]
    if (
        len(found) != 4
        or {(edge.source_body_id, edge.target_body_id) for edge in found}
        != expected_pairs
    ):
        raise SensoryToDNp01Error("four-edge routing identity mismatch.")
    expected_weights = {
        (source, target): weight for source, target, weight in EXPECTED_ROUTES
    }
    routes = []
    for edge in found:
        source = identities[edge.source_body_id]
        target = identities[edge.target_body_id]
        if (
            edge.dataset != "male-cns:v1.0"
            or (edge.source_type, edge.target_type) != (source.type, "DNp01")
            or source.soma_side != target.soma_side
            or edge.structural_weight
            != expected_weights[(edge.source_body_id, edge.target_body_id)]
        ):
            raise SensoryToDNp01Error("routing side/type/weight mismatch.")
        routes.append(
            Route(
                edge.source_body_id,
                edge.target_body_id,
                edge.structural_weight,
                source.type,
                source.soma_side,
            )
        )
    return tuple(
        sorted(routes, key=lambda route: (route.source_body_id, route.target_body_id))
    )


def build_readout_graph(contract: Any) -> SimulationGraph:
    """Reuse LIF on only the two validated DNp01 nodes, with no graph edges."""

    validated_routes(contract)
    graph = SimulationGraph(
        candidate_identifier=contract.candidate.identifier,
        candidate_version=contract.candidate.version,
        dataset=contract.provenance.dataset,
        graph_scope_id=PHASE7F_READOUT_SCOPE_ID,
        nodes=(contract.neurons_by_body_id[10001], contract.neurons_by_body_id[10010]),
        edges=(),
        circuit_integrity=tuple(contract.integrity.sha256_by_file),
    )
    graph.validate_phase7f_readout_scope()
    return graph


def route_drive(
    source_states: Mapping[int, float],
    routes: Sequence[Route],
    *,
    k_transfer_mveq_per_state: float,
    pathway_mask: str = "both",
) -> tuple[dict[int, float], list[dict[str, Any]]]:
    """Apply one shared conversion and sum by target; structural count unused."""

    k = _finite_nonnegative(k_transfer_mveq_per_state, "k_transfer_mveq_per_state")
    if pathway_mask not in {"none", "LC4", "LPLC2", "both"}:
        raise SensoryToDNp01Error("unsupported pathway mask.")
    if set(source_states) != set(BODY_IDS):
        raise SensoryToDNp01Error("source states must contain exactly four bodies.")
    if {(route.source_body_id, route.target_body_id) for route in routes} != {
        (source, target) for source, target, _ in EXPECTED_ROUTES
    } or len(routes) != 4:
        raise SensoryToDNp01Error("route set must contain the four pinned pairs.")
    identity_by_body = {item["body_id"]: item for item in BODY_IDENTITIES}
    target_side = {item["body_id"]: item["side"] for item in TARGET_IDENTITIES}
    if any(
        route.source_type != identity_by_body[route.source_body_id]["neuron_type"]
        or route.side != identity_by_body[route.source_body_id]["side"]
        or route.side != target_side[route.target_body_id]
        or isinstance(route.structural_weight, bool)
        or not isinstance(route.structural_weight, int)
        or route.structural_weight <= 0
        for route in routes
    ):
        raise SensoryToDNp01Error("route type/side/count metadata is invalid.")
    active_source_ids = {
        route.source_body_id
        for route in routes
        if pathway_mask == "both" or pathway_mask == route.source_type
    }
    return route_population_drive(
        source_states,
        routes,
        target_body_ids=(10001, 10010),
        active_source_ids=active_source_ids,
        k_transfer_mveq_per_state=k,
    )


def route_population_drive(
    source_states: Mapping[int, float],
    routes: Sequence[Route],
    *,
    target_body_ids: Sequence[int],
    active_source_ids: set[int] | frozenset[int],
    k_transfer_mveq_per_state: float,
) -> tuple[dict[int, float], list[dict[str, Any]]]:
    """Shared Phase 7F transfer primitive for an explicit bounded body sample.

    Routing metadata is validated but never enters the numerical contribution.
    Callers must validate source identities and the route contract before use.
    """

    k = _finite_nonnegative(k_transfer_mveq_per_state, "k_transfer_mveq_per_state")
    targets = tuple(target_body_ids)
    if not targets or len(targets) != len(set(targets)):
        raise SensoryToDNp01Error(
            "target body identities must be unique and non-empty."
        )
    route_sources = {route.source_body_id for route in routes}
    if set(source_states) != route_sources:
        raise SensoryToDNp01Error("source states must match the explicit route set.")
    if not set(active_source_ids) <= route_sources:
        raise SensoryToDNp01Error("active source mask contains an unrouted body.")
    if any(route.target_body_id not in targets for route in routes):
        raise SensoryToDNp01Error("route targets an unsupported readout body.")
    if len({(route.source_body_id, route.target_body_id) for route in routes}) != len(
        routes
    ):
        raise SensoryToDNp01Error("route set contains duplicate source-target pairs.")
    if any(
        isinstance(route.structural_weight, bool)
        or not isinstance(route.structural_weight, int)
        or route.structural_weight <= 0
        for route in routes
    ):
        raise SensoryToDNp01Error("route structural count metadata is invalid.")

    output = {target: 0.0 for target in targets}
    contributions = []
    for route in sorted(
        routes, key=lambda item: (item.source_body_id, item.target_body_id)
    ):
        source = _finite_nonnegative(
            source_states[route.source_body_id], "sensory state"
        )
        contribution = k * source if route.source_body_id in active_source_ids else 0.0
        if not math.isfinite(contribution):
            raise SensoryToDNp01Error("transfer contribution became non-finite.")
        output[route.target_body_id] += contribution
        if not math.isfinite(output[route.target_body_id]):
            raise SensoryToDNp01Error("summed target drive became non-finite.")
        contributions.append(
            {
                "source_body_id": route.source_body_id,
                "target_body_id": route.target_body_id,
                "model_drive_mveq": contribution,
            }
        )
    return output, contributions


def _validated_timelines(
    artifact: LoadedRelativeColumnSensoryArtifact,
) -> dict[str, tuple[str, float, dict[int, list[float]]]]:
    if (
        artifact.artifact_id != EXPECTED_SENSORY_ARTIFACT_ID
        or artifact.manifest.get("artifact_schema_version") != SENSORY_ARTIFACT_SCHEMA
        or artifact.result.get("schema") != SENSORY_STATE_RESULT_SCHEMA
        or tuple(artifact.result.get("body_ids", ())) != BODY_IDS
        or artifact.result.get("state_semantics")
        != "EXPLORATORY_DIMENSIONLESS_SENSORY_MODEL_STATE"
    ):
        raise SensoryToDNp01Error("wrong or malformed Phase 7E source artifact.")
    if sha256_bytes(
        canonical_json_bytes(dict(artifact.config)) + b"\n"
    ) != artifact.manifest.get("config_sha256") or sha256_bytes(
        canonical_json_bytes(dict(artifact.result)) + b"\n"
    ) != artifact.manifest.get("result_sha256"):
        raise SensoryToDNp01Error("Phase 7E source payload hash mismatch.")
    parsed = {}
    expected = {
        "left_expand_33_29": "L",
        "left_lplc2_11498_18_04": "L",
        "right_expand_23_09": "R",
        "right_translate_23_11": "R",
    }
    conditions = artifact.result.get("conditions")
    if not isinstance(conditions, list) or len(conditions) != 4:
        raise SensoryToDNp01Error("Phase 7E conditions are malformed.")
    for condition in conditions:
        name = condition.get("stimulus_id")
        side = condition.get("side")
        dt = condition.get("dt_ms")
        if (
            name not in expected
            or side != expected[name]
            or name in parsed
            or not isinstance(dt, (int, float))
            or not math.isfinite(dt)
            or dt <= 0
        ):
            raise SensoryToDNp01Error("Phase 7E condition identity/grid mismatch.")
        trajectories = condition.get("body_trajectories")
        if not isinstance(trajectories, list) or len(trajectories) != 4:
            raise SensoryToDNp01Error("Phase 7E trajectories are malformed.")
        by_body = {}
        length = None
        for trajectory in trajectories:
            body_id = trajectory.get("body_id")
            identity = next(
                (item for item in BODY_IDENTITIES if item["body_id"] == body_id), None
            )
            if (
                identity is None
                or body_id in by_body
                or (trajectory.get("neuron_type"), trajectory.get("side"))
                != (identity["neuron_type"], identity["side"])
            ):
                raise SensoryToDNp01Error("Phase 7E body identity mismatch.")
            rows = trajectory.get("state_timeline")
            if not isinstance(rows, list) or len(rows) < 2:
                raise SensoryToDNp01Error("Phase 7E state timeline is malformed.")
            if length is None:
                length = len(rows)
            if len(rows) != length:
                raise SensoryToDNp01Error("Phase 7E body timelines differ in length.")
            states = []
            for step, row in enumerate(rows):
                value = _finite_nonnegative(row.get("state_value"), "sensory state")
                if row.get("state_step") != step or row.get("time_ms") != step * dt:
                    raise SensoryToDNp01Error(
                        "Phase 7E integer-step identity mismatch."
                    )
                if identity["side"] != side and value != 0.0:
                    raise SensoryToDNp01Error(
                        "Phase 7E opposite-side state is nonzero."
                    )
                states.append(value)
            by_body[body_id] = states
        if set(by_body) != set(BODY_IDS):
            raise SensoryToDNp01Error("Phase 7E body set mismatch.")
        parsed[name] = (side, float(dt), by_body)
    if set(parsed) != set(expected):
        raise SensoryToDNp01Error("Phase 7E stimulus set mismatch.")
    return parsed


def _condition(
    *,
    condition_id: str,
    left_stimulus_id: str | None,
    right_stimulus_id: str | None,
    pathway_mask: str,
    k_transfer_mveq_per_state: float,
    timelines: Mapping[str, tuple[str, float, dict[int, list[float]]]],
    routes: Sequence[Route],
    simulator: LIFSimulator,
) -> dict[str, Any]:
    selections = [
        timelines[item] for item in (left_stimulus_id, right_stimulus_id) if item
    ]
    if not selections:
        raise SensoryToDNp01Error("condition needs a source timeline.")
    dt = simulator.config.dt_ms
    if any(source_dt != dt for _, source_dt, _ in selections):
        raise SensoryToDNp01Error("sensory and DNp01 grids differ.")
    steps = max(len(states[next(iter(states))]) - 1 for _, _, states in selections)
    states_by_body = {body_id: [0.0] * (steps + 1) for body_id in BODY_IDS}
    for side, _, source in selections:
        for identity in BODY_IDENTITIES:
            if identity["side"] == side:
                states_by_body[identity["body_id"]][
                    : len(source[identity["body_id"]])
                ] = source[identity["body_id"]]
    drive = {10001: [], 10010: []}
    contribution_rows = []
    for step in range(steps):
        current = {body_id: states[step] for body_id, states in states_by_body.items()}
        summed, contributions = route_drive(
            current,
            routes,
            k_transfer_mveq_per_state=k_transfer_mveq_per_state,
            pathway_mask=pathway_mask,
        )
        for target in drive:
            drive[target].append(summed[target])
        contribution_rows.append(
            {"step": step, "time_ms": step * dt, "contributions": contributions}
        )
    schedule = ExternalDriveSchedule.from_body_ids(
        drive, steps=steps, provenance_id=DRIVE_PROVENANCE_ID
    )
    simulation = simulator.run(
        schedule,
        record_body_ids=(10001, 10010),
        allow_model_readout_drive=True,
    )
    if simulation.delivered_events or any(
        spike.body_id not in (10001, 10010) for spike in simulation.spikes
    ):
        raise SensoryToDNp01Error("unexpected source synapse or non-DNp01 event.")
    targets = []
    for column, body_id in enumerate(simulation.body_ids):
        membrane = simulation.membrane_mv[:, column].tolist()
        filtered = simulation.synaptic_mveq[:, column].tolist()
        series = drive[body_id]
        peak_step = max(range(steps), key=series.__getitem__)
        targets.append(
            {
                "body_id": body_id,
                "side": next(
                    item["side"]
                    for item in TARGET_IDENTITIES
                    if item["body_id"] == body_id
                ),
                "contributing_source_body_ids": [
                    route.source_body_id
                    for route in routes
                    if route.target_body_id == body_id
                    and (pathway_mask == "both" or pathway_mask == route.source_type)
                ],
                "drive_mveq_by_interval": series,
                "peak_drive_mveq": series[peak_step],
                "peak_drive_step": peak_step,
                "peak_drive_time_ms": peak_step * dt,
                "membrane_mv_by_boundary": membrane,
                "minimum_membrane_mv": min(membrane),
                "maximum_membrane_mv": max(membrane),
                "filtered_synaptic_mveq_by_boundary": filtered,
                "maximum_filtered_synaptic_mveq": max(filtered),
                "simulated_spikes": [
                    {
                        "step": spike.step,
                        "time_ms": spike.time_ms,
                        "body_id": body_id,
                        "semantics": "SIMULATED_DNP01_MODEL_SPIKE",
                    }
                    for spike in simulation.spikes
                    if spike.body_id == body_id
                ],
            }
        )
    return {
        "condition_id": condition_id,
        "left_stimulus_id": left_stimulus_id,
        "right_stimulus_id": right_stimulus_id,
        "pathway_mask": pathway_mask,
        "k_transfer_mveq_per_state": k_transfer_mveq_per_state,
        "dt_ms": dt,
        "interval_count": steps,
        "time_alignment": "x_n_drives_dnp01_interval_n_to_n_plus_1",
        "source_contributions_by_interval": contribution_rows,
        "targets": targets,
    }


def compute_transfer_result(
    sensory_artifact: LoadedRelativeColumnSensoryArtifact,
    contract: Any,
    *,
    routes: Sequence[Route] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run fixed controls using replay-verified Phase 7E state and pinned routes."""

    timelines = _validated_timelines(sensory_artifact)
    pinned = validated_routes(contract)
    if routes is not None and tuple(routes) != pinned:
        raise SensoryToDNp01Error("custom routes cannot replace the pinned contract.")
    graph = build_readout_graph(contract)
    # Required by the unchanged LIFConfig schema but unreachable: this readout
    # graph has no event edges. This is not the Phase 7F transfer coefficient.
    lif_config = LIFConfig(
        k_syn_mv_per_contact=0.01,
        dt_ms=timelines["left_expand_33_29"][1],
        graph_scope_id=PHASE7F_READOUT_SCOPE_ID,
        input_drive_provenance_id=DRIVE_PROVENANCE_ID,
    )
    simulator = LIFSimulator(graph, lif_config)
    source_manifest_hash = sha256_bytes(
        canonical_json_bytes(dict(sensory_artifact.manifest)) + b"\n"
    )
    config = {
        "schema": CONFIG_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "model_id": MODEL_ID,
        "source_sensory_artifact": {
            "schema": SENSORY_ARTIFACT_SCHEMA,
            "artifact_id": sensory_artifact.artifact_id,
            "manifest_sha256": source_manifest_hash,
            "config_sha256": sensory_artifact.manifest["config_sha256"],
            "result_sha256": sensory_artifact.manifest["result_sha256"],
        },
        "routing": {
            "dataset": "male-cns:v1.0",
            "candidate_id": contract.candidate.identifier,
            "contract_file_hashes": dict(contract.integrity.sha256_by_file),
            "routes": [route.to_dict() for route in pinned],
            "classification": "MALECNS_CHEMICAL_STRUCTURAL_CONNECTIVITY_ROUTING_ONLY",
        },
        "transfer": {
            "equation": (
                "drive_i_mveq[n]=k_transfer_mveq_per_state*x_i[n]; "
                "target_drive=sum_routed_i(drive_i)"
            ),
            "reference_k_transfer_mveq_per_state": REFERENCE_K_MVEQ_PER_STATE,
            "sensitivity_k_transfer_mveq_per_state": list(SENSITIVITY_K),
            "parameter_classification": "MODEL_ASSUMPTION",
            "sign": "POSITIVE_DEPOLARIZING_MODEL_ASSUMPTION",
            "sign_provenance_id": SIGN_POLICY_ID,
            "input_state_semantics": "EXPLORATORY_DIMENSIONLESS_SENSORY_MODEL_STATE",
            "output_semantics": "EXPLORATORY_EDGE_ROUTED_MODEL_DRIVE",
            "output_units": EXTERNAL_DRIVE_SEMANTICS,
            "structural_weight_used_as_gain": False,
        },
        "dnp01_lif_config": lif_config.to_dict(),
        "graph_scope_id": graph.graph_scope_id,
        "body_ids": list(BODY_IDS) + [10001, 10010],
        "conditions": [item[0] for item in CONDITION_SPECS],
        "scientific_boundary": {
            "physiologically_calibrated": False,
            "type_level_angular_drive_present": False,
            "ttmn_propagation_present": False,
            "behavior_present": False,
        },
    }
    conditions = [
        _condition(
            condition_id=name,
            left_stimulus_id=left,
            right_stimulus_id=right,
            pathway_mask=mask,
            k_transfer_mveq_per_state=k,
            timelines=timelines,
            routes=pinned,
            simulator=simulator,
        )
        for name, left, right, mask, k in CONDITION_SPECS
    ]
    result = {
        "schema": RESULT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "model_id": MODEL_ID,
        "source_sensory_artifact_id": sensory_artifact.artifact_id,
        "body_ids": list(BODY_IDS) + [10001, 10010],
        "conditions": conditions,
        "result_semantics": "EXPLORATORY_TRANSFER_NOT_BIOLOGICAL_VALIDATION",
    }
    return config, result


def default_contract() -> Any:
    """Load and hash-validate the local pinned upstream CircuitContract."""

    return load_circuit_contract(DEFAULT_SOURCE_ROOT)
