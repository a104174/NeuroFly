import assert from "node:assert/strict";
import test from "node:test";
import {readFileSync} from "node:fs";
import {parseNeuralLocomotion} from "../src/lib/neuralLocomotion";
import {InteractiveNeuralEngine,FixedStepClock,replayEventLog,validateSession,PARITY_TOLERANCE,SOURCE_IDS,TARGET_IDS} from "../src/lib/interactiveNeuralLocomotion";
import type {LocomotionFrame} from "../src/lib/experimentalLocomotion";
const authority=parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json',import.meta.url),'utf8')));
const reference=JSON.parse(readFileSync(new URL('./fixtures/interactive-neural-reference-v2.json',import.meta.url),'utf8')).reference;
function parity(actual:unknown,expected:unknown,path='frame'){
 if(path.endsWith('pose_origin')){assert.equal(actual,'BROWSER_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY');return;}
 if(typeof expected==='number'){assert.equal(typeof actual,'number');assert.ok(Math.abs(Number(actual)-expected)<=PARITY_TOLERANCE,`${path}: ${actual} vs ${expected}`);}
 else if(Array.isArray(expected)){assert.equal((actual as unknown[]).length,expected.length);expected.forEach((v,i)=>parity((actual as unknown[])[i],v,`${path}[${i}]`));}
 else if(expected!==null&&typeof expected==='object'){for(const [k,v] of Object.entries(expected))if(k!=='visual_plane_z')parity((actual as Record<string,unknown>)[k],v,`${path}.${k}`);}
 else assert.equal(actual,expected,path);
}
function collect(engine:InteractiveNeuralEngine,switchStep?:number){const out:LocomotionFrame[]=[];while(engine.snapshot().step<400){if(engine.snapshot().step===switchStep)engine.requestPlane(-.4);out.push(engine.advance());}out.push(engine.finalBoundary());return out;}
for(const [index,mode,plane] of [[0,'baseline',.4],[1,'neural',.4],[2,'output_disabled',.4],[3,'neural',-.4]] as const){
 test(`Python parity: full 401 boundaries condition ${index}`,()=>{const e=new InteractiveNeuralEngine(authority,mode,plane);const frames=collect(e);frames.forEach((f,n)=>parity(f,authority.result.runs[index].frames[n],`condition${index}.boundary${n}`));assert.equal(e.snapshot().substeps,index===0?0:80000);});
}
test('Python mid-run switch parity, fixed event boundary and old-state continuity',()=>{
 const e=new InteractiveNeuralEngine(authority),frames=collect(e,100);
 for(const expected of reference.frames)parity(frames[expected.step],expected);
 assert.deepEqual(e.eventLog().events,reference.events);
 parity(frames[100].neural_summary!.hs_states,authority.result.runs[1].frames[100].neural_summary!.hs_states);
 parity(frames[100].neural_summary!.dnp15_states,authority.result.runs[1].frames[100].neural_summary!.dnp15_states);
 assert.notEqual(frames[100].sensory_summary!.right,authority.result.runs[1].frames[100].sensory_summary!.right);
 assert.notEqual(frames[100].neural_summary!.mean_yaw_drive_eq,authority.result.runs[1].frames[100].neural_summary!.mean_yaw_drive_eq);
 assert.ok(Math.abs(frames[200].orientation-authority.result.runs[1].frames[200].orientation)>.01);
});
test('identities, directed counts, model parameters and scientific configuration fail closed',()=>{
 assert.deepEqual(SOURCE_IDS,[10015,10016,10023,10034,10181,10419]);assert.deepEqual(TARGET_IDS,[11215,12069]);
 for(const change of [(a:typeof authority)=>{a.config.dataset_uuid='other';},(a:typeof authority)=>{a.config.sources.neural.source_identities.reverse();},(a:typeof authority)=>{a.config.policy.neural_substeps_per_interval=199;},(a:typeof authority)=>{a.config.body.speed=.2;},(a:typeof authority)=>{a.config.sources.yaw.orientation_model.normalization_horizon_ms=20;}]){const a=structuredClone(authority);change(a);assert.throws(()=>new InteractiveNeuralEngine(a));}
});
test('independent exact exponential old-state neural expectations on first driven interval',()=>{
 const e=new InteractiveNeuralEngine(authority);e.advance();const f=e.advance();
 const input=f.sensory_summary!.right;
 // 200 exact held input updates of tau=5ms, total interval=20ms.
 assert.ok(Math.abs(e.snapshot().hs[0]-input*(1-Math.exp(-20/5)))<1e-12);
 assert.equal(f.neural_summary!.hs_states[0],0);
 assert.notEqual(e.snapshot().dn[0],0);
});
test('visual changes never directly write pose/neural state; repeated UI requests coalesce',()=>{
 const e=new InteractiveNeuralEngine(authority);for(let i=0;i<100;i++)e.advance();const prior=e.snapshot();
 e.requestPlane(-.4);e.requestPlane(-.4);assert.deepEqual(e.snapshot(),prior);assert.equal(e.eventLog().events.length,0);
 e.advance();assert.equal(e.eventLog().events.length,1);assert.equal(e.eventLog().events[0].step,100);assert.equal(e.snapshot().substeps,20200);
});
test('FPS independent fixed scientific steps, pause/resume, reset and bounded catch-up',()=>{
 const a=new InteractiveNeuralEngine(authority),b=new InteractiveNeuralEngine(authority),ca=new FixedStepClock(),cb=new FixedStepClock();
 for(let i=0;i<100;i++)ca.advance(a,20,true);
 for(let i=0;i<50;i++){cb.advance(b,10,true);cb.advance(b,30,true);}
 assert.deepEqual(a.snapshot(),b.snapshot());const old=a.snapshot();ca.advance(a,5000,false);assert.deepEqual(a.snapshot(),old);ca.advance(a,20,true);assert.equal(a.snapshot().step,101);
 assert.equal(new InteractiveNeuralEngine(authority).snapshot().time,0);
 const result=cb.advance(b,5000,true);assert.equal(result.steps,5);assert.equal(result.limited,true);
 assert.throws(()=>ca.advance(a,NaN,true));
});
test('event replay reproduces full state exactly including pending paused intervention',()=>{
 const e=new InteractiveNeuralEngine(authority);for(let n=0;n<180;n++){if(n===100)e.requestPlane(-.4);e.advance();}e.requestPlane(.4);
 const r=replayEventLog(authority,e.eventLog());assert.deepEqual(r.snapshot(),e.snapshot());assert.deepEqual(r.eventLog(),e.eventLog());e.advance();r.advance();assert.deepEqual(r.snapshot(),e.snapshot());
});
test('invalid event timing, identities, gain, stimulus and initial state are rejected',()=>{
 const e=new InteractiveNeuralEngine(authority);collect(e,100);const log=e.eventLog();
 for(const change of [(l:typeof log)=>{l.config.gain=3;},(l:typeof log)=>{l.events[0].time=1.9;},(l:typeof log)=>{l.events[0].old_plane=-.4;},(l:typeof log)=>{l.events.push({...l.events[0]});},(l:typeof log)=>{l.config.initial_hs[0]=.1;},(l:typeof log)=>{l.stop_step=401;},(l:typeof log)=>{l.termination='PAUSED';}]){const x=structuredClone(log);change(x);assert.throws(()=>replayEventLog(authority,x));}
 assert.throws(()=>e.requestPlane(-.4));
});
test('session semantic replay rejects recalculated hashes accompanying false telemetry',async()=>{
 const e=new InteractiveNeuralEngine(authority);for(let i=0;i<4;i++)e.advance();const session=await e.exportSession();await validateSession(authority,session);
 const stable=(x:unknown):string=>Array.isArray(x)?`[${x.map(stable).join(',')}]`:x!==null&&typeof x==='object'?`{${Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,v])=>`${JSON.stringify(k)}:${stable(v)}`).join(',')}}`:JSON.stringify(x);
 const fake=structuredClone(session);fake.telemetry.final_state.heading+=.1;const bytes=new TextEncoder().encode(stable(fake.telemetry));fake.result_sha256=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');fake.artifact_id=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(stable({log_sha256:fake.log_sha256,result_sha256:fake.result_sha256})))),v=>v.toString(16).padStart(2,'0')).join('');await assert.rejects(validateSession(authority,fake),/semantic/);
});
test('contact latch and identical engineering propulsion survive neural intervention',()=>{
 const e=new InteractiveNeuralEngine(authority),frames=collect(e,100);for(const f of frames){assert.equal(f.propulsion_model_value,.18);assert.ok(Math.abs(f.position[0])<=.9654288893949121);assert.ok(Math.abs(f.position[2])<=.37542888939491215);if(f.contact)assert.deepEqual(f.linear_velocity,[0,0,0]);}
 const final=e.snapshot();assert.throws(()=>e.advance());assert.deepEqual(e.snapshot(),final);
});
test('final-boundary inspection is pure and completed-session replay stays exact',async()=>{
 const e=new InteractiveNeuralEngine(authority);while(e.snapshot().step<400)e.advance();const before=e.snapshot();e.finalBoundary();assert.deepEqual(e.snapshot(),before);await validateSession(authority,await e.exportSession());
});
test('reversed edges, altered structural counts and non-finite body state are rejected',()=>{
 for(const field of ['target_id','structural_count'] as const){const copy=structuredClone(authority);const n=copy.config.sources.neural as unknown as {selected_routes:{target_id:number;structural_count:number}[]};n.selected_routes[0][field]=999;assert.throws(()=>new InteractiveNeuralEngine(copy));}
 const invalid=structuredClone(authority);invalid.config.body.initial_position[0]=NaN;assert.throws(()=>new InteractiveNeuralEngine(invalid));
});
test('replay accepts numerical rounding within declared tolerance, never changed clocks',async()=>{
 const e=new InteractiveNeuralEngine(authority);e.advance();const v=await e.exportSession();
 const stable=(x:unknown):string=>Array.isArray(x)?`[${x.map(stable).join(',')}]`:x!==null&&typeof x==='object'?`{${Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,v])=>`${JSON.stringify(k)}:${stable(v)}`).join(',')}}`:JSON.stringify(x);
 const digest=async(x:unknown)=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(stable(x)))),n=>n.toString(16).padStart(2,'0')).join('');
 v.telemetry.final_state.heading+=1e-10;v.result_sha256=await digest(v.telemetry);v.artifact_id=await digest({log_sha256:v.log_sha256,result_sha256:v.result_sha256});await validateSession(authority,v);
 v.telemetry.final_state.time+=1e-10;v.result_sha256=await digest(v.telemetry);v.artifact_id=await digest({log_sha256:v.log_sha256,result_sha256:v.result_sha256});await assert.rejects(validateSession(authority,v),/semantic/);
});
