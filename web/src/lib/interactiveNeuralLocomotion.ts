/** Fixed-step browser implementation of the pinned Python v1 model.
 * No recorded pose or neural trajectory is read by this engine. */
import { locomotionBounds, type LocomotionFrame } from "./experimentalLocomotion";
import { NEURAL_LOCOMOTION_SHA256, NEURAL_LOCOMOTION_URL, type NeuralArtifact } from "./neuralLocomotion";
export const RUNTIME_VERSION = "INTERACTIVE_NEURAL_LOCOMOTION_V2";
export const SOURCE_IDS = [10015,10016,10023,10034,10181,10419] as const;
export const TARGET_IDS = [11215,12069] as const;
export const BODY_DT = .02, NEURAL_DT_MS = .1, SUBSTEPS = 200;
export const PARITY_TOLERANCE = 1e-8; // Absolute proxy/model-space units over eight seconds.
export type RuntimeMode = "neural" | "baseline" | "output_disabled";
export type Plane = .4 | -.4;
type Vec3 = [number,number,number];
type Pose = {position:Vec3; heading:number};
type NeuralContract = Omit<NeuralArtifact["config"]["sources"]["neural"],"source_identities"> & {
 source_identities:{body_id:number;side:string}[];
 source_model:{tau_ms:number};target_model:{tau_ms:number};transfer:{coefficient:number};
 selected_routes:{source_id:number;target_id:number;structural_count:number}[];
};
export type StimulusEvent = {step:number;time:number;old_plane:Plane;new_plane:Plane};
export type RuntimeSnapshot = {step:number;time:number;position:Vec3;heading:number;hs:number[];dn:number[];plane:Plane;contact:LocomotionFrame["contact"];distance:number;omega:number;readout:number|null;substeps:number};
export type EventLog = {
 schema:"interactive_neural_locomotion_event_log_v2";
 config:{source_url:string;body_model:NeuralArtifact["config"]["body"];runtime:string;source_artifact_id:string;source_raw_sha256:string;source_config_sha256:string;dataset_uuid:string;model_sources:Record<string,string>;mode:RuntimeMode;initial_plane:Plane;body_dt_s:number;neural_dt_ms:number;substeps:number;duration_s:number;propulsion:number;gain:number;omega_bound:number;random_policy:"NONE";initial_pose:Pose;initial_hs:number[];initial_dn:number[]};
 events:StimulusEvent[];stop_step:number;pending_plane:Plane|null;termination:"PAUSED"|"DURATION_COMPLETED";
};
const finite=(x:number)=>{if(!Number.isFinite(x))throw new Error("Non-finite simulation state");return x;};
const clip=(x:number,a:number,b:number)=>Math.max(a,Math.min(b,x));
const validPlane=(x:unknown):x is Plane=>x===.4||x===-.4;
function stableJSON(value:unknown):string {
 if(typeof value==="number")finite(value);
 if(Array.isArray(value))return `[${value.map(stableJSON).join(",")}]`;
 if(value!==null&&typeof value==="object")return `{${Object.entries(value).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,v])=>`${JSON.stringify(k)}:${stableJSON(v)}`).join(",")}}`;
 const result=JSON.stringify(value);if(result===undefined)throw new Error("Unsupported serialization");return result;
}
async function hash(value:unknown){const raw=new TextEncoder().encode(stableJSON(value));return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",raw)),v=>v.toString(16).padStart(2,"0")).join("");}

export class InteractiveNeuralEngine {
 protected readonly body:NeuralArtifact["config"]["body"];
 protected readonly limits:readonly number[];
 private readonly config:EventLog["config"];
 protected pose:Pose;
 protected previous:Pose|null=null;
 private hs:number[]=Array(6).fill(0);
 private dn:number[]=Array(2).fill(0);
 protected n=0;
 private plane:Plane;
 private pending:Plane|null=null;
 protected contact:LocomotionFrame["contact"]=null;
 protected distance=0;
 private readout:number|null=null;
 protected omega=0;
 private executedSubsteps=0;
 private readonly events:StimulusEvent[]=[];
 protected readonly records:LocomotionFrame[]=[];
 protected readonly path:Vec3[]=[];
 constructor(authority:NeuralArtifact,mode:RuntimeMode="neural",initialPlane:Plane=.4) {
  if(!["neural","baseline","output_disabled"].includes(mode)||!validPlane(initialPlane))throw new Error("Unsupported runtime configuration");
  const c=authority.config, n=c.sources.neural as NeuralContract;
  if(authority.artifact_id!=="4d7c791224f21ecf677df81d2127a6f8b753974694b6b324afc1948da3fb9064"||authority.config_sha256!=="a916769c730174b3d631ccda9df0dd89479cd1b12f43be250b856c1782736e2d"||c.dataset_uuid!=="4b2087c0fbe046bfaf0d60bc970e3e5d"||n.dt_ms!==NEURAL_DT_MS||n.source_model.tau_ms!==5||n.target_model.tau_ms!==10||n.transfer.coefficient!==1||c.sources.yaw.orientation_model.normalization_horizon_ms!==50)throw new Error("Runtime source authority mismatch");
  if(stableJSON(n.source_identities.map(x=>x.body_id))!==stableJSON(SOURCE_IDS)||stableJSON(n.target_identities.map(x=>x.body_id))!==stableJSON(TARGET_IDS))throw new Error("Runtime identity ordering mismatch");
  if(stableJSON(n.source_identities.map(x=>x.side))!=='["R","R","R","L","L","L"]'||stableJSON(c.source_sha256)!==stableJSON({neural:"371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074",observation:"49e91a10fa49c5d7004f28249b63f334a0e23767c20108f5578a0e2586c9767a",yaw:"1be0f6364070a5a5536f4c772bd47abb3be2f08357b439a51e03f034f8b2a654"}))throw new Error("Runtime source pins/side mismatch");
  const expected=SOURCE_IDS.map((id,i)=>[id,TARGET_IDS[i<3?0:1],[138,122,23,78,126,14][i]]);
  if(stableJSON(n.selected_routes.map(r=>[r.source_id,r.target_id,r.structural_count]))!==stableJSON(expected))throw new Error("Runtime directed route authority mismatch");
  if(c.policy.neural_dt_ms!==.1||c.policy.duration_s!==8||c.policy.random_policy!=="NONE"||c.policy.neural_substeps_per_interval!==SUBSTEPS||c.policy.body_dt_ms!==20||c.policy.steering_gain_rad_per_orientation_eq!==2.5||c.policy.max_abs_angular_velocity_rad_s!==.5||stableJSON(c.policy.landmark_x)!=="[0.6,-0.6]")throw new Error("Runtime multirate policy mismatch");
  this.body=structuredClone(c.body);this.limits=locomotionBounds(this.body);
  this.pose={position:[...this.body.initial_position],heading:this.body.initial_heading_rad};this.plane=initialPlane;
  this.config={source_url:NEURAL_LOCOMOTION_URL,body_model:structuredClone(this.body),runtime:RUNTIME_VERSION,source_artifact_id:authority.artifact_id,source_raw_sha256:NEURAL_LOCOMOTION_SHA256,source_config_sha256:authority.config_sha256,dataset_uuid:c.dataset_uuid,model_sources:{...c.source_sha256},mode,initial_plane:initialPlane,body_dt_s:BODY_DT,neural_dt_ms:NEURAL_DT_MS,substeps:SUBSTEPS,duration_s:8,propulsion:.18,gain:2.5,omega_bound:.5,random_policy:"NONE",initial_pose:structuredClone(this.pose),initial_hs:[...this.hs],initial_dn:[...this.dn]};
  this.path.push([...this.pose.position]);
 }
 protected lastStep=400;
 snapshot():RuntimeSnapshot {return {step:this.n,time:this.n*BODY_DT,position:[...this.pose.position],heading:this.pose.heading,hs:[...this.hs],dn:[...this.dn],plane:this.plane,contact:this.contact,distance:this.distance,omega:this.omega,readout:this.readout,substeps:this.executedSubsteps};}
 trajectory():Vec3[]{return this.path.map(p=>[...p]);}
 eventLog():EventLog {return structuredClone({schema:"interactive_neural_locomotion_event_log_v2",config:this.config,events:this.events,stop_step:this.n,pending_plane:this.pending,termination:this.n===this.lastStep?"DURATION_COMPLETED":"PAUSED"});}
 requestPlane(plane:Plane){if(!validPlane(plane)||this.n===this.lastStep)throw new Error("Invalid/finished stimulus intervention");this.pending=plane===this.plane?null:plane;}
 pendingPlane(){return this.pending;}
 protected observation():LocomotionFrame["sensory_summary"] {
  if(!this.previous)return null;
  const before=this.previous, after=this.pose, dx=after.position[0]-before.position[0],dz=after.position[2]-before.position[2];
  const dh=after.heading/(2*Math.PI)-before.heading/(2*Math.PI);
  const interval=this.n*BODY_DT*1000-(this.n-1)*BODY_DT*1000;
  if(Math.abs(dh)>=.5)throw new Error("Ambiguous heading interval");
  const raw:number[]=[],shifts:number[]=[],bounded:number[]=[],clipped:boolean[]=[];
  for(const [i,x] of [.6,-.6].entries()){
   const bx=x-before.position[0],bz=this.plane-before.position[2],ax=x-after.position[0],az=this.plane-after.position[2];
   const squared=dx*dx+dz*dz,fraction=squared?clip((bx*dx+bz*dz)/squared,0,1):0;
   if(Math.hypot(bx-fraction*dx,bz-fraction*dz)<=1e-9)throw new Error("Singular visual geometry");
   const shift=Math.atan2(bz*ax-bx*az,bx*ax+bz*az),relative=shift/(2*Math.PI)-dh;
   if(Math.abs(shift)>=Math.PI||Math.abs(relative)>=.5)throw new Error("Ambiguous bearing interval");
   const value=finite(50*(relative/interval)*(i===0?1:-1));raw.push(value);shifts.push(shift);bounded.push(clip(value,-1,1));clipped.push(value!==bounded[i]);
  }
  return {before_step:this.n-1,available_step:this.n,interval_ms:interval,right:bounded[0],left:bounded[1],raw_normalized:raw,bearing_shift_rad:shifts,clipped,heading_increment_eq:dh,pose_origin:"BROWSER_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY"};
 }
 /** Returns the left-boundary telemetry whose outgoing interval was computed.
  * snapshot() is the NEW right-boundary state, never a predicted prerecorded pose. */
 advance():LocomotionFrame {
  if(this.n>=this.lastStep)throw new Error("Simulation completed");
  if(this.pending!==null){this.events.push({step:this.n,time:this.n*BODY_DT,old_plane:this.plane,new_plane:this.pending});this.plane=this.pending;this.pending=null;}
  const f=this.calculateBoundary(true);
  this.records.push(f);this.previous=structuredClone(this.pose);
  const next:Vec3=[clip(this.pose.position[0]+f.linear_velocity[0]*BODY_DT,-this.limits[0],this.limits[0]),this.pose.position[1],clip(this.pose.position[2]+f.linear_velocity[2]*BODY_DT,-this.limits[1],this.limits[1])];
  this.distance+=Math.hypot(next[0]-this.pose.position[0],next[2]-this.pose.position[2]);
  this.pose={position:next,heading:finite(this.pose.heading+f.angular_velocity*BODY_DT)};this.n++;this.path.push([...next]);
  // Resolve the new boundary without advancing neural time.
  this.velocity();return structuredClone(f);
 }
 protected velocity():Vec3 {
  const [x,,z]=this.pose.position,[lx,lz]=this.limits;
  const vx=.18*Math.sin(finite(this.pose.heading)),vz=.18*Math.cos(this.pose.heading);
  if(!this.pose.position.every(Number.isFinite))throw new Error("Invalid pose");
  if(!this.contact){if((x>=lx&&vx>0)||(x<=-lx&&vx<0))this.contact="X_WALL";else if((z>=lz&&vz>0)||(z<=-lz&&vz<0))this.contact="Z_WALL";}
  return this.contact?[0,0,0]:[vx,0,vz];
 }
 protected calculateBoundary(outgoing:boolean):LocomotionFrame {
  const sensory=this.observation(),velocity=this.velocity(),oldHS=[...this.hs],oldDN=[...this.dn];
  let increment=0,driveSum=0,omega=0,clipped=false;
  const neural=this.config.mode!=="baseline";
  if(outgoing&&neural){
   const sourceDecay=Math.exp(-.1/5),targetDecay=Math.exp(-.1/10);
   for(let i=0;i<SUBSTEPS;i++){
    const drives=[this.hs[0]/3+this.hs[1]/3+this.hs[2]/3,this.hs[3]/3+this.hs[4]/3+this.hs[5]/3];
    const drive=this.dn[0]-this.dn[1];increment+=(.1/50)*drive;driveSum+=drive;
    this.hs=this.hs.map((s,index)=>{const u=(index<3?sensory?.right:sensory?.left)??0;return u+(s-u)*sourceDecay;});
    this.dn=this.dn.map((s,index)=>drives[index]+(s-drives[index])*targetDecay);
   }
   if([...this.hs,...this.dn].some(v=>!Number.isFinite(v)||Math.abs(v)>1))throw new Error("Invalid neural solution");
   const raw=2.5*increment/BODY_DT,bounded=clip(raw,-.5,.5);clipped=raw!==bounded;omega=this.config.mode==="neural"?bounded:0;
   this.executedSubsteps+=SUBSTEPS;this.readout=driveSum/SUBSTEPS;
  }
  if(outgoing)this.omega=omega;
  return {step:this.n,time:this.n*BODY_DT,position:[...this.pose.position],orientation:this.pose.heading,linear_velocity:velocity,angular_velocity:omega,contact:this.contact,propulsion_model_value:.18,steering_model_value:omega,sensory_summary:sensory,neural_summary:neural?{hs_states:oldHS,dnp15_states:oldDN,substeps:outgoing?SUBSTEPS:0,orientation_increment_eq:outgoing?increment:null,mean_yaw_drive_eq:outgoing?driveSum/SUBSTEPS:null}:null,model_mode:this.config.mode==="neural"?"CONNECTOME_INFORMED_NEURAL_STEERING":"EXPERIMENTAL_KINEMATIC_ONLY",steering_applied:this.config.mode==="neural",steering_clipped:clipped,distance:this.distance};
 }
 finalBoundary(){if(this.n!==this.lastStep)throw new Error("Not final boundary");return this.calculateBoundary(false);}
 async exportSession(){const log=this.eventLog(),telemetry={completed_intervals:structuredClone(this.records),final_state:this.snapshot()},log_sha256=await hash(log),result_sha256=await hash(telemetry);return {schema:"interactive_neural_locomotion_session_v2",log,telemetry,config_sha256:await hash(log.config),log_sha256,result_sha256,artifact_id:await hash({log_sha256,result_sha256})};}
}

export function replayEventLog(authority:NeuralArtifact,value:unknown):InteractiveNeuralEngine {
 const log=value as EventLog;
 if(!log||Object.keys(log).sort().join(",")!=="config,events,pending_plane,schema,stop_step,termination"||log.schema!=="interactive_neural_locomotion_event_log_v2"||!log.config||!Array.isArray(log.events)||!Number.isInteger(log.stop_step)||log.stop_step<0||log.stop_step>400||log.events.length>400)throw new Error("Invalid interactive event log");
 const engine=new InteractiveNeuralEngine(authority,log.config.mode,log.config.initial_plane);
 const expected=engine.eventLog().config;
 if(stableJSON(log.config)!==stableJSON(expected)||log.termination!==(log.stop_step===400?"DURATION_COMPLETED":"PAUSED")||(log.pending_plane!==null&&!validPlane(log.pending_plane))||(log.stop_step===400&&log.pending_plane!==null))throw new Error("Contradictory interactive provenance");
 let prior=-1,plane=log.config.initial_plane;
 for(const e of log.events){if(Object.keys(e).sort().join(',')!=="new_plane,old_plane,step,time"||!Number.isInteger(e.step)||e.step<=prior||e.step>=log.stop_step||e.time!==e.step*BODY_DT||e.old_plane!==plane||!validPlane(e.new_plane)||e.new_plane===plane)throw new Error("Invalid event timing/continuity");prior=e.step;plane=e.new_plane;}
 let i=0;
 while(engine.snapshot().step<log.stop_step){if(log.events[i]?.step===engine.snapshot().step)engine.requestPlane(log.events[i++].new_plane);engine.advance();}
 if(log.pending_plane!==null)engine.requestPlane(log.pending_plane);
 return engine;
}
export async function validateSession(authority:NeuralArtifact,value:unknown) {
 const v=value as Awaited<ReturnType<InteractiveNeuralEngine["exportSession"]>>;
 if(v.schema!=="interactive_neural_locomotion_session_v2"||await hash(v.log)!==v.log_sha256||await hash(v.telemetry)!==v.result_sha256)throw new Error("Session integrity mismatch");
 const reproduced=await replayEventLog(authority,v.log).exportSession();
 if(Object.keys(v).sort().join(",")!=="artifact_id,config_sha256,log,log_sha256,result_sha256,schema,telemetry"||stableJSON(reproduced.log)!==stableJSON(v.log)||await hash(v.log.config)!==v.config_sha256||await hash({log_sha256:v.log_sha256,result_sha256:v.result_sha256})!==v.artifact_id)throw new Error("Session semantic provenance mismatch");
 // Cross-engine libm rounding may differ; input metadata/counters are exact,
 // computed floating state quantities use the same declared parity tolerance.
 const equivalent=(actual:unknown,expected:unknown,key=""):boolean=>{
  if(typeof expected==="number")return typeof actual==="number"&&Number.isFinite(actual)&&(["step","time","substeps","propulsion_model_value"].includes(key)?actual===expected:Math.abs(actual-expected)<=PARITY_TOLERANCE);
  if(Array.isArray(expected))return Array.isArray(actual)&&actual.length===expected.length&&expected.every((x,i)=>equivalent(actual[i],x));
  if(expected!==null&&typeof expected==="object")return actual!==null&&typeof actual==="object"&&Object.keys(actual).sort().join(",")===Object.keys(expected).sort().join(",")&&Object.entries(expected).every(([k,x])=>equivalent((actual as Record<string,unknown>)[k],x,k));
  return actual===expected;
 };
 if(!equivalent(v.telemetry,reproduced.telemetry))throw new Error("Session semantic replay mismatch");
 return v;
}
/** Bounded fixed-step scheduler. Excess elapsed wall time is discarded explicitly;
 * scientific dt is never enlarged. Pause discards wall-time debt, not model state. */
export class FixedStepClock {
 private accumulator=0;
 advance(engine:Pick<InteractiveNeuralEngine,"snapshot"|"advance">,elapsedMs:number,playing:boolean,durationS=8) {
  if(!Number.isFinite(elapsedMs)||elapsedMs<0||!Number.isFinite(durationS)||durationS<=0)throw new Error("Invalid wall-clock interval");
  if(!playing){this.accumulator=0;return {steps:0,limited:false};}
  this.accumulator+=elapsedMs;let steps=0;
  while(this.accumulator>=20&&steps<5&&engine.snapshot().time<durationS){engine.advance();this.accumulator-=20;steps++;}
  const limited=this.accumulator>=20;if(limited)this.accumulator=0;
  return {steps,limited};
 }
 reset(){this.accumulator=0;}
}
