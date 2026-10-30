/**
 * Engineering-only state-feedback verification for the existing flight plant.
 * This module contains no neural controller, aerodynamic model, or renderer pose
 * integration. Every motor decision observes one accepted FlightEngine frame.
 */
import {
  FlightEngine, FLIGHT_MODEL, createFlightTrial, flightBounds, flightCanonical,
  flightHash, initialFlightFrame, type FlightCommand, type FlightFrame, type Vec3,
} from './engineeringFlight';
import { ARENA } from './experimentalArena';

export const VERTICAL_FLIGHT_CONTROLLER = Object.freeze({
  id: 'state_feedback_vertical_v1',
  version: 1,
  policy: 'bounded_vertical_velocity_pd',
  takeoff_vertical_command: 0.8,
  altitude_kp_s_inv: 1.5,
  vertical_velocity_kd: 1.2,
  target_altitude_above_ground: 0.2,
  target_altitude_tolerance: 0.01,
  settled_vertical_speed: 0.02,
});

export const VERTICAL_FLIGHT_CONFIG = Object.freeze({
  schema: 'neurofly_vertical_flight_verification_v1',
  classification: 'ENGINEERING_STATE_FEEDBACK_NOT_BIOLOGICALLY_VALIDATED',
  controller: VERTICAL_FLIGHT_CONTROLLER,
  initial_state: initialFlightFrame(),
  environment: {
    id: 'neurofly_experimental_arena_v1',
    chamber: structuredClone(ARENA.chamber),
    bounds: flightBounds(),
  },
  plant_schema: FLIGHT_MODEL.schema,
  plant_limits: {
    max_horizontal_speed: FLIGHT_MODEL.max_forward_speed,
    max_vertical_speed: FLIGHT_MODEL.max_vertical_speed,
    horizontal_acceleration: FLIGHT_MODEL.horizontal_acceleration,
    vertical_acceleration: FLIGHT_MODEL.vertical_acceleration,
    max_turn_rate: FLIGHT_MODEL.max_turn_rate,
    horizontal_clearance: FLIGHT_MODEL.horizontal_clearance,
    upper_clearance: FLIGHT_MODEL.upper_clearance,
  },
  policy: {
    takeoff_trigger: 'EXPLICIT_UI_START_AT_INITIAL_GROUNDED_BOUNDARY',
    altitude_condition: 'ACCEPTED_ALTITUDE_WITHIN_CONFIGURED_TOLERANCE_AND_SETTLED_VERTICAL_SPEED',
    landing_trigger: 'ALTITUDE_CONDITION_THEN_EXPLICIT_LAND_COMMAND',
    success: 'TAKEOFF_ALTITUDE_CONDITION_LANDING_AND_ACCEPTED_GROUNDED_FLOOR_CONTACT',
    failure: ['TIMEOUT', 'INVALID_COMMAND', 'NON_FINITE_STATE', 'UNEXPECTED_CONTACT', 'INVALID_TRANSITION', 'FAILED_LANDING'],
  },
  wing_presentation: { schema: 'engineering_flight_wings_v8', preset: 'normal', frequency_hz: 12, source: 'PRESENTATION_ONLY_NO_LIFT' },
  interval_s: FLIGHT_MODEL.dt_s,
  maximum_duration_s: 15,
  maximum_steps: Math.round(15 / FLIGHT_MODEL.dt_s),
  seed: null,
  randomness: 'NONE',
} as const);

export type VerticalFlightConfig = typeof VERTICAL_FLIGHT_CONFIG;
export type VerticalControllerPhase = 'awaiting_takeoff' | 'takeoff' | 'climb' | 'descent' | 'complete';
export type VerticalFlightStatus = 'ready' | 'running' | 'paused' | 'completed' | 'failed';
export type VerticalFlightTermination = 'LANDED' | 'TIMEOUT' | 'FAILED';

export type VerticalFlightObservation = {
  accepted: FlightFrame;
  bounds: ReturnType<typeof flightBounds>;
};

