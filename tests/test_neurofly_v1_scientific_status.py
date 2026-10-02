"""Scientific-governance freeze; never a production runtime dependency."""

import copy
import json
from pathlib import Path

import pytest

from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/science/neurofly_v1_scientific_status.json"
STATUS_ID = "1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6"


@pytest.fixture
def document():
    return json.loads(DOCUMENT.read_text())


def test_canonical_freeze_identity_and_tamper_detection(document):
    status = document["status"]
    assert document["schema"] == status["schema"] == "neurofly_v1_scientific_status_v1"
    assert document["status_id"] == canonical_sha256(status) == STATUS_ID
    assert status["completion_decision"] == (
        "NEUROFLY_V1_INITIAL_CIRCUIT_VALIDATION_COMPLETE"
    )
    altered = copy.deepcopy(status)
    altered["frozen_contracts"]["transfer"]["k"] = 2.0
    assert canonical_sha256(altered) != STATUS_ID


def test_authorities_reference_existing_immutable_documents(document):
    authorities = document["status"]["authorities"]
    assert len(authorities) == len({a["key"] for a in authorities}) == 18
    for authority in authorities:
        path = Path(authority["document"])
        assert not path.is_absolute()
        assert authority["id"] in (ROOT / path).read_text()
    by_key = {a["key"]: a for a in authorities}
    for phase, filename, payload_key, id_key in (
        ("phase19", "sensory_dnp01_transfer_evidence_review", "review", "review_id"),
        (
            "phase20",
            "observation_operator_assay_compatibility",
            "contract",
            "contract_id",
        ),
        ("phase21", "gf_voltage_dataset_compatibility_audit", "audit", "audit_id"),
        (
            "phase22",
            "gf_voltage_dataset_metadata_resolution",
            "resolution",
            "resolution_id",
        ),
    ):
        source = json.loads((ROOT / f"docs/science/{filename}.json").read_text())
        assert source[id_key] == canonical_sha256(source[payload_key])
        assert source[id_key] == by_key[phase]["id"]


def test_uncalibrated_contracts_and_non_efficacy(document):
    status = document["status"]
    contracts = status["frozen_contracts"]
    transfer = contracts["transfer"]
    assert transfer["k"] == 1.0
    assert transfer["k_units"] == "mV_eq/state"
    assert transfer["classification"] == "EXPLORATORY_UNCALIBRATED_MODEL_ASSUMPTION"
    assert transfer["normalization"] == "UNNORMALIZED_ADDITIVE_SUM"
    assert transfer["population_cardinality_affects_drive"] is True
    assert transfer["expansion_requires_contract_review"] is True
    assert status["empirical_structure"]["structural_count_used_as_efficacy"] is False
    assert status["empirical_structure"]["structural_count_semantics"] == (
        "STRUCTURAL_COUNT_ROUTING_METADATA_ONLY"
    )
    assert contracts["units"]["mV_eq"]["status"] == (
        "UNCALIBRATED_MODEL_SPACE_VOLTAGE_EQUIVALENT"
    )
    assert contracts["units"]["mV_eq"]["biological_mV_equivalence"] is False
    assert contracts["units"]["world_eq"]["status"] == (
        "EXPLORATORY_MODEL_SPACE_SPATIAL_COORDINATE"
    )
    assert contracts["units"]["world_eq"]["physical_length_equivalence"] is False
    assert status["evidence_classifications"]["limitations_independent"] is False
    assert status["evidence_classifications"]["corrected_projection_limiter"] == (
        "MATERIAL_MODEL_LIMITER"
    )


