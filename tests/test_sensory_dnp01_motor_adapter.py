"""Phase 8C provenance adapter and zero-event regression tests."""

from __future__ import annotations

import copy
import json
from dataclasses import replace

import pytest

import neurofly.sensory_dnp01_motor_adapter as adapter_module
from neurofly.motor_pathway import (
    MOTOR_PATHWAY_EVIDENCE,
    TTMnIntegratorConfig,
    _integrate_ttmn,
    _map_motor_inputs,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.sensory_dnp01_motor_adapter import (
    PHASE7O_ARTIFACT_ID,
    REFERENCE_CONDITION_ID,
    SOURCE_KIND,
    SensoryDnp01MotorAdapterError,
    _extract_condition_events,
    build_sensory_dnp01_motor_payload,
    phase7o_canonical_zero_event_assertion,
)
from neurofly.sensory_dnp01_motor_adapter_artifacts import (
    SensoryDnp01MotorArtifactError,
    generate_sensory_dnp01_motor_artifact,
    load_sensory_dnp01_motor_artifact,
    replay_sensory_dnp01_motor_artifact,
)
from neurofly.sensory_population_execution_artifacts import load_execution_artifact
from neurofly.sensory_population_readiness import load_phase7n_sources

PHASE7O_PATH = (
    DEFAULT_SOURCE_ROOT / "sensory_population_experiment_311_v1" / PHASE7O_ARTIFACT_ID
)


@pytest.fixture(scope="module")
def phase7o():
    return load_execution_artifact(PHASE7O_PATH)


@pytest.fixture(scope="module")
def sources():
    source, circuit, _grid = load_phase7n_sources()
    return source, circuit


def _condition(artifact, condition_id):
    return next(
        row
        for row in artifact.result["conditions"]
        if row["condition_id"] == condition_id
    )


def test_canonical_reference_zero_events_produce_exact_zero_ttmn(phase7o, sources):
    source, circuit = sources
    config, result = build_sensory_dnp01_motor_payload(
        phase7o, REFERENCE_CONDITION_ID, circuit, source
    )
    reference = phase7o_canonical_zero_event_assertion(phase7o)
    assert phase7o.artifact_id == PHASE7O_ARTIFACT_ID
    assert reference["reference_event_count"] == 0
    assert reference["all_condition_event_count"] == 0
    assert config["source_kind"] == SOURCE_KIND
    assert config["source_condition_id"] == REFERENCE_CONDITION_ID
    assert result["source_event_records"] == []
    assert result["adapted_dnp01_events"] == []
    assert result["mapped_motor_inputs"] == []
    assert result["event_count"] == 0
    assert result["all_conditions_zero_events"] is True
    assert [row["event_count"] for row in result["all_condition_event_audit"]] == [
        0
    ] * 35
    assert {row["body_id"]: row["state"] for row in result["ttmn_model_state"]} == {
        800146: [0.0] * 15,
        804642: [0.0] * 15,
    }


def test_non_rest_subthreshold_vm_and_positive_drive_do_not_create_motor_state(
    phase7o, sources
):
    source, circuit = sources
    condition = _condition(phase7o, REFERENCE_CONDITION_ID)
    assert any(
        target["maximum_membrane_mv"] > -52.0
        and target["peak_drive_mveq"] > 0.0
        and target["filtered_synaptic_mveq_by_boundary"] == [0.0] * 15
        for target in condition["targets"]
    )
    _config, result = build_sensory_dnp01_motor_payload(
        phase7o, REFERENCE_CONDITION_ID, circuit, source
    )
    assert result["event_count"] == 0
    assert result["voltage_or_drive_fallback_used"] is False
    assert all(not any(row["state"]) for row in result["ttmn_model_state"])


def test_selected_condition_is_required_and_events_are_not_aggregated(phase7o):
    with pytest.raises(SensoryDnp01MotorAdapterError, match="selected.*missing"):
        adapter_module._condition_by_id(phase7o, "not_a_condition")
    with pytest.raises(
        SensoryDnp01MotorAdapterError, match="explicit source condition"
    ):
        adapter_module._condition_by_id(phase7o, "")


def test_future_genuine_spike_record_is_preserved_and_routed_without_zero_lock(
    sources,
):
    _source, circuit = sources
    condition = {
        "interval_count": 14,
        "dt_ms": 0.1,
        "time_alignment": "sensory_state_boundary_n_drives_interval_n_to_n_plus_1",
        "targets": [
            {
                "body_id": 10001,
                "side": "R",
                "simulated_spikes": [
                    {
                        "body_id": 10001,
                        "step": 4,
                        "time_ms": 0.4,
                        "semantics": "SIMULATED_DNP01_MODEL_SPIKE",
                    }
                ],
            },
            {"body_id": 10010, "side": "L", "simulated_spikes": []},
        ],
    }
    events = _extract_condition_events(condition, dt_ms=0.1, circuit_contract=circuit)
    assert len(events) == 1
    event = events[0]
    assert (event.body_id, event.node_index, event.neuron_type) == (10001, 0, "DNp01")
    assert (event.step, event.time_ms) == (4, 0.4)
    inputs = _map_motor_inputs(
        events,
        dt_ms=0.1,
        steps=14,
        model=TTMnIntegratorConfig(),
        evidence_contract=MOTOR_PATHWAY_EVIDENCE,
    )
    trajectories = _integrate_ttmn(
        times_ms=tuple(step * 0.1 for step in range(15)),
        dt_ms=0.1,
        inputs=inputs,
        model=TTMnIntegratorConfig(),
        evidence_contract=MOTOR_PATHWAY_EVIDENCE,
    )
    by_id = {row.body_id: row for row in trajectories}
    assert by_id[800146].state[4] == 0.25
    assert by_id[800146].input_event_count == 1
    assert by_id[804642].input_event_count == 0
    assert not any(by_id[804642].state)


@pytest.mark.parametrize(
    ("patch_record", "message"),
    [
        ({"time_ms": 0.40000000000001}, "identity/timing"),
        (
            {"semantics": "SYNTHETIC_MOTOR_INTERFACE_TEST"},
            "identity/timing",
        ),
        ({"body_id": 10010}, "identity/timing"),
        ({"source_kind": "SYNTHETIC_MOTOR_INTERFACE_TEST"}, "exact persisted"),
    ],
)
def test_event_parser_rejects_mutation_or_synthetic_fixture_record(
    sources, patch_record, message
):
    _source, circuit = sources
    record = {
        "body_id": 10001,
        "step": 4,
        "time_ms": 0.4,
        "semantics": "SIMULATED_DNP01_MODEL_SPIKE",
    }
    record.update(patch_record)
    condition = {
        "interval_count": 14,
        "dt_ms": 0.1,
        "time_alignment": "sensory_state_boundary_n_drives_interval_n_to_n_plus_1",
        "targets": [
            {"body_id": 10001, "side": "R", "simulated_spikes": [record]},
            {"body_id": 10010, "side": "L", "simulated_spikes": []},
        ],
    }
    with pytest.raises(SensoryDnp01MotorAdapterError, match=message):
        _extract_condition_events(condition, dt_ms=0.1, circuit_contract=circuit)


def test_source_event_mutation_after_load_is_rejected(phase7o, sources):
    source, circuit = sources
    altered_result = copy.deepcopy(phase7o.result)
    altered_result["conditions"][-1]["targets"][0]["simulated_spikes"].append(
        {
            "body_id": 10001,
            "step": 1,
            "time_ms": 0.1,
            "semantics": "SIMULATED_DNP01_MODEL_SPIKE",
        }
    )
    altered = replace(phase7o, result=altered_result)
    with pytest.raises(
        SensoryDnp01MotorAdapterError, match="differs from its persisted"
    ):
        build_sensory_dnp01_motor_payload(
            altered, REFERENCE_CONDITION_ID, circuit, source
        )


def test_structural_count_metadata_does_not_change_transfer(
    monkeypatch, phase7o, sources
):
    source, circuit = sources
    _config_a, result_a = build_sensory_dnp01_motor_payload(
        phase7o, REFERENCE_CONDITION_ID, circuit, source
    )
    original = adapter_module._route_records

    def altered_metadata():
        return [
            {**row, "structural_weight": row["structural_weight"] + 1234}
            for row in original()
        ]

    monkeypatch.setattr(adapter_module, "_route_records", altered_metadata)
    _config_b, result_b = build_sensory_dnp01_motor_payload(
        phase7o, REFERENCE_CONDITION_ID, circuit, source
    )
    assert result_b["mapped_motor_inputs"] == result_a["mapped_motor_inputs"]
    assert result_b["ttmn_model_state"] == result_a["ttmn_model_state"]


def test_route_count_metadata_does_not_scale_a_nonzero_persisted_event(
    monkeypatch, phase7o, sources
):
    source, circuit = sources
    mocked_result = copy.deepcopy(phase7o.result)
    reference = next(
        row
        for row in mocked_result["conditions"]
        if row["condition_id"] == REFERENCE_CONDITION_ID
    )
    next(row for row in reference["targets"] if row["body_id"] == 10001)[
        "simulated_spikes"
    ].append(
        {
            "body_id": 10001,
            "step": 4,
            "time_ms": 0.4,
            "semantics": "SIMULATED_DNP01_MODEL_SPIKE",
        }
    )
    test_local_source = replace(phase7o, result=mocked_result)
    config_a, result_a = adapter_module._build_payload_from_loaded(
        test_local_source,
        REFERENCE_CONDITION_ID,
        circuit,
        source.source_identity,
    )
    original = adapter_module._route_records
    monkeypatch.setattr(
        adapter_module,
        "_route_records",
        lambda: [
            {**row, "structural_weight": row["structural_weight"] + 999}
            for row in original()
        ],
    )
    config_b, result_b = adapter_module._build_payload_from_loaded(
        test_local_source,
        REFERENCE_CONDITION_ID,
        circuit,
        source.source_identity,
    )
    assert config_a["verified_routes"] != config_b["verified_routes"]
    assert result_a["event_count"] == 1
    assert result_a["mapped_motor_inputs"] == result_b["mapped_motor_inputs"]
    assert result_a["ttmn_model_state"] == result_b["ttmn_model_state"]


def test_artifact_generation_replay_and_tamper_rejection(phase7o, tmp_path):
    artifact = generate_sensory_dnp01_motor_artifact(
        phase7o.path,
        REFERENCE_CONDITION_ID,
        output_root=tmp_path / "artifacts",
    )
    replayed = replay_sensory_dnp01_motor_artifact(
        artifact.path, phase7o.path, REFERENCE_CONDITION_ID
    )
    assert artifact.artifact_id == replayed.artifact_id
    assert artifact.config["config_sha256"] == replayed.config["config_sha256"]
    assert artifact.result["result_sha256"] == replayed.result["result_sha256"]
    assert replayed.result["event_count"] == 0
    with pytest.raises(SensoryDnp01MotorArtifactError, match="condition"):
        replay_sensory_dnp01_motor_artifact(artifact.path, phase7o.path, "lc4_only")

    tampered_path = tmp_path / "tampered" / artifact.artifact_id
    tampered_path.mkdir(parents=True)
    for name in ("adapter_config.json", "adapter_result.json", "manifest.json"):
        (tampered_path / name).write_bytes((artifact.path / name).read_bytes())
    result_path = tampered_path / "adapter_result.json"
    result = json.loads(result_path.read_text())
    result["event_count"] = 1
    result_path.write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    )
    with pytest.raises(SensoryDnp01MotorArtifactError):
        load_sensory_dnp01_motor_artifact(tampered_path)


def test_artifact_source_identity_and_explicit_sensory_provenance(phase7o, tmp_path):
    artifact = generate_sensory_dnp01_motor_artifact(
        phase7o.path,
        REFERENCE_CONDITION_ID,
        output_root=tmp_path / "artifacts",
    )
    assert artifact.config["upstream_artifact"]["artifact_id"] == PHASE7O_ARTIFACT_ID
    assert artifact.result["source_kind"] == "SIMULATED_FROM_SENSORY_EXPERIMENT"
    assert (
        artifact.config["scientific_boundary"]["phase8b_synthetic_provenance_in_chain"]
        is False
    )
    assert artifact.result["synthetic_fallback_used"] is False
    assert artifact.config["fallback_policy"] == {
        "voltage_to_event": False,
        "external_drive_to_event": False,
        "filtered_state_to_event": False,
        "synthetic_event_fallback": False,
    }
