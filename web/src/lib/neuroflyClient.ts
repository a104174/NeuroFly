const HTTP_SCHEMA = "experiment_http_v1" as const;
const APPLICATION_SCHEMA = "experiment_api_v1" as const;
const ERROR_SCHEMA = "experiment_http_error_v1" as const;
const VALIDATION_STATUS = "NOT_EVALUATED" as const;
const MORPHOLOGY_SCHEMA = "morphology_api_v1" as const;
const CONNECTIVITY_SCHEMA = "malecns_structural_connectivity_v1" as const;
const CONNECTIVITY_SOURCE_METADATA = {
  source: "Janelia neuPrint / MaleCNS",
  endpoint: "https://neuprint.janelia.org",
  dataset: "male-cns:v1.0",
  acquired_at_utc: "2026-09-10T20:39:56.889520+00:00",
  neuprint_python_version: "0.6.3",
  structural_weight_source: "neuPrint ConnectsTo.weight",
  structural_weight_is_physiological_coupling: false,
} as const;
export const CONNECTIVITY_SOURCE_HASHES = {
  "neurons.jsonl": "00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e",
  "connections.jsonl": "f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a",
} as const;
const EXPECTED_STRUCTURAL_EDGES = [
  [11498, 10010, 2],
  [12032, 10010, 62],
  [14465, 10001, 21],
  [16128, 10001, 65],
] as const;
export const STRUCTURAL_CONNECTIVITY_PROJECTION_ID =
  "phase5i_six_body_visual_to_dnp01_v1" as const;
export const STRUCTURAL_CONNECTIVITY_BODY_IDS = [
  10001, 10010, 11498, 12032, 14465, 16128,
] as const;
export type StructuralConnectivityBodyId =
  (typeof STRUCTURAL_CONNECTIVITY_BODY_IDS)[number];
const MORPHOLOGY_SOURCE_NEUPRINT = "JANELIA_NEUPRINT_MALECNS_SKELETON" as const;
const MORPHOLOGY_SOURCE_BULK = "OFFICIAL_MALECNS_BULK_SWC" as const;
const MORPHOLOGY_RETRIEVAL_NEUPRINT = "fetch_skeleton(heal=False, format=swc)" as const;
const MORPHOLOGY_RETRIEVAL_BULK =
  "official_malecns_bulk_swc(raw, heal=False, smoothing=False, repair=False)" as const;
const OFFICIAL_BULK_SWC_URLS = {
  "10001":
    "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/10001.swc",
  "10010":
    "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/10010.swc",
  "11498":
    "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/11498.swc",
  "12032":
    "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/12032.swc",
  "14465":
    "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/14465.swc",
  "16128":
    "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/16128.swc",
} as const;

const MORPHOLOGY_BODY_PROVENANCE = {
  10001: { nodeIndex: 0, neuronType: "DNp01", side: "R" },
  10010: { nodeIndex: 1, neuronType: "DNp01", side: "L" },
  11498: { nodeIndex: 2, neuronType: "LPLC2", side: "L" },
  12032: { nodeIndex: 3, neuronType: "LC4", side: "L" },
  14465: { nodeIndex: 12, neuronType: "LPLC2", side: "R" },
  16128: { nodeIndex: 16, neuronType: "LC4", side: "R" },
} as const;
const PHASE5F_BODY_IDS = [10001, 10010] as const;
const PHASE5G_BODY_IDS = [10001, 10010, 11498, 12032, 14465, 16128] as const;

export type MorphologySource =
  | typeof MORPHOLOGY_SOURCE_NEUPRINT
  | typeof MORPHOLOGY_SOURCE_BULK;
export type MorphologySourceUrls = Record<string, string>;

export type MorphologyBodyId = keyof typeof MORPHOLOGY_BODY_PROVENANCE;
export type MorphologyNeuronType = "LC4" | "LPLC2" | "DNp01";

export interface MorphologyBounds {
  minimum: [number, number, number];
  maximum: [number, number, number];
}

export interface MorphologyBodySummary {
  body_id: MorphologyBodyId;
  node_index: number;
  neuron_type: MorphologyNeuronType;
  source_side: "R" | "L";
  source_status: string | null;
  morphology_mode: "RAW";
  node_count: number;
  link_count: number;
  component_count: number;
  source_bounds: MorphologyBounds;
  source_swc_sha256: string;
  spatial_record_id: string;
}

export interface MorphologyArtifactSummary {
  schema: typeof MORPHOLOGY_SCHEMA;
  kind: "morphology_artifact_summary";
  artifact_id: string;
  artifact_schema_version: "malecns_morphology_artifact_v1";
  dataset: "male-cns:v1.0";
  candidate: { identifier: string; version: number };
  coordinate_frame_id: "male_cns_v1_em_native_voxels";
  coordinate_unit: "8_nm_voxel";
  morphology_mode: "RAW";
  body_ids: MorphologyBodyId[];
  bodies: MorphologyBodySummary[];
  generation: {
    generated_at_utc: string;
    neuprint_python_version: string;
    source_endpoint: string;
    source_mode: MorphologySource;
    source_urls: MorphologySourceUrls;
    retrieval:
      | typeof MORPHOLOGY_RETRIEVAL_NEUPRINT
      | typeof MORPHOLOGY_RETRIEVAL_BULK;
  };
}

export interface MorphologyNode {
  node_id: number;
  x: number;
  y: number;
  z: number;
  radius: number | null;
}

export interface MorphologyLink {
  child_node_id: number;
  parent_node_id: number;
  provenance: "MALECNS_RAW_SKELETON_LINK";
}

export interface MorphologyComponent {
  component_id: number;
  nodes: MorphologyNode[];
  links: MorphologyLink[];
}

export interface MorphologyBody extends MorphologyBodySummary {
  schema: typeof MORPHOLOGY_SCHEMA;
  kind: "morphology_body";
  artifact_id: string;
  artifact_schema_version: "malecns_morphology_artifact_v1";
  dataset: "male-cns:v1.0";
  candidate: { identifier: string; version: number };
  source_category: "MALECNS_DIRECT_DATA";
  morphology_source: MorphologySource;
  coordinate_frame_id: "male_cns_v1_em_native_voxels";
  coordinate_unit: "8_nm_voxel";
  soma_location: { x: number; y: number; z: number } | null;
  components: MorphologyComponent[];
}

export interface StructuralConnectivityBody {
  body_id: StructuralConnectivityBodyId;
  node_index: number;
  neuron_type: MorphologyNeuronType;
  source_side: "L" | "R";
  source_status: string;
}

export interface StructuralConnectivityEdge {
  pre_body_id: StructuralConnectivityBodyId;
  pre_node_index: number;
  pre_neuron_type: "LC4" | "LPLC2";
  pre_source_side: "L" | "R";
  post_body_id: StructuralConnectivityBodyId;
  post_node_index: number;
  post_neuron_type: "DNp01";
  post_source_side: "L" | "R";
  structural_weight: number;
}

export interface StructuralConnectivityProjection {
  schema: typeof CONNECTIVITY_SCHEMA;
  kind: "bounded_structural_connectivity";
  dataset: "male-cns:v1.0";
  candidate: { identifier: "looming_giant_fiber_v1"; version: 1 };
  source_contract: {
    source: string;
    endpoint: "https://neuprint.janelia.org";
    dataset: "male-cns:v1.0";
    acquired_at_utc: string;
    neuprint_python_version: string;
    integrity: {
      sha256_verified: true;
      record_counts_verified: true;
      sha256_by_file: { file: "neurons.jsonl" | "connections.jsonl"; sha256: string }[];
    };
    structural_weight_source: "neuPrint ConnectsTo.weight";
    structural_weight_is_physiological_coupling: false;
  };
  fixed_sample: {
    id: typeof STRUCTURAL_CONNECTIVITY_PROJECTION_ID;
    body_ids: StructuralConnectivityBodyId[];
    bodies: StructuralConnectivityBody[];
  };
  projection: {
    id: typeof STRUCTURAL_CONNECTIVITY_PROJECTION_ID;
    pre_neuron_types: ["LC4", "LPLC2"];
    post_neuron_type: "DNp01";
    direction: "pre_body_id -> post_body_id";
    canonical_order: "pre_node_index, then post_node_index";
    edge_semantics: string;
  };
  edge_semantics: {
    weight_field: "structural_weight";
    weight_source: "neuPrint ConnectsTo.weight";
    structural_weight_is_physiological_coupling: false;
  };
  edges: StructuralConnectivityEdge[];
  aggregates: {
    edge_count: number;
    total_structural_weight: number;
    structural_weight_by_source_type: { LC4: number; LPLC2: number };
  };
}

