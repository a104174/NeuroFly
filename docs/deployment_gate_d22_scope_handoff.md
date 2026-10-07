# Deployment Gate D2.2 resume — corrected release ownership

Decision: `STORAGE_PROVIDER_OPERATOR_ACTION_REQUIRED`.
Status: `READY_FOR_OPERATOR_ACTION`. No remote release is verified.

This resumes the committed authentication handoff, rather than restarting D2.2.
Initial clean `main == origin/main`:
`af63e08a245172288cfb4bc7ce394c617763cbe5`.
The authentication handoff, D2 and D2.1 are committed; diff check passed.

## Completed resumed checks

- Vercel CLI **62.7.0**, Node.js **24.11.1**.
- `whoami` succeeds as **hcruz**. No authentication token was inspected or printed.
- Installed `blob --help` and help for store listing/creation/upload/retrieval
  were inspected. Private access, explicit pathname, no-random-suffix and
  no-overwrite options are supported; both upload booleans default to false.
- The inventory, manifest and existing archive passed committed D2 verification.
  No rebuild or scientific artifact regeneration occurred.

Frozen inventory ID:
`cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`.
Frozen manifest ID:
`e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`.
Archive bytes: **3,674,299**. Archive SHA-256:
`12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`.
All 74 original inventory files retain exact sizes/hashes.

## Ownership correction — authoritative user direction

The previously referenced `andrepintos-projects-24230ca3` scope came from an
unrelated external connector account. The NeuroFly user explicitly confirmed
that it is not owned by or associated with this project. It is **invalid and
excluded from NeuroFly deployment authority**, not an alternative destination.
Its historical appearance does not authorize querying, mutating, reusing or
creating resources there. No further operations will target that scope.

The user-authenticated CLI session is the operational authority and lists only:

| CLI scope | Team name | Plan |
| --- | --- | --- |
| `hd-dev` | HC | Hobby |

Current verification at `e409f91e38463ea1457a77bf88ff26555aedc0ac`:
`whoami` succeeds as `hcruz`; `teams list` confirms only `hd-dev` / HC, Hobby.
The worktree started clean: this handoff had been committed since the previous
turn. The user authorizes its correction. No scientific files differ.

## Authorized continuation

**`hd-dev` / HC is the sole user-authorized NeuroFly release scope.** Ownership
is resolved; no further ownership choice or login to the excluded account is
required. Continue store enumeration and any private-store creation exclusively
through the authenticated Vercel CLI with explicit `--scope hd-dev`.

No personal/team destination was guessed. Store enumeration in `hd-dev` returned
no stores. One dedicated store was then created using the authenticated CLI:

- Name: `neurofly-runtime`.
- Safe identifier: `store_S3zkyGCIjHi3p79M`.
- Scope: `hd-dev` / HC, Hobby.
- Access: **private**, independently confirmed by `blob get-store` and the
  authenticated store-metadata API.
- Region: `iad1`; status available; billing active.
- Provider reports zero objects and zero bytes; no connected projects.
- Dashboard:
  <https://vercel.com/hd-dev/~/stores/blob/store_S3zkyGCIjHi3p79M>.

The store is retained for continuation. No object was uploaded, overwritten or
deleted. No frontend project was created/linked and no backend was deployed.
The original authentication handoff remains unchanged; its missing-account-
authentication observation is historical, not the current blocker.

## Remaining operator boundary — store transfer credentials

`blob list --scope hd-dev --prefix <content-addressed-prefix> --limit 100`
fails with **No Vercel Blob credentials found**. The authenticated store metadata
response provides access/identity metadata, not transfer credentials. Thus the
exact-key existing-object check is not completed, despite the store's reported
zero-object count. Account login is not object-transfer authentication.

Configure the **existing store's** `BLOB_READ_WRITE_TOKEN` externally in the
release-tool execution environment. Obtain it through the authenticated store
dashboard; do not paste it into chat, command arguments, tracked files or logs.
The CLI documents this server-side environment credential for unlinked/local
execution. Do not create/link a frontend project merely to obtain OIDC access.
Do not create another store or repeat account login to resolve this boundary.

The exact frozen object key is:

```text
neurofly/runtime/v2/12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz
```

The ignored local archive with that basename remains under
`data/derived/runtime_bundles/`. Continue from **exact-key existing-object check**
in this store, not store creation or artifact generation. Retrieve an existing
object and compare SHA-256 before reuse; otherwise upload the verified archive
with private access, no random suffix and no overwrite. Then retrieve into a
fresh temporary file and run the committed D2 verifier and
`tools/provisioned_runtime_validation.py`, followed by full quality gates.

No remote release JSON was created because cloud round-trip verification has not
occurred. Cloud-derived provisioning, `/health`, `/ready`, all five playback
identities, eight historical replays and post-run hashes are NOT_RUN. Full
repository quality gates are pending successful round-trip; no PASS is claimed.

## D3 boundary and operational observations

D3 must pin the store identifier, exact key, archive SHA-256, inventory ID and
manifest ID above. Frontend: **no Blob credential**. Backend build/release:
authenticated retrieval access only; if the provider requires a read-write
credential, restrict it operationally to controlled release tooling, not browser
or runtime execution. Baked backend runtime: **no Blob credential**. No claim of
a provisioned remote release or available read-only token is made here.

Upload/retrieval/download hashing/provisioning/startup-readiness timings are
NOT_RUN. Provider stored bytes are zero; the verified local archive is
3,674,299 bytes. Future rollback pins a previously verified content-addressed
object; it never edits an object in place. No mutable alias or overwrite was
used. Account/store-management access was exercised only in `hd-dev`.

Current official private-storage/CLI documentation was checked alongside the
installed CLI help:
[private storage](https://vercel.com/docs/vercel-blob/private-storage),
[Blob CLI](https://vercel.com/docs/cli/blob).
The Vercel CLI/storage skills informed the explicit-scope and secret-handling
checks. No provider credential was read, logged or committed.

Only this non-secret handoff document was modified. No scientific/application code,
frozen authority, archive, scenario payload or prior record was modified.
No Git staging, commit or push occurred.
