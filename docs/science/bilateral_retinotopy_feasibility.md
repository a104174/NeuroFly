# Phase 7A — bilateral MaleCNS retinotopic registration feasibility

**Audit:** 2026-09-24. **Dataset:** `male-cns:v1.0`. **Candidate:**
`looming_giant_fiber_v1`. **Decision:**
`RETINOTOPY_ONLY_NO_ABSOLUTE_VISUAL_ANGLE`.

This is a read-only evidence assessment. It does not assign a functional
receptive field, generate individual sensory dynamics, or change the existing
type-level LC4/LPLC2 encoder.

## Sources and coordinate meanings

The authoritative local evidence is the [Phase 1E body-column
contract](body_column_contract.md), joined by exact body ID to the validated
313-body CircuitContract. Its `matching_side_optic_primary_post_v1` rule counts
each body's primary postsynaptic optic-lobe sites in ME/LO/LOP columns on its
validated `somaSide`. Each sparse record preserves `olHex1`, `olHex2`, neuropil,
side, and a structural input-site count. Missing sites remain unassigned. These
are anatomical column indices, not degrees, functional RF centres, or response
weights. The local ignored `body_column_input_v1` snapshot contains 25,438
sparse records, 311 body summaries, 574,745 assigned sites and 2,790
unassigned sites. Its source and file hashes are recorded in the Phase 1E
document; no new neuPrint query was necessary.

