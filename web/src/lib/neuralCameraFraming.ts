import { Vector3 } from 'three';
import type { MorphologySourceBounds, NeuralMorphologyView } from './neuralMorphologyExplorer';

export const NEURAL_OVERVIEW = { position: [0, 5.8, 13.5], target: [0, 0, 0] } as const;
export type CameraFit = { ok: true; position: [number, number, number]; target: [number, number, number] } | { ok: false; reason: string };
export function presentationBounds(view: NeuralMorphologyView, bodyId: number): MorphologySourceBounds | null {
  const body = view.bodies.find(b => b.identity.body_id === bodyId);
  if (!body || !Number.isFinite(view.uniform_scale) || view.uniform_scale <= 0 || !view.center_source.every(Number.isFinite)) return null;
  const minimum = body.source_bounds.minimum.map((v, i) => (v - view.center_source[i]) * view.uniform_scale) as [number, number, number];
  const maximum = body.source_bounds.maximum.map((v, i) => (v - view.center_source[i]) * view.uniform_scale) as [number, number, number];
  if (![...minimum, ...maximum].every(Number.isFinite) || minimum.some((v, i) => v > maximum[i])) return null;
  return { minimum, maximum };
}

/** Bounds are in the unchanged shared presentation space. Margin is an NDC inset. */
export function fitNeuralCamera(bounds: MorphologySourceBounds | null, input: {
  direction: readonly number[]; up: readonly number[]; fov: number; aspect: number; zoom: number;
  near: number; far: number; minDistance: number; maxDistance: number; margin: number;
}): CameraFit {
  const fail = (reason: string): CameraFit => ({ ok: false, reason });
  const { fov, aspect, zoom, near, far, minDistance, maxDistance, margin } = input;
  if (!bounds || ![...bounds.minimum, ...bounds.maximum, fov, aspect, zoom, near, far, minDistance, maxDistance, margin].every(Number.isFinite) || bounds.minimum.some((v, i) => v > bounds.maximum[i]) || fov <= 0 || fov >= 180 || aspect <= 0 || zoom <= 0 || near <= 0 || far <= near || minDistance < 0 || maxDistance < minDistance || margin <= 0 || margin >= 1) return fail('Invalid bounds or camera configuration.');
  const low = new Vector3(...bounds.minimum), high = new Vector3(...bounds.maximum);
  if (low.distanceTo(high) === 0) return fail('Selected bounds have no extent.');
  const target = low.clone().add(high).multiplyScalar(.5);
  const forward = new Vector3().fromArray(input.direction);
  if (input.direction.length !== 3 || !input.direction.every(Number.isFinite) || forward.lengthSq() < 1e-16) forward.set(0, -5.8, -13.5);
  forward.normalize();
  const up = new Vector3().fromArray(input.up);
  if (input.up.length !== 3 || !input.up.every(Number.isFinite) || up.lengthSq() < 1e-16) return fail('Invalid camera up vector.');
  const right = forward.clone().cross(up).normalize();
  if (right.lengthSq() < 1e-16) return fail('Camera orientation is degenerate.');
  const vertical = right.clone().cross(forward).normalize();
  const ty = Math.tan(fov * Math.PI / 360) / zoom * (1 - margin), tx = ty * aspect;
  let distance = minDistance, upper = maxDistance;
  for (const x of [low.x, high.x]) for (const y of [low.y, high.y]) for (const z of [low.z, high.z]) {
    const q = new Vector3(x, y, z).sub(target), depth = q.dot(forward);
    distance = Math.max(distance, Math.abs(q.dot(right)) / tx - depth, Math.abs(q.dot(vertical)) / ty - depth, near * 1.001 - depth);
    upper = Math.min(upper, far * .999 - depth);
  }
  distance += 1e-7; // conservative floating-point guard
  if (!Number.isFinite(distance) || distance > upper) return fail('Selected structure cannot fit within the current camera limits.');
  const position = target.clone().addScaledVector(forward, -distance);
  if (![...position.toArray(), ...target.toArray()].every(Number.isFinite)) return fail('Camera result is unavailable.');
  return { ok: true, position: position.toArray(), target: target.toArray() };
}
