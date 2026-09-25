"""Phase 7H deterministic sample, generalization, and replay regressions."""

from __future__ import annotations

from dataclasses import replace

import pytest

from neurofly.bounded_sensory_population import (
    SENTINELS,
    STRATA,
    _maximin_candidate,
    _stratum_rank_bands,
    compute_population_experiment,
    make_source_bundle,
    select_bounded_sample,
)
from neurofly.bounded_sensory_population_artifacts import (
    BoundedPopulationArtifactError,
    export_population_artifact,
    export_sample_artifact,
    population_artifact_id,
    replay_population_artifact,
    replay_sample_artifact,
    sample_artifact_id,
)
from neurofly.relative_column_assignment import (
    DEFAULT_SOURCE_ROOT,
    DEFAULT_WORKBOOK,
    canonical_json_bytes,
    sha256_bytes,
)
from neurofly.relative_column_dnp01_artifacts import (
    DEFAULT_OUTPUT_ROOT as PHASE7F_OUTPUT_ROOT,
)
from neurofly.relative_column_dnp01_artifacts import (
    DEFAULT_SENSORY_ARTIFACT_PATH as PHASE7F_SENSORY_PATH,
)
from neurofly.relative_column_dnp01_artifacts import (
    replay_artifact as replay_phase7f,
)
from neurofly.relative_column_dnp01_transfer import (
    Route,
    route_population_drive,
)
from neurofly.relative_column_sensory_artifacts import (
    DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    replay_relative_column_sensory_artifact,
)
from neurofly.relative_column_sensory_artifacts import (
    DEFAULT_OUTPUT_ROOT as PHASE7E_OUTPUT_ROOT,
)

PHASE7E_ID = "09a3d3ddc02c81bb5ea229bf48b76811123ebd2e20cfce17f45e72442dcb8b15"
PHASE7F_ID = "4a000add359e60c0c0c654881a4659652d749c548af0e167469d210035c20213"
SAMPLE_ID = "18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7"
POPULATION_ID = "385480b3c915b25536e1119d17effa15567bc0c1afcfe73037e5dd5d69102958"

SOURCE_AVAILABLE = all(
    path.exists()
    for path in (
        DEFAULT_SOURCE_ROOT,
        DEFAULT_WORKBOOK,
        DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
        PHASE7E_OUTPUT_ROOT / PHASE7E_ID,
        PHASE7F_SENSORY_PATH,
        PHASE7F_OUTPUT_ROOT / PHASE7F_ID,
    )
)


@pytest.fixture(scope="module")
def phase7h_run():
    if not SOURCE_AVAILABLE:
        pytest.skip("pinned Phase 7D–7F local sources are unavailable")
    source, grid, circuit = make_source_bundle()
    sample_config, sample_result = select_bounded_sample(source, circuit)
    sample_input = _sample_input(sample_config, sample_result)
    baseline_sensory = replay_relative_column_sensory_artifact(
        PHASE7E_OUTPUT_ROOT / PHASE7E_ID,
        assignment_artifact_path=DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    )
    baseline_transfer = replay_phase7f(
        PHASE7F_OUTPUT_ROOT / PHASE7F_ID,
        sensory_artifact_path=PHASE7F_SENSORY_PATH,
        assignment_artifact_path=DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    )
    config, result = compute_population_experiment(
        sample_input,
        source,
        grid,
        circuit,
        baseline_sensory,
        baseline_transfer,
    )
    return source, circuit, sample_config, sample_result, sample_input, config, result


def _sample_input(config, result):
    config_hash = sha256_bytes(canonical_json_bytes(config) + b"\n")
    result_hash = sha256_bytes(canonical_json_bytes(result) + b"\n")
    manifest = {
        "artifact_schema": "bounded_sensory_sample_artifact_v1",
        "artifact_id": sample_artifact_id(config, result),
        "config_sha256": config_hash,
        "result_sha256": result_hash,
        "sample_size": 16,
        "body_ids": result["body_ids"],
    }
    return {
        "artifact_id": manifest["artifact_id"],
        "manifest_sha256": sha256_bytes(canonical_json_bytes(manifest) + b"\n"),
        "config_sha256": config_hash,
        "result_sha256": result_hash,
        "config": config,
        "result": result,
    }


