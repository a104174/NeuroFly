"""Outcome-blind disjoint Sample B robustness experiment for Phase 7J."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from neurofly.bounded_sensory_coverage import (
    MAX_RADIUS_LATTICE_STEPS,
    _artifact_reference,
    _coverage_candidates_for_side,
)
from neurofly.bounded_sensory_coverage_artifacts import (
    DEFAULT_EXPERIMENT_OUTPUT_ROOT as PHASE7I_EXPERIMENT_ROOT,
)
from neurofly.bounded_sensory_coverage_artifacts import (
    DEFAULT_PHASE7H_ARTIFACT_PATH,
    DEFAULT_SAMPLE_ARTIFACT_PATH,
    LoadedCoveragePlan,
    replay_coverage_experiment,
    replay_coverage_plan,
)
from neurofly.bounded_sensory_coverage_artifacts import (
    DEFAULT_PLAN_OUTPUT_ROOT as PHASE7I_PLAN_ROOT,
)
from neurofly.bounded_sensory_population import (
    REFERENCE_STIMULUS_IDS,
    SAMPLE_SIZE,
    STRATA,
    _assignment_result,
    _body_index,
    _condition_states,
    _mask_ids,
    _maximin_candidate,
    _route_set,
    _sensory_trajectories,
    _simulate_condition,
    make_source_bundle,
    select_bounded_sample,
)
from neurofly.bounded_sensory_population_artifacts import (
    LoadedPopulationArtifact,
    LoadedSampleArtifact,
    replay_population_artifact,
    replay_sample_artifact,
)
from neurofly.malecns.contract import CircuitContract
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    RelativeColumnAssignmentSource,
    RelativeColumnGrid,
    RelativeColumnStimulus,
    active_column_set,
    canonical_json_bytes,
    compute_body_exposure,
    sha256_bytes,
)

SAMPLE_CONFIG_SCHEMA = "bounded_independent_sensory_sample_config_v1"
SAMPLE_RESULT_SCHEMA = "bounded_independent_sensory_sample_result_v1"
SAMPLE_ARTIFACT_SCHEMA = "bounded_independent_sensory_sample_artifact_v1"
PLAN_CONFIG_SCHEMA = "bounded_independent_sensory_coverage_plan_config_v1"
PLAN_RESULT_SCHEMA = "bounded_independent_sensory_coverage_plan_result_v1"
PLAN_ARTIFACT_SCHEMA = "bounded_independent_sensory_coverage_plan_artifact_v1"
EXPERIMENT_CONFIG_SCHEMA = "bounded_independent_sensory_population_config_v1"
EXPERIMENT_RESULT_SCHEMA = "bounded_independent_sensory_population_result_v1"
EXPERIMENT_ARTIFACT_SCHEMA = "bounded_independent_sensory_population_artifact_v1"
SELECTION_METHOD_ID = "rank_quartile_sample_a_excluded_centroid_maximin_v1"
PLAN_METHOD_ID = "minimum_source_column_disk_set_cover_sample_b_v1"
EXPERIMENT_ID = "phase7j_disjoint_16_body_sample_b_robustness_v1"
CANONICAL_SAMPLE_A_ID = (
    "18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7"
)
CANONICAL_PHASE7H_ID = (
    "385480b3c915b25536e1119d17effa15567bc0c1afcfe73037e5dd5d69102958"
)
CANONICAL_PHASE7I_PLAN_ID = (
    "2b73f7c7707942be2644c5dfc0fcbed41be682c4877457ac86b6411619e8cd34"
)
CANONICAL_PHASE7I_EXPERIMENT_ID = (
    "5d2953a0e20e471cdf26de0dae16ffff75b8cab159e3fbfcbb959a5349117e87"
)
REFERENCE_K = 1.0
K_SENSITIVITY = (0.0, 0.5, 1.0, 2.0)
DEFAULT_SAMPLE_B_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_sample_b_v1"
DEFAULT_PLAN_B_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_coverage_plan_b_v1"
DEFAULT_EXPERIMENT_B_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_population_b_v1"
DEFAULT_PHASE7I_PLAN_PATH = PHASE7I_PLAN_ROOT / CANONICAL_PHASE7I_PLAN_ID
DEFAULT_PHASE7I_EXPERIMENT_PATH = (
    PHASE7I_EXPERIMENT_ROOT / CANONICAL_PHASE7I_EXPERIMENT_ID
)
DEFAULT_SAMPLE_A_PATH = DEFAULT_SAMPLE_ARTIFACT_PATH
DEFAULT_PHASE7H_PATH = DEFAULT_PHASE7H_ARTIFACT_PATH


class BoundedSensoryRobustnessError(ValueError):
    """Invalid source, disjoint sample, coverage plan, or Phase 7J run."""


def _as_input(artifact: Any) -> dict[str, Any]:
    return artifact.as_input() if hasattr(artifact, "as_input") else dict(artifact)


def _identity(
    source: RelativeColumnAssignmentSource, circuit: CircuitContract
) -> dict[str, Any]:
    return {
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": {
            "dataset": circuit.provenance.dataset,
            "candidate_id": circuit.candidate.identifier,
            "candidate_version": circuit.candidate.version,
            "file_sha256": dict(circuit.integrity.sha256_by_file),
        },
    }


def _rank_quartiles(candidates: Sequence[dict[str, Any]]) -> dict[int, dict[str, int]]:
    ordered = sorted(
        candidates,
        key=lambda item: (item["structural_weight"], item["body_id"]),
    )
    if len(ordered) < 4:
        raise BoundedSensoryRobustnessError(
            "disjoint candidate stratum has fewer than four bodies."
        )
    output: dict[int, dict[str, int]] = {}
    for rank, row in enumerate(ordered):
        quartile = min(3, (rank * 4) // len(ordered))
        prior_count = sum(
            min(3, (prior_rank * 4) // len(ordered)) == quartile
            for prior_rank in range(rank)
        )
        output[row["body_id"]] = {
            "rank_zero_based": rank,
            "quartile_index_zero_based": quartile,
            "rank_within_quartile_zero_based": prior_count,
        }
    if {value["quartile_index_zero_based"] for value in output.values()} != {
        0,
        1,
        2,
        3,
    }:
        raise BoundedSensoryRobustnessError("rank quartiles are degenerate.")
    return output


def select_independent_sample(
    source: RelativeColumnAssignmentSource,
    circuit: CircuitContract,
    sample_a_artifact: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Select four disjoint bodies per type/side stratum, using no outcomes."""
    sample_a = _as_input(sample_a_artifact)
    expected_a_config, expected_a_result = select_bounded_sample(source, circuit)
    if (
        sample_a.get("artifact_id") != CANONICAL_SAMPLE_A_ID
        or sample_a.get("config") != expected_a_config
        or sample_a.get("result") != expected_a_result
    ):
        raise BoundedSensoryRobustnessError(
            "canonical Sample A did not replay from pinned source contracts."
        )
    body_rows, _ = _body_index(source, circuit)
    selected_a = sample_a["result"]["selected_bodies"]
    a_ids = set(sample_a["result"]["body_ids"])
    selected_b: list[dict[str, Any]] = []
    quartile_summaries = []
    for neuron_type, side in STRATA:
        stratum_a = [
            body_rows[item["body_id"]]
            for item in selected_a
            if item["neuron_type"] == neuron_type and item["side"] == side
        ]
        candidates = [
            row
            for row in body_rows.values()
            if row["neuron_type"] == neuron_type
            and row["side"] == side
            and row["body_id"] not in a_ids
        ]
        ranks = _rank_quartiles(candidates)
        prior_selected = list(stratum_a)
        for quartile_index in range(4):
            quartile_rows = [
                row
                for row in candidates
                if ranks[row["body_id"]]["quartile_index_zero_based"] == quartile_index
            ]
            chosen, minimum_distance = _maximin_candidate(quartile_rows, prior_selected)
            rank = ranks[chosen["body_id"]]
            selection = dict(chosen)
            selection.update(
                {
                    "selection_quartile": quartile_index + 1,
                    "selection_rank_zero_based": rank["rank_zero_based"],
                    "rank_within_quartile_zero_based": rank[
                        "rank_within_quartile_zero_based"
                    ],
                    "quartile_candidate_count": len(quartile_rows),
                    "minimum_hex_centroid_distance_to_sample_a_and_prior_b": (
                        minimum_distance
                    ),
                    "canonical_sentinel": False,
                }
            )
            selected_b.append(selection)
            prior_selected.append(selection)
            quartile_summaries.append(
                {
                    "neuron_type": neuron_type,
                    "side": side,
                    "quartile": quartile_index + 1,
                    "candidate_count": len(quartile_rows),
                    "selected_body_id": chosen["body_id"],
                    "minimum_hex_centroid_distance": minimum_distance,
                }
            )

    b_ids = [item["body_id"] for item in selected_b]
    if (
        len(b_ids) != SAMPLE_SIZE
        or len(set(b_ids)) != SAMPLE_SIZE
        or set(b_ids) & a_ids
    ):
        raise BoundedSensoryRobustnessError(
            "Sample B must contain exactly 16 unique bodies disjoint from Sample A."
        )
    counts = [
        {
            "neuron_type": neuron_type,
            "side": side,
            "count": sum(
                item["neuron_type"] == neuron_type and item["side"] == side
                for item in selected_b
            ),
        }
        for neuron_type, side in STRATA
    ]
    if any(item["count"] != 4 for item in counts):
        raise BoundedSensoryRobustnessError("Sample B is not exactly 4×4 balanced.")
    config = {
        "schema": SAMPLE_CONFIG_SCHEMA,
        "artifact_schema": SAMPLE_ARTIFACT_SCHEMA,
        "sample_id": "phase7j_independent_disjoint_16_body_sample_b_v1",
        "selection_method_id": SELECTION_METHOD_ID,
        "sample_size": SAMPLE_SIZE,
        "sample_a_exclusion": _artifact_reference(
            sample_a, "bounded_sensory_sample_artifact_v1"
        ),
        **_identity(source, circuit),
        "strata": [
            {"neuron_type": neuron_type, "side": side, "count": 4}
            for neuron_type, side in STRATA
        ],
        "selection_inputs": [
            "body_id",
            "neuron_type",
            "side",
            "anatomical_column_centroid_hex",
            "column_topology_and_occupancy",
            "source_assignment_fraction",
            "direct_DNp01_structural_count_as_descriptor_only",
        ],
        "selection_excludes_sample_a": True,
        "selection_excludes_model_outcomes": True,
        "model_outcomes_used": False,
        "structural_count_semantics": "DESCRIPTIVE_RANK_PARTITION_ONLY",
        "centroid_semantics": "UNWEIGHTED_BODY_COLUMN_RECORD_CENTROID_HEX_SPACE",
        "method": {
            "candidate_order": "structural_weight_then_body_id",
            "rank_partition": "balanced_floor_rank_times_4_over_candidate_count",
            "quartile_selection_order": [1, 2, 3, 4],
            "within_quartile_choice": (
                "maximize_minimum_hex_centroid_distance_to_all_sample_a_and_prior_sample_b"
            ),
            "tie_break": "smallest_body_id",
            "canonical_sentinels_forced": False,
        },
    }
    result = {
        "schema": SAMPLE_RESULT_SCHEMA,
        "sample_id": config["sample_id"],
        "sample_size": SAMPLE_SIZE,
        "body_ids": b_ids,
        "selected_bodies": selected_b,
        "stratum_counts": counts,
        "quartile_summaries": quartile_summaries,
        "sample_a_body_ids": sorted(a_ids),
        "sample_a_overlap_count": len(set(b_ids) & a_ids),
        "selection_semantics": "INDEPENDENT_PRE_OUTCOME_ANATOMICAL_STRUCTURAL_SAMPLE",
        "model_outcomes_used": False,
        "disjoint_from_sample_a": True,
    }
    return config, result


