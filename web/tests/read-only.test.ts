import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

/**
 * Phase 0 decision 3: the frontend writes nothing to the API. A source scan stands in for the full
 * browser network assertion (which needs a browser tool in CI): no write method anywhere, and the
 * one allowed Server Action only reads stored data.
 */
const root = new URL("../src/", import.meta.url).pathname;
function files(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? files(path) : /\.(ts|tsx)$/.test(name) ? [path] : [];
  });
}
const sources = files(root).map((path) => [path.slice(root.length), readFileSync(path, "utf8")] as const);

test("no source file issues a write request to the API", () => {
  for (const [name, code] of sources) {
    assert.doesNotMatch(code, /method\s*:\s*["'`](?:POST|PUT|PATCH|DELETE)["'`]/i, `${name} sets a write method`);
    assert.doesNotMatch(code, /\.(?:post|put|patch|delete)\(\s*["'`]\/?api/i, name);
    assert.doesNotMatch(code, /fetch\([^)]*\{[^}]*body\s*:/, `${name} sends a request body`);
  }
});

test("the only Server Action is loadScenarioPlayback, and it performs a GET read of stored data", () => {
  const actions = sources.filter(([, code]) => /^\s*["']use server["']/m.test(code));
  assert.deepEqual(actions.map(([name]) => name), ["app/scenarios/actions.ts"]);
  const code = actions[0][1];
  assert.deepEqual([...code.matchAll(/export async function (\w+)/g)].map((m) => m[1]), ["loadScenarioPlayback"]);
  assert.match(code, /requestJson\(`\/api\/v1\/scenarios\/\$\{id\}\/playback`/);
  assert.doesNotMatch(code, /\b(?:POST|PUT|PATCH|DELETE)\b|body\s*:|method\s*:/);
  // requestJson itself sends a GET: no method and no body.
  const client = readFileSync(join(root, "lib/neuroflyClient.ts"), "utf8");
  const request = client.slice(client.indexOf("export async function requestJson"), client.indexOf("export async function listExperiments"));
  assert.match(request, /fetch\(`\$\{apiBaseUrl\(\)\}\$\{path\}\$\{suffix\}`, \{\s*cache: "no-store",\s*headers: \{ Accept: "application\/json" \},\s*\}\)/);
  assert.doesNotMatch(request, /method|body/);
});

test("the replay button says it replays a stored scenario", () => {
  const cockpit = readFileSync(join(root, "components/ScenarioCockpit.tsx"), "utf8");
  assert.match(cockpit, /Replay canonical scenario/);
  assert.doesNotMatch(cockpit, /Run canonical preset|validated replay/);
});
