"""Phase 8I common-origin composition and deterministic replay tests."""

from __future__ import annotations

import copy
from dataclasses import replace

import pytest

import neurofly.synthetic_parallel_motor_branches as composition_module
from neurofly.malecns.contract import load_circuit_contract
from neurofly.motor_pathway import MOTOR_PATHWAY_EVIDENCE
from neurofly.psi_dlmn_event_relay import (
    EXPECTED_MOTOR_CONTRACT_ID,
    _propagate_fixture,
    active_routes_from_contract,
    execute_reference_relay,
    load_pinned_motor_contract,
)
from neurofly.psi_dlmn_event_relay_artifacts import (
    psi_dlmn_event_relay_artifact_id,
)
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.synthetic_motor_interface import (
    FIXTURE_IDS,
    build_reference_fixture_battery,
    execute_reference_battery,
)
from neurofly.synthetic_motor_interface_artifacts import synthetic_motor_artifact_id
from neurofly.synthetic_parallel_motor_branch_artifacts import (
    SyntheticParallelMotorArtifactError,
    _artifact_id,
    export_synthetic_parallel_motor_artifact,
    generate_synthetic_parallel_motor_artifact,
    load_synthetic_parallel_motor_artifact,
    replay_synthetic_parallel_motor_artifact,
)
from neurofly.synthetic_parallel_motor_branches import (
    EXPECTED_RELAY_CHILD_ARTIFACT_ID,
    EXPECTED_TTMN_CHILD_ARTIFACT_ID,
    ParallelMotorCompositionError,
    canonical_sha256,
    execute_parallel_motor_branches,
    validate_and_replay_payload,
)

CONTRACT_PATH = (
    DEFAULT_SOURCE_ROOT
    / "motor_neural_pathway_contract_v1"
    / EXPECTED_MOTOR_CONTRACT_ID
)


@pytest.fixture(scope="module")
def source_contract():
    return load_circuit_contract(DEFAULT_SOURCE_ROOT)


@pytest.fixture(scope="module")
def pinned_motor_contract():
    return load_pinned_motor_contract(CONTRACT_PATH)


@pytest.fixture(scope="module")
def composition(source_contract, pinned_motor_contract):
    return execute_parallel_motor_branches(source_contract, pinned_motor_contract)


def _fixture(result: dict, fixture_id: str) -> dict:
    return next(item for item in result["fixtures"] if item["fixture_id"] == fixture_id)


def _record_projection(rows: list[dict], count_fields: set[str]) -> list[dict]:
    projected = copy.deepcopy(rows)
    for record in projected:
        for key in count_fields:
            record.pop(key, None)
    return projected


def test_shared_six_fixture_battery_and_unchanged_child_artifact_identities(
    composition, source_contract, pinned_motor_contract
):
    config, result = composition
    ttmn_config, ttmn_result = execute_reference_battery(source_contract)
    relay_config, relay_result = execute_reference_relay(pinned_motor_contract)

    assert tuple(row["fixture_id"] for row in result["fixtures"]) == FIXTURE_IDS
    assert [row["fixture_id"] for row in config["fixture_battery"]] == list(FIXTURE_IDS)
    ttmn_artifact_id = synthetic_motor_artifact_id(
        ttmn_config["config_sha256"], ttmn_result["result_sha256"]
    )
    relay_artifact_id = psi_dlmn_event_relay_artifact_id(
        relay_config["config_sha256"], relay_result["result_sha256"]
    )
    assert ttmn_artifact_id == EXPECTED_TTMN_CHILD_ARTIFACT_ID
    assert relay_artifact_id == EXPECTED_RELAY_CHILD_ARTIFACT_ID
    assert config["child_artifacts"]["ttmn_phase6c"]["artifact_id"] == (
        EXPECTED_TTMN_CHILD_ARTIFACT_ID
    )
    assert config["child_artifacts"]["psi_dlmn_phase8g"]["artifact_id"] == (
        EXPECTED_RELAY_CHILD_ARTIFACT_ID
    )
    assert result["child_artifacts"] == config["child_artifacts"]
    assert result["summary"] == {
        "fixture_count": 6,
        "origin_event_count": 8,
        "ttmn_input_event_count": 8,
        "psi_receipt_count": 16,
        "dlmn_path_receipt_count": 80,
        "supplemental_psi_to_psi_propagated_event_count": 0,
    }


