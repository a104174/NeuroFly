"""Phase 7J independent disjoint Sample B and pipeline regressions."""

from __future__ import annotations

import shutil
from copy import deepcopy

import pytest

from neurofly.bounded_sensory_population import STRATA, _maximin_candidate
from neurofly.bounded_sensory_robustness import (
    CANONICAL_PHASE7H_ID,
    CANONICAL_PHASE7I_EXPERIMENT_ID,
    CANONICAL_PHASE7I_PLAN_ID,
    CANONICAL_SAMPLE_A_ID,
    DEFAULT_PHASE7H_PATH,
    DEFAULT_PHASE7I_EXPERIMENT_PATH,
    DEFAULT_PHASE7I_PLAN_PATH,
    DEFAULT_SAMPLE_A_PATH,
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    _rank_quartiles,
    compute_sample_b_coverage_plan,
    compute_sample_b_experiment,
    replay_canonical_baselines,
    select_independent_sample,
)
from neurofly.bounded_sensory_robustness_artifacts import (
    BoundedSensoryRobustnessArtifactError,
    export_sample_b_artifact,
    export_sample_b_experiment_artifact,
    export_sample_b_plan_artifact,
    load_sample_b_experiment_artifact,
    replay_sample_b_artifact,
    replay_sample_b_experiment_artifact,
    replay_sample_b_plan_artifact,
    sample_b_artifact_id,
    sample_b_experiment_artifact_id,
    sample_b_plan_artifact_id,
)
from neurofly.relative_column_dnp01_transfer import Route, route_population_drive

SAMPLE_B_IDS = [
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
]
SAMPLE_A_IDS = [
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
]

SOURCE_AVAILABLE = all(
    path.exists()
    for path in (
        DEFAULT_SOURCE_ROOT,
        DEFAULT_WORKBOOK,
        DEFAULT_SAMPLE_A_PATH,
        DEFAULT_PHASE7H_PATH,
        DEFAULT_PHASE7I_PLAN_PATH,
        DEFAULT_PHASE7I_EXPERIMENT_PATH,
    )
)


@pytest.fixture(scope="module")
def phase7j_run(tmp_path_factory):
    if not SOURCE_AVAILABLE:
        pytest.skip("pinned Phase 7A–7I local artifacts are unavailable")
    baseline = replay_canonical_baselines()
    sample_a, phase7h, phase7i_plan, phase7i_experiment, source, grid, circuit = (
        baseline
    )
    sample_config, sample_result = select_independent_sample(
        source, circuit, sample_a.as_input()
    )
    sample_id = sample_b_artifact_id(sample_config, sample_result)
    sample_path = tmp_path_factory.mktemp("phase7j-sample-b") / sample_id
    sample_b = export_sample_b_artifact(sample_config, sample_result, sample_path)

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
    plan_id = sample_b_plan_artifact_id(plan_config, plan_result)
    plan_path = tmp_path_factory.mktemp("phase7j-plan-b") / plan_id
    plan_b = export_sample_b_plan_artifact(plan_config, plan_result, plan_path)

    experiment_config, experiment_result = compute_sample_b_experiment(
        sample_b.as_input(),
        plan_b.as_input(),
        sample_a,
        phase7h,
        phase7i_plan,
        phase7i_experiment,
        source,
        grid,
        circuit,
    )
    experiment_id = sample_b_experiment_artifact_id(
        experiment_config, experiment_result
    )
    experiment_path = tmp_path_factory.mktemp("phase7j-experiment-b") / experiment_id
    experiment_b = export_sample_b_experiment_artifact(
        experiment_config, experiment_result, experiment_path
    )
    return {
        "sample_a": sample_a,
        "phase7h": phase7h,
        "phase7i_plan": phase7i_plan,
        "phase7i_experiment": phase7i_experiment,
        "source": source,
        "grid": grid,
        "circuit": circuit,
        "sample_b": sample_b,
        "plan_b": plan_b,
        "experiment_b": experiment_b,
    }


def _condition(result, condition_id):
    return next(
        item for item in result["conditions"] if item["condition_id"] == condition_id
    )


def _target(condition, body_id):
    return next(item for item in condition["targets"] if item["body_id"] == body_id)


