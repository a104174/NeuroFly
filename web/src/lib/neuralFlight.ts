/** Experimental horizontal feedback, reusing the pinned v2 observer and neural kernel.
 * This module owns no neural equations and no body integrator. */
import { InteractiveNeuralEngine, SOURCE_IDS, TARGET_IDS, BODY_DT, SUBSTEPS, type Plane } from './interactiveNeuralLocomotion';
import { NEURAL_LOCOMOTION_SHA256, type NeuralArtifact } from './neuralLocomotion';
import { FlightEngine, createFlightTrial, flightCanonical, flightHash, type FlightFrame, type FlightCommand } from './engineeringFlight';

export const NEURAL_FLIGHT_SCHEMA = 'experimental_neural_flight_steering_v9';
export const NEURAL_FLIGHT_LIMITATION = 'Experimental connectome-informed visual steering; airborne yaw mapping is an engineering hypothesis, not a validated physiological flight controller.';
export const NEURAL_FLIGHT_CONDITIONS = ['OFF', 'ON', 'ZERO', 'VISUAL_PERTURBATION'] as const;
export type NeuralFlightCondition = typeof NEURAL_FLIGHT_CONDITIONS[number];
export const NEURAL_YAW = Object.freeze({ identity: 'existing_planar_omega_to_normalized_flight_turn_v9', gain_rad_per_orientation_eq: 2.5, omega_bound_rad_s: .5, flight_turn_rate_rad_s: .8, normalization_horizon_ms: 50, baseline: 0, sign: 'DN_RIGHT_MINUS_LEFT_POSITIVE_TOWARD_PLUS_X', combination: 'CLAMP_ENGINEERING_PLUS_NEURAL_MINUS_ONE_PLUS_ONE' });
export function projectFlightYaw(increment: number, engineeringTurn: number, condition: NeuralFlightCondition) {
  if (!Number.isFinite(increment) || !Number.isFinite(engineeringTurn) || Math.abs(engineeringTurn) > 1 || !NEURAL_FLIGHT_CONDITIONS.includes(condition)) throw new Error('Invalid neural yaw projection input');
  const rawOmega = NEURAL_YAW.gain_rad_per_orientation_eq * increment / BODY_DT;
  if (!Number.isFinite(rawOmega)) throw new Error('Non-finite projected neural yaw');
  const omega = Math.max(-NEURAL_YAW.omega_bound_rad_s, Math.min(NEURAL_YAW.omega_bound_rad_s, rawOmega));
  const potentialTurn = omega / NEURAL_YAW.flight_turn_rate_rad_s;
  const neuralTurn = condition === 'OFF' || condition === 'ZERO' ? 0 : potentialTurn;
  const rawTurn = engineeringTurn + neuralTurn, appliedTurn = Math.max(-1, Math.min(1, rawTurn));
  return { rawOmega, omega, potentialTurn, neuralTurn, appliedTurn, projectionClamped: rawOmega !== omega, combinedClamped: rawTurn !== appliedTurn };
}

/** Borrow only the actual existing observation/calculateBoundary methods. The inherited
 * private HS/DNp15 state persists. Planar velocity/propulsion/recovery are never run. */
