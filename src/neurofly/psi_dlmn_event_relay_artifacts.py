"""Immutable Phase 8G routed-event artifacts and offline replay."""

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

from neurofly.psi_dlmn_event_relay import (
    ARTIFACT_SCHEMA_VERSION,
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_MOTOR_CONTRACT_PATH,
    PsiDlmnEventRelayError,
    execute_reference_relay,
    load_pinned_motor_contract,
    validate_and_replay_payload,
)

CONFIG_FILENAME = "relay_config.json"
RESULT_FILENAME = "relay_result.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONFIG_FILENAME, RESULT_FILENAME, MANIFEST_FILENAME}


class PsiDlmnEventRelayArtifactError(RuntimeError):
    """Invalid, tampered, or unreplayable Phase 8G artifact."""


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
        raise PsiDlmnEventRelayArtifactError(
            "artifact data is not deterministic JSON"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise PsiDlmnEventRelayArtifactError(f"malformed {label}") from None
    if not isinstance(value, dict) or _json_bytes(value) != raw:
        raise PsiDlmnEventRelayArtifactError(f"{label} is not canonical JSON")
    return value


def _artifact_id(config_sha256: str, result_sha256: str) -> str:
    identity = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "config_sha256": config_sha256,
        "result_sha256": result_sha256,
    }
    return _sha256_bytes(_json_bytes(identity))


def psi_dlmn_event_relay_artifact_id(config_sha256: str, result_sha256: str) -> str:
    """Return the unchanged content identity for a Phase 8G child payload."""

    return _artifact_id(config_sha256, result_sha256)


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise PsiDlmnEventRelayArtifactError(f"could not write {path.name}") from exc


@dataclass(frozen=True, slots=True)
class LoadedPsiDlmnEventRelayArtifact:
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
            "motor_contract_id": self.result["motor_contract_id"],
            "source_kind": self.result["source_kind"],
            "event_semantics": self.result["event_semantics"],
            "fixture_count": self.result["summary"]["fixture_count"],
            "fixtures": [
                {
                    "fixture_id": fixture["fixture_id"],
                    "source_events": fixture["counts"]["source_events"],
                    "psi_routed_events": fixture["counts"]["psi_routed_events"],
                    "dlmn_routed_events": fixture["counts"]["dlmn_routed_events"],
                    "psi_targets": sorted(
                        {
                            row["target_psi_body_id"]
                            for row in fixture["psi_routed_events"]
                        }
                    ),
                    "dlmn_targets": sorted(
                        {
                            row["target_dlmn_body_id"]
                            for row in fixture["dlmn_routed_events"]
                        }
                    ),
                }
                for fixture in self.result["fixtures"]
            ],
            "artifact_bytes": sum(
                item.stat().st_size for item in self.path.iterdir() if item.is_file()
            ),
            "integrity_validation": "PASSED",
        }


def _read_artifact(
    artifact_path: str | Path,
    *,
    allow_staging: bool = False,
    expected_artifact_id: str | None = None,
) -> LoadedPsiDlmnEventRelayArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise PsiDlmnEventRelayArtifactError("Phase 8G artifact not found")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise PsiDlmnEventRelayArtifactError(
                "unexpected Phase 8G artifact file set"
            )
    except OSError as exc:
        raise PsiDlmnEventRelayArtifactError(
            "could not inspect artifact directory"
        ) from exc
    manifest = _read_json(path / MANIFEST_FILENAME, "artifact manifest")
    config = _read_json(path / CONFIG_FILENAME, "relay configuration")
    result = _read_json(path / RESULT_FILENAME, "relay result")
    if set(manifest) != {
        "artifact_schema_version",
        "artifact_id",
        "config_sha256",
        "result_sha256",
        "files",
    }:
        raise PsiDlmnEventRelayArtifactError("invalid artifact manifest fields")
    if manifest.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION or set(
        manifest.get("files", {})
    ) != {CONFIG_FILENAME, RESULT_FILENAME}:
        raise PsiDlmnEventRelayArtifactError("unsupported Phase 8G artifact schema")
    for filename, value in ((CONFIG_FILENAME, config), (RESULT_FILENAME, result)):
        payload = _json_bytes(value)
        record = manifest["files"][filename]
        if set(record) != {"schema", "bytes", "sha256"}:
            raise PsiDlmnEventRelayArtifactError(f"invalid {filename} manifest record")
        if (
            record.get("bytes") != len(payload)
            or record.get("sha256") != _sha256_bytes(payload)
            or (path / filename).stat().st_size != len(payload)
        ):
            raise PsiDlmnEventRelayArtifactError(f"{filename} integrity mismatch")
        expected_schema = (
            config.get("schema_version")
            if filename == CONFIG_FILENAME
            else result.get("schema_version")
        )
        if record.get("schema") != expected_schema:
            raise PsiDlmnEventRelayArtifactError(f"{filename} schema mismatch")
    config_hash = config.get("config_sha256")
    result_hash = result.get("result_sha256")
    expected_id = _artifact_id(config_hash, result_hash)
    if (
        manifest.get("config_sha256") != config_hash
        or manifest.get("result_sha256") != result_hash
        or manifest.get("artifact_id") != expected_id
        or (expected_artifact_id is not None and expected_id != expected_artifact_id)
        or (path.name != expected_id and not allow_staging)
    ):
        raise PsiDlmnEventRelayArtifactError("artifact content identity mismatch")
    return LoadedPsiDlmnEventRelayArtifact(
        path=path,
        artifact_id=expected_id,
        config=MappingProxyType(config),
        result=MappingProxyType(result),
        manifest=MappingProxyType(manifest),
    )


