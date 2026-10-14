import { ARENA } from "./experimentalArena";
import { FLY_VIEWER_ASSET } from "./flyViewer";
import type { ArenaCoursePose } from "./arenaCourseReplay";

export const LOCOMOTION_URL = "/experiments/experimental_locomotion_v0.json";
export const LOCOMOTION_SHA256 = "fc6d9882af59e63b4000d2426cc954342ce810ac2094f1e90f92d2d26cf2f893";
export type LocomotionFrame = { step: number; time: number; position: [number, number, number]; orientation: number; linear_velocity: [number, number, number]; angular_velocity: number; contact: null | "X_WALL" | "Z_WALL"; propulsion_model_value: number; steering_model_value: number | null; sensory_summary: { right: number; left: number; raw_normalized: number[]; clipped: boolean[]; bearing_shift_rad: number[]; heading_increment_eq: number; before_step: number; available_step: number; interval_ms: number; pose_origin: string } | null; neural_summary: { hs_states: number[]; dnp15_states: number[]; mean_yaw_drive_eq: number | null; orientation_increment_eq: number | null; substeps: number } | null; model_mode: "EXPERIMENTAL_KINEMATIC_ONLY" | "CONNECTOME_INFORMED_NEURAL_STEERING"; steering_applied?: boolean; steering_clipped?: boolean; distance: number };
export type LocomotionRun = { id: string; condition?: { id: string; neural: boolean; apply: boolean; plane_z: number }; neural_substeps?: number; speed: number; frames: LocomotionFrame[]; contact_events: { step: number; time: number; wall: string }[]; distance: number; termination_reason: "DURATION_COMPLETED" };
export type LocomotionReplay = { schema: string; config: { experiment_id: string; schema_version: string; model_mode: string; propulsion_source: string; boundary_response: string; presentation: string; neural_steering: string; malecns_references: unknown[]; random_policy: string; units: string; axes: string; update: string; dt_s: number; duration_s: number; speed: number; initial_position: [number, number, number]; initial_heading_rad: number; chamber: { width: number; depth: number; height: number; wall: number }; footprint_radius: number; fly_scale: number; fly_asset_sha256: string; asset_offset: [number, number, number]; bounds: { min: number[]; max: number[] }; floor_offset_y: number; limitations: string[] }; result: { runs: LocomotionRun[] }; artifact_id: string; config_sha256: string; result_sha256: string };
const close = (a: number, b: number) => Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) < 1e-10;
const fail = () => { throw new Error("Dados de locomoção incompatíveis ou corrompidos. Nenhum movimento foi criado."); };

/** Shared scene/plant guard; preserves the original v0 validation behavior. */
export function locomotionBounds(c: LocomotionReplay["config"]) {
  if (c.dt_s !== .02 || c.duration_s !== 8 || c.speed !== .18 || c.initial_heading_rad !== Math.PI / 2 || c.fly_scale !== ARENA.flyScale || c.fly_asset_sha256 !== FLY_VIEWER_ASSET.runtime.sha256) fail();
  for (const k of ["width", "depth", "height", "wall"] as const) if (c.chamber[k] !== ARENA.chamber[k]) fail();
  const a = FLY_VIEWER_ASSET.canonical_transform.visual_anchor!.position;
  const initial = a.map((v, i) => v * ARENA.flyScale + ARENA.flyOffset[i]);
  let radius = 0;
  for (const x of [FLY_VIEWER_ASSET.bounds.min[0], FLY_VIEWER_ASSET.bounds.max[0]]) for (const z of [FLY_VIEWER_ASSET.bounds.min[2], FLY_VIEWER_ASSET.bounds.max[2]]) radius = Math.max(radius, Math.hypot(x - a[0], z - a[2]) * ARENA.flyScale);
  if (!close(c.footprint_radius, radius) || !c.initial_position.every((v, i) => close(v, initial[i])) || !c.asset_offset.every((v, i) => close(v, -a[i]))) fail();
  if (ARENA.flyOffset[1] + FLY_VIEWER_ASSET.bounds.min[1] * ARENA.flyScale <= 0 || ARENA.flyOffset[1] + FLY_VIEWER_ASSET.bounds.max[1] * ARENA.flyScale >= c.chamber.height - c.chamber.wall / 2) fail();
  const lx = (c.chamber.width - c.chamber.wall) / 2 - radius, lz = (c.chamber.depth - c.chamber.wall) / 2 - radius;
  return [lx, lz] as const;
}

