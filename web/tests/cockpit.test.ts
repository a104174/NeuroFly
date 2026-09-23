import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import {
  COCKPIT_MORPHOLOGY_ARTIFACT_ID,
  cockpitEventPosition,
  deriveCockpitEvents,
  deriveCockpitFrame,
  validateCockpitConnectivity,
  validateCockpitExperiment,
  validateCockpitMorphology,
} from "../src/lib/cockpitModel";
import { toggleCockpitFocus, type CockpitFocusState } from "../src/lib/cockpitLayout";
import {
  activityContextForBody,
  bodySpecificActivityByMorphologyIdentity,
  deriveActivityStructureProjection,
} from "../src/lib/activityStructure";
import {
  CONNECTIVITY_SOURCE_HASHES,
  STRUCTURAL_CONNECTIVITY_BODY_IDS,
  STRUCTURAL_CONNECTIVITY_PROJECTION_ID,
  type BodyTelemetry,
  type ExperimentSummary,
  type ExperimentTimeline,
  type MorphologyArtifactSummary,
  type MorphologyBody,
  type MorphologyBodyId,
  type StructuralConnectivityProjection,
} from "../src/lib/neuroflyClient";
import { deriveSceneState, seekPlayback, createPlaybackClock } from "../src/lib/playback";

const bodyIdentities = {
  10001: [0, "DNp01", "R"],
  10010: [1, "DNp01", "L"],
  11498: [2, "LPLC2", "L"],
  12032: [3, "LC4", "L"],
  14465: [12, "LPLC2", "R"],
  16128: [16, "LC4", "R"],
} as const;

function bodyTelemetry(bodyId: 10001 | 10010, spikes: number[]): BodyTelemetry {
  return {
    body_id: bodyId,
    neuron_type: "DNp01",
    soma_side: bodyId === 10001 ? "R" : "L",
    time_unit: "ms",
    times_ms: [0, 1, 2, 3],
    step_times_ms: [0, 1, 2],
    membrane_unit: "mV",
    membrane_mv: bodyId === 10001 ? [-65, -61, -55, -51] : [-65, -62, -53, -50],
    synaptic_state_unit: "mV_eq",
    synaptic_state_mveq: [0, 0.2, 0.4, 0.6],
    external_drive_unit: "mV_eq",
    external_drive_mveq: [0, 0, 0],
    incoming_coupling_unit: "mV_eq",
    incoming_coupling_mveq: [0, 0.1, 0.2],
    spike_times_ms: spikes,
  };
}

function timeline(): ExperimentTimeline {
  return {
    schema: "experiment_api_v1",
    kind: "experiment_timeline",
    artifact_id: "e".repeat(64),
    time_unit: "ms",
    dt_ms: 1,
    duration_ms: 3,
    start_ms: 0,
    end_ms: 3,
    times_ms: [0, 1, 2, 3],
    step_times_ms: [0, 1, 2],
    interval_semantics: "step_values_apply_on_[t_n,t_n+dt)",
    theta_unit: "rad",
    theta_rad: [0.1, 0.2, 0.3],
    angular_expansion_velocity_unit: "rad/s",
    angular_expansion_velocity_rad_s: [1, 2, 3],
    lc4_normalized_feature: [0.1, 0.2, 0.3],
    lplc2_normalized_feature: [0.2, 0.3, 0.4],
    drive_unit: "mV_eq",
    lc4_drive_mveq: [1, 2, 3],
    lplc2_drive_mveq: [4, 5, 6],
    selected_body_telemetry: [bodyTelemetry(10001, [2]), bodyTelemetry(10010, [1, 3])],
  };
}

