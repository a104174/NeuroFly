"""Phase 7M outcome-blind A–H composition and deterministic replay tests."""

from __future__ import annotations

import json
import shutil
from collections import Counter
from dataclasses import replace

import pytest

from neurofly.bounded_sensory_population import STRATA
from neurofly.bounded_sensory_scale64 import (
    CANONICAL_SAMPLE_C_ID,
    CANONICAL_SAMPLE_D_ID,
)
from neurofly.bounded_sensory_scale128 import (
    CANONICAL_COMPOSITION128_ID,
    CANONICAL_EXPERIMENT128_ID,
    CANONICAL_PLAN128_ID,
    CANONICAL_SAMPLE_IDS,
    NEW_SAMPLE_LABELS,
    POPULATION_SIZE,
    SAMPLE_LABELS,
    canonical_phase7m_context,
    compose_eight_samples,
    compute_population128_experiment,
    make_coverage_plan128,
    scale128_artifact_path,
    select_sample128,
)
from neurofly.bounded_sensory_scale128_artifacts import (
    BoundedSensoryScale128ArtifactError,
    load_scale128_artifact,
)
from neurofly.relative_column_dnp01_transfer import Route, route_population_drive


@pytest.fixture(scope="module")
def phase7m_run():
    context = canonical_phase7m_context()
    samples = {}
    parents = [
        context["sample_a"],
        context["sample_b"],
        context["sample_c"],
        context["sample_d"],
    ]
    for label in NEW_SAMPLE_LABELS:
        artifact = load_scale128_artifact(
            scale128_artifact_path("sample", CANONICAL_SAMPLE_IDS[label], label=label),
            "sample",
        )
        expected = select_sample128(
            label, parents, context["source"], context["circuit"]
        )
        assert (artifact.config, artifact.result) == expected
        samples[label] = artifact
        parents.append(artifact)

    all_samples = [*parents[:4], *(samples[label] for label in NEW_SAMPLE_LABELS)]
    composition = load_scale128_artifact(
        scale128_artifact_path("composition", CANONICAL_COMPOSITION128_ID),
        "composition",
    )
    assert (composition.config, composition.result) == compose_eight_samples(
        all_samples, context["source"], context["circuit"]
    )
    plan = load_scale128_artifact(
        scale128_artifact_path("plan", CANONICAL_PLAN128_ID), "plan"
    )
    assert (plan.config, plan.result) == make_coverage_plan128(
        composition.as_input(),
        context["plan64"],
        context["experiment64"],
        context["source"],
        context["grid"],
    )
    experiment = load_scale128_artifact(
        scale128_artifact_path("experiment", CANONICAL_EXPERIMENT128_ID),
        "experiment",
    )
    assert (experiment.config, experiment.result) == compute_population128_experiment(
        composition.as_input(),
        plan.as_input(),
        context["plan64"],
        context["experiment64"],
        context,
    )
    return {
        **context,
        "samples_eh": samples,
        "composition128": composition,
        "plan128": plan,
        "experiment128": experiment,
    }


def _all_sample_artifacts(run):
    return [
        run["sample_a"],
        run["sample_b"],
        run["sample_c"],
        run["sample_d"],
        *(run["samples_eh"][label] for label in NEW_SAMPLE_LABELS),
    ]


def test_e_through_h_selection_is_deterministic_blind_and_pairwise_disjoint(
    phase7m_run,
):
    artifacts = _all_sample_artifacts(phase7m_run)
    ids_by_label = {}
    used = set()
    for label, artifact in zip(SAMPLE_LABELS, artifacts, strict=True):
        ids = artifact.result["body_ids"]
        ids_by_label[label] = set(ids)
        assert len(ids) == 16
        assert len(set(ids)) == 16
        assert [row["count"] for row in artifact.result["stratum_counts"]] == [4] * 4
        assert not (set(ids) & used)
        used.update(ids)
        if label in NEW_SAMPLE_LABELS:
            assert artifact.artifact_id == CANONICAL_SAMPLE_IDS[label]
            assert artifact.config["selection_method_id"] == (
                "rank_quartile_centroid_maximin_all_prior_samples_v1"
            )
            assert artifact.config["model_outcomes_used"] is False
            assert artifact.result["model_outcomes_used"] is False
            assert artifact.result["selection_stage_has_neural_dynamics"] is False
            assert len(
                artifact.config["exclusion_parent_artifacts"]
            ) == SAMPLE_LABELS.index(label)
            assert all(
                not body["sentinel"] for body in artifact.result["selected_bodies"]
            )
    assert len(used) == POPULATION_SIZE
    assert ids_by_label["A"] == set(phase7m_run["sample_a"].result["body_ids"])
    assert ids_by_label["B"] == set(phase7m_run["sample_b"].result["body_ids"])
    assert CANONICAL_SAMPLE_C_ID == phase7m_run["sample_c"].artifact_id
    assert CANONICAL_SAMPLE_D_ID == phase7m_run["sample_d"].artifact_id


