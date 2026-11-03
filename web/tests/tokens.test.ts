import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  THEME_INIT_SCRIPT,
  THEME_STORAGE_KEY,
  applyThemePreference,
  parseThemePreference,
} from "../src/lib/theme";

const css = readFileSync(new URL("../src/styles/tokens.css", import.meta.url), "utf8");

/** Top-level and one-level-nested rule blocks: [selector chain, body]. */
function blocks(source: string): Array<[string, string]> {
  const out: Array<[string, string]> = [];
  const walk = (text: string, parent: string) => {
    let i = 0;
    while (i < text.length) {
      const open = text.indexOf("{", i);
      if (open < 0) break;
      let depth = 1, j = open + 1;
      while (depth && j < text.length) { depth += text[j] === "{" ? 1 : text[j] === "}" ? -1 : 0; j++; }
      const selector = text.slice(i, open).replace(/\/\*[\s\S]*?\*\//g, "").trim();
      const body = text.slice(open + 1, j - 1);
      if (selector.startsWith("@media") || selector.startsWith("@supports")) walk(body, `${parent}${selector} > `);
      else out.push([parent + selector, body]);
      i = j;
    }
  };
  walk(source, "");
  return out;
}
function declarations(body: string): Record<string, string> {
  return Object.fromEntries([...body.matchAll(/(--[a-z0-9-]+):\s*([^;]+);/g)].map((m) => [m[1], m[2].trim()]));
}
const all = blocks(css);
const find = (selector: string) => all.filter(([s]) => s === selector).map(([, b]) => declarations(b));
const dark = Object.assign({}, ...find(':root,\n[data-theme-scope="dark"]'));
const lightSystem = Object.assign({}, ...find('@media (prefers-color-scheme: light) > :root:not([data-theme="dark"])'));
const lightExplicit = Object.assign({}, ...find(':root[data-theme="light"]'));

function luminance(hex: string): number {
  const channel = (n: number) => { const c = n / 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
  const [r, g, b] = [1, 3, 5].map((i) => channel(parseInt(hex.slice(i, i + 2), 16)));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function ratio(a: string, b: string): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

const TEXT = ["ink", "ink-2", "ink-3", "accent", "structural", "model", "not-evaluated", "unavailable", "danger", "success"];
const SURFACES = ["canvas", "surface", "raised"];

for (const [name, theme] of [["dark", dark], ["light", lightExplicit]] as const) {
  test(`${name} theme: every text colour reaches 4.5:1 on canvas, surface and raised`, () => {
    for (const t of TEXT) for (const s of SURFACES) {
      const value = ratio(theme[`--color-${t}`], theme[`--color-${s}`]);
      assert.ok(value >= 4.5, `${name} ${t} on ${s} is ${value.toFixed(2)}`);
    }
  });
  test(`${name} theme: kind and status colours reach 4.5:1 on their badge tint`, () => {
    for (const k of ["structural", "model", "not-evaluated", "unavailable", "danger", "accent"]) {
      const value = ratio(theme[`--color-${k}`], theme[`--tint-${k}`]);
      assert.ok(value >= 4.5, `${name} ${k} on its tint is ${value.toFixed(2)}`);
    }
  });
  test(`${name} theme: control borders reach 3:1 on every surface`, () => {
    for (const s of SURFACES) {
      const value = ratio(theme["--color-border-control"], theme[`--color-${s}`]);
      assert.ok(value >= 3, `${name} border-control on ${s} is ${value.toFixed(2)}`);
    }
  });
  test(`${name} theme: button text reaches 4.5:1 on the accent`, () => {
    assert.ok(ratio(theme["--color-on-accent"], theme["--color-accent"]) >= 4.5);
  });
}

test("the brief's published ratios match the tokens", () => {
  const near = (actual: number, expected: number) => assert.ok(Math.abs(actual - expected) < 0.02, `${actual.toFixed(2)} vs ${expected}`);
  near(ratio(lightExplicit["--color-ink"], lightExplicit["--color-canvas"]), 16.65);
  near(ratio(lightExplicit["--color-ink-3"], lightExplicit["--color-raised"]), 4.71);
  near(ratio(dark["--color-model"], dark["--color-surface"]), 9.9);
  near(ratio(dark["--color-accent"], dark["--color-canvas"]), 9.07);
});

test("the two copies of the light theme are identical and cover every dark token", () => {
  assert.deepEqual(lightSystem, lightExplicit);
  for (const key of Object.keys(lightExplicit)) assert.ok(key in dark, `${key} has no dark value`);
  for (const key of Object.keys(dark).filter((k) => k.startsWith("--color-") || k.startsWith("--tint-"))) {
    if (key === "--color-model-state") continue; // alias of ink-2, same in both themes
    assert.ok(key in lightExplicit, `${key} has no light value`);
  }
});

test("the dark scope resolves every colour-dependent token locally", () => {
  // A var() alias is resolved where it is declared, so aliases of colours must live in the colour blocks.
  for (const theme of [dark, lightExplicit, lightSystem]) {
    assert.equal(theme["--focus-ring"], "2px solid var(--color-accent)");
  }
  assert.equal(dark["--color-model-state"], "var(--color-ink-2)");
  assert.match(css, /\[data-theme-scope="dark"\]/);
  const shared = Object.assign({}, ...find(":root"));
  assert.equal("--focus-ring" in shared, false, "focus ring must not be declared in the theme-independent block");
});

test("success colour is documented as system-state only and the stage stays dark", () => {
  assert.match(css, /System states only[\s\S]*--color-success/);
  const root = Object.assign({}, ...find(":root"), ...find(':root,\n[data-theme-scope="dark"]'));
  assert.equal(root["--stage-bg"], "#0a0c0d");
  assert.equal(luminance(root["--stage-bg"]) < 0.01, true);
});

test("glass never drops below 0.82 opacity and has a solid fallback", () => {
  const root = Object.assign({}, ...find(":root"), ...find(':root,\n[data-theme-scope="dark"]'));
  const alpha = Number(/rgba\([^)]*,\s*([\d.]+)\)/.exec(root["--glass-bg"])![1]);
  assert.ok(alpha >= 0.82);
  assert.match(css, /prefers-reduced-transparency/);
  assert.match(css, /@supports not \(backdrop-filter/);
});

test("reduced motion zeroes every duration token", () => {
  const reduced = Object.assign({}, ...find("@media (prefers-reduced-motion: reduce) > :root"));
  for (const k of ["--dur-fast", "--dur-base", "--dur-slow", "--dur-camera"]) assert.equal(reduced[k], "0ms");
});

test("spacing, radii and component tokens match the brief", () => {
  const root = Object.assign({}, ...find(":root"), ...find(':root,\n[data-theme-scope="dark"]'));
  const px = [4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 160].map((n) => `${n}px`);
  px.forEach((value, index) => assert.equal(root[`--space-${index + 1}`], value));
  assert.equal(root["--radius-lg"], "16px");
  assert.equal(root["--header-height"], "64px");
  assert.equal(root["--text-caption-size"], "0.75rem");
});

test("no legacy page still hard-codes Arial", () => {
  const dir = new URL("../src/app", import.meta.url).pathname;
  let hits = "";
  try { hits = execFileSync("grep", ["-rl", "--include=*.css", "Arial", dir], { encoding: "utf8" }).trim(); } catch { /* grep exits 1 when nothing matches */ }
  assert.equal(hits, "");
});

test("theme preference parsing, storage and the pre-paint script", () => {
  assert.equal(parseThemePreference("light"), "light");
  assert.equal(parseThemePreference("dark"), "dark");
  for (const bad of [null, undefined, "", "auto", "LIGHT", 1]) assert.equal(parseThemePreference(bad), "system");

  const attrs = new Map<string, string>();
  const root = { setAttribute: (k: string, v: string) => void attrs.set(k, v), removeAttribute: (k: string) => void attrs.delete(k) };
  const store = new Map<string, string>();
  const storage = { setItem: (k: string, v: string) => void store.set(k, v), removeItem: (k: string) => void store.delete(k) };
  applyThemePreference("light", root, storage);
  assert.equal(attrs.get("data-theme"), "light");
  assert.equal(store.get(THEME_STORAGE_KEY), "light");
  applyThemePreference("system", root, storage);
  assert.equal(attrs.has("data-theme"), false);
  assert.equal(store.has(THEME_STORAGE_KEY), false);
  const blocked = { setItem() { throw new Error("blocked"); }, removeItem() { throw new Error("blocked"); } };
  assert.doesNotThrow(() => applyThemePreference("dark", root, blocked));
  assert.equal(attrs.get("data-theme"), "dark");

  const run = (stored: string | null | "throw") => {
    const out = new Map<string, string>();
    const fn = new Function("localStorage", "document", THEME_INIT_SCRIPT);
    fn({ getItem: () => { if (stored === "throw") throw new Error("blocked"); return stored; } },
      { documentElement: { setAttribute: (k: string, v: string) => void out.set(k, v) } });
    return out.get("data-theme") ?? null;
  };
  assert.equal(run("light"), "light");
  assert.equal(run("dark"), "dark");
  assert.equal(run("system"), null);
  assert.equal(run(null), null);
  assert.equal(run("throw"), null);
});
