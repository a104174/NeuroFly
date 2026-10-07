# Deployment Gate D2.2 resume — corrected release ownership

Decision: `D2.2_PASS`.
Status: `VERIFIED_REMOTE_RELEASE`; the storage anomaly below remains documented.

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
is resolved; no further ownership choice or login to the excluded account was
required. The resumed object transfer used only this scope and the existing
private store below.

No personal/team destination was guessed. Store enumeration in `hd-dev` returned
no stores. One dedicated store was then created using the authenticated CLI:

- Name: `neurofly-runtime`.
- Safe identifier: `store_S3zkyGCIjHi3p79M`.
- Scope: `hd-dev` / HC, Hobby.
- Access: **private**, independently confirmed by `blob get-store` and the
  authenticated store-metadata API.
- Region: `iad1`; status available; billing active.
- At creation the provider reported zero objects and zero bytes; no connected
  projects.
- Dashboard:
  <https://vercel.com/hd-dev/~/stores/blob/store_S3zkyGCIjHi3p79M>.

No frontend project was created or linked and no backend was deployed. The
original authentication handoff remains unchanged; its missing-account-
authentication observation is historical, not the current blocker.

## D2.2 remote release result — 2026-10-07

The required preflight succeeded using the supplied temporary credential
handoff and a writable npm cache at `/tmp/neurofly-npm-cache`. The credential
value was not printed, inspected, persisted in the repository or committed.
Every later Vercel CLI invocation reloaded it in that command execution and
used the same temporary npm cache.

The exact frozen object key is:

```text
neurofly/runtime/v2/12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz
```

The exact-key check found the pinned object absent. The first upload attempt
passed `--add-random-suffix false`; this CLI treated the flag's presence as
enabled and created an unintended copy at:

```text
neurofly/runtime/v2/12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar-uWy8EhI8y5cz7bIiPOgEWcImdbKmGy.gz
```

That copy was left in place because this gate does not authorize deletion. The
pinned object was then uploaded at the exact key above, using the CLI defaults
for no random suffix and no overwrite. A fresh private download returned
**3,674,299 bytes** and SHA-256
`12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`.
The committed D2 verifier passed against the remote download.

`tools/provisioned_runtime_validation.py` passed using only that downloaded
archive. It verified clean provisioning, denied network and checkout fallback,
read-only runtime data, `/health`, `/ready`, and all five canonical HTTP
playbacks. Historical replays 7O, 8C, 13B, 16_CORRECTED, 18, 25, 28 and 30
passed. The post-run check reverified all 74 runtime files and hashes.

The non-secret private release record is stored at:

```text
neurofly/runtime/v2/12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5/release-record.json
```

It is 2,761 bytes with SHA-256
`9d52b8fe9b13498b6feec43adefc38a07decbd4d9d08d0d18c0b797a8e9b0f5d`; a fresh
private retrieval matched its byte count and hash. It contains the storage
anomaly and verification outcomes, no credentials or signed URLs.
The final listing and store metadata show three private objects totaling
approximately 7.01 MB: the pinned archive, the suffixed copy and this record.

## Full quality gates

- Python: **1,264 passed**, one integration test deselected, two upstream
  deprecation warnings.
- Ruff check, Ruff format check and `git diff --check`: **PASS**.
- Frontend: **76 tests passed**; lint, typecheck and production build **PASS**.
- The build-generated `web/next-env.d.ts` change was restored, and typecheck
  passed again afterward.
- No application/scientific source, frozen authority or runtime archive was
  changed or rebuilt. No commit, push, frontend project or backend deployment
  occurred.

## D3 boundary and operational observations

D3 must pin the store identifier, exact key, archive SHA-256, inventory ID and
manifest ID above. Frontend: **no Blob credential**. Backend build/release:
controlled retrieval only; the credential used here is read-write and was not
shown to be read-only. Baked backend runtime: **no Blob credential**. D2.2
verified the remote release but did not deploy a backend.

Provisioning took 0.478 s, startup verification 0.097 s and the readiness probe
0.00071 s in this run. Upload and retrieval timings were not separately
instrumented. Future rollback pins a previously verified content-addressed
object; it never edits an object in place. The pinned key was not overwritten.
Account/store-management access was exercised only in `hd-dev`.

Current official private-storage/CLI documentation was checked alongside the
installed CLI help:
[private storage](https://vercel.com/docs/vercel-blob/private-storage),
[Blob CLI](https://vercel.com/docs/cli/blob).
The Vercel CLI/storage skills informed the explicit-scope and secret-handling
checks. The credential was loaded into the CLI process only; it was not printed,
inspected, persisted in the repository or committed.

Only this non-secret handoff document is modified. No scientific/application
code, frozen authority, archive, scenario payload or prior record was modified.
No Git staging, commit or push occurred.
