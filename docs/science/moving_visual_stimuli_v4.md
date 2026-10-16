# Moving Visual Stimuli v4

A live-browser, versioned extension of the v3 engineering body plant, with a
moving world evaluated by the actual HS/DNp15 model. This is
`CONNECTOME_INFORMED_VISUAL_MOTION_RESPONSE`, `ENGINEERING_PROPULSION`,
`ENGINEERING_BOUNDARY_RECOVERY`, `EXPERIMENTAL_MOVING_VISUAL_STIMULUS` and
`LIVE_BROWSER_MODEL_SIMULATION`. A prescribed world stimulus is not a prescribed
fly path, calibrated retina, physiological optomotor magnitude or biological gait.

## Fixed policy and geometry

The policy file was content-addressed locally before generating v4 results:
`65c334f0ddd3c769824d0449ed33da5e00c04c71fa56043091ebf2e23ff0a28b`.
This documents local chronology, not independently certified preregistration.
Amplitude, period, gain and numerical tolerances were not tuned after outcomes.

Two existing landmarks retain their identities, side assignments and Z=+0.4.
Their world X coordinates are `(+0.6,-0.6) + 0.08 sin(phi)`.
`phi_next = phi + direction * (2*pi/4) * 0.02`, with phase initially zero and
`direction` in {-1,0,+1}. Bounds are X [0.52,0.68] and [-0.68,-0.52], inside the
existing enclosure; Z remains outside the fly anchor's admissible Z extent.
Dimensions are presentation-world units, seconds and radians, not retinal or
physiological calibration. Period 4 simulated seconds resolves 200 body samples
per cycle; the 0.08 displacement is bounded relative to the scene's scale.
Positive/negative direction describes phase evolution, not a permanently positive
or negative X velocity of a sinusoid. Stopping holds the current phase/position.
Starting/reversing preserves position; velocity may change at the intervention.

## Relative observation and time

The old observer uses the same static world for both body endpoints. The v4
adapter instead takes both completed body poses and both landmark geometries.
For each landmark, let `b = L_before - P_before`, `a = L_now - P_now` in X/Z.
The existing clockwise bearing convention is
`shift = atan2(b_z*a_x - b_x*a_z, b_x*a_x + b_z*a_z)`.
Subtract body heading change in turns from `shift/(2*pi)`, multiply by the
existing 50 ms normalization horizon divided by interval milliseconds and the
existing R/L polarity, then clip the combined descriptor to [-1,+1].
Singular relative segments, ambiguous bearings/headings and nonfinite data fail.

Diagnostics separate self-motion (old landmark at both body endpoints) and the
additional bearing change of the landmark at the final body pose. These raw
terms sum to the combined raw descriptor within the bounded experimental
geometry; clipping is applied to the combined value only. This is geometrical
attribution, not independent physiological channels or new neural connections.

Boundary n ordering:

1. Apply the final pending direction request without changing phase or body state.
2. Observe the completed interval n-1→n; at n=0 there is no completed observation.
3. Hold that observation for exactly 200 old-state 0.1 ms neural updates.
4. Add the existing neural engineering yaw conversion to geometric boundary yaw.
5. Translate using the old heading, update heading, clamp/resolve contact as v3.
6. Advance world phase over the same 20 ms interval, then expose boundary n+1.

A command at n changes world motion over n→n+1. The changed motion is first
available to the neural model at n+1, not retrospectively injected at n. Paused
requests remain pending. Last request at a boundary wins; selecting the already
active direction cancels a pending change. Redundant noncanonical pending logs
are rejected. Reset restores initial body/neural state, phase zero and the
selected initial direction. Render FPS never defines either scientific clock.

## Reuse and isolation

`MovingVisualEngine` inherits the v3 plant and the v2 HS/DNp15 implementation.
The sole change in that existing solver file is the observation method's
TypeScript visibility from private to protected, permitting an explicitly
versioned observer. Its old observation and neural equations are unchanged.
Static v4 and old v3 produce exactly equal tested body/neural transition values.
The frozen Python neural kernel is called unchanged by the v4 Python reference.
MaleCNS v1.0 UUID 4b2087c0fbe046bfaf0d60bc970e3e5d remains pinned, with HS R
10015/10016/10023, L 10034/10181/10419 and DNp15 R/L 11215/12069. Propulsion 0.18,
steering gain 2.5, neural yaw clamp ±0.5 and engineering boundary policy are unchanged.
No DNg100 signal, muscle force, new synapse, random route or target controller.

## Sessions, comparison and compatibility

New explicit schemas: `moving_visual_stimulus_event_log_v4`,
`moving_visual_stimulus_session_v4`, `moving_visual_stimulus_comparison_v4` and
`experiment_session_library_v4`. Logs contain the exact initial config, source
pins, motion policy, initial direction, effective step/time transitions, pending
request and stopped duration. Exports include complete telemetry and separate
config/log/result/logical hashes; imports check hashes AND rerun the simulator.
Computed metric timestamps use the established 1e-8 model tolerance; discrete
boundary timestamps/counters remain exact. Numeric strings are not accepted.

