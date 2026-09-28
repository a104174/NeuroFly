"""Production adapter from persisted Phase 7O DNp01 events to the Phase 8G relay.

Only stored simulated DNp01 spike records from one explicitly selected,
integrity-validated Phase 7O condition enter the shared two-layer route core.
No voltage, drive, filtered state, or synthetic fixture can supply events.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping
from typing import Any

from neurofly.malecns.contract import CircuitContract
from neurofly.psi_dlmn_event_relay import (
    ACTIVE_ROUTE_POLICY_ID,
    RELAY_SEMANTICS,
    SENSORY_SOURCE_KIND,
    PsiDlmnEventRelayError,
    _contract_reference,
    _propagate_origin_events,
    active_edge_policy_from_contract,
    active_routes_from_contract,
    load_pinned_motor_contract,
)
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    RelativeColumnAssignmentSource,
    canonical_json_bytes,
)
from neurofly.sensory_dnp01_motor_adapter import (
    PHASE7O_TIME_ALIGNMENT,
    SPIKE_SEMANTICS,
    SensoryDnp01MotorAdapterError,
    _condition_by_id,
    _extract_condition_events,
    _persisted_event_records,
    _verify_source,
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

CONFIG_SCHEMA = "sensory_psi_dlmn_event_relay_config_v1"
RESULT_SCHEMA = "sensory_psi_dlmn_event_relay_result_v1"
ARTIFACT_SCHEMA = "sensory_psi_dlmn_event_relay_artifact_v1"
ORIGIN_EVENT_SCHEMA = "phase7o_dnp01_spike_origin_v1"
DEFAULT_OUTPUT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA
TIME_ALIGNMENT = "zero_added_delay_same_integer_boundary_v1"


class SensoryPsiDlmnEventAdapterError(ValueError):
    """Invalid Phase 7O source, condition, topology, or relay provenance."""


def _sha256(value: Any) -> str:
    try:
        return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    except (TypeError, ValueError) as exc:
        raise SensoryPsiDlmnEventAdapterError(
            "value is not deterministic JSON"
        ) from exc


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SensoryPsiDlmnEventAdapterError(f"{label} must be finite numeric data")
    result = float(value)
    if not math.isfinite(result):
        raise SensoryPsiDlmnEventAdapterError(f"{label} must be finite numeric data")
    return result


def _exact_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise SensoryPsiDlmnEventAdapterError(
            f"{label} must be an integer of at least {minimum}"
        )
    return value


def _origin_event_records(
    artifact: LoadedExecutionArtifact,
    condition_id: str,
    condition: Mapping[str, Any],
    events: tuple[SpikeEvent, ...],
    circuit_contract: CircuitContract,
) -> list[dict[str, Any]]:
    persisted = _persisted_event_records(condition)
    event_by_identity = {(event.body_id, event.step): event for event in events}
    if len(event_by_identity) != len(events) or len(persisted) != len(events):
        raise SensoryPsiDlmnEventAdapterError(
            "persisted event list differs from validated Phase 7O events"
        )
    records: list[dict[str, Any]] = []
    for stored in persisted:
        event = event_by_identity.get((stored["body_id"], stored["step"]))
        if (
            event is None
            or stored.get("time_ms") != event.time_ms
            or stored.get("semantics") != SPIKE_SEMANTICS
        ):
            raise SensoryPsiDlmnEventAdapterError(
                "persisted event changed during extraction"
            )
        source_neuron = circuit_contract.neurons_by_body_id[event.body_id]
        event_identity = {
            "schema_version": ORIGIN_EVENT_SCHEMA,
            "source_artifact_id": artifact.artifact_id,
            "source_condition_id": condition_id,
            "persisted_spike_record": stored,
            "node_index": event.node_index,
            "neuron_type": event.neuron_type,
            "side": source_neuron.soma_side,
        }
        origin_event_id = f"{ORIGIN_EVENT_SCHEMA}:{_sha256(event_identity)}"
        records.append(
            {
                "source_kind": SENSORY_SOURCE_KIND,
                "event_id": origin_event_id,
                "source_body_id": event.body_id,
                "source_side": source_neuron.soma_side,
                "source_node_index": event.node_index,
                "neuron_type": event.neuron_type,
                "step": event.step,
                "time_ms": event.time_ms,
                "event_semantics": SPIKE_SEMANTICS,
                "upstream_artifact_id": artifact.artifact_id,
                "source_condition_id": condition_id,
                "spike_event": {
                    "body_id": event.body_id,
                    "node_index": event.node_index,
                    "neuron_type": event.neuron_type,
                    "step": event.step,
                    "time_ms": event.time_ms,
                    "semantics": SPIKE_SEMANTICS,
                },
            }
        )
    return records


def _relay_condition(
    artifact: LoadedExecutionArtifact,
    condition_id: str,
    condition: Mapping[str, Any],
    circuit_contract: CircuitContract,
    routes: tuple[Any, ...],
    contract_reference: dict[str, Any],
) -> tuple[tuple[SpikeEvent, ...], list[dict[str, Any]], dict[str, Any]]:
    dt_ms = _finite_number(condition.get("dt_ms"), "condition dt_ms")
    interval_count = _exact_int(condition.get("interval_count"), "interval_count")
    events = _extract_condition_events(
        condition, dt_ms=dt_ms, circuit_contract=circuit_contract
    )
    source_events = _origin_event_records(
        artifact, condition_id, condition, events, circuit_contract
    )
    identity = {
        "upstream_artifact_id": artifact.artifact_id,
        "source_condition_id": condition_id,
    }
    try:
        relay = _propagate_origin_events(
            source_events,
            routes,
            contract_reference,
            source_kind=SENSORY_SOURCE_KIND,
            origin_identity=identity,
            context_fields=identity,
            dt_ms=dt_ms,
            maximum_step=interval_count,
        )
    except PsiDlmnEventRelayError as exc:
        raise SensoryPsiDlmnEventAdapterError(
            "validated Phase 7O events failed the shared relay contract"
        ) from exc
    return events, _persisted_event_records(condition), relay


def _build_payload_from_loaded(
    artifact: LoadedExecutionArtifact,
    condition_id: str,
    circuit_contract: CircuitContract,
    source_identity: Mapping[str, Any],
    pinned_motor_contract: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build after callers have loaded immutable sources; used for replay/tests."""

    _verify_source(artifact, circuit_contract, source_identity)
    if artifact.manifest.get("artifact_id") != artifact.artifact_id:
        raise SensoryPsiDlmnEventAdapterError("Phase 7O artifact identity mismatch")
    routes = active_routes_from_contract(pinned_motor_contract)
    policy = active_edge_policy_from_contract(pinned_motor_contract)
    contract_reference = _contract_reference(pinned_motor_contract)
    selected = _condition_by_id(artifact, condition_id)
    selected_events, source_records, selected_relay = _relay_condition(
        artifact,
        condition_id,
        selected,
        circuit_contract,
        routes,
        contract_reference,
    )
    selected_dt_ms = _finite_number(selected.get("dt_ms"), "condition dt_ms")
    selected_interval_count = _exact_int(
        selected.get("interval_count"), "interval_count"
    )

    condition_audit: list[dict[str, Any]] = []
    condition_ids = artifact.config.get("condition_ids")
    if not isinstance(condition_ids, list) or len(condition_ids) != len(
        set(condition_ids)
    ):
        raise SensoryPsiDlmnEventAdapterError("condition manifest is malformed")
    for audit_condition_id in condition_ids:
        condition = _condition_by_id(artifact, audit_condition_id)
        events, records, relay = _relay_condition(
            artifact,
            audit_condition_id,
            condition,
            circuit_contract,
            routes,
            contract_reference,
        )
        condition_audit.append(
            {
                "condition_id": audit_condition_id,
                "dnp01_event_count": len(events),
                "psi_routed_event_count": relay["counts"]["psi_routed_events"],
                "dlmn_routed_event_count": relay["counts"]["dlmn_routed_events"],
                "source_event_records_sha256": _sha256(records),
            }
        )

    config: dict[str, Any] = {
        "schema_version": CONFIG_SCHEMA,
        "artifact_schema_version": ARTIFACT_SCHEMA,
        "relay_schema_version": ACTIVE_ROUTE_POLICY_ID,
        "source_kind": SENSORY_SOURCE_KIND,
        "derived_event_semantics": RELAY_SEMANTICS,
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
        "motor_contract": contract_reference,
        "source_event_records_sha256": _sha256(source_records),
        "source_event_count": len(selected_events),
        "active_edge_policy": policy,
        "timing": {
            "source_alignment": PHASE7O_TIME_ALIGNMENT,
            "dt_ms": selected_dt_ms,
            "interval_count": selected_interval_count,
            "boundary_count": selected_interval_count + 1,
            "modeled_additional_delay_ms": 0.0,
            "classification": "ZERO_ADDED_DELAY_EXPLORATORY_ASSUMPTION",
            "semantics": "copy_source_integer_step_and_time_exactly",
        },
        "structural_count_numerical_use": "none_source_metadata_only",
        "population_normalization": "none",
        "latent_psi_or_dlmn_state": False,
        "psi_or_dlmn_spike_event_emission": False,
        "fallback_policy": {
            "voltage_to_event": False,
            "external_drive_to_event": False,
            "filtered_state_to_event": False,
            "synthetic_event_fallback": False,
        },
        "phase8b_synthetic_fixture_in_provenance": False,
        "phase6c_ttmn_branch_executed_here": False,
        "scientific_boundary": {
            "upstream_event": "SIMULATED_DNP01_MODEL_SPIKE",
            "source_kind": SENSORY_SOURCE_KIND,
            "route": "PINNED_MALECNS_STRUCTURAL_CONTRACT",
            "derived_records": RELAY_SEMANTICS,
            "psi_dlmn_latent_state": False,
            "muscle_or_behavior_model": False,
        },
    }
    config["config_sha256"] = _sha256(config)

    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA,
        "relay_schema_version": ACTIVE_ROUTE_POLICY_ID,
        "config_sha256": config["config_sha256"],
        "motor_contract_id": contract_reference["contract_id"],
        "motor_contract_sha256": contract_reference["contract_sha256"],
        "source_kind": SENSORY_SOURCE_KIND,
        "event_semantics": RELAY_SEMANTICS,
        "upstream_artifact_id": artifact.artifact_id,
        "source_condition_id": condition_id,
        "source_event_records": source_records,
        "adapted_dnp01_events": selected_relay["source_events"],
        "psi_routed_events": selected_relay["psi_routed_events"],
        "dlmn_routed_events": selected_relay["dlmn_routed_events"],
        "counts": {
            "dnp01_events": len(selected_events),
            "psi_routed_events": len(selected_relay["psi_routed_events"]),
            "dlmn_routed_events": len(selected_relay["dlmn_routed_events"]),
            "supplemental_psi_to_psi_propagated_events": 0,
        },
        "all_condition_audit": condition_audit,
        "all_conditions_zero_event_conditions": sum(
            row["dnp01_event_count"] == 0
            and row["psi_routed_event_count"] == 0
            and row["dlmn_routed_event_count"] == 0
            for row in condition_audit
        ),
        "all_conditions_zero_events": all(
            row["dnp01_event_count"] == 0
            and row["psi_routed_event_count"] == 0
            and row["dlmn_routed_event_count"] == 0
            for row in condition_audit
        ),
        "voltage_or_drive_fallback_used": False,
        "filtered_state_fallback_used": False,
        "synthetic_fallback_used": False,
        "timing_semantics": TIME_ALIGNMENT,
        "validation_status": "PASSED",
        "scientific_boundary": {
            "source_identity_and_routes": "SOURCE_CONTRACT_EVIDENCE",
            "upstream_event": "SIMULATED_DNP01_MODEL_SPIKE",
            "routed_records": RELAY_SEMANTICS,
            "biological_spike_claim_for_psi_or_dlmn": False,
            "psi_dlmn_neural_state": False,
            "muscle_or_behavior_output": False,
        },
    }
    result["result_sha256"] = _sha256(result)
    return config, result


