/** Explicit V10.6B-1 command only; importing this module never starts a run. */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { basename, dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';
import type { Plane } from '../src/lib/interactiveNeuralLocomotion';

export const PROTOCOL_COMMIT = 'e8ed01f32d4651871d43c4105eb929317325e249';
export const CONFIG_SHA256 = 'dbc0f37db7a614c1a1076041f6319999bb86e7414b17a21992a8797e43f4a392';
export const CONFIG_PATH = 'docs/science/second_initial_condition_v10_6b_control_config.json';
const DOCUMENT = 'docs/science/second_initial_condition_v10_6b_protocol.md';
const ROOT = realpathSync(new URL('../../', import.meta.url));
const RUNTIME_HASH = 'c5edf9edb0b1f08a0eb3e36808dd6ec25771be1bc575ce07e9cc3063aa6586cf';
const MORPHOLOGY_HASH = 'c538f94a6a3ea02390bfcb09ee77226fe6f0418455c0794cdfedd64593070697';
const VISUAL_MANIFEST = 'web/src/assets/fly_visual_v2f.json';
const VISUAL_MANIFEST_SHA256 = '6a3d05441afd0c25ed8c2a98472acc35601f6e525db6f74d4eb16b0e32ab3b9e';

/** Runtime-local V10.6B closure traced from this post-protocol wrapper.
 * engineeringFlight.ts is intentionally absent: no runtime import reaches it.
 */
const FROZEN_RUNTIME_SOURCES = [
  'web/src/lib/continuousArenaNavigation.ts',
  'web/src/lib/interactiveNeuralLocomotion.ts',
  'web/src/lib/neuralContributionComparison.ts',
  'web/src/lib/causalContributionExperiment.ts',
  'web/src/lib/experimentalLocomotion.ts',
  'web/src/lib/neuralLocomotion.ts',
  'web/src/lib/neuralSteeringComparison.ts',
  'web/src/lib/experimentalArena.ts',
  'web/src/lib/flyViewer.ts',
  'web/src/lib/flyVisualAssetV2.ts',
  'web/src/lib/flyVisualInstance.ts',
  'web/src/lib/flyVisualNodeIdentity.ts',
] as const;
const FROZEN_ENTRY_IMPORTS = [
  ['../src/lib/continuousArenaNavigation', 'web/src/lib/continuousArenaNavigation.ts'],
  ['../src/lib/neuralContributionComparison', 'web/src/lib/neuralContributionComparison.ts'],
  ['../src/lib/causalContributionExperiment', 'web/src/lib/causalContributionExperiment.ts'],
  ['../src/lib/experimentalLocomotion', 'web/src/lib/experimentalLocomotion.ts'],
  ['../src/lib/neuralLocomotion', 'web/src/lib/neuralLocomotion.ts'],
] as const;
const FROZEN_REFERENCE_FILES = [
  ...FROZEN_RUNTIME_SOURCES,
  VISUAL_MANIFEST,
  'web/package.json',
  'web/package-lock.json',
  'web/tsconfig.json',
  CONFIG_PATH,
  DOCUMENT,
  'web/public/experiments/experimental_locomotion_v1.json',
] as const;

export const sha256 = (bytes: string | Buffer) => createHash('sha256').update(bytes).digest('hex');
const git = (...args: string[]) => execFileSync('git', args, { cwd: ROOT, maxBuffer: 32 * 1024 * 1024 });

function verifyResolutionEnvironment() {
  const unsupported: string[] = [];
  if (process.env.TSX_TSCONFIG_PATH) unsupported.push('TSX_TSCONFIG_PATH');
  if (process.env.NODE_PATH) unsupported.push('NODE_PATH');
  if (/(^|\s)(?:--(?:import|loader|experimental-loader|require)(?:=|\s)|-r(?:=|\s))/.test(process.env.NODE_OPTIONS ?? '')) unsupported.push('loader hooks in NODE_OPTIONS');
  if (unsupported.length) throw new Error(`Unsupported frozen-run resolution override: ${unsupported.join(', ')}`);
}

function historicalFile(path: string) {
  try { return git('show', `${PROTOCOL_COMMIT}:${path}`); }
  catch { throw new Error(`Frozen protocol reference is missing: ${path}`); }
}

function optionalHistoricalFile(path: string) {
  try { return historicalFile(path); }
  catch { return undefined; }
}

function indexFile(path: string) {
  try { return git('show', `:${path}`); }
  catch { throw new Error(`Frozen dependency is deleted from the Git index: ${path}`); }
}

function verifyReferenceFile(path: string, read: (path: string) => Buffer, expectedHash?: string) {
  const reference = historicalFile(path);
  const referenceHash = sha256(reference);
  if (expectedHash && referenceHash !== expectedHash) throw new Error(`Frozen historical reference hash mismatch: ${path}`);
  if (!indexFile(path).equals(reference)) throw new Error(`Frozen dependency differs in the Git index: ${path}`);
  let current: Buffer;
  try { current = read(resolve(ROOT, path)); }
  catch { throw new Error(`Frozen dependency is missing from the working tree: ${path}`); }
  if (!current.equals(reference)) throw new Error(`Frozen dependency differs from protocol bytes: ${path}`);
  return referenceHash;
}

const SOURCE_EXTENSIONS = ['.ts', '.tsx', '.js', '.jsx', '.mts', '.cts', '.mjs', '.cjs', '.json'];
type NeuralArtifact = import('../src/lib/neuralLocomotion').NeuralArtifact;

function hasSyntaxErrors(text: string, fileName: string) {
  const result = ts.transpileModule(text, {
    fileName,
    reportDiagnostics: true,
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext },
  });
  return result.diagnostics?.some(diagnostic => diagnostic.category === ts.DiagnosticCategory.Error) ?? false;
}

