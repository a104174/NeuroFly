import { scenarioNarrative } from "@/lib/scenarioPresentation";
import type { ScenarioPlaybackFrame, ScenarioPlaybackResult } from "@/lib/scenarioPlayback";

export function ScenarioExplanation({ result, frame }: { result: ScenarioPlaybackResult; frame: ScenarioPlaybackFrame }) {
  const story = scenarioNarrative(result, frame);
  const final = frame.step === result.frames.at(-1)!.step;
  return <>
    <section className="causal-section" aria-label="Current causal pathway">
      <div className="causal-heading"><p className="eyebrow">FOLLOW THE CAUSAL PATH</p><span>Exact boundary {frame.step} · {frame.time_ms.toFixed(1)} ms</span></div>
      <ol className="causal-flow">{story.stages.map((s, i) => <li key={s.name} data-state={s.state}>
        <div className="causal-stage-name"><span>0{i + 1}</span>{s.name}</div>
        <strong>{s.title}</strong><p>{s.detail}</p><span className="causal-state">{s.state}</span>
      </li>)}</ol>
    </section>
    <section className="scenario-interpretation" aria-label="Scientific interpretation">
      <div><p className="eyebrow">{final ? "FINAL BOUNDARY · RUN COMPLETE" : "RUN INTERPRETATION"}</p>
        <h2>{story.baseline ? "A control, not a broken simulation." : result.statuses.body_movement_occurred ? "Movement recorded in the model." : "The circuit responds. The body stays still."}</h2>
        <p>{story.summary}</p>
      </div>
      <div className="result-verdict"><span>GENUINE ACTUATION</span><strong>{result.statuses.genuine_nonzero_actuation_occurred ? "Recorded" : "None"}</strong><span>BODY MOVEMENT</span><strong>{result.statuses.body_movement_occurred ? "Recorded" : "None"}</strong></div>
    </section>
    <section className="scenario-telemetry" aria-label="Scientific telemetry">
      <div><p className="eyebrow">SCIENTIFIC TIME</p><h3>{frame.time_ms.toFixed(1)} <small>ms</small></h3><p>Boundary {frame.step} · {result.dt_ms} ms steps</p></div>
      <div><p className="eyebrow">OBJECT DISTANCE</p><h3>{frame.relative_distance_world_eq?.toFixed(3) ?? "No object"}</h3><p>{story.baseline ? "Stimulus disabled" : "world_eq · uncalibrated"}</p></div>
      <div><p className="eyebrow">SENSORY EXPOSURE</p><h3>{frame.active_sensory_body_count} <small>/ 311 bodies</small></h3><p>{frame.lattice_radius === null ? "Projection disabled" : `Radius ${frame.lattice_radius} relative-column steps`}</p></div>
      <div><p className="eyebrow">DNp01</p><h3>{frame.dnp01_membrane_mv[0].toFixed(3)} <small>mV_eq</small></h3><p>{story.stages[2].state} · {result.total_dnp01_spikes} spikes in run</p></div>
      <div><p className="eyebrow">ACTUATOR</p><h3>{story.stages[3].state === "INACTIVE" ? "No command" : "Command present"}</h3><p>R {frame.actuator_commands.RIGHT_TTM_ACTUATOR.toFixed(3)} · L {frame.actuator_commands.LEFT_TTM_ACTUATOR.toFixed(3)} · dimensionless</p></div>
      <div><p className="eyebrow">BODY MOVEMENT</p><h3>{result.statuses.body_movement_occurred ? "Recorded" : "Stationary"}</h3><p>({frame.body.x_world_eq.toFixed(3)}, {frame.body.z_world_eq.toFixed(3)}) world_eq</p></div>
    </section>
    <details className="scenario-details"><summary>Model details, exact telemetry & provenance</summary>
      <p>world_eq and mV_eq denote uncalibrated model-space coordinates, not physical distance or biological voltage. Values are displayed unchanged from backend model records. Projection is fixed-centre and exploratory; shadows are not contact physics.</p>
      <div className="exact-neural-data">{result.dnp01_body_ids.map((id, i) => <p key={id}>DNp01 {id}: {frame.dnp01_membrane_mv[i].toFixed(6)} mV_eq · model coordinate</p>)}</div>
      <div className="scenario-sensory">{frame.sensory_summaries.map(s => <span key={`${s.neuron_type}-${s.side}`}>{s.neuron_type} {s.side}: {s.state_sum.toFixed(5)} model state sum</span>)}</div>
      <div className="scenario-statuses">{Object.entries(result.statuses).map(([key, value]) => <span key={key}>{key.replaceAll("_", " ")}: <strong>{value ? "yes" : "no"}</strong></span>)}</div>
      <p>Source: {result.source_operation}. Detailed 311-identity records remain in the scientific artifact.</p>
      <p className="scenario-hash">Artifact: {result.artifact_id}<br />Run: {result.run_id}</p>
      <ul>{result.scientific_limitations.map(s => <li key={s}>{s}</li>)}</ul>
    </details>
  </>;
}
