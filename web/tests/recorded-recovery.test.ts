import assert from "node:assert/strict";
import test from "node:test";
import { execFileSync } from "node:child_process";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { parseExperimentSummary } from "../src/lib/neuroflyClient";
import { recordedRunPurpose } from "../src/lib/recordedExperimentPresentation";
import { RecordedExperiments } from "../src/components/discovery/RecordedExperiments";
import { ExperimentSummaryView } from "../src/components/ExperimentSummaryView";

test("authentic Phase 3B API metadata keeps engineering purpose and stable detail/cockpit links", () => {
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
  for (const element of [createElement(RecordedExperiments, { experiments: [run], error: null }), createElement(ExperimentSummaryView, { summary: run })]) {
    const html = renderToStaticMarkup(element);
    assert.match(html, /Engineering \/ UI smoke reference/);
    assert.match(html, /Empirical validation has not been evaluated/);
    assert.doesNotMatch(html, /biologically validated|empirically validated/i);
  }
  const list = renderToStaticMarkup(createElement(RecordedExperiments, { experiments: [run], error: null }));
  assert(list.includes(`href="/experiments/${run.artifact_id}"`));
  assert(list.includes(`href="/experiments/${run.artifact_id}/cockpit"`));
});

test("engineering reference presentation does not assign purpose to unrelated experiments", () => {
  assert.equal(recordedRunPurpose("different_experiment"), null);
});
