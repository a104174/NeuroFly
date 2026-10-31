# V10.8J — Initial-heading robustness matrix

## Question, declaration and method

Does the unchanged engineering controller `mixed_ground_flight_landing_recovery_v1` complete landing and mixed-mode continuation for eight evenly spaced initial headings? The hypothesis is that its existing geometric state feedback and landing-clearance recovery are sufficient in these cases; a failure would remain a reportable result, not a reason to tune it.

Reference controller source: `86487b577fdef9bab69b0414136f1b32158b3b8f`. Evaluation identity: `mixed_flight_heading_robustness_v1`. Before execution the matrix was fixed at Hk = kπ/4, k=0…7, two identical repeats each. Heading zero faces +Z, positive heading turns toward +X. All eight poses were admissible through the existing public initializer. No headings or positions were replaced.

All cases retain initial XYZ [0, 0.11032208074629306, 0.12187743186950682], velocity [0,0,0], standard 2.4×1.22×0.86 chamber, engineering_3d_kinematic_flight_v8 plant, 20 ms body intervals, 0.06 landing-clearance requirement, all recovery/steering/altitude coefficients, unchanged fresh-zero HS/DNp15 ground-episode policy, seed null and randomness NONE. Only initial heading changes. Controller, engine, UI, scientific configurations and historical results were not edited.

The maximum is 60 simulated seconds for every case, with first accepted landing assessed separately against 30 seconds. The existing initial episode also retains its own 30-second failure cap. Had that ended a run early, the remaining observation window would be reported as censored rather than simulated or extended. In this matrix every run actually reached 60 s.

The planned canonical experiment comprised **16 runs**, executed sequentially in repeated pairs. Complete native result configurations, observations, decisions, motor commands, recovery records, accepted trajectories, active engines, handoffs, neural initialization, contacts, metrics and termination were compared with the existing sorted-key finite-value canonicalization, and both hashes were checked. Automated regression tests repeated this experiment; two additional diagnostic replays inspected ground contacts. Those validation executions are distinct from the planned 16-run matrix.

## Eight-condition results

Recovery counts below cover active abort-braking overrides across the whole run, including resumed flights. A recovery episode is a contiguous block of override intervals; all observed blocks lasted one 20 ms interval. This duration is **not** the longer time spent exploring before safe landing becomes possible.

| Case / heading | First landing (s) | Recovery count | Takeoffs / landings | Walking (s) | Total horizontal path | Bounds violations | Repeated | Classification / terminal outcome |
|---|---:|---:|---:|---:|---:|---:|---|---|
| H0: 0 | 10.22 | 7 | 5 / 4 | 8.88 | 6.632910 | 0 | identical | A / completed 60 s |
| H1: π/4 | 6.84 | 2 | 7 / 6 | 13.66 | 4.465832 | 0 | identical | D* / completed 60 s |
| H2: π/2 | 11.84 | 3 | 5 / 4 | 9.00 | 6.642920 | 0 | identical | A / completed 60 s |
| H3: 3π/4 | 6.84 | 4 | 6 / 5 | 10.28 | 6.380290 | 0 | identical | A / completed 60 s |
| H4: π | 6.84 | 3 | 6 / 5 | 10.50 | 6.218846 | 0 | identical | A / completed 60 s |
| H5: 5π/4 | 6.84 | 3 | 6 / 5 | 10.36 | 6.383161 | 0 | identical | A / completed 60 s |
| H6: 3π/2 | 11.84 | 3 | 5 / 4 | 9.06 | 6.774399 | 0 | identical | A / completed 60 s |
| H7: 7π/4 | 6.84 | 3 | 7 / 6 | 13.76 | 4.403975 | 0 | identical | D* / completed 60 s |

**Aggregate:** 8/8 first landings within 30 s; 8/8 landings by 60 s; 8/8 genuine ground continuation and re-takeoff; 8/8 repeated pairs identical; 0 failed or incomplete windows. All eight activate recovery somewhere, but **only H0 requires initial-flight recovery**. Other activations occur after resumed takeoffs.

