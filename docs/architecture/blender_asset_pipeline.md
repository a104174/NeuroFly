# Controlled Blender/glTF fly asset pipeline (Phase 5C)

Phase 5C replaces the normal procedural fly rendering path with one small,
project-created GLB while retaining the procedural mesh as the loading and
failure fallback. This is a visual-asset boundary only. The asset is not
MaleCNS morphology, measured anatomy, a reconstructed individual, or a
connectome-derived body model.

## Source, export, and runtime separation

The controlled chain is:

```text
tools/blender/export_fly_visual.py
    -> assets/blender/fly_visual_v1.blend
    -> web/public/assets/fly/fly_visual_v1.glb
    -> web/src/assets/fly_visual_v1.json
    -> FlyVisualAsset / GLTFLoader
```

The export script creates the source scene from named Blender primitives,
saves the editable `.blend`, exports only the intended objects, and writes the
manifest containing the resulting SHA-256 and measured presentation metadata.
It uses no downloaded model, texture, camera, light, rig, animation, or morph
target.

Run the tracked export with Blender 4.0.2:

```bash
blender --background --factory-startup \
  --python tools/blender/export_fly_visual.py
python tools/blender/verify_fly_visual.py
```

For an isolated repeatability check, append
`-- --output-root /path/to/temporary/root`. The same repository-relative
source, GLB, and manifest layout is produced beneath that root.

## Asset identity and provenance

The manifest schema is `neurofly_visual_asset_manifest_v1`; the asset is
`neurofly_fly_visual_v1`, version 1, with role
`NEUROFLY_VISUAL_ASSET`. The manifest records the source/export paths, Blender
and script versions, GLB hash, counts, budgets, transform contract, and a
presentation-only disclaimer.

The source was created inside NeuroFly. The repository currently contains no
project license file, so the manifest records
`PROJECT_CREATED_TERMS_UNSPECIFIED` rather than inventing broader reuse terms.

Visual asset identity is separate from scientific identity. Re-exporting or
replacing this mesh does not change an `ExperimentConfig` ID,
`ExperimentResult` ID, experiment artifact ID, or Phase 3C comparison ID.

## Scale, origin, and axes

Blender source convention:

- `+Z` is up;
- `-Y` is fly-forward;
- the root origin is the thorax center.

The Blender glTF Y-up conversion produces the runtime convention:

- `+Y` is up;
- `+Z` is fly-forward;
- `-X` is the fly's left side;
- the long-axis `+Z` extent is normalized to exactly 1.0 asset unit.

An asset unit is not a biological meter or measured anatomical unit. The one
presentation transform is recorded in the manifest and applied by
`FlyVisualAsset`: position `[0, 0.78, 0]`, zero Euler rotation, and uniform
scale `2.0`. No corrective rotations are scattered through scene code.

## Geometry and export budget

Version 1 contains a head, thorax, abdomen, two simple eyes, two static wings,
and six simplified legs. They provide a readable stylized silhouette, not an
anatomical claim.

The tracked export contains:

- 3,960 rendered triangles against a 20,000-triangle limit;
- 3 materials against a 6-material limit;
- no texture images;
- no animations;
- no cameras or lights;
- a 76,996-byte GLB.

The export is selection-only GLB with Y-up conversion, normals, no Draco
compression, and animation/camera/light export disabled. Blender 4.0.2 emits
an environment warning that its optional Draco library is unavailable, but
Draco is explicitly disabled and the GLB has no compression extension.

Two clean exports were logically repeatable: their geometry counts, bounds,
materials, file size, and validation results matched. Blender varied internal
accessor reuse/buffer packing, so their glTF JSON internals, binary bytes, and
SHA-256 values differed. Phase 5C therefore does not claim bit-for-bit Blender
export determinism. The tracked manifest hash identifies the exact committed
runtime GLB.

## Integrity and loading

`tools/blender/verify_fly_visual.py` uses only the Python standard library. It
checks the manifest identity, repository-relative path, SHA-256, GLB header,
triangle/material counts, zero animation/camera/light/image requirements,
budgets, finite nonzero bounds, and normalized long-axis extent. Frontend tests
independently verify the same committed hash and static GLB boundary.

`FlyVisualAsset` uses React Three Fiber's `useLoader` with Three.js
`GLTFLoader`; no additional loader dependency is required. The component
receives no experiment or neural data. While loading, the Phase 5B procedural
fly remains visible. A local asset error boundary also restores that fallback
and reports a restrained presentation status without removing the Canvas,
controls, scientific summary, or timeline inspector.

Phase 5D places the asset in the centralized `neurofly_scene_layout_v1`
composition while retaining the manifest's single canonical asset transform.
That surrounding layout remains presentation-only and is documented in
[`scientific_scene_composition.md`](scientific_scene_composition.md); it does
not alter the GLB, export pipeline, or asset identity.

## Scientific and behavioral boundary

The imported fly remains stationary. Its materials do not encode neural
activity. Existing abstract LC4, LPLC2, DNp01 10001, and DNp01 10010 indicators
retain their Phase 5B mappings; the looming proxy and `NOT_EVALUATED` status are
unchanged. No playback clock, timeline lookup, scientific value, spike
semantics, neural equation, motor command, or behavior is introduced or
modified.

A later asset version can improve morphology or materials without affecting
scientific experiment identity. Rigging or animation requires a separately
controlled meaning before it may be introduced.
