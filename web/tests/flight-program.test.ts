import test from 'node:test';
import assert from 'node:assert/strict';
import { createFlightTrial, exportFlight, flightCanonical, flightHash, reconstructFlight } from '../src/lib/engineeringFlight';
import { addFlightRow, duplicateFlightDraft, editFlightRow, exportFlightRun, flightOutcome, importFlightProgram, importFlightRun, normalizeFlightDraft, programDraft, referenceFlightProgram, REFERENCE_INPUT_HASH, REFERENCE_RESULT_HASH, removeFlightRow, validateFlightDraft } from '../src/lib/flightProgram';
import { FlightProgramLibrary, FLIGHT_LIBRARY_KEY, type FlightStorage } from '../src/lib/flightProgramLibrary';
class Memory implements FlightStorage { data = new Map<string, string>(); getItem(k: string) { return this.data.get(k) ?? null; } setItem(k: string, v: string) { this.data.set(k, v); } }
async function custom(turn = '.3') { const d = duplicateFlightDraft(programDraft(await referenceFlightProgram()), 'custom-flight'); return (await validateFlightDraft(editFlightRow(d, 'climbing-turn', { turn }))).program!; }

test('immutable original v8 input/result identities; metadata rename does not change numerical identity', async () => {
  const ref = await referenceFlightProgram(), result = await exportFlight(reconstructFlight(ref.trial), 'normal');
  assert.equal(ref.content_sha256, REFERENCE_INPUT_HASH); assert.equal(result.result_sha256, REFERENCE_RESULT_HASH);
  assert.deepEqual(ref.trial, createFlightTrial()); assert.equal(result.frames.length, 601);
  const bad = programDraft(ref); bad.rows[2].turn = '.3'; assert.equal((await validateFlightDraft(bad)).program, undefined);
  const p = await custom(), renamed = await importFlightProgram({ ...p, name: 'Renamed flight' }); assert.equal(p.content_sha256, renamed.content_sha256);
  assert.deepEqual(reconstructFlight(p.trial).frames(), reconstructFlight(renamed.trial).frames());
});
test('add/edit/duplicate/remove maintain stable IDs, normalize chronological order, never silently repair time', async () => {
  let d = duplicateFlightDraft(programDraft(await referenceFlightProgram()), 'editable'); const original = structuredClone(d);
  d = addFlightRow(d); const id = d.rows.at(-1)!.id; d = editFlightRow(d, id, { time: '0.40', forward: '0', intent: 'HOLD' });
  const n = normalizeFlightDraft(d); assert.equal(n.issues.length, 0); assert.equal(n.trial!.commands[0].step, 20); assert.equal(n.trial!.commands[0].id, id);
  assert.deepEqual(removeFlightRow(d, id), original);
  const copy = addFlightRow(d, d.rows[0]); assert.notEqual(copy.rows.at(-1)!.id, d.rows[0].id); assert(normalizeFlightDraft(copy).issues.some(x => x.field === 'time'));
  assert.equal(normalizeFlightDraft(editFlightRow(d, id, { time: '.401' })).trial, undefined);
  assert.equal(normalizeFlightDraft(editFlightRow(d, id, { time: '' })).trial, undefined);
});
test('ranges, missing/nonfinite input, conflicts, terminal boundaries, empty/oversized programs and intents rejected', async () => {
  const d = duplicateFlightDraft(programDraft(await referenceFlightProgram()), 'editable');
  for (const value of ['', '-1', '12', '.001', 'Infinity', 'NaN']) assert(normalizeFlightDraft(editFlightRow(d, 'takeoff', { time: value })).issues.length, value);
  for (const field of ['forward', 'turn', 'vertical'] as const) for (const value of ['', 'NaN', 'Infinity', '1.01', '-1.01']) assert(normalizeFlightDraft(editFlightRow(d, 'takeoff', { [field]: value })).issues.length);
  for (const duration of ['', '0', '12.02', '1.001', '-1']) assert(normalizeFlightDraft({ ...d, duration }).issues.length);
  assert(normalizeFlightDraft({ ...d, rows: [] }).issues.length);
  assert(normalizeFlightDraft({ ...d, rows: Array.from({ length: 101 }, (_, i) => ({ ...d.rows[0], id: `row-${i}`, time: String(i * .02) })) }).issues.length);
  for (const mutate of [editFlightRow(d, 'takeoff', { intent: 'LAND' }), editFlightRow(d, 'climbing-turn', { intent: 'TAKEOFF' }), removeFlightRow(d, 'takeoff')]) assert.equal((await validateFlightDraft(mutate)).program, undefined);
  const hundred = { ...d, rows: Array.from({ length: 100 }, (_, i) => ({ ...d.rows[0], id: `row-${i}`, time: (i * .02).toFixed(2), forward: '0', vertical: '0', intent: 'HOLD' as const })) };
  assert.equal((await validateFlightDraft(hundred)).issues.length, 0);
});
test('custom commands drive the existing plant: turning and vertical edits change computed trajectories; contacts are outcomes', async () => {
  const ref = await referenceFlightProgram(), p = await custom(), a = reconstructFlight(ref.trial), b = reconstructFlight(p.trial);
  assert.deepEqual(a.frames()[0], b.frames()[0]); assert.deepEqual(p.trial.commands.filter(c => c.id !== 'climbing-turn'), ref.trial.commands.filter(c => c.id !== 'climbing-turn'));
  assert.notEqual(a.snapshot().heading, b.snapshot().heading); assert.notDeepEqual(a.snapshot().position, b.snapshot().position);
  assert.deepEqual(reconstructFlight(p.trial).frames(), b.frames());
  const draft = programDraft(p), high = (await validateFlightDraft(editFlightRow(draft, 'climbing-turn', { vertical: '1' }))).program!;
  assert(flightOutcome(reconstructFlight(high.trial)).maxAltitude > flightOutcome(b).maxAltitude);
  const wallDraft = { ...draft, rows: [{ id: 'launch', time: '0', forward: '1', turn: '0', vertical: '1', intent: 'TAKEOFF' as const }] };
  const wall = await validateFlightDraft(wallDraft); assert(wall.program); assert(wall.warnings.length); assert(flightOutcome(reconstructFlight(wall.program.trial)).contactCount > 0);
});
test('versioned program/run import verifies real dynamics despite recomputed superficial hashes; snapshots immutable', async () => {
  const p = await custom(), engine = reconstructFlight(p.trial), run = await exportFlightRun(p, engine);
  assert.deepEqual(await importFlightProgram(JSON.parse(JSON.stringify(p))), p); assert.deepEqual((await importFlightRun(run)).engine.frames(), engine.frames());
  const before = flightCanonical(run); const d = programDraft(p); d.rows[0].time = '1.2'; assert.equal(flightCanonical(run), before);
  const bad = structuredClone(run); bad.result.frames[300].position[0] += .01; bad.result.result_sha256 = await flightHash({ frames: bad.result.frames, termination: bad.result.termination }); await assert.rejects(importFlightRun(bad));
  const contradictory = structuredClone(run); contradictory.program = await custom('.2'); await assert.rejects(importFlightRun(contradictory));
  for (const wrong of [{ ...p, schema: 'wrong' }, { ...p, content_sha256: '0'.repeat(64) }, { ...p, trial: { ...p.trial, initial: { ...p.trial.initial, heading: 0 } } }]) await assert.rejects(importFlightProgram(wrong));
  const mutated = structuredClone(p); mutated.trial.commands[0].intent = 'LAND'; mutated.content_sha256 = await flightHash(mutated.trial); await assert.rejects(importFlightProgram(mutated));
});
test('origin-local programs and compact runs verify on reopen, isolate bad records, preserve revisions and surface storage failure', async () => {
  const storage = new Memory(), library = new FlightProgramLibrary(storage), p = await custom(), run = await exportFlightRun(p, reconstructFlight(p.trial));
  await library.saveProgram(p); await library.saveRun(run); const entries = (await library.list()).records; assert.equal(entries.length, 2);
  const record = entries.find(r => r.kind === 'run')!; assert(!('frames' in record)); assert.deepEqual((await library.open(record)).engine!.frames(), run.result.frames);
  await library.saveProgram({ ...p, name: 'Renamed' }); assert.equal((await library.list()).records.length, 2);
  await library.saveProgram(await custom('.2')); assert.equal((await library.list()).records.length, 3);
  const raw = JSON.parse(storage.getItem(FLIGHT_LIBRARY_KEY)!); raw.records.push({ kind: 'run', key: 'corrupt', program: p, stop_step: 600, result_sha256: '0' }); storage.setItem(FLIGHT_LIBRARY_KEY, JSON.stringify(raw));
  assert.equal((await library.list()).errors.length, 1); await library.saveProgram(p); assert.equal(JSON.parse(storage.getItem(FLIGHT_LIBRARY_KEY)!).records.length, 4);
  await assert.rejects(library.saveProgram(await referenceFlightProgram()));
  await assert.rejects(library.open({ ...record, key: 'missing' }), /missing/);
  const broken = new FlightProgramLibrary({ getItem: () => null, setItem: () => { throw new Error('quota'); } }); await assert.rejects(broken.saveProgram(p), /quota/);
  storage.setItem(FLIGHT_LIBRARY_KEY, '{'); const before = storage.getItem(FLIGHT_LIBRARY_KEY); await assert.rejects(library.saveProgram(p)); assert.equal(storage.getItem(FLIGHT_LIBRARY_KEY), before);
});

test('inspector metrics stop at the selected recorded boundary, without exposing future contacts', async () => {
  const engine = reconstructFlight((await custom()).trial);
  assert.deepEqual(flightOutcome(engine, 0), { distance: 0, maxAltitude: 0, contactCount: 0 });
  assert.equal(flightOutcome(engine, 500).contactCount, 0); assert.equal(flightOutcome(engine, 600).contactCount, 1);
  for (const step of [-1, .5, 601, NaN]) assert.throws(() => flightOutcome(engine, step));
});
