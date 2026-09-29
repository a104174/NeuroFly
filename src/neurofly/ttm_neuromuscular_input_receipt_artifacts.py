"""Immutable Phase 8Q TTM NMJ-input receipt artifacts and offline replay."""

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

from neurofly.model_derived_ttmn_target_dispatch import DEFAULT_TARGET_CONTRACT_PATH
from neurofly.model_derived_ttmn_target_dispatch_artifacts import (
    DEFAULT_PHASE8B_SOURCE_ARTIFACT,
    DEFAULT_PHASE8N_ARTIFACT,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_neuromuscular_input_receipt import (
    ARTIFACT_SCHEMA_VERSION,
    CONFIG_SCHEMA_VERSION,
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_PHASE8O_ARTIFACT,
    RESULT_SCHEMA_VERSION,
    TTMNeuromuscularInputReceiptError,
    canonical_sha256,
    execute_reference_battery,
    replay_source_dispatch_artifact,
)

CONFIG_FILENAME = "receipt_config.json"
RESULT_FILENAME = "receipt_result.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONFIG_FILENAME, RESULT_FILENAME, MANIFEST_FILENAME}


class TTMNeuromuscularInputReceiptArtifactError(RuntimeError):
    """Invalid, tampered, or unreplayable Phase 8Q artifact."""


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
        raise TTMNeuromuscularInputReceiptArtifactError(
            "Phase 8Q artifact is not deterministic JSON"
        ) from exc


def _artifact_id(config_sha256: str, result_sha256: str) -> str:
    payload = _json_bytes(
        {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "config_sha256": config_sha256,
            "result_sha256": result_sha256,
        }
    )
    return sha256(payload).hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise TTMNeuromuscularInputReceiptArtifactError(f"malformed {label}") from None
    if not isinstance(value, dict) or _json_bytes(value) != raw:
        raise TTMNeuromuscularInputReceiptArtifactError(
            f"{label} is not canonical JSON"
        )
    return value


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise TTMNeuromuscularInputReceiptArtifactError(
            f"could not write {path.name}"
        ) from exc


@dataclass(frozen=True, slots=True)
class LoadedTTMNeuromuscularInputReceiptArtifact:
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
            "source_phase8o_artifact_id": self.result["source_phase8o_artifact_id"],
            "target_contract_id": self.result["target_contract_id"],
            "fixture_count": self.result["summary"]["fixture_count"],
            "parent_dispatch_count": self.result["summary"]["parent_dispatch_count"],
            "receipt_count": self.result["summary"]["receipt_count"],
            "per_body_receipt_counts": dict(
                self.result["summary"]["per_body_receipt_counts"]
            ),
            "fixtures": [
                {
                    "fixture_id": row["fixture_id"],
                    "dispatch_count": row["summary"]["dispatch_count"],
                    "receipt_count": row["summary"]["receipt_count"],
                }
                for row in self.result["fixtures"]
            ],
            "artifact_bytes": sum(
                item.stat().st_size for item in self.path.iterdir() if item.is_file()
            ),
            "integrity_validation": "PASSED",
        }


