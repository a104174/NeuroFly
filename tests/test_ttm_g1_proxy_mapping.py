"""Phase 8Y proxy metadata gates: no destination or physiology inference."""

from __future__ import annotations

import copy
import json
import shutil
import socket

import pytest

from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_observation_mapping import SOURCE_OBSERVATION_IDS
from neurofly.ttm_g1_proxy_mapping import (
    ASSUMPTION,
    CLASSIFICATION,
    DEFAULT_SOURCE_PATHS,
    INSTANCE_SEMANTICS,
    LATERALITY,
    SOURCE_IDENTITIES,
    TTMG1ProxyError,
    build_proxy_contract,
    contract_id,
    proxy_domain_id,
    source_mapping_id,
    validate_proxy_contract,
    validated_sources,
)
from neurofly.ttm_g1_proxy_mapping_artifacts import (
    CONTRACT_FILENAME,
    MANIFEST_FILENAME,
    TTMG1ProxyArtifactError,
    export_proxy_artifact,
    generate_proxy_artifact,
    replay_proxy_artifact,
)
from neurofly.ttm_g1_proxy_mapping_cli import main

EXPECTED_ID = "030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8"
DOMAIN_ID = "ttm-g1-proxy-domain-057e09a9a9c5b054f7ce"


@pytest.fixture(scope="module")
def canonical():
    return build_proxy_contract()


