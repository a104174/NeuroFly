# Motor-to-Gait Bridge v7 — bounded open-loop experiment

Classification: **EXPERIMENTAL_MODEL_DERIVED_GAIT_MODULATION**.
Required limitations: **SHADOW_ONLY_MOTOR_RESPONSE**, **ENGINEERING_JOINT_PROJECTION**,
**NO_VALIDATED_NEUROMUSCULAR_ACTUATION**.

## Reused authorities, without scientific mutation

Initial local/remote main: `9e69f3aa23646938eb5529fccfdbff92be2f9396`, clean.
MaleCNS v1.0 UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`.
The existing structural authority verifies INXXX466_R/T1 source **903216** to
Ti extensor MN_R/T1 target **804257**, 23 structural contacts. This does not
identify muscle force, functional sign, or a calibrated animated joint.
Structural row hash: `e5ff03ee94e0b46ba2827701c1533676b70af16f4d43000a7a29512002aacc6a`.

Existing converged recurrent source:
`d0f441ad8e9ebdbf83812dcbf52e86326d76e093632dfe5cbe58607a48d525f8`.
RK4 integration 0.03125 ms, recorded every 1 ms, states ordered
`[800173,800863,801884,800288,903216,803183]`, source index 4.
Both DNg100 inputs are externally prescribed 20 model units on [0.02,2) seconds.
The six-state recurrent model uses selected signs, threshold 7.5, tau 20 ms,
cap 200 and structural-count-to-model weight assumptions. These are model
assumptions, not measured neural activity. Biological functional signs remain
UNKNOWN. No HS/DNp15 → DNg100 functional connection is asserted.

Motor input artifact:
`7f40609a28662d6b4f61e00e24b6aaed688322b4bbf716bda98bdaba5a93c988`.
Input u = sign_assumption × 1 × source state; 23 contacts are provenance only.
Motor response artifact:
`deba097e484fa45675e2f5ab30add960bef141015af7344dc704d94444b9adad`;
raw response.json SHA256
`27da13861cc44d9cfc440573f037c4579e9f05da23bb3034ac35533566ec397f`.
Select existing TAU_10MS/A_POSITIVE, with C_ROUTE_OFF and D_SHAM controls.

The hypothetical response is `tau dy/dt = -y + u`, tau=0.01 s, initial y=0,
gain=1. Python's exact held-input update uses `-expm1(-dt/tau)`.
Receiver units inherit uncalibrated model input; not voltage, current, firing,
activation or force. The extracted source has 2001 boundaries on [0,2] s at
1 ms. State y[n] precedes consumption of u[n] on [t[n],t[n+1]); the last input
has no outgoing interval. No neural solve is added to the browser.

## Compact deployable reference

`tools/exports/build_motor_gait_reference.py` reads and verifies immutable raw
source identities, invokes the existing full semantic response replay (including
parent structural/input/neural authorities), then extracts two columns:
source_model_state, receiver_state. It verifies route-off is exactly zero and
sham exactly matches the positive receiver. No original solver is rerun.

Reproduce without changing historical outputs:

```
.venv/bin/python tools/exports/build_motor_gait_reference.py
```

Output: `web/public/experiments/motor_gait_bridge_v7.json`, schema
`motor_gait_reference_v7`, 84,415 bytes. SHA256:
`90ddfadcf9d8ccb85590d74de4b66cecfff24a3ec9f9b6592729b74d34031d06`.
It includes source chain identities, annotations, response assumptions, controls
and 101 Python-generated projection checkpoints. Browser validation pins the raw
identity and checks the receiver recurrence; recalculated superficial identities
cannot authorize different data. Missing/nonfinite/contradictory sources fail
visibly, with no substitute signal. Hashes detect corruption; they do not
identify the person who authored a trace.

The historical v1 NEURAL_STEERING body's first 2 s supply all matched poses
(101 boundaries, 20 ms). Source artifact:
`4d7c791224f21ecf677df81d2127a6f8b753974694b6b324afc1948da3fb9064`.
The existing raw SHA and semantic body validator run on load. Heading/position,
HS/DNp15 states, 0.1 ms / 200-substep scientific semantics, propulsion and contact
records are never recalculated or modified by the visual overlay. This bounded
reference does not reach a wall; historical recovery policy remains unchanged.

## One engineering projection

Visual version: `engineering_swing_height_projection_v7`.
Exactly one target: `Leg.R.Front`, rig index 3. Underlying descriptor SHA256
`1349d977ef9f72ba9d7f7ac8fe284572039b14c3c59dff2204e1bead800c191f`.
Original V2-F surfaces/CC BY 4.0, six-leg/18-bone rig, tripod phasing, body anchor,
scale, reach/joint limits, and original V6 gait code remain unchanged.

```
q = clamp(receiver_state / 100, -1, 1)
peak_swing_height = clamp(0.012 + 0.004*q, 0.008, 0.016)
envelope = clamp((base_foot_Y - 0.006) / 0.012, 0, 1)
projected_foot_Y = base_foot_Y + (peak_swing_height - 0.012)*envelope
```

Units: height and gain in arena presentation units, reference 100 receiver model
units, q dimensionless. The fixed reference and ±0.004 maximum excursion are
engineering choices bounded to one third of baseline swing height, chosen before
the final controls, without per-run peak normalization. The positive source
actually remains well below this clamp. Swing lift is multiplied by the existing
continuous height envelope; a planted foot receives zero change. No other foot,
phase, stride, body state or scientific input is changed. Existing IK can project
an unreachable target rather than stretch the anatomy; actual rendered joint
changes are reported separately from requested peak height.

BASE keeps the same calculated source/receiver but disables projection. ON applies
A_POSITIVE. ROUTE_OFF uses the verified zero-input/zero-initial-state receiver,
retaining recurrent source activity and all body/gait parameters. SHAM matches ON.
Route-off is a computational control, not a physiological lesion. No new external
model-drive variation (condition D) is introduced; the existing sham is available.

Between 1 ms source boundaries the browser uses deterministic linear visual
reconstruction. This is not a new neural integrator or hidden phase shift. No
extrapolation, loop, extension, or 30 s motor signal is allowed. Playback ends at
2 s. Seeking reads the cached body/gait history and reference, without neural
computation. Pause freezes simulation time. Controls can change at a fixed cursor
without resetting that cursor or the common body/gait.

Reproducibility identity is the tuple of pinned selected reference SHA, pinned
body artifact, visual rig SHA and projection version/parameters above. It is an
experiment-level visual contract, separate from historical scientific/session
identities. V7 introduces no storage migration or altered event logs.

## Product and resource boundary

Arena mode **Motor-to-Gait Bridge v7** provides Base/ON/route-off/sham, Play/Pause,
Reset, 1 ms seek, Inspect Fly, original/articulated toggle, signed model/parameter
values, actual selected knee/foot values and a shared-time two-lane SVG timeline.
The caption explicitly says PRECOMPUTED_PYTHON_MOTOR_MODEL_RESPONSE; this mode
uses precomputed body replay too. It does not claim live motor calculation.
The timeline and full scientific inspector agree at the cursor. Curves are memoized
across seeks; source data and body history load once per mounted experiment.
The bridge creates no geometry, bones, skeletons or materials; V6 retains ownership
and disposal. No neural/body solver imports occur in the pure projection adapter.

## Tracked next milestone (not implemented)

**ARTICULATED_WING_MOTION_V7_1** remains the explicitly requested next motor-visual
capability. Actual GLB has independent unskinned `Wing.L` and `Wing.R` meshes,
no wing bones or clips. Wings remain excluded from v6 skinning. Geometry bounds
place their roots near thoracic attachments, but bounds alone do not validate a
pivot. A derived pair of artist-reviewed attachment pivots and appropriate
reparenting/rest transforms are needed, preserving the original geometry.
Current locomotion has fixed altitude and **no flight-state contract**. V7.1 must
first receive or define an explicit engineering flight-state signal with simulated
time boundaries, before enabling deterministic wing articulation during flight.
Grounded walking must not continuously flap. No altitude, aerodynamic lift,
wing-muscle control or flight physics is implemented or inferred by v7.

## Local validation results

- 259 frontend tests; 113 focused Python tests (including original motor input,
  motor response and runtime/canonical bundle checks) passed. Original selected
  source comparisons and all 101 Python projection checkpoints use 1e-10;
  rendered foot endpoint comparisons use the existing 1e-8 visual tolerance.
- Positive receiver maximum 48.51900174689791 units at 0.042 s, peak-height
  parameter 0.013940760069875916. This is not necessarily a swing or joint maximum.
- On the common 20 ms body grid the largest actual added target lift is
  0.0007857500410935088 at 1.94 s. Selected knee changes from
  2.035459772045005 to 2.0538323776274767 rad; maximum absolute selected knee
  difference 0.018372605582471557 rad. No selected-leg reach clamps in 101
  matched boundaries. Five other limbs, body coordinates and gait phase match
  exactly. BASE=ROUTE_OFF; ON=SHAM. The effect is deliberately subtle.
- Local Chromium/SwiftShader desktop and 390 px: actual bone endpoints match
  calculated targets, selected joints differ under genuine positive response,
  route-off restores base, sham restores ON. Play/Pause/Reset/Seek and returning
  to original specimen pass. Missing reference is visibly rejected; the injected
  missing-source test intentionally produces HTTP 404 console entries, whereas
  normal operation produced no runtime errors.
- Same-pose repeated BASE/ON selections add no geometry, skeleton or material
  allocations. Three full original/articulated toggles consistently restore
  312 geometries/7 textures and 440/13 respectively in that browser sequence.
  Absolute renderer counters depend on which original surfaces were uploaded;
  they are not GPU-byte measurements. Six further bridge condition selections
  retain constant counters. Observed post-GC heap 20.9–23.0 MB, not a long-term
  memory guarantee. Actual gait apply 0–0.3 ms at browser timer resolution;
  1–3 FPS with SwiftShader, not a physical GPU benchmark.
- Separate CPU microprofile: bridge interpolation/projection about 0.235 us,
  selected IK 0.729 us, full 101-boundary base history 0.166 ms on this host.
  These averages describe the small numerical adapter, not full scene render
  time. SVG curves are memoized and do not run a model on seek.
- D2.2's 74 pinned files, canonical payload identities, DNg100 v0/v1 and
  motor-input/response raw identities, Planar SHADOW_ONLY and V5 policy/fixture
  checks pass. Frozen Python models, historical web experiments, session schemas,
  v6 mathematics, original asset and rig descriptor remain byte-unchanged.
- No scientific-model source change, new backend, dependency, storage migration,
  commit, push or deployment occurred during the local implementation phase.
  A subsequent operator instruction authorizes the scoped v7 commit/push and
  protected Preview acceptance; Production remains unauthorized.

Final production-build local acceptance (127.0.0.1:3001): all matched controls,
actual articulation, pause at 1.0332 s, resume/reset, exact seek reconstruction,
automatic bounded end at 2 s, and 390 px passed with no runtime errors. Maximum
observed actual/calculated foot-end error was 2.22e-16. The actual rendered
front-right foot ON−BASE lift at 1.94 s was 0.0007857500410934914, and joint-bend
difference 0.018372605582471557 rad. Three full toggles restored the same
312/7 off and 440/13 on geometry/texture counts. Final measured post-GC JavaScript
heap was 15.6 MB; software-rendered FPS around 1 in that full instrumentation
run. This differs from the development/profile samples above and is not a GPU
benchmark or a long-duration leak test. Full source after the bounded-end clock
cleanup passed the same 259 frontend tests and production build.
