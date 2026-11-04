import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import test from "node:test";
import { register } from "node:module";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  DATA_KINDS,
  KIND_COPY,
  RETIRED_TERMS,
  STATE_COPY,
  UNIT_COPY,
  isBiologicalUnit,
  statusLabel,
  type DataKind,
} from "../src/content/science-copy";

// Node cannot import CSS Modules. Register a test-only hook first, then import the components
// dynamically (static imports would be loaded before the hook exists). package.json is frozen by
// the contribution protocol, so this lives in the test, not in an npm script.
register("./support/css-hooks.mjs", import.meta.url);
const { KindBadge, KindGlyph, ProvenanceLabel, Readout, StatePanel, Tooltip } = await import("../src/components/ui");

const html = (node: Parameters<typeof renderToStaticMarkup>[0]) => renderToStaticMarkup(node);
const text = (markup: string) => markup.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();

test("every kind has a label, a tooltip and a distinct glyph shape", () => {
  const shapes = new Set<string>();
  for (const kind of DATA_KINDS) {
    assert.ok(KIND_COPY[kind].label && KIND_COPY[kind].tooltip);
    shapes.add(html(h(KindGlyph, { kind })));
  }
  assert.equal(shapes.size, DATA_KINDS.length, "glyph markup must differ for every kind");
  assert.equal(new Set(DATA_KINDS.map((k) => KIND_COPY[k].glyph)).size, DATA_KINDS.length);
});

test("kind labels and tooltips follow the Phase 0 decisions", () => {
  assert.equal(KIND_COPY.unavailable.label, "Not available yet");
  assert.match(KIND_COPY["model-state"].tooltip, /model units/);
  assert.doesNotMatch(KIND_COPY["model-state"].tooltip, /dimensionless/);
  assert.match(KIND_COPY.structural.tooltip, /not signal strength/);
  assert.match(KIND_COPY["not-evaluated"].tooltip, /not a failure/i);
  assert.equal(UNIT_COPY.modelEquivalentNote, "model-equivalent, not measured");
});

test("KindBadge shows glyph and text together, and glyph-only keeps an accessible name", () => {
  for (const kind of DATA_KINDS) {
    const full = html(h(KindBadge, { kind }));
    assert.ok(full.includes(KIND_COPY[kind].label));
    assert.ok(full.includes(`data-kind="${kind}"`));
    assert.ok(full.includes("<svg"));
    const glyph = html(h(KindBadge, { kind, variant: "glyph", inTitledGroup: true }));
    assert.ok(glyph.includes(`aria-label="${KIND_COPY[kind].label}"`));
    assert.ok(glyph.includes('role="img"'));
  }
  // Type-level rules, enforced by `npm run typecheck`.
  // @ts-expect-error a badge cannot be rendered without a kind
  void (() => h(KindBadge, {}));
  // @ts-expect-error glyph-only is allowed only inside a titled group
  void (() => h(KindBadge, { kind: "structural", variant: "glyph" }));
});

test("KindBadge with an explanation is focusable and describes itself", () => {
  const markup = html(h(KindBadge, { kind: "model-assumption", explain: true }));
  assert.match(markup, /tabindex="0"/);
  assert.match(markup, /aria-describedby="[^"]+"/);
  assert.match(markup, /role="tooltip"[^>]*hidden/);
  assert.ok(markup.includes(KIND_COPY["model-assumption"].tooltip));
});

test("Tooltip is hidden until opened and stays linked to its trigger", () => {
  const markup = html(h(Tooltip, { content: "Hello", focusable: true, children: h("span", null, "x") }));
  const id = /aria-describedby="([^"]+)"/.exec(markup)![1];
  assert.ok(markup.includes(`id="${id}"`));
  assert.match(markup, /role="tooltip"[^>]*hidden/);
});

test("Readout always shows its kind", () => {
  for (const kind of DATA_KINDS.filter((k) => k !== "model-state" && k !== "unavailable") as Exclude<DataKind, "model-state" | "unavailable">[]) {
    const markup = html(h(Readout, { kind, label: "Count", value: 42 }));
    assert.ok(markup.includes(`data-kind="${kind}"`));
    assert.ok(markup.includes(`aria-label="${KIND_COPY[kind].label}"`));
  }
  // @ts-expect-error a readout cannot be rendered without a kind
  void (() => h(Readout, { label: "x", value: 1 }));
});

