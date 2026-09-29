"""Phase 8N threshold-crossing semantics, provenance, and artifact replay."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from neurofly.motor_pathway import MOTOR_PATHWAY_EVIDENCE, TTMnIntegratorConfig
from neurofly.synthetic_motor_interface_artifacts import (
    generate_synthetic_motor_artifact,
)
from neurofly.synthetic_ttmn_output_rule import (
    GENERATOR_KIND,
    OUTPUT_EVENT_PROVENANCE,
    OUTPUT_EVENT_SCHEMA_VERSION,
    REFERENCE_THRESHOLD_DIMENSIONLESS,
    SENSITIVITY_THRESHOLDS,
    TTMnOutputRuleError,
    _crossing_steps,
    build_generator_config,
    canonical_sha256,
    execute_output_rule,
    validate_and_replay_payload,
)
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    SyntheticTTMnOutputArtifactError,
    generate_synthetic_ttmn_output_artifact,
    load_synthetic_ttmn_output_artifact,
    replay_synthetic_ttmn_output_artifact,
)

DATA_ROOT = Path(__file__).resolve().parents[1] / "data" / "derived"
SOURCE_ROOT = DATA_ROOT / "malecns" / "looming_giant_fiber_v1"


@pytest.fixture(scope="module")
def phase8b_source(tmp_path_factory):
    artifact = generate_synthetic_motor_artifact(
        source_root=SOURCE_ROOT,
        output_root=tmp_path_factory.mktemp("phase8b-source"),
    )
    return artifact


def _fixture(result, fixture_id):
    return next(item for item in result["fixtures"] if item["fixture_id"] == fixture_id)


def _events(fixture, threshold=0.25):
    row = next(
        item
        for item in fixture["sensitivity"]
        if item["threshold_dimensionless"] == threshold
    )
    return row["output_events"]


def _event_pairs(events):
    return [
        (item["motor_neuron_body_id"], item["step"], item["time_ms"]) for item in events
    ]


def test_crossing_rule_equality_rearming_and_downward_decay():
    theta = 0.25
    assert _crossing_steps([0.0, 0.2], theta) == ()  # below -> below
    assert _crossing_steps([0.0, theta], theta) == (1,)  # below -> equal
    assert _crossing_steps([0.0, 0.3], theta) == (1,)  # below -> above
    assert _crossing_steps([theta, 0.3], theta) == ()  # equal -> above
    assert _crossing_steps([0.3, 0.4], theta) == ()  # above -> above
    assert _crossing_steps([0.3, 0.2], theta) == ()  # decay-only downward crossing
    assert _crossing_steps([0.3, 0.2, theta], theta) == (2,)  # re-armed then up
    assert _crossing_steps([0.0, theta, 0.3, 0.4, 0.2, theta, 0.4], theta) == (
        1,
        5,
    )


@pytest.mark.parametrize("threshold", [0.0, -0.1, float("inf"), float("nan"), True])
def test_threshold_rejects_nonpositive_or_nonfinite_values(phase8b_source, threshold):
    with pytest.raises(TTMnOutputRuleError, match="finite and positive"):
        build_generator_config(phase8b_source, threshold)


def test_reference_output_events_use_canonical_phase6c_state(phase8b_source):
    config, result = execute_output_rule(phase8b_source)
    assert config["reference_generator_config"]["threshold_dimensionless"] == 0.25
    assert config["reference_generator_config"]["threshold_classification"] == (
        "MODEL_ASSUMPTION"
    )
    assert config["reference_generator_config"]["source_phase6c_model"]["config"] == (
        TTMnIntegratorConfig().to_dict()
    )
    assert (
        config["source_phase6c_model"]["config"]["parameters"]["event_gain"]["value"]
        == 0.25
    )
    assert (
        config["reference_generator_config"]["parameter_independence"][
            "threshold_is_independent_of_event_gain"
        ]
        is True
    )
    assert config["provenance"]["upstream_input"] == "SYNTHETIC_MOTOR_INTERFACE_TEST"
    assert config["provenance"]["derived_output"] == OUTPUT_EVENT_PROVENANCE
    for child_fixture in phase8b_source.result["fixtures"]:
        output_fixture = _fixture(result, child_fixture["fixture_id"])
        output_trajectories = {
            item["body_id"]: item for item in output_fixture["source_trajectories"]
        }
        for trajectory in child_fixture["ttmn_model_state"]:
            assert output_trajectories[trajectory["body_id"]][
                "trajectory_sha256"
            ] == canonical_sha256(trajectory)

    expected = {
        "ZERO_EVENT_CONTROL": [],
        "RIGHT_SINGLE_EVENT": [(800146, 10, 1.0)],
        "LEFT_SINGLE_EVENT": [(804642, 10, 1.0)],
        "BILATERAL_SIMULTANEOUS_EVENT": [
            (800146, 10, 1.0),
            (804642, 10, 1.0),
        ],
        "RIGHT_REPEATED_EVENTS": [(800146, 10, 1.0), (800146, 30, 3.0)],
        "LEFT_REPEATED_EVENTS": [(804642, 10, 1.0), (804642, 30, 3.0)],
    }
    for fixture_id, event_rows in expected.items():
        fixture = _fixture(result, fixture_id)
        events = fixture["reference_output_events"]
        assert _event_pairs(events) == event_rows
        assert _event_pairs(_events(fixture)) == event_rows
        for event in events:
            assert event["schema_version"] == OUTPUT_EVENT_SCHEMA_VERSION
            assert event["generator_kind"] == GENERATOR_KIND
            assert event["provenance_kind"] == OUTPUT_EVENT_PROVENANCE
            assert event["upstream_provenance_kind"] == "SYNTHETIC_MOTOR_INTERFACE_TEST"
            assert event["biological_action_potential_claim"] is False
            assert "muscle_target" not in event
            assert event["source_result"]["artifact_id"] == phase8b_source.artifact_id
            assert event["source_result"]["fixture_id"] == fixture_id
            assert (
                event["source_result"]["synthetic_run_id"]
                == fixture["synthetic_run_id"]
            )
            assert event["time_ms"] == event["step"] * 0.1
            assert event["event_id"] == canonical_sha256(
                {key: value for key, value in event.items() if key != "event_id"}
            )


def test_threshold_sensitivity_changes_only_output_operator(phase8b_source):
    config, result = execute_output_rule(phase8b_source)
    assert (
        tuple(config["sensitivity_thresholds_dimensionless"]) == SENSITIVITY_THRESHOLDS
    )
    expected = {
        0.20: {
            "RIGHT_SINGLE_EVENT": [(800146, 10, 1.0)],
            "RIGHT_REPEATED_EVENTS": [(800146, 10, 1.0)],
        },
        0.25: {
            "RIGHT_SINGLE_EVENT": [(800146, 10, 1.0)],
            "RIGHT_REPEATED_EVENTS": [(800146, 10, 1.0), (800146, 30, 3.0)],
        },
        0.30: {
            "RIGHT_SINGLE_EVENT": [],
            "RIGHT_REPEATED_EVENTS": [(800146, 30, 3.0)],
        },
        0.50: {"RIGHT_SINGLE_EVENT": [], "RIGHT_REPEATED_EVENTS": []},
    }
    for threshold, fixtures in expected.items():
        for fixture_id, rows in fixtures.items():
            assert (
                _event_pairs(_events(_fixture(result, fixture_id), threshold)) == rows
            )
    assert result["summary"]["sensitivity_output_event_counts"] == {
        "0.2": 6,
        "0.25": 8,
        "0.3": 2,
        "0.5": 0,
    }
    assert _event_pairs(_events(_fixture(result, "LEFT_REPEATED_EVENTS"), 0.30)) == [
        (804642, 30, 3.0)
    ]
    # All sensitivity rows cite the same persisted Phase 6C source result and
    # per-trajectory hashes, so the threshold cannot alter the state trajectory.
    for fixture in result["fixtures"]:
        assert (
            len({row["trajectory_sha256"] for row in fixture["source_trajectories"]})
            == 2
        )
        assert (
            len(
                {
                    item["source_fixture_sha256"]
                    for item in result["fixtures"]
                    if item["fixture_id"] == fixture["fixture_id"]
                }
            )
            == 1
        )
    low = build_generator_config(phase8b_source, 0.20)
    reference = build_generator_config(phase8b_source, 0.25)
    assert low["source_phase6c_model"] == reference["source_phase6c_model"]
    assert canonical_sha256(low) != canonical_sha256(reference)
    low_event = _events(_fixture(result, "RIGHT_SINGLE_EVENT"), 0.20)[0]
    reference_event = _events(_fixture(result, "RIGHT_SINGLE_EVENT"), 0.25)[0]
    assert (
        low_event["motor_neuron_body_id"],
        low_event["step"],
        low_event["time_ms"],
    ) == (
        reference_event["motor_neuron_body_id"],
        reference_event["step"],
        reference_event["time_ms"],
    )
    assert (
        low_event["generator_config_sha256"]
        != reference_event["generator_config_sha256"]
    )
    assert low_event["event_id"] != reference_event["event_id"]


def test_output_is_upward_crossing_not_level_triggered_or_input_passthrough(
    phase8b_source,
):
    _, result = execute_output_rule(phase8b_source)
    repeated = _fixture(result, "RIGHT_REPEATED_EVENTS")
    assert [event["step"] for event in repeated["reference_output_events"]] == [10, 30]
    assert len(repeated["reference_output_events"]) == 2
    repeated_source = next(
        item
        for item in phase8b_source.result["fixtures"]
        if item["fixture_id"] == "RIGHT_REPEATED_EVENTS"
    )
    right_state = next(
        item
        for item in repeated_source["ttmn_model_state"]
        if item["body_id"] == 800146
    )["state"]
    assert right_state[29] < REFERENCE_THRESHOLD_DIMENSIONLESS
    zero = _fixture(result, "ZERO_EVENT_CONTROL")
    assert zero["source_events"] == []
    assert zero["reference_output_events"] == []
    # Same-boundary DNp01 input at step 10 first appears in the input list; the
    # output time is taken from the crossing state boundary, not copied as an
    # unvalidated event record.
    right = _fixture(result, "RIGHT_SINGLE_EVENT")
    assert right["source_events"][0]["step"] == 10
    assert right["reference_output_events"][0]["step"] == 10
    assert right["reference_output_events"][0]["source_model"]["model_id"] == (
        "ttmn_dimensionless_event_integrator"
    )


def test_output_schema_config_identity_and_provenance_are_separate(phase8b_source):
    config_20 = build_generator_config(phase8b_source, 0.20)
    config_25 = build_generator_config(phase8b_source, 0.25)
    config_30 = build_generator_config(phase8b_source, 0.30)
    assert (
        len(
            {
                canonical_sha256(config_20),
                canonical_sha256(config_25),
                canonical_sha256(config_30),
            }
        )
        == 3
    )
    _, result = execute_output_rule(phase8b_source)
    event = _fixture(result, "RIGHT_SINGLE_EVENT")["reference_output_events"][0]
    assert event["provenance_kind"] != "SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST"
    assert event["provenance_kind"] != "SIMULATED_FROM_SENSORY_EXPERIMENT"
    assert event["upstream_provenance_kind"] == "SYNTHETIC_MOTOR_INTERFACE_TEST"
    assert "target" not in event and "muscle_target" not in event
    assert event["motor_neuron_body_id"] in {800146, 804642}
    assert event["motor_neuron_type"] == "TTMn"


def test_only_validated_phase8b_result_is_accepted(phase8b_source):
    with pytest.raises(TTMnOutputRuleError, match="validated Phase 8B"):
        execute_output_rule({"source_kind": "EXPLORATORY_ROUTED_MOTOR_EVENT"})
    wrong_source = type(phase8b_source)(
        path=phase8b_source.path,
        artifact_id="0" * 64,
        config=phase8b_source.config,
        result=phase8b_source.result,
        manifest=phase8b_source.manifest,
    )
    with pytest.raises(TTMnOutputRuleError, match="source artifact identity"):
        execute_output_rule(wrong_source)
    altered_result = deepcopy(dict(phase8b_source.result))
    altered_fixture = altered_result["fixtures"][1]
    altered_fixture["ttmn_model_state"][0]["state"][10] = 0.3
    altered_config = dict(phase8b_source.config)
    fake_source = type(phase8b_source)(
        path=phase8b_source.path,
        artifact_id=phase8b_source.artifact_id,
        config=phase8b_source.config,
        result=altered_result,
        manifest=phase8b_source.manifest,
    )
    with pytest.raises(TTMnOutputRuleError, match="deterministic replay"):
        execute_output_rule(fake_source)
    assert altered_config["source_kind"] == "SYNTHETIC_MOTOR_INTERFACE_TEST"


def test_payload_replay_rejects_rule_source_and_provenance_mutations(phase8b_source):
    config, result = execute_output_rule(phase8b_source)
    changed_config = deepcopy(config)
    changed_config["reference_generator_config"]["crossing_rule"] = (
        "x_current >= threshold_dimensionless"
    )
    with pytest.raises(TTMnOutputRuleError, match="config/source identity"):
        validate_and_replay_payload(changed_config, result, phase8b_source)
    for path, replacement in (
        (("provenance_kind",), "SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST"),
        (("step",), 11),
        (("motor_neuron_body_id",), 801295),
    ):
        changed_result = deepcopy(result)
        event = changed_result["fixtures"][1]["reference_output_events"][0]
        event[path[0]] = replacement
        with pytest.raises(TTMnOutputRuleError, match="results differ"):
            validate_and_replay_payload(config, changed_result, phase8b_source)


def test_artifact_generate_replay_and_tamper_rejection(phase8b_source, tmp_path):
    artifact = generate_synthetic_ttmn_output_artifact(
        source_artifact=phase8b_source.path,
        source_root=SOURCE_ROOT,
        output_root=tmp_path / "phase8n",
    )
    loaded = load_synthetic_ttmn_output_artifact(artifact.path)
    replayed = replay_synthetic_ttmn_output_artifact(
        artifact.path,
        source_artifact=phase8b_source.path,
        source_root=SOURCE_ROOT,
    )
    assert loaded.artifact_id == replayed.artifact_id == artifact.artifact_id
    assert dict(loaded.config) == dict(replayed.config)
    assert dict(loaded.result) == dict(replayed.result)
    assert artifact.summary()["fixture_count"] == 6
    assert artifact.summary()["reference_output_event_count"] == 8

    changed = deepcopy(dict(artifact.result))
    changed["fixtures"][1]["reference_output_events"][0]["step"] += 1
    with pytest.raises(TTMnOutputRuleError, match="results differ"):
        validate_and_replay_payload(dict(artifact.config), changed, phase8b_source)

    result_path = artifact.path / "output_result.json"
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    payload["fixtures"][1]["reference_output_events"][0]["step"] += 1
    result_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SyntheticTTMnOutputArtifactError, match="integrity mismatch"):
        load_synthetic_ttmn_output_artifact(artifact.path)


def test_full_generation_reconstructs_missing_canonical_phase8b_child(tmp_path):
    from neurofly.synthetic_ttmn_output_rule import EXPECTED_PHASE8B_ARTIFACT_ID

    source_path = tmp_path / "reconstructed-phase8b" / EXPECTED_PHASE8B_ARTIFACT_ID
    assert not source_path.exists()
    artifact = generate_synthetic_ttmn_output_artifact(
        source_artifact=source_path,
        source_root=SOURCE_ROOT,
        output_root=tmp_path / "phase8n",
    )
    assert source_path.is_dir()
    assert artifact.result["source_artifact_id"] == EXPECTED_PHASE8B_ARTIFACT_ID
    replayed = replay_synthetic_ttmn_output_artifact(
        artifact.path,
        source_artifact=source_path,
        source_root=SOURCE_ROOT,
    )
    assert replayed.artifact_id == artifact.artifact_id


def test_phase6c_ttmm_identity_contract_is_the_only_generator_population():
    assert {item["body_id"] for item in MOTOR_PATHWAY_EVIDENCE.ttmn_identities} == {
        800146,
        804642,
    }
    assert all(
        item["type"] == "TTMn" for item in MOTOR_PATHWAY_EVIDENCE.ttmn_identities
    )


def test_phase7o_production_source_remains_silent_and_separate():
    from neurofly.sensory_population_execution_artifacts import load_execution_artifact

    phase7o_path = (
        DATA_ROOT
        / "malecns"
        / "looming_giant_fiber_v1"
        / "sensory_population_experiment_311_v1"
        / "99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5"
    )
    phase7o = load_execution_artifact(phase7o_path)
    assert all(
        not target["simulated_spikes"]
        for condition in phase7o.result["conditions"]
        for target in condition["targets"]
    )
