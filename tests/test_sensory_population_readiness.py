"""Phase 7N all-311 identity, anatomy, routing, and dry-run contracts."""

from __future__ import annotations

import json
import shutil

import pytest

from neurofly.bounded_sensory_population import _mask_ids, _route_set
from neurofly.bounded_sensory_scale128 import (
    CANONICAL_EXPERIMENT128_ID,
    CANONICAL_PLAN128_ID,
    scale128_artifact_path,
)
from neurofly.bounded_sensory_scale128_artifacts import load_scale128_artifact
from neurofly.relative_column_assignment import (
    EXPECTED_CIRCUIT_FILE_HASHES,
    EXPECTED_COLUMN_FILE_HASHES,
    canonical_json_bytes,
)
from neurofly.relative_column_dnp01_transfer import Route, route_population_drive
from neurofly.sensory_population_readiness import (
    POPULATION_SIZE,
    REFERENCE_K_MVEQ_PER_STATE,
    TYPE_COUNTS,
    TYPE_SIDE_COUNTS,
    SensoryPopulationReadinessError,
    build_execution_dry_run,
    build_full_coverage_plan,
    build_full_population_plan,
    export_readiness_artifact,
    load_phase7n_sources,
    load_readiness_artifact,
    replay_full_coverage_plan,
)


@pytest.fixture(scope="module")
def readiness_run(tmp_path_factory):
    source, circuit, grid = load_phase7n_sources()
    plan128 = load_scale128_artifact(
        scale128_artifact_path("plan", CANONICAL_PLAN128_ID), "plan"
    )
    population_config, population_result = build_full_population_plan(
        source, circuit, grid
    )
    root = tmp_path_factory.mktemp("phase7n")
    population = export_readiness_artifact(
        "population", population_config, population_result, output_root=root / "pop"
    )
    coverage_config, coverage_result = build_full_coverage_plan(
        population, plan128, source, circuit, grid
    )
    coverage = export_readiness_artifact(
        "coverage", coverage_config, coverage_result, output_root=root / "coverage"
    )
    execution_config, execution_result = build_execution_dry_run(
        population, coverage, source, circuit
    )
    execution = export_readiness_artifact(
        "execution", execution_config, execution_result, output_root=root / "exec"
    )
    return {
        "source": source,
        "circuit": circuit,
        "grid": grid,
        "plan128": plan128,
        "population": population,
        "coverage": coverage,
        "execution": execution,
    }


def test_population_is_exact_complete_source_identity_and_route_set(readiness_run):
    run = readiness_run
    population = run["population"]
    config, result = population.config, population.result

    assert (
        population.artifact_id
        == "0db2b29f168039e23858db9831e345cc25fdec8c06775e2f23a7d8d681544356"
    )
    assert result["population_semantics"] == "COMPLETE_TARGET_POPULATION"
    assert result["body_count"] == POPULATION_SIZE == 311
    assert len(result["body_ids"]) == len(set(result["body_ids"])) == 311
    assert config["type_counts"] == TYPE_COUNTS == {"LC4": 126, "LPLC2": 185}
    assert set(result["body_ids"]) == {
        node.body_id for node in run["circuit"].neurons if node.type in {"LC4", "LPLC2"}
    }
    assert {
        (item["neuron_type"], item["side"]): item["count"]
        for item in config["type_side_counts"]
    } == TYPE_SIDE_COUNTS
    assert result["route_target_counts"] == [
        {"target_body_id": 10001, "source_count": 146},
        {"target_body_id": 10010, "source_count": 165},
    ]
    assert result["source_body_column_record_count"] == 25_438
    assert result["assigned_input_site_count"] == 574_745
    assert result["unassigned_input_site_count"] == 2_790
    assert result["all_bodies_have_column_topology"] is True
    assert result["all_source_coordinates_are_valid_relative_hex"] is True
    assert result["dynamic_state_present"] is False
    assert result["model_outcome_present"] is False
    assert config["model_outcomes_used"] is False
    assert config["source_contract_identity"]["source_file_sha256"] == (
        EXPECTED_COLUMN_FILE_HASHES
    )
    assert config["circuit_contract_identity"]["file_sha256"] == (
        EXPECTED_CIRCUIT_FILE_HASHES
    )
    assert not any(key.startswith("parent_sample") for key in config)

    rows = result["bodies"]
    assert len(rows) == 311
    assert all(row["body_column_source_available"] for row in rows)
    assert all(row["dynamic_state_present"] is False for row in rows)
    assert all(row["model_outcome_present"] is False for row in rows)
    assert all(row["target_body_id"] in {10001, 10010} for row in rows)
    assert all(
        row["structural_edge_count_semantics"]
        == "SOURCE_STRUCTURAL_COUNT_METADATA_ONLY"
        for row in rows
    )
    assert len(result["bodies_using_unclassified_coordinates"]) == 9
    assert result["official_grid_unclassified_source_coordinates"] == {
        "L": [[17, 34], [19, 35]],
        "R": [],
    }


