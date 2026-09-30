"""Admission-only scope, exact source authority, identity and offline replay gates."""

from __future__ import annotations

import copy
import json
import socket

import pytest

from neurofly.ttm_abstract_electrical_input import (
    BOUNDARIES,
    DEFAULT_SOURCE_ARTIFACT,
    INPUT_SEMANTICS,
    PROVENANCE,
    SOURCE_CONFIG_SHA256,
    SOURCE_ID,
    SOURCE_RESULT_SHA256,
    SUCCESS_SEMANTICS,
    TIMING_SEMANTICS,
    TTMAbstractInputError,
    admit_receipts,
    build_input_contract,
    contract_id,
    event_id,
    validate_input_contract,
    validated_source,
)
from neurofly.ttm_abstract_electrical_input_artifacts import (
    CONTRACT_FILENAME,
    TTMAbstractInputArtifactError,
    export_abstract_input_artifact,
    generate_abstract_input_artifact,
    replay_abstract_input_artifact,
)
from neurofly.ttm_abstract_electrical_input_cli import main
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_observation_mapping import DEFAULT_SOURCE_ARTIFACT as OBSERVATIONS
from neurofly.ttm_g1_observation_mapping_artifacts import (
    DEFAULT_ARTIFACT_ROOT as MAPPINGS_ROOT,
)
from neurofly.ttm_g1_observation_mapping_artifacts import (
    replay_ttm_g1_mapping_artifact,
)


@pytest.fixture(scope="module")
def source():
    return validated_source()


@pytest.fixture(scope="module")
def contract():
    return build_input_contract()


def tokens(contract):
    return [token for row in contract["result"]["fixtures"] for token in row["tokens"]]


def rehash(contract):
    for token in tokens(contract):
        token["event_id"] = event_id(token)
    contract["config_sha256"] = canonical_sha256(contract["config"])
    contract["result_sha256"] = canonical_sha256(contract["result"])
    contract["contract_id"] = contract_id(
        contract["config_sha256"], contract["result_sha256"]
    )


def test_reference_counts_source_parent_identity_and_timing(source, contract):
    fixtures = contract["result"]["fixtures"]
    assert [len(row["tokens"]) for row in fixtures] == [0, 1, 1, 2, 2, 2]
    assert [row["fixture_id"] for row in fixtures] == [
        row["fixture_id"] for row in source["fixtures"]
    ]
    assert contract["result"]["summary"] == {
        "receipt_count": 8,
        "token_count": 8,
        "per_body_token_counts": {"800146": 4, "804642": 4},
    }
    assert len({row["event_id"] for row in tokens(contract)}) == 8
    assert len({row["parent_receipt_id"] for row in tokens(contract)}) == 8
    for output, parent in zip(fixtures, source["fixtures"], strict=True):
        assert output["source_receipt_ids"] == [
            row["receipt_id"] for row in parent["receipts"]
        ]
        for token, receipt in zip(output["tokens"], parent["receipts"], strict=True):
            assert token["parent_receipt_id"] == receipt["receipt_id"]
            assert token["origin_output_event_id"] == receipt["origin_output_event_id"]
            assert (token["step"], token["time_ms"]) == (
                receipt["step"],
                receipt["time_ms"],
            )
            for key in ("motor_neuron_body_id", "motor_neuron_type", "neural_side"):
                assert token[key] == receipt[key]
            for key in (
                "target_class",
                "target_granularity",
                "muscle_target_side",
                "muscle_target_side_status",
                "muscle_target_side_basis",
                "mapping_confidence",
                "mapping_confidence_scope",
            ):
                assert token[key] == receipt["target_semantics"][key]
    assert [
        (row["motor_neuron_body_id"], row["step"]) for row in fixtures[3]["tokens"]
    ] == [(800146, 10), (804642, 10)]
    for fixture in fixtures[4:]:
        assert [row["step"] for row in fixture["tokens"]] == [10, 30]


