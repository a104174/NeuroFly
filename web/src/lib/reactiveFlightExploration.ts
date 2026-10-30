/** Engineering-only, deterministic closed-loop flight inside the existing chamber. */
import {
  FlightEngine, FLIGHT_MODEL, createFlightTrial, flightBounds, flightCanonical,
  flightHash, initialFlightFrame, type FlightCommand, type FlightEvent, type FlightFrame,
} from './engineeringFlight';
import { ARENA } from './experimentalArena';
import { observeFlightArena, validateFlightArenaObservation, type FlightArenaObservation } from './flightArenaObservations';

export const REACTIVE_FLIGHT_CONTROLLER = Object.freeze({
  id: 'engineering_reactive_flight_v1',
  version: 1,
  policy: 'accepted_state_geometric_wall_feedback_and_altitude_pd',
  explicit_takeoff_vertical_command: 0.8,
  cruise_forward_command: 0.85,
  near_wall_minimum_forward_command: 0.3,
  wall_approach_clearance_units: 0.34,
  wall_release_clearance_units: 0.5,
  wall_turn_command: 0.85,
  target_altitude_above_floor_units: 0.3,
  altitude_kp_s_inv: 1.5,
  vertical_velocity_kd: 1.2,
  floor_ceiling_recovery_clearance_units: 0.06,
});

export const REACTIVE_FLIGHT_ACCEPTANCE = Object.freeze({
  minimum_horizontal_distance_units: 1,
  minimum_x_extent_units: 0.75,
  minimum_z_extent_units: 0.25,
  minimum_steering_responses: 2,
  maximum_accepted_bound_violations: 0,
  maximum_floor_or_ceiling_contacts: 0,
});

export const REACTIVE_FLIGHT_CONFIG = Object.freeze({
  schema: 'neurofly_engineering_reactive_flight_v1',
  classification: 'ENGINEERING_STATE_FEEDBACK_NOT_BIOLOGICALLY_VALIDATED',
  controller: REACTIVE_FLIGHT_CONTROLLER,
  observation_schema: 'neurofly_flight_arena_observation_v1',
  initial_state: initialFlightFrame(),
  environment: {
    id: 'neurofly_experimental_arena_v1',
    chamber: structuredClone(ARENA.chamber),
    bounds: flightBounds(),
    bounds_source: 'engineeringFlight.flightBounds',
  },
  plant_schema: FLIGHT_MODEL.schema,
  plant_limits: {
    max_forward_speed_units_s: FLIGHT_MODEL.max_forward_speed,
    max_vertical_speed_units_s: FLIGHT_MODEL.max_vertical_speed,
    horizontal_acceleration_units_s2: FLIGHT_MODEL.horizontal_acceleration,
    vertical_acceleration_units_s2: FLIGHT_MODEL.vertical_acceleration,
    max_turn_rate_rad_s: FLIGHT_MODEL.max_turn_rate,
    horizontal_clearance_units: FLIGHT_MODEL.horizontal_clearance,
    upper_clearance_units: FLIGHT_MODEL.upper_clearance,
  },
  interval_s: FLIGHT_MODEL.dt_s,
  maximum_duration_s: 30,
  maximum_steps: Math.round(30 / FLIGHT_MODEL.dt_s),
  takeoff_trigger: 'EXPLICIT_START_ACTION_AT_INITIAL_GROUNDED_ACCEPTED_STATE',
  termination: 'FIXED_MAXIMUM_SIMULATION_DURATION_OR_EXPLICIT_VALIDATION_FAILURE',
  command_origin: 'ENGINEERING_STATE_FEEDBACK_REACTIVE_V1',
  seed: null,
  randomness: 'NONE',
  wing_presentation: { schema: 'engineering_flight_wings_v8', preset: 'normal', source: 'PRESENTATION_ONLY_NO_LIFT' },
  acceptance: REACTIVE_FLIGHT_ACCEPTANCE,
} as const);

export type ReactiveFlightConfig = typeof REACTIVE_FLIGHT_CONFIG;
export type ReactiveControllerPhase = 'ready' | 'takeoff' | 'exploring';
export type AvoidanceTurn = -1 | 0 | 1;
export type ReactiveControllerState = { phase: ReactiveControllerPhase; avoidance_turn: AvoidanceTurn };
export type BoundaryResponse = 'none' | 'started' | 'continued' | 'released' | 'redirected';
export type ReactiveFlightDecision = {
  state_before: ReactiveControllerState;
  state_after: ReactiveControllerState;
  reason: string;
  boundary_response: BoundaryResponse;
  command: FlightCommand;
};
export type ReactiveFlightInterval = {
  command_origin: typeof REACTIVE_FLIGHT_CONFIG.command_origin;
  observation_step: number;
  observation_time_s: number;
  observation: FlightArenaObservation;
  decision: ReactiveFlightDecision;
  accepted: FlightFrame;
};
export type ReactiveFlightStatus = 'ready' | 'running' | 'paused' | 'completed' | 'failed';
export type ReactiveFlightTermination = 'DURATION_LIMIT_REACHED' | 'FAILED';

