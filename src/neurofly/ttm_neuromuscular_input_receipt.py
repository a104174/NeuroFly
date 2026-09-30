"""Phase 8Q TTM-only exploratory neuromuscular-input receipt ledger.

Receipts mark a software handoff from validated Phase 8O target dispatches.
They do not model transmitter release, muscle response, or muscle dynamics.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from neurofly.model_derived_ttmn_target_dispatch import (
    DISPATCH_PROVENANCE,
    DISPATCH_SCHEMA_VERSION,
    EXPECTED_TARGET_CONTRACT_ID,
    UPSTREAM_PROVENANCE,
    ModelDerivedTTMnDispatchError,
)
from neurofly.model_derived_ttmn_target_dispatch_artifacts import (
    ARTIFACT_SCHEMA_VERSION as PHASE8O_ARTIFACT_SCHEMA_VERSION,
)
from neurofly.model_derived_ttmn_target_dispatch_artifacts import (
    DEFAULT_ARTIFACT_ROOT as DEFAULT_PHASE8O_ARTIFACT_ROOT,
)
from neurofly.model_derived_ttmn_target_dispatch_artifacts import (
    DEFAULT_PHASE8B_SOURCE_ARTIFACT,
    DEFAULT_PHASE8N_ARTIFACT,
    DEFAULT_TARGET_CONTRACT_PATH,
    LoadedModelDerivedTTMnTargetArtifact,
    ModelDerivedTTMnTargetArtifactError,
    load_model_derived_ttmn_target_artifact,
    replay_model_derived_ttmn_target_artifact,
)
from neurofly.motor_neuron_muscle_contract import (
    MotorNeuronMuscleContractError,
    replay_motor_neuron_muscle_target_artifact,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_motor_target_dispatch import target_association_id
from neurofly.synthetic_ttmn_output_rule import (
    FIXTURE_IDS as PHASE8O_FIXTURE_IDS,
)
from neurofly.synthetic_ttmn_output_rule import (
    GENERATOR_KIND,
    OUTPUT_EVENT_PROVENANCE,
    OUTPUT_EVENT_SCHEMA_VERSION,
)

CONFIG_SCHEMA_VERSION = "ttm_neuromuscular_input_receipt_config_v1"
RESULT_SCHEMA_VERSION = "ttm_neuromuscular_input_receipt_result_v1"
ARTIFACT_SCHEMA_VERSION = "ttm_neuromuscular_input_receipt_artifact_v1"
RECEIPT_SCHEMA_VERSION = "ttm_neuromuscular_input_receipt_v1"
RECEIPT_PROVENANCE = "EXPLORATORY_NEUROMUSCULAR_INPUT"
RECEIPT_SEMANTICS = "EXPLORATORY_TTM_NMJ_INPUT_HANDOFF_RECEIPT_ONLY"
TIME_SEMANTICS = "COPY_PARENT_DISPATCH_BOUNDARY_BOOKKEEPING_ONLY"
EXPECTED_PHASE8O_ARTIFACT_ID = (
    "3bc011f9a8831f5291b6078d6132ef0dc6d6d7e87cc45ecfaa957ec80b8af360"
)
EXPECTED_PHASE8O_CONFIG_SHA256 = (
    "79624d65a8aba4885c66791b4f40fe4f31e050e4fc70e794ea475af2e3881261"
)
EXPECTED_PHASE8O_RESULT_SHA256 = (
    "0d3826ffc4ef35246d48da9bbe586afc82b1cebb64beebbb1618e8f01f81fbcc"
)
EXPECTED_PHASE8N_ARTIFACT_ID = (
    "1c8aeac685646dac16fbb66f163743b662a3cd9a0e8f9f7582210fd7b39b9ab3"
)
EXPECTED_TARGET_CONTRACT_SHA256 = (
    "9816a180acc845c202f70e374a4de951536296fed979c21c12d796792b8bac1f"
)
DEFAULT_PHASE8O_ARTIFACT = DEFAULT_PHASE8O_ARTIFACT_ROOT / EXPECTED_PHASE8O_ARTIFACT_ID
DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA_VERSION

TARGET_ASSOCIATION_FIELDS = (
    "motor_neuron_body_id",
    "motor_neuron_type",
    "motor_neuron_instance",
    "neural_side",
    "association_relation",
    "target_structure_kind",
    "target_class",
    "target_group",
    "exact_target",
    "exact_muscle_fiber",
    "muscle_target_side",
    "muscle_target_side_status",
    "muscle_target_side_basis",
    "target_granularity",
    "mapping_confidence",
    "mapping_confidence_scope",
    "mapping_confidence_semantics",
    "evidence_classification",
    "evidence_refs",
    "unresolved_fields",
    "unresolved_reasons",
)


class TTMNeuromuscularInputReceiptError(ValueError):
    """Invalid Phase 8O source dispatch or Phase 8Q receipt ledger."""


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
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8Q payload must be deterministic JSON"
        ) from exc
    return hashlib.sha256(payload).hexdigest()


def _artifact_id(config_sha256: str, result_sha256: str) -> str:
    payload = (
        json.dumps(
            {
                "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                "config_sha256": config_sha256,
                "result_sha256": result_sha256,
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )
    return hashlib.sha256(payload).hexdigest()


def _verify_dispatch_source_object(
    source: LoadedModelDerivedTTMnTargetArtifact,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Check pinned Phase 8O identity and integrity without regenerating events."""

    config = copy.deepcopy(dict(source.config))
    result = copy.deepcopy(dict(source.result))
    manifest = copy.deepcopy(dict(source.manifest))
    try:
        disk_source = load_model_derived_ttmn_target_artifact(
            source.path, expected_artifact_id=EXPECTED_PHASE8O_ARTIFACT_ID
        )
    except (OSError, ValueError, ModelDerivedTTMnTargetArtifactError) as exc:
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8O source artifact failed integrity validation"
        ) from exc
    if (
        source.artifact_id != EXPECTED_PHASE8O_ARTIFACT_ID
        or dict(disk_source.config) != config
        or dict(disk_source.result) != result
        or dict(disk_source.manifest) != manifest
        or manifest.get("artifact_schema_version") != PHASE8O_ARTIFACT_SCHEMA_VERSION
        or config.get("config_sha256")
        != canonical_sha256(
            {key: value for key, value in config.items() if key != "config_sha256"}
        )
        or result.get("result_sha256")
        != canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        or config.get("config_sha256") != EXPECTED_PHASE8O_CONFIG_SHA256
        or result.get("result_sha256") != EXPECTED_PHASE8O_RESULT_SHA256
        or config.get("source_ttmn_output_artifact", {}).get("artifact_id")
        != EXPECTED_PHASE8N_ARTIFACT_ID
        or config.get("source_ttmn_output_artifact", {}).get("config_sha256")
        != "43ddd7fba90235f7331c4c53ee774810956b9b55a9dc4c3ddc94bb4887283ea8"
        or config.get("source_ttmn_output_artifact", {}).get("result_sha256")
        != "de54e2657560ae77a83b46174e029f7449008f968b0e0f4391cea8ec7a07c7b5"
        or result.get("source_ttmn_output_artifact_id") != EXPECTED_PHASE8N_ARTIFACT_ID
        or result.get("target_contract_id") != EXPECTED_TARGET_CONTRACT_ID
        or result.get("target_contract_sha256") != EXPECTED_TARGET_CONTRACT_SHA256
        or config.get("dispatch_schema_version") != DISPATCH_SCHEMA_VERSION
        or config.get("dispatch_provenance_kind") != DISPATCH_PROVENANCE
        or config.get("source_event_schema_version") != OUTPUT_EVENT_SCHEMA_VERSION
        or config.get("source_event_provenance_kind") != OUTPUT_EVENT_PROVENANCE
        or config.get("source_generator", {}).get("generator_kind") != GENERATOR_KIND
        or config.get("source_generator", {}).get("provenance_kind")
        != OUTPUT_EVENT_PROVENANCE
        or result.get("source_event_provenance_kind") != OUTPUT_EVENT_PROVENANCE
        or result.get("dispatch_provenance_kind") != DISPATCH_PROVENANCE
        or result.get("upstream_provenance_kind") != UPSTREAM_PROVENANCE
        or config.get("fixture_ids") != list(PHASE8O_FIXTURE_IDS)
        or [row.get("fixture_id") for row in result.get("fixtures", [])]
        != list(PHASE8O_FIXTURE_IDS)
        or result.get("summary", {}).get("fixture_count") != len(PHASE8O_FIXTURE_IDS)
        or result.get("summary", {}).get("model_derived_output_event_count") != 8
        or result.get("summary", {}).get("dispatch_record_count") != 8
        or result.get("summary", {}).get("per_body_event_counts")
        != {"800146": 4, "804642": 4}
    ):
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8O source schema, provenance, or pinned identity mismatch"
        )
    return config, result, manifest


