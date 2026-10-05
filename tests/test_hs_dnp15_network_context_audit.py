"""Evidence-only gate; no candidate recurrent execution or runtime dependency."""

import copy
import json
from pathlib import Path

import pytest

from neurofly.hs_dnp15_neural_validation import (
    PREREGISTRATION_ID,
    SELECTION_ID,
    V1_ID,
    load_preregistration,
    load_structural_authority,
    route_contributions,
)
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/science/hs_dnp15_network_context_audit.json"
AUDIT_ID = "04116360164262de5a2572f33e12cc90351869567c3202811807be576f1d03be"
ARTIFACT_ID = "2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113"
CANDIDATE_KEYS = {
    (10015, 10016),
    (10016, 10015),
    (10016, 10023),
    (10034, 10181),
    (10034, 10419),
    (10419, 10034),
    (12069, 10419),
}


@pytest.fixture
def audit():
    document = json.loads(DOCUMENT.read_text())
    assert document["schema"] == "hs_dnp15_network_context_audit_v1"
    assert document["audit_id"] == AUDIT_ID
    return document["audit"]


def test_identity_and_frozen_authorities(audit):
    assert canonical_sha256(audit) == AUDIT_ID
    assert audit["schema"] == "hs_dnp15_network_context_audit_v1"
    authorities = audit["authorities"]
    assert authorities["v1_status_id"] == V1_ID
    assert authorities["phase24_selection_id"] == SELECTION_ID
    assert authorities["phase25_preregistration_id"] == PREREGISTRATION_ID
    assert authorities["phase25_artifact_id"] == ARTIFACT_ID
    preregistration = load_preregistration()
    authority = load_structural_authority()
    assert audit["phase25_active_routes"] == preregistration["selected_routes"]
    assert audit["phase25_active_routes"] == authority["structural_edges"]


def test_all_thirteen_edges_and_metadata_laterality(audit):
    provenance = audit["structural_provenance"]
    assert provenance["dataset"] == "male-cns:v1.0"
    assert provenance["laterality_field"] == "somaSide"
    query = provenance["query"]
    assert query["row_count"] == len(query["rows"]) == 13
    assert canonical_sha256(query["rows"]) == query["response_sha256"]
    selection = json.loads((ROOT / authorities_path(audit)).read_text())["selection"]
    original = next(
        q
        for q in selection["structural_provenance"]["queries"]
        if q["key"] == "hs_induced_edges"
    )
    assert query == original
    identities = provenance["identities"]
    p = load_preregistration()
    assert identities == p["source_identities"] + p["target_identities"]
    nodes = {n["body_id"]: n for n in identities}
    assert len(nodes) == 8
    original_edges = {(e["source_id"], e["target_id"]): e for e in query["rows"]}
    topology = audit["induced_topology"]
    assert len(topology) == 13
    assert len({(e["source_id"], e["target_id"]) for e in topology}) == 13
    for edge in topology:
        original = original_edges[edge["source_id"], edge["target_id"]]
        assert all(edge[key] == value for key, value in original.items())
        for prefix in ("source", "target"):
            node = nodes[edge[f"{prefix}_id"]]
            assert edge[f"{prefix}_type"] == node["type"]
            assert edge[f"{prefix}_side"] == node["side"]
        assert edge["structural_verification"] == "PASS"
        assert edge["direction"] == "SOURCE_TO_TARGET"


def authorities_path(audit):
    return audit["authorities"]["structural_authority_path"]


def test_candidate_roles_evidence_and_exclusion(audit):
    candidates = audit["candidate_edges"]
    assert len(candidates) == 7
    assert {(e["source_id"], e["target_id"]) for e in candidates} == CANDIDATE_KEYS
    evidence = {e["id"] for e in audit["primary_evidence"]}
    evidence.add(audit["neurotransmitter_provenance"]["id"])
    assert len(evidence) == len(audit["primary_evidence"]) + 1
    role_counts = {}
    for edge in candidates:
        role = edge["structural_role"]
        role_counts[role] = role_counts.get(role, 0) + 1
        assert edge["sign_status"] in {
            "DIRECTLY_ESTABLISHED",
            "NEUROTRANSMITTER_INFERRED_WITH_SUPPORT",
            "FUNCTIONALLY_CONSTRAINED",
            "UNKNOWN",
        }
        assert edge["timing_status"] in {
            "MEASURED",
            "BOUNDED_BY_EVIDENCE",
            "MODEL_ASSUMPTION_REQUIRED",
            "UNKNOWN",
        }
        assert edge["magnitude_status"] == "NOT_IDENTIFIABLE"
        assert set(edge["sign_evidence"]) <= evidence
        assert set(edge["electrical_context"]) <= evidence
        assert edge["implementation_eligible"] is False
        assert edge["implemented_sign"] is None
        assert edge["functional_role_evidence"] == "NOT_LOCATED_FOR_THIS_CHEMICAL_EDGE"
        assert edge["limitation"]
    assert role_counts == {
        "SOURCE_SOURCE_RECURRENCE": 4,
        "SOURCE_SOURCE_FEEDFORWARD": 2,
        "TARGET_TO_SOURCE_FEEDBACK": 1,
    }


