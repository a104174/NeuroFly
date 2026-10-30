/** Bounded geometric observations for engineering flight; these are not neural sensory signals. */
import { FLIGHT_MODEL, flightBounds, flightCanonical, type FlightFrame } from './engineeringFlight';

export const FLIGHT_ARENA_OBSERVATION_SCHEMA = 'neurofly_flight_arena_observation_v1' as const;

export type FlightArenaBounds = ReturnType<typeof flightBounds>;
export type FlightArenaObservation = {
  schema: typeof FLIGHT_ARENA_OBSERVATION_SCHEMA;
  accepted: FlightFrame;
  forward_wall_clearance_units: number;
  left_wall_clearance_units: number;
  right_wall_clearance_units: number;
  floor_clearance_units: number;
  ceiling_clearance_units: number;
  horizontal_speed_units_s: number;
};

function rayBoxClearance(
  position: readonly [number, number, number],
  direction: readonly [number, number],
  bounds: FlightArenaBounds,
) {
  const [x, , z] = position;
  const [dx, dz] = direction;
  const tx = dx > 1e-12 ? (bounds.max[0] - x) / dx : dx < -1e-12 ? (bounds.min[0] - x) / dx : Infinity;
  const tz = dz > 1e-12 ? (bounds.max[2] - z) / dz : dz < -1e-12 ? (bounds.min[2] - z) / dz : Infinity;
  const distance = Math.min(tx, tz);
  if (!Number.isFinite(distance) || distance < -1e-12) throw new Error('Could not resolve finite arena wall clearance');
  return Math.max(0, distance);
}

function validateAcceptedFrame(frame: FlightFrame, bounds: FlightArenaBounds) {
  if (!frame || !Array.isArray(frame.position) || frame.position.length !== 3 || !Array.isArray(frame.velocity) || frame.velocity.length !== 3 ||
      !Number.isSafeInteger(frame.step) || frame.step < 0 || frame.time !== frame.step * FLIGHT_MODEL.dt_s ||
      ![...frame.position, ...frame.velocity, frame.heading, frame.stateSince].every(Number.isFinite) ||
      !['grounded', 'takeoff', 'flying', 'landing'].includes(frame.state) ||
      !Array.isArray(frame.contacts) || frame.contacts.some(contact => !['X_WALL', 'FLOOR', 'CEILING', 'Z_WALL'].includes(contact)) || !Array.isArray(frame.events) ||
      !bounds || !Array.isArray(bounds.min) || !Array.isArray(bounds.max) || bounds.min.length !== 3 || bounds.max.length !== 3 ||
      ![...bounds.min, ...bounds.max].every(Number.isFinite) ||
      bounds.min.some((value, axis) => value >= bounds.max[axis])) throw new Error('Invalid accepted flight state or arena bounds');
  for (let axis = 0; axis < 3; axis++) {
    if (frame.position[axis] < bounds.min[axis] - 1e-12 || frame.position[axis] > bounds.max[axis] + 1e-12)
      throw new Error(`Accepted flight position is outside axis ${axis} bounds`);
  }
}

/**
 * Query ray distances against the plant's conservative X/Z bounds. Heading 0
 * faces +Z; positive heading rotates toward +X. Clearances are presentation
 * units, not optic flow, calibrated vision, or biological sensory measurements.
 */
export function observeFlightArena(frame: FlightFrame, bounds: FlightArenaBounds = flightBounds()): FlightArenaObservation {
  validateAcceptedFrame(frame, bounds);
  const forward: [number, number] = [Math.sin(frame.heading), Math.cos(frame.heading)];
  const right: [number, number] = [Math.cos(frame.heading), -Math.sin(frame.heading)];
  const left: [number, number] = [-right[0], -right[1]];
  return {
    schema: FLIGHT_ARENA_OBSERVATION_SCHEMA,
    accepted: structuredClone(frame),
    forward_wall_clearance_units: rayBoxClearance(frame.position, forward, bounds),
    left_wall_clearance_units: rayBoxClearance(frame.position, left, bounds),
    right_wall_clearance_units: rayBoxClearance(frame.position, right, bounds),
    floor_clearance_units: frame.position[1] - bounds.min[1],
    ceiling_clearance_units: bounds.max[1] - frame.position[1],
    horizontal_speed_units_s: Math.hypot(frame.velocity[0], frame.velocity[2]),
  };
}

/** Reject altered/stale geometric observations before they can drive a command. */
export function validateFlightArenaObservation(observation: FlightArenaObservation, bounds: FlightArenaBounds = flightBounds()) {
  if (!observation || observation.schema !== FLIGHT_ARENA_OBSERVATION_SCHEMA) throw new Error('Unsupported flight arena observation schema');
  const expected = observeFlightArena(observation.accepted, bounds);
  if (flightCanonical(expected) !== flightCanonical(observation)) throw new Error('Flight arena observation does not match its accepted state and bounds');
  return structuredClone(expected);
}
