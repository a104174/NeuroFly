import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {parseNeuralLocomotion} from '../src/lib/neuralLocomotion';
import {flightCanonical,flightHash,flightBounds,initialFlightFrame,FlightClock,FLIGHT_MODEL} from '../src/lib/engineeringFlight';
import {observeFlightArena} from '../src/lib/flightArenaObservations';
import {decideReactiveFlight} from '../src/lib/reactiveFlightExploration';
import {decideTouchAndGo,decideTouchAndGoWithLandingRecovery,TOUCH_AND_GO_CONFIG,type TouchAndGoDecision,type TouchAndGoState} from '../src/lib/flightTouchAndGo';
import {MixedGroundFlightSession} from '../src/lib/mixedGroundFlight';
import {runMixedLandingRecovery} from '../src/lib/mixedFlightLandingRecovery';
import {runMixedFlightHeadingPair,mixedFlightHeadingPairHashes} from '../src/lib/mixedFlightRobustnessEvaluation';
import {LiveGroundSession,type LiveSample} from '../src/lib/liveGroundSession';
import {createReactiveFlightLabSession,ReactiveFlightExplorationLab,ReactiveFlightSessionLab} from '../src/components/ReactiveFlightExplorationLab';

const authority=parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json',import.meta.url),'utf8')));
const original=runMixedFlightHeadingPair(authority);
const corrected=runMixedLandingRecovery(authority);
type Native={decision:TouchAndGoDecision};

test('historical H hashes and missing initial override persist; the shared resumed override explains the treatment',async()=>{
  assert.deepEqual(await mixedFlightHeadingPairHashes(original),{
    baseline:'92c034ca11d507d9e2759ed5c3241ecb6510a17737388cdfe5f8d3fa96bd272b',
    variant:'51d898df0ead8c73520928f9770516b65a1497a784803eb199b8ed816fab0fea',
    pair:'d8d8f34983dabb4c5892df450d27ed54b47a56bf7a95908c02429321ad02151f'});
  assert.equal(original.variant.failure,'landing_not_reached');
  const active=corrected.intervals.find(i=>i.active_engine==='flight_initial'&&i.landing_recovery?.policy?.active)!;
  const old=original.variant.intervals[active.global_step],native=old.native_evidence as Native;
  assert.deepEqual(active.observation,old.observation);
  assert.equal(native.decision.command.forward,0);assert.equal(native.decision.command.intent,'HOLD');
  assert.equal(native.decision.state_after.phase,'braking');
  const recovery=decideTouchAndGoWithLandingRecovery(native.decision.state_before,old.observation);
  const reactive=decideReactiveFlight({phase:'exploring',avoidance_turn:0},old.observation);
  assert.deepEqual(recovery.command,reactive.command);
  assert.deepEqual(recovery.command,(active.native_evidence as Native).decision.command);
  assert(recovery.command.forward>0);assert.equal(recovery.state_after.phase,'exploring');
  assert.equal(recovery.reason,'UNSAFE_LANDING_CLEARANCE_RETURN_TO_REACTIVE_EXPLORATION');
  const resumed=original.baseline.intervals.find(i=>i.active_engine==='flight_resumed'&&i.decision.reason===recovery.reason)!;
  const d=(resumed.native_evidence as Native).decision;
  assert.deepEqual(decideTouchAndGoWithLandingRecovery(d.state_before,(resumed.native_evidence as {observation:typeof old.observation}).observation),d);
});

