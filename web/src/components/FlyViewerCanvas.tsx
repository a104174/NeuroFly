"use client";

import {articulateWings,type WingPose} from "@/lib/articulatedWings";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import {articulateFly,type GaitState} from "@/lib/articulatedGait";
import { ARENA, arenaCamera, arenaCameraLimits, constrainArenaInspectionCamera, type ArenaCameraView } from "@/lib/experimentalArena";
import { ExperimentalArena } from "./ExperimentalArena";
import { Component, useEffect, useLayoutEffect, useRef, useState, useMemo, type ReactNode } from "react";
import { AgXToneMapping, Color, DynamicDrawUsage, PMREMGenerator, PerspectiveCamera, Points as ThreePoints, PointsMaterial, Vector3, BufferAttribute, BufferGeometry, Line as ThreeLine, LineBasicMaterial, type Object3D } from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { GLTFLoader, type GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import { flyPresentationFit, prepareFlyVisual } from "@/lib/flyVisualInstance";
import { FLY_VIEWER_ASSET, flyViewerCamera, verifyFlyViewerBytes } from "@/lib/flyViewer";

import { ArenaComparison, type ArenaOverlayProps } from "./ArenaComparison";
import { recordedFlightMarkers, recordedFlightPositions, visibleFlightMarkers, visibleFlightVertexCount, type FlightTrajectoryDisplay, type FlightTrajectoryEventKind, type FlightTrajectoryMarker, type FlightTrajectoryLayer } from "@/lib/flightTrajectory";

export type ViewerStats = { wings?:unknown; gait?:unknown; stimulusPositions?: (number[]|undefined)[]; flightTrajectoryGeometry?: Record<string,{vertices:number;first:number[]|null;last:number[]|null}>; fps: number; calls: number; triangles: number; geometries: number; textures: number; cameraPosition: number[]; cameraTarget: number[]; bodyPosition?: number[]; bodyYaw?: number; comparisonMarkers?: Record<string, number[] | undefined> };
type Status = { state: "loading" | "ready" | "error"; detail?: string };
// Loader result is cached read-only. Only the cloned instance owns mutable materials.
let assetPromise: Promise<GLTF> | undefined;
function loadAsset() {
  if (!assetPromise) {
    assetPromise = (async () => {
      const response = await fetch(FLY_VIEWER_ASSET.runtime.public_url);
      if (!response.ok) throw new Error(`Fly asset could not load (HTTP ${response.status}).`);
      const bytes = await response.arrayBuffer();
      await verifyFlyViewerBytes(bytes);
      return new GLTFLoader().parseAsync(bytes, "");
    })();
  }
  return assetPromise;
}

function Fly({ onStatus,gaitState,onGaitFailure,flightPresentation }: { flightPresentation?:WingPose; onGaitFailure:(message:string|null)=>void; gaitState?:GaitState; onStatus: (value: Status) => void }) {
  const enabled=Boolean(gaitState);
  const wingEnabled=Boolean(flightPresentation);
  const wings=useRef<ReturnType<typeof articulateWings>|null>(null);
  const previousWing=useRef<WingPose|undefined>(undefined);
  const articulation=useRef<ReturnType<typeof articulateFly>|null>(null);
  const previousGait=useRef<GaitState|undefined>(undefined);
  const ownedScene=useRef<Object3D|null>(null);
  const [instance, setInstance] = useState<ReturnType<typeof prepareFlyVisual> | null>(null);
  useEffect(() => {
    let active = true;
    let owned: ReturnType<typeof prepareFlyVisual> | undefined;
    loadAsset().then(gltf => {
      if (!active) return;
      owned = prepareFlyVisual(gltf.scene, FLY_VIEWER_ASSET, "historical", gltf.animations.length, gltf.parser);
      if(enabled){try{articulation.current=articulateFly(owned.scene,owned.nodeIdentities!);onGaitFailure(null);}catch(error){owned.dispose();owned=prepareFlyVisual(gltf.scene,FLY_VIEWER_ASSET,"historical",gltf.animations.length,gltf.parser);onGaitFailure(String(error));}}
      if(wingEnabled){try{wings.current=articulateWings(owned.scene,owned.nodeIdentities!);}catch(error){onStatus({state:"error",detail:`Wing rig unavailable; original fly retained: ${String(error)}`});}}
      ownedScene.current=owned.scene;setInstance(owned); onStatus({ state: "ready" });
    }).catch(error => { if (active) onStatus({ state: "error", detail: error instanceof Error ? error.message : "The fly asset could not be validated." }); });
    return () => { active = false; wings.current?.dispose();wings.current=null;previousWing.current=undefined;ownedScene.current=null;articulation.current?.dispose();articulation.current=null;previousGait.current=undefined;owned?.dispose(); };
  }, [onStatus,enabled,onGaitFailure,wingEnabled]);
  useFrame(()=>{const scene=ownedScene.current;if(scene&&gaitState&&articulation.current&&previousGait.current!==gaitState){const start=performance.now();scene.userData.gait={...articulation.current.apply(gaitState),bones:18,meshes:articulation.current.meshes,update_ms:performance.now()-start};previousGait.current=gaitState;}});
  useFrame(()=>{if(wings.current&&ownedScene.current?.parent&&flightPresentation&&previousWing.current!==flightPresentation){const start=performance.now();wings.current.apply(flightPresentation);ownedScene.current.userData.wings={...flightPresentation,transforms:wings.current.diagnostics(),update_ms:performance.now()-start};previousWing.current=flightPresentation;}});
  const fit = flyPresentationFit(FLY_VIEWER_ASSET, "historical");
  return instance ? <group position={fit.position} rotation={fit.rotation} scale={fit.scale} dispose={null}><primitive object={instance.scene} dispose={null} /></group> : null;
}

function Studio({ view, reset, diagnostics, onStats, onFailure, arena, locomotion, flight, flight3D }: { flight3D:boolean; flight:boolean; locomotion: boolean; arena: boolean; view: ArenaCameraView; reset: number; diagnostics: boolean; onStats: (value: ViewerStats) => void; onFailure: (message: string) => void }) {
  const { gl, size } = useThree();
  const get = useThree(state => state.get);
  const controls = useRef<OrbitControls | null>(null);
  const sample = useRef({ start: 0, frames: 0 });
  useEffect(() => {
    const { camera, scene, gl } = get();
    const orbit = new OrbitControls(camera, gl.domElement);
    orbit.enableDamping = true; orbit.enablePan = false;
    orbit.minDistance = .18; orbit.maxDistance = 12;
    controls.current = orbit;
    const lost = (event: Event) => { event.preventDefault(); onFailure("The WebGL context was lost. Reload the viewer to restore it."); };
    gl.domElement.addEventListener("webglcontextlost", lost);
    const pmrem = new PMREMGenerator(gl), room = new RoomEnvironment();
    const environment = pmrem.fromScene(room, .04);
    scene.environment = environment.texture; scene.environmentIntensity = arena ? .45 : .8;
    room.dispose(); pmrem.dispose();
    return () => { orbit.dispose(); controls.current = null; scene.environment = null; environment.dispose(); gl.domElement.removeEventListener("webglcontextlost", lost); };
  }, [get, onFailure, arena]);
  useEffect(() => {
    const { camera } = get();
    if (!(camera instanceof PerspectiveCamera) || !controls.current) return;
    const initial = arena ? arenaCamera(size.width / size.height, view) : flyViewerCamera(size.width / size.height, view === "inspect" ? "three-quarter" : view);
    const limits = arena ? arenaCameraLimits(view) : { minDistance: .18, maxDistance: 12, maxPolarAngle: Math.PI };
    controls.current.minDistance = limits.minDistance;
    controls.current.maxDistance = Math.max(limits.maxDistance, initial.distance);
    controls.current.maxPolarAngle = limits.maxPolarAngle;
    // Drain any pending orbit damping before restoring an exact camera pose.
    controls.current.enableDamping = false; controls.current.update();
    camera.position.fromArray(initial.position); camera.up.set(0, 1, 0);
    // Wider portrait inspection frames deployed wings; original modes keep their camera.
    camera.fov = flight && view === "inspect" && (flight3D || size.width / size.height < .75) ? 75 : initial.fov; camera.near = arena && view === "inspect" ? .005 : .01; camera.far = 30;
    camera.updateProjectionMatrix();
    controls.current.target.fromArray(initial.target); controls.current.update();
    controls.current.saveState(); controls.current.enableDamping = true;
  }, [get, size.width, size.height, view, reset, arena, locomotion, flight, flight3D]);
  useFrame(() => {
    controls.current?.update();
    if (arena && view === "inspect" && controls.current) {
      const { camera, scene } = get();
      if (flight && scene.getObjectByName("RecordedBodyTransform")) {
        const target = scene.getObjectByName("RecordedBodyTransform")!.getWorldPosition(new Vector3());
        camera.position.add(target.clone().sub(controls.current.target)); controls.current.target.copy(target);
      } else if (flight) {
        const offset = scene.getObjectByName("FlightPresentationTransform")?.position.y ?? 0;
        const target = new Vector3(...ARENA.flyOffset).addScaledVector(new Vector3(0,.06168119236826897,.12187743186950684),ARENA.flyScale); target.y+=offset;
        camera.position.add(target.clone().sub(controls.current.target)); controls.current.target.copy(target);
      } else if (locomotion) {
        const body = scene.getObjectByName("RecordedBodyTransform");
        if (body) { const target = body.getWorldPosition(new Vector3()); camera.position.add(target.clone().sub(controls.current.target)); controls.current.target.copy(target); }
      }
      constrainArenaInspectionCamera(camera.position);
      camera.lookAt(controls.current.target);
    }
    if (!diagnostics) { sample.current = { start: 0, frames: 0 }; return; }
    const now = performance.now();
    if (!sample.current.start) sample.current.start = now;
    sample.current.frames++;
    if (now - sample.current.start >= 1000) {
      const flightTrajectoryGeometry: NonNullable<ViewerStats['flightTrajectoryGeometry']> = {};
      for (const name of ['RecordedFlightTrajectoryCurrent', 'RecordedFlightTrajectoryReference']) {
        const line = get().scene.getObjectByName(name) as ThreeLine | undefined;
        const position = line?.geometry.getAttribute('position') as BufferAttribute | undefined;
        const count = Math.min(line?.geometry.drawRange.count ?? 0, position?.count ?? 0);
        flightTrajectoryGeometry[name] = { vertices: count, first: count ? [position!.getX(0), position!.getY(0), position!.getZ(0)] : null,
          last: count ? [position!.getX(count - 1), position!.getY(count - 1), position!.getZ(count - 1)] : null };
      }
      onStats({ flightTrajectoryGeometry, wings:(()=>{let result:unknown;get().scene.traverse(n=>{if(n.userData.wings)result=n.userData.wings;});return result;})(), stimulusPositions:[0,1].map(i=>get().scene.getObjectByName(`VisualStimulus${i}`)?.getWorldPosition(new Vector3()).toArray()), gait: (()=>{let result:unknown;get().scene.traverse(n=>{if(n.userData.gait)result=n.userData.gait;});return result;})(), comparisonMarkers: Object.fromEntries(["B","C","D","ON","OFF","P","Q"].map(key=>[key,get().scene.getObjectByName(`ComparisonMarker${key}`)?.getWorldPosition(new Vector3()).toArray()])), fps: sample.current.frames * 1000 / (now - sample.current.start), calls: gl.info.render.calls, triangles: gl.info.render.triangles, geometries: gl.info.memory.geometries, textures: gl.info.memory.textures, bodyYaw: get().scene.getObjectByName("RecordedBodyTransform")?.rotation.y, bodyPosition: get().scene.getObjectByName("RecordedBodyTransform")?.getWorldPosition(new Vector3()).toArray(), cameraPosition: get().camera.position.toArray(), cameraTarget: controls.current?.target.toArray() ?? [] });
      sample.current = { start: now, frames: 0 };
    }
  });
  if (arena) return <>
    <hemisphereLight args={["#e6edf3", "#19232d", .22]} />
    <directionalLight position={[-2, 3.5, 2]} intensity={2} color="#f6f2e9" />
    <directionalLight position={[3, 1.5, 1]} intensity={.65} color="#c8d9e6" />
    <directionalLight position={[0, 2, -2]} intensity={1.1} color="#e2e9ef" />
  </>;
  return <><hemisphereLight args={["#f3efda", "#23272c", .6]} /><directionalLight position={[-.6, 1.4, 1]} intensity={2.2} color="#ffffff" /><directionalLight position={[2, 1, -2]} intensity={.5} color="#c5dbe5" /></>;
}

class ViewerBoundary extends Component<{ children: ReactNode; onFailure: (message: string) => void }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error: Error) { this.props.onFailure(error.message || "WebGL is unavailable on this device."); }
  render() { return this.state.failed ? null : this.props.children; }
}

