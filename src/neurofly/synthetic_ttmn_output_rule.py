"""Phase 8N: derive exploratory TTMn output records from Phase 6C state crossings.

This module is an output operator over the immutable Phase 8B trajectories. It
does not change or rerun the Phase 6C equation and does not model biological
TTMn action potentials.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

from neurofly.motor_pathway import MOTOR_PATHWAY_EVIDENCE, TTMnIntegratorConfig
from neurofly.synthetic_motor_interface import (
    FIXTURE_IDS,
    SYNTHETIC_SOURCE_KIND,
)
from neurofly.synthetic_motor_interface import (
    validate_and_replay_payload as validate_phase8b_payload,
)
from neurofly.synthetic_motor_interface_artifacts import LoadedSyntheticMotorArtifact

CONFIG_SCHEMA_VERSION = "synthetic_ttmn_output_rule_config_v1"
RESULT_SCHEMA_VERSION = "synthetic_ttmn_output_rule_result_v1"
ARTIFACT_SCHEMA_VERSION = "synthetic_ttmn_output_rule_artifact_v1"
GENERATOR_CONFIG_SCHEMA_VERSION = "ttmn_threshold_crossing_generator_config_v1"
OUTPUT_EVENT_SCHEMA_VERSION = "motor_neuron_output_event_v1"
GENERATOR_KIND = "TTMN_THRESHOLD_CROSSING_V1"
OUTPUT_EVENT_PROVENANCE = "EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT"
REFERENCE_THRESHOLD_DIMENSIONLESS = 0.25
SENSITIVITY_THRESHOLDS = (0.20, 0.25, 0.30, 0.50)
EXPECTED_PHASE8B_ARTIFACT_ID = (
    "4321adeee0412a79632ce4e008a1b8eaad22ee167f97f4a98521a9e71d9ef936"
)
_TTMN_BY_BODY_ID = {
    identity["body_id"]: identity for identity in MOTOR_PATHWAY_EVIDENCE.ttmn_identities
}


class TTMnOutputRuleError(ValueError):
    """Invalid source trajectory, threshold config, event, or replay payload."""


def canonical_sha256(value: Any) -> str:
    """Hash deterministic JSON using the repository's content identity pattern."""

    try:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise TTMnOutputRuleError("value is not deterministic JSON") from exc
    return hashlib.sha256(payload).hexdigest()


