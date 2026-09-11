"""Offline tests for the synthetic Phase 2C sensitivity benchmark."""

import json
from pathlib import Path

import numpy as np
import pytest

from neurofly.malecns.contract import load_circuit_contract
from neurofly.sensitivity import (
    PROVENANCE_CLASSIFICATION,
    SensitivityBenchmarkError,
    SensitivityPoint,
    SensitivityScenario,
    SensitivitySweep,
    build_synthetic_drive_schedule,
    run_sensitivity_point,
    run_sensitivity_sweep,
)
from neurofly.simulation import build_phase2b_graph


@pytest.fixture(scope="module")
def circuit_contract():
    snapshot_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "derived"
        / "malecns"
        / "looming_giant_fiber_v1"
    )
    return load_circuit_contract(snapshot_path)


@pytest.fixture(scope="module")
def simulation_graph(circuit_contract):
    return build_phase2b_graph(circuit_contract)


def _point(
    identifier: str,
    scenario: SensitivityScenario,
    *,
    k_syn: float = 0.01,
    lc4_drive: float = 0.0,
    lplc2_drive: float = 0.0,
    dt_ms: float = 0.1,
    total_duration_ms: float = 10.0,
) -> SensitivityPoint:
    return SensitivityPoint(
        identifier=identifier,
        scenario=scenario,
        k_syn_mv_per_contact=k_syn,
        lc4_drive_mveq=lc4_drive,
        lplc2_drive_mveq=lplc2_drive,
        dt_ms=dt_ms,
        total_duration_ms=total_duration_ms,
    )


def _response(summary, body_id):
    return next(
        response for response in summary.dnp01_responses if response.body_id == body_id
    )


def test_sweep_order_is_deterministic(simulation_graph) -> None:
    points = (
        _point(
            "zero",
            SensitivityScenario.ZERO,
        ),
        _point(
            "lplc2",
            SensitivityScenario.LPLC2_ONLY,
            lplc2_drive=150.0,
        ),
        _point(
            "combined",
            SensitivityScenario.COMBINED,
            lc4_drive=150.0,
            lplc2_drive=150.0,
        ),
        _point(
            "lc4",
            SensitivityScenario.LC4_ONLY,
            lc4_drive=150.0,
        ),
    )
    sweep = SensitivitySweep(points)
    expected = ("combined", "lc4", "lplc2", "zero")
    assert tuple(point.identifier for point in sweep.points) == expected
    result = run_sensitivity_sweep(simulation_graph, sweep)
    assert tuple(run.parameter_point.identifier for run in result.runs) == expected
    assert tuple(result.by_identifier) == expected


@pytest.mark.parametrize(
    ("scenario", "lc4_drive", "lplc2_drive", "driven_types"),
    [
        (SensitivityScenario.ZERO, 0.0, 0.0, set()),
        (SensitivityScenario.LC4_ONLY, 150.0, 0.0, {"LC4"}),
        (SensitivityScenario.LPLC2_ONLY, 0.0, 150.0, {"LPLC2"}),
        (SensitivityScenario.COMBINED, 150.0, 175.0, {"LC4", "LPLC2"}),
    ],
)
def test_synthetic_scenario_construction_targets_only_selected_visual_populations(
    simulation_graph,
    scenario,
    lc4_drive,
    lplc2_drive,
    driven_types,
) -> None:
    point = SensitivityPoint(
        identifier=scenario.value.lower(),
        scenario=scenario,
        k_syn_mv_per_contact=0.01,
        lc4_drive_mveq=lc4_drive,
        lplc2_drive_mveq=lplc2_drive,
        drive_onset_ms=0.2,
        drive_duration_ms=0.4,
        total_duration_ms=1.0,
    )
    matrix = build_synthetic_drive_schedule(simulation_graph, point).to_matrix(
        simulation_graph
    )
    for index, node in enumerate(simulation_graph.nodes):
        if node.type == "DNp01" or node.type not in driven_types:
            assert np.all(matrix[:, index] == 0.0)
        else:
            expected_amplitude = lc4_drive if node.type == "LC4" else lplc2_drive
            assert matrix[:, index].tolist() == [
                0.0,
                0.0,
                expected_amplitude,
                expected_amplitude,
                expected_amplitude,
                expected_amplitude,
                0.0,
                0.0,
                0.0,
                0.0,
            ]


def test_zero_fixture_preserves_rest_and_no_spike(simulation_graph) -> None:
    summary = run_sensitivity_point(
        simulation_graph,
        _point("zero", SensitivityScenario.ZERO, total_duration_ms=2.0),
    )
    assert summary.lc4_spike_count == 0
    assert summary.lplc2_spike_count == 0
    assert summary.delivered_event_count == 0
    assert summary.first_delivery_time_ms is None
    assert len(summary.dnp01_responses) == 2
    assert all(
        response.first_spike_time_ms is None for response in summary.dnp01_responses
    )
    assert all(response.spike_count == 0 for response in summary.dnp01_responses)
    assert all(
        response.peak_membrane_mv == -52.0 for response in summary.dnp01_responses
    )


