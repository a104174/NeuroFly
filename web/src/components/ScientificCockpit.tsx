"use client";

import Link from "next/link";
import { memo, useCallback, useMemo, useState } from "react";

import {
  CockpitEventLog,
  CockpitRunPanel,
  CockpitSelectedNeuronPanel,
  CockpitWorldPanel,
} from "@/components/CockpitPanels";
import { CockpitTelemetry } from "@/components/CockpitTelemetry";
import { MorphologyInspector } from "@/components/MorphologyInspector";
import { useExperimentPlayback } from "@/hooks/useExperimentPlayback";
import { toggleCockpitFocus, type CockpitFocusPanel, type CockpitFocusState } from "@/lib/cockpitLayout";
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
        <div><dt>Source coordinate frame</dt><dd>{morphology ? `${morphology.coordinate_frame_id} · ${morphology.coordinate_unit}` : "unavailable"}</dd></div>
      </dl>
      <p>Structural weight is a connectome count. The morphology connectors and world scene use separate presentation geometry; they do not locate synapses or align the fly to MaleCNS coordinates.</p>
    </div>
  </details>;
});

export function ScientificCockpit({
  summary,
  timeline,
  morphology,
  bodies,
  connectivity,
  morphologyFailure,
  connectivityFailure,
}: {
  summary: ExperimentSummary;
  timeline: ExperimentTimeline;
  morphology: MorphologyArtifactSummary | null;
  bodies: readonly MorphologyBody[];
  connectivity: StructuralConnectivityProjection | null;
  morphologyFailure: string | null;
  connectivityFailure: string | null;
}) {
  const playback = useExperimentPlayback(timeline);
  const [selection, setSelection] = useState<MorphologySelection>({ bodyId: null, componentId: null });
  const [visibility, setVisibility] = useState<Record<MorphologyBodyId, boolean>>({
    10001: true, 10010: true, 11498: true, 12032: true, 14465: true, 16128: true,
  });
  const [showConnectivity, setShowConnectivity] = useState(false);
  const [focusedPanel, setFocusedPanel] = useState<CockpitFocusState>(null);
  const frame = useMemo(
    () => deriveCockpitFrame(timeline, playback.sceneState, selection.bodyId),
    [timeline, playback.sceneState, selection.bodyId],
  );
  const events = useMemo(() => deriveCockpitEvents(timeline), [timeline]);
  const selectedBody = bodies.find((body) => body.body_id === selection.bodyId) ?? null;
  const selectBody = useCallback((bodyId: MorphologyBodyId) => {
    if (bodies.some((body) => body.body_id === bodyId)) setSelection(selectMorphologyBody(bodyId));
  }, [bodies]);
  const toggleFocus = useCallback((panel: CockpitFocusPanel) => {
    setFocusedPanel((current) => toggleCockpitFocus(current, panel));
  }, []);

  return (
    <div className="scientific-cockpit">
      <div className="cockpit-masthead">
        <div className="cockpit-masthead-title">
          <p className="eyebrow">NEUROFLY / SCIENTIFIC COCKPIT</p>
          <h1>Persisted experiment <span>{summary.candidate.identifier}</span></h1>
        </div>
        <div className="cockpit-masthead-meta" aria-label="Current run status">
          <span title={summary.artifact_id}>RUN {summary.artifact_id.slice(0, 12)}…</span>
          <span>{summary.dataset}</span>
          <span className="cockpit-validation">VALIDATION · {summary.validation_status.replaceAll("_", " ")}</span>
          <span className="cockpit-playback-status">{playback.isPlaying ? "PLAYING" : "PAUSED"} · {frame.playbackTimeMs.toFixed(2)} ms</span>
          {selectedBody ? <span>SELECTED · {selectedBody.neuron_type} {selectedBody.body_id}</span> : null}
        </div>
      </div>

      <div className="cockpit-grid" data-focus={focusedPanel ?? "none"}>
        <CockpitWorldPanel
          scene={playback.sceneState}
          frame={frame}
          focused={focusedPanel === "world"}
          onToggleFocus={() => toggleFocus("world")}
        />

        <section className="cockpit-panel cockpit-structure" aria-label="MaleCNS morphology and structural connectivity">
          <div className="cockpit-structure-link">
            <span className="eyebrow">02 / MALECNS SOURCE STRUCTURE</span>
            <div className="cockpit-panel-actions">
              {morphology ? <Link href={`/morphology/${morphology.artifact_id}`}>Full inspector ↗</Link> : null}
              {morphology ? <button type="button" className="cockpit-focus-button" aria-pressed={focusedPanel === "connectome"} onClick={() => toggleFocus("connectome")}>
                {focusedPanel === "connectome" ? "Restore workspace" : "Expand connectome"}
              </button> : null}
            </div>
          </div>
          {morphology ? <>
            <MorphologyInspector
              artifact={morphology}
              bodies={bodies}
              connectivity={connectivity}
              selection={selection}
              onSelectionChange={setSelection}
              visibility={visibility}
              onVisibilityChange={setVisibility}
              showConnectivity={showConnectivity}
              onShowConnectivityChange={setShowConnectivity}
              compact
            />
            {connectivityFailure ? <p className="cockpit-source-failure" role="status">Structural layer unavailable: {connectivityFailure}</p> : null}
          </> : <div className="cockpit-structural-empty" role="status">
            <h2>Source structure unavailable</h2>
            <p>{morphologyFailure ?? "The six-body morphology artifact could not be loaded."}</p>
            <p>Experiment playback and stored telemetry remain available.</p>
          </div>}
        </section>

        <div className="cockpit-rail">
          <CockpitRunPanel summary={summary} />
          <CockpitSelectedNeuronPanel body={selectedBody} connectivity={connectivity} frame={frame} />
        </div>

        <CockpitTelemetry
          timeline={timeline}
          frame={frame}
          selectedBodyId={selection.bodyId}
          focused={focusedPanel === "telemetry"}
          onToggleFocus={() => toggleFocus("telemetry")}
        />
        <CockpitEventLog
          events={events}
          frame={frame}
          selectedBodyId={selection.bodyId}
          onSeek={playback.seek}
          onSelectBody={selectBody}
        />
      </div>

      <div className="cockpit-transport" aria-label="Canonical experiment playback controls">
        <div className="cockpit-transport-buttons">
          <button type="button" onClick={playback.isPlaying ? playback.pause : playback.play}>
            {playback.isPlaying ? "Pause" : "Play"}
          </button>
          <button type="button" onClick={playback.reset}>Reset</button>
        </div>
        <label className="cockpit-transport-timeline">
          <span>EXPERIMENT TIME · {frame.playbackTimeMs.toFixed(3)} / {timeline.end_ms.toFixed(3)} ms</span>
          <input
            type="range"
            min={timeline.start_ms}
            max={timeline.end_ms}
            step={timeline.dt_ms}
            value={playback.currentTimeMs}
            onChange={(event) => playback.seek(Number(event.currentTarget.value))}
            aria-label="Seek canonical experiment playback time"
          />
        </label>
        <label className="cockpit-transport-rate">
          <span>PLAYBACK RATE</span>
          <select
            value={playback.playbackRate}
            onChange={(event) => playback.setPlaybackRate(Number(event.currentTarget.value) as PlaybackRate)}
            aria-label="Select playback presentation rate"
          >
            {PLAYBACK_RATES.map((rate) => <option key={rate} value={rate}>{rate}×</option>)}
          </select>
        </label>
      </div>

      <CockpitProvenance summary={summary} morphology={morphology} connectivity={connectivity} />
    </div>
  );
}
