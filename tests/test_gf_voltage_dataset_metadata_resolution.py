"""Isolated metadata contract tests: no trace analysis or model execution."""

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/science/gf_voltage_dataset_metadata_resolution.json"
AUDIT = ROOT / "docs/science/gf_voltage_dataset_compatibility_audit.json"
SOURCE_ID = "219622b71f1fd79caabe83665ddc859699875177883e7810c1b2bea4676e627d"
CANDIDATE_ID = "dombrovski_gf_zenodo_14983850"


@pytest.fixture
def document():
    return json.loads(DOCUMENT.read_text())


def test_canonical_resolution_and_immutable_authority(document):
    resolution = document["resolution"]
    audit = json.loads(AUDIT.read_text())
    assert document["schema"] == resolution["schema"]
    assert document["resolution_id"] == canonical_sha256(resolution)
    assert audit["audit_id"] == canonical_sha256(audit["audit"]) == SOURCE_ID
    assert resolution["source_audit_id"] == SOURCE_ID
    assert resolution["candidate_id"] == CANDIDATE_ID
    changed = copy.deepcopy(resolution)
    changed["unresolved_metadata"]["stored_voltage_units"] = "mV"
    assert canonical_sha256(changed) != document["resolution_id"]


def test_gates_classification_and_no_silent_calibration(document):
    resolution = document["resolution"]
    audit = json.loads(AUDIT.read_text())["audit"]
    candidate = next(r for r in audit["candidates"] if r["id"] == CANDIDATE_ID)
    gates = resolution["target_voltage_gates"]
    assert set(gates) == set(candidate["relative_voltage_gates"])
    assert all(g["status"] in {"PASS", "FAIL", "UNKNOWN"} for g in gates.values())
    assert all(g["reason"] for g in gates.values())
    assert resolution["gate_changes_from_phase21"] == [
        key
        for key in gates
        if gates[key]["status"] != candidate["relative_voltage_gates"][key]["status"]
    ]
    assert resolution["previous_classification"] == candidate["compatibility"]
    assert resolution["new_classification"] == "METADATA_INSUFFICIENT"
    assert resolution["decision"] == "TARGET_GF_METADATA_REMAINS_INSUFFICIENT"
    assert gates["measurement_units"]["status"] == "UNKNOWN"
    assert gates["filtering_metadata"]["status"] == "UNKNOWN"
    assert resolution["source_state_operator_available"] is False
    assert resolution["calibration_permitted"] is False
    assert not any(resolution["prohibitions"].values())
    text = DOCUMENT.read_text()
    assert "/home/" not in text
    for forbidden in (
        "voltage_samples",
        "waveform_samples",
        "raw_trace_values",
        "fit_scale",
    ):
        assert f'"{forbidden}"' not in text


def test_source_integrity_and_storage_safety(document):
    audit = json.loads(AUDIT.read_text())["audit"]
    sources = {r["filename"]: r for r in audit["local_acquisitions"]}
    for record in document["resolution"]["source_files"]:
        source = sources[record["filename"]]
        assert record["sha256"] == source["sha256"]
        assert record["byte_size"] == source["byte_size"]
        assert record["local_path"] == source["local_path"]
        path = Path(record["local_path"])
        assert not path.is_absolute()
        assert (
            subprocess.run(
                ["git", "check-ignore", "--quiet", str(path)], cwd=ROOT, check=False
            ).returncode
            == 0
        )
        assert not subprocess.check_output(
            ["git", "ls-files", "--", str(path)], cwd=ROOT, text=True
        ).strip()
        # Acquisition is not needed for metadata-only tests in a fresh checkout.
        if (ROOT / path).exists():
            data = (ROOT / path).read_bytes()
            assert len(data) == record["byte_size"]
            assert hashlib.sha256(data).hexdigest() == record["sha256"]
        assert record["embedded_metadata_fields"] == []
        assert record["time_vector_present"] is False
        assert record["source_modified"] is False


def test_trial_dictionary_and_representation_separation(document):
    resolution = document["resolution"]
    dictionary = resolution["individual_file_dictionary"]
    assert len(dictionary) == len({r["filename"] for r in dictionary}) == 44
    animals = {r["animal_id"] for r in dictionary}
    assert len(animals) == 22
    for animal in animals:
        assert {r["trial_id"] for r in dictionary if r["animal_id"] == animal} == {
            "trial01",
            "trial02",
        }
    assert all(
        r["stimulus_columns_r_over_v_ms"] == [10, 20, 40, 80] for r in dictionary
    )
    assert {r["group_id"] for r in dictionary} == {
        r["id"] for r in resolution["groups"]
    }
    combined = resolution["source_files"][1]
    assert combined["representation"] == "UNDOCUMENTED_COMBINED_ARRAY"
    assert combined["documented_axes"] == []
    assert combined["processing_status"] == "UNKNOWN"
    assert combined["filename"] not in {r["filename"] for r in dictionary}
    sampling = resolution["resolved_metadata"]["sampling"]
    assert (
        sampling["samples_per_condition"] / sampling["rate_hz"]
        == sampling["duration_s"]
    )
