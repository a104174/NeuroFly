"""Immutable admission-token artifact with full offline Phase 8Q source replay."""

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
from neurofly.ttm_abstract_electrical_input import (
    ARTIFACT_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    DEFAULT_SOURCE_ARTIFACT,
    build_input_contract,
    validate_input_contract,
)
from neurofly.ttm_g1_electrophysiology_observations import canonical_json_bytes

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA_VERSION
CONTRACT_FILENAME = "input_contract.json"
MANIFEST_FILENAME = "manifest.json"


class TTMAbstractInputArtifactError(ValueError):
    """Malformed or unreplayable abstract electrical-input artifact."""


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
        raise TTMAbstractInputArtifactError(f"malformed {path.name}") from exc


def _manifest(contract: dict, raw: bytes) -> dict:
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": contract["contract_id"],
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


@dataclass(frozen=True, slots=True)
class LoadedTTMAbstractInputArtifact:
    path: Path
    contract: MappingProxyType
    manifest: MappingProxyType

    @property
    def artifact_id(self) -> str:
        return self.contract["contract_id"]

    def summary(self, *, include_tokens: bool = False) -> dict:
        output = {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
            "artifact_id": self.artifact_id,
            "artifact_path": str(self.path),
            "config_sha256": self.contract["config_sha256"],
            "result_sha256": self.contract["result_sha256"],
            "source_phase8q": self.contract["config"]["source_phase8q"],
            **self.contract["result"]["summary"],
            "fixtures": [
                {"fixture_id": row["fixture_id"], "token_count": len(row["tokens"])}
                for row in self.contract["result"]["fixtures"]
            ],
            "scientific_boundary": self.contract["config"]["scientific_boundary"],
            "artifact_bytes": sum(item.stat().st_size for item in self.path.iterdir()),
            "integrity_validation": "PASSED",
        }
        if include_tokens:
            output["tokens"] = [
                token
                for fixture in self.contract["result"]["fixtures"]
                for token in fixture["tokens"]
            ]
        return output


def load_abstract_input_artifact(
    artifact_path: str | Path,
    *,
    source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT,
    allow_staging: bool = False,
) -> LoadedTTMAbstractInputArtifact:
    path = Path(artifact_path)
    if not path.is_dir() or {row.name for row in path.iterdir()} != {
        CONTRACT_FILENAME,
        MANIFEST_FILENAME,
    }:
        raise TTMAbstractInputArtifactError("unexpected abstract input file set")
    contract, manifest = (
        _read(path / CONTRACT_FILENAME),
        _read(path / MANIFEST_FILENAME),
    )
    validate_input_contract(contract, source_artifact=source_artifact)
    if manifest != _manifest(
        contract, canonical_json_bytes(contract, newline=True)
    ) or (not allow_staging and path.name != contract["contract_id"]):
        raise TTMAbstractInputArtifactError(
            "input artifact identity or file hash mismatch"
        )
    return LoadedTTMAbstractInputArtifact(
        path, MappingProxyType(contract), MappingProxyType(manifest)
    )


def export_abstract_input_artifact(
    contract: dict,
    destination: str | Path,
    *,
    source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT,
) -> LoadedTTMAbstractInputArtifact:
    contract = validate_input_contract(contract, source_artifact=source_artifact)
    output = Path(destination)
    if output.exists():
        raise TTMAbstractInputArtifactError("input artifact destination already exists")
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
        load_abstract_input_artifact(
            staging, source_artifact=source_artifact, allow_staging=True
        )
        os.replace(staging, output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return load_abstract_input_artifact(output, source_artifact=source_artifact)


def generate_abstract_input_artifact(
    *,
    source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
) -> LoadedTTMAbstractInputArtifact:
    contract = build_input_contract(source_artifact=source_artifact)
    destination = Path(output_root) / contract["contract_id"]
    if destination.exists():
        return load_abstract_input_artifact(
            destination, source_artifact=source_artifact
        )
    return export_abstract_input_artifact(
        contract, destination, source_artifact=source_artifact
    )


def replay_abstract_input_artifact(
    artifact_path: str | Path, *, source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT
) -> LoadedTTMAbstractInputArtifact:
    return load_abstract_input_artifact(artifact_path, source_artifact=source_artifact)
