import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import {
  parseMorphologyArtifactSummary,
  parseMorphologyBody,
  type MorphologyBody,
} from "../src/lib/neuroflyClient";
import {
  buildMorphologyLineComponents,
  deriveSharedMorphologyViewTransform,
  DNP01_MORPHOLOGY_VIEW_ID,
} from "../src/lib/morphologyView";

const hash = (letter: string) => letter.repeat(64);

function body(bodyId: 10001 | 10010): Record<string, unknown> {
  const offset = bodyId === 10001 ? 0 : 100;
  return {
    schema: "morphology_api_v1",
    kind: "morphology_body",
    artifact_id: hash("a"),
    artifact_schema_version: "malecns_morphology_artifact_v1",
    dataset: "male-cns:v1.0",
    candidate: { identifier: "looming_giant_fiber_v1", version: 1 },
    body_id: bodyId,
    node_index: bodyId === 10001 ? 0 : 1,
    neuron_type: "DNp01",
    source_side: bodyId === 10001 ? "R" : "L",
    source_status: "Traced",
    morphology_mode: "RAW",
    node_count: 2,
    link_count: 1,
    component_count: 1,
    source_bounds: {
      minimum: [offset, 0, 0],
      maximum: [offset + 10, 20, 30],
    },
    source_swc_sha256: hash(bodyId === 10001 ? "b" : "c"),
    spatial_record_id: `sha256:${hash(bodyId === 10001 ? "d" : "e")}`,
    source_category: "MALECNS_DIRECT_DATA",
    morphology_source: "JANELIA_NEUPRINT_MALECNS_SKELETON",
    coordinate_frame_id: "male_cns_v1_em_native_voxels",
    coordinate_unit: "8_nm_voxel",
    soma_location: { x: offset, y: 1, z: 2 },
    components: [
      {
        component_id: 0,
        nodes: [
          { node_id: 1, x: offset, y: 0, z: 0, radius: 1 },
          { node_id: 2, x: offset + 10, y: 20, z: 30, radius: 99 },
        ],
        links: [
          {
            child_node_id: 2,
            parent_node_id: 1,
            provenance: "MALECNS_RAW_SKELETON_LINK",
          },
        ],
      },
    ],
  };
}

function summary() {
  const bodies = [body(10001), body(10010)].map((item) => ({
    body_id: item.body_id,
    node_index: item.node_index,
    neuron_type: item.neuron_type,
    source_side: item.source_side,
    source_status: item.source_status,
    morphology_mode: item.morphology_mode,
    node_count: item.node_count,
    link_count: item.link_count,
    component_count: item.component_count,
    source_bounds: item.source_bounds,
    source_swc_sha256: item.source_swc_sha256,
    spatial_record_id: item.spatial_record_id,
  }));
  return {
    schema: "morphology_api_v1",
    kind: "morphology_artifact_summary",
    artifact_id: hash("a"),
    artifact_schema_version: "malecns_morphology_artifact_v1",
    dataset: "male-cns:v1.0",
    candidate: { identifier: "looming_giant_fiber_v1", version: 1 },
    coordinate_frame_id: "male_cns_v1_em_native_voxels",
    coordinate_unit: "8_nm_voxel",
    morphology_mode: "RAW",
    body_ids: [10001, 10010],
    bodies,
    generation: {
      generated_at_utc: "2026-09-13T00:00:00Z",
      neuprint_python_version: "0.6.1",
      source_endpoint: "https://neuprint.janelia.org",
      retrieval: "fetch_skeleton(heal=False, format=swc)",
      source_mode: "JANELIA_NEUPRINT_MALECNS_SKELETON",
      source_urls: {},
    },
  };
}

