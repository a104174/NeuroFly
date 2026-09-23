import type {
  ExperimentSummary,
  ExperimentTimeline,
  MorphologyArtifactSummary,
  MorphologyBody,
  MorphologyBodyId,
  StructuralConnectivityBody,
  StructuralConnectivityProjection,
} from "./neuroflyClient";
import {
  CONNECTIVITY_SOURCE_HASHES,
  STRUCTURAL_CONNECTIVITY_BODY_IDS,
  STRUCTURAL_CONNECTIVITY_PROJECTION_ID,
} from "./neuroflyClient";
import type { ExperimentSceneState } from "./playback";

export const COCKPIT_MORPHOLOGY_ARTIFACT_ID =
  "a3f090d5309d9ede0e9e0f78343a618a4bafba3fea91e5a27d37927d5ec55f79" as const;

const BODY_IDENTITIES: Readonly<Record<MorphologyBodyId, readonly [number, string, "L" | "R"]>> = {
  10001: [0, "DNp01", "R"],
  10010: [1, "DNp01", "L"],
  11498: [2, "LPLC2", "L"],
  12032: [3, "LC4", "L"],
  14465: [12, "LPLC2", "R"],
  16128: [16, "LC4", "R"],
};

export class CockpitCompatibilityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CockpitCompatibilityError";
  }
}

function sameCandidate(
  left: { identifier: string; version: number },
  right: { identifier: string; version: number },
): boolean {
  return left.identifier === right.identifier && left.version === right.version;
}

function sourceHashesMatch(entries: readonly (readonly [string, string])[]): boolean {
  const hashes = new Map(entries);
  return entries.length === 2 && hashes.size === 2 &&
    Object.entries(CONNECTIVITY_SOURCE_HASHES).every(([file, digest]) => hashes.get(file) === digest);
}

export function validateCockpitExperiment(
  summary: ExperimentSummary,
  timeline: ExperimentTimeline,
): void {
  if (summary.artifact_id !== timeline.artifact_id ||
      summary.dataset !== "male-cns:v1.0" ||
      summary.candidate.identifier !== "looming_giant_fiber_v1" ||
      summary.candidate.version !== 1 ||
      summary.source.endpoint !== "https://neuprint.janelia.org" ||
      !sourceHashesMatch(summary.source.circuit_integrity) ||
      summary.graph_scope_id !== "direct_visual_to_dnp01_v1" ||
      summary.dt_ms !== timeline.dt_ms ||
      summary.duration_ms !== timeline.duration_ms ||
      timeline.start_ms !== 0 ||
      timeline.end_ms !== summary.duration_ms ||
      timeline.times_ms[0] !== timeline.start_ms ||
      timeline.times_ms.at(-1) !== timeline.end_ms) {
    throw new CockpitCompatibilityError("This experiment does not match the pinned cockpit circuit and timeline.");
  }
  const expectedDN = new Map<number, "L" | "R">([[10001, "R"], [10010, "L"]]);
  if (summary.duration_ms <= 0 ||
      summary.dnp01.length !== 2 ||
      new Set(summary.dnp01.map((body) => body.body_id)).size !== 2 ||
      summary.dnp01.some((body) =>
    body.neuron_type !== "DNp01" || body.soma_side !== expectedDN.get(body.body_id)
  )) {
    throw new CockpitCompatibilityError("DNp01 summary identities do not match the cockpit sample.");
  }
  for (const body of timeline.selected_body_telemetry) {
    const expectedSide = expectedDN.get(body.body_id as 10001 | 10010);
    if (expectedSide !== undefined &&
        (body.neuron_type !== "DNp01" || body.soma_side !== expectedSide ||
         body.times_ms.length !== timeline.times_ms.length ||
         body.times_ms.some((time, index) => time !== timeline.times_ms[index]) ||
         body.spike_times_ms.some((time) => !timeline.times_ms.includes(time)))) {
      throw new CockpitCompatibilityError("Persisted DNp01 telemetry identity or time grid is incompatible.");
    }
  }
}

export function validateCockpitMorphology(
  summary: ExperimentSummary,
  artifact: MorphologyArtifactSummary,
  bodies: readonly MorphologyBody[],
): void {
  if (artifact.artifact_id !== COCKPIT_MORPHOLOGY_ARTIFACT_ID ||
      artifact.dataset !== summary.dataset ||
      !sameCandidate(artifact.candidate, summary.candidate) ||
      artifact.generation.source_mode !== "OFFICIAL_MALECNS_BULK_SWC" ||
      artifact.morphology_mode !== "RAW" ||
      artifact.body_ids.join(",") !== STRUCTURAL_CONNECTIVITY_BODY_IDS.join(",") ||
      bodies.length !== STRUCTURAL_CONNECTIVITY_BODY_IDS.length) {
    throw new CockpitCompatibilityError("The morphology artifact is not the validated six-body cockpit sample.");
  }
  const summaries = new Map(artifact.bodies.map((body) => [body.body_id, body]));
  const seen = new Set<number>();
  for (const body of bodies) {
    const expected = BODY_IDENTITIES[body.body_id];
    const listed = summaries.get(body.body_id);
    if (!expected || !listed || seen.has(body.body_id) ||
        body.artifact_id !== artifact.artifact_id ||
        body.dataset !== artifact.dataset ||
        !sameCandidate(body.candidate, artifact.candidate) ||
        body.node_index !== expected[0] || body.neuron_type !== expected[1] ||
        body.source_side !== expected[2] || body.source_status !== "Traced" ||
        body.node_index !== listed.node_index || body.node_count !== listed.node_count ||
        body.component_count !== listed.component_count ||
        body.coordinate_frame_id !== artifact.coordinate_frame_id ||
        body.coordinate_unit !== artifact.coordinate_unit || body.morphology_mode !== "RAW" ||
        body.morphology_source !== artifact.generation.source_mode) {
      throw new CockpitCompatibilityError("A morphology body identity differs from the validated sample.");
    }
    seen.add(body.body_id);
  }
}

