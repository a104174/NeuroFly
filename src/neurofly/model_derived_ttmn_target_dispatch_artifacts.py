"""Immutable Phase 8O model-derived TTMn target-dispatch artifacts."""

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

from neurofly.model_derived_ttmn_target_dispatch import (
    ARTIFACT_SCHEMA_VERSION,
    CONFIG_SCHEMA_VERSION,
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_PHASE8N_ARTIFACT,
    DEFAULT_TARGET_CONTRACT_PATH,
    RESULT_SCHEMA_VERSION,
    ModelDerivedTTMnDispatchError,
    canonical_sha256,
    execute_reference_battery,
    validate_and_replay_payload,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_ttmn_output_rule import TTMnOutputRuleError
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    DEFAULT_SOURCE_ARTIFACT as DEFAULT_PHASE8B_SOURCE_ARTIFACT,
)
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    LoadedSyntheticTTMnOutputArtifact,
    SyntheticTTMnOutputArtifactError,
    replay_synthetic_ttmn_output_artifact,
)

CONFIG_FILENAME = "dispatch_config.json"
RESULT_FILENAME = "dispatch_result.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONFIG_FILENAME, RESULT_FILENAME, MANIFEST_FILENAME}


class ModelDerivedTTMnTargetArtifactError(RuntimeError):
    """Invalid, tampered, or unreplayable Phase 8O artifact."""


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
        raise ModelDerivedTTMnTargetArtifactError(
            "Phase 8O artifact is not deterministic JSON"
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
        raise ModelDerivedTTMnTargetArtifactError(f"malformed {label}") from None
    if not isinstance(value, dict) or _json_bytes(value) != raw:
        raise ModelDerivedTTMnTargetArtifactError(f"{label} is not canonical JSON")
    return value


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise ModelDerivedTTMnTargetArtifactError(
            f"could not write {path.name}"
        ) from exc


@dataclass(frozen=True, slots=True)
class LoadedModelDerivedTTMnTargetArtifact:
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
            "source_ttmn_output_artifact_id": self.result[
                "source_ttmn_output_artifact_id"
            ],
            "target_contract_id": self.result["target_contract_id"],
            "fixture_count": len(self.result["fixtures"]),
            "model_derived_output_event_count": self.result["summary"][
                "model_derived_output_event_count"
            ],
            "dispatch_record_count": self.result["summary"]["dispatch_record_count"],
            "per_body_event_counts": dict(
                self.result["summary"]["per_body_event_counts"]
            ),
            "fixtures": [
                {
                    "fixture_id": row["fixture_id"],
                    "model_derived_output_event_count": row["summary"][
                        "model_derived_output_event_count"
                    ],
                    "dispatch_record_count": row["summary"]["dispatch_record_count"],
                }
                for row in self.result["fixtures"]
            ],
            "artifact_bytes": sum(
                item.stat().st_size for item in self.path.iterdir() if item.is_file()
            ),
            "integrity_validation": "PASSED",
        }


