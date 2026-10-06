"""Deterministic Phase32 heuristic evidence; no UI/runtime audit dependency."""

import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

import pytest

from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/science/frontend_scientific_readability_ux_audit.json"
AUDIT_ID = "3922ccf48edfcf10fc68b521573805f12a91a46909bdd044d8f704a5ee5c5157"
SCHEMA = "frontend_scientific_readability_audit_v1"
SCENARIOS = {
    "BASELINE_CONTROL",
    "LOOMING_CIRCUIT_VALIDATION",
    "LOOMING_WORLD_EXPERIMENT",
    "HORIZONTAL_MOTION_NEURAL_VALIDATION",
    "EXPLORATORY_COURSE_CONTROL",
}
ANSWERS = {"CLEAR", "PARTIALLY_CLEAR", "UNCLEAR", "MISLEADING"}
SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
CATEGORIES = {
    "SCIENTIFIC_COPY",
    "SCIENTIFIC_SEMANTICS",
    "INFORMATION_HIERARCHY",
    "VISUALIZATION",
    "TELEMETRY",
    "PLAYBACK",
    "PROVENANCE",
    "RESPONSIVE",
    "ACCESSIBILITY",
    "ERROR_STATE",
    "PERFORMANCE",
    "VISUAL_POLISH",
    "ASSET_LIMITATION",
}
LAYERS = {
    "FRONTEND_ONLY",
    "PRESENTATION_ADAPTER_ONLY",
    "BACKEND_TRANSPORT_CHANGE_REQUIRED",
    "SCIENTIFIC_MODEL_CHANGE_REQUIRED",
}


@pytest.fixture(scope="module")
def audit():
    document = json.loads(DOCUMENT.read_text())
    assert document["schema"] == SCHEMA
    assert document["audit_id"] == AUDIT_ID
    return document["audit"]


def test_canonical_identity(audit):
    assert audit["schema"] == SCHEMA
    assert canonical_sha256(audit) == AUDIT_ID
    # Object insertion order is not a scientific/evidence identity dependency.
    reordered = dict(reversed(list(audit.items())))
    assert canonical_sha256(reordered) == AUDIT_ID


def test_exact_scenarios_questions_matrix_and_viewports(audit):
    evaluations = audit["scenario_evaluations"]
    assert len(evaluations) == 5
    assert {e["scenario_id"] for e in evaluations} == SCENARIOS
    assert len(audit["methodology"]["core_questions"]) == 6
    for evaluation in evaluations:
        assert set(evaluation["newcomer_answers"]) == set(
            audit["methodology"]["question_keys"]
        )
        assert set(evaluation["newcomer_answers"].values()) <= ANSWERS
        assert evaluation["desktop_reviewed"] is True
        assert evaluation["viewport_dominance"] in {
            "DOMINANT",
            "BALANCED",
            "UNDERSIZED",
            "OBSCURED_BY_UI",
        }
        assert set(evaluation["matrix"].values()) <= ANSWERS | {"NOT_AUDITED"}
    assert len(audit["cross_scenario_matrix"]) == 5
    assert {e["scenario_id"] for e in audit["cross_scenario_matrix"]} == SCENARIOS
    reviewed = {e["scenario_id"] for e in evaluations if e["mobile_reviewed"]}
    assert {
        "HORIZONTAL_MOTION_NEURAL_VALIDATION",
        "EXPLORATORY_COURSE_CONTROL",
        "LOOMING_WORLD_EXPERIMENT",
    } <= reviewed
    assert {(v["width_px"], v["height_px"]) for v in audit["viewports"]} == {
        (1440, 1000),
        (390, 844),
    }


def test_findings_taxonomy_remedies_and_severity(audit):
    findings = audit["findings"]
    assert len(findings) == len({f["id"] for f in findings}) == 17
    counts = Counter(f["severity"] for f in findings)
    assert {s: counts[s] for s in SEVERITIES} == audit["severity_counts"]
    for finding in findings:
        assert finding["severity"] in SEVERITIES
        assert finding["category"] in CATEGORIES
        assert set(finding["scenarios"]) <= SCENARIOS
        assert finding["required_change_layer"] in LAYERS
        for field in (
            "current_behavior",
            "why_it_matters",
            "scientific_risk",
            "ux_impact",
            "phase33_remedy",
        ):
            assert finding[field]
        assert finding["scientific_model_change_required"] == (
            finding["required_change_layer"] == "SCIENTIFIC_MODEL_CHANGE_REQUIRED"
        )
    assert {f["id"] for f in findings if f["category"] == "ASSET_LIMITATION"}


