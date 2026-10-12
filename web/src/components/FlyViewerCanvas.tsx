"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { ARENA, arenaCamera, arenaCameraLimits, constrainArenaInspectionCamera, type ArenaCameraView } from "@/lib/experimentalArena";
import { ExperimentalArena } from "./ExperimentalArena";
import { Component, useEffect, useRef, useState, type ReactNode } from "react";
import { AgXToneMapping, PMREMGenerator, PerspectiveCamera } from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { GLTFLoader, type GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import { flyPresentationFit, prepareFlyVisual } from "@/lib/flyVisualInstance";
import { FLY_VIEWER_ASSET, flyViewerCamera, verifyFlyViewerBytes } from "@/lib/flyViewer";

export type ViewerStats = { fps: number; calls: number; triangles: number; geometries: number; textures: number; cameraPosition: number[]; cameraTarget: number[] };
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

function Fly({ onStatus }: { onStatus: (value: Status) => void }) {
  const [instance, setInstance] = useState<ReturnType<typeof prepareFlyVisual> | null>(null);
  useEffect(() => {
    let active = true;
    let owned: ReturnType<typeof prepareFlyVisual> | undefined;
    loadAsset().then(gltf => {
      if (!active) return;
      owned = prepareFlyVisual(gltf.scene, FLY_VIEWER_ASSET, "historical", gltf.animations.length, gltf.parser);
      setInstance(owned); onStatus({ state: "ready" });
    }).catch(error => { if (active) onStatus({ state: "error", detail: error instanceof Error ? error.message : "The fly asset could not be validated." }); });
    return () => { active = false; owned?.dispose(); };
  }, [onStatus]);
  const fit = flyPresentationFit(FLY_VIEWER_ASSET, "historical");
  return instance ? <group position={fit.position} rotation={fit.rotation} scale={fit.scale} dispose={null}><primitive object={instance.scene} dispose={null} /></group> : null;
}

function Studio({ view, reset, diagnostics, onStats, onFailure, arena }: { arena: boolean; view: ArenaCameraView; reset: number; diagnostics: boolean; onStats: (value: ViewerStats) => void; onFailure: (message: string) => void }) {
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
    camera.fov = initial.fov; camera.near = arena && view === "inspect" ? .005 : .01; camera.far = 30;
    camera.updateProjectionMatrix();
    controls.current.target.fromArray(initial.target); controls.current.update();
    controls.current.saveState(); controls.current.enableDamping = true;
  }, [get, size.width, size.height, view, reset, arena]);
  useFrame(() => {
    controls.current?.update();
    if (arena && view === "inspect" && controls.current) {
      const camera = get().camera;
      constrainArenaInspectionCamera(camera.position);
      camera.lookAt(controls.current.target);
    }
    if (!diagnostics) { sample.current = { start: 0, frames: 0 }; return; }
    const now = performance.now();
    if (!sample.current.start) sample.current.start = now;
    sample.current.frames++;
    if (now - sample.current.start >= 1000) {
      onStats({ fps: sample.current.frames * 1000 / (now - sample.current.start), calls: gl.info.render.calls, triangles: gl.info.render.triangles, geometries: gl.info.memory.geometries, textures: gl.info.memory.textures, cameraPosition: get().camera.position.toArray(), cameraTarget: controls.current?.target.toArray() ?? [] });
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

export default function FlyViewerCanvas({ view, reset, diagnostics, onStatus, onStats, onFailure, arena = false, onTableReady }: { arena?: boolean; onTableReady?: () => void; view: ArenaCameraView; reset: number; diagnostics: boolean; onStatus: (value: Status) => void; onStats: (value: ViewerStats) => void; onFailure: (message: string) => void }) {
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
    <color attach="background" args={["#182129"]} />
    <Studio view={view} reset={reset} diagnostics={diagnostics} onStats={onStats} onFailure={onFailure} arena={arena} />
    <group position={arena ? ARENA.flyOffset : [0, 0, 0]} scale={arena ? ARENA.flyScale : 1}><Fly onStatus={onStatus} /></group>
    {arena && onTableReady ? <ExperimentalArena onReady={onTableReady} onFailure={onFailure} /> : null}
  </Canvas></ViewerBoundary>;
}
