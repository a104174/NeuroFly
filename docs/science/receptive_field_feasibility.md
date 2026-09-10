# Phase 1D-B — bounded MaleCNS body-to-column feasibility validation

**Audit date:** 2026-09-10/11

**Candidate:** `looming_giant_fiber_v1`

**Dataset:** `male-cns:v1.0`

**Endpoint:** `https://neuprint.janelia.org`

This is a model-neutral feasibility audit, not a receptive-field dataset or a
production mapper. It uses the frozen deterministic 16-body sample from the
validated Phase 1B `CircuitContract`. No body was resampled, no skeleton was
retrieved, and no neural dynamics or structural-to-physiological conversion was
introduced.

## Decision summary

| Population | Decision | Scientifically supported boundary |
| --- | --- | --- |
| LC4 | **D3** | Body-specific input-column distributions are reproducible; a validated MaleCNS column-to-visual-space transform is not publicly machine-readable. |
| LPLC2 | **D3** | Body-specific input-column distributions are reproducible; a validated MaleCNS column-to-visual-space transform is not publicly machine-readable. |

The justified future encoder boundary is therefore **B: body-specific
column-space encoding, but not visual-angle encoding**. Phase 1D-B does not
implement that encoder.

## Repository and offline baseline

- branch: `main`, tracking `origin/main`;
- HEAD at audit start: `25f30d24f8bb6a30c06a71090a5ea7156803a442`;
- initial `git status --short`: one related pre-existing modification,
  `M docs/science/receptive_field_feasibility.md` (a one-line HEAD refresh from
  the already-started offline Phase 1D-B work); no unrelated changes;
- `NEUPRINT_APPLICATION_CREDENTIALS` availability: `true`; only this boolean
  was inspected;
- the ignored snapshot at
  `data/derived/malecns/looming_giant_fiber_v1/` passed
  `python -m neurofly.malecns inspect-snapshot`: SHA-256 and record counts
  verified, 313 neurons and 20,607 induced chemical edges.

The stable `CircuitContract` remains unchanged. It has no receptive-field,
visual-angle, or encoder fields.

## Frozen sample and Gate A identity validation

The sample is the existing SHA-256-ranked sample. Live values for every body
matched the validated snapshot on `bodyId`, `type`, `instance`, `somaSide`,
`status`, and `superclass`.

| Type | Side | Body ID | Instance | Status | Superclass | Live result |
| --- | --- | ---: | --- | --- | --- | --- |
| LC4 | L | 35616 | `LC4_L` | `Traced` | `visual_projection` | match |
| LC4 | L | 18432 | `LC4_L` | `Traced` | `visual_projection` | match |
| LC4 | L | 524899 | `LC4_L` | `Traced` | `visual_projection` | match |
| LC4 | L | 30087 | `LC4_L` | `Traced` | `visual_projection` | match |
| LC4 | R | 16138 | `LC4_R` | `Traced` | `visual_projection` | match |
| LC4 | R | 23098 | `LC4_R` | `Traced` | `visual_projection` | match |
| LC4 | R | 19954 | `LC4_R` | `Traced` | `visual_projection` | match |
| LC4 | R | 19260 | `LC4_R` | `Traced` | `visual_projection` | match |
| LPLC2 | L | 20329 | `LPLC2_L` | `Traced` | `visual_projection` | match |
| LPLC2 | L | 18936 | `LPLC2_L` | `Traced` | `visual_projection` | match |
| LPLC2 | L | 524366 | `LPLC2_L` | `Traced` | `visual_projection` | match |
| LPLC2 | L | 30893 | `LPLC2_L` | `Traced` | `visual_projection` | match |
| LPLC2 | R | 26915 | `LPLC2_R` | `Traced` | `visual_projection` | match |
| LPLC2 | R | 21808 | `LPLC2_R` | `Traced` | `visual_projection` | match |
| LPLC2 | R | 19034 | `LPLC2_R` | `Traced` | `visual_projection` | match |
| LPLC2 | R | 20471 | `LPLC2_R` | `Traced` | `visual_projection` | match |

No body was replaced.

## Gate B — body-specific visual input anatomy

### Deterministic territory and counting rule

