"""Content-addressed Phase 8S observation contract and offline replay."""

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

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import (
    ARTIFACT_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    TTMG1ObservationContractError,
    build_observation_contract,
    canonical_json_bytes,
    canonical_sha256,
    validate_contract_against_curated,
)

CONTRACT_FILENAME = "observation_contract.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONTRACT_FILENAME, MANIFEST_FILENAME}
DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA_VERSION


class TTMG1ObservationArtifactError(RuntimeError):
    """Malformed, tampered, or non-replayable Phase 8S artifact."""


def _artifact_id(config_sha256: str, result_sha256: str) -> str:
    return canonical_sha256(
        {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
            "config_sha256": config_sha256,
            "result_sha256": result_sha256,
        }
    )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise TTMG1ObservationArtifactError(f"malformed {label}") from None
    if not isinstance(value, dict) or canonical_json_bytes(value, newline=True) != raw:
        raise TTMG1ObservationArtifactError(f"{label} is not canonical JSON")
    return value


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise TTMG1ObservationArtifactError(f"could not write {path.name}") from exc


@dataclass(frozen=True, slots=True)
class LoadedTTMG1ObservationArtifact:
    path: Path
    artifact_id: str
    contract: MappingProxyType
    manifest: MappingProxyType

    def summary(self, *, include_observations: bool = False) -> dict[str, Any]:
        config = self.contract["config"]
        result = self.contract["result"]
        summary = {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "contract_schema_version": self.contract["schema_version"],
            "artifact_id": self.artifact_id,
            "contract_id": self.contract["contract_id"],
            "artifact_path": str(self.path),
            "config_sha256": self.contract["config_sha256"],
            "result_sha256": self.contract["result_sha256"],
            "observation_count": result["observation_count"],
            "evidence_sources": [
                source["evidence_id"]
                for source in config["evidence_manifest"]["sources"]
            ],
            "artifact_bytes": sum(
                item.stat().st_size for item in self.path.iterdir() if item.is_file()
            ),
            "integrity_validation": "PASSED",
        }
        if include_observations:
            summary["observations"] = result["observations"]
        return summary


def load_ttm_g1_observation_artifact(
    artifact_path: str | Path,
    *,
    allow_staging: bool = False,
    expected_artifact_id: str | None = None,
) -> LoadedTTMG1ObservationArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise TTMG1ObservationArtifactError("Phase 8S artifact not found")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise TTMG1ObservationArtifactError("unexpected Phase 8S artifact file set")
    except OSError as exc:
        raise TTMG1ObservationArtifactError(
            "could not inspect Phase 8S artifact"
        ) from exc
    contract = _read_json(path / CONTRACT_FILENAME, "Phase 8S contract")
    manifest = _read_json(path / MANIFEST_FILENAME, "Phase 8S manifest")
    config = contract.get("config")
    result = contract.get("result")
    if not isinstance(config, dict) or not isinstance(result, dict):
        raise TTMG1ObservationArtifactError("Phase 8S contract payload is malformed")
    config_hash = canonical_sha256(config)
    result_hash = canonical_sha256(result)
    artifact_id = _artifact_id(config_hash, result_hash)
    if (
        contract.get("schema_version") != CONTRACT_SCHEMA_VERSION
        or contract.get("config_sha256") != config_hash
        or contract.get("result_sha256") != result_hash
        or contract.get("contract_id") != artifact_id
        or manifest.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
        or manifest.get("artifact_id") != artifact_id
        or manifest.get("contract_id") != artifact_id
        or manifest.get("config_sha256") != config_hash
        or manifest.get("result_sha256") != result_hash
        or (expected_artifact_id is not None and artifact_id != expected_artifact_id)
        or (path.name != artifact_id and not allow_staging)
        or set(manifest)
        != {
            "artifact_schema_version",
            "artifact_id",
            "contract_id",
            "config_sha256",
            "result_sha256",
            "files",
        }
    ):
        raise TTMG1ObservationArtifactError("Phase 8S contract identity mismatch")
    file_records = manifest.get("files")
    if not isinstance(file_records, dict) or set(file_records) != {CONTRACT_FILENAME}:
        raise TTMG1ObservationArtifactError("Phase 8S manifest file set mismatch")
    contract_bytes = (path / CONTRACT_FILENAME).read_bytes()
    record = file_records[CONTRACT_FILENAME]
    if (
        not isinstance(record, dict)
        or set(record) != {"schema", "bytes", "sha256"}
        or record.get("schema") != CONTRACT_SCHEMA_VERSION
        or record.get("bytes") != len(contract_bytes)
        or record.get("sha256") != sha256(contract_bytes).hexdigest()
    ):
        raise TTMG1ObservationArtifactError("Phase 8S manifest file hash mismatch")
    return LoadedTTMG1ObservationArtifact(
        path=path,
        artifact_id=artifact_id,
        contract=MappingProxyType(contract),
        manifest=MappingProxyType(manifest),
    )


