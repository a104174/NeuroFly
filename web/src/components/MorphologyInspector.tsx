"use client";

import { Canvas, useThree } from "@react-three/fiber";
import {
  memo,
  useEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
  type Dispatch,
  type SetStateAction,
} from "react";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

import type {
  MorphologyArtifactSummary,
  MorphologyBody,
  MorphologyBodyId,
  MorphologyNeuronType,
  StructuralConnectivityProjection,
} from "@/lib/neuroflyClient";
import {
  bodySpecificActivityByMorphologyIdentity,
  type ActivityStructureProjection,
  type BodySpecificDnp01State,
} from "@/lib/activityStructure";
import { buildSchematicStructuralConnectors } from "@/lib/connectivityView";
import {
  getMorphologyWebGLCapability,
  getServerMorphologyWebGLCapability,
  selectMorphologyWebGLView,
  subscribeToMorphologyWebGLCapability,
} from "@/lib/morphologyWebGL";
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
  activityState,
  showSimulatedState,
}: {
  body: MorphologyBody;
  transform: MorphologyViewTransform;
  selection: MorphologySelection;
  activityState: BodySpecificDnp01State | null;
  showSimulatedState: boolean;
}) {
  const components = useMemo(
    () => buildMorphologyLineComponents(body, transform),
    [body, transform],
  );
  const geometryArgs = useMemo(
    () => components.map((component) => [component.positions, 3] as [Float32Array, number]),
    [components],
  );
  return components.map((component, index) => {
    const selectedOpacity = selection.bodyId === null ||
      (selection.bodyId === body.body_id &&
        (selection.componentId === null || selection.componentId === component.componentId))
      ? 1 : selection.bodyId === body.body_id ? 0.28 : 0.16;
    const normalizedPosition = activityState?.normalizedModelMembranePosition ?? null;
    return <group key={`${component.bodyId}-${component.componentId}`}>
      <SourceSkeletonLines
        positions={geometryArgs[index]}
        color={BODY_COLORS[body.body_id]}
        opacity={selectedOpacity}
      />
      {showSimulatedState && activityState && normalizedPosition !== null ? <SimulatedBodyStateLines
        positions={geometryArgs[index]}
        opacity={normalizedPosition * 0.36 * selectedOpacity}
      /> : null}
    </group>;
  });
}

const SourceSkeletonLines = memo(function SourceSkeletonLines({
  positions,
  color,
  opacity,
}: {
  positions: [Float32Array, number];
  color: string;
  opacity: number;
}) {
  return <lineSegments>
    <bufferGeometry>
      <bufferAttribute attach="attributes-position" args={positions} />
    </bufferGeometry>
    <lineBasicMaterial color={color} linewidth={1} transparent opacity={opacity} depthWrite={false} />
  </lineSegments>;
});

const SimulatedBodyStateLines = memo(function SimulatedBodyStateLines({
  positions,
  opacity,
}: {
  positions: [Float32Array, number];
  opacity: number;
}) {
  return <lineSegments renderOrder={1}>
    <bufferGeometry>
      <bufferAttribute attach="attributes-position" args={positions} />
    </bufferGeometry>
    <lineBasicMaterial color="#f4f2dd" linewidth={1} transparent opacity={opacity} depthWrite={false} />
  </lineSegments>;
});

const StructuralConnectivityLines = memo(function StructuralConnectivityLines({
  connectors,
}: {
  connectors: ReturnType<typeof buildSchematicStructuralConnectors>;
}) {
  return connectors.filter((connector) => connector.visible).map((connector) => (
    <lineSegments key={`${connector.preBodyId}-${connector.postBodyId}`} renderOrder={2}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[new Float32Array([...connector.start, ...connector.end]), 3]}
        />
      </bufferGeometry>
      <lineBasicMaterial
        color="#77c9c6"
        linewidth={1}
        transparent
        opacity={connector.opacity}
        depthTest={false}
        depthWrite={false}
      />
    </lineSegments>
  ));
});

function MorphologyScene({
  bodies,
  transform,
  visibility,
  showReference,
  selection,
  focusRequest,
  onFocused,
  showConnectivity,
  connectors,
  activityByBodyId,
  showSimulatedState,
}: {
  bodies: readonly MorphologyBody[];
  transform: MorphologyViewTransform;
  visibility: Readonly<Record<MorphologyBodyId, boolean>>;
  showReference: boolean;
  selection: MorphologySelection;
  focusRequest: FocusRequest;
  onFocused: (kind: FocusRequest["kind"]) => void;
  showConnectivity: boolean;
  connectors: ReturnType<typeof buildSchematicStructuralConnectors>;
  activityByBodyId: Readonly<Partial<Record<MorphologyBodyId, BodySpecificDnp01State>>>;
  showSimulatedState: boolean;
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
          <SkeletonLines
            key={body.body_id}
            body={body}
            transform={transform}
            selection={selection}
            activityState={activityByBodyId[body.body_id] ?? null}
            showSimulatedState={showSimulatedState}
          />
        ) : null,
      )}
      {showConnectivity ? <StructuralConnectivityLines connectors={connectors} /> : null}
      <CameraControls focusRequest={focusRequest} transform={transform} onFocused={onFocused} />
    </>
  );
}