const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));
const physicalStates = ['grounded', 'takeoff', 'flying', 'landing'] as const;
const legalTransitions: Record<(typeof physicalStates)[number], readonly (typeof physicalStates)[number][]> = {
  grounded: ['takeoff'], takeoff: ['flying', 'landing'], flying: ['landing'], landing: ['grounded'],
};

function assertConfig(config: ReactiveFlightConfig) {
  if (!config || flightCanonical(config) !== flightCanonical(REACTIVE_FLIGHT_CONFIG))
    throw new Error('Unsupported reactive-flight configuration identity');
  const { bounds } = config.environment;
  const targetY = bounds.min[1] + config.controller.target_altitude_above_floor_units;
  const safety = config.controller.floor_ceiling_recovery_clearance_units;
  if (config.plant_schema !== FLIGHT_MODEL.schema || config.interval_s !== FLIGHT_MODEL.dt_s ||
      config.maximum_steps !== config.maximum_duration_s / config.interval_s || config.maximum_steps > 1500 ||
      !(targetY - safety > bounds.min[1] && targetY + safety < bounds.max[1]) ||
      config.controller.wall_approach_clearance_units >= config.controller.wall_release_clearance_units ||
      config.controller.wall_release_clearance_units <= 0 ||
      flightCanonical(bounds) !== flightCanonical(flightBounds()))
    throw new Error('Reactive-flight configuration is inadmissible for the existing plant bounds');
}

function makeCommand(step: number, forward: number, turn: number, vertical: number, intent: FlightCommand['intent']): FlightCommand {
  return { id: `reactive-flight-${step}`, step, forward: clamp(forward, -1, 1), turn: clamp(turn, -1, 1), vertical: clamp(vertical, -1, 1), intent };
}

function turnTowardMoreClearance(observation: FlightArenaObservation): AvoidanceTurn {
  if (Math.abs(observation.right_wall_clearance_units - observation.left_wall_clearance_units) <= 1e-12) return 1;
  return observation.right_wall_clearance_units > observation.left_wall_clearance_units ? 1 : -1;
}

function verticalCommand(observation: FlightArenaObservation, config: ReactiveFlightConfig) {
  const c = config.controller;
  if (observation.ceiling_clearance_units < c.floor_ceiling_recovery_clearance_units) return -1;
  if (observation.floor_clearance_units < c.floor_ceiling_recovery_clearance_units) return 1;
  const altitudeError = c.target_altitude_above_floor_units - observation.floor_clearance_units;
  const desiredVerticalSpeed = clamp(
    c.altitude_kp_s_inv * altitudeError - c.vertical_velocity_kd * observation.accepted.velocity[1],
    -FLIGHT_MODEL.max_vertical_speed,
    FLIGHT_MODEL.max_vertical_speed,
  );
  return desiredVerticalSpeed / FLIGHT_MODEL.max_vertical_speed;
}

