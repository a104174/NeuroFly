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
    "EXPLORATORY_COURSE_CONTROL",
]
COURSE_KIND = "EXPLORATORY_COURSE_CONTROL"
COURSE_CONDITION = "CLOSED_LOOP_PERTURBATION"
CANONICAL_COURSE_ARTIFACT_ID = (
    "f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581"
)
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
    definitions.append(
        ScenarioDefinition(
            id=COURSE_KIND,
            scenario_kind=COURSE_KIND,
            title="Exploratory Course Control",
            description="Model-space visual-motion feedback through HS→DNp15 "
            "into exploratory orientation.",
            scientific_caveat=(
                "Closed-loop experiment · 50 ms · no translation. Marginal "
                "orientation dynamics: motion modes decay, but no absolute "
                "heading-error signal exists. Not calibrated biological behavior."
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


class CourseObservation(TransportModel):
    interval_start_step: int
    interval_end_step: int
    interval_start_ms: float
    interval_end_ms: float
    raw_view_motion_eq_per_ms: float
    normalized_unclipped: float
    global_horizontal_motion_eq: float = Field(ge=-1, le=1)
    clipped: bool


class CoursePlaybackFrame(TransportModel):
    step: int
    time_ms: float
    yaw_orientation_eq: float
    previous_orientation_eq: float | None
    relative_view_eq: float
    observation: CourseObservation | None
    input_descriptor: HorizontalInput
    hs_states: list[float] = Field(min_length=6, max_length=6)
    dnp15_states: list[float] = Field(min_length=2, max_length=2)
    bilateral_differential: float
    yaw_drive_eq: float
    observation_clipped: bool
    external_orientation_increment_eq: float | None


class CourseWorldReference(TransportModel):
    reference_id: Literal["WORLD_FIXED_HEADING_ZERO"]
    heading_eq: float
    period_eq: Literal[1]
    units: Literal["world_heading_eq"] = "world_heading_eq"


class CourseAnalysis(TransportModel):
    analysis_id: str
    stage_a_decision: Literal[
        "CLOSED_LOOP_COMPOSITION_MARGINAL_BUT_BOUNDED_FOR_FINITE_HORIZON_TEST"
    ]
    classification: Literal["MARGINAL_ORIENTATION_MODE"]
    local_motion_spectral_radius: float = Field(gt=0, lt=1)
    orientation_eigenvalue: Literal[1]
    clipping_required_for_local_stability: Literal[False]


class CourseProvenance(TransportModel):
    neural: NeuralProvenance
    neural_artifact_id: str
    orientation_evidence_id: str
    orientation_preregistration_id: str
    orientation_artifact_id: str
    observation_contract_id: str
    closed_loop_preregistration_id: str
    config_sha256: str
    result_sha256: str
    analysis: CourseAnalysis


class CourseScientificStatus(TransportModel):
    execution_completed: bool
    orientation_feedback_connected: Literal[True]
    orientation_feedback_realized: bool
    translation: Literal["NOT_MODELLED"]
    absolute_heading_error_signal: Literal[False]
    event_semantics: Literal["NOT_DEFINED"]
    recurrence_active: Literal[False]
    electrical_coupling_active: Literal[False]


class CourseSummary(TransportModel):
    initial_perturbation_eq: float
    final_orientation_eq: float
    clipping_count: int
    observed_interval_count: int
    clipping_duration_ms: float


class CoursePerturbation(TransportModel):
    start_step: int
    end_step: int
    increment_eq: float


class CourseTermination(TransportModel):
    status: Literal["COMPLETED_VALID_HORIZON"]
    step: int
    time_ms: float


class CoursePlaybackResult(TransportModel):
    schema_version: Literal["scenario_playback_v1"] = Field(
        default="scenario_playback_v1", serialization_alias="schema"
    )
    presentation_kind: Literal["EXPLORATORY_CLOSED_LOOP_MODEL"] = (
        "EXPLORATORY_CLOSED_LOOP_MODEL"
    )
    artifact_id: str
    run_id: str
    scenario: ScenarioDefinition
    condition_id: Literal["CLOSED_LOOP_PERTURBATION"]
    dt_ms: float
    duration_ms: float
    statuses: CourseScientificStatus
    world_reference: CourseWorldReference
    sources: list[NeuralIdentity] = Field(min_length=6, max_length=6)
    targets: list[NeuralIdentity] = Field(min_length=2, max_length=2)
    input_units: Literal["horizontal_motion_eq"]
    source_units: Literal["dimensionless_signed_proxy"]
    target_units: Literal["dnp15_state_eq"]
    orientation_units: Literal["yaw_orientation_eq"]
    yaw_drive_units: Literal["yaw_drive_eq"]
    view_units: Literal["relative_view_eq"]
    provenance: CourseProvenance
    summary: CourseSummary
    perturbation: CoursePerturbation
    termination: CourseTermination
    frames: list[CoursePlaybackFrame]
    scientific_limitations: list[str]
    source_operation: Literal["VALIDATED_CANONICAL_REPLAY"] = (
        "VALIDATED_CANONICAL_REPLAY"
    )


def load_course_playback(path: Path | None = None) -> CoursePlaybackResult:
    """Reduced presentation DTO over immutable Phase30 replay, never generation."""
    from neurofly.exploratory_course_control_artifacts import (
        DEFAULT_ARTIFACT_ROOT as COURSE_ROOT,
    )
    from neurofly.exploratory_course_control_artifacts import (
        replay_closed_loop_artifact,
    )
    from neurofly.hs_dnp15_neural_validation import load_preregistration
    from neurofly.ttm_g1_electrophysiology_observations import canonical_sha256

    payload = replay_closed_loop_artifact(
        path or COURSE_ROOT / CANONICAL_COURSE_ARTIFACT_ID
    )
    if payload["artifact_id"] != CANONICAL_COURSE_ARTIFACT_ID:
        raise ValueError("Phase30 canonical authority mismatch")
    p = payload["config"]["preregistration"]
    result = payload["result"]
    n = load_preregistration()
    run = next(r for r in result["runs"] if r["condition"]["id"] == COURSE_CONDITION)
    if run["termination"]["status"] != "COMPLETED_VALID_HORIZON":
        raise ValueError("canonical course-control experiment incomplete")
    authorities = {
        item["document"]: item["canonical_id"] for item in p["authority_records"]
    }
    frames = []
    for b in run["boundaries"]:
        o = b["observation"]
        frames.append(
            CoursePlaybackFrame(
                step=b["boundary_index"],
                time_ms=b["time_ms"],
                yaw_orientation_eq=b["yaw_orientation_eq"],
                previous_orientation_eq=b["previous_orientation_eq"],
                relative_view_eq=b["relative_view_eq"],
                observation=CourseObservation(
                    interval_start_step=o["interval"]["before"]["index"],
                    interval_end_step=o["available_boundary_index"],
                    interval_start_ms=o["interval"]["before"]["time_ms"],
                    interval_end_ms=o["interval"]["after"]["time_ms"],
                    raw_view_motion_eq_per_ms=o["raw_view_motion_eq_per_ms"],
                    normalized_unclipped=o["normalized_unclipped"],
                    global_horizontal_motion_eq=o["global_horizontal_motion_eq"],
                    clipped=o["clipped"],
                )
                if o
                else None,
                input_descriptor={
                    "R": b["latched_motion"]["right"],
                    "L": b["latched_motion"]["left"],
                },
                hs_states=b["hs_states"],
                dnp15_states=b["dnp15_states"],
                bilateral_differential=b["dnp15_differential"],
                yaw_drive_eq=b["yaw_drive_eq"],
                observation_clipped=b["observation_clipped"],
                external_orientation_increment_eq=b[
                    "external_orientation_increment_eq"
                ],
            )
        )
    diag, analysis = run["diagnostics"], p["analysis"]
    return CoursePlaybackResult(
        artifact_id=payload["artifact_id"],
        run_id=canonical_sha256([payload["artifact_id"], COURSE_CONDITION]),
        scenario=next(s for s in scenario_catalog() if s.id == COURSE_KIND),
        condition_id=COURSE_CONDITION,
        dt_ms=p["dt_ms"],
        duration_ms=p["duration_ms"],
        statuses=CourseScientificStatus(
            execution_completed=True,
            orientation_feedback_connected=True,
            orientation_feedback_realized=any(
                b["applied_neural_orientation_increment_eq"] not in (None, 0)
                for b in run["boundaries"]
            ),
            translation="NOT_MODELLED",
            absolute_heading_error_signal=False,
            event_semantics="NOT_DEFINED",
            recurrence_active=False,
            electrical_coupling_active=False,
        ),
        world_reference=CourseWorldReference(
            reference_id=p["world"]["reference_id"],
            heading_eq=p["world"]["heading_eq"],
            period_eq=p["world"]["period_eq"],
        ),
        sources=[
            {k: v[k] for k in ("body_id", "type", "side")}
            for v in result["source_order"]
        ],
        targets=[
            {k: v[k] for k in ("body_id", "type", "side")}
            for v in result["target_order"]
        ],
        input_units=p["units"]["motion"],
        source_units=p["units"]["source"],
        target_units=p["units"]["target"],
        orientation_units=p["units"]["orientation"],
        yaw_drive_units=p["units"]["drive"],
        view_units=p["units"]["view"],
        provenance=CourseProvenance(
            neural=NeuralProvenance(
                dataset=n["dataset"],
                selection_id=n["selection_record_id"],
                preregistration_id=authorities[
                    "hs_dnp15_neural_validation_preregistration.json"
                ],
                context_audit_id=CONTEXT_AUDIT_ID,
                context_decision="FEEDFORWARD_MOTIF_REMAINS_CURRENT_VALIDATED_BOUNDARY",
                active_routes=[
                    {k: e[k] for k in ("source_id", "target_id", "structural_count")}
                    for e in n["selected_routes"]
                ],
                excluded_routes=[
                    {k: e[k] for k in ("source_id", "target_id", "structural_count")}
                    for e in n["omitted_induced_edges"]
                ],
            ),
            neural_artifact_id=p["source_artifacts"]["phase25"]["artifact_id"],
            orientation_evidence_id=authorities["dnp15_yaw_mapping_evidence_gate.json"],
            orientation_preregistration_id=authorities[
                "dnp15_exploratory_yaw_preregistration.json"
            ],
            orientation_artifact_id=p["source_artifacts"]["phase28"]["artifact_id"],
            observation_contract_id=authorities[
                "orientation_to_horizontal_motion_contract.json"
            ],
            closed_loop_preregistration_id=payload["config"]["preregistration_id"],
            config_sha256=payload["config_sha256"],
            result_sha256=payload["result_sha256"],
            analysis=CourseAnalysis(
                analysis_id=p["analysis_id"],
                stage_a_decision=analysis["decision"],
                classification="MARGINAL_ORIENTATION_MODE",
                local_motion_spectral_radius=analysis["differential_spectral_radius"],
                orientation_eigenvalue=analysis["full_spectral_radius"],
                clipping_required_for_local_stability=False,
            ),
        ),
        summary=CourseSummary(
            initial_perturbation_eq=diag["initial_perturbation_eq"],
            final_orientation_eq=diag["final_orientation_eq"],
            clipping_count=diag["clipping"]["count"],
            observed_interval_count=diag["clipping"]["observed_interval_count"],
            clipping_duration_ms=diag["clipping"]["duration_ms"],
        ),
        perturbation=CoursePerturbation(
            start_step=p["perturbation"]["interval_index"],
            end_step=p["perturbation"]["interval_index"] + 1,
            increment_eq=diag["initial_perturbation_eq"],
        ),
        termination=CourseTermination(
            status=run["termination"]["status"],
            step=run["termination"]["boundary_index"],
            time_ms=frames[-1].time_ms,
        ),
        frames=frames,
        scientific_limitations=[
            "Exploratory model-space orientation, "
            "not biological yaw or calibrated behavior.",
            "Motion-only observation: no absolute heading-error signal; "
            "residual offset is expected.",
            "No translation, physical mechanics, chemical recurrence "
            "or electrical coupling.",
            "Rendering converts one abstract cycle to 2π display radians only; "
            "no visual amplification or scientific feedback.",
            "The open-loop control is stationary after its imposed step; feedback "
            "introduces subsequent counter-motion, "
            "not demonstrated biological superiority.",
        ],
    )


def load_scenario_playback(
    scenario_id: str, path: Path = DEFAULT_SCENARIO_PATH
) -> ScenarioPlaybackResult | NeuralPlaybackResult | CoursePlaybackResult:
    definitions = {item.id: item for item in scenario_catalog()}
    if scenario_id not in definitions:
        raise KeyError("unsupported scenario")
    if scenario_id == NEURAL_KIND:
        return load_neural_playback()
    if scenario_id == COURSE_KIND:
        return load_course_playback()
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
