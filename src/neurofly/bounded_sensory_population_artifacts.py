"""Immutable artifacts and full offline replay for the Phase 7H 16-body run."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.bounded_sensory_population import (
    DEFAULT_EXPERIMENT_OUTPUT_ROOT,
    DEFAULT_SAMPLE_OUTPUT_ROOT,
    EXPERIMENT_ARTIFACT_SCHEMA,
    EXPERIMENT_CONFIG_SCHEMA,
    EXPERIMENT_RESULT_SCHEMA,
    SAMPLE_ARTIFACT_SCHEMA,
    SAMPLE_CONFIG_SCHEMA,
    SAMPLE_RESULT_SCHEMA,
    compute_population_experiment,
    make_source_bundle,
    select_bounded_sample,
)
from neurofly.relative_column_assignment import (
    DEFAULT_OUTPUT_ROOT as ASSIGNMENT_OUTPUT_ROOT,
)
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    canonical_json_bytes,
    sha256_bytes,
)
from neurofly.relative_column_assignment_artifacts import (
    replay_relative_column_artifact,
)
from neurofly.relative_column_dnp01_artifacts import (
    DEFAULT_OUTPUT_ROOT as TRANSFER_OUTPUT_ROOT,
)
from neurofly.relative_column_dnp01_artifacts import (
    DEFAULT_SENSORY_ARTIFACT_PATH,
)
from neurofly.relative_column_dnp01_artifacts import (
    replay_artifact as replay_phase7f_artifact,
)
from neurofly.relative_column_sensory_artifacts import (
    replay_relative_column_sensory_artifact,
)

SAMPLE_CONFIG_FILENAME = "sample_config.json"
SAMPLE_RESULT_FILENAME = "sample_result.json"
EXPERIMENT_CONFIG_FILENAME = "config.json"
EXPERIMENT_RESULT_FILENAME = "population_result.json"
MANIFEST_FILENAME = "manifest.json"
DEFAULT_SAMPLE_ARTIFACT_ROOT = DEFAULT_SAMPLE_OUTPUT_ROOT
DEFAULT_EXPERIMENT_ARTIFACT_ROOT = DEFAULT_EXPERIMENT_OUTPUT_ROOT
DEFAULT_PHASE7D_ARTIFACT_PATH = ASSIGNMENT_OUTPUT_ROOT / (
    "404473c66c36b9f0332a203928200552c6c2e5490af446caae6c3d7475daafbe"
)
DEFAULT_PHASE7F_ARTIFACT_ROOT = TRANSFER_OUTPUT_ROOT


class BoundedPopulationArtifactError(ValueError):
    """A Phase 7H artifact is invalid or failed full-source replay."""


@dataclass(frozen=True, slots=True)
class LoadedSampleArtifact:
    path: Path
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def as_input(self) -> dict[str, Any]:
        return {
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
            "artifact_id": self.artifact_id,
            "artifact_schema": SAMPLE_ARTIFACT_SCHEMA,
            "sample_size": self.result["sample_size"],
            "body_ids": self.result["body_ids"],
            "stratum_counts": self.result["stratum_counts"],
            "selection_method_id": self.config["selection_method_id"],
            "selection_used_model_outcomes": self.result["model_outcomes_used"],
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
        }


@dataclass(frozen=True, slots=True)
class LoadedPopulationArtifact:
    path: Path
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def summary(self) -> dict[str, Any]:
        total_bytes = sum(path.stat().st_size for path in self.path.iterdir())
        return {
            "artifact_id": self.artifact_id,
            "artifact_schema": EXPERIMENT_ARTIFACT_SCHEMA,
            "sample_artifact_id": self.result["sample_artifact_id"],
            "body_ids": self.result["body_ids"],
            "stimulus_count": len(self.config["stimuli"]),
            "assignment_sample_count": self.result["assignment"]["sample_count"],
            "condition_summaries": [
                {
                    "condition_id": condition["condition_id"],
                    "pathway_mask": condition["pathway_mask"],
                    "k_transfer_mveq_per_state": condition["k_transfer_mveq_per_state"],
                    "targets": [
                        {
                            "body_id": target["body_id"],
                            "peak_drive_mveq": target["peak_drive_mveq"],
                            "minimum_membrane_mv": target["minimum_membrane_mv"],
                            "maximum_membrane_mv": target["maximum_membrane_mv"],
                            "simulated_spikes": target["simulated_spikes"],
                        }
                        for target in condition["targets"]
                    ],
                }
                for condition in self.result["conditions"]
            ],
            "scale_comparison": self.result["scale_comparison"],
            "artifact_bytes_including_manifest": total_bytes,
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


def sample_artifact_id(config: dict[str, Any], result: dict[str, Any]) -> str:
    return _artifact_id(SAMPLE_ARTIFACT_SCHEMA, config, result)


def population_artifact_id(config: dict[str, Any], result: dict[str, Any]) -> str:
    return _artifact_id(EXPERIMENT_ARTIFACT_SCHEMA, config, result)


def _read_canonical(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise BoundedPopulationArtifactError(f"malformed {label}.") from None
    if not isinstance(value, dict) or raw != canonical_json_bytes(value) + b"\n":
        raise BoundedPopulationArtifactError(f"{label} is not canonical JSON.")
    return value, raw


def _write_new(path: Path, payload: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _atomic_export(
    destination: Path,
    files: tuple[tuple[str, bytes], ...],
) -> None:
    if destination.exists():
        raise BoundedPopulationArtifactError(
            f"artifacts are immutable; destination exists: {destination}"
        )
    staging: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
        )
        for filename, payload in files:
            _write_new(staging / filename, payload)
        if destination.exists():
            raise BoundedPopulationArtifactError(
                f"artifacts are immutable; destination exists: {destination}"
            )
        os.replace(staging, destination)
        staging = None
    except OSError as exc:
        raise BoundedPopulationArtifactError(
            "could not finalize immutable artifact."
        ) from exc
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def export_sample_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedSampleArtifact:
    if (
        config.get("schema") != SAMPLE_CONFIG_SCHEMA
        or result.get("schema") != SAMPLE_RESULT_SCHEMA
    ):
        raise BoundedPopulationArtifactError(
            "unsupported sample artifact payload schema."
        )
    if result.get("sample_size") != 16 or len(result.get("body_ids", ())) != 16:
        raise BoundedPopulationArtifactError(
            "sample artifact must contain exactly 16 bodies."
        )
    config_bytes = canonical_json_bytes(config) + b"\n"
    result_bytes = canonical_json_bytes(result) + b"\n"
    manifest = {
        "artifact_schema": SAMPLE_ARTIFACT_SCHEMA,
        "artifact_id": sample_artifact_id(config, result),
        "config_sha256": sha256_bytes(config_bytes),
        "result_sha256": sha256_bytes(result_bytes),
        "sample_size": 16,
        "body_ids": result["body_ids"],
    }
    manifest_bytes = canonical_json_bytes(manifest) + b"\n"
    _atomic_export(
        Path(destination),
        (
            (SAMPLE_CONFIG_FILENAME, config_bytes),
            (SAMPLE_RESULT_FILENAME, result_bytes),
            (MANIFEST_FILENAME, manifest_bytes),
        ),
    )
    return load_sample_artifact(destination)


def load_sample_artifact(path: str | Path) -> LoadedSampleArtifact:
    root = Path(path)
    if not root.is_dir() or {item.name for item in root.iterdir()} != {
        SAMPLE_CONFIG_FILENAME,
        SAMPLE_RESULT_FILENAME,
        MANIFEST_FILENAME,
    }:
        raise BoundedPopulationArtifactError("sample artifact file set is invalid.")
    config, config_bytes = _read_canonical(
        root / SAMPLE_CONFIG_FILENAME, "sample config"
    )
    result, result_bytes = _read_canonical(
        root / SAMPLE_RESULT_FILENAME, "sample result"
    )
    manifest, _ = _read_canonical(root / MANIFEST_FILENAME, "sample manifest")
    if (
        set(manifest)
        != {
            "artifact_schema",
            "artifact_id",
            "config_sha256",
            "result_sha256",
            "sample_size",
            "body_ids",
        }
        or manifest["artifact_schema"] != SAMPLE_ARTIFACT_SCHEMA
        or manifest["config_sha256"] != sha256_bytes(config_bytes)
        or manifest["result_sha256"] != sha256_bytes(result_bytes)
        or manifest["artifact_id"] != sample_artifact_id(config, result)
        or manifest["sample_size"] != 16
        or manifest["body_ids"] != result.get("body_ids")
        or config.get("schema") != SAMPLE_CONFIG_SCHEMA
        or result.get("schema") != SAMPLE_RESULT_SCHEMA
        or len(result.get("body_ids", ())) != 16
        or len(set(result.get("body_ids", ()))) != 16
        or len(result.get("selected_bodies", ())) != 16
        or result.get("model_outcomes_used") is not False
        or config.get("selection_excludes_model_outcomes") is not True
    ):
        raise BoundedPopulationArtifactError(
            "sample artifact integrity/identity mismatch."
        )
    return LoadedSampleArtifact(root, manifest["artifact_id"], config, result, manifest)


def replay_sample_artifact(
    path: str | Path,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> LoadedSampleArtifact:
    artifact = load_sample_artifact(path)
    source, _, circuit = make_source_bundle(str(source_root), str(workbook_path))
    config, result = select_bounded_sample(source, circuit)
    if canonical_json_bytes(config) != canonical_json_bytes(
        artifact.config
    ) or canonical_json_bytes(result) != canonical_json_bytes(artifact.result):
        raise BoundedPopulationArtifactError("sample selection failed source replay.")
    return artifact


def _sample_artifact_input(artifact: LoadedSampleArtifact) -> dict[str, Any]:
    return artifact.as_input()


def make_population_artifact_payload(
    sample_artifact_path: str | Path,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
    phase7d_artifact_path: str | Path | None = None,
    phase7e_artifact_path: str | Path = DEFAULT_SENSORY_ARTIFACT_PATH,
    phase7f_artifact_path: str | Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    sample = replay_sample_artifact(
        sample_artifact_path, source_root=source_root, workbook_path=workbook_path
    )
    assignment_path = phase7d_artifact_path or DEFAULT_PHASE7D_ARTIFACT_PATH
    replay_relative_column_artifact(
        assignment_path, source_root=source_root, workbook_path=workbook_path
    )
    baseline_sensory = replay_relative_column_sensory_artifact(
        phase7e_artifact_path,
        assignment_artifact_path=assignment_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    transfer_root = (
        Path(phase7f_artifact_path)
        if phase7f_artifact_path
        else DEFAULT_PHASE7F_ARTIFACT_ROOT
    )
    # The canonical 7F artifact is content-addressed; locate its exact reference ID.
    from neurofly.relative_column_dnp01_artifacts import artifact_id as phase7f_id
    from neurofly.relative_column_dnp01_transfer import EXPECTED_SENSORY_ARTIFACT_ID

    baseline_candidate = transfer_root
    if (
        baseline_candidate.is_dir()
        and not (baseline_candidate / "manifest.json").exists()
    ):
        baseline_candidate = (
            baseline_candidate
            / "4a000add359e60c0c0c654881a4659652d749c548af0e167469d210035c20213"
        )
    baseline_transfer = replay_phase7f_artifact(
        baseline_candidate,
        sensory_artifact_path=phase7e_artifact_path,
        assignment_artifact_path=assignment_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    if (
        baseline_transfer.result.get("source_sensory_artifact_id")
        != EXPECTED_SENSORY_ARTIFACT_ID
    ):
        raise BoundedPopulationArtifactError(
            "canonical Phase 7F source identity changed."
        )
    if baseline_transfer.artifact_id != phase7f_id(
        baseline_transfer.config, baseline_transfer.result
    ):
        raise BoundedPopulationArtifactError(
            "canonical Phase 7F artifact identity is invalid."
        )
    source, grid, circuit = make_source_bundle(str(source_root), str(workbook_path))
    return compute_population_experiment(
        _sample_artifact_input(sample),
        source,
        grid,
        circuit,
        baseline_sensory,
        baseline_transfer,
    )


def export_population_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedPopulationArtifact:
    if (
        config.get("schema") != EXPERIMENT_CONFIG_SCHEMA
        or result.get("schema") != EXPERIMENT_RESULT_SCHEMA
    ):
        raise BoundedPopulationArtifactError("unsupported population artifact schema.")
    if (
        len(result.get("body_ids", ())) != 16
        or len(set(result.get("body_ids", ()))) != 16
    ):
        raise BoundedPopulationArtifactError(
            "population result must contain 16 bodies."
        )
    config_bytes = canonical_json_bytes(config) + b"\n"
    result_bytes = canonical_json_bytes(result) + b"\n"
    manifest = {
        "artifact_schema": EXPERIMENT_ARTIFACT_SCHEMA,
        "artifact_id": population_artifact_id(config, result),
        "config_sha256": sha256_bytes(config_bytes),
        "result_sha256": sha256_bytes(result_bytes),
        "sample_artifact_id": result["sample_artifact_id"],
        "body_ids": result["body_ids"],
    }
    _atomic_export(
        Path(destination),
        (
            (EXPERIMENT_CONFIG_FILENAME, config_bytes),
            (EXPERIMENT_RESULT_FILENAME, result_bytes),
            (MANIFEST_FILENAME, canonical_json_bytes(manifest) + b"\n"),
        ),
    )
    return load_population_artifact(destination)


def load_population_artifact(path: str | Path) -> LoadedPopulationArtifact:
    root = Path(path)
    if not root.is_dir() or {item.name for item in root.iterdir()} != {
        EXPERIMENT_CONFIG_FILENAME,
        EXPERIMENT_RESULT_FILENAME,
        MANIFEST_FILENAME,
    }:
        raise BoundedPopulationArtifactError("population artifact file set is invalid.")
    config, config_bytes = _read_canonical(
        root / EXPERIMENT_CONFIG_FILENAME, "population config"
    )
    result, result_bytes = _read_canonical(
        root / EXPERIMENT_RESULT_FILENAME, "population result"
    )
    manifest, _ = _read_canonical(root / MANIFEST_FILENAME, "population manifest")
    if (
        set(manifest)
        != {
            "artifact_schema",
            "artifact_id",
            "config_sha256",
            "result_sha256",
            "sample_artifact_id",
            "body_ids",
        }
        or manifest["artifact_schema"] != EXPERIMENT_ARTIFACT_SCHEMA
        or manifest["config_sha256"] != sha256_bytes(config_bytes)
        or manifest["result_sha256"] != sha256_bytes(result_bytes)
        or manifest["artifact_id"] != population_artifact_id(config, result)
        or manifest["sample_artifact_id"] != result.get("sample_artifact_id")
        or manifest["body_ids"] != result.get("body_ids")
        or config.get("schema") != EXPERIMENT_CONFIG_SCHEMA
        or result.get("schema") != EXPERIMENT_RESULT_SCHEMA
        or len(result.get("body_ids", ())) != 16
        or len(set(result.get("body_ids", ()))) != 16
        or config.get("sample_artifact", {}).get("artifact_id")
        != result.get("sample_artifact_id")
    ):
        raise BoundedPopulationArtifactError(
            "population artifact integrity/identity mismatch."
        )
    return LoadedPopulationArtifact(
        root, manifest["artifact_id"], config, result, manifest
    )


def replay_population_artifact(
    path: str | Path,
    sample_artifact_path: str | Path,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
    phase7d_artifact_path: str | Path | None = None,
    phase7e_artifact_path: str | Path = DEFAULT_SENSORY_ARTIFACT_PATH,
    phase7f_artifact_path: str | Path | None = None,
) -> LoadedPopulationArtifact:
    artifact = load_population_artifact(path)
    config, result = make_population_artifact_payload(
        sample_artifact_path,
        source_root=source_root,
        workbook_path=workbook_path,
        phase7d_artifact_path=phase7d_artifact_path,
        phase7e_artifact_path=phase7e_artifact_path,
        phase7f_artifact_path=phase7f_artifact_path,
    )
    if canonical_json_bytes(config) != canonical_json_bytes(
        artifact.config
    ) or canonical_json_bytes(result) != canonical_json_bytes(artifact.result):
        raise BoundedPopulationArtifactError("population artifact failed full replay.")
    return artifact
