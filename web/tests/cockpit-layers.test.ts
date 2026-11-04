import assert from "node:assert/strict";
import { test } from "node:test";
import { COCKPIT_LAYERS, OVERVIEW_MAX, PHONE_MAX, effectiveLayer, layerFromKey, overviewReadouts, parseLayer, widthClass } from "../src/lib/cockpitLayers";
import type { CockpitFrame } from "../src/lib/cockpitModel";

const frame: CockpitFrame = { playbackTimeMs: 0.7, boundaryIndex: 6, boundaryTimeMs: 0.7, intervalStartMs: 0.6, cursorFraction: 0.5, thetaRad: 0.1, lc4DriveMveq: 0.2, lplc2DriveMveq: 0.3 };

test("Overview shows six readouts or fewer, and each carries a model unit", () => {
  const readouts = overviewReadouts(frame, 15);
  assert.ok(readouts.length <= OVERVIEW_MAX);
  assert.ok(PHONE_MAX <= 3);
  for (const r of readouts) assert.ok(r.unit === "dimensionless" || r.unit === "ms" || r.unit === "rad" || r.unit.endsWith("_eq"), r.id);
  assert.ok(!readouts.some((r) => (r.unit as string) === "mV"));
});

test("layers, keys and URL values", () => {
  assert.deepEqual([...COCKPIT_LAYERS], ["overview", "detail", "raw"]);
  assert.equal(layerFromKey("1"), "overview");
  assert.equal(layerFromKey("2"), "detail");
  assert.equal(layerFromKey("3"), "raw");
  assert.equal(layerFromKey("4"), null);
  assert.equal(parseLayer("raw"), "raw");
  assert.equal(parseLayer("nonsense"), null);
});

test("width classes and the layer each one starts in", () => {
  assert.equal(widthClass(1920), "wide");
  assert.equal(widthClass(1440), "standard");
  assert.equal(widthClass(800), "tablet");
  assert.equal(widthClass(390), "phone");
  assert.equal(effectiveLayer(null, "wide"), "detail");
  assert.equal(effectiveLayer(null, "standard"), "overview");
  assert.equal(effectiveLayer("raw", "standard"), "raw");
  assert.equal(effectiveLayer("raw", "phone"), "overview");
});

import { timelineStepFromKey, timelineValueText } from "../src/lib/timelineKeys";
test("Timeline keyboard model: arrows 1, Shift 10, Home and End, clamped", () => {
  assert.equal(timelineStepFromKey("ArrowRight", false, 5, 20), 6);
  assert.equal(timelineStepFromKey("ArrowLeft", false, 5, 20), 4);
  assert.equal(timelineStepFromKey("ArrowRight", true, 5, 20), 15);
  assert.equal(timelineStepFromKey("ArrowRight", true, 15, 20), 20);
  assert.equal(timelineStepFromKey("ArrowLeft", true, 3, 20), 0);
  assert.equal(timelineStepFromKey("Home", false, 9, 20), 0);
  assert.equal(timelineStepFromKey("End", false, 9, 20), 20);
  assert.equal(timelineStepFromKey("x", false, 9, 20), null);
  assert.equal(timelineValueText(119, 800), "Step 120 of 800");
});
