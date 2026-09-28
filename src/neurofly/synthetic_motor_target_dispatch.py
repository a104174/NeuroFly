"""Synthetic motor-neuron output events dispatched to pinned muscle targets.

This bounded interface test records target resolution only. It does not turn
existing model outputs into events and does not model neuromuscular dynamics.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from neurofly.motor_neuron_muscle_contract import (
    DEFAULT_OUTPUT_ROOT as DEFAULT_TARGET_CONTRACT_ROOT,
)
from neurofly.motor_neuron_muscle_contract import (
    MotorNeuronMuscleContractError,
    replay_motor_neuron_muscle_target_artifact,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT

FIXTURE_SCHEMA_VERSION = "synthetic_motor_neuron_output_fixture_v1"
OUTPUT_EVENT_SCHEMA_VERSION = "synthetic_motor_neuron_output_event_v1"
DISPATCH_SCHEMA_VERSION = "muscle_target_dispatch_v1"
CONFIG_SCHEMA_VERSION = "synthetic_motor_target_dispatch_config_v1"
RESULT_SCHEMA_VERSION = "synthetic_motor_target_dispatch_result_v1"
ARTIFACT_SCHEMA_VERSION = "synthetic_motor_neuron_target_dispatch_artifact_v1"
TARGET_CONTRACT_SCHEMA_VERSION = "motor_neuron_muscle_target_contract_v1"
EXPECTED_TARGET_CONTRACT_ID = (
    "5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0"
)
SYNTHETIC_OUTPUT_PROVENANCE = "SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST"
DISPATCH_PROVENANCE = "EXPLORATORY_MUSCLE_TARGET_DISPATCH"
OUTPUT_SEMANTICS = "SYNTHETIC_ABSTRACT_MOTOR_NEURON_OUTPUT_EVENT"
DISPATCH_SEMANTICS = "TARGET_SELECTION_RECEIPT_ONLY_NO_MUSCLE_DYNAMICS"
DT_MS = 0.1
INTERVAL_COUNT = 80
EVENT_STEP = 10
FIXTURE_IDS = (
    "ZERO_EVENT_CONTROL",
    "TTMN_RIGHT_SINGLE",
    "TTMN_LEFT_SINGLE",
    "DLMN_AB_RIGHT_SINGLE",
    "DLMN_AB_LEFT_SINGLE",
    "DLMN_CF_LEFT_SINGLE",
    "DLMN_CF_RIGHT_SINGLE",
    "ALL_12_SIMULTANEOUS",
)
DEFAULT_TARGET_CONTRACT_PATH = (
    DEFAULT_TARGET_CONTRACT_ROOT / EXPECTED_TARGET_CONTRACT_ID
)
DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / "synthetic_motor_target_dispatch_v1"


class SyntheticMotorTargetDispatchError(ValueError):
    """Invalid synthetic output fixture, target contract, or dispatch result."""


def canonical_sha256(value: Any) -> str:
    try:
        payload = json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SyntheticMotorTargetDispatchError(
            "target dispatch payload must be deterministic JSON"
        ) from exc
    return hashlib.sha256(payload).hexdigest()


def _target_contract(
    artifact_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> dict[str, Any]:
    try:
        artifact = replay_motor_neuron_muscle_target_artifact(artifact_path)
    except (OSError, ValueError, MotorNeuronMuscleContractError) as exc:
        raise SyntheticMotorTargetDispatchError(
            "pinned motor-neuron muscle target contract failed replay"
        ) from exc
    contract = copy.deepcopy(dict(artifact.contract))
    if (
        contract.get("schema_version") != TARGET_CONTRACT_SCHEMA_VERSION
        or contract.get("contract_id") != EXPECTED_TARGET_CONTRACT_ID
        or contract.get("contract_semantics")
        != "NO_DYNAMICS_LITERATURE_SUPPORTED_TARGET_ASSOCIATIONS"
        or contract.get("mapping_policy", {}).get("dynamics") != "NO_DYNAMICS"
    ):
        raise SyntheticMotorTargetDispatchError(
            "unsupported motor-neuron muscle target contract"
        )
    return contract


def _target_records(contract: dict[str, Any]) -> dict[int, dict[str, Any]]:
    rows = contract.get("target_associations")
    if not isinstance(rows, list) or len(rows) != 12:
        raise SyntheticMotorTargetDispatchError(
            "target contract must contain the pinned 12 motor-neuron associations"
        )
    indexed: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise SyntheticMotorTargetDispatchError(
                "target contract association is malformed"
            )
        body_id = row.get("motor_neuron_body_id")
        if (
            isinstance(body_id, bool)
            or not isinstance(body_id, int)
            or body_id in indexed
        ):
            raise SyntheticMotorTargetDispatchError(
                "target contract has invalid or duplicate motor-neuron identity"
            )
        if row.get("motor_neuron_type") not in {"TTMn", "DLMn a, b", "DLMn c-f"}:
            raise SyntheticMotorTargetDispatchError(
                "target contract contains an unauthorized motor-neuron type"
            )
        if row.get("neural_side") not in {"L", "R"}:
            raise SyntheticMotorTargetDispatchError(
                "target contract neural side is malformed"
            )
        if (
            row.get("exact_muscle_fiber") is not None
            or row.get("exact_target") is not None
        ):
            raise SyntheticMotorTargetDispatchError(
                "unexpected exact muscle target in pinned target contract"
            )
        if (
            row.get("neural_identity_source", {}).get("motor_neural_contract_id")
            != contract["source_identity"]["motor_neural_contract_id"]
            or row.get("malecns_peripheral_muscle_edge_present") is not False
            or row.get("association_relation")
            != "LITERATURE_SUPPORTED_MUSCLE_TARGET_ASSOCIATION"
        ):
            raise SyntheticMotorTargetDispatchError(
                "target association provenance is malformed"
            )
        indexed[body_id] = row
    counts = {
        "TTMn": sum(row["motor_neuron_type"] == "TTMn" for row in indexed.values()),
        "DLMn a, b": sum(
            row["motor_neuron_type"] == "DLMn a, b" for row in indexed.values()
        ),
        "DLMn c-f": sum(
            row["motor_neuron_type"] == "DLMn c-f" for row in indexed.values()
        ),
    }
    if counts != {"TTMn": 2, "DLMn a, b": 2, "DLMn c-f": 8}:
        raise SyntheticMotorTargetDispatchError(
            f"unexpected target contract population: {counts!r}"
        )
    return indexed


def _selected_record(
    records: dict[int, dict[str, Any]], neuron_type: str, side: str
) -> dict[str, Any]:
    matches = [
        row
        for row in records.values()
        if row["motor_neuron_type"] == neuron_type and row["neural_side"] == side
    ]
    if len(matches) != 1:
        raise SyntheticMotorTargetDispatchError(
            f"target contract has no unique {neuron_type} {side} identity"
        )
    return matches[0]


def _selected_group_representative(
    records: dict[int, dict[str, Any]], neuron_type: str, side: str
) -> dict[str, Any]:
    matches = sorted(
        (
            row
            for row in records.values()
            if row["motor_neuron_type"] == neuron_type and row["neural_side"] == side
        ),
        key=lambda row: row["motor_neuron_body_id"],
    )
    if len(matches) != 4:
        raise SyntheticMotorTargetDispatchError(
            f"target contract has unexpected {neuron_type} {side} identities"
        )
    return matches[0]


def _fixture_event_specs(
    fixture_id: str, records: dict[int, dict[str, Any]]
) -> list[dict[str, Any]]:
    if fixture_id == "ZERO_EVENT_CONTROL":
        selected: list[dict[str, Any]] = []
    elif fixture_id == "TTMN_RIGHT_SINGLE":
        selected = [_selected_record(records, "TTMn", "R")]
    elif fixture_id == "TTMN_LEFT_SINGLE":
        selected = [_selected_record(records, "TTMn", "L")]
    elif fixture_id == "DLMN_AB_RIGHT_SINGLE":
        selected = [_selected_record(records, "DLMn a, b", "R")]
    elif fixture_id == "DLMN_AB_LEFT_SINGLE":
        selected = [_selected_record(records, "DLMn a, b", "L")]
    elif fixture_id == "DLMN_CF_LEFT_SINGLE":
        selected = [_selected_group_representative(records, "DLMn c-f", "L")]
    elif fixture_id == "DLMN_CF_RIGHT_SINGLE":
        selected = [_selected_group_representative(records, "DLMn c-f", "R")]
    elif fixture_id == "ALL_12_SIMULTANEOUS":
        selected = list(records.values())
    else:
        raise SyntheticMotorTargetDispatchError("unknown synthetic fixture ID")

    specs = [
        {
            "motor_neuron_body_id": row["motor_neuron_body_id"],
            "motor_neuron_type": row["motor_neuron_type"],
            "neural_side": row["neural_side"],
            "step": EVENT_STEP,
            "time_ms": EVENT_STEP * DT_MS,
        }
        for row in selected
    ]
    return sorted(specs, key=lambda row: (row["step"], row["motor_neuron_body_id"]))


def _event_dict(
    spec: dict[str, Any],
    *,
    fixture_id: str,
    run_id: str,
    config_sha256: str,
    target_contract_id: str,
) -> dict[str, Any]:
    semantic = {
        "schema_version": OUTPUT_EVENT_SCHEMA_VERSION,
        "fixture_id": fixture_id,
        "synthetic_run_id": run_id,
        "motor_neuron_body_id": spec["motor_neuron_body_id"],
        "motor_neuron_type": spec["motor_neuron_type"],
        "neural_side": spec["neural_side"],
        "step": spec["step"],
        "time_ms": spec["time_ms"],
        "target_contract_id": target_contract_id,
    }
    return {
        **semantic,
        "event_id": f"synthetic-motor-neuron-output-v1:{canonical_sha256(semantic)}",
        "fixture_config_sha256": config_sha256,
        "provenance_kind": SYNTHETIC_OUTPUT_PROVENANCE,
        "event_semantics": OUTPUT_SEMANTICS,
    }


def _build_fixture_config(fixture_id: str, contract: dict[str, Any]) -> dict[str, Any]:
    records = _target_records(contract)
    specs = _fixture_event_specs(fixture_id, records)
    core = {
        "schema_version": FIXTURE_SCHEMA_VERSION,
        "fixture_id": fixture_id,
        "provenance_kind": SYNTHETIC_OUTPUT_PROVENANCE,
        "event_semantics": OUTPUT_SEMANTICS,
        "event_generation_basis": "EXPLICIT_TEST_FIXTURE_ONLY",
        "source_neural_model_output_artifact_id": None,
        "target_contract_id": contract["contract_id"],
        "target_contract_sha256": contract["contract_sha256"],
        "dt_ms": DT_MS,
        "interval_count": INTERVAL_COUNT,
        "time_semantics": "time_ms_equals_integer_step_times_dt_ms_v1",
        "event_specs": specs,
    }
    config_sha256 = canonical_sha256(core)
    run_id = f"synthetic_motor_neuron_output_run_v1:{fixture_id}:{config_sha256}"
    events = [
        _event_dict(
            spec,
            fixture_id=fixture_id,
            run_id=run_id,
            config_sha256=config_sha256,
            target_contract_id=contract["contract_id"],
        )
        for spec in specs
    ]
    return {
        **core,
        "events": events,
        "fixture_config_sha256": config_sha256,
        "synthetic_run_id": run_id,
    }


def _validate_fixture_config(config: dict[str, Any], contract: dict[str, Any]) -> None:
    if not isinstance(config, dict):
        raise SyntheticMotorTargetDispatchError(
            "input must be a synthetic output fixture object"
        )
    fixture_id = config.get("fixture_id")
    if fixture_id not in FIXTURE_IDS:
        raise SyntheticMotorTargetDispatchError("unknown synthetic fixture ID")
    expected = _build_fixture_config(fixture_id, contract)
    if config != expected:
        raise SyntheticMotorTargetDispatchError(
            "synthetic output fixture differs from its deterministic definition"
        )
    for event in config["events"]:
        if (
            event["step"] < 0
            or event["step"] > config["interval_count"]
            or event["time_ms"] != event["step"] * config["dt_ms"]
        ):
            raise SyntheticMotorTargetDispatchError(
                "synthetic output event has invalid integer-step timing"
            )


def _association_id(row: dict[str, Any]) -> str:
    return f"motor-muscle-target-association-v1:{canonical_sha256(row)}"


def _dispatch_record(
    event: dict[str, Any], association: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    target_record = copy.deepcopy(association)
    association_id = _association_id(target_record)
    semantic = {
        "schema_version": DISPATCH_SCHEMA_VERSION,
        "origin_output_event_id": event["event_id"],
        "target_association_id": association_id,
        "target_contract_id": contract["contract_id"],
        "step": event["step"],
        "time_ms": event["time_ms"],
    }
    return {
        **semantic,
        "dispatch_id": (
            f"exploratory-muscle-target-dispatch-v1:{canonical_sha256(semantic)}"
        ),
        "origin_fixture_id": event["fixture_id"],
        "origin_run_id": event["synthetic_run_id"],
        "origin_provenance_kind": event["provenance_kind"],
        "provenance_kind": DISPATCH_PROVENANCE,
        "motor_neuron_body_id": target_record["motor_neuron_body_id"],
        "motor_neuron_type": target_record["motor_neuron_type"],
        "neural_side": target_record["neural_side"],
        "target_contract_sha256": contract["contract_sha256"],
        "target_relation": target_record["association_relation"],
        "target_structure_kind": target_record["target_structure_kind"],
        "target_class": target_record["target_class"],
        "target_group": target_record["target_group"],
        "exact_target": target_record["exact_target"],
        "exact_muscle_fiber": target_record["exact_muscle_fiber"],
        "muscle_target_side": target_record["muscle_target_side"],
        "muscle_target_side_status": target_record["muscle_target_side_status"],
        "muscle_target_side_basis": target_record["muscle_target_side_basis"],
        "target_granularity": target_record["target_granularity"],
        "mapping_confidence": target_record["mapping_confidence"],
        "mapping_confidence_scope": target_record["mapping_confidence_scope"],
        "evidence_classification": target_record["evidence_classification"],
        "evidence_refs": copy.deepcopy(target_record["evidence_refs"]),
        "unresolved_fields": copy.deepcopy(target_record["unresolved_fields"]),
        "unresolved_reasons": copy.deepcopy(target_record["unresolved_reasons"]),
        "time_semantics": "SAME_STORED_BOUNDARY_DISPATCH_BOOKKEEPING_ONLY",
        "dispatch_semantics": DISPATCH_SEMANTICS,
        "muscle_activation_created": False,
    }


def _execute_fixture(
    config: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    _validate_fixture_config(config, contract)
    records = _target_records(contract)
    dispatches = []
    for event in config["events"]:
        body_id = event["motor_neuron_body_id"]
        association = records.get(body_id)
        if association is None or (
            event["motor_neuron_type"] != association["motor_neuron_type"]
            or event["neural_side"] != association["neural_side"]
        ):
            raise SyntheticMotorTargetDispatchError(
                "synthetic output identity does not match the target contract"
            )
        dispatches.append(_dispatch_record(event, association, contract))
    dispatches.sort(
        key=lambda row: (
            row["step"],
            row["motor_neuron_body_id"],
            row["dispatch_id"],
        )
    )
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "fixture_id": config["fixture_id"],
        "fixture_config_sha256": config["fixture_config_sha256"],
        "synthetic_run_id": config["synthetic_run_id"],
        "input_provenance_kind": SYNTHETIC_OUTPUT_PROVENANCE,
        "dispatch_provenance_kind": DISPATCH_PROVENANCE,
        "target_contract_id": contract["contract_id"],
        "target_contract_sha256": contract["contract_sha256"],
        "origin_output_events": copy.deepcopy(config["events"]),
        "dispatch_records": dispatches,
        "summary": {
            "origin_event_count": len(config["events"]),
            "dispatch_record_count": len(dispatches),
            "target_class_counts": {
                target_class: sum(
                    row["target_class"] == target_class for row in dispatches
                )
                for target_class in sorted({row["target_class"] for row in dispatches})
            },
            "no_muscle_dynamics": True,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    return result


def build_reference_config(
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the deterministic eight-fixture config from the replayed contract."""

    contract = _target_contract(target_contract_path)
    records = _target_records(contract)
    fixtures = [
        _build_fixture_config(fixture_id, contract) for fixture_id in FIXTURE_IDS
    ]
    payload = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "input_provenance_kind": SYNTHETIC_OUTPUT_PROVENANCE,
        "dispatch_provenance_kind": DISPATCH_PROVENANCE,
        "target_contract_schema_version": TARGET_CONTRACT_SCHEMA_VERSION,
        "target_contract_id": contract["contract_id"],
        "target_contract_sha256": contract["contract_sha256"],
        "authorized_motor_neuron_count": len(records),
        "fixture_ids": list(FIXTURE_IDS),
        "fixtures": fixtures,
        "interface_semantics": "SYNTHETIC_IDENTITY_TO_TARGET_ASSOCIATION_ONLY",
        "muscle_dynamics": "NO_MUSCLE_DYNAMICS",
        "source_model_output_artifact_id": None,
        "current_model_output_conversion": False,
    }
    payload["config_sha256"] = canonical_sha256(payload)
    return payload


