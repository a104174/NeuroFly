import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createElement, type ComponentType } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { CurrentResult } from "../src/components/CurrentResult";
import { NeuralMotif } from "../src/components/NeuralMotif";
import { ScientificTrace } from "../src/components/ScientificTrace";
import { ScenarioCard } from "../src/components/ScenarioCard";
import { AuthorityIds, CausalChain, PlaybackPhases, ScientificPlaybackLoading, ScientificPlaybackUnavailable, TelemetryValue, UnitHelp } from "../src/components/ScientificInstrument";
import { experimentMetadata } from "../src/lib/scenarioPresentation";
import { isCoursePlayback, isNeuralPlayback, parseScenarioPlayback, SCENARIO_KINDS, type ScenarioPlayback } from "../src/lib/scenarioPlayback";

// Real five-scenario adapter output. Validated replay only; no artifact writes.
const payloads:unknown[]=JSON.parse(execFileSync("python",["-c","import json; from typing import get_args; from neurofly.scenario_playback_api import load_scenario_playback, ScenarioKind; print(json.dumps([load_scenario_playback(s).model_dump(mode='json', by_alias=True) for s in get_args(ScenarioKind)]))"],{cwd:fileURLToPath(new URL("../../",import.meta.url)),encoding:"utf8",maxBuffer:3_000_000}));
const results=payloads.map(parseScenarioPlayback);
const neural=results.find(isNeuralPlayback)!;
const course=results.find(isCoursePlayback)!;
const html=<P extends object>(component:ComponentType<P>,props:P)=>renderToStaticMarkup(createElement(component,props));
const source=(name:string)=>readFileSync(new URL(`../src/${name}`,import.meta.url),"utf8");
const resultHtml=(r:ScenarioPlayback,step=0)=>html(CurrentResult,{result:r,step});

