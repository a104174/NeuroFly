"""Immutable Phase 7K composition/32-body artifacts and deterministic replay."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.bounded_sensory_composition import (
    CANONICAL_BATTERY_IDS,
    COMPOSITION_ARTIFACT_SCHEMA,
    COMPOSITION_CONFIG_SCHEMA,
    COMPOSITION_RESULT_SCHEMA,
    DEFAULT_COMPOSITION_ROOT,
    DEFAULT_POPULATION32_ROOT,
    POPULATION32_ARTIFACT_SCHEMA,
    POPULATION32_CONFIG_SCHEMA,
    POPULATION32_RESULT_SCHEMA,
    SAMPLE_SIZE,
    composition_artifact_id,
    make_composition_payload,
    make_population32_payload,
    population32_artifact_id,
)
from neurofly.relative_column_assignment import canonical_json_bytes, sha256_bytes

COMPOSITION_CONFIG_FILENAME = "composition_config.json"
COMPOSITION_RESULT_FILENAME = "composition_result.json"
POPULATION32_CONFIG_FILENAME = "config.json"
POPULATION32_RESULT_FILENAME = "population32_result.json"
MANIFEST_FILENAME = "manifest.json"


class BoundedSensoryCompositionArtifactError(ValueError):
    """A Phase 7K artifact is malformed, tampered, or failed full replay."""


@dataclass(frozen=True, slots=True)
class LoadedPhase7KArtifact:
    path: Path
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def as_input(self) -> dict[str, Any]:
        return {
            "artifact_schema": self.manifest["artifact_schema"],
            "artifact_id": self.artifact_id,
            "manifest_sha256": sha256_bytes(
                canonical_json_bytes(self.manifest) + b"\n"
            ),
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "config": self.config,
            "result": self.result,
            "manifest": self.manifest,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "artifact_schema": self.manifest["artifact_schema"],
            "artifact_id": self.artifact_id,
            "body_count": self.result.get(
                "sample_size", len(self.result.get("body_ids", ()))
            ),
            "body_ids": self.result.get("body_ids", []),
            "stimulus_count": len(self.config.get("stimuli", ())),
            "assignment_sample_count": self.result.get("assignment", {}).get(
                "sample_count"
            ),
            "coverage_totals": self.result.get("coverage_totals"),
            "artifact_bytes_including_manifest": sum(
                child.stat().st_size for child in self.path.iterdir()
            ),
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
        }


def _read_canonical(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise BoundedSensoryCompositionArtifactError(f"malformed {label}.") from None
    if not isinstance(value, dict) or raw != canonical_json_bytes(value) + b"\n":
        raise BoundedSensoryCompositionArtifactError(f"{label} is not canonical JSON.")
    return value, raw


def _write_new(path: Path, payload: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _export(
    config: dict[str, Any],
    result: dict[str, Any],
    destination: str | Path,
    *,
    artifact_schema: str,
    config_schema: str,
    result_schema: str,
    config_filename: str,
    result_filename: str,
) -> LoadedPhase7KArtifact:
    if config.get("schema") != config_schema or result.get("schema") != result_schema:
        raise BoundedSensoryCompositionArtifactError("unsupported Phase 7K schema.")
    destination = Path(destination)
    if destination.exists():
        raise BoundedSensoryCompositionArtifactError(
            f"Phase 7K artifacts are immutable; destination exists: {destination}"
        )
    config_bytes = canonical_json_bytes(config) + b"\n"
    result_bytes = canonical_json_bytes(result) + b"\n"
    artifact_id = (
        composition_artifact_id(config, result)
        if artifact_schema == COMPOSITION_ARTIFACT_SCHEMA
        else population32_artifact_id(config, result)
    )
    manifest = {
        "artifact_schema": artifact_schema,
        "artifact_id": artifact_id,
        "config_sha256": sha256_bytes(config_bytes),
        "result_sha256": sha256_bytes(result_bytes),
        "body_ids": result.get("body_ids", []),
    }
    staging: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
        )
        for filename, payload in (
            (config_filename, config_bytes),
            (result_filename, result_bytes),
            (MANIFEST_FILENAME, canonical_json_bytes(manifest) + b"\n"),
        ):
            _write_new(staging / filename, payload)
        if destination.exists():
            raise BoundedSensoryCompositionArtifactError(
                "Phase 7K destination appeared during export."
            )
        os.replace(staging, destination)
        staging = None
    except OSError as exc:
        raise BoundedSensoryCompositionArtifactError(
            "could not persist immutable Phase 7K artifact."
        ) from exc
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return _load(
        destination,
        artifact_schema=artifact_schema,
        config_schema=config_schema,
        result_schema=result_schema,
        config_filename=config_filename,
        result_filename=result_filename,
    )


def _load(
    path: str | Path,
    *,
    artifact_schema: str,
    config_schema: str,
    result_schema: str,
    config_filename: str,
    result_filename: str,
) -> LoadedPhase7KArtifact:
    root = Path(path)
    if not root.is_dir() or {item.name for item in root.iterdir()} != {
        config_filename,
        result_filename,
        MANIFEST_FILENAME,
    }:
        raise BoundedSensoryCompositionArtifactError(
            "Phase 7K artifact file set is invalid."
        )
    config, config_bytes = _read_canonical(root / config_filename, "config")
    result, result_bytes = _read_canonical(root / result_filename, "result")
    manifest, _ = _read_canonical(root / MANIFEST_FILENAME, "manifest")
    identity = (
        composition_artifact_id(config, result)
        if artifact_schema == COMPOSITION_ARTIFACT_SCHEMA
        else population32_artifact_id(config, result)
    )
    if (
        manifest.get("artifact_schema") != artifact_schema
        or manifest.get("artifact_id") != identity
        or manifest.get("config_sha256") != sha256_bytes(config_bytes)
        or manifest.get("result_sha256") != sha256_bytes(result_bytes)
        or manifest.get("body_ids") != result.get("body_ids")
        or config.get("body_ids") != result.get("body_ids")
        or config.get("schema") != config_schema
        or result.get("schema") != result_schema
        or len(result.get("body_ids", ())) != SAMPLE_SIZE
        or len(set(result.get("body_ids", ()))) != SAMPLE_SIZE
    ):
        raise BoundedSensoryCompositionArtifactError(
            "Phase 7K artifact integrity/identity mismatch."
        )
    if artifact_schema == COMPOSITION_ARTIFACT_SCHEMA:
        if (
            result.get("sample_size") != SAMPLE_SIZE
            or result.get("sample_a_sample_b_overlap_count") != 0
            or result.get("sample_a_sample_b_disjoint") is not True
            or result.get("model_outcomes_used") is not False
            or config.get("composition_method") != "DISJOINT_ARTIFACT_UNION"
            or len(result.get("selected_bodies", ())) != SAMPLE_SIZE
            or result.get("body_ids")
            != sorted(
                [
                    *result.get("sample_a_body_ids", ()),
                    *result.get("sample_b_body_ids", ()),
                ]
            )
            or set(result.get("sample_a_body_ids", ()))
            & set(result.get("sample_b_body_ids", ()))
            or [row.get("count") for row in result.get("stratum_counts", ())]
            != [8, 8, 8, 8]
        ):
            raise BoundedSensoryCompositionArtifactError(
                "invalid Sample C composition."
            )
    elif (
        result.get("coverage_totals")
        != {
            "body_stimulus_covered": 32,
            "body_state_exercised": 32,
            "body_transfer_exercised": 32,
            "denominator": 32,
        }
        or result.get("source_contribution_accounting_validated") is not True
        or config.get("body_count") != SAMPLE_SIZE
        or len(config.get("stimuli", ())) != len(CANONICAL_BATTERY_IDS)
        or [row.get("config", {}).get("stimulus_id") for row in config["stimuli"]]
        != list(CANONICAL_BATTERY_IDS)
        or len(config.get("route_contract", ())) != SAMPLE_SIZE
        or {row.get("source_body_id") for row in config["route_contract"]}
        != set(result.get("body_ids", ()))
        or len(result.get("conditions", ())) != 25
    ):
        raise BoundedSensoryCompositionArtifactError(
            "Phase 7K population experiment is incomplete."
        )
    return LoadedPhase7KArtifact(root, identity, config, result, manifest)


def export_composition_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedPhase7KArtifact:
    return _export(
        config,
        result,
        destination,
        artifact_schema=COMPOSITION_ARTIFACT_SCHEMA,
        config_schema=COMPOSITION_CONFIG_SCHEMA,
        result_schema=COMPOSITION_RESULT_SCHEMA,
        config_filename=COMPOSITION_CONFIG_FILENAME,
        result_filename=COMPOSITION_RESULT_FILENAME,
    )


def load_composition_artifact(path: str | Path) -> LoadedPhase7KArtifact:
    return _load(
        path,
        artifact_schema=COMPOSITION_ARTIFACT_SCHEMA,
        config_schema=COMPOSITION_CONFIG_SCHEMA,
        result_schema=COMPOSITION_RESULT_SCHEMA,
        config_filename=COMPOSITION_CONFIG_FILENAME,
        result_filename=COMPOSITION_RESULT_FILENAME,
    )


def replay_composition_artifact(
    path: str | Path,
    **source_options: Any,
) -> LoadedPhase7KArtifact:
    artifact = load_composition_artifact(path)
    config, result = make_composition_payload(**source_options)
    if config != artifact.config or result != artifact.result:
        raise BoundedSensoryCompositionArtifactError(
            "Sample C composition failed full Sample A/B source replay."
        )
    return artifact


def export_population32_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedPhase7KArtifact:
    if config.get("composition_artifact_id") != result.get("composition_artifact_id"):
        raise BoundedSensoryCompositionArtifactError(
            "32-body composition reference mismatch."
        )
    return _export(
        config,
        result,
        destination,
        artifact_schema=POPULATION32_ARTIFACT_SCHEMA,
        config_schema=POPULATION32_CONFIG_SCHEMA,
        result_schema=POPULATION32_RESULT_SCHEMA,
        config_filename=POPULATION32_CONFIG_FILENAME,
        result_filename=POPULATION32_RESULT_FILENAME,
    )


def load_population32_artifact(path: str | Path) -> LoadedPhase7KArtifact:
    return _load(
        path,
        artifact_schema=POPULATION32_ARTIFACT_SCHEMA,
        config_schema=POPULATION32_CONFIG_SCHEMA,
        result_schema=POPULATION32_RESULT_SCHEMA,
        config_filename=POPULATION32_CONFIG_FILENAME,
        result_filename=POPULATION32_RESULT_FILENAME,
    )


def replay_population32_artifact(
    path: str | Path,
    composition_path: str | Path,
    **source_options: Any,
) -> LoadedPhase7KArtifact:
    artifact = load_population32_artifact(path)
    config, result = make_population32_payload(str(composition_path), **source_options)
    if config != artifact.config or result != artifact.result:
        raise BoundedSensoryCompositionArtifactError(
            "Phase 7K population experiment failed full deterministic replay."
        )
    return artifact


def make_composition_artifact_payload(
    *, output_root: str | Path = DEFAULT_COMPOSITION_ROOT, **source_options: Any
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    config, result = make_composition_payload(**source_options)
    artifact_id = composition_artifact_id(config, result)
    return config, result, Path(output_root) / artifact_id


def make_population32_artifact_payload(
    composition_path: str | Path,
    *,
    output_root: str | Path = DEFAULT_POPULATION32_ROOT,
    **source_options: Any,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    config, result = make_population32_payload(str(composition_path), **source_options)
    artifact_id = population32_artifact_id(config, result)
    return config, result, Path(output_root) / artifact_id
