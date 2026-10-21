/** Independent, origin-local engineering library. No scientific IndexedDB migration. */
import { reconstructFlight } from './engineeringFlight';
import { exportFlightRun, importFlightProgram, importFlightRun, REFERENCE_FLIGHT_ID, type FlightProgram, type FlightRun } from './flightProgram';
export const FLIGHT_LIBRARY_KEY = 'neurofly.engineering-flight-library.v8_1';
export interface FlightStorage { getItem(key: string): string | null; setItem(key: string, value: string): void }
type ProgramRecord = { kind: 'program'; key: string; program: FlightProgram };
type RunRecord = { kind: 'run'; key: string; program: FlightProgram; stop_step: number; result_sha256: string };
export type FlightLibraryRecord = ProgramRecord | RunRecord;
export class FlightProgramLibrary {
  constructor(private readonly storage: FlightStorage) {}
  private raw(): unknown[] {
    const value = this.storage.getItem(FLIGHT_LIBRARY_KEY);
    if (!value) return [];
    if (value.length > 2_000_000) throw new Error('Oversized engineering library retained without overwriting.');
    const data = JSON.parse(value);
    if (!data || data.schema !== 'engineering_flight_library_v8_1' || Object.keys(data).sort().join(',') !== 'records,schema' || !Array.isArray(data.records) || data.records.length > 40) throw new Error('Engineering flight library is invalid; retained without overwriting.');
    const ids = data.records.filter((r: unknown) => r && typeof r === 'object' && 'key' in r).map((r: { key: unknown }) => r.key);
    if (new Set(ids).size !== ids.length) throw new Error('Ambiguous duplicate engineering storage identities; records retained without overwriting.');
    return data.records;
  }
  private async validate(value: unknown): Promise<FlightLibraryRecord> {
    const record = value as FlightLibraryRecord;
    if (!record || !['program', 'run'].includes(record.kind)) throw new Error('Invalid flight library record');
    const program = await importFlightProgram(record.program);
    const key = `${record.kind}:${program.id}:${program.content_sha256}`;
    if (record.kind === 'program') {
      if (Object.keys(record).sort().join(',') !== 'key,kind,program' || record.key !== key) throw new Error('Invalid program record identity');
    } else {
      if (Object.keys(record).sort().join(',') !== 'key,kind,program,result_sha256,stop_step' || record.stop_step !== program.trial.stop_step || record.key !== key || typeof record.result_sha256 !== 'string') throw new Error('Invalid completed flight record');
      const expected = await exportFlightRun(program, reconstructFlight(program.trial));
      if (expected.result.result_sha256 !== record.result_sha256) throw new Error('Saved flight result disagrees with reconstructed commands');
    }
    return structuredClone(record);
  }
  async list() {
    const records: FlightLibraryRecord[] = [], errors: string[] = [];
    for (const raw of this.raw()) { try { records.push(await this.validate(raw)); } catch (e) { errors.push(`Isolated invalid engineering record: ${String(e)}`); } }
    return { records, errors };
  }
  private async put(record: FlightLibraryRecord) {
    const verified = await this.validate(record), all = this.raw();
    const index = all.findIndex(r => typeof r === 'object' && r !== null && 'key' in r && r.key === verified.key);
    if (index >= 0) { await this.validate(all[index]); all[index] = verified; } else all.push(verified);
    if (all.length > 40) throw new Error('Engineering library limit reached (40 snapshots). Export a program/run; no records were removed.');
    const data = JSON.stringify({ schema: 'engineering_flight_library_v8_1', records: all });
    if (data.length > 2_000_000) throw new Error('Engineering library exceeds 2 MB; existing records preserved.');
    try { this.storage.setItem(FLIGHT_LIBRARY_KEY, data); } catch { throw new Error('Unable to save engineering flight (storage unavailable or quota reached). Existing records were not replaced.'); }
  }
  async saveProgram(value: FlightProgram) {
    const program = await importFlightProgram(value);
    if (program.id === REFERENCE_FLIGHT_ID) throw new Error('Reference Flight v8 is built in and cannot be overwritten; duplicate it.');
    await this.put({ kind: 'program', key: `program:${program.id}:${program.content_sha256}`, program });
  }
  async saveRun(value: FlightRun) {
    const { program, engine } = await importFlightRun(value);
    if (engine.snapshot().step !== program.trial.stop_step) throw new Error('Only completed runs can be saved. Export a recorded prefix using the v8 exporter.');
    await this.put({ kind: 'run', key: `run:${program.id}:${program.content_sha256}`, program, stop_step: engine.stopStep, result_sha256: value.result.result_sha256 });
  }
  async open(record: FlightLibraryRecord) {
    const stored = this.raw().find(r => r && typeof r === 'object' && 'key' in r && r.key === record.key);
    if (!stored) throw new Error('Saved engineering flight is missing; refresh the library.');
    const verified = await this.validate(stored);
    return { program: verified.program, engine: verified.kind === 'run' ? reconstructFlight(verified.program.trial) : undefined };
  }
}