**D* means a conservative contact flag, not a numerical-invalidity assertion.** The helper's pre-execution safety screening flags any wall/ceiling contact as D. H1 and H7 each have one legal ground-wall contact later in continuation. Both completed their first landing at 6.84 s and still count toward the eight successful first landings. There are six A classifications and two D contact flags, no B/C/E cases. Counting only A would incorrectly report six first landings; the evaluator counts landing time independently from safety classification. It does not relabel these contacts as clean runs.

## Event timing, occupation and final state

All headings first reached accepted flying at **0.52 s**. “First sufficient” means the first accepted flying observation at/after initial recovery (if initial recovery occurred), otherwise the first accepted flying observation. It is not a new eligibility rule: avoidance release, braking, altitude and speed must also allow LAND. Missing initial recovery is represented as absent, not 0 s.

| Case | First recovery anywhere (s) | Initial recovery count | Active override duration (s) | First sufficient initial clearance (s) | First LAND request (s) | First walking episode (s / path) | First re-takeoff request (s) |
|---|---:|---:|---:|---:|---:|---|---:|
| H0 | 2.88 | 2 | 0.14 | 6.16 | 7.54 | 1.00 / 0.1800 | 11.22 |
| H1 | 38.40 | 0 | 0.04 | 0.52 | 4.26 | 1.02 / 0.1836 | 7.86 |
| H2 | 28.66 | 0 | 0.06 | 0.52 | 9.16 | 3.56 / 0.6408 | 15.40 |
| H3 | 18.22 | 0 | 0.08 | 0.52 | 4.26 | 1.00 / 0.1800 | 7.84 |
| H4 | 18.94 | 0 | 0.06 | 0.52 | 4.26 | 1.00 / 0.1800 | 7.84 |
| H5 | 18.26 | 0 | 0.06 | 0.52 | 4.26 | 1.00 / 0.1800 | 7.84 |
| H6 | 28.64 | 0 | 0.06 | 0.52 | 9.16 | 3.56 / 0.6408 | 15.40 |
| H7 | 38.54 | 0 | 0.06 | 0.52 | 4.26 | 1.00 / 0.1800 | 7.84 |

| Case | Flying/landing occupation (s) | Walking path | Explored X/Z extents | Minimum observed flying clearance | Final XYZ | Final heading / phase |
|---|---:|---:|---|---:|---|---|
| H0 | 48.52 | 1.598400 | 1.6789 / 0.6746 | 0.00483486 | -0.453075, 0.391942, 0.024100 | 4.293406 / exploring |
| H1 | 42.70 | 2.235176 | 1.7719 / 0.6657 | 0.01358768 | 0.227697, 0.338206, 0.152692 | 8.251955 / exploring |
| H2 | 48.40 | 1.620000 | 1.5641 / 0.5959 | 0.00605548 | -0.592864, 0.187763, 0.201313 | 13.883886 / landing |
| H3 | 46.60 | 1.850400 | 1.6117 / 0.6359 | 0.00621625 | -0.545123, 0.385650, 0.041883 | -8.291729 / exploring |
| H4 | 46.38 | 1.890000 | 1.6166 / 0.6372 | 0.00477662 | 0.249561, 0.300178, 0.184659 | 14.567348 / exploring |
| H5 | 46.52 | 1.864800 | 1.6116 / 0.6361 | 0.00729466 | 0.547222, 0.385650, 0.040761 | 14.575787 / exploring |
| H6 | 48.34 | 1.630800 | 1.5985 / 0.5984 | 0.00507222 | 0.589105, 0.393748, 0.210676 | -7.621052 / landing |
| H7 | 42.60 | 2.252600 | 1.8000 / 0.6663 | 0.01230924 | -0.087882, 0.290758, 0.193445 | -1.992631 / exploring |

