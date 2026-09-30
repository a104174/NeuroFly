"""Immutable offline artifacts for the static activation proxy."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.muscle_activation import (
    ARTIFACT_SCHEMA,
    ActivationConfig,
    build_activation,
    validate_activation,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA
RESULT_FILENAME = "activation.json"


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


def replay_activation_artifact(
    path: str | Path, *, allow_staging=False, **sources
) -> dict:
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("unexpected activation artifact file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical activation artifact JSON")
        payloads.append(payload)
    response, manifest = payloads
    validate_activation(response, **sources)
    if manifest != _manifest(response) or (
        not allow_staging and path.name != response["artifact_id"]
    ):
        raise ValueError("activation artifact/hash/directory mismatch")
    return response


def generate_activation_artifact(
    config: ActivationConfig, *, output_root=DEFAULT_ARTIFACT_ROOT, **sources
) -> Path:
    response = build_activation(config, **sources)
    root = Path(output_root)
    destination = root / response["artifact_id"]
    if destination.exists():
        replay_activation_artifact(destination, **sources)
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
        replay_activation_artifact(staging, allow_staging=True, **sources)
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def artifact_summary(path: Path, response: dict) -> dict:
    return {
        "operation": "EXPLORATORY_UNCALIBRATED_MUSCLE_ACTIVATION_PROXY",
        "artifact_schema": ARTIFACT_SCHEMA,
        "artifact_id": response["artifact_id"],
        "config_sha256": response["config_sha256"],
        "result_sha256": response["result_sha256"],
        "artifact_bytes": sum(p.stat().st_size for p in path.iterdir()),
        "config": response["config"],
        "trajectory_count": response["result"]["trajectory_count"],
        "sample_count": response["result"]["sample_count"],
        "fixtures": [
            {
                "fixture_id": f["fixture_id"],
                "instances": [
                    {
                        "source_body_id": i["source_body_id"],
                        "source_side": i["source_side"],
                        "source_trajectory_id": i["source_trajectory_id"],
                        **i["summary"],
                    }
                    for i in f["instances"]
                ],
            }
            for f in response["result"]["fixtures"]
        ],
    }