function summary(): ExperimentSummary {
  const population = {
    neuron_type: "LC4" as const,
    body_count: 126,
    bodies_that_spike: 0,
    total_spike_count: 0,
    first_spike_time_ms: null,
    peak_normalized_feature: 0,
    peak_drive_mveq: 0,
  };
  const dnp = (bodyId: 10001 | 10010) => ({
    body_id: bodyId,
    neuron_type: "DNp01",
    soma_side: bodyId === 10001 ? "R" : "L",
    total_spike_count: 1,
    first_spike_time_ms: 1,
    peak_membrane_mv: -50,
    peak_synaptic_state_mveq: 0.6,
    delivered_event_count: 0,
    model_increment_sum_mveq: 0,
  });
  return {
    schema: "experiment_api_v1",
    kind: "experiment_summary",
    artifact_id: "e".repeat(64),
    experiment_config_id: "config",
    experiment_config_sha256: "c".repeat(64),
    result_id: "result",
    artifact_schema_version: "experiment_artifact_v1",
    dataset: "male-cns:v1.0",
    candidate: { identifier: "looming_giant_fiber_v1", version: 1 },
    source: {
      endpoint: "https://neuprint.janelia.org",
      circuit_integrity: Object.entries(CONNECTIVITY_SOURCE_HASHES).map(([file, digest]) => [file, digest]),
    },
    graph_scope_id: "direct_visual_to_dnp01_v1",
    encoder: {
      id: "level_p_instantaneous_bounded_v1",
      version: "phase2e_v1",
      population_policy: "bilateral_type_broadcast_v1",
    },
    neural_model: {
      id: "lif_filtered_synapse",
      version: "phase2b_v1",
      membrane_state_references: { rest_mv: -52, threshold_mv: -45 },
    },
    pathway_condition: "both",
    duration_ms: 3,
    dt_ms: 1,
    validation_status: "NOT_EVALUATED",
    telemetry_profile: {},
    free_parameters: {
      lc4_gain_mv_eq: 1,
      lplc2_gain_mv_eq: 1,
      omega_half_rad_per_s: 1,
      theta_half_rad: 1,
      k_syn_mv_per_contact: 1,
    },
    populations: { LC4: population, LPLC2: { ...population, neuron_type: "LPLC2" } },
    dnp01: [dnp(10001), dnp(10010)],
  };
}

function morphologyBody(bodyId: MorphologyBodyId): MorphologyBody {
  const [nodeIndex, neuronType, side] = bodyIdentities[bodyId];
  return {
    schema: "morphology_api_v1",
    kind: "morphology_body",
    artifact_id: COCKPIT_MORPHOLOGY_ARTIFACT_ID,
    artifact_schema_version: "malecns_morphology_artifact_v1",
    dataset: "male-cns:v1.0",
    candidate: { identifier: "looming_giant_fiber_v1", version: 1 },
    source_category: "MALECNS_DIRECT_DATA",
    morphology_source: "OFFICIAL_MALECNS_BULK_SWC",
    coordinate_frame_id: "male_cns_v1_em_native_voxels",
    coordinate_unit: "8_nm_voxel",
    soma_location: null,
    body_id: bodyId,
    node_index: nodeIndex,
    neuron_type: neuronType,
    source_side: side,
    source_status: "Traced",
    morphology_mode: "RAW",
    node_count: 1,
    link_count: 0,
    component_count: 1,
    source_bounds: { minimum: [nodeIndex, 0, 0], maximum: [nodeIndex, 0, 0] },
    source_swc_sha256: "a".repeat(64),
    spatial_record_id: "sha256:" + "b".repeat(64),
    components: [{ component_id: 0, nodes: [{ node_id: 1, x: nodeIndex, y: 0, z: 0, radius: null }], links: [] }],
  };
}

function morphology(bodies: readonly MorphologyBody[]): MorphologyArtifactSummary {
  return {
    schema: "morphology_api_v1",
    kind: "morphology_artifact_summary",
    artifact_id: COCKPIT_MORPHOLOGY_ARTIFACT_ID,
    artifact_schema_version: "malecns_morphology_artifact_v1",
    dataset: "male-cns:v1.0",
    candidate: { identifier: "looming_giant_fiber_v1", version: 1 },
    coordinate_frame_id: "male_cns_v1_em_native_voxels",
    coordinate_unit: "8_nm_voxel",
    morphology_mode: "RAW",
    body_ids: [...STRUCTURAL_CONNECTIVITY_BODY_IDS],
    bodies: bodies.map(({ components: _components, ...body }) => body),
    generation: {
      generated_at_utc: "2026-09-14T01:54:16.562719+00:00",
      neuprint_python_version: "not_used_for_official_bulk_swc",
      source_endpoint: "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/",
      source_mode: "OFFICIAL_MALECNS_BULK_SWC",
      source_urls: {},
      retrieval: "official_malecns_bulk_swc(raw, heal=False, smoothing=False, repair=False)",
    },
  };
}

