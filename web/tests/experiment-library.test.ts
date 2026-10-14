import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parseNeuralLocomotion} from '../src/lib/neuralLocomotion';
import {ContinuousNavigationEngine,navigationHash,replayNavigationInChunks,replayNavigation} from '../src/lib/continuousArenaNavigation';
import {ExperimentLibrary,createRecord,restoreRecord,compareRecord,renameRecord,inspectRecord,experimentName,type LibraryRecord} from '../src/lib/experimentSessionLibrary';
const authority=parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json',import.meta.url),'utf8')));
async function sample(){const e=new ContinuousNavigationEngine(authority);for(let n=0;n<160;n++){if(n===100)e.requestPlane(-.4);e.advance();}e.requestPlane(.4);return e.exportNavigation();}
async function rehash(r:LibraryRecord){const {record_sha256,...body}=r;void record_sha256;r.record_sha256=await navigationHash(body);}
/** Minimal atomic IDB event fixture. Actual IndexedDB/reload is tested in browser. */
function fixture(){
 const rows=new Map<string,LibraryRecord>();let quota=false;
 const factory={open(){const req={} as IDBOpenDBRequest;setTimeout(()=>{Object.assign(req,{result:{objectStoreNames:{contains:()=>true},close(){},transaction(){
  const tx={} as IDBTransaction;const working=new Map(rows);let aborted=false;
  const request=(action:()=>unknown)=>{const r={} as IDBRequest;setTimeout(()=>{if(aborted)return;try{Object.assign(r,{result:structuredClone(action())});r.onsuccess?.call(r,{} as Event);}catch(e){Object.assign(tx,{error:e});aborted=true;tx.onabort?.call(tx,{} as Event);}},0);return r;};
  const store={get:(id:string)=>request(()=>working.get(id)),getAll:()=>request(()=>Array.from(working.values())),add:(r:LibraryRecord)=>request(()=>{if(quota)throw new DOMException('Quota exhausted','QuotaExceededError');if(working.has(r.id))throw new Error('Duplicate key');working.set(r.id,structuredClone(r));}),put:(r:LibraryRecord)=>request(()=>{if(quota)throw new DOMException('Quota exhausted','QuotaExceededError');working.set(r.id,structuredClone(r));}),delete:(id:string)=>request(()=>working.delete(id))};
  Object.assign(tx,{objectStore:()=>store,abort(){aborted=true;setTimeout(()=>tx.onabort?.call(tx,{} as Event),0);}});
  // Nested get->put callbacks complete before commit; no partial rows on abort.
  setTimeout(()=>{if(aborted)return;rows.clear();working.forEach((v,k)=>rows.set(k,v));tx.oncomplete?.call(tx,{} as Event);},15);
  return tx;
 }}});req.onsuccess?.call(req,{} as Event);},0);return req;}} as unknown as IDBFactory;
 return {factory,rows,setQuota:(v:boolean)=>{quota=v;}};
}
test('scientific inputs only, unchanged source and deterministic restore after intervention',async()=>{
 const s=await sample(),before=structuredClone(s),r=await createRecord(authority,s,' Experiência A ');assert.deepEqual(s,before);assert.equal(r.name,'Experiência A');assert.equal(r.source_session_id,s.artifact_id);assert.equal(r.inputs.artifact_id,s.artifact_id);assert.equal(r.summary.status,'RECORDED_PREFIX');assert(!('telemetry' in r.inputs));assert(!JSON.stringify(r).includes('hs_states'));assert(JSON.stringify(r).length<15000);
 const restored=await restoreRecord(authority,JSON.parse(JSON.stringify(r)));assert.deepEqual(restored.session,s);assert.equal(restored.engine.snapshot().substeps,160*200);assert.deepEqual(restored.engine.navigationLog().events,s.log.events);assert.equal(restored.engine.pendingPlane(),.4);assert.notDeepEqual(restored.engine.snapshot().hs,[0,0,0,0,0,0]);
});
test('stable scientific identity, duplicate names allowed and rename changes only metadata',async()=>{
 const s=await sample(),a=await createRecord(authority,s,'Same'),b=await createRecord(authority,s,'Same');assert.notEqual(a.id,b.id);assert.equal(a.inputs.artifact_id,b.inputs.artifact_id);const changed=await renameRecord(a,'Renamed');assert.equal(changed.id,a.id);assert.deepEqual(changed.inputs,a.inputs);assert.equal(changed.created_at,a.created_at);assert.notEqual(changed.revision,a.revision);assert.equal((await restoreRecord(authority,changed)).session.artifact_id,s.artifact_id);
 for(const name of ['', ' ', 'x'.repeat(101),'bad\nname'])assert.throws(()=>experimentName(name));
});
test('atomic indexedDB save/load/new instance/rename/concurrency/confirmed cascade',async()=>{
 const f=fixture(),db=new ExperimentLibrary(f.factory),r=await createRecord(authority,await sample(),'A');await db.insert(r);const reloaded=new ExperimentLibrary(f.factory);assert.equal((await reloaded.list()).length,1);assert.deepEqual(await reloaded.get(r.id),r);const independent=new ContinuousNavigationEngine(authority,'output_disabled');independent.advance();const other=await createRecord(authority,await independent.exportNavigation(),'A');await db.insert(other);assert.equal((await db.list()).length,2);assert.equal((await reloaded.get(other.id)).summary.mode,'output_disabled');assert.deepEqual((await restoreRecord(authority,await reloaded.get(other.id))).engine.snapshot(),independent.snapshot());
 const changed=await renameRecord(r,'B');await db.replace(changed,r.revision);await assert.rejects(db.replace(r,r.revision),/noutra aba/);await assert.rejects(db.remove(r.id,false));assert.equal((await db.list()).length,2);
 const comparison=await compareRecord(authority,changed);await db.replace(comparison.record,changed.revision);assert(comparison.record.comparison);await db.remove(r.id,true,comparison.record.revision);assert.equal((await db.list()).length,1);assert(!f.rows.has(r.id));await assert.rejects(db.get(r.id));
});
test('quota, unavailable storage, interrupted/failed writes never report success',async()=>{
 const f=fixture(),db=new ExperimentLibrary(f.factory),r=await createRecord(authority,await sample(),'A');f.setQuota(true);await assert.rejects(db.insert(r),/Quota/);assert.equal(f.rows.size,0);f.setQuota(false);await db.insert(r);await assert.rejects(db.insert(r),/Duplicate/);assert.equal(f.rows.size,1);const changed=await renameRecord(r,'B');f.setQuota(true);await assert.rejects(db.replace(changed,r.revision),/Quota/);assert.deepEqual(f.rows.get(r.id),r);await assert.rejects(new ExperimentLibrary(undefined).list(),/indisponível/);
});
test('corrupted/version-mismatched/rehashed contradictory local inputs fail closed',async()=>{
 const r=await createRecord(authority,await sample(),'A');const broken=structuredClone(r);broken.record_sha256='0'.repeat(64);await assert.rejects(inspectRecord(broken));await assert.rejects(inspectRecord({...r,schema:'future'}));
 const wrongSummary=structuredClone(r);wrongSummary.summary.distance+=.1;await rehash(wrongSummary);await assert.rejects(restoreRecord(authority,wrongSummary),/Distância/);
 const altered=structuredClone(r);altered.inputs.log.config.neural_dt_s=.001;altered.inputs.config_sha256=await navigationHash(altered.inputs.log.config);altered.inputs.log_sha256=await navigationHash(altered.inputs.log);altered.inputs.artifact_id=await navigationHash({log_sha256:altered.inputs.log_sha256,result_sha256:altered.inputs.result_sha256});await rehash(altered);await assert.rejects(restoreRecord(authority,altered),/provenance/);
 const f=fixture();f.rows.set(r.id,broken);const listed=await new ExperimentLibrary(f.factory).list();assert.equal(listed[0].record,null);assert(listed[0].error);
});
test('comparison reference regenerated without trajectories; original preserved, OFF computes neural',async()=>{
 const r=await createRecord(authority,await sample(),'A'),before=structuredClone(r),result=await compareRecord(authority,r);assert.deepEqual(r,before);assert(!('tracks' in result.record.comparison!));assert.equal(result.record.comparison!.parent_session_id,r.inputs.artifact_id);const next=await compareRecord(authority,result.record);assert.equal(next.pair.artifact_id,result.pair.artifact_id);const off=result.pair.result.tracks[1];assert(off.frames.every(f=>f.boundary_summary.neural_omega===0));assert(off.frames.some(f=>Math.abs(f.neural_summary!.mean_yaw_drive_eq??0)>0));assert.deepEqual(next.pair.parent.log.events,r.inputs.log.events);
 const fake=structuredClone(result.record);fake.comparison!.artifact_id='0'.repeat(64);await rehash(fake);await assert.rejects(compareRecord(authority,fake),/referência/);
});
test('existing portable JSON semantic validation rejects fabricated rehashed output',async()=>{
 const s=await sample();s.telemetry.final_state.position[0]+=.1;s.result_sha256=await navigationHash(s.telemetry);s.artifact_id=await navigationHash({log_sha256:s.log_sha256,result_sha256:s.result_sha256});await assert.rejects(createRecord(authority,s,'Bad'),/semantic/);await assert.rejects(createRecord(authority,await new ContinuousNavigationEngine(authority).exportNavigation(),'Empty'));
});

test('cooperative scheduling preserves exact old replay and all 200-substep boundaries',async()=>{
 const s=await sample();let yields=0;const chunked=await replayNavigationInChunks(authority,s.log,async()=>{yields++;});assert.equal(yields,3);assert.deepEqual(await chunked.exportNavigation(),await replayNavigation(authority,s.log).exportNavigation());assert.equal(chunked.snapshot().substeps,32000);
});
