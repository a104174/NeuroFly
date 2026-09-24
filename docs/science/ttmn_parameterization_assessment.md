# Phase 6D — TTMn parameterization and validation evidence assessment

**Decision: A — retain the Phase 6C exploratory integrator, without physiological calibration.** The literature reviewed here does not identify a biological quantity corresponding to either Phase 6C parameter. The integrator remains useful for deterministic event propagation, simulated intervention comparisons, and sensitivity analysis. It is not a TTMn electrophysiology model and cannot be quantitatively validated against muscle voltage, motor-neuron latency, or behavior.

**Scope:** documentation only. No simulator, artifact, transport, frontend, dependency, source-data, or model behavior changed.

## 1. Repository and model audit

The audit began at clean main, HEAD
9e01057be54e42ba54e23b4f30385eb7114cd9ba, aligned with origin/main.
Phase 6C is committed at that revision; the Phase 6B assessment is
fc06899. Inspected sources included:

- [motor_escape_feasibility.md](motor_escape_feasibility.md), the Phase 6B evidence boundary;
- [motor_pathway_model.md](motor_pathway_model.md), the Phase 6C model, artifact, sensitivity, and real-run record;
- src/neurofly/motor_pathway.py, artifact/CLI code, upstream simulator and runner, and Phase 6C tests.

The pinned downstream evidence contract remains separate from the upstream
313-body circuit contract. It maps exact persisted DNp01 events
10001/R → TTMn 800146/R and 10010/L → TTMn 804642/L. MaleCNS v1.0
ConnectsTo observations have chemical structural weights 70 and 20,
respectively. The evidence contract records no pair-specific electrical
conductance.

Phase 6C implements ttmn_dimensionless_event_integrator, version phase6c_v1.
For each target and stored simulation step it applies exact exponential
decay, followed by same-boundary event injection:

<pre>
x[n] = x[n−1] · exp(−dt_ms / tau_motor_ms)
       + event_count[n] · event_gain
</pre>

State x is dimensionless; dt_ms is the experiment grid spacing. Reference
assumptions are tau_motor_ms = 10 ms and event_gain = 0.25. There is no
transmission delay, stochastic component, threshold, or response event. The
only input is the exact same-run persisted DNp01 SpikeEvent after identity
and grid validation. Structural weights are not read by the update equation.

For one event, the immediate increment equals event_gain. Between events,
tau_motor_ms controls decay of this abstract state. Thus 10 ms is not a
measured TTMn membrane time constant, GF→TTMn delay, conduction time, or
muscle latency. The 0.25 increment is not voltage, current, conductance,
efficacy, response probability, or measured postsynaptic amplitude. The
existing sensitivity sweep varies tau over 5/10/20 ms and gain over
0.1/0.25/0.5. Event identities, times, mapping and peak steps remain fixed,
while state magnitude/decay vary. This is computational sensitivity, not
biological parameter estimation.

## 2. Sources reviewed and evidence classes

“Not found” means not found in this reviewed source set, not a claim that a
measurement cannot exist elsewhere.

