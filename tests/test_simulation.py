"""Offline tests for the deterministic Phase 2B LIF execution boundary."""

import json
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from neurofly.malecns.models import CANDIDATE, MALECNS_DATASET, NEUPRINT_ENDPOINT
from neurofly.simulation import (
    ExternalDriveSchedule,
    LIFConfig,
    LIFSimulator,
    SimulationConfigurationError,
    SimulationGraphError,
    SimulationInputError,
    build_phase2b_graph,
)


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
def simulator(simulation_graph):
    return LIFSimulator(simulation_graph, LIFConfig(k_syn_mv_per_contact=0.01))


def _body(graph, neuron_type):
    return next(node.body_id for node in graph.nodes if node.type == neuron_type)


def _index(result, body_id):
    return result.body_ids.index(body_id)


def test_phase2b_graph_scope_is_exact(simulation_graph) -> None:
    assert simulation_graph.node_count == 313
    assert simulation_graph.edge_count == 311
    assert sum(edge.source_type == "LC4" for edge in simulation_graph.edges) == 126
    assert sum(edge.source_type == "LPLC2" for edge in simulation_graph.edges) == 185
    assert {edge.target_type for edge in simulation_graph.edges} == {"DNp01"}
    assert {edge.model_sign for edge in simulation_graph.edges} == {1}


def test_graph_scope_rejects_missing_active_edge(simulation_graph) -> None:
    with pytest.raises(SimulationGraphError, match="requires 311 edges"):
        LIFSimulator(
            replace(simulation_graph, edges=simulation_graph.edges[:-1]),
            LIFConfig(k_syn_mv_per_contact=0.01),
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("dt_ms", 0.0, "dt_ms"),
        ("tau_m_ms", -1.0, "tau_m_ms"),
        ("tau_s_ms", 0.0, "tau_s_ms"),
        ("refractory_ms", -0.1, "refractory_ms"),
        ("delay_ms", -0.1, "delay_ms"),
        ("k_syn_mv_per_contact", 0.0, "k_syn"),
        ("threshold_mv", -52.0, "threshold_mv"),
        ("rest_mv", float("nan"), "rest_mv"),
        ("delay_ms", 0.15, "integral"),
        ("refractory_ms", 2.21, "integral"),
    ],
)
def test_configuration_validation(field, value, message) -> None:
    values = {"k_syn_mv_per_contact": 0.01, field: value}
    with pytest.raises(SimulationConfigurationError, match=message):
        LIFConfig(**values)


def test_zero_input_stays_at_rest(simulator) -> None:
    result = simulator.run(steps=5)
    assert np.all(result.membrane_mv == -52.0)
    assert np.all(result.synaptic_mveq == 0.0)
    assert result.spikes == ()
    assert result.delivered_events == ()
    assert result.dnp01_first_spike_time_ms == {10001: None, 10010: None}
    assert len(result.neuron_sides) == len(result.body_ids)
    assert "NEUPRINT_APPLICATION_CREDENTIALS" not in json.dumps(
        result.to_summary_dict()
    )


def test_passive_membrane_decay_is_exact(simulator, simulation_graph) -> None:
    body_id = _body(simulation_graph, "LC4")
    result = simulator.run(steps=1, initial_v_mv={body_id: -46.0})
    expected = -52.0 + 6.0 * np.exp(-0.1 / 20.0)
    assert result.membrane_mv[1, _index(result, body_id)] == pytest.approx(expected)


def test_synaptic_state_decay_is_exact(simulator, simulation_graph) -> None:
    body_id = _body(simulation_graph, "DNp01")
    result = simulator.run(steps=1, initial_s_mveq={body_id: 10.0})
    expected = 10.0 * np.exp(-0.1 / 5.0)
    assert result.synaptic_mveq[1, _index(result, body_id)] == pytest.approx(expected)


