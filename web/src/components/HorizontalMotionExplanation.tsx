import type { NeuralIdentity, NeuralPlaybackFrame, NeuralPlaybackResult } from "@/lib/scenarioPlayback";

function SignedRuler({value}:{value:number}) {
  // Signed, centred visual ruler only. Never a firing-rate or efficacy scale.
  const extent=Math.min(1,Math.abs(value))*50;
  return <><div className="neural-ruler" aria-hidden="true"><i style={{left:value < 0 ? `${50-extent}%` : "50%",width:`${extent}%`}}/><b/></div><small>− · neutral 0 · +</small></>;
}

function StateReadout({node,value,units}:{node:NeuralIdentity;value:number;units:string}) {
  return <div className="neural-state"><span>{node.type} {node.side} · {node.body_id}</span><strong>{value.toFixed(6)} <small>{units}</small></strong>
    <SignedRuler value={value}/>
  </div>;
}

export function HorizontalMotionExplanation({result,frame}:{result:NeuralPlaybackResult;frame:NeuralPlaybackFrame}) {
  const sourceResponse=frame.hs_states.some(v=>v !== 0), targetResponse=frame.dnp15_states.some(v=>v !== 0);
  const stages=[
    {name:"Motion input",title:frame.input_descriptor.R !== 0 ? "Right descriptor presented" : "Pulse off",detail:`R ${frame.input_descriptor.R} / L ${frame.input_descriptor.L} horizontal_motion_eq`,state:frame.input_descriptor.R !== 0 ? "ACTIVE" : "RECOVERY"},
    {name:"HS sources",title:sourceResponse ? "Identity-resolved source response" : "Sources neutral",detail:"Six signed continuous proxies",state:sourceResponse ? "RESPONDING" : "NEUTRAL"},
    {name:"Chemical motif",title:"Six verified feedforward routes",detail:"Structural counts are not efficacy",state:"FEEDFORWARD ONLY"},
    {name:"DNp15 readout",title:targetResponse ? "Bilateral continuous readout" : "Targets neutral",detail:"R 11215 / L 12069 · dnp15_state_eq",state:targetResponse ? "RESPONDING" : "NEUTRAL"},
    {name:"Diagnostic only",title:"Bilateral neural-state differential",detail:`R−L ${frame.bilateral_differential.toFixed(6)}`,state:"NO BODY MAPPING"},
  ];
  return <>
    <section className="causal-section" aria-label="Current causal pathway"><div className="causal-heading"><p className="eyebrow">FOLLOW THE NEURAL PATH</p><span>Exact boundary {frame.step} · {frame.time_ms.toFixed(1)} ms</span></div>
      <ol className="causal-flow">{stages.map((s,i)=><li key={s.name} data-state={s.state}><div className="causal-stage-name"><span>0{i+1}</span>{s.name}</div><strong>{s.title}</strong><p>{s.detail}</p><span className="causal-state">{s.state}</span></li>)}</ol>
    </section>
    <section className="scenario-interpretation" aria-label="Scientific interpretation"><div><p className="eyebrow">{frame.step === result.frames.length-1 ? "FINAL BOUNDARY · RUN COMPLETE" : "SELECTED NEURAL BOUNDARY"}</p><h2>A neural response, not a body action.</h2>
      <p>The controlled descriptor propagates through HS source proxies into DNp15, a descending-neuron readout. At this boundary: R {frame.dnp15_states[0].toFixed(6)}, L {frame.dnp15_states[1].toFixed(6)} dnp15_state_eq; R−L {frame.bilateral_differential.toFixed(6)}.</p>
      <p>{frame.bilateral_differential > 0 ? "The model currently produces a larger right DNp15 proxy state." : frame.bilateral_differential < 0 ? "The model currently produces a larger left DNp15 proxy state." : "The bilateral diagnostic is currently neutral."} No body mapping is defined, so no fly turn or movement is simulated.</p>
      <p>Continuous states only; event semantics not defined. Recurrence and electrical context remain excluded after the Phase 26 evidence gate.</p>
    </div></section>
    <section className="scenario-telemetry" aria-label="Scientific telemetry">
      <div><p className="eyebrow">SCIENTIFIC TIME</p><h3>{frame.time_ms.toFixed(1)} ms</h3><p>Boundary {frame.step} · {result.dt_ms} ms steps</p></div>
      <div><p className="eyebrow">MOTION DESCRIPTOR</p><h3>R {frame.input_descriptor.R.toFixed(3)} / L {frame.input_descriptor.L.toFixed(3)}</h3><p>horizontal_motion_eq · uncalibrated</p></div>
      <div><p className="eyebrow">BILATERAL DIFFERENTIAL</p><h3>{frame.bilateral_differential.toFixed(6)}</h3><p>R−L · model diagnostic only · zero is neutral</p><SignedRuler value={frame.bilateral_differential}/></div>
      {result.targets.map((n,i)=><StateReadout key={n.body_id} node={n} value={frame.dnp15_states[i]} units={result.target_units}/>)}
    </section>
    <section className="neural-sources" aria-label="Six identity-resolved HS source states"><h2>HS source states & active routes</h2><p>HS cells are visual interneurons associated with horizontal motion. Here each identity has a signed dimensionless proxy, not recorded activity. Only the right descriptor is presented in this condition; the left input is neutral.</p><div>{result.sources.map((n,i)=><div key={n.body_id}><StateReadout node={n} value={frame.hs_states[i]} units="signed proxy"/><p className="neural-route">{n.body_id} → DNp15 {result.provenance.active_routes.find(e=>e.source_id === n.body_id)!.target_id} · chemical route</p></div>)}</div></section>
    <details className="scenario-details"><summary>Verified motif, model units & provenance</summary>
      <p>{result.provenance.dataset} · {result.condition_id}. Backend numerical replay, not client simulation.</p>
      <p>Six active chemical routes; contact counts are structural evidence only. No recurrent, electrical, motor or body dynamics are added.</p>
      <ul>{result.provenance.active_routes.map(e=><li key={e.source_id}>{e.source_id} → {e.target_id} · {e.structural_count} structural contacts</li>)}</ul>
      <p>Seven excluded context routes: {result.provenance.excluded_routes.map(e=>`${e.source_id}→${e.target_id}`).join(", ")}. These are not active signal paths.</p>
      <p>horizontal_motion_eq is not angular velocity. dnp15_state_eq is not biological voltage. Signed source state is not calcium or firing rate.</p>
      <p className="scenario-hash">Artifact: {result.artifact_id}<br/>Phase24 selection: {result.provenance.selection_id}<br/>Phase25 preregistration: {result.provenance.preregistration_id}<br/>Phase26 context audit: {result.provenance.context_audit_id}<br/>{result.provenance.context_decision}</p>
      <ul>{result.scientific_limitations.map(s=><li key={s}>{s}</li>)}</ul>
    </details>
  </>;
}
