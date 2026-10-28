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

// Server rendering exercises the same stateless primary inspector used in both modes.
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { SelectedNeuralState, ActivityHistory } from '../src/components/NeuralActivityExplorer3D';

test('primary inspector preserves exact identity and signed proxy semantics in both presentations', () => {
  for (const value of [0.25, -0.25, 0, null, NaN, Infinity]) {
    const html = renderToStaticMarkup(createElement(SelectedNeuralState, { name: 'HSN', side: 'R', bodyId: 10015, field: 'hs_states[0]', value }));
    assert.match(html, /HSN · Right/);
    assert.match(html, /Body ID 10015/);
    assert.match(html, /hs_states\[0\]/);
    assert.ok(html.includes(activitySign(value)));
    assert.match(html, /not a measured biological response/);
    if (value !== null && Number.isFinite(value)) {
      assert.ok(html.includes(value.toFixed(5)));
      assert.match(html, /dimensionless model units/);
    } else {
      assert.match(html, /Unavailable/);
      assert.doesNotMatch(html, /NaN|Infinity/);
    }
  }
});

test('history renderer identifies the selected structure and retains interval times and gaps', () => {
  const history = [{ tick: 4, time: 0.08, value: -0.2 }, { tick: 6, time: 0.12, value: 0.4 }];
  const before = structuredClone(history);
  const html = renderToStaticMarkup(createElement(ActivityHistory, { history, name: 'HSN R · 10015' }));
  assert.match(html, /HSN R · 10015/);
  assert.match(html, /0.08 to 0.12 seconds/);
  assert.match(html, /interval-start time/);
  assert.equal((html.match(/<circle/g) ?? []).length, 2);
  assert.equal((html.match(/<line /g) ?? []).length, 1); // zero reference; no line across missing tick 5
  assert.deepEqual(history, before);
  const empty = renderToStaticMarkup(createElement(ActivityHistory, { history: [], name: 'DNp15 L · 12069' }));
  assert.match(empty, /No recent valid samples/);
});
