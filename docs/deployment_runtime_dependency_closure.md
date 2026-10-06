# Deployment Gate D2.1 — Complete scientific runtime dependency closure

## Outcome and frozen authorities

Decision: `DEPLOYMENT_RUNTIME_INVENTORY_V2_COMPLETE`; D2.1 status `PASS`.
D2.1 authorizes an explicit inventory only: no archive,
container image, upload or application deployment is created.

Initial clean `main == origin/main`:
`735015182ac6f5abac1b7fc90cecc642b474ae3c`; D2 blocking record, D1 and Phase 33
committed. D1 JSON and its canonical identity remain unchanged:
`edd7d36d4d4a9adcbc3df33a98dd5d474b8516f40074c8551faf8f4092ea82e2`.
Stored D1 bytes hash remains
`2e2719b09852164bdda97dac0f6ef3cd75f68670f6f531b1f70ae21bc1dc9b95`.

New [v2 inventory](deployment_runtime_inventory_v2.json):
schema `neurofly_deployment_runtime_inventory_v2`, canonical inner inventory ID
`cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`. The envelope's `inventory_id` hashes only its
`inventory` object using sorted-key, ASCII, finite JSON with compact separators.
It covers file identities, roles, reasons, gate requirements and validation
metadata; semantic changes create a new identity.

**74 ignored runtime files; 116,239,303 uncompressed bytes.**
Delta from D1: **8 files / 31,663,458 bytes**, zero removals.

v2 supersedes D1 for deployment bundle construction only. D1 remains the
historical five-scenario audit authority; neither inventory redefines scientific
models, results or artifact identities.

## Why D1 was insufficient

D1 traced product playback loading, not full historical numerical CLI replay.
D2 found the omitted corrected Phase 16 pair. Source inspection also identified
that Phase 7O's complete replay calls `execute_311` with nested/sentinel
regressions enabled:

- `_nested_128` loads the frozen Phase 7M 128-body config/result/manifest and
  compares exact states, source contributions and target responses.
- `_sentinel_regression` loads the Phase 7E config/result/manifest and compares
  exact sentinel source-state trajectories.

The product adapters validate stored Phase 7O evidence without invoking all
these historical generation/regression comparisons. That explains the additional
six files. Their ~31.6 MB is required frozen regression evidence, not a new or
unrelated source dataset. Canonical loaders validated them in the full replay.

## Deliberate audit methodology

Inspected the eight existing replay CLIs and their artifact/source loaders:
population execution/readiness, bounded scale128, relative-column sensory,
closed-loop sources, subthreshold diagnostic, looming world, HS/DNp15 validation,
exploratory orientation and course composition. Inspected FastAPI factory,
environment configuration, catalog and scenario adapters.

Then one complete read-only discovery pass executed all eight canonical CLI
replays, all five adapters, and FastAPI ASGI startup/health/catalog under a Python
stdlib audit hook. Discovery records reads and gate attribution; it does not
authorize or copy newly encountered files automatically. New paths were reviewed
against the frozen source call graph before candidate construction.

No new tracing dependency installed. The only additions were the two source-
explained regression groups and the Phase 16 pair. No questionable/unexpected
scientific data read was located.

## Exact additions

All these files are explicitly enumerated with sizes/hashes/reasons in v2:

