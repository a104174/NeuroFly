# Raw MaleCNS morphology inspector (Phases 5F–5G)

Phase 5F implements the first bounded MaleCNS morphology rendering slice. It
contains exactly DNp01 bodies `10001` and `10010` from `male-cns:v1.0`. The
inspector is a separate scientific mode: it contains neither the Blender fly
nor Phase 5D's abstract pathway layout and has no experiment-playback state.

Phase 5G extends the same contract to one fixed audited sample: LC4 12032 (L)
and 16128 (R), LPLC2 11498 (L) and 14465 (R), and DNp01 10010 (L) and 10001
(R). It does not enable arbitrary body selection or broader acquisition.

| bodyId | type | source side | node_index | nodes | components | official SWC SHA-256 |
|---:|---|---|---:|---:|---:|---|
| 10001 | DNp01 | R | 0 | 2,975 | 1 | `838c60b0e4724d8ca163be994012ebdc23e7ccbdcb9cde92f25e541bc4696511` |
| 10010 | DNp01 | L | 1 | 3,312 | 1 | `97e1c587397bd6ec1d6489c1ff129c13b3794745f1ada4376313fdf50363d336` |
| 11498 | LPLC2 | L | 2 | 2,121 | 2 | `172ed22b0ec942974d211a91d064d77a52ac49ffc3757d4fffee92d0ffa71d74` |
| 12032 | LC4 | L | 3 | 1,251 | 1 | `cd6893e4adf7eb5b8070d40e2ec5644fbfde09f98e8b231ccd56bf6e63711c3d` |
| 14465 | LPLC2 | R | 12 | 2,467 | 1 | `f7171d38867895e4bdd62ad13996573e30121a2bd2e852047417d4fb17e3467d` |
| 16128 | LC4 | R | 16 | 1,773 | 1 | `ffe661f5c0669fe54b253a2101940bd2b36d098a1c0af8caf3edee7c857354a0` |

Each source URL is the documented official base followed by `<bodyId>.swc` and
is retained verbatim in artifact provenance.

## Controlled acquisition and artifact

Generate the artifact with:

```bash
python -m neurofly.malecns morphology-artifact \
  --contract data/derived/malecns/looming_giant_fiber_v1 \
  --output-root data/derived/malecns/looming_giant_fiber_v1/morphology_artifacts_v1
```

Generate the six-body Phase 5G sample with the explicit selector:

```bash
python -m neurofly.malecns morphology-artifact \
  --sample phase5g-six-body \
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

The validated six-body artifact ID is
`a3f090d5309d9ede0e9e0f78343a618a4bafba3fea91e5a27d37927d5ec55f79`.
Its 13,899 nodes form seven raw components. LPLC2 body 11498 has two
components (9 and 2,112 nodes in canonical root order); every other body has
one. The exact source hashes and counts match the Phase 5E audit. The manifest
hash is `d408ca8c68e39115ed826b0afc20d0fcdb60a2e4093e8368cb27db37f5e4545a`.

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
frontend validates these identities and applies `dnp01_morphology_view_v1` to
the Phase 5F sample or `malecns_six_body_morphology_view_v1` to Phase 5G:

```text
view_position = (source_position - shared_source_bounds_center) * uniform_scale
```

One bounds calculation, center, and uniform scale is shared by every body in
the selected fixed sample; no body, type, side, or component is normalized
independently.
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

Orbit, pan, zoom, per-type/per-body visibility, native-axis/grid visibility, and camera reset
alter view state only. There is no activity animation, propagation, skeleton
deformation, fly alignment, or behavior inference. WebGL failure leaves source
provenance readable.

Source data are body identity, raw x/y/z, raw component topology and links,
source soma/status metadata, frame/unit, and hashes. View state is the shared
center/scale, identity axis mapping, camera, constant line width, colors,
background, grid, and visibility.

Phase 5G completes the bounded multi-type check at 13,899 nodes without new
rendering infrastructure. Expansion beyond these six bodies requires a fresh
review of rendering correctness, component handling, provenance readability,
and performance. Full-circuit morphology remains outside scope.