def test_provenance_and_branch_outputs_remain_semantically_separate(composition):
    config, result = composition
    assert config["input_source_kind"] == "SYNTHETIC_MOTOR_INTERFACE_TEST"
    assert config["sensory_source_artifact_id"] is None
    assert config["phase7o_causal_provenance"] is False
    assert (
        config["composition_semantics"]["phase7o_production_adapter_invoked"] is False
    )
    assert config["phase6c_ttmn_branch"]["output_semantics"] == (
        "SIMULATED_EXPLORATORY_TTMN_MODEL_STATE"
    )
    assert config["phase8g_psi_dlmn_branch"]["output_semantics"] == (
        "EXPLORATORY_ROUTED_MOTOR_EVENT"
    )
    assert config["composition_semantics"]["branch_outputs_merged"] is False
    assert config["composition_semantics"]["branch_priority_or_causality"] is None
    assert result["no_combined_motor_quantity"] is True
    assert result["sensory_source_artifact_id"] is None
    for fixture in result["fixtures"]:
        assert fixture["source_kind"] == "SYNTHETIC_MOTOR_INTERFACE_TEST"
        for row in fixture["psi_dlmn_branch"]["psi_routed_events"]:
            assert row["origin_source_kind"] == "SYNTHETIC_MOTOR_INTERFACE_TEST"
            assert row["provenance_kind"] == "EXPLORATORY_ROUTED_MOTOR_EVENT"
        for row in fixture["psi_dlmn_branch"]["dlmn_routed_events"]:
            assert row["origin_source_kind"] == "SYNTHETIC_MOTOR_INTERFACE_TEST"
            assert row["provenance_kind"] == "EXPLORATORY_ROUTED_MOTOR_EVENT"
    assert "SIMULATED_FROM_SENSORY_EXPERIMENT" not in str(result)
    assert not {
        "motor_activation_score",
        "motor_command",
        "escape_score",
        "branch_sum",
        "motor_strength",
    }.intersection(result)


def test_ttmn_and_psi_dlmn_branch_outputs_equal_canonical_children(
    composition, source_contract, pinned_motor_contract
):
    _, result = composition
    _, ttmn_result = execute_reference_battery(source_contract)
    _, relay_result = execute_reference_relay(pinned_motor_contract)
    canonical_ttmn = {row["fixture_id"]: row for row in ttmn_result["fixtures"]}
    canonical_relay = {row["fixture_id"]: row for row in relay_result["fixtures"]}

    for composed in result["fixtures"]:
        ttmn = canonical_ttmn[composed["fixture_id"]]
        relay = canonical_relay[composed["fixture_id"]]
        assert composed["origin_events"] == ttmn["source_events"]
        assert (
            composed["ttmn_branch"]["mapped_motor_inputs"]
            == ttmn["mapped_motor_inputs"]
        )
        assert composed["ttmn_branch"]["ttmn_model_state"] == ttmn["ttmn_model_state"]
        assert composed["ttmn_branch"]["child_fixture_result_sha256"] == (
            canonical_sha256(ttmn)
        )
        assert (
            composed["psi_dlmn_branch"]["psi_routed_events"]
            == relay["psi_routed_events"]
        )
        assert (
            composed["psi_dlmn_branch"]["dlmn_routed_events"]
            == relay["dlmn_routed_events"]
        )
        assert composed["psi_dlmn_branch"]["child_fixture_result_sha256"] == (
            canonical_sha256(relay)
        )


