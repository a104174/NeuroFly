"""Phase 8U: metadata for future G1 comparability; no executable operators."""

from __future__ import annotations

import copy
from pathlib import Path

from neurofly.ttm_g1_electrophysiology_observation_artifacts import (
    DEFAULT_ARTIFACT_ROOT as SOURCE_ARTIFACT_ROOT,
)
from neurofly.ttm_g1_electrophysiology_observation_artifacts import (
    replay_ttm_g1_observation_artifact,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    ARTIFACT_SCHEMA_VERSION as SOURCE_ARTIFACT_SCHEMA,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    CONTRACT_SCHEMA_VERSION as SOURCE_CONTRACT_SCHEMA,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_sha256,
)

CONTRACT_SCHEMA_VERSION = "ttm_g1_observation_mapping_v1"
CONFIG_SCHEMA_VERSION = "ttm_g1_observation_mapping_config_v1"
RESULT_SCHEMA_VERSION = "ttm_g1_observation_mapping_result_v1"
RECORD_SCHEMA_VERSION = "ttm_g1_observation_mapping_record_v1"
ARTIFACT_SCHEMA_VERSION = "ttm_g1_observation_mapping_artifact_v1"
SOURCE_ID = "5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f"
SOURCE_CONFIG_SHA256 = (
    "4c389614939cdf77c1aa545d25734eb810e829dae43c0c72aa1a18cbc378a48e"
)
SOURCE_RESULT_SHA256 = (
    "fb45ac6689c411774dc2e1c2ea6d2ac6f4fa324388b24ecb010df795560fa58b"
)
DEFAULT_SOURCE_ARTIFACT = SOURCE_ARTIFACT_ROOT / SOURCE_ID

# Exact source coverage is pinned, independently of any caller's record order.
SOURCE_OBSERVATION_IDS = (
    "ttm-g1-obs-21076e7816c87359e80f",
    "ttm-g1-obs-0e8110027289e2606870",
    "ttm-g1-obs-00171dce33f34d595a05",
    "ttm-g1-obs-87c7df503a4c6d752ea0",
    "ttm-g1-obs-cade4bdd5192612a0423",
    "ttm-g1-obs-399d70f32a656dea7a85",
    "ttm-g1-obs-745604f564d9f4c315d4",
    "ttm-g1-obs-61e331f15399e1627634",
    "ttm-g1-obs-24852cd49c1395db8e8c",
)

BLOCKER_TAXONOMY = {
    "MISSING_OBSERVATION_OPERATOR": (
        "Candidate measurement semantics have no executable operator."
    ),
    "SOURCE_PROTOCOL_INCOMPLETE": (
        "Relevant source protocol dimensions remain unverified or unreported."
    ),
    "MODEL_QUANTITY_ABSENT": (
        "Current NeuroFly output does not expose the required quantity."
    ),
    "RELEASE_SEMANTICS_ABSENT": (
        "Receipts and output-event counts do not represent release or quanta."
    ),
    "SPONTANEOUS_PROCESS_ABSENT": "No spontaneous miniature-event process exists.",
    "HISTORY_DYNAMICS_ABSENT": "No response-history or depression model exists.",
    "VESICLE_MODEL_ABSENT": (
        "No vesicle-state, recycling, or active-zone accounting exists."
    ),
    "SYSTEM_BOUNDARY_TOO_NARROW": (
        "Phase 8Q starts after the experimental motor-neuron-region stimulus."
    ),
    "ONSET_DETECTOR_UNRESOLVED": (
        "The numerical initial-potential-onset operation is not pinned."
    ),
    "INPUT_SEMANTICS_UNDEFINED": "A Phase 8Q handoff has no electrical-input meaning.",
    "PROTOCOL_MATCH_UNRESOLVED": (
        "Source and future simulation protocol matching has not been established."
    ),
    "DESCRIPTIVE_SOURCE_NO_NUMERICAL_COMPARISON_RULE": (
        "An approximate context value supplies no formal numerical comparison rule."
    ),
    "SOURCE_AMPLITUDE_OPERATION_UNRESOLVED": (
        "Original amplitude definition and observation window are incomplete."
    ),
    "MINIATURE_DETECTOR_UNRESOLVED": (
        "Miniature selection, baseline, and amplitude summary need specification."
    ),
    "OBSERVATION_INTERVAL_UNRESOLVED": (
        "Spontaneous-event detection and observation interval need specification."
    ),
    "DEPRESSION_DEFINITION_UNRESOLVED": (
        "The protocol-specific depression outcome needs an operational definition."
    ),
    "SOURCE_CORRECTION_PIPELINE_ABSENT": (
        "No justified source-matched quantal correction pipeline exists."
    ),
    "NO_DIRECT_COMPARISON_INTENDED": (
        "This prior-source analysis input has context-only meaning."
    ),
}

