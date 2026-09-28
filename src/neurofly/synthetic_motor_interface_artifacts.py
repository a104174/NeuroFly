"""Immutable artifacts for the synthetic DNp01-to-TTMn interface test."""

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

from neurofly.malecns.contract import load_circuit_contract
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_motor_interface import (
    ARTIFACT_SCHEMA_VERSION,
    RESULT_SCHEMA_VERSION,
    SyntheticMotorInterfaceError,
    execute_reference_battery,
    replay_synthetic_fixture_configuration,
    validate_and_replay_payload,
)

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / "synthetic_dnp01_ttmn_interface_v1"
CONFIG_FILENAME = "fixture_config.json"
RESULT_FILENAME = "fixture_result.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONFIG_FILENAME, RESULT_FILENAME, MANIFEST_FILENAME}


class SyntheticMotorArtifactError(RuntimeError):
    """Invalid, tampered, or unreplayable synthetic motor artifact."""


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
        raise SyntheticMotorArtifactError(
            "artifact data is not deterministic JSON"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise SyntheticMotorArtifactError(f"malformed {label}") from None
    if not isinstance(value, dict) or _json_bytes(value) != raw:
        raise SyntheticMotorArtifactError(f"{label} is not canonical JSON")
    return value


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


def synthetic_motor_artifact_id(config_sha256: str, result_sha256: str) -> str:
    """Return the unchanged content identity for a Phase 8B child payload."""

    return _artifact_id(config_sha256, result_sha256)


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise SyntheticMotorArtifactError(f"could not write {path.name}") from exc


@dataclass(frozen=True, slots=True)
class LoadedSyntheticMotorArtifact:
    path: Path
    artifact_id: str
    config: MappingProxyType
    result: MappingProxyType
    manifest: MappingProxyType

    def summary(self) -> dict[str, Any]:
        fixtures = self.result["fixtures"]
        return {
            "artifact_id": self.artifact_id,
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "config_sha256": self.config["config_sha256"],
            "result_sha256": self.result["result_sha256"],
            "source_kind": self.result["source_kind"],
            "sensory_source_artifact_id": self.result["sensory_source_artifact_id"],
            "fixture_count": len(fixtures),
            "fixtures": [
                {
                    "fixture_id": fixture["fixture_id"],
                    "events": fixture["source_events"],
                    "ttmn": [
                        {
                            "body_id": item["body_id"],
                            "side": item["side"],
                            "input_event_count": item["input_event_count"],
                            "peak_state": item["peak_state"],
                            "peak_step": item["peak_step"],
                            "peak_time_ms": item["peak_time_ms"],
                            "final_state": item["state"][-1],
                        }
                        for item in fixture["ttmn_model_state"]
                    ],
                }
                for fixture in fixtures
            ],
            "artifact_bytes": sum(
                item.stat().st_size for item in self.path.iterdir() if item.is_file()
            ),
            "artifact_path": str(self.path),
            "integrity_validation": "PASSED",
        }


def export_synthetic_motor_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedSyntheticMotorArtifact:
    """Persist a canonical immutable fixture artifact atomically."""

    try:
        validate_and_replay_payload(config, result)
    except SyntheticMotorInterfaceError as exc:
        raise SyntheticMotorArtifactError("fixture payload failed validation") from exc
    output = Path(destination)
    if output.exists():
        raise SyntheticMotorArtifactError(
            f"synthetic motor artifact output already exists: {output}"
        )
    config_bytes = _json_bytes(config)
    result_bytes = _json_bytes(result)
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    manifest = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "source_kind": "SYNTHETIC_MOTOR_INTERFACE_TEST",
        "files": {
            CONFIG_FILENAME: {
                "schema": config["schema_version"],
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
        staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    except OSError as exc:
        raise SyntheticMotorArtifactError(
            "could not create artifact staging area"
        ) from exc
    try:
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, manifest_bytes)
        load_synthetic_motor_artifact(staging, _allow_staging=True)
        try:
            os.replace(staging, output)
        except OSError as exc:
            raise SyntheticMotorArtifactError("could not finalize artifact") from exc
        return load_synthetic_motor_artifact(output)
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def load_synthetic_motor_artifact(
    artifact_path: str | Path,
    *,
    _allow_staging: bool = False,
) -> LoadedSyntheticMotorArtifact:
    """Verify canonical bytes, hashes, identity, and the deterministic model."""

    path = Path(artifact_path)
    if not path.is_dir():
        raise SyntheticMotorArtifactError("synthetic motor artifact not found")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise SyntheticMotorArtifactError("unexpected artifact file set")
    except OSError as exc:
        raise SyntheticMotorArtifactError(
            "could not inspect artifact directory"
        ) from exc
    manifest = _read_json(path / MANIFEST_FILENAME, "artifact manifest")
    config = _read_json(path / CONFIG_FILENAME, "fixture config")
    result = _read_json(path / RESULT_FILENAME, "fixture result")
    if set(manifest) != {
        "artifact_schema_version",
        "artifact_id",
        "source_kind",
        "files",
    }:
        raise SyntheticMotorArtifactError("invalid artifact manifest fields")
    if (
        manifest["artifact_schema_version"] != ARTIFACT_SCHEMA_VERSION
        or manifest["source_kind"] != "SYNTHETIC_MOTOR_INTERFACE_TEST"
        or set(manifest["files"]) != {CONFIG_FILENAME, RESULT_FILENAME}
    ):
        raise SyntheticMotorArtifactError("unsupported synthetic artifact schema")
    for filename, payload in (
        (CONFIG_FILENAME, _json_bytes(config)),
        (RESULT_FILENAME, _json_bytes(result)),
    ):
        record = manifest["files"][filename]
        if set(record) != {"schema", "bytes", "sha256"}:
            raise SyntheticMotorArtifactError(f"invalid {filename} manifest record")
        actual = path / filename
        if (
            record.get("bytes") != len(payload)
            or record.get("sha256") != _sha256_bytes(payload)
            or actual.stat().st_size != len(payload)
        ):
            raise SyntheticMotorArtifactError(f"{filename} integrity mismatch")
    if manifest["files"][CONFIG_FILENAME].get("schema") != config.get(
        "schema_version"
    ) or manifest["files"][RESULT_FILENAME].get("schema") != result.get(
        "schema_version"
    ):
        raise SyntheticMotorArtifactError("artifact file schema mismatch")
    try:
        validate_and_replay_payload(config, result)
    except SyntheticMotorInterfaceError as exc:
        raise SyntheticMotorArtifactError(
            "stored fixture failed deterministic replay"
        ) from exc
    expected_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    if manifest["artifact_id"] != expected_id:
        raise SyntheticMotorArtifactError("manifest artifact identity mismatch")
    if path.name != expected_id and not _allow_staging:
        raise SyntheticMotorArtifactError("artifact identity mismatch")
    return LoadedSyntheticMotorArtifact(
        path=path,
        artifact_id=expected_id,
        config=MappingProxyType(config),
        result=MappingProxyType(result),
        manifest=MappingProxyType(manifest),
    )


def replay_synthetic_motor_artifact(
    artifact_path: str | Path,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
) -> LoadedSyntheticMotorArtifact:
    """Replay against local pinned MaleCNS sources; performs no network access."""

    artifact = load_synthetic_motor_artifact(artifact_path)
    try:
        circuit = load_circuit_contract(Path(source_root))
        replay_synthetic_fixture_configuration(dict(artifact.config), circuit)
        config, result = execute_reference_battery(circuit)
    except (OSError, ValueError) as exc:
        raise SyntheticMotorArtifactError(
            "full synthetic artifact replay failed"
        ) from exc
    if config != dict(artifact.config) or result != dict(artifact.result):
        raise SyntheticMotorArtifactError("full replay identity differs")
    return artifact


def generate_synthetic_motor_artifact(
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
) -> LoadedSyntheticMotorArtifact:
    """Generate the fixed synthetic fixture battery after source validation."""

    circuit = load_circuit_contract(Path(source_root))
    config, result = execute_reference_battery(circuit)
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    destination = Path(output_root) / artifact_id
    if destination.exists():
        return replay_synthetic_motor_artifact(destination, source_root=source_root)
    return export_synthetic_motor_artifact(config, result, destination)


__all__ = [
    "DEFAULT_ARTIFACT_ROOT",
    "LoadedSyntheticMotorArtifact",
    "SyntheticMotorArtifactError",
    "export_synthetic_motor_artifact",
    "generate_synthetic_motor_artifact",
    "load_synthetic_motor_artifact",
    "replay_synthetic_motor_artifact",
    "synthetic_motor_artifact_id",
]
