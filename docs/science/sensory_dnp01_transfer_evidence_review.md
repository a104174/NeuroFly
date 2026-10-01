# Phase 19 — sensory→DNp01 transfer evidence and contract review

## Scope and decision

Evidence/contract audit only. No model, scenario, frontend, historical artifact,
gain, normalization or threshold changed. No new coefficient sweep or
required-gain calculation was performed.

Decision: `CURRENT_TRANSFER_CONTRACT_RETAIN_AS_EXPLORATORY_UNCALIBRATED_MODEL`.
This retains an internally coherent exploratory contract, not biologically
validated efficacy. The numerical coefficient is not identified by current
evidence; the positive pathway effect is qualitatively supported.

| Question | Classification |
| --- | --- |
| Magnitude | `QUALITATIVELY_CONSTRAINED_BUT_NOT_NUMERICALLY_IDENTIFIABLE` |
| Current normalization | `CURRENT_NORMALIZATION_ACCEPTABLE_EXPLORATORY_ASSUMPTION` |
| Equal LC4/LPLC2 conversion | `EQUAL_TRANSFER_MAGNITUDE_ACCEPTABLE_SIMPLIFICATION` |
| Equality provenance | `MODEL_SIMPLIFICATION` |

These are different questions: qualitative excitatory pathway evidence does
not constrain an absolute coefficient or demonstrate equal per-body efficacy.

## Repository and historical source gate

Audit started clean on `main == origin/main`, commit
`090f462a8d4f7e7c28f5de3a3ea14c964e1cc295` (Phase 18).
Required Phase 17, corrected 16, 15 and 13B commits are present. Offline replay
passed for these immutable sources:

