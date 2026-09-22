"use client";

import dynamic from "next/dynamic";
import { Component, useCallback, useState, type ErrorInfo, type ReactNode } from "react";

import { flyAssetStatusMessage, type FlyAssetLoadStatus } from "@/lib/flyVisualAsset";
import {
  cockpitEventPosition,
  type CockpitEvent,
  type CockpitFrame,
} from "@/lib/cockpitModel";
import type {
  ExperimentSummary,
  MorphologyBody,
  MorphologyBodyId,
  StructuralConnectivityProjection,
} from "@/lib/neuroflyClient";
import type { ExperimentSceneState } from "@/lib/playback";

const PlaybackCanvas = dynamic(
  () => import("./PlaybackCanvas").then((module) => module.PlaybackCanvas),
  { ssr: false, loading: () => <div className="cockpit-world-fallback">Loading world renderer…</div> },
);

class CockpitCanvasBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(_error: Error, _info: ErrorInfo) {
    // The experiment timeline and source readouts remain available outside this scene.
  }

  render() {
    return this.state.failed
      ? <div className="cockpit-world-fallback">3D world playback is unavailable in this browser.</div>
      : this.props.children;
  }
}

function shortId(value: string): string {
  return `${value.slice(0, 12)}…`;
}

export function CockpitWorldPanel({
  scene,
  frame,
}: {
  scene: ExperimentSceneState;
  frame: CockpitFrame;
}) {
  const [assetStatus, setAssetStatus] = useState<FlyAssetLoadStatus>("loading");
  const onAssetStatusChange = useCallback((status: FlyAssetLoadStatus) => setAssetStatus(status), []);
  return (
    <section className="cockpit-panel cockpit-world" aria-labelledby="cockpit-world-heading">
      <div className="cockpit-panel-heading">
        <div>
          <p className="eyebrow">01 / WORLD + STIMULUS</p>
          <h2 id="cockpit-world-heading">Looming experiment</h2>
        </div>
        <span className="cockpit-panel-tag">SIMULATED · PRESENTATION SCENE</span>
      </div>
      <div className="cockpit-world-stage" aria-label="Existing three-dimensional experiment playback scene">
        <CockpitCanvasBoundary>
          <PlaybackCanvas sceneState={scene} onAssetStatusChange={onAssetStatusChange} />
        </CockpitCanvasBoundary>
        <div className="cockpit-world-overlay" aria-live="off">
          <span>EXPERIMENT TIME <strong>{frame.playbackTimeMs.toFixed(3)} ms</strong></span>
          <span>ANGULAR SIZE <strong>{frame.thetaRad.toFixed(4)} rad</strong></span>
        </div>
      </div>
      <div className="cockpit-world-footer">
        <span>{flyAssetStatusMessage(assetStatus)}</span>
        <span>Scene layout is presentation space; the fly pose is not behavior.</span>
      </div>
    </section>
  );
}

export function CockpitRunPanel({
  summary,
  frame,
  isPlaying,
}: {
  summary: ExperimentSummary;
  frame: CockpitFrame;
  isPlaying: boolean;
}) {
  return (
    <section className="cockpit-panel cockpit-run" aria-labelledby="cockpit-run-heading">
      <div className="cockpit-panel-heading">
        <div>
          <p className="eyebrow">RUN / EXPERIMENT</p>
          <h2 id="cockpit-run-heading">Persisted run</h2>
        </div>
        <span className="cockpit-panel-tag">READ ONLY</span>
      </div>
      <dl className="cockpit-data-list">
        <div><dt>Artifact</dt><dd title={summary.artifact_id}>{shortId(summary.artifact_id)}</dd></div>
        <div><dt>Dataset</dt><dd>{summary.dataset}</dd></div>
        <div><dt>Circuit</dt><dd>{summary.candidate.identifier} · v{summary.candidate.version}</dd></div>
        <div><dt>Graph scope</dt><dd>{summary.graph_scope_id}</dd></div>
        <div><dt>Neural model</dt><dd>{summary.neural_model.id} · {summary.neural_model.version}</dd></div>
        <div><dt>Encoder</dt><dd>{summary.encoder.id} · {summary.encoder.version}</dd></div>
        <div><dt>Step / duration</dt><dd>{summary.dt_ms} / {summary.duration_ms} ms</dd></div>
        <div><dt>Validation</dt><dd>{summary.validation_status.replaceAll("_", " ")}</dd></div>
        <div><dt>Playback</dt><dd>{isPlaying ? "PLAYING" : "PAUSED"} · {frame.playbackTimeMs.toFixed(3)} ms</dd></div>
      </dl>
    </section>
  );
}

