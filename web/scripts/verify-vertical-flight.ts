import {
  canonicalVerticalFlightResult, runVerticalFlightVerification, verticalFlightResultHashes,
} from '../src/lib/verticalFlightFeedback';

const first = runVerticalFlightVerification();
const second = runVerticalFlightVerification();
for (const result of [first, second]) {
  if (result.termination !== 'LANDED' || result.metrics.final_state !== 'grounded' ||
      !result.metrics.target_condition_reached || result.metrics.airborne_duration_s <= 0 || result.metrics.bound_violations !== 0)
    throw new Error('State-feedback vertical-flight verification did not complete a valid bounded flight cycle');
}
if (canonicalVerticalFlightResult(first) !== canonicalVerticalFlightResult(second))
  throw new Error('Repeated state-feedback vertical-flight verification did not reproduce exactly');
const hashes = await verticalFlightResultHashes(first);
console.log(JSON.stringify({
  result_schema: first.schema,
  classification: first.classification,
  configuration: first.configuration,
  provenance: first.provenance,
  termination: first.termination,
  metrics: first.metrics,
  deterministic_repeat: 'MATCH',
  input_sha256: hashes.input_sha256,
  result_sha256: hashes.result_sha256,
}, null, 2));
