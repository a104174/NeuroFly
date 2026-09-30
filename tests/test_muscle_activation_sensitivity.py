"""Activation assumption sensitivity and identity, not empirical mechanics."""

import copy
import json
import socket

import pytest

from neurofly.g1_proxy_passive_electrical_artifacts import replay_response_artifact
from neurofly.muscle_activation import (
    DEFAULT_MODEL_ARTIFACT,
    ActivationConfig,
    activate_samples,
    transform_response,
)
from neurofly.muscle_activation_sensitivity import (
    ARTIFACT_SCHEMA,
    SCALES,
    SOURCE_ID,
    analyze_responses,
    build_sensitivity,
    validate_sensitivity,
)
from neurofly.muscle_activation_sensitivity_artifacts import (
    generate_sensitivity_artifact,
    replay_sensitivity_artifact,
)
from neurofly.muscle_activation_sensitivity_cli import main
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)


@pytest.fixture(scope="module")
def source():
    return replay_response_artifact(DEFAULT_MODEL_ARTIFACT)


@pytest.fixture(scope="module")
def responses(source):
    return [transform_response(source, ActivationConfig(s)) for s in SCALES]


@pytest.fixture(scope="module")
def experiment():
    return build_sensitivity()


def rows(p):
    return {
        (f["fixture_id"], i["source_body_id"]): i
        for f in p["result"]["fixtures"]
        for i in f["instances"]
    }


def test_accounting_reference_and_compact_output(experiment):
    assert experiment["artifact_id"] == (
        "b605e51e4ed42813d2562d61aa58129ed3d5b43e875ab1fd0de98ca0360c9a6e"
    )
    assert experiment["config_sha256"] == (
        "7b3826904b71182fe1dab3cbca9d2897e1c02ff23c2c2a2c448139599721d88e"
    )
    assert experiment["result_sha256"] == (
        "7f6e580b770741967f0dda3e87dcb3c9b1288575ccb2b872035751ed562d36dc"
    )
    r = experiment["result"]
    assert (
        r["cell_count"],
        r["fixture_run_count"],
        r["trajectory_count"],
        r["sample_count"],
    ) == (3, 18, 36, 2916)
    assert experiment["config"]["activation_scales_mV_eq"] == [5, 10, 20]
    cells = r["cells"]
    assert sum(c["is_reference_cell"] for c in cells) == 1
    assert cells[1]["activation_artifact_id"] == SOURCE_ID
    assert r["reference_cell_id"] == cells[1]["cell_id"]
    assert len({c["cell_id"] for c in cells}) == 3
    for c in cells:
        assert len(c["summaries"]) == 12
        assert len({s["fixture_id"] for s in c["summaries"]}) == 6
        assert all("activation_proxy" not in s for s in c["summaries"])
        # Peak/max names are diagnostics, no full sample arrays are persisted.


def test_all_samples_inverse_reconstruction_zero_timing(source, responses):
    analysis = analyze_responses(source, responses)
    assert (
        analysis["canonical_regime"]
        == "CANONICAL_FIXTURES_REMAIN_IN_UNCLIPPED_LINEAR_REGIME"
    )
    src = rows(source)
    indexed = [rows(p) for p in responses]
    for key, parent in src.items():
        arrays = [r[key]["activation_proxy"] for r in indexed]
        for n, u in enumerate(parent["voltage_deviation_mV_eq"]):
            assert arrays[0][n] == 2 * arrays[1][n]
            assert arrays[1][n] == 2 * arrays[2][n]
            for a, scale in zip(arrays, SCALES, strict=True):
                assert a[n] * scale == pytest.approx(u, rel=1e-12, abs=1e-14)
                if u == 0:
                    assert a[n] == 0
        for r in indexed:
            assert r[key]["summary"]["peak_step"] == parent["summary"]["peak_boundary"]
            assert r[key]["source_side"] == parent["source_side"]
            assert r[key]["source_trajectory_id"] == parent["instance_id"]


def test_cell_diagnostics_and_peaks(experiment):
    for c, scale, peak in zip(
        experiment["result"]["cells"], SCALES, [0.4, 0.2, 0.1], strict=True
    ):
        d = c["diagnostics"]
        assert d["clipped_sample_count"] == d["clipped_trajectory_count"] == 0
        assert d["above_ceiling_information_loss_sample_count"] == 0
        assert not d["ceiling_information_loss_occurs"]
        sums = {(s["fixture_id"], s["source_body_id"]): s for s in c["summaries"]}
        assert sums[("RIGHT_SINGLE_EVENT", 800146)]["peak_activation_proxy"] == peak
        assert sums[("LEFT_SINGLE_EVENT", 804642)]["peak_activation_proxy"] == peak
        repeated = sums[("RIGHT_REPEATED_EVENTS", 800146)]
        assert (
            repeated["peak_activation_proxy"]
            == repeated["source_peak_deviation_mV_eq"] / scale
        )
        assert d["maximum_activation_proxy"] == repeated["peak_activation_proxy"]
        assert d["maximum_unclipped_ratio"] == d["maximum_activation_proxy"] < 1


