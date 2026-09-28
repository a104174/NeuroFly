from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from neurofly.motor_neural_contract import load_pinned_artifact
from neurofly.motor_neuron_muscle_contract import (
    CONTRACT_FILENAME,
    DEFAULT_OUTPUT_ROOT,
    MotorNeuronMuscleContractError,
    build_motor_neuron_muscle_target_contract,
    export_motor_neuron_muscle_target_artifact,
    generate_motor_neuron_muscle_target_artifact,
    load_motor_neuron_muscle_target_artifact,
    replay_motor_neuron_muscle_target_artifact,
)
from neurofly.psi_dlmn_event_relay import DEFAULT_MOTOR_CONTRACT_PATH

EXPECTED_MOTOR_IDS = {
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


def _pinned_motor_contract() -> dict:
    return load_pinned_artifact(DEFAULT_MOTOR_CONTRACT_PATH)


def _records(contract: dict) -> dict[int, dict]:
    return {row["motor_neuron_body_id"]: row for row in contract["target_associations"]}


def test_contract_uses_exact_source_motor_neurons_and_expected_target_groups() -> None:
    contract = build_motor_neuron_muscle_target_contract(_pinned_motor_contract())
    records = _records(contract)
    assert set(records) == EXPECTED_MOTOR_IDS
    assert len(records) == 12
    assert contract["node_counts"] == {
        "TTMn": 2,
        "DLMn_a_b": 2,
        "DLMn_c_f": 8,
        "total": 12,
    }
    assert {records[body]["target_class"] for body in (800146, 804642)} == {"TTM"}
    assert {records[body]["target_group"] for body in (801295, 801970)} == {"a,b"}
    assert {
        records[body]["target_group"]
        for body in (800718, 800890, 801895, 803013, 801998, 802544, 803048, 1050014552)
    } == {"c-f"}
    assert len(contract["target_associations"]) == len(records)


def test_laterality_is_explicit_and_dlm_side_is_not_copied_from_neural_side() -> None:
    records = _records(
        build_motor_neuron_muscle_target_contract(_pinned_motor_contract())
    )
    for body_id in (800146, 804642):
        row = records[body_id]
        assert row["muscle_target_side"] == row["neural_side"]
        assert (
            row["muscle_target_side_status"]
            == "QUALIFIED_LITERATURE_IPSILATERAL_CLASS_INFERENCE"
        )
        assert (
            row["muscle_target_side_basis"]
            == "EXPLICIT_TTMN_IPSILATERAL_PATHWAY_EVIDENCE"
        )
    for body_id in EXPECTED_MOTOR_IDS - {800146, 804642}:
        row = records[body_id]
        assert row["neural_side"] in {"L", "R"}
        assert row["muscle_target_side"] is None
        assert row["muscle_target_side_status"] == "UNRESOLVED"
        assert "muscle_target_side" in row["unresolved_fields"]


def test_contract_separates_identity_evidence_from_literature_association() -> None:
    contract = build_motor_neuron_muscle_target_contract(_pinned_motor_contract())
    refs = {
        row["evidence_id"]: row
        for row in contract["mapping_policy"]["evidence_sources"]
    }
    assert {row["evidence_kind"] for row in refs.values()} == {"PRIMARY_LITERATURE"}
    for row in contract["target_associations"]:
        assert row["neural_identity_evidence_class"] == "MALECNS_NEURAL_IDENTITY"
        assert row["evidence_classification"] == "PRIMARY_LITERATURE_TARGET_EVIDENCE"
        assert (
            row["association_relation"]
            == "LITERATURE_SUPPORTED_MUSCLE_TARGET_ASSOCIATION"
        )
        assert row["malecns_peripheral_muscle_edge_present"] is False
        assert row["evidence_refs"]
        assert row["exact_target"] is None
        assert row["exact_muscle_fiber"] is None
        assert all(ref in refs for ref in row["evidence_refs"])
    assert contract["source_identity"]["motor_neural_contract_id"] == (
        "a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c"
    )


def test_contract_has_no_dynamic_or_muscle_output_fields() -> None:
    contract = build_motor_neuron_muscle_target_contract(_pinned_motor_contract())
    forbidden = {
        "gain",
        "delay",
        "delay_ms",
        "tau",
        "threshold",
        "state",
        "voltage",
        "spike_conversion",
        "activation",
        "contraction",
        "force",
        "torque",
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

    assert not (forbidden & set(keys(contract)))
    assert contract["contract_semantics"] == (
        "NO_DYNAMICS_LITERATURE_SUPPORTED_TARGET_ASSOCIATIONS"
    )
    assert contract["mapping_policy"]["dynamics"] == "NO_DYNAMICS"


def test_contract_fails_closed_on_source_population_or_mapping_tampering(
    tmp_path: Path,
) -> None:
    pinned = _pinned_motor_contract()
    expected = build_motor_neuron_muscle_target_contract(pinned)
    for mutation in (
        lambda row: row.update(motor_neuron_body_id=999),
        lambda row: row.update(motor_neural_contract_id="wrong"),
        lambda row: row.update(target_class="wing"),
        lambda row: row.update(target_granularity="EXACT_FIBER"),
        lambda row: row.update(mapping_confidence="CERTAIN"),
        lambda row: row.update(exact_muscle_fiber="invented"),
        lambda row: row.update(muscle_target_side="R"),
        lambda row: row.update(evidence_refs=[]),
    ):
        tampered = copy.deepcopy(expected)
        mutation(tampered["target_associations"][0])
        with pytest.raises(MotorNeuronMuscleContractError):
            export_motor_neuron_muscle_target_artifact(
                tampered,
                tmp_path / f"bad-{len(list(tmp_path.iterdir()))}",
                pinned_motor_contract=pinned,
            )
    missing_node = copy.deepcopy(pinned)
    missing_node["contract"]["nodes"] = [
        row for row in missing_node["contract"]["nodes"] if row["body_id"] != 800146
    ]
    with pytest.raises(MotorNeuronMuscleContractError):
        build_motor_neuron_muscle_target_contract(missing_node)


def test_generation_and_offline_replay_are_deterministic(tmp_path: Path) -> None:
    first = generate_motor_neuron_muscle_target_artifact(output_root=tmp_path)
    second = generate_motor_neuron_muscle_target_artifact(output_root=tmp_path)
    replayed = replay_motor_neuron_muscle_target_artifact(first.path)
    assert first.artifact_id == second.artifact_id == replayed.artifact_id
    assert first.contract["contract_sha256"] == second.contract["contract_sha256"]
    assert dict(first.contract) == dict(replayed.contract)
    assert first.path.parent == tmp_path
    loaded = load_motor_neuron_muscle_target_artifact(first.path)
    assert loaded.summary()["target_association_count"] == 12


def test_artifact_tampering_and_source_contract_mismatch_are_rejected(
    tmp_path: Path,
) -> None:
    artifact = generate_motor_neuron_muscle_target_artifact(output_root=tmp_path)
    contract_path = artifact.path / CONTRACT_FILENAME
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    payload["target_associations"][0]["target_class"] = "tampered"
    contract_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(MotorNeuronMuscleContractError):
        load_motor_neuron_muscle_target_artifact(artifact.path)
    with pytest.raises(MotorNeuronMuscleContractError):
        replay_motor_neuron_muscle_target_artifact(
            artifact.path,
            motor_contract_path=DEFAULT_OUTPUT_ROOT / "missing-source-contract",
        )
