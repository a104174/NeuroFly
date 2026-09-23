import type {
  ExperimentSummary,
  ExperimentTimeline,
  MorphologyBody,
  StructuralConnectivityProjection,
} from "./neuroflyClient";
import { CONNECTIVITY_SOURCE_HASHES, STRUCTURAL_CONNECTIVITY_BODY_IDS, STRUCTURAL_CONNECTIVITY_PROJECTION_ID } from "./neuroflyClient";
import type { ExperimentSceneState } from "./playback";

export type ActivityGranularity = "TYPE_LEVEL" | "BODY_SPECIFIC";
export type ActivityNeuronType = "LC4" | "LPLC2";
export type Dnp01BodyId = 10001 | 10010;

export interface TypeLevelDriveSignal {
  readonly granularity: "TYPE_LEVEL";
  readonly neuronType: ActivityNeuronType;
  readonly sourceField: "lc4_drive_mveq" | "lplc2_drive_mveq";
  readonly valueMveq: number;
  readonly intervalStartMs: number;
  readonly intervalEndMs: number;
}

export interface BodySpecificDnp01State {
  readonly granularity: "BODY_SPECIFIC";
  readonly bodyId: Dnp01BodyId;
  readonly nodeIndex: 0 | 1;
  readonly neuronType: "DNp01";
  readonly sourceSide: "L" | "R";
  readonly boundaryTimeMs: number;
  readonly membraneMv: number;
  readonly normalizedModelMembranePosition: number | null;
  readonly synapticStateMveq: number;
  readonly spikeAtBoundary: boolean;
  readonly spikeTimestampMs: number | null;
}

export interface ActivityStructureProjection {
  readonly artifactId: string;
  readonly playbackTimeMs: number;
  readonly boundaryTimeMs: number;
  readonly intervalStartMs: number;
  readonly typeLevelDrives: readonly [TypeLevelDriveSignal, TypeLevelDriveSignal] | null;
  readonly bodySpecificStates: Readonly<Record<Dnp01BodyId, BodySpecificDnp01State>> | null;
  readonly typeLevelUnavailableReason: string | null;
  readonly bodyStateUnavailableReason: string | null;
}

const DNP01_CONTRACT_IDENTITIES: Readonly<Record<Dnp01BodyId, {
  nodeIndex: 0 | 1;
  side: "L" | "R";
}>> = {
  10001: { nodeIndex: 0, side: "R" },
  10010: { nodeIndex: 1, side: "L" },
};

const TYPE_LEVEL_ENCODER = {
  id: "level_p_instantaneous_bounded_v1",
  version: "phase2e_v1",
  populationPolicy: "bilateral_type_broadcast_v1",
} as const;

const NORMALIZED_LIF_MODEL = {
  id: "lif_filtered_synapse",
  version: "phase2b_v1",
} as const;

function circuitHashesMatch(
  summary: ExperimentSummary,
  connectivity: StructuralConnectivityProjection,
): boolean {
  const expected = new Map<string, string>(Object.entries(CONNECTIVITY_SOURCE_HASHES));
  const experimentHashes = new Map<string, string>(summary.source.circuit_integrity);
  const contractHashes = new Map<string, string>(
    connectivity.source_contract.integrity.sha256_by_file.map(({ file, sha256 }) => [file, sha256]),
  );
  return summary.source.circuit_integrity.length === 2 && experimentHashes.size === 2 &&
    connectivity.source_contract.integrity.sha256_verified &&
    connectivity.source_contract.integrity.record_counts_verified &&
    contractHashes.size === 2 && expected.size === 2 &&
    [...expected].every(([file, digest]) =>
      experimentHashes.get(file) === digest && contractHashes.get(file) === digest,
    );
}

