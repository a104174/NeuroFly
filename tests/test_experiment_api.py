"""Offline tests for the Phase 4A read-only application boundary."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from neurofly.experiment_api import (
    APPLICATION_API_SCHEMA_VERSION,
    ArtifactNotFoundError,
    ArtifactPathError,
    BodyTelemetryUnavailableError,
    CorruptedArtifactError,
    ExperimentArtifactStore,
    InvalidArtifactIdError,
    InvalidRangeError,
)
from neurofly.experiment_artifacts import export_experiment_artifact
from neurofly.experiments import ExperimentConfig, ExperimentRunner, TelemetrySpec
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
    k_syn=0.01,
    lc4_gain=20.0,
    pathway=PathwayCondition.COMBINED,
    selected_visual_body_ids=(12032,),
):
    # NEUROFLY_SYNTHETIC_BENCHMARK: application fixture, not calibration.
    return ExperimentConfig.from_contract(
        experiment_id="phase4a-api-test",
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
        tmp_path, circuit_contract, _config(circuit_contract), "base"
    )
    return tmp_path, path, result


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


def test_summary_is_json_safe_and_exposes_scientific_identity(
    artifact_fixture, circuit_contract
):
    root, path, result = artifact_fixture
    store = ExperimentArtifactStore(root)
    artifact_id = store.discover_artifact_ids()[0]
    summary = store.get_experiment(artifact_id)
    payload = summary.to_dict()
    _assert_json_native(payload)
    json.dumps(payload, allow_nan=False)
    assert payload["schema"] == APPLICATION_API_SCHEMA_VERSION
    assert payload["artifact_id"] == artifact_id
    assert payload["experiment_config_id"] == result.config.experiment_id
    assert payload["result_id"] == result.result_sha256
    assert payload["dataset"] == result.dataset
    assert payload["candidate"]["identifier"] == result.candidate_identifier
    assert payload["graph_scope_id"] == result.graph_scope_id
    assert payload["pathway_condition"] == "COMBINED"
    assert payload["validation_status"] == "NOT_EVALUATED"
    assert set(payload["populations"]) == {"LC4", "LPLC2"}
    assert [item["body_id"] for item in payload["dnp01"]] == [10001, 10010]
    assert payload["free_parameters"] == {
        "lc4_gain_mv_eq": 20.0,
        "lplc2_gain_mv_eq": 20.0,
        "omega_half_rad_per_s": 1.0,
        "theta_half_rad": 0.4,
        "k_syn_mv_per_contact": 0.01,
    }
    assert (
        store.get_experiment_by_config_id(result.config.sha256).artifact_id
        == artifact_id
    )
    assert (
        store.get_experiment_by_result_id(result.result_sha256).artifact_id
        == artifact_id
    )
    assert path.is_dir()


def test_timeline_preserves_exact_times_and_aligned_ranges(artifact_fixture):
    root, _path, result = artifact_fixture
    store = ExperimentArtifactStore(root)
    artifact_id = store.discover_artifact_ids()[0]
    timeline = store.get_timeline(artifact_id)
    assert timeline.times_ms == result.times_ms
    assert timeline.step_times_ms == result.times_ms[:-1]
    assert timeline.theta_rad == result.stimulus_theta_rad
    assert timeline.lc4_drive_mveq == result.lc4_drive_mv_eq
    assert timeline.lplc2_drive_mveq == result.lplc2_drive_mv_eq
    assert timeline.to_dict()["interval_semantics"] == (
        "step_values_apply_on_[t_n,t_n+dt)"
    )
    ranged = store.get_timeline(
        artifact_id, start_ms=result.times_ms[1], end_ms=result.times_ms[3]
    )
    assert ranged.times_ms == result.times_ms[1:4]
    assert ranged.step_times_ms == result.times_ms[1:3]
    assert ranged.theta_rad == result.stimulus_theta_rad[1:3]
    with pytest.raises(InvalidRangeError):
        store.get_timeline(artifact_id, start_ms=0.05, end_ms=0.2)


def test_body_telemetry_keeps_dn_and_selected_visual_identity(artifact_fixture):
    root, _path, result = artifact_fixture
    store = ExperimentArtifactStore(root)
    artifact_id = store.discover_artifact_ids()[0]
    for body_id in (10001, 10010, 12032):
        body = store.get_body_telemetry(artifact_id, body_id)
        assert body.body_id == body_id
        assert len(body.times_ms) == len(result.times_ms)
        assert len(body.step_times_ms) == len(result.times_ms) - 1
        assert len(body.membrane_mv) == len(body.times_ms)
        assert len(body.external_drive_mveq) == len(body.step_times_ms)
    with pytest.raises(BodyTelemetryUnavailableError):
        store.get_body_telemetry(artifact_id, 999999)


def test_events_preserve_structural_and_model_fields(artifact_fixture):
    root, _path, result = artifact_fixture
    store = ExperimentArtifactStore(root)
    artifact_id = store.discover_artifact_ids()[0]
    events = store.get_events(artifact_id)
    assert len(events.spike_events) == len(result.spike_events)
    assert len(events.delivered_events) == len(result.delivered_events)
    assert events.delivered_events
    event = events.delivered_events[0]
    assert event.target_body_id in {10001, 10010}
    assert event.structural_weight > 0
    assert event.model_sign == 1
    assert event.event_increment_mveq == pytest.approx(
        event.structural_weight * result.config.lif_config.k_syn_mv_per_contact
    )
    payload = events.to_dict()
    _assert_json_native(payload)
    assert "event_increment_mV_eq" in payload["delivered_events"][0]


def test_comparison_reuses_phase3c_direction_and_status(tmp_path, circuit_contract):
    low_path, _low = _export(
        tmp_path, circuit_contract, _config(circuit_contract, k_syn=0.01), "low"
    )
    high_path, _high = _export(
        tmp_path, circuit_contract, _config(circuit_contract, k_syn=0.02), "high"
    )
    store = ExperimentArtifactStore(tmp_path)
    low_id, high_id = store.discover_artifact_ids()
    comparison = store.get_comparison(low_id, high_id)
    payload = comparison.to_dict()
    _assert_json_native(payload)
    assert payload["compatibility_class"] == "DIRECT_MODEL_COMPARISON"
    assert any(
        item["path"] == "neural.k_syn_mv_per_contact"
        for item in payload["configuration_differences"]
    )
    assert [item["body_id"] for item in payload["dnp01"]] == [10001, 10010]
    assert payload["empirical_validation_status"] == "NOT_EVALUATED"
    reverse = store.get_comparison(high_id, low_id)
    forward_delta = next(
        item["value_b"] - item["value_a"]
        for item in payload["configuration_differences"]
        if item["path"] == "neural.k_syn_mv_per_contact"
    )
    reverse_delta = next(
        item["value_b"] - item["value_a"]
        for item in reverse.to_dict()["configuration_differences"]
        if item["path"] == "neural.k_syn_mv_per_contact"
    )
    assert forward_delta == -reverse_delta
    assert low_path.is_dir() and high_path.is_dir()


def test_source_mismatch_is_preserved_as_summary_only(tmp_path, circuit_contract):
    config = _config(circuit_contract)
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
    store = ExperimentArtifactStore(tmp_path)
    first, second = store.discover_artifact_ids()
    payload = store.get_comparison(first, second).to_dict()
    assert payload["compatibility_class"] == "SUMMARY_ONLY_COMPARISON"
    assert payload["source_model_differences"]
    assert not payload["telemetry"]["dense_trajectory_comparable"]


def test_path_safety_rejects_traversal_and_symlink_escape(artifact_fixture, tmp_path):
    root, _path, _result = artifact_fixture
    store = ExperimentArtifactStore(root)
    with pytest.raises(InvalidArtifactIdError):
        store.get_experiment("../outside")
    with pytest.raises(InvalidArtifactIdError):
        store.get_experiment(str((tmp_path / "outside").resolve()))
    with pytest.raises(ArtifactNotFoundError):
        store.get_experiment("0" * 64)
    outside = tmp_path.parent / "phase4a-outside"
    outside.mkdir()
    try:
        (root / "escape").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")
    with pytest.raises(ArtifactPathError):
        store.list_experiments()


def test_corrupted_artifact_is_rejected_by_phase3b_loader(artifact_fixture):
    root, path, _result = artifact_fixture
    payload = bytearray((path / "telemetry.json").read_bytes())
    payload[len(payload) // 2] ^= 1
    (path / "telemetry.json").write_bytes(payload)
    store = ExperimentArtifactStore(root)
    with pytest.raises(CorruptedArtifactError):
        store.list_experiments()


def test_dto_conversion_does_not_execute_or_mutate_scientific_result(
    artifact_fixture, monkeypatch
):
    root, _path, result = artifact_fixture
    before = result.to_dict()

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("application API must not execute ExperimentRunner")

    monkeypatch.setattr(ExperimentRunner, "run", fail_if_called)
    store = ExperimentArtifactStore(root)
    artifact_id = store.discover_artifact_ids()[0]
    summary_payload = store.get_experiment(artifact_id).to_dict()
    summary_payload["free_parameters"]["k_syn_mv_per_contact"] = 999.0
    store.get_timeline(artifact_id)
    store.get_body_telemetry(artifact_id, 10001)
    store.get_events(artifact_id)
    assert result.to_dict() == before
