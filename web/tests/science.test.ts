import assert from "node:assert/strict";
import test from "node:test";
import { existsSync, readFileSync } from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { register } from "node:module";
// Node cannot import CSS Modules. Register the test-only hook before the components load, so the
// imports that reach CSS are dynamic. (package.json is frozen, so this cannot be an npm script.)
register(new URL("./support/css-hooks.mjs", import.meta.url));
const { default: SciencePage, metadata } = await import("../src/app/science/page");
const { default: HomePage } = await import("../src/app/page");
const { ScienceArchitecture } = await import("../src/components/science/ScienceArchitecture");
import { SCENARIO_KINDS } from "../src/lib/scenarioPlayback";
import { experimentMetadata } from "../src/lib/scenarioPresentation";
import { SITE_LINKS } from "../src/components/site/siteContent";

const render = () => renderToStaticMarkup(createElement(SciencePage));
const root = new URL("../../", import.meta.url);
const read = (path: string) => readFileSync(new URL(path, root), "utf8");

test("Science is a static independent explanation even when every scientific request would fail", () => {
  const previous = globalThis.fetch;
  let calls = 0;
  globalThis.fetch = async () => { calls++; throw new Error("Scientific API unavailable / 409"); };
  try {
    const html = render();
    assert.equal(calls, 0);
    assert.equal((html.match(/<h1\b/g) || []).length, 1);
    assert.match(html, /The science behind/);
    assert.match(html, /<main id="main-content" tabindex="-1"/);
    assert.match(html, /href="#main-content">Skip to content/);
    assert.match(String(metadata.title), /Science · NeuroFly/);
    assert.ok(metadata.description && metadata.openGraph);
    assert.doesNotMatch(html, /<canvas|<iframe|<video|data-live-/);
  } finally { globalThis.fetch = previous; }
});

test("Science navigation resolves without removing homepage anchors or promoting the recorded archive", () => {
  const html = render(), home = renderToStaticMarkup(createElement(HomePage));
  assert.equal(SITE_LINKS.find(link => link.label === "Science")?.href, "/science");
  // The redesigned Home has no Science teaser section; Science stays reachable from the header,
  // the footer and the "How much of this is real?" action, and the recorded run is not promoted.
  assert.match(home, /href="\/science\/status"[^>]*>How much of this is real\?/);
  assert.match(home, /<nav aria-label="Footer navigation"[^>]*>[\s\S]*href="\/science">Science<\/a>/);
  assert.doesNotMatch(home.match(/<nav[^>]*aria-label="Primary navigation"[\s\S]*?<\/nav>/)![0], /href="\/experiments"/);
  const primary = html.match(/<nav[^>]*aria-label="Primary navigation"[\s\S]*?<\/nav>/)![0];
  assert.match(primary, /aria-current="page" href="\/science"|href="\/science"[^>]*aria-current="page"/);
  assert.doesNotMatch(primary, /href="\/experiments"/);
  assert.match(html, /href="\/experiments">Engineering test, not a scientific experiment/);
  for (const [, href] of html.matchAll(/<a\b[^>]*href="([^"]+)"/g)) {
    if (href.startsWith("#")) assert(html.includes(`id="${href.slice(1)}"`), href);
    else if (href.startsWith("/")) {
      const path = href.startsWith("/scenarios/") ? "/scenarios/[scenarioId]" : href;
      assert(existsSync(new URL(`web/src/app${path === "/" ? "" : path}/page.tsx`, root)) || existsSync(new URL(`web/src/app${path}/(list)/page.tsx`, root)), href);
    }
  }
  for (const href of ["/visual-lab/arena", "/scenarios", "/visual-lab/arena/research"]) assert(html.includes(`href="${href}"`));
});

test("Science provides a route-scoped no-JavaScript reveal for the inherited root loading boundary", () => {
  const html = render();
  const fallback = html.match(/<noscript>[\s\S]*?<\/noscript>/)?.[0];
  assert.ok(fallback);
  assert.match(fallback, /body > \[hidden\]:has\(> \[data-themed-page\]\)/);
  assert.match(fallback, /display: block !important/);
  assert.match(fallback, /body:has\(> \[hidden\] > \[data-themed-page\]\) > \.app-shell/);
  assert.match(fallback, /display: none !important/);
  assert.doesNotMatch(fallback, /fetch|api\/|\.lab-shell/);
});

test("the architecture presents structural evidence outside an ordered runtime loop with explicit engineering roles", () => {
  const html = renderToStaticMarkup(createElement(ScienceArchitecture));
  const stages = html.match(/<ol class="stages"[\s\S]*?<\/ol>/)![0];
  assert.equal((stages.match(/<li\b/g) || []).length, 4);
  assert(stages.indexOf("Observe") < stages.indexOf("Compute"));
  assert(stages.indexOf("Compute") < stages.indexOf("Turn"));
  assert(stages.indexOf("Turn") < stages.indexOf("Move"));
  assert.doesNotMatch(stages, /Biological source/);
  assert.match(html, /<figure[^>]*aria-labelledby="architecture-caption"/);
  assert.match(html, /<figcaption id="architecture-caption">Conceptual architecture diagram/);
  assert.match(html, /Engineering projection/);
  assert.match(html, /Engineering body/);
  assert.match(html, /completed movement interval/);
  assert.match(html, /Rendered pixels do not drive this observer/);
});

