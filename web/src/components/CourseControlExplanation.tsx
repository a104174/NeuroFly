import type { CoursePlaybackFrame, CoursePlaybackResult } from "@/lib/courseControlPlayback";
import { CausalChain, TelemetryValue, AuthorityIds, signed } from "./ScientificInstrument";

export function CourseControlExplanation({result,frame}:{result:CoursePlaybackResult;frame:CoursePlaybackFrame}) {
  const p=result.provenance, o=frame.observation;
  const stages=[
    {name:"World / view",title:"Fixed world reference",detail:"Not a goal direction",state:"MODEL GEOMETRY"},
    {name:"Motion observation",title:o ? "Completed interval observed" : "No completed interval yet",detail:"horizontal_motion_eq · R / L",state:o ? "LATCHED INPUT" : "NOT DEFINED"},
    {name:"HS sources",title:"Six identity-resolved proxies",detail:"Six chemical feedforward routes only",state:"FEEDFORWARD ONLY"},
    {name:"DNp15",title:"Bilateral continuous readout",detail:"R−L · model diagnostic only",state:"CONTINUOUS"},
    {name:"Orientation",title:"Exploratory orientation response",detail:"yaw_drive_eq → yaw_orientation_eq",state:"NO TRANSLATION"},
    {name:"Next view ↺",title:"Next completed interval",detail:"Delayed closed-loop update",state:"NEXT-INTERVAL FEEDBACK"},
  ];
  return <>
    <CausalChain stages={stages} step={frame.step} time={frame.time_ms} loop/>
    <section className="scenario-telemetry course-telemetry" aria-label="Scientific telemetry">
      <TelemetryValue label="Model-space orientation" value={signed(frame.yaw_orientation_eq,9)} unit="yaw_orientation_eq" meaning="No translation"/>
      <TelemetryValue label="Motion descriptor · R / L" value={`R ${signed(frame.input_descriptor.R)} / L ${signed(frame.input_descriptor.L)}`} unit="horizontal_motion_eq" meaning="Uncalibrated view-motion observation"/>
      <TelemetryValue label="DNp15 · R / L" value={`R ${signed(frame.dnp15_states[0])} / L ${signed(frame.dnp15_states[1])}`} unit="dnp15_state_eq" meaning="Continuous proxy states; event semantics not defined"/>
      <TelemetryValue label="Bilateral differential · R−L" value={signed(frame.bilateral_differential)} unit="dnp15_state_eq" meaning="Model diagnostic only"/>
      <TelemetryValue label="Exploratory orientation drive" value={signed(frame.yaw_drive_eq)} unit="yaw_drive_eq" meaning="Frozen neural-to-orientation transform"/>
      <TelemetryValue label="Observation clipping" value={frame.observation_clipped ? "YES" : "NO"} meaning={`${result.summary.clipping_count} / ${result.summary.observed_interval_count} intervals clipped`}/>
    </section>
    <p className="course-mode"><strong>MARGINAL ORIENTATION MODE</strong> · Motion modes decay, but the model senses visual-motion changes, not absolute heading error. Orientation settles at a nonzero residual offset. No translation.</p>
    <details className="scenario-details"><summary>Six HS identities & geometric observation</summary>
      <ul>{result.sources.map((n,i)=><li key={n.body_id}>{n.type} {n.side} · {n.body_id}: {signed(frame.hs_states[i])} dimensionless_signed_proxy</li>)}</ul>
      <p>relative_view_eq: {signed(frame.relative_view_eq)}; previous orientation: {frame.previous_orientation_eq===null ? "No previous boundary" : signed(frame.previous_orientation_eq)}.</p>
      <p>{o ? `Observed interval ${o.interval_start_ms.toFixed(1)}–${o.interval_end_ms.toFixed(1)} ms; raw geometric motion ${signed(o.raw_view_motion_eq_per_ms)} relative_view_eq per model ms; unclipped descriptor ${signed(o.normalized_unclipped)}.` : "Boundary zero has no completed observation interval."}</p>
      <p>Motion at this boundary is latched for the next neural interval. The final boundary is an observation/readout only; no extra scientific tick is rendered.</p>
      <p>External perturbation: {result.perturbation.increment_eq} yaw_orientation_eq in interval {result.perturbation.start_step}→{result.perturbation.end_step}. Current outgoing increment: {frame.external_orientation_increment_eq===null ? "Experiment complete" : signed(frame.external_orientation_increment_eq)}.</p>
    </details>
    <details className="scenario-details"><summary>Scientific provenance, analysis & claim limits</summary>
      <h3>Dataset / experiment authority</h3><p>{p.neural.dataset} · {result.condition_id}. All scientific values originate from validated backend replay. Presentation interpolation cannot update science.</p>
      <h3>Analytical model context</h3><p>Local motion spectral radius {p.analysis.local_motion_spectral_radius}; orientation eigenvalue = {p.analysis.orientation_eigenvalue}. Clipping is not required for local stability. Finite 50 ms horizon; no absolute-heading restoration claim.</p>
      <p>The open-loop control is stationary after the imposed step. Closed-loop feedback introduces subsequent counter-motion; it is not claimed to reduce motion relative to that stationary control.</p>
      <h3>Active circuit</h3><p>Six active chemical routes; structural contacts are provenance, not physiological efficacy:</p><ul>{p.neural.active_routes.map(e=><li key={e.source_id}>{e.source_id} → {e.target_id}: {e.structural_count} structural contacts</li>)}</ul>
      <h3>Excluded context</h3><p>Verified context — excluded from active model: {p.neural.excluded_routes.map(e=>`${e.source_id}→${e.target_id}`).join(", ")}. Electrical coupling also excluded. {p.neural.context_decision}.</p>
      <h3>Experiment / model contracts</h3><AuthorityIds ids={{"Phase24 selection":p.neural.selection_id,"Phase25 preregistration":p.neural.preregistration_id,"Phase25 artifact":p.neural_artifact_id,"Phase26 context audit":p.neural.context_audit_id,"Phase28 evidence":p.orientation_evidence_id,"Phase28 preregistration":p.orientation_preregistration_id,"Phase28 artifact":p.orientation_artifact_id,"Phase29 observation":p.observation_contract_id,"Phase30 preregistration":p.closed_loop_preregistration_id,"Phase30 analysis":p.analysis.analysis_id,"Phase30 artifact":result.artifact_id,"Config":p.config_sha256,"Result":p.result_sha256}}/>
      <h3>Units / claim limits</h3><ul>{result.scientific_limitations.map(s=><li key={s}>{s}</li>)}</ul>
    </details>
  </>;
}
