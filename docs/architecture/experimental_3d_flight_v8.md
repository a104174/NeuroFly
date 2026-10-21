# Experimental 3D Flight v8

## Classification and boundary

`ENGINEERING_KINEMATIC_FLIGHT`, separate from all MaleCNS neural experiments.
No aerodynamic forces, gravity, wing-muscle control, neural flight controller,
or sensory feedback. Explicit control inputs drive this plant; wing motion is
downstream presentation and does not produce lift. No scientific experiment
schema, IndexedDB record, replay hash or biological source is modified.

The historical v7.1 visual preview remains its original eight-second,
presentation-only vertical-offset demonstration. Its descriptor SHA-256 stays
`f175ede40fd15892d6089d446146b371a4534be048ffa45447a7cb5a740a51ff`.
The source V2-F GLB remains
`0502cb995d25b2f9d7b57eff0cf95a0c9cfd7f838e212e95b3895bb69c7e5238`.
Original surfaces, CC BY 4.0 attribution, thoracic anchor and .3 scene scale are
reused. No additional geometry, bones, textures or scientific source data.

## Coordinate and state contract

Y is vertical; +Z is forward at heading zero. Positive yaw turns forward toward
+X. The body anchor is the existing artist-selected thoracic presentation
anchor, not a measured center of mass. Initial heading is pi/2. Initial position
is the source anchor scaled by .3 plus `ARENA.flyOffset`, giving ground anchor
Y approximately .11032208074629306. Original feet clear the floor by .006.

`engineering_3d_kinematic_flight_v8` state at each completed boundary:
integer step, time, position XYZ, velocity XYZ, unwrapped heading (radians),
`grounded|takeoff|flying|landing`, state-entry time, active command ID, current
contacts and boundary events. These are engineering quantities in presentation
units, seconds and radians; they never masquerade as neural telemetry.

Legal transitions:

- grounded -> takeoff: one-shot TAKEOFF intent.
- takeoff -> flying: integrated altitude reaches .04 units.
- takeoff/flying -> landing: one-shot LAND intent or floor contact.
- landing -> grounded: floor contact; velocity becomes zero.

TAKEOFF outside grounded and LAND outside takeoff/flying are rejected/logged;
their scalar controls remain declared inputs. Grounded motion without takeoff
is rejected, with no displacement. No autonomous launch or landing keyframes.

## Inputs and numerical integration

Trial schema: `engineering_flight_trial_v8`, classification
`ENGINEERING_KINEMATIC_FLIGHT`; full pinned model configuration, initial state,
stop step (1..1500), ordered commands and presentation identity/preset. No
randomness. A command contains exactly `id, step, forward, turn, vertical,
intent`. Scalar commands lie in [-1,1]; intent is HOLD/TAKEOFF/LAND. Stable IDs
are unique, steps are distinct integers from zero through stop_step-1, sorted
in increasing order. Invalid, duplicate, off-grid and non-finite input fails.

Commands at boundary k apply to [k*.02, (k+1)*.02). Scalars hold until the next
command, while intent applies once. The resulting telemetry is available only
at k+1. Command/intent events retain the interval-start timestamp; threshold
and contact transitions use their completed-boundary timestamps.

Every integration step uses dt=.02 s, independently of rendering:

1. Apply a due command and its permitted state intent.
2. Update heading by `turn * .8 * dt` (zero turn command during landing).
3. Target horizontal velocity is `.18 * forward * [sin(heading),cos(heading)]`.
   Move the current X/Z velocity toward the target by at most `.45 * dt`
   units/s in vector magnitude; this includes acceleration and deceleration.
4. Vertical target is `.16 * vertical`; takeoff enforces at least .128 units/s;
   landing overrides it with -.12 units/s. Approach the target by at most
   `.32 * dt` units/s.
5. Semi-implicit update `position += new_velocity * dt`.
6. Clamp exceeded bounds and cancel affected velocity, then emit contact and
   state transitions. Floor contact ends landing and zeros all velocity.

New integrated velocity/position and changed heading are rounded on a declared
1e-12 engineering-state grid before contact clamping. Initial anchor and exact
contact bounds remain their original constants. This prevents sub-ULP runtime
differences in hypot/trig from changing portable engineering replay hashes.
The resolution is a v8 model parameter, never a modification of historical
scientific precision, timestep, solver or tolerance.

All parameters are engineering choices fixed before acceptance. No body
position list, wing phase or neural output appears in the integrator.