function connectivity(): StructuralConnectivityProjection {
  const bodies = STRUCTURAL_CONNECTIVITY_BODY_IDS.map((bodyId) => {
    const [nodeIndex, neuronType, side] = bodyIdentities[bodyId];
    return { body_id: bodyId, node_index: nodeIndex, neuron_type: neuronType, source_side: side, source_status: "Traced" };
  });
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
        sha256_by_file: Object.entries(CONNECTIVITY_SOURCE_HASHES).map(([file, sha256]) => ({ file: file as "neurons.jsonl" | "connections.jsonl", sha256 })),
      },
      structural_weight_source: "neuPrint ConnectsTo.weight",
      structural_weight_is_physiological_coupling: false,
    },
    fixed_sample: { id: STRUCTURAL_CONNECTIVITY_PROJECTION_ID, body_ids: [...STRUCTURAL_CONNECTIVITY_BODY_IDS], bodies },
    projection: {
      id: STRUCTURAL_CONNECTIVITY_PROJECTION_ID,
      pre_neuron_types: ["LC4", "LPLC2"],
      post_neuron_type: "DNp01",
      direction: "pre_body_id -> post_body_id",
      canonical_order: "pre_node_index, then post_node_index",
      edge_semantics: "directed structural ConnectsTo relationships from the CircuitContract",
    },
    edge_semantics: { weight_field: "structural_weight", weight_source: "neuPrint ConnectsTo.weight", structural_weight_is_physiological_coupling: false },
    edges: [
      { pre_body_id: 11498, pre_node_index: 2, pre_neuron_type: "LPLC2", pre_source_side: "L", post_body_id: 10010, post_node_index: 1, post_neuron_type: "DNp01", post_source_side: "L", structural_weight: 2 },
      { pre_body_id: 12032, pre_node_index: 3, pre_neuron_type: "LC4", pre_source_side: "L", post_body_id: 10010, post_node_index: 1, post_neuron_type: "DNp01", post_source_side: "L", structural_weight: 62 },
      { pre_body_id: 14465, pre_node_index: 12, pre_neuron_type: "LPLC2", pre_source_side: "R", post_body_id: 10001, post_node_index: 0, post_neuron_type: "DNp01", post_source_side: "R", structural_weight: 21 },
      { pre_body_id: 16128, pre_node_index: 16, pre_neuron_type: "LC4", pre_source_side: "R", post_body_id: 10001, post_node_index: 0, post_neuron_type: "DNp01", post_source_side: "R", structural_weight: 65 },
    ],
    aggregates: { edge_count: 4, total_structural_weight: 150, structural_weight_by_source_type: { LC4: 127, LPLC2: 23 } },
  };
}

test("validated experiment, six-body morphology, and four-edge source projection compose", () => {
  const experiment = summary();
  const persisted = timeline();
  const bodies = STRUCTURAL_CONNECTIVITY_BODY_IDS.map((bodyId) => morphologyBody(bodyId));
  const artifact = morphology(bodies);
  const structure = connectivity();
  const before = structuredClone({ experiment, persisted, artifact, bodies, structure });
  validateCockpitExperiment(experiment, persisted);
  validateCockpitMorphology(experiment, artifact, bodies);
  validateCockpitConnectivity(experiment, artifact, structure);
  assert.deepEqual(structure.edges.map((edge) => [edge.pre_body_id, edge.post_body_id, edge.structural_weight]), [
    [11498, 10010, 2], [12032, 10010, 62], [14465, 10001, 21], [16128, 10001, 65],
  ]);
  assert.deepEqual({ experiment, persisted, artifact, bodies, structure }, before);
});