function RecordedTrajectory({ points }: { points: [number, number, number][] }) {
  const line = useMemo(() => new ThreeLine(new BufferGeometry().setFromPoints(points.map(p => new Vector3(p[0], .0025, p[2]))), new LineBasicMaterial({ color: "#67d3e0", transparent: true, opacity: .45 })), [points]);
  useEffect(() => () => { line.geometry.dispose(); line.material.dispose(); }, [line]);
  return <primitive object={line} dispose={null} />;
}

function LiveTrajectory({points}:{points:[number,number,number][]}) {
  const line=useMemo(()=>new ThreeLine(new BufferGeometry().setAttribute("position",new BufferAttribute(new Float32Array(1501*3),3)),new LineBasicMaterial({color:"#67d3e0",transparent:true,opacity:.65})),[]);
  useEffect(()=>()=>{line.geometry.dispose();line.material.dispose();},[line]);
  useEffect(()=>{const attr=line.geometry.getAttribute("position");points.forEach((p,i)=>attr.setXYZ(i,p[0],.003,p[2]));attr.needsUpdate=true;line.geometry.setDrawRange(0,points.length);line.geometry.computeBoundingSphere();},[line,points]);
  return <primitive object={line} dispose={null}/>;
}

const markerColors: Record<FlightTrajectoryEventKind, string> = {
  takeoff: '#67d3e0', airborne: '#a6e5dc', landing: '#f4c777', landed: '#f4c777', contact: '#f08372', endpoint: '#eef3f4',
};

