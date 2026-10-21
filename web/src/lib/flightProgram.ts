/** Engineering authoring only. The existing v8 plant remains the sole dynamics authority. */
import { createFlightTrial, exportFlight, flightCanonical, flightHash, FlightEngine, importFlight, reconstructFlight, validateFlightTrial, type FlightCommand, type FlightTrial } from './engineeringFlight';
import type { WingbeatPreset } from './flightWingsV8';

export const REFERENCE_FLIGHT_ID = 'reference-flight-v8';
export const REFERENCE_INPUT_HASH = '25af17966a60f9ed17267d6143cac86b783fd370ca09fef33ee49313177c9f61';
export const REFERENCE_RESULT_HASH = '8c8fc14e028a40fbc1aea526f253306bafc827b858a52495f0751168655528b7';
export type FlightProgram = {
  schema: 'engineering_flight_program_v8_1'; classification: 'ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT';
  id: string; name: string; source_program_id: string | null; trial: FlightTrial; content_sha256: string;
};
export type FlightDraftRow = { id: string; time: string; forward: string; turn: string; vertical: string; intent: FlightCommand['intent'] };
export type FlightDraft = { id: string; name: string; source_program_id: string | null; duration: string; preset: WingbeatPreset; rows: FlightDraftRow[] };
export type FlightIssue = { rowId?: string; field: string; message: string };
export type FlightRun = { schema: 'engineering_flight_run_v8_1'; program: FlightProgram; result: Awaited<ReturnType<typeof exportFlight>> };
const keys = (v: object, expected: string) => Object.keys(v).sort().join(',') === expected;
const idValid = (v: unknown): v is string => typeof v === 'string' && /^[a-zA-Z0-9_-]{1,80}$/.test(v);
export const newFlightId = () => crypto.randomUUID();
export function programDraft(p: FlightProgram): FlightDraft {
  return { id: p.id, name: p.name, source_program_id: p.source_program_id, duration: String(p.trial.stop_step * .02), preset: p.trial.presentation.preset,
    rows: p.trial.commands.map(c => ({ id: c.id, time: (c.step * .02).toFixed(2), forward: String(c.forward), turn: String(c.turn), vertical: String(c.vertical), intent: c.intent })) };
}
export function duplicateFlightDraft(d: FlightDraft, id = newFlightId()): FlightDraft {
  return { ...structuredClone(d), id, name: `${d.name.slice(0, 90)} copy`, source_program_id: d.id };
}
export function emptyFlightDraft(): FlightDraft { return { id: newFlightId(), name: 'Custom flight', source_program_id: null, duration: '12', preset: 'normal', rows: [] }; }
export function addFlightRow(d: FlightDraft, copy?: FlightDraftRow): FlightDraft {
  return { ...d, rows: [...d.rows, copy ? { ...copy, id: newFlightId() } : { id: newFlightId(), time: '', forward: '0', turn: '0', vertical: '0', intent: 'HOLD' }] };
}
export function editFlightRow(d: FlightDraft, id: string, values: Partial<Omit<FlightDraftRow, 'id'>>): FlightDraft {
  return { ...d, rows: d.rows.map(r => r.id === id ? { ...r, ...values } : r) };
}
export function removeFlightRow(d: FlightDraft, id: string): FlightDraft { return { ...d, rows: d.rows.filter(r => r.id !== id) }; }
const gridStep = (s: string) => s.trim() && Number.isFinite(Number(s)) && Math.abs(Number(s) / .02 - Math.round(Number(s) / .02)) < 1e-8 ? Math.round(Number(s) / .02) : null;
/** No dynamics on edits. Sorting only: off-grid times are rejected, never rounded to another boundary. */
export function normalizeFlightDraft(d: FlightDraft): { trial?: FlightTrial; issues: FlightIssue[] } {
  const issues: FlightIssue[] = [];
  if (!idValid(d.id) || (d.source_program_id !== null && !idValid(d.source_program_id))) issues.push({ field: 'identity', message: 'Invalid program identity.' });
  if (!d.name.trim() || d.name.length > 100) issues.push({ field: 'name', message: 'Name must contain 1–100 characters.' });
  const stop = gridStep(d.duration);
  if (stop === null || stop < 1 || stop > 600) issues.push({ field: 'duration', message: 'Duration must be on the 0.02 s grid, greater than zero and at most 12 s.' });
  if (!Array.isArray(d.rows) || d.rows.length < 1 || d.rows.length > 100) issues.push({ field: 'commands', message: 'Use 1–100 commands.' });
  const commands: FlightCommand[] = [], steps = new Set<number>(), ids = new Set<string>();
  for (const row of d.rows) {
    const issue = (field: string, message: string) => issues.push({ rowId: row.id, field, message });
    if (!idValid(row.id) || ids.has(row.id)) issue('id', 'Command IDs must be valid and unique.'); ids.add(row.id);
    const step = gridStep(row.time);
    if (step === null || step < 0 || (stop !== null && step >= stop)) issue('time', 'Time must be a 0.02 s boundary before the terminal boundary.');
    else if (steps.has(step)) issue('time', 'Only one complete command may apply at a boundary; merge these controls.');
    else steps.add(step);
    const controls = { forward: Number(row.forward), turn: Number(row.turn), vertical: Number(row.vertical) };
    for (const field of ['forward', 'turn', 'vertical'] as const) if (!row[field].trim() || !Number.isFinite(controls[field]) || Math.abs(controls[field]) > 1) issue(field, 'Enter a finite value from −1 to 1.');
    if (!['HOLD', 'TAKEOFF', 'LAND'].includes(row.intent)) issue('intent', 'Use HOLD, TAKEOFF or LAND.');
    if (step !== null) commands.push({ id: row.id, step, ...controls, intent: row.intent });
  }
  if (issues.length) return { issues };
  try { return { issues, trial: createFlightTrial(commands.sort((a, b) => a.step - b.step), stop!, d.preset) }; }
  catch (e) { return { issues: [{ field: 'program', message: String(e) }] }; }
}
/** Explicit validation executes the existing plant to diagnose impossible intents. Contacts are valid outcomes. */
export async function validateFlightDraft(d: FlightDraft): Promise<{ program?: FlightProgram; issues: FlightIssue[]; warnings: string[] }> {
  const normalized = normalizeFlightDraft(d);
  if (!normalized.trial) return { issues: normalized.issues, warnings: [] };
  const engine = reconstructFlight(normalized.trial);
  const issues = engine.events().filter(e => e.kind === 'REJECTED_COMMAND').map(e => ({ rowId: normalized.trial!.commands.find(c => c.step === e.step)?.id, field: 'intent', message: `${e.time.toFixed(2)} s: ${e.detail}` }));
  if (issues.length) return { issues, warnings: [] };
  const program: FlightProgram = { schema: 'engineering_flight_program_v8_1', classification: 'ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT', id: d.id, name: d.name.trim(), source_program_id: d.source_program_id, trial: normalized.trial, content_sha256: await flightHash(normalized.trial) };
  if (program.id === REFERENCE_FLIGHT_ID && (program.content_sha256 !== REFERENCE_INPUT_HASH || program.name !== 'Reference Flight v8' || program.source_program_id !== null)) return { issues: [{ field: 'identity', message: 'Reference Flight v8 is immutable. Duplicate it before editing.' }], warnings: [] };
  return { program, issues: [], warnings: engine.snapshot().state === 'grounded' ? [] : ['The computed program ends airborne. This is a valid bounded outcome, not a completed landing.'] };
}
export async function referenceFlightProgram(): Promise<FlightProgram> {
  return { schema: 'engineering_flight_program_v8_1', classification: 'ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT', id: REFERENCE_FLIGHT_ID, name: 'Reference Flight v8', source_program_id: null, trial: createFlightTrial(), content_sha256: await flightHash(createFlightTrial()) };
}
export async function importFlightProgram(value: unknown): Promise<FlightProgram> {
  const p = value as FlightProgram;
  if (!p || !keys(p, 'classification,content_sha256,id,name,schema,source_program_id,trial') || p.schema !== 'engineering_flight_program_v8_1' || p.classification !== 'ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT' || typeof p.name !== 'string' || !idValid(p.id) || (p.source_program_id !== null && !idValid(p.source_program_id))) throw new Error('Invalid engineering flight program schema/metadata');
  validateFlightTrial(p.trial);
  const result = await validateFlightDraft(programDraft(p));
  if (!result.program || result.program.content_sha256 !== p.content_sha256 || flightCanonical(result.program) !== flightCanonical(p)) throw new Error(`Flight program identity/semantics mismatch: ${result.issues.map(e => e.message).join(' ')}`);
  return structuredClone(p);
}
export async function exportFlightRun(program: FlightProgram, engine: FlightEngine): Promise<FlightRun> {
  const p = await importFlightProgram(program);
  if (flightCanonical(engine.trial()) !== flightCanonical(p.trial)) throw new Error('Run belongs to a different immutable program snapshot');
  return { schema: 'engineering_flight_run_v8_1', program: p, result: await exportFlight(engine, p.trial.presentation.preset) };
}
export async function importFlightRun(value: unknown) {
  const r = value as FlightRun;
  if (!r || !keys(r, 'program,result,schema') || r.schema !== 'engineering_flight_run_v8_1') throw new Error('Invalid engineering flight run schema');
  const program = await importFlightProgram(r.program), engine = await importFlight(r.result);
  if (flightCanonical(engine.trial()) !== flightCanonical(program.trial)) throw new Error('Run and program snapshot disagree');
  return { program, engine };
}
export function flightOutcome(engine: FlightEngine, step = engine.snapshot().step) {
  if (!Number.isInteger(step) || step < 0 || step > engine.snapshot().step) throw new Error('Outcome outside recorded flight boundaries');
  let distance = 0, maxAltitude = 0, contactCount = 0;
  const ground = engine.trial().model.ground_y; let previous = engine.frame(0);
  for (let i = 0; i <= step; i++) { const f = engine.frame(i); maxAltitude = Math.max(maxAltitude, f.position[1] - ground); contactCount += f.events.filter(e => e.kind === 'CONTACT').length; if (i) { distance += Math.hypot(...f.position.map((v, k) => v - previous.position[k])); } previous = f; }
  return { distance, maxAltitude, contactCount };
}
