"""Immutable offline artifacts for the functional actuator commands."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_actuator import (
    ARTIFACT_SCHEMA,
    build_commands,
    validate_commands,
)
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA
RESULT_FILENAME = "commands.json"


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


def replay_command_artifact(
    path: str | Path, *, allow_staging=False, **sources
) -> dict:
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("unexpected actuator artifact file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical actuator artifact JSON")
        payloads.append(payload)
    response, manifest = payloads
    validate_commands(response, **sources)
    if manifest != _manifest(response) or (
        not allow_staging and path.name != response["artifact_id"]
    ):
        raise ValueError("actuator artifact/hash/directory mismatch")
    return response


def generate_command_artifact(*, output_root=DEFAULT_ARTIFACT_ROOT, **sources) -> Path:
    response = build_commands(**sources)
    root = Path(output_root)
    destination = root / response["artifact_id"]
    if destination.exists():
        replay_command_artifact(destination, **sources)
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
        replay_command_artifact(staging, allow_staging=True, **sources)
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def artifact_summary(path: Path, response: dict) -> dict:
    return {
        "operation": (
            "EXPLORATORY FUNCTIONAL ACTUATOR COMMAND / "
            "NO PHYSICAL FORCE / NO JOINT MOTION"
        ),
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
                        "source_activation_trajectory_id": i[
                            "source_activation_trajectory_id"
                        ],
                        "actuator_id": i["actuator_id"],
                        "actuator_side": i["actuator_side"],
                        "action_kind": i["action_kind"],
                        **i["summary"],
                    }
                    for i in f["instances"]
                ],
            }
            for f in response["result"]["fixtures"]
        ],
    }
