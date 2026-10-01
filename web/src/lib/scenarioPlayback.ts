/** Transport validation and render-only playback. No scientific equations. */
export const SCENARIO_KINDS = ["BASELINE_CONTROL", "LOOMING_CIRCUIT_VALIDATION", "LOOMING_WORLD_EXPERIMENT"] as const;
export type ScenarioKind = typeof SCENARIO_KINDS[number];
export interface ScenarioDefinition {
  id: ScenarioKind; scenario_kind: ScenarioKind; title: string; description: string;
  availability: "CANONICAL_PRESET"; preset_only: true; scientific_caveat: string;
}
export interface ScenarioScientificStatus {
  closed_loop_execution_completed: boolean;
  environment_affected_sensory_input: boolean;
  body_state_feedback_wired: boolean;
  body_state_feedback_realized: boolean;
  genuine_nonzero_actuation_occurred: boolean;
  body_movement_occurred: boolean;
}
export interface ScenarioPlaybackFrame {
  step: number; time_ms: number;
  body: { x_world_eq: number; z_world_eq: number; fixed_heading: "POSITIVE_Z" };
  object: { x_world_eq: number; z_world_eq: number; radius_world_eq: number } | null;
  relative_distance_world_eq: number | null; lattice_radius: number | null;
  active_sensory_body_count: number;
  sensory_summaries: { neuron_type: "LC4" | "LPLC2"; side: "R" | "L"; state_sum: number }[];
  dnp01_membrane_mv: number[]; dnp01_spike_body_ids: number[]; ttmn_state: number[];
  actuator_commands: { RIGHT_TTM_ACTUATOR: number; LEFT_TTM_ACTUATOR: number };
}
export interface ScenarioPlaybackResult {
  schema: "scenario_playback_v1"; artifact_id: string; run_id: string;
  scenario: ScenarioDefinition; dt_ms: number; duration_ms: number;
  statuses: ScenarioScientificStatus; dnp01_body_ids: number[]; total_dnp01_spikes: number;
  frames: ScenarioPlaybackFrame[]; scientific_limitations: string[];
  source_operation: "VALIDATED_CANONICAL_REPLAY";
  termination?: { status: "COMPLETED_VALID_HORIZON" | "TERMINATED_GEOMETRY_DOMAIN"; step: number; time_ms: number; reason: string | null } | null;
  requested_duration_ms?: number | null;
  preregistration_id?: string | null;
}
function invalid(): never { throw new Error("Malformed authoritative scenario playback payload."); }
function record(v: unknown): Record<string, unknown> {
  if (!v || typeof v !== "object" || Array.isArray(v)) return invalid();
  return v as Record<string, unknown>;
}
function str(v: unknown): string { return typeof v === "string" ? v : invalid(); }
function num(v: unknown): number { return typeof v === "number" && Number.isFinite(v) ? v : invalid(); }
function integer(v: unknown): number { const n = num(v); return Number.isInteger(n) && n >= 0 ? n : invalid(); }
function bool(v: unknown): boolean { return typeof v === "boolean" ? v : invalid(); }
function array<T>(v: unknown, parse: (v: unknown) => T): T[] {
  return Array.isArray(v) ? v.map(parse) : invalid();
}
function literal<T extends string>(v: unknown, choices: readonly T[]): T {
  return choices.includes(v as T) ? v as T : invalid();
}
function nullable<T>(v: unknown, parse: (v: unknown) => T): T | null { return v === null ? null : parse(v); }
function command(v: unknown): number { const n = num(v); return n >= 0 && n <= 1 ? n : invalid(); }
function pair(v: unknown): number[] { const a = array(v, num); return a.length === 2 ? a : invalid(); }
export function parseScenarioDefinition(v: unknown): ScenarioDefinition {
  const r = record(v);
  const id = literal(r.id, SCENARIO_KINDS);
  if (r.scenario_kind !== id || r.preset_only !== true) return invalid();
  return { id, scenario_kind: id, title: str(r.title), description: str(r.description),
    availability: literal(r.availability, ["CANONICAL_PRESET"]), preset_only: true,
    scientific_caveat: str(r.scientific_caveat) };
}
export function parseScenarioCatalog(v: unknown): ScenarioDefinition[] {
  const a = array(v, parseScenarioDefinition);
  if (a.length !== SCENARIO_KINDS.length || a.some((s, i) => s.id !== SCENARIO_KINDS[i])) return invalid();
  return a;
}
export function parseScenarioPlayback(v: unknown): ScenarioPlaybackResult {
  const r = record(v), s = record(r.statuses);
  const scenario = parseScenarioDefinition(r.scenario);
  const statuses: ScenarioScientificStatus = {
    closed_loop_execution_completed: bool(s.closed_loop_execution_completed),
    environment_affected_sensory_input: bool(s.environment_affected_sensory_input),
    body_state_feedback_wired: bool(s.body_state_feedback_wired),
    body_state_feedback_realized: bool(s.body_state_feedback_realized),
    genuine_nonzero_actuation_occurred: bool(s.genuine_nonzero_actuation_occurred),
    body_movement_occurred: bool(s.body_movement_occurred),
  };
  const frames = array(r.frames, v => {
    const f = record(v), b = record(f.body), a = record(f.actuator_commands);
    const object = nullable(f.object, v => {
      const o = record(v), radius = num(o.radius_world_eq);
      if (radius <= 0) return invalid();
      return { x_world_eq: num(o.x_world_eq), z_world_eq: num(o.z_world_eq), radius_world_eq: radius };
    });
    const frame: ScenarioPlaybackFrame = {
      step: integer(f.step), time_ms: num(f.time_ms),
      body: { x_world_eq: num(b.x_world_eq), z_world_eq: num(b.z_world_eq), fixed_heading: literal(b.fixed_heading, ["POSITIVE_Z"]) },
      object, relative_distance_world_eq: nullable(f.relative_distance_world_eq, num),
      lattice_radius: nullable(f.lattice_radius, integer), active_sensory_body_count: integer(f.active_sensory_body_count),
      sensory_summaries: array(f.sensory_summaries, v => { const s = record(v); return {
        neuron_type: literal(s.neuron_type, ["LC4", "LPLC2"]), side: literal(s.side, ["R", "L"]), state_sum: num(s.state_sum),
      }; }),
      dnp01_membrane_mv: pair(f.dnp01_membrane_mv), dnp01_spike_body_ids: array(f.dnp01_spike_body_ids, integer),
      ttmn_state: pair(f.ttmn_state),
      actuator_commands: { RIGHT_TTM_ACTUATOR: command(a.RIGHT_TTM_ACTUATOR), LEFT_TTM_ACTUATOR: command(a.LEFT_TTM_ACTUATOR) },
    };
    if ((scenario.id === "BASELINE_CONTROL") !== (object === null) || frame.active_sensory_body_count > 311) return invalid();
    if (object === null ? frame.lattice_radius !== null || frame.relative_distance_world_eq !== null : frame.lattice_radius === null || frame.relative_distance_world_eq === null || frame.relative_distance_world_eq <= 0) return invalid();
    return frame;
  });
  const dt = num(r.dt_ms), duration = num(r.duration_ms);
  if (dt <= 0 || frames.length < 2 || duration <= 0 || frames.some((f, i) => f.step !== i || Math.abs(f.time_ms - i * dt) > 1e-9) || Math.abs(frames.at(-1)!.time_ms - duration) > 1e-9) return invalid();
  const hash = (v: unknown) => { const s = str(v); return /^[0-9a-f]{64}$/.test(s) ? s : invalid(); };
  const identities = array(r.dnp01_body_ids, integer);
  if (identities.length !== 2 || new Set(identities).size !== 2 || frames.some(f => f.dnp01_spike_body_ids.some(id => !identities.includes(id)))) return invalid();
  const termination = r.termination == null ? null : (() => {
    const t = record(r.termination);
    return { status: literal(t.status, ["COMPLETED_VALID_HORIZON", "TERMINATED_GEOMETRY_DOMAIN"]), step: integer(t.step), time_ms: num(t.time_ms), reason: nullable(t.reason, str) };
  })();
  const requested = r.requested_duration_ms == null ? null : num(r.requested_duration_ms);
  const preregistration = r.preregistration_id == null ? null : hash(r.preregistration_id);
  if (scenario.id === "LOOMING_WORLD_EXPERIMENT") {
    if (!termination || requested === null || !preregistration || requested < duration) return invalid();
    if (Math.abs(termination.time_ms - termination.step * dt) > 1e-9) return invalid();
    if (termination.status === "COMPLETED_VALID_HORIZON" ? !statuses.closed_loop_execution_completed || termination.step !== frames.at(-1)!.step || requested !== duration || termination.reason !== null : statuses.closed_loop_execution_completed || termination.step !== frames.at(-1)!.step + 1 || termination.reason === null) return invalid();
  }
  return { schema: literal(r.schema, ["scenario_playback_v1"]), artifact_id: hash(r.artifact_id), run_id: hash(r.run_id),
    scenario, statuses, dt_ms: dt, duration_ms: duration, frames,
    dnp01_body_ids: identities, total_dnp01_spikes: integer(r.total_dnp01_spikes),
    scientific_limitations: array(r.scientific_limitations, str), source_operation: literal(r.source_operation, ["VALIDATED_CANONICAL_REPLAY"]),
    termination, requested_duration_ms: requested, preregistration_id: preregistration,
  };
}

