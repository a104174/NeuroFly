"use client";

import dynamic from "next/dynamic";
import { Component, memo, useCallback, useState, type ErrorInfo, type ReactNode } from "react";

import { flyAssetStatusMessage, type FlyAssetLoadStatus } from "@/lib/flyVisualAsset";
import {
  cockpitEventPosition,
  type CockpitEvent,
  type CockpitFrame,
} from "@/lib/cockpitModel";
import { activityContextForBody, type ActivityStructureProjection } from "@/lib/activityStructure";
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
  focused,
  onToggleFocus,
}: {
  scene: ExperimentSceneState;
  frame: CockpitFrame;
  focused: boolean;
  onToggleFocus: () => void;
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
        <div className="cockpit-panel-actions">
          <span className="cockpit-panel-tag">SIMULATED · PRESENTATION</span>
          <button type="button" className="cockpit-focus-button" aria-pressed={focused} onClick={onToggleFocus}>
            {focused ? "Restore workspace" : "Expand world"}
          </button>
        </div>
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
        <span>Presentation scene · fly pose is not behavior</span>
      </div>
    </section>
  );
}

export const CockpitRunPanel = memo(function CockpitRunPanel({
  summary,
}: {
  summary: ExperimentSummary;
}) {
  return (
    <section className="cockpit-panel cockpit-run" aria-labelledby="cockpit-run-heading">
      <div className="cockpit-panel-heading">
        <div>
          <p className="eyebrow">RUN / EXPERIMENT</p>
          <h2 id="cockpit-run-heading">Run identity</h2>
        </div>
        <span className="cockpit-panel-tag">READ ONLY</span>
      </div>
      <dl className="cockpit-data-list">
        <div><dt>Artifact</dt><dd title={summary.artifact_id}>{shortId(summary.artifact_id)}</dd></div>
        <div><dt>Dataset</dt><dd>{summary.dataset}</dd></div>
        <div><dt>Circuit</dt><dd>{summary.candidate.identifier} · v{summary.candidate.version}</dd></div>
        <div><dt>Step / duration</dt><dd>{summary.dt_ms} / {summary.duration_ms} ms</dd></div>
      </dl>
      <details className="cockpit-panel-details">
        <summary>Model and encoder</summary>
        <dl className="cockpit-data-list">
          <div><dt>Graph scope</dt><dd>{summary.graph_scope_id}</dd></div>
          <div><dt>Neural model</dt><dd>{summary.neural_model.id} · {summary.neural_model.version}</dd></div>
          <div><dt>Encoder</dt><dd>{summary.encoder.id} · {summary.encoder.version}</dd></div>
        </dl>
      </details>
    </section>
  );
});

export function CockpitSelectedNeuronPanel({
  body,
  connectivity,
  activity,
}: {
  body: MorphologyBody | null;
  connectivity: StructuralConnectivityProjection | null;
  activity: ActivityStructureProjection;
}) {
  const incident = body && connectivity ? connectivity.edges.filter((edge) =>
    edge.pre_body_id === body.body_id || edge.post_body_id === body.body_id,
  ) : [];
  const activityContext = body ? activityContextForBody(activity, body) : null;
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
        <div className="cockpit-neuron-identity">
          <span>SOURCE SIDE <strong>{body.source_side}</strong></span>
          <span>NODE INDEX <strong>{body.node_index}</strong></span>
          <span>RAW NODES <strong>{body.node_count.toLocaleString()}</strong></span>
          <span>COMPONENTS <strong>{body.component_count}</strong></span>
        </div>
        <div className="cockpit-selected-dynamic">
          <h3>SIMULATED STATE · {activity.boundaryTimeMs.toFixed(2)} ms</h3>
          {activityContext?.granularity === "BODY_SPECIFIC" ? <>
            <p className="cockpit-activity-granularity">BODY-LEVEL SIMULATED LIF STATE · uniform presentation over morphology</p>
            <dl className="cockpit-dynamic-values">
              <div><dt>Membrane state</dt><dd>{activityContext.state.membraneMv.toFixed(4)} <small>mV</small></dd></div>
              <div><dt>Filtered synaptic state</dt><dd>{activityContext.state.synapticStateMveq.toFixed(4)} <small>mV_eq</small></dd></div>
              <div><dt>Normalized model membrane position</dt><dd>{activityContext.state.normalizedModelMembranePosition === null ? "not available" : activityContext.state.normalizedModelMembranePosition.toFixed(3)}</dd></div>
              <div><dt>Stored-boundary spike</dt><dd>{activityContext.state.spikeAtBoundary ? `SIMULATED SPIKE · ${activityContext.state.spikeTimestampMs?.toFixed(3)} ms` : "NO"}</dd></div>
            </dl>
          </> : activityContext?.granularity === "TYPE_LEVEL" ? <>
            <p className="cockpit-activity-granularity">TYPE-LEVEL {activityContext.signal.neuronType} MODEL DRIVE · {activityContext.signal.valueMveq.toFixed(4)} mV_eq</p>
            <p>No body-specific dynamic trace in this artifact.</p>
          </> : <p>{activityContext?.reason ?? "No dynamic state is available at this identity."}</p>}
        </div>
        <div className="cockpit-selected-relations">
          <h3>Structural relations · {incident.length}</h3>
          {connectivity ? incident.length > 0 ? <ul>
            {incident.map((edge) => <li key={`${edge.pre_body_id}-${edge.post_body_id}`}>
              <span>{edge.pre_neuron_type} {edge.pre_body_id} → {edge.post_neuron_type} {edge.post_body_id}</span>
              <strong>structural weight {edge.structural_weight}</strong>
            </li>)}
          </ul> : <p>No projected incident edge for this body.</p>
          : <p>Structural projection unavailable.</p>}
        </div>
        <details className="cockpit-panel-details">
          <summary>Source frame</summary>
          <p>{body.coordinate_frame_id} · {body.coordinate_unit}</p>
        </details>
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
            }} aria-label={`Seek to ${event.label}${event.nodeIndex === null ? "" : `, node index ${event.nodeIndex}`} at ${event.timeMs.toFixed(3)} milliseconds`}>
              <time>{event.timeMs.toFixed(3)} ms</time>
              <span>{event.kind === "dnp01_spike" ? `DNp01 ${event.bodyId} · node ${event.nodeIndex} · simulated spike` : event.label}</span>
              <small>{position}</small>
            </button>
          </li>;
        })}
      </ol>
      <details className="cockpit-panel-details">
        <summary>Event source</summary>
        <p>Rows come from timeline start/end and stored DNp01 spike times. Current marks the selected stored boundary; no behavioral event is inferred.</p>
      </details>
    </section>
  );
}
