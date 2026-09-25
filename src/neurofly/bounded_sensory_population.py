"""Phase 7H deterministic 16-body sensory architecture experiment.

This module composes the validated Phase 7D exposure, Phase 7E state, and
Phase 7F routing/LIF primitives. It is an offline bounded experiment, not a
replacement for the four-body versioned artifacts.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from neurofly.malecns.contract import CircuitContract, load_circuit_contract
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    EXPECTED_CIRCUIT_FILE_HASHES,
    EXPECTED_COLUMN_FILE_HASHES,
    RelativeColumnAssignmentSource,
    RelativeColumnGrid,
    RelativeColumnStimulus,
    active_column_set,
    canonical_json_bytes,
    compute_body_exposure,
    fixed_stimuli,
    load_relative_column_grid,
    load_relative_column_source,
    sha256_bytes,
)
from neurofly.relative_column_dnp01_transfer import (
    DRIVE_PROVENANCE_ID,
    REFERENCE_K_MVEQ_PER_STATE,
    Route,
    route_population_drive,
)
from neurofly.relative_column_sensory_dynamics import (
    INITIAL_STATE,
    INPUT_METRIC_COLUMN_OVERLAP,
    RECOVERY_TAIL_STEPS,
    REFERENCE_GAIN,
    REFERENCE_TAU_SENS_MS,
    SENSORY_STATE_CLASSIFICATION,
    integrate_exposure_values,
)
from neurofly.simulation import (
    PHASE7F_READOUT_SCOPE_ID,
    ExternalDriveSchedule,
    LIFConfig,
    LIFSimulator,
    SimulationGraph,
)

SAMPLE_CONFIG_SCHEMA = "bounded_sensory_sample_config_v1"
SAMPLE_RESULT_SCHEMA = "bounded_sensory_sample_result_v1"
SAMPLE_ARTIFACT_SCHEMA = "bounded_sensory_sample_artifact_v1"
EXPERIMENT_CONFIG_SCHEMA = "bounded_sensory_population_config_v1"
EXPERIMENT_RESULT_SCHEMA = "bounded_sensory_population_result_v1"
EXPERIMENT_ARTIFACT_SCHEMA = "bounded_sensory_population_artifact_v1"
SELECTION_METHOD_ID = "rank_tertile_centroid_maximin_v1"
SENSORY_MODEL_ID = "relative_column_exploratory_sensory_state_v1"
TRANSFER_MODEL_ID = "exploratory_edge_routed_model_drive_v1"
EXPERIMENT_ID = "phase7h_bounded_16_body_relative_column_sensory_to_dnp01_v1"
SAMPLE_SIZE = 16
STRATA = (("LC4", "L"), ("LC4", "R"), ("LPLC2", "L"), ("LPLC2", "R"))
SENTINELS = {
    ("LC4", "L"): 12032,
    ("LC4", "R"): 16128,
    ("LPLC2", "L"): 11498,
    ("LPLC2", "R"): 14465,
}
TARGET_BY_SIDE = {"R": 10001, "L": 10010}
TARGET_IDENTITIES = (
    {"body_id": 10001, "neuron_type": "DNp01", "side": "R"},
    {"body_id": 10010, "neuron_type": "DNp01", "side": "L"},
)
REFERENCE_STIMULUS_IDS = (
    "left_expand_33_29",
    "left_lplc2_11498_18_04",
    "right_expand_23_09",
    "right_translate_23_11",
)
K_SENSITIVITY = (0.0, 0.5, 1.0, 2.0)
DEFAULT_SAMPLE_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_sample_v1"
DEFAULT_EXPERIMENT_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_population_v1"


class BoundedPopulationError(ValueError):
    """Invalid source, sample, stimulus, or population-experiment identity."""


def _body_index(
    source: RelativeColumnAssignmentSource, circuit: CircuitContract
) -> tuple[dict[int, dict[str, Any]], dict[int, tuple[Any, ...]]]:
    if (
        source.contract.schema_version != "body_column_input_v1"
        or source.contract.dataset != "male-cns:v1.0"
        or source.contract.candidate_identifier != "looming_giant_fiber_v1"
        or source.contract.candidate_version != 1
        or dict(source.source_identity.get("source_file_sha256", {}))
        != EXPECTED_COLUMN_FILE_HASHES
        or dict(circuit.integrity.sha256_by_file) != EXPECTED_CIRCUIT_FILE_HASHES
        or circuit.provenance.dataset != "male-cns:v1.0"
        or circuit.candidate.identifier != "looming_giant_fiber_v1"
        or circuit.candidate.version != 1
    ):
        raise BoundedPopulationError("source contract identity/hash is not pinned.")

    summaries = {item.body_id: item for item in source.contract.summaries}
    records_by_body: dict[int, list[Any]] = defaultdict(list)
    for record in source.contract.records:
        records_by_body[record.body_id].append(record)

    sensory_nodes = [node for node in circuit.neurons if node.type in {"LC4", "LPLC2"}]
    if len(sensory_nodes) != 311:
        raise BoundedPopulationError(
            "CircuitContract must contain exactly 311 sensory bodies."
        )
    if (
        sum(node.type == "LC4" for node in sensory_nodes) != 126
        or sum(node.type == "LPLC2" for node in sensory_nodes) != 185
    ):
        raise BoundedPopulationError("CircuitContract sensory type counts changed.")
    sensory_body_ids = {node.body_id for node in sensory_nodes}
    if set(summaries) != sensory_body_ids or set(records_by_body) != sensory_body_ids:
        raise BoundedPopulationError(
            "body-column source identities do not exactly match the sensory circuit."
        )

    edge_by_source: dict[int, list[Any]] = defaultdict(list)
    for edge in circuit.connections:
        if edge.source_type in {"LC4", "LPLC2"} and edge.target_type == "DNp01":
            edge_by_source[edge.source_body_id].append(edge)

    result: dict[int, dict[str, Any]] = {}
    records_result: dict[int, tuple[Any, ...]] = {}
    for node in sensory_nodes:
        body_id = node.body_id
        summary = summaries.get(body_id)
        records = tuple(sorted(records_by_body.get(body_id, ())))
        edges = edge_by_source.get(body_id, [])
        if summary is None or not records:
            raise BoundedPopulationError(f"missing body-column source for {body_id}.")
        if (summary.neuron_type, summary.eye_side) != (node.type, node.soma_side):
            raise BoundedPopulationError(
                f"body-column identity mismatch for {body_id}."
            )
        if any(
            record.neuron_type != node.type
            or record.eye_side != node.soma_side
            or record.input_count <= 0
            for record in records
        ):
            raise BoundedPopulationError(f"malformed column records for {body_id}.")
        if (
            sum(record.input_count for record in records)
            != summary.assigned_input_count
        ):
            raise BoundedPopulationError(
                f"assigned source count mismatch for {body_id}."
            )
        if summary.assigned_input_count <= 0:
            raise BoundedPopulationError(f"zero source-site denominator for {body_id}.")
        if len(edges) != 1:
            raise BoundedPopulationError(
                f"body {body_id} must have exactly one direct DNp01 route."
            )
        edge = edges[0]
        target = circuit.neurons_by_body_id.get(edge.target_body_id)
        if (
            target is None
            or target.type != "DNp01"
            or target.soma_side != node.soma_side
            or edge.dataset != "male-cns:v1.0"
            or edge.structural_weight <= 0
        ):
            raise BoundedPopulationError(f"invalid direct route for body {body_id}.")
        result[body_id] = {
            "body_id": body_id,
            "neuron_type": node.type,
            "side": node.soma_side,
            "target_body_id": edge.target_body_id,
            "structural_weight": edge.structural_weight,
            "source_column_record_count": len(records),
            "source_unique_hex_count": len(
                {(item.ol_hex1, item.ol_hex2) for item in records}
            ),
            "assigned_input_sites": summary.assigned_input_count,
            "relevant_input_sites": summary.relevant_input_count,
            "unassigned_input_sites": summary.unassigned_input_count,
            "source_coverage_fraction": summary.assignment_fraction,
            "anatomical_column_centroid": _unweighted_record_centroid(records),
            "structural_weight_semantics": "MALECNS_SOURCE_STRUCTURAL_COUNT_ONLY",
        }
        records_result[body_id] = records

    if len(edge_by_source) != 311 or set(edge_by_source) != set(result):
        raise BoundedPopulationError(
            "sensory-to-DNp01 connectivity differs from the pinned 311-route audit."
        )
    return result, {body: tuple(records) for body, records in records_result.items()}


def _unweighted_record_centroid(records: Sequence[Any]) -> list[float]:
    """Phase 7C record-wise centroid; not a functional receptive-field centre."""
    if not records:
        raise BoundedPopulationError("cannot summarize an empty source-column set.")
    return [
        sum(record.ol_hex1 for record in records) / len(records),
        sum(record.ol_hex2 for record in records) / len(records),
    ]


def _hex_centroid_distance(first: Sequence[float], second: Sequence[float]) -> float:
    """Continuous extension of the validated axial hex norm for centroids."""
    delta_q = first[0] - second[0]
    delta_p = first[1] - second[1]
    return max(abs(delta_p), abs(delta_q), abs(delta_p - delta_q))


def _stratum_rank_bands(
    candidates: Sequence[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    """Partition sorted candidate ranks into balanced low/middle/high bands."""
    ordered = sorted(
        candidates,
        key=lambda item: (item["structural_weight"], item["body_id"]),
    )
    count = len(ordered)
    bands: dict[int, dict[str, Any]] = {}
    for rank, item in enumerate(ordered):
        band_index = min(2, (rank * 3) // count)
        bands[item["body_id"]] = {
            "rank": rank,
            "band_index": band_index,
            "band_id": ("low", "middle", "high")[band_index],
        }
    return bands


def _maximin_candidate(
    candidates: Sequence[dict[str, Any]],
    prior_selected: Sequence[dict[str, Any]],
) -> tuple[dict[str, Any], float]:
    """Choose the most separated candidate, breaking exact ties by body ID."""

    if not candidates or not prior_selected:
        raise BoundedPopulationError(
            "maximin selection requires candidates and prior stratum members."
        )
    scored = []
    for candidate in candidates:
        centroid = tuple(candidate["anatomical_column_centroid"])
        minimum_distance = min(
            _hex_centroid_distance(centroid, prior["anatomical_column_centroid"])
            for prior in prior_selected
        )
        scored.append((minimum_distance, candidate["body_id"], candidate))
    max_distance = max(item[0] for item in scored)
    _, _, chosen = min(
        (item for item in scored if item[0] == max_distance),
        key=lambda item: item[1],
    )
    return chosen, max_distance


def select_bounded_sample(
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Select exact 4×4 sample from anatomy and structural descriptors only."""
    if circuit.provenance.dataset != "male-cns:v1.0":
        raise BoundedPopulationError("sample selection requires male-cns:v1.0.")
    body_rows, _ = _body_index(source, circuit)
    selected: list[dict[str, Any]] = []
    for neuron_type, side in STRATA:
        sentinel_id = SENTINELS[(neuron_type, side)]
        candidates = [
            row
            for row in body_rows.values()
            if row["neuron_type"] == neuron_type
            and row["side"] == side
            and row["body_id"] != sentinel_id
        ]
        if sentinel_id not in body_rows or len(candidates) < 3:
            raise BoundedPopulationError(f"stratum {neuron_type}/{side} is incomplete.")
        sentinel = dict(body_rows[sentinel_id])
        if (sentinel["neuron_type"], sentinel["side"]) != (neuron_type, side):
            raise BoundedPopulationError(
                "sentinel identity does not match its stratum."
            )
        sentinel.update(
            {
                "selection_band": "sentinel",
                "selection_rank": None,
                "rank_within_band": None,
                "minimum_centroid_distance_to_prior_selection": None,
                "sentinel": True,
            }
        )
        stratum_selected = [sentinel]
        bands = _stratum_rank_bands(candidates)
        for band_index, band_id in enumerate(("low", "middle", "high")):
            band_candidates = [
                item
                for item in candidates
                if bands[item["body_id"]]["band_index"] == band_index
            ]
            if not band_candidates:
                raise BoundedPopulationError(
                    f"rank-based structural band {band_id} is empty."
                )
            chosen, max_distance = _maximin_candidate(band_candidates, stratum_selected)
            chosen_id = chosen["body_id"]
            selection_metadata = bands[chosen_id]
            band_rank = sum(
                1
                for item in band_candidates
                if bands[item["body_id"]]["rank"] < selection_metadata["rank"]
            )
            selected_row = dict(chosen)
            selected_row.update(
                {
                    "selection_band": band_id,
                    "selection_rank": selection_metadata["rank"],
                    "rank_within_band": band_rank,
                    "minimum_centroid_distance_to_prior_selection": max_distance,
                    "sentinel": False,
                }
            )
            stratum_selected.append(selected_row)
        if len(stratum_selected) != 4:
            raise BoundedPopulationError(
                "each type/side stratum must select four bodies."
            )
        selected.extend(stratum_selected)

    body_ids = [item["body_id"] for item in selected]
    if len(body_ids) != SAMPLE_SIZE or len(set(body_ids)) != SAMPLE_SIZE:
        raise BoundedPopulationError("sample must contain exactly 16 unique bodies.")
    config = {
        "schema": SAMPLE_CONFIG_SCHEMA,
        "sample_id": "phase7h_bounded_16_body_sample_v1",
        "selection_method_id": SELECTION_METHOD_ID,
        "sample_size": SAMPLE_SIZE,
        "strata": [
            {"neuron_type": neuron_type, "side": side, "count": 4}
            for neuron_type, side in STRATA
        ],
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": {
            "dataset": circuit.provenance.dataset,
            "candidate_id": circuit.candidate.identifier,
            "candidate_version": circuit.candidate.version,
            "file_sha256": dict(circuit.integrity.sha256_by_file),
        },
        "selection_inputs": [
            "type",
            "side",
            "body_id",
            "body_column_records",
            "relative_column_centroid",
            "direct_DNp01_structural_count",
        ],
        "selection_excludes_model_outcomes": True,
        "structural_count_semantics": "DESCRIPTIVE_SELECTION_STRATIFIER_ONLY",
        "centroid_semantics": "UNWEIGHTED_BODY_COLUMN_RECORD_CENTROID_HEX_SPACE",
        "method": {
            "candidate_order": "structural_weight_then_body_id",
            "rank_partition": "balanced_three_rank_bands_floor(rank*3/candidate_count)",
            "band_order": ["low", "middle", "high"],
            "within_band_choice": "maximize_minimum_hex_centroid_distance",
            "tie_break": "smallest_body_id",
            "sentinel_preselected": True,
        },
    }
    result = {
        "schema": SAMPLE_RESULT_SCHEMA,
        "sample_id": config["sample_id"],
        "sample_size": SAMPLE_SIZE,
        "body_ids": body_ids,
        "selected_bodies": selected,
        "stratum_counts": [
            {
                "neuron_type": neuron_type,
                "side": side,
                "count": sum(
                    item["neuron_type"] == neuron_type and item["side"] == side
                    for item in selected
                ),
            }
            for neuron_type, side in STRATA
        ],
        "selection_semantics": "PRE_OUTCOME_ANATOMICAL_AND_STRUCTURAL_SAMPLE",
        "model_outcomes_used": False,
    }
    return config, result


