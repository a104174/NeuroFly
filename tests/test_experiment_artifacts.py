"""Offline tests for the Phase 3B portable experiment artifact contract."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

import neurofly.experiment_artifacts as artifacts
from neurofly.experiment_artifacts import (
    ArtifactExportError,
    ArtifactIntegrityError,
    ArtifactReplayError,
    ArtifactSchemaError,
    export_experiment_artifact,
    inspect_experiment_artifact,
    load_experiment_artifact,
    replay_experiment_artifact,
)
from neurofly.experiments import ExperimentConfig, ExperimentRunner, TelemetrySpec
from neurofly.malecns.contract import load_circuit_contract
from neurofly.malecns.sensory import LoomingStimulus, VisualPoint
from neurofly.sensory_encoder import LevelPEncoderConfig
from neurofly.simulation import LIFConfig


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


@pytest.fixture(scope="module")
def experiment_result(circuit_contract):
    # NEUROFLY_SYNTHETIC_BENCHMARK: artifact software fixture, not calibration.
    config = ExperimentConfig.from_contract(
        experiment_id="phase3b-artifact-test",
        circuit_contract=circuit_contract,
        stimulus=LoomingStimulus(
            object_radius_m=0.01,
            initial_distance_m=0.1,
            approach_velocity_m_s=1.0,
            center=VisualPoint(azimuth_rad=0.0, elevation_rad=0.0),
        ),
        duration_ms=20.0,
        encoder_config=LevelPEncoderConfig(
            lc4_gain_mv_eq=20.0,
            lplc2_gain_mv_eq=20.0,
            omega_half_rad_per_s=1.0,
            theta_half_rad=0.4,
        ),
        lif_config=LIFConfig(k_syn_mv_per_contact=0.01),
        telemetry=TelemetrySpec.validation_profile(selected_visual_body_ids=(12032,)),
    )
    return ExperimentRunner(circuit_contract).run(config)


@pytest.fixture()
def artifact_path(tmp_path, experiment_result):
    return export_experiment_artifact(experiment_result, tmp_path / "artifact")


def test_round_trip_preserves_result_and_all_free_parameters(
    artifact_path, experiment_result
):
    loaded = load_experiment_artifact(artifact_path)
    assert loaded.result.to_dict() == experiment_result.to_dict()
    assert loaded.result.result_sha256 == experiment_result.result_sha256
    assert loaded.config.encoder_config.lc4_gain_mv_eq == 20.0
    assert loaded.config.encoder_config.lplc2_gain_mv_eq == 20.0
    assert loaded.config.encoder_config.omega_half_rad_per_s == 1.0
    assert loaded.config.encoder_config.theta_half_rad == 0.4
    assert loaded.config.lif_config.k_syn_mv_per_contact == 0.01
    assert loaded.result.validation_status == "NOT_EVALUATED"
    assert [body.body_id for body in loaded.result.selected_body_telemetry] == [
        10001,
        10010,
        12032,
    ]


def test_manifest_inspection_is_offline_and_credential_free(artifact_path):
    inspection = inspect_experiment_artifact(artifact_path)
    assert inspection["artifact_schema_version"] == "experiment_artifact_v1"
    assert inspection["graph_scope_id"] == "direct_visual_to_dnp01_v1"
    assert inspection["telemetry_profile"]["profile_id"] == "VALIDATION_TELEMETRY_V1"
    assert inspection["validation_status"] == "NOT_EVALUATED"
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in artifact_path.iterdir()
    )
    assert "NEUPRINT_APPLICATION_CREDENTIALS" not in text


@pytest.mark.parametrize(
    "filename",
    [
        artifacts.TELEMETRY_FILENAME,
        artifacts.SPIKES_FILENAME,
        artifacts.DELIVERED_EVENTS_FILENAME,
        artifacts.SUMMARY_FILENAME,
    ],
)
def test_one_byte_payload_corruption_is_rejected(artifact_path, filename):
    target = artifact_path / filename
    payload = bytearray(target.read_bytes())
    index = len(payload) // 2
    payload[index] ^= 1
    target.write_bytes(payload)
    with pytest.raises(ArtifactIntegrityError):
        load_experiment_artifact(artifact_path)


def test_missing_payload_is_rejected(artifact_path):
    (artifact_path / artifacts.SUMMARY_FILENAME).unlink()
    with pytest.raises(ArtifactIntegrityError, match="files differ|missing"):
        load_experiment_artifact(artifact_path)


def test_existing_artifact_is_never_overwritten(artifact_path, experiment_result):
    with pytest.raises(ArtifactExportError, match="already exists"):
        export_experiment_artifact(experiment_result, artifact_path)


def test_scientific_config_change_changes_artifact_identity(
    tmp_path, circuit_contract, experiment_result
):
    changed_config = replace(
        experiment_result.config,
        lif_config=replace(
            experiment_result.config.lif_config, k_syn_mv_per_contact=0.02
        ),
    )
    changed_result = ExperimentRunner(circuit_contract).run(changed_config)
    first_path = export_experiment_artifact(experiment_result, tmp_path / "first")
    second_path = export_experiment_artifact(changed_result, tmp_path / "second")
    first = load_experiment_artifact(first_path)
    second = load_experiment_artifact(second_path)
    assert first.result.config_sha256 != second.result.config_sha256
    assert first.artifact_id != second.artifact_id
    assert first.config.lif_config.k_syn_mv_per_contact == 0.01
    assert second.config.lif_config.k_syn_mv_per_contact == 0.02


def test_replay_passes_and_source_mismatch_reports_failure(
    artifact_path, circuit_contract
):
    replayed = replay_experiment_artifact(artifact_path, circuit_contract)
    loaded = load_experiment_artifact(artifact_path)
    assert replayed.result_sha256 == loaded.result.result_sha256
    mismatched = replace(
        circuit_contract, candidate=replace(circuit_contract.candidate, version=999)
    )
    with pytest.raises(ArtifactReplayError):
        replay_experiment_artifact(artifact_path, mismatched)


def test_atomic_export_does_not_finalize_after_write_failure(
    tmp_path, experiment_result, monkeypatch
):
    destination = tmp_path / "failed-artifact"

    def fail_write(*args, **kwargs):
        raise OSError("synthetic write failure")

    monkeypatch.setattr(artifacts, "_write_json", fail_write)
    with pytest.raises(ArtifactExportError):
        export_experiment_artifact(experiment_result, destination)
    assert not destination.exists()
    assert not list(tmp_path.glob(".failed-artifact.*"))


def test_summary_and_event_semantics_are_explicit(artifact_path):
    loaded = load_experiment_artifact(artifact_path)
    assert loaded.result.delivered_events
    assert all(
        event.target_body_id in {10001, 10010}
        for event in loaded.result.delivered_events
    )
    assert all(event.structural_weight > 0 for event in loaded.result.delivered_events)
    assert all(event.model_sign == 1 for event in loaded.result.delivered_events)
    assert all(
        event.event_increment_mV_eq
        == event.structural_weight * loaded.config.lif_config.k_syn_mv_per_contact
        for event in loaded.result.delivered_events
    )
    assert len(loaded.result.delivered_event_summaries) == 2


def test_schema_and_manifest_mutations_are_rejected(artifact_path):
    manifest_path = artifact_path / artifacts.MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["validation_status"] = "VALIDATED"
    # Recompute only the manifest checksum: the semantic status is still forbidden.
    manifest_without_digest = dict(manifest)
    manifest_without_digest.pop("manifest_sha256")
    manifest["manifest_sha256"] = artifacts._sha256_bytes(
        artifacts._json_bytes(manifest_without_digest)
    )
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ArtifactSchemaError, match="validation status"):
        load_experiment_artifact(artifact_path)


def test_config_mutation_is_rejected_even_with_rehashed_manifest(artifact_path):
    manifest_path = artifact_path / artifacts.MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["config"]["duration_ms"] = 10.0
    manifest_without_digest = dict(manifest)
    manifest_without_digest.pop("manifest_sha256")
    manifest["manifest_sha256"] = artifacts._sha256_bytes(
        artifacts._json_bytes(manifest_without_digest)
    )
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ArtifactIntegrityError, match="config SHA-256"):
        load_experiment_artifact(artifact_path)