function RecordedFlightPath({ layer, cursorStep, fullRecorded, color, name }: { layer: FlightTrajectoryLayer; cursorStep: number; fullRecorded: boolean; color: string; name: string }) {
  const line = useMemo(() => {
    const geometry = new BufferGeometry();
    geometry.setAttribute('position', new BufferAttribute(new Float32Array((layer.trial.stop_step + 1) * 3), 3).setUsage(DynamicDrawUsage));
    const object = new ThreeLine(geometry, new LineBasicMaterial({ color, transparent: true, opacity: .88, depthTest: true }));
    object.name = name; object.userData.engineeringTrajectorySource = layer.id;
    return object;
  }, [layer.id, layer.trial.stop_step, color, name]);
  const written = useRef(0);
  useEffect(() => () => { line.geometry.dispose(); (line.material as LineBasicMaterial).dispose(); }, [line]);
  useLayoutEffect(() => { written.current = 0; }, [line]);
  useLayoutEffect(() => {
    if (layer.frames.length < written.current) written.current = 0;
    const points = recordedFlightPositions(layer.frames);
    if (points.length > layer.trial.stop_step + 1) throw new Error('Trajectory exceeds its validated trial boundary.');
    const attribute = line.geometry.getAttribute('position') as BufferAttribute;
    for (let i = written.current; i < points.length; i++) attribute.setXYZ(i, ...points[i]);
    written.current = points.length;
    if (points.length) { attribute.needsUpdate = true; line.geometry.computeBoundingSphere(); }
  }, [line, layer.frames, layer.trial.stop_step]);
  useLayoutEffect(() => { line.geometry.setDrawRange(0, visibleFlightVertexCount(layer.frames.length, cursorStep, fullRecorded)); }, [line, layer.frames.length, cursorStep, fullRecorded]);
  return <primitive object={line} dispose={null} />;
}

