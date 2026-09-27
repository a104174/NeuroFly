"""Immutable, content-addressed Phase 7O result artifacts."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    canonical_json_bytes,
    sha256_bytes,
)
from neurofly.sensory_population_execution import (
    ARTIFACT_SCHEMA,
    CONFIG_SCHEMA,
    RESULT_SCHEMA,
)

DEFAULT_ROOT = DEFAULT_SOURCE_ROOT / "sensory_population_experiment_311_v1"
CONFIG_FILE = "experiment_config.json"
RESULT_FILE = "experiment_result.json"
MANIFEST_FILE = "manifest.json"


class SensoryPopulationExecutionArtifactError(ValueError):
    """A Phase 7O result artifact is malformed, altered, or incomplete."""


def _raw(value: dict[str, Any]) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def _identity(config_raw: bytes, result_raw: bytes) -> tuple[str, dict[str, Any]]:
    config_sha = sha256_bytes(config_raw)
    result_sha = sha256_bytes(result_raw)
    artifact_id = sha256_bytes(
        canonical_json_bytes(
            {
                "artifact_schema": ARTIFACT_SCHEMA,
                "config_sha256": config_sha,
                "result_sha256": result_sha,
            }
        )
    )
    return artifact_id, {
        "artifact_schema": ARTIFACT_SCHEMA,
        "artifact_id": artifact_id,
        "config_schema": CONFIG_SCHEMA,
        "result_schema": RESULT_SCHEMA,
        "config_sha256": config_sha,
        "result_sha256": result_sha,
    }


def _validate(config: dict[str, Any], result: dict[str, Any]) -> None:
    ids = result.get("body_ids", [])
    if (
        config.get("schema") != CONFIG_SCHEMA
        or config.get("artifact_schema") != ARTIFACT_SCHEMA
        or result.get("schema") != RESULT_SCHEMA
        or len(ids) != 311
        or len(set(ids)) != 311
        or result.get("body_count") != 311
        or len(result.get("route_contract", ())) != 311
        or {row.get("source_body_id") for row in result["route_contract"]} != set(ids)
        or result.get("condition_count") != len(result.get("conditions", ()))
        or result.get("coverage_totals")
        != {
            "body_stimulus_covered": 311,
            "body_state_exercised": 311,
            "body_transfer_exercised": 311,
        }
        or result.get("contribution_ledger_row_count") != 130931
        or result.get("source_contribution_accounting_validated") is not True
        or result.get("structural_weight_independence_validated") is not True
        or result.get("nested_128_regression", {}).get("exact_equality") is not True
        or config.get("population_normalization") != "none"
        or config.get("structural_edge_count_numerical_use")
        != "none_source_metadata_only"
    ):
        raise SensoryPopulationExecutionArtifactError(
            "invalid Phase 7O result schema or invariants"
        )


@dataclass(frozen=True, slots=True)
class LoadedExecutionArtifact:
    path: Path
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    @property
    def artifact_id(self) -> str:
        return self.manifest["artifact_id"]

    def summary(self) -> dict[str, Any]:
        return {
            "artifact_schema": ARTIFACT_SCHEMA,
            "artifact_id": self.artifact_id,
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "path": str(self.path),
            "bytes_including_manifest": sum(
                p.stat().st_size for p in self.path.iterdir()
            ),
            "body_count": 311,
            "condition_count": self.result["condition_count"],
            "contribution_ledger_row_count": self.result[
                "contribution_ledger_row_count"
            ],
        }


def load_execution_artifact(path: str | Path) -> LoadedExecutionArtifact:
    root = Path(path)
    if not root.is_dir() or {p.name for p in root.iterdir()} != {
        CONFIG_FILE,
        RESULT_FILE,
        MANIFEST_FILE,
    }:
        raise SensoryPopulationExecutionArtifactError(
            "Phase 7O artifact file set changed"
        )
    try:
        raws = [
            (root / name).read_bytes()
            for name in (CONFIG_FILE, RESULT_FILE, MANIFEST_FILE)
        ]
        config, result, manifest = [json.loads(raw.decode("utf-8")) for raw in raws]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SensoryPopulationExecutionArtifactError(
            "malformed Phase 7O JSON"
        ) from exc
    if any(
        raw != _raw(value)
        for raw, value in zip(raws, (config, result, manifest), strict=True)
    ):
        raise SensoryPopulationExecutionArtifactError("Phase 7O JSON is not canonical")
    _validate(config, result)
    _, expected_manifest = _identity(raws[0], raws[1])
    if manifest != expected_manifest or root.name != manifest["artifact_id"]:
        raise SensoryPopulationExecutionArtifactError(
            "Phase 7O artifact integrity mismatch"
        )
    return LoadedExecutionArtifact(root, config, result, manifest)


def export_execution_artifact(
    config: dict[str, Any],
    result: dict[str, Any],
    *,
    output_root: str | Path = DEFAULT_ROOT,
) -> LoadedExecutionArtifact:
    _validate(config, result)
    config_raw, result_raw = _raw(config), _raw(result)
    artifact_id, manifest = _identity(config_raw, result_raw)
    root = Path(output_root)
    destination = root / artifact_id
    if destination.exists():
        existing = load_execution_artifact(destination)
        if existing.config != config or existing.result != result:
            raise SensoryPopulationExecutionArtifactError(
                "immutable Phase 7O artifact differs from replay"
            )
        return existing
    root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{artifact_id}.", dir=root))
    try:
        for name, raw in (
            (CONFIG_FILE, config_raw),
            (RESULT_FILE, result_raw),
            (MANIFEST_FILE, _raw(manifest)),
        ):
            with (staging / name).open("xb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return load_execution_artifact(destination)