def _stimulus_identity(entry: Mapping[str, Any]) -> RelativeColumnStimulus:
    stimulus_config = entry.get("config")
    if not isinstance(stimulus_config, Mapping) or entry.get("sha256") != sha256_bytes(
        canonical_json_bytes(stimulus_config)
    ):
        raise BoundedSensoryRobustnessError("canonical Sample A stimulus is malformed.")
    return RelativeColumnStimulus.from_dict(dict(stimulus_config))


def _records_for_sample(
    body_ids: Sequence[int], source: RelativeColumnAssignmentSource
) -> tuple[dict[int, tuple[Any, ...]], dict[int, Any]]:
    ids = tuple(body_ids)
    records_by_body: dict[int, list[Any]] = defaultdict(list)
    for record in source.contract.records:
        if record.body_id in ids:
            records_by_body[record.body_id].append(record)
    summaries = {
        item.body_id: item for item in source.contract.summaries if item.body_id in ids
    }
    if set(records_by_body) != set(ids) or set(summaries) != set(ids):
        raise BoundedSensoryRobustnessError("Sample B source topology is incomplete.")
    return (
        {body_id: tuple(sorted(records_by_body[body_id])) for body_id in ids},
        summaries,
    )


def _anatomical_coverage(
    sample_result: Mapping[str, Any],
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    stimuli: Sequence[RelativeColumnStimulus],
) -> list[dict[str, Any]]:
    ids = tuple(sample_result["body_ids"])
    records_by_body, summaries = _records_for_sample(ids, source)
    covered: dict[int, list[str]] = {body_id: [] for body_id in ids}
    maximum: dict[int, float] = dict.fromkeys(ids, 0.0)
    for stimulus in stimuli:
        for radius in stimulus.radii_lattice_steps:
            active = frozenset(active_column_set(stimulus, grid, radius))
            for body_id in ids:
                exposure = compute_body_exposure(
                    records_by_body[body_id], summaries[body_id], stimulus, active
                )["column_overlap_fraction"]
                if not math.isfinite(exposure) or not 0.0 <= exposure <= 1.0:
                    raise BoundedSensoryRobustnessError(
                        "source anatomical exposure is invalid."
                    )
                maximum[body_id] = max(maximum[body_id], exposure)
                if exposure > 0.0:
                    covered[body_id].append(stimulus.stimulus_id)
    identities = {item["body_id"]: item for item in sample_result["selected_bodies"]}
    return [
        {
            "body_id": body_id,
            "neuron_type": identities[body_id]["neuron_type"],
            "side": identities[body_id]["side"],
            "max_column_overlap_fraction": maximum[body_id],
            "covered_stimulus_ids": list(dict.fromkeys(covered[body_id])),
            "body_stimulus_covered": maximum[body_id] > 0.0,
        }
        for body_id in ids
    ]