function contractDnp01Bodies(
  summary: ExperimentSummary,
  connectivity: StructuralConnectivityProjection | null,
): Readonly<Record<Dnp01BodyId, { nodeIndex: 0 | 1; side: "L" | "R" }>> | null {
  if (!connectivity ||
      connectivity.fixed_sample.id !== STRUCTURAL_CONNECTIVITY_PROJECTION_ID ||
      connectivity.projection.id !== STRUCTURAL_CONNECTIVITY_PROJECTION_ID ||
      connectivity.dataset !== summary.dataset ||
      connectivity.candidate.identifier !== summary.candidate.identifier ||
      connectivity.candidate.version !== summary.candidate.version ||
      connectivity.fixed_sample.body_ids.join(",") !== STRUCTURAL_CONNECTIVITY_BODY_IDS.join(",") ||
      connectivity.fixed_sample.bodies.length !== STRUCTURAL_CONNECTIVITY_BODY_IDS.length ||
      !circuitHashesMatch(summary, connectivity)) {
    return null;
  }
  const byId = new Map(connectivity.fixed_sample.bodies.map((body) => [body.body_id, body]));
  if (byId.size !== STRUCTURAL_CONNECTIVITY_BODY_IDS.length) return null;
  const identities = {} as Record<Dnp01BodyId, { nodeIndex: 0 | 1; side: "L" | "R" }>;
  for (const bodyId of [10001, 10010] as const) {
    const expected = DNP01_CONTRACT_IDENTITIES[bodyId];
    const body = byId.get(bodyId);
    if (!body || body.node_index !== expected.nodeIndex || body.source_side !== expected.side ||
        body.neuron_type !== "DNp01" || body.source_status !== "Traced") {
      return null;
    }
    identities[bodyId] = { nodeIndex: expected.nodeIndex, side: expected.side };
  }
  return identities;
}

function modelMembranePosition(valueMv: number, summary: ExperimentSummary): number | null {
  const references = summary.neural_model.membrane_state_references;
  if (summary.neural_model.id !== NORMALIZED_LIF_MODEL.id ||
      summary.neural_model.version !== NORMALIZED_LIF_MODEL.version ||
      !Number.isFinite(references.rest_mv) || !Number.isFinite(references.threshold_mv) ||
      references.threshold_mv <= references.rest_mv) {
    return null;
  }
  return Math.min(1, Math.max(0,
    (valueMv - references.rest_mv) / (references.threshold_mv - references.rest_mv),
  ));
}

function deriveTypeLevelDrives(
  summary: ExperimentSummary,
  timeline: ExperimentTimeline,
  scene: ExperimentSceneState,
): { signals: readonly [TypeLevelDriveSignal, TypeLevelDriveSignal] | null; reason: string | null } {
  if (summary.artifact_id !== timeline.artifact_id || summary.dataset !== "male-cns:v1.0" ||
      summary.candidate.identifier !== "looming_giant_fiber_v1" || summary.candidate.version !== 1 ||
      summary.dt_ms !== timeline.dt_ms || summary.duration_ms !== timeline.duration_ms ||
      timeline.end_ms - timeline.start_ms !== timeline.duration_ms) {
    return { signals: null, reason: "Experiment summary and stored interval timeline are incompatible." };
  }
  if (summary.encoder.id !== TYPE_LEVEL_ENCODER.id ||
      summary.encoder.version !== TYPE_LEVEL_ENCODER.version ||
      summary.encoder.population_policy !== TYPE_LEVEL_ENCODER.populationPolicy) {
    return { signals: null, reason: "Encoder granularity is not validated for type-level display." };
  }
  const intervalIndex = scene.intervalIndex;
  if (!Number.isInteger(intervalIndex) || intervalIndex < 0 ||
      intervalIndex >= timeline.step_times_ms.length ||
      timeline.lc4_drive_mveq.length !== timeline.step_times_ms.length ||
      timeline.lplc2_drive_mveq.length !== timeline.step_times_ms.length ||
      timeline.interval_semantics !== "step_values_apply_on_[t_n,t_n+dt)") {
    return { signals: null, reason: "Stored encoder intervals do not match the canonical playback time." };
  }
  const intervalStartMs = timeline.step_times_ms[intervalIndex];
  const intervalEndMs = intervalStartMs + timeline.dt_ms;
  if (!Number.isFinite(intervalStartMs) || scene.intervalStartMs !== intervalStartMs ||
      !Number.isFinite(intervalEndMs) || !Number.isFinite(timeline.lc4_drive_mveq[intervalIndex]) ||
      !Number.isFinite(timeline.lplc2_drive_mveq[intervalIndex])) {
    return { signals: null, reason: "Stored encoder interval values are malformed for the canonical playback time." };
  }
  return {
    signals: [
      {
        granularity: "TYPE_LEVEL",
        neuronType: "LC4",
        sourceField: "lc4_drive_mveq",
        valueMveq: timeline.lc4_drive_mveq[intervalIndex],
        intervalStartMs,
        intervalEndMs,
      },
      {
        granularity: "TYPE_LEVEL",
        neuronType: "LPLC2",
        sourceField: "lplc2_drive_mveq",
        valueMveq: timeline.lplc2_drive_mveq[intervalIndex],
        intervalStartMs,
        intervalEndMs,
      },
    ],
    reason: null,
  };
}