def test_canonical_scenario_null_results_and_frontend_authority(document):
    status = document["status"]
    scenarios = {s["kind"]: s for s in status["canonical_scenarios"]}
    assert set(scenarios) == {
        "BASELINE_CONTROL",
        "LOOMING_CIRCUIT_VALIDATION",
        "LOOMING_WORLD_EXPERIMENT",
    }
    for scenario in scenarios.values():
        assert scenario["sensory_body_count"] == 311
        assert scenario["boundaries"] == scenario["intervals"] + 1
        assert scenario["intervals"] * scenario["dt_ms"] == pytest.approx(
            scenario["duration_ms"]
        )
        for field in (
            "dnp01_spike_count",
            "motor_output_event_count",
            "nonzero_actuator_command_count",
            "body_displacement_world_eq",
        ):
            assert scenario[field] == 0
        flags = scenario["statuses"]
        assert flags["closed_loop_execution_completed"] is True
        assert flags["body_state_feedback_wired"] is True
        assert flags["body_state_feedback_realized"] is False
        assert flags["body_movement_occurred"] is False
        assert flags["genuine_nonzero_actuation_occurred"] is False
        assert (
            flags["environment_affected_sensory_input"] == scenario["stimulus_enabled"]
        )
    assert scenarios["BASELINE_CONTROL"]["stimulus_enabled"] is False
    assert scenarios["BASELINE_CONTROL"]["exposed_bodies_range"] == [0, 0]
    assert scenarios["LOOMING_CIRCUIT_VALIDATION"]["duration_ms"] == 1.4
    assert scenarios["LOOMING_CIRCUIT_VALIDATION"]["projection_radius_range"] == [2, 3]
    world = scenarios["LOOMING_WORLD_EXPERIMENT"]
    assert world["duration_ms"] == 40
    assert world["projection_radius_range"] == [2, 4]
    assert world["termination"] == "COMPLETED_VALID_HORIZON"
    assert status["frontend"]["scientific_state_authority"] == "BACKEND"
    assert status["frontend"]["behavior_decisions"] is False
    assert status["frontend"]["scientific_integration"] is False
    # Derived artifacts are ignored and optional in a fresh checkout. When
    # available, verify every summary against scientific bytes, not just prose.
    authorities = {a["key"]: a for a in status["authorities"]}
    base = ROOT / "data/derived/malecns/looming_giant_fiber_v1"
    for key, directory, filename in (
        ("phase13b", "closed_loop_scenario_artifact_v1", "scenarios.json"),
        ("phase18", "looming_world_experiment_artifact_v1", "experiment.json"),
    ):
        path = base / directory / authorities[key]["id"] / filename
        if not path.exists():
            continue
        artifact = json.loads(path.read_text())
        assert artifact["artifact_id"] == authorities[key]["id"]
        assert artifact["result_sha256"] == canonical_sha256(artifact["result"])
        runs = (
            [run["result"] for run in artifact["result"]["runs"]]
            if key == "phase13b"
            else [artifact["result"]]
        )
        for result in runs:
            summary = scenarios[result["scenario_kind"]]
            assert result["statuses"] == summary["statuses"]
            assert len(result["world_body"]) == summary["boundaries"]
            assert len(result["sensory_identities"]) == summary["sensory_body_count"]
            assert len(result["dnp01_spikes"]) == summary["dnp01_spike_count"]
            for side, index in (("R", 0), ("L", 1)):
                assert (
                    max(row[index] for row in result["dnp01_membrane_mv"])
                    == (summary[f"dnp01_peak_{side}_mV_eq"])
                )
            frames = result["telemetry"]
            assert [
                min(f["active_sensory_body_count"] for f in frames),
                max(f["active_sensory_body_count"] for f in frames),
            ] == summary["exposed_bodies_range"]
            assert all(
                f["body"]["x_world_eq"] == f["body"]["z_world_eq"] == 0
                and all(command == 0 for command in f["actuator_commands"].values())
                for f in frames
            )
            assert (
                len(result["downstream_events"]["motor_outputs"])
                == (summary["motor_output_event_count"])
            )
            if summary["stimulus_enabled"]:
                assert [
                    min(f["lattice_radius"] for f in frames),
                    max(f["lattice_radius"] for f in frames),
                ] == summary["projection_radius_range"]
            else:
                assert all(f["object"] is None for f in frames)
            if key == "phase18":
                assert result["termination"]["status"] == summary["termination"]


def test_closed_calibration_branch_claim_budget_and_no_dataset_paths(document):
    status = document["status"]
    branch = status["calibration_branch"]
    assert branch["status"] == "PHYSIOLOGICAL_TRANSFER_CALIBRATION_NOT_ESTABLISHED"
    assert branch["v1_branch"] == "CLOSED_FOR_V1"
    assert branch["candidate_classification"] == "METADATA_INSUFFICIENT"
    assert branch["author_contact_planned"] is False
    assert branch["additional_acquisition_planned"] is False
    assert "New public compatible data" in branch["reopen_condition"]
    forbidden = set(status["claims"]["forbidden"])
    assert forbidden.isdisjoint(status["claims"]["allowed"])
    assert {
        "Complete fly emulation",
        "Whole-connectome neural simulation",
        "Biologically calibrated DNp01 voltage",
        "Calibrated retinal geometry",
        "Calibrated physical world",
        "Calibrated jump or escape behavior",
        "Predicted biological escape probability",
        "Consciousness or sentience",
        "Genuine memory",
        "Genuine learning",
    } <= forbidden
    assert status["next_development"]["decision"] == (
        "EVIDENCE_GATED_SECOND_BOUNDED_CONNECTOME_CIRCUIT_MILESTONE"
    )
    assert status["next_development"]["circuit_selected"] is None
    text = DOCUMENT.read_text()
    for path_fragment in ("/home/", "data/raw/", "phase21_dataset_audit/", ".mat"):
        assert path_fragment not in text