The enclosure uses actual width 2.4, depth 1.22, height .86, wall thickness .012.
Horizontal clearance radius .28 and upper clearance .24 are conservative visual
envelopes tested against original surfaces, full wing excursions and yaw.
Anchor bounds: X +/- .914, Z +/- .324, Y [ground_y,.614]. The lower bound preserves
the existing grounded posture. Floor, ceiling, X_WALL and Z_WALL contacts clamp
only penetrated axes and stop their velocities; no planar recovery controller
or biological avoidance reflex is used. Continuing outward commands can remain
clamped; contact events record onset rather than repeating at every boundary.

## Default twelve-second input trial

| Boundary | Input | Forward | Turn | Vertical |
|---|---|---:|---:|---:|
| 0..49 | HOLD, implicit zero | 0 | 0 | 0 |
| 50 / 1 s | TAKEOFF | 0 | 0 | .8 |
| 150 / 3 s | HOLD | .7 | 0 | 0 |
| 250 / 5 s | HOLD | .8 | .65 | .35 |
| 350 / 7 s | HOLD | .6 | -.35 | -.3 |
| 450 / 9 s | LAND | 0 | 0 | 0 |

The engine integrates ascent, forward motion, a climbing turn, a descending
turn and landing. The final state is grounded with zero velocity. Tests delete
forward/turn inputs to establish that the resulting path changes through the
plant, and verify independent acceleration/position equations at early steps.

## Wings, legs and playback

`engineering_flight_wings_v8` reuses the v7.1 pivots and rig math. Presets:
Normal 12 Hz (default); Slow Inspection 2 Hz. These are visual engineering
frequencies, not measured Drosophila parameters. The v7.1 historical preview
continues to use its own untouched 2 Hz law and descriptor.

`phase=2*pi*f*time`, `e=smoothstep(clamp(altitude/.04,0,1))` for active flight
states, with e=0 when grounded. Stroke=`.45*e*sin(phase)` about mirrored local Z;
spread=`.95*e` about mirrored local Y. No visual elevation offset is added:
the rendered body anchor equals the integrated XYZ state. Altitude-dependent
envelopes ramp continuously through takeoff and ground contact. Original stable
leg posture is retained, as in v7.1; planted-foot gait cycles never run in air.
Returning to v3/v6 and v7 restores their original independent presentation.

The body and wing clock uses completed 20 ms boundaries, sampling the 12 Hz
law at 50 Hz. Rendering may sample it less often: at <24 FPS a 12 Hz wingbeat
can alias, including apparent reversal or freezing. This does not change phase
or integration. No motion blur, duplicate surfaces or geometry trails are used.
Physical-GPU perception must be distinguished from SwiftShader evidence.

Live Play executes the plant with bounded fifty-step (one second) cooperative catch-up.
Excess wall-clock backlog is dropped; at slow rendering, simulation runs slower
than wall time while all scientific step/event timings remain exact. Pause
resets only the scheduler remainder. Seek reads recorded boundaries. Replay
reads stored computed frames until the recorded frontier, then resumes live
integration when there is an uncomputed interval. Reset starts the same inputs
at the same initial state. No neural solver is imported or invoked.

Inspect Fly follows the full XYZ body anchor, with a v8-only 75-degree FOV to
retain deployed wings when the camera approaches the enclosure ceiling.
Other arena cameras remain fixed,
showing position relative to enclosure/floor; the floor shadow follows X/Z.

## Export/import and semantic verification

`engineering_flight_result_v8`, classification
`ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT`, includes trial inputs, computed
frames/events, DURATION_COMPLETED or RECORDED_PREFIX, SHA-256 identities of
canonical inputs and result. Presentation preset is recorded separately within
the engineering trial. No IndexedDB scientific session record is written.
Preset changes are presentation inspection preferences, not plant commands;
the selected preset at export is applied across the whole exported replay.

Import validates known model/initial-state/presentation identities, strictly
validates the input program, independently reconstructs the recorded prefix,
and compares every field and digest to the imported artifact. Imported
positions never drive the model. Recomputed hashes cannot conceal changed
positions, velocities, states or contacts. Wrong scientific-session types,
non-finite data, invalid boundaries and configuration changes are rejected.
File size is capped at 4 MB; reconstruction is bounded by 1500 steps.

## Verification

Focused tests cover independent integration expectations, all boundary types,
rejected intents, deterministic 3/30/60 FPS playback schedules, prefix/full
export reconstruction and semantic tampering rejection. The real original GLB
is loaded in tests to verify wing-root attachment, full-specimen clearance,
unchanged other limb transforms and normal-preset seek/FPS independence.
Existing v6/v7/v7.1 and scientific checks remain mandatory.

## Local acceptance (2026-10-21)

