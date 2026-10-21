/** Versioned visual preset; the frozen v7.1 descriptor and 2 Hz reference stay intact. */
import type { FlightState, WingPose } from './articulatedWings';
import rig from '@/assets/fly_wings_v7_1.json';

export const FLIGHT_WINGS_V8 = {
  schema: 'engineering_flight_wings_v8',
  rig_sha256: 'f175ede40fd15892d6089d446146b371a4534be048ffa45447a7cb5a740a51ff',
  presets: { normal: 12, inspection: 2 },
  stroke_rad: rig.animation.stroke_rad, spread_rad: rig.animation.spread_rad,
  activation_altitude: .04,
} as const;
export type WingbeatPreset = keyof typeof FLIGHT_WINGS_V8.presets;
export function flightWingsV8(time: number, state: FlightState, altitude: number, preset: WingbeatPreset): WingPose {
  if (!Number.isFinite(time) || time < 0 || !Number.isFinite(altitude) || altitude < -1e-10 ||
      !['grounded', 'takeoff', 'flying', 'landing'].includes(state) || !Object.hasOwn(FLIGHT_WINGS_V8.presets, preset) ||
      (state === 'grounded' && Math.abs(altitude) > 1e-10)) throw new Error('Invalid engineering flight wing input');
  const x = Math.max(0, Math.min(1, altitude / FLIGHT_WINGS_V8.activation_altitude));
  const envelope = state === 'grounded' ? 0 : x * x * (3 - 2 * x);
  const phase = 2 * Math.PI * FLIGHT_WINGS_V8.presets[preset] * time;
  return { source: 'ENGINEERING_3D_FLIGHT_V8', time, state, altitude, preset, envelope, offset: 0, phase,
    stroke: envelope === 0 ? 0 : envelope * FLIGHT_WINGS_V8.stroke_rad * Math.sin(phase), spread: envelope * FLIGHT_WINGS_V8.spread_rad };
}
export function validateFlightWingsV8(pose: WingPose) {
  if (pose.source !== 'ENGINEERING_3D_FLIGHT_V8' || pose.altitude === undefined || pose.preset === undefined ||
      JSON.stringify(pose) !== JSON.stringify(flightWingsV8(pose.time, pose.state, pose.altitude, pose.preset))) throw new Error('Contradictory v8 wing pose');
}
