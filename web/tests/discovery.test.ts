import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync, existsSync } from "node:fs";
import { createElement, type ComponentType, type ReactNode } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { register } from "node:module";
// Node cannot import CSS Modules. Register the test-only hook before the components load, so the
// imports that reach CSS are dynamic. (package.json is frozen, so this cannot be an npm script.)
register(new URL("./support/css-hooks.mjs", import.meta.url));
const { default: ScenariosPage } = await import("../src/app/scenarios/(list)/page");
const { PageShell } = await import("../src/components/site/PageShell");
import { parseExperimentSummary, listExperiments, NeuroflyApiError } from "../src/lib/neuroflyClient";
import { discoveryCopy, experimentMetadata } from "../src/lib/scenarioPresentation";
import { SCENARIO_KINDS, parseScenarioCatalog } from "../src/lib/scenarioPlayback";
const { default: ExperimentsPage } = await import("../src/app/experiments/(list)/page");
const { default: ScenarioLoading } = await import("../src/app/scenarios/(list)/loading");
const { default: ExperimentLoading } = await import("../src/app/experiments/(list)/loading");

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


const catalogPayload = () => SCENARIO_KINDS.map(id => ({id, scenario_kind:id, title:`Source ${id}`, description:"Transport fixture", availability:"CANONICAL_PRESET", preset_only:true, scientific_caveat:`Caveat for ${id}`}));
const catalog = () => parseScenarioCatalog(catalogPayload());
type Params = Record<string, string | string[] | undefined>;

/** Runs `check` with a fake API at https://api.test and records every request. */
async function withApi(respond: (url: string) => Response | Promise<Response>, check: (calls: { url: string; method: string }[]) => Promise<void>) {
  const saved = globalThis.fetch, base = process.env.NEUROFLY_API_BASE_URL;
  process.env.NEUROFLY_API_BASE_URL = "https://api.test";
  const calls: { url: string; method: string }[] = [];
  globalThis.fetch = async (input, init) => { calls.push({ url: String(input), method: init?.method ?? "GET" }); return respond(String(input)); };
  try { await check(calls); }
  finally { globalThis.fetch = saved; if (base === undefined) delete process.env.NEUROFLY_API_BASE_URL; else process.env.NEUROFLY_API_BASE_URL = base; }
}
const listOf = (experiments: unknown[]) => Response.json({ schema: "experiment_http_v1", kind: "experiment_list", experiments });
const renderExperiments = async (params: Params = {}) => renderToStaticMarkup(await ExperimentsPage({ searchParams: Promise.resolve(params) }));
const renderScenarios = async (params: Params = {}) => renderToStaticMarkup(await ScenariosPage({ searchParams: Promise.resolve(params) }));
const other = () => ({ ...summaryFixture(), artifact_id: "f".repeat(64), candidate: { identifier: "another_model_v3", version: 3 }, neural_model: { ...summaryFixture().neural_model, version: "phase9_v1" } });

