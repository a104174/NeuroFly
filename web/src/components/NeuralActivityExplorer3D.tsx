"use client";

import { Canvas, useThree } from "@react-three/fiber";
import { BufferGeometry, Float32BufferAttribute } from "three";
import { memo, useCallback, useEffect, useMemo, useState } from "react";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import {
  loadVerifiedNeuralMorphology,
  type DisplayNeuralMorphology,
  type NeuralActivityViewSnapshot,
  type NeuralMorphologyManifest,
  type NeuralMorphologyView,
} from "@/lib/neuralMorphologyExplorer";

interface LoadedBundle {
  readonly manifest: NeuralMorphologyManifest;
  readonly view: NeuralMorphologyView;
}

function CameraControls({ onContextLoss }: { readonly onContextLoss: () => void }) {
  const { camera, gl, invalidate } = useThree();
  useEffect(() => {
    const controls = new OrbitControls(camera, gl.domElement);
    controls.enableDamping = false;
    controls.enablePan = true;
    controls.minDistance = 4;
    controls.maxDistance = 28;
    controls.target.set(0, 0, 0);
    camera.position.set(0, 5.8, 13.5);
    camera.lookAt(0, 0, 0);
    camera.updateProjectionMatrix();
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
      controls.dispose();
    };
  }, [camera, gl, invalidate, onContextLoss]);
  return null;
}

function Skeleton({ body, value, selected }: {
  readonly body: DisplayNeuralMorphology;
  readonly value: number | null;
  readonly selected: boolean;
}) {
  const geometry = useMemo(() => {
    const result = new BufferGeometry();
    result.setAttribute("position", new Float32BufferAttribute(body.view_positions, 3));
    result.computeBoundingSphere();
    return result;
  }, [body]);
  const magnitude = value === null ? 0 : Math.min(1, Math.abs(value));
  const color = value === null ? "#607c8a" : value > 0 ? "#87e9df" : value < 0 ? "#e8b77b" : "#91a7b0";
  const opacity = selected ? 0.6 + 0.4 * magnitude : value === null ? 0.34 : 0.12 + 0.25 * magnitude;
  return (
    <lineSegments geometry={geometry}>
      <lineBasicMaterial color={color} transparent opacity={opacity} depthWrite={false} />
    </lineSegments>
  );
}

function NeuralScene({ view, selectedId, values, onContextLoss }: {
  readonly view: NeuralMorphologyView;
  readonly selectedId: number;
  readonly values: ReadonlyMap<number, number>;
  readonly onContextLoss: () => void;
}) {
  return (
    <>
      <color attach="background" args={["#07121a"]} />
      {view.bodies.map((body) => (
        <Skeleton
          key={body.identity.body_id}
          body={body}
          value={values.get(body.identity.body_id) ?? null}
          selected={selectedId === body.identity.body_id}
        />
      ))}
      <CameraControls onContextLoss={onContextLoss} />
    </>
  );
}

const NeuralCanvas = memo(function NeuralCanvas({ view, selectedId, values, onContextLoss }: {
  readonly view: NeuralMorphologyView;
  readonly selectedId: number;
  readonly values: ReadonlyMap<number, number>;
  readonly onContextLoss: () => void;
}) {
  return (
    <Canvas
      aria-label="MaleCNS HS and DNp15 raw skeletons in a 3D view"
      frameloop="demand"
      dpr={[1, 1.25]}
      camera={{ position: [0, 5.8, 13.5], fov: 42, near: 0.1, far: 100 }}
      fallback={<p className="neural-viewer-unavailable">WebGL is unavailable; verified source identities and model values remain listed beside the viewer.</p>}
    >
      <NeuralScene
        view={view}
        selectedId={selectedId}
        values={values}
        onContextLoss={onContextLoss}
      />
    </Canvas>
  );
});

function activityFor(snapshot: NeuralActivityViewSnapshot | null): ReadonlyMap<number, number> {
  return new Map(snapshot?.values.map((entry) => [entry.body_id, entry.value]) ?? []);
}

