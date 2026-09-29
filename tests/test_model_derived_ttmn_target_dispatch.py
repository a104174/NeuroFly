"""Phase 8O model-derived TTMn output to pinned target dispatch tests."""

from __future__ import annotations

import copy
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from neurofly.model_derived_ttmn_target_dispatch import (
    DEFAULT_PHASE8N_ARTIFACT,
    DEFAULT_TARGET_CONTRACT_PATH,
    DISPATCH_PROVENANCE,
    DISPATCH_SCHEMA_VERSION,
    EXPECTED_PHASE8N_ARTIFACT_ID,
    EXPECTED_TARGET_CONTRACT_ID,
    ModelDerivedTTMnDispatchError,
    _target_contract,
    _validate_event,
    canonical_sha256,
    execute_reference_battery,
    validate_and_replay_payload,
)
from neurofly.model_derived_ttmn_target_dispatch_artifacts import (
    ModelDerivedTTMnTargetArtifactError,
    generate_model_derived_ttmn_target_artifact,
    load_model_derived_ttmn_target_artifact,
    replay_model_derived_ttmn_target_artifact,
)
from neurofly.synthetic_motor_target_dispatch import (
    DEFAULT_TARGET_CONTRACT_PATH as PHASE8L_TARGET_CONTRACT_PATH,
)
from neurofly.synthetic_motor_target_dispatch import (
    SyntheticMotorTargetDispatchError,
    dispatch_fixture_config,
    target_association_id,
)
from neurofly.synthetic_motor_target_dispatch_artifacts import (
    replay_synthetic_motor_target_artifact,
)
from neurofly.synthetic_ttmn_output_rule import OUTPUT_EVENT_PROVENANCE
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    DEFAULT_SOURCE_ARTIFACT as DEFAULT_PHASE8B_ARTIFACT,
)
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    generate_synthetic_ttmn_output_artifact,
    replay_synthetic_ttmn_output_artifact,
)

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "data" / "derived"
PHASE8L_ARTIFACT = (
    SOURCE_ROOT
    / "malecns"
    / "looming_giant_fiber_v1"
    / "synthetic_motor_target_dispatch_v1"
    / "8e53c6bd224a82c9cbef2b51a82fc917fe993da73ff64cc4c894870dfc4abff8"
)


@pytest.fixture(scope="module")
def phase8n_source():
    return replay_synthetic_ttmn_output_artifact(
        DEFAULT_PHASE8N_ARTIFACT,
        source_artifact=DEFAULT_PHASE8B_ARTIFACT,
    )


def _fixture(result: dict, fixture_id: str) -> dict:
    return next(row for row in result["fixtures"] if row["fixture_id"] == fixture_id)


def _rehash_event(event: dict) -> dict:
    value = copy.deepcopy(event)
    value["event_id"] = canonical_sha256(
        {key: item for key, item in value.items() if key != "event_id"}
    )
    return value


def test_canonical_child_artifacts_remain_unchanged(phase8n_source) -> None:
    assert phase8n_source.artifact_id == EXPECTED_PHASE8N_ARTIFACT_ID
    assert phase8n_source.config["config_sha256"] == (
        "43ddd7fba90235f7331c4c53ee774810956b9b55a9dc4c3ddc94bb4887283ea8"
    )
    assert phase8n_source.result["result_sha256"] == (
        "de54e2657560ae77a83b46174e029f7449008f968b0e0f4391cea8ec7a07c7b5"
    )
    target = _target_contract(DEFAULT_TARGET_CONTRACT_PATH)[0]
    assert target["contract_id"] == EXPECTED_TARGET_CONTRACT_ID
    assert target["contract_sha256"] == (
        "9816a180acc845c202f70e374a4de951536296fed979c21c12d796792b8bac1f"
    )
    historical = replay_synthetic_motor_target_artifact(PHASE8L_ARTIFACT)
    assert historical.artifact_id == (
        "8e53c6bd224a82c9cbef2b51a82fc917fe993da73ff64cc4c894870dfc4abff8"
    )
    assert historical.config["config_sha256"] == (
        "736371154db08e2f587b2c7f2484be6ce9c249b5098bd7ac2e7d8196c207edb0"
    )
    assert historical.result["result_sha256"] == (
        "ac57f2c7385869a6954b4aac2578afb6857333d1ea47a75541b29811c5a21462"
    )


