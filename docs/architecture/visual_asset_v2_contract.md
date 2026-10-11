# V1 visual asset foundation — static v2 contract

This is a visual-asset compatibility foundation, not an asset replacement or a
scientific phase. The selected runtime manifest remains fly_visual_v1.json and
the committed GLB/Blender source are unchanged. No external model was downloaded.
V2 is opt-in: a future reviewed manifest selects a new GLB only after its rights,
container integrity, browser behavior and performance have been verified.

## Ownership and scientific boundary

```text
Canonical playback API -> validated DTO -> existing cursor/scene adapter
    -> scientific pose group (recorded translation / model-space orientation)
        -> flyPresentationFit (display-only offset, rotation and uniform scale)
            -> prepareFlyVisual (asset-local hierarchy and owned materials)
                -> cached GLTFLoader geometry/textures, immutable
```

No replay adapter, API, equation, clock, camera or scene composition was changed.
Baseline remains stationary, neural-only horizontal motion has no body, and
course control still maps only recorded orientation. Wings, legs and antennae
have no autonomous animation, gait, physics, sensory encoding or neural coloring.
A realistic appearance must never be described as MaleCNS-derived whole-body
anatomy, measured biomechanics, consciousness or complete biological emulation.

## Versions and required metadata

The existing neurofly_visual_asset_manifest_v1 schema retains its exact identity,
path, hash, zero-texture/static requirements and historical appearance.
parseFlyVisualAssetManifest dispatches explicitly to v1 or v2. Unknown schema or
mismatched asset_version fails, rather than accepting a partial configuration.

V2 schema: neurofly_visual_asset_manifest_v2, asset_version 2, role
NEUROFLY_VISUAL_ASSET. Required fields:

| Field | Contract |
| --- | --- |
| asset_id | Nonempty visual identifier; not a scientific experiment identity |
| runtime | Same-origin /assets/fly/<safe-name>.glb, matching web/public path, SHA-256 |
| export | Blender and tool_version |
| specimen | Drosophila melanogaster; male/female/unspecified; reference_basis |
| canonical_transform | Blender +Z up/-Y forward; runtime +Y up/+Z forward/-X left; thorax center; normalized +Z extent 1.0 arbitrary asset unit; finite position/Euler radians and positive uniform display scale |
| bounds | Finite min/max, positive dimensions and normalized Z extent |
| nodes | Root, required names and optional names; unique/disjoint identities |
| materials | AUTHORED_PBR; disjoint nonempty body/eyes/wings material-name roles; thin-wing alpha/side contract; texture role/color-space declarations |
| capabilities | static=true; skeletal_animation=false; morph_animation=false |
| measured | Positive triangle/material counts; nonnegative texture-image count; zero animation/camera/light counts |
| provenance | Public source URL, author, original license, license version and URL, attribution, source hash, modifications, material origins, texture-rights statement, exporter version |
| scientific_status | presentation_only=true and explicit limitations |

Unknown top-level fields are rejected. Runtime paths cannot reference arbitrary
remote hosts, credentials or queries. License/source links use HTTPS and exclude
queries/fragments/userinfo; licensing text records evidence, not legal approval.
No biological size, mass, mechanical coefficient or scientific gain is invented.
Species/sex are represented-asset declarations, not proof of anatomical accuracy.

Texture roles: base_color and emissive use sRGB; normal, metallic_roughness and
occlusion use linear data (Three.js NoColorSpace). The runtime checks used maps
against declarations, color space and the UV channel. Authored shaders must be
MeshStandardMaterial or MeshPhysicalMaterial, including their PBR maps. Other
custom shader families are outside this initial contract. Texture objects are
shared read-only; no recoloring, wrapping/color-space mutation or texture disposal
is performed by an instance. Maps not exercised by current fixtures require real
asset/browser inspection before V2 acceptance.

## Fitting and legacy preservation

flyPresentationFit is the shared adapter used by both renderers. It returns only
local presentation transforms and never consumes scientific body state.

- V1 historical: manifest position [0,0.78,0], zero rotation, scale 2.0.
- V1 scenario: explicit legacy position [0,0.64,0], zero rotation, scale 3.3.
- V2: both renderer profiles use the same manifest fitting values.

The legacy exceptions preserve exact current camera composition; they are not
biological dimensions. Parent replay transformations remain outside this layer.
A new asset must normalize its geometry before export, not request scientific
coordinate changes to compensate for its size or orientation.

## Anatomical names, hierarchy and static capability

