"""Independent clock/reference and causal tests; no biological motor claims."""

import copy
import json
import math

import numpy as np
import pytest

from neurofly import experimental_locomotion as body
from neurofly import experimental_neural_locomotion as model
from neurofly import exploratory_course_control as course
from neurofly.orientation_to_horizontal_motion import SideDescriptors
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256


@pytest.fixture(scope="module")
def artifact():
    return model.build()


@pytest.fixture(scope="module")
def components():
    return course.load_components(course.load_preregistration())


def test_200_substeps_against_independent_affine_matrix_power(components, monkeypatch):
    initial = model.NeuralState((0.1, 0.2, -0.1, 0.05, 0.15, -0.2), (0.12, -0.08))
    inputs = SideDescriptors(0.3, -0.2)
    # State [six HS, DN_R, DN_L, cumulative orientation_eq, affine constant].
    # The two leaks are exact ZOH; DN reads OLD HS, and yaw reads OLD DN.
    a, b = math.exp(-0.1 / 5), math.exp(-0.1 / 10)
    matrix = np.eye(10)
    for i in range(6):
        matrix[i, i] = a
        matrix[i, 9] = (1 - a) * (0.3 if i < 3 else -0.2)
    for row, indices in [(6, range(3)), (7, range(3, 6))]:
        matrix[row, row] = b
        for col in indices:
            matrix[row, col] = (1 - b) / 3
    matrix[8, 6], matrix[8, 7] = 0.1 / 50, -0.1 / 50
    expected = np.linalg.matrix_power(matrix, 200) @ np.array(
        [*initial.hs, *initial.dnp15, 0, 1]
    )
    calls = []
    actual_kernel = course.compose_neural_interval

    def tracked(hs, dn, sides, dt, comp):
        calls.append(dt)
        return actual_kernel(hs, dn, sides, dt, comp)

    monkeypatch.setattr(course, "compose_neural_interval", tracked)
    state, summary = model.advance_neural(initial, inputs, 20, components)
    assert calls == [0.1] * 200
    assert summary["substeps"] == 200
    np.testing.assert_allclose([*state.hs, *state.dnp15], expected[:8], atol=1e-12)
    assert summary["orientation_increment_eq"] == pytest.approx(expected[8], abs=1e-12)
    assert summary["mean_yaw_drive_eq"] == pytest.approx(expected[8] * 50 / 20)


def test_continuous_state_and_no_repeated_substeps(components):
    sides = SideDescriptors(0.2, -0.1)
    once, a = model.advance_neural(model.NeuralState(), sides, 40, components)
    half, b = model.advance_neural(model.NeuralState(), sides, 20, components)
    twice, c = model.advance_neural(half, sides, 20, components)
    assert once == twice
    assert a["orientation_increment_eq"] == pytest.approx(
        b["orientation_increment_eq"] + c["orientation_increment_eq"], abs=1e-14
    )
    assert a["substeps"] == b["substeps"] + c["substeps"] == 400


@pytest.mark.parametrize(
    "duration", [None, float("nan"), float("inf"), 0, -1, 0.15, 2000]
)
def test_invalid_clock_rejected(duration, components):
    with pytest.raises(ValueError):
        model.advance_neural(
            model.NeuralState(), SideDescriptors(0, 0), duration, components
        )


def test_identity_pins_and_v0_preservation(artifact):
    c = artifact["config"]
    assert [n["body_id"] for n in c["sources"]["neural"]["source_identities"]] == [
        10015,
        10016,
        10023,
        10034,
        10181,
        10419,
    ]
    assert [n["body_id"] for n in c["sources"]["neural"]["target_identities"]] == [
        11215,
        12069,
    ]
    assert (
        c["v0_artifact_id"]
        == "c33154916a33f3c88ba9d7421e0337e74b6def01eff674483427d4a0e8c64509"
    )
    assert (
        c["v0_raw_sha256"]
        == "fc6d9882af59e63b4000d2426cc954342ce810ac2094f1e90f92d2d26cf2f893"
    )
    body.validate_artifact(json.loads(body.OUTPUT.read_bytes()))
    assert c["sources"]["neural"]["transfer"]["structural_count_is_efficacy"] is False


