# Phase 9A — first exploratory G1-proxy electrical model selection

Decision: select a **passive G1-proxy electrical response** driven by abstract
events transformed into **effective voltage-equivalent model drive**. Phase
9B can implement this deterministic exploratory slice with explicit,
uncalibrated assumptions. This is readiness for an executable model, **not**
readiness for physiological validation. Phase 9A changes documentation only.

## Repository gate and Phase 8 completion boundary

Work began on clean `main` at
`23cbd96c908894e8efc983fd3f22903070f3a7fd`, equal to `origin/main`.
Phase 8Y was committed; `git diff --check` passed. Required offline replays
passed without migration:

| Contract/artifact | Identity | Verified boundary |
| --- | --- | --- |
| Phase 8W | `1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa` | Eight abstract tokens; no physical magnitude or transmission claim. |
| Phase 8Y | `030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8` | One virtual G1 domain type; two distinct causal association links. |
| Phase 8U | `f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f` | Nine metadata mappings; formal-ready count remains **zero**. |
| Phase 8S | `5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f` | Nine published, protocol-specific observations, not model parameters. |

Phase 8Y replay also validates Phase 8K, and Phase 8W replay validates its
Phase 8Q/8O/8N ancestry. Phase 8 completed identity, admission, empirical and
domain boundaries, not electrical physiology. The previous Phase 8Z suggestion
is superseded by the user's Phase 9A decision task; no intervening contract is
needed. Historical Phase 8U/8Y readiness snapshots remain unchanged: they
describe those contracts' boundaries, not a prohibition on a separately
identified future exploratory model.

The audit inspected the actual Phase 8W/8Y implementations, Phase 8S records,
Phase 8U mappings, [Phase 8T feasibility](ttm_g1_observation_model_feasibility.md),
Phase 6C numerical implementation in `motor_pathway.py`, LIF numerical
conventions in `simulation.py`, synthetic fixture grid in
`synthetic_motor_interface.py`, canonical serialization/hash helpers, and
Project Context. No new biological measurements, figure extraction or source
reinterpretation is needed to make the bounded modelling decision below.

## Four candidate model families and input transformations

| Family | Minimal input transformation | Important free quantities | Capability and interpretation | Selection |
| --- | --- | --- | --- | --- |
| A. Phenomenological voltage kernel | Token count selects an explicitly assumed voltage-equivalent kernel. | Baseline, amplitude, waveform width/shape; lag if allowed. A fixed exponential reduces to baseline, scale, decay. | Outputs a voltage-shaped response proxy; no NMJ mechanism. Flexible rise/shape terms would add unsupported freedoms. | Honest alternative, but use the equivalent minimal state formulation in B. |
| B. Passive relaxation + effective event drive | One token contributes one fixed effective voltage-equivalent jump, without current or release units. | Baseline/reference level, effective relaxation time, event jump scale. Impulsive temporal form, zero added lag and zero initial deviation are explicit fixed assumptions. | Deterministic voltage-valued state, relaxation and linear repeated-input composition. Biologically inspired **form**, not measured membrane or NMJ parameters. | **Selected** for the first executable slice. |
| C. Conductance response | Token must be transformed into assumed synaptic conductance kinetics. | Capacitance, leak conductance/rest level, synaptic reversal, peak conductance, kinetics and timing. | Adds driving-force/nonlinear interpretation but no independent identification of these quantities. | Reject for this slice; do not dress arbitrary input in nS or reuse the prior −10 mV analysis input. |
| D. Release/quantal response | Token must be interpreted through release/sites/pools before postsynaptic response. | Release probability/count/sites, vesicle availability, quantal response, spontaneous process, recycling/depression, plus electrical response quantities. | Could address more observation types only under matched mechanisms/protocols. Receipt or token count is not release/quantal count. | Premature and outside the first slice. |

An exponential voltage kernel and B's linear state are mathematically
equivalent for matched baseline, scale, time constant and event timing. B is
selected for explicit state initialization, recurrence and causal accounting,
**not because it has stronger physiological evidence**. No membrane spike,
threshold, reset, refractory period or activation state is introduced.

| Transformation candidate | Quantity/units | Scientific requirement / outcome |
| --- | --- | --- |
| Dimensionless event impulse | Discrete token count, no physical magnitude. | Useful source representation, but requires an explicit state-response scale. |
| Effective voltage-equivalent drive | Assumed model voltage increment in mV per token. | **Selected**; downstream model config owns the scale, not the token. No claim of measured electrical efficacy. |
| Current pulse/kernel | Physical current plus duration/waveform. | No pinned current evidence; arbitrary pA/nA is not acceptable here. Not selected. |
| Conductance transient | Physical conductance, reversal and kinetics. | No jointly identified conductance/membrane parameter set; arbitrary nS/µS is not acceptable here. Not selected. |
| Release event | Biological/quantal output and transmission success semantics. | Requires additional physiology rather than a token rename. Not selected. |

