# Phase 9C — deterministic exploratory G1-proxy sensitivity

## Repository gate and unchanged authorities

Work started clean at committed Phase 9B HEAD
`954c4c020ff3ae08aa1f2e8a7b99aff6a5bd9d68`, matching `origin/main`.
Canonical Phase 9B offline replay passed before edits, recursively validating
Phase 8W inputs and Phase 8Y domain plus Phase 8U/8S/K authorities. No model,
source token, proxy, observation or observation-mapping definition is changed.

Source model: `passive_g1_proxy_electrical_model_v1`.
Source artifact:
`72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f`.
Its reference configuration remains 0 mV-equivalent reference, 1 ms effective
tau, 2 mV-equivalent/token scale, 0.1 ms grid and 80 intervals. Principal
numerical values remain `MODEL_ASSUMPTION`, not evidence-derived physiology.

## Experiment design

Experiment schema: `g1_proxy_passive_electrical_sensitivity_v1`.
The experiment calls the existing Phase 9B `build_response()` exactly once per
cell. It does not copy or fork the simulator/update equation. Analytical
closed-form checks are diagnostics of that implementation, not new dynamics.

Relative factors are exactly 0.5, 1 and 2 for both tau and event scale:

- Tau: 0.5, 1, 2 ms.
- Event scale: 1, 2, 4 model-space mV-equivalent per token.
- Ordering: ascending tau factor, then ascending event-scale factor.
- Exactly 9 cells × 6 fixtures = 54 fixture runs, with 108 independent
  fixture/body trajectories and 8,748 computed boundary samples.

All source schedules, body/side identities, reference coordinate, grid,
initialization, update order, timing assumption and virtual proxy domain are
fixed. Each cell retains the same eight source tokens, four per causal body
across independent fixtures. Neither aggregate trajectories nor repeated token
uses constitute a biological sample size or firing rate.

The six fixtures are `ZERO_EVENT_CONTROL`, `RIGHT_SINGLE_EVENT`,
`LEFT_SINGLE_EVENT`, `BILATERAL_SIMULTANEOUS_EVENT`, `RIGHT_REPEATED_EVENTS`,
and `LEFT_REPEATED_EVENTS`. No new biological scenario or source event exists.

Reference voltage is not swept: it is an additive coordinate offset to
`proxy_voltage_mV_eq` and does not enter deviation dynamics. Changing it would
translate reported voltage coordinates without changing decay, event increments
or accumulation. Its biological interpretation remains unresolved; not sweeping
it does not identify a biological resting potential.

## Model diagnostics and numerical checks

These are explicitly **model-internal diagnostics**, not empirical observation
operators, calibration targets or acceptance windows.

For one input at step 10, inspect post-input deviation and retention at step 20:
10 intervals, or 1 ms later. The normalized retention diagnostic is
`u[20]/u[10]`. Repeated inputs occur at steps 10 and 30: 20 intervals, or 2 ms
apart; inspect `u[30]` and `u[30]/event_scale`.

For fixed tau and schedule, binary factors give exact computed scale linearity:
`u_k[n] = k*u_reference_scale[n]`. Normalized `u[n]/event_scale` is identical
across the three scale cells. These exact results are protected for this
power-of-two grid; they are not a promise of bit-exact scaling for every possible
floating-point factor.

For an isolated input, `u[10]=event_scale` independently of tau. Later samples
satisfy `u[10+k]=event_scale*exp(-k*dt/tau)` up to floating-point roundoff.
Normalized retention isolates tau and is independent of scale. The 1 ms
retentions are approximately 0.135335283, 0.367879441 and 0.606530660 for tau
0.5, 1 and 2 ms respectively. Larger tau strictly increases the retained
single-event deviation at every subsequent boundary through step 80.

For repeated inputs, the second peak is
`event_scale*(1+exp(-2/tau))`. Its normalized ratio is tau-dependent and
scale-independent; larger tau retains more first-event state and increases
the second peak. This is linear passive-state accumulation, not biological
facilitation, depression or release-history evidence.

