import math

import pytest

from neurofly.neural_contribution_comparison_reference import (
    contact_events,
    paired_metrics,
    run_pair,
)


def tiny(heading, x, n):
    return dict(
        step=n, time=n * 0.02, position=[x, 0, 0], orientation=heading, distance=x
    )


def test_wrapped_maximum_between_samples():
    a = [tiny(math.pi - 0.1, 0, 0), tiny(math.pi + 0.1, 1, 1)]
    b = [tiny(0, 0, 0), tiny(0, 0, 1)]
    m = paired_metrics(a, b)
    assert m["max_wrapped_heading"]["value"] == math.pi
    assert m["max_wrapped_heading"]["time"] == pytest.approx(0.01)
    assert m["final_wrapped_heading"] == pytest.approx(-math.pi + 0.1)
    assert m["max_separation"] == dict(value=1, time=0.02)
    b[1]["time"] = 0.04
    with pytest.raises(ValueError):
        paired_metrics(a, b)


def test_contact_event_direction_and_initial_contact():
    frames = [
        dict(step=n, time=n * 0.02, contact=v)
        for n, v in enumerate([None, "X_WALL", "X_WALL", None, "Z_WALL", None])
    ]
    assert [(e["step"], e["kind"], e["wall"]) for e in contact_events(frames)] == [
        (1, "CONTACT", "X_WALL"),
        (3, "RECOVERY", "X_WALL"),
        (4, "CONTACT", "Z_WALL"),
        (5, "RECOVERY", "Z_WALL"),
    ]

    switch = [
        dict(step=n, time=n * 0.02, contact=v)
        for n, v in enumerate([None, "X_WALL", "Z_WALL", None])
    ]
    assert [(e["step"], e["kind"]) for e in contact_events(switch)] == [
        (1, "CONTACT"),
        (2, "WALL_CHANGE"),
        (3, "RECOVERY"),
    ]


@pytest.fixture(scope="module")
def reference():
    return run_pair(((100, -0.4),))


def test_real_paired_controls_and_causal_divergence(reference):
    a, b = reference["tracks"]
    assert a["frames"][0] == {
        **b["frames"][0],
        "model_mode": "CONNECTOME_INFORMED_NEURAL_STEERING",
        "steering_applied": True,
    }
    assert a["frames"][1]["neural_summary"] == b["frames"][1]["neural_summary"]
    assert (
        a["frames"][1]["boundary_summary"]["omega"]
        == b["frames"][1]["boundary_summary"]["omega"]
        == 0
    )
    assert a["frames"][1]["angular_velocity"] != b["frames"][1]["angular_velocity"]
    assert a["frames"][3]["position"] != b["frames"][3]["position"]
    assert a["frames"][200]["sensory_summary"] != b["frames"][200]["sensory_summary"]
    assert a["contact_events"] != b["contact_events"]
    assert any(f["neural_summary"]["mean_yaw_drive_eq"] for f in b["frames"])
    for track in [a, b]:
        assert len(track["frames"]) == 1501
        assert sum(f["neural_summary"]["substeps"] for f in track["frames"]) == 300000
        assert all(f["propulsion_model_value"] == 0.18 for f in track["frames"])
    assert all(f["boundary_summary"]["neural_omega"] == 0 for f in b["frames"])
    assert reference["metrics"]["max_wrapped_heading"]["value"] <= math.pi


@pytest.mark.parametrize("n", [0, 1501, 2.5])
def test_invalid_prefix(n):
    with pytest.raises(ValueError):
        run_pair(stop_step=n)