/** Semantic guard in addition to the pinned byte checksum. Browser never simulates motion. */
export function parseLocomotion(value: unknown): LocomotionReplay {
  try {
    const r = value as LocomotionReplay, c = r.config;
    if (r.schema !== "experimental_locomotion_replay_v1" || c.schema_version !== r.schema || c.experiment_id !== "EXPERIMENTAL_LOCOMOTION_V0" || c.model_mode !== "EXPERIMENTAL_KINEMATIC_ONLY" || c.propulsion_source !== "ENGINEERING_ASSUMPTION" || c.boundary_response !== "ENGINEERING_CONTACT_MODEL" || c.presentation !== "PRECOMPUTED_SIMULATION_REPLAY" || c.neural_steering !== "NOT_MODELLED" || c.random_policy !== "NONE" || c.malecns_references.length !== 0 || c.units !== "arena_display_units_and_seconds_not_physical_calibration" || c.axes !== "Y_UP_HEADING_ZERO_POSITIVE_Z_POSITIVE_YAW_TOWARD_POSITIVE_X" || c.update !== "LEFT_BOUNDARY_CONSTANT_VELOCITY_THEN_CONTACT_STOP") fail();
    if (c.dt_s !== .02 || c.duration_s !== 8 || c.speed !== .18 || c.initial_heading_rad !== Math.PI / 2 || c.fly_scale !== ARENA.flyScale || c.fly_asset_sha256 !== FLY_VIEWER_ASSET.runtime.sha256) fail();
    for (const k of ["width", "depth", "height", "wall"] as const) if (c.chamber[k] !== ARENA.chamber[k]) fail();
    const [lx, lz] = locomotionBounds(c);
    const initial = c.initial_position;
    if (r.result.runs.length !== 2 || ![r.artifact_id, r.config_sha256, r.result_sha256].every(h => /^[a-f0-9]{64}$/.test(h))) fail();
    r.result.runs.forEach((run, index) => {
      if (run.id !== ["ENGINEERING_PROPULSION", "PROPULSION_OFF"][index] || run.speed !== (index === 0 ? c.speed : 0) || run.frames.length !== 401 || run.termination_reason !== "DURATION_COMPLETED") fail();
      let distance = 0;
      const events: LocomotionRun["contact_events"] = [];
      run.frames.forEach((f, n) => {
        if (f.step !== n || !close(f.time, n * c.dt_s) || f.model_mode !== c.model_mode || f.orientation !== c.initial_heading_rad || f.angular_velocity !== 0 || f.propulsion_model_value !== run.speed || f.steering_model_value !== null || f.neural_summary !== null || f.sensory_summary !== null || f.position.length !== 3 || !f.position.every(Number.isFinite)) fail();
        const prev = run.frames[n - 1];
        const expected = prev ? [Math.max(-lx, Math.min(lx, prev.position[0] + prev.linear_velocity[0] * c.dt_s)), initial[1], Math.max(-lz, Math.min(lz, prev.position[2] + prev.linear_velocity[2] * c.dt_s))] : initial;
        if (!f.position.every((v, i) => close(v, expected[i])) || Math.abs(f.position[0]) > lx + 1e-12 || Math.abs(f.position[2]) > lz + 1e-12) fail();
        if (prev) distance += Math.hypot(f.position[0] - prev.position[0], f.position[2] - prev.position[2]);
        const contact = prev?.contact ?? (run.speed > 0 && f.position[0] >= lx ? "X_WALL" : null);
        if (f.contact !== contact || !close(f.distance, distance)) fail();
        const velocity = contact ? [0, 0, 0] : [run.speed * Math.sin(f.orientation), 0, run.speed * Math.cos(f.orientation)];
        if (f.linear_velocity.length !== 3 || !f.linear_velocity.every((v, i) => close(v, velocity[i]))) fail();
        if (contact && !prev?.contact) events.push({ step: n, time: f.time, wall: contact });
      });
      if (!close(run.distance, distance) || JSON.stringify(events) !== JSON.stringify(run.contact_events.map(e => ({ step: e.step, time: e.time, wall: e.wall })))) fail();
    });
    return r;
  } catch { return fail(); }
}

export async function loadLocomotion(fetcher: typeof fetch = fetch) {
  const response = await fetcher(LOCOMOTION_URL);
  if (!response.ok) throw new Error(`Locomoção indisponível (HTTP ${response.status}).`);
  const bytes = await response.arrayBuffer();
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), n => n.toString(16).padStart(2, "0")).join("");
  if (hash !== LOCOMOTION_SHA256) fail();
  return parseLocomotion(JSON.parse(new TextDecoder().decode(bytes)));
}

/** Real scientific seconds; pausing/cameras cannot advance the replay. */
export function advanceLocomotion(time: number, elapsedMs: number, playing: boolean, duration = 8) {
  if (![time, elapsedMs, duration].every(Number.isFinite) || time < 0 || elapsedMs < 0 || duration <= 0 || time > duration) fail();
  return playing ? Math.min(duration, time + elapsedMs / 1000) : time;
}
export function locomotionScene(replay: LocomotionReplay, runIndex: number, time: number) {
  const run = replay.result.runs[runIndex], c = replay.config;
  if (!run || !Number.isFinite(time) || time < 0 || time > c.duration_s) fail();
  const cursor = time / c.dt_s, index = Math.min(run.frames.length - 1, Math.floor(cursor)), alpha = cursor - index;
  const f = run.frames[index], next = run.frames[Math.min(index + 1, run.frames.length - 1)];
  const position = f.position.map((v, i) => v + (next.position[i] - v) * alpha) as [number, number, number];
  const pose: ArenaCoursePose = { anchor: position, assetOffset: c.asset_offset, rotation: f.orientation + (next.orientation - f.orientation) * alpha };
  return { pose, frame: f, distance: f.distance + (next.distance - f.distance) * alpha, speed: Math.hypot(...f.linear_velocity), time };
}
