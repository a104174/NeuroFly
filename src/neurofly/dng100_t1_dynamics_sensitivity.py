"""Preregistered offline sensitivity; biological signs remain UNKNOWN."""

import argparse
import hashlib
import json
import platform
import tempfile
from pathlib import Path

import numpy as np

from neurofly import dng100_nt_sign_authority as authority
from neurofly import dng100_t1_counterfactual_dynamics as model
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

REPO = Path(__file__).resolve().parents[2]
PREREGISTRATION = REPO / "docs/science/dng100_t1_dynamics_preregistration.json"
POLICY_ID = "80e57ffdc0756c1afdbd57db6d066bc4e99b250dcd9ec1a9b112494be5a59a2b"
DEFAULT_ROOT = REPO.parent / "neurofly-science/work/dng100-t1-dynamics-v0"
SCHEMA = "dng100_t1_sign_uncertainty_artifact_v0"


def policy():
    p = json.loads(PREREGISTRATION.read_bytes())
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("preregistration identity mismatch")
    return p


def load_authority():
    p = policy()
    pin = json.loads(authority.REFERENCE_PATH.read_bytes())
    v = authority.load_artifact(authority.DEFAULT_ROOT / pin["artifact_id"])
    if v["artifact_id"] != p["nt_artifact_id"]:
        raise ValueError("transmitter authority mismatch")
    graph = [e["structural"] for e in v["result"]["edges"]]
    if graph != p["edges"] or len(graph) != 15:
        raise ValueError("structural identity/count/orientation mismatch")
    if any(e["functional_sign"] != "UNKNOWN" for e in v["result"]["edges"]):
        raise ValueError("biological sign authority changed")
    evidence = json.loads(
        (REPO / "docs/science/dng100_t1_postsynaptic_evidence.json").read_bytes()
    )
    if (
        evidence["review_id"] != p["postsynaptic_review_id"]
        or canonical_sha256(evidence["review"]) != evidence["review_id"]
        or any(
            e["functional_sign_status"] != "UNKNOWN"
            for e in evidence["review"]["evidence_records"]
        )
    ):
        raise ValueError("postsynaptic UNKNOWN authority mismatch")
    identities = {
        n["body_id"]: (n["annotation"]["type"], n["annotation"]["somaSide"])
        for n in v["result"]["neurons"]
    }
    expected = {
        10045: ("DNg100", "L"),
        10056: ("DNg100", "R"),
        800173: ("IN17A001", "L"),
        800863: ("INXXX466", "L"),
        801884: ("IN16B036", "L"),
        800288: ("IN17A001", "R"),
        903216: ("INXXX466", "R"),
        803183: ("IN16B036", "R"),
    }
    if identities != expected:
        raise ValueError("neuron identity/side mismatch")
    return graph


def configurations(p):
    configs = []
    for point in p["parameter_points"]:
        for variant in p["sign_variants"]:
            for schedule in p["schedules"]:
                for role in ["primary", "half_dt", "initial_2"]:
                    configs.append(
                        dict(
                            point=point["id"],
                            variant=variant,
                            schedule=schedule,
                            role=role,
                        )
                    )
    for role, schedule in [
        ("sham", "constant"),
        ("source_off", "constant"),
        ("feedback_disabled", "zero"),
        ("feedback_disabled", "constant"),
        ("feedback_disabled", "pulse"),
    ]:
        configs.append(
            dict(
                point="central",
                variant="A_PUBLISHED_LIKE",
                schedule=schedule,
                role=role,
            )
        )
    return configs


def matrices(p, graph, cfg):
    if (
        canonical_sha256(p) != POLICY_ID
        or graph != p["edges"]
        or cfg not in configurations(p)
    ):
        raise ValueError("unregistered graph/sign/configuration")
    point = next(x for x in p["parameter_points"] if x["id"] == cfg["point"])
    signs = p["sign_variants"][cfg["variant"]]
    ids = p["neurons"]
    source_types = {
        ids[0]: "E1",
        ids[1]: "E2",
        ids[2]: "I1",
        ids[3]: "E1",
        ids[4]: "E2",
        ids[5]: "I1",
        10045: "DNg100",
        10056: "DNg100",
    }
    w, b = np.zeros((6, 6)), np.zeros((6, 2))
    for e in graph:
        weight = point["b"] * e["synapse_count"] * signs[source_types[e["pre"]]]
        post = ids.index(e["post"])
        if e["pre"] in p["sources"]:
            b[post, p["sources"].index(e["pre"])] = weight
        else:
            w[post, ids.index(e["pre"])] = weight
    if cfg["role"] == "feedback_disabled":
        w *= 0
    if cfg["role"] == "source_off":
        b *= 0
    return w, b, point


