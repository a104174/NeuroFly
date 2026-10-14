"""Analytical independent references; no synthetic neural runtime input."""

import copy
import hashlib
import json
import math

import pytest

from neurofly import dng100_t1_motor_response_shadow as s


@pytest.fixture(scope="module")
def genuine():
    return s.load_input()


@pytest.fixture
def artifact(genuine, monkeypatch):
    p, source = genuine
    monkeypatch.setattr(s, "load_input", lambda: genuine)
    return s.package(s.config(p, source), s.experiment(p, source))


@pytest.mark.parametrize("tau", [0.001, 0.01, 0.1])
def test_independent_constant_and_initial_decay(tau):
    t = tuple(i * 0.001 for i in range(2001))
    r = s.response(t, (2.0,) * len(t), s.ReceiverConfig(tau, 1.0, -3.0))
    # Integrating-factor closed form, not a recurrence or production helper.
    expected = tuple(2.0 - 5.0 * math.exp(-time / tau) for time in t)
    assert max(abs(a - b) for a, b in zip(r, expected)) < 1e-12
    decay = s.response(t, (0.0,) * len(t), s.ReceiverConfig(tau, 1.0, 3.0))
    assert max(abs(y - 3 * math.exp(-time / tau)) for time, y in zip(t, decay)) < 1e-12
    assert s.response(t, (0.0,) * len(t), s.ReceiverConfig(tau)) == (0.0,) * len(t)


def test_piecewise_input_and_interval_boundaries():
    times = (0.0, 0.01, 0.02, 0.03, 0.04)
    y = s.response(times, (2.0, 2.0, -1.0, -1.0, 999.0), s.ReceiverConfig(0.01))
    expected = (
        0.0,
        2 * (1 - math.exp(-1)),
        2 * (1 - math.exp(-2)),
        -1 + (3 - 2 * math.exp(-2)) * math.exp(-1),
        -1 + (3 - 2 * math.exp(-2)) * math.exp(-2),
    )
    assert max(abs(a - b) for a, b in zip(y, expected)) < 1e-14
    # Final input has no outgoing interval. Neither y0 nor earlier states change.
    assert y == s.response(
        times, (2.0, 2.0, -1.0, -1.0, -999.0), s.ReceiverConfig(0.01)
    )


def test_nonuniform_held_intervals_and_no_rectification():
    t = (0.0, 0.003, 0.02)
    y = s.response(t, (-2.0, -2.0, -2.0), s.ReceiverConfig(0.1, 2))
    assert y[1] < 0 and y[2] < y[1]
    assert (
        max(abs(v - (-4 * (1 - math.exp(-time / 0.1)))) for time, v in zip(t, y))
        < 1e-14
    )


@pytest.mark.parametrize("tau", [1e-9, 1e6])
def test_engineering_extreme_timescales(tau):
    y = s.response((0.0, 0.001, 0.002), (1.0, 1.0, 1.0), s.ReceiverConfig(tau))
    # expm1 closed-form reference avoids cancellation for very large tau.
    assert abs(y[-1] + math.expm1(-0.002 / tau)) < 1e-15


@pytest.mark.parametrize(
    "field,value",
    [
        ("tau_s", 0),
        ("tau_s", -1),
        ("tau_s", math.inf),
        ("tau_s", True),
        ("gain", 0),
        ("gain", math.nan),
        ("gain", -1),
        ("initial_state", math.nan),
        ("initial_state", None),
    ],
)
def test_invalid_parameters(field, value):
    config = dict(tau_s=0.01, gain=1.0, initial_state=0.0)
    config[field] = value
    with pytest.raises(ValueError):
        s.ReceiverConfig(**config)


@pytest.mark.parametrize(
    "times,values",
    [
        ((), ()),
        ((0.0,), (1.0,)),
        ((1.0, 2.0), (1.0, 1.0)),
        ((0.0, 0.0), (1.0, 1.0)),
        ((0.0, -1.0), (1.0, 1.0)),
        ((0.0, math.nan), (1.0, 1.0)),
        ((0.0, 0.001), (math.inf, 1.0)),
        ((0.0, 0.001), (None, 1.0)),
        ((0.0, 0.001), (1.0,)),
    ],
)
def test_invalid_order_or_source(times, values):
    with pytest.raises(ValueError):
        s.response(times, values, s.ReceiverConfig(0.01))


def test_overflow_fails_instead_of_clipping():
    with pytest.raises(ValueError, match="nonfinite"):
        s.response((0.0, 1.0), (1e308, 1e308), s.ReceiverConfig(0.001, 1e308))


def test_metric_literal_reference_and_unavailable_ratio():
    m = s.metrics((0.0, 1.0, 2.0), (2.0, 1.0, 0.0), (0.0, 1.0, 1.0))
    assert m["peak_time_s"] == 1.0 and m["peak_time_offset_s"] == 1.0
    assert m["tail_input_centered_rms"] == 0.5
    assert m["tail_output_centered_rms"] == 0 and m["tail_attenuation_rms_ratio"] == 0
    z = s.metrics((0.0, 1.0, 2.0), (0.0,) * 3, (0.0,) * 3)
    assert z["tail_attenuation_rms_ratio"] is None and z["peak_time_offset_s"] is None


