/** Typed reduced Phase30 transport. Validation and visual interpolation only. */
import { parseScenarioDefinition, type ScenarioDefinition, type NeuralIdentity, type NeuralPlaybackResult } from "./scenarioPlayback";

export interface CourseObservation {
  interval_start_step: number; interval_end_step: number;
  interval_start_ms: number; interval_end_ms: number;
  raw_view_motion_eq_per_ms: number; normalized_unclipped: number;
  global_horizontal_motion_eq: number; clipped: boolean;
}
export interface CoursePlaybackFrame {
  step: number; time_ms: number; yaw_orientation_eq: number;
  previous_orientation_eq: number | null; relative_view_eq: number;
  observation: CourseObservation | null; input_descriptor: { R: number; L: number };
  hs_states: number[]; dnp15_states: number[]; bilateral_differential: number;
  yaw_drive_eq: number; observation_clipped: boolean;
  external_orientation_increment_eq: number | null;
}
export interface CoursePlaybackResult {
  schema: "scenario_playback_v1"; presentation_kind: "EXPLORATORY_CLOSED_LOOP_MODEL";
  artifact_id: string; run_id: string; scenario: ScenarioDefinition;
  condition_id: "CLOSED_LOOP_PERTURBATION"; dt_ms: number; duration_ms: number;
  statuses: { execution_completed: boolean; orientation_feedback_connected: true; orientation_feedback_realized: boolean;
    translation: "NOT_MODELLED"; absolute_heading_error_signal: false; event_semantics: "NOT_DEFINED";
    recurrence_active: false; electrical_coupling_active: false };
  world_reference: { reference_id: "WORLD_FIXED_HEADING_ZERO"; heading_eq: number; period_eq: 1; units: "world_heading_eq" };
  sources: NeuralIdentity[]; targets: NeuralIdentity[];
  input_units: "horizontal_motion_eq"; source_units: "dimensionless_signed_proxy"; target_units: "dnp15_state_eq";
  orientation_units: "yaw_orientation_eq"; yaw_drive_units: "yaw_drive_eq"; view_units: "relative_view_eq";
  provenance: { neural: NeuralPlaybackResult["provenance"]; neural_artifact_id: string;
    orientation_evidence_id: string; orientation_preregistration_id: string; orientation_artifact_id: string;
    observation_contract_id: string; closed_loop_preregistration_id: string; config_sha256: string; result_sha256: string;
    analysis: { analysis_id: string; stage_a_decision: "CLOSED_LOOP_COMPOSITION_MARGINAL_BUT_BOUNDED_FOR_FINITE_HORIZON_TEST";
      classification: "MARGINAL_ORIENTATION_MODE"; local_motion_spectral_radius: number;
      orientation_eigenvalue: 1; clipping_required_for_local_stability: false } };
  summary: { initial_perturbation_eq: number; final_orientation_eq: number; clipping_count: number;
    observed_interval_count: number; clipping_duration_ms: number };
  perturbation: { start_step: number; end_step: number; increment_eq: number };
  termination: { status: "COMPLETED_VALID_HORIZON"; step: number; time_ms: number };
  frames: CoursePlaybackFrame[]; scientific_limitations: string[]; source_operation: "VALIDATED_CANONICAL_REPLAY";
}
function invalid(): never { throw new Error("Malformed authoritative course-control playback payload."); }
function obj(v: unknown): Record<string, unknown> { return v && typeof v === "object" && !Array.isArray(v) ? v as Record<string, unknown> : invalid(); }
function num(v: unknown): number { return typeof v === "number" && Number.isFinite(v) ? v : invalid(); }
function str(v: unknown): string { return typeof v === "string" ? v : invalid(); }
function int(v: unknown): number { const n=num(v); return Number.isInteger(n) && n >= 0 ? n : invalid(); }
function bool(v: unknown): boolean { return typeof v === "boolean" ? v : invalid(); }
function lit<T extends string | number | boolean>(v: unknown, value: T): T { return v === value ? value : invalid(); }
function list<T>(v: unknown, parser: (v: unknown)=>T): T[] { return Array.isArray(v) ? v.map(parser) : invalid(); }
function maybe<T>(v: unknown, parser: (v: unknown)=>T): T | null { return v === null ? null : parser(v); }
function hash(v: unknown): string { const h=str(v); return /^[0-9a-f]{64}$/.test(h) ? h : invalid(); }
function descriptor(v: unknown): number { const n=num(v); return n >= -1 && n <= 1 ? n : invalid(); }
function forbidden(r: Record<string, unknown>) { if (["body","object","actuator_commands","total_dnp01_spikes","dnp01_spike_body_ids","torque","angular_velocity","spikes"].some(k=>k in r)) invalid(); }
function close(a: number,b: number) { return Math.abs(a-b) < 1e-10; }

