"use client";
import { useEffect, useRef, useState } from 'react';
import { FlightEngine } from '@/lib/engineeringFlight';
import { addFlightRow, duplicateFlightDraft, editFlightRow, emptyFlightDraft, importFlightProgram, importFlightRun, programDraft, referenceFlightProgram, REFERENCE_FLIGHT_ID, removeFlightRow, validateFlightDraft, type FlightDraft, type FlightDraftRow, type FlightIssue, type FlightProgram, type FlightRun } from '@/lib/flightProgram';
import { FlightProgramLibrary, type FlightLibraryRecord } from '@/lib/flightProgramLibrary';

export function FlightProgramEditor({ playing, incoming, onInvalidate, onActivate, getRun }: {
  playing: boolean; incoming: FlightProgram | null;
  onInvalidate(): void; onActivate(p: FlightProgram, engine?: FlightEngine, play?: boolean): void; getRun(): Promise<FlightRun>;
}) {
  const [draft, setDraft] = useState<FlightDraft | null>(null), [validated, setValidated] = useState<FlightProgram | null>(null);
  const [issues, setIssues] = useState<FlightIssue[]>([]), [message, setMessage] = useState(''), [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState<FlightLibraryRecord[]>([]), [selected, setSelected] = useState('');
  const epoch = useRef(0), panel = useRef<HTMLDetailsElement>(null);
  useEffect(() => { let current = true; void (incoming ? Promise.resolve(incoming) : referenceFlightProgram()).then(p => { if (current) { setDraft(programDraft(p)); setValidated(p); setIssues([]); } }); return () => { current = false; }; }, [incoming]);
  const locked = playing || busy, reference = draft?.id === REFERENCE_FLIGHT_ID;
  const library = () => new FlightProgramLibrary(window.localStorage);
  async function refresh() { const result = await library().list(); setSaved(result.records); return result.errors.join(' '); }
  async function task(action: () => Promise<void>) { setBusy(true); setMessage(''); try { await action(); } catch (e) { setMessage(String(e)); } finally { setBusy(false); } }
  function change(next: FlightDraft) { epoch.current++; setDraft(next); setValidated(null); setIssues([]); setMessage('Draft changed. Validate and Run from the beginning; saved snapshots remain intact.'); onInvalidate(); }
  async function validate() {
    if (!draft) return; const version = epoch.current, start = performance.now(), result = await validateFlightDraft(structuredClone(draft));
    if (version !== epoch.current) return;
    setIssues(result.issues); setValidated(result.program ?? null);
    if (result.program) { setDraft(programDraft(result.program)); setMessage(`Validated ${result.program.trial.commands.length} commands in ${(performance.now() - start).toFixed(2)} ms. ${result.warnings.join(' ')}`); }
    else setMessage('Program has errors; execution is disabled.');
  }
  function exportJson(value: unknown, filename: string) { const url = URL.createObjectURL(new Blob([JSON.stringify(value)], { type: 'application/json' })); const link = document.createElement('a'); link.href = url; link.download = filename; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
  async function upload(file?: File) {
    if (!file) return;
    if (file.size > 4_000_000) throw new Error('Flight program/run file exceeds 4 MB.');
    const value = JSON.parse(await file.text());
    if (value.schema === 'engineering_flight_run_v8_1') { const { program, engine } = await importFlightRun(value); setDraft(programDraft(program)); setValidated(program); setIssues([]); onActivate(program, engine); setMessage('Run reconstructed and every stored output verified.'); }
    else { const program = await importFlightProgram(value); setDraft(programDraft(program)); setValidated(program); setIssues([]); onActivate(program); setMessage('Program identity and command semantics verified.'); }
  }
  return <details ref={panel} className="flight-program-editor" onToggle={e => { if (e.currentTarget.open) void task(async () => { const warnings = await refresh(); if (warnings) setMessage(warnings); }); }}>
    <summary>Flight Program Editor v8.1</summary>
    <p>Engineering commands only · 20 ms boundaries · up to 12 s. Each row replaces all held controls until the next row; TAKEOFF/LAND applies once. No hidden commands are inserted.</p>
    <div className="flight-program-actions">
      <button disabled={locked} onClick={() => void task(async () => { const p = await referenceFlightProgram(); epoch.current++; setDraft(programDraft(p)); setValidated(p); setIssues([]); onActivate(p); setMessage('Original Reference Flight v8 restored.'); })}>Reference Flight v8</button>
      <button disabled={locked} onClick={() => change(emptyFlightDraft())}>New Flight Program</button>
      <button disabled={locked || !draft} onClick={() => draft && change(duplicateFlightDraft(draft))}>Duplicate Program</button>
    </div>
    {draft ? <>
      <p>{reference ? 'Built-in reference is read-only. Duplicate Program to edit.' : 'Editable engineering program'} · {validated ? 'Validated snapshot' : 'Draft — not executable'}</p>
      <fieldset disabled={locked || reference}>
        <label>Program name <input aria-label="Flight program name" value={draft.name} maxLength={100} onChange={e => change({ ...draft, name: e.target.value })}/></label>
        <label>Duration (s) <input aria-label="Flight program duration" type="number" min="0.02" max="12" step="0.02" value={draft.duration} onChange={e => change({ ...draft, duration: e.target.value })}/></label>
        <label>Program wing preset <select aria-label="Program wing preset" value={draft.preset} onChange={e => change({ ...draft, preset: e.target.value as FlightDraft['preset'] })}><option value="normal">Normal · 12 Hz</option><option value="inspection">Slow Inspection · 2 Hz</option></select></label>
        <ol className="flight-command-list">{draft.rows.map((row, index) => <li key={row.id} data-flight-command={row.id}>
          <strong>Command {index + 1}</strong><div className="flight-command-fields">
            {(['time', 'forward', 'turn', 'vertical'] as const).map(field => <label key={field}>{field === 'time' ? 'Effective time (s)' : field}<input aria-label={`Command ${index + 1} ${field}`} type="number" step={field === 'time' ? '.02' : '.05'} min={field === 'time' ? 0 : -1} max={field === 'time' ? draft.duration : 1} value={row[field]} onChange={e => change(editFlightRow(draft, row.id, { [field]: e.target.value }))}/></label>)}
            <label>Intent <select aria-label={`Command ${index + 1} intent`} value={row.intent} onChange={e => change(editFlightRow(draft, row.id, { intent: e.target.value as FlightDraftRow['intent'] }))}><option>HOLD</option><option>TAKEOFF</option><option>LAND</option></select></label>
          </div>
          {issues.filter(x => x.rowId === row.id).map((x, i) => <p role="alert" key={i}>{x.field}: {x.message}</p>)}
          <button onClick={() => change(addFlightRow(draft, row))}>Duplicate Command {index + 1}</button>{' '}<button onClick={() => change(removeFlightRow(draft, row.id))}>Remove Command {index + 1}</button>
        </li>)}</ol>
        <button disabled={draft.rows.length >= 100} onClick={() => change(addFlightRow(draft))}>Add Command</button>
      </fieldset>
      {issues.filter(x => !x.rowId).map((x, i) => <p role="alert" key={i}>{x.message}</p>)}
      <div className="flight-program-actions">
        <button disabled={locked} onClick={() => void task(validate)}>Validate Program</button>
        <button disabled={locked || !validated} onClick={() => { if (validated) { onActivate(structuredClone(validated), undefined, true); if (panel.current) panel.current.open = false; } }}>Run Program</button>
        <button disabled={locked || !validated || reference} onClick={() => void task(async () => { await library().saveProgram(validated!); const warnings = await refresh(); setMessage(`Program snapshot saved locally. ${warnings}`); })}>Save Program</button>
        <button disabled={locked} onClick={() => void task(async () => { await library().saveRun(await getRun()); const warnings = await refresh(); setMessage(`Completed run saved as reproducible inputs and verified result identity. ${warnings}`); })}>Save Completed Run</button>
        <button disabled={locked || !validated} onClick={() => validated && exportJson(validated, 'neurofly-flight-program-v8_1.json')}>Export Program</button>
        <button disabled={locked} onClick={() => void task(async () => exportJson(await getRun(), 'neurofly-flight-run-v8_1.json'))}>Export Program Run</button>
      </div>
      <p>Program ID: <code>{draft.id}</code><br/>Validated input SHA-256: <code>{validated?.content_sha256 ?? 'Not validated'}</code></p>
    </> : <p>Loading engineering reference…</p>}
    <label>Import Flight Program or Run <input aria-label="Import Flight Program or Run" type="file" accept="application/json" disabled={locked} onChange={e => { const file = e.target.files?.[0]; e.target.value = ''; void task(() => upload(file)); }}/></label>
    <div className="flight-program-actions">
      <label>Saved engineering flights <select aria-label="Saved engineering flights" value={selected} disabled={locked} onChange={e => setSelected(e.target.value)}><option value="">Choose a saved program or run</option>{saved.map(r => <option key={r.key} value={r.key}>{r.kind === 'program' ? 'Program' : 'Completed run'} · {r.program.name} · {r.program.content_sha256.slice(0, 8)}</option>)}</select></label>
      <button disabled={locked || !selected} onClick={() => void task(async () => { const record = saved.find(x => x.key === selected); if (!record) throw new Error('Saved flight is missing; refresh the list.'); const { program, engine } = await library().open(record); setDraft(programDraft(program)); setValidated(program); setIssues([]); onActivate(program, engine); setMessage('Saved engineering snapshot reopened and verified.'); })}>Open Saved Flight</button>
      <button disabled={locked} onClick={() => void task(async () => { const warnings = await refresh(); setMessage(warnings || 'Engineering library refreshed.'); })}>Refresh Saved Flights</button>
    </div>
    {playing ? <p>Execution snapshot frozen. Pause, then edit to start a new run.</p> : null}
    {message ? <p role="status">{message}</p> : null}
  </details>;
}
