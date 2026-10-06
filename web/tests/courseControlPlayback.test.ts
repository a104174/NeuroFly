import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { CourseControlExplanation } from "../src/components/CourseControlExplanation";
import { courseScene, type CoursePlaybackResult } from "../src/lib/courseControlPlayback";
import { isCoursePlayback, isNeuralPlayback, parseScenarioPlayback, advanceScenarioCursor } from "../src/lib/scenarioPlayback";
import { scenarioCopy } from "../src/lib/scenarioPresentation";
import { loadScenarioPlayback } from "../src/app/scenarios/actions";

// Real Pydantic payload over canonical Phase30 replay, not synthetic science.
const payload:unknown=JSON.parse(execFileSync("python",["-c","from neurofly.scenario_playback_api import load_course_playback; print(load_course_playback().model_dump_json(by_alias=True))"],{cwd:fileURLToPath(new URL("../../",import.meta.url)),encoding:"utf8",maxBuffer:1_000_000}));
const parsed=parseScenarioPlayback(payload);assert.ok(isCoursePlayback(parsed));
const result=parsed;
test("real Pydantic course variant and TypeScript agree exactly",()=>{
  assert.deepEqual(result,payload);assert.equal(isNeuralPlayback(result),false);
  assert.equal(result.condition_id,"CLOSED_LOOP_PERTURBATION");assert.equal(result.frames.length,501);
  assert.equal(result.summary.clipping_count,0);assert.equal(result.statuses.translation,"NOT_MODELLED");
  assert.equal(scenarioCopy[result.scenario.id].badge,"Marginal orientation dynamics");
});
test("course parser rejects malformed or incompatible scientific transport",()=>{
  const mutations:((r:CoursePlaybackResult)=>void)[]=[
    r=>{r.sources[0].body_id=999;},r=>{r.targets[0].side="L";},r=>{r.frames[5].hs_states.pop();},
    r=>{r.frames[1].previous_orientation_eq=.2;},r=>{r.frames[1].input_descriptor.R=2;},
    r=>{r.frames[1].observation!.interval_start_step=1;},r=>{r.frames[1].observation!.clipped=true;},
    r=>{r.provenance.neural.active_routes[0].target_id=12069;},r=>{r.provenance.neural.excluded_routes.pop();},
    r=>{r.provenance.analysis.local_motion_spectral_radius=1.1;},r=>{r.frames[2].yaw_drive_eq=1;},
    r=>{r.frames[2].dnp15_states[0]=NaN;},r=>{r.summary.final_orientation_eq=0;},
    r=>{r.provenance.observation_contract_id="invalid";},r=>{r.frames[1].time_ms=1;},
  ];
  for(const mutate of mutations){const r=structuredClone(result);mutate(r);assert.throws(()=>parseScenarioPlayback(r));}
  for(const extra of [{orientation_units:"degrees"},{total_dnp01_spikes:0},{presentation_kind:"NEURAL_ONLY_VALIDATION"}])assert.throws(()=>parseScenarioPlayback({...result,...extra}));
  assert.throws(()=>parseScenarioPlayback({...result,frames:[{...result.frames[0],body:{x:0}},...result.frames.slice(1)]}));
});
test("play pause scrub reset preserve exact telemetry and final residual",()=>{
  const before=JSON.stringify(result);assert.equal(advanceScenarioCursor(0,6000,true,500),500);
  assert.equal(advanceScenarioCursor(30,1000,false,500),30);
  for(const cursor of [0,1,50,199.5,500,0]){
    const scene=courseScene(result,cursor);assert.deepEqual(scene.frame,result.frames[Math.floor(cursor)]);
    const html=renderToStaticMarkup(createElement(CourseControlExplanation,{result,frame:scene.frame}));
    assert.ok(html.includes(`Exact boundary ${scene.frame.step}`));
    assert.ok(html.includes(scene.frame.yaw_orientation_eq.toFixed(9)));
  }
  assert.equal(courseScene(result,0).renderRotation,0);
  assert.equal(courseScene(result,500).renderRotation,result.summary.final_orientation_eq*2*Math.PI);
  assert.notEqual(courseScene(result,500).renderRotation,0);
  assert.equal(JSON.stringify(result),before);
});
test("scientific newcomer copy shows delayed loop, model units and honest residual",()=>{
  const html=renderToStaticMarkup(createElement(CourseControlExplanation,{result,frame:result.frames[500]}));
  for(const term of ["World / view","Motion observation","HS sources","DNp15","Next view","MARGINAL ORIENTATION MODE","nonzero residual offset","not absolute heading error","No translation","event semantics not defined","yaw_orientation_eq","relative_view_eq","horizontal_motion_eq","dnp15_state_eq","yaw_drive_eq","model diagnostic only","Phase30 artifact","excluded from active model"])assert.ok(html.includes(term),term);
  for(const node of [...result.sources,...result.targets])assert.ok(html.includes(String(node.body_id)));
  assert.doesNotMatch(html,/biological steering|returns to course|restores heading|calibrated yaw|torque|navigation|real turn rate|0 spikes/);
  assert.match(html,/not claimed to reduce motion relative to that stationary control/);
});
test("render transform is stateless and only consumes authoritative playback",()=>{
  const world=readFileSync(new URL("../src/components/CourseControlWorld.tsx",import.meta.url),"utf8");
  assert.match(world,/frameloop="demand"/);assert.match(world,/rotation=\{\[0,renderRotation,0\]\}/);
  assert.doesNotMatch(world,/useFrame|requestAnimationFrame|setInterval|source_tau|yaw_gain/);
  const cockpit=readFileSync(new URL("../src/components/ScenarioCockpit.tsx",import.meta.url),"utf8");
  assert.match(cockpit,/isCoursePlayback/);assert.match(cockpit,/setPlaying\(false\); setCursor\(0\)/);
  const page=readFileSync(new URL("../src/app/scenarios/page.tsx",import.meta.url),"utf8");assert.match(page,/Five executable presets/);
});
test("unavailable authority returns an error, never substitute science",async()=>{
  const saved=globalThis.fetch,savedUrl=process.env.NEUROFLY_API_BASE_URL;
  process.env.NEUROFLY_API_BASE_URL="http://127.0.0.1:8000";
  try{
    globalThis.fetch=async()=>new Response(JSON.stringify(payload),{status:200});
    const loaded=await loadScenarioPlayback("EXPLORATORY_COURSE_CONTROL");assert.ok("result" in loaded && isCoursePlayback(loaded.result));
    globalThis.fetch=async()=>new Response(JSON.stringify({code:"scenario_unavailable",detail:"Canonical artifact could not be validated"}),{status:503});
    assert.ok("error" in await loadScenarioPlayback("EXPLORATORY_COURSE_CONTROL"));
    assert.match(scenarioCopy.EXPLORATORY_COURSE_CONTROL.failureNote!,/No synthetic fallback has been substituted/);
  }finally{globalThis.fetch=saved;if(savedUrl===undefined)delete process.env.NEUROFLY_API_BASE_URL;else process.env.NEUROFLY_API_BASE_URL=savedUrl;}
});
