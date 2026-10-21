"use client";
import { useEffect, useMemo, useRef, useState } from 'react';
import { FlyViewer } from './FlyViewer';
import { loadNeuralLocomotion, type NeuralArtifact } from '@/lib/neuralLocomotion';
import { FlightClock, createFlightTrial, flightScene, FLIGHT_MODEL } from '@/lib/engineeringFlight';
import { flightWingsV8 } from '@/lib/flightWingsV8';
import { compareRecordedFlights, type FlightTrajectoryDisplay } from '@/lib/flightTrajectory';
import { NeuralFlightEngine, NEURAL_FLIGHT_CONDITIONS, NEURAL_FLIGHT_LIMITATION, NEURAL_YAW, exportNeuralFlight, importNeuralFlight, saveNeuralFlight, openNeuralFlight, type NeuralFlightCondition } from '@/lib/neuralFlight';

type Pair = Record<NeuralFlightCondition, NeuralFlightEngine>;
const labels = { OFF: 'Neural Steering OFF', ON: 'Neural Steering ON', ZERO: 'Projection-zero control', VISUAL_PERTURBATION: 'ON · Visual plane −0.4' };
function makePair(authority: NeuralArtifact): Pair { return Object.fromEntries(NEURAL_FLIGHT_CONDITIONS.map(c => [c, new NeuralFlightEngine(authority, c)])) as Pair; }
export function NeuralFlightArena() {
  const authority = useRef<NeuralArtifact | null>(null), pair = useRef<Pair | null>(null), clock = useRef(new FlightClock()), cursor = useRef(0);
  const [runs, setRuns] = useState<Pair | null>(null);
  const ready = Boolean(runs);
  const [condition, setCondition] = useState<NeuralFlightCondition>('OFF');
  const [step, setStep] = useState(0), [frontier, setFrontier] = useState(0), [playing, setPlaying] = useState(false), [generation, setGeneration] = useState(0);
  const [compare, setCompare] = useState(true), [error, setError] = useState(''), [notice, setNotice] = useState(''), [cost, setCost] = useState(0), [identity, setIdentity] = useState('');
  useEffect(() => {
    let active = true;
    loadNeuralLocomotion().then(data => { if (active) { authority.current = data.authority; pair.current = makePair(data.authority); setRuns(pair.current); } }).catch(e => { if (active) setError(String(e)); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (!playing || !ready) return;
    let raf = 0, previous: number | null = null;
    const tick = (now: number) => {
      if (previous !== null && pair.current) {
        try {
          const start = performance.now(), current = pair.current;
          clock.current.advance({ stopStep: 600, snapshot: () => ({ step: cursor.current }), advance: () => {
            if (cursor.current === current.OFF.snapshot().step) for (const c of NEURAL_FLIGHT_CONDITIONS) current[c].advance();
            cursor.current++;
          } }, now - previous);
          setStep(cursor.current); setFrontier(current.OFF.snapshot().step); setCost(performance.now() - start);
          if (cursor.current === 600) { setPlaying(false); return; }
        } catch (e) { setError(String(e)); setPlaying(false); return; }
      }
      previous = now; raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick); return () => cancelAnimationFrame(raf);
  }, [playing, ready]);
  function reset() {
    setPlaying(false); clock.current.reset(); cursor.current = 0;
    if (authority.current) { pair.current = makePair(authority.current); setRuns(pair.current); }
    setStep(0); setFrontier(0); setGeneration(n => n + 1); setIdentity(''); setNotice(''); setError('');
  }
  function seek(n: number) { setPlaying(false); clock.current.reset(); cursor.current = n; setStep(n); }
  async function fileAction(action: 'export' | 'save' | 'open', file?: File) {
    setPlaying(false); clock.current.reset(); setError('');
    try {
      if (!pair.current || !authority.current) throw new Error('Pinned neural source unavailable');
      const start = performance.now();
      if (file || action === 'open') {
        if (file && file.size > 10_000_000) throw new Error('Neural flight artifact exceeds 10 MB');
        const verified = file ? await importNeuralFlight(authority.current, JSON.parse(await file.text())) : await openNeuralFlight(localStorage, authority.current, condition);
        const next = makePair(authority.current), boundary = verified.snapshot().step;
        next[verified.config.condition] = verified;
        for (const c of NEURAL_FLIGHT_CONDITIONS) while (next[c].snapshot().step < boundary) next[c].advance();
        pair.current = next; setRuns(next); setCondition(verified.config.condition); cursor.current = boundary; setStep(boundary); setFrontier(boundary); setGeneration(n => n + 1);
        const run = await exportNeuralFlight(verified); setIdentity(run.artifact_id);
        setNotice(`Verified inputs, neural states and flight history reconstructed in ${(performance.now() - start).toFixed(1)} ms.`);
      } else {
        const engine = pair.current[condition];
        if (action === 'save') {
          await saveNeuralFlight(localStorage, engine, step);
          setNotice('Completed snapshot saved locally for this condition. Origin-local; JSON export transfers between origins.');
        } else {
          const run = await exportNeuralFlight(engine, step); setIdentity(run.artifact_id);
          const url = URL.createObjectURL(new Blob([JSON.stringify(run)], { type: 'application/json' }));
          const link = document.createElement('a'); link.href = url; link.download = `neurofly-neural-flight-v9-${condition}.json`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
          setNotice(`Verified recorded prefix exported · ${step * 200} neural substeps.`);
        }
      }
    } catch (e) { setError(String(e)); }
  }
  const engine = runs?.[condition] ?? null;
  const frame = engine?.frame(step) ?? createFlightTrial().initial;
  const frames = useMemo(() => engine?.frames().slice(0, frontier + 1) ?? [createFlightTrial().initial], [engine, frontier]);
  const offFrames = useMemo(() => runs ? runs.OFF.frames().slice(0, frontier + 1) : [createFlightTrial().initial], [runs, frontier]);
  const records = useMemo(() => engine?.records(step) ?? [], [engine, step]);
  const latest = records.at(-1);
  const separation = compareRecordedFlights(frames, offFrames, step, 600, 600);
  const flightTrajectory: FlightTrajectoryDisplay | undefined = engine ? { current: { id: `v9:${condition}:${generation}`, trial: engine.config.trial, frames }, reference: compare && condition !== 'OFF' ? { id: `v9:OFF:${generation}`, trial: engine.config.trial, frames: offFrames } : undefined, cursorStep: step, fullRecorded: false } : undefined;
  const wings = flightWingsV8(frame.time, frame.state, Math.max(0, frame.position[1] - FLIGHT_MODEL.ground_y), 'normal');
  const chart = (read: (r: typeof records[number]) => number, scale: number) => records.map(r => `${(r.available_time / 12 * 600).toFixed(2)},${(40 - read(r) * scale).toFixed(2)}`).join(' ');
  return <section className="arena-replay-panel neural-flight" aria-label="Experimental Neural Flight Steering v9">
    <h2>Experimental Neural Flight Steering v9</h2>
    <p>{NEURAL_FLIGHT_LIMITATION}</p>
    <p>Horizontal visual projection: XZ and yaw only; altitude excluded. Each condition calculates its own observations and neural states. Forward, vertical, TAKEOFF and LAND remain engineering commands.</p>
    {!ready && !error ? <p role="status">Verifying pinned HS/DNp15 source…</p> : null}
    {error ? <p role="alert">{error} No substitute activity or flight path is generated.</p> : null}
    {notice ? <p role="status">{notice}</p> : null}
    <div className="arena-replay-controls">
      <label>Condition <select aria-label="Neural flight condition" value={condition} disabled={!ready || playing} onChange={e => { setCondition(e.target.value as NeuralFlightCondition); setIdentity(''); }}>{NEURAL_FLIGHT_CONDITIONS.map(c => <option key={c} value={c}>{labels[c]}</option>)}</select></label>
      <label><input type="checkbox" checked={compare} onChange={e => setCompare(e.target.checked)}/> Compare with Neural OFF</label>
    </div>
    <p className="neural-flight-legend">Cyan — {labels[condition]}{compare && condition !== 'OFF' ? ' · Gold — independently computed Neural OFF' : ''} · World-space recorded XYZ</p>
    <FlyViewer arena replayPose={flightScene(frame)} stimulusPlane={engine?.config.visual.plane_z ?? .4} flightPresentation={wings} flightTrajectory={flightTrajectory} flightDisclosure={NEURAL_FLIGHT_LIMITATION} presentationLabel="v9 / Causal model computation + recorded replay" playbackControls={<div className="arena-replay-controls">
      <button disabled={!ready || playing || step === 600} onClick={() => { clock.current.reset(); setPlaying(true); }}>{step ? 'Resume' : 'Play'}</button>
      <button disabled={!playing} onClick={() => setPlaying(false)}>Pause</button><button disabled={!ready} onClick={reset}>Reset</button>
      <output data-neural-flight-frame={JSON.stringify(frame)} data-neural-flight-interval={JSON.stringify(latest ?? null)} data-neural-flight-condition={condition} data-neural-flight-separation={separation?.separation ?? 0}>{frame.time.toFixed(2)} / 12.00 s · {frame.state} · {step === 600 ? 'Completed' : `Recorded through ${(frontier * .02).toFixed(2)} s`}</output>
    </div>}/>
    <label>Recorded flight time <input aria-label="Neural flight time" type="range" min={0} max={frontier * .02} step={.02} value={step * .02} disabled={!ready || !frontier} onChange={e => seek(Math.round(Number(e.target.value) / .02))}/></label>
    <dl className="arena-course-telemetry">
      <div><dt>Position XYZ · presentation units</dt><dd>{frame.position.map(x => x.toFixed(9)).join(' / ')}</dd></div>
      <div><dt>Velocity XYZ · units/s; heading rad</dt><dd>{frame.velocity.map(x => x.toFixed(5)).join(' / ')} · {frame.heading.toFixed(9)}</dd></div>
      <div><dt>Neural OFF separation · current / final</dt><dd>{separation?.separation.toFixed(10) ?? 'Unavailable'} / {separation?.finalSeparation?.toFixed(10) ?? 'Not completed'}</dd></div>
      <div><dt>Last accepted interval · causal availability</dt><dd>{latest ? `${latest.time.toFixed(2)} → ${latest.available_time.toFixed(2)} s; observation from prior completed motion` : 'No accepted neural interval yet'}</dd></div>
      <div><dt>HS R / L · proxy model state</dt><dd>{latest ? `${latest.after.hs.slice(0,3).map(x=>x.toExponential(5)).join(' / ')} | ${latest.after.hs.slice(3).map(x=>x.toExponential(5)).join(' / ')}` : 'Initial zero state'}</dd></div>
      <div><dt>DNp15 R / L; mean R−L readout · yaw_drive_eq</dt><dd>{latest ? `${latest.after.dn.map(x=>x.toExponential(7)).join(' / ')}; ${latest.before.mean_yaw_drive_eq?.toExponential(7)}` : 'Initial zero state'}</dd></div>
      <div><dt>Observed R / L · normalized horizontal descriptor</dt><dd>{latest?.observation ? `${latest.observation.right.toExponential(7)} / ${latest.observation.left.toExponential(7)}` : 'No preceding motion'}</dd></div>
      <div><dt>Turn input · engineering / neural / combined</dt><dd>{latest ? `${latest.engineering.turn.toFixed(7)} / ${latest.yaw.neuralTurn.toFixed(7)} / ${latest.yaw.appliedTurn.toFixed(7)}; clamps ${latest.yaw.projectionClamped}/${latest.yaw.combinedClamped}` : 'No accepted input'}</dd></div>
      <div><dt>Execution · neural substeps / last paired batch</dt><dd>{latest?.after.substeps ?? 0} / {cost.toFixed(2)} ms · Normal Wingbeat 12 Hz</dd></div>
    </dl>
    <figure className="neural-flight-timeline"><figcaption>Accepted neural intervals only · cyan R−L readout (× 3000), gold projected turn (× 45); fixed 12 s axis</figcaption><svg viewBox="0 0 600 80" role="img" aria-label="Neural readout and engineering yaw timeline"><path d="M0 40H600" stroke="currentColor" opacity=".25"/><polyline points={chart(r => r.before.mean_yaw_drive_eq ?? 0, 3000)} fill="none" stroke="#50cddd"/><polyline points={chart(r => r.yaw.neuralTurn, 45)} fill="none" stroke="#e2b96e"/></svg></figure>
    <div className="arena-replay-controls"><button disabled={!ready || playing} onClick={() => void fileAction('export')}>Export v9 run</button><button disabled={step !== 600 || playing} onClick={() => void fileAction('save')}>Save completed v9</button><button disabled={!ready || playing} onClick={() => void fileAction('open')}>Reopen saved condition</button><label>Import v9 run <input aria-label="Import v9 run" type="file" accept="application/json,.json" disabled={!ready || playing} onChange={e => { const f = e.target.files?.[0]; if(f) void fileAction('open', f); e.target.value=''; }}/></label></div>
    {identity ? <p className="arena-artifact-id">Verified v9 artifact: {identity}</p> : null}
    <details><summary>Source, timing and projection assumptions</summary><p>MALECNS_CONNECTOME_EVIDENCE: male-cns:v1.0 · UUID 4b2087c0fbe046bfaf0d60bc970e3e5d. HS R 10015/10016/10023 → DNp15 R 11215 (138/122/23 structural contacts); HS L 10034/10181/10419 → DNp15 L 12069 (78/126/14). Counts do not establish synaptic sign or motor calibration.</p><p>MODELED_NEURAL_DYNAMICS: existing Python-authoritative HS/DNp15 proxy equations, unit mean transfer, zero initial state. 200 old-state substeps × 0.1 ms per 20 ms body interval. Observation of completed interval i−1→i is held while neural state advances over i→i+1; its integrated readout supplies the accepted yaw command for that same body interval. No future pose or render-clock input.</p><p>ENGINEERING_FLIGHT_CONTROL_PROJECTION: Δq = sum of existing kernel increments. ω = clamp(2.5 × Δq / 0.020, −0.5, +0.5) rad/s. Neural turn = ω / 0.8; OFF and projection-zero set this contribution to zero. Applied turn = clamp(engineering turn + neural turn, −1, +1). Positive DN right−left turns heading toward +X. Engineering units, no physiological yaw calibration.</p><p>ENGINEERING_HORIZONTAL_VISUAL_PROJECTION: existing landmarks X=±0.6, Z=+0.4; perturbation uses the previously validated static Z=−0.4 world. Y altitude ignored. Model observation is a geometric bearing-change proxy, not full 3D retinal optic flow. ENGINEERING_FLIGHT_PLANT: unchanged v8 integration, contacts and 12-second command program; no neural altitude, thrust or landing decisions.</p><p className="arena-artifact-id">Source raw SHA-256: {engine?.config.neural.source_raw_sha256}<br/>Neural contract: {engine?.config.neural.source_sha256.neural}<br/>Projection identity: {NEURAL_YAW.identity}</p><p>One compact, reconstructable completed snapshot per condition in a separate origin-local store. Invalid files are rejected through full neural/body reconstruction. No cloud storage or changes to historical session libraries.</p></details>
  </section>;
}
