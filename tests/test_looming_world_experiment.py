"""Frozen design, observational outcomes and deterministic domain termination."""

import copy
import math
import socket

import pytest

import neurofly.closed_loop_scenario as scenario
import neurofly.looming_world_experiment as world
from neurofly.looming_world_experiment_artifacts import (
    generate_world_artifact,
    replay_world_artifact,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)


@pytest.fixture(scope="module")
def sources():
    return scenario.load_scenario_sources()


@pytest.fixture(scope="module")
def run(sources):
    return world.run_world_experiment(sources)


def test_frozen_config_derived_from_contract_and_no_targeting(tmp_path):
    contract = world.load_preregistration()
    assert canonical_sha256(contract) == world.PREREGISTRATION_ID
    config = world.WorldExperimentConfig()
    payload = config.payload()
    assert payload["preregistration"] == contract
    assert config.interval_count * config.dt_ms == contract["duration_ms"]
    assert payload["projection"] == contract["projection"]
    assert payload["object"] == contract["object"]
    assert config.payload() == payload
    for key in (
        "target_spikes",
        "target_movement",
        "desired_displacement",
        "target_threshold_crossing",
    ):
        with pytest.raises(TypeError):
            world.WorldExperimentConfig(**{key: 1})
    mutated = copy.deepcopy(contract)
    mutated["duration_ms"] = 80
    path = tmp_path / "tampered.json"
    path.write_bytes(canonical_json_bytes(mutated))
    with pytest.raises(ValueError, match="preregistration"):
        world.load_preregistration(path)


def test_geometry_only_reference_proof_and_feedback(sources):
    config = world.WorldExperimentConfig()
    for n in range(config.interval_count + 1):
        obj = (
            0,
            config.object_z_world_eq + n * config.dt_ms * config.vz_world_eq_per_ms,
        )
        assert world.geometry_termination(config, (0, 0), obj, n) is None
        g, _, _ = scenario.exposure_vector(config, (0, 0), obj, sources)
        assert 2 <= g["lattice_radius"] <= 4
        assert g["relative_z_world_eq"] >= 2
        assert math.isfinite(g["half_angle"])
    obj = (0, 1 / math.tan(0.3) + 0.005)
    before, _, a = scenario.exposure_vector(config, (0, 0), obj, sources)
    after, _, b = scenario.exposure_vector(config, (0, 0.01), obj, sources)
    assert before["relative_distance_world_eq"] != after["relative_distance_world_eq"]
    assert before["lattice_radius"] != after["lattice_radius"]
    assert a != b
    invalid = world.geometry_termination(config, (0, 3), (0, 4), 1)
    assert invalid["status"] == "TERMINATED_GEOMETRY_DOMAIN"
    assert invalid == world.geometry_termination(config, (0, 3), (0, 4), 1)


def test_runner_stops_before_exposure_without_padding(sources, monkeypatch):
    # TEST_ONLY_NONCANONICAL artificial authoritative update; never artifact input.
    monkeypatch.setattr(scenario, "body_interval_step", lambda *args: (0, 10))
    r = world.run_world_experiment(sources)["result"]
    assert r["termination"]["step"] == 1
    assert r["termination"]["status"] == "TERMINATED_GEOMETRY_DOMAIN"
    assert r["termination"]["attempted_boundary_state"]["body"]["z_world_eq"] == 10
    assert len(r["time_ms"]) == len(r["sensory_state_by_boundary"]) == 1
    assert len(r["body_intervals"]) == 1
    assert not r["statuses"]["closed_loop_execution_completed"]
    assert r["statuses"]["body_movement_occurred"]


