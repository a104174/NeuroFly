# Experimental Locomotion v0

This product experiment delivers Python-computed body displacement in the existing
A+C arena. It is **EXPERIMENTAL_KINEMATIC_ONLY**, not biological walking or a
connectome-driven autonomous animal. The browser displays a **precomputed
simulation replay**, never executes the scientific runner, and never makes motor
decisions. No existing canonical scenario is replaced.

## Model and scene contract

The independent module `src/neurofly/experimental_locomotion.py` reuses the
canonical JSON serialization/hash helpers, the approved V2-F manifest, the
thoracic pivot and display scale 0.30. It leaves the existing planar plant intact:
that older model consumes synthetic TTM commands in world_eq/ms, explicitly
excludes arena contacts, and is not a compatible product body/world contract.

Coordinates are Three.js presentation units: Y up, zero heading along +Z,
positive yaw toward +X. No millimetres or biological speed calibration is implied.
The model integrates `x[n+1] = x[n] + v sin(theta) dt` and
`z[n+1] = z[n] + v cos(theta) dt`. Heading is constant, angular velocity zero;
Y is the existing approved floor clearance. The fixed timestep is 0.02 seconds,
the horizon 8 seconds, with 401 ordered boundaries including the final state.
There is no outgoing interval beyond the final boundary.

`PROPULSION_SOURCE = ENGINEERING_ASSUMPTION`: constant configured speed 0.18
arena display units/s. `BOUNDARY_RESPONSE = ENGINEERING_CONTACT_MODEL`: clamp
at the admissible planar boundary, latch contact, then stop all translation.
No wall sensing, avoidance, reflex, random walk or automatic turn is implemented.
The conservative circular footprint is the maximum X/Z distance of the approved
asset AABB corners from the thoracic pivot, scaled by 0.30: 0.22857111060508783.
Chamber inner half extents are `(width-wall)/2`, `(depth-wall)/2`, using the
unchanged dimensions 2.4 × 1.22 × 0.86 and wall thickness 0.012. The admissible
anchor extents subtract this footprint. Every rendered corner remains inside the
walls, including pose interpolation. Invalid start placement, nonfinite inputs,
invalid geometry/time grids and excessive step displacement are rejected.
This intentionally conservative collision representation stops before the visual
mesh itself would touch a wall. It is not a leg-ground or force/contact model.

## Runs and causal control

Both conditions start at the approved thoracic anchor with heading pi/2 (toward
+X), identical floor height and random policy NONE. A computes the body path from
nonzero engineering propulsion; B changes only speed to zero. A travels
0.9654288893949121 display units (3.218 rendered long-axis extents), contacts the
X wall at boundary 269 / 5.38 seconds, then stays there. B has exactly zero
translation and zero contacts. Neither run contains neural, sensory, muscle or
motor-neuron activity. Source states from the DNg100 shadow experiments are not
used as propulsion or forces.

Neural steering is deliberately **NOT_MODELLED**. The current HS/DNp15 spatial
experiment accepts prescribed pose intervals and produces a shadow readout. The
frozen Course composition has a 50-ms abstract-orientation contract; neither
provides a validated arena-time rad/s motor mapping and seconds-long closed-loop
spatial plant interface. In particular `compose_neural_interval` advances HS and
DNp15 using the frozen 0.1-ms neural step while its yaw increment uses the supplied
interval duration. Passing a 20-ms plant interval directly would mismatch those
clocks; a separately validated neural-substep/observation adapter is required. A new causal adapter with declared time/gain semantics
and matched sensory/interruption controls is needed before displaying neural
steering. This iteration ships the explicitly authorized engineering fallback
without altering those kernels or importing a prerecorded neural trace.

## Replay and integrity

