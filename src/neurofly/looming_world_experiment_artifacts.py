"""Immutable frozen-design experiment artifacts and offline numerical replay."""

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.looming_world_experiment import (
    ARTIFACT_SCHEMA,
    build_world_experiment,
    validate_world_experiment,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA
RESULT_FILENAME = "experiment.json"


def _manifest(response):
    raw = canonical_json_bytes(response, newline=True)
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA,
        **{k: response[k] for k in ("artifact_id", "config_sha256", "result_sha256")},
        "files": {
            RESULT_FILENAME: {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}
        },
    }


def replay_world_artifact(path, *, allow_staging=False):
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("unexpected world experiment artifact file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical world experiment JSON")
        payloads.append(payload)
    response, manifest = payloads
    validate_world_experiment(response)
    if manifest != _manifest(response) or (
        not allow_staging and path.name != response["artifact_id"]
    ):
        raise ValueError("world experiment manifest/hash/directory mismatch")
    return response


def generate_world_artifact(*, output_root=DEFAULT_ARTIFACT_ROOT):
    response = build_world_experiment()
    root = Path(output_root)
    destination = root / response["artifact_id"]
    if destination.exists():
        replay_world_artifact(destination)
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
        replay_world_artifact(staging, allow_staging=True)
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def artifact_summary(path, response):
    result = response["result"]
    return {
        "operation": "EXPLORATORY MODEL-SPACE WORLD EXPERIMENT — NOT BIOLOGICAL ESCAPE",
        "artifact_schema": ARTIFACT_SCHEMA,
        **{k: response[k] for k in ("artifact_id", "config_sha256", "result_sha256")},
        "preregistration_id": response["config"]["scenario"]["preregistration_id"],
        "artifact_bytes": sum(p.stat().st_size for p in Path(path).iterdir()),
        "boundary_count": len(result["time_ms"]),
        "dnp01_spike_count": len(result["dnp01_spikes"]),
        "event_counts": {k: len(v) for k, v in result["downstream_events"].items()},
        "statuses": result["statuses"],
        "termination": result["termination"],
        "final_body": result["telemetry"][-1]["body"],
    }