def _target_associations(
    target_contract_path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        artifact = replay_motor_neuron_muscle_target_artifact(target_contract_path)
    except (OSError, ValueError, MotorNeuronMuscleContractError) as exc:
        raise TTMNeuromuscularInputReceiptError(
            "pinned Phase 8K target contract failed replay"
        ) from exc
    contract = copy.deepcopy(dict(artifact.contract))
    if (
        artifact.artifact_id != EXPECTED_TARGET_CONTRACT_ID
        or contract.get("schema_version") != "motor_neuron_muscle_target_contract_v1"
        or contract.get("contract_id") != EXPECTED_TARGET_CONTRACT_ID
        or contract.get("contract_sha256") != EXPECTED_TARGET_CONTRACT_SHA256
        or contract.get("contract_semantics")
        != "NO_DYNAMICS_LITERATURE_SUPPORTED_TARGET_ASSOCIATIONS"
        or contract.get("mapping_policy", {}).get("dynamics") != "NO_DYNAMICS"
    ):
        raise TTMNeuromuscularInputReceiptError(
            "unsupported pinned Phase 8K target contract"
        )
    associations = [
        row
        for row in contract.get("target_associations", [])
        if isinstance(row, dict) and row.get("motor_neuron_type") == "TTMn"
    ]
    if len(associations) != 2:
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8K must expose exactly two TTMn target associations"
        )
    indexed = {target_association_id(row): row for row in associations}
    if len(indexed) != 2:
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8K TTM target association identities are duplicated"
        )
    for association in associations:
        if (
            association.get("target_class") != "TTM"
            or association.get("target_granularity") != "MUSCLE_CLASS"
            or association.get("exact_target") is not None
            or association.get("exact_muscle_fiber") is not None
            or association.get("mapping_confidence") != "HIGH"
            or association.get("muscle_target_side_status")
            != "QUALIFIED_LITERATURE_IPSILATERAL_CLASS_INFERENCE"
        ):
            raise TTMNeuromuscularInputReceiptError(
                "pinned TTM target association semantics changed"
            )
    return indexed, {
        "artifact_id": artifact.artifact_id,
        "contract_sha256": contract["contract_sha256"],
        "schema_version": contract["schema_version"],
        "source_motor_neural_contract_id": contract["source_identity"][
            "motor_neural_contract_id"
        ],
        "source_motor_neural_contract_sha256": contract["source_identity"][
            "motor_neural_contract_sha256"
        ],
    }


