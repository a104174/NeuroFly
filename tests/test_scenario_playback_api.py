"""World and neural playback adapters preserve their frozen scientific sources."""

import json

import pytest
from fastapi.testclient import TestClient

import neurofly.http_api as http
import neurofly.scenario_playback_api as transport
from neurofly.scenario_playback_api import (
    CANONICAL_NEURAL_ARTIFACT_ID,
    CANONICAL_SCENARIO_ARTIFACT_ID,
    CANONICAL_WORLD_ARTIFACT_ID,
    DEFAULT_SCENARIO_PATH,
    load_neural_playback,
    load_scenario_playback,
    scenario_catalog,
)


@pytest.fixture(scope="module")
def playbacks():
    # Each call performs the real full historical/source/numerical replay.
    return {s.id: load_scenario_playback(s.id) for s in scenario_catalog()}


def test_canonical_transport(playbacks):
    baseline, looming = [
        playbacks[k] for k in ("BASELINE_CONTROL", "LOOMING_CIRCUIT_VALIDATION")
    ]
    for p in (baseline, looming):
        assert p.artifact_id == CANONICAL_SCENARIO_ARTIFACT_ID
        assert len(p.frames) == 15
        assert p.dt_ms == 0.1
        assert p.duration_ms == pytest.approx(1.4)
        assert p.total_dnp01_spikes == 0
        assert p.statuses.closed_loop_execution_completed
        assert not p.statuses.body_movement_occurred
        assert not p.statuses.genuine_nonzero_actuation_occurred
        assert p.statuses.body_state_feedback_wired
        assert not p.statuses.body_state_feedback_realized
        for i, f in enumerate(p.frames):
            assert f.step == i
            assert f.time_ms == pytest.approx(i * 0.1)
            assert (f.body.x_world_eq, f.body.z_world_eq) == (0, 0)
            assert f.actuator_commands.RIGHT_TTM_ACTUATOR == 0
            assert f.actuator_commands.LEFT_TTM_ACTUATOR == 0
        payload = p.model_dump(mode="json", by_alias=True)
        assert len(json.dumps(payload).encode()) < 16000
        assert "sensory_state_by_boundary" not in payload
        assert "source_contributions_by_interval" not in payload
        assert payload["schema"] == "scenario_playback_v1"
    assert all(f.object is None for f in baseline.frames)
    assert all(f.active_sensory_body_count == 0 for f in baseline.frames)
    assert all(f.lattice_radius is None for f in baseline.frames)
    assert not baseline.statuses.environment_affected_sensory_input
    assert looming.frames[0].object.z_world_eq == 4
    assert looming.frames[-1].object.z_world_eq == pytest.approx(2.6)
    assert looming.frames[0].object.radius_world_eq == 1
    assert [looming.frames[i].lattice_radius for i in (0, 14)] == [2, 3]
    assert [looming.frames[i].active_sensory_body_count for i in (0, 14)] == [19, 22]
    assert (
        looming.frames[-1].dnp01_membrane_mv[0] > looming.frames[0].dnp01_membrane_mv[0]
    )
    assert looming.statuses.environment_affected_sensory_input


def test_world_transport_observational_and_compact(playbacks):
    p = playbacks["LOOMING_WORLD_EXPERIMENT"]
    assert p.artifact_id == CANONICAL_WORLD_ARTIFACT_ID
    assert len(p.frames) == 401 and p.duration_ms == 40
    assert p.requested_duration_ms == 40
    assert p.termination.status == "COMPLETED_VALID_HORIZON"
    assert p.preregistration_id
    assert p.statuses.genuine_nonzero_actuation_occurred == any(
        f.actuator_commands.RIGHT_TTM_ACTUATOR > 0
        or f.actuator_commands.LEFT_TTM_ACTUATOR > 0
        for f in p.frames
    )
    payload = p.model_dump(mode="json", by_alias=True)
    assert len(json.dumps(payload).encode()) < 400000
    assert "sensory_state_by_boundary" not in payload
    assert p.frames[0].object.z_world_eq == 4
    assert p.frames[-1].object.z_world_eq == pytest.approx(2)


def test_catalog_and_http(tmp_path, monkeypatch, playbacks):
    monkeypatch.setattr(
        http, "load_scenario_playback", lambda kind, path: playbacks[kind]
    )
    client = TestClient(http.create_app(tmp_path))
    catalog = client.get("/api/v1/scenarios").json()
    assert [s["id"] for s in catalog] == list(playbacks)
    assert all(s["preset_only"] for s in catalog)
    for kind in playbacks:
        response = client.get(f"/api/v1/scenarios/{kind}/playback")
        assert response.status_code == 200
        assert response.json()["scenario"]["id"] == kind
        assert response.json()["schema"] == "scenario_playback_v1"
    response = client.get("/api/v1/scenarios/ESCAPE/playback")
    assert response.status_code == 404
    assert response.json()["code"] == "unsupported_scenario"