test('actual observation geometry preserves strict below/exactly/above 0.06 semantics and rejects invalid input',()=>{
  const state:TouchAndGoState={phase:'braking',reactive:{phase:'exploring',avoidance_turn:0},floor_verified:false};
  const fixture=(clearance:number)=>observeFlightArena({...initialFlightFrame(),step:100,time:2,state:'flying',heading:0,
    position:[0,FLIGHT_MODEL.ground_y+.3,flightBounds().max[2]-clearance]});
  for(const clearance of [.06-1e-9,.06,.06+1e-9]) {
    const o=fixture(clearance),d=decideTouchAndGoWithLandingRecovery(state,o,undefined,true);
    if(clearance===.06)assert.equal(o.forward_wall_clearance_units,.06);
    assert.equal(d.recovery?.eligible,clearance<.06);
    assert.equal(d.recovery?.required_clearance,TOUCH_AND_GO_CONFIG.minimum_horizontal_clearance);
    assert.equal(d.command.intent,clearance<.06?'HOLD':'LAND');
    assert.equal(d.landing_eligible,clearance>=.06);
    if(clearance<.06)assert(d.command.forward>0);
    assert([d.command.forward,d.command.turn,d.command.vertical].every(v=>Number.isFinite(v)&&Math.abs(v)<=1));
    assert.equal(decideTouchAndGo(state,o).command.forward,0);
  }
  const o=fixture(.05965054);
  assert.throws(()=>decideTouchAndGoWithLandingRecovery(state,{...o,forward_wall_clearance_units:NaN}),/Non-finite/);
  assert.throws(()=>decideTouchAndGoWithLandingRecovery(state,{...o,forward_wall_clearance_units:-1}),/observation/);
  assert.throws(()=>decideTouchAndGoWithLandingRecovery({...state,phase:'invalid' as TouchAndGoState['phase']},o),/invalid_controller_state/);
  assert.throws(()=>decideTouchAndGoWithLandingRecovery(state,observeFlightArena({...o.accepted,state:'grounded'})),/illegal_state_transition/);
  assert.throws(()=>decideTouchAndGoWithLandingRecovery(state,observeFlightArena({...o.accepted,heading:Infinity})),/Invalid/);
  assert.throws(()=>decideTouchAndGoWithLandingRecovery(state,observeFlightArena({...o.accepted,step:1500,time:30})),/duration_limit_reached/);
});

test('corrected heading zero lands under the original cap, continues real walking/flight, and repeats full evidence',async()=>{
  const repeated=runMixedLandingRecovery(authority);
  assert.equal(flightCanonical(corrected),flightCanonical(repeated));
  assert.equal(await flightHash(corrected),await flightHash(repeated));
  assert.equal(await flightHash(corrected),'75924ccb594bd49efa1d697d75b13cb9638be319f895047005f0da9f2bf40048');
  const firstCommandDifference=original.variant.intervals.findIndex((old,n)=>{
    const a=(old.native_evidence as Native).decision.command,b=(corrected.intervals[n].native_evidence as Native).decision.command;
    return a.forward!==b.forward||a.turn!==b.turn||a.vertical!==b.vertical||a.intent!==b.intent;
  });
  assert.equal(firstCommandDifference,144);
  assert.equal(corrected.intervals[firstCommandDifference].global_time_s,2.88);
  assert.equal(original.variant.intervals.findIndex((old,n)=>old.accepted.heading!==corrected.intervals[n].accepted.heading),205);
  assert.equal(original.variant.intervals.findIndex((old,n)=>flightCanonical(old.accepted.position)!==flightCanonical(corrected.intervals[n].accepted.position)),144);
  assert(corrected.verification.heading_zero_correction_passed);assert(corrected.verification.continuation_passed);
  assert(corrected.verification.finite_window_completed);
  assert(corrected.verification.accepted_landing_time_s!<=30);
  assert.equal(corrected.metrics.accepted_bound_violations,0);assert.equal(corrected.metrics.invalid_command_count,0);
  assert.equal(corrected.metrics.maximum_handoff_position_discontinuity,0);assert.equal(corrected.metrics.maximum_timestamp_discontinuity,0);
  const firstLand=corrected.intervals.find(i=>i.active_engine==='flight_initial'&&i.accepted.state==='grounded')!;
  assert(firstLand.accepted.contacts.includes('FLOOR'));assert(firstLand.accepted.velocity.every(v=>v===0));
  const firstHandoff=corrected.handoffs[0];assert.deepEqual(firstHandoff.position,firstLand.accepted.position);
  assert(firstHandoff.neural_initialization?.hs.every(v=>v===0));assert(firstHandoff.neural_initialization?.dn.every(v=>v===0));
  assert.equal(firstHandoff.neural_initialization?.first_observation,null);
  const ground=corrected.intervals.find(i=>i.active_engine==='ground')!;
  const independent=new LiveGroundSession(authority,true,'independent-recovery-ground',undefined,{position:firstHandoff.position,heading:firstHandoff.heading});independent.start();
  assert.deepEqual(ground.native_evidence,independent.advance());independent.stop();
  assert.equal((ground.native_evidence as LiveSample).interval.sensory_summary,null);
  const second=corrected.handoffs[1];assert.equal(second.from,'ground');assert.equal(second.to,'flight_resumed');
  const takeoff=corrected.intervals[second.global_step];assert.deepEqual(takeoff.observation.accepted.position,second.position);
  assert.equal((takeoff.native_evidence as {command:{intent:string}}).command.intent,'TAKEOFF');
  for(const [n,i] of corrected.intervals.entries()) {
    assert.equal(i.global_step,n);assert.equal(i.global_time_s,n*.02);assert.equal(i.accepted.step,n+1);assert.equal(i.accepted.time,(n+1)*.02);
    assert.equal(i.landing_recovery?.observation_global_step,n);assert.equal(i.landing_recovery?.resulting_global_step,n+1);
    assert.equal(i.landing_recovery?.context,i.active_engine);
    assert.equal(i.landing_recovery?.applicable,i.active_engine!=='ground');
    assert.equal(i.sustained?.ground_neural===null,i.active_engine!=='ground');
    for(const [axis,value] of i.accepted.position.entries())assert(Math.abs(value-i.observation.accepted.position[axis])<=.18*.02+1e-10);
    assert([...i.accepted.position,...i.accepted.velocity,i.accepted.heading].every(Number.isFinite));
    if(i.active_engine==='ground')continue;
    const native=i.native_evidence as Native&{command?:TouchAndGoDecision['command']};
    const command=native.command??native.decision.command;
    assert.equal(command.step,i.source_local_step);
    if(i.landing_recovery?.policy?.active) {
      assert.equal(command.intent,'HOLD');assert.equal(i.controller_phase_after,'exploring');assert(command.forward>0);
      assert(i.landing_recovery.policy.observed_clearance<.06);
      assert.equal(corrected.intervals[n+1].landing_recovery?.previous_interval_active,true);
    }
    if(command.intent==='LAND') {
      assert(i.landing_recovery?.landing_eligible);assert(!i.landing_recovery?.policy?.active);
      assert(i.landing_recovery!.policy!.observed_clearance>=.06);
      assert.equal(i.accepted.state,'landing');
      const next=corrected.intervals[n+1].native_evidence as Native&{command?:TouchAndGoDecision['command']};
      assert.notEqual((next.command??next.decision.command).intent,'LAND');
    }
  }
});

