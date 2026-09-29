"""Phase 8Q tests: dispatch-to-TTM-NMJ-input receipt bookkeeping only."""

from __future__ import annotations

import copy
import json
import shutil
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import pytest

from neurofly.synthetic_motor_target_dispatch_artifacts import (
    replay_synthetic_motor_target_artifact,
)
from neurofly.ttm_neuromuscular_input_receipt import (
    EXPECTED_PHASE8N_ARTIFACT_ID,
    EXPECTED_PHASE8O_ARTIFACT_ID,
    EXPECTED_PHASE8O_CONFIG_SHA256,
    EXPECTED_PHASE8O_RESULT_SHA256,
    EXPECTED_TARGET_CONTRACT_SHA256,
    RECEIPT_PROVENANCE,
    RECEIPT_SCHEMA_VERSION,
    TTMNeuromuscularInputReceiptError,
    execute_reference_battery,
    replay_source_dispatch_artifact,
)
from neurofly.ttm_neuromuscular_input_receipt_artifacts import (
    TTMNeuromuscularInputReceiptArtifactError,
    generate_ttm_neuromuscular_input_receipt_artifact,
    load_ttm_neuromuscular_input_receipt_artifact,
    replay_ttm_neuromuscular_input_receipt_artifact,
    validate_and_replay_payload,
)

PHASE8O_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "derived"
    / "malecns"
    / "looming_giant_fiber_v1"
    / "model_derived_ttmn_target_dispatch_artifact_v1"
    / EXPECTED_PHASE8O_ARTIFACT_ID
)
PHASE8L_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "derived"
    / "malecns"
    / "looming_giant_fiber_v1"
    / "synthetic_motor_target_dispatch_v1"
    / "8e53c6bd224a82c9cbef2b51a82fc917fe993da73ff64cc4c894870dfc4abff8"
)
EXPECTED_COUNTS = {
    "ZERO_EVENT_CONTROL": 0,
    "RIGHT_SINGLE_EVENT": 1,
    "LEFT_SINGLE_EVENT": 1,
    "BILATERAL_SIMULTANEOUS_EVENT": 2,
    "RIGHT_REPEATED_EVENTS": 2,
    "LEFT_REPEATED_EVENTS": 2,
}
FORBIDDEN_KEYS = {
    "release_success",
    "release_probability",
    "vesicle_release_count",
    "quantal_content",
    "transmitter_amount",
    "nmj_delay_ms",
    "response_amplitude",
    "amplitude",
    "gain",
    "activation",
    "voltage",
    "calcium",
    "decay",
    "tau",
    "threshold",
    "depression",
    "recovery_tau",
    "vesicle_pool_state",
    "force",
    "contraction",
}


@pytest.fixture(scope="module")
def source():
    return replay_source_dispatch_artifact(PHASE8O_PATH)


def _fixture(result: dict, fixture_id: str) -> dict:
    return next(row for row in result["fixtures"] if row["fixture_id"] == fixture_id)


def _all_receipts(result: dict) -> list[dict]:
    return [receipt for row in result["fixtures"] for receipt in row["receipts"]]


def _recursive_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _recursive_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _recursive_keys(item)


def test_phase8o_source_is_pinned_and_full_battery_yields_one_receipt_per_dispatch(
    source,
) -> None:
    assert source.artifact_id == EXPECTED_PHASE8O_ARTIFACT_ID
    assert source.config["config_sha256"] == EXPECTED_PHASE8O_CONFIG_SHA256
    assert source.result["result_sha256"] == EXPECTED_PHASE8O_RESULT_SHA256

    config, result = execute_reference_battery(source)

    assert config["source_phase8o_artifact"]["artifact_id"] == (
        EXPECTED_PHASE8O_ARTIFACT_ID
    )
    assert config["target_contract"]["contract_sha256"] == (
        EXPECTED_TARGET_CONTRACT_SHA256
    )
    assert [row["fixture_id"] for row in result["fixtures"]] == list(EXPECTED_COUNTS)
    for fixture_id, expected_count in EXPECTED_COUNTS.items():
        fixture = _fixture(result, fixture_id)
        assert fixture["summary"]["dispatch_count"] == expected_count
        assert fixture["summary"]["receipt_count"] == expected_count
        assert fixture["summary"]["each_dispatch_has_one_receipt"] is True
        assert len(fixture["receipts"]) == expected_count

    assert result["summary"]["parent_dispatch_count"] == 8
    assert result["summary"]["receipt_count"] == 8
    assert result["summary"]["per_body_receipt_counts"] == {
        "800146": 4,
        "804642": 4,
    }
    assert result["summary"]["target_class_counts"] == {"TTM": 8}
    assert result["summary"]["all_dispatches_have_one_receipt"] is True
    assert result["summary"]["no_dlm_receipts"] is True


