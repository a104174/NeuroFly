"""Recorded model-state transfer only; no physiological transmission or actuation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import tempfile
from dataclasses import dataclass
from pathlib import Path

from neurofly import dng100_recurrent_motif_authority as motif
from neurofly import dng100_t1_numerical_convergence as convergence
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

REPO = motif.base.REPO
POLICY_PATH = REPO / "docs/science/dng100_t1_motor_input_shadow_preregistration.json"
POLICY_ID = "d45a5c1af870a20f75a0248fa1075fff09543ced5d945191d01c0ad38d1c8fad"
SCHEMA = "dng100_t1_motor_input_shadow_artifact_v0"
DEFAULT_ROOT = REPO.parent / "neurofly-science/work/dng100-t1-motor-input-shadow-v0"


@dataclass(frozen=True)
class SourceSample:
    step: int
    time_s: float
    source_state: float


def policy() -> dict:
    p = json.loads(POLICY_PATH.read_bytes())
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("unrecognized motor-input preregistration")
    return p


def validate_samples(samples: tuple[SourceSample, ...]) -> None:
    if type(samples) is not tuple or not samples:
        raise ValueError("missing immutable source samples")
    previous = -1.0
    for i, sample in enumerate(samples):
        if (
            not isinstance(sample, SourceSample)
            or type(sample.step) is not int
            or sample.step != i
            or type(sample.time_s) not in (float, int)
            or type(sample.source_state) not in (float, int)
            or not math.isfinite(sample.time_s)
            or not math.isfinite(sample.source_state)
            or sample.time_s <= previous
            or (i == 0 and sample.time_s != 0)
            or sample.source_state < 0
        ):
            raise ValueError("invalid source step/time/state")
        previous = sample.time_s


def transfer(
    samples: tuple[SourceSample, ...], sign: int, gain: float
) -> tuple[float, ...]:
    """Dimensionless engineering gain; count is deliberately not an argument."""
    validate_samples(samples)
    if (
        type(sign) is not int
        or sign not in (-1, 0, 1)
        or type(gain) not in (int, float)
        or not math.isfinite(gain)
        or gain <= 0
    ):
        raise ValueError("invalid transfer sign/gain")
    values = tuple(
        0.0 if sign == 0 else sign * gain * sample.source_state for sample in samples
    )
    if not all(math.isfinite(v) for v in values):
        raise ValueError("nonfinite shadow input")
    return values


def structural_evidence(p: dict) -> dict:
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("unregistered structural identities")
    path = motif.DEFAULT_ROOT / p["motif_artifact_id"]
    a = motif.load_artifact(path)
    if (
        a["artifact_id"] != p["motif_artifact_id"]
        or a["config"]["source_sha256"] != p["structural_source_sha256"]
        or a["config"]["annotation_sha256"] != p["annotation_sha256"]
        or a["config"]["policy"]["dataset_uuid"] != p["dataset_uuid"]
    ):
        raise ValueError("structural dataset/source mismatch")
    source = next(n for n in a["result"]["members"] if n["body_id"] == 903216)
    target = next(
        n for n in a["result"]["front_motor_authority"] if n["bodyId"] == 804257
    )
    if (
        source["annotation"] != p["source_annotation"]
        or target != p["target_annotation"]
    ):
        raise ValueError("motor source/target annotation mismatch")
    snapshot = json.loads((path / "source.json").read_bytes())
    evidence = []
    for query in ("primary_outputs", "motor_inputs"):
        rows = motif.base.parse_edges(snapshot["queries"][query], query)
        matches = [e for e in rows if (e["pre"], e["post"]) == (903216, 804257)]
        if len(matches) != 1:
            raise ValueError("missing directed motor edge")
        evidence.append(matches[0])
    if evidence != p["edge_evidence"] or any(
        e["synapse_count"] != 23 for e in evidence
    ):
        raise ValueError("motor edge count/direction/evidence mismatch")
    return {"source": source, "target": target, "edges": evidence}


def recorded_samples(trace: dict, state_order: list[int]) -> tuple[SourceSample, ...]:
    """Strict complete six-state source boundary; no interpolation or repair."""
    if state_order != [800173, 800863, 801884, 800288, 903216, 803183]:
        raise ValueError("source-neuron state ordering mismatch")
    times, states = trace.get("times_s"), trace.get("states")
    if (
        type(times) is not list
        or type(states) is not list
        or len(times) != 2001
        or len(states) != 2001
        or trace.get("termination") != "COMPLETED"
    ):
        raise ValueError("incomplete recorded source trace")
    samples = []
    for i, (time, row) in enumerate(zip(times, states)):
        if (
            type(time) not in (int, float)
            or not math.isfinite(time)
            or time != i * 0.001
            or type(row) is not list
            or len(row) != 6
            or any(
                type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 200
                for v in row
            )
        ):
            raise ValueError("missing/nonfinite/misaligned source boundary")
        samples.append(SourceSample(i, time, row[4]))
    result = tuple(samples)
    validate_samples(result)
    return result


def load_inputs() -> tuple[dict, tuple[SourceSample, ...], dict]:
    """Validate pinned sources without calling any neural simulation or solver."""
    p = policy()
    structure = structural_evidence(p)
    cp = convergence.policy()
    original, _ = convergence.source(cp)
    if (
        original["artifact_id"] != p["source_v0_artifact_id"]
        or cp["source_raw_sha256"] != p["source_v0_raw_sha256"]
        or original["config"]["preregistration"]["nt_artifact_id"]
        != p["nt_artifact_id"]
        or cp["model"] != p["source_model"]
    ):
        raise ValueError("original neural model/authority mismatch")
    path = convergence.DEFAULT_ROOT / p["source_artifact_id"]
    if (
        not path.is_dir()
        or {f.name for f in path.iterdir()} != {"convergence.json", "manifest.json"}
        or any(f.is_symlink() for f in path.iterdir())
    ):
        raise ValueError("missing or unsafe recorded convergence artifact")
    raw = (path / "convergence.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != p["source_raw_sha256"]:
        raise ValueError("recorded source raw checksum mismatch")
    a = json.loads(raw)
    manifest_raw = (path / "manifest.json").read_bytes()
    manifest = json.loads(manifest_raw)
    expected = {
        "schema": convergence.SCHEMA,
        "artifact_id": p["source_artifact_id"],
        "files": {
            "convergence.json": {"bytes": len(raw), "sha256": p["source_raw_sha256"]}
        },
    }
    if (
        raw != canonical_json_bytes(a, newline=True)
        or manifest_raw != canonical_json_bytes(expected, newline=True)
        or manifest != expected
        or a != convergence.package(a["config"], a["result"])
        or a["config"] != convergence.config(cp, original)
        or a["config_sha256"] != p["source_config_sha256"]
        or a["result_sha256"] != p["source_result_sha256"]
        or a["result"]["assessment"]["decision"] != "DNG100_T1_CONVERGENCE_VERIFIED"
    ):
        raise ValueError("recorded convergence provenance mismatch")
    trace = a["result"]["traces"][p["source_trace"]]
    if canonical_sha256(trace) != p["source_trace_sha256"]:
        raise ValueError("selected recorded trace mismatch")
    samples = recorded_samples(trace, p["state_order"])
    return p, samples, structure


def sample_records(samples: tuple[SourceSample, ...]) -> list[dict]:
    return [
        dict(step=s.step, time_s=s.time_s, source_state=s.source_state) for s in samples
    ]


def configuration(p: dict, samples: tuple[SourceSample, ...], structure: dict) -> dict:
    return {
        "schema": SCHEMA,
        "preregistration": p,
        "preregistration_id": POLICY_ID,
        "structural_evidence": structure,
        "input_sha256": canonical_sha256(sample_records(samples)),
        "software": {
            "python": platform.python_version(),
            "implementation_sha256": hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest(),
        },
    }


def run(p: dict, samples: tuple[SourceSample, ...]) -> dict:
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("unregistered transfer configuration")
    validate_samples(samples)
    if len(samples) != 2001 or any(s.time_s != s.step * 0.001 for s in samples):
        raise ValueError("incomplete scientific timing")
    before = canonical_sha256(sample_records(samples))
    conditions = []
    for condition in p["conditions"]:
        values = transfer(samples, condition["sign_assumption"], p["transfer"]["gain"])
        telemetry = [
            {
                **record,
                "condition": condition["id"],
                "source_body_id": 903216,
                "target_body_id": 804257,
                "shadow_input": value,
            }
            for record, value in zip(sample_records(samples), values)
        ]
        conditions.append(
            dict(
                condition=condition,
                telemetry=telemetry,
                output_range=[min(values), max(values)],
                input_sha256=before,
            )
        )
    a, b, off, sham = [
        tuple(s["shadow_input"] for s in c["telemetry"]) for c in conditions
    ]
    invariance = all(
        [
            {k: row[k] for k in ("step", "time_s", "source_state")}
            for row in c["telemetry"]
        ]
        == sample_records(samples)
        for c in conditions
    )
    checks = {
        "positive_negative_symmetry": a == tuple(-v for v in b),
        "route_off_exact_zero": all(v == 0.0 for v in off),
        "sham_exact_equality": a == sham,
        "source_invariance": invariance
        and before == canonical_sha256(sample_records(samples)),
    }
    if not all(checks.values()):
        raise ValueError("shadow transfer control failure")
    return {
        "conditions": conditions,
        "summary": {
            "samples_per_condition": len(samples),
            "conditions": len(conditions),
            "input_range": [
                min(s.source_state for s in samples),
                max(s.source_state for s in samples),
            ],
            "checks": checks,
            "semantics": p["semantics"],
            "termination": "COMPLETED",
            "decision": "DNG100_T1_MOTOR_INPUT_SHADOW_VALIDATED",
        },
    }


def package(config: dict, result: dict) -> dict:
    ch, rh = canonical_sha256(config), canonical_sha256(result)
    return dict(
        schema=SCHEMA,
        config=config,
        result=result,
        config_sha256=ch,
        result_sha256=rh,
        artifact_id=canonical_sha256({"config_sha256": ch, "result_sha256": rh}),
    )


def validate(value: dict) -> dict:
    p, samples, structure = load_inputs()
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
        or value["config"] != configuration(p, samples, structure)
        or value["result"] != run(p, samples)
    ):
        raise ValueError("contradictory shadow provenance/telemetry/hash")
    return value


def generate(root: Path = DEFAULT_ROOT) -> Path:
    p, samples, structure = load_inputs()
    a = package(configuration(p, samples, structure), run(p, samples))
    root = Path(root).resolve()
    if root.is_relative_to(REPO):
        raise ValueError("shadow artifacts must remain outside Git")
    root.mkdir(parents=True, exist_ok=True)
    dest = root / a["artifact_id"]
    if dest.exists():
        raise ValueError("refusing to overwrite scientific artifact")
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        stage = Path(tmp) / "artifact"
        stage.mkdir()
        raw = canonical_json_bytes(a, newline=True)
        (stage / "shadow.json").write_bytes(raw)
        (stage / "manifest.json").write_bytes(
            canonical_json_bytes(
                {
                    "schema": SCHEMA,
                    "artifact_id": a["artifact_id"],
                    "files": {
                        "shadow.json": {
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
        or {f.name for f in path.iterdir()} != {"shadow.json", "manifest.json"}
        or any(f.is_symlink() for f in path.iterdir())
    ):
        raise ValueError("missing or unsafe shadow artifact")
    raw = (path / "shadow.json").read_bytes()
    a = json.loads(raw)
    expected = {
        "schema": SCHEMA,
        "artifact_id": a["artifact_id"],
        "files": {
            "shadow.json": {
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
        raise ValueError("shadow artifact raw integrity mismatch")
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