def test_zero_unilateral_bilateral_and_repeated_fixture_composition(composition):
    _, result = composition
    zero = _fixture(result, "ZERO_EVENT_CONTROL")
    assert zero["origin_events"] == []
    assert zero["ttmn_branch"]["mapped_motor_inputs"] == []
    assert zero["psi_dlmn_branch"]["psi_routed_events"] == []
    assert zero["psi_dlmn_branch"]["dlmn_routed_events"] == []
    assert all(not any(row["state"]) for row in zero["ttmn_branch"]["ttmn_model_state"])

    expected = {
        "RIGHT_SINGLE_EVENT": (1, 1, 2, 10, {10001: 800146}),
        "LEFT_SINGLE_EVENT": (1, 1, 2, 10, {10010: 804642}),
        "BILATERAL_SIMULTANEOUS_EVENT": (
            2,
            2,
            4,
            20,
            {10001: 800146, 10010: 804642},
        ),
        "RIGHT_REPEATED_EVENTS": (2, 2, 4, 20, {10001: 800146}),
        "LEFT_REPEATED_EVENTS": (2, 2, 4, 20, {10010: 804642}),
    }
    for fixture_id, (
        origin_count,
        input_count,
        psi_count,
        dlmn_count,
        targets,
    ) in expected.items():
        fixture = _fixture(result, fixture_id)
        assert len(fixture["origin_events"]) == origin_count
        assert len(fixture["ttmn_branch"]["mapped_motor_inputs"]) == input_count
        assert len(fixture["psi_dlmn_branch"]["psi_routed_events"]) == psi_count
        assert len(fixture["psi_dlmn_branch"]["dlmn_routed_events"]) == dlmn_count
        assert {
            row["source_body_id"]: row["target_body_id"]
            for row in fixture["ttmn_branch"]["mapped_motor_inputs"]
        } == targets
        assert len(fixture["common_origin_accounting"]) == origin_count
        assert all(
            row["ttmn_input_count"] == 1
            and row["psi_receipt_count"] == 2
            and row["dlmn_path_receipt_count"] == 10
            for row in fixture["common_origin_accounting"]
        )

    right = _fixture(result, "RIGHT_SINGLE_EVENT")
    right_states = {
        row["body_id"]: row for row in right["ttmn_branch"]["ttmn_model_state"]
    }
    assert right_states[800146]["peak_state"] == 0.25
    assert right_states[804642]["state"] == [0.0] * len(right_states[804642]["state"])
    left = _fixture(result, "LEFT_SINGLE_EVENT")
    left_states = {
        row["body_id"]: row for row in left["ttmn_branch"]["ttmn_model_state"]
    }
    assert left_states[804642]["peak_state"] == 0.25
    assert left_states[800146]["state"] == [0.0] * len(left_states[800146]["state"])

    bilateral = _fixture(result, "BILATERAL_SIMULTANEOUS_EVENT")
    assert (
        len(
            {
                row["origin_event_id"]
                for row in bilateral["psi_dlmn_branch"]["dlmn_routed_events"]
            }
        )
        == 2
    )
    for target in {
        row["target_dlmn_body_id"]
        for row in bilateral["psi_dlmn_branch"]["dlmn_routed_events"]
    }:
        coincident = [
            row
            for row in bilateral["psi_dlmn_branch"]["dlmn_routed_events"]
            if row["target_dlmn_body_id"] == target
        ]
        assert len(coincident) == 2
        assert len({row["origin_event_id"] for row in coincident}) == 2


