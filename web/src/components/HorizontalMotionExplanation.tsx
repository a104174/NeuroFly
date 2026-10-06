import type { NeuralPlaybackFrame, NeuralPlaybackResult } from "@/lib/scenarioPlayback";
import { CausalChain, TelemetryValue, signed, AuthorityIds } from "./ScientificInstrument";

export function HorizontalMotionExplanation({result,frame}:{result:NeuralPlaybackResult;frame:NeuralPlaybackFrame}) {
  const sourceResponse=frame.hs_states.some(v=>v !== 0), targetResponse=frame.dnp15_states.some(v=>v !== 0);
  const stages=[
    {name:"Motion input",title:frame.input_descriptor.R !== 0 ? "Right descriptor presented" : "Pulse off",detail:`R ${frame.input_descriptor.R} / L ${frame.input_descriptor.L} horizontal_motion_eq`,state:frame.input_descriptor.R !== 0 ? "ACTIVE" : "RECOVERY"},
    {name:"HS sources",title:sourceResponse ? "Identity-resolved source response" : "Sources neutral",detail:"Six signed continuous proxies",state:sourceResponse ? "RESPONDING" : "NEUTRAL"},
    {name:"Chemical motif",title:"Six verified feedforward routes",detail:"Structural counts are not efficacy",state:"FEEDFORWARD ONLY"},
    {name:"DNp15 readout",title:targetResponse ? "Bilateral continuous readout" : "Targets neutral",detail:"R 11215 / L 12069 · dnp15_state_eq",state:targetResponse ? "RESPONDING" : "NEUTRAL"},
    {name:"Diagnostic only",title:"Bilateral neural-state differential",detail:"R−L · model diagnostic only",state:"NO BODY MAPPING"},
  ];
  return <>
    <CausalChain stages={stages} step={frame.step} time={frame.time_ms}/>
    <section className="scenario-telemetry" aria-label="Scientific telemetry">
      <TelemetryValue label="Motion descriptor · R / L" value={`R ${signed(frame.input_descriptor.R,3)} / L ${signed(frame.input_descriptor.L,3)}`} unit="horizontal_motion_eq" meaning="Uncalibrated visual-motion input"/>
      <TelemetryValue label="DNp15 · R / L" value={`R ${signed(frame.dnp15_states[0])} / L ${signed(frame.dnp15_states[1])}`} unit="dnp15_state_eq" meaning="Continuous target proxy states"/>
      <TelemetryValue label="Bilateral differential · R−L" value={signed(frame.bilateral_differential)} unit="dnp15_state_eq" meaning="Model diagnostic only · zero is neutral"/>
    </section>
    <details className="scenario-details"><summary>Six identity-resolved HS source states</summary><p>HS visual interneurons are represented as signed continuous proxies, not recorded activity. Only the right descriptor is presented. No body mapping is defined; event semantics not defined.</p>
      <div className="identity-state-list">{result.sources.map((n,i)=><div key={n.body_id}><span>{n.type} {n.side} · {n.body_id}</span><strong>{signed(frame.hs_states[i])}</strong><code>{result.source_units}</code><small>{n.body_id} → DNp15 {result.provenance.active_routes.find(e=>e.source_id === n.body_id)!.target_id}</small></div>)}</div>
      <p>{frame.bilateral_differential > 0 ? "The model currently produces a larger right DNp15 proxy state." : "The bilateral diagnostic is currently neutral."}</p>
      <p>Targets: {result.targets.map(n=>`${n.type} ${n.side} · ${n.body_id}`).join(" / ")}. Scientific time {frame.time_ms.toFixed(1)} ms.</p>
    </details>
    <details className="scenario-details"><summary>Verified motif, model units & provenance</summary>
      <h3>Dataset / structural authority</h3><p>{result.provenance.dataset} · {result.condition_id}. Backend numerical replay, not client simulation.</p>
      <p>Six active chemical routes; contact counts are structural evidence only. No recurrent, electrical, motor or body dynamics are added.</p>
      <ul>{result.provenance.active_routes.map(e=><li key={e.source_id}>{e.source_id} → {e.target_id} · {e.structural_count} structural contacts</li>)}</ul>
      <h3>Excluded context</h3><p>Seven excluded context routes: {result.provenance.excluded_routes.map(e=>`${e.source_id}→${e.target_id}`).join(", ")}. These are not active signal paths.</p>
      <h3>Units / claim limits</h3><p>horizontal_motion_eq is not angular velocity. dnp15_state_eq is not biological voltage. Signed source state is not calcium or firing rate.</p>
      <h3>Experiment / model authorities</h3><AuthorityIds ids={{Artifact:result.artifact_id,"Phase24 selection":result.provenance.selection_id,"Phase25 preregistration":result.provenance.preregistration_id,"Phase26 context audit":result.provenance.context_audit_id}}/><p>{result.provenance.context_decision}</p>
      <ul>{result.scientific_limitations.map(s=><li key={s}>{s}</li>)}</ul>
    </details>
  </>;
}
