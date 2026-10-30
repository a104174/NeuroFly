"use client";

import { Canvas, extend, useThree } from "@react-three/fiber";
import { BufferGeometry, Float32BufferAttribute, PerspectiveCamera, Vector3, type LineSegments, type Raycaster, type Intersection } from "three";
import { memo, useCallback, useEffect, useMemo, useState, useRef, useLayoutEffect } from "react";
import type { LiveSample } from "@/lib/liveGroundSession";
import { activityHistory, activitySign } from "@/lib/neuralExplorerPresentation";
import { activityHistoryRows } from "./neuralHistoryRows";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import {
  loadVerifiedNeuralMorphology,
  type DisplayNeuralMorphology,
  type NeuralActivityViewSnapshot,
  type NeuralMorphologyManifest,
  type NeuralMorphologyView,
} from "@/lib/neuralMorphologyExplorer";

import { fitNeuralCamera, presentationBounds, NEURAL_OVERVIEW } from "@/lib/neuralCameraFraming";

type CameraActions = { focus: () => string | null; overview: () => void };

import { pickNeuralSegments } from "@/lib/neuralScreenPicking";

import { NeuralSelectionGesture, bindNeuralSelectionGesture } from "./neuralSelectionGesture";

function SelectionGestureEvents({ gesture }: { readonly gesture: NeuralSelectionGesture }) {
  const gl = useThree(state => state.gl);
  useEffect(() => bindNeuralSelectionGesture(gl.domElement, gesture), [gl, gesture]);
  return null;
}

interface LoadedBundle {
  readonly manifest: NeuralMorphologyManifest;
  readonly view: NeuralMorphologyView;
}

function CameraControls({ onContextLoss, view, selectedId, onReady }: { readonly onContextLoss: () => void; readonly view: NeuralMorphologyView; readonly selectedId: number; readonly onReady: (actions: CameraActions | null) => void }) {
  const selection = useRef(selectedId);
  useLayoutEffect(() => { selection.current = selectedId; }, [selectedId]);
  const { camera, gl, invalidate } = useThree();
  useEffect(() => {
    const controls = new OrbitControls(camera, gl.domElement);
    controls.enableDamping = false;
    controls.enablePan = true;
    controls.minDistance = 4;
    controls.maxDistance = 28;
    controls.target.fromArray(NEURAL_OVERVIEW.target);
    camera.position.fromArray(NEURAL_OVERVIEW.position);
    camera.lookAt(0, 0, 0);
    camera.updateProjectionMatrix();
    if (camera instanceof PerspectiveCamera) onReady({
      focus: () => {
        const result = fitNeuralCamera(presentationBounds(view, selection.current), {
          direction: camera.getWorldDirection(new Vector3()).toArray(), up: camera.up.toArray(),
          fov: camera.fov, aspect: camera.aspect, zoom: camera.zoom, near: camera.near, far: camera.far,
          minDistance: controls.minDistance, maxDistance: controls.maxDistance, margin: .12,
        });
        if (!result.ok) return result.reason;
        camera.position.fromArray(result.position); controls.target.fromArray(result.target);
        controls.update(); invalidate(); return null;
      },
      overview: () => {
        camera.zoom = 1; camera.up.set(0, 1, 0); camera.updateProjectionMatrix();
        camera.position.fromArray(NEURAL_OVERVIEW.position); controls.target.fromArray(NEURAL_OVERVIEW.target);
        controls.update(); invalidate();
      },
    });
    const onChange = () => invalidate();
    const onLost = (event: Event) => {
      event.preventDefault();
      onContextLoss();
    };
    controls.addEventListener("change", onChange);
    gl.domElement.addEventListener("webglcontextlost", onLost);
    controls.update();
    invalidate();
    return () => {
      controls.removeEventListener("change", onChange);
      gl.domElement.removeEventListener("webglcontextlost", onLost);
      onReady(null);
      controls.dispose();
    };
  }, [camera, gl, invalidate, onContextLoss, onReady, view]);
  return null;
}