test("cockpit refuses unrelated experiment, morphology, body mapping, and circuit provenance", () => {
  const experiment = summary();
  const persisted = timeline();
  const bodies = STRUCTURAL_CONNECTIVITY_BODY_IDS.map((bodyId) => morphologyBody(bodyId));
  const artifact = morphology(bodies);
  const structure = connectivity();
  const mismatchedExperiment = structuredClone(experiment);
  mismatchedExperiment.source.circuit_integrity[0][1] = "f".repeat(64);
  assert.throws(() => validateCockpitExperiment(mismatchedExperiment, persisted), /pinned cockpit circuit/);
  const mismatchedTimeline = structuredClone(persisted);
  mismatchedTimeline.artifact_id = "f".repeat(64);
  assert.throws(() => validateCockpitExperiment(experiment, mismatchedTimeline), /pinned cockpit circuit/);
  const unrelatedMorphology = structuredClone(artifact);
  unrelatedMorphology.artifact_id = "f".repeat(64);
  assert.throws(() => validateCockpitMorphology(experiment, unrelatedMorphology, bodies), /validated six-body/);
  const wrongBody = structuredClone(bodies);
  wrongBody[0].source_side = "L";
  assert.throws(() => validateCockpitMorphology(experiment, artifact, wrongBody), /body identity/);
  const wrongSource = structuredClone(bodies);
  wrongSource[0].morphology_source = "JANELIA_NEUPRINT_MALECNS_SKELETON";
  assert.throws(() => validateCockpitMorphology(experiment, artifact, wrongSource), /body identity/);
  const unrelatedConnectivity = structuredClone(structure);
  unrelatedConnectivity.source_contract.integrity.sha256_by_file[0].sha256 = "f".repeat(64);
  assert.throws(() => validateCockpitConnectivity(experiment, artifact, unrelatedConnectivity), /structural projection/);
});

test("one playback time coordinates world, telemetry, selected DNp01, and event position", () => {
  const persisted = timeline();
  const before = structuredClone(persisted);
  const structure = connectivity();
  const events = deriveCockpitEvents(persisted, structure.fixed_sample.bodies);
  assert.deepEqual(events.map((event) => [event.kind, event.bodyId, event.nodeIndex, event.timeMs]), [
    ["start", null, null, 0], ["dnp01_spike", 10010, 1, 1], ["dnp01_spike", 10001, 0, 2],
    ["dnp01_spike", 10010, 1, 3], ["end", null, null, 3],
  ]);
  const worldAtOne = deriveSceneState(persisted, 1.75);
  const frameAtOne = deriveCockpitFrame(persisted, worldAtOne);
  const activityAtOne = deriveActivityStructureProjection(summary(), persisted, structure, worldAtOne);
  assert.equal(frameAtOne.playbackTimeMs, worldAtOne.playbackTimeMs);
  assert.equal(frameAtOne.thetaRad, worldAtOne.thetaRad);
  assert.equal(frameAtOne.lc4DriveMveq, persisted.lc4_drive_mveq[1]);
  assert.equal(frameAtOne.lplc2DriveMveq, persisted.lplc2_drive_mveq[1]);
  assert.equal(frameAtOne.cursorFraction, 1.75 / 3);
  assert.equal(activityAtOne.bodySpecificStates?.[10010].membraneMv, persisted.selected_body_telemetry[1].membrane_mv[1]);
  assert.equal(activityAtOne.bodySpecificStates?.[10010].spikeAtBoundary, true);
  assert.equal(activityAtOne.bodySpecificStates?.[10010].nodeIndex, 1);
  assert.equal(cockpitEventPosition(events[1], frameAtOne), "current");
  assert.equal(cockpitEventPosition(events[2], frameAtOne), "future");

  const seeked = seekPlayback(createPlaybackClock(0), 2.25, 0, 3);
  const worldAtTwo = deriveSceneState(persisted, seeked.currentTimeMs);
  const frameAtTwo = deriveCockpitFrame(persisted, worldAtTwo);
  const activityAtTwo = deriveActivityStructureProjection(summary(), persisted, structure, worldAtTwo);
  assert.equal(frameAtTwo.playbackTimeMs, 2.25);
  assert.equal(frameAtTwo.thetaRad, persisted.theta_rad[2]);
  assert.equal(activityAtTwo.bodySpecificStates?.[10001].membraneMv, persisted.selected_body_telemetry[0].membrane_mv[2]);
  assert.equal(cockpitEventPosition(events[2], frameAtTwo), "current");
  assert.equal(cockpitEventPosition(events[1], frameAtTwo), "past");
  assert.deepEqual(persisted, before);
});

