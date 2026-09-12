"""Offline tests for the Phase 3C deterministic comparison contract."""

from dataclasses import replace
from pathlib import Path

import pytest

from neurofly.experiment_artifacts import export_experiment_artifact
from neurofly.experiment_comparison import (
    ComparisonCompatibility,
    ComparisonConfigurationError,
    ExperimentComparisonConfig,
    compare_experiment_artifacts,
)
from neurofly.experiments import ExperimentConfig, ExperimentRunner, TelemetrySpec
from neurofly.malecns.contract import load_circuit_contract
from neurofly.malecns.sensory import LoomingStimulus, VisualPoint
from neurofly.sensory_encoder import LevelPEncoderConfig
from neurofly.simulation import LIFConfig
from neurofly.trajectory_characterization import PathwayCondition


@pytest.fixture(scope="module")
def circuit_contract():
    path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "derived"
        / "malecns"
        / "looming_giant_fiber_v1"
    )
    return load_circuit_contract(path)


def _config(
    circuit_contract,
    *,
    lc4_gain=20.0,
    lplc2_gain=20.0,
    omega_half=1.0,
    theta_half=0.4,
    k_syn=0.01,
    dt_ms=0.1,
    pathway=PathwayCondition.COMBINED,
    selected_visual_body_ids=(),
):
    # NEUROFLY_SYNTHETIC_BENCHMARK: comparison fixture, not calibration.
    return ExperimentConfig.from_contract(
        experiment_id="phase3c-comparison-test",
        circuit_contract=circuit_contract,
        stimulus=LoomingStimulus(
            object_radius_m=0.01,
            initial_distance_m=0.1,
            approach_velocity_m_s=1.0,
            center=VisualPoint(azimuth_rad=0.0, elevation_rad=0.0),
        ),
        duration_ms=20.0,
        encoder_config=LevelPEncoderConfig(
            lc4_gain_mv_eq=lc4_gain,
            lplc2_gain_mv_eq=lplc2_gain,
            omega_half_rad_per_s=omega_half,
            theta_half_rad=theta_half,
        ),
        lif_config=LIFConfig(k_syn_mv_per_contact=k_syn, dt_ms=dt_ms),
        telemetry=TelemetrySpec.validation_profile(
            selected_visual_body_ids=selected_visual_body_ids
        ),
        pathway_condition=pathway,
    )


def _artifact(tmp_path, circuit_contract, config, name):
    result = ExperimentRunner(circuit_contract).run(config)
    return export_experiment_artifact(result, tmp_path / name)


def test_identical_artifacts_are_exact_replay_equivalent(tmp_path, circuit_contract):
    config = _config(circuit_contract)
    artifact_a = _artifact(tmp_path, circuit_contract, config, "a")
    artifact_b = _artifact(tmp_path, circuit_contract, config, "b")
    comparison = compare_experiment_artifacts(artifact_a, artifact_b)
    assert comparison.compatibility is ComparisonCompatibility.EXACT_REPLAY_EQUIVALENT
    assert comparison.configuration_differences == ()
    assert comparison.source_model_differences == ()
    assert comparison.events.spike_event_sequences_equal
    assert comparison.events.delivered_event_sequences_equal
    assert comparison.telemetry.dense_trajectory_comparable
    assert all(
        metric.max_abs_membrane_difference_mv == 0.0
        for item in comparison.dnp01
        if (metric := item.trajectory_metrics) is not None
    )
    assert comparison.empirical_validation_status == "NOT_EVALUATED"
    assert comparison.comparison_sha256 == comparison.comparison_sha256
    assert comparison.to_json() == comparison.to_json()


def test_k_syn_difference_is_explicit_and_directly_comparable(
    tmp_path, circuit_contract
):
    low = _config(circuit_contract, k_syn=0.01)
    high = _config(circuit_contract, k_syn=0.02)
    comparison = compare_experiment_artifacts(
        _artifact(tmp_path, circuit_contract, low, "low"),
        _artifact(tmp_path, circuit_contract, high, "high"),
    )
    assert comparison.compatibility is ComparisonCompatibility.DIRECT_MODEL_COMPARISON
    paths = {item.path for item in comparison.configuration_differences}
    assert paths == {"neural.k_syn_mv_per_contact"}
    assert comparison.source_model_differences == ()
    assert all(
        item.total_spike_count_a == item.total_spike_count_b
        for item in comparison.visual_populations
    )
    assert any(
        item.model_increment_sum_difference_mveq != 0.0 for item in comparison.dnp01
    )