async function loadFrozenModules() {
  const [navigation, comparison, report, locomotion, neural] = await Promise.all([
    import('../src/lib/continuousArenaNavigation'),
    import('../src/lib/neuralContributionComparison'),
    import('../src/lib/causalContributionExperiment'),
    import('../src/lib/experimentalLocomotion'),
    import('../src/lib/neuralLocomotion'),
  ]);
  return { navigation, comparison, report, locomotion, neural };
}

function frozenCompilerOptions() {
  const configPath = resolve(ROOT, 'web/tsconfig.json');
  const configRead = ts.readConfigFile(configPath, ts.sys.readFile);
  if (configRead.error) throw new Error('Cannot read frozen TypeScript resolution config');
  const parsed = ts.parseJsonConfigFileContent(configRead.config, ts.sys, dirname(configPath));
  if (parsed.errors.length) throw new Error('Cannot resolve frozen imports from web/tsconfig.json');
  return parsed.options;
}

function rejectNewShadowCandidates(specifier: string, expected: string, importedFrom: string) {
  if (/[./](?:[cm]?[jt]sx?|json)$/.test(specifier)) return;
  const extension = SOURCE_EXTENSIONS.find(ext => expected.endsWith(ext));
  if (!extension) return;
  const stem = expected.slice(0, -extension.length);
  const candidates = [...SOURCE_EXTENSIONS.map(ext => `${stem}${ext}`), ...SOURCE_EXTENSIONS.map(ext => `${stem}/index${ext}`)];
  for (const candidate of candidates) {
    if (candidate === expected || !existsSync(resolve(ROOT, candidate))) continue;
    const reference = optionalHistoricalFile(candidate);
    if (!reference) throw new Error(`New source could shadow frozen import ${specifier} from ${importedFrom}: ${candidate}`);
    if (!indexFile(candidate).equals(reference) || !readFileSync(resolve(ROOT, candidate)).equals(reference)) {
      throw new Error(`Changed source could shadow frozen import ${specifier} from ${importedFrom}: ${candidate}`);
    }
  }
}