test("activity projection preserves type-level sensory granularity and exact DNp01 identities", () => {
  const experiment = summary();
  const persisted = timeline();
  const structure = connectivity();
  const bodies = STRUCTURAL_CONNECTIVITY_BODY_IDS.map((bodyId) => morphologyBody(bodyId));
  const scene = deriveSceneState(persisted, 1.5);
  const projection = deriveActivityStructureProjection(experiment, persisted, structure, scene);

  assert.deepEqual(projection.typeLevelDrives?.map(({ neuronType, sourceField, valueMveq }) => [neuronType, sourceField, valueMveq]), [
    ["LC4", "lc4_drive_mveq", 2],
    ["LPLC2", "lplc2_drive_mveq", 5],
  ]);
  const lc4Context = activityContextForBody(projection, morphologyBody(12032));
  const lplc2Context = activityContextForBody(projection, morphologyBody(11498));
  assert.equal(lc4Context.granularity, "TYPE_LEVEL");
  assert.equal(lplc2Context.granularity, "TYPE_LEVEL");
  if (lc4Context.granularity === "TYPE_LEVEL") assert.equal("bodyId" in lc4Context.signal, false);
  if (lplc2Context.granularity === "TYPE_LEVEL") assert.equal("bodyId" in lplc2Context.signal, false);

  assert.deepEqual(Object.keys(projection.bodySpecificStates ?? {}).sort(), ["10001", "10010"]);
  assert.deepEqual(
    [projection.bodySpecificStates?.[10001].nodeIndex, projection.bodySpecificStates?.[10001].sourceSide],
    [0, "R"],
  );
  assert.deepEqual(
    [projection.bodySpecificStates?.[10010].nodeIndex, projection.bodySpecificStates?.[10010].sourceSide],
    [1, "L"],
  );
  const reorderedContract = structuredClone(structure);
  reorderedContract.fixed_sample.bodies.reverse();
  const reorderedProjection = deriveActivityStructureProjection(experiment, persisted, reorderedContract, scene);
  assert.deepEqual(reorderedProjection.bodySpecificStates, projection.bodySpecificStates);
  const mapped = bodySpecificActivityByMorphologyIdentity(projection, bodies);
  assert.deepEqual(Object.keys(mapped).sort(), ["10001", "10010"]);
  assert.equal(mapped[12032], undefined);
  assert.equal(mapped[16128], undefined);
  assert.equal(mapped[11498], undefined);
  assert.equal(mapped[14465], undefined);
  const sameIdentityDifferentCoordinates = morphologyBody(10010);
  sameIdentityDifferentCoordinates.components[0].nodes[0].x = 999_999;
  assert.deepEqual(
    activityContextForBody(projection, sameIdentityDifferentCoordinates),
    activityContextForBody(projection, morphologyBody(10010)),
  );
});

test("activity mapping fails closed for unknown encoder granularity or mismatched CircuitContract identity", () => {
  const persisted = timeline();
  const structure = connectivity();
  const scene = deriveSceneState(persisted, 1);
  const unknownEncoder = structuredClone(summary());
  unknownEncoder.encoder.population_policy = "unverified_population_policy";
  const unknownProjection = deriveActivityStructureProjection(unknownEncoder, persisted, structure, scene);
  assert.equal(unknownProjection.typeLevelDrives, null);
  assert.equal(activityContextForBody(unknownProjection, morphologyBody(12032)).granularity, "UNAVAILABLE");
  assert.notEqual(unknownProjection.bodySpecificStates, null);

  const mismatchedContract = structuredClone(structure);
  const rightDnp = mismatchedContract.fixed_sample.bodies.find((body) => body.body_id === 10001);
  assert.ok(rightDnp);
  (rightDnp as { node_index: number }).node_index = 1;
  const mismatchedProjection = deriveActivityStructureProjection(summary(), persisted, mismatchedContract, scene);
  assert.equal(mismatchedProjection.bodySpecificStates, null);
  assert.notEqual(mismatchedProjection.typeLevelDrives, null);
  assert.equal(activityContextForBody(mismatchedProjection, morphologyBody(10001)).granularity, "UNAVAILABLE");
});

