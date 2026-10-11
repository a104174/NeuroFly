import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { Vector3 } from "three";
import { FLY_VIEWER_ASSET, flyViewerCamera, verifyFlyViewerBytes } from "../src/lib/flyViewer";
import { flyPresentationAnchor } from "../src/lib/flyVisualInstance";
import { parseVisualV2 } from "../src/lib/flyVisualAssetV2";
import { FLY_VISUAL_ASSET } from "../src/lib/flyVisualAsset";

test("real approved GLB identity, static combined anatomy, channels and attribution", async () => {
  const b = readFileSync(new URL("../public/assets/fly/fly_visual_v2f.glb", import.meta.url));
  assert.equal(b.length, 2418784);
  assert.equal(createHash("sha256").update(b).digest("hex"), "0502cb995d25b2f9d7b57eff0cf95a0c9cfd7f838e212e95b3895bb69c7e5238");
  const bytes = new Uint8Array(b).buffer;
  await verifyFlyViewerBytes(bytes); await assert.rejects(verifyFlyViewerBytes(bytes, "0".repeat(64)), /checksum/);
  assert.equal(b.toString("ascii", 0, 4), "glTF");
  const source = JSON.parse(b.toString("utf8", 20, 20 + b.readUInt32LE(12)));
  const names = source.nodes.map((n: { name: string }) => n.name);
  assert.equal(new Set(names).size, 285);
  for (const name of FLY_VIEWER_ASSET.nodes.required) assert.ok(names.includes(name));
  assert.ok(!names.includes("Thorax") && !names.includes("Abdomen"));
  assert.equal(FLY_VIEWER_ASSET.anatomy?.body_topology, "combined");
  assert.equal(source.images.length, 5); assert.equal(source.materials.length, 5);
  assert.equal(source.animations?.length ?? 0, 0); assert.equal(source.skins?.length ?? 0, 0);
  const eye = source.materials.find((m: { name: string }) => m.name === "Eyes.DeepRedMicrofacet");
  assert.ok(eye.normalTexture && eye.pbrMetallicRoughness.baseColorTexture && eye.pbrMetallicRoughness.metallicRoughnessTexture);
  for (const name of FLY_VIEWER_ASSET.materials.roles.wings) {
    const wing = source.materials.find((m: { name: string }) => m.name === name);
    assert.equal(wing.alphaMode, "BLEND"); assert.equal(wing.doubleSided, true); assert.ok(wing.pbrMetallicRoughness.baseColorTexture);
  }
  assert.equal(FLY_VIEWER_ASSET.provenance.author, "mlykouretzos");
  assert.equal(FLY_VIEWER_ASSET.provenance.license_url, "https://creativecommons.org/licenses/by/4.0/");
  assert.match(FLY_VIEWER_ASSET.provenance.attribution, /Modified for NeuroFly/);
  assert.equal(FLY_VISUAL_ASSET.asset_version, 1);
});

test("anchor transforms scale then rotation then translation, without relocating geometry", () => {
  assert.deepEqual(flyPresentationAnchor(FLY_VIEWER_ASSET, "historical"), [0, .06168119236826897, .12187743186950684]);
  const m = parseVisualV2({ ...FLY_VIEWER_ASSET, canonical_transform: { ...FLY_VIEWER_ASSET.canonical_transform, scene_position: [1, 2, 3], scene_uniform_scale: 2, scene_rotation_euler_rad: [0, 0, Math.PI / 2] } });
  const anchor = flyPresentationAnchor(m, "historical");
  const expected = [1 - 2 * .06168119236826897, 2, 3 + 2 * .12187743186950684];
  anchor.forEach((n, i) => assert.ok(Math.abs(n - expected[i]) < 1e-12));
});

test("reset poses target the anchor and keep framing valid at narrow aspect ratios", () => {
  const initial = flyViewerCamera(1.5);
  for (const aspect of [1.5, .55]) for (const view of ["three-quarter", "lateral", "head", "dorsal"] as const) {
    const camera = flyViewerCamera(aspect, view);
    assert.deepEqual(camera.target, initial.target);
    assert.ok(camera.position.every(Number.isFinite));
    assert.ok(Math.abs(new Vector3(...camera.position).distanceTo(new Vector3(...camera.target)) - camera.distance) < 1e-12);
  }
  assert.ok(flyViewerCamera(.55).distance > initial.distance);
  assert.deepEqual(flyViewerCamera(1.5), initial);
});

test("responsive preset framing contains all declared bounds without compensating model orientation", async () => {
  const { PerspectiveCamera } = await import("three");
  for (const aspect of [1.5, .55]) for (const view of ["three-quarter", "lateral", "head", "dorsal"] as const) {
    const pose = flyViewerCamera(aspect, view);
    const camera = new PerspectiveCamera(pose.fov, aspect, .01, 30);
    camera.position.fromArray(pose.position); camera.lookAt(new Vector3(...pose.target)); camera.updateMatrixWorld();
    for (const x of [FLY_VIEWER_ASSET.bounds.min[0], FLY_VIEWER_ASSET.bounds.max[0]])
      for (const y of [FLY_VIEWER_ASSET.bounds.min[1], FLY_VIEWER_ASSET.bounds.max[1]])
        for (const z of [FLY_VIEWER_ASSET.bounds.min[2], FLY_VIEWER_ASSET.bounds.max[2]]) {
          const projected = new Vector3(x, y, z).project(camera);
          assert.ok(Math.abs(projected.x) < 1 && Math.abs(projected.y) < 1 && projected.z > -1 && projected.z < 1);
        }
  }
});
