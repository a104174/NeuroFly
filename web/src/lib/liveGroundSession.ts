/** Bounded live presentation of the existing HS/DNp15 and arena equations. */
import { ContinuousNavigationEngine, type NavigationFrame, type NavigationSnapshot } from './continuousArenaNavigation';
import { BODY_DT, type Plane } from './interactiveNeuralLocomotion';
import { locomotionBounds } from './experimentalLocomotion';
import { NEURAL_LOCOMOTION_SHA256, type NeuralArtifact } from './neuralLocomotion';

export type LiveStatus = 'ready' | 'running' | 'paused' | 'stopped' | 'error';
export type LiveSample = { interval: NavigationFrame; accepted: NavigationSnapshot };
export type LiveEvent = { tick: number; time: number; kind: 'CONTACT' | 'RECOVERY' | 'ERROR'; detail: string };
export type LiveInitialPose = { position: [number, number, number]; heading: number };

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
  constructor(authority: NeuralArtifact, enabled: boolean, initial?: LiveInitialPose) {
    super(authority, enabled ? 'neural' : 'output_disabled', .4, initial);
    this.lastStep = Infinity;
    this.retainHistory = false;
    this.path.length = 0;
  }
  requestPlane(_plane: Plane): never { throw new Error('Live stimulus interventions are not supported'); }
  navigationLog(): never { throw new Error('Live rolling history is not a complete v3 recording'); }
  async exportNavigation(): Promise<never> { throw new Error('Live rolling history cannot be exported as a complete recording'); }
}

export class LiveGroundSession {
  readonly config: { schema: 'live_ground_session_v1'; session_id: string; seed: null; random_policy: 'NONE'; initial_pose: { position: [number, number, number]; heading: number }; neural_influence: boolean; body_dt_s: number; neural_dt_ms: number; source_artifact_id: string; source_config_sha256: string; source_raw_sha256: string; arena_source_artifact_id: string; source_sha256: Record<string, string>; boundary_policy: string; propulsion: string };
  readonly trajectory: Ring<[number, number, number]>;
  readonly telemetry: Ring<LiveSample>;
  readonly events: Ring<LiveEvent>;
  private engine: LiveEngine | null;
  private current: NavigationSnapshot;
  private readonly limits: readonly number[];
  status: LiveStatus = 'ready';
  error: string | null = null;

  constructor(private readonly authority: NeuralArtifact, readonly enabled: boolean, sessionId: string, capacities = { trajectory: 512, telemetry: 256, events: 128 }, initial?: LiveInitialPose) {
    if (!sessionId) throw new Error('A session identity is required');
    this.engine = new LiveEngine(authority, enabled, initial);
    this.current = this.engine.snapshot();
    this.limits = locomotionBounds(authority.config.body);
    this.trajectory = new Ring(capacities.trajectory); this.telemetry = new Ring(capacities.telemetry); this.events = new Ring(capacities.events);
    this.trajectory.push([...this.current.position]);
    this.config = { schema: 'live_ground_session_v1', session_id: sessionId, seed: null, random_policy: 'NONE', initial_pose: { position: [...this.current.position], heading: this.current.heading }, neural_influence: enabled, body_dt_s: BODY_DT, neural_dt_ms: .1, source_artifact_id: authority.artifact_id, source_config_sha256: authority.config_sha256, source_raw_sha256: NEURAL_LOCOMOTION_SHA256, arena_source_artifact_id: authority.config.v0_artifact_id, source_sha256: { ...authority.config.source_sha256 }, boundary_policy: 'GEOMETRIC_INWARD_NORMAL_V1', propulsion: 'ENGINEERING_CONSTANT_0.18' };
  }
  snapshot() { return structuredClone(this.current); }
  start() { if (!this.engine || !['ready', 'paused'].includes(this.status)) throw new Error('Session cannot start'); this.status = 'running'; }
  pause() { if (this.status === 'running') this.status = 'paused'; }
  stop() { this.engine = null; this.status = 'stopped'; }
  /** Reset starts a new session with the same scientific initial conditions. */
  reset(sessionId = this.config.session_id) { this.stop(); return new LiveGroundSession(this.authority, this.enabled, sessionId, { trajectory: this.trajectory.capacity, telemetry: this.telemetry.capacity, events: this.events.capacity }, this.config.initial_pose); }
  advance(): LiveSample {
    if (this.status !== 'running' || !this.engine) throw new Error('Session is not running');
    try {
      const before = this.current, interval = this.engine.advance(), accepted = this.engine.snapshot();
      const sensory = interval.sensory_summary;
      const numbers = [...accepted.position, accepted.heading, accepted.time, accepted.omega, ...accepted.hs, ...accepted.dn, ...interval.linear_velocity, interval.angular_velocity, interval.boundary_summary.neural_omega, interval.boundary_summary.omega, ...(sensory ? [sensory.right, sensory.left, ...sensory.raw_normalized, ...sensory.bearing_shift_rad] : [])];
      if (!numbers.every(Number.isFinite) || accepted.step !== before.step + 1 || accepted.time !== accepted.step * BODY_DT || interval.step !== before.step || accepted.substeps !== before.substeps + 200 || accepted.position[1] !== this.config.initial_pose.position[1] || [...accepted.hs, ...accepted.dn].some(value => Math.abs(value) > 1) || Math.abs(accepted.position[0]) > this.limits[0] + 1e-12 || Math.abs(accepted.position[2]) > this.limits[1] + 1e-12 || Math.abs(interval.boundary_summary.neural_omega) > .5 + 1e-12 || Math.abs(interval.boundary_summary.omega) > 1.2 + 1e-12 || Math.abs(interval.angular_velocity - interval.boundary_summary.neural_omega - interval.boundary_summary.omega) > 1e-12 || !Number.isSafeInteger(accepted.step)) throw new Error('Invalid live neural or body state');
      const sample = { interval, accepted };
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
