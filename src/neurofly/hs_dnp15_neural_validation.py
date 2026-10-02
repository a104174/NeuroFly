"""Preregistered signed continuous HS→DNp15 chemical-motif proxy.

This model ends at neural readout. It has no spikes, motor/body mapping or
physiological voltage units. Structural contact counts are provenance only.
"""

import json
import math
from pathlib import Path

from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

SCIENCE_ROOT = Path(__file__).resolve().parents[2] / "docs/science"
PREREGISTRATION_PATH = SCIENCE_ROOT / "hs_dnp15_neural_validation_preregistration.json"
PREREGISTRATION_ID = "371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074"
SELECTION_ID = "435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41"
V1_ID = "1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6"
CONFIG_SCHEMA = "hs_dnp15_neural_validation_config_v1"
RESULT_SCHEMA = "hs_dnp15_neural_validation_result_v1"
ARTIFACT_SCHEMA = "hs_dnp15_neural_validation_artifact_v1"
ROUTE_KEYS = frozenset(
    {
        (10015, 11215),
        (10016, 11215),
        (10023, 11215),
        (10034, 12069),
        (10181, 12069),
        (10419, 12069),
    }
)


def _ordered(rows, key="body_id"):
    return sorted(rows, key=lambda row: row[key])


def load_structural_authority():
    """Offline committed evidence, not a network query or fixture relabelling."""
    v1 = json.loads((SCIENCE_ROOT / "neurofly_v1_scientific_status.json").read_bytes())
    selection = json.loads(
        (SCIENCE_ROOT / "second_circuit_selection_gate.json").read_bytes()
    )
    if v1["status_id"] != V1_ID or canonical_sha256(v1["status"]) != V1_ID:
        raise ValueError("frozen v1 authority mismatch")
    if (
        selection["selection_id"] != SELECTION_ID
        or canonical_sha256(selection["selection"]) != SELECTION_ID
    ):
        raise ValueError("Phase 24 structural authority mismatch")
    record = selection["selection"]
    contract = record["selected_contract"]
    candidate = next(
        item
        for item in record["candidates"]
        if item["id"] == record["selected_candidate_id"]
    )
    if (
        record["source_v1_status_id"] != V1_ID
        or contract["candidate_id"] != "hs_dnp15_horizontal_motion"
        or candidate["classification"] != "READY_FOR_BOUNDED_VALIDATION_DESIGN"
        or contract["dataset"] != "male-cns:v1.0"
    ):
        raise ValueError("selected motif identity/classification mismatch")
    for query in record["structural_provenance"]["queries"]:
        if canonical_sha256(query["rows"]) != query["response_sha256"]:
            raise ValueError("structural query response hash mismatch")
    if {
        (e["source_id"], e["target_id"]) for e in contract["structural_edges"]
    } != ROUTE_KEYS:
        raise ValueError("selected routing keys differ from authority")
    return contract


def load_preregistration(path=PREREGISTRATION_PATH):
    contract = json.loads(Path(path).read_bytes())
    if canonical_sha256(contract) != PREREGISTRATION_ID:
        raise ValueError("frozen HS/DNp15 preregistration mismatch")
    authority = load_structural_authority()
    if (
        contract["selection_record_id"] != SELECTION_ID
        or contract["v1_status_id"] != V1_ID
        or contract["source_identities"] != _ordered(authority["source_identities"])
        or contract["target_identities"] != _ordered(authority["target_identities"])
        or contract["selected_routes"]
        != _ordered(authority["structural_edges"], "source_id")
        or contract["omitted_induced_edges"]
        != authority["full_induced_edges_not_selected"]
    ):
        raise ValueError("frozen identities/routes/omissions differ from authority")
    return contract


def proxy_step(state, drive, dt_ms, tau_ms):
    """Signed exact held-drive leaky proxy; not the v1 sensory or LIF model."""
    values = (state, drive, dt_ms, tau_ms)
    if any(
        isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
        for v in values
    ):
        raise ValueError("proxy step requires finite model coordinates")
    if dt_ms <= 0 or tau_ms <= 0:
        raise ValueError("proxy time constants/grid must be positive")
    return drive + (state - drive) * math.exp(-dt_ms / tau_ms)


def route_contributions(source_states, routes, targets, scale):
    """Pure three-channel mean. Counts are never read as numerical inputs.

    Accepting counts as provenance allows test-local mutation without changing
    execution. Canonical production inputs are pinned by load_preregistration.
    """
    selected = sorted(routes, key=lambda edge: (edge["source_id"], edge["target_id"]))
    totals = {target["body_id"]: 0.0 for target in _ordered(targets)}
    if len(targets) != 2 or set(totals) != {11215, 12069}:
        raise ValueError("bilateral target identity mismatch")
    if {(r["source_id"], r["target_id"]) for r in selected} != ROUTE_KEYS:
        raise ValueError("route not part of selected chemical motif")
    if (
        len(selected) != 6
        or len({(r["source_id"], r["target_id"]) for r in selected}) != 6
    ):
        raise ValueError("motif must contain exactly six unique routes")
    if any(sum(r["target_id"] == target for r in selected) != 3 for target in totals):
        raise ValueError("each target requires three eligible channels")
    if set(source_states) != {r["source_id"] for r in selected}:
        raise ValueError("identity-resolved source state mismatch")
    contributions = []
    for route in selected:
        if route["target_id"] not in totals:
            raise ValueError("unknown route target")
        state = source_states[route["source_id"]]
        if not math.isfinite(state) or not math.isfinite(scale):
            raise ValueError("nonfinite proxy transfer")
        value = scale * state / 3.0
        contributions.append(value)
        totals[route["target_id"]] += value
    return contributions, [totals[t["body_id"]] for t in _ordered(targets)]