function verifyRunnerImports(read: (path: string) => Buffer, compilerOptions: ts.CompilerOptions) {
  const path = 'web/scripts/frozen-contribution.ts';
  const text = read(resolve(ROOT, path)).toString('utf8');
  if (hasSyntaxErrors(text, path)) throw new Error(`Malformed frozen runner: ${path}`);
  const source = ts.createSourceFile(path, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
  const actual: string[] = [];
  const visit = (node: ts.Node) => {
    if (ts.isImportDeclaration(node) && ts.isStringLiteral(node.moduleSpecifier) && isRuntimeImportClause(node.importClause) && node.moduleSpecifier.text.startsWith('../src/lib/')) {
      throw new Error(`Frozen runner must load scientific modules after preflight: ${node.moduleSpecifier.text}`);
    }
    if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword) {
      const argument = node.arguments[0];
      if (!argument || !ts.isStringLiteral(argument)) throw new Error('Frozen runner contains a non-literal dynamic import');
      if (argument.text.startsWith('../src/lib/')) actual.push(argument.text);
    }
    ts.forEachChild(node, visit);
  };
  visit(source);
  const expected = FROZEN_ENTRY_IMPORTS.map(([specifier]) => specifier);
  if (JSON.stringify([...actual].sort()) !== JSON.stringify([...expected].sort())) {
    throw new Error('Frozen runner scientific entry imports differ from the reviewed dependency boundary');
  }
  for (const [specifier, expectedPath] of FROZEN_ENTRY_IMPORTS) {
    const resolved = ts.resolveModuleName(specifier, resolve(ROOT, path), compilerOptions, ts.sys).resolvedModule;
    if (!resolved || relative(ROOT, resolve(resolved.resolvedFileName)).split(sep).join('/') !== expectedPath) {
      throw new Error(`Frozen runner import resolution differs from the reviewed dependency boundary: ${specifier}`);
    }
    rejectNewShadowCandidates(specifier, expectedPath, path);
  }
}

function isRuntimeImportClause(clause: ts.ImportClause | undefined) {
  if (!clause) return true;
  if (clause.isTypeOnly) return false;
  if (!clause.namedBindings) return true;
  if (ts.isNamespaceImport(clause.namedBindings)) return true;
  return clause.namedBindings.elements.some(element => !element.isTypeOnly);
}

/** Resolve the pinned runtime imports with the repository's TS config. The
 * closure is explicit; new local imports and newly added shadow candidates fail.
 */
