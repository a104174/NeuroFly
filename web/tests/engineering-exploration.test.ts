import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { explorationCommand, explorationState, EXPLORATION_POLICY, forwardClearance } from '../src/lib/engineeringExploration';
import { ContinuousNavigationEngine } from '../src/lib/continuousArenaNavigation';
import { compareExplorationModes } from '../src/lib/explorationComparison';
import { BODY_DT } from '../src/lib/interactiveNeuralLocomotion';
import { LiveGroundSession } from '../src/lib/liveGroundSession';
import { locomotionBounds } from '../src/lib/experimentalLocomotion';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { ExploreLabView } from '../src/components/lab/ExploreLabView';

const authority = parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8')));

test('forward clearance uses the current arena rectangle and the declared heading convention', () => {
  assert.equal(forwardClearance([0, 0, 0], 0, [2, 1]), 1);
  assert.equal(forwardClearance([0, 0, 0], Math.PI / 2, [2, 1]), 2);
  assert.throws(() => forwardClearance([0, 0, 0], 0, [0, 1]), /geometry/);
});

test('the speed mapping is continuous, bounded, and unchanged in clear space', () => {
  const p = EXPLORATION_POLICY;
  assert.equal(explorationCommand(p.slow_clearance_units), p.baseline_speed_units_s);
  assert.equal(explorationCommand(p.minimum_speed_clearance_units), p.minimum_speed_units_s);
  assert(explorationCommand(.11) > p.minimum_speed_units_s && explorationCommand(.11) < p.baseline_speed_units_s);
  assert.equal(explorationCommand(10), .18);
  assert.throws(() => explorationCommand(Number.NaN), /clearance/);
});

test('behavior labels describe only measured clearance/contact transitions', () => {
  assert.equal(explorationState(.5, null, 'cruising'), 'cruising');
  assert.equal(explorationState(.1, null, 'cruising'), 'approaching_boundary');
  assert.equal(explorationState(.5, 'X_WALL', 'approaching_boundary'), 'boundary_contact');
  assert.equal(explorationState(.5, null, 'boundary_contact'), 'recovering');
  assert.equal(explorationState(.5, null, 'recovering'), 'cruising');
});

test('baseline remains frame-identical to v10.5b finite navigation', () => {
  const live = new LiveGroundSession(authority, true, 'baseline-check', undefined, undefined, 'baseline_v10_5b');
  const finite = new ContinuousNavigationEngine(authority);
  live.start();
  for (let i = 0; i < 1500; i++) {
    const sample = live.advance(), frame = finite.advance();
    assert.deepEqual(sample.interval, frame);
    assert.deepEqual(sample.accepted, finite.snapshot());
    assert.equal(sample.engineering.mode, 'baseline_v10_5b');
    assert.equal(sample.engineering.commanded_speed_units_s, .18);
  }
});

test('exploration changes only engineering speed and retains neural/yaw equations', () => {
  const [x, z] = locomotionBounds(authority.config.body), y = authority.config.body.initial_position[1];
  const initial = { position: [x - .01, y, 0] as [number, number, number], heading: Math.PI / 2 };
  const baseline = new LiveGroundSession(authority, true, 'base-near-wall', undefined, initial, 'baseline_v10_5b');
  const explore = new LiveGroundSession(authority, true, 'explore-near-wall', undefined, initial, 'engineering_exploration_v1');
  baseline.start(); explore.start();
  const baseFirst = baseline.advance(), exploreFirst = explore.advance();
  assert.deepEqual(exploreFirst.interval.neural_summary, baseFirst.interval.neural_summary);
  assert.equal(exploreFirst.interval.boundary_summary.neural_omega, baseFirst.interval.boundary_summary.neural_omega);
  assert.equal(exploreFirst.interval.boundary_summary.omega, baseFirst.interval.boundary_summary.omega);
  assert.equal(exploreFirst.engineering.state, 'approaching_boundary');
  assert(exploreFirst.engineering.commanded_speed_units_s < baseFirst.engineering.commanded_speed_units_s);
  assert.equal(exploreFirst.engineering.commanded_speed_units_s, EXPLORATION_POLICY.minimum_speed_units_s);
  assert(Math.abs(exploreFirst.engineering.actual_speed_units_s - exploreFirst.interval.linear_velocity[0]) < 1e-12);
  assert(Math.abs(explore.snapshot().position[0]) <= x && Math.abs(explore.snapshot().position[2]) <= z);
});

test('mode, pause/resume/reset and rolling telemetry preserve deterministic state', () => {
  const [x, z] = locomotionBounds(authority.config.body), y = authority.config.body.initial_position[1];
  const initial = { position: [x - .02, y, 0] as [number, number, number], heading: Math.PI / 2 };
  const a = new LiveGroundSession(authority, true, 'a', { trajectory: 4, telemetry: 3, events: 4 }, initial, 'engineering_exploration_v1');
  const b = new LiveGroundSession(authority, true, 'b', { trajectory: 4, telemetry: 3, events: 4 }, initial, 'engineering_exploration_v1');
  a.start(); b.start();
  for (let i = 0; i < 120; i++) assert.deepEqual(a.advance(), b.advance());
  const frozen = a.snapshot(); a.pause(); assert.deepEqual(a.snapshot(), frozen); a.start(); a.advance(); b.advance();
  assert.deepEqual(a.snapshot(), b.snapshot());
  assert.equal(a.telemetry.size, 3); assert(a.events.size <= 4); assert.equal(a.trajectory.size, 4);
  assert(a.telemetry.values().every(sample => Math.abs(sample.accepted.position[0]) <= x && Math.abs(sample.accepted.position[2]) <= z));
  const reset = a.reset('reset');
  assert.equal(reset.mode, 'engineering_exploration_v1'); assert.deepEqual(reset.snapshot().position, initial.position); assert.equal(reset.status, 'ready');
});

