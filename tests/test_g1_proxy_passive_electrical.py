"""Phase 9B equation, source composition, no-calibration and replay gates."""

from __future__ import annotations

import copy
import json
import math
import shutil
import socket
from dataclasses import replace

import pytest

from neurofly.g1_proxy_passive_electrical import (
    FIXTURE_IDS,
    PROXY_DOMAIN_ID,
    PassiveConfig,
    build_response,
    integrate_counts,
    reference_config,
    validate_response,
)
from neurofly.g1_proxy_passive_electrical_artifacts import (
    generate_response_artifact,
    replay_response_artifact,
)
from neurofly.g1_proxy_passive_electrical_cli import main
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_observation_mapping_artifacts import replay_ttm_g1_mapping_artifact
from neurofly.ttm_g1_proxy_mapping import DEFAULT_SOURCE_PATHS


@pytest.fixture(scope="module")
def response():
    return build_response(reference_config())


def instance(response, fixture, body=800146):
    row = next(f for f in response["result"]["fixtures"] if f["fixture_id"] == fixture)
    return next(i for i in row["instances"] if i["source_body_id"] == body)


def test_accounting_and_identity(response):
    assert tuple(f["fixture_id"] for f in response["result"]["fixtures"]) == FIXTURE_IDS
    assert response["result"]["source_token_count"] == 8
    assert response["result"]["instance_count"] == 12
    totals = {800146: 0, 804642: 0}
    identities = set()
    for f in response["result"]["fixtures"]:
        assert [i["source_body_id"] for i in f["instances"]] == [800146, 804642]
        for i in f["instances"]:
            totals[i["source_body_id"]] += sum(i["token_count"])
            identities.add(i["instance_id"])
            assert i["proxy_domain_id"] == PROXY_DOMAIN_ID
            assert len(i["voltage_deviation_mV_eq"]) == 81
    assert totals == {800146: 4, 804642: 4}
    assert len(identities) == 12


def test_zero_and_inactive_sides(response):
    for body in (800146, 804642):
        zero = instance(response, "ZERO_EVENT_CONTROL", body)
        assert zero["voltage_deviation_mV_eq"] == [0.0] * 81
        assert zero["proxy_voltage_mV_eq"] == [0.0] * 81
    assert instance(response, "RIGHT_SINGLE_EVENT", 804642)["token_count"] == [0] * 81
    assert (
        instance(response, "LEFT_SINGLE_EVENT", 800146)["voltage_deviation_mV_eq"]
        == [0.0] * 81
    )


@pytest.mark.parametrize(
    "fixture,body", [("RIGHT_SINGLE_EVENT", 800146), ("LEFT_SINGLE_EVENT", 804642)]
)
def test_single_closed_form_and_timing(response, fixture, body):
    row = instance(response, fixture, body)
    u = row["voltage_deviation_mV_eq"]
    assert u[:10] == [0.0] * 10
    assert u[10] == 2.0
    alpha = math.exp(-0.1)
    assert u[10:] == pytest.approx([2 * alpha**k for k in range(71)], rel=1e-14)
    assert all(a > b > 0 for a, b in zip(u[10:-1], u[11:], strict=True))
    assert response["result"]["time_ms"][10] == 1.0
    assert [n for n, c in enumerate(row["token_count"]) if c] == [10]


def test_bilateral_independent_states(response):
    r = instance(response, "BILATERAL_SIMULTANEOUS_EVENT")
    left = instance(response, "BILATERAL_SIMULTANEOUS_EVENT", 804642)
    assert r["instance_id"] != left["instance_id"]
    assert r["source_token_ids"] != left["source_token_ids"]
    assert r["voltage_deviation_mV_eq"] == left["voltage_deviation_mV_eq"]
    assert r["voltage_deviation_mV_eq"] is not left["voltage_deviation_mV_eq"]
    assert (
        r["voltage_deviation_mV_eq"]
        == instance(response, "RIGHT_SINGLE_EVENT")["voltage_deviation_mV_eq"]
    )


