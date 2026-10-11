import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { BoxGeometry, BufferGeometry, Float32BufferAttribute, DoubleSide, Group, Mesh, MeshPhysicalMaterial, MeshStandardMaterial, DataTexture, SRGBColorSpace } from "three";
import { FLY_VISUAL_ASSET, flyAssetStatusMessage, parseFlyVisualAssetManifest } from "../src/lib/flyVisualAsset";
import { REQUIRED_ANATOMY, STATIC_ANATOMY, VISUAL_SCHEMA_V2 } from "../src/lib/flyVisualAssetV2";
import { cloneVisualNodeIdentity, visualNodeIdentity } from "../src/lib/flyVisualNodeIdentity";
import { flyPresentationFit, prepareFlyVisual } from "../src/lib/flyVisualInstance";

// Synthetic visual metadata/geometry only; not anatomical or scientific evidence.
function metadata() {
  return {
    schema: VISUAL_SCHEMA_V2, asset_id: "test_only_visual", asset_version: 2, role: "NEUROFLY_VISUAL_ASSET",
    runtime: { public_url: "/assets/fly/test_only.glb", glb_path: "web/public/assets/fly/test_only.glb", sha256: "a".repeat(64) },
    export: { tool: "Blender", tool_version: "test-only" },
    canonical_transform: { ...FLY_VISUAL_ASSET.canonical_transform, source_up_axis: "+Z", source_forward_axis: "-Y", scene_position: [0, 0.5, 0], scene_uniform_scale: 1 },
    specimen: { species: "Drosophila melanogaster", sex: "unspecified", reference_basis: "Synthetic test fixture only" },
    bounds: { min: [-0.5, -0.5, -0.5], max: [0.5, 0.5, 0.5] },
    nodes: { root: "TestRoot", required: [...REQUIRED_ANATOMY], optional: ["WingAttachment.L"] },
    materials: { strategy: "AUTHORED_PBR", roles: { body: ["Body"], eyes: ["Eyes"], wings: ["Wings"] }, wings: { thin: true, double_sided: true, alpha_mode: "BLEND" }, textures: [{ role: "base_color", color_space: "srgb" }, { role: "normal", color_space: "linear" }, { role: "metallic_roughness", color_space: "linear" }, { role: "occlusion", color_space: "linear" }] },
    capabilities: { static: true, skeletal_animation: false, morph_animation: false },
    measured: { triangle_count: 156, material_count: 3, animation_count: 0, camera_count: 0, light_count: 0, texture_image_count: 4 },
    scientific_status: { presentation_only: true, disclaimer: "Not biological geometry; test only" },
    provenance: { source_url: "https://example.org/test-only", author: "Test fixture", license: "TEST_ONLY", license_version: "test-only", license_url: "https://example.org/test-license", attribution: "Synthetic fixture", source_sha256: "b".repeat(64), modifications: "Synthetic geometry", texture_rights: "Synthetic fixture pixels", material_origins: "Synthetic fixture shaders", exporter_version: "test-only" },
  };
}
function scene() {
  const source = new Group(), root = new Group(); root.name = "TestRoot"; source.add(root);
  const body = new MeshPhysicalMaterial({ roughness: 0.3, metalness: 0.2, clearcoat: 0.4 }); body.name = "Body";
  const map = new DataTexture(new Uint8Array([120, 40, 20, 255]), 1, 1); map.colorSpace = SRGBColorSpace; body.map = map;
  body.normalMap = new DataTexture(new Uint8Array([128,128,255,255]),1,1);
  body.roughnessMap = new DataTexture(new Uint8Array([255,128,50,255]),1,1); body.metalnessMap = body.roughnessMap;
  body.aoMap = new DataTexture(new Uint8Array([255,255,255,255]),1,1); body.normalScale.set(0.3,0.6);
  const eyes = new MeshStandardMaterial(); eyes.name = "Eyes";
  const wings = new MeshPhysicalMaterial({ transparent: true, opacity: 0.4, side: DoubleSide, depthWrite: false }); wings.name = "Wings";
  const geometry = new BoxGeometry();
  for (const name of REQUIRED_ANATOMY) { const mesh = new Mesh(geometry, name.startsWith("Wing") ? wings : name.startsWith("Eye") ? eyes : body); mesh.name = name; root.add(mesh); }
  return { source, root, body, eyes, wings, map, geometry };
}
test("v1 remains pinned; v2 is explicit and unknown or confused versions fail", () => {
  assert.equal(parseFlyVisualAssetManifest(FLY_VISUAL_ASSET).asset_version, 1);
  assert.equal(parseFlyVisualAssetManifest(metadata()).asset_version, 2);
  assert.equal(flyAssetStatusMessage("ready", parseFlyVisualAssetManifest(metadata())), "test_only_visual · presentation only");
  for (const patch of [{ schema: "neurofly_visual_asset_manifest_v3" }, { asset_version: 1 }]) assert.throws(() => parseFlyVisualAssetManifest({ ...metadata(), ...patch }));
  assert.throws(() => parseFlyVisualAssetManifest({ ...FLY_VISUAL_ASSET, schema: VISUAL_SCHEMA_V2, asset_version: 2 }));
});
test("v2 rejects missing anatomy, invalid axes/bounds/scale, motion, license or texture conventions", () => {
  const mutations: ((m: ReturnType<typeof metadata>) => void)[] = [
    m => m.nodes.required.pop(), m => { m.nodes.optional = ["Head"]; },
    m => { m.canonical_transform.runtime_up_axis = "Z" as "+Y"; },
    m => { m.canonical_transform.scene_uniform_scale = 0; }, m => { m.bounds.max[2] = 2; },
    m => { m.capabilities.skeletal_animation = true; }, m => { m.provenance.texture_rights = ""; },
    m => { m.materials.textures[0].color_space = "linear"; }, m => { m.materials.wings.double_sided = false; },
  ];
  for (const mutate of mutations) { const m = metadata(); mutate(m); assert.throws(() => parseFlyVisualAssetManifest(m)); }
});
test("shared fit preserves both v1 compositions; v2 has exactly one fitting convention", () => {
  assert.deepEqual(flyPresentationFit(FLY_VISUAL_ASSET, "scenario"), { position: [0, 0.64, 0], rotation: [0, 0, 0], scale: 3.3 });
  assert.deepEqual(flyPresentationFit(FLY_VISUAL_ASSET, "historical"), { position: [0, 0.78, 0], rotation: [0, 0, 0], scale: 2 });
  const m = parseFlyVisualAssetManifest(metadata()); assert.deepEqual(flyPresentationFit(m, "scenario"), flyPresentationFit(m, "historical"));
});
test("authored instances preserve PBR/maps/wing alpha and isolate all material mutation", () => {
  const s = scene(), m = parseFlyVisualAssetManifest(metadata());
  const a = prepareFlyVisual(s.source, m, "scenario"), b = prepareFlyVisual(s.source, m, "historical");
  const body = (a.scene.getObjectByName("Thorax") as Mesh).material as MeshPhysicalMaterial;
  assert.notEqual(body, s.body); assert.notEqual(body, (b.scene.getObjectByName("Thorax") as Mesh).material);
  assert.equal(body.map, s.map);
  for (const key of ["normalMap", "roughnessMap", "metalnessMap", "aoMap"] as const) assert.equal(body[key], s.body[key]);
  assert.deepEqual(body.normalScale.toArray(), [0.3,0.6]); assert.equal(body.roughness, 0.3); assert.equal(body.metalness, 0.2); assert.equal(body.clearcoat, 0.4);
  assert.equal((a.scene.getObjectByName("Thorax") as Mesh).geometry, s.geometry);
  const wing = (a.scene.getObjectByName("Wing.L") as Mesh).material as MeshPhysicalMaterial;
  assert.equal(wing.opacity, 0.4); assert.equal(wing.transparent, true); assert.equal(wing.depthWrite, false); assert.equal(wing.side, DoubleSide);
  body.roughness = 0.9; assert.equal(s.body.roughness, 0.3);
  let disposed = 0, cachedDisposed = 0;
  body.addEventListener("dispose", () => disposed++); s.body.addEventListener("dispose", () => cachedDisposed++); s.map.addEventListener("dispose", () => cachedDisposed++); s.geometry.addEventListener("dispose", () => cachedDisposed++);
  a.dispose(); a.dispose(); assert.equal(disposed, 1); assert.equal(cachedDisposed, 0); a.activate(); a.dispose(); assert.equal(disposed, 2); b.dispose();
});
test("runtime rejects missing/duplicate/outside-root anatomy and actual bounds mismatch", () => {
  const m = parseFlyVisualAssetManifest(metadata());
  const s = scene(); s.root.remove(s.root.getObjectByName("Head")!); assert.throws(() => prepareFlyVisual(s.source, m, "scenario"), /anatomical/);
  const duplicate = scene(); const d = new Group(); d.name = "Head"; duplicate.root.add(d); assert.throws(() => prepareFlyVisual(duplicate.source, m, "scenario"), /ambiguous/);
  const moved = scene(); moved.root.position.x = 1; assert.throws(() => prepareFlyVisual(moved.source, m, "scenario"), /identity/);
  const bounds = scene(); bounds.geometry.scale(2, 1, 1); assert.throws(() => prepareFlyVisual(bounds.source, m, "scenario"), /bounds/);
  assert.throws(() => prepareFlyVisual(scene().source, m, "scenario", 1), /Animated/);
});
test("runtime validates wing transparency, UVs and texture color spaces without correcting cache", () => {
  const m = parseFlyVisualAssetManifest(metadata());
  const wings = scene(); wings.wings.side = 0; assert.throws(() => prepareFlyVisual(wings.source, m, "scenario"), /Wing/);
  const color = scene(); color.map.colorSpace = ""; assert.throws(() => prepareFlyVisual(color.source, m, "scenario"), /color space/); assert.equal(color.map.colorSpace, "");
  const uv = scene(); uv.geometry.deleteAttribute("uv"); assert.throws(() => prepareFlyVisual(uv.source, m, "scenario"), /UV/);
  const masked = metadata(); masked.materials.wings.alpha_mode = "MASK"; const s = scene(); s.wings.transparent = false; s.wings.alphaTest = 0.5; prepareFlyVisual(s.source, parseFlyVisualAssetManifest(masked), "scenario").dispose();
});
test("legacy scenario colors and historical authored materials remain distinct and stationary", () => {
  const s = scene(); const a = prepareFlyVisual(s.source, FLY_VISUAL_ASSET, "scenario"), b = prepareFlyVisual(s.source, FLY_VISUAL_ASSET, "historical");
  assert.equal(((a.scene.getObjectByName("Thorax") as Mesh).material as MeshPhysicalMaterial).color.getHexString(), "554431");
  assert.equal(((a.scene.getObjectByName("Wing.L") as Mesh).material as MeshPhysicalMaterial).opacity, 0.22);
  assert.equal(((b.scene.getObjectByName("Thorax") as Mesh).material as MeshPhysicalMaterial).roughness, s.body.roughness);
  assert.deepEqual(a.scene.position.toArray(), s.source.position.toArray()); assert.deepEqual(a.scene.quaternion.toArray(), s.source.quaternion.toArray());
  const source = readFileSync(new URL("../src/lib/flyVisualInstance.ts", import.meta.url), "utf8"); assert.doesNotMatch(source, /useFrame|setInterval|requestAnimationFrame|Math.sin|world_eq/);
  a.dispose(); b.dispose();
});


