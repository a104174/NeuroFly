import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { register } from "node:module";
// Node cannot import CSS Modules. Register the test-only hook before the components load, so the
// imports that reach CSS are dynamic. (package.json is frozen, so this cannot be an npm script.)
register(new URL("./support/css-hooks.mjs", import.meta.url));
const { default: HomePage, metadata } = await import("../src/app/page");
const { default: Loading } = await import("../src/app/morphology/loading");
const { default: ExperimentsPage } = await import("../src/app/experiments/page");
const { default: ScenariosPage, dynamic: catalogueDynamic } = await import("../src/app/scenarios/page");
import { listExperiments, NeuroflyApiError } from "../src/lib/neuroflyClient";
import { listScenarios } from "../src/lib/scenarioCatalog";
import { parseScenarioCatalog, SCENARIO_KINDS } from "../src/lib/scenarioPlayback";
import { experimentMetadata } from "../src/lib/scenarioPresentation";
import { existsSync, readdirSync } from "node:fs";
import { LAB_HREF, SITE_LINKS } from "../src/components/site/siteContent";
const { SiteHeader } = await import("../src/components/site/SiteChrome");

test("product homepage renders one H1, the owner's headline and statement, and a genuine path to the scenarios, without fetching scientific data", async () => {
  await withFetch(async () => { throw new Error("Homepage must be independent of the scientific API"); }, async calls => {
    const markup = renderToStaticMarkup(createElement(HomePage));
    assert.equal((markup.match(/<h1\b/g) ?? []).length, 1);
    assert.match(markup, /<h1[^>]*>Selected fruit fly circuits, modelled from the connectome\.<\/h1>/);
    assert.match(markup, /NeuroFly is a research model of selected fruit fly neural circuits, built from the MaleCNS connectome and connected to a simplified simulated body\./);
    assert.match(markup, /Research project/);
    // The primary action opens one recorded run, ready to play with no setup.
    assert.match(markup, /href="\/scenarios\/LOOMING_CIRCUIT_VALIDATION\?replay=canonical"[^>]*>Watch the looming scenario/);
    assert.match(markup, /href="\/science\/status"[^>]*>How much of this is real\?/);
    assert.match(markup, /href="\/visual-lab\/arena"[^>]*>Explore the Lab/);
    assert.match(markup, /<main id="main-content" tabindex="-1"/);
    assert.match(markup, /<noscript><style>/);
    assert.deepEqual(calls, []);
    assert.doesNotMatch(markup, /<canvas|<iframe|<video/);
    assert.equal((markup.match(/class="neurofly-logo"/g) ?? []).length, 2);
    assert.match(markup, /src="\/assets\/brand\/neurofly-logo-white.png"/);
    assert.doesNotMatch(markup, /nf-brand-dot/);
  });
});

test("the status strip states scope and status as real text, with the owner's wording and no summed count", () => {
  const markup = renderToStaticMarkup(createElement(HomePage));
  const strip = markup.match(/<section class="strip" aria-label="Scope and status">[\s\S]*?<\/section>/)![0];
  assert.equal((strip.match(/<li\b/g) ?? []).length, 4);
  for (const fact of ["Two selected circuits: looming (313 bodies) and HS → DNp15 (8 bodies). Not a whole brain.", "Wiring from MaleCNS v1.0", "Kinematic body, no muscle or wing physics", "Not yet evaluated against real flies"]) assert.ok(strip.includes(fact), fact);
  assert.doesNotMatch(strip, /\b321\b/);
  // Each fact carries its kind as a named glyph, so the kind does not depend on colour.
  for (const kind of ["Structural", "Model assumption", "Not evaluated"]) assert.ok(strip.includes(`aria-label="${kind}"`), kind);
  // The strip comes directly after the hero.
  assert.ok(markup.indexOf('aria-labelledby="home-title"') < markup.indexOf('aria-label="Scope and status"'));
  assert.ok(markup.indexOf('aria-label="Scope and status"') < markup.indexOf('id="layers-title"'));
});

test("the hero poster is the eager, high-priority image and is described as an artistic model", () => {
  const markup = renderToStaticMarkup(createElement(HomePage));
  const poster = markup.match(/<img[^>]*src="\/assets\/site\/fly-specimen.webp"[^>]*>/)![0];
  assert.match(poster, /fetchPriority="high"/);
  assert.match(poster, /loading="eager"/);
  assert.match(poster, /width="1500" height="1400"/);
  assert.match(poster, /alt="Three-quarter render[^"]*not a reconstruction of the connectome\."/);
  assert.match(markup, /artistic 3D asset, not anatomy reconstructed from MaleCNS/);
  for (const file of ["fly-specimen.webp", "fly-specimen-small.webp"]) assert.ok(existsSync(new URL(`../public/assets/site/${file}`, import.meta.url)), file);
});

