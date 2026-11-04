"use client";

import Link from "next/link";
import { memo, useCallback, useEffect, useMemo, useState, useSyncExternalStore } from "react";

import {
  CockpitEventLog,
  CockpitRunPanel,
  CockpitSelectedNeuronPanel,
  CockpitWorldPanel,
} from "@/components/CockpitPanels";
import { CockpitTelemetry } from "@/components/CockpitTelemetry";
import { MorphologyInspector } from "@/components/MorphologyInspector";
import { useExperimentPlayback } from "@/hooks/useExperimentPlayback";
import { deriveActivityStructureProjection } from "@/lib/activityStructure";
import { deriveCockpitEvents, deriveCockpitFrame } from "@/lib/cockpitModel";
import type {
  ExperimentSummary,
  ExperimentTimeline,
  MorphologyArtifactSummary,
  MorphologyBody,
  MorphologyBodyId,
  StructuralConnectivityProjection,
} from "@/lib/neuroflyClient";
import { selectMorphologyBody, type MorphologySelection } from "@/lib/morphologyView";
import { PLAYBACK_RATES, type PlaybackRate } from "@/lib/playback";
import { KindBadge, Readout, Timeline, type TimelineMarker } from "@/components/ui";
import { experimentName } from "@/lib/recordedExperimentPresentation";
import {
  COCKPIT_LAYERS, PHONE_MAX, effectiveLayer, layerFromKey, overviewReadouts, widthClass,
  type CockpitLayer, type CockpitWidth,
} from "@/lib/cockpitLayers";

const CockpitProvenance = memo(function CockpitProvenance({
  summary,
  morphology,
  connectivity,
}: {
  summary: ExperimentSummary;
  morphology: MorphologyArtifactSummary | null;
  connectivity: StructuralConnectivityProjection | null;
}) {
  return <details className="cockpit-provenance">
    <summary>Provenance and scope</summary>
    <div className="cockpit-provenance-content">
      <dl>
        <div><dt>Experiment artifact</dt><dd>{summary.artifact_id}</dd></div>
        <div><dt>Experiment configuration SHA-256</dt><dd>{summary.experiment_config_sha256}</dd></div>
        <div><dt>MaleCNS circuit source</dt><dd>{summary.source.endpoint}</dd></div>
        <div><dt>Morphology</dt><dd>{morphology ? `${morphology.artifact_id} · ${morphology.generation.source_mode}` : "unavailable"}</dd></div>
        <div><dt>Structural projection</dt><dd>{connectivity?.projection.id ?? "unavailable"}</dd></div>
        <div><dt>Encoder population mapping</dt><dd>{summary.encoder.population_policy}</dd></div>
        <div><dt>LIF membrane references</dt><dd>{summary.neural_model.membrane_state_references.rest_mv} mV_eq rest · {summary.neural_model.membrane_state_references.threshold_mv} mV_eq threshold (model reference values, chosen for the model and not validated here)</dd></div>
        <div><dt>Source coordinate frame</dt><dd>{morphology ? `${morphology.coordinate_frame_id} · ${morphology.coordinate_unit}` : "unavailable"}</dd></div>
      </dl>
      <p>Structural weight is a connectome count. The morphology connectors and world scene use separate presentation geometry; they do not locate synapses or align the fly to MaleCNS coordinates.</p>
    </div>
  </details>;
});

function subscribeWidth(listener: () => void) { window.addEventListener("resize", listener); return () => window.removeEventListener("resize", listener); }
function useWidthClass(): CockpitWidth {
  return useSyncExternalStore(subscribeWidth, () => widthClass(window.innerWidth), () => "standard" as CockpitWidth);
}