export type VerticalFlightDecision = {
  phase_before: VerticalControllerPhase;
  phase_after: VerticalControllerPhase;
  transition_reason: string;
  command: FlightCommand | null;
};

export type VerticalFlightInterval = {
  command_origin: 'STATE_FEEDBACK_CONTROLLER_V1';
  observation_time_s: number;
  observation_step: number;
  observation: VerticalFlightObservation;
  decision: VerticalFlightDecision;
  accepted: FlightFrame;
};

const states = ['grounded', 'takeoff', 'flying', 'landing'] as const;
const legalTransitions: Record<(typeof states)[number], readonly (typeof states)[number][]> = {
  grounded: ['takeoff'], takeoff: ['flying', 'landing'], flying: ['landing'], landing: ['grounded'],
};
const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

function assertConfig(config: VerticalFlightConfig) {
  if (!config || typeof config !== 'object') throw new Error('Unsupported vertical-flight configuration identity');
  const boundedDuration = {
    ...config,
    maximum_duration_s: VERTICAL_FLIGHT_CONFIG.maximum_duration_s,
    maximum_steps: VERTICAL_FLIGHT_CONFIG.maximum_steps,
  };
  if (flightCanonical(boundedDuration) !== flightCanonical(VERTICAL_FLIGHT_CONFIG))
    throw new Error('Unsupported vertical-flight configuration identity');
  const targetY = FLIGHT_MODEL.ground_y + config.controller.target_altitude_above_ground;
  const tolerance = config.controller.target_altitude_tolerance;
  if (!(targetY - tolerance > config.environment.bounds.min[1] && targetY + tolerance < config.environment.bounds.max[1]) ||
      !Number.isSafeInteger(config.maximum_steps) || config.maximum_steps < 1 ||
      config.maximum_steps > VERTICAL_FLIGHT_CONFIG.maximum_steps ||
      config.maximum_duration_s !== config.maximum_steps * config.interval_s ||
      config.maximum_steps > 1500 || config.plant_schema !== FLIGHT_MODEL.schema || config.interval_s !== FLIGHT_MODEL.dt_s)
    throw new Error('Vertical-flight target or duration is inadmissible for the existing flight bounds');
}

function assertObservation(observation: VerticalFlightObservation, config: VerticalFlightConfig) {
  const frame = observation?.accepted;
  if (!frame || !Number.isSafeInteger(frame.step) || frame.step < 0 || frame.time !== frame.step * FLIGHT_MODEL.dt_s ||
      ![...frame.position, ...frame.velocity, frame.heading, frame.stateSince].every(Number.isFinite) ||
      !states.includes(frame.state) || !Array.isArray(frame.contacts) ||
      flightCanonical(observation.bounds) !== flightCanonical(config.environment.bounds))
    throw new Error('Invalid accepted flight observation or bounds identity');
  for (let axis = 0; axis < 3; axis++) {
    if (frame.position[axis] < observation.bounds.min[axis] - 1e-12 || frame.position[axis] > observation.bounds.max[axis] + 1e-12)
      throw new Error(`Accepted flight position is outside axis ${axis} bounds`);
  }
}

function decision(
  phaseBefore: VerticalControllerPhase,
  phaseAfter: VerticalControllerPhase,
  reason: string,
  frame: FlightFrame,
  intent: FlightCommand['intent'],
  vertical: number,
): VerticalFlightDecision {
  if (phaseAfter === 'complete') return { phase_before: phaseBefore, phase_after: phaseAfter, transition_reason: reason, command: null };
  return {
    phase_before: phaseBefore,
    phase_after: phaseAfter,
    transition_reason: reason,
    command: {
      id: `state-feedback-${frame.step}`,
      step: frame.step,
      forward: 0,
      turn: 0,
      vertical: clamp(vertical, -1, 1),
      intent,
    },
  };
}

