import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { Box3, Mesh, MeshStandardMaterial, PerspectiveCamera, Texture, Vector3 } from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { ARENA, ARENA_RESET_VIEW, TABLE_FILES, arenaCamera, arenaCameraLimits, arenaPanels, arenaTableFit, constrainArenaInspectionCamera, loadArenaTableBytes, prepareArenaTable } from "../src/lib/experimentalArena";
import { FLY_VIEWER_ASSET, flyViewerCamera } from "../src/lib/flyViewer";

test("licensed table and all dependencies retain original source bytes", async () => {
  const fetcher: typeof fetch = async input => new Response(readFileSync(new URL(`../public${input}`, import.meta.url)));
  const files = await loadArenaTableBytes(fetcher);
  for (const [name, hash] of Object.entries(TABLE_FILES)) assert.equal(createHash("sha256").update(new Uint8Array(files.get(name)!)).digest("hex"), hash);
  const source = JSON.parse(new TextDecoder().decode(files.get("scene.gltf")));
  assert.equal(source.asset.version, "2.0");
  assert.equal(source.asset.extras.author, "zeeshanfareed (https://sketchfab.com/zeeshanfareed)");
  assert.match(readFileSync(new URL("../public/assets/environment/lab-table/license.txt", import.meta.url), "utf8"), /CC-BY-4.0/);
  assert.equal(source.meshes.length, 2);
  assert.equal(source.meshes.reduce((sum: number, mesh: { primitives: { indices: number }[] }) => sum + mesh.primitives.reduce((n, p) => n + source.accessors[p.indices].count / 3, 0), 0), 31194);
});

test("missing table, missing texture and corrupt dependency fail without replacement geometry", async () => {
  for (const unavailable of Object.keys(TABLE_FILES)) {
    const fetcher: typeof fetch = async input => String(input).endsWith(unavailable) ? new Response(null, { status: 404 }) : new Response(readFileSync(new URL(`../public${input}`, import.meta.url)));
    await assert.rejects(loadArenaTableBytes(fetcher), /HTTP 404/);
  }
  await assert.rejects(loadArenaTableBytes(async () => new Response("corrupt")), /integrity/);
});

test("chamber encloses every fly-bound corner with floor clearance and useful lateral amplitude", () => {
  assert.equal(ARENA.flyScale, .30);
  const c = ARENA.chamber;
  assert.ok(c.width > 2 * (FLY_VIEWER_ASSET.bounds.max[0] - FLY_VIEWER_ASSET.bounds.min[0]));
  for (const [i, limit] of [[0, c.width / 2], [2, c.depth / 2]] as const)
    for (const bound of [FLY_VIEWER_ASSET.bounds.min, FLY_VIEWER_ASSET.bounds.max]) assert.ok(Math.abs(bound[i] * ARENA.flyScale + ARENA.flyOffset[i]) < limit - c.wall);
  assert.ok(FLY_VIEWER_ASSET.bounds.min[1] * ARENA.flyScale + ARENA.flyOffset[1] > 0);
  assert.ok(FLY_VIEWER_ASSET.bounds.max[1] * ARENA.flyScale + ARENA.flyOffset[1] < c.height);
  const size = new Vector3(...FLY_VIEWER_ASSET.bounds.max).sub(new Vector3(...FLY_VIEWER_ASSET.bounds.min)).multiplyScalar(ARENA.flyScale);
  assert.ok(size.x / c.width < .1 && size.z / c.depth < .25);
  const floorClearance = FLY_VIEWER_ASSET.bounds.min[1] * ARENA.flyScale + ARENA.flyOffset[1];
  assert.ok(Math.abs(floorClearance - (FLY_VIEWER_ASSET.bounds.min[1] + .292)) < 1e-12);
});

test("table fit is uniform and centered, rejecting unusable support geometry", () => {
  const bounds = new Box3(new Vector3(-1.31, -.51, -.4), new Vector3(1.31, 1.16, .51));
  const fit = arenaTableFit(bounds);
  assert.ok(Math.abs(ARENA.tableWorktopY * fit.scale + fit.position[1] - ARENA.tableTop) < 1e-12);
  assert.ok(Math.abs(bounds.getCenter(new Vector3()).z * fit.scale + fit.position[2]) < 1e-12);
  assert.throws(() => arenaTableFit(new Box3()), /invalid/);
  assert.throws(() => arenaTableFit(new Box3(new Vector3(0, 0, 0), new Vector3(3, 1, .01))), /shallow/);
});

