"""Typed product transport over replay-validated artifacts, never a model."""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from neurofly.closed_loop_scenario import scenario_metadata
from neurofly.closed_loop_scenario_artifacts import (
    DEFAULT_ARTIFACT_ROOT,
    replay_scenario_artifact,
)
from neurofly.looming_world_experiment import KIND as WORLD_KIND
from neurofly.looming_world_experiment_artifacts import (
    DEFAULT_ARTIFACT_ROOT as WORLD_ROOT,
)
from neurofly.looming_world_experiment_artifacts import (
    replay_world_artifact,
)

CANONICAL_SCENARIO_ARTIFACT_ID = (
    "55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b"
)
DEFAULT_SCENARIO_PATH = DEFAULT_ARTIFACT_ROOT / CANONICAL_SCENARIO_ARTIFACT_ID
ScenarioKind = Literal[
    "BASELINE_CONTROL",
    "LOOMING_CIRCUIT_VALIDATION",
    "LOOMING_WORLD_EXPERIMENT",
    "HORIZONTAL_MOTION_NEURAL_VALIDATION",
]
NEURAL_KIND = "HORIZONTAL_MOTION_NEURAL_VALIDATION"
CANONICAL_NEURAL_ARTIFACT_ID = (
    "2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113"
)
CONTEXT_AUDIT_ID = "04116360164262de5a2572f33e12cc90351869567c3202811807be576f1d03be"
NEURAL_CONDITION = "RIGHT_SIDE_MOTION"
# Derived from the first frozen execution, not a design-selection input.
CANONICAL_WORLD_ARTIFACT_ID = (
    "ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c"
)


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
    definitions = [
        ScenarioDefinition(
            id=item["id"],
            scenario_kind=item["id"],
            title=item["title"],
            description=item["description"],
            scientific_caveat=caveat,
        )
        for item in scenario_metadata()
    ]
    definitions.append(
        ScenarioDefinition(
            id=WORLD_KIND,
            scenario_kind=WORLD_KIND,
            title="Exploratory Looming World Experiment",
            description=(
                "A separately pre-registered 40 ms model-space experiment observes "
                "longer pinned-model dynamics and authoritative body feedback."
            ),
            scientific_caveat=(
                "Duration and trajectory are modelling assumptions, not biological "
                "timing or physical velocity. Genuine outputs are shown as produced; "
                "zero output is valid. No calibrated retinal geometry or escape claim."
            ),
        )
    )
    definitions.append(
        ScenarioDefinition(
            id=NEURAL_KIND,
            scenario_kind=NEURAL_KIND,
            title="Horizontal Motion Neural Validation",
            description=(
                "HS→DNp15 neural-only validation: a controlled right-side "
                "motion descriptor produces a bilateral continuous neural readout, "
                "not body movement."
            ),
            scientific_caveat=(
                "Uncalibrated horizontal_motion_eq and dnp15_state_eq. "
                "Six chemical feedforward routes only; no recurrent/electrical "
                "dynamics, events or body mapping."
            ),
        )
    )
    return definitions


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


class ExperimentTermination(TransportModel):
    status: Literal["COMPLETED_VALID_HORIZON", "TERMINATED_GEOMETRY_DOMAIN"]
    step: int
    time_ms: float
    reason: str | None


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
    termination: ExperimentTermination | None = None
    requested_duration_ms: float | None = None
    preregistration_id: str | None = None


class NeuralIdentity(TransportModel):
    body_id: int
    type: Literal["HSN", "HSE", "HSS", "DNp15"]
    side: Literal["R", "L"]


class NeuralRoute(TransportModel):
    source_id: int
    target_id: int
    structural_count: int


class HorizontalInput(TransportModel):
    R: float = Field(ge=-1, le=1)
    L: float = Field(ge=-1, le=1)


class NeuralPlaybackFrame(TransportModel):
    step: int
    time_ms: float
    input_descriptor: HorizontalInput
    hs_states: list[float] = Field(min_length=6, max_length=6)
    dnp15_states: list[float] = Field(min_length=2, max_length=2)
    bilateral_differential: float
    presentation_phase_eq: float


class NeuralProvenance(TransportModel):
    dataset: Literal["male-cns:v1.0"]
    selection_id: str
    preregistration_id: str
    context_audit_id: str
    context_decision: Literal["FEEDFORWARD_MOTIF_REMAINS_CURRENT_VALIDATED_BOUNDARY"]
    active_routes: list[NeuralRoute] = Field(min_length=6, max_length=6)
    excluded_routes: list[NeuralRoute] = Field(min_length=7, max_length=7)


class NeuralScientificStatus(TransportModel):
    execution_completed: bool
    event_semantics: Literal["NOT_DEFINED"]
    body_mapping: Literal["NOT_DEFINED"]
    recurrence_active: Literal[False]
    electrical_coupling_active: Literal[False]


class NeuralPlaybackResult(TransportModel):
    schema_version: Literal["scenario_playback_v1"] = Field(
        default="scenario_playback_v1", serialization_alias="schema"
    )
    presentation_kind: Literal["NEURAL_ONLY_VALIDATION"] = "NEURAL_ONLY_VALIDATION"
    artifact_id: str
    run_id: str
    scenario: ScenarioDefinition
    condition_id: Literal["RIGHT_SIDE_MOTION"]
    dt_ms: float
    duration_ms: float
    statuses: NeuralScientificStatus
    sources: list[NeuralIdentity] = Field(min_length=6, max_length=6)
    targets: list[NeuralIdentity] = Field(min_length=2, max_length=2)
    input_units: Literal["horizontal_motion_eq"]
    source_units: Literal["dimensionless_signed_proxy"]
    target_units: Literal["dnp15_state_eq"]
    provenance: NeuralProvenance
    frames: list[NeuralPlaybackFrame]
    scientific_limitations: list[str]
    source_operation: Literal["VALIDATED_CANONICAL_REPLAY"] = (
        "VALIDATED_CANONICAL_REPLAY"
    )


