# Phase 10B — static exploratory muscle-activation proxy

## Capability and scientific boundary

Persisted, replay-validated Phase 9B electrical deviation now drives one
deterministic, dimensionless activation trajectory per causal instance. This
implements the selected Phase 10A boundary and stops at activation. It is an
exploratory model-space transformation, not physiological excitation-contraction
validation, biological activation percentage, recruitment, calcium, shortening,
force fraction or a mechanics model. No biological source search or fitting was
performed. Phase 9's external primary-source benchmark blocker remains.

Work started clean on `main` at `7351954a8c617e5b64d74645be3b6109d0531519`,
equal to `origin/main`; Phase 10A and required historical phases were committed.
Initial diff check and required source replays passed before implementation.

## Direct source and historical authorities

| Source | Unchanged artifact identity |
| --- | --- |
| Phase 9B electrical response | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` |
| Phase 9C sensitivity | `dfe98ec90078124f4a66df825b552d05ed317fcb89d33e0f374b99c6bfd4bfa4` |
| Phase 9E extractor | `2c775d6e00d74b3b3a3ca5a36bb84fd4032959d29f3c7d4c8b0bca934e2942b8` |
| Phase 8Y proxy mapping | `030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8` |
| Phase 8W abstract input | `1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa` |

The direct runtime source is `g1_proxy_passive_electrical_response_v1`, through
its persisted `g1_proxy_passive_electrical_response_artifact_v1`. Only
`voltage_deviation_mV_eq` drives activation. No absolute proxy voltage,
Phase 9E result, token count/schedule or structural connectivity weight is read
to compute activation. Electrical source replay uses Phase 9B's authority to
reconstruct/validate its artifact; **the activation transform itself never
integrates electrical dynamics**. Source arrays are consumed after replay.

Phase 9C/9E are regression authorities, not runtime dependencies. Phase 8W/8Y
are validated recursively by source replay, not independently composed into
activation. Phase 8U remains unchanged and zero-ready.

## Model/config and equation

Model schema: `static_normalized_muscle_activation_model_v1`.
Result schema: `static_normalized_muscle_activation_result_v1`.
Provenance: `EXPLORATORY_MUSCLE_ACTIVATION_MODEL`, downstream of
`EXPLORATORY_G1_PROXY_ELECTRICAL_MODEL`, with source artifact, config/result and
trajectory identities/hashes retained.

```text
positive_driver[n] = max(0, voltage_deviation_mV_eq[n])
activation_unclipped[n] = positive_driver[n] / activation_scale_mV_eq
activation_proxy[n] = min(1, activation_unclipped[n])
```

The implementation compares against zero and scale before division, preventing
overflow for a very small finite positive scale. This is numerically equivalent
to the bounded equation; it adds no term or hidden state.

| Config quantity/convention | Reference | Classification |
| --- | --- | --- |
| `activation_scale_mV_eq` | 10.0 model-space mV_eq | `MODEL_ASSUMPTION`: simple finite positive normalization coordinate, prescribed independently of source peaks or empirical data |
| Rectification | `POSITIVE_PART_RECTIFICATION` | `MODEL_ASSUMPTION`: nonpositive driver gives zero |
| Ceiling | 1.0, `MODEL_NORMALIZATION_CEILING` | `MODEL_ASSUMPTION`, not physiological maximum |
| Config sharing | `SHARED_EXPLORATORY_MODEL_CONFIG` | `MODEL_ASSUMPTION`, not bilateral biological equivalence |
| Temporal semantics | Memoryless, same stored boundary | No activation tau, threshold, added delay, interpolation or resampling |

The scale is not derived from 45 biological mV, the 2 mV_eq electrical increment,
canonical peaks or sensitivity results. It was not revised after generation.
Ten mV_eq is not a biological threshold, EJP maximum or force calibration.
Config requires a finite positive scale and rejects changed/extra semantic
fields on replay. The ceiling is fixed in v1. Units remain dimensionless [0,1];
one means the model's normalization ceiling, not 100% contraction.

## Sample storage, causal independence and timing

Each result preserves fixture order, then source body order `800146/R`,
`804642/L`. Shared grid arrays store steps 0–80 and the exact source times
`n*0.1 ms` through 8 ms. Each instance contains the original deviation array,
activation array, source trajectory ID/hash, body/side, proxy domain/mapping,
activation config and content-addressed trajectory ID. No new event is emitted.
The source reference identifies exactly one electrical trajectory; token input
ancestry is reachable through that source, not reapplied as activation input.

The shared proxy DOMAIN TYPE is `ttm-g1-proxy-domain-057e09a9a9c5b054f7ce`.
It is not a physical G1 instance, a resolved MaleCNS-to-G1 endpoint or whole-TTM
state. Empirical laterality remains unresolved. Both bodies retain separate
activation trajectories, including inactive controls. No right/left summation
or averaging occurs. Equal outputs under identical schedules/config are a
mathematical symmetry, not bilateral physiological evidence.

At every source post-input electrical boundary, activation uses that same
sample and time. Boundary zero maps its stored electrical deviation directly.
There is no independent activation initialization or temporal memory. Equal
deviation samples produce equal activation regardless of prior history.

## Canonical fixture accounting and outcomes

Six fixtures × two causal trajectories × 81 boundaries = 12 trajectories and
972 activation samples. The following values are model regression results,
not biological measurements. Inactive counterparts remain exactly zero.

| Fixture | Active identity | Peak activation | Peak step/time | Final activation |
| --- | --- | ---: | --- | ---: |
| ZERO_EVENT_CONTROL | Neither; both controls retained | 0 | Earliest tied maximum: 0 / 0 ms | 0 |
| RIGHT_SINGLE_EVENT | 800146/R | 0.2 | 10 / 1 ms | 0.00018237639311090254 |
| LEFT_SINGLE_EVENT | 804642/L | 0.2 | 10 / 1 ms | 0.00018237639311090254 |
| BILATERAL_SIMULTANEOUS_EVENT | Both independently | 0.2 each | 10 / 1 ms each | 0.00018237639311090254 each |
| RIGHT_REPEATED_EVENTS | 800146/R | 0.22706705664732252 | 30 / 3 ms | 0.0015299657929279914 |
| LEFT_REPEATED_EVENTS | 804642/L | 0.22706705664732252 | 30 / 3 ms | 0.0015299657929279914 |

All canonical samples are finite and [0,1]; no canonical sample reaches the
ceiling. `ceiling_sample_count` counts driver values at or above scale, including
exact equality: it means model ceiling occupancy, not physiological saturation.
There is no redundant clipping state variable. Zero-input peak step zero is
only the earliest tied model-summary maximum, not an evoked response time.

Single activation follows passive electrical decay toward zero; it need not
reach exact zero by the final finite boundary. Repeated activation follows
residual-plus-event electrical deviation divided by ten. No independent
facilitation, depression, fatigue, recruitment or activation memory is added.

## Phase 9 sensitivity propagation

In the unclipped region, upstream electrical event-scale changes propagate
proportionally into activation through changed source samples. A larger
electrical tau preserves activation longer solely because the electrical
trajectory retains more deviation. No activation-specific tau exists. A change
to absolute reference coordinate with identical deviations cannot alter output.

Activation scale has inverse influence before clipping; event scale and
activation scale appear as a ratio and are confounded from activation alone.
Clipping loses magnitude information and may mask differences. These are
model-internal properties, not biologically identified transfer parameters.

## Artifact, generation and offline replay

Artifact schema: `static_normalized_muscle_activation_artifact_v1`.

- Artifact ID: `4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb`
- Config hash: `be33c72048caeae4227a504aa251d10acec454ef283a73adf77104d0a4c424c9`
- Result hash: `288b67f791f66765a17d6bdd6cadd30b9c98f4480dd23434bd4c6e9ae5667fce`
- Size including manifest: 35,407 bytes.

The two-file artifact (`activation.json`, `manifest.json`) lives in the existing
ignored `data/derived/malecns/looming_giant_fiber_v1/` schema directory. IDs hash
source/config/results including semantic labels. Generation uses exclusive
staged writes; existing artifacts are replayed rather than overwritten.

```sh
python -m neurofly.muscle_activation_cli generate
python -m neurofly.muscle_activation_cli inspect ARTIFACT_DIRECTORY
python -m neurofly.muscle_activation_cli replay ARTIFACT_DIRECTORY
```

The CLI generates the prescribed reference config, with no fit/calibrate/compare
or mechanics command. Inspect makes the uncalibrated status, assumption labels,
source, per-body peaks/final values and ceiling diagnostics visible.

Replay validates the exact canonical persisted Phase 9B artifact, loads its
arrays, validates activation config, reapplies the static transform in canonical
order and reproduces samples/summaries, IDs, hashes, canonical bytes, manifest
and directory identity. It uses no network, randomness or timestamps. Rehashed
semantic tampering fails comparison with freshly derived output. Noncanonical
source artifacts fail the published generation gate.

The pure transformation API checks source integrity, grid, fixture/body ordering,
instance/config identity, proxy and finite deviation arrays without simulation.
It accepts test-local integrity-valid Phase 9B-style inputs for regression
properties; this is not a substitute for provenance replay or publication of
those inputs as canonical evidence. Negative drivers and ceiling cases are
test-local only; historical source artifacts remain untouched.

## Verification and exclusions

Focused tests cover exact zeros, unilateral and bilateral independence, all
repeated samples, same-grid ancestry, negative rectification, equality/above-
ceiling clipping, linear region, inverse scale, no memory, coordinate-offset
independence, upstream scale/tau propagation, invalid scales/nonfinite drivers,
malformed grid/schema/body/proxy/identity, deterministic identities and offline
byte-equivalent replay. Tamper tests cover source reference, driver, scale,
rectification/ceiling semantics, body/side, proxy, output samples, hashes and
artifact ID/manifest. Phase 8U remains zero-ready.

No force, torque, contraction, strain, calcium, percent-activation, physical
voltage conversion, empirical target/error, optimizer, activation tau or
threshold is introduced. No frontend/API or historical schema changes.

## Exactly one Phase 10C handoff

Run one bounded activation-scale experiment at 5, 10 and 20 mV_eq (0.5×, 1×,
2× reference) against all six fixed Phase 9B trajectories. Test inverse scaling
where unclipped, ceiling occupancy/information loss and causal independence;
assess whether the complete bounded time series is suitable for a future force
interface. Do not rank scales biologically, select a best cell, add force or
implement this experiment in Phase 10B.

## Final acceptance and quality gates

Decision: `FIRST_EXPLORATORY_MUSCLE_ACTIVATION_MODEL_VALIDATED`; Phase 10B:
**PASS** (model/software behavior only). Focused tests: 41 passed. Full
`python -m pytest`: 830 passed, 1 deselected, two dependency deprecation warnings.
Ruff check and format check (260 files), plus `git diff --check`, pass.
Frontend regression: 38 tests, lint, typecheck and build pass. The generated
frontend declaration change was restored; no frontend source change remains.
Canonical activation replay and historical source regressions pass unchanged;
Phase 8U remains zero-ready. Generated artifact is Git-ignored. No commit/push.