def test_k_syn_sweep_scales_delivered_increment_monotonically(
    simulation_graph,
) -> None:
    sweep = SensitivitySweep(
        tuple(
            _point(
                f"lc4-k-{k_syn}",
                SensitivityScenario.LC4_ONLY,
                k_syn=k_syn,
                lc4_drive=150.0,
            )
            for k_syn in (0.005, 0.01, 0.02)
        )
    )
    result = run_sensitivity_sweep(simulation_graph, sweep)
    increments = [run.delivered_model_increment_sum_mveq for run in result.runs]
    assert increments == pytest.approx([31.81, 63.62, 127.24])
    assert increments[0] < increments[1] < increments[2]
    assert {run.delivered_event_count for run in result.runs} == {126}


def test_drive_amplitude_changes_visual_response_in_model_direction(
    simulation_graph,
) -> None:
    low = run_sensitivity_point(
        simulation_graph,
        _point(
            "lc4-low",
            SensitivityScenario.LC4_ONLY,
            k_syn=0.005,
            lc4_drive=100.0,
        ),
    )
    thresholded = run_sensitivity_point(
        simulation_graph,
        _point(
            "lc4-thresholded",
            SensitivityScenario.LC4_ONLY,
            k_syn=0.005,
            lc4_drive=150.0,
        ),
    )
    earlier = run_sensitivity_point(
        simulation_graph,
        _point(
            "lc4-earlier",
            SensitivityScenario.LC4_ONLY,
            k_syn=0.005,
            lc4_drive=300.0,
        ),
    )
    assert (low.lc4_spike_count, low.delivered_event_count) == (0, 0)
    assert (thresholded.lc4_spike_count, thresholded.delivered_event_count) == (
        126,
        126,
    )
    assert earlier.lc4_spike_count == thresholded.lc4_spike_count
    assert earlier.lc4_first_spike_time_ms < thresholded.lc4_first_spike_time_ms


def test_summary_preserves_both_dnp01_bodies_and_no_spike_case(
    simulation_graph,
) -> None:
    summary = run_sensitivity_point(
        simulation_graph,
        _point(
            "combined-subthreshold",
            SensitivityScenario.COMBINED,
            k_syn=0.005,
            lc4_drive=150.0,
            lplc2_drive=150.0,
        ),
    )
    assert [
        (response.body_id, response.side) for response in summary.dnp01_responses
    ] == [
        (10001, "R"),
        (10010, "L"),
    ]
    assert all(
        response.first_spike_time_ms is None for response in summary.dnp01_responses
    )
    assert (
        _response(summary, 10010).peak_membrane_mv
        > _response(summary, 10001).peak_membrane_mv
    )


def test_combined_subthreshold_response_matches_isolated_sum(
    simulation_graph,
) -> None:
    lc4 = run_sensitivity_point(
        simulation_graph,
        _point(
            "lc4-additivity",
            SensitivityScenario.LC4_ONLY,
            k_syn=0.005,
            lc4_drive=150.0,
        ),
    )
    lplc2 = run_sensitivity_point(
        simulation_graph,
        _point(
            "lplc2-additivity",
            SensitivityScenario.LPLC2_ONLY,
            k_syn=0.005,
            lplc2_drive=150.0,
        ),
    )
    combined = run_sensitivity_point(
        simulation_graph,
        _point(
            "combined-additivity",
            SensitivityScenario.COMBINED,
            k_syn=0.005,
            lc4_drive=150.0,
            lplc2_drive=150.0,
        ),
    )
    for body_id in (10001, 10010):
        lc4_deflection = _response(lc4, body_id).peak_membrane_mv + 52.0
        lplc2_deflection = _response(lplc2, body_id).peak_membrane_mv + 52.0
        combined_deflection = _response(combined, body_id).peak_membrane_mv + 52.0
        assert combined_deflection == pytest.approx(lc4_deflection + lplc2_deflection)


def test_identical_point_runs_are_exactly_reproducible_and_safe_to_serialize(
    simulation_graph,
) -> None:
    point = _point(
        "combined-replay",
        SensitivityScenario.COMBINED,
        lc4_drive=150.0,
        lplc2_drive=150.0,
    )
    first = run_sensitivity_point(simulation_graph, point)
    second = run_sensitivity_point(simulation_graph, point)
    assert first == second
    assert first.deterministic_replay_verified
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert PROVENANCE_CLASSIFICATION in serialized
    assert "NEUPRINT_APPLICATION_CREDENTIALS" not in serialized