def test_common_origin_identity_survives_both_branches_and_timing(composition):
    _, result = composition
    for fixture in result["fixtures"]:
        origin_by_id = {row["event_id"]: row for row in fixture["origin_events"]}
        accounting = {
            row["origin_event_id"]: row for row in fixture["common_origin_accounting"]
        }
        assert set(accounting) == set(origin_by_id)
        ttmn_inputs = fixture["ttmn_branch"]["mapped_motor_inputs"]
        psi_events = fixture["psi_dlmn_branch"]["psi_routed_events"]
        dlmn_events = fixture["psi_dlmn_branch"]["dlmn_routed_events"]
        for origin_id, origin in origin_by_id.items():
            link = accounting[origin_id]
            assert link["ttmn_input_count"] == 1
            assert link["psi_receipt_count"] == 2
            assert link["dlmn_path_receipt_count"] == 10
            assert any(
                row["source_body_id"] == origin["source_body_id"]
                and row["source_node_index"] == origin["source_node_index"]
                and row["target_body_id"] == link["ttmn_target_body_id"]
                and row["step"] == origin["step"]
                and row["time_ms"] == origin["time_ms"]
                for row in ttmn_inputs
            )
            psi = [row for row in psi_events if row["origin_event_id"] == origin_id]
            dlmn = [row for row in dlmn_events if row["origin_event_id"] == origin_id]
            assert {row["event_id"] for row in psi} == set(link["psi_event_ids"])
            assert {row["event_id"] for row in dlmn} == set(link["dlmn_event_ids"])
            assert all(
                row["routed_step"] == origin["step"]
                and row["routed_time_ms"] == origin["time_ms"]
                for row in psi
            )
            assert all(
                row["step"] == origin["step"] and row["time_ms"] == origin["time_ms"]
                for row in dlmn
            )


def test_cross_side_relay_and_excluded_psi_reciprocity_remain_explicit(
    composition,
):
    config, result = composition
    assert config["phase8g_psi_dlmn_branch"]["active_route_policy_id"] == (
        "psi_dlmn_event_relay_v1"
    )
    assert len(config["phase8g_psi_dlmn_branch"]["active_route_ids"]) == 14
    assert (
        len(config["phase8g_psi_dlmn_branch"]["excluded_psi_reciprocal_edge_ids"]) == 2
    )
    bilateral = _fixture(result, "BILATERAL_SIMULTANEOUS_EVENT")
    right_routes = [
        row
        for row in bilateral["psi_dlmn_branch"]["psi_routed_events"]
        if row["origin_dnp01_body_id"] == 10001
    ]
    assert {(row["source_side"], row["target_side"]) for row in right_routes} == {
        ("R", "L"),
        ("R", "R"),
    }
    assert result["summary"]["supplemental_psi_to_psi_propagated_event_count"] == 0
    excluded_ids = set(
        config["phase8g_psi_dlmn_branch"]["excluded_psi_reciprocal_edge_ids"]
    )
    assert not any(
        row["route_edge_id"] in excluded_ids
        for fixture in result["fixtures"]
        for row in fixture["psi_dlmn_branch"]["psi_routed_events"]
    )


def test_structural_counts_are_metadata_in_the_composed_outputs(
    composition, source_contract, pinned_motor_contract
):
    config, _ = composition
    routes = active_routes_from_contract(pinned_motor_contract)
    fixture = build_reference_fixture_battery()[1]
    reference = config["phase8g_psi_dlmn_branch"]["motor_contract"]
    baseline = _propagate_fixture(fixture, routes, reference)
    count_variant = tuple(
        replace(route, structural_count=route.structural_count * 1000)
        for route in routes
    )
    changed = _propagate_fixture(fixture, count_variant, reference)
    _, ttmn_result = execute_reference_battery(source_contract)
    ttmn_fixture = _fixture(ttmn_result, "RIGHT_SINGLE_EVENT")
    baseline_composed = composition_module._compose_fixture(
        ttmn_fixture,
        baseline,
    )
    changed_composed = composition_module._compose_fixture(
        ttmn_fixture,
        changed,
    )
    assert (
        baseline_composed["ttmn_branch"]["ttmn_model_state"]
        == changed_composed["ttmn_branch"]["ttmn_model_state"]
    )
    assert len(changed_composed["psi_dlmn_branch"]["psi_routed_events"]) == 2
    assert len(changed_composed["psi_dlmn_branch"]["dlmn_routed_events"]) == 10
    assert _record_projection(
        baseline_composed["psi_dlmn_branch"]["psi_routed_events"],
        {"structural_count"},
    ) == _record_projection(
        changed_composed["psi_dlmn_branch"]["psi_routed_events"],
        {"structural_count"},
    )
    assert _record_projection(
        baseline_composed["psi_dlmn_branch"]["dlmn_routed_events"],
        {"dnp01_psi_structural_count", "psi_dlmn_structural_count"},
    ) == _record_projection(
        changed_composed["psi_dlmn_branch"]["dlmn_routed_events"],
        {"dnp01_psi_structural_count", "psi_dlmn_structural_count"},
    )
    assert (
        baseline_composed["psi_dlmn_branch"]["psi_routed_events"][0]["structural_count"]
        != changed_composed["psi_dlmn_branch"]["psi_routed_events"][0][
            "structural_count"
        ]
    )
    assert ttmn_fixture["ttmn_model_state"][0]["peak_state"] == 0.25
    assert [
        edge["structural_weight"] for edge in MOTOR_PATHWAY_EVIDENCE.chemical_edges
    ] == [70, 20]