def execute_reference_battery(
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replay the target contract and dispatch the fixed synthetic fixture set."""

    contract = _target_contract(target_contract_path)
    config = build_reference_config(target_contract_path)
    results = [_execute_fixture(fixture, contract) for fixture in config["fixtures"]]
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "input_provenance_kind": SYNTHETIC_OUTPUT_PROVENANCE,
        "dispatch_provenance_kind": DISPATCH_PROVENANCE,
        "target_contract_id": contract["contract_id"],
        "target_contract_sha256": contract["contract_sha256"],
        "fixtures": results,
        "summary": {
            "fixture_count": len(results),
            "fixture_ids": [row["fixture_id"] for row in results],
            "total_origin_events": sum(
                row["summary"]["origin_event_count"] for row in results
            ),
            "total_dispatch_records": sum(
                row["summary"]["dispatch_record_count"] for row in results
            ),
            "no_muscle_dynamics": True,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    return config, result


def validate_and_replay_payload(
    config: dict[str, Any],
    result: dict[str, Any],
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate content hashes and rebuild every fixture/dispatch from source."""

    expected_config, expected_result = execute_reference_battery(target_contract_path)
    if config != expected_config:
        raise SyntheticMotorTargetDispatchError(
            "dispatch configuration differs from the pinned reference fixtures"
        )
    if result != expected_result:
        raise SyntheticMotorTargetDispatchError(
            "dispatch result differs from deterministic target-contract replay"
        )
    return expected_config, expected_result


def fixture_result(
    fixture_id: str,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return one fixture result after validating its source and identity."""

    contract = _target_contract(target_contract_path)
    config = _build_fixture_config(fixture_id, contract)
    return _execute_fixture(config, contract)


def dispatch_fixture_config(
    config: dict[str, Any],
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> dict[str, Any]:
    """Dispatch one validated fixture; model-output records are not accepted."""

    contract = _target_contract(target_contract_path)
    return _execute_fixture(config, contract)


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "CONFIG_SCHEMA_VERSION",
    "DEFAULT_ARTIFACT_ROOT",
    "DEFAULT_TARGET_CONTRACT_PATH",
    "DISPATCH_PROVENANCE",
    "DISPATCH_SCHEMA_VERSION",
    "EXPECTED_TARGET_CONTRACT_ID",
    "FIXTURE_IDS",
    "FIXTURE_SCHEMA_VERSION",
    "OUTPUT_EVENT_SCHEMA_VERSION",
    "RESULT_SCHEMA_VERSION",
    "SYNTHETIC_OUTPUT_PROVENANCE",
    "SyntheticMotorTargetDispatchError",
    "build_reference_config",
    "canonical_sha256",
    "dispatch_fixture_config",
    "execute_reference_battery",
    "fixture_result",
    "validate_and_replay_payload",
]
