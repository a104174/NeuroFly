/** Explicit V10.6B-1 command only; importing this module never starts a run. */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { basename, dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ContinuousNavigationEngine, boundarySteering, navigationHash } from '../src/lib/continuousArenaNavigation';
import { generatePair, validatePair } from '../src/lib/neuralContributionComparison';
import { contributionReport } from '../src/lib/causalContributionExperiment';
import { locomotionBounds } from '../src/lib/experimentalLocomotion';
import { NEURAL_LOCOMOTION_SHA256, parseNeuralLocomotion, type NeuralArtifact } from '../src/lib/neuralLocomotion';
import type { Plane } from '../src/lib/interactiveNeuralLocomotion';

export const PROTOCOL_COMMIT = 'e8ed01f32d4651871d43c4105eb929317325e249';
export const CONFIG_SHA256 = 'dbc0f37db7a614c1a1076041f6319999bb86e7414b17a21992a8797e43f4a392';
export const CONFIG_PATH = 'docs/science/second_initial_condition_v10_6b_control_config.json';
const DOCUMENT = 'docs/science/second_initial_condition_v10_6b_protocol.md';
const ROOT = realpathSync(new URL('../../', import.meta.url));
const RUNTIME_HASH = 'c5edf9edb0b1f08a0eb3e36808dd6ec25771be1bc575ce07e9cc3063aa6586cf';
const MORPHOLOGY_HASH = 'c538f94a6a3ea02390bfcb09ee77226fe6f0418455c0794cdfedd64593070697';
export const sha256 = (bytes: string | Buffer) => createHash('sha256').update(bytes).digest('hex');
const git = (...args: string[]) => execFileSync('git', args, { cwd: ROOT });

type Pose = { position: [number, number, number]; heading: number };
/** Constructor-only validation: no sensory, neural or body integration. */
export async function validateControl(config: Record<string, unknown>, authority: NeuralArtifact) {
  if (config.runtime !== 'CONTINUOUS_ARENA_NAVIGATION_V3' || config.mode !== 'neural' || config.duration_s !== 30 || config.body_dt_s !== .02 || config.substeps !== 200 || config.neural_dt_ms !== .1 || config.random_policy !== 'NONE') throw new Error('Unsupported frozen runtime/configuration');
  const pose = config.initial_pose as Pose;
  if (!pose || !Array.isArray(pose.position) || pose.position.length !== 3 || ![...pose.position, pose.heading].every(v => typeof v === 'number' && Number.isFinite(v))) throw new Error('Invalid frozen pose');
  const limits = locomotionBounds(authority.config.body);
  const boundary = boundarySteering(pose.position[0], pose.position[2], pose.heading, limits);
  if (boundary.active || boundary.distances.some(d => d <= .06)) throw new Error('Initial pose inside wall margin');
  const control = new ContinuousNavigationEngine(authority, 'neural', config.initial_plane as Plane, structuredClone(pose));
  const intervention = new ContinuousNavigationEngine(authority, 'output_disabled', config.initial_plane as Plane, structuredClone(pose));
  if (await navigationHash(control.navigationLog().config) !== await navigationHash(config)) throw new Error('Runtime does not match complete frozen configuration');
  const off = intervention.navigationLog().config;
  if (await navigationHash(off) !== await navigationHash({ ...config, mode: 'output_disabled' })) throw new Error('Unmatched intervention configuration');
  const baseline = new ContinuousNavigationEngine(authority, 'neural').navigationLog().config;
  if (await navigationHash(config) !== await navigationHash({ ...baseline, initial_pose: pose })) throw new Error('Non-pose controls differ from V10.6A');
  if (control.snapshot().step !== 0 || control.snapshot().substeps !== 0 || intervention.snapshot().step !== 0) throw new Error('Premature execution');
  return { control, intervention_config: off };
}

export async function parseFrozen(text: string, authority: NeuralArtifact) {
  if (sha256(text) !== CONFIG_SHA256) throw new Error('Frozen configuration hash mismatch');
  const config = JSON.parse(text) as Record<string, unknown>;
  if (await navigationHash(config) !== CONFIG_SHA256) throw new Error('Non-canonical frozen serialization');
  return { config, ...await validateControl(config, authority) };
}