test("public links resolve to preserved routes or existing homepage anchors", () => {
  assert.equal(LAB_HREF, "/visual-lab/arena");
  const markup = renderToStaticMarkup(createElement(HomePage));
  // React may emit image preload links; this checks navigation anchors only.
  for (const [, href] of markup.matchAll(/<a\b[^>]*href="([^"?#]*)(?:#([^"]*))?"/g)) {
    if (!href.startsWith("/") && href !== "") continue;
    const route = href.startsWith("/scenarios/") ? "/scenarios/[scenarioId]" : href || "/";
    assert.ok(existsSync(new URL(`../src/app${route === "/" ? "" : route}/page.tsx`, import.meta.url)), href);
  }
  for (const [, id] of markup.matchAll(/href="(?:\/)?#([^"]+)"/g)) assert.ok(markup.includes(`id="${id}"`));
  // Phase 0 decision 5: Home is the logo, and Experiments leaves the main navigation.
  assert.deepEqual(SITE_LINKS.map(link => link.label), ["Scenarios", "Neurons", "Lab", "Science"]);
});

test("authentic static laboratory capture is accessible, labelled as running in the browser, and links to the existing laboratory", () => {
  const markup = renderToStaticMarkup(createElement(HomePage));
  const card = markup.match(/<li class="card"><p class="cardKind">Lab<\/p>[\s\S]*?<\/li>/)?.[0];
  assert.ok(card);
  assert.match(card, /href="\/visual-lab\/arena"/);
  assert.match(card, /src="\/assets\/site\/neurofly-lab-preview.webp"/);
  assert.match(card, /width="1294" height="718" loading="lazy"/);
  assert.match(card, /alt="Screenshot of the NeuroFly 3D laboratory/);
  assert.match(card, /Actual Lab viewport/);
  assert.match(card, /static capture/);
  // Owner decision 2: the Lab says it runs in the browser, and is never called Replay.
  assert.match(card, /Runs in your browser/);
  assert.match(card, /no muscle or wing physics/);
  assert.doesNotMatch(card, /replay/i);
  assert.doesNotMatch(markup, /nf-room-diagram|nf-room-cube/);
  const image = readFileSync(new URL("../public/assets/site/neurofly-lab-preview.webp", import.meta.url));
  assert.equal(image.subarray(8, 12).toString(), "WEBP");
  assert.ok(image.length < 50_000);
});

test("mobile navigation is a native keyboard disclosure and critical links are present in server HTML", () => {
  const markup = renderToStaticMarkup(createElement(HomePage));
  assert.match(markup, /<details class="menu"><summary class="menuButton">/);
  assert.match(markup, /aria-label="Mobile primary navigation"/);
  assert.match(markup, /Skip to content/);
  // Home is the logo, so no primary item is current there; a section page marks exactly its own item.
  assert.doesNotMatch(markup, /aria-current="page"/);
  const scenarios = renderToStaticMarkup(createElement(SiteHeader, { current: "/scenarios/LOOMING_CIRCUIT_VALIDATION" }));
  assert.equal((scenarios.match(/aria-current="page"/g) ?? []).length, 2, "one desktop link and one mobile link");
  assert.match(scenarios, /aria-current="page"[^>]*href="\/scenarios"|href="\/scenarios"[^>]*aria-current="page"/);
  const experiments = renderToStaticMarkup(createElement(SiteHeader, { current: "/experiments/abc" }));
  assert.doesNotMatch(experiments, /aria-current="page"/, "Experiments is not a primary item");
  assert.doesNotMatch(markup, /role="menu"|tabindex="[1-9]/);
});

test("scientific copy distinguishes wiring, modelling and output, and keeps every disclosure visible", () => {
  const markup = renderToStaticMarkup(createElement(HomePage));
  const body = markup.replace(/<style[\s\S]*?<\/style>/g, " ").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/\s+/g, " ");
  for (const phrase of ["MaleCNS", "Two selected circuits", "Not a whole brain", "Not yet evaluated against real flies", "artistic 3D asset", "no muscle or wing physics", "Three layers, kept apart", "chosen for the model, not measured from the fly", "not a measurement from a fly", "wiring, not signal strength"]) assert.ok(body.includes(phrase), phrase);
  // The three layers carry their kinds as labelled badges.
  const layers = markup.match(/<ol class="layers">[\s\S]*?<\/ol>/)![0];
  for (const kind of ["structural", "model-assumption", "model-state"]) assert.ok(layers.includes(`data-kind="${kind}"`), kind);
  // Retired and overclaiming wording stays out of the interface.
  assert.doesNotMatch(body, /digital (organism|fly)|conscious digital|complete digital brain|biologically exact|bio-?accurate|all 166,000|living fly emulation|real biological learning|\bverified\b|\bvalidation\b/i);
  assert.doesNotMatch(body, /(?:^|[\s(])(?:m|µ)V(?![\w_])|\bHz\b|firing rate/);
  assert.match(markup, /creativecommons.org\/licenses\/by\/4.0/);
  assert.match(markup, /mlykouretzos/);
});

test("the gallery lists three canonical scenarios and the Lab, each with one stretched link and real durations", () => {
  const markup = renderToStaticMarkup(createElement(HomePage));
  const gallery = markup.match(/<ul class="gallery">[\s\S]*?<\/ul>/)![0];
  assert.equal((gallery.match(/<li class="card">/g) ?? []).length, 4);
  assert.equal((gallery.match(/<a\b/g) ?? []).length, 4, "one link per card");
  for (const id of ["LOOMING_CIRCUIT_VALIDATION", "HORIZONTAL_MOTION_NEURAL_VALIDATION", "EXPLORATORY_COURSE_CONTROL"] as const) {
    assert.ok(gallery.includes(`href="/scenarios/${id}"`), id);
    assert.ok(gallery.includes(experimentMetadata[id].duration), id);
    assert.ok(SCENARIO_KINDS.some(kind => kind === id), id);
  }
  assert.doesNotMatch(gallery, /Neural-only validation/);
});

test("homepage import tree stays within presentation; no neural or WebGL engine and no speculative route prefetch", () => {
  const paths = [new URL("../src/app/page.tsx", import.meta.url), ...readdirSync(new URL("../src/components/site", import.meta.url)).map(file => new URL(`../src/components/site/${file}`, import.meta.url))];
  for (const path of paths) {
    const code = readFileSync(path, "utf8");
    // Engines, WebGL, animation loops, data fetching and unprefetched links stay forbidden everywhere.
    // Only the shared chrome may use useEffect (menu focus, route focus) and the tiny theme helper.
    // Allowed under lib/: the theme helper and scenarioPresentation (display data only), plus type-only imports.
    const runtime = code.replace(/^import type .*$/gm, "");
    assert.doesNotMatch(runtime, /from ["'][^"']*(?:lib\/(?!(?:theme|scenarioPresentation)["'])|three|react-three|FlyViewer|ArenaCourseViewer)|requestAnimationFrame|setInterval|fetch\(/);
    const mayUseEffect = ["SiteNavigation.tsx", "RouteFocus.tsx"].some(name => path.pathname.endsWith(`/site/${name}`));
    if (!mayUseEffect) assert.doesNotMatch(code, /useEffect/);
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
  assert.doesNotMatch(markup, /class="discovery-card discovery-card--|Canonical replay available/);
}

test("preserved catalogue route requests the genuine catalogue contract and renders five accessible scenario links", async () => {
  const payload = fixture();
  assert.equal(parseScenarioCatalog(payload).length, 5);
  await withFetch(json(payload), async (calls) => {
    const markup = renderToStaticMarkup(await ScenariosPage());
    assert.equal(catalogueDynamic, "force-dynamic");
    assert.deepEqual(calls.map(c => c.url), ["https://preview.test/api/v1/scenarios"]);
    assert.equal(calls[0].options?.cache, "no-store");
    assert.match(markup, /Explore the/);
    assert.match(markup, /Look beneath the behaviour/);
    assert.equal((markup.match(/class="discovery-card discovery-card--/g) ?? []).length, 5);
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

test("recorded experiment page preserves the 409 integrity failure without replacement results", async () => {
  await withFetch(json({ schema: "experiment_http_error_v1", code: "artifact_integrity_failure" }, 409), async (calls) => {
    await assert.rejects(listExperiments(), (error: unknown) =>
      error instanceof NeuroflyApiError && error.code === "artifact_integrity_failure" && error.status === 409);
    const markup = renderToStaticMarkup(await ExperimentsPage());
    assert.match(markup, /Recorded experiments are temporarily unavailable/);
    assert.match(markup, /The current experiment archive could not be verified/);
    assert.match(markup, /Technical details/);
    assert.match(markup, /failed integrity validation/);
    assert.match(markup, /role="alert"/);
    assert.ok(calls.every(c => c.url.endsWith("/api/v1/experiments")));
    noCards(markup);
  });
});

test("scenarios page preserves its established presentation and shared navigation", async () => {
  await withFetch(json(fixture()), async (calls) => {
    const markup = renderToStaticMarkup(await ScenariosPage());
    assert.match(markup, /Explore the/);
    assert.match(markup, /Look beneath the behaviour/);
    assert.equal((markup.match(/class="discovery-card discovery-card--/g) ?? []).length, 5);
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
  // The fallback belongs to the routes that load data (Neurons). A root fallback would wrap every page,
  // including the static Home, and delay its first paint behind a "Loading scientific data" screen.
  assert.equal(existsSync(new URL("../src/app/loading.tsx", import.meta.url)), false);
  for (const route of ["morphology", "scenarios", "experiments", "experiments/[artifactId]", "scenarios/[scenarioId]"]) assert.ok(existsSync(new URL(`../src/app/${route}/loading.tsx`, import.meta.url)), route);
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
