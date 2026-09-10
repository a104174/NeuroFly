"""Model-neutral geometry for a reproducible looming stimulus.

This module describes physical/visual variables only. It does not produce
neural current, spikes, rates, membrane state, or motor output.
"""

import math
from dataclasses import asdict, dataclass
from typing import Any

from neurofly.malecns.errors import StimulusSpecificationError


def _finite(value: float, field_name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise StimulusSpecificationError(f"{field_name} must be finite and numeric.")
    if not math.isfinite(float(value)):
        raise StimulusSpecificationError(f"{field_name} must be finite and numeric.")
    return float(value)


@dataclass(frozen=True)
class VisualPoint:
    """A stimulus center in angular visual coordinates, measured in radians."""

    azimuth_rad: float
    elevation_rad: float

    def __post_init__(self) -> None:
        _finite(self.azimuth_rad, "azimuth_rad")
        _finite(self.elevation_rad, "elevation_rad")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LoomingSample:
    """Geometric stimulus state at one time; no neural interpretation."""

    time_s: float
    distance_m: float
    time_to_collision_s: float | None
    angular_size_rad: float
    angular_expansion_velocity_rad_s: float | None
    center: VisualPoint
    approaching: bool
    collided: bool

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["center"] = self.center.to_dict()
        return result


@dataclass(frozen=True)
class LoomingStimulus:
    """A spherical/disk object on a straight line of sight.

    ``object_radius_m`` is the physical radius (half-size) and
    ``approach_velocity_m_s`` is positive toward the observer. Angular size is
    the full visual diameter. Geometry is defined only before collision; at and
    after collision the sample is an explicit terminal state.
    """

    object_radius_m: float
    approach_velocity_m_s: float
    initial_distance_m: float
    center: VisualPoint

    def __post_init__(self) -> None:
        radius = _finite(self.object_radius_m, "object_radius_m")
        distance = _finite(self.initial_distance_m, "initial_distance_m")
        _finite(self.approach_velocity_m_s, "approach_velocity_m_s")
        if radius <= 0:
            raise StimulusSpecificationError("object_radius_m must be positive.")
        if distance <= 0:
            raise StimulusSpecificationError("initial_distance_m must be positive.")

    @property
    def time_to_collision_s(self) -> float | None:
        if self.approach_velocity_m_s > 0:
            return self.initial_distance_m / self.approach_velocity_m_s
        return None

    def sample(self, time_s: float) -> LoomingSample:
        """Evaluate deterministic pre-collision looming geometry at ``time_s``."""
        time = _finite(time_s, "time_s")
        if time < 0:
            raise StimulusSpecificationError("time_s must not be negative.")

        collision_time = self.time_to_collision_s
        if collision_time is not None and time >= collision_time:
            return LoomingSample(
                time_s=time,
                distance_m=0.0,
                time_to_collision_s=collision_time,
                angular_size_rad=math.pi,
                angular_expansion_velocity_rad_s=None,
                center=self.center,
                approaching=True,
                collided=True,
            )

        distance = self.initial_distance_m - self.approach_velocity_m_s * time
        angular_size = 2.0 * math.atan2(self.object_radius_m, distance)
        expansion_velocity = (
            2.0
            * self.object_radius_m
            * self.approach_velocity_m_s
            / (distance * distance + self.object_radius_m**2)
        )
        return LoomingSample(
            time_s=time,
            distance_m=distance,
            time_to_collision_s=collision_time,
            angular_size_rad=angular_size,
            angular_expansion_velocity_rad_s=expansion_velocity,
            center=self.center,
            approaching=self.approach_velocity_m_s > 0,
            collided=False,
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["center"] = self.center.to_dict()
        return result
