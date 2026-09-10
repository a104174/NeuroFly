# Phase 1D-B — bounded MaleCNS body-to-visual-space feasibility validation

**Audit date:** 2026-09-10
**Candidate:** `looming_giant_fiber_v1`
**Dataset:** `male-cns:v1.0`
**Scope:** bounded read-only feasibility validation. No neural dynamics,
production receptive-field mapper, or morphology framework is introduced.

## Current status

Phase 1D-A found no ready-made, provenance-verified `MaleCNS bodyId -> visual
receptive field` table in the inspected public resources. Phase 1D-B completed
the deterministic offline sample and snapshot annotation checks, then stopped
the live neuPrint component because credentials were unavailable. The current
snapshot alone therefore does not support per-body receptive-field assignment.

The Phase 1C population-level approximation remains the current operational
sensory boundary. Morphology, input-ROI, optic-column linkage, and the complete
column-to-eye-map transform remain unresolved until the bounded live study is
run. This is not evidence that body-level mapping is impossible or
fundamentally indefensible in MaleCNS, and it is not a final D2/D3/D4
adjudication.

| Population | Phase 1D-B status | Current consequence |
| --- | --- | --- |
| LC4 | **Unresolved — live body-to-input-anatomy validation pending credentials.** | Keep the Phase 1C angular-expansion-velocity population approximation. |
| LPLC2 | **Unresolved — live body-to-input-anatomy validation pending credentials.** | Keep the Phase 1C angular-size population approximation. |

No live body, synapse, ROI, or skeleton query was made. This is a deliberate
stop, not a synthetic negative result.

## Repository findings

The audit began with the repository as the source of truth:

- branch: `main`, tracking `origin/main`;
- HEAD: `ad6b597` (`docs: record receptive-field feasibility audit`);
- initial worktree status: clean;
- Phase 1D-A is committed and contains the prior public-resource audit;
- `src/neurofly/malecns/` remains the existing acquisition/contract/sensory
  implementation; no production code was added in this validation;
- local ignored snapshot: `data/derived/malecns/looming_giant_fiber_v1/`;
- snapshot manifest: candidate version 1, `male-cns:v1.0`, Janelia neuPrint,
  acquired `2026-09-10T20:39:56.889520+00:00`;
- snapshot counts: 126 LC4 (71 left, 55 right), 185 LPLC2 (94 left, 91 right),
  2 DNp01, 313 neurons total, 20,607 induced chemical edges;
- `credential_available`: **false** (the credential value was not printed,
  logged, or serialized);
- ignored feasibility artifact: `data/derived/malecns/looming_giant_fiber_v1/phase_1d_b_feasibility.json`.

The contract contains normalized annotations and chemical body-level edges.
It intentionally contains no skeleton nodes, synapse coordinates, optic-lobe
column IDs, or registered visual frame. `soma_side`, body ID, node order, and
structural edge weight are annotations/structural quantities, not visual
coordinates or receptive-field weights.

## Deterministic 16-body sample

The validated Phase 1B contract was used as the complete source population.
For each `(type, soma_side)` stratum, the UTF-8 string
`looming_giant_fiber_v1|<type>|<side>|<body_id>` was SHA-256 hashed, ranked
lexicographically by digest (body ID is the secondary key), and the first four
were selected. Selection is independent of morphology and has no biological
meaning. All four strata contain at least four eligible bodies.

