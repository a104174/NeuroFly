"use client";

import { Canvas } from "@react-three/fiber";
import { useEffect, useMemo, useState } from "react";
import { Quaternion, Vector3 } from "three";

import { FlyVisualAsset } from "@/components/FlyVisualAsset";
import type { FlyAssetLoadStatus } from "@/lib/flyVisualAsset";
import type { ExperimentSceneState } from "@/lib/playback";
import {
  derivePresentationOverlayState,
  SCENE_PRESENTATION_LAYOUT,
  type PresentationPoint,
} from "@/lib/sceneLayout";

function vectorTuple(point: PresentationPoint): [number, number, number] {
  return [point[0], point[1], point[2]];
}

function PresentationSegment({
  start,
  end,
  color,
  opacity,
  radius = 0.018,
}: {
  start: PresentationPoint;
  end: PresentationPoint;
  color: string;
  opacity: number;
  radius?: number;
}) {
  const transform = useMemo(() => {
    const startVector = new Vector3(...start);
    const endVector = new Vector3(...end);
    const direction = endVector.clone().sub(startVector);
    const length = direction.length();
    const midpoint = startVector.clone().add(endVector).multiplyScalar(0.5);
    const quaternion = new Quaternion().setFromUnitVectors(
      new Vector3(0, 1, 0),
      direction.normalize(),
    );
    return { length, midpoint, quaternion };
  }, [end, start]);

  return (
    <mesh position={transform.midpoint} quaternion={transform.quaternion}>
      <cylinderGeometry args={[radius, radius, transform.length, 8]} />
      <meshBasicMaterial color={color} transparent opacity={opacity} />
    </mesh>
  );
}

function LoomingPresentation({
  position,
  scale,
  level,
}: {
  position: PresentationPoint;
  scale: number;
  level: number;
}) {
  const layout = SCENE_PRESENTATION_LAYOUT.looming;
  return (
    <>
      <PresentationSegment
        start={layout.axis_start}
        end={layout.axis_end}
        color="#765d42"
        opacity={0.34}
        radius={layout.corridor_radius}
      />
      <group position={vectorTuple(position)} scale={scale}>
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
    </>
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

function ScientificScene({
  sceneState,
  onAssetStatusChange,
}: {
  sceneState: ExperimentSceneState;
  onAssetStatusChange: (status: FlyAssetLoadStatus) => void;
}) {
  const presentation = derivePresentationOverlayState(sceneState);
  const layout = SCENE_PRESENTATION_LAYOUT;
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
        args={[
          layout.reference_grid.size,
          layout.reference_grid.divisions,
          layout.reference_grid.major_color,
          layout.reference_grid.minor_color,
        ]}
        position={vectorTuple(layout.reference_grid.position)}
      />
      <FlyVisualAsset onStatusChange={onAssetStatusChange} />
      <LoomingPresentation
        position={presentation.looming.presentationPosition}
        scale={presentation.looming.presentationScale}
        level={presentation.looming.presentationLevel}
      />
      {(["LC4", "LPLC2"] as const).flatMap((pathwayId) =>
        ([10001, 10010] as const).map((bodyId) => (
          <PresentationSegment
            key={`${pathwayId}-${bodyId}`}
            start={layout.pathways[pathwayId].anchor}
            end={layout.dnp01[bodyId].anchor}
            color={layout.pathways[pathwayId].color}
            opacity={presentation.pathways[pathwayId].presentationIntensity}
          />
        )),
      )}
      <ActivityNode
        color={layout.pathways.LC4.color}
        level={presentation.pathways.LC4.presentationLevel}
        position={vectorTuple(layout.pathways.LC4.anchor)}
      />
      <ActivityNode
        color={layout.pathways.LPLC2.color}
        level={presentation.pathways.LPLC2.presentationLevel}
        position={vectorTuple(layout.pathways.LPLC2.anchor)}
      />
      <ActivityNode
        color={layout.dnp01[10001].color}
        level={presentation.dnp01[10001].presentationLevel}
        position={vectorTuple(layout.dnp01[10001].anchor)}
        spike={presentation.dnp01[10001].persistedBoundarySpike}
      />
      <ActivityNode
        color={layout.dnp01[10010].color}
        level={presentation.dnp01[10010].presentationLevel}
        position={vectorTuple(layout.dnp01[10010].anchor)}
        spike={presentation.dnp01[10010].persistedBoundarySpike}
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
  onAssetStatusChange,
}: {
  sceneState: ExperimentSceneState;
  onAssetStatusChange: (status: FlyAssetLoadStatus) => void;
}) {
  const [webGLAvailable] = useState(detectWebGL);
  useEffect(() => {
    if (!webGLAvailable) onAssetStatusChange("error");
  }, [onAssetStatusChange, webGLAvailable]);
  if (!webGLAvailable) {
    return (
      <div className="playback-canvas-fallback">
        3D playback is unavailable in this browser.
      </div>
    );
  }
  return (
    <Canvas
      camera={{
        position: vectorTuple(SCENE_PRESENTATION_LAYOUT.camera.position),
        fov: SCENE_PRESENTATION_LAYOUT.camera.field_of_view_degrees,
        near: SCENE_PRESENTATION_LAYOUT.camera.near,
        far: SCENE_PRESENTATION_LAYOUT.camera.far,
      }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: false }}
      frameloop="demand"
    >
      <ScientificScene
        sceneState={sceneState}
        onAssetStatusChange={onAssetStatusChange}
      />
    </Canvas>
  );
}