test('live controller selection is visible before a run and locked while a session is active', () => {
  const session = new LiveGroundSession(authority, true, 'mode-ui', undefined, undefined, 'engineering_exploration_v1');
  const noop = () => {};
  const render = (status: 'ready' | 'running') => renderToStaticMarkup(createElement(ExploreLabView, {
    state: session.snapshot(), playing: status === 'running', error: null, notice: '', neuralEnabled: true,
    onPlay: noop, onReset: noop, onNeuralChange: noop, onModeChange: noop, mode: 'engineering_exploration_v1',
    lagging: false, liveStatus: status, latestSample: null,
  }));
  const ready = render('ready'), running = render('running');
  assert.match(ready, /Engineering exploration · v1/);
  assert.match(running, /<select[^>]*disabled=""/);
  assert.match(running, /<input type="checkbox" checked=""\/>/);
});

test('real wall contact emits a bounded recovery transition without a scripted escape', () => {
  const [x, z] = locomotionBounds(authority.config.body), y = authority.config.body.initial_position[1];
  const session = new LiveGroundSession(authority, true, 'wall-recovery', { trajectory: 8, telemetry: 8, events: 8 }, { position: [x, y, 0], heading: Math.PI / 2 }, 'engineering_exploration_v1');
  session.start();
  for (let i = 0; i < 400 && !session.events.values().some(event => event.kind === 'BEHAVIOR' && event.detail.includes('recovering')); i++) session.advance();
  const events = session.events.values().filter(event => event.kind === 'BEHAVIOR');
  assert(events.some(event => event.detail.includes('boundary_contact')));
  assert(events.some(event => event.detail.includes('recovering') && event.detail.includes('contact_cleared')));
  const contact = events.find(event => event.kind === 'BEHAVIOR' && event.new_state === 'boundary_contact');
  const recovery = events.find(event => event.kind === 'BEHAVIOR' && event.new_state === 'recovering');
  assert.equal(contact?.controller_id, EXPLORATION_POLICY.id); assert.equal(contact?.observation.contact, 'X_WALL');
  assert.equal(recovery?.trigger, 'contact_cleared'); assert.equal(recovery?.threshold_units, null);
  assert(Math.abs(session.snapshot().position[0]) <= x && Math.abs(session.snapshot().position[2]) <= z);
});

test('unsupported runtime mode identifiers fail closed', () => {
  assert.throws(() => new LiveGroundSession(authority, true, 'bad-mode', undefined, undefined, 'invented' as never), /Invalid live locomotion mode/);
});

test('fixed-horizon A/B comparison is reproducible and computes bounded-memory aggregates', () => {
  const first = compareExplorationModes(authority, 1500);
  const repeated = compareExplorationModes(authority, 1500);
  assert.deepEqual(first, repeated);
  assert.equal(first.baseline.ticks, 1500); assert.equal(first.exploration.simulated_seconds, 30);
  assert.equal(first.baseline.containment_violations, 0); assert.equal(first.exploration.containment_violations, 0);
  assert.equal(first.baseline.non_finite_states, 0); assert.equal(first.exploration.non_finite_states, 0);
  assert(Math.abs(first.baseline.mean_commanded_speed_units_s - .18) < 1e-12);
  assert(first.exploration.mean_commanded_speed_units_s <= first.baseline.mean_commanded_speed_units_s);
  assert.equal(first.body_dt_s, BODY_DT);
});

test('long exploration continues beyond v10.5b terminal tick and multiple history wraps', () => {
  const session = new LiveGroundSession(authority, true, 'long-exploration', { trajectory: 32, telemetry: 16, events: 8 }, undefined, 'engineering_exploration_v1');
  const [x, z] = locomotionBounds(authority.config.body); session.start();
  for (let i = 0; i < 5000; i++) {
    const sample = session.advance();
    assert.equal(sample.accepted.step, i + 1);
    assert(Math.abs(sample.accepted.position[0]) <= x + 1e-12);
    assert(Math.abs(sample.accepted.position[2]) <= z + 1e-12);
    assert([...sample.accepted.hs, ...sample.accepted.dn, sample.accepted.heading].every(Number.isFinite));
  }
  assert.equal(session.snapshot().step, 5000); assert.equal(session.snapshot().time, 5000 * BODY_DT);
  assert.equal(session.telemetry.size, 16); assert.equal(session.trajectory.size, 32); assert(session.events.size <= 8);
});

test('long-horizon A/B reaches the same deterministic horizon with bounded states', () => {
  const result = compareExplorationModes(authority, 5000);
  assert.equal(result.baseline.ticks, 5000); assert.equal(result.exploration.ticks, 5000);
  assert.equal(result.baseline.containment_violations, 0); assert.equal(result.exploration.containment_violations, 0);
  assert.equal(result.baseline.non_finite_states, 0); assert.equal(result.exploration.non_finite_states, 0);
  assert(Math.abs(result.baseline.behavior_state_seconds.baseline - 100) < 1e-9);
  assert(result.exploration.behavior_state_seconds.cruising !== undefined);
});
