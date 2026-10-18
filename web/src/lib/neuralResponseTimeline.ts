/** Presentation only. Samples are available at the RIGHT boundary of a completed interval. */
import {BODY_DT} from './interactiveNeuralLocomotion';
import type {MovingWorld,MotionEvent,relativeObservation} from './movingVisualStimuli';
import type {IndependentWorld,IndependentEvent} from './independentVisualStimuli';
import type {NavigationFrame,NavigationSnapshot} from './continuousArenaNavigation';
export type TimelineFrame=NavigationFrame&{stimulus_summary:MovingWorld|IndependentWorld};
export type TimelineSnapshot=NavigationSnapshot&{stimulus:MovingWorld|IndependentWorld;observation:Observation|null};
export type TimelineEvent=MotionEvent|IndependentEvent;
type Observation=ReturnType<typeof relativeObservation>;
export type TimelineSample={step:number;time:number;inputAvailable:number|null;self:number[]|null;external:number[]|null;combined:number[]|null;readout:number|null;neural:number|null;boundary:number|null;heading:number;contact:string|null};
export function timelineSamples(frames:readonly TimelineFrame[],end:TimelineSnapshot):TimelineSample[]{
 if(frames.length!==end.step||end.time!==end.step*BODY_DT)throw new Error('Incomplete timeline boundaries');
 return Array.from({length:end.step+1},(_,k)=>{
  const f=k?frames[k-1]:null,next=frames[k];
  if(f&&(f.step!==k-1||f.time!==(k-1)*BODY_DT||f.neural_summary?.substeps!==200))throw new Error('Invalid timeline interval');
  const o=f?.sensory_summary as Observation|null|undefined;
  if(o&&(o.available_step!==k-1||o.before_step!==k-2))throw new Error('Misaligned observation');
  const sample={step:k,time:k*BODY_DT,inputAvailable:o?o.available_step*BODY_DT:null,self:o?.self_motion_raw??null,external:o?.external_motion_raw??null,combined:o?[o.right,o.left]:null,readout:f?.neural_summary?.mean_yaw_drive_eq??null,neural:f?.boundary_summary.neural_omega??null,boundary:f?.boundary_summary.omega??null,heading:next?.orientation??end.heading,contact:next?.contact??(k===end.step?end.contact:null)};
  for(const v of [sample.self,sample.external,sample.combined])if(v&&(v.length!==2||!v.every(Number.isFinite)))throw new Error('Invalid timeline signal');
  for(const v of [sample.readout,sample.neural,sample.boundary,sample.heading])if(v!==null&&!Number.isFinite(v))throw new Error('Non-finite timeline signal');
  return sample;
 });
}
export function timelineStep(time:number,last:number){if(!Number.isFinite(time)||time<0||time>last*BODY_DT+1e-9)throw new Error('Timeline outside completed prefix');return Math.min(last,Math.floor(time/BODY_DT+1e-9));}
/** Body/neural STATES at boundary k; input and rate readouts from interval k-1 → k. No solver. */
export function timelineState<T extends TimelineSnapshot>(frames:readonly TimelineFrame[],end:T,k:number):T{
 if(!Number.isInteger(k)||k<0||k>end.step)throw new Error('Invalid timeline cursor');if(k===end.step)return end;
 const f=frames[k],prev=k?frames[k-1]:null;if(f&&('landmarks' in f.stimulus_summary)!==('landmarks' in end.stimulus))throw new Error('Timeline world version mismatch');if(!f)throw new Error('Missing timeline boundary');
 let contacts=0,recoveries=0,seconds=0,stall=0,maxStall=0,neuralChange=0,boundaryChange=0,was=false;for(let i=1;i<=k;i++){const now=Boolean(frames[i].contact);if(now&&!was)contacts++;if(!now&&was)recoveries++;was=now;if(frames[i-1].contact){seconds+=BODY_DT;stall+=BODY_DT;maxStall=Math.max(maxStall,stall);}else stall=0;neuralChange+=frames[i-1].boundary_summary.neural_omega*BODY_DT;boundaryChange+=frames[i-1].boundary_summary.omega*BODY_DT;}
 return {...end,step:k,time:k*BODY_DT,position:[...f.position],heading:f.orientation,hs:[...f.neural_summary!.hs_states],dn:[...f.neural_summary!.dnp15_states],readout:prev?.neural_summary?.mean_yaw_drive_eq??null,substeps:k*200,distance:f.distance,contact:f.contact,omega:prev?.angular_velocity??0,neuralOmega:prev?.boundary_summary.neural_omega??0,boundaryOmega:prev?.boundary_summary.omega??0,proximity:Math.min(...f.boundary_summary.distances),contacts,recoveries,contactSeconds:seconds,maxStallSeconds:maxStall,neuralHeadingChange:neuralChange,boundaryHeadingChange:boundaryChange,stimulus:f.stimulus_summary,observation:prev?.sensory_summary as Observation|null??null} as T;
}
export function timelineEvents(events:readonly TimelineEvent[],last:number){return events.filter(e=>e.step<=last).map(e=>({...e,markerKey:'sequence' in e?`${e.step}:${e.sequence}`:String(e.step),label:'stimulus_id' in e?`${e.time.toFixed(2)} s · ${e.stimulus_id} ${e.kind}: ${e.old_state.enabled?'ON':'OFF'}/${e.old_state.direction} → ${e.new_state.enabled?'ON':'OFF'}/${e.new_state.direction} · A=0.08, T=4 s; fase contínua`:`${e.time.toFixed(2)} s · movimento ${e.old_motion} → ${e.new_motion} · A=0.08, T=4 s; posição contínua`}));}

/** Drawing coordinates only (0.01 SVG pixel); source values/timestamps stay full precision.
 * Exact flat runs are coalesced without removing any extrema or crossing a gap. */
export function timelinePath(samples:readonly TimelineSample[],value:(s:TimelineSample)=>number|null,extent:number){
 let path='',previous:number|null=null,lastX='';
 for(const s of samples){const v=value(s);if(v===null){if(previous!==null)path+=`H${lastX}`;previous=null;continue;}const x=(50+820*s.time/30).toFixed(2),y=(44-30*v/extent).toFixed(2);if(previous===null)path+=`M${x},${y}`;else if(v!==previous)path+=`H${x}V${y}`;previous=v;lastX=x;}
 if(previous!==null)path+=`H${lastX}`;return path;
}
