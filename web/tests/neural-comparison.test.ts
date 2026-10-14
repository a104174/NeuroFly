import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { parseNeuralLocomotion } from "../src/lib/neuralLocomotion";
import { advanceLocomotion } from "../src/lib/experimentalLocomotion";
import { comparisonOverview, comparisonScenes, comparisonDelta, wrappedAngle } from "../src/lib/neuralSteeringComparison";
const raw=JSON.parse(readFileSync(new URL("../public/experiments/experimental_locomotion_v1.json",import.meta.url),"utf8"));
const authority=parseNeuralLocomotion(raw);
const replay={...authority,config:authority.config.body};
const near=(a:number,b:number)=>assert.ok(Math.abs(a-b)<1e-10,`${a} != ${b}`);
test("B/C/D share scientific time and independently recorded four-second positions",()=>{
 const states=comparisonScenes(replay,4);
 assert.deepEqual(states.map(s=>s.key),["B","C","D"]);
 const expected=[[.7062456690702007,.23128556782922474,1.130897108380308],[.7200000000000022,.12187743186950682,1.5707963267948966],[.7087699494066295,.015621730315911193,1.9052698814015008]];
 states.forEach((s,i)=>{near(s.scene.time,4);near(s.scene.pose.anchor[0],expected[i][0]);near(s.scene.pose.anchor[2],expected[i][1]);near(s.scene.pose.rotation,expected[i][2]);});
 assert.ok(states[1].scene.frame.neural_summary!.mean_yaw_drive_eq!==0);
 assert.equal(states[1].scene.frame.steering_applied,false);
});
test("shared Play/Pause/Resume/Reset/Seek/end clock and interpolation do not extrapolate",()=>{
 let time=0;time=advanceLocomotion(time,1000,true);near(time,1);
 near(advanceLocomotion(time,500,false),1);near(advanceLocomotion(time,1000,true),2);
 time=4.01;const s=comparisonScenes(replay,time);
 s.forEach(x=>{const frames=replay.result.runs[x.index].frames;near(x.scene.pose.anchor[0],(frames[200].position[0]+frames[201].position[0])/2);near(x.scene.pose.rotation,(frames[200].orientation+frames[201].orientation)/2);});
 time=advanceLocomotion(time,20000,true);near(time,8);assert.equal(comparisonScenes(replay,time)[0].scene.frame.neural_summary!.mean_yaw_drive_eq,null);
 assert.equal(comparisonScenes(replay,0)[0].scene.time,0);
 for(const invalid of [-.01,8.01,NaN,Infinity])assert.throws(()=>comparisonScenes(replay,invalid));
});
test("signed wrapped angular separation handles ±pi without introducing a full rotation",()=>{
 near(wrappedAngle((-Math.PI+.01)-(Math.PI-.01)),.02);
 near(wrappedAngle((Math.PI-.01)-(-Math.PI+.01)),-.02);
 assert.throws(()=>wrappedAngle(NaN));
});
test("current separation, traveled difference and boundary maxima have distinct definitions",()=>{
 const s=comparisonScenes(replay,4), d=comparisonDelta(s[0].scene,s[2].scene);
 near(d.signedHeading,1.130897108380308-1.9052698814015008);
 near(d.separation,Math.sqrt((.7062456690702007-.7087699494066295)**2+(.23128556782922474-.015621730315911193)**2));
 near(d.traveledDifference,s[0].scene.distance-s[2].scene.distance);
 const o=comparisonOverview(authority);near(o.maxima[0].heading.value,.6766798814084118);near(o.maxima[0].heading.time,5.52);near(o.maxima[1].heading.value,1.1783775624855197);near(o.maxima[1].heading.time,5.6);near(o.maxima[1].separation.value,.4764494359566599);near(o.maxima[1].separation.time,5.58);
 assert.ok(d.separation<o.maxima[1].separation.value);
 assert.deepEqual(o.tracks.map(t=>t.plane),[.4,.4,-.4]);
});
test("contact transitions remain recorded and complete source is never mutated",()=>{
 const before=JSON.stringify(authority);
 for(const [key,t,wall] of [["B",5.5,"Z_WALL"],["C",5.38,"X_WALL"],["D",5.58,"X_WALL"]] as const){
  assert.equal(comparisonScenes(replay,t-.02).find(s=>s.key===key)!.scene.frame.contact,null);
  assert.equal(comparisonScenes(replay,t).find(s=>s.key===key)!.scene.frame.contact,wall);
 }
 assert.equal(JSON.stringify(authority),before);
});
test("incompatible provenance, missing conditions and contradictory environment are rejected",()=>{
 for(const mutate of [(a:typeof authority)=>{a.artifact_id="wrong";},(a:typeof authority)=>{a.result.runs[2].id="NEURAL_STEERING";},(a:typeof authority)=>{a.result.runs[3].condition!.plane_z=.4;}]){const copy=structuredClone(authority);mutate(copy);assert.throws(()=>comparisonOverview(copy));}
 const copy=structuredClone(raw);copy.result.runs[1].frames[200].position[0]=999;assert.throws(()=>parseNeuralLocomotion(copy));
});
