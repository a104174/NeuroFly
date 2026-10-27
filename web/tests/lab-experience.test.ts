import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ExploreLabView, explorationStatus } from "../src/components/lab/ExploreLabView";
import { FlyViewer } from "../src/components/FlyViewer";
import { ContinuousNavigationEngine } from "../src/lib/continuousArenaNavigation";
import { parseNeuralLocomotion } from "../src/lib/neuralLocomotion";
import { presentationGaitHistory } from "../src/lib/articulatedGait";

const authority = parseNeuralLocomotion(JSON.parse(readFileSync(new URL("../public/experiments/experimental_locomotion_v1.json", import.meta.url), "utf8")));
const noop = () => {};
const initial = () => new ContinuousNavigationEngine(authority).snapshot();
function markup(state = initial(), playing = false) {
  return renderToStaticMarkup(createElement(ExploreLabView, { state, playing, error: null, notice: "", neuralEnabled: true, onPlay: noop, onReset: noop, onNeuralChange: noop, onExport: noop, onReplay: noop, lagging: false }, "Scene"));
}

test("default Lab opens Explore with a real viewer, home navigation and no historical selector wall", () => {
  const html = markup();
  const page = readFileSync(new URL("../src/app/visual-lab/arena/page.tsx", import.meta.url), "utf8");
  assert.match(html, /Explore<span>\.<\/span>/);
  assert.match(page, /href="\/" aria-label="NeuroFly home"/);
  assert.match(html, /Exploration controls/);
  assert.match(page, /<LiveExploreArena/);
  assert.doesNotMatch(page, /ArenaCourseViewer/);
  assert.doesNotMatch(html, /arena-mode-controls|Experimental Locomotion v0|Motor-to-Gait Bridge v7/);
  assert.equal((html.match(/<h1\b/g) ?? []).length, 1);
});

test("accessible controls distinguish loading, playing, paused, complete and error states", () => {
  const state = initial();
  assert.equal(explorationStatus(null, false, null), "Preparing");
  assert.equal(explorationStatus(state, false, null), "Ready to explore");
  assert.equal(explorationStatus(state, true, null), "Exploring");
  assert.equal(explorationStatus({ ...state, step: 20 }, false, null), "Paused");
  assert.equal(explorationStatus({ ...state, step: 1500 }, false, null), "Exploration complete");
  assert.equal(explorationStatus(state, false, "failed"), "Unavailable");
  assert.match(markup(), /00:00 \/ 00:30/);
  assert.match(markup(state, true), />Pause<\/button>/);
  assert.match(markup({ ...state, step: 20, time: .4 }), />Resume<\/button>/);
  const complete = markup({ ...state, step: 1500, time: 30 });
  assert.match(complete, /00:30 \/ 00:30/);
  assert.match(complete, /Explore again/);
});

test("settings and diagnostics are closed native disclosures and report actual model values", () => {
  const html = markup();
  assert.match(html, /<details class="lab-settings"><summary>/);
  assert.match(html, /<details class="lab-details"><summary>/);
  assert.match(html, /Neural influence/);
  assert.match(html, /Changing this starts a new exploration/);
  assert.match(html, /data-live-step="0"/);
  assert.match(html, /href="\/scenarios"/);
  assert.match(html, /href="\/visual-lab\/arena\/research"/);
  assert.doesNotMatch(html, /<details[^>]*\bopen[ =>]/);
});

test("Explore gait is opt-in at composition boundary; historical viewers keep their original defaults", () => {
  const historical = renderToStaticMarkup(createElement(FlyViewer, { arena: true }));
  const product = renderToStaticMarkup(createElement(FlyViewer, { arena: true, experience: true, initialGait: true, initialView: "inspect" }));
  assert.match(historical, /Articulated Gait v6/);
  assert.doesNotMatch(historical, /checked=""/);
  assert.match(product, /checked=""/);
  assert.match(product, /Leg animation/);
  assert.match(product, /id="lab-camera"/);
  assert.match(product, /Display &amp; credits/);
  assert.doesNotMatch(product, /class="fly-viewer-toolbar"/);
});

test("existing navigation remains authoritative while presentation gait consumes its completed history", () => {
  const engine = new ContinuousNavigationEngine(authority);
  const history = [];
  for (let n = 0; n < 100; n++) { const f = engine.advance(); history.push({ time: f.time, position: f.position, orientation: f.orientation }); }
  const state = engine.snapshot(), before = structuredClone(state);
  const gait = presentationGaitHistory({ frames: history, end: { time: state.time, position: state.position, heading: state.heading }, time: state.time });
  assert(gait.some(s => s.moving));
  assert.equal(gait.length, 101);
  assert.deepEqual(engine.snapshot(), before);
  assert.deepEqual(gait.at(-1)!.body.position, state.position);
});

test("composition reuses the single existing runtime and retains complete research implementations", () => {
  const runtime = readFileSync(new URL("../src/components/ContinuousNavigationArena.tsx", import.meta.url), "utf8");
  const ui = readFileSync(new URL("../src/components/lab/ExploreLabView.tsx", import.meta.url), "utf8");
  const research = readFileSync(new URL("../src/app/visual-lab/arena/research/page.tsx", import.meta.url), "utf8");
  assert.match(runtime, /if\(presentation==="explore"\)return <ExploreLabView/);
  assert.match(runtime, /<FlyViewer experience initialGait/);
  assert.doesNotMatch(ui, /new ContinuousNavigationEngine|requestAnimationFrame|setInterval/);
  assert.match(research, /<ArenaCourseViewer \/>/);
});