// R3F owns this geometry as an attached child, including on replacement.
class NeuralGeometry extends BufferGeometry {
  constructor(positions: Float32Array) {
    super();
    this.setAttribute("position", new Float32BufferAttribute(positions, 3));
    this.computeBoundingSphere();
  }
}
const NeuralGeometryElement = extend(NeuralGeometry);

export function Skeleton({ body, value, selected, onSelect, gesture }: {
  readonly gesture: NeuralSelectionGesture;
  readonly body: DisplayNeuralMorphology;
  readonly value: number | null;
  readonly selected: boolean;
  readonly onSelect: (id: number) => void;
}) {
  const get = useThree(state => state.get);
  const raycast = useCallback(function(this: LineSegments, raycaster: Raycaster, hits: Intersection[]) {
    const state = get();
    const hit = pickNeuralSegments(body.view_positions, this.matrixWorld, state.camera, state.size, state.pointer);
    if (hit.status !== "hit") return;
    const cosine = state.camera.getWorldDirection(new Vector3()).dot(raycaster.ray.direction);
    const distance = hit.depth / cosine;
    if (!Number.isFinite(distance) || cosine <= 0) return;
    if (distance < raycaster.near || distance > raycaster.far) return;
    hits.push({ distance, point: hit.point, index: hit.index, object: this });
  }, [body, get]);
  const magnitude = value === null ? 0 : Math.min(1, Math.abs(value));
  const color = value === null ? "#607c8a" : value > 0 ? "#87e9df" : value < 0 ? "#e8b77b" : "#91a7b0";
  const opacity = selected ? 0.6 + 0.4 * magnitude : value === null ? 0.34 : 0.12 + 0.25 * magnitude;
  return (
    <lineSegments raycast={raycast} onClick={(event) => { event.stopPropagation(); if (gesture.consume(event.nativeEvent)) onSelect(body.identity.body_id); }}>
      <NeuralGeometryElement attach="geometry" args={[body.view_positions]} />
      <lineBasicMaterial color={color} transparent opacity={opacity} depthWrite={false} />
    </lineSegments>
  );
}

function NeuralScene({ view, selectedId, values, onContextLoss, onSelect, onReady, gesture }: {
  readonly gesture: NeuralSelectionGesture;
  readonly view: NeuralMorphologyView;
  readonly selectedId: number;
  readonly values: ReadonlyMap<number, number>;
  readonly onContextLoss: () => void;
  readonly onSelect: (id: number) => void;
  readonly onReady: (actions: CameraActions | null) => void;
}) {
  return (
    <>
      <SelectionGestureEvents gesture={gesture} />
      <color attach="background" args={["#07121a"]} />
      {view.bodies.map((body) => (
        <Skeleton
          key={body.identity.body_id}
          body={body}
          gesture={gesture}
          value={values.get(body.identity.body_id) ?? null}
          selected={selectedId === body.identity.body_id}
          onSelect={onSelect}
        />
      ))}
      <CameraControls onContextLoss={onContextLoss} view={view} selectedId={selectedId} onReady={onReady} />
    </>
  );
}

const NeuralCanvas = memo(function NeuralCanvas({ view, selectedId, values, onContextLoss, onSelect, onReady }: {
  readonly view: NeuralMorphologyView;
  readonly selectedId: number;
  readonly values: ReadonlyMap<number, number>;
  readonly onContextLoss: () => void;
  readonly onSelect: (id: number) => void;
  readonly onReady: (actions: CameraActions | null) => void;
}) {
  const gesture = useMemo(() => new NeuralSelectionGesture(), []);
  return (
    <Canvas
      aria-label="MaleCNS HS and DNp15 raw skeletons in a 3D view"
      frameloop="demand"
      dpr={[1, 1.25]}
      camera={{ position: [0, 5.8, 13.5], fov: 42, near: 0.1, far: 100 }}
      fallback={<p className="neural-viewer-unavailable">WebGL is unavailable; verified source identities and model values remain listed beside the viewer.</p>}
    >
      <NeuralScene
        gesture={gesture}
        view={view}
        selectedId={selectedId}
        values={values}
        onContextLoss={onContextLoss}
        onSelect={onSelect}
        onReady={onReady}
      />
    </Canvas>
  );
});

