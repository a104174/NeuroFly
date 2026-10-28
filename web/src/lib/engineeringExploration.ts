/** Deterministic engineering speed modulation over the existing rectangular arena. */
export const EXPLORATION_POLICY = Object.freeze({
  id: 'engineering_exploration_v1',
  baseline_speed_units_s: 0.18,
  minimum_speed_units_s: 0.045,
  slow_clearance_units: 0.18,
  minimum_speed_clearance_units: 0.04,
});

export type ExplorationState = 'cruising' | 'approaching_boundary' | 'boundary_contact' | 'recovering';
export type ExplorationMode = 'baseline_v10_5b' | 'engineering_exploration_v1';

export function forwardClearance(position: readonly number[], heading: number, limits: readonly number[]) {
  if (position.length !== 3 || limits.length !== 2 || ![...position, heading, ...limits].every(Number.isFinite) || limits.some(x => x <= 0)) throw new Error('Invalid exploration geometry');
  const dx = Math.sin(heading), dz = Math.cos(heading);
  const x = dx > 1e-12 ? (limits[0] - position[0]) / dx : dx < -1e-12 ? (-limits[0] - position[0]) / dx : Infinity;
  const z = dz > 1e-12 ? (limits[1] - position[2]) / dz : dz < -1e-12 ? (-limits[1] - position[2]) / dz : Infinity;
  const clearance = Math.max(0, Math.min(x, z));
  if (!Number.isFinite(clearance)) throw new Error('Forward clearance is not finite');
  return clearance;
}

export function explorationCommand(clearance: number) {
  const p = EXPLORATION_POLICY;
  if (!Number.isFinite(clearance) || clearance < 0) throw new Error('Invalid forward clearance');
  if (clearance >= p.slow_clearance_units) return p.baseline_speed_units_s;
  if (clearance <= p.minimum_speed_clearance_units) return p.minimum_speed_units_s;
  const fraction = (clearance - p.minimum_speed_clearance_units) / (p.slow_clearance_units - p.minimum_speed_clearance_units);
  return p.minimum_speed_units_s + fraction * (p.baseline_speed_units_s - p.minimum_speed_units_s);
}

export function explorationState(clearance: number, contact: string | null, previous: ExplorationState): ExplorationState {
  if (contact) return 'boundary_contact';
  if (previous === 'boundary_contact') return 'recovering';
  if (clearance < EXPLORATION_POLICY.slow_clearance_units) return 'approaching_boundary';
  return 'cruising';
}
