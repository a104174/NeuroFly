"""Immutable offline Phase 7F transfer artifact and full-source replay."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurofly.malecns.contract import load_circuit_contract
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    canonical_json_bytes,
    sha256_bytes,
)
from neurofly.relative_column_dnp01_transfer import (
    CONFIG_SCHEMA,
    EXPECTED_SENSORY_ARTIFACT_ID,
    RESULT_SCHEMA,
    compute_transfer_result,
)
from neurofly.relative_column_sensory_artifacts import (
    DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    replay_relative_column_sensory_artifact,
)
from neurofly.relative_column_sensory_artifacts import (
    DEFAULT_OUTPUT_ROOT as SENSORY_OUTPUT_ROOT,
)

ARTIFACT_SCHEMA = "relative_column_sensory_to_dnp01_artifact_v1"
DEFAULT_SENSORY_ARTIFACT_PATH = SENSORY_OUTPUT_ROOT / EXPECTED_SENSORY_ARTIFACT_ID
DEFAULT_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / "relative_column_sensory_to_dnp01_v1"
CONFIG_FILENAME = "config.json"
RESULT_FILENAME = "transfer_result.json"
MANIFEST_FILENAME = "manifest.json"


class TransferArtifactError(ValueError):
    """Invalid or non-replayable Phase 7F artifact."""


@dataclass(frozen=True, slots=True)
class LoadedTransferArtifact:
    path: Path
    artifact_id: str
    config: dict[str, Any]
    result: dict[str, Any]
    manifest: dict[str, Any]

    def summary(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_schema": ARTIFACT_SCHEMA,
            "source_sensory_artifact_id": EXPECTED_SENSORY_ARTIFACT_ID,
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "conditions": [
                {
                    "condition_id": condition["condition_id"],
                    "k_transfer_mveq_per_state": condition["k_transfer_mveq_per_state"],
                    "pathway_mask": condition["pathway_mask"],
                    "targets": [
                        {
                            "body_id": target["body_id"],
                            "peak_drive_mveq": target["peak_drive_mveq"],
                            "peak_drive_step": target["peak_drive_step"],
                            "minimum_membrane_mv": target["minimum_membrane_mv"],
                            "maximum_membrane_mv": target["maximum_membrane_mv"],
                            "maximum_filtered_synaptic_mveq": target[
                                "maximum_filtered_synaptic_mveq"
                            ],
                            "simulated_spikes": target["simulated_spikes"],
                        }
                        for target in condition["targets"]
                    ],
                }
                for condition in self.result["conditions"]
            ],
        }


def artifact_id(config: dict[str, Any], result: dict[str, Any]) -> str:
    return sha256_bytes(
        canonical_json_bytes(
            {
                "schema": ARTIFACT_SCHEMA,
                "config_sha256": sha256_bytes(canonical_json_bytes(config) + b"\n"),
                "result_sha256": sha256_bytes(canonical_json_bytes(result) + b"\n"),
            }
        )
    )


def _payload(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        parsed = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (OSError, UnicodeError, ValueError):
        raise TransferArtifactError(
            f"malformed artifact payload: {path.name}"
        ) from None
    if not isinstance(parsed, dict) or raw != canonical_json_bytes(parsed) + b"\n":
        raise TransferArtifactError(f"noncanonical artifact payload: {path.name}")
    return parsed, raw


def load_artifact(path: str | Path) -> LoadedTransferArtifact:
    root = Path(path)
    if not root.is_dir() or {entry.name for entry in root.iterdir()} != {
        CONFIG_FILENAME,
        RESULT_FILENAME,
        MANIFEST_FILENAME,
    }:
        raise TransferArtifactError("Phase 7F artifact file set is invalid.")
    config, config_bytes = _payload(root / CONFIG_FILENAME)
    result, result_bytes = _payload(root / RESULT_FILENAME)
    manifest, _ = _payload(root / MANIFEST_FILENAME)
    if (
        set(manifest)
        != {
            "artifact_schema",
            "artifact_id",
            "config_sha256",
            "result_sha256",
            "source_sensory_artifact_id",
        }
        or manifest["artifact_schema"] != ARTIFACT_SCHEMA
        or manifest["source_sensory_artifact_id"] != EXPECTED_SENSORY_ARTIFACT_ID
        or manifest["config_sha256"] != sha256_bytes(config_bytes)
        or manifest["result_sha256"] != sha256_bytes(result_bytes)
        or manifest["artifact_id"] != artifact_id(config, result)
        or config.get("schema") != CONFIG_SCHEMA
        or result.get("schema") != RESULT_SCHEMA
        or config.get("source_sensory_artifact", {}).get("artifact_id")
        != EXPECTED_SENSORY_ARTIFACT_ID
        or result.get("source_sensory_artifact_id") != EXPECTED_SENSORY_ARTIFACT_ID
    ):
        raise TransferArtifactError("Phase 7F artifact integrity/identity mismatch.")
    return LoadedTransferArtifact(
        root, manifest["artifact_id"], config, result, manifest
    )


def export_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: str | Path
) -> LoadedTransferArtifact:
    destination = Path(destination)
    if destination.exists():
        raise TransferArtifactError(
            "Phase 7F artifact is immutable; destination exists."
        )
    config_bytes = canonical_json_bytes(config) + b"\n"
    result_bytes = canonical_json_bytes(result) + b"\n"
    manifest = {
        "artifact_schema": ARTIFACT_SCHEMA,
        "artifact_id": artifact_id(config, result),
        "config_sha256": sha256_bytes(config_bytes),
        "result_sha256": sha256_bytes(result_bytes),
        "source_sensory_artifact_id": EXPECTED_SENSORY_ARTIFACT_ID,
    }
    staging = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
        )
        for filename, payload in (
            (CONFIG_FILENAME, config_bytes),
            (RESULT_FILENAME, result_bytes),
            (MANIFEST_FILENAME, canonical_json_bytes(manifest) + b"\n"),
        ):
            with (staging / filename).open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        load_artifact(staging)
        if destination.exists():
            raise TransferArtifactError(
                "Phase 7F artifact is immutable; destination exists."
            )
        os.replace(staging, destination)
        staging = None
    finally:
        if staging is not None:
            shutil.rmtree(staging)
    return load_artifact(destination)


def make_artifact_payload(
    *,
    sensory_artifact_path: str | Path = DEFAULT_SENSORY_ARTIFACT_PATH,
    assignment_artifact_path: str | Path = DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Require full 7D→7E replay before running the independent 7F family."""

    source = replay_relative_column_sensory_artifact(
        sensory_artifact_path,
        assignment_artifact_path=assignment_artifact_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    contract = load_circuit_contract(Path(source_root))
    return compute_transfer_result(source, contract)


def replay_artifact(
    path: str | Path,
    *,
    sensory_artifact_path: str | Path = DEFAULT_SENSORY_ARTIFACT_PATH,
    assignment_artifact_path: str | Path = DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> LoadedTransferArtifact:
    artifact = load_artifact(path)
    config, result = make_artifact_payload(
        sensory_artifact_path=sensory_artifact_path,
        assignment_artifact_path=assignment_artifact_path,
        source_root=source_root,
        workbook_path=workbook_path,
    )
    if canonical_json_bytes(config) != canonical_json_bytes(
        artifact.config
    ) or canonical_json_bytes(result) != canonical_json_bytes(artifact.result):
        raise TransferArtifactError(
            "Phase 7F artifact differs from full-source replay."
        )
    return artifact
