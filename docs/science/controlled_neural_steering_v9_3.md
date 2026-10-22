# Controlled neural steering v9.3 — first offline slice

## Preregistered protocol (before six-condition execution)

Baseline: `aad4ea60251c1b811046e18834ef56819835bcb6`, main. Seven existing
untracked v9.2/v9.2b files are preserved by SHA-256; their classifications remain
unchanged. This experiment has no dependency on the external G3 adapter.

The reference observer scene has R=(+0.6,+0.4), L=(-0.6,+0.4) in XZ.
An X reflection with consistent anatomical labels leaves this symmetric scene
unchanged. It is therefore rejected as a directional intervention. The already
supported visual-plane intervention is selected **before observing experimental
results**: V1 reflects the scene through Z=0, mapping (x,z) to (x,-z).
V1 has R=(+0.6,-0.4), L=(-0.6,-0.4). This is a front/back horizontal-plane
`CONTROLLED_VISUAL_MIRROR`, not global visual-motion inversion, not an anatomical
hemisphere swap, and not a reproduction of any experimental G3 stimulus.

The actual observer calculates the signed bearing increment
`bearing_shift_rad = atan2(bz*ax-bx*az, bx*ax+bz*az)` for each fixed landmark.
The bearing increment and completed body heading increment are both originally
in radians. Each is divided by `2π` to convert to turns before subtraction:

```text
u_side = clamp(
    (50 / interval_ms) * side_basis * (
        bearing_shift_rad / (2π) - heading_increment_rad / (2π)
    ),
    -1, +1
)
side_basis: R = +1, L = -1
```

The existing 50-ms normalization is applied to the difference in turns; the
right/left side basis determines its sign. This is an engineering observation,
not measured biological optic flow. Altitude is excluded. Mirroring only the scene while
holding the body's pose fixed does **not** generally negate that quantity.

For pure lateral displacement along Z=0 with constant heading, Z reflection
negates the cross product and preserves the dot product; both sensory descriptors
therefore negate. For pure yaw at a fixed location, landmark bearing increments
are zero, so both scenes give identical heading-derived descriptors. Mixed
motion has no exact global inversion prediction. These are mathematical
predictions, not physiological claims. No visual parameters will be tuned.

Gate A: run fixed 20-ms observer diagnostic sequences (static, +X translation,
positive body yaw, mixed motion) under both scenes. Require zero baseline,
lateral sign reversal and yaw equality within 1e-12. Diagnostics are prescribed
computational poses, never biological observations or closed-loop inputs.

Six conditions: E1 V0/OFF, E2 V0/ZERO_PROJECTION, E3 V0/ON,
E4 V1/OFF, E5 V1/ZERO_PROJECTION, E6 V1/ON. Each uses the unmodified 12-second
reference program, identical initial body/neural states, arena, model and timing.
OFF and ZERO both integrate neural state for telemetry, matching existing v9
semantics; neither applies neural yaw. ON uses the original bounded projection.

Predeclared hypotheses and gates:
- H0: no sensory change (max bilateral difference <=1e-10).
- H1: diagnostic lateral reversal and yaw equality (absolute residual <=1e-12).
- H2: ON neural histories distinguishable (max HS/DNp15 difference >1e-10).
- H3: visual-by-neural interaction in **unwrapped final heading** exceeds 1e-10 rad.
- H4: all OFF/ZERO body histories are exactly equal to the legacy v8 reference.

Primary metric is final heading. Interaction is
`[heading(E6)-heading(E4)] - [heading(E3)-heading(E1)]`.
Secondary metrics: final XYZ separation, integrated absolute applied neural
angular command, mean signed neural turn, peak readout, saturation fractions,
first heading/position difference >1e-10, and recorded boundary events.
No statistical significance or biological effect is inferred. Hypothesis rejection
is a valid scientific result when engineering controls and replay checks pass.

Implementation, results, quality gates and reproduction details follow after
execution; the definitions and thresholds above remain fixed.

## Implementation and actual results

Implementation composes `FlightPoseNeuralAdapter.observeAndAdvance`, the inherited
`InteractiveNeuralEngine.observation/calculateBoundary`, `projectFlightYaw`, and
`FlightEngine.advance/advanceWithTurn`. No production file is changed. Each
condition allocates its own adapter, six HS/two DNp15 states and plant; observations
use only its local previous/current accepted body frames. No sensory trace from
another condition or diagnostic probe is reused.

