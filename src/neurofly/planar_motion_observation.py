"""Preregistered fixed-landmark geometry; no neural or body-state update."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from neurofly.orientation_to_horizontal_motion import SideDescriptors
from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

PREREGISTRATION_ID = "49e91a10fa49c5d7004f28249b63f334a0e23767c20108f5578a0e2586c9767a"
PREREGISTRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs/science/planar_steering_shadow_preregistration.json"
)
FRAME = "PLANAR_WORLD_EQ_X_RIGHT_Z_FORWARD"


def finite(value: object) -> bool:
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def load_preregistration(path: Path = PREREGISTRATION_PATH) -> dict:
    try:
        record = json.loads(Path(path).read_bytes())
        if (
            canonical_sha256(record) != PREREGISTRATION_ID
            or record["schema"] != "planar_steering_shadow_preregistration_v1"
            or record["stage_a"]["stage_b_permitted"] is not True
        ):
            raise ValueError("preregistration authority mismatch")
        return record
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ValueError("missing or modified planar observation authority") from exc


@dataclass(frozen=True, slots=True)
class PlanarObservationContract:
    contract_id: str = PREREGISTRATION_ID
    frame: str = FRAME
    period_eq: float = 1.0
    reference_window_ms: float = 50.0
    minimum_distance_world_eq: float = 1e-9

    def __post_init__(self):
        if (
            self.contract_id != PREREGISTRATION_ID
            or self.frame != FRAME
            or any(
                not finite(value) or value != expected
                for value, expected in (
                    (self.period_eq, 1),
                    (self.reference_window_ms, 50),
                    (self.minimum_distance_world_eq, 1e-9),
                )
            )
        ):
            raise ValueError("unsupported planar observation configuration")


@dataclass(frozen=True, slots=True)
class PoseBoundary:
    index: int
    time_ms: float
    x_world_eq: float
    z_world_eq: float
    heading_eq: float
    source: Literal["ENGINEERING_PRESCRIBED_POSE"] = "ENGINEERING_PRESCRIBED_POSE"

    def __post_init__(self):
        if type(self.index) is not int or self.index < 0:
            raise ValueError("invalid prescribed boundary index")
        if (
            any(
                not finite(v)
                for v in (
                    self.time_ms,
                    self.x_world_eq,
                    self.z_world_eq,
                    self.heading_eq,
                )
            )
            or self.time_ms < 0
            or self.source != "ENGINEERING_PRESCRIBED_POSE"
        ):
            raise ValueError("invalid prescribed pose/time/source")


@dataclass(frozen=True, slots=True)
class Landmark:
    id: str
    side: Literal["R", "L"]
    x_world_eq: float
    z_world_eq: float

    def __post_init__(self):
        if (
            type(self.id) is not str
            or not self.id.strip()
            or self.id != self.id.strip()
            or self.side not in ("R", "L")
            or not finite(self.x_world_eq)
            or not finite(self.z_world_eq)
        ):
            raise ValueError("invalid fixed landmark")


@dataclass(frozen=True, slots=True)
class VisualGeometry:
    landmarks: tuple[Landmark, Landmark]
    frame: str = FRAME

    def __post_init__(self):
        if (
            self.frame != FRAME
            or type(self.landmarks) is not tuple
            or len(self.landmarks) != 2
            or any(type(p) is not Landmark for p in self.landmarks)
            or {p.side for p in self.landmarks} != {"R", "L"}
            or len({p.id for p in self.landmarks}) != 2
            or len({(p.x_world_eq, p.z_world_eq) for p in self.landmarks}) != 2
        ):
            raise ValueError("require two distinct, named R/L fixed references")


@dataclass(frozen=True, slots=True)
class LandmarkMotion:
    landmark: Landmark
    world_bearing_before_rad_model: float
    world_bearing_after_rad_model: float
    world_bearing_shift_rad_model: float
    relative_shift_eq: float
    raw_motion_eq_per_ms: float
    normalized_side_descriptor: float
    bounded_side_descriptor: float
    clipped: bool


@dataclass(frozen=True, slots=True)
class SpatialObservation:
    contract_id: str
    before_index: int
    available_boundary_index: int
    dt_ms: float
    translation_increment_world_eq: tuple[float, float]
    heading_increment_eq: float
    prescribed_cause: str
    samples: tuple[LandmarkMotion, LandmarkMotion]
    sides: SideDescriptors

    def payload(self) -> dict:
        return asdict(self)


def observe_interval(
    geometry: VisualGeometry,
    before: PoseBoundary,
    after: PoseBoundary,
    *,
    contract: PlanarObservationContract | None = None,
) -> SpatialObservation:
    config = PlanarObservationContract() if contract is None else contract
    if type(config) is not PlanarObservationContract:
        raise ValueError("require typed planar observation contract")
    if type(geometry) is not VisualGeometry:
        raise ValueError("require typed fixed geometry")
    if (
        type(before) is not PoseBoundary
        or type(after) is not PoseBoundary
        or after.index != before.index + 1
    ):
        raise ValueError("require consecutive prescribed boundaries")
    dt = after.time_ms - before.time_ms
    dx, dz = after.x_world_eq - before.x_world_eq, after.z_world_eq - before.z_world_eq
    dh = after.heading_eq - before.heading_eq
    if not all(finite(v) for v in (dt, dx, dz, dh)) or dt <= 0:
        raise ValueError("invalid finite completed pose interval")
    if abs(dh) >= config.period_eq / 2:
        raise ValueError("ambiguous half-cycle heading interval")
    samples = []
    for landmark in sorted(geometry.landmarks, key=lambda p: p.side, reverse=True):
        bx, bz = (
            landmark.x_world_eq - before.x_world_eq,
            landmark.z_world_eq - before.z_world_eq,
        )
        ax, az = (
            landmark.x_world_eq - after.x_world_eq,
            landmark.z_world_eq - after.z_world_eq,
        )
        squared = dx * dx + dz * dz
        # Inspect the straight swept translation segment, not just endpoints.
        fraction = max(0.0, min(1.0, (bx * dx + bz * dz) / squared)) if squared else 0.0
        nearest = math.hypot(bx - fraction * dx, bz - fraction * dz)
        if not all(finite(v) for v in (bx, bz, ax, az, squared, nearest)):
            raise ValueError("non-finite geometric projection")
        if nearest <= config.minimum_distance_world_eq:
            raise ValueError("singular landmark/swept pose geometry")
        cross, dot = bz * ax - bx * az, bx * ax + bz * az
        if not finite(cross) or not finite(dot):
            raise ValueError("bearing arithmetic overflow")
        world_shift = math.atan2(cross, dot)
        shift_eq = world_shift / math.tau - dh
        if abs(world_shift) >= math.pi or abs(shift_eq) >= config.period_eq / 2:
            raise ValueError("ambiguous relative bearing interval")
        raw = shift_eq / dt
        normalized = (
            config.reference_window_ms * raw * (1 if landmark.side == "R" else -1)
        )
        if not finite(raw) or not finite(normalized):
            raise ValueError("invalid motion normalization; never clip invalid values")
        bounded = max(-1.0, min(1.0, normalized))
        samples.append(
            LandmarkMotion(
                landmark,
                math.atan2(bx, bz),
                math.atan2(ax, az),
                world_shift,
                shift_eq,
                raw,
                normalized,
                bounded,
                bounded != normalized,
            )
        )
    translation, rotation = (dx != 0 or dz != 0), dh != 0
    cause = (
        "MIXED"
        if translation and rotation
        else "TRANSLATION"
        if translation
        else "ROTATION"
        if rotation
        else "STATIONARY"
    )
    return SpatialObservation(
        config.contract_id,
        before.index,
        after.index,
        dt,
        (dx, dz),
        dh,
        cause,
        tuple(samples),
        SideDescriptors(
            samples[0].bounded_side_descriptor, samples[1].bounded_side_descriptor
        ),
    )