Flying/landing occupation counts interval-start physical states and excludes takeoff. Takeoff intervals, walking and flying/landing together cover the global window. Final headings are the plant's unwrapped radians. Final velocities and full accepted final frames are retained in the reproducible matrix JSON. Minimum clearance is the minimum of forward/left/right engineering rays over accepted flying observations; values below 0.06 can legitimately trigger recovery and do not mean penetration. Ground X/Z travel uses its actual envelope, which differs from the conservative flight footprint.

## Recovery traces

Every activation below has accepted physical state flying and eligibility true, emits HOLD with forward 0.85 and turn 0, then produces a flying result at the next accepted boundary. Vertical output is the unchanged accepted-state altitude feedback. The compact JSON includes each activation's full preceding accepted state, phase, source-local command index, motor command, resulting accepted state, next observed clearance, first subsequent sufficient clearance and eventual accepted landing. The table reports the vertical motor component explicitly; no neural lift signal is invented.

| Case / context | Observation time (s) | Minimum clearance | Vertical command | Next clearance | First subsequent sufficient time (s) | Accepted landing (s) |
|---|---:|---:|---:|---:|---:|---:|
| H0 / initial | 2.88 | 0.05996405 | 0.24316964 | 0.05981775 | 6.16 | 10.22 |
| H0 / initial | 4.16 | 0.03847393 | 0.11422621 | 0.03824463 | 6.16 | 10.22 |
| H0 / resumed | 14.38 | 0.05984121 | 0.19874458 | 0.05952211 | 23.56 | 27.50 |
| H0 / resumed | 15.54 | 0.03902431 | 0.10413842 | 0.03878870 | 23.56 | 27.50 |
| H0 / resumed | 16.68 | 0.02567618 | 0.00968723 | 0.02552415 | 23.56 | 27.50 |
| H0 / resumed | 17.88 | 0.01666299 | -0.01179644 | 0.01659431 | 23.56 | 27.50 |
| H0 / resumed | 20.54 | 0.00756784 | 0.02271959 | 0.00754078 | 23.56 | 27.50 |
| H1 / resumed | 38.40 | 0.04032396 | 0.43363009 | 0.04011696 | 42.48 | 46.32 |
| H1 / resumed | 40.12 | 0.02261352 | 0.11213070 | 0.02249000 | 42.48 | 46.32 |
| H2 / resumed | 28.66 | 0.03263261 | 0.76484688 | 0.03245253 | 34.58 | 38.00 |
| H2 / resumed | 30.12 | 0.01958870 | 0.25656977 | 0.01949203 | 34.58 | 38.00 |
| H2 / resumed | 31.98 | 0.01063683 | 0.09958348 | 0.01058180 | 34.58 | 38.00 |
| H3 / resumed | 18.22 | 0.04272762 | 0.73938233 | 0.04248089 | 25.24 | 29.20 |
| H3 / resumed | 19.52 | 0.02676760 | 0.32980850 | 0.02660448 | 25.24 | 29.20 |
| H3 / resumed | 20.62 | 0.01790175 | 0.11965777 | 0.01782200 | 25.24 | 29.20 |
| H3 / resumed | 22.92 | 0.00877008 | 0.05167604 | 0.00873197 | 25.24 | 29.20 |
| H4 / resumed | 18.94 | 0.04464476 | 0.18941066 | 0.04439300 | 27.62 | 31.46 |
| H4 / resumed | 20.34 | 0.02720348 | 0.08777036 | 0.02707705 | 27.62 | 31.46 |
| H4 / resumed | 22.48 | 0.01379115 | -0.01263072 | 0.01374803 | 27.62 | 31.46 |
| H5 / resumed | 18.26 | 0.04084793 | 0.76484688 | 0.04063365 | 25.24 | 29.18 |
| H5 / resumed | 19.90 | 0.02336686 | 0.26896738 | 0.02323608 | 25.24 | 29.18 |
| H5 / resumed | 21.30 | 0.01432642 | 0.11270989 | 0.01427896 | 25.24 | 29.18 |
| H6 / resumed | 28.64 | 0.03420834 | 0.76484688 | 0.03403733 | 35.54 | 39.44 |
| H6 / resumed | 30.46 | 0.01874991 | 0.18788536 | 0.01866228 | 35.54 | 39.44 |
| H6 / resumed | 32.54 | 0.00967584 | 0.02446100 | 0.00962986 | 35.54 | 39.44 |
| H7 / resumed | 38.54 | 0.03907758 | 0.41534721 | 0.03884217 | 43.08 | 47.06 |
| H7 / resumed | 39.68 | 0.02573949 | 0.21931136 | 0.02558764 | 43.08 | 47.06 |
| H7 / resumed | 40.90 | 0.01658581 | 0.06225924 | 0.01651731 | 43.08 | 47.06 |

