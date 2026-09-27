"""Phase 7O: direct-source, all-311 exploratory execution (offline only)."""

from __future__ import annotations

import math
import time
from collections import Counter
from typing import Any

from neurofly.bounded_sensory_composition import _add_source_annotations
from neurofly.bounded_sensory_population import (
    _assignment_result,
    _body_index,
    _condition_states,
    _sensory_trajectories,
    _simulate_condition,
)
from neurofly.bounded_sensory_scale128 import (
    CANONICAL_EXPERIMENT128_ID,
    scale128_artifact_path,
)
from neurofly.bounded_sensory_scale128_artifacts import load_scale128_artifact
from neurofly.relative_column_assignment import RelativeColumnStimulus
from neurofly.relative_column_dnp01_transfer import Route, route_population_drive
from neurofly.relative_column_sensory_artifacts import (
    DEFAULT_OUTPUT_ROOT as PHASE7E_OUTPUT_ROOT,
)
from neurofly.relative_column_sensory_artifacts import (
    load_relative_column_sensory_artifact,
)
from neurofly.sensory_population_readiness import (
    POPULATION_SIZE,
    REFERENCE_K_MVEQ_PER_STATE,
    TARGET_IDS,
    _artifact_ref,
    _circuit_identity,
    build_execution_dry_run,
    build_full_population_plan,
    replay_full_coverage_plan,
)

CONFIG_SCHEMA = "sensory_population_311_experiment_config_v1"
RESULT_SCHEMA = "sensory_population_311_experiment_result_v1"
ARTIFACT_SCHEMA = "sensory_population_311_experiment_artifact_v1"
PHASE7E_SENTINEL_ARTIFACT_ID = (
    "09a3d3ddc02c81bb5ea229bf48b76811123ebd2e20cfce17f45e72442dcb8b15"
)


class SensoryPopulationExecutionError(ValueError):
    """An all-311 source, model, routing, or regression invariant failed."""


def _input(artifact: Any) -> dict[str, Any]:
    return artifact.as_input() if hasattr(artifact, "as_input") else dict(artifact)


