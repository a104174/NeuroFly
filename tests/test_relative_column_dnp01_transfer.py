"""Phase 7F routing, model-input, replay, and scientific-boundary tests."""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT, DEFAULT_WORKBOOK
from neurofly.relative_column_dnp01_artifacts import (
    DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    DEFAULT_SENSORY_ARTIFACT_PATH,
    TransferArtifactError,
    artifact_id,
    export_artifact,
    load_artifact,
    replay_artifact,
)
from neurofly.relative_column_dnp01_transfer import (
    EXPECTED_ROUTES,
    EXPECTED_SENSORY_ARTIFACT_ID,
    REFERENCE_K_MVEQ_PER_STATE,
    SENSITIVITY_K,
    SensoryToDNp01Error,
    _validated_timelines,
    build_readout_graph,
    compute_transfer_result,
    default_contract,
    route_drive,
    validated_routes,
)
from neurofly.relative_column_sensory_artifacts import (
    load_relative_column_sensory_artifact,
    replay_relative_column_sensory_artifact,
)
from neurofly.simulation import (
    PHASE7F_READOUT_SCOPE_ID,
    ExternalDriveSchedule,
    LIFConfig,
    LIFSimulator,
    SimulationInputError,
    build_phase2b_graph,
)

SOURCE_AVAILABLE = (
    DEFAULT_SOURCE_ROOT.exists()
    and DEFAULT_WORKBOOK.exists()
    and DEFAULT_ASSIGNMENT_ARTIFACT_PATH.exists()
    and DEFAULT_SENSORY_ARTIFACT_PATH.exists()
)


@pytest.fixture(scope="module")
def source():
    if not SOURCE_AVAILABLE:
        pytest.skip("pinned Phase 7D/7E local scientific source is unavailable")
    sensory = replay_relative_column_sensory_artifact(
        DEFAULT_SENSORY_ARTIFACT_PATH,
        assignment_artifact_path=DEFAULT_ASSIGNMENT_ARTIFACT_PATH,
    )
    return sensory, default_contract()


@pytest.fixture(scope="module")
def output(source):
    return compute_transfer_result(*source)


def _condition(result, name):
    return next(item for item in result["conditions"] if item["condition_id"] == name)


def _target(condition, body_id):
    return next(item for item in condition["targets"] if item["body_id"] == body_id)


def test_exact_pinned_routes_and_identity(source):
    _, contract = source
    routes = validated_routes(contract)
    assert (
        tuple((r.source_body_id, r.target_body_id, r.structural_weight) for r in routes)
        == EXPECTED_ROUTES
    )
    assert {(r.source_body_id, r.side) for r in routes} == {
        (11498, "L"),
        (12032, "L"),
        (14465, "R"),
        (16128, "R"),
    }
    assert all(
        route.side == ("R" if route.target_body_id == 10001 else "L")
        for route in routes
    )
    assert all(
        route.to_dict()["weight_semantics"] == "STRUCTURAL_COUNT_ROUTING_METADATA_ONLY"
        for route in routes
    )


def test_shared_transfer_sum_masks_and_structural_weight_independence(source):
    routes = validated_routes(source[1])
    values = {12032: 0.2, 16128: 0.2, 11498: 0.2, 14465: 0.2}
    total, contributions = route_drive(values, routes, k_transfer_mveq_per_state=2.0)
    assert total == {10001: 0.8, 10010: 0.8}
    assert {item["model_drive_mveq"] for item in contributions} == {0.4}
    changed_counts = tuple(replace(route, structural_weight=999) for route in routes)
    assert route_drive(values, changed_counts, k_transfer_mveq_per_state=2.0) == (
        total,
        contributions,
    )
    assert route_drive(values, routes, k_transfer_mveq_per_state=0.0)[0] == {
        10001: 0.0,
        10010: 0.0,
    }
    assert route_drive(values, routes, k_transfer_mveq_per_state=1.0)[0] == {
        10001: 0.4,
        10010: 0.4,
    }
    assert route_drive(
        values, routes, k_transfer_mveq_per_state=2.0, pathway_mask="LC4"
    )[0] == {10001: 0.4, 10010: 0.4}
    assert route_drive(
        values, routes, k_transfer_mveq_per_state=2.0, pathway_mask="LPLC2"
    )[0] == {10001: 0.4, 10010: 0.4}
    assert route_drive(
        values, routes, k_transfer_mveq_per_state=2.0, pathway_mask="none"
    )[0] == {10001: 0.0, 10010: 0.0}