test("current real GLB clones preserve historical material values and cached transforms", async () => {
  const { GLTFLoader } = await import("three/examples/jsm/loaders/GLTFLoader.js");
  const bytes = readFileSync(new URL("../public/assets/fly/fly_visual_v1.glb", import.meta.url));
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer, "");
  const original = gltf.scene.getObjectByName("Thorax") as Mesh;
  const a = prepareFlyVisual(gltf.scene, FLY_VISUAL_ASSET, "historical"), b = prepareFlyVisual(gltf.scene, FLY_VISUAL_ASSET, "historical");
  const cloned = a.scene.getObjectByName("Thorax") as Mesh;
  assert.notEqual(a.scene, b.scene); assert.equal(gltf.scene.parent, null);
  assert.deepEqual(cloned.position.toArray(), original.position.toArray()); assert.deepEqual(cloned.quaternion.toArray(), original.quaternion.toArray());
  assert.deepEqual((cloned.material as MeshStandardMaterial).color.toArray(), (original.material as MeshStandardMaterial).color.toArray());
  assert.equal((cloned.material as MeshStandardMaterial).roughness, (original.material as MeshStandardMaterial).roughness);
  assert.notEqual(cloned.material, original.material); a.dispose(); b.dispose();
});
test("optional attachments, array materials and repeated instances have predictable ownership", () => {
  const s = scene(), attachment = new Group(); attachment.name = "WingAttachment.L"; s.root.add(attachment);
  (s.root.getObjectByName("Head") as Mesh).material = [s.body, s.eyes];
  const m = parseFlyVisualAssetManifest(metadata()), instance = prepareFlyVisual(s.source, m, "scenario");
  const head = (instance.scene.getObjectByName("Head") as Mesh).material as MeshStandardMaterial[];
  assert.equal(head[0], (instance.scene.getObjectByName("Thorax") as Mesh).material);
  assert.notEqual(head[1], s.eyes); instance.dispose();
  const duplicate = new Group(); duplicate.name = attachment.name; s.root.add(duplicate);
  assert.throws(() => prepareFlyVisual(s.source, m, "scenario"), /ambiguous/);
});
test("actual static geometry counts and morph capability fail closed", () => {
  const bad = metadata(); bad.measured.triangle_count++; assert.throws(() => prepareFlyVisual(scene().source, parseFlyVisualAssetManifest(bad), "scenario"), /counts/);
  const materials = scene(); (materials.root.getObjectByName("Head") as Mesh).material = materials.body.clone();
  assert.throws(() => prepareFlyVisual(materials.source, parseFlyVisualAssetManifest(metadata()), "scenario"), /counts/);
  const s = scene(); s.geometry.morphAttributes.position = [s.geometry.getAttribute("position")];
  assert.throws(() => prepareFlyVisual(s.source, parseFlyVisualAssetManifest(metadata()), "scenario"), /morph/);
});