def test_reference_dispatch_matches_all_phase8n_events_once(phase8n_source) -> None:
    config, result = execute_reference_battery(phase8n_source)
    expected = {
        "ZERO_EVENT_CONTROL": (0, []),
        "RIGHT_SINGLE_EVENT": (1, [(800146, 10, 1.0)]),
        "LEFT_SINGLE_EVENT": (1, [(804642, 10, 1.0)]),
        "BILATERAL_SIMULTANEOUS_EVENT": (
            2,
            [(800146, 10, 1.0), (804642, 10, 1.0)],
        ),
        "RIGHT_REPEATED_EVENTS": (
            2,
            [(800146, 10, 1.0), (800146, 30, 3.0)],
        ),
        "LEFT_REPEATED_EVENTS": (
            2,
            [(804642, 10, 1.0), (804642, 30, 3.0)],
        ),
    }
    assert [row["fixture_id"] for row in result["fixtures"]] == list(expected)
    for fixture_id, (count, expected_boundaries) in expected.items():
        row = _fixture(result, fixture_id)
        events = row["origin_output_events"]
        dispatches = row["dispatch_records"]
        actual_boundaries = [
            (item["motor_neuron_body_id"], item["step"], item["time_ms"])
            for item in events
        ]
        assert len(events) == len(dispatches) == count
        assert actual_boundaries == expected_boundaries
        assert [item["origin_output_event_id"] for item in dispatches] == [
            item["event_id"] for item in events
        ]
        for event, dispatch in zip(events, dispatches, strict=True):
            assert dispatch["step"] == event["step"]
            assert dispatch["time_ms"] == event["time_ms"]
            assert dispatch["source_output_artifact_id"] == phase8n_source.artifact_id
            assert (
                dispatch["source_output_result_sha256"]
                == phase8n_source.result["result_sha256"]
            )
            assert dispatch["source_fixture_id"] == fixture_id
    assert result["summary"]["model_derived_output_event_count"] == 8
    assert result["summary"]["dispatch_record_count"] == 8
    assert result["summary"]["per_body_event_counts"] == {
        "800146": 4,
        "804642": 4,
    }
    assert result["summary"]["target_class_counts"] == {"TTM": 8}
    assert result["summary"]["all_events_dispatched_once"] is True
    assert result["summary"]["no_dlm_dispatches"] is True
    assert config["source_ttmn_output_artifact"]["artifact_id"] == (
        EXPECTED_PHASE8N_ARTIFACT_ID
    )
    source_event = _fixture(result, "RIGHT_SINGLE_EVENT")["origin_output_events"][0]
    assert config["source_generator"]["generator_kind"] == (
        "TTMN_THRESHOLD_CROSSING_V1"
    )
    assert (
        config["source_generator"]["config_sha256"]
        == source_event["generator_config_sha256"]
    )
    assert (
        config["source_phase6c_model_identity"]["config_sha256"]
        == (source_event["source_model"]["config_sha256"])
    )
    bilateral = _fixture(result, "BILATERAL_SIMULTANEOUS_EVENT")
    assert len({event["event_id"] for event in bilateral["origin_output_events"]}) == 2
    assert (
        len({row["origin_output_event_id"] for row in bilateral["dispatch_records"]})
        == 2
    )
    repeated = _fixture(result, "RIGHT_REPEATED_EVENTS")
    assert [row["step"] for row in repeated["dispatch_records"]] == [10, 30]
    assert len({row["dispatch_id"] for row in repeated["dispatch_records"]}) == 2


