import assert from 'node:assert/strict';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { LabSimulationModeControl } from '../src/components/lab/LabSimulationModeControl';
import { ReactiveFlightExplorationLab } from '../src/components/ReactiveFlightExplorationLab';
import { LiveExploreArena } from '../src/components/LiveExploreArena';
import {
  FlightEngine, FLIGHT_MODEL, createFlightTrial, flightBounds, flightScene, initialFlightFrame,
  type FlightCommand, type FlightFrame,
} from '../src/lib/engineeringFlight';
import { observeFlightArena, validateFlightArenaObservation } from '../src/lib/flightArenaObservations';
import {
  REACTIVE_FLIGHT_ACCEPTANCE, REACTIVE_FLIGHT_CONFIG, ReactiveFlightExplorationSession,
  canonicalReactiveFlightResult, decideReactiveFlight, reactiveFlightResultHashes,
  runReactiveFlightVerification,
} from '../src/lib/reactiveFlightExploration';

const external = (step: number, forward: number, turn = 0, vertical = .8, intent: FlightCommand['intent'] = 'HOLD'): FlightCommand => ({
  id: `observation-fixture-${step}`, step, forward, turn, vertical, intent,
});

function takeoffToExploration() {
  const session = new ReactiveFlightExplorationSession(); session.start();
  while (session.snapshot().state !== 'flying') session.advance();
  session.advance();
  return session;
}

test('arena observations use accepted pose, plant bounds, heading convention, and deterministic ray clearances', () => {
  const bounds = flightBounds();
  const initial = initialFlightFrame();
  const observation = observeFlightArena(initial, bounds);
  assert.equal(observation.schema, 'neurofly_flight_arena_observation_v1');
  assert.equal(observation.forward_wall_clearance_units, bounds.max[0] - initial.position[0]);
  assert.equal(observation.left_wall_clearance_units, bounds.max[2] - initial.position[2]);
  assert.equal(observation.right_wall_clearance_units, initial.position[2] - bounds.min[2]);
  assert.equal(observation.floor_clearance_units, 0);
  assert.equal(observation.ceiling_clearance_units, bounds.max[1] - initial.position[1]);
  assert.deepEqual(observeFlightArena(initial, bounds), observation);

  const centered = { ...initial, position: [0, initial.position[1], 0] as [number, number, number], heading: 0 };
  const facingZ = observeFlightArena(centered, bounds);
  assert.equal(facingZ.forward_wall_clearance_units, bounds.max[2]);
  assert.equal(facingZ.left_wall_clearance_units, -bounds.min[0]);
  assert.equal(facingZ.right_wall_clearance_units, bounds.max[0]);
  assert.deepEqual(validateFlightArenaObservation(facingZ, bounds), facingZ);
});

test('observation validation fails closed for altered values, non-finite states, out-of-bounds positions, and malformed inputs', () => {
  const valid = observeFlightArena(initialFlightFrame());
  assert.throws(() => validateFlightArenaObservation({ ...valid, forward_wall_clearance_units: 99 }), /does not match/);
  const nonFinite = { ...initialFlightFrame(), heading: NaN } as FlightFrame;
  assert.throws(() => observeFlightArena(nonFinite), /Invalid accepted flight state/);
  const outside = { ...initialFlightFrame(), position: [flightBounds().max[0] + .01, FLIGHT_MODEL.ground_y, 0] as [number, number, number] };
  assert.throws(() => observeFlightArena(outside), /outside axis 0 bounds/);
  assert.throws(() => observeFlightArena(null as unknown as FlightFrame), /Invalid accepted flight state/);
});

test('terminal accepted boundary and floor or ceiling contacts do not receive another exploration command', () => {
  const terminal = {
    ...initialFlightFrame(), step: REACTIVE_FLIGHT_CONFIG.maximum_steps,
    time: REACTIVE_FLIGHT_CONFIG.maximum_duration_s, state: 'flying' as const,
  };
  assert.throws(() => decideReactiveFlight({ phase: 'exploring', avoidance_turn: 0 }, observeFlightArena(terminal)), /no outgoing command/);
  const ceiling = { ...initialFlightFrame(), state: 'flying' as const, contacts: ['CEILING'] };
  assert.throws(() => decideReactiveFlight({ phase: 'exploring', avoidance_turn: 0 }, observeFlightArena(ceiling)), /vertical contact/);
});

