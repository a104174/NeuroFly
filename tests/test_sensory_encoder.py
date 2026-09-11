"""Offline tests for the deterministic Level P E1 encoder."""

import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from neurofly.malecns.contract import load_circuit_contract
from neurofly.malecns.models import CANDIDATE, MALECNS_DATASET, NEUPRINT_ENDPOINT
from neurofly.malecns.sensory import LoomingSample, LoomingStimulus, VisualPoint
from neurofly.sensory_encoder import (
    ENCODER_ID,
    LevelPEncoderConfig,
    LevelPEncodingError,
    encode_level_p,
)
from neurofly.simulation import LIFConfig, LIFSimulator, build_phase2b_graph


def _circuit_contract(snapshot):
    return SimpleNamespace(
        candidate=CANDIDATE,
        provenance=SimpleNamespace(dataset=MALECNS_DATASET, endpoint=NEUPRINT_ENDPOINT),
        integrity=SimpleNamespace(sha256_by_file=()),
        neurons=snapshot.neurons,
        connections=snapshot.connections,
    )


@pytest.fixture
def simulation_graph(valid_snapshot):
    return build_phase2b_graph(_circuit_contract(valid_snapshot))


@pytest.fixture
def validated_simulation_graph():
    path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "derived"
        / "malecns"
        / "looming_giant_fiber_v1"
    )
    return build_phase2b_graph(load_circuit_contract(path))


def _sample(
    time_s: float,
    *,
    theta: float = 0.2,
    omega: float = 0.4,
    approaching: bool = True,
    collided: bool = False,
) -> LoomingSample:
    return LoomingSample(
        time_s=time_s,
        distance_m=1.0,
        time_to_collision_s=None,
        angular_size_rad=theta,
        angular_expansion_velocity_rad_s=omega,
        center=VisualPoint(azimuth_rad=0.25, elevation_rad=-0.1),
        approaching=approaching,
        collided=collided,
    )


def _config(
    *,
    lc4_gain: float = 2.0,
    lplc2_gain: float = 3.0,
    omega_half: float = 0.4,
    theta_half: float = 0.2,
) -> LevelPEncoderConfig:
    # SYNTHETIC_BENCHMARK_VALUE: numerical fixture only, never calibration.
    return LevelPEncoderConfig(
        lc4_gain_mv_eq=lc4_gain,
        lplc2_gain_mv_eq=lplc2_gain,
        omega_half_rad_per_s=omega_half,
        theta_half_rad=theta_half,
    )


def test_config_requires_explicit_finite_nonnegative_parameters() -> None:
    assert _config().encoder_id == ENCODER_ID
    for field, value in (
        ("lc4_gain_mv_eq", -1.0),
        ("lplc2_gain_mv_eq", math.inf),
        ("omega_half_rad_per_s", 0.0),
        ("theta_half_rad", math.nan),
    ):
        with pytest.raises(LevelPEncodingError, match=field):
            LevelPEncoderConfig(**{**_config().to_dict(), field: value})


def test_exact_e1_formula_and_zero_baseline(simulation_graph) -> None:
    config = _config()
    result = encode_level_p(
        samples=[_sample(0.0)], graph=simulation_graph, config=config, dt_ms=0.1
    )
    assert result.lc4_normalized == pytest.approx((0.5,))
    assert result.lplc2_normalized == pytest.approx((0.5,))
    assert result.lc4_drive_mv_eq == pytest.approx((1.0,))
    assert result.lplc2_drive_mv_eq == pytest.approx((1.5,))

    zero = encode_level_p(
        samples=[_sample(0.0, theta=0.0, omega=0.0, approaching=False)],
        graph=simulation_graph,
        config=config,
        dt_ms=0.1,
    )
    assert zero.lc4_normalized == (0.0,)
    assert zero.lplc2_normalized == (0.0,)
    assert zero.lc4_drive_mv_eq == (0.0,)
    assert zero.lplc2_drive_mv_eq == (0.0,)


def test_features_are_monotonic_bounded_and_large_finite_safe(simulation_graph) -> None:
    samples = [
        _sample(0.0, theta=0.1, omega=0.1),
        _sample(0.0001, theta=0.2, omega=0.2),
        _sample(0.0002, theta=1.0e308, omega=1.0e308),
    ]
    result = encode_level_p(
        samples=samples,
        graph=simulation_graph,
        config=_config(omega_half=0.1, theta_half=0.1),
        dt_ms=0.1,
    )
    assert all(0.0 <= value < 1.0 for value in result.lc4_normalized)
    assert all(0.0 <= value < 1.0 for value in result.lplc2_normalized)
    assert (
        result.lc4_normalized[0] < result.lc4_normalized[1] < result.lc4_normalized[2]
    )
    assert (
        result.lplc2_normalized[0]
        < result.lplc2_normalized[1]
        < result.lplc2_normalized[2]
    )
    assert all(math.isfinite(value) for value in result.lc4_drive_mv_eq)
    assert all(math.isfinite(value) for value in result.lplc2_drive_mv_eq)