test('corrected pi/2 is deterministic and safe; old accepted trajectory remains numerically identical',()=>{
  const a=runMixedLandingRecovery(authority,Math.PI/2),b=runMixedLandingRecovery(authority,Math.PI/2);
  assert.equal(flightCanonical(a),flightCanonical(b));assert(a.verification.initial_landing_passed);assert(a.verification.continuation_passed);
  assert.equal(a.metrics.accepted_bound_violations,0);assert.equal(a.metrics.invalid_command_count,0);
  assert.deepEqual(a.intervals.map(i=>i.accepted),original.baseline.intervals.map(i=>i.accepted));
});

test('new Lab choice is opt-in with fresh owners; pause/resume at recovery cannot advance hidden intervals',()=>{
  const markup=renderToStaticMarkup(createElement(ReactiveFlightExplorationLab,{modeControl:null,authority}));
  assert.match(markup,/Mixed exploration — landing recovery/);assert.match(markup,/aria-pressed="true">Continuous exploration/);
  const s=createReactiveFlightLabSession('landing-recovery',authority);
  assert(s instanceof MixedGroundFlightSession);assert(s.landingRecovery);assert.equal(s.snapshot().heading,0);
  s.start();while(!s.latestInterval()?.landing_recovery?.policy?.active)s.advance();
  const frame=s.snapshot(),clock=new FlightClock();s.pause();clock.reset();
  assert.throws(()=>s.advance(),/not running/);assert.deepEqual(s.snapshot(),frame);
  s.start();clock.advance(s,20);assert.equal(s.snapshot().step,frame.step+1);s.dispose();
  assert.throws(()=>s.advance(),/not running/);
  const reset=createReactiveFlightLabSession('landing-recovery',authority);assert.equal(reset.snapshot().step,0);assert.equal(reset.controllerPhase,'ready');
  assert.equal(createReactiveFlightLabSession('sustained',authority).snapshot().heading,Math.PI/2);
  const view=renderToStaticMarkup(createElement(ReactiveFlightSessionLab,{modeControl:null,behavior:'landing-recovery',authority}));
  assert.match(view,/data-controller="mixed_ground_flight_landing_recovery_v1"/);
  assert.match(view,/data-flight-behavior="landing-recovery"/);
  assert.throws(()=>new MixedGroundFlightSession(authority,false,undefined,true),/versioned/);
});
