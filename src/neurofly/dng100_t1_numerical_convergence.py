"""Independent targeted numerical reference; no physiological sign inference."""

import argparse
import hashlib
import inspect
import json
import math
import platform
import tempfile
from pathlib import Path

import numpy as np

from neurofly import dng100_t1_counterfactual_dynamics as model
from neurofly import dng100_t1_dynamics_sensitivity as v0
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

POLICY_PATH = v0.REPO / "docs/science/dng100_t1_convergence_preregistration.json"
POLICY_ID = "ab20411d2abd16d728b3b5eacb3d94c2fe01da772f0056acc955640e8f285254"
DEFAULT_ROOT = v0.REPO.parent / "neurofly-science/work/dng100-t1-convergence-v1"
SCHEMA = "dng100_t1_numerical_convergence_artifact_v1"


def policy():
    p = json.loads(POLICY_PATH.read_bytes())
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("convergence preregistration mismatch")
    return p


def scipy_identity():
    try:
        import scipy
        from scipy.integrate import _ivp
    except ImportError:
        raise ValueError("recorded independent SciPy solver is unavailable") from None
    return {
        "version": scipy.__version__,
        "source_hashes": {
            Path(inspect.getfile(m)).name: hashlib.sha256(
                Path(inspect.getfile(m)).read_bytes()
            ).hexdigest()
            for m in [_ivp.rk, _ivp.ivp, _ivp.dop853_coefficients]
        },
    }


