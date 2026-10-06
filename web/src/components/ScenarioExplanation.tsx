import { scenarioNarrative } from "@/lib/scenarioPresentation";
import type { ScenarioPlaybackFrame, ScenarioPlaybackResult } from "@/lib/scenarioPlayback";
import { CausalChain, TelemetryValue, AuthorityIds } from "./ScientificInstrument";

export function ScenarioExplanation({ result, frame }: { result: ScenarioPlaybackResult; frame: ScenarioPlaybackFrame }) {
  const story = scenarioNarrative(result, frame);
  return <>
    <CausalChain stages={story.stages} step={frame.step} time={frame.time_ms}/>
    <section className="scenario-telemetry" aria-label="Scientific telemetry">
      <TelemetryValue label="DNp01 · R / L" value={`R ${frame.dnp01_membrane_mv[0].toFixed(3)} / L ${frame.dnp01_membrane_mv[1].toFixed(3)}`} unit="mV_eq" meaning={story.stages[2].title}/>
      <TelemetryValue label="Visual exposure" value={`${frame.active_sensory_body_count} / 311 bodies`} meaning={story.baseline ? "Stimulus disabled" : `Radius ${frame.lattice_radius} relative-column steps`}/>
      <TelemetryValue label="Recorded output" value={result.statuses.body_movement_occurred ? "Movement recorded" : "Stationary"} meaning={`${result.total_dnp01_spikes} DNp01 model spikes in run · ${story.stages[3].title}`}/>
    </section>
    <details className="scenario-details"><summary>Model details, exact telemetry & provenance</summary>
      <h3>Units / claim limits</h3><p>world_eq and mV_eq denote uncalibrated model-space coordinates, not physical distance or biological voltage. Values are displayed unchanged from backend model records. Projection is fixed-centre and exploratory; shadows are not contact physics.</p>
      <h3>Exact neural & body telemetry</h3><p>Scientific time {frame.time_ms.toFixed(1)} ms; boundary {frame.step}. Object distance {frame.relative_distance_world_eq?.toFixed(6) ?? "No object"} world_eq; body ({frame.body.x_world_eq.toFixed(6)}, {frame.body.z_world_eq.toFixed(6)}) world_eq.</p><p>Actuator R {frame.actuator_commands.RIGHT_TTM_ACTUATOR} / L {frame.actuator_commands.LEFT_TTM_ACTUATOR}; TTMn R {frame.ttmn_state[0]} / L {frame.ttmn_state[1]}.</p><div className="exact-neural-data">{result.dnp01_body_ids.map((id, i) => <p key={id}>DNp01 {id}: {frame.dnp01_membrane_mv[i].toFixed(6)} mV_eq · model coordinate</p>)}</div>
      <div className="scenario-sensory">{frame.sensory_summaries.map(s => <span key={`${s.neuron_type}-${s.side}`}>{s.neuron_type} {s.side}: {s.state_sum.toFixed(5)} model state sum</span>)}</div>
      <div className="scenario-statuses">{Object.entries(result.statuses).map(([key, value]) => <span key={key}>{key.replaceAll("_", " ")}: <strong>{value ? "yes" : "no"}</strong></span>)}</div>
      <p>Source: {result.source_operation}. Detailed 311-identity records remain in the scientific artifact.</p>
      <h3>Experiment authority</h3><AuthorityIds ids={{Artifact:result.artifact_id,Run:result.run_id,...(result.preregistration_id ? {"Frozen preregistration":result.preregistration_id} : {})}}/>
      {result.preregistration_id && <p>Parameters selected before neural execution; no output-driven tuning.</p>}
      {result.termination && <p>{result.termination.status.replaceAll("_"," ")} · {result.termination.time_ms} ms. Requested horizon {result.requested_duration_ms} ms; no padded continuation.</p>}<h3>Scientific limitations</h3><ul>{result.scientific_limitations.map(s => <li key={s}>{s}</li>)}</ul>
    </details>
  </>;
}
