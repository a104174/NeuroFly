"""Phase 7L four-sample 64-body composition and replay regressions."""

from __future__ import annotations

import json
import shutil
from collections import Counter
from dataclasses import replace

import pytest

from neurofly.bounded_sensory_population import STRATA
from neurofly.bounded_sensory_scale64 import (
    CANONICAL_BATTERY_IDS,
    CANONICAL_COMPOSITION64_ID,
    CANONICAL_EXPERIMENT64_ID,
    CANONICAL_PLAN64_ID,
    CANONICAL_SAMPLE_C_ID,
    CANONICAL_SAMPLE_D_ID,
    DEFAULT_COMPOSITION32_PATH,
    DEFAULT_EXPERIMENT32_PATH,
    DEFAULT_PHASE7H_PATH,
    DEFAULT_PHASE7I_EXPERIMENT_PATH,
    DEFAULT_PHASE7J_PATH,
    DEFAULT_SAMPLE_A_PATH,
    DEFAULT_SAMPLE_B_PATH,
    DEFAULT_SOURCE_ROOT,
    POPULATION64_SIZE,
    SAMPLE_C_ID,
    SAMPLE_D_ID,
    _balanced_quartile_ranks,
    canonical_phase7l_context,
    compose_four_samples,
    compute_population64_experiment,
    make_coverage_plan64,
    scale64_artifact_id,
    select_disjoint_sample,
)
from neurofly.bounded_sensory_scale64_artifacts import (
    BoundedSensoryScale64ArtifactError,
    load_scale64_artifact,
    scale64_artifact_path,
)
from neurofly.relative_column_assignment import DEFAULT_WORKBOOK
from neurofly.relative_column_dnp01_transfer import Route, route_population_drive

SOURCE_AVAILABLE = all(
    path.exists()
    for path in (
        DEFAULT_SOURCE_ROOT,
        DEFAULT_WORKBOOK,
        DEFAULT_SAMPLE_A_PATH,
        DEFAULT_SAMPLE_B_PATH,
        DEFAULT_PHASE7H_PATH,
        DEFAULT_PHASE7I_EXPERIMENT_PATH,
        DEFAULT_PHASE7J_PATH,
        DEFAULT_COMPOSITION32_PATH,
        DEFAULT_EXPERIMENT32_PATH,
        scale64_artifact_path("sample", CANONICAL_SAMPLE_C_ID, sample_label="C"),
        scale64_artifact_path("sample", CANONICAL_SAMPLE_D_ID, sample_label="D"),
        scale64_artifact_path("composition", CANONICAL_COMPOSITION64_ID),
        scale64_artifact_path("plan", CANONICAL_PLAN64_ID),
        scale64_artifact_path("experiment", CANONICAL_EXPERIMENT64_ID),
    )
)


@pytest.fixture(scope="module")
def phase7l_run():
    if not SOURCE_AVAILABLE:
        pytest.skip("pinned Phase 7A–7K and Phase 7L artifacts are unavailable")
    context = canonical_phase7l_context()
    sample_c = load_scale64_artifact(
        scale64_artifact_path("sample", CANONICAL_SAMPLE_C_ID, sample_label="C"),
        "sample",
    )
    sample_d = load_scale64_artifact(
        scale64_artifact_path("sample", CANONICAL_SAMPLE_D_ID, sample_label="D"),
        "sample",
    )
    composition = load_scale64_artifact(
        scale64_artifact_path("composition", CANONICAL_COMPOSITION64_ID),
        "composition",
    )
    plan = load_scale64_artifact(
        scale64_artifact_path("plan", CANONICAL_PLAN64_ID), "plan"
    )
    experiment = load_scale64_artifact(
        scale64_artifact_path("experiment", CANONICAL_EXPERIMENT64_ID), "experiment"
    )

    c_config, c_result = select_disjoint_sample(
        SAMPLE_C_ID,
        [context["sample_a"].as_input(), context["sample_b"].as_input()],
        context["source"],
        context["circuit"],
    )
    assert (c_config, c_result) == (sample_c.config, sample_c.result)
    d_config, d_result = select_disjoint_sample(
        SAMPLE_D_ID,
        [
            context["sample_a"].as_input(),
            context["sample_b"].as_input(),
            sample_c.as_input(),
        ],
        context["source"],
        context["circuit"],
    )
    assert (d_config, d_result) == (sample_d.config, sample_d.result)

    composition_config, composition_result = compose_four_samples(
        [
            context["sample_a"].as_input(),
            context["sample_b"].as_input(),
            sample_c.as_input(),
            sample_d.as_input(),
        ],
        context["source"],
        context["circuit"],
    )
    assert (composition_config, composition_result) == (
        composition.config,
        composition.result,
    )
    plan_config, plan_result = make_coverage_plan64(
        composition.as_input(),
        context["phase7k"],
        context["source"],
        context["grid"],
    )
    assert (plan_config, plan_result) == (plan.config, plan.result)
    experiment_config, experiment_result = compute_population64_experiment(
        composition.as_input(),
        plan.as_input(),
        context["phase7k"],
        context["phase7h"],
        context["phase7i"],
        context["phase7j"],
        context["source"],
        context["grid"],
        context["circuit"],
    )
    assert (experiment_config, experiment_result) == (
        experiment.config,
        experiment.result,
    )
    return {
        **context,
        "sample_c": sample_c,
        "sample_d": sample_d,
        "composition": composition,
        "plan": plan,
        "experiment": experiment,
    }


