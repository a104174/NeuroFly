"""Phase 7I coverage battery, non-zero paths, and replay regressions."""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from neurofly.bounded_sensory_coverage import (
    CANONICAL_BODY_IDS,
    CANONICAL_PHASE7H_ID,
    CANONICAL_SAMPLE_ID,
    compute_coverage_experiment,
    compute_coverage_plan,
    replay_inputs,
)
from neurofly.bounded_sensory_coverage_artifacts import (
    BoundedSensoryCoverageArtifactError,
    coverage_artifact_id,
    export_coverage_experiment,
    export_coverage_plan,
    load_coverage_experiment,
    plan_artifact_id,
    replay_coverage_experiment,
    replay_coverage_plan,
)
from neurofly.relative_column_assignment import canonical_json_bytes


@pytest.fixture(scope="module")
def phase7i_run(tmp_path_factory):
    sample, phase7h, source, grid, circuit = replay_inputs()
    plan_config, plan_result = compute_coverage_plan(
        sample.as_input(), phase7h, source, grid, circuit
    )
    root = tmp_path_factory.mktemp("phase7i")
    plan_path = root / "plan" / plan_artifact_id(plan_config, plan_result)
    plan = export_coverage_plan(plan_config, plan_result, plan_path)
    experiment_config, experiment_result = compute_coverage_experiment(
        plan.as_input(), sample.as_input(), phase7h, source, grid, circuit
    )
    experiment_path = (
        root / "experiment" / coverage_artifact_id(experiment_config, experiment_result)
    )
    experiment = export_coverage_experiment(
        experiment_config, experiment_result, experiment_path
    )
    return {
        "sample": sample,
        "phase7h": phase7h,
        "source": source,
        "grid": grid,
        "circuit": circuit,
        "plan": plan,
        "experiment": experiment,
    }


def _body_rows(result):
    return {item["body_id"]: item for item in result["body_coverage"]}


def test_plan_is_canonical_minimum_and_anatomy_only(phase7i_run):
    run = phase7i_run
    plan = run["plan"]
    assert plan.result["body_ids"] == list(CANONICAL_BODY_IDS)
    assert plan.result["initial_uncovered_body_ids"] == [
        16809,
        514956,
        38065,
        21804,
        40811,
        37925,
    ]
    assert (
        plan.result["covered_initially_uncovered_body_ids"]
        == plan.result["initial_uncovered_body_ids"]
    )
    assert plan.result["model_outcomes_used"] is False
    assert plan.result["neural_dynamics_computed"] is False
    assert plan.result["dn_p01_outputs_read_for_design"] is False
    assert plan.config["candidate_radii_lattice_steps"] == [1, 2, 3, 4]
    assert plan.config["objective_order"] == [
        "minimum_number_of_disks",
        "minimum_total_radius",
        "lexicographic_radius_then_source_centre",
    ]
    assert plan.result["candidate_search_summary"] == [
        {
            "side": "L",
            "source_centre_count": 116,
            "candidate_disks_evaluated": 464,
            "nonempty_unique_coverage_masks": 4,
            "selected_disks": 2,
        },
        {
            "side": "R",
            "source_centre_count": 130,
            "candidate_disks_evaluated": 520,
            "nonempty_unique_coverage_masks": 4,
            "selected_disks": 2,
        },
    ]
    extension = plan.result["coverage_extension_stimuli"]
    assert [
        (item["side"], tuple(item["centre_hex"]), item["radius_lattice_steps"])
        for item in extension
    ] == [
        ("L", (3, 10), 1),
        ("L", (12, 31), 1),
        ("R", (1, 7), 1),
        ("R", (12, 27), 1),
    ]
    source_centres = {
        (record.eye_side, record.ol_hex1, record.ol_hex2)
        for record in run["source"].contract.records
    }
    assert all(
        (item["side"], *item["centre_hex"]) in source_centres
        and item["centre_was_source_column"]
        for item in extension
    )
    assert len(plan.config["stimuli"]) == 10
    assert all(
        plan.config["stimuli"][index]["origin"] == "PHASE7H_RETAINED_UNCHANGED"
        for index in range(6)
    )
    assert all(
        plan.config["stimuli"][index]["config"]
        == run["phase7h"].config["stimuli"][index]["config"]
        for index in range(6)
    )


def test_initial_phase7h_coverage_is_explicit(phase7i_run):
    plan = phase7i_run["plan"]
    rows = {item["body_id"]: item for item in plan.result["initial_body_coverage"]}
    assert sum(item["body_stimulus_covered"] for item in rows.values()) == 10
    assert {
        body_id for body_id, row in rows.items() if not row["body_stimulus_covered"]
    } == {16809, 514956, 38065, 21804, 40811, 37925}
    assert all(
        rows[body_id]["max_column_overlap_fraction"] > 0.0
        for body_id in CANONICAL_BODY_IDS
        if rows[body_id]["body_stimulus_covered"]
    )
    result_rows = _body_rows(phase7i_run["experiment"].result)
    assert (
        sum(
            row["phase7h_max_exploratory_sensory_state"] > 0.0
            for row in result_rows.values()
        )
        == 10
    )
    assert (
        sum(
            row["phase7h_max_transfer_contribution_across_state_trajectories_mveq"]
            > 0.0
            for row in result_rows.values()
        )
        == 10
    )
    assert (
        sum(
            row["phase7h_transfer_exercised_in_persisted_reference_conditions"]
            for row in result_rows.values()
        )
        == 8
    )


