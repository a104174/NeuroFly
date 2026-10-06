import type { CoursePlaybackFrame, CoursePlaybackResult } from "@/lib/courseControlPlayback";

const signed=(v:number)=>`${v>=0 ? "+" : ""}${v.toFixed(9)}`;
export function CourseControlExplanation({result,frame}:{result:CoursePlaybackResult;frame:CoursePlaybackFrame}) {
  const p=result.provenance, o=frame.observation;
  const stages=[
    ["World / view","Fixed world reference",`Orientation ${signed(frame.yaw_orientation_eq)}`],
    ["Motion observation",o ? "Completed interval observed" : "No completed interval yet",`R ${signed(frame.input_descriptor.R)} / L ${signed(frame.input_descriptor.L)}`],
    ["HS sources","Six identity-resolved proxies","Six chemical feedforward routes only"],
    ["DNp15","Bilateral continuous readout",`R−L ${signed(frame.bilateral_differential)} · neural diagnostic`],
    ["Orientation","Exploratory orientation response",`yaw_drive_eq ${signed(frame.yaw_drive_eq)}`],
    ["Next view ↺","Next completed interval","Delayed closed-loop update; no same-boundary feedback"],
  ];
  return <>
    <section className="causal-section" aria-label="Delayed closed-loop causal pathway"><div className="causal-heading"><p className="eyebrow">FOLLOW THE DELAYED LOOP ↺</p><span>Exact boundary {frame.step} · {frame.time_ms.toFixed(1)} ms</span></div>
      <ol className="causal-flow course-causal-flow">{stages.map(([name,title,detail],i)=><li key={name}><div className="causal-stage-name"><span>0{i+1}</span>{name}</div><strong>{title}</strong><p>{detail}</p></li>)}</ol>
    </section>
    <section className="scenario-interpretation" aria-label="Scientific interpretation"><div><p className="eyebrow">{frame.step===500 ? "FINAL BOUNDARY · RESIDUAL OFFSET" : "WHAT IS HAPPENING"}</p><h2>Counter-motion, not a heading sensor.</h2>
      <p>A small external orientation perturbation changes the model’s view of a fixed world reference. That completed change produces a model-space horizontal-motion descriptor. The HS→DNp15 circuit responds, and the bilateral DNp15 difference feeds an exploratory orientation integrator.</p>
      <p>Neural feedback produces subsequent counter-rotation and small decaying reversals. Motion-related activity decays, but the model senses visual-motion changes, not absolute heading error. Orientation settles at a nonzero residual offset: {signed(result.summary.final_orientation_eq)} yaw_orientation_eq.</p>
      <p>No translation. Continuous DNp15 proxy states; event semantics not defined. This is an exploratory model-space experiment, not a biological behavior prediction.</p>
      <div className="course-mode"><strong>MARGINAL ORIENTATION MODE</strong><p>Motion modes decay. Absolute orientation is not restored because no heading-error signal exists. This is a model property, not an error.</p></div>
    </div></section>
    <section className="scenario-telemetry course-telemetry" aria-label="Scientific telemetry">
      <div><p className="eyebrow">SCIENTIFIC TIME</p><h3>{frame.time_ms.toFixed(1)} ms</h3><p>Boundary {frame.step}; {result.dt_ms} ms steps</p></div>
      <div><p className="eyebrow">MODEL-SPACE ORIENTATION</p><h3 data-testid="orientation-value">{signed(frame.yaw_orientation_eq)}</h3><p>yaw_orientation_eq · no translation</p></div>
      <div><p className="eyebrow">MOTION DESCRIPTOR</p><h3>R {signed(frame.input_descriptor.R)}<br/>L {signed(frame.input_descriptor.L)}</h3><p>horizontal_motion_eq · uncalibrated</p></div>
      <div><p className="eyebrow">DNp15 CONTINUOUS STATES</p><h3>R {signed(frame.dnp15_states[0])}<br/>L {signed(frame.dnp15_states[1])}</h3><p>11215 R / 12069 L · dnp15_state_eq</p></div>
      <div><p className="eyebrow">BILATERAL NEURAL-STATE DIFFERENTIAL</p><h3>{signed(frame.bilateral_differential)}</h3><p>R−L · model diagnostic only; zero is neutral</p></div>
      <div><p className="eyebrow">YAW DRIVE / OBSERVATION CLIPPING</p><h3>{signed(frame.yaw_drive_eq)} / {frame.observation_clipped ? "YES" : "NO"}</h3><p>yaw_drive_eq · exploratory transform<br/>{result.summary.clipping_count} / {result.summary.observed_interval_count} intervals clipped</p></div>
    </section>
    <details className="scenario-details"><summary>Six HS identities & geometric observation</summary>
      <ul>{result.sources.map((n,i)=><li key={n.body_id}>{n.type} {n.side} · {n.body_id}: {signed(frame.hs_states[i])} dimensionless_signed_proxy</li>)}</ul>
      <p>relative_view_eq: {signed(frame.relative_view_eq)}; previous orientation: {frame.previous_orientation_eq===null ? "No previous boundary" : signed(frame.previous_orientation_eq)}.</p>
      <p>{o ? `Observed interval ${o.interval_start_ms.toFixed(1)}–${o.interval_end_ms.toFixed(1)} ms; raw geometric motion ${signed(o.raw_view_motion_eq_per_ms)} relative_view_eq per model ms; unclipped descriptor ${signed(o.normalized_unclipped)}.` : "Boundary zero has no completed observation interval."}</p>
      <p>Motion at this boundary is latched for the next neural interval. The final boundary is an observation/readout only; no extra scientific tick is rendered.</p>
      <p>External perturbation: {result.perturbation.increment_eq} yaw_orientation_eq in interval {result.perturbation.start_step}→{result.perturbation.end_step}. Current outgoing increment: {frame.external_orientation_increment_eq===null ? "Experiment complete" : signed(frame.external_orientation_increment_eq)}.</p>
    </details>
    <details className="scenario-details"><summary>Scientific provenance, analysis & claim limits</summary>
      <p>{p.neural.dataset} · {result.condition_id}. All scientific values originate from validated backend replay. Presentation interpolation cannot update science.</p>
      <p>Local motion spectral radius {p.analysis.local_motion_spectral_radius}; orientation eigenvalue = {p.analysis.orientation_eigenvalue}. Clipping is not required for local stability. Finite 50 ms horizon; no absolute-heading restoration claim.</p>
      <p>The open-loop control is stationary after the imposed step. Closed-loop feedback introduces subsequent counter-motion; it is not claimed to reduce motion relative to that stationary control.</p>
      <p>Six active chemical routes; structural contacts are provenance, not physiological efficacy:</p><ul>{p.neural.active_routes.map(e=><li key={e.source_id}>{e.source_id} → {e.target_id}: {e.structural_count} structural contacts</li>)}</ul>
      <p>Verified context — excluded from active model: {p.neural.excluded_routes.map(e=>`${e.source_id}→${e.target_id}`).join(", ")}. Electrical coupling also excluded. {p.neural.context_decision}.</p>
      <dl className="course-authorities">{Object.entries({"Phase24 selection":p.neural.selection_id,"Phase25 preregistration":p.neural.preregistration_id,"Phase25 artifact":p.neural_artifact_id,"Phase26 context audit":p.neural.context_audit_id,"Phase28 evidence":p.orientation_evidence_id,"Phase28 preregistration":p.orientation_preregistration_id,"Phase28 artifact":p.orientation_artifact_id,"Phase29 observation":p.observation_contract_id,"Phase30 preregistration":p.closed_loop_preregistration_id,"Phase30 analysis":p.analysis.analysis_id,"Phase30 artifact":result.artifact_id,"Config":p.config_sha256,"Result":p.result_sha256}).map(([label,id])=><div key={label}><dt>{label}</dt><dd>{id}</dd></div>)}</dl>
      <ul>{result.scientific_limitations.map(s=><li key={s}>{s}</li>)}</ul>
    </details>
  </>;
}
