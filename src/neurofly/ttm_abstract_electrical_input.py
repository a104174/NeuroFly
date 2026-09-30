"""Phase 8W: admission-only TTM-class tokens, without physical input semantics."""

from __future__ import annotations

import copy
from pathlib import Path

from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_neuromuscular_input_receipt import (
    DEFAULT_ARTIFACT_ROOT as RECEIPT_ARTIFACT_ROOT,
)
from neurofly.ttm_neuromuscular_input_receipt_artifacts import (
    replay_ttm_neuromuscular_input_receipt_artifact,
)

EVENT_SCHEMA_VERSION = "ttm_abstract_electrical_input_event_v1"
CONTRACT_SCHEMA_VERSION = "ttm_abstract_electrical_input_contract_v1"
CONFIG_SCHEMA_VERSION = "ttm_abstract_electrical_input_config_v1"
RESULT_SCHEMA_VERSION = "ttm_abstract_electrical_input_result_v1"
ARTIFACT_SCHEMA_VERSION = "ttm_abstract_electrical_input_artifact_v1"
SOURCE_ID = "e04803f60304f58d0e6d27fdea5d15debb60358b46721caac09f10165c6df9c4"
SOURCE_CONFIG_SHA256 = (
    "826e326e98dda35113f776867561a9bb777f52035cacba104d49eacccd55a8f3"
)
SOURCE_RESULT_SHA256 = (
    "a243de98a5f67c4a7dd77313524b979f3165812f53f0c4f2b7c3c52288a667dc"
)
DEFAULT_SOURCE_ARTIFACT = RECEIPT_ARTIFACT_ROOT / SOURCE_ID
PROVENANCE = "EXPLORATORY_ABSTRACT_ELECTRICAL_INPUT"
INPUT_SEMANTICS = "ABSTRACT_ELECTRICAL_INPUT_TOKEN"
TIMING_SEMANTICS = "ZERO_ADDED_MODEL_DELAY_ASSUMPTION"
SUCCESS_SEMANTICS = "ONE_RECEIPT_ONE_INPUT_WITHOUT_RELEASE_CLAIM"
BOUNDARIES = (
    "ADMISSION_ONLY_REQUIRES_SEPARATE_MODEL_INPUT_TRANSFORMATION",
    "NO_RELEASE_CLAIM",
    "NO_PHYSICAL_AMPLITUDE",
    "NO_CURRENT_SEMANTICS",
    "NO_CONDUCTANCE_SEMANTICS",
    "NO_QUANTAL_SEMANTICS",
    "NO_G1_MAPPING",
    "NO_EXACT_FIBER_OR_PERIPHERAL_ENDPOINT",
    "NO_MUSCLE_STATE",
    "NO_MODEL_FAMILY_SELECTION",
    "NO_OBSERVATION_COMPARISON",
    "NO_BIOLOGICAL_ZERO_DELAY_CLAIM",
)


class TTMAbstractInputError(ValueError):
    """Invalid source receipt or abstract model-input contract."""


def validated_source(source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT) -> dict:
    """Replay persisted Phase 8Q and its ancestry; never independently make receipts."""
    try:
        artifact = replay_ttm_neuromuscular_input_receipt_artifact(source_artifact)
        if (
            artifact.artifact_id != SOURCE_ID
            or artifact.config["config_sha256"] != SOURCE_CONFIG_SHA256
            or artifact.result["result_sha256"] != SOURCE_RESULT_SHA256
            or artifact.result["summary"]["receipt_count"] != 8
        ):
            raise TTMAbstractInputError("unexpected pinned Phase 8Q identity")
        return copy.deepcopy(dict(artifact.result))
    except (OSError, ValueError, RuntimeError) as exc:
        raise TTMAbstractInputError("Phase 8Q source replay failed") from exc


def event_id(event: dict) -> str:
    """Identity covers the complete semantic envelope, excluding its own ID."""
    return "ttm-abstract-electrical-input-v1:" + canonical_sha256(
        {key: value for key, value in event.items() if key != "event_id"}
    )


def _token(receipt: dict) -> dict:
    target = receipt["target_semantics"]
    event = {
        "schema_version": EVENT_SCHEMA_VERSION,
        "provenance_kind": PROVENANCE,
        "parent_provenance_kind": receipt["provenance_kind"],
        "provenance_chain": [*receipt["provenance_chain"], PROVENANCE],
        "parent_receipt_id": receipt["receipt_id"],
        "source_phase8q_artifact_id": SOURCE_ID,
        "origin_output_event_id": receipt["origin_output_event_id"],
        "source_fixture_id": receipt["source_fixture_id"],
        "source_synthetic_run_id": receipt["source_synthetic_run_id"],
        "motor_neuron_body_id": receipt["motor_neuron_body_id"],
        "motor_neuron_type": receipt["motor_neuron_type"],
        "neural_side": receipt["neural_side"],
        "target_association_id": receipt["target_association_id"],
        "target_contract_id": receipt["target_contract_id"],
        "target_class": target["target_class"],
        "target_granularity": target["target_granularity"],
        "muscle_target_side": target["muscle_target_side"],
        "muscle_target_side_status": target["muscle_target_side_status"],
        "muscle_target_side_basis": target["muscle_target_side_basis"],
        "mapping_confidence": target["mapping_confidence"],
        "mapping_confidence_scope": target["mapping_confidence_scope"],
        "step": receipt["step"],
        "time_ms": receipt["time_ms"],
        "input_semantics_kind": INPUT_SEMANTICS,
        "added_delay_semantics": TIMING_SEMANTICS,
        "success_semantics": SUCCESS_SEMANTICS,
        "biological_transmission_success": "UNREPRESENTED_NOT_ASSERTED",
        "model_family_semantics": "NEUTRAL_REQUIRES_SEPARATE_TRANSFORMATION",
        "scientific_boundary": list(BOUNDARIES),
    }
    event["event_id"] = event_id(event)
    return event


