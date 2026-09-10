# Phase 1D — MaleCNS-native receptive-field feasibility audit

**Audit date:** 2026-09-10
**Candidate:** `looming_giant_fiber_v1`
**Dataset:** `male-cns:v1.0`
**Scope:** evidence and data feasibility only. No neural dynamics, sensory
encoder, or morphology framework is introduced.

## Current status (not a final D1–D4 decision)

The Phase 1C boundary remains the smallest defensible sensory boundary. The
public MaleCNS resources inspected in this audit provide column/ROI and
synapse-level ingredients, but no provenance-verifiable, body-keyed receptive
field table for the selected LC4 or LPLC2 bodies. The public resources also do
not expose a sufficiently specified, reproducible column-to-visual-coordinate
transform for this use. This is an evidence-status statement, not evidence
that body-level mapping is impossible or fundamentally indefensible in
MaleCNS. Morphology/ROI/optic-column feasibility remains unresolved until the
bounded Gate 3 live study is run.

| Population | Current status | Consequence |
| --- | --- | --- |
| LC4 | **Unresolved — not currently defensible from the inspected public resources; Gate 3 remains pending.** | Keep the Phase 1C population association with angular expansion velocity while feasibility remains unresolved. |
| LPLC2 | **Unresolved — not currently defensible from the inspected public resources; Gate 3 remains pending.** | Keep the Phase 1C population association with angular size while feasibility remains unresolved. |

No morphology was acquired. Gate 3 was stopped before any live request because
`NEUPRINT_APPLICATION_CREDENTIALS` is unavailable. This is a deliberate stop,
not a synthetic morphology result.

## Repository findings

The audit began with the repository as the source of truth:

- branch: `main`, tracking `origin/main`;
- HEAD: `fd5de1bde3119072b44e1b1cb6dfe3ac7bc5faab` (`phase 1C`);
- initial worktree status: clean;
- Phase 1C is committed and includes `sensory.py`, `benchmarks.py`, the sensory
  evidence document, and their offline tests;
- local ignored snapshot: `data/derived/malecns/looming_giant_fiber_v1/`;
- snapshot manifest: candidate version 1, `male-cns:v1.0`, Janelia neuPrint,
  acquired `2026-09-10T20:39:56.889520+00:00`;
- snapshot counts: 126 LC4 (71 left, 55 right), 185 LPLC2 (94 left, 91 right),
  2 DNp01, 313 neurons total, 20,607 induced chemical edges;
- `credential_available`: **false** (the credential value was not printed,
  logged, or serialized).

The contract contains normalized annotations and chemical body-level edges.
It intentionally contains no skeleton nodes, synapse coordinates, optic-lobe
column IDs, or registered visual frame. `soma_side`, body ID, node order, and
structural edge weight are annotations/structural quantities, not visual
coordinates or receptive-field weights.

## Gate 1 — MaleCNS-native literature and resource audit

### Hoeller et al., Cell (2026)

