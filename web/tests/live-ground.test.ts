import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { ContinuousNavigationEngine } from '../src/lib/continuousArenaNavigation';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';
import { LiveClock, LiveGroundSession, Ring, pauseForVisibility } from '../src/lib/liveGroundSession';
import { gaitHistory } from '../src/lib/articulatedGait';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { ExploreLabView } from '../src/components/lab/ExploreLabView';
import { locomotionBounds } from '../src/lib/experimentalLocomotion';

const authority = parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8')));

test('live prefix equals finite v3 and continues beyond its terminal boundary', () => {
  const live = new LiveGroundSession(authority, true, 'live', {trajectory: 8, telemetry: 4, events: 4});
  const finite = new ContinuousNavigationEngine(authority); live.start();
  for (let n = 0; n < 1500; n++) { const frame = live.advance(); const original = finite.advance(); assert.deepEqual(frame.interval, original); assert.deepEqual(frame.accepted, finite.snapshot()); }
  assert.equal(live.snapshot().step, 1500); assert.throws(() => finite.advance(), /completed/i);
  for (let n = 1500; n < 3000; n++) live.advance();
  assert.equal(live.snapshot().step, 3000); assert.equal(live.snapshot().substeps, 600000);
  assert.equal(live.trajectory.size, 8); assert.equal(live.telemetry.size, 4); assert(live.events.size <= 4);
  assert.equal(live.telemetry.values().at(-1)?.accepted.step, 3000);
  const internals = live as unknown as {engine: {records: unknown[]; path: unknown[]; events: unknown[]}};
  assert.equal(internals.engine.records.length, 0); assert.equal(internals.engine.path.length, 0); assert.equal(internals.engine.events.length, 0);
});

test('non-finite state fails closed while retaining the last accepted snapshot', () => {
  const session = new LiveGroundSession(authority, true, 'invalid'); session.start(); session.advance();
  const accepted = session.snapshot();
  const internals = session as unknown as {engine: {pose: {position: number[]}}}; internals.engine.pose.position[0] = NaN;
  assert.throws(() => session.advance()); assert.equal(session.status, 'error'); assert.deepEqual(session.snapshot(), accepted);
  assert.equal(session.events.values().at(-1)?.kind, 'ERROR');
});

test('corner, grazing and invalid initial conditions use the established wall policy', () => {
  const [x, z] = locomotionBounds(authority.config.body), y = authority.config.body.initial_position[1];
  const capacity = {trajectory: 16, telemetry: 8, events: 8};
  const corner = new LiveGroundSession(authority, true, 'corner', capacity, {position: [x, y, z], heading: Math.PI / 4});
  corner.start(); for (let i = 0; i < 500; i++) corner.advance();
  assert(corner.snapshot().recoveries > 0); assert(Math.abs(corner.snapshot().position[0]) <= x); assert(Math.abs(corner.snapshot().position[2]) <= z);
  const grazing = new LiveGroundSession(authority, true, 'grazing', capacity, {position: [x, y, 0], heading: -Math.PI / 2});
  grazing.start(); grazing.advance(); assert(grazing.snapshot().position[0] < x);
  const restored = grazing.reset(); assert.deepEqual(restored.snapshot().position, [x, y, 0]);
  assert.throws(() => new LiveGroundSession(authority, true, 'outside', capacity, {position: [x + .1, y, 0], heading: 0}));
});

test('live engine cannot export a rolling buffer as a complete v3 recording', async () => {
  const session = new LiveGroundSession(authority, true, 'no-export');
  const internals = session as unknown as {engine: {navigationLog(): unknown; exportNavigation(): Promise<unknown>}};
  assert.throws(() => internals.engine.navigationLog(), /rolling history/);
  await assert.rejects(internals.engine.exportNavigation(), /rolling history/);
  session.stop(); assert.equal((session as unknown as {engine: unknown}).engine, null);
});

