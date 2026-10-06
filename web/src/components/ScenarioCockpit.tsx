"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useState, useTransition } from "react";
import { loadScenarioPlayback } from "@/app/scenarios/actions";
import { ScenarioExplanation } from "./ScenarioExplanation";
import { HorizontalMotionExplanation } from "./HorizontalMotionExplanation";
import { CourseControlExplanation } from "./CourseControlExplanation";
import { scenarioCopy } from "@/lib/scenarioPresentation";
import { advanceScenarioCursor, isNeuralPlayback, isCoursePlayback, type ScenarioDefinition, type ScenarioPlayback } from "@/lib/scenarioPlayback";

const ScenarioWorld = dynamic(() => import("@/components/ScenarioWorld"), { ssr: false, loading: () => <div className="scenario-world" role="status">Preparing 3D view…</div> });
const HorizontalMotionWorld = dynamic(() => import("@/components/HorizontalMotionWorld"), {ssr:false,loading:()=><div className="scenario-world" role="status">Preparing motion presentation…</div>});
const CourseControlWorld = dynamic(() => import("@/components/CourseControlWorld"), {ssr:false,loading:()=><div className="scenario-world" role="status">Preparing orientation presentation…</div>});

function Playback({ result }: { result: ScenarioPlayback }) {
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
  const frame = result.frames[Math.floor(Math.max(0, Math.min(last,cursor)))];
  return <>
    {isCoursePlayback(result) ? <CourseControlWorld result={result} cursor={cursor}/> : isNeuralPlayback(result) ? <HorizontalMotionWorld result={result} cursor={cursor}/> : <ScenarioWorld result={result} cursor={cursor} />}
    <section className="scenario-transport" aria-label="Playback controls">
      <div className="scenario-control-row">
        <button onClick={() => { if (cursor >= last) setCursor(0); setPlaying(!isPlaying); }} aria-label={isPlaying ? "Pause playback" : "Play playback"}>{isPlaying ? "Pause" : "Play"}</button>
        <button onClick={() => { setPlaying(false); setCursor(0); }}>Reset</button>
        <span>Boundary {frame.step} / {last} · <strong>{frame.time_ms.toFixed(1)} ms</strong> scientific time</span>
      </div>
      <label htmlFor="scenario-timeline">Scientific boundary</label>
      <input id="scenario-timeline" type="range" min={0} max={last} step={1} value={Math.floor(cursor)} onChange={e => { setPlaying(false); setCursor(Number(e.target.value)); }} />
      <small>{result.duration_ms.toFixed(1)} ms simulation shown over 6 s playback · rendering only, scientific time unchanged</small>
      {isCoursePlayback(result) && <small>0→1: external perturbation · 1→500: feedback evolution · 500: experiment ends at a residual offset</small>}
    </section>
    {isCoursePlayback(result) ? <CourseControlExplanation result={result} frame={result.frames[frame.step]}/> : isNeuralPlayback(result) ? <HorizontalMotionExplanation result={result} frame={result.frames[frame.step]}/> : <ScenarioExplanation result={result} frame={result.frames[frame.step]} />}
  </>;
}

export function ScenarioCockpit({ scenario, initialResult = null, initialError = null }: { scenario: ScenarioDefinition; initialResult?: ScenarioPlayback | null; initialError?: string | null }) {
  const [result, setResult] = useState<ScenarioPlayback | null>(initialResult);
  const copy = scenarioCopy[scenario.id];
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
    <header className="scenario-heading"><div><p className="eyebrow">{copy.role}</p><h1>{scenario.title}</h1><p>{scenario.description}</p></div>
      <button className="scenario-run" disabled={running} onClick={() => startTransition(run)}>{running ? "Preparing validated replay…" : result ? "Run again" : "Run canonical preset"}</button>
    </header>
    {running && <p role="status" className="scenario-pending">Replaying the frozen scientific model and validating source provenance. This can take several seconds.</p>}
    {error && <p role="alert" className="scenario-error">{copy.failureNote && <><strong>{copy.failureNote}</strong><br/></>}{error} Retry Run when the scientific backend is available.</p>}
    {!result && !running && !error && <section className="scenario-ready"><p className="eyebrow">READY TO OBSERVE</p><h2>Backend state. Honest outcomes.</h2><p>{scenario.scientific_caveat}</p><p>Run loads the numerically replay-validated canonical result. No local physics or fallback animation.</p></section>}
    {result && <Playback key={`${result.run_id}-${revision}`} result={result} />}
  </main>;
}
