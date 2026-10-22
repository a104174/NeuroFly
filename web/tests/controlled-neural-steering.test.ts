import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync, writeFileSync, mkdtempSync, rmSync, cpSync, mkdirSync, symlinkSync, existsSync, readdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';
import { FlightEngine, createFlightTrial, exportFlight, flightCanonical, flightHash } from '../src/lib/engineeringFlight';
import { FlightPoseNeuralAdapter, NeuralFlightEngine, projectFlightYaw } from '../src/lib/neuralFlight';
import { InteractiveNeuralEngine } from '../src/lib/interactiveNeuralLocomotion';
import { conditionSpecs, experimentProtocol, visualScene, observerProbe, executeCondition, runControlledExperiment, verifyControlledExperiment, hypothesisOutcomes, type ControlledArtifact } from '../src/lib/controlledNeuralSteering';

const authority = parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8')));
const artifact = await runControlledExperiment(authority);
const runs = artifact.result.conditions;
const near = (a: number, b: number, tolerance = 1e-9) => assert.ok(Math.abs(a - b) <= tolerance, `${a} != ${b}`);

test('preregistered mirror is supported scene-only Z reflection; X symmetric reflection is degenerate', () => {
  const before = structuredClone(authority), v0 = visualScene('V0'), v1 = visualScene('V1');
  assert.deepEqual(v1.landmarks, v0.landmarks.map(l => ({ ...l, z: -l.z })));
  assert.deepEqual(v0.landmarks.map(l => ({ x: -l.x, z: l.z })).reverse(), v0.landmarks.map(l => ({ x: l.x, z: l.z })));
  assert.equal(v1.body_pose, 'UNCHANGED'); assert.equal(v1.collision_geometry, 'UNCHANGED');
  assert.throws(() => visualScene('INVERT_INPUTS' as 'V1'));
  assert.throws(() => executeCondition(authority, 'E7'));
  assert.deepEqual(authority, before);
  const protocol = experimentProtocol(authority); protocol.visuals[0].landmarks[0].x = 9;
  assert.equal(experimentProtocol(authority).visuals[0].landmarks[0].x, .6);
  assert.equal(experimentProtocol(authority).classification, 'CONTROLLED_VISUAL_MIRROR');
});

test('open-loop observer reversal is exact for lateral diagnostic; yaw is equal, not inverted', () => {
  const probes = observerProbe(authority);
  assert.deepEqual(probes, observerProbe(authority));
  for (const p of probes) for (const row of p.rows) {
    if (row.step === 0) { assert.deepEqual(row.observations, [null, null]); continue; }
    const [v0, v1] = row.observations;
    assert.ok(v0 && v1);
    assert.equal(v0.available_step, row.step); assert.equal(v0.before_step, row.step - 1);
    assert.deepEqual(v0.clipped, [false, false]); assert.deepEqual(v1.clipped, [false, false]);
    if (p.kind === 'STATIC') assert.ok([v0.right, v0.left, v1.right, v1.left].every(n => n === 0));
    if (p.kind === 'LATERAL') { assert.equal(v0.right, -v1.right); assert.equal(v0.left, -v1.left); assert.ok(v0.right < 0 && v0.left > 0); }
    if (p.kind === 'YAW') { near(v0.right, -50 * .01 / (2 * Math.PI * 20), 1e-14); assert.equal(flightCanonical(v0), flightCanonical(v1)); }
    if (p.kind === 'MIXED') { assert.equal(row.relation, 'NO_GLOBAL_SIGN_EXPECTATION'); assert.ok(Math.abs(v0.right + v1.right) > 1e-5); }
  }
});

test('frozen actual solver and projection reused, original scene/plant/configuration unchanged', () => {
  assert.equal(FlightPoseNeuralAdapter.prototype['observation'], InteractiveNeuralEngine.prototype['observation']);
  assert.equal(FlightPoseNeuralAdapter.prototype['calculateBoundary'], InteractiveNeuralEngine.prototype['calculateBoundary']);
  for (const [i, c] of runs.entries()) {
    assert.deepEqual({ id: c.id, mode: c.mode, visual: c.visual }, conditionSpecs()[i]);
    assert.equal(c.frames.length, 601); assert.equal(c.intervals.length, 600);
    assert.deepEqual(c.frames[0], createFlightTrial().initial);
    assert.deepEqual(c.intervals[0].before.hs_states, [0, 0, 0, 0, 0, 0]);
    assert.deepEqual(c.intervals[0].before.dnp15_states, [0, 0]);
    assert.equal(c.intervals.at(-1)!.after.substeps, 120000);
    assert.equal(c.summary.neural.total_substeps, 120000);
  }
  const invalid = structuredClone(authority); invalid.config.dataset_uuid = 'false';
  assert.throws(() => experimentProtocol(invalid));
});

