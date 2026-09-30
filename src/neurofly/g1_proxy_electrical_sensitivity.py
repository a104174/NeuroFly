"""Phase 9C: bounded assumption sensitivity, not biological parameter estimation."""

from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path

from neurofly.g1_proxy_passive_electrical import (
    ARTIFACT_SCHEMA as MODEL_ARTIFACT_SCHEMA,
)
from neurofly.g1_proxy_passive_electrical import (
    FIXTURE_IDS,
    PassiveConfig,
    build_response,
    reference_config,
)
from neurofly.g1_proxy_passive_electrical_artifacts import replay_response_artifact
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_observation_mapping_artifacts import replay_ttm_g1_mapping_artifact
from neurofly.ttm_g1_proxy_mapping import DEFAULT_SOURCE_PATHS

EXPERIMENT_SCHEMA = "g1_proxy_passive_electrical_sensitivity_v1"
ARTIFACT_SCHEMA = "g1_proxy_passive_electrical_sensitivity_artifact_v1"
SOURCE_ID = "72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f"
DEFAULT_MODEL_ARTIFACT = DEFAULT_SOURCE_ROOT / MODEL_ARTIFACT_SCHEMA / SOURCE_ID
FACTORS = (0.5, 1.0, 2.0)
RETENTION_INTERVALS = 10
DECISIONS = {
    "sensitivity": "G1_ELECTRICAL_SENSITIVITY_VALIDATED",
    "structural_separability": (
        "EVENT_SCALE_AND_TAU_STRUCTURALLY_SEPARABLE_IN_FULL_TRAJECTORY"
    ),
    "empirical_identifiability": "BIOLOGICAL_PARAMETER_IDENTIFICATION_NOT_READY",
    "reference_config": "KEEP_REFERENCE_CONFIG_AS_EXPLORATORY_BASELINE",
    "next_phase": "PROCEED_TO_OBSERVATION_COMPATIBILITY_ASSESSMENT",
}
BOUNDARIES = (
    "EXPLORATORY_PARAMETER_SENSITIVITY_NO_EMPIRICAL_FITTING",
    "MODEL_INTERNAL_SEPARABILITY_NOT_BIOLOGICAL_IDENTIFIABILITY",
    "NO_BEST_CELL_NO_PARAMETER_SELECTION",
    "MODEL_DIAGNOSTICS_NOT_EMPIRICAL_OBSERVATION_OPERATORS",
    "SHARED_CONFIG_SYMMETRY_NOT_BILATERAL_PHYSIOLOGICAL_EVIDENCE",
    "NO_MODEL_EXTENSION_OR_UPSTREAM_CHANGE",
)


def _instances(response: dict) -> dict:
    return {
        (f["fixture_id"], i["source_body_id"]): i
        for f in response["result"]["fixtures"]
        for i in f["instances"]
    }


def _near(actual: float, expected: float) -> bool:
    # Floating-point equation-check allowance only, never empirical acceptance.
    return math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-14)


