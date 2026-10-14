"""Deterministic display-space locomotion. No neural or biomechanical claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "web/src/assets/fly_visual_v2f.json"
OUTPUT = ROOT / "web/public/experiments/experimental_locomotion_v0.json"
EXPERIMENT = "EXPERIMENTAL_LOCOMOTION_V0"
SCHEMA = "experimental_locomotion_replay_v1"
MODE = "EXPERIMENTAL_KINEMATIC_ONLY"


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def configuration():
    asset = json.loads(ASSET.read_bytes())
    anchor = asset["canonical_transform"]["visual_anchor"]["position"]
    scale = 0.30
    offset = [0.0, 0.09181772303581237, 0.08531420230865478]
    position = [offset[i] + scale * anchor[i] for i in range(3)]
    radius = max(
        math.hypot(x - anchor[0], z - anchor[2]) * scale
        for x in (asset["bounds"]["min"][0], asset["bounds"]["max"][0])
        for z in (asset["bounds"]["min"][2], asset["bounds"]["max"][2])
    )
    return {
        "experiment_id": EXPERIMENT,
        "schema_version": SCHEMA,
        "model_mode": MODE,
        "propulsion_source": "ENGINEERING_ASSUMPTION",
        "boundary_response": "ENGINEERING_CONTACT_MODEL",
        "presentation": "PRECOMPUTED_SIMULATION_REPLAY",
        "neural_steering": "NOT_MODELLED",
        "malecns_references": [],
        "random_policy": "NONE",
        "units": "arena_display_units_and_seconds_not_physical_calibration",
        "axes": "Y_UP_HEADING_ZERO_POSITIVE_Z_POSITIVE_YAW_TOWARD_POSITIVE_X",
        "update": "LEFT_BOUNDARY_CONSTANT_VELOCITY_THEN_CONTACT_STOP",
        "dt_s": 0.02,
        "duration_s": 8.0,
        "speed": 0.18,
        "initial_position": position,
        "initial_heading_rad": math.pi / 2,
        "chamber": {"width": 2.4, "depth": 1.22, "height": 0.86, "wall": 0.012},
        "footprint_radius": radius,
        "fly_scale": scale,
        "fly_asset_sha256": asset["runtime"]["sha256"],
        "fly_manifest_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
        "asset_anchor": anchor,
        "asset_offset": [-v for v in anchor],
        "bounds": asset["bounds"],
        "floor_offset_y": offset[1],
        "limitations": [
            "Engineering propulsion; no connectome control or neural steering.",
            "Conservative circular footprint and stop-on-contact; no wall sensing.",
            "Static visual legs; no gait, muscle, force or biological speed model.",
            "Precomputed Python simulation; browser time only selects recorded poses.",
        ],
    }


def validate_config(c):
    try:
        numeric = [c[k] for k in ("dt_s", "duration_s", "speed", "footprint_radius")]
        numeric += list(c["initial_position"]) + [c["initial_heading_rad"]]
        numeric += list(c["chamber"].values())
        if not all(finite(v) for v in numeric):
            raise ValueError("non-finite configuration")
        if len(c["initial_position"]) != 3 or c["speed"] < 0:
            raise ValueError("invalid position or speed")
        dt, duration = c["dt_s"], c["duration_s"]
        if not 0 < dt <= 0.1 or not 0 < duration <= 60:
            raise ValueError("invalid integration horizon")
        if abs(duration / dt - round(duration / dt)) > 1e-9:
            raise ValueError("duration must contain complete intervals")
        if c["speed"] * dt > c["footprint_radius"] / 2:
            raise ValueError("excessive step displacement")
        g, r = c["chamber"], c["footprint_radius"]
        if min(g.values()) <= 0 or r <= 0:
            raise ValueError("invalid arena geometry")
        limits = [(g["width"] - g["wall"]) / 2 - r, (g["depth"] - g["wall"]) / 2 - r]
        if min(limits) <= 0:
            raise ValueError("footprint does not fit")
        p = c["initial_position"]
        if abs(p[0]) > limits[0] or abs(p[2]) > limits[1]:
            raise ValueError("initial pose outside bounds")
        if p[1] != c["floor_offset_y"] + c["fly_scale"] * c["asset_anchor"][1]:
            raise ValueError("initial height differs from floor placement")
        if c["experiment_id"] != EXPERIMENT or c["schema_version"] != SCHEMA:
            raise ValueError("invalid experiment identity")
        low = c["floor_offset_y"] + c["fly_scale"] * c["bounds"]["min"][1]
        high = c["floor_offset_y"] + c["fly_scale"] * c["bounds"]["max"][1]
        if not 0 < low < high < g["height"] - g["wall"] / 2:
            raise ValueError("invalid floor/lid clearance")
        if c["model_mode"] != MODE or c["random_policy"] != "NONE":
            raise ValueError("unsupported model")
        return limits
    except (KeyError, TypeError) as exc:
        raise ValueError("incomplete configuration") from exc


def simulate(c, run_id, speed):
    """Closed boundary state: contact latches; no artificial wall turn."""
    params = {**c, "speed": speed}
    lx, lz = validate_config(params)
    p = c["initial_position"].copy()
    heading, dt = c["initial_heading_rad"], c["dt_s"]
    count = round(c["duration_s"] / dt)
    vx, vz = speed * math.sin(heading), speed * math.cos(heading)
    contact, distance, frames, events = None, 0.0, [], []
    for n in range(count + 1):
        if contact is None and speed > 0:
            if (p[0] >= lx and vx > 0) or (p[0] <= -lx and vx < 0):
                contact = "X_WALL"
            elif (p[2] >= lz and vz > 0) or (p[2] <= -lz and vz < 0):
                contact = "Z_WALL"
            if contact:
                events.append({"step": n, "time": n * dt, "wall": contact})
        velocity = [0.0, 0.0, 0.0] if contact else [vx, 0.0, vz]
        frames.append(
            {
                "step": n,
                "time": n * dt,
                "position": p.copy(),
                "orientation": heading,
                "linear_velocity": velocity,
                "angular_velocity": 0.0,
                "contact": contact,
                "propulsion_model_value": speed,
                "steering_model_value": None,
                "sensory_summary": None,
                "neural_summary": None,
                "model_mode": MODE,
                "distance": distance,
            }
        )
        if n == count:
            break  # Final boundary has no outgoing interval.
        if contact:
            continue
        proposed = [p[0] + vx * dt, p[1], p[2] + vz * dt]
        proposed[0] = max(-lx, min(lx, proposed[0]))
        proposed[2] = max(-lz, min(lz, proposed[2]))
        distance += math.hypot(proposed[0] - p[0], proposed[2] - p[2])
        p = proposed
    return {
        "id": run_id,
        "speed": speed,
        "frames": frames,
        "contact_events": events,
        "distance": distance,
        "termination_reason": "DURATION_COMPLETED",
    }


def build():
    c = configuration()
    result = {
        "runs": [
            simulate(c, "ENGINEERING_PROPULSION", c["speed"]),
            simulate(c, "PROPULSION_OFF", 0.0),
        ]
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


def validate_artifact(value):
    # Complete regeneration validates semantics, including recomputed-hash tampering.
    if canonical_json_bytes(value) != canonical_json_bytes(build()):
        raise ValueError("locomotion artifact differs from deterministic simulation")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        validate_artifact(json.loads(args.verify.read_bytes()))
        print("Deterministic semantic replay verified")
    elif args.output:
        data = canonical_json_bytes(build(), newline=True)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)
        print(hashlib.sha256(data).hexdigest())
    else:
        parser.error("choose --output or --verify")


if __name__ == "__main__":
    main()