def test_128_union_has_exact_composition_routes_and_provenance(phase7m_run):
    artifact = phase7m_run["composition128"]
    result = artifact.result
    assert artifact.artifact_id == CANONICAL_COMPOSITION128_ID
    assert result["parent_artifact_ids"] == [
        item.artifact_id for item in _all_sample_artifacts(phase7m_run)
    ]
    assert len(result["body_ids"]) == POPULATION_SIZE == 128
    assert len(set(result["body_ids"])) == POPULATION_SIZE
    assert [item["count"] for item in result["stratum_counts"]] == [32] * 4
    assert result["pairwise_disjoint"] is True
    assert len(result["pairwise_disjointness"]) == 28
    assert all(row["overlap_count"] == 0 for row in result["pairwise_disjointness"])
    assert result["target_route_counts"] == [
        {"target_body_id": 10001, "source_count": 64},
        {"target_body_id": 10010, "source_count": 64},
    ]
    assert artifact.config["model_outcomes_used_for_composition"] is False
    assert artifact.config["source_contract_identity"] == dict(
        phase7m_run["source"].source_identity
    )


def test_coverage_plan_retains_19_stimuli_and_adds_anatomy_only_radius_one_disks(
    phase7m_run,
):
    plan = phase7m_run["plan128"]
    old_ids = [
        item["config"]["stimulus_id"]
        for item in phase7m_run["plan64"].config["stimuli"]
    ]
    assert plan.artifact_id == CANONICAL_PLAN128_ID
    assert plan.result["initial_stimulus_ids"] == old_ids
    assert len(old_ids) == 19
    assert len(plan.result["initial_uncovered_body_ids"]) == 9
    assert plan.result["initial_coverage"]
    assert len(plan.result["coverage_extension_stimuli"]) == 4
    assert [
        row["radius_lattice_steps"] for row in plan.result["coverage_extension_stimuli"]
    ] == [1] * 4
    assert all(
        row["centre_is_source_column"]
        for row in plan.result["coverage_extension_stimuli"]
    )
    assert all(
        row["model_outcomes_used"] is False
        for row in plan.result["coverage_extension_stimuli"]
    )
    assert plan.config["model_outcomes_used_for_battery_design"] is False
    assert plan.result["neural_dynamics_computed"] is False
    assert len(plan.config["stimuli"]) == 23
    assert len(plan.result["final_covered_body_ids"]) == 128


def test_128_body_path_and_model_invariants(phase7m_run):
    experiment = phase7m_run["experiment128"]
    config = experiment.config
    result = experiment.result
    assert experiment.artifact_id == CANONICAL_EXPERIMENT128_ID
    assert config["body_count"] == 128
    assert (
        config["sensory_model"]["model_id"]
        == "relative_column_exploratory_sensory_state_v1"
    )
    assert config["sensory_model"]["tau_sens_ms"] == 1.0
    assert config["sensory_model"]["gain"] == 1.0
    assert config["sensory_model"]["initial_state"] == 0.0
    assert config["sensory_model"]["input_metric_id"] == "column_overlap_fraction"
    assert config["transfer_model"]["k_transfer_mveq_per_state"] == 1.0
    assert config["transfer_model"]["structural_weight_used_as_gain"] is False
    assert config["population_normalization"] == "none"
    assert config["model_outcomes_used_for_selection_or_coverage"] is False
    assert result["coverage_totals"] == {
        "body_stimulus_covered": 128,
        "body_state_exercised": 128,
        "body_transfer_exercised": 128,
        "denominator": 128,
    }
    assert result["assignment"]["sample_count"] == 35
    assert len(config["stimuli"]) == 23
    assert result["condition_count"] == 56
    assert result["source_contribution_accounting_validated"] is True
    assert result["parent_additivity_validated"] is True
    assert result["per_step_source_accounting_comparisons"] == 1340
    assert result["per_step_A_H_additivity_comparisons"] == 1340
    assert len(result["phase7l_A_D_only_nested_regression"]) == 19
    assert all(
        row["per_source_contributions_identical"]
        and row["dn_p01_drive_membrane_events_identical"]
        for row in result["phase7l_A_D_only_nested_regression"]
    )
    assert result["standalone_E_H_state_comparisons"] == {
        label: 368 for label in "EFGH"
    }
    assert result["source_bodies_by_stratum"] == {
        f"{neuron_type}_{side}": [
            row["body_id"]
            for row in phase7m_run["composition128"].result["selected_bodies"]
            if row["neuron_type"] == neuron_type and row["side"] == side
        ]
        for neuron_type, side in STRATA
    }