def _admit(receipts: list[dict], source: dict) -> list[dict]:
    if not isinstance(receipts, list):
        raise TTMAbstractInputError("input must be a list of validated receipts")
    canonical = [row for fixture in source["fixtures"] for row in fixture["receipts"]]
    by_id = {row["receipt_id"]: row for row in canonical}
    selected = set()
    for row in receipts:
        if not isinstance(row, dict):
            raise TTMAbstractInputError("only Phase 8Q receipt records are accepted")
        identity = row.get("receipt_id")
        if not isinstance(identity, str) or identity not in by_id:
            raise TTMAbstractInputError("unknown receipt identity")
        if identity in selected:
            raise TTMAbstractInputError("duplicate or conflicting parent receipt")
        # Full equality includes provenance, qualified targets, unresolved fields,
        # and timing; extra fields (including physical magnitude or G1) fail closed.
        if canonical_json_bytes(row) != canonical_json_bytes(by_id[identity]):
            raise TTMAbstractInputError("receipt differs from pinned Phase 8Q source")
        selected.add(identity)
    return [_token(row) for row in canonical if row["receipt_id"] in selected]


def admit_receipts(
    receipts: list[dict], *, source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT
) -> list[dict]:
    """Admit an exact source subset in source order; no inference or physiology."""
    return _admit(receipts, validated_source(source_artifact))


def contract_id(config_hash: str, result_hash: str) -> str:
    return canonical_sha256(
        {
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "config_sha256": config_hash,
            "result_sha256": result_hash,
        }
    )


def _build(source: dict) -> dict:
    config = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "event_schema_version": EVENT_SCHEMA_VERSION,
        "source_phase8q": {
            "artifact_schema_version": "ttm_neuromuscular_input_receipt_artifact_v1",
            "receipt_schema_version": "ttm_neuromuscular_input_receipt_v1",
            "artifact_id": SOURCE_ID,
            "config_sha256": SOURCE_CONFIG_SHA256,
            "result_sha256": SOURCE_RESULT_SHA256,
        },
        "provenance_kind": PROVENANCE,
        "input_semantics_kind": INPUT_SEMANTICS,
        "added_delay_semantics": TIMING_SEMANTICS,
        "success_semantics": SUCCESS_SEMANTICS,
        "scientific_boundary": list(BOUNDARIES),
        "ordering": "PHASE8Q_FIXTURE_AND_RECEIPT_ORDER",
        "duplicate_policy": "REJECT_EXACT_OR_CONFLICTING_PARENT_IDENTITY",
        "admission_policy": "ONE_VALIDATED_RECEIPT_ONE_TOKEN",
        "remaining_input_blocker": "PHYSICAL_MODEL_INPUT_TRANSFORMATION_UNDEFINED",
        "observation_readiness": "NO_FORMAL_COMPARISON_READY",
    }
    fixtures = []
    for fixture in source["fixtures"]:
        receipts = fixture["receipts"]
        fixtures.append(
            {
                "fixture_id": fixture["fixture_id"],
                "source_synthetic_run_id": fixture["source_synthetic_run_id"],
                "source_receipt_ids": [row["receipt_id"] for row in receipts],
                "tokens": _admit(receipts, source),
            }
        )
    tokens = [row for fixture in fixtures for row in fixture["tokens"]]
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "fixtures": fixtures,
        "summary": {
            "receipt_count": sum(len(row["source_receipt_ids"]) for row in fixtures),
            "token_count": len(tokens),
            "per_body_token_counts": {
                str(body): sum(row["motor_neuron_body_id"] == body for row in tokens)
                for body in sorted({row["motor_neuron_body_id"] for row in tokens})
            },
        },
    }
    config_hash, result_hash = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "contract_id": contract_id(config_hash, result_hash),
        "config_sha256": config_hash,
        "result_sha256": result_hash,
        "config": config,
        "result": result,
    }


def build_input_contract(
    *, source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT
) -> dict:
    return _build(validated_source(source_artifact))


def validate_input_contract(
    contract: dict, *, source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT
) -> dict:
    """Reject rehashed mutations as well as hash drift, using exact source replay."""
    expected = build_input_contract(source_artifact=source_artifact)
    if not isinstance(contract, dict) or canonical_json_bytes(
        contract
    ) != canonical_json_bytes(expected):
        raise TTMAbstractInputError("abstract input differs from replayed admission")
    return expected