@pytest.mark.parametrize(
    "fixture,body",
    [("RIGHT_REPEATED_EVENTS", 800146), ("LEFT_REPEATED_EVENTS", 804642)],
)
def test_repeated_superposition(response, fixture, body):
    row = instance(response, fixture, body)
    u = row["voltage_deviation_mV_eq"]
    alpha = math.exp(-0.1)
    expected = [
        sum(2 * alpha ** (n - e) for e in (10, 30) if n >= e) for n in range(81)
    ]
    assert u == pytest.approx(expected, rel=1e-14)
    assert u[30] == pytest.approx(alpha * u[29] + 2)
    assert u[30] > u[10]
    assert row["summary"]["peak_boundary"] == 30
    assert response["result"]["time_ms"][30] == 3.0


def test_zero_boundary_and_multiplicity():
    counts = [0] * 81
    counts[0] = 2
    output = integrate_counts(reference_config(), counts)
    assert output["voltage_deviation_mV_eq"][0] == 4.0
    assert output["voltage_deviation_mV_eq"][1] == math.exp(-0.1) * 4


def test_equation_level_sensitivity():
    c = reference_config()
    counts = [0] * 81
    counts[10] = 1
    base = integrate_counts(c, counts)["voltage_deviation_mV_eq"]
    double = integrate_counts(replace(c, event_scale_effective_mV_eq=4), counts)[
        "voltage_deviation_mV_eq"
    ]
    slow = integrate_counts(replace(c, tau_effective_ms=2), counts)[
        "voltage_deviation_mV_eq"
    ]
    assert double == [2 * v for v in base]
    assert slow[10] == base[10]
    assert slow[11] > base[11]


@pytest.mark.parametrize(
    "field,value",
    [
        ("dt_ms", 0),
        ("dt_ms", -1),
        ("dt_ms", float("nan")),
        ("tau_effective_ms", 0),
        ("tau_effective_ms", -1),
        ("tau_effective_ms", float("inf")),
        ("event_scale_effective_mV_eq", 0),
        ("event_scale_effective_mV_eq", -1),
        ("reference_voltage_mV_eq", float("nan")),
        ("reference_voltage_mV_eq", True),
        ("interval_count", 0),
        ("interval_count", 80.0),
        ("interval_count", True),
        ("proxy_domain_id", "physical-g1-left"),
    ],
)
def test_invalid_config(field, value):
    with pytest.raises(ValueError):
        replace(reference_config(), **{field: value})


def test_config_strict_semantics_and_grid():
    c = reference_config()
    assert PassiveConfig.from_payload(c.payload()) == c
    for field, value in [
        ("duration_ms", 9),
        ("event_order", "INPUT_THEN_DECAY"),
        ("current_pA", 1),
        ("timing_assumption", "MEASURED_ZERO_DELAY"),
    ]:
        payload = c.payload()
        payload[field] = value
        with pytest.raises(ValueError):
            PassiveConfig.from_payload(payload)
    with pytest.raises(ValueError):
        build_response(replace(c, dt_ms=0.2))
    assert replace(c, reference_voltage_mV_eq=-60).reference_voltage_mV_eq == -60


@pytest.mark.parametrize(
    "counts", [[0], [0] * 80 + [True], [0] * 80 + [-1], [0] * 80 + [0.5]]
)
def test_invalid_counts(counts):
    with pytest.raises(ValueError):
        integrate_counts(reference_config(), counts)


def test_no_observation_parameterization_and_readiness(response):
    c = reference_config().payload()
    assert (
        c["reference_voltage_mV_eq"],
        c["tau_effective_ms"],
        c["event_scale_effective_mV_eq"],
    ) == (0, 1, 2)
    assert set(c["parameter_classifications"].values()) == {"MODEL_ASSUMPTION"}
    forbidden = (
        "current_pA",
        "conductance_nS",
        "release_probability",
        "quantal_count",
        "nmj_delay_ms",
        "model_threshold",
    )
    assert all(
        name not in canonical_json_bytes(response).decode() for name in forbidden
    )
    u = replay_ttm_g1_mapping_artifact(DEFAULT_SOURCE_PATHS["phase8u"])
    assert u.contract["result"]["formal_ready_mapping_count"] == 0