The selected HS R IDs remain 10015/10016/10023, HS L 10034/10181/10419,
DNp15 R/L 11215/12069. Neural contract SHA-256 remains
`371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074`;
observer pin `49e91a10fa49c5d7004f28249b63f334a0e23767c20108f5578a0e2586c9767a`.
The CLI authenticates the source artifact raw SHA-256 before parsing:
`17d335358a4f5cf4ed98b9682b103a81419cf82504203ce1bc72a7d76285d748`.
Structural contacts are provenance, not calibrated physiological weights.

Initial body: {"step": 0, "time": 0, "position": [0, 0.11032208074629306, 0.12187743186950682], "velocity": [0, 0, 0], "heading": 1.5707963267948966, "state": "grounded", "stateSince": 0, "commandId": null, "contacts": [], "events": []}

All conditions start with six zero HS proxies and two zero DNp15 proxies. Each
executes 600 body intervals and 120,000 neural substeps: **720,000 substeps**
across the six conditions. OFF and ZERO both compute the neural model but apply
zero neural yaw, exactly as existing v9 does. The separate observer diagnostic
executes 33,600 additional neural substeps because the public adapter computes
its neural boundary along with the observation (4 probes × 2 scenes × 21 calls ×
200); those states never seed the six conditions. Total construction workload
is 753,600 neural substeps. No rendering clock participates.

For interval i: observe completed body motion i-1→i; integrate the held sensory
input over 200 old-state simultaneous neural updates; project that interval
readout; integrate v8 once from body i→i+1. Boundary zero has no completed motion
and a neutral observation. Final boundary 600 has no outgoing neural interval.

Projection is unchanged: `rawOmega=2.5*delta_q/0.020`,
`omega=clamp(rawOmega,-0.5,0.5)`, `neuralTurn=omega/0.8` for ON (zero for controls),
`appliedTurn=clamp(engineeringTurn+neuralTurn,-1,1)`. Heading still changes only
inside the v8 plant, which ignores yaw while grounded or landing.

| Condition | Scene / mode | Final X | Final Y | Final Z | Final heading rad |
|---|---|---:|---:|---:|---:|
| E1 | V0 / OFF | 0.639532893281 | 0.110322080746 | -0.168962575892 | 2.050796326795 |
| E2 | V0 / ZERO_PROJECTION | 0.639532893281 | 0.110322080746 | -0.168962575892 | 2.050796326795 |
| E3 | V0 / ON | 0.743203454314 | 0.110322080746 | 0.061665339708 | 1.462534878738 |
| E4 | V1 / OFF | 0.639532893281 | 0.110322080746 | -0.168962575892 | 2.050796326795 |
| E5 | V1 / ZERO_PROJECTION | 0.639532893281 | 0.110322080746 | -0.168962575892 | 2.050796326795 |
| E6 | V1 / ON | 0.666279320461 | 0.110322080746 | -0.155177159005 | 2.186966175103 |

The Y column is formatted for reading; recorded ground Y retains its historical
full value 0.11032208074629306. Body records are never rounded to neural telemetry
precision. All six finish grounded with velocity [0,0,0].

## Observer diagnostic and interpretation

At the first +0.001 X displacement over 20 ms, heading=0 and body Z=0:
V0 (right,left)=(-0.0003064207000920774,+0.00030571439065063435),
V1=(+0.0003064207000920774,-0.00030571439065063435). Reversal residual is zero
through all 20 tested intervals. Static descriptors are zero (including signed
IEEE zero). For +0.01 rad yaw per interval, both scenes give
(-0.0039788735772973835,+0.0039788735772973835); equality residual is zero.
Mixed motion does not invert. Diagnostic rows carry an outer explicit prescribed
pose origin; their raw observer producer tag is inherited from the flight adapter
and must not be interpreted as a claim of genuine flight-generated poses.

Full scene+body Z reflection would also require heading→pi-heading, negating
bearing and heading increments. The primary experiment does **not** reflect the
body. Its initial body Z is nonzero, further excluding global inversion symmetry.
The legitimate manipulation is solely an existing visual-plane configuration.

## Causal comparisons and hypotheses

