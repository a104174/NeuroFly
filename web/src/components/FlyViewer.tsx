"use client";

import dynamic from "next/dynamic";
import { useCallback, useState } from "react";
import type { ViewerStats } from "./FlyViewerCanvas";
import { FLY_VIEWER_ASSET, type FlyViewerView } from "@/lib/flyViewer";

const FlyViewerCanvas = dynamic(() => import("./FlyViewerCanvas"), { ssr: false, loading: () => <p className="fly-viewer-message">Preparing the studio…</p> });
const views: { id: FlyViewerView; label: string }[] = [{ id: "three-quarter", label: "Overview" }, { id: "lateral", label: "Side" }, { id: "head", label: "Front" }, { id: "dorsal", label: "Top" }];
export function FlyViewer() {
  const [view, setView] = useState<FlyViewerView>("three-quarter");
  const [reset, setReset] = useState(0);
  const [status, setStatus] = useState<{ state: "loading" | "ready" | "error"; detail?: string }>({ state: "loading" });
  const [diagnostics, setDiagnostics] = useState(false);
  const [stats, setStats] = useState<ViewerStats | null>(null);
  const onStatus = useCallback((value: { state: "loading" | "ready" | "error"; detail?: string }) => setStatus(previous => previous.state === "error" ? previous : value), []);
  const onFailure = useCallback((detail: string) => setStatus({ state: "error", detail }), []);
  const provenance = FLY_VIEWER_ASSET.provenance;
  return <>
    <section className="fly-viewer-stage" aria-label="Interactive male Drosophila visual asset">
      <FlyViewerCanvas view={view} reset={reset} diagnostics={diagnostics} onStatus={onStatus} onStats={setStats} onFailure={onFailure} />
      <div className="fly-viewer-caption"><span>V2-F / MALE DROSOPHILA</span><small>Static visual specimen</small></div>
      {status.state !== "ready" ? <div className="fly-viewer-message" role={status.state === "error" ? "alert" : "status"}>
        <strong>{status.state === "error" ? "The specimen could not be displayed." : "Loading the specimen…"}</strong>
        {status.detail ? <p>{status.detail}</p> : null}
        {status.state === "error" ? <button onClick={() => window.location.reload()}>Reload viewer</button> : null}
      </div> : null}
      <div className="fly-viewer-toolbar" aria-label="Camera controls">
        <div className="fly-viewer-views">{views.map(item => <button key={item.id} aria-pressed={view === item.id} onClick={() => { setView(item.id); setReset(n => n + 1); }}>{item.label}</button>)}</div>
        <button onClick={() => { setView("three-quarter"); setReset(n => n + 1); }}>Reset view</button>
      </div>
      {diagnostics && stats ? <output data-camera-position={JSON.stringify(stats.cameraPosition)} data-camera-target={JSON.stringify(stats.cameraTarget)} className="fly-viewer-stats" aria-label="Measured renderer statistics">{stats.fps.toFixed(0)} FPS (approx.) · {stats.calls} calls · {stats.triangles.toLocaleString()} rendered triangles<br />{stats.geometries} geometries · {stats.textures} textures · renderer counters, not GPU memory</output> : null}
    </section>
    <div className="fly-viewer-notes"><p>Drag to orbit · Scroll or pinch to zoom · Camera pivots around the visual thoracic anchor.</p><label><input type="checkbox" checked={diagnostics} onChange={event => setDiagnostics(event.target.checked)} /> Render diagnostics</label></div>
    <footer className="fly-viewer-credits"><p><a href={provenance.source_url} target="_blank" rel="noreferrer">Wildtype Male Drosophila Melanogaster</a> by {provenance.author} · <a href={provenance.license_url} target="_blank" rel="noreferrer">CC BY 4.0</a> · Modified for NeuroFly.</p><p>A third-party visual representation, not MaleCNS-derived external anatomy. No simulation or experimental replay runs here.</p></footer>
  </>;
}
