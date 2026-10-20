import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { Group, Mesh, Vector3, Matrix4, Quaternion } from 'three';
import { WING_RIG, flightPose, validateWingConfig, articulateWings } from '../src/lib/articulatedWings';
import { visualNodeIdentity } from '../src/lib/flyVisualNodeIdentity';

async function model() {
  // Same real GLB positions/hierarchy; omit image-only browser APIs in Node.
  const b=readFileSync(new URL('../public/assets/fly/fly_visual_v2f.glb',import.meta.url));
  const length=b.readUInt32LE(12),g=JSON.parse(b.toString('utf8',20,20+length));
  g.materials=g.materials.map((m:{name:string})=>({name:m.name}));delete g.images;delete g.textures;
  const j=Buffer.from(JSON.stringify(g)),padding=Buffer.alloc((4-j.length%4)%4,32),bin=b.subarray(20+length),header=Buffer.alloc(20);
  header.write('glTF');header.writeUInt32LE(2,4);header.writeUInt32LE(20+j.length+padding.length+bin.length,8);header.writeUInt32LE(j.length+padding.length,12);header.write('JSON',16);
  const all=Buffer.concat([header,j,padding,bin]);const {GLTFLoader}=await import('three/examples/jsm/loaders/GLTFLoader.js');
  const gltf=await new GLTFLoader().parseAsync(all.buffer.slice(all.byteOffset,all.byteOffset+all.byteLength),'');
  return {scene:gltf.scene,ids:visualNodeIdentity(gltf.scene,gltf.parser)};
}
const distance=(a:number[],b:number[])=>new Vector3(...a).distanceTo(new Vector3(...b));

