/** Offline analysis only. No runtime imports, replay, neural or body integration. */
import { createHash } from 'node:crypto';
import type { PairArtifact } from '../src/lib/neuralContributionComparison';
export const ANALYSIS_TOLERANCE = 1e-8;
export function canonical(value: unknown): string {
  if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('Non-finite evidence');
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object') return `{${Object.entries(value).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,v])=>`${JSON.stringify(k)}:${canonical(v)}`).join(',')}}`;
  const s = JSON.stringify(value); if (s === undefined) throw new Error('Missing evidence'); return s;
}
export const evidenceHash = (x: unknown) => createHash('sha256').update(canonical(x)).digest('hex');
const requireEvidence = (ok: unknown, message: string) => { if (!ok) throw new Error(message); };
export function parseTemporalPair(text: string): PairArtifact {
  const p = JSON.parse(text) as PairArtifact;
  canonical(p); // recursively rejects every non-finite value
  requireEvidence(p?.schema === 'neural_contribution_comparison_v3_1' && p.config?.version === 'NEURAL_CONTRIBUTION_COMPARISON_V3_1', 'Unsupported pair schema');
  requireEvidence(evidenceHash(p.config) === p.config_sha256 && evidenceHash(p.result) === p.result_sha256 && evidenceHash({config_sha256:p.config_sha256,result_sha256:p.result_sha256}) === p.artifact_id, 'Pair integrity mismatch');
  const parent = p.parent, c = parent?.log?.config;
  requireEvidence(parent?.schema === 'continuous_arena_navigation_session_v3' && c?.runtime === 'CONTINUOUS_ARENA_NAVIGATION_V3' && c.mode === 'neural' && c.body_dt_s === .02 && c.gain === 2.5 && c.omega_bound === .5 && c.random_policy === 'NONE', 'Unsupported runtime provenance');
  requireEvidence(evidenceHash(parent.log) === parent.log_sha256 && evidenceHash(parent.telemetry) === parent.result_sha256 && evidenceHash(c) === parent.config_sha256 && evidenceHash({log_sha256:parent.log_sha256,result_sha256:parent.result_sha256}) === parent.artifact_id, 'Parent integrity mismatch');
  const matched = {...c}; delete matched.mode;
  requireEvidence(evidenceHash(matched) === evidenceHash(p.config.matched_config) && p.config.parent_session_id === parent.artifact_id && p.config.parent_config_sha256 === parent.config_sha256 && p.config.parent_log_sha256 === parent.log_sha256 && p.config.event_log_sha256 === evidenceHash(parent.log.events), 'Contradictory provenance');
  const n = parent.log.stop_step;
  requireEvidence(Number.isInteger(n) && n > 0 && n <= 1500 && p.config.duration_s === n*.02 && parent.log.termination === (n===1500?'DURATION_COMPLETED':'PAUSED') && p.result.tracks.length === 2, 'Incomplete horizon');
  requireEvidence(canonical(p.config.conditions) === canonical([{key:'ON',NEURAL_TO_HEADING_ENABLED:true},{key:'OFF',NEURAL_TO_HEADING_ENABLED:false}]), 'Contradictory conditions');
  p.result.tracks.forEach((t,k)=>{
    requireEvidence(t.key === (k===0?'ON':'OFF') && t.NEURAL_TO_HEADING_ENABLED === (k===0) && t.frames.length === n+1 && t.final_state.step === n && t.final_state.substeps === n*200, 'Incomplete or mismatched track');
    t.frames.forEach((f,i)=>{
      requireEvidence(f.step === i && f.time === i*.02 && f.position?.length === 3 && f.position.every(Number.isFinite) && Number.isFinite(f.orientation) && Number.isFinite(f.angular_velocity) && [null,'X_WALL','Z_WALL'].includes(f.contact), 'Invalid frame/alignment');
      const neural=f.neural_summary, wall=f.boundary_summary;
      requireEvidence(neural && neural.hs_states?.length===6 && neural.dnp15_states?.length===2 && neural.hs_states.every(Number.isFinite) && neural.dnp15_states.every(Number.isFinite) && wall && Number.isFinite(wall.omega) && Number.isFinite(wall.neural_omega), 'Missing neural/wall telemetry');
      if(i<n){
        requireEvidence(neural!.substeps===200 && Number.isFinite(neural!.orientation_increment_eq), 'Missing computed yaw');
        const computed=Math.max(-.5,Math.min(.5,2.5*neural!.orientation_increment_eq!/.02));
        requireEvidence(Math.abs(wall.neural_omega-(k===0?computed:0))<1e-12 && Math.abs(f.angular_velocity-wall.omega-wall.neural_omega)<1e-12 && Math.abs(t.frames[i+1].orientation-f.orientation-f.angular_velocity*.02)<1e-12,'Motor telemetry mismatch');
      } else requireEvidence(neural!.substeps===0 && neural!.orientation_increment_eq===null && f.angular_velocity===0 && wall.omega===0,'Invalid terminal record');
      requireEvidence(f.sensory_summary !== undefined, 'Missing observation field');
      if(f.sensory_summary) requireEvidence(Number.isFinite(f.sensory_summary.right) && Number.isFinite(f.sensory_summary.left) && f.sensory_summary.available_step===i && f.sensory_summary.before_step===i-1 && Math.abs(f.sensory_summary.interval_ms-20)<1e-8,'Invalid observation timing');
    });
    const initial=c.initial_pose as {position:number[];heading:number};
    requireEvidence(canonical(t.frames[0].position)===canonical(initial.position) && t.frames[0].orientation===initial.heading && canonical(t.frames.at(-1)!.position)===canonical(t.final_state.position) && t.frames.at(-1)!.orientation===t.final_state.heading,'Pose provenance mismatch');
  });
  requireEvidence(canonical(parent.telemetry.completed_intervals)===canonical(p.result.tracks[0].frames.slice(0,-1)), 'Parent/ON mismatch');
  return p;
}
function differences(a: unknown,b: unknown,path=''): {field:string;on:unknown;off:unknown;delta:number|null}[] {
  if(a===b) return [];
  if(typeof a==='number' && typeof b==='number') return [{field:path,on:a,off:b,delta:a-b}];
  if(a===null || b===null || typeof a!=='object' || typeof b!=='object') return [{field:path,on:a,off:b,delta:null}];
  const x=a as Record<string,unknown>,y=b as Record<string,unknown>;
  return [...new Set([...Object.keys(x),...Object.keys(y)])].sort().flatMap(k=>differences(x[k],y[k],path?`${path}.${k}`:k));
}
export function analyzeTemporalPair(text: string) {
  const p=parseTemporalPair(text),[a,b]=p.result.tracks.map(t=>t.frames),n=a.length-1;
  const wrap=(d:number)=>Math.atan2(Math.sin(d),Math.cos(d));
  const separation=(i:number)=>Math.hypot(a[i].position[0]-b[i].position[0],a[i].position[2]-b[i].position[2]);
  const yaw=(f:typeof a[number])=>Math.max(-.5,Math.min(.5,2.5*f.neural_summary!.orientation_increment_eq!/.02));
  const fields={applied:(i:number)=>[a[i].boundary_summary.neural_omega,b[i].boundary_summary.neural_omega],heading:(i:number)=>[wrap(a[i].orientation-b[i].orientation),0],position:(i:number)=>[separation(i),0],sensory:(i:number)=>[a[i].sensory_summary,b[i].sensory_summary],computed:(i:number)=>[yaw(a[i]),yaw(b[i])],neuralState:(i:number)=>[[a[i].neural_summary!.hs_states,a[i].neural_summary!.dnp15_states],[b[i].neural_summary!.hs_states,b[i].neural_summary!.dnp15_states]],wall:(i:number)=>[a[i].boundary_summary.omega,b[i].boundary_summary.omega],contact:(i:number)=>[a[i].contact,b[i].contact]};
  const sensoryAvailable=a.slice(1,n).every((f,i)=>f.sensory_summary!==null&&b[i+1].sensory_summary!==null);
  const events=Object.fromEntries(Object.entries(fields).map(([name,get])=>{
    const first=(tolerance:number)=>{for(let i=0;i<(name==='computed'||name==='applied'||name==='wall'||name==='sensory'?n:n+1);i++){const [x,y]=get(i);const d=differences(x,y).filter(v=>v.delta===null||Math.abs(v.delta)>tolerance);if(d.length)return {index:i,time_s:a[i].time,differences:d};}return null;};
    return [name,name==='sensory'&&!sensoryAvailable?{status:'UNAVAILABLE',exact:null,above_tolerance:null}:{status:'AVAILABLE',exact:first(0),above_tolerance:first(ANALYSIS_TOLERANCE)}];
  }));
  const evolution=a.map((f,i)=>({index:i,time_s:f.time,separation:separation(i),wrapped_heading:wrap(f.orientation-b[i].orientation)}));
  const maximum=evolution.reduce((best,x)=>x.separation>best.separation?x:best);
  const contacts=p.result.tracks.map(t=>{
    const intervals:{wall:string;start_s:number;end_s:number|null}[]=[];
    for(const f of t.frames){const last=intervals.at(-1);if(last?.end_s===null&&last.wall!==f.contact)last.end_s=f.time;if(f.contact&&(!last||last.end_s!==null))intervals.push({wall:f.contact,start_s:f.time,end_s:null});}
    return {condition:t.key,intervals};
  });
  return {schema:'neurofly_temporal_divergence_v1',pair_id:p.artifact_id,config_sha256:p.parent.config_sha256,tolerance:ANALYSIS_TOLERANCE,validation:'HASH_STRUCTURE_AND_RECORDED_ALGEBRA_ONLY_NO_SOLVER_REPLAY',events,maximum,final:evolution.at(-1)!,checkpoints:evolution.filter(x=>x.index===0||x.time_s%5===0||x.index===n),contacts,evolution};
}
