import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ScenarioExplanation } from "../src/components/ScenarioExplanation";
import { scenarioNarrative } from "../src/lib/scenarioPresentation";
import { loadScenarioPlayback } from "../src/app/scenarios/actions";
import { advanceScenarioCursor, parseScenarioCatalog, parseScenarioPlayback, scenarioScene, PRESENTATION_SCALE, type ScenarioPlaybackResult } from "../src/lib/scenarioPlayback";

// TEST_ONLY_NONCANONICAL transport, not a generated scientific artifact.
function fixture(): ScenarioPlaybackResult {
  return {
    schema: "scenario_playback_v1", artifact_id: "a".repeat(64), run_id: "b".repeat(64),
    scenario: { id: "LOOMING_CIRCUIT_VALIDATION", scenario_kind: "LOOMING_CIRCUIT_VALIDATION", title: "Looming", description: "Test only", availability: "CANONICAL_PRESET", preset_only: true, scientific_caveat: "Not biology" },
    dt_ms: 0.1, duration_ms: 0.2, source_operation: "VALIDATED_CANONICAL_REPLAY", dnp01_body_ids: [10001,10010], total_dnp01_spikes: 0, scientific_limitations: ["Model space"],
    statuses: { closed_loop_execution_completed: true, environment_affected_sensory_input: true, body_state_feedback_wired: true, body_state_feedback_realized: false, genuine_nonzero_actuation_occurred: false, body_movement_occurred: false },
    frames: [0,1,2].map(i => ({ step: i, time_ms: i * 0.1,
      body: { x_world_eq: 0, z_world_eq: 0, fixed_heading: "POSITIVE_Z" },
      object: { x_world_eq: 0, z_world_eq: 4 - i, radius_world_eq: 1 },
      relative_distance_world_eq: 4 - i, lattice_radius: 2, active_sensory_body_count: 19,
      sensory_summaries: [{ neuron_type: "LC4", side: "R", state_sum: i }], dnp01_membrane_mv: [-52+i*.01,-52], dnp01_spike_body_ids: [], ttmn_state: [0,0], actuator_commands: { RIGHT_TTM_ACTUATOR: 0, LEFT_TTM_ACTUATOR: 0 },
    })),
  };
}
test("typed payload preserves execution true and movement false independently", () => {
  const r = parseScenarioPlayback(fixture());
  assert.equal(r.statuses.closed_loop_execution_completed, true);
  assert.equal(r.statuses.body_movement_occurred, false);
  assert.equal(r.frames.length, 3);
});
test("exact five supported preset definitions and no phantom worlds", () => {
  const s = fixture().scenario;
  assert.equal(parseScenarioCatalog([{...s,id:"BASELINE_CONTROL",scenario_kind:"BASELINE_CONTROL"},s,{...s,id:"LOOMING_WORLD_EXPERIMENT",scenario_kind:"LOOMING_WORLD_EXPERIMENT"},{...s,id:"HORIZONTAL_MOTION_NEURAL_VALIDATION",scenario_kind:"HORIZONTAL_MOTION_NEURAL_VALIDATION"},{...s,id:"EXPLORATORY_COURSE_CONTROL",scenario_kind:"EXPLORATORY_COURSE_CONTROL"}]).length, 5);
  assert.throws(() => parseScenarioCatalog([s]));
  assert.throws(() => parseScenarioCatalog([{...s,id:"LIGHT_DARK"},s]));
});
test("world experiment preserves scientific horizon, termination and frozen identity", () => {
  const r = fixture();
  r.scenario.id = r.scenario.scenario_kind = "LOOMING_WORLD_EXPERIMENT";
  r.preregistration_id = "c".repeat(64);
  r.requested_duration_ms = r.duration_ms;
  r.termination = {status:"COMPLETED_VALID_HORIZON",step:2,time_ms:0.2,reason:null};
  assert.equal(parseScenarioPlayback(r).termination?.status,"COMPLETED_VALID_HORIZON");
  r.termination.status = "TERMINATED_GEOMETRY_DOMAIN";
  r.termination.step = 3; r.termination.time_ms = 0.3; r.termination.reason = "UNSAFE GEOMETRY";
  r.requested_duration_ms = 40;
  r.statuses.closed_loop_execution_completed = false;
  const parsed = parseScenarioPlayback(r);
  const html = renderToStaticMarkup(createElement(ScenarioExplanation,{result:parsed,frame:parsed.frames[2]}));
  assert.match(html,/STOPPED · GEOMETRY DOMAIN/);
  assert.match(html,/Requested horizon 40 ms/);
  assert.doesNotMatch(html,/RUN COMPLETE/);
  r.termination.step = 8;
  assert.throws(() => parseScenarioPlayback(r));
});
test("malformed grid, nonfinite positions, unknown kind and command are rejected", () => {
  for (const mutate of [
    (r: ScenarioPlaybackResult) => { r.frames[1].time_ms = 99; },
    (r: ScenarioPlaybackResult) => { r.frames[0].body.z_world_eq = NaN; },
    (r: ScenarioPlaybackResult) => { r.frames[1].actuator_commands.RIGHT_TTM_ACTUATOR = 2; },
    (r: ScenarioPlaybackResult) => { r.frames[0].object = null; },
  ]) { const r = fixture(); mutate(r); assert.throws(() => parseScenarioPlayback(r)); }
  assert.throws(() => parseScenarioPlayback({ ...fixture(), scenario: { ...fixture().scenario, id: "ESCAPE" } }));
});
test("baseline is object absent, not an object at zero", () => {
  const r = fixture();
  r.scenario.id = r.scenario.scenario_kind = "BASELINE_CONTROL";
  r.frames.forEach(f => { f.object = null; f.relative_distance_world_eq = null; f.lattice_radius = null; f.active_sensory_body_count = 0; });
  const parsed = parseScenarioPlayback(r);
  assert.equal(scenarioScene(parsed, 1).objectPosition, null);
});
test("presentation clock play pause finish do not mutate scientific time", () => {
  const r = fixture(), original = JSON.stringify(r);
  assert.equal(advanceScenarioCursor(0, 3000, true, 2), 1);
  assert.equal(advanceScenarioCursor(1, 3000, false, 2), 1);
  assert.equal(advanceScenarioCursor(1, 99999, true, 2), 2);
  assert.equal(scenarioScene(r, 0).frame.step, 0); // reset
  assert.equal(scenarioScene(r, 2).frame.step, 2); // scrub
  assert.equal(JSON.stringify(r), original);
});
test("neighbor-only render interpolation; exact telemetry and authoritative transforms", () => {
  const r = fixture(), scene = scenarioScene(r, 0.5);
  assert.equal(scene.frame, r.frames[0]);
  assert.equal(scene.objectPosition![2], 3.5 * PRESENTATION_SCALE);
  assert.deepEqual(scene.bodyPosition, [0,0,0]);
  // Noncanonical body snapshots must actually control rendered position.
  r.frames[1].body.x_world_eq = 4;
  r.frames[1].body.z_world_eq = 6;
  assert.deepEqual(scenarioScene(r, 1).bodyPosition, [4*PRESENTATION_SCALE,0,6*PRESENTATION_SCALE]);
});
test("UI uses backend action, no full artifact parsing, no frame physics", () => {
  const ui = readFileSync(new URL("../src/components/ScenarioCockpit.tsx", import.meta.url),"utf8");
  const scene = readFileSync(new URL("../src/components/ScenarioWorld.tsx", import.meta.url),"utf8");
  const action = readFileSync(new URL("../src/app/scenarios/actions.ts", import.meta.url),"utf8");
  assert.match(ui,/loadScenarioPlayback\(scenario.id\)/);
  assert.match(ui,/setPlaying\(false\); setCursor\(0\)/);
  assert.match(ui,/setCursor\(Number\(e.target.value\)\)/);
  assert.match(scene,/position=\{scene.bodyPosition\}/);
  assert.match(scene,/position=\{scene.objectPosition\}/);
  assert.match(action,/parseScenarioPlayback/);
  assert.doesNotMatch(scene,/useFrame|velocity|atan2|animateJump|jump\(/);
  assert.doesNotMatch(ui,/sensory_state_by_boundary|scenarios.json|escape successful|movement detected/);
});

test("backend action handles typed API errors and malformed payload without fallback", async () => {
  const originalFetch = globalThis.fetch, originalUrl = process.env.NEUROFLY_API_BASE_URL;
  process.env.NEUROFLY_API_BASE_URL = "http://127.0.0.1:8000";
  try {
    globalThis.fetch = async () => new Response(JSON.stringify({schema:"experiment_http_error_v1",code:"scenario_unavailable",message:"Replay unavailable"}),{status:503});
    assert.match((await loadScenarioPlayback("LOOMING_CIRCUIT_VALIDATION") as {error:string}).error,/could not be replay-validated/);
    globalThis.fetch = async () => new Response(JSON.stringify({schema:"full_internal_artifact"}),{status:200});
    assert.match((await loadScenarioPlayback("LOOMING_CIRCUIT_VALIDATION") as {error:string}).error,/Malformed/);
    globalThis.fetch = async () => new Response(JSON.stringify(fixture()),{status:200});
    const success = await loadScenarioPlayback("LOOMING_CIRCUIT_VALIDATION");
    assert.ok("result" in success);
    assert.deepEqual(await loadScenarioPlayback("BASELINE_CONTROL"),{error:"Backend returned the wrong scenario."});
  } finally {
    globalThis.fetch = originalFetch;
    if (originalUrl === undefined) delete process.env.NEUROFLY_API_BASE_URL;
    else process.env.NEUROFLY_API_BASE_URL = originalUrl;
  }
});

test("baseline rendered explanation makes stationary control intentional", () => {
  const r = fixture();
  r.scenario.id = r.scenario.scenario_kind = "BASELINE_CONTROL";
  r.frames.forEach(f => { f.object = null; f.lattice_radius = null; f.relative_distance_world_eq = null; f.active_sensory_body_count = 0; f.sensory_summaries.forEach(s => { s.state_sum = 0; }); });
  const html = renderToStaticMarkup(createElement(ScenarioExplanation, {result:r, frame:r.frames[0]}));
  assert.match(html,/A control, not a broken simulation/);
  assert.match(html,/No external stimulus/);
  assert.match(html,/Body stationary/);
  assert.match(html,/Stimulus disabled/);
  assert.match(html,/No genuine motor command/);
  assert.equal(scenarioScene(r,1).objectPosition,null);
});
test("looming rendered causal narrative explains subthreshold zero movement", () => {
  const r = fixture(), f = r.frames[2];
  const html = renderToStaticMarkup(createElement(ScenarioExplanation,{result:r,frame:f}));
  for (const text of ["Approaching object","Visual circuit responding","Below model spike threshold","SUBTHRESHOLD","No genuine motor command","Body stationary","RUN COMPLETE"]) assert.ok(html.includes(text),text);
  assert.match(html,/No genuine actuator command was produced/);
  assert.doesNotMatch(html,/escape failed/);
});
test("scientific values and selected-boundary story are sourced from DTO, not canonical literals", () => {
  const r = fixture(), f = r.frames[1];
  f.active_sensory_body_count = 31; f.lattice_radius = 8; f.dnp01_membrane_mv[0] = -48.125;
  const html = renderToStaticMarkup(createElement(ScenarioExplanation,{result:r,frame:f}));
  assert.match(html,/31/); assert.match(html,/Radius 8/); assert.match(html,/-48.125/); assert.match(html,/0.1/);
  assert.equal(scenarioNarrative(r,r.frames[0]).stages[1].state,"INITIAL STATE");
  assert.equal(scenarioNarrative(r,f).stages[1].state,"RESPONDING");
  assert.equal(scenarioScene(r,1).frame,f);
});
test("noncanonical nonzero records change labels, never inject or fake scientific motion", () => {
  const r = fixture(), f = r.frames[1];
  r.total_dnp01_spikes = 1; f.dnp01_spike_body_ids = [10001];
  f.actuator_commands.RIGHT_TTM_ACTUATOR = 0.4;
  r.statuses.genuine_nonzero_actuation_occurred = true; r.statuses.body_movement_occurred = true;
  f.body.z_world_eq = 2;
  const story = scenarioNarrative(r,f);
  assert.equal(story.stages[2].state,"SPIKE"); assert.equal(story.stages[3].state,"COMMAND");
  assert.equal(scenarioScene(r,1).bodyPosition[2],2*PRESENTATION_SCALE);
  assert.doesNotMatch(story.summary,/produced no DNp01 spikes/);
});
test("one current object, no opaque history spheres, no fake retinal geometry", () => {
  const scene = readFileSync(new URL("../src/components/ScenarioWorld.tsx",import.meta.url),"utf8");
  assert.equal(scene.match(/name="authoritative-looming-object"/g)?.length,1);
  assert.equal(scene.match(/<sphereGeometry/g)?.length,1);
  assert.match(scene,/LineDashedMaterial/);
  assert.match(scene,/!baseline && <ApproachGuide/);
  assert.match(scene,/scene.frame.lattice_radius/);
  assert.match(scene,/scene.frame.active_sensory_body_count/);
  assert.match(scene,/not a calibrated retinal map/);
  assert.doesNotMatch(scene,/atan2|Math.floor|useFrame|setInterval|animateJump/);
});
test("scenario-only material clone preserves historical asset and avoids idle motion", () => {
  const asset = readFileSync(new URL("../src/components/ScenarioFlyVisual.tsx",import.meta.url),"utf8");
  assert.match(asset,/gltf.scene.clone\(true\)/);
  assert.match(asset,/opacity: 0.22/);
  assert.doesNotMatch(asset,/useFrame|rotation\.set|position\.add|random|sin\(/);
  const ui = readFileSync(new URL("../src/components/ScenarioCockpit.tsx",import.meta.url),"utf8");
  assert.match(ui,/<ScenarioExplanation result=\{result\} frame=\{result.frames\[frame.step\]\}/);
});
