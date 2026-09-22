"use client";

import { Canvas, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef, useState } from "react";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

import type {
  MorphologyArtifactSummary,
  MorphologyBody,
  MorphologyBodyId,
  MorphologyNeuronType,
} from "@/lib/neuroflyClient";
import {
  buildMorphologyLineComponents,
  bodySourceBounds,
  componentSourceBounds,
  deriveSharedMorphologyViewTransform,
  focusForSourceBounds,
  globalMorphologyFocus,
  isMorphologySelectionVisible,
  selectMorphologyBody,
  selectMorphologyComponent,
  type MorphologySelection,
  type MorphologyViewTransform,
} from "@/lib/morphologyView";
import type { MorphologyBounds } from "@/lib/neuroflyClient";

const BODY_COLORS: Readonly<Record<MorphologyBodyId, string>> = {
  10001: "#79d7d1",
  10010: "#e6a35b",
  11498: "#f4bf72",
  12032: "#8fd5ff",
  14465: "#dc8e5a",
  16128: "#769bea",
};

function detectWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") ?? canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

interface FocusRequest {
  readonly token: number;
  readonly kind: "global" | "body" | "component";
  readonly bounds: MorphologyBounds | null;
}

function CameraControls({ focusRequest, transform, onFocused }: {
  focusRequest: FocusRequest;
  transform: MorphologyViewTransform;
  onFocused: (kind: FocusRequest["kind"]) => void;
}) {
  const { camera, gl, invalidate, size } = useThree();
  const controlsRef = useRef<OrbitControls | null>(null);
  useEffect(() => {
    const controls = new OrbitControls(camera, gl.domElement);
    controlsRef.current = controls;
    controls.enableDamping = false;
    const handleChange = () => invalidate();
    controls.addEventListener("change", handleChange);
    controls.target.set(0, 0, 0);
    controls.update();
    return () => {
      controlsRef.current = null;
      controls.removeEventListener("change", handleChange);
      controls.dispose();
    };
  }, [camera, gl, invalidate]);
  useEffect(() => {
    const focus = focusRequest.bounds
      ? focusForSourceBounds(focusRequest.bounds, transform, size.width / size.height, focusRequest.kind as "body" | "component")
      : globalMorphologyFocus();
    camera.position.set(...focus.position);
    controlsRef.current?.target.set(...focus.target);
    controlsRef.current?.update();
    camera.lookAt(...focus.target);
    camera.updateProjectionMatrix();
    invalidate();
    onFocused(focus.kind);
  }, [camera, focusRequest, invalidate, onFocused, size.height, size.width, transform]);
  return null;
}

function SkeletonLines({
  body,
  transform,
  selection,
}: {
  body: MorphologyBody;
  transform: MorphologyViewTransform;
  selection: MorphologySelection;
}) {
  const components = useMemo(
    () => buildMorphologyLineComponents(body, transform),
    [body, transform],
  );
  return components.map((component) => (
    <lineSegments key={`${component.bodyId}-${component.componentId}`}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[component.positions, 3]}
        />
      </bufferGeometry>
      <lineBasicMaterial
        color={BODY_COLORS[body.body_id]}
        linewidth={1}
        transparent
        opacity={selection.bodyId === null ||
          (selection.bodyId === body.body_id &&
            (selection.componentId === null || selection.componentId === component.componentId))
          ? 1 : selection.bodyId === body.body_id ? 0.28 : 0.16}
        depthWrite={false}
      />
    </lineSegments>
  ));
}

function MorphologyScene({
  bodies,
  transform,
  visibility,
  showReference,
  selection,
  focusRequest,
  onFocused,
}: {
  bodies: readonly MorphologyBody[];
  transform: MorphologyViewTransform;
  visibility: Readonly<Record<MorphologyBodyId, boolean>>;
  showReference: boolean;
  selection: MorphologySelection;
  focusRequest: FocusRequest;
  onFocused: (kind: FocusRequest["kind"]) => void;
}) {
  return (
    <>
      <color attach="background" args={["#071013"]} />
      {showReference ? (
        <>
          <gridHelper args={[10, 10, "#315159", "#183038"]} />
          <axesHelper args={[2]} />
        </>
      ) : null}
      {bodies.map((body) =>
        visibility[body.body_id] ? (
          <SkeletonLines key={body.body_id} body={body} transform={transform} selection={selection} />
        ) : null,
      )}
      <CameraControls focusRequest={focusRequest} transform={transform} onFocused={onFocused} />
    </>
  );
}

function vector(values: readonly number[]): string {
  return values.map((value) => value.toFixed(3)).join(", ");
}

