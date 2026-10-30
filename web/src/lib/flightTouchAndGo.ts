/** Engineering transition policy composed with unchanged reactive flight; no neural or renderer inputs. */
import { FlightEngine, FLIGHT_MODEL, createFlightTrial, flightCanonical, flightHash, initialFlightFrame, type FlightCommand } from './engineeringFlight';
import { observeFlightArena, validateFlightArenaObservation, type FlightArenaObservation } from './flightArenaObservations';
import { REACTIVE_FLIGHT_CONFIG, decideReactiveFlight, reactiveFlightMetrics, type ReactiveControllerState, type ReactiveFlightDecision, type ReactiveFlightStatus } from './reactiveFlightExploration';

export const TOUCH_AND_GO_CONFIG = {
  schema: 'neurofly_flight_touch_and_go_v1',
  controller: { id: 'engineering_flight_touch_and_go_v1', version: 1 },
  reactive_configuration: REACTIVE_FLIGHT_CONFIG,
  landing_trigger: 'ACCEPTED_BOUNDARY_AVOIDANCE_RELEASE_THEN_SAFE_BRAKED_ALTITUDE',
  horizontal_settled_speed: .01,
  vertical_settled_speed: .02,
  altitude_tolerance: .02,
  minimum_horizontal_clearance: .06,
  retakeoff_trigger: 'VERIFIED_LANDING_FLOOR_CONTACT_THEN_ONE_SETTLED_GROUNDED_HOLD_INTERVAL_AND_CLEAR_CORRIDOR',
  maximum_steps: 1500, interval_s: .02, seed: null, randomness: 'NONE',
  termination: 'SECOND_ACCEPTED_FLYING_STATE_WITH_EXPLORATION_COMMAND_OR_FAILURE_OR_DURATION_LIMIT',
} as const;
type Phase = 'ready' | 'takeoff' | 'exploring' | 'braking' | 'landing' | 'grounded' | 'retakeoff_ready' | 'retakeoff' | 'exploring_again';
export type TouchAndGoState = { phase: Phase; reactive: ReactiveControllerState; floor_verified: boolean };
export const initialTouchAndGoState = (): TouchAndGoState => ({ phase: 'ready', reactive: { phase: 'ready', avoidance_turn: 0 }, floor_verified: false });
export type TouchAndGoDecision = {
  state_before: TouchAndGoState; state_after: TouchAndGoState;
  landing_eligible: boolean; takeoff_eligible: boolean; reason: string;
  command: FlightCommand; reactive_decision: ReactiveFlightDecision | null;
  recovery?: { schema: 'landing_clearance_recovery_interval_v1'; observed_clearance: number; required_clearance: number; eligible: boolean; active: boolean; base_phase_after: Phase };
};
type Decision = TouchAndGoDecision;
export function decideTouchAndGo(state: TouchAndGoState, supplied: FlightArenaObservation, declaredInitialHeading?: number): Decision {
  const o = validateFlightArenaObservation(supplied), f = o.accepted, c = TOUCH_AND_GO_CONFIG;
  if (!state || !['ready','takeoff','exploring','braking','landing','grounded','retakeoff_ready','retakeoff','exploring_again'].includes(state.phase) ||
      typeof state.floor_verified !== 'boolean') throw new Error('invalid_controller_state');
  if ((['exploring','exploring_again','braking'].includes(state.phase) && f.state !== 'flying') ||
      (['grounded','retakeoff_ready'].includes(state.phase) && f.state !== 'grounded'))
    throw new Error('illegal_state_transition');
  if (f.step >= c.maximum_steps) throw new Error('duration_limit_reached');
  if (f.contacts.some(contact => contact !== 'FLOOR') || (f.contacts.includes('FLOOR') && f.state !== 'grounded')) throw new Error('invalid_contact');
  const after = structuredClone(state);
  const clearance = Math.min(o.forward_wall_clearance_units, o.left_wall_clearance_units, o.right_wall_clearance_units);
  const safeCorridor = clearance >= c.minimum_horizontal_clearance;
  const settled = f.velocity.every(v => Math.abs(v) <= 1e-12);
  const groundValid = f.state === 'grounded' && o.floor_clearance_units === 0 && settled;
  const landingEligible = f.state === 'flying' && safeCorridor && !f.contacts.length &&
    o.horizontal_speed_units_s <= c.horizontal_settled_speed && Math.abs(f.velocity[1]) <= c.vertical_settled_speed &&
    Math.abs(o.floor_clearance_units - REACTIVE_FLIGHT_CONFIG.controller.target_altitude_above_floor_units) <= c.altitude_tolerance;
  const takeoffEligible = groundValid && safeCorridor && o.ceiling_clearance_units >= REACTIVE_FLIGHT_CONFIG.controller.target_altitude_above_floor_units + .06 &&
    state.floor_verified && state.phase === 'retakeoff_ready';
  const emit = (reason: string, intent: FlightCommand['intent'] = 'HOLD', vertical = 0, forward = 0, turn = 0, reactive: ReactiveFlightDecision | null = null): Decision => ({
    state_before: structuredClone(state), state_after: after, landing_eligible: landingEligible,
    takeoff_eligible: takeoffEligible, reason, reactive_decision: reactive,
    command: { id: 'touch-and-go-' + f.step, step: f.step, forward, turn, vertical, intent },
  });
  // Evaluation-only startup boundary: same explicit motor request, validated against the declared initial pose.
  if (state.phase === 'ready' && declaredInitialHeading !== undefined) {
    if (!Number.isFinite(declaredInitialHeading) || flightCanonical(f) !== flightCanonical({...initialFlightFrame(),heading:declaredInitialHeading}))
      throw new Error('Invalid declared initial-heading evaluation state');
    after.phase='takeoff';after.reactive={phase:'takeoff',avoidance_turn:0};
    return emit('explicit_start_at_declared_evaluation_heading','TAKEOFF',REACTIVE_FLIGHT_CONFIG.controller.explicit_takeoff_vertical_command);
  }
  if (state.phase === 'landing') {
    if (groundValid && f.contacts.includes('FLOOR')) {
      after.phase = 'grounded'; after.floor_verified = true;
      return emit('accepted_landing_floor_contact;validate_grounded_hold');
    }
    if (f.state !== 'landing') throw new Error('illegal_state_transition');
    return emit('plant_landing_in_progress');
  }
  if (state.phase === 'grounded') {
    if (!groundValid || !state.floor_verified) throw new Error('invalid_grounded_state');
    after.phase = 'retakeoff_ready';
    return emit('accepted_stationary_grounded_hold_verified');
  }
  if (state.phase === 'retakeoff_ready') {
    if (!takeoffEligible) return emit('retakeoff_ineligible_wait');
    after.phase = 'retakeoff'; after.reactive = { phase: 'takeoff', avoidance_turn: 0 };
    return emit('accepted_grounded_state_and_clearance_allow_retakeoff', 'TAKEOFF', .8);
  }
  if (state.phase === 'braking') {
    if (f.state !== 'flying') throw new Error('illegal_state_transition');
    if (landingEligible) { after.phase = 'landing'; return emit('accepted_braked_speed_altitude_and_clearance_allow_landing', 'LAND'); }
    const reactive = decideReactiveFlight({ phase: 'exploring', avoidance_turn: 0 }, o);
    return emit('braking_until_landing_preconditions_hold', 'HOLD', reactive.command.vertical);
  }
  const reactive = decideReactiveFlight(state.reactive, o);
  after.reactive = reactive.state_after;
  if (state.phase === 'ready') after.phase = 'takeoff';
  else if (state.phase === 'takeoff' && f.state === 'flying') after.phase = 'exploring';
  else if (state.phase === 'retakeoff' && f.state === 'flying') after.phase = 'exploring_again';
  if (after.phase === 'exploring' && reactive.boundary_response === 'released') {
    after.phase = 'braking';
    return emit('accepted_boundary_avoidance_recovery_arms_landing;begin_braking', 'HOLD', reactive.command.vertical, 0, 0, reactive);
  }
  return emit(reactive.reason, reactive.command.intent, reactive.command.vertical, reactive.command.forward, reactive.command.turn, reactive);
}

