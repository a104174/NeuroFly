"""Compact immutable offline activation sensitivity artifacts."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

from neurofly.muscle_activation_sensitivity import (
    ARTIFACT_SCHEMA,
    build_sensitivity,
    validate_sensitivity,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA
RESULT_FILENAME = "sensitivity.json"


def _manifest(experiment: dict) -> dict:
    raw = canonical_json_bytes(experiment, newline=True)
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA,
        "artifact_id": experiment["artifact_id"],
        "config_sha256": experiment["config_sha256"],
        "result_sha256": experiment["result_sha256"],
        "files": {
            RESULT_FILENAME: {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}
        },
    }


def replay_sensitivity_artifact(
    path: str | Path, *, allow_staging=False, **sources
) -> dict:
    path = Path(path)
    if not path.is_dir() or {p.name for p in path.iterdir()} != {
        RESULT_FILENAME,
        "manifest.json",
    }:
        raise ValueError("unexpected activation sensitivity file set")
    payloads = []
    for name in (RESULT_FILENAME, "manifest.json"):
        raw = (path / name).read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical activation sensitivity JSON")
        payloads.append(payload)
    experiment, manifest = payloads
    validate_sensitivity(experiment, **sources)
    if manifest != _manifest(experiment) or (
        not allow_staging and path.name != experiment["artifact_id"]
    ):
        raise ValueError("activation sensitivity artifact/hash identity mismatch")
    return experiment


def generate_sensitivity_artifact(
    *, output_root=DEFAULT_ARTIFACT_ROOT, **sources
) -> Path:
    experiment = build_sensitivity(**sources)
    root = Path(output_root)
    destination = root / experiment["artifact_id"]
    if destination.exists():
        replay_sensitivity_artifact(destination, **sources)
        return destination
    root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{experiment['artifact_id']}.", dir=root))
    try:
        for name, payload in (
            (RESULT_FILENAME, experiment),
            ("manifest.json", _manifest(experiment)),
        ):
            with (staging / name).open("xb") as stream:
                stream.write(canonical_json_bytes(payload, newline=True))
                stream.flush()
                os.fsync(stream.fileno())
        replay_sensitivity_artifact(staging, allow_staging=True, **sources)
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def sensitivity_summary(path: Path, experiment: dict) -> dict:
    cells = experiment["result"]["cells"]
    return {
        "operation": "EXPLORATORY_ACTIVATION_SCALE_SENSITIVITY_NO_EMPIRICAL_FITTING",
        "artifact_schema": ARTIFACT_SCHEMA,
        "artifact_id": experiment["artifact_id"],
        "config_sha256": experiment["config_sha256"],
        "result_sha256": experiment["result_sha256"],
        "artifact_bytes": sum(p.stat().st_size for p in path.iterdir()),
        "config": experiment["config"],
        "analysis": experiment["result"]["analysis"],
        "reference_cell_id": experiment["result"]["reference_cell_id"],
        "cells": cells,
    }