def _stimulus_battery(
    sample_result: Mapping[str, Any],
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
) -> tuple[RelativeColumnStimulus, ...]:
    existing = fixed_stimuli()
    records_by_body: dict[int, list[Any]] = defaultdict(list)
    for record in source.contract.records:
        records_by_body[record.body_id].append(record)
    added = []
    for side in ("L", "R"):
        side_sample = [
            item for item in sample_result["selected_bodies"] if item["side"] == side
        ]
        centroid = (
            sum(item["anatomical_column_centroid"][0] for item in side_sample)
            / len(side_sample),
            sum(item["anatomical_column_centroid"][1] for item in side_sample)
            / len(side_sample),
        )
        occupied = sorted(
            {
                (record.ol_hex1, record.ol_hex2)
                for item in side_sample
                for record in records_by_body[item["body_id"]]
            }
        )
        if not occupied:
            raise BoundedPopulationError("selected side has no source columns.")
        center = min(
            occupied,
            key=lambda coordinate: (
                _hex_centroid_distance(centroid, coordinate),
                coordinate[0],
                coordinate[1],
            ),
        )
        if center not in grid.columns_by_side[side]:
            raise BoundedPopulationError(
                "derived stimulus centre is not a known column."
            )
        added.append(
            RelativeColumnStimulus(
                stimulus_id=f"sample_{side.lower()}_centroid_expand",
                side=side,
                centre_hex1=center[0],
                centre_hex2=center[1],
                dt_ms=0.1,
                radii_lattice_steps=(1, 2, 3, 4),
            )
        )
    return (*existing, *added)


