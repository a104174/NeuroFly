/** Bounded live presentation of the existing HS/DNp15 and arena equations. */
import { ContinuousNavigationEngine, type NavigationFrame, type NavigationSnapshot } from './continuousArenaNavigation';
import { BODY_DT, type Plane } from './interactiveNeuralLocomotion';
import { locomotionBounds } from './experimentalLocomotion';
import { NEURAL_LOCOMOTION_SHA256, type NeuralArtifact } from './neuralLocomotion';
import { EXPLORATION_POLICY, explorationCommand, explorationState, forwardClearance, type ExplorationMode, type ExplorationState } from './engineeringExploration';

export type LiveStatus = 'ready' | 'running' | 'paused' | 'stopped' | 'error';
export type LiveControlTrace = { mode: ExplorationMode; state: ExplorationState | 'baseline'; clearance_units: number; baseline_speed_units_s: number; commanded_speed_units_s: number; actual_speed_units_s: number; previous_state: ExplorationState | 'baseline'; transition_trigger: string; contact: string | null };
export type LiveSample = { interval: NavigationFrame; accepted: NavigationSnapshot; engineering: LiveControlTrace; source: { authority_artifact_id: string; dataset_uuid: string; config_sha256: string; raw_sha256: string } };
export type LiveEvent =
  | { tick: number; time: number; kind: 'BEHAVIOR'; previous_state: ExplorationState | 'baseline'; new_state: ExplorationState | 'baseline'; trigger: string; observation: { forward_clearance_units: number; contact: string | null }; threshold_units: number | null; commanded_speed_units_s: number; controller_id: string; detail: string }
  | { tick: number; time: number; kind: 'CONTACT' | 'RECOVERY' | 'ERROR'; detail: string };
export type LiveInitialPose = { position: [number, number, number]; heading: number };

type LiveControlObservation = { mode: ExplorationMode; clearance_units: number; baseline_speed_units_s: number; commanded_speed_units_s: number; contact: string | null };

export class Ring<T> {
  private readonly data: (T | undefined)[];
  private next = 0;
  private length = 0;
  constructor(readonly capacity: number) {
    if (!Number.isInteger(capacity) || capacity < 1 || capacity > 1501) throw new Error('Invalid live history capacity');
    this.data = new Array(capacity);
  }
  push(value: T) { this.data[this.next] = value; this.next = (this.next + 1) % this.capacity; this.length = Math.min(this.length + 1, this.capacity); }
  values(): T[] { return Array.from({ length: this.length }, (_, i) => this.data[(this.next - this.length + i + this.capacity) % this.capacity]!); }
  get size() { return this.length; }
}

/** No finite v3 export may represent this session's rolling history. */
class LiveEngine extends ContinuousNavigationEngine {
  private control!: LiveControlObservation;
  private acceptedIntervalControl!: LiveControlObservation;
  constructor(authority: NeuralArtifact, enabled: boolean, readonly mode: ExplorationMode, initial?: LiveInitialPose) {
    super(authority, enabled ? 'neural' : 'output_disabled', .4, initial);
    this.lastStep = Infinity;
    this.retainHistory = false;
    this.path.length = 0;
  }
  protected velocity(): [number, number, number] {
    const legacy = super.velocity();
    const clearance = forwardClearance(this.pose.position, this.pose.heading, this.limits);
    const command = this.mode === 'baseline_v10_5b' ? EXPLORATION_POLICY.baseline_speed_units_s : explorationCommand(clearance);
    this.control = { mode: this.mode, clearance_units: clearance, baseline_speed_units_s: EXPLORATION_POLICY.baseline_speed_units_s, commanded_speed_units_s: command, contact: this.contact };
    if (this.mode === 'baseline_v10_5b' || this.contact) return legacy;
    return [command * Math.sin(this.pose.heading), 0, command * Math.cos(this.pose.heading)];
  }
  protected calculateBoundary(outgoing: boolean): NavigationFrame {
    const frame = super.calculateBoundary(outgoing);
    if (!outgoing || !this.control) return frame;
    this.acceptedIntervalControl = structuredClone(this.control);
    // Historical baseline frames stay byte-for-byte shaped as before. In the
    // exploration mode this established field reports the applied command.
    return this.mode === 'baseline_v10_5b' ? frame : { ...frame, propulsion_model_value: this.control.commanded_speed_units_s };
  }
  intervalControl() { if (!this.acceptedIntervalControl) throw new Error('Engineering interval telemetry unavailable'); return structuredClone(this.acceptedIntervalControl); }
  requestPlane(_plane: Plane): never { throw new Error('Live stimulus interventions are not supported'); }
  navigationLog(): never { throw new Error('Live rolling history is not a complete v3 recording'); }
  async exportNavigation(): Promise<never> { throw new Error('Live rolling history cannot be exported as a complete recording'); }
}

