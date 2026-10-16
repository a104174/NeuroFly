"use client";

import Link from "next/link";
import { ARENA, ARENA_RESET_VIEW, type ArenaCameraView } from "@/lib/experimentalArena";
import dynamic from "next/dynamic";
import { useCallback, useState, type ReactNode } from "react";
import type { ArenaOverlayProps } from "./ArenaComparison";
import type { ViewerStats } from "./FlyViewerCanvas";
import { FLY_VIEWER_ASSET, type FlyViewerView } from "@/lib/flyViewer";

const FlyViewerCanvas = dynamic(() => import("./FlyViewerCanvas"), { ssr: false, loading: () => <p className="fly-viewer-message">Preparing the studio…</p> });
const views: { id: FlyViewerView; label: string }[] = [{ id: "three-quarter", label: "Overview" }, { id: "lateral", label: "Side" }, { id: "head", label: "Front" }, { id: "dorsal", label: "Top" }];
export function FlyViewer({ arena = false, replayPose, locomotion = false, locomotionVersion = "v0", stimulusPlane, stimulusX, trajectory, liveTrajectory, comparison, playbackControls, scientificTimeline }: { arena?: boolean; locomotion?: boolean; locomotionVersion?: "v0" | "v1" | "v2" | "v3" | "v3.1" | "v4"; stimulusPlane?: number; stimulusX?: number[]; trajectory?: [number, number, number][]; liveTrajectory?: [number, number, number][]; comparison?: ArenaOverlayProps; playbackControls?: ReactNode; scientificTimeline?: ReactNode; replayPose?: import("@/lib/arenaCourseReplay").ArenaCoursePose }) {
  const [tableReady, setTableReady] = useState(false);
  const onTableReady = useCallback(() => setTableReady(true), []);
  const [view, setView] = useState<ArenaCameraView>("three-quarter");
  const [reset, setReset] = useState(0);
  const [status, setStatus] = useState<{ state: "loading" | "ready" | "error"; detail?: string }>({ state: "loading" });
  const [diagnostics, setDiagnostics] = useState(false);
  const [stats, setStats] = useState<ViewerStats | null>(null);
  const onStatus = useCallback((value: { state: "loading" | "ready" | "error"; detail?: string }) => setStatus(previous => previous.state === "error" ? previous : value), []);
  const onFailure = useCallback((detail: string) => setStatus({ state: "error", detail }), []);
  const provenance = FLY_VIEWER_ASSET.provenance;
  return <>
    <section className={`fly-viewer-stage${arena ? " arena-viewer-stage" : ""}${locomotion ? " locomotion-viewer-stage" : ""}`} aria-label={arena ? "Controlled chamber visual prototype" : "Interactive male Drosophila visual asset"}>
      <FlyViewerCanvas arena={arena} replayPose={arena ? replayPose : undefined} locomotion={locomotion} stimulusPlane={stimulusPlane} stimulusX={stimulusX} trajectory={trajectory} liveTrajectory={liveTrajectory} comparison={comparison} onTableReady={onTableReady} view={view} reset={reset} diagnostics={diagnostics} onStatus={onStatus} onStats={setStats} onFailure={onFailure} />
      <div className="fly-viewer-caption"><span>V2-F / MALE DROSOPHILA</span><small>{arena ? locomotion ? locomotionVersion === "v4" ? comparison ? "Moving stimulus v4 / Recomputed counterfactual replay" : "Moving stimulus v4 / Live browser model" : locomotionVersion === "v3.1" ? "Neural ON/OFF / Recomputed counterfactual replay" : locomotionVersion === "v3" ? "Continuous v3 / Live neural + engineering navigation" : locomotionVersion === "v2" ? "Interactive v2 / Live browser model" : `Experimental Locomotion ${locomotionVersion} / Precomputed replay` : replayPose ? "A+C v0.2 / Course orientation replay" : "A+C v0.1 / Controlled chamber" : "Static visual specimen"}</small></div>
      {comparison ? <div className="comparison-stage-legend" aria-label="Comparison condition legend">{comparison.states.map(s=><span key={s.key} style={{color:s.color}}>{s.symbol} {s.key}{comparison.focus === s.key ? " · focus" : ""}</span>)}</div> : null}
      {playbackControls ? <div className="fly-viewer-playback">{playbackControls}</div> : null}
      {(status.state !== "ready" || (arena && !tableReady)) ? <div className="fly-viewer-message" role={status.state === "error" ? "alert" : "status"}>
        <strong>{status.state === "error" ? "The specimen could not be displayed." : arena ? "Preparing the chamber and specimen…" : "Loading the specimen…"}</strong>
        {status.detail ? <p>{status.detail}</p> : null}
        {status.state === "error" ? <button onClick={() => window.location.reload()}>Reload viewer</button> : null}
      </div> : null}
      <div className="fly-viewer-toolbar" aria-label="Camera controls">
        <div className="fly-viewer-views">{(arena ? [...views, { id: "inspect" as const, label: "Inspect Fly" }] : views).map(item => <button key={item.id} aria-pressed={view === item.id} onClick={() => { setView(item.id); setReset(n => n + 1); }}>{item.label}</button>)}</div>
        <button onClick={() => { setView(ARENA_RESET_VIEW); setReset(n => n + 1); }} title="Return to the default overview">Reset view</button>
      </div>
      {diagnostics && stats ? <output data-render-stimulus={JSON.stringify(stats.stimulusPositions)} data-comparison-marker-positions={JSON.stringify(stats.comparisonMarkers)} data-render-body-yaw={stats.bodyYaw} data-render-body-position={JSON.stringify(stats.bodyPosition)} data-camera-position={JSON.stringify(stats.cameraPosition)} data-camera-target={JSON.stringify(stats.cameraTarget)} className="fly-viewer-stats" aria-label="Measured renderer statistics">{stats.fps.toFixed(0)} FPS (approx.) · {stats.calls} calls · {stats.triangles.toLocaleString()} rendered triangles<br />{stats.geometries} geometries · {stats.textures} textures · renderer counters, not GPU memory</output> : null}
    </section>
    {scientificTimeline}
    <div className="fly-viewer-notes"><p>Drag to orbit · Scroll or pinch to zoom · Camera pivots around the visual thoracic anchor.{arena ? " Inspect Fly moves the camera only. Reset returns to Overview." : ""}</p><label><input type="checkbox" checked={diagnostics} onChange={event => setDiagnostics(event.target.checked)} /> Render diagnostics</label></div>
    <p className="fly-viewer-notes"><Link href={arena ? "/visual-lab/fly" : "/visual-lab/arena"}>{arena ? "Inspect the specimen in the studio →" : "Explore the experimental chamber prototype →"}</Link></p>
    <footer className="fly-viewer-credits"><p><a href={provenance.source_url} target="_blank" rel="noreferrer">Wildtype Male Drosophila Melanogaster</a> by {provenance.author} · <a href={provenance.license_url} target="_blank" rel="noreferrer">CC BY 4.0</a> · Modified for NeuroFly.</p><p>A third-party visual representation, not MaleCNS-derived external anatomy. {locomotion ? (locomotionVersion === "v3.1" || (locomotionVersion === "v4" && comparison)) ? "Counterfactual model trajectories recomputed locally from recorded events. Engineering propulsion and boundary recovery; computational steering intervention, not physiological ablation." : (locomotionVersion === "v2" || locomotionVersion === "v3" || locomotionVersion === "v4") ? "Live local browser computation with engineering propulsion and HS/DNp15 proxy-model steering. No biological gait, muscle calibration or fully connectome-driven locomotion." : "Precomputed replay with engineering propulsion; v1 steering is a proxy-model contribution, not fully connectome-driven locomotion. No biological gait or muscle model." : arena && replayPose ? "Recorded abstract model orientation only; no biological locomotion or chamber interaction." : "No simulation or experimental replay runs here."}</p>{arena ? <p>Environment: original NeuroFly acrylic enclosure and backdrop. <a href={ARENA.tableSource} target="_blank" rel="noreferrer">Lab Table</a> by zeeshanfareed · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">CC BY 4.0</a> · Uniformly fitted; decorative tabletop bottles omitted and material response adjusted for NeuroFly. Display scale is illustrative, not a biological measurement.</p> : null}</footer>
  </>;
}
