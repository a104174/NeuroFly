# Independent Visual Stimuli v5

V5 extends the live v4 world-input adapter; it does not change the HS/DNp15
kernel, propulsion, boundary navigation or historical experiment contracts.
Select **Independent Visual Stimuli v5** in `/visual-lab/arena`. Choose an initial
preset before Play; use Start, Stop and Reverse A/B during the run. The cyan
circle identifies A, the gold diamond identifies B. Open Neural Response Timeline
for synchronized inspection. Save/reopen and Neural ON/OFF comparison use the
existing local library and simulator dispatch.

## Fixed world-input contract

The content-addressed policy is
`independent_visual_stimuli_v5_policy.json`, SHA-256
`8a273ccd822c88c95a2f7383632385cfdb919c4f3c349eebc046bead19889296`.
It was recorded locally before generating the new reference results; this is
not an independently certified preregistration chronology.

For each stimulus i, independently:

- `X_i = anchor_i + 0.08 sin(phase_i)`, anchors A `+0.6`, B `−0.6`, Z `+0.4`.
- `phase_i[n+1] = phase_i[n] + enabled_i × direction_i × 2π × 0.02 / 4`.
- Direction is ±1; units are presentation world units, seconds and radians.
- Stop preserves phase and direction; Start resumes that direction; Reverse
  changes direction even when stopped. Position remains continuous.
- Presets: both stationary; synchronized +/+ (the exact v4 case); opposing +/−;
  A moving +, B stationary. No parameter tuning follows the control results.

Requests apply at the next uncomputed body boundary, in recorded request order.
Each event stores stable stimulus ID, kind, sequence, step/time and old/new control.
Start/Stop already in the requested state are idempotent. Multiple reversals are
preserved. Disjoint landmark events do not change one another's phase. There is
no neural/body reset, heading command, random escape or programmed body route.

## Observation and clocks

V4's observer is reused with two independently computed old/new landmark
positions. It does **not** sum the landmarks into a single input. A maps to the
right proxy and B to the left proxy, with the existing polarity convention.
This is mathematical input encoding, not evidence for retinal fields or
hemisphere-specific biological responses. Opposing motion need not cancel.

For each landmark, self-motion holds its previous world position fixed between
body poses; external motion changes that landmark at the final body pose. Their
wrapped bearing changes determine the existing combined input and clipping.
The Timeline retains raw per-landmark self/external components and the combined
proxy inputs; no independently rescaled amplitude or fictitious neural signal
is introduced.

At body boundary n, observation uses the completed geometry interval n−1→n.
It is held for exactly 200 neural substeps of 0.1 ms during n→n+1. Engineering
neural steering and boundary steering remain separate. Body integration is
20 ms; geometry then advances independently. An intervention at n changes world
motion over n→n+1, observed at n+1; that interval's neural aggregate is available
at n+2. Timeline signals are plotted at their completion boundary, not earlier.
At time zero unavailable observations/readouts remain null. Seeking inspects
recorded boundaries without invoking the solver.

## Controls and numerical reference

`src/neurofly/independent_visual_stimuli_reference.py` reuses the frozen Python
neural transition, v4 relative observer and v3 body/contact plant. Generate the
six bounded 30-second references outside Git:

```sh
mkdir -p /tmp/neurofly-v5
.venv/bin/python -m neurofly.independent_visual_stimuli_reference \
  --output /tmp/neurofly-v5/reference.json
```

Cases are stationary, synchronized, opposing, single, opposing Neural OFF and
an opposing session with ordered independent interventions at 2, 4, 7 and 9 s.
Full 1501-boundary traces stay external; the frontend test fixture contains only
selected reference boundaries, including first contact. Comparisons use absolute
Python–TypeScript tolerance 1e−8, without changing solver accuracy. Synchronized
v5 matches v4 states, observations and poses exactly in the TypeScript regression.
The stationary-body fixture independently checks bearing-change input from A
while B and the fly remain still.

| 30-second condition | Distance | Contacts / recoveries | Contact seconds |
|---|---:|---:|---:|
| Stationary | 4.391117 | 3 / 3 | 5.60 |
| Synchronized | 4.449383 | 3 / 3 | 5.26 |
| Opposing | 4.445581 | 3 / 3 | 5.28 |
| A only | 4.447152 | 3 / 3 | 5.28 |
| Opposing, Neural OFF | 5.175043 | 2 / 2 | 1.24 |
| Independent events | 4.439476 | 3 / 3 | 5.32 |

All have 300,000 neural substeps, unchanged propulsion 0.18 and no penetration.
At sampled boundaries, synchronized versus opposing maximum spatial separation
is 0.0338021 at 22.64 s; maximum wrapped angular separation 0.1000576 rad at
20.72 s; maximum raw readout difference 0.00589215 yaw_drive_eq at 21.50 s.
Stationary versus synchronized maxima are 0.0599433 units at 25.12 s and
0.191948 rad at 25.16 s. These maxima are separate from current cursor values.
Opposing ON/OFF reaches 0.840557 units separation at 30 s and 2.95706 rad maximum
wrapped angular separation at 21.60 s. OFF still computes raw neural activity;
only its heading contribution is zero. Greater distance is not better biological
navigation. Pose-dependent observations diverge as the two bodies diverge.

