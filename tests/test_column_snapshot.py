"""Offline persistence and integrity tests for the Phase 1E data product."""

from dataclasses import replace

import pytest
from test_columns import _circuit, _neuron, _rois, _rows

from neurofly.malecns.column_snapshot import (
    export_column_contract,
    load_column_contract,
)
from neurofly.malecns.columns import build_column_contract
from neurofly.malecns.errors import SnapshotIntegrityError


def _contract():
    return build_column_contract(
        _rows(), _circuit(_neuron(1)), _rois(), expected_population=False
    )


def test_column_export_is_deterministic_and_loads_offline(tmp_path) -> None:
    contract = _contract()
    first = export_column_contract(contract, tmp_path / "first")
    second = export_column_contract(
        replace(
            contract,
            records=tuple(reversed(contract.records)),
            summaries=tuple(reversed(contract.summaries)),
        ),
        tmp_path / "second",
    )
    for filename in (
        "column_inputs.jsonl",
        "column_body_summaries.jsonl",
        "column_manifest.json",
    ):
        assert (first / filename).read_bytes() == (second / filename).read_bytes()
    loaded = load_column_contract(first)
    assert loaded.records == contract.records
    assert loaded.summaries == contract.summaries


def test_checksum_corruption_is_rejected(tmp_path) -> None:
    output = export_column_contract(_contract(), tmp_path / "snapshot")
    path = output / "column_inputs.jsonl"
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError, match="SHA-256 mismatch"):
        load_column_contract(output)


def test_serialized_data_contains_no_credentials(tmp_path) -> None:
    output = export_column_contract(_contract(), tmp_path / "snapshot")
    serialized = "".join(
        path.read_text(encoding="utf-8")
        for path in sorted(output.iterdir())
        if path.is_file()
    )
    assert "NEUPRINT_APPLICATION_CREDENTIALS" not in serialized
    assert "token" not in serialized.lower()


def test_manifest_records_hashes_and_query_metadata(tmp_path) -> None:
    contract = replace(
        _contract(),
        query_counts=(
            ("identity_records", 1),
            ("full_aggregate_rows", 2),
        ),
        provenance=(("malecns_direct", "direct"),),
    )
    output = export_column_contract(contract, tmp_path / "snapshot")
    manifest = (output / "column_manifest.json").read_text(encoding="utf-8")
    assert "sha256" in manifest
    assert "identity_records" in manifest
    assert "malecns_direct" in manifest
