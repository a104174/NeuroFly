"""Model-space extraction, not physiological validation."""

from __future__ import annotations

import copy
import json
import socket
from dataclasses import replace

import pytest

from neurofly import g1_proxy_passive_electrical as model
from neurofly.g1_proxy_passive_electrical_artifacts import replay_response_artifact
from neurofly.g1_proxy_peak_deflection import (
    ARTIFACT_SCHEMA,
    CONTROL_KIND,
    DEFAULT_SOURCE_ARTIFACT,
    EXCLUDED_FIXTURES,
    PEAK_KIND,
    SOURCE_ID,
    SUPPORTED_FIXTURES,
    build_observations,
    extract_trajectory,
    operator_config,
    validate_observations,
)
from neurofly.g1_proxy_peak_deflection_artifacts import (
    generate_observation_artifact,
    replay_observation_artifact,
)
from neurofly.g1_proxy_peak_deflection_cli import main
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_observation_mapping_artifacts import replay_ttm_g1_mapping_artifact
from neurofly.ttm_g1_proxy_mapping import DEFAULT_SOURCE_PATHS


@pytest.fixture(scope="module")
def source():
    return replay_response_artifact(DEFAULT_SOURCE_ARTIFACT)


@pytest.fixture(scope="module")
def observations():
    return build_observations()


def row(source, fixture="RIGHT_SINGLE_EVENT", body=800146):
    fixture = next(
        f for f in source["result"]["fixtures"] if f["fixture_id"] == fixture
    )
    return next(i for i in fixture["instances"] if i["source_body_id"] == body)


def rehash_source(source):
    source["result_sha256"] = canonical_sha256(source["result"])
    source["artifact_id"] = canonical_sha256(
        [model.ARTIFACT_SCHEMA, source["config_sha256"], source["result_sha256"]]
    )


def test_exact_accounting_order_and_units(observations):
    records = observations["result"]["records"]
    assert len(records) == 8
    assert observations["result"]["isolated_event_result_count"] == 4
    assert observations["result"]["baseline_control_result_count"] == 4
    assert [(r["source_fixture_id"], r["source_body_id"]) for r in records] == [
        (f, b) for f in SUPPORTED_FIXTURES for b in (800146, 804642)
    ]
    assert len({r["result_id"] for r in records}) == 8
    assert {r["units"] for r in records} == {"mV_eq"}
    assert {r["protocol_match_status"] for r in records} == {"NOT_EVALUATED"}
    assert [
        f["fixture_id"] for f in observations["result"]["excluded_fixtures"]
    ] == list(EXCLUDED_FIXTURES)
    for r in records:
        assert r["source_phase9b_artifact_id"] == SOURCE_ID
        assert r["provenance_chain"][-1] == "EXPLORATORY_MODEL_SPACE_OBSERVATION"
        assert r["result_id"] == canonical_sha256(
            {k: v for k, v in r.items() if k != "result_id"}
        )
        assert (
            not {
                "empirical_value",
                "target_value",
                "error",
                "residual",
                "peak_mV",
                "voltage_mV",
            }
            & r.keys()
        )


@pytest.mark.parametrize(
    "fixture,body",
    [
        ("RIGHT_SINGLE_EVENT", 800146),
        ("LEFT_SINGLE_EVENT", 804642),
        ("BILATERAL_SIMULTANEOUS_EVENT", 800146),
        ("BILATERAL_SIMULTANEOUS_EVENT", 804642),
    ],
)
def test_isolated_peak(source, fixture, body):
    r = extract_trajectory(source, fixture, body, result_kind=PEAK_KIND)
    assert r["event_step"] == r["peak_step"] == 10
    assert r["event_time_ms"] == r["peak_time_ms"] == 1.0
    assert r["baseline_step"] == 9
    assert r["baseline_time_ms"] == 0.9
    assert r["baseline_proxy_voltage_mV_eq"] == 0
    assert r["peak_proxy_voltage_mV_eq"] == r["peak_deflection_mV_eq"] == 2
    assert (r["window_start_step"], r["window_end_step"]) == (10, 80)
    assert (r["window_start_time_ms"], r["window_end_time_ms"]) == (1, 8)
    assert (
        r["source_phase8w_token_id"]
        == row(source, fixture, body)["source_token_ids"][0]
    )
    assert r["neural_side"] == {800146: "R", 804642: "L"}[body]


