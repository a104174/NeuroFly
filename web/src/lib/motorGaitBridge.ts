/** Open-loop experimental projection; no neural/body engine imports or writes. */
import {GAIT,type GaitState} from './articulatedGait';
export const MOTOR_REFERENCE_SHA256='90ddfadcf9d8ccb85590d74de4b66cecfff24a3ec9f9b6592729b74d34031d06';
export const PROJECTION={version:'engineering_swing_height_projection_v7',leg:'Leg.R.Front',reference_units:100,gain:.004,baseline:.012,min:.008,max:.016} as const;
export type BridgeCondition='BASE'|'ON'|'ROUTE_OFF'|'SHAM';
export type MotorReference={schema:string;source:{dataset_uuid:string;edge:{pre:number;post:number;synapse_count:number};neural_source_artifact_id:string};response_artifact_id:string;response_raw_sha256:string;model:{gain:number;initial_state:number;units:string};tau_s:number;timebase:{dt_s:number;duration_s:number;samples:number};samples:number[][]};
export async function parseMotorReference(raw:string):Promise<MotorReference>{
 const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw)))).map(v=>v.toString(16).padStart(2,'0')).join('');
 if(digest!==MOTOR_REFERENCE_SHA256)throw new Error('Motor source identity mismatch; no substitute signal.');
 const r=JSON.parse(raw) as MotorReference;
 if(r.schema!=='motor_gait_reference_v7'||r.source.dataset_uuid!=='4b2087c0fbe046bfaf0d60bc970e3e5d'||JSON.stringify(r.source.edge)!=='{"post":804257,"pre":903216,"synapse_count":23}'||r.response_artifact_id!=='deba097e484fa45675e2f5ab30add960bef141015af7344dc704d94444b9adad'||r.tau_s!==.01||r.model.gain!==1||r.model.initial_state!==0||r.timebase.dt_s!==.001||r.timebase.duration_s!==2||r.timebase.samples!==2001||r.samples.length!==2001)throw new Error('Contradictory motor source configuration.');
 for(let n=0;n<r.samples.length;n++){const row=r.samples[n];if(row.length!==2||!row.every(Number.isFinite)||row.some(v=>v<0))throw new Error('Invalid motor samples.');if(n===0&&row[1]!==0)throw new Error('Invalid initial motor state.');if(n){const [u,y]=r.samples[n-1],expected=y+-Math.expm1(-((n*.001)-(n-1)*.001)/.01)*(u-y);if(Math.abs(row[1]-expected)>1e-10)throw new Error('Motor response semantic mismatch.');}}
 return r;
}
export async function loadMotorReference(fetcher:typeof fetch=fetch){const r=await fetcher('/experiments/motor_gait_bridge_v7.json');if(!r.ok)throw new Error('Motor source unavailable; bridge disabled.');return parseMotorReference(await r.text());}
/** Linear visual reconstruction between 1 ms Python boundary states; no extrapolation. */
export function motorAt(reference:MotorReference,time:number,condition:BridgeCondition){
 if(!['BASE','ON','ROUTE_OFF','SHAM'].includes(condition)||!Number.isFinite(time)||time<0||time>2)throw new Error('Unsupported motor condition/time.');
 const i=Math.min(2000,Math.floor(time/.001)),a=reference.samples[i],b=reference.samples[Math.min(2000,i+1)],t=(time-i*.001)/.001;
 const source=a[0]+(b[0]-a[0])*t,receiver=condition==='ROUTE_OFF'?0:a[1]+(b[1]-a[1])*t;
 if(![source,receiver].every(Number.isFinite))throw new Error('Nonfinite motor signal.');
 const normalized=Math.max(-1,Math.min(1,receiver/PROJECTION.reference_units));
 const height=condition==='BASE'?PROJECTION.baseline:Math.max(PROJECTION.min,Math.min(PROJECTION.max,PROJECTION.baseline+PROJECTION.gain*normalized));
 return {time,source,receiver,normalized,height,delta:height-PROJECTION.baseline,condition};
}
/** Pure presentation overlay on one swing foot. The original state is never mutated. */
export function projectMotorGait(state:GaitState,reference:MotorReference,condition:BridgeCondition):GaitState{
 const signal=motorAt(reference,state.body.time,condition),index=GAIT.legs.findIndex(l=>l.id===PROJECTION.leg),f=state.feet[index];
 if(condition==='BASE'||signal.delta===0||!state.moving)return state;
 const envelope=Math.max(0,Math.min(1,(f.foot[1]-GAIT.animation.floor_y)/PROJECTION.baseline));
 const feet=state.feet.map((v,i)=>i===index?{...v,foot:[v.foot[0],v.foot[1]+signal.delta*envelope,v.foot[2]]}:v);
 return {...state,feet};
}
