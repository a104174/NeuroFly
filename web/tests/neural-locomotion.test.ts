import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { parseNeuralLocomotion, NEURAL_LOCOMOTION_SHA256, loadNeuralLocomotion } from "../src/lib/neuralLocomotion";
import { locomotionScene, type LocomotionReplay } from "../src/lib/experimentalLocomotion";
import { FLY_VIEWER_ASSET } from "../src/lib/flyViewer";
import { Vector3 } from "three";
const bytes=readFileSync(new URL("../public/experiments/experimental_locomotion_v1.json",import.meta.url));
const a=parseNeuralLocomotion(JSON.parse(bytes.toString()));
const replay={...a,config:a.config.body} satisfies LocomotionReplay;
test("versioned Python replay pins real HS/DNp15 sources, clocks, geometry and honest mode labels",()=>{
  assert.equal(createHash('sha256').update(bytes).digest('hex'),NEURAL_LOCOMOTION_SHA256);
  assert.equal(a.result.runs.length,4);
  assert.equal(a.result.runs[1].neural_substeps,80000);
  assert.equal(a.config.body.speed,.18);
  assert.equal(a.result.causal_metrics.disabled_matches_baseline,true);
  assert.ok(Number(a.result.causal_metrics.visual_intervention_max_yaw_rad)>0);
  assert.ok(Number(a.result.causal_metrics.visual_intervention_max_readout)>0);
});
test("every interpolated heading/position is synchronized and the approved asset stays above floor and inside walls",()=>{
  for(let run=0;run<4;run++)for(let i=0;i<=800;i++){
    const s=locomotionScene(replay,run,i*.01);
    for(const x of [FLY_VIEWER_ASSET.bounds.min[0],FLY_VIEWER_ASSET.bounds.max[0]])for(const y of [FLY_VIEWER_ASSET.bounds.min[1],FLY_VIEWER_ASSET.bounds.max[1]])for(const z of [FLY_VIEWER_ASSET.bounds.min[2],FLY_VIEWER_ASSET.bounds.max[2]]){
      const q=new Vector3(x,y,z).add(new Vector3(...s.pose.assetOffset)).multiplyScalar(.3).applyAxisAngle(new Vector3(0,1,0),s.pose.rotation).add(new Vector3(...s.pose.anchor));
      assert.ok(Math.abs(q.x)<1.194 && Math.abs(q.z)<.604 && q.y>0 && q.y<.854);
    }
  }
  assert.notEqual(locomotionScene(replay,1,5).pose.rotation,locomotionScene(replay,3,5).pose.rotation);
  assert.deepEqual(locomotionScene(replay,0,5).pose,locomotionScene(replay,2,5).pose);
});
test("contradictory clock, neuron, sensory, heading, propulsion and mode metadata are rejected",()=>{
  for(const mutate of [
    (r:typeof a)=>{r.config.sources.neural.source_identities[0].body_id=1;},
    (r:typeof a)=>{r.config.policy.neural_substeps_per_interval=199;},
    (r:typeof a)=>{r.result.runs[1].frames[1].neural_summary!.substeps=199;},
    (r:typeof a)=>{r.result.runs[1].frames[1].sensory_summary!.right=.9;},
    (r:typeof a)=>{r.result.runs[1].frames[2].orientation+=.01;},
    (r:typeof a)=>{r.result.runs[1].frames[0].propulsion_model_value=.19;},
    (r:typeof a)=>{r.result.runs[2].frames[1].angular_velocity=.1;},
    (r:typeof a)=>{r.result.runs[3].frames[1].position[0]=NaN;},
    (r:typeof a)=>{r.result.runs[3].condition!.plane_z=.4;},
    (r:typeof a)=>{r.result.runs[1].frames.pop();},
  ]){const r=structuredClone(a);mutate(r);assert.throws(()=>parseNeuralLocomotion(r));}
});
test("missing/corrupted neural replay never falls back to invented steering",async()=>{
  await assert.rejects(loadNeuralLocomotion(async()=>new Response(null,{status:404})),/HTTP 404/);
  await assert.rejects(loadNeuralLocomotion(async()=>new Response('corrupt')),/corrompido/);
});