| Type | Side | Rank | Body ID | Digest | Instance | Status / status label |
| --- | --- | ---: | ---: | --- | --- | --- |
| LC4 | L | 1 | 35616 | `04bbbf78e15215c6c0ad19d823829efc90bafc1b98d3de120baa0e12cd12a3e5` | `LC4_L` | `Traced` / `Prelim Roughly traced` |
| LC4 | L | 2 | 18432 | `0665c51c24d98f7deb0f591ec9b0833a2838b65714cb2eb8ac627db73c178c26` | `LC4_L` | `Traced` / `Prelim Roughly traced` |
| LC4 | L | 3 | 524899 | `06fdf853734a317dabbfbc0d6401924dbd312116734125514a21cea992e57177` | `LC4_L` | `Traced` / `Prelim Roughly traced` |
| LC4 | L | 4 | 30087 | `074cffe5e42223293711737c6607d8c1576ca14ad5cd89efa236d085c4eb68b3` | `LC4_L` | `Traced` / `Prelim Roughly traced` |
| LC4 | R | 1 | 16138 | `03fc185f7ccc89e76ed9d215628182e8ec6779ad1f1424597ea94cdc392910e7` | `LC4_R` | `Traced` / `Roughly traced` |
| LC4 | R | 2 | 23098 | `0a2c6d41e8e062fc2290ae8257e91e29d683cfdff78d36ce1ff0a4e52b5d784c` | `LC4_R` | `Traced` / `Roughly traced` |
| LC4 | R | 3 | 19954 | `0cbbc51f6781c054ca0a163602b40194b08f57a714776585f363386b4d927a94` | `LC4_R` | `Traced` / `Roughly traced` |
| LC4 | R | 4 | 19260 | `1000c5933fefbb8d1349d217457444419e770395bc735b2da223eb702d13ebf6` | `LC4_R` | `Traced` / `Roughly traced` |
| LPLC2 | L | 1 | 20329 | `00d833ee81db87c4d56953143ce7007e12317bd7fdacc0051415a9cf2c17ffd9` | `LPLC2_L` | `Traced` / `Prelim Roughly traced` |
| LPLC2 | L | 2 | 18936 | `06ed076001c6220ea97044f5487810d06b10720459943d9d21f838990faeb79c` | `LPLC2_L` | `Traced` / `Prelim Roughly traced` |
| LPLC2 | L | 3 | 524366 | `0d66369f97c7511e02f4fba1d15dd4a259ca4ee8748da9ff93e3ec3e9758d4d8` | `LPLC2_L` | `Traced` / `Prelim Roughly traced` |
| LPLC2 | L | 4 | 30893 | `187f13205510e6be0b1bacc6c78456f634b4b67e449cd14b91409a3813f2165d` | `LPLC2_L` | `Traced` / `Prelim Roughly traced` |
| LPLC2 | R | 1 | 26915 | `0205f690dc0f63a78249d2805fd7c5b6e917dbb6ec619616bea6dcfe64ec1219` | `LPLC2_R` | `Traced` / `Roughly traced` |
| LPLC2 | R | 2 | 21808 | `0adabf834f0b2c69d59a0ddaf5063d04050a1beee78b29dfd9690e0e9470a782` | `LPLC2_R` | `Traced` / `Roughly traced` |
| LPLC2 | R | 3 | 19034 | `0cfa2481ac4840429c4426f991de5503b15a6685fcdbfc7396cd9e4a8d654f87` | `LPLC2_R` | `Traced` / `Roughly traced` |
| LPLC2 | R | 4 | 20471 | `0ec5702aed8ec367d8d42ecbb03061f1533d5ac3aedefe37f525fc045c43b7a1` | `LPLC2_R` | `Traced` / `Roughly traced` |

All 16 records are `male-cns:v1.0`, `visual_projection` superclass entries and
remain in their deterministic strata despite the differing reconstruction
status labels. No body was selected for apparent morphology completeness. The
same sample, ranks, digests, live-pending state, and provenance categories are
stored in the ignored machine-readable feasibility manifest at
`data/derived/malecns/looming_giant_fiber_v1/phase_1d_b_feasibility.json`.

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

## Live MaleCNS acquisition status

The live component was stopped before any neuPrint request because
`NEUPRINT_APPLICATION_CREDENTIALS` is unavailable. The exact query categories
that remain pending are:

- Gate A: authenticated confirmation of the 16 sampled body annotations;
- Gate B: narrowly scoped input-synapse coordinates, `kind`, and ROI metadata;
- Gate C: body-synapse linkage to the official optic-column IDs;
- Gate D: raw skeletons only if Gates B/C cannot identify body-specific visual
  topology.

Bodies queried: **0**. Skeletons queried: **0**. Input-synapse records queried:
**0**. Bulk downloads: **none**. No `heal=False` call was made because no
skeleton was fetched, and no morphology result was fabricated.

## Gate 2 — ROI and optic-column feasibility (public resources only)

The official resources make a bounded future derivation plausible, but the
body-level Gate B query could not run. Publicly documented ingredients are:

