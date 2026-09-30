"""Phase 9B: deterministic, uncalibrated passive G1-proxy model-space response."""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass

from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_abstract_electrical_input_artifacts import (
    replay_abstract_input_artifact,
)
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)
from neurofly.ttm_g1_proxy_mapping import DEFAULT_SOURCE_PATHS, SOURCE_IDENTITIES
from neurofly.ttm_g1_proxy_mapping_artifacts import replay_proxy_artifact

MODEL_SCHEMA = "passive_g1_proxy_electrical_model_v1"
RESULT_SCHEMA = "g1_proxy_passive_electrical_response_v1"
ARTIFACT_SCHEMA = "g1_proxy_passive_electrical_response_artifact_v1"
PROVENANCE = "EXPLORATORY_G1_PROXY_ELECTRICAL_MODEL"
PROXY_ARTIFACT_ID = "030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8"
PROXY_DOMAIN_ID = "ttm-g1-proxy-domain-057e09a9a9c5b054f7ce"
DEFAULT_PROXY_ARTIFACT = (
    DEFAULT_SOURCE_ROOT / "ttm_g1_proxy_mapping_artifact_v1" / PROXY_ARTIFACT_ID
)
FIXTURE_IDS = (
    "ZERO_EVENT_CONTROL",
    "RIGHT_SINGLE_EVENT",
    "LEFT_SINGLE_EVENT",
    "BILATERAL_SIMULTANEOUS_EVENT",
    "RIGHT_REPEATED_EVENTS",
    "LEFT_REPEATED_EVENTS",
)
BOUNDARIES = (
    "EXPLORATORY_UNCALIBRATED_MODEL_SPACE_VOLTAGE_EQUIVALENT",
    "NO_RELEASE_OR_CONDUCTANCE_OR_CURRENT_MODEL",
    "NO_BIOLOGICAL_DELAY_OR_CALIBRATION_CLAIM",
    "VIRTUAL_G1_PROXY_NOT_ANATOMICAL_DESTINATION",
    "NO_WHOLE_TTM_ACTIVATION_CONTRACTION_FORCE",
    "NO_OBSERVATION_OPERATOR_OR_COMPARISON",
    "SHARED_MODEL_ASSUMPTION_CONFIG_NOT_BILATERAL_PHYSIOLOGY",
)
SEMANTICS = {
    "schema_version": MODEL_SCHEMA,
    "transformation": "ABSTRACT_EVENT_TO_EFFECTIVE_MODEL_DRIVE",
    "initialization": "ZERO_DEVIATION_BEFORE_BOUNDARY_ZERO",
    "event_order": "EXACT_EXPONENTIAL_DECAY_THEN_BOUNDARY_INCREMENT_POST_INPUT_SAMPLE",
    "boundary_zero": "APPLY_ZERO_BOUNDARY_TOKENS_WITHOUT_PRECEDING_DECAY",
    "timing_assumption": "ZERO_ADDED_MODEL_DELAY_ASSUMPTION",
    "input_multiplicity": "DISTINCT_TOKEN_COUNT_NOT_QUANTA_OR_STRUCTURAL_WEIGHT",
    "config_sharing": "SHARED_MODEL_ASSUMPTION_CONFIG",
    "parameter_classifications": {
        "reference_voltage_mV_eq": "MODEL_ASSUMPTION",
        "tau_effective_ms": "MODEL_ASSUMPTION",
        "event_scale_effective_mV_eq": "MODEL_ASSUMPTION",
    },
}


