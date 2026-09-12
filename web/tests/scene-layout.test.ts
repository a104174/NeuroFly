import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import {
  FLY_VISUAL_ASSET,
  flyVisualAssetProvenance,
} from "../src/lib/flyVisualAsset";
import type { ExperimentSceneState } from "../src/lib/playback";
import {
  derivePresentationOverlayState,
  mapPresentationIntensity,
  SCENE_PRESENTATION_COORDINATE_SPACE,
  SCENE_PRESENTATION_LAYOUT,
  SCENE_PRESENTATION_LAYOUT_ID,
} from "../src/lib/sceneLayout";

const sceneState: ExperimentSceneState = {
  playbackTimeMs: 1.75,
  boundaryIndex: 1,
  boundaryTimeMs: 1,
  intervalIndex: 1,
  intervalStartMs: 1,
  thetaRad: 0.2,
  angularExpansionVelocityRadS: 2,
  lc4NormalizedFeature: 0.4,
  lplc2NormalizedFeature: 0.7,
  lc4DriveMveq: 4,
  lplc2DriveMveq: 7,
  lc4PresentationLevel: 0.4,
  lplc2PresentationLevel: 0.7,
  stimulusPresentationLevel: 0.5,
  dnp01: {
    10001: {
      bodyId: 10001,
      membraneMv: -61,
      synapticStateMveq: 0.2,
      presentationLevel: 0.25,
      spikedAtSelectedBoundary: false,
    },
    10010: {
      bodyId: 10010,
      membraneMv: -58,
      synapticStateMveq: 0.5,
      presentationLevel: 0.75,
      spikedAtSelectedBoundary: true,
    },
  },
};

test("scene layout is versioned presentation space with distinct anchors", () => {
  assert.equal(SCENE_PRESENTATION_LAYOUT.layout_id, SCENE_PRESENTATION_LAYOUT_ID);
  assert.equal(
    SCENE_PRESENTATION_LAYOUT.coordinate_space,
    SCENE_PRESENTATION_COORDINATE_SPACE,
  );
  assert.equal(
    SCENE_PRESENTATION_LAYOUT.scientific_status,
    "PRESENTATION_ONLY_NOT_ANATOMICAL",
  );
  assert.notDeepEqual(
    SCENE_PRESENTATION_LAYOUT.pathways.LC4.anchor,
    SCENE_PRESENTATION_LAYOUT.pathways.LPLC2.anchor,
  );
  assert.notDeepEqual(
    SCENE_PRESENTATION_LAYOUT.dnp01[10001].anchor,
    SCENE_PRESENTATION_LAYOUT.dnp01[10010].anchor,
  );
  assert.equal(Object.isFrozen(SCENE_PRESENTATION_LAYOUT), true);
  assert.equal(Object.isFrozen(SCENE_PRESENTATION_LAYOUT.pathways.LC4), true);
  assert.deepEqual(
    SCENE_PRESENTATION_LAYOUT.fly.origin,
    FLY_VISUAL_ASSET.canonical_transform.scene_position,
  );
  assert.equal("anatomical_coordinates" in SCENE_PRESENTATION_LAYOUT, false);
  assert.equal("soma_coordinates" in SCENE_PRESENTATION_LAYOUT, false);
});

test("presentation intensity is bounded and monotonic", () => {
  const values = [-1, 0, 0.25, 0.5, 1, 4].map(mapPresentationIntensity);
  assert.equal(values[0], values[1]);
  assert.equal(values.at(-1), values.at(-2));
  for (let index = 1; index < values.length; index += 1) {
    assert.ok(values[index] >= values[index - 1]);
  }
  assert.ok(values.every((value) => value >= 0.16 && value <= 0.84));
});

test("overlay derivation preserves raw data and pathway/body separation", () => {
  const overlay = derivePresentationOverlayState(sceneState);
  assert.equal(overlay.looming.rawThetaRad, sceneState.thetaRad);
  assert.equal(
    overlay.looming.rawAngularExpansionVelocityRadS,
    sceneState.angularExpansionVelocityRadS,
  );
  assert.equal(
    overlay.pathways.LC4.rawNormalizedFeature,
    sceneState.lc4NormalizedFeature,
  );
  assert.equal(
    overlay.pathways.LPLC2.rawNormalizedFeature,
    sceneState.lplc2NormalizedFeature,
  );
  assert.equal(overlay.pathways.LC4.rawDriveMveq, sceneState.lc4DriveMveq);
  assert.equal(
    overlay.pathways.LPLC2.rawDriveMveq,
    sceneState.lplc2DriveMveq,
  );
  assert.equal(overlay.dnp01[10001].bodyId, 10001);
  assert.equal(overlay.dnp01[10010].bodyId, 10010);
  assert.equal(overlay.dnp01[10001].rawMembraneMv, -61);
  assert.equal(overlay.dnp01[10010].rawMembraneMv, -58);
  assert.equal(overlay.dnp01[10010].persistedBoundarySpike, true);
  assert.equal("behavior" in overlay, false);
  assert.equal("anatomicalPosition" in overlay, false);
  assert.equal("interpolatedValue" in overlay, false);
});

test("visual provenance remains presentation-only and separate from experiments", () => {
  const provenance = flyVisualAssetProvenance();
  assert.equal(provenance.assetId, "neurofly_fly_visual_v1");
  assert.equal(provenance.assetVersion, 1);
  assert.match(provenance.sha256Prefix, /^[a-f0-9]{12}$/);
  assert.equal(provenance.exportTool, "Blender");
  assert.equal(provenance.exportToolVersion, "4.0.2");
  assert.equal(provenance.presentationOnly, true);
  assert.equal("experimentConfigId" in provenance, false);
  assert.equal("resultId" in provenance, false);

  const workspaceSource = readFileSync(
    new URL("../src/components/PlaybackWorkspace.tsx", import.meta.url),
    "utf8",
  );
  assert.match(workspaceSource, /NOT ANATOMICAL COORDINATES/);
  assert.match(workspaceSource, /Empirical validation/);
  assert.doesNotMatch(workspaceSource, /escape triggered|motor output/i);
});
