"""Multirate HS/DNp15 steering with separate engineering propulsion."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

from neurofly import experimental_locomotion as body
from neurofly import exploratory_course_control as course
from neurofly import planar_motion_observation as spatial
from neurofly.orientation_to_horizontal_motion import SideDescriptors
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

SCHEMA = "experimental_neural_locomotion_replay_v1"
EXPERIMENT = "EXPERIMENTAL_LOCOMOTION_V1"
MODE = "CONNECTOME_INFORMED_NEURAL_STEERING"
POLICY = body.ROOT / "docs/science/experimental_locomotion_v1_policy.json"
OUTPUT = body.ROOT / "web/public/experiments/experimental_locomotion_v1.json"


@dataclass(frozen=True)
class NeuralState:
    hs: tuple[float, ...] = (0.0,) * 6
    dnp15: tuple[float, ...] = (0.0,) * 2


def load_policy():
    p = json.loads(POLICY.read_bytes())
    if p != declared_policy():
        raise ValueError("unsupported multirate policy")
    return p


def declared_policy():
    return {
        "experiment_id": EXPERIMENT,
        "schema_version": SCHEMA,
        "body_dt_ms": 20.0,
        "neural_dt_ms": 0.1,
        "neural_substeps_per_interval": 200,
        "duration_s": 8.0,
        "sensory_hold": "PREVIOUS_COMPLETED_POSE_INTERVAL_HELD_FOR_200_SUBSTEPS",
        "initial_observation": "ZERO_NO_COMPLETED_MOTION",
        "observer_input_bridge": (
            "COMPUTED_BODY_SNAPSHOTS_TO_FROZEN_ENGINEERING_POSE_DTO"
        ),
        "pose_origin": "PYTHON_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY",
        "coordinate_bridge": "ONE_DISPLAY_UNIT_EQUALS_ONE_OBSERVER_WORLD_EQ_ASSUMPTION",
        "heading_bridge": "RADIANS_DIVIDED_BY_TWO_PI_UNWRAPPED_ORIENTATION_EQ",
        "neural_update": "OLD_STATE_SIMULTANEOUS_0_1_MS_FROZEN_KERNEL",
        "readout": "SUM_PROPOSED_ORIENTATION_INCREMENT_EQ_OVER_SUBSTEPS",
        "steering_gain_rad_per_orientation_eq": 2.5,
        "max_abs_angular_velocity_rad_s": 0.5,
        "gain_basis": "ENGINEERING_REFERENCE_0_01_HELD_YAW_DRIVE_MAPS_TO_0_5_RAD_S",
        "steering_equation": "omega=clip(2.5*sum_increment_eq/body_dt_s,-0.5,0.5)",
        "body_update": "LEFT_HEADING_TRANSLATION_THEN_HEADING_INCREMENT_THEN_CONTACT",
        "contact": "V0_LATCH_TRANSLATION_STOP_NEURAL_AND_HEADING_CONTINUE",
        "landmark_x": [0.6, -0.6],
        "primary_landmark_plane_z": 0.4,
        "intervention_landmark_plane_z": -0.4,
        "conditions": [
            {
                "id": "ENGINEERING_BASELINE",
                "neural": False,
                "apply": False,
                "plane_z": 0.4,
            },
            {"id": "NEURAL_STEERING", "neural": True, "apply": True, "plane_z": 0.4},
            {
                "id": "NEURAL_OUTPUT_DISABLED",
                "neural": True,
                "apply": False,
                "plane_z": 0.4,
            },
            {
                "id": "VISUAL_PLANE_INTERVENTION",
                "neural": True,
                "apply": True,
                "plane_z": -0.4,
            },
        ],
        "random_policy": "NONE",
        "physiology": "UNCALIBRATED_MODEL_NO_GAIT_MUSCLE_OR_WALL_SENSING",
    }


def advance_neural(state: NeuralState, sides: SideDescriptors, duration_ms, components):
    """Use the frozen composed transition once per actual 0.1-ms substep."""
    dt = components.neural_contract["dt_ms"]
    if not body.finite(duration_ms) or duration_ms <= 0:
        raise ValueError("invalid neural interval/grid/state")
    ratio = duration_ms / dt
    if (
        type(state) is not NeuralState
        or not body.finite(duration_ms)
        or duration_ms <= 0
        or abs(ratio - round(ratio)) > 1e-9
        or dt != 0.1
        or round(ratio) > 10000
    ):
        raise ValueError("invalid neural interval/grid/state")
    hs, dn = list(state.hs), list(state.dnp15)
    increment, drive_sum = 0.0, 0.0
    count = round(ratio)
    for _ in range(count):
        step = course.compose_neural_interval(hs, dn, sides, dt, components)
        increment += step["proposed_orientation_increment_eq"]
        drive_sum += step["yaw_drive_eq"]
        hs, dn = step["next_sources"], step["next_targets"]
    return NeuralState(tuple(hs), tuple(dn)), {
        "substeps": count,
        "orientation_increment_eq": increment,
        "mean_yaw_drive_eq": drive_sum / count,
    }


def observation(previous, current, geometry, n, dt):
    if previous is None:
        return None, SideDescriptors(0.0, 0.0)
    # The frozen DTO's prescribed tag describes caller-supplied engineering pose
    # samples. This bridge does NOT claim the generated trajectory was prescribed.
    poses = [
        spatial.PoseBoundary(i, i * dt * 1000, p[0], p[2], theta / math.tau)
        for i, (p, theta) in zip((n - 1, n), (previous, current), strict=True)
    ]
    observed = spatial.observe_interval(geometry, *poses)
    return {
        "before_step": n - 1,
        "available_step": n,
        "interval_ms": observed.dt_ms,
        "right": observed.sides.right,
        "left": observed.sides.left,
        "raw_normalized": [s.normalized_side_descriptor for s in observed.samples],
        "clipped": [s.clipped for s in observed.samples],
        "bearing_shift_rad": [
            s.world_bearing_shift_rad_model for s in observed.samples
        ],
        "heading_increment_eq": observed.heading_increment_eq,
        "pose_origin": "PYTHON_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY",
    }, observed.sides


def run_condition(c, condition, components):
    base, p = c["body"], c["policy"]
    limits = body.validate_config(base)
    geometry = spatial.VisualGeometry(
        tuple(
            spatial.Landmark(name, side, x, condition["plane_z"])
            for name, side, x in zip(
                ("RIGHT_REFERENCE", "LEFT_REFERENCE"),
                ("R", "L"),
                p["landmark_x"],
                strict=True,
            )
        )
    )
    pos, theta = base["initial_position"].copy(), base["initial_heading_rad"]
    previous, contact, neural = None, None, NeuralState()
    distance, frames, events, steps = 0.0, [], [], 0
    dt, count = base["dt_s"], round(base["duration_s"] / base["dt_s"])
    for n in range(count + 1):
        sensory, sides = observation(previous, (pos, theta), geometry, n, dt)
        old_contact = contact
        velocity, contact = body.body_velocity(
            pos, theta, base["speed"], contact, limits
        )
        if contact and old_contact is None:
            events.append({"step": n, "time": n * dt, "wall": contact})
        summary = None
        omega, clipped = 0.0, False
        if condition["neural"]:
            start = neural
            if n < count:
                neural, readout = advance_neural(neural, sides, dt * 1000, components)
                steps += readout["substeps"]
                raw = (
                    p["steering_gain_rad_per_orientation_eq"]
                    * readout["orientation_increment_eq"]
                    / dt
                )
                bounded = max(
                    -p["max_abs_angular_velocity_rad_s"],
                    min(p["max_abs_angular_velocity_rad_s"], raw),
                )
                omega = bounded if condition["apply"] else 0.0
                clipped = raw != bounded
            else:
                readout = {
                    "substeps": 0,
                    "orientation_increment_eq": None,
                    "mean_yaw_drive_eq": None,
                }
            summary = {
                "hs_states": list(start.hs),
                "dnp15_states": list(start.dnp15),
                **readout,
            }
        frames.append(
            {
                "step": n,
                "time": n * dt,
                "position": pos.copy(),
                "orientation": theta,
                "linear_velocity": velocity,
                "angular_velocity": omega,
                "contact": contact,
                "propulsion_model_value": base["speed"],
                "steering_model_value": omega,
                "sensory_summary": sensory,
                "neural_summary": summary,
                "model_mode": MODE if condition["apply"] else body.MODE,
                "steering_applied": condition["apply"],
                "steering_clipped": clipped,
                "distance": distance,
            }
        )
        if n == count:
            break
        previous = (pos.copy(), theta)
        pos, moved = body.advance_position(pos, velocity, dt, limits)
        distance += moved
        theta += omega * dt
    return {
        "id": condition["id"],
        "speed": base["speed"],
        "condition": condition,
        "frames": frames,
        "contact_events": events,
        "distance": distance,
        "neural_substeps": steps,
        "termination_reason": "DURATION_COMPLETED",
    }


def configuration():
    p = load_policy()
    components = course.load_components(course.load_preregistration())
    spatial.load_preregistration()
    v0 = body.validate_artifact(json.loads(body.OUTPUT.read_bytes()))
    sources = {
        "neural": components.neural_contract,
        "yaw": components.embodiment_contract,
        "observation": json.loads(spatial.PREREGISTRATION_PATH.read_bytes()),
    }
    return {
        "body": body.configuration(),
        "policy": p,
        "policy_sha256": canonical_sha256(p),
        "sources": sources,
        "source_sha256": {k: canonical_sha256(v) for k, v in sources.items()},
        "v0_artifact_id": v0["artifact_id"],
        "v0_raw_sha256": hashlib.sha256(body.OUTPUT.read_bytes()).hexdigest(),
        "dataset": "male-cns:v1.0",
        "dataset_uuid": "4b2087c0fbe046bfaf0d60bc970e3e5d",
        "model_mode": MODE,
        "physiological_motor_mapping": "NOT_VALIDATED",
        "software_model": "neurofly.experimental_neural_locomotion.v1",
    }, components


def build():
    c, components = configuration()
    runs = [run_condition(c, cond, components) for cond in c["policy"]["conditions"]]
    a, b, off, altered = runs
    assert all(
        x["position"] == y["position"] and x["orientation"] == y["orientation"]
        for x, y in zip(a["frames"], off["frames"], strict=True)
    )
    result = {
        "runs": runs,
        "causal_metrics": {
            "disabled_matches_baseline": True,
            "enabled_vs_disabled_max_yaw_rad": max(
                abs(x["orientation"] - y["orientation"])
                for x, y in zip(b["frames"], off["frames"], strict=True)
            ),
            "visual_intervention_max_yaw_rad": max(
                abs(x["orientation"] - y["orientation"])
                for x, y in zip(b["frames"], altered["frames"], strict=True)
            ),
            "visual_intervention_max_readout": max(
                abs(
                    x["neural_summary"]["mean_yaw_drive_eq"]
                    - y["neural_summary"]["mean_yaw_drive_eq"]
                )
                for x, y in zip(b["frames"][:-1], altered["frames"][:-1], strict=True)
            ),
            "visual_intervention_max_position": max(
                math.dist(x["position"], y["position"])
                for x, y in zip(b["frames"], altered["frames"], strict=True)
            ),
        },
    }
    ch, rh = canonical_sha256(c), canonical_sha256(result)
    return {
        "schema": SCHEMA,
        "config": c,
        "result": result,
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256({"config_sha256": ch, "result_sha256": rh}),
    }


def validate(value):
    if canonical_json_bytes(value) != canonical_json_bytes(build()):
        raise ValueError("neural locomotion semantic replay mismatch")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        validate(json.loads(args.verify.read_bytes()))
        print("Full sensory/neural/body semantic replay verified")
    elif args.output:
        import time

        start = time.perf_counter()
        data = canonical_json_bytes(build(), newline=True)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)
        print(hashlib.sha256(data).hexdigest(), len(data), time.perf_counter() - start)
    else:
        parser.error("choose --output or --verify")


if __name__ == "__main__":
    main()
