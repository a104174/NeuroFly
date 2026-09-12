"""Offline tests for the Phase 4B GET-only HTTP adapter."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from neurofly.experiment_api import APPLICATION_API_SCHEMA_VERSION
from neurofly.experiment_artifacts import export_experiment_artifact
from neurofly.experiments import ExperimentConfig, ExperimentRunner, TelemetrySpec
from neurofly.http_api import (
    ARTIFACT_ROOT_ENV,
    HTTP_API_SCHEMA_VERSION,
    HTTP_ERROR_SCHEMA_VERSION,
    create_app,
    create_app_from_env,
)
from neurofly.malecns.contract import load_circuit_contract
from neurofly.malecns.sensory import LoomingStimulus, VisualPoint
from neurofly.sensory_encoder import LevelPEncoderConfig
from neurofly.simulation import LIFConfig
from neurofly.trajectory_characterization import PathwayCondition


@pytest.fixture(scope="module")
def circuit_contract():
    path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "derived"
        / "malecns"
        / "looming_giant_fiber_v1"
    )
    return load_circuit_contract(path)


def _config(
    circuit_contract,
    *,
    experiment_id="phase4b-http-test",
    k_syn=0.01,
    lc4_gain=20.0,
    pathway=PathwayCondition.COMBINED,
    selected_visual_body_ids=(12032,),
):
    # NEUROFLY_SYNTHETIC_BENCHMARK: HTTP fixture only; not calibration data.
    return ExperimentConfig.from_contract(
        experiment_id=experiment_id,
        circuit_contract=circuit_contract,
        stimulus=LoomingStimulus(
            object_radius_m=0.01,
            initial_distance_m=0.1,
            approach_velocity_m_s=1.0,
            center=VisualPoint(azimuth_rad=0.0, elevation_rad=0.0),
        ),
        duration_ms=20.0,
        encoder_config=LevelPEncoderConfig(
            lc4_gain_mv_eq=lc4_gain,
            lplc2_gain_mv_eq=20.0,
            omega_half_rad_per_s=1.0,
            theta_half_rad=0.4,
        ),
        lif_config=LIFConfig(k_syn_mv_per_contact=k_syn, dt_ms=0.1),
        telemetry=TelemetrySpec.validation_profile(
            selected_visual_body_ids=selected_visual_body_ids
        ),
        pathway_condition=pathway,
    )


def _export(root, circuit_contract, config, name):
    result = ExperimentRunner(circuit_contract).run(config)
    path = export_experiment_artifact(result, root / name)
    return path, result


@pytest.fixture()
def artifact_fixture(tmp_path, circuit_contract):
    path, result = _export(
        tmp_path,
        circuit_contract,
        _config(circuit_contract),
        "base",
    )
    return tmp_path, path, result


def _ids(root):
    from neurofly.experiment_api import ExperimentArtifactStore

    return ExperimentArtifactStore(root).discover_artifact_ids()


def _assert_json_native(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return
    if isinstance(value, dict):
        assert all(isinstance(key, str) for key in value)
        for item in value.values():
            _assert_json_native(item)
        return
    if isinstance(value, list):
        for item in value:
            _assert_json_native(item)
        return
    raise AssertionError(f"non-JSON-native value: {type(value).__name__}")


def test_app_factory_info_and_no_simulation_at_startup(artifact_fixture, monkeypatch):
    root, _path, _result = artifact_fixture

    def fail_run(*_args, **_kwargs):
        raise AssertionError("HTTP app must not execute ExperimentRunner")

    monkeypatch.setattr(ExperimentRunner, "run", fail_run)
    client = TestClient(create_app(root))
    response = client.get("/api/v1")
    assert response.status_code == 200
    assert response.json() == {
        "schema": HTTP_API_SCHEMA_VERSION,
        "api": "neurofly",
        "http_api_version": "v1",
        "application_contract": APPLICATION_API_SCHEMA_VERSION,
        "read_only": True,
    }
    assert client.get("/health").json()["status"] == "ok"


def test_env_factory_uses_only_explicit_artifact_root(tmp_path, monkeypatch):
    monkeypatch.setenv(ARTIFACT_ROOT_ENV, str(tmp_path))
    app = create_app_from_env()
    assert app.state.experiment_artifact_store.root == tmp_path.resolve()


def test_list_and_summary_are_json_safe_and_complete(artifact_fixture):
    root, _path, result = artifact_fixture
    client = TestClient(create_app(root))
    response = client.get("/api/v1/experiments")
    assert response.status_code == 200
    payload = response.json()
    _assert_json_native(payload)
    assert payload["schema"] == HTTP_API_SCHEMA_VERSION
    assert payload["count"] == 1
    artifact_id = payload["experiments"][0]["artifact_id"]

    summary_response = client.get(f"/api/v1/experiments/{artifact_id}")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["artifact_id"] == artifact_id
    assert summary["dataset"] == result.dataset
    assert summary["candidate"]["identifier"] == result.candidate_identifier
    assert summary["graph_scope_id"] == result.graph_scope_id
    assert summary["pathway_condition"] == "COMBINED"
    assert summary["validation_status"] == "NOT_EVALUATED"
    assert set(summary["populations"]) == {"LC4", "LPLC2"}
    assert [item["body_id"] for item in summary["dnp01"]] == [10001, 10010]
    assert summary["free_parameters"] == {
        "lc4_gain_mv_eq": 20.0,
        "lplc2_gain_mv_eq": 20.0,
        "omega_half_rad_per_s": 1.0,
        "theta_half_rad": 0.4,
        "k_syn_mv_per_contact": 0.01,
    }


def test_timeline_preserves_exact_values_and_declared_range(artifact_fixture):
    root, _path, result = artifact_fixture
    client = TestClient(create_app(root))
    artifact_id = _ids(root)[0]
    response = client.get(f"/api/v1/experiments/{artifact_id}/timeline")
    assert response.status_code == 200
    payload = response.json()
    assert payload["times_ms"] == list(result.times_ms)
    assert payload["step_times_ms"] == list(result.times_ms[:-1])
    assert payload["theta_rad"] == list(result.stimulus_theta_rad)
    assert payload["angular_expansion_velocity_rad_s"] == list(
        result.stimulus_dtheta_dt_rad_s
    )
    assert payload["lc4_drive_mveq"] == list(result.lc4_drive_mv_eq)
    assert payload["lplc2_drive_mveq"] == list(result.lplc2_drive_mv_eq)
    assert payload["time_unit"] == "ms"
    assert payload["interval_semantics"] == "step_values_apply_on_[t_n,t_n+dt)"
    assert len(payload["selected_body_telemetry"]) == len(
        result.selected_body_telemetry
    )

    ranged = client.get(
        f"/api/v1/experiments/{artifact_id}/timeline",
        params={"start_ms": 0.1, "end_ms": 0.3},
    )
    assert ranged.status_code == 200
    assert ranged.json()["times_ms"] == list(result.times_ms[1:4])
    invalid = client.get(
        f"/api/v1/experiments/{artifact_id}/timeline",
        params={"start_ms": 0.05, "end_ms": 0.3},
    )
    assert invalid.status_code == 400
    assert invalid.json()["schema"] == HTTP_ERROR_SCHEMA_VERSION


def test_body_telemetry_and_events_preserve_semantics(artifact_fixture):
    root, _path, result = artifact_fixture
    client = TestClient(create_app(root))
    artifact_id = _ids(root)[0]
    for body_id in (10001, 10010, 12032):
        response = client.get(f"/api/v1/experiments/{artifact_id}/bodies/{body_id}")
        assert response.status_code == 200
        payload = response.json()
        assert payload["body_id"] == body_id
        assert payload["time_unit"] == "ms"
        assert len(payload["times_ms"]) == len(result.times_ms)
    unavailable = client.get(f"/api/v1/experiments/{artifact_id}/bodies/999999")
    assert unavailable.status_code == 404
    assert unavailable.json()["code"] == "body_telemetry_unavailable"

    spikes = client.get(f"/api/v1/experiments/{artifact_id}/spikes")
    events = client.get(f"/api/v1/experiments/{artifact_id}/events")
    assert spikes.status_code == events.status_code == 200
    assert spikes.json()["spike_event_count"] == len(result.spike_events)
    event_payload = events.json()
    assert event_payload["delivered_event_count"] == len(result.delivered_events)
    assert event_payload["delivered_events"]
    first = event_payload["delivered_events"][0]
    assert {"source_body_id", "target_body_id", "structural_weight"}.issubset(first)
    assert "model_sign" in first
    assert "event_increment_mV_eq" in first
    assert "synaptic_strength" not in first


def test_comparison_preserves_direction_parameters_pathways_and_status(
    tmp_path, circuit_contract
):
    _export(
        tmp_path,
        circuit_contract,
        _config(circuit_contract, experiment_id="http-low", k_syn=0.01),
        "low",
    )
    _export(
        tmp_path,
        circuit_contract,
        _config(
            circuit_contract,
            experiment_id="http-high",
            k_syn=0.02,
            lc4_gain=25.0,
            pathway=PathwayCondition.LC4_ONLY,
        ),
        "high",
    )
    client = TestClient(create_app(tmp_path))
    low_id, high_id = _ids(tmp_path)
    response = client.get(
        "/api/v1/comparisons",
        params={"artifact_a": low_id, "artifact_b": high_id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact_a_id"] == low_id
    assert payload["artifact_b_id"] == high_id
    assert payload["compatibility_class"] == "DIRECT_MODEL_COMPARISON"
    assert payload["empirical_validation_status"] == "NOT_EVALUATED"
    assert [item["body_id"] for item in payload["dnp01"]] == [10001, 10010]
    paths = {item["path"] for item in payload["configuration_differences"]}
    assert "neural.k_syn_mv_per_contact" in paths
    assert "encoder.lc4_gain_mv_eq" in paths
    assert "pathway_condition" in paths
    reverse = client.get(
        "/api/v1/comparisons",
        params={"artifact_a": high_id, "artifact_b": low_id},
    ).json()
    forward = next(
        item
        for item in payload["configuration_differences"]
        if item["path"] == "neural.k_syn_mv_per_contact"
    )
    backward = next(
        item
        for item in reverse["configuration_differences"]
        if item["path"] == "neural.k_syn_mv_per_contact"
    )
    assert forward["value_b"] - forward["value_a"] == -(
        backward["value_b"] - backward["value_a"]
    )


def test_source_mismatch_remains_visible_as_scientific_comparison(
    tmp_path, circuit_contract
):
    config = _config(circuit_contract, experiment_id="http-source-a")
    original = ExperimentRunner(circuit_contract).run(config)
    changed_config = replace(
        config,
        candidate_version=2,
        source_endpoint="https://example.invalid/other-source",
        circuit_integrity=(
            ("connections.jsonl", "a" * 64),
            ("neurons.jsonl", "b" * 64),
        ),
    )
    changed = replace(
        original,
        config=changed_config,
        config_sha256=changed_config.sha256,
        candidate_version=2,
        circuit_integrity=changed_config.circuit_integrity,
    )
    export_experiment_artifact(original, tmp_path / "source-a")
    export_experiment_artifact(changed, tmp_path / "source-b")
    client = TestClient(create_app(tmp_path))
    first, second = _ids(tmp_path)
    response = client.get(
        "/api/v1/comparisons",
        params={"artifact_a": first, "artifact_b": second},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["compatibility_class"] == "SUMMARY_ONLY_COMPARISON"
    assert payload["source_model_differences"]
    assert payload["telemetry"]["dense_trajectory_comparable"] is False


def test_path_safety_and_corruption_have_stable_nonleaking_errors(
    artifact_fixture,
):
    root, path, _result = artifact_fixture
    client = TestClient(create_app(root))
    artifact_id = _ids(root)[0]
    bad = client.get("/api/v1/experiments/%2E%2E")
    assert bad.status_code == 400
    assert bad.json()["schema"] == HTTP_ERROR_SCHEMA_VERSION
    assert str(root) not in bad.text

    telemetry = path / "telemetry.json"
    telemetry.write_text(telemetry.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    corrupted = client.get(f"/api/v1/experiments/{artifact_id}")
    assert corrupted.status_code == 409
    assert corrupted.json() == {
        "schema": HTTP_ERROR_SCHEMA_VERSION,
        "code": "artifact_integrity_failure",
        "message": "artifact failed integrity validation",
    }
    assert str(root) not in corrupted.text
    assert "Traceback" not in corrupted.text


def test_write_methods_are_not_exposed_and_core_remains_independent(
    artifact_fixture,
):
    root, _path, _result = artifact_fixture
    app = create_app(root)
    client = TestClient(app)
    for method in ("post", "put", "patch", "delete"):
        response = getattr(client, method)("/api/v1/experiments")
        assert response.status_code == 405
        assert response.json()["schema"] == HTTP_ERROR_SCHEMA_VERSION
        assert response.json()["code"] == "method_not_allowed"
    scientific_routes = {
        route.path: route for route in app.routes if route.path.startswith("/api/v1/")
    }
    assert scientific_routes
    assert all(route.methods == {"GET"} for route in scientific_routes.values())

    source_root = Path(__file__).resolve().parents[1] / "src" / "neurofly"
    for name in (
        "experiment_artifacts.py",
        "experiment_comparison.py",
        "experiments.py",
        "simulation.py",
        "sensory_encoder.py",
    ):
        assert "fastapi" not in (source_root / name).read_text().lower()


def test_openapi_is_versioned_and_no_numpy_types_escape(artifact_fixture):
    root, _path, _result = artifact_fixture
    client = TestClient(create_app(root))
    schema = client.get("/openapi.json")
    assert schema.status_code == 200
    paths = schema.json()["paths"]
    assert "/api/v1/experiments" in paths
    assert "/api/v1/comparisons" in paths
    for path, operations in paths.items():
        if path.startswith("/api/v1/"):
            assert set(operations) == {"get"}
    _assert_json_native(schema.json())
    json.dumps(schema.json(), allow_nan=False)
