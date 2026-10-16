"""v4 relative-world observation; frozen HS/DNp15 transition and v3 plant reused."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from neurofly import continuous_arena_navigation_reference as nav
from neurofly import experimental_locomotion as body
from neurofly import experimental_neural_locomotion as v1
from neurofly import exploratory_course_control as course
from neurofly.orientation_to_horizontal_motion import SideDescriptors
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

POLICY_PATH = body.ROOT / "docs/science/moving_visual_stimuli_v4_policy.json"
POLICY_SHA = "65c334f0ddd3c769824d0449ed33da5e00c04c71fa56043091ebf2e23ff0a28b"


def load_policy():
    raw = POLICY_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != POLICY_SHA:
        raise ValueError("v4 policy identity mismatch")
    return json.loads(raw)


def world(phase, direction):
    if (
        not math.isfinite(phase)
        or type(direction) is not int
        or direction not in (-1, 0, 1)
    ):
        raise ValueError("invalid stimulus")
    return {
        "phase": phase,
        "motion": direction,
        "x": [x + 0.08 * math.sin(phase) for x in (0.6, -0.6)],
        "z": 0.4,
        "velocity_x": direction * 0.08 * 2 * math.pi / 4 * math.cos(phase),
    }


def bearing(bx, bz, ax, az):
    dx, dz = bx - ax, bz - az
    squared = dx * dx + dz * dz
    fraction = max(0, min(1, (bx * dx + bz * dz) / squared)) if squared else 0
    if math.hypot(bx - fraction * dx, bz - fraction * dz) <= 1e-9:
        raise ValueError("singular relative geometry")
    shift = math.atan2(bz * ax - bx * az, bx * ax + bz * az)
    if abs(shift) >= math.pi:
        raise ValueError("ambiguous bearing")
    return shift


def observe(previous, current, old_world, new_world, n):
    if previous is None:
        return None, SideDescriptors(0.0, 0.0)
    before, bh = previous
    after, ah = current
    if not all(
        math.isfinite(v)
        for v in (*before, *after, bh, ah, *old_world["x"], *new_world["x"])
    ):
        raise ValueError("nonfinite geometry")
    dt = n * 0.02 * 1000 - (n - 1) * 0.02 * 1000
    dh = ah / math.tau - bh / math.tau
    if abs(dh) >= 0.5:
        raise ValueError("ambiguous heading")
    raw, shifts, own, external = [], [], [], []
    for i in range(2):
        bx, bz = old_world["x"][i] - before[0], old_world["z"] - before[2]
        sx, sz = old_world["x"][i] - after[0], old_world["z"] - after[2]
        ax, az = new_world["x"][i] - after[0], new_world["z"] - after[2]
        shift = bearing(bx, bz, ax, az)
        relative = shift / math.tau - dh
        if abs(relative) >= 0.5:
            raise ValueError("ambiguous relative motion")
        side = 1 if i == 0 else -1
        shifts.append(shift)
        raw.append(50 * (relative / dt) * side)
        own.append((bearing(bx, bz, sx, sz) / math.tau - dh) * (50 / dt * side))
        external.append(bearing(sx, sz, ax, az) / math.tau * (50 / dt * side))
    bounded = [max(-1, min(1, v)) for v in raw]
    return {
        "before_step": n - 1,
        "available_step": n,
        "interval_ms": dt,
        "right": bounded[0],
        "left": bounded[1],
        "raw_normalized": raw,
        "bearing_shift_rad": shifts,
        "clipped": [v != b for v, b in zip(raw, bounded, strict=True)],
        "heading_increment_eq": dh,
        "pose_origin": "PYTHON_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY",
        "self_motion_raw": own,
        "external_motion_raw": external,
        "previous_landmarks": {"x": old_world["x"].copy(), "z": old_world["z"]},
        "current_landmarks": {"x": new_world["x"].copy(), "z": new_world["z"]},
    }, SideDescriptors(*bounded)


def run_reference(initial_motion=1, events=(), apply=True, stop=1500):
    load_policy()
    if (
        type(initial_motion) is not int
        or initial_motion not in (-1, 0, 1)
        or type(stop) is not int
        or not 0 <= stop <= 1500
    ):
        raise ValueError("invalid v4 condition")
    prior, motion = -1, initial_motion
    for step, value in events:
        if (
            type(step) is not int
            or not prior < step < stop
            or type(value) is not int
            or value not in (-1, 0, 1)
            or value == motion
        ):
            raise ValueError("invalid motion event")
        prior, motion = step, value
    raw = v1.OUTPUT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != nav.SOURCE_RAW:
        raise ValueError("v1 source mismatch")
    c = json.loads(raw)["config"]
    components = course.load_components(course.load_preregistration())
    for key, contract in (
        ("neural", components.neural_contract),
        ("yaw", components.embodiment_contract),
    ):
        if canonical_sha256(contract) != c["source_sha256"][key]:
            raise ValueError("source contract mismatch")
    limits = body.validate_config(c["body"])
    pos, heading = (
        c["body"]["initial_position"].copy(),
        c["body"]["initial_heading_rad"],
    )
    previous, neural, phase, old_phase, motion = (
        None,
        v1.NeuralState(),
        0.0,
        0.0,
        initial_motion,
    )
    event_map, applied, frames = dict(events), [], []
    distance = 0.0
    for n in range(stop + 1):
        # At a paused endpoint a requested event has not begun an interval.
        if n in event_map:
            new = event_map[n]
            applied.append(
                {"step": n, "time": n * 0.02, "old_motion": motion, "new_motion": new}
            )
            motion = new
        geometry = world(phase, motion)
        sensory, sides = observe(
            previous, (pos, heading), world(old_phase, motion), geometry, n
        )
        velocity, contact = nav.velocity(pos, heading, limits)
        boundary = nav.boundary_steering(pos[0], pos[2], heading, limits)
        start = neural
        if n < stop:
            neural, readout = v1.advance_neural(neural, sides, 20.0, components)
            raw_omega = 2.5 * readout["orientation_increment_eq"] / 0.02
            bounded = max(-0.5, min(0.5, raw_omega))
            neural_omega = bounded if apply else 0.0
            omega = neural_omega + boundary["omega"]
        else:
            readout = {
                "substeps": 0,
                "orientation_increment_eq": None,
                "mean_yaw_drive_eq": None,
            }
            raw_omega, bounded, neural_omega, omega = 0.0, 0.0, 0.0, 0.0
            boundary["omega"] = 0.0
        frames.append(
            {
                "step": n,
                "time": n * 0.02,
                "position": pos.copy(),
                "orientation": heading,
                "linear_velocity": velocity,
                "angular_velocity": omega,
                "contact": contact,
                "propulsion_model_value": 0.18,
                "steering_model_value": neural_omega,
                "boundary_summary": {**boundary, "neural_omega": neural_omega},
                "sensory_summary": sensory,
                "neural_summary": {
                    "hs_states": list(start.hs),
                    "dnp15_states": list(start.dnp15),
                    **readout,
                },
                "model_mode": v1.MODE if apply else "EXPERIMENTAL_KINEMATIC_ONLY",
                "steering_applied": apply,
                "steering_clipped": raw_omega != bounded,
                "distance": distance,
                "stimulus_summary": geometry,
            }
        )
        if n < stop:
            previous = (pos.copy(), heading)
            pos, moved = body.advance_position(pos, velocity, 0.02, limits)
            distance += moved
            heading += omega * 0.02
            old_phase, phase = phase, phase + motion * 2 * math.pi * 0.02 / 4
    return {
        "schema": "moving_visual_stimulus_reference_v4",
        "policy_sha256": POLICY_SHA,
        "source_artifact_id": json.loads(raw)["artifact_id"],
        "events": applied,
        "frames": frames,
        "neural_substeps": stop * 200,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = {}
    for name, direction, events, apply in (
        ("static", 0, (), True),
        ("moving", 1, (), True),
        ("reverse", -1, (), True),
        ("off", 1, (), False),
        ("events", 1, ((100, 0), (200, -1), (350, 1)), True),
    ):
        data = run_reference(direction, events, apply)
        full = args.output.parent / (name + "-full.json")
        full.write_text(json.dumps(data, separators=(",", ":")) + "\n")
        selected = {
            0,
            1,
            2,
            99,
            100,
            101,
            199,
            200,
            201,
            250,
            349,
            350,
            351,
            400,
            750,
            1000,
            1499,
            1500,
        }
        contacts = [f["step"] for f in data["frames"] if f["contact"]]
        if contacts:
            selected.update(range(max(0, contacts[0] - 1), contacts[0] + 2))
        data["frames"] = [f for f in data["frames"] if f["step"] in selected]
        cases[name] = data
    args.output.write_text(
        json.dumps(
            {
                "schema": "moving_visual_stimulus_reference_v4",
                "cases": cases,
                "reference_sha256": canonical_sha256(cases),
            },
            separators=(",", ":"),
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
