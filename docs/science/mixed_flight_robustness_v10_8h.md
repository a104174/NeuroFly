# V10.8H — Mixed-flight robustness and browser evaluation

## Scope, declaration and evidence identity

The frozen comparison is `mixed_flight_heading_pair_v1`: A uses published sustained-v2 initial heading π/2; B uses heading 0. Both retain position [0, 0.11032208074629306, 0.12187743186950682], zero initial velocity, standard chamber, engineering flight plant, controller coefficients, 20 ms intervals, requested 60-second global horizon, 30-second per-flight cap, seed null and randomness NONE. The orthogonal heading was declared before paired execution; no alternative was selected after seeing B's failure.

The original sustained coordinator exposed no first-heading argument, although FlightEngine already supports a validated grounded pose. A tiny optional heading-only boundary now passes that public initialization through the first-flight wrapper. Its startup check compares the actual accepted frame with the explicitly declared initial heading before issuing the existing explicit TAKEOFF command. Later controller mathematics and all thresholds are unchanged. A canonical-heading startup is tested interval-by-interval against the legacy startup. Defaults and published G/E hashes remain exact.

Alternate runs use separately tagged evaluation result/configuration schemas and record the heading override and actual accepted initial state. The embedded base configuration is a historical controller reference; its initial pose is overridden only by the explicitly versioned evaluation field. Startup provenance/reason differs accordingly, while the first motor request remains TAKEOFF with vertical 0.8. Evaluation-specific error propagation retains the inner initial-flight failure instead of obscuring it as a later generic session error.

Reference source: `9ed2979736442a7b6157eec7d2eabda2cdb0a810`. Executed evidence comes from this phase's committed evaluator and additive initialization, not byte-identical historical source. The pair runner executes A twice and B twice and rejects unequal canonical repetitions. It uses the real existing engines and validated experiment authority; no synthetic canonical trajectory is used.

## Transition policy and stereotypy

Initial takeoff is an explicit Start action. Reactive yaw and forward input depend on accepted geometric clearances and avoidance hysteresis; altitude input depends on accepted altitude and vertical speed. Landing is armed by recovery from a boundary-avoidance response, followed by braking and accepted-state altitude/speed/contact/clearance checks. Each ground handoff follows accepted floor contact and starts a fresh zero-state HS/DNp15 episode, with null first ground sensory summary. Subsequent observations come from actual successive ground poses.

Re-takeoff requires cumulative accepted walking ≥0.18 units, at least 50 walking intervals, grounded floor height, zero vertical velocity, no unresolved wall contact, a valid destination flight footprint and sufficient ray/ceiling clearances. Fixed thresholds therefore strongly constrain episodes. The one-second minimum is necessary, never sufficient alone. Geometry and heading-dependent motion determine when all gates become true; the controller does not choose times from a schedule. The global 60-second horizon and local 30-second cap are termination guards, not motor-direction inputs.

