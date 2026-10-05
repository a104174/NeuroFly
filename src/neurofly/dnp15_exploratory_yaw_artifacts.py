"""Immutable content-addressed orientation artifacts and offline replay."""

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.dnp15_exploratory_yaw import (
    ARTIFACT_SCHEMA,
    build_yaw_artifact,
    validate_yaw_artifact,
)
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = Path("data/derived/experiments") / ARTIFACT_SCHEMA
RESULT_FILENAME = "orientation.json"


def _manifest(payload):
    raw = canonical_json_bytes(payload, newline=True)
    return {
        "schema": ARTIFACT_SCHEMA,
        **{k: payload[k] for k in ("artifact_id", "config_sha256", "result_sha256")},
        "files": {
            RESULT_FILENAME: {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}
        },
    }


def _load(path, *, allow_staging=False):
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("unexpected orientation artifact file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical orientation artifact JSON")
        payloads.append(payload)
    response, manifest = payloads
    if manifest != _manifest(response) or (
        not allow_staging and path.name != response["artifact_id"]
    ):
        raise ValueError("orientation manifest/hash/directory mismatch")
    return response


def replay_yaw_artifact(path):
    response = _load(path)
    validate_yaw_artifact(response)
    return response


def generate_yaw_artifact(*, output_root=DEFAULT_ARTIFACT_ROOT):
    # The first execution of all conditions occurs here after both freezes.
    # Staging verifies serialization only, not a second numerical execution.
    response = build_yaw_artifact()
    root = Path(output_root)
    destination = root / response["artifact_id"]
    if destination.exists():
        replay_yaw_artifact(destination)
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
        _load(staging, allow_staging=True)
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def artifact_summary(path, payload):
    return {
        "operation": (
            "EXPLORATORY MODEL-SPACE ORIENTATION — NO PHYSICAL YAW OR FEEDBACK"
        ),
        "schema": ARTIFACT_SCHEMA,
        **{k: payload[k] for k in ("artifact_id", "config_sha256", "result_sha256")},
        "evidence_gate_id": payload["config"]["evidence_gate_id"],
        "preregistration_id": payload["config"]["preregistration_id"],
        "artifact_bytes": sum(p.stat().st_size for p in Path(path).iterdir()),
        "conditions": [
            {"id": r["condition_id"], **r["summary"]} for r in payload["result"]["runs"]
        ],
    }
