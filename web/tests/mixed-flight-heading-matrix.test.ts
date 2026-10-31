import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {parseNeuralLocomotion} from '../src/lib/neuralLocomotion';
import {flightCanonical,flightHash,initialFlightFrame} from '../src/lib/engineeringFlight';
import {MixedGroundFlightSession} from '../src/lib/mixedGroundFlight';
import {runMixedLandingRecovery} from '../src/lib/mixedFlightLandingRecovery';
import {HEADING_MATRIX_PROTOCOL,runMixedHeadingMatrix,summarizeMixedHeadingRun,classifyHeadingLanding} from '../src/lib/mixedFlightHeadingMatrix';
const authority=parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json',import.meta.url),'utf8')));
let matrix:ReturnType<typeof runMixedHeadingMatrix>|undefined;
const evidence=()=>matrix??=runMixedHeadingMatrix(authority);

test('predeclared matrix enumerates exactly eight headings and supported initialization varies only heading',()=>{
  assert.deepEqual(HEADING_MATRIX_PROTOCOL.headings_rad,[0,Math.PI/4,Math.PI/2,3*Math.PI/4,Math.PI,5*Math.PI/4,3*Math.PI/2,7*Math.PI/4]);
  assert.equal(HEADING_MATRIX_PROTOCOL.maximum_horizon_s,60);assert.equal(HEADING_MATRIX_PROTOCOL.repeats,2);
  for(const heading of HEADING_MATRIX_PROTOCOL.headings_rad){
    const session=new MixedGroundFlightSession(authority,true,heading,true);
    assert.deepEqual(session.snapshot(),{...initialFlightFrame(),heading});session.dispose();
  }
});

test('real 16-run matrix repeats complete evidence, preserves I hashes and quantifies contact flags independently of landing counts',async()=>{
  const m=await evidence();
  assert.equal(m.rows.length,8);assert.equal(m.aggregate.canonical_runs,16);assert.equal(m.aggregate.reproduced,8);
  assert.equal(m.rows[0].canonical_hashes[0],'75924ccb594bd49efa1d697d75b13cb9638be319f895047005f0da9f2bf40048');
  assert.equal(m.rows[2].canonical_hashes[0],'fcfd8d492f8c3f2ca15a0c12b0095892087e29b7c84cd2e8350b6131ea07b43e');
  assert.equal(m.aggregate.first_landing_within_30_s,8);assert.equal(m.aggregate.ground_continuation,8);
  assert.equal(m.aggregate.unsafe,2); // Conservative evaluation flag for wall contact; not a penetration claim.
  for(const row of m.rows){
    assert.equal(row.canonical_hashes[0],row.canonical_hashes[1]);assert(row.reproduced);
    assert.equal(row.actual_end_s,60);assert.equal(row.termination,'DURATION_WINDOW_COMPLETED');assert.equal(row.failure,null);
    assert.equal(row.safety.conservative_bound_violations,0);assert.equal(row.safety.rejected_commands,0);
    assert.equal(row.safety.nonfinite_observations,0);assert.equal(row.safety.nonfinite_accepted_states,0);
    assert.equal(row.safety.illegal_physical_transitions,0);assert.equal(row.safety.invalid_handoff_attempts,0);
    assert.equal(row.safety.maximum_handoff_position_discontinuity,0);assert.equal(row.safety.maximum_handoff_heading_discontinuity,0);
    assert.equal(row.safety.maximum_timestamp_discontinuity,0);assert.equal(row.safety.ceiling_contacts,0);
    assert.equal(row.safety.floor_contacts,row.landings);
    assert.equal(row.contact_events.filter(e=>e.boundary.includes('WALL')).length,row.safety.wall_contacts);
    for(const contact of row.contact_events.filter(e=>e.boundary.includes('WALL')))assert.equal(contact.source,'ground');
  }
  // Optional external output for inspection, never a frontend dependency or committed trajectory dump.
  if(process.env.NEUROFLY_MATRIX_OUTPUT)writeFileSync(process.env.NEUROFLY_MATRIX_OUTPUT,JSON.stringify({...m,matrix_sha256:await flightHash(m)},null,2));
});

test('event extraction distinguishes missing initial recovery, timed requests/results, active override duration and later continuation',async()=>{
  const m=await evidence(),zero=m.rows[0],half=m.rows[2];
  assert.equal(zero.first_flying_time_s,.52);assert.equal(zero.first_initial_recovery?.observation_time_s,2.88);
  assert.equal(zero.first_initial_recovery?.result_time_s,2.9);assert.equal(zero.first_land_request?.observation_time_s,7.54);
  assert.equal(zero.first_landing_time_s,10.22);assert.equal(zero.first_retakeoff?.observation_time_s,11.22);
  assert.equal(half.first_initial_recovery,null);assert(half.first_recovery);assert.equal(half.initial_recovery_count,0);
  assert.equal(zero.recovery_active_duration_s,zero.recovery_activations.length*.02);
  for(const r of zero.recovery_activations){
    assert(r.eligible);assert(r.observed_clearance<.06);assert.equal(r.command.step,r.source_local_step);
    assert.equal(r.preceding_state.state,'flying');assert.equal(r.resulting_state.state,'flying');
    assert.equal(r.result_index,r.observation_index+1);
    assert.equal(r.command.intent,'HOLD');assert(r.command.forward>0);
  }
});

test('classification represents absent events without zero-time substitution and keeps safety/reproducibility overrides explicit',()=>{
  assert.equal(classifyHeadingLanding(null),'C_NO_LANDING_OBSERVED');
  assert.equal(classifyHeadingLanding(30),'A_WITHIN_30_S');assert.equal(classifyHeadingLanding(30.02),'B_AFTER_30_S');
  assert.equal(classifyHeadingLanding(60),'B_AFTER_30_S');assert.equal(classifyHeadingLanding(10,true),'D_INVALID_OR_UNSAFE');
  assert.equal(classifyHeadingLanding(10,false,false),'E_REPRODUCTION_INCONSISTENCY');
  for(const value of [NaN,Infinity,-1,61])assert.throws(()=>classifyHeadingLanding(value),/Invalid first-landing/);
});

test('malformed or mismatched scientific evidence is rejected rather than silently normalized',()=>{
  const real=runMixedLandingRecovery(authority),original=flightCanonical(real);
  assert.throws(()=>summarizeMixedHeadingRun(real,Math.PI/4,authority),/identity/);
  assert.throws(()=>summarizeMixedHeadingRun(real,NaN,authority),/identity/);
  const bad=structuredClone(real);bad.intervals[0].global_step=1;
  assert.throws(()=>summarizeMixedHeadingRun(bad,0,authority),/alignment/);
  const sensor=structuredClone(real);sensor.intervals[0].observation.forward_wall_clearance_units+=.01;
  assert.throws(()=>summarizeMixedHeadingRun(sensor,0,authority),/geometric observation/);
  assert.equal(flightCanonical(real),original);
});
