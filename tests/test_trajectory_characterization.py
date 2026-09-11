"""Offline tests for Phase 2F end-to-end trajectory characterization."""

import json
from pathlib import Path

import numpy as np
import pytest

from neurofly.malecns.contract import load_circuit_contract
from neurofly.malecns.sensory import LoomingStimulus, VisualPoint
from neurofly.sensory_encoder import LevelPEncoderConfig, encode_level_p
from neurofly.simulation import build_phase2b_graph
from neurofly.trajectory_characterization import (
    PROVENANCE_CLASSIFICATION,
    DNp01TrajectorySummary,
    LoomingTrajectoryScenario,
    OperatingRegime,
    PathwayCondition,
    TrajectoryBenchmarkPoint,
    TrajectoryBenchmarkSuite,
    TrajectoryCharacterizationError,
    VisualPopulationSummary,
    apply_pathway_condition,
    classify_operating_regime,
    run_trajectory_characterization,
    run_trajectory_suite,
    sample_looming_trajectory,
)


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
def simulation_graph(circuit_contract):
    return build_phase2b_graph(circuit_contract)


def _encoder_config(
    *,
    lc4_gain: float = 20.0,
    lplc2_gain: float = 20.0,
    omega_half: float = 1.0,
    theta_half: float = 0.4,
) -> LevelPEncoderConfig:
    # NEUROFLY_SYNTHETIC_BENCHMARK: never a biological/default calibration.
    return LevelPEncoderConfig(
        lc4_gain_mv_eq=lc4_gain,
        lplc2_gain_mv_eq=lplc2_gain,
        omega_half_rad_per_s=omega_half,
        theta_half_rad=theta_half,
    )


def _trajectory(
    identifier: str = "reference",
    *,
    velocity: float = 1.0,
    duration_ms: float = 80.0,
) -> LoomingTrajectoryScenario:
    return LoomingTrajectoryScenario(
        identifier=identifier,
        stimulus=LoomingStimulus(
            object_radius_m=0.01,
            initial_distance_m=0.1,
            approach_velocity_m_s=velocity,
            center=VisualPoint(azimuth_rad=0.0, elevation_rad=0.0),
        ),
        sample_duration_ms=duration_ms,
    )


def _point(
    identifier: str,
    *,
    trajectory: LoomingTrajectoryScenario | None = None,
    condition: PathwayCondition = PathwayCondition.COMBINED,
    config: LevelPEncoderConfig | None = None,
    k_syn: float = 0.005,
    dt_ms: float = 0.1,
) -> TrajectoryBenchmarkPoint:
    return TrajectoryBenchmarkPoint(
        identifier=identifier,
        trajectory=trajectory or _trajectory(),
        pathway_condition=condition,
        encoder_config=config or _encoder_config(),
        k_syn_mv_per_contact=k_syn,
        dt_ms=dt_ms,
    )


@pytest.fixture(scope="module")
def reference_result(simulation_graph):
    return run_trajectory_characterization(
        simulation_graph, _point("reference-combined")
    )


def _by_type(result, neuron_type):
    return next(
        item for item in result.visual_populations if item.neuron_type == neuron_type
    )


def _dnp(result, body_id):
    return next(item for item in result.dnp01_responses if item.body_id == body_id)


def test_sampling_uses_aligned_pre_collision_interval_boundaries() -> None:
    trajectory = _trajectory("fast", velocity=2.0, duration_ms=40.0)
    samples = sample_looming_trajectory(trajectory, dt_ms=0.2)
    assert len(samples) == 200
    assert samples[0].time_s == 0.0
    assert samples[-1].time_s == pytest.approx(0.0398)
    assert trajectory.stimulus.time_to_collision_s == pytest.approx(0.05)
    assert all(not sample.collided for sample in samples)
    assert samples[-1].angular_size_rad > samples[0].angular_size_rad
    assert (
        samples[-1].angular_expansion_velocity_rad_s
        > samples[0].angular_expansion_velocity_rad_s
    )


def test_invalid_duration_and_step_grid_are_rejected() -> None:
    with pytest.raises(TrajectoryCharacterizationError, match="past.*collision"):
        _trajectory("invalid", velocity=2.0, duration_ms=50.1)
    with pytest.raises(TrajectoryCharacterizationError, match="integral"):
        _point("misaligned", trajectory=_trajectory(duration_ms=80.05), dt_ms=0.1)
    with pytest.raises(TrajectoryCharacterizationError, match="greater than zero"):
        _point("bad-k", k_syn=0.0)


