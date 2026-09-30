# Phase 9F — isolated G1 evoked-response benchmark readiness

## Outcome and scope

The assessment is complete, but a source-matched empirical benchmark is **not
ready for implementation**. Recover the original 2005 protocol before choosing
stimulus, preparation or experimental measurement rules. Partial primary access
supports an evidence inventory, not invented defaults. No implementation, schema,
artifact, parameter change, unit conversion, fit or numerical comparison is added.
An unsuccessful full-text recovery is a negative readiness finding, not authority
to reconstruct Methods from another paper.

## Repository gate and immutable sources

The initial worktree was clean at committed Phase 9E HEAD
`34fb92f6b5c0e86b4c53a3027e0a60de7abaee98`, matching `origin/main`.
Phase 9D, 9B, 8S and 8U were also committed; initial `git diff --check` passed.
The audit read the Phase 9E operator and source-admission rules, Phase 9D
compatibility document, Phase 8R assessment, canonical Phase 8S evoked record,
Phase 8U blockers, Phase 9B model/fixtures and Project Context.

| Replayed source | Exact artifact ID |
| --- | --- |
| Phase 9E | `2c775d6e00d74b3b3a3ca5a36bb84fd4032959d29f3c7d4c8b0bca934e2942b8` |
| Phase 9B | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` |
| Phase 8S | `5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f` |
| Phase 8U | `f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f` |

All replays passed unchanged. Phase 8U still reports zero formally ready mappings.
The source observation is exactly `ttm-g1-obs-0e8110027289e2606870`; its
`PRIOR_PRIMARY_RESULT_REUSED` classification and unknown protocol fields remain
unchanged. This document is a subsequent assessment, not an observation-contract
revision or a new independent empirical-value store.

## Primary-source access audit

Access was checked during Phase 9F on 2026-09-30. Biological statements below
use only identifiable primary text. Search-index retrieval is explicitly
distinguished from inspecting a complete article. No paper text, PDF, figure
image or digitized value is added to the repository.

| Paper / bibliographic identity | Full text accessible here? | Abstract | Methods | Results | Figures/tables |
| --- | --- | --- | --- | --- | --- |
| Koenig JH, Ikeda K. 2005. *Relationship of the Reserve Vesicle Population to Synaptic Depression in the Tergotrochanteral and Dorsal Longitudinal Muscles of Drosophila*. J Neurophysiol 94:2111–2119. DOI `10.1152/jn.00323.2005` | No authenticated complete text recovered; publisher full/abstract/PDF/DOI-route requests failed | PubMed-indexed primary abstract recovered | Not verified | Original 45 mV passage not recovered; abstract only | Not verified; no figure inspection or extraction |
| Koenig JH, Ikeda K. 2007. *Release and Recycling of the Readily Releasable Vesicle Population in a Synapse Possessing No Reserve Population*. J Neurophysiol 97:4048–4057. DOI `10.1152/jn.01258.2006` | Direct publisher full-page access returned 403/fetch failure; complete-document access not established | PubMed accessible | Publisher-indexed Methods passages recovered | Publisher-indexed relevant Results passages recovered | Indexed captions only; no figure-image or table-value inspection |

The [2005 primary abstract](https://pubmed.ncbi.nlm.nih.gov/15958601/)
addresses repetitive-response depression; it does not establish the isolated
45 mV measurement protocol. Later papers' citation excerpts and catalog entries
were not used to fill missing original Methods. A PubMed sex indexing term is
not verification of the sex of the particular amplitude subexperiment.

## Evidence chain and exact amplitude audit

The [2007 paper](https://journals.physiology.org/doi/full/10.1152/jn.01258.2006),
Methods (Martin-correction paragraph) and Results (docked-vesicle/quantal-content
subsection), attributes the 45 mV estimate to 2005. It describes a G1 EJP from
one stimulus, a muscle-firing threshold qualifier, and 4 mM Na-L-glutamate
suppression of the electrogenic response. This is not a new 2007 measurement.
The threshold qualifier does not specify stimulus voltage or a stimulus-intensity
setting. The reported quantity is a synaptic/junction-potential amplitude, not
whole-TTM voltage, a spike amplitude or model gain.
However, the original baseline-relative versus absolute measurement operation,
peak versus another amplitude definition, and measurement window are **NOT_VERIFIED**.
No missing operation is inferred from common EJP terminology.

The 2007 quantal analysis invokes a single action potential without previous
activity; that analysis context does not recover the original trial spacing,
rest duration, sample count or amplitude-measurement procedure. Neither a 1-Hz
train elsewhere in that paper nor the abstract's frequency discussion can set
the isolated benchmark frequency. The amplitude record has no verified sample
size or uncertainty/statistical form; no SD, SEM or acceptance interval is invented.

## Separate 2007 context, not a substitute 2005 protocol

Recovered 2007 Methods describe four-day-old female D. melanogaster, Oregon-R
and shibire preparations; intracellular G1 recording near its tergal attachment
with a dye-filled glass electrode; neck stimulation with 0.1-ms square pulses.
Its anatomical saline paragraph concerns microscopy preparation, not a verified
electrophysiological bath for the reused amplitude. These facts are study context,
**not assigned to the original amplitude experiment**. Its exact genotype,
temperature, electrode location, preparation, saline and pulse remain unverified.
[Primary Methods](https://journals.physiology.org/doi/full/10.1152/jn.01258.2006)

In particular, the 2007 neck/GF pathway stimulation and a separate cut-nerve
stimulation subexperiment must not be merged into an assumed 2005 stimulus site.
The giant motor axon's G1 relationship does not identify the experimental axon
as either pinned MaleCNS body. Side-specific G1 physiology remains unresolved.

## Proposed minimal future protocol fields — not implemented

Every unknown empirical field would require null plus `NOT_VERIFIED` and a
source-access reason, not a wildcard. The table classifies requirements for a
**source-matched empirical benchmark**, not requirements for an arbitrary toy run.
`REQUIRED_AND_VERIFIED` includes independently checked repository references and
architectural constraints where indicated; those are not experimental measurements.
No concrete future benchmark ID or schema is generated.

| Proposed field(s) | Current content / scope | Classification | Why it matters |
| --- | --- | --- | --- |
| benchmark_id | Required deterministic run/protocol identity; eventual value not created | REQUIRED_AND_VERIFIED (architectural requirement) | Distinguish a benchmark from causal fixtures |
| source_observation_id | Canonical evoked record ID above | REQUIRED_AND_VERIFIED (repository) | Phase 8S empirical authority |
| source DOI / role | 2005 original attribution; 2007 reuse | REQUIRED_AND_VERIFIED | Do not relabel the measurement |
| source_location | 2007 Methods and docked-vesicle Results; original 2005 amplitude location unknown | REQUIRED_BUT_UNKNOWN for the original measurement | Auditable original procedure |
| species | D. melanogaster per pinned evidence scope | REQUIRED_AND_VERIFIED (scope) | Not proof of a matched preparation |
| age, sex, genotype | Original amplitude subexperiment NOT_VERIFIED | REQUIRED_BUT_UNKNOWN | Do not borrow 2007 study-wide demographics |
| temperature_c / temperature_role | Original test condition NOT_VERIFIED | REQUIRED_BUT_UNKNOWN | Rearing temperature is not test temperature |
| preparation | Original exposed/intact and conditioning details NOT_VERIFIED | REQUIRED_BUT_UNKNOWN | Changes recording/input interpretation |
| bath_or_medium | Glutamate condition reported in reuse; full medium and delivery NOT_VERIFIED | REQUIRED_BUT_UNKNOWN for complete condition | Preserve pharmacological suppression without inventing bath composition |
| stimulation_site / recruited pathway | Original site NOT_VERIFIED | REQUIRED_BUT_UNKNOWN | An experimental pulse is not an abstract token |
| pulse_duration / waveform / intensity | Original settings and recruitment criterion NOT_VERIFIED | REQUIRED_BUT_UNKNOWN | Do not copy 2007 pulse or interpret muscle threshold as stimulus voltage |
| stimulus_count_semantics | Single-stimulus response in 2007 reuse context | REQUIRED_AND_VERIFIED (reuse scope) | Isolated event family only |
| within-trial stimulation_frequency | No train within a single-stimulus trial | NOT_APPLICABLE | Does not authorize an intertrial frequency |
| stimulus_history / intertrial interval / equilibration | Actual original trial history NOT_VERIFIED | REQUIRED_BUT_UNKNOWN | Isolation and valid baseline require history control |
| recording_fiber | G1 | REQUIRED_AND_VERIFIED (reuse and pinned scope) | One fiber, not whole TTM |
| recording_method / location / mode | Original amplitude setup NOT_VERIFIED | REQUIRED_BUT_UNKNOWN | 2007 intracellular description is not original-protocol verification |
| electrode fabrication / acquisition hardware detail | Only if necessary to reproduce the recovered amplitude definition | OPTIONAL pending original Methods | Record verified details, never invent instrument settings |
| response_quantity | G1 evoked junction/synaptic-potential amplitude | REQUIRED_AND_VERIFIED (reuse scope) | Not muscle electrogenic response or model parameter |
| amplitude_semantic / baseline_semantic / operator_semantic | Original operation, baseline sample/interval and peak window NOT_VERIFIED | REQUIRED_BUT_UNKNOWN | Model peak extraction is not source-matched measurement |
| sample_size / uncertainty metadata | No recovered value-specific n or statistical form | OPTIONAL for execution; retain explicit unknowns | Essential before statistical scoring, not fillable from other subexperiments |
| empirical laterality | Original side-specific dataset not verified | OPTIONAL for side-agnostic proxy; unresolved | No manufactured bilateral equivalence |
| model_source / operator_source / provenance | Versioned model/operator identity and explicit benchmark origin required | REQUIRED_AND_VERIFIED (architectural requirements) | Prevent reuse of synthetic neural ancestry as evidence |
| physical-unit mapping | No justified biological mapping | REQUIRED_BUT_UNKNOWN for numerical comparison; NOT_APPLICABLE to model-space-only extraction | Keep execution and empirical validation separate |
| unresolved_fields | Structured inventory of every unverified requirement | REQUIRED_AND_VERIFIED (assessment requirement) | Unknown never equals matched |

Stimulus, preparation and amplitude-operation gaps materially affect interpretation.
They prevent implementation of a purported source-matched runner. A generically
executable single input with guessed settings would add a model-behavior fixture,
not recovery of this empirical protocol.

## Phase 9E compatibility and literal reuse limits

Compatibility classification: **CONCEPTUALLY_CLOSE_BUT_NOT_SOURCE_MATCHED**.
Phase 9E computes the immediate pre-event stored sample and maximum positive
deflection through the stored trajectory end. Neither that baseline rule nor
that search window is recovered as the experimental measurement rule. Its
window is legitimate for model extraction only, not an experimental duration.

Keep Phase 9E unchanged. Its mathematical baseline/peak semantics remain useful
for future model-space output, but current literal benchmark reuse is not ready:
the canonical artifact builder admits only the exact Phase 9B artifact, and the
extractor admits the four pinned fixture labels and Phase 9B/8W source envelope.
A new benchmark event has neither genuine Phase 8W ancestry nor existing
benchmark-trajectory admission. It must not spoof fixture labels or token IDs
to bypass those checks. A future benchmark needs explicit validated source
admission and provenance, with reuse of extraction logic assessed then; there is
no evidence yet requiring correction of the valid Phase 9E model-space operator.
Whether a different experimental baseline/window operator is necessary remains
unresolved until original Methods are recovered.

## Isolated benchmark architecture and input semantics

Recommended eventual boundary, not implemented:

`protocol-defined stimulus -> benchmark-specific model-input event -> same
passive model form -> admitted model-space observation extraction`.

The benchmark must be isolated from synthetic DNp01/TTMn fixtures. A distinct
benchmark provenance would mean an explicitly chosen experimental/model stimulus
boundary, not connectome-generated activity, transmitter release, one quantum,
measured current or biological transmission success. A deterministic event can
request one effective model increment only as an explicit modelling assumption.
It cannot derive the event scale from stimulus voltage or recruit the full
experimental pathway automatically. The public Phase 9B canonical runner admits
Phase 8W inputs only; using its numerical model form for benchmarks would require
separate admission, not changing historical source semantics.

The existing arbitrary reference config can remain useful for future plumbing
tests. It would not be a formal empirical calibration. Do not select another
config or a sensitivity-grid cell. No new biological delay may be assigned;
token-boundary zero-added model delay does not recreate experimental latency.

## Execution levels and physical interpretation

| Level | Meaning | Current readiness |
| --- | --- | --- |
| 0 | Reproduce a verified protocol's input/plumbing, no scoring | Not ready for this original protocol: essential fields unresolved |
| 1 | Extract a model-space observable | Executable for existing model fixtures; not yet for a newly admitted empirical benchmark |
| 2 | Establish physical interpretation/unit mapping | Not ready |
| 3 | Perform legitimate empirical numerical comparison | Not ready |

The term "protocol execution only" would be honest only after recovering the
material protocol fields. Lack of a physical-unit map alone would not prohibit
levels 0–1; the independent protocol and admission gaps prohibit claiming those
levels for this benchmark now. No biological benchmark accuracy is ranked.

## Physical mapping and parameter identifiability

`mV_eq` stays an uncalibrated coordinate. No equality with biological mV,
conversion coefficient or two-point calibration is asserted. A possible future
affine map would need independently justified offset, scale and protocol/domain
applicability; merely renaming units or imposing a physical-unit equation does
not supply that justification. No conversion is implemented here.

| Quantity | Current empirical identification | Conditional future information |
| --- | --- | --- |
| Effective event scale | Unidentified | A matched evoked amplitude could constrain an effective magnitude or physical-scale-times-event-scale product, not both factors independently |
| Reference/physical offset | Unidentified | Matched resting data could constrain baseline, not event scale or tau; the pinned descriptive resting context is not a confirmed common-protocol calibration point |
| Effective tau | Unidentified | Needs source-compatible temporal response data and observation semantics, not a single amplitude |

With a free physical scale and event scale, peak magnitude identifies at most
their product. With free coordinate reference and physical offset, the baseline
likewise contains a degeneracy. The existing reference is fixed at neutral zero,
but that does not identify a biological offset. Resting and reused evoked
observations must not be merged into one fictional matched experiment.

**TAU_NOT_CONSTRAINED_BY_CURRENT_PINNED_EVIDENCE.** Targeted primary-passage
searches for decay/time-constant/response-window evidence did not recover a
source-matched isolated EJP decay dataset. Recovered train/depletion and miniature
captions are different quantities, not effective electrical tau evidence. The
2005 figures remain inaccessible here, so this is not a claim that the complete
paper contains no time-course information. No digitization or fitting occurred.
Phase 9C's internal separability is mathematical model evidence only.

## Decisions and exactly one next phase

Phase 9F assessment status: **PASS**; benchmark implementation remains not ready.
Quality gates passed: 789 Python tests, one deselected, two existing dependency
warnings; Ruff check/format and diff whitespace checks; 38 frontend tests,
lint, typecheck and production build. Only this document and the minimal Project
Context update are retained. No commit or push was made.

- Benchmark readiness: `PRIMARY_SOURCE_PROTOCOL_RECOVERY_REQUIRED`.
- Phase 9E operator use: `OPERATOR_USE_NOT_READY` for an unchanged, newly sourced
  empirical benchmark; existing model-space extraction remains valid.
- Physical units: `BIOLOGICAL_MV_MAPPING_NOT_READY`.
- Execution level: `BENCHMARK_EXECUTION_NOT_READY`.
- Parameters: `PARAMETERS_STILL_EMPIRICALLY_UNIDENTIFIED`.
- Next phase: `RECOVER_PRIMARY_2005_PROTOCOL_DETAILS`.

Exactly one Phase 9G: obtain lawful complete original 2005 Methods and the
amplitude-associated Results/caption, then audit the isolated G1 preparation,
stimulus and amplitude/baseline/window definitions. Request a user-supplied or
institutionally accessible copy if public recovery cannot reach those sections;
do not contact authors or purchase access without separate authorization.
Deliver a source-location-linked protocol inventory and an explicit runner go/no-go
decision. Do not implement a runner, mutate pinned contracts, digitize figures,
fit parameters or compare model values. This is one concrete access/recovery
task, not another metadata-contract chain.