/** Pure controller: one accepted boundary and the previous hysteresis state produce the next interval command. */
export function decideReactiveFlight(
  state: ReactiveControllerState,
  suppliedObservation: FlightArenaObservation,
  config: ReactiveFlightConfig = REACTIVE_FLIGHT_CONFIG,
): ReactiveFlightDecision {
  assertConfig(config);
  const observation = validateFlightArenaObservation(suppliedObservation, config.environment.bounds);
  const frame = observation.accepted;
  if (frame.step >= config.maximum_steps) throw new Error('Reactive-flight duration limit has no outgoing command interval');
  if (!state || Object.keys(state).sort().join(',') !== 'avoidance_turn,phase' ||
      !['ready', 'takeoff', 'exploring'].includes(state.phase) || ![-1, 0, 1].includes(state.avoidance_turn))
    throw new Error('Invalid reactive-flight controller state');
  const stateBefore = structuredClone(state);
  if (state.phase === 'ready') {
    if (frame.step !== 0 || frame.state !== 'grounded' || flightCanonical(frame) !== flightCanonical(config.initial_state))
      throw new Error('Reactive flight must start from its accepted grounded initial state');
    return {
      state_before: stateBefore, state_after: { phase: 'takeoff', avoidance_turn: 0 },
      reason: 'explicit_start_requested_takeoff', boundary_response: 'none',
      command: makeCommand(frame.step, 0, 0, config.controller.explicit_takeoff_vertical_command, 'TAKEOFF'),
    };
  }

  let enteredExploration = false;
  if (state.phase === 'takeoff') {
    if (frame.state === 'takeoff') return {
      state_before: stateBefore, state_after: stateBefore,
      reason: 'plant_accepted_takeoff_in_progress', boundary_response: 'none',
      command: makeCommand(frame.step, 0, 0, config.controller.explicit_takeoff_vertical_command, 'HOLD'),
    };
    if (frame.state !== 'flying') throw new Error(`Invalid plant state ${frame.state} during takeoff`);
    enteredExploration = true;
    state = { phase: 'exploring', avoidance_turn: 0 };
  }

  if (state.phase !== 'exploring' || frame.state !== 'flying')
    throw new Error(`Reactive exploration requires accepted flying state; got ${state.phase}/${frame.state}`);
  if (frame.contacts.some(contact => contact === 'FLOOR' || contact === 'CEILING'))
    throw new Error(`Unexpected vertical contact during exploration: ${frame.contacts.join(', ')}`);
  const unexpectedContacts = frame.contacts.filter(contact => contact !== 'X_WALL' && contact !== 'Z_WALL');
  if (unexpectedContacts.length) throw new Error(`Unsupported accepted contact: ${unexpectedContacts.join(', ')}`);

  const c = config.controller;
  const wallContact = frame.contacts.some(contact => contact === 'X_WALL' || contact === 'Z_WALL');
  let avoidance = state.avoidance_turn;
  let boundaryResponse: BoundaryResponse = avoidance ? 'continued' : 'none';
  let reason = 'open_space_state_feedback';
  if (avoidance !== 0 && observation.forward_wall_clearance_units >= c.wall_release_clearance_units && !wallContact) {
    avoidance = 0;
    boundaryResponse = 'released';
    reason = 'accepted_forward_clearance_recovered';
  }
  if (wallContact) {
    avoidance = turnTowardMoreClearance(observation);
    boundaryResponse = state.avoidance_turn === 0 ? 'started' : 'redirected';
    reason = 'accepted_wall_contact_turn_toward_larger_side_clearance';
  } else if (avoidance === 0 && observation.forward_wall_clearance_units <= c.wall_approach_clearance_units) {
    avoidance = turnTowardMoreClearance(observation);
    boundaryResponse = 'started';
    reason = 'forward_wall_clearance_below_approach_threshold';
  }

  const forward = avoidance === 0
    ? c.cruise_forward_command
    : c.near_wall_minimum_forward_command +
      (c.cruise_forward_command - c.near_wall_minimum_forward_command) *
      clamp(observation.forward_wall_clearance_units / c.wall_approach_clearance_units, 0, 1);
  const turn = avoidance * c.wall_turn_command;
  const nextState: ReactiveControllerState = { phase: 'exploring', avoidance_turn: avoidance };
  if (enteredExploration) reason = `accepted_flying_state_entered_exploration;${reason}`;
  return {
    state_before: stateBefore, state_after: nextState, reason, boundary_response: boundaryResponse,
    command: makeCommand(frame.step, forward, turn, verticalCommand(observation, config), 'HOLD'),
  };
}

function transitionPath(previous: FlightFrame, accepted: FlightFrame) {
  let current = previous.state;
  for (const event of accepted.events.filter(item => item.kind === 'TRANSITION')) {
    const [from, to] = event.detail.split('->');
    if (from !== current || !physicalStates.includes(from as typeof current) || !physicalStates.includes(to as typeof current) ||
        !legalTransitions[current].includes(to as typeof current)) throw new Error(`Illegal accepted flight transition ${event.detail}`);
    current = to as typeof current;
  }
  if (current !== accepted.state) throw new Error('Accepted flight state does not match plant transition events');
}

export class ReactiveFlightExplorationSession {
  readonly config: ReactiveFlightConfig;
  private readonly engine: FlightEngine;
  private controllerState: ReactiveControllerState = { phase: 'ready', avoidance_turn: 0 };
  private readonly intervals: ReactiveFlightInterval[] = [];
  private failure: string | null = null;
  private termination: ReactiveFlightTermination | null = null;
  status: ReactiveFlightStatus = 'ready';

