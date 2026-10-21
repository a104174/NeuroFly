"""The new harness reuses frozen Python kernels; it is not a flight solver."""

import copy

import pytest

from neurofly.neural_flight_reference import neural_reference


def stationary():
    return [
        {"step": n, "time": n * 0.02, "position": [0.0, 0.2, 0.0], "heading": 0.0}
        for n in range(4)
    ]


def test_neutral_reference_and_altitude_exclusion():
    frames = stationary()
    result = neural_reference(frames)
    assert result["substeps"] == 600
    assert all(row["mean_yaw_drive_eq"] == 0 for row in result["records"])
    assert all(row["hs_after"] == [0] * 6 for row in result["records"])
    raised = copy.deepcopy(frames)
    for n, frame in enumerate(raised):
        frame["position"][1] += n * 0.1
    assert neural_reference(raised) == result


def test_current_pose_heading_and_real_encoder_response():
    frames = stationary()
    frames[1]["heading"] = 0.01
    frames[2]["heading"] = 0.02
    frames[3]["heading"] = 0.03
    result = neural_reference(frames)
    assert result["records"][0]["observation"] is None
    assert result["records"][1]["observation"]["right"] < 0
    assert result["records"][1]["observation"]["left"] > 0
    assert result["records"][1]["mean_yaw_drive_eq"] < 0
    assert result["records"][2]["hs_before"] == result["records"][1]["hs_after"]
    assert result["flight_parity"] == "NOT_CLAIMED_PYTHON_NEURAL_AND_OBSERVER_ONLY"


@pytest.mark.parametrize("fault", ["grid", "nan", "missing", "plane"])
def test_invalid_reference_input_rejected(fault):
    frames = stationary()
    plane = 0.4
    if fault == "grid":
        frames[2]["time"] = 0.041
    elif fault == "nan":
        frames[1]["position"][0] = float("nan")
    elif fault == "missing":
        frames.pop(1)
    else:
        plane = 1.2
    with pytest.raises(ValueError):
        neural_reference(frames, plane)
