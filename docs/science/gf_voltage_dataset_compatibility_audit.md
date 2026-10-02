# Phase 21 — GF voltage dataset compatibility and acquisition audit

## Finding and scope

Open numerical GF whole-cell data **were located**. The strongest accessible
candidate is Dombrovski's Zenodo record
[10.5281/zenodo.14983850](https://zenodo.org/records/14983850).
Two unmodified MAT files were acquired and their structure inspected. Their
arrays are not self-describing, but the companion workbook explicitly supplies
the individual-file clock, onset, stimulus-column and animal/trial mapping.
Stored voltage units/scale, acquisition filtering, recording metadata and the
combined-array/version bridge still require an authoritative dictionary.
They are `METADATA_INSUFFICIENT`, not calibration-ready. A related processed
LPLC2 calcium archive informs operator design, not a calibrated presynaptic scale.

Data availability: `OPERATOR_DESIGN_DATA_ONLY`.
Calibration readiness: `DATA_AVAILABLE_BUT_METADATA_INSUFFICIENT`.
Twelve candidate/source records; **zero** sufficient for calibration or for a
complete pre-registered calibration protocol under the Phase 20 strict standard.
This is not a claim that GF raw data do not exist, or that no additional data exist
outside the bounded search. File metadata and the separate source-state operator
are both unresolved; obtaining the dictionary alone would not identify `k`.

No fitting, trace digitization, OCR, waveform alignment, required-gain calculation,
new model run against candidate data, parameter changes or external author contact
occurred. No source data are tracked. No production code depends on this review.

## Authority and repository gate

Started clean on `main == origin/main`, HEAD
`76bd174ed63f8e2a40e1776ce91924daea1fbaad`; Phase 20, 19, 18, 17,
corrected 16, 15 and 13B commits verified before research.
The unchanged [Phase 20 specification](observation_operator_assay_compatibility.md)
and JSON are the compatibility authority. Its canonical SHA-256 is
`ae50e1faad223cdde63125a6216ce0993523f9933025fe1f04e9265450dec824`.

Historical offline replays passed before acquisition or edits:

| Source | Unchanged artifact identity |
| --- | --- |
| Phase 18 | `ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c` |
| Corrected Phase 16 | `bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b` |
| Phase 13B | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` |
| Full numerical Phase 7O | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` |
| Genuine Phase 8C | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` |

## Reproducible bounded search

Checked 2026-10-02. Started with Ache 2019, Klapoetke 2017, von Reyn
2014/2017, Namiki 2018, Koenig/Ikeda 2007 and Kadas 2019. Inspected publisher
supplement inventories, primary full text via PMC/Europe PMC where accessible,
author-uploaded paper text and data-availability statements. Publisher access was
intermittent; unavailable acquisition details remain unknown, not inferred.

DataCite title and GF/LC4/LPLC2 metadata queries led to Dombrovski 2025 and its
linked Zenodo/OSF archives, a bounded expansion specifically because they contain
the desired assay. Zenodo and OSF official API inventories and license records were
checked. Supplementary tables/images/videos are not automatically raw traces.

| Search location | Result / exclusion |
| --- | --- |
| DataCite | GF query returned 27 metadata records, LPLC2 9, LC4/Drosophila 7; exact three starting-paper title queries found no dataset records. Located relevant GF and LPLC2 deposits. |
| Zenodo | Record 14983850 has numerical GF MAT files; derivative Chai behavior archive excluded for assay mismatch. |
| OSF | z7xfk contains processed LPLC2 Rda and analysis Rmd; no raw movies in inspected root inventory. |
| Dryad | nc763 concerns another stimulation/muscle/behavior context; no qualifying upstream GF voltage record located. |
| Figshare / DANDI | No qualified record located in bounded indexed GF/LC4/LPLC2 queries; not exhaustive archive-wide absence. |
| Janelia / lab repositories | Publication and anatomical/driver resources, no additional qualified raw GF trace deposit located. |
| GitHub / ModelDB | ModelDB 230400 and LoomDetectionANN inventories are code/figures, not located experimental GF time series. |
| GEO | Linked GSE291561 is transcriptomic; not a relevant voltage assay. |
| Mendeley | Dombrovski 2023 explicitly links confocal stacks; other data by request. Not GF raw voltage deposits. |

Exact query/source/date/results are in the JSON `search_log`. A negative search
means **NOT_LOCATED within scope**, not proof of absence. Primary publications,
archive metadata and inspected file structures are distinguished throughout.

## Candidate compatibility table

Full required metadata, exact source/target enums and gate reasons are in the
[machine-readable audit](gf_voltage_dataset_compatibility_audit.json).

| Candidate | Source condition / target | Data actually available | Classification |
| --- | --- | --- | --- |
| `dombrovski_gf_zenodo_14983850` | Natural looming with pathway context; GF type with limitations | Numerical trial-labelled/combined MAT, summary XLSX; two arrays inspected | `METADATA_INSUFFICIENT` |
| `dombrovski_lplc2_osf_z7xfk` | LPLC2-matched calcium; **not GF voltage** | Processed Rda and Rmd | `SUFFICIENT_FOR_OPERATOR_DESIGN_ONLY` |
| `ache_2019_gf` | Looming plus LC4/LPLC2 silencing; GF | Protocol, figures; data by request | `SUFFICIENT_FOR_OPERATOR_DESIGN_ONLY` |
| `klapoetke_2017_gf_opto` | LPLC2-selective population optogenetics; GF | Protocol and plotted responses; no numeric GF traces located | `SUFFICIENT_FOR_OPERATOR_DESIGN_ONLY` |
| `von_reyn_2017_gf_lc4` | Visual/LC4 context; GF | Primary abstract; related simulation code, not raw physiology | `QUALITATIVE_ONLY` |
| `von_reyn_2014_gf` | Natural visual response, unresolved LC4/LPLC2 source | Abstract/supplement figure evidence | `QUALITATIVE_ONLY` |
| `modeldb_230400` | Simulation, not assay | MATLAB model, readme and two PNGs | `INCOMPATIBLE` |
| `namiki_2018_identity` | DNp01/GF anatomical identity | Driver/morphology tables/images | `INCOMPATIBLE` for voltage data |
| `koenig_ikeda_2007_g1` | Muscle physiology, not GF intracellular target | Physiological publication | `INCOMPATIBLE` |
| `kadas_2019_muscle` | Direct pathway stimulation; muscle output | Muscle AP evidence | `INCOMPATIBLE` |
| `dombrovski_2023_gf` | Natural looming, LC4 context; GF | Full acquisition protocol, figures; other data by request | `SUFFICIENT_FOR_OPERATOR_DESIGN_ONLY` |
| `jang_2023_gf` | Natural looming/bilateral context, unresolved LC4/LPLC2 activation; GF | Acquisition/analysis protocol; data by request | `SUFFICIENT_FOR_OPERATOR_DESIGN_ONLY` |

### Best available GF numerical candidate

[Dombrovski et al. 2025](https://doi.org/10.1038/s41586-025-09037-4) links the
[Zenodo GF deposit](https://zenodo.org/records/14983850) and
[OSF LPLC2 archive](https://osf.io/z7xfk/). Zenodo describes the data as corresponding
to the 2024 preprint v2, Fig. 1/Extended Data 1 and Fig. 3/Extended Data 8.
The final paper links the record, but a figure/file/genotype version bridge still
must be confirmed. Controls must not be silently pooled with DIP-epsilon mutant
or RNAi conditions.

The whole-cell target is identified GF in tethered flies, not a matched MaleCNS
body ID. Sex, exact compartment and acquisition metadata for these specific files
were not verified. The Fig. 1 protocol specifies three expanding disks, a 2 s
prestimulus baseline, a 150 ms response window and repeated randomized stimuli.
Those windows are **not automatically assigned to Fig. 3**. Animal/group counts,
trial file counts and repetitions are different quantities.

The 46-file inventory totals **32,794,129 bytes**: 44 individual MAT files, one
combined MAT and one XLSX. The two sampled MATLAB v5 files contain only named
double arrays: `(80000, 4)` and `(75, 80002)`. No explicit time vector or channel
dictionary was found embedded in those MAT files. Array dimensions alone do not
establish sampling or column semantics; the companion XLSX does explicitly map
the four individual-file columns to stimulus conditions. Paper-reported mV does
not independently establish the stored amplitude scale or conditioning.

`BEST_AVAILABLE_CANDIDATE` is based on lawful numerical availability and assay
relevance, **not** scientific truth, calibrated magnitude, or a winner forced
through failed gates. No candidate passes all Phase 20 gates.

### Source-specific and complementary datasets

[Ache et al. 2019](https://doi.org/10.1016/j.cub.2019.01.079) provides strong
natural-looming GF assay context with LC4/LPLC2 silencing. It reports female
somatic current-clamp, 20 kHz sampling and 10 kHz low-pass filtering. Public numeric
GF trial data were not located; request availability is not an acquired dataset.
LC4 necessity and GF waveform context do not supply measured per-body source
activity. [Von Reyn et al. 2017](https://pubmed.ncbi.nlm.nih.gov/28641115/) adds LC4
context; its [ModelDB entry](https://modeldb.science/230400) is simulation code.

[Klapoetke et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457385/) includes
GF current-clamp during LPLC2 population activation, with 40 kHz acquisition and
10 kHz low-pass filtering. Imaging/code are offered on reasonable request; that
statement is not evidence of a public raw GF deposit. LPLC2 optogenetic pulses
establish a source intervention, not its amplitude in NeuroFly sensory-state units.

The [OSF archive](https://osf.io/z7xfk/) contains `Dataframe_LPLC2_2025.Rda`
(35,914,499 bytes) and `AnalysisLPLC2.Rmd` (43,469 bytes), both under the project
CC-BY-4.0 license. Only the public index and Rmd were inspected remotely. Rmd
references time, deltaF, trial/animal/group and ROI position fields. The Rda was
not downloaded or parsed; raw-image availability is not established. Published
imaging and stimulus-marker rates are different clocks; marker existence alone
does not prove synchronization with GF files. Calcium filtering/ROI/baseline and
the `x_i` mapping remain unresolved. LC4 must not inherit this LPLC2 operator.

[Dombrovski et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9849133/) documents
female 2–4-day somatic current-clamp, 40 kHz sampling, 10 kHz low-pass, 2 s
baseline, 150 ms response windows and 4–8 averaged trials/neuron. A photodiode
was recorded simultaneously with voltage: a documented shared-clock protocol.
Publicly linked Mendeley datasets are confocal stacks; other data are by request.
These known **2023** methods must not be silently copied into the **2025** MAT
metadata without an explicit protocol/version bridge. Dombrovski 2025 also cites
[Jang et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10263144/) for acquisition:
that protocol uses 20 kHz sampling, female 2–5-day somatic recordings, a 1 s
prestimulus baseline and declared analysis smoothing. All Jang data/software are
by request. The referenced rate is useful provenance, but does not resolve the
clock or other acquired-file metadata by inference. The companion XLSX, however,
**directly** declares 20 kHz, four-second individual recordings, onset at two
seconds, columns 1–4 corresponding to r/v 10/20/40/80 ms, and exp/cont file labels.
This makes individual-file time alignment reconstructable without fitting.
It does not explicitly declare stored voltage scaling or acquisition filtering.
Its note confusingly calls the files “44 flies” while describing 22 animals with
two trials each; that wording is recorded, not silently treated as 44 animals.
The combined Fig. 1 array needs its own dictionary. The 13,886-byte spreadsheet
was inspected remotely in memory for ZIP members, string labels and metadata
rows; no response values were analysed and no local XLSX copy was retained.

GF-only stimulation, muscle output, anatomy, behavior and computed traces are
not interchangeable with visual or source-selective activation recorded in GF.
[Namiki et al.](https://elifesciences.org/articles/34272) supports GF/DNp01 type
terminology, not exact cross-animal body identity. [Koenig/Ikeda](https://pubmed.ncbi.nlm.nih.gov/17392409/)
and [Kadas et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6709211/) muscle assays
cannot substitute for GF membrane recordings.

## Unchanged Phase 20 gates

Each JSON candidate has explicit `PASS`/`FAIL`/`UNKNOWN` with reasons for the ten
requested relative-voltage checks and **exactly** these authority gates:

| Phase 20 gate | Principal unresolved requirement |
| --- | --- |
| `CELL_TYPE_AND_PREPARATION_MATCH` | GF type is supported; compartment/sex/preparation and model abstraction matching need explicit limits. |
| `SOURCE_POPULATION_AND_ROI_MAPPING` | Natural looming/population manipulation does not define individual `x_i` biological activity. |
| `STIMULUS_REFERENCE_MATCH` | Experimental visual/opto stimulus is not calibrated NeuroFly world_eq geometry. |
| `BASELINE_AND_UNITS_EXPLICIT` | Baseline and mV in paper may be known while trace columns/sample baseline remain unknown. |
| `OBSERVATION_TRANSFORM_ESTABLISHED` | Both source state and mV_eq voltage observation transforms remain absent. |
| `TEMPORAL_FILTER_AND_ALIGNMENT_DECLARED` | Individual Fig. 3 sampling/onset are explicit in XLSX; filtering and combined-array timing remain unresolved. |
| `AGGREGATION_AND_UNCERTAINTY_DECLARED` | Trial/animal/ROI and averaging must be known; animal N is not trial N. |
| `DATA_SUFFICIENCY_AND_IDENTIFIABILITY_ASSESSED` | Current files and mappings do not define a defensible numerical observation-space objective. |

Target-only GF neuron-type checks may pass while the complete model-to-assay gate
is unknown or fails. `PASS` for source condition means the intervention is known,
not that it measures source activity. Missing information is not a discovered
runtime bug or reason to revise the Phase 20 contract.

## Identifiability and missing-data specification

| Arrow | Updated status | Reason |
| --- | --- | --- |
| sensory state → presynaptic activity | `SUPPORTED_FOR_OPERATOR_DESIGN_ONLY` | LPLC2 calcium data inform measurement design; no `x_i`→activity scale. |
| presynaptic activity → postsynaptic effect | `QUALITATIVELY_SUPPORTED` | Population/pathway physiology supports relationship, not synchronized per-body efficacy. |
| postsynaptic effect → measured GF voltage | `SUPPORTED_FOR_OPERATOR_DESIGN_ONLY` | Numerical arrays and individual-file clock exist; stored scale/filter/protocol and model voltage transform remain unresolved. |

Separate OSF source and Zenodo target datasets cannot simply be paired to identify
`k`: interventions, clocks, ROIs, indicators, genotypes and population scales differ.
Do not divide GF response by source-cell count. Connectome contacts are not assay
weights. `mV_eq` is not biological mV; paper summaries cannot calibrate themselves.

The minimal future dataset requires identified LC4 and/or LPLC2 source population
with measured activity and explicit ROI/body coverage, identified GF intracellular
voltage and compartment, synchronized stimulus/source/target markers, baseline
sample definitions, units, sampling/filtering/resampling, genotype/preparation/sex,
repeated animal/trial traces, uncertainty and held-out trial structure, plus lawful
open numeric files with channel dictionaries and checksums. No new numeric rate,
gain or stimulus parameter is selected here. A parser would be a future scoped
MAT/Rda ingestion task after semantics are established, not a new dependency now.

## Local acquisition and integrity

Before downloading, verified `git check-ignore -v` for the intended existing
cache, matching `.gitignore` rule `data/derived/experiments/`. It is an audit-only
cache, not a generated experiment or runtime source. No new raw-data tree was added.
Source MAT bytes were not altered. Existing SciPy inspected only headers and
variable names/shapes/types; no new dependency was installed. No archive extraction.

| Ignored file under `data/derived/experiments/phase21_dataset_audit/` | Bytes | SHA-256 |
| --- | --- | --- |
| `DipE_Null_cont_fly22_trial01.mat` | 488,398 | `08035f5f79e94f6a215aae3ca44aa26f1d4edbff63a221eb90af3b5d03d6ae54` |
| `Fig1_Ext1_combined_GFMembraneP_HorizontalArrayLooming.mat` | 12,487,834 | `042224491f18f68f63cb829141d31fcb136a70e299ca0b64f3bb5c709e832740` |

Both MD5s match the official Zenodo file inventory. Source content URLs, CC-BY-4.0,
acquisition date, sizes, checksums and relative local paths are in the JSON manifest.
No local absolute paths or copyrighted source bytes occur in tracked metadata.

## Machine-readable identity and verification

Schema: `gf_voltage_dataset_compatibility_audit_v1`.
Audit canonical SHA-256 / ID:
`219622b71f1fd79caabe83665ddc859699875177883e7810c1b2bea4676e627d`.
The formatted JSON document is 82,553 bytes; canonical audit-object bytes are
64,062. Hash applies to the `audit` object
using the existing canonical JSON helper; the
wrapper ID is excluded. This is evidence metadata, not a simulation artifact.
Focused tests validate identity/mutation detection, Phase 20 hash/gate authority,
unique candidates, populated records, valid classifications, no calibration with
failed/unknown gates, no fitting and ignored/untracked acquisition destinations.
Source acquisition is not required to run these metadata tests.

Next bounded action: **obtain the authoritative stored-voltage scale/filtering,
recording metadata and combined-array/version dictionary for Zenodo 14983850**,
confirming the known individual-file clock/trial mapping. No author message was
sent in this phase. No
calibration protocol or fitting is yet authorized by this audit.

Phase 21 `PASS`: four focused metadata tests; full Python suite 1,026 passed,
one existing deselection and two dependency deprecation warnings (580.57 s).
All 53 frontend regression tests, lint/typecheck/build, Python Ruff/check-format
and `git diff --check` passed. All five historical replays passed both before
research and after metadata work. An initial full-suite run was interrupted
after a transient metadata-hash failure during an in-progress audit edit;
the complete frozen-file rerun passed. No scientific source mismatch occurred.
Only the four intended Phase 21 files remain changed/untracked; no commit/push.