def test_suite_order_and_configuration_identity_are_deterministic() -> None:
    low = _point("low", config=_encoder_config(lc4_gain=10.0))
    high = _point("high", config=_encoder_config(lc4_gain=40.0))
    suite = TrajectoryBenchmarkSuite((low, high))
    assert tuple(point.identifier for point in suite.points) == ("low", "high")
    assert low.sha256 == _point("low", config=_encoder_config(lc4_gain=10.0)).sha256
    assert low.sha256 != high.sha256
    with pytest.raises(TrajectoryCharacterizationError, match="unique"):
        TrajectoryBenchmarkSuite((low, low))


@pytest.mark.parametrize(
    ("condition", "active_types"),
    [
        (PathwayCondition.ZERO, set()),
        (PathwayCondition.LC4_ONLY, {"LC4"}),
        (PathwayCondition.LPLC2_ONLY, {"LPLC2"}),
        (PathwayCondition.COMBINED, {"LC4", "LPLC2"}),
    ],
)
def test_pathway_masks_preserve_population_and_never_target_dnp01(
    simulation_graph, condition, active_types
) -> None:
    samples = sample_looming_trajectory(_trajectory(duration_ms=0.2), dt_ms=0.1)
    encoding = encode_level_p(
        samples=samples,
        graph=simulation_graph,
        config=_encoder_config(),
        dt_ms=0.1,
    )
    schedule = apply_pathway_condition(encoding, simulation_graph, condition)
    assert len(schedule.by_body_id) == 311
    matrix = schedule.to_matrix(simulation_graph)
    for index, node in enumerate(simulation_graph.nodes):
        if node.type in active_types:
            assert np.all(matrix[:, index] > 0.0)
        else:
            assert np.all(matrix[:, index] == 0.0)


@pytest.mark.parametrize(
    ("identifier", "velocity"),
    [("static", 0.0), ("receding", -1.0)],
)
def test_static_and_receding_controls_are_r0(simulation_graph, identifier, velocity):
    trajectory = _trajectory(identifier, velocity=velocity, duration_ms=10.0)
    result = run_trajectory_characterization(
        simulation_graph,
        _point(identifier, trajectory=trajectory, k_syn=0.005),
    )
    assert result.operating_regime is OperatingRegime.R0
    assert all(channel.peak_drive_mv_eq == 0.0 for channel in result.encoder_channels)
    assert all(
        population.total_spike_count == 0 for population in result.visual_populations
    )
    assert all(
        response.delivered_event_count == 0 for response in result.dnp01_responses
    )


def test_complete_path_preserves_visual_and_dnp01_separation(reference_result) -> None:
    lc4 = _by_type(reference_result, "LC4")
    lplc2 = _by_type(reference_result, "LPLC2")
    assert (lc4.body_count, lplc2.body_count) == (126, 185)
    assert (lc4.bodies_that_spike, lplc2.bodies_that_spike) == (126, 185)
    assert (lc4.total_spike_count, lplc2.total_spike_count) == (756, 370)
    assert reference_result.operating_regime is OperatingRegime.R4
    assert tuple(response.body_id for response in reference_result.dnp01_responses) == (
        10001,
        10010,
    )
    assert reference_result.deterministic_replay_verified


@pytest.mark.parametrize(
    ("visual_spikes", "dnp_spikes", "expected"),
    [
        (0, (0, 0), OperatingRegime.R0),
        (1, (0, 0), OperatingRegime.R1),
        (1, (1, 0), OperatingRegime.R2),
        (1, (1, 1), OperatingRegime.R3),
        (1, (1, 2), OperatingRegime.R4),
    ],
)
def test_operating_regime_classification_boundaries(
    visual_spikes, dnp_spikes, expected
) -> None:
    populations = (
        VisualPopulationSummary(
            neuron_type="LC4",
            body_count=126,
            bodies_that_spike=int(visual_spikes > 0),
            total_spike_count=visual_spikes,
            first_population_spike_time_ms=None,
            last_body_first_spike_time_ms=None,
            median_body_first_spike_time_ms=None,
            distinct_first_spike_times_ms=(),
        ),
    )
    responses = tuple(
        DNp01TrajectorySummary(
            body_id=body_id,
            side=side,
            incoming_active_edge_count=edge_count,
            incoming_structural_weight=weight,
            delivered_event_count=0,
            delivered_model_increment_sum_mveq=0.0,
            peak_filtered_synaptic_state_mveq=0.0,
            peak_membrane_mv=-52.0,
            first_spike_time_ms=None,
            total_spike_count=spike_count,
        )
        for body_id, side, edge_count, weight, spike_count in (
            (10001, "L", 146, 4800, dnp_spikes[0]),
            (10010, "R", 165, 6424, dnp_spikes[1]),
        )
    )
    assert classify_operating_regime(populations, responses) is expected