function deriveBodySpecificStates(
  summary: ExperimentSummary,
  timeline: ExperimentTimeline,
  connectivity: StructuralConnectivityProjection | null,
  scene: ExperimentSceneState,
): {
  states: Readonly<Record<Dnp01BodyId, BodySpecificDnp01State>> | null;
  reason: string | null;
} {
  const contractIdentities = contractDnp01Bodies(summary, connectivity);
  if (!contractIdentities) {
    return { states: null, reason: "Validated CircuitContract body identities are unavailable." };
  }
  if (summary.artifact_id !== timeline.artifact_id ||
      summary.dataset !== "male-cns:v1.0" || summary.candidate.identifier !== "looming_giant_fiber_v1" ||
      summary.candidate.version !== 1 || summary.dt_ms !== timeline.dt_ms ||
      summary.duration_ms !== timeline.duration_ms || timeline.end_ms - timeline.start_ms !== timeline.duration_ms ||
      !summary.dnp01.every((item) => item.neuron_type === "DNp01") ||
      summary.dnp01.length !== 2 ||
      new Set(summary.dnp01.map((item) => item.body_id)).size !== 2) {
    return { states: null, reason: "Experiment identity or DNp01 summary mapping is incompatible." };
  }
  const records = timeline.selected_body_telemetry.filter((item) =>
    item.body_id === 10001 || item.body_id === 10010,
  );
  if (records.length !== 2 || new Set(records.map((item) => item.body_id)).size !== 2) {
    return { states: null, reason: "Both persisted DNp01 body records are required." };
  }
  const byId = new Map(records.map((record) => [record.body_id, record]));
  const states = {} as Record<Dnp01BodyId, BodySpecificDnp01State>;
  for (const bodyId of [10001, 10010] as const) {
    const identity = contractIdentities[bodyId];
    const record = byId.get(bodyId);
    const summaryIdentity = summary.dnp01.find((item) => item.body_id === bodyId);
    if (!record || !summaryIdentity || record.neuron_type !== "DNp01" ||
        record.soma_side !== identity.side || summaryIdentity.soma_side !== identity.side ||
        summaryIdentity.neuron_type !== "DNp01" ||
        record.times_ms.length !== timeline.times_ms.length ||
        record.times_ms.some((time, index) => time !== timeline.times_ms[index]) ||
        record.membrane_mv.length !== timeline.times_ms.length ||
        record.synaptic_state_mveq.length !== timeline.times_ms.length ||
        record.spike_times_ms.some((time) => !timeline.times_ms.includes(time))) {
      return { states: null, reason: "Persisted body state does not match its validated CircuitContract identity." };
    }
    if (!Number.isInteger(scene.boundaryIndex) || scene.boundaryIndex < 0 ||
        scene.boundaryIndex >= timeline.times_ms.length ||
        scene.boundaryTimeMs !== timeline.times_ms[scene.boundaryIndex]) {
      return { states: null, reason: "Stored boundary index is outside the experiment timeline." };
    }
    const membraneMv = record.membrane_mv[scene.boundaryIndex];
    const synapticStateMveq = record.synaptic_state_mveq[scene.boundaryIndex];
    const boundaryTimeMs = timeline.times_ms[scene.boundaryIndex];
    const spikeTimestampMs = record.spike_times_ms.find(
      (timeMs) => timeline.times_ms.indexOf(timeMs) === scene.boundaryIndex,
    ) ?? null;
    const spikeAtBoundary = spikeTimestampMs !== null;
    states[bodyId] = {
      granularity: "BODY_SPECIFIC",
      bodyId,
      nodeIndex: identity.nodeIndex,
      neuronType: "DNp01",
      sourceSide: identity.side,
      boundaryTimeMs,
      membraneMv,
      normalizedModelMembranePosition: modelMembranePosition(membraneMv, summary),
      synapticStateMveq,
      spikeAtBoundary,
      spikeTimestampMs,
    };
  }
  return { states, reason: null };
}

