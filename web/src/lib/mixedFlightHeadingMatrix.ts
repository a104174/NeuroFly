/** V10.8J evaluation only: invokes the unchanged V10.8I runner; never chooses motor commands. */
import {flightCanonical,flightHash,initialFlightFrame,flightBounds,FLIGHT_MODEL,type FlightCommand} from './engineeringFlight';
import {observeFlightArena} from './flightArenaObservations';
import {locomotionBounds} from './experimentalLocomotion';
import {LANDING_RECOVERY_PROTOCOL} from './mixedGroundFlight';
import {LANDING_RECOVERY_VERIFICATION,runMixedLandingRecovery} from './mixedFlightLandingRecovery';
import type {NeuralArtifact} from './neuralLocomotion';

export const HEADING_MATRIX_PROTOCOL={
  schema:'mixed_flight_heading_robustness_v1',reference_revision:'86487b577fdef9bab69b0414136f1b32158b3b8f',
  headings_rad:Array.from({length:8},(_,k)=>k*Math.PI/4),repeats:2,
  controller:LANDING_RECOVERY_PROTOCOL,initial:initialFlightFrame(),changed_variable:'INITIAL_HEADING_ONLY',
  maximum_horizon_s:60,first_landing_deadline_s:30,existing_initial_flight_cap_s:30,
  early_termination:'RETAIN_EXISTING_FAILURE_NO_EXTENSION; UNOBSERVED_REMAINDER_IS_CENSORED',
  recovery_duration:'CONTIGUOUS_ACTIVE_OVERRIDE_INTERVALS_ONLY_NOT_ALL_SUBSEQUENT_EXPLORATION',
  interval_s:FLIGHT_MODEL.dt_s,randomness:'NONE',seed:null,
} as const;
type Run=ReturnType<typeof runMixedLandingRecovery>;
type Interval=Run['intervals'][number];
type Native={command?:FlightCommand;decision?:{command:FlightCommand}};
const command=(i:Interval)=>(i.native_evidence as Native).command??(i.native_evidence as Native).decision?.command;
const clearance=(i:Interval)=>Math.min(i.observation.forward_wall_clearance_units,i.observation.left_wall_clearance_units,i.observation.right_wall_clearance_units);
const event=(i:Interval|undefined)=>i?{observation_index:i.global_step,observation_time_s:i.global_time_s,result_index:i.accepted.step,result_time_s:i.accepted.time}:null;
const minOrNull=(values:number[])=>values.length?Math.min(...values):null;

export function classifyHeadingLanding(time:number|null,unsafe=false,reproduced=true){
  if(time!==null&&(!Number.isFinite(time)||time<0||time>60))throw new Error('Invalid first-landing time');
  return !reproduced?'E_REPRODUCTION_INCONSISTENCY':unsafe?'D_INVALID_OR_UNSAFE':time===null?'C_NO_LANDING_OBSERVED':time<=30?'A_WITHIN_30_S':'B_AFTER_30_S';
}

