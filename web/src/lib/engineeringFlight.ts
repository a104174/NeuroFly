/** Independent engineering plant. No neural imports, scientific session storage or aerodynamic forces. */
import { ARENA } from './experimentalArena';
import { FLY_VIEWER_ASSET } from './flyViewer';
import type { ArenaCoursePose } from './arenaCourseReplay';
import type { FlightState } from './articulatedWings';
import { FLIGHT_WINGS_V8, type WingbeatPreset } from './flightWingsV8';

export type Vec3 = [number, number, number];
const anchor = FLY_VIEWER_ASSET.canonical_transform.visual_anchor!.position;
export const FLIGHT_MODEL = {
  schema: 'engineering_3d_kinematic_flight_v8', axes: 'Y_UP_Z_FORWARD', dt_s: .02,
  units: 'presentation units, seconds, radians', randomness: 'NONE',
  source_glb_sha256: FLY_VIEWER_ASSET.runtime.sha256,
  arena: ARENA.chamber, fly_scale: ARENA.flyScale,
  // Conservative envelopes validated on original surfaces across wing strokes and yaw.
  horizontal_clearance: .28, upper_clearance: .24,
  max_forward_speed: .18, max_vertical_speed: .16,
  state_decimal_places: 12,
  horizontal_acceleration: .45, vertical_acceleration: .32, max_turn_rate: .8,
  takeoff_speed: .128, airborne_altitude: .04, landing_speed: .12,
  ground_y: anchor[1] * ARENA.flyScale + ARENA.flyOffset[1],
} as const;
export type Intent = 'HOLD' | 'TAKEOFF' | 'LAND';
/** Event at boundary step controls the interval [step*.02, (step+1)*.02). Scalars hold until next event; intent is one-shot. */
export type FlightCommand = { id: string; step: number; forward: number; turn: number; vertical: number; intent: Intent };
export type FlightEvent = { kind: 'COMMAND' | 'REJECTED_COMMAND' | 'TRANSITION' | 'CONTACT'; step: number; time: number; detail: string };
export type FlightFrame = {
  step: number; time: number; position: Vec3; velocity: Vec3; heading: number;
  state: FlightState; stateSince: number; commandId: string | null;
  contacts: string[]; events: FlightEvent[];
};
export type FlightTrial = {
  schema: 'engineering_flight_trial_v8'; classification: 'ENGINEERING_KINEMATIC_FLIGHT';
  model: typeof FLIGHT_MODEL; initial: FlightFrame; stop_step: number; commands: FlightCommand[];
  presentation: { identity: typeof FLIGHT_WINGS_V8.schema; rig_sha256: string; preset: WingbeatPreset };
};
export const FLIGHT_DEMO: readonly FlightCommand[] = [
  { id: 'takeoff', step: 50, forward: 0, turn: 0, vertical: .8, intent: 'TAKEOFF' },
  { id: 'forward', step: 150, forward: .7, turn: 0, vertical: 0, intent: 'HOLD' },
  { id: 'climbing-turn', step: 250, forward: .8, turn: .65, vertical: .35, intent: 'HOLD' },
  { id: 'descending-turn', step: 350, forward: .6, turn: -.35, vertical: -.3, intent: 'HOLD' },
  { id: 'land', step: 450, forward: 0, turn: 0, vertical: 0, intent: 'LAND' },
];
export function initialFlightFrame(): FlightFrame {
  return { step: 0, time: 0, position: anchor.map((v, i) => v * ARENA.flyScale + ARENA.flyOffset[i]) as Vec3,
    velocity: [0, 0, 0], heading: Math.PI / 2, state: 'grounded', stateSince: 0, commandId: null, contacts: [], events: [] };
}
/** Sorted JSON plus finite-value rejection: used only for this engineering artifact. */
export function flightCanonical(value: unknown): string {
  if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('Non-finite flight value');
  if (Array.isArray(value)) return '[' + value.map(flightCanonical).join(',') + ']';
  if (value !== null && typeof value === 'object') return '{' + Object.entries(value).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([k, v]) => JSON.stringify(k) + ':' + flightCanonical(v)).join(',') + '}';
  if (value === undefined || typeof value === 'function') throw new Error('Unsupported flight value');
  return JSON.stringify(value);
}
export function createFlightTrial(commands: readonly FlightCommand[] = FLIGHT_DEMO, stopStep = 600, preset: WingbeatPreset = 'normal'): FlightTrial {
  const trial: FlightTrial = { schema: 'engineering_flight_trial_v8', classification: 'ENGINEERING_KINEMATIC_FLIGHT',
    model: structuredClone(FLIGHT_MODEL), initial: initialFlightFrame(), stop_step: stopStep, commands: structuredClone([...commands]),
    presentation: { identity: FLIGHT_WINGS_V8.schema, rig_sha256: FLIGHT_WINGS_V8.rig_sha256, preset } };
  validateFlightTrial(trial); return trial;
}
export function validateFlightTrial(value: unknown): FlightTrial {
  const t = value as FlightTrial;
  if (!t || Object.keys(t).sort().join(',') !== 'classification,commands,initial,model,presentation,schema,stop_step' ||
      t.schema !== 'engineering_flight_trial_v8' || t.classification !== 'ENGINEERING_KINEMATIC_FLIGHT' ||
      flightCanonical(t.model) !== flightCanonical(FLIGHT_MODEL) || flightCanonical(t.initial) !== flightCanonical(initialFlightFrame()) ||
      !Number.isInteger(t.stop_step) || t.stop_step < 1 || t.stop_step > 1500 || !Array.isArray(t.commands) || t.commands.length > 100 ||
      !t.presentation || flightCanonical(t.presentation) !== flightCanonical({ identity: FLIGHT_WINGS_V8.schema, rig_sha256: FLIGHT_WINGS_V8.rig_sha256, preset: t.presentation.preset }) ||
      !Object.hasOwn(FLIGHT_WINGS_V8.presets, t.presentation.preset)) throw new Error('Invalid engineering flight trial identity/configuration');
  const ids = new Set<string>(); let previous = -1;
  for (const c of t.commands) {
    if (!c || Object.keys(c).sort().join(',') !== 'forward,id,intent,step,turn,vertical' || typeof c.id !== 'string' || !/^[a-zA-Z0-9_-]{1,64}$/.test(c.id) || ids.has(c.id) ||
        !Number.isInteger(c.step) || c.step <= previous || c.step < 0 || c.step >= t.stop_step ||
        ![c.forward, c.turn, c.vertical].every(v => Number.isFinite(v) && Math.abs(v) <= 1) ||
        !['HOLD', 'TAKEOFF', 'LAND'].includes(c.intent)) throw new Error('Invalid/duplicate/off-grid flight command');
    ids.add(c.id); previous = c.step;
  }
  return structuredClone(t);
}
export type FlightChamber = { width: number; depth: number; height: number; wall: number; floor: number };
export function flightBounds(chamber: FlightChamber = FLIGHT_MODEL.arena) {
  if (!chamber || Object.keys(chamber).sort().join(',') !== 'depth,floor,height,wall,width' ||
      !Object.values(chamber).every(value => Number.isFinite(value) && value > 0) ||
      chamber.floor >= chamber.height || chamber.wall >= Math.min(chamber.width, chamber.depth, chamber.height))
    throw new Error('Invalid flight chamber dimensions');
  const c = { ...FLIGHT_MODEL, arena: chamber };
  const bounds = { min: [-(c.arena.width - c.arena.wall) / 2 + c.horizontal_clearance, c.ground_y, -(c.arena.depth - c.arena.wall) / 2 + c.horizontal_clearance] as Vec3,
    max: [(c.arena.width - c.arena.wall) / 2 - c.horizontal_clearance, c.arena.height - c.arena.wall / 2 - c.upper_clearance, (c.arena.depth - c.arena.wall) / 2 - c.horizontal_clearance] as Vec3 };
  if (bounds.min.some((value, axis) => value >= bounds.max[axis])) throw new Error('Chamber cannot accommodate conservative flight clearance');
  return bounds;
}
const approach = (current: number, target: number, amount: number) => current + Math.max(-amount, Math.min(amount, target - current));
// Portable engineering state grid: sub-ULP differences in runtime hypot/trig must
// not create different export identities. Never used by historical neural/body models.
const quantize = (value: number) => Math.round(value * 10 ** FLIGHT_MODEL.state_decimal_places) / 10 ** FLIGHT_MODEL.state_decimal_places;
const legal: Record<FlightState, FlightState[]> = { grounded: ['takeoff'], takeoff: ['flying', 'landing'], flying: ['landing'], landing: ['grounded'] };
export class FlightEngine {
  private readonly input: FlightTrial;
  private readonly history: FlightFrame[];
  private command: FlightCommand = { id: '', step: 0, forward: 0, turn: 0, vertical: 0, intent: 'HOLD' };
  private adaptedTurn = false;
  private externalCommandMode = false;
  private readonly externalCommandIds = new Set<string>();
  private readonly chamber: FlightChamber;
  constructor(trial = createFlightTrial(), chamber: FlightChamber = FLIGHT_MODEL.arena) {
    this.input = validateFlightTrial(trial);
    const bounds = flightBounds(chamber);
    if (this.input.initial.position.some((v, axis) => v < bounds.min[axis] || v > bounds.max[axis]))
      throw new Error('Initial flight pose is inadmissible in chamber');
    this.chamber = structuredClone(chamber);
    this.history = [structuredClone(this.input.initial)];
  }
  environment() { return structuredClone(this.chamber); }
  trial() { return structuredClone(this.input); }
  snapshot() { return structuredClone(this.history.at(-1)!); }
  frames() { return structuredClone(this.history); }
  events() { return structuredClone(this.history.flatMap(f => f.events)); }
  get stopStep() { return this.input.stop_step; }
  frame(step: number) { if (!Number.isInteger(step) || step < 0 || step >= this.history.length) throw new Error('Seek outside recorded flight boundaries'); return structuredClone(this.history[step]); }
  get hasExternalTurn() { return this.adaptedTurn; }
  get hasExternalCommand() { return this.externalCommandMode; }
  advance() {
    if (this.externalCommandMode) throw new Error('State-feedback flight requires a complete command for each interval');
    return this.advanceInterval();
  }
  /** Versioned downstream experiments may supply only a normalized turn input.
   * Such runs require their own artifact; they cannot be exported as legacy v8. */
  advanceWithTurn(turn: number) {
    if (this.externalCommandMode) throw new Error('Cannot mix full external commands with external turn inputs');
    if (!Number.isFinite(turn) || Math.abs(turn) > 1) throw new Error('Invalid external flight turn');
    return this.advanceInterval(turn);
  }
  /** Apply a complete normalized motor command to the interval beginning at the
   * current accepted boundary. This additive mode requires an empty legacy
   * schedule and must be selected before the first interval. */
  advanceWithCommand(value: FlightCommand) {
    const old = this.history.at(-1)!;
    const command = value as FlightCommand;
    if ((!this.externalCommandMode && this.history.length !== 1) || this.input.commands.length !== 0 || this.adaptedTurn)
      throw new Error('Full external commands require a fresh flight trial with no scheduled commands');
    if (!command || Object.keys(command).sort().join(',') !== 'forward,id,intent,step,turn,vertical' ||
        typeof command.id !== 'string' || !/^[a-zA-Z0-9_-]{1,64}$/.test(command.id) || this.externalCommandIds.has(command.id) ||
        command.step !== old.step || ![command.forward, command.turn, command.vertical].every(v => Number.isFinite(v) && Math.abs(v) <= 1) ||
        !['HOLD', 'TAKEOFF', 'LAND'].includes(command.intent)) throw new Error('Invalid or misaligned external flight command');
    const accepted = this.advanceInterval(undefined, command);
    this.externalCommandIds.add(command.id);
    this.externalCommandMode = true;
    return accepted;
  }
  private advanceInterval(turn?: number, externalCommand?: FlightCommand) {
    const old = this.history.at(-1)!;
    if (old.step >= this.input.stop_step) throw new Error('Flight trial completed');
    const c = FLIGHT_MODEL, dt = c.dt_s, next = structuredClone(old);
    next.step++; next.time = next.step * dt; next.events = []; next.contacts = [];
    const event = (kind: FlightEvent['kind'], detail: string, boundary = old.step) => next.events.push({ kind, step: boundary, time: boundary * dt, detail });
    const transition = (to: FlightState, boundary = old.step) => {
      if (!legal[next.state].includes(to)) throw new Error(`Illegal flight transition ${next.state} -> ${to}`);
      event('TRANSITION', `${next.state}->${to}`, boundary); next.state = to; next.stateSince = boundary * dt;
    };
    const due = this.input.commands.find(e => e.step === old.step);
    if (due) {
      this.command = due; next.commandId = due.id; event('COMMAND', due.id);
      if (due.intent === 'TAKEOFF') { if (next.state === 'grounded') transition('takeoff'); else event('REJECTED_COMMAND', 'TAKEOFF requires grounded'); }
      if (due.intent === 'LAND') { if (next.state === 'flying' || next.state === 'takeoff') transition('landing'); else event('REJECTED_COMMAND', 'LAND requires takeoff/flying'); }
    }
    if (externalCommand) {
      next.commandId = externalCommand.id; event('COMMAND', externalCommand.id);
      if (externalCommand.intent === 'TAKEOFF') { if (next.state === 'grounded') transition('takeoff'); else event('REJECTED_COMMAND', 'TAKEOFF requires grounded'); }
      if (externalCommand.intent === 'LAND') { if (next.state === 'flying' || next.state === 'takeoff') transition('landing'); else event('REJECTED_COMMAND', 'LAND requires takeoff/flying'); }
    }
    const cmd = externalCommand ?? (turn === undefined ? this.command : { ...this.command, turn });
    if (next.state === 'grounded') {
      if (due && (cmd.forward || cmd.turn || cmd.vertical)) event('REJECTED_COMMAND', 'Grounded motion requires TAKEOFF');
      next.velocity = [0, 0, 0];
    } else {
      const landing = next.state === 'landing';
      if (!landing && cmd.turn) next.heading = quantize(old.heading + cmd.turn * c.max_turn_rate * dt);
      const speed = landing ? 0 : cmd.forward * c.max_forward_speed;
      // Bounded vector acceleration avoids sqrt(2) diagonal acceleration inflation.
      const targetX = Math.sin(next.heading) * speed, targetZ = Math.cos(next.heading) * speed;
      const dx = targetX - old.velocity[0], dz = targetZ - old.velocity[2], norm = Math.hypot(dx, dz);
      const factor = norm ? Math.min(1, c.horizontal_acceleration * dt / norm) : 0;
      next.velocity[0] = quantize(old.velocity[0] + dx * factor); next.velocity[2] = quantize(old.velocity[2] + dz * factor);
      const vy = landing ? -c.landing_speed : next.state === 'takeoff' ? Math.max(c.takeoff_speed, cmd.vertical * c.max_vertical_speed) : cmd.vertical * c.max_vertical_speed;
      next.velocity[1] = quantize(approach(old.velocity[1], vy, c.vertical_acceleration * dt));
      next.position = old.position.map((v, i) => next.velocity[i] === 0 ? v : quantize(v + next.velocity[i] * dt)) as Vec3;
      const bounds = flightBounds(this.chamber);
      for (let axis = 0; axis < 3; axis++) {
        if (next.position[axis] < bounds.min[axis] || next.position[axis] > bounds.max[axis]) {
          const lower = next.position[axis] < bounds.min[axis], contact = ['X_WALL', lower ? 'FLOOR' : 'CEILING', 'Z_WALL'][axis];
          next.position[axis] = lower ? bounds.min[axis] : bounds.max[axis]; next.velocity[axis] = 0;
          next.contacts.push(contact); if (!old.contacts.includes(contact)) event('CONTACT', contact, next.step);
          if (axis === 1 && lower) {
            if (next.state !== 'landing') transition('landing', next.step);
            transition('grounded', next.step); next.velocity = [0, 0, 0];
          }
        }
      }
      if (next.state === 'takeoff' && next.position[1] - c.ground_y >= c.airborne_altitude) transition('flying', next.step);
    }
    this.history.push(next); if (turn !== undefined) this.adaptedTurn = true; return this.snapshot();
  }
}
/** Bounded cooperative scheduler. Rendering delays affect pacing, never dt or command boundaries. */
export class FlightClock {
  private remainder = 0;
  reset() { this.remainder = 0; }
  advance(engine: { snapshot(): { step: number }; advance(): unknown; readonly stopStep: number }, elapsedMs: number) {
    if (!Number.isFinite(elapsedMs) || elapsedMs < 0) throw new Error('Invalid flight clock elapsed interval');
    this.remainder += elapsedMs; let steps = 0;
    while (this.remainder + 1e-9 >= 20 && steps < 50 && engine.snapshot().step < engine.stopStep) { engine.advance(); this.remainder -= 20; steps++; }
    const limited = this.remainder >= 20 && engine.snapshot().step < engine.stopStep;
    if (limited || engine.snapshot().step === engine.stopStep) this.remainder = 0;
    return { steps, limited };
  }
}
/** Recorded playback is a read. Only advancing beyond the frontier executes the plant. */
export function advanceFlightCursor(engine: FlightEngine, step: number) {
  if (!Number.isInteger(step) || step < 0 || step > engine.snapshot().step) throw new Error('Invalid flight playback cursor');
  return step < engine.snapshot().step ? engine.frame(step + 1) : engine.advance();
}
export function flightScene(frame: FlightFrame): ArenaCoursePose {
  return { anchor: [...frame.position], rotation: frame.heading, assetOffset: anchor.map(v => -v) as Vec3 };
}
export function reconstructFlight(trial: FlightTrial, stopStep = trial.stop_step) {
  if (!Number.isInteger(stopStep) || stopStep < 0 || stopStep > trial.stop_step) throw new Error('Invalid flight prefix');
  const engine = new FlightEngine(trial); for (let i = 0; i < stopStep; i++) engine.advance(); return engine;
}
export async function flightHash(value: unknown) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(flightCanonical(value)));
  return [...new Uint8Array(digest)].map(n => n.toString(16).padStart(2, '0')).join('');
}
export async function exportFlight(engine: FlightEngine, preset: WingbeatPreset) {
  if (flightCanonical(engine.environment()) !== flightCanonical(FLIGHT_MODEL.arena) || engine.hasExternalTurn || engine.hasExternalCommand) throw new Error('Externally controlled flight requires its own versioned artifact');
  const trial = engine.trial(); trial.presentation.preset = preset; validateFlightTrial(trial);
  const frames = engine.frames(), termination = frames.length - 1 === trial.stop_step ? 'DURATION_COMPLETED' : 'RECORDED_PREFIX';
  return { schema: 'engineering_flight_result_v8', classification: 'ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT', trial, frames, termination,
    input_sha256: await flightHash(trial), result_sha256: await flightHash({ frames, termination }) };
}
export async function importFlight(value: unknown) {
  const v = value as Awaited<ReturnType<typeof exportFlight>>;
  if (!v || Object.keys(v).sort().join(',') !== 'classification,frames,input_sha256,result_sha256,schema,termination,trial' ||
      v.schema !== 'engineering_flight_result_v8' || v.classification !== 'ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT' ||
      !Array.isArray(v.frames) || v.frames.length < 1 || v.frames.length > 1501) throw new Error('Not an engineering v8 flight artifact');
  const trial = validateFlightTrial(v.trial), engine = reconstructFlight(trial, v.frames.length - 1);
  const expected = await exportFlight(engine, trial.presentation.preset);
  if (flightCanonical(expected) !== flightCanonical(v)) throw new Error('Flight replay/identity mismatch; imported positions are not authoritative');
  return engine;
}
