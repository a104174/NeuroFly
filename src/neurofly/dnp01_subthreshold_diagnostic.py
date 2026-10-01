"""Read-only canonical response accounting; no alternate scientific config."""

from __future__ import annotations

import copy
import math

import numpy as np

from neurofly.closed_loop_scenario import HISTORICAL_IDS, load_scenario_sources
from neurofly.closed_loop_scenario_artifacts import (
    DEFAULT_ARTIFACT_ROOT as SCENARIO_ROOT,
)
from neurofly.closed_loop_scenario_artifacts import (
    replay_scenario_artifact,
)
from neurofly.relative_column_dnp01_transfer import route_population_drive
from neurofly.relative_column_sensory_dynamics import integrate_exposure_values
from neurofly.sensory_population_execution import _assert_sources
from neurofly.sensory_population_execution_cli import _inputs
from neurofly.simulation import ExternalDriveSchedule, LIFSimulator, lif_interval_step
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

CONFIG_SCHEMA = "dnp01_subthreshold_diagnostic_config_v1"
RESULT_SCHEMA = "dnp01_subthreshold_diagnostic_v1"
ARTIFACT_SCHEMA = "dnp01_subthreshold_diagnostic_artifact_v1"
SOURCE_ID = "55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b"
DEFAULT_SOURCE = SCENARIO_ROOT / SOURCE_ID
DECISION = "SUBTHRESHOLD_RESPONSE_CHARACTERIZED_TARGETED_MODEL_REVIEW_JUSTIFIED"
LIMITATIONS = [
    "NO_RETUNING_PERFORMED_NO_SPIKE_TARGETING_OR_PARAMETER_SELECTION",
    "MODEL_COORDINATES_NOT_BIOLOGICAL_MILLIVOLTS_OR_CURRENT",
    "MALECNS_IDENTITIES_SIDES_EDGES_COLUMNS_NOT_EFFICACY",
    "STRUCTURAL_CONTACT_COUNTS_ROUTING_METADATA_ONLY",
    "MODEL_LIMITERS_NOT_BIOLOGICAL_INADEQUACY_OR_UNIQUE_CAUSAL_RANKING",
    "FULL_EXPOSURE_BOUND_NOT_A_SCENARIO_OR_RETINAL_CALIBRATION",
]


class DiagnosticCompositionError(ValueError):
    """Accounting contradicts the historical authority; stop, do not repair."""


def load_verified_inputs(source_path=DEFAULT_SOURCE):
    battery = replay_scenario_artifact(source_path)
    if battery["artifact_id"] != SOURCE_ID:
        raise ValueError("require exact pinned Phase 13B artifact")
    sources = load_scenario_sources()
    _, _, execution = _assert_sources(*_inputs()[0])
    return battery, sources, execution["config"]


def _same(actual, expected, name):
    if not np.allclose(actual, expected, rtol=0, atol=2e-12):
        raise DiagnosticCompositionError(f"{name} differs from existing authority")


def _lif_trace(drives, sources):
    """Use the existing batch authority, including its threshold/reset rules."""
    schedule = ExternalDriveSchedule.from_body_ids(
        {body: [d[i] for d in drives] for i, body in enumerate((10001, 10010))},
        steps=len(drives),
        provenance_id=sources["lif"].input_drive_provenance_id,
    )
    return LIFSimulator(sources["graph"], sources["lif"]).run(
        schedule, allow_model_readout_drive=True
    )


def _route_states(states, identities, sources, transfer):
    ids = [r["body_id"] for r in identities]
    return route_population_drive(
        dict(zip(ids, states, strict=True)),
        sources["routes"],
        target_body_ids=(10001, 10010),
        active_source_ids=set(ids),
        k_transfer_mveq_per_state=transfer,
    )


