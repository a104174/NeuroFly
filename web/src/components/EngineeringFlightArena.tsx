"use client";
import { useEffect, useRef, useState } from 'react';
import { FlyViewer } from './FlyViewer';
import { FlightClock, FlightEngine, advanceFlightCursor, createFlightTrial, exportFlight, importFlight, flightScene, FLIGHT_MODEL, type FlightFrame, type FlightTrial, type FlightEvent } from '@/lib/engineeringFlight';
import { FlightProgramEditor } from './FlightProgramEditor';
import { exportFlightRun, flightOutcome, importFlightProgram, newFlightId, referenceFlightProgram, type FlightProgram } from '@/lib/flightProgram';
import { flightHash } from '@/lib/engineeringFlight';
import { flightWingsV8, FLIGHT_WINGS_V8, type WingbeatPreset } from '@/lib/flightWingsV8';

export function EngineeringFlightArena() {
  const activeProgram = useRef<FlightProgram | null>(null);
  const [incoming, setIncoming] = useState<FlightProgram | null>(null), [runnable, setRunnable] = useState(true);
  const engine = useRef<FlightEngine | null>(null), clock = useRef(new FlightClock());
  const cursor = useRef(0);
  const [trial, setTrial] = useState<FlightTrial>(() => createFlightTrial());
  const [frame, setFrame] = useState<FlightFrame>(() => trial.initial);
  const [lastStep, setLastStep] = useState(0), [playing, setPlaying] = useState(false);
  const [preset, setPreset] = useState<WingbeatPreset>('normal');
  const [error, setError] = useState<string | null>(null), [notice, setNotice] = useState('');
  const [cost, setCost] = useState({ update_ms: 0, catchups: 0 });
  const [outcome, setOutcome] = useState({ distance: 0, maxAltitude: 0, contactCount: 0 });
  const [runLabel, setRunLabel] = useState('Reference Flight v8');
  const [events, setEvents] = useState<FlightEvent[]>([]);
  useEffect(() => {
    if (!playing) return;
    let raf = 0, previous: number | null = null;
    const tick = (now: number) => {
      if (previous !== null && engine.current) {
        try {
          const start = performance.now(), current = engine.current;
          const playback = { stopStep: current.stopStep, snapshot: () => ({ step: cursor.current }), advance: () => { const f = advanceFlightCursor(current, cursor.current); cursor.current = f.step; } };
          const result = clock.current.advance(playback, now - previous);
          if (result.steps) { setOutcome(flightOutcome(current, cursor.current)); setFrame(current.frame(cursor.current)); setLastStep(current.snapshot().step); setEvents(current.events().filter(e => e.kind !== 'COMMAND')); }
          setCost(c => ({ update_ms: performance.now() - start, catchups: c.catchups + Number(result.limited) }));
          if (cursor.current === trial.stop_step) { setPlaying(false); return; }
        } catch (e) { setError(String(e)); setPlaying(false); return; }
      }
      previous = now; raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick); return () => cancelAnimationFrame(raf);
  }, [playing, trial.stop_step]);
  function activate(program: FlightProgram, replay?: FlightEngine, run = false) {
    const frozen = structuredClone(program), next = replay ?? new FlightEngine(frozen.trial), snapshot = next.snapshot();
    activeProgram.current = frozen; engine.current = next; cursor.current = snapshot.step; clock.current.reset();
    setOutcome(flightOutcome(next, snapshot.step)); setRunLabel(frozen.name); setIncoming(frozen); setTrial(frozen.trial); setPreset(frozen.trial.presentation.preset); setFrame(snapshot); setLastStep(snapshot.step); setEvents(next.events().filter(e => e.kind !== 'COMMAND')); setRunnable(true); setPlaying(run); setError(null); setCost({ update_ms: 0, catchups: 0 });
    setNotice(`Immutable run input: ${frozen.name} · ${frozen.content_sha256}`);
  }
  async function programRun() {
    if (!runnable) throw new Error('Draft has changed. Validate and Run before saving/exporting a run.');
    const program = activeProgram.current ?? await referenceFlightProgram();
    return exportFlightRun(program, engine.current ?? new FlightEngine(trial));
  }
  function play() {
    if (!runnable) return;
    if (!engine.current) engine.current = new FlightEngine(trial);
    clock.current.reset(); setPlaying(true);
  }
  function reset() { engine.current = null; cursor.current = 0; clock.current.reset(); setPlaying(false); setFrame(trial.initial); setOutcome({ distance: 0, maxAltitude: 0, contactCount: 0 }); setLastStep(0); setEvents([]); setCost({ update_ms: 0, catchups: 0 }); setError(null); setNotice(''); }
  async function download() {
    try {
      const data = await exportFlight(engine.current ?? new FlightEngine(trial), preset);
      const url = URL.createObjectURL(new Blob([JSON.stringify(data)], { type: 'application/json' }));
      const link = document.createElement('a'); link.href = url; link.download = 'neurofly-engineering-flight-v8.json'; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (e) { setError(String(e)); }
  }
  async function upload(file?: File) {
    if (!file) return;
    setPlaying(false); clock.current.reset();
    try {
      if (file.size > 4_000_000) throw new Error('Engineering flight file exceeds 4 MB');
      const start = performance.now(), next = await importFlight(JSON.parse(await file.text()));
      const config = next.trial(), snapshot = next.snapshot();
      let p: FlightProgram | null = null;
      try { p = await importFlightProgram({ schema: 'engineering_flight_program_v8_1', classification: 'ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT', id: newFlightId(), name: 'Imported v8 flight', source_program_id: null, trial: config, content_sha256: await flightHash(config) }); } catch { /* Preserve the wider historical v8 replay contract; authoring stays bounded to v8.1. */ }
      activeProgram.current = p; setIncoming(p); setRunLabel(p?.name ?? 'Legacy v8 replay (outside v8.1 authoring limits)'); setRunnable(true); setOutcome(flightOutcome(next, snapshot.step));
      engine.current = next; cursor.current = snapshot.step; setTrial(config); setPreset(config.presentation.preset); setFrame(snapshot); setLastStep(snapshot.step); setEvents(next.events().filter(e => e.kind !== 'COMMAND')); setError(null);
      setNotice(`Engineering inputs replayed and all telemetry verified in ${(performance.now() - start).toFixed(2)} ms. Original scientific library untouched.`);
    } catch (e) { setError(String(e)); }
  }
  const wings = flightWingsV8(frame.time, frame.state, Math.max(0, frame.position[1] - FLIGHT_MODEL.ground_y), preset);
  return <section className="arena-replay-panel engineering-flight" aria-label="Experimental 3D Flight v8">
    <h2>Experimental 3D Flight v8</h2>
    <p>Engineering kinematic flight — integrated input commands, no neural flight control or aerodynamics. Position and velocity are engineering telemetry. Wingbeats do not generate lift.</p>
    <p>Current run: {runnable ? runLabel : 'Draft — no current trajectory'}</p>
    <label>Wingbeat mode <select aria-label="Wingbeat mode" value={preset} onChange={e => setPreset(e.target.value as WingbeatPreset)}><option value="normal">Normal Wingbeat · 12 Hz</option><option value="inspection">Slow Inspection · 2 Hz</option></select></label>
    <FlightProgramEditor playing={playing} incoming={incoming} onActivate={activate} getRun={programRun} onInvalidate={() => { reset(); activeProgram.current = null; setRunnable(false); setNotice('Draft has unapplied edits. Validate and Run a new snapshot; no previous trajectory is current.'); }}/>
    <FlyViewer arena replayPose={flightScene(frame)} flightPresentation={wings} presentationLabel="Engineering 3D flight / fixed 20 ms integration" playbackControls={<div className="arena-replay-controls">
      <button disabled={!runnable || playing || frame.step === trial.stop_step} onClick={play}>{frame.step < lastStep ? 'Replay flight' : lastStep ? 'Resume flight' : 'Play flight'}</button>
      <button disabled={!playing} onClick={() => { setPlaying(false); clock.current.reset(); }}>Pause flight</button>
      <button onClick={reset}>Reset flight</button>
      <label>Engineering time <input aria-label="Flight simulation time" type="range" min={0} max={lastStep * .02} step={.02} value={frame.time} onChange={e => { setPlaying(false); clock.current.reset(); if (engine.current) { cursor.current = Math.round(Number(e.target.value) / .02); setFrame(engine.current.frame(cursor.current)); setOutcome(flightOutcome(engine.current, cursor.current)); } }}/></label>
      <output>{frame.time.toFixed(2)} / {(trial.stop_step * .02).toFixed(2)} s · {frame.state}</output>
    </div>}/>
    <p data-flight-program-status={runnable ? 'RUN_INPUT_FROZEN' : 'DRAFT_NOT_EXECUTABLE'} data-flight-v8={JSON.stringify(frame)} data-flight-v8-frontier={lastStep} data-flight-v8-cost={JSON.stringify(cost)}>Engineering time {frame.time.toFixed(2)} s · {frame.state} · altitude {(frame.position[1] - FLIGHT_MODEL.ground_y).toFixed(4)} units · X/Y/Z {frame.position.map(v => v.toFixed(4)).join(' / ')} · velocity {frame.velocity.map(v => v.toFixed(4)).join(' / ')} units/s · heading {frame.heading.toFixed(4)} rad · contact {frame.contacts.join(', ') || 'none'} · {lastStep === trial.stop_step ? 'DURATION_COMPLETED' : 'RECORDED_PREFIX'}</p>
    <p data-flight-outcome={JSON.stringify(outcome)}>Calculated through {frame.time.toFixed(2)} s · traveled {outcome.distance.toFixed(5)} units · maximum altitude {outcome.maxAltitude.toFixed(5)} units · {outcome.contactCount} contacts · {frame.state === 'grounded' && frame.step > 0 ? 'grounded' : frame.state}. {runnable ? 'Trajectory belongs to the frozen run input.' : 'Draft has no current run.'}</p>
    <p>Wingbeat {FLIGHT_WINGS_V8.presets[preset]} Hz engineering presentation. Update {cost.update_ms.toFixed(3)} ms · bounded catch-up {cost.catchups}. Low rendering FPS can alias fast wing motion; phase remains analytical. Skipped rendering frames never change integration dt.</p>
    <button disabled={playing || !runnable} onClick={() => void download()}>Export engineering flight JSON</button>{' '}
    <label>Import engineering flight JSON <input type="file" accept="application/json" disabled={playing} onChange={e => { const file = e.target.files?.[0]; e.target.value = ''; void upload(file); }}/></label>
    {error ? <p role="alert">{error}</p> : null}{notice ? <p role="status">{notice}</p> : null}
    <details><summary>Engineering input program and flight contract</summary>
      <p>engineering_3d_kinematic_flight_v8 · Y up / +Z forward; positive yaw turns +Z toward +X. Ground anchor Y {FLIGHT_MODEL.ground_y.toFixed(8)}. Speed ≤ 0.18 horizontal / 0.16 vertical units/s; accelerations 0.45 / 0.32 units/s²; turn ≤ 0.8 rad/s. Velocity-first fixed 20 ms integration. No random input, lift or gravity. Floor/ceiling/wall clamps cancel the affected velocity.</p>
      <p>Commands apply at interval-start boundaries. Result and transitions become available at the next completed boundary. Takeoff requires grounded; landing requires takeoff/flying; invalid intents are logged and rejected. A landing command decelerates forward motion and descends at 0.12 units/s. Ground contact establishes grounded state. No position keyframes. Seek reads recorded boundaries without executing the plant.</p>
      <ol>{trial.commands.map(c => <li key={c.id}>{(c.step * .02).toFixed(2)} s / step {c.step}: {c.id} · {c.intent} · forward {c.forward}, turn {c.turn}, vertical {c.vertical}</li>)}</ol>
      <p>Events at recorded boundaries:</p><ul>{events.filter(e => e.time <= frame.time).map((e, i) => <li key={i}>{e.time.toFixed(2)} s · {e.kind} · {e.detail}</li>)}</ul>
      <p>Conservative full-specimen clearance: horizontal radius 0.28, upper extent 0.24 units. Stable original leg posture during this independent flight experiment; v6 walking and the v7 motor projection remain separate. Exported flight files are ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT and never enter My Experiments.</p>
    </details>
  </section>;
}