def test_dispatch_copies_exact_phase8k_target_and_lineage(phase8n_source) -> None:
    _, result = execute_reference_battery(phase8n_source)
    contract, _ = _target_contract()
    associations = {
        row["motor_neuron_body_id"]: row for row in contract["target_associations"]
    }
    dispatches = [
        row for fixture in result["fixtures"] for row in fixture["dispatch_records"]
    ]
    assert len(dispatches) == 8
    assert {row["motor_neuron_type"] for row in dispatches} == {"TTMn"}
    assert {row["target_class"] for row in dispatches} == {"TTM"}
    for dispatch in dispatches:
        target = associations[dispatch["motor_neuron_body_id"]]
        assert dispatch["schema_version"] == DISPATCH_SCHEMA_VERSION
        assert dispatch["provenance_kind"] == DISPATCH_PROVENANCE
        assert dispatch["origin_provenance_kind"] == OUTPUT_EVENT_PROVENANCE
        assert dispatch["upstream_provenance_kind"] == (
            "SYNTHETIC_MOTOR_INTERFACE_TEST"
        )
        assert dispatch["target_association_id"] == target_association_id(target)
        for key in (
            "target_class",
            "target_group",
            "exact_target",
            "exact_muscle_fiber",
            "muscle_target_side",
            "muscle_target_side_status",
            "target_granularity",
            "mapping_confidence",
            "evidence_refs",
            "unresolved_fields",
            "unresolved_reasons",
        ):
            assert dispatch[key] == target[key]
        assert dispatch["mapping_confidence"] == "HIGH"
        assert dispatch["muscle_target_side_status"] == (
            "QUALIFIED_LITERATURE_IPSILATERAL_CLASS_INFERENCE"
        )
        assert dispatch["exact_target"] is None
        assert dispatch["exact_muscle_fiber"] is None
        assert dispatch["time_semantics"] == (
            "SAME_STORED_BOUNDARY_TARGET_DISPATCH_BOOKKEEPING_ONLY"
        )
        assert dispatch["dispatch_semantics"] == (
            "TARGET_ASSOCIATION_RECEIPT_ONLY_NO_MUSCLE_DYNAMICS"
        )


def test_wrong_generator_provenance_and_dlmn_events_fail_closed(phase8n_source) -> None:
    source_config = copy.deepcopy(dict(phase8n_source.config))
    source_fixture = copy.deepcopy(dict(phase8n_source.result["fixtures"][1]))
    source_fixture["source_artifact_id"] = phase8n_source.result["source_artifact_id"]
    source_fixture["source_result_sha256"] = phase8n_source.result[
        "source_result_sha256"
    ]
    contract, _ = _target_contract()
    event = copy.deepcopy(source_fixture["reference_output_events"][0])
    invalid_variants = []
    for key, value in (
        ("generator_kind", "OTHER_GENERATOR"),
        ("provenance_kind", "SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST"),
        ("upstream_provenance_kind", "SIMULATED_FROM_SENSORY_EXPERIMENT"),
        ("motor_neuron_body_id", 801295),
        ("motor_neuron_type", "DLMn a, b"),
        ("neural_side", "L"),
        ("step", 11),
        ("time_ms", 99.0),
    ):
        changed = copy.deepcopy(event)
        changed[key] = value
        invalid_variants.append(_rehash_event(changed))
    phase8l_source = replay_synthetic_motor_target_artifact(PHASE8L_ARTIFACT)
    phase8l_event = phase8l_source.result["fixtures"][1]["origin_output_events"][0]
    invalid_variants.append(copy.deepcopy(phase8l_event))
    for invalid in invalid_variants:
        with pytest.raises(ModelDerivedTTMnDispatchError):
            _validate_event(
                invalid,
                fixture=source_fixture,
                source=phase8n_source,
                source_config=source_config,
                contract=contract,
            )


