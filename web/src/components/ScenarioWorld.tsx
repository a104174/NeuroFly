"use client";

import { Canvas, useThree } from "@react-three/fiber";
import { Component, useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { BufferGeometry, Line, LineDashedMaterial, PCFShadowMap, PerspectiveCamera, Vector3 } from "three";
import { ScenarioFlyVisual } from "./ScenarioFlyVisual";
import type { FlyAssetLoadStatus } from "@/lib/flyVisualAsset";
import { PRESENTATION_SCALE, scenarioScene, type ScenarioPlaybackResult } from "@/lib/scenarioPlayback";

class SceneBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <p role="alert" className="scenario-scene-error">3D rendering unavailable. Authoritative timeline and telemetry remain available below.</p> : this.props.children; }
}

function PresentationCamera({ baseline }: { baseline: boolean }) {
  const { camera, size, invalidate } = useThree();
  useEffect(() => {
    if (!(camera instanceof PerspectiveCamera)) return;
    const compact = size.width < 600;
    camera.position.set(...(baseline ? compact ? [7, 4, -4.5] : [4.8, 2.8, -3] : compact ? [13, 8, -7] : [9, 4.6, -2.5]) as [number, number, number]);
    // Three.js owns an imperative camera; this is render-only, not React state.
    // eslint-disable-next-line react-hooks/immutability
    camera.fov = compact ? 43 : baseline ? 34 : 36;
    camera.lookAt(0, 0.6, baseline ? 0 : 2.6);
    camera.updateProjectionMatrix(); camera.updateMatrixWorld(); invalidate();
  }, [baseline, camera, size.width, size.height, invalidate]);
  return null;
}

function ApproachGuide({ result }: { result: ScenarioPlaybackResult }) {
  const path = useMemo(() => {
    const first = result.frames[0];
    if (!first.object) return null;
    const points = result.frames.map(f => new Vector3(f.object!.x_world_eq * PRESENTATION_SCALE, 0.035, f.object!.z_world_eq * PRESENTATION_SCALE));
    points.push(new Vector3(first.body.x_world_eq * PRESENTATION_SCALE, 0.035, first.body.z_world_eq * PRESENTATION_SCALE));
    const line = new Line(new BufferGeometry().setFromPoints(points), new LineDashedMaterial({ color: "#b69768", dashSize: 0.18, gapSize: 0.14, transparent: true, opacity: 0.45 }));
    line.computeLineDistances();
    return line;
  }, [result]);
  useEffect(() => () => { path?.geometry.dispose(); if (path?.material instanceof LineDashedMaterial) path.material.dispose(); }, [path]);
  // No opaque ghost objects: one dashed presentation guide only.
  return path ? <primitive object={path} /> : null;
}

export default function ScenarioWorld({ result, cursor }: { result: ScenarioPlaybackResult; cursor: number }) {
  const scene = scenarioScene(result, cursor);
  const baseline = result.scenario.id === "BASELINE_CONTROL";
  const [assetStatus, setAssetStatus] = useState<FlyAssetLoadStatus>("loading");
  const reportAsset = useCallback((status: FlyAssetLoadStatus) => setAssetStatus(status), []);
  return <div className={`scenario-world ${baseline ? "control-world" : "looming-world"}`} aria-label="Authoritative scenario 3D playback">
    <SceneBoundary><Canvas shadows={{ type: PCFShadowMap }} frameloop="demand" dpr={[1, 1.5]}
      camera={{ position: baseline ? [4.8, 2.8, -3] : [9, 4.6, -2.5], fov: baseline ? 34 : 36 }}
      onCreated={({ camera }) => { camera.lookAt(0, 0.6, baseline ? 0 : 2.6); camera.updateMatrixWorld(); }}
      fallback={<p>WebGL unavailable; use the scientific telemetry.</p>}>
      <PresentationCamera baseline={baseline} />
      <color attach="background" args={["#161d20"]} />
      <fog attach="fog" args={["#161d20", 14, 30]} />
      <hemisphereLight args={["#e4dfce", "#554a3e", 1.25]} />
      <directionalLight castShadow position={[2, 7, -3]} intensity={2.1} color="#ffe7bf" shadow-mapSize={[1024, 1024]} shadow-camera-left={-6} shadow-camera-right={6} shadow-camera-top={8} shadow-camera-bottom={-5} shadow-bias={-0.001} />
      <directionalLight position={[-4, 3, 5]} intensity={1.3} color="#bbced1" />
      <gridHelper args={[30, 30, "#303b3e", "#242d30"]} position={[0, -0.015, 0]} />
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.03, 0]}><planeGeometry args={[60, 60]} /><meshStandardMaterial color="#1c2427" roughness={0.95} /></mesh>
      <group name="authoritative-fly" position={scene.bodyPosition}><ScenarioFlyVisual onStatusChange={reportAsset} /></group>
      {!baseline && <ApproachGuide result={result} />}
      {scene.objectPosition && scene.objectRadius !== null && <mesh name="authoritative-looming-object" position={scene.objectPosition} scale={scene.objectRadius} castShadow>
        <sphereGeometry args={[1, 40, 28]} /><meshStandardMaterial color="#9b623f" roughness={0.8} metalness={0} />
      </mesh>}
    </Canvas></SceneBoundary>
    <div className="scene-title"><span className="eyebrow">{baseline ? "BASELINE CONTROL" : "WORLD / MODEL-SPACE PRESENTATION"}</span><p>{baseline ? "No external stimulus. Stationary by design." : "One approaching object. No scripted fly response."}</p></div>
    <div className="scene-fly-label">Fly <small>Authoritative body state · {assetStatus === "ready" ? "project visual asset" : "loading visual asset"}</small></div>
    {!baseline && <>
      <div className="scene-object-label">Looming object <small>Approaching toward the fly →</small></div>
      <div className="scene-projection" aria-label="Exploratory sensory projection">
        <span className="projection-glyph" aria-hidden="true">⌾</span>
        <div><span className="eyebrow">EXPLORATORY SENSORY PROJECTION</span><strong>Radius {scene.frame.lattice_radius} · {scene.frame.active_sensory_body_count} / 311 exposed</strong><small>Fixed relative-column centre · not a calibrated retinal map</small></div>
      </div>
    </>}
    <details className="scene-legend"><summary>Scene guide</summary><p>Fly: project visual asset. {baseline ? "No stimulus, path or projection is active." : "Solid object: current authoritative position. Dashed line: approach guide, not another object. Inset: backend relative-column exposure, not retinal geometry."} Grid and shadows are presentation references, not contact physics.</p></details>
  </div>;
}
