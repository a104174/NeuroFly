"use client";

import { useEffect, useState } from "react";
import { DoubleSide, Mesh, MeshStandardMaterial, type Object3D } from "three";
import { GLTFLoader, type GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import { ARENA, arenaPanels, prepareArenaTable, loadArenaTableBytes } from "@/lib/experimentalArena";

let tablePromise: Promise<GLTF> | undefined;
function loadTable() {
  if (!tablePromise) tablePromise = (async () => {
    const files = await loadArenaTableBytes();
    const urls: string[] = [];
    try {
      // Parse verified bytes, including the texture. No remote or missing-texture fallback.
      const source = JSON.parse(new TextDecoder().decode(files.get("scene.gltf")));
      if (source.asset?.version !== "2.0" || source.buffers?.length !== 1 || source.images?.length !== 1) throw new Error("Unsupported Lab Table source format.");
      for (const entry of [...source.buffers, ...source.images]) {
        const bytes = files.get(entry.uri);
        if (!bytes) throw new Error("Lab Table references an unavailable dependency.");
        const url = URL.createObjectURL(new Blob([bytes])); urls.push(url); entry.uri = url;
      }
      const gltf = await new GLTFLoader().parseAsync(JSON.stringify(source), "");
      gltf.scene.traverse(node => {
        if (!(node instanceof Mesh)) return;
        const materials = Array.isArray(node.material) ? node.material : [node.material];
        if (materials.some(material => !(material instanceof MeshStandardMaterial) || !material.map)) throw new Error("Lab Table texture could not be decoded.");
      });
      return gltf;
    } finally { urls.forEach(url => URL.revokeObjectURL(url)); }
  })();
  return tablePromise;
}

function LabTable({ onReady, onFailure }: { onReady: () => void; onFailure: (message: string) => void }) {
  const [object, setObject] = useState<Object3D | null>(null);
  useEffect(() => {
    let active = true;
    let owned: ReturnType<typeof prepareArenaTable> | undefined;
    loadTable().then(gltf => {
      if (!active) return;
      owned = prepareArenaTable(gltf.scene);
      setObject(owned.scene); onReady();
    }).catch(error => { if (active) onFailure(error instanceof Error ? error.message : "Lab Table could not be loaded."); });
    return () => { active = false; owned?.dispose(); };
  }, [onReady, onFailure]);
  return object ? <primitive object={object} dispose={null} /> : null;
}

function Solid({ position, size, color = "#34454e", roughness = .8, metalness = .05 }: { position: [number, number, number]; size: [number, number, number]; color?: string; roughness?: number; metalness?: number }) {
  return <mesh position={position}><boxGeometry args={size} /><meshStandardMaterial color={color} roughness={roughness} metalness={metalness} /></mesh>;
}

/** Original in-house enclosure and backdrop. No behavioral apparatus or data implied. */
export function ExperimentalArena({ onReady, onFailure, shadowAnchor }: { shadowAnchor?: [number, number, number]; onReady: () => void; onFailure: (message: string) => void }) {
  const { width: w, depth: d, height: h, floor: f } = ARENA.chamber;
  const panels = arenaPanels();
  return <>
    <LabTable onReady={onReady} onFailure={onFailure} />
    <Solid position={[0, -f / 2, 0]} size={[w + .08, f, d + .08]} color="#555c61" roughness={.95} metalness={0} />
    {panels.map(panel => <mesh key={panel.id} position={panel.position} renderOrder={2}>
      <boxGeometry args={panel.size} /><meshStandardMaterial color="#f4f5f4" transparent opacity={.018} roughness={.28} metalness={0} side={DoubleSide} forceSinglePass depthWrite={false} />
    </mesh>)}
    {[-w / 2, w / 2].flatMap(x => [-d / 2, d / 2].map(z => <Solid key={`${x}:${z}`} position={[x, h / 2, z]} size={[.014, h, .014]} color="#52616b" roughness={.42} metalness={.65} />))}
    {[0, h].flatMap(y => [<Solid key={`front${y}`} position={[0, y, d / 2]} size={[w, .012, .012]} color="#52616b" roughness={.42} metalness={.65} />, <Solid key={`back${y}`} position={[0, y, -d / 2]} size={[w, .012, .012]} color="#52616b" roughness={.42} metalness={.65} />])}
    {[-w / 2, w / 2].map(x => <Solid key={`lid${x}`} position={[x, h, 0]} size={[.012, .012, d]} color="#52616b" roughness={.42} metalness={.65} />)}
    <mesh position={[shadowAnchor?.[0] ?? ARENA.flyOffset[0], .0008, shadowAnchor ? shadowAnchor[2] - .018 : ARENA.flyOffset[2] - .018]} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[.22, .34]} />
      <shaderMaterial transparent depthWrite={false}
        vertexShader="varying vec2 uvPosition; void main() { uvPosition = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }"
        fragmentShader="varying vec2 uvPosition; void main() { float shade = 1.0 - smoothstep(0.04, 0.5, length(uvPosition - 0.5)); gl_FragColor = vec4(0.0, 0.0, 0.0, shade * 0.20); }" />
    </mesh>
    <Solid position={[0, -2.5, 0]} size={[10, .08, 9]} color="#151e25" roughness={.94} metalness={0} />
    <Solid position={[0, .2, -2.4]} size={[12, 5.4, .12]} color="#17242e" roughness={.94} metalness={0} />
    {[-2.8, -1.4, 0, 1.4, 2.8].map(x => <Solid key={x} position={[x, .3, -2.31]} size={[.016, 4.7, .025]} color="#1a2b35" />)}
    <Solid position={[0, 1.65, -2.29]} size={[6.4, .025, .04]} color="#2b414d" />
    <Solid position={[2.35, -.3, -1.55]} size={[.5, .6, .45]} color="#34464e" />
    <Solid position={[2.35, -.02, -1.30]} size={[.33, .06, .012]} color="#758f98" />
  </>;
}
