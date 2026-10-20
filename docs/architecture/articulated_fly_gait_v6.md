# Articulated Gait v6 — engineering presentation

This optional local feature is downstream of the authoritative body pose. It is
**Engineering kinematic gait — not connectome-derived leg control**. No scientific
model, source identity, timebase, body trajectory, event log or storage schema is
changed. No leg motion or presentation configuration is serialized as neural data.

## Asset and provenance

The approved V2-F GLB is preserved byte for byte (SHA-256
`0502cb995d25b2f9d7b57eff0cf95a0c9cfd7f838e212e95b3895bb69c7e5238`).
Both it and the inspected external `fly_v2f_lookdev.blend` have six individually
named leg meshes, no armature and no animation clips. The thorax/abdomen remains
one joined body surface. The historical project V1 Blender source is a different,
simplified specimen and is not substituted.

`tools/blender/derive_fly_gait_rig.py` imports the immutable V2-F in Blender 4.0.2
and creates only `web/src/assets/fly_gait_v6.json`. It never saves over a Blender
source or GLB. Reproduce with:

```sh
blender -b --factory-startup --python tools/blender/derive_fly_gait_rig.py
```

The derived descriptor SHA-256 is
`1349d977ef9f72ba9d7f7ac8fe284572039b14c3c59dff2204e1bead800c191f`.
The versioned `engineering_fly_gait_rig_v6` descriptor identifies six hip/distal/
foot chains (18 bones), four artist-selected rest points per chain, expected leg
vertex counts and 122 nearby detail meshes. Detail assignment uses nearest leg
surface versus body/head/wing/eye surfaces, retaining source identities. Pivots
are checked against actual imported vertices. This is an engineering visual rig,
not independently validated biological joint segmentation.

The runtime skins cloned source leg/detail surfaces: 128 meshes are replaced,
not added. Body, head, eyes, wings, materials, textures, source triangle count,
scale 0.3 and thoracic anchor `[0, .06168119236826897, .12187743186950684]` remain.
Each instance owns its added geometry/bones/skeletons and releases them on toggle
or unmount; loader-cache geometry/textures and original specimen stay immutable.
No new GLB transfer, duplicate limbs or large Blender binary is required.

Credit: *Wildtype Male Drosophila Melanogaster*, mlykouretzos, CC BY 4.0,
https://sketchfab.com/3d-models/wildtype-male-drosophila-melanogaster-0affd20207ca4c889bd7e1e513e04dfa .
License: https://creativecommons.org/licenses/by/4.0/ . NeuroFly retains V2-F's
previous appearance changes and adds artist-selected pivots/procedural skinning.

## Motion and time contract

`articulatedGait.ts` consumes completed body boundaries only: simulation time,
position and unwrapped heading. It imports no neural simulator. Each 20 ms body
interval adds `(horizontal_distance + abs(yaw_change) * .065) / .055` cycles.
No RAF delta, render count, wall time, randomness or neural substep drives phase.
The 0.1 ms neural / 20 ms body / 200-substep scientific clocks remain unchanged.

The alternating groups are L-front/R-middle/L-rear versus their complements,
separated by half a cycle. Stance occupies 0.62 of a cycle; initial phases begin
halfway through stance, avoiding an overextended initial planted foot. During
stance the target is world-fixed. During swing it follows smoothstep horizontally
and `.012 * sin(pi*t)^2` vertically. Landing prediction uses current measured
translation/yaw, capped at 0.18 simulated seconds, solely to place visual feet.
It never predicts or writes an authoritative fly pose.

Parameters use arena presentation units, seconds and radians: stride 0.055,
swing height 0.012, ground target Y=0.006, turning radius 0.065, settling time
constant 0.18 s, nonzero-motion threshold 1e-7 units per completed interval.
The first engineering stride trial (0.070) overstretched some chains; shortening
it and centering initial stance reduced the maximum reach projection in the
30 s example from 0.01128 to about 0.00123 units. This is visual stability tuning,
not scientific/physiological parameter calibration.

Two-link IK plus an oriented visual foot preserves link lengths. Reach is bounded
to 0.998 of combined link length, hip deviation to 1.8 rad and knee bend to
2.65 rad. Degenerate targets/non-finite history are rejected. Small unreachable
placements are projected and reported as `clamped`; they never move the body.
Near-joint blend width is 0.018 asset units. Unsupported extreme targets can lose
exact planted contact under those limits rather than stretching a limb.

When translation and yaw stop, cycle progression stops and feet settle toward a
standing pose using **simulated** time. Resume from a stopped swing re-anchors the
remaining swing without a phase reset. Actual yaw at a blocked wall produces
restrained repositioning, not continued full-speed forward walking. Recovery
requires no new gait policy: actual translation resumes the ordinary cycle.
Pausing freezes scientific time and therefore the exact gait; a paused recording
may intentionally capture a lifted foot.

A deterministic body-history reconstruction creates presentation states. An
append-only WeakMap cache is keyed to the source history, validates every reused
pose and allocates only new states; changed prefixes are invalidated. Old arrays
are never mutated and discarded source histories can be garbage-collected. Seek
samples that cache (including interpolated foot targets where needed), without
running neural dynamics. Changing focus/time does not prescribe body motion.
Presentation diagnostics expose calculated and actual bone-end world positions,
joints, phase, reach projections and update cost separately from scientific data.