def source(p):
    if canonical_sha256(p) != POLICY_ID:
        raise ValueError("unregistered source/model configuration")
    for name, expected in p["source_6_file_sha256"].items():
        path = v0.REPO / name
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected
        ):
            raise ValueError("original v0 source file changed")
    path = v0.DEFAULT_ROOT / p["source_artifact_id"]
    raw = (path / "dynamics.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != p["source_raw_sha256"]:
        raise ValueError("original v0 raw artifact changed")
    a = json.loads(raw)
    manifest = json.loads((path / "manifest.json").read_bytes())
    if (
        a != v0.package(a["config"], a["result"])
        or raw != canonical_json_bytes(a, newline=True)
        or a["config_sha256"] != p["source_config_sha256"]
        or a["result_sha256"] != p["source_result_sha256"]
        or manifest
        != {
            "schema": v0.SCHEMA,
            "artifact_id": p["source_artifact_id"],
            "files": {
                "dynamics.json": {
                    "bytes": len(raw),
                    "sha256": p["source_raw_sha256"],
                }
            },
        }
        or a["config"] != v0.experiment_config(v0.policy(), v0.load_authority())
    ):
        raise ValueError("original v0 identity/provenance mismatch")
    runs = a["result"]["runs"]
    if [r["configuration"] for r in runs] != v0.configurations(v0.policy()):
        raise ValueError("original 275-run inventory changed")
    chosen = [
        next(r for r in runs if r["configuration"] == {**p["condition"], "role": role})
        for role in ["primary", "half_dt"]
    ]
    return a, chosen


def independent_matrices(p, original):
    """Rebuild from raw directed records, not production matrix construction."""
    ids, dn = p["state_order"], p["sources"]
    negative = {801884, 803183}
    w, b = np.zeros((6, 6)), np.zeros((6, 2))
    graph = original["config"]["structural_edges"]
    for edge in graph:
        pre, post = edge["pre"], edge["post"]
        weight = edge["synapse_count"] * 0.06 * (-1 if pre in negative else 1)
        if pre in dn:
            b[ids.index(post), dn.index(pre)] = weight
        else:
            w[ids.index(post), ids.index(pre)] = weight
    return w, b


def independent_rhs(state, w, b, source_rate):
    """Scalar half-tanh accumulation, independent from production derivative."""
    rates = []
    for i in range(len(state)):
        total = math.fsum(w[i, j] * float(state[j]) for j in range(len(state)))
        total += math.fsum(float(x) * source_rate for x in b[i])
        target = max(200.0 * math.tanh((total - 7.5) / 200.0), 0.0)
        rates.append((target - float(state[i])) / 0.02)
    return np.array(rates)


def solve_piecewise(rhs, initial, times, pieces, settings):
    """Independent adaptive solves; dense interpolation never spans an input jump."""
    from scipy.integrate import solve_ivp

    t = np.asarray(times, dtype=float)
    state = np.asarray(initial, dtype=float)
    if (
        t.ndim != 1
        or len(t) < 2
        or not np.isfinite(t).all()
        or not np.isfinite(state).all()
        or state.ndim != 1
        or np.any(np.diff(t) <= 0)
        or not pieces
        or pieces[0][0] != t[0]
        or pieces[-1][1] != t[-1]
        or any(a[1] != b[0] for a, b in zip(pieces, pieces[1:]))
        or any(not np.isfinite(x).all() or x[0] >= x[1] for x in pieces)
        or not np.isfinite(list(settings.values())).all()
        or any(x <= 0 for x in settings.values())
        or set(settings) != {"rtol", "atol", "max_step_s"}
    ):
        raise ValueError("invalid independent-solver timing/configuration")
    out = np.empty((len(t), len(state)))
    out[0] = state
    assigned = np.zeros(len(t), dtype=bool)
    assigned[0] = True
    stats = []
    for start, end, rate in pieces:
        sol = solve_ivp(
            lambda time, y: rhs(y, rate),
            (start, end),
            state,
            method="DOP853",
            dense_output=True,
            rtol=settings["rtol"],
            atol=settings["atol"],
            max_step=settings["max_step_s"],
        )
        if not sol.success or sol.status != 0 or sol.t[-1] != end:
            raise ValueError("independent solver did not complete interval")
        state = sol.sol(end)
        mask = (t > start) & (t <= end)
        out[mask] = sol.sol(t[mask]).T
        assigned[mask] = True
        stats.append(
            dict(
                start_s=start, end_s=end, rate=rate, nfev=sol.nfev, steps=len(sol.t) - 1
            )
        )
    if not assigned.all() or not np.isfinite(out).all():
        raise ValueError("incomplete/nonfinite independent reference")
    return {"times_s": t.tolist(), "states": out.tolist(), "solver_intervals": stats}


def compare(a, b, ids):
    if (
        a["times_s"] != b["times_s"]
        or not np.isfinite(a["times_s"]).all()
        or np.any(np.diff(a["times_s"]) <= 0)
    ):
        raise ValueError("comparison sample times are not identical/ordered")
    x, y = np.asarray(a["states"]), np.asarray(b["states"])
    if (
        x.shape != y.shape
        or x.shape != (len(a["times_s"]), len(ids))
        or not np.isfinite(x).all()
        or not np.isfinite(y).all()
    ):
        raise ValueError("comparison state dimensions/values mismatch")
    error = x - y
    row, col = np.unravel_index(np.abs(error).argmax(), error.shape)
    return {
        "max_absolute": float(np.abs(error).max()),
        "rms": float(np.sqrt(np.mean(error**2))),
        "time_s": a["times_s"][row],
        "body_id": ids[col],
        "per_state": [
            {
                "body_id": body,
                "max_absolute": float(np.abs(error[:, i]).max()),
                "rms": float(np.sqrt(np.mean(error[:, i] ** 2))),
            }
            for i, body in enumerate(ids)
        ],
    }


def properties(trace, rules):
    values = np.asarray(trace["states"])
    tail = values[np.asarray(trace["times_s"]) >= 1.0]
    return [
        {
            **model.cell_metrics(trace["times_s"], values[:, i], rules),
            "tail_mean": float(np.mean(tail[:, i])),
        }
        for i in range(6)
    ]


def phase_diagnostic(a, b):
    t = np.asarray(a["times_s"])
    x, y = np.asarray(a["states"]), np.asarray(b["states"])
    mask = (t >= 1.5) & (t <= 1.999)
    results = []
    for side, start in [("L", 0), ("R", 3)]:
        scores = []
        for lag in np.arange(-0.0002, 0.00020001, 0.000001):
            shifted = np.stack(
                [np.interp(t[mask] + lag, t, y[:, i]) for i in range(start, start + 3)],
                axis=1,
            )
            scores.append(
                (
                    float(np.mean((x[mask, start : start + 3] - shifted) ** 2)),
                    float(lag),
                )
            )
        mse, lag = min(scores)
        results.append(
            {
                "side": side,
                "lag_s": lag,
                "raw_rms": float(
                    np.sqrt(
                        np.mean(
                            (x[mask, start : start + 3] - y[mask, start : start + 3])
                            ** 2
                        )
                    )
                ),
                "aligned_rms": math.sqrt(mse),
            }
        )
    return {"classification": "SECONDARY_NOT_ACCEPTANCE", "sides": results}


def evaluate(p, traces, props):
    rules = p["metrics"]
    ids = p["state_order"]
    reference = traces["reference_tight"]
    reference_error = compare(traces["reference"], reference, ids)
    ref_ok = (
        reference_error["max_absolute"] <= rules["reference_max_difference"]
        and reference_error["rms"] <= rules["reference_rms_difference"]
    )
    errors = {str(dt): compare(traces[str(dt)], reference, ids) for dt in p["steps_s"]}
    fine_ok = all(
        errors[str(dt)]["max_absolute"] <= rules["fine_max_error"]
        and errors[str(dt)]["rms"] <= rules["fine_rms_error"]
        for dt in p["new_steps_s"]
    )
    trend = all(
        errors[str(b)]["max_absolute"]
        <= errors[str(a)]["max_absolute"] + rules["monotonic_error_slack"]
        for a, b in zip(p["steps_s"], p["steps_s"][1:])
    )
    fine_pair = compare(
        traces[str(p["new_steps_s"][0])], traces[str(p["new_steps_s"][1])], ids
    )
    fine_ok = (
        fine_ok
        and trend
        and fine_pair["max_absolute"] <= rules["successive_fine_difference_max"]
    )
    properties_ok = all(
        any(x["sustained"] for x in props["reference_tight"][start : start + 3])
        for start in [0, 3]
    )
    property_errors = {}
    for label in ["reference", *[str(dt) for dt in p["new_steps_s"]]]:
        cells = []
        for actual, target in zip(props[label], props["reference_tight"]):
            period_error = (
                abs(actual["period_s"] / target["period_s"] - 1)
                if actual["period_s"] and target["period_s"]
                else None
            )
            amplitude_error = (
                abs(actual["tail_amplitude"] / target["tail_amplitude"] - 1)
                if target["tail_amplitude"] > 0
                else None
            )
            mean_error = abs(actual["tail_mean"] - target["tail_mean"])
            good = (
                actual["sustained"] == target["sustained"]
                and period_error is not None
                and amplitude_error is not None
                and period_error <= rules["period_relative_max"]
                and amplitude_error <= rules["amplitude_relative_max"]
                and mean_error <= rules["mean_absolute_max"]
            )
            properties_ok = properties_ok and good
            cells.append(
                dict(
                    period_relative=period_error,
                    amplitude_relative=amplitude_error,
                    mean_absolute=mean_error,
                    accepted=bool(good),
                )
            )
        property_errors[label] = cells
    decision = "DNG100_T1_CONVERGENCE_INCONCLUSIVE"
    if ref_ok and properties_ok:
        decision = (
            "DNG100_T1_CONVERGENCE_VERIFIED"
            if fine_ok
            else "DNG100_T1_OSCILLATION_PROPERTIES_ONLY"
        )
    return {
        "reference_agreement": reference_error,
        "reference_accepted": bool(ref_ok),
        "errors_vs_tight_reference": errors,
        "successive_fine_error": fine_pair,
        "raw_convergence_accepted": bool(fine_ok),
        "property_errors": property_errors,
        "properties_accepted": bool(properties_ok),
        "decision": decision,
        "v0_failure_preserved": compare(
            traces[str(p["steps_s"][0])], traces[str(p["steps_s"][1])], ids
        ),
    }


def config(p, original):
    identity = scipy_identity()
    if identity != {
        "version": p["reference"]["scipy_version"],
        "source_hashes": p["reference"]["source_hashes"],
    }:
        raise ValueError("independent solver version/source mismatch")
    return {
        "schema": SCHEMA,
        "preregistration": p,
        "preregistration_id": POLICY_ID,
        "original_v0_preregistration": original["config"]["preregistration"],
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": identity,
            "implementation_sha256": hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest(),
        },
        "functional_sign_status": "ALL_15_UNKNOWN",
        "body_actuation": "NONE",
    }


