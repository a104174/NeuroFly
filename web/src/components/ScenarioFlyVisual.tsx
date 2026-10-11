"use client";

import { useLoader } from "@react-three/fiber";
import { Suspense, useEffect, useMemo } from "react";
import { flyPresentationFit, prepareFlyVisual } from "@/lib/flyVisualInstance";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { ProceduralFlyPlaceholder } from "./FlyVisualAsset";
import { FLY_VISUAL_ASSET, type FlyAssetLoadStatus } from "@/lib/flyVisualAsset";

function Specimen({ onStatusChange }: { onStatusChange: (status: FlyAssetLoadStatus) => void }) {
  const gltf = useLoader(GLTFLoader, FLY_VISUAL_ASSET.runtime.public_url);
  const prepared = useMemo(() => prepareFlyVisual(gltf.scene, FLY_VISUAL_ASSET, "scenario", gltf.animations.length, gltf.parser), [gltf.scene, gltf.animations.length, gltf.parser]);
  const fit = flyPresentationFit(FLY_VISUAL_ASSET, "scenario");
  useEffect(() => { onStatusChange("ready"); }, [onStatusChange]);
  useEffect(() => { prepared.activate(); return () => prepared.dispose(); }, [prepared]);
  return <group position={fit.position} rotation={fit.rotation} scale={fit.scale}><primitive object={prepared.scene} /></group>;
}

export function ScenarioFlyVisual({ onStatusChange }: { onStatusChange: (status: FlyAssetLoadStatus) => void }) {
  return <Suspense fallback={<ProceduralFlyPlaceholder />}><Specimen onStatusChange={onStatusChange} /></Suspense>;
}