def test_sample_c_and_d_are_deterministic_balanced_and_outcome_blind(phase7l_run):
    run = phase7l_run
    samples = (run["sample_c"], run["sample_d"])
    earlier_ids = set(run["sample_a"].result["body_ids"])
    earlier_ids.update(run["sample_b"].result["body_ids"])
    assert run["sample_c"].artifact_id == CANONICAL_SAMPLE_C_ID
    assert run["sample_d"].artifact_id == CANONICAL_SAMPLE_D_ID
    for sample in samples:
        assert len(sample.result["body_ids"]) == 16
        assert len(set(sample.result["body_ids"])) == 16
        assert [row["count"] for row in sample.result["stratum_counts"]] == [4] * 4
        assert sample.config["model_outcomes_used"] is False
        assert sample.result["model_outcomes_used"] is False
        assert sample.result["selection_stage_has_neural_dynamics"] is False
        assert set(sample.result["body_ids"]).isdisjoint(earlier_ids)
        earlier_ids.update(sample.result["body_ids"])
        assert all(row["sentinel"] is False for row in sample.result["selected_bodies"])
        assert all(
            row["tie_break"] == "smallest_body_id_among_exact_maximin_ties"
            for row in sample.result["selected_bodies"]
        )
    assert set(STRATA) == {
        (row["neuron_type"], row["side"])
        for row in run["sample_c"].result["stratum_counts"]
    }


def test_balanced_rank_quartiles_are_deterministic_with_discrete_counts():
    rows = [
        {"body_id": body_id, "structural_weight": weight}
        for body_id, weight in ((8, 1), (3, 1), (9, 2), (1, 2), (7, 2), (4, 8), (6, 9))
    ]
    ranks = _balanced_quartile_ranks(rows)
    assert ranks == _balanced_quartile_ranks(tuple(reversed(rows)))
    group_counts = Counter(row["rank_group_zero_based"] for row in ranks.values())
    assert set(group_counts) == {0, 1, 2, 3}
    assert max(group_counts.values()) - min(group_counts.values()) <= 1


def test_four_sample_union_is_pairwise_disjoint_and_route_verified(phase7l_run):
    result = phase7l_run["composition"].result
    assert result["parent_artifact_ids"] == [
        phase7l_run[label].artifact_id
        for label in ("sample_a", "sample_b", "sample_c", "sample_d")
    ]
    assert len(result["body_ids"]) == POPULATION64_SIZE == 64
    assert len(set(result["body_ids"])) == 64
    assert [row["count"] for row in result["stratum_counts"]] == [16] * 4
    assert len(result["pairwise_disjointness"]) == 6
    assert all(row["overlap_count"] == 0 for row in result["pairwise_disjointness"])
    assert result["pairwise_disjoint"] is True
    assert result["target_route_counts"] == [
        {"target_body_id": 10001, "source_count": 32},
        {"target_body_id": 10010, "source_count": 32},
    ]
    assert phase7l_run["composition"].artifact_id == CANONICAL_COMPOSITION64_ID


def test_anatomy_only_coverage_plan_retains_14_and_adds_five_radius_bounded_disks(
    phase7l_run,
):
    plan = phase7l_run["plan"]
    assert plan.artifact_id == CANONICAL_PLAN64_ID
    assert plan.result["initial_stimulus_ids"] == list(CANONICAL_BATTERY_IDS)
    assert len(plan.result["initial_uncovered_body_ids"]) == 12
    assert len(plan.result["coverage_extension_stimuli"]) == 5
    assert plan.config["model_outcomes_used_for_battery_design"] is False
    assert plan.result["neural_dynamics_computed"] is False
    assert all(
        1 <= row["radius_lattice_steps"] <= 4
        and row["centre_is_source_column"]
        and row["coverage_basis"] == "column_overlap_fraction_gt_zero"
        and row["model_outcomes_used"] is False
        for row in plan.result["coverage_extension_stimuli"]
    )
    assert len(plan.config["stimuli"]) == 19
    assert len(plan.result["final_covered_body_ids"]) == 64