def _integration_terms(result, sources):
    """Difference accounting via the actual kernel, not another LIF equation.

    Canonical readout has no spikes/synaptic deliveries/refractory activation.
    Zero-input and zero-synapse kernel evaluations isolate additive terms.
    """
    if result["dnp01_spikes"]:
        raise ValueError("v1 diagnosis requires canonical subthreshold no-spike run")
    terms = []
    refractory = np.zeros(2, dtype=np.int64)
    for n, drive in enumerate(result["dnp01_drive_by_interval"]):
        v = np.array(result["dnp01_membrane_mv"][n])
        s = np.array(result["dnp01_synaptic_mV_eq"][n])

        def evaluate(input_drive, synaptic):
            return lif_interval_step(
                sources["lif"],
                v.copy(),
                synaptic.copy(),
                refractory.copy(),
                np.array(input_drive),
            )

        leak, _, _ = evaluate([0.0, 0.0], np.zeros(2))
        driven, _, _ = evaluate(drive, np.zeros(2))
        actual, next_s, spikes = evaluate(drive, s)
        _same(actual, result["dnp01_membrane_mv"][n + 1], "LIF membrane")
        _same(next_s, result["dnp01_synaptic_mV_eq"][n + 1], "LIF synaptic state")
        if len(spikes):
            raise DiagnosticCompositionError("unexpected diagnostic threshold crossing")
        terms.append(
            {
                "step": n,
                "next_step": n + 1,
                "leak_delta_mV_eq": (leak - v).tolist(),
                "external_drive_delta_mV_eq": (driven - leak).tolist(),
                "synaptic_delta_mV_eq": (actual - driven).tolist(),
                "reset_refractory_delta_mV_eq": [0.0, 0.0],
                "refractory_remaining_steps": [0, 0],
                "net_delta_mV_eq": (actual - v).tolist(),
            }
        )
    return terms


