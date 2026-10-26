# v10.4b — dedicated Recorded Experiments recovery

Local implementation on `a5aeea83722ea7fc8aa011b0d1e73065b99881c2`.
No publication, Blob upload, environment change, Production support or new
scientific execution contract is authorized by this phase.

## Cause and ownership

`ExperimentArtifactStore` is an immediate-child, Phase 3B-only collection. The
legacy `data/derived/experiments` also holds namespaced HS/DNp15/yaw/course
artifacts and scientific audit directories. Applying the Phase 3B five-file
loader to those containers produces the observed 409 before payload validation.
The loader, its canonical manifest rules, result identities, numerical tolerances
and replay remain unchanged.

The v3 runtime owns a dedicated `data/derived/recorded_experiments_v1` root. Its
only child retains the configuration-hash directory name accepted by Phase 3B.
Historical families remain at their original paths and use their native loaders.
No recursive multi-family discovery, catch-and-skip or empty fallback is added.
The existing `NEUROFLY_EXPERIMENT_ARTIFACT_ROOT` configuration is reused.

The store accepts optional required artifact identities. v3 application assembly
always supplies the pinned reference identity; a missing run produces the existing
generic `artifact_store_error`, rather than a successful empty collection. Local
callers can explicitly configure a genuinely empty collection without required
identities. Corrupt/missing/extra artifact payloads still fail with 409; unsafe
links/non-regular entries are rejected before reading; duplicate IDs retain the
existing store error. An unverified provisioned runtime cannot serve records.

## Provenance gate

The existing local source is:

`data/derived/experiments/4481c8c202c06c5d45ce8808beec28f4e9fadb2f4ae29f39c1301a8f1aaedcf1`.

Its unchanged identities are:

- Experiment: `ui_smoke_phase2f_reference_v1`.
- Artifact: `63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656`.
- Result: `8af5a3f50f0cd9fee65ce62e5421c873e95a48e32333de475545c1be7f133b45`.
- Model: `lif_filtered_synapse`, `phase2b_v1`; 80 ms; `NOT_EVALUATED`.

`docs/recorded_experiments_reference_v1.json` records all five source filenames,
sizes and SHA-256 values, source connectivity references, classification and
attribution. The reference passed the original strict loader and exact
`ExperimentRunner` replay against the existing pinned CircuitContract.
The original shell command and creation timestamp were not recorded: no new
execution history is invented. Its historic use and identity are documented in
`activity_structure_mapping.md`, `motor_escape_feasibility.md` and
`motor_pathway_model.md`. This is an authentic persisted engineering/UI reference,
not an empirically validated biological experiment.

