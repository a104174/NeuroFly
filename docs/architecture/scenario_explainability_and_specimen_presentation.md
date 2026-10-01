# Phase 15 — explainable scenario playback and specimen presentation

Phase 15 improves presentation, not the scientific runtime. It starts from clean
`main == origin/main`, commit `e7bb923c7cadd6fb0d326187853d355a3333b989`
(Phase 14); Phase 13B is committed as `5d58fd7`. Initial scientific replay and
the 46-test frontend baseline passed before editing.

## Scientific authority

The unchanged Phase 14 `scenario_playback_v1` transport remains the only source
of scientific state. No API, model, scenario parameter, timestamp, artifact,
retinal registration or physics behavior changes. The original
`scenarioScene` interpolation and six-second presentation clock are unchanged:
telemetry selects an exact stored boundary while scene transforms interpolate
only adjacent authoritative body/object snapshots. Scientific duration stays
1.4 ms, dt 0.1 ms, 15 boundaries. Reset returns to boundary zero; completion
stops rather than looping. No idle animation, scripted response or local physics.

Canonical Phase 13B artifact remains
`55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b`.
Looming still changes relative-column radius 2→3, exposure 19→22, and DNp01
state; genuine spikes, actuator commands and body movement remain zero.
Baseline remains object-disabled, with empty exposure and stationary body.
Scientific closed-loop completion and movement remain separate statuses.

## Asset audit and decision

The real GLB, not the loading placeholder, is visible in completed runs:
`web/public/assets/fly/fly_visual_v1.glb`, authored by the project through
`tools/blender/export_fly_visual.py` / `assets/blender/fly_visual_v1.blend`.
It has 3,960 triangles, three materials, no textures, no skin and no animation.
Named body/eye/wing meshes are simplified ellipsoids; six legs are straight
cylinders. Its visual scale is presentation-only. Toy-like appearance is
primarily a geometry limitation, compounded by earlier teal materials, small
subject framing and ambiguous lighting. This is not validated morphology or
attachment geometry.

Choose existing-asset presentation improvements now, with a bounded Blender
asset requirement for future realism. No downloaded asset, license change,
anatomical code generation or rigging. GLB SHA-256 remains
`bc49dc056a9fee62779de38367e2f868eccdc4356f88412b72401cc149e0c49e`.

Scenario-only `ScenarioFlyVisual` clones nodes and assigns its own materials;
it does not mutate loader-cache materials or the existing artifact cockpit.
Brown rough nonmetal body, dark red faceted eye appearance, translucent wings,
warm key / cool fill / hemisphere lighting, contact-shadow cues, and closer
oblique framing materially improve readability. Faceting is a visual treatment,
not measured compound-eye geometry. Shadows and floor are display references,
not a contact model. The fly remains geometrically simplified, not photoreal.

### Bounded Blender asset requirement (not implemented)

One original or demonstrably licensed static fly GLB: segmented abdomen,
recognizable head/thorax proportions, antennae, anatomically recognizable but
nonmechanical segmented legs, thin wings with visual venation, and separately
named body/eyes/wings materials with texture or vertex-color detail. Provide
author/license/source manifest, visual-reference limitations, consistent
forward-axis/root origin and declared arbitrary display scale. Aim for a compact
static asset (roughly <=30k triangles, modest texture sizes), no armature,
animation, physics anchors or inferred biomechanical coordinates. Validate
loading, framing and stationary silhouettes in both presets before replacement.
Do not call decorative details empirically reconstructed morphology.

## Scenario story and scene

`/scenarios` presents Looming as the first demonstration without auto-running;
Baseline is explicitly CONTROL / ZERO STIMULUS. Each explains what the user
will see. The two supported scenario definitions still come from the backend;
the broader strategic taxonomy is unchanged.

The viewport is dominant. Looming contains exactly one solid current object,
one fly and a low-opacity dashed approach guide. The guide uses persisted
object snapshots and a presentation-only continuation toward the fly, not a
new trajectory equation. There are no opaque history spheres. Labels identify
the current object, approach direction and fly. A small exposure inset uses
the exact backend radius and exposed-body count; it explicitly denotes an
exploratory fixed-column projection, not a retina, geometric viewing cone or
calibrated receptive fields. Optional Scene guide explains the elements.
Baseline has no object, path or projection and prominently frames the fly.