def _assert_sources(
    population: Any, coverage: Any, dry_run: Any, source: Any, circuit: Any, grid: Any
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    population, coverage, dry_run = map(_input, (population, coverage, dry_run))
    if (population["config"], population["result"]) != build_full_population_plan(
        source, circuit, grid
    ):
        raise SensoryPopulationExecutionError("population failed direct source replay")
    if (coverage["config"], coverage["result"]) != replay_full_coverage_plan(
        population, coverage, source, circuit, grid
    ):
        raise SensoryPopulationExecutionError("coverage failed anatomy-only replay")
    if (dry_run["config"], dry_run["result"]) != build_execution_dry_run(
        population, coverage, source, circuit
    ):
        raise SensoryPopulationExecutionError("execution manifest failed replay")
    return population, coverage, dry_run


def _routes(population: dict[str, Any], source: Any, circuit: Any) -> tuple[Route, ...]:
    source_rows, _ = _body_index(source, circuit)
    rows = population["result"]["bodies"]
    routes = []
    for row in rows:
        body_id = row["body_id"]
        pinned = source_rows[body_id]
        if (
            row["neuron_type"] != pinned["neuron_type"]
            or row["side"] != pinned["side"]
            or row["target_body_id"] != pinned["target_body_id"]
            or row["structural_edge_count"] != pinned["structural_weight"]
        ):
            raise SensoryPopulationExecutionError(f"source route changed for {body_id}")
        routes.append(
            Route(
                body_id,
                pinned["target_body_id"],
                pinned["structural_weight"],
                pinned["neuron_type"],
                pinned["side"],
            )
        )
    routes = tuple(sorted(routes, key=lambda row: row.source_body_id))
    if len(routes) != POPULATION_SIZE or Counter(
        r.target_body_id for r in routes
    ) != Counter({10001: 146, 10010: 165}):
        raise SensoryPopulationExecutionError("311 routes/targets are incomplete")
    return routes


def _coverage(
    assignment: dict[str, Any],
    trajectories: dict[str, Any],
    conditions: list[dict[str, Any]],
    population: dict[str, Any],
) -> list[dict[str, Any]]:
    ids = population["result"]["body_ids"]
    maxima = {body_id: [0.0, 0.0, 0.0] for body_id in ids}
    for sample in assignment["samples"]:
        for row in sample["assignments"]:
            maxima[row["body_id"]][0] = max(
                maxima[row["body_id"]][0], row["column_overlap_fraction"]
            )
    for rows in trajectories.values():
        for row in rows:
            maxima[row["body_id"]][1] = max(
                maxima[row["body_id"]][1], row["peak_exploratory_state"]
            )
    for condition in conditions:
        if not condition["condition_id"].startswith("stimulus::"):
            continue
        for interval in condition["source_contributions_by_interval"]:
            for row in interval["contributions"]:
                body_id = row["source_body_id"]
                maxima[body_id][2] = max(maxima[body_id][2], row["model_drive_mveq"])
    rows = [
        {
            "body_id": body_id,
            "maximum_column_overlap_fraction": values[0],
            "maximum_exploratory_state": values[1],
            "maximum_transfer_contribution_mveq": values[2],
            "body_stimulus_covered": values[0] > 0,
            "body_state_exercised": values[1] > 0,
            "body_transfer_exercised": values[2] > 0,
        }
        for body_id, values in sorted(maxima.items())
    ]
    if any(
        not all(
            row[key]
            for key in (
                "body_stimulus_covered",
                "body_state_exercised",
                "body_transfer_exercised",
            )
        )
        for row in rows
    ):
        raise SensoryPopulationExecutionError(
            "311/311 non-zero model-path coverage failed"
        )
    return rows


def _assert_accounting(conditions: list[dict[str, Any]], expected_rows: int) -> None:
    total = 0
    for condition in conditions:
        targets = {row["body_id"]: row for row in condition["targets"]}
        for interval in condition["source_contributions_by_interval"]:
            step = interval["step"]
            contributions = interval["contributions"]
            if len(contributions) != POPULATION_SIZE:
                raise SensoryPopulationExecutionError(
                    "source contribution ledger is incomplete"
                )
            total += len(contributions)
            for target in TARGET_IDS:
                amount = sum(
                    row["model_drive_mveq"]
                    for row in contributions
                    if row["target_body_id"] == target
                )
                if not math.isclose(
                    amount,
                    targets[target]["drive_mveq_by_interval"][step],
                    rel_tol=0,
                    abs_tol=max(
                        1e-15,
                        POPULATION_SIZE
                        * math.ulp(targets[target]["drive_mveq_by_interval"][step])
                        * 2,
                    ),
                ):
                    raise SensoryPopulationExecutionError(
                        "per-step source accounting failed"
                    )
    if total != expected_rows:
        raise SensoryPopulationExecutionError(
            "ledger row count differs from Phase 7N manifest"
        )


def _nested_128(
    trajectories: dict[str, Any],
    conditions: list[dict[str, Any]],
    routes: tuple[Route, ...],
    circuit: Any,
    timings: dict[str, float],
) -> dict[str, Any]:
    old = load_scale128_artifact(
        scale128_artifact_path("experiment", CANONICAL_EXPERIMENT128_ID), "experiment"
    )
    old_ids = set(old.result["body_ids"])
    old_conditions = {row["condition_id"]: row for row in old.result["conditions"]}
    now_conditions = {row["condition_id"]: row for row in conditions}
    common = list(old.result["sensory_trajectories_by_stimulus"])
    state_checks = contribution_checks = target_checks = 0
    for stimulus_id in common:
        old_rows = {
            row["body_id"]: row
            for row in old.result["sensory_trajectories_by_stimulus"][stimulus_id]
        }
        new_rows = {row["body_id"]: row for row in trajectories[stimulus_id]}
        for body_id in old_ids:
            if new_rows[body_id] != old_rows[body_id]:
                raise SensoryPopulationExecutionError(
                    f"128-body state regression at {stimulus_id}/{body_id}"
                )
            state_checks += 1
        old_condition = old_conditions[f"stimulus::{stimulus_id}"]
        new_condition = now_conditions[f"stimulus::{stimulus_id}"]
        for new_interval, old_interval in zip(
            new_condition["source_contributions_by_interval"],
            old_condition["source_contributions_by_interval"],
            strict=True,
        ):
            restricted = {
                row["source_body_id"]: row
                for row in new_interval["contributions"]
                if row["source_body_id"] in old_ids
            }
            baseline = {
                row["source_body_id"]: row for row in old_interval["contributions"]
            }
            if restricted != baseline:
                raise SensoryPopulationExecutionError(
                    f"128-body transfer regression at {stimulus_id}"
                )
            contribution_checks += len(old_ids)
        states = {
            body_id: [point["state_value"] for point in row["state_timeline"]]
            for body_id, row in new_rows.items()
        }
        restricted_condition = _simulate_condition(
            condition_id=f"regression128::{stimulus_id}",
            pathway_mask="all_population",
            active_body_ids=old_ids,
            k=REFERENCE_K_MVEQ_PER_STATE,
            states=states,
            dt_ms=new_condition["dt_ms"],
            steps=new_condition["interval_count"],
            routes=routes,
            circuit=circuit,
        )
        for target in TARGET_IDS:
            actual = next(
                row
                for row in restricted_condition["targets"]
                if row["body_id"] == target
            )
            expected = next(
                row for row in old_condition["targets"] if row["body_id"] == target
            )
            for key in (
                "drive_mveq_by_interval",
                "membrane_mv_by_boundary",
                "filtered_synaptic_mveq_by_boundary",
                "simulated_spikes",
            ):
                if actual[key] != expected[key]:
                    raise SensoryPopulationExecutionError(
                        f"128-body DNp01 regression at {stimulus_id}/{target}/{key}"
                    )
            target_checks += 1
    first_rows = next(iter(trajectories.values()))
    identities = {
        "selected_bodies": [
            {"body_id": row["body_id"], "side": row["side"]} for row in first_rows
        ]
    }
    bilateral_states, bilateral_dt, bilateral_steps = _condition_states(
        trajectories, identities, "left_expand_33_29", "right_expand_23_09"
    )
    masked = _simulate_condition(
        condition_id="phase7m_128_only_regression_control",
        pathway_mask="all_population",
        active_body_ids=old_ids,
        k=REFERENCE_K_MVEQ_PER_STATE,
        states=bilateral_states,
        dt_ms=bilateral_dt,
        steps=bilateral_steps,
        routes=routes,
        circuit=circuit,
    )
    old_reference = next(
        row
        for row in old.result["conditions"]
        if row["condition_id"] == "all128_reference"
    )
    for target in TARGET_IDS:
        actual = next(row for row in masked["targets"] if row["body_id"] == target)
        expected = next(
            row for row in old_reference["targets"] if row["body_id"] == target
        )
        for key in (
            "drive_mveq_by_interval",
            "membrane_mv_by_boundary",
            "filtered_synaptic_mveq_by_boundary",
            "simulated_spikes",
        ):
            if actual[key] != expected[key]:
                raise SensoryPopulationExecutionError(
                    f"128-body bilateral control changed for {target}/{key}"
                )
        target_checks += 1
    return {
        "phase7m_artifact_id": old.artifact_id,
        "common_stimulus_count": len(common),
        "state_trajectory_comparisons": state_checks,
        "per_source_interval_comparisons": contribution_checks,
        "target_timeline_comparisons": target_checks,
        "phase7m_128_only_bilateral_control": {
            "reference_condition_id": "all128_reference",
            "exact_drive_membrane_and_spikes": True,
            "ledger_persisted": False,
        },
        "exact_equality": True,
        "regression_only_not_population_provenance": True,
    }


def _sentinel_regression(trajectories: dict[str, Any]) -> dict[str, Any]:
    baseline = load_relative_column_sensory_artifact(
        PHASE7E_OUTPUT_ROOT / PHASE7E_SENTINEL_ARTIFACT_ID
    )
    comparisons = 0
    for condition in baseline.result["conditions"]:
        stimulus_id = condition["stimulus_id"]
        current = {row["body_id"]: row for row in trajectories[stimulus_id]}
        for row in condition["body_trajectories"]:
            if row["state_timeline"] != current[row["body_id"]]["state_timeline"]:
                raise SensoryPopulationExecutionError(
                    "Phase 7E sentinel trajectory changed at "
                    f"{stimulus_id}/{row['body_id']}"
                )
            comparisons += 1
    return {
        "phase7e_artifact_id": PHASE7E_SENTINEL_ARTIFACT_ID,
        "trajectory_comparisons": comparisons,
        "exact_equality": True,
        "regression_only_not_population_provenance": True,
    }


def execute_311(
    population: Any,
    coverage: Any,
    dry_run: Any,
    source: Any,
    circuit: Any,
    grid: Any,
    *,
    check_nested: bool = True,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, float]]:
    """Run the pinned 7N manifest; timing data is separate from hashed results."""
    started = time.perf_counter()
    population, coverage, dry_run = _assert_sources(
        population, coverage, dry_run, source, circuit, grid
    )
    execution = dry_run["config"]
    body_ids = population["result"]["body_ids"]
    if (
        len(body_ids) != POPULATION_SIZE
        or execution["sensory_model"]["tau_sens_ms"] != 1.0
        or execution["sensory_model"]["gain"] != 1.0
        or execution["sensory_model"]["initial_state"] != 0.0
        or execution["transfer_model"]["k_transfer_mveq_per_state"] != 1.0
        or execution["population_normalization"] != "none"
        or execution["structural_edge_count_numerical_use"]
        != "none_source_metadata_only"
    ):
        raise SensoryPopulationExecutionError("model or population invariant changed")
    selected = {"body_ids": body_ids, "selected_bodies": population["result"]["bodies"]}
    routes = _routes(population, source, circuit)
    stimuli = tuple(
        RelativeColumnStimulus.from_dict(item["config"])
        for item in coverage["config"]["stimuli"]
    )
    timings: dict[str, float] = {
        "source_and_config_validation_seconds": time.perf_counter() - started
    }
    stage = time.perf_counter()
    assignment = _assignment_result(selected, source, grid, stimuli)
    timings["anatomical_assignment_seconds"] = time.perf_counter() - stage
    stage = time.perf_counter()
    trajectories = _sensory_trajectories(assignment, selected)
    timings["sensory_dynamics_seconds"] = time.perf_counter() - stage
    all_ids = set(body_ids)
    conditions = []
    conditions_started = time.perf_counter()
    for condition_config in execution["conditions"]:
        stimulus_ids = condition_config["stimulus_ids"]
        if len(stimulus_ids) == 1:
            stimulus_id = stimulus_ids[0]
            states = {
                row["body_id"]: [
                    point["state_value"] for point in row["state_timeline"]
                ]
                for row in trajectories[stimulus_id]
            }
            dt_ms = stimuli[0].dt_ms
            steps = len(next(iter(states.values()))) - 1
        else:
            states, dt_ms, steps = _condition_states(
                trajectories, selected, *stimulus_ids
            )
        mask = condition_config["mask"]
        if mask == "all_population":
            active = all_ids
        elif mask == "none":
            active = set()
        elif mask in ("LC4", "LPLC2"):
            active = {
                row["body_id"]
                for row in selected["selected_bodies"]
                if row["neuron_type"] == mask
            }
        elif mask in ("left", "right"):
            side = "L" if mask == "left" else "R"
            active = {
                row["body_id"]
                for row in selected["selected_bodies"]
                if row["side"] == side
            }
        else:
            raise SensoryPopulationExecutionError("unsupported manifest source mask")
        row = _simulate_condition(
            condition_id=condition_config["condition_id"],
            pathway_mask=mask,
            active_body_ids=active,
            k=condition_config["k_transfer_mveq_per_state"],
            states=states,
            dt_ms=dt_ms,
            steps=steps,
            routes=routes,
            circuit=circuit,
            phase_timings=timings,
        )
        body_rows = {body["body_id"]: body for body in selected["selected_bodies"]}
        annotation_started = time.perf_counter()
        _add_source_annotations(row, states, body_rows)
        timings["contribution_annotation_seconds"] = timings.get(
            "contribution_annotation_seconds", 0.0
        ) + (time.perf_counter() - annotation_started)
        conditions.append(row)
    timings["all_conditions_seconds"] = time.perf_counter() - conditions_started
    stage = time.perf_counter()
    _assert_accounting(
        conditions, dry_run["result"]["expected_contribution_ledger_rows"]
    )
    coverage_rows = _coverage(assignment, trajectories, conditions, population)
    timings["validation_seconds"] = time.perf_counter() - stage
    regression_started = time.perf_counter()
    nested = (
        _nested_128(trajectories, conditions, routes, circuit, timings)
        if check_nested
        else {"checked": False}
    )
    sentinels = (
        _sentinel_regression(trajectories) if check_nested else {"checked": False}
    )
    timings["nested_and_sentinel_regression_seconds"] = (
        time.perf_counter() - regression_started
    )
    # Structural contact counts are route metadata, never a numerical multiplier.
    probe = {body_id: 0.25 for body_id in body_ids}
    baseline, _ = route_population_drive(
        probe,
        routes,
        target_body_ids=TARGET_IDS,
        active_source_ids=all_ids,
        k_transfer_mveq_per_state=1.0,
    )
    mutated = tuple(
        Route(
            r.source_body_id,
            r.target_body_id,
            r.structural_weight + 1,
            r.source_type,
            r.side,
        )
        for r in routes
    )
    alternate, _ = route_population_drive(
        probe,
        mutated,
        target_body_ids=TARGET_IDS,
        active_source_ids=all_ids,
        k_transfer_mveq_per_state=1.0,
    )
    if baseline != alternate:
        raise SensoryPopulationExecutionError(
            "structural count affected numerical transfer"
        )
    config = {
        "schema": CONFIG_SCHEMA,
        "artifact_schema": ARTIFACT_SCHEMA,
        "population_artifact": _artifact_ref(population),
        "coverage_artifact": _artifact_ref(coverage),
        "execution_manifest_artifact": _artifact_ref(dry_run),
        "source_contract_identity": dict(source.source_identity),
        "circuit_contract_identity": _circuit_identity(circuit),
        "condition_ids": [row["condition_id"] for row in execution["conditions"]],
        "model_config_sha256": execution["model_config_sha256"],
        "population_normalization": "none",
        "structural_edge_count_numerical_use": "none_source_metadata_only",
        "time_alignment": execution["timing"]["transfer_alignment"],
        "scientific_semantics": "EXPLORATORY_MODEL_STATE_NOT_BIOLOGICAL_VALIDATION",
    }
    result = {
        "schema": RESULT_SCHEMA,
        "body_ids": body_ids,
        "body_count": POPULATION_SIZE,
        "route_contract": [route.to_dict() for route in routes],
        "target_body_ids": list(TARGET_IDS),
        "stimulus_ids": [stimulus.stimulus_id for stimulus in stimuli],
        "assignment": assignment,
        "sensory_trajectories_by_stimulus": trajectories,
        "conditions": conditions,
        "condition_count": len(conditions),
        "body_coverage": coverage_rows,
        "coverage_totals": {
            "body_stimulus_covered": POPULATION_SIZE,
            "body_state_exercised": POPULATION_SIZE,
            "body_transfer_exercised": POPULATION_SIZE,
        },
        "contribution_ledger_row_count": dry_run["result"][
            "expected_contribution_ledger_rows"
        ],
        "nested_128_regression": nested,
        "phase7e_sentinel_regression": sentinels,
        "source_contribution_accounting_validated": True,
        "structural_weight_independence_validated": True,
        "model_output_not_physiology": True,
    }
    timings["total_computation_seconds"] = time.perf_counter() - started
    return config, result, timings