The compact asset `web/public/experiments/experimental_locomotion_v0.json` is
computed by Python, not a hardcoded React pose list. It includes complete
configuration, asset/geometry references, velocities, contact events, boundary
telemetry, distance, termination, engineering limitations and canonical hashes.
There are 802 total recorded boundaries, no connectome data or credentials.
The browser checks the pinned byte SHA-256, schema, scene/asset compatibility,
ordered timebase, finite poses, bounds, expected integration/contact semantics
and mode labels. Failed loading/integrity shows an error and leaves a static
specimen; it never generates replacement motion.

Canonical configuration SHA-256:
`1d1c8b7660de6004c5cee58203eb91d5b5edf01afa2e1c6be6bd3f92b192b764`

Canonical result SHA-256:
`d84a45a7ec4253ead4933529f95b2abee5c4cbae5f71448a6d03eef226cdd7d1`

Logical artifact identity:
`c33154916a33f3c88ba9d7421e0337e74b6def01eff674483427d4a0e8c64509`

Raw asset SHA-256 (not the logical ID):
`fc6d9882af59e63b4000d2426cc954342ce810ac2094f1e90f92d2d26cf2f893`

Regenerate to a separate diagnostic file, then verify the delivered file:

```sh
.venv/bin/python -m neurofly.experimental_locomotion --output /tmp/locomotion.json
cmp /tmp/locomotion.json web/public/experiments/experimental_locomotion_v0.json
.venv/bin/python -m neurofly.experimental_locomotion --verify web/public/experiments/experimental_locomotion_v0.json
```

Play/Pause/Reset and seek operate on scientific seconds, independently of render
FPS. The visual thoracic group receives adjacent-boundary interpolation. Displayed
position/distance match that transform; velocity/contact use the selected left
boundary, explicitly labelled in the inspector. Camera changes do not affect the
scientific clock. Inspect Fly follows the moving thoracic visual anchor, only
changing camera transforms; Overview continues to frame the complete chamber. Switching to a static mode cancels playback. Legs remain static;
there is no invented gait animation. Renderer diagnostics measure the actual
Three.js body group position as well as FPS/draw calls.

## Validation and limits

Focused Python tests use independent heading/displacement expectations, zero-speed
controls, all wall directions, grazing/repeated contact, deterministic replay and
rehashed semantic tampering. Frontend tests cover pinned bytes, time/pause/reset/
finish, interpolation, all transformed asset bounds and rejected invalid data.
Browser smoke must check actual WebGL group displacement, pause/resume/reset,
zero-speed control, end contact, mobile layout and console errors. Software
SwiftShader observations must not be interpreted as physical-GPU performance.

Canonical gates: `.venv/bin/python -m pytest`, Ruff check and format check,
frontend `npm run lint`, `npm run typecheck`, `npm run test` (with the project
virtualenv on PATH for existing scientific replay tests), `npm run build`, and
`git diff --check`. Existing five replay hashes/provenance, D2.2 bundle, Planar
and DNg100 shadow artifacts remain frozen. No physiological sign is assigned.
All prior UNKNOWN sign evidence remains unchanged. This validates a product
body/replay interface and explicit engineering mechanics only.

The next product capability is an isolated causal HS/DNp15 steering adapter with
matched sensory controls, retaining explicit engineering propulsion. It is not
implemented or authorized by this document.

Delivery validation: 1655 Python tests passed (one integration test deselected by
existing policy, two dependency deprecation warnings); 30 are the focused plant
checks. All 130 frontend tests, ESLint, TypeScript, production build, Ruff and diff
checks passed. Desktop and 390-pixel browser smoke confirmed actual Three.js body
position equality with telemetry, displacement above one rendered asset length,
pause/resume/reset, wall stop, stationary control, camera independence/follow,
mode switching and visible rejection of missing replay data. The available
renderer was SwiftShader, also selected by an unforced renderer probe; sampled
software observations were approximately 4–10 FPS, with overview rendering 313
draw calls / 55,830 triangles. These are not physical-GPU measurements. An existing
missing favicon generated HTTP 404; it is unrelated to replay or WebGL execution.
The protected deployment is verified separately after Git publication.
