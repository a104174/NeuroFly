"""Phase 11B: functional addressing only, not geometry or muscle dynamics."""

from __future__ import annotations

import copy
import math

from neurofly.muscle_activation import MODEL_SCHEMA as SOURCE_MODEL_SCHEMA
from neurofly.muscle_activation import RESULT_SCHEMA as SOURCE_RESULT_SCHEMA
from neurofly.muscle_activation_artifacts import (
    DEFAULT_ARTIFACT_ROOT as SOURCE_ROOT,
)
from neurofly.muscle_activation_artifacts import (
    replay_activation_artifact,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

MODEL_SCHEMA = "ttm_exploratory_actuator_command_v1"
RESULT_SCHEMA = "ttm_exploratory_actuator_command_result_v1"
ARTIFACT_SCHEMA = "ttm_exploratory_actuator_command_artifact_v1"
SOURCE_ID = "4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb"
DEFAULT_SOURCE_ARTIFACT = SOURCE_ROOT / SOURCE_ID
PROVENANCE = "EXPLORATORY_TTM_ACTUATOR_COMMAND"
ACTION = "TTM_ASSOCIATED_FEMUR_EXTENSION_DRIVE"
EXCLUSIONS = (
    "NO_PHYSICAL_FORCE_OR_CONTRACTION",
    "NO_PHYSICAL_ACTUATOR_GEOMETRY_OR_JOINT_MAPPING",
    "NO_BODY_MOVEMENT_OR_SCENARIO",
    "VIRTUAL_CHANNEL_NOT_PHYSICAL_G1_OR_WHOLE_TTM",
    "NO_BILATERAL_PHYSIOLOGICAL_EQUIVALENCE",
    "NO_EMPIRICAL_CALIBRATION",
)


def routing_config() -> dict:
    """Fixed, versioned semantic configuration; no free numerical parameter."""
    records = []
    for body, side, channel in (
        (800146, "R", "RIGHT_TTM_ACTUATOR"),
        (804642, "L", "LEFT_TTM_ACTUATOR"),
    ):
        record = {
            "source_body_id": body,
            "source_neural_side": side,
            "source_activation_model_schema": SOURCE_MODEL_SCHEMA,
            "source_activation_artifact_id": SOURCE_ID,
            "actuator_id": channel,
            "actuator_side": side,
            "action_kind": ACTION,
            "classification": "EXPLORATORY_FUNCTIONAL_ACTUATOR_MAPPING",
            "assumption_classification": "MODEL_ASSUMPTION",
        }
        records.append({"routing_id": canonical_sha256(record), **record})
    return {
        "schema_version": MODEL_SCHEMA,
        "source_model_schema": SOURCE_MODEL_SCHEMA,
        "source_result_schema": SOURCE_RESULT_SCHEMA,
        "routing_records": records,
        "units": "dimensionless",
        "magnitude_semantics": "EXACT_ACTIVATION_PROXY_PASSTHROUGH",
        "temporal_semantics": "SAME_STORED_BOUNDARY_NO_RESAMPLING",
        "ceiling_semantics": "SOURCE_MODEL_NORMALIZATION_CEILING",
        "assumption_classification": "MODEL_ASSUMPTION",
        "exclusions": list(EXCLUSIONS),
    }


def validate_config(config: dict) -> None:
    if canonical_json_bytes(config) != canonical_json_bytes(routing_config()):
        raise ValueError("actuator routing/config semantics changed")


def actuator_channel(body_id: int, side: str) -> str:
    """Identity-validated functional routing, independent of artifact envelopes."""
    for row in routing_config()["routing_records"]:
        if (body_id, side) == (row["source_body_id"], row["source_neural_side"]):
            return row["actuator_id"]
    raise ValueError("unknown/cross-sided actuator source")


def route_activation(source: dict, config: dict) -> dict:
    """Observe a validated canonical source. Never integrate or read tokens.

    Production build_commands replays persisted activation first. This primitive
    additionally requires byte-semantic canonical source identity and checks
    trajectory identities before routing.
    """
    validate_config(config)
    try:
        from neurofly.muscle_activation import ARTIFACT_SCHEMA as source_schema

        ch = canonical_sha256(source["config"])
        rh = canonical_sha256(source["result"])
        if (
            source["artifact_id"] != SOURCE_ID
            or source["schema_version"] != SOURCE_RESULT_SCHEMA
            or source["result"]["schema_version"] != SOURCE_RESULT_SCHEMA
            or source["config"]["model"]["schema_version"] != SOURCE_MODEL_SCHEMA
            or source["config_sha256"] != ch
            or source["result_sha256"] != rh
            or SOURCE_ID != canonical_sha256([source_schema, ch, rh])
        ):
            raise ValueError("canonical activation source identity/schema changed")
        grid = source["result"]["boundary_indices"]
        times = source["result"]["time_ms"]
        if grid != list(range(81)) or times != [n * 0.1 for n in grid]:
            raise ValueError("malformed activation time grid")
        # Canonical fixtures are defined by the direct source, not event input.
        fixtures = source["result"]["fixtures"]
        expected_fixtures = (
            "ZERO_EVENT_CONTROL",
            "RIGHT_SINGLE_EVENT",
            "LEFT_SINGLE_EVENT",
            "BILATERAL_SIMULTANEOUS_EVENT",
            "RIGHT_REPEATED_EVENTS",
            "LEFT_REPEATED_EVENTS",
        )
        if tuple(f["fixture_id"] for f in fixtures) != expected_fixtures:
            raise ValueError("canonical activation fixture set/order changed")
        configuration = {
            "adapter": copy.deepcopy(config),
            "source_phase10b": {
                "artifact_id": SOURCE_ID,
                "config_sha256": ch,
                "result_sha256": rh,
                "schema_version": SOURCE_RESULT_SCHEMA,
            },
            "provenance_kind": PROVENANCE,
        }
        config_hash = canonical_sha256(configuration)
        seen = set()
        output = []
        for fixture in fixtures:
            rows = fixture["instances"]
            if [(r["source_body_id"], r["source_side"]) for r in rows] != [
                (800146, "R"),
                (804642, "L"),
            ]:
                raise ValueError("activation body/side identity mismatch")
            instances = []
            for row, routing in zip(rows, config["routing_records"], strict=True):
                tid = row["trajectory_id"]
                original = {k: v for k, v in row.items() if k != "trajectory_id"}
                values = row["activation_proxy"]
                if (
                    tid in seen
                    or tid != canonical_sha256(original)
                    or not row["proxy_domain_id"]
                    or not row["proxy_source_mapping_id"]
                    or len(values) != len(grid)
                    or any(
                        type(v) not in (int, float)
                        or not math.isfinite(v)
                        or not 0 <= v <= 1
                        for v in values
                    )
                ):
                    raise ValueError("invalid activation trajectory/proxy/samples")
                seen.add(tid)
                peak = max(values)
                step = values.index(peak)
                payload = {
                    "source_activation_trajectory_id": tid,
                    "source_activation_trajectory_sha256": canonical_sha256(row),
                    "source_body_id": row["source_body_id"],
                    "source_side": row["source_side"],
                    "proxy_domain_id": row["proxy_domain_id"],
                    "proxy_source_mapping_id": row["proxy_source_mapping_id"],
                    "routing_id": routing["routing_id"],
                    "actuator_id": actuator_channel(
                        row["source_body_id"], row["source_side"]
                    ),
                    "actuator_side": routing["actuator_side"],
                    "action_kind": ACTION,
                    "config_id": config_hash,
                    "provenance_chain": [*row["provenance_chain"], PROVENANCE],
                    "actuator_command": list(values),
                    "summary": {
                        "peak_actuator_command": peak,
                        "peak_step": step,
                        "peak_time_ms": times[step],
                        "final_command": values[-1],
                        "nonzero_sample_count": sum(v > 0 for v in values),
                    },
                }
                instances.append(
                    {"trajectory_id": canonical_sha256(payload), **payload}
                )
            output.append({"fixture_id": fixture["fixture_id"], "instances": instances})
        result = {
            "schema_version": RESULT_SCHEMA,
            "boundary_indices": list(grid),
            "time_ms": list(times),
            "fixtures": output,
            "trajectory_count": len(seen),
            "sample_count": len(seen) * len(grid),
        }
        result_hash = canonical_sha256(result)
        return {
            "schema_version": RESULT_SCHEMA,
            "config": configuration,
            "result": result,
            "config_sha256": config_hash,
            "result_sha256": result_hash,
            "artifact_id": canonical_sha256(
                [ARTIFACT_SCHEMA, config_hash, result_hash]
            ),
        }
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("malformed activation source") from exc


def build_commands(*, source_artifact=DEFAULT_SOURCE_ARTIFACT) -> dict:
    return route_activation(
        replay_activation_artifact(source_artifact), routing_config()
    )


def validate_commands(payload: dict, **sources) -> dict:
    expected = build_commands(**sources)
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError("actuator source/config/result differs from offline replay")
    return expected