def load_model_derived_ttmn_target_artifact(
    artifact_path: str | Path,
    *,
    allow_staging: bool = False,
    expected_artifact_id: str | None = None,
) -> LoadedModelDerivedTTMnTargetArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise ModelDerivedTTMnTargetArtifactError("Phase 8O artifact not found")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise ModelDerivedTTMnTargetArtifactError("unexpected Phase 8O file set")
    except OSError as exc:
        raise ModelDerivedTTMnTargetArtifactError(
            "could not inspect Phase 8O artifact directory"
        ) from exc
    config = _read_json(path / CONFIG_FILENAME, "Phase 8O config")
    result = _read_json(path / RESULT_FILENAME, "Phase 8O result")
    manifest = _read_json(path / MANIFEST_FILENAME, "Phase 8O manifest")
    config_hash = canonical_sha256(
        {key: value for key, value in config.items() if key != "config_sha256"}
    )
    result_hash = canonical_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"}
    )
    artifact_id = _artifact_id(config_hash, result_hash)
    if (
        config.get("schema_version") != CONFIG_SCHEMA_VERSION
        or result.get("schema_version") != RESULT_SCHEMA_VERSION
        or config.get("config_sha256") != config_hash
        or result.get("result_sha256") != result_hash
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
        raise ModelDerivedTTMnTargetArtifactError("Phase 8O artifact identity mismatch")
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != {CONFIG_FILENAME, RESULT_FILENAME}:
        raise ModelDerivedTTMnTargetArtifactError("Phase 8O manifest file set mismatch")
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
            raise ModelDerivedTTMnTargetArtifactError(
                f"Phase 8O {filename} manifest record mismatch"
            )
    return LoadedModelDerivedTTMnTargetArtifact(
        path=path,
        artifact_id=artifact_id,
        config=MappingProxyType(config),
        result=MappingProxyType(result),
        manifest=MappingProxyType(manifest),
    )


def _replay_phase8n(
    source_ttmn_artifact: str | Path,
    *,
    source_phase8b_artifact: str | Path | None,
    source_root: str | Path,
) -> LoadedSyntheticTTMnOutputArtifact:
    try:
        return replay_synthetic_ttmn_output_artifact(
            source_ttmn_artifact,
            source_artifact=source_phase8b_artifact,
            source_root=source_root,
        )
    except (
        OSError,
        ValueError,
        TTMnOutputRuleError,
        SyntheticTTMnOutputArtifactError,
    ) as exc:
        raise ModelDerivedTTMnTargetArtifactError(
            "Phase 8N source failed full offline replay"
        ) from exc


def export_model_derived_ttmn_target_artifact(
    config: dict[str, Any],
    result: dict[str, Any],
    destination: str | Path,
    *,
    source_artifact: LoadedSyntheticTTMnOutputArtifact,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> LoadedModelDerivedTTMnTargetArtifact:
    try:
        validate_and_replay_payload(
            config, result, source_artifact, target_contract_path
        )
    except (ModelDerivedTTMnDispatchError, OSError, ValueError) as exc:
        raise ModelDerivedTTMnTargetArtifactError(
            "Phase 8O payload failed 8N/8K source replay"
        ) from exc
    output = Path(destination)
    if output.exists():
        raise ModelDerivedTTMnTargetArtifactError(
            f"Phase 8O artifact destination already exists: {output}"
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
        raise ModelDerivedTTMnTargetArtifactError(
            "could not create Phase 8O staging directory"
        ) from exc
    try:
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, manifest_bytes)
        load_model_derived_ttmn_target_artifact(
            staging, allow_staging=True, expected_artifact_id=artifact_id
        )
        try:
            os.replace(staging, output)
        except OSError as exc:
            raise ModelDerivedTTMnTargetArtifactError(
                "could not finalize Phase 8O artifact"
            ) from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return load_model_derived_ttmn_target_artifact(output)


def replay_model_derived_ttmn_target_artifact(
    artifact_path: str | Path,
    *,
    source_ttmn_artifact: str | Path = DEFAULT_PHASE8N_ARTIFACT,
    source_phase8b_artifact: str | Path = DEFAULT_PHASE8B_SOURCE_ARTIFACT,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> LoadedModelDerivedTTMnTargetArtifact:
    artifact = load_model_derived_ttmn_target_artifact(artifact_path)
    source = _replay_phase8n(
        source_ttmn_artifact,
        source_phase8b_artifact=source_phase8b_artifact,
        source_root=source_root,
    )
    try:
        validate_and_replay_payload(
            dict(artifact.config),
            dict(artifact.result),
            source,
            target_contract_path,
        )
    except (ModelDerivedTTMnDispatchError, OSError, ValueError) as exc:
        raise ModelDerivedTTMnTargetArtifactError(
            "full offline Phase 8O replay failed"
        ) from exc
    return artifact


def generate_model_derived_ttmn_target_artifact(
    *,
    source_ttmn_artifact: str | Path = DEFAULT_PHASE8N_ARTIFACT,
    source_phase8b_artifact: str | Path = DEFAULT_PHASE8B_SOURCE_ARTIFACT,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
) -> LoadedModelDerivedTTMnTargetArtifact:
    source = _replay_phase8n(
        source_ttmn_artifact,
        source_phase8b_artifact=source_phase8b_artifact,
        source_root=source_root,
    )
    try:
        config, result = execute_reference_battery(source, target_contract_path)
    except (ModelDerivedTTMnDispatchError, OSError, ValueError) as exc:
        raise ModelDerivedTTMnTargetArtifactError(
            "could not construct Phase 8O reference artifact"
        ) from exc
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    destination = Path(output_root) / artifact_id
    if destination.exists():
        return replay_model_derived_ttmn_target_artifact(
            destination,
            source_ttmn_artifact=source_ttmn_artifact,
            source_phase8b_artifact=source_phase8b_artifact,
            source_root=source_root,
            target_contract_path=target_contract_path,
        )
    return export_model_derived_ttmn_target_artifact(
        config,
        result,
        destination,
        source_artifact=source,
        target_contract_path=target_contract_path,
    )


__all__ = [
    "DEFAULT_ARTIFACT_ROOT",
    "DEFAULT_PHASE8N_ARTIFACT",
    "LoadedModelDerivedTTMnTargetArtifact",
    "ModelDerivedTTMnTargetArtifactError",
    "export_model_derived_ttmn_target_artifact",
    "generate_model_derived_ttmn_target_artifact",
    "load_model_derived_ttmn_target_artifact",
    "replay_model_derived_ttmn_target_artifact",
]
