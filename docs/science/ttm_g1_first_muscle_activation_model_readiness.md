# Phase 10A — first exploratory electrical-to-activation model

## Decision and executable boundary

Select `STATIC_NORMALIZED_ACTIVATION_PROXY`, driven by the full persisted
Phase 9B `voltage_deviation_mV_eq` trajectory. Phase 10B should implement exactly
one deterministic pointwise transformation:

```text
u[n] = source.voltage_deviation_mV_eq[n]
positive_u[n] = max(0, u[n])
activation_proxy[n] = min(1, positive_u[n] / activation_scale_mV_eq)
```

`activation_scale_mV_eq` must be explicit, finite and strictly positive. The
output is dimensionless and bounded in [0,1]. Zero means no model activation;
one means `MODEL_NORMALIZATION_CEILING`, not full physiological activation,
fiber recruitment, tetanus or maximal force. This is an exploratory proxy,
not a measured electrical-to-muscle transfer function. The first slice has
one free numeric parameter, no activation threshold and no additional time
constant. No implementation or new metadata contract is created in Phase 10A.

## Repository gate and Phase 9 completion

Started clean on `main` at `26d1f459095954ddaca9c1fbc2864c7e478cdd73`,
equal to `origin/main`. The 20-entry log confirms committed Phases 9G, 9E, 9C
and 9B; initial diff check passed. Required offline replays passed unchanged:

