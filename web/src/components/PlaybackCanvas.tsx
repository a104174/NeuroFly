"use client";

import { Canvas } from "@react-three/fiber";
import { useState } from "react";

import type { ExperimentSceneState } from "@/lib/playback";

function FlyPlaceholder() {
  return (
    <group position={[0, 0.78, 0]} rotation={[0.06, 0, 0]}>
      <mesh scale={[0.62, 0.55, 0.82]}>
        <sphereGeometry args={[0.72, 32, 20]} />
        <meshStandardMaterial color="#24383d" roughness={0.72} />
      </mesh>
      <mesh position={[0, 0.02, -0.88]} scale={[0.48, 0.48, 0.92]}>
        <sphereGeometry args={[0.62, 32, 20]} />
        <meshStandardMaterial color="#18272c" roughness={0.78} />
      </mesh>
      <mesh position={[0, 0.04, 0.72]} scale={[0.7, 0.62, 0.58]}>
        <sphereGeometry args={[0.5, 32, 20]} />
        <meshStandardMaterial color="#31484c" roughness={0.7} />
      </mesh>
      <mesh position={[-0.25, 0.08, 0.96]} scale={[0.42, 0.5, 0.22]}>
        <sphereGeometry args={[0.28, 24, 16]} />
        <meshStandardMaterial color="#7f4039" roughness={0.5} />
      </mesh>
      <mesh position={[0.25, 0.08, 0.96]} scale={[0.42, 0.5, 0.22]}>
        <sphereGeometry args={[0.28, 24, 16]} />
        <meshStandardMaterial color="#7f4039" roughness={0.5} />
      </mesh>
      <mesh
        position={[-0.78, 0.2, -0.08]}
        rotation={[0.1, -0.18, 0.35]}
        scale={[1.1, 0.08, 0.46]}
      >
        <sphereGeometry args={[0.72, 28, 14]} />
        <meshStandardMaterial
          color="#8ba8aa"
          transparent
          opacity={0.36}
          roughness={0.35}
        />
      </mesh>
      <mesh
        position={[0.78, 0.2, -0.08]}
        rotation={[0.1, 0.18, -0.35]}
        scale={[1.1, 0.08, 0.46]}
      >
        <sphereGeometry args={[0.72, 28, 14]} />
        <meshStandardMaterial
          color="#8ba8aa"
          transparent
          opacity={0.36}
          roughness={0.35}
        />
      </mesh>
    </group>
  );
}

function LoomingProxy({ level }: { level: number }) {
  const scale = 0.32 + level * 1.28;
  const z = -4.1 + level * 1.7;
  return (
    <group position={[0, 1.45, z]} scale={scale}>
      <mesh>
        <sphereGeometry args={[0.72, 36, 24]} />
        <meshStandardMaterial
          color="#c18d58"
          emissive="#6d3e20"
          emissiveIntensity={0.25 + level * 0.7}
          roughness={0.58}
        />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]} scale={1.14}>
        <torusGeometry args={[0.72, 0.025, 12, 60]} />
        <meshBasicMaterial
          color="#e5bd79"
          transparent
          opacity={0.32 + level * 0.38}
        />
      </mesh>
    </group>
  );
}

function ActivityNode({
  color,
  level,
  position,
  spike = false,
}: {
  color: string;
  level: number;
  position: [number, number, number];
  spike?: boolean;
}) {
  const scale = 0.18 + level * 0.18;
  return (
    <group position={position}>
      <mesh scale={scale}>
        <sphereGeometry args={[1, 24, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.15 + level * 1.4 + (spike ? 0.7 : 0)}
          roughness={0.48}
        />
      </mesh>
      {spike ? (
        <mesh rotation={[Math.PI / 2, 0, 0]} scale={0.44}>
          <torusGeometry args={[1, 0.06, 10, 36]} />
          <meshBasicMaterial color={color} transparent opacity={0.72} />
        </mesh>
      ) : null}
    </group>
  );
}

function ScientificScene({ sceneState }: { sceneState: ExperimentSceneState }) {
  return (
    <>
      <color attach="background" args={["#071013"]} />
      <fog attach="fog" args={["#071013", 7, 16]} />
      <ambientLight intensity={0.82} />
      <directionalLight position={[4, 7, 5]} intensity={1.7} color="#d6ebe9" />
      <directionalLight
        position={[-4, 2, -3]}
        intensity={0.45}
        color="#6aa8a7"
      />
      <gridHelper
        args={[12, 24, "#1e464b", "#10262b"]}
        position={[0, -0.03, 0]}
      />
      <FlyPlaceholder />
      <LoomingProxy level={sceneState.stimulusPresentationLevel} />
      <ActivityNode
        color="#72d5d0"
        level={sceneState.lc4PresentationLevel}
        position={[-2.25, 0.42, 0.5]}
      />
      <ActivityNode
        color="#87a9ff"
        level={sceneState.lplc2PresentationLevel}
        position={[-1.35, 0.42, 0.5]}
      />
      <ActivityNode
        color="#e5bd79"
        level={sceneState.dnp01[10001].presentationLevel}
        position={[1.35, 0.42, 0.5]}
        spike={sceneState.dnp01[10001].spikedAtSelectedBoundary}
      />
      <ActivityNode
        color="#e58d79"
        level={sceneState.dnp01[10010].presentationLevel}
        position={[2.25, 0.42, 0.5]}
        spike={sceneState.dnp01[10010].spikedAtSelectedBoundary}
      />
    </>
  );
}

function detectWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") ?? canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

export function PlaybackCanvas({
  sceneState,
}: {
  sceneState: ExperimentSceneState;
}) {
  const [webGLAvailable] = useState(detectWebGL);
  if (!webGLAvailable) {
    return (
      <div className="playback-canvas-fallback">
        3D playback is unavailable in this browser.
      </div>
    );
  }
  return (
    <Canvas
      camera={{ position: [0, 3.35, 8.2], fov: 38, near: 0.1, far: 30 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: false }}
      frameloop="demand"
    >
      <ScientificScene sceneState={sceneState} />
    </Canvas>
  );
}
