"""Phase 8B synthetic-event provenance and TTMn interface tests."""

from __future__ import annotations

import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest

import neurofly.synthetic_motor_interface_artifacts as artifact_module
from neurofly.malecns.contract import load_circuit_contract
from neurofly.motor_pathway import (
    MOTOR_PATHWAY_EVIDENCE,
    TTMnIntegratorConfig,
    _integrate_ttmn,
    _map_motor_inputs,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.sensory_population_execution_artifacts import load_execution_artifact
from neurofly.synthetic_motor_interface import (
    FIXTURE_IDS,
    SYNTHETIC_SOURCE_KIND,
    SyntheticDNp01Event,
    SyntheticDNp01FixtureConfig,
    SyntheticMotorInterfaceError,
    build_fixture_configuration,
    build_reference_fixture_battery,
    execute_reference_battery,
    replay_synthetic_fixture_configuration,
    validate_and_replay_payload,
)
from neurofly.synthetic_motor_interface_artifacts import (
    SyntheticMotorArtifactError,
    export_synthetic_motor_artifact,
    generate_synthetic_motor_artifact,
    load_synthetic_motor_artifact,
    replay_synthetic_motor_artifact,
)

DATA_ROOT = Path(__file__).resolve().parents[1] / "data" / "derived"


@pytest.fixture(scope="module")
def circuit_contract():
    return load_circuit_contract(DATA_ROOT / "malecns" / "looming_giant_fiber_v1")


def _event(
    body_id: int = 10001,
    *,
    step: int = 2,
    time_ms: float | None = None,
    side: str | None = None,
    node_index: int | None = None,
    neuron_type: str = "DNp01",
    source_kind: str = SYNTHETIC_SOURCE_KIND,
) -> SyntheticDNp01Event:
    identity = {10001: ("R", 0), 10010: ("L", 1)}.get(body_id, ("R", 0))
    return SyntheticDNp01Event(
        source_body_id=body_id,
        source_side=identity[0] if side is None else side,
        source_node_index=identity[1] if node_index is None else node_index,
        step=step,
        time_ms=step * 0.1 if time_ms is None else time_ms,
        neuron_type=neuron_type,
        source_kind=source_kind,
    )


def _fixture_result(result, fixture_id):
    return next(item for item in result["fixtures"] if item["fixture_id"] == fixture_id)


def _state(fixture, body_id):
    return next(
        item for item in fixture["ttmn_model_state"] if item["body_id"] == body_id
    )


def test_fixture_battery_has_explicit_synthetic_provenance_and_six_conditions(
    circuit_contract,
):
    configs = build_reference_fixture_battery()
    assert tuple(item.fixture_id for item in configs) == FIXTURE_IDS
    assert len(configs) == 6
    assert all(item.source_kind == SYNTHETIC_SOURCE_KIND for item in configs)
    assert all(item.sensory_source_artifact_id is None for item in configs)
    assert all(
        event.source_kind == SYNTHETIC_SOURCE_KIND
        for item in configs
        for event in item.events
    )
    config, result = execute_reference_battery(circuit_contract)
    assert config["source_kind"] == "SYNTHETIC_MOTOR_INTERFACE_TEST"
    assert config["sensory_source_artifact_id"] is None
    assert (
        config["statement"] == "No sensory experiment generated these synthetic events."
    )
    assert result["provenance_semantics"] == "SYNTHETIC_MOTOR_INTERFACE_TEST_ONLY"
    assert result["sensory_source_artifact_id"] is None
    assert result["scientific_boundary"]["phase7o_event_source"] is False
    assert config["transmission_delay"]["modeled_additional_delay_ms"] == 0.0
    assert [item["fixture_id"] for item in result["fixtures"]] == list(FIXTURE_IDS)
    assert all(
        event["source_kind"] == SYNTHETIC_SOURCE_KIND
        for fixture in result["fixtures"]
        for event in fixture["source_events"]
    )
    assert all(
        fixture["synthetic_run_id"].startswith(
            f"synthetic_motor_interface_run_v1:{fixture['fixture_id']}:"
        )
        for fixture in result["fixtures"]
    )
    assert all(
        "phase7o" not in fixture["synthetic_run_id"].lower()
        for fixture in result["fixtures"]
    )


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"body_id": 12345}, "unknown DNp01"),
        ({"side": "L"}, "side does not match"),
        ({"node_index": 1}, "node index does not match"),
        ({"neuron_type": "LC4"}, "source type must be DNp01"),
        ({"source_kind": "SIMULATED_FROM_SENSORY_EXPERIMENT"}, "source kind"),
    ],
)
def test_fixture_event_rejects_identity_or_provenance_mismatch(kwargs, message):
    with pytest.raises(SyntheticMotorInterfaceError, match=message):
        _event(**kwargs)