test("model state accepts only model units", () => {
  const eq = html(h(Readout, { kind: "model-state", label: "DNp01 R", value: -52, digits: 3, unit: "mV_eq" }));
  assert.ok(eq.includes("-52.000"));
  assert.ok(eq.includes("mV_eq"));
  assert.ok(eq.includes(UNIT_COPY.modelEquivalentNote));
  const none = html(h(Readout, { kind: "model-state", label: "Index", value: 0.25, unit: "dimensionless" }));
  assert.ok(none.includes(UNIT_COPY.dimensionless));
  // @ts-expect-error a bare mV is a biological unit
  void (() => h(Readout, { kind: "model-state", label: "x", value: 1, unit: "mV" }));
  // @ts-expect-error model state must state its unit
  void (() => h(Readout, { kind: "model-state", label: "x", value: 1 }));
  assert.throws(() => html(h(Readout, { kind: "model-state", label: "x", value: 1, unit: "mV" as never })), /biological unit/);
  assert.throws(() => html(h(Readout, { kind: "structural", label: "x", value: 1, unit: "Hz" })), /biological unit/);
});

test("biological unit detection", () => {
  for (const unit of ["mV", "µV", "Hz", "kHz", "nA", "pA", "nS", "mS", "spikes/s", "firing rate"]) assert.equal(isBiologicalUnit(unit), true, unit);
  for (const unit of ["mV_eq", "rad", "ms", "s", "dimensionless", "contacts", "yaw_orientation_eq"]) assert.equal(isBiologicalUnit(unit), false, unit);
});

test("a missing value is never drawn as zero", () => {
  const missing = html(h(Readout, { kind: "model-state", label: "DNp01 R", state: "not-recorded" }));
  assert.ok(missing.includes("—"));
  assert.ok(missing.includes("Not recorded"));
  assert.doesNotMatch(text(missing), /\b0(\.0+)?\b/);
  const unavailable = html(h(Readout, { kind: "model-state", label: "Visual angle", state: "unavailable", reason: "Reason supplied by the page." }));
  assert.ok(unavailable.includes('data-kind="unavailable"'));
  assert.ok(unavailable.includes("Not available yet"));
  assert.ok(unavailable.includes("Reason supplied by the page."));
  // @ts-expect-error an unavailable readout must carry its reason
  void (() => h(Readout, { kind: "model-state", label: "x", state: "unavailable" }));
  const loading = html(h(Readout, { kind: "structural", label: "Count", state: "loading" }));
  assert.match(loading, /role="status"/);
  assert.doesNotMatch(loading, /class="[^"]*number/);
});

test("Readout reserves width so digits do not shift", () => {
  const markup = html(h(Readout, { kind: "structural", label: "Count", value: 7, minChars: 6 }));
  assert.match(markup, /--min-chars:6/);
});

test("ProvenanceLabel: inline has a details button, card and raw list the fields", () => {
  const props = { kind: "structural", source: "MaleCNS v1.0", modelVersion: "v1", status: "NOT_EVALUATED", artifactId: "abc123", apiHref: "/api/v1/x" } as const;
  const inline = html(h(ProvenanceLabel, props));
  assert.match(inline, /aria-expanded="false"/);
  assert.match(inline, /role="group"[^>]*hidden/);
  const card = html(h(ProvenanceLabel, { ...props, variant: "card" }));
  assert.ok(card.includes("Not evaluated"));
  assert.doesNotMatch(card, /NOT_EVALUATED/, "machine codes are for the raw layer only");
  assert.ok(card.includes("abc123"));
  assert.ok(card.includes('target="_blank"'));
  const raw = html(h(ProvenanceLabel, { ...props, variant: "raw" }));
  assert.ok(raw.includes("NOT_EVALUATED"));
  // @ts-expect-error provenance must state its kind
  void (() => h(ProvenanceLabel, { source: "x" }));
  const minimal = html(h(ProvenanceLabel, { kind: "model-assumption", source: "Gain setting", variant: "card" }));
  assert.doesNotMatch(minimal, /Model version|Artifact ID|API link|Status/);
});