def _validated_threshold(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TTMnOutputRuleError("dimensionless threshold must be finite and positive")
    threshold = float(value)
    if not math.isfinite(threshold) or threshold <= 0.0:
        raise TTMnOutputRuleError("dimensionless threshold must be finite and positive")
    return threshold


def _phase6c_model_config(source: LoadedSyntheticMotorArtifact) -> dict[str, Any]:
    model = dict(source.config["motor_model"])
    if model != TTMnIntegratorConfig().to_dict():
        raise TTMnOutputRuleError("Phase 8B source uses an altered Phase 6C config")
    return model


def build_generator_config(
    source: LoadedSyntheticMotorArtifact, threshold_dimensionless: Any
) -> dict[str, Any]:
    """Build an explicit generator config independent of Phase 6C event gain."""

    validate_source_artifact(source)
    threshold = _validated_threshold(threshold_dimensionless)
    model = _phase6c_model_config(source)
    return {
        "schema_version": GENERATOR_CONFIG_SCHEMA_VERSION,
        "generator_kind": GENERATOR_KIND,
        "threshold_dimensionless": threshold,
        "threshold_classification": "MODEL_ASSUMPTION",
        "state_semantics": "DIMENSIONLESS_EXPLORATORY_MOTOR_NEURAL_STATE",
        "crossing_rule": "x_prev < threshold_dimensionless <= x_current",
        "equality_at_new_boundary": "COUNTS_AS_CROSSING",
        "sampling": "stored_integer_state_boundaries_only_no_interpolation",
        "rearm": "eligible_again_only_after_state_is_below_threshold",
        "timing_semantics": "event_timestamp_is_first_crossing_state_boundary",
        "source_phase6c_model": {
            "model_id": model["model_id"],
            "model_version": model["model_version"],
            "config_sha256": canonical_sha256(model),
            "config": model,
        },
        "parameter_independence": {
            "threshold_is_independent_of_event_gain": True,
            "reference_equality_with_event_gain_is_incidental": True,
        },
        "provenance_kind": OUTPUT_EVENT_PROVENANCE,
        "biological_spike_claim": False,
    }


def _validate_fixture_source(source: LoadedSyntheticMotorArtifact) -> None:
    if not isinstance(source, LoadedSyntheticMotorArtifact):
        raise TTMnOutputRuleError(
            "output generation requires a validated Phase 8B artifact"
        )
    if source.artifact_id != EXPECTED_PHASE8B_ARTIFACT_ID:
        raise TTMnOutputRuleError("unsupported Phase 8B source artifact identity")
    if source.result.get("source_kind") != SYNTHETIC_SOURCE_KIND:
        raise TTMnOutputRuleError("Phase 8B source provenance is not synthetic")
    if source.result.get("sensory_source_artifact_id") is not None:
        raise TTMnOutputRuleError("synthetic source cannot reference Phase 7O")
    fixtures = source.result.get("fixtures")
    if (
        not isinstance(fixtures, list)
        or tuple(fixture.get("fixture_id") for fixture in fixtures) != FIXTURE_IDS
    ):
        raise TTMnOutputRuleError("Phase 8B source fixture battery is incomplete")
    _phase6c_model_config(source)


def validate_source_artifact(source: LoadedSyntheticMotorArtifact) -> None:
    """Fail closed unless input is the validated canonical Phase 8B child."""

    _validate_fixture_source(source)
    try:
        validate_phase8b_payload(dict(source.config), dict(source.result))
    except (TypeError, ValueError) as exc:
        raise TTMnOutputRuleError(
            "Phase 8B source trajectory failed deterministic replay"
        ) from exc


def _validate_trajectory(
    trajectory: Any, *, dt_ms: float, interval_count: int
) -> tuple[list[float], list[float], dict[str, Any]]:
    if not isinstance(trajectory, dict):
        raise TTMnOutputRuleError("Phase 8B trajectory record is malformed")
    body_id = trajectory.get("body_id")
    identity = _TTMN_BY_BODY_ID.get(body_id)
    if (
        identity is None
        or trajectory.get("neuron_type") != identity["type"]
        or trajectory.get("side") != identity["side"]
        or trajectory.get("state_unit") != "dimensionless"
    ):
        raise TTMnOutputRuleError("trajectory is not an authorized TTMn identity")
    times = trajectory.get("times_ms")
    states = trajectory.get("state")
    if (
        not isinstance(times, list)
        or not isinstance(states, list)
        or len(times) != interval_count + 1
        or len(states) != interval_count + 1
    ):
        raise TTMnOutputRuleError("trajectory boundaries do not match source run")
    for step, (time_ms, state) in enumerate(zip(times, states, strict=True)):
        if (
            isinstance(time_ms, bool)
            or not isinstance(time_ms, (int, float))
            or not math.isfinite(float(time_ms))
            or time_ms != step * dt_ms
        ):
            raise TTMnOutputRuleError("trajectory time is not its exact step boundary")
        if (
            isinstance(state, bool)
            or not isinstance(state, (int, float))
            or not math.isfinite(float(state))
        ):
            raise TTMnOutputRuleError("trajectory state must be finite")
    if (
        isinstance(trajectory.get("input_event_count"), bool)
        or not isinstance(trajectory.get("input_event_count"), int)
        or trajectory["input_event_count"] < 0
    ):
        raise TTMnOutputRuleError("trajectory input count is invalid")
    return (
        [float(value) for value in times],
        [float(value) for value in states],
        identity,
    )


def threshold_crossed(previous: float, current: float, threshold: float) -> bool:
    """Boundary crossing, not a level detector or repeated event generator."""
    return previous < threshold <= current


def _crossing_steps(
    states: list[float], threshold_dimensionless: Any
) -> tuple[int, ...]:
    """Cross stored values; public generation separately validates provenance."""

    threshold = _validated_threshold(threshold_dimensionless)
    if not states or any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        for value in states
    ):
        raise TTMnOutputRuleError("crossing input must contain finite state values")
    return tuple(
        step
        for step in range(1, len(states))
        if threshold_crossed(states[step - 1], states[step], threshold)
    )