// Six display seconds for the entire scientific record. Never modifies time_ms.
export const PRESENTATION_DURATION_MS = 6000;
export function advanceScenarioCursor(cursor: number, elapsedMs: number, playing: boolean, last: number): number {
  return playing ? Math.min(last, cursor + Math.max(0, elapsedMs) * last / PRESENTATION_DURATION_MS) : cursor;
}
// Shared render-only world_eq -> scene mapping; not returned to the scientific API.
export const PRESENTATION_SCALE = 1.5;
export function scenarioScene(result: ScenarioPlaybackResult, cursor: number) {
  const bounded = Math.min(result.frames.length - 1, Math.max(0, cursor));
  const i = Math.floor(bounded), a = result.frames[i], b = result.frames[Math.min(i + 1, result.frames.length - 1)];
  const t = bounded - i, mix = (x: number, y: number) => (x + (y - x) * t) * PRESENTATION_SCALE;
  return {
    frame: a, // Telemetry always the exact authoritative boundary.
    bodyPosition: [mix(a.body.x_world_eq, b.body.x_world_eq), 0, mix(a.body.z_world_eq, b.body.z_world_eq)] as [number, number, number],
    objectPosition: a.object && b.object ? [mix(a.object.x_world_eq, b.object.x_world_eq), 1.6, mix(a.object.z_world_eq, b.object.z_world_eq)] as [number, number, number] : null,
    objectRadius: a.object ? a.object.radius_world_eq * PRESENTATION_SCALE : null,
  };
}
