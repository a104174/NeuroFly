"""Deterministic Level P E1 sensory encoding.

The encoder consumes already-computed :class:`LoomingSample` geometry and
produces the existing Phase 2B :class:`ExternalDriveSchedule`.  It owns only
the explicitly documented NeuroFly Level P assumptions; the LIF simulator
remains unaware of stimulus semantics.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from neurofly.malecns.sensory import LoomingSample, VisualPoint
from neurofly.simulation import (
    ExternalDriveSchedule,
    SimulationGraph,
    SimulationGraphError,
)

ENCODER_ID = "level_p_instantaneous_bounded_v1"
ENCODER_VERSION = "phase2e_v1"
ENCODING_SCHEMA = "level_p_encoding_v1"
NORMALIZATION_POLICY = "bounded_half_scale_v1"
BASELINE_POLICY = "zero_v1"
NEGATIVE_FEATURE_POLICY = "clamp_zero_v1"
POPULATION_POLICY = "bilateral_type_broadcast_v1"
LATERALITY_POLICY = "bilateral_v1"
LATENCY_POLICY = "no_added_latency_v1"
FILTER_POLICY = "instantaneous_v1"
STOCHASTIC_POLICY = "deterministic"
_TIME_TOLERANCE_S = 1e-12


class LevelPEncodingError(ValueError):
    """The Level P input or encoder configuration is invalid."""


def _finite_float(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise LevelPEncodingError(f"{field_name} must be finite.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise LevelPEncodingError(f"{field_name} must be finite.") from None
    if not math.isfinite(result):
        raise LevelPEncodingError(f"{field_name} must be finite.")
    return result


def _non_empty_identifier(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise LevelPEncodingError(f"{field_name} must be a non-empty string.")
    return value


def _bounded_feature(value: float, half_scale: float) -> float:
    """Return ``value / (value + half_scale)`` without overflow.

    Both arguments are finite and non-negative/positive respectively.  The
    reciprocal form avoids overflowing their sum for very large finite
    stimulus values.  A finite floating-point value can round to one when the
    half-scale is far below machine precision; cap it at the largest float
    below one so the documented ``[0, 1)`` contract remains explicit.
    """

    if value == 0.0:
        return 0.0
    normalized = 1.0 / (1.0 + half_scale / value)
    if normalized >= 1.0:
        normalized = math.nextafter(1.0, 0.0)
    return normalized


def _sha256_json(value: Any) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


@dataclass(frozen=True, slots=True)
class LevelPEncoderConfig:
    """Immutable E1 configuration with explicit modelling provenance.

    The four numeric fields are required positional inputs in practice: they
    have no calibrated biological defaults.  The remaining fields identify
    fixed policies implemented by this encoder version.
    """

    lc4_gain_mv_eq: float
    lplc2_gain_mv_eq: float
    omega_half_rad_per_s: float
    theta_half_rad: float
    encoder_id: str = ENCODER_ID
    encoder_version: str = ENCODER_VERSION
    normalization_policy: str = NORMALIZATION_POLICY
    baseline_policy: str = BASELINE_POLICY
    negative_feature_policy: str = NEGATIVE_FEATURE_POLICY
    population_policy: str = POPULATION_POLICY
    laterality_policy: str = LATERALITY_POLICY
    latency_policy: str = LATENCY_POLICY
    filter_policy: str = FILTER_POLICY
    stochastic_policy: str = STOCHASTIC_POLICY

    def __post_init__(self) -> None:
        numeric = (
            ("lc4_gain_mv_eq", self.lc4_gain_mv_eq, False),
            ("lplc2_gain_mv_eq", self.lplc2_gain_mv_eq, False),
            ("omega_half_rad_per_s", self.omega_half_rad_per_s, True),
            ("theta_half_rad", self.theta_half_rad, True),
        )
        for field_name, raw_value, strictly_positive in numeric:
            value = _finite_float(raw_value, field_name)
            if strictly_positive and value <= 0.0:
                raise LevelPEncodingError(f"{field_name} must be greater than zero.")
            if not strictly_positive and value < 0.0:
                raise LevelPEncodingError(f"{field_name} cannot be negative.")
            object.__setattr__(self, field_name, value)

        for field_name in (
            "encoder_id",
            "encoder_version",
            "normalization_policy",
            "baseline_policy",
            "negative_feature_policy",
            "population_policy",
            "laterality_policy",
            "latency_policy",
            "filter_policy",
            "stochastic_policy",
        ):
            _non_empty_identifier(getattr(self, field_name), field_name)

        expected_policies = {
            "encoder_id": ENCODER_ID,
            "encoder_version": ENCODER_VERSION,
            "normalization_policy": NORMALIZATION_POLICY,
            "baseline_policy": BASELINE_POLICY,
            "negative_feature_policy": NEGATIVE_FEATURE_POLICY,
            "population_policy": POPULATION_POLICY,
            "laterality_policy": LATERALITY_POLICY,
            "latency_policy": LATENCY_POLICY,
            "filter_policy": FILTER_POLICY,
            "stochastic_policy": STOCHASTIC_POLICY,
        }
        for field_name, expected in expected_policies.items():
            if getattr(self, field_name) != expected:
                raise LevelPEncodingError(
                    f"Unsupported {field_name} {getattr(self, field_name)!r}; "
                    f"expected {expected!r}."
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "encoder_id": self.encoder_id,
            "encoder_version": self.encoder_version,
            "lc4_gain_mv_eq": self.lc4_gain_mv_eq,
            "lplc2_gain_mv_eq": self.lplc2_gain_mv_eq,
            "omega_half_rad_per_s": self.omega_half_rad_per_s,
            "theta_half_rad": self.theta_half_rad,
            "normalization_policy": self.normalization_policy,
            "baseline_policy": self.baseline_policy,
            "negative_feature_policy": self.negative_feature_policy,
            "population_policy": self.population_policy,
            "laterality_policy": self.laterality_policy,
            "latency_policy": self.latency_policy,
            "filter_policy": self.filter_policy,
            "stochastic_policy": self.stochastic_policy,
        }

    @property
    def sha256(self) -> str:
        """Stable identity of the complete encoder configuration."""

        return _sha256_json(self.to_dict())


@dataclass(frozen=True, slots=True)
class LevelPEncodingResult:
    """Immutable E1 features, schedule, and audit metadata."""

    samples: tuple[LoomingSample, ...]
    sample_times_s: tuple[float, ...]
    theta_rad: tuple[float, ...]
    angular_expansion_velocity_rad_per_s: tuple[float, ...]
    expanding: tuple[bool, ...]
    lc4_normalized: tuple[float, ...]
    lplc2_normalized: tuple[float, ...]
    lc4_drive_mv_eq: tuple[float, ...]
    lplc2_drive_mv_eq: tuple[float, ...]
    schedule: ExternalDriveSchedule
    metadata: MappingProxyType

    @property
    def config_sha256(self) -> str:
        return str(self.metadata["config_sha256"])

    @property
    def encoding_sha256(self) -> str:
        return str(self.metadata["encoding_sha256"])

    def to_summary_dict(self) -> dict[str, Any]:
        """Return JSON-compatible audit data without credentials."""

        result = dict(self.metadata)
        result.update(
            {
                "sample_times_s": list(self.sample_times_s),
                "theta_rad": list(self.theta_rad),
                "angular_expansion_velocity_rad_per_s": list(
                    self.angular_expansion_velocity_rad_per_s
                ),
                "expanding": list(self.expanding),
                "lc4_normalized": list(self.lc4_normalized),
                "lplc2_normalized": list(self.lplc2_normalized),
                "lc4_drive_mv_eq": list(self.lc4_drive_mv_eq),
                "lplc2_drive_mv_eq": list(self.lplc2_drive_mv_eq),
            }
        )
        return result


def _validate_graph(graph: SimulationGraph) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if not isinstance(graph, SimulationGraph):
        raise LevelPEncodingError("graph must be a Phase 2B SimulationGraph.")
    try:
        graph.validate_phase2b_scope()
    except SimulationGraphError as exc:
        raise LevelPEncodingError(str(exc)) from exc
    lc4_ids = tuple(node.body_id for node in graph.nodes if node.type == "LC4")
    lplc2_ids = tuple(node.body_id for node in graph.nodes if node.type == "LPLC2")
    if len(lc4_ids) != 126 or len(lplc2_ids) != 185:
        raise LevelPEncodingError(
            "Phase 2B graph must contain exactly 126 LC4 and 185 LPLC2 bodies."
        )
    if len(set(lc4_ids + lplc2_ids)) != 311:
        raise LevelPEncodingError("Visual population body IDs must be unique.")
    if any(
        node.type == "DNp01"
        for node in graph.nodes
        if node.body_id in lc4_ids + lplc2_ids
    ):
        raise LevelPEncodingError("DNp01 cannot be a Level P target.")
    return lc4_ids, lplc2_ids


def _validate_samples(
    samples: Sequence[LoomingSample], dt_ms: float
) -> tuple[LoomingSample, ...]:
    if isinstance(samples, (str, bytes)):
        raise LevelPEncodingError(
            "samples must be an ordered sequence of LoomingSample."
        )
    try:
        normalized = tuple(samples)
    except TypeError:
        raise LevelPEncodingError(
            "samples must be an ordered sequence of LoomingSample."
        ) from None
    if not normalized:
        raise LevelPEncodingError("samples must not be empty.")
    dt_s = dt_ms / 1000.0
    previous_time = -math.inf
    for index, sample in enumerate(normalized):
        if not isinstance(sample, LoomingSample):
            raise LevelPEncodingError("samples must contain LoomingSample values.")
        time_s = _finite_float(sample.time_s, f"samples[{index}].time_s")
        expected_time_s = index * dt_s
        if time_s <= previous_time:
            raise LevelPEncodingError("sample times must be strictly increasing.")
        if not math.isclose(
            time_s, expected_time_s, rel_tol=0.0, abs_tol=_TIME_TOLERANCE_S
        ):
            raise LevelPEncodingError(
                f"samples[{index}].time_s is not aligned to dt_ms={dt_ms!r}."
            )
        previous_time = time_s
        if not isinstance(sample.collided, bool):
            raise LevelPEncodingError(f"samples[{index}].collided must be boolean.")
        if sample.collided:
            raise LevelPEncodingError(
                f"samples[{index}] is a terminal collision sample and cannot be "
                "encoded."
            )
        if not isinstance(sample.approaching, bool):
            raise LevelPEncodingError(f"samples[{index}].approaching must be boolean.")
        if not isinstance(sample.center, VisualPoint):
            raise LevelPEncodingError(f"samples[{index}].center is invalid.")
        _finite_float(sample.center.azimuth_rad, f"samples[{index}].center.azimuth_rad")
        _finite_float(
            sample.center.elevation_rad, f"samples[{index}].center.elevation_rad"
        )
        distance = _finite_float(sample.distance_m, f"samples[{index}].distance_m")
        if distance <= 0.0:
            raise LevelPEncodingError(
                f"samples[{index}].distance_m must be positive pre-collision."
            )
        theta = _finite_float(
            sample.angular_size_rad, f"samples[{index}].angular_size_rad"
        )
        if theta < 0.0:
            raise LevelPEncodingError(
                f"samples[{index}].angular_size_rad cannot be negative."
            )
        if sample.angular_expansion_velocity_rad_s is None:
            raise LevelPEncodingError(
                f"samples[{index}] has no finite angular expansion velocity."
            )
        _finite_float(
            sample.angular_expansion_velocity_rad_s,
            f"samples[{index}].angular_expansion_velocity_rad_s",
        )
        if sample.time_to_collision_s is not None:
            _finite_float(
                sample.time_to_collision_s, f"samples[{index}].time_to_collision_s"
            )
    return normalized


def encode_level_p(
    *,
    samples: Sequence[LoomingSample],
    graph: SimulationGraph,
    config: LevelPEncoderConfig,
    dt_ms: float,
    stimulus_identity: str = "caller_supplied_samples_v1",
) -> LevelPEncodingResult:
    """Encode aligned pre-collision geometry into a Phase 2B drive schedule."""

    if not isinstance(config, LevelPEncoderConfig):
        raise LevelPEncodingError("config must be a LevelPEncoderConfig.")
    dt_ms = _finite_float(dt_ms, "dt_ms")
    if dt_ms <= 0.0:
        raise LevelPEncodingError("dt_ms must be greater than zero.")
    _non_empty_identifier(stimulus_identity, "stimulus_identity")
    lc4_ids, lplc2_ids = _validate_graph(graph)
    normalized_samples = _validate_samples(samples, dt_ms)

    sample_times_s: list[float] = []
    theta_rad: list[float] = []
    expansion_velocity: list[float] = []
    expanding: list[bool] = []
    lc4_features: list[float] = []
    lplc2_features: list[float] = []
    lc4_drive: list[float] = []
    lplc2_drive: list[float] = []

    for index, sample in enumerate(normalized_samples):
        time_s = float(sample.time_s)
        theta = float(sample.angular_size_rad)
        omega = float(sample.angular_expansion_velocity_rad_s)
        omega_plus = max(omega, 0.0)
        is_expanding = bool(sample.approaching and omega > 0.0)
        lc4_feature = _bounded_feature(omega_plus, config.omega_half_rad_per_s)
        lplc2_feature = (
            _bounded_feature(theta, config.theta_half_rad) if is_expanding else 0.0
        )
        lc4_value = config.lc4_gain_mv_eq * lc4_feature
        lplc2_value = config.lplc2_gain_mv_eq * lplc2_feature
        if not all(
            math.isfinite(value)
            for value in (lc4_feature, lplc2_feature, lc4_value, lplc2_value)
        ):
            raise LevelPEncodingError(
                f"Encoded values at sample {index} are not finite."
            )
        sample_times_s.append(time_s)
        theta_rad.append(theta)
        expansion_velocity.append(omega)
        expanding.append(is_expanding)
        lc4_features.append(lc4_feature)
        lplc2_features.append(lplc2_feature)
        lc4_drive.append(lc4_value)
        lplc2_drive.append(lplc2_value)

    by_body_id = {body_id: tuple(lc4_drive) for body_id in lc4_ids}
    by_body_id.update({body_id: tuple(lplc2_drive) for body_id in lplc2_ids})
    config_hash = config.sha256
    graph_identity = {
        "candidate_identifier": graph.candidate_identifier,
        "candidate_version": graph.candidate_version,
        "dataset": graph.dataset,
        "graph_scope_id": graph.graph_scope_id,
        "circuit_integrity": dict(graph.circuit_integrity),
        "body_ids": list(graph.body_ids),
        "neuron_types": list(graph.neuron_types),
        "neuron_sides": list(graph.neuron_sides),
    }
    encoding_identity = {
        "schema": ENCODING_SCHEMA,
        "config_sha256": config_hash,
        "dt_ms": dt_ms,
        "stimulus_identity": stimulus_identity,
        "samples": [sample.to_dict() for sample in normalized_samples],
        "graph": graph_identity,
    }
    encoding_hash = _sha256_json(encoding_identity)
    target_body_annotations = {
        neuron_type: [
            {"body_id": node.body_id, "soma_side": node.soma_side}
            for node in graph.nodes
            if node.type == neuron_type
        ]
        for neuron_type in ("LC4", "LPLC2")
    }
    schedule = ExternalDriveSchedule.from_body_ids(
        by_body_id,
        steps=len(normalized_samples),
        provenance_id=f"{ENCODER_ID}:{encoding_hash}",
    )
    metadata = MappingProxyType(
        {
            "schema": ENCODING_SCHEMA,
            "encoder_id": config.encoder_id,
            "encoder_version": config.encoder_version,
            "config": config.to_dict(),
            "config_sha256": config_hash,
            "encoding_sha256": encoding_hash,
            "stimulus_identity": stimulus_identity,
            "dt_ms": dt_ms,
            "sample_count": len(normalized_samples),
            "sample_start_s": sample_times_s[0],
            "sample_end_s": sample_times_s[-1],
            "lc4_body_count": len(lc4_ids),
            "lplc2_body_count": len(lplc2_ids),
            "visual_body_count": len(lc4_ids) + len(lplc2_ids),
            "target_body_ids": {
                "LC4": list(lc4_ids),
                "LPLC2": list(lplc2_ids),
            },
            "target_body_annotations": target_body_annotations,
            "candidate_identifier": graph.candidate_identifier,
            "candidate_version": graph.candidate_version,
            "dataset": graph.dataset,
            "graph_scope_id": graph.graph_scope_id,
            "circuit_integrity": dict(graph.circuit_integrity),
            "provenance": {
                "stimulus": "environment_geometry",
                "functional_evidence": "published_feature_association",
                "encoder": "neurofly_derived",
                "gains": "neurofly_free_parameter",
                "normalization_scales": "neurofly_free_parameter",
            },
        }
    )
    return LevelPEncodingResult(
        samples=normalized_samples,
        sample_times_s=tuple(sample_times_s),
        theta_rad=tuple(theta_rad),
        angular_expansion_velocity_rad_per_s=tuple(expansion_velocity),
        expanding=tuple(expanding),
        lc4_normalized=tuple(lc4_features),
        lplc2_normalized=tuple(lplc2_features),
        lc4_drive_mv_eq=tuple(lc4_drive),
        lplc2_drive_mv_eq=tuple(lplc2_drive),
        schedule=schedule,
        metadata=metadata,
    )


__all__ = [
    "BASELINE_POLICY",
    "ENCODER_ID",
    "ENCODER_VERSION",
    "ENCODING_SCHEMA",
    "FILTER_POLICY",
    "LATERALITY_POLICY",
    "LATENCY_POLICY",
    "LevelPEncoderConfig",
    "LevelPEncodingError",
    "LevelPEncodingResult",
    "NEGATIVE_FEATURE_POLICY",
    "NORMALIZATION_POLICY",
    "POPULATION_POLICY",
    "STOCHASTIC_POLICY",
    "encode_level_p",
]
