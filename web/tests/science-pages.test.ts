import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { register } from "node:module";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  CAPABILITIES,
  CAPABILITY_GROUPS,
  GLOSSARY,
  GLOSSARY_GROUPS,
  KIND_COPY,
  OPEN_QUESTIONS,
  RETIRED_TERMS,
  isBiologicalUnit,
} from "../src/content/science-copy";
import { STATUS_HREF } from "../src/components/site/siteContent";

// Node cannot import CSS Modules; see tests/support/css-hooks.mjs.
register(new URL("./support/css-hooks.mjs", import.meta.url));
const { default: SciencePage } = await import("../src/app/science/page");
const { default: StatusPage } = await import("../src/app/science/status/page");
const { default: GlossaryPage } = await import("../src/app/science/glossary/page");

const root = new URL("../../", import.meta.url);
const pages = { science: () => renderToStaticMarkup(createElement(SciencePage)), status: () => renderToStaticMarkup(createElement(StatusPage)), glossary: () => renderToStaticMarkup(createElement(GlossaryPage)) };
const text = (html: string) => html.replace(/<style[\s\S]*?<\/style>/g, " ").replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/&#x27;/g, "'").replace(/\s+/g, " ");

test("every capability cites an existing repository report and states a reason", () => {
  assert.equal(new Set(CAPABILITIES.map((c) => c.id)).size, CAPABILITIES.length);
  for (const capability of CAPABILITIES) {
    assert.ok(existsSync(new URL(capability.source.path, root)), `${capability.id}: ${capability.source.path}`);
    assert.ok(capability.reason.length > 40, capability.id);
    assert.ok(capability.name && capability.source.label);
  }
  for (const group of Object.keys(CAPABILITY_GROUPS)) assert.ok(CAPABILITIES.some((c) => c.group === group), `empty group ${group}`);
});

test("capabilities that are off are neutral kinds, never errors, and say why", () => {
  for (const capability of CAPABILITIES.filter((c) => c.group === "not-available")) {
    assert.ok(["unavailable", "not-evaluated"].includes(capability.kind), capability.id);
    assert.doesNotMatch(capability.reason, /\b(error|fault|broken|bug|failed)\b/i, capability.id);
  }
  const levelC = CAPABILITIES.find((c) => c.id === "level-c")!;
  assert.match(levelC.reason, /No validated mapping from a world object to MaleCNS columns exists/);
  const source = readFileSync(new URL(levelC.source.path, root), "utf8");
  assert.match(source, /no validated world-object → MaleCNS column mapping currently exists/);
});

test("the Lab capability states exactly what was compared and at what tolerance", () => {
  const lab = CAPABILITIES.find((c) => c.id === "lab")!;
  assert.match(lab.reason, /^Runs in your browser\./);
  assert.match(lab.reason, /recorded Python run/);
  assert.match(lab.reason, /1e-8/);
  assert.match(lab.reason, /eight seconds/);
  assert.doesNotMatch(lab.reason, /replay/i, "the Lab is never called Replay");
  assert.match(readFileSync(new URL(lab.source.path, root), "utf8"), /Absolute parity tolerance is 1e-8/);
});

test("the Status page lists every capability in a captioned table with a source link", () => {
  const html = pages.status();
  assert.equal((html.match(/<h1\b/g) ?? []).length, 1);
  assert.match(html, /<h1[^>]*>Status and limits<\/h1>/);
  assert.equal((html.match(/<table\b/g) ?? []).length, 3);
  assert.equal((html.match(/<caption>/g) ?? []).length, 3);
  assert.equal((html.match(/<th scope="row">/g) ?? []).length, CAPABILITIES.length);
  for (const capability of CAPABILITIES) {
    assert.ok(html.includes(`id="${capability.id}"`), capability.id);
    assert.ok(html.includes(`https://github.com/a104174/NeuroFly/blob/main/${capability.source.path}`), capability.id);
  }
  assert.match(html, /data-claim="capabilities"/);
  assert.ok(html.includes("Not available yet"));
});

test("the header status pill points at the Status page, and that route exists", () => {
  assert.equal(STATUS_HREF, "/science/status");
  assert.ok(existsSync(new URL("web/src/app/science/status/page.tsx", root)));
  assert.match(pages.science(), /href="\/science\/status"/);
});

