"""Content-addressed Phase 8C composition artifacts and full replay."""

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
from neurofly.sensory_dnp01_motor_adapter import (
    ARTIFACT_SCHEMA,
    CONFIG_SCHEMA,
    RESULT_SCHEMA,
    SensoryDnp01MotorAdapterError,
    build_sensory_dnp01_motor_payload,
)
from neurofly.sensory_population_execution_artifacts import (
    load_execution_artifact,
)
from neurofly.sensory_population_readiness import load_phase7n_sources

DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / "sensory_dnp01_ttmn_adapter_v1"
CONFIG_FILENAME = "adapter_config.json"
RESULT_FILENAME = "adapter_result.json"
MANIFEST_FILENAME = "manifest.json"
_ARTIFACT_FILES = {CONFIG_FILENAME, RESULT_FILENAME, MANIFEST_FILENAME}


class SensoryDnp01MotorArtifactError(RuntimeError):
    """Invalid, tampered, or unreplayable Phase 8C artifact."""


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
        raise SensoryDnp01MotorArtifactError(
            "Phase 8C artifact payload is not deterministic JSON."
        ) from exc


def _hash(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _content_hash(value: dict[str, Any]) -> str:
    without_hash = dict(value)
    without_hash.pop("config_sha256", None)
    without_hash.pop("result_sha256", None)
    return _hash(_json_bytes(without_hash).rstrip(b"\n"))


def _artifact_id(config_hash: str, result_hash: str) -> str:
    return _hash(
        _json_bytes(
            {
                "artifact_schema": ARTIFACT_SCHEMA,
                "config_sha256": config_hash,
                "result_sha256": result_hash,
            }
        ).rstrip(b"\n")
    )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise SensoryDnp01MotorArtifactError(f"malformed {label}.") from None
    if not isinstance(value, dict) or _json_bytes(value) != raw:
        raise SensoryDnp01MotorArtifactError(f"{label} is not canonical JSON.")
    return value


@dataclass(frozen=True, slots=True)
class LoadedSensoryDnp01MotorArtifact:
    path: Path
    artifact_id: str
    config: MappingProxyType
    result: MappingProxyType
    manifest: MappingProxyType

    def summary(self) -> dict[str, Any]:
        trajectories = self.result["ttmn_model_state"]
        return {
            "artifact_schema": ARTIFACT_SCHEMA,
            "artifact_id": self.artifact_id,
            "config_sha256": self.manifest["config_sha256"],
            "result_sha256": self.manifest["result_sha256"],
            "source_kind": self.result["source_kind"],
            "upstream_artifact_id": self.result["upstream_artifact_id"],
            "source_condition_id": self.result["source_condition_id"],
            "event_count": self.result["event_count"],
            "all_condition_event_audit": self.result["all_condition_event_audit"],
            "ttmn": [
                {
                    "body_id": item["body_id"],
                    "side": item["side"],
                    "input_event_count": item["input_event_count"],
                    "peak_state": item["peak_state"],
                    "final_state": item["state"][-1],
                }
                for item in trajectories
            ],
            "artifact_bytes": sum(
                item.stat().st_size for item in self.path.iterdir() if item.is_file()
            ),
            "artifact_path": str(self.path),
            "integrity_validation": "PASSED",
        }


def _validate_payload(config: dict[str, Any], result: dict[str, Any]) -> None:
    if (
        config.get("schema") != CONFIG_SCHEMA
        or config.get("artifact_schema") != ARTIFACT_SCHEMA
        or result.get("schema") != RESULT_SCHEMA
        or config.get("source_kind") != "SIMULATED_FROM_SENSORY_EXPERIMENT"
        or result.get("source_kind") != config.get("source_kind")
        or config.get("fallback_policy")
        != {
            "voltage_to_event": False,
            "external_drive_to_event": False,
            "filtered_state_to_event": False,
            "synthetic_event_fallback": False,
        }
        or config.get("population_normalization") != "none"
        or config.get("structural_weight_numerical_use") != "none_source_metadata_only"
        or config.get("routing_evidence_contract_sha256")
        != result.get("routing_evidence_contract_sha256")
        or result.get("voltage_or_drive_fallback_used") is not False
        or result.get("synthetic_fallback_used") is not False
        or result.get("validation_status") != "PASSED"
    ):
        raise SensoryDnp01MotorArtifactError(
            "Phase 8C config/result semantics are invalid."
        )
    source_events = result.get("source_event_records")
    adapted = result.get("adapted_dnp01_events")
    mapped = result.get("mapped_motor_inputs")
    audit = result.get("all_condition_event_audit")
    trajectories = result.get("ttmn_model_state")
    if not all(
        isinstance(item, list)
        for item in (source_events, adapted, mapped, audit, trajectories)
    ):
        raise SensoryDnp01MotorArtifactError("Phase 8C result arrays are malformed.")
    if (
        len(source_events) != len(adapted)
        or len(adapted) != len(mapped)
        or len(trajectories) != 2
        or result.get("event_count") != len(adapted)
        or result.get("upstream_artifact_id")
        != config.get("upstream_artifact", {}).get("artifact_id")
        or result.get("source_condition_id") != config.get("source_condition_id")
        or result.get("all_conditions_zero_events")
        != all(row.get("event_count") == 0 for row in audit)
    ):
        raise SensoryDnp01MotorArtifactError("Phase 8C result accounting is invalid.")
    expected_targets = {800146: "R", 804642: "L"}
    if {
        row.get("body_id"): row.get("side") for row in trajectories
    } != expected_targets:
        raise SensoryDnp01MotorArtifactError("Phase 8C TTMn identities are invalid.")
    for row in trajectories:
        if (
            row.get("neuron_type") != "TTMn"
            or row.get("state_unit") != "dimensionless"
            or not isinstance(row.get("state"), list)
            or len(row["state"]) != config.get("time_grid", {}).get("boundary_count")
            or row.get("input_event_count")
            != sum(item.get("target_body_id") == row.get("body_id") for item in mapped)
        ):
            raise SensoryDnp01MotorArtifactError(
                "Phase 8C TTMn trajectory identity/accounting is invalid."
            )
    if _content_hash(config) != config.get("config_sha256"):
        raise SensoryDnp01MotorArtifactError("Phase 8C config hash mismatch.")
    if _content_hash(result) != result.get("result_sha256"):
        raise SensoryDnp01MotorArtifactError("Phase 8C result hash mismatch.")


def load_sensory_dnp01_motor_artifact(
    artifact_path: str | Path,
) -> LoadedSensoryDnp01MotorArtifact:
    path = Path(artifact_path)
    if not path.is_dir():
        raise SensoryDnp01MotorArtifactError("Phase 8C artifact not found.")
    try:
        if {item.name for item in path.iterdir()} != _ARTIFACT_FILES:
            raise SensoryDnp01MotorArtifactError("unexpected Phase 8C artifact files.")
    except OSError as exc:
        raise SensoryDnp01MotorArtifactError(
            "could not inspect Phase 8C artifact directory."
        ) from exc
    config = _read_json(path / CONFIG_FILENAME, "Phase 8C config")
    result = _read_json(path / RESULT_FILENAME, "Phase 8C result")
    manifest = _read_json(path / MANIFEST_FILENAME, "Phase 8C manifest")
    _validate_payload(config, result)
    config_raw = _json_bytes(config)
    result_raw = _json_bytes(result)
    expected_id = _artifact_id(_hash(config_raw), _hash(result_raw))
    if (
        manifest
        != {
            "artifact_schema": ARTIFACT_SCHEMA,
            "artifact_id": expected_id,
            "config_sha256": _hash(config_raw),
            "result_sha256": _hash(result_raw),
        }
        or path.name != expected_id
    ):
        raise SensoryDnp01MotorArtifactError("Phase 8C artifact integrity mismatch.")
    return LoadedSensoryDnp01MotorArtifact(
        path,
        expected_id,
        MappingProxyType(config),
        MappingProxyType(result),
        MappingProxyType(manifest),
    )


def _compute_payload(
    source_artifact_path: str | Path,
    condition_id: str,
    source_root: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    upstream = load_execution_artifact(source_artifact_path)
    source, circuit, _grid = load_phase7n_sources(source_root)
    return build_sensory_dnp01_motor_payload(upstream, condition_id, circuit, source)


def export_sensory_dnp01_motor_artifact(
    config: dict[str, Any], result: dict[str, Any], output_root: str | Path
) -> LoadedSensoryDnp01MotorArtifact:
    _validate_payload(config, result)
    config_raw, result_raw = _json_bytes(config), _json_bytes(result)
    config_hash, result_hash = _hash(config_raw), _hash(result_raw)
    artifact_id = _artifact_id(config_hash, result_hash)
    root = Path(output_root)
    destination = root / artifact_id
    manifest = {
        "artifact_schema": ARTIFACT_SCHEMA,
        "artifact_id": artifact_id,
        "config_sha256": config_hash,
        "result_sha256": result_hash,
    }
    if destination.exists():
        existing = load_sensory_dnp01_motor_artifact(destination)
        if dict(existing.config) != config or dict(existing.result) != result:
            raise SensoryDnp01MotorArtifactError(
                "immutable Phase 8C artifact differs from deterministic output."
            )
        return existing
    try:
        root.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{artifact_id}.", dir=root))
    except OSError as exc:
        raise SensoryDnp01MotorArtifactError(
            "could not create Phase 8C artifact staging directory."
        ) from exc
    try:
        for name, payload in (
            (CONFIG_FILENAME, config_raw),
            (RESULT_FILENAME, result_raw),
            (MANIFEST_FILENAME, _json_bytes(manifest)),
        ):
            with (staging / name).open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        try:
            os.replace(staging, destination)
        except OSError as exc:
            raise SensoryDnp01MotorArtifactError(
                "could not finalize immutable Phase 8C artifact."
            ) from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return load_sensory_dnp01_motor_artifact(destination)


def generate_sensory_dnp01_motor_artifact(
    source_artifact_path: str | Path,
    condition_id: str,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    output_root: str | Path = DEFAULT_ARTIFACT_ROOT,
) -> LoadedSensoryDnp01MotorArtifact:
    config, result = _compute_payload(source_artifact_path, condition_id, source_root)
    return export_sensory_dnp01_motor_artifact(config, result, output_root)


def replay_sensory_dnp01_motor_artifact(
    artifact_path: str | Path,
    source_artifact_path: str | Path,
    condition_id: str,
    *,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
) -> LoadedSensoryDnp01MotorArtifact:
    artifact = load_sensory_dnp01_motor_artifact(artifact_path)
    if artifact.config.get("source_condition_id") != condition_id:
        raise SensoryDnp01MotorArtifactError(
            "requested source condition differs from the persisted adapter artifact."
        )
    try:
        config, result = _compute_payload(
            source_artifact_path, condition_id, source_root
        )
    except (OSError, ValueError, SensoryDnp01MotorAdapterError) as exc:
        raise SensoryDnp01MotorArtifactError("full Phase 8C replay failed.") from exc
    if config != dict(artifact.config) or result != dict(artifact.result):
        raise SensoryDnp01MotorArtifactError(
            "full Phase 8C replay differs from the stored result."
        )
    if (
        _artifact_id(_hash(_json_bytes(config)), _hash(_json_bytes(result)))
        != artifact.artifact_id
    ):
        raise SensoryDnp01MotorArtifactError("replayed Phase 8C identity changed.")
    return artifact


__all__ = [
    "DEFAULT_ARTIFACT_ROOT",
    "LoadedSensoryDnp01MotorArtifact",
    "SensoryDnp01MotorArtifactError",
    "export_sensory_dnp01_motor_artifact",
    "generate_sensory_dnp01_motor_artifact",
    "load_sensory_dnp01_motor_artifact",
    "replay_sensory_dnp01_motor_artifact",
]