def analyze_cells(responses: list[dict]) -> dict:
    """Check executed trajectories; no simulator equation is implemented here."""
    if len(responses) != 9:
        raise ValueError("require exactly nine executed parameter cells")
    indexed = [_instances(r) for r in responses]
    for cell, rows in zip(responses, indexed, strict=True):
        model = cell["config"]["model"]
        q, tau, dt = (
            model["event_scale_effective_mV_eq"],
            model["tau_effective_ms"],
            model["dt_ms"],
        )
        alpha = math.exp(-dt / tau)  # Expected closed form, not a simulator.
        for (fixture, body), row in rows.items():
            u = row["voltage_deviation_mV_eq"]
            if sum(row["token_count"]) == 0:
                if u != [0.0] * 81 or row["proxy_voltage_mV_eq"] != [0.0] * 81:
                    raise ValueError("zero/inactive instance changed")
                continue
            events = [n for n, count in enumerate(row["token_count"]) if count]
            if any(
                not _near(v, sum(q * alpha ** (n - e) for e in events if n >= e))
                for n, v in enumerate(u)
            ):
                raise ValueError("closed-form/superposition behavior unexpected")
            if u[10] != q:
                raise ValueError("isolated immediate response is not event scale")
            if len(events) == 1 and not all(
                a > b > 0 for a, b in zip(u[10:-1], u[11:], strict=True)
            ):
                raise ValueError("single-event passive decay unexpected")
            if len(events) == 2 and not _near(u[30] / q, 1 + alpha**20):
                raise ValueError("repeated residual behavior unexpected")
        if (
            rows[("RIGHT_SINGLE_EVENT", 800146)]["voltage_deviation_mV_eq"]
            != rows[("LEFT_SINGLE_EVENT", 804642)]["voltage_deviation_mV_eq"]
        ):
            raise ValueError("shared-config model symmetry changed")
        for body in (800146, 804642):
            single = rows[
                ("RIGHT_SINGLE_EVENT" if body == 800146 else "LEFT_SINGLE_EVENT", body)
            ]
            bilateral = rows[("BILATERAL_SIMULTANEOUS_EVENT", body)]
            if (
                single["voltage_deviation_mV_eq"]
                != bilateral["voltage_deviation_mV_eq"]
            ):
                raise ValueError("bilateral isolation changed")
    for tau_index in range(3):
        reference_rows = indexed[tau_index * 3 + 1]
        for scale_index, factor in enumerate(FACTORS):
            rows = indexed[tau_index * 3 + scale_index]
            for key, row in rows.items():
                u = row["voltage_deviation_mV_eq"]
                reference_u = reference_rows[key]["voltage_deviation_mV_eq"]
                if u != [factor * v for v in reference_u]:
                    raise ValueError("exact binary scale linearity failed")
                q = responses[tau_index * 3 + scale_index]["config"]["model"][
                    "event_scale_effective_mV_eq"
                ]
                if [v / q for v in u] != [v / 2.0 for v in reference_u]:
                    raise ValueError("normalized scale invariance failed")
    for scale_index in range(3):
        rows = [indexed[t * 3 + scale_index] for t in range(3)]
        traces = [
            r[("RIGHT_SINGLE_EVENT", 800146)]["voltage_deviation_mV_eq"] for r in rows
        ]
        if not all(traces[0][n] < traces[1][n] < traces[2][n] for n in range(11, 81)):
            raise ValueError("tau retention monotonicity failed")
        peaks = [
            r[("RIGHT_REPEATED_EVENTS", 800146)]["voltage_deviation_mV_eq"][30]
            for r in rows
        ]
        if not peaks[0] < peaks[1] < peaks[2]:
            raise ValueError("tau repeated residual monotonicity failed")
    return {
        "scale_linearity": "EXACT_FOR_BINARY_RELATIVE_FACTORS",
        "normalized_scale_invariance": "EXACT_FOR_CANONICAL_GRID",
        "tau_retention": "STRICTLY_INCREASING_WITH_TAU_AFTER_SINGLE_INPUT",
        "single_peak": "EVENT_SCALE_ONLY_TAU_INDEPENDENT",
        "closed_form_and_superposition": "PASSED_NUMERICAL_EQUATION_CHECK",
        "repeated_peak_ratio": "TAU_DEPENDENT_SCALE_INDEPENDENT",
        "zero_and_inactive_instances": "EXACT_BASELINE",
        "bilateral_independence": "PRESERVED",
        "scalar_summary_degeneracy": "LATE_SAMPLE_CONFOUNDS_SCALE_AND_TAU",
        "biological_event_scale": "NOT_BIOLOGICALLY_IDENTIFIABLE_CURRENTLY",
        "biological_tau": "NOT_BIOLOGICALLY_IDENTIFIABLE_CURRENTLY",
        **DECISIONS,
    }


