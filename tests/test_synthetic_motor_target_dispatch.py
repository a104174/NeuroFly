"""Phase 8L synthetic motor-neuron output to target-dispatch tests."""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from neurofly.malecns.contract import load_circuit_contract
from neurofly.motor_neuron_muscle_contract import (
    replay_motor_neuron_muscle_target_artifact,
)
from neurofly.psi_dlmn_event_relay import (
    DEFAULT_MOTOR_CONTRACT_PATH,
    execute_reference_relay,
    load_pinned_motor_contract,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_motor_interface import (
    execute_reference_battery as execute_ttmn_battery,
)
from neurofly.synthetic_motor_target_dispatch import (
    DEFAULT_TARGET_CONTRACT_PATH,
    DISPATCH_PROVENANCE,
    DISPATCH_SCHEMA_VERSION,
    EXPECTED_TARGET_CONTRACT_ID,
    FIXTURE_IDS,
    OUTPUT_EVENT_SCHEMA_VERSION,
    SYNTHETIC_OUTPUT_PROVENANCE,
    SyntheticMotorTargetDispatchError,
    build_reference_config,
    canonical_sha256,
    dispatch_fixture_config,
    execute_reference_battery,
    fixture_result,
    validate_and_replay_payload,
)
from neurofly.synthetic_motor_target_dispatch_artifacts import (
    SyntheticMotorTargetArtifactError,
    generate_synthetic_motor_target_artifact,
    load_synthetic_motor_target_artifact,
    replay_synthetic_motor_target_artifact,
)

TARGET_IDS = {
    800146,
    804642,
    801295,
    801970,
    800718,
    800890,
    801895,
    803013,
    801998,
    802544,
    803048,
    1050014552,
}
DATA_ROOT = DEFAULT_SOURCE_ROOT


def _target_records() -> dict[int, dict]:
    artifact = replay_motor_neuron_muscle_target_artifact(DEFAULT_TARGET_CONTRACT_PATH)
    return {
        row["motor_neuron_body_id"]: row
        for row in artifact.contract["target_associations"]
    }


def _fixture(result: dict, fixture_id: str) -> dict:
    return next(row for row in result["fixtures"] if row["fixture_id"] == fixture_id)


def test_reference_target_contract_and_fixture_battery_are_exact() -> None:
    records = _target_records()
    config, result = execute_reference_battery()
    assert EXPECTED_TARGET_CONTRACT_ID == (
        "5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0"
    )
    assert set(records) == TARGET_IDS
    assert config["target_contract_id"] == EXPECTED_TARGET_CONTRACT_ID
    assert config["authorized_motor_neuron_count"] == 12
    assert tuple(config["fixture_ids"]) == FIXTURE_IDS
    assert [row["fixture_id"] for row in result["fixtures"]] == list(FIXTURE_IDS)
    assert result["summary"]["fixture_count"] == 8
    assert config["config_sha256"] == canonical_sha256(
        {key: value for key, value in config.items() if key != "config_sha256"}
    )


def test_zero_fixture_has_no_background_dispatch() -> None:
    result = fixture_result("ZERO_EVENT_CONTROL")
    assert result["origin_output_events"] == []
    assert result["dispatch_records"] == []
    assert result["summary"]["origin_event_count"] == 0
    assert result["summary"]["dispatch_record_count"] == 0


@pytest.mark.parametrize(
    ("fixture_id", "body_id", "target_class", "target_group", "side_status"),
    [
        (
            "TTMN_RIGHT_SINGLE",
            800146,
            "TTM",
            None,
            "QUALIFIED_LITERATURE_IPSILATERAL_CLASS_INFERENCE",
        ),
        (
            "TTMN_LEFT_SINGLE",
            804642,
            "TTM",
            None,
            "QUALIFIED_LITERATURE_IPSILATERAL_CLASS_INFERENCE",
        ),
        ("DLMN_AB_RIGHT_SINGLE", 801295, "DLM", "a,b", "UNRESOLVED"),
        ("DLMN_AB_LEFT_SINGLE", 801970, "DLM", "a,b", "UNRESOLVED"),
        ("DLMN_CF_LEFT_SINGLE", 800718, "DLM", "c-f", "UNRESOLVED"),
        ("DLMN_CF_RIGHT_SINGLE", 801998, "DLM", "c-f", "UNRESOLVED"),
    ],
)
def test_single_body_dispatch_copies_exact_target_association(
    fixture_id: str,
    body_id: int,
    target_class: str,
    target_group: str | None,
    side_status: str,
) -> None:
    result = fixture_result(fixture_id)
    assert len(result["origin_output_events"]) == 1
    assert len(result["dispatch_records"]) == 1
    event = result["origin_output_events"][0]
    dispatch = result["dispatch_records"][0]
    target = _target_records()[body_id]
    assert event["schema_version"] == OUTPUT_EVENT_SCHEMA_VERSION
    assert event["provenance_kind"] == SYNTHETIC_OUTPUT_PROVENANCE
    assert event["event_semantics"] == "SYNTHETIC_ABSTRACT_MOTOR_NEURON_OUTPUT_EVENT"
    assert event["motor_neuron_body_id"] == body_id
    assert dispatch["schema_version"] == DISPATCH_SCHEMA_VERSION
    assert dispatch["provenance_kind"] == DISPATCH_PROVENANCE
    assert dispatch["origin_provenance_kind"] == SYNTHETIC_OUTPUT_PROVENANCE
    assert dispatch["origin_output_event_id"] == event["event_id"]
    assert dispatch["motor_neuron_body_id"] == body_id
    assert dispatch["target_class"] == target_class
    assert dispatch["target_group"] == target_group
    assert dispatch["target_granularity"] == target["target_granularity"]
    assert dispatch["mapping_confidence"] == target["mapping_confidence"]
    assert dispatch["muscle_target_side"] == target["muscle_target_side"]
    assert dispatch["muscle_target_side_status"] == side_status
    assert dispatch["unresolved_fields"] == target["unresolved_fields"]
    assert dispatch["unresolved_reasons"] == target["unresolved_reasons"]
    assert dispatch["step"] == event["step"]
    assert dispatch["time_ms"] == event["time_ms"] == event["step"] * 0.1
    assert dispatch["dispatch_semantics"] == (
        "TARGET_SELECTION_RECEIPT_ONLY_NO_MUSCLE_DYNAMICS"
    )


def test_all_twelve_bodies_resolve_once_without_fiber_or_side_inference() -> None:
    records = _target_records()
    result = _fixture(execute_reference_battery()[1], "ALL_12_SIMULTANEOUS")
    assert len(result["origin_output_events"]) == 12
    assert len(result["dispatch_records"]) == 12
    assert {
        row["motor_neuron_body_id"] for row in result["dispatch_records"]
    } == TARGET_IDS
    assert len({row["dispatch_id"] for row in result["dispatch_records"]}) == 12
    for row in result["dispatch_records"]:
        source = records[row["motor_neuron_body_id"]]
        assert row["target_class"] == source["target_class"]
        assert row["target_group"] == source["target_group"]
        assert row["target_granularity"] == source["target_granularity"]
        assert row["exact_target"] is None
        assert row["exact_muscle_fiber"] is None
        assert row["muscle_target_side"] == source["muscle_target_side"]
        if source["motor_neuron_type"].startswith("DLMn"):
            assert row["muscle_target_side"] is None
            assert row["muscle_target_side_status"] == "UNRESOLVED"
            assert "exact_muscle_fiber" in row["unresolved_fields"]


def test_target_fields_are_not_dynamic_quantities() -> None:
    config, result = execute_reference_battery()
    forbidden = {
        "gain",
        "delay",
        "tau",
        "activation",
        "force",
        "threshold",
        "contraction",
        "voltage",
        "calcium",
    }

    def keys(value):
        if isinstance(value, dict):
            for key, nested in value.items():
                yield key
                yield from keys(nested)
        elif isinstance(value, list):
            for nested in value:
                yield from keys(nested)

    assert not forbidden.intersection(keys(config))
    assert not forbidden.intersection(keys(result))
    assert config["muscle_dynamics"] == "NO_MUSCLE_DYNAMICS"
    assert config["current_model_output_conversion"] is False


def test_invalid_identity_provenance_timing_and_duplicate_mutations_fail_closed() -> (
    None
):
    config = build_reference_config()
    original = next(
        row for row in config["fixtures"] if row["fixture_id"] == "TTMN_RIGHT_SINGLE"
    )
    mutations = (
        lambda row: row["events"][0].update(motor_neuron_body_id=10001),
        lambda row: row["events"][0].update(motor_neuron_type="DLMn c-f"),
        lambda row: row["events"][0].update(neural_side="L"),
        lambda row: row["events"][0].update(
            provenance_kind="SIMULATED_FROM_SENSORY_EXPERIMENT"
        ),
        lambda row: row["events"][0].update(time_ms=1.0000001),
        lambda row: row["events"][0].update(step=-1),
        lambda row: row["events"].append(copy.deepcopy(row["events"][0])),
    )
    for mutate in mutations:
        tampered = copy.deepcopy(original)
        mutate(tampered)
        with pytest.raises(SyntheticMotorTargetDispatchError):
            dispatch_fixture_config(tampered)
    with pytest.raises(SyntheticMotorTargetDispatchError):
        dispatch_fixture_config({"fixture_id": "TTMN_RIGHT_SINGLE", "events": []})
    with pytest.raises(SyntheticMotorTargetDispatchError):
        fixture_result("UNKNOWN_BODY_FIXTURE")


def test_phase6c_state_and_phase8g_receipt_are_not_accepted_as_fixture_inputs() -> None:
    circuit_contract = load_circuit_contract(DATA_ROOT)
    _, ttmn_result = execute_ttmn_battery(circuit_contract)
    motor_contract = load_pinned_motor_contract(DEFAULT_MOTOR_CONTRACT_PATH)
    _, relay_result = execute_reference_relay(motor_contract)
    ttmn_child_fixture = next(
        row
        for row in ttmn_result["fixtures"]
        if row["fixture_id"] == "RIGHT_SINGLE_EVENT"
    )
    relay_child_fixture = next(
        row
        for row in relay_result["fixtures"]
        if row["fixture_id"] == "RIGHT_SINGLE_EVENT"
    )
    with pytest.raises(SyntheticMotorTargetDispatchError):
        dispatch_fixture_config(ttmn_child_fixture)
    with pytest.raises(SyntheticMotorTargetDispatchError):
        dispatch_fixture_config(relay_child_fixture)


def test_deterministic_replay_and_payload_tampering_rejection(tmp_path: Path) -> None:
    config, result = execute_reference_battery()
    expected_config, expected_result = validate_and_replay_payload(config, result)
    assert expected_config == config
    assert expected_result == result
    first = generate_synthetic_motor_target_artifact(output_root=tmp_path / "out")
    second = generate_synthetic_motor_target_artifact(output_root=tmp_path / "out")
    replayed = replay_synthetic_motor_target_artifact(first.path)
    assert first.artifact_id == second.artifact_id == replayed.artifact_id
    assert first.config["config_sha256"] == config["config_sha256"]
    assert first.result["result_sha256"] == result["result_sha256"]
    assert (
        load_synthetic_motor_target_artifact(first.path).summary()[
            "total_dispatch_records"
        ]
        == 18
    )

    copied = tmp_path / "tampered"
    shutil.copytree(first.path, copied)
    result_path = copied / "dispatch_result.json"
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    payload["fixtures"][1]["dispatch_records"][0]["target_class"] = "fake"
    result_path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SyntheticMotorTargetArtifactError):
        load_synthetic_motor_target_artifact(copied)


def test_wrong_target_contract_path_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(SyntheticMotorTargetDispatchError):
        build_reference_config(tmp_path / "missing-target-contract")


def test_tampered_target_association_is_rejected_before_dispatch(
    tmp_path: Path,
) -> None:
    copied = tmp_path / "tampered-target-contract"
    shutil.copytree(DEFAULT_TARGET_CONTRACT_PATH, copied)
    contract_path = copied / "target_contract.json"
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    payload["target_associations"][0]["mapping_confidence"] = "LOW"
    contract_path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SyntheticMotorTargetDispatchError):
        fixture_result("TTMN_RIGHT_SINGLE", copied)
