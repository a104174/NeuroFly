"""Phase 12B: synthetic-fixture, model-space kinematics, not biomechanics."""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass

from neurofly.ttm_actuator import ARTIFACT_SCHEMA as SOURCE_ARTIFACT_SCHEMA
from neurofly.ttm_actuator import RESULT_SCHEMA as SOURCE_RESULT_SCHEMA
from neurofly.ttm_actuator import validate_config as validate_routing_config
from neurofly.ttm_actuator_artifacts import DEFAULT_ARTIFACT_ROOT as SOURCE_ROOT
from neurofly.ttm_actuator_artifacts import replay_command_artifact
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

MODEL_SCHEMA = "exploratory_planar_body_plant_v1"
RESULT_SCHEMA = "exploratory_planar_body_plant_result_v1"
ARTIFACT_SCHEMA = "exploratory_planar_body_plant_artifact_v1"
PROVENANCE = "EXPLORATORY_PLANAR_BODY_PLANT"
SOURCE_ID = "478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40"
DEFAULT_SOURCE_ARTIFACT = SOURCE_ROOT / SOURCE_ID
FIXTURE_IDS = (
    "ZERO_EVENT_CONTROL",
    "RIGHT_SINGLE_EVENT",
    "LEFT_SINGLE_EVENT",
    "BILATERAL_SIMULTANEOUS_EVENT",
    "RIGHT_REPEATED_EVENTS",
    "LEFT_REPEATED_EVENTS",
)
EXCLUSIONS = (
    "SYNTHETIC_MECHANICS_VALIDATION_NOT_CONNECTOME_DRIVEN_MOVEMENT",
    "UNCALIBRATED_WORLD_EQ_NOT_PHYSICAL_DISPLACEMENT_OR_SPEED",
    "NO_INERTIA_ACCELERATION_GRAVITY_CONTACT_OR_ARENA",
    "NO_STEERING_OR_ARTICULATED_GEOMETRY",
    "NO_SCENARIO_FRONTEND_OR_PRODUCTION_PATH_COMPOSITION",
    "NO_EMPIRICAL_FITTING_OR_UPSTREAM_RETUNING",
)
SEMANTICS = {
    "schema_version": MODEL_SCHEMA,
    "source_result_schema": SOURCE_RESULT_SCHEMA,
    "coordinate_convention": "PLANAR_WORLD_EQ_POSITIVE_X_RIGHT_POSITIVE_Z_FORWARD",
    "fixed_heading": "POSITIVE_Z",
    "position_units": "world_eq",
    "speed_units": "world_eq_per_ms",
    "common_mode_semantics": "ARITHMETIC_MEAN_RIGHT_AND_LEFT_COMMAND",
    "update_semantics": "LEFT_BOUNDARY_COMMAND_HOLDS_OVER_NEXT_INTERVAL",
    "final_boundary_semantics": "NO_OUTGOING_INTERVAL_NO_EXTRA_INTEGRATION",
    "diagnostic_indexing": "INTERVAL_N_FROM_BOUNDARY_N_TO_N_PLUS_1",
    "state_ownership": "BACKEND_SIMULATION_AUTHORITATIVE",
    "validation_kind": "SYNTHETIC_MECHANICS_VALIDATION",
    "parameter_classifications": {
        "motion_gain_world_eq_per_ms": "MODEL_ASSUMPTION",
        "initial_x_world_eq": "MODEL_ASSUMPTION",
        "initial_z_world_eq": "MODEL_ASSUMPTION",
        "common_mode_mapping": "MODEL_ASSUMPTION",
        "fixed_heading": "MODEL_ASSUMPTION",
    },
    "scientific_exclusions": list(EXCLUSIONS),
}


