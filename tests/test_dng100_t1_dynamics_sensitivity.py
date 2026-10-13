"""Independent mathematical references and real pinned authority boundaries."""

import copy
import json

import numpy as np
import pytest

from neurofly import dng100_t1_counterfactual_dynamics as m
from neurofly import dng100_t1_dynamics_sensitivity as s
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256


@pytest.fixture(scope="module")
def source():
    return s.policy(), s.load_authority()


def cfg(role="primary", schedule="constant", variant="A_PUBLISHED_LIKE"):
    return dict(point="central", variant=variant, schedule=schedule, role=role)


def test_real_source_and_direction(source):
    p, edges = source
    assert len(edges) == 15
    assert {(e["pre"], e["post"]) for e in edges if e["pre"] < 20000} == {
        (10045, 800288),
        (10056, 800173),
        (10056, 800863),
    }
    w, b, _ = s.matrices(p, edges, cfg())
    # Literal counts and source/target order, independent of extraction helper.
    assert w[0, 2] == -0.03 * 526
    assert w[3, 5] == -0.03 * 439
    assert w[1, 0] == 0.03 * 465
    assert w[4, 3] == 0.03 * 328
    assert b[0, 1] == 0.03 * 155
    assert b[3, 0] == 0.03 * 100
    assert b[1, 1] == 0.03
    assert np.count_nonzero(w) == 12
    assert np.count_nonzero(b) == 3
    assert not w[:3, 3:].any() and not w[3:, :3].any()
    assert p["biological_sign_status"] == "UNKNOWN_FOR_ALL_15_CONNECTIONS"


@pytest.mark.parametrize("mutation", ["count", "reverse", "body", "remove"])
def test_reject_graph_tampering(source, mutation):
    p, graph = source
    altered = copy.deepcopy(graph)
    if mutation == "count":
        altered[0]["synapse_count"] += 1
    elif mutation == "reverse":
        altered[0]["pre"], altered[0]["post"] = altered[0]["post"], altered[0]["pre"]
    elif mutation == "body":
        altered[0]["pre"] = 1
    else:
        altered.pop()
    with pytest.raises(ValueError):
        s.matrices(p, altered, cfg())


@pytest.mark.parametrize(
    "key,value",
    [
        ("variant", "BIOLOGICAL_INHIBITION"),
        ("point", "tuned"),
        ("role", "noise"),
        ("schedule", "periodic"),
    ],
)
def test_unregistered_configuration(source, key, value):
    p, graph = source
    with pytest.raises(ValueError):
        s.matrices(p, graph, {**cfg(), key: value})


def test_policy_tampering_even_with_recomputed_hash(source, tmp_path, monkeypatch):
    p, graph = source
    changed = copy.deepcopy(p)
    changed["sign_variants"]["A_PUBLISHED_LIKE"]["I1"] = 1
    with pytest.raises(ValueError):
        s.matrices(changed, graph, cfg())
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(s, "PREREGISTRATION", path)
    with pytest.raises(ValueError):
        s.policy()
    assert canonical_sha256(changed) != s.POLICY_ID


@pytest.mark.parametrize(
    "field,value",
    [("tau_s", 0), ("gain", -1), ("threshold", float("nan")), ("cap", float("inf"))],
)
def test_invalid_parameters(field, value):
    with pytest.raises(ValueError):
        m.RateParameters(**{field: value}).validate()


def test_transfer_direction_and_simultaneous_state():
    p = m.RateParameters(tau_s=1, gain=1, threshold=1, cap=200)
    d = m.derivative(np.array([2.0, 0.0]), np.array([[0, 0], [1, 0]]), np.zeros(2), p)
    assert d[0] == -2
    assert d[1] == pytest.approx(200 * np.tanh(1 / 200))
    # No reverse connection or sequential updating of R0 before evaluating R1.


def test_analytic_decay_and_fourth_order_convergence():
    p = m.RateParameters(tau_s=0.02, threshold=100)
    errors = []
    for dt in [0.002, 0.001]:
        out = m.simulate(
            np.zeros((1, 1)), np.zeros((1, 2)), p, [2], dt, 0.002, 0.04, [0, 0]
        )
        exact = 2 * np.exp(-np.asarray(out["times_s"]) / 0.02)
        errors.append(np.max(np.abs(np.array(out["states"])[:, 0] - exact)))
    assert errors[0] / errors[1] > 14
    assert errors[1] < 1e-6


