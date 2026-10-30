import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { NeuralCameraGuidance } from '../src/components/NeuralActivityExplorer3D';

const explorer = readFileSync(new URL('../src/components/NeuralActivityExplorer3D.tsx', import.meta.url), 'utf8');
const controls = readFileSync(new URL('../node_modules/three/examples/jsm/controls/OrbitControls.js', import.meta.url), 'utf8');
const styles = readFileSync(new URL('../src/app/visual-lab/arena/lab.css', import.meta.url), 'utf8');

test('navigation guidance is visible text and describes installed OrbitControls defaults', () => {
  const html = renderToStaticMarkup(createElement(NeuralCameraGuidance));
  assert.match(html, /Mouse:<\/strong> left-drag to rotate · right-drag to pan · scroll to zoom/);
  assert.match(html, /Touch:<\/strong> one-finger drag rotates · two-finger drag pans and pinch zooms/);
  assert.match(html, /click or tap a neuron; camera drags do not change selection/);
  assert.match(html, /Focus selected<\/strong> frames the chosen morphology · <strong>Overview<\/strong> restores the full view/);
  assert.doesNotMatch(html, /<(?:button|a|input|select|details|summary)\b|tabindex=/i);

  assert.match(controls, /this\.mouseButtons = \{ LEFT: MOUSE\.ROTATE, MIDDLE: MOUSE\.DOLLY, RIGHT: MOUSE\.PAN \}/);
  assert.match(controls, /this\.touches = \{ ONE: TOUCH\.ROTATE, TWO: TOUCH\.DOLLY_PAN \}/);
  assert.match(controls, /this\.domElement\.addEventListener\( 'wheel', this\._onMouseWheel/);
  assert.match(controls, /this\.enableRotate = true/);
  assert.match(controls, /this\.enablePan = true/);
  assert.match(controls, /this\.enableZoom = true/);
  assert.match(explorer, /const controls = new OrbitControls\(camera, gl\.domElement\)/);
  assert.doesNotMatch(explorer, /controls\.(?:mouseButtons|touches)\s*=/);
});

test('guidance sits by the existing camera actions, wraps in the responsive layout and stays outside the canvas', () => {
  const actions = explorer.indexOf('className="neural-camera-actions"');
  const guidance = explorer.indexOf('<NeuralCameraGuidance />');
  const layout = explorer.indexOf('className="neural-explorer-layout"');
  assert.ok(actions >= 0 && actions < guidance && guidance < layout);
  assert.match(styles, /\.neural-camera-guidance\s*\{[^}]*max-width:\s*100%[^}]*overflow-wrap:\s*anywhere/);
  assert.match(styles, /\.neural-camera-guidance\s*>\s*span\s*\{\s*display:\s*block\s*;/);
  assert.doesNotMatch(styles.match(/\.neural-camera-guidance\s*\{[^}]*\}/)?.[0] ?? '', /position:\s*absolute/);
  assert.equal((explorer.match(/<Canvas\s/g) ?? []).length, 1);
});

test('guidance leaves camera actions, shared selection and the gesture-safe picker unchanged', () => {
  assert.match(explorer, /Focus selected<\/button>/);
  assert.match(explorer, /actions\?\.focus\(\)/);
  assert.match(explorer, /Overview<\/button>/);
  assert.match(explorer, /actions\?\.overview\(\)/);
  assert.match(explorer, /gesture\.consume\(event\.nativeEvent\)[\s\S]*onSelect\(body\.identity\.body_id\)/);
  assert.match(explorer, /onSelect=\{setSelectedId\}/);
  assert.match(explorer, /const controls = new OrbitControls\(camera, gl\.domElement\)/);
  assert.match(explorer, /controls\.minDistance = 4/);
  assert.match(explorer, /controls\.maxDistance = 28/);
  assert.match(explorer, /controls\.enableDamping = false/);
});
