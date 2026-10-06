"""Phase31 is a reduced, read-only transport over the frozen Phase30 authority."""

import copy
import hashlib
import json

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import neurofly.exploratory_course_control_artifacts as artifacts
import neurofly.http_api as http
import neurofly.scenario_playback_api as api
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256


@pytest.fixture(scope="module")
def authority():
    return artifacts.replay_closed_loop_artifact(
        artifacts.DEFAULT_ARTIFACT_ROOT / api.CANONICAL_COURSE_ARTIFACT_ID
    )


@pytest.fixture(scope="module")
def playback():
    return api.load_course_playback()


def test_exact_boundary_transport(authority, playback):
    run = next(
        r
        for r in authority["result"]["runs"]
        if r["condition"]["id"] == "CLOSED_LOOP_PERTURBATION"
    )
    assert playback.artifact_id == authority["artifact_id"]
    assert playback.presentation_kind == "EXPLORATORY_CLOSED_LOOP_MODEL"
    assert playback.condition_id == "CLOSED_LOOP_PERTURBATION"
    assert playback.scenario.id == "EXPLORATORY_COURSE_CONTROL"
    assert (playback.dt_ms, playback.duration_ms, len(playback.frames)) == (
        0.1,
        50,
        501,
    )
    assert playback.sources == api.load_neural_playback().sources
    assert [n.body_id for n in playback.targets] == [11215, 12069]
    assert len(playback.provenance.neural.active_routes) == 6
    assert len(playback.provenance.neural.excluded_routes) == 7
    for frame, boundary in zip(playback.frames, run["boundaries"], strict=True):
        for field in (
            "time_ms",
            "yaw_orientation_eq",
            "previous_orientation_eq",
            "relative_view_eq",
            "hs_states",
            "dnp15_states",
            "yaw_drive_eq",
            "observation_clipped",
            "external_orientation_increment_eq",
        ):
            assert getattr(frame, field) == boundary[field]
        assert frame.step == boundary["boundary_index"]
        assert frame.bilateral_differential == boundary["dnp15_differential"]
        assert frame.input_descriptor.R == boundary["latched_motion"]["right"]
        assert frame.input_descriptor.L == boundary["latched_motion"]["left"]
        if boundary["observation"]:
            assert frame.observation.interval_start_step == frame.step - 1
            assert frame.observation.interval_end_step == frame.step
            assert (
                frame.observation.raw_view_motion_eq_per_ms
                == (boundary["observation"]["raw_view_motion_eq_per_ms"])
            )
        else:
            assert frame.observation is None and frame.step == 0
    assert playback.frames[-1].external_orientation_increment_eq is None
    assert playback.summary.final_orientation_eq == 0.00033277101655776
    assert playback.summary.clipping_count == 0
    assert playback.summary.observed_interval_count == 500
    assert playback.summary.initial_perturbation_eq == 0.001


def test_analysis_units_and_no_fake_body(playback):
    assert playback.orientation_units == "yaw_orientation_eq"
    assert playback.view_units == "relative_view_eq"
    assert playback.target_units == "dnp15_state_eq"
    assert playback.input_units == "horizontal_motion_eq"
    assert playback.yaw_drive_units == "yaw_drive_eq"
    assert playback.statuses.translation == "NOT_MODELLED"
    assert playback.statuses.event_semantics == "NOT_DEFINED"
    assert not playback.statuses.absolute_heading_error_signal
    assert not playback.statuses.recurrence_active
    assert not playback.statuses.electrical_coupling_active
    analysis = playback.provenance.analysis
    assert analysis.classification == "MARGINAL_ORIENTATION_MODE"
    assert analysis.orientation_eigenvalue == 1
    assert analysis.local_motion_spectral_radius == 0.985517664092702
    assert not analysis.clipping_required_for_local_stability
    payload = playback.model_dump(mode="json", by_alias=True)
    assert len(playback.model_dump_json(by_alias=True).encode()) < 500_000
    for frame in payload["frames"]:
        assert not {"body", "torque", "angular_velocity", "spikes"} & frame.keys()
    for extra in ("body", "total_dnp01_spikes", "torque"):
        with pytest.raises(ValidationError):
            api.CoursePlaybackResult.model_validate({**payload, extra: 0})


