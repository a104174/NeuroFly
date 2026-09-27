"""Phase 7O complete exploratory 311→2 model-state execution gates."""

from __future__ import annotations

import json
from collections import Counter

import pytest

from neurofly.relative_column_assignment import canonical_json_bytes
from neurofly.relative_column_dnp01_transfer import Route, route_population_drive
from neurofly.sensory_population_execution import (
    SensoryPopulationExecutionError,
    _routes,
    execute_311,
)
from neurofly.sensory_population_execution_artifacts import (
    SensoryPopulationExecutionArtifactError,
    export_execution_artifact,
    load_execution_artifact,
)
from neurofly.sensory_population_execution_cli import (
    COVERAGE_ID,
    EXECUTION_ID,
    POPULATION_ID,
)
from neurofly.sensory_population_readiness import (
    DEFAULT_COVERAGE_ROOT,
    DEFAULT_EXECUTION_ROOT,
    DEFAULT_POPULATION_ROOT,
    load_phase7n_sources,
    load_readiness_artifact,
)


@pytest.fixture(scope="module")
def run311():
    source, circuit, grid = load_phase7n_sources()
    population = load_readiness_artifact(
        DEFAULT_POPULATION_ROOT / POPULATION_ID, "population"
    )
    coverage = load_readiness_artifact(DEFAULT_COVERAGE_ROOT / COVERAGE_ID, "coverage")
    execution = load_readiness_artifact(
        DEFAULT_EXECUTION_ROOT / EXECUTION_ID, "execution"
    )
    config, result, timings = execute_311(
        population, coverage, execution, source, circuit, grid
    )
    return (
        config,
        result,
        timings,
        (population, coverage, execution, source, circuit, grid),
    )


def test_complete_source_population_coverage_and_routes(run311):
    config, result, _, inputs = run311
    population, coverage, execution, _, _, _ = inputs
    assert len(result["body_ids"]) == len(set(result["body_ids"])) == 311
    assert Counter(row["neuron_type"] for row in population.result["bodies"]) == {
        "LC4": 126,
        "LPLC2": 185,
    }
    assert Counter(
        (row["neuron_type"], row["side"]) for row in population.result["bodies"]
    ) == {("LC4", "L"): 71, ("LC4", "R"): 55, ("LPLC2", "L"): 94, ("LPLC2", "R"): 91}
    assert Counter(row["target_body_id"] for row in population.result["bodies"]) == {
        10001: 146,
        10010: 165,
    }
    assert len(result["route_contract"]) == 311
    assert Counter(row["target_body_id"] for row in result["route_contract"]) == {
        10001: 146,
        10010: 165,
    }
    assert len(coverage.config["stimuli"]) == len(result["stimulus_ids"]) == 27
    assert len(result["body_coverage"]) == 311
    assert result["coverage_totals"] == {
        "body_stimulus_covered": 311,
        "body_state_exercised": 311,
        "body_transfer_exercised": 311,
    }
    assert (
        result["contribution_ledger_row_count"]
        == execution.result["expected_contribution_ledger_rows"]
        == 130931
    )
    assert result["condition_count"] == 35
    assert config["population_artifact"]["artifact_id"] == POPULATION_ID
    assert config["coverage_artifact"]["artifact_id"] == COVERAGE_ID
    assert config["execution_manifest_artifact"]["artifact_id"] == EXECUTION_ID


def test_reference_models_nested_regressions_and_no_legacy_drive(run311):
    config, result, _, inputs = run311
    execution = inputs[2]
    assert config["model_config_sha256"] == execution.config["model_config_sha256"]
    assert execution.config["sensory_model"]["tau_sens_ms"] == 1.0
    assert execution.config["sensory_model"]["gain"] == 1.0
    assert execution.config["sensory_model"]["initial_state"] == 0.0
    assert execution.config["transfer_model"]["k_transfer_mveq_per_state"] == 1.0
    assert config["population_normalization"] == "none"
    assert config["structural_edge_count_numerical_use"] == "none_source_metadata_only"
    assert result["nested_128_regression"]["exact_equality"] is True
    assert result["nested_128_regression"]["state_trajectory_comparisons"] == 128 * 23
    assert result["phase7e_sentinel_regression"]["exact_equality"] is True
    assert all(
        "theta_rad" not in key
        and "lc4_drive_mveq" not in key
        and "lplc2_drive_mveq" not in key
        for key in config
    )