export type ValidationStatus = typeof VALIDATION_STATUS;

export interface FreeParameters {
  lc4_gain_mv_eq: number;
  lplc2_gain_mv_eq: number;
  omega_half_rad_per_s: number;
  theta_half_rad: number;
  k_syn_mv_per_contact: number;
}

export interface PopulationSummary {
  neuron_type: "LC4" | "LPLC2";
  body_count: number;
  bodies_that_spike: number;
  total_spike_count: number;
  first_spike_time_ms: number | null;
  peak_normalized_feature: number;
  peak_drive_mveq: number;
}

export interface DNp01Summary {
  body_id: 10001 | 10010;
  neuron_type: string;
  soma_side: string | null;
  total_spike_count: number;
  first_spike_time_ms: number | null;
  peak_membrane_mv: number;
  peak_synaptic_state_mveq: number;
  delivered_event_count: number;
  model_increment_sum_mveq: number;
}

export interface ExperimentSummary {
  schema: typeof APPLICATION_SCHEMA;
  kind: "experiment_summary";
  artifact_id: string;
  experiment_config_id: string;
  experiment_config_sha256: string;
  result_id: string;
  artifact_schema_version: string;
  dataset: string;
  candidate: { identifier: string; version: number };
  source: {
    endpoint: string;
    circuit_integrity: [string, string][];
  };
  graph_scope_id: string;
  encoder: { id: string; version: string; population_policy: string };
  neural_model: {
    id: string;
    version: string;
    membrane_state_references: { rest_mv: number; threshold_mv: number };
  };
  pathway_condition: string;
  duration_ms: number;
  dt_ms: number;
  validation_status: ValidationStatus;
  telemetry_profile: Record<string, unknown>;
  free_parameters: FreeParameters;
  populations: {
    LC4: PopulationSummary;
    LPLC2: PopulationSummary;
  };
  dnp01: [DNp01Summary, DNp01Summary];
}

export interface BodyTelemetry {
  body_id: number;
  neuron_type: string | null;
  soma_side: string | null;
  time_unit: "ms";
  times_ms: number[];
  step_times_ms: number[];
  membrane_unit: "mV";
  membrane_mv: number[];
  synaptic_state_unit: "mV_eq";
  synaptic_state_mveq: number[];
  external_drive_unit: "mV_eq";
  external_drive_mveq: number[];
  incoming_coupling_unit: "mV_eq";
  incoming_coupling_mveq: number[];
  spike_times_ms: number[];
}

export interface ExperimentTimeline {
  schema: typeof APPLICATION_SCHEMA;
  kind: "experiment_timeline";
  artifact_id: string;
  time_unit: "ms";
  dt_ms: number;
  duration_ms: number;
  start_ms: number;
  end_ms: number;
  times_ms: number[];
  step_times_ms: number[];
  interval_semantics: "step_values_apply_on_[t_n,t_n+dt)";
  theta_unit: "rad";
  theta_rad: number[];
  angular_expansion_velocity_unit: "rad/s";
  angular_expansion_velocity_rad_s: number[];
  lc4_normalized_feature: number[];
  lplc2_normalized_feature: number[];
  drive_unit: "mV_eq";
  lc4_drive_mveq: number[];
  lplc2_drive_mveq: number[];
  selected_body_telemetry: BodyTelemetry[];
}

export interface SpikeEvent {
  time_ms: number;
  body_id: number;
  node_index: number;
  neuron_type: string;
  step: number;
}

export interface DeliveredEvent {
  delivery_time_ms: number;
  source_body_id: number;
  target_body_id: number;
  structural_weight: number;
  model_sign: number;
  event_increment_mV_eq: number;
  delivery_step: number;
  source_index: number;
  target_index: number;
}

export interface ComparisonSummary {
  schema: typeof APPLICATION_SCHEMA;
  kind: "comparison_summary";
  comparison_id: string;
  comparison_schema_version: string;
  artifact_a_id: string;
  artifact_b_id: string;
  compatibility_class: string;
  source_model_compatible: boolean;
  configuration_differences: Record<string, unknown>[];
  source_model_differences: Record<string, unknown>[];
  telemetry: Record<string, unknown>;
  pathway: Record<string, unknown>;
  visual_populations: Record<string, unknown>[];
  dnp01: Record<string, unknown>[];
  events: Record<string, unknown>;
  limitations: string[];
  empirical_validation_status: ValidationStatus;
}

export class NeuroflyApiError extends Error {
  readonly code: string;
  readonly status: number | null;

  constructor(code: string, message: string, status: number | null = null) {
    super(message);
    this.name = "NeuroflyApiError";
    this.code = code;
    this.status = status;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function fail(message: string): never {
  throw new NeuroflyApiError("INVALID_RESPONSE", message);
}

function record(value: unknown, label: string): Record<string, unknown> {
  if (!isRecord(value)) {
    return fail(`${label} is not an object`);
  }
  return value;
}

function stringValue(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) {
    return fail(`${label} is not a non-empty string`);
  }
  return value;
}

function finiteNumber(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return fail(`${label} is not a finite number`);
  }
  return value;
}

function integer(value: unknown, label: string): number {
  const result = finiteNumber(value, label);
  if (!Number.isInteger(result)) {
    return fail(`${label} is not an integer`);
  }
  return result;
}

function booleanValue(value: unknown, label: string): boolean {
  if (typeof value !== "boolean") {
    return fail(`${label} is not a boolean`);
  }
  return value;
}

function nullableNumber(value: unknown, label: string): number | null {
  return value === null ? null : finiteNumber(value, label);
}

function numberArray(value: unknown, label: string): number[] {
  if (!Array.isArray(value)) {
    return fail(`${label} is not an array`);
  }
  return value.map((item, index) => finiteNumber(item, `${label}[${index}]`));
}

function stringArray(value: unknown, label: string): string[] {
  if (!Array.isArray(value)) {
    return fail(`${label} is not an array`);
  }
  return value.map((item, index) => stringValue(item, `${label}[${index}]`));
}

function exactKeys(
  item: Record<string, unknown>,
  expected: readonly string[],
  label: string,
): void {
  if (Object.keys(item).sort().join(",") !== [...expected].sort().join(",")) {
    return fail(`${label} has unsupported fields`);
  }
}

function schema(value: Record<string, unknown>, expected: string): void {
  if (value.schema !== expected) {
    throw new NeuroflyApiError(
      "UNSUPPORTED_SCHEMA",
      `The API schema is not supported by this client (${expected}).`,
    );
  }
}

function freeParameters(value: unknown): FreeParameters {
  const item = record(value, "free_parameters");
  return {
    lc4_gain_mv_eq: finiteNumber(item.lc4_gain_mv_eq, "lc4_gain_mv_eq"),
    lplc2_gain_mv_eq: finiteNumber(item.lplc2_gain_mv_eq, "lplc2_gain_mv_eq"),
    omega_half_rad_per_s: finiteNumber(
      item.omega_half_rad_per_s,
      "omega_half_rad_per_s",
    ),
    theta_half_rad: finiteNumber(item.theta_half_rad, "theta_half_rad"),
    k_syn_mv_per_contact: finiteNumber(
      item.k_syn_mv_per_contact,
      "k_syn_mv_per_contact",
    ),
  };
}

