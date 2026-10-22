/** Explicit offline CLI; never imported by the application. */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, statSync, lstatSync, realpathSync, openSync, closeSync, unlinkSync, constants } from 'node:fs';
import { resolve, relative, isAbsolute, sep, dirname, basename, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseNeuralLocomotion, NEURAL_LOCOMOTION_SHA256 } from '../src/lib/neuralLocomotion';
import { runControlledExperiment, verifyControlledExperiment } from '../src/lib/controlledNeuralSteering';

function outputDestination(requested: string, root: string) {
  const entry = lstatSync(requested, { throwIfNoEntry: false });
  // Parents must already exist, as in the original CLI. realpath resolves every
  // ancestor symlink; a missing parent is rejected without creating directories.
  let parent: string;
  try { parent = realpathSync(dirname(requested)); }
  catch { throw new Error('Output parent must be an existing directory'); }
  if (!statSync(parent).isDirectory()) throw new Error('Output parent must be an existing directory');
  let canonical = join(parent, basename(requested));
  if (entry) {
    try { canonical = realpathSync(requested); }
    catch { throw new Error('Output exists; no overwrite'); } // Includes dangling symlinks.
  }
  const rel = relative(root, canonical);
  if (rel !== '..' && !rel.startsWith('..' + sep) && !isAbsolute(rel)) throw new Error('Keep generated output outside the repository');
  if (entry) throw new Error('Output exists; no overwrite');
  return canonical;
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length !== 2 || !['--output', '--verify'].includes(args[0])) throw new Error('Usage: node --import tsx tools/controlledNeuralSteering.ts --output EXTERNAL.json | --verify EXTERNAL.json');
  const raw = readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url));
  if (createHash('sha256').update(raw).digest('hex') !== NEURAL_LOCOMOTION_SHA256) throw new Error('Pinned neural source bytes changed');
  const authority = parseNeuralLocomotion(JSON.parse(raw.toString('utf8')));
  const path = resolve(args[1]);
  if (args[0] === '--verify') {
    if (statSync(path).size > 20_000_000) throw new Error('Oversized controlled experiment');
    const start = performance.now(), artifact = await verifyControlledExperiment(authority, JSON.parse(readFileSync(path, 'utf8')));
    console.log(JSON.stringify({ status: 'SEMANTIC_RECONSTRUCTION_VERIFIED', artifact_id: artifact.artifact_id, verification_ms: performance.now() - start }));
    return;
  }
  const root = realpathSync(fileURLToPath(new URL('../../', import.meta.url)));
  const destinations = [path, path + '.summary.json'].map(p => outputDestination(p, root));
  const timings: Record<string, number> = {}, start = performance.now();
  const artifact = await runControlledExperiment(authority, timings);
  timings.total_construction_ms = performance.now() - start;
  const serializationStart = performance.now(), serialized = JSON.stringify(artifact) + '\n';
  timings.serialization_ms = performance.now() - serializationStart;
  const summary = { schema: artifact.schema, artifact_id: artifact.artifact_id, input_sha256: artifact.input_sha256, result_sha256: artifact.result_sha256,
    hypotheses: artifact.result.hypotheses, comparisons: artifact.result.comparisons,
    conditions: artifact.result.conditions.map(c => ({ id: c.id, visual: c.visual, mode: c.mode, summary: c.summary })),
    timings, bytes: Buffer.byteLength(serialized), memory: process.memoryUsage(), max_rss_kib: process.resourceUsage().maxRSS,
    note: 'Performance metadata excluded from scientific result identity; maxRSS includes Node initialization and retained artifact' };
  // Recheck canonical parents after computation and write canonical paths rather
  // than the caller's aliases. This reduces, but does not eliminate, ancestor
  // replacement races. Exclusive no-follow opens protect the final components.
  destinations.forEach(p => outputDestination(p, root));
  const created: { path: string; fd: number }[] = [];
  try {
    // Reserve both destinations before writing either payload.
    for (const destination of destinations) created.push({ path: destination, fd: openSync(destination, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | constants.O_NOFOLLOW, 0o666) });
    writeFileSync(created[0].fd, serialized);
    writeFileSync(created[1].fd, JSON.stringify(summary, null, 2) + '\n');
  } catch (error) {
    for (const entry of created) { closeSync(entry.fd); unlinkSync(entry.path); }
    throw error;
  }
  for (const entry of created) closeSync(entry.fd);
  console.log(JSON.stringify({ status: 'COMPLETED', artifact_id: artifact.artifact_id, hypotheses: artifact.result.hypotheses, timings, bytes: summary.bytes }));
}
main().catch(error => { console.error(JSON.stringify({ status: 'EXECUTION_OR_INTEGRITY_FAILED', error: String(error) })); process.exitCode = 1; });
