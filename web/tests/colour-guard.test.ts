import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { test } from "node:test";

/**
 * Brief section 11, Tokens: no hard-coded colours outside tokens.css. The legacy stylesheets below still
 * carry some; their counts may only go down (a ratchet). Every other stylesheet must have none.
 * The same rule runs as Stylelint in web-quality/ (`npm run lint:css`).
 */
const LEGACY_LIMITS: Readonly<Record<string, number>> = {
  "app/cockpit.css": 14,
  "app/globals.css": 38,
  "app/product.css": 21,
  "app/scenarios.css": 48,
  "app/visual-lab/arena/lab.css": 73,
  "app/visual-lab/fly/viewer.css": 32,
};

function css(dir: URL, rel = ""): string[] {
  return readdirSync(dir).flatMap((name) => {
    const url = new URL(name, dir);
    return statSync(url).isDirectory() ? css(new URL(`${name}/`, dir), `${rel}${name}/`) : name.endsWith(".css") ? [`${rel}${name}`] : [];
  });
}

test("no hard-coded colours outside tokens.css, and the legacy files only shrink", () => {
  const src = new URL("../src/", import.meta.url);
  for (const rel of css(src)) {
    if (rel === "styles/tokens.css") continue;
    const text = readFileSync(new URL(rel, src), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
    const count = (text.match(/#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(/g) ?? []).length;
    const limit = LEGACY_LIMITS[rel] ?? 0;
    assert.ok(count <= limit, `${rel} has ${count} hard-coded colours (limit ${limit})`);
  }
});