def test_source_hash_and_contract_mismatch_fail_closed(
    phase8n_source, tmp_path
) -> None:
    different = generate_synthetic_ttmn_output_artifact(
        source_artifact=DEFAULT_PHASE8B_ARTIFACT,
        output_root=tmp_path / "different-8n",
        threshold_dimensionless=0.2,
    )
    with pytest.raises(ModelDerivedTTMnDispatchError):
        execute_reference_battery(different)
    with pytest.raises(ModelDerivedTTMnDispatchError):
        execute_reference_battery(phase8n_source, tmp_path / "missing-contract")


def test_deterministic_artifact_replay_and_tampering_rejection(
    phase8n_source, tmp_path
) -> None:
    first = generate_model_derived_ttmn_target_artifact(output_root=tmp_path / "out")
    second = generate_model_derived_ttmn_target_artifact(output_root=tmp_path / "out")
    replayed = replay_model_derived_ttmn_target_artifact(first.path)
    assert first.artifact_id == second.artifact_id == replayed.artifact_id
    assert first.artifact_id == (
        "3bc011f9a8831f5291b6078d6132ef0dc6d6d7e87cc45ecfaa957ec80b8af360"
    )
    assert first.config["config_sha256"] == second.config["config_sha256"]
    assert first.result["result_sha256"] == second.result["result_sha256"]
    assert first.config["config_sha256"] == (
        "79624d65a8aba4885c66791b4f40fe4f31e050e4fc70e794ea475af2e3881261"
    )
    assert first.result["result_sha256"] == (
        "0d3826ffc4ef35246d48da9bbe586afc82b1cebb64beebbb1618e8f01f81fbcc"
    )
    assert first.summary()["artifact_bytes"] == 47480
    assert first.summary()["model_derived_output_event_count"] == 8
    assert first.summary()["dispatch_record_count"] == 8

    _, payload = execute_reference_battery(phase8n_source)
    tampered = copy.deepcopy(payload)
    tampered["fixtures"][1]["dispatch_records"][0]["target_class"] = "DLM"
    with pytest.raises(ModelDerivedTTMnDispatchError):
        validate_and_replay_payload(dict(first.config), tampered, phase8n_source)

    copied = tmp_path / "tampered-artifact"
    shutil.copytree(first.path, copied)
    result_path = copied / "dispatch_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["fixtures"][1]["origin_output_events"][0]["time_ms"] = 2.0
    result_path.write_text(
        json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ModelDerivedTTMnTargetArtifactError):
        load_model_derived_ttmn_target_artifact(copied)


def test_phase8n_source_artifact_identity_mutation_is_rejected(phase8n_source) -> None:
    altered = replace(phase8n_source, artifact_id="0" * 64)
    with pytest.raises(ModelDerivedTTMnDispatchError):
        execute_reference_battery(altered)


def test_target_resolution_is_shared_but_phase8l_artifact_identity_is_fixed(
    phase8n_source,
) -> None:
    assert PHASE8L_TARGET_CONTRACT_PATH == DEFAULT_TARGET_CONTRACT_PATH
    # This directly uses the same resolver called by both 8L and 8O; changing
    # only the input provenance is not an accepted 8L fixture operation.
    config, result = execute_reference_battery(phase8n_source)
    assert config["dispatch_schema_version"] == DISPATCH_SCHEMA_VERSION
    assert result["summary"]["dispatch_record_count"] == 8
    artifact = replay_synthetic_motor_target_artifact(PHASE8L_ARTIFACT)
    assert artifact.artifact_id == (
        "8e53c6bd224a82c9cbef2b51a82fc917fe993da73ff64cc4c894870dfc4abff8"
    )
    phase8n_fixture = copy.deepcopy(dict(phase8n_source.result["fixtures"][1]))
    phase8n_fixture["fixture_id"] = "TTMN_RIGHT_SINGLE"
    with pytest.raises(SyntheticMotorTargetDispatchError):
        dispatch_fixture_config(phase8n_fixture)