export class FlightPoseNeuralAdapter extends InteractiveNeuralEngine {
  private expectedBoundary = 0;
  constructor(authority: NeuralArtifact, plane: Plane = .4) { super(authority, 'output_disabled', plane); }
  advance(): never { throw new Error('Use an accepted external pose boundary; planar integration is disabled'); }
  protected velocity(): [number, number, number] { return [0, 0, 0]; }
  observeAndAdvance(current: FlightFrame, previous?: FlightFrame) {
    if (current.step !== this.expectedBoundary || current.step >= 600 || current.time !== current.step * BODY_DT ||
        ![...current.position, current.heading].every(Number.isFinite) ||
        (current.step === 0 ? previous !== undefined : !previous || previous.step !== current.step - 1 || previous.time !== previous.step * BODY_DT || ![...previous.position, previous.heading].every(Number.isFinite))) throw new Error('Invalid/noncausal flight observation boundary');
    this.n = current.step;
    this.pose = { position: [...current.position], heading: current.heading };
    this.previous = previous ? { position: [...previous.position], heading: previous.heading } : null;
    const boundary = this.calculateBoundary(true), after = this.snapshot();
    this.expectedBoundary++;
    return { observation: boundary.sensory_summary, before: boundary.neural_summary!, after: { hs: after.hs, dn: after.dn, substeps: after.substeps } };
  }
}
export function neuralFlightConfig(authority: NeuralArtifact, condition: NeuralFlightCondition) {
  if (!NEURAL_FLIGHT_CONDITIONS.includes(condition)) throw new Error('Unsupported neural flight condition');
  // The inherited constructor verifies dataset, neuron ordering, six directed contact
  // counts, model identities, parameters and source pins before any execution.
  new FlightPoseNeuralAdapter(authority);
  return {
    schema: NEURAL_FLIGHT_SCHEMA, classification: 'EXPERIMENTAL_CONNECTOME_INFORMED_HORIZONTAL_FLIGHT_STEERING', condition,
    evidence: { classification: 'MALECNS_CONNECTOME_EVIDENCE', dataset: authority.config.dataset, dataset_uuid: authority.config.dataset_uuid, source_ids: [...SOURCE_IDS], target_ids: [...TARGET_IDS], structural_routes: structuredClone((authority.config.sources.neural as unknown as { selected_routes: unknown[] }).selected_routes) },
    neural: { classification: 'MODELED_NEURAL_DYNAMICS', source_artifact_id: authority.artifact_id, source_raw_sha256: NEURAL_LOCOMOTION_SHA256, source_config_sha256: authority.config_sha256, source_sha256: { ...authority.config.source_sha256 }, model: structuredClone(authority.config.sources.neural), initial_hs: Array(6).fill(0) as number[], initial_dn: Array(2).fill(0) as number[] },
    visual: { identity: 'ENGINEERING_HORIZONTAL_VISUAL_PROJECTION_V9', encoder: 'EXISTING_INTERACTIVE_NEURAL_V2_OBSERVATION', source_sha256: authority.config.source_sha256.observation, landmark_x: [.6, -.6], plane_z: (condition === 'VISUAL_PERTURBATION' ? -.4 : .4) as Plane, altitude: 'EXCLUDED_XZ_AND_UNWRAPPED_YAW_ONLY', units: 'ONE_PRESENTATION_UNIT_EQUALS_ONE_OBSERVER_WORLD_EQ', channels: 'X_PLUS_0_6_RIGHT_X_MINUS_0_6_LEFT', perturbation: condition === 'VISUAL_PERTURBATION' ? 'EXISTING_V1_VISUAL_PLANE_INTERVENTION_INITIAL_WORLD' : 'NONE' },
    projection: { classification: 'ENGINEERING_FLIGHT_CONTROL_PROJECTION', ...NEURAL_YAW, enabled: condition !== 'OFF', influence: condition === 'ZERO' ? 0 : 1 },
    trial: createFlightTrial(), timing: { body_dt_s: BODY_DT, neural_dt_ms: .1, substeps: SUBSTEPS, observation: 'PREVIOUS_COMPLETED_BODY_INTERVAL_I_MINUS_ONE_TO_I', neural: 'OLD_STATE_SIMULTANEOUS_HELD_OBSERVATION_OVER_I_TO_I_PLUS_ONE', readout: 'INTEGRATED_OLD_STATE_READOUT_OVER_200_SUBSTEPS_APPLIES_TO_BODY_INTERVAL_I', initial_observation: 'ZERO_NO_COMPLETED_MOTION' }, artifact_precision: 'NEURAL_INTERVALS_ROUND_1E_MINUS_10_BODY_AND_CONFIG_EXACT', randomness: 'NONE', limitation: NEURAL_FLIGHT_LIMITATION,
  };
}
export type NeuralFlightConfig = ReturnType<typeof neuralFlightConfig>;
export type NeuralFlightInterval = ReturnType<FlightPoseNeuralAdapter['observeAndAdvance']> & {
  step: number; time: number; available_time: number; engineering: FlightCommand;
  yaw: ReturnType<typeof projectFlightYaw>; heading_delta: number;
};
export class NeuralFlightEngine {
  readonly config: NeuralFlightConfig;
  private readonly flight: FlightEngine;
  private readonly neural: FlightPoseNeuralAdapter;
  private readonly intervals: NeuralFlightInterval[] = [];
  constructor(authority: NeuralArtifact, condition: NeuralFlightCondition, config?: NeuralFlightConfig) {
    this.config = neuralFlightConfig(authority, condition);
    if (config && flightCanonical(config) !== flightCanonical(this.config)) throw new Error('Neural flight source/model/configuration mismatch');
    this.flight = new FlightEngine(this.config.trial);
    this.neural = new FlightPoseNeuralAdapter(authority, this.config.visual.plane_z);
  }
  get stopStep() { return this.config.trial.stop_step; }
  snapshot() { return this.flight.snapshot(); }
  frame(step: number) { return this.flight.frame(step); }
  frames() { return this.flight.frames(); }
  interval(step: number) { if (!Number.isInteger(step) || step < 0 || step >= this.intervals.length) throw new Error('Neural interval outside accepted history'); return structuredClone(this.intervals[step]); }
  records(stop = this.intervals.length) { if (!Number.isInteger(stop) || stop < 0 || stop > this.intervals.length) throw new Error('Invalid neural history prefix'); return structuredClone(this.intervals.slice(0, stop)); }
  advance() {
    const current = this.flight.snapshot();
    if (current.step >= this.stopStep) throw new Error('Neural flight completed');
    const model = this.neural.observeAndAdvance(current, current.step ? this.flight.frame(current.step - 1) : undefined);
    const held = this.config.trial.commands.findLast(c => c.step <= current.step);
    const engineering: FlightCommand = held ? { ...held, intent: held.step === current.step ? held.intent : 'HOLD' } : { id: 'initial-held-zero', step: 0, forward: 0, turn: 0, vertical: 0, intent: 'HOLD' };
    const yaw = projectFlightYaw(model.before.orientation_increment_eq!, engineering.turn, this.config.condition);
    const next = yaw.appliedTurn === engineering.turn ? this.flight.advance() : this.flight.advanceWithTurn(yaw.appliedTurn);
    this.intervals.push({ step: current.step, time: current.time, available_time: next.time, ...model, engineering, yaw, heading_delta: next.heading - current.heading });
    return next;
  }
}
export function reconstructNeuralFlight(authority: NeuralArtifact, config: NeuralFlightConfig, stop = config.trial.stop_step) {
  if (!Number.isInteger(stop) || stop < 0 || stop > 600) throw new Error('Unsupported neural flight replay boundary');
  const engine = new NeuralFlightEngine(authority, config.condition, config);
  while (engine.snapshot().step < stop) engine.advance();
  return engine;
}
/** New v9 artifact convention only. The live kernel remains double precision;
 * interval telemetry rounds to 1e-10 (stricter than the existing 1e-8 parity gate).
 * Config and legacy body records remain exact. This avoids platform math noise
 * changing replay identity; inputs still reconstruct and verify every output. */
