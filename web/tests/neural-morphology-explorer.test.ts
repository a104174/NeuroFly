import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import {
  deriveNeuralMorphologyView,
  loadVerifiedNeuralMorphology,
  NEURAL_MORPHOLOGY_IDENTITIES,
  NEURAL_MORPHOLOGY_MANIFEST_SHA256,
  NEURAL_MORPHOLOGY_MANIFEST_URL,
  neuralActivityViewSnapshot,
  parseMaleCnsSwc,
  parseNeuralMorphologyManifest,
} from "../src/lib/neuralMorphologyExplorer";
import { parseNeuralLocomotion } from "../src/lib/neuralLocomotion";
import { LiveGroundSession } from "../src/lib/liveGroundSession";
import { neuralActivityTrace } from "../src/lib/neuralActivityTrace";

const assetRoot = new URL("../public/assets/neural/malecns-v1.0/hs-dnp15/", import.meta.url);
const manifestBytes = readFileSync(new URL("manifest.json", assetRoot));
const manifestObject = JSON.parse(manifestBytes.toString("utf8")) as unknown;
const manifest = parseNeuralMorphologyManifest(manifestObject);
const sha256 = (value: Uint8Array) => createHash("sha256").update(value).digest("hex");

test("pinned v1.0 morphology bundle maps only the eight verified HS/DNp15 identities", () => {
  assert.equal(sha256(manifestBytes), NEURAL_MORPHOLOGY_MANIFEST_SHA256);
  assert.equal(manifest.dataset, "male-cns:v1.0");
  assert.equal(manifest.coordinate_frame_id, "male_cns_v1_em_native_voxels");
  assert.equal(manifest.coordinate_unit, "8_nm_voxel");
  assert.deepEqual(manifest.bodies.map((body) => body.body_id), NEURAL_MORPHOLOGY_IDENTITIES.map((item) => item.body_id));
  assert.deepEqual(manifest.bodies.map((body) => [body.cell_type, body.side]), [
    ["HSN", "R"], ["HSE", "R"], ["HSS", "R"], ["HSE", "L"],
    ["HSN", "L"], ["HSS", "L"], ["DNp15", "R"], ["DNp15", "L"],
  ]);
  assert.deepEqual(manifest.bodies.map((body) => body.model_state.field), [
    "hs_states[0]", "hs_states[1]", "hs_states[2]", "hs_states[3]",
    "hs_states[4]", "hs_states[5]", "dnp15_states[0]", "dnp15_states[1]",
  ]);
  assert.ok(manifest.bodies.every((body) => body.mapping_status === "IDENTITY_RESOLVED_MODEL_PROXY"));
  assert.equal(manifest.selected_routes.length, 6);
});

test("all eight source SWCs retain their official bytes and parse as finite one-component trees", () => {
  const parsed = manifest.bodies.map((identity) => {
    const bytes = readFileSync(new URL(identity.morphology.path, assetRoot));
    assert.equal(sha256(bytes), identity.morphology.source_sha256, `body ${identity.body_id} source hash`);
    const morphology = parseMaleCnsSwc(bytes.toString("utf8"), identity);
    assert.equal(morphology.node_count, identity.morphology.node_count);
    assert.equal(morphology.component_count, 1);
    assert.ok(Array.from(morphology.source_positions).every(Number.isFinite));
    return morphology;
  });
  assert.equal(parsed.reduce((sum, body) => sum + body.node_count, 0), 35_465);
  const view = deriveNeuralMorphologyView(parsed);
  assert.equal(view.axis_mapping, "IDENTITY_NATIVE_XYZ");
  assert.equal(view.bodies.length, 8);
  assert.ok(view.uniform_scale > 0 && Number.isFinite(view.uniform_scale));
  assert.ok(view.bodies.every((body) => Array.from(body.view_positions).every(Number.isFinite)));
  assert.ok(view.source_bounds.minimum[0] < view.source_bounds.maximum[0]);
  assert.ok(view.source_bounds.minimum[1] < view.source_bounds.maximum[1]);
  assert.ok(view.source_bounds.minimum[2] < view.source_bounds.maximum[2]);
});

test("manifest rejects version, identity, or route substitutions", () => {
  const wrongVersion = structuredClone(manifestObject) as { dataset: string };
  wrongVersion.dataset = "male-cns:v0.9";
  assert.throws(() => parseNeuralMorphologyManifest(wrongVersion), /provenance or coordinates/);

  const wrongBody = structuredClone(manifestObject) as { bodies: { body_id: number }[] };
  wrongBody.bodies[0].body_id = 99999;
  assert.throws(() => parseNeuralMorphologyManifest(wrongBody), /identity mismatch/);

  const wrongRoute = structuredClone(manifestObject) as { selected_routes: { structural_contact_count: number }[] };
  wrongRoute.selected_routes[0].structural_contact_count += 1;
  assert.throws(() => parseNeuralMorphologyManifest(wrongRoute), /route identity mismatch/);
});