test('four controls equal all legacy body boundaries and exact original v8 hashes', async () => {
  const legacy = new FlightEngine(createFlightTrial()); while (legacy.snapshot().step < 600) legacy.advance();
  for (const i of [0, 1, 3, 4]) assert.deepEqual(runs[i].frames, legacy.frames());
  assert.deepEqual(runs[0].intervals, runs[1].intervals);
  assert.deepEqual(runs[3].intervals, runs[4].intervals);
  assert.notDeepEqual(runs[0].intervals, runs[3].intervals); // visuals alter model, not plant
  const old = await exportFlight(legacy, 'normal');
  assert.equal(old.input_sha256, '25af17966a60f9ed17267d6143cac86b783fd370ca09fef33ee49313177c9f61');
  assert.equal(old.result_sha256, '8c8fc14e028a40fbc1aea526f253306bafc827b858a52495f0751168655528b7');
});

test('new composition equals original v9 ON and existing visual perturbation exactly', () => {
  for (const [i, name] of [[2, 'ON'], [5, 'VISUAL_PERTURBATION']] as const) {
    const old = new NeuralFlightEngine(authority, name); while (old.snapshot().step < 600) old.advance();
    assert.deepEqual(runs[i].frames, old.frames());
    const row = runs[i].intervals[312], raw = old.interval(312);
    near(row.before.mean_yaw_drive_eq!, raw.before.mean_yaw_drive_eq!, 5.1e-11);
  }
});

test('each interval causally uses its own accepted poses, persistent model state and unchanged commands', () => {
  for (const c of runs) {
    const adapter = new FlightPoseNeuralAdapter(authority, c.scene.plane_z);
    for (let i = 0; i < 600; i++) {
      const row = c.intervals[i], frame = c.frames[i], next = c.frames[i + 1];
      const model = adapter.observeAndAdvance(frame, i ? c.frames[i - 1] : undefined);
      if (model.observation) {
        near(row.observation!.right, model.observation.right, 5.1e-11);
        near(row.observation!.left, model.observation.left, 5.1e-11);
      } else assert.equal(row.observation, null);
      const yaw = projectFlightYaw(model.before.orientation_increment_eq!, row.engineering.turn, c.mode === 'ZERO_PROJECTION' ? 'ZERO' : c.mode);
      near(row.yaw.appliedTurn, yaw.appliedTurn, 5.1e-11);
      if (i) row.before.hs_states.forEach((n, j) => assert.equal(n, c.intervals[i - 1].after.hs[j]));
      assert.equal(row.after.substeps, (i + 1) * 200);
      const held = createFlightTrial().commands.findLast(x => x.step <= i);
      assert.equal(row.engineering.forward, held?.forward ?? 0); assert.equal(row.engineering.vertical, held?.vertical ?? 0); assert.equal(row.engineering.turn, held?.turn ?? 0);
      assert.equal(row.engineering.intent, held?.step === i ? held.intent : 'HOLD');
      // Plant yaw is disabled grounded/landing; check the independent one-step rule.
      const turns = next.state !== 'grounded' && next.state !== 'landing';
      const expected = turns && yaw.appliedTurn ? Math.round((frame.heading + yaw.appliedTurn * .8 * .02) * 1e12) / 1e12 : frame.heading;
      assert.equal(next.heading, expected);
      near(row.heading_delta, next.heading - frame.heading, 5.1e-11);
    }
  }
  assert.notDeepEqual(runs[2].intervals[312].observation, runs[0].intervals[312].observation);
  assert.notDeepEqual(runs[5].intervals[312].observation, runs[3].intervals[312].observation);
});

