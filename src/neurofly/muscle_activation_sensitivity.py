"""Phase 10C: activation assumption sensitivity, not calibration or mechanics."""

from __future__ import annotations

import math

from neurofly.g1_proxy_passive_electrical import FIXTURE_IDS
from neurofly.g1_proxy_passive_electrical_artifacts import replay_response_artifact
from neurofly.muscle_activation import (
    DEFAULT_MODEL_ARTIFACT,
    ActivationConfig,
    reference_config,
    transform_response,
)
from neurofly.muscle_activation import (
    SOURCE_ID as ELECTRICAL_SOURCE_ID,
)
from neurofly.muscle_activation_artifacts import (
    DEFAULT_ARTIFACT_ROOT as ACTIVATION_ROOT,
)
from neurofly.muscle_activation_artifacts import (
    replay_activation_artifact,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

EXPERIMENT_SCHEMA = "static_normalized_muscle_activation_sensitivity_v1"
ARTIFACT_SCHEMA = "static_normalized_muscle_activation_sensitivity_artifact_v1"
SOURCE_ID = "4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb"
DEFAULT_ACTIVATION_ARTIFACT = ACTIVATION_ROOT / SOURCE_ID
SCALES = (5.0, 10.0, 20.0)
DECISIONS = {
    "sensitivity": "ACTIVATION_SCALE_SENSITIVITY_VALIDATED",
    "mechanics_interface": (
        "FULL_ACTIVATION_TRAJECTORY_READY_AS_EXPLORATORY_MECHANICS_INPUT"
    ),
    "clipping": "CANONICAL_ACTIVATION_REMAINS_UNCLIPPED",
    "information_preservation": (
        "TEMPORAL_SHAPE_PRESERVED_IN_CANONICAL_UNCLIPPED_REGIME"
    ),
    "parameter_confound": (
        "ACTIVATION_SCALE_EXPLICITLY_CONFOUNDED_WITH_UPSTREAM_AND_FUTURE_GAINS"
    ),
    "phase10_completion": "PHASE10_ACTIVATION_LAYER_COMPLETE",
    "next_phase": "PHASE11_ASSESS_FIRST_CONTRACTION_FORCE_MODEL",
}
BOUNDARIES = (
    "EXPLORATORY_MODEL_SENSITIVITY_NO_BIOLOGICAL_RANKING_OR_FITTING",
    "FIXED_PERSISTED_ELECTRICAL_INPUT_NO_MODEL_EXTENSION",
    "FULL_TRAJECTORY_INTERFACE_NOT_PHYSICAL_ACTUATOR_MAPPING",
    "NO_FORCE_CONTRACTION_OR_BODY_MECHANICS_IMPLEMENTATION",
    "MODEL_NORMALIZATION_CEILING_NOT_MAXIMUM_PHYSIOLOGICAL_OUTPUT",
)


def _rows(response: dict) -> dict:
    return {
        (f["fixture_id"], i["source_body_id"]): i
        for f in response["result"]["fixtures"]
        for i in f["instances"]
    }


def _near(a: float, b: float) -> bool:
    # Arithmetic roundoff only; never an empirical tolerance.
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-14)


def analyze_responses(source: dict, responses: list[dict]) -> dict:
    """Check executed outputs; this function does not implement activation."""
    if len(responses) != len(SCALES):
        raise ValueError("require exactly three activation cells")
    original = _rows(source)
    expected_keys = [(f, b) for f in FIXTURE_IDS for b in (800146, 804642)]
    indexed = []
    for scale, response in zip(SCALES, responses, strict=True):
        if (
            response["config"]["model"] != ActivationConfig(scale).payload()
            or response["result"]["time_ms"] != source["result"]["time_ms"]
            or response["result"]["boundary_indices"]
            != source["result"]["boundary_indices"]
            or response["result"]["trajectory_count"] != 12
            or response["result"]["sample_count"] != 972
        ):
            raise ValueError("activation cell config/grid/accounting changed")
        rows = _rows(response)
        if list(rows) != expected_keys:
            raise ValueError("activation fixture/causal identity set/order changed")
        indexed.append(rows)
        for key, row in rows.items():
            parent = original[key]
            values = row["activation_proxy"]
            driver = row["voltage_deviation_mV_eq"]
            if (
                driver != parent["voltage_deviation_mV_eq"]
                or row["source_trajectory_id"] != parent["instance_id"]
                or row["source_side"] != parent["source_side"]
                or row["proxy_domain_id"] != parent["proxy_domain_id"]
                or len(values) != 81
                or any(not math.isfinite(a) or not 0 <= a <= 1 for a in values)
            ):
                raise ValueError("electrical source/activation samples changed")
            if any(u >= scale for u in driver):
                raise ValueError("canonical clipping behavior unexpectedly changed")
            if any(
                not _near(a * scale, max(0, u))
                for a, u in zip(values, driver, strict=True)
            ):
                raise ValueError("normalized reconstruction failed")
            if all(u == 0 for u in driver) and values != [0.0] * 81:
                raise ValueError("zero invariance failed")
            if row["summary"]["peak_step"] != parent["summary"]["peak_boundary"]:
                raise ValueError("unclipped timing changed")
        for body in (800146, 804642):
            single = "RIGHT_SINGLE_EVENT" if body == 800146 else "LEFT_SINGLE_EVENT"
            if (
                rows[(single, body)]["activation_proxy"]
                != rows[("BILATERAL_SIMULTANEOUS_EVENT", body)]["activation_proxy"]
            ):
                raise ValueError("bilateral independence failed")
    for key in expected_keys:
        arrays = [r[key]["activation_proxy"] for r in indexed]
        if any(
            not _near(a, 2 * b) or not _near(b, 2 * c)
            for a, b, c in zip(*arrays, strict=True)
        ):
            raise ValueError("inverse-scale behavior failed")
    return {
        "inverse_scale": "VERIFIED_ALL_CANONICAL_SAMPLES",
        "normalized_reconstruction": (
            "VERIFIED_POSITIVE_DRIVER_WITH_ARITHMETIC_ROUNDOFF"
        ),
        "zero_invariance": "EXACT",
        "bilateral_independence": "PRESERVED",
        "timing": "UNCHANGED_FULL_GRID_AND_PEAK_BOUNDARIES",
        "canonical_regime": "CANONICAL_FIXTURES_REMAIN_IN_UNCLIPPED_LINEAR_REGIME",
        "rectification_information_loss": "NEGATIVE_SIGN_AND_MAGNITUDE_DISCARDED",
        "ceiling_information_loss": (
            "ABOVE_SCALE_AMPLITUDES_INDISTINGUISHABLE_NOT_OBSERVED_CANONICALLY"
        ),
        **DECISIONS,
    }