| Source | Artifact identity |
| --- | --- |
| Phase 9B electrical response | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` |
| Phase 9C sensitivity | `dfe98ec90078124f4a66df825b552d05ed317fcb89d33e0f374b99c6bfd4bfa4` |
| Phase 9E peak extractor | `2c775d6e00d74b3b3a3ca5a36bb84fd4032959d29f3c7d4c8b0bca934e2942b8` |
| Phase 8Y proxy mapping | `030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8` |
| Phase 8W abstract input | `1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa` |

Phase 9 is complete as an exploratory software/model milestone. The original
Koenig & Ikeda 2005 full protocol remains externally unavailable, as recorded
in [Phase 9G](g1_2005_evoked_protocol_recovery.md). This blocks source-matched
amplitude validation, biological mV conversion and parameter calibration; it
does not block explicitly assumed model-space propagation, sensitivity or
later mechanics prototyping. No source hunting is reopened here.

## Actual implementation audit

Inspected the Phase 9B numerical implementation, artifact replay and columnar
trajectory structure; Phase 9C experiment and findings; Phase 9E extraction
semantics; Phase 8Y domain/instance references; Phase 6C dimensionless motor-state
conventions; existing target contracts; frontend playback/scene interfaces;
pinned electrophysiology/readiness documentation; and Project Context.

Searches of backend, tests and frontend found no executable muscle activation,
calcium, contraction, muscle-force or rigid-body mechanics model and no existing
muscle-to-physics interface. The muscle-target contract resolves identity only.
The Phase 6C dimensionless state is neural, not muscle activation; its decay,
gain and threshold cannot be reused as activation parameters. Frontend bounded
intensity and scene transforms are explicitly presentation-only, not muscle
state or physical coordinates. Rapier/physics mentions in Project Context are
plans, not an implemented force interface. No conflicting activation model was
found, and no frontend/API integration is required for Phase 10B.

Existing canonical JSON/hash and staged immutable artifact helpers provide
reproducibility precedent, not a reason to create a generic activation framework.
Use their narrow conventions in Phase 10B; do not repurpose neural or rendering
normalization utilities merely because they have similar arithmetic.

## Electrical source and driver selection

Source model schema: `passive_g1_proxy_electrical_model_v1`; result schema:
`g1_proxy_passive_electrical_response_v1`; artifact schema:
`g1_proxy_passive_electrical_response_artifact_v1`. Its provenance is
`EXPLORATORY_G1_PROXY_ELECTRICAL_MODEL`. The result stores shared
`boundary_indices` and `time_ms`, with per-fixture/per-body columnar arrays
`voltage_deviation_mV_eq`, `proxy_voltage_mV_eq`, `token_count`, and instance,
config, token and proxy-source references.

The canonical grid is 0.1 ms, 80 intervals, 81 stored post-input boundaries,
0–8 ms. Reference coordinate 0, effective electrical tau 1 ms and event scale
2 mV_eq/token remain uncalibrated model assumptions. Both causal bodies are
stored for every fixture, including inactive controls: 12 trajectories and
972 boundary samples. The shared domain TYPE is
`ttm-g1-proxy-domain-057e09a9a9c5b054f7ce`, not a physical fiber instance.

| Driver candidate | Assessment |
| --- | --- |
| Full `voltage_deviation_mV_eq` | Selected: preserves electrical timing, decay and accumulated state without reference-offset dependence |
| Absolute `proxy_voltage_mV_eq` | Rejected: arbitrary coordinate offset would contaminate activation unless separately subtracted |
| Phase 9E peak scalar | Rejected: observation summary discards decay and duration, and excludes repeated fixtures |
| Phase 8W tokens or event counts | Rejected: bypasses electrical response and risks reapplying multiplicity |
| Empirical amplitude or structural weights | Rejected: no calibrated transformation; would violate source/model separation |

Activation samples are evaluated after the electrical boundary update at the
same stored step/time. No interpolation, resampling, render-FPS coupling,
additional lag or token reapplication occurs. Replay may reconstruct dynamics
to validate the source, but activation calculation reads the validated arrays;
it does not implement another electrical simulator. Boundary zero maps the
stored source value directly; zero source deviation gives zero activation.

## Candidate model families and assumption budget

| Family | Free quantities and conventions | Information added | Interpretation/readiness |
| --- | --- | --- | --- |
| Static rectified linear normalization | One scale; positive rectification; ceiling 1 | Bounded mechanics-facing trajectory, no new memory | Selected: honest minimal proxy; mostly rescaling below clipping |
| Static sigmoid/Hill-style transfer | Midpoint, slope/exponent; ceiling; zero-at-zero rule/rectification | Additional nonlinear shape | Defer: unmeasured shape parameters; ordinary logistic has nonzero output at zero unless modified |
| First-order normalized state | Scale plus activation tau; rectification/ceiling; initial state and update order | Independent temporal memory | Defer: unconstrained extra low-pass filter on an already decaying electrical signal |
| Calcium-mediated proxy | Electrical-to-calcium drive scale/form, release/influx kinetics, removal/buffering, initial state, activation sensitivity/slope | Intermediate state and transfer mechanism | Not ready mechanistically; arbitrary calcium-like numbers would not be measured calcium |
| Mechanistic activation | Cross-bridge/troponin state definitions, binding/transition rates, concentrations/sensitivity and initialization | Mechanistic interpretation only with matching evidence | Not supported by pinned evidence; Hill force-length/velocity laws are a separate force model, not an activation transfer |

Pinned project evidence concerns neural identity, target/domain associations and
electrical/release observations. It pins no quantitative TTM electrical-to-
activation transfer or calibration-ready activation trace. This is a statement
about project evidence, not a claim that such data do not exist in the literature.
No new biological law is needed to select the mathematical proxy; no new primary
source research was undertaken. Every quantitative activation choice is a
`MODEL_ASSUMPTION`, with no claim to physiological parameter identification.

## Parameter-assumption and identifiability table

Units refer to a proposed model, not measured physiology. `NOT_IDENTIFIABLE`
describes the current biological evidence status separately from assumption
classification. These are the complete parameter categories of the candidate
families at this assessment's level; a mechanistic family cannot honestly be
made implementation-ready without first choosing a concrete mechanism.

| Candidate(s) / quantity | Role | Units/model units | Evidence classification | Biological identifiability | Required for 10B? |
| --- | --- | --- | --- | --- | --- |
| Static/first-order: rectification | Negative deviations map to zero | Convention | `MODEL_ASSUMPTION` | Not an identified transfer law | Yes, fixed rule |
| Static/first-order: activation scale | Deviation at normalization ceiling | mV_eq | `MODEL_ASSUMPTION` | `NOT_IDENTIFIABLE` | Yes, only free number |
| All bounded candidates: ceiling 1 | Output normalization | Dimensionless | `MODEL_ASSUMPTION` | Not physiological maximum | Yes, fixed convention |
| Selected: independent activation threshold | Would introduce a dead zone | mV_eq | `NOT_REQUIRED` | `NOT_IDENTIFIABLE` if added | No |
| Sigmoid: midpoint/half-scale | Nonlinear transfer location | mV_eq | `MODEL_ASSUMPTION` | `NOT_IDENTIFIABLE` | No |
| Sigmoid: slope or Hill exponent | Transfer shape | 1/mV_eq or dimensionless, form-dependent | `MODEL_ASSUMPTION` | `NOT_IDENTIFIABLE` | No |
| Sigmoid: zero-output correction/rectification | Enforce zero-input control | Convention | `MODEL_ASSUMPTION` | Not established | No |
| First-order: activation tau | Additional temporal relaxation | Model ms | `MODEL_ASSUMPTION` | `NOT_IDENTIFIABLE` | No |
| First-order: initial activation/update order | State initialization/discretization | Dimensionless/convention | `MODEL_ASSUMPTION` | Not physiological initialization | No |
| Calcium: drive coupling/form | Electrical-to-intermediate input | Chosen model units per mV_eq | `MODEL_ASSUMPTION` | `NOT_IDENTIFIABLE` | No |
| Calcium: influx/release/removal/buffering rates and capacity | Intermediate dynamics | Model ms, rates and calcium-proxy units | `MODEL_ASSUMPTION` | `NOT_IDENTIFIABLE` | No |
| Calcium: sensitivity/midpoint/slope and initial intermediate state | Intermediate-to-activation mapping | Model-proxy units/conventions | `MODEL_ASSUMPTION` | `NOT_IDENTIFIABLE` | No |
| Mechanistic: binding/transition rates | Troponin/cross-bridge kinetics | Mechanism-dependent time/rate units | `MODEL_ASSUMPTION` if introduced | `NOT_IDENTIFIABLE` | No |
| Mechanistic: concentrations, occupancy normalization/sensitivity, initial states | Mechanistic state definition | Mechanism-dependent units | `MODEL_ASSUMPTION` if introduced | `NOT_IDENTIFIABLE` | No |
| Selected: added lag, stochastic parameters, fatigue/recruitment parameters | Extra causal/history mechanisms | Various | `NOT_REQUIRED` | No evidence basis here | No |
| Selected: activation dt/duration | Source grid identity | Model ms/count | `NOT_REQUIRED` as free parameters | Source grid verified, not physiology | Preserve source, do not duplicate as independent choices |

No candidate quantitative activation parameter is `EVIDENCE_SUPPORTED` or
`PARTIALLY_CONSTRAINED` by the current pinned data. Reference electrical offset
does not enter the selected mapping. Mechanical lengths, Fmax, force-velocity
coefficients and cross-bridge force are deliberately not activation parameters.

## Rectification, threshold, ceiling and temporal interpretation

Positive rectification is an explicit modelling convention that guarantees
nonnegative output for future finite negative deviation inputs. Current
canonical Phase 9B arrays are nonnegative; negative-input unit tests belong to
the transformation primitive, not fabricated canonical electrical artifacts.
No independent threshold is added: the zero boundary of rectification is not
a measured excitation threshold. Below the ceiling the transfer is continuous
linear normalization; at the ceiling further model drive is clipped.

Clipping is a lossy coordinate convention, not physiological saturation. It
can flatten responses and conceal upstream magnitude/retention differences;
save source deviation and report clipped samples so downstream consumers know
when information has been lost. Static activation adds no temporal state: it
returns toward zero only because the source does. The finite canonical run
does not require active trajectories to reach exactly zero by its last sample.

A new activation tau is not necessary for the first mechanics-facing signal.
The first-order alternative could later be useful if independent activation
memory is explicitly needed, but presently it adds unidentified kinetics and
double temporal filtering. Selecting a static proxy does not assert that
biological activation is instantaneous; it selects no added model lag/memory.

## Sensitivity propagation and separability

With electrical event scale q and fixed schedule/tau, pre-clipping activation
depends on q/activation_scale. Larger q increases activation and larger scale
reduces it; below clipping they are multiplicatively confounded from activation
alone. Larger electrical tau preserves electrical drive longer and therefore
increases retained static activation after input, without new activation memory.
Repeated accumulation belongs wholly to the electrical layer, not facilitation
or fatigue introduced by this mapping.

Clipping may break apparent proportionality and create indistinguishable
ceiling samples across parameter choices. Retaining source arrays makes the
mechanism auditable but does not biologically identify either layer's parameters.
Phase 9C established structural electrical separability, not activation
calibration. No empirical TTM activation trace suitable for calibration is
established in the project. No sensitivity cell or empirically preferred scale
is selected in Phase 10A.

## Instance, contraction and force boundaries

Preserve independent fixture/body instances `800146/R` and `804642/L`, including
inactive counterparts. Both reference one virtual G1 proxy DOMAIN TYPE with
unresolved empirical laterality. Use `SHARED_EXPLORATORY_MODEL_CONFIG` explicitly;
equal mathematical outputs under identical input/config are not bilateral
physiological equivalence, exact peripheral targeting or whole-TTM homogeneity.

Activation is neither shortening/strain nor contraction/work. It is not force,
torque, calcium concentration, cross-bridge occupancy or a measured activated
fiber fraction. No `force = activation * Fmax` relation is assumed. A later
force model may consume the dimensionless time series only after separately
defining its muscle/domain and force semantics. No body motion, joint, contact,
wing aerodynamics or neural production retuning is included.

## Exact executable Phase 10B scope

Implement one narrow backend model/transformation and canonical fixture runner:
validated persisted Phase 9B arrays → independent dimensionless activation
trajectories, plus deterministic content-addressed result/artifact/replay,
focused tests, repository-consistent generate/inspect/replay CLI if appropriate,
science document and minimal Project Context update. No intermediate metadata
phase, generic registry, physical calibration, new dynamics or frontend/API work.

### State and config

`activation_proxy[n]` is a derived sample, not an integrated hidden state. Config
must explicitly include a versioned model identity, positive finite
`activation_scale_mV_eq`, rectification rule, normalized ceiling, same-boundary
sample semantics, model-space input units, dimensionless output units, assumption
classification, shared-config convention and source/proxy identity requirements.
No seed, activation tau, threshold, delay or physical-voltage conversion field.

No reference scale number is selected in this read-only phase: it is unnecessary
to specify the equation/API and has no empirical constraint. Phase 10B must
choose and document an explicit reference model-space normalization coordinate
before generation, independently of Phase 9E peak output, source trajectory
maxima and all Phase 8S values. It must not auto-normalize per run or set its
ceiling from an observed/model peak. That choice becomes visible reference
config and remains arbitrary, uncalibrated and fixed across all fixtures.

### Source/output interface

Replay the exact canonical Phase 9B artifact for the reference run, validating
its Phase 8W/8Y ancestry using existing tools. Then consume the persisted arrays,
not tokens or Phase 9E outputs. Preserve source artifact/config/result identity,
fixture/instance ID, body/side, proxy mapping/domain and the unchanged shared
grid. Per-instance output arrays minimally carry `activation_proxy` and source
deviation reference (or copied `input_voltage_deviation_mV_eq` where useful).
Shared boundary/time arrays avoid redundant per-sample ancestry. Model/config
identity and provenance `EXPLORATORY_MUSCLE_ACTIVATION_MODEL` are explicit,
downstream of `EXPLORATORY_G1_PROXY_ELECTRICAL_MODEL`.

Validate finite inputs/outputs, array lengths, step/time consistency, exact source
and domain identities, positive scale and allowed semantic fields. Hash source,
config and result content; replay regenerates activation from validated source
samples and rejects changed units, scale, timing, body, proxy, ancestry, result
or hash. Keep generated artifacts ignored. No empirical targets/errors in output.

### Canonical fixtures and executable gates

All six Phase 9B fixtures are supported without retiming or dropping inactive
instances: zero, right single, left single, bilateral simultaneous, right repeated
and left repeated. This yields exactly 12 activation trajectories × 81 samples.
The eight historical tokens are source accounting only, not activation inputs.

Required tests/gates:

- Zero and inactive trajectories stay exactly zero activation.
- Finite outputs remain in [0,1]; negative primitive input maps to zero.
- Positive single response is deterministic, occurs at the same stored boundary
  and decays toward zero with its source; clipping may create a temporary plateau.
- Unsaturated input obeys linear normalization; threshold-free behavior is tested.
- Above-scale primitive input clips at 1 and is explicitly model-normalized.
- Repeated activation is exactly the pointwise transform of residual-plus-event
  electrical samples; no independent token increment/history rule.
- Bilateral trajectories remain independent; identity/ordering propagates exactly.
- Changing electrical reference coordinate alone cannot alter activation.
- Invalid scales/nonfinite or malformed sources fail closed; source/config/result
  tampering is rejected; deterministic replay reproduces bytes/hashes.
- Phase 9B/9C/9E and Phase 8W/8Y replays remain unchanged; Phase 8U stays zero-ready.
- Full Python/frontend regression and lint/format/diff gates pass; no empirical
  scoring, fitting, physiology, force or mechanics is introduced.

These gates validate the model form and software, not biological TTM activation.

## Bounded Phase 10C plan, not implementation

After Phase 10B, test activation_scale at 0.5×, 1× and 2× its declared reference
value across the unchanged six electrical fixtures. Hold all Phase 9 parameters,
source identities/grid and mapping semantics fixed. Test inverse-scale behavior
where unsaturated, clipping/ceiling sample counts, peak and final activation and
duration of model ceiling occupancy. Preserve complete trajectories for the
mechanics-facing assessment: a force model should receive the time-dependent
signal, not a single peak summary. Assess boundedness, timing, identity and lost
information before selecting any force law. No additional activation tau sweep,
best-cell ranking, biological scoring or separate metadata-contract chain.

## Decisions and claim budget

| Decision | Selected value |
| --- | --- |
| Model family | `STATIC_NORMALIZED_ACTIVATION_PROXY` |
| Driver | `FULL_G1_PROXY_VOLTAGE_DEVIATION_TRAJECTORY` |
| Output | `DIMENSIONLESS_ACTIVATION_PROXY_0_TO_1` |
| Parameter readiness | `IMPLEMENT_WITH_EXPLICIT_UNCALIBRATED_MODEL_ASSUMPTIONS` |
| Temporal dynamics | `NO_ADDITIONAL_ACTIVATION_TIME_CONSTANT` |
| Phase 10B readiness | `READY_FOR_FIRST_EXECUTABLE_MUSCLE_ACTIVATION_MODEL` |

Permitted after successful Phase 10B: “NeuroFly computes a deterministic
exploratory dimensionless muscle-activation proxy from the G1-proxy electrical
trajectory using explicit uncalibrated model assumptions.” Not permitted:
biological TTM activation reproduction, a physiological contraction percentage,
exact G1 anatomy, whole-TTM response or TTM force prediction.

Exactly one next executable phase: **Phase 10B implements the static normalized
activation proxy and replayable six-fixture result defined above.** It is not
implemented here. Phase 9's external benchmark blocker remains recorded without
blocking this deliberately exploratory downstream computation.

## Quality gates and status

Phase 10A: **PASS**. Required five source replays passed unchanged. Full
`python -m pytest`: 789 passed, 1 deselected, two dependency deprecation warnings.
`python -m ruff check .`, `python -m ruff format --check .` (255 files) and
`git diff --check` pass. Frontend regression: `npm test` (38 passed), lint,
typecheck and build pass. The build-generated `next-env.d.ts` modification was
restored to its original content. Only this document and the minimal Project
Context update remain changed; no Python, frontend/API source or scientific
artifact was added. No commit or push.
