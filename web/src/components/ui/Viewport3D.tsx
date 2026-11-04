"use client";

import { useCallback, useEffect, useRef, useState, useSyncExternalStore, type ReactNode } from "react";
import { KindBadge } from "./KindBadge";
import { StatePanel } from "./StatePanel";
import { STATE_COPY, type DataKind } from "@/content/science-copy";
import { getMorphologyWebGLCapability, getServerMorphologyWebGLCapability, subscribeToMorphologyWebGLCapability } from "@/lib/morphologyWebGL";
import { createFrameRateWatch, dprRange, nextLowerTier, TIER_LABEL, type ViewportTier } from "@/lib/viewportTier";
import styles from "./Viewport3D.module.css";

export type ViewportState = "loading" | "ready" | "paused" | "degraded" | "no-webgl" | "context-lost" | "missing-data";

export interface ViewportRenderProps {
  /** False while the view is offscreen or the tab is hidden: render nothing. */
  visible: boolean;
  tier: ViewportTier;
  dpr: [number, number];
  /** Report each rendered frame while playing, so the tier can drop. */
  onFrame: (now: number) => void;
}

const noop = () => {};

/** Calls the scene render function in its own component, so scene code is not part of the frame's render. */
function Slot({ render, state }: { render: (props: ViewportRenderProps) => ReactNode; state: ViewportRenderProps }) {
  return <>{render(state)}</>;
}

/**
 * Frame for every canvas. It reserves the aspect ratio, owns the states a 3D view can be in, and
 * always offers a text description. The scene itself is passed as a render function and is only
 * mounted when WebGL works.
 */
export function Viewport3D({
  title, kind, aspect = "16 / 10", description, legend, controls, children,
  dataAlternative = false, missingData, loading = false, playing = false, initialTier = "high", onRestart,
}: {
  title: string;
  kind: DataKind;
  aspect?: string;
  /** Text description of what the view shows. */
  description: string;
  legend?: ReactNode;
  controls?: ReactNode;
  children: (props: ViewportRenderProps) => ReactNode;
  /** True only when a table or list on the page shows the same information. */
  dataAlternative?: boolean;
  /** Set when the artifact has no data for this view. */
  missingData?: { what: string; detail?: string };
  loading?: boolean;
  /** Continuous rendering: frame rate is watched and the tier can drop. */
  playing?: boolean;
  initialTier?: ViewportTier;
  onRestart?: () => void;
}) {
  const capability = useSyncExternalStore(subscribeToMorphologyWebGLCapability, getMorphologyWebGLCapability, getServerMorphologyWebGLCapability);
  const box = useRef<HTMLDivElement>(null);
  const [contextLost, setContextLost] = useState(false);
  const [restartKey, setRestartKey] = useState(0);
  const [onScreen, setOnScreen] = useState(true);
  const [tabVisible, setTabVisible] = useState(true);
  const [tier, setTier] = useState<ViewportTier>(initialTier);
  const [dropped, setDropped] = useState<ViewportTier | null>(null);
  const watch = useRef(createFrameRateWatch());
  const phone = typeof window !== "undefined" && window.matchMedia?.("(max-width: 599px)").matches;

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    // webglcontextlost does not bubble, so it is caught on the way down.
    const lost = (event: Event) => { event.preventDefault(); setContextLost(true); };
    el.addEventListener("webglcontextlost", lost, true);
    const io = typeof IntersectionObserver === "undefined" ? null : new IntersectionObserver(([entry]) => setOnScreen(entry.isIntersecting));
    io?.observe(el);
    const vis = () => setTabVisible(document.visibilityState !== "hidden");
    document.addEventListener("visibilitychange", vis);
    return () => { el.removeEventListener("webglcontextlost", lost, true); io?.disconnect(); document.removeEventListener("visibilitychange", vis); };
  }, []);

  const onFrame = useCallback((now: number) => {
    if (watch.current(now)) {
      setTier((current) => { const lower = nextLowerTier(current); if (lower !== current) setDropped(lower); return lower; });
    }
  }, []);

  const state: ViewportState = missingData ? "missing-data"
    : capability === "unavailable" ? "no-webgl"
    : contextLost ? "context-lost"
    : loading || capability === "pending" ? "loading"
    : dropped ? "degraded" : "ready";
  const visible = onScreen && tabVisible;

  const restart = () => { setContextLost(false); setRestartKey((k) => k + 1); watch.current = createFrameRateWatch(); onRestart?.(); };
  const showScene = state === "ready" || state === "degraded";

  return (
    <figure className={styles.frame} data-state={state}>
      <figcaption className={styles.top}>
        <span className={styles.title}>{title}</span>
        <KindBadge kind={kind} />
      </figcaption>
      <div ref={box} className={styles.stage} style={{ aspectRatio: aspect }}>
        {showScene ? <div key={restartKey} className={styles.scene}><Slot render={children} state={{ visible, tier, dpr: dprRange(tier, phone), onFrame: playing ? onFrame : noop }} /></div> : null}
        {state === "loading" ? <div className={styles.overlay}><StatePanel state="loading" what={title.toLowerCase()} headingLevel={3} /></div> : null}
        {state === "no-webgl" ? <div className={styles.overlay}><StatePanel state="webgl-off" hasDataAlternative={dataAlternative} headingLevel={3} /></div> : null}
        {state === "context-lost" ? <div className={styles.overlay}><StatePanel state="context-lost" headingLevel={3} actions={<button type="button" className={styles.button} onClick={restart}>{STATE_COPY.contextLost.action}</button>} /></div> : null}
        {state === "missing-data" && missingData ? <div className={styles.overlay}><StatePanel state="missing-data" what={missingData.what} detail={missingData.detail} headingLevel={3} /></div> : null}
        {showScene && legend ? <div className={styles.legend}>{legend}</div> : null}
        {showScene && controls ? <div className={styles.controls}>{controls}</div> : null}
      </div>
      {state === "degraded" && dropped ? (
        <p className={styles.notice} role="status">{TIER_LABEL[dropped]} to keep playback smooth. <button type="button" className={styles.link} onClick={() => { setTier("high"); setDropped(null); watch.current = createFrameRateWatch(); }}>Use full detail</button></p>
      ) : null}
      <p className={styles.description}>{description}</p>
    </figure>
  );
}
