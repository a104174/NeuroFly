"""Evidence-only selection gate: no simulation or runtime dependency."""

import copy
import json
from pathlib import Path

import pytest

from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/science/second_circuit_selection_gate.json"
V1 = ROOT / "docs/science/neurofly_v1_scientific_status.json"
V1_ID = "1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6"
SELECTION_ID = "435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41"


@pytest.fixture
def selection():
    return json.loads(DOCUMENT.read_text())


def test_canonical_identity_and_unchanged_v1(selection):
    record = selection["selection"]
    assert selection["schema"] == record["schema"] == "second_circuit_selection_gate_v1"
    assert selection["selection_id"] == canonical_sha256(record) == SELECTION_ID
    source = json.loads(V1.read_text())
    assert source["status_id"] == canonical_sha256(source["status"]) == V1_ID
    assert record["source_v1_status_id"] == V1_ID
    altered = copy.deepcopy(record)
    altered["selected_candidate_id"] = None
    assert canonical_sha256(altered) != SELECTION_ID


def test_query_provenance_hashes_and_metadata_laterality(selection):
    provenance = selection["selection"]["structural_provenance"]
    assert provenance["dataset"] == "male-cns:v1.0"
    assert provenance["endpoint"] == "https://neuprint.janelia.org"
    assert provenance["structural_count_is_efficacy"] is False
    queries = provenance["queries"]
    assert len(queries) == len({q["key"] for q in queries}) == 6
    for query in queries:
        assert query["query"].startswith("MATCH ")
        assert query["row_count"] == len(query["rows"])
        assert query["response_sha256"] == canonical_sha256(query["rows"])
    nodes = next(q["rows"] for q in queries if q["key"] == "bounded_nodes")
    assert len(nodes) == len({n["body_id"] for n in nodes})
    assert all(n["side"] in {"L", "R"} for n in nodes)
    mdn_query = next(q for q in queries if q["key"] == "lc16_mdn_edges")
    assert mdn_query["rows"] == []  # no invented direct relay
    landing = next(q["rows"] for q in queries if q["key"] == "landing_nodes")
    assert not any(n["type"] == "LPLC3" for n in landing)
    assert sum(n["type"] == "LPLC4" for n in landing) == 97


def test_candidate_classifications_and_scientific_gates(selection):
    record = selection["selection"]
    candidates = record["candidates"]
    assert len(candidates) == len({c["id"] for c in candidates}) == 3
    classifications = {
        "READY_FOR_BOUNDED_VALIDATION_DESIGN",
        "PROMISING_BUT_EVIDENCE_REVIEW_REQUIRED",
        "PROMISING_BUT_INPUT_MODEL_BLOCKED",
        "PROMISING_BUT_OUTPUT_MODEL_BLOCKED",
        "TOO_MANY_UNCONSTRAINED_ASSUMPTIONS",
        "STRUCTURAL_SUPPORT_INSUFFICIENT",
        "FUNCTIONAL_EVIDENCE_INSUFFICIENT",
        "OUT_OF_SCOPE_FOR_NEXT_MILESTONE",
    }
    evidence = {e["id"]: e for e in record["primary_evidence"]}
    assert len(evidence) == len(record["primary_evidence"])
    query_ids = {q["key"] for q in record["structural_provenance"]["queries"]}
    for candidate in candidates:
        assert candidate["classification"] in classifications
        assert set(candidate["gates"]) == {f"G{i}" for i in range(1, 9)}
        assert all(
            g["status"] in {"PASS", "FAIL", "UNKNOWN"} and g["reason"]
            for g in candidate["gates"].values()
        )
        assert set(candidate["structural_query_ids"]) <= query_ids
        assert set(candidate["functional_evidence"]) <= evidence.keys()
        assert all(
            evidence[e]["kind"].startswith("PRIMARY_")
            for e in candidate["functional_evidence"]
        )
        assert candidate["author_contact_dependency"] is False
        assert all(
            a["classification"]
            in {
                "EVIDENCE_BACKED",
                "EXPLORATORY_BOUNDED_ASSUMPTION",
                "HIGH_RISK_UNCONSTRAINED_ASSUMPTION",
            }
            for a in candidate["assumptions"]
        )
    ready = [
        c
        for c in candidates
        if c["classification"] == "READY_FOR_BOUNDED_VALIDATION_DESIGN"
    ]
    assert len(ready) == 1
    assert record["selected_candidate_id"] == ready[0]["id"]
    assert all(g["status"] == "PASS" for g in ready[0]["gates"].values())
    assert record["decision"] == "SECOND_CIRCUIT_SELECTED_FOR_BOUNDED_VALIDATION"


def test_selected_contract_is_actual_bounded_structural_motif(selection):
    record = selection["selection"]
    contract = record["selected_contract"]
    selected = next(
        c for c in record["candidates"] if c["id"] == contract["candidate_id"]
    )
    assert contract["schema"] == "second_circuit_candidate_contract_v1"
    assert contract["candidate_id"] == record["selected_candidate_id"]
    assert (
        contract["capability"]
        == record["selected_capability"]
        == "VISUAL_COURSE_CONTROL"
    )
    assert (
        selected["body_compatibility"]
        == "BODY_OUTPUT_NOT_REQUIRED_FOR_FIRST_VALIDATION"
    )
    identities = contract["source_identities"] + contract["target_identities"]
    by_id = {n["body_id"]: n for n in identities}
    assert len(by_id) == 8
    assert {n["type"] for n in contract["source_identities"]} == {"HSN", "HSE", "HSS"}
    assert {(n["body_id"], n["side"]) for n in contract["target_identities"]} == {
        (11215, "R"),
        (12069, "L"),
    }
    edges = contract["structural_edges"]
    assert edges == selected["selected_edges"]
    assert len(edges) == 6
    induced = next(
        q["rows"]
        for q in record["structural_provenance"]["queries"]
        if q["key"] == "hs_induced_edges"
    )
    assert len(induced) == selected["full_induced_edge_count"] == 13
    assert len(contract["full_induced_edges_not_selected"]) == 7
    for edge in edges:
        assert edge in induced
        assert by_id[edge["source_id"]]["side"] == by_id[edge["target_id"]]["side"]
        assert edge["target_type"] == "DNp15"
        assert type(edge["structural_count"]) is int and edge["structural_count"] > 0
    assert "NO_STRUCTURAL_COUNT_AS_EFFICACY" in contract["exclusions"]
    assert "NO_MOTOR_ACTUATOR_YAW_OR_BODY_MAPPING" in contract["exclusions"]


def test_public_evidence_no_output_targeting_no_runtime_dependency(selection):
    record = selection["selection"]
    assert not any(record["prohibitions"].values())
    design = record["first_validation_design"]
    assert "NO_MOTION_CONTROL" in design["conditions"]
    assert "Accept zero, weak, asymmetric" in design["acceptance"]
    assert "before any new neural execution" in design["pre_execution_freeze"]
    assert "No body output required" in design["output"]
    for evidence in record["primary_evidence"]:
        assert evidence["url"].startswith("https://")
        assert evidence["supports"] and evidence["limitations"]
    text = DOCUMENT.read_text()
    for forbidden in (
        "data/raw/",
        "data/derived/",
        "/home/",
        '"target_spikes"',
        '"target_movement"',
        '"desired_displacement"',
    ):
        assert forbidden not in text
    for path in (ROOT / "src").rglob("*.py"):
        source = path.read_text()
        assert DOCUMENT.name not in source
        assert "second_circuit_selection_gate_v1" not in source