def _finite(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


@dataclass(frozen=True, slots=True)
class PlantConfig:
    """One assumed speed gain plus deterministic reset coordinates."""

    motion_gain_world_eq_per_ms: float
    initial_x_world_eq: float = 0.0
    initial_z_world_eq: float = 0.0

    def __post_init__(self) -> None:
        if (
            not _finite(self.motion_gain_world_eq_per_ms)
            or self.motion_gain_world_eq_per_ms <= 0
            or not _finite(self.initial_x_world_eq)
            or not _finite(self.initial_z_world_eq)
        ):
            raise ValueError(
                "require positive finite motion gain and finite reset state"
            )

    def payload(self) -> dict:
        return {
            **copy.deepcopy(SEMANTICS),
            "motion_gain_world_eq_per_ms": float(self.motion_gain_world_eq_per_ms),
            "initial_x_world_eq": float(self.initial_x_world_eq),
            "initial_z_world_eq": float(self.initial_z_world_eq),
        }

    @classmethod
    def from_payload(cls, payload: dict) -> PlantConfig:
        try:
            config = cls(
                payload["motion_gain_world_eq_per_ms"],
                payload["initial_x_world_eq"],
                payload["initial_z_world_eq"],
            )
        except (KeyError, TypeError) as exc:
            raise ValueError("malformed plant config") from exc
        if canonical_json_bytes(payload) != canonical_json_bytes(config.payload()):
            raise ValueError("plant config/schema/coordinate/update semantics changed")
        return config


def reference_config() -> PlantConfig:
    """Unit model-speed normalization, independent of biology and asset scale."""
    return PlantConfig(1.0)


def body_interval_step(
    x: float, z: float, dt: float, speed: float
) -> tuple[float, float]:
    """Shared model-space interval integration; velocity is not persistent state."""
    return x, z + dt * speed


def common_mode_speed(
    right: float, left: float, config: PlantConfig
) -> tuple[float, float]:
    """Exact arithmetic common mode, without differential steering."""
    common = (right + left) / 2
    return common, config.motion_gain_world_eq_per_ms * common


def integrate_commands(
    times: list[float], right: list[float], left: list[float], config: PlantConfig
) -> dict:
    """Pure finite-grid kinematics, also usable with controlled test-local inputs.

    The last command is validated but never applied without an outgoing interval.
    Velocity is an algebraic interval diagnostic, not dynamical state.
    """
    if (
        not isinstance(times, list)
        or len(times) < 2
        or any(not _finite(t) for t in times)
        or times[0] != 0
        or any(b <= a for a, b in zip(times[:-1], times[1:], strict=True))
    ):
        raise ValueError("require finite increasing source times starting at zero")
    for commands in (right, left):
        if (
            not isinstance(commands, list)
            or len(commands) != len(times)
            or any(not _finite(a) or not 0 <= a <= 1 for a in commands)
        ):
            raise ValueError("require one finite [0,1] command per source boundary")
    common = [
        common_mode_speed(right_value, left_value, config)[0]
        for right_value, left_value in zip(right[:-1], left[:-1], strict=True)
    ]
    speed = [config.motion_gain_world_eq_per_ms * c for c in common]
    z = [float(config.initial_z_world_eq)]
    for n, v in enumerate(speed):
        z.append(
            body_interval_step(
                config.initial_x_world_eq, z[-1], times[n + 1] - times[n], v
            )[1]
        )
    if any(not _finite(v) for v in (*speed, *z)):
        raise ValueError("nonfinite plant speed/position")
    return {
        "x_world_eq": [float(config.initial_x_world_eq)] * len(times),
        "z_world_eq": z,
        "common_mode_drive": common,
        "forward_speed_world_eq_per_ms": speed,
    }


def transform_commands(source: dict, config: PlantConfig) -> dict:
    """Consume a replayed canonical actuator result; never read upstream drivers."""
    try:
        ch, rh = canonical_sha256(source["config"]), canonical_sha256(source["result"])
        if (
            source["artifact_id"] != SOURCE_ID
            or source["schema_version"] != SOURCE_RESULT_SCHEMA
            or source["result"]["schema_version"] != SOURCE_RESULT_SCHEMA
            or source["config_sha256"] != ch
            or source["result_sha256"] != rh
            or SOURCE_ID != canonical_sha256([SOURCE_ARTIFACT_SCHEMA, ch, rh])
            or source["config"]["provenance_kind"] != "EXPLORATORY_TTM_ACTUATOR_COMMAND"
        ):
            raise ValueError("canonical Phase 11B identity/schema/provenance changed")
        validate_routing_config(source["config"]["adapter"])
        grid, times = source["result"]["boundary_indices"], source["result"]["time_ms"]
        if (
            grid != list(range(81))
            or any(type(n) is not int for n in grid)
            or times != [n * 0.1 for n in grid]
        ):
            raise ValueError("canonical actuator grid changed")
        fixtures = source["result"]["fixtures"]
        if tuple(f["fixture_id"] for f in fixtures) != FIXTURE_IDS:
            raise ValueError("canonical actuator fixture set/order changed")
        configuration = {
            "model": config.payload(),
            "provenance_kind": PROVENANCE,
            "source_phase11b": {
                "artifact_id": SOURCE_ID,
                "schema_version": SOURCE_RESULT_SCHEMA,
                "config_sha256": ch,
                "result_sha256": rh,
            },
        }
        config_hash = canonical_sha256(configuration)
        output, seen = [], set()
        for fixture in fixtures:
            rows = fixture["instances"]
            identities = [
                (
                    r["source_body_id"],
                    r["source_side"],
                    r["actuator_id"],
                    r["actuator_side"],
                )
                for r in rows
            ]
            if identities != [
                (800146, "R", "RIGHT_TTM_ACTUATOR", "R"),
                (804642, "L", "LEFT_TTM_ACTUATOR", "L"),
            ]:
                raise ValueError("missing/duplicate/cross-routed actuator channel")
            ancestors = []
            for row in rows:
                tid = row["trajectory_id"]
                unhashed = {k: v for k, v in row.items() if k != "trajectory_id"}
                if (
                    tid in seen
                    or tid != canonical_sha256(unhashed)
                    or row["config_id"] != ch
                    or not row["proxy_domain_id"]
                ):
                    raise ValueError("actuator trajectory identity/ancestry mismatch")
                seen.add(tid)
                ancestors.append(
                    {
                        "source_actuator_trajectory_id": tid,
                        "source_actuator_trajectory_sha256": canonical_sha256(row),
                        **{
                            k: copy.deepcopy(row[k])
                            for k in (
                                "source_body_id",
                                "source_side",
                                "actuator_id",
                                "actuator_side",
                                "routing_id",
                                "proxy_domain_id",
                                "proxy_source_mapping_id",
                                "source_activation_trajectory_id",
                                "provenance_chain",
                            )
                        },
                    }
                )
            samples = integrate_commands(
                times, rows[0]["actuator_command"], rows[1]["actuator_command"], config
            )
            payload = {
                "fixture_id": fixture["fixture_id"],
                "source_actuators": ancestors,
                "config_id": config_hash,
                "provenance_chain": ["EXPLORATORY_TTM_ACTUATOR_COMMAND", PROVENANCE],
                "initial_state": {
                    "x_world_eq": float(config.initial_x_world_eq),
                    "z_world_eq": float(config.initial_z_world_eq),
                },
                **samples,
                "summary": {
                    "final_x_world_eq": samples["x_world_eq"][-1],
                    "final_z_world_eq": samples["z_world_eq"][-1],
                    "total_forward_displacement_world_eq": (
                        samples["z_world_eq"][-1] - config.initial_z_world_eq
                    ),
                    "maximum_forward_speed_world_eq_per_ms": max(
                        samples["forward_speed_world_eq_per_ms"]
                    ),
                    "nonzero_speed_interval_count": sum(
                        v > 0 for v in samples["forward_speed_world_eq_per_ms"]
                    ),
                },
            }
            output.append({"trajectory_id": canonical_sha256(payload), **payload})
        result = {
            "schema_version": RESULT_SCHEMA,
            "boundary_indices": list(grid),
            "time_ms": list(times),
            "interval_start_boundary_indices": list(grid[:-1]),
            "fixtures": output,
            "trajectory_count": len(output),
            "sample_count": len(output) * len(grid),
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
        raise ValueError("malformed actuator source") from exc


def build_plant(
    config: PlantConfig, *, source_artifact=DEFAULT_SOURCE_ARTIFACT
) -> dict:
    return transform_commands(replay_command_artifact(source_artifact), config)


def validate_plant(payload: dict, **sources) -> dict:
    try:
        config = PlantConfig.from_payload(payload["config"]["model"])
    except (KeyError, TypeError) as exc:
        raise ValueError("malformed body plant result") from exc
    expected = build_plant(config, **sources)
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError("body plant source/config/result differs from offline replay")
    return expected
