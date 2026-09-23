"""Phase 6C downstream evidence, dynamics, artifacts, and API boundaries."""

from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from neurofly.experiments import ExperimentConfig, ExperimentRunner
from neurofly.http_api import create_app
from neurofly.malecns.contract import load_circuit_contract
from neurofly.malecns.sensory import LoomingStimulus, VisualPoint
from neurofly.motor_pathway import (
    MOTOR_PATHWAY_EVIDENCE,
    MotorPathwayError,
    MotorPathwayEvidenceContract,
    MotorPathwayExperimentRunner,
    MotorPathwayRunConfig,
    TTMnIntegratorConfig,
    _integrate_ttmn,
    _map_motor_inputs,
)
from neurofly.motor_pathway_artifacts import (
    MOTOR_ARTIFACT_SCHEMA_VERSION,
    MotorArtifactIntegrityError,
    export_motor_pathway_artifact,
    load_motor_pathway_artifact,
    replay_motor_pathway_artifact,
)
from neurofly.sensory_encoder import LevelPEncoderConfig
from neurofly.simulation import LIFConfig, SpikeEvent
from neurofly.trajectory_characterization import PathwayCondition

DATA_ROOT = Path(__file__).resolve().parents[1] / "data" / "derived"


@pytest.fixture(scope="module")
def circuit_contract():
    return load_circuit_contract(DATA_ROOT / "malecns" / "looming_giant_fiber_v1")


def _config(circuit_contract, *, experiment_id="phase6c-test", pathway=None):
    return ExperimentConfig.from_contract(
        experiment_id=experiment_id,
        circuit_contract=circuit_contract,
        stimulus=LoomingStimulus(
            object_radius_m=0.01,
            approach_velocity_m_s=1.0,
            initial_distance_m=0.1,
            center=VisualPoint(0.0, 0.0),
        ),
        duration_ms=80.0,
        encoder_config=LevelPEncoderConfig(
            lc4_gain_mv_eq=20.0,
            lplc2_gain_mv_eq=20.0,
            omega_half_rad_per_s=1.0,
            theta_half_rad=0.4,
        ),
        lif_config=LIFConfig(k_syn_mv_per_contact=0.005, dt_ms=0.1),
        pathway_condition=PathwayCondition.COMBINED if pathway is None else pathway,
    )


def _event(body_id: int, step: int, *, node_index: int | None = None) -> SpikeEvent:
    index = {10001: 0, 10010: 1}[body_id] if node_index is None else node_index
    return SpikeEvent(
        time_ms=step * 0.1,
        step=step,
        body_id=body_id,
        node_index=index,
        neuron_type="DNp01",
    )


def test_downstream_evidence_contract_is_pinned_and_separate(circuit_contract):
    MOTOR_PATHWAY_EVIDENCE.validate_upstream_contract(circuit_contract)
    payload = MOTOR_PATHWAY_EVIDENCE.to_dict()
    assert MOTOR_PATHWAY_EVIDENCE.schema_version == "malecns_dnp01_ttmn_evidence_v1"
    assert payload["contract_id"] == "malecns_dnp01_to_ttmn_v1"
    assert payload["dataset"] == "male-cns:v1.0"
    assert payload["upstream_contract"]["candidate_identifier"] == (
        "looming_giant_fiber_v1"
    )
    assert payload["upstream_contract"]["sha256"] == (
        "3af274ecbf6ba4025b9e6ef0d038716446b0b9c03d9dd4f97c0151d280ebb8a5"
    )
    assert [
        (body["body_id"], body["type"], body["side"]) for body in payload["bodies"]
    ] == [
        (10001, "DNp01", "R"),
        (10010, "DNp01", "L"),
        (800146, "TTMn", "R"),
        (804642, "TTMn", "L"),
    ]
    assert [
        (body["body_id"], body.get("node_index"), body["status"])
        for body in payload["bodies"]
    ] == [
        (10001, 0, "Traced"),
        (10010, 1, "Traced"),
        (800146, None, "Traced"),
        (804642, None, "Traced"),
    ]
    assert [
        (edge["pre_body_id"], edge["post_body_id"], edge["structural_weight"])
        for edge in payload["chemical_edges"]
    ] == [(10001, 800146, 70), (10010, 804642, 20)]
    assert all(
        item["numeric_value"] is None
        and item["male_cns_pair_specific_strength"] is None
        for item in payload["electrical_coupling_evidence"]
    )
    assert all(item["combined_weight"] is None for item in payload["mixed_connections"])
    assert MOTOR_PATHWAY_EVIDENCE.sha256 == (
        "e65b8aae96115a0cc6ac875bdc3eeda69e11bfbd1ecb6495f75cdbe8f003dcd2"
    )

    with pytest.raises(MotorPathwayError, match="TTMn identities"):
        MotorPathwayEvidenceContract(ttmn_identities=({"body_id": 9},))
    bad_config = replace(_config(circuit_contract), candidate_identifier="other")
    with pytest.raises(MotorPathwayError, match="configuration provenance"):
        MOTOR_PATHWAY_EVIDENCE.validate_upstream_config(bad_config)


