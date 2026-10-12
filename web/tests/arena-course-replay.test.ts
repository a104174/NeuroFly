import assert from "node:assert/strict";
import test from "node:test";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { Vector3 } from "three";
import { ARENA_COURSE_PAYLOAD_SHA256, arenaCoursePose, validateArenaCourseReplay } from "../src/lib/arenaCourseReplay";
import { ARENA, arenaCamera } from "../src/lib/experimentalArena";
import { FLY_VIEWER_ASSET } from "../src/lib/flyViewer";
import { advanceScenarioCursor } from "../src/lib/scenarioPlayback";
import { courseScene } from "../src/lib/courseControlPlayback";

// Real frozen replay via the canonical validator, never a runtime fixture.
const source = JSON.parse(execFileSync("python", ["-c", "import json,hashlib; from neurofly.scenario_playback_api import load_course_playback; r=load_course_playback().model_dump(mode='json',by_alias=True); print(json.dumps({'payload':r,'sha256':hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()).hexdigest()}))"], { cwd: fileURLToPath(new URL("../../", import.meta.url)), encoding: "utf8", maxBuffer: 1_000_000 }));
const replay = validateArenaCourseReplay(source.payload);
const close = (actual: number, expected: number) => assert.ok(Math.abs(actual - expected) < 1e-12, `${actual} != ${expected}`);
function transform(point: number[], cursor: number) {
  const pose = arenaCoursePose(replay, cursor);
  return new Vector3(...point).add(new Vector3(...pose.assetOffset)).multiplyScalar(ARENA.flyScale).applyAxisAngle(new Vector3(0, 1, 0), pose.rotation).add(new Vector3(...pose.anchor));
}
test("arena accepts only validated frozen Course identity and preserves its canonical hash", () => {
  assert.equal(source.sha256, ARENA_COURSE_PAYLOAD_SHA256);
  assert.equal(replay.frames.length, 501); assert.equal(replay.dt_ms, .1); assert.equal(replay.duration_ms, 50);
  assert.equal(replay.statuses.translation, "NOT_MODELLED");
  for (const change of [
    (r: typeof replay) => { r.scenario.id = "HORIZONTAL_MOTION_NEURAL_VALIDATION"; },
    (r: typeof replay) => { r.artifact_id = "a".repeat(64); },
    (r: typeof replay) => { r.frames[1].yaw_orientation_eq = NaN; },
    (r: typeof replay) => { r.frames[2].time_ms = .1; },
    (r: typeof replay) => { r.frames.splice(10, 1); },
    (r: typeof replay) => { Object.assign(r.world_reference, { period_eq: 2 }); },
  ]) { const r = structuredClone(replay); change(r); assert.throws(() => validateArenaCourseReplay(r)); }
});
test("representative Course rotations preserve sign, exact magnitude, scale and fixed thoracic pivot", () => {
  const before = JSON.stringify(replay);
  for (const [index, yaw] of [[0, 0], [1, .001], [50, .0007304413993428759], [250, .0003228997450294182], [500, .00033277101655776]]) {
    const pose = arenaCoursePose(replay, index);
    close(pose.rotation, yaw * 2 * Math.PI); assert.equal(ARENA.flyScale, .30);
    const anchor = FLY_VIEWER_ASSET.canonical_transform.origin === "model origin" ? FLY_VIEWER_ASSET.canonical_transform.visual_anchor.position : [0, 0, 0];
    transform(anchor, index).toArray().forEach((n, i) => close(n, pose.anchor[i]));
    const p = new Vector3(0, 0, 1).applyAxisAngle(new Vector3(0, 1, 0), pose.rotation); assert.ok(p.x >= 0);
  }
  for (const q of [FLY_VIEWER_ASSET.bounds.min, FLY_VIEWER_ASSET.bounds.max]) transform(q, 0).toArray().forEach((n, i) => close(n, q[i] * .30 + ARENA.flyOffset[i]));
  assert.equal(JSON.stringify(replay), before);
});
test("every recorded and interpolated orientation remains inside the unchanged enclosure", () => {
  const c = ARENA.chamber;
  for (let cursor = 0; cursor <= 500; cursor += .5)
    for (const x of [FLY_VIEWER_ASSET.bounds.min[0], FLY_VIEWER_ASSET.bounds.max[0]])
      for (const y of [FLY_VIEWER_ASSET.bounds.min[1], FLY_VIEWER_ASSET.bounds.max[1]])
        for (const z of [FLY_VIEWER_ASSET.bounds.min[2], FLY_VIEWER_ASSET.bounds.max[2]]) {
          const p = transform([x, y, z], cursor);
          assert.ok(Math.abs(p.x) < (c.width - c.wall) / 2 && Math.abs(p.z) < (c.depth - c.wall) / 2 && p.y > 0 && p.y < c.height - c.wall / 2);
        }
});
test("adjacent interpolation and exact boundary telemetry preserve nulls, seek, pause, finish and reset", () => {
  for (const i of [0, 1, 50, 250, 499]) {
    const scene = courseScene(replay, i + .5);
    const selectedPose = arenaCoursePose(replay, i);
    assert.equal(scene.frame, replay.frames[i]);
    close(scene.renderRotation, (replay.frames[i].yaw_orientation_eq + replay.frames[i + 1].yaw_orientation_eq) * Math.PI);
    arenaCoursePose(replay, Math.min(i + 37, 500));
    assert.deepEqual(arenaCoursePose(replay, i), selectedPose);
  }
  assert.equal(courseScene(replay, 0).frame.observation, null);
  assert.equal(courseScene(replay, 500).frame.external_orientation_increment_eq, null);
  assert.equal(advanceScenarioCursor(100, 1000, false, 500), 100);
  assert.equal(advanceScenarioCursor(0, 6000, true, 500), 500);
  assert.equal(advanceScenarioCursor(499, 6000, true, 500), 500);
  assert.equal(arenaCoursePose(replay, 0).rotation, 0);
  assert.notEqual(arenaCoursePose(replay, 500).rotation, 0);
  for (const i of [-1, 501, NaN, Infinity]) assert.throws(() => arenaCoursePose(replay, i));
});
test("camera presets keep a fixed target independent from replay orientation", () => {
  for (const view of ["three-quarter", "lateral", "head", "dorsal", "inspect"] as const) {
    const camera = arenaCamera(1.8, view);
    for (const cursor of [0, 1, 250, 500]) arenaCoursePose(replay, cursor).anchor.forEach((n, i) => close(n, camera.target[i]));
  }
});
test("incompatible presentation scale or chamber fails rather than resizing or clamping", () => {
  const originalScale = ARENA.flyScale, originalWidth = ARENA.chamber.width;
  try {
    ARENA.flyScale = .35;
    assert.throws(() => validateArenaCourseReplay(replay), /incompatível/);
    ARENA.flyScale = originalScale;
    ARENA.chamber.width = .1;
    assert.throws(() => validateArenaCourseReplay(replay), /limites/);
  } finally { ARENA.flyScale = originalScale; ARENA.chamber.width = originalWidth; }
});
