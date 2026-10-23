import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import HomePage, { metadata } from "../src/app/page";
import Loading from "../src/app/loading";
import ExperimentsPage from "../src/app/experiments/page";
import ScenariosPage, { dynamic as catalogueDynamic } from "../src/app/scenarios/page";
import { listExperiments, NeuroflyApiError } from "../src/lib/neuroflyClient";
import { listScenarios } from "../src/lib/scenarioCatalog";
import { parseScenarioCatalog, SCENARIO_KINDS } from "../src/lib/scenarioPlayback";
import { experimentMetadata } from "../src/lib/scenarioPresentation";
import { existsSync, readdirSync } from "node:fs";
import { LAB_HREF, SITE_LINKS } from "../src/components/site/siteContent";

test("product homepage renders one H1, meaningful sections and the genuine laboratory CTA without fetching scientific data", async () => {
  await withFetch(async () => { throw new Error("Homepage must be independent of the scientific API"); }, async calls => {
    const markup = renderToStaticMarkup(createElement(HomePage));
    assert.equal((markup.match(/<h1\b/g) ?? []).length, 1);
    assert.match(markup, /A digital fly\./);
    assert.match(markup, /explore behaviour\./);
    assert.match(markup, /href="\/visual-lab\/arena"[^>]*>Enter the Lab/);
    for (const id of ["main-content", "about", "explore", "science"]) assert.ok(markup.includes(`id="${id}"`));
    for (const term of ["Environment", "Neural model", "Behaviour", "Replay. Compare.", "Launch the Laboratory", "Enter NeuroFly Lab"]) assert.ok(markup.includes(term));
    assert.match(markup, /<main id="main-content" tabindex="-1"/);
    assert.match(markup, /<noscript><style>/);
    assert.deepEqual(calls, []);
    assert.doesNotMatch(markup, /<canvas|<iframe|<video/);
    assert.equal((markup.match(/class="neurofly-logo"/g) ?? []).length, 2);
    assert.match(markup, /src="\/assets\/brand\/neurofly-logo-white.png"/);
    assert.doesNotMatch(markup, /nf-brand-dot/);
  });
});

