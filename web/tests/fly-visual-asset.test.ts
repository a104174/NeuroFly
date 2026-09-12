import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import {
  FLY_VISUAL_ASSET,
  FLY_VISUAL_ASSET_ID,
  flyAssetStatusMessage,
  parseFlyVisualAssetManifest,
} from "../src/lib/flyVisualAsset";

const manifestPath = new URL("../src/assets/fly_visual_v1.json", import.meta.url);
const glbPath = new URL(
  "../public/assets/fly/fly_visual_v1.glb",
  import.meta.url,
);

function glbJson(payload: Buffer): Record<string, unknown> {
  assert.equal(payload.subarray(0, 4).toString("ascii"), "glTF");
  assert.equal(payload.readUInt32LE(4), 2);
  assert.equal(payload.readUInt32LE(8), payload.length);
  const jsonLength = payload.readUInt32LE(12);
  assert.equal(payload.subarray(16, 20).toString("ascii"), "JSON");
  return JSON.parse(
    payload.subarray(20, 20 + jsonLength).toString("utf8").trim(),
  ) as Record<string, unknown>;
}

test("visual asset manifest preserves its versioned presentation identity", () => {
  const raw = JSON.parse(readFileSync(manifestPath, "utf8")) as Record<
    string,
    unknown
  >;
  const manifest = parseFlyVisualAssetManifest(raw);
  assert.deepEqual(manifest, FLY_VISUAL_ASSET);
  assert.equal(manifest.asset_id, FLY_VISUAL_ASSET_ID);
  assert.equal(manifest.runtime.public_url, "/assets/fly/fly_visual_v1.glb");
  assert.equal(manifest.canonical_transform.runtime_up_axis, "+Y");
  assert.equal(manifest.canonical_transform.runtime_forward_axis, "+Z");
  assert.equal(manifest.canonical_transform.origin, "thorax center");
  assert.equal(manifest.scientific_status.presentation_only, true);
  assert.equal("experiment_config_id" in raw, false);
  assert.equal("result_id" in raw, false);
  assert.equal("artifact_id" in raw, false);
  assert.equal("comparison_id" in raw, false);
});

test("tracked GLB hash and static export block remain valid", () => {
  const payload = readFileSync(glbPath);
  const digest = createHash("sha256").update(payload).digest("hex");
  assert.equal(digest, FLY_VISUAL_ASSET.runtime.sha256);

  const glb = glbJson(payload);
  assert.equal(Array.isArray(glb.animations) ? glb.animations.length : 0, 0);
  assert.equal(Array.isArray(glb.cameras) ? glb.cameras.length : 0, 0);
  assert.equal(Array.isArray(glb.images) ? glb.images.length : 0, 0);
  assert.equal(
    Array.isArray(glb.materials) ? glb.materials.length : 0,
    FLY_VISUAL_ASSET.measured.material_count,
  );
});

test("loading and failure states explicitly preserve the procedural fallback", () => {
  assert.equal(flyAssetStatusMessage("loading"), "Loading 3D asset…");
  assert.equal(
    flyAssetStatusMessage("error"),
    "Fly asset unavailable · procedural fallback",
  );
  assert.match(flyAssetStatusMessage("ready"), /presentation only/);

  const componentSource = readFileSync(
    new URL("../src/components/FlyVisualAsset.tsx", import.meta.url),
    "utf8",
  );
  assert.equal(componentSource.includes("<Suspense fallback={<AssetLoading"), true);
  assert.equal(
    componentSource.includes(
      "this.state.failed ? <ProceduralFlyPlaceholder /> : this.props.children",
    ),
    true,
  );
  assert.doesNotMatch(componentSource, /ExperimentTimeline|neuroflyClient|playback/);
});