def receipt_target_semantics(association: dict) -> dict:
    return {key: copy.deepcopy(association[key]) for key in TARGET_ASSOCIATION_FIELDS}


def receipt_runtime_dispatch(dispatch: dict) -> dict:
    """One scenario dispatch→one handoff receipt, without release success."""
    if (
        dispatch.get("schema_version") != "scenario_ttm_target_dispatch_v1"
        or dispatch.get("motor_neuron_type") != "TTMn"
    ):
        raise ValueError("unsupported runtime TTM dispatch")
    record = {
        "schema_version": "scenario_ttm_neuromuscular_receipt_v1",
        "parent_dispatch_id": dispatch["dispatch_id"],
        "scenario_execution_id": dispatch["scenario_execution_id"],
        "step": dispatch["step"],
        "time_ms": dispatch["time_ms"],
        "motor_neuron_body_id": dispatch["motor_neuron_body_id"],
        "neural_side": dispatch["neural_side"],
        "target_association_id": dispatch["target_association_id"],
        "target_contract_id": dispatch["target_contract_id"],
        "target_semantics": receipt_target_semantics(dispatch),
        "provenance_kind": RECEIPT_PROVENANCE,
        "time_semantics": TIME_SEMANTICS,
        "receipt_semantics": RECEIPT_SEMANTICS,
        "boundary": "HANDOFF_RECORD_ONLY_NO_RELEASE_OR_MUSCLE_RESPONSE_CLAIM",
    }
    return {"receipt_id": canonical_sha256(record), **record}