| Repository-relative added file | Bytes | SHA-256 |
| --- | ---: | --- |
| `data/derived/malecns/looming_giant_fiber_v1/bounded_sensory_population_128_v1/3d0ec7e8ddf5baf00449f6452d538d995978b571da5ea9efc632b91228d5dcc6/experiment_config.json` | 44,284 | ffdd914eb703aef94820632dbf3129c430519ca1e29b10e31e28269f2151e82a |
| `data/derived/malecns/looming_giant_fiber_v1/bounded_sensory_population_128_v1/3d0ec7e8ddf5baf00449f6452d538d995978b571da5ea9efc632b91228d5dcc6/experiment_result.json` | 31,401,313 | f51903bba2911b1f74a712b5325730ec36f19108f176fcb06a5b6b8f8a2ce998 |
| `data/derived/malecns/looming_giant_fiber_v1/bounded_sensory_population_128_v1/3d0ec7e8ddf5baf00449f6452d538d995978b571da5ea9efc632b91228d5dcc6/manifest.json` | 1,111 | 5a39de432fd5b8c9478ed7711c3353d1f24cb31edc15b075850ce53964518a5a |
| `data/derived/malecns/looming_giant_fiber_v1/dnp01_subthreshold_diagnostic_artifact_v1/bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b/diagnostic.json` | 90,631 | e24335e0d44486857222e1b76f4fb3dc7ca1e7e78862eaecf641db4a5839f208 |
| `data/derived/malecns/looming_giant_fiber_v1/dnp01_subthreshold_diagnostic_artifact_v1/bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b/manifest.json` | 439 | 592dee368d13ea694a3a9c9e4bc72f0e47750be531d05c41b64c654ce7a1aded |
| `data/derived/malecns/looming_giant_fiber_v1/relative_column_sensory_state_v1/09a3d3ddc02c81bb5ea229bf48b76811123ebd2e20cfce17f45e72442dcb8b15/config.json` | 2,493 | ece7eccd1ee128ffdf0ec7c7262d4f8a9182ac237069590128683fcdcc767be7 |
| `data/derived/malecns/looming_giant_fiber_v1/relative_column_sensory_state_v1/09a3d3ddc02c81bb5ea229bf48b76811123ebd2e20cfce17f45e72442dcb8b15/manifest.json` | 786 | b0cd2097094ad93acd663edcd94a648fabccd54cacbfe1d2f6086c54cdf59168 |
| `data/derived/malecns/looming_giant_fiber_v1/relative_column_sensory_state_v1/09a3d3ddc02c81bb5ea229bf48b76811123ebd2e20cfce17f45e72442dcb8b15/sensory_state_result.json` | 122,401 | 91b785ec9de1509a40e14ad4096cc75282e75a8c80b46985a7bf61b54939a031 |

Phase 16's pair remains absent from frozen D1 and present in v2. Exact canonical
serialization, config/result identities, manifest integrity, byte sizes and file
SHA-256 are protected by focused tests and full isolated canonical replay.
No scientific artifact was regenerated.

## Classification and source boundaries

| Runtime category | Files | Bytes |
| --- | ---: | ---: |
| CANONICAL_SCIENTIFIC_ARTIFACT | 20 | 109,021,306 |
| CANONICAL_MANIFEST_OR_METADATA | 42 | 302,827 |
| STRUCTURAL_CONTRACT | 8 | 3,042,735 |
| SOURCE_VALIDATION_DEPENDENCY | 4 | 3,872,435 |

Every entry has a unique normalized relative path, size, SHA-256, category,
`required_by` gates, inclusion reason and Git-ignore classification.

The single raw dependency is the pinned 111,565-byte
`data/raw/malecns/optic-column-type-assignments-v1.0.xlsx`. Existing frozen column
geometry validation reads it; retaining it does not authorize other raw files.
The other three source-validation files are exact column-input/summary/manifest
records. Structural contacts remain evidence, not new efficacy or model gains.

APPLICATION_STATIC_ASSET: tracked `web/public` presentation assets are supplied
by Git/Next.js build, not by the scientific runtime inventory.
DEPLOYMENT_RUNTIME_METADATA: the tracked v2 inventory and closure tooling are
application/release metadata, not duplicated ignored scientific data.
NOT_REQUIRED_FOR_DEPLOYMENT: unobserved analysis batteries, morphology/SWC
collections, generated metrics/caches and unrelated raw files are excluded.
UNEXPECTED_DEPENDENCY: none found in the reviewed scientific dependency closure.

## Git/build delivery versus runtime bundle delivery

