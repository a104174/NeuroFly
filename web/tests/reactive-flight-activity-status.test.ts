import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import {
  acceptedLocomotionStatusText,
  createReactiveFlightLabSession,
} from '../src/components/ReactiveFlightExplorationLab';
import { MixedGroundFlightSession } from '../src/lib/mixedGroundFlight';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';
import type { ReactiveFlightStatus } from '../src/lib/reactiveFlightExploration';

const authority = parseNeuralLocomotion(JSON.parse(readFileSync(
  new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8',
)));

function mixedActivity(session: MixedGroundFlightSession, status: ReactiveFlightStatus = session.status) {
  const accepted = session.snapshot();
  const interval = session.latestInterval();
  const groundIntervalAccepted = interval?.active_engine === 'ground' && interval.accepted.step === accepted.step;
  return acceptedLocomotionStatusText(status, accepted.state, session.controllerPhase, groundIntervalAccepted);
}

test('accepted flight and ground phases map to honest activity labels', () => {
  assert.equal(acceptedLocomotionStatusText('ready', 'grounded', 'ready', false), 'Ready to take off');
  assert.equal(acceptedLocomotionStatusText('running', 'grounded', 'ready', false), 'Preparing for takeoff');
  assert.equal(acceptedLocomotionStatusText('running', 'takeoff', 'takeoff', false), 'Taking off');
  assert.equal(acceptedLocomotionStatusText('running', 'flying', 'exploring', false), 'Flying');
  assert.equal(acceptedLocomotionStatusText('running', 'flying', 'braking', false), 'Preparing to land');
  assert.equal(acceptedLocomotionStatusText('running', 'landing', 'landing', false), 'Landing');
  assert.equal(acceptedLocomotionStatusText('running', 'grounded', 'takeoff', false), 'Preparing for takeoff');
  assert.equal(acceptedLocomotionStatusText('running', 'grounded', 'retakeoff', false), 'Preparing for takeoff');
  assert.equal(acceptedLocomotionStatusText('running', 'grounded', 'walking', true), 'Walking');
  assert.equal(acceptedLocomotionStatusText('running', 'grounded', 'walking', false), 'Grounded');
  assert.equal(acceptedLocomotionStatusText('running', 'grounded', 'retakeoff_ready', false), 'Grounded');
});

test('pause retains the accepted phase; resume, reset and unknown states stay explicit', () => {
  assert.equal(acceptedLocomotionStatusText('paused', 'grounded', 'walking', true), 'Paused · Walking');
  assert.equal(acceptedLocomotionStatusText('paused', 'flying', 'exploring', false), 'Paused · Flying');
  assert.equal(acceptedLocomotionStatusText('running', 'flying', 'exploring', false), 'Flying');
  assert.equal(acceptedLocomotionStatusText('ready', 'grounded', 'ready', false), 'Ready to take off');
  assert.equal(acceptedLocomotionStatusText('running', null, 'walking', true), 'Locomotion status unavailable');
  assert.equal(acceptedLocomotionStatusText('running', 'unknown', null, false), 'Locomotion status unavailable');
  assert.equal(acceptedLocomotionStatusText('ready', undefined, undefined, false), 'Ready');
  assert.equal(acceptedLocomotionStatusText('completed', 'flying', 'exploring', false), 'Finite trial complete');
  assert.equal(acceptedLocomotionStatusText('failed', 'landing', 'landing', false), 'Exploration stopped on error');
});

test('both mixed behaviors label real accepted takeoff, flight, landing, walking and paused walking', () => {
  for (const behavior of ['sustained', 'landing-recovery'] as const) {
    const created = createReactiveFlightLabSession(behavior, authority);
    assert(created instanceof MixedGroundFlightSession);
    const session = created;
    assert.equal(mixedActivity(session), 'Ready to take off');

    session.start();
    assert.equal(mixedActivity(session), 'Preparing for takeoff');
    session.advance();
    assert.equal(session.snapshot().state, 'takeoff');
    assert.equal(mixedActivity(session), 'Taking off');
    while (session.snapshot().state !== 'flying') session.advance();
    assert.equal(mixedActivity(session), 'Flying');

    while (session.snapshot().state !== 'landing') session.advance();
    assert.equal(mixedActivity(session), 'Landing');
    while (session.controllerPhase !== 'walking') session.advance();
    assert.equal(session.snapshot().state, 'grounded');
    assert.equal(mixedActivity(session), 'Grounded');
    session.advance();
    assert.equal(session.latestInterval()?.active_engine, 'ground');
    assert.equal(mixedActivity(session), 'Walking');

    const pausedAt = session.snapshot();
    session.pause();
    assert.deepEqual(session.snapshot(), pausedAt);
    assert.throws(() => session.advance(), /not running/);
    assert.equal(mixedActivity(session), 'Paused · Walking');
    session.start();
    session.advance();
    assert.equal(mixedActivity(session), 'Walking');
    session.dispose();

    const reset = createReactiveFlightLabSession(behavior, authority);
    assert(reset instanceof MixedGroundFlightSession);
    assert.equal(reset.snapshot().step, 0);
    assert.equal(mixedActivity(reset), 'Ready to take off');
    reset.dispose();
  }
});

test('flight-only sessions never report walking from floor altitude or controller intent', () => {
  const session = createReactiveFlightLabSession('continuous');
  assert.equal(acceptedLocomotionStatusText('ready', session.snapshot().state, session.controllerPhase, false), 'Ready to take off');
  session.start();
  assert.equal(acceptedLocomotionStatusText('running', session.snapshot().state, session.controllerPhase, false), 'Preparing for takeoff');
  session.advance();
  assert.equal(acceptedLocomotionStatusText('running', session.snapshot().state, session.controllerPhase, false), 'Taking off');
  while (session.snapshot().state !== 'flying') session.advance();
  assert.equal(acceptedLocomotionStatusText('running', session.snapshot().state, session.controllerPhase, false), 'Flying');
});
