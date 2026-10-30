import assert from 'node:assert/strict';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { FlightEngine, FLIGHT_MODEL, createFlightTrial, exportFlight, flightCanonical, flightBounds, type FlightCommand } from '../src/lib/engineeringFlight';
import { LabSimulationModeControl } from '../src/components/lab/LabSimulationModeControl';
import { EngineeringVerticalFlightLab } from '../src/components/EngineeringVerticalFlightLab';
import { ExploreLabView } from '../src/components/lab/ExploreLabView';
import {
  VERTICAL_FLIGHT_CONFIG, VerticalFlightSession, canonicalVerticalFlightResult,
  decideVerticalFlight, runVerticalFlightVerification, verticalFlightResultHashes,
} from '../src/lib/verticalFlightFeedback';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';
import { readFileSync } from 'node:fs';
import { ContinuousNavigationEngine } from '../src/lib/continuousArenaNavigation';

const command = (step: number, intent: FlightCommand['intent'] = 'HOLD', vertical = 0): FlightCommand => ({
  id: `external-${step}`, step, forward: 0, turn: 0, vertical, intent,
});

function completeSession() {
  const session = new VerticalFlightSession();
  session.start();
  while (session.status === 'running') session.advance();
  return session;
}

test('full external command is validated, interval-aligned, one-shot and isolated from legacy trials', async () => {
  const engine = new FlightEngine(createFlightTrial([], 750));
  const before = engine.snapshot();
  assert.throws(() => engine.advanceWithCommand(command(1, 'TAKEOFF', .8)), /Invalid or misaligned/);
  assert.deepEqual(engine.snapshot(), before);
  assert.throws(() => engine.advanceWithCommand({ ...command(0), vertical: Infinity }), /Invalid or misaligned/);
  assert.throws(() => engine.advanceWithCommand({ ...command(0), unknown: 1 } as never), /Invalid or misaligned/);
  const first = engine.advanceWithCommand(command(0, 'TAKEOFF', .8));
  assert.equal(first.step, 1); assert.equal(first.time, FLIGHT_MODEL.dt_s); assert.equal(first.state, 'takeoff');
  assert.equal(first.commandId, 'external-0'); assert(first.events.some(event => event.kind === 'COMMAND'));
  const second = engine.advanceWithCommand(command(1, 'HOLD', .8)); assert.equal(second.step, 2);
  assert.throws(() => engine.advance(), /complete command/);
  assert.throws(() => engine.advanceWithTurn(0), /Cannot mix/);
  assert.throws(() => engine.advanceWithCommand({ ...command(2), id: 'external-0' }), /Invalid or misaligned/);

  const scheduled = new FlightEngine(createFlightTrial([{ id: 'scheduled', step: 0, forward: 0, turn: 0, vertical: .8, intent: 'TAKEOFF' }], 20));
  assert.throws(() => scheduled.advanceWithCommand(command(0, 'TAKEOFF', .8)), /fresh flight trial/);
  const exported = new FlightEngine(createFlightTrial([], 20)); exported.advanceWithCommand(command(0, 'TAKEOFF', .8));
  await assert.rejects(exportFlight(exported, 'normal'), /versioned artifact/);
});

test('legacy scheduled and external-turn command paths retain their old integration results', () => {
  const commands: FlightCommand[] = [
    { id: 'takeoff', step: 0, forward: 0, turn: 0, vertical: .8, intent: 'TAKEOFF' },
    { id: 'climb', step: 25, forward: .5, turn: 0, vertical: .4, intent: 'HOLD' },
    { id: 'land', step: 60, forward: 0, turn: 0, vertical: 0, intent: 'LAND' },
  ];
  const scheduled = new FlightEngine(createFlightTrial(commands, 100));
  const externalTurn = new FlightEngine(createFlightTrial(commands, 100));
  while (scheduled.snapshot().step < 100) {
    assert.deepEqual(externalTurn.advanceWithTurn(0), scheduled.advance());
  }
  assert.deepEqual(externalTurn.frames(), scheduled.frames());
});