def test_controls_have_no_evoked_fields(observations):
    controls = [
        r for r in observations["result"]["records"] if r["result_kind"] == CONTROL_KIND
    ]
    assert len(controls) == 4
    for r in controls:
        assert r["baseline_stable"] is True
        assert r["max_abs_deviation_mV_eq"] == 0
        assert r["baseline_proxy_voltage_mV_eq"] == 0
        assert (
            not {
                "event_step",
                "source_phase8w_token_id",
                "peak_deflection_mV_eq",
                "peak_step",
            }
            & r.keys()
        )


def test_bilateral_distinct_results(source):
    results = [
        extract_trajectory(source, "BILATERAL_SIMULTANEOUS_EVENT", b)
        for b in (800146, 804642)
    ]
    assert results[0]["result_id"] != results[1]["result_id"]
    assert results[0]["source_trajectory_id"] != results[1]["source_trajectory_id"]
    assert (
        results[0]["source_phase8w_token_id"] != results[1]["source_phase8w_token_id"]
    )


@pytest.mark.parametrize("fixture", EXCLUDED_FIXTURES)
@pytest.mark.parametrize("body", [800146, 804642])
def test_repeated_fixture_rejected_even_inactive(source, fixture, body):
    with pytest.raises(ValueError, match="unsupported fixture"):
        extract_trajectory(source, fixture, body)


@pytest.mark.parametrize(
    "fixture,kind",
    [("ZERO_EVENT_CONTROL", PEAK_KIND), ("RIGHT_SINGLE_EVENT", CONTROL_KIND)],
)
def test_wrong_kind(source, fixture, kind):
    with pytest.raises(ValueError, match="result kind"):
        extract_trajectory(source, fixture, 800146, result_kind=kind)


def test_boundary_zero_and_multiple_tokens_rejected(source):
    for boundary in (0, 20):
        changed = copy.deepcopy(source)
        r = row(changed)
        r["token_count"][boundary] = 1
        if boundary == 0:
            r["token_count"][10] = 0
        else:
            r["source_token_ids"].append("second-token")
        rehash_source(changed)
        with pytest.raises(ValueError, match="zero|exactly one"):
            extract_trajectory(changed, "RIGHT_SINGLE_EVENT", 800146)


@pytest.mark.parametrize(
    "reference,scale,tau", [(7, 2, 1), (-60, 2, 1), (0, 4, 1), (0, 2, 2)]
)
def test_coordinate_scale_tau_regressions(reference, scale, tau, monkeypatch):
    local = model.build_response(
        replace(
            model.reference_config(),
            reference_voltage_mV_eq=reference,
            event_scale_effective_mV_eq=scale,
            tau_effective_ms=tau,
        )
    )

    def no_simulation(*args, **kwargs):
        raise AssertionError("extractor must not simulate")

    monkeypatch.setattr(model, "integrate_counts", no_simulation)
    result = extract_trajectory(local, "RIGHT_SINGLE_EVENT", 800146)
    assert result["baseline_proxy_voltage_mV_eq"] == reference
    assert result["peak_proxy_voltage_mV_eq"] == reference + scale
    assert result["peak_deflection_mV_eq"] == scale
    assert result["peak_step"] == 10


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_side", "L"),
        ("proxy_domain_id", "physical-g1"),
        ("instance_id", "wrong"),
        ("config_id", "wrong"),
        ("provenance_chain", ["EMPIRICAL"]),
    ],
)
def test_source_identity_rejected(source, field, value):
    changed = copy.deepcopy(source)
    row(changed)[field] = value
    rehash_source(changed)
    with pytest.raises(ValueError):
        extract_trajectory(changed, "RIGHT_SINGLE_EVENT", 800146)