test("SWC parser rejects duplicate IDs, missing parents, cycles, non-finite values and count changes", () => {
  const identity = manifest.bodies[0];
  const fixture = {
    ...identity,
    morphology: { ...identity.morphology, node_count: 3, component_count: 1 },
  };
  const good = "1 0 0 0 0 1 -1\n2 0 1 0 0 1 1\n3 0 1 1 0 1 2\n";
  assert.equal(parseMaleCnsSwc(good, fixture).source_positions.length, 12);
  assert.throws(() => parseMaleCnsSwc(good.replace("3 0", "2 0"), fixture), /invalid node identity/);
  assert.throws(() => parseMaleCnsSwc(good.replace("3 0 1 1 0 1 2", "3 0 1 1 0 1 9"), fixture), /missing parent/);
  assert.throws(() => parseMaleCnsSwc("1 0 0 0 0 1 -1\n2 0 1 0 0 1 3\n3 0 1 1 0 1 2\n", fixture), /parent cycle/);
  assert.throws(() => parseMaleCnsSwc(good.replace("1 0 0 0 0 1 -1", "1 0 NaN 0 0 1 -1"), fixture), /finite/);
  assert.throws(() => parseMaleCnsSwc(good.slice(0, good.lastIndexOf("3 ")), fixture), /node count/);
});

test("browser loader verifies the manifest and every raw body before preparing a shared view", async () => {
  const responseFor = (url: string) => {
    const path = url === NEURAL_MORPHOLOGY_MANIFEST_URL
      ? "manifest.json"
      : url.slice(url.lastIndexOf("/") + 1);
    return new Response(readFileSync(new URL(path, assetRoot)));
  };
  const fetcher = async (input: RequestInfo | URL) => responseFor(String(input));
  const loaded = await loadVerifiedNeuralMorphology(fetcher as typeof fetch);
  assert.equal(loaded.manifest.bodies.length, 8);
  assert.equal(loaded.view.bodies.length, 8);

  const alteredFetcher = async (input: RequestInfo | URL) => {
    const response = responseFor(String(input));
    const url = String(input);
    if (!url.endsWith("/10015.swc")) return response;
    const bytes = await response.arrayBuffer();
    const changed = new Uint8Array(bytes);
    changed[changed.length - 1] ^= 1;
    return new Response(changed);
  };
  await assert.rejects(loadVerifiedNeuralMorphology(alteredFetcher as typeof fetch), /10015 SHA-256 mismatch/);
});

test("activity snapshot uses the real interval proxy values and separate accepted tick", () => {
  const authority = parseNeuralLocomotion(JSON.parse(readFileSync(new URL("../public/experiments/experimental_locomotion_v1.json", import.meta.url), "utf8")));
  const session = new LiveGroundSession(authority, true, "morphology-test-session");
  session.start();
  const sample = session.advance();
  const trace = neuralActivityTrace(sample);
  const snapshot = neuralActivityViewSnapshot(session.config.session_id, trace);
  assert.equal(snapshot.schema, "neural_activity_view_snapshot_v1");
  assert.equal(snapshot.interval_tick, sample.interval.step);
  assert.equal(snapshot.accepted_tick, sample.accepted.step);
  assert.equal(snapshot.simulation_time_s, sample.interval.time);
  assert.deepEqual(snapshot.values.map((item) => [item.body_id, item.value]), trace.states.map((state) => [state.id, state.value]));
  assert.equal(snapshot.neural_yaw_rad_s, sample.interval.boundary_summary.neural_omega);
  assert.equal(snapshot.boundary_yaw_rad_s, sample.interval.boundary_summary.omega);
  assert.ok(snapshot.values.every((item) => item.semantics === "DIMENSIONLESS_SIGNED_COMPUTED_PROXY"));
  assert.throws(() => neuralActivityViewSnapshot("", trace), /unavailable or does not match/);
  const wrongIdentity = { ...trace, states: trace.states.map((state, index) => index === 0 ? { ...state, id: 99999 } : state) } as unknown as typeof trace;
  assert.throws(() => neuralActivityViewSnapshot(session.config.session_id, wrongIdentity), /unavailable or does not match/);

  session.pause();
  const paused = neuralActivityViewSnapshot(session.config.session_id, trace);
  assert.deepEqual(paused, snapshot);
  session.start();
  const resumed = neuralActivityViewSnapshot(session.config.session_id, neuralActivityTrace(session.advance()));
  assert.equal(resumed.interval_tick, snapshot.accepted_tick);
});
