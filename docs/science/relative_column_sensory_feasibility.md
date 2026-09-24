# Phase 7C — relative column-space sensory individualization feasibility

**Audit:** 2026-09-24. **Source:** `male-cns:v1.0`,
`looming_giant_fiber_v1`, `body_column_input_v1`.
**Decision:** `RELATIVE_COLUMN_INPUT_FEASIBLE`, **for a bounded synthetic
model experiment only**. No per-body sensory neural state, encoder change,
absolute visual angle, or functional receptive field is produced in this phase.

## Source and lattice boundary

The [Phase 1E body-column contract](body_column_contract.md) joins exact
CircuitContract body IDs to 25,438 sparse `(body, neuropil, side, hex1,
hex2, input_count)` records and 311 summaries. Its SHA-256-validated local
snapshot has 126 LC4 and 185 LPLC2 bodies, 574,745 assigned primary optic
postsynaptic sites, and 2,790 relevant but unassigned sites. The selection
rule remains `matching_side_optic_primary_post_v1`; neither records nor
summaries were altered. The source file hashes are
`column_inputs.jsonl = 4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e`
and
`column_body_summaries.jsonl = ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b`.
The [Phase 7B audit](bilateral_optical_registration_assessment.md) still
finds no validated bilateral column→optical-ray transform.

