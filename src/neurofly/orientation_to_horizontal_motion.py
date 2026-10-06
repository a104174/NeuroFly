"""Geometric observation of a completed interval; no neural/body execution.

Coordinates and side bases are exploratory, not calibrated retinal imagery.
The caller owns the world and both unwrapped orientation endpoints.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

CONTRACT_SCHEMA = "orientation_to_horizontal_motion_contract_v1"
CONTRACT_ID = "9e58649144a4cf3ca7cd913a6cf91dde116524906b0c600dd09f5e66ec5ffaad"
CONTRACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs/science/orientation_to_horizontal_motion_contract.json"
)


class ObservationErrorCode(StrEnum):
    INVALID_COORDINATE = "INVALID_COORDINATE"
    INVALID_TIME_INTERVAL = "INVALID_TIME_INTERVAL"
    INVALID_BOUNDARY_ORDER = "INVALID_BOUNDARY_ORDER"
    INVALID_WORLD_REFERENCE = "INVALID_WORLD_REFERENCE"
    AMBIGUOUS_OR_DISCONTINUOUS_INTERVAL = "AMBIGUOUS_OR_DISCONTINUOUS_INTERVAL"
    CONTRACT_AUTHORITY_MISMATCH = "CONTRACT_AUTHORITY_MISMATCH"


class ObservationError(ValueError):
    def __init__(self, code: ObservationErrorCode, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


def _finite(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


@dataclass(frozen=True, slots=True)
class ObservationContract:
    contract_id: str
    period_eq: float
    reference_window_ms: float
    right_basis: int
    left_basis: int

    def __post_init__(self):
        if (
            self.contract_id != CONTRACT_ID
            or not _finite(self.period_eq)
            or self.period_eq != 1
            or not _finite(self.reference_window_ms)
            or self.reference_window_ms != 50
            or type(self.right_basis) is not int
            or self.right_basis != 1
            or type(self.left_basis) is not int
            or self.left_basis != -1
        ):
            raise ObservationError(
                ObservationErrorCode.CONTRACT_AUTHORITY_MISMATCH,
                "normalization/period/side bases must match the frozen contract",
            )


def load_contract(path: Path = CONTRACT_PATH) -> ObservationContract:
    try:
        record = json.loads(Path(path).read_bytes())
        if (
            canonical_sha256(record) != CONTRACT_ID
            or record["schema"] != CONTRACT_SCHEMA
            or record["stage_a"]["decision"]
            != "ORIENTATION_TO_MOTION_OBSERVATION_IDENTIFIABLE"
            or record["stage_a"]["stage_b_permitted"] is not True
        ):
            raise ValueError("identity or Stage A mismatch")
        return ObservationContract(
            CONTRACT_ID,
            record["coordinates"]["period_eq"],
            record["operator"]["reference_window_ms"],
            1,
            -1,
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ObservationError(
            ObservationErrorCode.CONTRACT_AUTHORITY_MISMATCH,
            "missing, malformed or modified observation authority",
        ) from exc


@dataclass(frozen=True, slots=True)
class WorldReference:
    reference_id: str
    heading_eq: float
    schema: Literal["orientation_observation_world_state_v1"] = (
        "orientation_observation_world_state_v1"
    )

    def __post_init__(self):
        if (
            type(self.reference_id) is not str
            or not self.reference_id.strip()
            or self.reference_id != self.reference_id.strip()
            or not _finite(self.heading_eq)
            or self.schema != "orientation_observation_world_state_v1"
        ):
            raise ObservationError(
                ObservationErrorCode.INVALID_WORLD_REFERENCE,
                "require a named finite independent world reference",
            )


@dataclass(frozen=True, slots=True)
class OrientationBoundary:
    index: int
    time_ms: float
    yaw_orientation_eq: float

    def __post_init__(self):
        if type(self.index) is not int or self.index < 0:
            raise ObservationError(
                ObservationErrorCode.INVALID_BOUNDARY_ORDER,
                "boundary index must be a nonnegative integer",
            )
        if not _finite(self.time_ms) or self.time_ms < 0:
            raise ObservationError(
                ObservationErrorCode.INVALID_TIME_INTERVAL,
                "scientific time must be finite and nonnegative",
            )
        if not _finite(self.yaw_orientation_eq):
            raise ObservationError(
                ObservationErrorCode.INVALID_COORDINATE,
                "orientation must be a finite unwrapped model coordinate",
            )


@dataclass(frozen=True, slots=True)
class ObservationInterval:
    world: WorldReference
    before: OrientationBoundary
    after: OrientationBoundary

    def __post_init__(self):
        if type(self.world) is not WorldReference:
            raise ObservationError(
                ObservationErrorCode.INVALID_WORLD_REFERENCE,
                "world must use the typed world-reference schema",
            )
        if (
            type(self.before) is not OrientationBoundary
            or type(self.after) is not OrientationBoundary
            or self.after.index != self.before.index + 1
        ):
            raise ObservationError(
                ObservationErrorCode.INVALID_BOUNDARY_ORDER,
                "observe consecutive authoritative boundaries only",
            )
        dt = self.after.time_ms - self.before.time_ms
        if not _finite(dt) or dt <= 0:
            raise ObservationError(
                ObservationErrorCode.INVALID_TIME_INTERVAL,
                "completed interval must have positive finite duration",
            )


@dataclass(frozen=True, slots=True)
class SideDescriptors:
    right: float
    left: float
    units: Literal["horizontal_motion_eq"] = "horizontal_motion_eq"


@dataclass(frozen=True, slots=True)
class ObservationUnits:
    body: Literal["yaw_orientation_eq"] = "yaw_orientation_eq"
    world: Literal["world_heading_eq"] = "world_heading_eq"
    view: Literal["relative_view_eq"] = "relative_view_eq"
    displacement: Literal["horizontal_view_shift_eq"] = "horizontal_view_shift_eq"
    raw_motion: Literal["relative_view_eq_per_ms"] = "relative_view_eq_per_ms"
    normalized: Literal["horizontal_motion_eq"] = "horizontal_motion_eq"


@dataclass(frozen=True, slots=True)
class HorizontalMotionObservation:
    contract_id: str
    interval: ObservationInterval
    available_boundary_index: int
    dt_ms: float
    relative_lift_before_eq: float
    relative_lift_after_eq: float
    relative_view_before_eq: float
    relative_view_after_eq: float
    horizontal_view_shift_eq: float
    raw_view_motion_eq_per_ms: float
    normalized_unclipped: float
    global_horizontal_motion_eq: float
    sides: SideDescriptors
    clipped: bool
    units: ObservationUnits = ObservationUnits()
    schema: Literal["horizontal_motion_observation_v1"] = (
        "horizontal_motion_observation_v1"
    )
    status: Literal["EXPLORATORY_GEOMETRIC_OBSERVATION_NOT_VISUAL_TRANSDUCTION"] = (
        "EXPLORATORY_GEOMETRIC_OBSERVATION_NOT_VISUAL_TRANSDUCTION"
    )

    def payload(self) -> dict:
        return asdict(self)

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.payload())

    def result_sha256(self) -> str:
        return canonical_sha256(self.payload())


def neutral_initial_descriptors() -> SideDescriptors:
    """No prior interval at boundary zero; never infer motion from an offset."""
    return SideDescriptors(0.0, 0.0)


def _wrap(value: float, period: float) -> float:
    # Remainder avoids subtracting large winding counts; maps +half to -half.
    half = period / 2
    wrapped = math.remainder(value, period)
    if wrapped >= half:
        wrapped -= period
    return 0.0 if wrapped == 0 else wrapped


def observe_interval(
    interval: ObservationInterval, *, contract: ObservationContract | None = None
) -> HorizontalMotionObservation:
    """Completed interval [n-1,n] -> latched input for [n,n+1], not a loop.

    Wrap only the view representation. Difference continuous, unwrapped body
    endpoints so a seam crossing cannot generate a false full-cycle signal.
    """
    config = load_contract() if contract is None else contract
    if type(config) is not ObservationContract:
        raise ObservationError(
            ObservationErrorCode.CONTRACT_AUTHORITY_MISMATCH,
            "require the typed frozen observation contract",
        )
    if type(interval) is not ObservationInterval:
        raise ObservationError(
            ObservationErrorCode.INVALID_BOUNDARY_ORDER, "require a typed interval"
        )
    before, after, world = interval.before, interval.after, interval.world
    increment = after.yaw_orientation_eq - before.yaw_orientation_eq
    if not _finite(increment) or abs(increment) >= config.period_eq / 2:
        raise ObservationError(
            ObservationErrorCode.AMBIGUOUS_OR_DISCONTINUOUS_INTERVAL,
            "require a continuous unwrapped increment strictly below half a cycle",
        )
    r0 = world.heading_eq - before.yaw_orientation_eq
    r1 = world.heading_eq - after.yaw_orientation_eq
    if not _finite(r0) or not _finite(r1):
        raise ObservationError(
            ObservationErrorCode.INVALID_COORDINATE, "relative coordinate overflow"
        )
    dt = after.time_ms - before.time_ms
    displacement = 0.0 if increment == 0 else -increment
    raw = displacement / dt
    normalized = config.reference_window_ms * raw / config.period_eq
    if not _finite(raw) or not _finite(normalized):
        raise ObservationError(
            ObservationErrorCode.INVALID_COORDINATE,
            "rate/normalization overflow; invalid values are never saturated",
        )
    bounded = max(-1.0, min(1.0, normalized))
    sides = SideDescriptors(config.right_basis * bounded, config.left_basis * bounded)
    return HorizontalMotionObservation(
        config.contract_id,
        interval,
        after.index,
        dt,
        r0,
        r1,
        _wrap(r0, config.period_eq),
        _wrap(r1, config.period_eq),
        displacement,
        raw,
        normalized,
        bounded,
        sides,
        bounded != normalized,
    )


def validate_observation(observation: HorizontalMotionObservation) -> None:
    """Reconstruct from typed geometry; a rewritten result hash is insufficient."""
    if (
        type(observation) is not HorizontalMotionObservation
        or observation.canonical_bytes()
        != observe_interval(observation.interval).canonical_bytes()
    ):
        raise ObservationError(
            ObservationErrorCode.CONTRACT_AUTHORITY_MISMATCH,
            "observation differs from frozen geometric reconstruction",
        )
