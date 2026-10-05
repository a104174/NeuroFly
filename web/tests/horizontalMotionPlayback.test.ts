import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { HorizontalMotionExplanation } from "../src/components/HorizontalMotionExplanation";
import { loadScenarioPlayback } from "../src/app/scenarios/actions";
import { advanceScenarioCursor, isNeuralPlayback, neuralScene, parseScenarioPlayback, type NeuralPlaybackResult } from "../src/lib/scenarioPlayback";
import { scenarioCopy } from "../src/lib/scenarioPresentation";

// Cross-language contract fixture: the actual Pydantic adapter replays the frozen
// Phase25 artifact. No model fixture, new scientific run, or generated artifact.
const payload: unknown = JSON.parse(execFileSync("python", ["-c", "from neurofly.scenario_playback_api import load_neural_playback; print(load_neural_playback().model_dump_json(by_alias=True))"], {
  cwd: fileURLToPath(new URL("../../", import.meta.url)), encoding: "utf8", maxBuffer: 1_000_000,
}));
const parsed = parseScenarioPlayback(payload);
assert.ok(isNeuralPlayback(parsed));
const result: NeuralPlaybackResult = parsed;

test("real Pydantic neural variant matches TypeScript without world/event fields", () => {
  assert.deepEqual(result, payload);
  assert.equal(result.frames.length, 501);
  assert.equal(result.duration_ms, 50);
  assert.equal(result.condition_id, "RIGHT_SIDE_MOTION");
  assert.equal(result.statuses.body_mapping, "NOT_DEFINED");
  assert.equal(result.statuses.event_semantics, "NOT_DEFINED");
  assert.equal(result.provenance.active_routes.length, 6);
  assert.equal(result.provenance.excluded_routes.length, 7);
  assert.equal(scenarioCopy[result.scenario.id].role, "HS→DNp15 · NEURAL-ONLY VALIDATION");
});

test("neural parser fails closed for identities, routes, units and invented semantics", () => {
  const mutations: ((r: NeuralPlaybackResult)=>void)[] = [
    r=>{r.sources[0].body_id=999;}, r=>{r.targets[0].side="L";},
    r=>{r.provenance.active_routes[0].target_id=12069;},
    r=>{r.provenance.excluded_routes.pop();}, r=>{r.frames[2].time_ms=100;},
    r=>{r.frames[0].hs_states[0]=NaN;}, r=>{r.frames[0].dnp15_states.pop();},
    r=>{r.frames[0].input_descriptor.R=2;},
  ];
  for(const mutate of mutations){const r=structuredClone(result); mutate(r); assert.throws(()=>parseScenarioPlayback(r));}
  for(const extra of [{target_units:"mV"},{total_dnp01_spikes:0},{presentation_kind:"WORLD"}]){
    assert.throws(()=>parseScenarioPlayback({...result,...extra}));
  }
  assert.throws(()=>parseScenarioPlayback({...result,frames:[{...result.frames[0],body:{x_world_eq:0,z_world_eq:0}},...result.frames.slice(1)]}));
});

test("play pause scrub reset coordinate telemetry and stateless visual phase", () => {
  const before=JSON.stringify(result);
  assert.equal(advanceScenarioCursor(0,3000,true,500),250);
  assert.equal(advanceScenarioCursor(100,3000,false,500),100);
  assert.equal(advanceScenarioCursor(100,6000,true,500),500);
  for(const cursor of [0,100,199.5,200,213,500,0]){
    const scene=neuralScene(result,cursor);
    assert.deepEqual(scene.frame,result.frames[Math.floor(cursor)]);
    const html=renderToStaticMarkup(createElement(HorizontalMotionExplanation,{result,frame:scene.frame}));
    assert.ok(html.includes(`Exact boundary ${scene.frame.step}`));
    assert.ok(html.includes(scene.frame.bilateral_differential.toFixed(6)));
  }
  assert.equal(neuralScene(result,199.5).phase,1.995);
  assert.equal(neuralScene(result,500).phase,2);
  assert.equal(neuralScene(result,0).phase,0);
  assert.equal(JSON.stringify(result),before);
});

test("newcomer explanation shows all identities, six active routes and diagnostic limits", () => {
  const html=renderToStaticMarkup(createElement(HorizontalMotionExplanation,{result,frame:result.frames[213]}));
  for(const term of ["Motion input","HS sources","Chemical motif","DNp15 readout","Diagnostic only","horizontal_motion_eq","dnp15_state_eq","model diagnostic only","event semantics not defined","No body mapping is defined","Phase26 context audit"]){assert.ok(html.includes(term),term);}
  for(const node of [...result.sources,...result.targets]) assert.ok(html.includes(String(node.body_id)));
  assert.match(html,/larger right DNp15 proxy state/);
  assert.match(html,/not active signal paths/);
  assert.doesNotMatch(html,/0 spikes|steering command|turn rate|the fly steers|the fly decides|calibrated DNp15 voltage|biological optic flow/);
  const negative=structuredClone(result.frames[100]); negative.hs_states[0]=-0.25;
  assert.match(renderToStaticMarkup(createElement(HorizontalMotionExplanation,{result,frame:negative})),/-0.250000/);
});

test("server action keeps authoritative data and explicit unavailable state", async()=>{
  const saved=globalThis.fetch;
  const savedUrl=process.env.NEUROFLY_API_BASE_URL;
  process.env.NEUROFLY_API_BASE_URL="http://127.0.0.1:8000";
  try {
    globalThis.fetch=async()=>new Response(JSON.stringify(payload),{status:200});
    const loaded=await loadScenarioPlayback("HORIZONTAL_MOTION_NEURAL_VALIDATION");
    assert.ok("result" in loaded && isNeuralPlayback(loaded.result));
    globalThis.fetch=async()=>new Response(JSON.stringify({code:"scenario_unavailable",detail:"Frozen authority unavailable"}),{status:503});
    assert.ok("error" in await loadScenarioPlayback("HORIZONTAL_MOTION_NEURAL_VALIDATION"));
  } finally {globalThis.fetch=saved; if(savedUrl === undefined) delete process.env.NEUROFLY_API_BASE_URL; else process.env.NEUROFLY_API_BASE_URL=savedUrl;}
});

test("presentation has no autonomous simulation or body transform", ()=>{
  const world=readFileSync(new URL("../src/components/HorizontalMotionWorld.tsx",import.meta.url),"utf8");
  assert.match(world,/frameloop="demand"/);
  assert.match(world,/neuralScene\(result,cursor\)/);
  assert.doesNotMatch(world,/useFrame|setInterval|requestAnimationFrame|ScenarioFlyVisual|yaw|target_tau|source_tau/);
  const cockpit=readFileSync(new URL("../src/components/ScenarioCockpit.tsx",import.meta.url),"utf8");
  assert.match(cockpit,/HorizontalMotionExplanation/);
  assert.match(cockpit,/setPlaying\(false\); setCursor\(0\)/);
  assert.match(cockpit,/role="alert"/);
});
