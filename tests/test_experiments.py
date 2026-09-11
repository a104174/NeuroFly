"""Offline tests for the Phase 3A reproducible experiment-run boundary."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from neurofly.experiments import (
    ExperimentConfig,
    ExperimentConfigurationError,
    ExperimentRunner,
    TelemetrySpec,
    verify_replay,
)
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


@pytest.fixture(scope="module")
def experiment_runner(circuit_contract):
    return ExperimentRunner(circuit_contract)


def _config(circuit_contract, *, selected_visual_body_ids=()):
    # NEUROFLY_SYNTHETIC_BENCHMARK: software fixture, not biological calibration.
    encoder = LevelPEncoderConfig(
        lc4_gain_mv_eq=20.0,
        lplc2_gain_mv_eq=20.0,
        omega_half_rad_per_s=1.0,
        theta_half_rad=0.4,
    )
    lif = LIFConfig(k_syn_mv_per_contact=0.01)
    stimulus = LoomingStimulus(
        object_radius_m=0.01,
        initial_distance_m=0.1,
        approach_velocity_m_s=1.0,
        center=VisualPoint(azimuth_rad=0.0, elevation_rad=0.0),
    )
    return ExperimentConfig.from_contract(
        experiment_id="phase3a-test",
        circuit_contract=circuit_contract,
        stimulus=stimulus,
        duration_ms=20.0,
        encoder_config=encoder,
        lif_config=lif,
        telemetry=TelemetrySpec.validation_profile(
            selected_visual_body_ids=selected_visual_body_ids
        ),
    )


def test_config_has_explicit_free_parameters_and_deterministic_identity(
    circuit_contract,
):
    config = _config(circuit_contract)
    assert config.encoder_config.lc4_gain_mv_eq == 20.0
    assert config.encoder_config.lplc2_gain_mv_eq == 20.0
    assert config.encoder_config.omega_half_rad_per_s == 1.0
    assert config.encoder_config.theta_half_rad == 0.4
    assert config.lif_config.k_syn_mv_per_contact == 0.01
    assert config.sha256 == config.sha256
    changed = replace(
        config,
        lif_config=replace(config.lif_config, k_syn_mv_per_contact=0.02),
    )
    assert changed.sha256 != config.sha256


def test_invalid_dt_and_telemetry_targets_are_rejected(circuit_contract):
    config = _config(circuit_contract)
    with pytest.raises(ExperimentConfigurationError, match="match LIFConfig"):
        replace(config, dt_ms=0.2)
    runner = ExperimentRunner(circuit_contract)
    invalid = _config(circuit_contract, selected_visual_body_ids=(10001,))
    with pytest.raises(ExperimentConfigurationError, match="non-visual"):
        runner.run(invalid)


def test_complete_production_pipeline_preserves_graph_and_dnp01(
    circuit_contract, experiment_runner
):
    config = _config(circuit_contract, selected_visual_body_ids=(12032,))
    result = experiment_runner.run(config)
    assert experiment_runner.graph.node_count == 313
    assert experiment_runner.graph.edge_count == 311
    assert result.config_sha256 == config.sha256
    assert result.validation_status == "NOT_EVALUATED"
    assert [item.body_id for item in result.selected_body_telemetry] == [
        10001,
        10010,
        12032,
    ]
    assert [item.body_id for item in result.selected_body_telemetry[:2]] == [
        10001,
        10010,
    ]
    assert len(result.population_spike_summaries) == 2
    assert len(result.delivered_events) > 0
    dnp_indices = [
        index
        for index, item in enumerate(result.selected_body_telemetry)
        if item.neuron_type == "DNp01"
    ]
    for index in dnp_indices:
        assert np.all(
            np.asarray(result.selected_body_telemetry[index].external_drive_mveq) == 0.0
        )
    assert len(result.delivered_event_summaries) == 2


def test_exact_replay_and_config_change_identity(circuit_contract, experiment_runner):
    config = _config(circuit_contract)
    first = experiment_runner.run(config)
    second = experiment_runner.run(config)
    assert verify_replay(first, second)
    assert first.result_sha256 == second.result_sha256
    changed = replace(
        config,
        stimulus=replace(config.stimulus, approach_velocity_m_s=0.8),
    )
    assert changed.sha256 != config.sha256
    changed_result = experiment_runner.run(changed)
    assert changed_result.config_sha256 != first.config_sha256


def test_zero_pathway_is_a_real_zero_drive_experiment(
    circuit_contract, experiment_runner
):
    config = replace(_config(circuit_contract), pathway_condition=PathwayCondition.ZERO)
    result = experiment_runner.run(config)
    assert all(value == 0.0 for value in result.lc4_drive_mv_eq)
    assert all(value == 0.0 for value in result.lplc2_drive_mv_eq)
    assert all(
        summary.total_spike_count == 0 for summary in result.population_spike_summaries
    )
    assert all(time_ms is None for _, time_ms in result.dnp01_first_spike_time_ms)


def test_manifest_is_small_deterministic_and_excludes_machine_metadata(
    circuit_contract, experiment_runner, tmp_path
):
    result = experiment_runner.run(_config(circuit_contract))
    first = result.to_manifest_dict()
    second = result.to_manifest_dict()
    assert first == second
    assert "executed_at_utc" not in first
    destination = result.write_manifest(tmp_path / "manifest.json")
    loaded = json.loads(destination.read_text(encoding="utf-8"))
    assert loaded["config_sha256"] == result.config_sha256
    assert loaded["validation_status"] == "NOT_EVALUATED"
    assert "NEUPRINT_APPLICATION_CREDENTIALS" not in destination.read_text(
        encoding="utf-8"
    )


def test_contract_is_not_mutated_by_run(circuit_contract, experiment_runner):
    neurons = circuit_contract.neurons
    connections = circuit_contract.connections
    graph_nodes = experiment_runner.graph.nodes
    experiment_runner.run(_config(circuit_contract))
    assert circuit_contract.neurons == neurons
    assert circuit_contract.connections == connections
    assert experiment_runner.graph.nodes == graph_nodes
