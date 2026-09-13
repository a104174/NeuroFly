# MaleCNS spatialization feasibility and coordinate contract (Phase 5E)

Phase 5E establishes a source-preserving morphology boundary; it does not add
an anatomical browser view. The current React Three Fiber scene remains
`NEUROFLY_PRESENTATION_MAPPING`. Its anchors are not replaced or reinterpreted
as MaleCNS coordinates.

**Readiness: S1 — sufficient evidence for a small raw MaleCNS morphology
rendering slice.** The bounded audit retrieved raw morphology for all six fixed
bodies by exact `bodyId`, the native frame and 8 nm voxel unit are documented,
and component fragmentation can be preserved without repair. S1 is limited to
a separate inspection view that displays the source frame opaquely. It does not
authorize anatomical axis labels, alignment with the presentation fly, healed
geometry, or a full-circuit rendering.

## Evidence categories

Every future spatial field must retain one of these meanings:

- **`MALECNS_DIRECT_DATA`**: values returned for a body in the pinned
  `male-cns:v1.0` dataset, including body annotations, source coordinates,
  radii, and raw skeleton linkage.
- **`PUBLISHED_DERIVED_EVIDENCE`**: findings or transformed products reported
  by the MaleCNS authors, such as mirrored or JRC2018-template skeleton sets.
  These are evidence, but they are not the unmodified native-frame record.
- **`NEUROFLY_PRESENTATION_MAPPING`**: camera, normalized Three.js coordinates,
  colors, line shapes, and view transforms. The Phase 5D scene is in this
  category.
- **`NEUROFLY_MODELLING_ASSUMPTION`**: any future inferred correspondence,
  repair, exclusion, or biological interpretation not present in the source.

The contract never promotes a derived, presentation, or modelling value into
`MALECNS_DIRECT_DATA`.

## Authoritative source findings

