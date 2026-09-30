"""Immutable offline artifacts for model-space observation extraction."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.g1_proxy_peak_deflection import (
    ARTIFACT_SCHEMA,
    build_observations,
    validate_observations,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA
RESULT_FILENAME = "observations.json"


def _manifest(response: dict) -> dict:
    raw = canonical_json_bytes(response, newline=True)
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA,
        "artifact_id": response["artifact_id"],
        "config_sha256": response["config_sha256"],
        "result_sha256": response["result_sha256"],
        "files": {
            RESULT_FILENAME: {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}
        },
    }


def replay_observation_artifact(
    path: str | Path, *, allow_staging=False, **sources
) -> dict:
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("unexpected observation artifact file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical observation artifact JSON")
        payloads.append(payload)
    response, manifest = payloads
    validate_observations(response, **sources)
    if manifest != _manifest(response) or (
        not allow_staging and path.name != response["artifact_id"]
    ):
        raise ValueError("observation artifact/hash/directory mismatch")
    return response


def generate_observation_artifact(
    *, output_root=DEFAULT_ARTIFACT_ROOT, **sources
) -> Path:
    response = build_observations(**sources)
    root = Path(output_root)
    destination = root / response["artifact_id"]
    if destination.exists():
        replay_observation_artifact(destination, **sources)
        return destination
    root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{response['artifact_id']}.", dir=root))
    try:
        for name, payload in (
            (RESULT_FILENAME, response),
            ("manifest.json", _manifest(response)),
        ):
            with (staging / name).open("xb") as stream:
                stream.write(canonical_json_bytes(payload, newline=True))
                stream.flush()
                os.fsync(stream.fileno())
        replay_observation_artifact(staging, allow_staging=True, **sources)
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def artifact_summary(path: Path, response: dict) -> dict:
    return {
        "artifact_schema": ARTIFACT_SCHEMA,
        "artifact_id": response["artifact_id"],
        "config_sha256": response["config_sha256"],
        "result_sha256": response["result_sha256"],
        "artifact_bytes": sum(p.stat().st_size for p in path.iterdir()),
        "operation": "MODEL_SPACE_EXTRACTION_NOT_EMPIRICAL_VALIDATION",
        "config": response["config"],
        "result": response["result"],
    }