test('accepted-state controller completes bounded takeoff, altitude feedback, descent and landing', () => {
  const session = completeSession();
  const result = session.result();
  assert.equal(session.status, 'completed'); assert.equal(result.termination, 'LANDED');
  assert.equal(result.schema, 'neurofly_vertical_flight_result_v1');
  assert.equal(result.provenance.controller_id, 'state_feedback_vertical_v1');
  assert.equal(result.provenance.command_origin, 'STATE_FEEDBACK_CONTROLLER_V1');
  assert.equal(result.configuration.environment.id, 'neurofly_experimental_arena_v1');
  assert.equal(result.intervals[0].observation.accepted.state, 'grounded');
  assert.equal(result.intervals[0].decision.command?.intent, 'TAKEOFF');
  assert.equal(result.intervals[0].accepted.state, 'takeoff');
  assert(result.intervals.some(interval => interval.accepted.state === 'flying'));
  assert(result.intervals.some(interval => interval.decision.transition_reason === 'accepted_altitude_and_vertical_speed_within_tolerance'));
  assert(result.intervals.some(interval => interval.decision.command?.intent === 'LAND'));
  assert.equal(result.metrics.final_state, 'grounded');
  assert.deepEqual(result.metrics.final_position, result.configuration.initial_state.position);
  assert(result.metrics.maximum_altitude_above_ground > 0);
  assert(result.metrics.target_condition_reached);
  assert(result.metrics.airborne_duration_s > 0);
  assert(result.metrics.descent_onset_time_s !== null);
  assert(result.metrics.landing_time_s !== null);
  assert.deepEqual(result.metrics.contacts.map(contact => contact.detail), ['FLOOR']);
  assert.equal(result.metrics.bound_violations, 0);
  assert.deepEqual(result.events.filter(event => event.kind === 'TRANSITION').map(event => event.detail), [
    'grounded->takeoff', 'takeoff->flying', 'flying->landing', 'landing->grounded',
  ]);
  let previous = result.configuration.initial_state;
  for (const interval of result.intervals) {
    assert.equal(interval.command_origin, 'STATE_FEEDBACK_CONTROLLER_V1');
    assert.equal(interval.observation_step, interval.observation.accepted.step);
    assert.equal(interval.observation_time_s, interval.observation.accepted.time);
    assert.equal(interval.decision.command?.step, interval.observation_step);
    assert.equal(interval.accepted.step, interval.observation_step + 1);
    assert.equal(interval.accepted.time, interval.accepted.step * FLIGHT_MODEL.dt_s);
    assert.equal(interval.decision.command?.forward, 0);
    assert.equal(interval.decision.command?.turn, 0);
    assert([...interval.accepted.position, ...interval.accepted.velocity].every(Number.isFinite));
    assert(Math.hypot(interval.accepted.velocity[0], interval.accepted.velocity[2]) <= FLIGHT_MODEL.max_forward_speed + 1e-12);
    assert(Math.abs(interval.accepted.velocity[1]) <= FLIGHT_MODEL.max_vertical_speed + 1e-12);
    assert(Math.hypot(interval.accepted.position[0] - previous.position[0], interval.accepted.position[2] - previous.position[2]) <= FLIGHT_MODEL.max_forward_speed * FLIGHT_MODEL.dt_s + 1e-12);
    if (!interval.accepted.contacts.length) assert(Math.abs(interval.accepted.velocity[1] - previous.velocity[1]) <= FLIGHT_MODEL.vertical_acceleration * FLIGHT_MODEL.dt_s + 1e-12);
    interval.accepted.position.forEach((value, axis) => {
      assert(value >= result.configuration.environment.bounds.min[axis]);
      assert(value <= result.configuration.environment.bounds.max[axis]);
    });
    previous = interval.accepted;
  }
  assert.equal(result.metrics.accepted_intervals, result.intervals.length);
});

test('identical verification inputs reproduce config, observations, commands, snapshots, events and hashes', async () => {
  const first = completeSession().result();
  const second = completeSession().result();
  const verified = runVerticalFlightVerification();
  assert.equal(verified.termination, 'LANDED');
  assert.equal(canonicalVerticalFlightResult(first), canonicalVerticalFlightResult(second));
  assert.deepEqual(await verticalFlightResultHashes(first), await verticalFlightResultHashes(second));
  assert.equal(canonicalVerticalFlightResult(first), canonicalVerticalFlightResult(verified));
});