export function MorphologyInspector({
  artifact,
  bodies,
}: {
  artifact: MorphologyArtifactSummary;
  bodies: readonly MorphologyBody[];
}) {
  const transform = useMemo(
    () => deriveSharedMorphologyViewTransform(bodies),
    [bodies],
  );
  const [visibility, setVisibility] = useState<Record<MorphologyBodyId, boolean>>({
    10001: true,
    10010: true,
    11498: true,
    12032: true,
    14465: true,
    16128: true,
  });
  const [showReference, setShowReference] = useState(true);
  const [selection, setSelection] = useState<MorphologySelection>({ bodyId: null, componentId: null });
  const [focusRequest, setFocusRequest] = useState<FocusRequest>({ token: 0, kind: "global", bounds: null });
  const [focusKind, setFocusKind] = useState<FocusRequest["kind"]>("global");
  const [webglAvailable] = useState(detectWebGL);
  const selectedBody = bodies.find((body) => body.body_id === selection.bodyId) ?? null;
  const selectedComponent = selectedBody?.components.find(
    (component) => component.component_id === selection.componentId,
  ) ?? null;
  const selectedVisible = isMorphologySelectionVisible(selection, visibility);

  function requestFocus(kind: FocusRequest["kind"], bounds: MorphologyBounds | null) {
    setFocusRequest((current) => ({ token: current.token + 1, kind, bounds }));
  }

  return (
    <section className="morphology-inspector" aria-labelledby="morphology-heading">
      <div className="morphology-heading-row">
        <div>
          <p className="eyebrow">MALECNS RAW MORPHOLOGY / BOUNDED SAMPLE</p>
          <h1 id="morphology-heading">MaleCNS morphology inspection</h1>
          <p>
            {bodies.length} source skeletons in one shared native-frame view. This
            is separate from experiment playback and is not aligned to the fly
            visual asset.
          </p>
        </div>
        <span className="morphology-mode">RAW · heal=False</span>
      </div>

      <div className="morphology-canvas-shell">
        {webglAvailable === false ? (
          <div className="morphology-webgl-fallback">
            3D morphology inspection is unavailable in this browser. Source
            provenance remains readable below.
          </div>
        ) : (
          <Canvas
            camera={{ position: [8.5, 6.5, 10.5], fov: 42, near: 0.01, far: 100 }}
            frameloop="demand"
            aria-label="Raw MaleCNS skeleton morphology view"
          >
            <MorphologyScene
              bodies={bodies}
              transform={transform}
              visibility={visibility}
              showReference={showReference}
              selection={selection}
              focusRequest={focusRequest}
              onFocused={setFocusKind}
            />
          </Canvas>
        )}
        <div className="morphology-canvas-key" aria-label="Body color key">
          {bodies.map((body) => (
            <span key={body.body_id}>
              <i style={{ backgroundColor: BODY_COLORS[body.body_id] }} />
              {body.neuron_type} {body.body_id} · source side {body.source_side}
              {body.component_count > 1 ? ` · ${body.component_count} components` : ""}
            </span>
          ))}
        </div>
      </div>

      <div className="morphology-controls" aria-label="Morphology view controls">
        {(["LC4", "LPLC2", "DNp01"] as const)
          .filter((neuronType) => bodies.some((body) => body.neuron_type === neuronType))
          .map((neuronType: MorphologyNeuronType) => (
          <label key={neuronType}>
            <input
              type="checkbox"
              checked={bodies
                .filter((body) => body.neuron_type === neuronType)
                .every((body) => visibility[body.body_id])}
              onChange={(event) =>
                setVisibility((current) => ({
                  ...current,
                  ...Object.fromEntries(
                    bodies
                      .filter((body) => body.neuron_type === neuronType)
                      .map((body) => [body.body_id, event.target.checked]),
                  ),
                }))
              }
            />
            Show {neuronType}
          </label>
        ))}
        {bodies.map((body) => (
          <label key={body.body_id}>
            <input
              type="checkbox"
              checked={visibility[body.body_id]}
              onChange={(event) =>
                setVisibility((current) => ({
                  ...current,
                  [body.body_id]: event.target.checked,
                }))
              }
            />
            Show {body.neuron_type} {body.body_id}
          </label>
        ))}
        <label>
          <input
            type="checkbox"
            checked={showReference}
            onChange={(event) => setShowReference(event.target.checked)}
          />
          Show native-axis/grid reference
        </label>
        <button type="button" onClick={() => requestFocus("global", null)}>
          Reset camera
        </button>
      </div>

      <section className="morphology-selection" aria-labelledby="morphology-selection-heading">
        <p className="eyebrow">PRESENTATION SELECTION</p>
        <h2 id="morphology-selection-heading">Inspect body and raw component</h2>
        <div className="morphology-body-selector" aria-label="Select morphology body">
          {bodies.map((body) => (
            <button
              key={body.body_id}
              type="button"
              aria-pressed={selection.bodyId === body.body_id}
              onClick={() => setSelection(selectMorphologyBody(body.body_id))}
            >
              {body.neuron_type} {body.body_id} · {body.source_side}
            </button>
          ))}
        </div>
        {selectedBody ? (
          <>
            <p aria-live="polite">
              Selected: {selectedBody.neuron_type} body {selectedBody.body_id}
              {selectedComponent ? `, raw component ${selectedComponent.component_id}` : ", all raw components"}.
              {selectedVisible ? " Visible." : " Hidden by visibility controls; enable the body to focus it."}
              {selectedBody.component_count > 1 ? ` ${selectedBody.component_count} disconnected raw components; no bridge is rendered.` : ""}
            </p>
            <p>
              Body: {selectedBody.node_count.toLocaleString()} nodes · {selectedBody.link_count.toLocaleString()} links · {selectedBody.component_count} component(s) · source bounds {vector(bodySourceBounds(selectedBody).minimum)} to {vector(bodySourceBounds(selectedBody).maximum)} {selectedBody.coordinate_unit}.
            </p>
            <button type="button" disabled={!selectedVisible || !webglAvailable} onClick={() => requestFocus("body", bodySourceBounds(selectedBody))}>
              Focus selected body
            </button>
            <div className="morphology-component-list" aria-label={`Raw components of body ${selectedBody.body_id}`}>
              {selectedBody.components.map((component) => {
                const bounds = componentSourceBounds(component);
                return (
                  <div key={component.component_id} className="morphology-component-row">
                    <button
                      type="button"
                      aria-pressed={selection.componentId === component.component_id}
                      onClick={() => setSelection(selectMorphologyComponent(selectedBody.body_id, component.component_id))}
                    >
                      Select component {component.component_id}
                    </button>
                    <span>
                      {selectedBody.neuron_type} body {selectedBody.body_id} · {component.nodes.length.toLocaleString()} nodes · {component.links.length.toLocaleString()} links · source bounds {vector(bounds.minimum)} to {vector(bounds.maximum)} {selectedBody.coordinate_unit}
                    </span>
                  </div>
                );
              })}
            </div>
            <button type="button" disabled={!selectedComponent || !selectedVisible || !webglAvailable} onClick={() => {
              if (selectedComponent) requestFocus("component", componentSourceBounds(selectedComponent));
            }}>
              Focus selected component
            </button>
          </>
        ) : <p>Select a body to inspect its raw components and source bounds.</p>}
        <p aria-live="polite">Camera framing: {focusKind}. Reset camera restores the global six-body view and keeps the selection.</p>
        <p>Selection and highlighting are presentation only; line color still identifies each body and type.</p>
      </section>

      <p className="morphology-warning">
        Source x/y/z are MaleCNS native voxel axes. They are intentionally not
        labelled anterior/posterior, dorsal/ventral, or left/right.
      </p>

      <div className="morphology-readouts">
        <section>
          <p className="eyebrow">SOURCE DATA</p>
          <dl>
            <div><dt>Dataset</dt><dd>{artifact.dataset}</dd></div>
            <div><dt>Coordinate frame</dt><dd>{artifact.coordinate_frame_id}</dd></div>
            <div><dt>Coordinate unit</dt><dd>{artifact.coordinate_unit}</dd></div>
            <div><dt>Acquisition mode</dt><dd>{artifact.generation.source_mode}</dd></div>
            <div><dt>Artifact</dt><dd>{artifact.artifact_id}</dd></div>
          </dl>
          {Object.keys(artifact.generation.source_urls).length > 0 ? (
            <>
              <p className="morphology-source-links">
                Official source SWC URLs are retained in the artifact provenance:
              </p>
              <ul className="morphology-source-links">
                {artifact.body_ids.map((bodyId) => (
                  <li key={bodyId}>
                    <a
                      href={artifact.generation.source_urls[String(bodyId)]}
                      target="_blank"
                      rel="noreferrer"
                    >
                      body {bodyId} source SWC
                    </a>
                  </li>
                ))}
              </ul>
            </>
          ) : null}
          {bodies.map((body) => (
            <article key={body.body_id} className="morphology-body-readout">
              <h2>{body.neuron_type} body {body.body_id}</h2>
              <p>
                node_index {body.node_index} · source side {body.source_side} · {body.node_count.toLocaleString()} nodes · {body.component_count} component(s)
              </p>
              <p>Source status: {body.source_status ?? "not supplied"}</p>
              <p>Source SWC SHA-256: {body.source_swc_sha256.slice(0, 16)}…</p>
              <p>Soma location: {body.soma_location ? `source-recorded (${body.soma_location.x}, ${body.soma_location.y}, ${body.soma_location.z})` : "not supplied"}</p>
            </article>
          ))}
        </section>
        <section>
          <p className="eyebrow">VIEW / PRESENTATION</p>
          <dl>
            <div><dt>Transform</dt><dd>{transform.view_id}</dd></div>
            <div><dt>Source minimum</dt><dd>{vector(transform.source_bounds.minimum)}</dd></div>
            <div><dt>Source maximum</dt><dd>{vector(transform.source_bounds.maximum)}</dd></div>
            <div><dt>Shared center</dt><dd>{vector(transform.center_source)}</dd></div>
            <div><dt>Uniform scale</dt><dd>{transform.uniform_scale.toExponential(6)}</dd></div>
            <div><dt>Axis mapping</dt><dd>source x/y/z → view x/y/z</dd></div>
          </dl>
          <p>
            Center, uniform scale, camera, line colors, one-pixel line width,
            grid, visibility, orbit, pan, and zoom are presentation state only.
            Source radius is retained in data but never controls line thickness.
          </p>
          <p>
            Roots and child-parent link ordering are representation details—not
            soma, signal origin, or biological signal direction.
          </p>
        </section>
      </div>
    </section>
  );
}
