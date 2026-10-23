import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync, existsSync } from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { RecordedExperiments } from "../src/components/discovery/RecordedExperiments";
import { ScenarioDiscovery, discoveryCopy } from "../src/components/discovery/ScenarioDiscovery";
import { DiscoveryShell, DiscoveryState } from "../src/components/discovery/DiscoveryShell";
import { parseExperimentSummary, listExperiments, NeuroflyApiError } from "../src/lib/neuroflyClient";
import { SCENARIO_KINDS, parseScenarioCatalog } from "../src/lib/scenarioPlayback";
import ExperimentsPage from "../src/app/experiments/page";
import ScenarioLoading from "../src/app/scenarios/loading";
import ExperimentLoading from "../src/app/experiments/loading";

// Existing API parser fixture; transport test only, never a biological observation.
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


const catalog = () => parseScenarioCatalog(SCENARIO_KINDS.map(id => ({id, scenario_kind:id, title:`Source ${id}`, description:"Transport fixture", availability:"CANONICAL_PRESET", preset_only:true, scientific_caveat:"Model assumptions apply"})));
const renderRuns = (experiments: ReturnType<typeof parseExperimentSummary>[] | null, error: string | null = null) => renderToStaticMarkup(createElement(RecordedExperiments,{experiments,error}));