/** Analyze actual accepted records. Structural mismatches are errors, not invented failure metrics. */
export function summarizeMixedHeadingRun(run:Run,heading:number,authority:NeuralArtifact){
  if(!HEADING_MATRIX_PROTOCOL.headings_rad.includes(heading)||
      run.schema!=='mixed_ground_flight_landing_recovery_result_v1'||
      flightCanonical(run.configuration)!==flightCanonical({...LANDING_RECOVERY_PROTOCOL,initial_heading:heading})||
      flightCanonical(run.initial)!==flightCanonical({...initialFlightFrame(),heading})||
      flightCanonical(run.verification.protocol)!==flightCanonical(LANDING_RECOVERY_VERIFICATION)||
      !run.intervals.length||run.intervals.length>3000)throw new Error('Malformed heading evidence identity/configuration');
  const bounds=flightBounds(),groundBounds=locomotionBounds(authority.config.body);
  const safety={rejected_commands:0,nonfinite_observations:0,nonfinite_accepted_states:0,wall_contacts:0,floor_contacts:0,ceiling_contacts:0,
    conservative_bound_violations:0,invalid_handoff_attempts:0,illegal_physical_transitions:0,
    maximum_handoff_position_discontinuity:Math.max(0,...run.handoffs.map(h=>h.position_discontinuity)),
    maximum_handoff_heading_discontinuity:Math.max(0,...run.handoffs.map(h=>h.heading_discontinuity)),maximum_timestamp_discontinuity:0};
  const contactEvents:{source:Interval['active_engine'];global_step:number;time_s:number;boundary:string;ground_path_units:number;retakeoff_eligible:boolean;before:Interval['accepted'];after:Interval['accepted']}[]=[];
  const legal:Record<string,string[]>={grounded:['takeoff'],takeoff:['flying','landing'],flying:['landing'],landing:['grounded']};
  let previous=run.initial;
  for(const [n,i] of run.intervals.entries()){
    const metadata=i.landing_recovery;
    if(i.global_step!==n||i.global_time_s!==n*.02||i.accepted.step!==n+1||
        flightCanonical(i.observation.accepted)!==flightCanonical(previous)||
        !['flight_initial','flight_resumed','ground'].includes(i.active_engine)||
        metadata?.controller_id!==LANDING_RECOVERY_PROTOCOL.schema||metadata.context!==i.active_engine||
        metadata.observation_global_step!==n||metadata.observation_global_time_s!==i.global_time_s||
        metadata.resulting_global_step!==n+1||metadata.resulting_global_time_s!==i.accepted.time)
      throw new Error('Malformed heading evidence interval alignment at '+n);
    const numericObservation=[...i.observation.accepted.position,...i.observation.accepted.velocity,i.observation.accepted.heading,
      i.observation.forward_wall_clearance_units,i.observation.left_wall_clearance_units,i.observation.right_wall_clearance_units,
      i.observation.floor_clearance_units,i.observation.ceiling_clearance_units,i.observation.horizontal_speed_units_s];
    if(!numericObservation.every(Number.isFinite))safety.nonfinite_observations++;
    if(![...i.accepted.position,...i.accepted.velocity,i.accepted.heading,i.accepted.time].every(Number.isFinite))safety.nonfinite_accepted_states++;
    const applicable=i.active_engine==='ground'?{min:[-groundBounds[0],bounds.min[1],-groundBounds[1]] as [number,number,number],max:[groundBounds[0],bounds.max[1],groundBounds[1]] as [number,number,number]}:bounds;
    if(i.accepted.position.some((v,a)=>v<applicable.min[a]||v>applicable.max[a]))safety.conservative_bound_violations++;
    if(flightCanonical(observeFlightArena(previous,applicable))!==flightCanonical(i.observation))throw new Error('Malformed geometric observation at '+n);
    if(i.active_engine!=='ground'&&command(i)?.step!==i.source_local_step)throw new Error('Malformed motor interval alignment at '+n);
    safety.maximum_timestamp_discontinuity=Math.max(safety.maximum_timestamp_discontinuity,Math.abs(i.accepted.time-(n+1)*.02));
    let physical=previous.state;
    for(const e of i.accepted.events){
      if(e.kind==='REJECTED_COMMAND')safety.rejected_commands++;
      if(e.kind==='CONTACT'){
        contactEvents.push({source:i.active_engine,global_step:i.accepted.step,time_s:e.time,boundary:e.detail,
          ground_path_units:i.sustained!.ground_path_since_landing,retakeoff_eligible:i.sustained!.retakeoff_eligible,before:i.observation.accepted,after:i.accepted});
        if(e.detail==='FLOOR')safety.floor_contacts++;
        else if(e.detail==='CEILING')safety.ceiling_contacts++;
        else if(['X_WALL','Z_WALL'].includes(e.detail))safety.wall_contacts++;
      }
      if(e.kind==='TRANSITION'){
        const [from,to]=e.detail.split('->');
        if(from!==physical||!legal[physical]?.includes(to))safety.illegal_physical_transitions++;
        physical=to as typeof physical;
      }
    }
    if(physical!==i.accepted.state)safety.illegal_physical_transitions++;
    previous=i.accepted;
  }
  if(run.failure&&/handoff|initialization mismatch/i.test(run.failure))safety.invalid_handoff_attempts++;
  const unsafeFailure=!!run.failure&&/invalid|non.?finite|outside|bounds|contact|illegal|rejected|misaligned/i.test(run.failure);
  // Intended FLOOR contacts are counted separately from safety violations.
  const unsafeCount=safety.rejected_commands+safety.nonfinite_observations+safety.nonfinite_accepted_states+safety.wall_contacts+safety.ceiling_contacts+
    safety.conservative_bound_violations+safety.invalid_handoff_attempts+safety.illegal_physical_transitions+
    safety.maximum_handoff_position_discontinuity+safety.maximum_handoff_heading_discontinuity+safety.maximum_timestamp_discontinuity;
  const flying=run.intervals.filter(i=>i.observation.accepted.state==='flying');
  const active=run.intervals.filter(i=>i.landing_recovery?.policy?.active);
  const firstRecovery=active.find(i=>i.active_engine==='flight_initial');
  const firstLand=run.intervals.find(i=>i.accepted.events.some(e=>e.kind==='TRANSITION'&&e.detail==='landing->grounded'));
  const firstRequest=run.intervals.find(i=>i.active_engine!=='ground'&&command(i)?.intent==='LAND');
  const initialFlying=flying.filter(i=>i.active_engine==='flight_initial'&&i.global_step>=(firstRecovery?.global_step??0));
  const firstSufficient=initialFlying.find(i=>clearance(i)>=.06);
  const episodes='episodes' in run.metrics?run.metrics.episodes:[];
  const ground=episodes.find(e=>e.type==='ground');
  const final=run.intervals.at(-1)!;
  return {heading_rad:heading,initial_admissible:true,classification:classifyHeadingLanding(firstLand?.accepted.time??null,unsafeFailure||unsafeCount>0),
    first_flying_time_s:run.metrics.airborne_start_time_s,first_recovery:event(active[0]),first_initial_recovery:event(firstRecovery),
    recovery_episode_count:active.filter(i=>!run.intervals[i.global_step-1]?.landing_recovery?.policy?.active).length,
    initial_recovery_count:active.filter(i=>i.active_engine==='flight_initial').length,recovery_active_duration_s:active.length*.02,
    minimum_observed_flying_clearance_units:minOrNull(flying.map(clearance)),first_sufficient_initial_clearance:event(firstSufficient),
    first_land_request:event(firstRequest),first_landing_time_s:firstLand?.accepted.time??null,
    first_walking_episode:ground?{start_s:ground.start_s,end_s:ground.end_s,duration_s:ground.duration_s,path_units:ground.distance_units,complete:ground.complete}:null,
    first_retakeoff:event(run.intervals.find(i=>i.active_engine==='flight_resumed'&&command(i)?.intent==='TAKEOFF')),
    takeoffs:'takeoff_count' in run.metrics?run.metrics.takeoff_count:0,landings:'landing_count' in run.metrics?run.metrics.landing_count:0,
    airborne_duration_s:run.metrics.airborne_duration_s,walking_duration_s:run.metrics.walking_duration_s,walking_path_units:run.metrics.walking_distance_units,
    horizontal_path_units:run.metrics.horizontal_distance_units,x_extent_units:run.metrics.explored_x_extent_units,z_extent_units:run.metrics.explored_z_extent_units,
    final_pose:final.accepted,final_controller_phase:final.controller_phase_after,actual_end_s:final.accepted.time,
    termination:run.termination,failure:run.failure,window_completed:run.termination==='DURATION_WINDOW_COMPLETED',
    ground_continuation:run.verification.continuation_passed,safety,contact_events:contactEvents,
    recovery_activations:active.map(i=>{
      const episode=run.intervals.filter(j=>j.sustained?.episode_id===i.sustained?.episode_id&&j.global_step>=i.global_step);
      const subsequent=episode.find(j=>j.global_step>i.global_step&&clearance(j)>=.06);
      const landed=episode.find(j=>j.accepted.state==='grounded');
      return {...event(i)!,source_local_step:i.source_local_step,context:i.active_engine,episode_id:i.sustained!.episode_id,preceding_state:i.observation.accepted,
        phase:i.controller_phase_before,observed_clearance:clearance(i),eligible:i.landing_recovery!.policy!.eligible,command:command(i)!,resulting_state:i.accepted,
        next_clearance_units:episode[1]?clearance(episode[1]):null,first_subsequent_sufficient_clearance:event(subsequent),
        eventual_landing_time_s:landed?.accepted.time??null,episode_outcome:landed?'LANDED':run.failure??'CENSORED_AT_FINITE_END'};
    })};
}