def _route_set(
    sample_result: Mapping[str, Any], circuit: CircuitContract
) -> tuple[Route, ...]:
    rows, _ = _body_index_from_contract_only(circuit)
    routes = []
    selected_ids = set(sample_result["body_ids"])
    for row in sample_result["selected_bodies"]:
        current = rows.get(row["body_id"])
        if current is None or any(
            current[key] != row[key]
            for key in ("neuron_type", "side", "target_body_id", "structural_weight")
        ):
            raise BoundedPopulationError(
                "sample route identity differs from CircuitContract."
            )
        routes.append(
            Route(
                source_body_id=row["body_id"],
                target_body_id=row["target_body_id"],
                structural_weight=row["structural_weight"],
                source_type=row["neuron_type"],
                side=row["side"],
            )
        )
    if {item.source_body_id for item in routes} != selected_ids or len(routes) != 16:
        raise BoundedPopulationError("all 16 selected bodies need one route.")
    if any(
        route.side != ("R" if route.target_body_id == 10001 else "L")
        for route in routes
    ):
        raise BoundedPopulationError("a selected route crosses DNp01 sides.")
    return tuple(sorted(routes, key=lambda item: item.source_body_id))


def _body_index_from_contract_only(
    circuit: CircuitContract,
) -> tuple[dict[int, dict[str, Any]], tuple[Any, ...]]:
    """Validate source route facts without using outcome/model data."""
    if (
        circuit.provenance.dataset != "male-cns:v1.0"
        or circuit.candidate.dataset != "male-cns:v1.0"
        or circuit.candidate.identifier != "looming_giant_fiber_v1"
        or circuit.candidate.version != 1
        or dict(circuit.integrity.sha256_by_file) != EXPECTED_CIRCUIT_FILE_HASHES
    ):
        raise BoundedPopulationError(
            "CircuitContract source identity/hash is not pinned."
        )

    rows: dict[int, dict[str, Any]] = {}
    sensory = {
        node.body_id: node for node in circuit.neurons if node.type in {"LC4", "LPLC2"}
    }
    by_source: dict[int, list[Any]] = defaultdict(list)
    for edge in circuit.connections:
        if edge.source_body_id in sensory and edge.target_type == "DNp01":
            by_source[edge.source_body_id].append(edge)
    for body_id, node in sensory.items():
        edges = by_source.get(body_id, ())
        if len(edges) != 1:
            raise BoundedPopulationError(
                f"body {body_id} lacks exactly one direct DNp01 route."
            )
        edge = edges[0]
        target = circuit.neurons_by_body_id[edge.target_body_id]
        if (
            edge.dataset != "male-cns:v1.0"
            or edge.source_type != node.type
            or edge.target_type != "DNp01"
            or target.soma_side != node.soma_side
            or target.type != "DNp01"
            or isinstance(edge.structural_weight, bool)
            or not isinstance(edge.structural_weight, int)
            or edge.structural_weight <= 0
        ):
            raise BoundedPopulationError(
                f"source route side/type mismatch for {body_id}."
            )
        rows[body_id] = {
            "body_id": body_id,
            "neuron_type": node.type,
            "side": node.soma_side,
            "target_body_id": edge.target_body_id,
            "structural_weight": edge.structural_weight,
        }
    if len(rows) != 311 or len(by_source) != 311:
        raise BoundedPopulationError("CircuitContract sensory routing is not 311-to-2.")
    return rows, tuple(sensory.values())


