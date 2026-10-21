import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';
import { InteractiveNeuralEngine, SOURCE_IDS, TARGET_IDS } from '../src/lib/interactiveNeuralLocomotion';
import { createFlightTrial, FlightEngine, exportFlight, flightHash, flightBounds, FLIGHT_MODEL } from '../src/lib/engineeringFlight';
import { FlightPoseNeuralAdapter, NeuralFlightEngine, NEURAL_FLIGHT_CONDITIONS, projectFlightYaw, exportNeuralFlight, importNeuralFlight, saveNeuralFlight, openNeuralFlight } from '../src/lib/neuralFlight';
const authority = parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8')));
const runs = Object.fromEntries(NEURAL_FLIGHT_CONDITIONS.map(c => { const e = new NeuralFlightEngine(authority, c); while (e.snapshot().step < 600) e.advance(); return [c, e]; })) as Record<typeof NEURAL_FLIGHT_CONDITIONS[number], NeuralFlightEngine>;
const legacy = new FlightEngine(createFlightTrial()); while (legacy.snapshot().step < 600) legacy.advance();
test('pinned actual circuit and inherited observer/kernel, no substitute solver', () => {
  assert.deepEqual(SOURCE_IDS, [10015,10016,10023,10034,10181,10419]); assert.deepEqual(TARGET_IDS,[11215,12069]);
  assert.equal(FlightPoseNeuralAdapter.prototype['calculateBoundary'], InteractiveNeuralEngine.prototype['calculateBoundary']);
  assert.equal(FlightPoseNeuralAdapter.prototype['observation'], InteractiveNeuralEngine.prototype['observation']);
  const invalid = structuredClone(authority); invalid.config.dataset_uuid = 'wrong'; assert.throws(() => new NeuralFlightEngine(invalid,'ON'));
  assert.throws(() => new FlightPoseNeuralAdapter(authority).advance());
});
test('previous completed pose observation, explicit altitude exclusion and strict ordering', () => {
  const a = new FlightPoseNeuralAdapter(authority), b = new FlightPoseNeuralAdapter(authority);
  for(let i=0;i<180;i++) { const f=legacy.frame(i), p=i?legacy.frame(i-1):undefined, high=structuredClone(f), highP=p?structuredClone(p):undefined; high.position[1]+=.2; if(highP) highP.position[1]+=.2; assert.deepEqual(a.observeAndAdvance(f,p),b.observeAndAdvance(high,highP)); }
  assert.throws(()=>a.observeAndAdvance(legacy.frame(179),legacy.frame(178)));
  const c = new FlightPoseNeuralAdapter(authority); c.observeAndAdvance(legacy.frame(0)); const f=legacy.frame(1); f.heading+=.01; const obs=c.observeAndAdvance(f,legacy.frame(0)).observation!;
  assert.ok(obs.right<0 && obs.left>0);
});
test('OFF and projection-zero reproduce all 601 legacy boundaries and original hashes', async () => {
  assert.deepEqual(runs.OFF.frames(),legacy.frames()); assert.deepEqual(runs.ZERO.frames(),legacy.frames()); assert.deepEqual(runs.OFF.records(),runs.ZERO.records());
  for(const e of Object.values(runs)) assert.equal(e.interval(599).after.substeps,120000);
  const original=await exportFlight(legacy,'normal'); assert.equal(original.input_sha256,'25af17966a60f9ed17267d6143cac86b783fd370ca09fef33ee49313177c9f61'); assert.equal(original.result_sha256,'8c8fc14e028a40fbc1aea526f253306bafc827b858a52495f0751168655528b7');
});
test('fixed bounded sign-correct projection, neutral control and protected plant seam', async () => {
  assert.equal(projectFlightYaw(.004,0,'ON').neuralTurn,.625); assert.equal(projectFlightYaw(-.004,0,'ON').neuralTurn,-.625);
  assert.equal(projectFlightYaw(0,.65,'ON').appliedTurn,.65); assert.equal(projectFlightYaw(.004,.65,'ON').appliedTurn,1); assert.ok(projectFlightYaw(.004,.65,'ON').combinedClamped);
  assert.equal(projectFlightYaw(1,0,'OFF').appliedTurn,0); assert.equal(projectFlightYaw(1,0,'ZERO').appliedTurn,0);
  for(const x of [NaN,Infinity,-Infinity,Number.MAX_VALUE]) assert.throws(()=>projectFlightYaw(x,0,'ON'));
  const e=new FlightEngine(createFlightTrial()); assert.throws(()=>e.advanceWithTurn(1.1)); e.advanceWithTurn(.1); await assert.rejects(exportFlight(e,'normal'),/versioned artifact/);
});
test('neural to yaw to unchanged integration, own-pose feedback and uninterrupted state', () => {
  let observedDivergence=false;
  for(const [condition,e] of Object.entries(runs)) {
    const frames=e.frames(), records=e.records();
    for(let i=0;i<600;i++) {
      const r=records[i]; assert.equal(r.step,i); assert.equal(r.available_time,frames[i+1].time);
      assert.deepEqual(r.yaw,projectFlightYaw(r.before.orientation_increment_eq!,r.engineering.turn,condition as typeof NEURAL_FLIGHT_CONDITIONS[number]));
      if(i) {assert.deepEqual(r.before.hs_states,records[i-1].after.hs); assert.deepEqual(r.before.dnp15_states,records[i-1].after.dn);}
      assert.equal(r.after.substeps,(i+1)*200); assert.ok(Math.abs(r.before.orientation_increment_eq! - r.before.mean_yaw_drive_eq!*.4)<1e-14);
      const due=e.config.trial.commands.find(c=>c.step===i);
      const turns=(frames[i].state!=='grounded' && frames[i].state!=='landing' && due?.intent!=='LAND') || due?.intent==='TAKEOFF';
      const expected=turns&&r.yaw.appliedTurn ? Math.round((frames[i].heading+r.yaw.appliedTurn*.8*.02)*1e12)/1e12 : frames[i].heading;
      assert.equal(frames[i+1].heading,expected);
      const held=e.config.trial.commands.findLast(c=>c.step<=i); assert.equal(r.engineering.forward,held?.forward??0); assert.equal(r.engineering.vertical,held?.vertical??0);
      assert.ok(frames[i].position.every(Number.isFinite)); const bounds=flightBounds();frames[i].position.forEach((v,axis)=>assert.ok(v>=bounds.min[axis] && v<=bounds.max[axis]));assert.equal(frames[i].position[1],runs.OFF.frame(i).position[1]);assert.equal(frames[i].velocity[1],runs.OFF.frame(i).velocity[1]);assert.ok(Math.hypot(frames[i].velocity[0],frames[i].velocity[2])<=.180000000002); assert.ok(Math.abs(r.yaw.appliedTurn)<=1);
      if(condition==='ON' && i>300 && JSON.stringify(r.observation)!==JSON.stringify(runs.OFF.interval(i).observation)) observedDivergence=true;
    }
    assert.equal(frames[600].state,'grounded'); assert.deepEqual(frames[600].velocity,[0,0,0]); assert.equal(e.interval(0).observation,null);
  }
  assert.ok(observedDivergence); assert.notDeepEqual(runs.ON.frames(),runs.OFF.frames()); assert.notDeepEqual(runs.ON.records(),runs.VISUAL_PERTURBATION.records());
  assert.deepEqual(runs.ON.snapshot().position,[.743203454314,FLIGHT_MODEL.ground_y,.061665339708]);
});
test('independent pinned Python observer and neural equations parity for all coupled intervals', () => {
  const selected=[runs.OFF,runs.ON,runs.VISUAL_PERTURBATION];
  const p=spawnSync('../.venv/bin/python',['-m','neurofly.neural_flight_reference'],{input:JSON.stringify({schema:'neural_flight_reference_input_v9',runs:selected.map(e=>({frames:e.frames(),plane:e.config.visual.plane_z}))}),encoding:'utf8',maxBuffer:12_000_000});
  assert.equal(p.status,0,p.stderr); const result=JSON.parse(p.stdout); let maxError=0;
  function parity(a:unknown,b:unknown) { if(typeof b==='number'){assert.equal(typeof a,'number'); const err=Math.abs(Number(a)-b); maxError=Math.max(maxError,err); assert.ok(err<=1e-8,`${a} != ${b}`);} else if(Array.isArray(b)){assert.equal((a as unknown[]).length,b.length);b.forEach((x,i)=>parity((a as unknown[])[i],x));} else if(b && typeof b==='object'){for(const [k,v] of Object.entries(b)) parity((a as Record<string,unknown>)[k],v);} else if(b==='PYTHON_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY') assert.equal(a,'BROWSER_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY'); else assert.equal(a,b); }
  result.forEach((r:{records:Record<string,unknown>[]},i:number)=>{assert.equal(r.records.length,600);r.records.forEach((x,j)=>{const a=selected[i].interval(j); parity({step:a.step,observation:a.observation,hs_before:a.before.hs_states,dn_before:a.before.dnp15_states,hs_after:a.after.hs,dn_after:a.after.dn,substeps:200,orientation_increment_eq:a.before.orientation_increment_eq,mean_yaw_drive_eq:a.before.mean_yaw_drive_eq},x);});});
  console.log(`Independent Python max neural/observer error: ${maxError}`);
});
test('deterministic replay, prefixes, pure seek and recomputed-hash tamper rejection', async () => {
  const run=await exportNeuralFlight(runs.ON), replay=await importNeuralFlight(authority,run); assert.deepEqual(replay.frames(),runs.ON.frames());
  const before=replay.snapshot(); replay.frame(50); replay.interval(49); assert.deepEqual(replay.snapshot(),before);
  const prefix=await exportNeuralFlight(runs.ON,100); assert.equal(prefix.result.frames.length,101); assert.equal(prefix.result.intervals.length,100); await importNeuralFlight(authority,prefix);
  assert.throws(()=>replay.frame(601)); assert.throws(()=>replay.interval(600)); await assert.rejects(exportNeuralFlight(runs.ON,601));
  for(const mutate of [(x:typeof run)=>{x.result.frames[100].position[0]+=.1;},(x:typeof run)=>{x.result.intervals[100].after.hs[0]+=.1;},(x:typeof run)=>{x.input.config.neural.source_raw_sha256='false';},(x:typeof run)=>{x.input.config.timing.substeps=199;},(x:typeof run)=>{x.input.config.neural.initial_dn[0]=.1;},(x:typeof run)=>{Object.assign(x.input.config.projection,{gain_rad_per_orientation_eq:3});},(x:typeof run)=>{x.input.stop_step=601;},(x:typeof run)=>{x.result.frames[50].time=.999;},(x:typeof run)=>{x.result.intervals[50].available_time=.99;}]) {
    const x=structuredClone(run); mutate(x); x.input_sha256=await flightHash(x.input); x.result_sha256=await flightHash(x.result); x.artifact_id=await flightHash({input_sha256:x.input_sha256,result_sha256:x.result_sha256}); await assert.rejects(importNeuralFlight(authority,x));
  }
});
test('separate compact storage, reconstruction, protected existing snapshots and visible errors', async () => {
  const map=new Map<string,string>(), store={getItem:(k:string)=>map.get(k)??null,setItem:(k:string,v:string)=>{map.set(k,v);}};
  await saveNeuralFlight(store,runs.ON); const raw=[...map.values()][0]; assert.ok(raw.length<50000); assert.ok(!raw.includes('"frames"')); assert.ok(!raw.includes('"intervals"'));
  assert.deepEqual((await openNeuralFlight(store,authority,'ON')).frames(),runs.ON.frames()); await saveNeuralFlight(store,runs.ON);
  await assert.rejects(saveNeuralFlight(store,runs.ON,100),/completed/); await assert.rejects(saveNeuralFlight({...store,setItem:()=>{throw Error('quota');}},runs.ON),/quota/);
  map.set([...map.keys()][0],'{bad'); await assert.rejects(saveNeuralFlight(store,runs.ON)); assert.equal([...map.values()][0],'{bad');
});