def build_sensory_psi_dlmn_payload(
    upstream_artifact: LoadedExecutionArtifact,
    condition_id: str,
    circuit_contract: CircuitContract,
    source_contract: RelativeColumnAssignmentSource,
    *,
    motor_contract_path: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Reload and verify all persisted production sources before adapting events."""

    if not isinstance(source_contract, RelativeColumnAssignmentSource):
        raise SensoryPsiDlmnEventAdapterError(
            "a validated body-column source contract is required"
        )
    try:
        reloaded = load_execution_artifact(upstream_artifact.path)
        pinned_source, pinned_circuit, _grid = load_phase7n_sources(
            source_contract.source_root
        )
        pinned_motor = (
            load_pinned_motor_contract(motor_contract_path)
            if motor_contract_path is not None
            else load_pinned_motor_contract()
        )
    except (OSError, ValueError) as exc:
        raise SensoryPsiDlmnEventAdapterError(
            "persisted Phase 7O or structural source could not be revalidated"
        ) from exc
    if (
        reloaded.artifact_id != upstream_artifact.artifact_id
        or reloaded.config != upstream_artifact.config
        or reloaded.result != upstream_artifact.result
        or reloaded.manifest != upstream_artifact.manifest
    ):
        raise SensoryPsiDlmnEventAdapterError(
            "in-memory Phase 7O source differs from its persisted artifact"
        )
    if dict(pinned_source.source_identity) != dict(
        source_contract.source_identity
    ) or _circuit_identity(pinned_circuit) != _circuit_identity(circuit_contract):
        raise SensoryPsiDlmnEventAdapterError(
            "supplied source contracts differ from pinned local sources"
        )
    try:
        return _build_payload_from_loaded(
            reloaded,
            condition_id,
            pinned_circuit,
            pinned_source.source_identity,
            pinned_motor,
        )
    except SensoryDnp01MotorAdapterError as exc:
        raise SensoryPsiDlmnEventAdapterError(
            f"selected Phase 7O condition failed event validation: {exc}"
        ) from exc


__all__ = [
    "ARTIFACT_SCHEMA",
    "CONFIG_SCHEMA",
    "DEFAULT_OUTPUT_ROOT",
    "ORIGIN_EVENT_SCHEMA",
    "RESULT_SCHEMA",
    "SensoryPsiDlmnEventAdapterError",
    "build_sensory_psi_dlmn_payload",
]