@pytest.mark.parametrize(
    "sample",
    [
        _sample(0.0, omega=-0.4, approaching=False),
        _sample(0.0, omega=0.0, approaching=False),
    ],
)
def test_receding_and_static_samples_have_zero_drive(simulation_graph, sample) -> None:
    result = encode_level_p(
        samples=[sample], graph=simulation_graph, config=_config(), dt_ms=0.1
    )
    assert result.lc4_drive_mv_eq == (0.0,)
    assert result.lplc2_drive_mv_eq == (0.0,)
    assert np.all(result.schedule.to_matrix(simulation_graph) == 0.0)


def test_zero_gains_are_valid(simulation_graph) -> None:
    result = encode_level_p(
        samples=[_sample(0.0)],
        graph=simulation_graph,
        config=_config(lc4_gain=0.0, lplc2_gain=0.0),
        dt_ms=0.1,
    )
    assert result.lc4_drive_mv_eq == (0.0,)
    assert result.lplc2_drive_mv_eq == (0.0,)


def test_population_targets_are_complete_bilateral_and_exclude_dnp01(
    validated_simulation_graph,
) -> None:
    result = encode_level_p(
        samples=[_sample(0.0)],
        graph=validated_simulation_graph,
        config=_config(),
        dt_ms=0.1,
    )
    entries = dict(result.schedule.by_body_id)
    lc4_ids = [
        node.body_id for node in validated_simulation_graph.nodes if node.type == "LC4"
    ]
    lplc2_ids = [
        node.body_id
        for node in validated_simulation_graph.nodes
        if node.type == "LPLC2"
    ]
    dnp_ids = [
        node.body_id
        for node in validated_simulation_graph.nodes
        if node.type == "DNp01"
    ]
    assert set(entries) == set(lc4_ids + lplc2_ids)
    assert len(entries) == 311
    assert not set(entries) & set(dnp_ids)
    assert {entries[body_id] for body_id in lc4_ids} == {(1.0,)}
    assert {entries[body_id] for body_id in lplc2_ids} == {(1.5,)}
    visual_sides = {
        node.soma_side
        for node in validated_simulation_graph.nodes
        if node.type in {"LC4", "LPLC2"}
    }
    assert {"L", "R"} <= visual_sides


def test_sample_alignment_collision_and_invalid_samples_are_rejected(
    simulation_graph,
) -> None:
    config = _config()
    with pytest.raises(LevelPEncodingError, match="aligned"):
        encode_level_p(
            samples=[_sample(0.0), _sample(0.00011)],
            graph=simulation_graph,
            config=config,
            dt_ms=0.1,
        )
    with pytest.raises(LevelPEncodingError, match="strictly increasing"):
        encode_level_p(
            samples=[_sample(0.0), _sample(0.0)],
            graph=simulation_graph,
            config=config,
            dt_ms=0.1,
        )
    with pytest.raises(LevelPEncodingError, match="collision"):
        encode_level_p(
            samples=[_sample(0.0, collided=True)],
            graph=simulation_graph,
            config=config,
            dt_ms=0.1,
        )
    with pytest.raises(LevelPEncodingError, match="expansion velocity"):
        encode_level_p(
            samples=[
                LoomingSample(
                    time_s=0.0,
                    distance_m=1.0,
                    time_to_collision_s=None,
                    angular_size_rad=0.2,
                    angular_expansion_velocity_rad_s=None,
                    center=VisualPoint(0.0, 0.0),
                    approaching=True,
                    collided=False,
                )
            ],
            graph=simulation_graph,
            config=config,
            dt_ms=0.1,
        )


@pytest.mark.parametrize(
    "sample",
    [
        _sample(0.0, theta=math.nan),
        _sample(0.0, omega=math.inf),
    ],
)
def test_nonfinite_sample_geometry_is_rejected(simulation_graph, sample) -> None:
    with pytest.raises(LevelPEncodingError, match="finite"):
        encode_level_p(
            samples=[sample], graph=simulation_graph, config=_config(), dt_ms=0.1
        )


