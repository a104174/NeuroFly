"""Evidence-gated orientation proxies, not biological yaw or desired movement."""

import copy
import json
from pathlib import Path

import pytest

from neurofly import dnp15_exploratory_yaw as model
from neurofly.dnp15_exploratory_yaw_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    _manifest,
    generate_yaw_artifact,
    replay_yaw_artifact,
)
from neurofly.dnp15_exploratory_yaw_cli import main
from neurofly.hs_dnp15_neural_validation_artifacts import replay_neural_artifact
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

ARTIFACT_ID = "243914905c17ceb1285c645aa9e9700b602a9e22c8703c9f9ce4c7fe4f7e935d"
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def artifact():
    return replay_yaw_artifact(DEFAULT_ARTIFACT_ROOT / ARTIFACT_ID)


def test_evidence_identity_classes_and_signed_inference():
    gate = model.load_evidence_gate()
    assert canonical_sha256(gate) == model.GATE_ID
    assert gate["identity_compatibility"]["classification"] == (
        "TARGET_IDENTITY_COMPATIBLE_WITH_LIMITATIONS"
    )
    assert gate["directional_evidence"]["classification"] == (
        "BILATERAL_DIRECTIONAL_RELATION_QUALITATIVELY_SUPPORTED"
    )
    assert gate["directional_evidence"]["causal_evidence_status"] == (
        "MIXED_CAUSAL_AND_CORRELATIONAL"
    )
    assert gate["directional_evidence"]["silenced_left_observed_bias"] == (
        "RIGHTWARD_CONTRALATERAL_PATH_DRIFT"
    )
    assert gate["directional_evidence"]["silenced_right_observed_bias"] == (
        "LEFTWARD_CONTRALATERAL_PATH_DRIFT"
    )
    assert gate["stage_a"]["decision"] == "EXPLORATORY_YAW_MAPPING_IDENTIFIABLE"
    assert gate["stage_a"]["stage_b_permitted"] is True
    assert not gate["stage_a"]["new_yaw_or_candidate_neural_execution_before_decision"]
    assert not gate["directional_evidence"]["physical_gain_identified"]
    assert not gate["directional_evidence"][
        "linearity_or_bilateral_subtraction_measured"
    ]
    assert all(
        e["url"].startswith("https://") and e["locators"]
        for e in gate["evidence_sources"]
    )
    assert len({e["id"] for e in gate["evidence_sources"]}) == 3
    assert "Biological yaw prediction" in gate["forbidden_claims"]
    assert not gate["exclusions"]["structural_count_is_body_efficacy"]
    for name, key, id_key, authority_key in [
        ("neurofly_v1_scientific_status.json", "status", "status_id", "v1_status_id"),
        (
            "second_circuit_selection_gate.json",
            "selection",
            "selection_id",
            "phase24_selection_id",
        ),
        (
            "hs_dnp15_network_context_audit.json",
            "audit",
            "audit_id",
            "phase26_audit_id",
        ),
    ]:
        record = json.loads((model.SCIENCE_ROOT / name).read_bytes())
        assert (
            canonical_sha256(record[key])
            == record[id_key]
            == gate["authorities"][authority_key]
        )


def test_frozen_preregistration_and_model_role(artifact):
    p = model.load_preregistration()
    assert canonical_sha256(p) == model.PREREGISTRATION_ID
    assert artifact["config"]["preregistration"] == p
    assert artifact["artifact_id"] == ARTIFACT_ID
    assert (
        p["frozen_before_yaw_execution"] and not p["output_based_parameter_selection"]
    )
    assert p["yaw_mapping"]["directional_sign"] == 1
    assert p["yaw_mapping"]["scale_status"] == "EXPLORATORY_BOUNDED_ASSUMPTION"
    assert p["orientation_model"]["normalization_horizon_ms"] == p["duration_ms"]
    assert (
        p["orientation_model"]["normalization"]
        == "GLOBAL_FIXED_SOURCE_HORIZON; NOT_PER_CONDITION"
    )
    assert p["analytical_bounds"]["absolute_orientation_horizon_bound"] == 2
    assert artifact["result"]["model_role"] == "EXPLORATORY_NEURAL_TO_ORIENTATION_MODEL"
    assert artifact["result"]["units"]["orientation"] == "yaw_orientation_eq"
    assert artifact["result"]["units"]["yaw_drive"] == "yaw_drive_eq"
    assert artifact["result"]["translation"] == "NOT_MODELLED"
    assert artifact["result"]["sensory_feedback"] == "NONE"
    for run in artifact["result"]["runs"]:
        assert (
            not {"x", "z", "force", "torque", "yaw_rate", "actuator", "spikes"}
            & run.keys()
        )
        assert run["yaw_orientation_eq"][0] == 0
        assert len(run["yaw_orientation_eq"]) == 501
        assert all(abs(v) <= 2 for v in run["yaw_orientation_eq"])