## Persistence and integrity

V5 uses separate schemas `independent_visual_stimulus_event_log_v5`,
`independent_visual_stimulus_session_v5`,
`independent_visual_stimulus_comparison_v5` and `experiment_session_library_v5`.
IndexedDB remains at version 1; no migration or historical record rewrite.
Only initial configuration and external events are authoritative. Imports check
hashes, pinned configuration, ordered canonical events, old/new controls and
full semantic reconstruction. Recomputed hashes do not legitimize contradictory
geometry, neural summaries or model parameters. Comparison independently reruns
ON/OFF from the same parent and external schedule, preserving pending-event
semantics. Saved records retain compact inputs and dependent comparison metadata,
not duplicate full neural histories. Hashes detect corruption; they do not
establish authorship. Browser storage is origin-specific and may be cleared;
portable JSON remains available.

## Interpretation

This is `CONNECTOME_INFORMED_VISUAL_MOTION_RESPONSE` in a
`LIVE_BROWSER_MODEL_SIMULATION` with prescribed experimental world motion,
`ENGINEERING_PROPULSION` and `ENGINEERING_BOUNDARY_RECOVERY`. Selected MaleCNS
identities and all frozen authorities are unchanged. Neither geometric encoding,
readout amplitude nor travel distance establishes measured retinal response,
biological gait, calibrated speed, muscle forces, learning or autonomous animal
behavior. The observed differences are modest model effects; the UI does not
amplify or manufacture turning. Software-rendered browser FPS is not a physical
GPU performance measurement.

## Implementation verification

The compact reference manifest records source/model identities, fixed controls,
full external result hashes and the selected Python fixture identity. All six
30-second Python–TypeScript comparisons pass at the unchanged 1e−8 tolerance;
the largest selected numeric discrepancy in the independent profiling pass was
2.154e−14 (boundary angular rate). This is tested-window agreement, not a claim
of universal numerical equivalence or biological validation.

Node profiling measured 80–113 ms to compute 30 seconds for the six conditions;
a complete 1500-interval ON/OFF reconstruction took ~523 ms. Validated compact
library inputs occupied 4891 bytes versus ~3.10 MB for an exported session with
full body-level telemetry. Semantic restore took ~165 ms; validated record
creation ~427 ms. A full defensive-copy-plus-Timeline view-model measured ~15.5 ms;
normal live updates use only newly completed intervals. These are local profiling
measurements, not wall-clock guarantees for users' devices.

Local production-browser acceptance exercised an actual 13.30-second session
with A stopped at 2.30 s, then B reversed and A restarted/reversed at 3.30 s.
It completed 133000 neural substeps, a wall contact and a subsequent recovery.
Ten historical boundaries matched exported state, observations, Timeline values
and actual Three.js body/landmark transforms. Seeking caused zero cached-curve
redraws. Export/import, same-origin IndexedDB reload, paired reconstruction,
return to the source, reset, narrow layout and rejection of rehashed invented
landmark telemetry passed with no runtime errors. The old v4 portable session
also reconstructed with its original scientific values. SwiftShader measured
about 4 FPS; paired browser reconstruction took ~649 ms. Protected deployment
acceptance is recorded separately in external validation evidence.

The extended local browser check also reopened the original v3.2 input-only
library record without migration and exercised all four presets through live
Play/Reset. Update batches measured ~0.7 ms (maximum 1.7 ms); the bounded catch-up
limit activated under software rendering, preserving scientific step counts.
An isolated Node microbenchmark measured ~0.00070 ms per independent world update
and ~0.00065 ms per two-landmark observation (100000 iterations each). These
small-function timings exclude neural stepping, React and graphics work.

All 217 frontend tests, lint, typecheck and production build pass. An independent
Python reconstruction of the actual local browser export compared 46560 numeric
values over 665 intervals and the final state, including its recorded A/B events.
The largest absolute discrepancy was 1.819e−12 (floating-point interval-ms
arithmetic), within the unchanged 1e−8 tolerance. The source export contained
133000 neural substeps. Existing authority artifacts, all 74 D2.2 files, external
DNg100 dynamics/convergence and motor shadow traces, and Planar SHADOW_ONLY
retain their pinned raw hashes. The sole edit to the historical v4 observer
module is its TypeScript parameter type: runtime equations are unchanged.

Final pre-publication gates: 1707 Python tests passed, one integration test
deselected under the existing policy, two dependency deprecation warnings
(23m35s). Ruff lint and format checks, 217 frontend tests, ESLint, TypeScript,
production build and `git diff --check` all passed. No frozen kernel, historical
result, dependency, environment, hosting or storage policy was changed.