def test_equal_membrane_and_synaptic_time_constants_use_limit(simulation_graph) -> None:
    body_id = _body(simulation_graph, "DNp01")
    config = LIFConfig(k_syn_mv_per_contact=0.01, tau_m_ms=5.0, tau_s_ms=5.0)
    result = LIFSimulator(simulation_graph, config).run(
        steps=1, initial_s_mveq={body_id: 10.0}
    )
    expected = -52.0 + 10.0 * (0.1 / 5.0) * np.exp(-0.1 / 5.0)
    assert result.membrane_mv[1, _index(result, body_id)] == pytest.approx(expected)


def test_threshold_reset_and_refractory_boundary(simulator, simulation_graph) -> None:
    body_id = _body(simulation_graph, "LC4")
    result = simulator.run(
        ExternalDriveSchedule.from_body_ids({body_id: [2_000.0] * 30})
    )
    body_spikes = [event for event in result.spikes if event.body_id == body_id]
    assert body_spikes[0].step == 1
    assert result.membrane_mv[1, _index(result, body_id)] == -52.0
    assert len(body_spikes) == 2
    assert body_spikes[1].step == 24
    assert body_spikes[1].step - body_spikes[0].step == 23


def test_delayed_event_arrives_on_exact_step(simulator, simulation_graph) -> None:
    source_id = _body(simulation_graph, "LC4")
    target_ids = {
        edge.target_body_id
        for edge in simulation_graph.edges
        if edge.source_body_id == source_id
    }
    result = simulator.run(
        ExternalDriveSchedule.from_body_ids({source_id: [2_000.0] + [0.0] * 40})
    )
    source_events = [
        event for event in result.delivered_events if event.source_body_id == source_id
    ]
    assert target_ids == {event.target_body_id for event in source_events}
    assert source_events
    assert all(event.delivery_step == 19 for event in source_events)
    assert all(event.delivery_time_ms == pytest.approx(1.9) for event in source_events)
    assert result.incoming_coupling_mveq[:19].sum() == 0.0
    assert result.incoming_coupling_mveq[19].sum() > 0.0


def test_event_during_refractory_is_retained_in_filtered_state(
    simulator, simulation_graph
) -> None:
    source_id = _body(simulation_graph, "LC4")
    target_id = next(
        edge.target_body_id
        for edge in simulation_graph.edges
        if edge.source_body_id == source_id
    )
    result = simulator.run(
        ExternalDriveSchedule.from_body_ids({source_id: [2_000.0] + [0.0] * 25}),
        initial_v_mv={target_id: -44.0},
    )
    assert any(
        event.source_body_id == source_id and event.target_body_id == target_id
        for event in result.delivered_events
    )
    target_index = _index(result, target_id)
    assert result.synaptic_mveq[20, target_index] > 0.0


def test_structural_ordering_is_preserved(simulation_graph) -> None:
    edge = simulation_graph.edges[0]
    low = replace(edge, structural_weight=10)
    high = replace(edge, structural_weight=20)
    assert high.event_increment(0.25) == pytest.approx(2 * low.event_increment(0.25))
    assert low.structural_weight == 10
    assert high.structural_weight == 20


def test_body_id_and_node_index_drive_targets_are_supported(
    simulator, simulation_graph
) -> None:
    lc4_id = _body(simulation_graph, "LC4")
    lplc2_index = next(
        index
        for index, node in enumerate(simulation_graph.nodes)
        if node.type == "LPLC2"
    )
    schedule = ExternalDriveSchedule.from_body_ids({lc4_id: [1.0, 2.0, 3.0]})
    result = simulator.run(schedule)
    assert result.external_drive_mveq[:, _index(result, lc4_id)].tolist() == [
        1.0,
        2.0,
        3.0,
    ]
    indexed = simulator.run(
        ExternalDriveSchedule.from_node_indices({lplc2_index: [4.0, 5.0]})
    )
    assert indexed.external_drive_mveq[:, lplc2_index].tolist() == [4.0, 5.0]


@pytest.mark.parametrize(
    "schedule",
    [
        ExternalDriveSchedule.from_body_ids({999_999: [1.0]}),
        ExternalDriveSchedule.from_body_ids({10010: [1.0]}),
    ],
)
def test_input_boundary_rejects_unknown_and_dnp01_drive(simulator, schedule) -> None:
    with pytest.raises(SimulationInputError):
        simulator.run(schedule)


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_input_boundary_rejects_nonfinite_drive(value) -> None:
    with pytest.raises(SimulationInputError, match="finite"):
        ExternalDriveSchedule.from_body_ids({20_000: [value]})


