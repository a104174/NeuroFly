"""Offline tests for deterministic, credential-free snapshot export."""

import json
from dataclasses import replace

import pytest

from neurofly.malecns.errors import MaleCNSValidationError, SnapshotExportError
from neurofly.malecns.snapshot import build_manifest, export_snapshot
from neurofly.malecns.validation import validate_snapshot


def test_manifest_contains_provenance_but_no_credential(valid_snapshot) -> None:
    report = validate_snapshot(valid_snapshot)
    manifest = build_manifest(valid_snapshot, report)
    serialized = json.dumps(manifest)
    assert manifest["dataset"] == "male-cns:v1.0"
    assert manifest["neuron_count"] == 313
    assert manifest["induced_connection_count"] == 312
    assert manifest["structural_weight_source"] == "neuPrint ConnectsTo.weight"
    assert "NEUPRINT_APPLICATION_CREDENTIALS" not in serialized
    assert "token" not in serialized.lower()


def test_export_is_deterministic_and_preserves_reverse_edges(
    tmp_path, valid_snapshot
) -> None:
    first = export_snapshot(valid_snapshot, tmp_path / "first")
    reversed_snapshot = replace(
        valid_snapshot,
        neurons=tuple(reversed(valid_snapshot.neurons)),
        connections=tuple(reversed(valid_snapshot.connections)),
    )
    second = export_snapshot(reversed_snapshot, tmp_path / "second")

    for filename in ("neurons.jsonl", "connections.jsonl", "manifest.json"):
        assert (first / filename).read_bytes() == (second / filename).read_bytes()
    connections = (first / "connections.jsonl").read_text(encoding="utf-8")
    assert '"source_type":"DNp01"' in connections
    assert '"target_type":"LC4"' in connections


def test_existing_snapshot_is_not_replaced(tmp_path, valid_snapshot) -> None:
    output = export_snapshot(valid_snapshot, tmp_path / "snapshot")
    with pytest.raises(SnapshotExportError, match="already exists"):
        export_snapshot(valid_snapshot, output)


def test_failed_validation_leaves_no_snapshot(tmp_path, valid_snapshot) -> None:
    invalid = replace(valid_snapshot, connections=())
    output = tmp_path / "invalid"
    with pytest.raises(MaleCNSValidationError):
        export_snapshot(invalid, output)
    assert not output.exists()
    assert list(tmp_path.iterdir()) == []