test('feedback command changes for an admissible altitude perturbation at the same accepted time', () => {
  const session = new VerticalFlightSession(); session.start();
  while (session.snapshot().state !== 'flying') session.advance();
  const accepted = session.snapshot();
  const observation = { accepted, bounds: flightBounds() };
  const baseline = decideVerticalFlight('climb', observation);
  const perturbedFrame = { ...accepted, position: [...accepted.position] as [number, number, number] };
  perturbedFrame.position[1] += .04;
  const perturbed = decideVerticalFlight('climb', { ...observation, accepted: perturbedFrame });
  assert.equal(baseline.command?.step, perturbed.command?.step);
  assert.equal(baseline.command?.intent, 'HOLD'); assert.equal(perturbed.command?.intent, 'HOLD');
  assert.notEqual(baseline.command?.vertical, perturbed.command?.vertical);
  assert.equal(baseline.command?.forward, 0); assert.equal(perturbed.command?.turn, 0);
});

test('pause/resume freezes accepted state; bounded timeout and invalid controller states fail explicitly', () => {
  const session = new VerticalFlightSession(); session.start();
  for (let i = 0; i < 12; i++) session.advance();
  session.pause(); const paused = session.snapshot();
  assert.throws(() => session.advance(), /not running/); assert.deepEqual(session.snapshot(), paused);
  session.start(); session.advance(); assert.equal(session.snapshot().step, paused.step + 1);
  const shortTrial = new VerticalFlightSession({ ...VERTICAL_FLIGHT_CONFIG, maximum_duration_s: FLIGHT_MODEL.dt_s, maximum_steps: 1 } as unknown as typeof VERTICAL_FLIGHT_CONFIG);
  shortTrial.start(); shortTrial.advance();
  assert.equal(shortTrial.status, 'failed'); assert.equal(shortTrial.result().termination, 'TIMEOUT');
  assert.equal(shortTrial.snapshot().state, 'takeoff');
  const bad = { ...paused, position: [...paused.position] as [number, number, number] }; bad.position[1] = NaN;
  assert.throws(() => decideVerticalFlight('takeoff', { accepted: bad, bounds: flightBounds() }), /Invalid accepted flight/);
  assert.throws(() => decideVerticalFlight('awaiting_takeoff', { accepted: { ...paused, step: 2, time: .04 }, bounds: flightBounds() }), /accepted grounded initial state/);
});

test('primary Lab keeps ground as default and presents explicit mode selection and flight labeling', () => {
  const noop = () => {};
  const control = renderToStaticMarkup(createElement(LabSimulationModeControl, { value: 'ground', onChange: noop }));
  assert.match(control, /aria-label="Simulation mode"/);
  assert.match(control, /aria-pressed="true">Ground exploration/);
  assert.match(control, /aria-pressed="false">Vertical flight verification/);
  const groundState = new ContinuousNavigationEngine(parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8')))).snapshot();
  const ground = renderToStaticMarkup(createElement(ExploreLabView, {
    state: groundState, playing: false, error: null, notice: '', neuralEnabled: true,
    onPlay: noop, onReset: noop, onNeuralChange: noop, lagging: false, modeControl: createElement(LabSimulationModeControl, { value: 'ground', onChange: noop }),
  }, 'Existing ground viewer'));
  assert.match(ground, /data-live-step="0"/); assert.match(ground, /Vertical flight verification/);
  const flight = renderToStaticMarkup(createElement(EngineeringVerticalFlightLab, { modeControl: createElement(LabSimulationModeControl, { value: 'vertical-flight', onChange: noop }) }));
  assert.match(flight, /data-lab-mode="engineering-flight"/);
  assert.match(flight, /data-flight-status="ready"/);
  assert.match(flight, /Start takeoff/); assert.match(flight, /Reset/);
  assert.match(flight, /not MaleCNS-derived vertical control/);
  assert.match(flight, /data-flight-position="\[0,0\.11032208074629306,0\.12187743186950682\]"/);
  assert.match(flight, /Vertical flight verification/);
});

test('versioned configuration is admissible inside the existing conservative flight bounds', () => {
  const bounds = VERTICAL_FLIGHT_CONFIG.environment.bounds;
  const targetY = FLIGHT_MODEL.ground_y + VERTICAL_FLIGHT_CONFIG.controller.target_altitude_above_ground;
  assert(bounds.min[1] < targetY && targetY < bounds.max[1]);
  assert(targetY + VERTICAL_FLIGHT_CONFIG.controller.target_altitude_tolerance < bounds.max[1]);
  assert.equal(VERTICAL_FLIGHT_CONFIG.maximum_steps * VERTICAL_FLIGHT_CONFIG.interval_s, VERTICAL_FLIGHT_CONFIG.maximum_duration_s);
  assert.equal(VERTICAL_FLIGHT_CONFIG.randomness, 'NONE'); assert.equal(VERTICAL_FLIGHT_CONFIG.seed, null);
});
