# V10.8C — Engineering reactive flight exploration

## Scope and interpretation

V10.8C adds an opt-in, deterministic engineering flight mode to the primary Visual Lab. It reuses `engineering_3d_kinematic_flight_v8`; it does not change the ground model or V10.8B vertical verification. This is state-feedback autonomy in a limited engineering sense: the controller reacts to its current accepted pose, velocity, flight state and geometric clearances. It does not follow waypoints, replay a route, learn, or use random steering.

The chamber boundary query is an explicitly assumed engineering observation. It is not a biological visual sensor, optic-flow measurement, MaleCNS signal or neural activity. The controller is not a validated Drosophila flight circuit. MaleCNS morphology, computed neural activity, engineering motor commands, body dynamics and visual wing articulation remain distinct evidence and model categories. Wing motion is presentation only and generates no lift.

## Frozen verification configuration

- Configuration: `neurofly_engineering_reactive_flight_v1`.
- Controller: `engineering_reactive_flight_v1`, version 1.
- Observation schema: `neurofly_flight_arena_observation_v1`.
- Plant: `engineering_3d_kinematic_flight_v8`; fixed `0.02 s` accepted intervals.
- Environment: `neurofly_experimental_arena_v1`; chamber dimensions are display units (`2.4 × 1.22 × 0.86`). The plant's conservative usable bounds are X `[-0.914, 0.914]`, Y `[0.11032208074629306, 0.614]`, and Z `[-0.324, 0.324]`.
- Initial accepted pose: `(0, 0.11032208074629306, 0.12187743186950682)`, heading `π/2`; initial velocity is zero and the plant is grounded.
- Takeoff: explicitly requested by Start, with normalized vertical command `0.8`.
- Altitude: target is `0.3` presentation units above the floor. A bounded proportional/vertical-velocity feedback command uses gains `1.5 s⁻¹` and `1.2`; the existing plant limits and integrates the result. A `0.06` unit floor/ceiling recovery clearance is declared.
- Horizontal policy: normalized cruise command `0.85`; when forward clearance reaches `0.34` units, turn toward the side with more clearance using normalized turn magnitude `0.85`. The turn is held until accepted forward clearance reaches `0.5` units. Forward command is bounded to `[0.3, 0.85]` during avoidance. Equal side clearances use a deterministic positive-turn tie break. A wall contact re-evaluates the clearer side.
- Duration: at most `1500` intervals (`30 s`); seed `null`; randomness `NONE`.
- Termination at the duration limit is not a landing decision. An accepted-state or command integrity failure terminates as `FAILED`.

These values are fixed in the versioned configuration before the canonical verification. The mode has no internal obstacle sensing or collision geometry. Existing FlightEngine chamber bounds remain authoritative.

## Observation and interval ordering

For accepted state `n`, the observation helper casts three horizontal rays from the accepted X/Z position: forward `(sin(heading), cos(heading))`, left `(-cos(heading), sin(heading))`, and right `(cos(heading), -sin(heading))`. It also records vertical clearance to the plant's floor and ceiling bounds and accepted horizontal speed. Distances use the same presentation units as the plant. Non-finite, stale, altered or out-of-bounds observations are rejected.

The ordering is `accepted state n → geometric observation n → feedback command n → FlightEngine integration of interval n → accepted state n+1`. The command is recorded with the observation step and time; the resulting accepted state is one fixed interval later. The controller reads no interpolated mesh pose or render time. The renderer receives `flightScene(acceptedFrame)` and the existing V8 wing presentation mapping.

## Finite verification result

The in-memory `runReactiveFlightVerification()` was run twice with the same configuration. Both runs produced identical canonical results. No trajectory file is required or committed.

| Metric | Reproduced result |
|---|---:|
| Termination | `DURATION_LIMIT_REACHED` at 30.00 s |
| Accepted states / intervals | 1,501 / 1,500 |
| First accepted flying state | 0.52 s |
| Airborne duration | 29.48 s |
| Horizontal distance | 4.2889199485 units |
| Explored X range / extent | `[-0.8288403700, 0.7794728968]` / 1.6083132667 units |
| Explored Z range / extent | `[-0.3182470562, 0.3174032061]` / 0.6356502624 units |
| Altitude range above floor | `[0, 0.3004906661]` units |
| Vertical velocity range | `[-0.003200000, 0.160000000]` units/s |
| Boundary steering responses | 12 |
| Minimum observed ray clearance to conservative flight bounds | 0.0057529662 units |
| Wall / floor / ceiling contacts | 0 / 0 / 0 |
| Accepted bound violations / rejected commands | 0 / 0 |
| Final state | flying, within bounds |

The minimum ray clearance is measured from the accepted body reference point to the conservative usable boundary; the separate `0.28` unit horizontal body/wing margin to the visible chamber walls remains part of `flightBounds()`. It is not a measurement of clearance for every animated wing pose. The plant reported no wall contact and accepted no out-of-bounds position.

The predefined acceptance gates were horizontal travel `≥1.0` unit, X extent `≥0.75`, Z extent `≥0.25`, at least 2 steering responses, zero accepted bound violations, zero floor/ceiling contacts and positive airborne duration. All passed. An open-space and a near-wall observation at the same accepted step/time were also compared: the near-wall observation caused a nonzero turn and lower forward command; open space caused no turn. This demonstrates state dependence inside this engineering controller, not biological causality.

Canonical identities for this implementation's verification:

- Configuration SHA-256: `261a0dbdeb44283ddad24c2f50e6437b4a449a8fae637a1a9374b8e6d467427d`
- Result SHA-256: `9e0bc37b5f0e15407fcb9a37ca32b55602a67c3212b97e52d56c505c1f93b019`

## Reproduction

From `web/`, run the committed controller and plant locally:

```sh
node --import tsx --input-type=module -e 'import {runReactiveFlightVerification,reactiveFlightResultHashes} from "./src/lib/reactiveFlightExploration.ts"; const r=runReactiveFlightVerification(); console.log(JSON.stringify({configuration:r.configuration,provenance:r.provenance,termination:r.termination,acceptance:r.acceptance,metrics:r.metrics,hashes:await reactiveFlightResultHashes(r)},null,2));'
```

The returned result also contains all bounded per-interval observations, decisions, commands, accepted snapshots and plant events for programmatic inspection. It is generated in memory; this phase adds no persistent storage or export service.

## Limitations

This controller only queries the existing rectangular chamber bounds. It has no internal obstacle model, learned behavior, route planning, stochasticity, pitch/roll dynamics, wingbeat aerodynamics or neural lift command. Its “exploration” is deterministic boundary-responsive movement under explicit engineering assumptions. The 30-second endpoint is a finite verification cutoff, not autonomous landing. The metrics establish behavior of this implementation and plant only; they do not establish biological flight fidelity, learning, connectome-driven flight or population-level robustness. No browser/device acceptance or performance profiling is claimed by the automated verification.