function combinedMetadata() {
  const m = metadata();
  return { ...m, anatomy: { body_topology: "combined" as const, body_node: "Torso.Unseparated", limitation: "One static joined surface; no independent thorax/abdomen articulation or anatomical validation." }, nodes: { ...m.nodes, required: [...STATIC_ANATOMY, "Torso.Unseparated"] }, measured: { ...m.measured, triangle_count: 144 } };
}
function combinedScene() {
  const s = scene();
  s.root.remove(s.root.getObjectByName("Thorax")!, s.root.getObjectByName("Abdomen")!);
  const body: Mesh<BufferGeometry, MeshPhysicalMaterial> = new Mesh(s.geometry, s.body); body.name = "Torso.Unseparated"; s.root.add(body);
  return { ...s, combinedBody: body };
}
test("explicit static composite preserves separated metadata and requires truthful declarations", () => {
  const m = combinedMetadata(); assert.equal(parseFlyVisualAssetManifest(m).asset_version, 2);
  assert.equal(parseFlyVisualAssetManifest({ ...metadata(), anatomy: { body_topology: "separated" } }).asset_version, 2);
  const mutations = [
    { ...m, anatomy: { ...m.anatomy, body_topology: "other" } },
    { ...m, anatomy: { body_topology: "combined", body_node: m.anatomy.body_node } },
    { ...m, anatomy: { ...m.anatomy, body_node: "Head" } },
    { ...m, nodes: { ...m.nodes, required: [...m.nodes.required, "Thorax"] } },
    { ...m, nodes: { ...m.nodes, optional: ["Abdomen"] } },
    { ...m, nodes: { ...m.nodes, required: [...STATIC_ANATOMY] } },
    { ...m, anatomy: { body_topology: "separated", body_node: m.anatomy.body_node } },
  ];
  for (const value of mutations) assert.throws(() => parseFlyVisualAssetManifest(value));
  for (const profile of ["historical", "scenario"] as const) {
    const s = combinedScene(); const instance = prepareFlyVisual(s.source, parseFlyVisualAssetManifest(m), profile);
    assert.deepEqual(instance.scene.position.toArray(), s.source.position.toArray()); instance.dispose();
  }
});
test("combined identity must contain real geometry and cannot alias another anatomical region", () => {
  const m = parseFlyVisualAssetManifest(combinedMetadata());
  const missing = combinedScene(); missing.root.remove(missing.combinedBody); assert.throws(() => prepareFlyVisual(missing.source, m, "scenario"), /missing/);
  const empty = combinedScene(); empty.root.remove(empty.combinedBody); const placeholder = new Group(); placeholder.name = "Torso.Unseparated"; empty.root.add(placeholder);
  assert.throws(() => prepareFlyVisual(empty.source, m, "scenario"), /actual mesh/);
  const grouped = combinedScene(); grouped.combinedBody.name = "BodySurface"; const group = new Group(); group.name = "Torso.Unseparated"; grouped.root.add(group); group.add(grouped.combinedBody);
  prepareFlyVisual(grouped.source, m, "scenario").dispose();
  group.remove(grouped.combinedBody); group.add(grouped.root.getObjectByName("Head")!); assert.throws(() => prepareFlyVisual(grouped.source, m, "scenario"), /actual mesh/);
  const duplicate = combinedScene(); const d = duplicate.combinedBody.clone(); duplicate.root.add(d); assert.throws(() => prepareFlyVisual(duplicate.source, m, "scenario"), /ambiguous/);
  const animated = combinedMetadata(); animated.capabilities.morph_animation = true; assert.throws(() => parseFlyVisualAssetManifest(animated), /static/);
});