```json
{
  "D_V0": {
    "a": "E3",
    "b": "E1",
    "heading_a_minus_b": -0.5882614480570001,
    "final_xyz_separation": 0.2528573128839617,
    "first_material_boundary": 152,
    "first_material_time_s": 3.04
  },
  "D_V1": {
    "a": "E6",
    "b": "E4",
    "heading_a_minus_b": 0.13616984830800005,
    "final_xyz_separation": 0.030090016378251212,
    "first_material_boundary": 152,
    "first_material_time_s": 3.04
  },
  "ON_visual_comparison": {
    "a": "E6",
    "b": "E3",
    "heading_a_minus_b": 0.7244312963650001,
    "final_xyz_separation": 0.23008257564868245,
    "first_material_boundary": 152,
    "first_material_time_s": 3.04
  },
  "final_heading_interaction": 0.7244312963650001,
  "max_ON_neural_difference": 0.0048977454,
  "max_ON_sensory_difference": 0.0049143006
}
```

All four OFF/ZERO histories equal all 601 legacy v8 boundaries exactly. V0 ON
and V1 ON also equal the existing v9 ON and VISUAL_PERTURBATION body histories
respectively, demonstrating composition without controller changes. Body
divergence first exceeds the predeclared 1e-10 threshold at boundary 152 (3.04 s).
At boundary 151, motion from 3.00→3.02 s first supplies a nonzero sensory input;
the neural interval then changes the next accepted heading.

H0 rejected: sensory observations differ. H1 supported within the declared
restricted diagnostic (not a global inversion). H2 distinguishable: maximum
ON HS/DNp15 difference 0.0048977454 model units. H3 distinguishable: final-heading
interaction 0.7244312963650001 rad. H4 exact equality. These deterministic
findings are not statistical biological effects or experimental replication.

At 6.24 s, both ON runs still have engineering turn +0.65. Their telemetry:

| Field | E3 V0 ON | E6 V1 ON |
|---|---:|---:|
| sensory R | -0.0047254655 | -0.0014271153 |
| sensory L | +0.0016723291 | +0.0019467173 |
| old DNp15 R | -0.0046989655 | -0.0014263550 |
| old DNp15 L | +0.0016844848 | +0.0019484762 |
| mean yaw_drive_eq | -0.0063894485 | -0.0033744137 |
| integrated delta_q | -0.0025557794 | -0.0013497655 |
| projected neural turn | -0.3993405302 | -0.2109008589 |
| combined turn | +0.2506594698 | +0.4390991411 |
| next heading | 1.781869567703 | 2.103679329999 |

Neural telemetry uses the existing v9 1e-10 reporting resolution. Projection and
heading computations use live precision, not those printed numbers. Later sensory
differences include accumulated pose-dependent feedback; they are not the direct
effect of the visual transformation alone. Both neural readouts can have the
same sign at a later time despite their different early responses.

## Saturation, commands and contacts

| Condition | Mean signed neural turn | Integrated absolute neural angular command | Potential projection clamps | Applied projection clamps | Combined clamps |
|---|---:|---:|---:|---:|---:|
| E1 | 0.0000000000 | 0.0000000000 | 89 | 0 | 0 |
| E2 | 0.0000000000 | 0.0000000000 | 89 | 0 | 0 |
| E3 | -0.0624979860 | 0.8120621006 | 0 | 0 | 0 |
| E4 | 0.0000000000 | 0.0000000000 | 0 | 0 | 0 |
| E5 | 0.0000000000 | 0.0000000000 | 0 | 0 | 0 |
| E6 | 0.0170701503 | 0.8422630857 | 0 | 0 | 0 |

Observer clipping and additional neural-input clipping are zero in every
condition. The solver receives those same bounded observer descriptors and adds
no separate clamp. E1/E2 potential projection saturation is 89/600=14.8333%, first
interval 253 (5.06 s), raw peak 0.5488591992, bounded peak 0.5 rad/s; their
**applied contribution is zero**. The active_projection_clamped counter describes
potential clamping during yaw-enabled plant phases, not enabled neural influence.
E3/E6 have no projection or combined clipping. Peak raw projected omega is
0.3723178699 / 0.3174265163 rad/s, and peak combined turn
0.7575279862 / 0.7133616475. All zero-clamp cases have fraction 0 and no first
saturated interval; full raw/post-clamp diagnostics are in each summary.

The integrated neural command includes values supplied while landing/grounded,
when the plant may ignore yaw. The separate yaw-enabled integrals are
0.7981676100 rad (E3) and 0.8145594916 rad (E6), compared with all-interval command
integrals 0.8120621006 / 0.8422630857. Neither is a measured physiological rate.
All runs have the same FLOOR contact at step 572, 11.44 s, after the LAND command
at 9 s; no wall/ceiling contacts occur. Thus differing wall contacts or applied
saturation do not explain the paired ON difference in this protocol.

## Identity, export and semantic reconstruction

Input SHA-256: `d07d44177a8360a0df91b3f82a095b9fbea7fcd2a1a805418ac6a6f2eee91548`