  constructor(config: ReactiveFlightConfig = REACTIVE_FLIGHT_CONFIG) {
    assertConfig(config);
    this.config = structuredClone(config);
    this.engine = new FlightEngine(createFlightTrial([], config.maximum_steps, 'normal'));
  }

  get stopStep() { return this.termination ? this.engine.snapshot().step : this.config.maximum_steps; }
  get error() { return this.failure; }
  get controllerPhase() { return this.controllerState.phase; }
  snapshot() { return this.engine.snapshot(); }
  records() { return structuredClone(this.intervals); }
  latestInterval() { const value = this.intervals.at(-1); return value ? structuredClone(value) : null; }
  start() { if (!['ready', 'paused'].includes(this.status)) throw new Error('Reactive-flight session cannot start'); this.status = 'running'; }
  pause() { if (this.status === 'running') this.status = 'paused'; }

  advance() {
    if (this.status !== 'running') throw new Error('Reactive-flight session is not running');
    const before = this.engine.snapshot();
    const observation = observeFlightArena(before, this.config.environment.bounds);
    try {
      const decision = decideReactiveFlight(this.controllerState, observation, this.config);
      if (decision.command.step !== before.step) throw new Error('Reactive-flight command is not aligned to its accepted observation');
      const accepted = this.engine.advanceWithCommand(decision.command);
      const interval: ReactiveFlightInterval = {
        command_origin: this.config.command_origin,
        observation_step: before.step,
        observation_time_s: before.time,
        observation,
        decision,
        accepted,
      };
      this.intervals.push(interval);
      this.controllerState = structuredClone(decision.state_after);
      transitionPath(before, accepted);
      if (accepted.events.some(event => event.kind === 'REJECTED_COMMAND')) throw new Error('FlightEngine rejected a reactive feedback command');
      if (![...accepted.position, ...accepted.velocity, accepted.heading, accepted.time].every(Number.isFinite)) throw new Error('FlightEngine produced non-finite accepted state');
      for (let axis = 0; axis < 3; axis++) {
        if (accepted.position[axis] < this.config.environment.bounds.min[axis] || accepted.position[axis] > this.config.environment.bounds.max[axis])
          throw new Error(`FlightEngine accepted position outside axis ${axis} bounds`);
      }
      if (accepted.contacts.some(contact => contact === 'FLOOR' || contact === 'CEILING'))
        throw new Error(`FlightEngine reached an inadmissible vertical contact: ${accepted.contacts.join(', ')}`);
      if (accepted.step >= this.config.maximum_steps) {
        this.termination = 'DURATION_LIMIT_REACHED';
        this.status = 'completed';
      }
      return accepted;
    } catch (error) {
      this.failure = error instanceof Error ? error.message : String(error);
      this.termination = 'FAILED';
      this.status = 'failed';
      throw error;
    }
  }

  metrics() { return reactiveFlightMetrics(this.config.initial_state, this.engine.frames(), this.intervals, this.engine.events(), this.config); }

  result() {
    if (!this.termination) throw new Error('Reactive-flight run is not terminal');
    const metrics = this.metrics();
    const acceptance = evaluateReactiveFlightAcceptance(metrics, this.config.acceptance);
    return structuredClone({
      schema: 'neurofly_engineering_reactive_flight_result_v1',
      classification: this.config.classification,
      configuration: this.config,
      provenance: {
        controller_id: this.config.controller.id,
        controller_version: this.config.controller.version,
        observation_schema: this.config.observation_schema,
        plant_schema: FLIGHT_MODEL.schema,
        plant_source_glb_sha256: FLIGHT_MODEL.source_glb_sha256,
        command_origin: this.config.command_origin,
        seed: this.config.seed,
        randomness: this.config.randomness,
      },
      intervals: this.records(),
      events: this.engine.events(),
      termination: this.termination,
      failure: this.failure,
      acceptance,
      metrics,
    });
  }
}