def _condition(result, condition_id):
    return next(
        item for item in result["conditions"] if item["condition_id"] == condition_id
    )


def _target(condition, body_id):
    return next(item for item in condition["targets"] if item["body_id"] == body_id)


def test_sample_is_exact_balanced_and_outcome_independent(phase7h_run):
    _, circuit, config, result, _, _, _ = phase7h_run
    assert config["selection_excludes_model_outcomes"] is True
    assert result["model_outcomes_used"] is False
    assert result["body_ids"] == [
        12032,
        16809,
        14888,
        514956,
        16128,
        38065,
        21804,
        19634,
        11498,
        40811,
        29815,
        515971,
        14465,
        37925,
        21045,
        22261,
    ]
    assert [
        (item["neuron_type"], item["side"], item["count"])
        for item in result["stratum_counts"]
    ] == [(neuron_type, side, 4) for neuron_type, side in STRATA]
    selected = result["selected_bodies"]
    assert {item["body_id"] for item in selected if item["sentinel"]} == set(
        SENTINELS.values()
    )
    assert all(
        item["target_body_id"] == (10001 if item["side"] == "R" else 10010)
        for item in selected
    )
    assert all(item["body_id"] in circuit.neurons_by_body_id for item in selected)
    for neuron_type, side in STRATA:
        rows = [
            item
            for item in selected
            if item["neuron_type"] == neuron_type and item["side"] == side
        ]
        assert len(rows) == 4
        assert {item["selection_band"] for item in rows if not item["sentinel"]} == {
            "low",
            "middle",
            "high",
        }


def test_rank_partitions_are_balanced_and_deterministic():
    candidates = [
        {"body_id": body_id, "structural_weight": weight}
        for body_id, weight in ((8, 1), (3, 1), (9, 2), (1, 2), (7, 2), (4, 8), (6, 9))
    ]
    first = _stratum_rank_bands(candidates)
    second = _stratum_rank_bands(tuple(reversed(candidates)))
    assert first == second
    counts = [
        sum(item["band_index"] == index for item in first.values())
        for index in range(3)
    ]
    assert max(counts) - min(counts) <= 1
    assert first[3]["rank"] == 0
    assert first[8]["rank"] == 1


def test_lattice_maximin_prefers_separation_then_smallest_body_id():
    prior = [{"body_id": 20, "anatomical_column_centroid": [0.0, 0.0]}]
    candidates = [
        {"body_id": 10, "anatomical_column_centroid": [-3.0, 0.0]},
        {"body_id": 5, "anatomical_column_centroid": [3.0, 0.0]},
        {"body_id": 1, "anatomical_column_centroid": [1.0, 0.0]},
    ]
    selected, minimum_distance = _maximin_candidate(candidates, prior)
    assert selected["body_id"] == 5
    assert minimum_distance == 3.0
    reversed_selection, reversed_distance = _maximin_candidate(
        tuple(reversed(candidates)), prior
    )
    assert reversed_selection == selected
    assert reversed_distance == minimum_distance


def test_sample_artifact_hash_and_source_replay(phase7h_run, tmp_path):
    _, _, config, result, _, _, _ = phase7h_run
    artifact_id = sample_artifact_id(config, result)
    assert artifact_id == SAMPLE_ID
    destination = tmp_path / artifact_id
    export_sample_artifact(config, result, destination)
    replayed = replay_sample_artifact(destination)
    assert replayed.artifact_id == artifact_id
    assert replayed.result == result
    assert replayed.manifest["body_ids"] == result["body_ids"]


