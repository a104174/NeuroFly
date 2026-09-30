"""Immutable Phase 8Y metadata artifacts, with full offline source replay."""

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
from neurofly.ttm_g1_proxy_mapping import (
    ARTIFACT_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    build_proxy_contract,
    validate_proxy_contract,
)

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA_VERSION
CONTRACT_FILENAME = "proxy_contract.json"
MANIFEST_FILENAME = "manifest.json"


class TTMG1ProxyArtifactError(ValueError):
    """Malformed, noncanonical or non-replayable proxy artifact."""


def _read(path: Path) -> dict:
    try:
        raw = path.read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or raw != canonical_json_bytes(
            payload, newline=True
        ):
            raise ValueError("noncanonical JSON")
        return payload
    except (OSError, UnicodeError, ValueError) as exc:
        raise TTMG1ProxyArtifactError(f"malformed {path.name}") from exc


def _manifest(contract: dict) -> dict:
    raw = canonical_json_bytes(contract, newline=True)
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
class LoadedTTMG1ProxyArtifact:
    path: Path
    contract: MappingProxyType
    manifest: MappingProxyType

    @property
    def artifact_id(self) -> str:
        return self.contract["contract_id"]

    def summary(self, *, include_mappings: bool = False) -> dict:
        output = {
            key: self.contract[key]
            for key in ("contract_id", "config_sha256", "result_sha256")
        }
        output.update(
            artifact_id=self.artifact_id,
            artifact_schema_version=ARTIFACT_SCHEMA_VERSION,
            contract_schema_version=CONTRACT_SCHEMA_VERSION,
            artifact_path=str(self.path),
            artifact_bytes=sum(item.stat().st_size for item in self.path.iterdir()),
            proxy_domain_count=self.contract["result"]["proxy_domain_count"],
            source_mapping_count=self.contract["result"]["source_mapping_count"],
            scientific_boundary=self.contract["config"]["scientific_boundary"],
            source_contracts=self.contract["config"]["sources"],
            integrity_validation="PASSED",
        )
        if include_mappings:
            output.update(
                proxy_domains=self.contract["result"]["proxy_domains"],
                source_mappings=self.contract["result"]["source_mappings"],
                evidence_manifest=self.contract["config"]["evidence_manifest"],
            )
        return output


def replay_proxy_artifact(
    artifact_path: str | Path,
    *,
    source_paths: dict[str, Path] | None = None,
    allow_staging: bool = False,
) -> LoadedTTMG1ProxyArtifact:
    path = Path(artifact_path)
    if not path.is_dir() or {item.name for item in path.iterdir()} != {
        CONTRACT_FILENAME,
        MANIFEST_FILENAME,
    }:
        raise TTMG1ProxyArtifactError("unexpected proxy artifact file set")
    contract, manifest = (
        _read(path / CONTRACT_FILENAME),
        _read(path / MANIFEST_FILENAME),
    )
    validate_proxy_contract(contract, source_paths=source_paths)
    if manifest != _manifest(contract) or (
        not allow_staging and path.name != contract["contract_id"]
    ):
        raise TTMG1ProxyArtifactError("proxy artifact identity or file hash mismatch")
    return LoadedTTMG1ProxyArtifact(
        path, MappingProxyType(contract), MappingProxyType(manifest)
    )


def export_proxy_artifact(
    contract: dict,
    destination: str | Path,
    *,
    source_paths: dict[str, Path] | None = None,
) -> LoadedTTMG1ProxyArtifact:
    contract = validate_proxy_contract(contract, source_paths=source_paths)
    output = Path(destination)
    if output.exists():
        raise TTMG1ProxyArtifactError("proxy destination already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{contract['contract_id']}.", dir=output.parent)
    )
    try:
        for name, payload in (
            (CONTRACT_FILENAME, contract),
            (MANIFEST_FILENAME, _manifest(contract)),
        ):
            with (staging / name).open("xb") as stream:
                stream.write(canonical_json_bytes(payload, newline=True))
                stream.flush()
                os.fsync(stream.fileno())
        replay_proxy_artifact(staging, source_paths=source_paths, allow_staging=True)
        os.replace(staging, output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return replay_proxy_artifact(output, source_paths=source_paths)


def generate_proxy_artifact(
    *,
    source_paths: dict[str, Path] | None = None,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
) -> LoadedTTMG1ProxyArtifact:
    contract = build_proxy_contract(source_paths=source_paths)
    destination = Path(output_root) / contract["contract_id"]
    if destination.exists():
        return replay_proxy_artifact(destination, source_paths=source_paths)
    return export_proxy_artifact(contract, destination, source_paths=source_paths)