def test_semantics_scope_and_no_physical_fields(contract):
    forbidden = {
        "amplitude",
        "gain",
        "weight",
        "magnitude",
        "current",
        "conductance",
        "voltage",
        "quantal_count",
        "release_success",
        "release_probability",
        "delay_ms",
        "tau",
        "waveform",
        "kernel",
        "capacitance",
        "resistance",
        "fiber",
        "exact_muscle_fiber",
        "exact_target",
        "peripheral_endpoint",
        "g1",
        "g1_target_id",
        "recording_fiber",
    }
    for token in tokens(contract):
        assert not forbidden & token.keys()
        assert token["target_class"] == "TTM"
        assert token["motor_neuron_type"] == "TTMn"
        assert token["input_semantics_kind"] == INPUT_SEMANTICS
        assert token["added_delay_semantics"] == TIMING_SEMANTICS
        assert token["success_semantics"] == SUCCESS_SEMANTICS
        assert token["biological_transmission_success"] == "UNREPRESENTED_NOT_ASSERTED"
        assert (
            token["model_family_semantics"]
            == "NEUTRAL_REQUIRES_SEPARATE_TRANSFORMATION"
        )
        assert token["scientific_boundary"] == list(BOUNDARIES)
        assert token["provenance_kind"] == PROVENANCE
        assert token["parent_provenance_kind"] == "EXPLORATORY_NEUROMUSCULAR_INPUT"
        assert token["provenance_chain"] == [
            "SYNTHETIC_MOTOR_INTERFACE_TEST",
            "PHASE_6C_TTMN_DIMENSIONLESS_EXPLORATORY_STATE",
            "EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT",
            "EXPLORATORY_MUSCLE_TARGET_DISPATCH",
            "EXPLORATORY_NEUROMUSCULAR_INPUT",
            PROVENANCE,
        ]


def test_public_admission_zero_order_duplicates_and_wrong_kinds(source, contract):
    assert admit_receipts([]) == []
    receipts = source["fixtures"][3]["receipts"]
    assert (
        admit_receipts(list(reversed(receipts)))
        == contract["result"]["fixtures"][3]["tokens"]
    )
    for invalid in (
        [receipts[0], receipts[0]],
        [{"schema_version": "muscle_target_dispatch_v1"}],
        [1.0],
        receipts[0],
    ):
        with pytest.raises(TTMAbstractInputError):
            admit_receipts(invalid)


@pytest.mark.parametrize(
    "field,value",
    [
        ("receipt_id", "orphan"),
        ("provenance_kind", "SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST"),
        ("origin_provenance_kind", "SIMULATED_FROM_SENSORY_EXPERIMENT"),
        ("motor_neuron_body_id", 801295),
        ("motor_neuron_type", "DLMn"),
        ("neural_side", "L"),
        ("step", 30),
        ("step", 10.0),
        ("time_ms", True),
        ("time_ms", 2.0),
        ("source_generator_kind", "UNKNOWN"),
        ("target_association_id", "wrong"),
        ("target_contract_id", "wrong"),
        ("source_phase8n_artifact_id", "wrong"),
        ("amplitude", 1.0),
        ("fiber", "G1"),
    ],
)
def test_mutated_receipt_rejected(source, field, value):
    receipt = copy.deepcopy(source["fixtures"][1]["receipts"][0])
    receipt[field] = value
    with pytest.raises(TTMAbstractInputError):
        admit_receipts([receipt])


@pytest.mark.parametrize(
    "field,value",
    [
        ("target_class", "DLM"),
        ("mapping_confidence", "MODERATE"),
        ("muscle_target_side_status", "EXACT"),
        ("exact_muscle_fiber", "G1"),
        ("exact_target", "peripheral-synapse"),
    ],
)
def test_target_mutation_rejected(source, field, value):
    receipt = copy.deepcopy(source["fixtures"][1]["receipts"][0])
    receipt["target_semantics"][field] = value
    with pytest.raises(TTMAbstractInputError):
        admit_receipts([receipt])


