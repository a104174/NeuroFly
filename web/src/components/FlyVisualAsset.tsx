"use client";

import { useLoader } from "@react-three/fiber";
import {
  Component,
  Suspense,
  useEffect,
  type ErrorInfo,
  type ReactNode,
} from "react";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

import {
  FLY_VISUAL_ASSET,
  type FlyAssetLoadStatus,
} from "@/lib/flyVisualAsset";

export function ProceduralFlyPlaceholder() {
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

function AssetLoading({
  onStatusChange,
}: {
  onStatusChange: (status: FlyAssetLoadStatus) => void;
}) {
  useEffect(() => onStatusChange("loading"), [onStatusChange]);
  return <ProceduralFlyPlaceholder />;
}

function LoadedFlyVisualAsset({
  onStatusChange,
}: {
  onStatusChange: (status: FlyAssetLoadStatus) => void;
}) {
  const gltf = useLoader(GLTFLoader, FLY_VISUAL_ASSET.runtime.public_url);
  useEffect(() => onStatusChange("ready"), [onStatusChange]);
  const transform = FLY_VISUAL_ASSET.canonical_transform;
  return (
    <group
      position={transform.scene_position}
      rotation={transform.scene_rotation_euler_rad}
      scale={transform.scene_uniform_scale}
    >
      <primitive object={gltf.scene} />
    </group>
  );
}

class AssetErrorBoundary extends Component<
  {
    children: ReactNode;
    onStatusChange: (status: FlyAssetLoadStatus) => void;
  },
  { failed: boolean }
> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(_error: Error, _info: ErrorInfo) {
    this.props.onStatusChange("error");
    console.warn("NeuroFly fly visual asset failed; using procedural fallback.");
  }

  render() {
    return this.state.failed ? <ProceduralFlyPlaceholder /> : this.props.children;
  }
}

export function FlyVisualAsset({
  onStatusChange,
}: {
  onStatusChange: (status: FlyAssetLoadStatus) => void;
}) {
  return (
    <AssetErrorBoundary onStatusChange={onStatusChange}>
      <Suspense fallback={<AssetLoading onStatusChange={onStatusChange} />}>
        <LoadedFlyVisualAsset onStatusChange={onStatusChange} />
      </Suspense>
    </AssetErrorBoundary>
  );
}
