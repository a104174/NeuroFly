/** Offline controlled model experiment. No observer, neural or plant equations. */
import { BODY_DT, SUBSTEPS, type Plane } from './interactiveNeuralLocomotion';
import { type NeuralArtifact } from './neuralLocomotion';
import { createFlightTrial, FlightEngine, flightCanonical, flightHash, type FlightCommand, type FlightFrame } from './engineeringFlight';
import { FlightPoseNeuralAdapter, neuralFlightConfig, projectFlightYaw, type NeuralFlightInterval } from './neuralFlight';

export const CONTROLLED_SCHEMA = 'controlled_neural_steering_experiment_v9_3_phase1';
export type Visual = 'V0' | 'V1';
export type Mode = 'OFF' | 'ZERO_PROJECTION' | 'ON';
export function conditionSpecs() {
  return [
    { id: 'E1', visual: 'V0', mode: 'OFF' },
    { id: 'E2', visual: 'V0', mode: 'ZERO_PROJECTION' },
    { id: 'E3', visual: 'V0', mode: 'ON' },
    { id: 'E4', visual: 'V1', mode: 'OFF' },
    { id: 'E5', visual: 'V1', mode: 'ZERO_PROJECTION' },
    { id: 'E6', visual: 'V1', mode: 'ON' },
  ] as const;
}
export function visualScene(visual: Visual) {
  if (visual !== 'V0' && visual !== 'V1') throw new Error('Unsupported visual transformation');
  const plane: Plane = visual === 'V0' ? .4 : -.4;
  return { identity: `CONTROLLED_VISUAL_MIRROR_Z_${visual}_V9_3`, plane_z: plane,
    landmarks: [{ side: 'R', x: .6, z: plane }, { side: 'L', x: -.6, z: plane }],
    transformation: visual === 'V0' ? 'IDENTITY' : 'SCENE_ONLY_X_UNCHANGED_Z_NEGATED',
    body_pose: 'UNCHANGED', collision_geometry: 'UNCHANGED', altitude: 'EXCLUDED' };
}
export function experimentProtocol(authority: NeuralArtifact) {
  return { schema: CONTROLLED_SCHEMA, source_revision: 'aad4ea60251c1b811046e18834ef56819835bcb6',
    classification: 'CONTROLLED_VISUAL_MIRROR', source: 'EXISTING_V9_VISUAL_PLANE_INTERVENTION_NOT_G3',
    reference: neuralFlightConfig(authority, 'ON'), visuals: [visualScene('V0'), visualScene('V1')],
    conditions: conditionSpecs(), timebase: { duration_s: 12, intervals: 600, boundaries: 601, body_dt_s: BODY_DT, neural_dt_ms: .1, substeps: SUBSTEPS },
    hypothesis_gates: { H0_max_sensory_difference: 1e-10, H1_max_symmetry_residual: 1e-12, H2_neural_difference: 1e-10, H3_final_heading_interaction_rad: 1e-10, H4_body_equality: 'EXACT' },
    metrics: { primary: 'UNWRAPPED_FINAL_HEADING', interaction: '(E6-E4)-(E3-E1)', divergence_threshold: 1e-10,
      secondary: ['FINAL_XYZ_DISTANCE', 'INTEGRATED_ABSOLUTE_APPLIED_NEURAL_OMEGA', 'MEAN_SIGNED_NEURAL_TURN', 'SATURATION', 'CONTACT_EVENTS'] },
    precision: 'V9_NEURAL_TELEMETRY_1E_MINUS_10_BODY_EXACT', seed: null, randomness: 'NONE',
    limitation: 'Internal model validation only; no G3 stimulus reproduction, calcium equivalence or physiological yaw calibration.' };
}
const roundNeural = (n: number) => Math.round(n * 1e10) / 1e10;
function portable<T>(value: T): T {
  return JSON.parse(JSON.stringify(value, (_key, item) => {
    if (typeof item !== 'number') return item;
    if (!Number.isFinite(item)) throw new Error('Non-finite controlled experiment telemetry');
    return roundNeural(item);
  }));
}
function commandAt(trial: ReturnType<typeof createFlightTrial>, step: number): FlightCommand {
  const held = trial.commands.findLast(c => c.step <= step);
  return held ? { ...held, intent: held.step === step ? held.intent : 'HOLD' }
    : { id: 'initial-held-zero', step: 0, forward: 0, turn: 0, vertical: 0, intent: 'HOLD' };
}

