"""Immutable Phase 7I coverage plans and full replayable experiment artifacts."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.bounded_sensory_coverage import (
    CANONICAL_BODY_IDS,
    CANONICAL_PHASE7H_ID,
    CANONICAL_SAMPLE_ID,
    DEFAULT_EXPERIMENT_OUTPUT_ROOT,
    DEFAULT_PLAN_OUTPUT_ROOT,
    EXPERIMENT_ARTIFACT_SCHEMA,
    EXPERIMENT_CONFIG_SCHEMA,
    EXPERIMENT_RESULT_SCHEMA,
    PLAN_ARTIFACT_SCHEMA,
    PLAN_CONFIG_SCHEMA,
    PLAN_RESULT_SCHEMA,
    compute_coverage_experiment,
    compute_coverage_plan,
    replay_inputs,
)
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    canonical_json_bytes,
    sha256_bytes,
)

PLAN_CONFIG_FILENAME = "plan_config.json"
PLAN_RESULT_FILENAME = "plan_result.json"
EXPERIMENT_CONFIG_FILENAME = "config.json"
EXPERIMENT_RESULT_FILENAME = "coverage_result.json"
MANIFEST_FILENAME = "manifest.json"
DEFAULT_SAMPLE_ARTIFACT_PATH = (
    DEFAULT_PLAN_OUTPUT_ROOT.parent / "bounded_sensory_sample_v1" / CANONICAL_SAMPLE_ID
)
DEFAULT_PHASE7H_ARTIFACT_PATH = (
    DEFAULT_EXPERIMENT_OUTPUT_ROOT.parent
    / "bounded_sensory_population_v1"
    / CANONICAL_PHASE7H_ID
)


class BoundedSensoryCoverageArtifactError(ValueError):
    """A Phase 7I artifact failed integrity or deterministic replay."""


@dataclass(frozen=True, slots=True)
class LoadedCoveragePlan:
    path: Path
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def as_input(self) -> dict[str, Any]:
        return {
            "artifact_schema": PLAN_ARTIFACT_SCHEMA,
            "artifact_id": self.artifact_id,
            "manifest_sha256": sha256_bytes(
                canonical_json_bytes(self.manifest) + b"\n"
            ),
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "config": self.config,
            "result": self.result,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "artifact_schema": PLAN_ARTIFACT_SCHEMA,
            "artifact_id": self.artifact_id,
            "phase7h_artifact_id": self.config["phase7h_artifact"]["artifact_id"],
            "body_ids": self.result["body_ids"],
            "initial_uncovered_body_ids": self.result["initial_uncovered_body_ids"],
            "coverage_extension_stimuli": self.result["coverage_extension_stimuli"],
            "model_outcomes_used": self.result["model_outcomes_used"],
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
        }


@dataclass(frozen=True, slots=True)
class LoadedCoverageExperiment:
    path: Path
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def summary(self) -> dict[str, Any]:
        return {
            "artifact_schema": EXPERIMENT_ARTIFACT_SCHEMA,
            "artifact_id": self.artifact_id,
            "coverage_plan_artifact_id": self.result["coverage_plan_artifact_id"],
            "phase7h_artifact_id": self.result["phase7h_artifact_id"],
            "body_ids": self.result["body_ids"],
            "stimulus_count": len(self.config["stimuli"]),
            "assignment_sample_count": self.result["assignment"]["sample_count"],
            "coverage_totals": self.result["coverage_totals"],
            "conditions": [
                {
                    "condition_id": condition["condition_id"],
                    "targets": [
                        {
                            "body_id": target["body_id"],
                            "peak_drive_mveq": target["peak_drive_mveq"],
                            "minimum_membrane_mv": target["minimum_membrane_mv"],
                            "maximum_membrane_mv": target["maximum_membrane_mv"],
                            "spikes": target["simulated_spikes"],
                        }
                        for target in condition["targets"]
                    ],
                }
                for condition in self.result["conditions"]
            ],
            "artifact_bytes_including_manifest": sum(
                item.stat().st_size for item in self.path.iterdir()
            ),
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
        }


def _artifact_id(schema: str, config: dict[str, Any], result: dict[str, Any]) -> str:
    return sha256_bytes(
        canonical_json_bytes(
            {
                "artifact_schema": schema,
                "config_sha256": sha256_bytes(canonical_json_bytes(config) + b"\n"),
                "result_sha256": sha256_bytes(canonical_json_bytes(result) + b"\n"),
            }
        )
    )


def plan_artifact_id(config: dict[str, Any], result: dict[str, Any]) -> str:
    return _artifact_id(PLAN_ARTIFACT_SCHEMA, config, result)


def coverage_artifact_id(config: dict[str, Any], result: dict[str, Any]) -> str:
    return _artifact_id(EXPERIMENT_ARTIFACT_SCHEMA, config, result)


def _write_immutable(destination: Path, files: tuple[tuple[str, bytes], ...]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise BoundedSensoryCoverageArtifactError(
            f"Phase 7I artifacts are immutable; destination exists: {destination}"
        )
    temporary = Path(tempfile.mkdtemp(prefix=".phase7i-", dir=destination.parent))
    try:
        for name, payload in files:
            (temporary / name).write_bytes(payload)
        os.replace(temporary, destination)
    except Exception:
        # A failed write leaves only a temporary child, never mutates an artifact.
        for path in temporary.iterdir():
            path.unlink()
        temporary.rmdir()
        raise


def _export(
    config: dict[str, Any],
    result: dict[str, Any],
    destination: str | Path,
    *,
    schema: str,
    config_schema: str,
    result_schema: str,
    config_filename: str,
    result_filename: str,
) -> Path:
    if config.get("schema") != config_schema or result.get("schema") != result_schema:
        raise BoundedSensoryCoverageArtifactError(
            "unsupported Phase 7I artifact schema."
        )
    destination = Path(destination)
    config_bytes = canonical_json_bytes(config) + b"\n"
    result_bytes = canonical_json_bytes(result) + b"\n"
    manifest = {
        "artifact_schema": schema,
        "artifact_id": _artifact_id(schema, config, result),
        "config_sha256": sha256_bytes(config_bytes),
        "result_sha256": sha256_bytes(result_bytes),
        "body_ids": result.get("body_ids", []),
    }
    _write_immutable(
        destination,
        (
            (config_filename, config_bytes),
            (result_filename, result_bytes),
            (MANIFEST_FILENAME, canonical_json_bytes(manifest) + b"\n"),
        ),
    )
    return destination


def export_coverage_plan(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedCoveragePlan:
    if config.get("artifact_schema") != PLAN_ARTIFACT_SCHEMA or result.get(
        "body_ids"
    ) != list(CANONICAL_BODY_IDS):
        raise BoundedSensoryCoverageArtifactError("unsupported coverage-plan identity.")
    path = _export(
        config,
        result,
        destination,
        schema=PLAN_ARTIFACT_SCHEMA,
        config_schema=PLAN_CONFIG_SCHEMA,
        result_schema=PLAN_RESULT_SCHEMA,
        config_filename=PLAN_CONFIG_FILENAME,
        result_filename=PLAN_RESULT_FILENAME,
    )
    return load_coverage_plan(path)


def export_coverage_experiment(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedCoverageExperiment:
    if (
        config.get("artifact_schema") != EXPERIMENT_ARTIFACT_SCHEMA
        or result.get("body_ids") != list(CANONICAL_BODY_IDS)
        or result.get("coverage_totals")
        != {
            "body_stimulus_covered": 16,
            "body_state_exercised": 16,
            "body_transfer_exercised": 16,
            "denominator": 16,
        }
    ):
        raise BoundedSensoryCoverageArtifactError("coverage experiment is incomplete.")
    path = _export(
        config,
        result,
        destination,
        schema=EXPERIMENT_ARTIFACT_SCHEMA,
        config_schema=EXPERIMENT_CONFIG_SCHEMA,
        result_schema=EXPERIMENT_RESULT_SCHEMA,
        config_filename=EXPERIMENT_CONFIG_FILENAME,
        result_filename=EXPERIMENT_RESULT_FILENAME,
    )
    return load_coverage_experiment(path)


def _read_canonical(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise BoundedSensoryCoverageArtifactError(f"could not read {label}.") from exc
    if not isinstance(value, dict) or raw != canonical_json_bytes(value) + b"\n":
        raise BoundedSensoryCoverageArtifactError(f"{label} is not canonical JSON.")
    return value, raw


def _load(
    path: str | Path, *, plan: bool
) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = Path(path)
    config_filename = PLAN_CONFIG_FILENAME if plan else EXPERIMENT_CONFIG_FILENAME
    result_filename = PLAN_RESULT_FILENAME if plan else EXPERIMENT_RESULT_FILENAME
    expected_files = {config_filename, result_filename, MANIFEST_FILENAME}
    if not root.is_dir() or {item.name for item in root.iterdir()} != expected_files:
        raise BoundedSensoryCoverageArtifactError(
            "Phase 7I artifact file set is invalid."
        )
    config, config_bytes = _read_canonical(root / config_filename, "config")
    result, result_bytes = _read_canonical(root / result_filename, "result")
    manifest, _ = _read_canonical(root / MANIFEST_FILENAME, "manifest")
    schema = PLAN_ARTIFACT_SCHEMA if plan else EXPERIMENT_ARTIFACT_SCHEMA
    config_schema = PLAN_CONFIG_SCHEMA if plan else EXPERIMENT_CONFIG_SCHEMA
    result_schema = PLAN_RESULT_SCHEMA if plan else EXPERIMENT_RESULT_SCHEMA
    if (
        set(manifest)
        != {
            "artifact_schema",
            "artifact_id",
            "config_sha256",
            "result_sha256",
            "body_ids",
        }
        or manifest.get("artifact_schema") != schema
        or manifest.get("config_sha256") != sha256_bytes(config_bytes)
        or manifest.get("result_sha256") != sha256_bytes(result_bytes)
        or manifest.get("artifact_id") != _artifact_id(schema, config, result)
        or manifest.get("body_ids") != result.get("body_ids")
        or config.get("schema") != config_schema
        or result.get("schema") != result_schema
    ):
        raise BoundedSensoryCoverageArtifactError(
            "Phase 7I artifact integrity mismatch."
        )
    if plan and config.get("artifact_schema") != schema:
        raise BoundedSensoryCoverageArtifactError(
            "coverage-plan schema identity mismatch."
        )
    if plan and result.get("body_ids") != list(CANONICAL_BODY_IDS):
        raise BoundedSensoryCoverageArtifactError(
            "coverage-plan body identities differ."
        )
    if not plan and (
        config.get("artifact_schema") != schema
        or config.get("body_ids") != result.get("body_ids")
        or result.get("body_ids") != list(CANONICAL_BODY_IDS)
    ):
        raise BoundedSensoryCoverageArtifactError(
            "coverage experiment identity mismatch."
        )
    return root, config, result, manifest


def load_coverage_plan(path: str | Path) -> LoadedCoveragePlan:
    root, config, result, manifest = _load(path, plan=True)
    return LoadedCoveragePlan(root, manifest["artifact_id"], config, result, manifest)


def load_coverage_experiment(path: str | Path) -> LoadedCoverageExperiment:
    root, config, result, manifest = _load(path, plan=False)
    return LoadedCoverageExperiment(
        root, manifest["artifact_id"], config, result, manifest
    )


def make_coverage_plan_payload(
    sample_artifact_path: str | Path = DEFAULT_SAMPLE_ARTIFACT_PATH,
    phase7h_artifact_path: str | Path = DEFAULT_PHASE7H_ARTIFACT_PATH,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> tuple[dict[str, Any], dict[str, Any]]:
    sample, phase7h, source, grid, circuit = replay_inputs(
        str(sample_artifact_path),
        str(phase7h_artifact_path),
        source_root=str(source_root),
        workbook_path=str(workbook_path),
    )
    return compute_coverage_plan(sample.as_input(), phase7h, source, grid, circuit)


def replay_coverage_plan(
    path: str | Path,
    sample_artifact_path: str | Path = DEFAULT_SAMPLE_ARTIFACT_PATH,
    phase7h_artifact_path: str | Path = DEFAULT_PHASE7H_ARTIFACT_PATH,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> LoadedCoveragePlan:
    artifact = load_coverage_plan(path)
    config, result = make_coverage_plan_payload(
        sample_artifact_path,
        phase7h_artifact_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    if config != artifact.config or result != artifact.result:
        raise BoundedSensoryCoverageArtifactError(
            "coverage plan failed full source replay."
        )
    return artifact


def make_coverage_experiment_payload(
    plan_artifact_path: str | Path,
    sample_artifact_path: str | Path = DEFAULT_SAMPLE_ARTIFACT_PATH,
    phase7h_artifact_path: str | Path = DEFAULT_PHASE7H_ARTIFACT_PATH,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> tuple[dict[str, Any], dict[str, Any]]:
    plan = load_coverage_plan(plan_artifact_path)
    sample, phase7h, source, grid, circuit = replay_inputs(
        str(sample_artifact_path),
        str(phase7h_artifact_path),
        source_root=str(source_root),
        workbook_path=str(workbook_path),
    )
    expected_config, expected_result = compute_coverage_plan(
        sample.as_input(), phase7h, source, grid, circuit
    )
    if plan.config != expected_config or plan.result != expected_result:
        raise BoundedSensoryCoverageArtifactError(
            "coverage plan did not replay from sources."
        )
    return compute_coverage_experiment(
        plan.as_input(), sample.as_input(), phase7h, source, grid, circuit
    )


def replay_coverage_experiment(
    path: str | Path,
    plan_artifact_path: str | Path,
    sample_artifact_path: str | Path = DEFAULT_SAMPLE_ARTIFACT_PATH,
    phase7h_artifact_path: str | Path = DEFAULT_PHASE7H_ARTIFACT_PATH,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> LoadedCoverageExperiment:
    artifact = load_coverage_experiment(path)
    config, result = make_coverage_experiment_payload(
        plan_artifact_path,
        sample_artifact_path,
        phase7h_artifact_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    if config != artifact.config or result != artifact.result:
        raise BoundedSensoryCoverageArtifactError(
            "coverage experiment failed full source replay."
        )
    return artifact