QUANTITIES = {
    "G1_MEMBRANE_VOLTAGE_TRACE",
    "G1_SINGLE_QUANTAL_ELECTRICAL_EVENTS",
    "G1_SPONTANEOUS_MINIATURE_EVENTS",
    "RELEASE_QUANTAL_OUTPUT_OR_MATCHED_CORRECTION_INPUTS",
    "STIMULUS_ALIGNED_RESPONSE_SERIES",
    "VESICLE_RECYCLING_OUTPUT",
    "FULL_TTMN_STIMULUS_TO_TTM_RESPONSE_PATH",
    "NO_DIRECT_MODEL_QUANTITY",
}
OPERATORS = {
    "PRE_STIMULUS_BASELINE",
    "PEAK_EVOKED_DEFLECTION",
    "MINIATURE_EVENT_AMPLITUDE",
    "SPONTANEOUS_EVENT_RATE",
    "REPEATED_RESPONSE_OUTCOME",
    "DERIVED_QUANTAL_CONTENT",
    "DERIVED_RECYCLING_RATE",
    "INITIAL_TTM_POTENTIAL_ONSET",
    "CONTEXT_ONLY",
}
OPERATOR_STATUSES = {
    "CANDIDATE_ONLY",
    "SOURCE_SEMANTICS_INCOMPLETE",
    "REQUIRES_ADDITIONAL_PHYSIOLOGY",
    "SYSTEM_BOUNDARY_MISMATCH",
    "CONTEXT_ONLY",
}
COMPARABILITIES = {
    "MODEL_OBSERVABLE_WITH_OPERATOR",
    "REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL",
    "SYSTEM_BOUNDARY_MISMATCH",
    "CONTEXT_ONLY",
    "UNRESOLVED",
}
ROLES = {
    "FUTURE_VALIDATION_CANDIDATE",
    "QUALITATIVE_SANITY_CONTEXT",
    "ANALYSIS_CONTEXT_ONLY",
    "NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL",
    "SYSTEM_LEVEL_VALIDATION_CANDIDATE",
}


class TTMG1ObservationMappingError(ValueError):
    """Invalid source identity, mapping semantics, or readiness claim."""


def validated_source(source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT) -> dict:
    """Replay persisted Phase 8S and require the exact pinned source population."""
    source = replay_ttm_g1_observation_artifact(source_artifact)
    contract = copy.deepcopy(dict(source.contract))
    if (
        source.artifact_id != SOURCE_ID
        or contract["schema_version"] != SOURCE_CONTRACT_SCHEMA
        or contract["config_sha256"] != SOURCE_CONFIG_SHA256
        or contract["result_sha256"] != SOURCE_RESULT_SHA256
        or contract["result"]["observation_count"] != 9
        or tuple(row["observation_id"] for row in contract["result"]["observations"])
        != SOURCE_OBSERVATION_IDS
    ):
        raise TTMG1ObservationMappingError(
            "Phase 8S source identity or coverage mismatch"
        )
    return contract


def mapping_id(record: dict) -> str:
    return (
        "ttm-g1-map-"
        + canonical_sha256(
            {key: value for key, value in record.items() if key != "mapping_id"}
        )[:20]
    )


def artifact_id(config_hash: str, result_hash: str) -> str:
    return canonical_sha256(
        {
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
            "config_sha256": config_hash,
            "result_sha256": result_hash,
        }
    )


