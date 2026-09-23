import assert from "node:assert/strict";
import { test } from "node:test";

import {
  getTimeline,
  listExperiments,
  NeuroflyApiError,
  parseExperimentSummary,
  parseExperimentTimeline,
} from "../src/lib/neuroflyClient";

function summaryFixture() {
  return {
    schema: "experiment_api_v1",
    kind: "experiment_summary",
    artifact_id: "a".repeat(64),
    experiment_config_id: "b".repeat(64),
    experiment_config_sha256: "c".repeat(64),
    result_id: "d".repeat(64),
    artifact_schema_version: "experiment_artifact_v1",
    dataset: "male-cns:v1.0",
    candidate: { identifier: "looming_giant_fiber_v1", version: 1 },
    source: {
      endpoint: "https://neuprint.janelia.org",
      circuit_integrity: [["connections.jsonl", "e".repeat(64)]],
    },
    graph_scope_id: "phase2b_direct_visual_dnp01_v1",
    encoder: {
      id: "level_p_instantaneous_bounded_v1",
      version: "phase2e_v1",
      population_policy: "bilateral_type_broadcast_v1",
    },
    neural_model: {
      id: "deterministic_lif_filtered_synapse_v1",
      version: "phase2b_v1",
      membrane_state_references: { rest_mv: -52, threshold_mv: -45 },
    },
    pathway_condition: "COMBINED",
    duration_ms: 0.2,
    dt_ms: 0.1,
    validation_status: "NOT_EVALUATED",
    telemetry_profile: { profile_id: "VALIDATION_TELEMETRY_V1" },
    free_parameters: {
      lc4_gain_mv_eq: 20,
      lplc2_gain_mv_eq: 21,
      omega_half_rad_per_s: 1,
      theta_half_rad: 0.4,
      k_syn_mv_per_contact: 0.01,
    },
    populations: {
      LC4: {
        neuron_type: "LC4",
        body_count: 126,
        bodies_that_spike: 1,
        total_spike_count: 1,
        first_spike_time_ms: 0.1,
        peak_normalized_feature: 0.2,
        peak_drive_mveq: 4,
      },
      LPLC2: {
        neuron_type: "LPLC2",
        body_count: 185,
        bodies_that_spike: 1,
        total_spike_count: 1,
        first_spike_time_ms: 0.1,
        peak_normalized_feature: 0.3,
        peak_drive_mveq: 6,
      },
    },
    dnp01: [
      {
        body_id: 10001,
        neuron_type: "DNp01",
        soma_side: "R",
        total_spike_count: 0,
        first_spike_time_ms: null,
        peak_membrane_mv: -55,
        peak_synaptic_state_mveq: 0.2,
        delivered_event_count: 1,
        model_increment_sum_mveq: 0.1,
      },
      {
        body_id: 10010,
        neuron_type: "DNp01",
        soma_side: "L",
        total_spike_count: 1,
        first_spike_time_ms: 0.2,
        peak_membrane_mv: -45,
        peak_synaptic_state_mveq: 0.3,
        delivered_event_count: 2,
        model_increment_sum_mveq: 0.2,
      },
    ],
  };
}

function timelineFixture() {
  return {
    schema: "experiment_api_v1",
    kind: "experiment_timeline",
    artifact_id: "a".repeat(64),
    time_unit: "ms",
    dt_ms: 0.1,
    duration_ms: 0.2,
    start_ms: 0,
    end_ms: 0.2,
    times_ms: [0, 0.1, 0.2],
    step_times_ms: [0, 0.1],
    interval_semantics: "step_values_apply_on_[t_n,t_n+dt)",
    theta_unit: "rad",
    theta_rad: [0.1, 0.2],
    angular_expansion_velocity_unit: "rad/s",
    angular_expansion_velocity_rad_s: [1, 2],
    lc4_normalized_feature: [0.1, 0.2],
    lplc2_normalized_feature: [0.2, 0.3],
    drive_unit: "mV_eq",
    lc4_drive_mveq: [2, 4],
    lplc2_drive_mveq: [3, 6],
    selected_body_telemetry: [],
  };
}