def test_sample_b_is_deterministic_balanced_disjoint_and_outcome_blind(phase7j_run):
    run = phase7j_run
    sample_a = run["sample_a"]
    sample_b = run["sample_b"]
    assert sample_a.artifact_id == CANONICAL_SAMPLE_A_ID
    assert sample_a.result["body_ids"] == SAMPLE_A_IDS
    assert sample_b.result["body_ids"] == SAMPLE_B_IDS
    assert set(sample_b.result["body_ids"]).isdisjoint(SAMPLE_A_IDS)
    assert sample_b.result["sample_a_overlap_count"] == 0
    assert sample_b.result["model_outcomes_used"] is False
    assert sample_b.config["selection_excludes_model_outcomes"] is True
    assert sample_b.config["selection_excludes_sample_a"] is True
    assert sample_b.config["method"]["canonical_sentinels_forced"] is False
    assert [
        (row["neuron_type"], row["side"], row["count"])
        for row in sample_b.result["stratum_counts"]
    ] == [(neuron_type, side, 4) for neuron_type, side in STRATA]

    selected = sample_b.result["selected_bodies"]
    assert all(not row["canonical_sentinel"] for row in selected)
    for neuron_type, side in STRATA:
        rows = [
            row
            for row in selected
            if row["neuron_type"] == neuron_type and row["side"] == side
        ]
        assert [row["selection_quartile"] for row in rows] == [1, 2, 3, 4]
        assert all(row["quartile_candidate_count"] > 0 for row in rows)
        assert all(
            row["minimum_hex_centroid_distance_to_sample_a_and_prior_b"] > 0
            for row in rows
        )
    assert select_independent_sample(
        run["source"], run["circuit"], sample_a.as_input()
    ) == (sample_b.config, sample_b.result)

    circuit_edges = {
        edge.source_body_id: edge
        for edge in run["circuit"].connections
        if edge.source_type in {"LC4", "LPLC2"} and edge.target_type == "DNp01"
    }
    for row in selected:
        edge = circuit_edges[row["body_id"]]
        assert row["target_body_id"] == edge.target_body_id
        assert row["structural_weight"] == edge.structural_weight
        assert (
            row["side"]
            == run["circuit"].neurons_by_body_id[edge.target_body_id].soma_side
        )


def test_rank_quartiles_are_balanced_even_with_discrete_ties():
    candidates = [
        {"body_id": body_id, "structural_weight": 4} for body_id in range(1, 19)
    ]
    ranks = _rank_quartiles(candidates)
    counts = [
        sum(row["quartile_index_zero_based"] == index for row in ranks.values())
        for index in range(4)
    ]
    assert max(counts) - min(counts) <= 1
    assert ranks == _rank_quartiles(list(reversed(candidates)))


def test_maximin_exact_distance_tie_uses_smallest_body_id():
    candidates = [
        {"body_id": 20, "anatomical_column_centroid": [2.0, 0.0]},
        {"body_id": 10, "anatomical_column_centroid": [0.0, 2.0]},
    ]
    prior_selected = [{"anatomical_column_centroid": [0.0, 0.0]}]
    chosen, distance = _maximin_candidate(candidates, prior_selected)
    assert chosen["body_id"] == 10
    assert distance == 2.0


def test_sample_b_export_rejects_overlap_with_canonical_sample_a(phase7j_run):
    run = phase7j_run
    config = deepcopy(run["sample_b"].config)
    result = deepcopy(run["sample_b"].result)
    result["body_ids"][0] = SAMPLE_A_IDS[0]
    with pytest.raises(BoundedSensoryRobustnessArtifactError, match="identity"):
        export_sample_b_artifact(
            config,
            result,
            run["sample_b"].path.parent / "overlap-rejected",
        )


def test_sample_b_coverage_uses_existing_battery_then_anatomical_extension(phase7j_run):
    plan = phase7j_run["plan_b"]
    result = plan.result
    assert result["initial_covered_body_ids"] == [
        518439,
        19954,
        20808,
        111903,
        27399,
        29702,
        18936,
        25316,
        29598,
        33185,
    ]
    assert result["initial_uncovered_body_ids"] == [
        31308,
        516909,
        81112,
        26112,
        23929,
        24268,
    ]
    assert plan.config["model_outcomes_used_for_battery_design"] is False
    assert result["model_outcomes_used"] is False
    assert result["neural_dynamics_computed"] is False
    assert result["dn_p01_outputs_read_for_design"] is False
    extensions = result["coverage_extension_stimuli"]
    assert [
        (row["side"], row["centre_hex"], row["radius_lattice_steps"])
        for row in extensions
    ] == [
        ("L", [3, 5], 1),
        ("L", [22, 21], 1),
        ("R", [3, 14], 1),
        ("R", [21, 32], 1),
    ]
    assert all(row["centre_is_source_column"] for row in extensions)
    assert all(row["model_outcomes_used"] is False for row in extensions)
    assert len(plan.config["stimuli"]) == 14
    assert len({row["config"]["stimulus_id"] for row in plan.config["stimuli"]}) == 14