function RecordedFlightEvents({ layers, markers }: { layers: FlightTrajectoryLayer[]; markers: FlightTrajectoryMarker[] }) {
  const markerCapacity = layers.reduce((sum, layer) => sum + (layer.trial.stop_step + 1) * 4 + 1, 0);
  const sourceKey = layers.map(layer => layer.id).join('|');
  const points = useMemo(() => {
    const geometry = new BufferGeometry();
    geometry.setAttribute('position', new BufferAttribute(new Float32Array(markerCapacity * 3), 3).setUsage(DynamicDrawUsage));
    geometry.setAttribute('color', new BufferAttribute(new Float32Array(markerCapacity * 3), 3).setUsage(DynamicDrawUsage));
    const object = new ThreePoints(geometry, new PointsMaterial({ size: .047, vertexColors: true, transparent: true, opacity: .96, depthTest: true, depthWrite: false, sizeAttenuation: true }));
    object.name = 'RecordedFlightEventMarkers'; object.userData.engineeringTrajectorySources = sourceKey;
    return object;
  }, [sourceKey, markerCapacity]);
  useEffect(() => () => { points.geometry.dispose(); (points.material as PointsMaterial).dispose(); }, [points]);
  useLayoutEffect(() => {
    if (markers.length > markerCapacity) throw new Error('Recorded event markers exceed bounded trajectory capacity.');
    const positions = points.geometry.getAttribute('position') as BufferAttribute;
    const colors = points.geometry.getAttribute('color') as BufferAttribute;
    markers.forEach((marker, index) => {
      positions.setXYZ(index, ...marker.position);
      const color = new Color(markerColors[marker.kind]); colors.setXYZ(index, color.r, color.g, color.b);
    });
    if (markers.length) { positions.needsUpdate = true; colors.needsUpdate = true; points.geometry.computeBoundingSphere(); }
  }, [points, markers, markerCapacity]);
  useLayoutEffect(() => { points.geometry.setDrawRange(0, markers.length); }, [points, markers.length]);
  return <primitive object={points} dispose={null} />;
}