def test_input_boundary_rejects_malformed_shapes(simulator, simulation_graph) -> None:
    body_id = _body(simulation_graph, "LC4")
    with pytest.raises(SimulationInputError, match="shape"):
        simulator.run(np.zeros((2, 2, 1)))
    with pytest.raises(SimulationInputError, match="exactly 3 steps"):
        simulator.run(
            ExternalDriveSchedule.from_body_ids({body_id: [1.0, 2.0]}, steps=3)
        )
    with pytest.raises(SimulationInputError, match="one column"):
        simulator.run(np.zeros((2, 312)))
    with pytest.raises(SimulationInputError, match="Unknown node index"):
        simulator.run(ExternalDriveSchedule.from_node_indices({-1: [1.0]}))


def test_piecewise_constant_boundary_is_preserved(simulator, simulation_graph) -> None:
    body_id = _body(simulation_graph, "LC4")
    result = simulator.run(
        ExternalDriveSchedule.from_body_ids({body_id: [0.0, 5.0, 0.0]})
    )
    assert result.external_drive_mveq[:, _index(result, body_id)].tolist() == [
        0.0,
        5.0,
        0.0,
    ]


def test_deterministic_replay_is_exact(simulator, simulation_graph) -> None:
    body_id = _body(simulation_graph, "LPLC2")
    schedule = ExternalDriveSchedule.from_body_ids({body_id: [100.0] * 20})
    first = simulator.run(schedule)
    second = simulator.run(schedule)
    assert np.array_equal(first.times_ms, second.times_ms)
    assert np.array_equal(first.membrane_mv, second.membrane_mv)
    assert np.array_equal(first.synaptic_mveq, second.synaptic_mveq)
    assert first.spikes == second.spikes
    assert first.delivered_events == second.delivered_events
    assert first.to_summary_dict() == second.to_summary_dict()


def test_dt_convergence_for_exact_passive_decay(simulation_graph) -> None:
    body_id = _body(simulation_graph, "LC4")
    final_values = {}
    for dt_ms, steps in ((0.05, 40), (0.1, 20), (0.2, 10)):
        config = LIFConfig(k_syn_mv_per_contact=0.01, dt_ms=dt_ms)
        result = LIFSimulator(simulation_graph, config).run(
            steps=steps, initial_v_mv={body_id: -46.0}
        )
        final_values[dt_ms] = result.membrane_mv[-1, _index(result, body_id)]
    assert final_values[0.05] == pytest.approx(final_values[0.1], abs=1e-12)
    assert final_values[0.1] == pytest.approx(final_values[0.2], abs=1e-12)


def test_lc4_lplc2_and_combined_inputs_reach_dnp01(simulator, simulation_graph) -> None:
    lc4_id = _body(simulation_graph, "LC4")
    lplc2_id = _body(simulation_graph, "LPLC2")
    for source_id in (lc4_id, lplc2_id):
        result = simulator.run(
            ExternalDriveSchedule.from_body_ids({source_id: [2_000.0] + [0.0] * 30})
        )
        assert any(
            event.source_body_id == source_id for event in result.delivered_events
        )

    combined = simulator.run(
        ExternalDriveSchedule.from_body_ids(
            {lc4_id: [2_000.0] + [0.0] * 30, lplc2_id: [2_000.0] + [0.0] * 30}
        )
    )
    assert {event.source_body_id for event in combined.delivered_events} == {
        lc4_id,
        lplc2_id,
    }
    assert all(
        event.target_body_id in {10001, 10010} for event in combined.delivered_events
    )


def test_contract_view_is_not_mutated(simulation_graph, valid_snapshot) -> None:
    neurons_before = valid_snapshot.neurons
    connections_before = valid_snapshot.connections
    LIFSimulator(simulation_graph, LIFConfig(k_syn_mv_per_contact=0.01)).run(steps=2)
    assert valid_snapshot.neurons == neurons_before
    assert valid_snapshot.connections == connections_before