test("five real IDs map one-to-one to preserved routes; the catalogue is rendered, immutable and inert", async () => {
  const data = catalog(), before = JSON.stringify(data);
  await withApi(() => Response.json(catalogPayload()), async (calls) => {
    const html = await renderScenarios();
    assert.deepEqual(calls.map(c => c.url), ["https://api.test/api/v1/scenarios"]);
    assert.deepEqual(Object.keys(discoveryCopy), [...SCENARIO_KINDS]);
    assert.equal((html.match(/data-scenario-id=/g) || []).length, 5);
    for (const item of data) {
      assert(html.includes(`href="/scenarios/${item.id}"`), item.id);
      assert(html.includes(discoveryCopy[item.id].title), item.id);
      // Provenance and the limit stay with each card, under "What this does not show".
      assert(html.includes(`Scenario name in the API: ${item.title}`), item.id);
      assert(html.includes(`Caveat for ${item.id}`), item.id);
      assert(html.includes(experimentMetadata[item.id].limit), item.id);
      assert(html.includes(experimentMetadata[item.id].duration), item.id);
    }
    assert.match(html, /What this does not show/);
    // Headings descend without a gap: h1, then one h2 per card.
    assert.equal((html.match(/<h2\b/g) || []).length >= 5, true);
    assert.doesNotMatch(html, /<h3\b/);
    assert.equal((html.match(/<h1\b/g) || []).length, 1);
    for (const [, href] of html.matchAll(/<a[^>]*href="([^"#?]+)"/g)) {
      const route = href.startsWith("/scenarios/") ? "/scenarios/[scenarioId]" : href;
      assert(existsSync(new URL(`../src/app${route}/page.tsx`, import.meta.url)) || existsSync(new URL(`../src/app${route}/(list)/page.tsx`, import.meta.url)) || href.startsWith("https://"), href);
    }
    assert.doesNotMatch(html, /<canvas|<iframe|<video|verified/i);
    assert.doesNotMatch(html, /Neural-only validation|Closed-loop experiment/);
  });
  assert.equal(JSON.stringify(data), before);
  for (const file of ["app/scenarios/(list)/page.tsx", "app/experiments/(list)/page.tsx"]) {
    assert.doesNotMatch(readFileSync(new URL(`../src/${file}`, import.meta.url), "utf8"), /new .*Engine|useEffect|requestAnimationFrame|fetch\(|from.*(?:NeuralAdapter|FlightEngine|scenarioPlaybackAPI)/, file);
  }
});

test("the stimulus filter lives in the URL, marks its selection, and unknown values show everything", async () => {
  await withApi(() => Response.json(catalogPayload()), async () => {
    const all = await renderScenarios();
    assert.match(all, /role="group" aria-label="Stimulus type"/);
    assert.match(all, /Showing 5 of 5 scenarios/);
    assert.match(all, /aria-current="true"[^>]*href="\/scenarios"|href="\/scenarios"[^>]*aria-current="true"/);
    const looming = await renderScenarios({ stimulus: "looming" });
    assert.match(looming, /Showing 2 of 5 scenarios/);
    assert.equal((looming.match(/data-scenario-id=/g) || []).length, 2);
    for (const id of ["LOOMING_CIRCUIT_VALIDATION", "LOOMING_WORLD_EXPERIMENT"]) assert(looming.includes(`data-scenario-id="${id}"`), id);
    assert.equal((looming.match(/aria-current="true"/g) || []).length, 1);
    assert.match(looming, /aria-current="true"[^>]*href="\/scenarios\?stimulus=looming"|href="\/scenarios\?stimulus=looming"[^>]*aria-current="true"/);
    assert.equal((await renderScenarios({ stimulus: "none" })).match(/data-scenario-id=/g)?.length, 1);
    for (const bogus of ["nonsense", "", ["looming", "none"].join(",")]) assert.match(await renderScenarios({ stimulus: bogus }), /Showing 5 of 5 scenarios/, bogus);
    // Every filter option is a real link, so it works without JavaScript.
    for (const key of ["none", "looming", "horizontal-motion", "orientation"]) assert(all.includes(`href="/scenarios?stimulus=${key}"`), key);
  });
});

test("zero, one and multiple recorded runs show identity, links and honest gaps, and never invent a scenario or date", async () => {
  const a = summaryFixture(), b = other();
  await withApi(() => listOf([]), async () => assert.match(await renderExperiments(), /No experiments are published yet/));
  for (const runs of [[a], [b, a]]) {
    await withApi(() => listOf(runs), async (calls) => {
      const html = await renderExperiments();
      assert.deepEqual(calls.map(c => c.url), ["https://api.test/api/v1/experiments"]);
      assert.equal((html.match(/<h1\b/g) || []).length, 1);
      assert.match(html, /<caption>Published experiments/);
      assert.equal((html.match(/<th[^>]*scope="row"/g) || []).length, runs.length);
      for (const run of runs) {
        assert(html.includes(`href="/experiments/${run.artifact_id}"`));
        assert(html.includes(`href="/experiments/${run.artifact_id}/cockpit"`));
        assert(html.includes(`aria-label="Open Cockpit for `));
        assert(html.includes(run.artifact_id));
      }
      // Scenario and date are not in the API summary: shown as "Not recorded", never invented.
      assert.equal((html.match(/Not recorded/g) || []).length, runs.length * 2);
      assert.equal((html.match(/data-kind="not-evaluated"/g) || []).length, runs.length, "one status badge per row");
      assert.doesNotMatch(html, /<time|2026-|cloud saved|sign in|verified/i);
    });
  }
  // Default order is by name, so "Another model v3" comes before "Looming giant fiber v1" even though the API lists it first or last.
  await withApi(() => listOf([a, b]), async () => { const html = await renderExperiments(); assert(html.indexOf(b.artifact_id) < html.indexOf(a.artifact_id)); });
});

test("only the recorded engineering smoke run carries the engineering-test label", async () => {
  const smoke = { ...summaryFixture(), experiment_config_id: "ui_smoke_phase2f_reference_v1" };
  await withApi(() => listOf([smoke, other()]), async () => {
    const html = await renderExperiments();
    assert.equal((html.match(/Engineering test, not a scientific experiment/g) || []).length, 2, "the row tag and the footer link");
    const row = html.match(/<tr role="row"><th[^>]*>[\s\S]*?<\/tr>/g)!.find(r => r.includes(smoke.artifact_id))!;
    assert.match(row, /Engineering test, not a scientific experiment/);
    const unrelated = html.match(/<tr role="row"><th[^>]*>[\s\S]*?<\/tr>/g)!.find(r => r.includes("f".repeat(64)))!;
    assert.doesNotMatch(unrelated, /Engineering test/);
  });
});

test("experiments sort, search and clear through the URL, with aria-sort on the sorted column", async () => {
  const a = summaryFixture(), b = other();
  await withApi(() => listOf([a, b]), async () => {
    const byName = await renderExperiments();
    assert.match(byName, /<th scope="col" role="columnheader" aria-sort="ascending">/);
    assert.match(byName, /<th scope="col" role="columnheader" aria-sort="none"><a[^>]*href="\/experiments\?sort=model"/);
    assert.match(byName, /href="\/experiments\?dir=desc"/, "the sorted column offers the opposite direction");
    const desc = await renderExperiments({ dir: "desc" });
    assert.match(desc, /aria-sort="descending"/);
    assert(desc.indexOf(a.artifact_id) < desc.indexOf(b.artifact_id));
    const byModel = await renderExperiments({ sort: "model" });
    assert.match(byModel, /<th scope="col" role="columnheader" aria-sort="ascending"><a[^>]*>Model version/);
    const found = await renderExperiments({ q: "another" });
    assert.match(found, /Showing 1 of 2 experiments/);
    assert(found.includes(b.artifact_id) && !found.includes(a.artifact_id));
    assert.match(found, /value="another"/);
    const none = await renderExperiments({ q: "zzz" });
    assert.match(none, /No experiments match these filters\./);
    assert.match(none, /href="\/experiments"[^>]*>Clear filters/);
    assert.doesNotMatch(none, /<table/);
    // The search form is a real GET form, and keeps a non-default sort.
    assert.match(byModel, /<form role="search"[^>]*action="\/experiments" method="get">/);
    assert.match(byModel, /<input type="hidden" name="sort" value="model"\/>/);
  });
});

test("the evaluation note is a one-line, dismissible and restorable note", async () => {
  await withApi(() => listOf([summaryFixture()]), async () => {
    const html = await renderExperiments();
    assert.match(html, /role="note"/);
    assert.match(html, /No experiment has been evaluated against biological data yet\./);
    assert.match(html, /aria-label="Dismiss this note"/);
  });
  const source = readFileSync(new URL("../src/components/NoticeBanner.tsx", import.meta.url), "utf8");
  assert.match(source, /Show the note|restoreLabel/);
  assert.match(source, /try \{/, "storage access is guarded");
});

test("failed or blocked data is visible and never rendered as an empty collection or stale records", async () => {
  await withApi(() => Response.json({ schema: "invalid", kind: "experiment_list", experiments: [] }), async () => {
    await assert.rejects(listExperiments());
    const html = await renderExperiments();
    assert.match(html, /role="alert"/);
    assert.match(html, /The data service isn&#x27;t responding\./);
    assert.match(html, /Nothing on this page has been lost\./);
    assert.doesNotMatch(html, /No experiments are published yet|<table/);
  });
  await withApi(() => Response.json({ schema: "experiment_http_error_v1", code: "artifact_integrity_failure", message: "artifact failed integrity validation" }, { status: 409 }), async () => {
    await assert.rejects(listExperiments(), (e: unknown) => e instanceof NeuroflyApiError && e.status === 409);
    const html = await renderExperiments();
    assert.match(html, /role="alert"/);
    assert.match(html, /The stored results failed their integrity check\./);
    assert.match(html, /No results are shown, and none are substituted\./);
    const technical = html.match(/<details class="technical">[\s\S]*?<\/details>/)?.[0];
    assert.ok(technical);
    assert.match(technical, /Technical details/);
    assert.match(technical, /failed integrity validation/);
    assert.doesNotMatch(technical, /<details[^>]* open/);
    assert.doesNotMatch(html, /No experiments are published yet|<table|data-scenario-id/);
  });
});

test("scenario failures are visible, explain themselves and never substitute a catalogue", async () => {
  for (const respond of [() => Response.json([]), () => Response.json({ schema: "experiment_http_error_v1", code: "scenario_unavailable" }, { status: 503 }), () => Response.json({ nope: true })]) {
    await withApi(respond, async () => {
      const html = await renderScenarios();
      assert.match(html, /role="alert"/);
      assert.match(html, /Technical details/);
      assert.match(html, /so no scenarios are shown and none are substituted/);
      assert.doesNotMatch(html, /data-scenario-id=|Showing \d+ of/);
      assert.match(html, /href="\/visual-lab\/arena"[^>]*>Enter the Lab/);
    });
  }
});

test("the list pages use the themed shell: header and footer follow the theme, Experiments is not primary", () => {
  for (const current of ["/scenarios", "/experiments"]) {
    const html = renderToStaticMarkup(createElement(PageShell as ComponentType<{ title: string; current: string; children?: ReactNode }>, { title: "T", current }, "Content"));
    assert.equal((html.match(/class="neurofly-logo"/g) || []).length, 2);
    assert.doesNotMatch(html, /<(?:header|footer) class="(?:header|footer)"[^>]*data-theme-scope/);
    assert.match(html, /aria-label="Colour theme"/);
    const nav = html.match(/<nav[^>]*aria-label="Primary navigation"[\s\S]*?<\/nav>/)![0];
    assert.match(nav, /href="\/scenarios"/); assert.doesNotMatch(nav, /href="\/experiments"/);
    if (current === "/scenarios") assert.match(nav, /aria-current="page"[^>]*href="\/scenarios"|href="\/scenarios"[^>]*aria-current="page"/);
    else assert.doesNotMatch(nav, /aria-current="page"/);
    const footer = html.match(/<nav aria-label="Footer navigation"[^>]*>[\s\S]*?<\/nav>/)![0];
    assert.match(footer, /href="\/experiments">Engineering test, not a scientific experiment<\/a>/);
    assert.match(html, /Skip to content/); assert.match(html, /<main id="main-content" tabindex="-1"/);
  }
});

test("the shared page frame reveals streamed content and hides the loading screen when scripts are off", () => {
  const html = renderToStaticMarkup(createElement(PageShell as ComponentType<{ title: string; children?: ReactNode }>, { title: "T" }, "Content"));
  const fallback = html.match(/<noscript>[\s\S]*?<\/noscript>/)?.[0];
  assert.ok(fallback);
  assert.match(fallback, /body > \[hidden\]:has\(> \[data-themed-page\]\) \{ display: block !important; \}/);
  assert.match(fallback, /body:has\(> \[hidden\] > \[data-themed-page\]\) > \[data-themed-page\] \{ display: none !important; \}/);
  assert.doesNotMatch(fallback, /fetch|api\//);
});

test("loading is distinct, accessible and does not display pretend records", () => {
  for (const component of [ScenarioLoading, ExperimentLoading]) {
    const html = renderToStaticMarkup(createElement(component));
    assert.match(html, /role="status" aria-busy="true"/);
    assert.equal((html.match(/<h1\b/g) || []).length, 1);
    assert.doesNotMatch(html, /<table|data-scenario-id=/);
  }
});

test("recorded deep-link return paths point to the collection without changing replay components", () => {
  for (const path of ["experiments/[artifactId]/page.tsx", "experiments/[artifactId]/cockpit/page.tsx"]) {
    const source = readFileSync(new URL(`../src/app/${path}`, import.meta.url), "utf8");
    assert.match(source, /href="\/experiments"/); assert.doesNotMatch(source, /href="\/"/);
  }
  assert(existsSync(new URL("../src/app/visual-lab/arena/research/page.tsx", import.meta.url)));
});
