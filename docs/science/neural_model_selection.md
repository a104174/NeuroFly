# Phase 2A — neural-dynamics evidence audit and first model selection

**Status:** design and literature audit only. No neural simulator, encoder,
integrator, neural state, or new dependency is implemented by Phase 2A.

Phase 1 provides two separate inputs to this design:

- an immutable `CircuitContract` for 313 MaleCNS bodies and 20,607 induced
  body-level chemical edges; and
- an immutable `BodyColumnInputContract` for 311 LC4/LPLC2 bodies with
  body-specific column topology.

The current sensory boundary is Level P from
[`sensory_consumption_boundary.md`](sensory_consumption_boundary.md). It is a
population-feature approximation, not a per-neuron receptive-field model.
Phase 1D/1E remains D3 for both LC4 and LPLC2: column topology is reproducible,
but no provenance-verified bilateral `male-cns:v1.0` column-to-angular-space
transform is available.

## Sensory-to-simulator boundary

The first experiment keeps four responsibilities distinct. The arrows are
interfaces, not claims that one layer's values are measurements of another
layer:

```text
environment / stimulus state
        │  observation (world and stimulus quantities)
        ▼
future sensory encoder (Level P now; Level C disabled)
        │  model-facing external_drive records
        ▼
future neural simulator (M1 state, events, and DNp01 output)
        │
        ▼
future motor/behaviour mapping (outside the Phase 2A boundary)
```

| Layer | Owns | Does not own |
| --- | --- | --- |
| Environment / stimulus state | object radius and distance, approach velocity, time, stimulus visual centre, angular size, and angular expansion velocity | MaleCNS identity, columns, synapses, or neural state |
| Sensory encoder | feature interpretation, spatial overlap, gain, normalization, population broadcast, temporal filtering, and conversion to `external_drive` | MaleCNS facts, membrane equations, or spike events |
| Biological structural data | body/type/side identity, BodyColumnInputContract topology, chemical edges, `structural_weight`, and transmitter annotations | drive amplitude, receptor-mediated sign, firing rate, or neural dynamics |
| Neural simulator | state equations, timestep, thresholds, resets, time constants, delays, coupling interpretation, and output events | environment rendering, encoder feature meaning, or a claim that parameters are MaleCNS measurements |

The environment may be rendered at any frame rate, while the neural simulator
uses its own integration clock. A future renderer must publish observations;
it must not mutate neuron state directly. The reverse path (neural output to a
motor/behaviour mapping and then to the environment) is outside this phase.

## Sensory capability levels

### Level P — population feature mode (operational)

Level P is the only currently operational environment-to-neuron boundary. A
future encoder consumes the Phase 1C looming features and makes an explicit
NeuroFly approximation:

```text
looming observation
  ├─ angular expansion velocity → LC4 population drive
  └─ angular size              → LPLC2 population drive
```

The mapping is a modelling assumption informed by the cited looming pathway
experiments, not MaleCNS metadata and not an individual-neuron receptive-field
model. The encoder must declare its feature scaling, baseline, saturation,
temporal filtering, and whether all bodies of a type receive a broadcast or
heterogeneous value. Phase 2A supplies none of those numeric gains.

Level P discards the body-specific organization retained in Phase 1E: it does
not use each body's neuropil/hex occupancy, cannot distinguish individual
visual territories, cannot represent column-to-world overlap, and cannot claim
spatially accurate angular looming encoding. It remains useful for a first
timing experiment because the feature-to-population hypothesis is explicit.

### Level C — body-specific column-space mode (preserved, disabled)

Phase 1E provides the biological topology needed by a future spatial encoder:

```text
body_id → neuropil → eye_side → ol_hex1 → ol_hex2 → input-site count
```

`input_count` is a postsynaptic contact count under the validated selection
rule. It is not neural sensitivity, firing rate, activation, or coupling.
Hex coordinates are not azimuth/elevation; a column centroid is not a
receptive-field centre; and equal hex pairs in different neuropils must not be
collapsed automatically. No provenance-verified bilateral
`male-cns:v1.0` optic-column-to-angular-visual-coordinate transform or
world-object-to-column projection is available. Level C therefore remains a
preserved biological/derived data path, not an operational encoder.

## Decision summary

| Decision | Phase 2B proposal | Status of the claim |
| --- | --- | --- |
| Model family | **M1 — LIF with one filtered synaptic state** | selected first model family |
| Initial graph | 311 direct `LC4/LPLC2 → DNp01` edges | deliberate validation subset; the full graph remains preserved |
| Visual input | Level P feature values mapped to deterministic `external_drive` | NeuroFly modelling assumption, not MaleCNS data |
| Synapse-count transform | `sign × k_syn × structural_weight` | `k_syn` is a required free parameter; no numeric value is selected here |
| Initial sign | Depolarizing assumption only for the two direct visual-to-DNp01 pathways | Drosophila circuit prior; not an ACh shortcut and not a claim about every edge |
| Basal activity | Zero baseline for the first validation | declared simplification, not measured biology |
| Stochasticity | Deterministic | chosen for attribution and exact replay |
| Delay | Common 1.8 ms starting prior, sensitivity-tested | Drosophila synaptic precedent, not a MaleCNS measurement |
| First numerical step | 0.1 ms fixed step, with convergence checks | numerical resolution choice, not a biological parameter |
| Phase 2 readiness | Ready to implement Phase 2B after review of this specification | the model is a testable hypothesis, not a finished biological simulation |