def _diagnose_run(run, sources, model):
    result = run["result"]
    rows, time = result["sensory_identities"], result["time_ms"]
    lif = sources["lif"]
    dt = run["config"]["scenario"]["dt_ms"]
    k = model["transfer_model"]["k_transfer_mveq_per_state"]
    n_intervals = len(time) - 1
    by_id = {r["body_id"]: r for r in rows}
    drives, ledgers, boundaries = [], [], []
    population_drives = {typ: [] for typ in ("LC4", "LPLC2")}
    for n, states in enumerate(result["sensory_state_by_boundary"]):
        output, ledger = _route_states(states, rows, sources, k)
        available_drive = [output[i] for i in (10001, 10010)]
        drives.append(available_drive)
        ledgers.append(ledger)
        if n < n_intervals:
            if ledger != result["source_contributions_by_interval"][n]:
                raise DiagnosticCompositionError(
                    "identity contribution ledger mismatch"
                )
            _same(available_drive, result["dnp01_drive_by_interval"][n], "routed drive")
        groups = []
        for typ in ("LC4", "LPLC2"):
            population_drives[typ].append(
                [
                    sum(
                        c["model_drive_mveq"]
                        for c in ledger
                        if c["target_body_id"] == target
                        and by_id[c["source_body_id"]]["neuron_type"] == typ
                    )
                    for target in (10001, 10010)
                ]
            )
            for side in ("L", "R"):
                indices = [
                    i
                    for i, row in enumerate(rows)
                    if (row["neuron_type"], row["side"]) == (typ, side)
                ]
                values = [states[i] for i in indices]
                exposures = [result["exposure_by_boundary"][n][i] for i in indices]
                groups.append(
                    {
                        "neuron_type": typ,
                        "side": side,
                        "population_count": len(indices),
                        "exposed_count": sum(e > 0 for e in exposures),
                        "exposure_sum": sum(exposures),
                        "state_mean": sum(values) / len(values),
                        "state_max": max(values),
                        "state_sum": sum(values),
                        "nonzero_state_count": sum(v > 0 for v in values),
                    }
                )
        world = result["world_body"][n]
        geometry = copy.deepcopy(world["geometry"])
        boundaries.append(
            {
                "step": n,
                "time_ms": time[n],
                "geometry": geometry,
                "active_columns": copy.deepcopy(world["active_columns"]),
                "active_column_count": len(world["active_columns"]),
                "exposed_body_count": sum(
                    e > 0 for e in result["exposure_by_boundary"][n]
                ),
                "sensory_groups": groups,
                "available_model_drive_mV_eq": available_drive,
                "drives_outgoing_interval": n < n_intervals,
                "membrane_mV_eq": result["dnp01_membrane_mv"][n],
                "threshold_mV_eq": lif.threshold_mv,
                "threshold_margin_mV_eq": [
                    lif.threshold_mv - v for v in result["dnp01_membrane_mv"][n]
                ],
                "refractory_remaining_steps": [0, 0],
                "population_drive_mV_eq": {
                    typ: population_drives[typ][-1] for typ in population_drives
                },
                "population_fraction_of_available_drive": {
                    typ: [
                        part / total if total else None
                        for part, total in zip(
                            population_drives[typ][-1], available_drive, strict=True
                        )
                    ]
                    for typ in population_drives
                },
            }
        )
    # Verify the sensory trace with its historical batch authority; no equation copy.
    for i in range(len(rows)):
        expected = integrate_exposure_values(
            [e[i] for e in result["exposure_by_boundary"][:-1]],
            dt_ms=dt,
            tau_sens_ms=model["sensory_model"]["tau_sens_ms"],
            gain=model["sensory_model"]["gain"],
        )
        _same(
            [s[i] for s in result["sensory_state_by_boundary"]],
            [s["state_value"] for s in expected],
            "sensory state",
        )
    simulated = _lif_trace(drives[:-1], sources)
    _same(simulated.membrane_mv, result["dnp01_membrane_mv"], "batch membrane")
    population_response = {}
    for typ, values in population_drives.items():
        trace = _lif_trace(values[:-1], sources)
        if trace.spikes:
            raise DiagnosticCompositionError(
                "population decomposition unexpectedly spikes"
            )
        population_response[typ] = (trace.membrane_mv - lif.rest_mv).tolist()
    _same(
        np.array(population_response["LC4"]) + np.array(population_response["LPLC2"]),
        np.array(result["dnp01_membrane_mv"]) - lif.rest_mv,
        "population membrane additivity",
    )
    summaries = []
    for index, (target, side) in enumerate(((10001, "R"), (10010, "L"))):
        peak = max(
            range(len(time)), key=lambda n: result["dnp01_membrane_mv"][n][index]
        )
        v_peak = result["dnp01_membrane_mv"][peak][index]
        integrated = dt * sum(d[index] for d in drives[:-1])
        parts = {
            typ: dt * sum(d[index] for d in values[:-1])
            for typ, values in population_drives.items()
        }
        body_contributions = []
        for i, row in enumerate(rows):
            route = next(
                r for r in sources["routes"] if r.source_body_id == row["body_id"]
            )
            if route.target_body_id != target:
                continue
            contribution = [
                next(
                    c["model_drive_mveq"]
                    for c in ledger
                    if c["source_body_id"] == row["body_id"]
                )
                for ledger in ledgers
            ]
            if not any(contribution):
                continue
            body_contributions.append(
                {
                    "body_id": row["body_id"],
                    "neuron_type": row["neuron_type"],
                    "side": row["side"],
                    "exposure_by_boundary": [
                        e[i] for e in result["exposure_by_boundary"]
                    ],
                    "state_by_boundary": [
                        s[i] for s in result["sensory_state_by_boundary"]
                    ],
                    "available_drive_by_boundary_mV_eq": contribution,
                    "integrated_used_drive_mV_eq_ms": dt * sum(contribution[:-1]),
                }
            )
        body_contributions.sort(
            key=lambda r: (-r["integrated_used_drive_mV_eq_ms"], r["body_id"])
        )
        summaries.append(
            {
                "body_id": target,
                "side": side,
                "peak_step": peak,
                "peak_time_ms": time[peak],
                "peak_membrane_mV_eq": v_peak,
                "final_membrane_mV_eq": result["dnp01_membrane_mv"][-1][index],
                "threshold_mV_eq": lif.threshold_mv,
                "threshold_margin_at_peak_mV_eq": lif.threshold_mv - v_peak,
                "depolarization_from_rest_mV_eq": v_peak - lif.rest_mv,
                "fraction_of_rest_to_threshold_excursion": (v_peak - lif.rest_mv)
                / (lif.threshold_mv - lif.rest_mv),
                "spike_count": sum(
                    s["body_id"] == target for s in result["dnp01_spikes"]
                ),
                "peak_used_drive_mV_eq": max(d[index] for d in drives[:-1]),
                "integrated_used_drive_mV_eq_ms": integrated,
                "integrated_population_drive_mV_eq_ms": parts,
                "fraction_of_integrated_drive": {
                    typ: part / integrated if integrated else None
                    for typ, part in parts.items()
                },
                "population_depolarization_at_peak_mV_eq": {
                    typ: trace[peak][index]
                    for typ, trace in population_response.items()
                },
                "identity_contributions": body_contributions,
                "largest_contributing_body_ids": [
                    r["body_id"] for r in body_contributions[:5]
                ],
            }
        )
    return {
        "scenario_kind": result["scenario_kind"],
        "scenario_execution_id": result["scenario_execution_id"],
        "source_result_id": run["result_id"],
        "boundaries": boundaries,
        "lif_terms_by_interval": _integration_terms(result, sources),
        "population_depolarization_by_boundary_mV_eq": population_response,
        "targets": summaries,
        "source_statuses": copy.deepcopy(result["statuses"]),
    }


