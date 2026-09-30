"""Immutable, offline-replayed Phase 9B trajectory artifacts."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.g1_proxy_passive_electrical import (
    ARTIFACT_SCHEMA,
    PassiveConfig,
    build_response,
    reference_config,
    validate_response,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA
RESULT_FILENAME = "response.json"


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


def replay_response_artifact(
    path: str | Path, *, allow_staging: bool = False, **sources
) -> dict:
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("unexpected response artifact file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical response artifact JSON")
        payloads.append(payload)
    response, manifest = payloads
    validate_response(response, **sources)
    if manifest != _manifest(response) or (
        not allow_staging and path.name != response["artifact_id"]
    ):
        raise ValueError("artifact/file hash or directory identity mismatch")
    return response


def generate_response_artifact(
    config: PassiveConfig,
    *,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
    **sources,
) -> Path:
    response = build_response(config, **sources)
    root = Path(output_root)
    destination = root / response["artifact_id"]
    if destination.exists():
        replay_response_artifact(destination, **sources)
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
        replay_response_artifact(staging, allow_staging=True, **sources)
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    replay_response_artifact(destination, **sources)
    return destination


def artifact_summary(path: Path, response: dict) -> dict:
    return {
        "artifact_schema": ARTIFACT_SCHEMA,
        "artifact_id": response["artifact_id"],
        "config_sha256": response["config_sha256"],
        "result_sha256": response["result_sha256"],
        "artifact_bytes": sum(p.stat().st_size for p in path.iterdir()),
        "model": response["config"]["model"],
        "sources": response["config"]["sources"],
        "scientific_boundary": response["config"]["scientific_boundary"],
        "source_token_count": response["result"]["source_token_count"],
        "fixtures": [
            {
                "fixture_id": f["fixture_id"],
                "instances": [
                    {
                        "source_body_id": i["source_body_id"],
                        "source_side": i["source_side"],
                        "token_boundaries": [
                            n for n, count in enumerate(i["token_count"]) if count
                        ],
                        **i["summary"],
                    }
                    for i in f["instances"]
                ],
            }
            for f in response["result"]["fixtures"]
        ],
        "reference_config": response["config"]["model"] == reference_config().payload(),
        "operation": "OFFLINE_REPLAY_PASSED_NOT_BIOLOGICAL_VALIDATION",
    }
