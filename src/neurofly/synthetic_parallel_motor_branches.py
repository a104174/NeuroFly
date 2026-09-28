"""Compose the existing synthetic DNp01→TTMn and DNp01→PSI/DLMn branches.

This module only orchestrates the Phase 8B and Phase 8G implementations. It
does not define another motor route mapper, state equation, or event relay.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

from neurofly.motor_pathway import MOTOR_PATHWAY_EVIDENCE
from neurofly.psi_dlmn_event_relay import (
    ACTIVE_ROUTE_POLICY_ID,
    RELAY_SEMANTICS,
    SYNTHETIC_SOURCE_KIND,
    execute_reference_relay,
)
from neurofly.psi_dlmn_event_relay_artifacts import (
    psi_dlmn_event_relay_artifact_id,
)
from neurofly.synthetic_motor_interface import (
    FIXTURE_IDS,
    build_reference_fixture_battery,
    execute_reference_battery,
)
from neurofly.synthetic_motor_interface_artifacts import synthetic_motor_artifact_id

COMPOSITION_SCHEMA_VERSION = "synthetic_parallel_motor_branch_composition_v1"
RESULT_SCHEMA_VERSION = "synthetic_parallel_motor_branch_result_v1"
ARTIFACT_SCHEMA_VERSION = "synthetic_parallel_motor_branch_artifact_v1"
EXPECTED_MOTOR_CONTRACT_ID = (
    "a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c"
)
EXPECTED_TTMN_CHILD_ARTIFACT_ID = (
    "4321adeee0412a79632ce4e008a1b8eaad22ee167f97f4a98521a9e71d9ef936"
)
EXPECTED_RELAY_CHILD_ARTIFACT_ID = (
    "1da8963e9097c570d67a2683f71744c2dee8c59662faa253cdc56ad32ee5e5b3"
)
TTMN_BRANCH_SEMANTICS = "SIMULATED_EXPLORATORY_TTMN_MODEL_STATE"
PARALLEL_BRANCH_SEMANTICS = "PARALLEL_FROM_COMMON_DNP01_ORIGINS_V1"


class ParallelMotorCompositionError(ValueError):
    """Invalid source, child branch, common origin, or composition result."""


def canonical_sha256(value: Any) -> str:
    try:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ParallelMotorCompositionError(
            "composition data must be deterministic JSON"
        ) from exc
    return hashlib.sha256(payload).hexdigest()


def _child_reference(
    *,
    schema_version: str,
    config: dict[str, Any],
    result: dict[str, Any],
    artifact_id: str,
) -> dict[str, Any]:
    return {
        "artifact_schema_version": schema_version,
        "artifact_id": artifact_id,
        "config_sha256": config["config_sha256"],
        "result_sha256": result["result_sha256"],
    }


def _fixture_map(result: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    rows = result.get("fixtures")
    if not isinstance(rows, list):
        raise ParallelMotorCompositionError(f"{label} child fixtures are malformed")
    mapped = {row.get("fixture_id"): row for row in rows if isinstance(row, dict)}
    if len(mapped) != len(rows) or tuple(mapped) != FIXTURE_IDS:
        raise ParallelMotorCompositionError(f"{label} fixture identities differ")
    return mapped


def _origin_projection(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event["event_id"],
        "source_kind": event["source_kind"],
        "source_body_id": event["source_body_id"],
        "source_side": event["source_side"],
        "source_node_index": event["source_node_index"],
        "neuron_type": event["neuron_type"],
        "step": event["step"],
        "time_ms": event["time_ms"],
    }


def _compose_fixture(
    ttmn_fixture: dict[str, Any], relay_fixture: dict[str, Any]
) -> dict[str, Any]:
    fixture_id = ttmn_fixture["fixture_id"]
    if (
        relay_fixture.get("fixture_id") != fixture_id
        or relay_fixture.get("fixture_config_sha256")
        != ttmn_fixture.get("fixture_config_sha256")
        or relay_fixture.get("synthetic_run_id") != ttmn_fixture.get("synthetic_run_id")
        or ttmn_fixture.get("source_kind") != SYNTHETIC_SOURCE_KIND
        or relay_fixture.get("source_kind") != SYNTHETIC_SOURCE_KIND
        or ttmn_fixture.get("sensory_source_artifact_id") is not None
    ):
        raise ParallelMotorCompositionError(
            "branch fixtures do not share the same synthetic run identity"
        )

    origins = ttmn_fixture.get("source_events")
    mapped_inputs = ttmn_fixture.get("mapped_motor_inputs")
    ttmn_states = ttmn_fixture.get("ttmn_model_state")
    relay_origins = relay_fixture.get("source_events")
    psi_events = relay_fixture.get("psi_routed_events")
    dlmn_events = relay_fixture.get("dlmn_routed_events")
    if not all(
        isinstance(value, list)
        for value in (
            origins,
            mapped_inputs,
            ttmn_states,
            relay_origins,
            psi_events,
            dlmn_events,
        )
    ):
        raise ParallelMotorCompositionError("branch output payload is malformed")

    origin_by_id = {event.get("event_id"): event for event in origins}
    if len(origin_by_id) != len(origins) or any(
        not isinstance(event_id, str) or not event_id for event_id in origin_by_id
    ):
        raise ParallelMotorCompositionError("fixture origin identities are invalid")
    relay_origin_by_id = {event.get("event_id"): event for event in relay_origins}
    if set(relay_origin_by_id) != set(origin_by_id) or len(relay_origin_by_id) != len(
        relay_origins
    ):
        raise ParallelMotorCompositionError(
            "Phase 8G branch received a different origin event set"
        )
    for event_id, event in origin_by_id.items():
        relay_event = relay_origin_by_id[event_id]
        expected_enriched_event = {
            **event,
            "spike_event": {
                "body_id": event["source_body_id"],
                "node_index": event["source_node_index"],
                "neuron_type": event["neuron_type"],
                "step": event["step"],
                "time_ms": event["time_ms"],
            },
            "fixture_id": fixture_id,
            "fixture_config_sha256": ttmn_fixture["fixture_config_sha256"],
            "synthetic_run_id": ttmn_fixture["synthetic_run_id"],
        }
        if relay_event != expected_enriched_event:
            raise ParallelMotorCompositionError(
                "Phase 8G origin event differs from shared Phase 8B event"
            )

    input_by_origin: dict[str, dict[str, Any]] = {}
    for input_record in mapped_inputs:
        matches = [
            event
            for event in origins
            if event["source_body_id"] == input_record.get("source_body_id")
            and event["source_node_index"] == input_record.get("source_node_index")
            and event["step"] == input_record.get("step")
            and event["time_ms"] == input_record.get("time_ms")
        ]
        if len(matches) != 1:
            raise ParallelMotorCompositionError(
                "TTMn input cannot be linked one-to-one to a fixture origin"
            )
        origin = matches[0]
        if origin["event_id"] in input_by_origin:
            raise ParallelMotorCompositionError("duplicate TTMn origin mapping")
        expected_target = MOTOR_PATHWAY_EVIDENCE.target_by_source.get(
            origin["source_body_id"]
        )
        if input_record.get("target_body_id") != expected_target:
            raise ParallelMotorCompositionError("TTMn child route identity differs")
        input_by_origin[origin["event_id"]] = input_record
    if set(input_by_origin) != set(origin_by_id):
        raise ParallelMotorCompositionError(
            "TTMn branch did not preserve every fixture origin"
        )

    psi_by_origin: dict[str, list[dict[str, Any]]] = {
        event_id: [] for event_id in origin_by_id
    }
    dlmn_by_origin: dict[str, list[dict[str, Any]]] = {
        event_id: [] for event_id in origin_by_id
    }
    for record in psi_events:
        event_id = record.get("origin_event_id")
        if (
            event_id not in psi_by_origin
            or record.get("origin_source_kind") != SYNTHETIC_SOURCE_KIND
            or record.get("provenance_kind") != RELAY_SEMANTICS
            or record.get("synthetic_run_id") != ttmn_fixture["synthetic_run_id"]
            or record.get("routed_step") != origin_by_id[event_id]["step"]
            or record.get("routed_time_ms") != origin_by_id[event_id]["time_ms"]
        ):
            raise ParallelMotorCompositionError(
                "PSI receipt is not attributable to its common origin"
            )
        psi_by_origin[event_id].append(record)
    for record in dlmn_events:
        event_id = record.get("origin_event_id")
        if (
            event_id not in dlmn_by_origin
            or record.get("origin_source_kind") != SYNTHETIC_SOURCE_KIND
            or record.get("provenance_kind") != RELAY_SEMANTICS
            or record.get("synthetic_run_id") != ttmn_fixture["synthetic_run_id"]
            or record.get("step") != origin_by_id[event_id]["step"]
            or record.get("time_ms") != origin_by_id[event_id]["time_ms"]
        ):
            raise ParallelMotorCompositionError(
                "DLMn path receipt is not attributable to its common origin"
            )
        dlmn_by_origin[event_id].append(record)

    if Counter(record["source_body_id"] for record in mapped_inputs) != Counter(
        event["source_body_id"] for event in origins
    ):
        raise ParallelMotorCompositionError(
            "TTMn route accounting differs from origins"
        )

    accounting: list[dict[str, Any]] = []
    for event in origins:
        event_id = event["event_id"]
        source_body_id = event["source_body_id"]
        psi_rows = psi_by_origin[event_id]
        dlmn_rows = dlmn_by_origin[event_id]
        if len(psi_rows) != 2 or len(dlmn_rows) != 10:
            raise ParallelMotorCompositionError(
                "motor branch fan-out differs from pinned Phase 8G topology"
            )
        if any(
            row.get("route_query_group") != "dnp01_to_psi" for row in psi_rows
        ) or any(len(row.get("route_edge_ids", [])) != 2 for row in dlmn_rows):
            raise ParallelMotorCompositionError("excluded route entered the relay")
        account = {
            "origin_event_id": event_id,
            "origin_dnp01_body_id": source_body_id,
            "origin_step": event["step"],
            "origin_time_ms": event["time_ms"],
            "ttmn_target_body_id": input_by_origin[event_id]["target_body_id"],
            "ttmn_input_count": 1,
            "psi_receipt_count": len(psi_rows),
            "psi_event_ids": [row["event_id"] for row in psi_rows],
            "dlmn_path_receipt_count": len(dlmn_rows),
            "dlmn_event_ids": [row["event_id"] for row in dlmn_rows],
            "accounting_semantics": "SOFTWARE_PATH_ACCOUNTING_NOT_EFFICACY",
        }
        accounting.append(account)

    active_psi_routes = 2
    active_dlmn_routes_per_psi = 5
    if (
        relay_fixture.get("supplemental_psi_to_psi_propagated_event_count") != 0
        or relay_fixture.get("counts", {}).get("psi_routed_events")
        != len(origins) * active_psi_routes
        or relay_fixture.get("counts", {}).get("dlmn_routed_events")
        != len(origins) * active_psi_routes * active_dlmn_routes_per_psi
    ):
        raise ParallelMotorCompositionError("relay aggregate accounting differs")

    return {
        "fixture_id": fixture_id,
        "fixture_config_sha256": ttmn_fixture["fixture_config_sha256"],
        "synthetic_run_id": ttmn_fixture["synthetic_run_id"],
        "source_kind": SYNTHETIC_SOURCE_KIND,
        "origin_events": origins,
        "ttmn_branch": {
            "semantics": TTMN_BRANCH_SEMANTICS,
            "child_fixture_result_sha256": canonical_sha256(ttmn_fixture),
            "mapped_motor_inputs": mapped_inputs,
            "ttmn_model_state": ttmn_states,
        },
        "psi_dlmn_branch": {
            "semantics": RELAY_SEMANTICS,
            "child_fixture_result_sha256": canonical_sha256(relay_fixture),
            "psi_routed_events": psi_events,
            "dlmn_routed_events": dlmn_events,
            "counts": relay_fixture["counts"],
            "supplemental_psi_to_psi_propagated_event_count": 0,
        },
        "common_origin_accounting": accounting,
        "branch_relationship": PARALLEL_BRANCH_SEMANTICS,
        "combined_branch_quantity": None,
    }


def _build_configuration(
    circuit_contract: Any,
    pinned_motor_contract: dict[str, Any],
    ttmn_config: dict[str, Any],
    ttmn_result: dict[str, Any],
    relay_config: dict[str, Any],
    relay_result: dict[str, Any],
    fixtures: tuple[Any, ...],
) -> dict[str, Any]:
    if (
        pinned_motor_contract.get("manifest", {}).get("artifact_id")
        != EXPECTED_MOTOR_CONTRACT_ID
    ):
        raise ParallelMotorCompositionError("pinned motor contract ID mismatch")
    edge_policy = relay_config["active_edge_policy"]
    ttmn_artifact_id = synthetic_motor_artifact_id(
        ttmn_config["config_sha256"], ttmn_result["result_sha256"]
    )
    relay_artifact_id = psi_dlmn_event_relay_artifact_id(
        relay_config["config_sha256"], relay_result["result_sha256"]
    )
    if (
        ttmn_artifact_id != EXPECTED_TTMN_CHILD_ARTIFACT_ID
        or relay_artifact_id != EXPECTED_RELAY_CHILD_ARTIFACT_ID
    ):
        raise ParallelMotorCompositionError("canonical child branch identity drift")
    value = {
        "schema_version": COMPOSITION_SCHEMA_VERSION,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "input_source_kind": SYNTHETIC_SOURCE_KIND,
        "sensory_source_artifact_id": None,
        "phase7o_causal_provenance": False,
        "fixture_battery": [fixture.to_dict() for fixture in fixtures],
        "child_artifacts": {
            "ttmn_phase6c": _child_reference(
                schema_version="synthetic_dnp01_ttmn_interface_artifact_v1",
                config=ttmn_config,
                result=ttmn_result,
                artifact_id=ttmn_artifact_id,
            ),
            "psi_dlmn_phase8g": _child_reference(
                schema_version="synthetic_psi_dlmn_event_relay_artifact_v1",
                config=relay_config,
                result=relay_result,
                artifact_id=relay_artifact_id,
            ),
        },
        "phase6c_ttmn_branch": {
            "model_config": ttmn_config["motor_model"],
            "model_config_sha256": canonical_sha256(ttmn_config["motor_model"]),
            "routing_evidence_contract_sha256": ttmn_config[
                "routing_evidence_contract_sha256"
            ],
            "structural_weight_numerical_use": "none_source_metadata_only",
            "output_semantics": TTMN_BRANCH_SEMANTICS,
        },
        "phase8g_psi_dlmn_branch": {
            "relay_schema_version": relay_config["relay_schema_version"],
            "model_config_sha256": relay_config["config_sha256"],
            "motor_contract": relay_config["motor_contract"],
            "active_route_policy_id": ACTIVE_ROUTE_POLICY_ID,
            "active_route_policy_sha256": canonical_sha256(edge_policy),
            "active_route_ids": [
                row["edge_id"] for row in edge_policy["active_routes"]
            ],
            "excluded_psi_reciprocal_edge_ids": [
                row["edge_id"] for row in edge_policy["excluded_supplemental_routes"]
            ],
            "zero_added_delay": True,
            "latent_psi_or_dlmn_state": False,
            "structural_count_numerical_use": "none_source_metadata_only",
            "output_semantics": RELAY_SEMANTICS,
        },
        "composition_semantics": {
            "id": PARALLEL_BRANCH_SEMANTICS,
            "same_origin_events_dispatched_to_both_children": True,
            "branch_priority_or_causality": None,
            "branch_outputs_merged": False,
            "new_numerical_parameters": False,
            "population_normalization": "none",
            "phase8b_fixture_is_causal_source": True,
            "phase7o_production_adapter_invoked": False,
        },
        "provenance": {
            "upstream": SYNTHETIC_SOURCE_KIND,
            "ttmn_branch": TTMN_BRANCH_SEMANTICS,
            "psi_dlmn_branch": RELAY_SEMANTICS,
            "sensory_experiment_parent": None,
        },
        "scientific_boundary": {
            "ttmn": "DIMENSIONLESS_EXPLORATORY_MOTOR_NEURAL_STATE",
            "psi_dlmn": "EXPLORATORY_ROUTED_EVENT_RECORDS",
            "routed_records_are_biological_spikes": False,
            "muscle_or_behavior_model": False,
        },
    }
    # The TTMn child config has already validated this source contract. Keep the
    # explicit check here to make the composition's source identity auditable.
    MOTOR_PATHWAY_EVIDENCE.validate_upstream_contract(circuit_contract)
    value["config_sha256"] = canonical_sha256(value)
    return value


def execute_parallel_motor_branches(
    circuit_contract: Any, pinned_motor_contract: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Execute one shared six-fixture battery through both existing branches."""

    fixtures = build_reference_fixture_battery()
    if tuple(fixture.fixture_id for fixture in fixtures) != FIXTURE_IDS:
        raise ParallelMotorCompositionError("canonical fixture battery changed")
    ttmn_config, ttmn_result = execute_reference_battery(
        circuit_contract, fixtures=fixtures
    )
    relay_config, relay_result = execute_reference_relay(
        pinned_motor_contract, fixtures=fixtures
    )
    config = _build_configuration(
        circuit_contract,
        pinned_motor_contract,
        ttmn_config,
        ttmn_result,
        relay_config,
        relay_result,
        fixtures,
    )
    ttmn_fixtures = _fixture_map(ttmn_result, "TTMn")
    relay_fixtures = _fixture_map(relay_result, "PSI/DLMn")
    composed_fixtures = [
        _compose_fixture(ttmn_fixtures[fixture_id], relay_fixtures[fixture_id])
        for fixture_id in FIXTURE_IDS
    ]
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "config_sha256": config["config_sha256"],
        "input_source_kind": SYNTHETIC_SOURCE_KIND,
        "sensory_source_artifact_id": None,
        "motor_contract_id": relay_config["motor_contract"]["contract_id"],
        "phase6c_evidence_contract_sha256": ttmn_config[
            "routing_evidence_contract_sha256"
        ],
        "child_artifacts": config["child_artifacts"],
        "fixtures": composed_fixtures,
        "summary": {
            "fixture_count": len(composed_fixtures),
            "origin_event_count": sum(
                len(item["origin_events"]) for item in composed_fixtures
            ),
            "ttmn_input_event_count": sum(
                len(item["ttmn_branch"]["mapped_motor_inputs"])
                for item in composed_fixtures
            ),
            "psi_receipt_count": sum(
                len(item["psi_dlmn_branch"]["psi_routed_events"])
                for item in composed_fixtures
            ),
            "dlmn_path_receipt_count": sum(
                len(item["psi_dlmn_branch"]["dlmn_routed_events"])
                for item in composed_fixtures
            ),
            "supplemental_psi_to_psi_propagated_event_count": 0,
        },
        "branch_accounting_semantics": "SOFTWARE_PATH_ACCOUNTING_NOT_EFFICACY",
        "no_combined_motor_quantity": True,
        "scientific_boundary": {
            "input": SYNTHETIC_SOURCE_KIND,
            "ttmn_output": TTMN_BRANCH_SEMANTICS,
            "psi_dlmn_output": RELAY_SEMANTICS,
            "production_sensory_input": False,
            "biological_motor_activity_claim": False,
            "muscle_or_behavior_output": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    return config, result


def validate_and_replay_payload(
    config: dict[str, Any],
    result: dict[str, Any],
    circuit_contract: Any,
    pinned_motor_contract: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Re-execute the shared inputs through both pinned child branches."""

    if not isinstance(config, dict) or not isinstance(result, dict):
        raise ParallelMotorCompositionError("composition payload is malformed")
    expected_config, expected_result = execute_parallel_motor_branches(
        circuit_contract, pinned_motor_contract
    )
    if config != expected_config:
        raise ParallelMotorCompositionError("composition config differs from replay")
    if result != expected_result:
        raise ParallelMotorCompositionError("composition result differs from replay")
    config_payload = {
        key: value for key, value in config.items() if key != "config_sha256"
    }
    result_payload = {
        key: value for key, value in result.items() if key != "result_sha256"
    }
    if config.get("config_sha256") != canonical_sha256(config_payload):
        raise ParallelMotorCompositionError("composition config hash mismatch")
    if result.get("result_sha256") != canonical_sha256(result_payload):
        raise ParallelMotorCompositionError("composition result hash mismatch")
    return expected_config, expected_result


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "COMPOSITION_SCHEMA_VERSION",
    "EXPECTED_MOTOR_CONTRACT_ID",
    "EXPECTED_RELAY_CHILD_ARTIFACT_ID",
    "EXPECTED_TTMN_CHILD_ARTIFACT_ID",
    "ParallelMotorCompositionError",
    "RESULT_SCHEMA_VERSION",
    "canonical_sha256",
    "execute_parallel_motor_branches",
    "validate_and_replay_payload",
]