def _maximum_exposure(sources, model):
    """Reproduce the pre-existing Phase 13A bound, not a spike-seeking sweep."""
    values = integrate_exposure_values(
        [1.0] * 14,
        dt_ms=sources["lif"].dt_ms,
        tau_sens_ms=model["sensory_model"]["tau_sens_ms"],
        gain=model["sensory_model"]["gain"],
    )
    drives = []
    for state in values[:-1]:
        output, _ = _route_states(
            [state["state_value"]] * 311,
            sources["rows"],
            sources,
            model["transfer_model"]["k_transfer_mveq_per_state"],
        )
        drives.append([output[i] for i in (10001, 10010)])
    trace = _lif_trace(drives, sources)
    return {
        "classification": "AUDIT_EXISTING_PHASE13A_FULL_EXPOSURE_BOUND_ONLY",
        "exposure": "ALL_311_BODIES_BOTH_SIDES_HELD_AT_ONE_FOR_14_INTERVALS",
        "canonical_geometry": False,
        "parameters_and_timing": "UNCHANGED_CANONICAL_MODELS_14_INTERVALS_0_1_MS",
        "route_counts_R_L": [
            sum(r.target_body_id == target for r in sources["routes"])
            for target in (10001, 10010)
        ],
        "peak_membrane_mV_eq_R_L": trace.membrane_mv.max(axis=0).tolist(),
        "threshold_margin_mV_eq_R_L": (
            sources["lif"].threshold_mv - trace.membrane_mv.max(axis=0)
        ).tolist(),
        "spike_count": len(trace.spikes),
        "scope": "Model/horizon exposure bound, not biological maximum stimulation",
    }


def _recorded_exposure_envelope(battery, sources, model):
    """Bound, not a simulation/config: convex sensory filtering cannot exceed
    gain times its largest recorded per-body exposure from zero initial state.
    With no synaptic input, subthreshold LIF displacement cannot exceed the
    maximum nonnegative external drive. Scope is ONLY the recorded footprints.
    """
    result = battery["result"]["runs"][1]["result"]
    maxima = np.max(result["exposure_by_boundary"], axis=0)
    state_bounds = maxima * model["sensory_model"]["gain"]
    drive, _ = _route_states(
        state_bounds.tolist(),
        sources["rows"],
        sources,
        model["transfer_model"]["k_transfer_mveq_per_state"],
    )
    excursion = sources["lif"].threshold_mv - sources["lif"].rest_mv
    bounds = [drive[target] for target in (10001, 10010)]
    return {
        "classification": "ANALYTICAL_BOUND_NOT_ALTERNATE_SCENARIO",
        "scope": "Only histories bounded by each recorded per-body exposure maximum",
        "exposure_maximum_sum_R_L": [
            sum(
                maxima[i]
                for i, row in enumerate(sources["rows"])
                if row["side"] == side
            )
            for side in ("R", "L")
        ],
        "external_drive_upper_bound_mV_eq_R_L": bounds,
        "rest_to_threshold_excursion_mV_eq": excursion,
        "threshold_margin_lower_bound_mV_eq_R_L": [excursion - v for v in bounds],
        "bound_below_threshold_excursion_R_L": [v < excursion for v in bounds],
        "exclusion": "NOT_AN_EXTENDED_APPROACH_NEW_FOOTPRINT_OR_BIOLOGICAL_BOUND",
    }


