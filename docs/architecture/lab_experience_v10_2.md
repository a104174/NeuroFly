# NeuroFly Lab experience v10.2

Presentation and interaction composition on published baseline
`689fa8c55962ebe75de72732468dde1dd7d2d135`. Existing local logo changes are
preserved byte-for-byte. No scientific library, source asset, solver, camera
equation, motor projection or navigation policy is changed.

## Primary journey

Home → Enter the Lab → Play → observe → Pause → inspect → Resume or Reset.
`/visual-lab/arena` opens **Explore** directly. The header provides Home and the
existing `/scenarios` archive. The fly occupies a single real WebGL viewport.
The existing Inspect camera is selected initially so the organism is visible;
Overview, Side, Front and Top remain available through the camera selector.
Reset view uses the existing Overview default. Camera changes never move the body.

Play/Pause/Resume, Reset, simulated time and neural-influence state sit beneath
the viewport. At exactly 30 seconds, Explore again starts a new run from zero;
it does not extend or loop the scientific horizon. Settings and Simulation details
are native, initially closed disclosures. Display options and third-party credits
are also progressively disclosed. Opening panels does not change engine state.
Mobile places settings below the viewport instead of keeping a permanent sidebar.

## Reused authorities

- `ContinuousNavigationArena` retains its existing authority loading, engine ref,
  single `FixedStepClock`, requestAnimationFrame driver and 1500-interval stop.
  A new `presentation="explore"` branch changes only what it renders. Other
  callers retain `presentation="research"` and their original defaults.
- `ContinuousNavigationEngine` and HS/DNp15 dynamics are unchanged: 20 ms body
  intervals, 200 neural substeps of 0.1 ms, engineering propulsion and boundary
  response, default neural contribution enabled, default visual plane Z=+0.4.
- `FlyViewer` reuses `FlyViewerCanvas`, original scene, original GLB, OrbitControls,
  existing camera presets, and the original gait history/IK. `initialGait` defaults
  to false; only Explore passes true. The gait follows completed authoritative
  body samples and does not propel or steer the body. Renderer diagnostics can
  still be enabled explicitly. Gait failures are visible outside closed panels.
- Neural influence changes construct the same `neural`/`output_disabled` engine
  configurations as before. The existing reset-on-change semantics are disclosed
  beside the setting. Off still computes neural state and preserves engineering
  propulsion and boundary response; it does not disable a whole nervous system.
- Session export and semantic replay use the existing functions and contracts.

No new engine, model, trajectory, clock, dependency or WebGL canvas is introduced.
The product view receives actual snapshots; it never fabricates telemetry.

## Research preservation and mode classification

The original `ArenaCourseViewer` remains byte-identical. Its full interface is
mounted at `/visual-lab/arena/research`, linked from Simulation details. The
original selector used React state, not recording-specific mode URLs. Existing
scenario, experiment, cockpit, specimen and replay routes are not relocated.

| Classification | Existing capability |
| --- | --- |
| Primary product experience | Continuous Arena Navigation v3, presented as Explore |
| Secondary interaction | Existing camera inspection, gait display, renderer diagnostics, export and verified replay |
| Research/diagnostic | Interactive v2, neural contribution/steering comparisons, moving/independent visual stimuli, protocol scheduler, visual comparisons, motor bridge, engineering v8 and neural v9 flight |
| Historical/reference presentation | Static arena, Course replay, precomputed locomotion v0/v1, flight visual preview v7.1 |

No flight activity is added to the primary slice. Bounded research flight and
program controls remain available in the original interface; scripted previews
are not relabelled autonomous flight. DNg100/T1 authority remains unchanged.

## Accessibility and performance

One H1, named navigation, a skip link, native buttons/select/checkbox/disclosures,
44 px controls, visible focus, and reduced-motion CSS are provided. Phase changes
have a status announcement; the timer's live announcements are disabled. Small
viewport captions have an opaque dark backing for contrast against the floor.
No custom modal, focus trap, UI animation loop or telemetry chart is introduced.

The unchanged clock may report reduced real-time pace when its catch-up cap is
reached, particularly with software WebGL in headless Chromium. It does not change
the scientific timestep. A paused session freezes scientific time and gait while
camera orbit remains interactive. This is not a physiological gait calibration.

## Local validation

From `web`:

```sh
PATH="/path/to/NeuroFly/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 npm test
node --import tsx --test tests/lab-experience.test.ts
npm run lint
npm run typecheck
npm run build
```

The six new UI/composition tests cover default Explore, accessible phase controls,
closed disclosures, scoped gait defaults, unchanged body state during gait
derivation and retained research composition. Existing scientific tests are not
edited. Final frontend results: 338 passed, including these six; focused counts
overlap. Lint, typecheck, build and whitespace verification passed.

Chromium/CDP tested the real Home→Lab journey, one canvas, Play/Pause/Resume/Reset,
neural-output control, panel state preservation, camera selection, keyboard
Settings, reduced motion and widths 320/390/768/1024/1440 without overflow.
Six desktop/mobile screenshots are kept outside Git in the persistent local QA
directory. Renderer diagnostics confirmed six moving feet and 18 articulation
bones. A complete run stopped at step 1500 with 300,000 neural substeps. Its final
body/HS/DNp15 snapshot matched the unchanged engine with maximum absolute error
`4.6074255521944e-15`; this checks UI composition, not independent biological
validation or a new Python flight reference.