def test_sample_b_pipeline_has_16_by_16_nonzero_path_and_exact_routing(phase7j_run):
    run = phase7j_run
    sample = run["sample_b"]
    artifact = run["experiment_b"]
    result = artifact.result
    assert result["body_ids"] == SAMPLE_B_IDS
    assert result["assignment"]["sample_count"] == 26
    assert result["coverage_totals"] == {
        "body_stimulus_covered": 16,
        "body_state_exercised": 16,
        "body_transfer_exercised": 16,
        "denominator": 16,
    }
    assert len(result["body_coverage"]) == 16
    assert all(
        row["body_stimulus_covered"]
        and row["body_state_exercised"]
        and row["body_transfer_exercised"]
        and row["max_column_overlap_fraction"] > 0.0
        and row["max_exploratory_state"] > 0.0
        and row["max_transfer_contribution_mveq"] > 0.0
        for row in result["body_coverage"]
    )

    route_by_body = {
        row["source_body_id"]: row for row in artifact.config["route_contract"]
    }
    assert set(route_by_body) == set(SAMPLE_B_IDS)
    for body in sample.result["selected_bodies"]:
        route = route_by_body[body["body_id"]]
        assert route["target_body_id"] == body["target_body_id"]
        assert route["side"] == body["side"]
        assert route["structural_weight"] == body["structural_weight"]
        assert route["weight_semantics"] == "STRUCTURAL_COUNT_ROUTING_METADATA_ONLY"

    for assignment_sample in result["assignment"]["samples"]:
        expected_side = assignment_sample["side"]
        for row in assignment_sample["assignments"]:
            if row["side"] != expected_side:
                assert row["column_overlap_fraction"] == 0.0
    for stimulus_id, rows in result["sensory_trajectories_by_stimulus"].items():
        side = next(
            item["config"]["side"]
            for item in artifact.config["stimuli"]
            if item["config"]["stimulus_id"] == stimulus_id
        )
        for row in rows:
            if row["side"] != side:
                assert all(tick["state_value"] == 0.0 for tick in row["state_timeline"])

    for condition in result["conditions"]:
        targets = {row["body_id"]: row for row in condition["targets"]}
        for interval in condition["source_contributions_by_interval"]:
            for target_id in (10001, 10010):
                value = sum(
                    row["model_drive_mveq"]
                    for row in interval["contributions"]
                    if row["target_body_id"] == target_id
                )
                assert value == pytest.approx(
                    targets[target_id]["drive_mveq_by_interval"][interval["step"]],
                    rel=0.0,
                    abs=1e-15,
                )