def test_sample_selection_rejects_changed_pinned_source_identity(phase7h_run):
    source, circuit, *_ = phase7h_run
    changed_source_identity = dict(source.source_identity)
    changed_source_identity["source_file_sha256"] = {
        "column_inputs.jsonl": "0" * 64,
        "column_body_summaries.jsonl": "1" * 64,
    }
    changed_source = replace(source, source_identity=changed_source_identity)
    with pytest.raises(ValueError, match="source contract identity/hash is not pinned"):
        select_bounded_sample(changed_source, circuit)

    changed_integrity = replace(
        circuit.integrity,
        sha256_by_file=(
            ("connections.jsonl", "0" * 64),
            ("neurons.jsonl", "1" * 64),
        ),
    )
    changed_circuit = replace(circuit, integrity=changed_integrity)
    with pytest.raises(ValueError, match="source contract identity/hash is not pinned"):
        select_bounded_sample(source, changed_circuit)


def test_assignment_and_sensory_states_generalize_and_preserve_sentinels(phase7h_run):
    _, _, _, sample_result, _, _, result = phase7h_run
    assert result["assignment"]["body_ids"] == sample_result["body_ids"]
    assert result["assignment"]["sample_count"] == 18
    assert len(result["sensory_trajectories_by_stimulus"]) == 6
    assert (
        result["sentinel_state_regression"][
            "all_reference_sentinel_state_traces_identical"
        ]
        is True
    )
    for sample in result["assignment"]["samples"]:
        assert [row["body_id"] for row in sample["assignments"]] == sample_result[
            "body_ids"
        ]
        assert len(sample["active_columns"]) == sample["active_column_count"]
        assert all(
            row["semantic_classification"] == "ANATOMICAL_EXPOSURE"
            and row["neural_response_present"] is False
            for row in sample["assignments"]
        )
        if sample["side"] == "L":
            assert all(
                row["column_overlap_fraction"] == 0.0
                for row in sample["assignments"]
                if row["side"] == "R"
            )
        else:
            assert all(
                row["column_overlap_fraction"] == 0.0
                for row in sample["assignments"]
                if row["side"] == "L"
            )


def test_routes_are_source_derived_and_structural_counts_are_not_gain(phase7h_run):
    _, circuit, _, sample_result, _, config, result = phase7h_run
    routes = config["route_contract"]
    assert len(routes) == 16
    assert {row["source_body_id"] for row in routes} == set(sample_result["body_ids"])
    circuit_weights = {
        edge.source_body_id: edge.structural_weight
        for edge in circuit.connections
        if edge.source_body_id in sample_result["body_ids"]
        and edge.target_type == "DNp01"
    }
    assert {
        row["source_body_id"]: row["structural_weight"] for row in routes
    } == circuit_weights
    assert all(
        row["side"] == ("R" if row["target_body_id"] == 10001 else "L")
        for row in routes
    )
    assert all(
        row["weight_semantics"] == "STRUCTURAL_COUNT_ROUTING_METADATA_ONLY"
        for row in routes
    )
    states = {body_id: 0.2 for body_id in sample_result["body_ids"]}
    route_values = tuple(
        Route(
            source_body_id=row["source_body_id"],
            target_body_id=row["target_body_id"],
            structural_weight=row["structural_weight"],
            source_type=row["source_type"],
            side=row["side"],
        )
        for row in routes
    )
    baseline = route_population_drive(
        states,
        route_values,
        target_body_ids=(10001, 10010),
        active_source_ids=set(states),
        k_transfer_mveq_per_state=1.0,
    )
    changed_metadata = tuple(
        replace(route, structural_weight=999) for route in route_values
    )
    changed = route_population_drive(
        states,
        changed_metadata,
        target_body_ids=(10001, 10010),
        active_source_ids=set(states),
        k_transfer_mveq_per_state=1.0,
    )
    assert changed == baseline
    assert result["sentinel_state_regression"][
        "all_reference_sentinel_state_traces_identical"
    ]


