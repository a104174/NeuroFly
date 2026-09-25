"""Phase 7I anatomy-only stimulus coverage and 16-body path validation."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from neurofly.bounded_sensory_population import (
    DEFAULT_EXPERIMENT_OUTPUT_ROOT as PHASE7H_EXPERIMENT_ROOT,
)
from neurofly.bounded_sensory_population import (
    DEFAULT_SAMPLE_OUTPUT_ROOT as PHASE7H_SAMPLE_ROOT,
)
from neurofly.bounded_sensory_population import (
    _assignment_result,
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

PLAN_CONFIG_SCHEMA = "bounded_sensory_coverage_plan_config_v1"
PLAN_RESULT_SCHEMA = "bounded_sensory_coverage_plan_result_v1"
PLAN_ARTIFACT_SCHEMA = "bounded_sensory_coverage_plan_artifact_v1"
EXPERIMENT_CONFIG_SCHEMA = "bounded_sensory_coverage_config_v1"
EXPERIMENT_RESULT_SCHEMA = "bounded_sensory_coverage_result_v1"
EXPERIMENT_ARTIFACT_SCHEMA = "bounded_sensory_coverage_artifact_v1"
PLAN_METHOD_ID = "minimum_source_column_disk_set_cover_v1"
EXPERIMENT_ID = "phase7i_bounded_16_body_coverage_validation_v1"
MAX_RADIUS_LATTICE_STEPS = 4
REFERENCE_K_MVEQ_PER_STATE = 1.0
CANONICAL_SAMPLE_ID = "18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7"
CANONICAL_PHASE7H_ID = (
    "385480b3c915b25536e1119d17effa15567bc0c1afcfe73037e5dd5d69102958"
)
CANONICAL_BODY_IDS = (
    12032,
    16809,
    14888,
    514956,
    16128,
    38065,
    21804,
    19634,
    11498,
    40811,
    29815,
    515971,
    14465,
    37925,
    21045,
    22261,
)
DEFAULT_PLAN_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_coverage_plan_v1"
DEFAULT_EXPERIMENT_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / "bounded_sensory_coverage_v1"


class BoundedSensoryCoverageError(ValueError):
    """A pinned Phase 7I source, plan, or coverage experiment is invalid."""


def _as_input(artifact: Any) -> dict[str, Any]:
    return artifact.as_input() if hasattr(artifact, "as_input") else dict(artifact)


def _artifact_reference(artifact: Any, schema: str) -> dict[str, Any]:
    if isinstance(artifact, Mapping):
        return {
            "artifact_schema": schema,
            "artifact_id": artifact["artifact_id"],
            "manifest_sha256": artifact["manifest_sha256"],
            "config_sha256": artifact["config_sha256"],
            "result_sha256": artifact["result_sha256"],
        }
    manifest = artifact.manifest
    return {
        "artifact_schema": schema,
        "artifact_id": artifact.artifact_id,
        "manifest_sha256": sha256_bytes(canonical_json_bytes(manifest) + b"\n"),
        "config_sha256": manifest["config_sha256"],
        "result_sha256": manifest["result_sha256"],
    }


def _selected_body_records(
    sample_result: Mapping[str, Any], source: RelativeColumnAssignmentSource
) -> tuple[dict[int, tuple[Any, ...]], dict[int, Any]]:
    body_ids = tuple(sample_result.get("body_ids", ()))
    if body_ids != CANONICAL_BODY_IDS or len(set(body_ids)) != 16:
        raise BoundedSensoryCoverageError("canonical Phase 7H 16-body sample mismatch.")
    record_map: dict[int, list[Any]] = defaultdict(list)
    for record in source.contract.records:
        if record.body_id in body_ids:
            record_map[record.body_id].append(record)
    summaries = {
        item.body_id: item
        for item in source.contract.summaries
        if item.body_id in body_ids
    }
    if set(record_map) != set(body_ids) or set(summaries) != set(body_ids):
        raise BoundedSensoryCoverageError("selected source topology is incomplete.")
    return (
        {body_id: tuple(sorted(record_map[body_id])) for body_id in body_ids},
        summaries,
    )


def _initial_body_coverage(
    phase7h_artifact: LoadedPopulationArtifact,
    sample_result: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if (
        phase7h_artifact.artifact_id != CANONICAL_PHASE7H_ID
        or phase7h_artifact.result.get("body_ids") != list(CANONICAL_BODY_IDS)
        or phase7h_artifact.result.get("sample_artifact_id") != CANONICAL_SAMPLE_ID
        or sample_result.get("body_ids") != list(CANONICAL_BODY_IDS)
    ):
        raise BoundedSensoryCoverageError(
            "canonical Phase 7H artifact identity mismatch."
        )
    max_exposure = dict.fromkeys(CANONICAL_BODY_IDS, 0.0)
    covered_by: dict[int, list[str]] = {body_id: [] for body_id in CANONICAL_BODY_IDS}
    assignment = phase7h_artifact.result.get("assignment", {})
    for sample in assignment.get("samples", ()):
        assignments = sample.get("assignments", ())
        if {item.get("body_id") for item in assignments} != set(CANONICAL_BODY_IDS):
            raise BoundedSensoryCoverageError("Phase 7H assignment body set changed.")
        for row in assignments:
            body_id = row["body_id"]
            exposure = row.get("column_overlap_fraction")
            if (
                isinstance(exposure, bool)
                or not isinstance(exposure, (int, float))
                or not math.isfinite(float(exposure))
                or not 0.0 <= float(exposure) <= 1.0
            ):
                raise BoundedSensoryCoverageError("Phase 7H exposure is malformed.")
            max_exposure[body_id] = max(max_exposure[body_id], float(exposure))
            if exposure > 0:
                covered_by[body_id].append(sample["stimulus_id"])

    identities = {item["body_id"]: item for item in sample_result["selected_bodies"]}
    return [
        {
            "body_id": body_id,
            "neuron_type": identities[body_id]["neuron_type"],
            "side": identities[body_id]["side"],
            "max_column_overlap_fraction": max_exposure[body_id],
            "covered_stimulus_ids": list(dict.fromkeys(covered_by[body_id])),
            "body_stimulus_covered": max_exposure[body_id] > 0.0,
        }
        for body_id in CANONICAL_BODY_IDS
    ]


def _coverage_candidates_for_side(
    side: str,
    target_ids: Sequence[int],
    records_by_body: Mapping[int, tuple[Any, ...]],
    summaries: Mapping[int, Any],
    grid: RelativeColumnGrid,
) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    if not target_ids:
        return (), {
            "side": side,
            "source_centre_count": 0,
            "candidate_disks_evaluated": 0,
            "nonempty_unique_coverage_masks": 0,
            "selected_disks": 0,
        }
    centers = sorted(
        {
            (record.ol_hex1, record.ol_hex2)
            for body_id in target_ids
            for record in records_by_body[body_id]
            if record.eye_side == side
        }
    )
    if not centers:
        raise BoundedSensoryCoverageError(
            f"uncovered {side} bodies have no source columns."
        )

    # Deduplicate geometries by the bodies they anatomically cover. The retained
    # representative minimizes radius, then uses source-coordinate order.
    best_by_coverage: dict[frozenset[int], dict[str, Any]] = {}
    for center in centers:
        if center not in grid.columns_by_side[side]:
            raise BoundedSensoryCoverageError(
                "source centre is absent from the pinned grid."
            )
        for radius in range(1, MAX_RADIUS_LATTICE_STEPS + 1):
            stimulus = RelativeColumnStimulus(
                stimulus_id="coverage_candidate",
                side=side,
                centre_hex1=center[0],
                centre_hex2=center[1],
                dt_ms=0.1,
                radii_lattice_steps=(radius,),
            )
            active = frozenset(active_column_set(stimulus, grid, radius))
            exposures = {
                body_id: compute_body_exposure(
                    records_by_body[body_id],
                    summaries[body_id],
                    stimulus,
                    active,
                )["column_overlap_fraction"]
                for body_id in target_ids
            }
            coverage = frozenset(
                body_id for body_id, value in exposures.items() if value > 0.0
            )
            if not coverage:
                continue
            candidate = {
                "side": side,
                "centre_hex": [center[0], center[1]],
                "radius_lattice_steps": radius,
                "covered_body_ids": sorted(coverage),
                "column_overlap_fraction_by_body": {
                    str(body_id): exposures[body_id] for body_id in sorted(coverage)
                },
            }
            prior = best_by_coverage.get(coverage)
            candidate_rank = (radius, center[0], center[1])
            if prior is None or candidate_rank < (
                prior["radius_lattice_steps"],
                prior["centre_hex"][0],
                prior["centre_hex"][1],
            ):
                best_by_coverage[coverage] = candidate

    candidates = tuple(
        sorted(
            best_by_coverage.values(),
            key=lambda item: (
                item["radius_lattice_steps"],
                item["centre_hex"][0],
                item["centre_hex"][1],
                item["covered_body_ids"],
            ),
        )
    )
    target_set = frozenset(target_ids)
    if not candidates:
        raise BoundedSensoryCoverageError(f"no bounded {side} coverage disk found.")

    def score(selection: tuple[dict[str, Any], ...]) -> tuple[Any, ...]:
        ordered = sorted(
            (
                item["radius_lattice_steps"],
                item["centre_hex"][0],
                item["centre_hex"][1],
            )
            for item in selection
        )
        return len(selection), sum(item[0] for item in ordered), tuple(ordered)

    # Exact dynamic-programming set cover; anatomical binary overlap only.
    best: dict[frozenset[int], tuple[dict[str, Any], ...]] = {frozenset(): ()}
    for candidate in candidates:
        candidate_coverage = frozenset(candidate["covered_body_ids"])
        updated = dict(best)
        for covered, selection in best.items():
            combined = covered | candidate_coverage
            if combined == covered:
                continue
            proposal = (*selection, candidate)
            prior = updated.get(combined)
            if prior is None or score(proposal) < score(prior):
                updated[combined] = proposal
        best = updated
    selected = best.get(target_set)
    if selected is None:
        raise BoundedSensoryCoverageError(
            f"radius <= {MAX_RADIUS_LATTICE_STEPS} cannot cover all {side} bodies."
        )
    selected = tuple(sorted(selected, key=lambda item: tuple(item["centre_hex"])))
    return selected, {
        "side": side,
        "source_centre_count": len(centers),
        "candidate_disks_evaluated": len(centers) * MAX_RADIUS_LATTICE_STEPS,
        "nonempty_unique_coverage_masks": len(candidates),
        "selected_disks": len(selected),
    }


def compute_coverage_plan(
    sample_artifact: Mapping[str, Any],
    phase7h_artifact: LoadedPopulationArtifact,
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create and hash a coverage battery using source anatomy, before dynamics."""
    sample = _as_input(sample_artifact)
    sample_config = sample.get("config", {})
    sample_result = sample.get("result", {})
    expected_sample_config, expected_sample_result = select_bounded_sample(
        source, circuit
    )
    if (
        sample.get("artifact_id") != CANONICAL_SAMPLE_ID
        or sample_config != expected_sample_config
        or sample_result != expected_sample_result
        or phase7h_artifact.artifact_id != CANONICAL_PHASE7H_ID
    ):
        raise BoundedSensoryCoverageError(
            "canonical Phase 7H source pair failed validation."
        )

    initial_coverage = _initial_body_coverage(phase7h_artifact, sample_result)
    uncovered = [
        row["body_id"] for row in initial_coverage if not row["body_stimulus_covered"]
    ]
    if not uncovered:
        raise BoundedSensoryCoverageError(
            "Phase 7H already has full stimulus coverage; Phase 7I plan is unnecessary."
        )
    records_by_body, summaries = _selected_body_records(sample_result, source)
    identities = {item["body_id"]: item for item in sample_result["selected_bodies"]}
    extension_candidates: list[dict[str, Any]] = []
    search_summaries = []
    for side in ("L", "R"):
        side_targets = [
            body_id for body_id in uncovered if identities[body_id]["side"] == side
        ]
        selected_for_side, summary = _coverage_candidates_for_side(
            side,
            side_targets,
            records_by_body,
            summaries,
            grid,
        )
        extension_candidates.extend(selected_for_side)
        search_summaries.append(summary)

    extension_stimuli: list[RelativeColumnStimulus] = []
    extension_rows = []
    for item in extension_candidates:
        center = item["centre_hex"]
        side = item["side"]
        radius = item["radius_lattice_steps"]
        stimulus_id = (
            f"coverage_{side.lower()}_{center[0]:02d}_{center[1]:02d}_r{radius}"
        )
        stimulus = RelativeColumnStimulus(
            stimulus_id=stimulus_id,
            side=side,
            centre_hex1=center[0],
            centre_hex2=center[1],
            dt_ms=0.1,
            radii_lattice_steps=(radius,),
        )
        extension_stimuli.append(stimulus)
        extension_rows.append(
            {
                "stimulus_id": stimulus_id,
                **item,
                "centre_was_source_column": True,
                "coverage_basis": "column_overlap_fraction_gt_zero",
            }
        )

    retained_entries = phase7h_artifact.config.get("stimuli", ())
    if not retained_entries or any(
        item.get("sha256") != sha256_bytes(canonical_json_bytes(item.get("config")))
        for item in retained_entries
    ):
        raise BoundedSensoryCoverageError("Phase 7H stimulus identity is malformed.")
    retained_ids = [item["config"]["stimulus_id"] for item in retained_entries]
    extension_ids = [item.stimulus_id for item in extension_stimuli]
    if len(set(retained_ids + extension_ids)) != len(retained_ids + extension_ids):
        raise BoundedSensoryCoverageError("coverage stimulus ID is duplicated.")
    stimuli = [
        {
            "origin": "PHASE7H_RETAINED_UNCHANGED",
            "config": item["config"],
            "sha256": item["sha256"],
        }
        for item in retained_entries
    ]
    stimuli.extend(
        {
            "origin": "PHASE7I_ANATOMY_ONLY_COVERAGE_EXTENSION",
            "config": stimulus.to_dict(),
            "sha256": sha256_bytes(canonical_json_bytes(stimulus.to_dict())),
        }
        for stimulus in extension_stimuli
    )
    source_identity = dict(source.source_identity)
    circuit_identity = {
        "dataset": circuit.provenance.dataset,
        "candidate_id": circuit.candidate.identifier,
        "candidate_version": circuit.candidate.version,
        "file_sha256": dict(circuit.integrity.sha256_by_file),
    }
    config = {
        "schema": PLAN_CONFIG_SCHEMA,
        "artifact_schema": PLAN_ARTIFACT_SCHEMA,
        "plan_method_id": PLAN_METHOD_ID,
        "phase7h_artifact": _artifact_reference(
            phase7h_artifact, "bounded_sensory_population_artifact_v1"
        ),
        "sample_artifact": _artifact_reference(
            sample_artifact, "bounded_sensory_sample_artifact_v1"
        ),
        "source_contract_identity": source_identity,
        "circuit_contract_identity": circuit_identity,
        "column_grid_identity": grid.to_identity_dict(),
        "coverage_metric": "column_overlap_fraction_gt_zero",
        "candidate_centres": "uncovered_selected_bodies_source_columns_only",
        "candidate_radii_lattice_steps": list(range(1, MAX_RADIUS_LATTICE_STEPS + 1)),
        "objective_order": [
            "minimum_number_of_disks",
            "minimum_total_radius",
            "lexicographic_radius_then_source_centre",
        ],
        "model_outcomes_used_for_battery_design": False,
        "stimulus_model_id": "relative_column_expanding_disk_v1",
        "stimuli": stimuli,
    }
    result = {
        "schema": PLAN_RESULT_SCHEMA,
        "body_ids": list(CANONICAL_BODY_IDS),
        "phase7h_stimulus_ids_retained_unchanged": retained_ids,
        "initial_body_coverage": initial_coverage,
        "initial_uncovered_body_ids": uncovered,
        "candidate_search_summary": search_summaries,
        "coverage_extension_stimuli": extension_rows,
        "covered_initially_uncovered_body_ids": sorted(
            {
                body_id
                for item in extension_rows
                for body_id in item["covered_body_ids"]
            },
            key=CANONICAL_BODY_IDS.index,
        ),
        "model_outcomes_used": False,
        "neural_dynamics_computed": False,
        "dn_p01_outputs_read_for_design": False,
        "purpose": "SOFTWARE_PATH_COVERAGE",
    }
    if result["covered_initially_uncovered_body_ids"] != uncovered:
        raise BoundedSensoryCoverageError("selected disk battery failed set coverage.")
    return config, result


