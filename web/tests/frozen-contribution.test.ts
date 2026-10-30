import test from 'node:test';
import assert from 'node:assert/strict';
import { appendFileSync, copyFileSync, existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync, unlinkSync, writeFileSync } from 'node:fs';
import { execFileSync, spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ContinuousNavigationEngine } from '../src/lib/continuousArenaNavigation';
import { InteractiveNeuralEngine } from '../src/lib/interactiveNeuralLocomotion';
import { CONFIG_PATH, CONFIG_SHA256, PROTOCOL_COMMIT, parseFrozen, prepareFrozen, reserveOutput, runFrozen, sha256, validateControl } from '../scripts/frozen-contribution';

// Input/orchestration-only: no second-pose experiment during test discovery.
const root = resolve(new URL('../../', import.meta.url).pathname);
const text = readFileSync(resolve(root, CONFIG_PATH), 'utf8');
const guardSource = fileURLToPath(new URL('../scripts/frozen-contribution.ts', import.meta.url));
const currentCommit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim();

function createGuardFixture() {
  const temp = mkdtempSync(join(tmpdir(), 'neurofly-frozen-guard-'));
  const repo = resolve(temp, 'repo');
  execFileSync('git', ['clone', '--quiet', '--shared', '--no-checkout', root, repo]);
  execFileSync('git', ['checkout', '--quiet', '--detach', currentCommit], { cwd: repo });
  symlinkSync(resolve(root, 'web/node_modules'), resolve(repo, 'web/node_modules'), 'dir');
  const runner = resolve(repo, 'web/scripts/frozen-contribution.ts');
  const restoreRunner = () => copyFileSync(guardSource, runner);
  restoreRunner();
  const reset = () => {
    execFileSync('git', ['reset', '--hard', 'HEAD'], { cwd: repo, stdio: 'ignore' });
    execFileSync('git', ['clean', '-fd'], { cwd: repo, stdio: 'ignore' });
    if (!existsSync(resolve(repo, 'web/node_modules'))) symlinkSync(resolve(root, 'web/node_modules'), resolve(repo, 'web/node_modules'), 'dir');
    restoreRunner();
  };
  const check = (extraEnv: Record<string, string> = {}) => {
    const env = { ...process.env };
    delete env.TSX_TSCONFIG_PATH;
    delete env.NODE_PATH;
    delete env.NODE_OPTIONS;
    Object.assign(env, extraEnv);
    const result = spawnSync(process.execPath, ['--import', 'tsx', 'scripts/frozen-contribution.ts', '--check'], {
      cwd: resolve(repo, 'web'), env, encoding: 'utf8',
    });
    return { status: result.status ?? 1, output: `${result.stdout ?? ''}${result.stderr ?? ''}` };
  };
  return { temp, repo, reset, check, runner };
}

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