def test_screenshot_references_portable_and_optional(audit):
    screenshots = audit["screenshots"]
    names = {s["filename"] for s in screenshots}
    assert len(names) == len(screenshots) == 14
    assert {
        "library-desktop.png",
        "baseline-desktop.png",
        "looming-circuit-desktop-final.png",
        "looming-world-desktop.png",
        "horizontal-motion-desktop.png",
        "course-control-desktop.png",
        "course-provenance-desktop.png",
        "horizontal-motion-mobile.png",
        "course-control-mobile.png",
        "scientific-playback-unavailable.png",
    } <= names
    for screenshot in screenshots:
        name = screenshot["filename"]
        assert Path(name).name == name and not Path(name).is_absolute()
        assert screenshot["scientific_authority"] is False
        assert screenshot["storage"] == "OUTSIDE_GIT_OPTIONAL_LOCAL_EVIDENCE"
        assert len(screenshot["sha256"]) == 64 and screenshot["bytes"] > 0
    for finding in audit["findings"]:
        assert set(finding["screenshot_evidence"]) <= names
    # Local captures are deliberately not required to exist in a fresh checkout.
    assert not list((ROOT / "docs/science").glob("*phase32*.png"))


def test_authorities_and_pinned_product_source(audit):
    source = audit["source"]
    assert source["commit"] == "c5ea8c35b757b7de5b70c78e86a6b4fba6b9cb40"
    assert source["initial_worktree_clean"] and source["origin_main_equal"]
    assert source["phase31_committed"]
    for authority in source["authorities"]:
        path = "docs/science/" + authority["document"]
        raw = subprocess.check_output(
            ["git", "show", f"{source['commit']}:{path}"], cwd=ROOT
        )
        key = authority["inner_key"]
        if key == "DOCUMENT_BYTES":
            digest = hashlib.sha256(raw).hexdigest()
        else:
            value = json.loads(raw)
            digest = canonical_sha256(value[key] if key else value)
        assert digest == authority["canonical_id"]
    for item in source["frontend_backend_source_files"]:
        assert not Path(item["path"]).is_absolute()
        raw = subprocess.check_output(
            ["git", "show", f"{source['commit']}:{item['path']}"], cwd=ROOT
        )
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
    assert {r["phase"] for r in source["historical_replays"]} == {
        "7O",
        "8C",
        "13B",
        "16",
        "18",
        "25",
        "28",
        "30",
    }
    assert {r["scenario"] for r in source["playback_identities"]} == SCENARIOS
    assert all(len(r["transport_sha256"]) == 64 for r in source["playback_identities"])


def test_heuristic_not_user_study_or_fake_score(audit):
    methodology = audit["methodology"]
    assert methodology["kind"] == "EXPERT_HEURISTIC_AUDIT"
    assert methodology["user_study"] is False
    assert methodology["wcag_conformance_evaluated"] is False

    def visit(value):
        if isinstance(value, dict):
            assert (
                not {"ux_score", "score", "usability_percent", "rating"} & value.keys()
            )
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, str):
            assert not value.startswith(("/home/", "/tmp/", "file://"))

    visit(audit)
    assert set(audit["claim_audit"]["forbidden_positive_claims_located"]) == set()


def test_frozen_stage_a_and_no_micro_fixes(audit):
    assert audit["stage_a"]["completed"] and audit["stage_a"]["findings_frozen"]
    assert audit["stage_a"]["freeze_identity_location"] == "OUTER_AUDIT_ID"
    assert audit["stage_b"]["status"] == "NOT_RUN"
    assert audit["severity_counts"]["CRITICAL"] == audit["severity_counts"]["HIGH"] == 0
    for field in ("fixes", "frontend_changes", "scientific_changes", "payload_changes"):
        assert audit["stage_b"][field] == []
    assert audit["decision"] == "FRONTEND_READY_FOR_VISUAL_SYSTEM_REDESIGN"


def test_redesign_brief_covers_all_screens_and_science(audit):
    phase33 = audit["phase33"]
    ids = {r["id"] for r in phase33["requirements"]}
    assert len(ids) == 18
    assert {r["priority"] for r in phase33["requirements"]} == {
        "MUST_PRESERVE_SCIENCE",
        "MUST_IMPROVE",
        "SHOULD_IMPROVE",
        "OPTIONAL_POLISH",
    }
    assert {b["screen"] for b in phase33["screen_briefs"]} == SCENARIOS | {
        "SCENARIO_LIBRARY",
        "PROVENANCE_EXPANDED",
        "SCIENTIFIC_PLAYBACK_UNAVAILABLE",
        "MOBILE_COMPLEX_SCENARIOS",
    }
    for brief in phase33["screen_briefs"]:
        assert set(brief["requirements"]) <= ids and brief["brief"]
    assert phase33["scientific_invariants"]
    assert phase33["science_limitations_not_ui_fixes"]
    assert {t["classification"] for t in audit["telemetry_classification"]} == {
        "ESSENTIAL",
        "USEFUL_SECONDARY",
        "PROVENANCE_ONLY",
        "REDUNDANT",
        "CONFUSING",
    }


@pytest.mark.parametrize("field", ["source", "findings", "stage_b", "decision"])
def test_material_evidence_mutations_change_identity(audit, field):
    changed = copy.deepcopy(audit)
    changed[field] = "tampered"
    assert canonical_sha256(changed) != AUDIT_ID