def test_64_body_experiment_has_coverage_accounting_nested_checks_and_controls(
    phase7l_run,
):
    experiment = phase7l_run["experiment"]
    result = experiment.result
    assert experiment.artifact_id == CANONICAL_EXPERIMENT64_ID
    assert experiment.config["body_count"] == 64
    assert experiment.config["sensory_model"]["model_id"] == (
        "relative_column_exploratory_sensory_state_v1"
    )
    assert experiment.config["sensory_model"]["tau_sens_ms"] == 1.0
    assert experiment.config["sensory_model"]["gain"] == 1.0
    assert experiment.config["sensory_model"]["initial_state"] == 0.0
    assert experiment.config["sensory_model"]["input_metric_id"] == (
        "column_overlap_fraction"
    )
    assert experiment.config["transfer_model"]["k_transfer_mveq_per_state"] == 1.0
    assert (
        experiment.config["transfer_model"]["structural_weight_used_as_gain"] is False
    )
    assert experiment.config["population_normalization"] == "none"
    assert result["coverage_totals"] == {
        "body_stimulus_covered": 64,
        "body_state_exercised": 64,
        "body_transfer_exercised": 64,
        "denominator": 64,
    }
    assert result["assignment"]["sample_count"] == 31
    assert len(result["conditions"]) == 53
    assert result["source_contribution_accounting_validated"] is True
    assert result["parent_additivity_validated"] is True
    assert result["per_step_source_accounting_comparisons"] == 1304
    assert result["per_step_A_B_C_D_additivity_comparisons"] == 1304
    assert len(result["phase7k_A_B_only_nested_regression"]) == 14
    assert all(
        row["per_source_contributions_identical"]
        and row["dn_p01_drive_membrane_events_identical"]
        for row in result["phase7k_A_B_only_nested_regression"]
    )
    assert result["sample_a_only_and_sample_b_only_reference"] == [
        {"condition_id": "sample_a_only", "identical": True},
        {"condition_id": "sample_b_only", "identical": True},
    ]
    assert result["side_isolation_checks"] > 0
    condition_ids = {row["condition_id"] for row in result["conditions"]}
    assert {
        "k_zero",
        "no_sources",
        "lc4_only",
        "lplc2_only",
        "left_only",
        "right_only",
        "sample_a_only",
        "sample_b_only",
        "sample_c_only",
        "sample_d_only",
        "sample_ab_only",
        "sample_cd_only",
        "all64_reference",
        "sensitivity_k_0_5",
        "sensitivity_k_2",
    } <= condition_ids
    for control_id in ("k_zero", "no_sources"):
        control = next(
            row for row in result["conditions"] if row["condition_id"] == control_id
        )
        for target in control["targets"]:
            assert set(target["drive_mveq_by_interval"]) == {0.0}
            assert set(target["membrane_mv_by_boundary"]) == {-52.0}


def test_structural_edge_count_is_metadata_not_transfer_gain(phase7l_run):
    routes = [
        Route(
            row["body_id"],
            row["target_body_id"],
            row["structural_weight"],
            row["neuron_type"],
            row["side"],
        )
        for row in phase7l_run["composition"].result["selected_bodies"]
    ]
    states = {route.source_body_id: 0.25 for route in routes}
    active = set(states)
    baseline = route_population_drive(
        states,
        routes,
        target_body_ids=(10001, 10010),
        active_source_ids=active,
        k_transfer_mveq_per_state=1.0,
    )
    altered_counts = [
        replace(route, structural_weight=route.structural_weight + 1000)
        for route in routes
    ]
    altered = route_population_drive(
        states,
        altered_counts,
        target_body_ids=(10001, 10010),
        active_source_ids=active,
        k_transfer_mveq_per_state=1.0,
    )
    assert altered == baseline


def test_phase7l_artifact_tampering_is_rejected(phase7l_run, tmp_path):
    original = phase7l_run["composition"]
    copied = tmp_path / original.artifact_id
    shutil.copytree(original.path, copied)
    manifest_path = copied / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifact_id"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BoundedSensoryScale64ArtifactError):
        load_scale64_artifact(copied, "composition")


def test_artifact_ids_are_content_deterministic(phase7l_run):
    composition = phase7l_run["composition"]
    assert scale64_artifact_id(
        "composition", composition.config, composition.result
    ) == (composition.artifact_id)
    assert (
        scale64_artifact_id(
            "experiment",
            phase7l_run["experiment"].config,
            phase7l_run["experiment"].result,
        )
        == phase7l_run["experiment"].artifact_id
    )