def _assignment_result(
    sample_result: Mapping[str, Any],
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    stimuli: Sequence[RelativeColumnStimulus],
) -> dict[str, Any]:
    records_by_body: dict[int, list[Any]] = defaultdict(list)
    summaries = {item.body_id: item for item in source.contract.summaries}
    for record in source.contract.records:
        records_by_body[record.body_id].append(record)
    samples: list[dict[str, Any]] = []
    for stimulus in stimuli:
        for offset, radius in enumerate(stimulus.radii_lattice_steps):
            step = stimulus.start_step + offset
            active = active_column_set(stimulus, grid, radius)
            active_set = frozenset(active)
            assignments = [
                compute_body_exposure(
                    tuple(sorted(records_by_body[body["body_id"]])),
                    summaries[body["body_id"]],
                    stimulus,
                    active_set,
                )
                for body in sample_result["selected_bodies"]
            ]
            samples.append(
                {
                    "stimulus_id": stimulus.stimulus_id,
                    "side": stimulus.side,
                    "step": step,
                    "time_ms": step * stimulus.dt_ms,
                    "dt_ms": stimulus.dt_ms,
                    "radius_lattice_steps": radius,
                    "active_column_count": len(active),
                    "active_column_set_sha256": sha256_bytes(
                        canonical_json_bytes([list(item) for item in active])
                    ),
                    "active_columns": [list(item) for item in active],
                    "assignments": assignments,
                }
            )
    return {
        "schema": "relative_column_population_assignment_result_v1",
        "semantics": "ANATOMICAL_EXPOSURE_ONLY",
        "body_ids": list(sample_result["body_ids"]),
        "sample_count": len(samples),
        "samples": samples,
        "limitations": {
            "absolute_visual_angle_present": False,
            "functional_receptive_field_present": False,
            "neural_dynamics_present": False,
            "structural_input_site_count_is_physiological_weight": False,
        },
    }