/** Pure deterministic controller: input is an accepted boundary, output applies to its next interval. */
export function decideVerticalFlight(
  phase: VerticalControllerPhase,
  observation: VerticalFlightObservation,
  config: VerticalFlightConfig = VERTICAL_FLIGHT_CONFIG,
): VerticalFlightDecision {
  assertConfig(config);
  assertObservation(observation, config);
  const frame = observation.accepted;
  const altitude = frame.position[1] - FLIGHT_MODEL.ground_y;
  const c = config.controller;
  const requestedPhase = phase;
  let enteredFlight = false;

  if (phase === 'awaiting_takeoff') {
    if (frame.step !== 0 || frame.state !== 'grounded' || frame.position[1] !== FLIGHT_MODEL.ground_y || frame.velocity.some(v => v !== 0))
      throw new Error('Vertical flight must begin from its accepted grounded initial state');
    return decision(phase, 'takeoff', 'explicit_initial_takeoff_request', frame, 'TAKEOFF', c.takeoff_vertical_command);
  }

  if (phase === 'takeoff') {
    if (frame.state === 'takeoff') return decision(phase, phase, 'plant_takeoff_in_progress', frame, 'HOLD', c.takeoff_vertical_command);
    if (frame.state !== 'flying') throw new Error(`Invalid plant state ${frame.state} during takeoff feedback`);
    phase = 'climb';
    enteredFlight = true;
  }

  if (phase === 'climb') {
    if (frame.state !== 'flying') throw new Error(`Invalid plant state ${frame.state} during altitude feedback`);
    if (frame.contacts.length) throw new Error(`Unexpected contact during altitude feedback: ${frame.contacts.join(', ')}`);
    const error = c.target_altitude_above_ground - altitude;
    if (altitude > c.target_altitude_above_ground + c.target_altitude_tolerance)
      throw new Error('Accepted altitude exceeded the configured target tolerance before descent');
    if (Math.abs(error) <= c.target_altitude_tolerance && Math.abs(frame.velocity[1]) <= c.settled_vertical_speed)
      return decision(requestedPhase, 'descent', enteredFlight ? 'plant_entered_flying_and_altitude_condition_reached' : 'accepted_altitude_and_vertical_speed_within_tolerance', frame, 'LAND', 0);
    const desiredVerticalSpeed = clamp(
      c.altitude_kp_s_inv * error - c.vertical_velocity_kd * frame.velocity[1],
      -FLIGHT_MODEL.max_vertical_speed,
      FLIGHT_MODEL.max_vertical_speed,
    );
    return decision(requestedPhase, 'climb', enteredFlight ? 'plant_entered_flying;bounded_altitude_velocity_feedback' : 'bounded_altitude_velocity_feedback', frame, 'HOLD', desiredVerticalSpeed / FLIGHT_MODEL.max_vertical_speed);
  }

  if (phase === 'descent') {
    if (frame.state === 'landing') return decision(phase, phase, 'plant_landing_in_progress', frame, 'HOLD', 0);
    if (frame.state === 'grounded' && frame.contacts.includes('FLOOR') && frame.position[1] === FLIGHT_MODEL.ground_y && frame.velocity.every(v => v === 0))
      return decision(phase, 'complete', 'accepted_floor_contact_and_grounded_state', frame, 'HOLD', 0);
    throw new Error(`Invalid plant state ${frame.state} during landing feedback`);
  }

  if (phase === 'complete' && frame.state === 'grounded')
    return decision(phase, phase, 'flight_already_complete', frame, 'HOLD', 0);
  throw new Error(`Controller phase ${phase} is inconsistent with accepted plant state ${frame.state}`);
}

function transitionPath(previous: FlightFrame, accepted: FlightFrame) {
  let current = previous.state;
  for (const event of accepted.events.filter(event => event.kind === 'TRANSITION')) {
    const [from, to] = event.detail.split('->');
    if (from !== current || !(states.includes(from as typeof current) && states.includes(to as typeof current)) || !legalTransitions[current].includes(to as typeof current))
      throw new Error(`Illegal accepted flight transition ${event.detail}`);
    current = to as typeof current;
  }
  if (current !== accepted.state) throw new Error('Accepted flight state does not match its transition events');
}

