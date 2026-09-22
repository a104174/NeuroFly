import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import {
  parseMorphologyArtifactSummary,
  parseMorphologyBody,
  parseStructuralConnectivity,
  type MorphologyBody,
  type MorphologyBodyId,
} from "../src/lib/neuroflyClient";
import {
  buildMorphologyLineComponents,
  bodySourceBounds,
  componentSourceBounds,
  deriveSharedMorphologyViewTransform,
  DNP01_MORPHOLOGY_VIEW_ID,
  focusForSourceBounds,
  globalMorphologyFocus,
  isMorphologySelectionVisible,
  MALECNS_SIX_BODY_MORPHOLOGY_VIEW_ID,
  selectMorphologyBody,
  selectMorphologyComponent,
  sourceBoundsFromNodes,
} from "../src/lib/morphologyView";
import {
  buildSchematicStructuralConnectors,
  deriveStructuralBodyAnchors,
} from "../src/lib/connectivityView";

const hash = (letter: string) => letter.repeat(64);

const BODY_PROVENANCE = {
  10001: [0, "DNp01", "R"],
  10010: [1, "DNp01", "L"],
  11498: [2, "LPLC2", "L"],
  12032: [3, "LC4", "L"],
  14465: [12, "LPLC2", "R"],
  16128: [16, "LC4", "R"],
} as const;