Next-interval clearance often decreases after an override; recovery is not an instantaneous displacement away from a wall. Existing reactive exploration subsequently changes heading and position before sufficient clearance and braking allow landing. Every activation in this finite matrix is followed by an accepted landing in its episode. No route, time-indexed steering, threshold change, future-state input or uncontrolled noise was added.

Command/observation time belongs to boundary n; the resulting accepted pose belongs to n+1. Global indices and episode-local command indices are different after handoffs. H0 reproduces the V10.8I sequence: activation at 2.88 s, resulting pose at 2.90 s, first sufficient clearance at 6.16 s, LAND request at 7.54 s and accepted floor landing at 10.22 s.

## Contacts, integrity and interpretation

Across all recorded intervals there are zero rejected commands, non-finite observations, non-finite accepted states, conservative-bound violations, invalid handoff attempts, illegal physical transitions, ceiling contacts, handoff position/heading discontinuities and global timestamp discrepancies. FLOOR contact-event counts equal accepted landing counts in each condition (4, 6, 4, 5, 5, 5, 4, 6). These counts are contact events, not persistent grounded samples. Failure strings and actual terminal endpoints remain available; unsuccessful unrecorded outgoing attempts cannot be inferred from an accepted trajectory alone.

The two X_WALL events are genuine ground events:

- H1: boundary 918, **18.36 s**, accepted X **+0.9654288893949121**, accepted ground path since landing **0.6583764671**.
- H7: boundary 920, **18.40 s**, accepted X **−0.9654288893949121**, accepted ground path since landing **0.6685996373**.

These are legal contacts at the existing ground solver's X boundary, with zero penetration. The destination flight X bound is only ±0.914; both accepted contact positions are therefore inadmissible for takeoff. The existing coordinator correctly rejects re-takeoff eligibility there and retains ground authority; it does not clamp the pose into flight bounds. The evidence does not establish an initial-flight recovery failure. It identifies a ground/destination-footprint interaction worth assessing separately; it does not prove that changing one threshold would prevent contact.

## Canonical evidence

Each hash below covers the complete unchanged V10.8I run result; both repeats have the same hash. H0 and H2 exactly match the published V10.8I hashes without provenance edits. Existing V10.8H original-controller evidence, including the heading-zero failure, remains protected by its unchanged regression tests.

| Case | SHA-256 of each complete repeated run |
|---|---|
| H0 | `75924ccb594bd49efa1d697d75b13cb9638be319f895047005f0da9f2bf40048` |
| H1 | `aaf3ea83c948295fb37c6ec3841affabd4f7ec9b7db196ed550a3a6d17c8c60a` |
| H2 | `fcfd8d492f8c3f2ca15a0c12b0095892087e29b7c84cd2e8350b6131ea07b43e` |
| H3 | `2910208f9f657d43b343117c28cca1dffbb3d02edb0e978136ae7bf851e306df` |
| H4 | `5435f966c8f300278b2cb5ff213aa28b5feb7a39a982f4524294429c4d412adc` |
| H5 | `71956cbc90bf5f5100b5168d3235ca345147a188a2fb522599f827166a29d92f` |
| H6 | `d20d3772a7f801ad0d9d9ba5d6cb65e64279c16d3771b8a6a4f69bcd1ea69214` |
| H7 | `c4b4064eeb1d5f8621a4fc3c68b55f8f641b742f53a265496fd7dc1da3eff59c` |