def test_exact_neural_authority_no_resampling_or_feedback(artifact):
    source = replay_neural_artifact(model.SOURCE_ROOT / model.SOURCE_ID)
    assert artifact["config"]["source_result_sha256"] == source["result_sha256"]
    assert artifact["result"]["time_ms"] == source["result"]["time_ms"]
    for output, neural in zip(
        artifact["result"]["runs"], source["result"]["runs"], strict=True
    ):
        assert output["condition_id"] == neural["condition_id"]
        assert output["dnp15_states"] == neural["target_states"]
        assert output["bilateral_differential"] == neural["right_minus_left_diagnostic"]
        for n, state in enumerate(output["dnp15_states"]):
            assert output["yaw_drive_eq"][n] == state[0] - state[1]
    assert model.build_yaw_artifact() == artifact


def test_neutral_matched_side_swap_and_reversal_invariants(artifact):
    runs = {r["condition_id"]: r for r in artifact["result"]["runs"]}
    for condition in ("NO_MOTION_CONTROL", "BILATERAL_MATCHED_MOTION"):
        assert all(v == 0 for v in runs[condition]["bilateral_differential"])
        assert all(v == 0 for v in runs[condition]["yaw_drive_eq"])
        assert all(v == 0 for v in runs[condition]["yaw_orientation_eq"])
    right = runs["RIGHT_SIDE_MOTION"]
    for condition in (
        "LEFT_SIDE_MOTION",
        "SIDE_SWAPPED_EQUIVALENT",
        "DIRECTION_REVERSED",
    ):
        for field in ("bilateral_differential", "yaw_drive_eq", "yaw_orientation_eq"):
            assert runs[condition][field] == [-value for value in right[field]]
    # Causal ordering from frozen inputs, not a desired biological latency.
    assert right["yaw_orientation_eq"][:3] == [0, 0, 0]
    times = artifact["result"]["time_ms"]
    assert right["yaw_orientation_eq"][3] == (
        (times[3] - times[2]) / 50 * right["yaw_drive_eq"][2]
    )


def test_final_boundary_and_global_normalization():
    p = model.load_preregistration()
    differential, drive, orientation = model.integrate_orientation(
        [0, 0.1], [[0.5, 0], [1, 0]], p
    )
    assert differential == drive == [0.5, 1]
    assert orientation == [0, 0.001]  # Final sample has no outgoing interval.
    _, _, neutral = model.integrate_orientation([0, 0.1], [[0, 0], [1, 0]], p)
    assert neutral == [0, 0]


def test_structural_counts_never_enter_orientation(artifact):
    source = replay_neural_artifact(model.SOURCE_ROOT / model.SOURCE_ID)
    changed = copy.deepcopy(source)
    for edge in changed["config"]["preregistration"]["selected_routes"]:
        edge["structural_count"] *= 1001
    # TEST_ONLY provenance mutation: not submitted as a canonical source.
    p = model.load_preregistration()
    for original, altered in zip(
        source["result"]["runs"], changed["result"]["runs"], strict=True
    ):
        assert model.integrate_orientation(
            source["result"]["time_ms"], original["target_states"], p
        ) == model.integrate_orientation(
            changed["result"]["time_ms"], altered["target_states"], p
        )
    assert (
        p["body_policy"]["recurrence"]
        == p["body_policy"]["electrical_coupling"]
        == "NONE"
    )
    assert p["body_policy"]["translation"] == "NOT_MODELLED; NO_X_Z_STATE"
    assert p["body_policy"]["sensory_feedback"] == "NONE"


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), True, 1.1, -1.1])
def test_invalid_neural_inputs_fail_without_clamping(bad):
    with pytest.raises(ValueError):
        model.integrate_orientation(
            [0, 0.1], [[bad, 0], [0, 0]], model.load_preregistration()
        )


@pytest.mark.parametrize("times", [[0, 0], [1, 2], [0, 51], [0, float("nan")]])
def test_invalid_time_domain(times):
    with pytest.raises(ValueError):
        model.integrate_orientation(
            times, [[0, 0], [0, 0]], model.load_preregistration()
        )


@pytest.mark.parametrize("field", ["sign", "gain", "gate"])
def test_preregistration_mutation_changes_identity_and_is_rejected(tmp_path, field):
    p = copy.deepcopy(model.load_preregistration())
    if field == "sign":
        p["yaw_mapping"]["directional_sign"] *= -1
    elif field == "gain":
        p["yaw_mapping"]["dnp15_to_yaw_proxy_scale"] = 0.5
    else:
        p["evidence_gate_id"] = "0" * 64
    assert canonical_sha256(p) != model.PREREGISTRATION_ID
    path = tmp_path / "test_only_preregistration.json"
    path.write_bytes(canonical_json_bytes(p))
    with pytest.raises(ValueError, match="preregistration mismatch"):
        model.load_preregistration(path)
    # No alternate-gain/sign trajectories executed.


