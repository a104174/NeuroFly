"""Phase 10B software/model checks, not biological activation validation."""

import copy
import json
import math
import socket
from dataclasses import replace

import pytest

from neurofly import g1_proxy_passive_electrical as electrical
from neurofly.g1_proxy_passive_electrical_artifacts import replay_response_artifact
from neurofly.muscle_activation import (
    ARTIFACT_SCHEMA,
    DEFAULT_MODEL_ARTIFACT,
    SOURCE_ID,
    ActivationConfig,
    activate_samples,
    build_activation,
    reference_config,
    transform_response,
    validate_activation,
)
from neurofly.muscle_activation_artifacts import (
    generate_activation_artifact,
    replay_activation_artifact,
)
from neurofly.muscle_activation_cli import main
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_observation_mapping_artifacts import replay_ttm_g1_mapping_artifact
from neurofly.ttm_g1_proxy_mapping import DEFAULT_SOURCE_PATHS


@pytest.fixture(scope="module")
def source():
    return replay_response_artifact(DEFAULT_MODEL_ARTIFACT)


@pytest.fixture(scope="module")
def result(source):
    return transform_response(source, reference_config())


def rows(payload):
    return {
        (f["fixture_id"], i["source_body_id"]): i
        for f in payload["result"]["fixtures"]
        for i in f["instances"]
    }


def rehash_source(source):
    source["result_sha256"] = canonical_sha256(source["result"])
    source["artifact_id"] = canonical_sha256(
        [electrical.ARTIFACT_SCHEMA, source["config_sha256"], source["result_sha256"]]
    )


def test_accounting_static_mapping_ancestry(source, result):
    assert result["result"]["trajectory_count"] == 12
    assert result["result"]["sample_count"] == 972
    assert result["result"]["time_ms"] == source["result"]["time_ms"]
    assert result["result"]["boundary_indices"] == list(range(81))
    assert result["config"]["source_phase9b"]["artifact_id"] == SOURCE_ID
    assert (
        result["config_sha256"]
        == "be33c72048caeae4227a504aa251d10acec454ef283a73adf77104d0a4c424c9"
    )
    assert (
        result["result_sha256"]
        == "288b67f791f66765a17d6bdd6cadd30b9c98f4480dd23434bd4c6e9ae5667fce"
    )
    assert (
        result["artifact_id"]
        == "4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb"
    )
    assert list(rows(result)) == [
        (f, b) for f in electrical.FIXTURE_IDS for b in (800146, 804642)
    ]
    ids = set()
    for key, row in rows(result).items():
        original = rows(source)[key]
        assert row["source_trajectory_id"] == original["instance_id"]
        assert row["source_trajectory_sha256"] == canonical_sha256(original)
        assert row["source_side"] == original["source_side"]
        assert row["proxy_domain_id"] == original["proxy_domain_id"]
        assert row["activation_proxy"] == [
            min(1, max(0, u) / 10) for u in original["voltage_deviation_mV_eq"]
        ]
        assert len(row["activation_proxy"]) == 81
        assert all(0 <= a <= 1 for a in row["activation_proxy"])
        assert row["summary"]["ceiling_sample_count"] == 0
        assert row["trajectory_id"] == canonical_sha256(
            {k: v for k, v in row.items() if k != "trajectory_id"}
        )
        ids.add(row["trajectory_id"])
    assert len(ids) == 12


def test_fixture_behaviors(result):
    r = rows(result)
    for body in (800146, 804642):
        assert r[("ZERO_EVENT_CONTROL", body)]["activation_proxy"] == [0] * 81
        single = "RIGHT_SINGLE_EVENT" if body == 800146 else "LEFT_SINGLE_EVENT"
        inactive = "LEFT_SINGLE_EVENT" if body == 800146 else "RIGHT_SINGLE_EVENT"
        assert r[(inactive, body)]["activation_proxy"] == [0] * 81
        a = r[(single, body)]["activation_proxy"]
        assert a[:10] == [0] * 10
        assert a[10] == 0.2
        assert all(x > y > 0 for x, y in zip(a[10:-1], a[11:], strict=True))
        assert r[("BILATERAL_SIMULTANEOUS_EVENT", body)]["activation_proxy"] == a
        repeated = "RIGHT_REPEATED_EVENTS" if body == 800146 else "LEFT_REPEATED_EVENTS"
        assert r[(repeated, body)]["activation_proxy"][30] == pytest.approx(
            (2 + 2 * math.exp(-2)) / 10
        )
    assert (
        r[("BILATERAL_SIMULTANEOUS_EVENT", 800146)]["trajectory_id"]
        != r[("BILATERAL_SIMULTANEOUS_EVENT", 804642)]["trajectory_id"]
    )


