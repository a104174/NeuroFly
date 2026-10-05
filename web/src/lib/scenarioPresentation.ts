import type { ScenarioKind, ScenarioPlaybackFrame, ScenarioPlaybackResult } from "./scenarioPlayback";

export const scenarioCopy: Record<ScenarioKind,{role:string;preview:string;observation:string}> = {
  BASELINE_CONTROL:{role:"CONTROL · ZERO STIMULUS",preview:"NO STIMULUS · NO COMMAND · STATIONARY",observation:"A prominent stationary fly with no object or sensory projection. Silence is the intentional scientific control."},
  LOOMING_CIRCUIT_VALIDATION:{role:"1.4 MS CIRCUIT MICRO-WINDOW · START HERE",preview:"OBJECT → VISUAL CIRCUIT → DNp01 → BODY",observation:"One object approaches. Sensory activity changes, but DNp01 remains subthreshold. No genuine motor command occurs; the fly stays still."},
  LOOMING_WORLD_EXPERIMENT:{role:"40 MS EXPLORATORY WORLD EXPERIMENT",preview:"OBJECT → VISUAL CIRCUIT → DNp01 → BODY",observation:"A separately frozen model-space approach. Inspect genuine neural, motor and body outputs as produced, including zero output. Not a biological escape experiment."},
  HORIZONTAL_MOTION_NEURAL_VALIDATION:{role:"HS→DNp15 · NEURAL-ONLY VALIDATION",preview:"MOTION INPUT → HS → DNp15 R/L → DIAGNOSTIC ONLY",observation:"A right-side horizontal-motion descriptor drives three right HS source proxies and a bilateral DNp15 readout. Inspect the neural-state differential; no body movement is simulated."},
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
      { name: "Sensory", title: sensoryResponding ? "Visual circuit responding" : "No sensory response yet", detail: `${frame.active_sensory_body_count} / 311 bodies exposed`, state: sensoryResponding ? "RESPONDING" : baseline ? "DISABLED" : "INITIAL STATE" },
      { name: "DNp01", title: frame.dnp01_spike_body_ids.length ? "Spike at this boundary" : silent ? "Below model spike threshold" : "No spike at this boundary", detail: `${result.total_dnp01_spikes} spikes in this run`, state: frame.dnp01_spike_body_ids.length ? "SPIKE" : silent ? "SUBTHRESHOLD" : "NO CURRENT SPIKE" },
      { name: "Motor", title: commandPresent ? "Genuine motor command" : "No genuine motor command", detail: "Independent right / left actuator streams", state: commandPresent ? "COMMAND" : "INACTIVE" },
      { name: "Body", title: result.statuses.body_movement_occurred ? "Movement recorded in this run" : "Body stationary", detail: result.statuses.body_movement_occurred ? "Authoritative body snapshots" : "No genuine actuator command was produced", state: result.statuses.body_movement_occurred ? "MOVEMENT RECORDED" : "STATIONARY" },
    ],
    summary: baseline && silent && !result.statuses.genuine_nonzero_actuation_occurred
      ? "No stimulus was active. No genuine neural or motor response occurred. The stationary body is the intentional control result."
      : silent && !result.statuses.genuine_nonzero_actuation_occurred
        ? "Visual input changed and DNp01 depolarized, but the pinned model produced no DNp01 spikes. No genuine motor command or body movement occurred."
        : "The causal loop executed. Inspect the authoritative neural, actuator and body records below; this is not a biological escape prediction.",
  };
}