// Offline glTF fixture parsed by the actual installed loader: no network or external asset dependency.
async function loadedFixture(names: string[]) {
  const { GLTFLoader } = await import("three/examples/jsm/loaders/GLTFLoader.js");
  const positions = new Float32Array([-0.5,-0.5,-0.5, .5,-.5,-.5, .5,.5,-.5, -.5,.5,-.5, -.5,-.5,.5, .5,-.5,.5, .5,.5,.5, -.5,.5,.5]);
  const indices = new Uint16Array([0,2,1,0,3,2,4,5,6,4,6,7,0,1,5,0,5,4,2,3,7,2,7,6,0,4,7,0,7,3,1,2,6,1,6,5]);
  const bytes = Buffer.concat([Buffer.from(positions.buffer), Buffer.from(indices.buffer)]);
  const roles = ["Body", "Eyes", "Wings"];
  const gltf = {
    asset: { version: "2.0" }, scene: 0, scenes: [{ nodes: [0] }],
    nodes: [{ name: "TestRoot", children: names.map((_, i) => i + 1) }, ...names.map(name => ({ name, mesh: name.startsWith("Wing") ? 2 : name.startsWith("Eye") ? 1 : 0, extras: { name: "untrusted-extra" } }))],
    buffers: [{ byteLength: bytes.length }],
    bufferViews: [{ buffer: 0, byteOffset: 0, byteLength: positions.byteLength }, { buffer: 0, byteOffset: positions.byteLength, byteLength: indices.byteLength }],
    accessors: [{ bufferView: 0, componentType: 5126, count: 8, type: "VEC3", min: [-.5,-.5,-.5], max: [.5,.5,.5] }, { bufferView: 1, componentType: 5123, count: 36, type: "SCALAR" }],
    materials: roles.map(name => ({ name, doubleSided: name === "Wings", alphaMode: name === "Wings" ? "BLEND" : "OPAQUE" })),
    meshes: roles.map((_, material) => ({ primitives: [{ attributes: { POSITION: 0 }, indices: 1, material }] })),
  };
  const json = Buffer.from(JSON.stringify(gltf));
  const padded = Buffer.alloc(Math.ceil(json.length / 4) * 4, 32); json.copy(padded);
  const binary = Buffer.alloc(Math.ceil(bytes.length / 4) * 4); bytes.copy(binary);
  const header = Buffer.alloc(12); header.write("glTF"); header.writeUInt32LE(2, 4); header.writeUInt32LE(28 + padded.length + binary.length, 8);
  const jsonHeader = Buffer.alloc(8); jsonHeader.writeUInt32LE(padded.length); jsonHeader.write("JSON", 4);
  const binHeader = Buffer.alloc(8); binHeader.writeUInt32LE(binary.length); binHeader.write("BIN\0", 4);
  const glb = Buffer.concat([header, jsonHeader, padded, binHeader, binary]);
  return new GLTFLoader().parseAsync(glb.buffer.slice(glb.byteOffset, glb.byteOffset + glb.byteLength) as ArrayBuffer, "");
}
test("actual loader source indices preserve punctuation, L/R and sanitized-name collisions", async () => {
  const gltf = await loadedFixture([...STATIC_ANATOMY, "Torso.Unseparated", "EyeL"]);
  const identities = visualNodeIdentity(gltf.scene, gltf.parser);
  assert.equal(identities.get("Eye.L")!.name, "EyeL");
  assert.notEqual(identities.get("Eye.L"), identities.get("EyeL"));
  assert.notEqual(identities.get("Eye.L"), identities.get("Eye.R"));
  assert.equal(identities.get("Torso.Unseparated")!.name, "TorsoUnseparated");
  const originalNames: string[] = []; gltf.scene.traverse(n => originalNames.push(n.name));
  const m = combinedMetadata(); m.measured.texture_image_count = 0; m.materials.textures = []; m.measured.triangle_count += 12;
  for (const profile of ["scenario", "historical"] as const) prepareFlyVisual(gltf.scene, parseFlyVisualAssetManifest(m), profile, 0, gltf.parser).dispose();
  const after: string[] = []; gltf.scene.traverse(n => after.push(n.name)); assert.deepEqual(after, originalNames);
});
test("real loader separated path works and duplicate original identities fail closed", async () => {
  const gltf = await loadedFixture([...REQUIRED_ANATOMY]); const m = metadata(); m.materials.textures = []; m.measured.texture_image_count = 0;
  prepareFlyVisual(gltf.scene, parseFlyVisualAssetManifest(m), "scenario", 0, gltf.parser).dispose();
  const duplicate = await loadedFixture([...REQUIRED_ANATOMY, "Eye.L"]);
  assert.throws(() => visualNodeIdentity(duplicate.scene, duplicate.parser), /ambiguous/);
  gltf.parser.associations.set(gltf.scene.getObjectByName("EyeL")!, { nodes: 0 });
  assert.throws(() => visualNodeIdentity(gltf.scene, gltf.parser), /ambiguous/);
});

