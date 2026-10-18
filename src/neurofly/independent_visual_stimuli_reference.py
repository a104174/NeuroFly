"""Independent inputs using the v4 observer, frozen neural transition and v3 plant."""

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
from neurofly import moving_visual_stimuli_reference as v4
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

POLICY_PATH = body.ROOT / "docs/science/independent_visual_stimuli_v5_policy.json"
POLICY_SHA = "8a273ccd822c88c95a2f7383632385cfdb919c4f3c349eebc046bead19889296"
IDS = ("A", "B")
KINDS = ("START", "STOP", "REVERSE")


def load_policy():
    v4.load_policy()
    raw = POLICY_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != POLICY_SHA:
        raise ValueError("v5 policy mismatch")
    return json.loads(raw)


def control(state, kind):
    if kind not in KINDS:
        raise ValueError("invalid event kind")
    return {
        "enabled": kind == "START" if kind != "REVERSE" else state["enabled"],
        "direction": -state["direction"] if kind == "REVERSE" else state["direction"],
    }


def world(phases, controls):
    if (
        len(phases) != 2
        or len(controls) != 2
        or not all(math.isfinite(p) for p in phases)
    ):
        raise ValueError("invalid independent phases")
    landmarks = []
    for i, (phase, c) in enumerate(zip(phases, controls, strict=True)):
        if (
            set(c) != {"enabled", "direction"}
            or type(c["enabled"]) is not bool
            or type(c["direction"]) is not int
            or c["direction"] not in (-1, 1)
        ):
            raise ValueError("invalid independent control")
        x = (0.6 if i == 0 else -0.6) + 0.08 * math.sin(phase)
        landmarks.append(
            {
                "id": IDS[i],
                "anchor_x": 0.6 if i == 0 else -0.6,
                "amplitude": 0.08,
                "period_s": 4,
                "phase": phase,
                **c,
                "x": x,
                "velocity_x": (c["direction"] if c["enabled"] else 0)
                * 0.08
                * 2
                * math.pi
                / 4
                * math.cos(phase),
            }
        )
    return {"x": [s["x"] for s in landmarks], "z": 0.4, "landmarks": landmarks}


def run_reference(preset="synchronized", events=(), apply=True, stop=1500):
    policy = load_policy()
    if (
        preset not in policy["presets"]
        or type(apply) is not bool
        or type(stop) is not int
        or not 0 <= stop <= 1500
    ):
        raise ValueError("invalid v5 condition")
    initial = json.loads(json.dumps(policy["presets"][preset]))
    preview = json.loads(json.dumps(initial))
    prior = -1
    for step, stimulus, kind in events:
        if type(step) is not int or not prior <= step < stop or stimulus not in IDS:
            raise ValueError("invalid independent event")
        new = control(preview[IDS.index(stimulus)], kind)
        if new == preview[IDS.index(stimulus)]:
            raise ValueError("redundant event")
        preview[IDS.index(stimulus)] = new
        prior = step
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
    previous, neural, phases, old_phases, controls = (
        None,
        v1.NeuralState(),
        [0.0, 0.0],
        [0.0, 0.0],
        initial,
    )
    applied, frames = [], []
    event_map = {}
    for step, stimulus, kind in events:
        event_map.setdefault(step, []).append((stimulus, kind))
    distance = 0.0
    for n in range(stop + 1):
        for stimulus, kind in event_map.get(n, []):
            i = IDS.index(stimulus)
            old = controls[i].copy()
            controls[i] = control(old, kind)
            applied.append(
                {
                    "sequence": len(applied),
                    "step": n,
                    "time": n * 0.02,
                    "stimulus_id": stimulus,
                    "kind": kind,
                    "old_state": old,
                    "new_state": controls[i].copy(),
                }
            )
        geometry = world(phases, controls)
        sensory, sides = v4.observe(
            previous, (pos, heading), world(old_phases, controls), geometry, n
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
            old_phases = phases.copy()
            phases = [
                p + (c["direction"] if c["enabled"] else 0) * 2 * math.pi * 0.02 / 4
                for p, c in zip(phases, controls, strict=True)
            ]
    return {
        "schema": "independent_visual_stimulus_reference_v5",
        "policy_sha256": POLICY_SHA,
        "source_artifact_id": json.loads(raw)["artifact_id"],
        "events": applied,
        "frames": frames,
        "neural_substeps": stop * 200,
    }


CASES = {
    "stationary": ("stationary", (), True),
    "synchronized": ("synchronized", (), True),
    "opposing": ("opposing", (), True),
    "single": ("single", (), True),
    "off": ("opposing", (), False),
    "events": (
        "opposing",
        (
            (100, "A", "STOP"),
            (100, "B", "REVERSE"),
            (200, "A", "START"),
            (200, "A", "REVERSE"),
            (350, "B", "STOP"),
            (450, "B", "START"),
            (450, "B", "REVERSE"),
        ),
        True,
    ),
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    cases = {}
    for name, (preset, events, apply) in CASES.items():
        data = run_reference(preset, events, apply)
        (args.output.parent / (name + "-full.json")).write_text(
            json.dumps(data, separators=(",", ":")) + "\n"
        )
        selected = {
            0,
            1,
            2,
            99,
            100,
            101,
            102,
            199,
            200,
            201,
            202,
            350,
            450,
            451,
            750,
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
                "schema": "independent_visual_stimulus_reference_v5",
                "cases": cases,
                "reference_sha256": canonical_sha256(cases),
            },
            separators=(",", ":"),
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