def test_controls_sensitivity_and_per_source_accounting(phase7m_run):
    result = phase7m_run["experiment128"].result
    conditions = {row["condition_id"]: row for row in result["conditions"]}
    assert {
        "k_zero",
        "no_sources",
        "lc4_only",
        "lplc2_only",
        "left_only",
        "right_only",
        "sample_abcd_only",
        "sample_efgh_only",
        "all128_reference",
        "sensitivity_k_2",
    } <= set(conditions)
    for condition_id in ("k_zero", "no_sources"):
        for target in conditions[condition_id]["targets"]:
            assert set(target["drive_mveq_by_interval"]) == {0.0}
            assert set(target["membrane_mv_by_boundary"]) == {-52.0}
    assert conditions["k_zero"]["k_transfer_mveq_per_state"] == 0.0
    assert conditions["all128_reference"]["k_transfer_mveq_per_state"] == 1.0
    assert conditions["sensitivity_k_2"]["k_transfer_mveq_per_state"] == 2.0
    assert conditions["no_sources"]["active_source_body_ids"] == []
    assert len(conditions["sample_abcd_only"]["active_source_body_ids"]) == 64
    assert len(conditions["sample_efgh_only"]["active_source_body_ids"]) == 64
    assert len(conditions["all128_reference"]["active_source_body_ids"]) == 128
    for condition in result["conditions"]:
        for interval in condition["source_contributions_by_interval"]:
            by_target = Counter()
            for row in interval["contributions"]:
                by_target[row["target_body_id"]] += row["model_drive_mveq"]
            for target in condition["targets"]:
                assert by_target[target["body_id"]] == pytest.approx(
                    target["drive_mveq_by_interval"][interval["step"]],
                    rel=0.0,
                    abs=1e-15,
                )


def test_structural_counts_do_not_change_128_route_transfer(phase7m_run):
    rows = phase7m_run["composition128"].result["selected_bodies"]
    routes = [
        Route(
            row["body_id"],
            row["target_body_id"],
            row["structural_weight"],
            row["neuron_type"],
            row["side"],
        )
        for row in rows
    ]
    states = {route.source_body_id: 0.25 for route in routes}
    baseline = route_population_drive(
        states,
        routes,
        target_body_ids=(10001, 10010),
        active_source_ids=set(states),
        k_transfer_mveq_per_state=1.0,
    )
    altered_routes = [
        replace(route, structural_weight=route.structural_weight + 1000)
        for route in routes
    ]
    altered = route_population_drive(
        states,
        altered_routes,
        target_body_ids=(10001, 10010),
        active_source_ids=set(states),
        k_transfer_mveq_per_state=1.0,
    )
    assert altered == baseline


def test_phase7m_sample_artifact_tampering_is_rejected(phase7m_run, tmp_path):
    original = phase7m_run["samples_eh"]["E"]
    copied = tmp_path / original.artifact_id
    shutil.copytree(original.path, copied)
    manifest_path = copied / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifact_id"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BoundedSensoryScale128ArtifactError):
        load_scale128_artifact(copied, "sample")


def test_canonical_phase7d_through_7l_sources_remain_replayable(phase7m_run):
    # Context construction replayed A/B, 7H–7K; Phase 7M recomputed and matched
    # the full immutable 64-body composition, plan, and experiment.
    assert phase7m_run["experiment64"].artifact_id == (
        "5095eddbf35c363cf4ae47ef875420ecad725eb0c837767ec8789e65bd68ab02"
    )
    assert (
        phase7m_run["experiment128"].config["phase7l_experiment_artifact_id"]
        == phase7m_run["experiment64"].artifact_id
    )
    assert (
        phase7m_run["experiment128"].config["parent_sample_artifacts"]
        == phase7m_run["composition128"].config["parent_sample_artifacts"]
    )