def _write_self_consistent_test_artifact(root, changed):
    changed["config_sha256"] = canonical_sha256(changed["config"])
    changed["result_sha256"] = canonical_sha256(changed["result"])
    changed["artifact_id"] = canonical_sha256(
        [model.ARTIFACT_SCHEMA, changed["config_sha256"], changed["result_sha256"]]
    )
    path = root / changed["artifact_id"]
    path.mkdir()
    (path / "orientation.json").write_bytes(canonical_json_bytes(changed, newline=True))
    (path / "manifest.json").write_bytes(
        canonical_json_bytes(_manifest(changed), newline=True)
    )
    return path


@pytest.mark.parametrize(
    "mutation",
    [
        "authority",
        "sign",
        "gain",
        "condition",
        "input",
        "differential",
        "drive",
        "orientation",
        "time",
        "result_hash",
    ],
)
def test_offline_replay_rejects_self_consistent_tampering(artifact, tmp_path, mutation):
    changed = copy.deepcopy(artifact)
    run = changed["result"]["runs"][2]
    if mutation == "authority":
        changed["config"]["source_artifact_id"] = "0" * 64
    elif mutation == "sign":
        changed["config"]["preregistration"]["yaw_mapping"]["directional_sign"] = -1
    elif mutation == "gain":
        changed["config"]["preregistration"]["yaw_mapping"][
            "dnp15_to_yaw_proxy_scale"
        ] = 0.5
    elif mutation == "condition":
        run["condition_id"] = "NOT_PREREGISTERED"
    elif mutation == "input":
        run["dnp15_states"][10][0] += 0.01
    elif mutation in ("differential", "drive", "orientation"):
        key = {
            "differential": "bilateral_differential",
            "drive": "yaw_drive_eq",
            "orientation": "yaw_orientation_eq",
        }[mutation]
        run[key][10] += 0.01
    elif mutation == "time":
        changed["result"]["time_ms"][10] += 0.01
    else:
        changed["result_sha256"] = "0" * 64
        with pytest.raises(ValueError, match="differs"):
            model.validate_yaw_artifact(changed)
        return
    path = _write_self_consistent_test_artifact(tmp_path, changed)
    assert changed["artifact_id"] != ARTIFACT_ID
    with pytest.raises(ValueError, match="differs"):
        replay_yaw_artifact(path)


def test_gate_tampering_blocks_stage_b(tmp_path):
    wrapper = json.loads(model.GATE_PATH.read_bytes())
    wrapper["gate"]["stage_a"]["stage_b_permitted"] = False
    wrapper["gate_id"] = canonical_sha256(wrapper["gate"])
    path = tmp_path / "gate.json"
    path.write_bytes(canonical_json_bytes(wrapper))
    with pytest.raises(ValueError, match="gate mismatch"):
        model.load_evidence_gate(path)


def test_blocked_gate_creates_no_yaw_execution_or_artifact(tmp_path, monkeypatch):
    def blocked():
        raise ValueError("evidence gate blocked")

    monkeypatch.setattr(model, "load_evidence_gate", blocked)
    monkeypatch.setattr(
        model, "integrate_orientation", lambda *args: pytest.fail("yaw before gate")
    )
    output = tmp_path / "not_created"
    with pytest.raises(ValueError, match="gate blocked"):
        generate_yaw_artifact(output_root=output)
    assert not output.exists()


def test_changed_source_trajectory_invalidates_source_replay(
    artifact, tmp_path, monkeypatch
):
    source = replay_neural_artifact(model.SOURCE_ROOT / model.SOURCE_ID)
    changed = copy.deepcopy(source)
    changed["result"]["runs"][2]["target_states"][10][0] += 0.01
    path = tmp_path / model.SOURCE_ID
    path.mkdir()
    from neurofly.hs_dnp15_neural_validation_artifacts import (
        _manifest as source_manifest,
    )

    (path / "validation.json").write_bytes(canonical_json_bytes(changed, newline=True))
    (path / "manifest.json").write_bytes(
        canonical_json_bytes(source_manifest(changed), newline=True)
    )
    monkeypatch.setattr(model, "SOURCE_ROOT", tmp_path)
    with pytest.raises(ValueError):
        model.build_yaw_artifact()


def test_cli_generation_replay_and_no_override_path(artifact, tmp_path, capsys):
    path = generate_yaw_artifact(output_root=tmp_path)
    assert path.name == ARTIFACT_ID
    assert main(["inspect", str(path)]) == 0
    assert ARTIFACT_ID in json.loads(capsys.readouterr().out)["artifact_id"]
    assert main(["replay", str(path)]) == 0
    capsys.readouterr()
    assert main(["replay", str(tmp_path / "absent")]) == 2
    with pytest.raises(SystemExit):
        main(["generate", "--gain", "2"])


def test_no_api_ui_or_v1_plant_dependency():
    source = (ROOT / "src/neurofly/dnp15_exploratory_yaw.py").read_text()
    for forbidden in (
        "planar_body_plant",
        "ttm_actuator",
        "http_api",
        "scenario_playback_api",
        "proxy_step",
        "route_contributions",
    ):
        assert forbidden not in source
