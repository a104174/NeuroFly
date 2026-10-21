import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { Group, Mesh, Vector3 } from 'three';
import { FlightEngine, FlightClock, advanceFlightCursor, FLIGHT_MODEL as M, FLIGHT_DEMO, createFlightTrial, validateFlightTrial, reconstructFlight, flightBounds, initialFlightFrame, flightScene, exportFlight, importFlight, flightHash, type FlightCommand } from '../src/lib/engineeringFlight';
import { flightWingsV8, FLIGHT_WINGS_V8 } from '../src/lib/flightWingsV8';
import { articulateWings, flightPose, WING_RIG } from '../src/lib/articulatedWings';
import { visualNodeIdentity } from '../src/lib/flyVisualNodeIdentity';
import { ARENA } from '../src/lib/experimentalArena';
import { FLY_VIEWER_ASSET } from '../src/lib/flyViewer';

const near = (a: number, b: number, tolerance = 1e-12) => assert(Math.abs(a - b) < tolerance, `${a} != ${b}`);
const command = (intent: FlightCommand['intent'], step = 0, forward = 0, vertical = 0, turn = 0): FlightCommand => ({ id: `${intent}-${step}`, step, intent, forward, vertical, turn });
const run = (commands: readonly FlightCommand[], stop = 600) => reconstructFlight(createFlightTrial(commands, stop));

