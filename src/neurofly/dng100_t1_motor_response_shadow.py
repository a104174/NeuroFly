"""Isolated engineering receiver of recorded shadow input; no motor recruitment."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import tempfile
from dataclasses import dataclass
from pathlib import Path

from neurofly import dng100_t1_motor_input_shadow as parent
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

SCHEMA = "dng100_t1_motor_response_shadow_artifact_v0"
POLICY_PATH = (
    parent.REPO / "docs/science/dng100_t1_motor_response_shadow_preregistration.json"
)
POLICY_ID = "133ab02e77008fbf1720deaa40a746cbcbef6adef923271222023cecdbfff4b4"
DEFAULT_ROOT = (
    parent.REPO.parent / "neurofly-science/work/dng100-t1-motor-response-shadow-v0"
)


def finite(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


@dataclass(frozen=True)
class ReceiverConfig:
    tau_s: float
    gain: float = 1.0
    initial_state: float = 0.0

    def __post_init__(self) -> None:
        if (
            not all(finite(x) for x in (self.tau_s, self.gain, self.initial_state))
            or self.tau_s <= 0
            or self.gain <= 0
        ):
            raise ValueError("invalid engineering receiver parameters")


def response(
    times: tuple[float, ...], inputs: tuple[float, ...], config: ReceiverConfig
) -> tuple[float, ...]:
    """Exact ZOH solution at recorded boundaries; final input is not consumed."""
    if (
        not isinstance(config, ReceiverConfig)
        or type(times) is not tuple
        or type(inputs) is not tuple
        or len(times) < 2
        or len(inputs) != len(times)
        or not all(finite(x) for x in (*times, *inputs))
        or times[0] != 0
        or any(b <= a for a, b in zip(times, times[1:]))
    ):
        raise ValueError("invalid ordered receiver input")
    state = config.initial_state
    states = [state]
    for start, end, input_value in zip(times, times[1:], inputs[:-1]):
        # expm1 preserves small interval coefficients without 1-exp cancellation.
        beta = -math.expm1(-(end - start) / config.tau_s)
        state += beta * (config.gain * input_value - state)
        if not finite(state):
            raise ValueError("nonfinite engineering receiver solution")
        states.append(state)
    return tuple(states)


def policy() -> dict:
    p = json.loads(POLICY_PATH.read_bytes())
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("unrecognized response preregistration")
    return p


def load_input() -> tuple[dict, dict]:
    """Replay scalar parent only; original neural dynamics never execute."""
    p = policy()
    folder = parent.DEFAULT_ROOT / p["input_artifact_id"]
    if not (folder / "shadow.json").is_file():
        raise ValueError("missing recorded motor-input authority")
    raw = (folder / "shadow.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != p["input_raw_sha256"]:
        raise ValueError("motor-input raw source mismatch")
    a = parent.replay(folder)
    previous = a["config"]["preregistration"]
    expected = {
        "dataset",
        "dataset_uuid",
        "edge",
        "source_annotation",
        "target_annotation",
        "motif_artifact_id",
        "structural_source_sha256",
        "annotation_sha256",
    }
    if (
        a["artifact_id"] != p["input_artifact_id"]
        or a["config_sha256"] != p["input_config_sha256"]
        or a["result_sha256"] != p["input_result_sha256"]
        or a["config"]["preregistration_id"] != p["input_preregistration_id"]
        or any(previous[k] != p[k] for k in expected)
        or previous["source_artifact_id"] != p["neural_source_artifact_id"]
        or previous["source_raw_sha256"] != p["neural_source_raw_sha256"]
        or previous["source_trace_sha256"] != p["neural_trace_sha256"]
        or a["result"]["summary"]["semantics"]["target_connection_functional_sign"]
        != "UNKNOWN"
    ):
        raise ValueError("contradictory structural/transfer/neural provenance")
    return p, a


def config(p: dict, a: dict) -> dict:
    return {
        "schema": SCHEMA,
        "preregistration": p,
        "preregistration_id": POLICY_ID,
        "parent_structural_evidence": a["config"]["structural_evidence"],
        "software": {
            "python": platform.python_version(),
            "implementation_sha256": hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest(),
        },
    }


def metrics(times: tuple, inputs: tuple, states: tuple) -> dict:
    """Finite-window engineering descriptors; no physiological delay inference."""
    if len(times) != len(inputs) or len(times) != len(states):
        raise ValueError("metric shape mismatch")
    if not all(finite(x) for x in (*times, *inputs, *states)):
        raise ValueError("nonfinite metric data")
    peak = max(abs(y) for y in states)
    peak_index = next(i for i, y in enumerate(states) if abs(y) == peak)
    input_peak = max(abs(u) for u in inputs)
    input_index = next(i for i, u in enumerate(inputs) if abs(u) == input_peak)
    selected = [i for i, t in enumerate(times) if 1.0 <= t <= 2.0]
    if not selected:
        raise ValueError("missing declared metric window")
    u = [inputs[i] for i in selected]
    y = [states[i] for i in selected]
    mean_u, mean_y = math.fsum(u) / len(u), math.fsum(y) / len(y)
    rms_u = math.sqrt(math.fsum((x - mean_u) ** 2 for x in u) / len(u))
    rms_y = math.sqrt(math.fsum((x - mean_y) ** 2 for x in y) / len(y))
    result = {
        "input_range": [min(inputs), max(inputs)],
        "output_range": [min(states), max(states)],
        "initial_state": states[0],
        "final_state": states[-1],
        "maximum_absolute_response": peak,
        "peak_time_s": times[peak_index],
        "input_peak_time_s": times[input_index] if input_peak else None,
        "peak_time_offset_s": times[peak_index] - times[input_index]
        if input_peak
        else None,
        "offset_interpretation": "DESCRIPTIVE_GLOBAL_PEAK_NOT_SYNAPTIC_LATENCY",
        "tail_input_mean": mean_u,
        "tail_output_mean": mean_y,
        "tail_input_centered_rms": rms_u,
        "tail_output_centered_rms": rms_y,
        "tail_attenuation_rms_ratio": rms_y / rms_u if rms_u else None,
    }
    if any(
        v is not None and not finite(v)
        for k, v in result.items()
        if k not in {"input_range", "output_range", "offset_interpretation"}
    ):
        raise ValueError("nonfinite response metric")
    return result


def experiment(p: dict, a: dict) -> dict:
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("unregistered response configuration")
    conditions = a["result"]["conditions"]
    if [c["condition"] for c in conditions] != p["conditions"]:
        raise ValueError("unexpected parent conditions")
    runs, controls = [], []
    original = canonical_sha256(a)
    baseline = conditions[0]["telemetry"]
    for point in p["timescales"]:
        matched = []
        for c in conditions:
            rows = c["telemetry"]
            if (
                len(rows) != 2001
                or any(
                    r["step"] != i or r["time_s"] != i * 0.001
                    for i, r in enumerate(rows)
                )
                or any(
                    (r["source_body_id"], r["target_body_id"]) != (903216, 804257)
                    for r in rows
                )
                or [(r["time_s"], r["source_state"]) for r in rows]
                != [(r["time_s"], r["source_state"]) for r in baseline]
            ):
                raise ValueError("inconsistent source identity/timing/state")
            times = tuple(r["time_s"] for r in rows)
            inputs = tuple(r["shadow_input"] for r in rows)
            parameters = ReceiverConfig(
                point["tau_s"], p["model"]["gain"], p["model"]["initial_state"]
            )
            states = response(times, inputs, parameters)
            matched.append(states)
            runs.append(
                {
                    "condition": c["condition"],
                    "parameter_point": point,
                    "integration_method": p["model"]["integration_method"],
                    "telemetry": [
                        {
                            "step": i,
                            "time_s": t,
                            "source_model_state": rows[i]["source_state"],
                            "shadow_input": inputs[i],
                            "receiver_state": states[i],
                            "receiver_consumed_input_step": i - 1 if i else None,
                            "outgoing_interval_input": inputs[i]
                            if i < len(times) - 1
                            else None,
                            "condition": c["condition"]["id"],
                            "parameter_id": point["id"],
                            "sign_assumption": c["condition"]["sign_assumption"],
                            "source_body_id": 903216,
                            "target_body_id": 804257,
                        }
                        for i, t in enumerate(times)
                    ],
                    "metrics": metrics(times, inputs, states),
                    "termination": "COMPLETED",
                }
            )
        pos, neg, off, sham = matched
        check = {
            "parameter_id": point["id"],
            "positive_negative_symmetry": pos == tuple(-x for x in neg),
            "route_off_exact_zero": all(x == 0 for x in off),
            "sham_exact_equality": pos == sham,
        }
        if not all(v for k, v in check.items() if k != "parameter_id"):
            raise ValueError("receiver control mismatch")
        controls.append(check)
    unchanged = canonical_sha256(a) == original
    if not unchanged:
        raise ValueError("source mutated by receiver")
    return {
        "runs": runs,
        "summary": {
            "run_count": len(runs),
            "boundaries_per_run": 2001,
            "completed_intervals_per_run": 2000,
            "controls": controls,
            "source_invariance": unchanged,
            "semantics": p["semantics"],
            "termination": "COMPLETED",
            "decision": "DNG100_T1_MOTOR_RESPONSE_SHADOW_VALIDATED",
        },
    }


def package(c: dict, r: dict) -> dict:
    ch, rh = canonical_sha256(c), canonical_sha256(r)
    return dict(
        schema=SCHEMA,
        config=c,
        result=r,
        config_sha256=ch,
        result_sha256=rh,
        artifact_id=canonical_sha256({"config_sha256": ch, "result_sha256": rh}),
    )


def validate(value: dict) -> dict:
    p, source = load_input()
    if (
        not isinstance(value, dict)
        or set(value)
        != {
            "schema",
            "config",
            "result",
            "config_sha256",
            "result_sha256",
            "artifact_id",
        }
        or value != package(value["config"], value["result"])
        or value["config"] != config(p, source)
        or value["result"] != experiment(p, source)
    ):
        raise ValueError("contradictory response provenance/telemetry/hash")
    return value


def generate(root: Path = DEFAULT_ROOT) -> Path:
    p, source = load_input()
    a = package(config(p, source), experiment(p, source))
    root = Path(root).resolve()
    if root.is_relative_to(parent.REPO):
        raise ValueError("response artifacts must remain outside Git")
    root.mkdir(parents=True, exist_ok=True)
    dest = root / a["artifact_id"]
    if dest.exists():
        raise ValueError("refusing to overwrite scientific artifact")
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        stage = Path(tmp) / "artifact"
        stage.mkdir()
        raw = canonical_json_bytes(a, newline=True)
        (stage / "response.json").write_bytes(raw)
        (stage / "manifest.json").write_bytes(
            canonical_json_bytes(
                {
                    "schema": SCHEMA,
                    "artifact_id": a["artifact_id"],
                    "files": {
                        "response.json": {
                            "bytes": len(raw),
                            "sha256": hashlib.sha256(raw).hexdigest(),
                        }
                    },
                },
                newline=True,
            )
        )
        stage.rename(dest)
    return dest


def replay(path: Path) -> dict:
    path = Path(path)
    if (
        not path.is_dir()
        or {f.name for f in path.iterdir()} != {"response.json", "manifest.json"}
        or any(f.is_symlink() for f in path.iterdir())
    ):
        raise ValueError("missing or unsafe response artifact")
    raw = (path / "response.json").read_bytes()
    a = json.loads(raw)
    expected = {
        "schema": SCHEMA,
        "artifact_id": a["artifact_id"],
        "files": {
            "response.json": {
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        },
    }
    if (
        raw != canonical_json_bytes(a, newline=True)
        or (path / "manifest.json").read_bytes()
        != canonical_json_bytes(expected, newline=True)
        or path.name != a["artifact_id"]
    ):
        raise ValueError("response raw manifest/hash mismatch")
    return validate(a)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["generate", "replay"])
    parser.add_argument("--path", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        print(generate(args.path))
    else:
        a = replay(args.path)
        print(a["artifact_id"], a["result"]["summary"]["decision"])


if __name__ == "__main__":
    main()