The [official MaleCNS project](https://male-cns.janelia.org/) links the dataset to
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (checked 2026-10-25).
The reference document credits FlyEM/HHMI Janelia, University of Cambridge,
MRC LMB and Google Research, identifies NeuroFly's modelling transformation, and
does not imply endorsement. No repository-wide software licence exists; this
phase grants no general software licence. Local reference use/copying is within
the task authorization; future external publication remains a separately approved
release including its provenance/attribution document.

## Versioned local runtime candidate

The frozen D2.2 inventory, manifest and all 74 payload files are preserved.
`runtime_bundle` now accepts two explicit inventory schema/identity pairs. Its
existing safe extraction, exact file set, size, SHA-256 and tar validation are
reused unchanged for payload verification. v2 and v3 manifests cannot be swapped.

`docs/deployment_runtime_inventory_v3.json` includes the exact 74 original file
records plus five byte-identical copies in the dedicated collection: 79 files,
117,128,374 uncompressed bytes. Required API/replay gates, parent inventory identity
and the dedicated collection's purpose are explicit. The additional run is
889,071 bytes; its connectivity dependencies already exist in D2.2.

Local candidate identities (source baseline above; implementation is uncommitted):

- Inventory: `75294376accee5f52261a8cdf922638e7cc17e2aa34963364d1f9b27e6fe4d46`.
- Archive: `c5edf9edb0b1f08a0eb3e36808dd6ec25771be1bc575ce07e9cc3063aa6586cf`.
- Manifest: `4634950e8375b1d6adeb258c17e2c58a22059f9bee48663fc9fae56de68be194`.
- Compressed bytes: 3,795,667.

Candidate files and the isolated native application are outside Git under the
sibling `neurofly-assets/work/v10-4b-artifact-recovery/` QA directory. Source
payloads are not staged or relocated in the repository. No ignore rule changed.

Build locally using existing source bytes:

```sh
.venv/bin/python -B -m neurofly.recorded_experiments_runtime \
  --source-root . --output /absolute/external/candidate-directory \
  --source-commit a5aeea83722ea7fc8aa011b0d1e73065b99881c2
```

This command explicitly verifies required ignored scientific inputs. Missing data
fails with a diagnostic; it never generates a replacement. It replays the source
in memory once before packaging. Ordinary API reads never execute that replay.
`provision_candidate(root, archive, manifest, expected_id, destination)` requires
a clean external destination and an explicitly supplied expected manifest identity.
It uses the existing provisioner and adds the tracked application/authority files
in the established native layout.

The deployment build now uses the same v3 pins and provisions from the committed
archive at `runtime-distributions/v3/`. It verifies the archive, manifest,
inventory and all payload hashes before exposing the release. The original v2
archive and manifest remain unchanged and are still covered by native bundle
compatibility tests; deployed source does not fall back to v2. The build no longer
retrieves runtime bytes from Blob or requires Blob credentials/OIDC. The manifest's
`source_git_commit` remains the scientific data provenance baseline; the deployed
application commit is recorded separately from Vercel's `VERCEL_GIT_COMMIT_SHA`.

`vercel.json` enables Git deployments for `main`, and its backend build command
invokes the local provisioning script directly. Connect the existing `hd-dev/neurofly`
project to `a104174/NeuroFly`, use `main` as its Production branch, and select Vercel
Authentication with Standard Protection. Standard Protection keeps Preview deployment
URLs protected while leaving the Production domain public. After this one-time project
setup, `git push origin main` triggers the Production build and updates the live site;
there is no required Preview review, manual promotion, or Blob upload step.

## API and UI

No API version, experiment schema or response identity changed. Existing
`experiment_config_id` exposes the recorded smoke-reference ID; `result_id`,
duration and `validation_status` remain authoritative. A small shared presentation
helper identifies that exact recorded configuration in collection, detail and
cockpit, with an explicit engineering/UI reference and not-evaluated statement.
It assigns no purpose to other configurations. Recorded Experiments remains in
secondary navigation. No solver, polling or WebGL context was added.

## Verification

The focused backend gate covers authentic list/detail/timeline, immutable reads,
the config-hash directory, adjacent historical families/audits, missing required
runs versus intentional emptiness, bytes/manifests/extra files, rehashed semantic
tampering, symlinks, FIFO and duplicate identity rejection. Native historical
family replays remain authoritative. The clean application test uses copied
application sources without the editable checkout and checks all five canonical
playback hashes, the authentic run's replay, readiness and failure after corruption.
Fixtures for negative tests are disposable copies; originals remain unchanged.

Frontend integration obtains metadata from the actual API over the pinned run,
then checks the existing parser, classification and detail/cockpit links. Missing
scientific data is an explicit integration failure, never a skip or substitute.
Local production-build Chromium checks cover collection desktop/mobile (including
320 px), detail/cockpit, Explore, Science and Lab. The collection has one real
record and no canvas. Optional morphology is unavailable in the minimal runtime;
the cockpit reports that while preserving stored telemetry and playback.
Screenshots and browser reports remain outside Git. No visual redesign is made.

Commands from the repository root (frontend commands from `web`):

```sh
.venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_recorded_experiments_recovery.py tests/test_experiment_artifacts.py \
  tests/test_experiment_api.py tests/test_http_api.py tests/test_runtime_bundle.py \
  tests/test_vercel_runtime.py
.venv/bin/python -B -m ruff check .
PATH="/path/to/NeuroFly/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 npm test
npm run lint
npm run typecheck
npm run build
git diff --check
```

Final affected backend suite: **114 passed**, including **18 new recovery cases**.
Authentic frontend/reference focused tests: **40 passed**; full frontend suite:
**367 passed**, zero failures/skips. The two authentic-reference frontend tests
were repeated after the final inventory update and passed. Ruff, ESLint,
typecheck, production build and whitespace checks passed. The generated
`next-env.d.ts` route/root-params imports were compared and restored to their
original bytes. No existing scientific test was weakened or skipped.

The complete Python suite was attempted, then interrupted at an unrelated
scientific-contract workload after **148 passed, one integration deselected,
308.51 seconds**, with no failures. It has 1,839 selected cases and was not
completed; no complete-Python-suite pass is claimed. The final targeted backend
suite was rerun after the inventory/assembly changes and passed. Existing
Starlette/httpx and BlockingPortal deprecation warnings do not alter outcomes;
no dependency was installed or upgraded.

## Release boundary

The runtime archive and application source are versioned together, so every Git
deployment provisions the pinned v3 bytes from its own immutable source tree. The
source commit SHA is recorded separately from the scientific data provenance commit.
Project-level Git and protection settings remain in Vercel and are configured once;
the repository requires no deployment service, custom workflow, or mutable artifact
upload.