def export_psi_dlmn_event_relay_artifact(
    config: dict[str, Any],
    result: dict[str, Any],
    destination: str | Path,
    *,
    pinned_motor_contract: dict[str, Any],
) -> LoadedPsiDlmnEventRelayArtifact:
    """Write a content-addressed artifact atomically without overwriting data."""

    try:
        validate_and_replay_payload(config, result, pinned_motor_contract)
    except PsiDlmnEventRelayError as exc:
        raise PsiDlmnEventRelayArtifactError("Phase 8G payload failed replay") from exc
    config_bytes = _json_bytes(config)
    result_bytes = _json_bytes(result)
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    output = Path(destination)
    if output.exists():
        raise PsiDlmnEventRelayArtifactError(
            f"artifact destination already exists: {output}"
        )
    manifest = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "config_sha256": config["config_sha256"],
        "result_sha256": result["result_sha256"],
        "files": {
            CONFIG_FILENAME: {
                "schema": config["schema_version"],
                "bytes": len(config_bytes),
                "sha256": _sha256_bytes(config_bytes),
            },
            RESULT_FILENAME: {
                "schema": result["schema_version"],
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
        raise PsiDlmnEventRelayArtifactError(
            "could not create artifact staging area"
        ) from exc
    try:
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, manifest_bytes)
        _read_artifact(staging, allow_staging=True, expected_artifact_id=artifact_id)
        try:
            os.replace(staging, output)
        except OSError as exc:
            raise PsiDlmnEventRelayArtifactError("could not finalize artifact") from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return _read_artifact(output)


def load_psi_dlmn_event_relay_artifact(
    artifact_path: str | Path,
) -> LoadedPsiDlmnEventRelayArtifact:
    """Validate canonical artifact bytes, hashes and content-addressed identity."""

    return _read_artifact(artifact_path)


def replay_psi_dlmn_event_relay_artifact(
    artifact_path: str | Path,
    *,
    motor_contract_path: str | Path = DEFAULT_MOTOR_CONTRACT_PATH,
) -> LoadedPsiDlmnEventRelayArtifact:
    """Replay against the pinned Phase 8E contract; performs no network access."""

    artifact = _read_artifact(artifact_path)
    try:
        pinned = load_pinned_motor_contract(motor_contract_path)
        validate_and_replay_payload(
            dict(artifact.config), dict(artifact.result), pinned
        )
    except (OSError, ValueError, PsiDlmnEventRelayError) as exc:
        raise PsiDlmnEventRelayArtifactError("full Phase 8G replay failed") from exc
    return artifact


def generate_psi_dlmn_event_relay_artifact(
    *,
    motor_contract_path: str | Path = DEFAULT_MOTOR_CONTRACT_PATH,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
) -> LoadedPsiDlmnEventRelayArtifact:
    """Generate or replay the fixed six-fixture Phase 8G event relay."""

    pinned = load_pinned_motor_contract(motor_contract_path)
    config, result = execute_reference_relay(pinned)
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    destination = Path(output_root) / artifact_id
    if destination.exists():
        return replay_psi_dlmn_event_relay_artifact(
            destination, motor_contract_path=motor_contract_path
        )
    return export_psi_dlmn_event_relay_artifact(
        config,
        result,
        destination,
        pinned_motor_contract=pinned,
    )


__all__ = [
    "DEFAULT_ARTIFACT_ROOT",
    "LoadedPsiDlmnEventRelayArtifact",
    "PsiDlmnEventRelayArtifactError",
    "export_psi_dlmn_event_relay_artifact",
    "generate_psi_dlmn_event_relay_artifact",
    "load_psi_dlmn_event_relay_artifact",
    "replay_psi_dlmn_event_relay_artifact",
    "psi_dlmn_event_relay_artifact_id",
]