def _receipt(
    dispatch: dict[str, Any],
    association: dict[str, Any],
    *,
    source: LoadedModelDerivedTTMnTargetArtifact,
    source_config: dict[str, Any],
    contract_reference: dict[str, Any],
) -> dict[str, Any]:
    semantic = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "parent_dispatch_id": dispatch["dispatch_id"],
        "target_association_id": dispatch["target_association_id"],
        "origin_output_event_id": dispatch["origin_output_event_id"],
        "step": dispatch["step"],
        "time_ms": dispatch["time_ms"],
        "source_phase8o_artifact_id": source.artifact_id,
    }
    receipt_id = f"ttm-neuromuscular-input-receipt-v1:{canonical_sha256(semantic)}"
    return {
        **semantic,
        "receipt_id": receipt_id,
        "provenance_kind": RECEIPT_PROVENANCE,
        "provenance_chain": [
            dispatch["upstream_provenance_kind"],
            "PHASE_6C_TTMN_DIMENSIONLESS_EXPLORATORY_STATE",
            dispatch["origin_provenance_kind"],
            dispatch["provenance_kind"],
            RECEIPT_PROVENANCE,
        ],
        "motor_neuron_body_id": association["motor_neuron_body_id"],
        "motor_neuron_type": association["motor_neuron_type"],
        "motor_neuron_instance": association["motor_neuron_instance"],
        "neural_side": association["neural_side"],
        "target_association_id": dispatch["target_association_id"],
        "target_contract_id": contract_reference["artifact_id"],
        "target_contract_sha256": contract_reference["contract_sha256"],
        "source_phase8o_config_sha256": source.config["config_sha256"],
        "source_phase8o_result_sha256": source.result["result_sha256"],
        "source_phase8n_artifact_id": dispatch["source_output_artifact_id"],
        "source_phase8n_config_sha256": dispatch["source_output_config_sha256"],
        "source_phase8n_result_sha256": dispatch["source_output_result_sha256"],
        "source_phase6c_model_config_sha256": source_config[
            "source_phase6c_model_identity"
        ]["config_sha256"],
        "source_generator_kind": dispatch["source_generator_kind"],
        "source_generator_config_sha256": dispatch["source_generator_config_sha256"],
        "source_fixture_id": dispatch["source_fixture_id"],
        "source_fixture_config_sha256": dispatch["source_fixture_config_sha256"],
        "source_fixture_result_sha256": dispatch["source_fixture_result_sha256"],
        "source_synthetic_run_id": dispatch["source_synthetic_run_id"],
        "upstream_provenance_kind": dispatch["upstream_provenance_kind"],
        "origin_provenance_kind": dispatch["origin_provenance_kind"],
        "dispatch_provenance_kind": dispatch["provenance_kind"],
        "target_semantics": receipt_target_semantics(association),
        "time_semantics": TIME_SEMANTICS,
        "receipt_semantics": RECEIPT_SEMANTICS,
        "boundary": "HANDOFF_RECORD_ONLY_NO_RELEASE_OR_MUSCLE_RESPONSE_CLAIM",
    }


