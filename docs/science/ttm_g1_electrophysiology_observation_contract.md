# Phase 8S — protocol-specific TTM G1 electrophysiology observation contract

Phase 8S pins nine curated observations and their protocol/source metadata in
`ttm_g1_electrophysiology_observation_contract_v1`. This is an empirical
observation layer, not a physiology model, parameter file, benchmark runner, or
calibration target with pass/fail tolerances. It contains no model-parameter
export.

The biological scope is adult *Drosophila melanogaster* TTM/G1 evidence at the
granularity actually reported. A G1 fiber is not the whole TTM. These studies
do not identify their recorded axon/fiber with MaleCNS body `800146` or
`804642`; the Phase 8K MaleCNS TTMn identities and this independent class-level
physiology evidence are not an exact-body crosswalk.

## Evidence manifest and limits

| Source | Role in this contract | Verification boundary |
| --- | --- | --- |
| Koenig & Ikeda 2007, [DOI 10.1152/jn.01258.2006](https://doi.org/10.1152/jn.01258.2006) | Primary source for G1 preparation, observations, and analysis context. | Publisher-indexed Methods, Results, Discussion, and figure-caption text was directly checked for Phase 8R. Direct page retrieval returned HTTP 403 there; no figure values were digitized. |
| Koenig & Ikeda 2005, [DOI 10.1152/jn.00323.2005](https://doi.org/10.1152/jn.00323.2005) | Prior primary result reused for the 45 mV analysis input; qualitative depression context only. | Primary [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/15958601/) only. Quantitative methods/results/figures are not pinned. |
| Kadas, Duch & Consoulas 2019, [DOI 10.1523/ENEURO.0181-19.2019](https://doi.org/10.1523/ENEURO.0181-19.2019) | Primary source for the age-labelled composite TTMn-region-stimulation to TTM-potential-onset latency. | Open full [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6709211/), including Methods, Figure 1, and Table 1. The latency is not an isolated NMJ delay or an intracellular G1 observation. |

The 2007 anatomical account describes 23 TTM fibers: giant motor-axon branches
innervate G1–G19; F1–F4 receive two finer axons. G1 is experimentally useful
because its small, regular geometry and extensive, relatively simple
innervation support intracellular recording and anatomical analysis. Calling
its innervation pattern representative does not establish identical
electrophysiology across fibers. G1 observations remain single-fiber evidence.

The 2007 preparation used four-day-old adult female flies, wild-type Oregon-R
and temperature-sensitive `shibire^ts1` (`shi`) preparations, with some
thoracic-`shi` gynandromorph preparations. The fly was fixed, a dye-filled glass
micropipette recorded intracellularly from G1 near its tergal attachment, and
a neck electrode delivered 0.1 ms square pulses where stimulation was used.
`shi` recycling functions at 19 °C and is impaired at higher temperatures;
29 °C was used for a separate blocked-recycling condition. Exact protocol
dimensions are attached to each record where source-verified. Missing
dimensions remain null with an explicit `NOT_REPORTED`, `NOT_VERIFIED`, or
`NOT_APPLICABLE` status and reason. Rearing temperature is not silently
substituted for an electrophysiology test temperature.

## Pinned observation records

The first contract contains exactly these nine records, in curated order.
`observation_id` values are deterministic hashes of each record’s semantic
content. Record classification and applicability are separate fields.

| Quantity | Observation | Classification | Applicability and protocol boundary |
| --- | --- | --- | --- |
| `G1_RESTING_MEMBRANE_POTENTIAL` | Approximately −95 mV | `DESCRIPTIVE_MEASURED_VALUE` | G1 study context. No distribution, uncertainty, or n is stated with this approximate value; not a NeuroFly `V_rest`. |
| `G1_EVOKED_JUNCTION_POTENTIAL` | 45 mV | `PRIOR_PRIMARY_RESULT_REUSED` | G1 threshold-level evoked response reused by the 2007 Martin correction; the 2007 account reports 4 mM Na-L-glutamate to suppress the electrogenic response. The value is attributed to Koenig & Ikeda 2005, whose exact protocol was not verified here. Not a new 2007 measurement, whole-TTM voltage, or gain. |
| `G1_MINIATURE_JUNCTION_POTENTIAL` | Approximately 0.5 mV | `DESCRIPTIVE_MEASURED_VALUE` | Approximate histogram-supported G1 MEJP estimate, `shi`, 19 °C. No uncertainty/n is pinned. It is a miniature potential, not an evoked response or `event_gain`. |
| `G1_EQUILIBRIUM_POTENTIAL_ANALYSIS_INPUT` | −10 mV | `ANALYSIS_INPUT_FROM_PRIOR_SOURCE` | `V0` used by the 2007 Martin RC correction and attributed there to Ikeda 1980. Not a new 2007 measurement or automatic NeuroFly reversal potential. |
| `G1_QUANTAL_CONTENT` | Approximately 191 quanta | `DERIVED_QUANTITY` | Single stimulus with no prior activity; reported corrected quantal content derived using the 45 mV response, approximately 0.5 mV miniature potential, and −10 mV `V0`. `v` is evoked potential, `v1` miniature/quantal potential, `V0` correction equilibrium input, and `m` derived quantal content. The contract records the reported result; ordinary loading does not recompute the physiology. |
| `G1_SPONTANEOUS_MEJP_FREQUENCY` | 7 ± 3 events/s; n = 5 flies | `SUMMARY_STATISTIC` | Wild-type G1 at 19 °C. The source passage does not establish whether ±3 is SEM, SD, or another uncertainty; the contract uses `UNKNOWN_NOT_ESTABLISHED`, never `MEAN_SEM`. Spontaneous observations are distinct from evoked trials. |
| `G1_DEPRESSION_PROTOCOL_OUTCOME` | `NO_OBSERVED_DEPRESSION_UNDER_THIS_PROTOCOL` | `CATEGORICAL_OBSERVATION` | `shi`, 19 °C, recycling permitted, 1 Hz, 1,500 stimuli, G1 recordings. This is protocol-specific and does not mean TTM never depresses at 1 Hz. The 29 °C blocked-recycling protocol is distinct. |
| `G1_VESICLE_RECYCLING_RATE` | 0.24 vesicle/active zone/s | `DERIVED_QUANTITY` | Source-reported rate derived from 286,500 ± 9,680 quanta (five flies; uncertainty type not established) versus 31,800 under blocked recycling, divided by 1,500 s and approximately 720 G1 active zones. These are derivation inputs, not extra records. It is not a NeuroFly recovery tau or model coefficient. |
| `TTMN_REGION_STIM_TO_TTM_POTENTIAL_ONSET_LATENCY` | 0.84 ± 0.02 ms; mean ± SEM; n = 8 | `SUMMARY_STATISTIC` | Kadas 24 h post-eclosion control; both sexes. Thoracic motor-neuron-region tungsten stimulation to onset of the initial TTM potential phase. The measured test temperature is not stated in the cited protocol. This composite includes axonal conduction, neuromuscular transmission, and muscle-potential onset; it is explicitly **not** isolated NMJ delay and is not a G1 intracellular recording. |

The 2007 analysis describes an approximately 720-active-zone G1, approximately
36,000 vesicles, and approximately 360 morphologically docked vesicles. These
study quantities contextualize the reported quantal estimate; they are not
MaleCNS structural counts, synapse weights, or NeuroFly efficacy values.

## Observation/model boundary

Each record has a `model_comparability` status of
`OBSERVATION_MODEL_REQUIRED`; its `current_neurofly_observable` is null.
Phase 8Q records only an exploratory NMJ-input handoff and cannot predict
membrane voltage, quantal content, spontaneous frequency, recycling rate, or
muscle-potential onset latency. A future electrical G1 model might produce a
comparable voltage only after an explicit observation mapping specifies fiber,
electrode, stimulation, and protocol. A dimensionless state would not be
numerically comparable to mV without such a mapping.

The 24 h post-eclosion Kadas value is kept age-specific and is not merged with
the 1 h comparator (0.80 ± 0.04 ms, mean ± SEM, n = 5). Neither value is
relabelled as NMJ delay. A muscle electrical potential is not muscle force.

## Explicit exclusions

- Quantitative Koenig & Ikeda 2005 depression series: `QUALITATIVE_ONLY` from
  the verified primary abstract; no figure digitization or curve reconstruction.
- Figure/OCR-derived values and copied article text/PDFs.
- Exact MaleCNS-body physiology, side-resolved G1 mapping, and whole-TTM
  inference from G1 observations.
- NeuroFly parameterization, fitting, priors, losses, acceptance windows, or
  calibration claims.
- NMJ/muscle dynamics, activation, release probability, force, mechanics, and
  behavior.

The 2005 qualitative abstract finding is retained in the evidence manifest as
context, not expanded into a tenth observation record. Source access is needed
for curation only; normal generation, inspection, validation, and replay use
the checked-in definitions and make no network requests.

## Artifact and replay

The artifact is immutable and content-addressed. `config_sha256` covers the
evidence manifest, source-verification scope, boundary, exclusions, and
vocabularies; `result_sha256` covers the nine canonical records and their
observation IDs; the contract/artifact ID covers both hashes. Replay rebuilds
the curated payload offline, validates source references, units, finite values,
uncertainty semantics, protocol status/reasons, classifications, applicability,
scope, and hashes, then requires exact equality with the pinned definition.

The reference artifact is
`5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f`;
`config_sha256` is
`4c389614939cdf77c1aa545d25734eb810e829dae43c0c72aa1a18cbc378a48e` and
`result_sha256` is
`fb45ac6689c411774dc2e1c2ea6d2ac6f4fa324388b24ecb010df795560fa58b`.
The two-file artifact occupies 40,012 bytes.

```bash
python -m neurofly.ttm_g1_electrophysiology_observation_cli generate
python -m neurofly.ttm_g1_electrophysiology_observation_cli inspect <artifact>
python -m neurofly.ttm_g1_electrophysiology_observation_cli replay <artifact>
```

The generated artifact is under ignored `data/derived/malecns/` data. It is
not an input to Phase 8Q and does not change any motor/NMJ runtime behavior.
