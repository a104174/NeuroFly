/** Fixed, heading-only model evaluation. No new controller or motor policy. */
import {flightCanonical,flightHash,initialFlightFrame,FLIGHT_MODEL} from './engineeringFlight';
import {runSustainedMixedGroundFlight,SUSTAINED_MIXED_PROTOCOL,mixedGroundFlightHash} from './mixedGroundFlight';
import type {NeuralArtifact} from './neuralLocomotion';
export const ROBUSTNESS_PROTOCOL={
 schema:'mixed_flight_heading_pair_v1',reference_revision:'9ed2979736442a7b6157eec7d2eabda2cdb0a810',
 controller:SUSTAINED_MIXED_PROTOCOL,plant:FLIGHT_MODEL.schema,
 changed_variable:'initial_heading_rad',baseline_heading:Math.PI/2,variant_heading:0,
 initial_position:initialFlightFrame().position,initial_velocity:[0,0,0],
 rationale:'Orthogonal heading at identical admissible grounded body position; no condition selected from outcomes',
 tolerance:1e-8,randomness:'NONE',seed:null,
 provenance:'Versioned evaluation metadata; actual source identified by implementing Git revision',
} as const;
type Run=ReturnType<typeof runSustainedMixedGroundFlight>;
function compare(a:Run,b:Run){
 const tolerance=ROBUSTNESS_PROTOCOL.tolerance;
 const as=[a.initial,...a.intervals.map(i=>i.accepted)],bs=[b.initial,...b.intervals.map(i=>i.accepted)];
 const length=Math.min(as.length,bs.length),intervals=Math.min(a.intervals.length,b.intervals.length);
 const event=(n:number)=>n<0?null:{index:n,time_s:n*.02};
 const fields=['forward_wall_clearance_units','left_wall_clearance_units','right_wall_clearance_units','floor_clearance_units','ceiling_clearance_units'] as const;
 const firstObservation=a.intervals.slice(0,intervals).findIndex((i,n)=>fields.some(k=>Math.abs(i.observation[k]-b.intervals[n].observation[k])>tolerance));
 const command=(i:Run['intervals'][number])=>{
   const n=i.native_evidence as {command?:{forward:number;turn:number;vertical:number;intent:string};decision?:{command:{forward:number;turn:number;vertical:number;intent:string}};interval?:{linear_velocity:number[];angular_velocity:number}};
   if(i.active_engine==='ground') return {source:'ground',scalars:[...n.interval!.linear_velocity,n.interval!.angular_velocity],intent:null};
   const c=n.command??n.decision!.command;
   return {source:'flight',scalars:[c.forward,c.turn,c.vertical],intent:c.intent};
 };
 const firstCommand=a.intervals.slice(0,intervals).findIndex((i,n)=>{
   const x=command(i),y=command(b.intervals[n]);
   return x.source!==y.source||x.intent!==y.intent||x.scalars.some((v,k)=>Math.abs(v-y.scalars[k])>tolerance);
 });
 const separations=as.slice(0,length).map((f,n)=>Math.hypot(...f.position.map((v,k)=>v-bs[n].position[k])));
 const firstState=as.slice(0,length).findIndex((f,n)=>separations[n]>tolerance||Math.abs(Math.atan2(Math.sin(f.heading-bs[n].heading),Math.cos(f.heading-bs[n].heading)))>tolerance||f.state!==bs[n].state||f.velocity.some((v,k)=>Math.abs(v-bs[n].velocity[k])>tolerance));
 const firstTransition=a.intervals.slice(0,intervals).findIndex((i,n)=>
   flightCanonical(i.accepted.events.filter(e=>e.kind==='TRANSITION'))!==flightCanonical(b.intervals[n].accepted.events.filter(e=>e.kind==='TRANSITION')));
 const max=Math.max(...separations);
 return {first_geometric_observation:event(firstObservation),first_motor_command:event(firstCommand),
   first_accepted_body_state:event(firstState),first_accepted_position:event(separations.findIndex(v=>v>tolerance)),first_different_transition_result:event(firstTransition<0?-1:firstTransition+1),
   maximum_position_separation_units:max,maximum_at:event(separations.indexOf(max)),
   common_final_boundary:event(length-1),common_final_position_separation_units:separations.at(-1)!,
   individual_final_boundaries:[{time_s:a.metrics.final_time_s,position:a.metrics.final_position},{time_s:b.metrics.final_time_s,position:b.metrics.final_position}]};
}
export function runMixedFlightHeadingPair(authority:NeuralArtifact){
 const a=runSustainedMixedGroundFlight(authority),ar=runSustainedMixedGroundFlight(authority);
 const b=runSustainedMixedGroundFlight(authority,ROBUSTNESS_PROTOCOL.variant_heading),br=runSustainedMixedGroundFlight(authority,ROBUSTNESS_PROTOCOL.variant_heading);
 if(flightCanonical(a)!==flightCanonical(ar)||flightCanonical(b)!==flightCanonical(br))throw new Error('Heading-pair deterministic reproduction failed');
 return {protocol:ROBUSTNESS_PROTOCOL,baseline:a,variant:b,comparison:compare(a,b),repeatability:{baseline:true,variant:true}};
}
export async function mixedFlightHeadingPairHashes(pair:ReturnType<typeof runMixedFlightHeadingPair>){
 return {baseline:await mixedGroundFlightHash(pair.baseline),variant:await mixedGroundFlightHash(pair.variant),pair:await flightHash(pair)};
}