def load_ttm_neuromuscular_input_receipt_artifact(
    artifact_path: str | Path,
    *,
    allow_staging: bool = False,
    expected_artifact_id: str | None = None,
) -> LoadedTTMNeuromuscularInputReceiptArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise TTMNeuromuscularInputReceiptArtifactError("Phase 8Q artifact not found")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise TTMNeuromuscularInputReceiptArtifactError(
                "unexpected Phase 8Q file set"
            )
    except OSError as exc:
        raise TTMNeuromuscularInputReceiptArtifactError(
            "could not inspect Phase 8Q artifact directory"
        ) from exc
    config = _read_json(path / CONFIG_FILENAME, "Phase 8Q config")
    result = _read_json(path / RESULT_FILENAME, "Phase 8Q result")
    manifest = _read_json(path / MANIFEST_FILENAME, "Phase 8Q manifest")
    config_hash = canonical_sha256(
        {key: value for key, value in config.items() if key != "config_sha256"}
    )
    result_hash = canonical_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"}
    )
    artifact_id = _artifact_id(config_hash, result_hash)
    if (
        config.get("schema_version") != CONFIG_SCHEMA_VERSION
        or config.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
        or result.get("schema_version") != RESULT_SCHEMA_VERSION
        or config.get("config_sha256") != config_hash
        or result.get("result_sha256") != result_hash
        or result.get("config_sha256") != config_hash
        or manifest.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
        or manifest.get("artifact_id") != artifact_id
        or manifest.get("config_sha256") != config_hash
        or manifest.get("result_sha256") != result_hash
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
        raise TTMNeuromuscularInputReceiptArtifactError(
            "Phase 8Q artifact identity mismatch"
        )
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != {CONFIG_FILENAME, RESULT_FILENAME}:
        raise TTMNeuromuscularInputReceiptArtifactError(
            "Phase 8Q manifest file set mismatch"
        )
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
            or record.get("sha256") != sha256(raw).hexdigest()
            or value.get("schema_version") != schema
        ):
            raise TTMNeuromuscularInputReceiptArtifactError(
                f"Phase 8Q {filename} manifest record mismatch"
            )
    return LoadedTTMNeuromuscularInputReceiptArtifact(
        path=path,
        artifact_id=artifact_id,
        config=MappingProxyType(config),
        result=MappingProxyType(result),
        manifest=MappingProxyType(manifest),
    )


def validate_and_replay_payload(
    config: dict[str, Any],
    result: dict[str, Any],
    source_phase8o_artifact: str | Path = DEFAULT_PHASE8O_ARTIFACT,
    *,
    source_ttmn_artifact: str | Path = DEFAULT_PHASE8N_ARTIFACT,
    source_phase8b_artifact: str | Path = DEFAULT_PHASE8B_SOURCE_ARTIFACT,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        source = replay_source_dispatch_artifact(
            source_phase8o_artifact,
            source_ttmn_artifact=source_ttmn_artifact,
            source_phase8b_artifact=source_phase8b_artifact,
            source_root=source_root,
            target_contract_path=target_contract_path,
        )
        expected_config, expected_result = execute_reference_battery(
            source, target_contract_path
        )
    except (OSError, ValueError, TTMNeuromuscularInputReceiptError) as exc:
        raise TTMNeuromuscularInputReceiptArtifactError(
            "Phase 8Q source replay or receipt validation failed"
        ) from exc
    if config != expected_config or result != expected_result:
        raise TTMNeuromuscularInputReceiptArtifactError(
            "Phase 8Q artifact differs from replayed Phase 8O receipts"
        )
    return expected_config, expected_result


def export_ttm_neuromuscular_input_receipt_artifact(
    config: dict[str, Any],
    result: dict[str, Any],
    destination: str | Path,
    *,
    source_phase8o_artifact: str | Path = DEFAULT_PHASE8O_ARTIFACT,
    source_ttmn_artifact: str | Path = DEFAULT_PHASE8N_ARTIFACT,
    source_phase8b_artifact: str | Path = DEFAULT_PHASE8B_SOURCE_ARTIFACT,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> LoadedTTMNeuromuscularInputReceiptArtifact:
    validate_and_replay_payload(
        config,
        result,
        source_phase8o_artifact,
        source_ttmn_artifact=source_ttmn_artifact,
        source_phase8b_artifact=source_phase8b_artifact,
        source_root=source_root,
        target_contract_path=target_contract_path,
    )
    output = Path(destination)
    if output.exists():
        raise TTMNeuromuscularInputReceiptArtifactError(
            f"Phase 8Q artifact destination already exists: {output}"
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
                "sha256": sha256(config_bytes).hexdigest(),
            },
            RESULT_FILENAME: {
                "schema": RESULT_SCHEMA_VERSION,
                "bytes": len(result_bytes),
                "sha256": sha256(result_bytes).hexdigest(),
            },
        },
    }
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{artifact_id}.", dir=output.parent))
    except OSError as exc:
        raise TTMNeuromuscularInputReceiptArtifactError(
            "could not create Phase 8Q staging directory"
        ) from exc
    try:
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, _json_bytes(manifest))
        load_ttm_neuromuscular_input_receipt_artifact(
            staging, allow_staging=True, expected_artifact_id=artifact_id
        )
        try:
            os.replace(staging, output)
        except OSError as exc:
            raise TTMNeuromuscularInputReceiptArtifactError(
                "could not finalize Phase 8Q artifact"
            ) from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return load_ttm_neuromuscular_input_receipt_artifact(output)


