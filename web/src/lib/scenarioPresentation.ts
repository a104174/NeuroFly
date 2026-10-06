import type { ScenarioKind, ScenarioPlaybackFrame, ScenarioPlaybackResult } from "./scenarioPlayback";

/** Presentation metadata only; it never configures a scientific experiment. */
export const experimentMetadata: Record<ScenarioKind, {kind:string; purpose:string; duration:string; input:string; scope:string; outcome:string; limit:string}> = {
  BASELINE_CONTROL: {kind:"Control",purpose:"Establish the intentional neutral reference.",duration:"1.4 ms",input:"No effective stimulus",scope:"Neural → body readout",outcome:"Expected neutral state",limit:"A control, not spontaneous locomotion."},
  LOOMING_CIRCUIT_VALIDATION: {kind:"Circuit micro-window",purpose:"Inspect LC4 / LPLC2 → DNp01 in a short causal probe.",duration:"1.4 ms",input:"Approaching object",scope:"Neural → body readout",outcome:"Subthreshold · stationary",limit:"Circuit execution, not behavior-scale escape."},
  LOOMING_WORLD_EXPERIMENT: {kind:"Exploratory world experiment",purpose:"Follow growing visual exposure through the frozen pathway.",duration:"40 ms",input:"Model-space approach",scope:"World + neural + body readout",outcome:"Subthreshold · stationary",limit:"Preregistered model-space timing, not biological calibration."},
  HORIZONTAL_MOTION_NEURAL_VALIDATION: {kind:"Neural-only validation",purpose:"Trace a right-side descriptor through the selected HS→DNp15 motif.",duration:"50 ms",input:"Horizontal-motion descriptor",scope:"Neural readout only",outcome:"Right-side response · diagnostic only",limit:"No body mapping defined; continuous proxy states."},
  EXPLORATORY_COURSE_CONTROL: {kind:"Closed-loop experiment",purpose:"Follow visual-motion feedback into exploratory orientation.",duration:"50 ms",input:"External orientation perturbation",scope:"Orientation only · no translation",outcome:"Counter-motion · residual offset",limit:"Marginal orientation dynamics; no absolute heading-error signal."},
};

export const scenarioCopy: Record<ScenarioKind,{role:string;preview:string;observation:string;badge?:string;failureNote?:string}> = {
  BASELINE_CONTROL:{role:"CONTROL · ZERO STIMULUS",preview:"NO STIMULUS · NO COMMAND · STATIONARY",observation:"A prominent stationary fly with no object or sensory projection. Silence is the intentional scientific control."},
  LOOMING_CIRCUIT_VALIDATION:{role:"1.4 MS CIRCUIT MICRO-WINDOW · START HERE",preview:"OBJECT → VISUAL CIRCUIT → DNp01 → BODY",observation:"One object approaches. Sensory activity changes, but DNp01 remains subthreshold. No recorded motor command occurs; the body stays stationary."},
  LOOMING_WORLD_EXPERIMENT:{role:"40 MS EXPLORATORY WORLD EXPERIMENT",preview:"OBJECT → VISUAL CIRCUIT → DNp01 → BODY",observation:"A separately frozen model-space approach. Inspect recorded neural, motor and body outputs as produced, including zero output. Not a biological escape experiment."},
  HORIZONTAL_MOTION_NEURAL_VALIDATION:{role:"HS→DNp15 · NEURAL-ONLY VALIDATION",preview:"MOTION INPUT → HS → DNp15 R/L → DIAGNOSTIC ONLY",observation:"A right-side horizontal-motion descriptor drives three right HS source proxies and a bilateral DNp15 readout. Inspect the neural-state differential; no body movement is simulated."},
  EXPLORATORY_COURSE_CONTROL:{role:"CLOSED-LOOP EXPERIMENT",preview:"WORLD / VIEW → HS → DNp15 → ORIENTATION ↺",observation:"Model-space visual-motion feedback follows an external orientation perturbation. Motion modes decay; orientation retains a residual offset. Closed loop · 50 ms · no translation · model-space orientation.",badge:"Marginal orientation dynamics",failureNote:"Experiment playback unavailable. The canonical scientific artifact could not be validated. No synthetic fallback has been substituted."},
};

/** Human-readable labels over authoritative data, never scientific updates. */
export function scenarioNarrative(result: ScenarioPlaybackResult, frame: ScenarioPlaybackFrame) {
  const baseline = result.scenario.id === "BASELINE_CONTROL";
  const sensoryResponding = frame.sensory_summaries.some(s => s.state_sum > 0);
  const commandPresent = frame.actuator_commands.RIGHT_TTM_ACTUATOR > 0 || frame.actuator_commands.LEFT_TTM_ACTUATOR > 0;
  const silent = result.total_dnp01_spikes === 0;
  return {
    baseline,
    stages: [
      { name: "World", title: baseline ? "No external stimulus" : "Approaching object", detail: baseline ? "Control condition" : "Prescribed model-space path", state: baseline ? "CONTROL" : "ACTIVE" },
      { name: "LC4 / LPLC2", title: sensoryResponding ? "Visual circuit responding" : baseline ? "Sensory input disabled" : "Sources at initial state", detail: `${frame.active_sensory_body_count} / 311 bodies exposed`, state: sensoryResponding ? "RESPONDING" : baseline ? "DISABLED" : "INITIAL STATE" },
      { name: "DNp01", title: frame.dnp01_spike_body_ids.length ? "Spike at this boundary" : silent ? "Below model spike threshold" : "No spike at this boundary", detail: `${result.total_dnp01_spikes} spikes in this run`, state: frame.dnp01_spike_body_ids.length ? "SPIKE" : silent ? "SUBTHRESHOLD" : "NO CURRENT SPIKE" },
      { name: "Motor", title: commandPresent ? "Recorded motor command" : "No recorded motor command", detail: "Independent right / left actuator streams", state: commandPresent ? "COMMAND" : "INACTIVE" },
      { name: "Body", title: result.statuses.body_movement_occurred ? "Movement recorded in this run" : "Body stationary", detail: result.statuses.body_movement_occurred ? "Authoritative body snapshots" : "No actuator command was produced", state: result.statuses.body_movement_occurred ? "MOVEMENT RECORDED" : "STATIONARY" },
    ],
    summary: baseline && silent && !result.statuses.genuine_nonzero_actuation_occurred
      ? "No stimulus was active. Sources remain neutral and DNp01 remains at its resting model coordinate. The stationary body is the intentional control result."
      : silent && !result.statuses.genuine_nonzero_actuation_occurred
        ? "Visual input changed and DNp01 depolarized, but the pinned model produced no DNp01 spikes. No recorded motor command or body movement occurred."
        : "The causal loop executed. Inspect the authoritative neural, actuator and body records below; this is not a biological escape prediction.",
  };
}