/** The published sustained-v2 override, shared without changing its comparisons or motor policy.
 * Abort braking for this interval, then resume the existing reactive hysteresis.
 * Historical resumed callers omit evidence; only the new controller records it.
 */
export function decideTouchAndGoWithLandingRecovery(state: TouchAndGoState, supplied: FlightArenaObservation, declaredInitialHeading?: number, recordRecovery = false): Decision {
  const o = validateFlightArenaObservation(supplied);
  let decision = decideTouchAndGo(state, o, declaredInitialHeading);
  const clearance = Math.min(o.forward_wall_clearance_units, o.left_wall_clearance_units, o.right_wall_clearance_units);
  const basePhase = decision.state_after.phase;
  const eligible = basePhase === 'braking' && clearance < TOUCH_AND_GO_CONFIG.minimum_horizontal_clearance;
  if (eligible) {
    const recovery = decideReactiveFlight({phase:'exploring',avoidance_turn:0},o);
    decision = {...decision,state_after:{...state,phase:'exploring',reactive:recovery.state_after},command:recovery.command,
      reason:'UNSAFE_LANDING_CLEARANCE_RETURN_TO_REACTIVE_EXPLORATION',reactive_decision:recovery};
  }
  if (recordRecovery) decision.recovery = {schema:'landing_clearance_recovery_interval_v1',observed_clearance:clearance,
    required_clearance:TOUCH_AND_GO_CONFIG.minimum_horizontal_clearance,eligible,active:eligible,base_phase_after:basePhase};
  return decision;
}

