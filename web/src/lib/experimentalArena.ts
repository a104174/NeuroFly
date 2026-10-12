import { Box3, Float32BufferAttribute, Material, Mesh, MeshStandardMaterial, Vector3, Color, type Object3D } from "three";
import { FLY_VIEWER_ASSET, flyViewerCamera, type FlyViewerView } from "./flyViewer";

export type ArenaCameraView = FlyViewerView | "inspect";
export const ARENA_RESET_VIEW: FlyViewerView = "three-quarter";

/** Display units only; relative presentation scale, not a biological measurement. */
export const ARENA = {
  chamber: { width: 2.4, depth: 1.22, height: .86, wall: .012, floor: .025 },
  flyScale: .3,
  // Keep the thoracic anchor's horizontal location and the previous floor clearance.
  // Offset = old placement + (1 - scale) * anchor in X/Z, or bounds.min in Y.
  flyOffset: [0, .09181772303581237, .08531420230865478] as [number, number, number],
  tableWidth: 3.8,
  tableTop: -.025,
  // Highest broad horizontal worktop plane, measured in the loaded source hierarchy.
  // AABB max includes bottles; using it would leave the chamber floating.
  tableWorktopY: .9117,
  tableUrl: "/assets/environment/lab-table/scene.gltf",
  tableSource: "https://sketchfab.com/3d-models/lab-table-a6585466b3bb4417bd0338c74328b209",
};

export const TABLE_FILES = {
  "scene.gltf": "430fbee27eca781d954a99066ddfdb686700f8302d104402f099aa7e81fb1b68",
  "scene.bin": "0e47e8021230a411ec17535ab987a6521ce7695e6e850fde16266c20021bbe78",
  "textures/clors_baseColor.png": "bbad4c96811768c0be0292e2de9e59a04418150dd68dd493821ac51bcb0cdcf4",
} as const;

/** Four walls plus a lid; visually closed only, not certified laboratory apparatus. */
export function arenaPanels() {
  const { width: w, depth: d, height: h, wall: t } = ARENA.chamber;
  return [
    { id: "left", position: [-w / 2, h / 2, 0], size: [t, h, d] },
    { id: "right", position: [w / 2, h / 2, 0], size: [t, h, d] },
    { id: "back", position: [0, h / 2, -d / 2], size: [w, h, t] },
    { id: "front", position: [0, h / 2, d / 2], size: [w, h, t] },
    { id: "lid", position: [0, h, 0], size: [w, t, d] },
  ] as { id: string; position: [number, number, number]; size: [number, number, number] }[];
}

export async function loadArenaTableBytes(fetcher: typeof fetch = fetch) {
  const files = await Promise.all(Object.entries(TABLE_FILES).map(async ([name, expected]) => {
    const response = await fetcher(`/assets/environment/lab-table/${name}`);
    if (!response.ok) throw new Error(`Lab Table ${name} could not load (HTTP ${response.status}).`);
    const bytes = await response.arrayBuffer();
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    const hash = Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2, "0")).join("");
    if (hash !== expected) throw new Error(`Lab Table ${name} failed its source integrity check.`);
    return [name, bytes] as const;
  }));
  return new Map(files);
}

/** Uniform fit; preserve the imported hierarchy and place the measured worktop at Y=tableTop. */
export function arenaTableFit(bounds: Box3) {
  const size = bounds.getSize(new Vector3()), center = bounds.getCenter(new Vector3());
  if (bounds.isEmpty() || ![...size.toArray(), ...center.toArray()].every(Number.isFinite) || size.x <= 0 || size.y <= 0 || size.z <= 0) throw new Error("Lab Table has invalid geometry bounds.");
  const scale = ARENA.tableWidth / size.x;
  if (size.z * scale < ARENA.chamber.depth + .08) throw new Error("Lab Table is too shallow to support this chamber safely.");
  return { scale, position: [-center.x * scale, ARENA.tableTop - ARENA.tableWorktopY * scale, -center.z * scale] as [number, number, number] };
}