test("the Glossary defines the five core objects and the five kinds with stable anchors", () => {
  const html = pages.glossary();
  for (const term of ["Scenario", "Run", "Experiment", "Artifact", "Cockpit"]) assert.ok(GLOSSARY.some((e) => e.term === term && e.group === "objects"), term);
  for (const kind of Object.values(KIND_COPY)) assert.ok(GLOSSARY.some((e) => e.term === kind.label), kind.label);
  assert.equal(new Set(GLOSSARY.map((e) => e.id)).size, GLOSSARY.length);
  for (const entry of GLOSSARY) {
    assert.ok(html.includes(`id="${entry.id}"`), entry.id);
    assert.ok(html.includes(`href="#${entry.id}"`), entry.id);
  }
  assert.equal((html.match(/<dl\b/g) ?? []).length, Object.keys(GLOSSARY_GROUPS).length);
  const body = GLOSSARY.find((e) => e.id === "body")!.meaning;
  assert.match(body, /313 bodies: 126 LC4, 185 LPLC2 and 2 DNp01/);
  assert.match(GLOSSARY.find((e) => e.id === "lif")!.meaning, /HS to DNp15 path uses continuous proxy states and defines no spikes/);
});

test("the Science page states both circuits without adding their counts", () => {
  const body = text(pages.science());
  assert.match(body, /looming circuit[^.]*\(313 bodies\)/);
  assert.match(body, /HS → DNp15 steering circuit \(8 bodies\)/);
  assert.match(body, /not added together/);
  assert.match(body, /Neither is a whole brain/);
  assert.doesNotMatch(body, /\b321\b/);
  assert.equal(OPEN_QUESTIONS.length, 8);
});

test("all three pages are migrated: themed, one landmark, skip link, contents, and no data fetching", () => {
  const previous = globalThis.fetch;
  let calls = 0;
  globalThis.fetch = async () => { calls++; throw new Error("no network"); };
  try {
    for (const [name, render] of Object.entries(pages)) {
      const html = render();
      assert.equal((html.match(/<h1\b/g) ?? []).length, 1, name);
      assert.equal((html.match(/<main\b/g) ?? []).length, 1, name);
      assert.match(html, /<main id="main-content" tabindex="-1"/, name);
      assert.match(html, /href="#main-content">Skip to content/, name);
      assert.match(html, /<div data-themed-page="true"/, name);
      // The chrome follows the theme (only the 3D stage figures are pinned dark, on purpose).
      assert.doesNotMatch(html, /<(?:header|footer) class="(?:header|footer)"[^>]*data-theme-scope/, `${name} follows the theme`);
      assert.match(html, /aria-label="Colour theme"/, `${name} shows the theme switch`);
      assert.match(html, /aria-current="page"[^>]*href="\/science"|href="\/science"[^>]*aria-current="page"/, name);
      const contents = html.match(/<nav[^>]*aria-label="On this page"[\s\S]*?<\/nav>/)![0];
      const targets = [...contents.matchAll(/href="#([^"]+)"/g)].map((m) => m[1]);
      assert.ok(targets.length >= 3, name);
      for (const id of targets) assert.ok(html.includes(`id="${id}"`), `${name}: #${id}`);
      assert.doesNotMatch(html, /<canvas|<iframe|<video/, `${name} has no 3D dependency`);
    }
    assert.equal(calls, 0);
  } finally { globalThis.fetch = previous; }
});

test("no retired term, biological unit or digital-organism claim appears in the rendered text", () => {
  for (const [name, render] of Object.entries(pages)) {
    const body = text(render());
    for (const { term } of RETIRED_TERMS) assert.doesNotMatch(body, term, `${name}: ${term}`);
    // A bare mV, µV, Hz or spikes/s would present model output as a measurement. mV_eq is allowed.
    assert.doesNotMatch(body, /(?:^|[\s(])(?:\d[\d.]*\s*)?(?:m|µ|n|p)?V(?![\w_])|\b[kK]?Hz\b|spikes?\s*\/\s*s/, `${name}: bare biological unit`);
    assert.equal(isBiologicalUnit("mV"), true);
    assert.doesNotMatch(body, /✓|✔|accuracy|biologically (exact|accurate)/i, name);
  }
});

test("the old Science stylesheet and layout are gone and nothing imports them", () => {
  assert.equal(existsSync(new URL("web/src/app/science/science.css", root)), false);
  assert.equal(existsSync(new URL("web/src/app/science/layout.tsx", root)), false);
  const css = readFileSync(new URL("web/src/components/science/Article.module.css", root), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  assert.doesNotMatch(css, /#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(/, "Article.module.css hard-codes a colour");
});

test("the allowed use of \"validation\" is only the explanation that a circuit check is not biological validation", () => {
  const rule = RETIRED_TERMS.find(({ term }) => term.source.includes("validation"))!.term;
  assert.equal(rule.test("The circuit check is not biological validation."), false);
  assert.equal(rule.test("Neural-only validation"), true);
  assert.equal(rule.test("Looming Circuit Validation"), true);
  assert.match(text(pages.science()), /not biological validation/);
});