test('actual frozen CLI protects protocol dependencies while permitting independent flight work', async t => {
  const fixture = createGuardFixture();
  const path = (relativePath: string) => resolve(fixture.repo, relativePath);
  const baseline = readFileSync(fixture.runner);
  const assertRejected = (result: ReturnType<typeof fixture.check>, reason: string, file?: string) => {
    assert.notEqual(result.status, 0, result.output || 'guard unexpectedly accepted the fixture');
    assert.match(result.output, new RegExp(reason));
    if (file) assert.ok(result.output.includes(file), result.output);
  };
  try {
    await t.test('unchanged dependency set passes', () => {
      const result = fixture.check();
      assert.equal(result.status, 0, result.output);
      assert.match(result.output, /FROZEN_PREFLIGHT_PASSED/);
    });
    await t.test('independent flight module and unrelated files pass', () => {
      appendFileSync(path('web/src/lib/engineeringFlight.ts'), '\n// independent engineering extension fixture\n');
      writeFileSync(path('NOTES.fixture.txt'), 'unrelated user note');
      const result = fixture.check();
      assert.equal(result.status, 0, result.output);
    });
    fixture.reset();
    await t.test('independent new flight source passes', () => {
      writeFileSync(path('web/src/lib/independentFlightController.ts'), 'export const controller = 1;\n');
      const result = fixture.check();
      assert.equal(result.status, 0, result.output);
    });
    fixture.reset();
    for (const relativePath of [
      'web/src/lib/interactiveNeuralLocomotion.ts',
      'web/src/lib/experimentalLocomotion.ts',
      'web/src/lib/causalContributionExperiment.ts',
      'web/src/assets/fly_visual_v2f.json',
      'docs/science/second_initial_condition_v10_6b_control_config.json',
    ]) {
      await t.test(`changed protected bytes fail for ${relativePath}`, () => {
        appendFileSync(path(relativePath), '\n/* integrity fixture mutation */\n');
        assertRejected(fixture.check(), 'differs from protocol bytes', relativePath);
      });
      fixture.reset();
    }
    await t.test('malformed visual manifest fails before acceptance', () => {
      writeFileSync(path('web/src/assets/fly_visual_v2f.json'), '{');
      assertRejected(fixture.check(), 'fly_visual_v2f\\.json');
    });
    fixture.reset();
    await t.test('deleted visual manifest fails before acceptance', () => {
      unlinkSync(path('web/src/assets/fly_visual_v2f.json'));
      assertRejected(fixture.check(), 'fly_visual_v2f\\.json');
    });
    fixture.reset();
    await t.test('staged source edit cannot be hidden by restoring working bytes', () => {
      const file = path('web/src/lib/causalContributionExperiment.ts');
      const original = readFileSync(file);
      appendFileSync(file, '\n/* staged integrity fixture */\n');
      execFileSync('git', ['add', '--', 'web/src/lib/causalContributionExperiment.ts'], { cwd: fixture.repo });
      writeFileSync(file, original);
      assertRejected(fixture.check(), 'differs in the Git index', 'web/src/lib/causalContributionExperiment.ts');
    });
    fixture.reset();
    await t.test('unstaged protected deletion fails', () => {
      unlinkSync(path('web/src/lib/neuralContributionComparison.ts'));
      assertRejected(fixture.check(), 'missing from the working tree', 'web/src/lib/neuralContributionComparison.ts');
    });
    fixture.reset();
    await t.test('new same-specifier source fails as a resolution ambiguity', () => {
      writeFileSync(path('web/src/lib/flyViewer.js'), 'export {};\n');
      assertRejected(fixture.check(), 'New source could shadow frozen import', 'web/src/lib/flyViewer.js');
    });
    fixture.reset();
    await t.test('new entrypoint shadow fails before the scientific module is loaded', () => {
      writeFileSync(path('web/src/lib/continuousArenaNavigation.js'), 'export {};\n');
      assertRejected(fixture.check(), 'New source could shadow frozen import', 'web/src/lib/continuousArenaNavigation.js');
    });
    fixture.reset();
    await t.test('independent flight edit cannot mask a protected change', () => {
      appendFileSync(path('web/src/lib/engineeringFlight.ts'), '\n// independent fixture\n');
      appendFileSync(path('web/src/lib/interactiveNeuralLocomotion.ts'), '\n// protected fixture\n');
      assertRejected(fixture.check(), 'differs from protocol bytes', 'web/src/lib/interactiveNeuralLocomotion.ts');
    });
    fixture.reset();
    await t.test('a substituted historical protocol identity is rejected', () => {
      const changed = readFileSync(fixture.runner, 'utf8').replace(PROTOCOL_COMMIT, '04ebca9e87b2edc0d842d9a9ee4a12bc53b88443');
      writeFileSync(fixture.runner, changed);
      assertRejected(fixture.check(), 'Unexpected protocol parent');
    });
    fixture.reset();
    await t.test('known resolution overrides fail with an actionable diagnostic', () => {
      assertRejected(fixture.check({ TSX_TSCONFIG_PATH: resolve(fixture.repo, 'web/tsconfig.json') }), 'Unsupported frozen-run resolution override.*TSX_TSCONFIG_PATH');
    });
    await t.test('NODE_PATH and NODE_OPTIONS loader hooks are rejected', () => {
      assertRejected(fixture.check({ NODE_PATH: resolve(fixture.repo, 'unused-node-path') }), 'Unsupported frozen-run resolution override.*NODE_PATH');
      assertRejected(fixture.check({ NODE_OPTIONS: '--require node:fs' }), 'Unsupported frozen-run resolution override.*loader hooks in NODE_OPTIONS');
    });
  } finally { rmSync(fixture.temp, { recursive: true, force: true }); }
  assert.equal(readFileSync(guardSource).equals(baseline), true);
});