| Source | Preparation / result | Provenance and relevance |
| --- | --- | --- |
| King & Wyman (1980), [Anatomy of the giant fibre pathway in Drosophila. I](https://doi.org/10.1007/BF01205017) | Thoracic anatomy of the identified GF pathway. | Anatomical evidence / literature prior. Does not provide a TTMn membrane tau or pair conductance for the MaleCNS identities. |
| Tanouye & Wyman (1980), [Motor outputs of giant nerve fiber in Drosophila](https://doi.org/10.1152/jn.1980.44.2.405) | Adult GF electrically stimulated in brain, GF axon recorded intracellularly, TTM and DLM muscle potentials measured. Single GF spikes drive short-latency muscle responses; TTM follows stimuli up to 300 Hz and DLM up to 100 Hz. | Direct circuit-output measurements, not TTMn voltage or a Phase 6C state decay. Sex is not established by the abstract/source material inspected for this audit. |
| Phelan et al. (1996), [Mutations in shaking-B prevent electrical synapse formation in the Drosophila giant fiber system](https://doi.org/10.1523/JNEUROSCI.16-03-01101.1996) | Developmental GF dye coupling to TTMn and PSI; shak-B2 prevents dye coupling / functional gap-junction formation. | Direct developmental connectivity evidence; not adult pair conductance. |
| Blagburn et al. (1999), [Null mutation in shaking-B eliminates electrical, but not chemical, synapses…](https://doi.org/10.1523/JNEUROSCI.19-21-09374.1999) | Ultrastructure shows chemical release-site features and close appositions consistent with electrical contacts; electrical specializations are lost in the Shaking-B mutant while chemical structures remain. | Direct ultrastructure plus interpretation; does not quantify coupling conductance. |
| Phelan et al. (2008), [Molecular mechanism of rectification at identified electrical synapses…](https://doi.org/10.1016/j.cub.2008.10.067) | Shaking-B isoforms form heterotypic channels; expression experiments show asymmetric voltage gating/rectification consistent with GF→target direction. | Channel/heterologous evidence, not a pair-specific in-vivo conductance. |
| Allen & Murphey (2007), [The chemical component of the mixed GF-TTMn synapse uses acetylcholine](https://doi.org/10.1111/j.1460-9568.2007.05686.x) | Chemical transmission is functional; disruption of electrical transmission or chemical release reveals delayed residual TTM response and impaired repetitive reliability. | Direct pharmacological/genetic circuit evidence; no numeric Phase 6C-equivalent gain. |
| von Reyn et al. (2014), [A spike-timing mechanism for action selection](https://doi.org/10.1038/nn.3741) | Looming, GF recordings, and escape kinematics; GF spike timing relates to short-mode output while parallel GF-independent escape output remains. | Direct neural/behavioral measurements; endpoints are not TTMn state. |
| Augustin et al. (2017), [Reduced insulin signaling maintains electrical transmission in a neural circuit in aging flies](https://doi.org/10.1371/journal.pbio.2001655) | Adult females at 25°C; electrical brain stimulation and intracellular muscle recordings quantify age-related brain-stimulus→muscle-EPSP latency. Thoracic stimulation separately probes motor-neuron-to-muscle output. | Direct circuit/muscle measurements, not isolated GF→TTMn delay or TTMn membrane tau. |
| Augustin, Zylbertal & Partridge (2019), [A Computational Model of the Escape Response Latency…](https://doi.org/10.1523/ENEURO.0423-18.2019), [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6469880/) | Four-cell NEURON conductance model; simplified GF, TTMn, PSI and DLMn; gap conductance varied to reproduce young/old end-to-end muscle latency. | Published computational model. Estimated and manually adjusted values are model fit/assumption, not direct TTMn measurements. |
| Günay et al. (2015), [Distal spike initiation zone location estimation… in an identified Drosophila motoneuron](https://doi.org/10.1371/journal.pcbi.1004189) | Electrophysiology and model for larval third-instar aCC/MN1-Ib, with channel sources from in-vivo aCC, heterologous DmNav expression and cultured fly neurons. | Literature prior for a different cell/developmental preparation, not adult TTMn. |

The Augustin article links its code as [ModelDB 245415](https://modeldb.science/245415); the public [ModelDBRepository/245415 code](https://github.com/ModelDBRepository/245415) was inspected read-only, including gfpn.py and gfs_param_scan_conductances.py. The repository page showed branch master and one commit, without a release tag or commit identity displayed in the inspected view. The paper describes a 4.3 kB archive. No archive or other external file was downloaded, no code was copied, and NEURON was not installed or run. The code's parameter-scan script activates NEURON CVode; the manuscript does not specify a fixed integration step or solver tolerance. This audit does not claim independent reproduction of the published simulation.

## 3. GF→TTMn: mixed physiology is not one weight

The adult GF→TTMn connection is described as a mixed electrochemical
connection. Its electrical component is Shaking-B-dependent and important
for fast short-latency transmission. Ultrastructure identifies chemical
release sites, and genetic/pharmacological work identifies an
acetylcholine-mediated component. When electrical coupling is disrupted,
residual TTM output is delayed and the chemical component contributes to
circuit response/repetitive reliability. The connection cannot be
represented as one unsupported scalar “synaptic strength.”

Shaking-B channel work supports rectifying electrical transmission in the
GF-to-target direction. It supplies mechanistic evidence, not an in-vivo
pair-specific coupling coefficient for either NeuroFly TTMn.

| Evidence kind | What is evidenced | Numeric quantity usable as model gain? |
| --- | --- | --- |
| CHEMICAL_CONNECTOME_EDGE | MaleCNS v1.0 directed ConnectsTo observations: 10001→800146 weight 70; 10010→804642 weight 20. | No. These remain chemical structural counts. |
| ELECTRICAL_COUPLING | Literature-supported electrical GF→TTMn mechanism. | No pair-specific MaleCNS conductance is available. |
| MIXED_CONNECTION | Literature describes both modalities. | No combined numeric weight exists. |

Neither the unequal chemical structural counts nor geometry supports
inferring left/right electrical asymmetry. Do not convert 70/20 to
conductance, event amplitude, drive, delay, probability, or physiological
gain.

## 4. Augustin et al. (2019) model audit

### Architecture, input, output

The four modeled cells are GF, TTMn, PSI and DLMn. Each uses one to three
unbranched cylindrical sections; each section is divided into 51
isopotential segments. The GF is active and electrically couples to the
TTMn medial passive dendrite, continuous with an active modeled axon. TTMn
has modeled medial and lateral dendrites of 60 and 30 µm, an axon of 50 µm,
and simplified 6 µm diameter; GF input is placed 12 µm from the medial
dendrite proximal end. These are reduced-model geometric inputs, not the
current MaleCNS raw TTMn skeleton.

All sections have passive leak. Active axonal sections use
Hodgkin–Huxley-type transient/persistent Na and K channels, drawing much of
their channel kinetics from the Günay et al. larval aCC model. PSI→DLMn uses
a double-exponential chemical conductance. The public ModelDB source also
creates a GF→TTMn chemical-synapse object, but its default NetCon weight is
zero; in that configuration the operative GF→TTMn input is the electrical
gap-junction mechanism. Do not mistake PSI→DLMn chemical parameters for a
measured GF→TTMn chemical gain.

The protocol injects 120 nA for 0.03 ms at proximal GF, chosen to approximate
high-amplitude brain stimulation. The model records TTMn/DLMn voltage along
the axon and reports time to distal AP peak. Code response detection accepts
a maximum above −30 mV and returns time of the maximum. A fixed 0.35 ms is
added to model AP-peak time to compare against experimental muscle-EPSP
onset; there is no muscle model. That 0.35 ms is estimated as approximately
0.65 ms thoracic stimulus→muscle response minus approximately 0.30 ms
simulated direct motoneuron stimulus→AP peak. It is model-derived, not a
direct isolated NMJ measurement.

### Model parameter provenance

The 2019 paper explicitly says some values were manually adjusted until all
model cells spiked and response latencies matched observations. An
“estimated” value is therefore not automatically a measurement.

| Model quantity | Published/reference value | Provenance class | Interpretation / limitation |
| --- | ---: | --- | --- |
| TTMn diameter | 6 µm | LITERATURE_PRIOR / anatomy | Cited to King & Wyman; simplified geometry, not MaleCNS-derived membrane properties. |
| TTMn axon / medial / lateral dendrite | 50 / 60 / 30 µm | LITERATURE_PRIOR / anatomy | Cited to Godenschwege et al.; modeled sections, not measured electrical cable parameters. |
| GF diameter / length | 8 / 400 µm | LITERATURE_PRIOR / anatomy | Sources include Augustin 2017, Phelan 1996, Smith 1996. |
| Specific membrane capacitance | 1 µF/cm² | ASSUMPTION / estimated | Not direct TTMn measurement. |
| Specific axial resistance | 35.4; paper table prints Ω/cm | ASSUMPTION / estimated | Not direct TTMn measurement. The paper's printed unit is retained here rather than silently normalizing it; this value is not used by NeuroFly. |
| Leak conductance density | 0.03 mS/cm² | ASSUMPTION / estimated | Not measured TTMn leak. |
| Max transient Na conductance density | 300 mS/cm² | LITERATURE_PRIOR | Cited to Günay et al. (2015), a larval aCC model. |
| Max persistent Na conductance density | 0.11 mS/cm² | LITERATURE_PRIOR | Cited to Günay et al. (2015), not adult TTMn. |
| Max K conductance density | 10 mS/cm² | ASSUMPTION / estimated | Not TTMn-specific. |
| Gap conductance, “young” / “old” | 135 / 34.5 µS | MODEL_FIT / estimated | Chosen so model plus fixed NMJ term reproduces young/old TTM/DLM muscle latency targets. Same global g_gap is used at modeled GF→TTMn and GF→PSI electrical junctions; not direct or MaleCNS-pair-specific. |
| PSI→DLMn chemical peak conductance | 80 µS in paper table; code weight 0.08 mS | MODEL_FIT / estimated | Modeled chemical synapse parameter, not a MaleCNS structural count or GF→TTMn coupling. |
| Chemical synaptic rise/decay and reversal | Paper table: 0.1 / 1 ms and 0 mV | ASSUMPTION / standard values | These table values correspond to the PSI→DLMn modeled chemical path. Code also creates a GF→TTMn chemical object with separate defaults but zero NetCon weight; neither defines a measured GF→TTMn chemical gain. |
| PSI→DLMn chemical delay | 0.15 ms in paper/code | ASSUMPTION / estimated | Not GF→TTMn delay. The GF→TTMn code delay is attached to a zero-weight chemical object and is not measured transmission delay. |
| NMJ delay | 0.35 ms | DERIVED_MEASUREMENT / model estimate | Approximately 0.65 ms thoracic stimulus→muscle minus 0.30 ms simulated direct motor stimulation→AP peak. Not independently measured as isolated junction delay. |
| Initial voltage in public source | −65 mV | ASSUMPTION / numerical initialization | Code initialization, not measured TTMn resting potential. |

The public ModelDB model uses a variable-step CVode solver. The paper does
not publish a fixed dt or solver tolerance. Its 0.03 ms value is the stimulus
pulse duration, not an integration step.

### The 135 / 34.5 µS conductance values

The paper explicitly labels these values “estimated.” Authors chose g_gap
such that simulated GF-stimulus→AP-peak time plus the estimated 0.35 ms NMJ
term matched observed young and old muscle-response latencies. They then
used them as young/old model conditions and scanned latency sensitivity.
They are model-fit/estimated global conductances, not direct conductance
recordings, not MaleCNS pair conductances, and not values transferable into
event_gain.

## 5. Latency taxonomy

| Start → end event | Value | Preparation/source | Comparability to Phase 6C |
| --- | ---: | --- | --- |
| GF spike → middle-leg extension | 0.9 ± 0.2 ms | von Reyn et al. 2014; looming-associated GF recording and leg kinematics; 27/27 reported spike-associated trials in 5/5 flies. | Behavioral/body endpoint, not synaptic delay, tau, or TTMn AP latency. |
| GF spike → flight initiation | 2.0 ± 0.1 ms | Same von Reyn assay/context. | Body/behavior endpoint including downstream circuit and mechanics. |
| GF spike → TTM muscle potential | 0.81 ± 0.07 ms | Tanouye & Wyman 1980, values cited by von Reyn; direct GF/muscle physiology. | Muscle-potential endpoint, not TTMn intracellular state. |
| GF spike → DLM muscle potential | 1.25 ± 0.10 ms | Tanouye & Wyman 1980, cited by von Reyn. | DLM/PSI branch endpoint, not TTMn. |
| Brain electrical stimulus → TTM muscle EPSP onset | ~0.93 ms young (5–7 d); ~1.22 ms old (45–50 d) | Augustin 2017; adult females at 25°C; 40 V, 0.03 ms brain stimulus; time from stimulus artifact to muscle EPSP onset. | End-to-end circuit+muscle measurement, not isolated TTMn AP, synapse delay, or tau. |
| Brain electrical stimulus → DLM muscle EPSP onset | ~1.44 ms young; ~1.85 ms old | Same Augustin preparation. | Disynaptic PSI/DLM branch, not TTMn. |
| Thoracic motoneuron-region stimulus → TTM/DLM muscle response | ~0.65 ms | Augustin 2017/2019; electrode moved to thorax to directly stimulate motor-neuron pathway; muscle recorded. | Motor excitation/AP plus NMJ-to-muscle endpoint, not pure NMJ delay. |
| Model GF current injection → TTMn AP peak | Simulated output | Augustin 2019; 120 nA, 0.03 ms proximal GF pulse. | Model output; paper adds estimated 0.35 ms to compare with muscle. |
| Phase 6C DNp01 event → x update | Same stored step; no added delay | NeuroFly stored-grid semantics. | Declared model convention; no AP or muscle observation operator. |

Augustin's brain-stimulus values end at muscle EPSP onset. The von Reyn
values start at a GF spike but end at body kinematics. Neither can be
substituted for tau_motor_ms or an unobserved GF→TTMn delay. A Phase 6C
hidden-state peak time is not TTMn AP or leg-extension latency.

## 6. TTMn-specific physiology search

No directly applicable adult TTMn intracellular parameter measurement was
identified in the reviewed primary-source set. Circuit studies primarily
measure GF activity and/or output-muscle potentials; Augustin's TTMn voltage
trace is simulated. Larval identified motor neurons and adult MN5 are
different-cell priors.

| Quantity | Finding | Available instead |
| --- | --- | --- |
| Resting membrane potential | NOT FOUND as direct adult TTMn measurement | −65 mV is model initialization; model leak reversal is −85 mV. Neither is measured TTMn resting potential. |
| Input resistance | NOT FOUND | Simplified Augustin geometry and estimated passive parameters. |
| Membrane capacitance | NOT FOUND | Augustin assumes 1 µF/cm² specific capacitance. |
| Membrane time constant | NOT FOUND | No adult TTMn tau mapping to tau_motor_ms found. |
| Spike threshold / AP waveform | NOT FOUND as direct intracellular TTMn measurement in this source set | Some circuit experiments infer motor-neuron events from muscle responses; Augustin APs are simulated. |
| Current–frequency / refractory behavior | NOT FOUND as direct intrinsic TTMn curves | Circuit muscle-following and refractory measurements combine GF, junction, motor axon, NMJ and muscle. |
| Postsynaptic TTMn voltage after GF spike | NOT FOUND as intracellular paired recording | GF-triggered muscle potential constrains the output endpoint, not TTMn voltage trajectory. |
| Pair-specific GF↔TTMn coupling coefficient/conductance | NOT FOUND as direct numeric measure applicable to MaleCNS identities | Shaking-B dependence, dye coupling, ultrastructure, latencies and model estimates provide mechanistic evidence only. |

This is a bounded negative result, not proof that unpublished, archived, or
differently indexed recordings do not exist. Such data would need source and
identity validation before being used for parameterization.

## 7. Reliability, age, and asymmetry

The deterministic one-event→state update omits biological response failures,
heterogeneous latency, refractoriness, and trial variability. These matter
for a future physiological model but do not justify adding randomness here.
Classic experiments report high-frequency following up to 300 Hz for TTM
output; Shaking-B disruption and chemical-transmission perturbations reveal
delayed responses and impaired repetitive reliability. These are system
output/following findings, not intrinsic TTMn refractory or membrane
parameters.

Augustin 2017 reports age-associated latency increases under its adult
female, 25°C assay and traces relevant effects upstream of motor-neuron/NMJ
output. Augustin 2019 represents young/old differences with fitted gap
conductances. This may benchmark a faithful reproduction of that assay, but
does not establish generic TTMn tau or MaleCNS-specific parameters.

No reviewed source establishes left/right physiological GF→TTMn coupling
asymmetry corresponding to MaleCNS's unequal chemical structural counts.
Future electrical models must not set left/right gap conductance from 70/20.

## 8. Identifiability of Phase 6C parameters

| Parameter | Mathematical role | Biological analogue found? | Identifiability against current evidence |
| --- | --- | --- | --- |
| tau_motor_ms = 10 | Exponential decay constant for dimensionless latent state x. | No. Not TTMn membrane tau, AP latency, synaptic delay, conduction time, or muscle response time. | NOT_IDENTIFIABLE biologically. No measured observation maps to x; end-to-end latency cannot isolate this decay. It remains controllable in software and sensitivity can be characterized. |
| event_gain = 0.25 | Dimensionless increment per same-step DNp01 event. | No measured quantity corresponds to a unit of x. | NOT_IDENTIFIABLE biologically. The one-event peak equals gain by construction, not from an independent observation. It is a scale parameter without an observation operator. |

Available observations do not independently constrain Phase 6C timing and
amplitude. There is no transfer function from x to TTMn voltage, muscle
potential, muscle force, or behavior. The model is causal/qualitative and
reproducible, not quantitatively calibratable. Fitting either parameter to a
non-equivalent latency or muscle amplitude would manufacture an observation
mapping.

## 9. Parameter provenance and future-use decisions

The evidence classes are kept distinct:
DIRECT_MEASUREMENT, DERIVED_MEASUREMENT, LITERATURE_PRIOR, MODEL_FIT,
MANUAL_ADJUSTMENT, ASSUMPTION, and UNKNOWN.

| Candidate quantity | Candidate value | Provenance class | Decision | Rationale |
| --- | ---: | --- | --- | --- |
| Phase 6C tau_motor_ms | 10 ms reference; sensitivity 5/10/20 ms | ASSUMPTION | KEEP_FREE | Retain only as named dimensionless-state decay assumption; no biological interpretation or latency calibration. |
| Phase 6C event_gain | 0.25 reference; sensitivity 0.1/0.25/0.5 | ASSUMPTION | KEEP_FREE | Retain only as dimensionless event scale for causal comparisons. Do not derive from structural weight or physiology. |
| Augustin g_gap, young / old | 135 / 34.5 µS | MODEL_FIT (paper labels estimated) | DO_NOT_USE for NeuroFly pair parameter | Reproduce only inside faithful benchmark of that model/preparation; not direct or MaleCNS pair-specific coupling. |
| GF→TTMn chemical weight / efficacy | No physiological scalar established | UNKNOWN | DO_NOT_USE | MaleCNS structural weight 70/20 is not efficacy; mixed connection cannot be collapsed to that count. |
| Adult TTMn passive R, C, tau, rest | No applicable values found | UNKNOWN | UNRESOLVED | Requires TTMn-specific adult measurements or a validated source. |
| TTMn AP threshold/reset/refractory | No applicable parameter set found | UNKNOWN | UNRESOLVED | Generic motor-neuron priors do not establish adult TTMn values. |
| Günay aCC channel values/kinetics | Larval aCC model values | LITERATURE_PRIOR | PRIOR_WITH_SENSITIVITY only in clearly different-cell exploratory model | Not adult TTMn; cell/development transfer assumptions must remain explicit. |
| Augustin 2019 morphology dimensions | Simplified literature-derived lengths/diameters | LITERATURE_PRIOR | PRIOR_WITH_SENSITIVITY in faithful replication | Not derived from current MaleCNS raw TTMn skeleton. |
| Augustin 0.35 ms NMJ term | ~0.65 ms thoracic→muscle minus ~0.30 ms simulated motor stimulation→AP peak | DERIVED_MEASUREMENT / model estimate | DO_NOT_USE as GF→TTMn delay | Composite model-dependent correction, not isolated direct NMJ measurement. |
| Measured brain→muscle / GF spike→kinematics latencies | Values in Section 5 | DIRECT_MEASUREMENT of stated endpoint | DO_NOT_USE as tau/gain; PIN_FROM_EVIDENCE only for identical assay/output | Valid benchmarks only when start/end, age, preparation and method match. |

The 2019 paper says some values were manually adjusted to obtain spiking and
latency matches but does not identify every adjusted value in that sentence.
No specific unlisted parameter is assigned MANUAL_ADJUSTMENT without
evidence. Explicitly estimated values remain MODEL_FIT or ASSUMPTION as
classified above.

## 10. Model alternatives

### A. Retain EXPLORATORY_EVENT_INTEGRATOR — recommended

**Strengths:** minimal, explicit, deterministic; receives exact upstream
events; demonstrates downstream causal wiring; supports intervention and
sensitivity comparisons without pretending to know electrical conductance.

**Valid outputs:** dimensionless exploratory state, event-to-target mapping,
decay/increment behavior under stated assumptions, and comparisons between
simulated controls under the same assumptions.

**Invalid interpretations:** TTMn voltage, biological TTMn spike, electrical
coupling, response probability, muscle amplitude, physiological response
threshold, GF→TTMn latency, motor output, jump/takeoff, or escape.

**Validation opportunity:** code-level causality, identity, determinism,
control behavior, and sensitivity. These do not upgrade empirical validation.

### B. Parameterize a minimal TTMn point-neuron model — not supported yet

A point model needs TTMn-relevant resting potential, input
resistance/capacitance or leak, threshold and spike/reset/refractory dynamics,
plus an input representation for a GF event. Because GF→TTMn is mixed, it
also needs separately specified electrical coupling (and a presynaptic GF
waveform or equivalent) and, if included, chemical conductance, reversal and
kinetics. A point model would hide synaptic location and cable load, which
the Augustin model found important.

Direct adult TTMn coverage for these parameters is absent in the reviewed
source set. Generic larval aCC or other adult motor-neuron parameters would
be priors only, with substantial transfer assumptions. A response threshold
would remain unconstrained. Without an equivalent TTMn AP measurement, a
point model may be more interpretable mathematically while remaining
quantitatively unidentifiable. Do not implement it until an equivalent output
target and parameter provenance exist.

### C. Reproduce/adapt the conductance-based GF→TTMn model — not the next production step

The Augustin code and paper provide a benchmarkable model with segmented
cable equations, active channels, electrical coupling, and TTMn AP-peak
output compared—after explicit NMJ correction—to brain-stimulus→muscle
response. The published code is small but uses NEURON and compiled channel
mechanisms; no installation or independent reproduction was performed.

It has stronger observability than Phase 6C but depends on simplified
literature geometry and fitted/estimated shared gap conductances. MaleCNS
chemical structural data do not supply electrical coupling. Importing MaleCNS
skeleton coordinates does not solve missing membrane/coupling parameters and
may mismatch the original model geometry. A careful reproduction could be a
separate benchmark later, not evidence its fitted conductance is a
MaleCNS-specific parameter.

## 11. Morphology opportunity and limits

The local real morphology artifact contains the fixed six Phase 5G bodies,
not TTMn 800146 or 804642. No TTMn SWC is present in the ignored local
morphology data inspected. The existing official bulk SWC source convention
addresses one body per bodyId.swc URL. HEAD-only checks on 2026-09-24 against
the official MaleCNS v1.0 objects returned HTTP 200: [800146.swc](https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/800146.swc)
reports 54,365 bytes and [804642.swc](https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/804642.swc)
40,837 bytes. No response body was downloaded, so no content SHA-256 or
skeleton identity validation was performed. The objects are available for a
separately authorized bounded acquisition and subsequent validation; their
presence alone does not establish model parameters.

If acquired and identity-validated, raw TTMn skeletons could constrain
reconstructed length, branching/topology, compartment discretization, and
geometric cable-path assumptions. They cannot provide membrane capacitance,
intracellular resistivity, channel distributions, resting potential,
threshold, electrical coupling, synaptic conductance, or model response. A
skeleton is an anatomical constraint, not an electrical parameter set.

## 12. Decision and Phase 6E gate

### Selected option

**A — RETAIN_PHASE6C_EXPLORATORY_INTEGRATOR.** Keep the existing model as a
reproducible dimensionless causal extension. Keep tau_motor_ms and
event_gain explicit and sensitivity-tested; do not tune them to unrelated
latency or amplitude data. The current real looming→DNp01→TTMn chain remains
**NOT EMPIRICALLY VALIDATED**.

### Smallest Phase 6E gate

Before parameterizing or replacing Phase 6C, establish an equivalent,
identity-resolved TTMn observation target and observation operator. The
smallest useful target is an adult GF-evoked TTMn AP or postsynaptic TTMn
voltage response with source, exact input timing and preparation metadata. If
no such primary data can be obtained, retain the integrator and explicitly
stop quantitative calibration. A faithful, separate Augustin model
reproduction may be considered as a software benchmark with its own source
identity and fit/assumption provenance, never conflated with the
MaleCNS-specific model.

Pass criterion: either (1) direct, equivalent, source-traceable TTMn
measurement plus sufficient parameters supports an explicitly bounded model
comparison, or (2) the absence is documented and the dimensionless state is
kept uncalibrated. No behavior gate or body adapter.

### PSI/DLMn ordering

Adding PSI/DLMn now introduces another mixed electrical GF→PSI interface,
chemical PSI→DLMn interface, identities, and assumptions without resolving
the unobservability of the TTMn state. Prefer an equivalent TTMn
observation/benchmark gate before expanding that branch. If the later goal is
the full short-mode motor-pathway core, PSI/DLMn can be added as a separately
versioned branch. TTMn-only output is not a complete takeoff model.

## 13. Validation status and limitations

After Phase 6D NeuroFly may claim that Phase 6C is a reproducible,
connectome-identity-mapped deterministic exploratory downstream state whose
causal wiring and sensitivity are tested. It may not claim that TTMn
membrane physiology, GF→TTMn conductance, motor-neuron AP latency, muscle
response, jump, takeoff, or escape behavior is quantitatively validated.
The looming→DNp01→TTMn system remains **NOT EMPIRICALLY VALIDATED**.

Remaining limits:

- no adult TTMn direct membrane-property set or response recording in the reviewed project source set;
- no MaleCNS v1.0 pair-specific electrical conductance/coupling coefficient;
- no physiological meaning or observation operator for dimensionless x;
- no source-matched model of the complete mixed GF→TTMn connection;
- the deterministic integrator omits reliability, failures, trial variation, refractoriness and high-frequency response dynamics;
- no experimentally constrained TTMn response criterion;
- no TTMn morphology in the fixed local six-body artifact;
- no PSI/DLMn output, muscle model, or body mechanics.

## 14. Data acquisition and reproducibility record

External primary sources and linked ModelDB code were inspected through their
public web pages. **No external files were downloaded:** no PDFs, ModelDB
archive, code, MaleCNS data, or TTMn skeletons. No file size/hash applies;
no external data were added to ignored storage or committed. ModelDB lists
the archive as 4.3 kB, but it was not retrieved. The published model was not
run because this was an evidence audit and NEURON was not installed.

Phase 6C artifact identities and sensitivity results remain those recorded
in [motor_pathway_model.md](motor_pathway_model.md); no new run was generated.
The reference set remains deterministic under its recorded upstream config,
evidence-contract hash, motor config, and source DNp01 events.