The official [MaleCNS download page](https://male-cns.janelia.org/download/)
identifies the programmatic neuPrint dataset as `male-cns:v1.0`, describes the
EM segmentation as 8 nm isotropic, and publishes native-frame SWC skeletons in
8 nm units. It separately offers 1 nm precomputed, mirrored, and
JRC2018-template products. Those products therefore require distinct frame and
transform identities; they are not interchangeable with native data.

The published MaleCNS resource describes the aligned 8 x 8 x 8 nm EM volume
and the whole-CNS reconstruction ([Cell article,
DOI 10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015)).
Paper-specific derived resources are linked from the
[project repository](https://github.com/flyconnectome/2025malecns).

The installed and pinned `neuprint-python==0.6.3` client reports
`voxelSize=[8, 8, 8]` and `voxelUnits="nanometers"` for the live dataset. Its
[`fetch_skeleton()` documentation](https://connectome-neuprint.github.io/neuprint-python/docs/client.html)
defines `heal=False` as the default. The
[skeleton documentation](https://connectome-neuprint.github.io/neuprint-python/docs/skeleton.html)
states that raw skeletons may have multiple fragments/roots, healing joins
nearest fragment points and retains a minimum spanning tree, and stored root
orientation is generally not significant.

The neuPrint
[`NeuronCriteria` documentation](https://connectome-neuprint.github.io/neuprint-python/docs/neuroncriteria.html)
defines `somaLocation` as the `[X,Y,Z]` voxel coordinate of a recorded cell
body. A missing soma can instead have a `tosomaLocation` annotation on the
severed cell-body fibre, while `rootLocation` can mark entry/exit from the
sample for some neurons without a soma. None of these point fields is a neuron
centroid or a functional location. The
[neuPrint data-model guide](https://neuprint.janelia.org/public/neuprintuserguide.pdf)
documents `bodyId` as the database body identifier and `somaLocation` as the
cell-body center. `somaRadius`, where present, is source metadata rather than a
general neurite-radius interpretation.

The sources establish a common native Cartesian x/y/z volume for this dataset,
but do **not** establish anatomical names for the positive axes or an
anatomical meaning for the numeric origin. Live points report the Neo4j CRS
label `cartesian-3d` and SRID `9157`; NeuroFly preserves those facts without
inventing an anatomical axis convention. Coordinates are directly comparable
within the same pinned native frame. Cross-frame comparison requires an
explicit, sourced transform.

## Body-ID provenance

Geometry is joined only by this complete key:

```text
dataset_id + candidate_id/version + body_id
    -> validated CircuitContract neuron
    -> deterministic NeuroFly node_index + type + source side
```

Name- or type-only matching is forbidden. `node_index` is the
`CircuitContract`'s deterministic body-ID order and is not a MaleCNS spatial
identifier. The source `somaSide` annotation is retained verbatim. Side is not
inferred from x-coordinate sign, a browser transform, instance text, or a
mirrored asset. The live MaleCNS sample returned `L` and `R`; generic neuPrint
documentation may use different controlled labels for other datasets.

The six-body audit sample was selected reproducibly as the lowest body ID for
each available type/side pair in the validated 313-body contract:

| Type | Source side | bodyId | node_index | instance |
|---|---:|---:|---:|---|
| LC4 | L | 12032 | 3 | `LC4_L` |
| LC4 | R | 16128 | 16 | `LC4_R` |
| LPLC2 | L | 11498 | 2 | `LPLC2_L` |
| LPLC2 | R | 14465 | 12 | `LPLC2_R` |
| DNp01 | L | 10010 | 1 | `DNp01(GF)_L` |
| DNp01 | R | 10001 | 0 | `DNp01(GF)_R` |

All six were `Traced`. That is a reconstruction-status annotation, not a
physiological or spatial-accuracy score.

## Raw skeleton semantics

`Client.fetch_skeleton(body_id, heal=False, format="pandas")` yields one row
per skeleton sample with `rowId`, `x`, `y`, `z`, `radius`, and `link`.
`link == -1` denotes a component root; otherwise `link` is the parent row ID.
The source association is the requested `bodyId`, which the future record must
store explicitly rather than infer from geometry.

The child/parent ordering is serialization tree linkage only. It is not axonal
direction, dendritic direction, signal flow, soma origin, or synaptic
direction. A root is likewise a representation artifact unless separate
source evidence gives it another meaning. Radius is preserved exactly as the
SWC numeric field; NeuroFly does not reinterpret it as measured cell-body size
or physiological calibre.

## Fragmentation and raw-versus-healed policy

One `bodyId` is not assumed to equal one connected tree. Each raw connected
component is serialized independently, its node and edge counts are retained,
and the body-level `component_count` is explicit. All components remain
renderable, with an inspection warning when the count exceeds one. Components
must never be joined merely to simplify a mesh.

Raw/unhealed morphology is the default and the only mode authorized for the
first renderer. `neuprint-python` healing finds nearest points between
fragments and selects repair connections with a minimum spanning tree. Such
links are algorithmic repairs, not observed morphology. The v1 schema assigns
every link one of:

- `MALECNS_RAW_SKELETON_LINK`;
- `NEUROFLY_ARTIFICIAL_REPAIR_LINK`.

A `RAW` record rejects artificial repair links. A future `HEALED` record may
contain them only with the explicit provenance value; healed geometry must be
visually distinguishable and cannot replace the raw identity. Phase 5E neither
fetches nor stores healed geometry.

## `malecns_neuron_spatial_v1`

`neurofly.malecns.spatial` implements the small immutable contract without a
network loader, cache writer, browser transform, or renderer:

- `NeuronSpatialRecord`: schema, dataset/candidate/body/node/type/side
  identities, evidence category, morphology source/mode, coordinate frame/unit,
  source SWC hash, optional source soma point, and ordered components;
- `SkeletonComponent`: an independently connected tree with ordered source
  nodes and explicit links;
- `SkeletonNode`: stable local source ID, unmodified x/y/z, and optional
  radius;
- `SkeletonLink`: child/parent serialization IDs and mandatory raw/repair
  provenance;
- `SpatialPoint`: finite source-frame x/y/z.

For the current native source the project-defined, evidence-linked labels are:

```text
coordinate_frame_id = male_cns_v1_em_native_voxels
coordinate_unit     = 8_nm_voxel
```

The frame ID is an opaque NeuroFly contract label for the official native EM
frame, not a claim about anatomical axes. The record validates exact linkage
against a `CircuitContract`, preserves component separation, rejects nonfinite
coordinates and hidden repair links, and serializes to canonical JSON-safe
types. `spatial_record_id` is a SHA-256 of that canonical scientific record;
`source_swc_sha256` separately pins the retrieved raw source bytes.

No field stores scene coordinates, centering, normalized scale, camera state,
or a Three.js transform. A view change therefore cannot change morphology,
experiment, result, artifact, or comparison identity.

## Fixed-sample live audit

On 2026-09-13, with credentials supplied through the existing environment, a
read-only query retrieved the six exact body records and called
`fetch_skeleton(body_id, heal=False, format="swc")` once per body. No healed
request, remote mutation, bulk circuit download, or repository write occurred.
Counts and ranges below were computed in memory from the returned raw SWC.
Coordinates and radii are in the native 8 nm voxel unit.

| bodyId | type / side | nodes | raw links | components (node counts) | x range | y range | z range | radius range | raw-response SHA-256 |
|---:|---|---:|---:|---|---|---|---|---|---|
| 12032 | LC4 / L | 1,251 | 1,250 | 1 (1,251) | 59,456–75,520 | 17,728–32,064 | 26,112–36,800 | 32–288 | `cd6893e4adf7eb5b8070d40e2ec5644fbfde09f98e8b231ccd56bf6e63711c3d` |
| 16128 | LC4 / R | 1,773 | 1,772 | 1 (1,773) | 20,288–37,440 | 27,200–39,744 | 26,496–34,624 | 32–275.074005 | `ffe661f5c0669fe54b253a2101940bd2b36d098a1c0af8caf3edee7c857354a0` |
| 11498 | LPLC2 / L | 2,121 | 2,119 | **2 (2,112; 9)** | 61,888–80,000 | 20,160–43,328 | 26,368–39,680 | 32–288 | `172ed22b0ec942974d211a91d064d77a52ac49ffc3757d4fffee92d0ffa71d74` |
| 14465 | LPLC2 / R | 2,467 | 2,466 | 1 (2,467) | 15,168–35,072 | 21,056–40,384 | 27,008–41,344 | 32–288 | `f7171d38867895e4bdd62ad13996573e30121a2bd2e852047417d4fb17e3467d` |
| 10010 | DNp01 / L | 3,312 | 3,311 | 1 (3,312) | 49,216–64,000 | 19,328–55,744 | 15,616–91,328 | 32–821.867004 | `97e1c587397bd6ec1d6489c1ff129c13b3794745f1ada4376313fdf50363d336` |
| 10001 | DNp01 / R | 2,975 | 2,974 | 1 (2,975) | 32,768–50,048 | 19,712–55,680 | 15,744–91,648 | 32–775.640991 | `838c60b0e4724d8ca163be994012ebdc23e7ccbdcb9cde92f25e541bc4696511` |

The only observed fragmentation in this sample was body 11498's nine-node
second component. It remains a separate raw component. All coordinates and
radii were finite; every non-root parent referenced a node in the same body.

Source soma points were present for all six: 12032 `[67030,31950,27092]`,
16128 `[30938,32810,29895]`, 11498 `[68710,20288,32378]`, 14465
`[27918,21096,32835]`, 10010 `[58238,22234,36276]`, and 10001
`[37124,22258,36274]`. `somaRadius` and `somaNeuromere` were null for all six.
These points are recorded cell-body locations, not skeleton roots or centroids.

## Storage and browser boundary

Bulk raw/live morphology belongs below the already ignored
`data/derived/malecns/` tree, preferably in a schema-versioned morphology
subdirectory. A future cache must include a small manifest with dataset,
candidate, retrieval mode, source/client versions, body IDs, per-file SHA-256,
record counts, coordinate frame/unit, and component counts. Small project-owned
schema metadata may be tracked; skeleton files, healed outputs, temporary
downloads, and browser geometry exports must not be committed by default.

Future rendering must retain two layers:

```text
MaleCNS source coordinates (preserved, hashed)
    -> explicit versioned view transform (presentation state)
    -> Three.js coordinates
```

The transform may center, scale, or reorient a view, but must never overwrite
source x/y/z or infer source side. Its identity is presentation-only. The first
view must remain separate from `neurofly_scene_layout_v1` so abstract model
overlays cannot be mistaken for morphology.

ROI metadata may annotate an inspection view later, but ROI hierarchies and
membership can overlap. Arbitrary ROI counts must not be summed as though all
regions were disjoint, and Phase 5E defines no ROI volumes.

## Uncertainties and first implementation boundary

- Official evidence does not assign anatomical names to native positive x/y/z
  axes or an anatomical origin; an inspection view must label them native
  source axes only.
- The exact semantic and physical convention of every skeleton `radius` value
  is not sufficiently documented for biological thickness claims; preserve it
  but initially render constant-width lines.
- `Traced` and the availability of a skeleton do not establish geometric
  accuracy at every branch.
- Native, mirrored, template, and precomputed products require separate frame
  identities and must not be mixed implicitly.

The smallest justified Phase 5F slice is a separate read-only morphology
inspection view for raw bodies 10001 and 10010 only. It should load a bounded,
hash-validated export, show components independently as constant-width lines,
display native 8 nm voxel axes without anatomical labels, and expose the
source-to-view transform. It must not align the skeletons to the visual fly,
infer signal direction, or modify the existing playback scene.
