# Phase 8T — TTM G1 electrical observation-model feasibility

**Assessment:** `PASS` (documentation only). The audit began on clean `main`
at `b2b41104c27cd174d7fac4fdee62636854991fb5`, equal to `origin/main`.
Offline replay passed for the Phase 8S observation artifact
`5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f`
(nine records), Phase 8Q receipt artifact
`e04803f60304f58d0e6d27fdea5d15debb60358b46721caac09f10165c6df9c4`
(eight receipts), and Phase 8K target contract
`5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0`
(12 associations). Phase 8S records and all model artifacts are unchanged.

## Current boundary and evidence

Phase 8N produces `motor_neuron_output_event_v1` from the uncalibrated
dimensionless Phase 6C TTMn state. Phase 8O resolves its TTM target association.
Phase 8Q then copies the dispatch boundary into a
`ttm_neuromuscular_input_receipt_v1` with provenance
`EXPLORATORY_NEUROMUSCULAR_INPUT`. A receipt records a software handoff; it
contains no successful release, input current or conductance, muscle voltage,
or response onset. Its timestamp is bookkeeping, not a measured NMJ delay.
The upstream Phase 8N event itself is an exploratory model-derived event under
synthetic DNp01 fixtures, not a calibrated TTMn action potential. See the
[Phase 8Q boundary](ttm_neuromuscular_input_receipt.md) and
[Phase 8P assessment](ttmn_ttm_neuromuscular_readiness.md).