def _source_fixture_records(
    source: LoadedSyntheticMotorArtifact,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    dt_ms = source.config["fixture_configs"][0]["dt_ms"]
    interval_count = source.config["fixture_configs"][0]["interval_count"]
    if any(
        config["dt_ms"] != dt_ms or config["interval_count"] != interval_count
        for config in source.config["fixture_configs"]
    ):
        raise TTMnOutputRuleError("Phase 8B fixture timing configs differ")
    for fixture in source.result["fixtures"]:
        if (
            fixture.get("source_kind") != SYNTHETIC_SOURCE_KIND
            or fixture.get("sensory_source_artifact_id") is not None
            or fixture.get("fixture_id") not in FIXTURE_IDS
            or not isinstance(fixture.get("synthetic_run_id"), str)
        ):
            raise TTMnOutputRuleError("Phase 8B fixture provenance is malformed")
        trajectories = fixture.get("ttmn_model_state")
        if not isinstance(trajectories, list) or len(trajectories) != len(
            _TTMN_BY_BODY_ID
        ):
            raise TTMnOutputRuleError("fixture must contain the two TTMn trajectories")
        if {item.get("body_id") for item in trajectories} != set(_TTMN_BY_BODY_ID):
            raise TTMnOutputRuleError("fixture TTMn body identities are incomplete")
        source_fixture_sha256 = canonical_sha256(fixture)
        body_records = []
        for trajectory in sorted(trajectories, key=lambda item: item["body_id"]):
            times, states, identity = _validate_trajectory(
                trajectory, dt_ms=dt_ms, interval_count=interval_count
            )
            body_records.append(
                {
                    "body_id": identity["body_id"],
                    "neuron_type": identity["type"],
                    "side": identity["side"],
                    "state_unit": "dimensionless",
                    "boundary_count": len(states),
                    "input_event_count": trajectory["input_event_count"],
                    "trajectory_sha256": canonical_sha256(trajectory),
                    "times_ms": times,
                    "state": states,
                }
            )
        records.append(
            {
                "fixture_id": fixture["fixture_id"],
                "fixture_config_sha256": fixture["fixture_config_sha256"],
                "synthetic_run_id": fixture["synthetic_run_id"],
                "source_kind": SYNTHETIC_SOURCE_KIND,
                "source_fixture_sha256": source_fixture_sha256,
                "source_events": fixture["source_events"],
                "trajectories": body_records,
            }
        )
    return records


def _output_event(
    *,
    source: LoadedSyntheticMotorArtifact,
    fixture: dict[str, Any],
    trajectory: dict[str, Any],
    step: int,
    time_ms: float,
    generator_config: dict[str, Any],
) -> dict[str, Any]:
    value = {
        "schema_version": OUTPUT_EVENT_SCHEMA_VERSION,
        "provenance_kind": OUTPUT_EVENT_PROVENANCE,
        "upstream_provenance_kind": SYNTHETIC_SOURCE_KIND,
        "motor_neuron_body_id": trajectory["body_id"],
        "motor_neuron_type": trajectory["neuron_type"],
        "neural_side": trajectory["side"],
        "step": step,
        "time_ms": time_ms,
        "generator_kind": GENERATOR_KIND,
        "generator_config_sha256": canonical_sha256(generator_config),
        "source_model": generator_config["source_phase6c_model"],
        "source_result": {
            "artifact_id": source.artifact_id,
            "result_sha256": source.result["result_sha256"],
            "fixture_id": fixture["fixture_id"],
            "fixture_result_sha256": fixture["source_fixture_sha256"],
            "fixture_config_sha256": fixture["fixture_config_sha256"],
            "synthetic_run_id": fixture["synthetic_run_id"],
            "trajectory_sha256": trajectory["trajectory_sha256"],
            "state_unit": "dimensionless",
        },
        "semantics": "EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT_EVENT",
        "biological_action_potential_claim": False,
    }
    value["event_id"] = canonical_sha256(value)
    return value


def _sorted_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        events,
        key=lambda event: (
            event["step"],
            event["motor_neuron_body_id"],
            event["event_id"],
        ),
    )


