"""Phase 8O: dispatch validated Phase 8N TTMn output records to pinned targets.

This module consumes already-persisted model-derived output events. It does
not rerun the threshold rule, derive a new event, or model a muscle response.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from neurofly.motor_neuron_muscle_contract import (
    MotorNeuronMuscleContractError,
    replay_motor_neuron_muscle_target_artifact,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_motor_target_dispatch import (
    DEFAULT_TARGET_CONTRACT_PATH,
    DISPATCH_PROVENANCE,
    SyntheticMotorTargetDispatchError,
    resolve_target_association,
    target_association_id,
)
from neurofly.synthetic_ttmn_output_rule import (
    ARTIFACT_SCHEMA_VERSION as PHASE8N_ARTIFACT_SCHEMA_VERSION,
)
from neurofly.synthetic_ttmn_output_rule import FIXTURE_IDS as PHASE8N_FIXTURE_IDS
from neurofly.synthetic_ttmn_output_rule import (
    GENERATOR_KIND,
    OUTPUT_EVENT_PROVENANCE,
    OUTPUT_EVENT_SCHEMA_VERSION,
)
from neurofly.synthetic_ttmn_output_rule import (
    RESULT_SCHEMA_VERSION as PHASE8N_RESULT_SCHEMA_VERSION,
)
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    DEFAULT_OUTPUT_ROOT as DEFAULT_PHASE8N_OUTPUT_ROOT,
)
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    DEFAULT_SOURCE_ARTIFACT as DEFAULT_PHASE8B_SOURCE_ARTIFACT,
)
from neurofly.synthetic_ttmn_output_rule_artifacts import (
    LoadedSyntheticTTMnOutputArtifact,
)

CONFIG_SCHEMA_VERSION = "model_derived_ttmn_target_dispatch_config_v1"
RESULT_SCHEMA_VERSION = "model_derived_ttmn_target_dispatch_result_v1"
ARTIFACT_SCHEMA_VERSION = "model_derived_ttmn_target_dispatch_artifact_v1"
DISPATCH_SCHEMA_VERSION = "model_derived_muscle_target_dispatch_v1"
TARGET_CONTRACT_SCHEMA_VERSION = "motor_neuron_muscle_target_contract_v1"
EXPECTED_PHASE8N_ARTIFACT_ID = (
    "1c8aeac685646dac16fbb66f163743b662a3cd9a0e8f9f7582210fd7b39b9ab3"
)
EXPECTED_TARGET_CONTRACT_ID = (
    "5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0"
)
UPSTREAM_PROVENANCE = "SYNTHETIC_MOTOR_INTERFACE_TEST"
DISPATCH_SEMANTICS = "TARGET_ASSOCIATION_RECEIPT_ONLY_NO_MUSCLE_DYNAMICS"
TIME_SEMANTICS = "SAME_STORED_BOUNDARY_TARGET_DISPATCH_BOOKKEEPING_ONLY"
DEFAULT_PHASE8N_ARTIFACT = DEFAULT_PHASE8N_OUTPUT_ROOT / EXPECTED_PHASE8N_ARTIFACT_ID
DEFAULT_ARTIFACT_ROOT = DEFAULT_SOURCE_ROOT / ARTIFACT_SCHEMA_VERSION


class ModelDerivedTTMnDispatchError(ValueError):
    """Invalid Phase 8N source event, target identity, or dispatch result."""


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
        raise ModelDerivedTTMnDispatchError(
            "Phase 8O payload must be deterministic JSON"
        ) from exc
    return hashlib.sha256(payload).hexdigest()


def _validate_source_artifact(
    source: LoadedSyntheticTTMnOutputArtifact,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    config = copy.deepcopy(dict(source.config))
    result = copy.deepcopy(dict(source.result))
    manifest = copy.deepcopy(dict(source.manifest))
    config_hash = config.get("config_sha256")
    result_hash = result.get("result_sha256")
    if (
        source.artifact_id != EXPECTED_PHASE8N_ARTIFACT_ID
        or manifest.get("artifact_id") != EXPECTED_PHASE8N_ARTIFACT_ID
        or manifest.get("artifact_schema_version") != PHASE8N_ARTIFACT_SCHEMA_VERSION
        or config.get("artifact_schema_version") != PHASE8N_ARTIFACT_SCHEMA_VERSION
        or result.get("artifact_schema_version") != PHASE8N_ARTIFACT_SCHEMA_VERSION
        or result.get("schema_version") != PHASE8N_RESULT_SCHEMA_VERSION
        or config_hash
        != canonical_sha256(
            {key: value for key, value in config.items() if key != "config_sha256"}
        )
        or result_hash
        != canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        or manifest.get("config_sha256") != config_hash
        or manifest.get("result_sha256") != result_hash
    ):
        raise ModelDerivedTTMnDispatchError(
            "canonical Phase 8N source identity or integrity mismatch"
        )

    generator = config.get("reference_generator_config")
    source_model = config.get("source_phase6c_model")
    fixtures = result.get("fixtures")
    if (
        config.get("schema_version") != "synthetic_ttmn_output_rule_config_v1"
        or not isinstance(generator, dict)
        or generator.get("schema_version")
        != "ttmn_threshold_crossing_generator_config_v1"
        or generator.get("generator_kind") != GENERATOR_KIND
        or generator.get("provenance_kind") != OUTPUT_EVENT_PROVENANCE
        or generator.get("threshold_dimensionless") != 0.25
        or not isinstance(source_model, dict)
        or not isinstance(fixtures, list)
        or [row.get("fixture_id") for row in fixtures] != list(PHASE8N_FIXTURE_IDS)
        or result.get("source_artifact_id")
        != config.get("source_artifact", {}).get("artifact_id")
        or result.get("source_kind") != UPSTREAM_PROVENANCE
        or config.get("provenance", {}).get("upstream_input") != UPSTREAM_PROVENANCE
        or config.get("provenance", {}).get("derived_output") != OUTPUT_EVENT_PROVENANCE
        or config.get("scientific_boundary", {}).get("muscle_target_dispatch")
        is not False
    ):
        raise ModelDerivedTTMnDispatchError(
            "Phase 8N artifact is not the canonical reference generator result"
        )
    return config, result, manifest


def _target_contract(
    artifact_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        artifact = replay_motor_neuron_muscle_target_artifact(artifact_path)
    except (OSError, ValueError, MotorNeuronMuscleContractError) as exc:
        raise ModelDerivedTTMnDispatchError(
            "pinned Phase 8K target contract failed replay"
        ) from exc
    contract = copy.deepcopy(dict(artifact.contract))
    if (
        artifact.artifact_id != EXPECTED_TARGET_CONTRACT_ID
        or contract.get("schema_version") != TARGET_CONTRACT_SCHEMA_VERSION
        or contract.get("contract_id") != EXPECTED_TARGET_CONTRACT_ID
        or contract.get("contract_semantics")
        != "NO_DYNAMICS_LITERATURE_SUPPORTED_TARGET_ASSOCIATIONS"
        or contract.get("mapping_policy", {}).get("dynamics") != "NO_DYNAMICS"
    ):
        raise ModelDerivedTTMnDispatchError("unsupported Phase 8K target contract")
    ttmn_rows = [
        row
        for row in contract.get("target_associations", [])
        if row.get("motor_neuron_type") == "TTMn"
    ]
    if len(ttmn_rows) != 2:
        raise ModelDerivedTTMnDispatchError(
            "pinned target contract must expose exactly two TTMn associations"
        )
    return contract, {
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


def _source_fixture_rows(
    source: LoadedSyntheticTTMnOutputArtifact,
) -> list[dict[str, Any]]:
    _, result, _ = _validate_source_artifact(source)
    rows = copy.deepcopy(result["fixtures"])
    for fixture in rows:
        events = fixture.get("reference_output_events")
        if not isinstance(events, list):
            raise ModelDerivedTTMnDispatchError(
                "Phase 8N fixture output event list is malformed"
            )
        if fixture.get("source_kind") != UPSTREAM_PROVENANCE:
            raise ModelDerivedTTMnDispatchError(
                "Phase 8N fixture has unsupported upstream provenance"
            )
    return rows


def _association_fields(association: dict[str, Any]) -> dict[str, Any]:
    keys = (
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
    return {key: copy.deepcopy(association[key]) for key in keys}


def _validate_event(
    event: dict[str, Any],
    *,
    fixture: dict[str, Any],
    source: LoadedSyntheticTTMnOutputArtifact,
    source_config: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise ModelDerivedTTMnDispatchError("Phase 8N output event is malformed")
    event_body_id = event.get("motor_neuron_body_id")
    event_type = event.get("motor_neuron_type")
    event_side = event.get("neural_side")
    source_result = event.get("source_result")
    generator = source_config["reference_generator_config"]
    trajectories = {
        row["body_id"]: row for row in fixture.get("source_trajectories", [])
    }
    trajectory = trajectories.get(event_body_id)
    expected_source = {
        "artifact_id": fixture.get("source_artifact_id"),
        "result_sha256": fixture.get("source_result_sha256"),
        "fixture_id": fixture.get("fixture_id"),
        "fixture_result_sha256": fixture.get("source_fixture_sha256"),
        "fixture_config_sha256": fixture.get("fixture_config_sha256"),
        "synthetic_run_id": fixture.get("synthetic_run_id"),
        "trajectory_sha256": trajectory.get("trajectory_sha256")
        if trajectory is not None
        else None,
        "state_unit": "dimensionless",
    }
    if (
        source.artifact_id != EXPECTED_PHASE8N_ARTIFACT_ID
        or event not in fixture.get("reference_output_events", [])
        or event.get("schema_version") != OUTPUT_EVENT_SCHEMA_VERSION
        or event.get("provenance_kind") != OUTPUT_EVENT_PROVENANCE
        or event.get("upstream_provenance_kind") != UPSTREAM_PROVENANCE
        or event.get("generator_kind") != GENERATOR_KIND
        or event.get("generator_config_sha256") != canonical_sha256(generator)
        or event.get("semantics")
        != "EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT_EVENT"
        or event.get("biological_action_potential_claim") is not False
        or event.get("source_model") != source_config["source_phase6c_model"]
        or source_result != expected_source
        or event.get("step") is None
        or isinstance(event.get("step"), bool)
        or not isinstance(event.get("step"), int)
        or event["step"] < 0
        or isinstance(event.get("time_ms"), bool)
        or not isinstance(event.get("time_ms"), (int, float))
        or not math.isfinite(event["time_ms"])
        or event.get("event_id")
        != canonical_sha256(
            {key: value for key, value in event.items() if key != "event_id"}
        )
        or event_type != "TTMn"
        or trajectory is None
        or trajectory.get("neuron_type") != event_type
        or trajectory.get("side") != event_side
        or trajectory.get("state_unit") != "dimensionless"
    ):
        raise ModelDerivedTTMnDispatchError(
            "Phase 8N output event identity, provenance, or source binding is invalid"
        )
    try:
        association = resolve_target_association(
            contract,
            motor_neuron_body_id=event_body_id,
            motor_neuron_type=event_type,
            neural_side=event_side,
        )
    except SyntheticMotorTargetDispatchError as exc:
        raise ModelDerivedTTMnDispatchError(
            "Phase 8N TTMn identity is not authorized by the Phase 8K contract"
        ) from exc
    if association["motor_neuron_type"] != "TTMn":
        raise ModelDerivedTTMnDispatchError(
            "Phase 8O accepts only TTMn model-derived output events"
        )
    return association


def _dispatch_event(
    event: dict[str, Any],
    association: dict[str, Any],
    *,
    source: LoadedSyntheticTTMnOutputArtifact,
    contract: dict[str, Any],
) -> dict[str, Any]:
    association_id = target_association_id(association)
    source_result = event["source_result"]
    semantic = {
        "schema_version": DISPATCH_SCHEMA_VERSION,
        "origin_output_event_id": event["event_id"],
        "source_output_artifact_id": source.artifact_id,
        "source_output_result_sha256": source.result["result_sha256"],
        "target_association_id": association_id,
        "target_contract_id": contract["contract_id"],
        "step": event["step"],
        "time_ms": event["time_ms"],
    }
    return {
        **semantic,
        "dispatch_id": (
            f"model-derived-muscle-target-dispatch-v1:{canonical_sha256(semantic)}"
        ),
        "source_output_config_sha256": source.config["config_sha256"],
        "source_generator_kind": event["generator_kind"],
        "source_generator_config_sha256": event["generator_config_sha256"],
        "source_fixture_id": source_result["fixture_id"],
        "source_fixture_config_sha256": source_result["fixture_config_sha256"],
        "source_fixture_result_sha256": source_result["fixture_result_sha256"],
        "source_synthetic_run_id": source_result["synthetic_run_id"],
        "upstream_provenance_kind": event["upstream_provenance_kind"],
        "origin_provenance_kind": event["provenance_kind"],
        "provenance_kind": DISPATCH_PROVENANCE,
        "target_contract_sha256": contract["contract_sha256"],
        **_association_fields(association),
        "time_semantics": TIME_SEMANTICS,
        "dispatch_semantics": DISPATCH_SEMANTICS,
    }


def _execute_fixture(
    fixture: dict[str, Any],
    *,
    source: LoadedSyntheticTTMnOutputArtifact,
    source_config: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    source_result = dict(source.result)
    raw_events = fixture.get("reference_output_events")
    if not isinstance(raw_events, list):
        raise ModelDerivedTTMnDispatchError("Phase 8N fixture event list is malformed")
    source_fixture = {
        **fixture,
        "source_artifact_id": source_result["source_artifact_id"],
        "source_result_sha256": source_result["source_result_sha256"],
    }
    events = copy.deepcopy(raw_events)
    event_ids = [event.get("event_id") for event in events if isinstance(event, dict)]
    if len(event_ids) != len(events) or len(event_ids) != len(set(event_ids)):
        raise ModelDerivedTTMnDispatchError(
            "Phase 8N fixture has malformed or duplicate output event identities"
        )
    associations = [
        _validate_event(
            event,
            fixture=source_fixture,
            source=source,
            source_config=source_config,
            contract=contract,
        )
        for event in events
    ]
    dispatches = [
        _dispatch_event(
            event,
            association,
            source=source,
            contract=contract,
        )
        for event, association in zip(events, associations, strict=True)
    ]
    dispatches.sort(
        key=lambda row: (
            row["step"],
            row["motor_neuron_body_id"],
            row["origin_output_event_id"],
        )
    )
    return {
        "fixture_id": fixture["fixture_id"],
        "source_fixture_config_sha256": fixture["fixture_config_sha256"],
        "source_fixture_result_sha256": fixture["source_fixture_sha256"],
        "source_synthetic_run_id": fixture["synthetic_run_id"],
        "upstream_provenance_kind": fixture["source_kind"],
        "origin_output_events": events,
        "dispatch_records": dispatches,
        "summary": {
            "model_derived_output_event_count": len(events),
            "dispatch_record_count": len(dispatches),
            "no_dlm_dispatches": all(
                row["motor_neuron_type"] == "TTMn" for row in dispatches
            ),
            "no_muscle_dynamics": True,
        },
    }


def build_reference_config(
    source: LoadedSyntheticTTMnOutputArtifact,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> dict[str, Any]:
    source_config, source_result, source_manifest = _validate_source_artifact(source)
    contract, contract_reference = _target_contract(target_contract_path)
    source_model = source_config["source_phase6c_model"]
    source_generator = source_config["reference_generator_config"]
    payload: dict[str, Any] = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "source_ttmn_output_artifact": {
            "artifact_id": source.artifact_id,
            "artifact_schema_version": source_manifest["artifact_schema_version"],
            "config_sha256": source_config["config_sha256"],
            "result_sha256": source_result["result_sha256"],
            "source_phase8b_artifact_id": source_result["source_artifact_id"],
            "upstream_provenance_kind": source_result["source_kind"],
        },
        "source_phase6c_model_identity": {
            "model_id": source_model["model_id"],
            "model_version": source_model["model_version"],
            "config_sha256": source_model["config_sha256"],
        },
        "source_generator": {
            "schema_version": source_generator["schema_version"],
            "generator_kind": source_generator["generator_kind"],
            "config_sha256": canonical_sha256(source_generator),
            "provenance_kind": source_generator["provenance_kind"],
        },
        "source_event_schema_version": OUTPUT_EVENT_SCHEMA_VERSION,
        "source_event_provenance_kind": OUTPUT_EVENT_PROVENANCE,
        "target_contract": contract_reference,
        "dispatch_schema_version": DISPATCH_SCHEMA_VERSION,
        "dispatch_provenance_kind": DISPATCH_PROVENANCE,
        "fixture_ids": [row["fixture_id"] for row in source_result["fixtures"]],
        "provenance_chain": [
            UPSTREAM_PROVENANCE,
            "PHASE_6C_TTMN_DIMENSIONLESS_EXPLORATORY_STATE",
            OUTPUT_EVENT_PROVENANCE,
            DISPATCH_PROVENANCE,
        ],
        "scientific_boundary": {
            "source_events_are_recomputed": False,
            "threshold_rule_is_reapplied": False,
            "target_resolution_source": "PINNED_PHASE_8K_CONTRACT_ONLY",
            "dispatch_semantics": DISPATCH_SEMANTICS,
            "muscle_activation_created": False,
            "neuromuscular_model": False,
            "dlmn_output_generation": False,
            "production_sensory_source": False,
            "behavior_model": False,
        },
    }
    payload["config_sha256"] = canonical_sha256(payload)
    # Ensures the source event battery and target contract were both validated
    # before a content-addressed run can be produced.
    _source_fixture_rows(source)
    return payload


def execute_reference_battery(
    source: LoadedSyntheticTTMnOutputArtifact,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_config, source_result, _ = _validate_source_artifact(source)
    contract, contract_reference = _target_contract(target_contract_path)
    config = build_reference_config(source, target_contract_path)
    fixtures = [
        _execute_fixture(
            fixture,
            source=source,
            source_config=source_config,
            contract=contract,
        )
        for fixture in source_result["fixtures"]
    ]
    events = [
        event for fixture in fixtures for event in fixture["origin_output_events"]
    ]
    dispatches = [row for fixture in fixtures for row in fixture["dispatch_records"]]
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "config_sha256": config["config_sha256"],
        "source_ttmn_output_artifact_id": source.artifact_id,
        "source_ttmn_output_result_sha256": source_result["result_sha256"],
        "target_contract_id": contract["contract_id"],
        "target_contract_sha256": contract["contract_sha256"],
        "source_event_provenance_kind": OUTPUT_EVENT_PROVENANCE,
        "upstream_provenance_kind": UPSTREAM_PROVENANCE,
        "dispatch_provenance_kind": DISPATCH_PROVENANCE,
        "fixtures": fixtures,
        "summary": {
            "fixture_count": len(fixtures),
            "fixture_ids": [row["fixture_id"] for row in fixtures],
            "model_derived_output_event_count": len(events),
            "dispatch_record_count": len(dispatches),
            "per_body_event_counts": {
                str(body_id): sum(
                    event["motor_neuron_body_id"] == body_id for event in events
                )
                for body_id in sorted(
                    {event["motor_neuron_body_id"] for event in events}
                )
            },
            "target_class_counts": {
                target_class: sum(
                    row["target_class"] == target_class for row in dispatches
                )
                for target_class in sorted({row["target_class"] for row in dispatches})
            },
            "all_events_dispatched_once": len(events) == len(dispatches)
            and {event["event_id"] for event in events}
            == {row["origin_output_event_id"] for row in dispatches},
            "no_dlm_dispatches": all(
                row["motor_neuron_type"] == "TTMn" for row in dispatches
            ),
            "no_muscle_dynamics": True,
        },
        "scientific_boundary": config["scientific_boundary"],
    }
    result["result_sha256"] = canonical_sha256(result)
    if contract_reference["artifact_id"] != result["target_contract_id"]:
        raise ModelDerivedTTMnDispatchError("target contract identity changed")
    return config, result


def validate_and_replay_payload(
    config: dict[str, Any],
    result: dict[str, Any],
    source: LoadedSyntheticTTMnOutputArtifact,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(config, dict) or not isinstance(result, dict):
        raise ModelDerivedTTMnDispatchError("Phase 8O payload must be JSON objects")
    expected_config, expected_result = execute_reference_battery(
        source, target_contract_path
    )
    if config != expected_config:
        raise ModelDerivedTTMnDispatchError(
            "Phase 8O config differs from the replayed 8N/8K sources"
        )
    if result != expected_result:
        raise ModelDerivedTTMnDispatchError(
            "Phase 8O result differs from deterministic target dispatch replay"
        )
    return expected_config, expected_result


def fixture_result(
    fixture_id: str,
    source: LoadedSyntheticTTMnOutputArtifact,
    target_contract_path: str | Path = DEFAULT_TARGET_CONTRACT_PATH,
) -> dict[str, Any]:
    if fixture_id not in PHASE8N_FIXTURE_IDS:
        raise ModelDerivedTTMnDispatchError("unknown Phase 8N source fixture")
    _, result = execute_reference_battery(source, target_contract_path)
    return copy.deepcopy(
        next(row for row in result["fixtures"] if row["fixture_id"] == fixture_id)
    )


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "CONFIG_SCHEMA_VERSION",
    "DEFAULT_ARTIFACT_ROOT",
    "DEFAULT_PHASE8B_SOURCE_ARTIFACT",
    "DEFAULT_PHASE8N_ARTIFACT",
    "DEFAULT_TARGET_CONTRACT_PATH",
    "DISPATCH_PROVENANCE",
    "DISPATCH_SCHEMA_VERSION",
    "EXPECTED_PHASE8N_ARTIFACT_ID",
    "EXPECTED_TARGET_CONTRACT_ID",
    "ModelDerivedTTMnDispatchError",
    "RESULT_SCHEMA_VERSION",
    "build_reference_config",
    "canonical_sha256",
    "execute_reference_battery",
    "fixture_result",
    "validate_and_replay_payload",
]