def test_real_structural_asymmetry_and_event_accounting_are_preserved(
    reference_result,
) -> None:
    weaker = _dnp(reference_result, 10001)
    stronger = _dnp(reference_result, 10010)
    assert (
        weaker.incoming_active_edge_count,
        weaker.incoming_structural_weight,
    ) == (146, 4800)
    assert (
        stronger.incoming_active_edge_count,
        stronger.incoming_structural_weight,
    ) == (165, 6424)
    assert (weaker.delivered_event_count, stronger.delivered_event_count) == (512, 614)
    assert weaker.delivered_model_increment_sum_mveq == pytest.approx(99.6)
    assert stronger.delivered_model_increment_sum_mveq == pytest.approx(139.88)
    assert stronger.first_spike_time_ms < weaker.first_spike_time_ms
    assert stronger.total_spike_count > weaker.total_spike_count


@pytest.mark.parametrize(
    ("condition", "expected_lc4", "expected_lplc2"),
    [
        (PathwayCondition.LC4_ONLY, True, False),
        (PathwayCondition.LPLC2_ONLY, False, True),
        (PathwayCondition.COMBINED, True, True),
    ],
)
def test_pathway_conditions_isolate_visual_spiking(
    simulation_graph, condition, expected_lc4, expected_lplc2
) -> None:
    result = run_trajectory_characterization(
        simulation_graph, _point(condition.value.lower(), condition=condition)
    )
    assert (_by_type(result, "LC4").total_spike_count > 0) is expected_lc4
    assert (_by_type(result, "LPLC2").total_spike_count > 0) is expected_lplc2
    channel_by_type = {
        channel.neuron_type: channel for channel in result.encoder_channels
    }
    assert (channel_by_type["LC4"].peak_drive_mv_eq > 0) is expected_lc4
    assert (channel_by_type["LPLC2"].peak_drive_mv_eq > 0) is expected_lplc2


def test_parameter_variation_changes_identity_without_biological_defaults(
    simulation_graph,
) -> None:
    points = (
        _point("gain-low", config=_encoder_config(lc4_gain=10.0)),
        _point("gain-high", config=_encoder_config(lc4_gain=40.0)),
    )
    result = run_trajectory_suite(simulation_graph, TrajectoryBenchmarkSuite(points))
    low = result.by_identifier["gain-low"]
    high = result.by_identifier["gain-high"]
    assert low.configuration_sha256 != high.configuration_sha256
    assert (
        _by_type(low, "LC4").first_population_spike_time_ms
        > _by_type(high, "LC4").first_population_spike_time_ms
    )
    assert {
        run.benchmark_point.to_dict()["provenance_classification"]
        for run in result.runs
    } == {PROVENANCE_CLASSIFICATION}


def test_replay_hash_and_contract_are_immutable(
    simulation_graph, circuit_contract, reference_result
) -> None:
    graph_nodes = simulation_graph.nodes
    graph_edges = simulation_graph.edges
    contract_neurons = circuit_contract.neurons
    contract_connections = circuit_contract.connections
    replay = run_trajectory_characterization(
        simulation_graph, _point("reference-combined")
    )
    assert replay.to_dict() == reference_result.to_dict()
    assert replay.result_sha256 == reference_result.result_sha256
    assert simulation_graph.nodes == graph_nodes
    assert simulation_graph.edges == graph_edges
    assert circuit_contract.neurons == contract_neurons
    assert circuit_contract.connections == contract_connections
    serialized = json.dumps(replay.to_dict(), sort_keys=True)
    assert "credential" not in serialized.lower()


def test_dt_characterization_preserves_regime_counts_and_bounded_timing(
    simulation_graph,
) -> None:
    results = [
        run_trajectory_characterization(
            simulation_graph, _point(f"dt-{dt_ms}", dt_ms=dt_ms)
        )
        for dt_ms in (0.05, 0.1, 0.2)
    ]
    assert {result.operating_regime for result in results} == {OperatingRegime.R4}
    assert {
        tuple(population.total_spike_count for population in result.visual_populations)
        for result in results
    } == {(756, 370)}
    assert {
        tuple(response.delivered_event_count for response in result.dnp01_responses)
        for result in results
    } == {(512, 614)}
    for body_id in (10001, 10010):
        first_spikes = [_dnp(result, body_id).first_spike_time_ms for result in results]
        assert max(first_spikes) - min(first_spikes) <= 0.2 + 1e-12
    peak_10001 = [_dnp(result, 10001).peak_membrane_mv for result in results]
    assert max(peak_10001) - min(peak_10001) < 0.06
    assert all(result.deterministic_replay_verified for result in results)