test('independent engineering identity, real arena axes, clearances and fixed initial anchor', () => {
  const t = createFlightTrial(), f = new FlightEngine(t).snapshot();
  assert.equal(t.classification, 'ENGINEERING_KINEMATIC_FLIGHT'); assert.equal(M.dt_s, .02); assert.equal(M.axes, 'Y_UP_Z_FORWARD');
  const anchor = FLY_VIEWER_ASSET.canonical_transform.visual_anchor!.position;
  assert.deepEqual(f.position, anchor.map((v, i) => v * .3 + ARENA.flyOffset[i]));
  assert.equal(f.state, 'grounded'); assert.deepEqual(f.velocity, [0, 0, 0]);
  t.initial.position[1] += .1; assert.throws(() => new FlightEngine(t));
  const b = flightBounds(); assert(b.min[0] < 0 && b.max[0] > 0 && b.max[1] < ARENA.chamber.height && b.max[2] < ARENA.chamber.depth / 2);
});
test('independent semi-implicit acceleration expectation, exact event interval and no future lookahead', () => {
  const e = new FlightEngine(); for (let i = 0; i < 50; i++) { const f = e.advance(); assert.equal(f.state, 'grounded'); assert.deepEqual(f.position, initialFlightFrame().position); }
  const a = e.advance(); assert.equal(a.time, 1.02); assert.equal(a.state, 'takeoff');
  near(a.velocity[1], .32 * .02); near(a.position[1] - M.ground_y, .32 * .02 ** 2);
  assert.deepEqual(a.events.map(e => [e.kind, e.step, e.time]), [['COMMAND', 50, 1], ['TRANSITION', 50, 1]]);
  for (let i = 1; i < 10; i++) e.advance();
  near(e.snapshot().position[1] - M.ground_y, .32 * .02 ** 2 * 10 * 11 / 2);
  assert.equal(e.snapshot().step, 60);
});
test('integrated demo takes off, translates, climbs, turns, descends, lands and stops', () => {
  const e = reconstructFlight(createFlightTrial()), fs = e.frames(), end = e.snapshot();
  assert.equal(fs.length, 601); assert.equal(fs[49].state, 'grounded'); assert.equal(fs[51].state, 'takeoff');
  assert(fs.some(f => f.state === 'flying')); assert(fs.some(f => f.state === 'landing')); assert.equal(end.state, 'grounded');
  assert.equal(end.position[1], M.ground_y); assert.deepEqual(end.velocity, [0, 0, 0]);
  assert(fs[350].position[1] > fs[250].position[1]); assert(fs[450].position[1] < fs[350].position[1]);
  assert(fs[350].heading > fs[250].heading); assert(fs[450].heading < fs[350].heading);
  assert(Math.hypot(end.position[0], end.position[2] - fs[0].position[2]) > .3);
  assert(e.events().some(e => e.kind === 'CONTACT' && e.detail === 'FLOOR'));
  const commands = e.events().filter(e => e.kind === 'COMMAND'); assert.deepEqual(commands.map(e => e.step), FLIGHT_DEMO.map(e => e.step));
  assert.throws(() => e.advance()); assert.throws(() => e.frame(601));
});
test('velocities, acceleration, heading and all spatial bounds remain finite under ceiling and lateral contacts', () => {
  const e = run([command('TAKEOFF', 0, 1, 1), command('HOLD', 500, 1, 1, 1), command('HOLD', 600, 1, 1, 0)], 1500), fs = e.frames(), b = flightBounds();
  for (const f of fs) {
    assert([...f.position, ...f.velocity, f.heading].every(Number.isFinite));
    assert(Math.hypot(f.velocity[0], f.velocity[2]) <= M.max_forward_speed + 1e-12); assert(Math.abs(f.velocity[1]) <= M.max_vertical_speed);
    f.position.forEach((v, i) => assert(v >= b.min[i] - 1e-12 && v <= b.max[i] + 1e-12));
  }
  for (const contact of ['CEILING', 'X_WALL', 'Z_WALL']) assert(e.events().some(e => e.detail === contact), contact);
  near(fs[501].heading - fs[500].heading, .8 * .02);
  for (let i = 1; i < fs.length; i++) if (!fs[i].contacts.length) {
    assert(Math.hypot(fs[i].velocity[0] - fs[i - 1].velocity[0], fs[i].velocity[2] - fs[i - 1].velocity[2]) <= .45 * .02 + 1e-12);
  }
});
test('empty schedule is stationary; grounded motion and illegal/repeated intents rejected without teleporting', () => {
  const e = run([], 100); assert(e.frames().every(f => JSON.stringify(f.position) === JSON.stringify(initialFlightFrame().position)));
  const grounded = run([command('LAND', 0, 1, 1, 1)], 10); assert(grounded.events().some(e => e.kind === 'REJECTED_COMMAND')); assert.deepEqual(grounded.snapshot().position, initialFlightFrame().position);
  const repeated = run([command('TAKEOFF'), command('TAKEOFF', 20), command('LAND', 80), command('LAND', 81)], 200);
  assert.equal(repeated.events().filter(e => e.kind === 'REJECTED_COMMAND').length, 2);
  assert.equal(repeated.snapshot().state, 'grounded');
});
test('invalid/off-grid/contradictory commands, wrong model/initial state and unsupported durations rejected', () => {
  for (const stop of [0, -1, .5, 1501, NaN]) assert.throws(() => createFlightTrial([], stop));
  for (const commands of [[command('TAKEOFF', -.1)], [command('TAKEOFF', .5)], [command('TAKEOFF', 600)], [command('TAKEOFF'), command('LAND')], [command('TAKEOFF', 10), command('LAND', 1)], [command('TAKEOFF', 0, NaN)]]) assert.throws(() => createFlightTrial(commands));
  for (const field of ['forward', 'vertical', 'turn'] as const) { const c = command('HOLD'); c[field] = Infinity; assert.throws(() => createFlightTrial([c])); c[field] = 1.01; assert.throws(() => createFlightTrial([c])); }
  const t = createFlightTrial(); (t.model as { dt_s: number }).dt_s = .01; assert.throws(() => validateFlightTrial(t));
  assert.throws(() => createFlightTrial([], 30, 'unknown' as 'normal'));
});
test('body positions depend on integrated inputs; deleting forward or turning command changes the computed path', () => {
  const full = reconstructFlight(createFlightTrial()), noForward = run(FLIGHT_DEMO.map(c => ({ ...c, forward: 0 }))), noTurn = run(FLIGHT_DEMO.map(c => ({ ...c, turn: 0 })));
  assert.notDeepEqual(full.snapshot().position, noForward.snapshot().position); assert.notDeepEqual(full.snapshot().position, noTurn.snapshot().position);
  assert.deepEqual(noForward.snapshot().position.filter((_, i) => i !== 1), initialFlightFrame().position.filter((_, i) => i !== 1));
});
test('pause/resume/reset/seek and 3/30/60 FPS clocks preserve exact states; catch-up only changes pacing', () => {
  const expected = reconstructFlight(createFlightTrial()).frames();
  for (const fps of [3, 30, 60]) {
    const e = new FlightEngine(), clock = new FlightClock(); let limited = false, paused = false;
    while (e.snapshot().step < e.stopStep) { const r = clock.advance(e, 1000 / fps); limited ||= r.limited; if (e.snapshot().step > 100 && !paused) { clock.reset(); paused = true; } }
    assert.deepEqual(e.frames(), expected); assert.equal(limited, false);
    const copy = e.frame(100); e.frame(400); assert.deepEqual(e.frame(100), copy); copy.position[0] = 100; assert.notEqual(e.frame(100).position[0], 100);
    assert.deepEqual(new FlightEngine().snapshot(), initialFlightFrame());
  }
  assert.throws(() => new FlightClock().advance(new FlightEngine(), -1));
  const e = new FlightEngine(); assert(new FlightClock().advance(e, 5000).limited); assert.equal(e.snapshot().step, 50);
});
test('engineering export reconstructs complete and prefix trials, rejects recomputed-hash semantic tampering and foreign sessions', async () => {
  for (const stop of [0, 200, 600]) {
    const e = reconstructFlight(createFlightTrial(), stop), artifact = await exportFlight(e, 'normal');
    assert.deepEqual((await importFlight(artifact)).frames(), e.frames()); assert.equal(artifact.termination, stop === 600 ? 'DURATION_COMPLETED' : 'RECORDED_PREFIX');
    const bad = structuredClone(artifact); bad.frames.at(-1)!.position[0] += .01; bad.result_sha256 = await flightHash({ frames: bad.frames, termination: bad.termination });
    await assert.rejects(importFlight(bad));
  }
  await assert.rejects(importFlight({ schema: 'experiment_session_library_v5' }));
  const bad = await exportFlight(new FlightEngine(), 'normal'); bad.trial.initial.heading = 0; bad.input_sha256 = await flightHash(bad.trial); await assert.rejects(importFlight(bad));
});
test('seeking and replaying computed history reads telemetry without executing the plant', () => {
  const e = reconstructFlight(createFlightTrial(), 200), history = e.frames();
  for (let step = 0; step < 200; step++) assert.deepEqual(advanceFlightCursor(e, step), history[step + 1]);
  assert.deepEqual(e.frames(), history); assert.equal(advanceFlightCursor(e, 200).step, 201);
  assert.throws(() => advanceFlightCursor(e, 300));
});
test('fixed normal/inspection presets, 12 Hz analytic phase, unchanged original 2 Hz descriptor and no scientific feedback', () => {
  assert.equal(FLIGHT_WINGS_V8.presets.normal, 12); assert.equal(FLIGHT_WINGS_V8.presets.inspection, 2);
  for (const time of [1.02, 3.12, 5.37, 10.1]) {
    const fast = flightWingsV8(time, 'flying', .1, 'normal'), slow = flightWingsV8(time, 'flying', .1, 'inspection');
    near(fast.phase, 2 * Math.PI * 12 * time); near(fast.phase, 6 * slow.phase); near(fast.stroke, .45 * Math.sin(24 * Math.PI * time));
    assert.equal(fast.offset, 0); assert.equal(slow.offset, 0);
  }
  assert.equal(flightPose(3.125).stroke, .45);
  const bytes = readFileSync(new URL('../src/assets/fly_wings_v7_1.json', import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), FLIGHT_WINGS_V8.rig_sha256);
  const normal = reconstructFlight(createFlightTrial()), slow = reconstructFlight(createFlightTrial(FLIGHT_DEMO, 600, 'inspection')); assert.deepEqual(normal.frames(), slow.frames());
  for (const time of [0, 1, 100]) assert.equal(flightWingsV8(time, 'grounded', 0, 'normal').stroke, 0);
  for (const time of [-1, NaN, Infinity]) assert.throws(() => flightWingsV8(time, 'flying', .1, 'normal'));
  assert.throws(() => flightWingsV8(1, 'grounded', .1, 'normal'));
});

