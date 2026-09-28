"""Provenance-preserving adapter from persisted Phase 7O events to Phase 6C.

This is a narrow production composition boundary, not an external-event API.
It re-loads a content-addressed Phase 7O artifact and adapts only the
``simulated_spikes`` records persisted for one explicitly selected condition.
No state or drive field is used to infer events.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping
from typing import Any

from neurofly.malecns.contract import CircuitContract
from neurofly.motor_pathway import (
    MOTOR_PATHWAY_EVIDENCE,
    TTMnIntegratorConfig,
    _integrate_ttmn,
    _map_motor_inputs,
)
from neurofly.relative_column_assignment import (
    RelativeColumnAssignmentSource,
    canonical_json_bytes,
)
from neurofly.sensory_population_execution_artifacts import (
    LoadedExecutionArtifact,
    load_execution_artifact,
)
from neurofly.sensory_population_readiness import (
    _circuit_identity,
    load_phase7n_sources,
)
from neurofly.simulation import SpikeEvent

CONFIG_SCHEMA = "sensory_dnp01_ttmn_adapter_config_v1"
RESULT_SCHEMA = "sensory_dnp01_ttmn_adapter_result_v1"
ARTIFACT_SCHEMA = "sensory_dnp01_ttmn_adapter_artifact_v1"
SOURCE_KIND = "SIMULATED_FROM_SENSORY_EXPERIMENT"
SPIKE_SEMANTICS = "SIMULATED_DNP01_MODEL_SPIKE"
PHASE7O_ARTIFACT_ID = "99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5"
REFERENCE_CONDITION_ID = "reference_bilateral"
PHASE7O_TIME_ALIGNMENT = "state_boundary_n_drives_interval_n_to_n_plus_1"
MOTOR_TIME_ALIGNMENT = "event_step_is_ttmn_state_boundary_v1"


class SensoryDnp01MotorAdapterError(ValueError):
    """Invalid source artifact, condition, event provenance, or motor result."""


def _sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SensoryDnp01MotorAdapterError(f"{label} must be a finite number.")
    result = float(value)
    if not math.isfinite(result):
        raise SensoryDnp01MotorAdapterError(f"{label} must be a finite number.")
    return result


def _exact_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise SensoryDnp01MotorAdapterError(
            f"{label} must be an integer of at least {minimum}."
        )
    return value


def _condition_by_id(
    artifact: LoadedExecutionArtifact, condition_id: str
) -> dict[str, Any]:
    if not isinstance(condition_id, str) or not condition_id:
        raise SensoryDnp01MotorAdapterError("an explicit source condition is required.")
    condition_ids = artifact.config.get("condition_ids")
    conditions = artifact.result.get("conditions")
    if (
        not isinstance(condition_ids, list)
        or not isinstance(conditions, list)
        or artifact.result.get("condition_count") != len(conditions)
        or condition_ids != [row.get("condition_id") for row in conditions]
    ):
        raise SensoryDnp01MotorAdapterError(
            "Phase 7O condition manifest/result identity is inconsistent."
        )
    matches = [row for row in conditions if row.get("condition_id") == condition_id]
    if len(matches) != 1:
        raise SensoryDnp01MotorAdapterError(
            "the selected Phase 7O condition is missing or duplicated."
        )
    return matches[0]


def _verify_source(
    artifact: LoadedExecutionArtifact,
    circuit_contract: CircuitContract,
    source_identity: Mapping[str, Any],
) -> None:
    """Bind the persisted run to the exact locally validated source contracts."""

    if artifact.config.get("schema") != "sensory_population_311_experiment_config_v1":
        raise SensoryDnp01MotorAdapterError("unsupported Phase 7O config schema.")
    if artifact.config.get("artifact_schema") != (
        "sensory_population_311_experiment_artifact_v1"
    ):
        raise SensoryDnp01MotorAdapterError("unsupported Phase 7O artifact schema.")
    if artifact.result.get("schema") != "sensory_population_311_experiment_result_v1":
        raise SensoryDnp01MotorAdapterError("unsupported Phase 7O result schema.")
    expected_circuit = _circuit_identity(circuit_contract)
    if artifact.config.get("circuit_contract_identity") != expected_circuit:
        raise SensoryDnp01MotorAdapterError(
            "Phase 7O CircuitContract identity differs from local source."
        )
    if artifact.config.get("source_contract_identity") != dict(source_identity):
        raise SensoryDnp01MotorAdapterError(
            "Phase 7O body-column source identity differs from local source."
        )
    try:
        MOTOR_PATHWAY_EVIDENCE.validate_upstream_contract(circuit_contract)
    except ValueError as exc:
        raise SensoryDnp01MotorAdapterError(
            "Phase 6C routing evidence does not match the local CircuitContract."
        ) from exc
    if artifact.config.get("time_alignment") != PHASE7O_TIME_ALIGNMENT:
        raise SensoryDnp01MotorAdapterError("unsupported Phase 7O time alignment.")
    model_hash = artifact.config.get("model_config_sha256")
    if (
        not isinstance(model_hash, str)
        or len(model_hash) != 64
        or any(char not in "0123456789abcdef" for char in model_hash)
    ):
        raise SensoryDnp01MotorAdapterError("Phase 7O model config hash is invalid.")


def _extract_condition_events(
    condition: Mapping[str, Any], *, dt_ms: float, circuit_contract: CircuitContract
) -> tuple[SpikeEvent, ...]:
    """Validate and convert exactly the persisted event records in one condition."""

    interval_count = _exact_int(condition.get("interval_count"), "interval_count")
    if interval_count < 1:
        raise SensoryDnp01MotorAdapterError("source condition has no update intervals.")
    if condition.get("time_alignment") != (
        "sensory_state_boundary_n_drives_interval_n_to_n_plus_1"
    ):
        raise SensoryDnp01MotorAdapterError("source condition timing semantics differ.")
    if _finite_number(condition.get("dt_ms"), "condition dt_ms") != dt_ms:
        raise SensoryDnp01MotorAdapterError("source condition dt differs from its run.")
    targets = condition.get("targets")
    if not isinstance(targets, list):
        raise SensoryDnp01MotorAdapterError("source condition targets are malformed.")
    expected_bodies = set(MOTOR_PATHWAY_EVIDENCE.target_by_source)
    if (
        len(targets) != len(expected_bodies)
        or {row.get("body_id") for row in targets if isinstance(row, dict)}
        != expected_bodies
    ):
        raise SensoryDnp01MotorAdapterError(
            "source condition does not contain exactly the two DNp01 bodies."
        )

    neurons = circuit_contract.neurons_by_body_id
    event_records: list[tuple[int, int, float, str]] = []
    seen: set[tuple[int, int]] = set()
    for target in targets:
        if not isinstance(target, dict):
            raise SensoryDnp01MotorAdapterError("source target record is malformed.")
        body_id = target.get("body_id")
        expected_side = {10001: "R", 10010: "L"}.get(body_id)
        neuron = neurons.get(body_id) if isinstance(body_id, int) else None
        if (
            expected_side is None
            or neuron is None
            or neuron.type != "DNp01"
            or neuron.soma_side != expected_side
            or target.get("side") != expected_side
        ):
            raise SensoryDnp01MotorAdapterError(
                "source DNp01 body/side identity differs from the pinned contract."
            )
        records = target.get("simulated_spikes")
        if not isinstance(records, list):
            raise SensoryDnp01MotorAdapterError("persisted spike list is malformed.")
        for record in records:
            if not isinstance(record, dict) or set(record) != {
                "body_id",
                "step",
                "time_ms",
                "semantics",
            }:
                raise SensoryDnp01MotorAdapterError(
                    "event is not an exact persisted Phase 7O spike record."
                )
            source_body_id = record["body_id"]
            step = _exact_int(record["step"], "event step", minimum=1)
            time_ms = _finite_number(record["time_ms"], "event time_ms")
            if (
                source_body_id != body_id
                or step > interval_count
                or record["semantics"] != SPIKE_SEMANTICS
                or time_ms != step * dt_ms
            ):
                raise SensoryDnp01MotorAdapterError(
                    "persisted Phase 7O event identity/timing is inconsistent."
                )
            key = (body_id, step)
            if key in seen:
                raise SensoryDnp01MotorAdapterError(
                    "duplicate DNp01 body/step event in source condition."
                )
            seen.add(key)
            event_records.append((step, body_id, time_ms, neuron.type))
    event_records.sort(key=lambda row: (row[0], row[1]))
    return tuple(
        SpikeEvent(
            time_ms=time_ms,
            step=step,
            body_id=body_id,
            node_index=circuit_contract.node_index_by_body_id[body_id],
            neuron_type=neuron_type,
        )
        for step, body_id, time_ms, neuron_type in event_records
    )


def _persisted_event_records(condition: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for target in condition["targets"]:
        for record in target["simulated_spikes"]:
            rows.append(dict(record))
    return sorted(rows, key=lambda row: (row["step"], row["body_id"]))


def _all_condition_audit(
    artifact: LoadedExecutionArtifact, circuit_contract: CircuitContract
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for condition_id in artifact.config["condition_ids"]:
        condition = _condition_by_id(artifact, condition_id)
        dt_ms = _finite_number(condition.get("dt_ms"), "condition dt_ms")
        events = _extract_condition_events(
            condition, dt_ms=dt_ms, circuit_contract=circuit_contract
        )
        records = _persisted_event_records(condition)
        rows.append(
            {
                "condition_id": condition_id,
                "event_count": len(events),
                "source_event_records_sha256": _sha256(records),
            }
        )
    return rows


def _route_records() -> list[dict[str, Any]]:
    source_by_id = {
        row["body_id"]: row for row in MOTOR_PATHWAY_EVIDENCE.dnp01_identities
    }
    target_by_id = {
        row["body_id"]: row for row in MOTOR_PATHWAY_EVIDENCE.ttmn_identities
    }
    return [
        {
            "source_body_id": edge["pre_body_id"],
            "source_type": source_by_id[edge["pre_body_id"]]["type"],
            "source_side": source_by_id[edge["pre_body_id"]]["side"],
            "source_node_index": source_by_id[edge["pre_body_id"]]["node_index"],
            "target_body_id": edge["post_body_id"],
            "target_type": target_by_id[edge["post_body_id"]]["type"],
            "target_side": target_by_id[edge["post_body_id"]]["side"],
            "structural_weight": edge["structural_weight"],
            "structural_weight_semantics": "SOURCE_STRUCTURAL_COUNT_ONLY",
        }
        for edge in MOTOR_PATHWAY_EVIDENCE.chemical_edges
    ]


def _build_payload_from_loaded(
    artifact: LoadedExecutionArtifact,
    condition_id: str,
    circuit_contract: CircuitContract,
    source_identity: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    _verify_source(artifact, circuit_contract, source_identity)
    condition = _condition_by_id(artifact, condition_id)
    dt_ms = _finite_number(condition.get("dt_ms"), "condition dt_ms")
    interval_count = _exact_int(condition.get("interval_count"), "interval_count")
    events = _extract_condition_events(
        condition, dt_ms=dt_ms, circuit_contract=circuit_contract
    )
    source_records = _persisted_event_records(condition)
    adapted = [
        {
            "source_kind": SOURCE_KIND,
            "upstream_artifact_id": artifact.artifact_id,
            "source_condition_id": condition_id,
            "body_id": event.body_id,
            "side": circuit_contract.neurons_by_body_id[event.body_id].soma_side,
            "node_index": event.node_index,
            "neuron_type": event.neuron_type,
            "step": event.step,
            "time_ms": event.time_ms,
            "event_semantics": SPIKE_SEMANTICS,
        }
        for event in events
    ]
    motor_model = TTMnIntegratorConfig()
    inputs = _map_motor_inputs(
        events,
        dt_ms=dt_ms,
        steps=interval_count,
        model=motor_model,
        evidence_contract=MOTOR_PATHWAY_EVIDENCE,
    )
    times_ms = tuple(step * dt_ms for step in range(interval_count + 1))
    trajectories = _integrate_ttmn(
        times_ms=times_ms,
        dt_ms=dt_ms,
        inputs=inputs,
        model=motor_model,
        evidence_contract=MOTOR_PATHWAY_EVIDENCE,
    )
    condition_audit = _all_condition_audit(artifact, circuit_contract)
    config: dict[str, Any] = {
        "schema": CONFIG_SCHEMA,
        "artifact_schema": ARTIFACT_SCHEMA,
        "source_kind": SOURCE_KIND,
        "upstream_artifact": {
            "artifact_schema": artifact.manifest["artifact_schema"],
            "artifact_id": artifact.artifact_id,
            "config_sha256": artifact.manifest["config_sha256"],
            "result_sha256": artifact.manifest["result_sha256"],
            "phase7o_model_config_sha256": artifact.config["model_config_sha256"],
        },
        "source_condition_id": condition_id,
        "source_contract_identity": dict(source_identity),
        "circuit_contract_identity": _circuit_identity(circuit_contract),
        "source_event_records_sha256": _sha256(source_records),
        "source_event_count": len(events),
        "time_grid": {
            "dt_ms": dt_ms,
            "interval_count": interval_count,
            "boundary_count": interval_count + 1,
            "source_alignment": PHASE7O_TIME_ALIGNMENT,
            "motor_alignment": MOTOR_TIME_ALIGNMENT,
            "additional_transmission_delay_ms": 0.0,
        },
        "routing_evidence_contract": MOTOR_PATHWAY_EVIDENCE.to_dict(),
        "routing_evidence_contract_sha256": MOTOR_PATHWAY_EVIDENCE.sha256,
        "verified_routes": _route_records(),
        "motor_model": motor_model.to_dict(),
        "population_normalization": "none",
        "structural_weight_numerical_use": "none_source_metadata_only",
        "fallback_policy": {
            "voltage_to_event": False,
            "external_drive_to_event": False,
            "filtered_state_to_event": False,
            "synthetic_event_fallback": False,
        },
        "provenance_semantics": (
            "only persisted Phase 7O simulated DNp01 spikes from the selected "
            "condition are adapted"
        ),
        "scientific_boundary": {
            "sensory_and_dnp01_state": "EXPLORATORY_MODEL_OUTPUT",
            "event": SPIKE_SEMANTICS,
            "source_kind": SOURCE_KIND,
            "route": "MALECNS_STRUCTURAL_EVIDENCE",
            "ttmn_state": "DIMENSIONLESS_EXPLORATORY_MOTOR_NEURAL_STATE",
            "structural_count": "SOURCE_METADATA_ONLY",
            "muscle_or_behavior_model": False,
            "phase8b_synthetic_provenance_in_chain": False,
        },
    }
    config["config_sha256"] = _sha256(config)
    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "source_kind": SOURCE_KIND,
        "routing_evidence_contract_sha256": MOTOR_PATHWAY_EVIDENCE.sha256,
        "upstream_artifact_id": artifact.artifact_id,
        "source_condition_id": condition_id,
        "source_event_records": source_records,
        "adapted_dnp01_events": adapted,
        "event_count": len(adapted),
        "mapped_motor_inputs": [item.to_dict() for item in inputs],
        "ttmn_model_state": [item.to_dict() for item in trajectories],
        "all_condition_event_audit": condition_audit,
        "all_conditions_zero_events": all(
            row["event_count"] == 0 for row in condition_audit
        ),
        "selected_condition_zero_events": len(adapted) == 0,
        "zero_event_is_valid_result": True,
        "voltage_or_drive_fallback_used": False,
        "synthetic_fallback_used": False,
        "time_alignment": MOTOR_TIME_ALIGNMENT,
        "output_semantics": "SIMULATED_EXPLORATORY_TTMN_MODEL_STATE",
        "validation_status": "PASSED",
    }
    result["result_sha256"] = _sha256(result)
    return config, result


def build_sensory_dnp01_motor_payload(
    upstream_artifact: LoadedExecutionArtifact,
    condition_id: str,
    circuit_contract: CircuitContract,
    source_contract: RelativeColumnAssignmentSource,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build a payload only after reloading and matching its persisted source.

    This public entry still cannot accept caller-mutated event data: the
    artifact is re-read from its content-addressed directory and compared to
    the supplied loaded object before any event is extracted.
    """

    if not isinstance(source_contract, RelativeColumnAssignmentSource):
        raise SensoryDnp01MotorAdapterError(
            "a validated body-column source contract is required."
        )
    try:
        reloaded = load_execution_artifact(upstream_artifact.path)
        pinned_source, pinned_circuit, _grid = load_phase7n_sources(
            source_contract.source_root
        )
    except (OSError, ValueError) as exc:
        raise SensoryDnp01MotorAdapterError(
            "persisted Phase 7O/source contracts could not be revalidated."
        ) from exc
    if (
        reloaded.artifact_id != upstream_artifact.artifact_id
        or reloaded.config != upstream_artifact.config
        or reloaded.result != upstream_artifact.result
        or reloaded.manifest != upstream_artifact.manifest
    ):
        raise SensoryDnp01MotorAdapterError(
            "in-memory Phase 7O source differs from its persisted artifact."
        )
    if dict(pinned_source.source_identity) != dict(
        source_contract.source_identity
    ) or _circuit_identity(pinned_circuit) != _circuit_identity(circuit_contract):
        raise SensoryDnp01MotorAdapterError(
            "supplied source contracts differ from their pinned local sources."
        )
    return _build_payload_from_loaded(
        reloaded,
        condition_id,
        pinned_circuit,
        pinned_source.source_identity,
    )