test("every public claim group maps to a reviewed evidence row and existing implementation sources", () => {
  const html = render(), evidence = read("docs/architecture/product_experience_v10_3b.md");
  const ids = new Set([...html.matchAll(/data-claim="([^"]+)"/g)].map(match => match[1]));
  // 17 reviewed groups, plus scope, kinds, open and circuitcheck (evidence rows added with the phase 4 redesign).
  assert.equal(ids.size, 21);
  for (const id of ids) assert(evidence.includes(`| ${id}:`), id);
  for (const source of ["src/neurofly/hs_dnp15_neural_validation.py", "web/src/lib/interactiveNeuralLocomotion.ts", "web/src/lib/articulatedGait.ts", "docs/science/empirical_hs_dnp15_response_benchmark_v9_2.md", "docs/science/experiment_artifact_contract.md"]) {
    assert(evidence.includes(source));
    assert(existsSync(new URL(source, root)), source);
  }
  for (const boundary of ["dimensionless proxy states", "not measured membrane voltages", "engineering yaw projection", "does not generate propulsion", "shadow-only status", "contract-only", "not a complete biological reconstruction"]) assert(html.includes(boundary), boundary);
  assert.match(html, /not evidence of consciousness, sentience or genuine learning/);
  assert.doesNotMatch(html, /biologically exact|fully simulated brain|proven consciousness|all neurons running|measured neural trace/i);
});

test("experiment examples preserve real scenario IDs and scientific durations without executing playback", () => {
  const html = render();
  const examples = html.match(/<ul class="examples">[\s\S]*?<\/ul>/)![0];
  const links = [...examples.matchAll(/href="\/scenarios\/([A-Z_]+)"/g)].map(match => match[1]);
  assert.equal(links.length, 3);
  for (const id of links) {
    assert(SCENARIO_KINDS.some(kind => kind === id), id);
    assert(examples.includes(experimentMetadata[id as keyof typeof experimentMetadata].duration));
  }
  assert.match(examples, /No translation is simulated/);
  assert.match(examples, /defines no body mapping/);
  assert.match(html, /millisecond scientific timelines are distinct from the Lab/);
  assert.doesNotMatch(examples, /data-run-id|data-result|<output|<canvas/);
});

test("references are primary sources or existing repository reports, and assets keep authentic attribution", () => {
  const html = render();
  const refs = html.match(/<ol class="references">[\s\S]*?<\/ol>/)![0];
  for (const [, href] of refs.matchAll(/href="([^"]+)"/g)) {
    const url = new URL(href);
    assert.equal(url.protocol, "https:");
    assert(["male-cns.janelia.org", "www.nature.com", "github.com"].includes(url.hostname));
    if (url.hostname === "github.com") {
      assert(url.pathname.startsWith("/a104174/NeuroFly/blob/main/"));
      assert(existsSync(new URL(url.pathname.replace("/a104174/NeuroFly/blob/main/", ""), root)));
    }
  }
  assert.match(html, /background, not evidence that the model matches real flies/);
  for (const asset of ["fly-specimen.webp", "neurofly-lab-preview.webp"]) {
    assert(html.includes(asset));
    assert(existsSync(new URL("web/public/assets/site/" + asset, root)));
  }
  assert.match(html, /alt="Three-quarter render/);
  assert.match(html, /alt="Screenshot of the NeuroFly 3D laboratory/);
  assert.match(html, /artistic 3D asset/);
  assert.match(html, /mlykouretzos/);
  assert.match(html, /creativecommons.org\/licenses\/by\/4.0/);
  assert.equal((html.match(/src="\/assets\/brand\/neurofly-logo-white.png"/g) || []).length, 2);
  assert.doesNotMatch(html, /\/home\/|\/tmp\//);
});

test("presentation boundaries remain lightweight and native navigation and disclosures retain accessibility", () => {
  const html = render();
  assert.match(html, /<details class="menu"><summary class="menuButton">/);
  assert.match(html, /aria-label="Mobile primary navigation"/);
  assert.match(html, /<details class="disclosure"><summary>/);
  assert.doesNotMatch(html, /role="menu"|tabindex="[1-9]/);
  for (const path of ["web/src/app/science/page.tsx", "web/src/app/science/status/page.tsx", "web/src/app/science/glossary/page.tsx", "web/src/components/science/ScienceArchitecture.tsx", "web/src/components/science/ArticleShell.tsx"]) {
    const source = read(path);
    assert.doesNotMatch(source, /useEffect|requestAnimationFrame|setInterval|fetch\(|new .*Engine|from ["'][^"']*(?:three|neuroflyClient|NeuralEngine|neuralFlight|continuousArena)/);
    for (const link of source.matchAll(/<Link\s[^>]+>/g)) assert.match(link[0], /prefetch=\{false\}/);
  }
  // Reduced motion is a global token override (tests/tokens.test.ts); the article adds no animation of its own.
  const css = read("web/src/components/science/Article.module.css");
  assert.doesNotMatch(css, /@keyframes|animation:/);
  assert.match(css, /@media \(min-width: 1024px\)/);
  assert.match(read("web/src/app/product.css"), /:focus-visible/);
  assert.match(read("web/src/components/site/SiteNavigation.tsx"), /Escape/);
});
