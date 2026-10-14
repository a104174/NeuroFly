"""Independent Python reference for deterministic engineering boundary navigation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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
SCHEMA = "continuous_arena_navigation_reference_v3"
POLICY = {
    "version": "GEOMETRIC_INWARD_NORMAL_V1",
    "margin": 0.06,
    "gain": 2,
    "max_omega": 1.2,
    "duration_s": 30,
    "release": "NO_OUTWARD_COMPONENT_AT_BOUNDARY",
    "tie": "POSITIVE_PI",
    "combined": "SUM_NO_ADDITIONAL_CLAMP",
}


def boundary_steering(x, z, heading, limits):
    if (
        len(limits) != 2
        or not all(math.isfinite(v) for v in (x, z, heading, *limits))
        or min(limits) <= POLICY["margin"]
        or abs(x) > limits[0]
        or abs(z) > limits[1]
    ):
        raise ValueError("Invalid navigation geometry/state")
    distances = [limits[0] - x, limits[0] + x, limits[1] - z, limits[1] + z]
    weights = [max(0, 1 - d / POLICY["margin"]) for d in distances]
    inward = [weights[1] - weights[0], weights[3] - weights[2]]
    active = math.hypot(*inward) > 0
    angle = math.atan2(inward[0], inward[1]) - heading if active else 0
    error = math.atan2(math.sin(angle), math.cos(angle))
    if abs(abs(error) - math.pi) < 1e-12:
        error = math.pi
    omega = max(-1.2, min(1.2, POLICY["gain"] * error * max(weights)))
    return {
        "distances": distances,
        "inward": inward,
        "omega": omega,
        "heading_error": error,
        "active": active,
    }


def velocity(pos, heading, limits):
    x, _, z = pos
    vx, vz = 0.18 * math.sin(heading), 0.18 * math.cos(heading)
    wall = None
    if (x >= limits[0] and vx > 1e-12) or (x <= -limits[0] and vx < -1e-12):
        wall = "X_WALL"
    elif (z >= limits[1] and vz > 1e-12) or (z <= -limits[1] and vz < -1e-12):
        wall = "Z_WALL"
    return ([0, 0, 0] if wall else [vx, 0, vz]), wall


def run_reference(events=(), apply=True, initial=None):
    """New policy; frozen observation and 200-substep neural adapter reused."""
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
        if type(step) is not int or not previous_step < step < 1500:
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
    if initial is not None:
        pos, heading = list(initial["position"]), initial["heading"]
        if len(pos) != 3 or pos[1] != base["initial_position"][1]:
            raise ValueError("Invalid initial altitude")
        boundary_steering(pos[0], pos[2], heading, limits)
    stats = dict(
        contacts=0,
        recoveries=0,
        contactSeconds=0.0,
        maxStallSeconds=0.0,
        neuralHeadingChange=0.0,
        boundaryHeadingChange=0.0,
    )
    active_contact, stall = False, 0.0
    previous, contact, neural = None, None, v1.NeuralState()
    distance, plane, frames, log = 0.0, 0.4, [], []
    dt = base["dt_s"]
    for n in range(1501):
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
        linear_velocity, contact = velocity(pos, heading, limits)
        boundary = boundary_steering(pos[0], pos[2], heading, limits)
        start = neural
        if n < 1500:
            neural, readout = v1.advance_neural(neural, sides, 20.0, components)
            raw_omega = 2.5 * readout["orientation_increment_eq"] / dt
            neural_omega = max(-0.5, min(0.5, raw_omega)) if apply else 0.0
            omega = neural_omega + boundary["omega"]
            stats["neuralHeadingChange"] += neural_omega * dt
            stats["boundaryHeadingChange"] += boundary["omega"] * dt
        else:
            raw_omega, omega, neural_omega = 0.0, 0.0, 0.0
            boundary["omega"] = 0.0
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
                "linear_velocity": linear_velocity,
                "angular_velocity": omega,
                "contact": contact,
                "propulsion_model_value": base["speed"],
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
                "steering_clipped": raw_omega != max(-0.5, min(0.5, raw_omega)),
                "distance": distance,
                "visual_plane_z": plane,
            }
        )
        if n < 1500:
            previous = (pos.copy(), heading)
            pos, moved = body.advance_position(pos, linear_velocity, dt, limits)
            distance += moved
            heading += omega * dt
            if contact:
                stats["contactSeconds"] += dt
                stall += dt
                stats["maxStallSeconds"] = max(stats["maxStallSeconds"], stall)
            else:
                stall = 0.0
            _, next_contact = velocity(pos, heading, limits)
            if next_contact and not active_contact:
                stats["contacts"] += 1
            if not next_contact and active_contact:
                stats["recoveries"] += 1
            active_contact = bool(next_contact)
    return {
        "schema": SCHEMA,
        "source_artifact_id": authority["artifact_id"],
        "source_raw_sha256": SOURCE_RAW,
        "source_config_sha256": authority["config_sha256"],
        "events": log,
        "frames": frames,
        "neural_substeps": 300000,
        "policy": POLICY,
        "statistics": stats,
        "random_policy": "NONE",
        "termination": "DURATION_COMPLETED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = [
        ("B", (), True, None),
        ("C", (), False, None),
        ("D", ((100, -0.4),), True, None),
        (
            "corner",
            (),
            True,
            {
                "position": [
                    0.9654288893949121,
                    0.11032208074629306,
                    0.37542888939491215,
                ],
                "heading": math.pi / 4,
            },
        ),
        (
            "head_on",
            (),
            True,
            {
                "position": [0.9654288893949121, 0.11032208074629306, 0],
                "heading": math.pi / 2,
            },
        ),
    ]
    references = {}
    for name, events, apply, initial in cases:
        data = run_reference(events, apply, initial)
        full = args.output.parent / (name + "-full.json")
        full.write_bytes(canonical_json_bytes(data, newline=True))
        first = next(f["step"] for f in data["frames"] if f["contact"])
        release = next(
            f["step"] for f in data["frames"] if f["step"] > first and not f["contact"]
        )
        steps = {0, 1, 99, 100, 101, 250, 400, 750, 1000, 1499, 1500}
        steps.update(range(first - 1, first + 2))
        steps.update(range(release - 1, release + 2))
        data["frames"] = [f for f in data["frames"] if f["step"] in steps]
        data["initial"] = initial
        references[name] = data
    out = {
        "schema": SCHEMA,
        "cases": references,
        "reference_sha256": canonical_sha256(references),
    }
    args.output.write_text(
        json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n"
    )
    print(out["reference_sha256"])


if __name__ == "__main__":
    main()