test('immutable source and v7.1 descriptor identity, original license and two independently named wings',()=>{
  const b=readFileSync(new URL('../public/assets/fly/fly_visual_v2f.glb',import.meta.url));
  assert.equal(createHash('sha256').update(b).digest('hex'),WING_RIG.source_glb_sha256);
  assert.equal(createHash('sha256').update(readFileSync(new URL('../src/assets/fly_wings_v7_1.json',import.meta.url))).digest('hex'),'f175ede40fd15892d6089d446146b371a4534be048ffa45447a7cb5a740a51ff');
  assert.deepEqual(WING_RIG.wings.map(w=>w.id),['Wing.L','Wing.R']);assert.equal(WING_RIG.license_url,'https://creativecommons.org/licenses/by/4.0/');
});
test('hinges are on real anterior root geometry, adjacent to torso, distinct and correctly sided',async()=>{
  const {scene,ids}=await model();scene.updateMatrixWorld(true);
  const torso=ids.get('Torso.Unseparated') as Mesh;
  for(const w of WING_RIG.wings){const mesh=ids.get(w.id) as Mesh,pivot=new Vector3(...w.pivot);assert.equal(mesh.parent,torso.parent);assert(Math.sign(pivot.x)===w.sign);assert(mesh.matrix.equals(new Matrix4().fromArray(w.rest_matrix)));
    for(const m of [mesh,torso]){const p=m.geometry.getAttribute('position');let nearest=Infinity;for(let n=0;n<p.count;n++)nearest=Math.min(nearest,pivot.distanceTo(new Vector3().fromBufferAttribute(p,n)));assert(nearest<.01);}
    assert(w.pivot[2]>.115);assert.equal(mesh.geometry.getAttribute('position').count,1252);
  }
});
test('explicit state transitions and independent analytic expectations, no grounded wingbeats',()=>{
  assert.equal(flightPose(0).state,'grounded');assert.equal(flightPose(1).state,'takeoff');assert.equal(flightPose(2.25).state,'flying');assert.equal(flightPose(5.75).state,'landing');assert.equal(flightPose(7).state,'grounded');
  for(const t of [0,.2,.9,7,7.4,8]){const p=flightPose(t);assert.equal(p.stroke,0);assert.equal(p.spread,0);assert.equal(p.offset,0);}
  const p=flightPose(3.125);assert.equal(p.envelope,1);assert(Math.abs(p.stroke-.45)<1e-14);assert.equal(p.spread,.95);assert.equal(p.offset,.18);
  const takeoff=flightPose(1.625);assert.equal(takeoff.envelope,.5);assert.equal(takeoff.offset,.09);assert.equal(flightPose(6.375).envelope,.5);
});
test('smooth activation, bounded finite motion and vertical clearance within arena',()=>{
  for(let n=0;n<=8000;n++){const p=flightPose(n/1000);assert(Object.values(p).filter(v=>typeof v==='number').every(Number.isFinite));assert(Math.abs(p.stroke)<=.45);assert(p.spread>=0&&p.spread<=.95);assert(p.offset>=0&&p.offset<=.18);}
  for(const t of [1,2.25,5.75,7]){const a=flightPose(t-1e-6),b=flightPose(t+1e-6);assert(Math.abs(a.offset-b.offset)<1e-6);assert(Math.abs(a.stroke-b.stroke)<2e-6*.45*(2*Math.PI*2+1.2));assert(Math.abs(a.spread-b.spread)<1e-5);}
});
test('invalid time, parameters, identity and hinge configuration rejected',()=>{
  for(const t of [NaN,Infinity,-.01,8.001])assert.throws(()=>flightPose(t));
  for(const [key,value] of [['frequency_hz',NaN],['frequency_hz',0],['duration_s',-1],['stroke_rad',10],['height',1],['hover_s',1]] as const){const c=structuredClone(WING_RIG);c.animation[key]=value;assert.throws(()=>validateWingConfig(c));}
  const c=structuredClone(WING_RIG);c.wings[0].pivot[0]=0;assert.throws(()=>validateWingConfig(c));
});
test('actual original surfaces articulate around stationary hinges; bilateral mirrored rotations and expected tip geometry',async()=>{
  const {scene,ids}=await model(),meshes:number[]=[];scene.traverse(n=>{if(n instanceof Mesh)meshes.push(n.id);});
  const geometries=WING_RIG.wings.map(w=>(ids.get(w.id) as Mesh).geometry),rig=articulateWings(scene,ids),p=flightPose(3.125);rig.apply(p);
  const state=rig.diagnostics();assert.equal(scene.getObjectsByProperty('type','Mesh').length,meshes.length);
  for(let i=0;i<2;i++){
    const w=WING_RIG.wings[i],mesh=ids.get(w.id) as Mesh;assert.equal(mesh.geometry,geometries[i]);
    assert(distance(state[i].root,w.pivot)<1e-12);
    const expected=new Quaternion().setFromAxisAngle(new Vector3(0,0,1),w.sign*.45).multiply(new Quaternion().setFromAxisAngle(new Vector3(0,1,0),-w.sign*.95));
    assert(new Quaternion(...state[i].quaternion).angleTo(expected)<1e-7);
    const attr=mesh.geometry.getAttribute('position');let tip=new Vector3(),max=-1;
    for(let n=0;n<attr.count;n++){const v=new Vector3().fromBufferAttribute(attr,n),d=v.distanceToSquared(new Vector3(...w.pivot));if(d>max){max=d;tip=v;}}
    const expectedTip=tip.sub(new Vector3(...w.pivot)).applyQuaternion(expected).add(new Vector3(...w.pivot));assert(distance(state[i].tip,expectedTip.toArray())<1e-12);
  }
  assert.notDeepEqual(state[0].quaternion,state[1].quaternion);
  rig.dispose();
});
test('seek/paused/replayed poses reproduce exactly, no accumulated drift or FPS dependence',async()=>{
  const {scene,ids}=await model(),rig=articulateWings(scene,ids);rig.apply(flightPose(3.125));const a=rig.diagnostics();
  for(const fps of [3,30,60]){for(let n=0;n<=8*fps;n++)rig.apply(flightPose(n/fps));rig.apply(flightPose(3.125));assert.deepEqual(rig.diagnostics(),a);}
  rig.apply(flightPose(3.125));assert.deepEqual(rig.diagnostics(),a);
  rig.apply(flightPose(0));const initial=rig.diagnostics();rig.apply(flightPose(8));assert.deepEqual(rig.diagnostics(),initial);rig.dispose();
});
test('other geometry, body and all six leg transforms unchanged; original rest restored on disposal without resource duplication',async()=>{
  const {scene,ids}=await model(),before=new Map([...ids].map(([k,v])=>[k,v.matrixWorld.clone()])),rig=articulateWings(scene,ids);
  for(const time of [0,1.5,3.125,5.9,8]){rig.apply(flightPose(time));for(const [id,matrix] of before)if(!id.startsWith('Wing.'))assert(ids.get(id)!.matrixWorld.equals(matrix),id);}
  rig.dispose();scene.updateMatrixWorld(true);for(const [id,m] of before)assert(ids.get(id)!.matrixWorld.equals(m),id);assert.equal(scene.getObjectByName('WingHinge.Wing.L'),undefined);rig.dispose();
});
test('missing/invalid hierarchy fails atomically, safe original surfaces retained',async()=>{
  const {scene,ids}=await model();const parent=ids.get('Wing.L')!.parent;
  const missing=new Map(ids);missing.delete('Wing.R');assert.throws(()=>articulateWings(scene,missing));assert.equal(ids.get('Wing.L')!.parent,parent);assert.equal(scene.getObjectByName('WingHinge.Wing.L'),undefined);
  ids.get('Wing.R')!.position.x=1;scene.updateMatrixWorld(true);assert.throws(()=>articulateWings(scene,ids));
});
test('contradictory state rejected; presentation imports no scientific solver or storage; no scientific serialization',async()=>{
  const {scene,ids}=await model(),rig=articulateWings(scene,ids);assert.throws(()=>rig.apply({...flightPose(3),state:'grounded'}));rig.dispose();
  const source=readFileSync(new URL('../src/lib/articulatedWings.ts',import.meta.url),'utf8'),ui=readFileSync(new URL('../src/components/FlightVisualPreview.tsx',import.meta.url),'utf8');
  for(const name of ['IndependentVisualEngine','NeuralKernel','indexedDB','exportSession','localStorage'])assert(!source.includes(name)&&!ui.includes(name));
});

test('initial and moved presentation parents are included in measured world transforms on the first frame',async()=>{
  const {scene,ids}=await model(),parent=new Group();parent.scale.setScalar(.3);parent.position.set(0,.1,.08);parent.add(scene);const rig=articulateWings(scene,ids);rig.apply(flightPose(0));
  let d=rig.diagnostics();for(let i=0;i<2;i++)assert(distance(d[i].root,WING_RIG.wings[i].pivot.map((v,k)=>v*.3+[0,.1,.08][k]))<1e-12);
  parent.position.y+=.18;rig.apply(flightPose(3.12));d=rig.diagnostics();for(let i=0;i<2;i++)assert(distance(d[i].root,WING_RIG.wings[i].pivot.map((v,k)=>v*.3+[0,.28,.08][k]))<1e-12);rig.dispose();
});
