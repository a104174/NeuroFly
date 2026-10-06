"""Frozen composition: geometric observation -> neural proxies -> orientation.

No biological yaw, motor/translation, chemical recurrence or product endpoint.
All three scientific kernels remain in their existing modules.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from neurofly import dnp15_exploratory_yaw as embodiment
from neurofly import hs_dnp15_neural_validation as neural
from neurofly import orientation_to_horizontal_motion as observation
from neurofly.dnp15_exploratory_yaw_artifacts import (
    DEFAULT_ARTIFACT_ROOT as YAW_ROOT,
)
from neurofly.dnp15_exploratory_yaw_artifacts import replay_yaw_artifact
from neurofly.hs_dnp15_neural_validation_artifacts import (
    DEFAULT_ARTIFACT_ROOT as NEURAL_ROOT,
)
from neurofly.hs_dnp15_neural_validation_artifacts import replay_neural_artifact
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

PREREGISTRATION_ID = "efc27a18e1d19119b8eebc5d0f8b91e61a47337dbb9f60e2518fabc42672cd0f"
ANALYSIS_ID = "a8e82f1561df6deb05216d795f7d61067c9338fefffb5cb7d2a415f6a3464586"
SCIENCE_ROOT = Path(__file__).resolve().parents[2] / "docs/science"
PREREGISTRATION_PATH = (
    SCIENCE_ROOT / "exploratory_course_control_closed_loop_preregistration.json"
)
CONFIG_SCHEMA = "exploratory_course_control_closed_loop_config_v1"
RESULT_SCHEMA = "exploratory_course_control_closed_loop_result_v1"
ARTIFACT_SCHEMA = "exploratory_course_control_closed_loop_artifact_v1"


def load_preregistration(path=PREREGISTRATION_PATH):
    p = json.loads(Path(path).read_bytes())
    if (
        canonical_sha256(p) != PREREGISTRATION_ID
        or canonical_sha256(p["analysis"]) != ANALYSIS_ID
        or p["analysis_id"] != ANALYSIS_ID
        or p["analysis"]["decision"]
        != "CLOSED_LOOP_COMPOSITION_MARGINAL_BUT_BOUNDED_FOR_FINITE_HORIZON_TEST"
        or p["analysis"]["stage_b_permitted"] is not True
    ):
        raise ValueError("frozen composition preregistration/Stage A mismatch")
    # Metadata identity validation only: never derive dynamic parameters from
    # evidence/context documents. Parameters come from frozen component APIs.
    for authority in p["authority_records"]:
        filename = authority["document"]
        if Path(filename).name != filename:
            raise ValueError("authority must be a science document basename")
        raw = (SCIENCE_ROOT / filename).read_bytes()
        key = authority["inner_key"]
        if key == "DOCUMENT_BYTES":
            digest = hashlib.sha256(raw).hexdigest()
        else:
            record = json.loads(raw)
            digest = canonical_sha256(record[key] if key else record)
        if digest != authority["canonical_id"]:
            raise ValueError("frozen source document authority mismatch")
    return p


@dataclass(frozen=True)
class Components:
    neural_contract: dict
    embodiment_contract: dict
    observation_contract: observation.ObservationContract


def load_components(p):
    components = Components(
        neural.load_preregistration(),
        embodiment.load_preregistration(),
        observation.load_contract(),
    )
    n, y = components.neural_contract, components.embodiment_contract
    if (
        p["dt_ms"] != n["dt_ms"]
        or p["duration_ms"] != y["duration_ms"]
        or p["interval_count"] != n["interval_count"]
        or p["world"]["period_eq"] != components.observation_contract.period_eq
    ):
        raise ValueError("composition grid differs from frozen component contracts")
    verify_analysis(p, components)
    return components


def verify_analysis(p, components):
    """Matrix/eigenvalue audit only, not a time-domain candidate execution."""
    n = components.neural_contract
    a = math.exp(-p["dt_ms"] / n["source_model"]["tau_ms"])
    b = math.exp(-p["dt_ms"] / n["target_model"]["tau_ms"])
    matrix = np.array([[a, 0, -2 * (1 - a)], [1 - b, b, 0], [0, 1, 0]])
    record = p["analysis"]
    tolerance = record["eigenvalue_comparison_tolerance"]
    if not np.allclose(matrix, record["differential_matrix"], atol=tolerance, rtol=0):
        raise ValueError("analytical transition matrix mismatch")
    eigenvalues = np.linalg.eigvals(matrix)
    expected = [complex(*pair) for pair in record["differential_eigenvalues_real_imag"]]
    if any(
        min(abs(root - other) for other in eigenvalues) > tolerance for root in expected
    ):
        raise ValueError("analytical eigenvalue mismatch")
    radius = float(max(abs(eigenvalues)))
    if radius >= 1 or abs(radius - record["differential_spectral_radius"]) > tolerance:
        raise ValueError("local dynamics do not pass the frozen marginal-system gate")
    if record["full_spectral_radius"] != 1:
        raise ValueError("motion-only orientation unit mode must remain explicit")


def _bounded(values):
    if any(
        type(v) not in (int, float) or not math.isfinite(v) or abs(v) > 1
        for v in values
    ):
        raise ValueError("non-finite or out-of-range continuous neural proxy")


def compose_neural_interval(sources, targets, sides, interval_dt_ms, components):
    """Old-state simultaneous updates and a neutral-origin embodiment increment.

    The local orientation kernel has no leak: its increment can be accumulated
    without resetting the actual body orientation. Exogenous perturbation and
    experimental disconnection are handled separately by the experiment.
    """
    n, y = components.neural_contract, components.embodiment_contract
    if len(sources) != 6 or len(targets) != 2:
        raise ValueError("require six sources and two targets in canonical order")
    _bounded(sources + targets + [sides.right, sides.left])
    nodes = n["source_identities"]
    contributions, drives = neural.route_contributions(
        {node["body_id"]: value for node, value in zip(nodes, sources, strict=True)},
        n["selected_routes"],
        n["target_identities"],
        n["transfer"]["coefficient"],
    )
    delta, yaw_drive, increments = embodiment.integrate_orientation(
        [0, interval_dt_ms], [targets.copy(), targets.copy()], y
    )
    next_sources = [
        neural.proxy_step(
            state,
            sides.right if node["side"] == "R" else sides.left,
            n["dt_ms"],
            n["source_model"]["tau_ms"],
        )
        for node, state in zip(nodes, sources, strict=True)
    ]
    next_targets = [
        neural.proxy_step(state, drive, n["dt_ms"], n["target_model"]["tau_ms"])
        for state, drive in zip(targets, drives, strict=True)
    ]
    _bounded(next_sources + next_targets)
    return {
        "next_sources": next_sources,
        "next_targets": next_targets,
        "route_contributions": contributions,
        "target_drives": drives,
        "differential": delta[0],
        "yaw_drive_eq": yaw_drive[0],
        "proposed_orientation_increment_eq": increments[-1],
    }


def _crossings(values):
    nonzero = [v for v in values if v != 0]
    return sum(
        (a > 0) != (b > 0) for a, b in zip(nonzero[:-1], nonzero[1:], strict=True)
    )


def diagnostics(boundaries, perturbation):
    observed = [b["observation"] for b in boundaries if b["observation"] is not None]
    clipped = [o for o in observed if o["clipped"]]
    orientations = [b["yaw_orientation_eq"] for b in boundaries]
    differentials = [b["dnp15_differential"] for b in boundaries]
    motions = [b["latched_motion"]["right"] for b in boundaries]
    crossings = {
        "orientation": _crossings(orientations),
        "dnp15_differential": _crossings(differentials),
        "motion_descriptor": _crossings(motions),
    }
    return {
        "initial_perturbation_eq": perturbation,
        "max_absolute_orientation_eq": max(map(abs, orientations)),
        "final_orientation_eq": orientations[-1],
        "max_absolute_horizontal_motion_eq": max(map(abs, motions)),
        "absolute_peak_dnp15_differential": max(map(abs, differentials)),
        "final_absolute_dnp15_differential": abs(differentials[-1]),
        "subsequent_orientation_change_eq": orientations[-1] - perturbation,
        "clipping": {
            "count": len(clipped),
            "observed_interval_count": len(observed),
            "fraction": len(clipped) / len(observed) if observed else 0,
            "positive_count": sum(
                o["global_horizontal_motion_eq"] > 0 for o in clipped
            ),
            "negative_count": sum(
                o["global_horizontal_motion_eq"] < 0 for o in clipped
            ),
            "duration_ms": sum(o["dt_ms"] for o in clipped),
        },
        "sign_changes": crossings,
        "zero_crossing_brackets": crossings.copy(),
    }


def run_condition(condition, p, components):
    """One frozen intervention; no condition-specific coefficients or bias."""
    times = [n * p["dt_ms"] for n in range(p["interval_count"] + 1)]
    world = observation.WorldReference(
        p["world"]["reference_id"], p["world"]["heading_eq"]
    )
    ncontract = components.neural_contract
    sources = [p["initialization"]["all_six_HS_states"]] * 6
    targets = [p["initialization"]["both_DNp15_states"]] * 2
    theta = p["initialization"]["orientation_eq"]
    previous_theta = p["initialization"]["previous_orientation"]
    perturbation = (
        condition["perturbation_sign"] * p["perturbation"]["positive_increment_eq"]
    )
    boundaries = []
    termination = {
        "status": "COMPLETED_VALID_HORIZON",
        "boundary_index": len(times) - 1,
    }
    for index, time_ms in enumerate(times):
        try:
            obs = None
            sides = observation.neutral_initial_descriptors()
            if index > 0:
                obs = observation.observe_interval(
                    observation.ObservationInterval(
                        world,
                        observation.OrientationBoundary(
                            index - 1, times[index - 1], previous_theta
                        ),
                        observation.OrientationBoundary(index, time_ms, theta),
                    ),
                    contract=components.observation_contract,
                )
                sides = obs.sides
            _bounded(sources + targets)
            outgoing = index < len(times) - 1
            if outgoing:
                step = compose_neural_interval(
                    sources, targets, sides, times[index + 1] - time_ms, components
                )
                differential = step["differential"]
                yaw_drive = step["yaw_drive_eq"]
                proposed = step["proposed_orientation_increment_eq"]
                applied = (
                    proposed if condition["orientation_feedback_connected"] else 0.0
                )
                external = (
                    perturbation
                    if index == p["perturbation"]["interval_index"]
                    else 0.0
                )
            else:
                # Derived readouts only; no extra neural/embodiment integration.
                contributions, drives = neural.route_contributions(
                    dict(
                        zip(
                            (s["body_id"] for s in ncontract["source_identities"]),
                            sources,
                            strict=True,
                        )
                    ),
                    ncontract["selected_routes"],
                    ncontract["target_identities"],
                    ncontract["transfer"]["coefficient"],
                )
                step = {"route_contributions": contributions, "target_drives": drives}
                differential = targets[0] - targets[1]
                mapping = components.embodiment_contract["yaw_mapping"]
                yaw_drive = (
                    mapping["directional_sign"]
                    * mapping["dnp15_to_yaw_proxy_scale"]
                    * differential
                )
                proposed = applied = external = None
            boundaries.append(
                {
                    "boundary_index": index,
                    "time_ms": time_ms,
                    "world_reference": asdict(world),
                    "yaw_orientation_eq": theta,
                    "previous_orientation_eq": previous_theta,
                    "relative_view_eq": obs.relative_view_after_eq if obs else 0,
                    "observation": obs.payload() if obs else None,
                    "latched_motion": asdict(sides),
                    "hs_states": sources.copy(),
                    "dnp15_states": targets.copy(),
                    "route_contributions": step["route_contributions"],
                    "target_drives": step["target_drives"],
                    "dnp15_differential": differential,
                    "yaw_drive_eq": yaw_drive,
                    "proposed_neural_orientation_increment_eq": proposed,
                    "applied_neural_orientation_increment_eq": applied,
                    "external_orientation_increment_eq": external,
                    "observation_clipped": obs.clipped if obs else False,
                }
            )
            if not outgoing:
                break
            new_theta = theta + applied + external
            if (
                not math.isfinite(new_theta)
                or abs(new_theta) > 2 + abs(perturbation) + 1e-12
            ):
                raise ValueError(
                    "non-finite orientation or finite-horizon bound violation"
                )
            previous_theta, theta = theta, new_theta
            sources, targets = step["next_sources"], step["next_targets"]
        except (ValueError, TypeError, OverflowError) as exc:
            termination = {
                "status": "TERMINATED_INVALID_STATE",
                "boundary_index": index,
                "reason": str(exc),
            }
            break
    return {
        "condition": condition,
        "boundaries": boundaries,
        "termination": termination,
        "diagnostics": diagnostics(boundaries, perturbation) if boundaries else None,
    }


def build_closed_loop_artifact():
    p = load_preregistration()
    components = load_components(p)
    for key, root, replay in [
        ("phase25", NEURAL_ROOT, replay_neural_artifact),
        ("phase28", YAW_ROOT, replay_yaw_artifact),
    ]:
        authority = p["source_artifacts"][key]
        source = replay(root / authority["artifact_id"])
        if any(
            source[k] != authority[k]
            for k in ("artifact_id", "config_sha256", "result_sha256", "schema")
        ):
            raise ValueError("frozen numerical source authority mismatch")
    config = {
        "schema": CONFIG_SCHEMA,
        "preregistration_id": PREREGISTRATION_ID,
        "preregistration": p,
        "analysis_id": ANALYSIS_ID,
        "component_config_id": canonical_sha256(
            [
                components.neural_contract,
                components.embodiment_contract,
                asdict(components.observation_contract),
            ]
        ),
        "source_authorities": p["authority_records"],
        "source_artifacts": p["source_artifacts"],
    }
    result = {
        "schema": RESULT_SCHEMA,
        "source_order": components.neural_contract["source_identities"],
        "target_order": components.neural_contract["target_identities"],
        "active_routes": components.neural_contract["selected_routes"],
        "units": p["units"],
        "translation": "NOT_MODELLED",
        "chemical_recurrence": "NONE",
        "electrical_coupling": "NONE",
        "event_semantics": "NOT_DEFINED",
        "analysis_id": ANALYSIS_ID,
        "runs": [
            run_condition(condition, p, components) for condition in p["conditions"]
        ],
        "limitations": p["forbidden_claims"],
    }
    ch, rh = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema": ARTIFACT_SCHEMA,
        "config": config,
        "result": result,
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256([ARTIFACT_SCHEMA, ch, rh]),
    }


def validate_closed_loop_artifact(response):
    expected = build_closed_loop_artifact()
    if canonical_json_bytes(response) != canonical_json_bytes(expected):
        raise ValueError("closed-loop artifact differs from frozen offline replay")
    return expected