def test_rectification_ceiling_memory_and_scale():
    assert activate_samples([-2, 0, 2, 10, 20, 2], reference_config()) == [
        0,
        0,
        0.2,
        1,
        1,
        0.2,
    ]
    assert activate_samples([2], ActivationConfig(20)) == [0.1]
    assert activate_samples([1e308], ActivationConfig(1e-308)) == [1]


@pytest.mark.parametrize(
    "value", [0, -1, float("nan"), float("inf"), -float("inf"), True, "10"]
)
def test_invalid_scale(value):
    with pytest.raises(ValueError):
        ActivationConfig(value)


@pytest.mark.parametrize(
    "values", [[], [float("nan")], [float("inf")], [True], ["2"], None]
)
def test_invalid_driver(values):
    with pytest.raises(ValueError):
        activate_samples(values, reference_config())


def test_local_negative_and_offset_source(source):
    changed = copy.deepcopy(source)
    row = changed["result"]["fixtures"][0]["instances"][0]
    row["voltage_deviation_mV_eq"][0] = -2
    rehash_source(changed)
    assert (
        transform_response(changed, reference_config())["result"]["fixtures"][0][
            "instances"
        ][0]["activation_proxy"][0]
        == 0
    )
    # Pure transform ignores the absolute coordinate and never calls a simulator.
    shifted = copy.deepcopy(source)
    for row in rows(shifted).values():
        row["proxy_voltage_mV_eq"] = [v + 17 for v in row["proxy_voltage_mV_eq"]]
    rehash_source(shifted)
    original, offset = (
        rows(transform_response(source, reference_config())),
        rows(transform_response(shifted, reference_config())),
    )
    assert all(
        original[k]["activation_proxy"] == offset[k]["activation_proxy"]
        for k in original
    )