Application delivery: committed `src/neurofly`, Python packaging/dependencies,
tracked scientific documents, frontend source/lockfile/static assets, and
deployment metadata. The ten science documents actually read by these gates are
listed separately in v2 with byte hashes and gate attribution. They are NOT
duplicated into the ignored runtime data inventory. Interpreter/third-party/OS
files belong to the application environment, not the scientific bundle.

Data delivery: ONLY the 74 explicit `runtime_files` entries. No directory-wide
authorization. The isolated test also permits the separately copied tracked
`data/reference` registry as build-delivered content; no gate read it and it is
not in the runtime inventory.

This validates a source checkout layout, not a wheel-only or hermetically locked
container. The current source-tree-relative science-document lookup must remain
supported by the later application image.

## Strict isolated construction and no local fallback

The tooling creates a fresh temporary root and copies:

1. only tracked source/science/build files selected from `git ls-files`;
2. only the explicitly authorized runtime files;
3. the closure helper and supplied inventory as deployment test metadata.

It scans the isolated data tree before and after execution, rejects unexpected
ignored data files/symlinks, and verifies every byte size/hash. It prepends the
isolated `src` to PYTHONPATH and checks `neurofly.__file__` resolves there.
The child working directory is isolated. A guard rejects reads anywhere in the
original developer checkout except the installed interpreter/dependency
environment. Original application/science/data fallback is forbidden.

Unknown runtime paths, external data paths, writes to scientific runtime files
and network resolution/connect attempts are rejected. The guard traces Python
file-open events; this is not a complete operating-system syscall sandbox.
Source inspection and copied layout complement the tracing. No empirical claim
of universal native-library tracing is made.

The isolated read mapping exactly matched the discovery mapping: all 74 files
used; zero unauthorized data reads, zero outside-candidate files, no network.
No fallback to the normal populated data tree was needed.

## Backend startup and root configuration

The actual existing FastAPI factory and ASGI lifespan were exercised with
TestClient, not a mocked scientific response. `GET /health` returned liveness
`ok`; `GET /api/v1/scenarios` returned exactly the five canonical identifiers.

The helper clears inherited `NEUROFLY_*` configuration, then explicitly sets
experiment store, pinned Phase 13B scenario path and structural root inside the
isolated tree. Other frozen replay roots remain their existing relative paths
under that isolated working directory. Optional morphology and separate motor
API stores are intentionally unconfigured: they are outside this canonical
five-scenario scope, not silently pointed at the developer checkout.

No new server endpoint, schema, scientific kernel or caching behavior was added.

## Historical closure

All existing CLI replay identities reproduced in the isolated root:

