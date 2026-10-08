import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import HomePage, { dynamic } from "../src/app/page";
import Loading from "../src/app/loading";
import ExperimentsPage from "../src/app/experiments/page";
import ScenariosPage from "../src/app/scenarios/page";
import { listExperiments, NeuroflyApiError } from "../src/lib/neuroflyClient";
import { listScenarios } from "../src/lib/scenarioCatalog";
import { parseScenarioCatalog, SCENARIO_KINDS } from "../src/lib/scenarioPlayback";
import { experimentMetadata } from "../src/lib/scenarioPresentation";

// Synthetic catalogue transport only: no replay frames or production fallback.
const fixture = () => SCENARIO_KINDS.map((id) => ({
  id, scenario_kind: id, title: `Fixture ${id}`, description: `Fixture description ${id}`,
  availability: "CANONICAL_PRESET", preset_only: true, scientific_caveat: "Model-only fixture",
}));

async function withFetch(
  response: () => Promise<Response>,
  check: (calls: { url: string; options?: RequestInit }[]) => Promise<void>,
) {
  const oldFetch = globalThis.fetch;
  const oldBase = process.env.NEUROFLY_API_BASE_URL;
  const calls: { url: string; options?: RequestInit }[] = [];
  process.env.NEUROFLY_API_BASE_URL = "https://preview.test";
  globalThis.fetch = async (url, options) => {
    calls.push({ url: String(url), options });
    return response();
  };
  try { await check(calls); }
  finally {
    globalThis.fetch = oldFetch;
    if (oldBase === undefined) delete process.env.NEUROFLY_API_BASE_URL;
    else process.env.NEUROFLY_API_BASE_URL = oldBase;
  }
}
const json = (payload: unknown, status = 200) => async () => new Response(
  JSON.stringify(payload), { status, headers: { "Content-Type": "application/json" } },
);

function noCards(markup: string) {
  assert.doesNotMatch(markup, /class="scenario-card"|Canonical replay available/);
}

test("homepage requests the genuine catalogue contract and renders five accessible scenario links", async () => {
  const payload = fixture();
  assert.equal(parseScenarioCatalog(payload).length, 5);
  await withFetch(json(payload), async (calls) => {
    const markup = renderToStaticMarkup(await HomePage());
    assert.equal(dynamic, "force-dynamic");
    assert.deepEqual(calls.map(c => c.url), ["https://preview.test/api/v1/scenarios"]);
    assert.equal(calls[0].options?.cache, "no-store");
    assert.match(markup, /Explore canonical scenarios\./);
    assert.match(markup, /CANONICAL SCENARIOS/);
    assert.match(markup, /aria-label="Canonical scenario catalogue"/);
    assert.equal((markup.match(/class="scenario-card"/g) ?? []).length, 5);
    for (const scenario of payload) {
      assert.ok(markup.includes(`href="/scenarios/${scenario.id}"`));
      assert.ok(markup.includes(`aria-label="Open ${scenario.title}"`));
      assert.ok(markup.includes(scenario.title));
      assert.ok(markup.includes(experimentMetadata[scenario.id].kind));
    }
    assert.match(markup, /href="\/experiments"/);
    assert.doesNotMatch(markup, /href="\/experiments\/[a-f0-9]{64}"|Completed experiments/);
    assert.deepEqual(payload, fixture());
  });
});

test("homepage titles come from the response, not a hardcoded successful catalogue", async () => {
  const payload = fixture(); payload[0].title = "Different authoritative title";
  await withFetch(json(payload), async () => {
    const markup = renderToStaticMarkup(await HomePage());
    assert.match(markup, /Different authoritative title/);
    assert.doesNotMatch(markup, /Fixture BASELINE_CONTROL/);
  });
});

test("empty catalogue is explicit absence, never a valid fabricated canonical set", async () => {
  assert.throws(() => parseScenarioCatalog([]));
  await withFetch(json([]), async () => {
    const markup = renderToStaticMarkup(await HomePage());
    assert.match(markup, /NO CANONICAL SCENARIOS/);
    assert.match(markup, /The scenario catalogue is empty/);
    noCards(markup);
  });
});

