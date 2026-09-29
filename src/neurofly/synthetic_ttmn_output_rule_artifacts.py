"""Immutable Phase 8N output-rule artifacts and deterministic source replay."""

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
from neurofly.synthetic_motor_interface_artifacts import (
    DEFAULT_ARTIFACT_ROOT as DEFAULT_PHASE8B_ARTIFACT_ROOT,
)
from neurofly.synthetic_motor_interface_artifacts import (
    LoadedSyntheticMotorArtifact,
    SyntheticMotorArtifactError,
    generate_synthetic_motor_artifact,
    replay_synthetic_motor_artifact,
)
from neurofly.synthetic_ttmn_output_rule import (
    ARTIFACT_SCHEMA_VERSION,
    RESULT_SCHEMA_VERSION,
    TTMnOutputRuleError,
    canonical_sha256,
    execute_output_rule,
    validate_and_replay_payload,
)

DEFAULT_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / "synthetic_ttmn_output_rule_v1"
DEFAULT_SOURCE_ARTIFACT = (
    DEFAULT_PHASE8B_ARTIFACT_ROOT
    / "4321adeee0412a79632ce4e008a1b8eaad22ee167f97f4a98521a9e71d9ef936"
)
CONFIG_FILENAME = "generator_config.json"
RESULT_FILENAME = "output_result.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONFIG_FILENAME, RESULT_FILENAME, MANIFEST_FILENAME}


class SyntheticTTMnOutputArtifactError(RuntimeError):
    """Invalid, tampered, or unreplayable Phase 8N artifact."""


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
        raise SyntheticTTMnOutputArtifactError(
            "artifact data is not deterministic JSON"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


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
        raise SyntheticTTMnOutputArtifactError(f"malformed {label}") from None
    if not isinstance(value, dict) or _json_bytes(value) != raw:
        raise SyntheticTTMnOutputArtifactError(f"{label} is not canonical JSON")
    return value


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise SyntheticTTMnOutputArtifactError(f"could not write {path.name}") from exc


@dataclass(frozen=True, slots=True)
class LoadedSyntheticTTMnOutputArtifact:
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
            "source_artifact_id": self.result["source_artifact_id"],
            "reference_threshold_dimensionless": self.result["summary"][
                "reference_threshold_dimensionless"
            ],
            "fixture_count": len(self.result["fixtures"]),
            "reference_output_event_count": self.result["summary"][
                "reference_output_event_count"
            ],
            "sensitivity_output_event_counts": dict(
                self.result["summary"]["sensitivity_output_event_counts"]
            ),
            "fixtures": [
                {
                    "fixture_id": fixture["fixture_id"],
                    "reference_events": [
                        {
                            "event_id": event["event_id"],
                            "body_id": event["motor_neuron_body_id"],
                            "side": event["neural_side"],
                            "step": event["step"],
                            "time_ms": event["time_ms"],
                        }
                        for event in fixture["reference_output_events"]
                    ],
                    "sensitivity_event_counts": {
                        str(item["threshold_dimensionless"]): len(item["output_events"])
                        for item in fixture["sensitivity"]
                    },
                }
                for fixture in self.result["fixtures"]
            ],
            "artifact_bytes": sum(
                item.stat().st_size for item in self.path.iterdir() if item.is_file()
            ),
            "integrity_validation": "PASSED",
        }


def _read_artifact(
    artifact_path: str | Path, *, allow_staging: bool = False
) -> LoadedSyntheticTTMnOutputArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise SyntheticTTMnOutputArtifactError("Phase 8N artifact not found")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise SyntheticTTMnOutputArtifactError("unexpected Phase 8N artifact files")
    except OSError as exc:
        raise SyntheticTTMnOutputArtifactError(
            "could not inspect Phase 8N artifact"
        ) from exc
    config = _read_json(path / CONFIG_FILENAME, "Phase 8N config")
    result = _read_json(path / RESULT_FILENAME, "Phase 8N result")
    manifest = _read_json(path / MANIFEST_FILENAME, "Phase 8N manifest")
    if set(manifest) != {
        "artifact_schema_version",
        "artifact_id",
        "config_sha256",
        "result_sha256",
        "files",
    }:
        raise SyntheticTTMnOutputArtifactError("invalid Phase 8N manifest fields")
    if (
        manifest.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
        or not isinstance(manifest.get("files"), dict)
        or set(manifest["files"]) != {CONFIG_FILENAME, RESULT_FILENAME}
    ):
        raise SyntheticTTMnOutputArtifactError("unsupported Phase 8N artifact schema")
    for filename, value in ((CONFIG_FILENAME, config), (RESULT_FILENAME, result)):
        payload = _json_bytes(value)
        record = manifest["files"].get(filename)
        if (
            not isinstance(record, dict)
            or set(record) != {"schema", "bytes", "sha256"}
            or record.get("schema") != value.get("schema_version")
            or record.get("bytes") != len(payload)
            or record.get("sha256") != _sha256_bytes(payload)
            or (path / filename).stat().st_size != len(payload)
        ):
            raise SyntheticTTMnOutputArtifactError(f"{filename} integrity mismatch")
    config_hash = config.get("config_sha256")
    result_hash = result.get("result_sha256")
    if (
        config.get("schema_version") != "synthetic_ttmn_output_rule_config_v1"
        or config.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
        or result.get("schema_version") != RESULT_SCHEMA_VERSION
        or result.get("artifact_schema_version") != ARTIFACT_SCHEMA_VERSION
        or result.get("config_sha256") != config_hash
        or manifest.get("config_sha256") != config_hash
        or manifest.get("result_sha256") != result_hash
        or not isinstance(config_hash, str)
        or not isinstance(result_hash, str)
        or config_hash
        != canonical_sha256(
            {key: value for key, value in config.items() if key != "config_sha256"}
        )
        or result_hash
        != canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
    ):
        raise SyntheticTTMnOutputArtifactError("Phase 8N payload hash/schema mismatch")
    artifact_id = _artifact_id(config_hash, result_hash)
    if manifest.get("artifact_id") != artifact_id or (
        path.name != artifact_id and not allow_staging
    ):
        raise SyntheticTTMnOutputArtifactError("Phase 8N artifact identity mismatch")
    return LoadedSyntheticTTMnOutputArtifact(
        path=path,
        artifact_id=artifact_id,
        config=MappingProxyType(config),
        result=MappingProxyType(result),
        manifest=MappingProxyType(manifest),
    )