export const NeuralActivityExplorer3D = memo(function NeuralActivityExplorer3D({
  snapshot,
  activityError,
}: {
  readonly snapshot: NeuralActivityViewSnapshot | null;
  readonly activityError?: string | null;
}) {
  const [bundle, setBundle] = useState<LoadedBundle | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState(10015);
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
          <p>Orbit or zoom the verified native-space skeletons. Selection changes display only.</p>
        </div>
        {snapshot ? (
          <output className="neural-explorer-clock" aria-label="Synchronized model tick and time">
            Model tick {snapshot.interval_tick} · accepted tick {snapshot.accepted_tick}<br />
            {snapshot.simulation_time_s.toFixed(2)} s · neural influence {snapshot.neural_enabled ? "on" : "off"}<br />
            Neural yaw {snapshot.neural_yaw_rad_s >= 0 ? "+" : ""}{snapshot.neural_yaw_rad_s.toFixed(4)} rad/s · boundary yaw {snapshot.boundary_yaw_rad_s >= 0 ? "+" : ""}{snapshot.boundary_yaw_rad_s.toFixed(4)} rad/s
          </output>
        ) : <span className="neural-explorer-clock">Start a live session to view computed activity.</span>}
      </div>

      {activityError ? <p className="neural-explorer-error" role="alert">{activityError}. The neural view is not synchronized.</p> : null}
      {contextLost ? <p className="neural-explorer-error" role="alert">The neural viewer lost its WebGL context. Reload the page to restore it.</p> : null}

      <div className="neural-explorer-layout">
        <div className="neural-explorer-canvas-wrap">
          {!contextLost ? <NeuralCanvas
            view={bundle.view}
            selectedId={selectedId}
            values={values}
            onContextLoss={onContextLoss}
          /> : <div className="neural-explorer-canvas-lost" role="status">3D context unavailable</div>}
          <span className="neural-explorer-canvas-label">Native MaleCNS X / Y / Z · shared display fit</span>
        </div>

        <aside className="neural-explorer-inspector" aria-label="Neural entity selection and activity">
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

          {selected ? <div className="neural-entity-detail" aria-live="polite">
            <span className="lab-eyebrow">{selected.identity.role === "SOURCE" ? "HS MODEL SOURCE" : "DNp15 MODEL TARGET"}</span>
            <h3>{selected.identity.cell_type} {selected.identity.side}</h3>
            <dl>
              <div><dt>MaleCNS body ID</dt><dd>{selected.identity.body_id}</dd></div>
              <div><dt>Model state</dt><dd>{selected.identity.model_state.field}</dd></div>
              <div><dt>Activity</dt><dd>{selectedValue === null ? "Unavailable" : `${selectedValue >= 0 ? "+" : ""}${selectedValue.toFixed(5)} model units`}</dd></div>
              <div><dt>SWC nodes</dt><dd>{selected.node_count.toLocaleString()}</dd></div>
              <div><dt>Skeleton sampling</dt><dd>{selected.identity.morphology.source_sampling.downres_level} · ds_intv {selected.identity.morphology.source_sampling.ds_intv.join("/ ")}</dd></div>
              <div><dt>Selected structural routes</dt><dd>{routes.length ? routes.map((route) => `${route.source_body_id}→${route.target_body_id} (${route.structural_contact_count} contacts)`).join(" · ") : "No selected route in this motif"}</dd></div>
            </dl>
          </div> : null}

          <div className="neural-activity-legend">
            <strong>Signed proxy state</strong>
            <div><i className="is-positive" /> positive <i className="is-negative" /> negative</div>
            <p>Hue and whole-skeleton highlight encode the current signed, dimensionless model proxy. This is not measured fluorescence, Δf/F, or branch-local activity.</p>
          </div>
        </aside>
      </div>

      <div className="neural-explorer-provenance">
        <p><strong>Interpretation:</strong> the body ID and type/side come from the pinned MaleCNS v1.0 identity contract; the displayed value is a computational proxy associated with that identity, not a measured single-cell response. The 3D highlight applies one value to the whole skeleton.</p>
        <p>Structural connectivity records the selected HS→DNp15 routes; contact counts are provenance, not model gains. Neural yaw is the existing engineering projection. Boundary yaw and translational control remain engineering rules.</p>
        <p>Coordinates: male_cns_v1_em_native_voxels · 8 nm voxel. Raw source geometry is unhealed and unsmoothed; one shared center and uniform scale are used for display only. Sampling resolution varies by skeleton.</p>
        <p><a href="https://male-cns.janelia.org/download/" target="_blank" rel="noreferrer">MaleCNS v1.0 source and license ↗</a> · CC-BY attribution: official MaleCNS connectome dataset, FlyEM/Janelia and collaborators.</p>
      </div>
    </section>
  );
});