/** Omit only disconnected, small bottle pieces above the verified worktop.
 * Position joins account for UV/normal seams; no source vertex or attribute is edited.
 * The retained index buffer is instance-owned. Worktop, cabinet and supports are retained.
 */
function unclutterTableMesh(mesh: Mesh) {
  const geometry = mesh.geometry, p = geometry.attributes.position, index = geometry.index;
  if (!index) throw new Error("Lab Table must retain its indexed source geometry.");
  const parents = Array.from({ length: p.count }, (_, i) => i);
  const find = (i: number): number => {
    let root = i;
    while (parents[root] !== root) root = parents[root];
    while (parents[i] !== i) { const next = parents[i]; parents[i] = root; i = next; }
    return root;
  };
  const join = (a: number, b: number) => { parents[find(a)] = find(b); };
  const positions = new Map<string, number>();
  const world: Vector3[] = [];
  for (let i = 0; i < p.count; i++) {
    const point = new Vector3().fromBufferAttribute(p, i).applyMatrix4(mesh.matrixWorld);
    world.push(point);
    const key = point.toArray().map(n => Math.round(n * 1e6)).join(":");
    const existing = positions.get(key);
    if (existing !== undefined) join(i, existing); else positions.set(key, i);
  }
  for (let i = 0; i < index.count; i += 3) {
    join(index.getX(i), index.getX(i + 1)); join(index.getX(i), index.getX(i + 2));
  }
  const bounds = new Map<number, Box3>();
  world.forEach((point, i) => {
    const root = find(i), box = bounds.get(root) ?? new Box3();
    box.expandByPoint(point); bounds.set(root, box);
  });
  const hidden = new Set<number>();
  bounds.forEach((box, root) => {
    const size = box.getSize(new Vector3());
    // The structural worktop bevel ends at source Y=.921675. Short residual glass
    // prop pieces reach .933 and were missed by the old .94 cutoff, protruding
    // through the chamber floor. Keep the slab; omit those disconnected props too.
    if (box.min.y > .909 && box.max.y > .922 && size.x < .14 && size.z < .14 && size.y < .3) hidden.add(root);
  });
  if (!hidden.size) return null;
  const kept: number[] = [];
  for (let i = 0; i < index.count; i += 3) {
    if (!hidden.has(find(index.getX(i)))) kept.push(index.getX(i), index.getX(i + 1), index.getX(i + 2));
  }
  const result = geometry.clone(); result.setIndex(kept);
  // Component-level base colors replace the old palette on this instance only.
  // Positions, normals, UVs and original texture data remain untouched.
  const colors = new Float32Array(p.count * 3);
  world.forEach((_, i) => {
    const box = bounds.get(find(i))!, size = box.getSize(new Vector3());
    const worktop = size.x > 2 && size.z > .6 && size.y < .08;
    const trim = (box.min.z > .41 && size.y < .04) || (size.x < .07 && size.y > .3);
    new Color(worktop ? "#a7aaa8" : trim ? "#88949b" : "#414c55").toArray(colors, i * 3);
  });
  result.setAttribute("color", new Float32BufferAttribute(colors, 3));
  return result;
}

/** Own presentation materials; retain cache-owned meshes, textures and source transforms. */
export function prepareArenaTable(source: Object3D) {
  const scene = source.clone(true);
  const fit = arenaTableFit(new Box3().setFromObject(scene));
  const materials = new Map<Material, Material>();
  const ownedGeometry: Mesh["geometry"][] = [];
  scene.traverse(node => {
    if (!(node instanceof Mesh)) return;
    const uncluttered = unclutterTableMesh(node);
    if (uncluttered) { node.geometry = uncluttered; ownedGeometry.push(uncluttered); }
    const isolate = (original: Material) => {
      let owned = materials.get(original);
      if (!owned) {
        owned = original.clone();
        if (owned instanceof MeshStandardMaterial) {
          owned.roughness = .62; owned.metalness = .16;
          owned.color.set("#ffffff"); owned.vertexColors = true; owned.map = null;
        }
        materials.set(original, owned);
      }
      return owned;
    };
    node.material = Array.isArray(node.material) ? node.material.map(isolate) : isolate(node.material);
  });
  scene.scale.multiplyScalar(fit.scale); scene.position.add(new Vector3(...fit.position));
  return { scene, dispose: () => { materials.forEach(material => material.dispose()); ownedGeometry.forEach(geometry => geometry.dispose()); } };
}

