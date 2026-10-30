/** Predeclared V10.8I verification; the treatment is recovery applicability only. */
import type { NeuralArtifact } from './neuralLocomotion';
import { MixedGroundFlightSession, LANDING_RECOVERY_PROTOCOL } from './mixedGroundFlight';

export const LANDING_RECOVERY_VERIFICATION = {
  schema:'mixed_landing_recovery_verification_v1', controller:LANDING_RECOVERY_PROTOCOL,
  initial_heading_rad:0, robustness_heading_rad:Math.PI/2,
  initial_landing_deadline_s:30, continuation_horizon_s:60,
  treatment:'EXISTING_RESUMED_RECOVERY_ALSO_APPLIES_TO_INITIAL_FLIGHT',
  success:'OBSERVED_UNSAFE_CLEARANCE_RECOVERY_THEN_ADMISSIBLE_LAND_REQUEST_AND_ACCEPTED_FLOOR_BEFORE_30_SECONDS',
  continuation:'GENUINE_GROUND_WALKING_THEN_SECOND_ACCEPTED_FLIGHT_WITHIN_60_SECONDS',
  randomness:'NONE',seed:null,
} as const;

export function runMixedLandingRecovery(authority:NeuralArtifact, heading:number = LANDING_RECOVERY_VERIFICATION.initial_heading_rad) {
  const session=new MixedGroundFlightSession(authority,true,heading,true);
  session.start();
  while(session.status==='running') { try { session.advance(); } catch { break; } }
  const result=session.result();
  const activation=result.intervals.find(i=>i.active_engine==='flight_initial'&&i.landing_recovery?.policy?.active);
  const request=result.intervals.find(i=>i.active_engine==='flight_initial'&&
    (i.native_evidence as {decision?:{command:{intent:string}}}).decision?.command.intent==='LAND');
  const landing=result.intervals.find(i=>i.active_engine==='flight_initial'&&i.accepted.state==='grounded');
  const secondFlight=result.intervals.find(i=>i.active_engine==='flight_resumed'&&i.accepted.state==='flying');
  const safe=result.metrics.accepted_bound_violations===0&&result.metrics.invalid_command_count===0&&
    result.metrics.maximum_handoff_position_discontinuity===0&&result.metrics.maximum_timestamp_discontinuity===0;
  const landed=!!request&&!!landing&&request.landing_recovery?.landing_eligible===true&&
    landing.accepted.contacts.includes('FLOOR')&&landing.accepted.time<=LANDING_RECOVERY_VERIFICATION.initial_landing_deadline_s;
  return {...result,verification:{protocol:LANDING_RECOVERY_VERIFICATION,
    recovery_activated:!!activation,first_activation_time_s:activation?.global_time_s??null,
    landing_request_time_s:request?.global_time_s??null,accepted_landing_time_s:landing?.accepted.time??null,
    first_resumed_flying_time_s:secondFlight?.accepted.time??null,
    initial_landing_passed:landed&&safe,
    heading_zero_correction_passed:heading===0&&!!activation&&landed&&safe,
    continuation_passed:landed&&safe&&!!secondFlight&&result.metrics.walking_distance_units>0,
    finite_window_completed:result.termination==='DURATION_WINDOW_COMPLETED'}};
}
