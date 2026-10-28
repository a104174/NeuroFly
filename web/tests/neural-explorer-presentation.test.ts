import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';
import { LiveGroundSession } from '../src/lib/liveGroundSession';
import { activityHistory, activitySign } from '../src/lib/neuralExplorerPresentation';
import { turnExplanation } from '../src/components/lab/ExploreLabView';

const authority = parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8')));

test('history uses bounded real interval states, follows selection and resets with the session', () => {
  const session = new LiveGroundSession(authority, true, 'history', { trajectory: 16, telemetry: 16, events: 16 });
  session.start(); for (let i = 0; i < 25; i++) session.advance();
  const samples = session.telemetry.values();
  const hs = activityHistory(samples, 10015), dn = activityHistory(samples, 11215);
  assert.equal(hs.length, 16);
  assert.equal(hs[0].tick, 9);
  assert.equal(hs[0].time, samples[0].interval.time);
  assert.equal(hs[0].value, samples[0].interval.neural_summary!.hs_states[0]);
  assert.equal(dn[0].value, samples[0].interval.neural_summary!.dnp15_states[0]);
  assert.deepEqual(activityHistory(samples, -1), []);
  session.pause(); assert.deepEqual(activityHistory(session.telemetry.values(), 10015), hs);
  session.start(); session.advance(); assert.equal(activityHistory(session.telemetry.values(), 10015).at(-1)!.tick, 25);
  assert.deepEqual(activityHistory(session.reset('new').telemetry.values(), 10015), []);
});

test('activity signs and movement explanation reflect actual values', () => {
  assert.equal(activitySign(null), 'unavailable'); assert.equal(activitySign(0), 'zero');
  assert.equal(activitySign(-0.2), 'negative'); assert.equal(activitySign(0.2), 'positive');
  assert.match(turnExplanation(0, 0, 0), /not rotating/);
  assert.match(turnExplanation(0, 0.2, 0.2), /neural circuit contributes no yaw/);
  assert.match(turnExplanation(0.1, 0, 0.1), /boundary response contributes no yaw/);
  assert.match(turnExplanation(NaN, 0, 0), /unavailable/);
});
