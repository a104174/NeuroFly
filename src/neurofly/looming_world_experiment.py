"""Frozen model-design contract for a separate longer closed-loop experiment.

No outcome-dependent design, alternative parameter interface, or neural equation.
"""

import json
import math
from pathlib import Path

from neurofly.closed_loop_scenario import (
    TICK_SEMANTICS,
    load_scenario_sources,
    project_world,
    run_closed_loop_scenario,
)
from neurofly.closed_loop_scenario_artifacts import replay_scenario_artifact
from neurofly.relative_column_assignment import DEFAULT_SOURCE_ROOT
from neurofly.ttm_g1_electrophysiology_observations import (
    canonical_json_bytes,
    canonical_sha256,
)

KIND = "LOOMING_WORLD_EXPERIMENT"
CONFIG_SCHEMA = "looming_world_experiment_config_v1"
RESULT_SCHEMA = "looming_world_experiment_result_v1"
ARTIFACT_SCHEMA = "looming_world_experiment_artifact_v1"
PREREGISTRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs/science/looming_world_experiment_preregistration.json"
)
PREREGISTRATION_ID = "580e088d89b38f086689c39568bf38bd04f5edf7f0d05065abe2c076a0d16bed"


def load_preregistration(path=PREREGISTRATION_PATH):
    contract = json.loads(Path(path).read_bytes())
    if canonical_sha256(contract) != PREREGISTRATION_ID:
        raise ValueError("frozen preregistration identity mismatch")
    return contract


class WorldExperimentConfig:
    """Only the frozen contract can create scientific configuration."""

    def __init__(self):
        self._contract = load_preregistration()
        self.kind = self._contract["scenario_kind"]
        self.dt_ms = self._contract["dt_ms"]
        self.interval_count = self._contract["interval_count"]
        self.body_x_world_eq = self._contract["body_initial"]["x_world_eq"]
        self.body_z_world_eq = self._contract["body_initial"]["z_world_eq"]
        for key, value in self._contract["object"].items():
            setattr(self, key, value)
        if self._contract["tick_semantics"] != TICK_SEMANTICS:
            raise ValueError("unsupported frozen causal semantics")

    def payload(self):
        # Read a fresh, validated contract: callers cannot mutate a cached dict.
        contract = load_preregistration()
        return {
            "schema_version": CONFIG_SCHEMA,
            "scenario_kind": contract["scenario_kind"],
            "dt_ms": contract["dt_ms"],
            "interval_count": contract["interval_count"],
            "body_initial": contract["body_initial"],
            "stimulus_enabled": True,
            "object": contract["object"],
            "projection": contract["projection"],
            "tick_semantics": contract["tick_semantics"],
            "preregistration_id": PREREGISTRATION_ID,
            "preregistration": contract,
        }


def geometry_termination(config, body, object_position, step):
    """Check authoritative state before exposure; never clamp invalid geometry."""
    reason = None
    try:
        geometry = project_world(config, body, object_position)
        margin = config.payload()["preregistration"]["termination"][
            "minimum_forward_separation_radii"
        ]
        if geometry["relative_z_world_eq"] <= margin * config.radius_world_eq:
            reason = "FORWARD_SEPARATION_AT_OR_BELOW_ONE_OBJECT_RADIUS"
    except ValueError:
        reason = "UNSUPPORTED_PROJECTION_GEOMETRY"
    if reason is None:
        return None
    if not all(math.isfinite(v) for v in (*body, *object_position)):
        # Nonfinite states cannot be serialized as canonical scientific JSON.
        raise ValueError("nonfinite authoritative world state")
    return {
        "status": "TERMINATED_GEOMETRY_DOMAIN",
        "step": step,
        "time_ms": step * config.dt_ms,
        "reason": reason,
        "attempted_boundary_state": {
            "body": {"x_world_eq": body[0], "z_world_eq": body[1]},
            "object": {
                "x_world_eq": object_position[0],
                "z_world_eq": object_position[1],
            },
        },
    }


def run_world_experiment(sources=None):
    config = WorldExperimentConfig()
    sources = load_scenario_sources() if sources is None else sources
    if (
        canonical_sha256(sources["identity"])
        != config._contract["source_model_identity_sha256"]
    ):
        raise ValueError("frozen scientific model identity mismatch")
    return run_closed_loop_scenario(
        config,
        sources,
        geometry_guard=geometry_termination,
        result_schema=RESULT_SCHEMA,
    )


def build_world_experiment():
    contract = load_preregistration()
    historical = replay_scenario_artifact(
        DEFAULT_SOURCE_ROOT
        / "closed_loop_scenario_artifact_v1"
        / contract["source_phase13b_artifact_id"]
    )
    if historical["artifact_id"] != contract["source_phase13b_artifact_id"]:
        raise ValueError("historical source identity mismatch")
    run = run_world_experiment()
    config, result = run["config"], run["result"]
    ch, rh = canonical_sha256(config), canonical_sha256(result)
    return {
        "schema_version": ARTIFACT_SCHEMA,
        "config": config,
        "result": result,
        "config_sha256": ch,
        "result_sha256": rh,
        "artifact_id": canonical_sha256([ARTIFACT_SCHEMA, ch, rh]),
    }


def validate_world_experiment(payload):
    expected = build_world_experiment()
    if canonical_json_bytes(payload) != canonical_json_bytes(expected):
        raise ValueError("world experiment differs from frozen offline replay")
    return expected