function verifyFrozenImportResolution(read: (path: string) => Buffer, compilerOptions: ts.CompilerOptions) {
  const expectedLocal = new Set<string>([...FROZEN_RUNTIME_SOURCES, VISUAL_MANIFEST]);
  for (const path of FROZEN_RUNTIME_SOURCES) {
    const absolute = resolve(ROOT, path);
    let text: string;
    try { text = read(absolute).toString('utf8'); }
    catch { throw new Error(`Frozen source cannot be inspected for imports: ${path}`); }
    if (hasSyntaxErrors(text, path)) throw new Error(`Malformed frozen TypeScript source: ${path}`);
    const source = ts.createSourceFile(path, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
    const imports: { specifier: string; kind: 'static' | 'dynamic' }[] = [];
    const visit = (node: ts.Node) => {
      if (ts.isImportDeclaration(node) && ts.isStringLiteral(node.moduleSpecifier) && isRuntimeImportClause(node.importClause)) {
        imports.push({ specifier: node.moduleSpecifier.text, kind: 'static' });
      } else if (ts.isExportDeclaration(node) && node.moduleSpecifier && ts.isStringLiteral(node.moduleSpecifier) && !node.isTypeOnly) {
        imports.push({ specifier: node.moduleSpecifier.text, kind: 'static' });
      } else if (ts.isCallExpression(node) && (node.expression.kind === ts.SyntaxKind.ImportKeyword || (ts.isIdentifier(node.expression) && node.expression.text === 'require'))) {
        const argument = node.arguments[0];
        if (!argument || !ts.isStringLiteral(argument)) throw new Error(`Non-literal dynamic dependency in frozen source: ${path}`);
        imports.push({ specifier: argument.text, kind: 'dynamic' });
      }
      ts.forEachChild(node, visit);
    };
    visit(source);
    for (const { specifier } of imports) {
      if (!specifier.startsWith('.') && !specifier.startsWith('@/')) continue;
      const resolved = ts.resolveModuleName(specifier, absolute, compilerOptions, ts.sys).resolvedModule;
      if (!resolved) throw new Error(`Unresolved frozen import ${specifier} from ${path}`);
      const target = resolve(resolved.resolvedFileName);
      const relativeTarget = relative(ROOT, target).split(sep).join('/');
      if (relativeTarget.startsWith('web/src/') && !expectedLocal.has(relativeTarget)) {
        throw new Error(`Frozen dependency closure is incomplete: ${path} imports ${relativeTarget}`);
      }
      if (expectedLocal.has(relativeTarget)) rejectNewShadowCandidates(specifier, relativeTarget, path);
    }
  }
}

type Pose = { position: [number, number, number]; heading: number };
/** Constructor-only validation: no sensory, neural or body integration. */
export async function validateControl(config: Record<string, unknown>, authority: NeuralArtifact) {
  const { navigation, locomotion } = await loadFrozenModules();
  if (config.runtime !== 'CONTINUOUS_ARENA_NAVIGATION_V3' || config.mode !== 'neural' || config.duration_s !== 30 || config.body_dt_s !== .02 || config.substeps !== 200 || config.neural_dt_ms !== .1 || config.random_policy !== 'NONE') throw new Error('Unsupported frozen runtime/configuration');
  const pose = config.initial_pose as Pose;
  if (!pose || !Array.isArray(pose.position) || pose.position.length !== 3 || ![...pose.position, pose.heading].every(v => typeof v === 'number' && Number.isFinite(v))) throw new Error('Invalid frozen pose');
  const limits = locomotion.locomotionBounds(authority.config.body);
  const boundary = navigation.boundarySteering(pose.position[0], pose.position[2], pose.heading, limits);
  if (boundary.active || boundary.distances.some(d => d <= .06)) throw new Error('Initial pose inside wall margin');
  const control = new navigation.ContinuousNavigationEngine(authority, 'neural', config.initial_plane as Plane, structuredClone(pose));
  const intervention = new navigation.ContinuousNavigationEngine(authority, 'output_disabled', config.initial_plane as Plane, structuredClone(pose));
  if (await navigation.navigationHash(control.navigationLog().config) !== await navigation.navigationHash(config)) throw new Error('Runtime does not match complete frozen configuration');
  const off = intervention.navigationLog().config;
  if (await navigation.navigationHash(off) !== await navigation.navigationHash({ ...config, mode: 'output_disabled' })) throw new Error('Unmatched intervention configuration');
  const baseline = new navigation.ContinuousNavigationEngine(authority, 'neural').navigationLog().config;
  if (await navigation.navigationHash(config) !== await navigation.navigationHash({ ...baseline, initial_pose: pose })) throw new Error('Non-pose controls differ from V10.6A');
  if (control.snapshot().step !== 0 || control.snapshot().substeps !== 0 || intervention.snapshot().step !== 0) throw new Error('Premature execution');
  return { control, intervention_config: off };
}

export async function parseFrozen(text: string, authority: NeuralArtifact) {
  if (sha256(text) !== CONFIG_SHA256) throw new Error('Frozen configuration hash mismatch');
  const config = JSON.parse(text) as Record<string, unknown>;
  const { navigation } = await loadFrozenModules();
  if (await navigation.navigationHash(config) !== CONFIG_SHA256) throw new Error('Non-canonical frozen serialization');
  return { config, ...await validateControl(config, authority) };
}

export async function prepareFrozen(read: (path: string) => Buffer = path => readFileSync(path)) {
  verifyResolutionEnvironment();
  git('merge-base', '--is-ancestor', PROTOCOL_COMMIT, 'HEAD');
  if (git('rev-parse', `${PROTOCOL_COMMIT}^`).toString().trim() !== '04ebca9e87b2edc0d842d9a9ee4a12bc53b88443') throw new Error('Unexpected protocol parent');
  const frozenDependencyHashes = Object.fromEntries(FROZEN_REFERENCE_FILES.map(path => [path, verifyReferenceFile(path, read)]));
  if (frozenDependencyHashes[VISUAL_MANIFEST] !== VISUAL_MANIFEST_SHA256) throw new Error(`Frozen visual manifest hash mismatch: ${VISUAL_MANIFEST}`);
  const compilerOptions = frozenCompilerOptions();
  verifyRunnerImports(read, compilerOptions);
  verifyFrozenImportResolution(read, compilerOptions);
  const protectedFiles: Record<string, string> = {};
  function verify(path: string, expected: string) {
    const actual = verifyReferenceFile(path, read, expected);
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
  const sourceHash = (JSON.parse(read(resolve(ROOT, CONFIG_PATH)).toString('utf8')) as { source_raw_sha256?: unknown }).source_raw_sha256;
  if (typeof sourceHash !== 'string' || !/^[a-f0-9]{64}$/.test(sourceHash)) throw new Error('Frozen configuration has an invalid source artifact hash');
  verify(source, sourceHash);
  const { neural } = await loadFrozenModules();
  const authority = neural.parseNeuralLocomotion(JSON.parse(read(resolve(ROOT, source)).toString('utf8')));
  const prepared = await parseFrozen(read(resolve(ROOT, CONFIG_PATH)).toString('utf8'), authority);
  return { ...prepared, authority, provenance: {
    protocol_commit: PROTOCOL_COMMIT, config_sha256: CONFIG_SHA256, protocol_document_sha256: sha256(read(resolve(ROOT, DOCUMENT))),
    execution_source_commit: git('rev-parse', 'HEAD').toString().trim(),
    wrapper_sha256: sha256(readFileSync(fileURLToPath(import.meta.url))),
    node: process.version, platform: process.platform, architecture: process.arch,
    frozen_dependency_files: frozenDependencyHashes,
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
  const { navigation, comparison, report: reportModule } = await loadFrozenModules();
  for (let n = 0; n < 1500; n++) prepared.control.advance();
  const parent = await prepared.control.exportNavigation();
  const pair = await comparison.generatePair(prepared.authority, parent, () => {}, async () => {});
  await comparison.validatePair(prepared.authority, pair);
  if (pair.config.duration_s !== 30 || parent.log.stop_step !== 1500 || parent.log.termination !== 'DURATION_COMPLETED' || pair.config.parent_config_sha256 !== CONFIG_SHA256 || pair.parent.log.events.length || pair.result.tracks.some(t => t.frames.length !== 1501 || t.final_state.step !== 1500 || t.final_state.substeps !== 300000)) throw new Error('Incomplete or mismatched frozen result');
  const report = { ...reportModule.contributionReport(pair), experiment: 'V10.6B', protocol: prepared.provenance, validation: 'validatePair:PASS' };
  // Existing pair validator checks semantic replay and finite telemetry. Reject any additional report non-finites.
  await navigation.navigationHash(report);
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
  if (output === '--check' && extra.length === 0) {
    const prepared = await prepareFrozen();
    console.log(JSON.stringify({ status: 'FROZEN_PREFLIGHT_PASSED', protocol_commit: prepared.provenance.protocol_commit, execution_source_commit: prepared.provenance.execution_source_commit, frozen_dependency_files: Object.keys(prepared.provenance.frozen_dependency_files) }, null, 2));
  } else {
    if (!output || extra.length) throw new Error('Usage: node --import tsx scripts/frozen-contribution.ts NEW_EXTERNAL_DIRECTORY | --check');
    console.log(JSON.stringify(await runFrozen(output), null, 2));
  }
}