@dataclass(frozen=True, slots=True)
class PassiveConfig:
    """All free numbers required explicitly; no empirical parameter defaults."""

    dt_ms: float
    interval_count: int
    reference_voltage_mV_eq: float
    tau_effective_ms: float
    event_scale_effective_mV_eq: float
    proxy_domain_id: str

    def __post_init__(self) -> None:
        for name in (
            "dt_ms",
            "reference_voltage_mV_eq",
            "tau_effective_ms",
            "event_scale_effective_mV_eq",
        ):
            value = getattr(self, name)
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"{name} must be finite numeric")
        if (
            min(self.dt_ms, self.tau_effective_ms, self.event_scale_effective_mV_eq)
            <= 0
        ):
            raise ValueError("dt, tau and event scale must be positive")
        if (
            type(self.interval_count) is not int
            or not 1 <= self.interval_count <= 100_000
        ):
            raise ValueError("interval count must be an integer in 1..100000")
        if not math.isfinite(self.dt_ms * self.interval_count):
            raise ValueError("nonfinite duration")
        if self.proxy_domain_id != PROXY_DOMAIN_ID:
            raise ValueError("require pinned virtual G1 domain type")

    def payload(self) -> dict:
        return {
            **copy.deepcopy(SEMANTICS),
            "dt_ms": float(self.dt_ms),
            "interval_count": self.interval_count,
            "duration_ms": self.dt_ms * self.interval_count,
            "reference_voltage_mV_eq": float(self.reference_voltage_mV_eq),
            "tau_effective_ms": float(self.tau_effective_ms),
            "event_scale_effective_mV_eq": float(self.event_scale_effective_mV_eq),
            "proxy_domain_id": self.proxy_domain_id,
        }

    @classmethod
    def from_payload(cls, payload: dict) -> PassiveConfig:
        try:
            config = cls(**{name: payload[name] for name in cls.__dataclass_fields__})
        except (KeyError, TypeError) as exc:
            raise ValueError("malformed model config") from exc
        if canonical_json_bytes(payload) != canonical_json_bytes(config.payload()):
            raise ValueError("config fields or update/assumption semantics changed")
        return config


def reference_config() -> PassiveConfig:
    """Neutral origin; ten-grid-step decay; simple two-unit increment, not a fit."""
    return PassiveConfig(0.1, 80, 0.0, 1.0, 2.0, PROXY_DOMAIN_ID)


def integrate_counts(config: PassiveConfig, counts: list[int]) -> dict:
    """Numerical primitive only; the fixture runner supplies validated token counts."""
    if len(counts) != config.interval_count + 1 or any(
        type(n) is not int or n < 0 for n in counts
    ):
        raise ValueError("require one nonnegative integer count per boundary")
    alpha = math.exp(-config.dt_ms / config.tau_effective_ms)
    deviations, voltages = [], []
    u = 0.0
    for step, count in enumerate(counts):
        u = (alpha * u if step else 0.0) + count * config.event_scale_effective_mV_eq
        voltage = config.reference_voltage_mV_eq + u
        if not math.isfinite(u) or not math.isfinite(voltage):
            raise ValueError("nonfinite model trajectory")
        deviations.append(u)
        voltages.append(voltage)
    peak = max(deviations)
    return {
        "token_count": list(counts),
        "voltage_deviation_mV_eq": deviations,
        "proxy_voltage_mV_eq": voltages,
        "summary": {
            "input_token_count": sum(counts),
            "peak_deviation_mV_eq": peak,
            "peak_boundary": deviations.index(peak),
            "final_deviation_mV_eq": deviations[-1],
        },
    }