test('explicit start takes off through the real full-command boundary and enters accepted-state exploration', () => {
  const session = new ReactiveFlightExplorationSession();
  session.start();
  const first = session.advance();
  const firstRecord = session.latestInterval()!;
  assert.equal(firstRecord.command_origin, 'ENGINEERING_STATE_FEEDBACK_REACTIVE_V1');
  assert.equal(firstRecord.observation_step, 0);
  assert.equal(firstRecord.decision.command.intent, 'TAKEOFF');
  assert.equal(first.commandId, firstRecord.decision.command.id);
  assert.equal(first.state, 'takeoff');
  while (session.snapshot().state !== 'flying') session.advance();
  const exploring = session.advance();
  const record = session.latestInterval()!;
  assert.equal(session.controllerPhase, 'exploring');
  assert.equal(record.observation.accepted.state, 'flying');
  assert.equal(record.observation_step, record.decision.command.step);
  assert.equal(exploring.step, record.observation_step + 1);
  assert.equal(exploring.time, exploring.step * FLIGHT_MODEL.dt_s);
  assert.equal(exploring.commandId, record.decision.command.id);
  assert(!exploring.events.some(event => event.kind === 'REJECTED_COMMAND'));
});

test('open-space and near-wall observations at the same accepted interval produce different motor commands', () => {
  const stateAtStep = (forward: number) => {
    const engine = new FlightEngine(createFlightTrial([], 300));
    while (engine.snapshot().step < 220) {
      const accepted = engine.snapshot();
      engine.advanceWithCommand({
        id: `controlled-state-${accepted.step}`, step: accepted.step,
        forward, turn: 0, vertical: accepted.state === 'grounded' || accepted.state === 'takeoff' ? .8 : 0,
        intent: accepted.state === 'grounded' ? 'TAKEOFF' : 'HOLD',
      });
    }
    return engine;
  };
  const openEngine = stateAtStep(0);
  const nearWallEngine = stateAtStep(.85);
  const open = observeFlightArena(openEngine.snapshot());
  const nearWall = observeFlightArena(nearWallEngine.snapshot());
  assert.equal(open.accepted.step, nearWall.accepted.step);
  assert.equal(open.accepted.time, nearWall.accepted.time);
  assert.equal(open.accepted.state, 'flying'); assert.equal(nearWall.accepted.state, 'flying');
  assert(open.forward_wall_clearance_units > REACTIVE_FLIGHT_CONFIG.controller.wall_approach_clearance_units);
  assert(nearWall.forward_wall_clearance_units < REACTIVE_FLIGHT_CONFIG.controller.wall_approach_clearance_units);
  const controllerState = { phase: 'exploring' as const, avoidance_turn: 0 as const };
  const openDecision = decideReactiveFlight(controllerState, open);
  const wallDecision = decideReactiveFlight(controllerState, nearWall);
  assert.equal(openDecision.command.turn, 0);
  assert.notEqual(wallDecision.command.turn, 0);
  assert.equal(wallDecision.boundary_response, 'started');
  assert.notEqual(openDecision.command.forward, wallDecision.command.forward);
  assert.equal(wallDecision.command.intent, 'HOLD');
  const openAccepted = openEngine.advanceWithCommand(openDecision.command);
  const nearWallAccepted = nearWallEngine.advanceWithCommand(wallDecision.command);
  assert.equal(openAccepted.commandId, openDecision.command.id);
  assert.equal(nearWallAccepted.commandId, wallDecision.command.id);
  assert(!openAccepted.events.some(event => event.kind === 'REJECTED_COMMAND'));
  assert(!nearWallAccepted.events.some(event => event.kind === 'REJECTED_COMMAND'));
});