test("arena presets retain the translated thoracic target, responsive chamber framing and studio behavior", () => {
  const studio = flyViewerCamera(1.5);
  for (const aspect of [1.5, .55]) for (const view of ["three-quarter", "lateral", "head", "dorsal"] as const) {
    const pose = arenaCamera(aspect, view);
    pose.target.forEach((n, i) => assert.ok(Math.abs(n - studio.target[i] * ARENA.flyScale - ARENA.flyOffset[i]) < 1e-12));
    assert.ok(Math.abs(pose.target[0] - studio.target[0]) < 1e-12);
    assert.ok(Math.abs(pose.target[2] - studio.target[2]) < 1e-12);
    const camera = new PerspectiveCamera(pose.fov, aspect, .01, 30);
    camera.position.fromArray(pose.position); camera.lookAt(new Vector3(...pose.target)); camera.updateMatrixWorld();
    for (const x of [-1.2, 1.2]) for (const y of [0, ARENA.chamber.height]) for (const z of [-.61, .61]) {
      const p = new Vector3(x, y, z).project(camera); assert.ok(Math.abs(p.x) < 1 && Math.abs(p.y) < 1 && p.z > -1 && p.z < 1);
    }
  }
  assert.deepEqual(flyViewerCamera(1.5), studio);
});

test("real table fits onto its broad worktop, and independent instances preserve cache resources", async () => {
  // Node has no image decoder: parse real source geometry; image fetch/integrity is tested above
  // and actual textured loading is exercised in the browser smoke.
  if (typeof ProgressEvent === "undefined") Object.defineProperty(globalThis, "ProgressEvent", { configurable: true, value: class extends Event {} });
  const source = JSON.parse(readFileSync(new URL("../public/assets/environment/lab-table/scene.gltf", import.meta.url), "utf8"));
  source.buffers[0].uri = `data:application/octet-stream;base64,${readFileSync(new URL("../public/assets/environment/lab-table/scene.bin", import.meta.url)).toString("base64")}`;
  delete source.images; delete source.textures;
  for (const material of source.materials) delete material.pbrMetallicRoughness.baseColorTexture;
  const gltf = await new GLTFLoader().parseAsync(JSON.stringify(source), "");
  gltf.scene.updateMatrixWorld(true);
  const levels = new Map<number, number>();
  gltf.scene.traverse(node => {
    if (!(node instanceof Mesh)) return;
    const p = node.geometry.attributes.position, index = node.geometry.index!;
    for (let i = 0; i < index.count; i += 3) {
      const a = new Vector3().fromBufferAttribute(p, index.getX(i)).applyMatrix4(node.matrixWorld);
      const b = new Vector3().fromBufferAttribute(p, index.getX(i + 1)).applyMatrix4(node.matrixWorld);
      const c = new Vector3().fromBufferAttribute(p, index.getX(i + 2)).applyMatrix4(node.matrixWorld);
      if (Math.max(a.y, b.y, c.y) - Math.min(a.y, b.y, c.y) > 1e-5) continue;
      const level = Math.round(a.y * 10000) / 10000;
      levels.set(level, (levels.get(level) ?? 0) + b.sub(a).cross(c.sub(a)).length() / 2);
    }
  });
  const broadTop = Math.max(...[...levels].filter(([, area]) => area > 1).map(([y]) => y));
  assert.equal(broadTop, ARENA.tableWorktopY);
  assert.ok(new Box3().setFromObject(gltf.scene).max.y > broadTop + .2, "props must not define the support plane");
  const originals: Mesh[] = []; gltf.scene.traverse(n => { if (n instanceof Mesh) originals.push(n); });
  const texture = new Texture(); const original = originals[0].material as MeshStandardMaterial;
  original.map = texture;
  const before = original.color.clone(), transform = gltf.scene.matrix.clone();
  const a = prepareArenaTable(gltf.scene), b = prepareArenaTable(gltf.scene);
  const meshA = a.scene.getObjectByName(originals[0].name) as Mesh;
  const meshB = b.scene.getObjectByName(originals[0].name) as Mesh;
  assert.notEqual(meshA.geometry, originals[0].geometry);
  assert.notEqual(meshA.geometry, meshB.geometry);
  assert.equal(meshA.geometry.attributes.position.count, originals[0].geometry.attributes.position.count);
  assert.deepEqual(meshA.geometry.attributes.position.array, originals[0].geometry.attributes.position.array);
  assert.deepEqual(meshA.geometry.attributes.normal.array, originals[0].geometry.attributes.normal.array);
  assert.ok(meshA.geometry.index!.count < originals[0].geometry.index!.count);
  // Retained components include both broad worktops and the supports/cabinet.
  const sourceSize = new Box3().setFromObject(gltf.scene).getSize(new Vector3());
  const retainedBounds = new Box3();
  a.scene.updateMatrixWorld(true);
  a.scene.traverse(node => {
    if (!(node instanceof Mesh)) return;
    const p = node.geometry.attributes.position, index = node.geometry.index!;
    for (let i = 0; i < index.count; i++) retainedBounds.expandByPoint(new Vector3().fromBufferAttribute(p, index.getX(i)).applyMatrix4(node.matrixWorld));
  });
  const fit = arenaTableFit(new Box3().setFromObject(gltf.scene));
  assert.ok(Math.abs(retainedBounds.getSize(new Vector3()).x - sourceSize.x * fit.scale) < 1e-6);
  assert.ok(Math.abs(retainedBounds.min.y - (new Box3().setFromObject(gltf.scene).min.y * fit.scale + fit.position[1])) < 1e-6);
  assert.ok(retainedBounds.max.y < 0, "no residual glass prop may protrude through the chamber floor");
  assert.notEqual(meshA.material, meshB.material); assert.notEqual(meshA.material, original);
  assert.equal((meshA.material as MeshStandardMaterial).map, null);
  assert.equal(original.map, texture, "source palette must remain untouched");
  assert.equal((meshA.material as MeshStandardMaterial).vertexColors, true);
  assert.ok(!originals[0].geometry.attributes.color, "source geometry must not acquire presentation colors");
  assert.equal(meshA.geometry.attributes.color.count, meshA.geometry.attributes.position.count);
  const colors = meshA.geometry.attributes.color;
  const tones = new Set(Array.from({ length: colors.count }, (_, i) => [colors.getX(i), colors.getY(i), colors.getZ(i)].join(":")));
  assert.ok(tones.size >= 3, "worktop, cabinet and trim should retain distinct tones");
  let sourceDisposals = 0, geometryDisposals = 0, textureDisposals = 0, otherDisposals = 0;
  original.addEventListener("dispose", () => sourceDisposals++);
  originals[0].geometry.addEventListener("dispose", () => geometryDisposals++);
  texture.addEventListener("dispose", () => textureDisposals++);
  (meshB.material as MeshStandardMaterial).addEventListener("dispose", () => otherDisposals++);
  a.dispose();
  assert.deepEqual([sourceDisposals, geometryDisposals, textureDisposals, otherDisposals], [0, 0, 0, 0]);
  assert.ok(original.color.equals(before)); assert.ok(gltf.scene.matrix.equals(transform));
  assert.ok(Math.abs(broadTop * a.scene.scale.x + a.scene.position.y - ARENA.tableTop) < 1e-12);
  b.dispose();
});

