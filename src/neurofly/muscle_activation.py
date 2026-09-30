"""Phase 10B: memoryless, uncalibrated activation proxy, not muscle physiology."""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass

from neurofly.g1_proxy_passive_electrical import (
    ARTIFACT_SCHEMA as SOURCE_ARTIFACT_SCHEMA,
)
from neurofly.g1_proxy_passive_electrical import (
    FIXTURE_IDS,
    PassiveConfig,
)
from neurofly.g1_proxy_passive_electrical import (
    PROVENANCE as SOURCE_PROVENANCE,
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

MODEL_SCHEMA = "static_normalized_muscle_activation_model_v1"
RESULT_SCHEMA = "static_normalized_muscle_activation_result_v1"
ARTIFACT_SCHEMA = "static_normalized_muscle_activation_artifact_v1"
PROVENANCE = "EXPLORATORY_MUSCLE_ACTIVATION_MODEL"
SOURCE_ID = "72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f"
DEFAULT_MODEL_ARTIFACT = DEFAULT_SOURCE_ROOT / SOURCE_ARTIFACT_SCHEMA / SOURCE_ID
BOUNDARIES = (
    "EXPLORATORY_UNCALIBRATED_DIMENSIONLESS_ACTIVATION_PROXY",
    "MV_EQ_DRIVER_NOT_BIOLOGICAL_MV",
    "VIRTUAL_G1_DOMAIN_NOT_PHYSICAL_FIBER_OR_WHOLE_TTM",
    "NO_CONTRACTION_FORCE_CALCIUM_OR_BODY_MECHANICS",
    "NO_ADDITIONAL_ACTIVATION_MEMORY_THRESHOLD_OR_DELAY",
    "NO_EMPIRICAL_COMPARISON_OR_CALIBRATION",
    "SHARED_CONFIG_NOT_BILATERAL_PHYSIOLOGICAL_EQUIVALENCE",
)
SEMANTICS = {
    "schema_version": MODEL_SCHEMA,
    "source_model_schema": "passive_g1_proxy_electrical_model_v1",
    "driver_quantity": "voltage_deviation_mV_eq",
    "driver_units": "UNCALIBRATED_MODEL_SPACE_MV_EQ",
    "output_units": "dimensionless",
    "rectification": "POSITIVE_PART_RECTIFICATION",
    "normalization": "POSITIVE_DRIVER_DIVIDED_BY_EXPLICIT_SCALE",
    "ceiling": 1.0,
    "ceiling_semantics": "MODEL_NORMALIZATION_CEILING",
    "temporal_semantics": "MEMORYLESS_SAME_STORED_BOUNDARY_NO_RESAMPLING",
    "config_sharing": "SHARED_EXPLORATORY_MODEL_CONFIG",
    "parameter_classifications": {
        "activation_scale_mV_eq": "MODEL_ASSUMPTION",
        "rectification": "MODEL_ASSUMPTION",
        "ceiling": "MODEL_ASSUMPTION",
        "config_sharing": "MODEL_ASSUMPTION",
    },
    "scientific_boundary": list(BOUNDARIES),
}


def _finite(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


@dataclass(frozen=True, slots=True)
class ActivationConfig:
    """The only free parameter is an explicitly assumed normalization scale."""

    activation_scale_mV_eq: float

    def __post_init__(self) -> None:
        if not _finite(self.activation_scale_mV_eq) or self.activation_scale_mV_eq <= 0:
            raise ValueError("activation scale must be finite and positive")

    def payload(self) -> dict:
        return {
            **copy.deepcopy(SEMANTICS),
            "activation_scale_mV_eq": float(self.activation_scale_mV_eq),
        }

    @classmethod
    def from_payload(cls, payload: dict) -> ActivationConfig:
        try:
            config = cls(payload["activation_scale_mV_eq"])
        except (KeyError, TypeError) as exc:
            raise ValueError("malformed activation config") from exc
        if canonical_json_bytes(payload) != canonical_json_bytes(config.payload()):
            raise ValueError("activation config/semantics changed")
        return config


def reference_config() -> ActivationConfig:
    """Ten model-space units, selected independently of evidence/source peaks."""
    return ActivationConfig(10.0)


def activate_samples(deviations: list[float], config: ActivationConfig) -> list[float]:
    """Pure pointwise transformation; no source event or electrical integration."""
    if (
        not isinstance(deviations, list)
        or not deviations
        or any(not _finite(u) for u in deviations)
    ):
        raise ValueError("require finite nonempty electrical deviation samples")
    # Compare before division to avoid overflow for tiny positive scales.
    scale = config.activation_scale_mV_eq
    return [0.0 if u <= 0 else 1.0 if u >= scale else u / scale for u in deviations]


def transform_response(source: dict, config: ActivationConfig) -> dict:
    """Consume an already replayed source; integrity/shape checks do not simulate.

    Production uses build_activation(), which replays the exact persisted source.
    This primitive also accepts integrity-valid test-local Phase 9B outputs.
    No Phase 8W token schedule or Phase 9E result is read here.
    """
    try:
        model = PassiveConfig.from_payload(source["config"]["model"])
        ch, rh = canonical_sha256(source["config"]), canonical_sha256(source["result"])
        if (
            source["schema_version"] != SOURCE_RESULT_SCHEMA
            or source["result"]["schema_version"] != SOURCE_RESULT_SCHEMA
            or source["config"]["provenance_kind"] != SOURCE_PROVENANCE
            or source["config_sha256"] != ch
            or source["result_sha256"] != rh
            or source["artifact_id"]
            != canonical_sha256([SOURCE_ARTIFACT_SCHEMA, ch, rh])
        ):
            raise ValueError("electrical source schema/provenance/hash mismatch")
        grid, times = source["result"]["boundary_indices"], source["result"]["time_ms"]
        if (
            grid != list(range(model.interval_count + 1))
            or any(type(n) is not int for n in grid)
            or len(times) != len(grid)
            or any(not _finite(t) or t != n * model.dt_ms for n, t in enumerate(times))
        ):
            raise ValueError("invalid electrical source grid")
        fixtures = source["result"]["fixtures"]
        if tuple(f["fixture_id"] for f in fixtures) != FIXTURE_IDS:
            raise ValueError("electrical fixture set/order changed")
        config_payload = {
            "model": config.payload(),
            "provenance_kind": PROVENANCE,
            "source_phase9b": {
                "artifact_id": source["artifact_id"],
                "config_sha256": ch,
                "result_sha256": rh,
                "schema_version": SOURCE_RESULT_SCHEMA,
            },
        }
        config_hash = canonical_sha256(config_payload)
        seen = set()
        results = []
        for fixture in fixtures:
            rows = fixture["instances"]
            if [(i["source_body_id"], i["source_side"]) for i in rows] != [
                (800146, "R"),
                (804642, "L"),
            ]:
                raise ValueError("electrical causal identity set/order changed")
            instances = []
            for row in rows:
                sid = row["instance_id"]
                if (
                    type(row["source_body_id"]) is not int
                    or sid in seen
                    or sid
                    != canonical_sha256(
                        [fixture["fixture_id"], row["source_body_id"], ch]
                    )
                    or row["config_id"] != ch
                    or row["proxy_domain_id"] != model.proxy_domain_id
                    or not isinstance(row["proxy_source_mapping_id"], str)
                    or not row["proxy_source_mapping_id"]
                ):
                    raise ValueError("electrical trajectory identity/proxy mismatch")
                seen.add(sid)
                driver = row["voltage_deviation_mV_eq"]
                if len(driver) != len(grid):
                    raise ValueError("electrical sample count mismatch")
                activation = activate_samples(driver, config)
                peak = max(activation)
                peak_step = activation.index(peak)
                payload = {
                    "source_trajectory_id": sid,
                    "source_trajectory_sha256": canonical_sha256(row),
                    "source_body_id": row["source_body_id"],
                    "source_side": row["source_side"],
                    "proxy_domain_id": row["proxy_domain_id"],
                    "proxy_source_mapping_id": row["proxy_source_mapping_id"],
                    "config_id": config_hash,
                    "provenance_chain": [SOURCE_PROVENANCE, PROVENANCE],
                    "voltage_deviation_mV_eq": list(driver),
                    "activation_proxy": activation,
                    "summary": {
                        "peak_activation_proxy": peak,
                        "peak_step": peak_step,
                        "peak_time_ms": times[peak_step],
                        "final_activation_proxy": activation[-1],
                        "ceiling_sample_count": sum(
                            u >= config.activation_scale_mV_eq for u in driver
                        ),
                        "source_peak_deviation_mV_eq": max(driver),
                    },
                }
                instances.append(
                    {"trajectory_id": canonical_sha256(payload), **payload}
                )
            results.append(
                {"fixture_id": fixture["fixture_id"], "instances": instances}
            )
        result = {
            "schema_version": RESULT_SCHEMA,
            "boundary_indices": list(grid),
            "time_ms": list(times),
            "fixtures": results,
            "trajectory_count": len(seen),
            "sample_count": len(seen) * len(grid),
        }
        result_hash = canonical_sha256(result)
        return {
            "schema_version": RESULT_SCHEMA,
            "config": config_payload,
            "result": result,
            "config_sha256": config_hash,
            "result_sha256": result_hash,
            "artifact_id": canonical_sha256(
                [ARTIFACT_SCHEMA, config_hash, result_hash]
            ),
        }
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("malformed electrical source") from exc


def build_activation(
    config: ActivationConfig, *, source_artifact=DEFAULT_MODEL_ARTIFACT
) -> dict:
    source = replay_response_artifact(source_artifact)
    if source["artifact_id"] != SOURCE_ID:
        raise ValueError("require canonical Phase 9B source artifact")
    return transform_response(source, config)


def validate_activation(payload: dict, **sources) -> dict:
    try:
        config = ActivationConfig.from_payload(payload["config"]["model"])
    except (KeyError, TypeError) as exc:
        raise ValueError("malformed activation result") from exc
    expected = build_activation(config, **sources)
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError("activation source/config/result differs from offline replay")
    return expected
