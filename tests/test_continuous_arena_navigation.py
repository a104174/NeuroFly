import math

import pytest

from neurofly.continuous_arena_navigation_reference import (
    boundary_steering,
    run_reference,
)


def test_normals_and_deterministic_head_on_tie():
    assert boundary_steering(0, 0, 0, (1, 0.4))["omega"] == 0
    assert boundary_steering(1, 0, math.pi / 2, (1, 0.4))["omega"] == 1.2
    b = boundary_steering(1, 0.4, math.pi / 4, (1, 0.4))
    assert b["inward"] == [-1, -1]
    assert b["omega"] == 1.2
    assert boundary_steering(1, 0, -math.pi / 2, (1, 0.4))["omega"] == 0


@pytest.mark.parametrize(
    "args", [(float("nan"), 0, 0, (1, 0.4)), (2, 0, 0, (1, 0.4)), (0, 0, 0, (0, 0.4))]
)
def test_invalid_geometry(args):
    with pytest.raises(ValueError):
        boundary_steering(*args)


@pytest.fixture(scope="module")
def reference():
    return run_reference(((100, -0.4),))


def test_authoritative_thirty_second_recovery(reference):
    assert len(reference["frames"]) == 1501
    assert reference["neural_substeps"] == 300000
    stats = reference["statistics"]
    assert stats["contacts"] > 0
    assert stats["recoveries"] > 0
    assert stats["maxStallSeconds"] < 5
    frames = reference["frames"]
    first = next(i for i, f in enumerate(frames) if f["contact"])
    later = next(i for i in range(first + 1, len(frames)) if not frames[i]["contact"])
    assert (
        math.dist(frames[later]["position"], frames[min(later + 100, 1500)]["position"])
        > 0.05
    )
    assert frames[-1]["distance"] > 2
    for n, f in enumerate(frames):
        assert f["time"] == n * 0.02
        assert abs(f["position"][0]) <= 0.9654288893949121
        assert abs(f["position"][2]) <= 0.37542888939491215
        assert abs(f["boundary_summary"]["omega"]) <= 1.2
        assert f["propulsion_model_value"] == 0.18
        assert (
            f["angular_velocity"]
            == f["boundary_summary"]["omega"] + f["boundary_summary"]["neural_omega"]
        )


def test_intervention_continuity_and_neural_off(reference):
    baseline = run_reference()
    off = run_reference(apply=False)
    assert (
        reference["frames"][100]["neural_summary"]["hs_states"]
        == baseline["frames"][100]["neural_summary"]["hs_states"]
    )
    assert (
        reference["frames"][101]["neural_summary"]
        != baseline["frames"][101]["neural_summary"]
    )
    assert (
        reference["frames"][200]["orientation"]
        != baseline["frames"][200]["orientation"]
    )
    assert off["statistics"]["recoveries"] > 0
    assert off["statistics"]["neuralHeadingChange"] == 0
    assert off["frames"][200]["orientation"] != baseline["frames"][200]["orientation"]