test("named anatomy groups and primitive child names preserve wing shadow/material behavior", () => {
  const s = combinedScene();
  const wing = s.root.getObjectByName("Wing.L") as Mesh; wing.name = "Primitive_0";
  const parent = new Group(); parent.name = "Wing.L"; s.root.add(parent); parent.add(wing);
  const instance = prepareFlyVisual(s.source, parseFlyVisualAssetManifest(combinedMetadata()), "scenario");
  const cloned = instance.scene.getObjectByName("Primitive_0") as Mesh;
  assert.equal(cloned.castShadow, false); assert.equal((cloned.material as MeshPhysicalMaterial).opacity, .4);
  assert.equal(wing.castShadow, false); instance.dispose();
});

test("combined body cannot be represented by a degenerate triangle placeholder", () => {
  const s = combinedScene(); const g = new BufferGeometry(); g.setAttribute("position", new Float32BufferAttribute([0,0,0, 0,0,0, 0,0,0],3));
  s.combinedBody.geometry = g;
  assert.throws(() => prepareFlyVisual(s.source, parseFlyVisualAssetManifest(combinedMetadata()), "scenario"), /actual mesh/);
});

test("nested anatomical regions own distinct surfaces without requiring a flat hierarchy", () => {
  const s = combinedScene(); const head = s.root.getObjectByName("Head")!;
  head.add(s.root.getObjectByName("Eye.L")!, s.root.getObjectByName("Eye.R")!);
  prepareFlyVisual(s.source, parseFlyVisualAssetManifest(combinedMetadata()), "scenario").dispose();
  // Naming a head group around eyes alone cannot fabricate a head surface.
  const replacement = new Group(); replacement.name = "Head";
  replacement.add(...head.children); s.root.remove(head); s.root.add(replacement);
  assert.throws(() => prepareFlyVisual(s.source, parseFlyVisualAssetManifest(combinedMetadata()), "scenario"), /actual mesh/);
});