function population(value: unknown, expectedType: "LC4" | "LPLC2"): PopulationSummary {
  const item = record(value, expectedType);
  if (item.neuron_type !== expectedType) {
    return fail(`${expectedType} population has an unexpected neuron_type`);
  }
  return {
    neuron_type: expectedType,
    body_count: integer(item.body_count, `${expectedType}.body_count`),
    bodies_that_spike: integer(
      item.bodies_that_spike,
      `${expectedType}.bodies_that_spike`,
    ),
    total_spike_count: integer(
      item.total_spike_count,
      `${expectedType}.total_spike_count`,
    ),
    first_spike_time_ms: nullableNumber(
      item.first_spike_time_ms,
      `${expectedType}.first_spike_time_ms`,
    ),
    peak_normalized_feature: finiteNumber(
      item.peak_normalized_feature,
      `${expectedType}.peak_normalized_feature`,
    ),
    peak_drive_mveq: finiteNumber(
      item.peak_drive_mveq,
      `${expectedType}.peak_drive_mveq`,
    ),
  };
}

function dnp01(value: unknown, label: string): DNp01Summary {
  const item = record(value, label);
  const bodyId = integer(item.body_id, `${label}.body_id`);
  if (bodyId !== 10001 && bodyId !== 10010) {
    return fail(`${label}.body_id is not a supported DNp01 body`);
  }
  return {
    body_id: bodyId,
    neuron_type: stringValue(item.neuron_type, `${label}.neuron_type`),
    soma_side:
      item.soma_side === null
        ? null
        : stringValue(item.soma_side, `${label}.soma_side`),
    total_spike_count: integer(item.total_spike_count, `${label}.total_spike_count`),
    first_spike_time_ms: nullableNumber(
      item.first_spike_time_ms,
      `${label}.first_spike_time_ms`,
    ),
    peak_membrane_mv: finiteNumber(item.peak_membrane_mv, `${label}.peak_membrane_mv`),
    peak_synaptic_state_mveq: finiteNumber(
      item.peak_synaptic_state_mveq,
      `${label}.peak_synaptic_state_mveq`,
    ),
    delivered_event_count: integer(
      item.delivered_event_count,
      `${label}.delivered_event_count`,
    ),
    model_increment_sum_mveq: finiteNumber(
      item.model_increment_sum_mveq,
      `${label}.model_increment_sum_mveq`,
    ),
  };
}

export function parseExperimentSummary(value: unknown): ExperimentSummary {
  const item = record(value, "experiment summary");
  schema(item, APPLICATION_SCHEMA);
  if (item.kind !== "experiment_summary") {
    return fail("response is not an experiment summary");
  }
  if (item.validation_status !== VALIDATION_STATUS) {
    return fail("validation_status is not the registered NOT_EVALUATED value");
  }
  const candidate = record(item.candidate, "candidate");
  const source = record(item.source, "source");
  const encoder = record(item.encoder, "encoder");
  const neuralModel = record(item.neural_model, "neural_model");
  const membraneReferences = record(
    neuralModel.membrane_state_references,
    "neural_model.membrane_state_references",
  );
  const populations = record(item.populations, "populations");
  const dnpValues = item.dnp01;
  if (!Array.isArray(dnpValues) || dnpValues.length !== 2) {
    return fail("dnp01 must contain both DNp01 summaries");
  }
  const dnp = dnpValues.map((entry, index) => dnp01(entry, `dnp01[${index}]`));
  if (new Set(dnp.map((entry) => entry.body_id)).size !== 2) {
    return fail("dnp01 summaries must have distinct body IDs");
  }
  const circuitIntegrity = source.circuit_integrity;
  if (!Array.isArray(circuitIntegrity)) {
    return fail("source.circuit_integrity is not an array");
  }
  const integrity = circuitIntegrity.map((entry, index) => {
    if (!Array.isArray(entry) || entry.length !== 2) {
      return fail(`source.circuit_integrity[${index}] is invalid`);
    }
    return [
      stringValue(entry[0], `source.circuit_integrity[${index}][0]`),
      stringValue(entry[1], `source.circuit_integrity[${index}][1]`),
    ] as [string, string];
  });
  return {
    schema: APPLICATION_SCHEMA,
    kind: "experiment_summary",
    artifact_id: stringValue(item.artifact_id, "artifact_id"),
    experiment_config_id: stringValue(
      item.experiment_config_id,
      "experiment_config_id",
    ),
    experiment_config_sha256: stringValue(
      item.experiment_config_sha256,
      "experiment_config_sha256",
    ),
    result_id: stringValue(item.result_id, "result_id"),
    artifact_schema_version: stringValue(
      item.artifact_schema_version,
      "artifact_schema_version",
    ),
    dataset: stringValue(item.dataset, "dataset"),
    candidate: {
      identifier: stringValue(candidate.identifier, "candidate.identifier"),
      version: integer(candidate.version, "candidate.version"),
    },
    source: {
      endpoint: stringValue(source.endpoint, "source.endpoint"),
      circuit_integrity: integrity,
    },
    graph_scope_id: stringValue(item.graph_scope_id, "graph_scope_id"),
    encoder: {
      id: stringValue(encoder.id, "encoder.id"),
      version: stringValue(encoder.version, "encoder.version"),
      population_policy: stringValue(
        encoder.population_policy,
        "encoder.population_policy",
      ),
    },
    neural_model: {
      id: stringValue(neuralModel.id, "neural_model.id"),
      version: stringValue(neuralModel.version, "neural_model.version"),
      membrane_state_references: {
        rest_mv: finiteNumber(
          membraneReferences.rest_mv,
          "neural_model.membrane_state_references.rest_mv",
        ),
        threshold_mv: finiteNumber(
          membraneReferences.threshold_mv,
          "neural_model.membrane_state_references.threshold_mv",
        ),
      },
    },
    pathway_condition: stringValue(item.pathway_condition, "pathway_condition"),
    duration_ms: finiteNumber(item.duration_ms, "duration_ms"),
    dt_ms: finiteNumber(item.dt_ms, "dt_ms"),
    validation_status: VALIDATION_STATUS,
    telemetry_profile: record(item.telemetry_profile, "telemetry_profile"),
    free_parameters: freeParameters(item.free_parameters),
    populations: {
      LC4: population(populations.LC4, "LC4"),
      LPLC2: population(populations.LPLC2, "LPLC2"),
    },
    dnp01: [dnp[0], dnp[1]],
  };
}

