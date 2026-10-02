# Phase 22 — Zenodo 14983850 GF recording metadata resolution

## Outcome

Decision: `TARGET_GF_METADATA_REMAINS_INSUFFICIENT`.
Candidate `dombrovski_gf_zenodo_14983850` remains `METADATA_INSUFFICIENT`.
The trial/group dictionary and cohort metadata are better specified, but stored
voltage scale, file-specific acquisition/processing filters and combined-array
semantics remain unknown. No previously `UNKNOWN` target-voltage gate can be
upgraded to `PASS` on the inspected evidence. This is not a negative result about
the recordings' scientific value, and not permission to assume missing metadata.

No fitting, waveform statistics, numerical model comparison, gain calculation,
trace digitization, source MAT rewrite, production-model change or author contact.
The unresolved `x_i`→biological LC4/LPLC2 activity operator remains separate.

## Repository and immutable authorities

Started clean at `7b44a63c1d708f18e04018e38d71d2bfb8f195ce`, with
`main == origin/main`; required Phase 21/20/19/18 commits verified.
The unchanged [Phase 21 audit](gf_voltage_dataset_compatibility_audit.json) hashes
to `219622b71f1fd79caabe83665ddc859699875177883e7810c1b2bea4676e627d`.
The unchanged [Phase 20 operator contract](observation_operator_assay_compatibility.json)
hash is `ae50e1faad223cdde63125a6216ce0993523f9933025fe1f04e9265450dec824`.
Phase 22 is a new evidence record; neither historical document is rewritten.

Required offline replays passed before research/edits: Phase 18, corrected 16,
13B, full numerical 7O and genuine 8C, all with unchanged canonical identities.

## Source integrity and structure

