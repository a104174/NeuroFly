import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { advanceLocomotion, loadLocomotion, locomotionScene, LOCOMOTION_SHA256, parseLocomotion } from "../src/lib/experimentalLocomotion";
import { FLY_VIEWER_ASSET } from "../src/lib/flyViewer";
import { ARENA } from "../src/lib/experimentalArena";
import { Vector3 } from "three";
const bytes = readFileSync(new URL("../public/experiments/experimental_locomotion_v0.json", import.meta.url));
const replay = parseLocomotion(JSON.parse(bytes.toString()));
test("Python generated replay has pinned bytes, explicit engineering identity and matched stationary control", () => {
  assert.equal(createHash("sha256").update(bytes).digest("hex"), LOCOMOTION_SHA256);
  assert.equal(replay.config.neural_steering, "NOT_MODELLED");
  assert.equal(replay.result.runs[0].frames.length, 401);
  assert.ok(replay.result.runs[0].distance > .9);
  const control = replay.result.runs[1];
  assert.equal(control.distance, 0);
  control.frames.forEach(f => assert.deepEqual(f.position, control.frames[0].position));
});
test("play, pause, resume and finish use seconds independent of FPS; reset pose is exact", () => {
  const t = advanceLocomotion(0, 2000, true);
  assert.equal(t, 2);
  assert.equal(advanceLocomotion(t, 3000, false), t);
  assert.equal(advanceLocomotion(t, 1000, true), 3);
  assert.equal(advanceLocomotion(7.9, 1000, true), 8);
  assert.equal(advanceLocomotion(8, 1000, true), 8);
  assert.deepEqual(locomotionScene(replay, 0, 0).pose.anchor, replay.config.initial_position);
  assert.ok(Math.abs(locomotionScene(replay, 0, t).pose.anchor[0] - .36) < 1e-12);
});
test("adjacent pose interpolation is synchronized, remains on floor and inside walls", () => {
  const before = JSON.stringify(replay);
  for (let n = 0; n <= 800; n++) {
    const time = n / 100, scene = locomotionScene(replay, 0, time), pose = scene.pose;
    assert.equal(pose.rotation, Math.PI / 2);
    for (const x of [FLY_VIEWER_ASSET.bounds.min[0], FLY_VIEWER_ASSET.bounds.max[0]]) for (const y of [FLY_VIEWER_ASSET.bounds.min[1], FLY_VIEWER_ASSET.bounds.max[1]]) for (const z of [FLY_VIEWER_ASSET.bounds.min[2], FLY_VIEWER_ASSET.bounds.max[2]]) {
      const p = new Vector3(x, y, z).add(new Vector3(...pose.assetOffset)).multiplyScalar(ARENA.flyScale).applyAxisAngle(new Vector3(0,1,0), pose.rotation).add(new Vector3(...pose.anchor));
      assert.ok(Math.abs(p.x) <= (2.4 - .012) / 2 && Math.abs(p.z) <= (1.22 - .012) / 2);
      assert.ok(p.y > 0 && p.y < .86 - .006);
    }
  }
  assert.equal(JSON.stringify(replay), before);
  assert.equal(locomotionScene(replay, 0, 8).frame.contact, "X_WALL");
  assert.equal(locomotionScene(replay, 0, 8).speed, 0);
});
test("malformed, missing and contradictory data fail visibly instead of generating motion", async () => {
  for (const mutate of [
    (r: typeof replay) => { r.result.runs[0].frames.pop(); },
    (r: typeof replay) => { r.result.runs[0].frames[2].time = 0; },
    (r: typeof replay) => { r.result.runs[0].frames[1].position[0] = NaN; },
    (r: typeof replay) => { r.result.runs[0].frames[1].position[0] = 1; },
    (r: typeof replay) => { r.config.propulsion_source = "BIOLOGICAL_MUSCLE"; },
    (r: typeof replay) => { r.config.chamber.width = 3; },
    (r: typeof replay) => { r.result.runs[1].frames[1].linear_velocity[0] = 1; },
    (r: typeof replay) => { r.result.runs[0].contact_events = []; },
  ]) { const r = structuredClone(replay); mutate(r); assert.throws(() => parseLocomotion(r)); }
  await assert.rejects(loadLocomotion(async () => new Response("broken")), /corrompidos/);
  await assert.rejects(loadLocomotion(async () => new Response(null, {status:404})), /HTTP 404/);
  for (const t of [-1, NaN, 9]) assert.throws(() => locomotionScene(replay, 0, t));
  assert.throws(() => advanceLocomotion(0, -1, true));
});
