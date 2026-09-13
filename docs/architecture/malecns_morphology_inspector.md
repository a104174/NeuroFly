# Raw DNp01 MaleCNS morphology inspector (Phase 5F)

Phase 5F implements the first bounded MaleCNS morphology rendering slice. It
contains exactly DNp01 bodies `10001` and `10010` from `male-cns:v1.0`. The
inspector is a separate scientific mode: it contains neither the Blender fly
nor Phase 5D's abstract pathway layout and has no experiment-playback state.

## Controlled acquisition and artifact

Generate the artifact with:

```bash
python -m neurofly.malecns morphology-artifact \
  --contract data/derived/malecns/looming_giant_fiber_v1 \
  --output-root data/derived/malecns/looming_giant_fiber_v1/morphology_artifacts_v1
```

The command reloads the committed `CircuitContract`, requires mappings
`10001 -> node_index 0 / DNp01 / R` and
`10010 -> node_index 1 / DNp01 / L`, and downloads only the official bulk SWC
files below. No other body is fetched.

```text
https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/10001.swc
https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/10010.swc
```

The artifact records `source_mode=OFFICIAL_MALECNS_BULK_SWC`, each exact source
URL, and the downloaded-byte SHA-256. The source is raw SWC only: no healing,
smoothing, repair, or inferred missing structure is performed. neuPrint access
was unavailable in the acquisition environment; the official MaleCNS bulk
source is the explicit, provenance-preserving acquisition path for this slice.
Output is atomic and an existing identity is never overwritten.

The validated local artifact is currently stored at the ignored path
`data/derived/malecns/looming_giant_fiber_v1/morphology_artifacts_v1/`
under artifact ID
`719426f0cd2db586b149943483abfe6519d45c4a39fb48aa1f4a566c514c84f3`.
The source SWC hashes are `838c60b0e4724d8ca163be994012ebdc23e7ccbdcb9cde92f25e541bc4696511`
for body 10001 and
`97e1c587397bd6ec1d6489c1ff129c13b3794745f1ada4376313fdf50363d336` for body
10010. The artifact remains derived data and is not tracked in Git.

`malecns_morphology_artifact_v1` has a canonical JSON manifest and one
canonical JSON payload per body. It preserves `malecns_neuron_spatial_v1`
records, disconnected components, raw child-parent tree links, source soma
metadata when supplied, source SWC SHA-256, and per-file hashes. The logical artifact ID is
deterministic for scientific source records and excludes retrieval time.
Generation metadata is retained but is not scientific identity. Validate an
artifact offline with:

```bash
python -m neurofly.malecns inspect-morphology-artifact ARTIFACT_DIRECTORY \
  --contract data/derived/malecns/looming_giant_fiber_v1
```

Real artifacts stay under ignored `data/derived/malecns/`; they are not copied
into `web/public` or committed. No production synthetic fallback exists.

## Read-only boundary

The server uses a second explicit root:

```text
NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT=/path/to/morphology_artifacts_v1
```

`MorphologyArtifactStore` rejects malformed IDs, symlinks, corruption,
unsupported schemas, and absent bodies. Every read uses the production offline
loader. Browser-facing GET requests never contact neuPrint.

| Method | Path | Result |
|---|---|---|
| GET | `/api/v1/morphology` | Validated artifact summaries |
| GET | `/api/v1/morphology/{artifact_id}` | One validated summary |
| GET | `/api/v1/morphology/{artifact_id}/bodies/{body_id}` | Raw body components, nodes, and links |

The existing `experiment_http_error_v1` envelope maps malformed IDs to 400,
missing artifact/body to 404, integrity/schema/path failures to 409, absent
root configuration to 503, and store defects to 500. It exposes no local path,
credential, or traceback.

## Source coordinates and view transform

Artifact/API coordinates remain exact `male_cns_v1_em_native_voxels` values in
unit `8_nm_voxel`. Source x/y/z have no anatomical axis names here. The
frontend validates these identities and applies `dnp01_morphology_view_v1`:

```text
view_position = (source_position - shared_source_bounds_center) * uniform_scale
```

One bounds calculation, center, and uniform scale is shared by both bodies.
The axis mapping is identity (`source_x -> view_x`, etc.), preserving relative
native-frame positions. Original coordinates are unchanged. Bounds, center,
scale, frame, unit, and mapping are inspectable presentation state and do not
affect morphology, experiment, result, comparison, or visual-asset identity.

## Rendering semantics

Each raw component becomes independent constant-width `THREE.LineSegments`.
Bodies have separate colors and textual IDs, so color is not the only identity
cue. Source radius remains in transport but does not control line width or
imply biological calibre. Roots are not labelled soma, input, or signal
source. Child-parent serialization ordering is not biological signal
direction, and fragments are never joined.

Orbit, pan, zoom, visibility, native-axis/grid visibility, and camera reset
alter view state only. There is no activity animation, propagation, skeleton
deformation, fly alignment, or behavior inference. WebGL failure leaves source
provenance readable.

Source data are body identity, raw x/y/z, raw component topology and links,
source soma/status metadata, frame/unit, and hashes. View state is the shared
center/scale, identity axis mapping, camera, constant line width, colors,
background, grid, and visibility.

Expansion beyond these DNp01 bodies requires review of rendering correctness,
component handling, provenance readability, and performance. LC4/LPLC2 and
full-circuit morphology remain outside Phase 5F.