export class LiveGroundSession {
  readonly config: { schema: 'live_ground_session_v1'; session_id: string; seed: null; random_policy: 'NONE'; mode: ExplorationMode; initial_pose: { position: [number, number, number]; heading: number }; neural_influence: boolean; body_dt_s: number; neural_dt_ms: number; source_artifact_id: string; source_config_sha256: string; source_raw_sha256: string; arena_source_artifact_id: string; source_sha256: Record<string, string>; boundary_policy: string; propulsion: string };
  readonly trajectory: Ring<[number, number, number]>;
  readonly telemetry: Ring<LiveSample>;
  readonly events: Ring<LiveEvent>;
  private engine: LiveEngine | null;
  private current: NavigationSnapshot;
  private readonly limits: readonly number[];
  status: LiveStatus = 'ready';
  error: string | null = null;

  private previousBehavior: ExplorationState | 'baseline' = 'baseline';
  constructor(private readonly authority: NeuralArtifact, readonly enabled: boolean, sessionId: string, capacities = { trajectory: 512, telemetry: 256, events: 128 }, initial?: LiveInitialPose, readonly mode: ExplorationMode = 'baseline_v10_5b') {
    if (!sessionId) throw new Error('A session identity is required');
    if (mode !== 'baseline_v10_5b' && mode !== 'engineering_exploration_v1') throw new Error('Invalid live locomotion mode');
    this.engine = new LiveEngine(authority, enabled, mode, initial);
    this.current = this.engine.snapshot();
    this.limits = locomotionBounds(authority.config.body);
    if (mode !== 'baseline_v10_5b') this.previousBehavior = forwardClearance(this.current.position, this.current.heading, this.limits) < EXPLORATION_POLICY.slow_clearance_units ? 'approaching_boundary' : 'cruising';
    this.trajectory = new Ring(capacities.trajectory); this.telemetry = new Ring(capacities.telemetry); this.events = new Ring(capacities.events);
    this.trajectory.push([...this.current.position]);
    this.config = { schema: 'live_ground_session_v1', session_id: sessionId, seed: null, random_policy: 'NONE', mode, initial_pose: { position: [...this.current.position], heading: this.current.heading }, neural_influence: enabled, body_dt_s: BODY_DT, neural_dt_ms: .1, source_artifact_id: authority.artifact_id, source_config_sha256: authority.config_sha256, source_raw_sha256: NEURAL_LOCOMOTION_SHA256, arena_source_artifact_id: authority.config.v0_artifact_id, source_sha256: { ...authority.config.source_sha256 }, boundary_policy: 'GEOMETRIC_INWARD_NORMAL_V1', propulsion: mode === 'baseline_v10_5b' ? 'ENGINEERING_CONSTANT_0.18' : `ENGINEERING_CLEARANCE_SPEED_${EXPLORATION_POLICY.id}` };
  }
  snapshot() { return structuredClone(this.current); }
  start() { if (!this.engine || !['ready', 'paused'].includes(this.status)) throw new Error('Session cannot start'); this.status = 'running'; }
  pause() { if (this.status === 'running') this.status = 'paused'; }
  stop() { this.engine = null; this.status = 'stopped'; }
  /** Reset starts a new session with the same scientific initial conditions. */
  reset(sessionId = this.config.session_id) { this.stop(); return new LiveGroundSession(this.authority, this.enabled, sessionId, { trajectory: this.trajectory.capacity, telemetry: this.telemetry.capacity, events: this.events.capacity }, this.config.initial_pose, this.mode); }
  advance(): LiveSample {
    if (this.status !== 'running' || !this.engine) throw new Error('Session is not running');
    try {
      const before = this.current, interval = this.engine.advance(), accepted = this.engine.snapshot(), observation = this.engine.intervalControl();
      const previousState = this.previousBehavior;
      const state: ExplorationState | 'baseline' = this.mode === 'baseline_v10_5b' ? 'baseline' : explorationState(observation.clearance_units, interval.contact, previousState === 'baseline' ? 'cruising' : previousState);
      const transitionTrigger = state === previousState ? 'none' : state === 'boundary_contact' ? `contact:${interval.contact ?? accepted.contact ?? 'wall'}` : state === 'recovering' ? 'contact_cleared' : state === 'approaching_boundary' ? `forward_clearance_below_${EXPLORATION_POLICY.slow_clearance_units}` : 'forward_clearance_recovered';
      const actualSpeed = Math.hypot(accepted.position[0] - before.position[0], accepted.position[2] - before.position[2]) / BODY_DT;
      const engineering: LiveControlTrace = { ...observation, state, previous_state: previousState, transition_trigger: transitionTrigger, contact: interval.contact ?? accepted.contact, actual_speed_units_s: actualSpeed };
      const sensory = interval.sensory_summary;
      const numbers = [...accepted.position, accepted.heading, accepted.time, accepted.omega, ...accepted.hs, ...accepted.dn, ...interval.linear_velocity, interval.angular_velocity, interval.boundary_summary.neural_omega, interval.boundary_summary.omega, engineering.clearance_units, engineering.baseline_speed_units_s, engineering.commanded_speed_units_s, engineering.actual_speed_units_s, ...(sensory ? [sensory.right, sensory.left, ...sensory.raw_normalized, ...sensory.bearing_shift_rad] : [])];
      if (!numbers.every(Number.isFinite) || accepted.step !== before.step + 1 || accepted.time !== accepted.step * BODY_DT || interval.step !== before.step || accepted.substeps !== before.substeps + 200 || accepted.position[1] !== this.config.initial_pose.position[1] || [...accepted.hs, ...accepted.dn].some(value => Math.abs(value) > 1) || Math.abs(accepted.position[0]) > this.limits[0] + 1e-12 || Math.abs(accepted.position[2]) > this.limits[1] + 1e-12 || Math.abs(interval.boundary_summary.neural_omega) > .5 + 1e-12 || Math.abs(interval.boundary_summary.omega) > 1.2 + 1e-12 || Math.abs(interval.angular_velocity - interval.boundary_summary.neural_omega - interval.boundary_summary.omega) > 1e-12 || !Number.isSafeInteger(accepted.step)) throw new Error('Invalid live neural or body state');
      if (engineering.state !== previousState) {
        const threshold = engineering.state === 'approaching_boundary' || engineering.state === 'cruising' ? EXPLORATION_POLICY.slow_clearance_units : null;
        this.events.push({ tick: accepted.step, time: accepted.time, kind: 'BEHAVIOR', previous_state: previousState, new_state: engineering.state, trigger: engineering.transition_trigger, observation: { forward_clearance_units: engineering.clearance_units, contact: engineering.contact }, threshold_units: threshold, commanded_speed_units_s: engineering.commanded_speed_units_s, controller_id: this.mode === 'baseline_v10_5b' ? this.mode : EXPLORATION_POLICY.id, detail: `${previousState}->${engineering.state}; clearance=${engineering.clearance_units.toFixed(6)}; trigger=${engineering.transition_trigger}` });
      }
      this.previousBehavior = engineering.state;
      const sample = { interval, accepted, engineering, source: { authority_artifact_id: this.config.source_artifact_id, dataset_uuid: this.authority.config.dataset_uuid, config_sha256: this.config.source_config_sha256, raw_sha256: this.config.source_raw_sha256 } };
      if (!before.contact && accepted.contact) this.events.push({ tick: accepted.step, time: accepted.time, kind: 'CONTACT', detail: accepted.contact });
      if (before.contact && !accepted.contact) this.events.push({ tick: accepted.step, time: accepted.time, kind: 'RECOVERY', detail: before.contact });
      this.current = accepted; this.telemetry.push(sample); this.trajectory.push([...accepted.position]);
      return sample;
    } catch (error) {
      this.error = error instanceof Error ? error.message : String(error); this.status = 'error'; this.engine = null;
      this.events.push({ tick: this.current.step, time: this.current.time, kind: 'ERROR', detail: this.error });
      throw error;
    }
  }
}

/** Wall time schedules fixed intervals; excess time is dropped rather than simulated. */
export class LiveClock {
  private remainder = 0;
  reset() { this.remainder = 0; }
  advance(session: LiveGroundSession, elapsedMs: number, onStep?: (sample: LiveSample) => void) {
    if (!Number.isFinite(elapsedMs) || elapsedMs < 0) throw new Error('Invalid live clock interval');
    if (session.status !== 'running') { this.reset(); return { steps: 0, limited: false }; }
    this.remainder += elapsedMs; let steps = 0;
    while (this.remainder >= 20 && steps < 5) { const sample = session.advance(); onStep?.(sample); this.remainder -= 20; steps++; }
    const limited = this.remainder >= 20; if (limited) this.remainder = 0;
    return { steps, limited };
  }
}

export function pauseForVisibility(session: LiveGroundSession, hidden: boolean) {
  if (hidden && session.status === 'running') { session.pause(); return true; }
  return false;
}