def test_deterministic_and_four_payloads_immutable(playback):
    assert api.load_course_playback().model_dump_json(by_alias=True) == (
        playback.model_dump_json(by_alias=True)
    )
    expected = {
        "BASELINE_CONTROL": (
            "75d1f2856f0d896589a8b1f62fb61016d701045b760e216b7cb5fa70daa30668"
        ),
        "LOOMING_CIRCUIT_VALIDATION": (
            "c3387396dcffa6372287df1a7d4680bb7ba605df319af4cf10f140cfc3a4d223"
        ),
        "LOOMING_WORLD_EXPERIMENT": (
            "d06ef32aaf054b981464948916e5687951b40f571be5286513dad8ae440f26df"
        ),
        "HORIZONTAL_MOTION_NEURAL_VALIDATION": (
            "52554962f3e9c85c6866b5e3ec56f8a12d24340db2236ec52c7809c6ece8d404"
        ),
    }
    for kind, digest in expected.items():
        payload = api.load_scenario_playback(kind).model_dump(
            mode="json", by_alias=True
        )
        assert canonical_sha256(payload) == digest


def test_exact_old_serialized_bytes():
    # Captured from the committed Phase30 adapter, separately from canonical JSON.
    expected = {
        "BASELINE_CONTROL": (
            "475b550734133d6357fd5f8914549d9d1c5469ccfeaca8e1fb229311a9db5380"
        ),
        "LOOMING_CIRCUIT_VALIDATION": (
            "743e475ec7ad41e4cb80492688491607a19ef31ce3389ddddf6281ee9f8d8510"
        ),
        "LOOMING_WORLD_EXPERIMENT": (
            "cd9755131ecf6eb39ec26136f8d4bdadc1e65573ebfd387c4bbac25d3e53a060"
        ),
        "HORIZONTAL_MOTION_NEURAL_VALIDATION": (
            "2d61227727a0708ed5635a0054c729f9664db4e6b883edfac417573eddaafa6b"
        ),
    }
    for kind, digest in expected.items():
        raw = api.load_scenario_playback(kind).model_dump_json(by_alias=True).encode()
        assert hashlib.sha256(raw).hexdigest() == digest


@pytest.mark.parametrize("failure", ["missing", "corrupt", "authority", "analysis"])
def test_typed_failures_no_fallback(tmp_path, monkeypatch, authority, failure):
    if failure in ("missing", "corrupt"):
        path = tmp_path / "source"
        if failure == "corrupt":
            path.mkdir()
            (path / "manifest.json").write_text("{}")
        original = api.load_course_playback
        monkeypatch.setattr(api, "load_course_playback", lambda: original(path))
    else:
        invalid = copy.deepcopy(authority)
        if failure == "authority":
            invalid["artifact_id"] = "0" * 64
        else:
            invalid["config"]["preregistration"]["analysis"][
                "differential_spectral_radius"
            ] = 1.1
        monkeypatch.setattr(
            artifacts, "replay_closed_loop_artifact", lambda path: invalid
        )
    response = TestClient(http.create_app(tmp_path)).get(
        "/api/v1/scenarios/EXPLORATORY_COURSE_CONTROL/playback"
    )
    assert response.status_code == 503
    assert response.json()["schema"] == "experiment_http_error_v1"
    assert response.json()["code"] == "scenario_unavailable"
    assert "frames" not in response.json()


def test_real_http_variant(tmp_path, playback, monkeypatch):
    monkeypatch.setattr(api, "load_course_playback", lambda: playback)
    client = TestClient(http.create_app(tmp_path))
    assert len(client.get("/api/v1/scenarios").json()) == 5
    response = client.get("/api/v1/scenarios/EXPLORATORY_COURSE_CONTROL/playback")
    assert response.status_code == 200
    assert response.json() == json.loads(playback.model_dump_json(by_alias=True))
