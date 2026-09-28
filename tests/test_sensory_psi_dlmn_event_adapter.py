"""Phase 8H condition-explicit production PSI/DLMn adapter tests."""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest

from neurofly.psi_dlmn_event_relay import (
    EXPECTED_MOTOR_CONTRACT_ID,
    RELAY_SEMANTICS,
    SENSORY_SOURCE_KIND,
    _contract_reference,
    _propagate_origin_events,
    active_routes_from_contract,
    load_pinned_motor_contract,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.sensory_dnp01_motor_adapter import (
    PHASE7O_ARTIFACT_ID,
    REFERENCE_CONDITION_ID,
    build_sensory_dnp01_motor_payload,
)
from neurofly.sensory_population_execution_artifacts import (
    export_execution_artifact,
    load_execution_artifact,
)
from neurofly.sensory_population_readiness import load_phase7n_sources
from neurofly.sensory_psi_dlmn_event_adapter import (
    ARTIFACT_SCHEMA,
    SensoryPsiDlmnEventAdapterError,
    _build_payload_from_loaded,
    build_sensory_psi_dlmn_payload,
)
from neurofly.sensory_psi_dlmn_event_adapter_artifacts import (
    SensoryPsiDlmnEventArtifactError,
    generate_sensory_psi_dlmn_event_artifact,
    load_sensory_psi_dlmn_event_artifact,
    replay_sensory_psi_dlmn_event_artifact,
)

PHASE7O_PATH = (
    DEFAULT_SOURCE_ROOT / "sensory_population_experiment_311_v1" / PHASE7O_ARTIFACT_ID
)
PHASE8G_PATH = (
    DEFAULT_SOURCE_ROOT
    / "synthetic_psi_dlmn_event_relay_v1"
    / "1da8963e9097c570d67a2683f71744c2dee8c59662faa253cdc56ad32ee5e5b3"
)
MOTOR_CONTRACT_PATH = (
    DEFAULT_SOURCE_ROOT
    / "motor_neural_pathway_contract_v1"
    / EXPECTED_MOTOR_CONTRACT_ID
)
EXPECTED_DLMN_TARGETS = {
    800718,
    800890,
    801295,
    801895,
    801970,
    801998,
    802544,
    803013,
    803048,
    1050014552,
}


@pytest.fixture(scope="module")
def phase7o():
    return load_execution_artifact(PHASE7O_PATH)


@pytest.fixture(scope="module")
def sources():
    source, circuit, _grid = load_phase7n_sources()
    return source, circuit


@pytest.fixture(scope="module")
def pinned_motor():
    return load_pinned_motor_contract(MOTOR_CONTRACT_PATH)


def _condition(artifact, condition_id):
    return next(
        row
        for row in artifact.result["conditions"]
        if row["condition_id"] == condition_id
    )


def _with_reference_events(artifact, event_specs):
    result = copy.deepcopy(artifact.result)
    condition = next(
        row
        for row in result["conditions"]
        if row["condition_id"] == REFERENCE_CONDITION_ID
    )
    for target in condition["targets"]:
        target["simulated_spikes"] = [
            {
                "body_id": body_id,
                "step": step,
                "time_ms": step * condition["dt_ms"],
                "semantics": "SIMULATED_DNP01_MODEL_SPIKE",
            }
            for body_id, step in event_specs
            if target["body_id"] == body_id
        ]
    return replace(artifact, result=result)


def _local_production_result(artifact, sources, pinned_motor, event_specs):
    source, circuit = sources
    test_source = _with_reference_events(artifact, event_specs)
    _config, result = _build_payload_from_loaded(
        test_source,
        REFERENCE_CONDITION_ID,
        circuit,
        source.source_identity,
        pinned_motor,
    )
    return result


def test_canonical_reference_is_valid_empty_relay_and_audits_all_conditions(
    phase7o, sources
):
    source, circuit = sources
    config, result = build_sensory_psi_dlmn_payload(
        phase7o, REFERENCE_CONDITION_ID, circuit, source
    )
    assert phase7o.artifact_id == PHASE7O_ARTIFACT_ID
    assert config["source_kind"] == SENSORY_SOURCE_KIND
    assert config["source_condition_id"] == REFERENCE_CONDITION_ID
    assert config["phase8b_synthetic_fixture_in_provenance"] is False
    assert config["active_edge_policy"]["policy_id"] == "psi_dlmn_event_relay_v1"
    assert len(config["active_edge_policy"]["active_routes"]) == 14
    assert len(config["active_edge_policy"]["excluded_supplemental_routes"]) == 2
    assert result["source_event_records"] == []
    assert result["adapted_dnp01_events"] == []
    assert result["psi_routed_events"] == []
    assert result["dlmn_routed_events"] == []
    assert result["counts"] == {
        "dnp01_events": 0,
        "psi_routed_events": 0,
        "dlmn_routed_events": 0,
        "supplemental_psi_to_psi_propagated_events": 0,
    }
    assert result["all_conditions_zero_events"] is True
    assert result["all_conditions_zero_event_conditions"] == 35
    assert len(result["all_condition_audit"]) == 35
    assert all(
        row["dnp01_event_count"]
        == row["psi_routed_event_count"]
        == row["dlmn_routed_event_count"]
        == 0
        for row in result["all_condition_audit"]
    )
    assert result["source_kind"] == SENSORY_SOURCE_KIND
    assert "SYNTHETIC_MOTOR_INTERFACE_TEST" not in json.dumps(result)


def test_wrong_motor_contract_identity_fails_closed(phase7o, sources, pinned_motor):
    source, circuit = sources
    wrong_contract = copy.deepcopy(pinned_motor)
    wrong_contract["contract"]["contract_id"] = "0" * 64
    with pytest.raises(ValueError, match="pinned motor contract identity mismatch"):
        _build_payload_from_loaded(
            phase7o,
            REFERENCE_CONDITION_ID,
            circuit,
            source.source_identity,
            wrong_contract,
        )


def test_nonzero_vm_and_external_drive_do_not_fallback_to_routed_events(
    phase7o, sources
):
    source, circuit = sources
    condition = _condition(phase7o, REFERENCE_CONDITION_ID)
    assert any(
        target["maximum_membrane_mv"] > -52.0 and target["peak_drive_mveq"] > 0.0
        for target in condition["targets"]
    )
    config, result = build_sensory_psi_dlmn_payload(
        phase7o, REFERENCE_CONDITION_ID, circuit, source
    )
    assert any(
        target["filtered_synaptic_mveq_by_boundary"] == [0.0] * 15
        for target in condition["targets"]
    )
    assert config["fallback_policy"] == {
        "voltage_to_event": False,
        "external_drive_to_event": False,
        "filtered_state_to_event": False,
        "synthetic_event_fallback": False,
    }
    assert result["counts"]["dnp01_events"] == 0
    assert result["counts"]["psi_routed_events"] == 0
    assert result["counts"]["dlmn_routed_events"] == 0


def test_future_test_local_persisted_event_uses_shared_fanout_and_keeps_provenance(
    phase7o, sources, tmp_path
):
    source, circuit = sources
    # This isolated content-addressed fixture tests future adapter compatibility;
    # it neither mutates nor claims to be a canonical Phase 7O model result.
    mock_result = copy.deepcopy(phase7o.result)
    reference = next(
        row
        for row in mock_result["conditions"]
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
    test_local_persisted = export_execution_artifact(
        phase7o.config,
        mock_result,
        output_root=tmp_path / "test-local-phase7o",
    )
    result_config, result = build_sensory_psi_dlmn_payload(
        test_local_persisted, REFERENCE_CONDITION_ID, circuit, source
    )
    assert result_config["upstream_artifact"]["artifact_id"] == (
        test_local_persisted.artifact_id
    )
    assert result["counts"] == {
        "dnp01_events": 1,
        "psi_routed_events": 2,
        "dlmn_routed_events": 10,
        "supplemental_psi_to_psi_propagated_events": 0,
    }
    origin = result["adapted_dnp01_events"][0]
    assert origin["source_kind"] == SENSORY_SOURCE_KIND
    assert origin["spike_event"] == {
        "body_id": 10001,
        "node_index": origin["spike_event"]["node_index"],
        "neuron_type": "DNp01",
        "step": 4,
        "time_ms": 0.4,
        "semantics": "SIMULATED_DNP01_MODEL_SPIKE",
    }
    assert {row["target_psi_body_id"] for row in result["psi_routed_events"]} == {
        802401,
        903327,
    }
    assert {
        row["target_psi_body_id"]: (row["source_side"], row["target_side"])
        for row in result["psi_routed_events"]
    } == {802401: ("R", "L"), 903327: ("R", "R")}
    assert {
        row["target_dlmn_body_id"] for row in result["dlmn_routed_events"]
    } == EXPECTED_DLMN_TARGETS
    for record in [*result["psi_routed_events"], *result["dlmn_routed_events"]]:
        assert record["origin_source_kind"] == SENSORY_SOURCE_KIND
        assert record["provenance_kind"] == RELAY_SEMANTICS
        assert record["upstream_artifact_id"] == test_local_persisted.artifact_id
        assert record["source_condition_id"] == REFERENCE_CONDITION_ID
        assert record.get("step", record.get("routed_step")) == 4
        assert record.get("time_ms", record.get("routed_time_ms")) == 0.4


def test_test_local_bilateral_origins_remain_distinct_at_same_boundary(
    phase7o, sources, pinned_motor
):
    result = _local_production_result(
        phase7o, sources, pinned_motor, [(10001, 4), (10010, 4)]
    )
    assert result["counts"]["dnp01_events"] == 2
    assert result["counts"]["psi_routed_events"] == 4
    assert result["counts"]["dlmn_routed_events"] == 20
    assert len({row["origin_event_id"] for row in result["psi_routed_events"]}) == 2
    assert len({row["origin_event_id"] for row in result["dlmn_routed_events"]}) == 2
    assert len({row["event_id"] for row in result["dlmn_routed_events"]}) == 20
    for target_body_id in EXPECTED_DLMN_TARGETS:
        target_rows = [
            row
            for row in result["dlmn_routed_events"]
            if row["target_dlmn_body_id"] == target_body_id
        ]
        assert len(target_rows) == 2
        assert len({row["origin_event_id"] for row in target_rows}) == 2


def test_two_repeated_stored_events_each_keep_independent_paths(
    phase7o, sources, pinned_motor
):
    result = _local_production_result(
        phase7o, sources, pinned_motor, [(10010, 4), (10010, 9)]
    )
    assert result["counts"]["dnp01_events"] == 2
    assert result["counts"]["psi_routed_events"] == 4
    assert result["counts"]["dlmn_routed_events"] == 20
    assert {row["step"] for row in result["dlmn_routed_events"]} == {4, 9}
    assert len({row["origin_event_id"] for row in result["dlmn_routed_events"]}) == 2


def test_condition_must_be_explicit_and_caller_mutation_is_rejected(phase7o, sources):
    source, circuit = sources
    with pytest.raises(SensoryPsiDlmnEventAdapterError, match="missing or duplicated"):
        build_sensory_psi_dlmn_payload(phase7o, "not-a-condition", circuit, source)
    changed = copy.deepcopy(phase7o.result)
    condition = next(
        row
        for row in changed["conditions"]
        if row["condition_id"] == REFERENCE_CONDITION_ID
    )
    next(row for row in condition["targets"] if row["body_id"] == 10001)[
        "simulated_spikes"
    ].append(
        {
            "body_id": 10001,
            "step": 4,
            "time_ms": 0.4,
            "semantics": "SIMULATED_DNP01_MODEL_SPIKE",
        }
    )
    with pytest.raises(
        SensoryPsiDlmnEventAdapterError, match="differs from its persisted"
    ):
        build_sensory_psi_dlmn_payload(
            replace(phase7o, result=changed), REFERENCE_CONDITION_ID, circuit, source
        )


def test_synthetic_phase8g_artifact_cannot_enter_production_loader():
    with pytest.raises(SensoryPsiDlmnEventArtifactError):
        generate_sensory_psi_dlmn_event_artifact(
            PHASE8G_PATH,
            REFERENCE_CONDITION_ID,
            output_root=Path("/tmp/phase8h-invalid-source"),
        )


def test_phase8c_parallel_branch_remains_zero_for_same_condition(phase7o, sources):
    source, circuit = sources
    _config, ttmn_result = build_sensory_dnp01_motor_payload(
        phase7o, REFERENCE_CONDITION_ID, circuit, source
    )
    _config, relay_result = build_sensory_psi_dlmn_payload(
        phase7o, REFERENCE_CONDITION_ID, circuit, source
    )
    assert ttmn_result["event_count"] == 0
    assert all(not any(row["state"]) for row in ttmn_result["ttmn_model_state"])
    assert relay_result["counts"]["dnp01_events"] == 0
    assert relay_result["counts"]["psi_routed_events"] == 0
    assert relay_result["counts"]["dlmn_routed_events"] == 0


def test_structural_count_metadata_does_not_change_production_route_behavior(
    phase7o, sources, pinned_motor
):
    result = _local_production_result(phase7o, sources, pinned_motor, [(10001, 4)])
    routes = active_routes_from_contract(pinned_motor)
    reference = _contract_reference(pinned_motor)
    origins = result["adapted_dnp01_events"]
    identity = {
        "upstream_artifact_id": PHASE7O_ARTIFACT_ID,
        "source_condition_id": REFERENCE_CONDITION_ID,
    }
    source_events = [dict(row) for row in origins]
    original = _propagate_origin_events(
        source_events,
        routes,
        reference,
        source_kind=SENSORY_SOURCE_KIND,
        origin_identity=identity,
        context_fields=identity,
        dt_ms=0.1,
        maximum_step=14,
    )
    altered = tuple(
        replace(route, structural_count=route.structural_count * 97) for route in routes
    )
    changed_counts = _propagate_origin_events(
        source_events,
        altered,
        reference,
        source_kind=SENSORY_SOURCE_KIND,
        origin_identity=identity,
        context_fields=identity,
        dt_ms=0.1,
        maximum_step=14,
    )
    assert (
        len(original["psi_routed_events"])
        == len(changed_counts["psi_routed_events"])
        == 2
    )
    assert (
        len(original["dlmn_routed_events"])
        == len(changed_counts["dlmn_routed_events"])
        == 10
    )
    for key in ("psi_routed_events", "dlmn_routed_events"):
        first = copy.deepcopy(original[key])
        second = copy.deepcopy(changed_counts[key])
        for row in first:
            for metadata_key in (
                "structural_count",
                "dnp01_psi_structural_count",
                "psi_dlmn_structural_count",
            ):
                row.pop(metadata_key, None)
        for row in second:
            for metadata_key in (
                "structural_count",
                "dnp01_psi_structural_count",
                "psi_dlmn_structural_count",
            ):
                row.pop(metadata_key, None)
        assert first == second


def test_production_artifact_generation_replay_and_tamper_rejection(phase7o, tmp_path):
    artifact = generate_sensory_psi_dlmn_event_artifact(
        phase7o.path,
        REFERENCE_CONDITION_ID,
        output_root=tmp_path / ARTIFACT_SCHEMA,
    )
    replayed = replay_sensory_psi_dlmn_event_artifact(
        artifact.path, phase7o.path, REFERENCE_CONDITION_ID
    )
    assert artifact.artifact_id == replayed.artifact_id
    assert artifact.config["config_sha256"] == replayed.config["config_sha256"]
    assert artifact.result["result_sha256"] == replayed.result["result_sha256"]
    assert artifact.result["counts"]["dnp01_events"] == 0
    assert artifact.result["counts"]["psi_routed_events"] == 0
    assert artifact.result["counts"]["dlmn_routed_events"] == 0
    with pytest.raises(SensoryPsiDlmnEventArtifactError, match="does not match"):
        replay_sensory_psi_dlmn_event_artifact(artifact.path, phase7o.path, "lc4_only")
    with pytest.raises(SensoryPsiDlmnEventArtifactError):
        load_sensory_psi_dlmn_event_artifact(PHASE8G_PATH)

    tampered_path = tmp_path / "tampered" / artifact.artifact_id
    tampered_path.mkdir(parents=True)
    for name in ("adapter_config.json", "adapter_result.json", "manifest.json"):
        (tampered_path / name).write_bytes((artifact.path / name).read_bytes())
    result_path = tampered_path / "adapter_result.json"
    tampered = json.loads(result_path.read_text())
    tampered["counts"]["psi_routed_events"] = 1
    result_path.write_text(
        json.dumps(tampered, sort_keys=True, separators=(",", ":")) + "\n"
    )
    with pytest.raises(SensoryPsiDlmnEventArtifactError):
        load_sensory_psi_dlmn_event_artifact(tampered_path)