def test_model_invariants_controls_sensitivity_and_no_population_normalization(
    phase7j_run,
):
    run = phase7j_run
    artifact = run["experiment_b"]
    result = artifact.result
    baseline = run["phase7i_experiment"]
    assert artifact.config["sensory_model"] == baseline.config["sensory_model"]
    assert artifact.config["transfer_model"] == baseline.config["transfer_model"]
    assert artifact.config["dnp01_model"] == baseline.config["dnp01_model"]
    assert artifact.config["transfer_model"]["k_transfer_mveq_per_state"] == 1.0
    assert artifact.config["sensory_model"]["tau_sens_ms"] == 1.0
    assert artifact.config["sensory_model"]["gain"] == 1.0
    assert artifact.config["sensory_model"]["initial_state"] == 0.0
    assert artifact.config["transfer_model"]["source_normalization"] == "none"
    assert artifact.config["model_invariants_match_sample_a"] is True
    assert result["model_invariants_match_sample_a"] is True
    assert result["selection_and_stimulus_design_outcome_blind"] is True
    comparison = artifact.config["sample_a_vs_b_comparison"]
    assert comparison["sample_a_disjointness_overlap_count"] == 0
    assert comparison["sample_a_artifact_bytes"] == 784421
    assert comparison["sample_b_artifact_bytes"] == 16512
    assert comparison["sample_a_coverage_totals"]["body_stimulus_covered"] == 16
    assert comparison["sample_b_coverage_totals"]["body_transfer_exercised"] == 16
    assert (
        comparison["sample_a_population_summary"]["target_model_output"]["10001"][
            "simulated_spike_count"
        ]
        == 0
    )
    assert comparison["sample_b_population_summary"]["target_model_output"]["10001"][
        "maximum_membrane_mv"
    ] == pytest.approx(-51.99779857002841)

    zero = _condition(result, "k_zero")
    none = _condition(result, "no_sources")
    for condition in (zero, none):
        assert all(target["peak_drive_mveq"] == 0.0 for target in condition["targets"])
        assert all(
            target["maximum_membrane_mv"] == -52.0 for target in condition["targets"]
        )
    assert _condition(result, "left_only")["targets"][0]["peak_drive_mveq"] == 0.0
    assert _condition(result, "right_only")["targets"][1]["peak_drive_mveq"] == 0.0
    assert set(_condition(result, "lc4_only")["active_source_body_ids"]) == {
        row["body_id"]
        for row in run["sample_b"].result["selected_bodies"]
        if row["neuron_type"] == "LC4"
    }
    assert set(_condition(result, "lplc2_only")["active_source_body_ids"]) == {
        row["body_id"]
        for row in run["sample_b"].result["selected_bodies"]
        if row["neuron_type"] == "LPLC2"
    }
    assert all(
        not target["simulated_spikes"]
        for condition in result["conditions"]
        for target in condition["targets"]
    )

    reference = _condition(result, "reference_all16")
    half = _condition(result, "sensitivity_k_0_5")
    double = _condition(result, "sensitivity_k_2")
    for target_id in (10001, 10010):
        peak = _target(reference, target_id)["peak_drive_mveq"]
        assert _target(half, target_id)["peak_drive_mveq"] == pytest.approx(
            peak * 0.5, rel=0.0, abs=1e-15
        )
        assert _target(double, target_id)["peak_drive_mveq"] == pytest.approx(
            peak * 2.0, rel=0.0, abs=1e-15
        )

    routes = tuple(
        Route(
            source_body_id=row["source_body_id"],
            target_body_id=row["target_body_id"],
            structural_weight=row["structural_weight"],
            source_type=row["source_type"],
            side=row["side"],
        )
        for row in artifact.config["route_contract"]
    )
    states = {row.source_body_id: 0.125 for row in routes}
    normal, normal_rows = route_population_drive(
        states,
        routes,
        target_body_ids=(10001, 10010),
        active_source_ids=set(states),
        k_transfer_mveq_per_state=1.0,
    )
    changed_metadata = tuple(
        Route(
            source_body_id=row.source_body_id,
            target_body_id=row.target_body_id,
            structural_weight=row.structural_weight + 1000,
            source_type=row.source_type,
            side=row.side,
        )
        for row in routes
    )
    changed, changed_rows = route_population_drive(
        states,
        changed_metadata,
        target_body_ids=(10001, 10010),
        active_source_ids=set(states),
        k_transfer_mveq_per_state=1.0,
    )
    assert changed == normal
    assert changed_rows == normal_rows


def test_phase7j_artifact_identity_full_replay_and_old_baselines(phase7j_run):
    run = phase7j_run
    assert run["phase7h"].artifact_id == CANONICAL_PHASE7H_ID
    assert run["phase7i_plan"].artifact_id == CANONICAL_PHASE7I_PLAN_ID
    assert run["phase7i_experiment"].artifact_id == CANONICAL_PHASE7I_EXPERIMENT_ID
    sample_b = run["sample_b"]
    plan_b = run["plan_b"]
    experiment_b = run["experiment_b"]
    assert sample_b.artifact_id == sample_b_artifact_id(
        sample_b.config, sample_b.result
    )
    assert plan_b.artifact_id == sample_b_plan_artifact_id(plan_b.config, plan_b.result)
    assert experiment_b.artifact_id == sample_b_experiment_artifact_id(
        experiment_b.config, experiment_b.result
    )
    assert replay_sample_b_artifact(sample_b.path).artifact_id == sample_b.artifact_id
    assert (
        replay_sample_b_plan_artifact(plan_b.path, sample_b.path).artifact_id
        == plan_b.artifact_id
    )
    replayed = replay_sample_b_experiment_artifact(
        experiment_b.path, sample_b.path, plan_b.path
    )
    assert replayed.artifact_id == experiment_b.artifact_id
    assert replayed.result == experiment_b.result

    corrupted = experiment_b.path.parent / "tampered"
    shutil.copytree(experiment_b.path, corrupted)
    result_file = corrupted / "population_b_result.json"
    result_file.write_bytes(result_file.read_bytes() + b" ")
    with pytest.raises(BoundedSensoryRobustnessArtifactError, match="canonical JSON"):
        load_sample_b_experiment_artifact(corrupted)
