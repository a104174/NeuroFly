# V10.8B — State-feedback vertical flight verification

## Scope

This is a finite engineering verification of the existing `engineering_3d_kinematic_flight_v8` plant inside the primary Visual Lab arena. It adds a versioned full-command boundary and one deterministic altitude-feedback controller. It does not change the frozen V10.6 experiments, ground locomotion, neural equations, or `neuralFlight` behavior.

The trial is not a biological flight model, autonomous exploration, or evidence that a MaleCNS circuit commands vertical motion. The controller is an explicit engineering assumption. The plant supplies kinematic acceleration limits and arena contacts. The existing wing articulation is presentation only and generates no lift.

## Configuration and controller

Configuration identity: `neurofly_vertical_flight_verification_v1`.
Controller identity: `state_feedback_vertical_v1` (version 1).
Result identity: `neurofly_vertical_flight_result_v1`.

The initial accepted state is the existing grounded `initialFlightFrame`: position `(0, 0.11032208074629306, 0.12187743186950682)`, zero velocity, and heading `π/2`. The arena is the existing 2.4 × 1.22 × 0.86 presentation-unit chamber. `flightBounds()` gives X `[-0.914, 0.914]`, Y `[0.11032208074629306, 0.614]`, and Z `[-0.324, 0.324]`, subject to the existing conservative fly/wing clearances.

The target is 0.200 units above the plant ground anchor, with a ±0.010 altitude tolerance and a settled vertical-speed limit of 0.020 units/s. This places the target band wholly inside the existing vertical bounds. The verification lasts at most 15 seconds (750 fixed 20 ms intervals), has no random input (`seed: null`, `randomness: NONE`), and holds forward and turn commands at zero.

The user explicitly starts the trial from the grounded initial boundary. Takeoff uses normalized vertical command 0.8. During climb, the controller computes a desired vertical speed from accepted altitude error and accepted vertical velocity:

`clamp(1.5 × altitude_error − 1.2 × vertical_velocity, −0.16, +0.16)`

It normalizes that speed for the existing plant command. When an accepted state is inside the target altitude band and within the settled-speed limit, it issues one explicit `LAND` intent. The plant then performs its existing bounded landing descent and floor-contact transition. No waypoint, timer-driven phase change, mesh translation, or direct position write controls the flight.

## Timing and telemetry

At accepted boundary *n*, the controller records the accepted frame and bounds, calculates command *n*, and calls `advanceWithCommand` for interval `[n × 0.02, (n+1) × 0.02)`. The plant returns accepted frame *n+1*. Each record preserves observation and command steps/times, controller phases and transition reason, command origin, command values, and the resulting accepted frame. Plant events retain command and transition boundaries.

The full bounded result is available in memory with the configuration, plant and fly-asset identities, controller version, events, accepted snapshots, metrics, and termination reason. `verticalFlightResultHashes` calculates independent deterministic input and result hashes. The verification script prints only the compact configuration and result summary; it does not write the trajectory to disk.

## Verified run

Two identical runs of the declared configuration produced canonical identical inputs, observations, commands, accepted frames, events, metrics, and termination.

| Measurement | Result |
|---|---:|
| Takeoff command boundary | 0.00 s |
| First accepted `flying` state | 0.52 s |
| Maximum altitude above ground | 0.1901921685 units |
| Target condition | Reached: altitude `[0.190, 0.210]` and `|vertical velocity| ≤ 0.020` |
| Vertical velocity range | −0.120 to +0.128 units/s |
| Descent command / landing transition boundary | 4.52 s |
| Accepted grounded floor contact | 6.32 s |
| Airborne duration, first accepted `flying` through grounded landing | 5.80 s |
| Contacts / bound violations | FLOOR / 0 |
| Accepted intervals / termination | 316 / `LANDED` |

The maximum is at the lower edge of the declared tolerance band; the result does not claim that the exact 0.200-unit center was reached. The final accepted position and velocity equal the declared grounded state. No parameter was tuned after observing the run.

Reproduction command, from `web/`:

```sh
node --import tsx scripts/verify-vertical-flight.ts
```

The command runs two trials and fails if their canonical result differs. At validation, input SHA-256 was `c60faf14425d0e3d1368f05e42f1160c03f9babb65c5e277136161a3591b4b38` and result SHA-256 was `9146d3899c06c24fb21c022c11ce5dc0df2ef09690a5d918899985d073a3ab82`.

## Integration and limits

The primary Lab remains on ground exploration by default. Vertical flight is opt-in. The viewer receives `flightScene(acceptedFrame)` for body position and the existing V8 wing presentation for accepted time/state/altitude. Fixed plant steps are paced by `FlightClock`; pause resets pacing, and reset constructs the exact initial trial again. Rendering does not integrate body motion.

This demonstrates engineering state-feedback vertical motion only. It does not establish biological flight fidelity, autonomous obstacle response, neural lift control, gravity, aerodynamics, or six-degree-of-freedom dynamics. The whole visual chamber is not a calibrated biological environment. Browser/device rendering has not been manually validated in this phase.