export const ActivityHistory = memo(function ActivityHistory({ history, name, rows = history }: {
  readonly history: ReturnType<typeof activityHistory>;
  readonly name: string;
  readonly rows?: ReturnType<typeof activityHistoryRows>;
}) {
  return (
            <div className="neural-history"><strong>Recent activity · {name}</strong>
              {history.length ? <><svg viewBox="0 0 240 70" preserveAspectRatio="none" role="img" aria-label={`Recent ${name} model proxy values from ${history[0].time.toFixed(2)} to ${history[history.length - 1].time.toFixed(2)} seconds`}>
                <line x1="0" x2="240" y1="35" y2="35" stroke="#6c8994" strokeDasharray="3 3" />
                {history.map((point, i) => { const span = history[history.length - 1].time - history[0].time; const x = span > 0 ? (point.time - history[0].time) * 240 / span : 0; const y = 35 - Math.max(-1, Math.min(1, point.value)) * 30; const previous = history[i - 1]; return <g key={point.tick}>{previous && point.tick === previous.tick + 1 ? <line x1={span > 0 ? (previous.time - history[0].time) * 240 / span : 0} y1={35 - Math.max(-1, Math.min(1, previous.value)) * 30} x2={x} y2={y} stroke="#87e9df" /> : null}<circle cx={x} cy={y} r="1.2" fill="#d6f4f0" /></g>; })}
              </svg><span>{history[0].time.toFixed(2)} s <span>interval-start time</span> {history[history.length - 1].time.toFixed(2)} s</span><small>Rolling window, up to 256 samples; −1 to +1 model units. Not a complete recording.</small></> : <p>{rows.length ? "No valid activity is available in this window." : "No recent valid samples yet. Start a session to see activity."}</p>}
              {rows.length ? <details className="neural-history-values"><summary>View recorded values ({rows.length} samples)</summary><div className="neural-history-table-scroll"><table><caption>{name}: model-computed activity, dimensionless units; interval-start times, oldest first.</caption><thead><tr><th scope="col">Interval</th><th scope="col">Time (s)</th><th scope="col">Activity</th></tr></thead><tbody>{rows.map((row, i) => <tr key={`${row.tick ?? 'unavailable'}-${i}`}><td>{row.tick ?? 'Unavailable'}</td><td>{row.time === null ? 'Unavailable' : String(row.time)}</td><td>{row.value === null || !Number.isFinite(row.value) ? 'Unavailable' : row.value > 0 ? `+${row.value}` : String(row.value)}</td></tr>)}</tbody></table></div></details> : null}
            </div>
  );
});

export function SelectedNeuralState({ name, side, bodyId, field, value }: {
  readonly name: string; readonly side: string; readonly bodyId: number;
  readonly field: string; readonly value: number | null;
}) {
  const valid = value !== null && Number.isFinite(value);
  return <header className="neural-selected-state" aria-label="Selected structure and current computational state">
    <span className="lab-eyebrow">Selected MaleCNS structure</span>
    <h3>{name} · {side === "R" ? "Right" : side === "L" ? "Left" : side}</h3>
    <p>Body ID {bodyId} · {field}</p>
    <div className="neural-current-state" aria-label="Current computational proxy">
      <span>Current model state</span>
      <strong>{valid ? value.toFixed(5) : "Unavailable"}</strong>
      <span>{activitySign(value)}{valid ? " · dimensionless model units" : " · no valid activity available"}</span>
    </div>
    <p>Computed whole-structure proxy associated with this anatomy. It is not a measured biological response.</p>
  </header>;
}

