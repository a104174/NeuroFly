"""Phase 8Y: metadata-only exploratory G1 domain selection, never tracing."""

from __future__ import annotations

import copy
from pathlib import Path

from neurofly.motor_neuron_muscle_contract import (
    replay_motor_neuron_muscle_target_artifact,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_motor_target_dispatch import target_association_id
from neurofly.ttm_abstract_electrical_input_artifacts import (
    replay_abstract_input_artifact,
)
from neurofly.ttm_g1_electrophysiology_observation_artifacts import (
    replay_ttm_g1_observation_artifact,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_observation_mapping import SOURCE_OBSERVATION_IDS
from neurofly.ttm_g1_observation_mapping_artifacts import (
    replay_ttm_g1_mapping_artifact,
)

CONTRACT_SCHEMA_VERSION = "ttm_g1_proxy_mapping_contract_v1"
ARTIFACT_SCHEMA_VERSION = "ttm_g1_proxy_mapping_artifact_v1"
DOMAIN_SCHEMA_VERSION = "ttm_g1_proxy_domain_v1"
MAPPING_SCHEMA_VERSION = "ttm_g1_proxy_source_mapping_v1"
CLASSIFICATION = "EXPLORATORY_OBSERVATION_DOMAIN_PROXY"
ASSUMPTION = "MODEL_ASSUMPTION"
LATERALITY = "OBSERVATION_PROXY_SIDE_UNRESOLVED"
INSTANCE_SEMANTICS = "SHARED_PROXY_DOMAIN_TYPE_NOT_SHARED_PHYSICAL_INSTANCE"

# These are immutable empirical/causal authorities, not model parameters.
SOURCE_IDENTITIES = {
    "phase8k": (
        "motor_neuron_muscle_target_contract_v1",
        "5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0",
    ),
    "phase8w": (
        "ttm_abstract_electrical_input_artifact_v1",
        "1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa",
    ),
    "phase8s": (
        "ttm_g1_electrophysiology_observation_artifact_v1",
        "5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f",
    ),
    "phase8u": (
        "ttm_g1_observation_mapping_artifact_v1",
        "f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f",
    ),
}
DEFAULT_SOURCE_PATHS = {
    name: DEFAULT_SOURCE_ROOT / schema / identity
    for name, (schema, identity) in SOURCE_IDENTITIES.items()
}
BOUNDARIES = (
    "METADATA_ONLY",
    "MODEL_ASSUMPTION_NOT_ANATOMICAL_DESTINATION",
    "SIDE_AGNOSTIC_DOMAIN_TYPE_ONLY",
    "SHARED_EVIDENCE_BASIS_NOT_BILATERAL_PHYSIOLOGICAL_EQUIVALENCE",
    "PHASE8W_REMAINS_TTM_CLASS_ONLY",
    "PHASE8S_EMPIRICAL_AUTHORITY_PHASE8U_COMPARABILITY_AUTHORITY",
    "NO_FORMAL_COMPARISON_READY",
    "NO_MODEL_FAMILY_SELECTED",
)
EXCLUSIONS = (
    "EXACT_MALECNS_BODY_TO_G1_TRACING",
    "EXACT_PERIPHERAL_ENDPOINT",
    "SHARED_PHYSICAL_G1_INSTANCE",
    "SIDE_RESOLVED_EMPIRICAL_G1_PHYSIOLOGY",
    "BILATERAL_PHYSIOLOGICAL_EQUIVALENCE",
    "IDENTICAL_PHYSIOLOGY_ACROSS_TTM_FIBERS",
    "WHOLE_TTM_REPRESENTATION",
    "EMPIRICAL_VALUES_AS_MODEL_PARAMETERS",
    "SUCCESSFUL_NEUROMUSCULAR_TRANSMISSION",
    "PHYSICAL_INPUT_TRANSFORMATION",
    "RUNTIME_PROXY_EVENTS_OR_INSTANCES",
    "ELECTRICAL_DYNAMICS",
    "OBSERVATION_OPERATORS_OR_COMPARISONS",
    "CALIBRATION_OR_ACCEPTANCE_WINDOWS",
    "CONTRACTION_FORCE_MECHANICS_BEHAVIOR",
    "PRODUCTION_COMPOSITION_OR_DLM_WORK",
)


class TTMG1ProxyError(ValueError):
    """A source or proxy claim differs from the pinned bounded definition."""


def semantic_id(prefix: str, record: dict, identity_key: str) -> str:
    """Hash all semantic fields; the identity itself is excluded."""
    return (
        prefix
        + canonical_sha256(
            {key: value for key, value in record.items() if key != identity_key}
        )[:20]
    )


def proxy_domain_id(record: dict) -> str:
    return semantic_id("ttm-g1-proxy-domain-", record, "proxy_domain_id")


def source_mapping_id(record: dict) -> str:
    return semantic_id("ttm-g1-proxy-map-", record, "mapping_id")


def contract_id(config_hash: str, result_hash: str) -> str:
    return canonical_sha256(
        {
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "config_sha256": config_hash,
            "result_sha256": result_hash,
        }
    )


def validated_sources(source_paths: dict[str, Path] | None = None) -> dict:
    """Full offline child replay before any domain metadata is constructed."""
    paths = DEFAULT_SOURCE_PATHS if source_paths is None else source_paths
    if set(paths) != set(SOURCE_IDENTITIES):
        raise TTMG1ProxyError("require exactly the four pinned source paths")
    try:
        k = replay_motor_neuron_muscle_target_artifact(paths["phase8k"])
        w = replay_abstract_input_artifact(paths["phase8w"])
        s = replay_ttm_g1_observation_artifact(paths["phase8s"])
        u = replay_ttm_g1_mapping_artifact(
            paths["phase8u"], source_artifact=paths["phase8s"]
        )
    except (OSError, ValueError, RuntimeError) as exc:
        raise TTMG1ProxyError("required source failed offline replay") from exc
    sources = {"phase8k": k, "phase8w": w, "phase8s": s, "phase8u": u}
    if any(
        value.artifact_id != SOURCE_IDENTITIES[name][1]
        for name, value in sources.items()
    ):
        raise TTMG1ProxyError("source semantic identity mismatch")
    contracts = {
        name: copy.deepcopy(dict(value.contract)) for name, value in sources.items()
    }
    if (
        tuple(
            row["observation_id"]
            for row in contracts["phase8s"]["result"]["observations"]
        )
        != SOURCE_OBSERVATION_IDS
        or contracts["phase8u"]["result"]["formal_ready_mapping_count"] != 0
    ):
        raise TTMG1ProxyError("observation coverage or readiness changed")
    return contracts


def _evidence_manifest() -> list[dict]:
    return [
        {
            "evidence_id": "king_wyman_1980",
            "authors": "King DG; Wyman RJ",
            "year": 1980,
            "title": (
                "Anatomy of the giant fibre pathway in Drosophila. "
                "I. Three thoracic components of the pathway."
            ),
            "journal": "Journal of Neurocytology 9:753–770",
            "doi": "10.1007/BF01205017",
            "source_location": "Publisher Summary",
            "verification_scope": "PRIMARY_PUBLISHER_SUMMARY",
            "roles": ["GF_MOTOR_PATHWAY_TO_TTM_CLASS_CONTEXT"],
            "limitations": [
                "FULL_TEXT_SUBSCRIPTION_RESTRICTED",
                "NO_G1_DESTINATION_OR_MALECNS_BODY_CROSSWALK",
            ],
        },
        {
            "evidence_id": "koenig_ikeda_2007",
            "authors": "Koenig JH; Ikeda K",
            "year": 2007,
            "title": (
                "Release and Recycling of the Readily Releasable Vesicle "
                "Population in a Synapse Possessing No Reserve Population."
            ),
            "journal": "Journal of Neurophysiology 97:4048–4057",
            "doi": "10.1152/jn.01258.2006",
            "source_location": (
                "Methods; Results anatomy; Figures 1/2 captions; Discussion"
            ),
            "verification_scope": "PUBLISHER_INDEXED_PRIMARY_PASSAGES",
            "roles": [
                "TTM_FIBER_ORGANIZATION",
                "G1_G19_GIANT_MOTOR_AXON_INNERVATION_CONTEXT",
                "G1_EXPERIMENTAL_CHARACTERIZATION",
            ],
            "limitations": [
                "DIRECT_FULL_PAGE_ACCESS_HTTP_403_IN_PHASE8X",
                "INNERVATION_PATTERN_NOT_IDENTICAL_PHYSIOLOGY",
                "NO_WHOLE_TTM_OR_BILATERAL_PHYSIOLOGICAL_EQUIVALENCE",
                "NO_MALECNS_BODY_TO_G1_TRACING",
            ],
        },
    ]


def _build(sources: dict) -> dict:
    source_refs = {}
    for name, source in sources.items():
        ref = {
            "contract_schema_version": source["schema_version"],
            "contract_id": source["contract_id"],
        }
        if name == "phase8k":
            ref["contract_sha256"] = source["contract_sha256"]
        else:
            ref.update(
                config_sha256=source["config_sha256"],
                result_sha256=source["result_sha256"],
                artifact_schema_version=SOURCE_IDENTITIES[name][0],
            )
        source_refs[name] = ref
    config = {
        "schema_version": "ttm_g1_proxy_mapping_config_v1",
        "sources": source_refs,
        "evidence_manifest": _evidence_manifest(),
        "assumption_classification": ASSUMPTION,
        "scientific_boundary": list(BOUNDARIES),
        "exclusions": list(EXCLUSIONS),
        "decision_snapshot": {
            "proxy_readiness": "G1_EXPLORATORY_PROXY_READY",
            "proxy_instance": "SIDE_AGNOSTIC_PROXY_DOMAIN_ONLY",
            "upstream_token": "KEEP_PHASE8W_TOKEN_TTM_CLASS_ONLY",
            "observation_use": (
                "G1_PROXY_CAN_REFERENCE_PHASE8S_OBSERVATIONS_AS_FUTURE_VALIDATION_EVIDENCE"
            ),
        },
        "ordering": "ONE_DOMAIN_THEN_SOURCE_BODY_ID_ASCENDING",
        "resolved_assumption": "TTM_CLASS_TO_G1_PROXY_DOMAIN_SELECTED",
        "remaining_requirements_authority": (
            "UNCHANGED_PHASE8U_MAPPINGS_AND_SEPARATE_PHYSICAL_INPUT_TRANSFORMATION"
        ),
    }
    domain = {
        "schema_version": DOMAIN_SCHEMA_VERSION,
        "domain_kind": "G1_EXPLORATORY_OBSERVATION_DOMAIN",
        "biological_scope": (
            "ONE_EXPERIMENTALLY_CHARACTERIZED_TTM_G_FIBER_OBSERVATION_DOMAIN"
        ),
        "laterality_semantics": LATERALITY,
        "type_instance_semantics": INSTANCE_SEMANTICS,
        "evidence_sharing_semantics": "SHARED_EVIDENCE_BASIS",
        "assumption_classification": ASSUMPTION,
        "mapping_classification": CLASSIFICATION,
        "is_anatomical_destination": False,
        "is_physical_instance": False,
        "bilateral_physiology_asserted": False,
        "evidence_refs": [row["evidence_id"] for row in config["evidence_manifest"]],
        "evidence_basis_sha256": canonical_sha256(config["evidence_manifest"]),
        "permitted_uses": [
            "DEFINE_BOUNDED_FUTURE_G1_PROXY_MODEL_DOMAIN",
            "REFERENCE_PHASE8S_G1_EVIDENCE_WITH_PHASE8U_REQUIREMENTS",
            "PRESERVE_DISTINCT_UPSTREAM_CAUSAL_IDENTITIES",
            "FUTURE_COMPARISON_ONLY_AFTER_MODEL_OPERATOR_PROTOCOL_BLOCKERS_RESOLVED",
        ],
        "prohibited_interpretations": list(EXCLUSIONS),
        "observation_references": {
            "g1_domain_observation_ids": [
                identity
                for index, identity in enumerate(SOURCE_OBSERVATION_IDS)
                if index not in (3, 8)
            ],
            "analysis_context_observation_ids": [SOURCE_OBSERVATION_IDS[3]],
            "distinct_system_boundary_observation_ids": [SOURCE_OBSERVATION_IDS[8]],
            "semantics": "REFERENCES_ONLY_NOT_COMPARABILITY_OVERRIDES",
        },
    }
    domain["proxy_domain_id"] = proxy_domain_id(domain)
    associations = sorted(
        (
            row
            for row in sources["phase8k"]["target_associations"]
            if row["motor_neuron_type"] == "TTMn"
        ),
        key=lambda row: row["motor_neuron_body_id"],
    )
    if tuple((r["motor_neuron_body_id"], r["neural_side"]) for r in associations) != (
        (800146, "R"),
        (804642, "L"),
    ):
        raise TTMG1ProxyError("expected exactly the two pinned TTMn identities")
    mappings = []
    tokens = [
        token
        for fixture in sources["phase8w"]["result"]["fixtures"]
        for token in fixture["tokens"]
    ]
    for association in associations:
        aid = target_association_id(association)
        body = association["motor_neuron_body_id"]
        matched = [token for token in tokens if token["motor_neuron_body_id"] == body]
        if (
            association["target_class"] != "TTM"
            or association["exact_muscle_fiber"] is not None
            or association["exact_target"] is not None
            or not matched
            or any(token["target_association_id"] != aid for token in matched)
        ):
            raise TTMG1ProxyError("input/target association mismatch")
        row = {
            "schema_version": MAPPING_SCHEMA_VERSION,
            "source_motor_neuron_body_id": body,
            "source_motor_neuron_type": association["motor_neuron_type"],
            "source_neural_side": association["neural_side"],
            "source_target_class": association["target_class"],
            "source_ttm_association_id": aid,
            "source_phase8k_contract_id": source_refs["phase8k"]["contract_id"],
            "source_phase8w_contract_id": source_refs["phase8w"]["contract_id"],
            "proxy_domain_id": domain["proxy_domain_id"],
            "mapping_classification": CLASSIFICATION,
            "assumption_classification": ASSUMPTION,
            "laterality_semantics": LATERALITY,
            "causal_identity_semantics": "PRESERVED_NOT_MERGED",
            "unresolved_fields": [
                *association["unresolved_fields"],
                "observation_proxy_side",
                "physical_input_transformation",
                "future_model_quantity_and_observation_operator",
                "protocol_match",
            ],
        }
        row["mapping_id"] = source_mapping_id(row)
        mappings.append(row)
    result = {
        "schema_version": "ttm_g1_proxy_mapping_result_v1",
        "proxy_domain_count": 1,
        "source_mapping_count": 2,
        "proxy_domains": [domain],
        "source_mappings": mappings,
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


def build_proxy_contract(*, source_paths: dict[str, Path] | None = None) -> dict:
    return _build(validated_sources(source_paths))


def validate_proxy_contract(
    contract: dict, *, source_paths: dict[str, Path] | None = None
) -> dict:
    """Reject unknown fields and rehashed semantic drift, not just bad hashes."""
    expected = build_proxy_contract(source_paths=source_paths)
    if not isinstance(contract, dict) or canonical_json_bytes(
        contract
    ) != canonical_json_bytes(expected):
        raise TTMG1ProxyError("proxy metadata differs from replayed pinned definition")
    return expected