The published MaleCNS method maps visual-projection-neuron **input synapses**
to optic-column ROIs. Accordingly, the relevant territory is defined as each
sampled visual projection neuron's `post` synapses whose primary ROI is a
descendant of the matching-side `Optic(L)` or `Optic(R)` hierarchy in the live
MaleCNS metadata. This is an anatomical rule; it uses no coordinate cutoff and
does not select results by outcome.

Synapses were fetched with neuPrint `SynapseCriteria(type="post",
primary_only=True)`. A primary ROI is non-overlapping, so every returned row is
one synapse even though the underlying MaleCNS synapse has hierarchical ROI,
layer, and column properties. `compartment` was inspected but not used as a
filter: excluding optic-lobe `linker` or `cell-body-fiber` annotations would add
an unsupported classifier threshold. Synapses in `Optic-unspecified` or AME
remain relevant but unassigned when they lack a column.

A relevant synapse is assigned only when both direct MaleCNS fields `olHex1`
and `olHex2` are present and the corresponding official
`ME_<side>_col_<hex1>_<hex2>` row exists. Its actual ME/LO/LOP column ROI key
must have the same side and hex suffix. Partial hex pairs, unknown official
IDs, key mismatches, and multiple column keys are counted separately. This
audit found zero in all four categories.

The two centroid coordinates below are weighted arithmetic means of the
dimensionless `olHex1`/`olHex2` indices. They are
`neurofly_derived input_column_centroid`, not receptive-field centers or visual
angles. Ranges are occupied column-index ranges, not angular extents.

### LC4 results

| Side | Body | All post | Relevant optic input | Official-column assigned | Fraction | Columns | Unassigned | Primary optic ROIs | Input-column centroid | Hex range |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| L | 35616 | 1,792 | 1,524 | 1,523 | 0.999344 | 49 | 1 | LO 1,523; unspecified 1 | (19.590, 19.724) | 15–23, 16–23 |
| L | 18432 | 1,986 | 1,662 | 1,662 | 1.000000 | 46 | 0 | LO 1,662 | (12.798, 18.851) | 10–16, 14–24 |
| L | 524899 | 2,406 | 2,078 | 2,077 | 0.999519 | 75 | 1 | LO 2,077; unspecified 1 | (31.201, 25.523) | 25–36, 20–31 |
| L | 30087 | 1,867 | 1,623 | 1,622 | 0.999384 | 41 | 1 | LO 1,622; unspecified 1 | (16.512, 26.985) | 13–21, 24–30 |
| R | 16138 | 2,336 | 2,063 | 2,061 | 0.999031 | 58 | 2 | LO 2,061; AME 2 | (17.894, 22.632) | 14–22, 18–27 |
| R | 23098 | 2,625 | 2,340 | 2,338 | 0.999145 | 59 | 2 | LO 2,338; unspecified 2 | (19.851, 17.173) | 15–24, 14–21 |
| R | 19954 | 2,806 | 2,499 | 2,498 | 0.999600 | 54 | 1 | LO 2,498; unspecified 1 | (14.404, 13.731) | 10–18, 10–18 |
| R | 19260 | 2,820 | 2,549 | 2,546 | 0.998823 | 69 | 3 | LO 2,546; unspecified 3 | (23.568, 19.540) | 19–29, 15–24 |

LC4 totals are 16,338 relevant input synapses, 16,327 assigned (0.999327),
and 11 unassigned. Every assigned LC4 synapse is in an LO column. All visual
ROIs are ipsilateral. The non-identical occupied ranges, distributions, and
centroids show reproducible body-specific column territories; they do not by
themselves establish angular receptive fields or physiological weights.

### LPLC2 results