The selected-boundary causal flow is WORLD → SENSORY → DNp01 → MOTOR → BODY.
It distinguishes exposed cells from evolving sensory response (boundary zero
has exposure but no sensory response yet). For the pinned silent run DNp01 is
SUBTHRESHOLD; actual backend membrane values and spike records are shown.
The DTO has no numerical threshold field: no threshold is invented or added,
and the explanatory label applies to the validated no-spike pinned run.
The primary DNp01 card shows the right record; both identities and exact values
remain in details. Values are labelled mV_eq/model coordinates as requested,
displayed unchanged, without claiming biological voltage calibration.

Motor primarily reads “No genuine motor command”, and body “Body stationary”,
with the causal reason. Full-run interpretation is labelled as such, separate
from current-boundary state. Final boundary displays RUN COMPLETE, not failed
escape. Six compact cards show scientific time, object distance, exposure,
DNp01, actuator and body. Provenance, both neural identities, LC4/LPLC2 sums,
all six scientific status flags and limitations remain in collapsed details.
No arbitrary activity percentages. No change to world_eq or dimensionless
command semantics. No frontend geometry-to-sensory calculation.

## Verification and performance

Frontend tests: 52 passed (46 historical plus six focused presentation tests).
They protect Baseline/Looming explanations, DTO-derived changing numerical
values, one current object, no local scientific calculation/idle animation,
and noncanonical changing authoritative positions. Existing clock, parsing,
pause/reset/scrub and authoritative interpolation tests remain unchanged.
Full Python: 979 passed, 1 deselected, two existing dependency warnings.
Ruff check/format, frontend lint/typecheck/build and diff check pass.

Actual Chromium smoke reviewed catalog, Baseline, Looming start/final and
390 px layout. Play advanced; pause held boundary 3; reset returned to zero;
scrub synchronized object, exposure inset, causal narrative and telemetry.
Mobile document width equalled 390 px (no page overflow); cards stack and
the legend was moved away from fly labels. Desktop screenshots reviewed:
`/tmp/neurofly-phase15-scenarios.png`, `...-baseline.png`,
`...-looming-start.png`, `...-looming-final.png` (untracked temporary evidence).
Scene labels are composed for the fixed cameras, not anatomical landmarks.

Simple headless development-browser diagnostic: mean requestAnimationFrame
spacing ~36.3 ms over 39 intervals during playback at 1440×1050. This is not
a calibrated GPU/FPS benchmark. A final optimized-production smoke measured
~41.0 ms rAF spacing using ANGLE/SwiftShader software rendering; this is a presentation
cadence diagnostic, not a hardware performance guarantee.
No heavy postprocessing: one existing small GLB, one object, one dashed line,
1024 shadow map, DPR capped at 1.5, demand rendering when paused. No new
scientific validation cost or playback payload fields.

The Three.js Clock deprecation originates in installed R3F 9.7's state factory,
which constructs `THREE.Clock`. Its integration accesses Clock-specific fields
and methods; Timer is not a local drop-in replacement. Do not monkey-patch,
suppress warnings or broaden Phase 15 into a dependency upgrade. Warning
remains nonblocking; no application Clock was introduced.
An additional removed-PCFSoftShadowMap warning was localized to Canvas's
default shadow setting. The scenario explicitly selects supported PCFShadowMap
(the same fallback Three was already using); no dependency mutation. This avoids
per-frame warning spam without altering scientific data or the displayed path.
Final production browser console contains only the known Clock warning, with
no application errors; play/pause and unchanged zero-result explanation pass.

## Status and next milestone

Phase 15 PASS: substantially clearer scene and explanation; scientific zero
movement preserved. Remaining visual realism is bounded by the current asset,
and physical/retinal calibration remains unavailable. No commit/push, no
generated science or screenshot files tracked.

Exactly one next scientific milestone: characterize the genuine subthreshold
DNp01 looming response under the existing pinned assumptions, without visually
motivated retuning. Separate response diagnosis from any later scientific
decision to alter parameters; movement is not a UX acceptance target.