def test_stimulus_plan_does_not_read_phase7h_model_outcomes(phase7i_run):
    run = phase7i_run
    changed_result = dict(run["phase7h"].result)
    changed_result["sensory_trajectories_by_stimulus"] = {"mutated": []}
    changed_result["conditions"] = [{"mutated_model_outcome": True}]
    altered_h = replace(run["phase7h"], result=changed_result)
    config, result = compute_coverage_plan(
        run["sample"].as_input(),
        altered_h,
        run["source"],
        run["grid"],
        run["circuit"],
    )
    assert config == run["plan"].config
    assert result == run["plan"].result
    wrong_h = replace(run["phase7h"], artifact_id="not-canonical")
    with pytest.raises(ValueError, match="canonical Phase 7H source pair"):
        compute_coverage_plan(
            run["sample"].as_input(),
            wrong_h,
            run["source"],
            run["grid"],
            run["circuit"],
        )


def test_all_sixteen_exposure_state_and_transfer_paths_are_nonzero(phase7i_run):
    run = phase7i_run
    result = run["experiment"].result
    assert result["body_ids"] == list(CANONICAL_BODY_IDS)
    assert result["coverage_totals"] == {
        "body_stimulus_covered": 16,
        "body_state_exercised": 16,
        "body_transfer_exercised": 16,
        "denominator": 16,
    }
    rows = _body_rows(result)
    assert set(rows) == set(CANONICAL_BODY_IDS)
    for row in rows.values():
        assert row["body_stimulus_covered"] is True
        assert row["body_state_exercised"] is True
        assert row["body_transfer_exercised"] is True
        assert row["phase7i_max_column_overlap_fraction"] > 0.0
        assert row["phase7i_max_exploratory_sensory_state"] > 0.0
        assert row["phase7i_max_transfer_contribution_mveq"] > 0.0
    extension_ids = {
        item["stimulus_id"] for item in run["plan"].result["coverage_extension_stimuli"]
    }
    newly_covered = set()
    for stimulus in extension_ids:
        assignments = next(
            item
            for item in result["assignment"]["samples"]
            if item["stimulus_id"] == stimulus
        )["assignments"]
        newly_covered.update(
            row["body_id"]
            for row in assignments
            if row["column_overlap_fraction"] > 0.0
        )
    assert newly_covered == {16809, 514956, 38065, 21804, 40811, 37925}


def test_phase7h_sensory_trajectories_are_unchanged(phase7i_run):
    phase7h = phase7i_run["phase7h"].result
    current = phase7i_run["experiment"].result
    for stimulus_id, expected in phase7h["sensory_trajectories_by_stimulus"].items():
        assert current["sensory_trajectories_by_stimulus"][stimulus_id] == expected
    assert current["old_phase7h_stimuli_and_sensory_trajectories_unchanged"] is True
    assert phase7h["sample_artifact_id"] == CANONICAL_SAMPLE_ID
    assert (
        phase7h["experiment_id"]
        == "phase7h_bounded_16_body_relative_column_sensory_to_dnp01_v1"
    )
    assert phase7h["body_ids"] == list(CANONICAL_BODY_IDS)


def test_left_right_stimulus_and_dn_target_isolation(phase7i_run):
    result = phase7i_run["experiment"].result
    stimuli = {
        item["config"]["stimulus_id"]: item["config"]["side"]
        for item in phase7i_run["plan"].config["stimuli"]
    }
    trajectories = result["sensory_trajectories_by_stimulus"]
    conditions = {item["condition_id"]: item for item in result["conditions"]}
    for stimulus_id, side in stimuli.items():
        assert all(
            row["peak_exposure"] == 0.0
            and row["peak_exploratory_state"] == 0.0
            and all(value["state_value"] == 0.0 for value in row["state_timeline"])
            for row in trajectories[stimulus_id]
            if row["side"] != side
        )
        condition = conditions[f"phase7i_{stimulus_id}"]
        wrong_target = 10001 if side == "L" else 10010
        target = next(
            row for row in condition["targets"] if row["body_id"] == wrong_target
        )
        assert target["peak_drive_mveq"] == 0.0
        assert target["minimum_membrane_mv"] == -52.0
        assert target["maximum_membrane_mv"] == -52.0