Required names anchored to v1: Head, Thorax, Abdomen, Eye.L, Eye.R, Wing.L,
Wing.R, Leg.L.Front, Leg.L.Middle, Leg.L.Rear, Leg.R.Front, Leg.R.Middle,
Leg.R.Rear. A distinct manifest-named root has an identity local transform and
contains every required node and rendered mesh. Required nodes occur exactly
once. Optional declared nodes may be absent, but cannot be ambiguous/overlap.

Optional future names may include WingAttachment.L/R and named leg-segment
attachment groups. These are static visual organization only. No skin, morph
target, animation clip or asset-local light/camera is accepted. Naming attachment
points does not establish measured joint mechanics or authorize animation.

prepareFlyVisual checks actual hierarchy, bounds, triangle/material counts,
material roles, used texture/UV/color spaces and wing alpha/side behavior before
cloning. Wings require DoubleSide and the declared BLEND (transparent, no alpha
cutoff) or MASK (alpha cutoff, opaque render mode) contract. Authored opacity,
depthWrite and other PBR values are preserved, never guessed from body colors.

Each instance owns cloned nodes and unique cloned materials; sharing inside an
instance is retained. Loader-cache geometry/textures and source materials remain
owned by the loader. Disposal releases only instance materials. activate/dispose
allows React effect cleanup/re-setup without permanently suppressing later
cleanup. Both renderers retain their established loading/error behavior. The
historical renderer now clones instead of reparenting the shared cached scene.
The scenario v1 body/eye/wing treatment and shadow flags remain unchanged.

## Provenance record and candidate assessment (2026-10-09)

Primary metadata inspected without a model download:
https://api.sketchfab.com/v3/models/0affd20207ca4c889bd7e1e513e04dfa

Listing: Wildtype Male Drosophila Melanogaster; author mlykouretzos;
downloadable=true; 1,053,144 faces / 527,208 vertices. Current API declares
CC Attribution, linked to CC BY 4.0; author credit and commercial use permitted.
It reports animationCount=0 and textureCount=0, with an empty description.
Direct listing access was unavailable through the web tool; public API metadata
was independently accessible. No geometry, UVs, rigs or texture files inspected.

CC BY 4.0 permits sharing/adaptation with appropriate credit, license link and
modification disclosure: https://creativecommons.org/licenses/by/4.0/
The listing's male designation does not demonstrate anatomical accuracy. The
empty description supplies no scan/specimen/reference-method evidence. There
are no disclosed included textures whose independent rights can be certified.
Any subsequently discovered files and every newly authored/acquired texture must
receive its own provenance review. Do not assume a listing license resolves all
third-party rights or endorsement.

Recommendation: CONDITIONAL geometry candidate, not an accepted runtime asset.
It is approximately 53 times the provisional triangle budget if its reported
faces correspond to triangles. Retopology/UV/material work and independent male
anatomy review are required. Its present metadata does not establish a textured,
rigged or biologically validated model. A million-face source must not be served
as the runtime GLB. No adoption or download is authorized by this V1 task.

Alternative: author an original Blender asset from properly licensed male
anatomical references. This offers controlled topology, proportions, UVs and
material provenance but greater authoring effort. Keep the existing project asset
as the compatibility baseline; its reuse status remains
PROJECT_CREATED_TERMS_UNSPECIFIED, not an assumed open license.

Future provenance should additionally identify license version, exact source
revision/hash, anatomical reference basis/specimen sex, retopology, UV work,
texture authors/rights, artistic changes, export/optimization tools, output hash,
attribution text and limitations. These belong exclusively to visual metadata.

## Provisional V2 budgets and acceptance

Initial proposals: <=20,000 triangles, <=6 material slots, approximately <=2 MB
transferred GLB and <=16 MiB decoded texture memory. Target p95 frame time below
33 ms on explicitly named devices/browser versions, near-idle paused rendering,
and no progressive GPU allocation after repeated navigation. These are proposed
future gates, not measurements or claims about the current application.

Before replacing the selected manifest, extend offline container verification
for the actual v2 GLB (content hash, images/UVs, complete static export and measured
metadata). The existing Python verifier intentionally continues certifying v1;
synthetic metadata tests do not certify a future binary. Inspect actual materials,
transparency sorting, both fitting profiles, source bounds and licensing files.
Browser gates: asset fetch/load/error, neutral Baseline, all canonical replay
transforms and hashes, repeated independent instances, StrictMode/remount/disposal,
WebGL errors, desktop/mobile framing, alpha-wing appearance and performance.
No browser-level result is claimed by this local foundation.

## Local verification evidence

Current result: V1_VISUAL_ASSET_CONTRACT_LOCAL_VERIFIED.