test('metrics use authoritative body values, predefined interaction and saturation accounting', () => {
  const m = artifact.result.comparisons;
  const h = runs.map(c => c.frames[600].heading);
  assert.equal(m.final_heading_interaction, (h[5] - h[3]) - (h[2] - h[0]));
  assert.equal(m.ON_visual_comparison.final_xyz_separation, Math.hypot(...runs[5].frames[600].position.map((n, i) => n - runs[2].frames[600].position[i])));
  for (const c of runs) {
    const s = c.summary.neural.saturation;
    assert.equal(s.visual.count, c.intervals.filter(r => r.observation?.clipped.some(Boolean)).length);
    assert.equal(s.projection_potential.count, c.intervals.filter(r => r.yaw.projectionClamped).length);
    assert.equal(s.projection_applied.count, c.mode === 'ON' ? s.projection_potential.count : 0);
    near(s.projection_potential.fraction, s.projection_potential.count / 600, 5.1e-11);
    near(c.summary.neural.integrated_absolute_applied_neural_omega, c.intervals.reduce((sum, r) => sum + Math.abs(r.yaw.neuralTurn) * .8 * .02, 0), 1e-9);
    assert.deepEqual(c.summary.final, c.frames[600]);
    assert.deepEqual(c.summary.contacts, c.frames.flatMap(f => f.events.filter(e => e.kind === 'CONTACT')));
    assert.equal(c.summary.grounded, true);
  }
});