test("parses the real application contract without collapsing scientific identities", () => {
  const summary = parseExperimentSummary(summaryFixture());
  assert.equal(summary.validation_status, "NOT_EVALUATED");
  assert.equal(summary.dataset, "male-cns:v1.0");
  assert.equal(summary.graph_scope_id, "phase2b_direct_visual_dnp01_v1");
  assert.equal(summary.pathway_condition, "COMBINED");
  assert.equal(summary.free_parameters.lc4_gain_mv_eq, 20);
  assert.equal(summary.free_parameters.lplc2_gain_mv_eq, 21);
  assert.equal(summary.free_parameters.k_syn_mv_per_contact, 0.01);
  assert.equal(summary.free_parameters.omega_half_rad_per_s, 1);
  assert.equal(summary.free_parameters.theta_half_rad, 0.4);
  assert.equal(summary.encoder.population_policy, "bilateral_type_broadcast_v1");
  assert.equal(summary.neural_model.membrane_state_references.rest_mv, -52);
  assert.equal(summary.neural_model.membrane_state_references.threshold_mv, -45);
  assert.equal(summary.populations.LC4.neuron_type, "LC4");
  assert.equal(summary.populations.LPLC2.neuron_type, "LPLC2");
  assert.deepEqual(summary.dnp01.map((item) => item.body_id), [10001, 10010]);
});

test("rejects incompatible status, schema, and timeline shapes", () => {
  assert.throws(
    () => parseExperimentSummary({ ...summaryFixture(), schema: "future_v2" }),
    (error: unknown) =>
      error instanceof NeuroflyApiError && error.code === "UNSUPPORTED_SCHEMA",
  );
  assert.throws(
    () => parseExperimentSummary({ ...summaryFixture(), validation_status: "VALIDATED" }),
    (error: unknown) =>
      error instanceof NeuroflyApiError && error.code === "INVALID_RESPONSE",
  );
  assert.throws(
    () => parseExperimentTimeline({ ...timelineFixture(), step_times_ms: [0] }),
    (error: unknown) =>
      error instanceof NeuroflyApiError && error.code === "INVALID_RESPONSE",
  );
  assert.throws(
    () => parseExperimentTimeline({ ...timelineFixture(), theta_rad: [0.1] }),
    (error: unknown) =>
      error instanceof NeuroflyApiError && error.code === "INVALID_RESPONSE",
  );
  assert.throws(
    () => parseExperimentSummary({
      ...summaryFixture(),
      neural_model: { id: "lif", version: "v1" },
    }),
    (error: unknown) =>
      error instanceof NeuroflyApiError && error.code === "INVALID_RESPONSE",
  );
});

test("uses the configured API, preserves timeline values, and never falls back to mock data", async () => {
  const originalFetch = globalThis.fetch;
  const originalBase = process.env.NEUROFLY_API_BASE_URL;
  process.env.NEUROFLY_API_BASE_URL = "http://api.test";
  let requestUrl = "";
  globalThis.fetch = async (input) => {
    requestUrl = String(input);
    return new Response(
      JSON.stringify({
        schema: "experiment_http_v1",
        kind: "experiment_list",
        experiments: [summaryFixture()],
        count: 1,
      }),
      { status: 200, headers: { "content-type": "application/json" } },
    );
  };
  try {
    const experiments = await listExperiments();
    assert.equal(requestUrl, "http://api.test/api/v1/experiments");
    assert.equal(experiments[0].artifact_id, "a".repeat(64));
    assert.equal(experiments[0].free_parameters.lc4_gain_mv_eq, 20);

    globalThis.fetch = async (input) => {
      requestUrl = String(input);
      return new Response(JSON.stringify(timelineFixture()), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    };
    const timeline = await getTimeline("a".repeat(64), { start_ms: 0, end_ms: 0.2 });
    assert.equal(
      requestUrl,
      `http://api.test/api/v1/experiments/${"a".repeat(64)}/timeline?start_ms=0&end_ms=0.2`,
    );
    assert.deepEqual(timeline.times_ms, [0, 0.1, 0.2]);
    assert.deepEqual(timeline.lc4_drive_mveq, [2, 4]);

    globalThis.fetch = async () => {
      throw new Error("offline");
    };
    await assert.rejects(
      () => listExperiments(),
      (error: unknown) =>
        error instanceof NeuroflyApiError && error.code === "API_UNREACHABLE",
    );
  } finally {
    globalThis.fetch = originalFetch;
    if (originalBase === undefined) delete process.env.NEUROFLY_API_BASE_URL;
    else process.env.NEUROFLY_API_BASE_URL = originalBase;
  }
});