Executed on the final candidate:
- Full .venv/bin/python -m pytest: 1,304 passed, one authenticated integration
  test deselected by canonical configuration, two existing Starlette/httpx and
  AnyIO deprecation warnings; 880.00 seconds.
- Focused pinned provisioning/readiness test: one passed, including all five
  complete canonical payload SHA-256 comparisons; two existing warnings.
- Frontend npm test: 98 passed, including ten new visual-contract/instance tests.
- npm run lint, typecheck and build: passed. Typecheck was also rerun after
  restoring only the build-generated Next declaration paths to their original
  development paths. No unrelated declaration change is retained.
- Ruff check and format check: passed, 356 files formatted; git diff --check passed.
- Existing read-only Blender asset verifier: passed, unchanged GLB hash
  bc49dc056a9fee62779de38367e2f868eccdc4356f88412b72401cc149e0c49e,
  76,996 bytes, 3,960 triangles, three materials, zero animations.
- Existing Node Blob SDK suite: 23 passed; retrieval code unchanged.
- Source packaging dry-run and targeted source/frontend-static credential scan:
  passed; no deployment created. Final counts are recorded in the final response.

No Blender re-export was performed, because it would regenerate the selected
asset. Browser/WebGL, real-device performance and a real v2 binary remain future
V2 acceptance gates. A transient TypeScript narrowing error and command-working-
directory mistakes were corrected; no final mandatory gate remains failed.
Tests use synthetic metadata and simple fixture geometry only under web/tests;
no fabricated production v2 manifest or GLB is selected or saved. The tracked v1
manifest/GLB/Blender source, scientific authorities and playback adapters remain
unchanged. No new dependency, Git publication or provider mutation.

## V2-D — explicit static combined body and source-node identity

This local extension supersedes the universal separated-body requirement above
for explicitly declared static composite assets. It does not accept the external
prototype as finished, change the selected v1 manifest, or waive material,
provenance, static geometry, bounds or origin checks.

Current renderers consume the specimen as a whole. ScenarioWorld translates a
parent group from scenarioScene; CourseControlWorld rotates a parent group from
courseScene; historical PlaybackCanvas mounts the fixed fitted specimen without
independent anatomical transforms.
No current caller transforms Thorax or Abdomen separately. Baseline neutral pose,
neural-only horizontal-motion absence of a body, replay timing and scientific
payloads remain unchanged. Separate body meshes are a visual organization choice,
not a requirement of the frozen scientific data.

Optional v2 `anatomy` metadata has two exact variants:

```json
{"body_topology": "separated"}
```

```json
{
  "body_topology": "combined",
  "body_node": "Torso.Unseparated",
  "limitation": "One static joined thorax/abdomen surface; no independent articulation or validated anatomical separation."
}
```

These examples describe visual metadata only; no production manifest is created.
Absent anatomy retains the original v2 separated contract, including both Thorax
and Abdomen. Explicit separated accepts no combined-body fields. Combined requires
its named real node in nodes.required, plus Head, both eyes, both wings and all six
legs. Thorax/Abdomen cannot also appear in required/optional declarations. Unknown
modes, empty limitations, reused root/other anatomical identities and missing body
names fail closed. The combined node may be a mesh or a group containing actual
mesh geometry; an empty placeholder is rejected. Validated anatomical regions
cannot claim the same mesh object via nested/alias groups. Child anatomical regions retain ownership of their own surfaces, so eyes may
nest under a head with its own geometry; a group containing only other regions
cannot fabricate its missing surface. Shared immutable buffer geometry across
distinct mesh instances remains permitted.

Both modes remain static: no skins, morphs, clips, asset cameras/lights or new
motion. Optional attachment names are organization only. This variant would cease
to suffice if a future scientifically authorized renderer needed independently
validated thorax/abdomen transforms or deformation; it cannot supply that rig.

### Original glTF node identity

The installed Three.js 0.186.0 GLTFLoader normalizes punctuation and uniquifies
runtime names. Eye.L becomes EyeL; another source node named EyeL can become a
different runtime name. Matching by globally stripping punctuation would alias
those distinct source identities and is prohibited.

visualNodeIdentity reads parser.associations for each loaded object, validates the
source `nodes` index and takes the exact name from parser.json.nodes[index]. This
is the mapping exposed by the installed loader/types, covered by actual-loader
regressions; keep those tests when updating Three.js. Duplicate source names,
reused/invalid source indices and missing anatomical identities fail closed.
Scene wrappers and primitive children without node associations are not guessed
from runtime names or untrusted glTF extras. Direct offline Object3D fixtures use
an explicit no-parser path with unique exact object names. Both application loader
callers supply the real parser; v1 continues its existing rendering path.

