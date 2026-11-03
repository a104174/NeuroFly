import assert from "node:assert/strict";
import { register } from "node:module";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createFrameRateWatch, dprRange, nextLowerTier } from "../src/lib/viewportTier";

// Node cannot import CSS Modules; see tests/support/css-hooks.mjs.
register(new URL("./support/css-hooks.mjs", import.meta.url));
const { Viewport3D } = await import("../src/components/ui/Viewport3D");
const { StatePanel } = await import("../src/components/ui/StatePanel");

test("tiers drop high to medium to low and stay at low", () => {
  assert.equal(nextLowerTier("high"), "medium");
  assert.equal(nextLowerTier("medium"), "low");
  assert.equal(nextLowerTier("low"), "low");
});

test("pixel ratio is capped: 1.5 on phones, 2 on desktop, 1 on the low tier", () => {
  assert.deepEqual(dprRange("high", true), [1, 1.5]);
  assert.deepEqual(dprRange("high", false), [1, 2]);
  assert.deepEqual(dprRange("low", false), [1, 1]);
});

test("a sustained rate under 30 fps for 3 s reports a drop; 60 fps does not", () => {
  const slow = createFrameRateWatch();
  let dropped = false;
  for (let t = 0; t <= 3500; t += 50) dropped = slow(t) || dropped; // 20 fps
  assert.equal(dropped, true);
  const fast = createFrameRateWatch();
  let fastDropped = false;
  for (let t = 0; t <= 6000; t += 16) fastDropped = fast(t) || fastDropped;
  assert.equal(fastDropped, false);
});

test("the frame reserves its aspect ratio, names its kind, and describes the view before WebGL is known", () => {
  const html = renderToStaticMarkup(createElement(Viewport3D, {
    title: "Reconstructed neuron shapes", kind: "structural", aspect: "16 / 10", description: "Six skeletons.", children: () => null,
  }));
  assert.match(html, /aspect-ratio:16 \/ 10/);
  assert.match(html, /Structural/);
  assert.match(html, /Six skeletons\./);
  assert.match(html, /Loading reconstructed neuron shapes/); // pending state, no canvas yet
  assert.doesNotMatch(html, /<canvas/);
});

test("missing data is a useful message, not an empty stage", () => {
  const html = renderToStaticMarkup(createElement(Viewport3D, {
    title: "Neuron shapes", kind: "structural", description: "d", missingData: { what: "Neuron shapes", detail: "Fetch failed." }, children: () => null,
  }));
  assert.match(html, /Neuron shapes not included in this artifact\./);
  assert.match(html, /Fetch failed\./);
});

test("WebGL-off and context-lost panels say what happened and what still works", () => {
  const off = renderToStaticMarkup(createElement(StatePanel, { state: "webgl-off", hasDataAlternative: true }));
  assert.match(off, /3D isn&#x27;t available on this device\./);
  assert.match(off, /The data below is the same\./);
  const lost = renderToStaticMarkup(createElement(StatePanel, { state: "context-lost", actions: createElement("button", null, "Restart 3D view") }));
  assert.match(lost, /role="alert"/);
  assert.match(lost, /Nothing on this page has been lost\./);
  assert.match(lost, /Restart 3D view/);
});