export function deriveActivityStructureProjection(
  summary: ExperimentSummary,
  timeline: ExperimentTimeline,
  connectivity: StructuralConnectivityProjection | null,
  scene: ExperimentSceneState,
): ActivityStructureProjection {
  const typeLevel = deriveTypeLevelDrives(summary, timeline, scene);
  const bodySpecific = deriveBodySpecificStates(summary, timeline, connectivity, scene);
  const intervalStartMs = timeline.step_times_ms[scene.intervalIndex] ?? timeline.end_ms;
  return {
    artifactId: summary.artifact_id,
    playbackTimeMs: scene.playbackTimeMs,
    boundaryTimeMs: scene.boundaryTimeMs,
    intervalStartMs,
    typeLevelDrives: typeLevel.signals,
    bodySpecificStates: bodySpecific.states,
    typeLevelUnavailableReason: typeLevel.reason,
    bodyStateUnavailableReason: bodySpecific.reason,
  };
}

export type SelectedActivityContext =
  | { readonly granularity: "BODY_SPECIFIC"; readonly state: BodySpecificDnp01State }
  | { readonly granularity: "TYPE_LEVEL"; readonly signal: TypeLevelDriveSignal }
  | { readonly granularity: "UNAVAILABLE"; readonly reason: string };

export function activityContextForBody(
  projection: ActivityStructureProjection,
  body: Pick<MorphologyBody, "body_id" | "node_index" | "neuron_type" | "source_side">,
): SelectedActivityContext {
  if (body.neuron_type === "DNp01" && (body.body_id === 10001 || body.body_id === 10010)) {
    const state = projection.bodySpecificStates?.[body.body_id];
    if (state && state.nodeIndex === body.node_index && state.sourceSide === body.source_side) {
      return { granularity: "BODY_SPECIFIC", state };
    }
    return {
      granularity: "UNAVAILABLE",
      reason: projection.bodyStateUnavailableReason ?? "Selected body identity does not match the validated activity mapping.",
    };
  }
  if (body.neuron_type === "LC4" || body.neuron_type === "LPLC2") {
    const signal = projection.typeLevelDrives?.find((item) => item.neuronType === body.neuron_type);
    if (signal) return { granularity: "TYPE_LEVEL", signal };
  }
  return {
    granularity: "UNAVAILABLE",
    reason: projection.typeLevelUnavailableReason ?? "No dynamic state is available at this source identity's granularity.",
  };
}

export function bodySpecificActivityByMorphologyIdentity(
  projection: ActivityStructureProjection,
  bodies: readonly MorphologyBody[],
): Partial<Record<MorphologyBody["body_id"], BodySpecificDnp01State>> {
  const states: Partial<Record<MorphologyBody["body_id"], BodySpecificDnp01State>> = {};
  for (const body of bodies) {
    const context = activityContextForBody(projection, body);
    if (context.granularity === "BODY_SPECIFIC") states[body.body_id] = context.state;
  }
  return states;
}