export class VerticalFlightSession {
  readonly config: VerticalFlightConfig;
  private readonly engine: FlightEngine;
  private phase: VerticalControllerPhase = 'awaiting_takeoff';
  private readonly intervals: VerticalFlightInterval[] = [];
  private failure: string | null = null;
  private termination: VerticalFlightTermination | null = null;
  status: VerticalFlightStatus = 'ready';

  constructor(config: VerticalFlightConfig = VERTICAL_FLIGHT_CONFIG) {
    assertConfig(config);
    this.config = structuredClone(config);
    this.engine = new FlightEngine(createFlightTrial([], config.maximum_steps, 'normal'));
  }

  get stopStep() {
    return this.termination ? this.engine.snapshot().step : this.config.maximum_steps;
  }
  get error() { return this.failure; }
  get controllerPhase() { return this.phase; }
  snapshot() { return this.engine.snapshot(); }
  records() { return structuredClone(this.intervals); }
  start() {
    if (!['ready', 'paused'].includes(this.status)) throw new Error('Vertical flight session cannot start');
    this.status = 'running';
  }
  pause() { if (this.status === 'running') this.status = 'paused'; }

  advance() {
    if (this.status !== 'running') throw new Error('Vertical flight session is not running');
    const before = this.engine.snapshot();
    const observation: VerticalFlightObservation = { accepted: before, bounds: structuredClone(this.config.environment.bounds) };
    try {
      const selected = decideVerticalFlight(this.phase, observation, this.config);
      if (!selected.command) throw new Error('Controller completed before the flight plant reached its terminal grounded state');
      if (selected.command.step !== before.step || selected.command.forward !== 0 || selected.command.turn !== 0)
        throw new Error('Controller emitted a misaligned or nonvertical motor command');
      const accepted = this.engine.advanceWithCommand(selected.command);
      transitionPath(before, accepted);
      if (!accepted.position.every(Number.isFinite) || !accepted.velocity.every(Number.isFinite) || !Number.isFinite(accepted.time))
        throw new Error('FlightEngine produced a non-finite accepted state');
      for (let axis = 0; axis < 3; axis++) {
        if (accepted.position[axis] < observation.bounds.min[axis] || accepted.position[axis] > observation.bounds.max[axis])
          throw new Error(`FlightEngine accepted position outside axis ${axis} bounds`);
      }
      if (accepted.contacts.some(contact => contact !== 'FLOOR') ||
          (accepted.contacts.includes('FLOOR') && (accepted.state !== 'grounded' || selected.phase_after !== 'descent')))
        throw new Error(`Unexpected flight contact: ${accepted.contacts.join(', ')}`);
      if (accepted.events.some(event => event.kind === 'REJECTED_COMMAND')) throw new Error('FlightEngine rejected the feedback command');
      this.phase = selected.phase_after;
      this.intervals.push({
        command_origin: 'STATE_FEEDBACK_CONTROLLER_V1',
        observation_time_s: before.time,
        observation_step: before.step,
        observation,
        decision: selected,
        accepted,
      });
      if (accepted.state === 'grounded') {
        const targetReached = this.intervals.some(interval => interval.decision.transition_reason === 'accepted_altitude_and_vertical_speed_within_tolerance');
        const tookOff = this.intervals.some(interval => interval.accepted.state === 'flying' || interval.accepted.state === 'landing');
        const landedFromLanding = before.state === 'landing' && accepted.contacts.includes('FLOOR') && this.phase === 'descent';
        if (!targetReached || !tookOff || !landedFromLanding) throw new Error('Ground contact occurred before a valid takeoff, altitude condition, and landing transition');
        this.phase = 'complete'; this.termination = 'LANDED'; this.status = 'completed';
      } else if (accepted.step >= this.config.maximum_steps) {
        this.termination = 'TIMEOUT'; this.failure = 'Maximum verification duration reached before landing'; this.status = 'failed';
      }
      return accepted;
    } catch (error) {
      this.failure = error instanceof Error ? error.message : String(error);
      this.termination = 'FAILED'; this.status = 'failed';
      throw error;
    }
  }

  metrics() { return verticalFlightMetrics(this.engine.frames(), this.engine.events(), this.config); }

