import { SOURCE_IDS, TARGET_IDS } from './interactiveNeuralLocomotion';
import type { LiveSample } from './liveGroundSession';

/** Computed states at the interval's left boundary; no anatomy is inferred. */
export function neuralActivityTrace(sample: LiveSample) {
  const { interval, accepted, engineering } = sample;
  const neural = interval.neural_summary;
  if (!neural || neural.hs_states.length !== SOURCE_IDS.length || neural.dnp15_states.length !== TARGET_IDS.length) throw new Error('Neural interval state unavailable');
  const values = [...neural.hs_states, ...neural.dnp15_states, interval.angular_velocity, interval.boundary_summary.neural_omega, interval.boundary_summary.omega, engineering.clearance_units, engineering.baseline_speed_units_s, engineering.commanded_speed_units_s, engineering.actual_speed_units_s];
  if (!values.every(Number.isFinite) || accepted.step !== interval.step + 1) throw new Error('Invalid neural interval trace');
  return {
    schema: 'live_neural_activity_trace_v1' as const,
    tick: interval.step, time_s: interval.time, accepted_tick: accepted.step,
    states: [...SOURCE_IDS.map((id, i) => ({ id, model: 'HS' as const, value: neural.hs_states[i], semantics: 'COMPUTED_MODEL_STATE' as const })), ...TARGET_IDS.map((id, i) => ({ id, model: 'DNp15' as const, value: neural.dnp15_states[i], semantics: 'COMPUTED_MODEL_STATE' as const }))],
    mean_differential: neural.mean_yaw_drive_eq,
    neural_enabled: interval.steering_applied === true,
    neural_yaw_rad_s: interval.boundary_summary.neural_omega,
    boundary_yaw_rad_s: interval.boundary_summary.omega,
    angular_velocity_rad_s: interval.angular_velocity,
    previous_position: interval.position, accepted_position: accepted.position,
    previous_heading: interval.orientation, accepted_heading: accepted.heading,
    engineering: {
      mode: engineering.mode,
      behavior_state: engineering.state,
      previous_state: engineering.previous_state,
      transition_trigger: engineering.transition_trigger,
      forward_clearance_units: engineering.clearance_units,
      baseline_speed_units_s: engineering.baseline_speed_units_s,
      commanded_speed_units_s: engineering.commanded_speed_units_s,
      accepted_speed_units_s: engineering.actual_speed_units_s,
      contact: engineering.contact,
    },
    provenance: {
      structure: 'VERIFIED_MALECNS_DERIVED_AUTHORITY',
      authority_artifact_id: sample.source.authority_artifact_id,
      dataset_uuid: sample.source.dataset_uuid,
      authority_config_sha256: sample.source.config_sha256,
      authority_raw_sha256: sample.source.raw_sha256,
      activity: 'COMPUTED_HS_DNP15_MODEL_STATE',
      motor_mapping: 'ENGINEERING_NEURAL_YAW_PROJECTION',
      boundary_mapping: 'ENGINEERING_GEOMETRIC_YAW_RECOVERY',
      speed_mapping: engineering.mode === 'baseline_v10_5b' ? 'ENGINEERING_CONSTANT_PROPULSION' : 'ENGINEERING_CLEARANCE_SPEED_POLICY',
      morphology: 'UNAVAILABLE',
    },
  };
}
