import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parseNeuralLocomotion} from '../src/lib/neuralLocomotion';
import {runMixedLandingRecovery} from '../src/lib/mixedFlightLandingRecovery';
import {sustainedTakeoffEligible} from '../src/lib/mixedGroundFlight';
import {FlightEngine,createFlightTrial,FLIGHT_MODEL,flightBounds,flightCanonical,flightHash} from '../src/lib/engineeringFlight';
import {locomotionBounds} from '../src/lib/experimentalLocomotion';
import {LiveGroundSession,type LiveSample} from '../src/lib/liveGroundSession';
import {observeFlightArena} from '../src/lib/flightArenaObservations';
import {classifyHeadingLanding} from '../src/lib/mixedFlightHeadingMatrix';
const authority=parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json',import.meta.url),'utf8')));
for(const [k,hash,contactStep,admissibleStep,takeoffStep] of [
  [1,'aaf3ea83c948295fb37c6ec3841affabd4f7ec9b7db196ed550a3a6d17c8c60a',918,1024,1045],
  [7,'c4b4064eeb1d5f8621a4fc3c68b55f8f641b742f53a265496fd7dc1da3eff59c',920,1026,1048],
] as const)test('real H'+k+' contact defers destination initialization until bounds AND clearance pass, with repeat parity',async()=>{
  const run=runMixedLandingRecovery(authority,k*Math.PI/4),repeat=runMixedLandingRecovery(authority,k*Math.PI/4);
  assert.equal(flightCanonical(run),flightCanonical(repeat));assert.equal(await flightHash(run),hash);
  const contact=run.intervals[contactStep-1],f=contact.accepted;
  assert.equal(contact.active_engine,'ground');assert(f.contacts.includes('X_WALL'));
  const [x,z]=locomotionBounds(authority.config.body);
  assert.equal(Math.abs(f.position[0]),x);assert(Math.abs(f.position[2])<=z);
  assert.equal(f.position[1],FLIGHT_MODEL.ground_y);
  const ground=new LiveGroundSession(authority,true,'contact-admissibility-probe',undefined,{position:f.position,heading:f.heading});
  assert.deepEqual(ground.snapshot().position,f.position);assert.equal(ground.snapshot().heading,f.heading);ground.stop();
  const initialize=(frame:typeof f)=>new FlightEngine(createFlightTrial([],1500),FLIGHT_MODEL.arena,{position:frame.position,heading:frame.heading,velocity:frame.velocity});
  assert.throws(()=>initialize(f),/inadmissible in chamber/);
  const saved=structuredClone(f);
  const handoff=run.handoffs.find(h=>h.from==='ground'&&h.global_step>=contactStep)!;
  assert.equal(handoff.global_step,takeoffStep);
  let firstAdmissible:number|null=null;
  for(const i of run.intervals.slice(contactStep-1,takeoffStep)){
    assert.equal(i.active_engine,'ground');const a=i.accepted;
    assert(a.position.every(Number.isFinite));assert(Math.abs(a.position[0])<=x&&Math.abs(a.position[2])<=z);
    const local=(i.native_evidence as LiveSample).accepted.step;
    const eligible=sustainedTakeoffEligible(i.sustained!.ground_path_since_landing,a,local);
    assert.equal(eligible,i.sustained!.retakeoff_eligible);
    if(a.step<admissibleStep){assert.throws(()=>initialize(a),/inadmissible in chamber/);assert(!eligible);}
    else {
      const plant=initialize(a);assert.deepEqual(plant.snapshot().position,a.position);assert.equal(plant.snapshot().heading,a.heading);
      firstAdmissible??=a.step;
      const o=observeFlightArena(a),clearance=Math.min(o.forward_wall_clearance_units,o.left_wall_clearance_units,o.right_wall_clearance_units);
      if(a.step<takeoffStep){assert(!eligible);assert(clearance<.06);}
      else {assert(eligible);assert(clearance>=.06);}
    }
    assert.equal(a.time,a.step*.02);
    assert.equal(i.accepted.step,i.global_step+1);
    assert(!run.handoffs.some(h=>h.from==='ground'&&h.global_step===a.step&&a.step<takeoffStep));
  }
  assert.equal(firstAdmissible,admissibleStep);assert.deepEqual(f,saved);
  assert.deepEqual(run.intervals[contactStep].accepted.position,f.position); // Ground contact holds position; no destination clamp.
  const takeoff=run.intervals[takeoffStep],native=takeoff.native_evidence as {command:{intent:string};observation:ReturnType<typeof observeFlightArena>};
  assert.equal(takeoff.active_engine,'flight_resumed');assert.equal(native.command.intent,'TAKEOFF');
  assert.deepEqual(native.observation.accepted.position,handoff.position);assert.equal(native.observation.accepted.heading,handoff.heading);
  assert.equal(handoff.position_discontinuity,0);assert.equal(handoff.heading_discontinuity,0);
  assert.equal(run.metrics.accepted_bound_violations,0);assert.equal(run.metrics.invalid_command_count,0);
  assert.equal(run.metrics.maximum_timestamp_discontinuity,0);assert.equal(run.metrics.wall_contacts.length,1);
  assert.equal(classifyHeadingLanding(run.verification.accepted_landing_time_s,true),'D_INVALID_OR_UNSAFE'); // Historical combined flag, not a proof of unsafe physics.
  assert(Math.abs(f.position[0])>flightBounds().max[0]);
});
