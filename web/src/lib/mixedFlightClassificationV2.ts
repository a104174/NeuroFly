/** Separate interpretation of immutable V10.8J evidence; no motor decisions. */
import {flightHash,FlightEngine,createFlightTrial,FLIGHT_MODEL} from './engineeringFlight';
import type {runMixedHeadingMatrix} from './mixedFlightHeadingMatrix';
type Matrix=Awaited<ReturnType<typeof runMixedHeadingMatrix>>;type Row=Matrix['rows'][number];
export const CLASSIFICATION_V2={schema:'mixed_flight_heading_classification_v2',version:2,function_id:'classifyMixedHeadingV2_v2',source_matrix_sha256:'ec419ea63d839eaf58a0451a86980eecb9c82ea472552ed04d53f341bc367468',handoff_reference:'docs/science/ground_contact_handoff_admissibility_v10_8k.md'} as const;
const keys=['nonfinite_observations','nonfinite_accepted_states','conservative_bound_violations','invalid_handoff_attempts','illegal_physical_transitions','maximum_handoff_position_discontinuity','maximum_handoff_heading_discontinuity','maximum_timestamp_discontinuity','rejected_commands'] as const;
export function classifyMixedHeadingV2(row:Partial<Omit<Row,'safety'>>&{safety?:Partial<Row['safety']>}){
 const failures=keys.filter(k=>typeof row.safety?.[k]==='number'&&row.safety[k]!>0);
 const complete=keys.every(k=>typeof row.safety?.[k]==='number'&&Number.isFinite(row.safety[k])&&row.safety[k]!>=0);
 const t=row.first_landing_time_s;
 const landing=typeof t==='number'&&Number.isFinite(t)&&t>=0&&t<=60?(t<=30?'WITHIN_30_SECONDS':'AFTER_30_SECONDS'):t===null&&row.actual_end_s===60?'NOT_REACHED_WITHIN_HORIZON':'UNDETERMINED';
 const events=row.contact_events?.map(e=>{
  const kind=['X_WALL','Z_WALL'].includes(e.boundary)?e.source==='ground'?'GROUND_WALL':'FLIGHT_WALL':['FLOOR','CEILING'].includes(e.boundary)?e.boundary:'UNCLASSIFIED';
  let destination_admissible:boolean|null=null;
  if(e.source==='ground')try{new FlightEngine(createFlightTrial([],1500),FLIGHT_MODEL.arena,{position:e.after.position,heading:e.after.heading,velocity:e.after.velocity});destination_admissible=true;}catch{destination_admissible=false;}
  return {kind,time_s:e.time_s,source:e.source,destination_admissible,eligible:e.retakeoff_eligible,handoff_attempted:e.source==='ground'&&!e.retakeoff_eligible?false:null,postponement:e.source==='ground'&&!e.retakeoff_eligible?'RECORDED_INELIGIBILITY; AUDIT_PROBE_IS_NOT_AN_ATTEMPT':null};
 })??null;
 const hk=['invalid_handoff_attempts','maximum_handoff_position_discontinuity','maximum_handoff_heading_discontinuity'] as const;
 return {heading_rad:row.heading_rad??null,behavior:{first_landing:landing,first_landing_time_s:t??null,continuation:row.window_completed===true&&row.ground_continuation===true?'COMPLETED':row.window_completed===false||row.ground_continuation===false?'INCOMPLETE':'UNDETERMINED'},
 integrity:{status:failures.length?'FAIL':complete?'PASS':'UNDETERMINED',failure_fields:failures,diagnostic_fields:row.safety??null,rejected_command_policy:'FAIL: EXISTING FEEDBACK CONTRACT REQUIRES ACCEPTANCE'},
 contacts:{events,observed:events===null?null:events.length>0,penetration_count:row.safety?.conservative_bound_violations??null},
 handoffs:{status:hk.some(k=>(row.safety?.[k]??0)>0)?'FAIL':hk.every(k=>row.safety?.[k]===0)?'PASS':'UNDETERMINED',accepted_ground_to_flight_count:typeof row.takeoffs==='number'?Math.max(0,row.takeoffs-1):null,attempted_count:null,rejected_count:row.safety?.invalid_handoff_attempts??null,limitation:'No explicit attempt counter; counts derive from source diagnostics and accepted transitions'},
 reproducibility:row.reproduced===true?'PASS':row.reproduced===false?'FAIL':'UNDETERMINED',source_run_hashes:row.canonical_hashes??null};
}
export async function classifyHeadingMatrixV2(source:Matrix){
 const hash=await flightHash(source);if(hash!==CLASSIFICATION_V2.source_matrix_sha256)throw new Error('Source V10.8J matrix identity mismatch');
 return {classification:CLASSIFICATION_V2,source_protocol:source.protocol,source_evidence_sha256:hash,rows:source.rows.map(classifyMixedHeadingV2)};
}
