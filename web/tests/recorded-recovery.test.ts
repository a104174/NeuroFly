import assert from "node:assert/strict";
import test from "node:test";
import { execFileSync } from "node:child_process";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { parseExperimentSummary } from "../src/lib/neuroflyClient";
import { recordedRunPurpose } from "../src/lib/recordedExperimentPresentation";
import { register } from "node:module";
// Node cannot import CSS Modules. Register the test-only hook before the components load, so the
// imports that reach CSS are dynamic. (package.json is frozen, so this cannot be an npm script.)
register(new URL("./support/css-hooks.mjs", import.meta.url));
const { default: ExperimentsPage } = await import("../src/app/experiments/(list)/page");
import { ExperimentSummaryView } from "../src/components/ExperimentSummaryView";

test("authentic Phase 3B API metadata keeps engineering purpose and stable detail/cockpit links", async () => {
  // Explicit integration dependency: missing pinned local data fails; no fixture fallback.
  const raw = execFileSync("python", ["-B", "-c", `
import json, shutil, tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from neurofly.http_api import create_app
from neurofly.recorded_experiments_runtime import reference, REQUIRED_ARTIFACT_IDS
source, spec = reference(Path.cwd(), replay=False)
with tempfile.TemporaryDirectory() as d:
    shutil.copytree(source, Path(d)/spec['directory_name'])
    with TestClient(create_app(d, required_artifact_ids=REQUIRED_ARTIFACT_IDS)) as c:
        r=c.get('/api/v1/experiments')
        assert r.status_code==200
        print(json.dumps(r.json()['experiments'][0]))
`], { cwd: new URL("../../", import.meta.url), encoding: "utf8", timeout: 30000 });
  const run = parseExperimentSummary(JSON.parse(raw));
  assert.equal(run.artifact_id, "63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656");
  assert.equal(run.result_id, "8af5a3f50f0cd9fee65ce62e5421c873e95a48e32333de475545c1be7f133b45");
  assert.equal(run.duration_ms, 80);
  assert.equal(run.validation_status, "NOT_EVALUATED");
  // The detail view keeps the engineering purpose sentence; the list carries the owner's label.
  const detail = renderToStaticMarkup(createElement(ExperimentSummaryView, { summary: run }));
  assert.match(detail, /Engineering \/ UI smoke reference/);
  assert.match(detail, /No comparison with real fly data has been made/);
  assert.doesNotMatch(detail, /biologically validated|empirically validated/i);
  const savedFetch = globalThis.fetch, savedBase = process.env.NEUROFLY_API_BASE_URL;
  process.env.NEUROFLY_API_BASE_URL = "https://api.test";
  globalThis.fetch = async () => Response.json({ schema: "experiment_http_v1", kind: "experiment_list", experiments: [JSON.parse(raw)] });
  let list: string;
  try { list = renderToStaticMarkup(await ExperimentsPage({ searchParams: Promise.resolve({}) })); }
  finally { globalThis.fetch = savedFetch; if (savedBase === undefined) delete process.env.NEUROFLY_API_BASE_URL; else process.env.NEUROFLY_API_BASE_URL = savedBase; }
  assert.match(list, /Engineering test, not a scientific experiment/);
  assert.match(list, /Not evaluated/);
  assert.doesNotMatch(list, /biologically validated|empirically validated/i);
  assert(list.includes(`href="/experiments/${run.artifact_id}"`));
  assert(list.includes(`href="/experiments/${run.artifact_id}/cockpit"`));
});

test("engineering reference presentation does not assign purpose to unrelated experiments", () => {
  assert.equal(recordedRunPurpose("different_experiment"), null);
});