def test_nt_snapshot_is_not_physiology_or_efficacy(audit):
    snapshot = audit["neurotransmitter_provenance"]
    assert snapshot["response_sha256"] == canonical_sha256(snapshot["rows"])
    assert snapshot["row_count"] == len(snapshot["rows"]) == 8
    nodes = {n["body_id"]: n for n in audit["structural_provenance"]["identities"]}
    assert {n["body_id"] for n in snapshot["rows"]} == set(nodes)
    for row in snapshot["rows"]:
        assert row["side"] == nodes[row["body_id"]]["side"]
        assert row["type"] == nodes[row["body_id"]]["type"]
        assert row["predicted_nt"] == row["consensus_nt"] == "acetylcholine"
        assert 0 <= row["prediction_confidence"] <= 1
    assert snapshot["prediction_is_direct_physiology"] is False
    assert snapshot["confidence_is_synaptic_efficacy"] is False
    assert snapshot["target_receptor_measurements_located"] is False
    # Inferred support is recorded honestly, without assigning an active +1.
    assert all(
        e["sign_status"] == "NEUROTRANSMITTER_INFERRED_WITH_SUPPORT"
        and e["putative_sign"] == "EXCITATORY"
        and e["implemented_sign"] is None
        for e in audit["candidate_edges"]
    )


def test_no_stage_b_feedback_electrical_or_mirror_completion(audit):
    gate = audit["stage_a"]
    assert gate["decision"] == "RECURRENT_SIGN_OR_DYNAMICS_NOT_IDENTIFIABLE"
    assert gate["stage_b_permitted"] is gate["stage_b_executed"] is False
    assert gate["neural_candidate_execution_count"] == 0
    assert gate["parameters_selected"] is gate["output_targeting"] is False
    assert audit["active_extended_topology"] == []
    assert audit["extended_preregistration_id"] is None
    assert audit["extended_artifact_id"] is None
    assert (
        audit["phase26_decision"]
        == "FEEDFORWARD_MOTIF_REMAINS_CURRENT_VALIDATED_BOUNDARY"
    )
    excluded = audit["excluded_verified_topology"]
    assert {(e["source_id"], e["target_id"]) for e in excluded} == CANDIDATE_KEYS
    assert audit["feedback_gate"]["edge"] == [12069, 10419]
    assert audit["feedback_gate"]["implementation_eligible"] is False
    electrical = audit["electrical_context"]
    assert electrical["implemented"] is False
    assert electrical["chemical_edges_represent_gap_junctions"] is False
    assert (
        electrical["indispensable_for_any_partial_chemical_model"] == "NOT_ESTABLISHED"
    )
    assert audit["structural_provenance"]["missing_mirror_edges_synthesized"] is False


def test_counts_only_provenance_and_frozen_feedforward_count_mutation(audit):
    assert audit["structural_provenance"]["structural_count_is_efficacy"] is False
    assert audit["structural_provenance"]["structural_count_is_sign"] is False
    p = load_preregistration()
    sources = {s["body_id"]: 0.125 for s in p["source_identities"]}
    original = route_contributions(
        sources,
        p["selected_routes"],
        p["target_identities"],
        p["transfer"]["coefficient"],
    )
    changed = copy.deepcopy(p["selected_routes"])
    for edge in changed:
        edge["structural_count"] *= 1001
    assert original == route_contributions(
        sources, changed, p["target_identities"], p["transfer"]["coefficient"]
    )
    # Evidence identity changes with contact provenance; no numerical recurrence exists.
    altered = copy.deepcopy(audit)
    for edge in altered["induced_topology"]:
        edge["structural_count"] *= 1001
    assert canonical_sha256(altered) != AUDIT_ID
    assert altered["active_extended_topology"] == []


@pytest.mark.parametrize(
    "mutation",
    ["edge", "sign", "evidence", "authority", "gate", "feedback", "electrical"],
)
def test_context_tampering_changes_canonical_identity(audit, mutation):
    altered = copy.deepcopy(audit)
    if mutation == "edge":
        altered["candidate_edges"][0]["implementation_eligible"] = True
    elif mutation == "sign":
        altered["candidate_edges"][0]["implemented_sign"] = 1
    elif mutation == "evidence":
        altered["candidate_edges"][0]["sign_status"] = "DIRECTLY_ESTABLISHED"
    elif mutation == "authority":
        altered["authorities"]["phase25_artifact_id"] = "0" * 64
    elif mutation == "gate":
        altered["stage_a"]["decision"] = "EXTENDED_CHEMICAL_MOTIF_MODEL_IDENTIFIABLE"
    elif mutation == "feedback":
        altered["feedback_gate"]["implementation_eligible"] = True
    else:
        altered["electrical_context"]["implemented"] = True
    assert canonical_sha256(altered) != AUDIT_ID


def test_no_raw_paths_or_scientific_model_dependency(audit):
    def visit(value):
        if isinstance(value, str):
            assert not value.startswith(("/", "data/", "file://"))
        elif isinstance(value, dict):
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(audit)
    for source in (ROOT / "src/neurofly").rglob("*.py"):
        # Phase27 explicitly validates/displays the frozen interpretation in
        # playback. Only this read-only product adapter may consume the audit;
        # no scientific model/operator gains a runtime dependency on it.
        if source == ROOT / "src/neurofly/scenario_playback_api.py":
            continue
        assert DOCUMENT.name not in source.read_text()
