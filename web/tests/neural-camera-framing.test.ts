import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { PerspectiveCamera, Vector3 } from 'three';
import { fitNeuralCamera, presentationBounds, NEURAL_OVERVIEW } from '../src/lib/neuralCameraFraming';
import { parseNeuralMorphologyManifest, parseMaleCnsSwc, deriveNeuralMorphologyView } from '../src/lib/neuralMorphologyExplorer';
const base = { direction: [0,-5.8,-13.5], up: [0,1,0], fov:42, aspect:1.5, zoom:1, near:.1, far:100, minDistance:4, maxDistance:28, margin:.12 };
const bounds = { minimum:[-1,-2,-3] as [number,number,number], maximum:[1,2,3] as [number,number,number] };
function verify(b: { readonly minimum: readonly [number,number,number]; readonly maximum: readonly [number,number,number] }, config = base) {
  const before = structuredClone(b), result=fitNeuralCamera(b,config);
  assert.equal(result.ok,true, JSON.stringify(result)); if(!result.ok) return;
  const camera=new PerspectiveCamera(config.fov,config.aspect,config.near,config.far);
  camera.zoom=config.zoom;camera.position.fromArray(result.position);camera.up.fromArray(config.up);camera.lookAt(new Vector3(...result.target));camera.updateProjectionMatrix();camera.updateMatrixWorld();
  for(const x of [b.minimum[0],b.maximum[0]]) for(const y of [b.minimum[1],b.maximum[1]]) for(const z of [b.minimum[2],b.maximum[2]]) {
    const p=new Vector3(x,y,z).project(camera);assert.ok(Math.abs(p.x)<=1-config.margin+1e-7);assert.ok(Math.abs(p.y)<=1-config.margin+1e-7);assert.ok(p.z>=-1 && p.z<=1);
  }
  assert.deepEqual(b,before);assert.deepEqual(fitNeuralCamera(b,config),result);
}
test('depth-aware fits contain corners under wide/narrow aspect, zoom and rotated orientations',()=>{
 for(const aspect of [.4,1,2.5]) for(const direction of [[0,0,-1],[1,2,3],[-2,.5,1]]) for(const zoom of [.8,1.2]) verify(bounds,{...base,aspect,direction,zoom,maxDistance:100,far:200});
 verify({minimum:[0,0,0],maximum:[0,1,0]});
 verify({minimum:[1,1,1],maximum:[1.00001,1.00001,1.00001]});
 verify({minimum:[-.1,-.1,-9],maximum:[.1,.1,9]},{...base,maxDistance:60});
});
test('unsafe bounds, projection, clipping and controls constraints fail explicitly',()=>{
 assert.equal(fitNeuralCamera(null,base).ok,false);
 assert.equal(fitNeuralCamera({minimum:[0,0,0],maximum:[0,0,0]},base).ok,false);
 assert.equal(fitNeuralCamera({minimum:[NaN,0,0],maximum:[1,1,1]},base).ok,false);
 assert.equal(fitNeuralCamera({minimum:[2,0,0],maximum:[1,1,1]},base).ok,false);
 for(const patch of [{fov:0},{fov:180},{aspect:0},{zoom:0},{far:1},{near:20,far:21},{maxDistance:4},{margin:0},{up:[0,0,0]}]) assert.equal(fitNeuralCamera(bounds,{...base,...patch}).ok,false,JSON.stringify(patch));
 verify(bounds,{...base,direction:[0,0,0]});
});
test('all eight real shared-space boxes fit without source mutation, including mobile aspects',()=>{
 const root=new URL('../public/assets/neural/malecns-v1.0/hs-dnp15/',import.meta.url);
 const manifest=parseNeuralMorphologyManifest(JSON.parse(readFileSync(new URL('manifest.json',root),'utf8')));
 const bodies=manifest.bodies.map(b=>parseMaleCnsSwc(readFileSync(new URL(b.morphology.path,root),'utf8'),b));
 const view=deriveNeuralMorphologyView(bodies), before=view.bodies.map(b=>Array.from(b.source_positions));
 for(const b of bodies){const box=presentationBounds(view,b.identity.body_id);assert.ok(box);for(const aspect of [1.5,390/310,320/250,.5]) verify(box,{...base,aspect});}
 assert.equal(presentationBounds(view,-1),null);
 assert.deepEqual(view.bodies.map(b=>Array.from(b.source_positions)),before);
 assert.deepEqual(NEURAL_OVERVIEW,{position:[0,5.8,13.5],target:[0,0,0]});
});
test('camera commands remain explicit and independent of selection, activity and resize effects',()=>{
 const source=readFileSync(new URL('../src/components/NeuralActivityExplorer3D.tsx',import.meta.url),'utf8');
 assert.equal((source.match(/<Canvas\s/g)??[]).length,1);
 assert.match(source,/onClick=\{\(\) => setCameraNotice\(actions\?\.focus\(\)/);
 assert.match(source,/onSelect=\{setSelectedId\}/);
 assert.match(source,/aspect: camera.aspect/);
 assert.match(source,/if \(!result.ok\) return result.reason;\s*camera.position/);
 assert.doesNotMatch(source,/useFrame|requestAnimationFrame|\.advance\(/);
});