def test_fixture_grid_requires_positive_integer_steps_and_exact_times():
    with pytest.raises(SyntheticMotorInterfaceError, match="step must be positive"):
        _event(step=0)
    with pytest.raises(SyntheticMotorInterfaceError, match="exactly equal"):
        SyntheticDNp01FixtureConfig(
            fixture_id="RIGHT_SINGLE_EVENT",
            events=(_event(step=2, time_ms=0.2000000000001),),
        )
    with pytest.raises(SyntheticMotorInterfaceError, match="outside"):
        SyntheticDNp01FixtureConfig(
            fixture_id="RIGHT_SINGLE_EVENT",
            events=(_event(step=81),),
        )
    with pytest.raises(SyntheticMotorInterfaceError, match="deterministic"):
        SyntheticDNp01FixtureConfig(
            fixture_id="BILATERAL_SIMULTANEOUS_EVENT",
            events=(_event(10010), _event(10001)),
        )
    with pytest.raises(SyntheticMotorInterfaceError, match="duplicate events"):
        SyntheticDNp01FixtureConfig(
            fixture_id="RIGHT_REPEATED_EVENTS",
            events=(_event(step=2), _event(step=2)),
        )


def test_zero_single_bilateral_and_repeated_event_dynamics(circuit_contract):
    _, result = execute_reference_battery(circuit_contract)
    decay = math.exp(-0.1 / 10.0)
    event_step = 10
    intervals_after_single = 80 - event_step

    zero = _fixture_result(result, "ZERO_EVENT_CONTROL")
    assert all(set(item["state"]) == {0.0} for item in zero["ttmn_model_state"])
    assert all(item["input_event_count"] == 0 for item in zero["ttmn_model_state"])

    right = _fixture_result(result, "RIGHT_SINGLE_EVENT")
    right_state = _state(right, 800146)
    untouched_left = _state(right, 804642)
    assert right_state["input_event_count"] == 1
    assert right_state["state"][event_step] == pytest.approx(0.25, abs=0.0)
    assert right_state["peak_step"] == event_step
    assert right_state["state"][-1] == pytest.approx(
        0.25 * decay**intervals_after_single, rel=1e-14
    )
    assert set(untouched_left["state"]) == {0.0}
    assert untouched_left["input_event_count"] == 0

    left = _fixture_result(result, "LEFT_SINGLE_EVENT")
    assert _state(left, 800146)["input_event_count"] == 0
    assert _state(left, 804642)["state"][event_step] == pytest.approx(0.25, abs=0.0)

    bilateral = _fixture_result(result, "BILATERAL_SIMULTANEOUS_EVENT")
    assert _state(bilateral, 800146)["state"] == _state(bilateral, 804642)["state"]
    assert _state(bilateral, 800146)["input_event_count"] == 1
    assert _state(bilateral, 804642)["input_event_count"] == 1

    repeated = _fixture_result(result, "RIGHT_REPEATED_EVENTS")
    repeated_state = _state(repeated, 800146)
    expected_second = 0.25 + 0.25 * decay**20
    assert repeated_state["input_event_count"] == 2
    assert repeated_state["state"][30] == pytest.approx(expected_second, rel=1e-14)
    assert repeated_state["peak_step"] == 30
    assert repeated_state["state"][-1] == pytest.approx(
        expected_second * decay**50, rel=1e-14
    )
    assert set(_state(repeated, 804642)["state"]) == {0.0}

    repeated_left = _fixture_result(result, "LEFT_REPEATED_EVENTS")
    assert _state(repeated_left, 804642)["state"] == repeated_state["state"]
    assert set(_state(repeated_left, 800146)["state"]) == {0.0}


def test_routes_are_exact_and_structural_count_is_not_numeric(circuit_contract):
    MOTOR_PATHWAY_EVIDENCE.validate_upstream_contract(circuit_contract)
    assert MOTOR_PATHWAY_EVIDENCE.target_by_source == {
        10001: 800146,
        10010: 804642,
    }
    assert [
        edge["structural_weight"] for edge in MOTOR_PATHWAY_EVIDENCE.chemical_edges
    ] == [
        70,
        20,
    ]
    source_events = (_event(10001).to_spike_event(), _event(10010).to_spike_event())
    model = TTMnIntegratorConfig()
    baseline_inputs = _map_motor_inputs(source_events, dt_ms=0.1, steps=80, model=model)
    baseline = _integrate_ttmn(
        times_ms=tuple(step * 0.1 for step in range(81)),
        dt_ms=0.1,
        inputs=baseline_inputs,
        model=model,
    )

    # The numerical Phase 6C primitives consume identity routes, not edge counts.
    altered_metadata = SimpleNamespace(
        dnp01_identities=MOTOR_PATHWAY_EVIDENCE.dnp01_identities,
        ttmn_identities=MOTOR_PATHWAY_EVIDENCE.ttmn_identities,
        target_by_source=MOTOR_PATHWAY_EVIDENCE.target_by_source,
        chemical_edges=tuple(
            {**edge, "structural_weight": edge["structural_weight"] * 1000}
            for edge in MOTOR_PATHWAY_EVIDENCE.chemical_edges
        ),
    )
    altered_inputs = _map_motor_inputs(
        source_events,
        dt_ms=0.1,
        steps=80,
        model=model,
        evidence_contract=altered_metadata,
    )
    altered = _integrate_ttmn(
        times_ms=tuple(step * 0.1 for step in range(81)),
        dt_ms=0.1,
        inputs=altered_inputs,
        model=model,
        evidence_contract=altered_metadata,
    )
    assert altered_inputs == baseline_inputs
    assert altered == baseline


