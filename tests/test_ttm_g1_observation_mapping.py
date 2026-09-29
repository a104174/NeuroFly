"""Phase 8U gates: future comparability metadata with no operator execution."""

from __future__ import annotations

import copy
import json
import socket
from pathlib import Path

import pytest

from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_observation_mapping import (
    DEFAULT_SOURCE_ARTIFACT,
    SOURCE_ID,
    SOURCE_OBSERVATION_IDS,
    TTMG1ObservationMappingError,
    artifact_id,
    build_mapping_contract,
    mapping_id,
    validate_mapping_contract,
    validated_source,
)
from neurofly.ttm_g1_observation_mapping_artifacts import (
    TTMG1MappingArtifactError,
    export_ttm_g1_mapping_artifact,
    generate_ttm_g1_mapping_artifact,
    replay_ttm_g1_mapping_artifact,
)
from neurofly.ttm_g1_observation_mapping_cli import main


def _rehash(contract: dict) -> None:
    for row in contract["result"]["mappings"]:
        row["mapping_id"] = mapping_id(row)
    contract["config_sha256"] = canonical_sha256(contract["config"])
    contract["result_sha256"] = canonical_sha256(contract["result"])
    contract["contract_id"] = artifact_id(
        contract["config_sha256"], contract["result_sha256"]
    )


def _keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _keys(child)


def test_exact_source_order_one_to_one_coverage_and_no_ready_records() -> None:
    contract = build_mapping_contract()
    rows = contract["result"]["mappings"]
    assert len(rows) == len(set(row["mapping_id"] for row in rows)) == 9
    assert tuple(row["observation_id"] for row in rows) == SOURCE_OBSERVATION_IDS
    assert (
        tuple(
            row["observation_id"]
            for row in validated_source()["result"]["observations"]
        )
        == SOURCE_OBSERVATION_IDS
    )
    assert contract["config"]["source_observation_contract"]["contract_id"] == SOURCE_ID
    assert contract["result"]["formal_ready_mapping_count"] == 0
    for row in rows:
        assert row["current_model_produces_quantity"] is False
        assert row["formal_comparison_ready"] is False
        assert row["operator_executable"] is False
    assert validate_mapping_contract(contract) == contract


def test_pinned_hashes_and_mapping_identities() -> None:
    contract = build_mapping_contract()
    assert contract["contract_id"] == (
        "f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f"
    )
    assert contract["config_sha256"] == (
        "5b7752ee0577a2f072fecc3b2713df116f7758a308825cd18ab1041d6c862f0e"
    )
    assert contract["result_sha256"] == (
        "661cca4291351fc003fcc2ce0b1ec629047cc5e7ad9442a801e3cf9085eea1d0"
    )
    assert [row["mapping_id"] for row in contract["result"]["mappings"]] == [
        "ttm-g1-map-9a2671f1c090550f7650",
        "ttm-g1-map-5da7ca6dd5fcb7b35f3f",
        "ttm-g1-map-2cbbf530608a91760b87",
        "ttm-g1-map-cdf252596e108903b638",
        "ttm-g1-map-487694b2e2ebc9aecae5",
        "ttm-g1-map-72d04f7808be7c08c15e",
        "ttm-g1-map-2ffdcc9a27aa934e746c",
        "ttm-g1-map-33e3c83e533b880cd95b",
        "ttm-g1-map-0a731ae2f1c668d2606e",
    ]


def test_specific_blockers_and_context_status_are_preserved() -> None:
    rows = build_mapping_contract()["result"]["mappings"]
    required = {
        0: {"DESCRIPTIVE_SOURCE_NO_NUMERICAL_COMPARISON_RULE"},
        1: {"SOURCE_PROTOCOL_INCOMPLETE", "SOURCE_AMPLITUDE_OPERATION_UNRESOLVED"},
        2: {"RELEASE_SEMANTICS_ABSENT"},
        4: {"RELEASE_SEMANTICS_ABSENT", "SOURCE_CORRECTION_PIPELINE_ABSENT"},
        5: {"SPONTANEOUS_PROCESS_ABSENT", "OBSERVATION_INTERVAL_UNRESOLVED"},
        6: {"HISTORY_DYNAMICS_ABSENT", "DEPRESSION_DEFINITION_UNRESOLVED"},
        7: {"VESICLE_MODEL_ABSENT", "HISTORY_DYNAMICS_ABSENT"},
        8: {"SYSTEM_BOUNDARY_TOO_NARROW", "ONSET_DETECTOR_UNRESOLVED"},
    }
    for index, codes in required.items():
        assert codes <= set(rows[index]["blockers"])
    assert rows[3]["candidate_operator_kind"] == "CONTEXT_ONLY"
    assert rows[3]["comparison_role"] == "ANALYSIS_CONTEXT_ONLY"
    assert rows[3]["required_model_quantity"] == "NO_DIRECT_MODEL_QUANTITY"
    assert rows[8]["comparability"] == "SYSTEM_BOUNDARY_MISMATCH"
    assert "INPUT_SEMANTICS_UNDEFINED" in rows[1]["blockers"]


