import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';
import { LiveGroundSession } from '../src/lib/liveGroundSession';
import { neuralActivityTrace } from '../src/lib/neuralActivityTrace';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { ExploreLabView } from '../src/components/lab/ExploreLabView';

const authority = parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8')));

test('trace uses the real left-boundary states and outgoing contributions', () => {
  for (const enabled of [true, false]) {
    const session = new LiveGroundSession(authority, enabled, 'trace'); session.start();
    for (let i = 0; i < 20; i++) session.advance();
    const sample = session.advance(), trace = neuralActivityTrace(sample);
    assert.deepEqual(trace.states.map(s => s.id), [10015, 10016, 10023, 10034, 10181, 10419, 11215, 12069]);
    assert.deepEqual(trace.states.map(s => s.value), [...sample.interval.neural_summary!.hs_states, ...sample.interval.neural_summary!.dnp15_states]);
    assert.equal(trace.accepted_tick, trace.tick + 1);
    assert.equal(trace.neural_yaw_rad_s, sample.interval.boundary_summary.neural_omega);
    assert.equal(trace.boundary_yaw_rad_s, sample.interval.boundary_summary.omega);
    assert.equal(trace.angular_velocity_rad_s, trace.neural_yaw_rad_s + trace.boundary_yaw_rad_s);
    assert.equal(trace.neural_enabled, enabled);
    if (!enabled) assert.equal(trace.neural_yaw_rad_s, 0);
    assert.deepEqual(trace.accepted_position, sample.accepted.position);
    assert.equal(trace.provenance.authority_artifact_id, sample.source.authority_artifact_id);
    assert.equal(trace.provenance.authority_config_sha256, authority.config_sha256);
    assert.equal(trace.engineering.accepted_speed_units_s, sample.engineering.actual_speed_units_s);
  }
});

test('the explanation displays the computed interval and its separate yaw components', () => {
  const session = new LiveGroundSession(authority, true, 'ui'); session.start();
  for (let i = 0; i < 20; i++) session.advance();
  const sample = session.advance(), trace = neuralActivityTrace(sample), noop = () => {};
  const html = renderToStaticMarkup(createElement(ExploreLabView, {state: sample.accepted, playing: true, error: null, notice: '', neuralEnabled: true, onPlay: noop, onReset: noop, onNeuralChange: noop, lagging: false, liveStatus: 'running', latestSample: sample}));
  assert.match(html, /Why did it turn\?/);
  assert.ok(html.includes(trace.neural_yaw_rad_s.toFixed(4)));
  assert.ok(html.includes(trace.boundary_yaw_rad_s.toFixed(4)));
  assert.match(html, /MaleCNS-derived authority supplies structural connectivity/);
  assert.match(html, /not calibrated fluorescence/);
});