def validate_and_replay_contract(contract: dict[str, Any]) -> dict[str, Any]:
    try:
        return validate_contract_against_curated(contract)
    except (TTMG1ObservationContractError, TypeError, ValueError) as exc:
        raise TTMG1ObservationArtifactError(
            "Phase 8S contract differs from deterministic curated replay"
        ) from exc


def export_ttm_g1_observation_artifact(
    contract: dict[str, Any], destination: str | Path
) -> LoadedTTMG1ObservationArtifact:
    validate_and_replay_contract(contract)
    output = Path(destination)
    if output.exists():
        raise TTMG1ObservationArtifactError(
            f"Phase 8S artifact destination already exists: {output}"
        )
    contract_bytes = canonical_json_bytes(contract, newline=True)
    manifest = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": contract["contract_id"],
        "contract_id": contract["contract_id"],
        "config_sha256": contract["config_sha256"],
        "result_sha256": contract["result_sha256"],
        "files": {
            CONTRACT_FILENAME: {
                "schema": CONTRACT_SCHEMA_VERSION,
                "bytes": len(contract_bytes),
                "sha256": sha256(contract_bytes).hexdigest(),
            }
        },
    }
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{contract['contract_id']}.", dir=output.parent)
        )
    except OSError as exc:
        raise TTMG1ObservationArtifactError(
            "could not create Phase 8S staging directory"
        ) from exc
    try:
        _write(staging / CONTRACT_FILENAME, contract_bytes)
        _write(
            staging / MANIFEST_FILENAME, canonical_json_bytes(manifest, newline=True)
        )
        load_ttm_g1_observation_artifact(
            staging, allow_staging=True, expected_artifact_id=contract["contract_id"]
        )
        try:
            os.replace(staging, output)
        except OSError as exc:
            raise TTMG1ObservationArtifactError(
                "could not finalize Phase 8S artifact"
            ) from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return load_ttm_g1_observation_artifact(output)


def replay_ttm_g1_observation_artifact(
    artifact_path: str | Path,
) -> LoadedTTMG1ObservationArtifact:
    artifact = load_ttm_g1_observation_artifact(artifact_path)
    validate_and_replay_contract(dict(artifact.contract))
    return artifact


def generate_ttm_g1_observation_artifact(
    *, output_root: str | Path = DEFAULT_ARTIFACT_ROOT
) -> LoadedTTMG1ObservationArtifact:
    contract = build_observation_contract()
    destination = Path(output_root) / contract["contract_id"]
    if destination.exists():
        return replay_ttm_g1_observation_artifact(destination)
    return export_ttm_g1_observation_artifact(contract, destination)


__all__ = [
    "DEFAULT_ARTIFACT_ROOT",
    "LoadedTTMG1ObservationArtifact",
    "TTMG1ObservationArtifactError",
    "export_ttm_g1_observation_artifact",
    "generate_ttm_g1_observation_artifact",
    "load_ttm_g1_observation_artifact",
    "replay_ttm_g1_observation_artifact",
    "validate_and_replay_contract",
]
