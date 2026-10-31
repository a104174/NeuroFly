import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {parseNeuralLocomotion} from '../src/lib/neuralLocomotion';import {flightCanonical,flightHash} from '../src/lib/engineeringFlight';
import {runMixedHeadingMatrix} from '../src/lib/mixedFlightHeadingMatrix';import {classifyMixedHeadingV2,classifyHeadingMatrixV2} from '../src/lib/mixedFlightClassificationV2';
test('canonical v1 parity and independent v2 interpretation of all eight real cases',async()=>{
 const a=parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json',import.meta.url),'utf8')));
 const m=await runMixedHeadingMatrix(a),before=flightCanonical(m),v=await classifyHeadingMatrixV2(m);
 assert.equal(flightCanonical(v),flightCanonical(await classifyHeadingMatrixV2(m)));assert.equal(flightCanonical(m),before);
 assert.equal(m.rows.filter(r=>r.classification==='D_INVALID_OR_UNSAFE').length,2);
 assert(v.rows.every(r=>r.integrity.status==='PASS'&&r.behavior.first_landing==='WITHIN_30_SECONDS'&&r.behavior.continuation==='COMPLETED'&&r.reproducibility==='PASS'&&r.handoffs.status==='PASS'));
 assert.equal(v.rows.filter(r=>r.contacts.events?.some(e=>e.kind==='GROUND_WALL')).length,2);
 const contact=m.rows.find(r=>r.contact_events.some(e=>e.boundary==='X_WALL'))!;
 const failed=classifyMixedHeadingV2({...contact,safety:{...contact.safety,conservative_bound_violations:1}});
 assert.equal(failed.integrity.status,'FAIL');assert(failed.contacts.observed);assert.equal(failed.behavior.first_landing,'WITHIN_30_SECONDS');
 assert.notEqual(await flightHash(v),await flightHash(m));await assert.rejects(()=>classifyHeadingMatrixV2({...m,rows:[]}));
});
test('isolated classifier fixtures preserve failures, unknown evidence and independent reproducibility',()=>{
 const safety={nonfinite_observations:0,nonfinite_accepted_states:0,conservative_bound_violations:0,invalid_handoff_attempts:0,illegal_physical_transitions:0,maximum_handoff_position_discontinuity:0,maximum_handoff_heading_discontinuity:0,maximum_timestamp_discontinuity:0,rejected_commands:0};
 for(const k of Object.keys(safety) as (keyof typeof safety)[])assert.equal(classifyMixedHeadingV2({safety:{...safety,[k]:1}}).integrity.status,'FAIL');
 assert.equal(classifyMixedHeadingV2({safety}).integrity.status,'PASS');assert.equal(classifyMixedHeadingV2({}).integrity.status,'UNDETERMINED');
 assert.equal(classifyMixedHeadingV2({safety:{...safety,nonfinite_accepted_states:NaN}}).integrity.status,'UNDETERMINED');
 assert.equal(classifyMixedHeadingV2({safety,reproduced:false}).integrity.status,'PASS');assert.equal(classifyMixedHeadingV2({safety,reproduced:false}).reproducibility,'FAIL');
 assert.equal(classifyMixedHeadingV2({first_landing_time_s:null}).behavior.first_landing,'UNDETERMINED');assert.equal(classifyMixedHeadingV2({first_landing_time_s:null,actual_end_s:60}).behavior.first_landing,'NOT_REACHED_WITHIN_HORIZON');
 assert.equal(classifyMixedHeadingV2({first_landing_time_s:31}).behavior.first_landing,'AFTER_30_SECONDS');
});