def _validated_fixture_receipts(
    fixture: dict[str, Any],
    *,
    source: LoadedModelDerivedTTMnTargetArtifact,
    source_config: dict[str, Any],
    target_by_id: dict[str, Any],
    contract_reference: dict[str, Any],
) -> dict[str, Any]:
    dispatches = fixture.get("dispatch_records")
    events = fixture.get("origin_output_events")
    if not isinstance(dispatches, list) or not isinstance(events, list):
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8O fixture dispatch or event list is malformed"
        )
    if fixture.get("upstream_provenance_kind") != UPSTREAM_PROVENANCE:
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8O fixture has an unauthorized upstream provenance"
        )
    event_by_id = {
        event.get("event_id"): event for event in events if isinstance(event, dict)
    }
    if len(event_by_id) != len(events):
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8O fixture has duplicate or malformed event identities"
        )
    dispatch_ids: set[str] = set()
    receipt_records = []
    for dispatch in dispatches:
        if not isinstance(dispatch, dict):
            raise TTMNeuromuscularInputReceiptError(
                "Phase 8O dispatch record is malformed"
            )
        association_id = dispatch.get("target_association_id")
        association = target_by_id.get(association_id)
        event = event_by_id.get(dispatch.get("origin_output_event_id"))
        if association is None or event is None:
            raise TTMNeuromuscularInputReceiptError(
                "dispatch has no authorized TTM association or output event"
            )
        dispatch_id = dispatch.get("dispatch_id")
        if (
            not isinstance(dispatch_id, str)
            or dispatch_id in dispatch_ids
            or dispatch.get("schema_version") != DISPATCH_SCHEMA_VERSION
            or dispatch.get("provenance_kind") != DISPATCH_PROVENANCE
            or dispatch.get("origin_provenance_kind") != OUTPUT_EVENT_PROVENANCE
            or dispatch.get("upstream_provenance_kind") != UPSTREAM_PROVENANCE
            or dispatch.get("source_generator_kind") != GENERATOR_KIND
            or dispatch.get("source_generator_config_sha256")
            != source_config.get("source_generator", {}).get("config_sha256")
            or dispatch.get("source_output_config_sha256")
            != source_config.get("source_ttmn_output_artifact", {}).get("config_sha256")
            or dispatch.get("source_output_result_sha256")
            != source_config.get("source_ttmn_output_artifact", {}).get("result_sha256")
            or dispatch.get("target_contract_id") != EXPECTED_TARGET_CONTRACT_ID
            or dispatch.get("target_contract_sha256") != EXPECTED_TARGET_CONTRACT_SHA256
            or dispatch.get("source_output_artifact_id") != EXPECTED_PHASE8N_ARTIFACT_ID
            or dispatch.get("motor_neuron_type") != "TTMn"
            or dispatch.get("target_class") != "TTM"
            or dispatch.get("dispatch_semantics")
            != "TARGET_ASSOCIATION_RECEIPT_ONLY_NO_MUSCLE_DYNAMICS"
            or dispatch.get("time_semantics")
            != "SAME_STORED_BOUNDARY_TARGET_DISPATCH_BOOKKEEPING_ONLY"
            or event.get("schema_version") != OUTPUT_EVENT_SCHEMA_VERSION
            or event.get("provenance_kind") != OUTPUT_EVENT_PROVENANCE
            or event.get("upstream_provenance_kind") != UPSTREAM_PROVENANCE
            or event.get("generator_kind") != GENERATOR_KIND
            or event.get("generator_config_sha256")
            != source_config.get("source_generator", {}).get("config_sha256")
            or event.get("biological_action_potential_claim") is not False
            or dispatch.get("step") != event.get("step")
            or dispatch.get("time_ms") != event.get("time_ms")
            or dispatch.get("motor_neuron_body_id") != event.get("motor_neuron_body_id")
            or dispatch.get("motor_neuron_type") != event.get("motor_neuron_type")
            or dispatch.get("neural_side") != event.get("neural_side")
            or dispatch.get("source_fixture_id") != fixture.get("fixture_id")
            or dispatch.get("source_synthetic_run_id")
            != fixture.get("source_synthetic_run_id")
            or dispatch.get("source_fixture_config_sha256")
            != fixture.get("source_fixture_config_sha256")
            or dispatch.get("source_fixture_result_sha256")
            != fixture.get("source_fixture_result_sha256")
            or not isinstance(dispatch.get("step"), int)
            or isinstance(dispatch.get("step"), bool)
            or dispatch["step"] < 0
            or isinstance(dispatch.get("time_ms"), bool)
            or not isinstance(dispatch.get("time_ms"), (int, float))
            or not math.isfinite(dispatch["time_ms"])
            or any(
                dispatch.get(key) != association.get(key)
                for key in TARGET_ASSOCIATION_FIELDS
            )
        ):
            raise TTMNeuromuscularInputReceiptError(
                "Phase 8O dispatch identity, provenance, timing, or TTM target "
                "is invalid"
            )
        dispatch_ids.add(dispatch_id)
        receipt_records.append(
            _receipt(
                dispatch,
                association,
                source=source,
                source_config=source_config,
                contract_reference=contract_reference,
            )
        )
    if set(event_by_id) != {
        dispatch.get("origin_output_event_id") for dispatch in dispatches
    }:
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8O fixture events and dispatches do not correspond one-to-one"
        )
    if fixture.get("fixture_id") not in PHASE8O_FIXTURE_IDS:
        raise TTMNeuromuscularInputReceiptError("unexpected Phase 8O fixture identity")
    receipt_records.sort(
        key=lambda row: (
            row["step"],
            row["motor_neuron_body_id"],
            row["origin_output_event_id"],
            row["parent_dispatch_id"],
        )
    )
    return {
        "fixture_id": fixture["fixture_id"],
        "source_synthetic_run_id": fixture["source_synthetic_run_id"],
        "upstream_provenance_kind": fixture["upstream_provenance_kind"],
        "source_dispatch_ids": [row["dispatch_id"] for row in dispatches],
        "receipts": receipt_records,
        "summary": {
            "dispatch_count": len(dispatches),
            "receipt_count": len(receipt_records),
            "each_dispatch_has_one_receipt": len(dispatches) == len(receipt_records)
            and {row["parent_dispatch_id"] for row in receipt_records} == dispatch_ids,
        },
    }