def load_neural_playback(path: Path | None = None) -> NeuralPlaybackResult:
    """Replay frozen authorities and adapt presentation; never generate science."""
    from neurofly.hs_dnp15_neural_validation import SCIENCE_ROOT
    from neurofly.hs_dnp15_neural_validation_artifacts import (
        DEFAULT_ARTIFACT_ROOT as NEURAL_ROOT,
    )
    from neurofly.hs_dnp15_neural_validation_artifacts import replay_neural_artifact
    from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

    context = json.loads(
        (SCIENCE_ROOT / "hs_dnp15_network_context_audit.json").read_bytes()
    )
    if (
        context["audit_id"] != CONTEXT_AUDIT_ID
        or canonical_sha256(context["audit"]) != CONTEXT_AUDIT_ID
    ):
        raise ValueError("Phase26 context authority mismatch")
    payload = replay_neural_artifact(path or NEURAL_ROOT / CANONICAL_NEURAL_ARTIFACT_ID)
    if (
        payload["artifact_id"] != CANONICAL_NEURAL_ARTIFACT_ID
        or context["audit"]["authorities"]["phase25_artifact_id"]
        != payload["artifact_id"]
    ):
        raise ValueError("Phase25 authority mismatch")
    config, result = payload["config"], payload["result"]
    p = config["preregistration"]
    run = next(r for r in result["runs"] if r["condition_id"] == NEURAL_CONDITION)

    def identity(n):
        return {k: n[k] for k in ("body_id", "type", "side")}

    def route(e):
        return {k: e[k] for k in ("source_id", "target_id", "structural_count")}

    return NeuralPlaybackResult(
        artifact_id=payload["artifact_id"],
        run_id=canonical_sha256([payload["artifact_id"], NEURAL_CONDITION]),
        scenario=next(s for s in scenario_catalog() if s.id == NEURAL_KIND),
        condition_id=NEURAL_CONDITION,
        dt_ms=p["dt_ms"],
        duration_ms=result["time_ms"][-1],
        statuses=NeuralScientificStatus(
            execution_completed=run["execution_completed"],
            event_semantics=result["event_semantics"],
            body_mapping="NOT_DEFINED",
            recurrence_active=False,
            electrical_coupling_active=False,
        ),
        sources=[identity(n) for n in result["source_order"]],
        targets=[identity(n) for n in result["target_order"]],
        input_units="horizontal_motion_eq",
        source_units="dimensionless_signed_proxy",
        target_units=result["state_units"]["target"],
        provenance=NeuralProvenance(
            dataset=p["dataset"],
            selection_id=config["structural_authority_id"],
            preregistration_id=config["preregistration_id"],
            context_audit_id=CONTEXT_AUDIT_ID,
            context_decision=context["audit"]["phase26_decision"],
            active_routes=[route(e) for e in p["selected_routes"]],
            excluded_routes=[route(e) for e in p["omitted_induced_edges"]],
        ),
        frames=[
            NeuralPlaybackFrame(
                step=i,
                time_ms=t,
                input_descriptor=run["input_descriptors"][i],
                hs_states=run["source_states"][i],
                dnp15_states=run["target_states"][i],
                bilateral_differential=run["right_minus_left_diagnostic"][i],
                # Display stripe phase only: time-based guide freezes at pulse end.
                presentation_phase_eq=min(t, p["input"]["offset_boundary"] * p["dt_ms"])
                / 10.0,
            )
            for i, t in enumerate(result["time_ms"])
        ],
        scientific_limitations=[
            "Neural-only feedforward proxy, not steering or calibrated optic flow.",
            "Signed HS proxy is not membrane voltage, calcium or firing rate.",
            "DNp15 events and body mapping are not defined; "
            "no measured zero body output is claimed.",
            "Phase26 excludes seven additional chemical edges and electrical "
            "context: recurrent operator insufficiently identified.",
            "Display stripe phase is presentation-only, "
            "not retinal geometry or a scientific input.",
        ],
    )


def load_scenario_playback(
    scenario_id: str, path: Path = DEFAULT_SCENARIO_PATH
) -> ScenarioPlaybackResult | NeuralPlaybackResult:
    definitions = {item.id: item for item in scenario_catalog()}
    if scenario_id not in definitions:
        raise KeyError("unsupported scenario")
    if scenario_id == NEURAL_KIND:
        return load_neural_playback()
    # Full numerical replay and provenance validation on every request. No cache
    # of unvalidated internal JSON and no presentation-driven scientific changes.
    if scenario_id == WORLD_KIND:
        payload = replay_world_artifact(WORLD_ROOT / CANONICAL_WORLD_ARTIFACT_ID)
        if payload["artifact_id"] != CANONICAL_WORLD_ARTIFACT_ID:
            raise ValueError("unexpected frozen world experiment identity")
        run = payload
    else:
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
        termination=ExperimentTermination.model_validate(
            {
                k: result["termination"][k]
                for k in ("status", "step", "time_ms", "reason")
            }
        )
        if "termination" in result
        else None,
        requested_duration_ms=config["preregistration"]["duration_ms"]
        if "preregistration" in config
        else None,
        preregistration_id=config.get("preregistration_id"),
        scientific_limitations=[
            definitions[scenario_id].scientific_caveat,
            "world_eq is not a physical distance. Actuator commands are dimensionless.",
            "DNp01 membrane values are model coordinates, not measured physiology.",
            "Object projection uses fixed R / hex(23,9); no absolute retinotopy.",
            "Stationary output is not evidence of biological non-response.",
        ],
    )
