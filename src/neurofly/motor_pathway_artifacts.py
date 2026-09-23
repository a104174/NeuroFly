"""Portable Phase 6C motor-pathway artifacts with embedded upstream runs."""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any

from neurofly.experiment_artifacts import (
    ArtifactExportError,
    ArtifactSchemaError,
    LoadedExperimentArtifact,
    export_experiment_artifact,
    load_experiment_artifact,
)
from neurofly.experiments import ExperimentResult
from neurofly.motor_pathway import (
    MOTOR_PATHWAY_EVIDENCE,
    MOTOR_RESULT_SCHEMA_VERSION,
    MotorPathwayError,
    MotorPathwayExperimentResult,
    MotorPathwayRunConfig,
    MotorSensitivityPoint,
    TTMnInputEvent,
    TTMnIntegratorConfig,
    TTMnStateTrajectory,
)

MOTOR_ARTIFACT_SCHEMA_VERSION = "motor_pathway_experiment_artifact_v1"
MOTOR_STATE_FILENAME = "motor_neural_state.json"
MANIFEST_FILENAME = "manifest.json"
UPSTREAM_DIRECTORY = "upstream"


class MotorArtifactError(RuntimeError):
    """Base error for Phase 6C artifact persistence and loading."""


class MotorArtifactNotFoundError(MotorArtifactError):
    """The requested immutable motor artifact is not present."""


class InvalidMotorArtifactIdError(MotorArtifactError):
    """A requested motor artifact identifier is malformed."""


class MotorArtifactIntegrityError(MotorArtifactError):
    """A motor artifact failed integrity or cross-layer validation."""


def _json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MotorArtifactSchemaError("value is not deterministic JSON") from exc


def _sha256_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise MotorArtifactIntegrityError("could not read motor payload") from exc
    return digest.hexdigest()


class MotorArtifactSchemaError(MotorArtifactError):
    """A motor artifact uses unsupported or malformed fields."""


def _write(path: Path, data: bytes) -> None:
    try:
        with path.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise ArtifactExportError(f"could not write {path.name}") from exc