Both local files were located through Phase 21 acquisition metadata, not guessed.
Their bytes and SHA-256 match the historical audit and their remote MD5 matches
the [official Zenodo inventory](https://zenodo.org/api/records/14983850).
Git-ignore coverage was explicitly verified before inspection.

| Ignored source file under `data/derived/experiments/phase21_dataset_audit/` | Bytes | SHA-256 |
| --- | --- | --- |
| `DipE_Null_cont_fly22_trial01.mat` | 488,398 | `08035f5f79e94f6a215aae3ca44aa26f1d4edbff63a221eb90af3b5d03d6ae54` |
| `Fig1_Ext1_combined_GFMembraneP_HorizontalArrayLooming.mat` | 12,487,834 | `042224491f18f68f63cb829141d31fcb136a70e299ca0b64f3bb5c709e832740` |

MATLAB v5/PCWIN64 headers record export creation on 6 March 2025 at 17:23:17
and 12:49:59 respectively. Those are **not experiment dates**. Existing SciPy
`whosmat` inspected variable names, dimensions and types only:

| Representation | Variable | Shape / type | Embedded metadata |
| --- | --- | --- | --- |
| Individual trial-labelled file | `DipE_Null_cont_fly22_trial01` | `(80000, 4)`, double | No additional structures, time vector or named metadata fields |
| Combined Fig. 1 file | `combined_T` | `(75, 80002)`, double | No additional structures, time vector or axis dictionary |

Do not infer what the combined array's extra columns or 75 rows represent.
Its name associates it with Fig. 1/Extended Data 1, not a documented row-level
animal/trial/elevation map. Raw/processed, averaging, concatenation, subtraction,
offset correction, filtering and axis meanings remain unverified. The paper's
five-animal/five-trial context does not authorize reverse-engineering its rows.
Prefer the better documented individual files for any future design.

## Authoritative metadata inspected

Sources are recorded with URLs/locators in the [resolution JSON](gf_voltage_dataset_metadata_resolution.json):

- Zenodo record description, license and full 46-file inventory; no README located.
- Companion `ephys original data for Fig.3 and Ext data Fig.8 .xlsx`, Sheet1
  B1–B3 and filename/condition rows; inspected in memory, no source copy retained.
- [Dombrovski et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12350164/),
  electrophysiology methods, Fig. 3h/i and Extended Data 8a–d, data availability.
- [Supplementary Table 1](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-025-09037-4/MediaObjects/41586_2025_9037_MOESM1_ESM.xlsx),
  genotype rows 125–136; remotely inspected worksheet metadata, not response values.
- [Reporting Summary](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-025-09037-4/MediaObjects/41586_2025_9037_MOESM2_ESM.pdf),
  page 4, Laboratory animals/Reporting on sex; visually inspected, no OCR.
- [Published source-data ZIP](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-025-09037-4/MediaObjects/41586_2025_9037_MOESM4_ESM.zip),
  archive members, sheet names/string labels for Fig. 1/3 and Extended Data 1/8.
- [Jang et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10263144/), the explicitly
  cited acquisition protocol; its other processing choices are not silently inherited.

The first attempted legacy supplement host did not resolve, including an escalated
retry. Europe PMC's supplement bundle timed out; publisher HTML provided working
official `media.springernature.com` links. Thus the relevant supplements were
accessed, rather than declaring them absent because a mirror failed.

## Stored voltage scale and processing

**UNKNOWN** for both selected MAT representations. Published peak/area summaries
are labelled physiological mV and mV×ms. Those labels do not explicitly establish
the units of the stored MAT numbers, an ADC/amplifier conversion, or their export
processing history. No range/minimum/maximum/waveform appearance was used to infer
scale. No `mV_eq`↔biological mV correspondence is claimed.

The acquired workbook establishes timing and column conditions, not a voltage
conversion. The source-data spreadsheets provide figure summaries, not an explicit
raw-array unit declaration. Baseline subtraction, offset/junction correction and
whether scaling changed between raw export and published summaries remain unknown.

| Component | Status for individual stored traces | Evidence / limitation |
| --- | --- | --- |
| Hardware acquisition filter | UNKNOWN | File-specific bandwidth/cutoff not located |
| Amplifier settings | UNKNOWN | MultiClamp 700B in referenced method; file-specific gain/filter settings absent |
| Acquisition sampling | PASS | Dataset workbook explicitly states 20 kHz |
| Offline low/high-pass | UNKNOWN | Stored-array processing not specified |
| Smoothing | UNKNOWN | Referenced Jang analysis smoothing does not establish processing of these MAT bytes |
| Published averaging | PASS | Figure legends document animal means over two recordings; not proof stored arrays are averaged |
| Resampling | UNKNOWN | No author-declared export/resampling history |

No 10 kHz cutoff is copied from another preparation or inferred from 20 kHz sampling.
The exact acquisition filter must remain unknown until dataset-specific evidence exists.

## Timebase and baseline

For the **individual Fig. 3/Extended Data 8 files**, workbook B1 states 20 kHz,
four seconds, 80,000 samples, stimulus onset two seconds after recording start.
Array row count is consistent: `80000 / 20000 = 4 s`. The reconstructed sample
interval is 0.05 ms. This is recording resolution, not NeuroFly's 0.1 ms timestep.
No resampling, waveform alignment or timestamp matching was performed.

Two seconds of prestimulus data are available. The first-sample timestamp convention,
stored subtraction/offset history and the exact future baseline statistic require
explicit declaration. Experimental stimulus onset is not automatically NeuroFly
scenario time zero. The combined array does not inherit this timebase merely because
one dimension resembles 80,000 samples. Fig. 1's published baseline/response window
does not prove the combined array's stored processing.

## Trial, condition, genotype and figure mapping

All 44 workbook filenames exactly match the 44 individual MAT entries in Zenodo:
no missing, extra or duplicate filename. The JSON preserves all 44 mappings.
Each file contains four columns for stimulus `r/v = 10, 20, 40, 80 ms` in that order.
Each animal has `trial01` and `trial02`. A distinct recording/session ID is not
provided beyond those animal/trial labels; do not invent one.

| Filename group | Animal IDs | Individual files | Published group/panels |
| --- | --- | --- | --- |
| `DipE_RNAi_exp` | fly01–fly05 | 10 | GF DIP-ε RNAi; Fig. 3i, Extended Data 8c–d |
| `DipE_RNAi_cont` | fly06–fly10 | 10 | GF control RNAi; same panels |
| `DipE_Null_exp` | fly11–fly17 | 14 | DIP-ε null; Fig. 3h, Extended Data 8a–b |
| `DipE_Null_cont` | fly18–fly22 | 10 | Wild-type control; same panels |

Genotype table rows 125–136 specify GF targeting with VT042336-GAL4 and GFP
markers. They distinguish null versus wild-type controls, and DIP-ε RNAi
(VDRC #103497) versus mCherry control RNAi (BDSC #35787). The JSON preserves
the reported components and source rows, not an invented complete allelic sequence.
`DipE_Null_cont_fly22_trial01` belongs to the null-comparison **control**, not a
null-mutant trial. Never pool controls with mutants/RNAi or both control designs.

Panel association uses matching author group labels/table/legends, not numerical
trace matching. The exact plotted line identity, trial exclusion and derived-value
processing remain unknown. The combined array has no such trial dictionary.

### Workbook ambiguity

Classification: `RESOLVED_BY_OTHER_AUTHORITATIVE_METADATA` for the usable counting
interpretation. B2 says “44 flies” but then “22 flies” with two trials. The original
wording is not corrected. Workbook identities and file inventory establish 22
animals/44 files; published counts 5+7+5+5 and two recordings/animal corroborate it.
No author erratum was located. The original textual inconsistency is retained,
while 44 files are not misrepresented as 44 independent biological animals.

## Preparation and source condition

The current study's reporting summary explicitly establishes **female** flies,
aged **3–7 days**, for electrophysiology. Do not import 2–5 days from an earlier
paper as the age of this cohort. Species is Drosophila melanogaster; the study
reports in vivo whole-cell current-clamp on behaving tethered flies. The explicitly
referenced method targets GF soma with patch electrodes. This is method-level
compartment provenance, not an independent per-file anatomical reconstruction.
A dataset-specific compartment deviation, recorded GF side and amplifier settings
are not provided. Rearing temperature is not recording temperature.

MaleCNS is male: the female preparation is an explicit compatibility limitation,
not an automatic rejection and not exact body-ID correspondence.

These are natural visual looming conditions, with null/RNAi pathway context and
appropriate controls. The published method specifies the cylindrical visual
display; the workbook specifies four r/v conditions. Exact selected trial bearing,
angular endpoints and stimulus-marker channels need file-specific confirmation.
LC4/LPLC2 activity is not measured in these files; GF manipulation does not become
source-matched LC4/LPLC2 activation.

## Version bridge

Zenodo associates the deposit with preprint DOI `10.1101/2024.09.04.610846v2`.
The final Nature paper explicitly references the same Zenodo dataset DOI. That
publication-level bridge and matching group/panel labels are verified, not a
complete preprint-to-final raw-export processing history. Header/export dates are
not acquisition dates. Row-to-panel/version mapping of `combined_T` remains unknown.

## Exact target-voltage gate reevaluation

These are the same ten keys as the Phase 21 target checks, interpreted under
unchanged Phase 20 authority. They apply to selected **individual** files only.

| Gate | Status | Reason |
| --- | --- | --- |
| Compatible GF target | PASS | Identified GF type; exact MaleCNS body identity not claimed |
| Baseline | PASS | Declared prestimulus data; stored subtraction history still unknown |
| Relative-deflection scale | UNKNOWN | Raw stored unit/conversion/offset history absent |
| Time axis | PASS | Explicit 20 kHz / 4 s, structurally consistent |
| Stimulus reference | PASS | Explicit two-second onset |
| Filtering metadata | UNKNOWN | Dataset-specific acquisition/offline filters absent |
| Stored measurement units/scale | UNKNOWN | Published summary mV does not certify raw MAT scale |
| Preparation | PASS | In vivo whole-cell tethered GF; female/age now explicit |
| Cell identity | PASS | GF type and targeting genotype documented |
| Source condition | PASS | Natural looming/group context; not presynaptic activity calibration |

Previous and new candidate classification: `METADATA_INSUFFICIENT`.
Additional cohort/group metadata do not upgrade an already-PASS type/preparation
gate; unresolved scale/filter requirements do not become PASS by implication.
No readiness downgrade/upgrade is forced just to claim progress.

The full Phase 20 source mapping and observation-transform gates remain unmet.
Even perfect GF target metadata would not establish `x_i`→presynaptic activity or
identify `k`. No coefficient, offset, normalization or relative efficacy was selected.

## Resolution identity and local safety

Schema: `gf_voltage_dataset_metadata_resolution_v1`.
Canonical ID/SHA-256 of the `resolution` object:
`b40c260a4a37ef99853425dfb927aa2729c6f93da8abd6de66d6c7ead2654ee4`.
Formatted JSON: 39,892 bytes; canonical resolution-object bytes: 30,156.
Wrapper identity is excluded from canonical hashing.
This is metadata/evidence, not simulation output; no runtime dependency.

The reporting-summary PDF (1,722,679 bytes, SHA-256
`2783c6b6c099b6efe4d067c3adbc3f30827bee8bd7c45e854d5331e34930051e`)
and two render-only inspection pages remain under existing ignored
`data/derived/experiments/phase22_metadata_audit/`. The publisher reporting summary
and article are CC-BY-4.0. No source PDF/PNG/MAT bytes are tracked or staged.
All worksheet/ZIP inspections were in memory. No normalized trace copies exist.

Four focused tests verify identity/tamper detection, immutable Phase 21 authority,
exact file hashes, identical gate keys/enums, no silent calibration, storage safety,
complete 44-file dictionary and separation of the undocumented combined array.

Exactly one next action: request one author-confirmed export/acquisition dictionary
covering stored voltage units/conversion/filtering and `combined_T` axes/processing,
with file-specific protocol/version mapping. No message was sent in this phase.

Phase 22 `PASS`: four focused tests, 1,030 full Python tests passed (one existing
deselection, two dependency deprecation warnings; 565.39 s). All 53 frontend
regression tests, lint/typecheck/build, Ruff/check-format and `git diff --check`
passed. All five required historical replays passed before research and again
after the metadata record was frozen. Phase 21/20 hashes and both raw MAT hashes
remain unchanged. Only the four intended Phase 22 files are visible; no commit/push.