function body(bodyId: MorphologyBodyId): Record<string, unknown> {
  const [nodeIndex, neuronType, side] = BODY_PROVENANCE[bodyId];
  const offset = nodeIndex * 100;
  const components: Array<Record<string, unknown>> = [
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
  ];
  if (bodyId === 11498) {
    components.push({
      component_id: 1,
      nodes: [{ node_id: 3, x: offset + 30, y: 40, z: 50, radius: 4 }],
      links: [],
    });
  }
  return {
    schema: "morphology_api_v1",
    kind: "morphology_body",
    artifact_id: hash("a"),
    artifact_schema_version: "malecns_morphology_artifact_v1",
    dataset: "male-cns:v1.0",
    candidate: { identifier: "looming_giant_fiber_v1", version: 1 },
    body_id: bodyId,
    node_index: nodeIndex,
    neuron_type: neuronType,
    source_side: side,
    source_status: "Traced",
    morphology_mode: "RAW",
    node_count: bodyId === 11498 ? 3 : 2,
    link_count: 1,
    component_count: bodyId === 11498 ? 2 : 1,
    source_bounds: {
      minimum: [offset, 0, 0],
      maximum: [offset + 10, 20, 30],
    },
    source_swc_sha256: bodyId.toString(16).padStart(64, "0"),
    spatial_record_id: `sha256:${(bodyId + 1).toString(16).padStart(64, "0")}`,
    source_category: "MALECNS_DIRECT_DATA",
    morphology_source: "JANELIA_NEUPRINT_MALECNS_SKELETON",
    coordinate_frame_id: "male_cns_v1_em_native_voxels",
    coordinate_unit: "8_nm_voxel",
    soma_location: { x: offset, y: 1, z: 2 },
    components,
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

function connectivityPayload() {
  const bodies = [10001, 10010, 11498, 12032, 14465, 16128].map((bodyId) => {
    const [nodeIndex, neuronType, sourceSide] = BODY_PROVENANCE[bodyId as MorphologyBodyId];
    return { body_id: bodyId, node_index: nodeIndex, neuron_type: neuronType, source_side: sourceSide, source_status: "Traced" };
  });
  const edges = [
    { pre_body_id: 11498, pre_node_index: 2, pre_neuron_type: "LPLC2", pre_source_side: "L", post_body_id: 10010, post_node_index: 1, post_neuron_type: "DNp01", post_source_side: "L", structural_weight: 2 },
    { pre_body_id: 12032, pre_node_index: 3, pre_neuron_type: "LC4", pre_source_side: "L", post_body_id: 10010, post_node_index: 1, post_neuron_type: "DNp01", post_source_side: "L", structural_weight: 62 },
    { pre_body_id: 14465, pre_node_index: 12, pre_neuron_type: "LPLC2", pre_source_side: "R", post_body_id: 10001, post_node_index: 0, post_neuron_type: "DNp01", post_source_side: "R", structural_weight: 21 },
    { pre_body_id: 16128, pre_node_index: 16, pre_neuron_type: "LC4", pre_source_side: "R", post_body_id: 10001, post_node_index: 0, post_neuron_type: "DNp01", post_source_side: "R", structural_weight: 65 },
  ];
  return {
    schema: "malecns_structural_connectivity_v1",
    kind: "bounded_structural_connectivity",
    dataset: "male-cns:v1.0",
    candidate: { identifier: "looming_giant_fiber_v1", version: 1 },
    source_contract: {
      source: "Janelia neuPrint / MaleCNS",
      endpoint: "https://neuprint.janelia.org",
      dataset: "male-cns:v1.0",
      acquired_at_utc: "2026-09-10T20:39:56.889520+00:00",
      neuprint_python_version: "0.6.3",
      integrity: {
        sha256_verified: true,
        record_counts_verified: true,
        sha256_by_file: [
          { file: "neurons.jsonl", sha256: "00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e" },
          { file: "connections.jsonl", sha256: "f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a" },
        ],
      },
      structural_weight_source: "neuPrint ConnectsTo.weight",
      structural_weight_is_physiological_coupling: false,
    },
    fixed_sample: {
      id: "phase5i_six_body_visual_to_dnp01_v1",
      body_ids: [10001, 10010, 11498, 12032, 14465, 16128],
      bodies,
    },
    projection: {
      id: "phase5i_six_body_visual_to_dnp01_v1",
      pre_neuron_types: ["LC4", "LPLC2"],
      post_neuron_type: "DNp01",
      direction: "pre_body_id -> post_body_id",
      canonical_order: "pre_node_index, then post_node_index",
      edge_semantics: "directed structural ConnectsTo relationships from the CircuitContract",
    },
    edge_semantics: {
      weight_field: "structural_weight",
      weight_source: "neuPrint ConnectsTo.weight",
      structural_weight_is_physiological_coupling: false,
    },
    edges,
    aggregates: {
      edge_count: 4,
      total_structural_weight: 150,
      structural_weight_by_source_type: { LC4: 127, LPLC2: 23 },
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

test("six-body parsing preserves types, fragmentation, and one shared transform", () => {
  const bodyIds = [10001, 10010, 11498, 12032, 14465, 16128] as const;
  const payload = summary() as unknown as {
    body_ids: number[];
    bodies: Record<string, unknown>[];
    generation: Record<string, unknown>;
  };
  payload.body_ids = [...bodyIds];
  payload.bodies = bodyIds.map((bodyId) => {
    const item = body(bodyId);
    return Object.fromEntries(
      Object.entries(item).filter(([key]) =>
        [
          "body_id", "node_index", "neuron_type", "source_side", "source_status",
          "morphology_mode", "node_count", "link_count", "component_count",
          "source_bounds", "source_swc_sha256", "spatial_record_id",
        ].includes(key),
      ),
    );
  });
  payload.generation.source_mode = "OFFICIAL_MALECNS_BULK_SWC";
  payload.generation.retrieval =
    "official_malecns_bulk_swc(raw, heal=False, smoothing=False, repair=False)";
  payload.generation.source_urls = Object.fromEntries(
    bodyIds.map((bodyId) => [
      String(bodyId),
      `https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/${bodyId}.swc`,
    ]),
  );
  const artifact = parseMorphologyArtifactSummary(payload);
  const bodies = bodyIds.map((bodyId) => parseMorphologyBody(body(bodyId)));
  const sourceBefore = structuredClone(bodies);
  const transform = deriveSharedMorphologyViewTransform(bodies);
  assert.deepEqual(artifact.body_ids, [...bodyIds]);
  assert.deepEqual(new Set(bodies.map((item) => item.neuron_type)), new Set(["LC4", "LPLC2", "DNp01"]));
  assert.equal(bodies.find((item) => item.body_id === 11498)?.components.length, 2);
  assert.equal(buildMorphologyLineComponents(bodies[2], transform).length, 2);
  assert.equal(transform.view_id, MALECNS_SIX_BODY_MORPHOLOGY_VIEW_ID);
  assert.equal(transform.uniform_scale, 8 / 1610);
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
  assert.match(source, /Show \{neuronType\}/);
  assert.match(source, /component_count > 1/);
  assert.match(source, /lineBasicMaterial/);
  assert.match(source, /Selection and highlighting are presentation only/);
  assert.equal(source.includes("spike animation"), false);
  assert.equal(source.includes("component bridge"), false);
});

test("source bounds and camera focus are deterministic and leave the shared transform untouched", () => {
  const bodies = [parseMorphologyBody(body(10001)), parseMorphologyBody(body(10010))];
  const before = structuredClone(bodies);
  const transform = deriveSharedMorphologyViewTransform(bodies);
  const transformBefore = structuredClone(transform);
  const componentBounds = componentSourceBounds(bodies[0].components[0]);
  assert.deepEqual(componentBounds, { minimum: [0, 0, 0], maximum: [10, 20, 30] });
  assert.deepEqual(bodySourceBounds(bodies[1]), { minimum: [100, 0, 0], maximum: [110, 20, 30] });
  assert.deepEqual(sourceBoundsFromNodes(bodies[0].components[0].nodes), componentBounds);
  assert.throws(() => sourceBoundsFromNodes([{ node_id: 1, x: Infinity, y: 0, z: 0, radius: null }]), /finite/);
  const bodyFocus = focusForSourceBounds(bodySourceBounds(bodies[1]), transform, 1.5, "body");
  const componentFocus = focusForSourceBounds(componentBounds, transform, 1.5, "component");
  assert.deepEqual(bodyFocus, focusForSourceBounds(bodySourceBounds(bodies[1]), transform, 1.5, "body"));
  assert.notDeepEqual(bodyFocus.target, componentFocus.target);
  assert.deepEqual(globalMorphologyFocus(), { kind: "global", target: [0, 0, 0], position: [8.5, 6.5, 10.5] });
  assert.ok([...bodyFocus.target, ...bodyFocus.position].every(Number.isFinite));
  assert.deepEqual(transform, transformBefore);
  assert.deepEqual(bodies, before);
});

test("fragmented 11498 retains separate component selection, focus, and links", () => {
  const input = body(11498);
  const components = input.components as Array<Record<string, unknown>>;
  components.splice(0, components.length, ...[9, 2112].map((count, componentId) => {
    const firstId = componentId === 0 ? 1 : 10;
    const offset = componentId === 0 ? 200 : 300;
    return {
      component_id: componentId,
      nodes: Array.from({ length: count }, (_, index) => ({
        node_id: firstId + index, x: offset + index, y: componentId * 50, z: 0, radius: null,
      })),
      links: Array.from({ length: count - 1 }, (_, index) => ({
        child_node_id: firstId + index + 1,
        parent_node_id: firstId + index,
        provenance: "MALECNS_RAW_SKELETON_LINK",
      })),
    };
  }));
  input.node_count = 2121;
  input.link_count = 2119;
  input.source_bounds = { minimum: [200, 0, 0], maximum: [2411, 50, 0] };
  const fragmented = parseMorphologyBody(input);
  const bodies = [10001, 10010, 11498, 12032, 14465, 16128].map(
    (bodyId) => bodyId === 11498 ? fragmented : parseMorphologyBody(body(bodyId as MorphologyBodyId)),
  );
  const before = structuredClone(fragmented);
  const transform = deriveSharedMorphologyViewTransform(bodies);
  const first = fragmented.components[0];
  const second = fragmented.components[1];
  assert.deepEqual(fragmented.components.map((component) => [component.component_id, component.nodes.length, component.links.length]), [[0, 9, 8], [1, 2112, 2111]]);
  assert.deepEqual(selectMorphologyComponent(11498, 0), { bodyId: 11498, componentId: 0 });
  assert.deepEqual(selectMorphologyComponent(11498, 1), { bodyId: 11498, componentId: 1 });
  assert.notDeepEqual(
    focusForSourceBounds(componentSourceBounds(first), transform, 1.5, "component").target,
    focusForSourceBounds(componentSourceBounds(second), transform, 1.5, "component").target,
  );
  const lines = buildMorphologyLineComponents(fragmented, transform);
  assert.deepEqual(lines.map((line) => [line.componentId, line.positions.length]), [[0, 48], [1, 12666]]);
  assert.ok(first.links.every((link) => link.child_node_id <= 9 && link.parent_node_id <= 9));
  assert.ok(second.links.every((link) => link.child_node_id >= 10 && link.parent_node_id >= 10));
  assert.deepEqual(fragmented, before);
  assert.equal(transform.view_id, MALECNS_SIX_BODY_MORPHOLOGY_VIEW_ID);
});

test("selection and visibility remain local presentation state", () => {
  const parsed = parseMorphologyBody(body(11498));
  const before = structuredClone(parsed);
  const selection = selectMorphologyComponent(11498, 1);
  const visible = { 10001: true, 10010: true, 11498: false, 12032: true, 14465: true, 16128: true };
  assert.equal(isMorphologySelectionVisible(selection, visible), false);
  assert.deepEqual(selectMorphologyBody(11498), { bodyId: 11498, componentId: null });
  assert.equal(isMorphologySelectionVisible(selection, { ...visible, 11498: true }), true);
  assert.equal("selectedBody" in parsed, false);
  assert.equal("selectedComponent" in parsed, false);
  assert.equal("focus" in parsed, false);
  assert.deepEqual(parsed, before);
  assert.deepEqual(new Set(Object.values(BODY_PROVENANCE).map((item) => item[1])), new Set(["LC4", "LPLC2", "DNp01"]));
});

test("structural connectivity parser accepts the fixed source projection and rejects contract drift", () => {
  const valid = connectivityPayload();
  const parsed = parseStructuralConnectivity(valid);
  assert.equal(parsed.edges.length, 4);
  assert.deepEqual(parsed.edges.map((edge) => edge.structural_weight), [2, 62, 21, 65]);
  const wrongBodySet = structuredClone(valid);
  (wrongBodySet.fixed_sample.body_ids as number[])[0] = 999;
  assert.throws(() => parseStructuralConnectivity(wrongBodySet), /fixed body set/);
  const wrongRole = structuredClone(valid);
  (wrongRole.edges as Array<Record<string, unknown>>)[0].pre_neuron_type = "DNp01";
  assert.throws(() => parseStructuralConnectivity(wrongRole), /fixed directed projection/);
  const reversed = structuredClone(valid);
  (reversed.edges as Array<Record<string, unknown>>)[0] = {
    ...(reversed.edges as Array<Record<string, unknown>>)[0],
    pre_body_id: 10010, pre_node_index: 1, pre_neuron_type: "DNp01", pre_source_side: "L",
    post_body_id: 11498, post_node_index: 2, post_neuron_type: "LPLC2", post_source_side: "L",
  };
  assert.throws(() => parseStructuralConnectivity(reversed), /fixed directed projection/);
  const unsupportedRelation = structuredClone(valid);
  (unsupportedRelation.edges as Array<Record<string, unknown>>)[0] = {
    ...(unsupportedRelation.edges as Array<Record<string, unknown>>)[0],
    post_body_id: 10001,
    post_node_index: 0,
    post_source_side: "R",
  };
  assert.throws(() => parseStructuralConnectivity(unsupportedRelation), /pinned source projection/);
  const unsupportedWeight = structuredClone(valid);
  (unsupportedWeight.edges as Array<Record<string, unknown>>)[0].structural_weight = 3;
  assert.throws(() => parseStructuralConnectivity(unsupportedWeight), /pinned source projection/);
  const invalidWeight = structuredClone(valid);
  (invalidWeight.edges as Array<Record<string, unknown>>)[0].structural_weight = 0;
  assert.throws(() => parseStructuralConnectivity(invalidWeight), /fixed directed projection/);
  const fractionalWeight = structuredClone(valid);
  (fractionalWeight.edges as Array<Record<string, unknown>>)[0].structural_weight = 1.5;
  assert.throws(() => parseStructuralConnectivity(fractionalWeight), /integer/);
  const unsupportedSchema = structuredClone(valid);
  unsupportedSchema.schema = "malecns_structural_connectivity_v2";
  assert.throws(() => parseStructuralConnectivity(unsupportedSchema), /schema is not supported/);
  const badProvenance = structuredClone(valid);
  (badProvenance.source_contract as Record<string, unknown>).endpoint = "https://example.invalid";
  assert.throws(() => parseStructuralConnectivity(badProvenance), /provenance is unsupported/);
  const badHash = structuredClone(valid);
  const badHashes = (badHash.source_contract as { integrity: { sha256_by_file: { sha256: string }[] } }).integrity.sha256_by_file;
  badHashes[0].sha256 = "a".repeat(64);
  assert.throws(() => parseStructuralConnectivity(badHash), /source hashes do not match/);
  const changedAggregate = structuredClone(valid);
  (changedAggregate.aggregates as Record<string, unknown>).total_structural_weight = 151;
  assert.throws(() => parseStructuralConnectivity(changedAggregate), /aggregates do not match/);
  const duplicateEdge = structuredClone(valid);
  (duplicateEdge.edges as Array<Record<string, unknown>>)[1] = structuredClone(
    (duplicateEdge.edges as Array<Record<string, unknown>>)[0],
  );
  assert.throws(() => parseStructuralConnectivity(duplicateEdge), /duplicate directed edges/);
  const outOfOrder = structuredClone(valid);
  (outOfOrder.edges as Array<Record<string, unknown>>).reverse();
  assert.throws(() => parseStructuralConnectivity(outOfOrder), /canonical order/);
});

test("schematic connectors use shared transformed body-bound centers and body selection only", () => {
  const bodies = [10001, 10010, 11498, 12032, 14465, 16128].map((bodyId) =>
    parseMorphologyBody(body(bodyId as MorphologyBodyId)),
  );
  const projection = parseStructuralConnectivity(connectivityPayload());
  const before = structuredClone(bodies);
  const transform = deriveSharedMorphologyViewTransform(bodies);
  const visibility = { 10001: true, 10010: true, 11498: true, 12032: true, 14465: true, 16128: true };
  const anchors = deriveStructuralBodyAnchors(bodies, transform);
  const connectors = buildSchematicStructuralConnectors(projection, bodies, transform, selectMorphologyBody(11498), visibility);
  assert.equal(connectors.length, 4);
  assert.deepEqual(connectors.map(({ preBodyId, postBodyId }) => [preBodyId, postBodyId]), projection.edges.map(({ pre_body_id, post_body_id }) => [pre_body_id, post_body_id]));
  assert.deepEqual(connectors[0].start, anchors.get(11498));
  assert.deepEqual(connectors[0].end, anchors.get(10010));
  assert.equal(connectors[0].highlighted, true);
  assert.equal(connectors[1].highlighted, false);
  const selectedComponent = buildSchematicStructuralConnectors(projection, bodies, transform, selectMorphologyComponent(11498, 1), visibility);
  assert.deepEqual(selectedComponent, connectors);
  const hidden = buildSchematicStructuralConnectors(projection, bodies, transform, selectMorphologyBody(11498), { ...visibility, 11498: false });
  assert.equal(hidden[0].visible, false);
  assert.equal(hidden[1].visible, true);
  assert.ok(connectors.every((connector) => connector.opacity === 0.82 || connector.opacity === 0.14));
  assert.deepEqual(bodies, before);
  assert.equal(transform.view_id, MALECNS_SIX_BODY_MORPHOLOGY_VIEW_ID);
  const inspector = readFileSync(new URL("../src/components/MorphologyInspector.tsx", import.meta.url), "utf8");
  assert.equal(inspector.includes("connector.structuralWeight"), false);
  assert.equal(inspector.includes("useFrame"), false);
  assert.equal(inspector.includes("FlyVisualAsset"), false);
  assert.match(inspector, /Show structural connectivity/);
  assert.ok(inspector.includes(" → "));
  assert.match(inspector, /schematic anchors/);
});

test("healed and repair-link source contracts are rejected", () => {
  const healed = body(10001);
  healed.morphology_mode = "HEALED";
  assert.throws(() => parseMorphologyBody(healed), /supported raw/);
  const repaired = body(10001);
  const components = repaired.components as Array<Record<string, unknown>>;
  const links = components[0].links as Array<Record<string, unknown>>;
  links[0].provenance = "NEUROFLY_ARTIFICIAL_REPAIR_LINK";
  assert.throws(() => parseMorphologyBody(repaired), /non-raw link/);
});
