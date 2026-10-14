/** Engineering recovery only. The inherited HS/DNp15 updates are unchanged. */
import {InteractiveNeuralEngine,BODY_DT,PARITY_TOLERANCE,type RuntimeSnapshot,type Plane,type RuntimeMode,type StimulusEvent} from './interactiveNeuralLocomotion';
import type {NeuralArtifact} from './neuralLocomotion';
import type {LocomotionFrame} from './experimentalLocomotion';
export const NAVIGATION_POLICY=Object.freeze({version:'GEOMETRIC_INWARD_NORMAL_V1',margin:.06,gain:2,max_omega:1.2,duration_s:30,release:'NO_OUTWARD_COMPONENT_AT_BOUNDARY',tie:'POSITIVE_PI',combined:'SUM_NO_ADDITIONAL_CLAMP'});
export const NAVIGATION_MODE='CONNECTOME_INFORMED_NEURAL_STEERING_WITH_ENGINEERING_BOUNDARY_NAVIGATION';
type Pose={position:[number,number,number];heading:number};
export type NavigationFrame=LocomotionFrame & {boundary_summary:{distances:number[];inward:number[];omega:number;neural_omega:number;heading_error:number;active:boolean}};
export type NavigationSnapshot=RuntimeSnapshot & {neuralOmega:number;boundaryOmega:number;proximity:number;contacts:number;recoveries:number;contactSeconds:number;maxStallSeconds:number;neuralHeadingChange:number;boundaryHeadingChange:number};
export type NavigationLog={schema:'continuous_arena_navigation_event_log_v3';config:Record<string,unknown>;events:StimulusEvent[];stop_step:number;pending_plane:Plane|null;termination:'PAUSED'|'DURATION_COMPLETED'};
function stable(x:unknown):string {
 if(typeof x==='number'&&!Number.isFinite(x))throw new Error('Non-finite navigation serialization');
 if(Array.isArray(x))return `[${x.map(stable).join(',')}]`;
 if(x!==null&&typeof x==='object')return `{${Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,v])=>`${JSON.stringify(k)}:${stable(v)}`).join(',')}}`;
 const out=JSON.stringify(x);if(out===undefined)throw new Error('Unsupported navigation serialization');return out;
}
const hash=async(x:unknown)=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(stable(x)))),v=>v.toString(16).padStart(2,'0')).join('');
/** Heading zero points +Z, positive heading turns toward +X. */
export function boundarySteering(x:number,z:number,heading:number,limits:readonly number[]){
 if(![x,z,heading,...limits].every(Number.isFinite)||limits.length!==2||limits.some(v=>v<=NAVIGATION_POLICY.margin)||Math.abs(x)>limits[0]||Math.abs(z)>limits[1])throw new Error('Invalid navigation geometry/state');
 const distances=[limits[0]-x,limits[0]+x,limits[1]-z,limits[1]+z];
 const weights=distances.map(d=>Math.max(0,1-d/NAVIGATION_POLICY.margin));
 const inward=[weights[1]-weights[0],weights[3]-weights[2]],active=Math.hypot(...inward)>0;
 let error=active?Math.atan2(Math.sin(Math.atan2(inward[0],inward[1])-heading),Math.cos(Math.atan2(inward[0],inward[1])-heading)):0;
 if(Math.abs(Math.abs(error)-Math.PI)<1e-12)error=Math.PI;
 const omega=Math.max(-1.2,Math.min(1.2,NAVIGATION_POLICY.gain*error*Math.max(...weights)));
 return {distances,inward,omega,heading_error:error,active};
}
export class ContinuousNavigationEngine extends InteractiveNeuralEngine {
 private readonly navigationConfig:Record<string,unknown>;
 private neuralOmega=0;private boundaryOmega=0;private contacts=0;private recoveries=0;private contactSeconds=0;private stallSeconds=0;private maxStallSeconds=0;private neuralHeadingChange=0;private boundaryHeadingChange=0;
 private contactActive=false;
 constructor(authority:NeuralArtifact,mode:RuntimeMode='neural',initialPlane:Plane=.4,initial?:Pose){
  super(authority,mode,initialPlane);if(mode==="baseline")throw new Error("v3 requires neural computation; use output_disabled control");this.lastStep=1500;
  if(initial){if(initial.position.length!==3||initial.position[1]!==this.pose.position[1])throw new Error('Invalid initial altitude');boundarySteering(initial.position[0],initial.position[2],initial.heading,this.limits);this.pose=structuredClone(initial);this.path[0]=[...initial.position];}
  this.navigationConfig={...super.eventLog().config,runtime:'CONTINUOUS_ARENA_NAVIGATION_V3',duration_s:30,body_model_role:"PINNED_SOURCE_PLANT_NOT_ACTIVE_RUN_SCHEDULE",initial_pose:structuredClone(this.pose),boundary_policy:{...NAVIGATION_POLICY},classification:NAVIGATION_MODE};
 }
 protected velocity():[number,number,number]{
  const [x,,z]=this.pose.position,[lx,lz]=this.limits,vx=.18*Math.sin(this.pose.heading),vz=.18*Math.cos(this.pose.heading);
  if(![x,z,vx,vz].every(Number.isFinite))throw new Error('Invalid navigation state');
  this.contact=((x>=lx&&vx>1e-12)||(x<=-lx&&vx< -1e-12))?'X_WALL':((z>=lz&&vz>1e-12)||(z<=-lz&&vz< -1e-12))?'Z_WALL':null;
  return this.contact?[0,0,0]:[vx,0,vz];
 }
 protected calculateBoundary(outgoing:boolean):NavigationFrame{
  const f=super.calculateBoundary(outgoing),b=boundarySteering(this.pose.position[0],this.pose.position[2],this.pose.heading,this.limits);
  const neural=f.angular_velocity;
  if(outgoing){this.neuralOmega=neural;this.boundaryOmega=b.omega;this.omega=neural+b.omega;this.neuralHeadingChange+=neural*BODY_DT;this.boundaryHeadingChange+=b.omega*BODY_DT;}
  return {...f,angular_velocity:outgoing?neural+b.omega:0,boundary_summary:{...b,omega:outgoing?b.omega:0,neural_omega:neural}};
 }
 finalBoundary():NavigationFrame{return super.finalBoundary() as NavigationFrame;}
 advance():NavigationFrame{
  const f=super.advance() as NavigationFrame;
  if(f.contact){this.contactSeconds+=BODY_DT;this.stallSeconds+=BODY_DT;this.maxStallSeconds=Math.max(this.maxStallSeconds,this.stallSeconds);}
  else this.stallSeconds=0;
  const now=Boolean(this.contact);
  if(now&&!this.contactActive)this.contacts++;
  if(!now&&this.contactActive)this.recoveries++;
  this.contactActive=now;return f;
 }
 snapshot():NavigationSnapshot{return {...super.snapshot(),neuralOmega:this.neuralOmega,boundaryOmega:this.boundaryOmega,proximity:Math.min(...boundarySteering(this.pose.position[0],this.pose.position[2],this.pose.heading,this.limits).distances),contacts:this.contacts,recoveries:this.recoveries,contactSeconds:this.contactSeconds,maxStallSeconds:this.maxStallSeconds,neuralHeadingChange:this.neuralHeadingChange,boundaryHeadingChange:this.boundaryHeadingChange};}
 // The v2 envelopes cannot describe this version's plant semantics.
 eventLog():never {throw new Error('Use versioned navigationLog');}
 async exportSession():Promise<never> {throw new Error('Use versioned exportNavigation');}
 navigationLog():NavigationLog{return {schema:'continuous_arena_navigation_event_log_v3',config:structuredClone(this.navigationConfig),events:super.eventLog().events,stop_step:this.n,pending_plane:this.pendingPlane(),termination:this.n===1500?'DURATION_COMPLETED':'PAUSED'};}
 async exportNavigation(){const log=this.navigationLog(),telemetry={completed_intervals:structuredClone(this.records),final_state:this.snapshot()},log_sha256=await hash(log),result_sha256=await hash(telemetry);return {schema:'continuous_arena_navigation_session_v3',log,telemetry,config_sha256:await hash(log.config),log_sha256,result_sha256,artifact_id:await hash({log_sha256,result_sha256})};}
}
function* navigationReplay(authority:NeuralArtifact,value:unknown){
 const log=value as NavigationLog;
 if(!log||log.schema!=='continuous_arena_navigation_event_log_v3'||Object.keys(log).sort().join(',')!=='config,events,pending_plane,schema,stop_step,termination'||!log.config||!Number.isInteger(log.stop_step)||log.stop_step<0||log.stop_step>1500||!Array.isArray(log.events)||log.events.length>1500)throw new Error('Invalid navigation log');
 const engine=new ContinuousNavigationEngine(authority,log.config.mode as RuntimeMode,log.config.initial_plane as Plane,log.config.initial_pose as Pose);
 if(stable(engine.navigationLog().config)!==stable(log.config)||log.termination!==(log.stop_step===1500?'DURATION_COMPLETED':'PAUSED')||![null,.4,-.4].includes(log.pending_plane)||(log.stop_step===1500&&log.pending_plane!==null))throw new Error('Navigation provenance mismatch');
 let prev=-1,plane=log.config.initial_plane;
 for(const e of log.events){if(Object.keys(e).sort().join(',')!=='new_plane,old_plane,step,time'||!Number.isInteger(e.step)||e.step<=prev||e.step>=log.stop_step||e.time!==e.step*BODY_DT||e.old_plane!==plane||![.4,-.4].includes(e.new_plane)||e.new_plane===plane)throw new Error('Navigation event mismatch');prev=e.step;plane=e.new_plane;}
 let i=0;while(engine.snapshot().step<log.stop_step){if(log.events[i]?.step===engine.snapshot().step)engine.requestPlane(log.events[i++].new_plane);engine.advance();yield;}if(log.pending_plane!==null)engine.requestPlane(log.pending_plane);return engine;
}
/** Same validated transitions, consumed synchronously by historical callers. */
export function replayNavigation(authority:NeuralArtifact,value:unknown){const steps=navigationReplay(authority,value);let next=steps.next();while(!next.done)next=steps.next();return next.value;}
/** Scheduling only: no numerical/state/contract change; yield every 50 intervals. */
export async function replayNavigationInChunks(authority:NeuralArtifact,value:unknown,yieldControl:()=>Promise<void>=()=>new Promise(resolve=>setTimeout(resolve,0))){
 const steps=navigationReplay(authority,value);let next=steps.next(),count=0;
 while(!next.done){if(++count%50===0)await yieldControl();next=steps.next();}return next.value;
}
export async function validateNavigation(authority:NeuralArtifact,value:unknown,cooperative=false){
 const v=value as Awaited<ReturnType<ContinuousNavigationEngine['exportNavigation']>>;
 if(!v||v.schema!=='continuous_arena_navigation_session_v3'||Object.keys(v).sort().join(',')!=='artifact_id,config_sha256,log,log_sha256,result_sha256,schema,telemetry'||await hash(v.log)!==v.log_sha256||await hash(v.telemetry)!==v.result_sha256||await hash(v.log.config)!==v.config_sha256||await hash({log_sha256:v.log_sha256,result_sha256:v.result_sha256})!==v.artifact_id)throw new Error('Navigation integrity mismatch');
 const expected=await (cooperative?await replayNavigationInChunks(authority,v.log):replayNavigation(authority,v.log)).exportNavigation();
 const eq=(a:unknown,b:unknown,key=''):boolean=>typeof b==='number'?typeof a==='number'&&Number.isFinite(a)&&(['step','time','substeps','contacts','recoveries','propulsion_model_value'].includes(key)?a===b:Math.abs(a-b)<=PARITY_TOLERANCE):Array.isArray(b)?Array.isArray(a)&&a.length===b.length&&b.every((x,i)=>eq(a[i],x)):b!==null&&typeof b==='object'?a!==null&&typeof a==='object'&&Object.keys(a).sort().join(',')===Object.keys(b).sort().join(',')&&Object.entries(b).every(([k,x])=>eq((a as Record<string,unknown>)[k],x,k)):a===b;
 if(!eq(v.telemetry,expected.telemetry))throw new Error('Navigation semantic mismatch');return v;
}

/** Shared finite canonical serialization for versioned navigation evidence. */
export const navigationHash=hash;
