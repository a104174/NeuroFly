"""Small switched-stimulus reference; frozen Python v1 kernels remain unchanged."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from neurofly import experimental_locomotion as body
from neurofly import experimental_neural_locomotion as v1
from neurofly import exploratory_course_control as course
from neurofly import planar_motion_observation as spatial
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

SOURCE_RAW = "17d335358a4f5cf4ed98b9682b103a81419cf82504203ce1bc72a7d76285d748"
SCHEMA = "interactive_neural_locomotion_reference_v2"
SAMPLE_STEPS = (
    0,
    1,
    2,
    99,
    100,
    101,
    102,
    103,
    150,
    200,
    250,
    269,
    275,
    300,
    350,
    399,
    400,
)


def run_reference(events=((100, -0.4),)):
    """Events apply BEFORE observation at the next uncomputed body boundary.

    Both endpoints of the completed movement are evaluated against the new fixed
    landmark geometry. No relocation flash or instantaneous pose change is added.
    The old-state HS/DNp15 update and all body functions are the Python v1 ones.
    """
    raw = v1.OUTPUT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_RAW:
        raise ValueError("source v1 raw identity mismatch")
    authority = json.loads(raw)
    c = authority["config"]
    components = course.load_components(course.load_preregistration())
    if canonical_sha256(components.neural_contract) != c["source_sha256"]["neural"]:
        raise ValueError("neural source mismatch")
    if canonical_sha256(components.embodiment_contract) != c["source_sha256"]["yaw"]:
        raise ValueError("yaw source mismatch")
    spatial.load_preregistration()
    previous_step, active_plane = -1, 0.4
    for step, plane in events:
        if type(step) is not int or not previous_step < step < 400:
            raise ValueError("unordered/invalid event step")
        if type(plane) not in (int, float) or plane not in (-0.4, 0.4):
            raise ValueError("invalid visual plane")
        if plane == active_plane:
            raise ValueError("duplicate stimulus event")
        previous_step, active_plane = step, plane
    event_map = dict(events)
    base, policy = c["body"], c["policy"]
    limits = body.validate_config(base)
    pos, heading = base["initial_position"].copy(), base["initial_heading_rad"]
    previous, contact, neural = None, None, v1.NeuralState()
    distance, plane, frames, log = 0.0, 0.4, [], []
    dt = base["dt_s"]
    for n in range(401):
        if n in event_map:
            new_plane = event_map[n]
            log.append(
                {"step": n, "time": n * dt, "old_plane": plane, "new_plane": new_plane}
            )
            plane = new_plane
        geometry = spatial.VisualGeometry(
            tuple(
                spatial.Landmark(name, side, x, plane)
                for name, side, x in zip(
                    ("RIGHT_REFERENCE", "LEFT_REFERENCE"),
                    ("R", "L"),
                    policy["landmark_x"],
                    strict=True,
                )
            )
        )
        sensory, sides = v1.observation(previous, (pos, heading), geometry, n, dt)
        velocity, contact = body.body_velocity(
            pos, heading, base["speed"], contact, limits
        )
        start = neural
        if n < 400:
            neural, readout = v1.advance_neural(neural, sides, 20.0, components)
            raw_omega = 2.5 * readout["orientation_increment_eq"] / dt
            omega = max(-0.5, min(0.5, raw_omega))
        else:
            raw_omega, omega = 0.0, 0.0
            readout = {
                "substeps": 0,
                "orientation_increment_eq": None,
                "mean_yaw_drive_eq": None,
            }
        frames.append(
            {
                "step": n,
                "time": n * dt,
                "position": pos.copy(),
                "orientation": heading,
                "linear_velocity": velocity,
                "angular_velocity": omega,
                "contact": contact,
                "propulsion_model_value": base["speed"],
                "steering_model_value": omega,
                "sensory_summary": sensory,
                "neural_summary": {
                    "hs_states": list(start.hs),
                    "dnp15_states": list(start.dnp15),
                    **readout,
                },
                "model_mode": v1.MODE,
                "steering_applied": True,
                "steering_clipped": raw_omega != omega,
                "distance": distance,
                "visual_plane_z": plane,
            }
        )
        if n < 400:
            previous = (pos.copy(), heading)
            pos, moved = body.advance_position(pos, velocity, dt, limits)
            distance += moved
            heading += omega * dt
    return {
        "schema": SCHEMA,
        "source_artifact_id": authority["artifact_id"],
        "source_raw_sha256": SOURCE_RAW,
        "source_config_sha256": authority["config_sha256"],
        "events": log,
        "frames": frames,
        "neural_substeps": 80000,
        "random_policy": "NONE",
        "termination": "DURATION_COMPLETED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    data = run_reference()
    if args.compact:
        data["frames"] = [f for f in data["frames"] if f["step"] in SAMPLE_STEPS]
        data["sampling"] = "SELECTED_COMPLETE_BOUNDARIES_NOT_A_REPLAY_TRAJECTORY"
    envelope = {"reference": data, "reference_sha256": canonical_sha256(data)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_json_bytes(envelope, newline=True))
    print(envelope["reference_sha256"])


if __name__ == "__main__":
    main()