def _execute(contract):
    sources = _ordered(contract["source_identities"])
    targets = _ordered(contract["target_identities"])
    dt = contract["dt_ms"]
    intervals = contract["interval_count"]
    times = [step * dt for step in range(intervals + 1)]
    runs = []
    for condition in contract["conditions"]:
        state = [contract["source_model"]["initial_state"]] * len(sources)
        target_state = [contract["target_model"]["initial_state"]] * len(targets)
        inputs, source_rows, target_rows, routes, drives, differences = (
            [],
            [],
            [],
            [],
            [],
            [],
        )
        for n in range(intervals + 1):
            active = (
                contract["input"]["onset_boundary"]
                <= n
                < contract["input"]["offset_boundary"]
            )
            descriptor = {
                "R": condition["right"] if active else 0.0,
                "L": condition["left"] if active else 0.0,
            }
            contributions, drive = route_contributions(
                dict(zip((s["body_id"] for s in sources), state, strict=True)),
                contract["selected_routes"],
                targets,
                contract["transfer"]["coefficient"],
            )
            inputs.append(descriptor)
            source_rows.append(state.copy())
            target_rows.append(target_state.copy())
            routes.append(contributions)
            drives.append(drive)
            by_side = {
                t["side"]: value for t, value in zip(targets, target_state, strict=True)
            }
            differences.append(by_side["R"] - by_side["L"])
            if n == intervals:
                break
            # Target uses s[n]; new exposure/input only changes s[n+1].
            next_target = [
                proxy_step(value, held, dt, contract["target_model"]["tau_ms"])
                for value, held in zip(target_state, drive, strict=True)
            ]
            next_source = [
                proxy_step(
                    value, descriptor[s["side"]], dt, contract["source_model"]["tau_ms"]
                )
                for s, value in zip(sources, state, strict=True)
            ]
            state, target_state = next_source, next_target
        summaries = []
        for j, target in enumerate(targets):
            peak = max(range(len(times)), key=lambda n: abs(target_rows[n][j]))
            summaries.append(
                {
                    "body_id": target["body_id"],
                    "side": target["side"],
                    "peak_absolute_state": abs(target_rows[peak][j]),
                    "state_at_absolute_peak": target_rows[peak][j],
                    "peak_step": peak,
                    "peak_time_ms": times[peak],
                    "final_state": target_rows[-1][j],
                }
            )
        runs.append(
            {
                "condition_id": condition["id"],
                "input_descriptors": inputs,
                "source_states": source_rows,
                "route_contributions": routes,
                "target_drives": drives,
                "target_states": target_rows,
                "right_minus_left_diagnostic": differences,
                "target_events": None,
                "target_summaries": summaries,
                "execution_completed": True,
            }
        )
    return {
        "schema": RESULT_SCHEMA,
        "time_ms": times,
        "source_order": sources,
        "target_order": targets,
        "route_order": _ordered(contract["selected_routes"], "source_id"),
        "state_units": {
            "source": contract["source_model"]["state_units"],
            "target": contract["target_model"]["state_units"],
        },
        "event_semantics": "NOT_DEFINED",
        "runs": runs,
        "limitations": contract["claim_limits"],
    }


def build_neural_validation():
    """Production execution accepts only the frozen contract, no overrides."""
    contract = load_preregistration()
    model = {
        key: contract[key]
        for key in (
            "model_identity",
            "input",
            "source_model",
            "transfer",
            "target_model",
            "tick_semantics",
        )
    }
    config = {
        "schema": CONFIG_SCHEMA,
        "preregistration_id": PREREGISTRATION_ID,
        "structural_authority_id": SELECTION_ID,
        "v1_status_id": V1_ID,
        "model_sha256": canonical_sha256(model),
        "preregistration": contract,
    }
    result = _execute(contract)
    config_hash, result_hash = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema": ARTIFACT_SCHEMA,
        "config": config,
        "result": result,
        "config_sha256": config_hash,
        "result_sha256": result_hash,
        "artifact_id": canonical_sha256([ARTIFACT_SCHEMA, config_hash, result_hash]),
    }


def validate_neural_validation(response):
    expected = build_neural_validation()
    if canonical_json_bytes(response) != canonical_json_bytes(expected):
        raise ValueError("HS/DNp15 artifact differs from frozen offline replay")
    return expected
