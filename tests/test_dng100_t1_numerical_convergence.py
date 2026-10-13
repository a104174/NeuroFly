"""Independent analytical references; toy signals are never runtime data."""

import copy
import json
import math

import numpy as np
import pytest

from neurofly import dng100_t1_counterfactual_dynamics as old_model
from neurofly import dng100_t1_dynamics_sensitivity as old
from neurofly import dng100_t1_numerical_convergence as c

SETTINGS = dict(rtol=1e-10, atol=1e-12, max_step_s=0.001)


@pytest.fixture(scope="module")
def genuine():
    p = c.policy()
    source, selected = c.source(p)
    return p, source, selected


def test_reference_exponential_closed_form():
    times = np.arange(101) / 1000
    r = c.solve_piecewise(
        lambda y, rate: -100 * y, [2.0], times, [(0, 0.1, 0)], SETTINGS
    )
    assert (
        np.max(np.abs(np.array(r["states"])[:, 0] - 2 * np.exp(-100 * times))) < 1e-10
    )


def test_reference_coupled_analytic_rotation():
    times = np.arange(2001) / 1000
    r = c.solve_piecewise(
        lambda y, rate: np.array([-3 * y[1], 3 * y[0]]),
        [1, 0],
        times,
        [(0, 2, 0)],
        SETTINGS,
    )
    expected = np.stack([np.cos(3 * times), np.sin(3 * times)], axis=1)
    assert np.max(np.abs(np.asarray(r["states"]) - expected)) < 1e-10


def test_piecewise_input_and_boundary_continuity():
    times = np.arange(101) / 1000
    r = c.solve_piecewise(
        lambda y, rate: rate - 50 * y,
        [0],
        times,
        [(0, 0.02, 0), (0.02, 0.08, 10), (0.08, 0.1, 0)],
        SETTINGS,
    )
    expected = np.zeros(101)
    active = (times >= 0.02) & (times <= 0.08)
    expected[active] = 0.2 * (1 - np.exp(-50 * (times[active] - 0.02)))
    expected[times > 0.08] = (
        0.2 * (1 - np.exp(-3)) * np.exp(-50 * (times[times > 0.08] - 0.08))
    )
    assert np.max(np.abs(np.asarray(r["states"])[:, 0] - expected)) < 1e-10
    assert r["states"][20] == [0]
    assert [s["rate"] for s in r["solver_intervals"]] == [0, 10, 0]


def test_independent_rhs_literal_reference():
    state = np.array([3.0, 4.0])
    w = np.array([[0, 2], [-1, 0]])
    b = np.array([[1, 0], [0, 0]])
    d = c.independent_rhs(state, w, b, 20)
    assert d[0] == pytest.approx((200 * math.tanh(20.5 / 200) - 3) / 0.02)
    assert d[1] == -200


@pytest.mark.parametrize("rate", [0.0, 20.0])
def test_real_state_order_weights_and_rhs(genuine, rate):
    p, source, selected = genuine
    assert p["state_order"] == [800173, 800863, 801884, 800288, 903216, 803183]
    w, b = c.independent_matrices(p, source)
    assert np.array_equal(w, selected[0]["counterfactual_W_post_pre"])
    assert np.array_equal(b, selected[0]["counterfactual_B_post_source"])
    assert w[3, 5] == -0.06 * 439
    assert w[0, 2] == -0.06 * 526
    for y in [np.zeros(6), np.array([2, 3, 0, 1, 4, 0]), np.full(6, 200)]:
        independent = c.independent_rhs(y, w, b, rate)
        production = old_model.derivative(
            y, w, b @ np.full(2, rate), old_model.RateParameters()
        )
        assert np.max(np.abs(independent - production)) < 1e-9


def test_original_failure_preserved(genuine):
    p, _, selected = genuine
    error = c.compare(
        selected[0]["telemetry"], selected[1]["telemetry"], p["state_order"]
    )
    assert error["max_absolute"] == 0.28221829111123853
    assert error["body_id"] == 903216
    assert error["time_s"] == 1.922
    assert error["max_absolute"] > 0.2
    assert selected[0]["initial_rates"] == selected[1]["initial_rates"] == [0] * 6
    assert (
        selected[0]["telemetry"]["prescribed_source_rates"]
        == selected[1]["telemetry"]["prescribed_source_rates"]
    )


@pytest.mark.parametrize(
    "kind", ["duplicate", "reverse", "gap", "nonfinite", "tolerance"]
)
def test_invalid_reference_timing_and_parameters(kind):
    t = [0, 0.001, 0.002]
    pieces = [(0, 0.002, 0)]
    settings = SETTINGS.copy()
    if kind == "duplicate":
        t[1] = 0
    elif kind == "reverse":
        t[1] = -1
    elif kind == "gap":
        pieces = [(0, 0.0005, 0), (0.001, 0.002, 0)]
    elif kind == "nonfinite":
        t[1] = np.nan
    else:
        settings["atol"] = -1
    with pytest.raises(ValueError):
        c.solve_piecewise(lambda y, rate: -y, [0], t, pieces, settings)


