"""Immutable Phase 16 diagnostic persistence and offline source/result replay."""

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.dnp01_subthreshold_diagnostic import (
    ARTIFACT_SCHEMA,
    DEFAULT_SOURCE,
    build_diagnostic,
    validate_diagnostic,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA
RESULT_FILENAME = "diagnostic.json"


def _manifest(payload):
    raw = canonical_json_bytes(payload, newline=True)
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA,
        "artifact_id": payload["artifact_id"],
        "config_sha256": payload["config_sha256"],
        "result_sha256": payload["result_sha256"],
        "files": {
            RESULT_FILENAME: {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}
        },
    }


def replay_diagnostic_artifact(
    path, *, source_path=DEFAULT_SOURCE, allow_staging=False
):
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("unexpected diagnostic artifact file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        value = json.loads(raw)
        if not isinstance(value, dict) or raw != canonical_json_bytes(
            value, newline=True
        ):
            raise ValueError("noncanonical diagnostic JSON")
        payloads.append(value)
    payload, manifest = payloads
    validate_diagnostic(payload, source_path)
    if manifest != _manifest(payload) or (
        not allow_staging and path.name != payload["artifact_id"]
    ):
        raise ValueError("diagnostic manifest/hash/directory mismatch")
    return payload


def generate_diagnostic_artifact(
    *, output_root=DEFAULT_ARTIFACT_ROOT, source_path=DEFAULT_SOURCE
):
    payload = build_diagnostic(source_path)
    root = Path(output_root)
    destination = root / payload["artifact_id"]
    if destination.exists():
        replay_diagnostic_artifact(destination, source_path=source_path)
        return destination
    root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{payload['artifact_id']}.", dir=root))
    try:
        for name, value in (
            (RESULT_FILENAME, payload),
            ("manifest.json", _manifest(payload)),
        ):
            with (staging / name).open("xb") as stream:
                stream.write(canonical_json_bytes(value, newline=True))
                stream.flush()
                os.fsync(stream.fileno())
        replay_diagnostic_artifact(staging, source_path=source_path, allow_staging=True)
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def diagnostic_summary(path, payload):
    result = payload["result"]
    return {
        "operation": "MODEL_DIAGNOSIS_ONLY — NO RETUNING PERFORMED",
        "artifact_schema": ARTIFACT_SCHEMA,
        **{k: payload[k] for k in ("artifact_id", "config_sha256", "result_sha256")},
        "artifact_bytes": sum(p.stat().st_size for p in Path(path).iterdir()),
        "source_artifact_id": result["source_artifact_id"],
        "looming_targets": [
            {k: v for k, v in target.items() if k != "identity_contributions"}
            for target in result["runs"][1]["targets"]
        ],
        "baseline_targets": [
            {
                k: target[k]
                for k in (
                    "body_id",
                    "peak_membrane_mV_eq",
                    "threshold_margin_at_peak_mV_eq",
                    "integrated_used_drive_mV_eq_ms",
                )
            }
            for target in result["runs"][0]["targets"]
        ],
        "causal_latency": result["causal_latency"],
        "temporal_window": result["temporal_window"],
        "maximum_exposure_audit": result["maximum_exposure_audit"],
        "recorded_exposure_envelope": result["recorded_exposure_envelope"],
        "bottlenecks": result["bottlenecks"],
        "decision": result["decision"],
        "future_review_target": result["future_review_target"],
    }
