# V10.8L — Independent contact and integrity classification

## Evidence and preservation

Source baseline: `a52f01d87d9e2377b446c1484f28b52a6429921f`. This phase changes interpretation only. The existing `mixed_flight_heading_robustness_v1` evaluator, its documentation, original D labels, controller, trajectories and protocols are unchanged.

V1 `summarizeMixedHeadingRun()` combines any wall contact with integrity-failure metrics in `unsafeCount`; `classifyHeadingLanding()` maps the combined flag to D. Ordinary FLOOR contacts are excluded. This conservative label does not establish a physical or numerical violation.

The retained complete compact matrix was available locally and verified against the published SHA before classification. No new scientific conditions or canonical simulations were needed for the assessment. Regression tests regenerate the original matrix to verify exact source parity. No synthetic unit fixture replaces canonical evidence.

Authoritative handoff interpretation: [V10.8K](ground_contact_handoff_admissibility_v10_8k.md). Ground accepted X/Z limits are ±0.9654288894 / ±0.3754288894; flight limits are ±0.914 / ±0.324. Thus a ground-valid pose need not be a valid flight initializer. At the two legal X-wall contacts (18.36 and 18.40 s), the coordinator withheld takeoff. Subsequent destination admissibility at 20.48/20.52 s was still insufficient until ray clearance passed at 20.90/20.96 s. Later handoffs preserved pose; no rejected audit probe was a coordinator attempt.

## Versioned axes

`mixed_flight_heading_classification_v2`, function `classifyMixedHeadingV2_v2`, is a separate deterministic interpretation of exactly the original eight cases. The matrix entrypoint validates the complete source hash before interpreting rows. It retains the source protocol/controller, per-run hashes, diagnostic field names and a K assessment reference. No timestamps, machine paths or rewritten source fields enter its canonical hash.

- **Behavior:** first accepted landing is WITHIN_30_SECONDS, AFTER_30_SECONDS, NOT_REACHED_WITHIN_HORIZON, or UNDETERMINED. An absent event is not replaced by time zero. A null landing with an early endpoint remains UNDETERMINED for the full horizon. Mixed continuation is independently COMPLETED, INCOMPLETE or UNDETERMINED from the existing completion/continuation evidence.
- **Integrity:** PASS means all required recorded numerical/bounds/transition/handoff/discontinuity/rejected-command diagnostics are available, finite, nonnegative and zero. A positive failure metric produces FAIL, even alongside contacts or successful behavior. Missing or malformed required diagnostics produce UNDETERMINED unless another metric already establishes FAIL. PASS is bounded to those source diagnostic contracts, not a claim of universal safety.
- **Contacts:** preserve each event's source, time and ground-wall, flight-wall, floor, ceiling or unclassified category. Accepted penetration count is separate. No legal wall or ordinary landing FLOOR contact alone forces FAIL. Ground contact positions are tested through the real public flight initializer; inadmissibility is reported without clamping or altering evidence.
- **Handoffs:** status uses recorded invalid-attempt and pose-discontinuity diagnostics. Accepted ground-to-flight counts derive from accepted takeoff counts minus initial takeoff. Total attempts remain null because there is no explicit attempt counter. At recorded ground contact, false eligibility indicates postponement under the inspected coordinator guard; probe rejection is never counted as a handoff rejection. Missing handoff diagnostics remain UNDETERMINED. Rejected count refers to source terminal invalid-handoff diagnostics, not hypothetical candidate poses.
- **Reproducibility:** PASS, FAIL or UNDETERMINED is independent of physical integrity. A reproducibility failure cannot erase a contact or manufacture a physical failure.

Rejected motor commands remain explicitly reported. A positive rejection diagnostic is classified FAIL because the existing feedback-session contract requires each outgoing command to be accepted and stops on rejection. This is an existing command-integrity convention, not a new physical rule. The classifier consumes trusted summary diagnostics rather than attempting to recover omitted or unrecorded raw events.

## Eight-case result

| Heading | First landing | Continuation | Integrity | Ground wall events | FLOOR events | Handoffs | Reproducibility |
|---|---|---|---|---:|---:|---|---|
| 0 | within 30 s (10.22 s) | completed | PASS | 0 | 4 | PASS | PASS |
| π/4 | within 30 s (6.84 s) | completed | PASS | 1 | 6 | PASS | PASS |
| π/2 | within 30 s (11.84 s) | completed | PASS | 0 | 4 | PASS | PASS |
| 3π/4 | within 30 s (6.84 s) | completed | PASS | 0 | 5 | PASS | PASS |
| π | within 30 s (6.84 s) | completed | PASS | 0 | 5 | PASS | PASS |
| 5π/4 | within 30 s (6.84 s) | completed | PASS | 0 | 5 | PASS | PASS |
| 3π/2 | within 30 s (11.84 s) | completed | PASS | 0 | 4 | PASS | PASS |
| 7π/4 | within 30 s (6.84 s) | completed | PASS | 1 | 6 | PASS | PASS |

Eight timely first landings, eight continuations, two headings with legal ground-wall contact, zero observed integrity failures and zero invalid handoffs under the documented metrics. These counts derive from source evidence, not hardcoded evaluator outcomes. Flight wall and ceiling event counts are zero. V1 still reports D for the two contact cases; the separate v2 result preserves contact while assigning integrity PASS.

## Canonical identities and reproduction

- Original J matrix: `ec419ea63d839eaf58a0451a86980eecb9c82ea472552ed04d53f341bc367468` (unchanged).
- V2 interpretation: `5259b301a52c812fbe61742b084651a12f6a5a763693c6ba5cbb97fcbefc67ea`.
- The eight source run hashes remain those in [the historical J report](initial_heading_robustness_v10_8j.md); each is also carried into v2. K's H1/H7 hashes and exact contact regression remain unchanged.

Given a retained source JSON with its appended `matrix_sha256`, classify without rerunning from `web/`:

```sh
node --import tsx --input-type=module <<'JS'
import {readFileSync} from 'node:fs';
import {classifyHeadingMatrixV2} from './src/lib/mixedFlightClassificationV2.ts';
import {flightHash} from './src/lib/engineeringFlight.ts';
const {matrix_sha256,...source}=JSON.parse(readFileSync('/tmp/neurofly-v108j-final-matrix.json','utf8'));
const result=await classifyHeadingMatrixV2(source);
console.log(JSON.stringify({result,sha256:await flightHash(result)},null,2));
JS
```

The temporary path is an example retained artifact, not a runtime dependency. If unavailable, regenerate the identical source with the existing J reproduction command; hash validation must pass before classification. Tests use that canonical runner, not temporary files. No generated trajectory is committed.

## Limits and next step

This is a classification of the documented source diagnostics. An unknown attempt count stays unknown; PASS does not imply every possible physical hazard was measured. No claim of biological autonomy, learning or continuous neural flight control follows. Ground HS/DNp15 values are model-computed; airborne neural activity remains unavailable. No browser/device check was performed because no UI or movement code changed.

One next recommendation: perform a focused real-browser review of walking, landing, takeoff and body posture/continuity before changing movement dynamics or adding biological mechanisms. Do not implement that review or any behavioral change in this phase.

Validation: 2 focused tests and 508 full-suite tests passed, zero failures/skips. Lint, typecheck, build and whitespace checks passed. Frozen V10.6B preflight verified unchanged source, all eight SWCs and the established runtime/configuration/visual/morphology hashes listed in the K report. Only the build-generated next-env.d.ts difference was restored; unrelated user work was preserved. Source/classifier tests and this assessment are the only new files.