Result SHA-256: `4a4bb929e5814b795483b612a0a1de4403d0d1d00e5a15a7e3d970bcae0a14cd`

Artifact ID: `1ed06c4892c3f7101fb8b1c6c5ee78d8c72ea8f654efc9a819d05bf3e92f092b`

The versioned protocol includes scenes, hypotheses, fixed thresholds, modes, full
v9 source/model provenance, initial body/neural states, trial commands, projection,
timebase, precision and no-randomness policy. `flightCanonical/flightHash` are
reused. Live computation is unchanged; only neural/probe reporting rounds to
1e-10, matching v9. Metrics derive from live histories; body metrics use exact
recorded states. Machine paths, clocks, runtime timing and memory metadata are
excluded from scientific identity.

Verification validates the fixed input contract, dimensions/order/hashes and
re-executes the complete experiment. Recomputed superficial hashes cannot bypass
changed model input, scenes, commands, conditions, body/neural histories or derived
metrics. Recorded seeks are array reads and never advance authoritative state.
No legacy export namespace, storage or replay schema is modified.

## Reproduction and performance

From web/:
```sh
PYTHONDONTWRITEBYTECODE=1 node --import tsx tools/controlledNeuralSteering.ts \
  --output /tmp/neurofly-v9-3-run.json
PYTHONDONTWRITEBYTECODE=1 node --import tsx tools/controlledNeuralSteering.ts \
  --verify /tmp/neurofly-v9-3-run.json
```

The CLI checks source raw bytes, requires an explicit external output path,
refuses overwrite, and exits nonzero for computational/integrity errors. A valid
negative hypothesis remains an ordinary completed model experiment. No browser,
experimental workbook or G3 artifact is used. Output consists of the scientific
JSON plus a separate summary/performance JSON.

Observed construction: probe 22.06 ms; six conditions 242.79 ms; complete construction including canonical hashing/control reference 439.10 ms; serialization 15.84 ms. Artifact 4,170,941 bytes. Fresh semantic verification 807.58 ms. Maximum process RSS 184,664 KiB; final RSS 189,095,936 bytes. These are local Node measurements, include runtime initialization and retained output, and establish no leak-free or GPU-performance claim.

## Scientific limitations and one next experiment

Only internal model causality is established. The observer has two static
landmark samples, no retina/FOV/occlusion/depth/altitude model. The reduced neural
model omits the larger circuit mechanisms discussed in prior audits. Proxy
activity is neither calcium, measured membrane voltage nor calibrated firing
rate. The yaw projection and plant remain engineering hypotheses. This result
does not activate v9.2b, revise v9.2, or reproduce Erginkaya stimuli.

Exactly one next falsifiable experiment: a separately versioned delayed projection
onset control under V0. Keep the real neural model advancing, but apply ZERO
until a preregistered boundary (for example 5.00 s), then use the unchanged ON
projection. Compare with always-ZERO and the existing immediate-ON reference.
Independent variable: projection onset boundary. Reuse the same observer, solver,
public projection modes and flight plant. Require exact delayed-ON/always-ZERO
body and neural equality before the intervention, no prematurely changed command,
and first downstream heading change only after a nonzero accepted ON command.
This isolates onset attribution without a new visual-input seam, sensory biology
or gain tuning. It is not implemented here.


## Executed quality gates and preservation

- Final frontend suite: **316 passed**, including **12 new controlled-experiment
  tests** and existing v3–v9, visual encoder, wing/gait/motor, flight/program/
  trajectory and semantic-integrity tests. Initial focused runs are subsets,
  not additional unique tests. The initial signed-zero assertion was corrected
  to mathematical zero equality; no model equation or tolerance changed.
- Independent Python checks on **all six own-pose histories**: maximum error
  against serialized neural/observer telemetry **4.999669558566899e-11**,
  within the declared 1e-10 reporting resolution and stricter than the unchanged
  1e-8 legacy parity tolerance. Existing raw v9 parity also passed with maximum
  error **2.6020852139652106e-18**. Neither validates an independent Python flight
  plant; none was added.
- Focused Python batch: **280 passed** in 92.21 s, including 44 v9.2 benchmark
  and 62 v9.2b contract tests. All overlap with any broader Python attempt.
- Optional complete Python run collected 1,821 selected tests (one integration
  deselection), then was deliberately interrupted after **175 passed**, no
  failures observed, at 373.62 s due the cost of legacy replay tests. Exit 2
  records KeyboardInterrupt. **No complete Python-suite pass is claimed**;
  no missing-fixture explanation is inferred from this incomplete run.