The official [Janelia publication page](https://www.janelia.org/publication/the-organization-of-visual-pathways-in-the-drosophila-brain)
and the [Cell article landing page](https://www.sciencedirect.com/science/article/pii/S0092867426009414)
describe a connectome/network analysis that propagates photoreceptor signals
through layered optic-lobe and central-brain pathway classes. It reports
neuron-by-neuron predictions of receptive-field structure and feature-related
input biases, with predictions compared with physiological observations.
This is a connectome-derived prediction, not a direct physiological recording
for each NeuroFly body.

The following reuse checks could not be satisfied from the publicly visible
materials inspected:

1. no downloadable body-keyed RF table, schema, or official regeneration
   repository was located;
2. no key was exposed that could be verified as MaleCNS `bodyId`, a cell
   instance, or a stable type/side identifier;
3. the accessible abstract/landing pages do not state the exact RF payload
   representation (azimuth/elevation, column weights, pixels, polygons, or
   another map), bilateral convention, or uncertainty field;
4. the MaleCNS release/version and body-ID namespace used by the published
   outputs could not be matched to this snapshot's `male-cns:v1.0` manifest;
5. LC4 and LPLC2 could not be confirmed as explicitly represented in a
   reusable, body-keyed output from the inspected public artifacts.

The full article Methods/supplement and any associated release were not
machine-readable in this audit (the article landing page was access-limited),
so a claim that those outputs can be consumed by NeuroFly would not be
provenance-safe. The result is therefore **not D1**. The paper remains an
important method lead: if the authors release a versioned table and identifier
mapping, it should be preferred over an independent morphology-to-eye
reconstruction.

### Berg et al. MaleCNS visual-system resources

The public [MaleCNS paper record](https://pmc.ncbi.nlm.nih.gov/articles/PMC12636603/)
describes visual-projection-neuron eye maps made by mapping input synapses to
optic-lobe column ROIs and displaying their spatial distribution on a visual
field projection. The public [supplemental repository](https://github.com/flyconnectome/2025malecns)
contains `optic-column-type-assignments-v1.0.xlsx`: one row per left or right
visual column, with L1/R7/R8 body IDs, column type, and marker-branch
annotations. That is a column annotation resource; it is not an LC4/LPLC2
body receptive-field table.

The methods establish the important direction of a defensible derivation—use
visual input synapses and their column assignment—not downstream DNp01
connectivity. They do not, in the public machine-readable resources inspected,
provide a NeuroFly-ready sparse map from each selected LC4/LPLC2 body to
visual-field coordinates. The supplemental repository is an official data/code
entry point for derived MaleCNS products (including notebooks and the column
spreadsheet), but no released routine there directly emits that per-body RF
map. The paper's analysis tooling (principally `navis`/`natverse`) is general
connectome tooling, not a validated NeuroFly adapter.

### Official MaleCNS download and exploration resources

The official [MaleCNS download page](https://male-cns.janelia.org/download/)
identifies the pinned `male-cns:v1.0` dataset and documents:

- ROI segmentation under `gs://flyem-male-cns/rois/fullbrain-roi-v4`;
- syn-point records containing pre/post locations, body IDs, `kind`, and
  encompassing ROIs (8-nm voxel coordinates);
- synaptic partner records containing pre/post body IDs and `primary_post`;
- raw MaleCNS-coordinate SWC skeletons, 1-nm precomputed skeletons, mirrored
  skeletons, and a JRC2018 unisex-template transform.

These are direct data ingredients, not already-derived receptive fields. The
official [Explore page](https://male-cns.janelia.org/explore/) exposes NeuPrint,
Neuroglancer, and Cell Type Explorer for inspection, but it does not add a
body-level RF artifact.

The [Male CNS Cell Type Explorer repository](https://github.com/reiserlab/celltype-explorer-drosophila-male-cns)
documents dataset UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`, dataset
`male-cns:v1.0`, and an interactive type-level catalog with morphology, ROI
innervation, and population spatial-coverage maps. Its downloadable displayed
neuron skeleton/mesh files are not RF metadata. The [LC4 page](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/LC4.html)
reports 126 neurons (55 right, 71 left) and type/side population grids; the
[LPLC2 page](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/LPLC2.html)
reports 185 neurons (91 right, 94 left) and the analogous population grids.
Neither page exposes a body-keyed visual-field map.

### Gate 1 answers

| Question | Audit result |
| --- | --- |
| Body-level predictions already reusable? | Not found in an inspectable, provenance-verifiable public artifact. |
| Downloadable and keyed by `bodyId`/instance? | No such RF file or key schema was located. |
| LC4/LPLC2 explicitly included? | Not verifiable from the accessible Hoeller output; Cell Type Explorer only supplies type/side aggregates. |
| Coordinate representation? | Berg-style eye-map projection is described at visual-field/column level; the Hoeller payload and exact coordinate convention are not exposed. |
| Bilateral representation? | MaleCNS column resources and Explorer aggregates distinguish left/right; no body-level RF payload with bilateral transform was located. |
| Dataset/version match? | Official resources are `male-cns:v1.0`; the Hoeller output's exact release and body-ID namespace are not exposed, so compatibility is unverified. |
| Regeneration code? | No official Hoeller RF regeneration repository was found in the inspected public resources. |
| Method class? | Hoeller: connectome/network-derived prediction; Berg eye maps: published-derived spatial summary from input synapses and columns; neither is a direct NeuroFly physiological model. |

## Existing mapping availability

There is currently **no body-level MaleCNS receptive-field mapping available to
NeuroFly for either LC4 or LPLC2**.

- **LC4:** the MaleCNS Cell Type Explorer has left/right population synapse
  density grids and ROI totals, not a body-ID-to-field record. The Phase 1C
  angular-expansion-velocity association remains a population-level modelling
  approximation.
- **LPLC2:** the Explorer has left/right population grids and ROI totals, not a
  body-ID-to-field record. Published work establishes localized fields and
  population tiling, but not a mapping for these MaleCNS bodies.

The older [Klapoetke et al. study](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457385/)
provides physiological LPLC2 field centers/tiling, and [Moreno-Sanchez et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11071487/)
provides morphology/synapse-based anatomical estimates. Those resources use
other preparations/datasets (including FAFB/FlyWire-derived material) and are
methodological background only. No body IDs or coordinates were transferred.

## Gate 2 — ROI and optic-column feasibility

The official resources make a bounded future derivation plausible, but not
currently defensible without a targeted, authenticated linkage audit.

### What is available

1. The `male-cns:v1.0` bulk syn-point table can, in principle, link a selected
   body to pre/post coordinates and encompassing ROIs. The partner table also
   carries body pairs and primary post-synaptic neuropil.
2. MaleCNS neuropil/column ROI segmentation and the left/right column
   assignment spreadsheet provide an anatomical column vocabulary.
3. Raw skeletons and coordinate transforms are published as source data, so a
   future audit need not download meshes or the full connectome.

### What remains unresolved

- The current contract has no synapse-level records. A body-level query must
  distinguish visual/dendritic input synapses from central-brain outputs using
  explicit `kind`/ROI provenance, not arbitrary coordinate thresholds.
- A biological rule for which input synapses represent the RF must be stated
  per type. A broad ROI total or a type-level synapse-density grid cannot stand
  in for the individual input-column distribution.
- Raw MaleCNS-to-template coordinate transforms are not themselves a
  column-to-eye-map transform. The public materials inspected do not provide a
  validated, machine-readable mapping with orientation conventions and
  uncertainty for every column used by this candidate.
- The column resource records left/right columns and documents missing or
  uncertain assignments (for example sentinel IDs/notes in the spreadsheet).
  Any future map must preserve that uncertainty rather than silently filling
  columns.
- Hierarchical ROI memberships must not be summed naively. Input/output
  classification must use the source table's semantics and documented ROI
  provenance.

Thus Gate 2 does not establish D2, but it also does not establish a final D4
conclusion. It establishes the smallest next evidence request: a targeted
body→input-synapse→column linkage and transform validation, with no
whole-population bulk download.

## Gate 3 — bounded morphology feasibility

Gate 1 and the public Gate 2 audit were insufficient, so morphology would be
the next possible evidence source. The live portion was **not run** because
`NEUPRINT_APPLICATION_CREDENTIALS` was absent. No skeleton or synapse query was
made, no morphology data was written, and no sampled IDs exist to report.

The pending run is deliberately bounded and deterministic:

```text
for each (type, side) in (LC4,L), (LC4,R), (LPLC2,L), (LPLC2,R):
    digest = SHA256("looming_giant_fiber_v1|<type>|<side>|<body_id>")
    sort eligible contract body IDs by digest
    select the first four
```

The contract has enough bodies for all four strata (71/55 LC4 and 94/91
LPLC2). A credentialed run must record the 16 exact IDs and retrieve raw
MaleCNS skeletons with `heal=False`, then inspect raw node/root/component
counts, bounding boxes, cable length where available, and only narrowly
necessary input/output ROI data. Because that run did not occur, there are no
node, fragment, cable, or ROI statistics and no claim that `heal=False` was
observed. The absence of a query also means no skeleton healing occurred.

## Independent population status (provisional)

No final D1/D2/D3/D4 decision is made for either population in this
documentation-only phase. The statuses below mean only that the inspected
public resources do not currently support assignment and that the bounded
live Gate 3 study is still pending. They do not mean that MaleCNS body-level
mapping is impossible or fundamentally indefensible.

### LC4 — unresolved; Gate 3 pending

The selected LC4 bodies have no reusable body-level RF record. Population
eye-map grids and broad ROI totals cannot identify each cell's visual input
columns, and the public materials do not supply a validated column-to-visual
coordinate payload. No MaleCNS morphology was inspected to test a derivation.
Therefore a per-body LC4 center, extent, polygon, or weight map would require
unrecorded assumptions. Until Gate 3 is run, NeuroFly should retain only the
Phase 1C population-level association with angular expansion velocity.

### LPLC2 — unresolved; Gate 3 pending

The published localized/tiled LPLC2 field organization is strong biological
motivation, but it does not key the physiological fields to these
`male-cns:v1.0` bodies. The MaleCNS population maps and ROI summaries are not
individual fields, and no four-layer dendritic feasibility sample was acquired
because credentials were unavailable. A body-specific LPLC2 field would
therefore require an unvalidated transform and cannot currently be claimed as
MaleCNS metadata. This provisional status must not be read as a conclusion
that a MaleCNS-native mapping cannot be derived.

## Proposed sensory metadata contract

No new contract is justified by the evidence currently available, so no
receptive-field fields were added to `CircuitContract` or to the snapshot.

If the pending linkage audit or an official Hoeller release succeeds, the
future representation should preserve the richest supplied map rather than
collapse it to a center prematurely. A conditional model-neutral shape is:

```text
body_id                         # MaleCNS v1.0 body key
eye_side                        # explicit L/R provenance
input_column_map                # sparse column_id -> count/weight, if supplied
visual_coordinate_system        # named projection and orientation/version
mapping_method                  # published method or exact NeuroFly derivation
mapping_source                  # URL/release/table identifier
source_dataset                  # dataset + version/UUID
uncertainty                     # missing columns, confidence, and error semantics
```

`input_column_map` should remain a sparse count/weight or polygon/heatmap
payload when that is what the source supports. Azimuth/elevation centers and
extents are not justified until the transform and uncertainty are validated.
Any centroid, fit, normalization, or interpolation would be explicitly
NeuroFly-derived, not a MaleCNS field.

## Provenance and safeguards

| Provenance class | Allowed in a future artifact | Status in this phase |
| --- | --- | --- |
| Direct MaleCNS | Body IDs, type/side annotations, synapse coordinates/ROIs, raw skeleton fields, structural edges. | Existing snapshot contains only the first, second, and structural-edge items. |
| Published-derived MaleCNS | Hoeller network RF predictions, Berg column/eye-map products, with release and identifier schema retained. | Inspected as evidence; no body-level artifact was adopted. |
| NeuroFly-derived | Phase 1C looming geometry, benchmark labels, deterministic sample hash, centroids/polygons/normalization if later computed. | No RF derivation or morphology summary was produced. |

The audit did not transfer FAFB/FlyWire body IDs or coordinates, use body ID or
soma side as a visual coordinate, use DNp01 connectivity or structural weight
as an RF, or introduce physiological weights/neural dynamics. No skeleton
healing occurred because no skeleton was queried.

## Smallest next phase

Keep the Phase 1C population-level sensory approximation for experiments. The
smallest scientifically justified follow-up is a credentialed, read-only
validation on exactly the 16 deterministic LC4/LPLC2 bodies: confirm
body→visual-input-synapse→column linkage, bilateral orientation, and a
versioned column-to-eye-map transform before writing any receptive-field
encoder. Do not acquire the remaining visual population or implement neural
dynamics as part of that check.
