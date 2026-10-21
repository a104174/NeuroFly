"""Independent frozen Python neural/observer check for supplied v9 body histories.

This is not an independent Python flight plant. No TypeScript neural outputs are
used: the existing Python observer and composed HS/DNp15 kernel compute them.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys

from neurofly import experimental_neural_locomotion as neural
from neurofly import exploratory_course_control as course
from neurofly import planar_motion_observation as spatial
from neurofly.interactive_neural_locomotion_reference import SOURCE_RAW
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256


def neural_reference(frames, plane=0.4):
    if (
        plane not in (0.4, -0.4)
        or type(frames) is not list
        or not 2 <= len(frames) <= 601
    ):
        raise ValueError("unsupported v9 observer reference window")
    for n, frame in enumerate(frames):
        if (
            frame.get("step") != n
            or frame.get("time") != n * 0.02
            or type(frame.get("position")) is not list
            or len(frame["position"]) != 3
            or not all(
                type(v) in (int, float) and math.isfinite(v)
                for v in [*frame["position"], frame.get("heading")]
            )
        ):
            raise ValueError("invalid v9 reference pose/time")
    raw = neural.OUTPUT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_RAW:
        raise ValueError("neural source identity mismatch")
    authority = json.loads(raw)
    components = course.load_components(course.load_preregistration())
    if (
        canonical_sha256(components.neural_contract)
        != authority["config"]["source_sha256"]["neural"]
    ):
        raise ValueError("pinned neural contract mismatch")
    geometry = spatial.VisualGeometry(
        (
            spatial.Landmark("RIGHT_REFERENCE", "R", 0.6, plane),
            spatial.Landmark("LEFT_REFERENCE", "L", -0.6, plane),
        )
    )
    state, records = neural.NeuralState(), []
    for n, frame in enumerate(frames[:-1]):
        previous = (frames[n - 1]["position"], frames[n - 1]["heading"]) if n else None
        observed, sides = neural.observation(
            previous, (frame["position"], frame["heading"]), geometry, n, 0.02
        )
        before = state
        state, readout = neural.advance_neural(state, sides, 20.0, components)
        records.append(
            {
                "step": n,
                "observation": observed,
                "hs_before": list(before.hs),
                "dn_before": list(before.dnp15),
                "hs_after": list(state.hs),
                "dn_after": list(state.dnp15),
                **readout,
            }
        )
    return {
        "schema": "independent_python_neural_flight_reference_v9",
        "source_raw_sha256": SOURCE_RAW,
        "neural_contract_sha256": authority["config"]["source_sha256"]["neural"],
        "flight_parity": "NOT_CLAIMED_PYTHON_NEURAL_AND_OBSERVER_ONLY",
        "substeps": 200 * len(records),
        "records": records,
    }


def main():
    value = json.load(sys.stdin)
    if (
        set(value) != {"schema", "runs"}
        or value["schema"] != "neural_flight_reference_input_v9"
    ):
        raise ValueError("unsupported neural flight reference input")
    if not isinstance(value["runs"], list) or not 1 <= len(value["runs"]) <= 4:
        raise ValueError("unsupported reference run count")
    json.dump(
        [neural_reference(run["frames"], run["plane"]) for run in value["runs"]],
        sys.stdout,
        allow_nan=False,
        separators=(",", ":"),
    )


if __name__ == "__main__":
    main()