def _sensory_trajectories(
    assignment: Mapping[str, Any],
    sample_result: Mapping[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for sample in assignment["samples"]:
        grouped[sample["stimulus_id"]].append(sample)
    output: dict[str, list[dict[str, Any]]] = {}
    for stimulus_id, samples in grouped.items():
        samples.sort(key=lambda item: item["step"])
        if [item["step"] for item in samples] != list(range(len(samples))):
            raise BoundedPopulationError(
                "assignment timeline steps are not contiguous."
            )
        dt_values = {item["dt_ms"] for item in samples}
        if len(dt_values) != 1:
            raise BoundedPopulationError("assignment dt changes within a stimulus.")
        dt_ms = float(samples[0]["dt_ms"])
        trajectories = []
        for identity in sample_result["selected_bodies"]:
            exposures = []
            for sample in samples:
                assignment_row = next(
                    item
                    for item in sample["assignments"]
                    if item["body_id"] == identity["body_id"]
                )
                exposure = float(assignment_row[INPUT_METRIC_COLUMN_OVERLAP])
                if not math.isfinite(exposure) or not 0.0 <= exposure <= 1.0:
                    raise BoundedPopulationError("anatomical exposure is invalid.")
                exposures.append(exposure)
            timeline = integrate_exposure_values(
                exposures,
                dt_ms=dt_ms,
                tau_sens_ms=REFERENCE_TAU_SENS_MS,
                gain=REFERENCE_GAIN,
                recovery_tail_steps=RECOVERY_TAIL_STEPS,
            )
            peak_idx = max(
                range(len(timeline)), key=lambda idx: timeline[idx]["state_value"]
            )
            peak_exposure_idx = max(range(len(exposures)), key=exposures.__getitem__)
            trajectories.append(
                {
                    "body_id": identity["body_id"],
                    "neuron_type": identity["neuron_type"],
                    "side": identity["side"],
                    "input_metric_id": INPUT_METRIC_COLUMN_OVERLAP,
                    "shared_parameter_set_id": "phase7e_reference_assumptions_v1",
                    "parameter_classification": SENSORY_STATE_CLASSIFICATION,
                    "peak_exposure": exposures[peak_exposure_idx],
                    "peak_exposure_assignment_step": samples[peak_exposure_idx]["step"],
                    "peak_exploratory_state": timeline[peak_idx]["state_value"],
                    "peak_state_step": timeline[peak_idx]["state_step"],
                    "peak_state_time_ms": timeline[peak_idx]["time_ms"],
                    "state_timeline": list(timeline),
                    "state_semantics": "EXPLORATORY_DIMENSIONLESS_SENSORY_MODEL_STATE",
                }
            )
        output[stimulus_id] = trajectories
    return output


def _validate_sensory_reference(
    trajectories: Mapping[str, Sequence[Mapping[str, Any]]],
    baseline_sensory: Any,
) -> dict[str, Any]:
    conditions = {
        item["stimulus_id"]: item for item in baseline_sensory.result["conditions"]
    }
    regressions = []
    for stimulus_id in REFERENCE_STIMULUS_IDS:
        if stimulus_id not in conditions or stimulus_id not in trajectories:
            raise BoundedPopulationError(
                "sentinel stimulus missing from 7E comparison."
            )
        baseline = {
            item["body_id"]: item
            for item in conditions[stimulus_id]["body_trajectories"]
        }
        current = {item["body_id"]: item for item in trajectories[stimulus_id]}
        for sentinel_id in SENTINELS.values():
            old_trace = baseline[sentinel_id]["state_timeline"]
            new_trace = current[sentinel_id]["state_timeline"]
            if old_trace != new_trace:
                raise BoundedPopulationError(
                    "Phase 7E sentinel trajectory changed for "
                    f"{sentinel_id}/{stimulus_id}."
                )
            regressions.append(
                {
                    "body_id": sentinel_id,
                    "stimulus_id": stimulus_id,
                    "state_timeline_identical": True,
                }
            )
    return {
        "all_reference_sentinel_state_traces_identical": True,
        "comparisons": regressions,
    }


def _condition_states(
    trajectories: Mapping[str, Sequence[Mapping[str, Any]]],
    sample_result: Mapping[str, Any],
    left_stimulus_id: str,
    right_stimulus_id: str,
) -> tuple[dict[int, list[float]], float, int]:
    by_stimulus = {
        stimulus_id: {item["body_id"]: item for item in values}
        for stimulus_id, values in trajectories.items()
    }
    if left_stimulus_id not in by_stimulus or right_stimulus_id not in by_stimulus:
        raise BoundedPopulationError("bilateral condition references missing stimulus.")
    left = by_stimulus[left_stimulus_id]
    right = by_stimulus[right_stimulus_id]
    dt_left = left[next(iter(left))]["state_timeline"][1]["time_ms"]
    dt_right = right[next(iter(right))]["state_timeline"][1]["time_ms"]
    if dt_left != dt_right:
        raise BoundedPopulationError("bilateral sensory timelines use different dt.")
    max_intervals = max(
        len(left[next(iter(left))]["state_timeline"]) - 1,
        len(right[next(iter(right))]["state_timeline"]) - 1,
    )
    states: dict[int, list[float]] = {}
    for body in sample_result["selected_bodies"]:
        trajectory = (
            left[body["body_id"]] if body["side"] == "L" else right[body["body_id"]]
        )
        values = [row["state_value"] for row in trajectory["state_timeline"]]
        states[body["body_id"]] = values + [0.0] * (max_intervals + 1 - len(values))
    return states, float(dt_left), max_intervals


def _simulate_condition(
    *,
    condition_id: str,
    pathway_mask: str,
    active_body_ids: set[int],
    k: float,
    states: Mapping[int, Sequence[float]],
    dt_ms: float,
    steps: int,
    routes: Sequence[Route],
    circuit: CircuitContract,
) -> dict[str, Any]:
    if pathway_mask not in {
        "all16",
        "none",
        "LC4",
        "LPLC2",
        "left",
        "right",
        "sentinels",
    }:
        raise BoundedPopulationError("unsupported Phase 7H source mask.")
    if not math.isfinite(k) or k < 0:
        raise BoundedPopulationError(
            "transfer coefficient must be finite and nonnegative."
        )
    active_routes = [
        route for route in routes if route.source_body_id in active_body_ids
    ]
    drives = {10001: [], 10010: []}
    contribution_rows = []
    type_drive = {target: {"LC4": [], "LPLC2": []} for target in drives}
    for step in range(steps):
        values = {body_id: float(trace[step]) for body_id, trace in states.items()}
        summed, contributions = route_population_drive(
            values,
            routes,
            target_body_ids=(10001, 10010),
            active_source_ids=active_body_ids,
            k_transfer_mveq_per_state=k,
        )
        for target in drives:
            drives[target].append(summed[target])
            for neuron_type in ("LC4", "LPLC2"):
                type_drive[target][neuron_type].append(
                    sum(
                        row["model_drive_mveq"]
                        for row, route in zip(contributions, routes, strict=True)
                        if route.target_body_id == target
                        and route.source_type == neuron_type
                    )
                )
        contribution_rows.append(
            {
                "step": step,
                "time_ms": step * dt_ms,
                "contributions": contributions,
            }
        )
        for target in drives:
            recorded = sum(
                row["model_drive_mveq"]
                for row in contributions
                if row["target_body_id"] == target
            )
            if not math.isclose(recorded, summed[target], rel_tol=0.0, abs_tol=1e-15):
                raise BoundedPopulationError("source contributions do not sum exactly.")

    graph = SimulationGraph(
        candidate_identifier=circuit.candidate.identifier,
        candidate_version=circuit.candidate.version,
        dataset=circuit.provenance.dataset,
        graph_scope_id=PHASE7F_READOUT_SCOPE_ID,
        nodes=(circuit.neurons_by_body_id[10001], circuit.neurons_by_body_id[10010]),
        edges=(),
        circuit_integrity=tuple(circuit.integrity.sha256_by_file),
    )
    lif_config = _reference_lif_config(dt_ms)
    simulator = LIFSimulator(graph, lif_config)
    schedule = ExternalDriveSchedule.from_body_ids(
        drives, steps=steps, provenance_id=DRIVE_PROVENANCE_ID
    )
    simulation = simulator.run(
        schedule,
        record_body_ids=(10001, 10010),
        allow_model_readout_drive=True,
    )
    targets = []
    for index, body_id in enumerate(simulation.body_ids):
        drive_series = drives[body_id]
        peak_index = max(range(len(drive_series)), key=drive_series.__getitem__)
        targets.append(
            {
                "body_id": body_id,
                "side": "R" if body_id == 10001 else "L",
                "contributing_source_body_ids": [
                    route.source_body_id
                    for route in active_routes
                    if route.target_body_id == body_id
                ],
                "drive_mveq_by_interval": drive_series,
                "peak_drive_mveq": drive_series[peak_index],
                "peak_drive_step": peak_index,
                "peak_drive_time_ms": peak_index * dt_ms,
                "lc4_model_contribution_by_interval": type_drive[body_id]["LC4"],
                "lplc2_model_contribution_by_interval": type_drive[body_id]["LPLC2"],
                "minimum_membrane_mv": float(simulation.membrane_mv[:, index].min()),
                "maximum_membrane_mv": float(simulation.membrane_mv[:, index].max()),
                "membrane_mv_by_boundary": simulation.membrane_mv[:, index].tolist(),
                "filtered_synaptic_mveq_by_boundary": simulation.synaptic_mveq[
                    :, index
                ].tolist(),
                "simulated_spikes": [
                    {
                        "body_id": spike.body_id,
                        "step": spike.step,
                        "time_ms": spike.time_ms,
                        "semantics": "SIMULATED_DNP01_MODEL_SPIKE",
                    }
                    for spike in simulation.spikes
                    if spike.body_id == body_id
                ],
            }
        )
    return {
        "condition_id": condition_id,
        "pathway_mask": pathway_mask,
        "active_source_body_ids": sorted(active_body_ids),
        "k_transfer_mveq_per_state": k,
        "dt_ms": dt_ms,
        "interval_count": steps,
        "time_alignment": "sensory_state_boundary_n_drives_interval_n_to_n_plus_1",
        "source_contributions_by_interval": contribution_rows,
        "targets": targets,
    }


def _reference_lif_config(dt_ms: float) -> LIFConfig:
    """Phase 7F readout configuration, unchanged for the larger sample."""
    return LIFConfig(
        k_syn_mv_per_contact=0.01,
        dt_ms=dt_ms,
        graph_scope_id=PHASE7F_READOUT_SCOPE_ID,
        input_drive_provenance_id=DRIVE_PROVENANCE_ID,
    )


def _mask_ids(sample_result: Mapping[str, Any], mask: str) -> set[int]:
    bodies = sample_result["selected_bodies"]
    if mask == "none":
        return set()
    if mask == "all16":
        return {item["body_id"] for item in bodies}
    if mask == "sentinels":
        return set(SENTINELS.values())
    if mask in {"LC4", "LPLC2"}:
        return {item["body_id"] for item in bodies if item["neuron_type"] == mask}
    if mask in {"left", "right"}:
        side = "L" if mask == "left" else "R"
        return {item["body_id"] for item in bodies if item["side"] == side}
    raise BoundedPopulationError("unsupported body mask.")


def _condition_summary(condition: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "condition_id": condition["condition_id"],
        "pathway_mask": condition["pathway_mask"],
        "k_transfer_mveq_per_state": condition["k_transfer_mveq_per_state"],
        "targets": [
            {
                "body_id": target["body_id"],
                "peak_drive_mveq": target["peak_drive_mveq"],
                "minimum_membrane_mv": target["minimum_membrane_mv"],
                "maximum_membrane_mv": target["maximum_membrane_mv"],
                "spike_count": len(target["simulated_spikes"]),
            }
            for target in condition["targets"]
        ],
    }


def compute_population_experiment(
    sample_artifact: Mapping[str, Any],
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    circuit: CircuitContract,
    baseline_sensory: Any,
    baseline_transfer: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Derive assignment, 16 exploratory states, and routed DNp01 readout."""
    sample_config = sample_artifact["config"]
    sample_result = sample_artifact["result"]
    expected_config, expected_result = select_bounded_sample(source, circuit)
    if sample_config != expected_config or sample_result != expected_result:
        raise BoundedPopulationError(
            "sample artifact does not replay from pinned sources."
        )

    stimuli = _stimulus_battery(sample_result, source, grid)
    stimulus_dicts = [stimulus.to_dict() for stimulus in stimuli]
    assignment = _assignment_result(sample_result, source, grid, stimuli)
    sensory = _sensory_trajectories(assignment, sample_result)
    sentinel_regression = _validate_sensory_reference(sensory, baseline_sensory)
    routes = _route_set(sample_result, circuit)

    left_id, right_id = "left_expand_33_29", "right_expand_23_09"
    states, dt_ms, steps = _condition_states(sensory, sample_result, left_id, right_id)
    sample_states, sample_dt_ms, sample_steps = _condition_states(
        sensory,
        sample_result,
        "sample_l_centroid_expand",
        "sample_r_centroid_expand",
    )
    if (sample_dt_ms, sample_steps) != (dt_ms, steps):
        raise BoundedPopulationError("stimulus comparison grids must match exactly.")
    masks = (
        ("all16_reference", "all16", REFERENCE_K_MVEQ_PER_STATE),
        ("k_zero", "all16", 0.0),
        ("no_sources", "none", REFERENCE_K_MVEQ_PER_STATE),
        ("lc4_only", "LC4", REFERENCE_K_MVEQ_PER_STATE),
        ("lplc2_only", "LPLC2", REFERENCE_K_MVEQ_PER_STATE),
        ("left_only", "left", REFERENCE_K_MVEQ_PER_STATE),
        ("right_only", "right", REFERENCE_K_MVEQ_PER_STATE),
        ("sentinels_only", "sentinels", REFERENCE_K_MVEQ_PER_STATE),
        ("sensitivity_k_0_5", "all16", 0.5),
        ("sensitivity_k_2", "all16", 2.0),
    )
    conditions = [
        _simulate_condition(
            condition_id=name,
            pathway_mask=mask,
            active_body_ids=_mask_ids(sample_result, mask),
            k=k,
            states=states,
            dt_ms=dt_ms,
            steps=steps,
            routes=routes,
            circuit=circuit,
        )
        for name, mask, k in masks
    ]
    sample_masks = (
        ("sample_centroid_all16", "all16"),
        ("sample_centroid_sentinels_only", "sentinels"),
    )
    conditions.extend(
        _simulate_condition(
            condition_id=name,
            pathway_mask=mask,
            active_body_ids=_mask_ids(sample_result, mask),
            k=REFERENCE_K_MVEQ_PER_STATE,
            states=sample_states,
            dt_ms=sample_dt_ms,
            steps=sample_steps,
            routes=routes,
            circuit=circuit,
        )
        for name, mask in sample_masks
    )
    compare_sentinel_transfer = _compare_with_phase7f_sentinels(
        conditions, baseline_transfer
    )
    reference_condition = next(
        item for item in conditions if item["condition_id"] == "all16_reference"
    )
    sentinel_condition = next(
        item for item in conditions if item["condition_id"] == "sentinels_only"
    )
    sample_centroid_condition = next(
        item for item in conditions if item["condition_id"] == "sample_centroid_all16"
    )
    sample_centroid_sentinels = next(
        item
        for item in conditions
        if item["condition_id"] == "sample_centroid_sentinels_only"
    )
    sentinel_ids = set(SENTINELS.values())
    all_sample_ids = set(sample_result["body_ids"])
    comparison = {
        "comparison_semantics": "ARCHITECTURE_SCALE_ONLY_NOT_BIOLOGICAL_REALISM",
        "stimulus_comparisons": [
            {
                "stimulus_condition": "reference_bilateral_expansion",
                "four_body_sentinel": _condition_scale_summary(
                    _source_state_summary(states, sample_result, sentinel_ids, steps),
                    sentinel_condition,
                    active_count=4,
                ),
                "sixteen_body": _condition_scale_summary(
                    _source_state_summary(states, sample_result, all_sample_ids, steps),
                    reference_condition,
                    active_count=16,
                ),
            },
            {
                "stimulus_condition": "sample_centroid_bilateral_expansion",
                "four_body_sentinel": _condition_scale_summary(
                    _source_state_summary(
                        sample_states,
                        sample_result,
                        sentinel_ids,
                        sample_steps,
                    ),
                    sample_centroid_sentinels,
                    active_count=4,
                ),
                "sixteen_body": _condition_scale_summary(
                    _source_state_summary(
                        sample_states,
                        sample_result,
                        all_sample_ids,
                        sample_steps,
                    ),
                    sample_centroid_condition,
                    active_count=16,
                ),
            },
        ],
    }
    config = {
        "schema": EXPERIMENT_CONFIG_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "sample_artifact": {
            "artifact_schema": SAMPLE_ARTIFACT_SCHEMA,
            "artifact_id": sample_artifact["artifact_id"],
            "manifest_sha256": sample_artifact["manifest_sha256"],
            "config_sha256": sample_artifact["config_sha256"],
            "result_sha256": sample_artifact["result_sha256"],
        },
        "source_contract_identity": dict(source.source_identity),
        "column_grid_identity": grid.to_identity_dict(),
        "circuit_contract_identity": {
            "dataset": circuit.provenance.dataset,
            "candidate_id": circuit.candidate.identifier,
            "candidate_version": circuit.candidate.version,
            "file_sha256": dict(circuit.integrity.sha256_by_file),
        },
        "stimulus_model_id": "relative_column_expanding_disk_v1",
        "stimulus_selection_method": (
            "side_sample_mean_centroid_nearest_occupied_column_v1"
        ),
        "stimuli": [
            {
                "config": item,
                "sha256": sha256_bytes(canonical_json_bytes(item)),
            }
            for item in stimulus_dicts
        ],
        "sensory_model": {
            "model_id": SENSORY_MODEL_ID,
            "model_version": 1,
            "input_metric_id": INPUT_METRIC_COLUMN_OVERLAP,
            "tau_sens_ms": REFERENCE_TAU_SENS_MS,
            "gain": REFERENCE_GAIN,
            "initial_state": INITIAL_STATE,
            "recovery_tail_steps": RECOVERY_TAIL_STEPS,
            "integration_scheme": "exact_exponential_zero_order_hold_v1",
            "classification": "MODEL_ASSUMPTION",
        },
        "transfer_model": {
            "model_id": TRANSFER_MODEL_ID,
            "equation": (
                "d_i[n]=k_transfer*x_i[n]; target=sum_routed_source_contributions"
            ),
            "k_transfer_mveq_per_state": REFERENCE_K_MVEQ_PER_STATE,
            "classification": "MODEL_ASSUMPTION",
            "structural_weight_used_as_gain": False,
            "source_normalization": "none",
        },
        "dnp01_model": {
            "model_id": _reference_lif_config(dt_ms).model_id,
            "config": _reference_lif_config(dt_ms).to_dict(),
            "configuration_source": "unchanged Phase 7F reference readout model",
        },
        "route_contract": [route.to_dict() for route in routes],
        "condition_ids": [item[0] for item in masks]
        + [item[0] for item in sample_masks],
        "sentinel_reference": {
            "phase7e_artifact_id": baseline_sensory.artifact_id,
            "phase7f_artifact_id": baseline_transfer.artifact_id,
            "state_traces_identical": sentinel_regression[
                "all_reference_sentinel_state_traces_identical"
            ],
            "transfer_reference_comparison": compare_sentinel_transfer,
        },
        "scientific_boundary": {
            "absolute_visual_angle_present": False,
            "functional_rf_claim": False,
            "physiological_calibration": False,
            "structural_counts_are_efficacy": False,
            "behavior_or_body_mechanics": False,
            "dn_p01_is_existing_model_output": True,
        },
    }
    result = {
        "schema": EXPERIMENT_RESULT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "sample_artifact_id": sample_artifact["artifact_id"],
        "body_ids": list(sample_result["body_ids"]),
        "assignment": assignment,
        "sensory_trajectories_by_stimulus": sensory,
        "sentinel_state_regression": sentinel_regression,
        "conditions": conditions,
        "scale_comparison": comparison,
        "result_semantics": "EXPLORATORY_16_BODY_ARCHITECTURE_EXPERIMENT",
    }
    return config, result


def _source_state_summary(
    states: Mapping[int, Sequence[float]],
    sample_result: Mapping[str, Any],
    active_body_ids: set[int],
    steps: int,
) -> dict[str, Any]:
    result = {}
    for side in ("L", "R"):
        ids = [
            item["body_id"]
            for item in sample_result["selected_bodies"]
            if item["side"] == side and item["body_id"] in active_body_ids
        ]
        series = [sum(states[body][step] for body in ids) for step in range(steps)]
        result[side] = {
            "source_body_count": len(ids),
            "peak_total_source_state": max(series, default=0.0),
            "peak_step": max(range(len(series)), key=series.__getitem__)
            if series
            else 0,
            "sum_over_interval_states": sum(series),
        }
    return result


def _condition_scale_summary(
    source_summary: Mapping[str, Any],
    condition: Mapping[str, Any],
    *,
    active_count: int,
) -> dict[str, Any]:
    return {
        "active_sensory_state_count": active_count,
        "total_source_state_by_side": source_summary,
        "targets": [
            {
                "body_id": target["body_id"],
                "peak_transfer_drive_mveq": target["peak_drive_mveq"],
                "maximum_membrane_mv": target["maximum_membrane_mv"],
                "spike_count": len(target["simulated_spikes"]),
                "spikes": target["simulated_spikes"],
            }
            for target in condition["targets"]
        ],
    }


def _compare_with_phase7f_sentinels(
    conditions: Sequence[Mapping[str, Any]], baseline_transfer: Any
) -> dict[str, Any]:
    current = next(
        item for item in conditions if item["condition_id"] == "sentinels_only"
    )
    baseline = next(
        item
        for item in baseline_transfer.result["conditions"]
        if item["condition_id"] == "reference_bilateral_expansion"
    )
    same = []
    current_targets = {item["body_id"]: item for item in current["targets"]}
    baseline_targets = {item["body_id"]: item for item in baseline["targets"]}
    for target_id in TARGET_BY_SIDE.values():
        lhs = current_targets[target_id]
        rhs = baseline_targets[target_id]
        fields = (
            "drive_mveq_by_interval",
            "membrane_mv_by_boundary",
            "filtered_synaptic_mveq_by_boundary",
            "simulated_spikes",
        )
        equal_fields = [field for field in fields if lhs[field] == rhs[field]]
        same.append(
            {
                "target_body_id": target_id,
                "identical_fields": equal_fields,
                "all_numeric_and_event_outputs_identical": len(equal_fields)
                == len(fields),
            }
        )
    if not all(item["all_numeric_and_event_outputs_identical"] for item in same):
        raise BoundedPopulationError("Phase 7F sentinel transfer regression changed.")
    return {"all_targets_identical_to_phase7f": True, "targets": same}


def make_source_bundle(
    source_root: str = str(DEFAULT_SOURCE_ROOT),
    workbook_path: str = str(DEFAULT_WORKBOOK),
) -> tuple[RelativeColumnAssignmentSource, RelativeColumnGrid, CircuitContract]:
    source = load_relative_column_source(source_root)
    grid = load_relative_column_grid(workbook_path, source)
    return source, grid, load_circuit_contract(source_root)