def test_lc4_gain_difference_does_not_collapse_other_free_parameters(
    tmp_path, circuit_contract
):
    comparison = compare_experiment_artifacts(
        _artifact(tmp_path, circuit_contract, _config(circuit_contract), "base"),
        _artifact(
            tmp_path,
            circuit_contract,
            _config(circuit_contract, lc4_gain=40.0),
            "lc4-high",
        ),
    )
    assert comparison.compatibility is ComparisonCompatibility.DIRECT_MODEL_COMPARISON
    assert {item.path for item in comparison.configuration_differences} == {
        "encoder.lc4_gain_mv_eq"
    }
    assert comparison.visual_populations[0].peak_drive_difference_mv_eq > 0.0


def test_all_free_parameters_are_individually_reported(tmp_path, circuit_contract):
    comparison = compare_experiment_artifacts(
        _artifact(tmp_path, circuit_contract, _config(circuit_contract), "base-free"),
        _artifact(
            tmp_path,
            circuit_contract,
            _config(
                circuit_contract,
                lc4_gain=30.0,
                lplc2_gain=35.0,
                omega_half=2.0,
                theta_half=0.8,
                k_syn=0.02,
            ),
            "changed-free",
        ),
    )
    assert {item.path for item in comparison.configuration_differences} == {
        "encoder.lc4_gain_mv_eq",
        "encoder.lplc2_gain_mv_eq",
        "encoder.omega_half_rad_per_s",
        "encoder.theta_half_rad",
        "neural.k_syn_mv_per_contact",
    }


def test_pathway_difference_is_reported_without_supralinear_label(
    tmp_path, circuit_contract
):
    comparison = compare_experiment_artifacts(
        _artifact(
            tmp_path,
            circuit_contract,
            _config(circuit_contract, pathway=PathwayCondition.LC4_ONLY),
            "lc4-only",
        ),
        _artifact(tmp_path, circuit_contract, _config(circuit_contract), "combined"),
    )
    assert comparison.compatibility is ComparisonCompatibility.DIRECT_MODEL_COMPARISON
    assert comparison.pathway_condition_a == "LC4_ONLY"
    assert comparison.pathway_condition_b == "COMBINED"
    assert any(
        item.path == "pathway_condition"
        for item in comparison.configuration_differences
    )
    assert "supralinear" not in comparison.to_json().lower()


def test_none_first_spike_semantics_never_create_infinity(tmp_path, circuit_contract):
    zero_a = _artifact(
        tmp_path,
        circuit_contract,
        _config(circuit_contract, pathway=PathwayCondition.ZERO),
        "zero-a",
    )
    zero_b = _artifact(
        tmp_path,
        circuit_contract,
        _config(circuit_contract, pathway=PathwayCondition.ZERO),
        "zero-b",
    )
    unchanged = compare_experiment_artifacts(zero_a, zero_b)
    assert all(
        item.first_spike_timing_status == "NONE_BOTH" for item in unchanged.dnp01
    )
    assert all(item.first_spike_time_difference_ms is None for item in unchanged.dnp01)
    firing = _artifact(
        tmp_path,
        circuit_contract,
        _config(circuit_contract, lc4_gain=100.0, lplc2_gain=100.0),
        "firing",
    )
    transition = compare_experiment_artifacts(zero_a, firing)
    assert all(item.first_spike_timing_status == "B_ONLY" for item in transition.dnp01)
    assert all(item.first_spike_time_difference_ms is None for item in transition.dnp01)
    assert "Infinity" not in transition.to_json()


def test_dt_difference_is_summary_only_without_interpolation(
    tmp_path, circuit_contract
):
    comparison = compare_experiment_artifacts(
        _artifact(tmp_path, circuit_contract, _config(circuit_contract), "dt01"),
        _artifact(
            tmp_path,
            circuit_contract,
            _config(circuit_contract, dt_ms=0.2),
            "dt02",
        ),
    )
    assert comparison.compatibility is ComparisonCompatibility.SUMMARY_ONLY_COMPARISON
    assert not comparison.telemetry.dense_trajectory_comparable
    assert all(item.trajectory_metrics is None for item in comparison.dnp01)
    assert any(item.path == "dt_ms" for item in comparison.configuration_differences)
    assert any(
        item.path == "neural.dt_ms" for item in comparison.configuration_differences
    )
    assert any("no interpolation" in item for item in comparison.limitations)