test("five library cards have comparable metadata and accessible navigation",()=>{
  assert.deepEqual(results.map(r=>r.scenario.id),[...SCENARIO_KINDS]);
  results.forEach((result,index)=>{
    const card=html(ScenarioCard,{scenario:result.scenario,index}), meta=experimentMetadata[result.scenario.id];
    assert.match(card,/aria-label="Open /); assert.ok(card.includes(`/scenarios/${result.scenario.id}`));
    for(const term of [meta.kind,meta.duration,meta.input,meta.scope,meta.outcome,"Canonical replay available"])assert.ok(card.includes(term),term);
    assert.ok(Math.abs(Number.parseFloat(meta.duration)-result.duration_ms)<1e-9);
    assert.doesNotMatch(card,/biological steering|returns to course|calibrated yaw|navigation|complete fly brain/);
  });
});
test("current results distinguish whole run and boundary zero without inventing activity",()=>{
  const baseline=resultHtml(results[0]);assert.match(baseline,/Expected neutral control state/);assert.match(baseline,/resting model coordinate/);assert.match(baseline,/not a broken simulation/);
  for(const r of results){
    const before=JSON.stringify(r), first=resultHtml(r),last=resultHtml(r,r.frames.length-1);
    assert.match(first,/Whole canonical run/);assert.match(first,/Selected boundary/);assert.match(first,/0.0 ms/);assert.match(last,/RUN COMPLETE/);
    for(const word of ["DATA","MODEL","RESULT"])assert.ok(first.includes(word));
    assert.doesNotMatch(first,/fly decides|fly chooses|biological steering|real yaw|calibrated optic flow|returns to course|restores heading|navigation|complete fly brain/);
    assert.equal(JSON.stringify(r),before);
  }
  for(const r of results.slice(1,3)){assert.match(resultHtml(r),/DNp01 remains subthreshold/);assert.match(resultHtml(r),/no DNp01 spikes/);assert.match(resultHtml(r),/body movement/);}
  assert.match(resultHtml(neural),/No body mapping is defined/);assert.match(resultHtml(neural),/event semantics not defined/);assert.doesNotMatch(resultHtml(neural),/0 spikes/);
  assert.match(resultHtml(course),/nonzero residual offset/);assert.match(resultHtml(course),/not absolute heading error/);assert.match(resultHtml(course),/MARGINAL ORIENTATION MODE/);
});
test("selected DNp15 result follows the backend boundary, not a fixed canonical peak",()=>{
  assert.match(resultHtml(neural,0),/diagnostic is currently neutral/);
  assert.match(resultHtml(neural,200),/larger right DNp15 proxy state/);
  assert.ok(resultHtml(neural,200).includes(neural.frames[200].dnp15_states[0].toFixed(6)));
  assert.ok(resultHtml(course,500).includes(course.frames[500].yaw_orientation_eq.toFixed(9)));
});
test("neural viewport exposes exactly eight identities and six uniform active routes",()=>{
  const markup=html(NeuralMotif,{result:neural,frame:neural.frames[200]});
  for(const n of [...neural.sources,...neural.targets]) assert.ok(markup.includes(`data-identity="${n.body_id}"`));
  const routes=Array.from(markup.matchAll(/data-route="([^"]+)"/g),m=>m[1]).sort();
  assert.deepEqual(routes,neural.provenance.active_routes.map(r=>`${r.source_id}:${r.target_id}`).sort());
  assert.match(markup,/LEFT · L/);assert.match(markup,/RIGHT · R/);assert.match(markup,/no body mapping/);
  for(const r of neural.provenance.excluded_routes) assert.ok(!routes.includes(`${r.source_id}:${r.target_id}`));
  const changed=structuredClone(neural);changed.provenance.active_routes.forEach(r=>r.structural_count*=17);
  assert.equal(html(NeuralMotif,{result:changed,frame:changed.frames[200]}),markup);
  assert.doesNotMatch(markup,/spikes|steering command|mV/);
});
test("course trace displays authoritative samples, zero, selected time and residual only",()=>{
  const before=JSON.stringify(course);
  for(const step of [0,1,100,500]){
    const markup=html(ScientificTrace,{result:course,step});
    assert.ok(markup.includes(course.frames[step].yaw_orientation_eq.toFixed(9)));
    assert.match(markup,/chart scale only/);assert.match(markup,/Specimen rotation is not amplified/);assert.match(markup,/residual offset/);assert.match(markup,/not a sensed target heading/);
    assert.ok(markup.includes(course.summary.final_orientation_eq.toFixed(9)));
  }
  assert.equal(JSON.stringify(course),before);
  assert.doesNotMatch(source("components/ScientificTrace.tsx"),/source_tau|yaw_gain|setInterval|requestAnimationFrame/);
});
test("phase annotations originate from authoritative duration, pulse and perturbation",()=>{
  assert.match(html(PlaybackPhases,{result:neural}),/0–20 ms · stimulus/);assert.match(html(PlaybackPhases,{result:neural}),/50 ms · recovery/);
  assert.match(html(PlaybackPhases,{result:course}),/0→1 · external perturbation/);assert.match(html(PlaybackPhases,{result:course}),/50 ms · residual offset/);
  assert.match(html(PlaybackPhases,{result:results[1]}),/1.4 ms · experiment ends/);
  assert.match(html(PlaybackPhases,{result:results[2]}),/40 ms · experiment ends/);
});
test("undefined, unavailable, and model zero remain semantically distinct",()=>{
  const neutral=html(TelemetryValue,{label:"Neutral proxy",value:"+0.000000",unit:"dnp15_state_eq"});assert.match(neutral,/\+0.000000/);
  const notDefined=resultHtml(neural);assert.match(notDefined,/not defined/);assert.doesNotMatch(notDefined,/0 spikes/);
  const error=html(ScientificPlaybackUnavailable,{detail:"Authority mismatch",retry:()=>{}});
  for(const term of ["Experiment playback unavailable.","The canonical scientific artifact could not be validated.","No synthetic fallback has been substituted.","Retry","Back to experiments"])assert.ok(error.includes(term));
  assert.match(error,/role="alert"/);assert.doesNotMatch(error,/<canvas|<svg|Expected neutral/);
  const loading=html(ScientificPlaybackLoading,{});assert.match(loading,/Validating canonical scientific playback/);assert.match(loading,/aria-busy="true"/);assert.match(loading,/loading—not a neutral result/);assert.doesNotMatch(loading,/<canvas|<svg|0\.000/);
});
test("units and full authority hashes remain accessible under native disclosures",()=>{
  const units=html(UnitHelp,{});for(const unit of ["mV_eq","world_eq","horizontal_motion_eq","dnp15_state_eq","yaw_drive_eq","yaw_orientation_eq","relative_view_eq"])assert.ok(units.includes(unit));
  const id=course.artifact_id,ids=html(AuthorityIds,{ids:{"Phase30 artifact":id}});assert.ok(ids.includes(id));assert.ok(ids.includes(id.slice(0,10)));assert.match(ids,/<details/);assert.match(ids,/<summary/);
});
test("shared causal chain distinguishes delayed return and not-defined boundaries",()=>{
  const chain=html(CausalChain,{stages:[{name:"Motion observation",title:"No completed interval",detail:"Boundary zero",state:"NOT DEFINED"},{name:"Next view",title:"Next interval",detail:"Delayed",state:"NEXT-INTERVAL FEEDBACK"}],step:0,time:0,loop:true});
  assert.match(chain,/NOT DEFINED/);assert.match(chain,/delayed closed-loop update/);assert.match(chain,/no same-boundary feedback/);
});
test("layout promotes results, mobile transport, focus and comfortable disclosures",()=>{
  const css=source("app/scenarios.css"),cockpit=source("components/ScenarioCockpit.tsx");
  assert.match(cockpit,/CurrentResult result=\{result\} step=\{frame.step\}/);
  assert.match(css,/experiment-main.*grid-template-columns: minmax\(0,1fr\) 340px/);
  assert.match(css,/\.scenario-transport \{ order: 1;/);assert.match(css,/\.causal-section \{ order: 2;/);
  assert.match(css,/outline: 2px solid var\(--science-focus\)/);assert.match(css,/min-height: 44px/);assert.match(css,/prefers-reduced-motion/);
  assert.match(source("app/scenarios/[scenarioId]/page.tsx"),/<Suspense fallback=/);assert.match(source("app/scenarios/[scenarioId]/loading.tsx"),/ScientificPlaybackLoading/);
});
test("frozen Phase32 audit and transport/parsers are not altered by visual redesign",()=>{
  const root=fileURLToPath(new URL("../../",import.meta.url));
  for(const file of ["docs/science/frontend_scientific_readability_ux_audit.md","docs/science/frontend_scientific_readability_ux_audit.json","web/src/lib/scenarioPlayback.ts","web/src/lib/courseControlPlayback.ts","src/neurofly/scenario_playback_api.py"]){
    const prior=execFileSync("git",["show",`ae5a469:${file}`],{cwd:root});
    assert.equal(createHash("sha256").update(readFileSync(`${root}/${file}`)).digest("hex"),createHash("sha256").update(prior).digest("hex"));
  }
  results.forEach((r,i)=>assert.deepEqual(r,payloads[i]));
});