test("verified source identities map to distinct cloned instance objects without parser guessing", async () => {
  for (const combined of [false, true]) {
    const names = combined ? [...STATIC_ANATOMY, "Torso.Unseparated"] : [...REQUIRED_ANATOMY];
    const gltf = await loadedFixture(names);
    const m = combined ? combinedMetadata() : metadata(); m.materials.textures = []; m.measured.texture_image_count = 0;
    const manifest = parseFlyVisualAssetManifest(m), original = visualNodeIdentity(gltf.scene, gltf.parser);
    const a = prepareFlyVisual(gltf.scene, manifest, "scenario", 0, gltf.parser);
    const b = prepareFlyVisual(gltf.scene, manifest, "historical", 0, gltf.parser);
    assert.throws(() => visualNodeIdentity(a.scene, gltf.parser), /associations/);
    for (const name of ["TestRoot", ...names]) {
      const source = original.get(name)!, first = a.nodeIdentities!.get(name)!, second = b.nodeIdentities!.get(name)!;
      assert.ok(first && second); assert.notEqual(first, source); assert.notEqual(first, second);
      assert.equal(a.scene.getObjectById(first.id), first); assert.equal(b.scene.getObjectById(second.id), second);
      assert.equal(first.name, source.name); assert.deepEqual(first.position.toArray(), source.position.toArray());
      if (first instanceof Mesh && second instanceof Mesh && source instanceof Mesh) {
        assert.equal(first.geometry, source.geometry); assert.notEqual(first.material, source.material); assert.notEqual(first.material, second.material);
      }
    }
    a.nodeIdentities!.get("Eye.L")!.position.x = 7;
    assert.notEqual(original.get("Eye.L")!.position.x, 7); assert.notEqual(b.nodeIdentities!.get("Eye.L")!.position.x, 7);
    a.dispose(); b.dispose();
  }
});

test("clone mapping rejects altered hierarchy, foreign objects and aliased identities", () => {
  const s = scene(), verified = visualNodeIdentity(s.source);
  assert.throws(() => cloneVisualNodeIdentity(s.source, s.source, verified), /hierarchy/);
  const incomplete = s.source.clone(true); incomplete.children[0].remove(incomplete.getObjectByName("Head")!);
  assert.throws(() => cloneVisualNodeIdentity(s.source, incomplete, verified), /hierarchy/);
  assert.throws(() => cloneVisualNodeIdentity(s.source, s.source.clone(true), new Map([["Foreign", new Group()]])), /Missing/);
  const eye = s.root.getObjectByName("Eye.L")!;
  assert.throws(() => cloneVisualNodeIdentity(s.source, s.source.clone(true), new Map([["Eye.L", eye], ["Eye.R", eye]])), /ambiguous/);
});
