# V10.6B — Second Initial-Condition Replication Protocol

**PROTOCOL PRE-SPECIFIED**
**RESULTS NOT YET GENERATED**

Version: V10.6B-0, 2026-10-29. Reference implementation: V10.6A commit
`04ebca9e87b2edc0d842d9a9ee4a12bc53b88443`.
This local Git checkpoint is a version-controlled pre-specification, not an
independent public preregistration. Do not amend it after inspecting outcomes.

## Question and single selected condition

Does the total model-level causal effect of applying neural yaw persist, change
or disappear under a second valid initial orientation? Change only heading,
using the canonical +Z direction rather than the reference +X direction. This
90-degree change isolates orientation at an identical spatial location. No
outcome was used to select this pose; no alternative pose was evaluated here.

| Active initial-pose field | V10.6A reference | V10.6B locked condition |
|---|---|---|
| position X | 0 | 0 |
| position Y | 0.11032208074629306 | 0.11032208074629306 |
| position Z | 0.12187743186950682 | 0.12187743186950682 |
| heading, radians | 1.5707963267948966 | 0 |

Position units are arena presentation units, not physically calibrated metres.
Y is upward; heading zero points +Z and positive yaw turns toward +X.
There are no additional initial pose variables in this runtime contract.
Both paired conditions use exactly the second pose. Initial previous observation
is absent, six HS and two DNp15 states are zero, and initial integration counters
are zero. No initial velocity override is introduced.

## Authoritative machine-readable configuration

`second_initial_condition_v10_6b_control_config.json` contains the COMPLETE existing
`ContinuousNavigationEngine.navigationLog().config` for the control, not a new
schema, event log or result. It was obtained from constructor-only configuration
inspection. Its top-level `initial_pose` is authoritative. Nested `body_model`
initial heading and eight-second duration remain immutable source-plant
provenance; `body_model_role` explicitly says they are not the active schedule.
The active runtime is CONTINUOUS_ARENA_NAVIGATION_V3 with a 30-second horizon.
Do not edit nested source-plant metadata to make it resemble this experiment.

Configuration bytes are canonical JSON: recursively lexicographically sorted
object keys, array order retained, standard JavaScript JSON number encoding,
UTF-8, no trailing newline. SHA-256 (also existing `navigationHash(config)`):
`dbc0f37db7a614c1a1076041f6319999bb86e7414b17a21992a8797e43f4a392`.
Regenerate with:
`sha256sum docs/science/second_initial_condition_v10_6b_control_config.json`
The digest excludes this document and contains no self-reference. The protocol
identity is this document plus that configuration at the V10.6B-0 commit SHA.

## Frozen controls and intervention

Control mode is `neural`; intervention mode is `output_disabled`. The only paired
configuration difference is `mode`, recorded by the existing
NEURAL_TO_HEADING_ENABLED condition flag. Both still execute the neural solver;
the intervention removes only applied neural yaw after computation and before
motor integration. Use the existing `neural_contribution_comparison_v3_1`,
`generatePair` and `validatePair`; preserve full parent and pair provenance.

Freeze 1500 completed intervals, 0.02 s body step, 200 neural substeps of 0.1 ms,
and a normal duration-completed stop at 30 s. No external stimulus switches or
pending plane changes. Landmark X coordinates remain +0.6 and -0.6, plane Z
+0.4. HS tau is 5 ms, DNp15 tau 10 ms, transfer coefficient 1, orientation
normalization horizon 50 ms, motor gain 2.5, neural yaw bound ±0.5 rad/s.
Engineering propulsion remains 0.18 units/s. Boundary policy remains
GEOMETRIC_INWARD_NORMAL_V1, margin 0.06, gain 2, maximum ±1.2 rad/s, no extra
summed-yaw clamp. All source IDs, hashes, chamber, footprint, collision rules and
other settings are pinned by the complete JSON and existing authority validator.
Seed is null and random policy NONE; no PRNG, noise or seed selection is used.

## Static admissibility, without simulation

Existing authority parsing and `locomotionBounds` give symmetric X/Z limits
±0.9654288893949121 and ±0.37542888939491215. The chosen position is strictly
inside them, at the same validated altitude and more than 0.06 from all walls.
All four values are finite and the heading is accepted by the existing constructor.
The point is distinct from both landmarks. The static boundary observation is
inactive, with no initial wall contact implied by the geometric contract.

Constructor-only checks compared the reference configuration with the locked
control: the only difference was `initial_pose.heading`. Constructing the OFF
configuration yielded equality after changing only `mode`. Step and substep
counters remained zero. Execution methods (`advance`, `calculateBoundary`,
`observation`, `velocity`) on both engine prototypes were replaced with throwing
guards during this input-only check. No neural output, trajectory, separation,
contact sequence or future run metric was calculated or inspected.

## Future V10.6B-1 execution procedure — not executed here

1. Record the V10.6B-0 commit SHA, execution source SHA and platform. Verify the
   configuration digest and protected scientific hashes before any step.
2. Parse the existing authority. Construct the control with the JSON mode,
   initial_plane and initial_pose. Compare its COMPLETE configuration with the
   locked JSON using existing canonical hashing; abort on any difference.
3. Execute exactly 1500 intervals, export the existing finite navigation parent,
   and generate/validate the existing pair. `generatePair` inherits this exact
   initial_pose and checks matched configuration excluding mode.
4. Reuse V10.6A motor derivations/report metrics. Label the future report V10.6B
   and include the frozen configuration digest and checkpoint commit. The current
   V10.6A CLI has no pose argument and must not be used as though it executes
   this protocol; a bounded explicit execution wrapper is a B-1 prerequisite.
   Its existing report helper's V10.6A label must be explicitly qualified or
   replaced in B-1 report metadata, without changing numerical semantics.
5. Write complete parent/pair and motor-interval evidence outside Git, without
   overwriting records. Repeat the identical protocol and compare outputs for
   determinism; do not tune parameters or replace the pose after seeing results.

## Predefined measurements and reporting rules

Reuse V10.6A: mean absolute computed neural yaw, mean absolute applied neural yaw,
mean absolute wall yaw (rad/s); travelled distance (presentation units); contact
episodes (existing interval-start event definition); final heading (rad); final
position separation; signed wrapped final heading difference; existing maximum
separation and wrapped-heading metrics. Exclude the terminal no-outgoing sample
from interval means. Preserve full trajectories, computed/applied contribution,
interval-start time, accepted tick, source hashes, artifact IDs and deterministic
repeat evidence. Missing telemetry is unavailable, never zero.

Report zero and nonzero effects, smaller/larger magnitudes and either signed
heading difference. Do not set a minimum effect threshold or choose another pose
for a weak/null result. Invalid authority/configuration, non-finite state,
incomplete horizon, incorrect ablation, mismatch in matched controls, failed
semantic replay or unexpected nondeterminism invalidates the run. Preserve its
diagnostics and report the failure; do not silently reset or invent output.

Later sensory and wall differences are downstream closed-loop consequences.
Interpretation remains model-level and condition-specific. Two initial poses do
not establish statistical generalisation, biological causality, measured firing,
fluorescence, learning or whole-fly emulation. No second-condition results are
reported in this protocol-lock phase.