def build_output_config(
    source: LoadedSyntheticMotorArtifact,
    *,
    threshold_dimensionless: Any = REFERENCE_THRESHOLD_DIMENSIONLESS,
) -> dict[str, Any]:
    """Build the fixed-battery output-rule config from a replayable Phase 8B child."""

    validate_source_artifact(source)
    reference_generator = build_generator_config(source, threshold_dimensionless)
    sensitivity_generators = [
        build_generator_config(source, threshold)
        for threshold in SENSITIVITY_THRESHOLDS
    ]
    model = _phase6c_model_config(source)
    value: dict[str, Any] = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "source_artifact": {
            "artifact_id": source.artifact_id,
            "artifact_schema_version": source.manifest["artifact_schema_version"],
            "config_sha256": source.config["config_sha256"],
            "result_sha256": source.result["result_sha256"],
            "source_kind": SYNTHETIC_SOURCE_KIND,
        },
        "source_phase6c_model": {
            "model_id": model["model_id"],
            "model_version": model["model_version"],
            "config_sha256": canonical_sha256(model),
            "config": model,
        },
        "authorized_targets": [
            {
                "body_id": identity["body_id"],
                "neuron_type": identity["type"],
                "side": identity["side"],
            }
            for identity in sorted(
                MOTOR_PATHWAY_EVIDENCE.ttmn_identities,
                key=lambda item: item["body_id"],
            )
        ],
        "reference_generator_config": reference_generator,
        "sensitivity_generator_configs": sensitivity_generators,
        "sensitivity_thresholds_dimensionless": list(SENSITIVITY_THRESHOLDS),
        "threshold_event_gain_independence": "explicit_independent_config_fields",
        "provenance": {
            "upstream_input": SYNTHETIC_SOURCE_KIND,
            "derived_output": OUTPUT_EVENT_PROVENANCE,
            "phase7o_source": False,
            "phase8l_synthetic_output_fixture_source": False,
        },
        "scientific_boundary": {
            "source_state": "DIMENSIONLESS_EXPLORATORY_MOTOR_NEURAL_STATE",
            "threshold": "UNCALIBRATED_MODEL_ASSUMPTION",
            "output": "EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT_EVENT",
            "biological_action_potential_claim": False,
            "phase6c_trajectory_modified": False,
            "production_adapter": False,
            "muscle_target_dispatch": False,
            "muscle_dynamics": False,
            "dlmn_generator": False,
            "behavior_model": False,
        },
    }
    value["config_sha256"] = canonical_sha256(value)
    return value