function bodyTelemetry(value: unknown, label: string): BodyTelemetry {
  const item = record(value, label);
  schema(item, APPLICATION_SCHEMA);
  if (item.kind !== "body_telemetry") {
    return fail(`${label} is not body telemetry`);
  }
  const times = numberArray(item.times_ms, `${label}.times_ms`);
  const stepTimes = numberArray(item.step_times_ms, `${label}.step_times_ms`);
  if (times.length !== stepTimes.length + 1) {
    return fail(`${label} has inconsistent state/step time lengths`);
  }
  const membrane = numberArray(item.membrane_mv, `${label}.membrane_mv`);
  const synaptic = numberArray(
    item.synaptic_state_mveq,
    `${label}.synaptic_state_mveq`,
  );
  const external = numberArray(
    item.external_drive_mveq,
    `${label}.external_drive_mveq`,
  );
  const incoming = numberArray(
    item.incoming_coupling_mveq,
    `${label}.incoming_coupling_mveq`,
  );
  if (membrane.length !== times.length || synaptic.length !== times.length) {
    return fail(`${label} has inconsistent state lengths`);
  }
  if (external.length !== stepTimes.length || incoming.length !== stepTimes.length) {
    return fail(`${label} has inconsistent interval lengths`);
  }
  return {
    body_id: integer(item.body_id, `${label}.body_id`),
    neuron_type:
      item.neuron_type === null
        ? null
        : stringValue(item.neuron_type, `${label}.neuron_type`),
    soma_side:
      item.soma_side === null
        ? null
        : stringValue(item.soma_side, `${label}.soma_side`),
    time_unit: item.time_unit === "ms" ? "ms" : fail(`${label}.time_unit is not ms`),
    times_ms: times,
    step_times_ms: stepTimes,
    membrane_unit:
      item.membrane_unit === "mV" ? "mV" : fail(`${label}.membrane_unit is not mV`),
    membrane_mv: membrane,
    synaptic_state_unit:
      item.synaptic_state_unit === "mV_eq"
        ? "mV_eq"
        : fail(`${label}.synaptic_state_unit is not mV_eq`),
    synaptic_state_mveq: synaptic,
    external_drive_unit:
      item.external_drive_unit === "mV_eq"
        ? "mV_eq"
        : fail(`${label}.external_drive_unit is not mV_eq`),
    external_drive_mveq: external,
    incoming_coupling_unit:
      item.incoming_coupling_unit === "mV_eq"
        ? "mV_eq"
        : fail(`${label}.incoming_coupling_unit is not mV_eq`),
    incoming_coupling_mveq: incoming,
    spike_times_ms: numberArray(item.spike_times_ms, `${label}.spike_times_ms`),
  };
}

export function parseExperimentTimeline(value: unknown): ExperimentTimeline {
  const item = record(value, "experiment timeline");
  schema(item, APPLICATION_SCHEMA);
  if (item.kind !== "experiment_timeline") {
    return fail("response is not an experiment timeline");
  }
  const stepTimes = numberArray(item.step_times_ms, "step_times_ms");
  const times = numberArray(item.times_ms, "times_ms");
  if (times.length !== stepTimes.length + 1) {
    return fail("timeline state/step time lengths are inconsistent");
  }
  const stepSeries = {
    angular_expansion_velocity_rad_s: numberArray(
      item.angular_expansion_velocity_rad_s,
      "angular_expansion_velocity_rad_s",
    ),
    lc4_normalized_feature: numberArray(
      item.lc4_normalized_feature,
      "lc4_normalized_feature",
    ),
    lplc2_normalized_feature: numberArray(
      item.lplc2_normalized_feature,
      "lplc2_normalized_feature",
    ),
    lc4_drive_mveq: numberArray(item.lc4_drive_mveq, "lc4_drive_mveq"),
    lplc2_drive_mveq: numberArray(item.lplc2_drive_mveq, "lplc2_drive_mveq"),
  };
  const theta = numberArray(item.theta_rad, "theta_rad");
  if (theta.length !== stepTimes.length) {
    return fail("theta_rad does not match step_times_ms length");
  }
  for (const [label, series] of Object.entries(stepSeries)) {
    if (series.length !== stepTimes.length) {
      return fail(`${label} does not match step_times_ms length`);
    }
  }
  if (item.interval_semantics !== "step_values_apply_on_[t_n,t_n+dt)") {
    return fail("timeline interval semantics are unsupported");
  }
  const bodies = item.selected_body_telemetry;
  if (!Array.isArray(bodies)) {
    return fail("selected_body_telemetry is not an array");
  }
  const parsedBodies = bodies.map((entry, index) =>
    bodyTelemetry(entry, `selected_body_telemetry[${index}]`),
  );
  if (new Set(parsedBodies.map((entry) => entry.body_id)).size !== parsedBodies.length) {
    return fail("selected_body_telemetry contains duplicate body IDs");
  }
  return {
    schema: APPLICATION_SCHEMA,
    kind: "experiment_timeline",
    artifact_id: stringValue(item.artifact_id, "artifact_id"),
    time_unit: item.time_unit === "ms" ? "ms" : fail("timeline time_unit is not ms"),
    dt_ms: finiteNumber(item.dt_ms, "dt_ms"),
    duration_ms: finiteNumber(item.duration_ms, "duration_ms"),
    start_ms: finiteNumber(item.start_ms, "start_ms"),
    end_ms: finiteNumber(item.end_ms, "end_ms"),
    times_ms: times,
    step_times_ms: stepTimes,
    interval_semantics: "step_values_apply_on_[t_n,t_n+dt)",
    theta_unit: item.theta_unit === "rad" ? "rad" : fail("theta_unit is not rad"),
    theta_rad: theta,
    angular_expansion_velocity_unit:
      item.angular_expansion_velocity_unit === "rad/s"
        ? "rad/s"
        : fail("angular_expansion_velocity_unit is not rad/s"),
    angular_expansion_velocity_rad_s:
      stepSeries.angular_expansion_velocity_rad_s,
    lc4_normalized_feature: stepSeries.lc4_normalized_feature,
    lplc2_normalized_feature: stepSeries.lplc2_normalized_feature,
    drive_unit:
      item.drive_unit === "mV_eq" ? "mV_eq" : fail("drive_unit is not mV_eq"),
    lc4_drive_mveq: stepSeries.lc4_drive_mveq,
    lplc2_drive_mveq: stepSeries.lplc2_drive_mveq,
    selected_body_telemetry: parsedBodies,
  };
}

function parseHttpError(value: unknown, status: number): NeuroflyApiError {
  if (isRecord(value) && value.schema === ERROR_SCHEMA) {
    const code = typeof value.code === "string" ? value.code : "HTTP_ERROR";
    const messages: Record<string, string> = {
      artifact_not_found: "The requested experiment was not found.",
      body_telemetry_unavailable: "That body has no persisted telemetry.",
      artifact_integrity_failure: "The experiment artifact failed integrity validation.",
      unsupported_artifact_schema: "The experiment artifact schema is unsupported.",
      connectivity_source_unavailable: "The CircuitContract source is not configured.",
      circuit_contract_not_found: "The local CircuitContract was not found.",
      circuit_contract_invalid: "The local CircuitContract failed integrity validation.",
      connectivity_provenance_mismatch: "The CircuitContract does not match the fixed connectivity projection.",
      unsupported_connectivity_projection: "The requested connectivity projection is unsupported.",
      invalid_time_range: "The requested timeline range is invalid.",
    };
    return new NeuroflyApiError(
      code,
      messages[code] ?? "The NeuroFly API could not complete this request.",
      status,
    );
  }
  return new NeuroflyApiError(
    "HTTP_ERROR",
    "The NeuroFly API returned an unexpected error.",
    status,
  );
}

function apiBaseUrl(): string {
  const configured = process.env.NEUROFLY_API_BASE_URL;
  if (!configured) {
    throw new NeuroflyApiError(
      "CONFIGURATION",
      "NEUROFLY_API_BASE_URL is not configured for this browser application.",
    );
  }
  try {
    const parsed = new URL(configured);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      throw new Error("unsupported protocol");
    }
    return configured.replace(/\/+$/, "");
  } catch {
    throw new NeuroflyApiError(
      "CONFIGURATION",
      "NEUROFLY_API_BASE_URL must be an HTTP or HTTPS URL.",
    );
  }
}

