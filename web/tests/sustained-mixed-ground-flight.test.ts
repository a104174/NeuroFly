import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {parseNeuralLocomotion} from '../src/lib/neuralLocomotion';
import {flightCanonical,FlightClock} from '../src/lib/engineeringFlight';
import {observeFlightArena} from '../src/lib/flightArenaObservations';
import {LiveGroundSession,type LiveSample} from '../src/lib/liveGroundSession';
import {runMixedGroundFlight,runSustainedMixedGroundFlight,mixedGroundFlightHash,sustainedTakeoffEligible,validateLandingHandoff,MixedGroundFlightSession} from '../src/lib/mixedGroundFlight';
import {ReactiveFlightExplorationLab,createReactiveFlightLabSession} from '../src/components/ReactiveFlightExplorationLab';
const authority=parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json',import.meta.url),'utf8')));
test('60-second canonical sustained run repeats complete evidence with real longer neural ground episodes and preserved v10.8f hash',async()=>{
 const a=runSustainedMixedGroundFlight(authority),b=runSustainedMixedGroundFlight(authority);
 assert.equal(a.termination,'DURATION_WINDOW_COMPLETED',a.failure??'');assert(a.acceptance.passed);
 assert.equal(flightCanonical(a),flightCanonical(b));assert.equal(await mixedGroundFlightHash(a),await mixedGroundFlightHash(b));
 assert.equal(await mixedGroundFlightHash(runMixedGroundFlight(authority)),'e630d4278fb9fc94e8dd736726a7049af9d85af5df28dcfb80be864b0f1282d5');
 assert.equal(a.intervals.length,3000);assert.equal(a.metrics.final_time_s,60);
 const episodes='episodes' in a.metrics?a.metrics.episodes:[];
 assert(episodes.filter(e=>e.type==='ground'&&e.complete).length>=2);
 for(const episode of episodes.filter(e=>e.type==='ground')){
   assert(episode.duration_s>=1-1e-10);assert(episode.distance_units>=.18-1e-10);
   const init=a.handoffs.find(h=>h.global_time_s===episode.start_s)!;
   assert(init.neural_initialization?.hs.every(v=>v===0));assert(init.neural_initialization?.dn.every(v=>v===0));
   const engine=new LiveGroundSession(authority,true,'independent',undefined,{position:init.position,heading:init.heading});engine.start();
   const steps=a.intervals.filter(i=>i.sustained?.episode_id===episode.id);
   for(const interval of steps)assert.deepEqual(interval.native_evidence,engine.advance());
   assert.equal((steps[0].native_evidence as LiveSample).interval.sensory_summary,null);
 }
 assert.equal(a.metrics.accepted_bound_violations,0);assert.equal(a.metrics.invalid_command_count,0);assert.equal(a.metrics.maximum_handoff_position_discontinuity,0);assert.equal(a.metrics.maximum_timestamp_discontinuity,0);
 for(let n=0;n<a.intervals.length;n++){
   const i=a.intervals[n];assert.equal(i.global_step,n);assert.equal(i.accepted.step,n+1);assert.equal(i.accepted.time,(n+1)*.02);
   assert([...i.accepted.position,...i.accepted.velocity,i.accepted.heading].every(Number.isFinite));
   assert.equal(i.sustained?.ground_neural===null,i.active_engine!=='ground');
   i.accepted.position.forEach((v,axis)=>assert(Math.abs(v-i.observation.accepted.position[axis])<=.18*.02+1e-10));
 }
 assert(a.intervals.some(i=>i.decision.reason==='UNSAFE_LANDING_CLEARANCE_RETURN_TO_REACTIVE_EXPLORATION'));
 const guarded=a.intervals.find(i=>i.decision.reason==='UNSAFE_LANDING_CLEARANCE_RETURN_TO_REACTIVE_EXPLORATION')!;
 const native=guarded.native_evidence as {command:{intent:string;forward:number};observation:ReturnType<typeof observeFlightArena>};
 assert.equal(native.command.intent,'HOLD');assert(native.command.forward>0);
 assert(Math.min(native.observation.forward_wall_clearance_units,native.observation.left_wall_clearance_units,native.observation.right_wall_clearance_units)<.06);
});
test('same-boundary distance, elapsed ground steps, contact and clearance determine re-takeoff eligibility',()=>{
 const a=runSustainedMixedGroundFlight(authority);
 const end=a.intervals.find(i=>i.sustained?.retakeoff_eligible)!.accepted;
 assert(sustainedTakeoffEligible(.18,end,50));assert(!sustainedTakeoffEligible(.05,end,50));assert(!sustainedTakeoffEligible(.18,end,49));
 assert(!sustainedTakeoffEligible(.18,{...end,position:[.913,end.position[1],0],heading:Math.PI/2},50));
 assert(!sustainedTakeoffEligible(.18,{...end,state:'flying'},50));assert(!sustainedTakeoffEligible(.18,{...end,contacts:['FLOOR','X_WALL']},50));
 assert.throws(()=>validateLandingHandoff({...end,state:'landing'},authority),/handoff/);
});
test('sustained UI is explicit and pause/reset during walking preserves ownership without hidden steps',()=>{
 const markup=renderToStaticMarkup(createElement(ReactiveFlightExplorationLab,{modeControl:null,authority}));
 assert.match(markup,/Sustained flight \+ ground exploration/);assert.match(markup,/aria-pressed="true">Continuous exploration/);
 const s=new MixedGroundFlightSession(authority,true);s.start();while(s.controllerPhase!=='walking')s.advance();
 const clock=new FlightClock();s.pause();clock.reset();const f=s.snapshot();assert.throws(()=>s.advance(),/not running/);assert.deepEqual(f,s.snapshot());s.start();clock.advance(s,20);assert.equal(s.snapshot().step,f.step+1);
 s.dispose();assert.throws(()=>s.advance(),/not running/);
 assert.equal(createReactiveFlightLabSession('sustained',authority).snapshot().step,0);
});