The choice is intentionally small. GF/DNp01 spike timing is important enough
to make a thresholded model useful, but LC4/LPLC2 membrane and receptor
properties are not sufficiently measured to justify a detailed conductance or
multi-compartment model. A homogeneous LIF model is therefore a falsifiable
first hypothesis. It does not assert that all LC4/LPLC2 cells are biologically
spiking or that the resulting voltages are calibrated physiology.

## Evidence reviewed

### Shiu et al. (2024), Nature

Shiu et al., *A Drosophila computational brain model reveals sensorimotor
processing*, DOI
[`10.1038/s41586-024-07763-9`](https://doi.org/10.1038/s41586-024-07763-9),
implemented a whole-brain LIF model using FlyWire connectivity and predicted
neurotransmitter identity. The Methods describe a leaky state with an
exponentially decaying, alpha-like synaptic state, threshold/reset/refractory
events, a fixed synaptic delay, and a single free per-synapse voltage-step
parameter. Their published model precedent is:

- resting and reset potential: −52 mV;
- threshold: −45 mV;
- membrane time scale: 20 ms (from a resistance/capacitance prior);
- synaptic decay: 5 ms;
- refractory period: 2.2 ms;
- synaptic delay: 1.8 ms; and
- a fitted per-synapse scale (`W_syn`), rather than a value supplied by the
  connectome.

The model used FlyWire materialization v630, not `male-cns:v1.0`. Its common
cell model, transmitter-derived signs, zero basal firing, omitted morphology,
omitted receptor dynamics, omitted gap junctions, and fitted synaptic scale
are modelling choices. The authors explicitly caution that absolute firing
rates are unlikely to be accurate and that additional receptor, synapse, and
morphology information could improve the model. These values are therefore
published modelling precedent, never MaleCNS facts.

The open Methods/preprint record of this model gives the equations, parameter
origins, zero-baseline policy, and limitations in detail:
[`Shiu et al. Methods`](https://storage.prod.researchhub.com/uploads/papers/2023/07/03/2023.05.02.539144.full.pdf).
The reference implementation is also public, but its code is a precedent and
not a NeuroFly dependency:
[`philshiu/Drosophila_brain_model`](https://github.com/philshiu/Drosophila_brain_model).

**Supports:** a simple connectome-constrained LIF model can generate
testable, reproducible circuit predictions; filtered synapses and a global
calibration parameter are practical abstractions at this scale.

**Does not justify:** importing any value as a MaleCNS measurement, assigning
one sign to every cholinergic edge, treating `ConnectsTo.weight` as a
physiological efficacy, or claiming calibrated LC4/LPLC2/DNp01 firing rates.

### Ache et al. (2019), Current Biology

Ache et al., *Neural Basis for Looming Size and Velocity Encoding in the
Drosophila Giant Fiber Escape Pathway*, DOI
[`10.1016/j.cub.2019.01.079`](https://doi.org/10.1016/j.cub.2019.01.079),
used in-vivo whole-cell patch-clamp recordings from GF, genetic silencing, and
EM reconstruction. They found direct LC4 and LPLC2 input onto the GF and
associated LC4 with an angular-velocity component and LPLC2 with an
angular-size component. Their phenomenological GF model used a linear
angular-velocity term and a Gaussian angular-size term, plus empirically
measured inhibitory components; it was not a neuron-dynamics model.

The experiment measured a roughly 19 ms onset/sensory latency in the GF
recording regime, not a universal chemical synaptic delay. The authors fitted
isolated-pathway contributions to the combined membrane response and reported
that a negative residual could reflect an additional inhibitory input and/or
supralinear concurrent integration. Their weighted isolated-component fit had
`R²` around 0.93 across the tested looming conditions. The paper proposes
supralinear summation within or just presynaptic to GF; it does not establish a
particular supralinear equation for every MaleCNS body.

The measured variable was whole-cell GF membrane potential during expanding
disk looming trials (including the tested `r/v` regimes), compared across
LC4-silenced, LPLC2-silenced, and control preparations. The residual was a
membrane-response difference after summing isolated components, not a direct
measurement of a synaptic nonlinearity. Its size and mechanism therefore do
not identify whether the effect is intrinsic to GF, presynaptic, or an omitted
inhibitory pathway.

For clarity, the paper's phenomenological fit can be summarized (with its
published notation) as:

```text
V_LC4(t)   = C1 * angular_velocity(t - d1)
V_LPLC2(t) = C2 * exp(-(ln[angular_size(t - d2)] - ln[C3])^2 / (2*C4^2))
V_GF(t)    = W_LPLC2*V_LPLC2 + W_LC4*V_LC4 + W_i1*V_i1 + W_i2*V_i2
```

`V_i1` is a size-dependent sigmoid and `V_i2` a smaller LC4-dependent
size-Gaussian inhibition. Ache et al. fitted, among other constants,
`C1=0.0002567`, `d1=d2=0.019 s`, `C2=1.7`, `C3=42°`, `C4=0.52`, and weights
`W_LPLC2=1.45`, `W_LC4=1.62`, `W_i1=2.27`, `W_i2=1`. These are recorded only
as published phenomenological evidence; they are not NeuroFly LIF parameters,
not MaleCNS fields, and not an angular transform for the column contract.

**Supports:** the first benchmark must retain LC4-only, LPLC2-only, and
combined conditions; GF membrane/state time courses and output spike timing
are meaningful observables; direct visual-to-GF depolarization is a defensible
Drosophila prior for the two central pathways.

**Does not justify:** copying the phenomenological formula as LC4/LPLC2
neuron dynamics, assigning its fitted coefficients to MaleCNS synapses, or
hard-coding a supralinear term before testing whether threshold and filtered
integration already reproduce the qualitative phenomenon.

### Klapoetke et al. (2017), Nature

Klapoetke et al., *Ultra-selective looming detection from radial motion
opponency*, DOI
[`10.1038/nature24626`](https://doi.org/10.1038/nature24626), established
LPLC2 as a localized, radial-motion-opponent looming detector. LPLC2 showed
strong selectivity for focal expansion and little response to wide-field
translation, receding motion, or motion-free darkening; optogenetic activation
produced a rapid GF depolarization and escape-related effects.

**Supports:** looming, receding, darkening, wide-field, and contraction controls
are scientifically informative, and the visual pathway is fast and
feature-selective.

**Does not justify:** a membrane time constant, threshold, receptor identity,
or an angular coordinate for a `male-cns:v1.0` body. A separate Drosophila GF
recording report describes LC4/LPLC2 presynaptic activity as apparently
non-spiking, so representing every visual body with LIF is explicitly a
model hypothesis to be challenged:
[`PLOS GF recording`](https://doi.org/10.1371/journal.pone.0224057).

### von Reyn et al. (2014), Nature Neuroscience

von Reyn et al., *A spike-timing mechanism for action selection*, DOI
[`10.1038/nn.3741`](https://doi.org/10.1038/nn.3741), used intracellular GF
recording during head-fixed escape. The timing of a single GF spike relative
to parallel escape circuitry determined short- versus long-mode escape. A
simple higher-threshold GF model captured the action-selection logic.

**Supports:** DNp01/GF first-spike timing is a meaningful first output
benchmark, and a threshold/reset model is more informative than a purely
continuous state for that benchmark.

**Does not justify:** a specific MaleCNS membrane parameter, complete motor
propagation, or a behaviour model inside the current DNp01 endpoint.

### Additional parameter and model precedents

- Kakaria and de Bivort, *Ring Attractor Dynamics Emerge from a Spiking Model
  of the Entire Protocerebral Bridge*, DOI
  [`10.3389/fnbeh.2017.00008`](https://doi.org/10.3389/fnbeh.2017.00008),
  showed that LIF and even non-spiking leaky-integrator variants can reproduce
  a robust network-level attractor. This supports M2 as a useful control, not
  as a reason to discard GF timing.
- Lazar et al., *Accelerating with FlyBrainLab the discovery of the functional
  logic of the Drosophila brain in the connectomic and synaptomic era*, DOI
  [`10.7554/eLife.62362`](https://doi.org/10.7554/eLife.62362), is another
  connectome-modeling precedent behind the refractory prior; it is not a
  measurement of this candidate circuit.
- Gouwens and Wilson, *Signal Propagation in Drosophila Central Neurons*, DOI
  [`10.1523/JNEUROSCI.0764-09.2009`](https://doi.org/10.1523/JNEUROSCI.0764-09.2009),
  measured passive properties and spike initiation in antennal-lobe projection
  neurons. It demonstrates substantial compartmental and recording issues; it
  is a Drosophila prior, not an LC4/LPLC2/GF measurement.
- Rohrbough and Broadie, *Electrophysiological analysis of synaptic
  transmission in central neurons of Drosophila larvae*, DOI
  [`10.1152/jn.2002.88.2.847`](https://doi.org/10.1152/jn.2002.88.2.847),
  reported central-neuron resting potentials around −50 to −60 mV and
  nicotinic ACh-mediated excitation in the larval CNS. It does not measure
  the candidate adult male circuit.
- Titlow et al., *The Nicotinic Acetylcholine Receptor Dα7 Is Required for an
  Escape Behavior in Drosophila*, DOI
  [`10.1371/journal.pbio.0040063`](https://doi.org/10.1371/journal.pbio.0040063),
  links cholinergic visual/mechanosensory input and Dα7 function to GF escape
  circuitry. It supports a pathway-level cholinergic/depolarizing prior, not
  a receptor or sign annotation for each MaleCNS connection.
- Hamasaka et al., *Inhibitory muscarinic acetylcholine receptors enhance
  aversive olfactory learning in adult Drosophila*, DOI
  [`10.7554/eLife.48264`](https://doi.org/10.7554/eLife.48264), demonstrates
  that a metabotropic muscarinic ACh receptor can inhibit responses in an
  adult fly circuit. Together with fast ionotropic nicotinic signalling, this
  is why presynaptic ACh alone cannot determine a connection sign here.
- Jürgensen et al., *A neuromorphic model of olfactory processing and sparse
  coding in the Drosophila larva brain*, DOI
  [`10.1088/2634-4386/ac3ba6`](https://doi.org/10.1088/2634-4386/ac3ba6),
  is a spiking larval model using filtered synapses. Its time constants are
  modelling precedent, not LC4/LPLC2/DNp01 measurements.
- Paul et al., *Bruchpilot and Synaptotagmin collaborate to drive rapid
  glutamate release and active zone differentiation*, DOI
  [`10.3389/fncel.2015.00029`](https://doi.org/10.3389/fncel.2015.00029),
  measured approximately 1.8 ms wild-type synaptic delay at a Drosophila
  neuromuscular junction. That supports a millisecond-scale prior only; it is
  not a central MaleCNS delay measurement.

## Answers to the Phase 2A scientific questions

1. **Spiking or continuous?** Use spiking M1 for the first model, with M2 as
   an offline comparison/control. A continuous model can test subthreshold
   feature integration but cannot produce a discrete DNp01/GF spike time.
2. **Is GF timing important?** Yes. The single-spike timing result in von Reyn
   et al. makes millisecond output timing a biological target even though the
   current experiment stops at DNp01 and does not simulate TTMn/PSI.
3. **What temporal resolution is needed?** Start at `dt = 0.1 ms`. This is a
   numerical choice that resolves a 1.8 ms delay, a 2.2 ms refractory interval,
   and sub-millisecond GF events without tying simulation time to display FPS.
   Phase 2B must repeat representative trials at 0.05 and 0.2 ms and report
   convergence of first-spike time and subthreshold traces.
4. **Why model LC4/LPLC2 as spiking?** Direct visual-to-GF experiments show
   fast depolarizing drive and the endpoint GF is spiking. Direct evidence that
   every LC4/LPLC2 body emits conventional action potentials is incomplete and
   may be negative in some preparations. LIF visual cells are therefore a
   deliberately falsifiable simplification; a graded-input control remains
   required before interpreting visual-cell spike counts.
5. **Which parameters are generic?** The Shiu/Kakaria/Lazar/Jürgensen/Paul
   values are Drosophila modelling or electrophysiology priors. None is a
   measured `male-cns:v1.0` LC4, LPLC2, or DNp01 value. Ache's 19 ms is a GF
   sensory-latency observation, not a membrane or synaptic constant.
6. **How should structural counts enter?** Only through an explicit future
   calibration transform. The selected first transform preserves ordering as
   `k_syn × structural_weight`; `k_syn` is free and exposed.
7. **What sign is known?** Ache/Klapoetke and Dα7/GF physiology support a
   depolarizing prior for the direct visual-to-GF pathway. MaleCNS transmitter
   annotations alone do not supply a connection sign.
8. **What is unknown?** Postsynaptic receptor subtype, receptor number,
   reversal potential, synapse-specific efficacy, and signs for same-type,
   reverse, and cross-type edges are unknown in the candidate contract.
9. **What is `external_drive`?** For M1 it is a deterministic,
   voltage-equivalent additive drive in the same model units as filtered
   synaptic drive. It is produced by a future Level P encoder and is not a
   MaleCNS quantity, rate, current, or conductance.
10. **What can falsify the choice?** A model that cannot reproduce the
    qualitative LC4/LPLC2 feature separation, isolated-versus-combined GF
    timing, stable no-input rest, or deterministic first-spike ordering under
    a defensible calibration is not adequate. Phase 2B must report failure,
    not add unidentifiable nonlinear terms to rescue it.

## Model comparison

| Criterion | M1 — LIF + filtered synapses | M2 — continuous leaky/rate | M3 — discrete propagation/threshold |
| --- | --- | --- | --- |
| GF spike timing | Directly represented by threshold, reset, refractory state | Not represented without an extra output rule | A threshold event is possible, but membrane integration is too schematic |
| Subthreshold GF response | Yes, with a filtered state | Yes, naturally | Weak/implementation-dependent |
| LC4/LPLC2 spiking hypothesis | Explicit, testable simplification | Avoids the hypothesis | Usually collapses it into graph events |
| Structural-count ordering | Preserved by explicit `k_syn` transform | Requires a separate coupling definition | Usually existence/equal coupling; loses magnitude |
| Free parameters | Moderate and inspectable | Fewer initially, but transfer function/coupling units are unresolved | Few, but poor physiological interpretability |
| Level P compatibility | Deterministic voltage-equivalent drive is explicit | Dimensionless forcing is easy but not comparable to GF spikes | Feature-to-threshold rule would be arbitrary |
| Delays and filtered synapses | Native | Requires extra state/filters | Usually absent or ad hoc |
| Determinism and telemetry | Straightforward at 313 nodes | Straightforward | Straightforward, but output is less informative |
| Computational cost | Trivial for 313 nodes and 311 initial edges | Trivial | Trivial |
| False-precision risk | Managed by provenance and calibration gates | Lower parameter risk, higher risk of missing GF timing | High risk of mistaking graph propagation for physiology |
| Scientific role | **Selected first hypothesis** | Required comparison/control | Minimal graph-control baseline |

M1 is selected because this experiment's decisive observable is a
time-ordered GF/DNp01 output, not because LIF is universally correct. A
hybrid graded-LC4/LPLC2 plus spiking-DNp01 model could be scientifically useful
later, but introducing it now adds an unmeasured interface and more sign and
scale assumptions. Hodgkin–Huxley or multi-compartment models are not justified
by the available candidate-specific parameters.

## Selected model: M1

### State and equations

Phase 2B should implement a homogeneous, single-compartment LIF hypothesis
with one filtered synaptic state. Let `v_i` be the model membrane-potential
state, `s_i` a filtered synaptic drive, and `d_i` the model-facing
`external_drive`. `s_i` and `d_i` are voltage-equivalent model quantities in
`mV_eq`; they are not measured currents or conductances.

Between events, for each body `i`:

```text
tau_m * dv_i/dt = -(v_i - V_rest) + s_i(t) + d_i(t)
tau_s * ds_i/dt = -s_i(t)
```

For a presynaptic spike from `j` to `i`, enqueue an event at
`t_spike + delay_ij`. At that event:

```text
s_i <- s_i + sign_ij * k_syn * structural_weight_ij
```

The event is a filtered, exponential/alpha-like synaptic impulse; the state
then decays with `tau_s`. If `v_i >= V_threshold` outside its refractory
interval, emit one spike timestamp, set `v_i <- V_reset`, and hold state
updates for `T_refractory`. Event ordering at equal timestamps must be stable
and deterministic. Initial conditions are `v_i = V_rest`, `s_i = 0`, and no
pending events.

This is a proposal for Phase 2B, not code. It intentionally avoids a
conductance equation and therefore does not imply a receptor reversal
potential or a physical capacitance/resistance for an individual body.

### What is and is not represented

- Threshold, reset, refractory state, filtered coupling, and explicit delays
  represent the timing abstraction needed for the first GF benchmark.
- Individual ion channels, dendritic compartments, adaptation, gap junctions,
  neuromodulation, receptor kinetics, and electrical propagation are not
  represented.
- The graph ends at the two DNp01/GF bodies. The known mixed electrical and
  chemical GF connections to TTMn/PSI are outside this experiment, so this
  model cannot claim complete motor escape behaviour.

## Initial experiment graph

The full `CircuitContract` remains immutable and retains all 20,607 chemical
edges, including same-type, reverse, cross-type, and DNp01-originating edges.
The first M1 validation graph is an explicit **central feed-forward subset**:

```text
126 LC4 bodies  ─┐
                 ├── 311 direct chemical edges → 2 DNp01/GF bodies
185 LPLC2 bodies ┘
```

The 311 edges are the 126 `LC4 → DNp01` edges plus the 185 `LPLC2 → DNp01`
edges in the validated contract. All visual bodies and both DNp01 bodies stay
in scope; edges from DNp01 back to visual cells and LC4/LPLC2 recurrent or
cross-type edges are not deleted from the data product, but are excluded from
the first experiment because their functional signs and roles are less
constrained. This is a documented experiment subset, not a revised biological
connectome.

The subset makes the first sign assumption auditable and tests the literature's
central convergence claim before adding recurrent edges whose receptor and
sign uncertainties could obscure attribution. A later expansion may use the
full graph only after a separate sign/dynamics decision and a comparison with
the central slice.

## `external_drive` semantics under Level P

### Future model-facing record (proposal only)

The simulator should consume a small neutral record and remain agnostic to
whether its producer used Level P, a future Level C projection, or a validated
angular mapping. This is a documentation proposal, not a production type:

| Field | Meaning and owner |
| --- | --- |
| `simulation_time` / `step` | simulation clock supplied by the orchestrator |
| `body_id` | target body, linked to the immutable circuit contract |
| `external_drive` | model-facing drive value supplied by the encoder |
| `input_channel` / `source` | declared feature/channel label, owned by the encoder |
| `encoder_id` / `encoder_version` | reproducible producer identity |
| `units` / `semantics` | explicit model/encoder contract; unresolved until that pair is selected |

The field must not be named or interpreted as current, firing rate, or
conductance by default. The selected neural model and encoder jointly define
its units and meaning; the simulator only applies the declared model
semantics.

For the selected M1 model, `external_drive_i(t)` means:

> a deterministic, piecewise-constant, voltage-equivalent additive drive
> presented to body `i` during a simulation step, expressed in the same
> `mV_eq` scale as `s_i`, with units and scale owned jointly by the selected
> encoder and M1 configuration.

The first Level P encoder proposal (not implemented here) consumes the
model-neutral stimulus features as follows:

```text
LC4 population   ← angular_expansion_velocity_rad_s feature
LPLC2 population ← angular_size_rad feature
```

It must then declare scaling, baseline, saturation, temporal filtering, and
whether the feature is broadcast or heterogeneous. No numeric gain, unit
conversion, per-body sensitivity, or stochastic source is supplied by MaleCNS.
For the first deterministic comparison, zero feature should mean zero
`external_drive` after the declared baseline policy. A Poisson spike source is
not selected: it would add an unmeasured feature-to-rate and rate-to-event
assumption before the GF timing hypothesis can be tested.

The simulator receives the neutral field and does not know whether it came
from Level P, a future Level C projection, or a future validated angular map.
The encoder owns feature interpretation; M1 owns state evolution.

## Structural-weight transformation policy

MaleCNS `structural_weight` is the neuPrint `ConnectsTo.weight` contact-count
quantity. It is not a signed coupling or physiological efficacy. Candidate
transformations are:

| Family | Benefit | Risk/status |
| --- | --- | --- |
| `k × structural_weight` | Preserves strong-versus-weak ordering and has one interpretable global scale | Chosen policy; `k` is unidentifiable without calibration and is confounded with Level P drive scale |
| `k × f(structural_weight)` with saturation/normalization | Could limit extreme degree effects | Adds unsupported function and parameters; deferred |
| Equal coupling for every existing edge | Clean graph-existence control | Discards MaleCNS contact-count ordering; control only |
| Receptor/PSC-specific mapping | Could be more biological | Receptor and connection-level efficacy data are unavailable; unresolved |

Phase 2B must require an explicit positive `k_syn` value in configuration and
must never silently substitute Shiu's fitted `0.275 mV` value. The model edge
is:

```text
w_model_ij = sign_ij × k_syn × structural_weight_ij
```

where `structural_weight_ij` remains directly traceable to MaleCNS and
`k_syn` is a `NEUROFLY_FREE_PARAMETER`. Calibration should use one global scale
before considering any per-type or per-edge scale. A sensitivity sweep and an
equal-coupling control are mandatory if the fitted output depends strongly on
the transform. No transformation from contact count to neural efficacy exists
in the current data products.

## Connection-sign policy

The candidate's LC4, LPLC2, and DNp01 annotations are acetylcholine
consensus/prediction values. A presynaptic transmitter annotation does not
identify the postsynaptic receptor, reversal potential, or sign. Drosophila
central ACh is commonly mediated by nicotinic receptors, and Dα7/GF work
provides direct cholinergic visual-input evidence, but that evidence is not a
body- and connection-specific MaleCNS receptor annotation.

For the first 311-edge central slice only, Phase 2B may use an explicit
`sign_ij = +1` depolarizing assumption. Its provenance is **DROSOPHILA_PRIOR
plus a NeuroFly modelling decision**, supported by the direct visual-to-GF
depolarization and escape experiments. It is not derived by the rule “ACh means
positive,” and it must be reported and sensitivity-tested. All same-type,
reverse, and other cross-type signs are **UNRESOLVED** and remain outside the
first graph. A future full-graph experiment must obtain receptor/functional
evidence or keep signs as explicit alternatives; it must not infer them from
`predicted_nt`/`consensus_nt` alone.

## Parameter provenance and identifiability

The table distinguishes a direct candidate fact from a generic Drosophila prior
and a free NeuroFly choice. Proposed values are starting points for Phase 2B,
not frozen biological truths.

| Parameter | Symbol | Units | Role/population | Proposed Phase 2B treatment | Source | Evidence class |
| --- | --- | --- | --- | --- | --- | --- |
| Resting potential | `V_rest` | mV | all 313 model nodes | −52 starting prior; sensitivity required | Shiu/Kakaria precedent; Drosophila electrophysiology priors | `PUBLISHED_MODEL_ASSUMPTION` |
| Reset potential | `V_reset` | mV | all spiking nodes | −52 starting prior; sensitivity required | Shiu/Kakaria precedent | `PUBLISHED_MODEL_ASSUMPTION` |
| Threshold | `V_threshold` | mV | all spiking nodes | −45 starting prior; sensitivity required | Gouwens/Wilson and Shiu precedent | `DROSOPHILA_PRIOR` |
| Membrane time constant | `tau_m` | ms | all model nodes | 20 starting prior; convergence/sensitivity required | RC prior used by Shiu/Kakaria | `PUBLISHED_MODEL_ASSUMPTION` |
| Filter decay | `tau_s` | ms | all selected chemical inputs | 5 starting prior; sensitivity required | Jürgensen/Shiu modelling precedent | `PUBLISHED_MODEL_ASSUMPTION` |
| Refractory interval | `T_refractory` | ms | all spiking nodes | 2.2 starting prior; sensitivity required | Lazar/Shiu precedent | `DROSOPHILA_PRIOR` |
| Chemical delay | `delay_ij` | ms | selected visual→DNp01 edges | 1.8 common starting prior; no morphology-derived delays | Paul/Shiu precedent | `DROSOPHILA_PRIOR` |
| GF sensory latency reference | `d_GF` | ms | benchmark observation only | approximately 19; not inserted as `delay_ij` | Ache patch-clamp response latency | `DIRECT_CIRCUIT_EVIDENCE` |
| Synapse-count scale | `k_syn` | `mV_eq/contact` | selected chemical edges | required positive free parameter; no default | no MaleCNS physiological conversion | `NEUROFLY_FREE_PARAMETER` |
| Direct visual-edge sign | `sign_ij` | dimensionless | LC4/LPLC2→DNp01 only | +1 declared starting assumption; alternatives tested | Ache/Klapoetke/Dα7 pathway evidence | `DROSOPHILA_PRIOR` |
| Level P drive | `external_drive_i` | `mV_eq` | LC4/LPLC2 target bodies | encoder-supplied; scale and baseline must be configured | Phase 1C features, no MaleCNS amplitude | `NEUROFLY_FREE_PARAMETER` |
| Baseline drive | `b_i` | `mV_eq` | all nodes | zero in first validation; later configurable | Shiu precedent, not measured here | `PUBLISHED_MODEL_ASSUMPTION` |
| Integration step | `dt` | ms | numerical solver | 0.1 initial; 0.05/0.2 convergence checks | numerical design requirement | `NEUROFLY_FREE_PARAMETER` |
| Initial state | `v_i(0), s_i(0)` | mV, `mV_eq` | all nodes | `V_rest`, 0, no queued events | deterministic protocol | `NEUROFLY_FREE_PARAMETER` |
| Resistance/capacitance | `R_m`, `C_m` | MΩ, nF (if used) | exact cells | omitted from normalized equation; exact values unresolved | generic Drosophila priors only | `UNRESOLVED` |
| Supralinear interaction | — | — | combined GF response | not added initially; test emergent threshold/integration first | Ache identifies phenomenon but not mechanism | `UNRESOLVED` |

`structural_weight_ij` itself is a direct `malecns_direct` field and is not a
parameter with physiological units. It is carried into the equation only by
the explicitly calibrated `k_syn` transform.

Identifiability requirements:

- `k_syn` and the Level P drive scale can trade off against one another. Fit
  one global ratio using isolated versus combined first-spike timing and
  subthreshold amplitude, then report sensitivity rather than fitting many
  correlated gains.
- `tau_m`, `tau_s`, and `delay_ij` can be constrained only by subthreshold
  waveform, onset latency, and first-spike timing. Candidate-specific data are
  not currently sufficient to fit them independently; keep the published
  priors and test perturbations.
- `V_threshold` and `T_refractory` can be challenged by first-spike and
  repeated-spike behavior. If no condition constrains repeated spiking, do not
  add adaptation or neuron-specific thresholds.
- The direct-edge sign can be challenged by isolated/combined response
  ordering, but output behavior alone cannot identify receptor subtype. A sign
  choice remains a model assumption until functional receptor data exist.
- Baseline is constrained by the no-stimulus condition. If future recordings
  demonstrate spontaneous activity, replace the zero-baseline simplification
  with a configurable measured or calibrated process.

## Temporal, basal-activity, and stochasticity policies

### Temporal policy

Phase 2B should use a fixed `0.1 ms` integration step initially and an exact
exponential update between event boundaries where possible. It must separate:

- `dt`, the numerical integration resolution;
- `tau_m` and `tau_s`, model time constants;
- `delay_ij`, a model synaptic delay;
- `d_GF`, the approximately 19 ms experimental sensory-latency reference; and
- rendering/environment tick rates, which are independent.

No morphology path length will be used to invent a delay. The common 1.8 ms
delay is a sensitivity-tested Drosophila prior, not a claim that every
MaleCNS synapse has that latency. The first model's refractory behavior is an
absolute hold for the declared interval; it does not reproduce a measured GF
action-potential waveform.

### Basal activity

Use zero baseline (`b_i = 0`) for the first validation, explicitly labelled a
declared simplification inherited as a precedent from Shiu. This makes feature
attribution and no-input rest tests clear, but removes spontaneous activity,
background synaptic drive, and any effect of an inhibitory input on an
otherwise inactive cell. Future baseline activity must be a configurable
experiment condition, not silently added noise.

### Stochasticity

Use deterministic feature drives, initial states, event ordering, and solver
settings for the first experiment. This supports exact replay, debugging,
parameter sensitivity, and attribution of LC4/LPLC2 differences. Poisson input
is a valid future modelling alternative, not a biological requirement. If a
future experiment introduces stochastic drive, its random generator, seed,
stream, and distribution must be recorded and repeated trials must be
explicit.

## GF/DNp01 benchmark

The first benchmark stops at the two DNp01/GF bodies. It does not infer TTMn,
PSI, wing, leg, or escape behavior. Every condition uses the same candidate,
graph subset, configuration, and deterministic initial state.

| Condition | Input | Required observations |
| --- | --- | --- |
| No stimulus | zero Level P features and zero direct drive | rest stability, no spontaneous spike, exact replay |
| LC4-only | angular-expansion-velocity-related feature; LPLC2 drive zero | DNp01 subthreshold trace and first-spike timing versus loom speed |
| LPLC2-only | angular-size-related feature; LC4 drive zero | DNp01 subthreshold trace and first-spike timing versus loom size |
| Combined | both Level P features | joint threshold timing, peak/subthreshold state, isolated-versus-combined comparison |
| Receding/contraction/darkening/wide-field controls | Phase 1C control stimuli | failure or reduction of the feature-specific response where literature predicts selectivity |

The qualitative constraints are:

- LC4-only should carry the velocity-related component;
- LPLC2-only should carry the size-related component;
- combined input should be compared with the isolated traces and may show
  earlier/stronger threshold crossing through ordinary integration and
  thresholding;
- the first spike time, if present, is the primary timing output; and
- subthreshold DNp01 state before the spike must remain visible.

Ache's weighted fit and its interpretation of a negative residual motivate a
supralinearity diagnostic, not a hard-coded term. Phase 2B should first test
whether filtered integration plus threshold can generate the observed
qualitative combined effect. If a residual remains, report whether it could be
an omitted inhibitory pathway, an unsupported sign, or a genuine missing
nonlinearity. Do not fit an extra nonlinear interaction without an independent
observable.

Quantitative constraints are limited to reported timing/ordering and waveform
comparisons in the cited experiments. No numeric firing-rate, voltage,
threshold, or escape acceptance criterion is invented for this MaleCNS
candidate. A selected parameter set that produces highly sensitive, unstable,
or non-reproducible outcomes across plausible priors falsifies the first-model
claim rather than licensing more free parameters.

## Phase 2B implementation specification (not implemented)

### Responsibilities

1. **Configuration validation:** require model ID/version, all numerical
   parameters, graph scope, sign policy, baseline policy, external-drive
   semantics, timestep, delay policy, and deterministic/stochastic policy.
2. **Graph adapter:** load `CircuitContract` offline, select the explicitly
   named 311-edge central slice, verify endpoints and preserve links back to
   `structural_weight` and body/type/side provenance. Do not mutate either
   Phase 1 contract.
3. **State engine:** maintain `v_i`, filtered `s_i`, refractory timers, and a
   deterministic delayed-event queue for 313 nodes (or the named subset).
4. **Level P input boundary:** accept already-defined model-facing
   `external_drive` records. Phase 2B may include a narrow adapter for a
   documented fixture, but it must not silently derive drive from column
   counts or implement Level C.
5. **Telemetry:** expose the minimum scientific traces below without making
   full-resolution logging mandatory by default.

### Configuration proposal

```text
model_id: lif_filtered_synapse
model_version: <explicit version>
candidate_id: looming_giant_fiber_v1
circuit_contract_version: <schema/integrity reference>
graph_scope: direct_visual_to_dnp01_v1
dt_ms: 0.1
tau_m_ms: 20.0
tau_s_ms: 5.0
v_rest_mV: -52.0
v_reset_mV: -52.0
v_threshold_mV: -45.0
refractory_ms: 2.2
delay_ms: 1.8
synapse_gain_mV_eq_per_contact: <required calibrated value>
sign_policy: direct_visual_dnp01_depolarizing_assumption_v1
baseline_policy: zero
stochastic_policy: deterministic
external_drive_semantics: voltage_equivalent_mV_eq_v1
encoder_id: <explicit Level P encoder identifier>
encoder_version: <explicit version>
seed: null  # mandatory integer if stochasticity is later enabled
```

The exact configuration serialization is a Phase 2B decision; these names
are a contract proposal, not a production schema in Phase 2A.

### Integration and numerical requirements

- Use fixed-step deterministic scheduling with stable body-ID ordering.
- Apply exact exponential decay between events when the drive is constant over
  a step; document the event/step boundary convention.
- Process delayed events in timestamp order, with a stable tie-break by source
  and target body ID.
- Reject non-finite parameters, non-positive time constants, missing gains,
  unknown graph/sign policies, and ambiguous units.
- Run `dt` convergence checks before interpreting first-spike timing.
- Do not choose an optimization technology based on 313 neurons; a transparent
  project-owned integrator is sufficient.

### Minimum telemetry

Each run should make available, at least on demand:

- simulation time and step;
- body ID and type for each recorded node;
- `v_i` and filtered `s_i` state;
- applied `external_drive_i` and incoming model-coupling contribution;
- refractory status and threshold/spike event timestamp;
- DNp01 first-spike time and output summary;
- candidate/contract/artifact integrity identifiers;
- model, encoder, benchmark, configuration versions, and seed policy.

Telemetry must not imply that `v_i` is an observed MaleCNS voltage or that
`s_i` is a measured conductance.

### Required Phase 2B tests

- zero-input decay to `V_rest` and no spontaneous spike;
- isolated-neuron deterministic behavior;
- threshold, reset, and refractory semantics;
- one-edge propagation with exact delay and filtered decay;
- ordered effect of larger `structural_weight` under the selected `k_syn`
  transform, plus equal-coupling control;
- delay/timestep convergence and stable equal-time event ordering;
- exact repeatability with the same deterministic configuration;
- left/right symmetry sanity check where the candidate graph permits it;
- LC4-only, LPLC2-only, and combined conditions;
- no direct environment input path to DNp01;
- no mutation of `CircuitContract` or `BodyColumnInputContract`; and
- configuration/provenance validation, including rejection of missing units or
  an unstated sign policy.

### Dependency decision

Choose **A — NumPy plus a project-owned integrator** for Phase 2B, subject to a
small prototype and profiling. NumPy gives transparent vector operations and
deterministic arrays while leaving event scheduling and telemetry under project
control. Brian2 is a credible published precedent, but it adds a substantial
runtime dependency and simulator/code-generation semantics that are not needed
for 313 nodes. Standard Python loops remain a useful reference test but are not
the preferred implementation once traces and event queues are added. Rust,
WASM, GPU, or browser execution are not justified. No dependency is added in
Phase 2A.

## Reproducibility metadata

Every future neural run must record:

- candidate circuit ID/version and graph-scope identifier;
- MaleCNS dataset (`male-cns:v1.0`) and endpoint;
- CircuitContract schema/integrity and source snapshot;
- BodyColumnInputContract schema/hash if referenced by an encoder;
- sensory mode (`P` or future `C`), encoder ID/version, and all encoder
  parameters;
- complete stimulus parameters and benchmark condition;
- every model parameter, units, evidence class, and calibration procedure;
- deterministic/stochastic policy and seed/stream when applicable; and
- model ID/version, code revision, numerical method, timestep, and telemetry
  configuration.

No credential, secret, or unverified angular coordinate belongs in a run
record.

## Scientific safeguards and remaining limitations

- `structural_weight` remains a MaleCNS structural contact count; it is never
  silently renamed as physiological efficacy.
- ACh annotations remain presynaptic biological annotations; they are not a
  universal sign rule. The direct visual-to-DNp01 sign is an explicit,
  limited, sensitivity-tested assumption.
- Level P feature values are environment/encoder quantities. They are not
  MaleCNS amplitudes, rates, currents, or spikes.
- Level C body-column topology is preserved for later work but does not supply
  an environment-to-column map or visual-angle calibration.
- No receptive-field center, azimuth/elevation transform, cross-dataset body
  mapping, or column centroid is introduced.
- No morphology-derived delay, gap-junction coupling, receptor kinetics,
  neuromodulation, adaptation, or motor propagation is inferred.
- The two DNp01 bodies receive no fabricated direct environmental input; their
  first input is activity from the selected graph, except for a future
  explicitly labelled experimental clamp.
- Absolute firing rates, membrane voltages, and behaviour are not claimed to be
  experimentally calibrated by this phase.

## Phase 2A conclusion

The model-selection gate passes for the narrow first experiment:

> **Select M1 — LIF with filtered synapses, deterministic Level P drive, a
> direct visual-to-DNp01 validation graph, explicit limited depolarizing sign,
> global contact-count gain requiring calibration, zero baseline, and a
> millisecond-resolving fixed-step solver.**

Phase 2B may begin implementing and testing this specification. That decision
does not complete sensory modelling, establish body-specific angular vision,
or claim that the simple LIF parameters are MaleCNS measurements. If the
central-slice benchmark cannot be interpreted without adding unsupported
parameters, the correct outcome is to retain the structural data and revise
the model choice, not to hide the uncertainty in code.
