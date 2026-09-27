"""Immutable Phase 7J Sample B artifacts and deterministic full-source replay."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.bounded_sensory_population_artifacts import replay_sample_artifact
from neurofly.bounded_sensory_robustness import (
    CANONICAL_SAMPLE_A_ID,
    DEFAULT_PHASE7H_PATH,
    DEFAULT_PHASE7I_EXPERIMENT_PATH,
    DEFAULT_PHASE7I_PLAN_PATH,
    DEFAULT_SAMPLE_A_PATH,
    EXPERIMENT_ARTIFACT_SCHEMA,
    EXPERIMENT_CONFIG_SCHEMA,
    EXPERIMENT_RESULT_SCHEMA,
    PLAN_ARTIFACT_SCHEMA,
    PLAN_CONFIG_SCHEMA,
    PLAN_RESULT_SCHEMA,
    SAMPLE_ARTIFACT_SCHEMA,
    SAMPLE_CONFIG_SCHEMA,
    SAMPLE_RESULT_SCHEMA,
    compute_sample_b_coverage_plan,
    compute_sample_b_experiment,
    make_source_bundle,
    replay_canonical_baselines,
    select_independent_sample,
)
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    canonical_json_bytes,
    sha256_bytes,
)

SAMPLE_CONFIG_FILENAME = "sample_b_config.json"
SAMPLE_RESULT_FILENAME = "sample_b_result.json"
PLAN_CONFIG_FILENAME = "coverage_plan_b_config.json"
PLAN_RESULT_FILENAME = "coverage_plan_b_result.json"
EXPERIMENT_CONFIG_FILENAME = "population_b_config.json"
EXPERIMENT_RESULT_FILENAME = "population_b_result.json"
MANIFEST_FILENAME = "manifest.json"


class BoundedSensoryRobustnessArtifactError(ValueError):
    """A Phase 7J artifact failed integrity or deterministic source replay."""


@dataclass(frozen=True, slots=True)
class LoadedSampleBArtifact:
    path: Path
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def as_input(self) -> dict[str, Any]:
        return _as_input(self)

    def summary(self) -> dict[str, Any]:
        return {
            "artifact_schema": SAMPLE_ARTIFACT_SCHEMA,
            "artifact_id": self.artifact_id,
            "sample_size": self.result["sample_size"],
            "body_ids": self.result["body_ids"],
            "stratum_counts": self.result["stratum_counts"],
            "sample_a_overlap_count": self.result["sample_a_overlap_count"],
            "selection_method_id": self.config["selection_method_id"],
            "model_outcomes_used": self.result["model_outcomes_used"],
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "artifact_bytes_including_manifest": sum(
                item.stat().st_size for item in self.path.iterdir()
            ),
        }


@dataclass(frozen=True, slots=True)
class LoadedSampleBCoveragePlan:
    path: Path
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def as_input(self) -> dict[str, Any]:
        return _as_input(self)

    def summary(self) -> dict[str, Any]:
        return {
            "artifact_schema": PLAN_ARTIFACT_SCHEMA,
            "artifact_id": self.artifact_id,
            "body_ids": self.result["body_ids"],
            "initial_covered_body_ids": self.result["initial_covered_body_ids"],
            "initial_uncovered_body_ids": self.result["initial_uncovered_body_ids"],
            "coverage_extension_stimuli": self.result["coverage_extension_stimuli"],
            "model_outcomes_used": self.result["model_outcomes_used"],
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "artifact_bytes_including_manifest": sum(
                item.stat().st_size for item in self.path.iterdir()
            ),
        }


@dataclass(frozen=True, slots=True)
class LoadedSampleBExperiment:
    path: Path
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def as_input(self) -> dict[str, Any]:
        return _as_input(self)

    def summary(self) -> dict[str, Any]:
        return {
            "artifact_schema": EXPERIMENT_ARTIFACT_SCHEMA,
            "artifact_id": self.artifact_id,
            "sample_a_artifact_id": self.result["sample_a_artifact_id"],
            "sample_b_artifact_id": self.result["sample_b_artifact_id"],
            "coverage_plan_artifact_id": self.result["coverage_plan_artifact_id"],
            "body_ids": self.result["body_ids"],
            "stimulus_count": len(self.config["stimuli"]),
            "assignment_sample_count": self.result["assignment"]["sample_count"],
            "coverage_totals": self.result["coverage_totals"],
            "target_summary": self.result["target_summary"],
            "artifact_bytes_including_manifest": sum(
                item.stat().st_size for item in self.path.iterdir()
            ),
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
        }


def _as_input(artifact: Any) -> dict[str, Any]:
    if isinstance(artifact, dict):
        return artifact
    manifest = artifact.manifest
    return {
        "artifact_schema": manifest["artifact_schema"],
        "artifact_id": artifact.artifact_id,
        "manifest_sha256": sha256_bytes(canonical_json_bytes(manifest) + b"\n"),
        "config_sha256": manifest["config_sha256"],
        "result_sha256": manifest["result_sha256"],
        "config": artifact.config,
        "result": artifact.result,
        "manifest": manifest,
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


def sample_b_artifact_id(config: dict[str, Any], result: dict[str, Any]) -> str:
    return _artifact_id(SAMPLE_ARTIFACT_SCHEMA, config, result)


def sample_b_plan_artifact_id(config: dict[str, Any], result: dict[str, Any]) -> str:
    return _artifact_id(PLAN_ARTIFACT_SCHEMA, config, result)


def sample_b_experiment_artifact_id(
    config: dict[str, Any], result: dict[str, Any]
) -> str:
    return _artifact_id(EXPERIMENT_ARTIFACT_SCHEMA, config, result)


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
) -> tuple[Path, dict[str, Any]]:
    if config.get("schema") != config_schema or result.get("schema") != result_schema:
        raise BoundedSensoryRobustnessArtifactError("unsupported Phase 7J schema.")
    config_bytes = canonical_json_bytes(config) + b"\n"
    result_bytes = canonical_json_bytes(result) + b"\n"
    manifest = {
        "artifact_schema": schema,
        "artifact_id": _artifact_id(schema, config, result),
        "config_sha256": sha256_bytes(config_bytes),
        "result_sha256": sha256_bytes(result_bytes),
        "body_ids": result.get("body_ids", []),
    }
    destination = Path(destination)
    if destination.exists():
        raise BoundedSensoryRobustnessArtifactError(
            f"Phase 7J artifacts are immutable; destination exists: {destination}"
        )
    staging: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
        )
        payloads = (
            (config_filename, config_bytes),
            (result_filename, result_bytes),
            (MANIFEST_FILENAME, canonical_json_bytes(manifest) + b"\n"),
        )
        for filename, payload in payloads:
            with (staging / filename).open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        if destination.exists():
            raise BoundedSensoryRobustnessArtifactError(
                "Phase 7J artifact destination appeared during export."
            )
        os.replace(staging, destination)
        staging = None
    except OSError as exc:
        raise BoundedSensoryRobustnessArtifactError(
            "could not persist immutable Phase 7J artifact."
        ) from exc
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return destination, manifest


def _read_canonical(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        data = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise BoundedSensoryRobustnessArtifactError(f"malformed {label}.") from None
    if not isinstance(data, dict) or raw != canonical_json_bytes(data) + b"\n":
        raise BoundedSensoryRobustnessArtifactError(f"{label} is not canonical JSON.")
    return data, raw


def _load(
    path: str | Path,
    *,
    schema: str,
    config_schema: str,
    result_schema: str,
    config_filename: str,
    result_filename: str,
) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = Path(path)
    expected_files = {config_filename, result_filename, MANIFEST_FILENAME}
    if not root.is_dir() or {entry.name for entry in root.iterdir()} != expected_files:
        raise BoundedSensoryRobustnessArtifactError(
            "Phase 7J artifact file set is invalid."
        )
    config, config_bytes = _read_canonical(root / config_filename, "config")
    result, result_bytes = _read_canonical(root / result_filename, "result")
    manifest, _ = _read_canonical(root / MANIFEST_FILENAME, "manifest")
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
        raise BoundedSensoryRobustnessArtifactError(
            "Phase 7J artifact integrity mismatch."
        )
    body_ids = result.get("body_ids")
    if (
        not isinstance(body_ids, list)
        or len(body_ids) != 16
        or len(set(body_ids)) != 16
    ):
        raise BoundedSensoryRobustnessArtifactError(
            "Phase 7J artifact body set is invalid."
        )
    return root, config, result, manifest


def _validate_sample_b_identity(config: dict[str, Any], result: dict[str, Any]) -> None:
    body_ids = result.get("body_ids", ())
    sample_a_ids = result.get("sample_a_body_ids", ())
    selected = result.get("selected_bodies", ())
    if (
        config.get("artifact_schema") != SAMPLE_ARTIFACT_SCHEMA
        or result.get("sample_size") != 16
        or len(body_ids) != 16
        or len(set(body_ids)) != 16
        or len(set(body_ids) & set(sample_a_ids)) != 0
        or result.get("sample_a_overlap_count") != 0
        or result.get("disjoint_from_sample_a") is not True
        or len(selected) != 16
        or [item.get("body_id") for item in selected] != body_ids
    ):
        raise BoundedSensoryRobustnessArtifactError("Sample B identity is invalid.")
    for neuron_type, side in (
        ("LC4", "L"),
        ("LC4", "R"),
        ("LPLC2", "L"),
        ("LPLC2", "R"),
    ):
        if (
            sum(
                item.get("neuron_type") == neuron_type and item.get("side") == side
                for item in selected
            )
            != 4
        ):
            raise BoundedSensoryRobustnessArtifactError("Sample B is not 4×4 balanced.")
    if (
        result.get("model_outcomes_used") is not False
        or config.get("selection_excludes_model_outcomes") is not True
    ):
        raise BoundedSensoryRobustnessArtifactError(
            "Sample B selection must be explicitly outcome-blind."
        )


def export_sample_b_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedSampleBArtifact:
    _validate_sample_b_identity(config, result)
    path, _ = _export(
        config,
        result,
        destination,
        schema=SAMPLE_ARTIFACT_SCHEMA,
        config_schema=SAMPLE_CONFIG_SCHEMA,
        result_schema=SAMPLE_RESULT_SCHEMA,
        config_filename=SAMPLE_CONFIG_FILENAME,
        result_filename=SAMPLE_RESULT_FILENAME,
    )
    return load_sample_b_artifact(path)


def load_sample_b_artifact(path: str | Path) -> LoadedSampleBArtifact:
    root, config, result, manifest = _load(
        path,
        schema=SAMPLE_ARTIFACT_SCHEMA,
        config_schema=SAMPLE_CONFIG_SCHEMA,
        result_schema=SAMPLE_RESULT_SCHEMA,
        config_filename=SAMPLE_CONFIG_FILENAME,
        result_filename=SAMPLE_RESULT_FILENAME,
    )
    _validate_sample_b_identity(config, result)
    return LoadedSampleBArtifact(
        root, manifest["artifact_id"], config, result, manifest
    )


def _sample_a_and_source(
    sample_a_path: str | Path,
    *,
    source_root: str | Path,
    workbook_path: str | Path,
) -> tuple[Any, Any, Any]:
    sample_a = replay_sample_artifact(
        sample_a_path, source_root=source_root, workbook_path=workbook_path
    )
    if sample_a.artifact_id != CANONICAL_SAMPLE_A_ID:
        raise BoundedSensoryRobustnessArtifactError(
            "wrong canonical Sample A artifact."
        )
    source, grid, circuit = make_source_bundle(str(source_root), str(workbook_path))
    return sample_a, source, circuit


def replay_sample_b_artifact(
    path: str | Path,
    sample_a_path: str | Path = DEFAULT_SAMPLE_A_PATH,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> LoadedSampleBArtifact:
    artifact = load_sample_b_artifact(path)
    sample_a, source, circuit = _sample_a_and_source(
        sample_a_path, source_root=source_root, workbook_path=workbook_path
    )
    config, result = select_independent_sample(source, circuit, sample_a.as_input())
    if canonical_json_bytes(config) != canonical_json_bytes(
        artifact.config
    ) or canonical_json_bytes(result) != canonical_json_bytes(artifact.result):
        raise BoundedSensoryRobustnessArtifactError(
            "Sample B failed deterministic source replay."
        )
    return artifact


def export_sample_b_plan_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedSampleBCoveragePlan:
    if (
        config.get("artifact_schema") != PLAN_ARTIFACT_SCHEMA
        or result.get("body_ids") != config.get("body_ids")
        or result.get("model_outcomes_used") is not False
        or result.get("neural_dynamics_computed") is not False
        or result.get("dn_p01_outputs_read_for_design") is not False
    ):
        raise BoundedSensoryRobustnessArtifactError(
            "Sample B coverage plan identity/semantic boundary is invalid."
        )
    path, _ = _export(
        config,
        result,
        destination,
        schema=PLAN_ARTIFACT_SCHEMA,
        config_schema=PLAN_CONFIG_SCHEMA,
        result_schema=PLAN_RESULT_SCHEMA,
        config_filename=PLAN_CONFIG_FILENAME,
        result_filename=PLAN_RESULT_FILENAME,
    )
    return load_sample_b_plan_artifact(path)


def load_sample_b_plan_artifact(path: str | Path) -> LoadedSampleBCoveragePlan:
    root, config, result, manifest = _load(
        path,
        schema=PLAN_ARTIFACT_SCHEMA,
        config_schema=PLAN_CONFIG_SCHEMA,
        result_schema=PLAN_RESULT_SCHEMA,
        config_filename=PLAN_CONFIG_FILENAME,
        result_filename=PLAN_RESULT_FILENAME,
    )
    if (
        result.get("body_ids") != config.get("body_ids")
        or result.get("model_outcomes_used") is not False
        or result.get("neural_dynamics_computed") is not False
        or result.get("dn_p01_outputs_read_for_design") is not False
    ):
        raise BoundedSensoryRobustnessArtifactError(
            "Sample B plan semantics are invalid."
        )
    return LoadedSampleBCoveragePlan(
        root, manifest["artifact_id"], config, result, manifest
    )


def make_sample_b_plan_payload(
    sample_b_path: str | Path,
    sample_a_path: str | Path = DEFAULT_SAMPLE_A_PATH,
    phase7h_path: str | Path = DEFAULT_PHASE7H_PATH,
    phase7i_plan_path: str | Path = DEFAULT_PHASE7I_PLAN_PATH,
    phase7i_experiment_path: str | Path = DEFAULT_PHASE7I_EXPERIMENT_PATH,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> tuple[dict[str, Any], dict[str, Any]]:
    sample_b = replay_sample_b_artifact(
        sample_b_path,
        sample_a_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    baselines = replay_canonical_baselines(
        sample_a_path=str(sample_a_path),
        phase7h_path=str(phase7h_path),
        phase7i_plan_path=str(phase7i_plan_path),
        phase7i_experiment_path=str(phase7i_experiment_path),
        source_root=str(source_root),
        workbook_path=str(workbook_path),
    )
    sample_a, phase7h, plan_i, experiment_i, source, grid, circuit = baselines
    return compute_sample_b_coverage_plan(
        sample_b.as_input(),
        sample_a,
        phase7h,
        plan_i,
        experiment_i,
        source,
        grid,
        circuit,
    )


def replay_sample_b_plan_artifact(
    path: str | Path,
    sample_b_path: str | Path,
    sample_a_path: str | Path = DEFAULT_SAMPLE_A_PATH,
    phase7h_path: str | Path = DEFAULT_PHASE7H_PATH,
    phase7i_plan_path: str | Path = DEFAULT_PHASE7I_PLAN_PATH,
    phase7i_experiment_path: str | Path = DEFAULT_PHASE7I_EXPERIMENT_PATH,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> LoadedSampleBCoveragePlan:
    artifact = load_sample_b_plan_artifact(path)
    config, result = make_sample_b_plan_payload(
        sample_b_path,
        sample_a_path,
        phase7h_path,
        phase7i_plan_path,
        phase7i_experiment_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    if config != artifact.config or result != artifact.result:
        raise BoundedSensoryRobustnessArtifactError(
            "Sample B coverage plan failed full anatomy/source replay."
        )
    return artifact


def export_sample_b_experiment_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedSampleBExperiment:
    if (
        config.get("artifact_schema") != EXPERIMENT_ARTIFACT_SCHEMA
        or result.get("body_ids") != config.get("body_ids")
        or result.get("coverage_totals")
        != {
            "body_stimulus_covered": 16,
            "body_state_exercised": 16,
            "body_transfer_exercised": 16,
            "denominator": 16,
        }
        or result.get("contribution_accounting_validated") is not True
    ):
        raise BoundedSensoryRobustnessArtifactError(
            "Sample B experiment is incomplete or semantically invalid."
        )
    path, _ = _export(
        config,
        result,
        destination,
        schema=EXPERIMENT_ARTIFACT_SCHEMA,
        config_schema=EXPERIMENT_CONFIG_SCHEMA,
        result_schema=EXPERIMENT_RESULT_SCHEMA,
        config_filename=EXPERIMENT_CONFIG_FILENAME,
        result_filename=EXPERIMENT_RESULT_FILENAME,
    )
    return load_sample_b_experiment_artifact(path)


def load_sample_b_experiment_artifact(path: str | Path) -> LoadedSampleBExperiment:
    root, config, result, manifest = _load(
        path,
        schema=EXPERIMENT_ARTIFACT_SCHEMA,
        config_schema=EXPERIMENT_CONFIG_SCHEMA,
        result_schema=EXPERIMENT_RESULT_SCHEMA,
        config_filename=EXPERIMENT_CONFIG_FILENAME,
        result_filename=EXPERIMENT_RESULT_FILENAME,
    )
    if (
        config.get("artifact_schema") != EXPERIMENT_ARTIFACT_SCHEMA
        or result.get("body_ids") != config.get("body_ids")
        or result.get("sample_a_artifact_id") != CANONICAL_SAMPLE_A_ID
        or result.get("coverage_totals")
        != {
            "body_stimulus_covered": 16,
            "body_state_exercised": 16,
            "body_transfer_exercised": 16,
            "denominator": 16,
        }
    ):
        raise BoundedSensoryRobustnessArtifactError(
            "Sample B experiment identity is invalid."
        )
    return LoadedSampleBExperiment(
        root, manifest["artifact_id"], config, result, manifest
    )


def make_sample_b_experiment_payload(
    sample_b_path: str | Path,
    plan_b_path: str | Path,
    sample_a_path: str | Path = DEFAULT_SAMPLE_A_PATH,
    phase7h_path: str | Path = DEFAULT_PHASE7H_PATH,
    phase7i_plan_path: str | Path = DEFAULT_PHASE7I_PLAN_PATH,
    phase7i_experiment_path: str | Path = DEFAULT_PHASE7I_EXPERIMENT_PATH,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> tuple[dict[str, Any], dict[str, Any]]:
    sample_b = replay_sample_b_artifact(
        sample_b_path,
        sample_a_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    plan_b = load_sample_b_plan_artifact(plan_b_path)
    baselines = replay_canonical_baselines(
        sample_a_path=str(sample_a_path),
        phase7h_path=str(phase7h_path),
        phase7i_plan_path=str(phase7i_plan_path),
        phase7i_experiment_path=str(phase7i_experiment_path),
        source_root=str(source_root),
        workbook_path=str(workbook_path),
    )
    sample_a, phase7h, plan_i, experiment_i, source, grid, circuit = baselines
    expected_plan_config, expected_plan_result = compute_sample_b_coverage_plan(
        sample_b.as_input(),
        sample_a,
        phase7h,
        plan_i,
        experiment_i,
        source,
        grid,
        circuit,
    )
    if expected_plan_config != plan_b.config or expected_plan_result != plan_b.result:
        raise BoundedSensoryRobustnessArtifactError(
            "persisted Sample B plan does not replay from source anatomy."
        )
    return compute_sample_b_experiment(
        sample_b.as_input(),
        plan_b.as_input(),
        sample_a,
        phase7h,
        plan_i,
        experiment_i,
        source,
        grid,
        circuit,
    )


def replay_sample_b_experiment_artifact(
    path: str | Path,
    sample_b_path: str | Path,
    plan_b_path: str | Path,
    sample_a_path: str | Path = DEFAULT_SAMPLE_A_PATH,
    phase7h_path: str | Path = DEFAULT_PHASE7H_PATH,
    phase7i_plan_path: str | Path = DEFAULT_PHASE7I_PLAN_PATH,
    phase7i_experiment_path: str | Path = DEFAULT_PHASE7I_EXPERIMENT_PATH,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> LoadedSampleBExperiment:
    artifact = load_sample_b_experiment_artifact(path)
    config, result = make_sample_b_experiment_payload(
        sample_b_path,
        plan_b_path,
        sample_a_path,
        phase7h_path,
        phase7i_plan_path,
        phase7i_experiment_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    if config != artifact.config or result != artifact.result:
        raise BoundedSensoryRobustnessArtifactError(
            "Sample B experiment failed full deterministic replay."
        )
    return artifact
