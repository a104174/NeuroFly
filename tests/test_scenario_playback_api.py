"""Phase 14 compact transport tests; scientific authority remains Phase 13B."""

import json

import pytest
from fastapi.testclient import TestClient

import neurofly.http_api as http
from neurofly.scenario_playback_api import (
    CANONICAL_SCENARIO_ARTIFACT_ID,
    DEFAULT_SCENARIO_PATH,
    load_scenario_playback,
    scenario_catalog,
)


@pytest.fixture(scope="module")
def playbacks():
    # Each call performs the real full historical/source/numerical replay.
    return {s.id: load_scenario_playback(s.id) for s in scenario_catalog()}


def test_canonical_transport(playbacks):
    baseline, looming = playbacks.values()
    for p in playbacks.values():
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