def _definition_rows() -> list[tuple]:
    # Each tuple adds mapping metadata only. Empirical values are never copied.
    common = (
        "MODEL_QUANTITY_ABSENT",
        "MISSING_OBSERVATION_OPERATOR",
        "PROTOCOL_MATCH_UNRESOLVED",
    )
    g1 = (
        "species",
        "developmental_age",
        "sex",
        "genotype",
        "temperature_c",
        "preparation",
        "recording_fiber",
        "recording_site",
        "recording_mode",
    )
    evoked = g1 + ("stimulation_site", "stimulation_pulse_ms", "stimulus_history")
    train = evoked + (
        "stimulation_frequency_hz",
        "stimulus_count",
        "recycling_condition",
    )
    return [
        (
            "G1_MEMBRANE_VOLTAGE_TRACE",
            "PRE_STIMULUS_BASELINE",
            "CANDIDATE_ONLY",
            "MODEL_OBSERVABLE_WITH_OPERATOR",
            "QUALITATIVE_SANITY_CONTEXT",
            common
            + (
                "SOURCE_PROTOCOL_INCOMPLETE",
                "DESCRIPTIVE_SOURCE_NO_NUMERICAL_COMPARISON_RULE",
            ),
            g1,
            (
                "Specify equilibration and baseline sampling without inventing "
                "a numerical acceptance window.",
            ),
        ),
        (
            "G1_MEMBRANE_VOLTAGE_TRACE",
            "PEAK_EVOKED_DEFLECTION",
            "SOURCE_SEMANTICS_INCOMPLETE",
            "UNRESOLVED",
            "FUTURE_VALIDATION_CANDIDATE",
            common
            + (
                "SOURCE_PROTOCOL_INCOMPLETE",
                "SOURCE_AMPLITUDE_OPERATION_UNRESOLVED",
                "INPUT_SEMANTICS_UNDEFINED",
            ),
            evoked,
            (
                "Recover the original 2005 protocol and exact amplitude "
                "operation/window before comparison.",
                "Baseline deflection is a candidate, not an executable "
                "definition or input gain.",
            ),
        ),
        (
            "G1_SINGLE_QUANTAL_ELECTRICAL_EVENTS",
            "MINIATURE_EVENT_AMPLITUDE",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL",
            "NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL",
            common + ("RELEASE_SEMANTICS_ABSENT", "MINIATURE_DETECTOR_UNRESOLVED"),
            g1 + ("stimulus_history",),
            (
                "Specify single-quantal/miniature electrical-event semantics; "
                "Phase 8Q receipts cannot substitute.",
            ),
        ),
        (
            "NO_DIRECT_MODEL_QUANTITY",
            "CONTEXT_ONLY",
            "CONTEXT_ONLY",
            "CONTEXT_ONLY",
            "ANALYSIS_CONTEXT_ONLY",
            ("NO_DIRECT_COMPARISON_INTENDED", "SOURCE_PROTOCOL_INCOMPLETE"),
            ("correction_method", "recording_fiber"),
            (
                "Preserve prior-source analysis context; verify the original "
                "source before any future parameter interpretation.",
            ),
        ),
        (
            "RELEASE_QUANTAL_OUTPUT_OR_MATCHED_CORRECTION_INPUTS",
            "DERIVED_QUANTAL_CONTENT",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL",
            "NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL",
            common + ("RELEASE_SEMANTICS_ABSENT", "SOURCE_CORRECTION_PIPELINE_ABSENT"),
            evoked + ("stimulus_count", "correction_method"),
            (
                "Require release/quantal output or a justified source-matched "
                "correction with its linked Phase 8S inputs.",
                "Receipt or output-event counts must not stand in for quanta.",
            ),
        ),
        (
            "G1_SPONTANEOUS_MINIATURE_EVENTS",
            "SPONTANEOUS_EVENT_RATE",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL",
            "NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL",
            common
            + (
                "SPONTANEOUS_PROCESS_ABSENT",
                "OBSERVATION_INTERVAL_UNRESOLVED",
                "MINIATURE_DETECTOR_UNRESOLVED",
            ),
            g1 + ("stimulus_history",),
            (
                "Specify spontaneous process, detector, observation interval "
                "and protocol matching.",
                "Source uncertainty kind remains solely under Phase 8S authority.",
            ),
        ),
        (
            "STIMULUS_ALIGNED_RESPONSE_SERIES",
            "REPEATED_RESPONSE_OUTCOME",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL",
            "NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL",
            common
            + (
                "HISTORY_DYNAMICS_ABSENT",
                "DEPRESSION_DEFINITION_UNRESOLVED",
                "INPUT_SEMANTICS_UNDEFINED",
            ),
            train,
            (
                "Require response-amplitude/history semantics and a "
                "protocol-specific depression definition.",
                "A categorical outcome supplies no numerical dynamics coefficient.",
            ),
        ),
        (
            "VESICLE_RECYCLING_OUTPUT",
            "DERIVED_RECYCLING_RATE",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY",
            "REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL",
            "NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL",
            common + ("VESICLE_MODEL_ABSENT", "HISTORY_DYNAMICS_ABSENT"),
            train + ("correction_method",),
            (
                "Require vesicle/recycling semantics, active-zone accounting "
                "and the source comparison denominator.",
            ),
        ),
        (
            "FULL_TTMN_STIMULUS_TO_TTM_RESPONSE_PATH",
            "INITIAL_TTM_POTENTIAL_ONSET",
            "SYSTEM_BOUNDARY_MISMATCH",
            "SYSTEM_BOUNDARY_MISMATCH",
            "SYSTEM_LEVEL_VALIDATION_CANDIDATE",
            common
            + (
                "SYSTEM_BOUNDARY_TOO_NARROW",
                "ONSET_DETECTOR_UNRESOLVED",
                "SOURCE_PROTOCOL_INCOMPLETE",
                "INPUT_SEMANTICS_UNDEFINED",
            ),
            (
                "species",
                "developmental_age",
                "sex",
                "genotype",
                "temperature_c",
                "preparation",
                "stimulation_site",
                "recording_site",
                "recording_method",
                "recording_mode",
            ),
            (
                "Require motor-neuron-region stimulation through axonal "
                "conduction and initial TTM potential onset.",
                "Resolve time reference and onset detector; Phase 8Q receipt "
                "timing cannot substitute for the full path.",
            ),
        ),
    ]