def _rehash(contract):
    for domain in contract["result"]["proxy_domains"]:
        domain["proxy_domain_id"] = proxy_domain_id(domain)
    for row in contract["result"]["source_mappings"]:
        row["mapping_id"] = source_mapping_id(row)
    contract["config_sha256"] = canonical_sha256(contract["config"])
    contract["result_sha256"] = canonical_sha256(contract["result"])
    contract["contract_id"] = contract_id(
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


def test_one_domain_two_preserved_causal_identities(canonical):
    result = canonical["result"]
    assert result["proxy_domain_count"] == len(result["proxy_domains"]) == 1
    assert result["source_mapping_count"] == len(result["source_mappings"]) == 2
    rows = result["source_mappings"]
    assert [
        (r["source_motor_neuron_body_id"], r["source_neural_side"]) for r in rows
    ] == [(800146, "R"), (804642, "L")]
    assert len({r["mapping_id"] for r in rows}) == 2
    assert len({r["source_ttm_association_id"] for r in rows}) == 2
    assert {r["proxy_domain_id"] for r in rows} == {DOMAIN_ID}
    assert all(r["causal_identity_semantics"] == "PRESERVED_NOT_MERGED" for r in rows)
    assert all(r["mapping_classification"] == CLASSIFICATION for r in rows)
    assert all(r["assumption_classification"] == ASSUMPTION for r in rows)
    assert validate_proxy_contract(canonical) == canonical


def test_domain_is_assumption_not_fiber_instance_or_bilateral_measurement(canonical):
    domain = canonical["result"]["proxy_domains"][0]
    assert domain["laterality_semantics"] == LATERALITY
    assert domain["type_instance_semantics"] == INSTANCE_SEMANTICS
    assert domain["evidence_sharing_semantics"] == "SHARED_EVIDENCE_BASIS"
    assert domain["assumption_classification"] == ASSUMPTION
    assert domain["is_physical_instance"] is False
    assert domain["is_anatomical_destination"] is False
    assert domain["bilateral_physiology_asserted"] is False
    assert "ONE_EXPERIMENTALLY_CHARACTERIZED" in domain["biological_scope"]
    assert "WHOLE_TTM_REPRESENTATION" in domain["prohibited_interpretations"]


def test_observation_partition_and_no_value_or_comparability_duplication(canonical):
    refs = canonical["result"]["proxy_domains"][0]["observation_references"]
    g1 = refs["g1_domain_observation_ids"]
    assert len(g1) == 7
    assert refs["analysis_context_observation_ids"] == [SOURCE_OBSERVATION_IDS[3]]
    assert refs["distinct_system_boundary_observation_ids"] == [
        SOURCE_OBSERVATION_IDS[8]
    ]
    assert set(
        g1
        + refs["analysis_context_observation_ids"]
        + refs["distinct_system_boundary_observation_ids"]
    ) == set(SOURCE_OBSERVATION_IDS)
    assert not {
        "value",
        "units",
        "uncertainty",
        "comparability",
        "blockers",
        "comparison_role",
        "protocol_requirements",
        "formal_comparison_ready",
    } & set(_keys(canonical))


def test_no_model_parameters_runtime_or_physical_instance_fields(canonical):
    assert not {
        "current",
        "conductance",
        "voltage",
        "tau",
        "gain",
        "capacitance",
        "resistance",
        "release_probability",
        "force",
        "threshold",
        "amplitude",
        "delay_ms",
        "tokens",
        "events",
        "physical_instance_id",
        "peripheral_endpoint_id",
        "model_family",
    } & set(_keys(canonical))


def test_evidence_roles_and_access_limits(canonical):
    king, koenig = canonical["config"]["evidence_manifest"]
    assert king["doi"] == "10.1007/BF01205017"
    assert king["roles"] == ["GF_MOTOR_PATHWAY_TO_TTM_CLASS_CONTEXT"]
    assert king["verification_scope"] == "PRIMARY_PUBLISHER_SUMMARY"
    assert koenig["doi"] == "10.1152/jn.01258.2006"
    assert koenig["verification_scope"] == "PUBLISHER_INDEXED_PRIMARY_PASSAGES"
    assert "DIRECT_FULL_PAGE_ACCESS_HTTP_403_IN_PHASE8X" in koenig["limitations"]


def test_historical_sources_remain_exact_and_zero_ready(canonical):
    sources = validated_sources()
    for name, source in sources.items():
        assert source["contract_id"] == SOURCE_IDENTITIES[name][1]
    assert sources["phase8u"]["result"]["formal_ready_mapping_count"] == 0
    assert len(sources["phase8s"]["result"]["observations"]) == 9
    assert sources["phase8w"]["result"]["summary"]["token_count"] == 8
    for fixture in sources["phase8w"]["result"]["fixtures"]:
        for token in fixture["tokens"]:
            assert (
                not {"proxy_domain_id", "g1", "fiber", "observation_ids"} & token.keys()
            )
    assert canonical["config"]["sources"]["phase8w"]["result_sha256"] == (
        "f61f963bc889c4180882479bffeb8856e514d0cbf954749e4f4747801f3479db"
    )


def test_pinned_ids_hashes_and_order(canonical):
    assert canonical["contract_id"] == EXPECTED_ID
    assert (
        canonical["config_sha256"]
        == "c94121f3ea0b5092b4943c8daedb7cd220b5b4edd96d04f5a1883d3e487bbe52"
    )
    assert (
        canonical["result_sha256"]
        == "d81bac4965be55d94c5a37938ac088df6961a02f9d5f5a8df4c59a0a8f7e1025"
    )
    assert canonical["result"]["proxy_domains"][0]["proxy_domain_id"] == DOMAIN_ID
    assert [r["mapping_id"] for r in canonical["result"]["source_mappings"]] == [
        "ttm-g1-proxy-map-225e2206304a02050c08",
        "ttm-g1-proxy-map-ed72e23f25c37cc4a516",
    ]


@pytest.mark.parametrize(
    "field,value",
    [
        ("domain_kind", "ANATOMICAL_G1_TARGET"),
        ("mapping_classification", "ANATOMICAL_MAPPING"),
        ("laterality_semantics", "LEFT_G1_PHYSIOLOGY"),
        ("type_instance_semantics", "SHARED_PHYSICAL_G1"),
        ("is_physical_instance", True),
        ("is_anatomical_destination", True),
        ("bilateral_physiology_asserted", True),
        ("biological_scope", "WHOLE_TTM"),
        ("assumption_classification", "MEASURED"),
        ("evidence_refs", []),
        ("evidence_basis_sha256", "0" * 64),
        ("prohibited_interpretations", []),
        ("physical_instance_id", "g1_left_physical"),
        ("permitted_uses", ["MODEL_PARAMETERS"]),
    ],
)
def test_rehashed_domain_tamper_rejected(canonical, field, value):
    altered = copy.deepcopy(canonical)
    domain = altered["result"]["proxy_domains"][0]
    domain[field] = value
    assert proxy_domain_id(domain) != DOMAIN_ID
    _rehash(altered)
    assert altered["contract_id"] != canonical["contract_id"]
    with pytest.raises(TTMG1ProxyError):
        validate_proxy_contract(altered)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_motor_neuron_body_id", 804642),
        ("source_motor_neuron_type", "DLMn"),
        ("source_neural_side", "L"),
        ("source_target_class", "DLM"),
        ("source_ttm_association_id", "fabricated"),
        ("proxy_domain_id", "fabricated"),
        ("mapping_classification", "EXACT_TARGET"),
        ("assumption_classification", "PERIPHERAL_TRACING"),
        ("causal_identity_semantics", "MERGED"),
        ("unresolved_fields", []),
    ],
)
def test_rehashed_source_link_tamper_rejected(canonical, field, value):
    altered = copy.deepcopy(canonical)
    row = altered["result"]["source_mappings"][0]
    row[field] = value
    assert (
        source_mapping_id(row)
        != canonical["result"]["source_mappings"][0]["mapping_id"]
    )
    _rehash(altered)
    with pytest.raises(TTMG1ProxyError):
        validate_proxy_contract(altered)


