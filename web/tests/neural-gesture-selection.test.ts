import test from 'node:test';
import assert from 'node:assert/strict';
import {createEvents} from '@react-three/fiber';
import {Object3D, PerspectiveCamera, Raycaster, Vector2, Vector3} from 'three';
// Real installed R3F event dispatcher, synthetic intersection, no renderer/anatomy fixture.
function dispatcher(select:(event:{nativeEvent:MouseEvent})=>void) {
 const object=new Object3D();
 const camera=new PerspectiveCamera();camera.updateMatrixWorld();
 const state={camera,pointer:new Vector2(),raycaster:new Raycaster(),events:{enabled:true,priority:1,compute:()=>{state.raycaster.camera=camera;}},internal:{interaction:[object],initialClick:[0,0],initialHits:[] as Object3D[],capturedMap:new Map(),hovered:new Map(),lastEvent:{current:null}}};
 const store={getState:()=>state};
 Object.assign(object,{__r3f:{root:store,eventCount:1,handlers:{onClick:select}}});
 object.raycast=(_ray,hits)=>{hits.push({distance:1,point:new Vector3(),object});};
 const events=createEvents(store as unknown as Parameters<typeof createEvents>[0]);
 return (name:string,x:number,y=0)=>events.handlePointer(name)({offsetX:x,offsetY:y,clientX:x,clientY:y,button:0,pointerId:1,pointerType:'mouse',isPrimary:true,target:{}} as unknown as Parameters<ReturnType<typeof events.handlePointer>>[0]);
}
test('installed R3F permits an object click after a large drag when the initial object is still hit',()=>{let calls=0;const send=dispatcher(()=>calls++);send('onPointerDown',0);send('onPointerMove',30);send('onPointerUp',30);send('onClick',30);assert.equal(calls,1);});