def _analysis(battery, sources, model):
    runs = [_diagnose_run(run, sources, model) for run in battery["result"]["runs"]]
    baseline, looming = runs
    delta = []
    for b, stim in zip(baseline["boundaries"], looming["boundaries"], strict=True):
        delta.append(
            {
                "step": stim["step"],
                "time_ms": stim["time_ms"],
                "membrane_delta_mV_eq_R_L": [
                    lv - bv
                    for lv, bv in zip(
                        stim["membrane_mV_eq"], b["membrane_mV_eq"], strict=True
                    )
                ],
                "available_drive_delta_mV_eq_R_L": [
                    lv - bv
                    for lv, bv in zip(
                        stim["available_model_drive_mV_eq"],
                        b["available_model_drive_mV_eq"],
                        strict=True,
                    )
                ],
                "threshold_margin_delta_mV_eq_R_L": [
                    lv - bv
                    for lv, bv in zip(
                        stim["threshold_margin_mV_eq"],
                        b["threshold_margin_mV_eq"],
                        strict=True,
                    )
                ],
                "exposed_body_count_delta": stim["exposed_body_count"]
                - b["exposed_body_count"],
                "sensory_state_sum_delta_by_type_side": [
                    {
                        "neuron_type": lg["neuron_type"],
                        "side": lg["side"],
                        "delta": lg["state_sum"] - bg["state_sum"],
                    }
                    for lg, bg in zip(
                        stim["sensory_groups"], b["sensory_groups"], strict=True
                    )
                ],
            }
        )
    first = {}
    for label, key in (
        ("exposure", "exposed_body_count"),
        ("drive", "available_model_drive_mV_eq"),
        ("membrane", "membrane_mV_eq"),
    ):
        first[label] = next(
            (
                b["step"]
                for b in looming["boundaries"]
                if (
                    b[key] > 0
                    if label == "exposure"
                    else any(v > 0 for v in b[key])
                    if label == "drive"
                    else any(v > sources["lif"].rest_mv for v in b[key])
                )
            ),
            None,
        )
    duration = looming["boundaries"][-1]["time_ms"]
    full = _maximum_exposure(sources, model)
    return {
        "schema_version": RESULT_SCHEMA,
        "source_artifact_id": battery["artifact_id"],
        "model_parameters_snapshot_not_alternates": {
            "sensory": copy.deepcopy(model["sensory_model"]),
            "transfer": copy.deepcopy(model["transfer_model"]),
            "lif": sources["lif"].to_dict(),
            "coordinate_status": (
                "PINNED_MODEL_SPACE_PARAMETERS_NOT_DNP01_EMPIRICAL_CALIBRATION"
            ),
        },
        "runs": runs,
        "baseline_vs_looming_by_boundary": delta,
        "causal_latency": {
            "first_exposed_boundary": first["exposure"],
            "first_nonzero_drive_boundary": first["drive"],
            "first_depolarized_boundary": first["membrane"],
            "exposure_to_state_boundaries": 1,
            "exposure_to_membrane_boundaries": first["membrane"] - first["exposure"],
            "spike_stamp": (
                "IF_THRESHOLD_CROSSED_IN_INTERVAL_N_EVENT_IS_BOUNDARY_N_PLUS_1_"
                "AVAILABLE_TO_DOWNSTREAM_THERE"
            ),
            "no_additional_readout_edge_delay": (
                "EMPTY_READOUT_GRAPH_DELAY_MS_DOES_NOT_DELAY_EXTERNAL_DRIVE"
            ),
            "final_boundary_drive_not_consumed": True,
        },
        "temporal_window": {
            "duration_ms": duration,
            "interval_count": 14,
            "duration_over_tau_sens": duration / model["sensory_model"]["tau_sens_ms"],
            "duration_over_tau_m": duration / sources["lif"].tau_m_ms,
            "held_constant_drive_membrane_fraction": -math.expm1(
                -duration / sources["lif"].tau_m_ms
            ),
            "description": (
                "Short pinned-horizon accumulation, not a recommendation to extend it"
            ),
        },
        "maximum_exposure_audit": full,
        "recorded_exposure_envelope": _recorded_exposure_envelope(
            battery, sources, model
        ),
        "bottlenecks": [
            {
                "component": "WORLD_TO_COLUMN_PROJECTION",
                "classification": "MATERIAL_MODEL_LIMITER",
                "reason": (
                    "Sparse fractional recorded exposure materially limits drive "
                    "with pinned gain/k; full exposure also remains subthreshold "
                    "over the same horizon, so no dominant causal ranking "
                    "is established"
                ),
            },
            {
                "component": "SENSORY_STATE_DYNAMICS",
                "classification": "MATERIAL_MODEL_LIMITER",
                "reason": (
                    "Zero initial state and finite tau build drive over a short horizon"
                ),
            },
            {
                "component": "SENSORY_TO_DNP01_TRANSFER_MAGNITUDE",
                "classification": "NOT_IDENTIFIABLE_FROM_CURRENT_EVIDENCE",
                "reason": (
                    "Uncalibrated k sets magnitude; ranking cannot be isolated "
                    "from sensory normalization and threshold excursion"
                ),
            },
            {
                "component": "DNP01_MEMBRANE_DYNAMICS",
                "classification": "MATERIAL_MODEL_LIMITER",
                "reason": (
                    "tau_m=20 ms integrates a small held-drive fraction in 1.4 ms; "
                    "synaptic/reset/refractory terms are inactive"
                ),
            },
            {
                "component": "SCENARIO_TEMPORAL_WINDOW",
                "classification": "MATERIAL_MODEL_LIMITER",
                "reason": (
                    "Duration/tau_m=0.07; even the full-exposure bound stays "
                    "subthreshold at this horizon"
                ),
            },
            {
                "component": "DISCRETE_CAUSAL_LATENCY",
                "classification": "MATERIAL_MODEL_LIMITER",
                "reason": (
                    "Exposure at n changes membrane at n+2; initial zero drive and "
                    "terminal unconsumed state matter in 14 intervals"
                ),
            },
        ],
        "counterfactual_drive_factor": "NOT_COMPUTED_NO_SPIKE_TARGETING_NEEDED",
        "decision": DECISION,
        "future_review_target": (
            "SCENARIO_TEMPORAL_DESIGN_EVIDENCE_FOR_THE_1_4_MS_"
            "OBSERVATION_HORIZON_NO_ALTERNATE_VALUE"
        ),
        "scientific_limitations": list(LIMITATIONS),
    }


