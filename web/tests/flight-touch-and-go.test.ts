import assert from 'node:assert/strict';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { FlightClock, FLIGHT_MODEL, flightCanonical, flightScene } from '../src/lib/engineeringFlight';
import { observeFlightArena } from '../src/lib/flightArenaObservations';
import { runTouchAndGoVerification, canonicalTouchAndGoResult, touchAndGoResultHash, TouchAndGoSession, decideTouchAndGo } from '../src/lib/flightTouchAndGo';
import { ReactiveFlightExplorationLab, ReactiveFlightSessionLab, createReactiveFlightLabSession } from '../src/components/ReactiveFlightExplorationLab';
import { flightWingsV8 } from '../src/lib/flightWingsV8';

test('one real plant lands and takes off again with continuous accepted history and deterministic evidence', async () => {
  const a = runTouchAndGoVerification(), b = runTouchAndGoVerification();
  assert.equal(a.termination, 'SECOND_FLIGHT_CONFIRMED', a.failure ?? '');
  assert.equal(canonicalTouchAndGoResult(a), canonicalTouchAndGoResult(b));
  assert.equal(await touchAndGoResultHash(a), await touchAndGoResultHash(b));
  assert.equal(a.provenance.controller_id, 'engineering_flight_touch_and_go_v1');
  assert(a.metrics.horizontal_distance_units > 0);
  assert(a.metrics.airborne_duration_s > 0);
  assert.equal(a.metrics.accepted_bound_violations, 0);
  assert.equal(a.metrics.invalid_command_count, 0);
  assert.deepEqual(a.metrics.landing_position, a.metrics.second_takeoff_position);
  assert.notDeepEqual(a.metrics.landing_position, a.configuration.reactive_configuration.initial_state.position);
  assert.deepEqual(a.metrics.transitions.map(e => e.detail), ['grounded->takeoff','takeoff->flying','flying->landing','landing->grounded','grounded->takeoff','takeoff->flying']);
  assert.equal(a.intervals.filter(i => i.decision.command.intent === 'TAKEOFF').length, 2);
  assert.equal(a.intervals.filter(i => i.decision.command.intent === 'LAND').length, 1);
  assert.equal(a.metrics.floor_ceiling_contacts.length, 1);
  let previous = a.configuration.reactive_configuration.initial_state;
  for (const i of a.intervals) {
    assert.equal(i.observation_step, previous.step);
    assert.equal(i.observation_time_s, previous.time);
    assert.equal(i.decision.command.step, previous.step);
    assert.deepEqual(i.observation.accepted, previous);
    assert.equal(i.accepted.step, previous.step + 1);
    assert.equal(i.accepted.time, i.accepted.step * .02);
    assert.equal(i.accepted.commandId, i.decision.command.id);
    assert.equal(i.command_origin, 'ENGINEERING_TOUCH_AND_GO_V1');
    const bounds = a.configuration.reactive_configuration.environment.bounds;
    i.accepted.position.forEach((v, axis) => {
      assert(Number.isFinite(v) && v >= bounds.min[axis] && v <= bounds.max[axis]);
      assert(Math.abs(v - previous.position[axis]) <= .18 * .02 + 1e-10);
    });
    assert(i.accepted.velocity.every(Number.isFinite));
    const dv = i.accepted.velocity.map((v, axis) => v - previous.velocity[axis]);
    assert(Math.hypot(dv[0],dv[2]) <= FLIGHT_MODEL.horizontal_acceleration * .02 + 1e-10);
    // Floor contact arrests downward velocity under the existing kinematic contact rule.
    if (!i.accepted.contacts.includes('FLOOR')) assert(Math.abs(dv[1]) <= FLIGHT_MODEL.vertical_acceleration * .02 + 1e-10);
    assert.deepEqual(flightScene(i.accepted).anchor, i.accepted.position);
    const wings = flightWingsV8(i.accepted.time, i.accepted.state, i.accepted.position[1] - FLIGHT_MODEL.ground_y, 'normal');
    assert.equal(wings.source, 'ENGINEERING_3D_FLIGHT_V8');
    previous = i.accepted;
  }
});