def test_independent_constant_input_solution_and_withdrawal():
    p = m.RateParameters(tau_s=0.02)
    out = m.simulate(
        np.zeros((1, 1)), np.array([[1, 0]]), p, [0], 0.00025, 0.001, 0.1, [0.02, 0.05]
    )
    t = np.asarray(out["times_s"])
    target = 200 * np.tanh((20 - 7.5) / 200)
    expected = np.where(
        t < 0.02, 0, target * (1 - np.exp(-np.minimum(t - 0.02, 0.03) / 0.02))
    )
    expected[t >= 0.05] *= np.exp(-(t[t >= 0.05] - 0.05) / 0.02)
    assert np.max(np.abs(np.asarray(out["states"])[:, 0] - expected)) < 1e-7
    assert out["prescribed_source_rates"][19] == [0, 0]
    assert out["prescribed_source_rates"][20] == [20, 20]
    assert out["prescribed_source_rates"][50] == [0, 0]


@pytest.mark.parametrize(
    "interval", [[0.02, 0.01], [-0.1, 0.02], [0, float("nan")], [0, 0.01003]]
)
def test_invalid_timing(interval):
    with pytest.raises(ValueError):
        m.simulate(
            np.zeros((1, 1)),
            np.zeros((1, 2)),
            m.RateParameters(),
            [0],
            0.001,
            0.001,
            0.1,
            interval,
        )


def test_numerical_divergence_not_zero_substitution():
    out = m.simulate(
        np.zeros((1, 1)),
        np.ones((1, 2)),
        m.RateParameters(tau_s=0.001),
        [0],
        1,
        1,
        2,
        [0, 2],
    )
    assert out["termination"] == "NUMERICAL_DIVERGENCE"
    assert len(out["states"]) == 1
    assert out["final_residual"] is None


def test_periodic_mathematical_reference_and_transient_rejection(source):
    rules = source[0]["metrics"]
    t = np.arange(2001) / 1000
    sine = 10 + 3 * np.sin(2 * np.pi * 20 * t)
    metrics = m.cell_metrics(t, sine, rules)
    assert metrics["sustained"]
    assert metrics["period_s"] == pytest.approx(0.05, abs=1e-5)
    assert metrics["complete_cycles"] >= 5
    for y in [
        np.exp(-10 * t),
        np.exp(-4 * t) * np.sin(2 * np.pi * 20 * t),
        np.exp(-(((t - 0.5) / 0.05) ** 2)),
        np.zeros_like(t),
    ]:
        assert not m.cell_metrics(t, y, rules)["sustained"]


@pytest.mark.parametrize("bad", ["nan", "duplicate", "ordering"])
def test_invalid_metric_trace(source, bad):
    t = np.arange(2001) / 1000
    y = np.zeros(2001)
    if bad == "nan":
        y[0] = np.nan
    elif bad == "duplicate":
        t[1] = t[0]
    else:
        t[1] = -1
    with pytest.raises(ValueError):
        m.cell_metrics(t, y, source[0]["metrics"])


def test_zero_source_off_and_feedback_controls(source):
    p, graph = source
    for config in [cfg(schedule="zero"), cfg(role="source_off")]:
        r = s.run(p, graph, config)
        assert not np.asarray(r["telemetry"]["states"]).any()
        assert not np.asarray(r["telemetry"]["prescribed_source_rates"]).any()
        assert r["classification"] == "STABLE_FIXED_POINT"
    disabled = s.run(p, graph, cfg(role="feedback_disabled"))
    assert not np.asarray(disabled["counterfactual_W_post_pre"]).any()
    assert disabled["classification"] == "STABLE_FIXED_POINT"
    # Independent one-cell plateau: E1L receives155*.03*20=93 model input.
    target = 200 * np.tanh((93 - 7.5) / 200)
    assert disabled["telemetry"]["states"][-1][0] == pytest.approx(target, abs=1e-8)


def test_sham_determinism_and_no_body_state(source):
    p, graph = source
    a = s.run(p, graph, cfg(role="feedback_disabled", schedule="pulse"))
    b = s.run(p, graph, cfg(role="feedback_disabled", schedule="pulse"))
    assert a == b
    assert not {"position", "heading", "motor_command"}.intersection(a["telemetry"])
    w1, b1, _ = s.matrices(p, graph, cfg())
    w2, b2, _ = s.matrices(p, graph, cfg(role="sham"))
    assert np.array_equal(w1, w2) and np.array_equal(b1, b2)
    assert len(s.configurations(p)) == 275


def test_rehashed_contradictory_artifact_rejected(source):
    p, graph = source
    config = s.experiment_config(p, graph)
    config["functional_sign_status"] = "BIOLOGICALLY_INHIBITORY"
    fake = s.package(config, {"runs": [], "summary": {}})
    with pytest.raises(ValueError, match="contradictory configuration"):
        s.validate(fake)


def test_missing_artifact(tmp_path):
    with pytest.raises(ValueError):
        s.replay(tmp_path)
