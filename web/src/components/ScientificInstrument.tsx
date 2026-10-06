import Link from "next/link";
import type { ReactNode } from "react";
import { isCoursePlayback, isNeuralPlayback, type ScenarioPlayback } from "@/lib/scenarioPlayback";

export const signed = (value:number, precision=6) => `${value >= 0 ? "+" : ""}${value.toFixed(precision)}`;

export interface CausalStage {name:string;title:string;detail:string;state?:string}
export function CausalChain({stages,step,time,loop=false}:{stages:CausalStage[];step:number;time:number;loop?:boolean}) {
  return <section className="causal-section" aria-label={loop ? "Delayed closed-loop causal pathway" : "Current causal pathway"}>
    <div className="causal-heading"><h2>{loop ? "Follow the delayed loop ↺" : "Follow the causal path"}</h2><span>Exact boundary {step} · {time.toFixed(1)} ms</span></div>
    <ol className={`causal-flow ${loop ? "course-causal-flow" : ""}`}>{stages.map((stage,i)=><li key={stage.name} data-state={stage.state}>
      <div className="causal-stage-name"><span>{String(i+1).padStart(2,"0")}</span>{stage.name}{i < stages.length-1 && <b aria-hidden="true">→</b>}</div>
      <strong>{stage.title}</strong><p>{stage.detail}</p>{stage.state && <span className="causal-state">{stage.state}</span>}
    </li>)}</ol>
    {loop && <p className="loop-return">↺ Next completed interval · delayed closed-loop update · no same-boundary feedback</p>}
  </section>;
}

export function TelemetryValue({label,value,unit,meaning}:{label:string;value:ReactNode;unit?:string;meaning?:string}) {
  return <div className="telemetry-value"><span className="telemetry-label">{label}</span><strong>{value}</strong>{unit && <code>{unit}</code>}{meaning && <small>{meaning}</small>}</div>;
}
export function EvidenceGrammar({data,model}:{data:string;model:string}) {
  return <dl className="evidence-grammar"><div><dt>DATA</dt><dd>{data}</dd></div><div><dt>MODEL</dt><dd>{model}</dd></div><div><dt>RESULT</dt><dd>Recorded model states · deterministic replay</dd></div></dl>;
}
const unitMeanings = [
  ["mV_eq","Uncalibrated membrane model coordinate, not measured voltage."],
  ["world_eq","Uncalibrated world geometry, not physical distance."],
  ["horizontal_motion_eq","Signed model-space motion descriptor, not calibrated optic flow."],
  ["dimensionless_signed_proxy","HS continuous model state, not firing rate or calcium."],
  ["dnp15_state_eq","Continuous DNp15 proxy state; event semantics not defined."],
  ["yaw_drive_eq","Exploratory neural-to-orientation drive, not torque or measured turn rate."],
  ["yaw_orientation_eq","Model-space orientation, not measured biological yaw."],
  ["relative_view_eq","Relative model-space view geometry, not retinal calibration."],
];
export function UnitHelp() {
  return <details className="scenario-details unit-help"><summary>Model-space units · what the values mean</summary><dl>{unitMeanings.map(([unit,meaning])=><div key={unit}><dt><code>{unit}</code></dt><dd>{meaning}</dd></div>)}</dl></details>;
}
export function PlaybackPhases({result}:{result:ScenarioPlayback}) {
  const horizon=Number(result.duration_ms.toFixed(1)); // Label precision only.
  return <div className="timeline-phases">{isCoursePlayback(result) ? <><span>0→{result.perturbation.end_step} · external perturbation</span><span>Completed intervals · feedback evolution</span><span>{horizon} ms · residual offset</span></> : isNeuralPlayback(result) ? <><span>0–{result.frames.find(f=>f.input_descriptor.R===0)?.time_ms} ms · stimulus</span><span>Pulse off → {horizon} ms · recovery</span></> : <><span>0 ms · {result.scenario.id==="BASELINE_CONTROL" ? "Neutral control" : "Prescribed approach"}</span><span>{horizon} ms · experiment ends</span></>}</div>;
}
/** Full IDs remain native-selectable and accessible in a nested disclosure. */
export function AuthorityIds({ids}:{ids:Record<string,string>}) {
  return <div className="authority-ids">{Object.entries(ids).map(([label,id])=><details key={label}><summary><span>{label}</span><code>{id.slice(0,10)}…</code></summary><code className="full-authority">{id}</code></details>)}</div>;
}
export function ScientificPlaybackLoading() {
  return <section className="scientific-loading" role="status" aria-live="polite" aria-busy="true"><span className="instrument-index">AUTHORITY CHECK</span><h2>Validating canonical scientific playback</h2><p>Replaying the frozen model and checking source provenance. This can take several seconds.</p><p className="subtle-note">No scientific values or visualization are displayed until validation completes. This is loading—not a neutral result.</p></section>;
}
export function ScientificPlaybackUnavailable({detail,retry}:{detail:string;retry?:()=>void}) {
  return <section className="scientific-unavailable" role="alert"><span className="instrument-index">PLAYBACK UNAVAILABLE</span><h2>Experiment playback unavailable.</h2><p>The canonical scientific artifact could not be validated.</p><p>No synthetic fallback has been substituted.</p><div className="unavailable-actions">{retry ? <button onClick={retry}>Retry</button> : <Link href="?replay=canonical">Retry</Link>}<Link href="/scenarios">Back to experiments</Link></div><details><summary>Validation detail</summary><p>{detail}</p></details></section>;
}
