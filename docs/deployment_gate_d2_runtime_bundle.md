# Deployment Gate D2 — immutable runtime release

## Authority and scope

The clean starting checkout is `f7baa1db24d2ff6c993894d4edafc33d736a58cd`
(`main == origin/main`). D2.1 is committed. D1 and the earlier blocking D2
record remain unchanged. Progression: D1 inventory → D2 inventory gap → D2.1
dependency closure → this deterministic D2 release.

The exclusive bundle input is `docs/deployment_runtime_inventory_v2.json`,
schema `neurofly_deployment_runtime_inventory_v2`, inventory authority
`cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`.
All 74 entries verify, totaling 116,239,303 bytes. No scientific file is
regenerated, removed, added to the authorized set or modified.

## Release identities

The tracked sidecar `docs/neurofly_runtime_bundle_manifest_v1.json` has schema
`neurofly_runtime_bundle_manifest_v1` and canonical manifest ID
`e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`.
Its identity hashes the inner `manifest` using sorted, compact, finite ASCII
JSON, excluding the envelope's own ID. The sidecar is outside the archive to
avoid a circular archive-hash dependency. It references the inventory's
authorization rather than redefining scientific meaning.

Archive:
`neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz`

SHA-256: `12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`.
Compressed bytes: 3,674,299; ratio: 3.16% of authorized file bytes (31.64:1).
Manifest stored bytes: 27,620. Application commit and runtime release identity
are independent; these uncommitted application changes are not represented as
a new deployed Git commit.

## Format and determinism

Neither zstd nor Docker is installed locally. USTAR plus gzip uses Python 3.12's
standard library without a new compression dependency. Every entry is a regular
file; there are no directory entries. Paths are lexicographic, uid/gid/mtime are
zero, ownership names empty, mode 0444. Gzip has no filename, mtime zero and
compression level 9. Format tool revision: `ustar-gzip-mtime0-level9-v1`.

Two independent builds produced identical archive bytes and manifest bytes.
The repeatability guarantee is tested on this Python/zlib environment; a future
compressor upgrade must re-test bytes and cannot reuse a conflicting hash/key.
The manifest separately includes a deterministic canonical file-content ID.

## Commands

From the repository root (existing Python environment):

```sh
python -m neurofly.runtime_bundle_cli build \
  --inventory docs/deployment_runtime_inventory_v2.json \
  --output data/derived/runtime_bundles
```

Set non-secret release inputs, never credentials:

```sh
export NF_D2_MANIFEST_ID=e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882
export NF_D2_ARCHIVE=data/derived/runtime_bundles/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz
python -m neurofly.runtime_bundle_cli verify \
  --inventory docs/deployment_runtime_inventory_v2.json \
  --manifest docs/neurofly_runtime_bundle_manifest_v1.json \
  --expected-manifest-id "$NF_D2_MANIFEST_ID" --archive "$NF_D2_ARCHIVE"
python -m neurofly.runtime_bundle_cli provision \
  --inventory docs/deployment_runtime_inventory_v2.json \
  --manifest docs/neurofly_runtime_bundle_manifest_v1.json \
  --expected-manifest-id "$NF_D2_MANIFEST_ID" --archive "$NF_D2_ARCHIVE" \
  --destination <NEW_RELEASE_ROOT>
```

The destination must not exist. Provisioning verifies the pinned manifest,
archive hash, exact entries and every file; extraction happens in a private
temporary sibling before atomic rename. A failure never publishes a ready
destination. Release metadata is `.neurofly-runtime-release.json`, outside
scientific data. Runtime files are 0444, data directories 0555. Git-delivered
application files and authority documents must then be assembled into the
release (not into the runtime archive). Preserve the source checkout layout;
an installed wheel alone does not supply scientific documents.

```sh
python -m neurofly.runtime_bundle_cli verify-release \
  --inventory <NEW_RELEASE_ROOT>/docs/deployment_runtime_inventory_v2.json \
  --root <NEW_RELEASE_ROOT> --expected-manifest-id "$NF_D2_MANIFEST_ID"
python tools/provisioned_runtime_validation.py \
  --archive "$NF_D2_ARCHIVE" \
  --manifest docs/neurofly_runtime_bundle_manifest_v1.json \
  --expected-manifest-id "$NF_D2_MANIFEST_ID"
```

## Security and exclusions

