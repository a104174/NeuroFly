"""Phase 9E: one model-space operator, not an empirical voltage observation."""

from __future__ import annotations

import copy
import math
from pathlib import Path

from neurofly.g1_proxy_passive_electrical import (
    ARTIFACT_SCHEMA as SOURCE_ARTIFACT_SCHEMA,
)
from neurofly.g1_proxy_passive_electrical import (
    MODEL_SCHEMA,
    PROXY_DOMAIN_ID,
    PassiveConfig,
)
from neurofly.g1_proxy_passive_electrical import (
    PROVENANCE as MODEL_PROVENANCE,
)
from neurofly.g1_proxy_passive_electrical import (
    RESULT_SCHEMA as SOURCE_RESULT_SCHEMA,
)
from neurofly.g1_proxy_passive_electrical_artifacts import replay_response_artifact
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

OPERATOR_SCHEMA = "g1_proxy_model_space_peak_deflection_operator_v1"
RESULT_SCHEMA = "g1_proxy_model_space_observation_result_v1"
ARTIFACT_SCHEMA = "g1_proxy_model_space_peak_deflection_artifact_v1"
PROVENANCE = "EXPLORATORY_MODEL_SPACE_OBSERVATION"
SOURCE_ID = "72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f"
DEFAULT_SOURCE_ARTIFACT = DEFAULT_SOURCE_ROOT / SOURCE_ARTIFACT_SCHEMA / SOURCE_ID
SUPPORTED_FIXTURES = (
    "ZERO_EVENT_CONTROL",
    "RIGHT_SINGLE_EVENT",
    "LEFT_SINGLE_EVENT",
    "BILATERAL_SIMULTANEOUS_EVENT",
)
EXCLUDED_FIXTURES = ("RIGHT_REPEATED_EVENTS", "LEFT_REPEATED_EVENTS")
PEAK_KIND = "ISOLATED_EVENT_PEAK_DEFLECTION"
CONTROL_KIND = "NO_EVENT_BASELINE_CONTROL"
BOUNDARIES = (
    "MODEL_SPACE_ONLY_MV_EQ_NOT_BIOLOGICAL_MV",
    "NO_PHYSICAL_UNIT_CONVERSION_OR_CALIBRATION",
    "NO_EMPIRICAL_COMPARISON_OR_TARGET",
    "MODEL_BEHAVIOR_FIXTURES_NOT_EXPERIMENTAL_PROTOCOLS",
    "PROTOCOL_MATCH_NOT_EVALUATED",
    "NO_REPEATED_MINIATURE_QUANTAL_OR_LATENCY_OPERATOR",
    "VIRTUAL_G1_DOMAIN_NOT_PHYSICAL_FIBER_OR_WHOLE_TTM",
)


def operator_config() -> dict:
    return {
        "schema_version": OPERATOR_SCHEMA,
        "source_model_schema": MODEL_SCHEMA,
        "unit_semantics": "UNCALIBRATED_MODEL_SPACE_MV_EQ",
        "baseline_semantics": "IMMEDIATE_PRE_EVENT_BOUNDARY_BASELINE",
        "control_baseline_semantics": "MODEL_REFERENCE_INITIAL_BOUNDARY",
        "window_semantics": "EVENT_BOUNDARY_THROUGH_TRAJECTORY_END_INCLUSIVE",
        "deflection_semantics": (
            "MAX_PROXY_VOLTAGE_MINUS_PRE_EVENT_BASELINE_NOT_ABSOLUTE"
        ),
        "peak_tie_policy": "EARLIEST_STORED_BOUNDARY",
        "supported_token_counts": [0, 1],
        "boundary_zero_policy": "REJECT_ISOLATED_EVENT_WITHOUT_PRE_EVENT_BOUNDARY",
        "protocol_match_status": "NOT_EVALUATED",
        "scientific_boundary": list(BOUNDARIES),
    }