The [official bilateral workbook](https://github.com/flyconnectome/2025malecns/blob/67767d2233657983993ff6c2be48e836a935863c/supplemental_data/optic-column-type-assignments-v1.0.xlsx)
was downloaded read-only for this audit from commit
`67767d2233657983993ff6c2be48e836a935863c`: 111,565 bytes,
SHA-256 `d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`.
Its `Right OL` and `Left OL` sheets contain respectively 892 and 880 unique
ME column keys, `ME_<side>_col_<hex1>_<hex2>`. The `READ ME` defines columns
`column`, `L1`, `R7`, `R7_type`, `R8`, `R8_type`, `column_type`,
`aMe12_branch`, `Tm5a_branch`, `Notes`; `-99` means a reference L1/R7/R8
cell was not found. Column types include pale, yellow1, yellow2, edge, DRA,
and unclear. The L1/R7/R8 IDs annotate columns; they are not LC4/LPLC2 RFs.
Both sides have explicit keys, but equal handedness, equal coverage, and a
left/right degree transform do not follow from the key syntax. ME/LO/LOP keys
share the side and hex suffix under the validated MaleCNS assignment rule.

[Nern et al., *Connectome-driven neural inventory of a complete visual
system*](https://www.nature.com/articles/s41586-025-08746-0) describes
the male optic-lobe hex lattice: `p,q` column axes, eye-oriented horizontal
and vertical axes, an equator anchored through lamina photoreceptor anatomy,
and approximate column–ommatidium correspondence except at edges. Direct
column pins were assigned to 15 listed columnar types, not to LC4 or LPLC2
as individual RFs. This optic-lobe work is not, by itself, a bilateral
`male-cns:v1.0` column-to-degree contract. One EM specimen's reconstructed
column–lens correspondence also does not give that lens's optical ray in
world/display coordinates.

The [MaleCNS project](https://male-cns.janelia.org/) and [published MaleCNS
study](https://doi.org/10.1016/j.cell.2026.08.015) provide v1.0 source
identity and type-level eye maps. The [Cell Type Explorer
help](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/help.html)
describes population spatial coverage as per-column cell counts and synapse
density in ME/LO/LOP. Those anatomical counts are not measured RFs. The
published eye-map method projects column counts onto a Mollweide map based
on Zhao et al., with a MaleCNS column extension described as work in
preparation. The audited official supplement and local project evidence do
not release a column-keyed bilateral angular transform with defined origin,
signs, handedness, interpolation, and uncertainty. SVG eye-map pixels are not
such a contract and were not reverse-engineered.

The [official optic-lobe annotation matching
repository](https://github.com/flyconnectome/ol_annotations) and the MaleCNS
supplement provide type/group comparisons with FlyWire/FAFB. They do not
provide a documented one-to-one MaleCNS LC4/LPLC2 body ↔ FAFB body mapping.
Type matching cannot transfer an individual RF.

## Primary functional and cross-dataset evidence

[Klapoetke et al. 2017](https://www.nature.com/articles/nature24626)
demonstrated spatially local LPLC2 looming responses in live flies. It
supports population RF diversity, not identity of any MaleCNS body.
[Dombrovski et al., *Synaptic gradients transform object location to
action*](https://www.nature.com/articles/s41586-022-05562-8) estimated
anatomical RFs for 55 individual **FAFB** LC4 neurons from dendritic lobula
territory registered to eye coordinates using reconstructed column landmarks;
downstream DN responses were experimentally tested. The anatomical centre,
assumed RF shape, functional centre, and gain remain different concepts.
Neither the FAFB IDs nor fitted transform can be silently copied to MaleCNS.

[Zhao et al., *Eye structure shapes neuron function*](https://www.nature.com/articles/s41586-025-09276-5)
registers a right-side female FAFB medulla lattice to optical directions from
a separate female micro-CT specimen, with explicit interpolation for a T4
analysis. This is a valuable primary registration method, but the released
analysis does not establish a validated **bilateral** `male-cns:v1.0`
key-to-angle mapping with uncertainty
for NeuroFly's 311 bodies. [Recent LPLC2 work](https://www.nature.com/articles/s41586-025-09037-4)
maps two stimulus-directed ommatidia to identified male optic-lobe columns,
then uses T4 pathways to nominate LPLC2 cells. This is a bounded right-field
registration example, not a complete bilateral lookup or a MaleCNS-body
functional RF catalogue. A generic interommatidial angle or a mirror rule
would be a **model assumption**, not a source transform. No angular origin,
azimuth sign, elevation sign, equator convention, or left/right mirror is
assigned here.

[A separate FlyWire/FAFB navigation study](https://www.nature.com/articles/s41586-024-07967-z)
provides a bilateral Mi1 eye-map CSV and aligns micro-CT ommatidial directions
to medulla columns using photoreceptor-defined equator landmarks. Its body IDs
and column grid belong to FAFB/FlyWire, not MaleCNS v1.0; the available CSV is
not a documented MaleCNS per-column angular lookup. This is an informative
registration precedent, not a transferable body/column identity.

## LC4 and LPLC2 body evidence and coverage

The direct MaleCNS evidence for both types is per-body **postsynaptic
column occupancy**, not a direct assigned RF/angle. LC4 assigned inputs are
predominantly lobula columns; LPLC2 spans lobula and lobula-plate columns,
with a small medulla contribution. Connectivity from column-identified
upstream neurons (including T4/T5 for LPLC2) could be investigated as an
independent *anatomical* estimator, but no complete upstream identity/column
join or functional transfer is established here. Structural counts could
weight an explicitly named anatomical occupancy estimator, never response
gain; an unweighted counterpart and missing-site sensitivity would be needed.

“Direct” below means a direct body-specific angular/RF assignment (none).
“Relative” means a derivable body-specific column-space territory, not an
absolute angle. “Angular unresolved” overlaps relative coverage deliberately:
all 311 have column evidence and all 311 still lack a validated degree map.

| Type | Side | Bodies | Direct angle/RF | Relative column topology | Column-unresolved | Angular unresolved | Assigned sites | Unassigned sites |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LC4 | L | 71 | 0 | 71 | 0 | 71 | 139,441 | 353 |
| LC4 | R | 55 | 0 | 55 | 0 | 55 | 137,866 | 102 |
| LPLC2 | L | 94 | 0 | 94 | 0 | 94 | 129,806 | 1,598 |
| LPLC2 | R | 91 | 0 | 91 | 0 | 91 | 167,632 | 737 |
| **Total** | | **311** | **0** | **311** | **0** | **311** | **574,745** | **2,790** |

Coverage was recomputed from the ignored Phase 1E summary and sparse files,
without modifying them. Every listed body has at least one assigned column;
assignment fractions vary, so missing sites remain a real uncertainty.

### Bounded four-body descriptive proof

The following index centroids are arithmetic means of `olHex1/olHex2`
weighted by **anatomical input-site counts**. They are descriptive summaries
of source-column occupancy, not final RF estimators, angular coordinates, or
physiological weights. Neuropil remains part of each source column key.

| Type/body/side | Assigned / relevant | Distinct columns | Largest source columns (input sites) | Column-index centroid | Degree coordinate |
| --- | ---: | ---: | --- | --- | --- |
| LC4 12032 L | 2,436 / 2,477 | 75 | `LO_L_col_33_29` (132), `LO_L_col_35_28` (127), `LO_L_col_35_27` (111) | (33.47, 30.73) | unresolved |
| LC4 16128 R | 3,709 / 3,710 | 66 | `LO_R_col_23_09` (178), `LO_R_col_25_11` (133), `LO_R_col_21_08` (126) | (22.62, 10.08) | unresolved |
| LPLC2 11498 L | 1,254 / 1,263 | 95 | `LO_L_col_18_04` (83), `LO_L_col_17_03` (55), `LO_L_col_15_02` (50) | (15.95, 5.98) | unresolved |
| LPLC2 14465 R | 1,854 / 1,859 | 105 | `LO_R_col_23_11` (77), `LO_R_col_24_12` (68), `LOP_R_col_22_09` (56) | (23.65, 12.00) | unresolved |

The complete source-column list for each body remains in the ignored Phase 1E
`column_inputs.jsonl`, keyed by exact body ID; the table is only a bounded
summary. No visual-side mirroring or relative ordering **between** L/R was inferred.
Body 11498's fragmented morphology does not create component-level RFs.

## Decision, uncertainty, and next gate

**Decision C: `RETINOTOPY_ONLY_NO_ABSOLUTE_VISUAL_ANGLE`.** MaleCNS-native
body→column distributions are available bilaterally for all 311 sensory
bodies. A calibrated bilateral column→azimuth/elevation transform, with
documented orientation and uncertainty, is not available in the audited
public machine-readable sources. This is an absence in the bounded source
audit, not proof that no registration can ever be derived.

A future `VisualFieldRegistrationV1` should keep dataset/version, side,
neuropil/column ID and hex indices separate from eye-ray azimuth/elevation;
identify its direct calibration landmarks, eye/dataset registration method,
orientation/handedness, angular uncertainty, source version and assumption
class. A separate `NeuronReceptiveFieldAssignmentV1` could reference source
columns, body/type/side, anatomical estimator, coverage/missing fractions,
centre/extent uncertainty, and provenance. These are **proposals only**;
no production schema is introduced. Functional RF centre and response gain
must remain absent unless independently measured or modelled as assumptions.

The smallest Phase 7B is a **bilateral eye-registration evidence and landmark
reproducibility gate**: seek a released official column-keyed map or construct
and cross-validate a bounded landmark registration using primary micro-CT
optical directions, explicit left/right column↔lens correspondences, orientation,
and held-out angular error. Apply it first to the four fixed bodies with
uncertainty, not to all 311 or the encoder. If that evidence fails, retain
column-space-only topology. Reaching 313 explicit dynamics also requires a
scientifically justified per-body visual input/response model; coordinates
alone do not provide it.

No simulation, API, frontend, source morphology, CircuitContract, structural
weight, experiment artifact, or type-level encoder was changed. The existing
experiment remains not empirically validated.