def test_dnp01_first_spike_time_alone_is_parameter_degenerate(
    simulation_graph,
) -> None:
    higher_k_later_visual_spike = run_sensitivity_point(
        simulation_graph,
        _point(
            "combined-k-0.02-drive-150",
            SensitivityScenario.COMBINED,
            k_syn=0.02,
            lc4_drive=150.0,
            lplc2_drive=150.0,
        ),
    )
    lower_k_earlier_visual_spike = run_sensitivity_point(
        simulation_graph,
        _point(
            "combined-k-0.018-drive-180",
            SensitivityScenario.COMBINED,
            k_syn=0.018,
            lc4_drive=180.0,
            lplc2_drive=180.0,
        ),
    )
    assert [
        response.first_spike_time_ms
        for response in higher_k_later_visual_spike.dnp01_responses
    ] == [
        response.first_spike_time_ms
        for response in lower_k_earlier_visual_spike.dnp01_responses
    ]
    assert higher_k_later_visual_spike.lc4_first_spike_time_ms == 1.0
    assert lower_k_earlier_visual_spike.lc4_first_spike_time_ms == 0.8
    assert (
        higher_k_later_visual_spike.delivered_model_increment_sum_mveq
        != lower_k_earlier_visual_spike.delivered_model_increment_sum_mveq
    )


def test_network_dt_sensitivity_is_stable_and_deterministic(
    simulation_graph,
) -> None:
    points = tuple(
        _point(
            f"combined-dt-{dt_ms}",
            SensitivityScenario.COMBINED,
            lc4_drive=150.0,
            lplc2_drive=150.0,
            dt_ms=dt_ms,
        )
        for dt_ms in (0.05, 0.1, 0.2)
    )
    result = run_sensitivity_sweep(simulation_graph, SensitivitySweep(points))
    assert all(run.deterministic_replay_verified for run in result.runs)
    assert {(run.lc4_spike_count, run.lplc2_spike_count) for run in result.runs} == {
        (126, 185)
    }
    assert {run.delivered_event_count for run in result.runs} == {311}
    assert all(run.lc4_first_spike_time_ms == 1.0 for run in result.runs)
    assert all(run.lplc2_first_spike_time_ms == 1.0 for run in result.runs)
    assert all(run.first_delivery_time_ms == pytest.approx(2.8) for run in result.runs)

    for body_id in (10001, 10010):
        responses = [_response(run, body_id) for run in result.runs]
        first_spike_times = [response.first_spike_time_ms for response in responses]
        assert all(time is not None for time in first_spike_times)
        assert max(first_spike_times) - min(first_spike_times) <= 0.2
        peak_membranes = [response.peak_membrane_mv for response in responses]
        assert max(peak_membranes) - min(peak_membranes) <= 0.2


@pytest.mark.parametrize(
    "kwargs",
    [
        {"k_syn_mv_per_contact": 0.0},
        {"k_syn_mv_per_contact": float("nan")},
        {"drive_duration_ms": 0.0},
        {"drive_duration_ms": 10.1},
        {"drive_onset_ms": 0.05},
        {"lc4_drive_mveq": -1.0},
    ],
)
def test_malformed_parameter_points_fail(kwargs) -> None:
    values = {
        "identifier": "invalid",
        "scenario": SensitivityScenario.COMBINED,
        "k_syn_mv_per_contact": 0.01,
        "lc4_drive_mveq": 150.0,
        "lplc2_drive_mveq": 150.0,
    }
    values.update(kwargs)
    with pytest.raises(SensitivityBenchmarkError):
        SensitivityPoint(**values)


def test_unsupported_scenario_fails() -> None:
    with pytest.raises(SensitivityBenchmarkError, match="unsupported"):
        SensitivityPoint(
            identifier="invalid-scenario",
            scenario="LC4_ONLY",  # type: ignore[arg-type]
            k_syn_mv_per_contact=0.01,
            lc4_drive_mveq=150.0,
            lplc2_drive_mveq=0.0,
        )


def test_empty_and_duplicate_parameter_sweeps_fail() -> None:
    with pytest.raises(SensitivityBenchmarkError, match="empty"):
        SensitivitySweep(())
    point = _point(
        "duplicate",
        SensitivityScenario.LC4_ONLY,
        lc4_drive=150.0,
    )
    with pytest.raises(SensitivityBenchmarkError, match="unique"):
        SensitivitySweep((point, point))


def test_benchmark_does_not_mutate_biological_contract(
    circuit_contract, simulation_graph
) -> None:
    neurons_before = circuit_contract.neurons
    connections_before = circuit_contract.connections
    run_sensitivity_point(
        simulation_graph,
        _point(
            "immutable-contract",
            SensitivityScenario.LPLC2_ONLY,
            lplc2_drive=150.0,
        ),
    )
    assert circuit_contract.neurons == neurons_before
    assert circuit_contract.connections == connections_before
