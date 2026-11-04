"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useState, useTransition } from "react";
import { loadScenarioPlayback } from "@/app/scenarios/actions";
import { ScenarioExplanation } from "./ScenarioExplanation";
import { HorizontalMotionExplanation } from "./HorizontalMotionExplanation";
import { CourseControlExplanation } from "./CourseControlExplanation";
import { scenarioCopy, experimentMetadata } from "@/lib/scenarioPresentation";
import { WebGLGate } from "./WebGLGate";
import { CurrentResult } from "./CurrentResult";
import { GuidedCaptions, type Caption } from "./GuidedCaptions";
import { ProvenanceLabel, KindBadge } from "@/components/ui";
import { MALECNS_RELEASE } from "@/content/science-copy";
import styles from "./ScenarioDetail.module.css";
import { ScientificTrace } from "./ScientificTrace";
import { ScientificPlaybackLoading, ScientificPlaybackUnavailable, UnitHelp, PlaybackPhases } from "./ScientificInstrument";
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
  const meta = experimentMetadata[result.scenario.id];
  const captions: Caption[] = [
    { title: "Start of the run", text: scenarioCopy[result.scenario.id].observation, step: 0 },
    { title: "Stored model state", text: "Every frame is a stored model state with its model time. Scrubbing replays the record; no simulation runs in your browser.", step: Math.floor(last / 2) },
    { title: "End of the run", text: `Recorded outcome: ${meta.outcome}. ${meta.limit}`, step: last },
  ];
  const goTo = (step: number) => { setPlaying(false); setCursor(Math.max(0, Math.min(last, step))); };
  return <div className="scientific-playback">
    <GuidedCaptions captions={captions} onGoTo={goTo}/>
    <div className="experiment-main">
      <div className="experiment-viewport"><WebGLGate hasDataAlternative>{isCoursePlayback(result) ? <><CourseControlWorld result={result} cursor={cursor}/><ScientificTrace result={result} step={frame.step}/></> : isNeuralPlayback(result) ? <HorizontalMotionWorld result={result} cursor={cursor}/> : <ScenarioWorld result={result} cursor={cursor} />}</WebGLGate></div>
      <CurrentResult result={result} step={frame.step}/>
    </div>
    <section className="scenario-transport" aria-label="Playback controls">
      <div className="scenario-control-row">
        <button onClick={() => { if (cursor >= last) setCursor(0); setPlaying(!isPlaying); }} aria-label={isPlaying ? "Pause playback" : "Play playback"}>{isPlaying ? "Pause" : "Play"}</button>
        <button onClick={() => { setPlaying(false); setCursor(0); }}>Reset</button>
        <span>Boundary {frame.step} / {last} · <strong>{frame.time_ms.toFixed(1)} ms</strong> scientific time</span>
      </div>
      <label htmlFor="scenario-timeline">Scrub scientific boundary</label>
      <input id="scenario-timeline" type="range" min={0} max={last} step={1} value={Math.floor(cursor)} onChange={e => { setPlaying(false); setCursor(Number(e.target.value)); }} />
      <small>{result.duration_ms.toFixed(1)} ms simulation shown over 6 s playback · rendering only, scientific time unchanged</small>
      <PlaybackPhases result={result}/>
    </section>
    <div className="experiment-explanation">{isCoursePlayback(result) ? <CourseControlExplanation result={result} frame={result.frames[frame.step]}/> : isNeuralPlayback(result) ? <HorizontalMotionExplanation result={result} frame={result.frames[frame.step]}/> : <ScenarioExplanation result={result} frame={result.frames[frame.step]} />}<UnitHelp/></div>
  </div>;
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
        // A reload of this URL asks the backend to replay the same scenario again.
        window.history.replaceState(null, "", `/scenarios/${scenario.id}?replay=canonical`);
      }
    } catch { setError("Backend connection failed. No substitute simulation was loaded."); }
  }
  const meta = experimentMetadata[scenario.id];
  return <>
    <div className={styles.bar}>
      <Link className={styles.back} href="/scenarios" prefetch={false}>← Scenarios</Link>
      <button type="button" className={styles.run} disabled={running} onClick={() => startTransition(run)}>{running ? "Preparing the recorded replay…" : result ? "Replay again" : "Replay canonical scenario"}</button>
    </div>
    <div className={styles.facts}><span>{meta.duration} horizon</span><span>{meta.input}</span><span>{meta.scope}</span></div>
    <div className={`scenario-route ${styles.stage}`} data-theme-scope="dark">
      {running && <ScientificPlaybackLoading/>}
      {error && <ScientificPlaybackUnavailable detail={error} retry={()=>startTransition(run)}/>}
      {!result && !running && !error && <section className="scenario-ready"><p className="eyebrow">READY TO OBSERVE</p><h2>Press Replay to load the recorded run</h2><p>{scenario.scientific_caveat}</p><p>Replay loads the integrity-checked recorded result. No local physics or fallback animation.</p></section>}
      {result && <Playback key={`${result.run_id}-${revision}`} result={result} />}
    </div>
    <div className={styles.columns}>
      <section aria-labelledby="happens">
        <h2 id="happens">What happens</h2>
        <p>{copy.observation}</p>
        <h2 id="notice" className={styles.second}>What to notice</h2>
        <p>{meta.purpose} {meta.limit}</p>
        <p className={styles.small}>Everything on the stage is stored model state, not a measurement of a fly.</p>
      </section>
      <section aria-labelledby="provenance" className={styles.card}>
        <h2 id="provenance">Provenance</h2>
        <dl>
          <div><dt>Stimulus</dt><dd>{meta.input}</dd></div>
          <div><dt>Circuit</dt><dd>{meta.scope}</dd></div>
          <div><dt>Kind</dt><dd>{meta.kind}</dd></div>
          <div><dt>Status</dt><dd><KindBadge kind="not-evaluated"/></dd></div>
        </dl>
        {result ? <ProvenanceLabel variant="card" kind="model-state" source={MALECNS_RELEASE} status="NOT_EVALUATED" artifactId={result.artifact_id}/> : <p className={styles.small}>Run IDs appear after the replay loads.</p>}
      </section>
    </div>
    <p className={styles.next}>Next: <Link href="/experiments" prefetch={false}>See the published experiments</Link>. The list cannot be filtered by scenario yet.</p>
  </>;
}