def run(p, graph, cfg):
    w, b, point = matrices(p, graph, cfg)
    params = model.RateParameters(tau_s=point["tau_s"])
    dt = p["refinement_dt_s"] if cfg["role"] == "half_dt" else p["integration_dt_s"]
    initial = np.full(6, 2.0 if cfg["role"] == "initial_2" else 0.0)
    output = model.simulate(
        w,
        b,
        params,
        initial,
        dt,
        p["sample_dt_s"],
        p["duration_s"],
        [0.0, 0.0] if cfg["role"] == "source_off" else p["schedules"][cfg["schedule"]],
    )
    metrics = []
    classification = "NUMERICAL_DIVERGENCE"
    sides = {"L": classification, "R": classification}
    if output["termination"] == "COMPLETED":
        values = np.asarray(output["states"])
        metrics = [
            model.cell_metrics(output["times_s"], values[:, i], p["metrics"])
            for i in range(6)
        ]
        classification = model.classify(metrics, output["final_residual"], p["metrics"])
        sides = {
            side: model.classify(
                metrics[start : start + 3],
                max(output["final_residual_by_neuron"][start : start + 3]),
                p["metrics"],
            )
            for side, start in [("L", 0), ("R", 3)]
        }
    return {
        "configuration": cfg,
        "integration_dt_s": dt,
        "initial_rates": initial.tolist(),
        "counterfactual_W_post_pre": w.tolist(),
        "counterfactual_B_post_source": b.tolist(),
        "telemetry": output,
        "cell_metrics": metrics,
        "classification": classification,
        "side_classification": sides,
    }


def summarize(p, runs):
    counts, refinements, initial = {}, [], []
    for r in runs:
        counts[r["classification"]] = counts.get(r["classification"], 0) + 1
        cfg = r["configuration"]
        if cfg["role"] != "primary":
            continue

        def partner(role):
            return next(x for x in runs if x["configuration"] == {**cfg, "role": role})

        refined = partner("half_dt")
        complete = all(
            x["telemetry"]["termination"] == "COMPLETED" for x in [r, refined]
        )
        error = (
            float(
                np.max(
                    np.abs(
                        np.asarray(r["telemetry"]["states"])
                        - np.asarray(refined["telemetry"]["states"])
                    )
                )
            )
            if complete
            else None
        )
        robust = (
            complete
            and error <= p["metrics"]["refinement_max_error_cap_fraction"] * 200
        )
        robust = robust and r["classification"] == refined["classification"]
        for a, b in zip(r["cell_metrics"], refined["cell_metrics"]):
            if a["sustained"] or b["sustained"]:
                robust = robust and a["sustained"] == b["sustained"]
                if a["sustained"] and b["sustained"]:
                    robust = (
                        robust
                        and abs(a["period_s"] / b["period_s"] - 1)
                        <= p["metrics"]["refinement_period_relative_max"]
                    )
                    robust = (
                        robust
                        and abs(a["tail_amplitude"] / b["tail_amplitude"] - 1)
                        <= p["metrics"]["refinement_amplitude_relative_max"]
                    )
        refinements.append(
            {"configuration": cfg, "max_error": error, "robust": bool(robust)}
        )
        perturb = partner("initial_2")
        initial.append(
            {
                "configuration": cfg,
                "same_classification": r["classification"] == perturb["classification"],
                "perturbed_classification": perturb["classification"],
            }
        )
    primary = [r for r in runs if r["configuration"]["role"] == "primary"]
    rhythms = [
        r for r in primary if r["classification"] == "SUSTAINED_MODEL_OSCILLATION"
    ]
    if any(r["classification"] == "NUMERICAL_DIVERGENCE" for r in runs) or not all(
        x["robust"] for x in refinements
    ):
        decision = "RHYTHM_RESULT_INCONCLUSIVE"
    elif rhythms:
        decision = "RHYTHM_ASSUMPTION_DEPENDENT"
    elif any(r["classification"] == "INCONCLUSIVE" for r in primary):
        decision = "RHYTHM_RESULT_INCONCLUSIVE"
    else:
        decision = "NO_SUSTAINED_RHYTHM_OBSERVED"
    return {
        "classification_counts": counts,
        "refinement": refinements,
        "initial_sensitivity": initial,
        "scientific_result": decision,
    }