- `npm run lint`, `npm run typecheck`, `npm run build`: passed on final code.
  The build's generated `web/next-env.d.ts` route-import rewrite was restored
  exactly from the known clean baseline. It is not part of the change.
- Repository Ruff check and format verification passed (433 Python files).
- Existing frozen runtime bundle verified with all **74 pinned files**.
  Isolated provisioned-runtime validation passed **eight historical replay
  gates, five canonical playback identities, HTTP/readiness and invalid-pin
  no-fallback checks**, with network/original-checkout writes denied.
- Original v8 input/result hashes passed exactly in the new tests and existing
  v9 regression tests. No historical fixtures were regenerated.
- `git diff --check`, final preservation checks and Git inventory passed.

Actual commands (repository root unless noted):

```sh
# From web/:
PATH="/home/l1tren/projetos/NeuroFly/.venv/bin:$PATH" \
  PYTHONDONTWRITEBYTECODE=1 npm test
npm run lint
npm run typecheck
npm run build
# From repository root:
NEUROFLY_FIG1_SOURCE=/tmp/neurofly-v9-2a/figure1.xlsx \
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -p no:cacheprovider -q \
  tests/test_empirical_hs_dnp15_benchmark.py \
  tests/test_horizontal_visual_motion_contract.py \
  tests/test_neural_flight_reference.py \
  tests/test_experimental_neural_locomotion.py \
  tests/test_hs_dnp15_neural_validation.py \
  tests/test_orientation_to_horizontal_motion.py \
  tests/test_planar_steering_shadow.py tests/test_exploratory_course_control.py
# Optional full run, interrupted as reported above:
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -p no:cacheprovider -x -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m neurofly.runtime_bundle_cli verify \
  --inventory docs/deployment_runtime_inventory_v2.json \
  --manifest docs/neurofly_runtime_bundle_manifest_v1.json \
  --expected-manifest-id e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882 \
  --archive data/derived/runtime_bundles/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B tools/provisioned_runtime_validation.py \
  --manifest docs/neurofly_runtime_bundle_manifest_v1.json \
  --expected-manifest-id e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882 \
  --archive data/derived/runtime_bundles/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B /tmp/neurofly-v9-3/preserve.py
git diff --check
```

External JSON outputs and logs are under `/tmp/neurofly-v9-3`. No new external
scientific data or package dependency was acquired. No biological fixture was
fabricated. The seven prior files remain unchanged and unstaged. New files only:

- `web/src/lib/controlledNeuralSteering.ts`
- `web/tests/controlled-neural-steering.test.ts`
- `web/tools/controlledNeuralSteering.ts`
- `docs/science/controlled_neural_steering_v9_3.md`

Tracked modifications: none. No staging, commit, push, Preview/Production
 deployment, environment or infrastructure change occurred. v9.2b remains
CONTRACT_ONLY. No subsequent experiment was implemented.

Decision: `CONTROLLED_NEURAL_STEERING_EXPERIMENTS_V9_3_LOCAL_VALIDATED`.

## Initial and final seven-file SHA-256 inventory

| File | Preserved SHA-256 |
|---|---|
| `src/neurofly/empirical_hs_dnp15_benchmark.py` | `947a42774b710d3c46d7df8caf57084286608f6949bf7f9c9e39e00e1db20bfd` |
| `tests/test_empirical_hs_dnp15_benchmark.py` | `ffbb45282061afbe734d979bbffb0b64ad978384b989a353a6d7fbd2b10a2d49` |
| `docs/science/empirical_hs_dnp15_v9_2_source.json` | `0186d88c281119c14f52a1971920ecfbcc4ea24d7315afa5e63f39fefa72b7cd` |
| `docs/science/empirical_hs_dnp15_response_benchmark_v9_2.md` | `a01d12e6896215ddb5c0615a53dc8756c27735fd334a35db9b574143f128ca1b` |
| `src/neurofly/horizontal_visual_motion_contract.py` | `7e7f5234c6f356467fbcf5e60b1889b1dc63506e0f4b054daab74920ec57e0e3` |
| `tests/test_horizontal_visual_motion_contract.py` | `697982507bb9a57090bc93f9882332a256aee5b86b61adabe029cd508fe86d38` |
| `docs/science/horizontal_visual_motion_adapter_v9_2b.md` | `9527098e551eb32dd34e091692f77b0bc78dca7fac2f43262e21ef625bdc4ce9` |
