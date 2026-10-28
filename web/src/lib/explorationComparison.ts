import { BODY_DT } from './interactiveNeuralLocomotion';
import { EXPLORATION_POLICY, type ExplorationMode } from './engineeringExploration';
import { LiveGroundSession, type LiveInitialPose } from './liveGroundSession';
import { locomotionBounds } from './experimentalLocomotion';
import type { NeuralArtifact } from './neuralLocomotion';

export type ExplorationRunMetrics = {
  mode: ExplorationMode;
  ticks: number;
  simulated_seconds: number;
  path_length_units: number;
  mean_commanded_speed_units_s: number;
  mean_accepted_speed_units_s: number;
  wall_contact_count: number;
  wall_contact_frequency_per_minute: number;
  time_near_forward_boundary_s: number;
  accepted_speed_bin_counts: Record<string, number>;
  angular_velocity_bin_counts: Record<string, number>;
  behavior_state_seconds: Record<string, number>;
  mean_neural_yaw_rad_s: number;
  mean_absolute_neural_yaw_rad_s: number;
  mean_boundary_yaw_rad_s: number;
  mean_absolute_boundary_yaw_rad_s: number;
  containment_violations: number;
  non_finite_states: number;
};

export type ExplorationComparison = {
  schema: 'engineering_exploration_ab_v1';
  ticks: number;
  body_dt_s: typeof BODY_DT;
  identical_initial_pose: true;
  neural_influence: boolean;
  baseline: ExplorationRunMetrics;
  exploration: ExplorationRunMetrics;
};

function run(authority: NeuralArtifact, initial: LiveInitialPose, neural: boolean, mode: ExplorationMode, ticks: number): ExplorationRunMetrics {
  const session = new LiveGroundSession(authority, neural, `ab-${mode}`, { trajectory: 4, telemetry: 4, events: 8 }, initial, mode);
  const [xLimit, zLimit] = locomotionBounds(authority.config.body);
  const behavior: Record<string, number> = {};
  const speedBins = { zero: 0, '(0,0.045]': 0, '(0.045,0.09]': 0, '(0.09,0.135]': 0, '(0.135,0.18]': 0, '>0.18': 0 };
  const yawBins = { '<-1.0': 0, '[-1.0,-0.5)': 0, '[-0.5,0)': 0, '[0,0.5)': 0, '[0.5,1.0)': 0, '>=1.0': 0 };
  let path = 0, command = 0, acceptedSpeed = 0, near = 0;
  let neuralYaw = 0, neuralAbs = 0, boundaryYaw = 0, boundaryAbs = 0;
  let containmentViolations = 0, nonFinite = 0;
  let previous = session.snapshot().position;
  session.start();
  for (let i = 0; i < ticks; i++) {
    const sample = session.advance(), point = sample.accepted.position;
    const distance = Math.hypot(point[0] - previous[0], point[2] - previous[2]);
    path += distance; command += sample.engineering.commanded_speed_units_s; acceptedSpeed += sample.engineering.actual_speed_units_s;
    const acceptedRate = sample.engineering.actual_speed_units_s, yaw = sample.interval.angular_velocity;
    if (acceptedRate === 0) speedBins.zero++;
    else if (acceptedRate <= .045 + 1e-12) speedBins['(0,0.045]']++;
    else if (acceptedRate <= .09 + 1e-12) speedBins['(0.045,0.09]']++;
    else if (acceptedRate <= .135 + 1e-12) speedBins['(0.09,0.135]']++;
    else if (acceptedRate <= .18 + 1e-12) speedBins['(0.135,0.18]']++;
    else speedBins['>0.18']++;
    if (yaw < -1) yawBins['<-1.0']++;
    else if (yaw < -.5) yawBins['[-1.0,-0.5)']++;
    else if (yaw < 0) yawBins['[-0.5,0)']++;
    else if (yaw < .5) yawBins['[0,0.5)']++;
    else if (yaw < 1) yawBins['[0.5,1.0)']++;
    else yawBins['>=1.0']++;
    if (sample.engineering.clearance_units <= EXPLORATION_POLICY.slow_clearance_units) near++;
    behavior[sample.engineering.state] = (behavior[sample.engineering.state] ?? 0) + BODY_DT;
    const ny = sample.interval.boundary_summary.neural_omega, by = sample.interval.boundary_summary.omega;
    neuralYaw += ny; neuralAbs += Math.abs(ny); boundaryYaw += by; boundaryAbs += Math.abs(by);
    if (Math.abs(point[0]) > xLimit + 1e-12 || Math.abs(point[2]) > zLimit + 1e-12) containmentViolations++;
    if (![...point, sample.accepted.heading, ...sample.accepted.hs, ...sample.accepted.dn, ny, by, sample.engineering.commanded_speed_units_s, sample.engineering.actual_speed_units_s].every(Number.isFinite)) nonFinite++;
    previous = point;
  }
  const final = session.snapshot(); session.stop();
  return {
    mode, ticks, simulated_seconds: ticks * BODY_DT, path_length_units: path,
    mean_commanded_speed_units_s: command / ticks, mean_accepted_speed_units_s: acceptedSpeed / ticks,
    wall_contact_count: final.contacts, wall_contact_frequency_per_minute: final.contacts / (ticks * BODY_DT) * 60,
    time_near_forward_boundary_s: near * BODY_DT, accepted_speed_bin_counts: speedBins, angular_velocity_bin_counts: yawBins,
    behavior_state_seconds: behavior,
    mean_neural_yaw_rad_s: neuralYaw / ticks, mean_absolute_neural_yaw_rad_s: neuralAbs / ticks,
    mean_boundary_yaw_rad_s: boundaryYaw / ticks, mean_absolute_boundary_yaw_rad_s: boundaryAbs / ticks,
    containment_violations: containmentViolations, non_finite_states: nonFinite,
  };
}

/** Same initial pose, authority, seed policy, interval count and neural setting; all aggregates are incremental. */
export function compareExplorationModes(authority: NeuralArtifact, ticks: number, neuralInfluence = true, initial?: LiveInitialPose): ExplorationComparison {
  if (!Number.isSafeInteger(ticks) || ticks < 1 || ticks > 100_000) throw new Error('Invalid A/B comparison horizon');
  const baseline = new LiveGroundSession(authority, neuralInfluence, 'ab-initial', undefined, initial, 'baseline_v10_5b');
  const pose = baseline.config.initial_pose;
  return {
    schema: 'engineering_exploration_ab_v1', ticks, body_dt_s: BODY_DT, identical_initial_pose: true,
    neural_influence: neuralInfluence,
    baseline: run(authority, pose, neuralInfluence, 'baseline_v10_5b', ticks),
    exploration: run(authority, pose, neuralInfluence, 'engineering_exploration_v1', ticks),
  };
}