| Side | Body | All post | Relevant optic input | Official-column assigned | Fraction | Columns | Unassigned | Primary optic ROIs | Input-column centroid | Hex range |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| L | 20329 | 2,199 | 1,759 | 1,756 | 0.998294 | 77 | 3 | LO 903; LOP 853; unspecified 3 | (21.647, 17.511) | 17–27, 13–22 |
| L | 18936 | 2,317 | 1,891 | 1,883 | 0.995769 | 71 | 8 | LO 770; LOP 1,076; ME 37; unspecified 8 | (25.331, 12.943) | 10–31, 6–30 |
| L | 524366 | 1,228 | 934 | 933 | 0.998929 | 48 | 1 | LO 385; LOP 548; unspecified 1 | (12.076, 26.386) | 7–17, 21–31 |
| L | 30893 | 1,439 | 1,175 | 1,159 | 0.986383 | 46 | 16 | LO 626; LOP 533; unspecified 16 | (7.363, 22.306) | 4–12, 13–29 |
| R | 26915 | 1,916 | 1,614 | 1,610 | 0.997522 | 70 | 4 | LO 595; LOP 1,015; unspecified 4 | (16.925, 23.958) | 12–22, 19–28 |
| R | 21808 | 2,601 | 2,205 | 2,200 | 0.997732 | 81 | 5 | LO 1,269; LOP 931; unspecified 5 | (33.471, 29.822) | 27–36, 24–38 |
| R | 19034 | 3,247 | 2,805 | 2,798 | 0.997504 | 86 | 7 | LO 1,326; LOP 1,472; unspecified 7 | (23.584, 18.851) | 17–29, 13–25 |
| R | 20471 | 2,487 | 2,072 | 2,067 | 0.997587 | 74 | 5 | LO 1,226; LOP 841; unspecified 5 | (31.530, 34.792) | 27–36, 28–39 |

LPLC2 totals are 14,455 relevant input synapses, 14,406 assigned (0.996610),
and 49 unassigned. Its input territory spans LO and LOP, with 37 ME inputs for
body 18936. All visual ROIs are ipsilateral. The bodies have distinct occupied
column ranges, distributions, and centroids. The unusually broad range for
18936 is retained as observed; no body or site is discarded for convenience.

## Gate C — official optic-column linkage