Verification requires an externally pinned expected manifest ID, not merely a
self-consistent hash supplied beside arbitrary bytes. The v2 inventory ID is
pinned in the byte-only tooling. It rejects changed/missing files, unauthorized
entries, traversal, absolute/non-normalized paths, duplicates, links, devices,
noncanonical metadata, malformed archives and hidden content after tar EOF.
No `extractall` call or archive-supplied path is trusted. Entry sizes are checked
before streaming file contents; extracted files are independently verified.

Only v2-authorized data is packaged: 20 scientific artifacts, 42 manifests or
metadata, eight structural contracts and four source-validation dependencies.
The one raw XLSX is included because frozen replay requires it. Unrelated raw
MaleCNS datasets, other derived artifacts, developer environments, caches,
frontend assets and secrets are excluded. Ten scientific authority documents,
tracked reference metadata and application code are Git/build-delivered.

## Runtime mode and readiness

Existing local mode remains the default and requires no bundle. `/health`
continues to report process liveness. `/ready` returns 503 `LOCAL_UNVERIFIED`
locally; this does not block existing local playback.

For verified deployment mode, configure these **server-only** values:

| Variable | Value |
| --- | --- |
| `NEUROFLY_RUNTIME_MODE` | `provisioned` |
| `NEUROFLY_RUNTIME_RELEASE_ROOT` | `<RELEASE_ROOT>` |
| `NEUROFLY_RUNTIME_INVENTORY_ID` | inventory ID above |
| `NEUROFLY_RUNTIME_MANIFEST_ID` | manifest ID above |
| `NEUROFLY_EXPERIMENT_ARTIFACT_ROOT` | `<RELEASE_ROOT>/data/derived/experiments` |
| `NEUROFLY_CIRCUIT_CONTRACT_ROOT` | `<RELEASE_ROOT>/data/derived/malecns/looming_giant_fiber_v1` |
| `NEUROFLY_SCENARIO_ARTIFACT_PATH` | optional explicit in-release Phase 13 canonical directory; otherwise existing relative default |

The process working directory must be the release root. Optional morphology
and motor roots cannot escape that release; they are not required for the five
canonical scenarios. No developer absolute paths become deployment defaults.

The existing factory checks the pinned release, all 74 data hashes, ten tracked
authority documents, inventory identity and configured roots once per process.
`/ready` reads this startup result cheaply; it never replays experiments.
Invalid provisioned state returns 503 and blocks scenario playback with the
existing typed `scenario_unavailable` error. Liveness remains independent.
Invalid/nonexistent store roots may prevent application startup entirely,
which also fails closed. Responses contain safe status/authority IDs, no paths,
secrets or URLs. No network download or scientific-result cache is added.

Readiness is a startup snapshot, not continuous tamper detection. Deploy the
data read-only and restart after release changes. Playback retains its existing
canonical replay checks. Never permit runtime writes to the scientific release.

## Clean-runtime proof

The validation helper creates a new tree from the archive, separately copies
Git-delivered application/authority/reference files, and runs a child from that
root. D2.1's filesystem audit hook denies original-checkout fallback, unknown
runtime reads, all runtime writes and network access. Bytecode writing is
disabled. Hashes are verified before and after scientific execution.

Fresh results: Phase 7O, 8C, 13B, corrected 16, 18, 25, 28 and 30 all PASS;
five adapters reproduce frozen serialized hashes; all five actual FastAPI
playback endpoints reproduce canonical payload identities. Startup, catalog,
`/health`, valid readiness and invalid-pin no-fallback behavior PASS. All 74
authorized files were read, no unauthorized runtime file was read.

## Controlled storage handoff (not performed)

Recommended single release location: an operator-approved **private Vercel Blob
store** in the connected project-owning team. Read-only account inspection found
no NeuroFly project; no existing approved release store ID/token was supplied.
No project/store was created, no upload occurred, no backend host was selected.
The Vercel storage skill informed this private-store handoff, not runtime code.