def test_accounting_side_and_integer_step_alignment(run311):
    _, result, _, inputs = run311
    population = inputs[0]
    body_side = {row["body_id"]: row["side"] for row in population.result["bodies"]}
    stimulus_side = {
        row["config"]["stimulus_id"]: row["config"]["side"]
        for row in inputs[1].config["stimuli"]
    }
    for condition in result["conditions"]:
        assert (
            condition["time_alignment"]
            == "sensory_state_boundary_n_drives_interval_n_to_n_plus_1"
        )
        assert (
            len(condition["source_contributions_by_interval"])
            == condition["interval_count"]
        )
        targets = {row["body_id"]: row for row in condition["targets"]}
        for target in targets.values():
            assert (
                len(target["membrane_mv_by_boundary"])
                == condition["interval_count"] + 1
            )
        for step, interval in enumerate(condition["source_contributions_by_interval"]):
            assert interval["step"] == step
            assert len(interval["contributions"]) == 311
            for target_id in (10001, 10010):
                amount = sum(
                    row["model_drive_mveq"]
                    for row in interval["contributions"]
                    if row["target_body_id"] == target_id
                )
                stored = targets[target_id]["drive_mveq_by_interval"][step]
                assert amount == pytest.approx(stored, abs=1e-12)
            if condition["condition_id"].startswith("stimulus::"):
                side = stimulus_side[condition["condition_id"].split("::", 1)[1]]
                assert all(
                    row["model_drive_mveq"] == 0.0
                    for row in interval["contributions"]
                    if body_side[row["source_body_id"]] != side
                )
    condition = next(
        row
        for row in result["conditions"]
        if row["condition_id"] == "stimulus::left_expand_33_29"
    )
    traces = {
        row["body_id"]: row["state_timeline"]
        for row in result["sensory_trajectories_by_stimulus"]["left_expand_33_29"]
    }
    for interval in condition["source_contributions_by_interval"]:
        step = interval["step"]
        for contribution in interval["contributions"]:
            state = traces[contribution["source_body_id"]][step]["state_value"]
            assert contribution["sensory_state"] == state
            assert contribution["model_drive_mveq"] == state


def test_controls_and_sensitivity(run311):
    _, result, _, _ = run311
    by_id = {row["condition_id"]: row for row in result["conditions"]}
    assert {
        "reference_bilateral",
        "k_zero",
        "no_sources",
        "lc4_only",
        "lplc2_only",
        "left_only",
        "right_only",
        "sensitivity_k_2",
    } <= set(by_id)
    for name in ("k_zero", "no_sources"):
        assert all(
            all(value == 0.0 for value in target["drive_mveq_by_interval"])
            for target in by_id[name]["targets"]
        )
    assert by_id["reference_bilateral"]["k_transfer_mveq_per_state"] == 1.0
    assert by_id["sensitivity_k_2"]["k_transfer_mveq_per_state"] == 2.0
    for reference, double in zip(
        by_id["reference_bilateral"]["targets"],
        by_id["sensitivity_k_2"]["targets"],
        strict=True,
    ):
        assert double["drive_mveq_by_interval"] == [
            2 * value for value in reference["drive_mveq_by_interval"]
        ]


def test_artifact_replay_and_tamper_rejection(run311, tmp_path):
    config, result, _, inputs = run311
    artifact = export_execution_artifact(config, result, output_root=tmp_path)
    assert load_execution_artifact(artifact.path).artifact_id == artifact.artifact_id
    new_config, new_result, _ = execute_311(*inputs)
    assert (new_config, new_result) == (config, result)
    assert (
        export_execution_artifact(
            new_config, new_result, output_root=tmp_path
        ).artifact_id
        == artifact.artifact_id
    )
    manifest_path = artifact.path / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["result_sha256"] = "0" * 64
    manifest_path.write_bytes(canonical_json_bytes(manifest) + b"\n")
    with pytest.raises(SensoryPopulationExecutionArtifactError):
        load_execution_artifact(artifact.path)


def test_source_and_planning_mismatch_rejected(run311):
    _, _, _, inputs = run311
    population, coverage, execution, source, circuit, grid = inputs
    changed = population.as_input()
    changed["result"]["body_ids"] = changed["result"]["body_ids"][:-1]
    with pytest.raises(SensoryPopulationExecutionError):
        execute_311(changed, coverage, execution, source, circuit, grid)

    changed_coverage = coverage.as_input()
    changed_coverage["config"]["stimuli"][0]["config"]["radius_schedule"][0][
        "radius_lattice_steps"
    ] = 0
    with pytest.raises(SensoryPopulationExecutionError):
        execute_311(population, changed_coverage, execution, source, circuit, grid)

    changed_execution = execution.as_input()
    changed_execution["config"]["transfer_model"]["k_transfer_mveq_per_state"] = 2.0
    with pytest.raises(SensoryPopulationExecutionError):
        execute_311(population, coverage, changed_execution, source, circuit, grid)


def test_all_311_structural_counts_are_metadata_only(run311):
    _, result, _, inputs = run311
    population, _, _, source, circuit, _ = inputs
    routes = _routes(population.as_input(), source, circuit)
    states = {body_id: 0.25 for body_id in result["body_ids"]}
    targets = (10001, 10010)
    original, contributions = route_population_drive(
        states,
        routes,
        target_body_ids=targets,
        active_source_ids=set(states),
        k_transfer_mveq_per_state=1.0,
    )
    altered_routes = tuple(
        Route(
            route.source_body_id,
            route.target_body_id,
            route.structural_weight + 100,
            route.source_type,
            route.side,
        )
        for route in routes
    )
    changed, changed_contributions = route_population_drive(
        states,
        altered_routes,
        target_body_ids=targets,
        active_source_ids=set(states),
        k_transfer_mveq_per_state=1.0,
    )
    assert original == changed
    assert contributions == changed_contributions