export function arenaCamera(aspect: number, view: ArenaCameraView) {
  const pose = flyViewerCamera(aspect, view === "inspect" ? "three-quarter" : view);
  const target = new Vector3(...pose.target).multiplyScalar(ARENA.flyScale).add(new Vector3(...ARENA.flyOffset));
  if (view === "inspect") {
    // Move the camera only; the model remains at the approved scale and placement.
    const direction = new Vector3(-.6, 1.5, 1).normalize();
    const right = new Vector3().crossVectors(new Vector3(0, 1, 0), direction).normalize();
    const up = new Vector3().crossVectors(direction, right).normalize();
    const fov = 55, tanV = Math.tan(fov * Math.PI / 360), tanH = tanV * Math.max(.1, aspect);
    let distance = .32;
    for (const x of [FLY_VIEWER_ASSET.bounds.min[0], FLY_VIEWER_ASSET.bounds.max[0]])
      for (const y of [FLY_VIEWER_ASSET.bounds.min[1], FLY_VIEWER_ASSET.bounds.max[1]])
        for (const z of [FLY_VIEWER_ASSET.bounds.min[2], FLY_VIEWER_ASSET.bounds.max[2]]) {
          const corner = new Vector3(x, y, z).multiplyScalar(ARENA.flyScale).add(new Vector3(...ARENA.flyOffset)).sub(target);
          distance = Math.max(distance, corner.dot(direction) + 1.25 * Math.max(Math.abs(corner.dot(right)) / tanH, Math.abs(corner.dot(up)) / tanV));
        }
    return { ...pose, fov, target: target.toArray(), position: target.clone().addScaledVector(direction, distance).toArray(), distance };
  }
  const direction = new Vector3(...pose.position).sub(new Vector3(...pose.target)).normalize();
  const right = new Vector3().crossVectors(new Vector3(0, 1, 0), direction).normalize();
  const up = new Vector3().crossVectors(direction, right).normalize();
  const tanV = Math.tan(pose.fov * Math.PI / 360), tanH = tanV * Math.max(.1, aspect);
  let distance = 0;
  // Frame the chamber and tabletop center, rather than a large room or the table legs.
  for (const x of [-1.4, 1.4]) for (const y of [-.3, .9]) for (const z of [-.72, .72]) {
    const corner = new Vector3(x, y, z).sub(target);
    distance = Math.max(distance, corner.dot(direction) + 1.12 * Math.max(Math.abs(corner.dot(right)) / tanH, Math.abs(corner.dot(up)) / tanV));
  }
  return { ...pose, target: target.toArray(), position: target.clone().addScaledVector(direction, distance).toArray(), distance };
}

export function arenaCameraLimits(view: ArenaCameraView) {
  return view === "inspect"
    ? { minDistance: .32, maxDistance: 1, maxPolarAngle: 1.3 }
    : { minDistance: .18, maxDistance: 12, maxPolarAngle: Math.PI };
}

/** Inspection is inside the enclosure: keep the near plane clear of its panels and base. */
export function constrainArenaInspectionCamera(position: Vector3) {
  const c = ARENA.chamber, clearance = .045;
  position.x = Math.max(-c.width / 2 + clearance, Math.min(c.width / 2 - clearance, position.x));
  position.y = Math.max(clearance, Math.min(c.height - clearance, position.y));
  position.z = Math.max(-c.depth / 2 + clearance, Math.min(c.depth / 2 - clearance, position.z));
}
