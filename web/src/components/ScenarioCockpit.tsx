"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useState, useTransition } from "react";
import { loadScenarioPlayback } from "@/app/scenarios/actions";
import { advanceScenarioCursor, scenarioScene, type ScenarioDefinition, type ScenarioPlaybackResult } from "@/lib/scenarioPlayback";

const ScenarioWorld = dynamic(() => import("@/components/ScenarioWorld"), { ssr: false, loading: () => <div className="scenario-world" role="status">Preparing 3D view…</div> });

function Playback({ result }: { result: ScenarioPlaybackResult }) {
  const [cursor, setCursor] = useState(0);
  const [playing, setPlaying] = useState(false);
  const last = result.frames.length - 1;
  const isPlaying = playing && cursor < last;
  useEffect(() => {
    if (!isPlaying) return;
    let frame = 0, previous: number | null = null;
    const tick = (now: number) => {
      if (previous !== null) {
        const elapsed = now - previous;
        setCursor(c => advanceScenarioCursor(c, elapsed, true, last));
      }
      previous = now;
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [isPlaying, last]);
  const { frame } = scenarioScene(result, cursor);
  const statuses = result.statuses;
  return <>
    <ScenarioWorld result={result} cursor={cursor} />
    <section className="scenario-transport" aria-label="Playback controls">
      <div className="scenario-control-row">
        <button onClick={() => { if (cursor >= last) setCursor(0); setPlaying(!isPlaying); }} aria-label={isPlaying ? "Pause playback" : "Play playback"}>{isPlaying ? "Pause" : "Play"}</button>
        <button onClick={() => { setPlaying(false); setCursor(0); }}>Reset</button>
        <span>Boundary {frame.step} / {last} · <strong>{frame.time_ms.toFixed(1)} ms</strong> scientific time</span>
      </div>
      <label htmlFor="scenario-timeline">Scientific boundary</label>
      <input id="scenario-timeline" type="range" min={0} max={last} step={1} value={Math.floor(cursor)} onChange={e => { setPlaying(false); setCursor(Number(e.target.value)); }} />
      <small>Six seconds of presentation playback · {result.duration_ms.toFixed(1)} ms simulated · visual interpolation only</small>
    </section>
    <section className="scenario-interpretation" aria-label="Scientific interpretation">
      <p className="eyebrow">{statuses.closed_loop_execution_completed ? "CLOSED LOOP EXECUTED" : "EXECUTION INCOMPLETE"}</p>
      <h2>{statuses.body_movement_occurred ? "Body movement recorded." : "Stationary is an honest result."}</h2>
      <p>{result.scenario.id === "BASELINE_CONTROL" ? "Stimulus disabled. The neutral control has zero sensory exposure and no genuine motor actuation or body movement." : "Closed-loop causal execution completed. The looming stimulus changed sensory activity, but the pinned DNp01 model produced no spikes; no genuine motor actuation or body movement occurred."}</p>
      <div className="scenario-statuses">{Object.entries(statuses).map(([key, value]) => <span key={key}>{key.replaceAll("_", " ")}: <strong>{value ? "yes" : "no"}</strong></span>)}</div>
    </section>
    <section className="scenario-telemetry" aria-label="Scientific telemetry">
      <div><p className="eyebrow">WORLD / PROJECTION</p><h3>{frame.relative_distance_world_eq?.toFixed(3) ?? "—"} <small>world_eq distance</small></h3><p>Lattice radius: {frame.lattice_radius ?? "disabled"} · Exposed bodies: <strong>{frame.active_sensory_body_count} / 311</strong></p></div>
      <div><p className="eyebrow">DNp01 / EXACT MODEL BOUNDARY</p><h3>{result.total_dnp01_spikes} <small>total spikes</small></h3>{result.dnp01_body_ids.map((id, i) => <p key={id}>{id}: {frame.dnp01_membrane_mv[i].toFixed(6)} <small>model membrane coordinate</small></p>)}</div>
      <div><p className="eyebrow">ACTUATOR / DIMENSIONLESS</p><h3>R {frame.actuator_commands.RIGHT_TTM_ACTUATOR.toFixed(3)} · L {frame.actuator_commands.LEFT_TTM_ACTUATOR.toFixed(3)}</h3><p>Genuine actuation: {statuses.genuine_nonzero_actuation_occurred ? "yes" : "none"}</p></div>
      <div><p className="eyebrow">BODY / AUTHORITATIVE</p><h3>({frame.body.x_world_eq.toFixed(3)}, {frame.body.z_world_eq.toFixed(3)})</h3><p>x / z world_eq · Movement: <strong>{statuses.body_movement_occurred ? "yes" : "none"}</strong></p></div>
      <div className="scenario-sensory"><p className="eyebrow">SENSORY MODEL STATE SUMS / EXACT BOUNDARY</p>{frame.sensory_summaries.map(s => <span key={`${s.neuron_type}-${s.side}`}>{s.neuron_type} {s.side}: {s.state_sum.toFixed(5)}</span>)}</div>
    </section>
    <details className="scenario-details"><summary>Scientific provenance & limitations</summary>
      <p>Source: {result.source_operation}. Detailed 311-identity scientific state remains in the research artifact, not the playback payload.</p>
      <p className="scenario-hash">Artifact: {result.artifact_id}<br />Run: {result.run_id}</p>
      <ul>{result.scientific_limitations.map(s => <li key={s}>{s}</li>)}</ul>
    </details>
  </>;
}

export function ScenarioCockpit({ scenario, initialResult = null, initialError = null }: { scenario: ScenarioDefinition; initialResult?: ScenarioPlaybackResult | null; initialError?: string | null }) {
  const [result, setResult] = useState<ScenarioPlaybackResult | null>(initialResult);
  const [running, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(initialError);
  const [revision, setRevision] = useState(0);
  async function run() {
    setError(null); setResult(null);
    try {
      const response = await loadScenarioPlayback(scenario.id);
      if ("error" in response) setError(response.error);
      else {
        setResult(response.result); setRevision(r => r + 1);
        // A reload of this URL asks the backend to validate the same preset again.
        window.history.replaceState(null, "", `/scenarios/${scenario.id}?replay=canonical`);
      }
    } catch { setError("Backend connection failed. No substitute simulation was loaded."); }
  }
  return <main className="scenario-route">
    <Link className="back-link" href="/scenarios">← scenarios</Link>
    <header className="scenario-heading"><div><p className="eyebrow">AUTHORITATIVE SCIENTIFIC PLAYBACK</p><h1>{scenario.title}</h1><p>{scenario.description}</p></div>
      <button className="scenario-run" disabled={running} onClick={() => startTransition(run)}>{running ? "Preparing validated replay…" : result ? "Run again" : "Run canonical preset"}</button>
    </header>
    {running && <p role="status" className="scenario-pending">Recomputing the canonical causal loop and validating source provenance. This can take several seconds.</p>}
    {error && <p role="alert" className="scenario-error">{error} Retry Run when the scientific backend is available.</p>}
    {!result && !running && !error && <section className="scenario-ready"><p className="eyebrow">READY TO OBSERVE</p><h2>Backend state. Honest outcomes.</h2><p>{scenario.scientific_caveat}</p><p>Run loads the numerically replay-validated canonical result. No local physics or fallback animation.</p></section>}
    {result && <Playback key={`${result.run_id}-${revision}`} result={result} />}
  </main>;
}