No cached names, geometry, textures or source transforms are rewritten. Materials
are still cloned per instance and maps shared read-only. V2 wing shadows use their
validated material role, including primitive children without a Wing-prefixed
runtime name; authored opacity/maps/side/depthWrite remain intact. V1 colors,
shadow policy and both legacy fitting profiles are unchanged.

### Origin and external prototype limitations

Combined geometry does not validate a pivot. A visually selected thorax anchor can
be established on a combined mesh without physically separating it, but must be
supported by inspection and recorded independently of replay pose. No new anchor,
pivot offset or fitting value was selected in V2-D. At the V2-D checkpoint the contract required
a declared thorax-centred origin; the V2-C joined-body AABB midpoint
is provisional and cannot honestly satisfy that declaration yet. Final asset
acceptance remains blocked until its anchor is reviewed. Do not label that pivot a
measured biological centre of mass or change scientific pose to compensate.

Read-only inspection of the real external V2-C GLB validates 284 unique source-node
identities, including Torso.Unseparated, both eyes/wings and six legs. This proves
identity recovery, not complete model acceptance. Eye defects, unclassified fine
geometry, opaque inspection wings, source-color transfer, UV/PBR, anchor and browser
performance remain external asset work. ZIP/V2-B/V2-C checkpoints are not changed.

### V2-D validation scope

Tests add an offline generated GLB fixture parsed by the installed GLTFLoader,
including punctuation collisions, duplicate original names/source indices, both
body modes, actual composite mesh groups, missing/empty/alias geometry and wing
primitive handling. Existing real v1 GLB, material ownership/PBR and replay tests
remain. Canonical CI never depends on external workspace files. The external V2-C
identity check is a separate read-only local observation.


### Resume: clone identities and TypeScript fixture correction

Parser associations reference the original loader objects and do not survive
Object3D.clone(true). The original source is validated first. prepareFlyVisual
then returns nodeIdentities mapped explicitly to that instance's cloned nodes,
using the ordered hierarchy produced by clone(true). No source name, parser map,
geometry or texture is modified. Each instance has its own identity map and node
objects; material clones remain instance-owned, buffer geometry/maps shared.
Changed hierarchy, missing counterparts or two identities claiming one cloned
object fail. Passing a cloned scene to the original parser is rejected instead
of silently returning an empty map or guessing from normalized names.

Real-loader offline tests exercise both separated and combined manifests,
punctuation collisions, two independent renderer instances, unchanged source
transforms, isolated instance transforms/materials, and invalid clone maps. The
external V2-C file remains an optional read-only observation, never a CI fixture.

TS2741 was caused by a test Mesh inferred with BoxGeometry being assigned a
BufferGeometry for the degenerate-surface rejection test. Only that fixture's
combined body is now explicitly typed Mesh<BufferGeometry, MeshPhysicalMaterial>;
no any, ignore directive or production type/validation weakening is used.

### Completed local resume gates (2026-10-11)

The final frontend suite passed 107 tests (including 19 visual-contract tests).
TypeScript, ESLint and the Next.js production build passed. The focused visual
run passed 18 tests before the final invalid-clone regression was added; the
complete 107-test run includes that regression. No browser/WebGL or performance
measurement is claimed.

The full Python suite passed 1,304 tests with one configured integration test
deselected, in 908.99 seconds. Two existing deprecation warnings concern the
Starlette TestClient httpx integration and AnyIO BlockingPortal alias. The suite
includes isolated provisioned startup/readiness, fail-closed legacy catalogue
behavior and all five complete canonical playback SHA-256 comparisons. Ruff
check and format check passed (356 files); the Blob SDK suite passed 23 tests.

Read-only v1 verification retained SHA-256
`bc49dc056a9fee62779de38367e2f868eccdc4356f88412b72401cc149e0c49e`,
76,996 bytes, 3,960 triangles, three materials and no animations. The optional
external V2-C check recovered 284 original identities and mapped them to two
independent clones. This remains identity-only evidence, not acceptance of the
external geometry, pivot, UVs or materials.

Source packaging was inspected locally with the pinned Vercel file inspector;
no deployment or provider mutation was performed. Required visual/runtime and
scientific authority files were included, and environments, caches, credentials
and external source archives were excluded. Credential-pattern scans found no
new hits; the existing synthetic SDK error fixture remained unchanged. The
historical deployment report, source ZIP and V2-C checkpoint were preserved.

## V2-G: preserved model origin and explicit visual anchor

