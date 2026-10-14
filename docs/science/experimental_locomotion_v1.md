# Experimental Locomotion v1 — causal HS/DNp15 steering

This is a separately versioned **precomputed Python simulation replay**. It
combines connectome-informed neural steering with engineering propulsion, not
fully connectome-driven locomotion or biological walking. V0 remains separately
selectable and retains its byte-identical artifact.

## Fixed design and actual causal loop

The versioned policy `experimental_locomotion_v1_policy.json` was written and its
content identity recorded before the new trajectories were generated:
`760328e025b4256dc2bbb2fe5e680d0a80f56d8f83e1bda774c84696b49812ef`.
This records this implementation workflow, not independently certified prospective
preregistration chronology. No gain or geometry was tuned after observing results.

Source structure: MaleCNS v1.0, UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`.
HS R: 10015 / 10016 / 10023; HS L: 10034 / 10181 / 10419.
DNp15 R: 11215; DNp15 L: 12069. The existing six selected directed routes,
positive proxy transfer convention and frozen kernels are unchanged. Structural
counts are evidence, never numerical synaptic gains. Neither this experiment nor
its engineering conversion establishes physiological synaptic signs.

At boundary n, compute apparent angular landmark motion between the actual
computed poses n-1 and n (n=0 has neutral observation). Hold that descriptor for
the next body interval, advance the continuous HS/DNp15 states over 200 neural
substeps, aggregate yaw increments, compute engineering angular motion, advance
the shared body plant, and feed the resulting pose into the next observation.
This is a causal delayed closed loop; it contains neither a prerecorded neural
trace nor a target-seeking, wandering or wall-avoidance policy.

The existing two-landmark observer is reused directly. Landmark coordinates are
X=+0.6 (R reference), X=-0.6 (L reference), with one common fixed Z plane.
Primary Z=+0.4; the sensory intervention changes only Z to -0.4. Each reference
keeps its declared channel identity rather than being reassigned by instantaneous
field of view. The planes are outside the admissible anchor Z extent, preventing
coincident geometry. Visual floor markers render these exact world coordinates;
they are not collision obstacles.

World bearing is `atan2(landmark_x-body_x, landmark_z-body_z)`. The apparent
relative bearing change is the shortest world-bearing difference divided by
2*pi, minus body heading change divided by 2*pi. Each side's descriptor is that
change / elapsed ms, multiplied by the frozen 50-ms reference and R:+1 / L:-1,
then clipped to [-1,1] with raw values and flags recorded. The observer's geometric
singularity and ordering validators remain in force. This is an engineering
visual-motion descriptor, not a calibrated retina; two descriptors cannot
uniquely identify all planar movement causes.

The frozen observer's PoseBoundary DTO labels caller-supplied engineering samples
as ENGINEERING_PRESCRIBED_POSE. V1 uses it only as an input bridge for computed
snapshots, never as trajectory generation or an assertion of prescribed movement.
Policy and telemetry explicitly label their origin
PYTHON_COMPUTED_BODY_POSE_NOT_PRESCRIBED_TRAJECTORY. One display unit is mapped to
one observer world_eq and radians to unwrapped cycles; these are new explicit
engineering coordinate mappings, not physical calibration.

## Multirate numerical contract

Body dt=20 ms (0.02 s), neural dt=0.1 ms, 200 substeps per body interval.
Eight seconds contain 400 body intervals / 401 boundaries. Every neural condition
executes 80,000 substeps, with no extra final-boundary transition.

The existing `compose_neural_interval` is called with **0.1 ms**, never 20 ms.
It uses the frozen old-state simultaneous transition: exact held-input exponential
HS leak (tau=5 model ms), DNp15 leak (tau=10 model ms) driven by the OLD HS states,
and yaw readout of the OLD DNp15 states. States carry continuously across intervals.
All three HS inputs per hemisphere share a descriptor and proxy dynamics; this
experiment does not identify their individual anatomical-route necessity.

For each neural step k, the existing yaw kernel returns
`delta_orientation_eq[k] = (0.1/50) * yaw_drive_eq[k]`.
The adapter sums 200 increments, rather than treating an increment as a rate.
Mean yaw drive is independently recorded. The engineering conversion is:

`omega = clip(2.5 * sum(delta_orientation_eq) / 0.02, -0.5, +0.5) rad/s`

`theta_next = theta + omega * 0.02`

Gain 2.5 rad/orientation_eq is an engineering reference normalization: a held
0.01 yaw_drive_eq corresponds to 0.5 rad/s before saturation. The angular bound
limits one body-step rotation to 0.01 rad. Neither gain, bound nor the model
leak constants are measurements of a walking fly. Dt is applied once in the
source increments and once when converting rate back to body heading; it is not
multiplied twice. The 8-s proxy execution extends beyond the canonical 50-ms
experiment without overwriting or reinterpreting that frozen result.

## Shared plant and conditions

The original v0 plant now exposes its pure velocity/contact and position/clamp
operations, reused unchanged by both runners. V0 regeneration remains exactly
identical. All runs use speed 0.18 display units/s, initial heading pi/2, original
floor height, scale, geometry and circular footprint. Translation uses the LEFT
heading over the interval, then heading advances. Outward contact is checked at
the resulting boundary, and once detected latches translation to zero. Neural
state and heading continue; there is no synthetic wall reflex. Body stays inside
the admissible region, including oblique contact and arbitrary visual rotation.

A: engineering baseline; neural computation disabled.
B: neural computation and engineering steering enabled, Z=+0.4.
C: identical initial configuration and world as B, neural computation continues
but only its contribution to heading is suppressed.
D: same configuration as B except the visual plane Z=-0.4.
Random policy NONE. A and C have exactly identical body trajectories. B and C
have identical sensory/neural computations before their poses diverge; later
upstream differences are the intended consequence of feedback.

## Recorded results and bounded interpretation

A/C travel 0.9654288893949121 units and contact X at 5.38 s.
B travels 0.9892713969187931 units and contacts Z at 5.50 s.
D travels 1.0025490049292485 units and contacts X at 5.58 s.
B's maximum yaw difference from C is 0.6766798814084118 rad.
Changing only the plane (B vs D) changes the mean neural yaw drive by up to
0.006540882606567513, heading by up to 1.1783775624855197 rad and position by up to
0.4764494359566599 units. These are deterministic model differences, not biological
statistical effect sizes or fitted behavioral results.

At boundary 1, all conditions still share the same actual pose. Independent
atan2 checks establish that the different visual plane changes the sensory
values; the real kernel then changes the readout, and the declared mapping changes
heading at boundary 2. Subsequent pose changes alter subsequent sensory inputs.
Disabling only output application removes angular motion while retaining neural
computation. Propulsion remains exactly matched. This traces causality within the
implemented model rather than inferring it merely from different trajectories.

The browser uses the existing playback clock, interpolation and rendered body
transform. The optional line is a floor X/Z projection of the COMPLETE recorded
trajectory, not a future live prediction. UI shows run controls, HS/DNp15 states,
readout, heading/angular velocity, engineering propulsion, geometry, contact,
parameters, provenance and limitations. No Python executes live in the browser.

## Reproduction and gates

```sh
.venv/bin/python -m neurofly.experimental_neural_locomotion --output /tmp/neural-locomotion.json
cmp /tmp/neural-locomotion.json web/public/experiments/experimental_locomotion_v1.json
.venv/bin/python -m neurofly.experimental_neural_locomotion --verify web/public/experiments/experimental_locomotion_v1.json
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
# With the project virtualenv on PATH for existing scientific replay tests:
npm run test --prefix web
npm run lint --prefix web
npm run typecheck --prefix web
npm run build --prefix web
git diff --check
```

The compact public asset contains 1,604 body boundaries with per-interval sensory
and neural summaries, never all 240,000 neural substep traces. Complete policy,
source definitions, model identities, configuration and results are recoverable.
Canonical config/result hashes and logical ID are distinct from the raw file hash.
Semantic validation regenerates the complete loop and rejects contradictory content
even with recalculated hashes. Numerical tests use an independently constructed
old-state affine matrix raised to power 200, not production expected-value helpers.

No DNg100 SHADOW_ONLY receiver is used as actuation. All previous UNKNOWN sign
evidence remains intact. No motor-neuron spiking, muscle force, gait, learning,
consciousness or biologically validated locomotion is established. Frozen canonical
science and the prior experimental v0 artifact must remain unchanged.

## Content identities

Configuration: `a916769c730174b3d631ccda9df0dd89479cd1b12f43be250b856c1782736e2d`.
Result: `b4b1ac2737cfca5f5e1d2d06050e5b0ab063d22f14f59bae0115e7fe368c95aa`.
Logical artifact: `4d7c791224f21ecf677df81d2127a6f8b753974694b6b324afc1948da3fb9064`.
Raw JSON: `17d335358a4f5cf4ed98b9682b103a81419cf82504203ce1bc72a7d76285d748`.

Frozen model definition identities (canonical content SHA-256):
HS/DNp15 `371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074`;
yaw `1be0f6364070a5a5536f4c772bd47abb3be2f08357b439a51e03f034f8b2a654`;
planar observation `49e91a10fa49c5d7004f28249b63f334a0e23767c20108f5578a0e2586c9767a`.

Implementation byte identities of the unchanged kernel files:
`hs_dnp15_neural_validation.py`: `5196c338c9f8f352d761935ac311f4d44d5fd7cdee1091665241505455caa1b6`;
`exploratory_course_control.py`: `4b9c27915998dc091ac882b53b52ae2ad88914b6f9fd3ee57bc32ef981f607ba`;
`dnp15_exploratory_yaw.py`: `b08b7cc6b895aba3d425fcb704771106cea1813597331fd40d819411a5324042`;
`planar_motion_observation.py`: `ecd1f154afe487be77583db6badad6eff72a8480dfd4040e62c3e68b771ec540`.
These are distinct from the authority/model-definition hashes above.

Generation measured 4.32 seconds for the four conditions and 240,000 neural
substeps, including JSON serialization. B's maximum |omega| was
0.21800913359782603 rad/s; D's was 0.11034000657923607 rad/s. No steering interval
reached the declared angular clipping bound. Public JSON is 1,712,143 bytes;
full microstep traces are not stored. New biological parameter values were not
introduced; only the explicitly labelled engineering gain, angular bound,
coordinate bridge, stimulus geometry and longer model horizon were added.

Validation completed: 1,672 Python tests passed, one integration test deselected
under the existing policy, two dependency deprecation warnings. There are 17 new
focused tests (47 together with v0). All 134 frontend tests, lint, typecheck,
production build, Ruff and diff checks passed. Source authority, five canonical
payload hashes/provenance, D2.2 bundle, prior Planar and DNg100 artifacts, and v0
were preserved. Browser controls and the four causal conditions were exercised on
actual WebGL; desktop and 390-pixel layouts passed without execution errors.
The available renderer was SwiftShader, not a physical-GPU performance reference.
Protected Preview verification is performed separately after publication.
