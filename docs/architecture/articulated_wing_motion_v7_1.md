# Articulated Wing Motion v7.1 — local engineering presentation

`Flight Visual Preview v7.1` is **ENGINEERING_FLIGHT_VISUAL_DEMO**. It is not a
neural experiment, scientific flight trajectory, wing-muscle signal or flight
physics model. It creates no session-library record, event log or scientific
telemetry. No MaleCNS, HS/DNp15, DNg100 or motor SHADOW_ONLY model is changed.

## Asset and reproducible hinges

Original V2-F SHA-256 remains
`0502cb995d25b2f9d7b57eff0cf95a0c9cfd7f838e212e95b3895bb69c7e5238`.
The deployed GLB contains separate `Wing.L` and `Wing.R` meshes with 1252 vertices
each, identity local transforms and the same geometry-root parent as
`Torso.Unseparated`. There are no authored wing hinges, skins or clips.
The external `fly_v2f_lookdev.blend` was opened read-only in Blender 4.0.2: both
wing names/counts and identity transforms agree; no armature or wing modifiers.
Its file SHA-256 is
`1f3496303736775c435aeb3ad7cbfc87bc0b45e964a40d4e1057922b15a23058`.
The runtime derivation uses the immutable **deployed GLB**, not an assumed
byte-equivalent Blender export. No Blender asset or original GLB is overwritten.

Generate the descriptor, without Blender or additional dependencies:

```sh
.venv/bin/python tools/exports/build_wing_rig.py
```

Output `web/src/assets/fly_wings_v7_1.json` has SHA-256
`f175ede40fd15892d6089d446146b371a4534be048ffa45447a7cb5a740a51ff`.
The anterior cap, Z > .115 asset units, is ranked by distance to actual torso
vertices; the mean of its ten closest wing vertices defines each visual hinge.
The resulting engineering attachment locations are:

| Wing | X | Y | Z |
|---|---:|---:|---:|
| L | -.108843148500 | .142743347585 | .128510651737 |
| R | .110000303388 | .141247807443 | .132486370951 |

Runtime/tests verify identity, hierarchy, vertex counts, rest matrices and pivot
proximity to source geometry. Independent tests also verify torso proximity.
These are artistically plausible attachment locations, not reconstructed
biological wing joints. The source is slightly asymmetric; symmetry is not
manufactured by modifying its surfaces.

Each original wing mesh is reparented under one new Group hinge. A compensating
negative pivot translation preserves the exact rest geometry. No wing surface,
material, vertex buffer, bone, texture, draw call or replacement GLB is added.
Animation changes the private instance's hinge quaternion only. Disposal restores
original mesh transforms/parent and removes the two groups. Shared loader assets,
geometry and materials remain immutable. Failed validation occurs before either
wing is moved and retains the original fly with an explicit visible diagnostic.

Original attribution retained: *Wildtype Male Drosophila Melanogaster*,
mlykouretzos, CC BY 4.0,
https://sketchfab.com/3d-models/wildtype-male-drosophila-melanogaster-0affd20207ca4c889bd7e1e513e04dfa .
NeuroFly adds engineering hinges only; V2-F surface/material authorship remains.

## State and deterministic time

Version: `articulated_wing_motion_v7_1`; coordinates +Y up, +Z forward.
An eight-second **presentation clock**, separate from all neural/body clocks:

| Presentation seconds | Explicit state | Envelope |
|---|---|---|
| 0–1 | grounded | 0 |
| 1–2.25 | takeoff | smoothstep((t−1)/1.25) |
| 2.25–5.75 | flying | 1 |
| 5.75–7 | landing | 1−smoothstep((t−5.75)/1.25) |
| 7–8 | grounded | 0 |

Smoothstep(u)=u²(3−2u). A pure function computes the pose at each timestamp:

- phase = 2π × **2 Hz** × (t−1).
- stroke = envelope × **.45 rad** × sin(phase).
- spread = envelope × **.95 rad**.
- quaternion = Rz(sign × stroke) Ry(−sign × spread), sign L=−1, R=+1.
- presentation-only vertical offset = **.18 × envelope** arena units.

The spread opens the original rearward wings laterally. Mirrored Z strokes lift
and lower both wings; the local matrices are appropriately different. The 2 Hz
frequency is deliberately legible engineering animation, **not a physiological
Drosophila wingbeat rate**. Ramps give continuous position/angle and first
velocity at state boundaries. Stable grounded wings are exactly at rest.
No cumulative quaternion rotation or render-count phase is used. Invalid or
out-of-domain time/configuration/pose is rejected; there is no extrapolation,
randomness or repeat after 8 s.

Play/Resume anchors an absolute monotonic elapsed presentation clock at the
current cursor. A skipped render changes only which analytic pose is displayed,
not the law. Pause freezes that cursor; Reset/Seek are deterministic pure
sampling. Resize/focus/camera updates do not advance time. No scientific solver
is called to seek. Presentation time is never labeled neural or motor-model time.

## Renderer integration and scientific boundary

The existing FlyViewer/FlyViewerCanvas, asset loader, material handling, cameras,
acrylic enclosure and lighting are reused. A clearly named
`FlightPresentationTransform` applies the vertical offset only within this mode.
It never writes `RecordedBodyTransform`, a replay pose, neural observation,
propulsion, collision or a session identity. There is no XY path. The maximum
hover fits inside the .86-unit arena height. Original legs retain a stable modest
rest posture; grounded walking cycles are not played in midair. Inspect Fly
tracks the visual thoracic anchor; portrait inspection uses a 75° FOV to frame
deployed wings. Original modes keep their existing camera. Diagnostic counters
move above the camera toolbar on narrow screens, leaving playback reachable.