const ACCORDION_KEY = "neurofly-cockpit-accordions";
const ACCORDION_EVENT = "neurofly-cockpit-accordions-change";
function subscribeStored(listener: () => void) {
  window.addEventListener(ACCORDION_EVENT, listener); window.addEventListener("storage", listener);
  return () => { window.removeEventListener(ACCORDION_EVENT, listener); window.removeEventListener("storage", listener); };
}
function readStored(): string { try { return localStorage.getItem(ACCORDION_KEY) ?? ""; } catch { return ""; } }
/** Which Detail accordions the reader closed. Stored only in this browser; defaults to all open. */
function Accordion({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  const closed = useSyncExternalStore(subscribeStored, readStored, () => "").split(",");
  const open = !closed.includes(id);
  return (
    <details className="cockpit-accordion" open={open} onToggle={(event) => {
      const nowOpen = (event.currentTarget as HTMLDetailsElement).open;
      if (nowOpen === open) return;
      const set = new Set(readStored().split(",").filter(Boolean));
      if (nowOpen) set.delete(id); else set.add(id);
      try { localStorage.setItem(ACCORDION_KEY, [...set].join(",")); } catch { /* blocked storage */ }
      window.dispatchEvent(new Event(ACCORDION_EVENT));
    }}>
      <summary>{title}</summary>
      {children}
    </details>
  );
}

const SHORTCUTS: readonly (readonly [string, string])[] = [
  ["Space", "Play or pause"], ["← →", "Step back or forward (Shift for 10 steps)"], ["Home, End", "Jump to start or end"],
  ["1, 2, 3", "Overview, Detail, Raw"], ["?", "Show or hide this list"],
];

function RawTable({ summary, timeline, frame, selectedBody, activity }: {
  summary: ExperimentSummary; timeline: ExperimentTimeline; frame: ReturnType<typeof deriveCockpitFrame>; selectedBody: MorphologyBody | null;
  activity: ReturnType<typeof deriveActivityStructureProjection>;
}) {
  const state = selectedBody && (selectedBody.body_id === 10001 || selectedBody.body_id === 10010) ? activity.bodySpecificStates?.[selectedBody.body_id] ?? null : null;
  const rows: { name: string; value: string; unit: string; code: string }[] = [
    { name: "Experiment time", value: frame.playbackTimeMs.toFixed(3), unit: "ms", code: "playback_time_ms" },
    { name: "Boundary step", value: String(frame.boundaryIndex), unit: "dimensionless", code: "boundary_index" },
    { name: "Boundary time", value: frame.boundaryTimeMs.toFixed(3), unit: "ms", code: "boundary_time_ms" },
    { name: "Interval start", value: frame.intervalStartMs.toFixed(3), unit: "ms", code: "interval_start_ms" },
    { name: "Angular size θ", value: frame.thetaRad.toFixed(6), unit: "rad", code: "theta_rad" },
    { name: "LC4 type drive", value: frame.lc4DriveMveq.toFixed(6), unit: "mV_eq", code: "lc4_drive_mveq" },
    { name: "LPLC2 type drive", value: frame.lplc2DriveMveq.toFixed(6), unit: "mV_eq", code: "lplc2_drive_mveq" },
  ];
  if (state && selectedBody) rows.push({ name: `DNp01 ${selectedBody.body_id} membrane`, value: state.membraneMv.toFixed(6), unit: "mV_eq", code: "membrane_mv" });
  return (
    <section className="cockpit-raw" aria-labelledby="cockpit-raw-heading">
      <h2 id="cockpit-raw-heading">Raw values at this step <KindBadge kind="model-state" /></h2>
      <div className="cockpit-raw-scroll">
        <table>
          <caption>Values at the current stored boundary. Units ending in _eq are model-equivalent, not measured.</caption>
          <thead><tr><th scope="col">Name</th><th scope="col">Value</th><th scope="col">Unit</th><th scope="col">Machine code</th></tr></thead>
          <tbody>{rows.map((r) => <tr key={r.code}><th scope="row">{r.name}</th><td>{r.value}</td><td>{r.unit}</td><td><code>{r.code}</code></td></tr>)}</tbody>
        </table>
      </div>
      <dl className="cockpit-raw-ids">
        <div><dt>Status code</dt><dd><code>{summary.validation_status}</code></dd></div>
        <div><dt>Artifact</dt><dd><code>{summary.artifact_id}</code></dd></div>
        <div><dt>Result</dt><dd><code>{summary.result_id}</code></dd></div>
        <div><dt>Steps</dt><dd><code>{timeline.times_ms.length}</code></dd></div>
      </dl>
    </section>
  );
}

export function ScientificCockpit({
  summary,
  timeline,
  morphology,
  bodies,
  connectivity,
  morphologyFailure,
  connectivityFailure,
  initialBodyId = null,
  initialLayer = null,
}: {
  summary: ExperimentSummary;
  timeline: ExperimentTimeline;
  morphology: MorphologyArtifactSummary | null;
  bodies: readonly MorphologyBody[];
  connectivity: StructuralConnectivityProjection | null;
  morphologyFailure: string | null;
  connectivityFailure: string | null;
  initialBodyId?: MorphologyBodyId | null;
  initialLayer?: CockpitLayer | null;
}) {
  const playback = useExperimentPlayback(timeline);
  const width = useWidthClass();
  const [chosenLayer, setChosenLayer] = useState<CockpitLayer | null>(initialLayer);
  const layer = effectiveLayer(chosenLayer, width);
  const [tab, setTab] = useState<"connectome" | "readouts">("connectome");
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [copied, setCopied] = useState("");
  const [selection, setSelection] = useState<MorphologySelection>(() =>
    initialBodyId !== null && bodies.some((body) => body.body_id === initialBodyId) ? selectMorphologyBody(initialBodyId) : { bodyId: null, componentId: null });
  const [visibility, setVisibility] = useState<Record<MorphologyBodyId, boolean>>({
    10001: true, 10010: true, 11498: true, 12032: true, 14465: true, 16128: true,
  });
  const [showConnectivity, setShowConnectivity] = useState(false);
  const [showSimulatedState, setShowSimulatedState] = useState(true);
  const frame = useMemo(() => deriveCockpitFrame(timeline, playback.sceneState), [timeline, playback.sceneState]);
  const activity = useMemo(
    () => deriveActivityStructureProjection(summary, timeline, connectivity, playback.sceneState),
    [summary, timeline, connectivity, playback.sceneState],
  );
  const events = useMemo(() => deriveCockpitEvents(timeline, connectivity?.fixed_sample.bodies ?? []), [timeline, connectivity]);
  const selectedBody = bodies.find((body) => body.body_id === selection.bodyId) ?? null;
  const selectBody = useCallback((bodyId: MorphologyBodyId) => {
    if (bodies.some((body) => body.body_id === bodyId)) setSelection(selectMorphologyBody(bodyId));
  }, [bodies]);
  const stepCount = timeline.times_ms.length;
  const seekStep = useCallback((step: number) => {
    const t = timeline.times_ms[Math.max(0, Math.min(stepCount - 1, step))];
    if (t !== undefined) playback.seek(t);
  }, [timeline.times_ms, stepCount, playback]);
  const ended = frame.boundaryIndex >= stepCount - 1 && !playback.isPlaying;
  const togglePlay = useCallback(() => {
    if (playback.isPlaying) playback.pause();
    else { if (ended) playback.reset(); playback.play(); }
  }, [playback, ended]);
  const markers: TimelineMarker[] = useMemo(() => events.map((event) => ({ id: event.id, step: event.stepIndex, label: `${event.label} at ${event.timeMs.toFixed(3)} ms` })), [events]);

  // The selected body and the layer live in the URL, so a view can be shared.
  useEffect(() => {
    const url = new URL(window.location.href);
    if (selection.bodyId === null) url.searchParams.delete("body"); else url.searchParams.set("body", String(selection.bodyId));
    if (chosenLayer === null) url.searchParams.delete("layer"); else url.searchParams.set("layer", chosenLayer);
    window.history.replaceState(null, "", url);
  }, [selection.bodyId, chosenLayer]);

  // Keyboard: Space plays or pauses, arrows step, 1 2 3 change layer, ? lists shortcuts.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      const target = event.target as HTMLElement | null;
      const tag = target?.tagName;
      if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA" || target?.isContentEditable) return;
      if (event.key === "?") { event.preventDefault(); setShowShortcuts((v) => !v); return; }
      const next = layerFromKey(event.key);
      if (next) { setChosenLayer(next); return; }
      if (target?.getAttribute("role") === "slider") return; // the slider handles its own arrows
      if (event.key === " " && tag !== "BUTTON" && tag !== "SUMMARY") { event.preventDefault(); togglePlay(); }
      else if (event.key === "ArrowRight") { event.preventDefault(); seekStep(frame.boundaryIndex + (event.shiftKey ? 10 : 1)); }
      else if (event.key === "ArrowLeft") { event.preventDefault(); seekStep(frame.boundaryIndex - (event.shiftKey ? 10 : 1)); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [togglePlay, seekStep, frame.boundaryIndex]);

  const readouts = overviewReadouts(frame, stepCount);
  const phone = width === "phone";
  const tablet = width === "tablet";
  const shown = phone ? readouts.slice(0, PHONE_MAX) : readouts;
  const showStructure = !phone && (!tablet || tab === "connectome");
  const showReadouts = phone || (tablet ? tab === "readouts" : true);
  const detail = layer === "detail" || layer === "raw";

  const structurePanel = morphology ? (
    <section className="cockpit-panel cockpit-structure" aria-label="MaleCNS morphology and structural connectivity">
      <div className="cockpit-structure-link">
        <span className="eyebrow">Connectome <KindBadge kind="structural" /></span>
        <div className="cockpit-panel-actions">
          <Link href={`/morphology/${morphology.artifact_id}`}>Full inspector ↗</Link>
        </div>
      </div>
      <MorphologyInspector
        artifact={morphology} bodies={bodies} connectivity={connectivity}
        selection={selection} onSelectionChange={setSelection}
        activity={activity} showSimulatedState={showSimulatedState} onShowSimulatedStateChange={setShowSimulatedState}
        visibility={visibility} onVisibilityChange={setVisibility}
        showConnectivity={showConnectivity} onShowConnectivityChange={setShowConnectivity}
        compact
      />
      {connectivityFailure ? <p className="cockpit-source-failure" role="status">Structural layer unavailable: {connectivityFailure}</p> : null}
    </section>
  ) : (
    <div className="cockpit-structural-empty" role="status">
      <h2>Source structure unavailable</h2>
      <p>{morphologyFailure ?? "The six-body morphology artifact could not be loaded."}</p>
      <p>Experiment playback and stored telemetry remain available.</p>
    </div>
  );

  return (
    <div className="scientific-cockpit cockpit-layered" data-layer={layer} data-width={width}>
      <div className="cockpit-masthead">
        <div className="cockpit-masthead-title">
          <p className="eyebrow">Cockpit</p>
          <h1>{experimentName(summary.candidate.identifier)}</h1>
        </div>
        <div className="cockpit-toolbar" aria-label="Cockpit toolbar">
          <span className="cockpit-replay-note">Replay of a completed run</span>
          <KindBadge kind="not-evaluated" />
          {!phone ? (
            <div className="cockpit-layer-switch" role="group" aria-label="Detail layer">
              {COCKPIT_LAYERS.map((name, index) => (
                <button key={name} type="button" aria-pressed={layer === name} onClick={() => setChosenLayer(name)}>
                  {name[0].toUpperCase() + name.slice(1)} <kbd>{index + 1}</kbd>
                </button>
              ))}
            </div>
          ) : null}
          <button type="button" className="cockpit-shortcuts-button" aria-expanded={showShortcuts} onClick={() => setShowShortcuts((v) => !v)}>Shortcuts <kbd>?</kbd></button>
        </div>
      </div>
      {showShortcuts ? (
        <section className="cockpit-shortcuts" aria-label="Keyboard shortcuts">
          <dl>{SHORTCUTS.map(([key, text]) => <div key={key}><dt><kbd>{key}</kbd></dt><dd>{text}</dd></div>)}</dl>
        </section>
      ) : null}

      {phone ? (
        <p className="cockpit-phone-note" role="note">
          This is a simplified replay. The connectome view and raw values need a larger screen.{" "}
          <button type="button" onClick={async () => { try { await navigator.clipboard.writeText(window.location.href); setCopied("Link copied"); } catch { setCopied("Could not copy. Select the address instead."); } }}>Copy link for desktop</button>
          <span role="status" className="cockpit-copied">{copied}</span>
        </p>
      ) : null}

      {tablet ? (
        <div className="cockpit-tabs" role="group" aria-label="Panel">
          <button type="button" aria-pressed={tab === "connectome"} onClick={() => setTab("connectome")}>Connectome</button>
          <button type="button" aria-pressed={tab === "readouts"} onClick={() => setTab("readouts")}>Readouts</button>
        </div>
      ) : null}

      <div className="cockpit-main" data-detail={detail ? "open" : "closed"}>
        <div className="cockpit-stage-column">
          <CockpitWorldPanel scene={playback.sceneState} frame={frame} focused={false} onToggleFocus={() => {}} />
          {showReadouts ? (
            <div className="cockpit-readouts" aria-label="Key readouts">
              {shown.map((r) => <Readout key={r.id} kind="model-state" label={r.label} value={r.value} digits={r.digits} unit={r.unit} />)}
            </div>
          ) : null}
        </div>
        {showStructure ? <div className="cockpit-side-column">{structurePanel}</div> : null}
        {detail && !phone ? (
          <aside className="cockpit-detail-panel" aria-label="Detail">
            <Accordion id="system" title="System"><CockpitRunPanel summary={summary} /></Accordion>
            <Accordion id="body" title="Body"><CockpitSelectedNeuronPanel body={selectedBody} connectivity={connectivity} activity={activity} /></Accordion>
            <Accordion id="signals" title="Stimulus and neural signals">
              <CockpitTelemetry timeline={timeline} frame={frame} selectedBodyId={selection.bodyId} activity={activity} focused={false} onToggleFocus={() => {}} />
            </Accordion>
            <Accordion id="events" title="Events">
              <CockpitEventLog events={events} frame={frame} selectedBodyId={selection.bodyId} onSeek={playback.seek} onSelectBody={selectBody} />
            </Accordion>
          </aside>
        ) : null}
      </div>

      <Timeline
        step={frame.boundaryIndex} steps={stepCount}
        timeLabel={`${frame.playbackTimeMs.toFixed(2)} / ${timeline.end_ms.toFixed(2)} ms`}
        playing={playback.isPlaying} ended={ended}
        onPlayPause={togglePlay} onStep={seekStep}
        rate={playback.playbackRate} rates={PLAYBACK_RATES} onRate={(r) => playback.setPlaybackRate(r as PlaybackRate)}
        markers={markers} onMarker={(m) => { seekStep(m.step); const e = events.find((x) => x.id === m.id); if (e?.bodyId) selectBody(e.bodyId); }}
      />

      {layer === "raw" && !phone ? <RawTable summary={summary} timeline={timeline} frame={frame} selectedBody={selectedBody} activity={activity} /> : null}

      <CockpitProvenance summary={summary} morphology={morphology} connectivity={connectivity} />
    </div>
  );
}
