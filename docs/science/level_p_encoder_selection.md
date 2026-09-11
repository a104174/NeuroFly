# Phase 2D — Level P sensory-encoder evidence audit and contract selection

**Status:** Phase 2D selection document; the E1 contract is implemented in
`neurofly.sensory_encoder` (Phase 2E). No gain calibration, neural-model
change, or visual-angle mapping is implemented.

**Decision:** select **E1 — direct bounded-normalized instantaneous feature
drive** for the first Level P encoder. The proposed identifier is
`level_p_instantaneous_bounded_v1`.

Level P remains a NeuroFly population approximation. It does not reconstruct
photoreceptor-to-LC4/LPLC2 processing, individual receptive fields, or a
MaleCNS visual-angle map.

## Evidence audit

### Ache et al. (2019)

[*Neural Basis for Looming Size and Velocity Encoding in the Drosophila Giant
Fiber Escape Pathway*](https://doi.org/10.1016/j.cub.2019.01.079) used in-vivo
whole-cell current-clamp recordings from the Giant Fiber (GF), pathway
silencing, behavior, and EM reconstruction. Silencing LPLC2 left a GF
depolarization whose time course tracked instantaneous looming angular
velocity; pooled GF membrane potential was approximately linear in angular
velocity. The complementary LC4-silenced response supported an LPLC2-related
angular-size component. The isolated and combined responses support treating
LC4 and LPLC2 as complementary feature channels into GF.

The paper's model does **not** directly specify an LC4/LPLC2-to-NeuroFly
encoder. Its LC4 term is a scaled, delayed angular-velocity approximation to
the **GF membrane response measured while LPLC2 was silenced**. Its LPLC2 term
is an empirical Gaussian in log angular size fitted to the **GF response while
LC4 was silenced**, with a peak near 42 degrees. The authors used a 19 ms shift
to align stimulus and GF response and combined those excitatory terms with
additional inhibitory GF-response components. These fitted amplitudes, the
Gaussian shape, and the 19 ms alignment are therefore output-level
phenomenology for that preparation—not measurements of presynaptic population
drive, encoder gain, or an LC4/LPLC2 sensory latency.

The paper also reports that LPLC2 neurons require looming motion to be active
despite contributing size-related information. Its combined-response analysis
is compatible with supralinearity either within GF or presynaptically; it does
not locate a unique mechanism and does not justify adding an encoder
nonlinearity or temporal filter.

### Klapoetke et al. (2017)

[*Ultra-selective looming detection from radial motion
opponency*](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457385/), DOI
[`10.1038/nature24626`](https://doi.org/10.1038/nature24626), used in-vivo
two-photon calcium imaging of LPLC2 populations and individual cells,
single-cell anatomy, circuit perturbations, and whole-cell GF recording during
optogenetic LPLC2 activation. LPLC2 responded strongly to dark focal looming,
with detectable population responses early in expansion, but not to dark
receding looming, luminance-matched motion-free darkening, contraction, or
wide-field motion. Individual cells preferred outward motion from their local
receptive-field centers; radial motion opponency and spatial tiling are central
to that selectivity.

This supports requiring positive expansion for the simplified LPLC2 size
channel. It also shows exactly what Level P discards: local direction, focality,
receptive-field center, tiling, overlap, and body-specific stimulus coverage.
Calcium fluorescence contains indicator and measurement dynamics, so its time
course does not by itself identify a voltage-equivalent encoder filter or
latency. The paper provides no `mV_eq` gain, feature normalization scale, or
body-independent temporal constant.

## Existing stimulus geometry

Phase 1C remains the sole definition of looming geometry. For object radius
`r`, signed approach velocity `v` (positive toward the observer), initial
distance `d0`, and pre-collision time `t`:

```text
d(t) = d0 - v t
theta(t) = 2 atan2(r, d(t))                         [rad, full diameter]
omega(t) = dtheta/dt
         = 2 r v / (d(t)^2 + r^2)                 [rad/s]
```

Positive `omega` is expansion, zero is no expansion, and negative `omega` is
recession/contraction in this scalar geometry. At collision the existing
`LoomingSample` is terminal, `theta = pi`, and `omega = None`. A Phase 2E
encoder must consume finite pre-collision samples only and must stop before the
terminal sample rather than invent a post-collision drive.

`center.azimuth_rad` and `center.elevation_rad` remain environment fields.
Level P cannot map them to bodies, so E1 intentionally ignores them and states
that loss in provenance.

## Encoder candidates

| Candidate | Form | Strengths | Scientific cost / decision |
| --- | --- | --- | --- |
| **E1 — instantaneous normalized drive** | Current feature sample → deterministic normalization → population drive | Preserves stimulus time course; fewest dynamical assumptions; attributes filtering to already explicit neural dynamics; easiest to inspect and falsify | Selected, with bounded monotone normalization and an explicit positive-expansion gate. The normalization is a NeuroFly assumption. |
| **E2 — normalized drive plus causal filter** | E1 followed by one first-order filter per channel | Could represent additional sensory dynamics | Rejected initially. GF membrane traces and GCaMP traces confound upstream, indicator, synaptic, and membrane filtering. Added time constants would overlap Phase 2B filtering and are not presently identifiable. |
| **E3 — onset/event epochs** | Feature threshold triggers bounded drive epochs | Compact event vocabulary | Rejected. It introduces thresholds, epoch amplitudes, and durations while discarding continuous looming geometry and turning unsupported onset choices into dominant timing assumptions. |
| Ache GF phenomenology as an encoder | Delayed linear velocity plus Gaussian size terms | Closely reproduces the reported GF-level fit | Rejected as a category error. Those equations model pathway-isolated GF membrane components and include omitted/inhibitory circuit effects; they are not measured LC4/LPLC2 external drive. |

### Normalization alternatives

| Policy | Near zero | Extreme feature | Identifiability / transfer issue |
| --- | --- | --- | --- |
| `x / x_ref` | Linear | Unbounded | `x_ref` and gain are exactly confounded unless one is merely a fixed unit convention. Expansion velocity also grows sharply near collision. |
| **`x / (x + x_half)`** | Approximately linear | Bounded below 1 | Selected. `x_half` is an explicit free shape parameter that must be constrained across multiple feature ranges; it is not a biological constant. |
| Experimental min/max | Protocol-dependent | Clipped to audited range | Transfers poorly and silently makes the selected dataset an encoder constant. |
| No normalization | Unitful linear mapping | Unbounded | Leaves gain tied to the input unit convention and gives no explicit extreme-value behavior. |

Bounded normalization is selected for numerical and semantic transparency, not
because the literature establishes a Michaelis–Menten sensory response. It
adds one positive half-scale per channel. Unlike linear reference scaling, its
shape and gain can in principle be separated using responses spanning several
feature magnitudes. They may still be strongly correlated over a narrow range.

## Selected encoder E1

For a finite pre-collision sample, define:

```text
omega_plus(t) = max(omega(t), 0)
expanding(t)  = 1 if sample.approaching and omega(t) > 0, else 0

u_LC4(t)   = omega_plus(t) / (omega_plus(t) + omega_half)
u_LPLC2(t) = expanding(t) * theta(t) / (theta(t) + theta_half)

external_drive_LC4(t)   = G_LC4   * u_LC4(t)
external_drive_LPLC2(t) = G_LPLC2 * u_LPLC2(t)
```

where:

- `omega_half > 0` has units `rad/s`;
- `theta_half > 0` has units `rad`;
- `G_LC4 >= 0` and `G_LPLC2 >= 0` have units `mV_eq`; and
- `u_LC4` and `u_LPLC2` are dimensionless NeuroFly-derived features in
  `[0, 1)`.

No numeric value is selected for any of these four parameters. Zero gain is
valid for pathway-isolation experiments; it is not a calibrated absence of a
biological pathway.

The `expanding` gate prevents a large static or receding disk from becoming an
LPLC2 drive merely because it has nonzero angular size. Literature motivates
expansion selectivity, but this exact binary gate is a NeuroFly encoder
assumption necessitated by Level P's limited scalar vocabulary. It does not
reconstruct radial motion opponency.

E1 has no encoder state, convolution, adaptation, threshold, stochastic source,
or added latency. Output is evaluated from the current sample only. The Phase
2B membrane and synaptic filters remain separate and unchanged.

## LC4 mapping

- **Input:** positive instantaneous `angular_expansion_velocity_rad_s`.
- **Normalization:** bounded by the free positive `omega_half_rad_s`.
- **Gain:** separate free `lc4_gain_mv_eq`.
- **Time:** current pre-collision sample; no encoder-side filter or offset.
- **Negative/zero input:** maps to zero, never to inhibition.
- **Targets:** every validated LC4 body receives the same value under the
  initial bilateral broadcast policy.

Ache supports an angular-velocity-related LC4 contribution at GF. It does not
establish the bounded normalization, gain, population homogeneity, or
`mV_eq` semantics.

## LPLC2 mapping

- **Input:** instantaneous `angular_size_rad`, only while the scalar stimulus
  is positively expanding.
- **Normalization:** bounded by the free positive `theta_half_rad`.
- **Gain:** separate free `lplc2_gain_mv_eq`.
- **Time:** current pre-collision sample; no encoder-side filter or offset.
- **Receding/static input:** the expansion gate maps it to zero, never to
  inhibition.
- **Targets:** every validated LPLC2 body receives the same value under the
  initial bilateral broadcast policy.

This is intentionally simpler than Ache's non-monotonic GF size component and
Klapoetke's spatial radial-motion computation. The former is not an upstream
drive measurement; the latter cannot be reconstructed from Level P scalars.
The selected monotone size term is therefore a falsifiable first approximation,
not a claim about LPLC2 physiology.

## Temporal, baseline, population, and laterality policies

### Time and latency

The following times remain distinct:

```text
environment/stimulus time
    → E1 evaluation at a neural step boundary (no added offset)
    → LC4/LPLC2 external_drive interval
    → visual-neuron threshold/spike
    → Phase 2B chemical delay
    → DNp01 state/spike
```

For Phase 2E, E1 is sampled at Phase 2B neural step boundaries. A sample at
`t_n` produces a piecewise-constant drive on `[t_n, t_n + dt)`. There is no
separate encoder timestep and no interpolation. Stimulus/environment producers
may run independently but must be sampled deterministically onto that time
base. Rendering FPS remains unrelated.

No biological zero-latency claim is made. “No added encoder latency” is the
minimum computational policy while the relevant LC4/LPLC2 latency is
unresolved. Ache's approximately 19 ms shift includes visual processing and GF
response latency and must not become `encoder_latency_ms`.

### Baseline and negative features

- Baseline drive is exactly zero when the selected feature/gate is absent.
- Negative expansion is rectified to zero; it is not an inhibitory current.
- Receding and scalar contraction therefore produce zero E1 drive.
- Zero baseline and exact rectification are declared NeuroFly simplifications.

Klapoetke supports rejection of receding, contraction, and motion-free
darkening by biological LPLC2. E1 can represent the expansion sign distinction,
but it cannot reproduce the spatial circuit mechanism.

### Population and laterality

E1 broadcasts one value identically to every body of a type: 126 LC4 bodies
receive the LC4 value and 185 LPLC2 bodies receive the LPLC2 value. Every body
ID remains explicit in the resulting schedule. No body-level heterogeneity is
introduced.

The initial policy is bilateral broadcast: left- and right-annotated bodies of
the same type receive identical values. This is an approximation, not evidence
that a real centered or off-center stimulus drives both eyes equally. Level P
ignores stimulus center because no validated center-to-MaleCNS-body mapping
exists. Level C column topology must not be used to fabricate one.

### Determinism

Identical stimulus, encoder configuration, candidate contract, and timestep
must produce exactly the same ordered schedule. E1 has no random generator,
noise, adaptation, or hidden state.

## Control-stimulus capability

| Control | E1 status |
| --- | --- |
| Approaching scalar loom | Representable as the two selected features. |
| Receding / scalar contraction | Representable only by negative expansion and therefore zero-drive policy. |
| Static / zero expansion | Produces zero drive even when angular size is nonzero. |
| Motion-free darkening | Not faithfully representable by `theta` and `omega` alone; the existing geometry lacks an edge-motion/luminance channel. |
| Wide-field translation | Not faithfully representable; Level P lacks focality and motion-field structure. |
| Off-center / monocular stimulation | Not faithfully representable; bilateral broadcast ignores center and body-specific coverage. |

Unsupported controls must be reported as such. Phase 2E must not invent a
darkening, translation, focality, eye-side, or receptive-field discriminator.

## Parameter provenance and Phase 2E treatment

| Parameter / policy | Symbol / units | Role | Evidence/source | Evidence class | Phase 2E treatment |
| --- | --- | --- | --- | --- | --- |
| LC4 feature channel | `omega_plus`, `rad/s` before normalization | Velocity-related population feature | Ache pathway-silencing GF recordings | `DIRECT_CIRCUIT_EVIDENCE` for the qualitative association | Fixed channel choice; exact mapping remains a NeuroFly assumption. |
| LPLC2 feature channel | `theta`, `rad` | Size-related population feature during expansion | Ache pathway-silencing GF recordings; Klapoetke expansion selectivity | `DIRECT_CIRCUIT_EVIDENCE` for the qualitative association | Fixed channel choice with explicit expansion gate. |
| LC4 gain | `G_LC4`, `mV_eq` | Maps normalized feature to Phase 2B drive | No MaleCNS or circuit-specific value | `NEUROFLY_FREE_PARAMETER` | Required, finite, `>= 0`; no default presented as calibrated. |
| LPLC2 gain | `G_LPLC2`, `mV_eq` | Maps normalized feature to Phase 2B drive | No MaleCNS or circuit-specific value | `NEUROFLY_FREE_PARAMETER` | Required, finite, `>= 0`; no default presented as calibrated. |
| Velocity half-scale | `omega_half`, `rad/s` | Controls LC4 normalization curvature | Bounded form selected for explicit extreme behavior, not measured biology | `NEUROFLY_FREE_PARAMETER` | Required, finite, `> 0`; no biological default. |
| Size half-scale | `theta_half`, `rad` | Controls LPLC2 normalization curvature | Bounded form selected for explicit extreme behavior, not measured biology | `NEUROFLY_FREE_PARAMETER` | Required, finite, `> 0`; no biological default. |
| Positive-expansion rule | `expanding`, dimensionless Boolean | Rejects static/negative expansion | LPLC2 looming selectivity supports the direction; exact gate is NeuroFly-defined | `DROSOPHILA_PRIOR` | Fixed versioned rule; not a fitted inhibitory effect. |
| Encoder baseline | `0 mV_eq` | Drive with absent feature | Tonic pathway drive is not established here | `UNRESOLVED` biologically | Fixed zero simplification; no configurable baseline in v1. |
| Encoder filter constant | omitted, `ms` | Would add causal sensory memory | GF and GCaMP time courses cannot isolate it | `UNRESOLVED` | No filter and no parameter in v1. |
| Encoder latency | omitted; computational offset `0 ms` | Would shift stimulus to drive | The 19 ms GF alignment is not an LC4/LPLC2 encoder delay | `UNRESOLVED` | No added latency and no parameter in v1. |
| Body heterogeneity | omitted | Would vary drive by body | Level P has no body-specific physiological constraint | `UNRESOLVED` | Identical within-type broadcast. |
| Stochastic term | omitted | Would add input variability | No selected distribution or circuit-specific magnitude | `UNRESOLVED` | Deterministic; no RNG or seed. |

The bounded functional form, bilateral broadcast, exact gate, and zero
baseline are NeuroFly modelling assumptions even where qualitative published
evidence motivates them. Evidence classification does not turn them into
MaleCNS fields.

## Phase 2C saturation and required observability

Phase 2C showed that sufficiently strong short `mV_eq` pulses can make all
targeted visual neurons spike once. Above that regime, doubling pulse amplitude
left event counts and coupling increments unchanged while advancing timing.
E1 must not hide this threshold effect or choose gains to avoid it by fiat.

A future run must retain, at minimum:

- raw `theta` and `omega` samples;
- the expansion gate and normalized `u_LC4`/`u_LPLC2` values;
- emitted `external_drive` per population/body;
- visual-neuron first-spike times and counts;
- delivered-event counts/times and model increments; and
- both DNp01 subthreshold trajectories and spikes.

Realistic time-varying drives may carry amplitude information through membrane
state and spike timing even where spike counts saturate. Whether they operate
mostly below or above visual-neuron threshold is an empirical/model question;
Phase 2D assigns no calibrated operating range.

## Identifiability and calibration order

The four free encoder parameters are not identifiable from DNp01 first-spike
time alone. In particular, encoder gains affect visual spike timing/count,
whereas `k_syn_mv_per_contact` affects the DNp01 event increment only after a
presynaptic spike exists. A narrow stimulus range can also correlate a gain
with its normalization half-scale.

| Quantity | Potential constraint | Present limitation |
| --- | --- | --- |
| `omega_half` | LC4 or pathway-isolated response shape across multiple expansion-velocity ranges | Existing GF component is downstream; direct LC4 population voltage/spike calibration is absent. |
| `theta_half` | LPLC2 population response shape across multiple sizes during matched focal expansion | GCaMP dynamics and spatial selectivity must not be mistaken for instantaneous drive. |
| `G_LC4` | LC4 response timing/count or another declared visual-population observable after shape is constrained | Phase 2B applies a homogeneous LIF model with unmeasured LC4 input units. |
| `G_LPLC2` | LPLC2 response timing/count or another declared visual-population observable after shape is constrained | Same limitation; size-only Level P omits radial-motion computation. |
| `k_syn` | DNp01 subthreshold response after measured/known visual spike and event timing | Contact count does not determine efficacy; Phase 2C shows first-spike degeneracy. |
| relative channel behavior | Pathway-isolated GF subthreshold time courses after upstream channel constraints | Silencing data include downstream and omitted inhibitory effects. |

Recommended future order:

1. Validate feature sign, gate, and time-course shape against LC4/LPLC2
   population measurements under matched stimuli, accounting for measurement
   dynamics.
2. Constrain `omega_half` and `theta_half` from multiple feature ranges before
   fitting output amplitudes.
3. Constrain `G_LC4` and `G_LPLC2` separately using visual-population
   observables, not DNp01 timing alone.
4. With presynaptic spike/event timing constrained, estimate `k_syn` from
   pathway-isolated DNp01 subthreshold responses.
5. Reserve combined DNp01 response and first-spike timing as external
   validation observables, including tests for residual supralinearity; do not
   fit every free parameter jointly to those outputs.

Until direct visual-population observables and measurement models are selected,
all four encoder parameters remain unresolved. No fitting occurs in Phase 2D.

## Phase 2E implementation specification

Phase 2E should implement only E1 as a small module composable with the
existing stimulus and simulator boundaries.

### Immutable configuration

Conceptually, an immutable `LevelPEncoderConfig` should contain:

```text
encoder_id = "level_p_instantaneous_bounded_v1"
lc4_gain_mv_eq                         required finite >= 0
lplc2_gain_mv_eq                       required finite >= 0
lc4_velocity_half_scale_rad_s          required finite > 0
lplc2_size_half_scale_rad              required finite > 0
baseline_policy = "zero_v1"            fixed
negative_feature_policy = "clamp_zero_v1" fixed
population_policy = "bilateral_type_broadcast_v1" fixed
latency_policy = "no_added_latency_v1" fixed
filter_policy = "instantaneous_v1"     fixed
stochastic_policy = "deterministic"    fixed
```

No calibrated convenience defaults should be provided for the four numeric
parameters. Fixed policy identifiers make the assumptions visible and
versionable rather than configurable without evidence.

### API and output

A narrow encoder function should accept:

- the validated `SimulationGraph` or an immutable visual-body target view;
- a `LoomingStimulus` plus explicit pre-collision sample times, or an immutable
  sequence of `LoomingSample` values;
- Phase 2B `dt_ms` and the encoder configuration; and
- provenance identity for the stimulus/configuration.

It should return a Phase 2B-compatible `ExternalDriveSchedule` with one ordered
series for every LC4 and LPLC2 `body_id`, no DNp01 entry, and a provenance ID
derived deterministically from encoder/config/stimulus/graph identities. Each
sample at `t_n` applies to `[t_n, t_n + dt)`. Time values must align exactly
with `dt_ms` within the repository's strict tolerance; malformed, duplicate,
non-finite, post-collision, or inconsistent samples must fail rather than be
rounded or skipped.

A compact companion metadata/result object—not a change to
`CircuitContract`, `BodyColumnInputContract`, or `SimulationResult`—should make
the following recoverable:

- encoder schema/ID/version and fixed policy IDs;
- candidate, graph-scope, and stimulus identity;
- all four free parameter values with units and provenance classification;
- `dt_ms`, ordered sample times, source feature/channel names;
- raw and normalized population feature series;
- target body IDs/types/sides; and
- deterministic configuration/stimulus hashes.

The encoder must not calculate `k_syn`, alter neural configuration, consult
MaleCNS column counts, or drive DNp01.

### Phase 2E tests

Required focused tests are:

- exact deterministic replay and deterministic serialization/hash identity;
- formula checks at zero, ordinary positive, and large finite features;
- monotonic normalized features and bounds `[0, 1)`;
- receding, contraction, and zero-expansion samples produce zero drive;
- collision/undefined expansion and non-finite samples are rejected;
- zero gains are valid; negative/non-finite gains and non-positive/non-finite
  half-scales are rejected;
- exactly all 126 LC4 and 185 LPLC2 bodies are targeted, preserving body ID,
  type, and side;
- bilateral within-type values are identical under the fixed policy;
- neither DNp01 body is ever targeted;
- sample times align exactly to the neural `dt_ms`, with render FPS absent;
- produced schedules are accepted unchanged by Phase 2B
  `ExternalDriveSchedule`/`LIFSimulator`;
- stimulus, `CircuitContract`, `BodyColumnInputContract`, and simulation graph
  remain immutable; and
- provenance output contains no credential or claim of biological gain.

Tests must use explicitly synthetic encoder parameters and must not assert an
invented biological voltage, spike rate, or GF latency.

## Known limitations

- E1 cannot reproduce individual LC4/LPLC2 visual fields, focality, radial
  motion opponency, or eye-specific stimulation.
- Its monotone bounded LPLC2 term does not reproduce Ache's downstream
  non-monotonic GF size component.
- No explicit visual-computation latency, adaptation, or sensory filtering is
  represented.
- Normalization half-scales and gains remain uncalibrated and potentially
  correlated.
- Phase 2B's homogeneous visual-neuron LIF parameters remain modelling priors.
- Motion-free darkening and wide-field translation require richer stimulus
  descriptors; Level P must report them as unsupported rather than pretending
  to discriminate them.
- Level C remains disabled because no provenance-verified bilateral MaleCNS
  column-to-angular-visual-space transform exists.

## Phase 2E readiness

**PASS.** E1 is concrete, deterministic, bounded, compatible with the current
stimulus and `ExternalDriveSchedule`, and introduces only four explicit free
numeric parameters. Its gate, broadcast, zero-baseline, no-filter, and
no-latency policies are fixed and visibly classified as modelling choices.
Phase 2E may implement this contract without fitting gains, normalization
scales, `k_syn`, or biological latency.

## Phase 2E implementation status

The implementation is intentionally small and remains separate from the neural
simulator:

- `LevelPEncoderConfig` validates the four required finite numeric parameters
  and fixed policy identifiers;
- `encode_level_p` consumes aligned, finite, pre-collision `LoomingSample`
  values and applies the equations above without recomputing geometry;
- `LevelPEncodingResult` retains raw features, normalized features, generated
  population drives, deterministic hashes, and provenance metadata; and
- the returned `ExternalDriveSchedule` targets all 126 LC4 and 185 LPLC2 body
  IDs, contains no DNp01 drive, and runs through Phase 2B without simulator
  knowledge of stimulus semantics.

Phase 2E uses no new dependency, performs no calibration, and does not add an
encoder filter, latency correction, Level C information, or body-level
heterogeneity. Focused offline coverage is in
`tests/test_sensory_encoder.py`, including one real-snapshot
encoder-to-LIF integration test.