test('symmetric and corner observations resolve deterministically and wall contact turns toward the clearer side', () => {
  const base = { ...initialFlightFrame(), step: 26, time: 26 * FLIGHT_MODEL.dt_s, state: 'flying' as const };
  const symmetric = { ...base, position: [0, base.position[1], 0] as [number, number, number], heading: 0 };
  const symmetricObservation = observeFlightArena(symmetric);
  assert.equal(symmetricObservation.left_wall_clearance_units, symmetricObservation.right_wall_clearance_units);
  const tiedDecision = decideReactiveFlight({ phase: 'exploring', avoidance_turn: 0 }, symmetricObservation);
  assert.equal(tiedDecision.command.turn, REACTIVE_FLIGHT_CONFIG.controller.wall_turn_command);

  const bounds = flightBounds();
  const corner = { ...base, position: [bounds.max[0] - .01, base.position[1], bounds.max[2] - .01] as [number, number, number], heading: Math.PI / 4 };
  const cornerObservation = observeFlightArena(corner);
  assert([cornerObservation.forward_wall_clearance_units, cornerObservation.left_wall_clearance_units, cornerObservation.right_wall_clearance_units].every(Number.isFinite));
  const contact = { ...corner, contacts: ['X_WALL'] };
  const contactDecision = decideReactiveFlight({ phase: 'exploring', avoidance_turn: 1 }, observeFlightArena(contact));
  const expectedTurn = contactDecision.command.turn;
  assert.equal(contactDecision.boundary_response, 'redirected');
  assert.notEqual(expectedTurn, 0);
  assert.equal(expectedTurn, cornerObservation.left_wall_clearance_units >= cornerObservation.right_wall_clearance_units
    ? REACTIVE_FLIGHT_CONFIG.controller.wall_turn_command : -REACTIVE_FLIGHT_CONFIG.controller.wall_turn_command);
});

test('vertical output reacts to accepted altitude and vertical velocity, not elapsed-time scripting', () => {
  const session = takeoffToExploration();
  const accepted = session.snapshot();
  const base = decideReactiveFlight({ phase: 'exploring', avoidance_turn: 0 }, observeFlightArena(accepted));
  const higher = { ...accepted, position: [...accepted.position] as [number, number, number] };
  higher.position[1] += .05;
  const perturbed = decideReactiveFlight({ phase: 'exploring', avoidance_turn: 0 }, observeFlightArena(higher));
  assert.equal(base.command.step, perturbed.command.step);
  assert.notEqual(base.command.vertical, perturbed.command.vertical);
  assert.equal(base.command.forward, REACTIVE_FLIGHT_CONFIG.controller.cruise_forward_command);
  assert.equal(base.command.intent, 'HOLD');
  assert(!('waypoints' in REACTIVE_FLIGHT_CONFIG));
});

test('full finite verification explores horizontally, responds to walls, stays bounded and reproduces exactly', async () => {
  const first = runReactiveFlightVerification();
  const second = runReactiveFlightVerification();
  assert.equal(first.termination, 'DURATION_LIMIT_REACHED');
  assert.equal(first.acceptance.passed, true, JSON.stringify(first.acceptance.checks));
  assert.deepEqual(first.configuration, second.configuration);
  assert.equal(canonicalReactiveFlightResult(first), canonicalReactiveFlightResult(second));
  assert.deepEqual(await reactiveFlightResultHashes(first), await reactiveFlightResultHashes(second));
  assert.equal(first.configuration.schema, 'neurofly_engineering_reactive_flight_v1');
  assert.equal(first.provenance.controller_id, 'engineering_reactive_flight_v1');
  assert.equal(first.provenance.command_origin, 'ENGINEERING_STATE_FEEDBACK_REACTIVE_V1');
  assert.equal(first.metrics.final_time_s, REACTIVE_FLIGHT_CONFIG.maximum_duration_s);
  assert(first.metrics.horizontal_distance_units >= REACTIVE_FLIGHT_ACCEPTANCE.minimum_horizontal_distance_units);
  assert(first.metrics.airborne_duration_s > 0);
  assert(first.metrics.steering_response_count >= REACTIVE_FLIGHT_ACCEPTANCE.minimum_steering_responses);
  assert.equal(first.metrics.accepted_bound_violations, 0);
  assert.equal(first.metrics.floor_ceiling_contacts.length, 0);
  assert.equal(first.intervals.length, REACTIVE_FLIGHT_CONFIG.maximum_steps);
  const boundaryResponse = first.intervals.find(interval => interval.decision.boundary_response === 'started');
  assert(boundaryResponse);
  assert(boundaryResponse.observation.forward_wall_clearance_units <= REACTIVE_FLIGHT_CONFIG.controller.wall_approach_clearance_units);
  assert.notEqual(boundaryResponse.decision.command.turn, 0);
  assert.equal(boundaryResponse.accepted.commandId, boundaryResponse.decision.command.id);
  for (const interval of first.intervals) {
    assert.equal(interval.observation_step, interval.observation.accepted.step);
    assert.equal(interval.observation_time_s, interval.observation.accepted.time);
    assert.equal(interval.decision.command.step, interval.observation_step);
    assert.equal(interval.accepted.step, interval.observation_step + 1);
    assert.equal(interval.accepted.time, interval.accepted.step * FLIGHT_MODEL.dt_s);
    assert.equal(interval.accepted.commandId, interval.decision.command.id);
    assert.equal(interval.command_origin, 'ENGINEERING_STATE_FEEDBACK_REACTIVE_V1');
    assert([...interval.accepted.position, ...interval.accepted.velocity, interval.accepted.heading].every(Number.isFinite));
    assert([interval.decision.command.forward, interval.decision.command.turn, interval.decision.command.vertical].every(value => Number.isFinite(value) && Math.abs(value) <= 1));
    assert(Math.hypot(interval.accepted.velocity[0], interval.accepted.velocity[2]) <= FLIGHT_MODEL.max_forward_speed + 1e-12);
    assert(Math.abs(interval.accepted.velocity[1]) <= FLIGHT_MODEL.max_vertical_speed + 1e-12);
    interval.accepted.position.forEach((value, axis) => {
      assert(value >= first.configuration.environment.bounds.min[axis]);
      assert(value <= first.configuration.environment.bounds.max[axis]);
    });
  }
});

