# Phase 9G — original 2005 G1 evoked-protocol recovery gate

## Outcome

`NO_GO_REQUIRE_USER_SUPPLIED_2005_FULL_TEXT`.

The bounded lawful recovery attempt did not obtain the original Methods,
relevant Results or captions. Essential stimulus and amplitude operations remain
unverified. This closes the current benchmark implementation path, not merely
postpones it to another source-search phase. Supply the primary material listed
below to resume Phase 9G. No runner, schema, artifact, operator revision,
parameter change, fitting, figure digitization or empirical comparison is added.
Completion of this negative source gate can be a Phase 9G PASS; it is not a
benchmark GO.

## Repository gate and source replay

Initial worktree was clean on `main` at
`271746393deab9b7929b0089bd2dfebbcd31c288`, equal to `origin/main`.
The log confirmed committed Phases 9F, 9E, 9B and 8S; initial diff check passed.
The audit inspected the Phase 9F readiness document, Phase 8S evoked record,
Phase 9E extraction/admission semantics, Phase 9D compatibility assessment,
source-access conventions and Project Context.

| Replayed source | Unchanged artifact identity |
| --- | --- |
| Phase 9E | `2c775d6e00d74b3b3a3ca5a36bb84fd4032959d29f3c7d4c8b0bca934e2942b8` |
| Phase 9B | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` |
| Phase 8S | `5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f` |
| Phase 8U | `f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f` |

All four passed. Phase 8U remains at zero formally ready mappings. No source
artifact, observation, model config or historical readiness snapshot is changed.

## Authenticity, access and lawful recovery ledger

Target identity: Koenig JH, Ikeda K (2005), *Relationship of the Reserve Vesicle
Population to Synaptic Depression in the Tergotrochanteral and Dorsal
Longitudinal Muscles of Drosophila*, Journal of Neurophysiology 94(3):2111–2119,
DOI `10.1152/jn.00323.2005`, PMID 15958601. The primary bibliographic record and
abstract establish this identity, not possession of its full text.
[PubMed record](https://pubmed.ncbi.nlm.nih.gov/15958601/)

**2005 access classification: `ABSTRACT_ONLY`.** No version-of-record full text,
accepted manuscript or other authenticated primary full text was recovered.
Methods, original G1 amplitude Results, figures, tables and captions were not
accessible for inspection. The approximately 45 mV original passage is
`NOT_LOCATED` in the accessible 2005 material. This does not mean the value is
absent from the complete paper; its exact original page/figure is unknown.

Recovery was checked on 2026-09-30:

| Legitimate route | Result and limitation |
| --- | --- |
| APS publisher full/PDF/ePDF and DOI routes | Requests failed or returned access denial; no complete text inspected |
| PubMed and Europe PMC | Primary abstract/identity recovered; no target PMC full-text copy found |
| Europe PMC core metadata API | Successfully retrieved: subscription-required DOI link only; no indexed PMC PDF or author manuscript |
| DOI/title searches for institutional/author copies and accepted manuscripts | No authenticated target full text recovered; citing theses, publication lists and different articles excluded |
| Project files, including ignored data outside dependency/build trees | No user-supplied target paper copy found; a build-cache numeric filename is not evidence |
| Indexed 2007 publisher Methods/Results | Reused-value passages accessible, not the original 2005 Methods; complete 2007 access not established |

The [Europe PMC record](https://europepmc.org/article/MED/15958601) metadata
reports no indexed open-access/PMC/author-manuscript version and provides only
the subscription DOI full-text URL. This describes that index and this recovery
attempt, not proof that no lawful copy exists anywhere. No pirate archive,
secondary summary or unidentified manuscript supplied biological facts. No
paper text/PDF is redistributed in the repository.

## Original versus reused evidence

The 2005 abstract addresses repetitive-response depression but does not recover
the isolated amplitude protocol. The 2007 indexed primary passages, Methods
(Martin-correction paragraph) and Results (docked-vesicle/quantal-content
subsection), attribute the amplitude estimate to 2005. They give an EJP/G1,
single-stimulus description and a muscle-firing-threshold qualifier, together
with a glutamate suppression condition. These remain reused evidence, not
newly verified original measurements.
[2007 primary paper](https://journals.physiology.org/doi/full/10.1152/jn.01258.2006)

| Fact | Chain classification | Evidentiary limit |
| --- | --- | --- |
| 2005 authors/title/journal/DOI and repetitive-depression abstract | `ORIGINAL_2005` | Bibliography/abstract only |
| Approximately 45 mV G1 EJP, one-stimulus and firing-threshold descriptions | `REUSED_IN_2007` | Original operation, isolated-trial history and statistic not recovered |
| Reported 4 mM Na-L-glutamate used to suppress electrogenic response | `REUSED_IN_2007` | Original condition scope/delivery and benchmark applicability unverified |
| 2007 preparation, recording and stimulation Methods | `2007_ONLY_CONTEXT` | Must not fill original 2005 protocol fields |
| Original baseline, peak window, stimulus/preparation subexperiment and sample statistics | `UNRESOLVED` | Requires original Methods/Results/captions |

The glutamate condition belongs to the reused amplitude explanation in 2007,
not an independently verified 2005 benchmark bath recipe. It is not copied into
a future protocol. Likewise the threshold qualifier is not a stimulus voltage,
current or recruitment criterion. A one-stimulus response is not proof of a
history-free isolated trial. No 2007 age, sex, genotype, pulse or saline is
substituted for the original experiment.

## Protocol completeness and materiality

Verification levels below distinguish repository authority, original abstract,
reused primary passage and original source unavailable. A material unknown is
one whose omission would change the interpretation of stimulus, recording or
response. Equipment brands and optional descriptive details do not themselves
block implementation. Unknown never means matched or wildcard-compatible.

| Field | Value/status | Primary source location / verification level | Implementation importance/classification |
| --- | --- | --- | --- |
| Source observation reference | `ttm-g1-obs-0e8110027289e2606870` | Phase 8S repository authority, not a primary measurement | `REQUIRED_AND_VERIFIED`: exact evidence reference |
| Original paper identity | DOI `10.1152/jn.00323.2005` | PubMed/Europe PMC bibliography | `REQUIRED_AND_VERIFIED`: authentic source |
| Response quantity | G1 EJP/synaptic-potential amplitude in reused account; original operation unverified | 2007 Methods/Results, reused primary passages | `REQUIRED_BUT_UNKNOWN`: original measurement definition material |
| Recording domain | G1 in reused account; original fiber-identification criteria unknown | 2007 Results; 2005 Results unavailable | `REQUIRED_BUT_UNKNOWN`: original domain confirmation material |
| Amplitude operation | `AMPLITUDE_OPERATION_UNRESOLVED`; peak/absolute/baseline-relative/mean/representative not verified | 2005 Methods/Results/captions unavailable | `REQUIRED_BUT_UNKNOWN`: architecture-critical |
| Baseline | `BASELINE_SEMANTICS_UNRESOLVED` | Original measurement procedure unavailable | `REQUIRED_BUT_UNKNOWN`: amplitude interpretation |
| Measurement window/timing criterion | `WINDOW_SEMANTICS_UNRESOLVED` | Original Methods/captions unavailable | `REQUIRED_BUT_UNKNOWN`: honest operator specification; no invented interval |
| Stimulus location | UNKNOWN: neck/nerve/axon/CNS not verified for this experiment | Original Methods unavailable | `REQUIRED_BUT_UNKNOWN`: input boundary material |
| Pulse duration/form/intensity/recruitment | UNKNOWN; firing threshold does not specify these | Original Methods unavailable | `REQUIRED_BUT_UNKNOWN`: stimulus context material |
| Stimulus count/trial context | One stimulus described in 2007; isolated trial versus train-first/averaging unknown | Reused Results, original Results unavailable | `REQUIRED_BUT_UNKNOWN`: source-matched scheduling |
| Train frequency | Not applicable if an isolated single-stimulus protocol is confirmed; presently unverified | Original trial context unavailable | `REQUIRED_BUT_UNKNOWN`: do not assume isolation |
| Intertrial/prior stimulation/recovery history | UNKNOWN | Original Methods/Results unavailable | `REQUIRED_BUT_UNKNOWN`: depression/recovery context material |
| Species | Drosophila study verified; exact preparation specification not recovered | Original title/abstract | `REQUIRED_BUT_UNKNOWN`: preparation-specific record incomplete |
| Age, sex, genotype, temperature | UNKNOWN for amplitude subexperiment | Original Methods unavailable | `REQUIRED_BUT_UNKNOWN`: materially condition-dependent |
| Dissection/preparation, saline, pharmacology | UNKNOWN; glutamate reported only in reused account | Original Methods unavailable; 2007 reused Results | `REQUIRED_BUT_UNKNOWN`: electrogenic suppression/context material |
| Intracellular/extracellular method and relevant recording location | UNKNOWN for original amplitude subexperiment | Original Methods unavailable | `REQUIRED_BUT_UNKNOWN`: measured-potential interpretation |
| Electrode/acquisition equipment detail | UNKNOWN | Original Methods unavailable | `OPTIONAL_UNKNOWN`: only becomes required if it defines the operation |
| Sample n/statistic/uncertainty kind | UNKNOWN; no verified mean/SEM/SD | Original Results/captions unavailable | `OPTIONAL_UNKNOWN` for execution; required before inferential scoring |
| Side-specific empirical physiology | Not established | No verified original side dataset | `OPTIONAL_UNKNOWN`: retain side-agnostic proxy, no bilateral claim |
| Biological voltage conversion | Absent | Not an experimental protocol field | `NOT_APPLICABLE` to execution-only; required separately for numerical comparison |

Thus stimulation, recording, preparation and statistic recovery did not progress
beyond explicitly labelled reused/abstract evidence. No original figure or table
was inspected. Lack of a recovered window is not authority to make the Phase 9E
whole-trajectory window the experimental one.

## Phase 8S consistency and Phase 9E operator compatibility

Phase 8S is `INCOMPLETE_BUT_NOT_INCORRECT`: its evoked record correctly remains
`PRIOR_PRIMARY_RESULT_REUSED`, with missing original protocol metadata. No
contradiction was recovered, but the original source has not confirmed the
measurement. Source-contract decision: `PHASE8S_OBSERVATION_INCOMPLETE_BUT_VALID`.
Do not silently revise the canonical record or upgrade it to an original result.

Internal experimental/operator assessment: `UNRESOLVED`. Phase 9E uses the
immediate pre-event stored boundary and positive maximum from event boundary
through trajectory end, without interpolation. Original baseline and amplitude
operation are unavailable. Consequently none of exact reuse, reuse with a
source-specific window, or a distinct empirical operator can be selected yet.
Decision: `OPERATOR_SEMANTICS_NOT_READY`. This is not a defect in its validated
model-space behavior. Canonical source admission also requires Phase 9B fixture
ancestry; a future benchmark must not fabricate Phase 8W tokens or synthetic
DNp01 history to pass it.

## Conditional benchmark design, not a minimum viable recovered protocol

No source-matched minimum viable protocol can presently be specified. Before
implementation, the original material must establish response operation/domain,
stimulus context, material preparation and recording conditions, and honest
baseline/window rules. Nonmaterial unreported fields can remain explicit unknowns;
the table does not require inventing apparatus trivia or forcing every possible
field to be reported.

The eventual architecture may separate an empirical benchmark stimulus from
connectome-driven causal runs. A distinct benchmark-provenance event could admit
an abstract model input at a declared stimulus boundary, as an explicit model
assumption—not release, a quantum or measured current. No synthetic neural
ancestry would be assigned. This conceptual interface does not recover the
unknown experimental stimulus and is not implemented.

Level A, source-matched protocol execution in the uncalibrated model, is **not
ready** because of material protocol/operation unknowns. Level B, numerical
comparison with biological mV, is independently **not ready**. Physical
calibration is not required for Level A, but missing original semantics cannot
be waived by calling a toy run a benchmark. The arbitrary reference model
configuration is unchanged, and no sensitivity cell is selected.

## Physical units and parameter identifiability

`mV_eq` remains model-space voltage-equivalent coordinates, not biological mV.
Source recovery has not established a conversion. A hypothetical biological
output scale and the effective event scale remain multiplicatively confounded;
an amplitude alone would constrain their product, not each independently.
Neither is fitted. A resting observation from another protocol cannot silently
fix the offset; preparation/operator/protocol compatibility must first exist.

Original 2005 isolated-response time-course evidence is `UNRESOLVED` because
the Results/figures are inaccessible. Do not label it figure-only, qualitative,
numeric or absent from the full paper. **Tau is not constrained by current pinned
evidence** (`TAU_NOT_CONSTRAINED`); no verified numeric decay constraint was
recovered. No plot points are extracted. All model parameters remain empirically
unidentified; the Phase 9C structural-separability finding does not change that.

## Definitive decisions and source requirement

| Gate | Decision |
| --- | --- |
| Benchmark protocol | `PRIMARY_SOURCE_FULL_TEXT_REQUIRED` |
| Source contract | `PHASE8S_OBSERVATION_INCOMPLETE_BUT_VALID` |
| Operator | `OPERATOR_SEMANTICS_NOT_READY` |
| Execution level | `BENCHMARK_EXECUTION_NOT_READY` |
| Physical units | `BIOLOGICAL_MV_MAPPING_NOT_READY` |
| Tau | `TAU_NOT_CONSTRAINED` |
| Runner | `NO_GO_REQUIRE_USER_SUPPLIED_2005_FULL_TEXT` |

Request a lawful copy of Koenig & Ikeda 2005 (article pages 2111–2119), or at
minimum its **Methods pages, G1 evoked-response Results, associated figure/table
captions, and any section defining the approximately 45 mV measurement**.
The exact relevant page/figure cannot be specified because it was not located.
Only after that material is supplied should Phase 9G resume. Do not create a
Phase 9H that repeats the same access search or implement a runner now.

Scientific boundaries remain: no physical input transformation, release claim,
exact MaleCNS-to-G1 anatomy, whole-TTM response, calibration, scoring, dynamics,
contraction or force. Only this document and the minimal Project Context entry
are authorized tracked changes. No generated scientific artifact is created.

## Quality gates and phase status

`python -m pytest`: 789 passed, 1 deselected, two dependency deprecation warnings.
`python -m ruff check .`, `python -m ruff format --check .` (254 files) and
`git diff --check` pass. Frontend regression commands `npm test` (38 passed),
`npm run lint`, `npm run typecheck` and `npm run build` pass. The build-generated
`next-env.d.ts` change was restored to its original content; no frontend source
change remains. No commit or push. Phase 9G status: **PASS**, with the definitive
benchmark NO-GO above and no newly generated scientific data.