function RecordedFlightTrajectories({ display }: { display: FlightTrajectoryDisplay }) {
  const current = display.current, reference = display.reference;
  const layers = reference ? [current, reference] : [current];
  const markers = useMemo(() => visibleFlightMarkers([
    ...recordedFlightMarkers(current.frames, current.trial, current.id),
    ...(reference ? recordedFlightMarkers(reference.frames, reference.trial, reference.id) : []),
  ].sort((a, b) => a.step - b.step || a.source.localeCompare(b.source) || a.kind.localeCompare(b.kind)), display.cursorStep, display.fullRecorded),
  [current.id, current.frames, current.trial, reference, display.cursorStep, display.fullRecorded]);
  return <>
    <RecordedFlightPath layer={display.current} cursorStep={display.cursorStep} fullRecorded={display.fullRecorded} color="#67d3e0" name="RecordedFlightTrajectoryCurrent" />
    {display.reference ? <RecordedFlightPath layer={display.reference} cursorStep={display.cursorStep} fullRecorded={display.fullRecorded} color="#f4c777" name="RecordedFlightTrajectoryReference" /> : null}
    <RecordedFlightEvents markers={markers} layers={layers} />
  </>;
}

export default function FlyViewerCanvas({ view, reset, diagnostics, onStatus, onStats, onFailure, arena = false, onTableReady, replayPose, locomotion = false, stimulusPlane, stimulusX, stimulusIds, trajectory, liveTrajectory, comparison, gaitState, onGaitFailure, flightPresentation, flightTrajectory }: { flightPresentation?:WingPose; flightTrajectory?:FlightTrajectoryDisplay; onGaitFailure:(message:string|null)=>void; gaitState?:GaitState; comparison?: ArenaOverlayProps; trajectory?: [number, number, number][]; liveTrajectory?: [number, number, number][]; stimulusPlane?: number; stimulusX?: number[]; stimulusIds?: string[]; locomotion?: boolean; replayPose?: import("@/lib/arenaCourseReplay").ArenaCoursePose; arena?: boolean; onTableReady?: () => void; view: ArenaCameraView; reset: number; diagnostics: boolean; onStatus: (value: Status) => void; onStats: (value: ViewerStats) => void; onFailure: (message: string) => void }) {
  const [webGLAvailable] = useState(() => {
    try {
      const probe = document.createElement("canvas").getContext("webgl2");
      if (!probe) return false;
      probe.getExtension("WEBGL_lose_context")?.loseContext();
      return true;
    } catch { return false; }
  });
  useEffect(() => { if (!webGLAvailable) onFailure("WebGL 2 is unavailable. Use a browser with WebGL enabled."); }, [webGLAvailable, onFailure]);
  if (!webGLAvailable) return null;
  return <ViewerBoundary onFailure={onFailure}><Canvas dpr={[1, 1.5]} camera={{ position: [1.5, 1, 2], fov: 35 }} gl={{ antialias: true, alpha: false, toneMapping: AgXToneMapping, toneMappingExposure: 1 }} fallback={null}>
    {liveTrajectory ? <LiveTrajectory points={liveTrajectory}/> : null}
    {comparison ? <ArenaComparison {...comparison}/> : null}
    {trajectory ? <RecordedTrajectory points={trajectory} /> : null}
    {flightTrajectory ? <RecordedFlightTrajectories display={flightTrajectory} /> : null}
    <color attach="background" args={["#182129"]} />
    <Studio flight3D={flightPresentation?.source === 'ENGINEERING_3D_FLIGHT_V8'} flight={Boolean(flightPresentation)} view={view} reset={reset} diagnostics={diagnostics} onStats={onStats} onFailure={onFailure} arena={arena} locomotion={locomotion} />
    <group name="FlightPresentationTransform" position={[0,flightPresentation?.offset??0,0]}>
    {arena && replayPose ? <group name="RecordedBodyTransform" userData={{ replayAnchor: replayPose.anchor }} position={replayPose.anchor} rotation={[0, replayPose.rotation, 0]} scale={ARENA.flyScale}><group position={replayPose.assetOffset}><Fly flightPresentation={flightPresentation} onGaitFailure={onGaitFailure} gaitState={gaitState} onStatus={onStatus} /></group></group> : <group position={arena ? ARENA.flyOffset : [0, 0, 0]} scale={arena ? ARENA.flyScale : 1}><Fly flightPresentation={flightPresentation} onGaitFailure={onGaitFailure} gaitState={gaitState} onStatus={onStatus} /></group>}
    </group>
    {arena && onTableReady ? <ExperimentalArena stimulusPlane={stimulusPlane} stimulusX={stimulusX} stimulusIds={stimulusIds} shadowAnchor={locomotion || flightPresentation?.source === 'ENGINEERING_3D_FLIGHT_V8' ? replayPose?.anchor : undefined} onReady={onTableReady} onFailure={onFailure} /> : null}
  </Canvas></ViewerBoundary>;
}