def build_sensitivity(
    *,
    activation_artifact=DEFAULT_ACTIVATION_ARTIFACT,
    electrical_artifact=DEFAULT_MODEL_ARTIFACT,
) -> dict:
    baseline = replay_activation_artifact(
        activation_artifact, source_artifact=electrical_artifact
    )
    if (
        baseline["artifact_id"] != SOURCE_ID
        or baseline["config"]["model"] != reference_config().payload()
    ):
        raise ValueError("canonical Phase 10B source changed")
    source = replay_response_artifact(electrical_artifact)
    if source["artifact_id"] != ELECTRICAL_SOURCE_ID:
        raise ValueError("canonical electrical source changed")
    config = {
        "schema_version": EXPERIMENT_SCHEMA,
        "source_phase10b": {
            k: baseline[k] for k in ("artifact_id", "config_sha256", "result_sha256")
        },
        "source_phase9b": {
            k: source[k] for k in ("artifact_id", "config_sha256", "result_sha256")
        },
        "reference_model": reference_config().payload(),
        "activation_scales_mV_eq": list(SCALES),
        "relative_factors": [0.5, 1.0, 2.0],
        "fixture_ids": list(FIXTURE_IDS),
        "cell_order": "ACTIVATION_SCALE_ASCENDING",
        "numerical_check_semantics": "ARITHMETIC_ROUNDOFF_NOT_EMPIRICAL_TOLERANCE",
        "ceiling_count_semantics": "AT_OR_ABOVE_SCALE_INCLUDES_EXACT_CEILING",
        "scientific_boundary": list(BOUNDARIES),
    }
    cells, responses = [], []
    for scale in SCALES:
        model = ActivationConfig(scale)
        response = transform_response(
            source, model
        )  # The unchanged Phase 10B authority.
        responses.append(response)
        identity = {
            "schema_version": EXPERIMENT_SCHEMA,
            "source_phase10b_artifact_id": SOURCE_ID,
            "source_phase9b_artifact_id": source["artifact_id"],
            "model_config": model.payload(),
        }
        summaries = [
            {
                "fixture_id": fixture,
                "source_body_id": body,
                "source_side": row["source_side"],
                "proxy_domain_id": row["proxy_domain_id"],
                "source_trajectory_id": row["source_trajectory_id"],
                "activation_trajectory_id": row["trajectory_id"],
                **row["summary"],
            }
            for (fixture, body), row in _rows(response).items()
        ]
        count = sum(s["ceiling_sample_count"] for s in summaries)
        loss = sum(
            u > scale
            for row in _rows(source).values()
            for u in row["voltage_deviation_mV_eq"]
        )
        cells.append(
            {
                **identity,
                "cell_id": canonical_sha256(identity),
                "is_reference_cell": scale == reference_config().activation_scale_mV_eq,
                "activation_artifact_id": response["artifact_id"],
                "activation_config_sha256": response["config_sha256"],
                "activation_result_sha256": response["result_sha256"],
                "summaries": summaries,
                "diagnostics": {
                    "maximum_activation_proxy": max(
                        s["peak_activation_proxy"] for s in summaries
                    ),
                    "maximum_unclipped_ratio": max(
                        s["source_peak_deviation_mV_eq"] for s in summaries
                    )
                    / scale,
                    "clipped_sample_count": count,
                    "clipped_trajectory_count": sum(
                        s["ceiling_sample_count"] > 0 for s in summaries
                    ),
                    "above_ceiling_information_loss_sample_count": loss,
                    "ceiling_information_loss_occurs": loss > 0,
                },
            }
        )
    if canonical_json_bytes(responses[1]) != canonical_json_bytes(baseline):
        raise ValueError("reference cell no longer reproduces Phase 10B")
    result = {
        "cells": cells,
        "cell_count": 3,
        "fixture_run_count": 18,
        "trajectory_count": 36,
        "sample_count": 2916,
        "reference_cell_id": cells[1]["cell_id"],
        "analysis": analyze_responses(source, responses),
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


def validate_sensitivity(payload: dict, **sources) -> dict:
    expected = build_sensitivity(**sources)
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError(
            "activation sensitivity differs from exact offline reconstruction"
        )
    return expected