| Source | Artifact ID |
| --- | --- |
| Phase 18 world | `ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c` |
| Corrected Phase 16 | `bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b` |
| Phase 13B | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` |
| Full numerical Phase 7O | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` |
| Genuine Phase 8C | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` |

Phase 7O still has 35 conditions with zero DNp01 events. Phase 8C still has
zero motor inputs/state. These are regression observations, not model-selection
targets. Existing Baseline, micro-window and world results remain unchanged.

## Exact current contract: sensory_dnp01_transfer_contract_current_v1

Authority is `route_population_drive` in
`src/neurofly/relative_column_dnp01_transfer.py`, called by Phase 7O,
Phase 13B's causal runner and Phase 16's contribution decomposition. Phase 18
reuses that runner. Source callers validate the pinned identities/routes;
the primitive validates masks, target membership, finite nonnegative states
and coefficient, positive integer count metadata, and duplicate source-target
pairs. It does not independently infer anatomical routing from side strings.

For target `j`, population `p`, valid routed source `i`, and source mask `a_i`:

```text
x_i[n+1] = alpha*x_i[n] + gain*e_i[n]*(1-alpha)
alpha = exp(-dt_ms/tau_sens_ms)
d_i[n] = a_i*k*x_i[n]
D_j,p[n] = sum(d_i[n] for i routed to j with type p)
D_j[n] = sum(d_i[n] for i routed to j)
```

The production primitive performs one source-body-ordered sum, not separate
type-normalized sums. Its ledger makes the LC4/LPLC2 decomposition additive.
`k = 1.0 mV_eq/state` is shared by every body, type and side. There is no
per-body/type/side coefficient, population mean, count denominator, structural
weight multiplier, synaptic release probability or inferred sign from counts.
Current exposure uses record-based `column_overlap_fraction` (dimensionless
fraction), not the alternate input-site-weighted exposure metric.

All 311 identities remain explicit: 126 LC4 and 185 LPLC2, with 146 routes to
10001/R and 165 to 10010/L. The route contract preserves ipsilateral identity.
A right-side stimulus changes right-side exposure; absent left exposure and
zero initial state keep left drive zero. Equal conversion does not make the
two sides' populations or trajectories equal.

Boundary `x[n]` drives DNp01 during interval `n→n+1`; exposure `e[n]` produces
`x[n+1]`. First membrane effect of exposure is boundary `n+2`. DNp01 consumes
the sum as a held external-drive coordinate, not a delivered presynaptic spike.
The separate readout graph has zero event edges and zero filtered synaptic
state. Its required `k_syn_mv_per_contact` field is dormant in this path and
is not `k_transfer`. The LIF kernel adds `D[n]*(1-exp(-dt/tau_m))` to the
leaked membrane coordinate. A contribution is therefore not an instantaneous
EPSP of size `k*x`.

## Dimensions and assumptions

| Quantity | Implemented/model dimension | Scientific status |
| --- | --- | --- |
| Exposure `e_i` | dimensionless record-overlap fraction [0,1] | anatomical exposure abstraction, not physiological sensitivity |
| Sensory state `x_i` | dimensionless hidden state | exploratory dynamics; tau=1 ms, gain=1, initial=0 are assumptions |
| Shared `k` | mV_eq per dimensionless state | uncalibrated conversion assumption |
| Individual/aggregate `d_i`, `D_j` | mV_eq external model drive | not current, conductance, release or observed EPSP |
| DNp01 membrane | mV_eq | uncalibrated coordinate, not biological millivolts |
| `dt`, model taus | ms in simulation timing | not direct measurements of these populations |

Variable names inherited from the general LIF code sometimes use `mv`; this
does not convert the present exploratory coordinate into measured biological mV.
No observation operator connects `x_i` to firing, voltage, calcium or release,
or connects the external-drive coordinate to a source-matched GF recording.

## Git provenance

Phase 7E commit `5ae7529` introduced dimensionless individual states with
shared tau/gain assumptions, not inherited DNp01 dynamics.
Phase 7F commit `8e1775b9af1d96b0a1cc60202621c3a721b36b68` introduced
`k=1`, the four-body additive loop and explicit documentation of a shared,
unnormalized sum. The contemporaneous rationale is a simple, numerically safe
software reference, not fitting to biology or earlier angular spike times.
There is no recorded basis to claim it was selected to force or avoid spikes.
This is a deliberately documented rule, not an accidental missing denominator.

Phase 7G `4f91b83` retained the shared coefficient to avoid false precision in
unsupported per-edge or per-type values. Phase 7H `3a820eb` generalized the
same loop into `route_population_drive`, preserving the four-body authority.
Phase 7O `e84fa63` executed all 311 identities under that inherited contract;
13B and 18 pin it unchanged. Inheritance explains continuity, not calibration.

## Population size, equality and alternative semantics

For equal source states `x` and `N_j` active routed identities, `D_j=k*N_j*x`.
In general both identity cardinality and state magnitudes affect drive. A body
counts through its state, not merely through a binary exposed/unexposed flag.
Current LC4 and LPLC2 have identical conversion and aggregation semantics;
unequal observed totals arise from populations, exposure and state trajectories.
Neither anatomy nor functional importance establishes equal biological efficacy.

| Thought experiment (not executed) | Meaning and identity accounting | Population-size implication / evidence |
| --- | --- | --- |
| Unnormalized additive sum (current) | each routed body contributes `k*x_i`; exact ledger | grows with summed state; coherent explicit model assumption, not established physiology |
| Population-normalized mean | divide summed contributions by a declared population denominator | denominator must distinguish all routed vs currently active bodies; neither choice is established here |
| Type-normalized sum | add separately normalized LC4/LPLC2 totals | prevents type cardinality scaling but assumes type balancing; identity ledger still possible |
| Explicit per-body efficacy | sum `k_i*x_i` | preserves identity; requires unsupported per-body physiological parameters |
| Repository angular-feature model | sums different feature encodings | different source variables/path; not an interchangeable 311-state normalization |

No replacement is selected or numerically evaluated. Current normalization
is acceptable for explicitly uncalibrated exploration, not uniquely justified
biology. Equal conversion is a simplification, not evidence of equal synapses.

## Existing sensitivity and numerical context

Phase 7F declared `k={0,0.5,1,2,4}` in its original config/code, with masks and
zero controls. Drive and subthreshold response scaled, while its fixed runs
had no spikes. The repository documents a fixed non-optimized grid, but does
not establish a separate pre-execution content-addressed preregistration for it.
Phase 7O also retains a diagnostic `k=2` condition. Neither supplies calibration.

Phase 7G additionally recorded an output-targeting stress search for model
threshold locations. It was not physiological evidence, a preferred coefficient,
or a valid basis for this review. It was not repeated; crossing gains are not
reported here. No new sensitivity/required-gain computation occurred.

Corrected Phase 16: R peak `-51.933657842035174 mV_eq`, rest displacement
`0.06634215796482579 mV_eq`, with `k=1` and zero spikes.
Phase 18: R peak `-48.733429620244685 mV_eq`, L `-52`, zero spikes and
downstream movement. These characterize coupled model dynamics; they do not
identify transfer efficacy or choose a new gain.

## Bounded primary/official evidence review

Reviewed the existing Phase 7G evidence gate, neural-model selection, empirical
constraint protocol and Phase 17 temporal review. Reverified primary papers and
official graph semantics on 2026-10-01. Search scope: LC4/LPLC2→GF/DNp01
whole-cell voltage, paired/unitary EPSP, current/conductance and controlled
presynaptic activation. Unrelated auditory GF physiology, secondary reviews and
other simulators were excluded as transfer-calibration evidence.

| Source / category | Preparation, population and target | Measurement, timing and result | Applicability / limitation |
| --- | --- | --- | --- |
| [Ache 2019, DOI 10.1016/j.cub.2019.01.079](https://pubmed.ncbi.nlm.nih.gov/30827912/); physiology, manipulation, anatomy, behavior | D. melanogaster; GF current clamp in tethered 3–5-day females; LC4/LPLC2 silencing; adult female EM, not MaleCNS identities | looming disks 10°→90°, r/v 10–80 ms; GF voltage in biological mV, sampled 20 kHz; separates velocity/size components and supports excitatory contributions; Fig. 3 groups N=5/7/6 | direct population-associated postsynaptic voltage, not controlled single-body transfer; silencing/inhibitory/context effects prevent unitary interpretation |
| [Klapoetke 2017, DOI 10.1038/nature24626](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457385/); optogenetic GF physiology | D. melanogaster; tethered 3–5-day females, femur-cut/glued legs; population LPLC2 activation, GF soma whole-cell current clamp | 595 nm, 50 ms pulses every 30 s; 40 kHz recording; Fig. 1c N=4/group, rapid depolarization in biological mV | supports excitatory functional connection; no calibrated number/state of activated source bodies or unitary conductance |
| Same paper; calcium imaging | 2–5-day females, LPLC2 axons/terminals; visual expansion/radial-motion assays | fluorescence ΔF/F or peak-normalized ΔF; peak averaged over 300 ms around maximum; looming selectivity | upstream feature evidence, not a GF voltage or transfer coefficient |
| [von Reyn 2017, DOI 10.1016/j.neuron.2017.05.036](https://www.sciencedirect.com/science/article/pii/S0896627317304749); functional/electrophysiological | D. melanogaster LC4→GF, in-vivo recordings with genetic removal of LC4 input | GF looming response/feature integration and behavior; angular velocity contribution; source abstract does not specify assay sex/age/timing window | matches pathway/type, not MaleCNS bodies or `x_i`; those protocol details are not claimed from the abstract |
| [neuPrint graph specification](https://github.com/connectome-neuprint/neuPrint/blob/master/pgmspecs.md); structural | EM reconstruction schema, not physiological preparation | `ConnectsTo.weight` counts postsynaptic densities per connection; no timing/electrophysiological units | topology/count provenance only; not conductance or efficacy |
| [MaleCNS official download](https://male-cns.janelia.org/download/); structural | male D. melanogaster CNS reconstructed segments/synapse partners | confidence-filtered counts/locations and segment connections, no physiological timing | current pinned body/topology source; filtering/reconstruction limits, not functional calibration |

Ache full text was checked in the [author-uploaded primary manuscript](https://www.researchgate.net/publication/331408732_Neural_Basis_for_Looming_Size_and_Velocity_Encoding_in_the_Drosophila_Giant_Fiber_Escape_Pathway).
Its fitted component weights (1.45 LPLC2, 1.62 LC4; a separate combination
analysis uses 1.1/1.5) scale feature/isolated population components, not `x_i`.
They cannot establish NeuroFly per-body relative or absolute efficacy.
Reported supralinearity also does not identify whether interaction is within
GF, presynaptic, or affected by silencing. Distinct feature roles are not proof
of distinct per-unit transfer coefficients for our artificial state variable.

Behavioral silencing effects support pathway involvement, not magnitude.
Direct GF voltage evidence **is located**; identified single-source paired
LC4/LPLC2→GF unitary voltage/current/conductance mapped to this contract is
`NOT_LOCATED` in the bounded search. This is not proof of universal absence.

## Structural evidence and identifiability

MaleCNS establishes pinned body/type/side, connection existence/direction,
contact counts and column topology. It does not supply physiological efficacy,
normalization, shared conversion, LIF parameters or world projection. Positive
pathway sign is supported functionally, not inferred from a positive count.
Count metadata never enters the current numerical contribution. Existing tests
change structural counts without changing output, reject invalid routes/sides,
and check masks and additive contributions; full Phase 7O replay also checks
count independence. No implementation/contract bug was found.

Neither point nor range identifiability holds for `k` on the present scale:
one must first establish compatible observations of source `x_i`, target drive
and membrane, assay conditions and aggregation. Biological voltage alone is
not that mapping. Rescaling an arbitrary source-state scale can be offset by
the reciprocal conversion; responses also depend on exposure and LIF dynamics.
These are coupled assumptions, not independent causal/statistical factors.
Qualitative excitation is constrained; no numeric interval or relative LC4/LPLC2
efficacy is identified. Existing zero-spike results remain legitimate model
outcomes, not evidence that transfer is biologically weak/wrong.

## Claims and next bounded action

Allowed: deterministic identity-resolved, ipsilateral additive exploratory
drive; explicit shared uncalibrated conversion; quantitatively inspectable
model contributions. Forbidden: calibrated EPSPs/current/conductance, counts
as efficacy, equal biological synaptic strength, measured lack of escape,
or a scientifically recommended spike-producing gain.

Exactly one next action: define a source/target observation-operator and assay
compatibility specification for LC4/LPLC2-associated GF physiology, documenting
which measured quantities could constrain this contract and which remain
unidentified. Do not fit a gain or revise the model in that specification.

The adjacent JSON is a content-addressed **evidence review**, not a new
simulation artifact. Its `review_id` is the repository canonical SHA-256 of
the `review` object; semantic changes invalidate it. Historical artifacts and
Phase 18 preregistration remain untouched.

Review identity: `f7d278372f3527393bb041e4db3b45126668a5ec904ce65cb1f9f3546b28d267`.

## Verification

Phase 19 `PASS`. Full Python suite: 1,018 passed, 1 existing deselection,
2 dependency deprecation warnings (566.34 s). Focused transfer suite: 13 passed.
Evidence-review canonical identity matched; equation, normalization and
provenance mutation probes each changed the hash. Frontend regression suite:
53 passed; lint/typecheck/build passed. Ruff/check-format and `git diff --check`
passed. No commit or push; only these review files and minimal Project Context
changes are intended. No new generated simulation data.