test("membrane presentation uses only persisted LIF references and clamps without mutating source values", () => {
  const persisted = timeline();
  const before = structuredClone(persisted);
  const right = persisted.selected_body_telemetry.find((body) => body.body_id === 10001);
  const left = persisted.selected_body_telemetry.find((body) => body.body_id === 10010);
  assert.ok(right && left);
  (right.membrane_mv as number[]).splice(0, 4, -52, -48.5, -45, -55);
  (left.membrane_mv as number[]).splice(0, 4, -53, -45, -42, -50);
  const editedSourceBeforeProjection = structuredClone(persisted);
  const structure = connectivity();
  const model = summary();
  const atRest = deriveActivityStructureProjection(model, persisted, structure, deriveSceneState(persisted, 0));
  const intermediate = deriveActivityStructureProjection(model, persisted, structure, deriveSceneState(persisted, 1));
  const atThreshold = deriveActivityStructureProjection(model, persisted, structure, deriveSceneState(persisted, 2));
  const belowRest = deriveActivityStructureProjection(model, persisted, structure, deriveSceneState(persisted, 3));
  assert.equal(atRest.bodySpecificStates?.[10001].normalizedModelMembranePosition, 0);
  assert.equal(intermediate.bodySpecificStates?.[10001].normalizedModelMembranePosition, 0.5);
  assert.equal(intermediate.bodySpecificStates?.[10010].normalizedModelMembranePosition, 1);
  assert.equal(atThreshold.bodySpecificStates?.[10001].normalizedModelMembranePosition, 1);
  assert.equal(atThreshold.bodySpecificStates?.[10010].normalizedModelMembranePosition, 1);
  assert.equal(belowRest.bodySpecificStates?.[10001].normalizedModelMembranePosition, 0);
  assert.equal(intermediate.bodySpecificStates?.[10001].membraneMv, -48.5);
  assert.deepEqual(persisted, editedSourceBeforeProjection);
  assert.deepEqual(before.selected_body_telemetry[0].membrane_mv, [-65, -61, -55, -51]);

  const unknownModel = structuredClone(model);
  unknownModel.neural_model.version = "unknown_lif_version";
  const unnormalized = deriveActivityStructureProjection(unknownModel, persisted, structure, deriveSceneState(persisted, 1));
  assert.equal(unnormalized.bodySpecificStates?.[10001].membraneMv, -48.5);
  assert.equal(unnormalized.bodySpecificStates?.[10001].normalizedModelMembranePosition, null);
  assert.equal(unnormalized.bodySpecificStates?.[10010].spikeAtBoundary, true);
});

test("persisted spike event, body-specific state, and selected-body identity agree at stored boundaries", () => {
  const persisted = timeline();
  const structure = connectivity();
  const events = deriveCockpitEvents(persisted, structure.fixed_sample.bodies);
  const scene = deriveSceneState(persisted, 1.75);
  const projection = deriveActivityStructureProjection(summary(), persisted, structure, scene);
  const spikeEvent = events.find((event) => event.kind === "dnp01_spike" && event.timeMs === 1);
  assert.deepEqual([spikeEvent?.bodyId, spikeEvent?.nodeIndex], [10010, 1]);
  assert.equal(projection.boundaryTimeMs, spikeEvent?.timeMs);
  assert.deepEqual(
    [projection.bodySpecificStates?.[10010].spikeAtBoundary, projection.bodySpecificStates?.[10010].spikeTimestampMs],
    [true, 1],
  );
  assert.equal(projection.bodySpecificStates?.[10001].spikeAtBoundary, false);
  assert.equal(cockpitEventPosition(spikeEvent!, deriveCockpitFrame(persisted, scene)), "current");

  const atEnd = deriveActivityStructureProjection(summary(), persisted, structure, deriveSceneState(persisted, 3));
  assert.equal(atEnd.boundaryTimeMs, 3);
  assert.equal(atEnd.bodySpecificStates?.[10001].spikeAtBoundary, false);
  assert.equal(atEnd.bodySpecificStates?.[10010].spikeAtBoundary, true);
});