def test_receipts_preserve_dispatch_identity_target_timing_and_full_provenance(
    source,
) -> None:
    _, result = execute_reference_battery(source)
    source_result = source.result
    for fixture, source_fixture in zip(
        result["fixtures"], source_result["fixtures"], strict=True
    ):
        assert fixture["fixture_id"] == source_fixture["fixture_id"]
        assert fixture["source_dispatch_ids"] == [
            row["dispatch_id"] for row in source_fixture["dispatch_records"]
        ]
        for receipt, dispatch in zip(
            fixture["receipts"], source_fixture["dispatch_records"], strict=True
        ):
            assert receipt["schema_version"] == RECEIPT_SCHEMA_VERSION
            assert receipt["parent_dispatch_id"] == dispatch["dispatch_id"]
            assert (
                receipt["origin_output_event_id"] == dispatch["origin_output_event_id"]
            )
            assert receipt["step"] == dispatch["step"]
            assert receipt["time_ms"] == dispatch["time_ms"]
            assert receipt["provenance_kind"] == RECEIPT_PROVENANCE
            assert receipt["upstream_provenance_kind"] == (
                "SYNTHETIC_MOTOR_INTERFACE_TEST"
            )
            assert receipt["origin_provenance_kind"] == (
                "EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT"
            )
            assert receipt["dispatch_provenance_kind"] == (
                "EXPLORATORY_MUSCLE_TARGET_DISPATCH"
            )
            assert receipt["provenance_chain"] == [
                "SYNTHETIC_MOTOR_INTERFACE_TEST",
                "PHASE_6C_TTMN_DIMENSIONLESS_EXPLORATORY_STATE",
                "EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT",
                "EXPLORATORY_MUSCLE_TARGET_DISPATCH",
                "EXPLORATORY_NEUROMUSCULAR_INPUT",
            ]
            assert receipt["source_phase8o_artifact_id"] == (
                EXPECTED_PHASE8O_ARTIFACT_ID
            )
            assert receipt["source_phase8n_artifact_id"] == (
                EXPECTED_PHASE8N_ARTIFACT_ID
            )
            assert receipt["target_contract_id"] == (
                "5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0"
            )
            assert receipt["target_semantics"]["target_class"] == "TTM"
            assert receipt["target_semantics"]["mapping_confidence"] == "HIGH"
            assert receipt["target_semantics"]["target_granularity"] == ("MUSCLE_CLASS")
            assert receipt["target_semantics"]["muscle_target_side_status"] == (
                "QUALIFIED_LITERATURE_IPSILATERAL_CLASS_INFERENCE"
            )
            assert receipt["target_semantics"]["exact_target"] is None
            assert receipt["target_semantics"]["exact_muscle_fiber"] is None
            assert receipt["receipt_semantics"] == (
                "EXPLORATORY_TTM_NMJ_INPUT_HANDOFF_RECEIPT_ONLY"
            )
            assert receipt["boundary"] == (
                "HANDOFF_RECORD_ONLY_NO_RELEASE_OR_MUSCLE_RESPONSE_CLAIM"
            )

    receipt_ids = [row["receipt_id"] for row in _all_receipts(result)]
    assert len(receipt_ids) == len(set(receipt_ids)) == 8


def test_zero_bilateral_and_repeated_receipts_are_not_collapsed(source) -> None:
    _, result = execute_reference_battery(source)
    assert _fixture(result, "ZERO_EVENT_CONTROL")["receipts"] == []

    bilateral = _fixture(result, "BILATERAL_SIMULTANEOUS_EVENT")["receipts"]
    assert len(bilateral) == 2
    assert len({row["motor_neuron_body_id"] for row in bilateral}) == 2
    assert len({row["origin_output_event_id"] for row in bilateral}) == 2
    assert len({row["receipt_id"] for row in bilateral}) == 2
    assert {(row["step"], row["time_ms"]) for row in bilateral} == {(10, 1.0)}

    for fixture_id, expected_body in (
        ("RIGHT_REPEATED_EVENTS", 800146),
        ("LEFT_REPEATED_EVENTS", 804642),
    ):
        repeated = _fixture(result, fixture_id)["receipts"]
        assert [row["motor_neuron_body_id"] for row in repeated] == [
            expected_body,
            expected_body,
        ]
        assert [row["step"] for row in repeated] == [10, 30]
        assert [row["time_ms"] for row in repeated] == [1.0, 3.0]
        assert len({row["origin_output_event_id"] for row in repeated}) == 2
        assert len({row["receipt_id"] for row in repeated}) == 2


