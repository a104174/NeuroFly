# Phase 10C — activation-scale sensitivity and mechanics interface

## Outcome and scope

The activation layer is complete as an exploratory software/model milestone.
The three-scale experiment verifies inverse normalization, unchanged temporal
shape and causal independence. Canonical fixtures remain wholly unclipped.
The complete activation trajectory is ready as an **exploratory downstream
model input**, not a physical actuator command or empirically validated force
fraction. No force, contraction, strain, torque, geometry, mechanics or frontend
integration is implemented. No biological ranking/calibration or new research.

## Repository gate and unchanged source authorities

Started clean on `main` at committed Phase 10B
`f287ea8083cfc063899a16b90efb4217b6432668`, equal to `origin/main`.
Phase 10A, 9B and 9C were committed; initial diff check passed. Required replays
passed before edits:

| Source | Unchanged artifact identity |
| --- | --- |
| Phase 10B | `4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb` |
| Phase 9B | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` |
| Phase 9C | `dfe98ec90078124f4a66df825b552d05ed317fcb89d33e0f374b99c6bfd4bfa4` |
| Phase 8Y | `030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8` |

The audit inspected Phase 10B model/config/trajectory representation, artifact
and CLI conventions, source ancestry, fixed grid/fixture identities and existing
downstream code. No force/contraction/mechanics implementation or physical
actuator interface was found. Existing visual contraction control stimuli,
schema prohibitions and frontend presentation intensity are not muscle dynamics.
Phase 9E is a historical regression, not an experiment input; its identity is
`2c775d6e00d74b3b3a3ca5a36bb84fd4032959d29f3c7d4c8b0bca934e2942b8`.
No historical module/config/artifact is modified or migrated.

## Experiment design and authority reuse

Source model: `static_normalized_muscle_activation_model_v1`, with reference
`activation_scale_mV_eq = 10.0`, classified `MODEL_ASSUMPTION`. The experiment
replays Phase 10B and its canonical persisted Phase 9B source, then calls the
**unchanged** Phase 10B `transform_response()` once per scale on the same loaded
electrical response. There is no copied activation equation or sensitivity-only
simulator. Electrical replay reconstructs solely to validate source authenticity;
no electrical dynamics are rerun for sensitivity cells or retuned.

Exactly three scales: 5, 10, 20 mV_eq, corresponding to 0.5×, 1×, 2× reference,
in ascending order. All source arrays, proxy domain, body/side identities,
rectification, ceiling, same-boundary semantics and provenance rules remain fixed.
The source grid is 0.1 ms, 80 intervals, 81 boundaries through 8 ms.

Each cell runs ZERO_EVENT_CONTROL, RIGHT_SINGLE_EVENT, LEFT_SINGLE_EVENT,
BILATERAL_SIMULTANEOUS_EVENT, RIGHT_REPEATED_EVENTS and LEFT_REPEATED_EVENTS.
There are 18 fixture runs, 36 independent fixture/body trajectories and 2,916
evaluated samples. This is model accounting, not biological sample size.
One reference cell at scale 10 exactly reproduces the Phase 10B canonical bytes
and artifact identity. It is reference-by-history, never best or calibrated.

## Per-cell canonical results

All values below are dimensionless model activation. Right/left responses under
identical inputs/shared config agree only as model symmetry. Inactive instances
and zero controls remain exactly zero. Single/bilateral peak is at step 10 / 1 ms;
repeated peak is at step 30 / 3 ms. Final means stored boundary 80 / 8 ms.

| Scale (mV_eq) | Single peak | Repeated peak | Repeated final | Maximum activation | Clipped samples | Clipped trajectories | Reference |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 5 | 0.4 | 0.45413411329464504 | 0.0030599315858559828 | 0.45413411329464504 | 0 | 0 | No |
| 10 | 0.2 | 0.22706705664732252 | 0.0015299657929279914 | 0.22706705664732252 | 0 | 0 | Yes |
| 20 | 0.1 | 0.11353352832366126 | 0.0007649828964639957 | 0.11353352832366126 | 0 | 0 | No |

Maximum unclipped ratios equal the listed maxima in each cell. Counts classify
samples **at or above** the scale as ceiling-reaching (including exact equality),
consistent with Phase 10B's `ceiling_sample_count`. A separate count of strictly
above-scale samples diagnoses ceiling amplitude loss; it is also zero everywhere.
No empirical thresholds or interpretation are attached to these counts.

## Verified sensitivity and information preservation

Every canonical sample was checked, not only peaks. With scale 5/10/20 the
activation arrays obey inverse scaling: the first is twice the second, the
second twice the third. In the positive unclipped region, activation × scale
reconstructs electrical deviation up to ordinary arithmetic roundoff. Equation
checks use `rel_tol=1e-12`, `abs_tol=1e-14`, not biological acceptance windows.
Zero drivers give exact zero. No negative canonical driver exists; rectification
cases are tested locally, without altering canonical sources.

Source fixture/body order, source trajectory IDs, proxy references and full
boundary/time grid are retained. Each cell preserves two independent streams
`800146/R` and `804642/L`; bilateral output matches corresponding unilateral
output without coupling or aggregation. All samples remain finite and bounded.
Canonical peak timing remains unchanged across scales. In the unclipped regime
the positive electrical temporal shape is preserved up to a constant multiplier;
scale introduces neither delay nor temporal memory. Temporal persistence remains
entirely Phase 9B's electrical retention.

Diagnostic result: `CANONICAL_FIXTURES_REMAIN_IN_UNCLIPPED_LINEAR_REGIME`.
This is a model-input finding, not evidence that real muscle responses are linear
or unsaturated. In artificial clipped cases the ceiling can create plateaus and
earliest-maximum ties; canonical timing invariance is not asserted universally.

## Intentional information loss outside the canonical regime

The Phase 10B ceiling maps distinct values at/above scale to one. Above-scale
amplitudes therefore cannot be recovered from activation alone. Test-local
drivers at scale, twice scale and three times scale give the same output 1 for
each experiment scale. Full source ancestry retains the original electrical
arrays for audit, but does not restore that information in the activation signal.

Rectification maps all negative deviations to zero, discarding their magnitude
and sign distinction relative to zero. Test-local negative inputs protect this
property. Neither operation is a measured TTM physiological law.

## Layered uncertainty and parameter confounds

Phase 9 event scale sets electrical magnitude, which propagates into activation.
Phase 9 effective tau sets temporal retention, which propagates into activation
shape. Phase 10 activation scale adds normalization uncertainty. None is
biologically calibrated; Phase 9 structural separability is not physiological
parameter identification.

Below clipping, activation amplitude depends on electrical event scale divided
by activation scale. Observing activation amplitude alone cannot independently
identify those two scale choices. Retaining both config identities and source
arrays makes this explicit rather than resolving the biological confound.

For a hypothetical future linear downstream gain, output would be proportional
to that gain × electrical deviation / activation scale. Thus a future force
scale and activation scale would enter as a ratio: multiplying both by the same
factor leaves the hypothetical unclipped force output unchanged. This is a
conditional mathematical finding, **not an implemented force law**. Independent
constraints or a declared normalization convention would be needed to distinguish
them. Do not silently absorb the activation scale, set it to one, fit either
parameter or call the ceiling maximal physiological force. Clipping/nonlinear
future dynamics may alter the simple degeneracy but do not supply calibration.

## Mechanics-input candidates and readiness

| Candidate | Information and implication | Assessment |
| --- | --- | --- |
| Full activation trajectory | Preserves normalized positive temporal shape, step/time and causal ancestry | Preferred exploratory input |
| Peak only | Discards duration, retention and repeated-event evolution | Insufficient as the sole time-dependent downstream driver |
| Binary activated/not activated | Adds an unsupported threshold and loses magnitude/temporal detail | Not selected |
| Direct electrical deviation | Bypasses the explicit activation boundary and its assumptions | No reason to bypass for the next slice |

The recommended **conceptual** downstream interface consumes complete
`activation_proxy` arrays with unchanged grid, body/side, source electrical
trajectory and activation config/artifact references, and virtual proxy ancestry.
Shared arrays/trajectory envelopes may carry these fields without repeating
them at every sample. No new interface implementation or metadata contract is
created here. The ready claim is restricted to exploratory mathematical models;
physical actuator commands are not ready.

Activation contains no muscle length, shortening, strain, velocity, work or
force. A value of one is only `MODEL_NORMALIZATION_CEILING`. Side-qualified
causal streams must not be merged into whole-TTM or whole-body activation.
The Phase 8Y domain remains an exploratory observation proxy, not an exact
physical fiber. A later body-mechanics model must explicitly choose what physical
actuator it represents and how each causal stream is mapped to it.

## Physical-force blockers and Phase 11 direction

The project has no pinned/calibrated physical force scale or maximum force,
muscle/attachment geometry, actuator mapping, moment arms, length/velocity state,
contraction kinetics or force-length/force-velocity parameters for these proxy
instances. These quantities are absent as a usable physical mechanics interface;
the statement does not claim that the literature contains none. Dimensional
physical force and body motion cannot be obtained merely by interpreting the
dimensionless activation as a physical fraction.

The smallest next direction is **one Phase 11A first contraction/force-model
decision**, starting by assessing a dimensionless downstream output proxy versus
a physical force model. An explicit dimensionless exploratory proxy can advance
model-space computation without fabricated Newtons or geometry. Phase 11A must
define one bounded executable Phase 11B if defensible, enumerate scale/kinetics
assumptions and normalization confounds, preserve full temporal causal streams,
and state which physical actuator mapping is deferred. It must not quietly
equate a proxy with shortening or force. If the goal instead becomes physical
body motion, explicit actuator/geometry mapping is a prerequisite. No long
metadata-phase chain, Phase 10D or force implementation is proposed here.

## Compact artifact and offline replay

Experiment schema: `static_normalized_muscle_activation_sensitivity_v1`.
Artifact schema: `static_normalized_muscle_activation_sensitivity_artifact_v1`.

- Artifact ID: `b605e51e4ed42813d2562d61aa58129ed3d5b43e875ab1fd0de98ca0360c9a6e`
- Config hash: `7b3826904b71182fe1dab3cbca9d2897e1c02ff23c2c2a2c448139599721d88e`
- Result hash: `7f6e580b770741967f0dda3e87dcb3c9b1288575ccb2b872035751ed562d36dc`
- Reference cell ID: `a06eae7a35f4e7926413d73923f168986e7cbd4fc4acfc156f292b1972512bc0`
- Total size including manifest: 28,144 bytes.

Each cell hashes the source Phase 10B identity, fixed Phase 9B identity and explicit
Phase 10B model config. It stores reconstructed activation identities/hashes,
12 per-trajectory summaries and clipping diagnostics, not repeated full arrays.
Fixture order follows the source and body order is stable. Source grids/arrays
are recoverable through the pinned artifacts. Reference marking is singular and
protected, not biological preference. Readiness decisions are modelling metadata,
not biological observations or force outputs.

```sh
python -m neurofly.muscle_activation_sensitivity_cli generate
python -m neurofly.muscle_activation_sensitivity_cli inspect ARTIFACT_DIRECTORY
python -m neurofly.muscle_activation_sensitivity_cli replay ARTIFACT_DIRECTORY
```

Generation/replay is offline, deterministic and timestamp-free, with staged
immutable writes and existing-artifact validation. Replay validates Phase 10B
and its fixed Phase 9B source, regenerates three cells through the unchanged
activation transform, verifies behavior, then reproduces summaries/order,
identities, hashes, canonical bytes and manifest/directory identity. Rehashed
grid/reference/source/cell/fixture/summary/clipping/decision mutations fail exact
reconstruction. No fit/rank/best-cell command exists. Generated data is ignored.

## Decisions

| Gate | Decision |
| --- | --- |
| Sensitivity | `ACTIVATION_SCALE_SENSITIVITY_VALIDATED` |
| Mechanics interface | `FULL_ACTIVATION_TRAJECTORY_READY_AS_EXPLORATORY_MECHANICS_INPUT` |
| Clipping | `CANONICAL_ACTIVATION_REMAINS_UNCLIPPED` |
| Information | `TEMPORAL_SHAPE_PRESERVED_IN_CANONICAL_UNCLIPPED_REGIME` |
| Confounds | `ACTIVATION_SCALE_EXPLICITLY_CONFOUNDED_WITH_UPSTREAM_AND_FUTURE_GAINS` |
| Phase 10 | `PHASE10_ACTIVATION_LAYER_COMPLETE` |
| Next direction | `PHASE11_ASSESS_FIRST_CONTRACTION_FORCE_MODEL` |

Phase 10 completion is exploratory and does not waive the remaining external
empirical-validation, physiological calibration or physical-actuator limitations.

## Acceptance and quality gates

Phase 10C: **PASS**. Focused tests: 27 passed. Full `python -m pytest`: 857
passed, 1 deselected, two dependency deprecation warnings. Ruff check and format
check (265 files), plus diff check, pass. Frontend regression: 38 tests, lint,
typecheck and build pass; build-generated declaration changes were restored.
Phase 10B/9B/9C/9E and proxy regressions pass unchanged; Phase 8U remains zero-ready.
Canonical sensitivity replay reproduces bytes/identities/hashes. Generated data
is Git-ignored. Only the intended Phase 10C modules/tests/docs remain changed;
no historical source, frontend/API or model implementation was modified.
No commit or push. No Phase 10D.
