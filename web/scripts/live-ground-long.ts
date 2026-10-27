/** Explicit long-duration gate: node --expose-gc --import tsx scripts/live-ground-long.ts */
import { readFileSync } from 'node:fs';
import { performance } from 'node:perf_hooks';
import { gaitHistory } from '../src/lib/articulatedGait';
import { LiveGroundSession } from '../src/lib/liveGroundSession';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';

const authority = parseNeuralLocomotion(JSON.parse(readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8')));
const session = new LiveGroundSession(authority, true, 'long-validation');
const initial = session.snapshot();
let gait = gaitHistory([{time: initial.time, position: initial.position, heading: initial.heading}])[0];
let minX = initial.position[0], maxX = minX, minZ = initial.position[2], maxZ = minZ, minHeading = initial.heading, maxHeading = minHeading;
let maxHeap = 0;
global.gc?.(); const initialHeap = process.memoryUsage().heapUsed, start = performance.now();
session.start();
for (let i = 0; i < 90000; i++) {
  const { accepted } = session.advance();
  gait = gaitHistory([gait.body, {time: accepted.time, position: accepted.position, heading: accepted.heading}], [gait])[1];
  minX = Math.min(minX, accepted.position[0]); maxX = Math.max(maxX, accepted.position[0]);
  minZ = Math.min(minZ, accepted.position[2]); maxZ = Math.max(maxZ, accepted.position[2]);
  minHeading = Math.min(minHeading, accepted.heading); maxHeading = Math.max(maxHeading, accepted.heading);
  if ((i + 1) % 5000 === 0) { global.gc?.(); maxHeap = Math.max(maxHeap, process.memoryUsage().heapUsed); }
}
const elapsedMs = performance.now() - start, end = session.snapshot();
if (end.step !== 90000 || end.substeps !== 18000000 || session.trajectory.size !== 512 || session.telemetry.size !== 256 || session.events.size > 128) throw new Error('Long-duration gate failed');
console.log(JSON.stringify({ steps: end.step, simulated_seconds: end.time, neural_substeps: end.substeps, elapsed_ms: elapsedMs, mean_step_ms: elapsedMs / end.step, simulated_seconds_per_wall_second: end.time / (elapsedMs / 1000), heap_start_bytes: initialHeap, sampled_heap_max_bytes: maxHeap, trajectory_size: session.trajectory.size, telemetry_size: session.telemetry.size, event_size: session.events.size, contacts: end.contacts, recoveries: end.recoveries, max_stall_seconds: end.maxStallSeconds, range: {x: [minX, maxX], z: [minZ, maxZ], heading: [minHeading, maxHeading]}, gait_cycle: gait.cycle }, null, 2));
