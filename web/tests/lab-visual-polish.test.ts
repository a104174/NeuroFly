import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { PerspectiveCamera, Vector3 } from "three";
import { exploreCamera, EXPLORE_STYLE, EXPLORE_CAMERA_LIMITS } from "../src/components/lab/explorePresentation";
import { arenaCamera, ARENA } from "../src/lib/experimentalArena";
import { FLY_VIEWER_ASSET } from "../src/lib/flyViewer";
import { FlyViewer } from "../src/components/FlyViewer";
import { ExploreLabView } from "../src/components/lab/ExploreLabView";

test("Explore framing keeps approved fly bounds and rear enclosure frame in view on portrait and landscape", () => {
  for (const aspect of [.35, .65, 1, 2, 3]) {
    const pose = exploreCamera(aspect), camera = new PerspectiveCamera(pose.fov, aspect, .01, 30);
    camera.position.fromArray(pose.position); camera.lookAt(new Vector3(...pose.target)); camera.updateMatrixWorld();
    assert([...pose.position, ...pose.target, pose.distance, pose.fov].every(Number.isFinite));
    for (const x of [FLY_VIEWER_ASSET.bounds.min[0], FLY_VIEWER_ASSET.bounds.max[0]])
      for (const y of [FLY_VIEWER_ASSET.bounds.min[1], FLY_VIEWER_ASSET.bounds.max[1]])
        for (const z of [FLY_VIEWER_ASSET.bounds.min[2], FLY_VIEWER_ASSET.bounds.max[2]]) {
          const p = new Vector3(x, y, z).multiplyScalar(ARENA.flyScale).add(new Vector3(...ARENA.flyOffset)).project(camera);
          assert(Math.abs(p.x) < 1 && Math.abs(p.y) < 1 && p.z > -1 && p.z < 1);
        }
    const front = new Vector3(0, ARENA.chamber.height, -ARENA.chamber.depth / 2).project(camera);
    assert(Math.abs(front.x) < 1 && Math.abs(front.y) < 1);
    assert(pose.distance > arenaCamera(aspect, "inspect").distance);
  }
});

test("invalid camera dimensions fail explicitly and portrait composition widens without resizing the organism", () => {
  for (const aspect of [0, -1, NaN, Infinity]) assert.throws(() => exploreCamera(aspect), /aspect/);
  assert(exploreCamera(.5).distance > exploreCamera(2).distance);
  assert.equal(ARENA.flyScale, .3);
  assert(EXPLORE_CAMERA_LIMITS.minDistance > 0);
  assert(EXPLORE_CAMERA_LIMITS.maxPolarAngle < Math.PI / 2);
});

test("product camera selection adds Explore and retains every historical preset", () => {
  const product = renderToStaticMarkup(createElement(FlyViewer, { arena: true, experience: true }));
  assert.match(product, /value="explore" selected=""/);
  for (const label of ["Overview", "Side", "Front", "Top", "Inspect", "Reset view"]) assert(product.includes(label));
  const historical = renderToStaticMarkup(createElement(FlyViewer, { arena: true }));
  assert.doesNotMatch(historical, /value="explore"/);
  assert.match(historical, /Inspect Fly/);
});

test("Explore camera calculations never mutate historical camera results", () => {
  for (const view of ["three-quarter", "lateral", "head", "dorsal", "inspect"] as const) {
    const before = arenaCamera(.7, view);
    exploreCamera(.7); exploreCamera(2);
    assert.deepEqual(arenaCamera(.7, view), before);
  }
  assert.notEqual(EXPLORE_STYLE.floor, "#555c61");
});

test("sidebar is compact and slowdown is disclosed both in status and model details", () => {
  const noop = () => {};
  const html = renderToStaticMarkup(createElement(ExploreLabView, { state: null, playing: false, error: null, notice: "", neuralEnabled: true, onPlay: noop, onReset: noop, onNeuralChange: noop, onExport: noop, onReplay: noop, lagging: true }));
  assert.doesNotMatch(html, /lab-guide|Make room for curiosity|Watch a turn|Play to begin/);
  assert.match(html, /class="lab-performance" role="status"/);
  assert.match(html, /Simulation slower than real time/);
  assert.match(html, /fixed simulation timestep remains unchanged/);
  assert.match(html, /simulation time, not wall-clock time/);
  assert.match(html, /<details class="lab-settings">/);
  assert.match(html, /<details class="lab-details">/);
});

test("turquoise ring remains the geometric landmark annotation, optional only in product presentation", () => {
  const arena = readFileSync(new URL("../src/components/ExperimentalArena.tsx", import.meta.url), "utf8");
  const viewer = readFileSync(new URL("../src/components/FlyViewer.tsx", import.meta.url), "utf8");
  assert.match(arena, /showLandmarks = true/);
  assert.match(arena, /showLandmarks && stimulusPlane !== undefined/);
  assert.match(arena, /name=\{`VisualStimulus\$\{i\}`\}/);
  assert.match(arena, /ringGeometry args=\{\[\.015,\.027/);
  assert.match(viewer, /showLandmarks=\{!experience \|\| showLandmarks\}/);
  assert.match(viewer, /Visibility does not change sensory inputs/);
});

test("scoped rendering uses the existing camera controller and one canvas, without a new simulation loop", () => {
  const renderer = readFileSync(new URL("../src/components/FlyViewerCanvas.tsx", import.meta.url), "utf8");
  const presentation = readFileSync(new URL("../src/components/lab/explorePresentation.ts", import.meta.url), "utf8");
  assert.equal((renderer.match(/<Canvas\b/g) ?? []).length, 1);
  assert.match(renderer, /explore = false, showLandmarks = true/);
  assert.match(renderer, /if \(view === "inspect"\) constrainArenaInspectionCamera/);
  assert.doesNotMatch(presentation, /ContinuousNavigationEngine|FixedStepClock|requestAnimationFrame|setInterval/);
});