def test_event_identity_maps_only_to_the_pinned_ipsilateral_target():
    model = TTMnIntegratorConfig(tau_motor_ms=10.0, event_gain=0.25)
    events = (_event(10001, 2), _event(10010, 4))
    mapped = _map_motor_inputs(events, dt_ms=0.1, steps=8, model=model)
    assert [
        (item.source_body_id, item.target_body_id, item.step) for item in mapped
    ] == [
        (10001, 800146, 2),
        (10010, 804642, 4),
    ]
    assert events == (_event(10001, 2), _event(10010, 4))
    with pytest.raises(MotorPathwayError, match="node index"):
        _map_motor_inputs(
            (_event(10001, 2, node_index=1),), dt_ms=0.1, steps=8, model=model
        )


def test_integrator_is_dimensionless_deterministic_and_weight_independent():
    model = TTMnIntegratorConfig(tau_motor_ms=10.0, event_gain=0.25)
    times = tuple(step * 0.1 for step in range(8))
    mapped = _map_motor_inputs(
        (_event(10001, 2), _event(10010, 2), _event(10010, 4)),
        dt_ms=0.1,
        steps=len(times) - 1,
        model=model,
    )
    first = _integrate_ttmn(times_ms=times, dt_ms=0.1, inputs=mapped, model=model)
    second = _integrate_ttmn(times_ms=times, dt_ms=0.1, inputs=mapped, model=model)
    assert first == second
    right, left = first
    assert right.body_id == 800146 and right.side == "R"
    assert left.body_id == 804642 and left.side == "L"
    assert right.state[1] == 0.0
    assert right.state[2] == 0.25
    # Different source counts (70 vs 20) do not scale model event input.
    assert right.state[2] == left.state[2]
    assert left.state[4] == pytest.approx(0.25 + 0.25 * math.exp(-0.02))
    assert left.input_event_count == 2
    assert "structural_weight" not in model.to_dict()
    assert model.parameter_classification == "MODEL_ASSUMPTION"
    assert model.state_unit == "dimensionless"
    with pytest.raises(MotorPathwayError, match="assumption set"):
        TTMnIntegratorConfig(assumption_set_id="male-cns-fitted")


def test_runner_composes_same_run_dnp_events_and_silences_only_motor_input(
    circuit_contract,
):
    config = _config(circuit_contract)
    upstream = ExperimentRunner(circuit_contract).run(config)
    runner = MotorPathwayExperimentRunner(circuit_contract)
    reference = runner.run(config)
    assert reference.upstream_result.result_sha256 == upstream.result_sha256
    assert reference.source_dnp01_spike_events == tuple(
        event for event in upstream.spike_events if event.neuron_type == "DNp01"
    )
    assert [
        (event.source_body_id, event.target_body_id, event.step)
        for event in reference.delivered_motor_inputs
    ] == [
        (10010, 804642, 453),
        (10001, 800146, 693),
        (10010, 804642, 693),
    ]
    left = next(item for item in reference.ttmn_trajectories if item.body_id == 804642)
    assert left.state[453] == pytest.approx(0.25)
    assert left.state[693] == pytest.approx(0.27267948832235345)
    assert [item.input_event_count for item in reference.ttmn_trajectories] == [1, 2]
    assert len(reference.sensitivity) == 9
    assert all(
        "structural_weight" not in item.to_dict()
        for item in reference.delivered_motor_inputs
    )

    silenced = runner.run(config, MotorPathwayRunConfig(dnp01_to_ttmn_silenced=True))
    assert silenced.source_dnp01_spike_events == reference.source_dnp01_spike_events
    assert silenced.delivered_motor_inputs == ()
    assert [item.peak_state for item in silenced.ttmn_trajectories] == [0.0, 0.0]


@pytest.mark.parametrize(
    ("pathway", "expected_type", "expected_event_count"),
    [
        (PathwayCondition.LC4_ONLY, "LC4_ONLY", 1),
        (PathwayCondition.LPLC2_ONLY, "LPLC2_ONLY", 0),
        (PathwayCondition.COMBINED, "COMBINED", 3),
    ],
)
def test_sensory_conditions_reach_ttmn_only_through_dnp01(
    circuit_contract, pathway, expected_type, expected_event_count
):
    result = MotorPathwayExperimentRunner(circuit_contract).run(
        _config(circuit_contract, pathway=pathway)
    )
    assert result.upstream_result.config.pathway_condition.value == expected_type
    assert len(result.source_dnp01_spike_events) == expected_event_count
    assert len(result.delivered_motor_inputs) == len(result.source_dnp01_spike_events)
    assert all(
        item.source_body_id in (10001, 10010)
        and item.target_body_id in (800146, 804642)
        for item in result.delivered_motor_inputs
    )
    if not expected_event_count:
        assert all(item.peak_state == 0.0 for item in result.ttmn_trajectories)


