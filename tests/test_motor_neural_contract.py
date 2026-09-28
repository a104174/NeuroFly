from __future__ import annotations

import json
from pathlib import Path

import pytest

from neurofly.motor_neural_contract import (
    HISTORICAL_ANNOTATION_SHA256,
    QUERY_GROUPS,
    MotorNeuralContractError,
    build_motor_neural_contract,
    build_source_response,
    canonical_json_bytes,
    canonical_sha256,
    historical_differences,
    load_pinned_artifact,
    source_manifest,
    write_pinned_artifact,
)
from neurofly.motor_pathway import MOTOR_PATHWAY_EVIDENCE
from neurofly.sensory_dnp01_motor_adapter import _route_records

IDENTITIES = (
    {
        "body_id": 10001,
        "type": "DNp01",
        "instance": "DNp01(GF)_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Roughly traced",
        "superclass": "descending_neuron",
        "subclass": "lt",
        "soma_neuromere": None,
    },
    {
        "body_id": 10010,
        "type": "DNp01",
        "instance": "DNp01(GF)_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Roughly traced",
        "superclass": "descending_neuron",
        "subclass": "lt",
        "soma_neuromere": None,
    },
    {
        "body_id": 800146,
        "type": "TTMn",
        "instance": "TTMn_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T2",
    },
    {
        "body_id": 804642,
        "type": "TTMn",
        "instance": "TTMn_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T2",
    },
    {
        "body_id": 802401,
        "type": "PSI",
        "instance": "PSI_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_efferent",
        "subclass": None,
        "soma_neuromere": "T2",
    },
    {
        "body_id": 903327,
        "type": "PSI",
        "instance": "PSI_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_efferent",
        "subclass": None,
        "soma_neuromere": "T2",
    },
    {
        "body_id": 800718,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 800890,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 801295,
        "type": "DLMn a, b",
        "instance": "DLMn a, b_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T2",
    },
    {
        "body_id": 801895,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 801970,
        "type": "DLMn a, b",
        "instance": "DLMn a, b_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T2",
    },
    {
        "body_id": 801998,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 802544,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 803013,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_L",
        "side": "L",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 803048,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
    {
        "body_id": 1050014552,
        "type": "DLMn c-f",
        "instance": "DLMn c-f_R",
        "side": "R",
        "status": "Traced",
        "status_label": "Reviewed",
        "superclass": "vnc_motor",
        "subclass": "wm",
        "soma_neuromere": "T1",
    },
)
EDGE_ROWS = {
    "dnp01_to_ttmn": [
        (10001, 800146, 70),
        (10010, 804642, 20),
    ],
    "dnp01_to_psi": [
        (10001, 802401, 3),
        (10001, 903327, 2),
        (10010, 802401, 9),
        (10010, 903327, 2),
    ],
    "psi_to_dlmn": [
        (802401, 801970, 17),
        (802401, 801998, 40),
        (802401, 802544, 67),
        (802401, 803048, 35),
        (802401, 1050014552, 64),
        (903327, 800718, 68),
        (903327, 800890, 24),
        (903327, 801295, 26),
        (903327, 801895, 58),
        (903327, 803013, 50),
    ],
    "dnp01_to_candidate_dlmn": [],
    "psi_to_psi_supplemental": [
        (802401, 903327, 5),
        (903327, 802401, 17),
    ],
}


def source_response():
    rows = {
        query_id: [
            {
                "source_body_id": pre,
                "target_body_id": post,
                "roi": "VNC",
                "structural_count": count,
            }
            for pre, post, count in group_rows
        ]
        for query_id, group_rows in EDGE_ROWS.items()
    }
    return build_source_response(IDENTITIES, rows, HISTORICAL_ANNOTATION_SHA256)


def test_query_response_canonicalizes_order_and_hash():
    response = source_response()
    reversed_rows = {key: list(reversed(value)) for key, value in EDGE_ROWS.items()}
    rows = {
        query_id: [
            {
                "source_body_id": pre,
                "target_body_id": post,
                "roi": "VNC",
                "structural_count": count,
            }
            for pre, post, count in group_rows
        ]
        for query_id, group_rows in reversed_rows.items()
    }
    replay = build_source_response(
        list(reversed(IDENTITIES)), rows, HISTORICAL_ANNOTATION_SHA256
    )
    assert response == replay
    assert canonical_json_bytes(response) == canonical_json_bytes(replay)
    assert canonical_sha256(response) == canonical_sha256(replay)
    assert historical_differences(response) == []


def test_query_response_rejects_duplicate_nodes_or_edges():
    with pytest.raises(MotorNeuralContractError, match="duplicate/invalid IDs"):
        build_source_response(
            (*IDENTITIES, IDENTITIES[0]),
            {group["query_id"]: [] for group in QUERY_GROUPS},
            HISTORICAL_ANNOTATION_SHA256,
        )

    duplicate = source_response()
    rows = {
        group["query_id"]: list(group["rows"]) for group in duplicate["query_groups"]
    }
    rows["dnp01_to_ttmn"].append(rows["dnp01_to_ttmn"][0])
    with pytest.raises(MotorNeuralContractError, match="duplicate edge"):
        build_source_response(IDENTITIES, rows, HISTORICAL_ANNOTATION_SHA256)


def test_exact_identities_and_historical_route_groups_are_validated():
    response = source_response()
    assert len(response["nodes"]) == 16
    assert {node["type"] for node in response["nodes"]} == {
        "DNp01",
        "TTMn",
        "PSI",
        "DLMn a, b",
        "DLMn c-f",
    }
    assert [len(group["rows"]) for group in response["query_groups"]] == [
        2,
        4,
        10,
        0,
        2,
    ]
    bad = json.loads(canonical_json_bytes(response))
    bad["query_groups"][0]["rows"][0]["structural_count"] = 71
    differences = historical_differences(bad)
    assert any(
        row["kind"] == "edges" and row["query_id"] == "dnp01_to_ttmn"
        for row in differences
    )


def test_contract_is_content_addressed_no_dynamics_and_compatible_with_6c_8c():
    contract = build_motor_neural_contract(source_response())
    assert (
        contract["contract_id"]
        == build_motor_neural_contract(source_response())["contract_id"]
    )
    assert contract["scope"]["no_dynamics"] is True
    assert len(contract["nodes"]) == 16
    assert len(contract["chemical_edges"]) == 18
    assert contract["direct_dnp01_to_candidate_dlmn_audit"]["returned_edge_count"] == 0

    forbidden = {"tau", "gain", "conductance", "threshold", "delay", "voltage"}

    def keys(value):
        if isinstance(value, dict):
            for key, child in value.items():
                yield key.lower()
                yield from keys(child)
        elif isinstance(value, list):
            for child in value:
                yield from keys(child)

    assert forbidden.isdisjoint(set(keys(contract)))

    contract_routes = {
        (row["source_body_id"], row["target_body_id"], row["structural_count"])
        for row in contract["chemical_edges"]
    }
    phase6c_routes = {
        (row["pre_body_id"], row["post_body_id"], row["structural_weight"])
        for row in MOTOR_PATHWAY_EVIDENCE.chemical_edges
    }
    phase8c_routes = {
        (row["source_body_id"], row["target_body_id"], row["structural_weight"])
        for row in _route_records()
    }
    assert phase6c_routes == phase8c_routes
    assert phase6c_routes <= contract_routes


def test_immutable_artifact_offline_replay_and_tamper_rejection(tmp_path: Path):
    response = source_response()
    manifest = source_manifest(
        response,
        retrieved_at_utc="2026-09-28T12:00:00+00:00",
        neuprint_python_version="0.6.3",
        python_version="3.12.3",
    )
    output_root = tmp_path / "motor-contracts"
    path = write_pinned_artifact(output_root, response, manifest)
    loaded = load_pinned_artifact(path)
    assert loaded["response"] == response
    assert loaded["contract"]["contract_id"] == path.name
    assert write_pinned_artifact(output_root, response, manifest) == path

    contract_file = path / "contract.json"
    modified = json.loads(contract_file.read_bytes())
    modified["chemical_edges"][0]["structural_count"] += 1
    contract_file.write_bytes(canonical_json_bytes(modified))
    with pytest.raises(MotorNeuralContractError, match="contract content"):
        load_pinned_artifact(path)


def test_source_manifest_rejects_source_or_query_mismatch(tmp_path: Path):
    response = source_response()
    manifest = source_manifest(
        response,
        retrieved_at_utc="2026-09-28T12:00:00+00:00",
        neuprint_python_version="0.6.3",
    )
    manifest["dataset"] = "other-dataset"
    with pytest.raises(MotorNeuralContractError, match="source manifest"):
        write_pinned_artifact(tmp_path / "unused", response, manifest)