@pytest.mark.parametrize(
    "field,value",
    [
        ("parent_receipt_id", "orphan"),
        ("event_id", "wrong"),
        ("motor_neuron_body_id", 804642),
        ("neural_side", "L"),
        ("target_class", "DLM"),
        ("target_association_id", "wrong"),
        ("step", 30),
        ("time_ms", 2),
        ("provenance_kind", "EXPLORATORY_NEUROMUSCULAR_INPUT"),
        ("source_phase8q_artifact_id", "wrong"),
        ("input_semantics_kind", "CURRENT_INPUT"),
        ("added_delay_semantics", "BIOLOGICAL_ZERO_DELAY"),
        ("success_semantics", "RELEASE_SUCCEEDED"),
        ("biological_transmission_success", True),
        ("model_family_semantics", "CONDUCTANCE"),
        ("scientific_boundary", []),
        ("amplitude", 1.0),
        ("gain", 1.0),
        ("delay_ms", 0),
        ("fiber", "G1"),
        ("exact_peripheral_endpoint", "synapse"),
    ],
)
def test_rehashed_token_mutation_rejected(contract, field, value):
    mutated = copy.deepcopy(contract)
    token = tokens(mutated)[0]
    original_identity = token["event_id"]
    token[field] = value
    rehash(mutated)
    if field != "event_id":
        assert token["event_id"] != original_identity
    else:
        token["event_id"] = "wrong"
    with pytest.raises(TTMAbstractInputError):
        validate_input_contract(mutated)


@pytest.mark.parametrize(
    "mutation", ["source", "boundary", "duplicate", "missing", "order"]
)
def test_rehashed_container_mutation_rejected(contract, mutation):
    changed = copy.deepcopy(contract)
    if mutation == "source":
        changed["config"]["source_phase8q"]["artifact_id"] = "wrong"
    elif mutation == "boundary":
        changed["config"]["scientific_boundary"] = []
    elif mutation == "duplicate":
        changed["result"]["fixtures"][1]["tokens"].append(
            copy.deepcopy(tokens(changed)[0])
        )
    elif mutation == "missing":
        changed["result"]["fixtures"][1]["tokens"].clear()
    else:
        changed["result"]["fixtures"].reverse()
    rehash(changed)
    assert changed["contract_id"] != contract["contract_id"]
    with pytest.raises(TTMAbstractInputError):
        validate_input_contract(changed)


def test_offline_byte_determinism_source_failure_and_tamper(
    tmp_path, monkeypatch, contract
):
    def deny_network(*args, **kwargs):
        raise AssertionError("network used")

    monkeypatch.setattr(socket, "create_connection", deny_network)
    monkeypatch.setattr(socket.socket, "connect", deny_network)
    first = generate_abstract_input_artifact(output_root=tmp_path / "one")
    second = generate_abstract_input_artifact(output_root=tmp_path / "two")
    assert first.artifact_id == second.artifact_id == contract["contract_id"]
    assert replay_abstract_input_artifact(first.path).contract == first.contract
    for file in first.path.iterdir():
        assert file.read_bytes() == (second.path / file.name).read_bytes()
    with pytest.raises(TTMAbstractInputArtifactError):
        export_abstract_input_artifact(contract, first.path)
    with pytest.raises(TTMAbstractInputError):
        build_input_contract(source_artifact=tmp_path / "missing")
    path = first.path / CONTRACT_FILENAME
    value = json.loads(path.read_bytes())
    tokens(value)[0]["time_ms"] = 99
    path.write_bytes(canonical_json_bytes(value, newline=True))
    with pytest.raises(TTMAbstractInputError):
        replay_abstract_input_artifact(first.path)