test("morphology schemas preserve fixed raw provenance", () => {
  const artifact = parseMorphologyArtifactSummary(summary());
  const first = parseMorphologyBody(body(10001));
  const second = parseMorphologyBody(body(10010));
  assert.deepEqual(artifact.body_ids, [10001, 10010]);
  assert.deepEqual([first.body_id, first.node_index, first.source_side], [10001, 0, "R"]);
  assert.deepEqual([second.body_id, second.node_index, second.source_side], [10010, 1, "L"]);
  assert.equal(first.coordinate_unit, "8_nm_voxel");
  assert.equal(first.components[0].links[0].provenance, "MALECNS_RAW_SKELETON_LINK");
  assert.equal("experiment_config_id" in first, false);
  assert.equal("playback_time_ms" in first, false);
});

test("official bulk SWC provenance is accepted without changing body identity", () => {
  const officialSummary = summary();
  const generation = officialSummary.generation as Record<string, unknown>;
  generation.source_mode = "OFFICIAL_MALECNS_BULK_SWC";
  generation.source_urls = {
    "10001":
      "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/10001.swc",
    "10010":
      "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/10010.swc",
  };
  generation.retrieval =
    "official_malecns_bulk_swc(raw, heal=False, smoothing=False, repair=False)";
  const officialBody = body(10001);
  officialBody.morphology_source = "OFFICIAL_MALECNS_BULK_SWC";
  const parsedSummary = parseMorphologyArtifactSummary(officialSummary);
  const parsedBody = parseMorphologyBody(officialBody);
  assert.equal(parsedSummary.generation.source_mode, "OFFICIAL_MALECNS_BULK_SWC");
  assert.equal(parsedBody.morphology_source, "OFFICIAL_MALECNS_BULK_SWC");
  assert.equal(parsedSummary.body_ids.join(","), "10001,10010");
});

test("one shared deterministic uniform transform preserves relative positions", () => {
  const bodies = [parseMorphologyBody(body(10001)), parseMorphologyBody(body(10010))] as [MorphologyBody, MorphologyBody];
  const sourceBefore = structuredClone(bodies);
  const transform = deriveSharedMorphologyViewTransform(bodies);
  assert.deepEqual(transform, deriveSharedMorphologyViewTransform(bodies));
  assert.equal(transform.view_id, DNP01_MORPHOLOGY_VIEW_ID);
  assert.equal(transform.uniform_scale, 8 / 110);
  assert.deepEqual(transform.center_source, [55, 10, 15]);
  assert.deepEqual(transform.axis_mapping, { source_x: "view_x", source_y: "view_y", source_z: "view_z" });
  const first = buildMorphologyLineComponents(bodies[0], transform)[0].positions;
  const second = buildMorphologyLineComponents(bodies[1], transform)[0].positions;
  assert.ok(second[0] > first[0]);
  assert.deepEqual(bodies, sourceBefore);
});

test("render contract uses native axes without anatomical mapping", () => {
  const source = readFileSync(new URL("../src/components/MorphologyInspector.tsx", import.meta.url), "utf8");
  assert.match(source, /lineBasicMaterial/);
  assert.match(source, /linewidth=\{1\}/);
  assert.equal(source.includes("FlyVisualAsset"), false);
  assert.equal(source.includes("node.radius"), false);
  assert.match(source, /Source x\/y\/z are MaleCNS native voxel axes/);
  assert.match(source, /not\s+labelled anterior\/posterior, dorsal\/ventral, or left\/right/);
  assert.match(source, /source x\/y\/z → view x\/y\/z/);
  assert.equal(source.includes("anatomical_position"), false);
  assert.equal(source.includes("anatomical_coordinates"), false);
  assert.equal(source.includes("signal direction"), true);
});

test("healed and repair-link source contracts are rejected", () => {
  const healed = body(10001);
  healed.morphology_mode = "HEALED";
  assert.throws(() => parseMorphologyBody(healed), /raw DNp01/);
  const repaired = body(10001);
  const components = repaired.components as Array<Record<string, unknown>>;
  const links = components[0].links as Array<Record<string, unknown>>;
  links[0].provenance = "NEUROFLY_ARTIFICIAL_REPAIR_LINK";
  assert.throws(() => parseMorphologyBody(repaired), /non-raw link/);
});