def test_no_loom_far_field_control_follows_upstream_without_special_case(
    circuit_contract,
):
    config = _config(circuit_contract, experiment_id="phase6c-no-loom")
    config = replace(
        config,
        stimulus=replace(
            config.stimulus,
            approach_velocity_m_s=0.0,
            initial_distance_m=1_000_000.0,
        ),
    )
    result = MotorPathwayExperimentRunner(circuit_contract).run(config)
    assert max(result.upstream_result.lc4_drive_mv_eq) == 0.0
    assert max(result.upstream_result.lplc2_drive_mv_eq) == 0.0
    assert result.source_dnp01_spike_events == ()
    assert result.delivered_motor_inputs == ()
    assert [item.peak_state for item in result.ttmn_trajectories] == [0.0, 0.0]


def test_sensitivity_ranges_are_deterministic_and_causal(circuit_contract):
    result = MotorPathwayExperimentRunner(circuit_contract).run(
        _config(circuit_contract)
    )
    assert {(item.tau_motor_ms, item.event_gain) for item in result.sensitivity} == {
        (tau, gain) for tau in (5.0, 10.0, 20.0) for gain in (0.1, 0.25, 0.5)
    }
    assert all(item.delivered_event_count == 3 for item in result.sensitivity)
    for tau in (5.0, 10.0, 20.0):
        points = sorted(
            (item for item in result.sensitivity if item.tau_motor_ms == tau),
            key=lambda item: item.event_gain,
        )
        assert all(
            lower.peak_state_by_body_id[0][1] < upper.peak_state_by_body_id[0][1]
            for lower, upper in zip(points, points[1:], strict=False)
        )
    for gain in (0.1, 0.25, 0.5):
        tau_points = sorted(
            (item for item in result.sensitivity if item.event_gain == gain),
            key=lambda item: item.tau_motor_ms,
        )
        left_peaks = [dict(item.peak_state_by_body_id)[804642] for item in tau_points]
        assert left_peaks[0] < left_peaks[1] < left_peaks[2]
        assert [dict(item.peak_step_by_body_id)[804642] for item in tau_points] == [
            693,
            693,
            693,
        ]
    assert all(item.peak_state > 0.0 for item in result.ttmn_trajectories)


def test_motor_artifact_round_trip_replay_and_read_only_api(
    tmp_path, circuit_contract, monkeypatch
):
    from neurofly.motor_pathway_artifacts import (
        MotorPathwayArtifactStore,
    )

    result = MotorPathwayExperimentRunner(circuit_contract).run(
        _config(circuit_contract)
    )
    motor_root = tmp_path / "motor"
    artifact = export_motor_pathway_artifact(result, motor_root / "reference")
    loaded = load_motor_pathway_artifact(artifact.path)
    assert loaded.artifact_id == artifact.artifact_id
    assert (
        loaded.upstream_artifact.artifact_id == artifact.upstream_artifact.artifact_id
    )
    assert loaded.result.result_sha256 == result.result_sha256
    assert loaded.manifest["artifact_schema_version"] == MOTOR_ARTIFACT_SCHEMA_VERSION
    assert replay_motor_pathway_artifact(
        artifact.path, circuit_contract
    ).result_sha256 == (result.result_sha256)
    assert MotorPathwayArtifactStore(motor_root).get(
        artifact.artifact_id
    ).artifact_id == (artifact.artifact_id)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("GET must not run the experiment")

    monkeypatch.setattr(ExperimentRunner, "run", fail_run)
    base_root = tmp_path / "base-empty"
    base_root.mkdir()
    client = TestClient(
        create_app(base_root, motor_experiment_artifact_root=motor_root)
    )
    response = client.get(f"/api/v1/motor-experiments/{artifact.artifact_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["kind"] == "motor_neural_state"
    assert payload["artifact_schema_version"] == MOTOR_ARTIFACT_SCHEMA_VERSION
    assert payload["upstream_artifact_id"] == artifact.upstream_artifact.artifact_id
    assert payload["ttmn_model_state"][0]["body_id"] == 800146
    assert payload["ttmn_model_state"][1]["body_id"] == 804642
    assert (
        client.post(f"/api/v1/motor-experiments/{artifact.artifact_id}").status_code
        == 405
    )
    unconfigured = TestClient(create_app(base_root))
    missing_config = unconfigured.get(
        f"/api/v1/motor-experiments/{artifact.artifact_id}"
    )
    assert missing_config.status_code == 503
    assert missing_config.json()["code"] == "motor_artifact_store_unavailable"


def test_motor_artifact_corruption_is_rejected(tmp_path, circuit_contract):
    result = MotorPathwayExperimentRunner(circuit_contract).run(
        _config(circuit_contract)
    )
    artifact = export_motor_pathway_artifact(result, tmp_path / "motor-artifact")
    payload = artifact.path / "motor_neural_state.json"
    payload.write_text(
        payload.read_text(encoding="utf-8").replace(
            '"event_gain":0.25', '"event_gain":0.5'
        ),
        encoding="utf-8",
    )
    with pytest.raises(MotorArtifactIntegrityError, match="byte count|digest"):
        load_motor_pathway_artifact(artifact.path)