def _build(source: dict) -> dict:
    records = []
    required_semantics = (
        ["EQUILIBRATION_AND_BASELINE_SAMPLING"],
        ["ORIGINAL_SOURCE_PROTOCOL", "AMPLITUDE_OPERATION_AND_WINDOW"],
        ["MINIATURE_EVENT_SELECTION_AND_AMPLITUDE"],
        ["PRIOR_SOURCE_APPLICABILITY"],
        ["QUANTAL_COUNT_OR_MATCHED_CORRECTION"],
        ["EVENT_DETECTOR_AND_OBSERVATION_INTERVAL"],
        ["OPERATIONAL_DEPRESSION_DEFINITION"],
        ["RECYCLING_COMPARISON_AND_ACTIVE_ZONE_DENOMINATOR"],
        ["STIMULUS_TIME_REFERENCE", "CONTROL_CONDITION", "INITIAL_ONSET_DETECTOR"],
    )
    for observation, definition in zip(
        source["result"]["observations"], _definition_rows(), strict=True
    ):
        (
            quantity,
            operator,
            status,
            comparability,
            role,
            blockers,
            dimensions,
            unresolved,
        ) = definition
        record = {
            "schema_version": RECORD_SCHEMA_VERSION,
            "source_observation_contract_id": SOURCE_ID,
            "observation_id": observation["observation_id"],
            "required_model_quantity": quantity,
            "candidate_operator_kind": operator,
            "operator_status": status,
            "operator_executable": False,
            "comparability": comparability,
            "comparison_role": role,
            "current_model_produces_quantity": False,
            "formal_comparison_ready": False,
            "blockers": sorted(blockers),
            "unresolved_requirements": list(unresolved),
            "protocol_requirements": {
                "source_observation_id": observation["observation_id"],
                "biological_scope_ref": "biological_scope",
                "source_context_refs": ["source_locations"],
                "required_dimensions": sorted(set(dimensions)),
                "source_status_refs": {
                    key: f"protocol.dimension_status.{key}"
                    for key in sorted(set(dimensions))
                },
                "unknown_source_policy": "REQUIRES_SOURCE_CLARIFICATION_NEVER_WILDCARD",
                "missing_model_policy": "UNRESOLVED_NEVER_COMPATIBLE_BY_DEFAULT",
                "match_status": "NOT_EVALUATED",
                "additional_semantics": list(unresolved),
                "required_additional_semantics": required_semantics[len(records)],
            },
        }
        record["mapping_id"] = mapping_id(record)
        records.append(record)
    config = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "source_observation_contract": {
            "schema_version": SOURCE_CONTRACT_SCHEMA,
            "artifact_schema_version": SOURCE_ARTIFACT_SCHEMA,
            "contract_id": SOURCE_ID,
            "config_sha256": SOURCE_CONFIG_SHA256,
            "result_sha256": SOURCE_RESULT_SHA256,
            "observation_count": 9,
        },
        "scientific_boundary": [
            "METADATA_ONLY",
            "NO_EXECUTABLE_OBSERVATION_OPERATORS",
            "NO_FORMAL_NUMERICAL_COMPARISON_READY",
            "NO_MODEL_FAMILY_SELECTED",
            "NO_MODEL_CALIBRATION",
            "NO_ELECTRICAL_DYNAMICS",
            "INPUT_SEMANTICS_UNRESOLVED",
        ],
        "explicit_exclusions": [
            "OPERATOR_EXECUTION",
            "COMPARISON_ENGINE",
            "ACCEPTANCE_WINDOWS",
            "MODEL_PARAMETERS",
            "MODEL_CALIBRATION",
            "PHASE8Q_RUNTIME_COMPOSITION",
            "NEW_EMPIRICAL_RECORDS",
            "FIGURE_DIGITIZATION",
            "DLM_WORK",
            "MUSCLE_FORCE_OR_MECHANICS",
        ],
        "readiness_snapshot": {
            "early_validation_subset": "NO_VALIDATION_SUBSET_READY",
            "model_family": "MODEL_FAMILY_PREMATURE",
            "parameter_readiness": "UNDERDETERMINED_MODEL_ASSUMPTIONS_REQUIRED",
            "input_semantics": "INPUT_SEMANTICS_REQUIRE_SEPARATE_CONTRACT",
        },
        "blocker_taxonomy": BLOCKER_TAXONOMY.copy(),
        "vocabularies": {
            "required_model_quantities": sorted(QUANTITIES),
            "candidate_operators": sorted(OPERATORS),
            "operator_statuses": sorted(OPERATOR_STATUSES),
            "comparabilities": sorted(COMPARABILITIES),
            "comparison_roles": sorted(ROLES),
        },
        "ordering": "SOURCE_PHASE8S_CANONICAL_ORDER",
    }
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "mapping_count": 9,
        "formal_ready_mapping_count": 0,
        "mappings": records,
    }
    config_hash, result_hash = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "contract_id": artifact_id(config_hash, result_hash),
        "config_sha256": config_hash,
        "result_sha256": result_hash,
        "config": config,
        "result": result,
    }