def execute_reference_battery(
    source: LoadedModelDerivedTTMnTargetArtifact,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_config, source_result, _ = _verify_dispatch_source_object(source)
    target_by_id, contract_reference = _target_associations(target_contract_path)
    payload: dict[str, Any] = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "source_phase8o_artifact": {
            "artifact_id": source.artifact_id,
            "artifact_schema_version": PHASE8O_ARTIFACT_SCHEMA_VERSION,
            "config_sha256": source_config["config_sha256"],
            "result_sha256": source_result["result_sha256"],
            "dispatch_schema_version": DISPATCH_SCHEMA_VERSION,
        },
        "target_contract": contract_reference,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "receipt_provenance_kind": RECEIPT_PROVENANCE,
        "receipt_semantics": RECEIPT_SEMANTICS,
        "time_semantics": TIME_SEMANTICS,
        "fixture_ids": [row["fixture_id"] for row in source_result["fixtures"]],
        "provenance_chain": [
            UPSTREAM_PROVENANCE,
            "PHASE_6C_TTMN_DIMENSIONLESS_EXPLORATORY_STATE",
            OUTPUT_EVENT_PROVENANCE,
            DISPATCH_PROVENANCE,
            RECEIPT_PROVENANCE,
        ],
        "scientific_boundary": {
            "receipt_is_handoff_bookkeeping_only": True,
            "nmj_release_modelled": False,
            "muscle_electrical_response_modelled": False,
            "muscle_state_created": False,
            "nmj_delay_modelled": False,
            "depression_or_recovery_modelled": False,
            "structural_counts_used_numerically": False,
            "dlmn_interface_created": False,
            "production_sensory_source": False,
            "force_or_behavior_modelled": False,
        },
    }
    payload["config_sha256"] = canonical_sha256(payload)
    fixtures = [
        _validated_fixture_receipts(
            fixture,
            source=source,
            source_config=source_config,
            target_by_id=target_by_id,
            contract_reference=contract_reference,
        )
        for fixture in source_result["fixtures"]
    ]
    receipts = [row for fixture in fixtures for row in fixture["receipts"]]
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "config_sha256": payload["config_sha256"],
        "source_phase8o_artifact_id": source.artifact_id,
        "source_phase8o_config_sha256": source_config["config_sha256"],
        "source_phase8o_result_sha256": source_result["result_sha256"],
        "target_contract_id": contract_reference["artifact_id"],
        "target_contract_sha256": contract_reference["contract_sha256"],
        "source_event_provenance_kind": OUTPUT_EVENT_PROVENANCE,
        "dispatch_provenance_kind": DISPATCH_PROVENANCE,
        "receipt_provenance_kind": RECEIPT_PROVENANCE,
        "upstream_provenance_kind": UPSTREAM_PROVENANCE,
        "fixtures": fixtures,
        "summary": {
            "fixture_count": len(fixtures),
            "fixture_ids": [row["fixture_id"] for row in fixtures],
            "parent_dispatch_count": source_result["summary"]["dispatch_record_count"],
            "receipt_count": len(receipts),
            "per_body_receipt_counts": {
                str(body_id): sum(
                    row["motor_neuron_body_id"] == body_id for row in receipts
                )
                for body_id in sorted({row["motor_neuron_body_id"] for row in receipts})
            },
            "target_class_counts": {
                target_class: sum(
                    row["target_semantics"]["target_class"] == target_class
                    for row in receipts
                )
                for target_class in sorted(
                    {row["target_semantics"]["target_class"] for row in receipts}
                )
            },
            "all_dispatches_have_one_receipt": len(receipts)
            == source_result["summary"]["dispatch_record_count"]
            and {row["parent_dispatch_id"] for row in receipts}
            == {
                dispatch["dispatch_id"]
                for fixture in source_result["fixtures"]
                for dispatch in fixture["dispatch_records"]
            },
            "no_dlm_receipts": all(
                row["motor_neuron_type"] == "TTMn" for row in receipts
            ),
            "no_muscle_state": True,
        },
        "scientific_boundary": payload["scientific_boundary"],
    }
    result["result_sha256"] = canonical_sha256(result)
    return payload, result