def test_artifact_is_deterministic_replayable_and_tamper_evident(
    tmp_path, source_contract, pinned_motor_contract
):
    config, result = execute_parallel_motor_branches(
        source_contract, pinned_motor_contract
    )
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    path = tmp_path / artifact_id
    artifact = export_synthetic_parallel_motor_artifact(
        config,
        result,
        path,
        circuit_contract=source_contract,
        pinned_motor_contract=pinned_motor_contract,
    )
    assert artifact.artifact_id == artifact.path.name
    assert load_synthetic_parallel_motor_artifact(path).artifact_id == artifact_id
    replayed = replay_synthetic_parallel_motor_artifact(
        path,
        source_root=DEFAULT_SOURCE_ROOT,
        motor_contract_path=CONTRACT_PATH,
    )
    assert replayed.artifact_id == artifact_id
    assert dict(replayed.config) == config
    assert dict(replayed.result) == result
    with pytest.raises(SyntheticParallelMotorArtifactError, match="already exists"):
        export_synthetic_parallel_motor_artifact(
            config,
            result,
            path,
            circuit_contract=source_contract,
            pinned_motor_contract=pinned_motor_contract,
        )

    tampered = copy.deepcopy(result)
    tampered["fixtures"][1]["ttmn_branch"]["ttmn_model_state"][0]["state"][10] = 99
    with pytest.raises(ParallelMotorCompositionError, match="differs from replay"):
        validate_and_replay_payload(
            config, tampered, source_contract, pinned_motor_contract
        )

    tampered_config = copy.deepcopy(config)
    tampered_config["composition_semantics"]["branch_outputs_merged"] = True
    with pytest.raises(
        ParallelMotorCompositionError, match="config differs from replay"
    ):
        validate_and_replay_payload(
            tampered_config, result, source_contract, pinned_motor_contract
        )

    result_path = path / "composition_result.json"
    original = result_path.read_bytes()
    result_path.write_bytes(original + b" ")
    with pytest.raises(SyntheticParallelMotorArtifactError, match="canonical JSON"):
        load_synthetic_parallel_motor_artifact(path)


def test_generate_is_idempotent_and_rejects_wrong_motor_contract(tmp_path):
    first = generate_synthetic_parallel_motor_artifact(output_root=tmp_path)
    second = generate_synthetic_parallel_motor_artifact(output_root=tmp_path)
    assert first.artifact_id == second.artifact_id
    assert first.path == second.path

    wrong = {
        "contract": {"contract_id": "0" * 64},
        "manifest": {"artifact_id": "0" * 64},
    }
    source_contract = load_circuit_contract(DEFAULT_SOURCE_ROOT)
    with pytest.raises(ValueError):
        execute_parallel_motor_branches(source_contract, wrong)
