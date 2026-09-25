"""Immutable Phase 7E exploratory sensory-state artifacts and replay."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from neurofly.relative_column_assignment import (
    DEFAULT_OUTPUT_ROOT as DEFAULT_ASSIGNMENT_OUTPUT_ROOT,
)
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    canonical_json_bytes,
    sha256_bytes,
)
from neurofly.relative_column_assignment_artifacts import (
    RelativeColumnArtifactError,
    replay_relative_column_artifact,
)
from neurofly.relative_column_sensory_dynamics import (
    BODY_IDS,
    EXPECTED_ASSIGNMENT_ARTIFACT_ID,
    SENSORY_STATE_CONFIG_SCHEMA,
    SENSORY_STATE_RESULT_SCHEMA,
    RelativeColumnSensoryDynamicsError,
    compute_sensory_state_result,
    sensitivity_summary,
)

ARTIFACT_SCHEMA_VERSION = "relative_column_sensory_state_artifact_v1"
CONFIG_FILENAME = "config.json"
RESULT_FILENAME = "sensory_state_result.json"
MANIFEST_FILENAME = "manifest.json"
DEFAULT_ASSIGNMENT_ARTIFACT_PATH = (
    DEFAULT_ASSIGNMENT_OUTPUT_ROOT / EXPECTED_ASSIGNMENT_ARTIFACT_ID
)
DEFAULT_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / "relative_column_sensory_state_v1"
_PAYLOAD_SCHEMAS = {
    CONFIG_FILENAME: SENSORY_STATE_CONFIG_SCHEMA,
    RESULT_FILENAME: SENSORY_STATE_RESULT_SCHEMA,
}


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class RelativeColumnSensoryArtifactError(RuntimeError):
    """Base error for Phase 7E immutable artifacts."""


class RelativeColumnSensoryArtifactIntegrityError(RelativeColumnSensoryArtifactError):
    """A Phase 7E artifact failed schema, payload, or replay validation."""


class RelativeColumnSensoryArtifactExportError(RelativeColumnSensoryArtifactError):
    """A Phase 7E immutable artifact could not be exported."""


@dataclass(frozen=True, slots=True)
class LoadedRelativeColumnSensoryArtifact:
    path: Path
    artifact_id: str
    config: Mapping[str, Any]
    result: Mapping[str, Any]
    manifest: Mapping[str, Any]

    def inspection_dict(self) -> dict[str, Any]:
        body_summary: list[dict[str, Any]] = []
        for body_id in BODY_IDS:
            trajectories = [
                trajectory
                for condition in self.result["conditions"]
                for trajectory in condition["body_trajectories"]
                if trajectory["body_id"] == body_id
            ]
            body_summary.append(
                {
                    "body_id": body_id,
                    "neuron_type": trajectories[0]["neuron_type"],
                    "side": trajectories[0]["side"],
                    "input_metric_id": trajectories[0]["input_metric_id"],
                    "maximum_peak_exposure": max(
                        item["peak_exposure"] for item in trajectories
                    ),
                    "maximum_peak_exploratory_state": max(
                        item["peak_exploratory_state"] for item in trajectories
                    ),
                    "condition_count": len(trajectories),
                }
            )
        return {
            "artifact_id": self.artifact_id,
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "experiment_id": self.result["experiment_id"],
            "model_id": self.result["model_id"],
            "assignment_artifact_id": self.result["assignment_artifact_id"],
            "body_ids": list(BODY_IDS),
            "condition_count": len(self.result["conditions"]),
            "reference_input_metric_id": self.config["reference_parameters"][
                "input_metric_id"
            ],
            "reference_tau_sens_ms": self.config["reference_parameters"]["tau_sens_ms"][
                "value"
            ],
            "reference_gain": self.config["reference_parameters"]["gain"]["value"],
            "sensitivity": sensitivity_summary(self.result),
            "body_summary": body_summary,
            "physiological_interpretation": False,
            "validation_status": "EXPLORATORY_MODEL_REPLAY_ONLY",
        }


def _artifact_id(config_sha256: str, result_sha256: str) -> str:
    return sha256_bytes(
        canonical_json_bytes(
            {
                "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                "config_sha256": config_sha256,
                "result_sha256": result_sha256,
                "body_ids": list(BODY_IDS),
            }
        )
    )


def relative_column_sensory_artifact_id(
    config: Mapping[str, Any], result: Mapping[str, Any]
) -> str:
    """Calculate the immutable output identity without writing files."""

    config_bytes = canonical_json_bytes(dict(config)) + b"\n"
    result_bytes = canonical_json_bytes(dict(result)) + b"\n"
    return _artifact_id(sha256_bytes(config_bytes), sha256_bytes(result_bytes))


def _canonical_payload(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise RelativeColumnSensoryArtifactIntegrityError(
            f"malformed Phase 7E {label}."
        ) from None
    if not isinstance(value, dict):
        raise RelativeColumnSensoryArtifactIntegrityError(
            f"Phase 7E {label} must be a JSON object."
        )
    expected = canonical_json_bytes(value) + b"\n"
    if raw != expected:
        raise RelativeColumnSensoryArtifactIntegrityError(
            f"Phase 7E {label} is not canonical JSON."
        )
    return value, raw


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise RelativeColumnSensoryArtifactExportError(
            f"could not write Phase 7E file {path.name}."
        ) from exc


def export_relative_column_sensory_artifact(
    config: Mapping[str, Any],
    result: Mapping[str, Any],
    destination: str | Path,
) -> LoadedRelativeColumnSensoryArtifact:
    """Atomically create a separate immutable Phase 7E state artifact."""

    if config.get("schema") != SENSORY_STATE_CONFIG_SCHEMA:
        raise RelativeColumnSensoryArtifactExportError(
            "unsupported Phase 7E config schema."
        )
    if result.get("schema") != SENSORY_STATE_RESULT_SCHEMA:
        raise RelativeColumnSensoryArtifactExportError(
            "unsupported Phase 7E result schema."
        )
    if tuple(result.get("body_ids", ())) != BODY_IDS:
        raise RelativeColumnSensoryArtifactExportError(
            "Phase 7E output body set is not the fixed four."
        )
    output = Path(destination)
    if output.exists():
        raise RelativeColumnSensoryArtifactExportError(
            f"Phase 7E artifacts are immutable; destination exists: {output}"
        )
    config_bytes = canonical_json_bytes(dict(config)) + b"\n"
    result_bytes = canonical_json_bytes(dict(result)) + b"\n"
    config_hash = sha256_bytes(config_bytes)
    result_hash = sha256_bytes(result_bytes)
    artifact_id = relative_column_sensory_artifact_id(config, result)
    manifest = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "config_sha256": config_hash,
        "result_sha256": result_hash,
        "body_ids": list(BODY_IDS),
        "files": {
            CONFIG_FILENAME: {
                "schema": _PAYLOAD_SCHEMAS[CONFIG_FILENAME],
                "bytes": len(config_bytes),
                "sha256": config_hash,
            },
            RESULT_FILENAME: {
                "schema": _PAYLOAD_SCHEMAS[RESULT_FILENAME],
                "bytes": len(result_bytes),
                "sha256": result_hash,
            },
        },
        "assignment_artifact_id": config["assignment_input"]["artifact_id"],
    }
    manifest_bytes = canonical_json_bytes(manifest) + b"\n"
    staging: Path | None = None
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, manifest_bytes)
        load_relative_column_sensory_artifact(staging)
        if output.exists():
            raise RelativeColumnSensoryArtifactExportError(
                f"Phase 7E artifacts are immutable; destination exists: {output}"
            )
        os.replace(staging, output)
        staging = None
    except RelativeColumnSensoryArtifactError:
        raise
    except OSError as exc:
        raise RelativeColumnSensoryArtifactExportError(
            "could not finalize Phase 7E artifact."
        ) from exc
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return load_relative_column_sensory_artifact(output)


def load_relative_column_sensory_artifact(
    path: str | Path,
) -> LoadedRelativeColumnSensoryArtifact:
    """Verify canonical payloads and artifact identity without recomputing input."""

    root = Path(path)
    if not root.is_dir():
        raise RelativeColumnSensoryArtifactIntegrityError(
            f"Phase 7E artifact directory is missing: {root}"
        )
    if {item.name for item in root.iterdir()} != {
        CONFIG_FILENAME,
        RESULT_FILENAME,
        MANIFEST_FILENAME,
    }:
        raise RelativeColumnSensoryArtifactIntegrityError(
            "Phase 7E artifact file set is invalid."
        )
    manifest, _ = _canonical_payload(root / MANIFEST_FILENAME, "manifest")
    expected_fields = {
        "artifact_schema_version",
        "artifact_id",
        "config_sha256",
        "result_sha256",
        "body_ids",
        "files",
        "assignment_artifact_id",
    }
    if set(manifest) != expected_fields:
        raise RelativeColumnSensoryArtifactIntegrityError(
            "Phase 7E manifest fields are invalid."
        )
    if (
        manifest["artifact_schema_version"] != ARTIFACT_SCHEMA_VERSION
        or manifest["body_ids"] != list(BODY_IDS)
        or manifest["assignment_artifact_id"] != EXPECTED_ASSIGNMENT_ARTIFACT_ID
    ):
        raise RelativeColumnSensoryArtifactIntegrityError(
            "Phase 7E manifest identity does not match the fixed experiment."
        )
    files = manifest["files"]
    if not isinstance(files, dict) or set(files) != set(_PAYLOAD_SCHEMAS):
        raise RelativeColumnSensoryArtifactIntegrityError(
            "Phase 7E manifest payload list is invalid."
        )
    payloads: dict[str, dict[str, Any]] = {}
    for filename, schema in _PAYLOAD_SCHEMAS.items():
        file_info = files[filename]
        if (
            not isinstance(file_info, dict)
            or set(file_info) != {"schema", "bytes", "sha256"}
            or file_info["schema"] != schema
            or not _is_int(file_info["bytes"])
            or file_info["bytes"] < 0
        ):
            raise RelativeColumnSensoryArtifactIntegrityError(
                f"Phase 7E payload metadata is invalid for {filename}."
            )
        payload, raw = _canonical_payload(root / filename, filename)
        digest = sha256_bytes(raw)
        if len(raw) != file_info["bytes"] or digest != file_info["sha256"]:
            raise RelativeColumnSensoryArtifactIntegrityError(
                f"Phase 7E payload hash mismatch for {filename}."
            )
        payloads[filename] = payload
    config = payloads[CONFIG_FILENAME]
    result = payloads[RESULT_FILENAME]
    assignment_input = config.get("assignment_input")
    config_hash = sha256_bytes((root / CONFIG_FILENAME).read_bytes())
    result_hash = sha256_bytes((root / RESULT_FILENAME).read_bytes())
    if (
        config.get("schema") != SENSORY_STATE_CONFIG_SCHEMA
        or result.get("schema") != SENSORY_STATE_RESULT_SCHEMA
        or tuple(result.get("body_ids", ())) != BODY_IDS
        or result.get("assignment_artifact_id") != EXPECTED_ASSIGNMENT_ARTIFACT_ID
        or not isinstance(assignment_input, dict)
        or assignment_input.get("artifact_id") != EXPECTED_ASSIGNMENT_ARTIFACT_ID
        or manifest["config_sha256"] != config_hash
        or manifest["result_sha256"] != result_hash
        or manifest["artifact_id"] != _artifact_id(config_hash, result_hash)
    ):
        raise RelativeColumnSensoryArtifactIntegrityError(
            "Phase 7E payload or content identity is inconsistent."
        )
    return LoadedRelativeColumnSensoryArtifact(
        path=root,
        artifact_id=manifest["artifact_id"],
        config=MappingProxyType(config),
        result=MappingProxyType(result),
        manifest=MappingProxyType(manifest),
    )


def replay_relative_column_sensory_artifact(
    artifact_path: str | Path,
    *,
    assignment_artifact_path: str | Path,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> LoadedRelativeColumnSensoryArtifact:
    """Replay Phase 7D first, then require exact Phase 7E config/result equality."""

    artifact = load_relative_column_sensory_artifact(artifact_path)
    try:
        assignment = replay_relative_column_artifact(
            assignment_artifact_path,
            source_root=source_root,
            workbook_path=workbook_path,
        )
        expected_config, expected_result = compute_sensory_state_result(assignment)
    except (
        RelativeColumnArtifactError,
        RelativeColumnSensoryDynamicsError,
        OSError,
        ValueError,
    ) as exc:
        raise RelativeColumnSensoryArtifactIntegrityError(
            f"Phase 7E replay could not validate Phase 7D input: {exc}"
        ) from exc
    if canonical_json_bytes(expected_config) != canonical_json_bytes(
        dict(artifact.config)
    ):
        raise RelativeColumnSensoryArtifactIntegrityError(
            "Phase 7E config differs on replay."
        )
    if canonical_json_bytes(expected_result) != canonical_json_bytes(
        dict(artifact.result)
    ):
        raise RelativeColumnSensoryArtifactIntegrityError(
            "Phase 7E result differs on replay."
        )
    return artifact


def make_relative_column_sensory_artifact(
    *,
    assignment_artifact_path: str | Path = DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    workbook_path: str | Path = DEFAULT_WORKBOOK,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replay the pinned 7D assignment and derive the Phase 7E artifact payload."""

    try:
        assignment = replay_relative_column_artifact(
            assignment_artifact_path,
            source_root=source_root,
            workbook_path=workbook_path,
        )
        return compute_sensory_state_result(assignment)
    except (
        RelativeColumnArtifactError,
        RelativeColumnSensoryDynamicsError,
        OSError,
        ValueError,
    ) as exc:
        raise RelativeColumnSensoryArtifactIntegrityError(
            f"could not load replay-verified Phase 7D input: {exc}"
        ) from exc