export function validateCockpitConnectivity(
  summary: ExperimentSummary,
  morphology: MorphologyArtifactSummary,
  connectivity: StructuralConnectivityProjection,
): void {
  const sourceHashes = connectivity.source_contract.integrity.sha256_by_file.map(
    ({ file, sha256 }) => [file, sha256] as const,
  );
  const morphologyById = new Map(morphology.bodies.map((body) => [body.body_id, body]));
  if (connectivity.projection.id !== STRUCTURAL_CONNECTIVITY_PROJECTION_ID ||
      connectivity.fixed_sample.id !== STRUCTURAL_CONNECTIVITY_PROJECTION_ID ||
      connectivity.dataset !== summary.dataset ||
      !sameCandidate(connectivity.candidate, summary.candidate) ||
      !sourceHashesMatch(sourceHashes) ||
      !sourceHashesMatch(summary.source.circuit_integrity) ||
      connectivity.fixed_sample.body_ids.join(",") !== morphology.body_ids.join(",") ||
      connectivity.fixed_sample.bodies.some((body) => {
        const morphologyBody = morphologyById.get(body.body_id);
        return !morphologyBody || body.node_index !== morphologyBody.node_index ||
          body.neuron_type !== morphologyBody.neuron_type || body.source_side !== morphologyBody.source_side;
      })) {
    throw new CockpitCompatibilityError("The structural projection is incompatible with this experiment and morphology sample.");
  }
}

export interface CockpitEvent {
  readonly id: string;
  readonly timeMs: number;
  readonly stepIndex: number;
  readonly kind: "start" | "dnp01_spike" | "end";
  readonly bodyId: 10001 | 10010 | null;
  readonly nodeIndex: 0 | 1 | null;
  readonly label: string;
}

const DNP01_NODE_INDEX: Readonly<Record<10001 | 10010, 0 | 1>> = {
  10001: 0,
  10010: 1,
};

export function deriveCockpitEvents(
  timeline: ExperimentTimeline,
  contractBodies: readonly StructuralConnectivityBody[],
): CockpitEvent[] {
  const identityById = new Map(contractBodies.map((body) => [body.body_id, body]));
  const events: CockpitEvent[] = [
    { id: "start", timeMs: timeline.start_ms, stepIndex: 0, kind: "start", bodyId: null, nodeIndex: null, label: "Experiment boundary: start" },
  ];
  for (const body of timeline.selected_body_telemetry) {
    if (body.body_id !== 10001 && body.body_id !== 10010) continue;
    const identity = identityById.get(body.body_id);
    if (!identity || identity.neuron_type !== "DNp01" ||
        identity.node_index !== DNP01_NODE_INDEX[body.body_id] ||
        identity.source_side !== body.soma_side || body.neuron_type !== "DNp01") continue;
    body.spike_times_ms.forEach((timeMs, index) => {
      const stepIndex = timeline.times_ms.indexOf(timeMs);
      if (stepIndex < 0) {
        throw new CockpitCompatibilityError("A persisted spike does not map to a stored experiment boundary.");
      }
      events.push({
        id: `spike-${body.body_id}-${index}`,
        timeMs,
        stepIndex,
        kind: "dnp01_spike",
        bodyId: body.body_id as 10001 | 10010,
        nodeIndex: identity.node_index as 0 | 1,
        label: `Persisted DNp01 body ${body.body_id} spike`,
      });
    });
  }
  events.push({ id: "end", timeMs: timeline.end_ms, stepIndex: timeline.times_ms.length - 1, kind: "end", bodyId: null, nodeIndex: null, label: "Experiment boundary: end" });
  const rank = { start: 0, dnp01_spike: 1, end: 2 } as const;
  return events.sort((left, right) => left.timeMs - right.timeMs ||
    rank[left.kind] - rank[right.kind] || (left.bodyId ?? 0) - (right.bodyId ?? 0));
}

export interface CockpitFrame {
  readonly playbackTimeMs: number;
  readonly boundaryIndex: number;
  readonly boundaryTimeMs: number;
  readonly intervalStartMs: number;
  readonly cursorFraction: number;
  readonly thetaRad: number;
  readonly lc4DriveMveq: number;
  readonly lplc2DriveMveq: number;
}

export function deriveCockpitFrame(
  timeline: ExperimentTimeline,
  scene: ExperimentSceneState,
): CockpitFrame {
  const duration = timeline.end_ms - timeline.start_ms;
  return {
    playbackTimeMs: scene.playbackTimeMs,
    boundaryIndex: scene.boundaryIndex,
    boundaryTimeMs: scene.boundaryTimeMs,
    intervalStartMs: scene.intervalStartMs,
    cursorFraction: duration === 0 ? 0 : (scene.playbackTimeMs - timeline.start_ms) / duration,
    thetaRad: scene.thetaRad,
    lc4DriveMveq: scene.lc4DriveMveq,
    lplc2DriveMveq: scene.lplc2DriveMveq,
  };
}

export function cockpitEventPosition(
  event: CockpitEvent,
  frame: CockpitFrame,
): "past" | "current" | "future" {
  if (event.stepIndex < frame.boundaryIndex) return "past";
  if (event.stepIndex === frame.boundaryIndex) return "current";
  return "future";
}