def experiment_config(p, graph):
    return {
        "schema": SCHEMA,
        "preregistration": p,
        "preregistration_sha256": POLICY_ID,
        "structural_edges": graph,
        "configurations": configurations(p),
        "software": {
            "source_parent_commit": p["source_commit"],
            "python": platform.python_version(),
            "numpy": np.__version__,
            "implementation_sha256": {
                x.name: hashlib.sha256(x.read_bytes()).hexdigest()
                for x in [Path(__file__), Path(model.__file__)]
            },
        },
        "body_actuation": "NONE",
        "functional_sign_status": "UNKNOWN_FOR_ALL_15_CONNECTIONS",
    }


def package(config, result):
    c, r = canonical_sha256(config), canonical_sha256(result)
    return dict(
        schema=SCHEMA,
        config=config,
        result=result,
        config_sha256=c,
        result_sha256=r,
        artifact_id=canonical_sha256({"config_sha256": c, "result_sha256": r}),
    )


def generate(output_root=DEFAULT_ROOT):
    p, graph = policy(), load_authority()
    runs = []
    for i, cfg in enumerate(configurations(p)):
        runs.append(run(p, graph, cfg))
        if (i + 1) % 15 == 0:
            print(f"Completed {i + 1}/275", flush=True)
    artifact = package(
        experiment_config(p, graph), {"runs": runs, "summary": summarize(p, runs)}
    )
    root = Path(output_root).resolve()
    if root.is_relative_to(REPO):
        raise ValueError("simulation output must remain outside Git")
    root.mkdir(parents=True, exist_ok=True)
    dest = root / artifact["artifact_id"]
    if dest.exists():
        raise ValueError("refusing to overwrite existing artifact")
    with tempfile.TemporaryDirectory(dir=root) as temp:
        stage = Path(temp) / "artifact"
        stage.mkdir()
        data = canonical_json_bytes(artifact, newline=True)
        (stage / "dynamics.json").write_bytes(data)
        (stage / "manifest.json").write_bytes(
            canonical_json_bytes(
                {
                    "schema": SCHEMA,
                    "artifact_id": artifact["artifact_id"],
                    "files": {
                        "dynamics.json": {
                            "bytes": len(data),
                            "sha256": hashlib.sha256(data).hexdigest(),
                        }
                    },
                },
                newline=True,
            )
        )
        stage.rename(dest)
    return dest


def validate(value):
    p, graph = policy(), load_authority()
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
        or not isinstance(value["result"], dict)
        or set(value["result"]) != {"runs", "summary"}
    ):
        raise ValueError("malformed artifact")
    if value != package(value["config"], value["result"]):
        raise ValueError("artifact identity/schema/hash mismatch")
    if value["config"] != experiment_config(p, graph):
        raise ValueError("contradictory configuration/provenance")
    runs = value["result"]["runs"]
    if [r["configuration"] for r in runs] != configurations(p):
        raise ValueError("incomplete or contradictory run inventory")
    for i, r in enumerate(runs):
        if r != run(p, graph, r["configuration"]):
            raise ValueError("semantic numerical reproduction failure")
        if (i + 1) % 30 == 0:
            print(f"Reproduced {i + 1}/275", flush=True)
    if value["result"]["summary"] != summarize(p, runs):
        raise ValueError("contradictory summary")
    return value


def replay(path):
    path = Path(path)
    if {x.name for x in path.iterdir()} != {"dynamics.json", "manifest.json"}:
        raise ValueError("invalid artifact inventory")
    if any(x.is_symlink() for x in path.iterdir()):
        raise ValueError("unsafe artifact")
    raw = (path / "dynamics.json").read_bytes()
    v = json.loads(raw)
    manifest = json.loads((path / "manifest.json").read_bytes())
    expected = {
        "schema": SCHEMA,
        "artifact_id": v["artifact_id"],
        "files": {
            "dynamics.json": {
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        },
    }
    if (
        raw != canonical_json_bytes(v, newline=True)
        or manifest != expected
        or path.name != v["artifact_id"]
    ):
        raise ValueError("file/manifest integrity failure")
    return validate(v)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["generate", "replay"])
    parser.add_argument("--path", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        print(generate(args.path))
    else:
        v = replay(args.path)
        print(v["artifact_id"], v["result"]["summary"]["scientific_result"])


if __name__ == "__main__":
    main()