export async function prepareFrozen(read: (path: string) => Buffer = path => readFileSync(path)) {
  git('merge-base', '--is-ancestor', PROTOCOL_COMMIT, 'HEAD');
  if (git('rev-parse', `${PROTOCOL_COMMIT}^`).toString().trim() !== '04ebca9e87b2edc0d842d9a9ee4a12bc53b88443') throw new Error('Unexpected protocol parent');
  for (const path of [CONFIG_PATH, DOCUMENT]) {
    if (!read(resolve(ROOT, path)).equals(git('show', `${PROTOCOL_COMMIT}:${path}`))) throw new Error('Protocol differs from committed checkpoint');
  }
  // The experiment reuses exactly the runtime/replay/report sources locked before outcomes.
  if (git('diff', PROTOCOL_COMMIT, '--', 'web/src/lib', 'web/public/experiments/experimental_locomotion_v1.json').length) throw new Error('Scientific implementation changed since protocol lock');
  const protectedFiles: Record<string, string> = {};
  function verify(path: string, expected: string) {
    const actual = sha256(read(resolve(ROOT, path)));
    if (actual !== expected) throw new Error(`Protected source integrity: ${path}`);
    protectedFiles[path] = actual;
  }
  verify(`runtime-distributions/v3/neurofly-runtime-v3-${RUNTIME_HASH}.tar.gz`, RUNTIME_HASH);
  const morphology = 'web/public/assets/neural/malecns-v1.0/hs-dnp15/';
  verify(`${morphology}manifest.json`, MORPHOLOGY_HASH);
  const manifest = JSON.parse(read(resolve(ROOT, morphology, 'manifest.json')).toString('utf8'));
  if (manifest.bodies.length !== 8) throw new Error('Expected eight protected morphologies');
  for (const body of manifest.bodies) {
    if (body.morphology.path !== `${body.body_id}.swc`) throw new Error('Invalid morphology identity/path');
    verify(morphology + body.morphology.path, body.morphology.source_sha256);
  }
  const source = 'web/public/experiments/experimental_locomotion_v1.json';
  verify(source, NEURAL_LOCOMOTION_SHA256);
  const authority = parseNeuralLocomotion(JSON.parse(read(resolve(ROOT, source)).toString('utf8')));
  const prepared = await parseFrozen(read(resolve(ROOT, CONFIG_PATH)).toString('utf8'), authority);
  return { ...prepared, authority, provenance: {
    protocol_commit: PROTOCOL_COMMIT, config_sha256: CONFIG_SHA256, protocol_document_sha256: sha256(read(resolve(ROOT, DOCUMENT))),
    execution_source_commit: git('rev-parse', 'HEAD').toString().trim(),
    wrapper_sha256: sha256(readFileSync(fileURLToPath(import.meta.url))),
    node: process.version, platform: process.platform, architecture: process.arch,
    protected_files: protectedFiles, seed: null, random_policy: 'NONE',
  } };
}
export type Prepared = Awaited<ReturnType<typeof prepareFrozen>>;

/** Resolve the existing parent, including symlinks; reserve a NEW directory atomically. */
export function reserveOutput(destination: string) {
  const requested = resolve(destination);
  const parent = realpathSync(dirname(requested));
  const output = resolve(parent, basename(requested));
  const rel = relative(ROOT, output);
  if (!(rel === '..' || rel.startsWith('..' + sep) || isAbsolute(rel))) throw new Error('Output must be outside repository');
  if (existsSync(output)) throw new Error('Output already exists; evidence will not be overwritten');
  mkdirSync(output); // EEXIST also rejects races and dangling symlinks.
  return output;
}

export async function executePrepared(prepared: Prepared) {
  for (let n = 0; n < 1500; n++) prepared.control.advance();
  const parent = await prepared.control.exportNavigation();
  const pair = await generatePair(prepared.authority, parent, () => {}, async () => {});
  await validatePair(prepared.authority, pair);
  if (pair.config.duration_s !== 30 || parent.log.stop_step !== 1500 || parent.log.termination !== 'DURATION_COMPLETED' || pair.config.parent_config_sha256 !== CONFIG_SHA256 || pair.parent.log.events.length || pair.result.tracks.some(t => t.frames.length !== 1501 || t.final_state.step !== 1500 || t.final_state.substeps !== 300000)) throw new Error('Incomplete or mismatched frozen result');
  const report = { ...contributionReport(pair), experiment: 'V10.6B', protocol: prepared.provenance, validation: 'validatePair:PASS' };
  // Existing pair validator checks semantic replay and finite telemetry. Reject any additional report non-finites.
  await navigationHash(report);
  return { pair, report };
}

/** Test seam replaces execution only, never preflight checks. No integration before reservation. */
export async function runFrozen(destination: string, execute = executePrepared) {
  const prepared = await prepareFrozen();
  const output = reserveOutput(destination);
  const write = (name: string, value: unknown) => writeFileSync(resolve(output, name), JSON.stringify(value), { flag: 'wx' });
  write('provenance.json', { ...prepared.provenance, status: 'PREFLIGHT_PASSED_NOT_YET_ACCEPTED' });
  try {
    const { pair, report } = await execute(prepared);
    write('pair.json', pair);
    write('report.json', report);
    const checksums = Object.fromEntries(['provenance.json', 'pair.json', 'report.json'].map(name => [name, sha256(readFileSync(resolve(output, name)))]));
    write('checksums.json', { status: 'ACCEPTED', files: checksums });
    return { output, artifact_id: pair.artifact_id, checksums, metrics: report.metrics, tracks: report.tracks.map(({ intervals, ...t }) => ({ ...t, interval_count: intervals.length })) };
  } catch (error) {
    write('failure.json', { status: 'FAILED_NOT_ACCEPTED', error: String(error) });
    throw error;
  }
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [output, ...extra] = process.argv.slice(2);
  if (!output || extra.length) throw new Error('Usage: node --import tsx scripts/frozen-contribution.ts NEW_EXTERNAL_DIRECTORY');
  console.log(JSON.stringify(await runFrozen(output), null, 2));
}