def test_controls_summation_and_scale_comparison(phase7h_run):
    _, _, _, sample_result, _, _, result = phase7h_run
    zero = _condition(result, "k_zero")
    none = _condition(result, "no_sources")
    assert all(target["peak_drive_mveq"] == 0.0 for target in zero["targets"])
    assert all(target["peak_drive_mveq"] == 0.0 for target in none["targets"])
    assert all(target["maximum_membrane_mv"] == -52.0 for target in zero["targets"])
    assert all(target["maximum_membrane_mv"] == -52.0 for target in none["targets"])
    left = _condition(result, "left_only")
    right = _condition(result, "right_only")
    assert _target(left, 10001)["peak_drive_mveq"] == 0.0
    assert _target(right, 10010)["peak_drive_mveq"] == 0.0
    assert len(_condition(result, "lc4_only")["active_source_body_ids"]) == 8
    assert len(_condition(result, "lplc2_only")["active_source_body_ids"]) == 8
    assert _condition(result, "sentinels_only")["active_source_body_ids"] == sorted(
        SENTINELS.values()
    )
    for condition in result["conditions"]:
        assert (
            len(condition["source_contributions_by_interval"])
            == condition["interval_count"]
        )
        for interval in condition["source_contributions_by_interval"]:
            for target in (10001, 10010):
                source_sum = sum(
                    row["model_drive_mveq"]
                    for row in interval["contributions"]
                    if row["target_body_id"] == target
                )
                target_series = _target(condition, target)["drive_mveq_by_interval"]
                assert source_sum == pytest.approx(
                    target_series[interval["step"]], rel=0.0, abs=1e-15
                )
    assert (
        result["scale_comparison"]["stimulus_comparisons"][0]["four_body_sentinel"][
            "active_sensory_state_count"
        ]
        == 4
    )
    assert (
        result["scale_comparison"]["stimulus_comparisons"][0]["sixteen_body"][
            "active_sensory_state_count"
        ]
        == 16
    )
    assert len(result["body_ids"]) == 16


def test_sample_source_hash_or_payload_mismatch_fails_closed(phase7h_run):
    source, circuit, _, _, sample_input, _, _ = phase7h_run
    changed = dict(sample_input)
    changed["config"] = dict(sample_input["config"])
    changed["config"]["selection_method_id"] = "outcome_chosen"
    _, grid, _ = make_source_bundle()
    baseline_sensory = replay_relative_column_sensory_artifact(
        PHASE7E_OUTPUT_ROOT / PHASE7E_ID,
        assignment_artifact_path=DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    )
    baseline_transfer = replay_phase7f(
        PHASE7F_OUTPUT_ROOT / PHASE7F_ID,
        sensory_artifact_path=PHASE7F_SENSORY_PATH,
        assignment_artifact_path=DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    )
    with pytest.raises(ValueError, match="sample artifact does not replay"):
        compute_population_experiment(
            changed,
            source,
            grid,
            circuit,
            baseline_sensory,
            baseline_transfer,
        )


def test_full_immutable_artifact_replay_and_tamper_rejection(phase7h_run, tmp_path):
    _, _, sample_config, sample_result, sample_input, config, result = phase7h_run
    assert population_artifact_id(config, result) == POPULATION_ID
    sample_path = tmp_path / "sample" / sample_artifact_id(sample_config, sample_result)
    export_sample_artifact(sample_config, sample_result, sample_path)
    experiment_path = tmp_path / "experiment" / population_artifact_id(config, result)
    artifact = export_population_artifact(config, result, experiment_path)
    assert artifact.artifact_id == population_artifact_id(config, result)
    replayed = replay_population_artifact(experiment_path, sample_path)
    assert replayed.artifact_id == artifact.artifact_id
    assert replayed.result == result

    result_path = experiment_path / "population_result.json"
    original = result_path.read_bytes()
    result_path.write_bytes(original + b" ")
    from neurofly.bounded_sensory_population_artifacts import (
        load_population_artifact,
    )

    with pytest.raises(BoundedPopulationArtifactError, match="canonical JSON"):
        load_population_artifact(experiment_path)