def _validated_envelope(source: dict) -> PassiveConfig:
    """Integrity/shape checks only; this helper never simulates dynamics."""
    try:
        model = PassiveConfig.from_payload(source["config"]["model"])
        ch, rh = canonical_sha256(source["config"]), canonical_sha256(source["result"])
        if (
            source["schema_version"] != SOURCE_RESULT_SCHEMA
            or source["result"]["schema_version"] != SOURCE_RESULT_SCHEMA
            or source["config"]["provenance_kind"] != MODEL_PROVENANCE
            or source["config_sha256"] != ch
            or source["result_sha256"] != rh
            or source["artifact_id"]
            != canonical_sha256([SOURCE_ARTIFACT_SCHEMA, ch, rh])
        ):
            raise ValueError("source envelope/schema/hash mismatch")
        grid = source["result"]["boundary_indices"]
        times = source["result"]["time_ms"]
        if (
            grid != list(range(model.interval_count + 1))
            or any(type(step) is not int for step in grid)
            or len(times) != len(grid)
            or any(
                type(t) not in (int, float)
                or not math.isfinite(t)
                or t != n * model.dt_ms
                for n, t in enumerate(times)
            )
        ):
            raise ValueError("invalid source time grid")
        return model
    except (KeyError, TypeError) as exc:
        raise ValueError("malformed source trajectory envelope") from exc


def extract_trajectory(
    source: dict, fixture_id: str, body_id: int, *, result_kind: str | None = None
) -> dict:
    """Observe a validated Phase 9B response; never integrate or fit a trajectory.

    Production artifact extraction first calls Phase 9B offline replay. This
    pure extraction primitive also accepts integrity-valid test-local Phase 9B
    responses for coordinate/scale regression tests, without publishing them as
    canonical source evidence.
    """
    model = _validated_envelope(source)
    if fixture_id not in SUPPORTED_FIXTURES:
        raise ValueError("unsupported fixture: repeated-event fixtures are excluded")
    if type(body_id) is not int:
        raise ValueError("invalid source body identity")
    try:
        fixtures = [
            f for f in source["result"]["fixtures"] if f["fixture_id"] == fixture_id
        ]
        instances = [
            i
            for f in fixtures
            for i in f["instances"]
            if i["source_body_id"] == body_id
        ]
    except (KeyError, TypeError) as exc:
        raise ValueError("malformed source fixture/trajectory identity") from exc
    if len(fixtures) != 1:
        raise ValueError("missing/duplicate source fixture")
    if len(instances) != 1:
        raise ValueError("missing/duplicate source trajectory")
    row = instances[0]
    try:
        if (
            (row["source_body_id"], row["source_side"])
            not in ((800146, "R"), (804642, "L"))
            or row["proxy_domain_id"] != model.proxy_domain_id
            or row["proxy_domain_id"] != PROXY_DOMAIN_ID
            or row["config_id"] != source["config_sha256"]
            or row["instance_id"]
            != canonical_sha256([fixture_id, body_id, source["config_sha256"]])
            or row["provenance_chain"][-1] != MODEL_PROVENANCE
        ):
            raise ValueError("source causal/domain/model identity mismatch")
        counts, values, deviations = (
            row["token_count"],
            row["proxy_voltage_mV_eq"],
            row["voltage_deviation_mV_eq"],
        )
        length = model.interval_count + 1
        if (
            any(len(array) != length for array in (counts, values, deviations))
            or any(type(n) is not int or n < 0 for n in counts)
            or any(
                type(v) not in (int, float) or not math.isfinite(v)
                for v in [*values, *deviations]
            )
            or any(
                v != model.reference_voltage_mV_eq + u
                for v, u in zip(values, deviations, strict=True)
            )
        ):
            raise ValueError("malformed/nonfinite source trajectory")
        tokens = row["source_token_ids"]
        count = sum(counts)
        if (
            count not in (0, 1)
            or len(tokens) != count
            or any(not isinstance(t, str) or not t for t in tokens)
        ):
            raise ValueError("require zero or exactly one source token")
        kind = PEAK_KIND if count else CONTROL_KIND
        if result_kind is not None and result_kind != kind:
            raise ValueError("result kind does not match source token count")
        config = operator_config()
        common = {
            "schema_version": RESULT_SCHEMA,
            "result_kind": kind,
            "operator_id": canonical_sha256(config),
            "provenance_kind": PROVENANCE,
            "parent_provenance_kind": MODEL_PROVENANCE,
            "provenance_chain": [*row["provenance_chain"], PROVENANCE],
            "source_phase9b_artifact_id": source["artifact_id"],
            "source_phase8w_artifact_id": source["config"]["sources"]["phase8w"][
                "artifact_id"
            ],
            "source_fixture_id": fixture_id,
            "source_trajectory_id": row["instance_id"],
            "source_trajectory_sha256": canonical_sha256(row),
            "source_body_id": body_id,
            "neural_side": row["source_side"],
            "proxy_domain_id": row["proxy_domain_id"],
            "unit_semantics": config["unit_semantics"],
            "units": "mV_eq",
            "protocol_match_status": "NOT_EVALUATED",
            "scientific_boundary": list(BOUNDARIES),
        }
        times = source["result"]["time_ms"]
        if not count:
            baseline = model.reference_voltage_mV_eq
            if values[0] != baseline:
                raise ValueError(
                    "zero control initial baseline differs from model reference"
                )
            common.update(
                baseline_semantics=config["control_baseline_semantics"],
                baseline_step=0,
                baseline_time_ms=times[0],
                baseline_proxy_voltage_mV_eq=baseline,
                max_abs_deviation_mV_eq=max(abs(v - baseline) for v in values),
                baseline_stable=all(v == baseline for v in values),
            )
        else:
            event = next(n for n, c in enumerate(counts) if c)
            if event == 0:
                raise ValueError("event at zero has no immediate pre-event baseline")
            baseline, peak = values[event - 1], max(values[event:])
            peak_step = next(n for n in range(event, length) if values[n] == peak)
            deflection = peak - baseline
            if not math.isfinite(deflection) or deflection <= 0:
                raise ValueError("unsupported nonpositive/nonfinite model deflection")
            common.update(
                source_phase8w_token_id=tokens[0],
                event_step=event,
                event_time_ms=times[event],
                baseline_semantics=config["baseline_semantics"],
                baseline_step=event - 1,
                baseline_time_ms=times[event - 1],
                baseline_proxy_voltage_mV_eq=baseline,
                window_semantics=config["window_semantics"],
                window_start_step=event,
                window_end_step=length - 1,
                window_start_time_ms=times[event],
                window_end_time_ms=times[-1],
                peak_proxy_voltage_mV_eq=peak,
                peak_deflection_mV_eq=deflection,
                peak_step=peak_step,
                peak_time_ms=times[peak_step],
            )
        common["result_id"] = canonical_sha256(common)
        return common
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError("malformed source trajectory") from exc


