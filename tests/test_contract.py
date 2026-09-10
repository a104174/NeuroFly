"""Offline tests for the model-neutral scientific circuit contract."""

import hashlib
import json
import sys

import pytest

import neurofly.malecns.contract as contract_module
from neurofly.malecns.__main__ import main
from neurofly.malecns.contract import (
    EXPERIMENTAL_BOUNDARY,
    TypePairSummary,
    _load_circuit_contract,
    _SnapshotExpectations,
)
from neurofly.malecns.errors import (
    MaleCNSAccessError,
    MaleCNSValidationError,
    SnapshotIntegrityError,
)
from neurofly.malecns.models import PrimaryMetrics


@pytest.fixture
def tiny_expectations() -> _SnapshotExpectations:
    return _SnapshotExpectations(
        neuron_counts=(("DNp01", 2), ("LC4", 2), ("LPLC2", 1)),
        connection_count=6,
        total_structural_weight=12,
        type_pairs=(
            TypePairSummary("DNp01", "LC4", 1, 1),
            TypePairSummary("LC4", "DNp01", 2, 5),
            TypePairSummary("LC4", "LC4", 1, 1),
            TypePairSummary("LPLC2", "DNp01", 1, 4),
            TypePairSummary("LPLC2", "LPLC2", 1, 1),
        ),
        primary=(
            ("LC4", PrimaryMetrics(2, 2, 5)),
            ("LPLC2", PrimaryMetrics(1, 1, 4)),
        ),
    )


def _neuron(body_id: int, neuron_type: str, instance: str | None = None) -> dict:
    return {
        "dataset": "male-cns:v1.0",
        "body_id": body_id,
        "instance": instance,
        "type": neuron_type,
        "status": "Traced",
        "status_label": None,
        "superclass": (
            "descending_neuron" if neuron_type == "DNp01" else "visual_projection"
        ),
        "class": None,
        "soma_side": None,
        "soma_neuromere": None,
        "pre": None,
        "post": None,
        "upstream": None,
        "downstream": None,
        "predicted_nt": "acetylcholine",
        "predicted_nt_confidence": None,
        "consensus_nt": "acetylcholine",
        "dimorphism": None,
    }


def _edge(source: int, target: int, source_type: str, target_type: str, weight: int):
    return {
        "dataset": "male-cns:v1.0",
        "source_body_id": source,
        "target_body_id": target,
        "source_type": source_type,
        "target_type": target_type,
        "structural_weight": weight,
    }


def _tiny_records() -> tuple[list[dict], list[dict]]:
    neurons = [
        _neuron(2, "LC4"),
        _neuron(10010, "DNp01", "DNp01(GF)_L"),
        _neuron(3, "LPLC2"),
        _neuron(10001, "DNp01", "DNp01(GF)_R"),
        _neuron(1, "LC4"),
    ]
    connections = [
        _edge(3, 3, "LPLC2", "LPLC2", 1),
        _edge(1, 1, "LC4", "LC4", 1),
        _edge(10001, 1, "DNp01", "LC4", 1),
        _edge(3, 10010, "LPLC2", "DNp01", 4),
        _edge(2, 10010, "LC4", "DNp01", 3),
        _edge(1, 10001, "LC4", "DNp01", 2),
    ]
    return neurons, connections


