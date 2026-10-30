import test from 'node:test';
import assert from 'node:assert/strict';
import { act, createElement, StrictMode } from 'react';
import { createRoot, extend } from '@react-three/fiber';
import * as THREE from 'three';
import { Skeleton } from '../src/components/NeuralActivityExplorer3D';
import { NeuralSelectionGesture } from '../src/components/neuralSelectionGesture';
import type { DisplayNeuralMorphology } from '../src/lib/neuralMorphologyExplorer';

// Exercise the installed R3F reconciler with real Three objects and a stub renderer.
(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
extend({ LineSegments: THREE.LineSegments, LineBasicMaterial: THREE.LineBasicMaterial });
async function makeRoot() {
  const canvas = { width: 100, height: 100, style: {} } as unknown as HTMLCanvasElement;
  const gl = { isWebGLRenderer: true, setPixelRatio() {}, setSize() {}, render() {}, shadowMap: {}, renderLists: { dispose() {} }, forceContextLoss() {}, xr: { enabled: false, isPresenting: false, addEventListener() {}, removeEventListener() {}, setAnimationLoop() {} } } as unknown as THREE.WebGLRenderer;
  const root = createRoot(canvas);
  await root.configure({ gl, size: { width: 100, height: 100, top: 0, left: 0 }, frameloop: 'never' });
  return root;
}
const body = (id: number, positions: Float32Array) => ({ identity: { body_id: id }, view_positions: positions }) as unknown as DisplayNeuralMorphology;
const gesture = new NeuralSelectionGesture();
const select = () => {};
const tree = (b: DisplayNeuralMorphology, value: number, selected: boolean) => createElement(StrictMode, null, createElement(Skeleton, { body: b, value, selected, onSelect: select, gesture }));

test('R3F does not dispose a geometry supplied as a line property', async () => {
  const root = await makeRoot(), geometry = new THREE.BufferGeometry();
  let disposed = 0; geometry.addEventListener('dispose', () => disposed++);
  await act(async () => { root.render(createElement('lineSegments', { geometry })); });
  await act(async () => { root.render(null); });
  assert.equal(disposed, 0);
  geometry.dispose();
  await act(async () => { root.unmount(); });
});

test('real skeleton geometry survives updates and StrictMode, and R3F releases it on replacement and remount', async () => {
  const root = await makeRoot();
  const positions = new Float32Array([0, 0, 0, 1, 2, 3]);
  const firstBody = body(10015, positions);
  let store: ReturnType<typeof root.render>;
  await act(async () => { store = root.render(tree(firstBody, 0.2, false)); });
  const line = store!.getState().scene.children[0] as THREE.LineSegments;
  const first = line.geometry; let firstDisposed = 0;
  first.addEventListener('dispose', () => firstDisposed++);
  assert.deepEqual(Array.from(first.getAttribute('position').array), Array.from(positions));
  assert.equal(first.getAttribute('position').count, 2);
  assert.ok(first.boundingSphere);
  await act(async () => { root.render(tree(firstBody, -0.3, true)); });
  assert.equal(line.geometry, first); assert.equal(firstDisposed, 0);
  const secondBody = body(10015, new Float32Array([4, 5, 6, 7, 8, 9]));
  await act(async () => { root.render(tree(secondBody, 0, false)); });
  const second = line.geometry; let secondDisposed = 0;
  second.addEventListener('dispose', () => secondDisposed++);
  assert.notEqual(second, first); assert.equal(firstDisposed, 1);
  assert.deepEqual(Array.from(second.getAttribute('position').array), Array.from(secondBody.view_positions));
  await act(async () => { root.render(null); });
  assert.equal(firstDisposed, 1); assert.equal(secondDisposed, 1);
  await act(async () => { root.render(tree(secondBody, 0, true)); });
  const remounted = (store!.getState().scene.children[0] as THREE.LineSegments).geometry;
  assert.notEqual(remounted, second); assert.ok(remounted.boundingSphere);
  let remountedDisposed = 0; remounted.addEventListener('dispose', () => remountedDisposed++);
  await act(async () => { root.render(null); root.render(null); });
  assert.equal(remountedDisposed, 1); assert.equal(secondDisposed, 1);
  await act(async () => { root.unmount(); });
});

test('independent skeleton owners do not share their geometry', async () => {
  const root = await makeRoot(), positions = new Float32Array([0, 0, 0, 1, 1, 1]);
  let store: ReturnType<typeof root.render>;
  await act(async () => { store = root.render(createElement(StrictMode, null, tree(body(10015, positions), 0, false), tree(body(10016, positions), 0, false))); });
  const lines = store!.getState().scene.children as THREE.LineSegments[];
  assert.equal(lines.length, 2); assert.notEqual(lines[0].geometry, lines[1].geometry);
  let disposed = 0; lines[0].geometry.addEventListener('dispose', () => disposed++);
  await act(async () => { root.render(null); }); assert.equal(disposed, 1);
  await act(async () => { root.unmount(); });
});
