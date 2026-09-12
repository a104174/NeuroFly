const HTTP_SCHEMA = "experiment_http_v1" as const;
const APPLICATION_SCHEMA = "experiment_api_v1" as const;
const ERROR_SCHEMA = "experiment_http_error_v1" as const;
const VALIDATION_STATUS = "NOT_EVALUATED" as const;

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
  encoder: { id: string; version: string };
  neural_model: { id: string; version: string };
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
    },
    neural_model: {
      id: stringValue(neuralModel.id, "neural_model.id"),
      version: stringValue(neuralModel.version, "neural_model.version"),
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