def test_receipt_schema_contains_no_release_response_delay_or_state_fields(
    source,
) -> None:
    config, result = execute_reference_battery(source)
    assert not FORBIDDEN_KEYS.intersection(_recursive_keys(config))
    assert not FORBIDDEN_KEYS.intersection(_recursive_keys(result))
    assert config["scientific_boundary"] == {
        "receipt_is_handoff_bookkeeping_only": True,
        "nmj_release_modelled": False,
        "muscle_electrical_response_modelled": False,
        "muscle_state_created": False,
        "nmj_delay_modelled": False,
        "depression_or_recovery_modelled": False,
        "structural_counts_used_numerically": False,
        "dlmn_interface_created": False,
        "production_sensory_source": False,
        "force_or_behavior_modelled": False,
    }


def test_mutated_source_dispatch_provenance_and_dlm_target_fail_closed(source) -> None:
    changed_result = copy.deepcopy(dict(source.result))
    first = next(
        row
        for fixture in changed_result["fixtures"]
        for row in fixture["dispatch_records"]
    )
    first["origin_provenance_kind"] = "SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST"
    mutated_source = replace(source, result=MappingProxyType(changed_result))
    with pytest.raises(TTMNeuromuscularInputReceiptError):
        execute_reference_battery(mutated_source)

    dlmn_result = copy.deepcopy(dict(source.result))
    dlmn = next(
        row
        for fixture in dlmn_result["fixtures"]
        for row in fixture["dispatch_records"]
    )
    dlmn["motor_neuron_type"] = "DLMn c-f"
    dlmn_source = replace(source, result=MappingProxyType(dlmn_result))
    with pytest.raises(TTMNeuromuscularInputReceiptError):
        execute_reference_battery(dlmn_source)


def test_phase8l_synthetic_output_interface_artifact_remains_separate() -> None:
    historical = replay_synthetic_motor_target_artifact(PHASE8L_PATH)
    assert historical.artifact_id == (
        "8e53c6bd224a82c9cbef2b51a82fc917fe993da73ff64cc4c894870dfc4abff8"
    )
    assert historical.config["config_sha256"] == (
        "736371154db08e2f587b2c7f2484be6ce9c249b5098bd7ac2e7d8196c207edb0"
    )
    assert historical.result["result_sha256"] == (
        "ac57f2c7385869a6954b4aac2578afb6857333d1ea47a75541b29811c5a21462"
    )


def test_receipt_artifact_generate_offline_replay_and_tamper_rejection(
    tmp_path,
) -> None:
    artifact = generate_ttm_neuromuscular_input_receipt_artifact(
        source_phase8o_artifact=PHASE8O_PATH,
        output_root=tmp_path / "artifacts",
    )
    assert artifact.artifact_id == (
        "e04803f60304f58d0e6d27fdea5d15debb60358b46721caac09f10165c6df9c4"
    )
    assert artifact.config["config_sha256"] == (
        "826e326e98dda35113f776867561a9bb777f52035cacba104d49eacccd55a8f3"
    )
    assert artifact.result["result_sha256"] == (
        "a243de98a5f67c4a7dd77313524b979f3165812f53f0c4f2b7c3c52288a667dc"
    )
    replayed = replay_ttm_neuromuscular_input_receipt_artifact(
        artifact.path, source_phase8o_artifact=PHASE8O_PATH
    )
    assert replayed.summary() == artifact.summary()

    config = copy.deepcopy(dict(artifact.config))
    result = copy.deepcopy(dict(artifact.result))
    result["fixtures"][1]["receipts"][0]["time_ms"] = 1.01
    with pytest.raises(TTMNeuromuscularInputReceiptArtifactError):
        validate_and_replay_payload(
            config, result, source_phase8o_artifact=PHASE8O_PATH
        )

    tampered_path = tmp_path / "tampered"
    shutil.copytree(artifact.path, tampered_path)
    path = tampered_path / "receipt_result.json"
    tampered = json.loads(path.read_text())
    tampered["summary"]["receipt_count"] = 7
    path.write_text(json.dumps(tampered, sort_keys=True, separators=(",", ":")) + "\n")
    with pytest.raises(TTMNeuromuscularInputReceiptArtifactError):
        load_ttm_neuromuscular_input_receipt_artifact(tampered_path)