def test_upstream_parameter_effects_and_no_integration(monkeypatch):
    baseline = electrical.build_response(electrical.reference_config())
    scaled = electrical.build_response(
        replace(electrical.reference_config(), event_scale_effective_mV_eq=4)
    )
    slower = electrical.build_response(
        replace(electrical.reference_config(), tau_effective_ms=2)
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("activation must not simulate or inspect tokens")

    monkeypatch.setattr(electrical, "integrate_counts", forbidden)
    for payload in (baseline, scaled, slower):
        for row in rows(payload).values():
            row.pop("token_count")
            row.pop("source_token_ids")
        rehash_source(payload)
    a, b, c = [
        rows(transform_response(p, reference_config()))[("RIGHT_SINGLE_EVENT", 800146)][
            "activation_proxy"
        ]
        for p in (baseline, scaled, slower)
    ]
    assert b == [2 * x for x in a]
    assert c[20] > a[20]


@pytest.mark.parametrize(
    "mutation",
    [
        "schema",
        "grid",
        "nonfinite",
        "body",
        "side",
        "proxy",
        "duplicate",
        "fixture",
        "identity",
    ],
)
def test_malformed_source(source, mutation):
    s = copy.deepcopy(source)
    row = s["result"]["fixtures"][0]["instances"][0]
    if mutation == "schema":
        s["schema_version"] = "other"
    elif mutation == "grid":
        s["result"]["time_ms"][10] = 1.1
    elif mutation == "nonfinite":
        row["voltage_deviation_mV_eq"][0] = float("nan")
    elif mutation == "body":
        row["source_body_id"] = 5
    elif mutation == "side":
        row["source_side"] = "L"
    elif mutation == "proxy":
        row["proxy_domain_id"] = "physical-g1"
    elif mutation == "duplicate":
        s["result"]["fixtures"][0]["instances"].append(copy.deepcopy(row))
    elif mutation == "fixture":
        s["result"]["fixtures"][0]["fixture_id"] = "OTHER"
    else:
        row["instance_id"] = "changed"
    with pytest.raises(ValueError):
        if mutation != "nonfinite":
            rehash_source(s)
        transform_response(s, reference_config())


@pytest.mark.parametrize(
    "mutation",
    [
        "source",
        "driver",
        "scale",
        "rectification",
        "ceiling",
        "body",
        "side",
        "proxy",
        "sample",
        "hash",
        "id",
    ],
)
def test_rehashed_result_tampering(result, mutation):
    p = copy.deepcopy(result)
    row = p["result"]["fixtures"][0]["instances"][0]
    if mutation == "source":
        p["config"]["source_phase9b"]["artifact_id"] = "other"
    elif mutation == "driver":
        row["voltage_deviation_mV_eq"][0] = 1
    elif mutation == "scale":
        p["config"]["model"]["activation_scale_mV_eq"] = 20
    elif mutation == "rectification":
        p["config"]["model"]["rectification"] = "ABSOLUTE"
    elif mutation == "ceiling":
        p["config"]["model"]["ceiling_semantics"] = "PHYSIOLOGICAL"
    elif mutation == "body":
        row["source_body_id"] = 1
    elif mutation == "side":
        row["source_side"] = "L"
    elif mutation == "proxy":
        row["proxy_domain_id"] = "other"
    elif mutation == "sample":
        row["activation_proxy"][0] = 0.5
    elif mutation == "hash":
        p["result_sha256"] = "other"
    else:
        p["artifact_id"] = "other"
    if mutation not in ("hash", "id"):
        p["config_sha256"] = canonical_sha256(p["config"])
        p["result_sha256"] = canonical_sha256(p["result"])
        p["artifact_id"] = canonical_sha256(
            [ARTIFACT_SCHEMA, p["config_sha256"], p["result_sha256"]]
        )
    with pytest.raises(ValueError):
        validate_activation(p)


def test_no_extra_state_fields(result):
    def keys(p):
        if isinstance(p, dict):
            return set(p) | set().union(*(keys(v) for v in p.values()))
        if isinstance(p, list):
            return set().union(*(keys(v) for v in p))
        return set()

    assert not {
        "force",
        "force_N",
        "force_fraction",
        "Fmax",
        "torque",
        "contraction",
        "strain",
        "calcium",
        "tau_activation",
        "threshold",
        "delay_ms",
        "percent_activation",
        "empirical_value",
        "loss",
    } & keys(result)
    assert (
        result["config"]["model"]["parameter_classifications"]["activation_scale_mV_eq"]
        == "MODEL_ASSUMPTION"
    )


def test_artifact_replay_cli_offline_and_bytes(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("offline")

    monkeypatch.setattr(socket, "create_connection", no_network)
    path = generate_activation_artifact(reference_config(), output_root=tmp_path)
    before = {p.name: p.read_bytes() for p in path.iterdir()}
    response = replay_activation_artifact(path)
    assert response == build_activation(reference_config())
    assert (
        generate_activation_artifact(reference_config(), output_root=tmp_path) == path
    )
    assert before == {p.name: p.read_bytes() for p in path.iterdir()}
    assert main(["inspect", str(path)]) == 0
    assert main(["replay", str(path)]) == 0
    assert main(["generate", "--output-root", str(tmp_path)]) == 0
    manifest = path / "manifest.json"
    payload = json.loads(manifest.read_text())
    payload["result_sha256"] = "tampered"
    manifest.write_bytes(canonical_json_bytes(payload, newline=True))
    with pytest.raises(ValueError):
        replay_activation_artifact(path)
    assert main(["replay", str(path)]) == 2


def test_historical_zero_ready():
    u = replay_ttm_g1_mapping_artifact(DEFAULT_SOURCE_PATHS["phase8u"])
    assert u.contract["result"]["formal_ready_mapping_count"] == 0