test('render schedules, pause and recorded seeks cannot alter coupled phase/state', async () => {
  const { FlightClock } = await import('../src/lib/engineeringFlight');
  for(const fps of [3,30,60]) {
    const e=new NeuralFlightEngine(authority,'ON'), clock=new FlightClock();
    for(let n=0;n<12*fps+2 && e.snapshot().step<600;n++) clock.advance(e,1000/fps);
    assert.deepEqual(e.frames(),runs.ON.frames()); assert.deepEqual(e.records(),runs.ON.records());
    const before=e.snapshot(); e.frame(100); e.frame(599); assert.deepEqual(e.snapshot(),before);
  }
  const e=new NeuralFlightEngine(authority,'ON'); e.advance(); const before=e.snapshot();
  // Pause is absence of accepted steps; resuming preserves the persistent kernel state.
  assert.deepEqual(e.snapshot(),before); e.advance(); assert.deepEqual(e.interval(1),runs.ON.interval(1));
});

test('explicit v9 neural artifact precision removes platform noise without rounding body or live states', async () => {
  class PlatformNoise extends NeuralFlightEngine {
    override records(stop?:number) {
      const rows=super.records(stop);
      for(const r of rows) {if(r.observation)r.observation.interval_ms+=1e-12;r.before.mean_yaw_drive_eq!+=1e-16;r.yaw.appliedTurn+=1e-14;}
      return rows;
    }
  }
  const noisy=new PlatformNoise(authority,'ON');while(noisy.snapshot().step<600)noisy.advance();
  const original=await exportNeuralFlight(runs.ON), portable=await exportNeuralFlight(noisy);
  assert.deepEqual(portable,original); assert.deepEqual(portable.result.frames,runs.ON.frames());
  const smallTamper=structuredClone(original);smallTamper.result.intervals[300].yaw.appliedTurn+=1e-9;
  smallTamper.result_sha256=await flightHash(smallTamper.result);smallTamper.artifact_id=await flightHash({input_sha256:smallTamper.input_sha256,result_sha256:smallTamper.result_sha256});await assert.rejects(importNeuralFlight(authority,smallTamper));
});
