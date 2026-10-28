import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { PerspectiveCamera, Matrix4, Vector3, Vector2, Raycaster, BufferGeometry, Float32BufferAttribute, LineSegments, LineBasicMaterial } from 'three';
import { pickNeuralSegments } from '../src/lib/neuralScreenPicking';
import { parseNeuralMorphologyManifest, parseMaleCnsSwc, deriveNeuralMorphologyView } from '../src/lib/neuralMorphologyExplorer';
import { fitNeuralCamera, presentationBounds } from '../src/lib/neuralCameraFraming';
const world=new Matrix4(), size={width:600,height:410};
function camera(){const c=new PerspectiveCamera(42,size.width/size.height,.1,100);c.updateMatrixWorld();c.updateProjectionMatrix();return c;}
test('CSS distance boundary, projection zoom/resize and source immutability',()=>{
 const c=camera(), data=[-1,0,-5,1,0,-5], before=[...data];
 for(const height of [250,410]) for(const zoom of [1,2]) {c.aspect=320/height;c.zoom=zoom;c.updateProjectionMatrix();const v={width:320,height};
 assert.equal(pickNeuralSegments(data,world,c,v,{x:0,y:2*5.9/height}).status,'hit');
 assert.equal(pickNeuralSegments(data,world,c,v,{x:0,y:2*6.1/height}).status,'miss');}
 assert.deepEqual(data,before);
});
test('frustum clipping rejects invisible segments and handles near/far crossings and points',()=>{
 const c=camera();
 for(const data of [[-1,0,1,1,0,2],[-1,0,-101,1,0,-102],[NaN,0,-1,1,0,-1]]) assert.notEqual(pickNeuralSegments(data,world,c,size,{x:0,y:0}).status,'hit');
 for(const data of [[0,0,1,0,0,-2],[0,0,-99,0,0,-110],[0,0,-2,0,0,-2],[-100,0,-5,1,0,-5]]) assert.equal(pickNeuralSegments(data,world,c,size,{x:0,y:0}).status,'hit');
 assert.equal(pickNeuralSegments([],world,c,{width:0,height:410},{x:0,y:0}).status,'invalid');
 assert.equal(pickNeuralSegments([0,0,-1,0,0,-1],world,c,size,{x:0,y:0},NaN).status,'invalid');
});
test('real-data regression and bounded Overview/Focus probes retain only eligible bodies',()=>{
 const root=new URL('../public/assets/neural/malecns-v1.0/hs-dnp15/',import.meta.url);
 const m=parseNeuralMorphologyManifest(JSON.parse(readFileSync(new URL('manifest.json',root),'utf8')));
 const v=deriveNeuralMorphologyView(m.bodies.map(b=>parseMaleCnsSwc(readFileSync(new URL(b.morphology.path,root),'utf8'),b)));
 const objects=v.bodies.map(b=>{const g=new BufferGeometry();g.setAttribute('position',new Float32BufferAttribute(b.view_positions,3));const o=new LineSegments(g,new LineBasicMaterial());o.userData.id=b.identity.body_id;o.updateMatrixWorld();return o;});
 for(const mode of ['Overview','Focus']) {
 const c=camera();c.position.set(0,5.8,13.5);let target=new Vector3();
 if(mode==='Focus'){const f=fitNeuralCamera(presentationBounds(v,10015),{direction:[0,-5.8,-13.5],up:[0,1,0],fov:42,aspect:c.aspect,zoom:1,near:.1,far:100,minDistance:4,maxDistance:28,margin:.12});assert.ok(f.ok);if(f.ok){c.position.fromArray(f.position);target.fromArray(f.target);}}
 c.lookAt(target);c.updateMatrixWorld();const ray=new Raycaster();
 const pointer=new Vector3(...v.bodies[0].view_positions.slice(0,3)).project(c);ray.setFromCamera(new Vector2(pointer.x,pointer.y),c);
 assert.equal(ray.intersectObjects(objects,false)[0].object.userData.id,11215);
 const candidates=()=>v.bodies.flatMap(b=>{const h=pickNeuralSegments(b.view_positions,world,c,size,pointer);return h.status==='hit'?[{id:b.identity.body_id,...h}]:[]}).sort((a,b)=>a.depth-b.depth || a.id-b.id);
 const regression=candidates();assert.ok(regression.some(h=>h.id===10015));console.log("REGRESSION", mode, regression.map(h=>({id:h.id,pixels:h.pixels,depth:h.depth})));
 const oldHit=ray.intersectObjects(objects,false)[0];const oldSegment=v.bodies.find(b=>b.identity.body_id===11215)!.view_positions.slice(oldHit.index!*3,oldHit.index!*3+6);assert.equal(pickNeuralSegments(oldSegment,world,c,size,pointer).status,"miss");
 if(mode==="Focus") assert.equal(regression[0].id,10015);
 regression.forEach(h=>assert.ok(h.pixels<=6));
 let samples=0, overlaps=0, rejectedOld=0;const start=performance.now();
 for(const b of v.bodies) for(let j=0;j<12;j++) {const i=Math.floor((b.view_positions.length/3-1)*j/11)*3;pointer.fromArray(b.view_positions,i).project(c);if(Math.abs(pointer.x)>1||Math.abs(pointer.y)>1||Math.abs(pointer.z)>1)continue;samples++;
 const hits=candidates();hits.forEach(h=>assert.ok(h.pixels<=6));if(hits.length>1)overlaps++;
 ray.setFromCamera(new Vector2(pointer.x,pointer.y),c);const old=ray.intersectObjects(objects,false)[0]?.object.userData.id;if(old && !hits.some(h=>h.id===old))rejectedOld++;
 }
 console.log(JSON.stringify({mode,samples,overlaps,rejectedOld,diagnosticMilliseconds:performance.now()-start}));
 }
 objects.forEach(o=>{o.geometry.dispose();(o.material as LineBasicMaterial).dispose();});
});
test('local raycast preserves one selection path and excludes pointer-move handlers',()=>{
 const s=readFileSync(new URL('../src/components/NeuralActivityExplorer3D.tsx',import.meta.url),'utf8');
 assert.match(s,/raycast=\{raycast\}/);assert.match(s,/onSelect\(body.identity.body_id\)/);assert.match(s,/onSelect=\{setSelectedId\}/);
 assert.equal((s.match(/<Canvas\s/g)??[]).length,1);assert.doesNotMatch(s,/onPointerMove|useFrame|requestAnimationFrame/);
});
test('depth ordering and transformed camera use eligible visible points',()=>{
 const c=camera();c.position.set(3,2,4);c.lookAt(0,0,0);c.updateMatrixWorld();
 const near=new Vector3(0,0,-3).applyMatrix4(c.matrixWorld),far=new Vector3(0,0,-8).applyMatrix4(c.matrixWorld);
 const segment=(v:Vector3)=>[...v.toArray(),...v.toArray()];
 const a=pickNeuralSegments(segment(near),world,c,size,{x:0,y:0}),b=pickNeuralSegments(segment(far),world,c,size,{x:0,y:0});
 assert.equal(a.status,'hit');assert.equal(b.status,'hit');if(a.status==='hit'&&b.status==='hit')assert.ok(a.depth<b.depth);
 assert.equal(pickNeuralSegments(segment(near),world,c,size,{x:.8,y:.8}).status,'miss');
});
