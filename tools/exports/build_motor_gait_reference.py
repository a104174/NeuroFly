"""Extract one immutable SHADOW_ONLY receiver trace; never rerun neural dynamics."""

import hashlib
import json
from pathlib import Path

from neurofly import dng100_t1_motor_response_shadow as motor

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "web/public/experiments/motor_gait_bridge_v7.json"


def reference():
    ref = json.loads(
        (
            REPO / "docs/science/dng100_t1_motor_response_shadow_reference.json"
        ).read_text()
    )["reference"]
    folder = motor.DEFAULT_ROOT / ref["artifact_id"]
    raw = (folder / "response.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ref["files"]["response.json"]["sha256"]
    artifact = motor.replay(folder)
    runs = {
        r["condition"]["id"]: r
        for r in artifact["result"]["runs"]
        if r["parameter_point"]["id"] == "TAU_10MS"
    }
    positive = runs["A_POSITIVE"]["telemetry"]
    assert all(r["receiver_state"] == 0 for r in runs["C_ROUTE_OFF"]["telemetry"])
    assert positive == [
        {**r, "condition": "A_POSITIVE"} for r in runs["D_SHAM"]["telemetry"]
    ]
    return {
        "schema": "motor_gait_reference_v7",
        "source": ref["source"],
        "response_artifact_id": ref["artifact_id"],
        "response_raw_sha256": ref["files"]["response.json"]["sha256"],
        "model": ref["model"],
        "tau_s": 0.01,
        "timebase": {"dt_s": 0.001, "duration_s": 2, "samples": 2001},
        "classification": [
            "PRECOMPUTED_PYTHON_MOTOR_MODEL_RESPONSE",
            "SHADOW_ONLY_MOTOR_RESPONSE",
        ],
        "controls": {
            "ON": "A_POSITIVE",
            "BASE": "A_POSITIVE_NOT_APPLIED",
            "ROUTE_OFF": "C_ROUTE_OFF",
            "SHAM": "D_SHAM",
        },
        "columns": ["source_model_state", "receiver_state"],
        "samples": [[r["source_model_state"], r["receiver_state"]] for r in positive],
        "projection_reference": [
            [
                r["time_s"],
                r["receiver_state"],
                0.012 + 0.004 * max(-1, min(1, r["receiver_state"] / 100)),
            ]
            for r in positive[::20]
        ],
    }


if __name__ == "__main__":
    payload = json.dumps(reference(), separators=(",", ":"), sort_keys=True) + "\n"
    OUTPUT.write_text(payload)
    print(
        OUTPUT.relative_to(REPO),
        len(payload),
        hashlib.sha256(payload.encode()).hexdigest(),
    )