def test_per_source_contributions_sum_to_target_drive(phase7i_run):
    for condition in phase7i_run["experiment"].result["conditions"]:
        target_series = {
            item["body_id"]: item["drive_mveq_by_interval"]
            for item in condition["targets"]
        }
        assert (
            len(condition["source_contributions_by_interval"])
            == condition["interval_count"]
        )
        for interval in condition["source_contributions_by_interval"]:
            for target_id in (10001, 10010):
                contributions = [
                    row["model_drive_mveq"]
                    for row in interval["contributions"]
                    if row["target_body_id"] == target_id
                ]
                assert len(contributions) == 8
                assert sum(contributions) == pytest.approx(
                    target_series[target_id][interval["step"]],
                    rel=0.0,
                    abs=1e-15,
                )


def test_extension_sample_and_state_boundary_are_grid_exact(phase7i_run):
    result = phase7i_run["experiment"].result
    extension_ids = {
        item["stimulus_id"]
        for item in phase7i_run["plan"].result["coverage_extension_stimuli"]
    }
    trajectories = result["sensory_trajectories_by_stimulus"]
    conditions = {item["condition_id"]: item for item in result["conditions"]}
    for stimulus_id in extension_ids:
        assignments = next(
            sample
            for sample in result["assignment"]["samples"]
            if sample["stimulus_id"] == stimulus_id
        )
        assert assignments["step"] == 0
        assert assignments["time_ms"] == 0.0
        for trajectory in trajectories[stimulus_id]:
            timeline = trajectory["state_timeline"]
            assert timeline[0]["state_step"] == 0
            assert timeline[0]["state_value"] == 0.0
            if trajectory["peak_exposure"] > 0.0:
                assert timeline[1]["state_step"] == 1
                assert timeline[1]["time_ms"] == 0.1
                assert timeline[1]["state_value"] > 0.0
        condition = conditions[f"phase7i_{stimulus_id}"]
        interval_rows = condition["source_contributions_by_interval"]
        for trajectory in trajectories[stimulus_id]:
            if trajectory["peak_exposure"] <= 0.0:
                continue
            body_id = trajectory["body_id"]
            first_input = next(
                row
                for row in interval_rows[1]["contributions"]
                if row["source_body_id"] == body_id
            )
            assert first_input["model_drive_mveq"] == pytest.approx(
                trajectory["state_timeline"][1]["state_value"],
                rel=0.0,
                abs=1e-15,
            )
            assert first_input["target_body_id"] == (
                10010 if trajectory["side"] == "L" else 10001
            )


def test_artifacts_replay_and_tampering_fails_closed(phase7i_run, tmp_path):
    run = phase7i_run
    replayed_plan = replay_coverage_plan(run["plan"].path)
    replayed = replay_coverage_experiment(run["experiment"].path, run["plan"].path)
    assert replayed_plan.artifact_id == run["plan"].artifact_id
    assert replayed.artifact_id == run["experiment"].artifact_id
    assert (
        coverage_artifact_id(replayed.config, replayed.result) == replayed.artifact_id
    )
    assert replayed.result == run["experiment"].result

    tampered = tmp_path / "tampered"
    shutil.copytree(run["experiment"].path, tampered)
    result_path = tampered / "coverage_result.json"
    result_path.write_bytes(result_path.read_bytes() + b" ")
    with pytest.raises(BoundedSensoryCoverageArtifactError, match="canonical JSON"):
        load_coverage_experiment(tampered)

    manifest_tampered = tmp_path / "manifest-tampered"
    shutil.copytree(run["experiment"].path, manifest_tampered)
    manifest_path = manifest_tampered / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["unexpected"] = True
    manifest_path.write_bytes(canonical_json_bytes(manifest) + b"\n")
    with pytest.raises(BoundedSensoryCoverageArtifactError, match="integrity mismatch"):
        load_coverage_experiment(manifest_tampered)


def test_phase7h_and_upstream_artifact_identities_are_pinned(phase7i_run):
    run = phase7i_run
    assert run["sample"].artifact_id == CANONICAL_SAMPLE_ID
    assert run["phase7h"].artifact_id == CANONICAL_PHASE7H_ID
    assert run["phase7h"].manifest["result_sha256"] == (
        "22cfba7705d0989d764934f80e13e73febe6c9904a76a8078b143699464dd792"
    )
    assert run["experiment"].config["sensory_model"]["tau_sens_ms"] == 1.0
    assert run["experiment"].config["sensory_model"]["gain"] == 1.0
    assert (
        run["experiment"].config["transfer_model"]["k_transfer_mveq_per_state"] == 1.0
    )
    assert run["experiment"].config["sensory_model"]["classification"] == (
        "MODEL_ASSUMPTION"
    )
    assert (
        run["experiment"].config["transfer_model"]["structural_weight_used_as_gain"]
        is False
    )
    assert (
        run["experiment"].config["scientific_boundary"]["absolute_visual_angle_present"]
        is False
    )
    assert Path(run["experiment"].path).is_dir()