Existing v2 manifests with `canonical_transform.origin: "thorax center"` retain
exactly their previous semantics and fitting. They cannot also declare a separate
anchor. V1 and the default scientific scene asset remain unchanged.

The additive variant uses `origin: "model origin"`, a nonempty
`origin_description`, and `visual_anchor` containing `coordinate_space:
"runtime asset"`, a finite position triplet, an original-source `node` identity,
and a nonempty artistic `rationale`. The node must be an optional helper, distinct
from root and anatomical identities. It must exist inside the root, contain no
mesh, and its actual asset-space world position must match metadata within 1e-6.
Coordinates must be inside declared bounds. Missing, conflicting, non-finite or
unknown-space declarations fail closed. Root identity and static-only checks remain.

The anchor is a viewing reference, not biological data or a thorax mesh. Asset
geometry is not translated. Its presentation target is computed once as
`scene_position + EulerXYZ(scene_rotation) * (scene_uniform_scale * anchor)`.
Camera targeting uses this result; fitting still applies only the existing scale,
rotation and translation to the instance. No implicit anchor subtraction occurs.
This keeps recorded scientific pose, display fitting and asset coordinates separate.

The opt-in `/visual-lab/fly` route uses the byte-identical approved V2-F GLB and
`web/src/assets/fly_visual_v2f.json`. Runtime SHA-256 is checked before parsing;
actual source-node associations and `prepareFlyVisual` validate anatomy, bounds,
static geometry, PBR maps/UV/color spaces and instance ownership. Cached geometry
and textures remain shared read-only, materials are cloned per mounted instance.
No procedural fallback is used. The app's existing v1 scene selection is unchanged.

The preserved model origin is the joined-body bounding-box midpoint. The anchor
is runtime `[0, 0.06168119236826897, 0.12187743186950684]`; Blender conversion
`(x,y,z) -> (x,z,-y)` gives Blender `[0,-0.12187743186950684,0.06168119236826897]`.
It is an artist-selected visual pivot, not a measured centre of mass.

Viewer cameras orbit this anchor, disable pan, and reset both position and target.
Responsive framing fits projected asset bounds into both horizontal and
vertical fields of view, retaining the anchor as target. The fly is static. Optional FPS is a one-second frame-rate
sample; draw calls/triangles and geometry/texture counts come from renderer counters,
not scientific telemetry or GPU memory measurement. No mobile certification is implied.

Source: *Wildtype Male Drosophila Melanogaster*, mlykouretzos, CC BY 4.0,
https://sketchfab.com/3d-models/wildtype-male-drosophila-melanogaster-0affd20207ca4c889bd7e1e513e04dfa .
Modified for NeuroFly: selective optimization, restored original eyes, source-derived
colors and wing textures, localized UVs, artistic PBR maps and visual anchor.
The runtime asset is a third-party visualization, not MaleCNS-derived morphology.
Prior source checkpoints remain external. The viewer is not an experiment.

### Local V2-G verification

Frontend: `PATH="<repository>/.venv/bin:$PATH" npm test` (112 passed),
`npm run lint`, `npm run typecheck`, `npm run build`, and `git diff --check`.
`python3 tools/blender/verify_fly_visual.py` confirms the original v1 SHA-256
`bc49dc056a9fee62779de38367e2f868eccdc4356f88412b72401cc149e0c49e`.
The approved v2 runtime SHA-256 is
`0502cb995d25b2f9d7b57eff0cf95a0c9cfd7f838e212e95b3895bb69c7e5238`.

Chromium 134 headless / SwiftShader inspected the actual production-built local
route at desktop 1440x1080 and narrow 390x844. Overview, lateral, frontal, dorsal,
zoomed eyes, orbit/zoom and reset screenshots were reviewed. Camera reset restores
identical measured position/target; the narrow layout has no horizontal overflow.
HTTP 404, corrupted-byte checksum and WebGL-disabled cases display explicit errors.
No normal-load React, WebGL or texture errors; a pre-existing favicon.ico 404 remains.
Measured renderer counters: 284 draw calls, 46,440 rendered triangles, 282 geometries,
7 renderer textures including studio resources. Asset geometry remains 41,440 triangles
and five embedded images. Sampled software-rendered FPS is approximately 17–25,
not hardware GPU or mobile performance certification. Transparent layered wings
may still sort imperfectly at untested angles; no destructive material correction
was applied. Human visual approval and hardware profiling remain separate gates.

No backend, replay, scientific payload, v1 asset, provider or source Blender changes.
No commits, pushes or deployments were performed. Browser evidence and reproducible
Playwright scripts remain outside Git under the external assets work/v2g/browser folder.