test("chamber retains its approved dimensions, four walls and a separate lid", () => {
  const panels = arenaPanels();
  assert.deepEqual(panels.map(p => p.id).sort(), ["back", "front", "left", "lid", "right"]);
  assert.deepEqual(panels.find(p => p.id === "lid")?.position, [0, ARENA.chamber.height, 0]);
  assert.deepEqual([ARENA.chamber.width, ARENA.chamber.depth, ARENA.chamber.height], [2.4, 1.22, .86]);
  assert.ok(panels.every(p => p.size.every(n => Number.isFinite(n) && n > 0)));
});

test("Inspect Fly fits the scaled specimen, preserves the anchor and resets to global Overview", () => {
  for (const aspect of [1.5, .55]) {
    const overview = arenaCamera(aspect, "three-quarter"), inspect = arenaCamera(aspect, "inspect");
    assert.deepEqual(inspect.target, overview.target);
    assert.ok(inspect.distance < overview.distance / 3);
    const camera = new PerspectiveCamera(inspect.fov, aspect, .005, 30);
    camera.position.fromArray(inspect.position);
    const before = camera.position.clone(); constrainArenaInspectionCamera(camera.position);
    assert.ok(before.equals(camera.position), "default inspect pose must be clear of the enclosure panels");
    camera.lookAt(new Vector3(...inspect.target)); camera.updateMatrixWorld();
    for (const x of [FLY_VIEWER_ASSET.bounds.min[0], FLY_VIEWER_ASSET.bounds.max[0]])
      for (const y of [FLY_VIEWER_ASSET.bounds.min[1], FLY_VIEWER_ASSET.bounds.max[1]])
        for (const z of [FLY_VIEWER_ASSET.bounds.min[2], FLY_VIEWER_ASSET.bounds.max[2]]) {
          const p = new Vector3(x, y, z).multiplyScalar(ARENA.flyScale).add(new Vector3(...ARENA.flyOffset)).project(camera);
          assert.ok(Math.abs(p.x) < 1 && Math.abs(p.y) < 1 && p.z > -1 && p.z < 1);
        }
    assert.deepEqual(arenaCamera(aspect, ARENA_RESET_VIEW), overview);
    assert.ok(arenaCameraLimits("inspect").minDistance > .3);
    assert.equal(arenaCameraLimits(ARENA_RESET_VIEW).maxPolarAngle, Math.PI);
  }
  const position = new Vector3(10, -10, 10); constrainArenaInspectionCamera(position);
  assert.ok(position.x < ARENA.chamber.width / 2 && position.y > .005 && position.z < ARENA.chamber.depth / 2);
});
