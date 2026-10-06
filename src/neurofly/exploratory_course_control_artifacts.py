"""Immutable closed-loop composition artifacts and offline deterministic replay."""

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.exploratory_course_control import (
    ARTIFACT_SCHEMA,
    build_closed_loop_artifact,
    validate_closed_loop_artifact,
)
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = Path("data/derived/experiments") / ARTIFACT_SCHEMA
RESULT_FILENAME = "closed_loop.json"


def _manifest(response):
    raw = canonical_json_bytes(response, newline=True)
    return {
        "schema": ARTIFACT_SCHEMA,
        **{k: response[k] for k in ("artifact_id", "config_sha256", "result_sha256")},
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
        raise ValueError("unexpected course-control artifact file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical course-control artifact JSON")
        payloads.append(payload)
    response, manifest = payloads
    if manifest != _manifest(response) or (
        not allow_staging and path.name != response["artifact_id"]
    ):
        raise ValueError("course-control manifest/hash/directory mismatch")
    return response


def replay_closed_loop_artifact(path):
    response = _load(path)
    validate_closed_loop_artifact(response)
    return response


def generate_closed_loop_artifact(*, output_root=DEFAULT_ARTIFACT_ROOT):
    # First frozen generation executes each condition once. Serialization-only
    # staging checks do not perform a second closed-loop execution.
    response = build_closed_loop_artifact()
    root = Path(output_root)
    destination = root / response["artifact_id"]
    if destination.exists():
        replay_closed_loop_artifact(destination)
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


def artifact_summary(path, response):
    return {
        "operation": "EXPLORATORY MODEL-SPACE MOTION FEEDBACK; NOT BIOLOGICAL STEERING",
        "schema": ARTIFACT_SCHEMA,
        **{k: response[k] for k in ("artifact_id", "config_sha256", "result_sha256")},
        "preregistration_id": response["config"]["preregistration_id"],
        "analysis_id": response["config"]["analysis_id"],
        "artifact_bytes": sum(p.stat().st_size for p in Path(path).iterdir()),
        "conditions": [
            {
                "id": run["condition"]["id"],
                "termination": run["termination"],
                **run["diagnostics"],
            }
            for run in response["result"]["runs"]
        ],
    }