def _write_jsonl(path, records) -> str:
    content = "".join(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    ).encode()
    path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def _write_snapshot(path, neurons=None, connections=None):
    path.mkdir()
    default_neurons, default_connections = _tiny_records()
    neurons = default_neurons if neurons is None else neurons
    connections = default_connections if connections is None else connections
    hashes = {
        "neurons.jsonl": _write_jsonl(path / "neurons.jsonl", neurons),
        "connections.jsonl": _write_jsonl(path / "connections.jsonl", connections),
    }
    manifest = {
        "candidate": {
            "identifier": "looming_giant_fiber_v1",
            "version": 1,
            "selected_neuron_types": ["LC4", "LPLC2", "DNp01"],
        },
        "source": "Janelia neuPrint / MaleCNS",
        "endpoint": "https://neuprint.janelia.org",
        "dataset": "male-cns:v1.0",
        "acquired_at_utc": "2026-09-10T00:00:00+00:00",
        "neuprint_python_version": "0.6.3",
        "neuron_count": len(neurons),
        "induced_connection_count": len(connections),
        "structural_weight_source": "neuPrint ConnectsTo.weight",
        "structural_weight_is_physiological_coupling": False,
        "sha256": hashes,
    }
    (path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return path


def _rewrite_manifest(path, update) -> None:
    manifest_path = path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    update(manifest)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def _rewrite_records(path, filename, update) -> None:
    file_path = path / filename
    records = [json.loads(line) for line in file_path.read_text().splitlines()]
    update(records)
    digest = _write_jsonl(file_path, records)
    _rewrite_manifest(
        path, lambda manifest: manifest["sha256"].update({filename: digest})
    )


def _load(path, expectations):
    return _load_circuit_contract(path, expectations)


def test_valid_snapshot_load_builds_model_neutral_contract(
    tmp_path, tiny_expectations
) -> None:
    loaded = _load(_write_snapshot(tmp_path / "snapshot"), tiny_expectations)

    assert loaded.integrity.sha256_verified
    assert loaded.integrity.record_counts_verified
    assert loaded.boundary == EXPERIMENTAL_BOUNDARY
    assert loaded.boundary.provenance == "NeuroFly experimental design decision"
    assert loaded.provenance.dataset == "male-cns:v1.0"
    assert loaded.neurons[0].body_id == 1
    assert loaded.neurons[0].status_label is None
    assert loaded.neurons[0].predicted_nt_confidence is None


def test_body_id_index_and_inverse_are_deterministic(
    tmp_path, tiny_expectations
) -> None:
    first = _load(_write_snapshot(tmp_path / "first"), tiny_expectations)
    neurons, connections = _tiny_records()
    second = _load(
        _write_snapshot(
            tmp_path / "second",
            list(reversed(neurons)),
            list(reversed(connections)),
        ),
        tiny_expectations,
    )

    assert first.body_id_by_node_index == (1, 2, 3, 10001, 10010)
    assert dict(first.node_index_by_body_id) == dict(second.node_index_by_body_id)
    assert first.node_index_by_body_id[10010] == 4
    assert first.body_id_by_node_index[first.node_index_by_body_id[3]] == 3
    assert first.neurons_by_body_id[10001].instance == "DNp01(GF)_R"


def test_checksum_mismatch_is_rejected(tmp_path, tiny_expectations) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    with (path / "neurons.jsonl").open("a") as stream:
        stream.write("{}\n")
    with pytest.raises(SnapshotIntegrityError, match="SHA-256 mismatch"):
        _load(path, tiny_expectations)


def test_malformed_manifest_is_rejected(tmp_path, tiny_expectations) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    (path / "manifest.json").write_text("{", encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError, match="Malformed manifest"):
        _load(path, tiny_expectations)


@pytest.mark.parametrize("filename", ["neurons.jsonl", "connections.jsonl"])
def test_malformed_jsonl_is_rejected(tmp_path, tiny_expectations, filename) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    (path / filename).write_text("{\n", encoding="utf-8")
    digest = hashlib.sha256((path / filename).read_bytes()).hexdigest()
    _rewrite_manifest(
        path, lambda manifest: manifest["sha256"].update({filename: digest})
    )
    with pytest.raises(SnapshotIntegrityError, match=f"Malformed {filename}"):
        _load(path, tiny_expectations)


@pytest.mark.parametrize(
    "filename", ["manifest.json", "neurons.jsonl", "connections.jsonl"]
)
def test_missing_required_file_is_rejected(
    tmp_path, tiny_expectations, filename
) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    (path / filename).unlink()
    with pytest.raises(SnapshotIntegrityError, match="missing required files"):
        _load(path, tiny_expectations)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("identifier", "unknown", "Unsupported candidate"),
        ("version", 2, "Unsupported candidate"),
    ],
)
def test_wrong_candidate_is_rejected(
    tmp_path, tiny_expectations, field, value, message
) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    _rewrite_manifest(
        path, lambda manifest: manifest["candidate"].update({field: value})
    )
    with pytest.raises(SnapshotIntegrityError, match=message):
        _load(path, tiny_expectations)


def test_wrong_dataset_is_rejected(tmp_path, tiny_expectations) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    _rewrite_manifest(path, lambda manifest: manifest.update({"dataset": "wrong"}))
    with pytest.raises(SnapshotIntegrityError, match="Wrong dataset"):
        _load(path, tiny_expectations)


def test_duplicate_neuron_is_rejected(tmp_path, tiny_expectations) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    _rewrite_records(
        path,
        "neurons.jsonl",
        lambda records: records[1].update({"body_id": records[0]["body_id"]}),
    )
    with pytest.raises(MaleCNSValidationError, match="Duplicate neuron"):
        _load(path, tiny_expectations)


