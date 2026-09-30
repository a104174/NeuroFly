# Phase 12A — first body/world plant architecture

## Decision and scope

Select **an exploratory planar kinematic body plant**, driven by common-mode
Phase 11B actuator commands, with one explicit model-space speed gain. Phase
12B must execute body-position trajectories, not create another metadata layer.
No mass, force, articulated legs, vertical flight, contact solver or frontend
physics. This is an assumption-labeled path toward world interaction, not
predicted Drosophila takeoff mechanics.

Phase 12A changes documentation only. Phase 11 is complete as functional
routing; neither the production closed loop nor interactive scenarios exist.

## Repository gate and source replays

Started clean on `main` at `68e3de4d13e4c2fd71c79b11bc7666a72a8d8efd`, equal
to local `origin/main` (no fresh remote fetch). Commits for 11B, 11A, 10C and
10B are present; initial diff check passed. Required offline replays passed:

| Source | Identity |
| --- | --- |
| 11B actuator | `478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40` |
| 10B activation | `4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb` |
| 9B electrical | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` |
| 7O genuine sensory execution | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` |
| 8C genuine sensory→TTMn adapter | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` |

7O full numerical replay used existing `execute_311` and canonical source loading,
then compared stored config/result; no generation or replacement. 8C full
replay re-extracted `reference_bilateral` events and reconstructed motor state.
11B/10B/9B replay validates established upstream ancestry unchanged.

## Genuine production-path reality: two distinct blockers

Repository truth confirms **35/35 Phase 7O conditions have zero DNp01 spikes**.
Phase 8C reference condition has zero adapted events and mapped motor inputs.
TTMn 800146/R and 804642/L each have 15 boundaries, 0–1.4 ms, all exactly zero.
Subthreshold membrane/drive is not converted into a substitute event.

The stronger statement “persisted production TTM activation is zero” is not an
executed downstream result: there is **no canonical production composition into
the later actuator chain**. `synthetic_ttmn_output_rule.py` consumes the pinned
8B synthetic artifact; 8O validates that 8N synthetic source. The subsequent
8Q/8W→9B→10B→11B canonical artifacts inherit synthetic fixtures, not 8C.
Consequently distinguish:

- Verified genuine execution: 7O→8C is valid and silent.
- Hypothetical unchanged downstream zero-input propagation: would remain zero
  under current model forms, but has not been persisted as production activation.
- Missing production composition: 8C output semantics are not connected through
  the later fixture-pinned contracts into 11B.

Do not splice the 1.4 ms production horizon into the 8 ms fixture horizon,
manufacture ancestry, relax historical source checks, or retune neural parameters
in Phase 12. Status choice is `PRODUCTION_PATH_NOT_CONNECTED_TO_ACTUATOR`, while
explicitly retaining the verified zero-output finding for its existing prefix.

12B's nonzero demonstrations are **SYNTHETIC_MECHANICS_VALIDATION**. They are
not autonomous sensory/connectome-driven behavior. Passing plant tests cannot
resolve either the zero-spike or production-composition blocker.

## Backend, frontend, world and asset audit

Inspected simulation, sensory/column execution, motor adapter, actuator/result/
replay modules, HTTP/experiment API, dependency manifests, frontend client,
playback, cockpit/scene, visual loader/layout, Blender pipeline and actual GLB.

| Area | Existing implementation | Consequence |
| --- | --- | --- |
| Backend simulation | Deterministic numerical experiment runners and state-boundary arrays; neural LIF default dt 0.1 ms. No world/body state or plant integrator. | Reuse timing, validation, canonical serialization and artifact conventions, not neural equations as mechanics. |
| World/environment | Scalar analytic looming stimulus and synthetic anatomical relative-column stimuli; no arena/object registry, body pose, world update loop, contacts or physics engine. | Existing looming geometry is stimulus generation, not embodied world dynamics. |
| HTTP/transport | FastAPI read-only persisted experiment/timeline/body/spike/event/morphology/connectivity routes. No scenario stepping API, mechanics snapshots or live WebSocket/SSE simulation stream found. | Future interactive runtime/transport must be explicit; do not mistake the current playback API for a closed-loop runtime. |
| Frontend | R3F stationary fly plus presentation-only looming/pathway overlays; playback controls select persisted data by time. | No contradictory frontend mechanics authority. Playback wall time advances the viewer, not a physical simulation. |
| Asset | Actual GLB: 14 nodes, 13 meshes, zero skins, zero animations; named static L/R front/middle/rear legs. No articulated joints, bone rig or validated pivots. | Articulation is not a prerequisite for first body translation. Visual nodes are not mechanical attachment data. |
| Coordinates | Numerical times and neural/anatomical coordinates exist; frontend +Y up, +Z forward, −X left with normalized presentation scale. | Define separate model-world coordinates; visual scale/height/camera must not become physical plant parameters. |

The GLB is a project-created static stylization, long-axis normalized to one
asset unit. Its current `[0,0.78,0]` placement and scale 2 are presentation
settings. See [asset pipeline](../architecture/blender_asset_pipeline.md) and
[scene composition](../architecture/scientific_scene_composition.md).
No rigid-body/contact engine or conflicting existing plant was found.

## Five candidate architectures

| Candidate | Benefit | Free assumptions / blockers | Assessment |
| --- | --- | --- | --- |
| A. Actuator-space only | Minimal, preserves side channels | Any extra extension state duplicates/filters existing commands; body never moves | Too conservative after 11B; fails body-state milestone. |
| B. Kinematic body | Deterministic displacement of an observer/body reference point; useful for later relative-object sensing | Model-space gain, common-mode rule, fixed direction, initial coordinate | **Select**: smallest useful body-state slice, no force claim. |
| C. Dynamic model-space | Position/velocity memory and coast/decay could enrich scenarios | Acceleration gain, velocity state/initialization, damping/tau; physical meaning still absent | Defer inertia until a scenario demands it. Adding another unidentified filter now is unnecessary. |
| D. Articulated-leg kinematic | Could expose extension geometry before body motion | Rig, joint axes/pivots, angle mapping, foot constraints missing | Not ready; fabricated anatomy would be required for a biological interpretation. |
| E. Physical rigid body | Could simulate SI motion with applicable parameters | Mass/inertia, dimensions, force scale/vectors, gravity, ground reaction/contact and attachments absent | Not ready. A physics library does not supply scientific parameterization. |

TTM-associated femur-extension function motivates the upstream channel label,
but **does not derive forward body speed**. The selected body's direction and
combination law are deliberately exploratory modeling assumptions. No new
biomechanics claim or numerical transfer from another preparation is needed.

## Coordinates, dimension and contact choices

Use a **planar 2D model world** with position `[x,z]` in `world_eq` units:
world +X right, +Z forward. Fixed body-forward equals world +Z; lateral axis is
available for future object-relative geometry but is unchanged by this v1 plant.
No dynamic heading, Euler angle or quaternion. A future visual embedding may
use +Y up and presentation height, but Y is not a plant state or physical floor.
`world_eq` is neither meters/mm nor a calibrated asset unit. Rendering scale
conversion must later be explicit and may not feed back into simulation.

Planar 2D suffices for a body-relative approaching-object demonstration.
2.5D would add vertical launch/return/contact assumptions before they are needed;
full 3D adds orientation/inertia/geometry complexity without current support.
Rendering can remain 3D independently.

First plant: unbounded mathematical plane, **no contact** and no gravity.
No grounded/airborne flag, floor clamp, obstacles, arena walls or collision
solver. Planar restriction is a state-space convention, not verified ground
contact. A bounded scenario arena and boundary policy belong to later world
runtime, not this first isolated plant test.

## Actuator→body rule and unilateral semantics

For validated right/left commands `R[n]`, `L[n]`:

```text
common[n] = (R[n] + L[n]) / 2
v_x_interval[n] = 0
v_z_interval[n] = motion_gain_world_eq_per_ms * common[n]
```

The arithmetic mean is fixed semantic normalization of two channels, not a
fitted gain or a physical muscle-force sum. Both original channel identities
and sample ancestry must remain auditable in the plant result.

RIGHT-only and LEFT-only each generate the same model-forward speed for equal
command magnitudes, at half the common-mode drive of equal bilateral commands.
This is an **explicit model symmetry**, not bilateral biomechanical evidence.
No side→turn rule. Differential input has no yaw/lateral/roll effect in v1;
preserve inputs so future asymmetry modeling is possible without reconstructing
or changing upstream identities. Do not require coincidence, use a binary
trigger, threshold or conditional escape action.
Forward direction is fixed by config semantics, not selected from threat
location. The plant does not decide whether motion approaches or avoids an object.

Both side contributions influence one modeled body's state only at this new
explicit plant boundary. Do not merge the neural, activation or actuator
trajectories upstream. Equal bilateral commands produce exploratory common-mode
translation, not a validated jump, takeoff or generic locomotion controller.

## Exact executable Phase 12B boundary

Implement one backend **common-mode planar kinematic body plant** consuming the
replayed persisted Phase 11B actuator artifact. Reuse all six source fixtures,
two channels per fixture, without electrical/activation reconstruction.

Only dynamical state is `position_world_eq = [x,z]`. Config includes initial
position; reference `[0,0]`, fixed +Z forward and one positive finite speed gain.
Recommend canonical gain **1.0 world_eq/ms** as a transparent unit-model speed
scale, not chosen from fixture outputs, geometry or biology. It is not a claim
that one command unit is a physiological speed. Initial position is an explicit
reset coordinate, not anatomical placement.

Update for each source interval `n = 0..N−1`:

```text
position_x[n+1] = position_x[n]
position_z[n+1] = position_z[n] + (time_ms[n+1] − time_ms[n]) * v_z_interval[n]
```

Commands at stored boundary n are held over `[t_n,t_n+1)` (left-boundary ZOH).
`position[0]` is the configured initial condition even if the boundary-zero command is
nonzero. Motion caused by a boundary-10 command first appears in position at
boundary 11: elapsed integration, **not an extra actuator/neural delay**.
No backdating of motion to boundary 10. Boundary N command remains retained as
source data but causes no displacement without a subsequent defined interval.
Do not append another interval or extrapolate beyond source duration.

Canonical source grid stays 0.1 ms, 80 intervals, 81 body-position boundaries,
8 ms duration. This avoids aggregation/resampling; a coarser mechanics clock can
be assessed later if measured performance requires it. `velocity_world_eq_per_ms`
is an optional **derived interval diagnostic**, not an independent inertial
state. If stored, it has 80 entries with explicit interval indexing, not an
ambiguous 81-boundary velocity series. No coast after command becomes zero.

Direct displacement-per-sample without dt would be grid dependent; reject it.
Prescribed speed integrated over dt retains a meaningful kinematic law with one
gain, while actuator→acceleration→velocity→position adds unidentified inertia
and damping. The selected plant is not dynamic merely because it integrates
position.

Minimal future output: versioned result/config identity, source artifact and
fixture identity, both actuator trajectory IDs/body/side/routing/proxy ancestry,
shared boundary/time grid, body position array, optional interval common drive/
speed diagnostics, explicit synthetic-validation provenance and limitations.
Six fixtures yield **six body trajectories × 81 boundaries**. There are not two
independent physical bodies corresponding to the two motor streams.

Config: gain; initial `[x,z]`; coordinate/units convention; fixed-forward,
arithmetic-mean and left-boundary-ZOH semantics; source schema requirement;
no-contact/unbounded-plane policy; modeling-assumption/exclusion metadata.
Source dt/horizon are validated references, not independent tunable defaults.
No general game controller, world engine, frontend/API, objects or new sensory
input in 12B. Provide deterministic runner/artifact/replay and repository-
consistent inspect tooling, not another standalone metadata phase.

## Selected parameter/assumption budget

| Quantity / convention | Units / role | Classification and readiness |
| --- | --- | --- |
| Motion gain, reference 1.0 | world_eq/ms per normalized common drive | MODEL_ASSUMPTION; biologically NOT_IDENTIFIABLE; only new free mechanics gain |
| Initial position, reference [0,0] | world_eq reset coordinate | MODEL_ASSUMPTION initial condition, not a fitted physiology parameter |
| Mean of two channels | Dimensionless normalization; unilateral half-drive | MODEL_ASSUMPTION fixed semantics, not EVIDENCE_SUPPORTED body mechanics |
| Fixed world/body +Z forward | Direction convention | MODEL_ASSUMPTION; no anatomical vector inferred |
| ZOH/update order | Boundary n drives the following interval | MODEL_ASSUMPTION explicit numerical semantics |
| Time grid/source ancestry | Existing 11B stored times and identities | Repository-supported contract, not biological evidence; fixed and validated |
| Planar restriction / unbounded domain | State-space choice | MODEL_ASSUMPTION, no floor-contact claim |
| Inertia, velocity decay, maximum speed cap | Additional dynamic/controller quantities | NOT_REQUIRED |
| Mass, force, gravity, stiffness, damping, floor height | Physical or extra plant quantities | NOT_REQUIRED in v1; physical applicability NOT_IDENTIFIABLE |
| Differential steering, heading, joint geometry | Extra control/anatomical mapping | NOT_REQUIRED; evidence/mapping absent |

Physical readiness remains not ready. Existing electrical/activation gains
and the new motion gain are confounded by output magnitude; displacement alone
does not identify them independently. Do not tune gain to jump distance or
select upstream sensitivity cells. No empirical loss/fit/score.

## Phase 12B behavior and reproducibility gates

- Zero/inactive pair gives exact stationary configured position and zero speed.
- Unilateral equal-magnitude histories give identical assumed forward motion;
  original right/left ancestry remains distinct, with no turn.
- Equal bilateral drive yields twice the unilateral displacement under the same
  config; this is an equation property, not measured biomechanics.
- Repeated fixtures follow the complete actuator waveform; no hidden trigger,
  extra memory or imported event schedule.
- Verify cumulative displacement against the explicit dt-weighted command sum;
  motion gain scaling, translation-invariant initial offsets and deterministic
  reset/replay. No future command may affect an earlier body boundary.
- Validate exact channel pair/body/side/source, fixture order, finite `[0,1]`
  commands, consistent strictly increasing times, positive finite gain and
  finite initial/output coordinates. Reject missing/duplicate/cross-routed
  channels, malformed grids, overflow/nonfinite state and tampering.
- Content-addressed config/result/artifact, deterministic order, identical
  persisted replay, ignored generated data, full historical regressions.

No browser clock, randomness, render-frame integration or visual transform is
an authoritative input. A future incremental step function may reuse this
plant law in a backend loop; 12B initially proves it with persisted fixtures.

## Backend authority, sensor feedback and looming gap

Backend simulation owns authoritative body/object state. Future transport can
deliver timestamped snapshots; R3F may visually interpolate position (heading
only if later modeled) without feeding interpolation back into sensory state.
Current playback floor-selects persisted neural samples; that is not already a
mechanics interpolation system. Render speed/pause must not alter an artifact
trajectory or the deterministic simulation clock.

Future minimal environment object: model-world position/approach trajectory,
positive model radius and deterministic schedule. Not implemented in Phase 12.
Relative bearing, apparent size and expansion must be calculated from the
authoritative body/object states at the simulation tick, with explicit
visibility/occlusion, side and coordinate policies as needed.

Existing `malecns/sensory.py` has analytic line-of-sight spherical/disk looming
geometry in meters and seconds, with a fixed visual center; `sensory_encoder.py`
uses angular quantities for earlier sensory models. Neither supplies arbitrary
body-relative 3D retinal projection into the current Phase 7O population.
`RelativeColumnStimulus` is a synthetic disk schedule in integer MaleCNS hex
lattice steps, with `absolute_visual_angle_present = False`. A model-world
position or 3D rendered sphere does not automatically define LC4/LPLC2 input.

World→sensory work therefore requires: explicit model-world/body/view relation;
apparent angular geometry (without relabeling world_eq as meters); a justified
or assumption-labeled visual-angle/bearing→left/right relative-column mapping;
time-aligned per-body exposure/drive construction using the existing source
associations; and a causal online sampling convention. No fabricated anatomical
retinotopy. Earlier scalar looming code can inform mathematics, not silently
replace the current sensory contract. Avoid precomputing an open-loop sensory
schedule while claiming body feedback.
The later scheduler must avoid an algebraic feedback loop: sample authoritative
body/object boundary n for sensing, respect existing neural state/event boundary
semantics, and apply newly available boundary commands only to their following
plant interval. Never let a rendered or future body state determine earlier
sensory input. Exact online pipeline latency/order remains a Phase 13 integration
decision, not a fabricated zero-delay end-to-end claim in 12B.

## Scenario readiness and Phase 13 handoff

| Blocker class | After successful 12B |
| --- | --- |
| Mechanics | Isolated planar body trajectory exists; explicit scenario bounds/object/contact policies still need a world-runtime decision. No physical jump mechanics. |
| Sensory/world | World/body/object→existing column input mapping and causal feedback scheduler remain missing. |
| Neural output | Canonical genuine 7O source is silent; no nonzero connectome-driven actuation demonstrated. Do not retune in Phase 12. |
| Production composition | Genuine 8C prefix is not connected into fixture-pinned downstream electrical/activation/actuator execution; provenance-preserving runtime composition remains required. |
| Frontend/product | No live scenario API/snapshot contract or scenario controls; stationary visual asset still needs simulation-owned transform binding. |

Thus **additional major blockers remain**, not “closed loop ready after 12B.”
The missing production composition is separate from the zero-spike issue; a
future nonzero neural result alone would not close the path. No prescribed
looming→jump, threshold→animation, generic threat response or LLM control.

Phase 13 should integrate one minimal deterministic looming-object world
runtime, the explicit world→column sensory mapping and tick ordering, and
provenance-preserving causal composition. It must expose genuine zero output
honestly and distinguish any synthetic plant-only demonstration. Nonzero neural
output investigation is an independent scientific task, not a movement
fallback. Phase 14 can add a scenario picker/polished rendering after backend
state semantics are stable; no long mechanics metadata sequence is recommended.

## Scientific claim budget and decisions

After 12B, permitted: deterministic exploratory model-space body-position
trajectories from side-addressed actuator fixtures under explicit kinematic
assumptions. For genuine runs, claim connectome-driven movement only when
actual provenance-preserving nonzero execution exists.

Not permitted: predicted jump distance, SI force, biological takeoff mechanics,
anatomical joint motion, autonomous escape from synthetic fixtures, or an
already complete closed sensory–motor–world loop.

| Decision | Selected value |
| --- | --- |
| Model philosophy | `EXPLORATORY_KINEMATIC_BODY_PLANT` |
| Dimension | `PLANAR_2D` |
| Physical mechanics | `PHYSICAL_MECHANICS_NOT_READY_USE_MODEL_SPACE` |
| Actuator→body | `COMMON_MODE_PROPULSION_ONLY` |
| Contact | `NO_CONTACT_IN_FIRST_PLANT` |
| Ownership | `BACKEND_SIMULATION_AUTHORITATIVE_FRONTEND_INTERPOLATES` |
| 12B readiness | `READY_FOR_FIRST_EXECUTABLE_BODY_PLANT` |
| Connectome movement | `PRODUCTION_PATH_NOT_CONNECTED_TO_ACTUATOR` |
| Closed-loop scenario | `ADDITIONAL_MAJOR_BLOCKERS_REMAIN` |

Exactly one next executable Phase 12B: the planar common-mode kinematic plant
above, with all six fixtures, persisted body-state results and offline replay.
No implementation or new artifact in 12A.

## Verification and status

Required source replays pass, including full numerical 7O and genuine 8C
replay. `python -m pytest`: 899 passed, 1 deselected, two existing dependency
deprecation warnings. Ruff check and format check pass; `git diff --check`
passes. Frontend regression: 38 tests pass; lint, typecheck and build pass.
The generated Next type-reference path change was restored; only this document
and the minimal Project Context addition remain. No production code, new
generated artifact, commit or push.

Phase 12A status: `PASS` for architecture/readiness. This does not certify
physical biomechanics or closed-loop behavior.