/** Only compact measurements/hashes are retained; complete native evidence is compared pairwise then released. */
export async function runMixedHeadingMatrix(authority:NeuralArtifact,onCondition?:(row:unknown)=>void){
  const rows=[];
  for(const heading of HEADING_MATRIX_PROTOCOL.headings_rad){
    const a=runMixedLandingRecovery(authority,heading),b=runMixedLandingRecovery(authority,heading);
    const summary=summarizeMixedHeadingRun(a,heading,authority);
    const hashes=[await flightHash(a),await flightHash(b)];
    const reproduced=flightCanonical(a)===flightCanonical(b)&&hashes[0]===hashes[1];
    const row={...summary,reproduced,canonical_hashes:hashes};rows.push(row);onCondition?.(row);
    if(!reproduced)throw new Error('Heading matrix reproducibility failure at '+heading);
    if(summary.safety.nonfinite_observations||summary.safety.nonfinite_accepted_states)throw new Error('Unsafe non-finite heading matrix state');
  }
  return {protocol:HEADING_MATRIX_PROTOCOL,rows,aggregate:{conditions:rows.length,canonical_runs:rows.length*2,
    first_landing_within_30_s:rows.filter(r=>r.first_landing_time_s!==null&&r.first_landing_time_s<=30).length,
    first_landing_by_60_s:rows.filter(r=>r.first_landing_time_s!==null&&r.first_landing_time_s<=60).length,
    ground_continuation:rows.filter(r=>r.ground_continuation).length,recovery_required:rows.filter(r=>r.recovery_episode_count>0).length,
    initial_recovery_required:rows.filter(r=>r.initial_recovery_count>0).length,
    failed_or_incomplete:rows.filter(r=>!r.window_completed).length,unsafe:rows.filter(r=>r.classification==='D_INVALID_OR_UNSAFE').length,
    reproduced:rows.filter(r=>r.reproduced).length}};
}
