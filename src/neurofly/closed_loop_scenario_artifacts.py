"""Immutable integrated Baseline/Looming artifacts with offline numerical replay."""

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.closed_loop_scenario import (
    ARTIFACT_SCHEMA,
    build_scenario_battery,
    validate_scenario_battery,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA
RESULT_FILENAME = "scenarios.json"


def _manifest(response):
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


def replay_scenario_artifact(path, *, allow_staging=False):
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("unexpected scenario artifact file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical scenario JSON")
        payloads.append(payload)
    response, manifest = payloads
    validate_scenario_battery(response)
    if manifest != _manifest(response) or (
        not allow_staging and path.name != response["artifact_id"]
    ):
        raise ValueError("scenario manifest/hash/directory mismatch")
    return response


def generate_scenario_artifact(*, output_root=DEFAULT_ARTIFACT_ROOT):
    response = build_scenario_battery()
    root = Path(output_root)
    destination = root / response["artifact_id"]
    if destination.exists():
        replay_scenario_artifact(destination)
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
        replay_scenario_artifact(staging, allow_staging=True)
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def artifact_summary(path, response):
    return {
        "operation": "EXPLORATORY CLOSED LOOP — NOT BIOLOGICAL ESCAPE",
        "artifact_schema": ARTIFACT_SCHEMA,
        **{k: response[k] for k in ("artifact_id", "config_sha256", "result_sha256")},
        "artifact_bytes": sum(p.stat().st_size for p in Path(path).iterdir()),
        "runs": [
            {
                "scenario_kind": r["result"]["scenario_kind"],
                "scenario_execution_id": r["result"]["scenario_execution_id"],
                "sensory_body_count": len(r["result"]["sensory_identities"]),
                "boundary_count": len(r["result"]["time_ms"]),
                "dnp01_spike_count": len(r["result"]["dnp01_spikes"]),
                "event_counts": {
                    k: len(v) for k, v in r["result"]["downstream_events"].items()
                },
                "statuses": r["result"]["statuses"],
                "final_body": r["result"]["telemetry"][-1]["body"],
            }
            for r in response["result"]["runs"]
        ],
    }