def experiment(p, original, selected):
    w, b = independent_matrices(p, original)
    for r in selected:
        if not np.array_equal(w, r["counterfactual_W_post_pre"]) or not np.array_equal(
            b, r["counterfactual_B_post_source"]
        ):
            raise ValueError("independent directed-weight reconstruction disagrees")
    traces = {str(dt): r["telemetry"] for dt, r in zip(p["steps_s"][:2], selected)}
    times = selected[0]["telemetry"]["times_s"]
    for setting in p["reference"]["runs"]:
        print("Solving", setting["id"], flush=True)
        options = {k: value for k, value in setting.items() if k != "id"}
        trace = solve_piecewise(
            lambda y, rate: independent_rhs(y, w, b, rate),
            p["model"]["initial"],
            times,
            [(0.0, 0.02, 0.0), (0.02, 2.0, 20.0)],
            options,
        )
        states = np.asarray(trace["states"])
        if np.any(states < -1e-8) or np.any(states > 200 + 1e-8):
            raise ValueError("independent reference violates state invariant")
        traces[setting["id"]] = trace
    for dt in p["new_steps_s"]:
        print("Solving RK4", dt, flush=True)
        trace = model.simulate(
            w,
            b,
            model.RateParameters(),
            p["model"]["initial"],
            dt,
            0.001,
            2.0,
            [0.02, 2.0],
        )
        if trace["termination"] != "COMPLETED":
            raise ValueError("fine RK4 numerical failure")
        traces[str(dt)] = trace
    props = {
        key: properties(trace, original["config"]["preregistration"]["metrics"])
        for key, trace in traces.items()
    }
    return {
        "traces": traces,
        "cell_properties": props,
        "assessment": evaluate(p, traces, props),
        "phase_secondary": {
            str(dt): phase_diagnostic(traces[str(dt)], traces["reference_tight"])
            for dt in p["steps_s"]
        },
        "v0_outcomes_unchanged": [
            "DNG100_T1_DYNAMICS_NUMERIC_ONLY",
            "RHYTHM_RESULT_INCONCLUSIVE",
        ],
        "weights_post_pre": w.tolist(),
        "source_weights": b.tolist(),
    }