def build_mapping_contract(
    *, source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT
) -> dict:
    """Build metadata using the exact persisted, offline-replayed Phase 8S source."""
    return _build(validated_source(source_artifact))


def validate_mapping_contract(
    contract: dict, *, source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT
) -> dict:
    """Reject even rehashed semantic drift against the pinned source and definitions."""
    source = validated_source(source_artifact)
    try:
        records = contract["result"]["mappings"]
        if (
            len(records) != 9
            or tuple(row["observation_id"] for row in records) != SOURCE_OBSERVATION_IDS
        ):
            raise TTMG1ObservationMappingError("mapping coverage or order mismatch")
        for row, observation in zip(
            records, source["result"]["observations"], strict=True
        ):
            if (
                row["required_model_quantity"] not in QUANTITIES
                or row["candidate_operator_kind"] not in OPERATORS
                or row["operator_status"] not in OPERATOR_STATUSES
                or row["comparability"] not in COMPARABILITIES
                or row["comparison_role"] not in ROLES
                or row["operator_executable"] is not False
                or row["current_model_produces_quantity"] is not False
                or row["formal_comparison_ready"] is not False
                or not row["blockers"]
                or any(code not in BLOCKER_TAXONOMY for code in row["blockers"])
                or row["mapping_id"] != mapping_id(row)
            ):
                raise TTMG1ObservationMappingError(
                    "invalid mapping status, blocker or identity"
                )
            required = row["protocol_requirements"]["required_dimensions"]
            if any(
                key not in observation["protocol"]["dimensions"] for key in required
            ):
                raise TTMG1ObservationMappingError("unknown protocol dimension")
        expected = _build(source)
        if contract != expected:
            raise TTMG1ObservationMappingError(
                "mapping differs from pinned Phase 8T semantics"
            )
        return expected
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, TTMG1ObservationMappingError):
            raise
        raise TTMG1ObservationMappingError("malformed mapping contract") from exc


__all__ = [
    "DEFAULT_SOURCE_ARTIFACT",
    "SOURCE_ID",
    "SOURCE_OBSERVATION_IDS",
    "CONTRACT_SCHEMA_VERSION",
    "ARTIFACT_SCHEMA_VERSION",
    "TTMG1ObservationMappingError",
    "build_mapping_contract",
    "validate_mapping_contract",
]
