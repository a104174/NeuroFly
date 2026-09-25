"""Immutable, offline artifacts for Phase 7D anatomical assignments."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from neurofly.relative_column_assignment import (
    BODY_IDS,
    RELATIVE_ASSIGNMENT_RESULT_SCHEMA,
    RelativeColumnAssignmentError,
    canonical_json_bytes,
    compute_assignment_result,
    fixed_body_exposure_summary,
    load_relative_column_grid,
    load_relative_column_source,
    sha256_bytes,
)

ARTIFACT_SCHEMA_VERSION = "relative_column_sensory_assignment_artifact_v1"
CONFIG_FILENAME = "config.json"
RESULT_FILENAME = "assignment_result.json"
MANIFEST_FILENAME = "manifest.json"
_PAYLOAD_SCHEMAS = {
    CONFIG_FILENAME: "relative_column_assignment_config_v1",
    RESULT_FILENAME: RELATIVE_ASSIGNMENT_RESULT_SCHEMA,
}


class RelativeColumnArtifactError(RuntimeError):
    """Base error for Phase 7D artifact operations."""


class RelativeColumnArtifactIntegrityError(RelativeColumnArtifactError):
    """An assignment artifact failed schema, hash, or replay validation."""


class RelativeColumnArtifactExportError(RelativeColumnArtifactError):
    """An immutable assignment artifact could not be created."""


@dataclass(frozen=True, slots=True)
class LoadedRelativeColumnArtifact:
    path: Path
    artifact_id: str
    config: Mapping[str, Any]
    result: Mapping[str, Any]
    manifest: Mapping[str, Any]

    def inspection_dict(self) -> dict[str, Any]:
        result = dict(self.result)
        return {
            "artifact_id": self.artifact_id,
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "experiment_id": result["experiment_id"],
            "source_contract_sha256": self.config["source_identity"][
                "contract_identity_sha256"
            ],
            "column_grid_sha256": self.config["column_grid_identity"]["sha256"],
            "body_ids": list(BODY_IDS),
            "sample_count": result["sample_count"],
            "stimulus_ids": [
                entry["config"]["stimulus_id"] for entry in self.config["stimuli"]
            ],
            "body_exposure_summary": fixed_body_exposure_summary(result),
            "neural_dynamics_present": False,
            "validation_status": "ANATOMICAL_ASSIGNMENT_REPLAY_ONLY",
        }


def _artifact_id(config_sha256: str, result_sha256: str) -> str:
    return sha256_bytes(
        canonical_json_bytes(
            {
                "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                "config_sha256": config_sha256,
                "result_sha256": result_sha256,
                "body_ids": list(BODY_IDS),
            }
        )
    )


def relative_column_artifact_id(
    config: Mapping[str, Any], result: Mapping[str, Any]
) -> str:
    """Return the immutable content identity without writing an artifact."""

    config_bytes = canonical_json_bytes(dict(config)) + b"\n"
    result_bytes = canonical_json_bytes(dict(result)) + b"\n"
    return _artifact_id(sha256_bytes(config_bytes), sha256_bytes(result_bytes))


def _canonical_payload(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise RelativeColumnArtifactIntegrityError(f"malformed {label}.") from None
    if not isinstance(value, dict):
        raise RelativeColumnArtifactIntegrityError(f"{label} must be a JSON object.")
    expected = canonical_json_bytes(value) + b"\n"
    if raw != expected:
        raise RelativeColumnArtifactIntegrityError(f"{label} is not canonical JSON.")
    return value, raw


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise RelativeColumnArtifactExportError(
            f"could not write assignment artifact file {path.name}"
        ) from exc


def export_relative_column_artifact(
    config: Mapping[str, Any],
    result: Mapping[str, Any],
    destination: str | Path,
) -> LoadedRelativeColumnArtifact:
    """Atomically create one immutable config/result artifact directory."""

    if config.get("schema") != _PAYLOAD_SCHEMAS[CONFIG_FILENAME]:
        raise RelativeColumnArtifactExportError("unsupported assignment config schema.")
    if result.get("schema") != _PAYLOAD_SCHEMAS[RESULT_FILENAME]:
        raise RelativeColumnArtifactExportError("unsupported assignment result schema.")
    if tuple(result.get("body_ids", ())) != BODY_IDS:
        raise RelativeColumnArtifactExportError(
            "assignment result body set is not the fixed four."
        )
    output = Path(destination)
    if output.exists():
        raise RelativeColumnArtifactExportError(
            f"assignment artifacts are immutable; destination exists: {output}"
        )
    config_bytes = canonical_json_bytes(dict(config)) + b"\n"
    result_bytes = canonical_json_bytes(dict(result)) + b"\n"
    config_hash = sha256_bytes(config_bytes)
    result_hash = sha256_bytes(result_bytes)
    artifact_id = relative_column_artifact_id(config, result)
    manifest = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "config_sha256": config_hash,
        "result_sha256": result_hash,
        "body_ids": list(BODY_IDS),
        "files": {
            CONFIG_FILENAME: {
                "schema": _PAYLOAD_SCHEMAS[CONFIG_FILENAME],
                "bytes": len(config_bytes),
                "sha256": sha256_bytes(config_bytes),
            },
            RESULT_FILENAME: {
                "schema": _PAYLOAD_SCHEMAS[RESULT_FILENAME],
                "bytes": len(result_bytes),
                "sha256": sha256_bytes(result_bytes),
            },
        },
        "source_contract_sha256": config["source_identity"]["contract_identity_sha256"],
        "column_grid_sha256": config["column_grid_identity"]["sha256"],
    }
    manifest_bytes = canonical_json_bytes(manifest) + b"\n"
    staging: Path | None = None
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, manifest_bytes)
        load_relative_column_artifact(staging)
        if output.exists():
            raise RelativeColumnArtifactExportError(
                f"assignment artifacts are immutable; destination exists: {output}"
            )
        os.replace(staging, output)
        staging = None
    except RelativeColumnArtifactError:
        raise
    except OSError as exc:
        raise RelativeColumnArtifactExportError(
            "could not finalize assignment artifact"
        ) from exc
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return load_relative_column_artifact(output)


def load_relative_column_artifact(
    path: str | Path,
) -> LoadedRelativeColumnArtifact:
    """Load without executing a stimulus; validate all payload and identity hashes."""

    root = Path(path)
    if not root.is_dir():
        raise RelativeColumnArtifactIntegrityError(
            f"assignment artifact directory does not exist: {root}"
        )
    if {item.name for item in root.iterdir()} != {
        CONFIG_FILENAME,
        RESULT_FILENAME,
        MANIFEST_FILENAME,
    }:
        raise RelativeColumnArtifactIntegrityError(
            "assignment artifact contains missing or unexpected files."
        )
    manifest, _ = _canonical_payload(root / MANIFEST_FILENAME, "manifest")
    expected_manifest_fields = {
        "artifact_schema_version",
        "artifact_id",
        "config_sha256",
        "result_sha256",
        "body_ids",
        "files",
        "source_contract_sha256",
        "column_grid_sha256",
    }
    if set(manifest) != expected_manifest_fields:
        raise RelativeColumnArtifactIntegrityError(
            "invalid assignment manifest fields."
        )
    if manifest["artifact_schema_version"] != ARTIFACT_SCHEMA_VERSION:
        raise RelativeColumnArtifactIntegrityError(
            "unsupported assignment artifact schema."
        )
    if manifest["body_ids"] != list(BODY_IDS):
        raise RelativeColumnArtifactIntegrityError(
            "manifest body identities are not the fixed four."
        )
    if not isinstance(manifest["files"], dict) or set(manifest["files"]) != set(
        _PAYLOAD_SCHEMAS
    ):
        raise RelativeColumnArtifactIntegrityError(
            "assignment manifest file set is invalid."
        )
    payloads: dict[str, dict[str, Any]] = {}
    payload_hashes: dict[str, str] = {}
    for filename, schema in _PAYLOAD_SCHEMAS.items():
        entry = manifest["files"][filename]
        if not isinstance(entry, dict) or set(entry) != {"schema", "bytes", "sha256"}:
            raise RelativeColumnArtifactIntegrityError(
                f"invalid metadata for {filename}."
            )
        if (
            entry["schema"] != schema
            or isinstance(entry["bytes"], bool)
            or not isinstance(entry["bytes"], int)
            or entry["bytes"] < 0
        ):
            raise RelativeColumnArtifactIntegrityError(
                f"invalid schema/size for {filename}."
            )
        payload, raw = _canonical_payload(root / filename, filename)
        if len(raw) != entry["bytes"] or sha256_bytes(raw) != entry["sha256"]:
            raise RelativeColumnArtifactIntegrityError(
                f"payload digest mismatch for {filename}."
            )
        payloads[filename] = payload
        payload_hashes[filename] = sha256_bytes(raw)
    config = payloads[CONFIG_FILENAME]
    result = payloads[RESULT_FILENAME]
    if result.get("body_ids") != list(BODY_IDS):
        raise RelativeColumnArtifactIntegrityError(
            "result body set is not the fixed four."
        )
    if result.get("schema") != RELATIVE_ASSIGNMENT_RESULT_SCHEMA:
        raise RelativeColumnArtifactIntegrityError(
            "unsupported assignment result payload."
        )
    if (
        manifest["config_sha256"] != payload_hashes[CONFIG_FILENAME]
        or manifest["result_sha256"] != payload_hashes[RESULT_FILENAME]
        or manifest["artifact_id"]
        != _artifact_id(manifest["config_sha256"], manifest["result_sha256"])
    ):
        raise RelativeColumnArtifactIntegrityError(
            "assignment artifact identity mismatch."
        )
    source_identity = config.get("source_identity")
    grid_identity = config.get("column_grid_identity")
    if not isinstance(source_identity, dict) or not isinstance(grid_identity, dict):
        raise RelativeColumnArtifactIntegrityError("artifact provenance is malformed.")
    if manifest["source_contract_sha256"] != source_identity.get(
        "contract_identity_sha256"
    ):
        raise RelativeColumnArtifactIntegrityError("source contract identity mismatch.")
    if manifest["column_grid_sha256"] != config.get("column_grid_identity", {}).get(
        "sha256"
    ):
        raise RelativeColumnArtifactIntegrityError("column grid identity mismatch.")
    return LoadedRelativeColumnArtifact(
        path=root,
        artifact_id=manifest["artifact_id"],
        config=MappingProxyType(config),
        result=MappingProxyType(result),
        manifest=MappingProxyType(manifest),
    )


def replay_relative_column_artifact(
    artifact_path: str | Path,
    *,
    source_root: str | Path,
    workbook_path: str | Path,
) -> LoadedRelativeColumnArtifact:
    """Recompute assignments from source/config and require exact JSON equality."""

    artifact = load_relative_column_artifact(artifact_path)
    try:
        source = load_relative_column_source(source_root)
        grid = load_relative_column_grid(workbook_path, source)
        expected_config, expected_result = compute_assignment_result(
            source, grid, config=dict(artifact.config)
        )
    except (RelativeColumnAssignmentError, OSError, ValueError) as exc:
        raise RelativeColumnArtifactIntegrityError(
            f"assignment artifact replay could not validate source: {exc}"
        ) from exc
    if canonical_json_bytes(expected_config) != canonical_json_bytes(
        dict(artifact.config)
    ):
        raise RelativeColumnArtifactIntegrityError(
            "assignment config differs on replay."
        )
    if canonical_json_bytes(expected_result) != canonical_json_bytes(
        dict(artifact.result)
    ):
        raise RelativeColumnArtifactIntegrityError(
            "assignment result differs on replay."
        )
    return artifact


def make_fixed_assignment(
    *,
    source_root: str | Path,
    workbook_path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    source = load_relative_column_source(source_root)
    grid = load_relative_column_grid(workbook_path, source)
    return compute_assignment_result(source, grid)