Official SDK supports private access, fixed pathnames and rejecting overwrite:
[Blob SDK](https://vercel.com/docs/vercel-blob/using-blob-sdk) and
[private storage](https://vercel.com/docs/vercel-blob/private-storage).
This is operational immutability, **not a claim of provider-enforced WORM**.
Use content addressing, prohibit overwrite/deletion operationally and pin
SHA-256 independently. Never grant public write or ship credentials to browsers.

Object key:
`neurofly/runtime/v2/12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz`

Operator procedure:

1. Approve/select the private store and retrieve its credentials through the
   provider secret manager. Do not put tokens in Git, manifests, command arguments
   or logs. For SDK use outside Vercel, a server-side `BLOB_READ_WRITE_TOKEN` is
   documented; restrict its use to the release-preparation operator, not the app.
2. Run the offline verify command above. In a separate release-tool directory
   (not the web project), install the official `@vercel/blob` SDK.
3. Upload the exact archive at the key above using `put(key, archiveBytes,
   {access: 'private', addRandomSuffix: false, allowOverwrite: false})`.
   An already-existing key is not overwritten; retrieve and independently verify
   it before treating it as the same release.
4. In a fresh release-tool directory, use `get(key, {access: 'private'})`, require
   status 200 and write its stream to a new local archive. Keep credentials in
   secret environment variables. Do not print signed URLs or secret values.
5. Run the offline verifier against that downloaded archive and the tracked
   manifest with the externally pinned ID, then provision into a clean root.
6. Run the clean provisioning gate and readiness. Supply only verified local
   bytes as a container build context. Private retrieval is build/release-time
   only; the final image and HTTP process require **no storage credentials**.

The storage SDK is operator tooling only, not a new application dependency.
No `latest` pointer is required. Rollback pins a previous application commit,
manifest ID and archive hash together; immutable scientific authorities are not
manually repaired in cloud storage. No post-upload retrieval result is claimed.

## Container approach and limits

`Dockerfile.backend` uses the existing Python packaging and FastAPI factory,
preserves source/docs/reference layout, provisions the independently pinned
archive, runs as a non-root UID and keeps runtime bytes read-only. `.dockerignore`
allowlists application inputs; no developer caches/venv/raw directories enter
the application context. The separate `runtime` build context supplies only the
verified archive. Example, after operator retrieval:

```sh
docker buildx build -f Dockerfile.backend \
  --build-context runtime=<DIRECTORY_CONTAINING_ONLY_VERIFIED_ARCHIVE> \
  -t neurofly-backend:d2 .
docker run --rm --read-only --tmpfs /tmp -p 8000:8000 neurofly-backend:d2
```

Docker is unavailable here: image build/startup/size are **NOT VERIFIED**.
The repository has no Python lockfile; existing bounded pyproject dependencies
are installed without duplicating a requirements list. Pin the base-image digest
and freeze resolved dependencies when preparing the first deployable image;
this document does not claim a reproducible image dependency closure. D2 proves
scientific bundle bytes and runtime provisioning independently of a host/image.

## Deployment measurements (not replay profiling)

- Build including compression and internal verification: 1.906 s; repeat 1.904 s.
- Offline archive verification: 0.514 s.
- Verified extraction, per-file verification and read-only publication: 0.579 s.
- Independent verified extraction: 0.558 s; subsequent per-file verification:
  0.0927 s, measured against a separate clean extracted root.
- Startup byte verification: 0.139 s; readiness HTTP probe: 0.00143 s.
- Compression time is not separately instrumented; build time is not presented
  as pure compression time. These are single local observations, not benchmarks.

No frontend/backend deployment, scientific-result cache, parameter tuning or
artifact regeneration occurred. Final full Python gate: **1,264 passed, one
deselected, two existing upstream deprecation warnings, 1,071.41 s**. Focused
bundle/readiness tests: 25 passed; automated clean provisioned closure: one
passed (150.06 s); D2.1 isolated inventory regressions: 20 passed. The first full
attempt located a local-mode packaging regression introduced during this work:
unconditional import of the new readiness module into D2.1's tracked-only
checkout. Restricting the import to explicit provisioned mode resolved it;
the restarted complete suite passed. No existing scientific bug was found.

Frontend: 76 tests passed; lint, typecheck and production build passed. Ruff
check, format check and Git diff check passed. Build-generated `next-env.d.ts`
changes were restored, then typecheck passed again. No frontend diff remains.
The automated clean closure test remains available as a regression gate.

Decision: `BUNDLE_COMPLETE_STORAGE_UPLOAD_OPERATOR_ACTION_REQUIRED`.
Status: `READY_FOR_OPERATOR_ACTION`; full quality gates passed.
