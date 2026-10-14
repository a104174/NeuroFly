/** Paired counterfactuals reuse the actual v3 engine; no trajectory is imported. */
import {ContinuousNavigationEngine,validateNavigation,navigationHash,type NavigationFrame,type NavigationSnapshot} from './continuousArenaNavigation';
import {BODY_DT,PARITY_TOLERANCE,type Plane} from './interactiveNeuralLocomotion';
import type {NeuralArtifact} from './neuralLocomotion';
import {wrappedAngle} from './neuralSteeringComparison';
export type NavigationSession=Awaited<ReturnType<ContinuousNavigationEngine['exportNavigation']>>;
export type PairKey='ON'|'OFF';
export type ContactEvent={step:number;time:number;kind:'CONTACT'|'RECOVERY'|'WALL_CHANGE';wall:NavigationFrame['contact'];previous_wall?:NavigationFrame['contact']};
export type PairTrack={key:PairKey;NEURAL_TO_HEADING_ENABLED:boolean;frames:NavigationFrame[];contact_events:ContactEvent[];final_state:NavigationSnapshot};
class SamplingEngine extends ContinuousNavigationEngine {boundary(){return this.calculateBoundary(false);}}
export function contactEvents(frames:NavigationFrame[]):ContactEvent[]{
 const events:ContactEvent[]=[];let previous:NavigationFrame['contact']=null;
 for(const f of frames){if(f.contact!==previous){if(previous&&f.contact)events.push({step:f.step,time:f.time,kind:'WALL_CHANGE',wall:f.contact,previous_wall:previous});else if(previous)events.push({step:f.step,time:f.time,kind:'RECOVERY',wall:previous});else if(f.contact)events.push({step:f.step,time:f.time,kind:'CONTACT',wall:f.contact});previous=f.contact;}}
 return events;
}
export function pairedMetrics(a:NavigationFrame[],b:NavigationFrame[]){
 if(!a.length||a.length!==b.length)throw new Error('Unaligned pair');
 let separation={value:-1,time:0},heading={value:-1,time:0};
 for(let i=0;i<a.length;i++){
  if(a[i].time!==b[i].time||a[i].step!==b[i].step)throw new Error('Unaligned scientific timestamps');
  const distance=Math.hypot(a[i].position[0]-b[i].position[0],a[i].position[2]-b[i].position[2]),delta=a[i].orientation-b[i].orientation,angle=Math.abs(wrappedAngle(delta));
  if(distance>separation.value)separation={value:distance,time:a[i].time};
  if(angle>heading.value)heading={value:angle,time:a[i].time};
  // Piecewise-linear heading separation can cross an odd pi between boundaries.
  if(i){const previous=a[i-1].orientation-b[i-1].orientation,lo=Math.min(previous,delta),hi=Math.max(previous,delta),odd=Math.PI+2*Math.PI*Math.ceil((lo-Math.PI)/(2*Math.PI));
   if(odd>=lo&&odd<=hi&&delta!==previous&&heading.value<Math.PI)heading={value:Math.PI,time:a[i-1].time+(odd-previous)/(delta-previous)*BODY_DT};}
 }
 const last=a.length-1;
 return {max_separation:separation,max_wrapped_heading:heading,final_separation:Math.hypot(a[last].position[0]-b[last].position[0],a[last].position[2]-b[last].position[2]),final_wrapped_heading:wrappedAngle(a[last].orientation-b[last].orientation),traveled_difference:a[last].distance-b[last].distance};
}
export type PairResult={tracks:PairTrack[];metrics:ReturnType<typeof pairedMetrics>};
export type PairConfig={version:'NEURAL_CONTRIBUTION_COMPARISON_V3_1';parent_session_id:string;parent_config_sha256:string;parent_log_sha256:string;model_runtime:string;matched_config:Record<string,unknown>;event_log_sha256:string;conditions:{key:PairKey;NEURAL_TO_HEADING_ENABLED:boolean}[];duration_s:number;window:'RECORDED_PREFIX_ONLY';pending_policy:'NOT_APPLIED';sampling:'LEFT_BOUNDARY_OUTGOING_INTERVAL_ENDPOINT_NO_OUTGOING';random_policy:'NONE'};
export type PairArtifact={schema:'neural_contribution_comparison_v3_1';parent:NavigationSession;config:PairConfig;result:PairResult;config_sha256:string;result_sha256:string;artifact_id:string};
const yieldUI=()=>new Promise<void>(resolve=>setTimeout(resolve,0));
export async function generatePair(authority:NeuralArtifact,input:unknown,onProgress:(n:number)=>void=()=>{},yieldControl:()=>Promise<void>=yieldUI):Promise<PairArtifact>{
 await yieldControl();const parent=structuredClone(await validateNavigation(authority,input)),log=parent.log;
 if(log.stop_step<1)throw new Error('Run at least one interval before comparing');
 const matched=structuredClone(log.config);delete matched.mode;
 const conditions:PairConfig['conditions']=[{key:'ON',NEURAL_TO_HEADING_ENABLED:true},{key:'OFF',NEURAL_TO_HEADING_ENABLED:false}];
 const engines=conditions.map(c=>new SamplingEngine(authority,c.NEURAL_TO_HEADING_ENABLED?'neural':'output_disabled',log.config.initial_plane as Plane,log.config.initial_pose as {position:[number,number,number];heading:number}));
 for(const e of engines){const cfg=e.navigationLog().config;delete cfg.mode;if(await navigationHash(cfg)!==await navigationHash(matched))throw new Error('Unmatched counterfactual configuration');}
 const frames:NavigationFrame[][]=[[],[]];let event=0;
 for(let n=0;n<log.stop_step;n++){
  if(log.events[event]?.step===n){for(const e of engines)e.requestPlane(log.events[event].new_plane);event++;}
  engines.forEach((e,i)=>frames[i].push(e.advance()));
  if((n+1)%50===0){onProgress((n+1)/log.stop_step);await yieldControl();}
 }
 engines.forEach((e,i)=>frames[i].push(e.boundary()));
 const tracks=conditions.map((c,i)=>({...c,frames:frames[i],contact_events:contactEvents(frames[i]),final_state:engines[i].snapshot()}));
 const config:PairConfig={version:'NEURAL_CONTRIBUTION_COMPARISON_V3_1',parent_session_id:parent.artifact_id,parent_config_sha256:parent.config_sha256,parent_log_sha256:parent.log_sha256,model_runtime:String(log.config.runtime),matched_config:matched,event_log_sha256:await navigationHash(log.events),conditions,duration_s:log.stop_step*BODY_DT,window:'RECORDED_PREFIX_ONLY',pending_policy:'NOT_APPLIED',sampling:'LEFT_BOUNDARY_OUTGOING_INTERVAL_ENDPOINT_NO_OUTGOING',random_policy:'NONE'};
 const result={tracks,metrics:pairedMetrics(frames[0],frames[1])},config_sha256=await navigationHash(config),result_sha256=await navigationHash(result);
 onProgress(1);return {schema:'neural_contribution_comparison_v3_1',parent,config,result,config_sha256,result_sha256,artifact_id:await navigationHash({config_sha256,result_sha256})};
}
export async function validatePair(authority:NeuralArtifact,value:unknown){
 const v=value as PairArtifact;
 if(!v||v.schema!=='neural_contribution_comparison_v3_1'||Object.keys(v).sort().join(',')!=='artifact_id,config,config_sha256,parent,result,result_sha256,schema'||await navigationHash(v.config)!==v.config_sha256||await navigationHash(v.result)!==v.result_sha256||await navigationHash({config_sha256:v.config_sha256,result_sha256:v.result_sha256})!==v.artifact_id)throw new Error('Comparison integrity mismatch');
 const expected=await generatePair(authority,v.parent);
 if(await navigationHash(expected.config)!==v.config_sha256)throw new Error('Comparison matching/provenance mismatch');
 const eq=(a:unknown,b:unknown,key=''):boolean=>typeof b==='number'?typeof a==='number'&&Number.isFinite(a)&&(['step','time','substeps','contacts','recoveries','propulsion_model_value'].includes(key)?a===b:Math.abs(a-b)<=PARITY_TOLERANCE):Array.isArray(b)?Array.isArray(a)&&a.length===b.length&&b.every((x,i)=>eq(a[i],x)):b!==null&&typeof b==='object'?a!==null&&typeof a==='object'&&Object.keys(a).sort().join(',')===Object.keys(b).sort().join(',')&&Object.entries(b).every(([k,x])=>eq((a as Record<string,unknown>)[k],x,k)):a===b;
 // Maxima can occur between samples; their timestamp is a computed floating value.
 if(Object.keys(v.result.metrics).sort().join(',')!==Object.keys(expected.result.metrics).sort().join(',')||!eq({...v.result,metrics:undefined},{...expected.result,metrics:undefined})||!Object.entries(expected.result.metrics).every(([k,x])=>{
  const a=v.result.metrics[k as keyof typeof v.result.metrics];return typeof x==='number'?typeof a==='number'&&Math.abs(a-x)<=PARITY_TOLERANCE:typeof a==='object'&&a!==null&&Object.keys(a).sort().join(',')==='time,value'&&Math.abs(a.value-x.value)<=PARITY_TOLERANCE&&Math.abs(a.time-x.time)<=PARITY_TOLERANCE;
 }))throw new Error('Comparison semantic replay mismatch');
 return expected;
}
export function pairScene(track:PairTrack,time:number,assetOffset:[number,number,number]){
 const last=track.frames.at(-1)!;if(!Number.isFinite(time)||time<0||time>last.time)throw new Error('Invalid comparison cursor');
 const cursor=time/BODY_DT,nearest=Math.round(cursor),i=Math.min(last.step,Math.abs(cursor-nearest)<1e-9?nearest:Math.floor(cursor)),f=track.frames[i],next=track.frames[Math.min(i+1,last.step)],alpha=Math.max(0,Math.min(1,(time-f.time)/BODY_DT));
 const position=f.position.map((v,k)=>v+(next.position[k]-v)*alpha) as [number,number,number];
 const heading=f.orientation+wrappedAngle(next.orientation-f.orientation)*alpha;
 const neural=f.boundary_summary.neural_omega,boundary=f.boundary_summary.omega;
 const count=(kind:ContactEvent['kind'])=>track.contact_events.filter(e=>e.kind===kind&&e.time<=time).length;
 return {pose:{anchor:position,rotation:heading,assetOffset},frame:f,distance:f.distance+(next.distance-f.distance)*alpha,speed:Math.hypot(...f.linear_velocity),time,neural,boundary,readout:f.neural_summary?.mean_yaw_drive_eq??null,contacts:count('CONTACT'),recoveries:count('RECOVERY')};
}
export const PAIR_STYLE=[{key:'ON' as const,label:'Neural ON',color:'#67d3e0',symbol:'●'},{key:'OFF' as const,label:'Neural OFF',color:'#f3c777',symbol:'■'}];
export function pairOverview(pair:PairArtifact,landmarkX:number[]){return {tracks:PAIR_STYLE.map((s,i)=>({...s,plane:pair.parent.log.config.initial_plane as number,points:pair.result.tracks[i].frames.map(f=>f.position)})),landmarkX};}
export function activePairPlane(pair:PairArtifact,time:number){let plane=pair.parent.log.config.initial_plane as number;for(const e of pair.parent.log.events)if(e.time<=time)plane=e.new_plane;return plane;}