export function NeuralCameraGuidance() {
  return <p className="neural-camera-guidance">
    <span><strong>Mouse:</strong> left-drag to rotate · right-drag to pan · scroll to zoom. <strong>Touch:</strong> one-finger drag rotates · two-finger drag pans and pinch zooms.</span>
    <span><strong>Select:</strong> click or tap a neuron; camera drags do not change selection. <strong>Focus selected</strong> frames the chosen morphology · <strong>Overview</strong> restores the full view.</span>
  </p>;
}

function activityFor(snapshot: NeuralActivityViewSnapshot | null): ReadonlyMap<number, number> {
  return new Map(snapshot?.values.map((entry) => [entry.body_id, entry.value]) ?? []);
}

export const NeuralActivityExplorer3D = memo(function NeuralActivityExplorer3D({
  snapshot,
  activityError,
  recentSamples = [],
}: {
  readonly snapshot: NeuralActivityViewSnapshot | null;
  readonly activityError?: string | null;
  readonly recentSamples?: readonly LiveSample[];
}) {
  const [bundle, setBundle] = useState<LoadedBundle | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState(10015);
  const [presentation, setPresentation] = useState<"simple" | "detailed">("simple");
  const [actions, setActions] = useState<CameraActions | null>(null);
  const [cameraNotice, setCameraNotice] = useState<string | null>(null);
  const [contextLost, setContextLost] = useState(false);
  const onContextLoss = useCallback(() => setContextLost(true), []);

  useEffect(() => {
    let current = true;
    loadVerifiedNeuralMorphology()
      .then((loaded) => { if (current) setBundle(loaded); })
      .catch((error: unknown) => {
        if (current) setLoadError(error instanceof Error ? error.message : "Neural morphology integrity validation failed");
      });
    return () => { current = false; };
  }, []);

  const values = useMemo(() => activityFor(snapshot), [snapshot]);
  const selected = bundle?.view.bodies.find((body) => body.identity.body_id === selectedId) ?? null;
  const historyAvailable = !activityError && Boolean(snapshot);
  const historyRows = useMemo(() => historyAvailable ? activityHistoryRows(recentSamples, selectedId) : [], [recentSamples, selectedId, historyAvailable]);
  const history = useMemo(() => historyRows.filter((row): row is { tick: number; time: number; value: number } => row.tick !== null && row.time !== null && row.value !== null), [historyRows]);
  const selectedValue = snapshot?.values.find((entry) => entry.body_id === selectedId)?.value ?? null;
  const routes = bundle?.manifest.selected_routes.filter((route) =>
    route.source_body_id === selectedId || route.target_body_id === selectedId,
  ) ?? [];

  if (loadError) {
    return <div className="neural-explorer-error" role="alert">
      <strong>Verified MaleCNS morphology is unavailable.</strong>
      <p>{loadError}. No substitute geometry is displayed.</p>
    </div>;
  }

  if (!bundle) {
    return <div className="neural-explorer-loading" role="status">Verifying the pinned MaleCNS v1.0 skeleton bundle…</div>;
  }

  return (
    <section className="neural-explorer" aria-label="Verified neural anatomy and live activity">
      <div className="neural-explorer-heading">
        <div>
          <span className="lab-eyebrow">MALECNS v1.0 · 8 RAW SKELETONS</span>
          <h2>Neural activity explorer</h2>
          <p>Real anatomical skeletons, coloured by simulated model states. Select one to look closer.</p>
        </div>
        {snapshot ? (
          <output className="neural-explorer-clock" aria-label="Synchronized model tick and time">
            Model tick {snapshot.interval_tick} · accepted tick {snapshot.accepted_tick}<br />
            {snapshot.simulation_time_s.toFixed(2)} s · neural influence {snapshot.neural_enabled ? "on" : "off"}<br />
            Neural yaw {snapshot.neural_yaw_rad_s >= 0 ? "+" : ""}{snapshot.neural_yaw_rad_s.toFixed(4)} rad/s · boundary yaw {snapshot.boundary_yaw_rad_s >= 0 ? "+" : ""}{snapshot.boundary_yaw_rad_s.toFixed(4)} rad/s
          </output>
        ) : <span className="neural-explorer-clock">Start a live session to view computed activity.</span>}
      </div>

      <details className="neural-help"><summary>How to read this</summary><div>
        <p><strong>The fly:</strong> a continuous simulation using modeled neural signals and engineering movement rules.</p>
        <p><strong>The neurons:</strong> verified MaleCNS shapes; their colours show computed whole-cell proxy values, not recorded activity.</p>
        <p><strong>The connection:</strong> modeled neural yaw and an engineering wall response contribute to rotation. Select a structure or use the list to inspect it.</p>
      </div></details>
      <div className="neural-presentation" role="group" aria-label="Explanation detail">
        <button type="button" aria-pressed={presentation === "simple"} onClick={() => setPresentation("simple")}>Simple</button>
        <button type="button" aria-pressed={presentation === "detailed"} onClick={() => setPresentation("detailed")}>Detailed</button>
      </div>
      {activityError ? <p className="neural-explorer-error" role="alert">{activityError}. The neural view is not synchronized.</p> : null}
      {contextLost ? <p className="neural-explorer-error" role="alert">The neural viewer lost its WebGL context. Reload the page to restore it.</p> : null}

      <div className="neural-camera-actions" role="group" aria-label="Morphology camera">
        <button type="button" disabled={!actions || !selected || !presentationBounds(bundle.view, selectedId) || contextLost} onClick={() => setCameraNotice(actions?.focus() ?? null)}>Focus selected</button>
        <button type="button" disabled={!actions || contextLost} onClick={() => { actions?.overview(); setCameraNotice(null); }}>Overview</button>
        <span role="status">{cameraNotice}</span>
      </div>
      <NeuralCameraGuidance />
      <div className="neural-explorer-layout">
        <div className="neural-explorer-canvas-wrap">
          {!contextLost ? <NeuralCanvas
            view={bundle.view}
            selectedId={selectedId}
            values={values}
            onContextLoss={onContextLoss}
            onSelect={setSelectedId}
            onReady={setActions}
          /> : <div className="neural-explorer-canvas-lost" role="status">3D context unavailable</div>}
          <span className="neural-explorer-canvas-label">Native MaleCNS X / Y / Z · shared display fit</span>
        </div>

        <aside className="neural-explorer-inspector" aria-label="Neural entity selection and activity">

          {selected ? <div className="neural-entity-detail">
            <SelectedNeuralState name={selected.identity.cell_type} side={selected.identity.side} bodyId={selected.identity.body_id} field={selected.identity.model_state.field} value={selectedValue} />
            <p>{!snapshot ? "Start a session to see the circuit’s current contribution." : !snapshot.neural_enabled ? "Neural influence on movement is off; model states remain computed." : Math.abs(snapshot.neural_yaw_rad_s) < 1e-9 ? "The circuit’s current yaw contribution is zero." : "The circuit contributes to yaw through an engineering projection, not a decision by this individual cell."}</p>
            {snapshot ? <p>Engineering wall response: {Math.abs(snapshot.boundary_yaw_rad_s) < 1e-9 ? "no yaw contribution in this interval" : "also contributes to yaw in this interval"}.</p> : null}
            <ActivityHistory history={history} rows={historyRows} name={`${selected.identity.cell_type} ${selected.identity.side} · ${selected.identity.body_id}`} />
            {presentation === "detailed" ? <dl>
              <div><dt>MaleCNS body ID</dt><dd>{selected.identity.body_id}</dd></div>
              <div><dt>Model state</dt><dd>{selected.identity.model_state.field}</dd></div>
              <div><dt>Model role</dt><dd>{selected.identity.model} · {selected.identity.role}</dd></div>
              <div><dt>SWC nodes</dt><dd>{selected.node_count.toLocaleString()}</dd></div>
              <div><dt>Skeleton sampling</dt><dd>{selected.identity.morphology.source_sampling.downres_level} · ds_intv {selected.identity.morphology.source_sampling.ds_intv.join("/ ")}</dd></div>
              <div><dt>Selected structural routes</dt><dd>{routes.length ? routes.map((route) => `${route.source_body_id}→${route.target_body_id} (${route.structural_contact_count} contacts)`).join(" · ") : "No selected route in this motif"}</dd></div>
            </dl> : null}
            {presentation === "detailed" ? <div className="neural-relationships"><strong>Connections and model</strong><p>MaleCNS structural contacts: {routes.length ? routes.map((route) => `${route.source_body_id} → ${route.target_body_id} (${route.structural_contact_count})`).join(" · ") : "none in this selected motif"}. Contact counts are not model gains.</p><p>The computational model links HS proxies to DNp15 proxies; its yaw projection and the wall response are engineering mappings. Selecting one cell does not establish individual causation.</p></div> : <p>MaleCNS supplies anatomical structure; HS/DNp15 activity and yaw are modeled. Structural contacts are not model gains.</p>}
          </div> : <p role="status">Select a verified structure to inspect its model state.</p>}

          <strong className="neural-list-title">Select a neuron · list or 3D</strong>
          <div className="neural-entity-list" aria-label="Select a modeled neural identity">
            {bundle.view.bodies.map((body) => {
              const { identity } = body;
              const value = snapshot?.values.find((entry) => entry.body_id === identity.body_id)?.value;
              return <button
                key={identity.body_id}
                type="button"
                className="neural-entity-button"
                aria-pressed={selectedId === identity.body_id}
                onClick={() => setSelectedId(identity.body_id)}
              >
                <span><strong>{identity.cell_type}</strong> {identity.side} · {identity.body_id}</span>
                <small>{value === undefined ? "activity unavailable" : `proxy ${value >= 0 ? "+" : ""}${value.toFixed(3)}`}</small>
              </button>;
            })}
          </div>


          <div className="neural-activity-legend">
            <strong>Signed proxy state</strong>
            <div><i className="is-positive" /> positive <i className="is-negative" /> negative · zero is grey</div>
            <p>Hue shows the sign; opacity grows with |value|, capped at 1. Selection also brightens the whole skeleton. The scale uses signed, dimensionless model proxy values. This is not measured fluorescence, Δf/F, or branch-local activity.</p>
          </div>
        </aside>
      </div>

      <details className="neural-provenance-details"><summary>Scientific provenance and limitations</summary><div className="neural-explorer-provenance">
        <p><strong>Interpretation:</strong> the body ID and type/side come from the pinned MaleCNS v1.0 identity contract; the displayed value is a computational proxy associated with that identity, not a measured single-cell response. The 3D highlight applies one value to the whole skeleton.</p>
        <p>Structural connectivity records the selected HS→DNp15 routes; contact counts are provenance, not model gains. Neural yaw is the existing engineering projection. Boundary yaw and translational control remain engineering rules.</p>
        <p>Coordinates: male_cns_v1_em_native_voxels · 8 nm voxel. Raw source geometry is unhealed and unsmoothed; one shared center and uniform scale are used for display only. Sampling resolution varies by skeleton.</p>
        <p><a href="https://male-cns.janelia.org/download/" target="_blank" rel="noreferrer">MaleCNS v1.0 source and license ↗</a> · CC-BY attribution: official MaleCNS connectome dataset, FlyEM/Janelia and collaborators.</p>
      </div></details>
    </section>
  );
});