import {NeuralSelectionGesture, bindNeuralSelectionGesture, NEURAL_CLICK_MOVEMENT_PX} from '../src/components/neuralSelectionGesture';
import {readFileSync} from 'node:fs';
const input=(x=0, extra={})=>({clientX:x,clientY:0,pointerId:1,pointerType:'mouse',button:0,isPrimary:true,...extra});
function guarded() {
 const guard=new NeuralSelectionGesture();let selected=10015,calls=0;
 const send=dispatcher(event=>{if(guard.consume(event.nativeEvent)) {selected=11215;calls++;}});
 let position=0;
 return {guard, get selected(){return selected;}, get calls(){return calls;},down(e=input()){position=e.clientX;guard.down(e);send('onPointerDown',position);},move(e:ReturnType<typeof input>){position=e.clientX;guard.move(e);send('onPointerMove',position);},up(e=input()){position=e.clientX;guard.up(e);send('onPointerUp',position);},click(e=input()){position=e.clientX;send('onClick',position);}};
}
test('guarded real R3F dispatch selects exact identity once; normal click recovers after drag',()=>{
 const h=guarded();h.down();h.move(input(30));h.up(input(30));h.click(input(30));assert.equal(h.calls,0);assert.equal(h.selected,10015);
 h.down();h.up();h.click();h.click();assert.equal(h.calls,1);assert.equal(h.selected,11215);
});
test('mouse click jitter at and below 3 CSS px selects; above threshold and away/back never select',()=>{
 for(const x of [0,NEURAL_CLICK_MOVEMENT_PX-.01,NEURAL_CLICK_MOVEMENT_PX]){const h=guarded();h.down();h.move(input(x));h.up(input(x));h.click(input(x));assert.equal(h.calls,1);}
 for(const back of [false,true]){const h=guarded();h.down();h.move(input(NEURAL_CLICK_MOVEMENT_PX+.01));if(back)h.move(input());h.up(input(back?0:3.01));h.click(input(back?0:3.01));assert.equal(h.calls,0);assert.equal(h.selected,10015);}
});
test('nonprimary, right/middle and modified pan sequences do not dispatch selection',()=>{
 for(const extra of [{button:1},{button:2},{shiftKey:true},{ctrlKey:true},{metaKey:true},{altKey:true},{isPrimary:false}]){const h=guarded();h.down(input(0,extra));h.up(input(0,extra));h.click();assert.equal(h.calls,0);}
});
test('single touch tap selects; touch drag and multipointer pinch cannot select, including compatibility click',()=>{
 const tap=guarded();tap.down(input(0,{pointerType:'touch'}));tap.up(input(0,{pointerType:'touch'}));tap.click();tap.click();assert.equal(tap.calls,1);
 const drag=guarded();drag.down(input(0,{pointerType:'touch'}));drag.move(input(20,{pointerType:'touch'}));drag.up(input(20,{pointerType:'touch'}));drag.click(input(20));assert.equal(drag.calls,0);
 const h=guarded();h.down(input(0,{pointerType:'touch'}));h.guard.down(input(1,{pointerId:2,pointerType:'touch',isPrimary:false}));h.guard.up(input(1,{pointerId:2,pointerType:'touch'}));h.up(input(0,{pointerType:'touch'}));h.click();assert.equal(h.calls,0);h.down();h.up();h.click();assert.equal(h.calls,1);
});
test('cancel, lost capture during gesture and invalid coordinates suppress stale clicks',()=>{
 for(const invalidate of [(g:NeuralSelectionGesture)=>g.cancel(),(g:NeuralSelectionGesture)=>g.lost(input()),(g:NeuralSelectionGesture)=>g.move(input(NaN))]){const h=guarded();h.down();invalidate(h.guard);h.up();h.click();assert.equal(h.calls,0);h.down();h.up();h.click();assert.equal(h.calls,1);}
 const h=guarded();h.down();h.up();h.guard.lost(input());h.click();assert.equal(h.calls,1); // ordinary release after pointer-up
});
test('DOM listener wiring cancels leave/wheel/blur, observes global movement and cleans up without capture',()=>{
 class Target extends EventTarget {emit(type:string,e={}){const event=new Event(type);Object.assign(event,input(),e);this.dispatchEvent(event);}}
 const canvas=new Target(),owner=new Target(),g=new NeuralSelectionGesture();
 const cleanup=bindNeuralSelectionGesture(canvas as unknown as HTMLElement,g,owner as unknown as Window);
 for(const kind of ['pointerleave','wheel','blur','pointercancel','lostpointercapture']){canvas.emit('pointerdown');(kind==='blur'||kind==='pointercancel'?owner:canvas).emit(kind);owner.emit('pointerup');assert.equal(g.consume(input()),false);}
 canvas.emit('pointerdown');owner.emit('pointermove',{clientX:10});owner.emit('pointermove');owner.emit('pointerup');assert.equal(g.consume(input()),false);
 canvas.emit('pointerdown');owner.emit('pointerup');assert.equal(g.consume(input()),true);
 canvas.emit('pointerdown');cleanup();owner.emit('pointerup');assert.equal(g.consume(input()),false);
 const fresh=new NeuralSelectionGesture();const remove=bindNeuralSelectionGesture(canvas as unknown as HTMLElement,fresh,owner as unknown as Window);canvas.emit('pointerdown');owner.emit('pointerup');assert.equal(fresh.consume(input()),true);remove();
});
test('component keeps shared selection, native click guard and no new geometry pointer-move path',()=>{
 const s=readFileSync(new URL('../src/components/NeuralActivityExplorer3D.tsx',import.meta.url),'utf8');assert.match(s,/gesture.consume\(event.nativeEvent\)/);assert.match(s,/onSelect\(body.identity.body_id\)/);assert.match(s,/onSelect=\{setSelectedId\}/);assert.equal((s.match(/<Canvas\s/g)??[]).length,1);assert.doesNotMatch(s,/onPointerMove|useFrame|requestAnimationFrame/);
});
