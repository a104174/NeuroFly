import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parseNeuralLocomotion} from '../src/lib/neuralLocomotion';
import {ContinuousNavigationEngine,navigationHash} from '../src/lib/continuousArenaNavigation';
import {generatePair,validatePair,pairScene,pairedMetrics,activePairPlane,contactEvents,type PairArtifact} from '../src/lib/neuralContributionComparison';
const authority=parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json',import.meta.url),'utf8')));
const refs=JSON.parse(readFileSync(new URL('./fixtures/neural-contribution-reference-v3-1.json',import.meta.url),'utf8'));
const fast=async()=>{};
async function parent(switchAt?:number,stop=1500,mode:'neural'|'output_disabled'='neural'){
 const e=new ContinuousNavigationEngine(authority,mode);for(let n=0;n<stop;n++){if(n===switchAt)e.requestPlane(-.4);e.advance();}return e.exportNavigation();
}
function eq(a:unknown,b:unknown,p=''){
 if(p.endsWith('pose_origin')){assert.equal(a,'BROWSER_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY');return;}
 if(typeof b==='number')assert(typeof a==='number'&&Math.abs(a-b)<=1e-8,`${p} ${a} vs ${b}`);
 else if(Array.isArray(b)){assert.equal((a as unknown[]).length,b.length);b.forEach((v,i)=>eq((a as unknown[])[i],v,p+`[${i}]`));}
 else if(b!==null&&typeof b==='object'){for(const[k,v]of Object.entries(b))if(k!=='visual_plane_z')eq((a as Record<string,unknown>)[k],v,p+'.'+k);}
 else assert.equal(a,b,p);
}
for(const name of ['none','switch'])test(`real Python paired numerical reference: ${name}`,async()=>{
 const source=await parent(name==='switch'?100:undefined),pair=await generatePair(authority,source,()=>{},fast);assert.equal(pair.config.parent_session_id,source.artifact_id);assert.equal(pair.result.tracks.length,2);
 refs.cases[name].tracks.forEach((expected:{frames:unknown[];contact_events:unknown[]},i:number)=>{for(const f of expected.frames as {step:number}[])eq(pair.result.tracks[i].frames[f.step],f,`${name}.${i}.${f.step}`);eq(pair.result.tracks[i].contact_events,expected.contact_events);});eq(pair.result.metrics,refs.cases[name].metrics);
 assert.deepEqual(pair.result.tracks[0].frames[0].position,pair.result.tracks[1].frames[0].position);
 for(const t of pair.result.tracks){assert.equal(t.final_state.substeps,300000);assert(t.final_state.recoveries>0);assert(t.frames.every(f=>f.propulsion_model_value===.18));}
 assert.notDeepEqual(pair.result.tracks[0].contact_events,pair.result.tracks[1].contact_events);
 assert(pair.result.tracks[1].frames.every(f=>f.boundary_summary.neural_omega===0));assert(pair.result.tracks[1].frames.some(f=>Math.abs(f.neural_summary!.mean_yaw_drive_eq??0)>1e-5));
});
test('only output application differs; source preserved and divergence begins causally',async()=>{
 const source=await parent(undefined,400,'output_disabled'),before=structuredClone(source);const pair=await generatePair(authority,source,()=>{},fast);assert.deepEqual(source,before);const [a,b]=pair.result.tracks;
 assert.deepEqual(a.frames[1].sensory_summary,b.frames[1].sensory_summary);assert.deepEqual(a.frames[1].neural_summary,b.frames[1].neural_summary);assert.equal(a.frames[1].boundary_summary.omega,0);assert.equal(b.frames[1].boundary_summary.omega,0);assert.equal(a.frames[1].angular_velocity-b.frames[1].angular_velocity,a.frames[1].boundary_summary.neural_omega);assert.notDeepEqual(a.frames[3].position,b.frames[3].position);assert.notDeepEqual(a.frames[200].sensory_summary,b.frames[200].sensory_summary);assert.notEqual(a.frames[200].neural_summary!.mean_yaw_drive_eq,b.frames[200].neural_summary!.mean_yaw_drive_eq);
 assert.deepEqual(pair.config.matched_config.initial_hs,[0,0,0,0,0,0]);assert.equal(pair.config.window,'RECORDED_PREFIX_ONLY');assert.equal(pair.result.tracks[0].frames.length,401);
});
test('multiple external switches match both worlds without resetting neural state',async()=>{
 const e=new ContinuousNavigationEngine(authority);for(let n=0;n<800;n++){if(n===100)e.requestPlane(-.4);if(n===600)e.requestPlane(.4);e.advance();}e.requestPlane(-.4);const source=await e.exportNavigation(),pair=await generatePair(authority,source,()=>{},fast);
 assert.deepEqual(pair.parent.log.events,source.log.events);assert.equal(activePairPlane(pair,1.99),.4);assert.equal(activePairPlane(pair,2),-.4);assert.equal(activePairPlane(pair,12),.4);assert.equal(activePairPlane(pair,16),.4);assert.equal(pair.parent.log.pending_plane,-.4);
 for(const t of pair.result.tracks){assert.equal(t.final_state.substeps,160000);assert.equal(t.frames[100].neural_summary!.substeps,200);assert.notDeepEqual(t.frames[100].neural_summary!.hs_states,[0,0,0,0,0,0]);}
});
test('independent interpolation, wrapped angles and between-boundary maxima',async()=>{
 const pair=await generatePair(authority,await parent(undefined,10),()=>{},fast),a=pair.result.tracks[0];const f=pairScene(a,.03,authority.config.body.asset_offset);assert.equal(f.time,.03);eq(f.pose.anchor,a.frames[1].position.map((x,i)=>(x+a.frames[2].position[i])/2));assert.equal(pairScene(a,.2,authority.config.body.asset_offset).readout,null);assert.throws(()=>pairScene(a,.201,authority.config.body.asset_offset));
 const x=structuredClone(a.frames.slice(0,2)),y=structuredClone(x);x[0].orientation=Math.PI-.1;x[1].orientation=Math.PI+.1;y.forEach(f=>f.orientation=0);const m=pairedMetrics(x,y);assert.equal(m.max_wrapped_heading.value,Math.PI);assert(Math.abs(m.max_wrapped_heading.time-.01)<1e-12);assert(Math.abs(m.final_wrapped_heading-(-Math.PI+.1))<1e-12);const peak=structuredClone(a.frames.slice(0,3)),flat=structuredClone(peak);peak.forEach((f,i)=>{f.position=[i===1?1:0,0,0];f.orientation=0;});flat.forEach(f=>{f.position=[0,0,0];f.orientation=0;});const maxima=pairedMetrics(peak,flat);assert.equal(maxima.max_separation.value,1);assert.equal(maxima.max_separation.time,.02);assert.equal(maxima.final_separation,0);y[1].time=.04;assert.throws(()=>pairedMetrics(x,y));
});
test('contact-event timestamps and current versus whole-prefix metrics',async()=>{
 const pair=await generatePair(authority,await parent(),()=>{},fast);assert.equal(pairScene(pair.result.tracks[0],0,authority.config.body.asset_offset).contacts,0);const first=pair.result.tracks[0].contact_events[0];assert.equal(pairScene(pair.result.tracks[0],first.time,authority.config.body.asset_offset).contacts,1);assert.equal(first.kind,'CONTACT');assert.equal(first.time,first.step*.02);assert.deepEqual(contactEvents(pair.result.tracks[0].frames),pair.result.tracks[0].contact_events);assert(pair.result.metrics.max_separation.value>=pair.result.metrics.final_separation);assert(pair.result.metrics.max_separation.value>0);
});
test('determinism, export/import recomputation, rehashed semantic tampering',async()=>{
 const source=await parent(100,200),pair=await generatePair(authority,source,()=>{},fast);assert.deepEqual(await generatePair(authority,source,()=>{},fast),pair);const imported=await validatePair(authority,JSON.parse(JSON.stringify(pair)));assert.deepEqual(imported,pair);
 const rehash=async(x:PairArtifact)=>{x.config_sha256=await navigationHash(x.config);x.result_sha256=await navigationHash(x.result);x.artifact_id=await navigationHash({config_sha256:x.config_sha256,result_sha256:x.result_sha256});};
 for(const change of [(x:PairArtifact)=>{x.result.tracks[1].frames[3].boundary_summary.neural_omega=.1;},(x:PairArtifact)=>{x.result.tracks[0].frames[3].position[0]+=.1;},(x:PairArtifact)=>{x.config.conditions[1].NEURAL_TO_HEADING_ENABLED=true;},(x:PairArtifact)=>{x.result.metrics.max_separation.value+=.1;}]){const fake=structuredClone(pair);change(fake);await rehash(fake);await assert.rejects(validatePair(authority,fake));}
 const reordered=JSON.parse(JSON.stringify(source,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).reverse()):v));assert.deepEqual((await generatePair(authority,reordered,()=>{},fast)).result,pair.result);
});
test('missing source, malformed logs and empty prefix fail closed',async()=>{
 const source=await parent(undefined,2);const fake=structuredClone(source);fake.log.config.propulsion=.2;await assert.rejects(generatePair(authority,fake));await assert.rejects(generatePair(authority,await new ContinuousNavigationEngine(authority).exportNavigation()));await assert.rejects(generatePair(authority,null));
});
