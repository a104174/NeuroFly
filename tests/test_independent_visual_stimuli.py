"""Independent geometry and frozen-kernel controls for the versioned v5 adapter."""

import math

import pytest

from neurofly import independent_visual_stimuli_reference as v5
from neurofly import moving_visual_stimuli_reference as v4


def test_analytical_independent_geometry_and_retained_direction():
    controls = [{"enabled": True, "direction": 1}, {"enabled": False, "direction": -1}]
    w = v5.world([math.pi / 2, 0], controls)
    assert w["x"] == pytest.approx([0.68, -0.6], abs=1e-15)
    assert [s["id"] for s in w["landmarks"]] == ["A", "B"]
    assert w["landmarks"][1]["velocity_x"] == 0
    assert v5.control(controls[1], "START") == {"enabled": True, "direction": -1}
    assert v5.control(controls[1], "REVERSE") == {"enabled": False, "direction": 1}
    for p in range(100):
        a, b = v5.world([p / 7, -p / 11], controls)["x"]
        assert 0.52 - 1e-15 <= a <= 0.68 + 1e-15 and -0.68 - 1e-15 <= b <= -0.52 + 1e-15
    with pytest.raises(ValueError):
        v5.world([math.nan, 0], controls)
    with pytest.raises(ValueError):
        v5.control(controls[0], "TURN")


def test_stationary_body_per_landmark_geometry_not_sum_or_retinal_evidence():
    p = ([0, 0, 0], 0)
    controls = v5.load_policy()["presets"]["single"]
    before = v5.world([0, 0], controls)
    after = v5.world([0.02 * math.tau / 4, 0], controls)
    obs, _ = v4.observe(p, p, before, after, 1)
    expected = (
        (math.atan2(after["x"][0], 0.4) - math.atan2(0.6, 0.4)) / math.tau * 50 / 20
    )
    assert obs["right"] == pytest.approx(expected, abs=1e-15)
    assert obs["left"] == 0 and obs["self_motion_raw"] == [0, 0]
    assert obs["external_motion_raw"][1] == 0


@pytest.fixture(scope="module")
def cases():
    return {
        name: v5.run_reference(preset, events, apply, 501)
        for name, (preset, events, apply) in v5.CASES.items()
    }


def test_synchronized_v4_identity(cases):
    old = v4.run_reference(stop=501)
    for a, b in zip(cases["synchronized"]["frames"], old["frames"], strict=True):
        for key in a:
            if key != "stimulus_summary":
                assert a[key] == b[key], key
        assert a["stimulus_summary"]["x"] == b["stimulus_summary"]["x"]
        assert [s["phase"] for s in a["stimulus_summary"]["landmarks"]] == [
            b["stimulus_summary"]["phase"]
        ] * 2


def test_fixed_controls_and_causal_neural_off(cases):
    a, b, c = (
        cases["synchronized"]["frames"],
        cases["opposing"]["frames"],
        cases["off"]["frames"],
    )
    assert a[0]["neural_summary"] == b[0]["neural_summary"] == c[0]["neural_summary"]
    assert a[2]["sensory_summary"] != b[2]["sensory_summary"]
    assert a[250]["neural_summary"] != b[250]["neural_summary"]
    assert b[-1]["orientation"] != c[-1]["orientation"]
    assert all(f["boundary_summary"]["neural_omega"] == 0 for f in c)
    assert any(f["neural_summary"]["mean_yaw_drive_eq"] for f in c)
    assert all(f["propulsion_model_value"] == 0.18 for f in a + b + c)
    assert all(case["neural_substeps"] == 501 * 200 for case in cases.values())
    assert cases["single"]["frames"][-1]["stimulus_summary"]["x"][1] == -0.6


def test_simultaneous_interventions_order_continuity_and_completed_interval_delay(
    cases,
):
    f = cases["events"]["frames"]
    events = cases["events"]["events"]
    assert [e["sequence"] for e in events] == list(range(7))
    assert [(e["step"], e["stimulus_id"]) for e in events[:4]] == [
        (100, "A"),
        (100, "B"),
        (200, "A"),
        (200, "A"),
    ]
    assert f[101]["stimulus_summary"]["x"][0] == f[100]["stimulus_summary"]["x"][0]
    assert f[102]["sensory_summary"]["external_motion_raw"][0] == 0
    assert f[100]["sensory_summary"]["external_motion_raw"][0] != 0
    assert f[101]["stimulus_summary"]["x"][1] != f[100]["stimulus_summary"]["x"][1]
    assert f[100]["neural_summary"]["substeps"] == 200
    assert f[100]["neural_summary"]["hs_states"] != [0] * 6
    with pytest.raises(ValueError):
        v5.run_reference(events=((1, "X", "STOP"),), stop=2)
    with pytest.raises(ValueError):
        v5.run_reference(events=((2, "A", "STOP"),), stop=2)
    with pytest.raises(ValueError):
        v5.run_reference(events=((1, "A", "START"),), stop=2)