The independent [Phase 8S contract](ttm_g1_electrophysiology_observation_contract.md)
pins nine published records with source and protocol metadata. Its source
scope is [Koenig & Ikeda 2007](https://doi.org/10.1152/jn.01258.2006)
(publisher-indexed primary Methods/Results audited in Phase 8R),
[Koenig & Ikeda 2005](https://doi.org/10.1152/jn.00323.2005)
(primary abstract only for this contract), and
[Kadas, Duch & Consoulas 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6709211/)
(open Methods, Figure 1, Table 1). G1 is one recorded TTM fiber, with no
crosswalk to MaleCNS body `800146` or `804642`; Kadas records a TTM muscle
potential, not an intracellular G1 trace. The [Phase 8R audit](ttm_g1_electrophysiology_observation_readiness.md)
and the pinned Phase 8S contract remain the source of record for these facts.

An observation model would take a specified model trajectory or event ledger,
apply a versioned measurement operation under a matched protocol, and yield a
quantity with the published meaning and units. A model state, model event,
observation operator, published observation, and possible future calibration
objective are five distinct objects. Phase 8T defines none of the operators
numerically and creates no calibration objective. Phase 2G's
[empirical protocol](empirical_constraint_protocol.md) is useful precedent:
declare modality, source time reference, normalization, availability, role,
and transform separately; never choose a free alignment or scale after seeing
the result.

## Observation-by-observation feasibility

`MODEL_OBSERVABLE_WITH_OPERATOR` below means a **future** model could expose
the required output after its operator and protocol are specified. Every Phase
8S record still has `OBSERVATION_MODEL_REQUIRED` and no current NeuroFly
observable. `VALIDATION_ONLY` means a possible held-out scientific role, not a
ready pass/fail target or an acceptance window.

| Phase 8S observation ID; published quantity/classification | Required future output and conceptual operator | Protocol to match | Feasibility and role; missing semantics |
| --- | --- | --- | --- |
| `ttm-g1-obs-21076e7816c87359e80f`; G1 resting voltage ~−95 mV, `DESCRIPTIVE_MEASURED_VALUE` | G1 voltage in mV; `PRE_STIMULUS_BASELINE` or equilibrated resting sample. | G1 intracellular site and preparation; source does not attach a value-specific genotype, test temperature, equilibration interval, n, or dispersion. | `MODEL_OBSERVABLE_WITH_OPERATOR`, but currently `CONTEXT_ONLY`. A future qualitative baseline check is plausible; a numeric validation window or fixed `V_rest` is unsupported. |
| `ttm-g1-obs-0e8110027289e2606870`; 45 mV G1 evoked potential, `PRIOR_PRIMARY_RESULT_REUSED` | Stimulus-aligned G1 voltage trace and baseline; candidate `PEAK_EVOKED_DEFLECTION`. Do not substitute peak absolute voltage. | Threshold-level response and 4 mM Na-L-glutamate context reported in 2007; full 2005 source protocol, response window, and exact amplitude convention are not pinned. | `UNRESOLVED` as an executable comparison; future `VALIDATION_ONLY` after source clarification. The 45 mV is neither a new 2007 measurement nor a fixed model input/gain. |
| `ttm-g1-obs-00171dce33f34d595a05`; ~0.5 mV G1 miniature potential, `DESCRIPTIVE_MEASURED_VALUE` | Spontaneous single-quantal electrical events and `MINIATURE_EVENT_AMPLITUDE` detector/summary. | `shi`, 19 °C, G1 intracellular histogram context; event selection and recording details must match. | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE` to a first evoked-only electrical model. A DNp01 or Phase 8Q receipt is not one quantum. |
| `ttm-g1-obs-87c7df503a4c6d752ea0`; −10 mV correction equilibrium input, `ANALYSIS_INPUT_FROM_PRIOR_SOURCE` | None for direct validation; `CONTEXT_ONLY` analysis input. | Ikeda 1980 value as attributed by the 2007 Martin correction; prior preparation and applicability need independent verification. | `CONTEXT_ONLY`. It cannot be copied into a conductance model as `E_syn` without source, preparation, and mechanism evidence. |
| `ttm-g1-obs-cade4bdd5192612a0423`; ~191 corrected quanta, `DERIVED_QUANTITY` | Explicit release/quantal output plus source-matched counting, or a justified voltage-to-quantal Martin correction using matched inputs. | Single stimulus with no prior activity; 45 mV, ~0.5 mV, −10 mV and G1 correction assumptions. | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE` to a voltage-only model. Neither receipt count nor synaptic-event count equals quantal content. |
| `ttm-g1-obs-399d70f32a656dea7a85`; 7 ± 3 spontaneous events/s, `SUMMARY_STATISTIC` with unknown uncertainty kind | Spontaneous release/miniature generator and `SPONTANEOUS_EVENT_RATE` detector over a declared observation interval. | Wild-type G1, 19 °C, five flies, no evoked train; detection and sampling duration need definition. | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE` to deterministic evoked-only dynamics. The ±3 cannot be interpreted as SEM or SD. |
| `ttm-g1-obs-745604f564d9f4c315d4`; no observed depression, `CATEGORICAL_OBSERVATION` | Per-stimulus response series and a source-matched `REPEATED_RESPONSE_OUTCOME` rule. | `shi` G1, 19 °C, recycling permitted, 1 Hz, 1,500 stimuli; distinguish 29 °C recycling block. | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE` without response-history semantics and an operational depression criterion. Do not encode a gain of 1. |
| `ttm-g1-obs-61e331f15399e1627634`; 0.24 vesicle/active-zone/s, `DERIVED_QUANTITY` | Vesicle/release-pool state, active-zone denominator, recycling comparison, and `DERIVED_RECYCLING_RATE`. | Same 1-Hz `shi` comparison; 19 °C recycling permitted versus blocked condition, 1,500 s, ~720 G1 active zones. | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE` to membrane-only dynamics. It is not recovery `tau`. |
| `ttm-g1-obs-24852cd49c1395db8e8c`; 0.84 ± 0.02 ms, mean ± SEM, n=8, `SUMMARY_STATISTIC` | Motor-neuron-region stimulation event, axonal conduction, NMJ and muscle response, plus `INITIAL_TTM_POTENTIAL_ONSET` detector. | Kadas 24 h post-eclosion control, both sexes; thoracic tungsten stimulus and TTM potential recording. Test temperature and onset detection rule are not pinned. | `SYSTEM_BOUNDARY_MISMATCH`; `NOT_COMPARABLE` to receipt-to-muscle onset. The latter would start after the motor-neuron-region stimulus and omit axonal conduction; no arbitrary onset threshold or subtraction is justified. |

The smallest bounded operator vocabulary for the nine records is
`PRE_STIMULUS_BASELINE`, `PEAK_EVOKED_DEFLECTION`,
`MINIATURE_EVENT_AMPLITUDE`, `SPONTANEOUS_EVENT_RATE`,
`REPEATED_RESPONSE_OUTCOME`, `DERIVED_QUANTAL_CONTENT`,
`DERIVED_RECYCLING_RATE`, `INITIAL_TTM_POTENTIAL_ONSET`, and `CONTEXT_ONLY`.
These are candidate mapping names, not implemented operators. The last
latency operator would require the wider Kadas stimulation-to-recording model
boundary, not merely a G1 membrane state.

## Early validation and protocol matching

A dimensionless TTM activation state has no direct mV comparison. A mapping
from it to G1 voltage would introduce at least a free scale and offset, plus
stimulus/recording assumptions. An explicit `V_G1(t)` state in mV could support
a baseline sample and an evoked peak-deflection operator, but voltage units
alone do not determine membrane, input, or observation parameters.

The ~−95 mV record is a descriptive, approximate context value. A future G1
voltage model could make a qualitative baseline sanity check only after the
pre-stimulus/equilibration procedure is specified. The 45 mV record is a
potentially more informative evoked target, but its full 2005 protocol and
precise amplitude operation are not verified within the Phase 8S source
boundary. Published "synaptic potential" favors a deflection from baseline
over an absolute voltage interpretation, but the operator remains `UNRESOLVED`
until source/protocol details establish the exact comparison. Neither value
is presently a formal numerical validation target. **Early-validation-subset
decision: `NO_VALIDATION_SUBSET_READY`.** A future mapping contract can retain
both as candidates with explicit source-resolution gates.

Protocol matching must preserve four-day-old adult female G1 preparation from
Koenig & Ikeda 2007 separately from the Kadas 24 h post-eclosion control,
which included both sexes and a different recording mode. The `shi` 19 °C,
1-Hz, 1,500-stimulus recycling-permitted train cannot be treated as wild-type
or as the distinct 29 °C blocked-recycling experiment. The spontaneous-rate
record is wild-type at 19 °C. A model comparison needs the matching fiber,
genotype, test temperature (distinct from rearing temperature), age, stimulus
site/pulse/frequency/count, history, recycling condition, recording mode/site,
and time reference. Missing Phase 8S dimensions remain unknown; the mapping
must refuse to treat unknown as a match.

Conceptual partition of the nine records: early G1 voltage candidates are
resting context and the conditional 45 mV evoked result (2); miniature
amplitude, quantal content, and spontaneous rate require quantal/spontaneous
release semantics (3); depression and recycling rate require history/vesicle
semantics (2); Kadas latency requires a wider stimulation-to-recording system
boundary (1); the −10 mV prior analysis input is context only (1). These
groups do not change Phase 8S applicability classifications.

## Input semantics and candidate model families

An input convention is needed between Phase 8Q receipts and any electrical
equation. The alternatives have different assumption burdens:

- **Fixed response:** assume every receipt yields one successful, fixed
  electrical response with fixed amplitude/waveform/timing and no spontaneous
  release or history dependence. It could make an illustrative voltage trace,
  but neither 45 mV nor the receipt establishes that input rule.
- **Fixed conductance event:** additionally choose peak conductance, reversal
  potential, kinetics, delay and muscle membrane properties. Phase 8S does
  not identify these as a coherent parameter set; the −10 mV correction input
  cannot be silently reused as conductance reversal.
- **Release/quantal model:** represent release success/sites, quanta, pool and
  recycling/depression, spontaneous activity, and quantal electrical effect.
  It can in principle address more observations but adds substantially more
  unidentified mechanisms and preparation-specific conditions.
- **Defer electrical input:** keep receipts as handoff records while the
  input-to-electrical-state assumption is specified in a separate, versioned
  contract. This is the chosen next boundary.

| Model family | Illustrative free assumptions/parameters for the stated form | Phase 8S observations potentially addressed / unavailable | Interpretation and readiness |
| --- | --- | --- | --- |
| Phenomenological voltage kernel | At least baseline, response scale, onset lag and waveform width/shape (4+). | Conditional resting/45 mV; cannot predict quanta, spontaneous rate, recycling or Kadas composite latency. | Can visualize a G1-like evoked trace, but a fitted kernel is an output proxy rather than NMJ mechanism. Underconstrained; family selection premature. |
| Passive membrane + event input | At least resting/leak level, effective membrane `tau`, input scale, waveform, and lag (5+); separate `R` and `C` add nonidentifiability. | Conditional resting/45 mV, possibly receipt-to-G1 onset under an independent operator; no miniature, vesicle, depression or Kadas composite prediction. | Biologically inspired exploratory state form; receipt-to-current rule and parameters remain unmeasured. |
| Conductance-based synaptic response | At least capacitance, leak conductance/reversal, synaptic reversal, peak conductance, conductance kinetics and lag (7+). | Conditional resting/45 mV; other release/history records still need added models; Kadas boundary still mismatches. | More mechanistic form, but `g_syn`, driving force and membrane properties are confounded by one amplitude. Current evidence does not parameterize it. |
| Quantal/release-aware model | Conductance/membrane terms plus release sites, probability, quantal response, spontaneous process, pool/depression/recovery and temperature effects (many; >10). | Could eventually address miniature, quantal, spontaneous, depression and recycling records under matched protocols; Kadas still needs axonal/stimulation scope. | Most biological mechanisms, largest unsupported assumption burden. Premature for a first slice. |

These counts describe the candidate forms in the table, not a universal
minimum: a predeclared fixed waveform could reduce the number of adjustable
terms but would add an externally chosen waveform assumption. There are
**zero fully protocol-matched early quantitative validation targets** in Phase 8S;
the resting context is
one approximate descriptor, and the 45 mV prior result has unresolved source
protocol/operator details. Even if both were provisionally used, two scalar
summaries could not identify the four or more free terms of the illustrated
flexible kernel. Baseline, scale and input magnitude can trade off; effective
`R*C` and input time course can produce similar voltage profiles. Phase 8S
contains no numerical G1 waveform, so rise/decay kinetics cannot be inferred.

| Parameter or observation rule | Readiness | Reason |
| --- | --- | --- |
| Resting voltage | `PARTIALLY_CONSTRAINED` | Approximately −95 mV descriptive G1 context, without distribution or value-specific genotype/temperature; possible initial-state assumption only if labelled exploratory, not fixed physiology. |
| Membrane time constant | `NOT_IDENTIFIABLE` | No pinned G1 voltage-decay time series. |
| Membrane resistance / capacitance | `NOT_IDENTIFIABLE` | No independent electrical measurements; `R*C` degeneracy remains. |
| Synaptic input amplitude / conductance | `NOT_IDENTIFIABLE` | A 45 mV response does not isolate release, conductance, membrane resistance or waveform. |
| Synaptic reversal potential | `NOT_IDENTIFIABLE` | −10 mV is a prior correction input, not verified as a parameter for a proposed conductance model. |
| Synaptic waveform / decay `tau` | `NOT_IDENTIFIABLE` | No pinned response waveform or kinetics. |
| Motor-axon/NMJ/response delay | `NOT_IDENTIFIABLE` | Kadas 0.84 ms is composite and begins before Phase 8Q; no isolated transfer delay. |
| Onset-detection rule | `MODEL_ASSUMPTION_REQUIRED` | Kadas reports initial TTM-potential onset, but Phase 8S does not pin a numerical voltage threshold/detector. |
| Saturation or nonlinear summation | `MODEL_ASSUMPTION_REQUIRED` | The Martin correction describes source analysis, not a NeuroFly saturation law. |
| Spontaneous-event process | `NOT_IDENTIFIABLE` | A single 19 °C rate does not identify distribution, temperature law or event waveform. |
| Depression/recovery | `NOT_IDENTIFIABLE` | One categorical 1-Hz outcome and derived rate do not identify a history model or recovery `tau`. |

`MODEL_ASSUMPTION_REQUIRED` describes a design choice, not permission to claim
that a value was measured. The ~−95 mV record could be a future qualitative
sanity check or an explicitly exploratory initial condition; it is not a fixed
parameter. The 45 mV record is a potential validation target after protocol
and operator clarification, not currently a fitting target. Phase 8S
uncertainty values do not define pass/fail tolerances.

## Candidate Phase 8U mapping contract and decisions

A bounded future `ttm_g1_observation_mapping_v1` could reference the pinned
Phase 8S contract and, for each record, declare `observation_id`, required
model quantity and units, candidate operator/version, required protocol fields,
comparison class, intended role, and unresolved requirements. It should
record `BLOCKED_BY_MODEL_OUTPUT`, `BLOCKED_BY_PROTOCOL`, or
`BLOCKED_BY_SYSTEM_BOUNDARY` without inventing an executable transform. A
future comparison result would need model run/config identity, observation
contract/record IDs, operator version, and protocol match status. Phase 8U
should pin that mapping metadata only; it should not execute operators, choose
parameters, or attach Phase 8Q receipts to Phase 8S observations.

- Observation-model decision: `DEFINE_TTM_G1_OBSERVATION_MAPPING_CONTRACT`.
- Early-validation-subset decision: `NO_VALIDATION_SUBSET_READY` for a formal,
  protocol-matched numeric comparison; the resting context remains a
  qualitative candidate.
- Model-family decision: `MODEL_FAMILY_PREMATURE`.
- Parameter-readiness decision: `UNDERDETERMINED_MODEL_ASSUMPTIONS_REQUIRED`.
- Phase 8Q input-semantics decision: `INPUT_SEMANTICS_REQUIRE_SEPARATE_CONTRACT`.

**Scientific boundary:** Phase 8T defines no electrical dynamics or numerical
observation operator. Phase 8Q remains a software handoff, and Phase 8S
remains empirical literature evidence. No current NeuroFly model is validated
against G1 electrophysiology. No fitting, digitization, release model, muscle
activation, force, body mechanics, or DLMn work occurs here.

**Exactly one Phase 8U:** pin and offline-replay the bounded, metadata-only
`ttm_g1_observation_mapping_v1` for the nine Phase 8S records. It should
version candidate operator semantics, protocol requirements, and explicit
blocking conditions without executing a comparison or implementing dynamics.