The official resource is
[`optic-column-type-assignments-v1.0.xlsx`](https://github.com/flyconnectome/2025malecns/blob/67767d2233657983993ff6c2be48e836a935863c/supplemental_data/optic-column-type-assignments-v1.0.xlsx)
from `flyconnectome/2025malecns`, inspected at commit
`67767d2233657983993ff6c2be48e836a935863c`. File size is 111,565 bytes;
SHA-256 is
`d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`.
It was read as XLSX ZIP/XML with the Python standard library; no project
dependency changed.

The workbook has three sheets:

- `Right OL`: 892 unique rows named `ME_R_col_<hex1>_<hex2>`;
- `Left OL`: 880 unique rows named `ME_L_col_<hex1>_<hex2>`;
- `READ ME`: field definitions and missing-value semantics.

Both data sheets have the schema `column`, `L1`, `R7`, `R7_type`, `R8`,
`R8_type`, `column_type`, `aMe12_branch`, `Tm5a_branch`, `Notes`.
`column_type` is one of `pale`, `yellow1`, `yellow2`, `edge`, `DRA`, or
`unclear`. The workbook defines L1, R7, and R8 as body IDs of those reference
cells assigned to a column; they identify/annotate the column and are not
LC4/LPLC2 receptive fields. `-99` means that no cell of that reference type
was found. Branch fields are binary anatomical markers used for column-type
classification.

MaleCNS synapses carry `olHex1`, `olHex2`, `olLayer`, and an ME/LO/LOP column
ROI key. ME, LO, and LOP keys share the exact side and two-coordinate suffix.
Replacing only the neuropil prefix with `ME` yields the workbook's column key.
For the sample, every synapse with a complete hex pair mapped to one of the
1,772 official rows; no malformed, unknown, contralateral, mismatched, or
multi-column assignment occurred. Primary-only ROI output prevented
hierarchical double counting.

## Column-to-visual-space transform audit

**Result: not found in a public, documented, machine-readable form that is
specifically compatible with bilateral `male-cns:v1.0`.**

Primary/official resources inspected:

1. Berg et al. preprint v2, Methods, “Eye maps for visual projection neuron
   spatial analysis” ([Europe PMC full text](https://europepmc.org/articles/PMC12636603)).
   The method maps input synapses to column ROIs and displays counts on a new
   compound-eye map; Figure 4 uses a Mollweide projection. The method says the
   map is based on Zhao et al. but extended for MaleCNS medulla columns, with
   details in work “in prep.” It supplies no per-column coordinates, units,
   eye handedness/orientation, interpolation contract, or executable transform.
2. The official `flyconnectome/2025malecns` release above. Its current tree
   contains the column-type workbook but no eye-map coordinate table or
   transform implementation.
3. The official MaleCNS Cell Type Explorer repository at commit
   `789cc6c105798ce2fd70ba85dab394f90899616b`. It contains rendered type/side
   SVG eye maps, not a documented column-keyed transform. Those pixels/paths
   were not scraped or reverse-engineered.
4. Zhao et al., *Nature* (2025), DOI
   [`10.1038/s41586-025-09276-5`](https://doi.org/10.1038/s41586-025-09276-5),
   and the author repository `artxz/eyemap_T4`. That repository is a right-eye
   T4 study workflow with R data/index objects; it is not released with a
   bilateral `male-cns:v1.0` column-ID compatibility contract. It was not
   transferred into NeuroFly.

Thus the published representation is a Mollweide visual-field map, but its
MaleCNS column-to-map coordinates, angular units/orientation, bilateral
handedness, and interpolation procedure are not reproducible from a released
machine-readable artifact. No visual-space quantity is computed here.

## Gate D — morphology

Gate D did not run. Gates B/C already establish reproducible body-specific
input-column topology, while skeleton morphology cannot supply the missing
published eye-map transform. Skeletons retrieved: **0**. Healing was neither
requested nor performed; any future bounded skeleton call remains required to
use `heal=False`.

## Live acquisition volume

- distinct bodies queried: **16**;
- full primary-only postsynaptic table: **36,072 unique records**;
- schema probe before the full table: **3 postsynaptic rows**, duplicated in
  the full table, so **36,075 synapse rows were transferred in total**;
- body/column aggregate rows used for independent reconciliation: **1,290**
  (server-side counts, not additional raw synapse records);
- skeletons retrieved: **0**;
- meshes, EM volumes, whole-population tables, and bulk downloads: **0**.

Query categories were exact-ID identity annotations, one-body synapse schema,
16-body primary-only postsynapses, live ROI hierarchy metadata, and exact-ID
body/column aggregation. No LC4/LPLC2 population-wide synapse query occurred.

## Provenance separation

### `malecns_direct`

`bodyId`, type, instance, `somaSide`, status, superclass, postsynaptic site,
primary ROI, synapse coordinates, compartment, `olHex1`, `olHex2`, `olLayer`,
and exact column ROI membership.

### `published_derived`

The versioned official column workbook, its column-type/reference-body
annotations, the published input-synapse-to-column method, and the published
statement that Figure 4 uses a Mollweide eye-map representation.

### `neurofly_derived`

The frozen SHA-256 sample rank; relevant-input selection under the published
anatomical rule; per-body counts, assigned fractions, sparse column
distributions, distinct-column counts, and `input_column_centroid` summaries;
the D3 decisions and encoder-boundary consequence.

No NeuroFly-derived value is represented as a MaleCNS field.

## Scientific safeguards and limitations

- No receptive-field center, azimuth, elevation, visual polygon, or angular
  extent was invented.
- No body ID, soma location, node order, soma side alone, DNp01 connection, or
  downstream topology was used as a spatial shortcut.
- No FAFB/FlyWire or other cross-dataset body/coordinate mapping was used.
- `ConnectsTo.weight` remains structural only; it was not used in this audit or
  transformed into physiology.
- No skeleton was healed, merged, repaired, or interpreted for signal flow.
- No neural dynamics, stimulus conversion, encoder, or receptive-field mapper
  was implemented.
- Column-index centroids describe topology only. The two axes have no claimed
  angular units or published visual orientation in this artifact.
- Small unassigned fractions are preserved. LPLC2 body 30893 has the largest
  unassigned fraction (1.36%); this uncertainty does not erase its reproducible
  assigned distribution.

## Smallest supported next phase

Specify and test a model-neutral **body-to-column sparse input distribution**
schema for LC4 and LPLC2, retaining source dataset/version, eye side, official
column key, counts, missing fraction, and provenance. Do not add visual-angle
fields until the MaleCNS-specific bilateral eye-map transform is released with
documented units, orientation, handedness, and identifier compatibility.
