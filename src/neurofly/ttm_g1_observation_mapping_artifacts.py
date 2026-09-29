"""Immutable Phase 8U mapping artifacts with offline Phase 8S replay."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes
from neurofly.ttm_g1_observation_mapping import (
    ARTIFACT_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    DEFAULT_SOURCE_ARTIFACT,
    build_mapping_contract,
    validate_mapping_contract,
    validated_source,
)

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA_VERSION
CONTRACT_FILENAME = "mapping_contract.json"
MANIFEST_FILENAME = "manifest.json"


class TTMG1MappingArtifactError(ValueError):
    """Malformed or non-replayable observation-mapping artifact."""


def _read(path: Path) -> dict:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
        if not isinstance(value, dict) or raw != canonical_json_bytes(
            value, newline=True
        ):
            raise ValueError("noncanonical JSON")
        return value
    except (OSError, UnicodeError, ValueError) as exc:
        raise TTMG1MappingArtifactError(f"malformed {path.name}") from exc


@dataclass(frozen=True, slots=True)
class LoadedTTMG1MappingArtifact:
    path: Path
    contract: MappingProxyType
    manifest: MappingProxyType

    @property
    def artifact_id(self) -> str:
        return self.contract["contract_id"]

    def summary(
        self,
        *,
        include_mappings: bool = False,
        source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT,
    ) -> dict:
        summary = {
            key: self.contract[key]
            for key in ("contract_id", "config_sha256", "result_sha256")
        }
        summary.update(
            {
                "artifact_id": self.artifact_id,
                "contract_schema_version": CONTRACT_SCHEMA_VERSION,
                "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                "artifact_path": str(self.path),
                "artifact_bytes": sum(
                    item.stat().st_size for item in self.path.iterdir()
                ),
                "source_contract_id": self.contract["config"][
                    "source_observation_contract"
                ]["contract_id"],
                "mapping_count": self.contract["result"]["mapping_count"],
                "formal_ready_mapping_count": 0,
                "readiness_snapshot": self.contract["config"]["readiness_snapshot"],
                "integrity_validation": "PASSED",
            }
        )
        if include_mappings:
            observations = {
                row["observation_id"]: row
                for row in validated_source(source_artifact)["result"]["observations"]
            }
            summary["mappings"] = [
                {
                    **row,
                    "source_quantity_label": observations[row["observation_id"]][
                        "quantity"
                    ],
                    "source_protocol": observations[row["observation_id"]]["protocol"],
                }
                for row in self.contract["result"]["mappings"]
            ]
        return summary


def _manifest(contract: dict, raw: bytes) -> dict:
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": contract["contract_id"],
        "contract_id": contract["contract_id"],
        "config_sha256": contract["config_sha256"],
        "result_sha256": contract["result_sha256"],
        "files": {
            CONTRACT_FILENAME: {
                "schema": CONTRACT_SCHEMA_VERSION,
                "bytes": len(raw),
                "sha256": sha256(raw).hexdigest(),
            }
        },
    }


def load_ttm_g1_mapping_artifact(
    artifact_path: str | Path,
    *,
    source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT,
    allow_staging: bool = False,
) -> LoadedTTMG1MappingArtifact:
    path = Path(artifact_path)
    if not path.is_dir() or {item.name for item in path.iterdir()} != {
        CONTRACT_FILENAME,
        MANIFEST_FILENAME,
    }:
        raise TTMG1MappingArtifactError("unexpected mapping artifact file set")
    contract, manifest = (
        _read(path / CONTRACT_FILENAME),
        _read(path / MANIFEST_FILENAME),
    )
    validate_mapping_contract(contract, source_artifact=source_artifact)
    if manifest != _manifest(
        contract, canonical_json_bytes(contract, newline=True)
    ) or (not allow_staging and path.name != contract["contract_id"]):
        raise TTMG1MappingArtifactError(
            "mapping artifact identity or file hash mismatch"
        )
    return LoadedTTMG1MappingArtifact(
        path, MappingProxyType(contract), MappingProxyType(manifest)
    )


def export_ttm_g1_mapping_artifact(
    contract: dict,
    destination: str | Path,
    *,
    source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT,
) -> LoadedTTMG1MappingArtifact:
    contract = validate_mapping_contract(contract, source_artifact=source_artifact)
    output = Path(destination)
    if output.exists():
        raise TTMG1MappingArtifactError("mapping artifact destination already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{contract['contract_id']}.", dir=output.parent)
    )
    raw = canonical_json_bytes(contract, newline=True)
    try:
        for name, payload in (
            (CONTRACT_FILENAME, raw),
            (
                MANIFEST_FILENAME,
                canonical_json_bytes(_manifest(contract, raw), newline=True),
            ),
        ):
            with (staging / name).open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        load_ttm_g1_mapping_artifact(
            staging, source_artifact=source_artifact, allow_staging=True
        )
        os.replace(staging, output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return load_ttm_g1_mapping_artifact(output, source_artifact=source_artifact)


def replay_ttm_g1_mapping_artifact(
    artifact_path: str | Path, *, source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT
) -> LoadedTTMG1MappingArtifact:
    return load_ttm_g1_mapping_artifact(artifact_path, source_artifact=source_artifact)


def generate_ttm_g1_mapping_artifact(
    *,
    source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
) -> LoadedTTMG1MappingArtifact:
    contract = build_mapping_contract(source_artifact=source_artifact)
    destination = Path(output_root) / contract["contract_id"]
    if destination.exists():
        return replay_ttm_g1_mapping_artifact(
            destination, source_artifact=source_artifact
        )
    return export_ttm_g1_mapping_artifact(
        contract, destination, source_artifact=source_artifact
    )