1. The `male-cns:v1.0` syn-point table can link a selected body to pre/post
   locations, `kind`, and encompassing ROIs; the partner table carries pre/post
   body IDs and `primary_post`.
2. MaleCNS neuropil/column ROI segmentation and
   `optic-column-type-assignments-v1.0.xlsx` provide a bilateral column
   vocabulary. The spreadsheet is one row per visual column, with a string
   column identifier such as `ME_R_col_...`, L1/R7/R8 anchor IDs, column type,
   marker branches, and notes. The L1/R7/R8 IDs annotate columns; they are not
   LC4/LPLC2 receptive fields.
3. Raw MaleCNS skeletons and template transforms are published source data,
   but no morphology or synapse table was downloaded in this bounded run.

### LC4

Useful input-synapse amount/fraction, column-assigned fraction, unassigned
fraction, ambiguity, and body-to-body variation are **not measured**: zero
sampled-body synapse records were queried. The public type/side population
grids do not substitute for those measurements.

### LPLC2

The same quantities are **not measured** for the same reason. Localized,
tiling receptive fields are a biological motivation, not evidence that the
selected bodies have been linked to columns in this run.

### Shared linkage limitations

The body-level query must separate visual/dendritic input synapses from
central-brain outputs using explicit `kind`/ROI provenance, not coordinate
thresholds. Hierarchical ROI memberships must not be summed naively. The
published column assignment file documents left/right columns and missing or
uncertain anchors, but the public materials inspected do not expose a
validated machine-readable column-to-eye-map coordinate transform with
orientation and uncertainty semantics for this candidate.

Gate 2 therefore remains pending rather than yielding a D2, D3, or D4
scientific conclusion.

## Gate 3 — bounded morphology feasibility

Gate 3 was not entered because the credential stop condition applied before
the live Gate B/D work. No skeleton or synapse query was made, no morphology
data was written, and no morphology statistics exist. Consequently, raw
fragmentation, component sizes, bounding boxes, cable lengths, and dendritic
territories remain unresolved. No skeleton healing occurred.

## Independent scientific interpretation

### LC4

The 16-body sample is valid and deterministic, but no live input anatomy was
retrieved. An individual LC4 body therefore cannot yet be assigned a
reproducible visual-input spatial representation from this phase. This is an
unresolved Gate B/D result, not a D4 conclusion: D2/D3/D4 adjudication remains
pending the credentialed body-to-input-ROI/column check.

### LPLC2

The 16-body sample is valid and deterministic, but no live input anatomy or
four-layer dendritic morphology was retrieved. An individual LPLC2 body
therefore cannot yet be assigned a reproducible visual-input spatial
representation from this phase. This is an unresolved Gate B/D result, not a
D4 conclusion: D2/D3/D4 adjudication remains pending the credentialed
body-to-input-ROI/column check.

### Future NeuroFly encoder

Only the Phase 1C population-level sensory boundary is scientifically
defensible for current operation. Body-specific or column-space encoding is
not justified yet, and no azimuth/elevation conversion may be introduced.
This status does not imply that a MaleCNS-native mapping cannot be derived.

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
| NeuroFly-derived | Phase 1C looming geometry, benchmark labels, deterministic sample hash, centroids/polygons/normalization if later computed. | The deterministic sample ranks/digests are recorded; no RF derivation or morphology summary was produced. |

The audit did not transfer FAFB/FlyWire body IDs or coordinates, use body ID or
soma side as a visual coordinate, use DNp01 connectivity or structural weight
as an RF, or introduce physiological weights/neural dynamics. No skeleton
healing occurred because no skeleton was queried.

## Smallest next phase

Keep the Phase 1C population-level sensory approximation for experiments. The
smallest scientifically justified follow-up is a credentialed, read-only Gate B
query on exactly the 16 deterministic LC4/LPLC2 bodies. Confirm body
annotations, visual-input synapse/ROI linkage, bilateral column identity, and
the versioned column-to-eye-map transform. Run Gate D raw `heal=False`
skeleton inspection only if Gate B/C cannot identify body-specific topology.
Do not acquire the remaining visual population, reverse-engineer rendered eye
maps, or implement neural dynamics as part of that check.
