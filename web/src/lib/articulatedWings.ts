import { Group, Mesh, Matrix4, Quaternion, Vector3, type Object3D } from 'three';
import descriptor from '@/assets/fly_wings_v7_1.json';

export const WING_RIG = descriptor;
export type FlightState = 'grounded' | 'takeoff' | 'flying' | 'landing';
export type WingPose = {
  source: 'ENGINEERING_FLIGHT_VISUAL_DEMO'; time: number; state: FlightState;
  envelope: number; offset: number; phase: number; stroke: number; spread: number;
};
const smooth = (x: number) => x * x * (3 - 2 * x);
export function validateWingConfig(config = WING_RIG) {
  if (config.schema !== 'articulated_wing_motion_v7_1' || config.source_glb_sha256 !== WING_RIG.source_glb_sha256 ||
      config.axes !== 'Y_UP_Z_FORWARD' || config.classification !== 'ENGINEERING_FLIGHT_VISUAL_DEMO' ||
      config.wings.length !== 2) throw new Error('Invalid wing presentation identity');
  for (let i = 0; i < 2; i++) {
    const wing = config.wings[i], expected = WING_RIG.wings[i];
    if (wing.id !== expected.id || wing.sign !== expected.sign || wing.vertices !== expected.vertices ||
        JSON.stringify(wing.pivot) !== JSON.stringify(expected.pivot) ||
        JSON.stringify(wing.rest_matrix) !== JSON.stringify(expected.rest_matrix)) throw new Error('Invalid wing attachment');
  }
  const a = config.animation;
  if (!Object.values(a).every(Number.isFinite) || a.frequency_hz <= 0 || a.frequency_hz > 4 ||
      a.stroke_rad <= 0 || a.stroke_rad > .6 || a.spread_rad < 0 || a.spread_rad > 1.1 ||
      a.height <= 0 || a.height > .25 || !(0 < a.takeoff_s && a.takeoff_s < a.hover_s &&
      a.hover_s < a.landing_s && a.landing_s < a.grounded_s && a.grounded_s < a.duration_s && a.duration_s <= 15)) throw new Error('Invalid engineering wing parameters');
}
validateWingConfig();

/** Pure presentation clock: no neural model, scientific trajectory, or frame count. */
export function flightPose(time: number): WingPose {
  const a = WING_RIG.animation;
  if (!Number.isFinite(time) || time < 0 || time > a.duration_s) throw new Error('Flight presentation time outside supported window');
  const state: FlightState = time < a.takeoff_s || time >= a.grounded_s ? 'grounded' :
    time < a.hover_s ? 'takeoff' : time < a.landing_s ? 'flying' : 'landing';
  const envelope = state === 'grounded' ? 0 : state === 'flying' ? 1 : state === 'takeoff' ?
    smooth((time - a.takeoff_s) / (a.hover_s - a.takeoff_s)) : 1 - smooth((time - a.landing_s) / (a.grounded_s - a.landing_s));
  const phase = 2 * Math.PI * a.frequency_hz * (time - a.takeoff_s);
  return { source: 'ENGINEERING_FLIGHT_VISUAL_DEMO', time, state, envelope,
    offset: a.height * envelope, phase, stroke: envelope === 0 ? 0 : a.stroke_rad * envelope * Math.sin(phase), spread: a.spread_rad * envelope };
}

/** Original mesh surfaces are reparented on this private instance only. No geometry/material copies. */
export function articulateWings(scene: Object3D, identities: ReadonlyMap<string, Object3D>) {
  validateWingConfig();
  scene.updateWorldMatrix(true, true);
  const torso = identities.get('Torso.Unseparated');
  if (!(torso instanceof Mesh)) throw new Error('Missing source torso for wing attachment');
  const entries = WING_RIG.wings.map(config => {
    const mesh = identities.get(config.id);
    if (!(mesh instanceof Mesh) || !mesh.parent || mesh.parent !== torso.parent || mesh.geometry.getAttribute('position').count !== config.vertices ||
        !mesh.matrix.equals(new Matrix4().fromArray(config.rest_matrix))) throw new Error(`Incompatible source wing ${config.id}`);
    const pivot = new Vector3(...config.pivot), points = mesh.geometry.getAttribute('position');
    let nearest = Infinity, farthest = -Infinity;
    const tip = new Vector3(), p = new Vector3();
    for (let i = 0; i < points.count; i++) {
      p.fromBufferAttribute(points, i); const distance = p.distanceToSquared(pivot);
      nearest = Math.min(nearest, distance); if (distance > farthest) { farthest = distance; tip.copy(p); }
    }
    if (nearest > .01 ** 2) throw new Error('Wing pivot not on source attachment geometry');
    return { config, mesh, parent: mesh.parent, rest: mesh.matrix.clone(), pivot, tip, hinge: new Group() };
  });
  for (const e of entries) {
    e.hinge.name = `WingHinge.${e.config.id}`; e.hinge.position.copy(e.pivot);
    e.parent.add(e.hinge); e.hinge.add(e.mesh); e.mesh.position.copy(e.pivot).negate();
    e.mesh.updateMatrix();
  }
  const stroke = new Quaternion(), spread = new Quaternion(), z = new Vector3(0, 0, 1), y = new Vector3(0, 1, 0);
  let disposed = false;
  return {
    apply(pose: WingPose) {
      // Do not accept externally invented states/angles disguised as a valid pose.
      if (disposed || JSON.stringify(pose) !== JSON.stringify(flightPose(pose.time))) throw new Error('Invalid flight presentation state');
      for (const e of entries) {
        stroke.setFromAxisAngle(z, e.config.sign * pose.stroke);
        spread.setFromAxisAngle(y, -e.config.sign * pose.spread);
        e.hinge.quaternion.copy(stroke).multiply(spread);
      }
      scene.updateWorldMatrix(true, true);
    },
    diagnostics() {
      return entries.map(e => ({ id: e.config.id, root: e.hinge.getWorldPosition(new Vector3()).toArray(),
        tip: e.mesh.localToWorld(e.tip.clone()).toArray(), matrix: e.mesh.matrixWorld.toArray(),
        quaternion: e.hinge.quaternion.toArray() }));
    },
    dispose() {
      if (disposed) return;
      for (const e of entries) { e.parent.add(e.mesh); e.rest.decompose(e.mesh.position, e.mesh.quaternion, e.mesh.scale); e.mesh.updateMatrix(); e.hinge.removeFromParent(); }
      disposed = true;
    },
  };
}
