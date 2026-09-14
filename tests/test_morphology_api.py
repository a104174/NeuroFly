"""Tests for the strict read-only morphology application store."""

from __future__ import annotations

from pathlib import Path

import pytest

from neurofly.malecns.morphology_artifacts import export_morphology_artifact
from neurofly.morphology_api import (
    CorruptedMorphologyArtifactError,
    InvalidMorphologyArtifactIdError,
    MorphologyArtifactStore,
    MorphologyBodyNotFoundError,
    MorphologyPathError,
)
from tests.test_morphology_artifacts import (
    synthetic_morphology_bodies,
    synthetic_phase5g_morphology_bodies,
)


def test_store_lists_and_loads_json_safe_source_data(tmp_path: Path) -> None:
    path = export_morphology_artifact(synthetic_morphology_bodies(), tmp_path)
    store = MorphologyArtifactStore(tmp_path)

    summaries = store.list_artifacts()
    assert len(summaries) == 1
    payload = summaries[0].to_dict()
    assert payload["artifact_id"] == path.name
    assert payload["body_ids"] == [10001, 10010]
    assert payload["morphology_mode"] == "RAW"
    body = store.get_body(path.name, 10010).to_dict()
    assert body["node_index"] == 1
    assert body["source_side"] == "L"
    assert body["coordinate_unit"] == "8_nm_voxel"
    assert body["components"][0]["nodes"][0]["x"] == 101.25


def test_store_rejects_invalid_identity_missing_body_and_symlink(
    tmp_path: Path,
) -> None:
    path = export_morphology_artifact(synthetic_morphology_bodies(), tmp_path)
    store = MorphologyArtifactStore(tmp_path)
    with pytest.raises(InvalidMorphologyArtifactIdError):
        store.get_artifact("../outside")
    with pytest.raises(MorphologyBodyNotFoundError):
        store.get_body(path.name, 99999)

    external = tmp_path.parent / "outside-morphology"
    external.mkdir(exist_ok=True)
    (tmp_path / ("f" * 64)).symlink_to(external, target_is_directory=True)
    with pytest.raises(MorphologyPathError):
        store.list_artifacts()


def test_store_preserves_integrity_failure(tmp_path: Path) -> None:
    path = export_morphology_artifact(synthetic_morphology_bodies(), tmp_path)
    (path / "bodies/10010.json").write_text("{}", encoding="utf-8")
    with pytest.raises(CorruptedMorphologyArtifactError):
        MorphologyArtifactStore(tmp_path).list_artifacts()


def test_store_serves_all_six_bodies_and_fragmented_metadata(tmp_path: Path) -> None:
    path = export_morphology_artifact(synthetic_phase5g_morphology_bodies(), tmp_path)
    store = MorphologyArtifactStore(tmp_path)
    summary = store.get_artifact(path.name).to_dict()
    assert summary["body_ids"] == [10001, 10010, 11498, 12032, 14465, 16128]
    assert [body["neuron_type"] for body in summary["bodies"]] == [
        "DNp01",
        "DNp01",
        "LPLC2",
        "LC4",
        "LPLC2",
        "LC4",
    ]
    assert store.get_body(path.name, 11498).to_dict()["component_count"] == 2