function vector(values: readonly number[]): string {
  return values.map((value) => value.toFixed(3)).join(", ");
}

export const MorphologyInspector = memo(function MorphologyInspector({
  artifact,
  bodies,
  connectivity,
  selection: controlledSelection,
  onSelectionChange,
  visibility: controlledVisibility,
  onVisibilityChange,
  showConnectivity: controlledShowConnectivity,
  onShowConnectivityChange,
  activity,
  showSimulatedState = false,
  onShowSimulatedStateChange,
  compact = false,
}: {
  artifact: MorphologyArtifactSummary;
  bodies: readonly MorphologyBody[];
  connectivity: StructuralConnectivityProjection | null;
  selection?: MorphologySelection;
  onSelectionChange?: (selection: MorphologySelection) => void;
  visibility?: Readonly<Record<MorphologyBodyId, boolean>>;
  onVisibilityChange?: Dispatch<SetStateAction<Record<MorphologyBodyId, boolean>>>;
  showConnectivity?: boolean;
  onShowConnectivityChange?: Dispatch<SetStateAction<boolean>>;
  activity?: ActivityStructureProjection;
  showSimulatedState?: boolean;
  onShowSimulatedStateChange?: Dispatch<SetStateAction<boolean>>;
  compact?: boolean;
}) {
  const transform = useMemo(
    () => deriveSharedMorphologyViewTransform(bodies),
    [bodies],
  );
  const [localVisibility, setLocalVisibility] = useState<Record<MorphologyBodyId, boolean>>({
    10001: true,
    10010: true,
    11498: true,
    12032: true,
    14465: true,
    16128: true,
  });
  const [showReference, setShowReference] = useState(true);
  const [localShowConnectivity, setLocalShowConnectivity] = useState(false);
  const [localSelection, setLocalSelection] = useState<MorphologySelection>({ bodyId: null, componentId: null });
  const selection = controlledSelection ?? localSelection;
  const setSelection = onSelectionChange ?? setLocalSelection;
  const visibility = controlledVisibility ?? localVisibility;
  const setVisibility = onVisibilityChange ?? setLocalVisibility;
  const showConnectivity = controlledShowConnectivity ?? localShowConnectivity;
  const setShowConnectivity = onShowConnectivityChange ?? setLocalShowConnectivity;
  const [focusRequest, setFocusRequest] = useState<FocusRequest>({ token: 0, kind: "global", bounds: null });
  const [focusKind, setFocusKind] = useState<FocusRequest["kind"]>("global");
  const webglCapability = useSyncExternalStore(
    subscribeToMorphologyWebGLCapability,
    getMorphologyWebGLCapability,
    getServerMorphologyWebGLCapability,
  );
  const webglView = selectMorphologyWebGLView(webglCapability);
  const webglAvailable = webglCapability === "available";
  const selectedBody = bodies.find((body) => body.body_id === selection.bodyId) ?? null;
  const selectedComponent = selectedBody?.components.find(
    (component) => component.component_id === selection.componentId,
  ) ?? null;
  const selectedVisible = isMorphologySelectionVisible(selection, visibility);
  const connectors = useMemo(
    () => connectivity ? buildSchematicStructuralConnectors(connectivity, bodies, transform, selection, visibility) : [],
    [bodies, connectivity, selection, transform, visibility],
  );
  const activityByBodyId = useMemo(() => {
    return activity ? bodySpecificActivityByMorphologyIdentity(activity, bodies) : {};
  }, [activity, bodies]);
  const incidentEdges = selectedBody === null
    ? connectivity?.edges ?? []
    : connectivity?.edges.filter((edge) =>
      edge.pre_body_id === selectedBody.body_id || edge.post_body_id === selectedBody.body_id,
    ) ?? [];

  function requestFocus(kind: FocusRequest["kind"], bounds: MorphologyBounds | null) {
    setFocusRequest((current) => ({ token: current.token + 1, kind, bounds }));
  }

  const bodyVisibilityControls = bodies.map((body) => (
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
  ));
  const referenceControl = (
    <label>
      <input
        type="checkbox"
        checked={showReference}
        onChange={(event) => setShowReference(event.target.checked)}
      />
      Show native-axis/grid reference
    </label>
  );
  const structuralEdgeList = connectivity ? (
    <ul aria-label="Directed structural edge readout">
      {incidentEdges.map((edge) => {
        const preBody = bodies.find((body) => body.body_id === edge.pre_body_id);
        const postBody = bodies.find((body) => body.body_id === edge.post_body_id);
        const isIncident = selection.bodyId === null || edge.pre_body_id === selection.bodyId || edge.post_body_id === selection.bodyId;
        return (
          <li key={`${edge.pre_body_id}-${edge.post_body_id}`} className={isIncident ? "is-incident" : "is-unrelated"}>
            <span>{edge.pre_neuron_type} body {edge.pre_body_id} (source side {edge.pre_source_side}) → {edge.post_neuron_type} body {edge.post_body_id} (source side {edge.post_source_side})</span>
            <span>structural weight: {edge.structural_weight}</span>
            <span>Source body indices: {preBody?.node_index} → {postBody?.node_index}</span>
          </li>
        );
      })}
    </ul>
  ) : null;

  return (
    <section className={`morphology-inspector${compact ? " morphology-inspector-compact" : ""}`} aria-labelledby="morphology-heading">
      <div className="morphology-heading-row">
        <div>
          <p className="eyebrow">MALECNS RAW MORPHOLOGY / BOUNDED SAMPLE</p>
          {compact ? <h2 id="morphology-heading">Connectome / neural structure</h2> :
            <h1 id="morphology-heading">MaleCNS morphology inspection</h1>}
          {!compact ? <p>
            {bodies.length} source skeletons in one shared native-frame view. This
            is separate from experiment playback and is not aligned to the fly
            visual asset.
          </p> : null}
        </div>
        <span className="morphology-mode">RAW · heal=False</span>
      </div>

      <div className="morphology-canvas-shell">
        {webglView === "placeholder" ? (
          <div className="morphology-webgl-pending" role="status">
            Initializing 3D morphology view…
          </div>
        ) : webglView === "fallback" ? (
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
              showConnectivity={showConnectivity}
              connectors={connectors}
              activityByBodyId={compact ? activityByBodyId : {}}
              showSimulatedState={compact && showSimulatedState}
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

      {compact && activity ? <section className="morphology-activity" aria-label="Experiment state mapped to source structure">
        <div className="morphology-activity-legend">
          <span><i className="morphology-activity-source" /> MALECNS MORPHOLOGY · raw source</span>
          <span><i className="morphology-activity-structural" /> STRUCTURAL · CircuitContract</span>
          <span><i className="morphology-activity-simulated" /> SIMULATED · model state</span>
          <label>
            <input type="checkbox" checked={showSimulatedState} onChange={(event) => onShowSimulatedStateChange?.(event.target.checked)} />
            Show simulated body-state overlay
          </label>
        </div>
        <p className="morphology-activity-note">DNp01 is a point-neuron model: body-level state is mapped uniformly across raw morphology for presentation, not spatially resolved along neurites.</p>
        <div className="morphology-type-drive-readouts" aria-label="Type-level encoder drives">
          {activity.typeLevelDrives ? activity.typeLevelDrives.map((signal) => <div key={signal.neuronType}>
            <span>TYPE-LEVEL {signal.neuronType} DRIVE</span>
            <strong>{signal.valueMveq.toFixed(4)} <small>mV_eq</small></strong>
            <small>interval {signal.intervalStartMs.toFixed(3)}–{signal.intervalEndMs.toFixed(3)} ms</small>
          </div>) : <p role="status">{activity.typeLevelUnavailableReason ?? "Validated type-level encoder data unavailable."}</p>}
        </div>
        <div className="morphology-body-state-readouts" aria-label="DNp01 body-level simulated state">
          {([10001, 10010] as const).map((bodyId) => {
            const body = bodies.find((candidate) => candidate.body_id === bodyId);
            const state = activity.bodySpecificStates?.[bodyId];
            return <div key={bodyId}>
              <span>DNp01 BODY {bodyId} · node_index {body?.node_index ?? "unavailable"} · source side {body?.source_side ?? "unavailable"}</span>
              {state ? <>
                <strong>{state.membraneMv.toFixed(4)} mV · filtered state {state.synapticStateMveq.toFixed(4)} mV_eq</strong>
                <small>normalized model membrane position: {state.normalizedModelMembranePosition === null ? "not available" : state.normalizedModelMembranePosition.toFixed(3)} · boundary {state.boundaryTimeMs.toFixed(3)} ms{state.spikeAtBoundary ? " · SIMULATED SPIKE at stored boundary" : ""}</small>
              </> : <small>{activity.bodyStateUnavailableReason ?? "Body-specific state unavailable."}</small>}
            </div>;
          })}
        </div>
      </section> : null}

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
        {compact ? null : bodyVisibilityControls}
        {compact ? null : referenceControl}
        <label>
          <input
            type="checkbox"
            checked={showConnectivity}
            disabled={connectivity === null}
            onChange={(event) => setShowConnectivity(event.target.checked)}
          />
          Show structural connectivity
        </label>
        <button type="button" onClick={() => requestFocus("global", null)}>
          Reset camera
        </button>
        {compact ? <details className="morphology-secondary-controls">
          <summary>Individual bodies and grid</summary>
          <div>{bodyVisibilityControls}{referenceControl}</div>
        </details> : null}
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
              Body: {selectedBody.node_count.toLocaleString()} nodes · {selectedBody.link_count.toLocaleString()} links · {selectedBody.component_count} component(s)
              {compact ? "." : ` · source bounds ${vector(bodySourceBounds(selectedBody).minimum)} to ${vector(bodySourceBounds(selectedBody).maximum)} ${selectedBody.coordinate_unit}.`}
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
                      {selectedBody.neuron_type} body {selectedBody.body_id} · {component.nodes.length.toLocaleString()} nodes · {component.links.length.toLocaleString()} links
                      {compact ? "" : ` · source bounds ${vector(bounds.minimum)} to ${vector(bounds.maximum)} ${selectedBody.coordinate_unit}`}
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
        {compact ? <details className="morphology-source-note"><summary>Selection meaning</summary><p>Selection and highlighting are presentation only; line color still identifies each body and type.</p></details>
          : <p>Selection and highlighting are presentation only; line color still identifies each body and type.</p>}
      </section>

      {connectivity ? <section className="morphology-connectivity" aria-labelledby="connectivity-heading">
        <p className="eyebrow">SOURCE CONNECTIVITY · {connectivity.fixed_sample.id}</p>
        <h2 id="connectivity-heading">{compact ? "Structural edges" : "Structural relationships in the fixed six-body sample"}</h2>
        <p>
          {incidentEdges.length} {selectedBody ? "incident structural edge(s)" : "projected structural edge(s)"}
          {selectedBody ? ` for ${selectedBody.neuron_type} body ${selectedBody.body_id}` : ""} · structural weight total {incidentEdges.reduce((sum, edge) => sum + edge.structural_weight, 0)}.
        </p>
        {compact ? <details className="morphology-compact-details"><summary>Directed edge details</summary>{structuralEdgeList}</details> : structuralEdgeList}
        {compact ? <details className="morphology-compact-details"><summary>Connector meaning and source</summary><p>
          Lines show directed structural relationships from the CircuitContract. Connector positions and straight paths are schematic anchors at transformed raw body-bounds centers; no synapse locations are present or claimed. Structural weight is not physiological efficacy. Morphology coordinates remain MaleCNS source data. This layer displays no neural activity.
        </p>
        <p>
          Source: {connectivity.source_contract.source}, {connectivity.source_contract.dataset}; verified `neurons.jsonl` and `connections.jsonl` SHA-256 provenance. Projection direction: LC4/LPLC2 → DNp01. The six-body projection is not a population-wide connectivity summary.
        </p></details> : <><p>
          Lines show directed structural relationships from the CircuitContract. Connector positions and straight paths are schematic anchors at transformed raw body-bounds centers; no synapse locations are present or claimed. Structural weight is not physiological efficacy. Morphology coordinates remain MaleCNS source data. This layer displays no neural activity.
        </p>
        <p>
          Source: {connectivity.source_contract.source}, {connectivity.source_contract.dataset}; verified `neurons.jsonl` and `connections.jsonl` SHA-256 provenance. Projection direction: LC4/LPLC2 → DNp01. The six-body projection is not a population-wide connectivity summary.
        </p></>}
        {!compact ? <details>
          <summary>Verified CircuitContract file hashes</summary>
          <ul>
            {connectivity.source_contract.integrity.sha256_by_file.map((entry) => (
              <li key={entry.file}>{entry.file} SHA-256: {entry.sha256}</li>
            ))}
          </ul>
        </details> : null}
      </section> : <p className="morphology-warning">Structural connectivity is unavailable. Raw morphology remains inspectable.</p>}

      {compact ? <details className="morphology-source-note"><summary>Native source axes</summary><p>
        Source x/y/z are MaleCNS native voxel axes. They are intentionally not
        labelled anterior/posterior, dorsal/ventral, or left/right.
      </p></details> : <p className="morphology-warning">
        Source x/y/z are MaleCNS native voxel axes. They are intentionally not
        labelled anterior/posterior, dorsal/ventral, or left/right.
      </p>}

      {!compact ? <div className="morphology-readouts">
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
      </div> : null}
    </section>
  );
});