## Product scope and error handling

Enable **Articulated Gait v6** below the arena in live v3/v4/v5 or the Protocol
Scheduler. Saved/imported sessions in these modes reconstruct from the existing
scientifically validated event inputs and supply their cached body boundaries.
The control is deliberately unavailable where this change does not supply a
complete motion history (including historical canonical views and comparison
viewers); those retain the original specimen and existing behavior.

Inspect Fly, orbit and arena cameras remain unchanged. Missing/incompatible rig
surfaces are detected before mutation; rig failure retains the validated static
V2-F with an explicit message. Failure to load the original GLB remains a visible
asset error, never a fabricated articulated specimen. Metadata has no IndexedDB
migration and changing gait presentation does not affect experiment identity.

## Verification and limits

Focused tests check the real source geometry, six chains, original triangle/mesh
counts and buffer ownership, actual skinned vertex changes, bone endpoints,
length/joint/reach bounds, floor clearance, tripod coordination, world-planted
stance, speed/yaw/stop/recovery, deterministic seek/FPS independence and invalid
inputs. Two full neural experiments with and without downstream gait calculations
must produce exactly identical scientific exports (300,000 substeps each).

Canonical frontend gates and applicable Python asset/reference integrity checks
are required. Browser acceptance must additionally inspect actual geometry,
world-space feet versus bone endpoints, contact/recovery, original toggle,
pause/reset, save/reload and seek, on desktop and 390 px. Evidence belongs outside
Git under `../neurofly-assets/work/articulated-gait-v6/`.

This is a lightweight skinned artistic specimen with engineering tripod timing,
not a measured Drosophila gait, joint reconstruction, leg CPG, muscle simulation,
physical contact-force solver or individual-leg connectome control. It supplies
no proprioception, sensory input or feedback to the experiment. Source artistic
proportions and transparent-wing sorting remain limitations. Software-rendered
SwiftShader performance is not a physical GPU benchmark. The initial local
implementation phase did not authorize publication. A subsequent operator
instruction authorizes one scoped commit/push and protected Preview acceptance.
The local results below remain distinct from verified Preview acceptance.

## Completed local acceptance

Baseline `main` and remote: `093cb9d6cc7477766bf0267a50a41fa0ecee0739`, initially
clean. No staging, commit, push, Preview or Production deployment was performed.
The change inventory is four modified components and five new source/test/doc
files. Original V2-F GLB and Blender sources remain unchanged. Re-running the new
Blender generator reproduced descriptor SHA-256
`1349d977ef9f72ba9d7f7ac8fe284572039b14c3c59dff2204e1bead800c191f`
(6235 bytes), with no new GLB or Blender binary.

Final gates: 252 frontend tests; lint, typecheck and production build; Ruff lint
and format; 48 focused Python tests plus the isolated pinned-runtime check of all
five canonical replay hashes. Two existing Python dependency deprecation warnings
remain. Read-only verification covers D2.2's 74 files, DNg100 convergence/dynamics/
motor artifacts, Planar raw files, v5 policy/fixture and unchanged scientific
source/public data. No historical output was regenerated.

Chromium with SwiftShader tested the actual local production build on desktop
1440×1100 and 390×844, with screenshots, video and numerical transform evidence.
Six independent chains moved; computed feet and actual bone-end world positions
agreed within 1e-8. Stationary, walking, contact, turning at contact, recovery,
pause/resume/reset, toggle and original-resource restoration passed. Example v3
contact at 6.00 s and turning at 6.90 s had exactly the same position but changed
heading; by 9.20 s translation had resumed with one recovery. These are sampled
acceptance observations, not newly prescribed behavior.

A historical 30 s protocol was imported and reconstructed, inspected at 4/8/4 s,
saved, reloaded and reopened. Its scientific export remained exactly equal to
the prior result, execution ID
`37c10f1b1f78e424d9ac64d3873e12995b1cbac6bcdebccb40b4f82659d69e0b`.
The same sought timestamp reproduced identical joint transforms after reload.
No runtime/console errors were found (the pre-existing favicon 404 is excluded).

Same-pose, same-Inspect-Fly-camera renderer samples: approximately 3 FPS both
original and articulated; 306 calls and 55,734 rendered triangles in both.
Counters changed from 314 geometries/7 textures to 442/13 (128 owned skinned
geometry copies and six skeleton textures); toggling off restored 314/7.
These are renderer counters, not GPU memory. Warm enabling to the next diagnostic
sample took 1.98 s including shader/UI/render/report scheduling; source GLB fetch
was 79 ms locally. Sampled gait solve/application cost was about 0.1–0.6 ms.
Observed JS heap was approximately 41–49 MB, not an isolated allocation delta.

CPU microprofile (rendering excluded): complete 1501-boundary reconstruction
median 8.20 ms, validated cache 0.235 ms, one appended boundary 0.153 ms, selected
six-foot sample 0.0015 ms, six-leg IK 0.014 ms. Cache/full-reconstruction equality
and changed-prefix invalidation are regression-tested. Renderer timing, neural
simulation timing and gait computation remain distinct; no fixed timestep was
changed to improve performance.

Outcome: `ARTICULATED_FLY_GAIT_V6_LOCAL_VALIDATED`. This is local engineering
presentation acceptance, not a published Preview or biological gait validation.