test("public links resolve to preserved routes or existing homepage anchors", () => {
  assert.equal(LAB_HREF, "/visual-lab/arena");
  const markup = renderToStaticMarkup(createElement(HomePage));
  // React may emit image preload links; this checks navigation anchors only.
  for (const [, href] of markup.matchAll(/<a\b[^>]*href="([^"?#]*)(?:#([^"]*))?"/g)) {
    if (!href.startsWith("/") && href !== "") continue;
    const route = href || "/";
    assert.ok(existsSync(new URL(`../src/app${route === "/" ? "" : route}/page.tsx`, import.meta.url)), href);
  }
  for (const [, id] of markup.matchAll(/href="(?:\/)?#([^"]+)"/g)) assert.ok(markup.includes(`id="${id}"`));
  assert.deepEqual(SITE_LINKS.map(link => link.label), ["Home", "Lab", "Experiments", "Science"]);
});

test("authentic static laboratory capture is accessible and links to the existing laboratory", () => {
  const markup = renderToStaticMarkup(createElement(HomePage));
  const card = markup.match(/<a[^>]*class="nf-feature-card nf-feature-main"[^>]*>([\s\S]*?)<\/a>/)?.[0];
  assert.ok(card);
  assert.match(card, /href="\/visual-lab\/arena"/);
  assert.match(card, /src="\/assets\/site\/neurofly-lab-preview.webp"/);
  assert.match(card, /width="1294" height="718" loading="lazy"/);
  assert.match(card, /alt="Screenshot of the NeuroFly 3D laboratory/);
  assert.match(card, /Actual Lab viewport/);
  assert.match(card, /Static capture/);
  assert.doesNotMatch(markup, /nf-room-diagram|nf-room-cube/);
  const image = readFileSync(new URL("../public/assets/site/neurofly-lab-preview.webp", import.meta.url));
  assert.equal(image.subarray(8, 12).toString(), "WEBP");
  assert.ok(image.length < 50_000);
});

test("mobile navigation is a native keyboard disclosure and critical links are present in server HTML", () => {
  const markup = renderToStaticMarkup(createElement(HomePage));
  assert.match(markup, /<details class="nf-mobile-menu"><summary>/);
  assert.match(markup, /aria-label="Mobile primary navigation"/);
  assert.match(markup, /Skip to content/);
  assert.match(markup, /aria-current="page"/);
  assert.doesNotMatch(markup, /role="menu"|tabindex="[1-9]/);
});

test("scientific copy distinguishes selected connectivity, modelling and artistic presentation", () => {
  const markup = renderToStaticMarkup(createElement(HomePage));
  for (const phrase of ["MaleCNS", "selected circuits", "not physiological calibration", "not a whole-fly physiological emulation", "artistic 3D asset", "engineering projection"]) assert.ok(markup.includes(phrase), phrase);
  assert.doesNotMatch(markup, /conscious digital|complete digital brain|biologically exact|all 166,000|living fly emulation|real biological learning/i);
  assert.match(markup, /creativecommons.org\/licenses\/by\/4.0/);
  assert.match(markup, /mlykouretzos/);
  assert.match(String(metadata.title), /NeuroFly/);
  assert.ok(metadata.description && metadata.openGraph);
});

test("homepage import tree stays within presentation; no neural or WebGL engine and no speculative route prefetch", () => {
  const paths = [new URL("../src/app/page.tsx", import.meta.url), ...readdirSync(new URL("../src/components/site", import.meta.url)).map(file => new URL(`../src/components/site/${file}`, import.meta.url))];
  for (const path of paths) {
    const code = readFileSync(path, "utf8");
    assert.doesNotMatch(code, /from ["'][^"']*(?:lib\/|three|react-three|FlyViewer|ArenaCourseViewer)|requestAnimationFrame|setInterval|useEffect|fetch\(/);
    for (const tag of code.matchAll(/<Link\s[^>]+>/g)) assert.match(tag[0], /prefetch=\{false\}/);
  }
  const asset = readFileSync(new URL("../public/assets/site/fly-specimen.webp", import.meta.url));
  assert.ok(asset.length < 220_000);
  assert.equal(asset.subarray(8, 12).toString(), "WEBP");
});

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

test("preserved catalogue route requests the genuine catalogue contract and renders five accessible scenario links", async () => {
  const payload = fixture();
  assert.equal(parseScenarioCatalog(payload).length, 5);
  await withFetch(json(payload), async (calls) => {
    const markup = renderToStaticMarkup(await ScenariosPage());
    assert.equal(catalogueDynamic, "force-dynamic");
    assert.deepEqual(calls.map(c => c.url), ["https://preview.test/api/v1/scenarios"]);
    assert.equal(calls[0].options?.cache, "no-store");
    assert.match(markup, /Experiments, not predictions/);
    assert.match(markup, /CANONICAL EXPERIMENTS/);
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

test("catalogue route titles come from the response, not a hardcoded successful catalogue", async () => {
  const payload = fixture(); payload[0].title = "Different authoritative title";
  await withFetch(json(payload), async () => {
    const markup = renderToStaticMarkup(await ScenariosPage());
    assert.match(markup, /Different authoritative title/);
    assert.doesNotMatch(markup, /Fixture BASELINE_CONTROL/);
  });
});

test("empty catalogue is explicit absence, never a valid fabricated canonical set", async () => {
  assert.throws(() => parseScenarioCatalog([]));
  await withFetch(json([]), async () => {
    const markup = renderToStaticMarkup(await ScenariosPage());
    assert.match(markup, /Scenarios could not load/);
    assert.match(markup, /role="alert"/);
    noCards(markup);
  });
});

for (const [label, payload] of [
  ["incomplete", fixture().slice(0, 4)],
  ["missing metadata", fixture().map((row, i) => i ? row : { id: row.id })],
  ["wrong classification", fixture().map((row, i) => i ? row : { ...row, preset_only: false })],
  ["wrong shape", { scenarios: fixture() }],
] as const) {
  test(`catalogue route rejects ${label} catalogue without substitution`, async () => {
    await withFetch(json(payload), async () => {
      const markup = renderToStaticMarkup(await ScenariosPage());
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
      const markup = renderToStaticMarkup(await ScenariosPage());
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