def test_protocol_requirements_reference_source_and_never_match_unknowns() -> None:
    rows = build_mapping_contract()["result"]["mappings"]
    for row in rows:
        requirements = row["protocol_requirements"]
        assert requirements["source_observation_id"] == row["observation_id"]
        assert requirements["match_status"] == "NOT_EVALUATED"
        assert "NEVER_WILDCARD" in requirements["unknown_source_policy"]
        assert requirements["biological_scope_ref"] == "biological_scope"
    assert {"temperature_c", "genotype"} <= set(
        rows[5]["protocol_requirements"]["required_dimensions"]
    )
    assert {
        "temperature_c",
        "genotype",
        "preparation",
        "stimulation_frequency_hz",
        "stimulus_count",
        "recycling_condition",
    } <= set(rows[6]["protocol_requirements"]["required_dimensions"])
    assert {"developmental_age", "stimulation_site", "recording_site"} <= set(
        rows[8]["protocol_requirements"]["required_dimensions"]
    )
    assert (
        "CONTROL_CONDITION"
        in rows[8]["protocol_requirements"]["required_additional_semantics"]
    )


def test_no_values_parameters_runtime_or_calibration_fields() -> None:
    keys = set(_keys(build_mapping_contract()))
    assert not keys & {
        "value",
        "units",
        "uncertainty_value",
        "gain",
        "tau",
        "conductance",
        "threshold",
        "delay",
        "release_probability",
        "activation",
        "force",
        "model_v_rest",
        "tolerance",
        "loss",
        "calibration_target",
    }


@pytest.mark.parametrize(
    ("index", "field", "replacement"),
    [
        (0, "observation_id", "unknown"),
        (0, "required_model_quantity", "PHASE8Q_RECEIPT_COUNT"),
        (0, "candidate_operator_kind", "EXECUTABLE_BASELINE"),
        (0, "operator_status", "READY"),
        (0, "operator_executable", True),
        (0, "comparability", "DIRECT_NUMERICAL_COMPARISON_READY"),
        (0, "comparison_role", "CALIBRATION_TARGET"),
        (0, "blockers", []),
        (0, "current_model_produces_quantity", True),
        (0, "formal_comparison_ready", True),
        (1, "operator_status", "CANDIDATE_ONLY"),
        (2, "required_model_quantity", "G1_MEMBRANE_VOLTAGE_TRACE"),
        (3, "candidate_operator_kind", "PEAK_EVOKED_DEFLECTION"),
        (4, "required_model_quantity", "PHASE8N_OUTPUT_EVENT_COUNT"),
        (6, "amplitude_ratio", 1.0),
        (7, "recovery_tau", 1.0),
        (8, "comparability", "MODEL_OBSERVABLE_WITH_OPERATOR"),
        (8, "blockers", ["MISSING_OBSERVATION_OPERATOR"]),
    ],
)
def test_rehashed_semantic_mutations_fail_closed(index, field, replacement) -> None:
    contract = build_mapping_contract()
    original_id = contract["contract_id"]
    old_mapping_id = contract["result"]["mappings"][index]["mapping_id"]
    contract["result"]["mappings"][index][field] = replacement
    _rehash(contract)
    assert contract["contract_id"] != original_id
    assert contract["result"]["mappings"][index]["mapping_id"] != old_mapping_id
    with pytest.raises(TTMG1ObservationMappingError):
        validate_mapping_contract(contract)


