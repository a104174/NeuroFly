"""Immutable Phase 8H production DNp01-to-PSI/DLMn artifacts and replay."""

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

from neurofly.psi_dlmn_event_relay import DEFAULT_MOTOR_CONTRACT_PATH
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    canonical_json_bytes,
)
from neurofly.sensory_dnp01_motor_adapter import PHASE7O_ARTIFACT_ID
from neurofly.sensory_population_execution_artifacts import load_execution_artifact
from neurofly.sensory_population_readiness import load_phase7n_sources
from neurofly.sensory_psi_dlmn_event_adapter import (
    ARTIFACT_SCHEMA,
    CONFIG_SCHEMA,
    DEFAULT_OUTPUT_ROOT,
    RESULT_SCHEMA,
    SensoryPsiDlmnEventAdapterError,
    build_sensory_psi_dlmn_payload,
)

CONFIG_FILENAME = "adapter_config.json"
RESULT_FILENAME = "adapter_result.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONFIG_FILENAME, RESULT_FILENAME, MANIFEST_FILENAME}
DEFAULT_PHASE7O_ROOT = DEFAULT_SOURCE_ROOT / "sensory_population_experiment_311_v1"


class SensoryPsiDlmnEventArtifactError(RuntimeError):
    """Invalid, tampered, or unreplayable Phase 8H artifact."""


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
        raise SensoryPsiDlmnEventArtifactError(
            "artifact data is not deterministic JSON"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _payload_sha256(value: Any) -> str:
    return _sha256_bytes(canonical_json_bytes(value))


def _artifact_id(config_sha256: str, result_sha256: str) -> str:
    return _sha256_bytes(
        _json_bytes(
            {
                "artifact_schema_version": ARTIFACT_SCHEMA,
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
        raise SensoryPsiDlmnEventArtifactError(f"malformed {label}") from None
    if not isinstance(value, dict) or _json_bytes(value) != raw:
        raise SensoryPsiDlmnEventArtifactError(f"{label} is not canonical JSON")
    return value


def _validate_payload_hashes(config: dict[str, Any], result: dict[str, Any]) -> None:
    policy = config.get("active_edge_policy")
    counts = result.get("counts")
    upstream = config.get("upstream_artifact")
    source_records = result.get("source_event_records")
    adapted_events = result.get("adapted_dnp01_events")
    psi_events = result.get("psi_routed_events")
    dlmn_events = result.get("dlmn_routed_events")
    if (
        config.get("schema_version") != CONFIG_SCHEMA
        or config.get("artifact_schema_version") != ARTIFACT_SCHEMA
        or result.get("schema_version") != RESULT_SCHEMA
        or config.get("source_kind") != "SIMULATED_FROM_SENSORY_EXPERIMENT"
        or result.get("source_kind") != "SIMULATED_FROM_SENSORY_EXPERIMENT"
        or config.get("phase8b_synthetic_fixture_in_provenance") is not False
        or config.get("latent_psi_or_dlmn_state") is not False
        or not isinstance(policy, dict)
        or policy.get("propagation_layers") != 2
        or policy.get("recursive_graph_traversal") is not False
        or not isinstance(upstream, dict)
        or upstream.get("artifact_id") != result.get("upstream_artifact_id")
        or config.get("source_condition_id") != result.get("source_condition_id")
        or not isinstance(counts, dict)
        or not isinstance(source_records, list)
        or not isinstance(adapted_events, list)
        or not isinstance(psi_events, list)
        or not isinstance(dlmn_events, list)
        or counts.get("dnp01_events") != len(adapted_events)
        or counts.get("psi_routed_events") != len(psi_events)
        or counts.get("dlmn_routed_events") != len(dlmn_events)
        or config.get("source_event_count") != len(adapted_events)
        or config.get("source_event_records_sha256") != _payload_sha256(source_records)
        or not isinstance(result.get("all_condition_audit"), list)
    ):
        raise SensoryPsiDlmnEventArtifactError("Phase 8H payload invariants failed")
    if not isinstance(config.get("config_sha256"), str) or config[
        "config_sha256"
    ] != _payload_sha256(
        {key: value for key, value in config.items() if key != "config_sha256"}
    ):
        raise SensoryPsiDlmnEventArtifactError("Phase 8H configuration hash mismatch")
    if (
        not isinstance(result.get("result_sha256"), str)
        or result["result_sha256"]
        != _payload_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        or result.get("config_sha256") != config.get("config_sha256")
    ):
        raise SensoryPsiDlmnEventArtifactError("Phase 8H result hash mismatch")


def _write(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise SensoryPsiDlmnEventArtifactError(f"could not write {path.name}") from exc


@dataclass(frozen=True, slots=True)
class LoadedSensoryPsiDlmnEventArtifact:
    path: Path
    artifact_id: str
    config: MappingProxyType
    result: MappingProxyType
    manifest: MappingProxyType

    def summary(self) -> dict[str, Any]:
        counts = self.result["counts"]
        return {
            "artifact_schema_version": ARTIFACT_SCHEMA,
            "artifact_id": self.artifact_id,
            "artifact_path": str(self.path),
            "config_sha256": self.config["config_sha256"],
            "result_sha256": self.result["result_sha256"],
            "upstream_artifact_id": self.result["upstream_artifact_id"],
            "source_condition_id": self.result["source_condition_id"],
            "source_kind": self.result["source_kind"],
            "motor_contract_id": self.result["motor_contract_id"],
            "condition_audit_count": len(self.result["all_condition_audit"]),
            "all_conditions_zero_events": self.result["all_conditions_zero_events"],
            "event_counts": dict(counts),
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
) -> LoadedSensoryPsiDlmnEventArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise SensoryPsiDlmnEventArtifactError("Phase 8H artifact not found")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise SensoryPsiDlmnEventArtifactError(
                "unexpected Phase 8H artifact file set"
            )
    except OSError as exc:
        raise SensoryPsiDlmnEventArtifactError(
            "could not inspect Phase 8H artifact directory"
        ) from exc
    config = _read_json(path / CONFIG_FILENAME, "Phase 8H configuration")
    result = _read_json(path / RESULT_FILENAME, "Phase 8H result")
    manifest = _read_json(path / MANIFEST_FILENAME, "Phase 8H manifest")
    if set(manifest) != {
        "artifact_schema_version",
        "artifact_id",
        "config_sha256",
        "result_sha256",
        "files",
    }:
        raise SensoryPsiDlmnEventArtifactError("invalid Phase 8H manifest fields")
    if (
        manifest.get("artifact_schema_version") != ARTIFACT_SCHEMA
        or not isinstance(manifest.get("files"), dict)
        or set(manifest.get("files", {})) != {CONFIG_FILENAME, RESULT_FILENAME}
    ):
        raise SensoryPsiDlmnEventArtifactError("unsupported Phase 8H artifact schema")
    for filename, value in ((CONFIG_FILENAME, config), (RESULT_FILENAME, result)):
        payload = _json_bytes(value)
        record = manifest["files"][filename]
        expected_schema = (
            CONFIG_SCHEMA if filename == CONFIG_FILENAME else RESULT_SCHEMA
        )
        if (
            not isinstance(record, dict)
            or set(record) != {"schema", "bytes", "sha256"}
            or record.get("schema") != expected_schema
            or record.get("bytes") != len(payload)
            or record.get("sha256") != _sha256_bytes(payload)
            or (path / filename).stat().st_size != len(payload)
        ):
            raise SensoryPsiDlmnEventArtifactError(f"{filename} integrity mismatch")
    _validate_payload_hashes(config, result)
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    if (
        manifest.get("config_sha256") != config["config_sha256"]
        or manifest.get("result_sha256") != result["result_sha256"]
        or manifest.get("artifact_id") != artifact_id
        or (expected_artifact_id is not None and artifact_id != expected_artifact_id)
        or (path.name != artifact_id and not allow_staging)
    ):
        raise SensoryPsiDlmnEventArtifactError("Phase 8H artifact identity mismatch")
    return LoadedSensoryPsiDlmnEventArtifact(
        path,
        artifact_id,
        MappingProxyType(config),
        MappingProxyType(result),
        MappingProxyType(manifest),
    )


def load_sensory_psi_dlmn_event_artifact(
    artifact_path: str | Path,
) -> LoadedSensoryPsiDlmnEventArtifact:
    """Validate canonical file bytes and the Phase 8H content identity."""

    return _read_artifact(artifact_path)


def _export_artifact(
    config: dict[str, Any], result: dict[str, Any], destination: Path
) -> LoadedSensoryPsiDlmnEventArtifact:
    _validate_payload_hashes(config, result)
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    if destination.exists():
        raise SensoryPsiDlmnEventArtifactError(
            f"immutable artifact destination already exists: {destination}"
        )
    config_bytes = _json_bytes(config)
    result_bytes = _json_bytes(result)
    manifest = {
        "artifact_schema_version": ARTIFACT_SCHEMA,
        "artifact_id": artifact_id,
        "config_sha256": config["config_sha256"],
        "result_sha256": result["result_sha256"],
        "files": {
            CONFIG_FILENAME: {
                "schema": CONFIG_SCHEMA,
                "bytes": len(config_bytes),
                "sha256": _sha256_bytes(config_bytes),
            },
            RESULT_FILENAME: {
                "schema": RESULT_SCHEMA,
                "bytes": len(result_bytes),
                "sha256": _sha256_bytes(result_bytes),
            },
        },
    }
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{artifact_id}.", dir=destination.parent)
        )
    except OSError as exc:
        raise SensoryPsiDlmnEventArtifactError(
            "could not create artifact staging area"
        ) from exc
    try:
        _write(staging / CONFIG_FILENAME, config_bytes)
        _write(staging / RESULT_FILENAME, result_bytes)
        _write(staging / MANIFEST_FILENAME, _json_bytes(manifest))
        _read_artifact(staging, allow_staging=True, expected_artifact_id=artifact_id)
        os.replace(staging, destination)
    except OSError as exc:
        raise SensoryPsiDlmnEventArtifactError(
            "could not finalize Phase 8H artifact"
        ) from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return _read_artifact(destination)


def _rebuild_payload(
    phase7o_artifact_path: str | Path,
    condition_id: str,
    *,
    source_root: str | Path,
    motor_contract_path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        source_artifact = load_execution_artifact(phase7o_artifact_path)
        source, circuit_contract, _grid = load_phase7n_sources(source_root)
        return build_sensory_psi_dlmn_payload(
            source_artifact,
            condition_id,
            circuit_contract,
            source,
            motor_contract_path=str(motor_contract_path),
        )
    except (OSError, ValueError, SensoryPsiDlmnEventAdapterError) as exc:
        raise SensoryPsiDlmnEventArtifactError(
            "Phase 8H production source could not be revalidated"
        ) from exc


def generate_sensory_psi_dlmn_event_artifact(
    phase7o_artifact_path: str | Path,
    condition_id: str,
    *,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    motor_contract_path: str | Path = DEFAULT_MOTOR_CONTRACT_PATH,
) -> LoadedSensoryPsiDlmnEventArtifact:
    """Generate, or replay if present, one explicitly selected condition."""

    config, result = _rebuild_payload(
        phase7o_artifact_path,
        condition_id,
        source_root=source_root,
        motor_contract_path=motor_contract_path,
    )
    destination = Path(output_root) / _artifact_id(
        config["config_sha256"], result["result_sha256"]
    )
    if destination.exists():
        return replay_sensory_psi_dlmn_event_artifact(
            destination,
            phase7o_artifact_path,
            condition_id,
            source_root=source_root,
            motor_contract_path=motor_contract_path,
        )
    return _export_artifact(config, result, destination)


def replay_sensory_psi_dlmn_event_artifact(
    artifact_path: str | Path,
    phase7o_artifact_path: str | Path,
    condition_id: str,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    motor_contract_path: str | Path = DEFAULT_MOTOR_CONTRACT_PATH,
) -> LoadedSensoryPsiDlmnEventArtifact:
    """Re-extract genuine source events and deterministically replay the relay."""

    artifact = _read_artifact(artifact_path)
    if artifact.config.get("source_condition_id") != condition_id:
        raise SensoryPsiDlmnEventArtifactError(
            "requested condition does not match Phase 8H artifact"
        )
    config, result = _rebuild_payload(
        phase7o_artifact_path,
        condition_id,
        source_root=source_root,
        motor_contract_path=motor_contract_path,
    )
    if dict(artifact.config) != config or dict(artifact.result) != result:
        raise SensoryPsiDlmnEventArtifactError(
            "Phase 8H artifact differs from deterministic source replay"
        )
    return artifact


def default_phase7o_artifact_path() -> Path:
    """Return the content-addressed canonical Phase 7O artifact path."""

    return DEFAULT_PHASE7O_ROOT / PHASE7O_ARTIFACT_ID


__all__ = [
    "DEFAULT_OUTPUT_ROOT",
    "LoadedSensoryPsiDlmnEventArtifact",
    "SensoryPsiDlmnEventArtifactError",
    "default_phase7o_artifact_path",
    "generate_sensory_psi_dlmn_event_artifact",
    "load_sensory_psi_dlmn_event_artifact",
    "replay_sensory_psi_dlmn_event_artifact",
]