async function model() {
  const b = readFileSync(new URL('../public/assets/fly/fly_visual_v2f.glb', import.meta.url)), length = b.readUInt32LE(12), g = JSON.parse(b.toString('utf8', 20, 20 + length));
  g.materials = g.materials.map((m: { name: string }) => ({ name: m.name })); delete g.images; delete g.textures;
  const j = Buffer.from(JSON.stringify(g)), pad = Buffer.alloc((4 - j.length % 4) % 4, 32), bin = b.subarray(20 + length), header = Buffer.alloc(20);
  header.write('glTF'); header.writeUInt32LE(2, 4); header.writeUInt32LE(20 + j.length + pad.length + bin.length, 8); header.writeUInt32LE(j.length + pad.length, 12); header.write('JSON', 16);
  const all = Buffer.concat([header, j, pad, bin]), { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js');
  const gltf = await new GLTFLoader().parseAsync(all.buffer.slice(all.byteOffset, all.byteOffset + all.byteLength), '');
  return { scene: gltf.scene, ids: visualNodeIdentity(gltf.scene, gltf.parser) };
}
test('actual original wing surfaces and plant body transform: attached roots, bounded geometry, stable other limbs and no phase drift', async () => {
  const { scene, ids } = await model(), parent = new Group(), assetOffset = new Group(); parent.scale.setScalar(.3); assetOffset.position.fromArray(flightScene(initialFlightFrame()).assetOffset); parent.add(assetOffset); assetOffset.add(scene);
  const rig = articulateWings(scene, ids), fs = reconstructFlight(createFlightTrial()).frames();
  const originals = new Map([...ids].filter(([id]) => !id.startsWith('Wing.')).map(([id, n]) => [id, n.matrix.clone()]));
  for (const frame of fs.filter((_, i) => i % 5 === 0)) {
    parent.position.fromArray(frame.position); parent.rotation.y = frame.heading;
    const pose = flightWingsV8(frame.time, frame.state, frame.position[1] - M.ground_y, 'normal'); rig.apply(pose);
    const d = rig.diagnostics();
    for (let i = 0; i < 2; i++) {
      const expected = new Vector3(...WING_RIG.wings[i].pivot).add(assetOffset.position).multiplyScalar(.3).applyAxisAngle(new Vector3(0, 1, 0), frame.heading).add(parent.position);
      near(new Vector3(...d[i].root).distanceTo(expected), 0);
    }
    for (const [id, matrix] of originals) assert(ids.get(id)!.matrix.equals(matrix));
    scene.traverse(n => { if (n instanceof Mesh) { const p = n.geometry.getAttribute('position'); for (let i = 0; i < p.count; i++) {
      const point = n.localToWorld(new Vector3().fromBufferAttribute(p, i)), relative = point.clone().sub(parent.position);
      assert(Math.hypot(relative.x, relative.z) < M.horizontal_clearance); assert(relative.y < M.upper_clearance); assert(point.y >= -.000001);
    } } });
  }
  const frame = fs[200]; parent.position.fromArray(frame.position); parent.rotation.y = frame.heading;
  const pose = flightWingsV8(4, frame.state, frame.position[1] - M.ground_y, 'normal'); rig.apply(pose); const first = rig.diagnostics();
  rig.apply(flightWingsV8(4.02, frame.state, frame.position[1] - M.ground_y, 'normal')); assert.notDeepEqual(first, rig.diagnostics()); rig.apply(pose); assert.deepEqual(first, rig.diagnostics());
  for (const fps of [3, 30, 60]) {
    for (let n = 0; n <= fps; n++) rig.apply(flightWingsV8(4 + n / fps, 'flying', frame.position[1] - M.ground_y, 'normal'));
    rig.apply(pose); assert.deepEqual(first, rig.diagnostics());
  }
  assert.throws(() => rig.apply({ ...pose, stroke: 2 })); rig.dispose();
});