type Interval = { command_origin: 'ENGINEERING_TOUCH_AND_GO_V1'; observation_step: number; observation_time_s: number; observation: FlightArenaObservation; decision: Decision; accepted: ReturnType<FlightEngine['snapshot']> };
export class TouchAndGoSession {
  private readonly engine: FlightEngine;
  private controller = initialTouchAndGoState();
  private readonly intervals: Interval[] = [];
  private failure: string | null = null;
  private termination: 'SECOND_FLIGHT_CONFIRMED' | 'DURATION_LIMIT_REACHED' | 'FAILED' | null = null;
  status: ReactiveFlightStatus = 'ready';
  constructor(private readonly declaredInitialHeading?: number, private readonly landingRecovery = false) {
    if(declaredInitialHeading!==undefined&&!Number.isFinite(declaredInitialHeading))throw new Error('Invalid evaluation heading');
    const initial=initialFlightFrame();
    this.engine=new FlightEngine(createFlightTrial([],TOUCH_AND_GO_CONFIG.maximum_steps),FLIGHT_MODEL.arena,
      declaredInitialHeading===undefined?undefined:{position:initial.position,velocity:initial.velocity,heading:declaredInitialHeading});
  }
  get error() { return this.failure; }
  get stopStep() { return this.termination ? this.snapshot().step : TOUCH_AND_GO_CONFIG.maximum_steps; }
  get controllerPhase() { return this.controller.phase; }
  snapshot() { return this.engine.snapshot(); }
  latestInterval() { return structuredClone(this.intervals.at(-1) ?? null); }
  records() { return structuredClone(this.intervals); }
  start() { if (!['ready','paused'].includes(this.status)) throw new Error('Session cannot start'); this.status = 'running'; }
  pause() { if (this.status === 'running') this.status = 'paused'; }
  advance() {
    if (this.status !== 'running') throw new Error('Session is not running');
    try {
      const before = this.snapshot(), observation = observeFlightArena(before);
      const decision = this.landingRecovery
        ? decideTouchAndGoWithLandingRecovery(this.controller, observation, this.declaredInitialHeading, true)
        : decideTouchAndGo(this.controller, observation, this.declaredInitialHeading);
      const accepted = this.engine.advanceWithCommand(decision.command);
      this.intervals.push({ command_origin: 'ENGINEERING_TOUCH_AND_GO_V1', observation_step: before.step, observation_time_s: before.time, observation, decision, accepted });
      this.controller = decision.state_after;
      observeFlightArena(accepted); // finite, aligned and inside the actual conservative bounds
      if (accepted.events.some(e => e.kind === 'REJECTED_COMMAND')) throw new Error('invalid_command');
      if (accepted.contacts.some(c => c !== 'FLOOR') || (accepted.contacts.includes('FLOOR') && (before.state !== 'landing' || accepted.state !== 'grounded'))) throw new Error('invalid_contact');
      if (this.controller.phase === 'exploring_again' && before.state === 'flying' && accepted.state === 'flying') {
        this.termination = 'SECOND_FLIGHT_CONFIRMED'; this.status = 'completed';
      } else if (accepted.step >= TOUCH_AND_GO_CONFIG.maximum_steps) {
        this.failure = this.controller.phase === 'landing' ? 'landing_timeout' : this.controller.floor_verified ? 'retakeoff_not_reached' : 'landing_not_reached';
        this.termination = 'DURATION_LIMIT_REACHED'; this.status = 'failed';
      }
      return accepted;
    } catch (error) {
      this.failure = error instanceof Error ? error.message : String(error);
      this.termination = 'FAILED'; this.status = 'failed'; throw error;
    }
  }
  metrics() {
    const frames = this.engine.frames(), events = this.engine.events();
    const base = reactiveFlightMetrics(frames[0], frames, [], events);
    return { ...base,
      airborne_duration_s: frames.slice(0,-1).filter(f => f.state === 'flying' || f.state === 'landing').length * FLIGHT_MODEL.dt_s,
      steering_response_count: this.intervals.filter(i => ['started','redirected'].includes(i.decision.reactive_decision?.boundary_response ?? '')).length,
      minimum_observed_wall_clearance_units: this.intervals.length ? Math.min(...this.intervals.flatMap(i => [i.observation.forward_wall_clearance_units,i.observation.left_wall_clearance_units,i.observation.right_wall_clearance_units])) : null,
      transitions: events.filter(e => e.kind === 'TRANSITION'),
      landing_position: frames.find(f => f.state === 'grounded' && f.step > 0)?.position ?? null,
      second_takeoff_position: this.intervals.find(i => i.decision.command.intent === 'TAKEOFF' && i.observation_step > 0)?.observation.accepted.position ?? null,
    };
  }
  result() {
    if (!this.termination) throw new Error('Touch-and-go verification is not terminal');
    return structuredClone({ schema: this.landingRecovery?'touch_and_go_landing_recovery_result_v1':this.declaredInitialHeading===undefined?'neurofly_flight_touch_and_go_result_v1':'touch_and_go_initial_heading_evaluation_v1', configuration: this.declaredInitialHeading===undefined?TOUCH_AND_GO_CONFIG:{...TOUCH_AND_GO_CONFIG,schema:'touch_and_go_initial_heading_evaluation_config_v1',reactive_configuration:{...TOUCH_AND_GO_CONFIG.reactive_configuration,initial_state:{...initialFlightFrame(),heading:this.declaredInitialHeading}}},
      provenance: { controller_id: this.landingRecovery?'mixed_ground_flight_landing_recovery_v1':TOUCH_AND_GO_CONFIG.controller.id, command_origin: 'ENGINEERING_TOUCH_AND_GO_V1', plant: FLIGHT_MODEL.schema, source_glb_sha256: FLIGHT_MODEL.source_glb_sha256, randomness: 'NONE' },
      intervals: this.intervals, events: this.engine.events(), metrics: this.metrics(), termination: this.termination, failure: this.failure });
  }
}
export function runTouchAndGoVerification() {
  const session = new TouchAndGoSession(); session.start();
  while (session.status === 'running') { try { session.advance(); } catch { break; } }
  return session.result();
}
export const canonicalTouchAndGoResult = (result: ReturnType<TouchAndGoSession['result']>) => flightCanonical(result);
export const touchAndGoResultHash = (result: ReturnType<TouchAndGoSession['result']>) => flightHash(result);