The [male optic-lobe publication](https://www.nature.com/articles/s41586-025-08746-0)
defines p/q hexagonal coordinates and extends the same column indices from
medulla into LO/LOP. The [pinned coordinate-system description and
diagram](https://github.com/reiserlab/visualpathways/blob/23f6ac131529b5f56894c6eeb9b88b17894fc00d/docs/coordinate-systems.md)
identify `hex1=q`, `hex2=p`, a conventional origin `(18,19)`, and axes of a
six-neighbour lattice. Its [coordinate diagram
PDF](https://raw.githubusercontent.com/reiserlab/visualpathways/23f6ac131529b5f56894c6eeb9b88b17894fc00d/docs/column_coord.pdf)
was inspected read-only (24,146 B; SHA-256
`7d3214e5251307462f63fbab6aef77709b4e8cb62ec6bc23e00238a3daece385`).
The neighbouring coordinate offsets are ±(1,0), ±(0,1), ±(1,1); for
`Δq=Δhex1`, `Δp=Δhex2`, shortest lattice distance is
`max(|Δp|, |Δq|, |Δp−Δq|)` steps. A disk radius means **lattice steps**, not
Euclidean EM distance or degrees. The left and right coordinates are handled
as independent grids; no mirrored angle, common azimuth sign, or physical
cross-eye alignment is inferred.

The pinned [official column workbook](https://github.com/flyconnectome/2025malecns/blob/67767d2233657983993ff6c2be48e836a935863c/supplemental_data/optic-column-type-assignments-v1.0.xlsx)
has 880 L and 892 R *medulla* rows (SHA-256
`d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`).
An offline join found **18 valid source LO/LOP records, 713 input sites, at
two left hexes `(17,34)` and `(19,35)` absent from that workbook**. This is
not a side or snapshot-integrity failure: the Phase 1E source validates its
LO/LOP ROI keys, while the workbook is a medulla-column classification
table. Those records remain in centroids and exposures; their workbook edge
class is `unclassified`, not silently non-edge. They are included in the
synthetic lattice universe as source coordinates. The code refuses an
un-pinned workbook hash.

## Offline analysis and anatomical definitions

The non-runtime [research helper](../../research/relative_column_space.py)
loads the hash-validated source and CircuitContract, parses the pinned
workbook, and deterministically writes the ignored
`malecns_relative_retinotopy_analysis_v1` JSON. Each of 311 body rows
retains exact body/type/side, record and unique-hex counts, assigned and
missing-site fractions, unweighted and structural-input-weighted coordinate
centroids, lattice-norm RMS spreads, and edge fraction **among workbook-
classified hexes**. A centroid may lie between columns and is not a source
column, optical ray, or functional RF centre. Spread is in *relative lattice
steps* under the stated metric. Input-site weighting describes anatomical
occupancy only.

For a named active set of same-side lattice hexes `S`, the helper reports:

1. `any_source_column_overlap`: binary presence/absence of at least one
   matching source record;
2. `source_column_overlap_fraction`: matching `(neuropil, hex)` records over
   all associated records (mean of the per-record binary indicators);
3. `unique_hex_occupancy_overlap_fraction`: matching unique hex locations
   over all occupied hex locations, collapsing ME/LO/LOP duplicates;
4. `structural_input_site_overlap_fraction`: assigned source input sites at
   active locations divided by all assigned source sites for the body.

These are **anatomical exposure statistics**, never measured drive, response
probability or firing gain. Missing/unassigned source sites remain outside
the denominator of the structural fraction and are reported separately.
Opposite-side exposure is exactly zero by explicit stimulus-side identity,
not by an inferred optical field-of-view boundary. Stimuli name their side,
centre source hex, integer radius and active official-or-source hex set.

## All-body structural topology

The table summarizes the complete ignored analysis. Centroid ranges are
unweighted `(hex1,hex2)` ranges across bodies; spread is median unweighted
RMS in lattice steps. All 311 detailed rows, including weighted centroids and
spreads, are in the hash-identified derived JSON. `occupied/official` reports
the fraction of *workbook* hexes touched by at least one body in that group;
source-only LO/LOP coordinates are counted separately.

| Type/side | Bodies | Source columns/body min–median–max | Assigned fraction min–median–max | Missing sites | Centroid hex1 range / hex2 range | Median RMS steps | Occupied official hexes | Bodies/occupied hex median–max | Edge fraction median–max |
| --- | ---: | --- | --- | ---: | --- | ---: | ---: | --- | --- |
| LC4 L | 71 | 36–53–75 | .9716–.9991–1 | 353 | 4.52–32.89 / 4.03–35.72 | 3.16 | 865/880 | 4–9 | 0–.205 |
| LC4 R | 55 | 45–63–85 | .9965–.9994–1 | 102 | 4.52–32.77 / 3.89–35.62 | 3.50 | 875/892 | 4–8 | 0–.194 |
| LPLC2 L | 94 | 54–95–146 | .9354–.9914–1 | 1,598 | 4.69–33.27 / 4.58–36.01 | 3.46 | 871/880 | 7–14 | 0–.155 |
| LPLC2 R | 91 | 58–103–138 | .9826–.9963–.9996 | 737 | 4.48–32.78 / 3.93–36.21 | 3.56 | 883/892 | 7–16 | 0–.172 |

These broad, overlapping anatomical territories cover much of the indexed
lattice. Multiple same-type bodies occupy many hexes; this is not evidence
for one-neuron-per-column tiling or a functional sensitivity map. Edge class
is missing for the two source-only left coordinates; its per-body fraction
uses the classified subset only. The 15 LC4-L and LPLC2-L body-level
unclassified-hex occurrences are retained, not mistaken for 15 distinct
coordinates.

### Four-body continuity

| Body | Source columns | Assigned/relevant sites | Unweighted centroid | Structural-weighted centroid | Unweighted RMS steps |
| --- | ---: | ---: | --- | --- | ---: |
| LC4 12032 L | 75 | 2,436/2,477 | (32.89, 31.24) | (33.47, 30.73) | 4.47 |
| LC4 16128 R | 66 | 3,709/3,710 | (22.18, 10.23) | (22.62, 10.08) | 3.57 |
| LPLC2 11498 L | 95 | 1,254/1,263 | (15.22, 6.74) | (15.95, 5.98) | 7.93 |
| LPLC2 14465 R | 105 | 1,854/1,859 | (23.31, 12.16) | (23.65, 12.00) | 3.33 |

Source counts and weighted centroids reproduce [Phase 7A's four-body
descriptive proof](bilateral_retinotopy_feasibility.md). The two components
of 11498 morphology are not separate sensory input identities.

## Bounded synthetic proof — no neural dynamics

The eight body IDs were fixed before evaluating stimuli: the four continuity
bodies above plus the next numerical ID in each type/side stratum (`LC4`
12349 L, 16138 R; `LPLC2` 12384 L, 17551 R). Explicit, synthetic same-side
disks use `(L,33,29)` radius 1→4 (an expanding-disk sequence), translated
left centre `(18,4)` radius 2, `(R,23,9)` radius 1→4, and translated right
centre `(23,11)` radius 2. Each centre is an official source column. No
physical looming trajectory is represented. The table shows source-record
overlap / structural-input-site overlap; the derived JSON also records unique-
hex overlap and binary overlap for every proof body.

| Stimulus (lattice steps) | Active hexes | LC4 12032 L | LC4 16128 R | LPLC2 11498 L | LPLC2 14465 R |
| --- | ---: | ---: | ---: | ---: | ---: |
| L `(33,29)`, r1 | 7 | .093 / .161 | 0 / 0 | 0 / 0 | 0 / 0 |
| L `(33,29)`, r4 | 56 | .627 / .757 | 0 / 0 | 0 / 0 | 0 / 0 |
| L `(18,4)`, r2 | 13 | 0 / 0 | 0 / 0 | .211 / .390 | 0 / 0 |
| R `(23,9)`, r1 | 7 | 0 / 0 | .106 / .199 | 0 / 0 | .095 / .119 |
| R `(23,9)`, r4 | 44 | 0 / 0 | .652 / .822 | 0 / 0 | .533 / .670 |
| R `(23,11)`, r2 | 19 | 0 / 0 | .288 / .468 | 0 / 0 | .352 / .535 |

For right r4, the additional LPLC2 17551 R has .358 source-record and .398
structural-site exposure; the other three additional bodies have zero for
these selected disks. These are *stimulus-geometry examples*, not evidence
that any cell would fire, prefer looming, or have those RFs. Increasing radius
monotonically adds active columns. Translating a centre changes which source
territories overlap. The exact values are reproducible from the ignored
artifact and pinned source hashes.

## Functional evidence and transfer limits

**LC4.** [Dombrovski et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9849133/)
map dendritic territories for **55 female FAFB LC4** neurons into an
*estimated anatomical* eye-coordinate RF map, supporting population coverage
and an anatomy→position relation. Their pseudo-stimulus overlap model and
downstream recordings support a spatially organized circuit hypothesis, but
do not measure each MaleCNS LC4 body's RF centre, width, gain or transfer
function. Broad VPN RF estimates (roughly 20–40°) are not a per-body MaleCNS
kernel and cannot be converted to lattice steps without registration.

**LPLC2.** [Klapoetke et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457385/)
show individual LPLC2 neurons responding to outward motion centred on their
RFs, with a reported ~60° upper bound for individual RF size under their
stimuli. [Dombrovski et al. 2025](https://www.nature.com/articles/s41586-025-09037-4)
show dorsal/ventral positional organization and molecular/input-output
synaptic gradients; two right male optic-lobe LPLC2 examples are explicitly
identified. This is evidence of spatially heterogeneous function, not a
calibrated RF width/gain for any of NeuroFly's 185 MaleCNS bodies. Structural
input-site counts are not equivalent to functional input strength, and
Klapoetke's degrees cannot be converted to column steps here.

Both cases support studying *relative anatomical addressing*; neither
transfers FAFB body identity, absolute optical angles, polarity/direction
tuning, nonlinear transfer, adaptation, per-body gain, or firing dynamics to
the MaleCNS sample. Anatomical dendritic/input position may correlate with
functional RF location but is not itself a measured RF.

## Input-model comparison and decision

| Candidate | Semantics and assumptions | Scientific use | Invalid interpretation / remaining gap |
| --- | --- | --- | --- |
| A `TYPE_BROADCAST_CURRENT` | Current Level-P `bilateral_type_broadcast_v1` produces interval-level LC4/LPLC2 type drives in mV-equivalent; no individual sensory state. | Preserves existing angular looming experiment and baseline reproducibility. | Does not test individual spatial routing. |
| B `RELATIVE_ANATOMICAL_EXPOSURE` | New, versioned **synthetic** column-space active set produces per-body anatomical overlap. An explicit, future exposure→model-input transfer would be a *model assumption*, not a measurement. | Bounded software/causal tests of body-addressing, selection, heterogeneity and downstream routing. | Overlap alone is not a drive, RF, voltage, spike, looming response or real-world angular stimulus. RF kernel/width, gain, selectivity and dynamics remain unknown. |
| C `RELATIVE_EXPOSURE_X_TYPE_DRIVE` | Would multiply current angular/type-level time signal by an unrelated relative-column exposure. Requires an explicit coupling, normalization and physical-to-column association assumption. | Could be a later sensitivity model **if** independently justified. | In current form it mixes incompatible stimulus spaces and may misleadingly allocate type drive to bodies. It is **not endorsed for Phase 7D**; structural counts cannot be used to force aggregate drive conservation. |
| D `BLOCKED` | Keep only type-level state. | Avoids all model assumptions. | Leaves reproducible relative anatomical body addressing untested despite verified source topology. |

**Decision: `RELATIVE_COLUMN_INPUT_FEASIBLE` for a bounded *model-assumption*
experiment, not physiological individualization.** B can precede absolute
optical registration when its stimulus is explicitly native lattice space and
its output remains labelled anatomical exposure until a separately versioned
transfer model is specified. It has information gain for identity, schema,
intervention and reproducibility tests. It cannot validate angular RFs,
physical looming, measured firing or behaviour. Candidate C must not silently
reuse `theta_rad`/`angular_expansion_velocity_rad_s` as columns or normalize
body outputs to match a type drive by construction.

The smallest **Phase 7D** is a new synthetic `RELATIVE_COLUMN_SPACE`
experiment on a predeclared small LC4/LPLC2 subset from both sides, with
separate stimulus and transfer contracts, explicit free gain/threshold
assumptions and sensitivity, plus a type-level baseline. It must report exact
per-body model input, any downstream DNp01 effects, no-angle semantics and
source identity. It must *not* expand directly to all 311 bodies or call its
output a calibrated visual response. If a genuine optical registration is
released, that is a separate evidence gate, not a silent reinterpretation.

Milestone gates: **311 exact identities — done; 311 source column
distributions — done; reproducible relative anatomical addressing — feasible
offline; absolute rays — unresolved; functional RF/input transfer —
unresolved; per-body neural dynamics — absent; circuit validation — absent.**
The existing angular looming, DNp01 and TTMn experiments remain unchanged
and not empirically validated.

## Reproduction and data handling

```bash
python -m neurofly.malecns inspect-column-snapshot
python -m research.relative_column_space \
  --workbook /path/to/pinned/optic-column-type-assignments-v1.0.xlsx \
  --output data/derived/malecns/looming_giant_fiber_v1/relative_column_space_v1/analysis.json
```

The research result is ignored by Git. Its current SHA-256 is
`596bd234b8748c9cb1d453c8026616cf1729900bd6d0c33fd7f44389ecbeead0`;
a repeat run gave identical bytes. It is **not** an experiment artifact,
scientific source amendment, neural-state contract, or runtime API product.
The official workbook and coordinate PDF remain external temporary research
files; neither was committed or placed in `web/public`.
