import { DoubleSide, Material, Mesh, MeshPhysicalMaterial, MeshStandardMaterial, Object3D, SRGBColorSpace, NoColorSpace, Box3, Vector3, Matrix4, Quaternion, Euler } from "three";
import type { FlyVisualAssetManifest } from "./flyVisualAsset";
import { cloneVisualNodeIdentity, visualNodeIdentity, type VisualNodeParser } from "./flyVisualNodeIdentity";
import { STATIC_ANATOMY, VISUAL_SCHEMA_V2 } from "./flyVisualAssetV2";

export type FlyPresentationProfile = "historical" | "scenario";
/** Scientific position/orientation remains in the caller's parent group. */
export function flyPresentationFit(manifest: FlyVisualAssetManifest, profile: FlyPresentationProfile) {
  if (manifest.schema !== VISUAL_SCHEMA_V2 && profile === "scenario") {
    return { position: [0, 0.64, 0] as [number, number, number], rotation: [0, 0, 0] as [number, number, number], scale: 3.3 };
  }
  const t = manifest.canonical_transform;
  return { position: t.scene_position, rotation: t.scene_rotation_euler_rad, scale: t.scene_uniform_scale };
}

/** Anchor is a camera/presentation target, never an implicit mesh translation.
 * Runtime asset point -> uniform scale -> Euler rotation -> scene translation.
 */
export function flyPresentationAnchor(manifest: FlyVisualAssetManifest, profile: FlyPresentationProfile): [number, number, number] {
  const fit = flyPresentationFit(manifest, profile);
  const point = manifest.schema === VISUAL_SCHEMA_V2 && manifest.canonical_transform.origin === "model origin"
    ? manifest.canonical_transform.visual_anchor.position : [0, 0, 0];
  return new Vector3(...point).applyMatrix4(new Matrix4().compose(
    new Vector3(...fit.position), new Quaternion().setFromEuler(new Euler(...fit.rotation)),
    new Vector3(fit.scale, fit.scale, fit.scale),
  )).toArray();
}

/** A named placeholder or degenerate triangle is not anatomical surface geometry. */
function hasSurface(mesh: Mesh): boolean {
  const position = mesh.geometry.getAttribute("position"), index = mesh.geometry.index;
  if (!position || position.itemSize < 3) return false;
  const count = index?.count ?? position.count;
  for (let i = 0; i + 2 < count; i += 3) {
    const ids = [0, 1, 2].map(k => index ? index.getX(i + k) : i + k);
    if (ids.some(id => !Number.isInteger(id) || id < 0 || id >= position.count)) throw new Error("Invalid anatomical surface indices.");
    const points = ids.map(id => [position.getX(id), position.getY(id), position.getZ(id)]);
    if (points.some(p => p.some(v => !Number.isFinite(v)))) throw new Error("Invalid anatomical surface positions.");
    const u = points[1].map((v, j) => v - points[0][j]), v = points[2].map((x, j) => x - points[0][j]);
    if (u[1] * v[2] !== u[2] * v[1] || u[2] * v[0] !== u[0] * v[2] || u[0] * v[1] !== u[1] * v[0]) return true;
  }
  return false;
}