def test_source_mismatch_is_explicit_and_blocks_dense_comparison(
    tmp_path, circuit_contract
):
    original_config = _config(circuit_contract)
    original_result = ExperimentRunner(circuit_contract).run(original_config)
    changed_config = replace(
        original_config,
        candidate_version=2,
        source_endpoint="https://example.invalid/other-source",
        circuit_integrity=(
            ("connections.jsonl", "a" * 64),
            ("neurons.jsonl", "b" * 64),
        ),
    )
    changed_result = replace(
        original_result,
        config=changed_config,
        config_sha256=changed_config.sha256,
        candidate_version=2,
        circuit_integrity=changed_config.circuit_integrity,
    )
    artifact_a = export_experiment_artifact(original_result, tmp_path / "source-a")
    artifact_b = export_experiment_artifact(changed_result, tmp_path / "source-b")
    comparison = compare_experiment_artifacts(artifact_a, artifact_b)
    assert comparison.compatibility is ComparisonCompatibility.SUMMARY_ONLY_COMPARISON
    assert comparison.source_model_differences
    assert not comparison.telemetry.dense_trajectory_comparable
    assert all(item.trajectory_metrics is None for item in comparison.dnp01)


def test_telemetry_coverage_mismatch_uses_common_bodies_only(
    tmp_path, circuit_contract
):
    comparison = compare_experiment_artifacts(
        _artifact(tmp_path, circuit_contract, _config(circuit_contract), "minimal"),
        _artifact(
            tmp_path,
            circuit_contract,
            _config(circuit_contract, selected_visual_body_ids=(12032,)),
            "selected",
        ),
    )
    assert comparison.compatibility is ComparisonCompatibility.DIRECT_MODEL_COMPARISON
    assert comparison.telemetry.dense_trajectory_comparable
    assert comparison.telemetry.missing_body_ids_in_a == (12032,)
    assert comparison.telemetry.missing_body_ids_in_b == ()
    assert all(item.trajectory_metrics is not None for item in comparison.dnp01)
    assert any("coverage_mismatch" in item for item in comparison.limitations)


def test_directional_deltas_reverse_and_comparison_identity_changes(
    tmp_path, circuit_contract
):
    low = _artifact(
        tmp_path, circuit_contract, _config(circuit_contract, k_syn=0.01), "low"
    )
    high = _artifact(
        tmp_path, circuit_contract, _config(circuit_contract, k_syn=0.02), "high"
    )
    forward = compare_experiment_artifacts(low, high)
    reverse = compare_experiment_artifacts(high, low)
    assert forward.comparison_sha256 != reverse.comparison_sha256
    assert (
        forward.dnp01[0].peak_membrane_difference_mv
        == -reverse.dnp01[0].peak_membrane_difference_mv
    )
    assert (
        forward.dnp01[0].model_increment_sum_difference_mveq
        == -reverse.dnp01[0].model_increment_sum_difference_mveq
    )
    assert forward.configuration_differences[0].value_a == 0.01
    assert reverse.configuration_differences[0].value_a == 0.02


def test_comparison_does_not_mutate_loaded_artifacts(tmp_path, circuit_contract):
    config = _config(circuit_contract)
    artifact_a = _artifact(tmp_path, circuit_contract, config, "a")
    artifact_b = _artifact(tmp_path, circuit_contract, config, "b")
    from neurofly.experiment_artifacts import load_experiment_artifact

    loaded_a = load_experiment_artifact(artifact_a)
    loaded_b = load_experiment_artifact(artifact_b)
    before_a = loaded_a.result.to_dict()
    before_b = loaded_b.result.to_dict()
    compare_experiment_artifacts(loaded_a, loaded_b)
    assert loaded_a.result.to_dict() == before_a
    assert loaded_b.result.to_dict() == before_b


def test_invalid_comparison_policy_is_rejected():
    with pytest.raises(ComparisonConfigurationError):
        ExperimentComparisonConfig(time_base_policy="interpolate_v1")