def test_coverage_is_anatomy_only_and_extends_exactly_to_311(readiness_run):
    coverage = readiness_run["coverage"]
    config, result = coverage.config, coverage.result

    assert (
        coverage.artifact_id
        == "0331ff3d309892ac5284e0da3898683df7b5fb8fd06055090b6100dcea4a6e56"
    )
    assert result["initial_covered_count"] == 299
    assert result["initial_uncovered_body_ids"] == [
        12384,
        18189,
        18396,
        19550,
        22677,
        23226,
        23919,
        32597,
        33137,
        518983,
        524366,
        533129,
    ]
    assert result["covered_body_count"] == 311
    assert result["uncovered_body_ids"] == []
    assert result["stimulus_count"] == 27
    assert len(result["coverage_extension_stimuli"]) == 4
    assert all(
        row["model_outcomes_used"] is False
        and row["coverage_basis"] == "binary_column_overlap_only"
        and row["centre_is_source_column"]
        and 1 <= row["radius_lattice_steps"] <= 4
        for row in result["coverage_extension_stimuli"]
    )
    assert all(
        entry["origin"] == "PHASE7M_BATTERY_CONFIG_RETAINED"
        for entry in config["stimuli"][:23]
    )
    assert result["neural_dynamics_computed"] is False
    assert result["dn_p01_outputs_read_for_design"] is False
    assert config["model_outcomes_used"] is False
    assert [
        row["covered_count"] for row in result["initial_coverage_by_type_side"]
    ] == [65, 53, 91, 90]
    assert [
        row["uncovered_count"] for row in result["initial_coverage_by_type_side"]
    ] == [6, 2, 3, 1]
    assert [row["covered_count"] for row in result["final_coverage_by_type_side"]] == [
        71,
        55,
        94,
        91,
    ]


def test_dry_run_config_is_exact_and_contains_no_normalization_or_dynamics(
    readiness_run,
):
    run = readiness_run
    artifact = run["execution"]
    config, result = artifact.config, artifact.result

    assert (
        artifact.artifact_id
        == "a7d828993674634875b8b8862d40083690e77bb8aa748ad7079135cc8e10725f"
    )
    assert result["body_count"] == 311
    assert len(result["body_routes"]) == 311
    assert len(result["target_body_ids"]) == 2
    assert result["stimulus_count"] == 27
    assert result["assignment_sample_count"] == 39
    assert result["expected_assignment_body_exposure_rows"] == 12_129
    assert result["expected_state_boundary_values_per_body"] == 336
    assert result["planned_condition_count"] == 35
    assert result["planned_model_interval_count"] == 421
    assert result["expected_contribution_ledger_rows"] == 130_931
    assert result["dynamic_results_present"] is False
    assert result["sensory_trajectories_computed"] is False
    assert result["transfer_ledger_computed"] is False
    assert result["dn_p01_execution_performed"] is False
    assert config["sensory_model"]["model_id"] == (
        "relative_column_exploratory_sensory_state_v1"
    )
    assert config["sensory_model"]["tau_sens_ms"] == 1.0
    assert config["sensory_model"]["gain"] == 1.0
    assert config["sensory_model"]["initial_state"] == 0.0
    assert config["sensory_model"]["input_metric_id"] == "column_overlap_fraction"
    assert config["transfer_model"]["k_transfer_mveq_per_state"] == (
        REFERENCE_K_MVEQ_PER_STATE
    )
    assert config["transfer_model"]["source_normalization"] == "none"
    assert config["transfer_model"]["structural_weight_used_as_gain"] is False
    assert config["population_normalization"] == "none"
    assert config["structural_edge_count_numerical_use"] == "none_source_metadata_only"
    assert config["dnp01_model"]["config"]["dt_ms"] == 0.1
    assert config["historical_sample_chain_required"] is False
    assert run["coverage"].artifact_id in json.dumps(config)
    baseline = load_scale128_artifact(
        scale128_artifact_path("experiment", CANONICAL_EXPERIMENT128_ID),
        "experiment",
    )
    assert config["sensory_model"] == baseline.config["sensory_model"]
    assert config["transfer_model"] == baseline.config["transfer_model"]
    assert config["dnp01_model"] == baseline.config["dnp01_model"]
    assert (
        config["model_config_reference"]["config_sha256"]
        == (baseline.manifest["config_sha256"])
    )