def test_source_configuration_is_pinned_and_mismatch_fails_closed(circuit_contract):
    config = build_fixture_configuration(circuit_contract)
    replay_synthetic_fixture_configuration(config, circuit_contract)
    altered = json.loads(json.dumps(config))
    altered["source_circuit_contract_identity"]["source_hashes"][0][1] = "0" * 64
    with pytest.raises(SyntheticMotorInterfaceError, match="source CircuitContract"):
        replay_synthetic_fixture_configuration(altered, circuit_contract)
    with pytest.raises(SyntheticMotorInterfaceError, match="config identity"):
        validate_and_replay_payload(
            altered, execute_reference_battery(circuit_contract)[1]
        )


def test_content_addressed_artifact_replays_and_rejects_tampering(
    circuit_contract, tmp_path
):
    config, result = execute_reference_battery(circuit_contract)
    artifact_id = __import__(
        "neurofly.synthetic_motor_interface_artifacts",
        fromlist=["_artifact_id"],
    )._artifact_id(config["config_sha256"], result["result_sha256"])
    artifact_path = tmp_path / artifact_id
    exported = export_synthetic_motor_artifact(config, result, artifact_path)
    assert exported.artifact_id == artifact_id
    assert load_synthetic_motor_artifact(artifact_path).summary() == exported.summary()
    assert (
        replay_synthetic_motor_artifact(
            artifact_path, source_root=DEFAULT_SOURCE_ROOT
        ).artifact_id
        == artifact_id
    )

    result_path = artifact_path / "fixture_result.json"
    original = result_path.read_bytes()
    result_path.write_bytes(original + b" ")
    with pytest.raises(SyntheticMotorArtifactError, match="canonical JSON"):
        load_synthetic_motor_artifact(artifact_path)


def test_artifact_generation_rejects_existing_destination(circuit_contract, tmp_path):
    config, result = execute_reference_battery(circuit_contract)
    destination = tmp_path / "existing"
    destination.mkdir()
    with pytest.raises(SyntheticMotorArtifactError, match="already exists"):
        export_synthetic_motor_artifact(config, result, destination)


def test_generate_is_deterministic_and_replays_existing_artifact(tmp_path):
    first = generate_synthetic_motor_artifact(
        source_root=DEFAULT_SOURCE_ROOT,
        output_root=tmp_path,
    )
    second = generate_synthetic_motor_artifact(
        source_root=DEFAULT_SOURCE_ROOT,
        output_root=tmp_path,
    )
    assert first.artifact_id == second.artifact_id
    assert first.path == second.path


def test_full_replay_rejects_wrong_source_contract(
    monkeypatch, circuit_contract, tmp_path
):
    config, result = execute_reference_battery(circuit_contract)
    artifact_id = artifact_module._artifact_id(
        config["config_sha256"], result["result_sha256"]
    )
    path = tmp_path / artifact_id
    export_synthetic_motor_artifact(config, result, path)
    monkeypatch.setattr(
        artifact_module,
        "load_circuit_contract",
        lambda _: SimpleNamespace(
            candidate=SimpleNamespace(identifier="wrong", version=1),
            provenance=SimpleNamespace(dataset="male-cns:v1.0"),
            integrity=SimpleNamespace(sha256_by_file=()),
        ),
    )
    with pytest.raises(
        SyntheticMotorArtifactError, match="full synthetic artifact replay"
    ):
        replay_synthetic_motor_artifact(path, source_root=tmp_path)


def test_phase6c_same_run_result_invariant_remains_unchanged():
    """The synthetic path never makes a fake ExperimentResult parent."""

    from neurofly.motor_pathway import MotorPathwayExperimentResult

    assert "upstream_result" in MotorPathwayExperimentResult.__dataclass_fields__
    config = build_reference_fixture_battery()[1]
    assert config.source_kind == "SYNTHETIC_MOTOR_INTERFACE_TEST"
    assert all(event.to_spike_event().neuron_type == "DNp01" for event in config.events)


def test_phase7o_canonical_artifact_remains_zero_event_and_separate():
    artifact = load_execution_artifact(
        DATA_ROOT
        / "malecns"
        / "looming_giant_fiber_v1"
        / "sensory_population_experiment_311_v1"
        / "99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5"
    )
    assert artifact.artifact_id == (
        "99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5"
    )
    assert all(
        not target["simulated_spikes"]
        for condition in artifact.result["conditions"]
        for target in condition["targets"]
    )