Initial main and origin/main were both
`c84e9a0a659bdcd2c79649c3e122cb64e623e636`, with a clean worktree/index.
No staging, commit, push or deployment was performed. Five modified source
files and five new source/test/documentation files comprise this iteration.

Fresh canonical frontend gates: **283 tests passed**, ESLint, TypeScript and
production build passed. **55 focused Python tests passed** for wing descriptor
regeneration, genuine v7 motor-reference replay, runtime bundle, HS/DNp15 and
scientific status (two pre-existing dependency deprecations). Full Ruff lint
and format verification passed, as did `git diff --check`. No full historical
Python suite was run; no external MaleCNS fixture was created or regenerated.

Read-only D2.2 integrity verified all 74 pinned files. The original GLB, v6 rig
descriptor and gait source, v7 motor reference/projection, v7.1 descriptor and
preview component, v3/v5 runtime, v5.2 protocol and scientific session-library
sources remained byte-identical to the baseline. No scientific Python kernel,
raw/reference data, event schema or scientific configuration changed. Existing
frontend parity and saved-session regression tests passed unchanged.

Actual local production server and Chromium/SwiftShader at 1440x1050 and
390x844 passed the full scenario, without JavaScript errors. The default trial
has 601 boundaries, maximum altitude approximately .368, takeoff at 1 s,
flying threshold at 1.52 s, LAND intent at 9 s and ground contact at 11.44 s.
Final position is `[.639532893281,.11032208074629306,-.168962575892]`, final
heading `2.050796326795`, and velocity zero.

The actual browser export matched all Node reference frames and hashes exactly:
input SHA-256 `25af17966a60f9ed17267d6143cac86b783fd370ca09fef33ee49313177c9f61`;
result SHA-256 `8c8fc14e028a40fbc1aea526f253306bafc827b858a52495f0751168655528b7`.
This includes the explicit v8 state grid, not altered scientific tolerances.
Import re-executed inputs and validated all stored output; a position edit with
a recomputed result hash was rejected. Pause held exact body/wing transforms,
repeated seeks reproduced them, and historical playback left its 600-step
computed frontier unchanged. Rendered body positions matched engineering
telemetry, and both wing roots matched transformed descriptor pivots within
1e-11. Normal and Slow changed only presentation: phase ratio six, same body.

Screenshots captured takeoff, flight, turning, opposing 12 Hz stroke phases,
landing/rest, Side/Front/Top/Inspect cameras, and the expanded narrow UI.
At 390 px, document width=390 and viewer width=320; controls and full engineering
disclosure remained accessible. The v8-only inspection FOV retains deployed
wings in the desktop view; narrow inspection also supports orbit/zoom.

Normal's phase and actual mesh-transform progression are six times the 2 Hz
inspection preset. Only software rendering was available: approximately 3--5
FPS at desktop, with higher rates at the narrow viewport. This under-samples
12 Hz, so apparent aliasing is expected; no physical-GPU perceptual assessment
or physiological wingbeat claim is made.

Browser regressions: v3 advanced 45 body steps / 9000 neural substeps with the
18-bone gait active and no flight-wing rig. The v7 test at 1.94 s retained
foot elevation difference `.0007857500410935088` and knee difference
`.018372605582471557` rad; route-off=Base, sham=ON, and body/other five legs
were identical. Historical v7.1 at 3.12 s retained its original source and
stroke `.44911202779272225`.

Node CPU microprofile: full 600-step reconstruction median approximately
3.62 ms / 6.03 microseconds per step including history snapshots; pure wing
projection approximately .062 microseconds. Browser full import validation
reported 20 ms (1112 ms inclusive file-action/diagnostic synchronization in the
end-to-end harness). Wing rig updates measured 0--.1 ms at available timer
resolution. Equivalent settled v7.1/v8 switches both reported 313 draw calls,
311 geometries, 7 textures and 55,830 rendered triangles. No geometry/bone/
texture growth was observed through three alternating mode cycles.

Heap is not certified leak-free. The main acceptance session grew from
12.90 to 15.10 MB after collection. A separate four-round comparison against
the existing v7.1 preview showed approximately 1.0--1.1 MB retained per complete
remount pair in both controls and v8. This reproduces the pre-existing common
viewer remount observation; it does not establish a v8-specific increase or
prove the absence of a long-term leak. No broad renderer rewrite was attempted.

Evidence and harnesses remain outside Git in `/tmp/neurofly-v8/`; the product
does not depend on them. Outcome: `EXPERIMENTAL_3D_FLIGHT_LOCOMOTION_V8_LOCAL_VALIDATED`.
