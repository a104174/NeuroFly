"""Metadata-only validation; no acquisition, fitting or simulation dependency."""

import copy
import json
import subprocess
from pathlib import Path

import pytest

from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/science/gf_voltage_dataset_compatibility_audit.json"
CLASSIFICATIONS = {
    "SUFFICIENT_FOR_CALIBRATION",
    "SUFFICIENT_FOR_PRE_REGISTERED_CALIBRATION_DESIGN_ONLY",
    "SUFFICIENT_FOR_OPERATOR_DESIGN_ONLY",
    "QUALITATIVE_ONLY",
    "INCOMPATIBLE",
    "NOT_ACCESSIBLE",
    "METADATA_INSUFFICIENT",
}


@pytest.fixture
def audit_document():
    return json.loads(DOCUMENT.read_text())


def test_identity_authority_and_tamper(audit_document):
    audit = audit_document["audit"]
    authority = json.loads(
        (
            ROOT / "docs/science/observation_operator_assay_compatibility.json"
        ).read_text()
    )
    assert authority["contract_id"] == (
        "ae50e1faad223cdde63125a6216ce0993523f9933025fe1f04e9265450dec824"
    )
    assert canonical_sha256(authority["contract"]) == authority["contract_id"]
    assert audit["phase20_contract_id"] == authority["contract_id"]
    assert (
        audit["required_gates"]
        == authority["contract"]["comparison_policy"]["required_gates"]
    )
    assert audit_document["schema"] == audit["schema"]
    assert canonical_sha256(audit) == audit_document["audit_id"]
    changed = copy.deepcopy(audit)
    changed["candidates"][0]["compatibility"] = "SUFFICIENT_FOR_CALIBRATION"
    assert canonical_sha256(changed) != audit_document["audit_id"]


def test_candidates_metadata_and_gate_integrity(audit_document):
    audit = audit_document["audit"]
    ids = [r["id"] for r in audit["candidates"]]
    assert len(ids) == len(set(ids))
    assert audit["best_available_candidate"] in ids
    for record in audit["candidates"]:
        assert record["compatibility"] in CLASSIFICATIONS
        for key in (
            "publication",
            "repository",
            "persistent_identifier",
            "access_url",
            "access_date",
            "license_reuse",
            "neuron_identity",
            "assay",
            "stimulus",
            "source_manipulation",
            "time_reference",
            "sampling_rate",
            "voltage_units",
            "baseline_semantics",
            "filtering",
            "trial_structure",
            "preparation",
            "sex",
            "raw_data_availability",
            "metadata_completeness",
            "missing_requirements",
            "acquisition_feasibility",
        ):
            assert record[key]
        assert record["access_url"].startswith("https://")
        assert set(record["contract_gates"]) == set(audit["required_gates"])
        for gates in (record["contract_gates"], record["relative_voltage_gates"]):
            assert all(
                g["status"] in {"PASS", "FAIL", "UNKNOWN"} for g in gates.values()
            )
            assert all(g["reason"] for g in gates.values())
        if record["compatibility"] == "SUFFICIENT_FOR_CALIBRATION":
            assert all(g["status"] == "PASS" for g in record["contract_gates"].values())
            assert all(
                g["status"] == "PASS" for g in record["relative_voltage_gates"].values()
            )
    assert audit["calibration_ready_count"] == sum(
        r["compatibility"] == "SUFFICIENT_FOR_CALIBRATION" for r in audit["candidates"]
    )


def test_no_fitting_or_silent_operator_calibration(audit_document):
    audit = audit_document["audit"]
    assert not any(audit["prohibitions"].values())
    assert audit["calibration_ready_count"] == 0
    assert audit["decisions"] == {
        "data_availability": "OPERATOR_DESIGN_DATA_ONLY",
        "calibration_readiness": "DATA_AVAILABLE_BUT_METADATA_INSUFFICIENT",
    }
    assert all(
        r["status"]
        in {
            "SUPPORTED_BY_COMPATIBLE_DATA",
            "SUPPORTED_FOR_OPERATOR_DESIGN_ONLY",
            "QUALITATIVELY_SUPPORTED",
            "DATA_NOT_LOCATED",
            "INCOMPATIBLE_DATA",
            "UNKNOWN",
        }
        for r in audit["identifiability_chain"]
    )


def test_acquired_bytes_are_metadata_only_and_git_ignored(audit_document):
    for record in audit_document["audit"]["local_acquisitions"]:
        path = Path(record["local_path"])
        assert not path.is_absolute()
        assert len(record["sha256"]) == 64
        assert record["byte_size"] > 0
        assert record["license"] == "CC-BY-4.0"
        assert (
            subprocess.run(
                ["git", "check-ignore", "--quiet", str(path)], cwd=ROOT, check=False
            ).returncode
            == 0
        )
        assert not subprocess.check_output(
            ["git", "ls-files", "--", str(path)], cwd=ROOT, text=True
        ).strip()
    assert "/home/" not in DOCUMENT.read_text()
