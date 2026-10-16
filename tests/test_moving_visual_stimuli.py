"""Independent geometry/analytical checks; actual frozen kernel in model cases."""

import math

import pytest

from neurofly import continuous_arena_navigation_reference as old
from neurofly import moving_visual_stimuli_reference as v4


def test_policy_pin_and_analytical_bounded_motion():
    assert v4.load_policy()["amplitude"] == 0.08
    assert v4.world(0, 1)["x"] == [0.6, -0.6]
    assert v4.world(math.pi / 2, 1)["x"] == [0.6799999999999999, -0.52]
    assert v4.world(0.7, 0)["x"] == v4.world(0.7, -1)["x"]
    assert v4.world(0.7, 0)["velocity_x"] == 0
    for direction in (-1, 0, 1):
        for i in range(100):
            x = v4.world(direction * i / 10, direction)["x"]
            assert 0.52 - 1e-15 <= x[0] <= 0.68 + 1e-15
            assert -0.68 - 1e-15 <= x[1] <= -0.52 + 1e-15
    with pytest.raises(ValueError):
        v4.world(float("nan"), 1)
    with pytest.raises(ValueError):
        v4.world(0, 2)


def test_stationary_body_separates_external_motion_and_zero_control():
    pose = ([0, 0, 0], 0)
    start, end = v4.world(0, 1), v4.world(math.pi * 0.02 / 2, 1)
    observed, sides = v4.observe(pose, pose, start, end, 1)
    expected_angle = math.atan2(end["x"][0], 0.4) - math.atan2(0.6, 0.4)
    assert observed["right"] == pytest.approx(
        50 * expected_angle / math.tau / 20, abs=1e-15
    )
    assert observed["self_motion_raw"] == [0, 0]
    assert observed["external_motion_raw"][0] > 0
    assert sides.right != 0
    zero, _ = v4.observe(pose, pose, start, start, 1)
    assert zero["raw_normalized"] == [0, 0]
    assert zero["external_motion_raw"] == [0, 0]


def test_relative_geometry_decomposition_and_invalid_intervals():
    a, b = ([0.1, 0, 0.02], 0.1), ([0.11, 0, 0.025], 0.12)
    observation, _ = v4.observe(a, b, v4.world(0, 1), v4.world(0.03, 1), 1)
    assert observation["raw_normalized"] == pytest.approx(
        [
            s + w
            for s, w in zip(
                observation["self_motion_raw"],
                observation["external_motion_raw"],
                strict=True,
            )
        ],
        abs=1e-14,
    )
    with pytest.raises(ValueError):
        v4.observe(a, ([float("nan"), 0, 0], 0), v4.world(0, 1), v4.world(0.03, 1), 1)
    with pytest.raises(ValueError):
        v4.observe(a, (b[0], 4), v4.world(0, 1), v4.world(0.03, 1), 1)


@pytest.fixture(scope="module")
def cases():
    return {
        name: v4.run_reference(motion, events, apply, 401)
        for name, motion, events, apply in [
            ("static", 0, (), True),
            ("moving", 1, (), True),
            ("reverse", -1, (), True),
            ("off", 1, (), False),
            ("events", 1, ((100, 0), (200, -1), (350, 1)), True),
        ]
    }


def test_static_geometry_is_existing_v3_model(cases):
    reference = old.run_reference()
    for a, b in zip(cases["static"]["frames"][:-1], reference["frames"], strict=False):
        assert a["position"] == b["position"]
        assert a["orientation"] == b["orientation"]
        assert a["neural_summary"] == b["neural_summary"]
        for key, value in b["sensory_summary"].items() if b["sensory_summary"] else []:
            assert a["sensory_summary"][key] == value


def test_controls_causal_response_and_neural_off(cases):
    assert all(c["neural_substeps"] == 401 * 200 for c in cases.values())
    assert cases["moving"]["frames"][0]["neural_summary"]["hs_states"] == [0] * 6
    assert cases["moving"]["frames"][1]["sensory_summary"]["external_motion_raw"] != [
        0,
        0,
    ]
    assert (
        cases["moving"]["frames"][2]["neural_summary"]
        != cases["static"]["frames"][2]["neural_summary"]
    )
    assert (
        cases["moving"]["frames"][400]["orientation"]
        != cases["static"]["frames"][400]["orientation"]
    )
    assert (
        cases["reverse"]["frames"][400]["orientation"]
        != cases["moving"]["frames"][400]["orientation"]
    )
    off = cases["off"]["frames"]
    assert all(f["boundary_summary"]["neural_omega"] == 0 for f in off)
    assert any(f["neural_summary"]["mean_yaw_drive_eq"] for f in off[:-1])
    assert all(
        f["propulsion_model_value"] == 0.18 for c in cases.values() for f in c["frames"]
    )


def test_stop_reverse_no_teleport_or_neural_reset(cases):
    f = cases["events"]["frames"]
    assert f[100]["stimulus_summary"]["phase"] == pytest.approx(math.pi)
    assert f[100]["stimulus_summary"]["x"] == f[200]["stimulus_summary"]["x"]
    assert f[200]["stimulus_summary"]["phase"] == f[100]["stimulus_summary"]["phase"]
    assert any(f[200]["neural_summary"]["hs_states"])
    assert f[200]["sensory_summary"]["external_motion_raw"] == [0, 0]
    assert f[201]["sensory_summary"]["external_motion_raw"] != [0, 0]
    assert f[100]["neural_summary"] == cases["moving"]["frames"][100]["neural_summary"]
    assert (
        v4.run_reference(1, ((100, 0), (200, -1), (350, 1)), stop=401)
        == cases["events"]
    )


@pytest.mark.parametrize(
    "events", [((2, 2),), ((2, 1),), ((3, 0), (2, -1)), ((400, 0),)]
)
def test_invalid_events_rejected(events):
    with pytest.raises(ValueError):
        v4.run_reference(events=events, stop=400)