test("visual bodies have no invented individual trace and cockpit source text stays bounded", () => {
  const persisted = timeline();
  const scene = deriveSceneState(persisted, 1);
  const activity = deriveActivityStructureProjection(summary(), persisted, connectivity(), scene);
  assert.equal(activityContextForBody(activity, morphologyBody(12032)).granularity, "TYPE_LEVEL");
  assert.equal(activityContextForBody(activity, morphologyBody(11498)).granularity, "TYPE_LEVEL");
  const source = ["ScientificCockpit.tsx", "CockpitPanels.tsx", "CockpitTelemetry.tsx"]
    .map((file) => readFileSync(new URL(`../src/components/${file}`, import.meta.url), "utf8"))
    .join("\n");
  assert.doesNotMatch(source, /\buseFrame\s*\(|\bExperimentRunner\b|<FlyVisualAsset\b|\breward\b|\bpolicy\b|\breinforcement learning\b|\bconsciousness\b|\bsentience\b/i);
  assert.match(source, /No body-specific dynamic trace in this artifact/);
  assert.match(source, /structural weight/);
  assert.match(source, /PlaybackCanvas/);
  const morphologyInspector = readFileSync(new URL("../src/components/MorphologyInspector.tsx", import.meta.url), "utf8");
  assert.match(morphologyInspector, /compact && activity/);
  assert.match(morphologyInspector, /showSimulatedState && activityState && normalizedPosition !== null/);
  assert.match(morphologyInspector, /normalizedModelMembranePosition/);
  assert.match(morphologyInspector, /const SourceSkeletonLines = memo/);
  assert.match(morphologyInspector, /const SimulatedBodyStateLines = memo/);
  assert.match(morphologyInspector, /\[components\]/);
  assert.doesNotMatch(morphologyInspector, /activation\s*%|firing probability|signal propagation|local membrane voltage/i);
  assert.match(morphologyInspector, /linewidth=\{1\}/);
  assert.doesNotMatch(morphologyInspector, /node\.radius.*linewidth|structural_weight.*opacity/i);
  const structuralRenderer = morphologyInspector.slice(
    morphologyInspector.indexOf("const StructuralConnectivityLines"),
    morphologyInspector.indexOf("function MorphologyScene"),
  );
  assert.match(structuralRenderer, /linewidth=\{1\}/);
  assert.doesNotMatch(structuralRenderer, /activity|structural_weight/i);
});

test("panel focus is reversible presentation state and keeps scientific sources untouched", () => {
  const experiment = summary();
  const persisted = timeline();
  const bodies = STRUCTURAL_CONNECTIVITY_BODY_IDS.map((bodyId) => morphologyBody(bodyId));
  const structure = connectivity();
  const before = structuredClone({ experiment, persisted, bodies, structure });
  const frame = deriveCockpitFrame(persisted, deriveSceneState(persisted, 1.75));
  let focus: CockpitFocusState = null;
  focus = toggleCockpitFocus(focus, "world");
  assert.equal(focus, "world");
  focus = toggleCockpitFocus(focus, "connectome");
  assert.equal(focus, "connectome");
  focus = toggleCockpitFocus(focus, "telemetry");
  assert.equal(focus, "telemetry");
  focus = toggleCockpitFocus(focus, "telemetry");
  assert.equal(focus, null);
  assert.equal(frame.playbackTimeMs, 1.75);
  assert.deepEqual({ experiment, persisted, bodies, structure }, before);
});

test("cockpit keeps one transport and scopes layout styling away from standalone pages", () => {
  const cockpit = readFileSync(new URL("../src/components/ScientificCockpit.tsx", import.meta.url), "utf8");
  const panels = readFileSync(new URL("../src/components/CockpitPanels.tsx", import.meta.url), "utf8");
  const telemetry = readFileSync(new URL("../src/components/CockpitTelemetry.tsx", import.meta.url), "utf8");
  const css = readFileSync(new URL("../src/app/cockpit.css", import.meta.url), "utf8");
  assert.equal(cockpit.match(/useExperimentPlayback\(timeline\)/g)?.length, 1);
  assert.equal(cockpit.match(/Canonical experiment playback controls/g)?.length, 1);
  assert.match(cockpit, /data-focus=\{focusedPanel \?\? "none"\}/);
  assert.match(cockpit, /playback\.play/);
  assert.match(cockpit, /playback\.pause/);
  assert.match(cockpit, /playback\.reset/);
  assert.match(cockpit, /playback\.seek/);
  assert.match(cockpit, /playback\.setPlaybackRate/);
  assert.match(panels, /onSeek\(event\.timeMs\)/);
  assert.match(telemetry, /timeline\.theta_rad/);
  assert.match(telemetry, /timeline\.lc4_drive_mveq/);
  assert.match(telemetry, /timeline\.lplc2_drive_mveq/);
  assert.match(telemetry, /selectedTelemetry\.membrane_mv/);
  assert.match(css, /\.cockpit-shell \.app-header/);
  assert.match(css, /\.cockpit-grid\[data-focus="connectome"\]/);
  assert.doesNotMatch(css, /^\s*\.app-header\s*\{/m);
  assert.doesNotMatch(css, /^\s*\.morphology-inspector\s*\{/m);
});