def test_intervention_is_sensory_then_neural_then_heading_not_authored_path(artifact):
    a, b, off, d = artifact["result"]["runs"]
    # At boundary 1 all runs have the identical actual pose and neural state.
    # Only the world plane differs. Independent atan2 bearing differences verify input.
    for run in (b, off, d):
        f0, f1, f2 = run["frames"][:3]
        assert f1["position"] == a["frames"][1]["position"]
        assert f1["orientation"] == math.pi / 2
        shifts = []
        for x in (0.6, -0.6):
            z = run["condition"]["plane_z"]
            shifts.append(
                math.atan2(x - f1["position"][0], z - f1["position"][2])
                - math.atan2(x - f0["position"][0], z - f0["position"][2])
            )
        sensory = f1["sensory_summary"]
        assert sensory["right"] == pytest.approx(50 / 20 * shifts[0] / math.tau)
        assert sensory["left"] == pytest.approx(-50 / 20 * shifts[1] / math.tau)
        assert sensory["pose_origin"].startswith("PYTHON_COMPUTED")
        raw_omega = 2.5 * f1["neural_summary"]["orientation_increment_eq"] / 0.02
        expected = max(-0.5, min(0.5, raw_omega)) if run["condition"]["apply"] else 0
        assert f1["angular_velocity"] == expected
        assert f2["orientation"] == f1["orientation"] + expected * 0.02
    assert b["frames"][1]["neural_summary"] == off["frames"][1]["neural_summary"]
    assert b["frames"][1]["sensory_summary"] != d["frames"][1]["sensory_summary"]
    assert (
        b["frames"][1]["neural_summary"]["mean_yaw_drive_eq"]
        != d["frames"][1]["neural_summary"]["mean_yaw_drive_eq"]
    )
    assert b["frames"][2]["orientation"] != d["frames"][2]["orientation"]
    # The changed headings subsequently alter the next observation (feedback).
    assert b["frames"][2]["sensory_summary"]["heading_increment_eq"] != 0
    assert off["frames"][2]["sensory_summary"]["heading_increment_eq"] == 0
    assert artifact["result"]["causal_metrics"]["visual_intervention_max_position"] > 0


def test_all_body_intervals_bounds_clocks_propulsion_and_controls(artifact):
    c = artifact["config"]["body"]
    lx, lz = body.validate_config(c)
    baseline, _, off, _ = artifact["result"]["runs"]
    for run in artifact["result"]["runs"]:
        assert len(run["frames"]) == 401 and run["speed"] == 0.18
        assert run["neural_substeps"] == (80000 if run["condition"]["neural"] else 0)
        for n, frame in enumerate(run["frames"]):
            assert frame["time"] == n * 0.02 and frame["step"] == n
            assert abs(frame["position"][0]) <= lx and abs(frame["position"][2]) <= lz
            assert frame["position"][1] == c["initial_position"][1]
            assert frame["propulsion_model_value"] == 0.18
            assert abs(frame["angular_velocity"]) <= 0.5
            if frame["contact"]:
                assert frame["linear_velocity"] == [0.0, 0.0, 0.0]
            if frame["neural_summary"]:
                assert frame["neural_summary"]["substeps"] == (200 if n < 400 else 0)
            if n < 400:
                following = run["frames"][n + 1]
                assert (
                    following["orientation"]
                    == frame["orientation"] + frame["angular_velocity"] * 0.02
                )
                vx, _, vz = frame["linear_velocity"]
                assert following["position"][0] == max(
                    -lx, min(lx, frame["position"][0] + vx * 0.02)
                )
                assert following["position"][2] == max(
                    -lz, min(lz, frame["position"][2] + vz * 0.02)
                )
    assert all(
        x["position"] == y["position"] and x["orientation"] == y["orientation"]
        for x, y in zip(baseline["frames"], off["frames"], strict=True)
    )
    # Same actual speed, never an independent neural translational contribution.
    for r in artifact["result"]["runs"]:
        assert all(
            math.hypot(*f["linear_velocity"]) == pytest.approx(0.18)
            for f in r["frames"]
            if not f["contact"]
        )


def test_complete_public_artifact_reproduces(artifact):
    assert json.loads(model.OUTPUT.read_bytes()) == artifact


@pytest.mark.parametrize("field", ["substeps", "source_id", "position", "gain"])
def test_recomputed_hash_does_not_authorize_contradictory_telemetry(artifact, field):
    tampered = copy.deepcopy(artifact)
    if field == "substeps":
        tampered["result"]["runs"][1]["frames"][1]["neural_summary"]["substeps"] = 199
    elif field == "position":
        tampered["result"]["runs"][1]["frames"][1]["position"][0] += 0.1
    elif field == "source_id":
        tampered["config"]["sources"]["neural"]["source_identities"][0]["body_id"] = 1
    else:
        tampered["config"]["policy"]["steering_gain_rad_per_orientation_eq"] = 3
    for key in ("config", "result"):
        tampered[key + "_sha256"] = canonical_sha256(tampered[key])
    tampered["artifact_id"] = canonical_sha256(
        {
            "config_sha256": tampered["config_sha256"],
            "result_sha256": tampered["result_sha256"],
        }
    )
    with pytest.raises(ValueError, match="semantic"):
        model.validate(tampered)