def test_source_artifact_mutation_rejected(tmp_path):
    from shutil import copytree

    damaged = tmp_path / DEFAULT_SOURCE_ARTIFACT.name
    copytree(DEFAULT_SOURCE_ARTIFACT, damaged)
    path = damaged / "receipt_result.json"
    value = json.loads(path.read_bytes())
    value["fixtures"][1]["receipts"][0]["step"] = 30
    path.write_bytes(canonical_json_bytes(value, newline=True))
    with pytest.raises(TTMAbstractInputError):
        build_input_contract(source_artifact=damaged)


def test_historical_source_and_mapping_are_exact(contract):
    assert contract["config"]["source_phase8q"]["artifact_id"] == SOURCE_ID
    assert contract["config"]["source_phase8q"]["config_sha256"] == SOURCE_CONFIG_SHA256
    assert contract["config"]["source_phase8q"]["result_sha256"] == SOURCE_RESULT_SHA256
    mapping = replay_ttm_g1_mapping_artifact(
        MAPPINGS_ROOT
        / "f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f"
    )
    assert mapping.contract["result"]["formal_ready_mapping_count"] == 0
    assert (
        mapping.contract["config_sha256"]
        == "5b7752ee0577a2f072fecc3b2713df116f7758a308825cd18ab1041d6c862f0e"
    )
    assert (
        mapping.contract["result_sha256"]
        == "661cca4291351fc003fcc2ce0b1ec629047cc5e7ad9442a801e3cf9085eea1d0"
    )
    from neurofly.ttm_g1_electrophysiology_observation_artifacts import (
        replay_ttm_g1_observation_artifact,
    )

    observations = replay_ttm_g1_observation_artifact(OBSERVATIONS)
    assert (
        observations.artifact_id
        == "5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f"
    )


def test_cli_generate_inspect_replay_and_error(tmp_path, capsys):
    assert main(["generate", "--output-root", str(tmp_path)]) == 0
    generated = json.loads(capsys.readouterr().out)
    assert main(["inspect", generated["artifact_path"]]) == 0
    inspected = json.loads(capsys.readouterr().out)
    assert len(inspected["tokens"]) == 8
    assert inspected["tokens"][0]["input_semantics_kind"] == INPUT_SEMANTICS
    assert main(["replay", generated["artifact_path"]]) == 0
    assert main(["replay", str(tmp_path / "missing")]) == 2


def test_pinned_contract_and_parent_event_identity_snapshots(source, contract):
    assert (
        contract["contract_id"]
        == "1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa"
    )
    assert (
        contract["config_sha256"]
        == "30f3eccd8d30b36895472abba80351fc2750f244c7685b2d8626314499f1bc81"
    )
    assert (
        contract["result_sha256"]
        == "f61f963bc889c4180882479bffeb8856e514d0cbf954749e4f4747801f3479db"
    )
    parents = [
        row["receipt_id"]
        for fixture in source["fixtures"]
        for row in fixture["receipts"]
    ]
    assert (
        canonical_sha256(parents)
        == "bf796b20c0ab4703421c2fe384743f082adfbb947f95146da637e6a31bb40ad9"
    )
    assert (
        canonical_sha256([row["event_id"] for row in tokens(contract)])
        == "66df4965ec3d3dddd60f984e25388bc4cba5c3a570376db87c623e3efee7c879"
    )


def test_manifest_hash_and_extra_artifact_files_rejected(tmp_path):
    artifact = generate_abstract_input_artifact(output_root=tmp_path)
    manifest_path = artifact.path / "manifest.json"
    original = manifest_path.read_bytes()
    manifest = json.loads(original)
    manifest["result_sha256"] = "wrong"
    manifest_path.write_bytes(canonical_json_bytes(manifest, newline=True))
    with pytest.raises(TTMAbstractInputArtifactError):
        replay_abstract_input_artifact(artifact.path)
    manifest_path.write_bytes(original)
    (artifact.path / "extra.json").write_bytes(b"{}\n")
    with pytest.raises(TTMAbstractInputArtifactError):
        replay_abstract_input_artifact(artifact.path)
