"use client";

import { useLoader } from "@react-three/fiber";
import { Suspense, useEffect, useMemo } from "react";
import { DoubleSide, Mesh, MeshPhysicalMaterial } from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { ProceduralFlyPlaceholder } from "./FlyVisualAsset";
import { FLY_VISUAL_ASSET, type FlyAssetLoadStatus } from "@/lib/flyVisualAsset";

function Specimen({ onStatusChange }: { onStatusChange: (status: FlyAssetLoadStatus) => void }) {
  const gltf = useLoader(GLTFLoader, FLY_VISUAL_ASSET.runtime.public_url);
  // Clone nodes/materials: never mutate the loader cache or historical cockpit.
  const prepared = useMemo(() => {
    const scene = gltf.scene.clone(true);
    const body = new MeshPhysicalMaterial({ color: "#554431", roughness: 0.68, metalness: 0, clearcoat: 0.12 });
    const eyes = new MeshPhysicalMaterial({ color: "#702b1c", roughness: 0.43, metalness: 0, clearcoat: 0.2, flatShading: true });
    const wings = new MeshPhysicalMaterial({ color: "#cfccbb", roughness: 0.4, transparent: true, opacity: 0.22, depthWrite: false, side: DoubleSide });
    scene.traverse(node => {
      if (!(node instanceof Mesh)) return;
      node.material = node.name.startsWith("Wing") ? wings : node.name.startsWith("Eye") ? eyes : body;
      node.castShadow = !node.name.startsWith("Wing");
      node.receiveShadow = true;
    });
    return { scene, materials: [body, eyes, wings] };
  }, [gltf.scene]);
  useEffect(() => { onStatusChange("ready"); }, [onStatusChange]);
  useEffect(() => () => prepared.materials.forEach(m => m.dispose()), [prepared]);
  return <group position={[0, 0.64, 0]} scale={3.3}><primitive object={prepared.scene} /></group>;
}

export function ScenarioFlyVisual({ onStatusChange }: { onStatusChange: (status: FlyAssetLoadStatus) => void }) {
  return <Suspense fallback={<ProceduralFlyPlaceholder />}><Specimen onStatusChange={onStatusChange} /></Suspense>;
}