@pytest.mark.parametrize(
    "mutation",
    [
        "sources",
        "evidence",
        "snapshot",
        "exclusions",
        "boundaries",
        "duplicate",
        "omit",
        "extra_domain",
        "order",
    ],
)
def test_rehashed_contract_semantic_drift_rejected(canonical, mutation):
    altered = copy.deepcopy(canonical)
    config, result = altered["config"], altered["result"]
    if mutation == "sources":
        for source in config["sources"].values():
            source["contract_id"] = "0" * 64
    elif mutation == "evidence":
        config["evidence_manifest"][0]["roles"] = ["EXACT_G1_DESTINATION"]
    elif mutation == "snapshot":
        config["decision_snapshot"]["upstream_token"] = "ADD_G1_TO_TOKEN"
    elif mutation == "exclusions":
        config["exclusions"] = []
    elif mutation == "boundaries":
        config["scientific_boundary"] = []
    elif mutation == "duplicate":
        result["source_mappings"][1] = copy.deepcopy(result["source_mappings"][0])
    elif mutation == "omit":
        result["source_mappings"].pop()
    elif mutation == "extra_domain":
        result["proxy_domains"].append(copy.deepcopy(result["proxy_domains"][0]))
    else:
        result["source_mappings"].reverse()
    _rehash(altered)
    with pytest.raises(TTMG1ProxyError):
        validate_proxy_contract(altered)


@pytest.mark.parametrize("phase", list(DEFAULT_SOURCE_PATHS))
def test_mutated_persisted_source_rejected(tmp_path, phase):
    source = DEFAULT_SOURCE_PATHS[phase]
    copied = tmp_path / source.name
    shutil.copytree(source, copied)
    path = copied / "manifest.json"
    value = json.loads(path.read_bytes())
    value["artifact_id"] = "0" * 64
    path.write_bytes(canonical_json_bytes(value, newline=True))
    paths = {**DEFAULT_SOURCE_PATHS, phase: copied}
    with pytest.raises(ValueError):
        build_proxy_contract(source_paths=paths)


def test_offline_byte_equivalent_generation_replay_and_immutable_export(
    tmp_path, monkeypatch, canonical
):
    def forbidden(*args, **kwargs):
        raise AssertionError("network forbidden")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    a = generate_proxy_artifact(output_root=tmp_path / "a")
    b = generate_proxy_artifact(output_root=tmp_path / "b")
    assert a.artifact_id == b.artifact_id == EXPECTED_ID
    assert dict(replay_proxy_artifact(a.path).contract) == canonical
    for name in (CONTRACT_FILENAME, MANIFEST_FILENAME):
        assert (a.path / name).read_bytes() == (b.path / name).read_bytes()
    with pytest.raises(TTMG1ProxyArtifactError):
        export_proxy_artifact(canonical, a.path)
    assert (
        generate_proxy_artifact(output_root=tmp_path / "a").artifact_id == EXPECTED_ID
    )


@pytest.mark.parametrize(
    "mutation", ["record", "manifest", "extra_file", "noncanonical", "wrong_directory"]
)
def test_artifact_tamper_rejected(tmp_path, mutation):
    artifact = generate_proxy_artifact(output_root=tmp_path)
    path = artifact.path
    if mutation == "record":
        value = json.loads((path / CONTRACT_FILENAME).read_bytes())
        value["result"]["proxy_domains"][0]["is_anatomical_destination"] = True
        _rehash(value)
        (path / CONTRACT_FILENAME).write_bytes(
            canonical_json_bytes(value, newline=True)
        )
    elif mutation == "manifest":
        value = json.loads((path / MANIFEST_FILENAME).read_bytes())
        value["result_sha256"] = "0" * 64
        (path / MANIFEST_FILENAME).write_bytes(
            canonical_json_bytes(value, newline=True)
        )
    elif mutation == "extra_file":
        (path / "extra").write_text("unexpected")
    elif mutation == "noncanonical":
        (path / CONTRACT_FILENAME).write_bytes(
            (path / CONTRACT_FILENAME).read_bytes() + b" "
        )
    else:
        destination = tmp_path / "incorrect"
        path.rename(destination)
        path = destination
    with pytest.raises(ValueError):
        replay_proxy_artifact(path)


def test_cli_generate_inspect_replay_and_error(tmp_path, capsys):
    assert main(["generate", "--output-root", str(tmp_path)]) == 0
    generated = json.loads(capsys.readouterr().out)
    path = generated["artifact_path"]
    assert main(["inspect", path]) == 0
    inspected = json.loads(capsys.readouterr().out)
    assert inspected["proxy_domains"][0]["is_anatomical_destination"] is False
    assert len(inspected["source_mappings"]) == 2
    assert "prohibited_interpretations" in inspected["proxy_domains"][0]
    assert main(["replay", path]) == 0
    assert json.loads(capsys.readouterr().out)["artifact_id"] == EXPECTED_ID
    assert main(["replay", str(tmp_path / "missing")]) == 2
    assert "proxy contract error" in capsys.readouterr().err
