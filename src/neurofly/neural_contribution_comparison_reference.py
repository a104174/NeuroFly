"""Paired engineering-navigation counterfactuals; existing v3 model unchanged."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from neurofly.continuous_arena_navigation_reference import run_reference
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256


def contact_events(frames):
    events, previous = [], None
    for f in frames:
        wall = f["contact"]
        if wall != previous:
            if previous and wall:
                events.append(
                    dict(
                        step=f["step"],
                        time=f["time"],
                        kind="WALL_CHANGE",
                        wall=wall,
                        previous_wall=previous,
                    )
                )
            elif previous:
                events.append(
                    dict(step=f["step"], time=f["time"], kind="RECOVERY", wall=previous)
                )
            elif wall:
                events.append(
                    dict(step=f["step"], time=f["time"], kind="CONTACT", wall=wall)
                )
            previous = wall
    return events


def paired_metrics(a, b):
    if not a or len(a) != len(b):
        raise ValueError("Unaligned pair")
    distance_max, heading_max = dict(value=-1, time=0), dict(value=-1, time=0)
    previous = None
    for x, y in zip(a, b, strict=True):
        if x["time"] != y["time"] or x["step"] != y["step"]:
            raise ValueError("Unaligned scientific timestamps")
        distance = math.hypot(
            x["position"][0] - y["position"][0], x["position"][2] - y["position"][2]
        )
        delta = x["orientation"] - y["orientation"]
        angle = abs(math.atan2(math.sin(delta), math.cos(delta)))
        if distance > distance_max["value"]:
            distance_max = dict(value=distance, time=x["time"])
        if angle > heading_max["value"]:
            heading_max = dict(value=angle, time=x["time"])
        if previous is not None:
            lo, hi = min(previous, delta), max(previous, delta)
            odd = math.pi + 2 * math.pi * math.ceil((lo - math.pi) / (2 * math.pi))
            if lo <= odd <= hi and delta != previous and heading_max["value"] < math.pi:
                heading_max = dict(
                    value=math.pi,
                    time=x["time"]
                    - 0.02
                    + (odd - previous) / (delta - previous) * 0.02,
                )
        previous = delta
    return dict(
        max_separation=distance_max,
        max_wrapped_heading=heading_max,
        final_separation=distance,
        final_wrapped_heading=math.atan2(math.sin(delta), math.cos(delta)),
        traveled_difference=a[-1]["distance"] - b[-1]["distance"],
    )


def run_pair(events=(), stop_step=1500):
    if type(stop_step) is not int or not 1 <= stop_step <= 1500:
        raise ValueError("Invalid recorded prefix")
    if any(e[0] >= stop_step for e in events):
        raise ValueError("Event outside completed prefix")
    tracks = []
    for key, enabled in [("ON", True), ("OFF", False)]:
        r = run_reference(events, apply=enabled)
        frames = r["frames"][: stop_step + 1]
        # A prefix endpoint has no outgoing interval, unlike a continued full run.
        if stop_step < 1500:
            f = frames[-1]
            f["angular_velocity"] = 0
            f["steering_model_value"] = 0
            f["steering_clipped"] = False
            f["boundary_summary"]["omega"] = 0
            f["boundary_summary"]["neural_omega"] = 0
            for field in ["mean_yaw_drive_eq", "orientation_increment_eq"]:
                f["neural_summary"][field] = None
            f["neural_summary"]["substeps"] = 0
        tracks.append(
            dict(
                key=key,
                NEURAL_TO_HEADING_ENABLED=enabled,
                frames=frames,
                contact_events=contact_events(frames),
            )
        )
    return dict(
        schema="neural_contribution_comparison_reference_v3_1",
        events=events,
        source={
            k: r[k]
            for k in ["source_artifact_id", "source_raw_sha256", "source_config_sha256"]
        },
        stop_step=stop_step,
        tracks=tracks,
        metrics=paired_metrics(tracks[0]["frames"], tracks[1]["frames"]),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = {}
    for key, events in [("none", ()), ("switch", ((100, -0.4),))]:
        r = run_pair(events)
        (args.output.parent / (key + "-full.json")).write_text(
            json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n"
        )
        steps = {
            0,
            1,
            2,
            3,
            99,
            100,
            101,
            200,
            269,
            282,
            320,
            356,
            408,
            750,
            1000,
            1499,
            1500,
        }
        for track in r["tracks"]:
            track["frames"] = [f for f in track["frames"] if f["step"] in steps]
        cases[key] = r
    out = dict(
        schema="neural_contribution_comparison_reference_v3_1",
        cases=cases,
        reference_sha256=canonical_sha256(cases),
    )
    args.output.write_text(
        json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n"
    )
    print(out["reference_sha256"])


if __name__ == "__main__":
    main()
