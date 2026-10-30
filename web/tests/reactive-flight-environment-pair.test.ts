import assert from 'node:assert/strict';
import test from 'node:test';
import { FlightEngine, FLIGHT_MODEL, flightBounds, createFlightTrial, exportFlight, flightCanonical } from '../src/lib/engineeringFlight';
import { observeFlightArena } from '../src/lib/flightArenaObservations';
import { reactiveFlightResultHashes, runReactiveFlightVerification } from '../src/lib/reactiveFlightExploration';
import { ENVIRONMENT_PAIR_PROTOCOL, runReactiveFlightEnvironmentPair, validateReactiveFlightEnvironmentPair, environmentPairHash } from '../src/lib/reactiveFlightEnvironmentPair';

test('width perturbation preserves initial pose and conservative clearance; invalid geometry fails', async () => {
  const chamber = ENVIRONMENT_PAIR_PROTOCOL.variant.environment.chamber;
  assert.equal(chamber.width, 2);
  assert.deepEqual({ ...chamber, width: 2.4 }, FLIGHT_MODEL.arena);
  const engine = new FlightEngine(createFlightTrial(), chamber);
  const bounds = flightBounds(chamber);
  assert.equal(bounds.max[0], (2 - chamber.wall) / 2 - FLIGHT_MODEL.horizontal_clearance);
  assert.deepEqual(observeFlightArena(engine.snapshot(), bounds).accepted, engine.snapshot());
  for (const width of [NaN, Infinity, -1, 0, .5]) assert.throws(() => flightBounds({ ...chamber, width }));
  assert.throws(() => new FlightEngine(createFlightTrial(), { ...chamber, depth: .6 }), /inadmissible/);
  await assert.rejects(() => exportFlight(engine, 'normal'), /own versioned artifact/);
});

test('actual paired runs reproduce canonical evidence and baseline V10.8C hash', async () => {
  const pair = runReactiveFlightEnvironmentPair(), repeat = runReactiveFlightEnvironmentPair();
  assert.equal(flightCanonical(pair), flightCanonical(repeat));
  assert.equal(await environmentPairHash(pair), await environmentPairHash(repeat));
  assert.equal((await reactiveFlightResultHashes(pair.baseline)).result_sha256, '9e0bc37b5f0e15407fcb9a37ca32b55602a67c3212b97e52d56c505c1f93b019');
  assert.deepEqual(pair.baseline, runReactiveFlightVerification());
  assert.deepEqual(pair.baseline.configuration.controller, pair.variant.configuration.controller);
  assert.deepEqual(pair.baseline.configuration.initial_state, pair.variant.configuration.initial_state);
  assert.deepEqual(pair.comparison.initial_observation_differences, ['forward_wall_clearance_units']);
  assert(pair.comparison.first_command);
  assert(pair.comparison.first_heading);
  assert(pair.comparison.first_position);
  for (const run of [pair.baseline, pair.variant]) {
    const bounds = run.configuration.environment.bounds;
    let previous = run.configuration.initial_state;
    for (const interval of run.intervals) {
      assert.deepEqual(interval.observation, observeFlightArena(previous, bounds));
      assert.equal(interval.decision.command.step, previous.step);
      assert.equal(interval.accepted.step, previous.step + 1);
      interval.accepted.position.forEach((v, axis) => {
        assert(Number.isFinite(v) && v >= bounds.min[axis] && v <= bounds.max[axis]);
        assert(Math.abs(v - previous.position[axis]) <= FLIGHT_MODEL.max_forward_speed * FLIGHT_MODEL.dt_s + 1e-10);
      });
      previous = interval.accepted;
    }
  }
  const tampered = structuredClone(pair); tampered.variant.configuration.environment.bounds.max[0] += .1;
  assert.throws(() => validateReactiveFlightEnvironmentPair(tampered), /mismatched/);
  assert.throws(() => validateReactiveFlightEnvironmentPair({}), /mismatched/);
  assert.deepEqual(validateReactiveFlightEnvironmentPair(pair), pair);
});

test('plant collision uses alternate physical width, while legacy defaults remain identical', () => {
  const commands = [{ id: 'takeoff', step: 0, forward: 1, turn: 0, vertical: 0, intent: 'TAKEOFF' as const }];
  const trial = createFlightTrial(commands, 500), old = new FlightEngine(trial), explicit = new FlightEngine(trial, FLIGHT_MODEL.arena);
  const variant = new FlightEngine(trial, ENVIRONMENT_PAIR_PROTOCOL.variant.environment.chamber);
  for (let i = 0; i < 500; i++) { assert.deepEqual(old.advance(), explicit.advance()); variant.advance(); }
  assert(variant.events().some(event => event.kind === 'CONTACT' && event.detail === 'X_WALL'));
  assert.equal(variant.snapshot().position[0], flightBounds(variant.environment()).max[0]);
  assert.notEqual(variant.snapshot().position[0], old.snapshot().position[0]);
});
