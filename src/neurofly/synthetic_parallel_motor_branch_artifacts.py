"""Immutable content-addressed Phase 8I parallel-branch artifacts."""

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
from neurofly.psi_dlmn_event_relay import (
    DEFAULT_MOTOR_CONTRACT_PATH,
    load_pinned_motor_contract,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_parallel_motor_branches import (
    ARTIFACT_SCHEMA_VERSION,
    COMPOSITION_SCHEMA_VERSION,
    EXPECTED_MOTOR_CONTRACT_ID,
    RESULT_SCHEMA_VERSION,
    ParallelMotorCompositionError,
    canonical_sha256,
    execute_parallel_motor_branches,
    validate_and_replay_payload,
)

DEFAULT_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / "synthetic_parallel_motor_branch_v1"
CONFIG_FILENAME = "composition_config.json"
RESULT_FILENAME = "composition_result.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONFIG_FILENAME, RESULT_FILENAME, MANIFEST_FILENAME}


class SyntheticParallelMotorArtifactError(RuntimeError):
    """Invalid, tampered, or unreplayable Phase 8I artifact."""


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
        raise SyntheticParallelMotorArtifactError(
            "artifact data is not deterministic JSON"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _artifact_id(config_sha256: str, result_sha256: str) -> str:
    identity = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "config_sha256": config_sha256,
        "result_sha256": result_sha256,
    }
    return _sha256_bytes(_json_bytes(identity))


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise SyntheticParallelMotorArtifactError(f"malformed {label}") from None
    if not isinstance(value, dict) or _json_bytes(value) != raw:
        raise SyntheticParallelMotorArtifactError(f"{label} is not canonical JSON")
    return value


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise SyntheticParallelMotorArtifactError(
            f"could not write {path.name}"
        ) from exc


@dataclass(frozen=True, slots=True)
class LoadedSyntheticParallelMotorArtifact:
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
            "source_kind": self.result["input_source_kind"],
            "motor_contract_id": self.result["motor_contract_id"],
            "fixture_count": len(self.result["fixtures"]),
            "summary": dict(self.result["summary"]),
            "fixtures": [
                {
                    "fixture_id": fixture["fixture_id"],
                    "origin_event_count": len(fixture["origin_events"]),
                    "ttmn_input_event_count": len(
                        fixture["ttmn_branch"]["mapped_motor_inputs"]
                    ),
                    "psi_receipt_count": len(
                        fixture["psi_dlmn_branch"]["psi_routed_events"]
                    ),
                    "dlmn_path_receipt_count": len(
                        fixture["psi_dlmn_branch"]["dlmn_routed_events"]
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
) -> LoadedSyntheticParallelMotorArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise SyntheticParallelMotorArtifactError("Phase 8I artifact not found")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise SyntheticParallelMotorArtifactError(
                "unexpected Phase 8I artifact file set"
            )
    except OSError as exc:
        raise SyntheticParallelMotorArtifactError(
            "could not inspect Phase 8I artifact directory"
        ) from exc
    config = _read_json(path / CONFIG_FILENAME, "Phase 8I configuration")
    result = _read_json(path / RESULT_FILENAME, "Phase 8I result")
    manifest = _read_json(path / MANIFEST_FILENAME, "Phase 8I manifest")
    if set(manifest) != {
        "artifact_schema_version",
        "artifact_id",
        "config_sha256",
        "result_sha256",
        "files",
    }:
        raise SyntheticParallelMotorArtifactError("invalid Phase 8I manifest fields")
    if (
        manifest.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
        or not isinstance(manifest.get("files"), dict)
        or set(manifest.get("files", {})) != {CONFIG_FILENAME, RESULT_FILENAME}
    ):
        raise SyntheticParallelMotorArtifactError("unsupported Phase 8I schema")
    for filename, value, schema in (
        (CONFIG_FILENAME, config, config.get("schema_version")),
        (RESULT_FILENAME, result, RESULT_SCHEMA_VERSION),
    ):
        payload = _json_bytes(value)
        record = manifest["files"].get(filename)
        if (
            not isinstance(record, dict)
            or set(record) != {"schema", "bytes", "sha256"}
            or record.get("schema") != schema
            or record.get("bytes") != len(payload)
            or record.get("sha256") != _sha256_bytes(payload)
            or (path / filename).stat().st_size != len(payload)
        ):
            raise SyntheticParallelMotorArtifactError(f"{filename} integrity mismatch")
    config_hash = config.get("config_sha256")
    result_hash = result.get("result_sha256")
    if (
        config.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
        or config.get("schema_version") != COMPOSITION_SCHEMA_VERSION
        or result.get("schema_version") != RESULT_SCHEMA_VERSION
        or result.get("config_sha256") != config_hash
        or manifest.get("config_sha256") != config_hash
        or manifest.get("result_sha256") != result_hash
        or not isinstance(config_hash, str)
        or not isinstance(result_hash, str)
    ):
        raise SyntheticParallelMotorArtifactError("Phase 8I payload schema mismatch")
    if config_hash != canonical_sha256(
        {key: value for key, value in config.items() if key != "config_sha256"}
    ) or result_hash != canonical_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"}
    ):
        raise SyntheticParallelMotorArtifactError("Phase 8I payload hash mismatch")
    artifact_id = _artifact_id(config_hash, result_hash)
    if (
        manifest.get("artifact_id") != artifact_id
        or (expected_artifact_id is not None and artifact_id != expected_artifact_id)
        or (path.name != artifact_id and not allow_staging)
    ):
        raise SyntheticParallelMotorArtifactError("Phase 8I artifact identity mismatch")
    return LoadedSyntheticParallelMotorArtifact(
        path=path,
        artifact_id=artifact_id,
        config=MappingProxyType(config),
        result=MappingProxyType(result),
        manifest=MappingProxyType(manifest),
    )


def load_synthetic_parallel_motor_artifact(
    artifact_path: str | Path,
) -> LoadedSyntheticParallelMotorArtifact:
    """Validate canonical artifact bytes and content-addressed identity."""

    return _read_artifact(artifact_path)


def export_synthetic_parallel_motor_artifact(
    config: dict[str, Any],
    result: dict[str, Any],
    destination: str | Path,
    *,
    circuit_contract: Any,
    pinned_motor_contract: dict[str, Any],
) -> LoadedSyntheticParallelMotorArtifact:
    """Persist a deterministic composition after full child/source replay."""

    try:
        validate_and_replay_payload(
            config, result, circuit_contract, pinned_motor_contract
        )
    except (ParallelMotorCompositionError, ValueError) as exc:
        raise SyntheticParallelMotorArtifactError(
            "Phase 8I payload failed deterministic replay"
        ) from exc
    output = Path(destination)
    if output.exists():
        raise SyntheticParallelMotorArtifactError(
            f"Phase 8I destination already exists: {output}"
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
        raise SyntheticParallelMotorArtifactError(
            "could not create Phase 8I staging directory"
        ) from exc
    try:
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, manifest_bytes)
        _read_artifact(staging, allow_staging=True, expected_artifact_id=artifact_id)
        try:
            os.replace(staging, output)
        except OSError as exc:
            raise SyntheticParallelMotorArtifactError(
                "could not finalize Phase 8I artifact"
            ) from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return _read_artifact(output)


def replay_synthetic_parallel_motor_artifact(
    artifact_path: str | Path,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    motor_contract_path: str | Path = DEFAULT_MOTOR_CONTRACT_PATH,
) -> LoadedSyntheticParallelMotorArtifact:
    """Replay both branches from local pinned sources without network access."""

    artifact = _read_artifact(artifact_path)
    try:
        circuit_contract = load_circuit_contract(Path(source_root))
        pinned_motor_contract = load_pinned_motor_contract(motor_contract_path)
        validate_and_replay_payload(
            dict(artifact.config),
            dict(artifact.result),
            circuit_contract,
            pinned_motor_contract,
        )
    except (OSError, ValueError, ParallelMotorCompositionError) as exc:
        raise SyntheticParallelMotorArtifactError(
            "full Phase 8I replay failed"
        ) from exc
    if (
        pinned_motor_contract["manifest"].get("artifact_id")
        != EXPECTED_MOTOR_CONTRACT_ID
    ):
        raise SyntheticParallelMotorArtifactError("motor contract identity mismatch")
    return artifact


def generate_synthetic_parallel_motor_artifact(
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    motor_contract_path: str | Path = DEFAULT_MOTOR_CONTRACT_PATH,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> LoadedSyntheticParallelMotorArtifact:
    """Generate or replay the fixed six-fixture Phase 8I composition."""

    try:
        circuit_contract = load_circuit_contract(Path(source_root))
        pinned_motor_contract = load_pinned_motor_contract(motor_contract_path)
        config, result = execute_parallel_motor_branches(
            circuit_contract, pinned_motor_contract
        )
    except (OSError, ValueError, ParallelMotorCompositionError) as exc:
        raise SyntheticParallelMotorArtifactError(
            "could not construct Phase 8I composition"
        ) from exc
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    destination = Path(output_root) / artifact_id
    if destination.exists():
        return replay_synthetic_parallel_motor_artifact(
            destination,
            source_root=source_root,
            motor_contract_path=motor_contract_path,
        )
    return export_synthetic_parallel_motor_artifact(
        config,
        result,
        destination,
        circuit_contract=circuit_contract,
        pinned_motor_contract=pinned_motor_contract,
    )


__all__ = [
    "CONFIG_FILENAME",
    "DEFAULT_OUTPUT_ROOT",
    "LoadedSyntheticParallelMotorArtifact",
    "MANIFEST_FILENAME",
    "RESULT_FILENAME",
    "SyntheticParallelMotorArtifactError",
    "export_synthetic_parallel_motor_artifact",
    "generate_synthetic_parallel_motor_artifact",
    "load_synthetic_parallel_motor_artifact",
    "replay_synthetic_parallel_motor_artifact",
]