def build_observations(
    *, source_artifact: str | Path = DEFAULT_SOURCE_ARTIFACT
) -> dict:
    source = replay_response_artifact(source_artifact)
    if source["artifact_id"] != SOURCE_ID:
        raise ValueError("require exact canonical Phase 9B source artifact")
    operator = operator_config()
    config = {
        "operator": operator,
        "operator_id": canonical_sha256(operator),
        "source_phase9b": {
            key: source[key]
            for key in (
                "artifact_id",
                "schema_version",
                "config_sha256",
                "result_sha256",
            )
        },
        "supported_fixtures": list(SUPPORTED_FIXTURES),
        "ordering": "SOURCE_FIXTURE_ORDER_THEN_SOURCE_BODY_ORDER",
        "scientific_boundary": list(BOUNDARIES),
    }
    records = [
        extract_trajectory(source, f["fixture_id"], row["source_body_id"])
        for f in source["result"]["fixtures"]
        if f["fixture_id"] in SUPPORTED_FIXTURES
        for row in f["instances"]
    ]
    result = {
        "schema_version": RESULT_SCHEMA,
        "records": records,
        "isolated_event_result_count": sum(
            r["result_kind"] == PEAK_KIND for r in records
        ),
        "baseline_control_result_count": sum(
            r["result_kind"] == CONTROL_KIND for r in records
        ),
        "excluded_fixtures": [
            {
                "fixture_id": f,
                "reason": (
                    "V1_EXCLUDES_REPEATED_EVENT_FIXTURE_AND_ITS_INACTIVE_TRAJECTORY"
                ),
            }
            for f in EXCLUDED_FIXTURES
        ],
    }
    ch, rh = canonical_sha256(config), canonical_sha256(result)
    return {
        "config": config,
        "result": result,
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256([ARTIFACT_SCHEMA, ch, rh]),
    }


def validate_observations(
    payload: dict, *, source_artifact=DEFAULT_SOURCE_ARTIFACT
) -> dict:
    expected = build_observations(source_artifact=source_artifact)
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError(
            "observation source/semantics/results differ from offline extraction"
        )
    return copy.deepcopy(expected)