def test_missing_connection_endpoint_is_rejected(tmp_path, tiny_expectations) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    _rewrite_records(
        path,
        "connections.jsonl",
        lambda records: records[0].update({"target_body_id": 999}),
    )
    with pytest.raises(MaleCNSValidationError, match="outside the selected"):
        _load(path, tiny_expectations)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("source_type", "LC4", "Source type mismatch"),
        ("target_type", "DNp01", "Target type mismatch"),
    ],
)
def test_connection_endpoint_type_mismatch_is_rejected(
    tmp_path, tiny_expectations, field, value, message
) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    _rewrite_records(
        path,
        "connections.jsonl",
        lambda records: records[0].update({field: value}),
    )
    with pytest.raises(MaleCNSValidationError, match=message):
        _load(path, tiny_expectations)


@pytest.mark.parametrize("weight", [0, -1, 1.5, True])
def test_invalid_structural_weight_is_rejected(
    tmp_path, tiny_expectations, weight
) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    _rewrite_records(
        path,
        "connections.jsonl",
        lambda records: records[0].update({"structural_weight": weight}),
    )
    with pytest.raises(SnapshotIntegrityError, match="structural_weight"):
        _load(path, tiny_expectations)


def test_same_type_reverse_and_self_edges_are_preserved(
    tmp_path, tiny_expectations
) -> None:
    loaded = _load(_write_snapshot(tmp_path / "snapshot"), tiny_expectations)
    edges = {(edge.source_body_id, edge.target_body_id) for edge in loaded.connections}
    assert (1, 1) in edges
    assert (3, 3) in edges
    assert (10001, 1) in edges


def test_type_pair_summary_is_deterministic(tmp_path, tiny_expectations) -> None:
    loaded = _load(_write_snapshot(tmp_path / "snapshot"), tiny_expectations)
    summary = loaded.structural_summary()
    assert summary.type_pairs == tiny_expectations.type_pairs
    assert summary.total_chemical_edge_count == 6
    assert summary.total_structural_weight == 12


@pytest.mark.parametrize(
    ("edge_index", "message"),
    [(4, "LC4 -> DNp01"), (3, "LPLC2 -> DNp01")],
)
def test_primary_metric_mismatch_is_rejected(
    tmp_path, tiny_expectations, edge_index, message
) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    _rewrite_records(
        path,
        "connections.jsonl",
        lambda records: records[edge_index].update(
            {"structural_weight": records[edge_index]["structural_weight"] + 1}
        ),
    )
    with pytest.raises(MaleCNSValidationError, match=message):
        _load(path, tiny_expectations)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("neuron_count", 6, "Manifest neuron count mismatch"),
        ("induced_connection_count", 7, "Manifest connection count mismatch"),
    ],
)
def test_manifest_record_count_mismatch_is_rejected(
    tmp_path, tiny_expectations, field, value, message
) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    _rewrite_manifest(path, lambda manifest: manifest.update({field: value}))
    with pytest.raises(SnapshotIntegrityError, match=message):
        _load(path, tiny_expectations)


def test_duplicate_body_level_connection_is_rejected(
    tmp_path, tiny_expectations
) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    _rewrite_records(
        path,
        "connections.jsonl",
        lambda records: records[1].update(
            {
                "source_body_id": records[0]["source_body_id"],
                "target_body_id": records[0]["target_body_id"],
                "source_type": records[0]["source_type"],
                "target_type": records[0]["target_type"],
            }
        ),
    )
    with pytest.raises(MaleCNSValidationError, match="Duplicate body-level"):
        _load(path, tiny_expectations)


def test_cli_inspection_is_offline(
    tmp_path, tiny_expectations, monkeypatch, capsys
) -> None:
    path = _write_snapshot(tmp_path / "snapshot")
    monkeypatch.setattr(contract_module, "CURRENT_EXPECTATIONS", tiny_expectations)
    monkeypatch.setattr(
        "neurofly.malecns.__main__.create_client",
        lambda: (_ for _ in ()).throw(MaleCNSAccessError("network called")),
    )
    monkeypatch.delenv("NEUPRINT_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.setattr(
        sys, "argv", ["neurofly.malecns", "inspect-snapshot", str(path)]
    )

    assert main() == 0
    output = capsys.readouterr().out
    assert "integrity=SHA-256 verified" in output
    assert "chemical_edges=6 total_structural_weight=12" in output


def test_cli_inspection_failure_returns_nonzero(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["neurofly.malecns", "inspect-snapshot", str(tmp_path / "missing")],
    )
    assert main() == 1
    assert "Snapshot directory does not exist" in capsys.readouterr().out