def _result_for_config(
    source: LoadedSyntheticMotorArtifact, config: dict[str, Any]
) -> dict[str, Any]:
    fixture_sources = _source_fixture_records(source)
    reference_config = config["reference_generator_config"]
    thresholds = config["sensitivity_generator_configs"]
    result_fixtures = []
    for fixture in fixture_sources:
        sensitivity_rows = []
        generator_configs = list(thresholds)
        if all(
            item["threshold_dimensionless"]
            != reference_config["threshold_dimensionless"]
            for item in generator_configs
        ):
            generator_configs.append(reference_config)
        for generator_config in generator_configs:
            threshold = generator_config["threshold_dimensionless"]
            events = []
            for trajectory in fixture["trajectories"]:
                times = trajectory["times_ms"]
                states = trajectory["state"]
                for step in _crossing_steps(states, threshold):
                    events.append(
                        _output_event(
                            source=source,
                            fixture=fixture,
                            trajectory=trajectory,
                            step=step,
                            time_ms=times[step],
                            generator_config=generator_config,
                        )
                    )
            sensitivity_rows.append(
                {
                    "threshold_dimensionless": threshold,
                    "generator_config_sha256": canonical_sha256(generator_config),
                    "output_events": _sorted_events(events),
                }
            )
        reference_events = next(
            row["output_events"]
            for row in sensitivity_rows
            if row["threshold_dimensionless"]
            == reference_config["threshold_dimensionless"]
        )
        result_fixtures.append(
            {
                "fixture_id": fixture["fixture_id"],
                "fixture_config_sha256": fixture["fixture_config_sha256"],
                "synthetic_run_id": fixture["synthetic_run_id"],
                "source_kind": fixture["source_kind"],
                "source_fixture_sha256": fixture["source_fixture_sha256"],
                "source_events": fixture["source_events"],
                "source_trajectories": [
                    {
                        "body_id": item["body_id"],
                        "neuron_type": item["neuron_type"],
                        "side": item["side"],
                        "state_unit": item["state_unit"],
                        "boundary_count": item["boundary_count"],
                        "input_event_count": item["input_event_count"],
                        "trajectory_sha256": item["trajectory_sha256"],
                    }
                    for item in fixture["trajectories"]
                ],
                "reference_output_events": reference_events,
                "sensitivity": sensitivity_rows,
            }
        )
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "config_sha256": config["config_sha256"],
        "source_artifact_id": source.artifact_id,
        "source_result_sha256": source.result["result_sha256"],
        "source_kind": SYNTHETIC_SOURCE_KIND,
        "output_provenance_kind": OUTPUT_EVENT_PROVENANCE,
        "fixtures": result_fixtures,
        "summary": {
            "fixture_count": len(result_fixtures),
            "reference_threshold_dimensionless": reference_config[
                "threshold_dimensionless"
            ],
            "reference_output_event_count": sum(
                len(fixture["reference_output_events"]) for fixture in result_fixtures
            ),
            "sensitivity_output_event_counts": {
                str(row["threshold_dimensionless"]): sum(
                    len(
                        next(
                            item["output_events"]
                            for item in fixture["sensitivity"]
                            if item["threshold_dimensionless"]
                            == row["threshold_dimensionless"]
                        )
                    )
                    for fixture in result_fixtures
                )
                for row in thresholds
            },
        },
        "scientific_boundary": config["scientific_boundary"],
    }
    result["result_sha256"] = canonical_sha256(result)
    return result


def execute_output_rule(
    source: LoadedSyntheticMotorArtifact,
    *,
    threshold_dimensionless: Any = REFERENCE_THRESHOLD_DIMENSIONLESS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run threshold crossing over the canonical, validated Phase 8B trajectories."""

    config = build_output_config(
        source, threshold_dimensionless=threshold_dimensionless
    )
    return config, _result_for_config(source, config)


def validate_and_replay_payload(
    config: dict[str, Any],
    result: dict[str, Any],
    source: LoadedSyntheticMotorArtifact,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Rebuild source-bound generator config and output records exactly."""

    if not isinstance(config, dict) or not isinstance(result, dict):
        raise TTMnOutputRuleError("Phase 8N payload must be JSON objects")
    threshold = config.get("reference_generator_config", {}).get(
        "threshold_dimensionless"
    )
    expected_config, expected_result = execute_output_rule(
        source, threshold_dimensionless=threshold
    )
    if config != expected_config:
        raise TTMnOutputRuleError("Phase 8N config/source identity mismatch")
    if result != expected_result:
        raise TTMnOutputRuleError("Phase 8N results differ from replayed crossings")
    return expected_config, expected_result


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "CONFIG_SCHEMA_VERSION",
    "GENERATOR_KIND",
    "OUTPUT_EVENT_PROVENANCE",
    "OUTPUT_EVENT_SCHEMA_VERSION",
    "REFERENCE_THRESHOLD_DIMENSIONLESS",
    "RESULT_SCHEMA_VERSION",
    "SENSITIVITY_THRESHOLDS",
    "TTMnOutputRuleError",
    "build_generator_config",
    "build_output_config",
    "canonical_sha256",
    "execute_output_rule",
    "validate_and_replay_payload",
]
