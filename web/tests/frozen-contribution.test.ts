import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';
import { ContinuousNavigationEngine } from '../src/lib/continuousArenaNavigation';
import { InteractiveNeuralEngine } from '../src/lib/interactiveNeuralLocomotion';
import { CONFIG_PATH, CONFIG_SHA256, parseFrozen, prepareFrozen, reserveOutput, runFrozen, sha256, validateControl } from '../scripts/frozen-contribution';

// Input/orchestration-only: no second-pose experiment during test discovery.
const root = resolve(new URL('../../', import.meta.url).pathname);
const text = readFileSync(resolve(root, CONFIG_PATH), 'utf8');
test('frozen canonical bytes, complete runtime schema and matched initial state pass without advancing', async () => {
  const advance = ContinuousNavigationEngine.prototype.advance;
  const neuralAdvance = InteractiveNeuralEngine.prototype.advance;
  ContinuousNavigationEngine.prototype.advance = InteractiveNeuralEngine.prototype.advance = () => { throw new Error('Test prohibits advancement'); };
  try {
    const p = await prepareFrozen();
    assert.equal(sha256(text), CONFIG_SHA256);
    assert.equal(p.config.duration_s, 30); assert.equal(p.config.body_dt_s, .02);
    assert.equal(Number(p.config.duration_s) / Number(p.config.body_dt_s), 1500);
    assert.deepEqual(p.intervention_config, { ...p.config, mode: 'output_disabled' });
    assert.deepEqual(p.config.initial_pose, { position: [0, .11032208074629306, .12187743186950682], heading: 0 });
    assert.equal(p.control.snapshot().step, 0); assert.equal(p.control.snapshot().substeps, 0);
    const parsed = await parseFrozen(text, p.authority);
    (parsed.config.initial_pose as { heading: number }).heading = 1;
    assert.equal((JSON.parse(text).initial_pose).heading, 0);
    assert.equal(p.provenance.seed, null); assert.equal(p.provenance.random_policy, 'NONE');
    assert.equal(Object.keys(p.provenance.protected_files).length, 11);
  } finally { ContinuousNavigationEngine.prototype.advance = advance; InteractiveNeuralEngine.prototype.advance = neuralAdvance; }
});
test('missing/changed/malformed configuration or missing provenance fails before execution', async () => {
  let executions = 0;
  for (const scenario of ['missing', 'changed', 'malformed', 'source', 'manifest']) {
    const load = (path: string) => {
      if ((scenario === 'source' && path.endsWith('experimental_locomotion_v1.json')) || (scenario === 'manifest' && path.endsWith('manifest.json')) || (scenario === 'missing' && path.endsWith(CONFIG_PATH))) throw new Error('Unavailable required input');
      if (path.endsWith(CONFIG_PATH) && scenario === 'malformed') return Buffer.from('{');
      if (path.endsWith(CONFIG_PATH) && scenario === 'changed') return Buffer.from(text + '\n');
      return readFileSync(path);
    };
    await assert.rejects(prepareFrozen(load).then(() => { executions++; }));
  }
  const p = await prepareFrozen();
  await assert.rejects(parseFrozen(text + ' ', p.authority).then(() => { executions++; }), /hash/);
  assert.equal(executions, 0);
});
test('invalid pose, non-pose changes and unsupported runtime fail constructor-only validation', async () => {
  const p = await prepareFrozen(); let executions = 0;
  const configurations = [
    { ...p.config, initial_pose: { position: [4, .11032208074629306, 0], heading: 0 } },
    { ...p.config, initial_pose: { position: [0, .11032208074629306, 0], heading: NaN } },
    { ...p.config, gain: 3 }, { ...p.config, initial_hs: [1, 0, 0, 0, 0, 0] },
    { ...p.config, runtime: 'unknown' }, { ...p.config, duration_s: 29 },
    { ...p.config, initial_pose: { position: [0, 2, 0], heading: 0 } },
  ];
  for (const config of configurations) await assert.rejects(validateControl(config, p.authority).then(() => { executions++; }));
  assert.equal(executions, 0);
});
test('intervention changing more than mode is rejected without executing', async () => {
  const p = await prepareFrozen();
  const original = ContinuousNavigationEngine.prototype.navigationLog;
  ContinuousNavigationEngine.prototype.navigationLog = function () {
    const log = original.call(this);
    if (log.config.mode === 'output_disabled') log.config.gain = 3;
    return log;
  };
  try { await assert.rejects(validateControl(p.config, p.authority), /Unmatched intervention/); }
  finally { ContinuousNavigationEngine.prototype.navigationLog = original; }
});
test('output rejects existing, repository, symlink-to-repository and missing-parent paths before execution', async () => {
  const temp = mkdtempSync(resolve(tmpdir(), 'neurofly-frozen-gate-'));
  let executions = 0;
  const execute = async () => { executions++; throw new Error('Should not execute'); };
  try {
    symlinkSync(root, resolve(temp, 'repo'));
    mkdirSync(resolve(temp, 'occupied'));
    for (const path of [resolve(temp, 'occupied'), resolve(root, 'forbidden-output'), resolve(temp, 'repo', 'forbidden-output'), resolve(temp, 'missing', 'output')]) await assert.rejects(runFrozen(path, execute));
    assert.equal(executions, 0);
    const out = reserveOutput(resolve(temp, 'new'));
    assert.equal(out, resolve(temp, 'new'));
    assert.throws(() => reserveOutput(out), /already exists/);
  } finally { rmSync(temp, { recursive: true, force: true }); }
});
test('failure after preflight is preserved separately and never marked accepted', async () => {
  const temp = mkdtempSync(resolve(tmpdir(), 'neurofly-frozen-failure-'));
  const out = resolve(temp, 'run'); let executions = 0;
  try {
    await assert.rejects(runFrozen(out, async () => { executions++; throw new Error('instrumented execution failure; no advancement'); }), /instrumented/);
    assert.equal(executions, 1);
    assert.equal(JSON.parse(readFileSync(resolve(out, 'failure.json'), 'utf8')).status, 'FAILED_NOT_ACCEPTED');
    assert.throws(() => readFileSync(resolve(out, 'report.json')));
    assert.throws(() => readFileSync(resolve(out, 'checksums.json')));
  } finally { rmSync(temp, { recursive: true, force: true }); }
});