def build_diagnostic(source_path=DEFAULT_SOURCE):
    battery, sources, model = load_verified_inputs(source_path)
    config = {
        "schema_version": CONFIG_SCHEMA,
        "source_artifact_id": SOURCE_ID,
        "source_config_sha256": battery["config_sha256"],
        "source_result_sha256": battery["result_sha256"],
        "source_model_identity_sha256": canonical_sha256(sources["identity"]),
        "historical_references": dict(HISTORICAL_IDS),
        "analysis_semantics": {
            "threshold_margin": "THRESHOLD_MINUS_STORED_MEMBRANE",
            "baseline_comparison": "MATCHED_BOUNDARY_LOOMING_MINUS_BASELINE",
            "integration": "HELD_DRIVE_DT_SUM_OVER_14_OUTGOING_INTERVALS_ONLY",
            "terms": "DIFFERENCE_ACCOUNTING_USING_EXISTING_LIF_KERNEL",
            "identity_ranking": (
                "TOP_FIVE_INTEGRATED_USED_DRIVE_DESCENDING_BODY_ID_TIEBREAK"
            ),
            "maximum_exposure": "REPRODUCE_EXISTING_PHASE13A_BOUND_NOT_PARAMETER_SWEEP",
        },
        "scientific_exclusions": list(LIMITATIONS),
    }
    result = _analysis(battery, sources, model)
    ch, rh = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema_version": RESULT_SCHEMA,
        "config": config,
        "result": result,
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256([ARTIFACT_SCHEMA, ch, rh]),
    }


def validate_diagnostic(payload, source_path=DEFAULT_SOURCE):
    expected = build_diagnostic(source_path)
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError(
            "diagnostic state/semantics/identity differs from offline replay"
        )
    return expected