/** Prescribed diagnostic poses only. Never replayed as closed-loop sensory input. */
export function observerProbe(authority: NeuralArtifact) {
  const probes = ['STATIC', 'LATERAL', 'YAW', 'MIXED'] as const;
  return probes.map(kind => {
    const adapters = [new FlightPoseNeuralAdapter(authority, .4), new FlightPoseNeuralAdapter(authority, -.4)];
    let previous: FlightFrame | undefined;
    const rows = [];
    for (let step = 0; step <= 20; step++) {
      const current = createFlightTrial().initial;
      current.step = step; current.time = step * BODY_DT; current.heading = kind === 'YAW' ? step * .01 : kind === 'MIXED' ? step * .002 : 0;
      current.position[0] = kind === 'LATERAL' || kind === 'MIXED' ? step * .001 : 0;
      current.position[2] = kind === 'MIXED' ? step * .0005 : 0;
      const observations = adapters.map(a => a.observeAndAdvance(current, previous).observation);
      const pairs = observations.map(o => o ? [o.right, o.left] : [0, 0]);
      const relation = kind === 'LATERAL' ? 'NEGATED' : kind === 'MIXED' ? 'NO_GLOBAL_SIGN_EXPECTATION' : 'IDENTICAL';
      const residual = relation === 'NO_GLOBAL_SIGN_EXPECTATION' ? null : Math.max(...pairs[0].map((n, i) => Math.abs(pairs[1][i] - (relation === 'NEGATED' ? -n : n))));
      if (residual !== null && residual > 1e-12) throw new Error('Observer representability gate failed');
      rows.push({ step, pose: structuredClone(current), observations, relation, residual });
      previous = current;
    }
    return { kind, origin: 'OFFLINE_PRESCRIBED_OBSERVER_DIAGNOSTIC_NOT_FLIGHT_DATA', rows };
  });
}
function diagnostic(raw: number[], bounded: number[], flags: boolean[]) {
  return { intervals: raw.length, count: flags.filter(Boolean).length,
    fraction: flags.filter(Boolean).length / flags.length, first_interval: flags.indexOf(true) < 0 ? null : flags.indexOf(true),
    peak_pre_clamp: Math.max(0, ...raw.map(Math.abs)), peak_post_clamp: Math.max(0, ...bounded.map(Math.abs)) };
}
function summarize(frames: FlightFrame[], intervals: NeuralFlightInterval[], mode: Mode) {
  const visualRaw = intervals.map(r => Math.max(0, ...r.observation?.raw_normalized.map(Math.abs) ?? [0]));
  const visualBounded = intervals.map(r => Math.max(Math.abs(r.observation?.right ?? 0), Math.abs(r.observation?.left ?? 0)));
  const visualFlags = intervals.map(r => r.observation?.clipped.some(Boolean) ?? false);
  const visual = diagnostic(visualRaw, visualBounded, visualFlags);
  const neural = portable({
    total_substeps: intervals.at(-1)!.after.substeps,
    mean_signed_neural_turn: intervals.reduce((s, r) => s + r.yaw.neuralTurn, 0) / intervals.length,
    integrated_absolute_applied_neural_omega: intervals.reduce((s, r) => s + Math.abs(r.yaw.neuralTurn * .8) * BODY_DT, 0),
    integrated_absolute_neural_omega_while_yaw_enabled: intervals.reduce((s, r, i) => s + (frames[i + 1].state !== 'grounded' && frames[i + 1].state !== 'landing' ? Math.abs(r.yaw.neuralTurn * .8) * BODY_DT : 0), 0),
    peak_absolute_readout: Math.max(...intervals.map(r => Math.abs(r.before.mean_yaw_drive_eq!))),
    peak_absolute_hs: Math.max(...intervals.flatMap(r => r.after.hs.map(Math.abs))),
    peak_absolute_dnp15: Math.max(...intervals.flatMap(r => r.after.dn.map(Math.abs))),
    saturation: { visual, neural_input: { ...visual, note: 'Same bounded observer values; solver adds no additional input clamp' },
      projection_potential: diagnostic(intervals.map(r => r.yaw.rawOmega), intervals.map(r => r.yaw.omega), intervals.map(r => r.yaw.projectionClamped)),
      projection_applied: diagnostic(intervals.map(r => mode === 'ON' ? r.yaw.rawOmega : 0), intervals.map(r => r.yaw.neuralTurn * .8), intervals.map(r => mode === 'ON' && r.yaw.projectionClamped)),
      combined_applied_command: diagnostic(intervals.map(r => r.engineering.turn + r.yaw.neuralTurn), intervals.map(r => r.yaw.appliedTurn), intervals.map(r => r.yaw.combinedClamped)),
      active_projection_clamped: intervals.filter((r, i) => frames[i + 1].state !== 'grounded' && frames[i + 1].state !== 'landing' && r.yaw.projectionClamped).length,
    },
  });
  return { final: structuredClone(frames.at(-1)!), cumulative_heading_change: frames.at(-1)!.heading - frames[0].heading,
    neural, events: frames.flatMap(f => f.events), contacts: frames.flatMap(f => f.events.filter(e => e.kind === 'CONTACT')),
    termination: 'DURATION_COMPLETED', grounded: frames.at(-1)!.state === 'grounded' };
}
export function executeCondition(authority: NeuralArtifact, id: string) {
  const spec = conditionSpecs().find(c => c.id === id);
  if (!spec) throw new Error('Unexpected controlled condition ID');
  const scene = visualScene(spec.visual), trial = createFlightTrial();
  const flight = new FlightEngine(trial), neural = new FlightPoseNeuralAdapter(authority, scene.plane_z);
  const intervals: NeuralFlightInterval[] = [];
  // Same public observer/solver, projection and plant seams used by v9. Each
  // invocation owns independent state and only accepted local body history.
  for (let step = 0; step < 600; step++) {
    const current = flight.snapshot(), previous = step ? flight.frame(step - 1) : undefined;
    const model = neural.observeAndAdvance(current, previous), engineering = commandAt(trial, step);
    const yaw = projectFlightYaw(model.before.orientation_increment_eq!, engineering.turn, spec.mode === 'ZERO_PROJECTION' ? 'ZERO' : spec.mode);
    const next = yaw.appliedTurn === engineering.turn ? flight.advance() : flight.advanceWithTurn(yaw.appliedTurn);
    intervals.push({ step, time: current.time, available_time: next.time, ...model, engineering, yaw, heading_delta: next.heading - current.heading });
  }
  const frames = flight.frames();
  return { ...spec, scene, frames, intervals, summary: summarize(frames, intervals, spec.mode) };
}
type ConditionResult = ReturnType<typeof executeCondition>;
function compare(a: ConditionResult, b: ConditionResult) {
  const finalA = a.frames.at(-1)!, finalB = b.frames.at(-1)!;
  const first = a.frames.findIndex((f, i) => Math.max(Math.abs(f.heading - b.frames[i].heading), ...f.position.map((n, j) => Math.abs(n - b.frames[i].position[j]))) > 1e-10);
  return { a: a.id, b: b.id, heading_a_minus_b: finalA.heading - finalB.heading,
    final_xyz_separation: Math.hypot(...finalA.position.map((n, i) => n - finalB.position[i])),
    first_material_boundary: first < 0 ? null : first, first_material_time_s: first < 0 ? null : first * BODY_DT };
}
export async function runControlledExperiment(authority: NeuralArtifact, timings: Record<string, number> = {}) {
  const protocol = experimentProtocol(authority);
  let start = performance.now();
  const probe = observerProbe(authority);
  timings.observer_probe_ms = performance.now() - start;
  // Gate A precedes every closed-loop run; no result-dependent visual selection.
  const lateral = probe.find(p => p.kind === 'LATERAL')!;
  if (!lateral.rows.some(r => Math.abs(r.observations[0]?.right ?? 0) > 1e-10)) throw new Error('Degenerate visual transformation');
  start = performance.now();
  const conditions = conditionSpecs().map(s => executeCondition(authority, s.id));
  timings.six_conditions_ms = performance.now() - start;
  const [e1, e2, e3, e4, e5, e6] = conditions;
  const legacy = new FlightEngine(createFlightTrial()); while (legacy.snapshot().step < 600) legacy.advance();
  for (const control of [e1, e2, e4, e5]) if (flightCanonical(control.frames) !== flightCanonical(legacy.frames())) throw new Error('OFF/ZERO historical body equality failed');
  const d0 = compare(e3, e1), d1 = compare(e6, e4), paired = compare(e6, e3);
  const neuralDifference = Math.max(...e3.intervals.flatMap((r, i) => [...r.after.hs.map((n, j) => Math.abs(n - e6.intervals[i].after.hs[j])), ...r.after.dn.map((n, j) => Math.abs(n - e6.intervals[i].after.dn[j]))]));
  const sensoryDifference = Math.max(...e3.intervals.flatMap((r, i) => ['right', 'left'].map(k => Math.abs((r.observation?.[k as 'right'] ?? 0) - (e6.intervals[i].observation?.[k as 'right'] ?? 0)))));
  const interaction = d1.heading_a_minus_b - d0.heading_a_minus_b;
  const result = { probe: portable(probe), conditions: conditions.map(c => ({ ...c, intervals: portable(c.intervals) })),
    comparisons: { D_V0: d0, D_V1: d1, ON_visual_comparison: paired, final_heading_interaction: interaction,
      max_ON_neural_difference: roundNeural(neuralDifference), max_ON_sensory_difference: roundNeural(sensoryDifference) },
    hypotheses: hypothesisOutcomes(sensoryDifference, neuralDifference, interaction),
    scientific_status: 'INTERNAL_MODEL_EXPERIMENT_NOT_EMPIRICAL_VALIDATION' };
  const input = { protocol }, input_sha256 = await flightHash(input), result_sha256 = await flightHash(result);
  return { schema: CONTROLLED_SCHEMA, input, result, input_sha256, result_sha256, artifact_id: await flightHash({ input_sha256, result_sha256 }) };
}
export type ControlledArtifact = Awaited<ReturnType<typeof runControlledExperiment>>;
export function hypothesisOutcomes(sensoryDifference: number, neuralDifference: number, interaction: number) {
  if (![sensoryDifference, neuralDifference, interaction].every(Number.isFinite) || sensoryDifference < 0 || neuralDifference < 0) throw new Error('Invalid hypothesis metrics');
  // H1/H4 are reached only after their explicit engineering gates in the runner.
  return { H0: sensoryDifference <= 1e-10 ? 'SUPPORTED' : 'REJECTED', H1: 'SUPPORTED', H2: neuralDifference > 1e-10 ? 'DISTINGUISHABLE' : 'UNCHANGED', H3: Math.abs(interaction) > 1e-10 ? 'DISTINGUISHABLE' : 'UNCHANGED', H4: 'EXACT_CONTROL_EQUALITY' };
}
export async function verifyControlledExperiment(authority: NeuralArtifact, value: unknown) {
  const run = value as ControlledArtifact;
  if (!run || run.schema !== CONTROLLED_SCHEMA || !run.input || !run.result ||
    flightCanonical(run.input.protocol) !== flightCanonical(experimentProtocol(authority)) ||
    !Array.isArray(run.result.conditions) || run.result.conditions.length !== 6 ||
    run.result.conditions.some((c, i) => c.id !== conditionSpecs()[i].id || !Array.isArray(c.frames) || c.frames.length !== 601 || !Array.isArray(c.intervals) || c.intervals.length !== 600)) throw new Error('Invalid controlled experiment schema/input/history');
  if (await flightHash(run.input) !== run.input_sha256 || await flightHash(run.result) !== run.result_sha256 || await flightHash({ input_sha256: run.input_sha256, result_sha256: run.result_sha256 }) !== run.artifact_id) throw new Error('Controlled experiment hash mismatch');
  const expected = await runControlledExperiment(authority);
  if (flightCanonical(run) !== flightCanonical(expected)) throw new Error('Controlled experiment semantic reconstruction mismatch');
  return expected;
}
