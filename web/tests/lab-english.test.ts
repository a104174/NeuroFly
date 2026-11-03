import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { test } from "node:test";
import { displayText } from "../src/lib/frozenText";

function files(dir: URL): URL[] {
  return readdirSync(dir).flatMap((name) => {
    const url = new URL(name, dir);
    return statSync(url).isDirectory() ? files(new URL(`${name}/`, dir)) : /\.tsx?$/.test(name) ? [url] : [];
  });
}

// Strings that live in files pinned by scripts/frozen-contribution.ts. They are shown through displayText.
const FROZEN = ["lib/experimentalLocomotion.ts", "lib/neuralLocomotion.ts", "lib/neuralSteeringComparison.ts", "lib/frozenText.ts"];

test("no Portuguese text remains in the interface sources, apart from the frozen modules", () => {
  const src = new URL("../src/", import.meta.url);
  for (const file of files(src)) {
    const rel = file.pathname.split("/src/")[1];
    if (FROZEN.includes(rel)) continue;
    const text = readFileSync(file, "utf8");
    assert.doesNotMatch(text, /[ãçõâêô]/, `${rel} contains Portuguese`);
    assert.doesNotMatch(text, /\b(não|Não|indisponível|incompatível|Sessão|Replay canónico|A verificar)\b/, `${rel} contains Portuguese`);
  }
});

test("frozen Portuguese strings are shown in English", () => {
  assert.equal(displayText("Steering neural ativo"), "Neural steering on");
  assert.equal(displayText("Saída para steering desligada"), "Steering output off");
  assert.equal(displayText("Locomoção indisponível (HTTP 503)."), "Locomotion unavailable (HTTP 503).");
  assert.equal(displayText("Already English"), "Already English");
});
