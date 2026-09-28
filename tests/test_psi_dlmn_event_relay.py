"""Phase 8G bounded PSI/DLMn synthetic event relay tests."""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest

from neurofly.psi_dlmn_event_relay import (
    DLMN_EVENT_SCHEMA_VERSION,
    EXPECTED_MOTOR_CONTRACT_ID,
    PSI_EVENT_SCHEMA_VERSION,
    RELAY_SEMANTICS,
    SYNTHETIC_SOURCE_KIND,
    ActiveRoute,
    PsiDlmnEventRelayError,
    _propagate_fixture,
    active_routes_from_contract,
    execute_reference_relay,
    load_pinned_motor_contract,
    validate_and_replay_payload,
)
from neurofly.psi_dlmn_event_relay_artifacts import (
    PsiDlmnEventRelayArtifactError,
    _artifact_id,
    export_psi_dlmn_event_relay_artifact,
    load_psi_dlmn_event_relay_artifact,
    replay_psi_dlmn_event_relay_artifact,
)
from neurofly.psi_dlmn_event_relay_cli import main as relay_cli_main
from neurofly.synthetic_motor_interface import build_reference_fixture_battery

DATA_ROOT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "derived"
    / "malecns"
    / ("looming_giant_fiber_v1")
)
CONTRACT_PATH = (
    DATA_ROOT / "motor_neural_pathway_contract_v1" / EXPECTED_MOTOR_CONTRACT_ID
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
def pinned_motor_contract():
    return load_pinned_motor_contract(CONTRACT_PATH)


def _fixture(result: dict, fixture_id: str) -> dict:
    return next(item for item in result["fixtures"] if item["fixture_id"] == fixture_id)


def _route_projection(result: dict) -> dict:
    """Drop the descriptive source count fields while comparing event behavior."""

    projected = copy.deepcopy(result)
    for fixture in projected["fixtures"]:
        for record in fixture["psi_routed_events"]:
            record.pop("structural_count", None)
        for record in fixture["dlmn_routed_events"]:
            record.pop("dnp01_psi_structural_count", None)
            record.pop("psi_dlmn_structural_count", None)
    return projected


def test_active_policy_uses_fourteen_contract_routes_and_excludes_psi_reciprocity(
    pinned_motor_contract,
):
    routes = active_routes_from_contract(pinned_motor_contract)
    assert len(routes) == 14
    assert {route.query_group for route in routes} == {"dnp01_to_psi", "psi_to_dlmn"}
    assert sum(route.query_group == "dnp01_to_psi" for route in routes) == 4
    assert sum(route.query_group == "psi_to_dlmn" for route in routes) == 10
    assert not any(route.query_group == "psi_to_psi_supplemental" for route in routes)
    assert len(pinned_motor_contract["contract"]["chemical_edges"]) == 18


def test_zero_unilateral_bilateral_and_repeated_fanout(pinned_motor_contract):
    _, result = execute_reference_relay(pinned_motor_contract)

    zero = _fixture(result, "ZERO_EVENT_CONTROL")
    assert zero["counts"] == {
        "source_events": 0,
        "psi_routed_events": 0,
        "dlmn_routed_events": 0,
    }
    assert zero["psi_routed_events"] == []
    assert zero["dlmn_routed_events"] == []

    for fixture_id in ("RIGHT_SINGLE_EVENT", "LEFT_SINGLE_EVENT"):
        fixture = _fixture(result, fixture_id)
        assert fixture["counts"] == {
            "source_events": 1,
            "psi_routed_events": 2,
            "dlmn_routed_events": 10,
        }
        assert {row["target_psi_body_id"] for row in fixture["psi_routed_events"]} == {
            802401,
            903327,
        }
        assert {
            row["target_dlmn_body_id"] for row in fixture["dlmn_routed_events"]
        } == (EXPECTED_DLMN_TARGETS)

    for fixture_id in (
        "BILATERAL_SIMULTANEOUS_EVENT",
        "RIGHT_REPEATED_EVENTS",
        "LEFT_REPEATED_EVENTS",
    ):
        fixture = _fixture(result, fixture_id)
        assert fixture["counts"] == {
            "source_events": 2,
            "psi_routed_events": 4,
            "dlmn_routed_events": 20,
        }


def test_bilateral_coincident_paths_keep_distinct_origins_and_full_path_identity(
    pinned_motor_contract,
):
    _, result = execute_reference_relay(pinned_motor_contract)
    fixture = _fixture(result, "BILATERAL_SIMULTANEOUS_EVENT")
    assert {row["origin_dnp01_body_id"] for row in fixture["psi_routed_events"]} == {
        10001,
        10010,
    }
    assert {row["origin_dnp01_body_id"] for row in fixture["dlmn_routed_events"]} == {
        10001,
        10010,
    }
    assert len({row["event_id"] for row in fixture["dlmn_routed_events"]}) == 20
    assert all(len(row["route_edge_ids"]) == 2 for row in fixture["dlmn_routed_events"])
    for target in EXPECTED_DLMN_TARGETS:
        rows = [
            row
            for row in fixture["dlmn_routed_events"]
            if row["target_dlmn_body_id"] == target
        ]
        assert len(rows) == 2
        assert len({row["origin_event_id"] for row in rows}) == 2


def test_route_side_labels_and_same_boundary_timing_are_preserved(
    pinned_motor_contract,
):
    _, result = execute_reference_relay(pinned_motor_contract)
    right = _fixture(result, "RIGHT_SINGLE_EVENT")
    right_psi = {row["target_psi_body_id"]: row for row in right["psi_routed_events"]}
    assert (right_psi[802401]["source_side"], right_psi[802401]["target_side"]) == (
        "R",
        "L",
    )
    assert (right_psi[903327]["source_side"], right_psi[903327]["target_side"]) == (
        "R",
        "R",
    )
    left = _fixture(result, "LEFT_SINGLE_EVENT")
    left_psi = {row["target_psi_body_id"]: row for row in left["psi_routed_events"]}
    assert (left_psi[802401]["source_side"], left_psi[802401]["target_side"]) == (
        "L",
        "L",
    )
    assert (left_psi[903327]["source_side"], left_psi[903327]["target_side"]) == (
        "L",
        "R",
    )
    for row in [*right["psi_routed_events"], *right["dlmn_routed_events"]]:
        assert row.get("routed_step", row.get("step")) == 10
        assert row.get("routed_time_ms", row.get("time_ms")) == 1.0


def test_provenance_and_event_schemas_do_not_claim_psi_or_dlmn_spikes(
    pinned_motor_contract,
):
    _, result = execute_reference_relay(pinned_motor_contract)
    for fixture in result["fixtures"]:
        for event in fixture["source_events"]:
            assert event["source_kind"] == SYNTHETIC_SOURCE_KIND
            assert event["spike_event"]["body_id"] == event["source_body_id"]
        for record in fixture["psi_routed_events"]:
            assert record["schema_version"] == PSI_EVENT_SCHEMA_VERSION
            assert record["provenance_kind"] == RELAY_SEMANTICS
            assert record["origin_source_kind"] == SYNTHETIC_SOURCE_KIND
            assert "node_index" not in record
        for record in fixture["dlmn_routed_events"]:
            assert record["schema_version"] == DLMN_EVENT_SCHEMA_VERSION
            assert record["provenance_kind"] == RELAY_SEMANTICS
            assert record["origin_source_kind"] == SYNTHETIC_SOURCE_KIND
    assert "SIMULATED_FROM_SENSORY_EXPERIMENT" not in json.dumps(result)
    assert result["sensory_source_artifact_id"] is None


def test_repeated_events_have_independent_origin_and_boundary_groups(
    pinned_motor_contract,
):
    _, result = execute_reference_relay(pinned_motor_contract)
    for fixture_id in ("RIGHT_REPEATED_EVENTS", "LEFT_REPEATED_EVENTS"):
        fixture = _fixture(result, fixture_id)
        source_steps = {
            row["event_id"]: row["step"] for row in fixture["source_events"]
        }
        psi_by_origin = {}
        dlmn_by_origin = {}
        for row in fixture["psi_routed_events"]:
            psi_by_origin.setdefault(row["origin_event_id"], set()).add(
                row["routed_step"]
            )
        for row in fixture["dlmn_routed_events"]:
            dlmn_by_origin.setdefault(row["origin_event_id"], set()).add(row["step"])
        assert len(psi_by_origin) == len(dlmn_by_origin) == 2
        assert {next(iter(steps)) for steps in psi_by_origin.values()} == set(
            source_steps.values()
        )
        assert {next(iter(steps)) for steps in dlmn_by_origin.values()} == set(
            source_steps.values()
        )


def test_structural_count_metadata_does_not_scale_or_change_routing(
    pinned_motor_contract,
):
    routes = active_routes_from_contract(pinned_motor_contract)
    fixture = build_reference_fixture_battery()[1]
    contract_ref = {
        "contract_id": EXPECTED_MOTOR_CONTRACT_ID,
        "contract_sha256": pinned_motor_contract["manifest"]["contract_sha256"],
    }
    original = _propagate_fixture(fixture, routes, contract_ref)
    altered = tuple(
        replace(route, structural_count=route.structural_count * 100)
        for route in routes
    )
    metadata_changed = _propagate_fixture(fixture, altered, contract_ref)
    assert (
        len(original["psi_routed_events"])
        == len(metadata_changed["psi_routed_events"])
        == 2
    )
    assert (
        len(original["dlmn_routed_events"])
        == len(metadata_changed["dlmn_routed_events"])
        == 10
    )
    assert _route_projection({"fixtures": [original]}) == _route_projection(
        {"fixtures": [metadata_changed]}
    )
    assert [row["structural_count"] for row in original["psi_routed_events"]] != [
        row["structural_count"] for row in metadata_changed["psi_routed_events"]
    ]


def test_supplemental_psi_routes_are_visible_but_cannot_enter_propagation(
    pinned_motor_contract,
):
    config, result = execute_reference_relay(pinned_motor_contract)
    policy = config["active_edge_policy"]
    assert len(policy["excluded_supplemental_routes"]) == 2
    assert all(not row["active"] for row in policy["excluded_supplemental_routes"])
    assert result["summary"]["supplemental_psi_to_psi_propagated_event_count"] == 0
    active_routes = active_routes_from_contract(pinned_motor_contract)
    excluded = policy["excluded_supplemental_routes"][0]
    unauthorized = ActiveRoute(
        edge_id=excluded["edge_id"],
        query_group="psi_to_psi_supplemental",
        source_body_id=excluded["source_body_id"],
        source_type="PSI",
        source_instance="PSI_L",
        source_side="L",
        target_body_id=excluded["target_body_id"],
        target_type="PSI",
        target_instance="PSI_R",
        target_side="R",
        structural_count=excluded["structural_count"],
        modality="MALECNS_CHEMICAL_CONNECTIVITY",
        source_query_response_sha256=config["motor_contract"]["query_response_sha256"],
    )
    with pytest.raises(PsiDlmnEventRelayError, match="excluded route class"):
        _propagate_fixture(
            build_reference_fixture_battery()[1],
            (*active_routes, unauthorized),
            config["motor_contract"],
        )
    assert all(
        row["route_edge_id"]
        not in {edge["edge_id"] for edge in policy["excluded_supplemental_routes"]}
        for fixture in result["fixtures"]
        for row in fixture["psi_routed_events"]
    )


def test_wrong_or_tampered_contract_config_and_result_fail_closed(
    pinned_motor_contract,
):
    config, result = execute_reference_relay(pinned_motor_contract)
    wrong_contract = copy.deepcopy(pinned_motor_contract)
    wrong_contract["contract"]["contract_id"] = "0" * 64
    with pytest.raises(PsiDlmnEventRelayError, match="identity mismatch"):
        active_routes_from_contract(wrong_contract)
    tampered_config = copy.deepcopy(config)
    tampered_config["active_edge_policy"]["allowed_query_groups"].append(
        "psi_to_psi_supplemental"
    )
    with pytest.raises(PsiDlmnEventRelayError):
        validate_and_replay_payload(tampered_config, result, pinned_motor_contract)
    tampered_result = copy.deepcopy(result)
    tampered_result["fixtures"][1]["dlmn_routed_events"].pop()
    with pytest.raises(PsiDlmnEventRelayError, match="hash mismatch"):
        validate_and_replay_payload(config, tampered_result, pinned_motor_contract)


def test_artifact_generation_and_full_replay_are_deterministic(
    tmp_path, pinned_motor_contract
):
    config, result = execute_reference_relay(pinned_motor_contract)
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    destination = tmp_path / "phase8g" / artifact_id
    artifact = export_psi_dlmn_event_relay_artifact(
        config,
        result,
        destination,
        pinned_motor_contract=pinned_motor_contract,
    )
    assert artifact.artifact_id == artifact.path.name
    assert (
        load_psi_dlmn_event_relay_artifact(destination).artifact_id
        == artifact.artifact_id
    )
    replayed = replay_psi_dlmn_event_relay_artifact(
        destination, motor_contract_path=CONTRACT_PATH
    )
    assert replayed.artifact_id == artifact.artifact_id
    assert dict(replayed.config) == config
    assert dict(replayed.result) == result
    with pytest.raises(PsiDlmnEventRelayArtifactError, match="already exists"):
        export_psi_dlmn_event_relay_artifact(
            config,
            result,
            destination,
            pinned_motor_contract=pinned_motor_contract,
        )


def test_artifact_tampering_is_rejected(tmp_path, pinned_motor_contract):
    config, result = execute_reference_relay(pinned_motor_contract)
    artifact_id = _artifact_id(config["config_sha256"], result["result_sha256"])
    artifact_path = tmp_path / artifact_id
    export_psi_dlmn_event_relay_artifact(
        config,
        result,
        artifact_path,
        pinned_motor_contract=pinned_motor_contract,
    )
    result_path = artifact_path / "relay_result.json"
    result_path.write_bytes(result_path.read_bytes() + b" ")
    with pytest.raises(PsiDlmnEventRelayArtifactError):
        load_psi_dlmn_event_relay_artifact(artifact_path)


def test_offline_cli_generate_inspect_and_replay(tmp_path, capsys):
    output_root = tmp_path / "derived"
    assert (
        relay_cli_main(
            [
                "generate",
                "--motor-contract",
                str(CONTRACT_PATH),
                "--output-root",
                str(output_root),
            ]
        )
        == 0
    )
    generated = json.loads(capsys.readouterr().out)
    artifact_path = Path(generated["artifact_path"])
    assert generated["fixtures"][0]["fixture_id"] == "ZERO_EVENT_CONTROL"
    assert relay_cli_main(["inspect", str(artifact_path)]) == 0
    inspected = json.loads(capsys.readouterr().out)
    assert inspected["artifact_id"] == generated["artifact_id"]
    assert (
        relay_cli_main(
            ["replay", str(artifact_path), "--motor-contract", str(CONTRACT_PATH)]
        )
        == 0
    )
    replayed = json.loads(capsys.readouterr().out)
    assert replayed["artifact_id"] == generated["artifact_id"]