export function CockpitSelectedNeuronPanel({
  body,
  connectivity,
  frame,
}: {
  body: MorphologyBody | null;
  connectivity: StructuralConnectivityProjection | null;
  frame: CockpitFrame;
}) {
  const incident = body && connectivity ? connectivity.edges.filter((edge) =>
    edge.pre_body_id === body.body_id || edge.post_body_id === body.body_id,
  ) : [];
  return (
    <section className="cockpit-panel cockpit-selected" aria-labelledby="cockpit-selected-heading">
      <div className="cockpit-panel-heading">
        <div>
          <p className="eyebrow">SELECTED NEURON</p>
          <h2 id="cockpit-selected-heading">{body ? `${body.neuron_type} · ${body.body_id}` : "Select a body"}</h2>
        </div>
        <span className="cockpit-panel-tag">MALECNS SOURCE</span>
      </div>
      {body ? <>
        <dl className="cockpit-data-list">
          <div><dt>Body / node index</dt><dd>{body.body_id} / {body.node_index}</dd></div>
          <div><dt>Source side</dt><dd>{body.source_side}</dd></div>
          <div><dt>Raw morphology</dt><dd>{body.node_count.toLocaleString()} nodes · {body.component_count} component(s)</dd></div>
          <div><dt>Frame / unit</dt><dd>{body.coordinate_frame_id} · {body.coordinate_unit}</dd></div>
        </dl>
        <div className="cockpit-selected-relations">
          <h3>Structural relations in this sample</h3>
          {connectivity ? incident.length > 0 ? <ul>
            {incident.map((edge) => <li key={`${edge.pre_body_id}-${edge.post_body_id}`}>
              <span>{edge.pre_neuron_type} {edge.pre_body_id} → {edge.post_neuron_type} {edge.post_body_id}</span>
              <strong>structural weight {edge.structural_weight}</strong>
            </li>)}
          </ul> : <p>No projected incident edge for this body.</p>
          : <p>Structural projection unavailable.</p>}
        </div>
        <div className="cockpit-selected-dynamic">
          <h3>At {frame.boundaryTimeMs.toFixed(3)} ms · stored boundary</h3>
          {frame.selectedDynamic?.bodyId === body.body_id ? <dl className="cockpit-data-list">
            <div><dt>Membrane</dt><dd>{frame.selectedDynamic.membraneMv.toFixed(4)} mV</dd></div>
            <div><dt>Synaptic state</dt><dd>{frame.selectedDynamic.synapticStateMveq.toFixed(4)} mV_eq</dd></div>
            <div><dt>Persisted spike</dt><dd>{frame.selectedDynamic.spikedAtBoundary ? "YES" : "NO"}</dd></div>
          </dl> : <p>Dynamic body trace not present in this experiment artifact. LC4/LPLC2 drives are type-level model signals in telemetry.</p>}
        </div>
      </> : <p className="cockpit-panel-note">Select one of the six morphology bodies to inspect source identity, structural relations, and any stored body-specific dynamics.</p>}
    </section>
  );
}

export function CockpitEventLog({
  events,
  frame,
  selectedBodyId,
  onSeek,
  onSelectBody,
}: {
  events: readonly CockpitEvent[];
  frame: CockpitFrame;
  selectedBodyId: MorphologyBodyId | null;
  onSeek: (timeMs: number) => void;
  onSelectBody: (bodyId: MorphologyBodyId) => void;
}) {
  return (
    <section className="cockpit-panel cockpit-events" aria-labelledby="cockpit-events-heading">
      <div className="cockpit-panel-heading">
        <div>
          <p className="eyebrow">EVENT TIMELINE</p>
          <h2 id="cockpit-events-heading">Persisted events</h2>
        </div>
        <span className="cockpit-panel-tag">{events.length} ENTRIES</span>
      </div>
      <ol>
        {events.map((event) => {
          const position = cockpitEventPosition(event, frame);
          return <li key={event.id} className={`cockpit-event-${position}${event.bodyId === selectedBodyId ? " cockpit-event-selected" : ""}`}>
            <button type="button" onClick={() => {
              onSeek(event.timeMs);
              if (event.bodyId !== null) onSelectBody(event.bodyId);
            }} aria-label={`Seek to ${event.label} at ${event.timeMs.toFixed(3)} milliseconds`}>
              <time>{event.timeMs.toFixed(3)} ms</time>
              <span>{event.label}</span>
              <small>{position}</small>
            </button>
          </li>;
        })}
      </ol>
      <p className="cockpit-panel-note">Rows come from timeline start/end and stored DNp01 spike times. Current marks the selected stored boundary; no behavioral event is inferred.</p>
    </section>
  );
}
