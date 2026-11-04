import assert from "node:assert/strict";
import { register } from "node:module";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { NeuroflyApiError } from "../src/lib/neuroflyClient";
import { isMorphologyNotOnDeployment } from "../src/lib/morphologyAvailability";

// Node cannot import CSS Modules; see tests/support/css-hooks.mjs.
register(new URL("./support/css-hooks.mjs", import.meta.url));
const { StatePanel } = await import("../src/components/ui/StatePanel");
const { default: MorphologyPage } = await import("../src/app/morphology/(list)/page");

test("only the 'morphology root is not configured' answer counts as not being on this deployment", () => {
  assert.equal(isMorphologyNotOnDeployment(new NeuroflyApiError("morphology_store_unavailable", "x", 503)), true);
  assert.equal(isMorphologyNotOnDeployment(new NeuroflyApiError("artifact_not_found", "x", 404)), false);
  assert.equal(isMorphologyNotOnDeployment(new NeuroflyApiError("artifact_integrity_failure", "x", 409)), false);
  assert.equal(isMorphologyNotOnDeployment(new Error("network down")), false);
  assert.equal(isMorphologyNotOnDeployment(null), false);
});

test("the not-on-deployment panel says so, and does not say the data service is not responding", () => {
  const html = renderToStaticMarkup(createElement(StatePanel, { state: "not-on-deployment" }));
  assert.match(html, /Neuron shape data is not available on this deployment\./);
  assert.match(html, /role="status"/);
  assert.doesNotMatch(html, /isn(&#x27;|')t responding/);
});

async function withApi(response: () => Response, check: () => Promise<void>) {
  const oldFetch = globalThis.fetch, oldBase = process.env.NEUROFLY_API_BASE_URL;
  process.env.NEUROFLY_API_BASE_URL = "https://deploy.test";
  globalThis.fetch = async () => response();
  try { await check(); } finally {
    globalThis.fetch = oldFetch;
    if (oldBase === undefined) delete process.env.NEUROFLY_API_BASE_URL; else process.env.NEUROFLY_API_BASE_URL = oldBase;
  }
}

test("Neurons list: the API's 'not configured' answer shows the deployment message, not an outage", async () => {
  await withApi(
    () => new Response(JSON.stringify({ schema: "experiment_http_error_v1", code: "morphology_store_unavailable", message: "morphology artifact root is not configured" }), { status: 503, headers: { "content-type": "application/json" } }),
    async () => {
      const html = renderToStaticMarkup(await MorphologyPage());
      assert.match(html, /Neuron shape data is not available on this deployment\./);
      assert.doesNotMatch(html, /isn(&#x27;|')t responding/);
      assert.doesNotMatch(html, /Retry/);
    },
  );
});

test("Neurons list: a real outage still says the data service is not responding", async () => {
  await withApi(
    () => new Response("bad gateway", { status: 502 }),
    async () => {
      const html = renderToStaticMarkup(await MorphologyPage());
      assert.match(html, /isn(&#x27;|')t responding/);
      assert.doesNotMatch(html, /not available on this deployment/);
    },
  );
});
