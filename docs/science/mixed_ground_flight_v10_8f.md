# V10.8F — Explicit ground/flight handoff

## Protocol and ownership

`mixed_ground_flight_v1`, version 1, composes existing engines without merging integrators. Initial flight uses unchanged V10.8E touch-and-go feedback until its first accepted landing. The ground episode uses `LiveGroundSession` in `baseline_v10_5b`, with neural influence enabled, constant engineering forward drive, unchanged HS/DNp15 computation, wall response, sensory timing and 200 neural substeps per 20 ms body interval. Resumed flight uses the existing FlightEngine and reactive-flight-v1 takeoff/exploration policy. One engine owns each outgoing global interval.

The predeclared policy requests re-takeoff after at least 0.05 units of accumulated accepted ground travel and forward/left/right flight-bound ray clearances ≥0.06 units, grounded floor height, zero vertical velocity, and ceiling clearance ≥0.36 units. Maximum verification horizon is 1,500 global intervals (30 s); randomness NONE, seed null. The standard chamber is used throughout. Success requires an accepted flying interval after the resumed flight has already reached flying state. The first canonical run succeeded without threshold changes.

The reference revision before this phase is `6a5708a8f5f68f8e7f7c58b24f84013cc02d2076`. This phase's committed implementation is the execution source; it is not represented as a historical artifact. The versioned result includes the full initial-flight configuration, source authority/configuration identities, accepted initial state, native engine evidence, global observations, controller phases, handoff metadata, metrics and termination.

## Supported initialization and geometry

Ground initialization already accepts `LiveInitialPose` through the public LiveGroundSession constructor. Its protected ContinuousNavigationEngine validates destination bounds and exact floor altitude. Fresh ground episodes initialize six HS and two DNp15 states to zero; the first sensory summary is null because there is no previous ground interval. The next observation uses the first two ground accepted poses. No observer interval is fabricated across flight.

Flight previously admitted only the canonical spawn. An additive validated grounded-pose constructor argument now accepts XYZ, heading and planar velocity for empty-schedule mixed episodes. It checks finite fields, exact floor Y, zero vertical velocity, bounded planar speed and actual destination bounds. Historical trial validation/defaults remain unchanged; handoff-initialized engines cannot expose/export a legacy v8 trial artifact. No private state is mutated.

Both engines use Y up, heading zero toward +Z and positive yaw toward +X. The body anchor is exactly Y = 0.11032208074629306; no Y offset or heading conversion is applied. Ground X/Z limits are ±0.9654288893949121 / ±0.37542888939491215. Flight limits are ±0.914 / ±0.324, using the unchanged conservative 0.28 horizontal footprint margin. Both handoffs are validated against the destination envelope. Walking is required to stay inside the flight envelope for this bounded prototype; invalid positions fail rather than being clamped by the coordinator.

At landing, the plant has already accepted FLOOR contact and zero velocity. Ground starts at exactly that pose. Walking is kinematic and has its existing immediate forward-drive semantics; no new acceleration model is claimed for ground motion. At re-takeoff, XYZ, heading and the accepted planar walking velocity transfer exactly into flight, with vertical velocity zero. Flight acceleration integration then remains authoritative.

## Global time and neural interpretation

Each global boundary n selects one engine, uses that engine's observation/command contract, integrates one 20 ms interval, then accepts global boundary n+1. Source-local counters are retained separately. Resumed flight transition events and state-since times are explicitly translated to global time. Handoff construction consumes no extra integration interval. Position and heading differences are calculated from actual source and destination initial snapshots.

The global grounded contact label during walking denotes the planar floor constraint, not a new flight collision measurement. Native ground contact fields retain their own wall-contact meaning. Ground neural samples are model-computed and unavailable during flight. No continuous neural state, biological reset mechanism, neural lift or physiological handoff is inferred.

## Measured canonical result

| Event | Global index | Time |
|---|---:|---:|
| Initial takeoff request | 0 | 0 s |
| First accepted flying state | 26 | 0.52 s |
| Landing request | 458 | 9.16 s |
| Accepted FLOOR contact and ground handoff | 592 | 11.84 s |
| Walking endpoint / re-takeoff eligibility and request | 606 | 12.12 s |
| Second accepted flying state | 632 | 12.64 s |
| Subsequent airborne exploration; success | 633 | 12.66 s |

Landing / ground-start position:
`[0.60641332557, 0.11032208074629306, -0.25062881669]`,
heading 4.562796326795 rad.

Walking endpoint / second takeoff input:
`[0.5565137134830744, 0.11032208074629306, -0.25770641923892534]`,
heading 4.58307709160589 rad, planar velocity
`[-0.1784609272166282, 0, -0.023488240823474338]` units/s.

Actual walking covers 0.0504000000 units in 14 intervals / 0.28 s, with heading change +0.0202807648 rad. Total horizontal travel is 1.2489598574 units; X/Z extents are 0.7794728968 / 0.3840698282. Altitude above floor ranges 0–0.2997485800 units; vertical velocity ranges −0.12 to +0.16 units/s. Flying/landing start-state intervals total 11.34 s, excluding ground and takeoff intervals. There is one FLOOR collision event, no wall/ceiling events, no rejected commands and no accepted conservative-bound violations. Measured handoff position/heading discrepancies and global timestamp discrepancies are zero. Termination is `SECOND_FLIGHT_CONFIRMED`.

Two runs produce identical canonical configuration, engine ownership, native observations/commands, global trajectory, events, handoffs, neural initialization, metrics and termination. Result SHA-256:
`e630d4278fb9fc94e8dd736726a7049af9d85af5df28dcfb80be864b0f1282d5`.

## UI, verification and limitations

Primary Lab → Reactive flight exploration → Flight + ground exploration. Ground and continuous reactive exploration remain defaults. Validated ground authority is loaded through the existing primary Lab path. Pause freezes both active-engine progression and global accepted time; reset/behavior switching creates a fresh coordinator. Cleanup stops the owned ground session. Existing GLB, camera, body transform, wing and leg rigs are reused. Leg gait uses only accepted walking samples; airborne leg presentation is idle. Wing articulation produces no lift.

Tests match every native walking interval against an independent real LiveGroundSession initialized at the same landing pose, assert zero initial neural states/null first observation, verify exact handoffs and flight initial velocity, reject unsafe handoffs/insufficient displacement, check uninterrupted global boundaries, and compare repeated complete results. Synthetic invalid-state variations are unit fixtures only. Historical flight, ground and frozen science regression suites remain applicable.

For local reproduction from `web/`:

```sh
node --import tsx --input-type=module -e 'import {readFileSync} from "node:fs";import {parseNeuralLocomotion} from "./src/lib/neuralLocomotion.ts";import {runMixedGroundFlight,mixedGroundFlightHash} from "./src/lib/mixedGroundFlight.ts";const a=parseNeuralLocomotion(JSON.parse(readFileSync("public/experiments/experimental_locomotion_v1.json","utf8")));const r=runMixedGroundFlight(a);console.log(JSON.stringify({metrics:r.metrics,termination:r.termination,failure:r.failure,sha256:await mixedGroundFlightHash(r)},null,2));'
```

This is a short mixed engineering/neural-model prototype with a fresh ground neural episode. It does not establish continuous biological neural control, learning, physiological reset, realistic impact mechanics or long-running behavioral diversity. The existing flight floor-contact velocity-arrest rule and the ground kinematic forward-drive rule remain explicit limitations. No real-browser/device or GPU performance acceptance is claimed.