One token is one discrete **model drive event**, not one successful biological
transmission, vesicle, quantum or junction potential. Every valid token affects
the selected model deterministically **as a model rule only**. Structural
connectivity and mapping confidence never scale the input.

## Parameter evidence/readiness and assumption budget

The following classifications concern the proposed model, not a claim that
all quantities are interchangeable physiological parameters. Units of the
selected voltage state are hypothesized model mV, not a measured potential;
its input is a voltage-equivalent jump, not current inferred from mV.

| Important quantity | A: voltage kernel | B: selected passive state | C: conductance | D: release/quantal | Evidence and permitted use |
| --- | --- | --- | --- | --- | --- |
| Baseline/rest level | `MODEL_ASSUMPTION` | `MODEL_ASSUMPTION` | `MODEL_ASSUMPTION` | `MODEL_ASSUMPTION` | Approximate −95 mV is `EVIDENCE_SUPPORTED_CONTEXT`, not an identified baseline for this model/protocol. |
| Electrical decay/time constant | `MODEL_ASSUMPTION` | `MODEL_ASSUMPTION` | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` | Phase 8S pins no quantitative voltage-decay waveform. No repository tau is evidence. |
| Event scale | `MODEL_ASSUMPTION` | `MODEL_ASSUMPTION` | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` | Reused 45 mV response does not identify drive, conductance or release scale. |
| Event waveform | `MODEL_ASSUMPTION` | `MODEL_ASSUMPTION`: boundary jump | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` | No measured response/input kernel pinned. Jump form is a declared reduced abstraction. |
| Added model delay | `NOT_REQUIRED` | `NOT_REQUIRED` | `NOT_IDENTIFIABLE` if introduced | `NOT_IDENTIFIABLE` if introduced | Preserve zero-added-model-delay scheduling; biological delay remains unknown. |
| Reversal potential | `NOT_REQUIRED` | `NOT_REQUIRED` | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` if conductance-based | −10 mV remains prior-source correction context, not automatically E_rev. |
| Capacitance/resistance or leak | `NOT_REQUIRED` | `NOT_REQUIRED` separately | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` if membrane-based | An effective tau avoids claiming independent R/C or membrane measurements. |
| Release probability/sites/pools | `NOT_REQUIRED` | `NOT_REQUIRED` | `NOT_IDENTIFIABLE` if claimed | `NOT_IDENTIFIABLE` | Pinned quantal/recycling observations do not identify a complete transferable release model. |
| Spontaneous/history/depression rules | `NOT_REQUIRED` | `NOT_REQUIRED` | `NOT_IDENTIFIABLE` if claimed | `NOT_IDENTIFIABLE` | Their omission limits the model; it does not establish absent biological history dependence. |
| Initial condition | `MODEL_ASSUMPTION` | `MODEL_ASSUMPTION`: zero deviation | `MODEL_ASSUMPTION` | `MODEL_ASSUMPTION` plus pool state | Deterministic start without claiming experimental equilibration. |

For B there are **three numerical model freedoms**: reference voltage,
effective relaxation time and effective event scale. Fixed modelling choices
are impulsive drive, linear summation/no saturation, zero initial deviation,
zero added model lag, no spontaneous process and no depression model. All are
explicit assumptions; omission of mechanisms is not evidence of their absence.
Sharing a parameter config across causal sides is another explicit assumption.

C adds at least membrane/drive/reversal/kinetic freedoms; D adds multiple
release and history processes. A flexible kernel adds rise/shape freedoms
without independent observations. There are **zero formal protocol-matched
numerical validation targets** currently ready, and no pinned waveform to
identify tau. Even treating baseline and response amplitude as provisional
descriptors cannot identify three numerical freedoms or the omitted mechanisms.
Implementation readiness comes from transparent assumptions and testable model
behavior, not parameter identifiability.

## Baseline, evoked potential and timing decisions

The ~−95 mV record remains descriptive G1 context. It may eventually inform a
declared exploratory initialization scenario, but this phase does not select
it as `V_rest`, fit it or claim calibration. Likewise the 45 mV prior-result
record is conditional **future validation evidence**, not an active fitting
target. Source protocol and amplitude/window semantics remain unresolved.
The first event scale must not be chosen to make the model yield 45 mV.

Phase 9A selects no numerical reference voltage, event scale or tau. Phase 9B
must require all three explicitly, classify them `MODEL_ASSUMPTION`, and pin
one reference/test configuration before running trajectories, independently of
Phase 8S values. No hidden defaults or observation-to-config export are allowed.
This is a bounded implementation choice, not a missing biological calibration
to be improvised. Tau must not be copied from Phase 6C or the LIF model.

Keep `ZERO_ADDED_MODEL_DELAY_ASSUMPTION` unchanged: drive at the token's exact
stored boundary, with no numeric NMJ-delay parameter, interpolation or inferred
lag. A boundary jump is a discrete model abstraction, not instantaneous
biological depolarization. Kadas' 0.84 ms composite interval starts at a wider
experimental boundary and is not a delay for this model.

## Concrete Phase 9B state and numerical design

For each independent fixture and each causal body `b`, use one deviation
state `u_b` and report the hypothetical voltage `V_proxy,b = V_ref + u_b`.
The same explicit reference config may be shared, but instances are keyed by
fixture/run and causal body; sharing config is not measured bilateral equality.
Both instances use the pinned G1 proxy **type**, never a shared physical fiber.
Source body/side, association, token and parent identities must remain intact.

Between events, define passive relaxation conceptually as
`du_b/dt = -u_b / tau_effective_ms`. At integer boundary `n`, let `k_b[n]`
count only the validated tokens for that body/fixture. Recommend:

`u_b[n] = exp(-dt_ms / tau_effective_ms) * u_b[n-1] + k_b[n] * q_effective_mV`

for `n >= 1`, with zero deviation before boundary zero and
`u_b[0] = k_b[0] * q_effective_mV` if a validated input at zero is ever allowed.
Canonical sources contain no boundary-zero event. Samples are **post-input**
boundary values; decay precedes application at every later boundary. Positive
scale is a depolarizing **model** assumption. This is not a measured membrane
ODE parameterization or a model of transmitter release.

Use exact exponential relaxation, not forward Euler; do not infer a second
current state or resistance/capacitance. Preserve the canonical source grid:
`dt_ms = 0.1`, 80 intervals, boundaries 0–80, total 8 ms. Integer step identity
is primary; require token time to match the source grid exactly. Source token
identity and event multiplicity remain unchanged. Do not merge bilateral
states or collapse repeated tokens by body. Token validation/adaptation occurs
only downstream of replayed Phase 8W/8Y in the future model implementation.

The inspected Phase 6C code uses exact exponential decay followed by stored
boundary events, and the fixture battery supplies this grid. Reuse these
**numerical conventions**, canonical hashing and validated source loaders
where applicable. Do not call the TTMn integrator to produce electrical states,
reuse its dimensionless result type/parameters, or instantiate a LIF neuron.
The mathematical resemblance does not change state meaning or authorize a
neural threshold/reset/refractory mechanism in the G1 proxy.

### Minimum explicit config for 9B

- Model/version and transformation/version identities; assumption labels.
- `reference_voltage_mV` (finite), `tau_effective_ms` (finite, positive),
  `event_scale_effective_mV` (finite, positive); no silent physiology defaults.
- Initial deviation zero; boundary-jump waveform; linear summation;
  decay-then-input sample semantics; zero-added-model-delay marker.
- Grid/duration: source-compatible 0.1 ms, 80 intervals; no truncation of input.
- Phase 8W input artifact and Phase 8Y proxy-contract/domain references,
  exact causal association links and independent fixture/body instance policy.
- Shared-config semantics `MODEL_ASSUMPTION`, scientific exclusions and full
  upstream provenance. No physical current/conductance/release parameters.

Reject invalid/nonfinite values, incompatible input/grid/domain identities,
duplicates/conflicting token identities and nonfinite resulting trajectories.
Use deterministic float64 operations with canonical iteration/order. No
stochastic process or seed is needed in the first model. Pin config, input and
result identity and retain samples for offline replay in a bounded Phase 9B
experiment artifact, using existing repository conventions. This document
implements no schema, artifact, CLI or model.

## Canonical experiment and behavior gates

| Existing independent fixture | Preserved input | Expected model behavior, not physiology |
| --- | --- | --- |
| `ZERO_EVENT_CONTROL` | No tokens. | Both trajectories remain exactly at configured baseline. |
| `RIGHT_SINGLE_EVENT` | 800146/R, step 10 / 1.0 ms. | Right instance jumps once and relaxes; left remains baseline. |
| `LEFT_SINGLE_EVENT` | 804642/L, step 10 / 1.0 ms. | Left instance jumps once and relaxes; right remains baseline. |
| `BILATERAL_SIMULTANEOUS_EVENT` | Distinct tokens for both at step 10. | Two independent state updates; no coincident-state/event merge. |
| `RIGHT_REPEATED_EVENTS` | 800146/R, steps 10/30 / 1.0/3.0 ms. | Two increments plus intervening relaxation; left stays baseline. |
| `LEFT_REPEATED_EVENTS` | 804642/L, steps 10/30 / 1.0/3.0 ms. | Mirror fixture accounting through verified identities, not inferred anatomy. |

Required software/model gates: finite deterministic trajectories; exact initial
and zero-control state; positive jump equal to the configured effective scale
after passive decay; monotonic approach toward baseline between events;
linear superposition for repeated input; independent bilateral identities;
unchanged source token IDs/times; config-dependent output identity and exact
offline replay. Equal curves under shared config are **model behavior**, not
bilateral physiological proof. The finite 8-ms horizon need not reach baseline;
no forced reset or tail clamp is allowed. No saturation or all-input-range
biological validity is claimed by this linear model.

The repeated fixture spacing is model-test timing, not the published 1-Hz
protocol. Deterministic summation does not establish absence of depression or
successful repeated transmission. Production upstream parameters stay untouched.

## Phase 9C sensitivity plan and future observations

Plan one compact, non-fitting sensitivity study over **event scale and
effective tau**: for each use 0.5, 1 and 2 times the independently pinned 9B
reference, a nine-cell product with baseline/config/source identities fixed.
These are operator/model probes, not biological parameter candidates. Record
trajectories and deterministic software summaries, never residuals or scores
against Phase 8S. Baseline is an explicit offset freedom; its choice changes
absolute modeled voltage but not deviation dynamics. It need not become a
third large sweep. Longer observation duration, if needed, must be explicit;
do not retune scale/tau to force return within the original window.

A hypothetical voltage trace could eventually support baseline and evoked
deflection operators, but neither operator/protocol is ready now. Miniature,
quantal, spontaneous, depression and recycling observations require additional
mechanisms and matched observation semantics. The prior equilibrium input
remains context-only. Kadas latency remains a system-boundary mismatch.
No Phase 8U mapping changes or becomes formally ready in 9A; a future model
output alone would not settle its remaining operator/protocol blockers.

## Scientific claim budget and decisions

Permitted future claim: NeuroFly computes a deterministic, biologically
inspired G1-proxy electrical trajectory driven by abstract TTM input events
under explicit uncalibrated model assumptions. The result is not measured or
calibrated G1 physiology, a biological NMJ simulation, exact MaleCNS-to-G1
anatomy, whole-TTM voltage, activation, contraction, force or behavior.

- Model family: `PASSIVE_G1_ELECTRICAL_RESPONSE`.
- Input transformation: `ABSTRACT_EVENT_TO_EFFECTIVE_MODEL_DRIVE`.
- Parameter readiness: `IMPLEMENT_AS_EXPLICIT_UNCALIBRATED_MODEL_ASSUMPTIONS`.
- Phase 9B readiness: `READY_FOR_FIRST_EXPLORATORY_G1_ELECTRICAL_MODEL`.

Exactly one **Phase 9B**: implement and offline-replay the bounded deterministic
passive G1-proxy model and effective voltage-equivalent token transformation
defined above, on the six unchanged Phase 8W fixtures with independent causal
instances and one explicit assumption config. Test model behavior and source
immutability; do not fit observations, add release/dynamics complexity,
implement comparison operators or change Phase 8 contracts. No part of 9B is
implemented in 9A.

## Verification

Phase 9A: **PASS**. Required Phase 8W, 8Y, 8U and 8S offline replays passed
before edits; their contracts were not modified. Phase 8U retains zero formal
comparison-ready mappings.

- `python -m pytest`: 681 passed, 1 deselected, 2 warnings.
- `python -m ruff check .`: passed.
- `python -m ruff format --check .`: passed.
- `git diff --check`: passed.
- Frontend regression: 38 tests passed; lint, typecheck and build passed.

The frontend build's automatic generated-type import rewrite was restored;
frontend source remains unchanged. Only this assessment and the minimal Project
Context update are changed. No production code, artifact, fitting, comparison or
electrical dynamics were introduced. No commit or push was performed.