def phase7o_canonical_zero_event_assertion(
    artifact: LoadedExecutionArtifact,
) -> dict[str, Any]:
    """Return the canonical-zero audit without imposing it on generic runs."""

    if artifact.artifact_id != PHASE7O_ARTIFACT_ID:
        raise SensoryDnp01MotorAdapterError(
            "canonical zero-event assertion requires the pinned Phase 7O artifact."
        )
    condition = _condition_by_id(artifact, REFERENCE_CONDITION_ID)
    events = sum(len(row["simulated_spikes"]) for row in condition["targets"])
    all_events = sum(
        len(row["simulated_spikes"])
        for source_condition in artifact.result["conditions"]
        for row in source_condition["targets"]
    )
    if events != 0 or all_events != 0:
        raise SensoryDnp01MotorAdapterError(
            "canonical Phase 7O zero-event regression changed."
        )
    return {
        "artifact_id": artifact.artifact_id,
        "reference_condition_id": REFERENCE_CONDITION_ID,
        "reference_event_count": events,
        "condition_count": artifact.result["condition_count"],
        "all_condition_event_count": all_events,
        "all_conditions_event_free": True,
    }


__all__ = [
    "ARTIFACT_SCHEMA",
    "CONFIG_SCHEMA",
    "PHASE7O_ARTIFACT_ID",
    "REFERENCE_CONDITION_ID",
    "RESULT_SCHEMA",
    "SOURCE_KIND",
    "SensoryDnp01MotorAdapterError",
    "build_sensory_dnp01_motor_payload",
    "phase7o_canonical_zero_event_assertion",
]