@pytest.mark.parametrize("k", [-1, math.inf, math.nan, True])
def test_invalid_transfer_coefficient_fails_closed(source, k):
    with pytest.raises(SensoryToDNp01Error):
        route_drive(
            {body: 0.1 for body in (12032, 16128, 11498, 14465)},
            validated_routes(source[1]),
            k_transfer_mveq_per_state=k,
        )


def test_unauthorized_routes_and_side_mismatch_fail_closed(source):
    routes = validated_routes(source[1])
    states = {body: 0.1 for body in (12032, 16128, 11498, 14465)}
    with pytest.raises(SensoryToDNp01Error):
        route_drive(
            states,
            (*routes[:-1], replace(routes[-1], target_body_id=10010)),
            k_transfer_mveq_per_state=1.0,
        )
    with pytest.raises(SensoryToDNp01Error):
        route_drive(
            states,
            (*routes[:-1], replace(routes[-1], side="L")),
            k_transfer_mveq_per_state=1.0,
        )
    with pytest.raises(SensoryToDNp01Error):
        route_drive({**states, 999: 0.1}, routes, k_transfer_mveq_per_state=1.0)


def test_phase7e_integer_step_lookup_and_interval_alignment(source, output):
    timelines = _validated_timelines(source[0])
    left = timelines["left_expand_33_29"][2][12032]
    assert left[0] == 0.0 and left[1] > 0.0
    reference = _condition(output[1], "reference_bilateral_expansion")
    left_target = _target(reference, 10010)
    assert reference["time_alignment"] == "x_n_drives_dnp01_interval_n_to_n_plus_1"
    assert left_target["drive_mveq_by_interval"][0] == 0.0
    assert left_target["drive_mveq_by_interval"][1] == pytest.approx(left[1])
    assert reference["source_contributions_by_interval"][1]["step"] == 1
    assert reference["source_contributions_by_interval"][1]["time_ms"] == 0.1
    assert left_target["membrane_mv_by_boundary"][1] == -52.0
    assert left_target["membrane_mv_by_boundary"][2] > -52.0
    assert (
        len(left_target["membrane_mv_by_boundary"]) == reference["interval_count"] + 1
    )
    assert reference["dt_ms"] == 0.1


def test_existing_lif_default_rejection_and_explicit_model_boundary(source):
    graph = build_readout_graph(source[1])
    assert graph.node_count == 2 and graph.edge_count == 0
    simulator = LIFSimulator(
        graph,
        LIFConfig(
            k_syn_mv_per_contact=0.01,
            graph_scope_id=PHASE7F_READOUT_SCOPE_ID,
        ),
    )
    drive = ExternalDriveSchedule.from_body_ids(
        {10010: [1.0]}, provenance_id="phase7f_edge_routed_exploratory_model_drive_v1"
    )
    with pytest.raises(SimulationInputError, match="Direct external drive"):
        simulator.run(drive)
    result = simulator.run(
        drive, record_body_ids=(10001, 10010), allow_model_readout_drive=True
    )
    expected = -52.0 + (1.0 - math.exp(-0.1 / 20.0))
    assert result.membrane_mv[1, 1] == pytest.approx(expected)
    assert result.membrane_mv[1, 0] == -52.0
    assert not result.spikes and not result.delivered_events
    with pytest.raises(SimulationInputError, match="provenance"):
        simulator.run(
            ExternalDriveSchedule.from_body_ids({10010: [1.0]}),
            allow_model_readout_drive=True,
        )
    with pytest.raises(SimulationInputError, match="only the two"):
        simulator.run(
            ExternalDriveSchedule.from_body_ids(
                {12032: [1.0]},
                provenance_id="phase7f_edge_routed_exploratory_model_drive_v1",
            ),
            allow_model_readout_drive=True,
        )
    legacy = LIFSimulator(
        build_phase2b_graph(source[1]), LIFConfig(k_syn_mv_per_contact=0.01)
    )
    with pytest.raises(SimulationInputError, match="two-readout graph"):
        legacy.run(drive, allow_model_readout_drive=True)