def compute_coverage_experiment(
    plan_artifact: Mapping[str, Any],
    sample_artifact: Mapping[str, Any],
    phase7h_artifact: LoadedPopulationArtifact,
    source: RelativeColumnAssignmentSource,
    grid: RelativeColumnGrid,
    circuit: CircuitContract,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replay 7H, then exercise all 16 states and source-derived target routes."""
    plan = _as_input(plan_artifact)
    sample = _as_input(sample_artifact)
    expected_plan_config, expected_plan_result = compute_coverage_plan(
        sample, phase7h_artifact, source, grid, circuit
    )
    if (
        plan.get("artifact_schema") != PLAN_ARTIFACT_SCHEMA
        or plan.get("config") != expected_plan_config
        or plan.get("result") != expected_plan_result
    ):
        raise BoundedSensoryCoverageError("coverage plan failed deterministic replay.")

    sample_result = sample["result"]
    plan_config = plan["config"]
    stimuli = tuple(
        RelativeColumnStimulus.from_dict(item["config"])
        for item in plan_config["stimuli"]
    )
    if tuple(stimulus.stimulus_id for stimulus in stimuli[:6]) != tuple(
        item["config"]["stimulus_id"] for item in phase7h_artifact.config["stimuli"]
    ):
        raise BoundedSensoryCoverageError("Phase 7H stimulus battery was modified.")
    assignment = _assignment_result(sample_result, source, grid, stimuli)
    sensory = _sensory_trajectories(assignment, sample_result)

    for stimulus_id in plan_result_ids(phase7h_artifact.config):
        expected = phase7h_artifact.result["sensory_trajectories_by_stimulus"].get(
            stimulus_id
        )
        if expected != sensory.get(stimulus_id):
            raise BoundedSensoryCoverageError(
                f"Phase 7H sensory trajectory changed for {stimulus_id}."
            )

    routes = _route_set(sample_result, circuit)
    conditions = []
    for stimulus in stimuli:
        trajectories = sensory[stimulus.stimulus_id]
        states = {
            row["body_id"]: [
                sample_row["state_value"] for sample_row in row["state_timeline"]
            ]
            for row in trajectories
        }
        lengths = {len(trace) for trace in states.values()}
        if len(lengths) != 1 or len(lengths) == 0:
            raise BoundedSensoryCoverageError("sensory state grid is inconsistent.")
        interval_count = next(iter(lengths)) - 1
        conditions.append(
            _simulate_condition(
                condition_id=f"phase7i_{stimulus.stimulus_id}",
                pathway_mask="all16",
                active_body_ids=set(CANONICAL_BODY_IDS),
                k=REFERENCE_K_MVEQ_PER_STATE,
                states=states,
                dt_ms=stimulus.dt_ms,
                steps=interval_count,
                routes=routes,
                circuit=circuit,
            )
        )

    _validate_existing_condition_replay(conditions, phase7h_artifact.result)
    coverage_rows = _body_coverage_summary(
        sample_result,
        phase7h_artifact.result,
        assignment,
        sensory,
        conditions,
        [item["stimulus_id"] for item in plan["result"]["coverage_extension_stimuli"]],
    )
    if not all(
        row["body_stimulus_covered"]
        and row["body_state_exercised"]
        and row["body_transfer_exercised"]
        for row in coverage_rows
    ):
        raise BoundedSensoryCoverageError("coverage experiment did not exercise 16/16.")

    config = {
        "schema": EXPERIMENT_CONFIG_SCHEMA,
        "artifact_schema": EXPERIMENT_ARTIFACT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "purpose": "SOFTWARE_PATH_COVERAGE",
        "coverage_plan_artifact": _artifact_reference(plan, PLAN_ARTIFACT_SCHEMA),
        "phase7h_artifact": _artifact_reference(
            phase7h_artifact, "bounded_sensory_population_artifact_v1"
        ),
        "sample_artifact": _artifact_reference(
            sample, "bounded_sensory_sample_artifact_v1"
        ),
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": plan_config["circuit_contract_identity"],
        "column_grid_identity": grid.to_identity_dict(),
        "body_ids": list(CANONICAL_BODY_IDS),
        "stimulus_model_id": "relative_column_expanding_disk_v1",
        "stimuli": plan_config["stimuli"],
        "sensory_model": phase7h_artifact.config["sensory_model"],
        "transfer_model": phase7h_artifact.config["transfer_model"],
        "dnp01_model": phase7h_artifact.config["dnp01_model"],
        "route_contract": phase7h_artifact.config["route_contract"],
        "time_alignment": "sensory_state_boundary_n_drives_interval_n_to_n_plus_1",
        "model_outcomes_used_for_stimulus_design": False,
        "scientific_boundary": {
            "purpose_is_software_path_coverage": True,
            "absolute_visual_angle_present": False,
            "functional_receptive_field_claim": False,
            "biological_response_claim": False,
            "structural_count_is_physiological_weight": False,
            "sensory_state_is_exploratory": True,
            "transfer_coefficient_is_model_assumption": True,
            "behavior_or_body_mechanics": False,
        },
    }
    result = {
        "schema": EXPERIMENT_RESULT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "purpose": "SOFTWARE_PATH_COVERAGE",
        "sample_artifact_id": CANONICAL_SAMPLE_ID,
        "phase7h_artifact_id": CANONICAL_PHASE7H_ID,
        "coverage_plan_artifact_id": plan["artifact_id"],
        "body_ids": list(CANONICAL_BODY_IDS),
        "assignment": assignment,
        "sensory_trajectories_by_stimulus": sensory,
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
            "denominator": 16,
        },
        "old_phase7h_stimuli_and_sensory_trajectories_unchanged": True,
        "contribution_accounting_validated": True,
        "result_semantics": "EXPLORATORY_16_BODY_SOFTWARE_PATH_COVERAGE",
    }
    return config, result


def plan_result_ids(phase7h_config: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(item["config"]["stimulus_id"] for item in phase7h_config["stimuli"])


def _validate_existing_condition_replay(
    conditions: Sequence[Mapping[str, Any]], phase7h_result: Mapping[str, Any]
) -> None:
    by_id = {item["condition_id"]: item for item in conditions}
    baseline_conditions = {
        "left_expand_33_29": "all16_reference",
        "right_expand_23_09": "all16_reference",
        "sample_l_centroid_expand": "sample_centroid_all16",
        "sample_r_centroid_expand": "sample_centroid_all16",
    }
    phase7h_conditions = {
        item["condition_id"]: item for item in phase7h_result["conditions"]
    }
    for stimulus_id, condition_id in baseline_conditions.items():
        current = by_id.get(f"phase7i_{stimulus_id}")
        baseline = phase7h_conditions[condition_id]
        if current is None:
            raise BoundedSensoryCoverageError("required Phase 7H condition is absent.")
        side = (
            "L"
            if stimulus_id.startswith("left") or stimulus_id.startswith("sample_l")
            else "R"
        )
        target_id = 10010 if side == "L" else 10001
        current_target = next(
            row for row in current["targets"] if row["body_id"] == target_id
        )
        baseline_target = next(
            row for row in baseline["targets"] if row["body_id"] == target_id
        )
        for field in (
            "drive_mveq_by_interval",
            "membrane_mv_by_boundary",
            "filtered_synaptic_mveq_by_boundary",
            "simulated_spikes",
        ):
            if current_target[field] != baseline_target[field]:
                raise BoundedSensoryCoverageError(
                    f"Phase 7H transfer regression changed for {stimulus_id}."
                )


def _body_coverage_summary(
    sample_result: Mapping[str, Any],
    phase7h_result: Mapping[str, Any],
    assignment: Mapping[str, Any],
    sensory: Mapping[str, Sequence[Mapping[str, Any]]],
    conditions: Sequence[Mapping[str, Any]],
    extension_stimulus_ids: Sequence[str],
) -> list[dict[str, Any]]:
    identity = {item["body_id"]: item for item in sample_result["selected_bodies"]}
    h_exposure = {body_id: 0.0 for body_id in CANONICAL_BODY_IDS}
    for sample in phase7h_result["assignment"]["samples"]:
        for row in sample["assignments"]:
            h_exposure[row["body_id"]] = max(
                h_exposure[row["body_id"]], row["column_overlap_fraction"]
            )
    h_state = {body_id: 0.0 for body_id in CANONICAL_BODY_IDS}
    for trajectories in phase7h_result["sensory_trajectories_by_stimulus"].values():
        for row in trajectories:
            h_state[row["body_id"]] = max(
                h_state[row["body_id"]], row["peak_exploratory_state"]
            )
    h_transfer = {body_id: 0.0 for body_id in CANONICAL_BODY_IDS}
    h_reference_conditions = {
        "all16_reference",
        "sample_centroid_all16",
    }
    for condition in phase7h_result["conditions"]:
        if condition["condition_id"] not in h_reference_conditions:
            continue
        for interval in condition["source_contributions_by_interval"]:
            for row in interval["contributions"]:
                h_transfer[row["source_body_id"]] = max(
                    h_transfer[row["source_body_id"]], row["model_drive_mveq"]
                )

    exposure_by_stimulus: dict[str, dict[int, float]] = defaultdict(dict)
    for sample in assignment["samples"]:
        for row in sample["assignments"]:
            exposure_by_stimulus[sample["stimulus_id"]][row["body_id"]] = row[
                "column_overlap_fraction"
            ]
    state_by_stimulus: dict[str, dict[int, Mapping[str, Any]]] = {
        stimulus_id: {row["body_id"]: row for row in rows}
        for stimulus_id, rows in sensory.items()
    }
    transfer_by_stimulus: dict[str, dict[int, float]] = defaultdict(
        lambda: dict.fromkeys(CANONICAL_BODY_IDS, 0.0)
    )
    for condition in conditions:
        stimulus_id = condition["condition_id"].removeprefix("phase7i_")
        for interval in condition["source_contributions_by_interval"]:
            for row in interval["contributions"]:
                body_id = row["source_body_id"]
                transfer_by_stimulus[stimulus_id][body_id] = max(
                    transfer_by_stimulus[stimulus_id][body_id],
                    row["model_drive_mveq"],
                )

    rows = []
    extension_id_set = set(extension_stimulus_ids)
    for body_id in CANONICAL_BODY_IDS:
        values = [
            (stimulus_id, stimulus_rows.get(body_id, 0.0))
            for stimulus_id, stimulus_rows in exposure_by_stimulus.items()
        ]
        positive = [
            (stimulus_id, value) for stimulus_id, value in values if value > 0.0
        ]
        if not positive:
            raise BoundedSensoryCoverageError(
                f"body {body_id} has no positive exposure."
            )
        first_stimulus = positive[0][0]
        most_stimulus = max(values, key=lambda item: item[1])[0]
        max_extension_state = max(
            (
                (stimulus_id, row["peak_exploratory_state"])
                for stimulus_id, per_body in state_by_stimulus.items()
                if (row := per_body[body_id]) is not None
            ),
            key=lambda item: item[1],
        )
        max_transfer = max(
            (
                (stimulus_id, per_body[body_id])
                for stimulus_id, per_body in transfer_by_stimulus.items()
            ),
            key=lambda item: item[1],
        )
        extension_exposure = max(
            (
                stimulus_rows.get(body_id, 0.0)
                for stimulus_id, stimulus_rows in exposure_by_stimulus.items()
                if stimulus_id in extension_id_set
            ),
            default=0.0,
        )
        extension_state = max(
            (
                state_by_stimulus[stimulus_id][body_id]["peak_exploratory_state"]
                for stimulus_id in extension_id_set
            ),
            default=0.0,
        )
        extension_transfer = max(
            (
                transfer_by_stimulus[stimulus_id][body_id]
                for stimulus_id in extension_id_set
            ),
            default=0.0,
        )
        extended_exposure = max(value for _, value in values)
        extended_state = max(h_state[body_id], max_extension_state[1])
        extended_transfer = max(h_transfer[body_id], max_transfer[1])
        rows.append(
            {
                "body_id": body_id,
                "neuron_type": identity[body_id]["neuron_type"],
                "side": identity[body_id]["side"],
                "dnp01_target_body_id": identity[body_id]["target_body_id"],
                "phase7h_max_column_overlap_fraction": h_exposure[body_id],
                "phase7h_max_exploratory_sensory_state": h_state[body_id],
                "phase7h_max_transfer_contribution_across_state_trajectories_mveq": (
                    h_state[body_id] * REFERENCE_K_MVEQ_PER_STATE
                ),
                "phase7h_max_reference_transfer_contribution_mveq": h_transfer[body_id],
                "phase7h_transfer_exercised_in_persisted_reference_conditions": (
                    h_transfer[body_id] > 0.0
                ),
                "phase7i_max_column_overlap_fraction": extended_exposure,
                "phase7i_coverage_extension_max_column_overlap_fraction": (
                    extension_exposure
                ),
                "phase7i_max_exploratory_sensory_state": max_extension_state[1],
                "phase7i_peak_state_stimulus_id": max_extension_state[0],
                "phase7i_max_transfer_contribution_mveq": max_transfer[1],
                "phase7i_peak_transfer_stimulus_id": max_transfer[0],
                "phase7i_coverage_extension_max_exploratory_state": extension_state,
                "phase7i_coverage_extension_max_transfer_contribution_mveq": (
                    extension_transfer
                ),
                "first_nonzero_exposure_stimulus_id": first_stimulus,
                "most_exercising_stimulus_id": most_stimulus,
                "body_stimulus_covered": extended_exposure > 0.0,
                "body_state_exercised": extended_state > 0.0,
                "body_transfer_exercised": extended_transfer > 0.0,
                "coverage_metric_semantics": "SOFTWARE_EXPERIMENT_COVERAGE_ONLY",
            }
        )
    return rows


def replay_inputs(
    sample_path: str = str(PHASE7H_SAMPLE_ROOT / CANONICAL_SAMPLE_ID),
    phase7h_path: str = str(PHASE7H_EXPERIMENT_ROOT / CANONICAL_PHASE7H_ID),
    *,
    source_root: str = str(DEFAULT_SOURCE_ROOT),
    workbook_path: str = str(DEFAULT_WORKBOOK),
) -> tuple[LoadedSampleArtifact, LoadedPopulationArtifact, Any, Any, CircuitContract]:
    sample = replay_sample_artifact(
        sample_path, source_root=source_root, workbook_path=workbook_path
    )
    phase7h = replay_population_artifact(
        phase7h_path,
        sample_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    source, grid, circuit = make_source_bundle(source_root, workbook_path)
    return sample, phase7h, source, grid, circuit