@pytest.mark.parametrize(
    "change",
    [
        "source",
        "readiness",
        "boundary",
        "protocol",
        "order",
        "duplicate",
        "omission",
        "extra",
    ],
)
def test_contract_and_protocol_mutations_fail_even_after_rehash(change) -> None:
    contract = build_mapping_contract()
    rows = contract["result"]["mappings"]
    if change == "source":
        contract["config"]["source_observation_contract"]["contract_id"] = "0" * 64
    elif change == "readiness":
        contract["config"]["readiness_snapshot"]["early_validation_subset"] = "READY"
    elif change == "boundary":
        contract["config"]["scientific_boundary"] = []
    elif change == "protocol":
        rows[5]["protocol_requirements"]["required_dimensions"].remove("temperature_c")
    elif change == "order":
        rows.reverse()
    elif change == "duplicate":
        rows[1] = copy.deepcopy(rows[0])
    elif change == "omission":
        rows.pop()
    else:
        rows.append(copy.deepcopy(rows[0]))
    _rehash(contract)
    with pytest.raises(TTMG1ObservationMappingError):
        validate_mapping_contract(contract)


def test_offline_generation_replay_and_byte_identity(tmp_path, monkeypatch) -> None:
    def no_network(*args, **kwargs):
        raise AssertionError("network used during offline mapping replay")

    monkeypatch.setattr(socket, "create_connection", no_network)
    first = generate_ttm_g1_mapping_artifact(output_root=tmp_path / "first")
    second = generate_ttm_g1_mapping_artifact(output_root=tmp_path / "second")
    assert first.artifact_id == second.artifact_id
    assert replay_ttm_g1_mapping_artifact(first.path).contract == second.contract
    for name in ("mapping_contract.json", "manifest.json"):
        assert (first.path / name).read_bytes() == (second.path / name).read_bytes()
    with pytest.raises(TTMG1MappingArtifactError, match="already exists"):
        export_ttm_g1_mapping_artifact(dict(first.contract), first.path)


def test_mutated_source_is_rejected_without_modifying_canonical_source(
    tmp_path,
) -> None:
    source = tmp_path / DEFAULT_SOURCE_ARTIFACT.name
    source.mkdir()
    for item in DEFAULT_SOURCE_ARTIFACT.iterdir():
        (source / item.name).write_bytes(item.read_bytes())
    payload = json.loads((source / "observation_contract.json").read_bytes())
    payload["result"]["observations"][5]["uncertainty_kind"] = "MEAN_SEM"
    (source / "observation_contract.json").write_bytes(
        canonical_json_bytes(payload, newline=True)
    )
    with pytest.raises((ValueError, RuntimeError)):
        build_mapping_contract(source_artifact=source)
    assert (
        validated_source()["result"]["observations"][5]["uncertainty_kind"]
        == "UNKNOWN_NOT_ESTABLISHED"
    )


def test_artifact_tamper_and_missing_source_rejected(tmp_path) -> None:
    artifact = generate_ttm_g1_mapping_artifact(output_root=tmp_path)
    with pytest.raises((ValueError, RuntimeError)):
        replay_ttm_g1_mapping_artifact(
            artifact.path, source_artifact=tmp_path / "missing"
        )
    raw = dict(artifact.contract)
    raw["result"]["mappings"][8]["operator_status"] = "READY"
    (artifact.path / "mapping_contract.json").write_bytes(
        canonical_json_bytes(raw, newline=True)
    )
    with pytest.raises(TTMG1ObservationMappingError):
        replay_ttm_g1_mapping_artifact(artifact.path)


def test_cli_inspect_joins_source_labels_and_displays_blockers(
    tmp_path, capsys
) -> None:
    assert main(["generate", "--output-root", str(tmp_path)]) == 0
    generated = json.loads(capsys.readouterr().out)
    assert main(["inspect", generated["artifact_path"]]) == 0
    inspected = json.loads(capsys.readouterr().out)
    assert inspected["formal_ready_mapping_count"] == 0
    assert (
        inspected["mappings"][0]["source_quantity_label"]
        == "G1 resting membrane potential"
    )
    assert "SYSTEM_BOUNDARY_TOO_NARROW" in inspected["mappings"][8]["blockers"]
    serialized = json.loads(
        (Path(generated["artifact_path"]) / "mapping_contract.json").read_bytes()
    )
    assert "source_quantity_label" not in serialized["result"]["mappings"][0]
    assert main(["replay", generated["artifact_path"]]) == 0
    capsys.readouterr()
    assert main(["replay", str(tmp_path / "missing")]) == 2