test("statusLabel maps machine codes to words", () => {
  assert.equal(statusLabel("NOT_EVALUATED"), "Not evaluated");
  assert.equal(statusLabel("SOMETHING_NEW"), "Something new");
});

test("StatePanel: every state names what happened and uses the right role", () => {
  const alert = (state: Parameters<typeof StatePanel>[0]) => /role="alert"/.test(html(h(StatePanel, state)));
  assert.equal(alert({ state: "api-down" }), true);
  assert.equal(alert({ state: "route-error", reference: "abc" }), true);
  assert.equal(alert({ state: "integrity-failure" }), true);
  assert.equal(alert({ state: "empty", message: "No experiments match these filters." }), false);
  assert.equal(alert({ state: "not-found" }), false);
  assert.equal(alert({ state: "missing-data", what: "Neuron shapes" }), false);

  const down = html(h(StatePanel, { state: "api-down" }));
  assert.ok(down.includes(STATE_COPY.apiDown.title) && down.includes(STATE_COPY.apiDown.body.replace("'", "&#x27;")) || text(down).includes("Nothing on this page has been lost."));
  const integrity = text(html(h(StatePanel, { state: "integrity-failure" })));
  assert.ok(integrity.includes("The stored results failed their integrity check."));
  assert.ok(integrity.includes("none are substituted"));
  assert.doesNotMatch(integrity, /responding|verified/);
  const unknown = html(h(StatePanel, { state: "unknown-id", noun: "experiment", id: "abc123" }));
  assert.match(unknown, /There is no experiment with the ID <code[^>]*>abc123<\/code>\./);
  const loading = html(h(StatePanel, { state: "loading", what: "313 neuron shapes" }));
  assert.match(loading, /role="status"/);
  assert.match(loading, /aria-busy="true"/);
  assert.ok(loading.includes("Loading 313 neuron shapes"));
  assert.ok(text(html(h(StatePanel, { state: "webgl-off", hasDataAlternative: true }))).includes("The data below is the same."));
  assert.doesNotMatch(text(html(h(StatePanel, { state: "webgl-off", hasDataAlternative: false }))), /data below/);
  assert.ok(text(html(h(StatePanel, { state: "missing-data", what: "Neuron shapes" }))).includes("Neuron shapes not included in this artifact."));
  assert.match(html(h(StatePanel, { state: "route-error", reference: "dig-1", headingLevel: 3 })), /<h3[^>]*>This page couldn&#x27;t load\.<\/h3>/);
  // @ts-expect-error an unknown ID panel needs the ID it is describing
  void (() => h(StatePanel, { state: "unknown-id", noun: "experiment" }));
});

test("no retired term, bare biological unit or success colour in the new UI or copy", () => {
  const root = new URL("../src/components/ui/", import.meta.url);
  const files = readdirSync(root).filter((f) => /\.(tsx?|css)$/.test(f)).map((f) => [`ui/${f}`, readFileSync(new URL(f, root), "utf8")] as const);
  const copy = readFileSync(new URL("../src/content/science-copy.ts", import.meta.url), "utf8");
  // The copy file lists the retired terms on purpose; check everything else in it.
  const copyBody = copy.slice(0, copy.indexOf("export const RETIRED_TERMS"));
  for (const [name, source] of [...files, ["science-copy.ts", copyBody] as const]) {
    const prose = source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");
    for (const { term } of RETIRED_TERMS) assert.doesNotMatch(prose, term, `${name} uses a retired term: ${term}`);
    assert.doesNotMatch(prose, /color-success|✓|✔/, `${name} must not mark a result with a success colour or tick`);
  }
});

test("components use tokens, not hard-coded colours", () => {
  const root = new URL("../src/components/ui/", import.meta.url);
  for (const file of readdirSync(root).filter((f) => f.endsWith(".css"))) {
    const css = readFileSync(new URL(file, root), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
    assert.doesNotMatch(css, /#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(/, `${file} hard-codes a colour`);
  }
});