| Gate | Canonical artifact ID |
| --- | --- |
| 7O | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` |
| 8C | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` |
| 13B | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` |
| 16_CORRECTED | `bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b` |
| 18 | `ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c` |
| 25 | `2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113` |
| 28 | `243914905c17ceb1285c645aa9e9700b602a9e22c8703c9f9ce4c7fe4f7e935d` |
| 30 | `f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581` |

The tool calls each existing CLI's public `main(["replay", ...])` entrypoint;
there is no substitute replay equation. Stored source/result comparisons and
canonical manifest checks retain their original semantics.

## Five production playback identities

Every authoritative adapter reproduced the frozen transport bytes and canonical
payload identity:

| Scenario | Artifact authority | Canonical payload identity | Transport bytes |
| --- | --- | --- | ---: |
| BASELINE_CONTROL | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` | `75d1f2856f0d896589a8b1f62fb61016d701045b760e216b7cb5fa70daa30668` | 10,290 |
| LOOMING_CIRCUIT_VALIDATION | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` | `c3387396dcffa6372287df1a7d4680bb7ba605df319af4cf10f140cfc3a4d223` | 12,021 |
| LOOMING_WORLD_EXPERIMENT | `ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c` | `d06ef32aaf054b981464948916e5687951b40f571be5286513dad8ae440f26df` | 283,219 |
| HORIZONTAL_MOTION_NEURAL_VALIDATION | `2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113` | `52554962f3e9c85c6866b5e3ec56f8a12d24340db2236ec52c7809c6ece8d404` | 138,336 |
| EXPLORATORY_COURSE_CONTROL | `f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581` | `7fddc1109495023d8f64744237796d5d8e86852abef80b6979f1994088d46806` | 453,262 |

Dependency groups: the three looming/baseline variants use pinned LC4/LPLC2
structural/column/311-population and historical downstream authorities.
Horizontal neural uses Phase 25 and committed v1/selection/context contracts.
Course control adds Phase 28 and Phase 30 artifacts plus committed observation,
orientation and composition authorities. Exact per-file per-gate relationships
are in v2. Phase 7M/7E additions are required by REPLAY_7O only; the Phase 16 pair
by REPLAY_16_CORRECTED only.

## Future bounded readiness

D2.1 does not implement /ready. Provisioning/startup must verify every one of the
74 files and the separately listed tracked science authority hashes, exact roots,
expected inventory ID and application release identity. Readiness may thereafter
report the verified startup state; it must not run expensive numerical replay
on every probe. Existing /health semantics remain unchanged.

D2 must take this complete v2 authority as its explicit file set, verify input
hashes, and safely package/provision it without updating it silently. If a new
required data read appears, stop and version the deployment authority again.

## Minimality and exclusions

All 66 inherited D1 entries were read by at least one required gate; none was
retained merely because it happened to exist. All eight added files were read by
their documented historical replay. No apparently unnecessary inherited entry
was found. Exact artifact-directory file-set checks also retain required metadata.

Scope excludes other generic experiment/morphology API pages, arbitrary new
experiments, frontend scientific recomputation and future user-edited models.
It is not an authorization for all files needed by every API endpoint.

## Reproduction and tests

From the repository, without network or archive creation:

```sh
python tools/runtime_dependency_closure.py audit
python tools/runtime_dependency_closure.py isolated \
  --inventory docs/deployment_runtime_inventory_v2.json
python -m pytest tests/test_deployment_runtime_inventory.py
```

The audit command is discovery evidence only; the isolated command enforces
the supplied v2 path whitelist. It fails if files are missing/mutated, paths
escape, extra runtime files appear, a frozen replay/payload differs, or an
unauthorized runtime read occurs.

Focused tests protect D1 byte identity, v2 relationship, hashes/sizes/counts/
classifications, Phase 16 omission history, the raw workbook, tracked-document
boundary, semantic hash mutations, unsafe paths, duplicate/extra/missing files,
symlinks and a complete fresh isolated run. No production kernel changed.

A deliberately rehashed 73-file candidate omitted the Phase 16 manifest while
retaining self-reported successful gate metadata. The isolated gate passed 7O,
8C and 13B, then rejected corrected Phase 16 with the canonical file-set error
and nonzero exit. This demonstrates that candidate metadata cannot substitute
for real closure execution. The negative probe did not modify the final v2
authority or authorize any new files.

## Quality results and Git scope

Frontend: 76 tests passed; ESLint, typecheck and production build passed. The
build's generated next-env import changes were restored to the committed form;
typecheck passed again. No frontend changes remain.

Focused fast checks: 19 passed (the twentieth is full isolated closure).
Ruff check, format check and diff check passed.
Full Python suite including the automated isolated run: **1,238 passed,
1 deselected** in 941.54 seconds. The standard authenticated integration test
remained deselected by the repository's canonical pytest configuration. Two
upstream Starlette/httpx/AnyIO deprecation warnings remain; no dependency or
framework migration was attempted. All 20 new focused tests passed in the full
suite, including the complete fresh isolated closure test.

Intended tracked scope: v2 JSON, this document, closure tooling and focused tests.
Temporary isolated trees are removed by the helper after execution. Diagnostic
read reports live outside Git. No scientific data staged, archive created,
container built, storage upload, application deployment, Git commit or push.

## Next bounded action

Resume D2 bundle creation/provisioning using the frozen v2 inventory as its
explicit authorized runtime file set.