def package(c, r):
    ch, rh = canonical_sha256(c), canonical_sha256(r)
    return dict(
        schema=SCHEMA,
        config=c,
        result=r,
        config_sha256=ch,
        result_sha256=rh,
        artifact_id=canonical_sha256({"config_sha256": ch, "result_sha256": rh}),
    )


def generate(root=DEFAULT_ROOT):
    p = policy()
    original, selected = source(p)
    c = config(p, original)
    artifact = package(c, experiment(p, original, selected))
    root = Path(root).resolve()
    if root.is_relative_to(v0.REPO):
        raise ValueError("convergence output must remain outside Git")
    root.mkdir(parents=True, exist_ok=True)
    dest = root / artifact["artifact_id"]
    if dest.exists():
        raise ValueError("refusing to overwrite scientific artifact")
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        stage = Path(tmp) / "artifact"
        stage.mkdir()
        data = canonical_json_bytes(artifact, newline=True)
        (stage / "convergence.json").write_bytes(data)
        (stage / "manifest.json").write_bytes(
            canonical_json_bytes(
                {
                    "schema": SCHEMA,
                    "artifact_id": artifact["artifact_id"],
                    "files": {
                        "convergence.json": {
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
    p = policy()
    original, selected = source(p)
    if not isinstance(value, dict) or set(value) != {
        "schema",
        "config",
        "result",
        "config_sha256",
        "result_sha256",
        "artifact_id",
    }:
        raise ValueError("malformed convergence artifact")
    if value != package(value["config"], value["result"]) or value["config"] != config(
        p, original
    ):
        raise ValueError("contradictory convergence identity/configuration")
    if value["result"] != experiment(p, original, selected):
        raise ValueError("convergence semantic reproduction mismatch")
    return value


def replay(path):
    path = Path(path)
    if (
        not path.is_dir()
        or {f.name for f in path.iterdir()} != {"convergence.json", "manifest.json"}
        or any(f.is_symlink() for f in path.iterdir())
    ):
        raise ValueError("invalid convergence artifact inventory")
    raw = (path / "convergence.json").read_bytes()
    a = json.loads(raw)
    manifest_raw = (path / "manifest.json").read_bytes()
    manifest = json.loads(manifest_raw)
    expected = {
        "schema": SCHEMA,
        "artifact_id": a["artifact_id"],
        "files": {
            "convergence.json": {
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        },
    }
    if (
        raw != canonical_json_bytes(a, newline=True)
        or manifest_raw != canonical_json_bytes(manifest, newline=True)
        or manifest != expected
        or path.name != a["artifact_id"]
    ):
        raise ValueError("convergence raw manifest/hash mismatch")
    return validate(a)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["generate", "replay"])
    parser.add_argument("--path", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        print(generate(args.path))
    else:
        a = replay(args.path)
        print(a["artifact_id"], a["result"]["assessment"]["decision"])


if __name__ == "__main__":
    main()