@pytest.mark.parametrize(
    "path,value",
    [
        (("config", "sources", "phase8w", "artifact_id"), "wrong"),
        (("config", "sources", "phase8y", "artifact_id"), "wrong"),
        (("config", "model", "proxy_domain_id"), "physical-g1"),
        (("config", "model", "event_scale_effective_mV_eq"), 3.0),
        (("config", "model", "event_order"), "WRONG"),
        (
            ("result", "fixtures", 1, "instances", 0, "voltage_deviation_mV_eq", 10),
            45.0,
        ),
        (("result", "fixtures", 1, "instances", 0, "token_count", 10), 2),
        (
            ("result", "fixtures", 1, "instances", 0, "source_token_ids", 0),
            "fabricated",
        ),
        (("result", "fixtures", 1, "fixture_id"), "OTHER"),
        (("result", "fixtures", 1, "instances", 0, "source_body_id"), 804642),
        (("result_sha256",), "wrong"),
        (("artifact_id",), "wrong"),
    ],
)
def test_tamper_rejection(response, path, value):
    bad = copy.deepcopy(response)
    node = bad
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    with pytest.raises(ValueError):
        validate_response(bad)


def test_content_identity(response):
    assert response["artifact_id"] == (
        "72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f"
    )
    assert response["config_sha256"] == (
        "d3807d88f777e8f6754a8e3aab591e42b643974e7417451509771581d7c013d0"
    )
    assert response["result_sha256"] == (
        "fa11b093b1a3013d397bb459c3c1f39b1a96543b8380a792e89dc0bdfa8e91d8"
    )
    assert build_response(reference_config()) == response
    for config in (
        replace(reference_config(), reference_voltage_mV_eq=-1),
        replace(reference_config(), tau_effective_ms=2),
        replace(reference_config(), event_scale_effective_mV_eq=3),
    ):
        changed = build_response(config)
        assert changed["config_sha256"] != response["config_sha256"]
        assert changed["artifact_id"] != response["artifact_id"]


def test_rehashed_trajectory_tamper(response):
    bad = copy.deepcopy(response)
    bad["result"]["fixtures"][1]["instances"][0]["voltage_deviation_mV_eq"][11] = 1.0
    bad["result_sha256"] = canonical_sha256(bad["result"])
    bad["artifact_id"] = canonical_sha256(
        [
            "g1_proxy_passive_electrical_response_artifact_v1",
            bad["config_sha256"],
            bad["result_sha256"],
        ]
    )
    with pytest.raises(ValueError):
        validate_response(bad)


def test_source_schedule_tamper_fails_child_replay(tmp_path):
    source = DEFAULT_SOURCE_PATHS["phase8w"]
    destination = tmp_path / source.name
    shutil.copytree(source, destination)
    payload = json.loads((destination / "input_contract.json").read_bytes())
    payload["result"]["fixtures"][1]["tokens"][0]["step"] = 11
    (destination / "input_contract.json").write_bytes(
        canonical_json_bytes(payload, newline=True)
    )
    with pytest.raises(ValueError):
        build_response(reference_config(), input_artifact=destination)


def test_offline_byte_replay_cli_and_file_tamper(tmp_path, monkeypatch, capsys):
    def no_network(*args, **kwargs):
        raise AssertionError("network forbidden")

    monkeypatch.setattr(socket, "create_connection", no_network)
    path = generate_response_artifact(reference_config(), output_root=tmp_path)
    original = {p.name: p.read_bytes() for p in path.iterdir()}
    assert replay_response_artifact(path)["result"]["source_token_count"] == 8
    assert generate_response_artifact(reference_config(), output_root=tmp_path) == path
    assert {p.name: p.read_bytes() for p in path.iterdir()} == original
    for command in ("inspect", "replay"):
        assert main([command, str(path)]) == 0
        assert json.loads(capsys.readouterr().out)["reference_config"] is True
    assert main(["generate", "--output-root", str(tmp_path)]) == 0
    capsys.readouterr()
    (path / "response.json").write_bytes(original["response.json"] + b" ")
    with pytest.raises(ValueError):
        replay_response_artifact(path)
    assert main(["replay", str(path)]) == 2
