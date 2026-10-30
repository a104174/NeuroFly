# V10.8E — Engineering state-dependent landing and re-takeoff

## Protocol declared before the first canonical run

Controller: `engineering_flight_touch_and_go_v1`, version 1. Configuration:
`neurofly_flight_touch_and_go_v1`; result: `neurofly_flight_touch_and_go_result_v1`.
The full configuration embeds the unchanged V10.8C reactive configuration: original chamber, conservative bounds, initial pose/velocity, plant identity, reactive coefficients and observation schema. The plant remains `engineering_3d_kinematic_flight_v8`. Intervals are 20 ms; maximum horizon is 1,500 intervals / 30 s; seed null, randomness NONE.

Landing is armed by an accepted boundary-avoidance recovery (`released` from the existing reactive controller), not by elapsed time or a waypoint. The controller then commands zero horizontal/turn input while retaining the existing altitude feedback. LAND requires accepted flying state, no contacts, horizontal speed ≤0.01 units/s, absolute vertical speed ≤0.02 units/s, altitude within 0.02 units of the existing 0.3-unit target, and minimum forward/left/right geometric ray clearance ≥0.06 units. These thresholds were fixed before the first trial; the first trial succeeded, so no alternate protocol or tuning was used.

The physical plant handles all braking, descent and contacts. In landing, it targets zero horizontal speed and −0.12 vertical units/s with its existing acceleration limits. Floor contact clamps position to its existing ground anchor and arrests velocity. This contact rule is kinematic, not a compliant mechanical impact model. Grounded state retains horizontal position and heading. No plant changes or private-state mutation were needed.

After accepted landing floor contact, a HOLD validates grounded state. A further grounded accepted boundary validates zero velocity, floor height and retained landing evidence before arming re-takeoff. The recorded trial has two grounded HOLD intervals (40 ms). Re-takeoff requires grounded state, zero velocity (numerical tolerance 1e-12), recorded floor-contact evidence, minimum horizontal ray clearance 0.06 and ceiling clearance ≥0.36 units. The plant receives one TAKEOFF request from the actual landing position. Initial takeoff is an explicit user Start request.

The new policy composes unchanged reactive decisions during initial takeoff and exploration, then resumes that same steering/altitude policy after the second takeoff. Physical plant state and controller phase are recorded separately. The finite verification stops after an exploration command from the second accepted flying state produces another accepted flying state. Duration limit is failure, with landing/retakeoff-not-reached diagnostics. Invalid observations, contacts, commands or state combinations fail explicitly. There is no walking or ground-model handoff.

## Accepted timing and results

Ordering is accepted state n → geometric observation n → controller decision/command n → plant interval n → accepted state n+1. Each interval records both observation time/index and resulting accepted state, controller phases, eligibility flags, transition reason, nested reactive decision when used, command source, contacts and commands. The result includes configuration, plant/GLB provenance, events, metrics and termination.

| Event | Boundary index | Simulation time |
|---|---:|---:|
| Initial TAKEOFF request / plant transition | 0 | 0 s |
| First accepted flying state | 26 | 0.52 s |
| LAND request / plant transition | 458 | 9.16 s |
| Accepted grounded FLOOR contact | 592 | 11.84 s |
| Second TAKEOFF request / plant transition | 594 | 11.88 s |
| Second accepted flying state | 620 | 12.40 s |
| Subsequent airborne exploration accepted; success | 621 | 12.42 s |

Landing and re-takeoff observation positions are exactly identical:
`[0.60641332557, 0.11032208074629306, -0.25062881669]`.
Grounded velocities are exactly zero and heading is retained. This differs from the initial position: the plant was not recreated or reset.

Measured horizontal distance: 1.1643598574 units; X/Z extents: 0.7794728968 / 0.3725330749 units. Altitude above floor: [0, 0.2997485800] units; vertical velocity: [−0.12, 0.16] units/s. Airborne duration is 11.34 s, counted from intervals whose accepted start state is flying or landing, excluding takeoff and grounded intervals. There is one avoidance response, one FLOOR event at 11.84 s, no wall/ceiling contacts, no rejected commands and zero accepted bounds violations. There are exactly two TAKEOFF commands and one LAND command.

Both canonical runs produced identical configurations, observations, decisions, commands, accepted states, events, metrics and termination `SECOND_FLIGHT_CONFIRMED`. Canonical result SHA-256:
`b9636f67ee6fe70559015399d1df9f60c3eef048e96793a3c840d1e135264894`.
Reference repository revision before additive implementation:
`c03b0f28daf45d7d6903b4fe768e75c08aa9a416`; reproduce using this phase's committed sources.

## UI, reproduction and limitations

Primary Lab → Reactive flight exploration → Landing and re-takeoff. Continuous exploration remains the default reactive behavior; ground exploration remains the primary default. Behavior switching unmounts the session; Reset creates a new session; pause freezes accepted state and clears scheduler remainder. Body pose and wings use the existing accepted-state mapping and flight presentation. No geometry, camera, GLB or renderer integration equations changed.

From `web/`:

```sh
node --import tsx --input-type=module -e 'import {runTouchAndGoVerification,touchAndGoResultHash} from "./src/lib/flightTouchAndGo.ts";const r=runTouchAndGoVerification();console.log(JSON.stringify({termination:r.termination,failure:r.failure,metrics:r.metrics,sha256:await touchAndGoResultHash(r)},null,2));'
```

This is an engineering behavioral prototype. Geometric queries and transition decisions are modelling assumptions, not measured fly sensory physiology or validated voluntary behavior. Wing articulation produces no lift. The separate HS/DNp15 ground model is not activated on landing, and walking is not integrated. Matched-phase state-variation tests demonstrate refusal of unsafe landing and unsettled/unverified re-takeoff; these unit fixtures are not experimental evidence. Canonical verification uses the real plant. Browser/device acceptance and GPU performance were not measured.

Existing V10.8B/C/D and v8/v9 scientific tests remain applicable; the V10.8C canonical hash is still
`9e0bc37b5f0e15407fcb9a37ca32b55602a67c3212b97e52d56c505c1f93b019`.
No frozen scientific sources, assets, experiment configurations or historical outputs are modified.
