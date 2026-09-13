"""GET-only HTTP tests for raw MaleCNS morphology inspection."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from neurofly.http_api import HTTP_ERROR_SCHEMA_VERSION, create_app
from neurofly.malecns.morphology_artifacts import export_morphology_artifact
from tests.test_morphology_artifacts import synthetic_morphology_bodies


def _client(tmp_path: Path) -> tuple[TestClient, Path]:
    experiment_root = tmp_path / "experiments"
    morphology_root = tmp_path / "morphology"
    experiment_root.mkdir()
    morphology_root.mkdir()
    artifact = export_morphology_artifact(
        synthetic_morphology_bodies(), morphology_root
    )
    return TestClient(create_app(experiment_root, morphology_root)), artifact


def test_list_metadata_and_body_are_read_only(tmp_path: Path) -> None:
    client, artifact = _client(tmp_path)

    listing = client.get("/api/v1/morphology")
    assert listing.status_code == 200
    assert listing.json()["count"] == 1
    assert listing.json()["artifacts"][0]["artifact_id"] == artifact.name
    summary = client.get(f"/api/v1/morphology/{artifact.name}")
    assert summary.status_code == 200
    assert summary.json()["body_ids"] == [10001, 10010]
    body = client.get(f"/api/v1/morphology/{artifact.name}/bodies/10001")
    assert body.status_code == 200
    assert body.json()["components"][0]["links"][0]["provenance"] == (
        "MALECNS_RAW_SKELETON_LINK"
    )
    assert client.post("/api/v1/morphology").status_code == 405
    assert client.put(f"/api/v1/morphology/{artifact.name}").status_code == 405


def test_missing_invalid_and_unconfigured_errors_do_not_leak_paths(
    tmp_path: Path,
) -> None:
    client, artifact = _client(tmp_path)
    missing = client.get(f"/api/v1/morphology/{'f' * 64}")
    assert missing.status_code == 404
    assert missing.json()["schema"] == HTTP_ERROR_SCHEMA_VERSION
    invalid = client.get("/api/v1/morphology/not-a-hash")
    assert invalid.status_code == 400
    body = client.get(f"/api/v1/morphology/{artifact.name}/bodies/99999")
    assert body.status_code == 404
    for response in (missing, invalid, body):
        assert str(tmp_path) not in response.text

    experiment_root = tmp_path / "other-experiments"
    experiment_root.mkdir()
    unavailable = TestClient(create_app(experiment_root)).get("/api/v1/morphology")
    assert unavailable.status_code == 503
    assert unavailable.json()["code"] == "morphology_store_unavailable"


def test_corruption_and_unsupported_schema_are_explicit(tmp_path: Path) -> None:
    client, artifact = _client(tmp_path)
    payload = artifact / "bodies/10001.json"
    payload.write_text("{}", encoding="utf-8")
    corrupt = client.get("/api/v1/morphology")
    assert corrupt.status_code == 409
    assert corrupt.json()["code"] == "morphology_integrity_failure"
    assert str(tmp_path) not in corrupt.text

    other_root = tmp_path / "unsupported"
    other_root.mkdir()
    bad = other_root / ("e" * 64)
    bad.mkdir()
    (bad / "manifest.json").write_text(
        json.dumps({"artifact_schema_version": "malecns_morphology_artifact_v2"}),
        encoding="utf-8",
    )
    experiment_root = tmp_path / "unused-experiments"
    experiment_root.mkdir()
    unsupported = TestClient(create_app(experiment_root, other_root)).get(
        "/api/v1/morphology"
    )
    assert unsupported.status_code == 409
    assert unsupported.json()["code"] == "unsupported_morphology_schema"


def test_gets_never_acquire_live_morphology(tmp_path: Path, monkeypatch) -> None:
    client, artifact = _client(tmp_path)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("HTTP reads must never call neuPrint acquisition")

    monkeypatch.setattr(
        "neurofly.malecns.morphology_artifacts.acquire_dnp01_morphology",
        forbidden,
    )
    assert client.get(f"/api/v1/morphology/{artifact.name}").status_code == 200