def build_sensitivity(*, model_artifact: str | Path = DEFAULT_MODEL_ARTIFACT) -> dict:
    source = replay_response_artifact(model_artifact)
    if (
        source["artifact_id"] != SOURCE_ID
        or source["config"]["model"] != reference_config().payload()
    ):
        raise ValueError("canonical Phase 9B source identity/config changed")
    u = replay_ttm_g1_mapping_artifact(DEFAULT_SOURCE_PATHS["phase8u"])
    if u.contract["result"]["formal_ready_mapping_count"] != 0:
        raise ValueError("Phase 8U readiness changed")
    base = PassiveConfig.from_payload(source["config"]["model"])
    config = {
        "schema_version": EXPERIMENT_SCHEMA,
        "source_phase9b": {
            key: source[key]
            for key in ("artifact_id", "config_sha256", "result_sha256")
        },
        "source_phase8u": {
            "artifact_id": u.artifact_id,
            "formal_ready_mapping_count": 0,
        },
        "model": base.payload(),
        "sources": source["config"]["sources"],
        "tau_factors": list(FACTORS),
        "event_scale_factors": list(FACTORS),
        "ordering": "TAU_FACTOR_ASCENDING_THEN_EVENT_SCALE_FACTOR_ASCENDING",
        "fixture_ids": list(FIXTURE_IDS),
        "retention_diagnostic": {
            "fixture_kind": "SINGLE_EVENT",
            "event_step": 10,
            "sample_step": 20,
            "interval_count": RETENTION_INTERVALS,
            "delta_ms": RETENTION_INTERVALS * base.dt_ms,
        },
        "repeated_diagnostic": {"first_step": 10, "second_step": 30, "delta_ms": 2.0},
        "numerical_check_semantics": "FLOAT_ROUNDOFF_ALLOWANCE_NOT_EMPIRICAL_TOLERANCE",
        "scientific_boundary": list(BOUNDARIES),
    }
    cells, responses = [], []
    source_rows = _instances(source)
    for tau_factor in FACTORS:
        for scale_factor in FACTORS:
            model = replace(
                base,
                tau_effective_ms=base.tau_effective_ms * tau_factor,
                event_scale_effective_mV_eq=base.event_scale_effective_mV_eq
                * scale_factor,
            )
            response = build_response(model)  # Sole authoritative Phase 9B simulator.
            responses.append(response)
            identity = {
                "schema_version": EXPERIMENT_SCHEMA,
                "source_model_artifact_id": SOURCE_ID,
                "model_config": model.payload(),
                "tau_factor": tau_factor,
                "event_scale_factor": scale_factor,
            }
            summaries = []
            for (fixture, body), row in _instances(response).items():
                original = source_rows[(fixture, body)]
                if (
                    row["source_token_ids"] != original["source_token_ids"]
                    or row["token_count"] != original["token_count"]
                ):
                    raise ValueError("source schedule changed across parameter cells")
                values = row["voltage_deviation_mV_eq"]
                count = row["summary"]["input_token_count"]
                summaries.append(
                    {
                        "fixture_id": fixture,
                        "source_body_id": body,
                        "source_side": row["source_side"],
                        "source_token_ids": row["source_token_ids"],
                        **row["summary"],
                        "peak_time_ms": response["result"]["time_ms"][
                            row["summary"]["peak_boundary"]
                        ],
                        "single_retention_fraction_after_1ms": values[20] / values[10]
                        if count == 1
                        else None,
                        "repeated_second_peak_mV_eq": values[30]
                        if count == 2
                        else None,
                        "repeated_second_peak_ratio": values[30]
                        / model.event_scale_effective_mV_eq
                        if count == 2
                        else None,
                    }
                )
            cells.append(
                {
                    **identity,
                    "cell_id": canonical_sha256(identity),
                    "is_reference_cell": tau_factor == scale_factor == 1.0,
                    "response_artifact_id": response["artifact_id"],
                    "response_config_sha256": response["config_sha256"],
                    "response_result_sha256": response["result_sha256"],
                    "summaries": summaries,
                }
            )
    if cells[4]["response_artifact_id"] != SOURCE_ID:
        raise ValueError("reference cell no longer reproduces Phase 9B")
    result = {
        "cells": cells,
        "cell_count": 9,
        "fixture_run_count": 54,
        "trajectory_count": 108,
        "source_tokens_per_cell": 8,
        "analysis": analyze_cells(responses),
    }
    ch, rh = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema_version": EXPERIMENT_SCHEMA,
        "config": config,
        "result": result,
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256([ARTIFACT_SCHEMA, ch, rh]),
    }


def validate_sensitivity(
    payload: dict, *, model_artifact=DEFAULT_MODEL_ARTIFACT
) -> dict:
    expected = build_sensitivity(model_artifact=model_artifact)
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError(
            "sensitivity metadata/results differ from exact offline reconstruction"
        )
    return expected