def replay_ttm_neuromuscular_input_receipt_artifact(
    artifact_path: str | Path,
    *,
    source_phase8o_artifact: str | Path = DEFAULT_PHASE8O_ARTIFACT,
    source_ttmn_artifact: str | Path = DEFAULT_PHASE8N_ARTIFACT,
    source_phase8b_artifact: str | Path = DEFAULT_PHASE8B_SOURCE_ARTIFACT,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> LoadedTTMNeuromuscularInputReceiptArtifact:
    artifact = load_ttm_neuromuscular_input_receipt_artifact(artifact_path)
    validate_and_replay_payload(
        dict(artifact.config),
        dict(artifact.result),
        source_phase8o_artifact,
        source_ttmn_artifact=source_ttmn_artifact,
        source_phase8b_artifact=source_phase8b_artifact,
        source_root=source_root,
        target_contract_path=target_contract_path,
    )
    return artifact


def generate_ttm_neuromuscular_input_receipt_artifact(
    *,
    source_phase8o_artifact: str | Path = DEFAULT_PHASE8O_ARTIFACT,
    source_ttmn_artifact: str | Path = DEFAULT_PHASE8N_ARTIFACT,
    source_phase8b_artifact: str | Path = DEFAULT_PHASE8B_SOURCE_ARTIFACT,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
) -> LoadedTTMNeuromuscularInputReceiptArtifact:
    try:
        source = replay_source_dispatch_artifact(
            source_phase8o_artifact,
            source_ttmn_artifact=source_ttmn_artifact,
            source_phase8b_artifact=source_phase8b_artifact,
            source_root=source_root,
            target_contract_path=target_contract_path,
        )
        config, result = execute_reference_battery(source, target_contract_path)
    except (OSError, ValueError, TTMNeuromuscularInputReceiptError) as exc:
        raise TTMNeuromuscularInputReceiptArtifactError(
            "could not construct Phase 8Q reference artifact"
        ) from exc
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    destination = Path(output_root) / artifact_id
    if destination.exists():
        return replay_ttm_neuromuscular_input_receipt_artifact(
            destination,
            source_phase8o_artifact=source_phase8o_artifact,
            source_ttmn_artifact=source_ttmn_artifact,
            source_phase8b_artifact=source_phase8b_artifact,
            source_root=source_root,
            target_contract_path=target_contract_path,
        )
    return export_ttm_neuromuscular_input_receipt_artifact(
        config,
        result,
        destination,
        source_phase8o_artifact=source_phase8o_artifact,
        source_ttmn_artifact=source_ttmn_artifact,
        source_phase8b_artifact=source_phase8b_artifact,
        source_root=source_root,
        target_contract_path=target_contract_path,
    )


__all__ = [
    "DEFAULT_ARTIFACT_ROOT",
    "DEFAULT_PHASE8O_ARTIFACT",
    "LoadedTTMNeuromuscularInputReceiptArtifact",
    "TTMNeuromuscularInputReceiptArtifactError",
    "export_ttm_neuromuscular_input_receipt_artifact",
    "generate_ttm_neuromuscular_input_receipt_artifact",
    "load_ttm_neuromuscular_input_receipt_artifact",
    "replay_ttm_neuromuscular_input_receipt_artifact",
]