export function reactiveFlightMetrics(
  initial: FlightFrame,
  frames: FlightFrame[],
  intervals: ReactiveFlightInterval[],
  events: FlightEvent[],
  config: ReactiveFlightConfig = REACTIVE_FLIGHT_CONFIG,
) {
  const all = [initial, ...frames.slice(1)];
  const firstAirborne = all.find(frame => frame.state === 'flying');
  const final = all.at(-1)!;
  const altitudes = all.map(frame => frame.position[1] - config.environment.bounds.min[1]);
  const horizontalDistance = all.slice(1).reduce((sum, frame, index) => sum + Math.hypot(
    frame.position[0] - all[index].position[0], frame.position[2] - all[index].position[2],
  ), 0);
  const observations = intervals.map(interval => interval.observation);
  const xValues = all.map(frame => frame.position[0]), zValues = all.map(frame => frame.position[2]);
  const boundViolations = all.reduce((count, frame) => count + Number(frame.position.some((value, axis) =>
    value < config.environment.bounds.min[axis] || value > config.environment.bounds.max[axis])), 0);
  const floorCeilingContacts = events.filter(event => event.kind === 'CONTACT' && (event.detail === 'FLOOR' || event.detail === 'CEILING'));
  return {
    takeoff_time_s: events.find(event => event.kind === 'TRANSITION' && event.detail === 'grounded->takeoff')?.time ?? null,
    airborne_start_time_s: firstAirborne?.time ?? null,
    airborne_duration_s: firstAirborne ? Math.max(0, final.time - firstAirborne.time) : 0,
    horizontal_distance_units: horizontalDistance,
    explored_x_range_units: [Math.min(...xValues), Math.max(...xValues)] as [number, number],
    explored_z_range_units: [Math.min(...zValues), Math.max(...zValues)] as [number, number],
    explored_x_extent_units: Math.max(...xValues) - Math.min(...xValues),
    explored_z_extent_units: Math.max(...zValues) - Math.min(...zValues),
    altitude_range_above_floor_units: [Math.min(...altitudes), Math.max(...altitudes)] as [number, number],
    vertical_velocity_range_units_s: [Math.min(...all.map(frame => frame.velocity[1])), Math.max(...all.map(frame => frame.velocity[1]))] as [number, number],
    steering_response_count: intervals.filter(interval => interval.decision.boundary_response === 'started' || interval.decision.boundary_response === 'redirected').length,
    minimum_observed_wall_clearance_units: observations.length ? Math.min(...observations.flatMap(observation => [
      observation.forward_wall_clearance_units, observation.left_wall_clearance_units, observation.right_wall_clearance_units,
    ])) : null,
    wall_contacts: events.filter(event => event.kind === 'CONTACT' && (event.detail === 'X_WALL' || event.detail === 'Z_WALL')).map(event => ({ time_s: event.time, boundary: event.detail })),
    floor_ceiling_contacts: floorCeilingContacts.map(event => ({ time_s: event.time, boundary: event.detail })),
    accepted_bound_violations: boundViolations,
    invalid_command_count: events.filter(event => event.kind === 'REJECTED_COMMAND').length,
    accepted_state_count: all.length,
    final_time_s: final.time,
    final_state: final.state,
    final_position: [...final.position],
    final_velocity: [...final.velocity],
  };
}

export function evaluateReactiveFlightAcceptance(metrics: ReturnType<typeof reactiveFlightMetrics>, acceptance = REACTIVE_FLIGHT_ACCEPTANCE) {
  const checks = {
    horizontal_travel: metrics.horizontal_distance_units >= acceptance.minimum_horizontal_distance_units,
    x_extent: metrics.explored_x_extent_units >= acceptance.minimum_x_extent_units,
    z_extent: metrics.explored_z_extent_units >= acceptance.minimum_z_extent_units,
    repeated_boundary_steering: metrics.steering_response_count >= acceptance.minimum_steering_responses,
    accepted_bounds: metrics.accepted_bound_violations <= acceptance.maximum_accepted_bound_violations,
    floor_ceiling_contacts: metrics.floor_ceiling_contacts.length <= acceptance.maximum_floor_or_ceiling_contacts,
    finite_state: [...metrics.final_position, ...metrics.final_velocity, metrics.final_time_s].every(Number.isFinite),
    flight_occurred: metrics.airborne_duration_s > 0,
  };
  return { passed: Object.values(checks).every(Boolean), checks };
}

/** Finite, deterministic in-memory verification; no files or network services are used. */
export function runReactiveFlightVerification(config: ReactiveFlightConfig = REACTIVE_FLIGHT_CONFIG) {
  const session = new ReactiveFlightExplorationSession(config);
  session.start();
  while (session.status === 'running') {
    try { session.advance(); } catch { break; }
  }
  return session.result();
}

export function canonicalReactiveFlightResult(result: ReturnType<ReactiveFlightExplorationSession['result']>) {
  return flightCanonical(result);
}

export async function reactiveFlightResultHashes(result: ReturnType<ReactiveFlightExplorationSession['result']>) {
  const { schema, classification, configuration, ...body } = result;
  return {
    input_sha256: await flightHash({ schema, classification, configuration }),
    result_sha256: await flightHash(body),
  };
}
