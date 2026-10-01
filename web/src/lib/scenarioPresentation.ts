import type { ScenarioPlaybackFrame, ScenarioPlaybackResult } from "./scenarioPlayback";

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
