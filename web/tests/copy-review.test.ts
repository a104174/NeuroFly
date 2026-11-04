import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { GLOSSARY, KIND_COPY } from "../src/content/science-copy";

const read = (p: string) => readFileSync(new URL(`../src/${p}`, import.meta.url), "utf8");

test("owner-approved wording for the Run definition and the Model assumption tooltip", () => {
  assert.equal(GLOSSARY.find((g) => g.id === "run")?.meaning, "One execution of the model. The model is deterministic, so the same inputs give the same run. A run is a model run, not a trial with a real fly.");
  assert.equal(KIND_COPY["model-assumption"].tooltip, "Chosen for the model; not validated here.");
});

test("parameters are not described as 'not measured': some come from published models", () => {
  const copy = read("content/science-copy.ts");
  assert.doesNotMatch(copy, /not measured from the fly/);
  assert.match(GLOSSARY.find((g) => g.id === "model-assumption")!.meaning, /published models/);
});

test("the replay caption says no simulation runs in the browser", () => {
  assert.match(read("components/ScenarioCockpit.tsx"), /no simulation runs in your browser/);
  assert.doesNotMatch(read("components/ScenarioCockpit.tsx"), /nothing is computed in your browser/);
});

test("'The data below is the same' appears only where a data alternative is declared", () => {
  assert.match(read("components/WebGLGate.tsx"), /hasDataAlternative = false/);
  assert.doesNotMatch(read("components/MorphologyInspector.tsx"), /dataAlternative/);
  assert.match(read("components/ScenarioCockpit.tsx"), /<WebGLGate hasDataAlternative>/);
  assert.match(read("components/PlaybackWorkspace.tsx"), /<WebGLGate hasDataAlternative>/);
});

test("the circuit-check note claims preregistration only for the checks that have it", () => {
  const page = read("app/science/page.tsx");
  assert.match(page, /Some circuit checks are preregistered, such as the HS → DNp15 check\./);
  assert.doesNotMatch(page, /is a preregistered test/);
});