def validate_and_replay_payload(
    config: dict[str, Any],
    result: dict[str, Any],
    source: LoadedModelDerivedTTMnTargetArtifact,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(config, dict) or not isinstance(result, dict):
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8Q config and result must be JSON objects"
        )
    expected_config, expected_result = execute_reference_battery(
        source, target_contract_path
    )
    if config != expected_config or result != expected_result:
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8Q artifact differs from its replayed Phase 8O source"
        )
    return expected_config, expected_result


def replay_source_dispatch_artifact(
    source_phase8o_artifact: str | Path = DEFAULT_PHASE8O_ARTIFACT,
    *,
    source_ttmn_artifact: str | Path = DEFAULT_PHASE8N_ARTIFACT,
    source_phase8b_artifact: str | Path = DEFAULT_PHASE8B_SOURCE_ARTIFACT,
    source_root: str | Path = DEFAULT_SOURCE_ROOT,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> LoadedModelDerivedTTMnTargetArtifact:
    try:
        return replay_model_derived_ttmn_target_artifact(
            source_phase8o_artifact,
            source_ttmn_artifact=source_ttmn_artifact,
            source_phase8b_artifact=source_phase8b_artifact,
            source_root=source_root,
            target_contract_path=target_contract_path,
        )
    except (
        OSError,
        ValueError,
        ModelDerivedTTMnDispatchError,
        ModelDerivedTTMnTargetArtifactError,
    ) as exc:
        raise TTMNeuromuscularInputReceiptError(
            "Phase 8O source failed full offline replay"
        ) from exc


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "CONFIG_SCHEMA_VERSION",
    "DEFAULT_ARTIFACT_ROOT",
    "DEFAULT_PHASE8O_ARTIFACT",
    "EXPECTED_PHASE8O_ARTIFACT_ID",
    "RECEIPT_PROVENANCE",
    "RECEIPT_SCHEMA_VERSION",
    "RESULT_SCHEMA_VERSION",
    "TTMNeuromuscularInputReceiptError",
    "canonical_sha256",
    "execute_reference_battery",
    "replay_source_dispatch_artifact",
    "validate_and_replay_payload",
]