Closed-form checks allow only numerical roundoff (`rel_tol=1e-12`,
`abs_tol=1e-14`); these constants are equation-check allowances and **not**
empirical model-acceptance tolerances. Exact equality is used for zero input,
binary scale linearity and normalized invariance. No scientific inference is
made from numerical test tolerances.

## Nine-cell summary

Peak/final amplitudes below are model-space mV-equivalent, not observed voltage.
Single final is step 80 after the isolated step-10 input. Repeated peak is step
30 after the second input. Both causal sides yield these values only as a
model property of identical schedules and the shared assumption config.

| Tau (ms) | Scale | Single peak | Single final | Repeated second peak | Second peak / scale | Reference |
|---:|---:|---:|---:|---:|---:|---|
| 0.5 | 1 | 1 | 0.000000831529 | 1.018315639 | 1.018315639 | no |
| 0.5 | 2 | 2 | 0.000001663057 | 2.036631278 | 1.018315639 | no |
| 0.5 | 4 | 4 | 0.000003326115 | 4.073262556 | 1.018315639 | no |
| 1 | 1 | 1 | 0.000911881966 | 1.135335283 | 1.135335283 | no |
| 1 | 2 | 2 | 0.001823763931 | 2.270670566 | 1.135335283 | yes |
| 1 | 4 | 4 | 0.003647527862 | 4.541341133 | 1.135335283 | no |
| 2 | 1 | 1 | 0.030197383422 | 1.367879441 | 1.367879441 | no |
| 2 | 2 | 2 | 0.060394766845 | 2.735758882 | 1.367879441 | no |
| 2 | 4 | 4 | 0.120789533689 | 5.471517765 | 1.367879441 | no |

The artifact preserves full-precision model summaries for all 108 trajectories,
including final repeated-event deviations, token IDs/counts, peak boundary/time
and applicable retention/second-peak diagnostics. Inactive diagnostics remain
null where their denominator/event conditions do not apply; no fictitious
spontaneous response is introduced.

Zero input and inactive sides remain exactly zero deviation and reference
voltage in every cell. Bilateral states remain independent and match the
corresponding single-side responses. Right/left responses under shared config
do not establish measured bilateral physiological equality. Timing remains
`ZERO_ADDED_MODEL_DELAY_ASSUMPTION`, not zero biological NMJ delay.

## Structural separability versus reduced-summary degeneracy

Under the fixed model form, known input boundaries, positive scale and a
noiseless model trajectory, isolated-event immediate response reveals scale.
The subsequent normalized temporal ratio reveals tau independently of scale.
For retention `r` at known positive interval `delta`, the analytical relation
is `tau=-delta/log(r)`. This is a structural argument, not a parameter-fitting
implementation or inference from experimental data. The canonical grid stays
within numerically resolved positive decay; pathological floating-point regimes
outside the experiment are not claimed identifiable.

Full trajectories can therefore distinguish scale from decay under this model.
A single isolated-event peak alone cannot identify tau. A normalized retention
or second-peak ratio alone cannot identify scale. A single later-time sample
`y=scale*exp(-delta/tau)` confounds both: any admissible tau can be paired with
`scale=y*exp(delta/tau)` to reproduce that scalar. Similarly, repeated peak
alone combines scale and retention. The finite nine-cell sweep is not claimed
to contain exact duplicate scalar values; the degeneracy concerns reducing the
continuous two-parameter model to one scalar constraint. No similarity threshold
or best-cell ranking is introduced.

## Empirical identifiability and reference status

Both parameters remain `NOT_BIOLOGICALLY_IDENTIFIABLE_CURRENTLY`. Phase 8U
replays with zero formal-ready mappings. There is no executable observation
operator or established protocol matching, no pinned response-decay constraint,
and no valid numerical mapping from a Phase 8S amplitude to this effective
input transformation. No Phase 8S numerical value is used in the sweep.

Model-internal separability does not prove biological model correctness,
identifiable physiological efficacy/tau, calibration readiness or experimental
agreement. The reference cell is marked solely by historical config/identity:
tau 1 ms, scale 2, factors 1/1. Its reconstructed response artifact ID is
exactly the canonical Phase 9B ID. It is not best, fitted or biologically preferred.
The reference assumptions remain unchanged; no cell is selected as a replacement.

