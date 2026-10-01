"""Compact product transport over replay-validated Phase 13B data, never a model."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from neurofly.closed_loop_scenario import scenario_metadata
from neurofly.closed_loop_scenario_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    replay_scenario_artifact,
)

CANONICAL_SCENARIO_ARTIFACT_ID = (
    "55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b"
)
DEFAULT_SCENARIO_PATH = DEFAULT_ARTIFACT_ROOT / CANONICAL_SCENARIO_ARTIFACT_ID
ScenarioKind = Literal["BASELINE_CONTROL", "LOOMING_CIRCUIT_VALIDATION"]


class TransportModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ScenarioDefinition(TransportModel):
    id: ScenarioKind
    scenario_kind: ScenarioKind
    title: str
    description: str
    availability: Literal["CANONICAL_PRESET"] = "CANONICAL_PRESET"
    preset_only: Literal[True] = True
    scientific_caveat: str


def scenario_catalog() -> list[ScenarioDefinition]:
    caveat = (
        "Uncalibrated model-space execution; fixed relative-column projection, "
        "not registered retinal geometry or biological escape. Current genuine "
        "model produces no movement. Canonical presets only."
    )
    return [
        ScenarioDefinition(
            id=item["id"],
            scenario_kind=item["id"],
            title=item["title"],
            description=item["description"],
            scientific_caveat=caveat,
        )
        for item in scenario_metadata()
    ]


class BodySnapshot(TransportModel):
    x_world_eq: float
    z_world_eq: float
    fixed_heading: Literal["POSITIVE_Z"]


class ObjectSnapshot(TransportModel):
    x_world_eq: float
    z_world_eq: float
    radius_world_eq: float


class SensorySummary(TransportModel):
    neuron_type: Literal["LC4", "LPLC2"]
    side: Literal["R", "L"]
    state_sum: float


class ActuatorSnapshot(TransportModel):
    RIGHT_TTM_ACTUATOR: float
    LEFT_TTM_ACTUATOR: float


class ScenarioPlaybackFrame(TransportModel):
    step: int
    time_ms: float
    body: BodySnapshot
    object: ObjectSnapshot | None
    relative_distance_world_eq: float | None
    lattice_radius: int | None
    active_sensory_body_count: int
    sensory_summaries: list[SensorySummary]
    dnp01_membrane_mv: list[float]
    dnp01_spike_body_ids: list[int]
    ttmn_state: list[float]
    actuator_commands: ActuatorSnapshot


class ScenarioScientificStatus(TransportModel):
    closed_loop_execution_completed: bool
    environment_affected_sensory_input: bool
    body_state_feedback_wired: bool
    body_state_feedback_realized: bool
    genuine_nonzero_actuation_occurred: bool
    body_movement_occurred: bool


class ScenarioPlaybackResult(TransportModel):
    schema_version: Literal["scenario_playback_v1"] = Field(
        default="scenario_playback_v1", serialization_alias="schema"
    )
    artifact_id: str
    run_id: str
    scenario: ScenarioDefinition
    dt_ms: float
    duration_ms: float
    statuses: ScenarioScientificStatus
    dnp01_body_ids: list[int]
    total_dnp01_spikes: int
    frames: list[ScenarioPlaybackFrame]
    scientific_limitations: list[str]
    source_operation: Literal["VALIDATED_CANONICAL_REPLAY"] = (
        "VALIDATED_CANONICAL_REPLAY"
    )


def load_scenario_playback(
    scenario_id: str, path: Path = DEFAULT_SCENARIO_PATH
) -> ScenarioPlaybackResult:
    definitions = {item.id: item for item in scenario_catalog()}
    if scenario_id not in definitions:
        raise KeyError("unsupported scenario")
    # Full numerical replay and provenance validation on every request. No cache
    # of unvalidated internal JSON and no presentation-driven scientific changes.
    payload = replay_scenario_artifact(path)
    if payload["artifact_id"] != CANONICAL_SCENARIO_ARTIFACT_ID:
        raise ValueError("unexpected canonical scenario identity")
    run = next(
        r
        for r in payload["result"]["runs"]
        if r["result"]["scenario_kind"] == scenario_id
    )
    result = run["result"]
    config = run["config"]["scenario"]
    frames = []
    for boundary in result["telemetry"]:
        frame = dict(boundary)
        if frame["object"] is not None:
            frame["object"] = {
                **frame["object"],
                "radius_world_eq": config["object"]["radius_world_eq"],
            }
        frames.append(ScenarioPlaybackFrame.model_validate(frame))
    return ScenarioPlaybackResult(
        artifact_id=payload["artifact_id"],
        run_id=result["scenario_execution_id"],
        scenario=definitions[scenario_id],
        dt_ms=config["dt_ms"],
        duration_ms=result["time_ms"][-1],
        statuses=ScenarioScientificStatus.model_validate(result["statuses"]),
        dnp01_body_ids=result["dnp01_body_ids"],
        total_dnp01_spikes=len(result["dnp01_spikes"]),
        frames=frames,
        scientific_limitations=[
            definitions[scenario_id].scientific_caveat,
            "world_eq is not a physical distance. Actuator commands are dimensionless.",
            "DNp01 membrane values are model coordinates, not measured physiology.",
            "Object projection uses fixed R / hex(23,9); no absolute retinotopy.",
            "Stationary output is not evidence of biological non-response.",
        ],
    )