Switching to normal navigation creates the original viewer with no wing adapter.
Its v6 gait and optional v7 motor projection retain their old contracts; the wing
preview neither imports them as scientific sources nor sends them feedback.
The original V2-F and v6/v7 descriptors/references are unchanged. No scientific
library schema or persistence migration is introduced. The disclosure is:

> Engineering flight visualization — wing motion is not neurally or
> aerodynamically validated.

Details wrap on narrow screens without truncation or hiding provenance. The
pre-existing 375 px global-header overflow is outside this feature's scope.

## Acceptance and limitations

Required local gates include full frontend tests, lint, typecheck, production
build, Python descriptor regeneration and existing motor-reference tests, Ruff,
read-only scientific authority/frozen-artifact checks and `git diff --check`.
Browser checks must inspect real wing roots, matrices/tips, rendered side/front/
top views, airborne/rest poses, pause/resume/reset/seek, 390 px, repeated toggles,
normal v3 six-leg gait and unchanged v7 controls. Evidence is kept outside Git.

This is a rigid-wing artistic first articulation, not elastic wing deformation,
aerodynamic lift, flight stabilization, flight navigation or neural wing control.
Leg flight posture is the existing specimen rest posture, not modeled recruitment.
Transparent wing sorting and software-rendered frame rate remain presentation
limits. No altitude or force is added to scientific state. Publication requires
separate operator authorization; this phase does not stage, commit, push or deploy.

## Completed local verification

Initial `main`, local/remote HEAD
`2e021e477865998e91e9b5798c5136d35d493111`, clean index/tree. Implementation is
four modified presentation files and seven new descriptor/generator/test/doc/UI
files. No staging, commit, push or deployment. Framework-generated agent files
and the generated next-env change were removed/restored to the original state;
no unrelated cleanup or configuration edit is included.

Fresh canonical frontend gates passed: **271 tests**, ESLint, TypeScript and
production build. Python: **55 focused tests** (new hinge regeneration, genuine
v7 motor-reference semantic replay, runtime bundle, HS/DNp15 validation and
scientific-status identities); two existing dependency warnings. Full Ruff lint
and formatting and `git diff --check` passed. Read-only integrity verified all
74 frozen D2.2 files, DNg100 recurrent/converged/motor SHADOW_ONLY artifacts,
Planar files, v5 policy/fixture and unchanged scientific/runtime authorities.
No full historical experiment suite or source-dataset generation was performed.
The GLB, v6 descriptor/gait, v7 reference/projection, v5 runtime, protocol and
session-library sources were also checked byte-exact against the baseline.

Actual local **production build** tested with Chromium/SwiftShader at 1440×1100
and 390×844. Both wings visibly articulate on the original surfaces. Close-up
Inspect Fly plus Side/Front/Top screenshots and video demonstrate attached roots,
airborne hover, opposing stroke extrema, landing and exact grounded rest.
Actual roots differ only by the declared vertical offset (tolerance 1e-12).
Pause/Resume/Reset/Seek, resize, repeated runs and 8-second no-loop termination
passed; same timestamps reproduce identical wing matrices. Document scroll width
is exactly 390 at viewport 390 with details expanded. Camera and playback controls
remain reachable and the diagnostics do not obscure them. No runtime JS errors.

Normal v3 resumed genuine six-leg gait with 200 neural substeps per body boundary
and no wing adapter. After returning from flight, v7 Base/ON/route-off/sham were
checked using actual articulated joint/foot transforms. Body and other five legs
match exactly; route-off equals Base and sham equals ON. At 1.94 s the original
foot-height difference is .0007857500410935817 presentation units and knee-angle
difference .018372605582471557 rad. The original motor-response asset is unchanged.

Resource measurements: **two added pivot Groups, zero added geometries, bones,
textures or draw calls**. Eight complete static/flight switches retained 313
calls, 55,830 triangles, 311 geometries and seven textures. Sampled wing apply+
diagnostic cost was 0–.2 ms (coarse browser timer); analytic pose-only Node CPU
microprofile was .011–.049 microseconds after warmup. Source GLB fetched once,
74.8 ms, no new GLB transfer. Software rendering measured 2 FPS during concurrent
acceptance work and approximately 4–5 FPS during isolated profiling, not a
physical-GPU benchmark.

The broader viewer lifecycle shows growing **JS heap**, despite stable renderer
resource counters: about 11.5→18.6 MB over eight static/flight remounts after GC.
The analogous static/v7 control (no wing adapter) shows similar growth. This
measurement does **not** establish an absence of general viewer-memory retention;
no wing geometry/skeleton accumulation was observed, and no unrelated renderer
rewrite was attempted. Keep this as a known profiling limitation/follow-up.

Local evidence (screenshots, video, matrices, controls, gate logs and provenance)
is outside Git under `../neurofly-assets/work/articulated-wings-v7-1/`.
Decision: `ARTICULATED_WING_MOTION_V7_1_LOCAL_VALIDATED` — engineering visual
presentation only, not published Preview acceptance or validated animal flight.