test("five real IDs map one-to-one to preserved routes; catalog rendering is immutable and inert", () => {
  const data=catalog(),before=JSON.stringify(data),html=renderToStaticMarkup(createElement(ScenarioDiscovery,{scenarios:data}));
  assert.deepEqual(Object.keys(discoveryCopy),[...SCENARIO_KINDS]);
  assert.equal((html.match(/data-scenario-id=/g)||[]).length,5);
  for(const item of data){assert(html.includes(`href="/scenarios/${item.id}"`));assert(html.includes(item.title));assert(html.includes(discoveryCopy[item.id].title));}
  assert.equal(JSON.stringify(data),before);
  for(const [,href] of html.matchAll(/<a[^>]*href="([^"#]+)"/g)) {
    const route=href.startsWith("/scenarios/")?"/scenarios/[scenarioId]":href;
    assert(existsSync(new URL(`../src/app${route}/page.tsx`,import.meta.url)),href);
  }
  assert.doesNotMatch(html,/<canvas|<iframe|<video/);
  assert.match(html,/Concept diagram · not measured data/);
  const source=readFileSync(new URL("../src/components/discovery/ScenarioDiscovery.tsx",import.meta.url),"utf8");
  assert.doesNotMatch(source,/new .*Engine|useEffect|requestAnimationFrame|fetch\(|from.*(?:NeuralAdapter|FlightEngine|scenarioPlaybackAPI)/);
});

test("zero, one and multiple recorded runs preserve API order, identity, duration and links", () => {
  assert.match(renderRuns([]),/No recorded experiments yet/);assert.match(renderRuns([]),/not automatically saved here/);
  const a=parseExperimentSummary(summaryFixture()),b=parseExperimentSummary({...summaryFixture(),artifact_id:"f".repeat(64),candidate:{identifier:"another_model_v3",version:3}});
  for(const runs of [[a],[b,a]]) {
    const before=JSON.stringify(runs),html=renderRuns(runs);
    assert.equal((html.match(/class="recorded-identity"/g)||[]).length,runs.length);
    for(const run of runs){assert(html.includes(`href="/experiments/${run.artifact_id}"`));assert(html.includes(`href="/experiments/${run.artifact_id}/cockpit"`));assert(html.includes(`${run.duration_ms} ms`));assert(html.includes(run.artifact_id));}
    if(runs.length>1)assert(html.indexOf(b.artifact_id)<html.indexOf(a.artifact_id));
    assert.equal(JSON.stringify(runs),before);assert.doesNotMatch(html,/<time|2026-|cloud saved|sign in/i);
    assert.match(html,/Empirical validation: not evaluated/);
  }
});

test("failed verification is visible and never rendered as an empty collection or stale records", () => {
  const html=renderRuns([parseExperimentSummary(summaryFixture())],"The experiment artifact failed integrity validation.");
  assert.match(html,/role="alert"/);
  assert.match(html,/Recorded experiments are temporarily unavailable/);
  assert.match(html,/The current experiment archive could not be verified, so no results are displayed/);
  const technical=html.match(/<details class="discovery-context">[\s\S]*?<\/details>/)?.[0];
  assert.ok(technical);assert.match(technical,/Technical details/);assert.match(technical,/The experiment artifact failed integrity validation/);assert.doesNotMatch(technical,/<details[^>]* open/);
  assert.match(html,/href="\/visual-lab\/arena"[^>]*>Enter the Lab/);assert.match(html,/href="\/visual-lab\/arena\/research"[^>]*>Find research tools/);
  assert.doesNotMatch(html,/No recorded experiments yet|class="recorded-identity"/);
});

test("page preserves the read-only API for empty, valid, malformed and failed data", async () => {
  const saved=globalThis.fetch,url=process.env.NEUROFLY_API_BASE_URL;process.env.NEUROFLY_API_BASE_URL="https://api.test";
  try {
    for(const experiments of [[],[summaryFixture()],[summaryFixture(),{...summaryFixture(),artifact_id:"f".repeat(64)}]]) {
      const calls:string[]=[];globalThis.fetch=async input=>{calls.push(String(input));return Response.json({schema:"experiment_http_v1",kind:"experiment_list",experiments});};
      const html=renderToStaticMarkup(await ExperimentsPage());assert.deepEqual(calls,["https://api.test/api/v1/experiments"]);
      assert.equal((html.match(/<h1\b/g)||[]).length,1);
      if(experiments.length)assert.equal((html.match(/class="recorded-identity"/g)||[]).length,experiments.length);else assert.match(html,/No recorded experiments yet/);
    }
    globalThis.fetch=async()=>Response.json({schema:"invalid",kind:"experiment_list",experiments:[]});
    await assert.rejects(listExperiments());assert.match(renderToStaticMarkup(await ExperimentsPage()),/role="alert"/);
    globalThis.fetch=async()=>Response.json({schema:"experiment_http_error_v1",code:"artifact_integrity_failure"},{status:409});
    await assert.rejects(listExperiments(),(e:unknown)=>e instanceof NeuroflyApiError&&e.status===409);
    const html=renderToStaticMarkup(await ExperimentsPage());assert.match(html,/Recorded experiments are temporarily unavailable/);assert.match(html,/Technical details/);assert.match(html,/failed integrity validation/);assert.doesNotMatch(html,/No recorded experiments yet/);
  }finally{globalThis.fetch=saved;if(url===undefined)delete process.env.NEUROFLY_API_BASE_URL;else process.env.NEUROFLY_API_BASE_URL=url;}
});

test("shell keeps Explore primary and Recorded experiments in secondary footer navigation", () => {
  for(const active of ["scenarios","experiments"] as const) {
    const html=renderToStaticMarkup(createElement(DiscoveryShell,{active},"Content"));
    assert.equal((html.match(/class="neurofly-logo"/g)||[]).length,2);
    assert.doesNotMatch(html,/class="discovery-switch"/);
    const nav=html.match(/<nav class="nf-desktop-nav"[\s\S]*?<\/nav>/)![0];
    assert.match(nav,/href="\/scenarios"/);assert.doesNotMatch(nav,/href="\/experiments"/);
    if(active==="scenarios")assert.match(nav,/aria-current="page" href="\/scenarios"/);
    else assert.doesNotMatch(nav,/aria-current="page"/);
    const footer=html.match(/<nav aria-label="Footer navigation">[\s\S]*?<\/nav>/)![0];
    assert.match(footer,/href="\/experiments">Recorded experiments<\/a>/);
    assert.match(html,/href="\/visual-lab\/arena"/);assert.match(html,/href="\/#science"/);assert.match(html,/Skip to content/);
  }
});

test("loading is distinct, accessible and does not display pretend records", () => {
  for(const component of [ScenarioLoading,ExperimentLoading]){const html=renderToStaticMarkup(createElement(component));assert.match(html,/role="status" aria-busy="true"/);assert.equal((html.match(/<h1\b/g)||[]).length,1);assert.doesNotMatch(html,/class="recorded-identity"|data-scenario-id=/);}
  assert.match(renderToStaticMarkup(createElement(DiscoveryState,{kind:"error",title:"Unavailable"},"Reason")),/role="alert"/);
});

test("recorded deep-link return paths point to the collection without changing replay components", () => {
  for(const path of ["experiments/[artifactId]/page.tsx","experiments/[artifactId]/cockpit/page.tsx"]){const source=readFileSync(new URL(`../src/app/${path}`,import.meta.url),"utf8");assert.match(source,/href="\/experiments"/);assert.doesNotMatch(source,/href="\/"/);}
  assert(existsSync(new URL("../src/app/visual-lab/arena/research/page.tsx",import.meta.url)));
});