test('live controls show elapsed time and rolling history without a complete export', () => {
  const session = new LiveGroundSession(authority, true, 'ui'); const noop = () => {};
  const state = {...session.snapshot(), step: 1501, time: 30.02};
  const html = renderToStaticMarkup(createElement(ExploreLabView, {state, playing: true, error: null, notice: '', neuralEnabled: true, onPlay: noop, onReset: noop, onStop: noop, onNeuralChange: noop, lagging: false, liveStatus: 'running'}));
  assert.match(html, /00:00:30/); assert.doesNotMatch(html, /00:30 \/ 00:30/); assert.match(html, />Stop<\/button>/);
  assert.match(html, /rolling window/); assert.doesNotMatch(html, /Export session|Verify replay|Exploration complete/);
});

test('identity does not affect deterministic initial state, pause, reset or stop', () => {
  const a = new LiveGroundSession(authority, true, 'a'), b = new LiveGroundSession(authority, true, 'b');
  assert.deepEqual(a.snapshot(), b.snapshot()); assert.equal(a.config.seed, null); assert.equal(a.config.random_policy, 'NONE');
  a.start(); b.start(); for (let i = 0; i < 50; i++) { a.advance(); b.advance(); }
  assert.deepEqual(a.snapshot(), b.snapshot()); a.pause(); const frozen = a.snapshot();
  assert.throws(() => a.advance(), /not running/); assert.deepEqual(a.snapshot(), frozen);
  a.start(); a.advance(); b.advance(); assert.deepEqual(a.snapshot(), b.snapshot());
  a.stop(); assert.throws(() => a.advance(), /not running/); assert.equal(a.status, 'stopped');
  const reset = a.reset('new'); assert.deepEqual(reset.snapshot(), new LiveGroundSession(authority, true, 'fresh').snapshot()); assert.equal(reset.status, 'ready');
});

test('neural-output-disabled live mode preserves the finite v3 dynamics', () => {
  const live = new LiveGroundSession(authority, false, 'off');
  const finite = new ContinuousNavigationEngine(authority, 'output_disabled'); live.start();
  for (let i = 0; i < 1500; i++) { const sample = live.advance(); assert.deepEqual(sample.interval, finite.advance()); }
  assert.deepEqual(live.snapshot(), finite.snapshot()); assert.equal(live.snapshot().neuralHeadingChange, 0);
  assert.equal(live.snapshot().substeps, 300000);
  const reset = live.reset(); assert.equal(live.status, 'stopped'); assert.equal(reset.snapshot().step, 0);
});

test('live construction rejects an altered neural authority', () => {
  const altered = structuredClone(authority); altered.artifact_id = '0'.repeat(64);
  assert.throws(() => new LiveGroundSession(altered, true, 'bad'), /authority mismatch/);
});

test('rolling buffers preserve order and fixed clock drops excess wall time', () => {
  const ring = new Ring<number>(3); for (let n = 0; n < 8; n++) ring.push(n); assert.deepEqual(ring.values(), [5, 6, 7]);
  const s = new LiveGroundSession(authority, false, 'clock'); const clock = new LiveClock(); s.start();
  assert.deepEqual(clock.advance(s, 1000), {steps: 5, limited: true}); assert.equal(s.snapshot().time, .1);
  assert(pauseForVisibility(s, true)); const frozen = s.snapshot(); clock.advance(s, 5000); assert.deepEqual(s.snapshot(), frozen);
  assert.equal(pauseForVisibility(s, false), false); s.start(); clock.advance(s, 20); assert.equal(s.snapshot().step, 6);
});

test('incremental gait uses only the previous accepted gait state', () => {
  const s = new LiveGroundSession(authority, true, 'gait'); const first = s.snapshot();
  const bodies = [{time: first.time, position: first.position, heading: first.heading}];
  let gait = gaitHistory(bodies)[0]; s.start();
  for (let n = 0; n < 100; n++) { const next = s.advance().accepted; const body = {time: next.time, position: next.position, heading: next.heading}; bodies.push(body); gait = gaitHistory([gait.body, body], [gait])[1]; }
  assert.deepEqual(gait, gaitHistory(bodies).at(-1));
});
