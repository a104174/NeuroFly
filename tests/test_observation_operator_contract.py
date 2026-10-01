"""Isolated science-document validation; no production observation model."""

import copy
import json
from pathlib import Path

import pytest

from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

CONTRACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs/science/observation_operator_assay_compatibility.json"
)
OPERATOR_STATUSES = {
    "DIRECTLY_OBSERVABLE",
    "OBSERVABLE_WITH_KNOWN_TRANSFORM",
    "OBSERVABLE_WITH_UNKNOWN_TRANSFORM",
    "QUALITATIVELY_COMPARABLE_ONLY",
    "NO_VALID_OBSERVATION_OPERATOR_CURRENTLY_DEFINED",
    "NOT_A_BIOLOGICAL_OBSERVABLE",
}
CALIBRATION_STATUSES = {
    "CALIBRATED",
    "PARTIALLY_CONSTRAINED",
    "UNCALIBRATED",
    "NOT_CALIBRATABLE_FROM_CURRENT_ASSAY",
    "NOT_APPLICABLE",
}


@pytest.fixture
def document():
    return json.loads(CONTRACT_PATH.read_text())


def test_canonical_identity_and_semantic_mutation(document):
    contract = document["contract"]
    assert document["schema"] == contract["schema"]
    assert document["contract_id"] == canonical_sha256(contract)
    assert canonical_sha256(json.loads(json.dumps(contract))) == document["contract_id"]
    changed = copy.deepcopy(contract)
    changed["comparison_policy"]["mv_eq_equals_biological_mv"] = True
    assert canonical_sha256(changed) != document["contract_id"]


def test_unique_ids_references_and_statuses(document):
    contract = document["contract"]
    indexes = {}
    for group in ("model_variables", "assays", "mappings", "evidence_sources"):
        ids = [row["id"] for row in contract[group]]
        assert len(ids) == len(set(ids))
        indexes[group] = set(ids)
    for row in contract["model_variables"]:
        assert row["operator_status"] in OPERATOR_STATUSES
        assert row["calibration_status"] in CALIBRATION_STATUSES
        assert set(row["mapping_ids"]) <= indexes["mappings"]
        assert set(row["evidence_sources"]) <= indexes["evidence_sources"]
        assert set(row["compatible_assays"]) <= set(contract["assay_types"])
        for key in (
            "model_name",
            "model_units",
            "source_class",
            "allowed_interpretation",
            "forbidden_interpretation",
            "temporal_semantics",
            "population_semantics",
            "identifiability_status",
        ):
            assert row[key]
    for row in contract["mappings"]:
        assert row["variable_id"] in indexes["model_variables"]
        assert row["assay_id"] is None or row["assay_id"] in indexes["assays"]
        assert row["operator_status"] in OPERATOR_STATUSES
        assert row["calibration_status"] in CALIBRATION_STATUSES
        assert row["numerical_biological_comparison_allowed"] is False


def test_complete_assay_matrix_and_no_silent_calibration(document):
    contract = document["contract"]
    rows = contract["compatibility_matrix"]["rows"]
    assert {r["variable_id"] for r in rows} == {
        r["id"] for r in contract["model_variables"]
    }
    for row in rows:
        assert len(row["cells"]) == len(contract["assay_types"])
        assert set(row["cells"]) <= {
            "DIRECT",
            "TRANSFORM_REQUIRED",
            "QUALITATIVE_ONLY",
            "INCOMPATIBLE",
            "NOT_APPLICABLE",
        }
    policy = contract["comparison_policy"]
    assert policy["numeric_comparison_enabled"] is False
    assert policy["structural_counts_used_as_observation_weights"] is False
    assert policy["mv_eq_equals_biological_mv"] is False
    assert policy["sensory_state_equals_fluorescence"] is False
    assert policy["population_response_divided_by_body_count_is_efficacy"] is False
    assert policy["behavior_calibrates_transfer"] is False
    for row in contract["model_variables"]:
        assert row["source_class"] in contract["source_classes"]
        if row["model_units"] in {"mV_eq", "world_eq", "dimensionless_state"}:
            assert row["calibration_status"] != "CALIBRATED"
    assert contract["identifiability"]["future_calibration_protocol"] is None


def test_assay_metadata_and_required_variables(document):
    contract = document["contract"]
    assert {
        "relative_column_exposure",
        "sensory_state",
        "sensory_contribution",
        "aggregate_drive",
        "dnp01_membrane",
        "dnp01_spikes",
        "ttmn_state",
        "electrical_input_token",
        "g1_proxy",
        "activation_proxy",
        "actuator_command",
        "planar_body",
    } <= {r["id"] for r in contract["model_variables"]}
    for row in contract["assays"]:
        for key in (
            "neuron_population",
            "preparation",
            "stimulus",
            "observable",
            "units",
            "baseline",
            "time_reference",
            "temporal_resolution",
            "population_aggregation",
            "reported_result",
            "data_form",
            "data_sufficiency",
            "relevance",
            "limitations",
        ):
            assert row[key]
        assert row["assay_type"] in contract["assay_types"]
        assert row["data_sufficiency"] in {
            "SUFFICIENT_FOR_CALIBRATION",
            "SUFFICIENT_FOR_OPERATOR_DESIGN_ONLY",
            "QUALITATIVE_ONLY",
            "NOT_LOCATED",
            "INCOMPATIBLE",
        }
    assert contract["decisions"]["scientific"] == (
        "OBSERVATION_OPERATOR_SPECIFIED_CALIBRATION_NOT_READY"
    )