def build_response(
    config: PassiveConfig,
    *,
    input_artifact=DEFAULT_SOURCE_PATHS["phase8w"],
    proxy_artifact=DEFAULT_PROXY_ARTIFACT,
) -> dict:
    """Replay sources, then independently integrate both bodies per fixture."""
    w = replay_abstract_input_artifact(input_artifact)
    y = replay_proxy_artifact(proxy_artifact)
    if (
        w.artifact_id != SOURCE_IDENTITIES["phase8w"][1]
        or y.artifact_id != PROXY_ARTIFACT_ID
    ):
        raise ValueError("source artifact identity changed")
    if config.dt_ms != 0.1 or config.interval_count != 80:
        raise ValueError(
            "canonical source runner requires unchanged 0.1ms/80-interval grid"
        )
    domain = y.contract["result"]["proxy_domains"][0]
    mappings = y.contract["result"]["source_mappings"]
    if domain["proxy_domain_id"] != config.proxy_domain_id:
        raise ValueError("proxy domain mismatch")
    fixtures = w.contract["result"]["fixtures"]
    if tuple(f["fixture_id"] for f in fixtures) != FIXTURE_IDS:
        raise ValueError("source fixture set/order changed")
    config_payload = {
        "model": config.payload(),
        "scientific_boundary": list(BOUNDARIES),
        "provenance_kind": PROVENANCE,
        "sources": {
            phase: {
                "artifact_id": a.artifact_id,
                "config_sha256": a.contract["config_sha256"],
                "result_sha256": a.contract["result_sha256"],
            }
            for phase, a in (("phase8w", w), ("phase8y", y))
        },
        "instance_semantics": (
            "INDEPENDENT_FIXTURE_AND_CAUSAL_BODY_STATES_SHARED_VIRTUAL_DOMAIN_TYPE"
        ),
    }
    config_hash = canonical_sha256(config_payload)
    results = []
    for fixture in fixtures:
        instances = []
        for mapping in mappings:
            body = mapping["source_motor_neuron_body_id"]
            tokens = [t for t in fixture["tokens"] if t["motor_neuron_body_id"] == body]
            counts = [0] * (config.interval_count + 1)
            for token in tokens:
                step = token["step"]
                if (
                    type(step) is not int
                    or not 0 <= step <= config.interval_count
                    or token["time_ms"] != step * config.dt_ms
                    or token["neural_side"] != mapping["source_neural_side"]
                    or token["target_association_id"]
                    != mapping["source_ttm_association_id"]
                ):
                    raise ValueError("token/proxy association or grid mismatch")
                counts[step] += 1
            instances.append(
                {
                    "source_body_id": body,
                    "source_side": mapping["source_neural_side"],
                    "proxy_domain_id": config.proxy_domain_id,
                    "proxy_source_mapping_id": mapping["mapping_id"],
                    "config_id": config_hash,
                    "instance_id": canonical_sha256(
                        [fixture["fixture_id"], body, config_hash]
                    ),
                    "source_token_ids": [t["event_id"] for t in tokens],
                    "provenance_chain": [*tokens[0]["provenance_chain"], PROVENANCE]
                    if tokens
                    else [PROVENANCE],
                    **integrate_counts(config, counts),
                }
            )
        if sum(i["summary"]["input_token_count"] for i in instances) != len(
            fixture["tokens"]
        ):
            raise ValueError("unassigned source token")
        results.append(
            {
                "fixture_id": fixture["fixture_id"],
                "source_synthetic_run_id": fixture["source_synthetic_run_id"],
                "instances": instances,
            }
        )
    result = {
        "schema_version": RESULT_SCHEMA,
        "boundary_indices": list(range(config.interval_count + 1)),
        "time_ms": [n * config.dt_ms for n in range(config.interval_count + 1)],
        "fixtures": results,
        "source_token_count": sum(len(f["tokens"]) for f in fixtures),
        "instance_count": len(results) * len(mappings),
    }
    result_hash = canonical_sha256(result)
    return {
        "schema_version": RESULT_SCHEMA,
        "config": config_payload,
        "result": result,
        "config_sha256": config_hash,
        "result_sha256": result_hash,
        "artifact_id": canonical_sha256([ARTIFACT_SCHEMA, config_hash, result_hash]),
    }


def validate_response(payload: dict, **sources) -> dict:
    try:
        config = PassiveConfig.from_payload(payload["config"]["model"])
    except (KeyError, TypeError) as exc:
        raise ValueError("malformed passive response") from exc
    expected = build_response(config, **sources)
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError(
            "response/source/trajectory identity differs from offline replay"
        )
    return expected
