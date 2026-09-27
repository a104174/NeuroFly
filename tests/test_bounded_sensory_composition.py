"""Phase 7K simultaneous A∪B composition and replay regression tests."""

from __future__ import annotations

import shutil
from collections import Counter

import pytest

from neurofly.bounded_sensory_composition import (
    CANONICAL_BATTERY_IDS,
    CANONICAL_SAMPLE_B_ID,
    COMPOSITION_ARTIFACT_SCHEMA,
    DEFAULT_COMPOSITION_ROOT,
    DEFAULT_COVERAGE_B_ARTIFACT,
    DEFAULT_PHASE7J_ARTIFACT,
    DEFAULT_POPULATION32_ROOT,
    SAMPLE_SIZE,
    _assert_contribution_accounting,
    compose_samples,
    composition_artifact_id,
    compute_population32_experiment,
)
from neurofly.bounded_sensory_composition_artifacts import (
    BoundedSensoryCompositionArtifactError,
    load_composition_artifact,
    load_population32_artifact,
    replay_population32_artifact,
)
from neurofly.bounded_sensory_robustness import (
    CANONICAL_SAMPLE_A_ID,
    DEFAULT_PHASE7H_PATH,
    DEFAULT_PHASE7I_EXPERIMENT_PATH,
    DEFAULT_PHASE7I_PLAN_PATH,
    DEFAULT_SAMPLE_A_PATH,
    compute_sample_b_coverage_plan,
    compute_sample_b_experiment,
    replay_canonical_baselines,
    select_independent_sample,
)
from neurofly.bounded_sensory_robustness_artifacts import (
    load_sample_b_artifact,
    load_sample_b_experiment_artifact,
    load_sample_b_plan_artifact,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT, DEFAULT_WORKBOOK
from neurofly.relative_column_dnp01_transfer import Route, route_population_drive

SAMPLE_A_BODY_IDS = {
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
}
SAMPLE_B_BODY_IDS = {
    31308,
    516909,
    81112,
    518439,
    19954,
    20808,
    26112,
    23929,
    111903,
    27399,
    29702,
    18936,
    25316,
    29598,
    24268,
    33185,
}

SOURCE_AVAILABLE = all(
    path.exists()
    for path in (
        DEFAULT_SOURCE_ROOT,
        DEFAULT_WORKBOOK,
        DEFAULT_SAMPLE_A_PATH,
        DEFAULT_PHASE7H_PATH,
        DEFAULT_PHASE7I_PLAN_PATH,
        DEFAULT_PHASE7I_EXPERIMENT_PATH,
        DEFAULT_COVERAGE_B_ARTIFACT,
        DEFAULT_PHASE7J_ARTIFACT,
    )
)


@pytest.fixture(scope="module")
def phase7k_run():
    if not SOURCE_AVAILABLE:
        pytest.skip("pinned Phase 7A–7J local artifacts are unavailable")
    sample_a, phase7h, phase7i_plan, phase7i_experiment, source, grid, circuit = (
        replay_canonical_baselines()
    )
    sample_b = load_sample_b_artifact(
        DEFAULT_SOURCE_ROOT / "bounded_sensory_sample_b_v1" / CANONICAL_SAMPLE_B_ID
    )
    coverage_b = load_sample_b_plan_artifact(DEFAULT_COVERAGE_B_ARTIFACT)
    experiment_b = load_sample_b_experiment_artifact(DEFAULT_PHASE7J_ARTIFACT)

    b_config, b_result = select_independent_sample(source, circuit, sample_a.as_input())
    assert sample_b.artifact_id == CANONICAL_SAMPLE_B_ID
    assert (b_config, b_result) == (sample_b.config, sample_b.result)
    plan_config, plan_result = compute_sample_b_coverage_plan(
        sample_b.as_input(),
        sample_a,
        phase7h,
        phase7i_plan,
        phase7i_experiment,
        source,
        grid,
        circuit,
    )
    assert (plan_config, plan_result) == (coverage_b.config, coverage_b.result)
    exp_config, exp_result = compute_sample_b_experiment(
        sample_b.as_input(),
        coverage_b.as_input(),
        sample_a,
        phase7h,
        phase7i_plan,
        phase7i_experiment,
        source,
        grid,
        circuit,
    )
    assert (exp_config, exp_result) == (experiment_b.config, experiment_b.result)

    composition_config, composition_result = compose_samples(
        sample_a, sample_b, source, circuit
    )
    composition_id = composition_artifact_id(composition_config, composition_result)
    composition = {
        "artifact_schema": COMPOSITION_ARTIFACT_SCHEMA,
        "artifact_id": composition_id,
        "config": composition_config,
        "result": composition_result,
    }
    config, result = compute_population32_experiment(
        composition,
        sample_a,
        phase7h,
        phase7i_plan,
        phase7i_experiment,
        sample_b,
        coverage_b,
        experiment_b,
        source,
        grid,
        circuit,
    )
    return {
        "sample_a": sample_a,
        "sample_b": sample_b,
        "phase7h": phase7h,
        "phase7i_plan": phase7i_plan,
        "phase7i_experiment": phase7i_experiment,
        "coverage_b": coverage_b,
        "experiment_b": experiment_b,
        "source": source,
        "grid": grid,
        "circuit": circuit,
        "composition": composition,
        "composition_config": composition_config,
        "composition_result": composition_result,
        "config": config,
        "result": result,
    }


def _condition(result, condition_id):
    return next(
        item for item in result["conditions"] if item["condition_id"] == condition_id
    )


def _target(condition, body_id):
    return next(item for item in condition["targets"] if item["body_id"] == body_id)


def test_sample_c_is_exact_persisted_disjoint_union(phase7k_run):
    run = phase7k_run
    a = run["sample_a"]
    b = run["sample_b"]
    union = run["composition_result"]
    assert a.artifact_id == CANONICAL_SAMPLE_A_ID
    assert b.artifact_id == CANONICAL_SAMPLE_B_ID
    assert set(a.result["body_ids"]) == SAMPLE_A_BODY_IDS
    assert set(b.result["body_ids"]) == SAMPLE_B_BODY_IDS
    assert set(a.result["body_ids"]).isdisjoint(b.result["body_ids"])
    assert union["sample_a_sample_b_overlap_count"] == 0
    assert union["sample_a_sample_b_disjoint"] is True
    assert set(union["body_ids"]) == SAMPLE_A_BODY_IDS | SAMPLE_B_BODY_IDS
    assert len(union["body_ids"]) == SAMPLE_SIZE
    assert [row["count"] for row in union["stratum_counts"]] == [8, 8, 8, 8]
    assert Counter(
        row["target_body_id"] for row in run["composition_config"]["route_contract"]
    ) == {
        10001: 16,
        10010: 16,
    }
    again = compose_samples(a, b, run["source"], run["circuit"])
    assert again == (run["composition_config"], union)
    assert composition_artifact_id(*again) == run["composition"]["artifact_id"]
    assert run["composition_config"]["composition_method"] == "DISJOINT_ARTIFACT_UNION"
    assert run["composition_config"]["selection_or_filtering_used_outcomes"] is False


def test_canonical_14_battery_covers_all_32_before_dynamics(phase7k_run):
    result = phase7k_run["result"]
    assert result["config_stimulus_ids"] == list(CANONICAL_BATTERY_IDS)
    assert len(result["config_stimulus_ids"]) == 14
    assert result["assignment"]["sample_count"] == 26
    assert result["coverage_totals"] == {
        "body_stimulus_covered": 32,
        "body_state_exercised": 32,
        "body_transfer_exercised": 32,
        "denominator": 32,
    }
    assert all(row["body_stimulus_covered"] for row in result["anatomical_coverage"])
    assert all(row["body_state_exercised"] for row in result["body_coverage"])
    assert all(row["body_transfer_exercised"] for row in result["body_coverage"])
    assert len(result["conditions"]) == 25


def test_nested_sample_results_and_union_additivity_are_exact(phase7k_run):
    result = phase7k_run["result"]
    regression = result["nested_regression"]
    assert regression["sample_a_state_trace_comparisons"] == 160
    assert regression["sample_b_state_trace_comparisons"] == 224
    assert regression["sample_a_transfer_source_step_comparisons"] == 1952
    assert regression["sample_b_transfer_source_step_comparisons"] == 2656
    assert result["per_step_A_B_target_additivity"]["passed"] is True
    assert result["per_step_A_B_target_additivity"]["target_step_comparisons"] == 244
    assert [
        row["identical_to_canonical_reference"]
        for row in regression["sample_a_only_and_sample_b_only_reference"]
    ] == [True, True]
    _assert_contribution_accounting(result["conditions"])


def test_controls_sensitivity_and_same_side_routing(phase7k_run):
    result = phase7k_run["result"]
    config = phase7k_run["config"]
    assert config["sensitivity_k_transfer_mveq_per_state"] == [0.0, 0.5, 1.0, 2.0]
    assert {row["condition_id"] for row in result["conditions"]} >= {
        "k_zero",
        "no_sources",
        "lc4_only",
        "lplc2_only",
        "left_only",
        "right_only",
        "sample_a_only",
        "sample_b_only",
        "all32_reference",
        "sensitivity_k_0_5",
        "sensitivity_k_2",
    }
    for condition_id in ("k_zero", "no_sources"):
        for target in _condition(result, condition_id)["targets"]:
            assert set(target["drive_mveq_by_interval"]) == {0.0}
            assert set(target["membrane_mv_by_boundary"]) == {-52.0}
    left = _condition(result, "left_only")
    right = _condition(result, "right_only")
    assert set(_target(left, 10001)["drive_mveq_by_interval"]) == {0.0}
    assert set(_target(right, 10010)["drive_mveq_by_interval"]) == {0.0}
    reference = _condition(result, "all32_reference")
    assert all(not target["simulated_spikes"] for target in reference["targets"])
    assert all(
        route["side"] == ("R" if route["target_body_id"] == 10001 else "L")
        for route in config["route_contract"]
    )


def test_structural_weight_metadata_does_not_change_32_body_transfer(phase7k_run):
    run = phase7k_run
    result = run["result"]
    identities = {
        row["body_id"]: row for row in run["composition_result"]["selected_bodies"]
    }
    routes = [
        Route(
            source_body_id=row["source_body_id"],
            target_body_id=row["target_body_id"],
            structural_weight=identities[row["source_body_id"]]["structural_weight"],
            source_type=identities[row["source_body_id"]]["neuron_type"],
            side=identities[row["source_body_id"]]["side"],
        )
        for row in run["config"]["route_contract"]
    ]
    changed_routes = [
        Route(
            route.source_body_id,
            route.target_body_id,
            route.structural_weight + 1000,
            route.source_type,
            route.side,
        )
        for route in routes
    ]
    trajectory = result["sensory_trajectories_by_stimulus"][CANONICAL_BATTERY_IDS[0]]
    states = {
        row["body_id"]: max(item["state_value"] for item in row["state_timeline"])
        for row in trajectory
    }
    active_ids = set(states)
    base = route_population_drive(
        states,
        routes,
        target_body_ids=(10001, 10010),
        active_source_ids=active_ids,
        k_transfer_mveq_per_state=1.0,
    )
    changed = route_population_drive(
        states,
        changed_routes,
        target_body_ids=(10001, 10010),
        active_source_ids=active_ids,
        k_transfer_mveq_per_state=1.0,
    )
    assert base == changed


def test_persisted_phase7k_artifacts_and_full_replay(tmp_path):
    composition_path = DEFAULT_COMPOSITION_ROOT / (
        "82ebef1acef2415fd57b9922e815e87e2d60fd76070a93e67103e2f3924198bf"
    )
    experiment_path = DEFAULT_POPULATION32_ROOT / (
        "b6be84a66d3cecde3e7bf05992515dc31521a8ebc5e8feebadf9b5f0560d9405"
    )
    composition = load_composition_artifact(composition_path)
    experiment = load_population32_artifact(experiment_path)
    assert composition.result["sample_a_sample_b_overlap_count"] == 0
    assert (
        experiment.artifact_id
        == "b6be84a66d3cecde3e7bf05992515dc31521a8ebc5e8feebadf9b5f0560d9405"
    )
    replayed = replay_population32_artifact(experiment_path, composition_path)
    assert replayed.artifact_id == experiment.artifact_id
    assert replayed.result == experiment.result

    tampered = tmp_path / "tampered-population32"
    shutil.copytree(experiment_path, tampered)
    result_path = tampered / "population32_result.json"
    result_path.write_bytes(result_path.read_bytes() + b" ")
    with pytest.raises(BoundedSensoryCompositionArtifactError):
        load_population32_artifact(tampered)