  result() {
    if (!this.termination) throw new Error('Vertical flight verification is not terminal');
    const metrics = this.metrics();
    const body = {
      schema: 'neurofly_vertical_flight_result_v1',
      classification: this.config.classification,
      configuration: structuredClone(this.config),
      provenance: {
        controller_id: this.config.controller.id,
        controller_version: this.config.controller.version,
        plant_schema: FLIGHT_MODEL.schema,
        plant_source_glb_sha256: FLIGHT_MODEL.source_glb_sha256,
        command_origin: 'STATE_FEEDBACK_CONTROLLER_V1',
        seed: this.config.seed,
        randomness: this.config.randomness,
      },
      intervals: this.records(),
      events: this.engine.events(),
      termination: this.termination,
      failure: this.failure,
      metrics,
    };
    return structuredClone(body);
  }
}

export function verticalFlightMetrics(frames: FlightFrame[], events: FlightFrame['events'], config: VerticalFlightConfig = VERTICAL_FLIGHT_CONFIG) {
  const takeoffEvent = events.find(event => event.kind === 'TRANSITION' && event.detail === 'grounded->takeoff');
  const descentEvent = events.find(event => event.kind === 'TRANSITION' && (event.detail === 'flying->landing' || event.detail === 'takeoff->landing'));
  const firstFlying = frames.find(frame => frame.state === 'flying');
  const final = frames.at(-1)!;
  const altitudes = frames.map(frame => frame.position[1] - FLIGHT_MODEL.ground_y);
  const verticalVelocities = frames.map(frame => frame.velocity[1]);
  const bounds = config.environment.bounds;
  const boundViolations = frames.reduce((count, frame) => count + Number(frame.position.some((value, axis) => value < bounds.min[axis] || value > bounds.max[axis])), 0);
  return {
    takeoff_time_s: takeoffEvent?.time ?? null,
    airborne_start_time_s: firstFlying?.time ?? null,
    airborne_duration_s: firstFlying ? Math.max(0, final.time - firstFlying.time) : 0,
    target_altitude_above_ground: config.controller.target_altitude_above_ground,
    target_condition_reached: targetConditionIn(frames, config),
    maximum_altitude_above_ground: Math.max(...altitudes),
    vertical_velocity_range: [Math.min(...verticalVelocities), Math.max(...verticalVelocities)] as [number, number],
    descent_onset_time_s: descentEvent?.time ?? null,
    landing_time_s: final.state === 'grounded' && final.step > 0 ? final.time : null,
    contacts: events.filter(event => event.kind === 'CONTACT').map(event => ({ time: event.time, detail: event.detail })),
    bound_violations: boundViolations,
    accepted_intervals: Math.max(0, frames.length - 1),
    final_state: final.state,
    final_position: [...final.position] as Vec3,
    final_velocity: [...final.velocity] as Vec3,
  };
}

function targetConditionIn(frames: FlightFrame[], config: VerticalFlightConfig) {
  return frames.some(frame => frame.state === 'flying' &&
    Math.abs((frame.position[1] - FLIGHT_MODEL.ground_y) - config.controller.target_altitude_above_ground) <= config.controller.target_altitude_tolerance &&
    Math.abs(frame.velocity[1]) <= config.controller.settled_vertical_speed);
}

/** Bounded, deterministic offline verification runner; it never writes artifacts. */
export function runVerticalFlightVerification(config: VerticalFlightConfig = VERTICAL_FLIGHT_CONFIG) {
  const session = new VerticalFlightSession(config);
  session.start();
  while (session.status === 'running') {
    try { session.advance(); }
    catch { break; }
  }
  return session.result();
}

export async function verticalFlightResultHashes(result: ReturnType<VerticalFlightSession['result']>) {
  const { schema, classification, configuration, ...body } = result;
  const input = { schema, classification, configuration };
  return { input_sha256: await flightHash(input), result_sha256: await flightHash(body) };
}

export function canonicalVerticalFlightResult(result: ReturnType<VerticalFlightSession['result']>) {
  return flightCanonical(result);
}
