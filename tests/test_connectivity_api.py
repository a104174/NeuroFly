"""Bounded structural connectivity is projected from the validated contract."""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from neurofly.connectivity_api import (
    STRUCTURAL_CONNECTIVITY_BODY_IDS,
    STRUCTURAL_CONNECTIVITY_PROJECTION_ID,
    ConnectivityProvenanceError,
    UnsupportedConnectivityProjectionError,
    project_structural_connectivity,
)
from neurofly.http_api import (
    ARTIFACT_ROOT_ENV,
    CIRCUIT_CONTRACT_ROOT_ENV,
    HTTP_ERROR_SCHEMA_VERSION,
    create_app,
    create_app_from_env,
)
from neurofly.malecns.contract import load_circuit_contract

CONTRACT_ROOT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "derived"
    / "malecns"
    / "looming_giant_fiber_v1"
)


@pytest.fixture(scope="module")
def contract():
    return load_circuit_contract(CONTRACT_ROOT)


def _client(tmp_path: Path, contract_root: Path | None = CONTRACT_ROOT) -> TestClient:
    experiment_root = tmp_path / "experiments"
    experiment_root.mkdir(parents=True, exist_ok=True)
    return TestClient(create_app(experiment_root, circuit_contract_root=contract_root))


def test_projection_is_exact_directed_bounded_and_deterministic(contract):
    payload = project_structural_connectivity(contract)
    assert payload == project_structural_connectivity(contract)
    assert payload["fixed_sample"]["body_ids"] == list(STRUCTURAL_CONNECTIVITY_BODY_IDS)
    assert payload["projection"]["canonical_order"] == (
        "pre_node_index, then post_node_index"
    )
    assert [
        (
            edge["pre_body_id"],
            edge["pre_neuron_type"],
            edge["pre_source_side"],
            edge["post_body_id"],
            edge["post_neuron_type"],
            edge["post_source_side"],
            edge["structural_weight"],
        )
        for edge in payload["edges"]
    ] == [
        (11498, "LPLC2", "L", 10010, "DNp01", "L", 2),
        (12032, "LC4", "L", 10010, "DNp01", "L", 62),
        (14465, "LPLC2", "R", 10001, "DNp01", "R", 21),
        (16128, "LC4", "R", 10001, "DNp01", "R", 65),
    ]
    source_edges = {
        (edge.source_body_id, edge.target_body_id): edge
        for edge in contract.connections
    }
    assert all(
        (edge["pre_body_id"], edge["post_body_id"]) in source_edges
        and source_edges[(edge["pre_body_id"], edge["post_body_id"])].structural_weight
        == edge["structural_weight"]
        for edge in payload["edges"]
    )
    assert all(
        edge["pre_body_id"] in STRUCTURAL_CONNECTIVITY_BODY_IDS
        for edge in payload["edges"]
    )
    assert all(
        edge["post_body_id"] in STRUCTURAL_CONNECTIVITY_BODY_IDS
        for edge in payload["edges"]
    )
    assert all(edge["pre_neuron_type"] in {"LC4", "LPLC2"} for edge in payload["edges"])
    assert all(edge["post_neuron_type"] == "DNp01" for edge in payload["edges"])
    assert payload["aggregates"] == {
        "edge_count": 4,
        "total_structural_weight": 150,
        "structural_weight_by_source_type": {"LC4": 127, "LPLC2": 23},
    }
    assert payload["source_contract"]["integrity"]["sha256_verified"] is True
    assert payload["source_contract"]["integrity"]["sha256_by_file"] == [
        {
            "file": "neurons.jsonl",
            "sha256": (
                "00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e"
            ),
        },
        {
            "file": "connections.jsonl",
            "sha256": (
                "f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a"
            ),
        },
    ]


def test_payload_uses_structural_weight_without_activity_or_physiology_fields(contract):
    payload = project_structural_connectivity(contract)
    forbidden = {
        "efficacy",
        "conductance",
        "probability",
        "activity",
        "firing_rate",
        "gain",
        "current",
    }

    def visit(value):
        if isinstance(value, dict):
            assert not (set(value) & forbidden)
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    visit(payload)
    assert all("structural_weight" in edge for edge in payload["edges"])
    assert "k_syn" not in json.dumps(payload)