/** Clone owned materials; cached geometry/textures are immutable and never disposed here. */
export function prepareFlyVisual(source: Object3D, manifest: FlyVisualAssetManifest, profile: FlyPresentationProfile, animationCount = 0, parser?: VisualNodeParser) {
  const authored = manifest.schema === VISUAL_SCHEMA_V2;
  let sourceIdentities: Map<string, Object3D> | undefined;
  if (authored) {
    if (animationCount !== 0) throw new Error("Animated visual assets are not supported.");
    const identities = visualNodeIdentity(source, parser);
    sourceIdentities = identities;
    for (const name of [manifest.nodes.root, ...manifest.nodes.required]) {
      if (!identities.has(name)) throw new Error("Required anatomical node is missing.");
    }
    const root = identities.get(manifest.nodes.root)!;
    if (root.position.lengthSq() !== 0 || root.scale.toArray().some(v => v !== 1) || root.quaternion.toArray().some((v,i) => v !== (i === 3 ? 1 : 0))) throw new Error("Asset root must have an identity local transform.");
    const anatomyMeshes = new Set<Mesh>();
    const actualAnatomy = manifest.anatomy?.body_topology === "combined"
      ? [...STATIC_ANATOMY, manifest.anatomy.body_node] : ["Head", "Thorax", "Abdomen", ...STATIC_ANATOMY.filter(n => n !== "Head")];
    const regionNodes = new Set(actualAnatomy.map(name => identities.get(name)!));
    for (const name of manifest.nodes.required) {
      const node = identities.get(name)!;
      if (!root.getObjectById(node.id)) throw new Error("Anatomical node lies outside asset root.");
      if (!actualAnatomy.includes(name)) continue;
      let meshes = 0;
      function visit(child: Object3D) {
        // Child anatomical regions own their surfaces (e.g. eyes nested under head).
        if (child !== node && regionNodes.has(child)) return;
        if (child instanceof Mesh && hasSurface(child)) {
          if (anatomyMeshes.has(child)) throw new Error("Conflicting anatomical geometry identities.");
          anatomyMeshes.add(child); meshes++;
        }
        child.children.forEach(visit);
      }
      visit(node);
      if (!meshes) throw new Error("Anatomical identity needs actual mesh geometry.");
    }
    const bounds = new Box3().setFromObject(source);
    for (const [actual, expected] of [[bounds.min.toArray(), manifest.bounds.min], [bounds.max.toArray(), manifest.bounds.max]]) {
      if (actual.some((v,i) => !Number.isFinite(v) || Math.abs(v - expected[i]) > 1e-5)) throw new Error("Asset geometry bounds do not match metadata.");
    }
    if (manifest.canonical_transform.origin === "model origin") {
      const anchor = manifest.canonical_transform.visual_anchor;
      const helper = identities.get(anchor.node);
      if (!helper || helper === root || !root.getObjectById(helper.id)) throw new Error("Visual anchor helper missing or outside root.");
      let hasMesh = false; helper.traverse(n => { if (n instanceof Mesh) hasMesh = true; });
      if (hasMesh) throw new Error("Visual anchor must be a transform helper, not anatomical geometry.");
      source.updateMatrixWorld(true);
      const actual = helper.getWorldPosition(new Vector3()).toArray();
      if (actual.some((v, i) => !Number.isFinite(v) || Math.abs(v - anchor.position[i]) > 1e-6)) throw new Error("Visual anchor transform does not match metadata.");
    }
    const roles = manifest.materials.roles;
    const allowed = [...roles.body, ...roles.eyes, ...roles.wings];
    const seen = new Set<string>();
    const actualMaterials = new Set<Material>();
    const textureRoles = new Set(manifest.materials.textures.map(t => t.role));
    let triangles = 0;
    source.traverse(n => {
      if ("isCamera" in n || "isLight" in n) throw new Error("Asset-local cameras/lights are not supported.");
      if (!(n instanceof Mesh)) return;
      if (!root.getObjectById(n.id)) throw new Error("Mesh lies outside asset root.");
      triangles += (n.geometry.index?.count ?? n.geometry.getAttribute("position")?.count ?? 0) / 3;
      if ("isSkinnedMesh" in n || Object.keys(n.geometry.morphAttributes).length) throw new Error("Static assets cannot contain skins or morph targets.");
      for (const material of Array.isArray(n.material) ? n.material : [n.material]) {
        if (!(material instanceof MeshStandardMaterial) || !allowed.includes(material.name)) throw new Error("Unsupported authored PBR material role.");
        seen.add(material.name);
        actualMaterials.add(material);
        if (roles.wings.includes(material.name)) {
          if (material.side !== DoubleSide || (manifest.materials.wings.alpha_mode === "BLEND" ? !material.transparent || material.alphaTest !== 0 : material.transparent || material.alphaTest <= 0)) throw new Error("Wing alpha/side does not match authored contract.");
        }
        const maps = [[material.map, "base_color", SRGBColorSpace], [material.emissiveMap, "emissive", SRGBColorSpace], [material.normalMap, "normal", NoColorSpace], [material.roughnessMap, "metallic_roughness", NoColorSpace], [material.metalnessMap, "metallic_roughness", NoColorSpace], [material.aoMap, "occlusion", NoColorSpace]] as const;
        for (const [map, role, space] of maps) if (map && (!textureRoles.has(role) || map.colorSpace !== space || !n.geometry.getAttribute(map.channel === 0 ? "uv" : `uv${map.channel}`))) throw new Error("Authored texture/UV/color space contract mismatch.");
      }
    });
    if (triangles !== manifest.measured.triangle_count || actualMaterials.size !== manifest.measured.material_count) throw new Error("Actual geometry/material counts do not match metadata.");
    if (allowed.some(name => !seen.has(name))) throw new Error("Declared material role is absent from asset.");
  }
  const scene = source.clone(true);
  const nodeIdentities = sourceIdentities ? cloneVisualNodeIdentity(source, scene, sourceIdentities) : undefined;
  const owned = new Set<Material>();
  const clones = new Map<Material, Material>();
  let legacy: Material[] | undefined;
  if (!authored && profile === "scenario") {
    legacy = [
      new MeshPhysicalMaterial({ color: "#554431", roughness: 0.68, metalness: 0, clearcoat: 0.12 }),
      new MeshPhysicalMaterial({ color: "#702b1c", roughness: 0.43, metalness: 0, clearcoat: 0.2, flatShading: true }),
      new MeshPhysicalMaterial({ color: "#cfccbb", roughness: 0.4, transparent: true, opacity: 0.22, depthWrite: false, side: DoubleSide }),
    ];
    legacy.forEach(m => owned.add(m));
  }
  function cloneMaterial(m: Material) {
    let clone = clones.get(m);
    if (!clone) { clone = m.clone(); clones.set(m, clone); owned.add(clone); }
    return clone;
  }
  scene.traverse(n => {
    if (!(n instanceof Mesh)) return;
    n.material = legacy ? n.name.startsWith("Wing") ? legacy[2] : n.name.startsWith("Eye") ? legacy[1] : legacy[0] : Array.isArray(n.material) ? n.material.map(cloneMaterial) : cloneMaterial(n.material);
    if (profile === "scenario") {
      const isWing = authored
        ? (Array.isArray(n.material) ? n.material : [n.material]).some(m => manifest.materials.roles.wings.includes(m.name))
        : n.name.startsWith("Wing");
      n.castShadow = !isWing; n.receiveShadow = true;
    }
  });
  let disposed = false;
  return { scene, nodeIdentities, activate() { disposed = false; }, dispose() { if (!disposed) { owned.forEach(m => m.dispose()); disposed = true; } } };
}