def _canonical_stimulus_entries(
    phase7i_plan: LoadedCoveragePlan,
) -> list[dict[str, Any]]:
    entries = phase7i_plan.config.get("stimuli")
    if not isinstance(entries, list) or not entries:
        raise BoundedSensoryRobustnessError("canonical Phase 7I battery is empty.")
    parsed = [_stimulus_identity(entry) for entry in entries]
    ids = [item.stimulus_id for item in parsed]
    if len(ids) != len(set(ids)):
        raise BoundedSensoryRobustnessError("canonical battery has duplicate stimuli.")
    if not set(REFERENCE_STIMULUS_IDS) <= set(ids):
        raise BoundedSensoryRobustnessError(
            "canonical battery is missing Phase 7F reference conditions."
        )
    return entries


def compute_sample_b_coverage_plan(
    sample_b_artifact: Mapping[str, Any],
    sample_a_artifact: LoadedSampleArtifact,
    phase7h_artifact: LoadedPopulationArtifact,
    phase7i_plan: LoadedCoveragePlan,
    phase7i_experiment: Any,
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Plan extra disks from source-column overlap only; no model outputs read."""
    sample_b = _as_input(sample_b_artifact)
    expected_b_config, expected_b_result = select_independent_sample(
        source, circuit, sample_a_artifact.as_input()
    )
    if (
        sample_b.get("artifact_schema") != SAMPLE_ARTIFACT_SCHEMA
        or sample_b.get("config") != expected_b_config
        or sample_b.get("result") != expected_b_result
        or sample_b.get("artifact_id")
        != sample_b.get("manifest", {}).get("artifact_id")
    ):
        raise BoundedSensoryRobustnessError(
            "independent Sample B failed source replay."
        )
    if (
        sample_a_artifact.artifact_id != CANONICAL_SAMPLE_A_ID
        or phase7h_artifact.artifact_id != CANONICAL_PHASE7H_ID
        or phase7i_plan.artifact_id != CANONICAL_PHASE7I_PLAN_ID
        or phase7i_experiment.artifact_id != CANONICAL_PHASE7I_EXPERIMENT_ID
        or phase7i_experiment.result.get("coverage_plan_artifact_id")
        != CANONICAL_PHASE7I_PLAN_ID
        or phase7h_artifact.result.get("sample_artifact_id") != CANONICAL_SAMPLE_A_ID
    ):
        raise BoundedSensoryRobustnessError("canonical Sample A/7I baseline mismatch.")
    baseline_entries = _canonical_stimulus_entries(phase7i_plan)
    base_stimuli = tuple(_stimulus_identity(item) for item in baseline_entries)
    b_result = sample_b["result"]
    initial_coverage = _anatomical_coverage(b_result, source, grid, base_stimuli)
    uncovered = [
        row["body_id"] for row in initial_coverage if not row["body_stimulus_covered"]
    ]
    if uncovered:
        records_by_body, summaries = _records_for_sample(b_result["body_ids"], source)
        identities = {row["body_id"]: row for row in b_result["selected_bodies"]}
        selected_disks: list[dict[str, Any]] = []
        search = []
        for side in ("L", "R"):
            side_uncovered = [
                body_id for body_id in uncovered if identities[body_id]["side"] == side
            ]
            disks, summary = _coverage_candidates_for_side(
                side, side_uncovered, records_by_body, summaries, grid
            )
            selected_disks.extend(disks)
            search.append(summary)
    else:
        selected_disks = []
        search = [
            {
                "side": side,
                "source_centre_count": 0,
                "candidate_disks_evaluated": 0,
                "nonempty_unique_coverage_masks": 0,
                "selected_disks": 0,
            }
            for side in ("L", "R")
        ]

    extension_entries = []
    extension_rows = []
    for disk in selected_disks:
        side = disk["side"]
        center = disk["centre_hex"]
        radius = disk["radius_lattice_steps"]
        stimulus_id = (
            f"coverage_b_{side.lower()}_{center[0]:02d}_{center[1]:02d}_r{radius}"
        )
        stimulus = RelativeColumnStimulus(
            stimulus_id=stimulus_id,
            side=side,
            centre_hex1=center[0],
            centre_hex2=center[1],
            dt_ms=0.1,
            radii_lattice_steps=(radius,),
        )
        serialized = stimulus.to_dict()
        extension_entries.append(
            {
                "origin": "PHASE7J_SAMPLE_B_ANATOMY_ONLY_EXTENSION",
                "config": serialized,
                "sha256": sha256_bytes(canonical_json_bytes(serialized)),
            }
        )
        extension_rows.append(
            {
                "stimulus_id": stimulus_id,
                **disk,
                "centre_is_source_column": True,
                "coverage_basis": "column_overlap_fraction_gt_zero",
                "model_outcomes_used": False,
            }
        )

    all_entries = [*baseline_entries, *extension_entries]
    all_ids = [item["config"]["stimulus_id"] for item in all_entries]
    if len(all_ids) != len(set(all_ids)):
        raise BoundedSensoryRobustnessError(
            "coverage extension duplicates an existing stimulus identity."
        )
    total_stimuli = tuple(_stimulus_identity(item) for item in all_entries)
    final_coverage = _anatomical_coverage(b_result, source, grid, total_stimuli)
    if any(not row["body_stimulus_covered"] for row in final_coverage):
        raise BoundedSensoryRobustnessError(
            "bounded anatomy-only extension did not cover every Sample B body."
        )

    config = {
        "schema": PLAN_CONFIG_SCHEMA,
        "artifact_schema": PLAN_ARTIFACT_SCHEMA,
        "plan_method_id": PLAN_METHOD_ID,
        "sample_a_artifact": _artifact_reference(
            sample_a_artifact.as_input(), "bounded_sensory_sample_artifact_v1"
        ),
        "sample_b_artifact": _artifact_reference(sample_b, SAMPLE_ARTIFACT_SCHEMA),
        "phase7h_artifact": _artifact_reference(
            phase7h_artifact, "bounded_sensory_population_artifact_v1"
        ),
        "phase7i_plan_artifact": _artifact_reference(
            phase7i_plan, "bounded_sensory_coverage_plan_artifact_v1"
        ),
        "phase7i_experiment_artifact": _artifact_reference(
            phase7i_experiment, "bounded_sensory_coverage_artifact_v1"
        ),
        **_identity(source, circuit),
        "column_grid_identity": grid.to_identity_dict(),
        "body_ids": list(b_result["body_ids"]),
        "initial_battery_identity": [
            {"stimulus_id": item["config"]["stimulus_id"], "sha256": item["sha256"]}
            for item in baseline_entries
        ],
        "coverage_metric": "column_overlap_fraction_gt_zero",
        "candidate_centres": "uncovered_sample_b_source_columns_only",
        "candidate_radii_lattice_steps": list(range(1, MAX_RADIUS_LATTICE_STEPS + 1)),
        "objective_order": [
            "minimum_number_of_disks",
            "minimum_total_radius",
            "lexicographic_radius_then_source_centre",
        ],
        "model_outcomes_used_for_battery_design": False,
        "stimulus_model_id": "relative_column_expanding_disk_v1",
        "stimuli": all_entries,
    }
    result = {
        "schema": PLAN_RESULT_SCHEMA,
        "body_ids": list(b_result["body_ids"]),
        "initial_coverage": initial_coverage,
        "initial_covered_body_ids": [
            row["body_id"] for row in initial_coverage if row["body_stimulus_covered"]
        ],
        "initial_uncovered_body_ids": uncovered,
        "candidate_search_summary": search,
        "coverage_extension_stimuli": extension_rows,
        "final_coverage": final_coverage,
        "model_outcomes_used": False,
        "neural_dynamics_computed": False,
        "dn_p01_outputs_read_for_design": False,
        "purpose": "DISJOINT_SAMPLE_B_ANATOMICAL_COVERAGE_PLAN",
    }
    return config, result


def _sample_reference_states(
    trajectories: Mapping[str, Sequence[Mapping[str, Any]]],
    sample_result: Mapping[str, Any],
) -> tuple[dict[int, list[float]], float, int]:
    return _condition_states(
        trajectories,
        sample_result,
        "left_expand_33_29",
        "right_expand_23_09",
    )


def _body_path_coverage(
    sample_result: Mapping[str, Any],
    assignment: Mapping[str, Any],
    trajectories: Mapping[str, Sequence[Mapping[str, Any]]],
    conditions: Sequence[Mapping[str, Any]],
    stimulus_ids: Sequence[str],
) -> list[dict[str, Any]]:
    ids = tuple(sample_result["body_ids"])
    maximum_exposure = dict.fromkeys(ids, 0.0)
    for sample in assignment["samples"]:
        for row in sample["assignments"]:
            maximum_exposure[row["body_id"]] = max(
                maximum_exposure[row["body_id"]], row["column_overlap_fraction"]
            )
    maximum_state = dict.fromkeys(ids, 0.0)
    for values in trajectories.values():
        for item in values:
            peak = max(row["state_value"] for row in item["state_timeline"])
            maximum_state[item["body_id"]] = max(maximum_state[item["body_id"]], peak)
    maximum_transfer = dict.fromkeys(ids, 0.0)
    first_nonzero_transfer: dict[int, str | None] = dict.fromkeys(ids, None)
    prefix = "sample_b_stimulus_"
    for condition in conditions:
        if not condition["condition_id"].startswith(prefix):
            continue
        stimulus_id = condition["condition_id"][len(prefix) :]
        for interval in condition["source_contributions_by_interval"]:
            for contribution in interval["contributions"]:
                body_id = contribution["source_body_id"]
                if contribution["model_drive_mveq"] > maximum_transfer[body_id]:
                    maximum_transfer[body_id] = contribution["model_drive_mveq"]
                if (
                    contribution["model_drive_mveq"] > 0.0
                    and first_nonzero_transfer[body_id] is None
                ):
                    first_nonzero_transfer[body_id] = stimulus_id

    identities = {item["body_id"]: item for item in sample_result["selected_bodies"]}
    rows = []
    for body_id in ids:
        exposure = maximum_exposure[body_id]
        state = maximum_state[body_id]
        transfer = maximum_transfer[body_id]
        rows.append(
            {
                "body_id": body_id,
                "neuron_type": identities[body_id]["neuron_type"],
                "side": identities[body_id]["side"],
                "target_body_id": identities[body_id]["target_body_id"],
                "max_column_overlap_fraction": exposure,
                "max_exploratory_state": state,
                "max_transfer_contribution_mveq": transfer,
                "first_positive_transfer_stimulus_id": first_nonzero_transfer[body_id],
                "body_stimulus_covered": exposure > 0.0,
                "body_state_exercised": state > 0.0,
                "body_transfer_exercised": transfer > 0.0,
                "coverage_semantics": "SOFTWARE_EXPERIMENT_COVERAGE_ONLY",
            }
        )
    if len(stimulus_ids) == 0:
        raise BoundedSensoryRobustnessError("coverage battery cannot be empty.")
    return rows


def _target_summary(conditions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    output = {}
    for target_id in (10001, 10010):
        target_rows = [
            target
            for condition in conditions
            for target in condition["targets"]
            if target["body_id"] == target_id
        ]
        output[str(target_id)] = {
            "maximum_peak_drive_mveq": max(
                (item["peak_drive_mveq"] for item in target_rows), default=0.0
            ),
            "minimum_membrane_mv": min(
                (item["minimum_membrane_mv"] for item in target_rows), default=-52.0
            ),
            "maximum_membrane_mv": max(
                (item["maximum_membrane_mv"] for item in target_rows), default=-52.0
            ),
            "simulated_spikes": [
                {"condition_id": condition["condition_id"], **spike}
                for condition in conditions
                for target in condition["targets"]
                if target["body_id"] == target_id
                for spike in target["simulated_spikes"]
            ],
        }
    return output


def _source_population_summary(
    sample_result: Mapping[str, Any],
    states: Mapping[int, Sequence[float]],
    conditions: Sequence[Mapping[str, Any]],
    *,
    condition_prefix: str,
) -> dict[str, Any]:
    bodies = sample_result["selected_bodies"]
    result: dict[str, Any] = {}
    for side in ("L", "R"):
        side_rows = [row for row in bodies if row["side"] == side]
        intervals = max(
            (len(states[row["body_id"]]) - 1 for row in side_rows), default=0
        )
        total = [
            sum(
                states[row["body_id"]][step]
                if step < len(states[row["body_id"]])
                else 0.0
                for row in side_rows
            )
            for step in range(intervals)
        ]
        result[side] = {
            "body_count": len(side_rows),
            "peak_source_state_sum": max(total, default=0.0),
        }
    relevant_conditions = [
        condition
        for condition in conditions
        if condition["condition_id"].startswith(condition_prefix)
    ]
    target_model_output = {}
    for target_id in (10001, 10010):
        target_rows = [
            (condition, target)
            for condition in relevant_conditions
            for target in condition["targets"]
            if target["body_id"] == target_id
        ]
        target_model_output[str(target_id)] = {
            "maximum_peak_drive_mveq": max(
                (target["peak_drive_mveq"] for _, target in target_rows),
                default=0.0,
            ),
            "minimum_membrane_mv": min(
                (target["minimum_membrane_mv"] for _, target in target_rows),
                default=-52.0,
            ),
            "maximum_membrane_mv": max(
                (target["maximum_membrane_mv"] for _, target in target_rows),
                default=-52.0,
            ),
            "simulated_spike_count": sum(
                len(target["simulated_spikes"]) for _, target in target_rows
            ),
            "simulated_spikes": [
                {"condition_id": condition["condition_id"], **spike}
                for condition, target in target_rows
                for spike in target["simulated_spikes"]
            ],
        }
    result["target_peak_drive_mveq"] = {
        str(target): max(
            (
                row["peak_drive_mveq"]
                for condition in relevant_conditions
                for row in condition["targets"]
                if row["body_id"] == target
            ),
            default=0.0,
        )
        for target in (10001, 10010)
    }
    result["target_model_output"] = target_model_output
    return result


def _serialized_artifact_bytes(artifact: Mapping[str, Any]) -> int:
    """Measure a persisted canonical artifact payload including its manifest."""
    try:
        return sum(
            len(canonical_json_bytes(artifact[key])) + 1
            for key in ("config", "result", "manifest")
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise BoundedSensoryRobustnessError(
            "persisted sample B artifact is missing canonical payload metadata."
        ) from exc


def _assert_contribution_accounting(conditions: Sequence[Mapping[str, Any]]) -> None:
    for condition in conditions:
        targets = {item["body_id"]: item for item in condition["targets"]}
        for interval in condition["source_contributions_by_interval"]:
            for target_id in (10001, 10010):
                summed = sum(
                    item["model_drive_mveq"]
                    for item in interval["contributions"]
                    if item["target_body_id"] == target_id
                )
                stored = targets[target_id]["drive_mveq_by_interval"][interval["step"]]
                if not math.isclose(summed, stored, rel_tol=0.0, abs_tol=1e-15):
                    raise BoundedSensoryRobustnessError(
                        "source contributions do not sum to target drive."
                    )


def compute_sample_b_experiment(
    sample_b_artifact: Mapping[str, Any],
    plan_artifact: Mapping[str, Any],
    sample_a_artifact: LoadedSampleArtifact,
    phase7h_artifact: LoadedPopulationArtifact,
    phase7i_plan: LoadedCoveragePlan,
    phase7i_experiment: Any,
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Use Phase 7H/7I pure components for a disjoint Sample B experiment."""
    sample_b = _as_input(sample_b_artifact)
    plan = _as_input(plan_artifact)
    expected_plan_config, expected_plan_result = compute_sample_b_coverage_plan(
        sample_b,
        sample_a_artifact,
        phase7h_artifact,
        phase7i_plan,
        phase7i_experiment,
        source,
        grid,
        circuit,
    )
    if (
        plan.get("artifact_schema") != PLAN_ARTIFACT_SCHEMA
        or plan.get("config") != expected_plan_config
        or plan.get("result") != expected_plan_result
    ):
        raise BoundedSensoryRobustnessError("Sample B coverage plan failed replay.")
    sample_result = sample_b["result"]
    stimuli_entries = plan["config"]["stimuli"]
    stimuli = tuple(_stimulus_identity(item) for item in stimuli_entries)
    assignment = _assignment_result(sample_result, source, grid, stimuli)
    trajectories = _sensory_trajectories(assignment, sample_result)
    routes = _route_set(sample_result, circuit)
    sample_ids = set(sample_result["body_ids"])

    conditions = []
    for stimulus in stimuli:
        trajectory_rows = trajectories[stimulus.stimulus_id]
        states = {
            item["body_id"]: [row["state_value"] for row in item["state_timeline"]]
            for item in trajectory_rows
        }
        intervals = len(next(iter(states.values()))) - 1
        conditions.append(
            _simulate_condition(
                condition_id=f"sample_b_stimulus_{stimulus.stimulus_id}",
                pathway_mask="all16",
                active_body_ids=sample_ids,
                k=REFERENCE_K,
                states=states,
                dt_ms=stimulus.dt_ms,
                steps=intervals,
                routes=routes,
                circuit=circuit,
            )
        )

    reference_states, reference_dt, reference_steps = _sample_reference_states(
        trajectories, sample_result
    )
    reference_masks = (
        ("reference_all16", "all16", REFERENCE_K),
        ("k_zero", "all16", 0.0),
        ("no_sources", "none", REFERENCE_K),
        ("lc4_only", "LC4", REFERENCE_K),
        ("lplc2_only", "LPLC2", REFERENCE_K),
        ("left_only", "left", REFERENCE_K),
        ("right_only", "right", REFERENCE_K),
        ("sensitivity_k_0_5", "all16", 0.5),
        ("sensitivity_k_2", "all16", 2.0),
    )
    for condition_id, mask, k in reference_masks:
        conditions.append(
            _simulate_condition(
                condition_id=condition_id,
                pathway_mask=mask,
                active_body_ids=_mask_ids(sample_result, mask),
                k=k,
                states=reference_states,
                dt_ms=reference_dt,
                steps=reference_steps,
                routes=routes,
                circuit=circuit,
            )
        )

    _assert_contribution_accounting(conditions)
    coverage_rows = _body_path_coverage(
        sample_result,
        assignment,
        trajectories,
        conditions,
        [stimulus.stimulus_id for stimulus in stimuli],
    )
    if any(
        not row["body_stimulus_covered"]
        or not row["body_state_exercised"]
        or not row["body_transfer_exercised"]
        for row in coverage_rows
    ):
        raise BoundedSensoryRobustnessError(
            "Sample B failed 16/16 non-zero path coverage."
        )
    if any(
        condition["pathway_mask"] == "none"
        and any(target["peak_drive_mveq"] != 0.0 for target in condition["targets"])
        for condition in conditions
    ):
        raise BoundedSensoryRobustnessError("no-sources control produced transfer.")
    zero_condition = next(
        item for item in conditions if item["condition_id"] == "k_zero"
    )
    if any(target["peak_drive_mveq"] != 0.0 for target in zero_condition["targets"]):
        raise BoundedSensoryRobustnessError("k=0 control produced transfer.")

    sample_a_rows = sample_a_artifact.result["selected_bodies"]
    sample_b_rows = sample_result["selected_bodies"]
    sample_a_strata = _structural_anatomical_summary(sample_a_rows)
    sample_b_strata = _structural_anatomical_summary(sample_b_rows)
    phase7i_stimulus_count = len(phase7i_plan.config["stimuli"])
    extension_count = len(plan["result"]["coverage_extension_stimuli"])
    ref_trajectories_a = phase7i_experiment.result["sensory_trajectories_by_stimulus"]
    ref_states_a, _, _ = _sample_reference_states(
        ref_trajectories_a, sample_a_artifact.result
    )
    sample_a_population_summary = _source_population_summary(
        sample_a_artifact.result,
        ref_states_a,
        phase7i_experiment.result["conditions"],
        condition_prefix="phase7i_",
    )
    sample_b_population_summary = _source_population_summary(
        sample_result,
        reference_states,
        conditions,
        condition_prefix="sample_b_stimulus_",
    )

    sample_a_total_artifact_bytes = phase7i_experiment.summary()[
        "artifact_bytes_including_manifest"
    ]
    sample_b_total_artifact_bytes = _serialized_artifact_bytes(sample_b)
    sample_a_coverage_totals = phase7i_experiment.result["coverage_totals"]
    sample_b_coverage_totals = {
        "body_stimulus_covered": sum(
            row["body_stimulus_covered"] for row in coverage_rows
        ),
        "body_state_exercised": sum(
            row["body_state_exercised"] for row in coverage_rows
        ),
        "body_transfer_exercised": sum(
            row["body_transfer_exercised"] for row in coverage_rows
        ),
        "denominator": SAMPLE_SIZE,
    }
    config = {
        "schema": EXPERIMENT_CONFIG_SCHEMA,
        "artifact_schema": EXPERIMENT_ARTIFACT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "purpose": "DISJOINT_SAMPLE_B_ARCHITECTURE_ROBUSTNESS",
        "sample_a_artifact": _artifact_reference(
            sample_a_artifact.as_input(), "bounded_sensory_sample_artifact_v1"
        ),
        "sample_b_artifact": _artifact_reference(sample_b, SAMPLE_ARTIFACT_SCHEMA),
        "coverage_plan_artifact": _artifact_reference(plan, PLAN_ARTIFACT_SCHEMA),
        "phase7h_artifact": _artifact_reference(
            phase7h_artifact, "bounded_sensory_population_artifact_v1"
        ),
        "phase7i_plan_artifact": _artifact_reference(
            phase7i_plan, "bounded_sensory_coverage_plan_artifact_v1"
        ),
        "phase7i_experiment_artifact": _artifact_reference(
            phase7i_experiment, "bounded_sensory_coverage_artifact_v1"
        ),
        **_identity(source, circuit),
        "column_grid_identity": grid.to_identity_dict(),
        "body_ids": list(sample_result["body_ids"]),
        "stimulus_model_id": "relative_column_expanding_disk_v1",
        "stimuli": stimuli_entries,
        "sensory_model": phase7i_experiment.config["sensory_model"],
        "transfer_model": phase7i_experiment.config["transfer_model"],
        "dnp01_model": phase7i_experiment.config["dnp01_model"],
        "route_contract": [route.to_dict() for route in routes],
        "pathway_controls": [item[0] for item in reference_masks],
        "sensitivity_k_transfer_mveq_per_state": list(K_SENSITIVITY),
        "model_invariants_match_sample_a": True,
        "sample_a_vs_b_comparison": {
            "sample_a_id": CANONICAL_SAMPLE_A_ID,
            "sample_a_body_ids": sample_a_artifact.result["body_ids"],
            "sample_a_stratum_summaries": sample_a_strata,
            "sample_b_stratum_summaries": sample_b_strata,
            "sample_a_disjointness_overlap_count": len(
                set(sample_result["body_ids"])
                & set(sample_a_artifact.result["body_ids"])
            ),
            "sample_a_stimulus_count": phase7i_stimulus_count,
            "sample_b_stimulus_count": len(stimuli),
            "sample_a_coverage_extension_stimulus_count": len(
                phase7i_plan.result["coverage_extension_stimuli"]
            ),
            "sample_b_coverage_extension_stimulus_count": extension_count,
            "sample_a_assignment_samples": phase7i_experiment.result["assignment"][
                "sample_count"
            ],
            "sample_b_assignment_samples": assignment["sample_count"],
            "sample_a_coverage_totals": sample_a_coverage_totals,
            "sample_b_coverage_totals": sample_b_coverage_totals,
            "sample_a_population_summary": sample_a_population_summary,
            "sample_b_population_summary": sample_b_population_summary,
            "sample_a_artifact_bytes": sample_a_total_artifact_bytes,
            "sample_b_artifact_bytes": sample_b_total_artifact_bytes,
            "interpretation": "ARCHITECTURE_ROBUSTNESS_ONLY_NOT_BIOLOGICAL_REPLICATION",
        },
        "time_alignment": "sensory_state_boundary_n_drives_interval_n_to_n_plus_1",
        "scientific_boundary": {
            "absolute_visual_angle_present": False,
            "functional_receptive_field_claim": False,
            "physiological_calibration": False,
            "structural_count_is_efficacy": False,
            "body_specific_gain": False,
            "behavior_or_body_mechanics": False,
            "dn_p01_is_existing_model_output": True,
        },
    }
    result = {
        "schema": EXPERIMENT_RESULT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "purpose": "DISJOINT_SAMPLE_B_ARCHITECTURE_ROBUSTNESS",
        "sample_a_artifact_id": CANONICAL_SAMPLE_A_ID,
        "sample_b_artifact_id": sample_b["artifact_id"],
        "coverage_plan_artifact_id": plan["artifact_id"],
        "body_ids": list(sample_result["body_ids"]),
        "assignment": assignment,
        "sensory_trajectories_by_stimulus": trajectories,
        "conditions": conditions,
        "body_coverage": coverage_rows,
        "coverage_totals": {
            "body_stimulus_covered": sum(
                row["body_stimulus_covered"] for row in coverage_rows
            ),
            "body_state_exercised": sum(
                row["body_state_exercised"] for row in coverage_rows
            ),
            "body_transfer_exercised": sum(
                row["body_transfer_exercised"] for row in coverage_rows
            ),
            "denominator": SAMPLE_SIZE,
        },
        "target_summary": _target_summary(conditions),
        "contribution_accounting_validated": True,
        "selection_and_stimulus_design_outcome_blind": True,
        "model_invariants_match_sample_a": True,
        "result_semantics": "EXPLORATORY_DISJOINT_16_BODY_ARCHITECTURE_ROBUSTNESS",
    }
    return config, result


def _structural_anatomical_summary(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    output = []
    for neuron_type, side in STRATA:
        stratum = [
            row
            for row in rows
            if row["neuron_type"] == neuron_type and row["side"] == side
        ]
        weights = sorted(row["structural_weight"] for row in stratum)
        centroids = [row["anatomical_column_centroid"] for row in stratum]
        if not stratum:
            raise BoundedSensoryRobustnessError("sample stratum is empty.")
        output.append(
            {
                "neuron_type": neuron_type,
                "side": side,
                "body_count": len(stratum),
                "structural_count_values": weights,
                "structural_count_min": min(weights),
                "structural_count_max": max(weights),
                "structural_count_mean": sum(weights) / len(weights),
                "mean_column_centroid_hex": [
                    sum(point[index] for point in centroids) / len(centroids)
                    for index in (0, 1)
                ],
                "centroid_semantics": "UNWEIGHTED_RELATIVE_COLUMN_ANATOMY_ONLY",
            }
        )
    return output


def replay_canonical_baselines(
    *,
    sample_a_path: str = str(DEFAULT_SAMPLE_A_PATH),
    phase7h_path: str = str(DEFAULT_PHASE7H_PATH),
    phase7i_plan_path: str = str(DEFAULT_PHASE7I_PLAN_PATH),
    phase7i_experiment_path: str = str(DEFAULT_PHASE7I_EXPERIMENT_PATH),
    source_root: str = str(DEFAULT_SOURCE_ROOT),
    workbook_path: str = str(DEFAULT_WORKBOOK),
) -> tuple[
    LoadedSampleArtifact,
    LoadedPopulationArtifact,
    LoadedCoveragePlan,
    Any,
    RelativeColumnAssignmentSource,
    RelativeColumnGrid,
    CircuitContract,
]:
    """Replay A and 7D–7I baseline artifacts before any Sample B dynamics."""
    sample_a = replay_sample_artifact(
        sample_a_path, source_root=source_root, workbook_path=workbook_path
    )
    if sample_a.artifact_id != CANONICAL_SAMPLE_A_ID:
        raise BoundedSensoryRobustnessError("canonical Sample A identity changed.")
    phase7h = replay_population_artifact(
        phase7h_path,
        sample_a_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    if phase7h.artifact_id != CANONICAL_PHASE7H_ID:
        raise BoundedSensoryRobustnessError("canonical Phase 7H identity changed.")
    plan_i = replay_coverage_plan(
        phase7i_plan_path,
        sample_a_path,
        phase7h_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    if plan_i.artifact_id != CANONICAL_PHASE7I_PLAN_ID:
        raise BoundedSensoryRobustnessError("canonical Phase 7I plan identity changed.")
    experiment_i = replay_coverage_experiment(
        phase7i_experiment_path,
        phase7i_plan_path,
        sample_a_path,
        phase7h_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    if experiment_i.artifact_id != CANONICAL_PHASE7I_EXPERIMENT_ID:
        raise BoundedSensoryRobustnessError(
            "canonical Phase 7I experiment identity changed."
        )
    source, grid, circuit = make_source_bundle(source_root, workbook_path)
    return sample_a, phase7h, plan_i, experiment_i, source, grid, circuit


def make_sample_b_payload(
    sample_a_path: str = str(DEFAULT_SAMPLE_A_PATH),
    *,
    source_root: str = str(DEFAULT_SOURCE_ROOT),
    workbook_path: str = str(DEFAULT_WORKBOOK),
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Generate Sample B using only source contracts and canonical Sample A."""
    sample_a = replay_sample_artifact(
        sample_a_path, source_root=source_root, workbook_path=workbook_path
    )
    source, _, circuit = make_source_bundle(source_root, workbook_path)
    return select_independent_sample(source, circuit, sample_a.as_input())


def make_sample_b_plan_payload(
    sample_b_artifact: Mapping[str, Any],
    *,
    sample_a_path: str = str(DEFAULT_SAMPLE_A_PATH),
    phase7h_path: str = str(DEFAULT_PHASE7H_PATH),
    phase7i_plan_path: str = str(DEFAULT_PHASE7I_PLAN_PATH),
    phase7i_experiment_path: str = str(DEFAULT_PHASE7I_EXPERIMENT_PATH),
    source_root: str = str(DEFAULT_SOURCE_ROOT),
    workbook_path: str = str(DEFAULT_WORKBOOK),
) -> tuple[dict[str, Any], dict[str, Any]]:
    sample_a, phase7h, plan_i, experiment_i, source, grid, circuit = (
        replay_canonical_baselines(
            sample_a_path=sample_a_path,
            phase7h_path=phase7h_path,
            phase7i_plan_path=phase7i_plan_path,
            phase7i_experiment_path=phase7i_experiment_path,
            source_root=source_root,
            workbook_path=workbook_path,
        )
    )
    return compute_sample_b_coverage_plan(
        sample_b_artifact,
        sample_a,
        phase7h,
        plan_i,
        experiment_i,
        source,
        grid,
        circuit,
    )


def make_sample_b_experiment_payload(
    sample_b_artifact: Mapping[str, Any],
    plan_artifact: Mapping[str, Any],
    *,
    sample_a_path: str = str(DEFAULT_SAMPLE_A_PATH),
    phase7h_path: str = str(DEFAULT_PHASE7H_PATH),
    phase7i_plan_path: str = str(DEFAULT_PHASE7I_PLAN_PATH),
    phase7i_experiment_path: str = str(DEFAULT_PHASE7I_EXPERIMENT_PATH),
    source_root: str = str(DEFAULT_SOURCE_ROOT),
    workbook_path: str = str(DEFAULT_WORKBOOK),
) -> tuple[dict[str, Any], dict[str, Any]]:
    baselines = replay_canonical_baselines(
        sample_a_path=sample_a_path,
        phase7h_path=phase7h_path,
        phase7i_plan_path=phase7i_plan_path,
        phase7i_experiment_path=phase7i_experiment_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    sample_a, phase7h, plan_i, experiment_i, source, grid, circuit = baselines
    return compute_sample_b_experiment(
        sample_b_artifact,
        plan_artifact,
        sample_a,
        phase7h,
        plan_i,
        experiment_i,
        source,
        grid,
        circuit,
    )