def _finite(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise MotorArtifactSchemaError(f"{field_name} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise MotorArtifactSchemaError(f"{field_name} must be finite.") from None
    if not math.isfinite(result):
        raise MotorArtifactSchemaError(f"{field_name} must be finite.")
    return result


def _int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise MotorArtifactSchemaError(f"{field_name} must be an integer.")
    return value


def _keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MotorArtifactSchemaError(f"{label} must be an object.")
    missing = expected - value.keys()
    extra = value.keys() - expected
    if missing or extra:
        raise MotorArtifactSchemaError(
            f"invalid {label} fields: missing={sorted(missing)!r}, "
            f"unexpected={sorted(extra)!r}"
        )
    return value


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        raise MotorArtifactIntegrityError(f"malformed {label}") from None
    return _keys(value, set(value) if isinstance(value, dict) else set(), label)


@dataclass(frozen=True, slots=True)
class LoadedMotorPathwayArtifact:
    path: Path
    artifact_id: str
    upstream_artifact: LoadedExperimentArtifact
    result: MotorPathwayExperimentResult
    manifest: MappingProxyType

    def inspection_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_schema_version": MOTOR_ARTIFACT_SCHEMA_VERSION,
            "upstream_artifact_id": self.upstream_artifact.artifact_id,
            "upstream_config_sha256": self.result.upstream_result.config_sha256,
            "upstream_result_sha256": self.result.upstream_result.result_sha256,
            "motor_result_sha256": self.result.result_sha256,
            "model": self.result.run_config.model.to_dict(),
            "intervention": self.result.run_config.to_dict()["intervention"],
            "evidence_contract_sha256": self.result.evidence_contract.sha256,
            "source_dnp01_event_count": len(self.result.source_dnp01_spike_events),
            "delivered_motor_input_count": len(self.result.delivered_motor_inputs),
            "ttmn": [
                {
                    "body_id": item.body_id,
                    "side": item.side,
                    "input_event_count": item.input_event_count,
                    "peak_state": item.peak_state,
                    "peak_step": item.peak_step,
                    "peak_time_ms": item.peak_time_ms,
                }
                for item in self.result.ttmn_trajectories
            ],
            "validation_status": "NOT_EVALUATED",
        }

    def to_dict(self) -> dict[str, Any]:
        return self.result.to_dict()


def _artifact_identity(
    *,
    upstream_artifact_id: str,
    run_config_sha256: str,
    result_sha256: str,
    evidence_contract_sha256: str,
    state_sha256: str,
) -> str:
    return _sha256_bytes(
        _json_bytes(
            {
                "artifact_schema_version": MOTOR_ARTIFACT_SCHEMA_VERSION,
                "upstream_artifact_id": upstream_artifact_id,
                "run_config_sha256": run_config_sha256,
                "result_sha256": result_sha256,
                "evidence_contract_sha256": evidence_contract_sha256,
                "motor_state_sha256": state_sha256,
            }
        )
    )


def export_motor_pathway_artifact(
    result: MotorPathwayExperimentResult,
    destination: str | Path,
) -> LoadedMotorPathwayArtifact:
    """Atomically persist a motor result and its unchanged Phase 3B parent."""

    if not isinstance(result, MotorPathwayExperimentResult):
        raise MotorArtifactSchemaError("result must be MotorPathwayExperimentResult.")
    output = Path(destination)
    if output.exists():
        raise ArtifactExportError(
            f"motor artifact output already exists: {output}; artifacts are immutable"
        )
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    except OSError as exc:
        raise ArtifactExportError(
            "could not create motor artifact staging area"
        ) from exc
    try:
        upstream_path = export_experiment_artifact(
            result.upstream_result, staging / UPSTREAM_DIRECTORY
        )
        upstream = load_experiment_artifact(upstream_path)
        state_bytes = _json_bytes(result.to_dict()) + b"\n"
        _write(staging / MOTOR_STATE_FILENAME, state_bytes)
        state_sha = _sha256_bytes(state_bytes)
        artifact_id = _artifact_identity(
            upstream_artifact_id=upstream.artifact_id,
            run_config_sha256=result.run_config.sha256,
            result_sha256=result.result_sha256,
            evidence_contract_sha256=result.evidence_contract.sha256,
            state_sha256=state_sha,
        )
        manifest = {
            "artifact_schema_version": MOTOR_ARTIFACT_SCHEMA_VERSION,
            "artifact_id": artifact_id,
            "upstream_artifact_id": upstream.artifact_id,
            "upstream_result_sha256": result.upstream_result.result_sha256,
            "upstream_config_sha256": result.upstream_result.config_sha256,
            "evidence_contract": result.evidence_contract.to_dict(),
            "evidence_contract_sha256": result.evidence_contract.sha256,
            "run_config": result.run_config.to_dict(),
            "run_config_sha256": result.run_config.sha256,
            "motor_result_sha256": result.result_sha256,
            "motor_state_file": {
                "name": MOTOR_STATE_FILENAME,
                "schema": MOTOR_RESULT_SCHEMA_VERSION,
                "bytes": len(state_bytes),
                "sha256": state_sha,
                "records": 1,
            },
            "validation_status": "NOT_EVALUATED",
        }
        _write(staging / MANIFEST_FILENAME, _json_bytes(manifest) + b"\n")
        load_motor_pathway_artifact(staging)
        try:
            os.replace(staging, output)
        except OSError as exc:
            raise ArtifactExportError("could not finalize motor artifact") from exc
        return load_motor_pathway_artifact(output)
    except (ArtifactExportError, ArtifactSchemaError, MotorArtifactError):
        raise
    except Exception as exc:
        raise ArtifactExportError("could not export motor pathway artifact") from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def _model_from_dict(value: Any) -> TTMnIntegratorConfig:
    value = _keys(
        value,
        {
            "model_id",
            "model_version",
            "assumption_set_id",
            "state_unit",
            "integration_scheme",
            "input_semantics",
            "stochastic_policy",
            "parameters",
        },
        "motor model",
    )
    if value["stochastic_policy"] != "deterministic":
        raise MotorArtifactSchemaError("motor model must be deterministic.")
    params = _keys(value["parameters"], {"tau_motor_ms", "event_gain"}, "parameters")
    parsed: dict[str, float] = {}
    for name, units in (("tau_motor_ms", "ms"), ("event_gain", "dimensionless")):
        record = _keys(
            params[name], {"value", "units", "classification"}, f"parameter {name}"
        )
        if record["units"] != units or record["classification"] != "MODEL_ASSUMPTION":
            raise MotorArtifactSchemaError("motor parameter semantics are invalid.")
        parsed[name] = _finite(record["value"], name)
    try:
        model = TTMnIntegratorConfig(
            tau_motor_ms=parsed["tau_motor_ms"],
            event_gain=parsed["event_gain"],
            model_id=value["model_id"],
            model_version=value["model_version"],
            assumption_set_id=value["assumption_set_id"],
            state_unit=value["state_unit"],
            integration_scheme=value["integration_scheme"],
            input_semantics=value["input_semantics"],
        )
    except MotorPathwayError as exc:
        raise MotorArtifactSchemaError("motor model configuration is invalid") from exc
    if model.to_dict() != value:
        raise MotorArtifactSchemaError("motor model serialization is not canonical.")
    return model


def _run_config_from_dict(value: Any) -> MotorPathwayRunConfig:
    value = _keys(
        value,
        {"schema_version", "evidence_contract_sha256", "model", "intervention"},
        "motor run config",
    )
    intervention = _keys(
        value["intervention"],
        {"id", "dnp01_to_ttmn_silenced", "semantics"},
        "motor intervention",
    )
    if intervention["semantics"] != (
        "blocks persisted DNp01 events at the motor input boundary"
    ):
        raise MotorArtifactSchemaError("unsupported motor intervention semantics.")
    try:
        parsed = MotorPathwayRunConfig(
            model=_model_from_dict(value["model"]),
            dnp01_to_ttmn_silenced=intervention["dnp01_to_ttmn_silenced"],
            evidence_contract_sha256=value["evidence_contract_sha256"],
            schema_version=value["schema_version"],
        )
    except MotorPathwayError as exc:
        raise MotorArtifactSchemaError("motor run config is invalid") from exc
    if parsed.to_dict() != value:
        raise MotorArtifactSchemaError("motor run config is not canonical.")
    return parsed


def _input_from_dict(value: Any) -> TTMnInputEvent:
    value = _keys(
        value,
        {
            "source_body_id",
            "source_node_index",
            "target_body_id",
            "step",
            "time_ms",
            "event_gain",
            "event_semantics",
        },
        "motor input event",
    )
    return TTMnInputEvent(
        source_body_id=_int(value["source_body_id"], "source_body_id"),
        source_node_index=_int(value["source_node_index"], "source_node_index"),
        target_body_id=_int(value["target_body_id"], "target_body_id"),
        step=_int(value["step"], "step"),
        time_ms=_finite(value["time_ms"], "time_ms"),
        event_gain=_finite(value["event_gain"], "event_gain"),
        event_semantics=value["event_semantics"],
    )


def _trajectory_from_dict(value: Any) -> TTMnStateTrajectory:
    value = _keys(
        value,
        {
            "body_id",
            "neuron_type",
            "side",
            "state_unit",
            "times_ms",
            "state",
            "input_event_count",
            "peak_state",
            "peak_step",
            "peak_time_ms",
        },
        "TTMn trajectory",
    )
    if value["state_unit"] != "dimensionless":
        raise MotorArtifactSchemaError("TTMn state must be dimensionless.")
    return TTMnStateTrajectory(
        body_id=_int(value["body_id"], "body_id"),
        neuron_type=value["neuron_type"],
        side=value["side"],
        times_ms=tuple(_finite(item, "times_ms") for item in value["times_ms"]),
        state=tuple(_finite(item, "state") for item in value["state"]),
        input_event_count=_int(value["input_event_count"], "input_event_count"),
        peak_state=_finite(value["peak_state"], "peak_state"),
        peak_step=_int(value["peak_step"], "peak_step"),
        peak_time_ms=_finite(value["peak_time_ms"], "peak_time_ms"),
    )


def _sensitivity_from_dict(value: Any) -> MotorSensitivityPoint:
    value = _keys(
        value,
        {
            "tau_motor_ms",
            "event_gain",
            "parameter_classification",
            "peak_state_by_body_id",
            "peak_step_by_body_id",
            "delivered_event_count",
        },
        "motor sensitivity point",
    )
    if value["parameter_classification"] != "MODEL_ASSUMPTION":
        raise MotorArtifactSchemaError("sensitivity parameters must be assumptions.")
    peaks = tuple(
        (
            _int(
                _keys(item, {"body_id", "peak_state"}, "sensitivity peak")["body_id"],
                "body_id",
            ),
            _finite(item["peak_state"], "peak_state"),
        )
        for item in value["peak_state_by_body_id"]
    )
    peak_steps = tuple(
        (
            _int(
                _keys(item, {"body_id", "peak_step"}, "sensitivity peak step")[
                    "body_id"
                ],
                "body_id",
            ),
            _int(item["peak_step"], "peak_step"),
        )
        for item in value["peak_step_by_body_id"]
    )
    return MotorSensitivityPoint(
        tau_motor_ms=_finite(value["tau_motor_ms"], "tau_motor_ms"),
        event_gain=_finite(value["event_gain"], "event_gain"),
        peak_state_by_body_id=peaks,
        peak_step_by_body_id=peak_steps,
        delivered_event_count=_int(
            value["delivered_event_count"], "delivered_event_count"
        ),
    )


def _validate_motor_payload(
    value: Any,
    *,
    upstream_result: ExperimentResult,
) -> MotorPathwayExperimentResult:
    value = _keys(
        value,
        {
            "schema_version",
            "upstream_config_sha256",
            "upstream_result_sha256",
            "evidence_contract",
            "evidence_contract_sha256",
            "run_config",
            "run_config_sha256",
            "source_dnp01_spike_events",
            "delivered_motor_inputs",
            "ttmn_model_state",
            "sensitivity",
            "output_semantics",
            "validation_status",
            "result_sha256",
        },
        "motor state payload",
    )
    if (
        value["schema_version"] != MOTOR_RESULT_SCHEMA_VERSION
        or value["output_semantics"] != "SIMULATED_EXPLORATORY_TTMN_MODEL_STATE"
        or value["validation_status"] != "NOT_EVALUATED"
    ):
        raise MotorArtifactSchemaError("unsupported motor output semantics.")
    evidence = value["evidence_contract"]
    if evidence != MOTOR_PATHWAY_EVIDENCE.to_dict():
        raise MotorArtifactIntegrityError(
            "motor evidence differs from the pinned contract."
        )
    if value["evidence_contract_sha256"] != MOTOR_PATHWAY_EVIDENCE.sha256:
        raise MotorArtifactIntegrityError("motor evidence digest mismatch.")
    run_config = _run_config_from_dict(value["run_config"])
    if value["run_config_sha256"] != run_config.sha256:
        raise MotorArtifactIntegrityError("motor run configuration digest mismatch.")
    if value["upstream_config_sha256"] != upstream_result.config_sha256:
        raise MotorArtifactIntegrityError("upstream config digest mismatch.")
    if value["upstream_result_sha256"] != upstream_result.result_sha256:
        raise MotorArtifactIntegrityError("upstream result digest mismatch.")
    expected_source = [
        {
            "body_id": item.body_id,
            "node_index": item.node_index,
            "step": item.step,
            "time_ms": item.time_ms,
            "neuron_type": item.neuron_type,
        }
        for item in upstream_result.spike_events
        if item.neuron_type == "DNp01"
    ]
    if value["source_dnp01_spike_events"] != expected_source:
        raise MotorArtifactIntegrityError("source DNp01 events differ from parent run.")
    try:
        result = MotorPathwayExperimentResult(
            upstream_result=upstream_result,
            run_config=run_config,
            evidence_contract=MOTOR_PATHWAY_EVIDENCE,
            source_dnp01_spike_events=tuple(
                item
                for item in upstream_result.spike_events
                if item.neuron_type == "DNp01"
            ),
            delivered_motor_inputs=tuple(
                _input_from_dict(item) for item in value["delivered_motor_inputs"]
            ),
            ttmn_trajectories=tuple(
                _trajectory_from_dict(item) for item in value["ttmn_model_state"]
            ),
            sensitivity=tuple(
                _sensitivity_from_dict(item) for item in value["sensitivity"]
            ),
        )
    except MotorPathwayError as exc:
        raise MotorArtifactIntegrityError(
            "motor state failed model validation"
        ) from exc
    if result.result_sha256 != value["result_sha256"]:
        raise MotorArtifactIntegrityError("motor result digest mismatch.")
    if result.to_dict() != value:
        raise MotorArtifactIntegrityError("motor result is not canonical.")
    return result


def load_motor_pathway_artifact(path: str | Path) -> LoadedMotorPathwayArtifact:
    """Load, verify, and reconstruct a motor artifact without simulating."""

    root = Path(path)
    if not root.is_dir() or root.is_symlink():
        raise MotorArtifactNotFoundError("motor artifact directory was not found.")
    try:
        entries = tuple(root.iterdir())
    except OSError:
        raise MotorArtifactIntegrityError(
            "could not enumerate motor artifact"
        ) from None
    expected_names = {MANIFEST_FILENAME, MOTOR_STATE_FILENAME, UPSTREAM_DIRECTORY}
    if {item.name for item in entries} != expected_names or any(
        item.is_symlink() for item in entries
    ):
        raise MotorArtifactIntegrityError("motor artifact file set is invalid.")
    manifest = _read_json(root / MANIFEST_FILENAME, "motor manifest")
    _keys(
        manifest,
        {
            "artifact_schema_version",
            "artifact_id",
            "upstream_artifact_id",
            "upstream_result_sha256",
            "upstream_config_sha256",
            "evidence_contract",
            "evidence_contract_sha256",
            "run_config",
            "run_config_sha256",
            "motor_result_sha256",
            "motor_state_file",
            "validation_status",
        },
        "motor manifest",
    )
    if manifest["artifact_schema_version"] != MOTOR_ARTIFACT_SCHEMA_VERSION:
        raise MotorArtifactSchemaError("unsupported motor artifact schema.")
    if manifest["validation_status"] != "NOT_EVALUATED":
        raise MotorArtifactSchemaError("motor artifact cannot claim validation.")
    state_record = _keys(
        manifest["motor_state_file"],
        {"name", "schema", "bytes", "sha256", "records"},
        "motor state file record",
    )
    if (
        state_record["name"] != MOTOR_STATE_FILENAME
        or state_record["schema"] != MOTOR_RESULT_SCHEMA_VERSION
        or state_record["records"] != 1
    ):
        raise MotorArtifactSchemaError("motor payload file metadata is invalid.")
    state_path = root / MOTOR_STATE_FILENAME
    if state_path.stat().st_size != state_record["bytes"]:
        raise MotorArtifactIntegrityError("motor state byte count mismatch.")
    if _sha256_file(state_path) != state_record["sha256"]:
        raise MotorArtifactIntegrityError("motor state payload digest mismatch.")
    upstream = load_experiment_artifact(root / UPSTREAM_DIRECTORY)
    if upstream.artifact_id != manifest["upstream_artifact_id"]:
        raise MotorArtifactIntegrityError("upstream artifact identity mismatch.")
    motor_result = _validate_motor_payload(
        _read_json(state_path, "motor state"), upstream_result=upstream.result
    )
    if (
        motor_result.result_sha256 != manifest["motor_result_sha256"]
        or motor_result.upstream_result.result_sha256
        != manifest["upstream_result_sha256"]
        or motor_result.upstream_result.config_sha256
        != manifest["upstream_config_sha256"]
        or motor_result.evidence_contract.to_dict() != manifest["evidence_contract"]
        or motor_result.run_config.to_dict() != manifest["run_config"]
        or motor_result.evidence_contract.sha256 != manifest["evidence_contract_sha256"]
        or motor_result.run_config.sha256 != manifest["run_config_sha256"]
    ):
        raise MotorArtifactIntegrityError("motor manifest and payload differ.")
    expected_id = _artifact_identity(
        upstream_artifact_id=upstream.artifact_id,
        run_config_sha256=motor_result.run_config.sha256,
        result_sha256=motor_result.result_sha256,
        evidence_contract_sha256=motor_result.evidence_contract.sha256,
        state_sha256=state_record["sha256"],
    )
    if manifest["artifact_id"] != expected_id:
        raise MotorArtifactIntegrityError("motor artifact identity mismatch.")
    return LoadedMotorPathwayArtifact(
        path=root,
        artifact_id=expected_id,
        upstream_artifact=upstream,
        result=motor_result,
        manifest=MappingProxyType(manifest),
    )


def replay_motor_pathway_artifact(
    path: str | Path,
    circuit_contract: Any,
) -> MotorPathwayExperimentResult:
    """Replay a complete motor artifact from its stored base configuration."""

    from neurofly.motor_pathway import MotorPathwayExperimentRunner

    artifact = load_motor_pathway_artifact(path)
    runner = MotorPathwayExperimentRunner(circuit_contract)
    replayed = runner.run(
        artifact.upstream_artifact.result.config,
        artifact.result.run_config,
    )
    if replayed.result_sha256 != artifact.result.result_sha256:
        raise MotorArtifactIntegrityError("motor artifact replay differs from source.")
    return replayed


class MotorPathwayArtifactStore:
    """Read-only ID lookup for a dedicated bounded motor artifact root."""

    def __init__(self, root: str | Path) -> None:
        configured = Path(root)
        if not configured.exists() or not configured.is_dir():
            raise MotorArtifactIntegrityError("motor artifact root is unavailable.")
        self._root = configured.resolve()

    def _all_loaded(self) -> tuple[LoadedMotorPathwayArtifact, ...]:
        try:
            children = tuple(sorted(self._root.iterdir(), key=lambda item: item.name))
        except OSError:
            raise MotorArtifactIntegrityError(
                "could not enumerate motor artifact root"
            ) from None
        loaded: list[LoadedMotorPathwayArtifact] = []
        for child in children:
            if child.is_symlink():
                raise MotorArtifactIntegrityError(
                    "symlink motor artifact is not allowed"
                )
            if not child.is_dir():
                continue
            artifact = load_motor_pathway_artifact(child)
            loaded.append(artifact)
        ids = [item.artifact_id for item in loaded]
        if len(ids) != len(set(ids)):
            raise MotorArtifactIntegrityError("duplicate motor artifact identity")
        return tuple(loaded)

    def discover_artifact_ids(self) -> tuple[str, ...]:
        return tuple(item.artifact_id for item in self._all_loaded())

    def get(self, artifact_id: str) -> LoadedMotorPathwayArtifact:
        if (
            not isinstance(artifact_id, str)
            or re.fullmatch(r"[0-9a-f]{64}", artifact_id) is None
        ):
            raise InvalidMotorArtifactIdError("motor artifact ID is malformed")
        for artifact in self._all_loaded():
            if artifact.artifact_id == artifact_id:
                return artifact
        raise MotorArtifactNotFoundError("motor artifact was not found")


__all__ = [
    "MOTOR_ARTIFACT_SCHEMA_VERSION",
    "MOTOR_STATE_FILENAME",
    "LoadedMotorPathwayArtifact",
    "MotorArtifactError",
    "MotorArtifactIntegrityError",
    "MotorArtifactNotFoundError",
    "MotorArtifactSchemaError",
    "InvalidMotorArtifactIdError",
    "MotorPathwayArtifactStore",
    "export_motor_pathway_artifact",
    "load_motor_pathway_artifact",
    "replay_motor_pathway_artifact",
]
