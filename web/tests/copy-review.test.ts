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

import { AUTHOR_HREF, AUTHOR_NAME } from "../src/components/site/siteContent";
test("the author credit is in the footer and on the Science page, and the asset credits stay", () => {
  assert.equal(AUTHOR_NAME, "Hélder Cruz");
  assert.equal(AUTHOR_HREF, "https://heldercruz.dev/pt");
  const footer = read("components/site/SiteChrome.tsx");
  assert.match(footer, /Created by <a href=\{AUTHOR_HREF\}>\{AUTHOR_NAME\}<\/a>/);
  assert.match(footer, /Visual assets: fly by/);
  assert.match(read("app/science/page.tsx"), /Created by <a href=\{AUTHOR_HREF\}>\{AUTHOR_NAME\}<\/a>/);
});

import { CC_BY_HREF, MALECNS_PAPER, MALECNS_RELEASE_HREF } from "../src/components/site/siteContent";
test("the MaleCNS credit names the dataset and version, links CC BY 4.0, says the files are derived, and cites the paper", () => {
  assert.equal(CC_BY_HREF, "https://creativecommons.org/licenses/by/4.0/");
  assert.equal(MALECNS_RELEASE_HREF, "https://male-cns.janelia.org/release/");
  assert.equal(MALECNS_PAPER.doi, "10.1101/2025.10.09.680999");
  assert.equal(MALECNS_PAPER.title, "Sexual dimorphism in the complete connectome of the Drosophila male central nervous system");
  const footer = read("components/site/SiteChrome.tsx");
  assert.match(footer, /MALECNS_RELEASE_HREF/);
  assert.match(footer, /CC BY 4\.0/);
  assert.match(footer, /files are derived from it/);
  const science = read("app/science/page.tsx");
  assert.match(science, /id="data-credit"/);
  assert.match(science, /licensed under/);
  assert.match(science, /derived from it/);
  assert.match(science, /No healing, smoothing or repair was applied/);
  assert.match(science, /MALECNS_PAPER\.href/);
});