function portableIntervals(records: NeuralFlightInterval[]): NeuralFlightInterval[] {
  return JSON.parse(JSON.stringify(records, (_key, value) => {
    if (typeof value !== 'number') return value;
    if (!Number.isFinite(value)) throw new Error('Non-finite neural telemetry');
    return Math.round(value * 1e10) / 1e10;
  }));
}
export async function exportNeuralFlight(engine: NeuralFlightEngine, stop = engine.snapshot().step) {
  if (!Number.isInteger(stop) || stop < 0 || stop > engine.snapshot().step) throw new Error('Export outside accepted neural flight history');
  const result = { frames: engine.frames().slice(0, stop + 1), intervals: portableIntervals(engine.records(stop)), termination: stop === engine.stopStep ? 'DURATION_COMPLETED' : 'RECORDED_PREFIX' };
  const input = { config: engine.config, stop_step: stop }, input_sha256 = await flightHash(input), result_sha256 = await flightHash(result);
  return { schema: NEURAL_FLIGHT_SCHEMA, input, result, input_sha256, result_sha256, artifact_id: await flightHash({ input_sha256, result_sha256 }) };
}
export type NeuralFlightRun = Awaited<ReturnType<typeof exportNeuralFlight>>;
export async function importNeuralFlight(authority: NeuralArtifact, value: unknown) {
  const run = value as NeuralFlightRun;
  if (!run || run.schema !== NEURAL_FLIGHT_SCHEMA || !run.input || !run.result || !Array.isArray(run.result.frames) || run.result.frames.length > 601) throw new Error('Invalid neural flight artifact');
  const engine = reconstructNeuralFlight(authority, run.input.config, run.input.stop_step), expected = await exportNeuralFlight(engine);
  if (flightCanonical(run) !== flightCanonical(expected)) throw new Error('Neural flight semantic replay/identity mismatch');
  return engine;
}
const STORAGE_KEY = 'neurofly.experimental-neural-flight.v9';
export interface NeuralFlightStorage { getItem(key: string): string | null; setItem(key: string, value: string): void }
/** One compact snapshot per fixed condition. Never touches scientific or v8.1 stores. */
export async function saveNeuralFlight(storage: NeuralFlightStorage, engine: NeuralFlightEngine, stop = engine.snapshot().step) {
  if (stop !== engine.stopStep) throw new Error('Only completed neural flight runs can be saved locally; export a prefix instead');
  const run = await exportNeuralFlight(engine, stop), prior = storage.getItem(STORAGE_KEY);
  if (prior && prior.length > 500_000) throw new Error('Oversized neural flight library retained without overwriting');
  const data = prior ? JSON.parse(prior) : { schema: 'neural_flight_library_v9', entries: {} };
  if (data.schema !== 'neural_flight_library_v9' || !data.entries || Object.keys(data).sort().join(',') !== 'entries,schema' || Object.keys(data.entries).some(k => !NEURAL_FLIGHT_CONDITIONS.includes(k as NeuralFlightCondition))) throw new Error('Invalid neural flight library retained without overwriting');
  const entry = { input: run.input, input_sha256: run.input_sha256, result_sha256: run.result_sha256 };
  if (data.entries[engine.config.condition] && flightCanonical(data.entries[engine.config.condition]) !== flightCanonical(entry)) throw new Error('Existing condition snapshot differs; retained without overwriting');
  data.entries[engine.config.condition] = entry;
  try { storage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch { throw new Error('Unable to save neural flight snapshot; storage unavailable or quota exceeded'); }
}
export async function openNeuralFlight(storage: NeuralFlightStorage, authority: NeuralArtifact, condition: NeuralFlightCondition) {
  const raw = storage.getItem(STORAGE_KEY);
  if (!raw || raw.length > 500_000) throw new Error('Missing/oversized neural flight library');
  const data = JSON.parse(raw), entry = data.schema === 'neural_flight_library_v9' && data.entries?.[condition];
  if (!entry || entry.input.config.condition !== condition) throw new Error('No saved snapshot for this neural flight condition');
  const engine = reconstructNeuralFlight(authority, entry.input.config, entry.input.stop_step), run = await exportNeuralFlight(engine);
  if (flightCanonical(entry) !== flightCanonical({ input: run.input, input_sha256: run.input_sha256, result_sha256: run.result_sha256 })) throw new Error('Saved neural flight inputs/results contradict reconstructed dynamics');
  return engine;
}