def test_controls_side_isolation_and_sensitivity(output):
    config, result = output
    assert (
        config["transfer"]["reference_k_transfer_mveq_per_state"]
        == REFERENCE_K_MVEQ_PER_STATE
    )
    assert (
        tuple(config["transfer"]["sensitivity_k_transfer_mveq_per_state"])
        == SENSITIVITY_K
    )
    assert config["transfer"]["parameter_classification"] == "MODEL_ASSUMPTION"
    assert config["transfer"]["structural_weight_used_as_gain"] is False
    assert config["scientific_boundary"]["type_level_angular_drive_present"] is False
    assert config["scientific_boundary"]["ttmn_propagation_present"] is False
    for name in ("k_zero", "no_sources"):
        condition = _condition(result, name)
        assert all(
            target["peak_drive_mveq"] == 0 and target["maximum_membrane_mv"] == -52.0
            for target in condition["targets"]
        )
    assert _target(_condition(result, "left_lplc2_disk"), 10001)["peak_drive_mveq"] == 0
    assert (
        _target(_condition(result, "right_translated_disk"), 10010)["peak_drive_mveq"]
        == 0
    )
    lc4 = _target(_condition(result, "lc4_only"), 10001)["peak_drive_mveq"]
    lplc2 = _target(_condition(result, "lplc2_only"), 10001)["peak_drive_mveq"]
    combined = _target(_condition(result, "reference_bilateral_expansion"), 10001)[
        "peak_drive_mveq"
    ]
    assert combined == pytest.approx(lc4 + lplc2)
    assert _target(_condition(result, "sensitivity_k_2"), 10001)[
        "peak_drive_mveq"
    ] == pytest.approx(2 * combined)
    assert all(
        not target["simulated_spikes"]
        for condition in result["conditions"]
        for target in condition["targets"]
    )
    assert all(
        target["maximum_filtered_synaptic_mveq"] == 0
        for condition in result["conditions"]
        for target in condition["targets"]
    )


def test_source_identity_and_grid_tamper_fail_closed(source):
    artifact, contract = source
    changed = replace(artifact, artifact_id="wrong")
    with pytest.raises(SensoryToDNp01Error):
        compute_transfer_result(changed, contract)
    altered = json.loads(json.dumps(dict(artifact.result)))
    altered["conditions"][0]["body_trajectories"][0]["state_timeline"][1][
        "state_step"
    ] = 2
    with pytest.raises(SensoryToDNp01Error):
        _validated_timelines(replace(artifact, result=altered))
    changed_value = json.loads(json.dumps(dict(artifact.result)))
    changed_value["conditions"][0]["body_trajectories"][0]["state_timeline"][1][
        "state_value"
    ] = 0.9
    with pytest.raises(SensoryToDNp01Error, match="hash mismatch"):
        compute_transfer_result(replace(artifact, result=changed_value), contract)
    with pytest.raises(SensoryToDNp01Error):
        compute_transfer_result(
            artifact, contract, routes=validated_routes(contract)[:-1]
        )


def test_artifact_identity_replay_and_tamper(tmp_path: Path, output):
    config, result = output
    first_id = artifact_id(config, result)
    assert first_id == artifact_id(config, result)
    destination = tmp_path / first_id
    export_artifact(config, result, destination)
    assert load_artifact(destination).artifact_id == first_id
    assert replay_artifact(destination).artifact_id == first_id
    with pytest.raises(TransferArtifactError, match="immutable"):
        export_artifact(config, result, destination)
    payload = json.loads((destination / "transfer_result.json").read_text())
    payload["conditions"][0]["targets"][0]["peak_drive_mveq"] = 999
    (destination / "transfer_result.json").write_text(json.dumps(payload))
    with pytest.raises(TransferArtifactError):
        load_artifact(destination)
    assert (
        load_relative_column_sensory_artifact(DEFAULT_SENSORY_ARTIFACT_PATH).artifact_id
        == EXPECTED_SENSORY_ARTIFACT_ID
    )


def test_scientific_text_boundary(output):
    config, result = output
    text = json.dumps({"config": config, "result": result}).lower()
    for forbidden in (
        "biological spike",
        "synaptic efficacy",
        "escape triggered",
        "takeoff",
        "muscle force",
        "firing probability",
        "calibrated physiology",
    ):
        assert forbidden not in text