for (const [label, payload] of [
  ["incomplete", fixture().slice(0, 4)],
  ["missing metadata", fixture().map((row, i) => i ? row : { id: row.id })],
  ["wrong classification", fixture().map((row, i) => i ? row : { ...row, preset_only: false })],
  ["wrong shape", { scenarios: fixture() }],
] as const) {
  test(`homepage rejects ${label} catalogue without substitution`, async () => {
    await withFetch(json(payload), async () => {
      const markup = renderToStaticMarkup(await HomePage());
      assert.match(markup, /role="alert"/);
      assert.match(markup, /Scenarios could not load/);
      noCards(markup);
    });
  });
}

test("scenario HTTP failure and unreachable backend render visible errors without legacy fallback", async () => {
  for (const response of [
    json({ schema: "experiment_http_error_v1", code: "scenario_unavailable" }, 503),
    async () => { throw new Error("synthetic network failure"); },
    async () => new Response("invalid synthetic JSON"),
  ]) {
    await withFetch(response, async (calls) => {
      const markup = renderToStaticMarkup(await HomePage());
      assert.match(markup, /SCENARIO API UNAVAILABLE/);
      assert.match(markup, /role="alert"/);
      noCards(markup);
      assert.deepEqual(calls.map(c => c.url), ["https://preview.test/api/v1/scenarios"]);
    });
  }
});

test("legacy experiment catalogue and preserved page retain the 409 integrity failure", async () => {
  await withFetch(json({ schema: "experiment_http_error_v1", code: "artifact_integrity_failure" }, 409), async (calls) => {
    await assert.rejects(listExperiments(), (error: unknown) =>
      error instanceof NeuroflyApiError && error.code === "artifact_integrity_failure" && error.status === 409);
    const markup = renderToStaticMarkup(await ExperimentsPage());
    assert.match(markup, /The catalogue could not load/);
    assert.match(markup, /failed integrity validation/);
    assert.match(markup, /role="alert"/);
    assert.ok(calls.every(c => c.url.endsWith("/api/v1/experiments")));
    noCards(markup);
  });
});

test("scenarios page preserves its established presentation and shared navigation", async () => {
  await withFetch(json(fixture()), async (calls) => {
    const markup = renderToStaticMarkup(await ScenariosPage());
    assert.match(markup, /Experiments, not predictions/);
    assert.match(markup, /CANONICAL EXPERIMENTS/);
    assert.equal((markup.match(/class="scenario-card"/g) ?? []).length, 5);
    assert.deepEqual(calls.map(c => c.url), ["https://preview.test/api/v1/scenarios"]);
    assert.equal((await listScenarios()).length, 5);
  });
});

test("scenarios page still rejects empty canonical data as an error", async () => {
  await withFetch(json([]), async () => {
    const markup = renderToStaticMarkup(await ScenariosPage());
    assert.match(markup, /Scenarios could not load/);
    assert.match(markup, /role="alert"/);
    noCards(markup);
  });
});

test("loading remains accessible and legacy detail/cockpit functionality remains available", () => {
  const markup = renderToStaticMarkup(createElement(Loading));
  assert.match(markup, /role="status"/);
  assert.match(markup, /aria-live="polite"/);
  assert.match(markup, /aria-busy="true"/);
  assert.match(markup, /Loading scientific data/);
  noCards(markup);
  const source = (file: string) => readFileSync(new URL(`../src/${file}`, import.meta.url), "utf8");
  assert.doesNotMatch(source("app/page.tsx"), /listExperiments|ExperimentList/);
  assert.match(source("app/experiments/page.tsx"), /listExperiments|ExperimentList/);
  assert.match(source("components/ExperimentList.tsx"), /\/experiments\/\$\{experiment.artifact_id\}\/cockpit/);
  assert.ok(source("app/experiments/[artifactId]/page.tsx"));
  assert.ok(source("app/experiments/[artifactId]/cockpit/page.tsx"));
});