The same IndexedDB database/version/store remains in place. Old v3.2 records
retain their original schema and dispatch to the original static v3 replay and
v3.1 pair functions. There is no database migration, rewrite or rehash of an old
record. V4 records store inputs, result fingerprints and dependent comparison
references; not full world/body histories. The existing atomic revision and
confirmed dependency-deletion policies remain. Opening a stored version also
updates the actual displayed mode; no old log is silently treated as v4.

ON/OFF share initial conditions, parameters and the external phase-change events.
Both compute neural responses from their own current poses and identical external
world geometry. OFF suppresses only neural-to-heading application, keeping raw
neural activity and geometric recovery active. Synchronized inspection reuses
one fly and existing markers/trails. World geometry is evaluated from recorded
phase/motion at the shared cursor, without extrapolating past the prefix.

## Matched results and controls

The independent Python reference reuses the frozen neural transition and v3 plant.
Five bounded cases use the fixed policy: static, moving, initially reversed,
moving with neural output disabled, and stop at 2 s/reverse at 4 s/start positive
at 7 s. A stationary-body analytical fixture demonstrates external observation
without requiring self-motion. This fixture does not imply locomotion.

| 30 s condition | Actual distance | Contacts / recoveries |
|---|---:|---:|
| Static, neural ON | 4.39112 | 3 / 3 |
| Moving, neural ON | 4.44938 | 3 / 3 |
| Reversed, neural ON | 4.50754 | 2 / 2 |
| Moving, neural OFF | 5.17504 | 2 / 2 |
| Motion-change events, ON | 4.45067 | 3 / 3 |

Moving versus static: maximum sampled separation 0.059943 units at 25.12 s;
maximum sampled wrapped heading separation 0.191948 rad; neural readout difference
at 4 s 0.00231752 yaw_drive_eq. Moving versus reversed: final separation 0.529239
units. Moving versus OFF: final separation 0.832494 units. These differences include
subsequent closed-loop/body/contact consequences, not isolated physiological gains.
Moving and static OFF bodies follow exactly equal tested trajectories despite
separate nonzero/different neural responses, excluding a direct world-to-yaw rule.

## Reproduction, performance and gates

`.venv/bin/python -m neurofly.moving_visual_stimuli_reference --output /tmp/v4/reference.json`
produces recoverable full external traces plus a bounded selected-boundary fixture.
Create the output directory first. Fixture and tests are in web/tests; no full
trajectory, scientific dataset or credentials enter Git. The compact reference
manifest records policy/source/output identities and deterministic reproduction.

Read-only Node profiling of 30 s reported ~82–98 ms for ON model computations,
with 300000 neural updates each; this is not a physical-GPU benchmark. Live
rendering retains bounded catch-up and may run slower than wall time on SwiftShader.
UI updates occur per body batch, never per neural substep. Two simple world rings
use the mathematical world positions; no additional fly GLB is introduced.

Validation covers independent analytical geometry, no false motion, self/world
attribution, exact static compatibility, all five Python/TypeScript conditions,
continuity and no-look-ahead timing, bounded contacts and recovery, neural-off
causality, canonical event rejection, semantic/rehashed tampering, old saved-record
compatibility, local persistence, comparison and responsive browser interaction.
All scientific interpretations remain limited to this uncalibrated model.

Pre-publication gates: 1702 Python tests passed, one existing authenticated
integration deselection and two dependency deprecation warnings; 192 frontend
tests passed, with 11 focused v4 tests also passing after integrity refinements.
Ruff lint/format, frontend lint/typecheck/build and diff checks passed. All 74
D2.2 pinned file hashes verified. No historical scientific artifact was regenerated.

Local browser acceptance used an actual 12.30 s session with stop at boundary
105 (2.10 s) and reversed motion at boundary 215 (4.30 s). It executed 123000
neural substeps, encountered/recovered from a wall, preserved state across events,
and reproduced after library reload. Both rendered landmark positions matched
the model. All 616 boundaries of each reconstructed ON/OFF world and the original
completed intervals independently matched Python within 1.819e-12 (limit 1e-8).
The session used 4507 bytes of IndexedDB input metadata; save/validation took
~390 ms locally. A genuine old v3.2 stored record reopened and exported with its
original identity, without a migration. Desktop and 390 px layout, pause/resume,
reset, event replay, comparison and rehashed corruption rejection passed with no
runtime errors. The browser harness resumed from exported evidence after a
server restart removed an old temporary fixture; no model correction was needed.
SwiftShader reported ~5 FPS; this measures software rendering, not hardware GPU
performance. Protected deployment acceptance and evidence are recorded separately.