export function parseCoursePlayback(v: unknown): CoursePlaybackResult {
  const r=obj(v), s=obj(r.statuses), w=obj(r.world_reference), p=obj(r.provenance), n=obj(p.neural), a=obj(p.analysis), summary=obj(r.summary), perturb=obj(r.perturbation), term=obj(r.termination);
  forbidden(r);
  const identity=(v:unknown):NeuralIdentity=>{const n=obj(v);const type=str(n.type),side=str(n.side);if (!["HSN","HSE","HSS","DNp15"].includes(type) || !["R","L"].includes(side))return invalid();return {body_id:int(n.body_id),type:type as NeuralIdentity["type"],side:side as NeuralIdentity["side"]};};
  const sources=list(r.sources,identity),targets=list(r.targets,identity);
  const expected=[[10015,"HSN","R"],[10016,"HSE","R"],[10023,"HSS","R"],[10034,"HSE","L"],[10181,"HSN","L"],[10419,"HSS","L"],[11215,"DNp15","R"],[12069,"DNp15","L"]];
  if(sources.length!==6 || targets.length!==2 || [...sources,...targets].some((n,i)=>n.body_id!==expected[i][0] || n.type!==expected[i][1] || n.side!==expected[i][2]))return invalid();
  const route=(v:unknown)=>{const e=obj(v);return {source_id:int(e.source_id),target_id:int(e.target_id),structural_count:int(e.structural_count)};};
  const active=list(n.active_routes,route),excluded=list(n.excluded_routes,route);
  const keys=(edges:typeof active)=>edges.map(e=>`${e.source_id}:${e.target_id}`).sort().join(",");
  if(keys(active)!==["10015:11215","10016:11215","10023:11215","10034:12069","10181:12069","10419:12069"].sort().join(",") || keys(excluded)!==["10015:10016","10016:10015","10016:10023","10034:10181","10034:10419","10419:10034","12069:10419"].sort().join(","))return invalid();
  const dt=num(r.dt_ms),duration=num(r.duration_ms);
  const frames=list(r.frames,(v):CoursePlaybackFrame=>{const f=obj(v),input=obj(f.input_descriptor);forbidden(f);
    const hs=list(f.hs_states,num),dn=list(f.dnp15_states,num);if(hs.length!==6 || dn.length!==2)return invalid();
    const observation=maybe(f.observation,v=>{const o=obj(v);return {interval_start_step:int(o.interval_start_step),interval_end_step:int(o.interval_end_step),interval_start_ms:num(o.interval_start_ms),interval_end_ms:num(o.interval_end_ms),raw_view_motion_eq_per_ms:num(o.raw_view_motion_eq_per_ms),normalized_unclipped:num(o.normalized_unclipped),global_horizontal_motion_eq:descriptor(o.global_horizontal_motion_eq),clipped:bool(o.clipped)};});
    return {step:int(f.step),time_ms:num(f.time_ms),yaw_orientation_eq:num(f.yaw_orientation_eq),previous_orientation_eq:maybe(f.previous_orientation_eq,num),relative_view_eq:num(f.relative_view_eq),observation,input_descriptor:{R:descriptor(input.R),L:descriptor(input.L)},hs_states:hs,dnp15_states:dn,bilateral_differential:num(f.bilateral_differential),yaw_drive_eq:num(f.yaw_drive_eq),observation_clipped:bool(f.observation_clipped),external_orientation_increment_eq:maybe(f.external_orientation_increment_eq,num)};
  });
  if(dt!==.1 || duration!==50 || frames.length!==501)return invalid();
  frames.forEach((f,i)=>{
    const o=f.observation;
    if(f.step!==i || !close(f.time_ms,i*dt) || !close(f.bilateral_differential,f.dnp15_states[0]-f.dnp15_states[1]) || !close(f.yaw_drive_eq,f.bilateral_differential))invalid();
    if(i===0){if(o!==null || f.previous_orientation_eq!==null || f.observation_clipped)invalid();}
    else if(!o || o.interval_start_step!==i-1 || o.interval_end_step!==i || !close(o.interval_start_ms,(i-1)*dt) || !close(o.interval_end_ms,i*dt) || f.previous_orientation_eq!==frames[i-1].yaw_orientation_eq || o.clipped!==f.observation_clipped || o.global_horizontal_motion_eq!==f.input_descriptor.R || f.input_descriptor.L!==-f.input_descriptor.R)invalid();
  });
  if(!close(num(summary.final_orientation_eq),frames.at(-1)!.yaw_orientation_eq) || int(summary.observed_interval_count)!==500 || int(summary.clipping_count)!==frames.filter(f=>f.observation_clipped).length || !close(num(summary.clipping_duration_ms),int(summary.clipping_count)*dt) || int(term.step)!==500 || num(term.time_ms)!==duration)invalid();
  const radius=num(a.local_motion_spectral_radius);if(radius<=0 || radius>=1)invalid();
  const scenario=parseScenarioDefinition(r.scenario);if(scenario.id!=="EXPLORATORY_COURSE_CONTROL")invalid();
  return {schema:lit(r.schema,"scenario_playback_v1"),presentation_kind:lit(r.presentation_kind,"EXPLORATORY_CLOSED_LOOP_MODEL"),artifact_id:hash(r.artifact_id),run_id:hash(r.run_id),scenario,condition_id:lit(r.condition_id,"CLOSED_LOOP_PERTURBATION"),dt_ms:dt,duration_ms:duration,
    statuses:{execution_completed:bool(s.execution_completed),orientation_feedback_connected:lit(s.orientation_feedback_connected,true),orientation_feedback_realized:bool(s.orientation_feedback_realized),translation:lit(s.translation,"NOT_MODELLED"),absolute_heading_error_signal:lit(s.absolute_heading_error_signal,false),event_semantics:lit(s.event_semantics,"NOT_DEFINED"),recurrence_active:lit(s.recurrence_active,false),electrical_coupling_active:lit(s.electrical_coupling_active,false)},
    world_reference:{reference_id:lit(w.reference_id,"WORLD_FIXED_HEADING_ZERO"),heading_eq:num(w.heading_eq),period_eq:lit(w.period_eq,1),units:lit(w.units,"world_heading_eq")},sources,targets,
    input_units:lit(r.input_units,"horizontal_motion_eq"),source_units:lit(r.source_units,"dimensionless_signed_proxy"),target_units:lit(r.target_units,"dnp15_state_eq"),orientation_units:lit(r.orientation_units,"yaw_orientation_eq"),yaw_drive_units:lit(r.yaw_drive_units,"yaw_drive_eq"),view_units:lit(r.view_units,"relative_view_eq"),
    provenance:{neural:{dataset:lit(n.dataset,"male-cns:v1.0"),selection_id:hash(n.selection_id),preregistration_id:hash(n.preregistration_id),context_audit_id:hash(n.context_audit_id),context_decision:lit(n.context_decision,"FEEDFORWARD_MOTIF_REMAINS_CURRENT_VALIDATED_BOUNDARY"),active_routes:active,excluded_routes:excluded},neural_artifact_id:hash(p.neural_artifact_id),orientation_evidence_id:hash(p.orientation_evidence_id),orientation_preregistration_id:hash(p.orientation_preregistration_id),orientation_artifact_id:hash(p.orientation_artifact_id),observation_contract_id:hash(p.observation_contract_id),closed_loop_preregistration_id:hash(p.closed_loop_preregistration_id),config_sha256:hash(p.config_sha256),result_sha256:hash(p.result_sha256),analysis:{analysis_id:hash(a.analysis_id),stage_a_decision:lit(a.stage_a_decision,"CLOSED_LOOP_COMPOSITION_MARGINAL_BUT_BOUNDED_FOR_FINITE_HORIZON_TEST"),classification:lit(a.classification,"MARGINAL_ORIENTATION_MODE"),local_motion_spectral_radius:radius,orientation_eigenvalue:lit(a.orientation_eigenvalue,1),clipping_required_for_local_stability:lit(a.clipping_required_for_local_stability,false)}},
    summary:{initial_perturbation_eq:num(summary.initial_perturbation_eq),final_orientation_eq:num(summary.final_orientation_eq),clipping_count:int(summary.clipping_count),observed_interval_count:int(summary.observed_interval_count),clipping_duration_ms:num(summary.clipping_duration_ms)},perturbation:{start_step:int(perturb.start_step),end_step:int(perturb.end_step),increment_eq:num(perturb.increment_eq)},termination:{status:lit(term.status,"COMPLETED_VALID_HORIZON"),step:int(term.step),time_ms:num(term.time_ms)},frames,scientific_limitations:list(r.scientific_limitations,str),source_operation:lit(r.source_operation,"VALIDATED_CANONICAL_REPLAY")};
}

/** Interpolation is display-only. One declared abstract cycle is 2π render radians.
 * Telemetry selects an exact authoritative boundary; no observation/integration. */
export function courseScene(result:CoursePlaybackResult,cursor:number) {
  const c=Math.max(0,Math.min(result.frames.length-1,cursor)),i=Math.floor(c),t=c-i;
  const frame=result.frames[i],next=result.frames[Math.min(i+1,result.frames.length-1)];
  const orientation=frame.yaw_orientation_eq+(next.yaw_orientation_eq-frame.yaw_orientation_eq)*t;
  const relativeView=frame.relative_view_eq+(next.relative_view_eq-frame.relative_view_eq)*t;
  return {frame,renderRotation:orientation/result.world_reference.period_eq*2*Math.PI,relativeView};
}