| Baseline ground episode | Duration (s) | Path | Heading change (rad) | First path/interval gate (s) | Minimum flight ray clearance then | Re-takeoff clearance | Additional clearance wait (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1, 11.84–15.40 s | 3.56 | 0.6408 | +0.25130924 | 12.84 | 0.05318093 | 0.06016669 | 2.56 |
| 2, 26.56–27.58 s | 1.02 | 0.1836 | −0.18770406 | 27.58 | 0.06326275 | 0.06326275 | 0 |
| 3, 38.00–39.00 s | 1.00 | 0.1800 | −0.04372460 | 39.00 | 0.23702187 | 0.23702187 | 0 |
| 4, 45.84–49.26 s | 3.42 | 0.6156 | +0.24360906 | 46.84 | 0.05847354 | 0.06023709 | 2.42 |

Distances are presentation units. Episode 2 crosses the exact floating-point path gate at 1.02 s rather than 1.00 s. Episodes 1 and 4 wait because clearance is below 0.06 when their path/interval gates first pass.

Baseline takeoff-to-accepted-landing durations are 11.84, 11.16, 10.42 and 6.84 s; the fifth flight is incomplete at the 60-second cutoff. Their accepted paths are 1.1641798574, 1.1518792524, 1.0802817641, 0.4336298162 and 1.1929493084 units. Flight heading changes are +2.9920, +2.7880, +1.3464, +2.1216 and +2.8016 rad. All five accepted flying transitions occur 0.52 s after their takeoff requests, reflecting the fixed plant takeoff speed/acceleration/altitude condition. Repeated phase ordering and engineering thresholds are stereotyped; varying accepted geometry produces differing durations. None of this is evidence of learning or biological decision-making.

## Controlled outcome: deterministic but not robust across this heading pair

| Metric | A: heading π/2 | B: heading 0 |
|---|---:|---:|
| Actual accepted endpoint | 60 s | 30 s |
| Termination | DURATION_WINDOW_COMPLETED | FAILED: landing_not_reached |
| Sustained acceptance gate | passed | failed |
| Takeoffs / accepted landings | 5 / 4 | 1 / 0 |
| Ground duration / path | 9 s / 1.62 | 0 s / 0 |
| Flight ownership duration | 51 s | 30 s |
| Flying/landing start-state duration | 48.4 s | 29.48 s |
| Total horizontal path | 6.6429199986 | 0.2443806824 |
| Boundary steering responses | 8 | 1 |
| FLOOR contacts | 4 | 0 |
| Wall/ceiling contacts | 0 / 0 | 0 / 0 |
| Accepted bounds violations / rejected commands | 0 / 0 | 0 / 0 |
| Handoff position/time discontinuity | 0 / 0 | 0 / 0 (no handoffs) |

A's ground occupation is 15% and flight ownership 85% of its 60-second window. B spends its entire accepted window under flight ownership; it never reaches a ground episode. Zero handoff discrepancy for B is vacuous, not evidence of successful handoffs.

Geometric observations first differ at accepted index 0, time 0. The initial heading itself also differs at index 0 by construction. First motor scalars differ at interval 26, t=0.52 s, and accepted XYZ first differs at index 27, t=0.54 s. The first differing transition is A's LAND request at interval 458, t=9.16 s; its resulting accepted record is 459, t=9.18 s. B issues no corresponding LAND.

Over the common 0–30 s window, maximum XYZ separation is 0.9812001857 units at index 1054, t=21.08 s. Separation at the common final boundary 1500, t=30 s, is 0.3125578015 units. Individual terminal states have different times (A at 60 s, B at 30 s); their final positions must not be presented as a synchronized 60-second comparison. Observation/command comparisons use tolerance 1e-8, wrapped heading, XYZ Euclidean separation and explicit interval identities. Motor scalars exclude descriptive provenance and command identifiers.

B enters braking at accepted time 2.68 s and has 1,366 braking-start intervals (27.32 s). Its final outgoing observation has horizontal speed zero, altitude 0.3004906661 units above floor, and minimum ray clearance 0.0596505449. The required clearance is 0.06. It therefore cannot issue LAND, stays braking, and reaches the unchanged first-flight cap. The sustained recovery override applies only to resumed flights; the initial flight still uses the original TouchAndGoSession. This is a verified coordinator asymmetry and a narrow behavioral robustness limitation. No dynamics or threshold correction is implemented here.

Canonical hashes (each condition repeated identically):
- A: `92c034ca11d507d9e2759ed5c3241ecb6510a17737388cdfe5f8d3fa96bd272b` — exact published G result.
- B: `51d898df0ead8c73520928f9770516b65a1497a784803eb199b8ed816fab0fea`.
- Pair: `d8d8f34983dabb4c5892df450d27ed54b47a56bf7a95908c02429321ad02151f`.

The result establishes sensitivity and a failure under one controlled admissible initial condition. It is not a population-level estimate, proof of general autonomy, biological adaptation or neural flight validation.

## Browser evidence and classification

The existing cached Chromium/debugging-protocol workflow was reused against the published Production route `/visual-lab/arena`, using the existing sustained mode. No browser dependency, visual asset or renderer code was added. Screenshots were inspected for stable flight (2.68 s), boundary correction (4.78 s), landing (10.28 s), walking (12.38 and 14.56 s), and subsequent flight (16.66 s). The accepted walking positions changed from X/Z [0.51005131, −0.26331109] to [0.11822742, −0.27522463] at constant floor Y. The fly remained visible within the chamber, yaw direction changed near the boundary, and wing/leg states corresponded to flight/ground presentation.

Pause held the accepted step unchanged; Reset and behavior switching returned to step 0, time 0, ready state and the canonical spawn. One canvas and zero uncaught page exceptions were recorded. No confirmed body snapping, camera clipping or continuously flapping walking wings was observed in these samples. Code inspection confirms zero wing envelope when grounded and gait driven by accepted walking samples. Airborne yaw-only posture is an existing presentation/model limitation; preference for banking is not itself a demonstrated rendering defect.

These are sampled desktop software-rendered frames, not exhaustive continuous-motion, human perceptual, real-device, cross-browser or GPU/FPS acceptance. The alternate heading was evaluated headlessly and is not exposed as a UI preset.

## Telemetry assurance and one next step

Native evidence retains actual observations, complete motor commands, accepted poses, events and neural initialization. Flight neural values remain null/unavailable rather than fabricated zeros. All observed behavioral transitions can be traced to the recorded states and conditions.

An existing timing caveat remains: `sustained.landing_eligible` comes from the outgoing decision at state n, while `sustained.retakeoff_eligible` and ground-path accumulation are checked after acceptance at n+1. Their states are reconstructable from native/global evidence, but the flags do not carry separate eligibility-state timestamps. This report explains the distinction without altering old records. The pair's transition-result timestamp is likewise distinct from the motor-request timestamp.

Exactly one next step is recommended: a separately versioned correction that applies the same landing-clearance recovery contract to the initial flight as to resumed flights, with this heading-0 failure as its regression case. Preserve all published G evidence and compare the corrected version explicitly. Do not add randomness or new biological mechanisms.

For reproduction from `web/`:

```sh
node --import tsx --input-type=module -e 'import {readFileSync} from "node:fs";import {parseNeuralLocomotion} from "./src/lib/neuralLocomotion.ts";import {runMixedFlightHeadingPair,mixedFlightHeadingPairHashes} from "./src/lib/mixedFlightRobustnessEvaluation.ts";const a=parseNeuralLocomotion(JSON.parse(readFileSync("public/experiments/experimental_locomotion_v1.json","utf8")));const p=runMixedFlightHeadingPair(a);console.log(JSON.stringify({hashes:await mixedFlightHeadingPairHashes(p),comparison:p.comparison,baseline:p.baseline.metrics,variant:p.variant.metrics,variant_failure:p.variant.failure},null,2));'
```