The real neural-output-disabled browser run also matched the existing engine
exactly at step 102 (distance 0.3672 model units, zero applied neural omega,
ongoing neural integration). Semantic replay reproduced the current state and
an actual browser download exported the unchanged v3 session schema. The research
route exposed all 15 original selectors with gait still off by default; the local
API supplied all five scenarios at `/scenarios`. The homepage remained independent
of WebGL. No critical application console errors were recorded. An initial
headless-browser process terminated during QA; the restarted final run completed
all checks and the full 30-second horizon.

All 218 recorded scientific/library/asset source hashes and the pre-existing
logo files were preserved. The full frontend suite includes existing neural,
navigation, gait, flight, parity, historical-hash and semantic-replay tests. The
full Python suite is not required or claimed. No Safari/Firefox acceptance or
formal accessibility certification is claimed. No commit, staging or deployment
is performed in this local phase.

## v10.2a — scoped visual polish

This refinement supersedes the initial Inspect framing and the longer persistent
sidebar described above. The scientific simulation and historical presets are
unchanged. `explorePresentation.ts` holds the product-only camera and palette;
`FlyViewerCanvas` and `ExperimentalArena` receive opt-in flags defaulting to false.

The default **Explore** camera uses a 50° vertical FOV, direction `(-.5, .35, 1)`
(normalized), distance `max(1.15, .9 / max(.05, aspect))`, and a fixed 0.2-unit
vertical framing offset above the existing visual anchor. The offset reveals
rear enclosure framing while keeping the fly in the lower central composition.
Portrait views gain distance rather than changing the organism's scale. Reset
view restores this product preset. Overview, Inspect, Side, Front and Top retain
the original camera equations. The product preset reuses the existing translation
follow of the accepted body pose with that constant offset; no new tracking loop,
look-ahead, smoothing, target control or body movement is introduced. Orbit bounds
are product-only; Inspect keeps its existing enclosure constraint.

The Explore floor, enclosure frames, acrylic tint, clear colour and backdrop use
cooler presentation colours. Modest fill/hemisphere light and a shadowless point
light separate the fly and its surroundings. Product environment intensity is
0.28; historical arena intensity remains 0.45. No geometry, floor height, collision
boundary, scientific coordinate, original texture or GLB byte changes. There is
no postprocessing, new texture, shadow-map pass or renderer dependency.

### Turquoise ring

The ring is `VisualStimulus0` in `ExperimentalArena.tsx`: the cyan geometric
landmark at X=+0.6, Z=`stimulusPlane`, Y=0.0015; its radii remain 0.015/0.027.
The second reference is at X=-0.6 and uses the original warm colour. These are
engineering annotations of the observer's geometric references, not a loading,
contact or camera artifact. The CPU observer in `interactiveNeuralLocomotion.ts`
uses declared landmark coordinates and accepted poses, not rendered pixels.

Explore therefore defaults these annotations off and exposes **Model landmarks
(annotations)** in Display & credits. The UI explicitly states that visibility
does not change sensory inputs. Coordinates, ring geometry, observer inputs and
research defaults remain unchanged. Browser diagnostics verify that the same two
world positions return when enabled and disappear only from rendering when off;
toggling them preserves the paused scientific boundary.

### Interface and validation

The persistent sidebar now contains one short description and its two existing
progressive disclosures. Numbered onboarding and the repeated instructional block
are removed. Slow pacing occupies a reserved compact status slot; its tooltip and
Simulation details distinguish simulation time from wall-clock time and retain
the fixed-step explanation. The original catch-up condition is preserved.

Seven additional tests cover camera bounds/context at multiple aspects, invalid
dimensions, historical preset isolation, reset composition, compact copy,
truthful pacing, annotation gating and single-canvas composition. Existing v10.2
coverage remains, with its initial-camera assertion updated for the new preset.
Scientific tests and historical fixtures are not edited. QA screenshots, temporary
scripts, measured browser results and preservation manifests stay outside Git in
`/home/l1tren/projetos/neurofly-assets/work/lab-v10-2a-20261023/`; they are not runtime
inputs. No Git publication or deployment is performed.

The older preservation manifest named 13 branding/source files; its quoted-path
handling had omitted the transparent PNG with an accented filename. This phase's
NUL-delimited inventory includes that already-known user-provided original too.
All 14 pre-existing branding/source paths are protected, including both original
PNGs, in addition to the 218 scientific/library/asset hashes.

Final v10.2a checks: 345 frontend tests passed (13 focused Lab tests included,
seven newly added), ESLint, standalone typecheck, production build and whitespace
checks passed. Chromium used 320/390/768/1024/1440 px, camera switches/reset,
orbit/zoom while paused, panel state preservation, reduced motion and orientation
resizing. Actual captures were reviewed against v10.2, including default/running/
paused/settings, Overview/Inspect and mobile camera controls. One canvas remained.
No critical application console errors were recorded before the deliberate
context-loss test; that test retained the explicit alert and reload action.

The current 30-second browser run completed 1500 intervals / 300000 substeps;
its final body/HS/DNp15 state matched the unchanged engine to
`4.6074255521944e-15`. A fresh output-disabled run matched exactly at step 102,
with 0.3672 units travelled and zero applied neural omega. Semantic replay,
all 15 research modes and the five real scenario catalogue entries were verified.

Rendering used ANGLE/SwiftShader software WebGL, not a hardware GPU. At 640×600,
a five-second sample measured 5.0097 wall seconds and 3.82 simulated seconds,
approximately 9 render FPS (rounded renderer counter), 310 calls, 55,782 rendered
triangles, 312 geometries and 13 textures. These are renderer observations, not
GPU-memory measurements or production performance guarantees. There is no
controlled hardware comparison against v10.2. The truthful pacing status remains
necessary; scientific timing was not accelerated to improve presentation.