def test_routes_and_arbitrary_population_transfer_ignore_structural_counts(
    readiness_run,
):
    rows = readiness_run["population"].result["bodies"]
    route_input = {
        "body_ids": [row["body_id"] for row in rows],
        "selected_bodies": [
            {
                "body_id": row["body_id"],
                "neuron_type": row["neuron_type"],
                "side": row["side"],
                "target_body_id": row["target_body_id"],
                "structural_weight": row["structural_edge_count"],
            }
            for row in rows
        ],
    }
    generic_routes = _route_set(route_input, readiness_run["circuit"])
    assert len(generic_routes) == 311
    assert {route.source_body_id for route in generic_routes} == set(
        route_input["body_ids"]
    )
    small_route_input = {
        "body_ids": route_input["body_ids"][:5],
        "selected_bodies": route_input["selected_bodies"][:5],
    }
    assert len(_route_set(small_route_input, readiness_run["circuit"])) == 5

    route_rows = [
        Route(
            source_body_id=row["body_id"],
            target_body_id=row["target_body_id"],
            structural_weight=row["structural_edge_count"],
            source_type=row["neuron_type"],
            side=row["side"],
        )
        for row in rows
    ]
    states = {row["body_id"]: 0.25 for row in rows}
    active = set(states)
    kwargs = {
        "target_body_ids": (10001, 10010),
        "active_source_ids": active,
        "k_transfer_mveq_per_state": 1.0,
    }
    original_drive, original_ledger = route_population_drive(
        states, route_rows, **kwargs
    )
    changed_weights = [
        Route(
            route.source_body_id,
            route.target_body_id,
            route.structural_weight + 1000,
            route.source_type,
            route.side,
        )
        for route in route_rows
    ]
    changed_drive, changed_ledger = route_population_drive(
        states, changed_weights, **kwargs
    )
    assert original_drive == changed_drive
    assert original_ledger == changed_ledger
    assert len(original_ledger) == 311
    assert original_drive == {10001: 36.5, 10010: 41.25}


def test_generic_all_population_mask_uses_the_supplied_population():
    bodies = [{"body_id": body_id} for body_id in range(311)]
    assert _mask_ids({"selected_bodies": bodies}, "all_population") == set(range(311))


def test_full_replay_is_self_contained_and_content_addressed(readiness_run, tmp_path):
    run = readiness_run
    source, circuit, grid = run["source"], run["circuit"], run["grid"]
    population = load_readiness_artifact(run["population"].path, "population")
    coverage = load_readiness_artifact(run["coverage"].path, "coverage")
    execution = load_readiness_artifact(run["execution"].path, "execution")

    assert build_full_population_plan(source, circuit, grid) == (
        population.config,
        population.result,
    )
    assert replay_full_coverage_plan(population, coverage, source, circuit, grid) == (
        coverage.config,
        coverage.result,
    )
    assert build_execution_dry_run(population, coverage, source, circuit) == (
        execution.config,
        execution.result,
    )
    assert execution.result["dynamic_results_present"] is False

    copied = tmp_path / "tampered"
    shutil.copytree(population.path, copied)
    result_path = copied / "population_result.json"
    data = json.loads(result_path.read_text())
    data["body_count"] = 310
    result_path.write_bytes(canonical_json_bytes(data) + b"\n")
    with pytest.raises(
        SensoryPopulationReadinessError, match="invalid full-population"
    ):
        load_readiness_artifact(copied, "population")

    for kind, artifact, filename, mutate, error in (
        (
            "coverage",
            run["coverage"],
            "coverage_result.json",
            lambda payload: payload.update(covered_body_count=310),
            "invalid all-311 coverage payload",
        ),
        (
            "execution",
            run["execution"],
            "execution_manifest.json",
            lambda payload: payload.update(body_count=310),
            "invalid dry-run execution manifest",
        ),
    ):
        copied = tmp_path / f"tampered-{kind}"
        shutil.copytree(artifact.path, copied)
        result_path = copied / filename
        data = json.loads(result_path.read_text())
        mutate(data)
        result_path.write_bytes(canonical_json_bytes(data) + b"\n")
        with pytest.raises(SensoryPopulationReadinessError, match=error):
            load_readiness_artifact(copied, kind)


def test_phase7m_battery_and_source_hash_mismatches_fail_closed(readiness_run):
    run = readiness_run
    population_input = run["population"].as_input()
    bad_population = dict(population_input)
    bad_population["config"] = dict(population_input["config"])
    bad_population["config"]["source_contract_identity"] = {"changed": True}
    with pytest.raises(
        SensoryPopulationReadinessError, match="failed direct source replay"
    ):
        build_full_coverage_plan(
            bad_population,
            run["plan128"],
            run["source"],
            run["circuit"],
            run["grid"],
        )

    tampered_plan = run["plan128"].as_input()
    tampered_plan["config"] = dict(tampered_plan["config"])
    tampered_plan["config"]["stimuli"] = list(tampered_plan["config"]["stimuli"])
    tampered_plan["config"]["stimuli"][0] = dict(tampered_plan["config"]["stimuli"][0])
    tampered_plan["config"]["stimuli"][0]["sha256"] = "0" * 64
    with pytest.raises(SensoryPopulationReadinessError, match="battery is malformed"):
        build_full_coverage_plan(
            run["population"],
            tampered_plan,
            run["source"],
            run["circuit"],
            run["grid"],
        )


def test_artifacts_are_content_addressed_and_preserve_pinned_config_hashes(
    readiness_run,
):
    run = readiness_run
    assert run["population"].manifest["config_sha256"] == (
        "55206aa053c5cdf7b262132156abd175ddc3ec14792d98228053b3122853d307"
    )
    assert run["coverage"].manifest["config_sha256"] == (
        "f3e47dd552ee12f01e7b3ce637f055d0f51b1393b1770235ce686725ad40c3e3"
    )
    assert run["execution"].manifest["config_sha256"] == (
        "7e2c3d1168a631873e2206796c3ad53ce5cedfd7712676d799521e04451ee7c8"
    )