def test_real_source_authority_and_all_controls(genuine):
    p, a = genuine
    assert p["edge"] == {"pre": 903216, "post": 804257, "synapse_count": 23}
    assert p["dataset_uuid"] == "4b2087c0fbe046bfaf0d60bc970e3e5d"
    before = copy.deepcopy(a)
    result = s.experiment(p, a)
    assert a == before and len(result["runs"]) == 12
    for offset in range(0, 12, 4):
        pos, neg, off, sham = result["runs"][offset : offset + 4]
        for i in range(2001):
            pa, nb, oc, ds = [r["telemetry"][i] for r in (pos, neg, off, sham)]
            assert pa["receiver_state"] == -nb["receiver_state"]
            assert oc["receiver_state"] == 0
            assert ds["receiver_state"] == pa["receiver_state"]
            assert (
                pa["shadow_input"]
                == a["result"]["conditions"][0]["telemetry"][i]["shadow_input"]
            )
            assert (
                pa["time_s"] == a["result"]["conditions"][0]["telemetry"][i]["time_s"]
            )
            assert pa["receiver_consumed_input_step"] == (i - 1 if i else None)
            assert pa["outgoing_interval_input"] == (
                pa["shadow_input"] if i < 2000 else None
            )
            assert set(pa) == {
                "step",
                "time_s",
                "source_model_state",
                "shadow_input",
                "receiver_state",
                "receiver_consumed_input_step",
                "outgoing_interval_input",
                "condition",
                "parameter_id",
                "sign_assumption",
                "source_body_id",
                "target_body_id",
            }
        assert off["metrics"]["tail_attenuation_rms_ratio"] is None
    assert (
        result["summary"]["semantics"]["physiological_motor_recruitment"]
        == "NOT_VALIDATED"
    )
    assert result["summary"]["semantics"]["body_movement"] == "NOT_MODELLED"


def test_real_loader_never_regenerates_neural_dynamics(genuine, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Original neural dynamics must not execute")

    monkeypatch.setattr(s.parent.convergence.model, "simulate", forbidden)
    monkeypatch.setattr(s.parent.convergence, "solve_piecewise", forbidden)
    monkeypatch.setattr(s.parent.convergence.v0, "run", forbidden)
    assert s.load_input() == genuine


@pytest.mark.parametrize(
    "change",
    ["state", "time", "input", "tau", "gain", "initial", "edge", "recruitment"],
)
def test_rehashed_contradictions(artifact, change):
    a = copy.deepcopy(artifact)
    if change in ("state", "time", "input"):
        key = {"state": "receiver_state", "time": "time_s", "input": "shadow_input"}[
            change
        ]
        a["result"]["runs"][0]["telemetry"][10][key] += 1
    elif change in ("tau", "gain", "initial"):
        p = a["config"]["preregistration"]
        if change == "tau":
            p["timescales"][0]["tau_s"] = 0.002
        else:
            p["model"][{"gain": "gain", "initial": "initial_state"}[change]] = 2
    elif change == "edge":
        a["config"]["preregistration"]["edge"]["synapse_count"] = 24
    else:
        a["config"]["preregistration"]["semantics"][
            "physiological_motor_recruitment"
        ] = "VALIDATED"
    with pytest.raises(ValueError, match="contradictory"):
        s.validate(s.package(a["config"], a["result"]))


def test_deterministic_replay_and_external_output(artifact, tmp_path):
    path = s.generate(tmp_path)
    assert s.replay(path) == artifact
    raw = (path / "response.json").read_bytes()
    assert (
        json.loads((path / "manifest.json").read_bytes())["files"]["response.json"][
            "sha256"
        ]
        == hashlib.sha256(raw).hexdigest()
    )
    with pytest.raises(ValueError, match="overwrite"):
        s.generate(tmp_path)
    with pytest.raises(ValueError, match="outside Git"):
        s.generate(s.parent.REPO)
    (path / "response.json").write_bytes(raw + b" ")
    with pytest.raises(ValueError, match="hash"):
        s.replay(path)


def test_missing_and_corrupted_parent(genuine, monkeypatch, tmp_path):
    monkeypatch.setattr(s.parent, "DEFAULT_ROOT", tmp_path)
    with pytest.raises(ValueError, match="missing"):
        s.load_input()
    path = tmp_path / genuine[0]["input_artifact_id"]
    path.mkdir()
    (path / "shadow.json").write_text("{}")
    with pytest.raises(ValueError, match="source mismatch"):
        s.load_input()


def test_preregistration_tamper(genuine, monkeypatch, tmp_path):
    p = copy.deepcopy(genuine[0])
    p["timescales"][0]["tau_s"] = 1
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(p))
    monkeypatch.setattr(s, "POLICY_PATH", path)
    with pytest.raises(ValueError, match="preregistration"):
        s.policy()