## Compact artifact and offline replay

Artifact schema: `g1_proxy_passive_electrical_sensitivity_artifact_v1`.

- Artifact ID: `dfe98ec90078124f4a66df825b552d05ed317fcb89d33e0f374b99c6bfd4bfa4`
- Config hash: `58ec7a9fa8125b48ed62a4ca66f794e4a47c83a0d789e6fbd078a05555b80073`
- Result hash: `bd24acf765556e8f0e2b2189ba5d6a0cf14824253c44ba951c07bd0d24d804f3`
- Reference cell ID: `f3c01a2ae572f10800e24f3daf586d870fd886e1f430314e7de734f80fac1467`
- Total size including manifest: 62,626 bytes.

Cell identity hashes source model artifact, explicit fixed/model config and
factor pair. Ordering is deterministic. Exactly one reference marker exists.
Each cell pins its reconstructed Phase 9B config/result/response identity and
compact per-instance diagnostics. Full trajectories are regenerated using the
unchanged source model and schedules rather than stored nine times. The
artifact is ignored by Git under the existing `data/derived/...` conventions.

Replay validates canonical Phase 9B, its required Phase 8 authorities and
Phase 8U readiness; rebuilds all nine cells through `build_response()`; checks
computed behavior; then reproduces canonical bytes, IDs, summaries and hashes.
No network, stochastic process, new physiological parameter or timestamp exists.
Tamper checks cover factors/values, source identity, reference marker, fixture,
token linkage, summaries, classifications, manifest and hashes, including
rehashed tampering. Source schedule mutation must fail Phase 9B replay first.

```sh
python -m neurofly.g1_proxy_electrical_sensitivity_cli generate
python -m neurofly.g1_proxy_electrical_sensitivity_cli inspect ARTIFACT_DIRECTORY
python -m neurofly.g1_proxy_electrical_sensitivity_cli replay ARTIFACT_DIRECTORY
```

Inspect shows the grid, reference cell, compact cell summaries, checked model
properties and separate biological-identifiability status. There are no fitting,
ranking, best-cell, empirical scoring or observation-comparison commands.

## Decisions and next phase

- `G1_ELECTRICAL_SENSITIVITY_VALIDATED`
- `EVENT_SCALE_AND_TAU_STRUCTURALLY_SEPARABLE_IN_FULL_TRAJECTORY`
- `BIOLOGICAL_PARAMETER_IDENTIFICATION_NOT_READY`
- `KEEP_REFERENCE_CONFIG_AS_EXPLORATORY_BASELINE`
- `PROCEED_TO_OBSERVATION_COMPATIBILITY_ASSESSMENT`

Exactly one Phase 9D: a read-only observation-compatibility assessment of the
existing model outputs against the pinned Phase 8S/8U measurement semantics.
Determine candidate baseline/evoked-response mappings, model-space versus
recorded-voltage assumptions, required observation operators and protocol
matching; keep miniature/release/history and composite-latency limitations
explicit. Do not implement operators, compare numbers, fit parameters or make
historical Phase 8U records ready in that assessment. Phase 9D is not implemented
here.

## Verification

Phase 9C: **PASS**, meaning deterministic model-behavior validation, not
biological parameter identification.

- Focused sensitivity tests: 21 passed in 87.40 seconds.
- Full `python -m pytest`: 747 passed, 1 deselected, 2 existing deprecation
  warnings in 465.54 seconds.
- `python -m ruff check .`, `python -m ruff format --check .` and
  `git diff --check`: passed.
- Frontend regression: 38 tests passed; lint, typecheck and build passed.
  The build's generated type-import rewrite was restored; frontend is unchanged.
- Canonical sensitivity offline generation/replay and historical Phase 9B,
  8W/Y/U replays passed, including unchanged source hashes and zero-ready status.
- Generated sensitivity data is Git-ignored. Only Phase 9C experiment,
  artifact/CLI/tests, this document and the minimal Project Context update are
  changed. No model equation/reference change, comparison, fit or new dynamics.

No commit or push was performed.