def test_projection_rejects_wrong_fixed_identity_and_projection(contract):
    altered_neurons = tuple(
        replace(neuron, soma_side="R") if neuron.body_id == 12032 else neuron
        for neuron in contract.neurons
    )
    with pytest.raises(ConnectivityProvenanceError, match="body identity"):
        project_structural_connectivity(replace(contract, neurons=altered_neurons))
    with pytest.raises(UnsupportedConnectivityProjectionError):
        project_structural_connectivity(contract, "other_projection")


def test_projection_requires_the_pinned_contract_hashes_and_provenance(contract):
    altered_hashes = replace(
        contract.integrity,
        sha256_by_file=(
            ("neurons.jsonl", "a" * 64),
            ("connections.jsonl", "b" * 64),
        ),
    )
    with pytest.raises(ConnectivityProvenanceError, match="integrity provenance"):
        project_structural_connectivity(replace(contract, integrity=altered_hashes))

    altered_provenance = replace(
        contract.provenance, acquired_at_utc="2026-09-11T00:00:00+00:00"
    )
    with pytest.raises(ConnectivityProvenanceError, match="provenance mismatch"):
        project_structural_connectivity(
            replace(contract, provenance=altered_provenance)
        )


def test_connectivity_endpoint_is_get_only_and_does_not_use_neuprint(
    tmp_path, monkeypatch
):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("connectivity GET must remain offline")

    monkeypatch.setattr("neurofly.malecns.client.create_client", forbidden)
    client = _client(tmp_path)
    response = client.get(
        f"/api/v1/connectivity/{STRUCTURAL_CONNECTIVITY_PROJECTION_ID}"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["schema"] == "malecns_structural_connectivity_v1"
    assert payload["kind"] == "bounded_structural_connectivity"
    assert len(payload["edges"]) == 4
    assert (
        client.post(
            f"/api/v1/connectivity/{STRUCTURAL_CONNECTIVITY_PROJECTION_ID}"
        ).status_code
        == 405
    )
    assert (
        client.put(
            f"/api/v1/connectivity/{STRUCTURAL_CONNECTIVITY_PROJECTION_ID}"
        ).status_code
        == 405
    )
    assert (
        client.patch(
            f"/api/v1/connectivity/{STRUCTURAL_CONNECTIVITY_PROJECTION_ID}"
        ).status_code
        == 405
    )
    assert (
        client.delete(
            f"/api/v1/connectivity/{STRUCTURAL_CONNECTIVITY_PROJECTION_ID}"
        ).status_code
        == 405
    )


def test_connectivity_errors_are_explicit_sanitized_and_fail_closed(tmp_path):
    unconfigured = _client(tmp_path / "unconfigured", None).get(
        f"/api/v1/connectivity/{STRUCTURAL_CONNECTIVITY_PROJECTION_ID}"
    )
    assert unconfigured.status_code == 503
    assert unconfigured.json()["schema"] == HTTP_ERROR_SCHEMA_VERSION
    assert unconfigured.json()["code"] == "connectivity_source_unavailable"

    missing = _client(tmp_path / "missing", tmp_path / "absent").get(
        f"/api/v1/connectivity/{STRUCTURAL_CONNECTIVITY_PROJECTION_ID}"
    )
    assert missing.status_code == 404
    assert missing.json()["code"] == "circuit_contract_not_found"
    assert str(tmp_path) not in missing.text

    unsupported = _client(tmp_path / "unsupported").get(
        "/api/v1/connectivity/not-a-phase5i-projection"
    )
    assert unsupported.status_code == 404
    assert unsupported.json()["code"] == "unsupported_connectivity_projection"


def test_corrupt_contract_fails_integrity_validation_without_path_leak(tmp_path):
    root = tmp_path / "snapshot"
    shutil.copytree(CONTRACT_ROOT, root)
    with (root / "connections.jsonl").open("a", encoding="utf-8") as stream:
        stream.write("{}\n")
    response = _client(tmp_path / "api", root).get(
        f"/api/v1/connectivity/{STRUCTURAL_CONNECTIVITY_PROJECTION_ID}"
    )
    assert response.status_code == 409
    assert response.json()["code"] == "circuit_contract_invalid"
    assert str(tmp_path) not in response.text


def test_environment_factory_uses_explicit_contract_root(tmp_path, monkeypatch):
    experiment_root = tmp_path / "experiments"
    experiment_root.mkdir()
    monkeypatch.setenv(ARTIFACT_ROOT_ENV, str(experiment_root))
    monkeypatch.setenv(CIRCUIT_CONTRACT_ROOT_ENV, str(CONTRACT_ROOT))
    app = create_app_from_env()
    assert app.state.structural_connectivity_store.root == CONTRACT_ROOT
