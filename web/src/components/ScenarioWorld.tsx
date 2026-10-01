"use client";

import { Canvas } from "@react-three/fiber";
import { Component, useCallback, useState, type ReactNode } from "react";
import { FlyVisualAsset } from "@/components/FlyVisualAsset";
import type { FlyAssetLoadStatus } from "@/lib/flyVisualAsset";
import { scenarioScene, type ScenarioPlaybackResult } from "@/lib/scenarioPlayback";

class SceneBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <p role="alert" className="scenario-scene-error">3D rendering unavailable. Authoritative timeline and telemetry remain available below.</p> : this.props.children; }
}
export default function ScenarioWorld({ result, cursor }: { result: ScenarioPlaybackResult; cursor: number }) {
  const scene = scenarioScene(result, cursor);
  const [assetStatus, setAssetStatus] = useState<FlyAssetLoadStatus>("loading");
  const reportAsset = useCallback((status: FlyAssetLoadStatus) => setAssetStatus(status), []);
  return <div className="scenario-world" aria-label="Authoritative scenario 3D playback">
    <SceneBoundary><Canvas camera={{ position: [9, 8, 11], fov: 43 }} fallback={<p>WebGL unavailable; use the scientific telemetry.</p>}>
      <color attach="background" args={["#0d1c22"]} />
      <ambientLight intensity={1.1} />
      <directionalLight position={[3, 8, 2]} intensity={2.6} />
      <gridHelper args={[24, 24, "#35545b", "#203940"]} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}><planeGeometry args={[24, 24]} /><meshStandardMaterial color="#10242b" roughness={1} /></mesh>
      <group position={scene.bodyPosition}><FlyVisualAsset onStatusChange={reportAsset} /></group>
      {scene.objectPosition && scene.objectRadius !== null && <mesh position={scene.objectPosition} scale={scene.objectRadius}>
        <sphereGeometry args={[1, 40, 28]} /><meshStandardMaterial color="#cd9c68" roughness={0.52} metalness={0.12} />
      </mesh>}
    </Canvas></SceneBoundary>
    <div className="scenario-world-label"><span>+Z FORWARD · DISPLAY GRID ONLY</span><span>{assetStatus === "ready" ? "FLY ASSET" : assetStatus === "error" ? "VISUAL PLACEHOLDER" : "LOADING FLY ASSET"}</span></div>
  </div>;
}