def test_observational_outcome_and_causal_accounting(run, sources):
    r = run["result"]
    assert r["termination"]["status"] == "COMPLETED_VALID_HORIZON"
    assert len(r["time_ms"]) == 401 and len(r["body_intervals"]) == 400
    assert r["time_ms"][-1] == 40
    assert len(r["sensory_identities"]) == 311
    assert r["sensory_identities"] == list(sources["rows"])
    for n, (b, t, states, exposure) in enumerate(
        zip(
            r["world_body"],
            r["telemetry"],
            r["sensory_state_by_boundary"],
            r["exposure_by_boundary"],
            strict=True,
        )
    ):
        assert len(states) == len(exposure) == 311
        assert (
            b["geometry"]["relative_z_world_eq"]
            == b["object_z_world_eq"] - b["z_world_eq"]
        )
        assert b["geometry"]["relative_z_world_eq"] > 1
        assert t["body"]["z_world_eq"] == b["z_world_eq"]
        assert b["x_world_eq"] == 0
        if n:
            interval = r["body_intervals"][n - 1]
            assert b["z_world_eq"] == pytest.approx(
                r["world_body"][n - 1]["z_world_eq"]
                + (n * 0.1 - (n - 1) * 0.1) * interval["forward_speed_world_eq_per_ms"]
            )
    # No spike/movement quota: statuses must describe actual genuine outputs.
    commands = [s["actuator_commands"] for s in r["downstream_state_by_boundary"]]
    assert r["statuses"]["genuine_nonzero_actuation_occurred"] == any(
        any(v > 0 for v in c.values()) for c in commands
    )
    assert r["statuses"]["body_movement_occurred"] == any(
        b["z_world_eq"] != 0 for b in r["world_body"]
    )
    assert r["statuses"]["environment_affected_sensory_input"]
    assert r["dnp01_drive_by_interval"][0] == [0, 0]
    # Structural counts do not enter additive model contributions.
    for ledger in r["source_contributions_by_interval"]:
        assert "weight" not in str(ledger)


@pytest.fixture
def artifact(run, monkeypatch):
    ch, rh = canonical_sha256(run["config"]), canonical_sha256(run["result"])
    payload = {
        "schema_version": world.ARTIFACT_SCHEMA,
        "config": run["config"],
        "result": run["result"],
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256([world.ARTIFACT_SCHEMA, ch, rh]),
    }
    # Full source validation already occurred; reuse the deterministic run for
    # file-integrity mutation tests rather than repeating historical replay.
    monkeypatch.setattr(world, "build_world_experiment", lambda: payload)
    return payload


@pytest.mark.parametrize(
    "mutation",
    [
        "preregistration",
        "duration",
        "trajectory",
        "model",
        "telemetry",
        "hash",
        "termination",
        "identity",
    ],
)
def test_tamper_rejection_even_with_rehashed_payload(artifact, mutation):
    p = copy.deepcopy(artifact)
    if mutation == "preregistration":
        p["config"]["scenario"]["preregistration_id"] = "forged"
    elif mutation == "duration":
        p["config"]["scenario"]["interval_count"] = 800
    elif mutation == "trajectory":
        p["config"]["scenario"]["object"]["vz_world_eq_per_ms"] = -1
    elif mutation == "model":
        p["config"]["sources"]["lif_model"]["threshold_mv"] = 0
    elif mutation == "telemetry":
        p["result"]["telemetry"][1]["body"]["z_world_eq"] = 1
    elif mutation == "termination":
        p["result"]["termination"]["status"] = "TERMINATED_GEOMETRY_DOMAIN"
    elif mutation == "hash":
        p["result_sha256"] = "forged"
    else:
        p["artifact_id"] = "forged"
    with pytest.raises(ValueError):
        world.validate_world_experiment(p)
    p["config_sha256"], p["result_sha256"] = (
        canonical_sha256(p["config"]),
        canonical_sha256(p["result"]),
    )
    p["artifact_id"] = canonical_sha256(
        [world.ARTIFACT_SCHEMA, p["config_sha256"], p["result_sha256"]]
    )
    if mutation not in ("hash", "identity"):
        with pytest.raises(ValueError):
            world.validate_world_experiment(p)


def test_offline_artifact_bytes_reset_and_manifest(artifact, tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "create_connection", no_network)
    path = generate_world_artifact(output_root=tmp_path)
    assert replay_world_artifact(path) == artifact
    raw = (path / "experiment.json").read_bytes()
    assert raw == canonical_json_bytes(artifact, newline=True)
    assert generate_world_artifact(output_root=tmp_path) == path
    assert (path / "experiment.json").read_bytes() == raw
    (path / "manifest.json").write_bytes(b"{}\n")
    with pytest.raises(ValueError):
        replay_world_artifact(path)
