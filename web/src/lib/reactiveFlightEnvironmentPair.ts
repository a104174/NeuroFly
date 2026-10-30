/** Headless engineering comparison; no renderer, biological sensor, or new controller. */
import { FLIGHT_MODEL, flightCanonical, flightHash } from './engineeringFlight';
import { REACTIVE_FLIGHT_CONFIG, reactiveFlightEnvironmentConfig, runReactiveFlightVerification } from './reactiveFlightExploration';

export const ENVIRONMENT_PAIR_PROTOCOL = {
  schema: 'reactive_flight_environment_pair_v1',
  reference_revision: '6e3295b10526cf4d1fdf784dec99fc99c2d64e4a',
  baseline: REACTIVE_FLIGHT_CONFIG,
  variant: reactiveFlightEnvironmentConfig({ ...FLIGHT_MODEL.arena, width: 2 }),
  perturbation: { parameter: 'chamber.width', baseline: 2.4, variant: 2, units: 'presentation units' },
  difference_tolerance: 1e-8,
  randomness: 'NONE',
} as const;

type Run = ReturnType<typeof runReactiveFlightVerification>;
function compare(a: Run, b: Run) {
  const tolerance = ENVIRONMENT_PAIR_PROTOCOL.difference_tolerance;
  const fields = ['forward_wall_clearance_units', 'left_wall_clearance_units', 'right_wall_clearance_units',
    'floor_clearance_units', 'ceiling_clearance_units'] as const;
  const firstObservation = a.intervals.findIndex((interval, index) => fields.some(key =>
    Math.abs(interval.observation[key] - b.intervals[index].observation[key]) > tolerance));
  const firstCommand = a.intervals.findIndex((interval, index) => {
    const other = b.intervals[index].decision.command, command = interval.decision.command;
    return ['forward', 'turn', 'vertical'].some(key => Math.abs(command[key as 'forward'] - other[key as 'forward']) > tolerance) || command.intent !== other.intent;
  });
  const statesA = [a.configuration.initial_state, ...a.intervals.map(v => v.accepted)];
  const statesB = [b.configuration.initial_state, ...b.intervals.map(v => v.accepted)];
  const separation = statesA.map((frame, index) => Math.hypot(...frame.position.map((v, axis) => v - statesB[index].position[axis])));
  const headingIndex = statesA.findIndex((frame, index) => {
    const delta = frame.heading - statesB[index].heading;
    return Math.abs(Math.atan2(Math.sin(delta), Math.cos(delta))) > tolerance;
  });
  const positionIndex = separation.findIndex(value => value > tolerance);
  const event = (index: number) => index < 0 ? null : { index, time_s: index * FLIGHT_MODEL.dt_s };
  const maximum = Math.max(...separation), maxIndex = separation.indexOf(maximum);
  return {
    initial_observation_differences: fields.filter(key => a.intervals[0].observation[key] !== b.intervals[0].observation[key]),
    first_observation: event(firstObservation), first_command: event(firstCommand),
    first_heading: event(headingIndex), first_position: event(positionIndex),
    maximum_position_separation_units: maximum, maximum_separation_at: event(maxIndex),
    final_position_separation_units: separation.at(-1)!,
    contact_events_differ: flightCanonical(a.events.filter(e => e.kind === 'CONTACT')) !== flightCanonical(b.events.filter(e => e.kind === 'CONTACT')),
    interpretation: firstCommand < 0 || positionIndex < 0 ? 'INCONCLUSIVE_TRAJECTORY_SENSITIVITY' : 'ENGINEERING_ENVIRONMENT_SENSITIVITY_OBSERVED',
  };
}
export function runReactiveFlightEnvironmentPair() {
  const baseline = runReactiveFlightVerification(ENVIRONMENT_PAIR_PROTOCOL.baseline);
  const variant = runReactiveFlightVerification(ENVIRONMENT_PAIR_PROTOCOL.variant);
  for (const run of [baseline, variant]) {
    if (run.termination !== 'DURATION_LIMIT_REACHED' || run.metrics.accepted_bound_violations || run.failure)
      throw new Error('Environment pair did not complete valid bounded flight');
  }
  return { protocol: structuredClone(ENVIRONMENT_PAIR_PROTOCOL), baseline, variant, comparison: compare(baseline, variant) };
}
/** Reconstruction checks complete scientific evidence, including command/pose alignment and environment identity. */
export function validateReactiveFlightEnvironmentPair(value: unknown) {
  const expected = runReactiveFlightEnvironmentPair();
  if (flightCanonical(value) !== flightCanonical(expected)) throw new Error('Malformed or mismatched reactive environment pair evidence');
  return expected;
}
export async function environmentPairHash(value: ReturnType<typeof runReactiveFlightEnvironmentPair>) {
  return flightHash(value);
}