Compact matrix evidence SHA-256 (excluding its separately appended hash field): `ec419ea63d839eaf58a0451a86980eecb9c82ea472552ed04d53f341bc367468`. This summary has its own versioned evaluation identity; it is not a replacement or reinterpretation of historical artifacts. Actual evaluator source is identified by the implementing Git revision. The reference revision above identifies the unchanged controller baseline.

Reproduce from `web/` (full compact JSON includes the detailed metrics and activation/contact records; generated output is outside Git):

```sh
node --import tsx --input-type=module <<'JS'
import {readFileSync,writeFileSync} from 'node:fs';
import {parseNeuralLocomotion} from './src/lib/neuralLocomotion.ts';
import {runMixedHeadingMatrix} from './src/lib/mixedFlightHeadingMatrix.ts';
import {flightHash} from './src/lib/engineeringFlight.ts';
const authority=parseNeuralLocomotion(JSON.parse(readFileSync('public/experiments/experimental_locomotion_v1.json','utf8')));
const result=await runMixedHeadingMatrix(authority);
writeFileSync('/tmp/neurofly-v108j-matrix.json',JSON.stringify({...result,matrix_sha256:await flightHash(result)},null,2));
console.log(result.aggregate);
JS
```

## Validation and limitations

Focused tests verify enumeration, public initialization, exact I hashes, complete deterministic repetition, event extraction, local/global timing, missing events, landing classification, real contact counts and malformed/mismatched evidence. An initial test confused local motor indices with global accepted indices; the test and extracted source-local field were corrected without changing simulation. An initial typecheck invocation from the repository root failed because package.json is under web; canonical web gates were then used. The initial aggregate excluded contact-flagged cases from the first-landing count; that analysis bug was corrected while retaining the conservative contact flags and all native results.

Quality gates: focused evaluation tests **5 passed, 0 failed, 0 skipped** after the timing correction; complete frontend suite **504 passed, 0 failed, 0 skipped**. Canonical web lint, typecheck and build passed. Git whitespace validation passed. Frozen V10.6B preflight passed, including the eight SWCs and these unchanged pins:

- Runtime v3: `c5edf9edb0b1f08a0eb3e36808dd6ec25771be1bc575ce07e9cc3063aa6586cf`.
- Frozen V10.6B configuration: `dbc0f37db7a614c1a1076041f6319999bb86e7414b17a21992a8797e43f4a392`.
- Frozen fly visual manifest: `6a3d05441afd0c25ed8c2a98472acc35601f6e525db6f74d4eb16b0e32ab3b9e`.
- Morphology manifest: `c538f94a6a3ea02390bfcb09ee77226fe6f0418455c0794cdfedd64593070697`.

No new browser/device test was performed: no UI, renderer or dynamics changed. The prior Chromium check does not establish cross-browser, human visual, GPU or real-device acceptance for these six additional orientations. Eight deterministic starting headings in one chamber are engineering test cases, not biological specimens, a population estimate, learning or proof of general safety. Ground HS/DNp15 values remain model-computed; airborne neural activity remains unavailable. The fresh-zero ground policy does not assert biological neural reset. No LLM makes motor decisions.

Exactly one next step: assess the ground-to-flight eligibility corridor in the two contact-flagged cases, using the recorded ground and destination flight footprints to determine whether a separately versioned coordinator policy can avoid those ground-wall contacts. Do not change the protected ground solver or implement that correction in this phase.