test('pause and resume freeze accepted state; a fresh session reset has no stale controller state', () => {
  const session = new ReactiveFlightExplorationSession(); session.start();
  for (let i = 0; i < 20; i++) session.advance();
  session.pause(); const paused = session.snapshot();
  assert.throws(() => session.advance(), /not running/);
  assert.deepEqual(session.snapshot(), paused);
  session.start(); session.advance();
  assert.equal(session.snapshot().step, paused.step + 1);
  const reset = new ReactiveFlightExplorationSession();
  assert.equal(reset.status, 'ready'); assert.equal(reset.controllerPhase, 'ready');
  assert.equal(reset.snapshot().step, 0); assert.deepEqual(reset.snapshot(), initialFlightFrame());
});

test('primary Lab keeps ground as default, retains vertical verification, and exposes labeled reactive mode', () => {
  const noop = () => {};
  const selector = renderToStaticMarkup(createElement(LabSimulationModeControl, { value: 'ground', onChange: noop }));
  assert.match(selector, /aria-label="Simulation mode"/);
  assert.match(selector, /aria-pressed="true">Ground exploration/);
  assert.match(selector, /aria-pressed="false">Vertical flight verification/);
  assert.match(selector, /aria-pressed="false">Reactive flight exploration/);
  const primaryLab = renderToStaticMarkup(createElement(LiveExploreArena));
  assert.match(primaryLab, /aria-pressed="true">Ground exploration/);
  assert.match(primaryLab, /aria-pressed="false">Vertical flight verification/);
  assert.match(primaryLab, /aria-pressed="false">Reactive flight exploration/);
  const lab = renderToStaticMarkup(createElement(ReactiveFlightExplorationLab, {
    modeControl: createElement(LabSimulationModeControl, { value: 'reactive-flight', onChange: noop }),
  }));
  assert.match(lab, /data-lab-mode="reactive-flight"/);
  assert.match(lab, /Engineering state feedback/);
  assert.match(lab, /Start takeoff/);
  assert.match(lab, /Pause/);
  assert.match(lab, /Reset/);
  assert.match(lab, /not a biological flight-control model/);
  assert.match(lab, /data-flight-position="\[0,0\.11032208074629306,0\.12187743186950682\]"/);
  const acceptedPose = flightScene(initialFlightFrame());
  assert.deepEqual(acceptedPose.anchor, initialFlightFrame().position);
});

test('full command interface remains additive and legacy scheduled outcomes are unchanged', () => {
  const commands: FlightCommand[] = [
    { id: 'takeoff', step: 0, forward: 0, turn: 0, vertical: .8, intent: 'TAKEOFF' },
    { id: 'cruise', step: 30, forward: .5, turn: 0, vertical: .2, intent: 'HOLD' },
  ];
  const scheduled = new FlightEngine(createFlightTrial(commands, 80));
  const turnPath = new FlightEngine(createFlightTrial(commands, 80));
  while (scheduled.snapshot().step < 80) assert.deepEqual(turnPath.advanceWithTurn(0), scheduled.advance());
  assert.deepEqual(turnPath.frames(), scheduled.frames());
});