async function requestJson<T>(
  path: string,
  parse: (value: unknown) => T,
  search?: URLSearchParams,
): Promise<T> {
  const suffix = search && search.size > 0 ? `?${search.toString()}` : "";
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}${path}${suffix}`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new NeuroflyApiError(
      "API_UNREACHABLE",
      "The NeuroFly API is unavailable. Check the server connection.",
    );
  }
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new NeuroflyApiError(
      "INVALID_RESPONSE",
      "The NeuroFly API returned invalid JSON.",
      response.status,
    );
  }
  if (!response.ok) {
    throw parseHttpError(payload, response.status);
  }
  return parse(payload);
}

export async function listExperiments(): Promise<ExperimentSummary[]> {
  return requestJson("/api/v1/experiments", (value) => {
    const item = record(value, "experiment list");
    schema(item, HTTP_SCHEMA);
    if (item.kind !== "experiment_list" || !Array.isArray(item.experiments)) {
      return fail("response is not an experiment list");
    }
    return item.experiments.map((entry, index) =>
      parseExperimentSummary(entry),
    );
  });
}

export async function getExperiment(artifactId: string): Promise<ExperimentSummary> {
  return requestJson(
    `/api/v1/experiments/${encodeURIComponent(artifactId)}`,
    parseExperimentSummary,
  );
}

export async function getTimeline(
  artifactId: string,
  range?: { start_ms?: number; end_ms?: number },
): Promise<ExperimentTimeline> {
  const search = new URLSearchParams();
  if (range?.start_ms !== undefined) search.set("start_ms", String(range.start_ms));
  if (range?.end_ms !== undefined) search.set("end_ms", String(range.end_ms));
  return requestJson(
    `/api/v1/experiments/${encodeURIComponent(artifactId)}/timeline`,
    parseExperimentTimeline,
    search,
  );
}

export async function getBodyTelemetry(
  artifactId: string,
  bodyId: number,
): Promise<BodyTelemetry> {
  return requestJson(
    `/api/v1/experiments/${encodeURIComponent(artifactId)}/bodies/${bodyId}`,
    (value) => {
      const telemetry = bodyTelemetry(value, "body telemetry");
      if (telemetry.body_id !== bodyId) {
        return fail("body telemetry identity does not match the request");
      }
      return telemetry;
    },
  );
}

export async function getSpikes(artifactId: string): Promise<SpikeEvent[]> {
  return requestJson(
    `/api/v1/experiments/${encodeURIComponent(artifactId)}/spikes`,
    (value) => {
      const item = record(value, "spike events");
      schema(item, HTTP_SCHEMA);
      if (item.kind !== "spike_events" || !Array.isArray(item.spike_events)) {
        return fail("response is not a spike-event collection");
      }
      return item.spike_events.map((entry, index) => {
        const event = record(entry, `spike_events[${index}]`);
        return {
          time_ms: finiteNumber(event.time_ms, `spike_events[${index}].time_ms`),
          body_id: integer(event.body_id, `spike_events[${index}].body_id`),
          node_index: integer(event.node_index, `spike_events[${index}].node_index`),
          neuron_type: stringValue(
            event.neuron_type,
            `spike_events[${index}].neuron_type`,
          ),
          step: integer(event.step, `spike_events[${index}].step`),
        };
      });
    },
  );
}

export async function getEvents(artifactId: string): Promise<DeliveredEvent[]> {
  return requestJson(
    `/api/v1/experiments/${encodeURIComponent(artifactId)}/events`,
    (value) => {
      const item = record(value, "delivered events");
      schema(item, HTTP_SCHEMA);
      if (
        item.kind !== "delivered_events" ||
        !Array.isArray(item.delivered_events)
      ) {
        return fail("response is not a delivered-event collection");
      }
      return item.delivered_events.map((entry, index) => {
        const event = record(entry, `delivered_events[${index}]`);
        return {
          delivery_time_ms: finiteNumber(
            event.delivery_time_ms,
            `delivered_events[${index}].delivery_time_ms`,
          ),
          source_body_id: integer(
            event.source_body_id,
            `delivered_events[${index}].source_body_id`,
          ),
          target_body_id: integer(
            event.target_body_id,
            `delivered_events[${index}].target_body_id`,
          ),
          structural_weight: integer(
            event.structural_weight,
            `delivered_events[${index}].structural_weight`,
          ),
          model_sign: integer(
            event.model_sign,
            `delivered_events[${index}].model_sign`,
          ),
          event_increment_mV_eq: finiteNumber(
            event.event_increment_mV_eq,
            `delivered_events[${index}].event_increment_mV_eq`,
          ),
          delivery_step: integer(
            event.delivery_step,
            `delivered_events[${index}].delivery_step`,
          ),
          source_index: integer(
            event.source_index,
            `delivered_events[${index}].source_index`,
          ),
          target_index: integer(
            event.target_index,
            `delivered_events[${index}].target_index`,
          ),
        };
      });
    },
  );
}

export async function getComparison(
  artifactA: string,
  artifactB: string,
): Promise<ComparisonSummary> {
  return requestJson(
    "/api/v1/comparisons",
    (value) => {
      const item = record(value, "comparison summary");
      schema(item, APPLICATION_SCHEMA);
      if (item.kind !== "comparison_summary") {
        return fail("response is not a comparison summary");
      }
      if (item.empirical_validation_status !== VALIDATION_STATUS) {
        return fail("comparison validation status is not NOT_EVALUATED");
      }
      return {
        schema: APPLICATION_SCHEMA,
        kind: "comparison_summary",
        comparison_id: stringValue(item.comparison_id, "comparison_id"),
        comparison_schema_version: stringValue(
          item.comparison_schema_version,
          "comparison_schema_version",
        ),
        artifact_a_id: stringValue(item.artifact_a_id, "artifact_a_id"),
        artifact_b_id: stringValue(item.artifact_b_id, "artifact_b_id"),
        compatibility_class: stringValue(
          item.compatibility_class,
          "compatibility_class",
        ),
        source_model_compatible: booleanValue(
          item.source_model_compatible,
          "source_model_compatible",
        ),
        configuration_differences: recordArray(
          item.configuration_differences,
          "configuration_differences",
        ),
        source_model_differences: recordArray(
          item.source_model_differences,
          "source_model_differences",
        ),
        telemetry: record(item.telemetry, "telemetry"),
        pathway: record(item.pathway, "pathway"),
        visual_populations: recordArray(
          item.visual_populations,
          "visual_populations",
        ),
        dnp01: recordArray(item.dnp01, "dnp01"),
        events: record(item.events, "events"),
        limitations: stringArray(item.limitations, "limitations"),
        empirical_validation_status: VALIDATION_STATUS,
      };
    },
    new URLSearchParams({ artifact_a: artifactA, artifact_b: artifactB }),
  );
}

function recordArray(value: unknown, label: string): Record<string, unknown>[] {
  if (!Array.isArray(value)) {
    return fail(`${label} is not an array`);
  }
  return value.map((entry, index) => record(entry, `${label}[${index}]`));
}

function sha256(value: unknown, label: string): string {
  const result = stringValue(value, label);
  if (!/^[0-9a-f]{64}$/.test(result) && !/^sha256:[0-9a-f]{64}$/.test(result)) {
    return fail(`${label} is not a lowercase SHA-256 identity`);
  }
  return result;
}

function morphologyBodyId(value: unknown, label: string): MorphologyBodyId {
  const result = integer(value, label);
  return Object.hasOwn(MORPHOLOGY_BODY_PROVENANCE, result)
    ? (result as MorphologyBodyId)
    : fail(`${label} is outside the audited morphology samples`);
}

function tuple3(value: unknown, label: string): [number, number, number] {
  if (!Array.isArray(value) || value.length !== 3) {
    return fail(`${label} is not a three-coordinate tuple`);
  }
  return [
    finiteNumber(value[0], `${label}[0]`),
    finiteNumber(value[1], `${label}[1]`),
    finiteNumber(value[2], `${label}[2]`),
  ];
}

function morphologyBounds(value: unknown, label: string): MorphologyBounds {
  const item = record(value, label);
  return {
    minimum: tuple3(item.minimum, `${label}.minimum`),
    maximum: tuple3(item.maximum, `${label}.maximum`),
  };
}

function morphologySource(value: unknown, label: string): MorphologySource {
  if (value === MORPHOLOGY_SOURCE_NEUPRINT || value === MORPHOLOGY_SOURCE_BULK) {
    return value;
  }
  return fail(`${label} is an unsupported morphology source`);
}

function morphologySourceUrls(value: unknown, label: string): MorphologySourceUrls {
  const item = record(value, label);
  const result: MorphologySourceUrls = {};
  for (const [bodyId, url] of Object.entries(item)) {
    result[bodyId] = stringValue(url, `${label}.${bodyId}`);
  }
  return result;
}

function morphologySummaryBody(value: unknown, label: string): MorphologyBodySummary {
  const item = record(value, label);
  const bodyId = morphologyBodyId(item.body_id, `${label}.body_id`);
  const expected = MORPHOLOGY_BODY_PROVENANCE[bodyId];
  const nodeIndex = integer(item.node_index, `${label}.node_index`);
  if (nodeIndex !== expected.nodeIndex || item.source_side !== expected.side) {
    return fail(`${label} does not match the fixed body/index/side provenance`);
  }
  if (item.neuron_type !== expected.neuronType || item.morphology_mode !== "RAW") {
    return fail(`${label} is not a supported raw morphology record`);
  }
  return {
    body_id: bodyId,
    node_index: nodeIndex,
    neuron_type: expected.neuronType,
    source_side: expected.side as "R" | "L",
    source_status:
      item.source_status === null
        ? null
        : stringValue(item.source_status, `${label}.source_status`),
    morphology_mode: "RAW",
    node_count: integer(item.node_count, `${label}.node_count`),
    link_count: integer(item.link_count, `${label}.link_count`),
    component_count: integer(item.component_count, `${label}.component_count`),
    source_bounds: morphologyBounds(item.source_bounds, `${label}.source_bounds`),
    source_swc_sha256: sha256(item.source_swc_sha256, `${label}.source_swc_sha256`),
    spatial_record_id: sha256(item.spatial_record_id, `${label}.spatial_record_id`),
  };
}

export function parseMorphologyArtifactSummary(
  value: unknown,
): MorphologyArtifactSummary {
  const item = record(value, "morphology artifact summary");
  schema(item, MORPHOLOGY_SCHEMA);
  if (
    item.kind !== "morphology_artifact_summary" ||
    item.artifact_schema_version !== "malecns_morphology_artifact_v1" ||
    item.dataset !== "male-cns:v1.0" ||
    item.coordinate_frame_id !== "male_cns_v1_em_native_voxels" ||
    item.coordinate_unit !== "8_nm_voxel" ||
    item.morphology_mode !== "RAW"
  ) {
    return fail("morphology artifact contract is unsupported");
  }
  if (!Array.isArray(item.body_ids)) {
    return fail("morphology artifact does not contain the fixed body set");
  }
  const bodyIds = item.body_ids.map((bodyId, index) =>
    morphologyBodyId(bodyId, `body_ids[${index}]`),
  );
  const isPhase5f = bodyIds.join(",") === PHASE5F_BODY_IDS.join(",");
  const isPhase5g = bodyIds.join(",") === PHASE5G_BODY_IDS.join(",");
  if (!isPhase5f && !isPhase5g) {
    return fail("morphology artifact does not contain a supported fixed body set");
  }
  if (!Array.isArray(item.bodies) || item.bodies.length !== bodyIds.length) {
    return fail("morphology body summary count does not match body_ids");
  }
  const bodies = item.bodies.map((body, index) =>
    morphologySummaryBody(body, `bodies[${index}]`),
  );
  if (bodies.some((body, index) => body.body_id !== bodyIds[index])) {
    return fail("morphology body summaries are not canonically ordered");
  }
  const candidate = record(item.candidate, "candidate");
  const generation = record(item.generation, "generation");
  const sourceMode = morphologySource(generation.source_mode, "generation.source_mode");
  const sourceUrls = morphologySourceUrls(generation.source_urls, "generation.source_urls");
  const retrieval = stringValue(generation.retrieval, "generation.retrieval");
  if (
    (sourceMode === MORPHOLOGY_SOURCE_BULK &&
      (retrieval !== MORPHOLOGY_RETRIEVAL_BULK ||
        bodyIds.some(
          (bodyId) =>
            sourceUrls[String(bodyId)] !== OFFICIAL_BULK_SWC_URLS[String(bodyId) as keyof typeof OFFICIAL_BULK_SWC_URLS],
        ) ||
        Object.keys(sourceUrls).length !== bodyIds.length)) ||
    (sourceMode === MORPHOLOGY_SOURCE_NEUPRINT &&
      (retrieval !== MORPHOLOGY_RETRIEVAL_NEUPRINT || Object.keys(sourceUrls).length !== 0))
  ) {
    return fail("morphology retrieval provenance is unsupported or not raw/unhealed");
  }
  return {
    schema: MORPHOLOGY_SCHEMA,
    kind: "morphology_artifact_summary",
    artifact_id: sha256(item.artifact_id, "artifact_id"),
    artifact_schema_version: "malecns_morphology_artifact_v1",
    dataset: "male-cns:v1.0",
    candidate: {
      identifier: stringValue(candidate.identifier, "candidate.identifier"),
      version: integer(candidate.version, "candidate.version"),
    },
    coordinate_frame_id: "male_cns_v1_em_native_voxels",
    coordinate_unit: "8_nm_voxel",
    morphology_mode: "RAW",
    body_ids: bodyIds,
    bodies,
    generation: {
      generated_at_utc: stringValue(generation.generated_at_utc, "generated_at_utc"),
      neuprint_python_version: stringValue(
        generation.neuprint_python_version,
        "neuprint_python_version",
      ),
      source_endpoint: stringValue(generation.source_endpoint, "source_endpoint"),
      source_mode: sourceMode,
      source_urls: sourceUrls,
      retrieval: retrieval as
        | typeof MORPHOLOGY_RETRIEVAL_NEUPRINT
        | typeof MORPHOLOGY_RETRIEVAL_BULK,
    },
  };
}

function morphologyComponent(value: unknown, label: string): MorphologyComponent {
  const item = record(value, label);
  if (!Array.isArray(item.nodes) || !Array.isArray(item.links)) {
    return fail(`${label} nodes and links must be arrays`);
  }
  const nodes = item.nodes.map((value, index) => {
    const node = record(value, `${label}.nodes[${index}]`);
    return {
      node_id: integer(node.node_id, `${label}.nodes[${index}].node_id`),
      x: finiteNumber(node.x, `${label}.nodes[${index}].x`),
      y: finiteNumber(node.y, `${label}.nodes[${index}].y`),
      z: finiteNumber(node.z, `${label}.nodes[${index}].z`),
      radius:
        node.radius === null
          ? null
          : finiteNumber(node.radius, `${label}.nodes[${index}].radius`),
    };
  });
  const nodeIds = new Set(nodes.map((node) => node.node_id));
  const links = item.links.map((value, index) => {
    const link = record(value, `${label}.links[${index}]`);
    const child = integer(link.child_node_id, `${label}.links[${index}].child_node_id`);
    const parent = integer(
      link.parent_node_id,
      `${label}.links[${index}].parent_node_id`,
    );
    if (!nodeIds.has(child) || !nodeIds.has(parent)) {
      return fail(`${label} contains a cross-component or missing-node link`);
    }
    if (link.provenance !== "MALECNS_RAW_SKELETON_LINK") {
      return fail(`${label} contains a non-raw link`);
    }
    return {
      child_node_id: child,
      parent_node_id: parent,
      provenance: "MALECNS_RAW_SKELETON_LINK" as const,
    };
  });
  return {
    component_id: integer(item.component_id, `${label}.component_id`),
    nodes,
    links,
  };
}

export function parseMorphologyBody(value: unknown): MorphologyBody {
  const item = record(value, "morphology body");
  schema(item, MORPHOLOGY_SCHEMA);
  const source = morphologySource(item.morphology_source, "morphology_source");
  if (
    item.kind !== "morphology_body" ||
    item.artifact_schema_version !== "malecns_morphology_artifact_v1" ||
    item.dataset !== "male-cns:v1.0" ||
    item.source_category !== "MALECNS_DIRECT_DATA" ||
    item.coordinate_frame_id !== "male_cns_v1_em_native_voxels" ||
    item.coordinate_unit !== "8_nm_voxel"
  ) {
    return fail("morphology body source contract is unsupported");
  }
  const summary = morphologySummaryBody(item, "morphology body");
  if (!Array.isArray(item.components)) {
    return fail("morphology components are not an array");
  }
  const components = item.components.map((component, index) =>
    morphologyComponent(component, `components[${index}]`),
  );
  if (
    components.length !== summary.component_count ||
    components.reduce((count, component) => count + component.nodes.length, 0) !==
      summary.node_count ||
    components.reduce((count, component) => count + component.links.length, 0) !==
      summary.link_count
  ) {
    return fail("morphology component counts do not match metadata");
  }
  const candidate = record(item.candidate, "candidate");
  const soma = item.soma_location === null ? null : record(item.soma_location, "soma_location");
  return {
    ...summary,
    schema: MORPHOLOGY_SCHEMA,
    kind: "morphology_body",
    artifact_id: sha256(item.artifact_id, "artifact_id"),
    artifact_schema_version: "malecns_morphology_artifact_v1",
    dataset: "male-cns:v1.0",
    candidate: {
      identifier: stringValue(candidate.identifier, "candidate.identifier"),
      version: integer(candidate.version, "candidate.version"),
    },
    source_category: "MALECNS_DIRECT_DATA",
    morphology_source: source,
    coordinate_frame_id: "male_cns_v1_em_native_voxels",
    coordinate_unit: "8_nm_voxel",
    soma_location:
      soma === null
        ? null
        : {
            x: finiteNumber(soma.x, "soma_location.x"),
            y: finiteNumber(soma.y, "soma_location.y"),
            z: finiteNumber(soma.z, "soma_location.z"),
          },
    components,
  };
}

const CONNECTIVITY_BODY_IDENTITIES: Readonly<
  Record<StructuralConnectivityBodyId, readonly [number, MorphologyNeuronType, "L" | "R"]>
> = {
  10001: [0, "DNp01", "R"],
  10010: [1, "DNp01", "L"],
  11498: [2, "LPLC2", "L"],
  12032: [3, "LC4", "L"],
  14465: [12, "LPLC2", "R"],
  16128: [16, "LC4", "R"],
};

export function parseStructuralConnectivity(
  value: unknown,
): StructuralConnectivityProjection {
  const item = record(value, "structural connectivity");
  exactKeys(item, [
    "schema", "kind", "dataset", "candidate", "source_contract", "fixed_sample",
    "projection", "edge_semantics", "edges", "aggregates",
  ], "structural connectivity");
  schema(item, CONNECTIVITY_SCHEMA);
  if (item.kind !== "bounded_structural_connectivity" || item.dataset !== "male-cns:v1.0") {
    return fail("structural connectivity kind or dataset is unsupported");
  }
  const candidate = record(item.candidate, "connectivity.candidate");
  exactKeys(candidate, ["identifier", "version"], "connectivity.candidate");
  if (candidate.identifier !== "looming_giant_fiber_v1" || candidate.version !== 1) {
    return fail("structural connectivity candidate is unsupported");
  }

  const provenance = record(item.source_contract, "connectivity.source_contract");
  exactKeys(provenance, [
    "source", "endpoint", "dataset", "acquired_at_utc", "neuprint_python_version",
    "integrity", "structural_weight_source", "structural_weight_is_physiological_coupling",
  ], "connectivity.source_contract");
  if (Object.entries(CONNECTIVITY_SOURCE_METADATA).some(([key, expected]) => provenance[key] !== expected)) {
    return fail("structural connectivity provenance is unsupported");
  }
  const integrity = record(provenance.integrity, "connectivity.source_contract.integrity");
  exactKeys(integrity, ["sha256_verified", "record_counts_verified", "sha256_by_file"], "connectivity integrity");
  if (integrity.sha256_verified !== true || integrity.record_counts_verified !== true || !Array.isArray(integrity.sha256_by_file)) {
    return fail("CircuitContract integrity is not verified");
  }
  const hashes = integrity.sha256_by_file.map((entry, index) => {
    const hashRecord = record(entry, `connectivity hash ${index}`);
    exactKeys(hashRecord, ["file", "sha256"], `connectivity hash ${index}`);
    if (hashRecord.file !== "neurons.jsonl" && hashRecord.file !== "connections.jsonl") {
      return fail("CircuitContract hash names an unsupported file");
    }
    const digest = stringValue(hashRecord.sha256, `connectivity hash ${index}.sha256`);
    if (!/^[0-9a-f]{64}$/.test(digest)) return fail("CircuitContract hash is malformed");
    return {
      file: hashRecord.file as "neurons.jsonl" | "connections.jsonl",
      sha256: digest,
    };
  });
  if (hashes.length !== 2 || new Set(hashes.map((entry) => entry.file)).size !== 2 ||
      !hashes.some((entry) => entry.file === "neurons.jsonl") ||
      !hashes.some((entry) => entry.file === "connections.jsonl")) {
    return fail("CircuitContract provenance must identify both verified files");
  }
  if (hashes.some((entry) => CONNECTIVITY_SOURCE_HASHES[entry.file] !== entry.sha256)) {
    return fail("CircuitContract source hashes do not match the fixed contract");
  }
  const sourceContract: StructuralConnectivityProjection["source_contract"] = {
    source: CONNECTIVITY_SOURCE_METADATA.source,
    endpoint: CONNECTIVITY_SOURCE_METADATA.endpoint,
    dataset: CONNECTIVITY_SOURCE_METADATA.dataset,
    acquired_at_utc: stringValue(provenance.acquired_at_utc, "connectivity.acquired_at_utc"),
    neuprint_python_version: stringValue(provenance.neuprint_python_version, "connectivity.neuprint_python_version"),
    integrity: {
      sha256_verified: true,
      record_counts_verified: true,
      sha256_by_file: hashes as StructuralConnectivityProjection["source_contract"]["integrity"]["sha256_by_file"],
    },
    structural_weight_source: "neuPrint ConnectsTo.weight",
    structural_weight_is_physiological_coupling: false,
  };

  const sample = record(item.fixed_sample, "connectivity.fixed_sample");
  exactKeys(sample, ["id", "body_ids", "bodies"], "connectivity.fixed_sample");
  if (sample.id !== STRUCTURAL_CONNECTIVITY_PROJECTION_ID || !Array.isArray(sample.body_ids) || !Array.isArray(sample.bodies)) {
    return fail("connectivity fixed sample identity is unsupported");
  }
  const bodyIds = sample.body_ids.map((id, index) => integer(id, `fixed_sample.body_ids[${index}]`));
  if (bodyIds.join(",") !== STRUCTURAL_CONNECTIVITY_BODY_IDS.join(",") || sample.bodies.length !== STRUCTURAL_CONNECTIVITY_BODY_IDS.length) {
    return fail("connectivity fixed body set is unsupported");
  }
  const bodies = sample.bodies.map((entry, index): StructuralConnectivityBody => {
    const body = record(entry, `connectivity.fixed_sample.bodies[${index}]`);
    exactKeys(body, ["body_id", "node_index", "neuron_type", "source_side", "source_status"], `connectivity body ${index}`);
    const bodyId = integer(body.body_id, `connectivity body ${index}.body_id`) as StructuralConnectivityBodyId;
    const expected = CONNECTIVITY_BODY_IDENTITIES[bodyId];
    if (!expected || bodyId !== STRUCTURAL_CONNECTIVITY_BODY_IDS[index] ||
        body.node_index !== expected[0] || body.neuron_type !== expected[1] ||
        body.source_side !== expected[2] || body.source_status !== "Traced") {
      return fail(`connectivity body ${index} identity is unsupported`);
    }
    return { body_id: bodyId, node_index: expected[0], neuron_type: expected[1], source_side: expected[2], source_status: "Traced" };
  });
  const identityById = new Map(bodies.map((body) => [body.body_id, body]));

  const projection = record(item.projection, "connectivity.projection");
  exactKeys(projection, ["id", "pre_neuron_types", "post_neuron_type", "direction", "canonical_order", "edge_semantics"], "connectivity.projection");
  if (projection.id !== STRUCTURAL_CONNECTIVITY_PROJECTION_ID ||
      !Array.isArray(projection.pre_neuron_types) || projection.pre_neuron_types.join(",") !== "LC4,LPLC2" ||
      projection.post_neuron_type !== "DNp01" || projection.direction !== "pre_body_id -> post_body_id" ||
      projection.canonical_order !== "pre_node_index, then post_node_index" ||
      projection.edge_semantics !== "directed structural ConnectsTo relationships from the CircuitContract") {
    return fail("connectivity projection roles or direction are unsupported");
  }
  const semantics = record(item.edge_semantics, "connectivity.edge_semantics");
  exactKeys(semantics, ["weight_field", "weight_source", "structural_weight_is_physiological_coupling"], "connectivity.edge_semantics");
  if (semantics.weight_field !== "structural_weight" || semantics.weight_source !== "neuPrint ConnectsTo.weight" || semantics.structural_weight_is_physiological_coupling !== false) {
    return fail("connectivity structural-weight semantics are unsupported");
  }
  const rawEdges = item.edges;
  if (!Array.isArray(rawEdges)) return fail("connectivity edges are not an array");
  const seen = new Set<string>();
  const edges = rawEdges.map((entry, index): StructuralConnectivityEdge => {
    const edge = record(entry, `connectivity.edges[${index}]`);
    exactKeys(edge, ["pre_body_id", "pre_node_index", "pre_neuron_type", "pre_source_side", "post_body_id", "post_node_index", "post_neuron_type", "post_source_side", "structural_weight"], `connectivity edge ${index}`);
    const preId = integer(edge.pre_body_id, `edges[${index}].pre_body_id`) as StructuralConnectivityBodyId;
    const postId = integer(edge.post_body_id, `edges[${index}].post_body_id`) as StructuralConnectivityBodyId;
    const pre = identityById.get(preId);
    const post = identityById.get(postId);
    const preIndex = integer(edge.pre_node_index, `edges[${index}].pre_node_index`);
    const postIndex = integer(edge.post_node_index, `edges[${index}].post_node_index`);
    const weight = integer(edge.structural_weight, `edges[${index}].structural_weight`);
    if (!pre || !post || !(pre.neuron_type === "LC4" || pre.neuron_type === "LPLC2") || post.neuron_type !== "DNp01" ||
        pre.node_index !== preIndex || post.node_index !== postIndex || edge.pre_neuron_type !== pre.neuron_type ||
        edge.pre_source_side !== pre.source_side || edge.post_neuron_type !== "DNp01" ||
        edge.post_source_side !== post.source_side || weight <= 0) {
      return fail(`connectivity edge ${index} violates the fixed directed projection`);
    }
    const identity = `${preId}:${postId}`;
    if (seen.has(identity)) return fail("connectivity contains duplicate directed edges");
    seen.add(identity);
    if (index > 0) {
      const previous = rawEdges[index - 1] as Record<string, unknown>;
      const previousPre = integer(previous.pre_node_index, "previous pre_node_index");
      const previousPost = integer(previous.post_node_index, "previous post_node_index");
      if (preIndex < previousPre || (preIndex === previousPre && postIndex <= previousPost)) {
        return fail("connectivity edges are not in canonical order");
      }
    }
    return {
      pre_body_id: preId,
      pre_node_index: preIndex,
      pre_neuron_type: pre.neuron_type as "LC4" | "LPLC2",
      pre_source_side: pre.source_side,
      post_body_id: postId,
      post_node_index: postIndex,
      post_neuron_type: "DNp01",
      post_source_side: post.source_side,
      structural_weight: weight,
    };
  });
  if (edges.length !== EXPECTED_STRUCTURAL_EDGES.length || edges.some((edge, index) => {
    const expected = EXPECTED_STRUCTURAL_EDGES[index];
    return edge.pre_body_id !== expected[0] || edge.post_body_id !== expected[1] ||
      edge.structural_weight !== expected[2];
  })) {
    return fail("connectivity edges do not match the pinned source projection");
  }
  const aggregates = record(item.aggregates, "connectivity.aggregates");
  exactKeys(aggregates, ["edge_count", "total_structural_weight", "structural_weight_by_source_type"], "connectivity.aggregates");
  const byType = record(aggregates.structural_weight_by_source_type, "connectivity aggregate by type");
  exactKeys(byType, ["LC4", "LPLC2"], "connectivity aggregate by type");
  const weightByType = {
    LC4: edges.filter((edge) => edge.pre_neuron_type === "LC4").reduce((sum, edge) => sum + edge.structural_weight, 0),
    LPLC2: edges.filter((edge) => edge.pre_neuron_type === "LPLC2").reduce((sum, edge) => sum + edge.structural_weight, 0),
  };
  if (integer(aggregates.edge_count, "aggregates.edge_count") !== edges.length ||
      integer(aggregates.total_structural_weight, "aggregates.total_structural_weight") !== edges.reduce((sum, edge) => sum + edge.structural_weight, 0) ||
      integer(byType.LC4, "aggregates.structural_weight_by_source_type.LC4") !== weightByType.LC4 ||
      integer(byType.LPLC2, "aggregates.structural_weight_by_source_type.LPLC2") !== weightByType.LPLC2) {
    return fail("connectivity aggregates do not match the directed edge set");
  }
  return {
    schema: CONNECTIVITY_SCHEMA,
    kind: "bounded_structural_connectivity",
    dataset: "male-cns:v1.0",
    candidate: { identifier: "looming_giant_fiber_v1", version: 1 },
    source_contract: sourceContract,
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
    edges,
    aggregates: {
      edge_count: edges.length,
      total_structural_weight: edges.reduce((sum, edge) => sum + edge.structural_weight, 0),
      structural_weight_by_source_type: weightByType,
    },
  };
}

export async function listMorphologyArtifacts(): Promise<MorphologyArtifactSummary[]> {
  return requestJson("/api/v1/morphology", (value) => {
    const item = record(value, "morphology artifact list");
    schema(item, MORPHOLOGY_SCHEMA);
    if (item.kind !== "morphology_artifact_list" || !Array.isArray(item.artifacts)) {
      return fail("response is not a morphology artifact list");
    }
    return item.artifacts.map(parseMorphologyArtifactSummary);
  });
}

export async function getMorphologyArtifact(
  artifactId: string,
): Promise<MorphologyArtifactSummary> {
  return requestJson(
    `/api/v1/morphology/${encodeURIComponent(artifactId)}`,
    (value) => {
      const summary = parseMorphologyArtifactSummary(value);
      if (summary.artifact_id !== artifactId) {
        return fail("morphology artifact identity does not match the request");
      }
      return summary;
    },
  );
}

export async function getMorphologyBody(
  artifactId: string,
  bodyId: MorphologyBodyId,
): Promise<MorphologyBody> {
  return requestJson(
    `/api/v1/morphology/${encodeURIComponent(artifactId)}/bodies/${bodyId}`,
    (value) => {
      const body = parseMorphologyBody(value);
      if (body.artifact_id !== artifactId || body.body_id !== bodyId) {
        return fail("morphology response identity does not match the request");
      }
      return body;
    },
  );
}

export async function getStructuralConnectivity(
  projectionId: typeof STRUCTURAL_CONNECTIVITY_PROJECTION_ID = STRUCTURAL_CONNECTIVITY_PROJECTION_ID,
): Promise<StructuralConnectivityProjection> {
  return requestJson(
    `/api/v1/connectivity/${encodeURIComponent(projectionId)}`,
    parseStructuralConnectivity,
  );
}