def test_unavailable_replay_is_not_animation(tmp_path):
    client = TestClient(
        http.create_app(tmp_path, scenario_artifact_path=tmp_path / "absent")
    )
    response = client.get("/api/v1/scenarios/BASELINE_CONTROL/playback")
    assert response.status_code == 503
    assert response.json()["code"] == "scenario_unavailable"
    assert response.json()["schema"] == "experiment_http_error_v1"


def test_unknown_id_rejected_before_source_access():
    with pytest.raises(KeyError):
        load_scenario_playback("ESCAPE", DEFAULT_SCENARIO_PATH)


def test_neural_transport_exact_frozen_condition(playbacks):
    from neurofly.hs_dnp15_neural_validation_artifacts import (
        DEFAULT_ARTIFACT_ROOT,
        replay_neural_artifact,
    )

    p = playbacks[transport.NEURAL_KIND]
    source = replay_neural_artifact(
        DEFAULT_ARTIFACT_ROOT / CANONICAL_NEURAL_ARTIFACT_ID
    )
    run = next(
        r for r in source["result"]["runs"] if r["condition_id"] == p.condition_id
    )
    assert p.presentation_kind == "NEURAL_ONLY_VALIDATION"
    assert p.artifact_id == CANONICAL_NEURAL_ARTIFACT_ID
    assert (p.condition_id, p.duration_ms, p.dt_ms) == ("RIGHT_SIDE_MOTION", 50, 0.1)
    assert len(p.frames) == 501
    assert [n.body_id for n in p.sources] == [10015, 10016, 10023, 10034, 10181, 10419]
    assert [(n.body_id, n.side) for n in p.targets] == [(11215, "R"), (12069, "L")]
    assert p.input_units == "horizontal_motion_eq"
    assert p.source_units == "dimensionless_signed_proxy"
    assert p.target_units == "dnp15_state_eq"
    assert p.statuses.event_semantics == p.statuses.body_mapping == "NOT_DEFINED"
    assert (
        not p.statuses.recurrence_active and not p.statuses.electrical_coupling_active
    )
    assert {(e.source_id, e.target_id) for e in p.provenance.active_routes} == {
        (10015, 11215),
        (10016, 11215),
        (10023, 11215),
        (10034, 12069),
        (10181, 12069),
        (10419, 12069),
    }
    assert len(p.provenance.excluded_routes) == 7
    for i, frame in enumerate(p.frames):
        assert frame.time_ms == source["result"]["time_ms"][i]
        assert frame.hs_states == run["source_states"][i]
        assert frame.dnp15_states == run["target_states"][i]
        assert frame.input_descriptor.model_dump() == run["input_descriptors"][i]
        assert frame.bilateral_differential == run["right_minus_left_diagnostic"][i]
        assert (
            not {"body", "object", "actuator_commands", "spikes"}
            & frame.model_dump().keys()
        )
    assert load_neural_playback().model_dump_json() == p.model_dump_json()
    assert (
        not {"dnp01_body_ids", "total_dnp01_spikes", "termination"}
        & p.model_dump().keys()
    )


@pytest.mark.parametrize("failure", ["missing", "corrupt", "authority"])
def test_neural_scientific_failure_is_typed_not_fallback(
    tmp_path, monkeypatch, failure
):
    from neurofly.hs_dnp15_neural_validation_artifacts import DEFAULT_ARTIFACT_ROOT

    original = load_neural_playback
    if failure == "authority":
        monkeypatch.setattr(transport, "CONTEXT_AUDIT_ID", "0" * 64)
    else:
        target = tmp_path / "absent"
        if failure == "corrupt":
            import shutil

            target = tmp_path / CANONICAL_NEURAL_ARTIFACT_ID
            shutil.copytree(
                DEFAULT_ARTIFACT_ROOT / CANONICAL_NEURAL_ARTIFACT_ID, target
            )
            artifact_file = next(target.glob("*.json"))
            artifact_file.write_text("{}")  # TEST_ONLY corrupted copy, never source.
        monkeypatch.setattr(transport, "load_neural_playback", lambda: original(target))
    response = TestClient(http.create_app(tmp_path)).get(
        f"/api/v1/scenarios/{transport.NEURAL_KIND}/playback"
    )
    assert response.status_code == 503
    assert response.json()["schema"] == "experiment_http_error_v1"
    assert response.json()["code"] == "scenario_unavailable"
    assert "frames" not in response.json()