def load_synthetic_ttmn_output_artifact(
    artifact_path: str | Path,
) -> LoadedSyntheticTTMnOutputArtifact:
    """Check canonical artifact bytes and content-addressed hashes."""

    return _read_artifact(artifact_path)


def export_synthetic_ttmn_output_artifact(
    config: dict[str, Any],
    result: dict[str, Any],
    destination: str | Path,
    *,
    source_artifact: LoadedSyntheticMotorArtifact,
) -> LoadedSyntheticTTMnOutputArtifact:
    """Persist a source-replayed Phase 8N payload atomically."""

    try:
        validate_and_replay_payload(config, result, source_artifact)
    except (TTMnOutputRuleError, ValueError) as exc:
        raise SyntheticTTMnOutputArtifactError(
            "Phase 8N payload failed source replay"
        ) from exc
    output = Path(destination)
    if output.exists():
        raise SyntheticTTMnOutputArtifactError(f"Phase 8N destination exists: {output}")
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
        raise SyntheticTTMnOutputArtifactError(
            "could not create Phase 8N staging"
        ) from exc
    try:
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, manifest_bytes)
        _read_artifact(staging, allow_staging=True)
        os.replace(staging, output)
    except OSError as exc:
        raise SyntheticTTMnOutputArtifactError(
            "could not finalize Phase 8N artifact"
        ) from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return _read_artifact(output)


def _source_path(
    source_artifact: str | Path | None,
    source_root: str | Path,
) -> Path:
    if source_artifact is not None:
        return Path(source_artifact)
    root = Path(source_root)
    if root == DEFAULT_SOURCE_ROOT:
        return DEFAULT_SOURCE_ARTIFACT
    return root / DEFAULT_PHASE8B_ARTIFACT_ROOT.name / DEFAULT_SOURCE_ARTIFACT.name


def _load_or_reconstruct_phase8b(
    artifact_path: str | Path,
    *,
    source_root: str | Path,
) -> LoadedSyntheticMotorArtifact:
    path = Path(artifact_path)
    if path.exists():
        return replay_synthetic_motor_artifact(path, source_root=source_root)
    generated = generate_synthetic_motor_artifact(
        source_root=source_root,
        output_root=path.parent,
    )
    if generated.path != path:
        raise SyntheticTTMnOutputArtifactError(
            "missing Phase 8B source path is not its deterministic artifact identity"
        )
    return replay_synthetic_motor_artifact(generated.path, source_root=source_root)


def replay_synthetic_ttmn_output_artifact(
    artifact_path: str | Path,
    *,
    source_artifact: str | Path | None = None,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
) -> LoadedSyntheticTTMnOutputArtifact:
    """Replay Phase 8B then regenerate Phase 8N with no network access."""

    artifact = _read_artifact(artifact_path)
    try:
        source = _load_or_reconstruct_phase8b(
            _source_path(source_artifact, source_root), source_root=source_root
        )
        validate_and_replay_payload(
            dict(artifact.config), dict(artifact.result), source
        )
    except (OSError, ValueError, SyntheticMotorArtifactError) as exc:
        raise SyntheticTTMnOutputArtifactError("full Phase 8N replay failed") from exc
    return artifact


def generate_synthetic_ttmn_output_artifact(
    *,
    source_artifact: str | Path | None = None,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    threshold_dimensionless: Any = 0.25,
) -> LoadedSyntheticTTMnOutputArtifact:
    """Generate the fixed six-fixture output rule from a replayed Phase 8B artifact."""

    try:
        phase8b = _load_or_reconstruct_phase8b(
            _source_path(source_artifact, source_root), source_root=source_root
        )
        config, result = execute_output_rule(
            phase8b, threshold_dimensionless=threshold_dimensionless
        )
    except (OSError, ValueError, SyntheticMotorArtifactError) as exc:
        raise SyntheticTTMnOutputArtifactError(
            "could not construct Phase 8N output rule"
        ) from exc
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    destination = Path(output_root) / artifact_id
    if destination.exists():
        return replay_synthetic_ttmn_output_artifact(
            destination,
            source_artifact=source_artifact,
            source_root=source_root,
        )
    return export_synthetic_ttmn_output_artifact(
        config,
        result,
        destination,
        source_artifact=phase8b,
    )


__all__ = [
    "CONFIG_FILENAME",
    "DEFAULT_OUTPUT_ROOT",
    "DEFAULT_SOURCE_ARTIFACT",
    "LoadedSyntheticTTMnOutputArtifact",
    "MANIFEST_FILENAME",
    "RESULT_FILENAME",
    "SyntheticTTMnOutputArtifactError",
    "export_synthetic_ttmn_output_artifact",
    "generate_synthetic_ttmn_output_artifact",
    "load_synthetic_ttmn_output_artifact",
    "replay_synthetic_ttmn_output_artifact",
]