test('independent Python observer/neural reference checks all six own-pose histories, not body parity', () => {
  const p = spawnSync('../.venv/bin/python', ['-B', '-m', 'neurofly.neural_flight_reference'], {
    input: JSON.stringify({ schema: 'neural_flight_reference_input_v9', runs: [] }), encoding: 'utf8', env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  assert.notEqual(p.status, 0); // existing harness permits at most four histories per request
  let maxError = 0;
  for (const batch of [runs.slice(0, 3), runs.slice(3)]) {
    const child = spawnSync('../.venv/bin/python', ['-B', '-m', 'neurofly.neural_flight_reference'], {
      input: JSON.stringify({ schema: 'neural_flight_reference_input_v9', runs: batch.map(c => ({ frames: c.frames, plane: c.scene.plane_z })) }),
      encoding: 'utf8', maxBuffer: 15_000_000, env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
    });
    assert.equal(child.status, 0, child.stderr);
    const outputs = JSON.parse(child.stdout);
    outputs.forEach((out: { records: { observation: { right: number; left: number } | null; hs_after: number[]; dn_after: number[]; orientation_increment_eq: number; mean_yaw_drive_eq: number }[]; flight_parity: string }, j: number) => {
      assert.equal(out.flight_parity, 'NOT_CLAIMED_PYTHON_NEURAL_AND_OBSERVER_ONLY');
      out.records.forEach((r, i) => {
        const row = batch[j].intervals[i];
        const pairs = [[row.before.orientation_increment_eq!, r.orientation_increment_eq], [row.before.mean_yaw_drive_eq!, r.mean_yaw_drive_eq], ...row.after.hs.map((n, k) => [n, r.hs_after[k]]), ...row.after.dn.map((n, k) => [n, r.dn_after[k]])];
        if (r.observation) pairs.push([row.observation!.right, r.observation.right], [row.observation!.left, r.observation.left]);
        for (const [a, b] of pairs) { maxError = Math.max(maxError, Math.abs(a - b)); near(a, b, 5.1e-11); }
      });
    });
  }
  console.log('Controlled six-history serialized Python neural/observer max error:', maxError);
});

test('deterministic full reconstruction, roundtrip and read-only recorded seeks', async () => {
  const again = await runControlledExperiment(authority);
  assert.equal(flightCanonical(again), flightCanonical(artifact));
  assert.equal((await verifyControlledExperiment(authority, JSON.parse(JSON.stringify(artifact)))).artifact_id, artifact.artifact_id);
  const before = flightCanonical(artifact); runs[2].frames.at(0); runs[2].frames.at(600); runs[2].intervals.at(50);
  assert.equal(flightCanonical(artifact), before);
});

test('semantic tampering is rejected even after all superficial hashes are recomputed', async () => {
  const mutations: ((x: ControlledArtifact) => void)[] = [
    x => { x.input.protocol.timebase.substeps = 199; },
    x => { x.input.protocol.visuals[1].plane_z = .4; },
    x => { x.input.protocol.reference.trial.initial.heading = 0; },
    x => { x.input.protocol.reference.trial.commands[2].turn = .3; },
    x => { x.result.conditions[5].mode = 'OFF'; },
    x => { x.result.conditions[0].id = 'E6'; },
    x => { x.result.conditions[2].frames.pop(); },
    x => { x.result.conditions[2].intervals[200].after.hs[0] += .01; },
    x => { x.result.conditions[5].frames[400].position[0] += .01; },
    x => { x.result.comparisons.final_heading_interaction += .01; },
    x => { x.result.conditions[0].summary.neural.saturation.visual.count = 1; },
  ];
  for (const mutate of mutations) {
    const x = structuredClone(artifact); mutate(x);
    x.input_sha256 = await flightHash(x.input); x.result_sha256 = await flightHash(x.result); x.artifact_id = await flightHash({ input_sha256: x.input_sha256, result_sha256: x.result_sha256 });
    await assert.rejects(verifyControlledExperiment(authority, x));
  }
  await assert.rejects(verifyControlledExperiment(authority, { schema: 'v0' }));
  const invalid = structuredClone(artifact); invalid.result.conditions[0].frames[1].heading = NaN;
  await assert.rejects(verifyControlledExperiment(authority, invalid));
  const wrongHash = structuredClone(artifact); wrongHash.result_sha256 = 'false';
  await assert.rejects(verifyControlledExperiment(authority, wrongHash));
});

test('scientifically negative response is a valid outcome and never becomes biological calibration', () => {
  const outcome = hypothesisOutcomes(0, 0, 0);
  assert.equal(outcome.H0, 'SUPPORTED'); assert.equal(outcome.H2, 'UNCHANGED'); assert.equal(outcome.H3, 'UNCHANGED');
  assert.throws(() => hypothesisOutcomes(NaN, 0, 0));
  assert.equal(artifact.result.scientific_status, 'INTERNAL_MODEL_EXPERIMENT_NOT_EMPIRICAL_VALIDATION');
  assert.ok(experimentProtocol(authority).limitation.includes('no G3 stimulus reproduction'));
});

test('offline CLI rejects repository paths, overwrite, malformed input and unsupported arguments', () => {
  const directory = mkdtempSync(join(tmpdir(), 'neurofly-controlled-v93-'));
  const cli = (...args: string[]) => spawnSync(process.execPath, ['--import', 'tsx', 'tools/controlledNeuralSteering.ts', ...args], { encoding: 'utf8', env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' } });
  try {
    assert.notEqual(cli('--unknown', 'value').status, 0);
    const inside = cli('--output', '../..not-an-external-directory.json');
    assert.notEqual(inside.status, 0); assert.ok(inside.stderr.includes('outside the repository'));
    const existing = join(directory, 'existing.json'); writeFileSync(existing, 'retained');
    assert.notEqual(cli('--output', existing).status, 0); assert.equal(readFileSync(existing, 'utf8'), 'retained');
    assert.notEqual(cli('--verify', existing).status, 0);
    const valid = join(directory, 'valid.json'); writeFileSync(valid, JSON.stringify(artifact));
    const verified = cli('--verify', valid); assert.equal(verified.status, 0, verified.stderr);
    assert.equal(JSON.parse(verified.stdout).artifact_id, artifact.artifact_id);
  } finally { rmSync(directory, { recursive: true }); }
});

test('CLI canonical containment protects both outputs in a disposable checkout', async t => {
  const directory = mkdtempSync(join(tmpdir(), 'neurofly-cli-containment-'));
  const checkout = join(directory, 'checkout'), web = join(checkout, 'web');
  mkdirSync(join(web, 'tools'), { recursive: true });
  mkdirSync(join(web, 'public', 'experiments'), { recursive: true });
  cpSync(new URL('../tools/controlledNeuralSteering.ts', import.meta.url), join(web, 'tools', 'controlledNeuralSteering.ts'));
  cpSync(new URL('../src/lib', import.meta.url), join(web, 'src', 'lib'), { recursive: true });
  cpSync(new URL('../package.json', import.meta.url), join(web, 'package.json'));
  cpSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), join(web, 'public', 'experiments', 'experimental_locomotion_v1.json'));
  symlinkSync(new URL('../node_modules', import.meta.url), join(web, 'node_modules'), 'dir');
  const cli = (...args: string[]) => spawnSync(process.execPath, ['--import', 'tsx', join(web, 'tools', 'controlledNeuralSteering.ts'), ...args], {
    encoding: 'utf8', env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  const noOutput = (path: string) => {
    assert.equal(existsSync(path), false);
    assert.equal(existsSync(path + '.summary.json'), false);
  };
  const reject = (path: string) => assert.notEqual(cli('--output', path).status, 0);
  try {
    const valid = join(directory, 'external.json');
    await t.test('T1/T9 legitimate external output and semantic verification remain valid', () => {
      const result = cli('--output', valid); assert.equal(result.status, 0, result.stderr);
      assert.equal(JSON.parse(readFileSync(valid, 'utf8')).artifact_id, artifact.artifact_id);
      assert.equal(JSON.parse(readFileSync(valid + '.summary.json', 'utf8')).artifact_id, artifact.artifact_id);
      const verified = cli('--verify', valid); assert.equal(verified.status, 0, verified.stderr);
      assert.equal(JSON.parse(verified.stdout).artifact_id, artifact.artifact_id);
    });
    await t.test('T2 direct internal path and exact repository root are rejected without writes', () => {
      const path = join(checkout, 'direct.json'); reject(path); noOutput(path);
      reject(checkout); assert.equal(existsSync(checkout + '.summary.json'), false);
    });
    await t.test('T3 external parent symlink into checkout is rejected without writes', () => {
      const alias = join(directory, 'alias'); symlinkSync(checkout, alias, 'dir');
      reject(join(alias, 'parent-link.json')); noOutput(join(checkout, 'parent-link.json'));
    });
    await t.test('T4 nested symlinked ancestor is rejected without writes', () => {
      mkdirSync(join(checkout, 'nested')); mkdirSync(join(directory, 'outside'));
      symlinkSync(checkout, join(directory, 'outside', 'ancestor'), 'dir');
      reject(join(directory, 'outside', 'ancestor', 'nested', 'nested-link.json'));
      assert.deepEqual(readdirSync(join(checkout, 'nested')), []);
    });
    await t.test('T5 existing final symlink into checkout preserves the target', () => {
      const target = join(checkout, 'sentinel'); writeFileSync(target, 'retained');
      const output = join(directory, 'final-link.json'); symlinkSync(target, output);
      reject(output); assert.equal(readFileSync(target, 'utf8'), 'retained');
      assert.equal(existsSync(output + '.summary.json'), false);
    });
    await t.test('T6 summary symlink is checked before main output is written', () => {
      const target = join(checkout, 'summary-sentinel'); writeFileSync(target, 'retained-summary');
      const output = join(directory, 'summary-link.json'); symlinkSync(target, output + '.summary.json');
      reject(output); assert.equal(existsSync(output), false);
      assert.equal(readFileSync(target, 'utf8'), 'retained-summary');
    });
    await t.test('T7 similar-prefix external sibling remains writable', () => {
      const sibling = checkout + '-sibling'; mkdirSync(sibling);
      const output = join(sibling, 'allowed.json'), result = cli('--output', output);
      assert.equal(result.status, 0, result.stderr);
      assert.equal(JSON.parse(readFileSync(output, 'utf8')).artifact_id, artifact.artifact_id);
      assert.equal(existsSync(output + '.summary.json'), true);
    });
    await t.test('T8 existing companion causes rejection without partial main output', () => {
      const output = join(directory, 'occupied-summary.json'); writeFileSync(output + '.summary.json', 'retained');
      reject(output); assert.equal(existsSync(output), false);
      assert.equal(readFileSync(output + '.summary.json', 'utf8'), 'retained');
    });
    await t.test('missing parents and dangling final symlinks are rejected without creating outputs', () => {
      const absent = join(directory, 'absent'); reject(join(absent, 'nested', 'output.json'));
      assert.equal(existsSync(absent), false);
      const output = join(directory, 'dangling.json'), target = join(checkout, 'absent-target');
      symlinkSync(target, output); reject(output); noOutput(target);
      assert.equal(existsSync(output + '.summary.json'), false);
    });
  } finally { rmSync(directory, { recursive: true }); }
});
