import assert from "node:assert/strict";
import test from "node:test";

import {
  DEFAULT_EXPERIMENT_QUERY,
  STIMULUS_FILTERS,
  STIMULUS_OF,
  experimentsHref,
  filterScenarios,
  parseExperimentQuery,
  parseStimulus,
  scenarioIsPresentable,
  scenariosHref,
  searchExperiments,
  sortExperiments,
} from "../src/lib/listing";
import { SCENARIO_KINDS } from "../src/lib/scenarioPlayback";
import { parseExperimentSummary } from "../src/lib/neuroflyClient";

const base = (id: string, identifier: string, model: string) => parseExperimentSummary({
  schema: "experiment_api_v1", kind: "experiment_summary", artifact_id: id.repeat(64), experiment_config_id: "cfg", experiment_config_sha256: "c".repeat(64), result_id: "d".repeat(64),
  artifact_schema_version: "experiment_artifact_v1", dataset: "male-cns:v1.0", candidate: { identifier, version: 1 },
  source: { endpoint: "https://neuprint.janelia.org", circuit_integrity: [["connections.jsonl", "e".repeat(64)]] }, graph_scope_id: "g",
  encoder: { id: "e", version: "v", population_policy: "p" }, neural_model: { id: "lif", version: model, membrane_state_references: { rest_mv: -52, threshold_mv: -45 } },
  pathway_condition: "COMBINED", duration_ms: 1, dt_ms: 0.1, validation_status: "NOT_EVALUATED", telemetry_profile: {},
  free_parameters: { lc4_gain_mv_eq: 1, lplc2_gain_mv_eq: 1, omega_half_rad_per_s: 1, theta_half_rad: 1, k_syn_mv_per_contact: 1 },
  populations: {
    LC4: { neuron_type: "LC4", body_count: 1, bodies_that_spike: 0, total_spike_count: 0, first_spike_time_ms: null, peak_normalized_feature: 0, peak_drive_mveq: 0 },
    LPLC2: { neuron_type: "LPLC2", body_count: 1, bodies_that_spike: 0, total_spike_count: 0, first_spike_time_ms: null, peak_normalized_feature: 0, peak_drive_mveq: 0 },
  },
  dnp01: [
    { body_id: 10001, neuron_type: "DNp01", soma_side: "R", total_spike_count: 0, first_spike_time_ms: null, peak_membrane_mv: -52, peak_synaptic_state_mveq: 0, delivered_event_count: 0, model_increment_sum_mveq: 0 },
    { body_id: 10010, neuron_type: "DNp01", soma_side: "L", total_spike_count: 0, first_spike_time_ms: null, peak_membrane_mv: -52, peak_synaptic_state_mveq: 0, delivered_event_count: 0, model_increment_sum_mveq: 0 },
  ],
});

test("every canonical scenario has exactly one stimulus type, and every filter has a scenario", () => {
  for (const id of SCENARIO_KINDS) { assert.ok(STIMULUS_OF[id], id); assert.ok(scenarioIsPresentable(id), id); }
  for (const { key } of STIMULUS_FILTERS) assert.ok(SCENARIO_KINDS.some((id) => STIMULUS_OF[id] === key), key);
  assert.equal(new Set(STIMULUS_FILTERS.map((f) => f.key)).size, STIMULUS_FILTERS.length);
});

test("stimulus parsing and filtering fall back to everything for unknown input", () => {
  assert.equal(parseStimulus("looming"), "looming");
  for (const bad of [undefined, "", "LOOMING", "x", ["x"], ["none", "looming"].join(",")]) assert.equal(parseStimulus(bad as never), null, String(bad));
  assert.equal(parseStimulus(["looming", "none"]), "looming", "the first repeated parameter wins");
  const all = SCENARIO_KINDS.map((id) => ({ id }));
  assert.equal(filterScenarios(all, null).length, 5);
  assert.deepEqual(filterScenarios(all, "looming").map((s) => s.id), ["LOOMING_CIRCUIT_VALIDATION", "LOOMING_WORLD_EXPERIMENT"]);
  assert.equal(scenariosHref(null), "/scenarios");
  assert.equal(scenariosHref("horizontal-motion"), "/scenarios?stimulus=horizontal-motion");
});

test("experiment queries parse defensively and round-trip through the URL without default noise", () => {
  assert.deepEqual(parseExperimentQuery({}), DEFAULT_EXPERIMENT_QUERY);
  assert.deepEqual(parseExperimentQuery({ q: "  loom  ", sort: "model", dir: "desc" }), { q: "loom", sort: "model", dir: "desc" });
  assert.deepEqual(parseExperimentQuery({ sort: "evil", dir: "sideways", q: "x".repeat(500) }).dir, "asc");
  assert.equal(parseExperimentQuery({ q: "x".repeat(500) }).q.length, 100);
  assert.equal(experimentsHref({}), "/experiments");
  assert.equal(experimentsHref({ dir: "desc" }), "/experiments?dir=desc");
  assert.equal(experimentsHref({ q: "a b", sort: "model" }), "/experiments?q=a+b&sort=model");
  for (const query of [{ q: "loom", sort: "model", dir: "desc" }, { q: "", sort: "name", dir: "asc" }] as const) {
    const url = new URL(experimentsHref(query), "https://x.test");
    assert.deepEqual(parseExperimentQuery(Object.fromEntries(url.searchParams)), query);
  }
});

test("search matches name, ids and model case-insensitively, and sort is stable and non-mutating", () => {
  const a = base("a", "looming_giant_fiber_v1", "phase2b_v1"), b = base("b", "another_model_v3", "phase9_v1"), c = base("c", "another_model_v3", "phase2b_v1");
  const list = [a, b, c], before = JSON.stringify(list);
  assert.deepEqual(searchExperiments(list, "LOOMING").map((e) => e.artifact_id[0]), ["a"]);
  assert.deepEqual(searchExperiments(list, "another").map((e) => e.artifact_id[0]), ["b", "c"]);
  assert.deepEqual(searchExperiments(list, "b".repeat(8)).map((e) => e.artifact_id[0]), ["b"]);
  assert.deepEqual(searchExperiments(list, "phase9").map((e) => e.artifact_id[0]), ["b"]);
  assert.equal(searchExperiments(list, "nothing here").length, 0);
  assert.equal(searchExperiments(list, "  ").length, 3);
  // Names tie for b and c, so they keep the API order; descending reverses the groups, not the ties.
  assert.deepEqual(sortExperiments(list, "name", "asc").map((e) => e.artifact_id[0]), ["b", "c", "a"]);
  assert.deepEqual(sortExperiments(list, "name", "desc").map((e) => e.artifact_id[0]), ["a", "b", "c"]);
  assert.deepEqual(sortExperiments(list, "model", "asc").map((e) => e.artifact_id[0]), ["a", "c", "b"]);
  assert.equal(JSON.stringify(list), before);
});