def test_deterministic_replay_metadata_and_schedule(simulation_graph) -> None:
    stimulus = LoomingStimulus(
        object_radius_m=0.5,
        approach_velocity_m_s=2.0,
        initial_distance_m=10.0,
        center=VisualPoint(0.25, -0.1),
    )
    samples = tuple(stimulus.sample(index * 0.0001) for index in range(4))
    config = _config()
    first = encode_level_p(
        samples=samples,
        graph=simulation_graph,
        config=config,
        dt_ms=0.1,
        stimulus_identity="synthetic_geometry_fixture_v1",
    )
    second = encode_level_p(
        samples=samples,
        graph=simulation_graph,
        config=config,
        dt_ms=0.1,
        stimulus_identity="synthetic_geometry_fixture_v1",
    )
    assert first.to_summary_dict() == second.to_summary_dict()
    assert first.schedule == second.schedule
    assert first.config_sha256 == config.sha256
    assert "NEUPRINT_APPLICATION_CREDENTIALS" not in json.dumps(first.to_summary_dict())


def test_encoding_does_not_mutate_samples_or_simulation_graph(simulation_graph) -> None:
    sample = _sample(0.0)
    graph_before = simulation_graph.to_dict()
    sample_before = sample.to_dict()
    encode_level_p(
        samples=[sample], graph=simulation_graph, config=_config(), dt_ms=0.1
    )
    assert simulation_graph.to_dict() == graph_before
    assert sample.to_dict() == sample_before


def test_encoder_runs_through_phase2b_without_stimulus_knowledge(
    validated_simulation_graph,
) -> None:
    stimulus = LoomingStimulus(
        object_radius_m=0.5,
        approach_velocity_m_s=2.0,
        initial_distance_m=10.0,
        center=VisualPoint(0.0, 0.0),
    )
    first = stimulus.sample(0.0)
    samples = tuple(stimulus.sample(index * 0.0001) for index in range(40))
    result = encode_level_p(
        samples=samples,
        graph=validated_simulation_graph,
        # SYNTHETIC_BENCHMARK_VALUE: end-to-end integration probe only.
        config=_config(
            lc4_gain=300.0,
            lplc2_gain=300.0,
            omega_half=first.angular_expansion_velocity_rad_s,
            theta_half=first.angular_size_rad,
        ),
        dt_ms=0.1,
        stimulus_identity="synthetic_end_to_end_fixture_v1",
    )
    simulator = LIFSimulator(
        validated_simulation_graph,
        # SYNTHETIC_BENCHMARK_VALUE: existing engine smoke configuration.
        LIFConfig(k_syn_mv_per_contact=0.01),
    )
    lc4_id = next(
        node.body_id for node in validated_simulation_graph.nodes if node.type == "LC4"
    )
    lplc2_id = next(
        node.body_id
        for node in validated_simulation_graph.nodes
        if node.type == "LPLC2"
    )
    dnp_ids = tuple(
        node.body_id
        for node in validated_simulation_graph.nodes
        if node.type == "DNp01"
    )
    simulation = simulator.run(
        result.schedule,
        record_body_ids=(lc4_id, lplc2_id, *dnp_ids),
    )
    replay = simulator.run(
        result.schedule,
        record_body_ids=(lc4_id, lplc2_id, *dnp_ids),
    )
    assert result.schedule.steps == 40
    assert simulation.times_ms[-1] == pytest.approx(4.0)
    assert np.any(result.lc4_drive_mv_eq)
    assert np.any(result.lplc2_drive_mv_eq)
    assert simulation.external_drive_mveq[0, 0] > 0.0
    assert simulation.external_drive_mveq[0, 1] > 0.0
    assert np.any(simulation.external_drive_mveq[:, 0] > 0.0)
    assert np.any(simulation.external_drive_mveq[:, 1] > 0.0)
    assert np.any(simulation.membrane_mv[1:, 0] != -52.0)
    assert np.any(simulation.membrane_mv[1:, 1] != -52.0)
    assert simulation.delivered_events
    assert all(event.target_body_id in dnp_ids for event in simulation.delivered_events)
    assert all(
        np.all(simulation.external_drive_mveq[:, index] == 0.0) for index in range(2, 4)
    )
    assert np.array_equal(simulation.membrane_mv, replay.membrane_mv)
    assert np.array_equal(simulation.synaptic_mveq, replay.synaptic_mveq)
    assert simulation.spikes == replay.spikes
    assert simulation.delivered_events == replay.delivered_events