def test_raw_errors_independently_known():
    a = {"times_s": [0, 0.001], "states": [[0, 0], [3, 4]]}
    b = {"times_s": [0, 0.001], "states": [[0, 0], [0, 0]]}
    e = c.compare(a, b, [11, 22])
    assert e["max_absolute"] == 4
    assert e["rms"] == 2.5
    assert e["body_id"] == 22 and e["time_s"] == 0.001


@pytest.mark.parametrize("bad", ["time", "shape", "nan"])
def test_mismatched_samples_rejected(bad):
    a = {"times_s": [0, 1], "states": [[0], [1]]}
    b = copy.deepcopy(a)
    if bad == "time":
        b["times_s"][1] = 2
    elif bad == "shape":
        b["states"][0] = [0, 1]
    else:
        b["states"][0] = [np.nan]
    with pytest.raises(ValueError):
        c.compare(a, b, [1])


def test_deterministic_refinement_matches_analytic_decay():
    errors = []
    for dt in [0.001, 0.0005]:
        r = old_model.simulate(
            np.zeros((1, 1)),
            np.zeros((1, 2)),
            old_model.RateParameters(threshold=100),
            [2],
            dt,
            0.001,
            0.04,
            [0, 0],
        )
        repeat = old_model.simulate(
            np.zeros((1, 1)),
            np.zeros((1, 2)),
            old_model.RateParameters(threshold=100),
            [2],
            dt,
            0.001,
            0.04,
            [0, 0],
        )
        assert r == repeat
        exact = 2 * np.exp(-np.asarray(r["times_s"]) / 0.02)
        errors.append(np.max(np.abs(np.array(r["states"])[:, 0] - exact)))
    assert errors[1] < errors[0] / 14


def toy_traces(p, mode):
    # Analytic toy waveform exclusively for outcome logic, not a neural fixture.
    t = np.arange(2001) / 1000
    base = 30 + 10 * np.sin(2 * np.pi * 20 * t)
    labels = ["reference", "reference_tight", *[str(dt) for dt in p["steps_s"]]]
    traces = {}
    for label in labels:
        y = base.copy()
        if label not in ["reference", "reference_tight"]:
            if mode == "nonconvergent":
                y += 1
            elif mode == "phase":
                y = 30 + 10 * np.sin(2 * np.pi * 20 * (t + 0.00005))
        traces[label] = dict(
            times_s=t.tolist(), states=np.repeat(y[:, None], 6, axis=1).tolist()
        )
    rules = old.policy()["metrics"]
    props = {name: c.properties(trace, rules) for name, trace in traces.items()}
    return traces, props


def test_nonconvergent_case_not_accepted():
    p = c.policy()
    traces, props = toy_traces(p, "nonconvergent")
    result = c.evaluate(p, traces, props)
    assert not result["raw_convergence_accepted"]
    assert result["decision"] == "DNG100_T1_CONVERGENCE_INCONCLUSIVE"


def test_phase_alignment_never_replaces_raw_acceptance():
    p = c.policy()
    traces, props = toy_traces(p, "phase")
    result = c.evaluate(p, traces, props)
    assert result["properties_accepted"]
    assert not result["raw_convergence_accepted"]
    assert result["decision"] == "DNG100_T1_OSCILLATION_PROPERTIES_ONLY"
    secondary = c.phase_diagnostic(
        traces[str(p["steps_s"][0])], traces["reference_tight"]
    )
    assert secondary["classification"] == "SECONDARY_NOT_ACCEPTANCE"
    assert all(x["aligned_rms"] < x["raw_rms"] for x in secondary["sides"])
    assert (
        result["errors_vs_tight_reference"][str(p["steps_s"][0])]["max_absolute"] > 0.05
    )


def test_contradictory_rehashed_metadata(genuine):
    p, source, _ = genuine
    config = c.config(p, source)
    config["functional_sign_status"] = "BIOLOGICALLY_SIGNED"
    value = c.package(config, {"traces": {}})
    with pytest.raises(ValueError, match="contradictory"):
        c.validate(value)


def test_source_identity_and_original_files_preserved(genuine):
    p, _, _ = genuine
    changed = copy.deepcopy(p)
    changed["dataset_uuid"] = "another-connectome"
    with pytest.raises(ValueError):
        c.source(changed)
    assert len(p["source_6_file_sha256"]) == 6


def test_missing_artifact_and_wrong_preregistration(tmp_path, monkeypatch):
    with pytest.raises(ValueError):
        c.replay(tmp_path)
    changed = c.policy()
    changed["metrics"]["fine_max_error"] = 100
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(c, "POLICY_PATH", path)
    with pytest.raises(ValueError):
        c.policy()