test('matched-phase decisions refuse unsafe landing and unsettled or unverified re-takeoff', () => {
  const result = runTouchAndGoVerification();
  const landing = result.intervals.find(i => i.decision.command.intent === 'LAND')!;
  assert(landing.decision.landing_eligible);
  const safe = decideTouchAndGo(landing.decision.state_before, landing.observation);
  assert.equal(safe.command.intent, 'LAND');
  // Clearly identified mathematical state-variation fixtures; not experimental results.
  const unsafe = structuredClone(landing.observation.accepted); unsafe.velocity[0] = .1;
  const blocked = decideTouchAndGo(landing.decision.state_before, observeFlightArena(unsafe));
  assert.equal(blocked.command.intent, 'HOLD');
  assert.equal(blocked.landing_eligible, false);
  const retakeoff = result.intervals.find(i => i.decision.command.intent === 'TAKEOFF' && i.observation_step > 0)!;
  assert(retakeoff.decision.takeoff_eligible);
  const unsettled = structuredClone(retakeoff.observation.accepted); unsettled.velocity[1] = .01;
  assert.equal(decideTouchAndGo(retakeoff.decision.state_before, observeFlightArena(unsettled)).command.intent, 'HOLD');
  assert.equal(decideTouchAndGo({ ...retakeoff.decision.state_before, floor_verified: false }, retakeoff.observation).command.intent, 'HOLD');
  const notFinite = structuredClone(unsafe); notFinite.heading = NaN;
  assert.throws(() => decideTouchAndGo(landing.decision.state_before, observeFlightArena(notFinite)), /Invalid/);
  const terminal = { ...unsafe, step:1500, time:30 };
  assert.throws(() => decideTouchAndGo(landing.decision.state_before, observeFlightArena(terminal)), /duration_limit/);
  const floor = result.intervals.find(i => i.accepted.contacts.includes('FLOOR'))!;
  assert.equal(floor.accepted.state, 'grounded');
  assert(floor.accepted.velocity.every(v => v === 0));
  const hold = result.intervals.find(i => i.observation_step === floor.accepted.step)!;
  assert.equal(hold.decision.command.intent, 'HOLD');
  assert.deepEqual(hold.accepted.position, floor.accepted.position);
  assert.equal(hold.accepted.heading, floor.accepted.heading);
});

test('session pause freezes physical time, reset and behavior selection create fresh owners', () => {
  const session = new TouchAndGoSession(), clock = new FlightClock(); session.start();
  clock.advance(session, 200); session.pause(); clock.reset();
  const paused = session.snapshot();
  assert.throws(() => session.advance(), /not running/);
  assert.deepEqual(session.snapshot(), paused);
  session.start(); clock.advance(session, 20);
  assert.equal(session.snapshot().step, paused.step + 1);
  const reset = createReactiveFlightLabSession('touch-and-go');
  assert.equal(reset.status, 'ready'); assert.equal(reset.snapshot().step, 0);
  assert.equal(createReactiveFlightLabSession('continuous').controllerPhase, 'ready');
  assert.notEqual(reset, session);
  assert.equal(flightCanonical(reset.snapshot()), flightCanonical(resultInitial()));
});
function resultInitial() { return runTouchAndGoVerification().configuration.reactive_configuration.initial_state; }

test('primary reactive UI keeps continuous behavior default and exposes opt-in accepted-state landing presentation', () => {
  const normal = renderToStaticMarkup(createElement(ReactiveFlightExplorationLab, { modeControl: null }));
  assert.match(normal, /aria-pressed="true">Continuous exploration/);
  assert.match(normal, /aria-pressed="false">Landing and re-takeoff/);
  const selected = renderToStaticMarkup(createElement(ReactiveFlightSessionLab, { behavior: 'touch-and-go', modeControl: null }));
  assert.match(selected, /data-flight-behavior="touch-and-go"/);
  assert.match(selected, /engineering_flight_touch_and_go_v1/);
  assert.match(selected, /Walking is not integrated/);
  assert.match(selected, /data-flight-step="0"/);
});