def test_time_grid_and_nonfinite_rejected(source):
    changed = copy.deepcopy(source)
    changed["result"]["time_ms"][10] = 1.01
    rehash_source(changed)
    with pytest.raises(ValueError, match="grid"):
        extract_trajectory(changed, "RIGHT_SINGLE_EVENT", 800146)
    changed = copy.deepcopy(source)
    row(changed)["proxy_voltage_mV_eq"][10] = float("inf")
    with pytest.raises(ValueError):
        extract_trajectory(changed, "RIGHT_SINGLE_EVENT", 800146)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_phase9b_artifact_id", "wrong"),
        ("source_trajectory_id", "wrong"),
        ("source_phase8w_token_id", "wrong"),
        ("event_step", 11),
        ("event_time_ms", 1.1),
        ("baseline_semantics", "RESTING_POTENTIAL"),
        ("baseline_proxy_voltage_mV_eq", 1),
        ("window_semantics", "EXPERIMENTAL"),
        ("peak_proxy_voltage_mV_eq", 3),
        ("peak_step", 11),
        ("peak_time_ms", 1.1),
        ("unit_semantics", "BIOLOGICAL_MV"),
        ("result_kind", CONTROL_KIND),
    ],
)
def test_semantic_tampering_rejected_even_rehashed(observations, field, value):
    changed = copy.deepcopy(observations)
    peak = next(
        r for r in changed["result"]["records"] if r["result_kind"] == PEAK_KIND
    )
    peak[field] = value
    peak["result_id"] = canonical_sha256(
        {k: v for k, v in peak.items() if k != "result_id"}
    )
    changed["result_sha256"] = canonical_sha256(changed["result"])
    changed["artifact_id"] = canonical_sha256(
        [ARTIFACT_SCHEMA, changed["config_sha256"], changed["result_sha256"]]
    )
    with pytest.raises(ValueError, match="offline extraction"):
        validate_observations(changed)


def test_operator_and_hash_tampering(observations):
    for field in ("baseline_semantics", "window_semantics", "unit_semantics"):
        changed = copy.deepcopy(observations)
        changed["config"]["operator"][field] = "WRONG"
        with pytest.raises(ValueError):
            validate_observations(changed)
    changed = copy.deepcopy(observations)
    changed["result_sha256"] = "wrong"
    with pytest.raises(ValueError):
        validate_observations(changed)


def test_offline_byte_replay_cli_and_tamper(
    tmp_path, monkeypatch, capsys, observations
):
    def no_network(*args, **kwargs):
        raise AssertionError("offline replay")

    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.setattr(socket.socket, "connect", no_network)
    path = generate_observation_artifact(output_root=tmp_path)
    before = {p.name: p.read_bytes() for p in path.iterdir()}
    assert generate_observation_artifact(output_root=tmp_path) == path
    assert replay_observation_artifact(path) == observations
    assert before == {p.name: p.read_bytes() for p in path.iterdir()}
    for command in ("inspect", "replay"):
        assert main([command, str(path)]) == 0
        assert (
            json.loads(capsys.readouterr().out)["operation"]
            == "MODEL_SPACE_EXTRACTION_NOT_EMPIRICAL_VALIDATION"
        )
    assert main(["generate", "--output-root", str(tmp_path)]) == 0
    capsys.readouterr()
    assert main(["replay", str(tmp_path / "missing")]) == 2
    capsys.readouterr()
    # Intentional test-local artifact tamper, not a repository file edit.
    (path / "manifest.json").write_bytes(canonical_json_bytes({}, newline=True))
    with pytest.raises(ValueError):
        replay_observation_artifact(path)


def test_historical_zero_ready_and_source_identity(source):
    assert source["artifact_id"] == SOURCE_ID
    mapping = replay_ttm_g1_mapping_artifact(DEFAULT_SOURCE_PATHS["phase8u"])
    assert mapping.contract["result"]["formal_ready_mapping_count"] == 0
    assert operator_config()["supported_token_counts"] == [0, 1]


def test_pinned_deterministic_identities(observations):
    assert observations["config"]["operator_id"] == (
        "7a9cbf8f4341382757a118f3485780a1f49c6f810a5151f35112eb60286b1e19"
    )
    assert observations["artifact_id"] == (
        "2c775d6e00d74b3b3a3ca5a36bb84fd4032959d29f3c7d4c8b0bca934e2942b8"
    )
    assert observations["config_sha256"] == (
        "44be1b554dafc1c867f92ff1c50100157aa0787ea04cf2480e390cc7f0a778ca"
    )
    assert observations["result_sha256"] == (
        "766b98a29bd6343f3ba633cfa5a9de900f697ff93be8ac89da3f083e1325dba9"
    )


def test_source_artifact_mutation_rejected(tmp_path, source):
    from neurofly.g1_proxy_passive_electrical_artifacts import _manifest

    changed = copy.deepcopy(source)
    row(changed)["token_count"][10] = 0
    row(changed)["token_count"][11] = 1
    rehash_source(changed)
    path = tmp_path / changed["artifact_id"]
    path.mkdir()
    for name, payload in (
        ("response.json", changed),
        ("manifest.json", _manifest(changed)),
    ):
        (path / name).write_bytes(canonical_json_bytes(payload, newline=True))
    with pytest.raises(ValueError):
        build_observations(source_artifact=path)
