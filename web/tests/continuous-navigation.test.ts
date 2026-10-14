import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parseNeuralLocomotion} from '../src/lib/neuralLocomotion';
import {ContinuousNavigationEngine,boundarySteering,replayNavigation,validateNavigation} from '../src/lib/continuousArenaNavigation';
import {InteractiveNeuralEngine,FixedStepClock} from '../src/lib/interactiveNeuralLocomotion';
const authority=parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json',import.meta.url),'utf8')));
const fixture=JSON.parse(readFileSync(new URL('./fixtures/continuous-navigation-reference-v3.json',import.meta.url),'utf8'));
function equal(a:unknown,b:unknown,path=''){
 if(path.endsWith('pose_origin')){assert.equal(a,'BROWSER_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY');return;}
 if(typeof b==='number')assert.ok(typeof a==='number'&&Math.abs(a-b)<=1e-8,`${path}: ${a} vs ${b}`);
 else if(Array.isArray(b)){assert.equal((a as unknown[]).length,b.length);b.forEach((v,i)=>equal((a as unknown[])[i],v,path+`[${i}]`));}
 else if(b!==null&&typeof b==='object')for(const [k,v] of Object.entries(b)){if(k!=='visual_plane_z')equal((a as Record<string,unknown>)[k],v,path+'.'+k);}
 else assert.equal(a,b,path);
}
for(const name of ['B','C','D','corner','head_on'])test(`independent Python parity and actual recovery: ${name}`,()=>{
 const c=fixture.cases[name],e=new ContinuousNavigationEngine(authority,name==='C'?'output_disabled':'neural',.4,c.initial??undefined);
 const frames=[];while(e.snapshot().step<1500){if(name==='D'&&e.snapshot().step===100)e.requestPlane(-.4);frames.push(e.advance());}frames.push(e.finalBoundary());
 for(const expected of c.frames)equal(frames[expected.step],expected,`${name}.${expected.step}`);
 const end=e.snapshot();for(const [k,v] of Object.entries(c.statistics))equal(end[k as keyof typeof end],v,`stats.${k}`);
 assert.equal(end.substeps,300000);assert(end.recoveries>0);assert(end.distance>2);assert(end.maxStallSeconds<5);
 const contact=frames.findIndex(f=>Boolean(f.contact));assert(contact>=0);const released=frames.findIndex((f,i)=>i>contact&&!f.contact);assert(released>contact);assert(frames[Math.min(released+100,1500)].distance-frames[released].distance>.05);
 for(const f of frames){assert(Math.abs(f.position[0])<=.9654288893949121);assert(Math.abs(f.position[2])<=.37542888939491215);assert.equal(f.propulsion_model_value,.18);assert.equal(f.angular_velocity,f.boundary_summary.neural_omega+f.boundary_summary.omega);}
});
test('normal, corner, grazing and exact antipodal tie independent expectations',()=>{
 assert.equal(boundarySteering(0,0,0,[1,.4]).omega,0);
 assert.deepEqual(boundarySteering(1,.4,Math.PI/4,[1,.4]).inward,[-1,-1]);
 assert.equal(boundarySteering(1,0,Math.PI/2,[1,.4]).omega,1.2);
 assert.equal(boundarySteering(1,0,-Math.PI/2,[1,.4]).omega,0);
 assert.throws(()=>boundarySteering(NaN,0,0,[1,.4]));assert.throws(()=>boundarySteering(1.1,0,0,[1,.4]));assert.throws(()=>boundarySteering(0,0,0,[0,.4]));
});
test('v2 remains latched; v3 neural off removes only neural heading contribution',()=>{
 const old=new InteractiveNeuralEngine(authority),e=new ContinuousNavigationEngine(authority,'output_disabled');for(let n=0;n<400;n++)old.advance();for(let n=0;n<1500;n++)e.advance();assert(old.snapshot().contact);assert(old.snapshot().distance<2);assert.equal(e.snapshot().neuralHeadingChange,0);assert(e.snapshot().boundaryHeadingChange!==0);assert(e.snapshot().recoveries>0);
});
test('continuous state across live stimulus and fixed clock independent of FPS',()=>{
 const a=new ContinuousNavigationEngine(authority),b=new ContinuousNavigationEngine(authority),clock=new FixedStepClock();for(let n=0;n<100;n++){a.advance();clock.advance(b,20,true,30);}assert.deepEqual(a.snapshot(),b.snapshot());const before=a.snapshot();a.requestPlane(-.4);assert.deepEqual(a.snapshot(),before);const f=a.advance();assert.deepEqual(f.neural_summary!.hs_states,before.hs);assert.equal(a.snapshot().substeps,20200);const frozen=a.snapshot();clock.advance(a,9999,false,30);assert.deepEqual(a.snapshot(),frozen);assert.deepEqual(new ContinuousNavigationEngine(authority).snapshot().hs,[0,0,0,0,0,0]);
});
test('long event replay and semantic tampering rejection after rehash',async()=>{
 const e=new ContinuousNavigationEngine(authority);for(let n=0;n<1500;n++){if(n===100)e.requestPlane(-.4);e.advance();}
 assert.deepEqual(replayNavigation(authority,e.navigationLog()).snapshot(),e.snapshot());const data=await e.exportNavigation();await validateNavigation(authority,data);
 const fake=structuredClone(data);fake.telemetry.final_state.boundaryOmega+=.1;
 const stable=(x:unknown):string=>Array.isArray(x)?`[${x.map(stable).join(',')}]`:x!==null&&typeof x==='object'?`{${Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,v])=>`${JSON.stringify(k)}:${stable(v)}`).join(',')}}`:JSON.stringify(x);
 const digest=async(x:unknown)=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(stable(x)))),n=>n.toString(16).padStart(2,'0')).join('');
 fake.result_sha256=await digest(fake.telemetry);fake.artifact_id=await digest({log_sha256:fake.log_sha256,result_sha256:fake.result_sha256});await assert.rejects(validateNavigation(authority,fake),/semantic/);
 for(const k of ['gain','propulsion','boundary_policy']){const bad=structuredClone(data.log);bad.config[k]=999;assert.throws(()=>replayNavigation(authority,bad));}
 const bad=structuredClone(data.log);bad.events[0].time=1.9;assert.throws(()=>replayNavigation(authority,bad));
});
