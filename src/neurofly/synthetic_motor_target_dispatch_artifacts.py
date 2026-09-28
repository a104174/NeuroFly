"""Immutable content-addressed artifacts for Phase 8L target dispatch."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any

from neurofly.synthetic_motor_target_dispatch import (
    ARTIFACT_SCHEMA_VERSION,
    CONFIG_SCHEMA_VERSION,
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_TARGET_CONTRACT_PATH,
    RESULT_SCHEMA_VERSION,
    SyntheticMotorTargetDispatchError,
    canonical_sha256,
    execute_reference_battery,
    validate_and_replay_payload,
)

CONFIG_FILENAME = "dispatch_config.json"
RESULT_FILENAME = "dispatch_result.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONFIG_FILENAME, RESULT_FILENAME, MANIFEST_FILENAME}


class SyntheticMotorTargetArtifactError(RuntimeError):
    """Invalid, tampered, or unreplayable Phase 8L artifact."""


def _json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
            + b"\n"
        )
    except (TypeError, ValueError) as exc:
        raise SyntheticMotorTargetArtifactError(
            "artifact data is not deterministic JSON"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _artifact_id(config_sha256: str, result_sha256: str) -> str:
    return _sha256_bytes(
        _json_bytes(
            {
                "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                "config_sha256": config_sha256,
                "result_sha256": result_sha256,
            }
        )
    )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise SyntheticMotorTargetArtifactError(f"malformed {label}") from None
    if not isinstance(value, dict) or _json_bytes(value) != raw:
        raise SyntheticMotorTargetArtifactError(f"{label} is not canonical JSON")
    return value


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise SyntheticMotorTargetArtifactError(f"could not write {path.name}") from exc


@dataclass(frozen=True, slots=True)
class LoadedSyntheticMotorTargetArtifact:
    path: Path
    artifact_id: str
    config: MappingProxyType
    result: MappingProxyType
    manifest: MappingProxyType

    def summary(self) -> dict[str, Any]:
        return {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "artifact_id": self.artifact_id,
            "artifact_path": str(self.path),
            "config_sha256": self.config["config_sha256"],
            "result_sha256": self.result["result_sha256"],
            "target_contract_id": self.result["target_contract_id"],
            "fixture_count": len(self.result["fixtures"]),
            "total_origin_events": self.result["summary"]["total_origin_events"],
            "total_dispatch_records": self.result["summary"]["total_dispatch_records"],
            "fixtures": [
                {
                    "fixture_id": row["fixture_id"],
                    "origin_event_count": row["summary"]["origin_event_count"],
                    "dispatch_record_count": row["summary"]["dispatch_record_count"],
                }
                for row in self.result["fixtures"]
            ],
            "artifact_bytes": sum(
                item.stat().st_size for item in self.path.iterdir() if item.is_file()
            ),
            "integrity_validation": "PASSED",
        }


def load_synthetic_motor_target_artifact(
    artifact_path: str | Path,
    *,
    allow_staging: bool = False,
    expected_artifact_id: str | None = None,
) -> LoadedSyntheticMotorTargetArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise SyntheticMotorTargetArtifactError("Phase 8L artifact not found")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise SyntheticMotorTargetArtifactError("unexpected Phase 8L file set")
    except OSError as exc:
        raise SyntheticMotorTargetArtifactError(
            "could not inspect Phase 8L artifact directory"
        ) from exc
    config = _read_json(path / CONFIG_FILENAME, "Phase 8L config")
    result = _read_json(path / RESULT_FILENAME, "Phase 8L result")
    manifest = _read_json(path / MANIFEST_FILENAME, "Phase 8L manifest")
    config_payload = {
        key: value for key, value in config.items() if key != "config_sha256"
    }
    result_payload = {
        key: value for key, value in result.items() if key != "result_sha256"
    }
    config_sha256 = canonical_sha256(config_payload)
    result_sha256 = canonical_sha256(result_payload)
    artifact_id = _artifact_id(config_sha256, result_sha256)
    if (
        config.get("schema_version") != CONFIG_SCHEMA_VERSION
        or result.get("schema_version") != RESULT_SCHEMA_VERSION
        or config.get("config_sha256") != config_sha256
        or result.get("result_sha256") != result_sha256
        or manifest.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
        or manifest.get("artifact_id") != artifact_id
        or manifest.get("config_sha256") != config_sha256
        or manifest.get("result_sha256") != result_sha256
        or (expected_artifact_id is not None and artifact_id != expected_artifact_id)
        or (path.name != artifact_id and not allow_staging)
        or set(manifest)
        != {
            "artifact_schema_version",
            "artifact_id",
            "config_sha256",
            "result_sha256",
            "files",
        }
    ):
        raise SyntheticMotorTargetArtifactError("Phase 8L artifact identity mismatch")
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != {CONFIG_FILENAME, RESULT_FILENAME}:
        raise SyntheticMotorTargetArtifactError("Phase 8L manifest file set mismatch")
    for filename, value, schema in (
        (CONFIG_FILENAME, config, CONFIG_SCHEMA_VERSION),
        (RESULT_FILENAME, result, RESULT_SCHEMA_VERSION),
    ):
        raw = (path / filename).read_bytes()
        record = files[filename]
        if (
            not isinstance(record, dict)
            or set(record) != {"schema", "bytes", "sha256"}
            or record.get("schema") != schema
            or record.get("bytes") != len(raw)
            or record.get("sha256") != _sha256_bytes(raw)
            or value.get("schema_version") != schema
        ):
            raise SyntheticMotorTargetArtifactError(
                f"Phase 8L {filename} manifest record mismatch"
            )
    return LoadedSyntheticMotorTargetArtifact(
        path=path,
        artifact_id=artifact_id,
        config=MappingProxyType(config),
        result=MappingProxyType(result),
        manifest=MappingProxyType(manifest),
    )


def export_synthetic_motor_target_artifact(
    config: dict[str, Any],
    result: dict[str, Any],
    destination: str | Path,
    *,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> LoadedSyntheticMotorTargetArtifact:
    try:
        validate_and_replay_payload(config, result, target_contract_path)
    except (SyntheticMotorTargetDispatchError, OSError, ValueError) as exc:
        raise SyntheticMotorTargetArtifactError(
            "Phase 8L payload failed source replay"
        ) from exc
    output = Path(destination)
    if output.exists():
        raise SyntheticMotorTargetArtifactError(
            f"Phase 8L artifact destination already exists: {output}"
        )
    config_bytes = _json_bytes(config)
    result_bytes = _json_bytes(result)
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    manifest = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "config_sha256": config["config_sha256"],
        "result_sha256": result["result_sha256"],
        "files": {
            CONFIG_FILENAME: {
                "schema": CONFIG_SCHEMA_VERSION,
                "bytes": len(config_bytes),
                "sha256": _sha256_bytes(config_bytes),
            },
            RESULT_FILENAME: {
                "schema": RESULT_SCHEMA_VERSION,
                "bytes": len(result_bytes),
                "sha256": _sha256_bytes(result_bytes),
            },
        },
    }
    manifest_bytes = _json_bytes(manifest)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{artifact_id}.", dir=output.parent))
    except OSError as exc:
        raise SyntheticMotorTargetArtifactError(
            "could not create Phase 8L staging directory"
        ) from exc
    try:
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, manifest_bytes)
        load_synthetic_motor_target_artifact(
            staging, allow_staging=True, expected_artifact_id=artifact_id
        )
        try:
            os.replace(staging, output)
        except OSError as exc:
            raise SyntheticMotorTargetArtifactError(
                "could not finalize Phase 8L artifact"
            ) from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return load_synthetic_motor_target_artifact(output)


def replay_synthetic_motor_target_artifact(
    artifact_path: str | Path,
    *,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> LoadedSyntheticMotorTargetArtifact:
    artifact = load_synthetic_motor_target_artifact(artifact_path)
    try:
        validate_and_replay_payload(
            dict(artifact.config), dict(artifact.result), target_contract_path
        )
    except (SyntheticMotorTargetDispatchError, OSError, ValueError) as exc:
        raise SyntheticMotorTargetArtifactError(
            "full offline Phase 8L replay failed"
        ) from exc
    return artifact


def generate_synthetic_motor_target_artifact(
    *,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
) -> LoadedSyntheticMotorTargetArtifact:
    try:
        config, result = execute_reference_battery(target_contract_path)
    except (SyntheticMotorTargetDispatchError, OSError, ValueError) as exc:
        raise SyntheticMotorTargetArtifactError(
            "could not build Phase 8L reference artifact"
        ) from exc
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    destination = Path(output_root) / artifact_id
    if destination.exists():
        return replay_synthetic_motor_target_artifact(
            destination, target_contract_path=target_contract_path
        )
    return export_synthetic_motor_target_artifact(
        config,
        result,
        destination,
        target_contract_path=target_contract_path,
    )


__all__ = [
    "DEFAULT_ARTIFACT_ROOT",
    "LoadedSyntheticMotorTargetArtifact",
    "SyntheticMotorTargetArtifactError",
    "export_synthetic_motor_target_artifact",
    "generate_synthetic_motor_target_artifact",
    "load_synthetic_motor_target_artifact",
    "replay_synthetic_motor_target_artifact",
]
