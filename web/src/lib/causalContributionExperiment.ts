/** V10.6A protocol reuses the existing v3.1 matched, replayable comparison. */
import { ContinuousNavigationEngine, navigationHash } from './continuousArenaNavigation';
import { generatePair, validatePair, type PairArtifact } from './neuralContributionComparison';
import { BODY_DT } from './interactiveNeuralLocomotion';
import type { NeuralArtifact } from './neuralLocomotion';

export function contributionReport(pair: PairArtifact) {
  if (pair.result.tracks.length !== 2 || pair.result.tracks.some((t, i) => t.key !== (i === 0 ? "ON" : "OFF") || t.NEURAL_TO_HEADING_ENABLED !== (i === 0) || t.frames.length < 2 || t.frames.length !== Math.round(pair.config.duration_s / BODY_DT) + 1)) throw new Error("Incomplete or mismatched comparison");
  const gain = Number(pair.config.matched_config.gain), bound = Number(pair.config.matched_config.omega_bound);
  if (gain !== 2.5 || bound !== .5) throw new Error('Unsupported motor projection provenance');
  const tracks = pair.result.tracks.map(track => {
    let computedAbs = 0, appliedAbs = 0, boundaryAbs = 0;
    const intervals = track.frames.slice(0, -1).map((frame, i) => {
      const increment = frame.neural_summary?.orientation_increment_eq;
      if (increment === null || increment === undefined || !Number.isFinite(increment)) throw new Error('Missing computed motor measurement');
      const computed = Math.max(-bound, Math.min(bound, gain * increment / BODY_DT));
      const applied = frame.boundary_summary.neural_omega, boundary = frame.boundary_summary.omega;
      const next = track.frames[i + 1];
      if (![computed, applied, boundary, frame.angular_velocity, next.orientation].every(Number.isFinite) || Math.abs(applied - (track.NEURAL_TO_HEADING_ENABLED ? computed : 0)) > 1e-12 || Math.abs(frame.angular_velocity - applied - boundary) > 1e-12 || Math.abs(next.orientation - frame.orientation - frame.angular_velocity * BODY_DT) > 1e-12) throw new Error('Motor boundary telemetry mismatch');
      computedAbs += Math.abs(computed); appliedAbs += Math.abs(applied); boundaryAbs += Math.abs(boundary);
      return { tick: frame.step, interval_start_s: frame.time, accepted_tick: next.step, computed_neural_yaw_rad_s: computed, applied_neural_yaw_rad_s: applied, engineering_boundary_yaw_rad_s: boundary, total_yaw_rad_s: frame.angular_velocity, heading_before_rad: frame.orientation, heading_after_rad: next.orientation };
    });
    return { run_id: `${pair.artifact_id}:${track.key}`, condition: track.key === 'ON' ? 'CONTROL' : 'neural_yaw_contribution_ablation', intervals, mean_abs_computed_yaw_rad_s: computedAbs / intervals.length, mean_abs_applied_yaw_rad_s: appliedAbs / intervals.length, mean_abs_boundary_yaw_rad_s: boundaryAbs / intervals.length, final_position: track.final_state.position, final_heading_rad: track.final_state.heading, path_length_units: track.final_state.distance, contact_events: track.contact_events.filter(e => e.kind === 'CONTACT').length };
  });
  return { experiment: 'V10.6A', pair_artifact_id: pair.artifact_id, parent_artifact_id: pair.parent.artifact_id, seed: null, random_policy: pair.config.random_policy, matched_config: pair.config.matched_config, independent_variable: 'NEURAL_TO_HEADING_ENABLED', intervention_boundary: 'AFTER_NEURAL_COMPUTATION_BEFORE_YAW_INTEGRATION', duration_s: pair.config.duration_s, metrics: pair.result.metrics, tracks, interpretation: 'Deterministic total closed-loop effect inside this model; later sensory inputs may diverge. Not biological causal validation.' };
}

export async function runContributionExperiment(authority: NeuralArtifact, ticks = 1500) {
  if (!Number.isInteger(ticks) || ticks < 1 || ticks > 1500) throw new Error('Experiment requires 1..1500 body intervals');
  const control = new ContinuousNavigationEngine(authority, 'neural');
  for (let n = 0; n < ticks; n++) control.advance();
  const parent = await control.exportNavigation();
  const pair = await generatePair(authority, parent, () => {}, async () => {});
  await validatePair(authority, pair);
  const report = contributionReport(pair);
  return { pair, report, report_sha256: await navigationHash(report) };
}