def test_bilateral_independence(responses):
    for p in responses:
        r = rows(p)
        for body in (800146, 804642):
            single = "RIGHT_SINGLE_EVENT" if body == 800146 else "LEFT_SINGLE_EVENT"
            assert (
                r[(single, body)]["activation_proxy"]
                == r[("BILATERAL_SIMULTANEOUS_EVENT", body)]["activation_proxy"]
            )
        assert (
            r[("BILATERAL_SIMULTANEOUS_EVENT", 800146)]["trajectory_id"]
            != r[("BILATERAL_SIMULTANEOUS_EVENT", 804642)]["trajectory_id"]
        )


@pytest.mark.parametrize("scale", SCALES)
def test_controlled_information_loss(scale):
    assert activate_samples(
        [-2, -1, 0, scale, 2 * scale, 3 * scale], ActivationConfig(scale)
    ) == [0, 0, 0, 1, 1, 1]


def test_reuses_transform_once_per_cell(monkeypatch, source):
    from neurofly import muscle_activation_sensitivity as m

    calls = []
    original = m.transform_response

    def tracked(s, c):
        calls.append((id(s), c.activation_scale_mV_eq))
        return original(s, c)

    monkeypatch.setattr(m, "transform_response", tracked)
    build_sensitivity()
    assert [s for _, s in calls] == list(SCALES)
    assert len({i for i, _ in calls}) == 1


@pytest.mark.parametrize("kind", ["count", "grid", "driver", "value", "timing", "side"])
def test_analysis_rejects_changed_executions(source, responses, kind):
    rs = copy.deepcopy(responses)
    row = rs[0]["result"]["fixtures"][1]["instances"][0]
    if kind == "count":
        rs.pop()
    elif kind == "grid":
        rs[0]["result"]["time_ms"][10] = 2
    elif kind == "driver":
        row["voltage_deviation_mV_eq"][10] = 3
    elif kind == "value":
        row["activation_proxy"][10] = 0.8
    elif kind == "timing":
        row["summary"]["peak_step"] = 11
    else:
        row["source_side"] = "L"
    with pytest.raises(ValueError):
        analyze_responses(source, rs)


@pytest.mark.parametrize(
    "kind",
    [
        "grid",
        "reference",
        "10b",
        "9b",
        "scale",
        "fixture",
        "summary",
        "clipping",
        "decision",
        "hash",
        "id",
    ],
)
def test_rehashed_tamper_rejection(experiment, kind):
    p = copy.deepcopy(experiment)
    c = p["result"]["cells"][0]
    if kind == "grid":
        p["config"]["activation_scales_mV_eq"][0] = 6
    elif kind == "reference":
        c["is_reference_cell"] = True
    elif kind == "10b":
        p["config"]["source_phase10b"]["artifact_id"] = "other"
    elif kind == "9b":
        p["config"]["source_phase9b"]["artifact_id"] = "other"
    elif kind == "scale":
        c["model_config"]["activation_scale_mV_eq"] = 6
    elif kind == "fixture":
        c["summaries"][0]["fixture_id"] = "other"
    elif kind == "summary":
        c["summaries"][0]["peak_activation_proxy"] = 0.5
    elif kind == "clipping":
        c["diagnostics"]["clipped_sample_count"] = 1
    elif kind == "decision":
        p["result"]["analysis"]["mechanics_interface"] = "PHYSICAL_MAPPING_READY"
    elif kind == "hash":
        p["result_sha256"] = "wrong"
    else:
        p["artifact_id"] = "wrong"
    if kind not in ("hash", "id"):
        p["config_sha256"] = canonical_sha256(p["config"])
        p["result_sha256"] = canonical_sha256(p["result"])
        p["artifact_id"] = canonical_sha256(
            [ARTIFACT_SCHEMA, p["config_sha256"], p["result_sha256"]]
        )
    with pytest.raises(ValueError):
        validate_sensitivity(p)


def test_no_physical_output_fields(experiment):
    def keys(p):
        if isinstance(p, dict):
            return set(p) | set().union(*(keys(v) for v in p.values()))
        if isinstance(p, list):
            return set().union(*(keys(v) for v in p))
        return set()

    assert not {
        "force",
        "torque",
        "contraction",
        "strain",
        "Fmax",
        "physical_actuator_outputs",
    } & keys(experiment)


def test_offline_artifact_bytes_cli_tamper(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("offline")

    monkeypatch.setattr(socket, "create_connection", no_network)
    path = generate_sensitivity_artifact(output_root=tmp_path)
    before = {p.name: p.read_bytes() for p in path.iterdir()}
    assert replay_sensitivity_artifact(path) == build_sensitivity()
    assert generate_sensitivity_artifact(output_root=tmp_path) == path
    assert before == {p.name: p.read_bytes() for p in path.iterdir()}
    assert main(["generate", "--output-root", str(tmp_path)]) == 0
    assert main(["inspect", str(path)]) == 0
    assert main(["replay", str(path)]) == 0
    payload = json.loads((path / "manifest.json").read_text())
    payload["artifact_id"] = "tampered"
    (path / "manifest.json").write_bytes(canonical_json_bytes(payload, newline=True))
    with pytest.raises(ValueError):
        replay_sensitivity_artifact(path)
    assert main(["replay", str(path)]) == 2
