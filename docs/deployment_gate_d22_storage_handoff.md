# Deployment Gate D2.2 — storage authentication handoff

Decision: `STORAGE_PROVIDER_OPERATOR_ACTION_REQUIRED`.
Status: `READY_FOR_OPERATOR_ACTION`, **not a verified remote release**.

## Repository and frozen authority gate

Initial clean `main == origin/main`:
`808ce43b1afdf327545f0d6ec4a9dcb7840fc3de`.
D2, D2.1, the earlier D2 blocking record, D1 and Phase 33 are committed.
`git diff --check` passed. No prior authority record was edited.

The committed v2 inventory verifies all 74 files / 116,239,303 bytes:
`cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`.
The committed bundle manifest verifies:
`e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`.
The existing D2 archive passed the committed offline verifier, including exact
entries, safety constraints, individual hashes and inventory correspondence.

Archive filename:
`neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz`.
Bytes: 3,674,299. SHA-256:
`12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`.
Its location under `data/derived/runtime_bundles/` is ignored by Git.

No rebuild was needed. The frozen manifest captures source commit
`f7baa1db24d2ff6c993894d4edafc33d736a58cd`; the packaging work is now committed
at `808ce43b1afdf327545f0d6ec4a9dcb7840fc3de`. Do not rewrite that historical
manifest merely to replace its source-commit metadata. A future remote release
record should distinguish the committed verification tooling from the original
bundle-manifest provenance.

## Provider compatibility and access evidence

Current official documentation was reviewed:

- [Private storage](https://vercel.com/docs/vercel-blob/private-storage): private
  stores authenticate reads and writes; team-level/non-Vercel clients require
  their own credential configuration.
- [Blob SDK](https://vercel.com/docs/vercel-blob/using-blob-sdk): fixed pathnames,
  private upload/retrieval, overwrite rejection, metadata inspection and deletion.
- [Blob CLI](https://vercel.com/docs/cli/blob): team store listing, store creation,
  private object upload/download and local credential requirements.
- [CLI login](https://vercel.com/docs/cli/login): operator authentication.
- [Pricing](https://vercel.com/docs/vercel-blob/usage-and-pricing): storage,
  operations and transfer are separate usage dimensions. The proposed first
  object is approximately 3.67 MB; actual billing/allowances were not inspected.

There is no demonstrated private-storage or object-size incompatibility.
Content-addressing and overwrite prohibition provide operational immutability,
not a claim of provider-enforced WORM. SHA-256 remains authoritative.

Authenticated MCP team discovery confirms the existing team:
`team_lqFdMyuSy0bBP4cAMU8az64v`, slug
`andrepintos-projects-24230ca3`. A read-only NeuroFly project search returned no
projects. This is **not evidence that no suitable team-level store exists**.

The connected tool surface supports creating a store and getting a store by
known ID, but does not expose team store enumeration or object upload/download.
No store ID was supplied. The local runtime has no Vercel CLI binary, standard
CLI authentication file, or configured `VERCEL_TOKEN`, `BLOB_READ_WRITE_TOKEN`,
`BLOB_STORE_ID`/`VERCEL_OIDC_TOKEN` credential combination. Checked local dotenv
files contain none of those credential keys. Checks reported presence only;
no credential values were read into logs or repository records.

The Vercel storage and CLI skills informed this authentication handoff.
Creating a store before being able to inspect existing stores and transfer
objects would not complete the gate. No provider mutation was attempted.

## Exact next operator action

Authenticate the CLI in the execution environment using the existing account:

```sh
npx --yes vercel@latest login
```

Complete the deliberate browser/device authentication flow. Do not paste tokens
into chat or put them in source control. No project linking or deployment is
requested. Installing/authenticating the CLI is an operator action; it was not
executed automatically here.

After authentication, resume D2.2. Use a clean, unlinked operator working
directory and the confirmed team scope to inspect existing stores:

```sh
npx --yes vercel@latest blob list-stores --all \
  --scope andrepintos-projects-24230ca3
```

Select only a clearly NeuroFly-specific private store. If none exists, creation
of a dedicated `neurofly-runtime-releases` private team-level store is authorized
by D2.2. Verify installed CLI help before creation; do not auto-link a frontend
project. Obtain store-specific transfer credentials through the provider's
secret mechanism; account CLI login alone is not a Blob read/write credential.

## Pinned object and resumed verification contract

Exact object key:
`neurofly/runtime/v2/12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz`.

Before mutation, check that exact key. Retrieve an existing object and require
the frozen SHA-256; otherwise stop without overwriting. If absent, hash the local
archive again immediately before one private upload using a fixed pathname and
`allowOverwrite: false`, `addRandomSuffix: false` (SDK semantics). Record safe
store/object identifiers and reported bytes, never credentials or signed URLs.

Retrieve into a fresh temporary file, independently hash it, run the committed
D2 verifier, then run `tools/provisioned_runtime_validation.py` **using only the
downloaded archive**. Prefer all eight historical replays. That helper preserves
the original-data/network/write guards, validates all five adapters and HTTP
endpoints, checks `/health` and `/ready`, and re-verifies runtime bytes afterward.
Complete full repository quality gates before declaring D2.2 PASS.

No remote release record was created: inventing a store identity, object identity
or successful retrieval/provisioning state would misrepresent an uncompleted
cloud round-trip. D3 must remain gated until the real record exists.

## Secret boundary, pinning and cleanup

Release operator: authorized upload credential, external and secret-scoped.
Backend build/release preparation: prefer a scoped read-only/delegated retrieval
credential when supported; do not assume a standard read-write token is read-only.
Frontend: no Blob credential. Baked backend runtime: no Blob credential.
Never log secret values, pass tokens as command-line arguments, track signed URLs
or download bundles during scenario requests. No replay/result cache is added.

Rollback pins a previous verified key and its archive/manifest/inventory IDs.
Never edit an object in place. Do not delete the verified release needed by D3.
Later removal requires a separate explicit authorization for the exact object;
store deletion/emptying is destructive and is not authorized by this gate.

## Work and verification actually performed

Local inventory, manifest, archive and Git-ignore verification: PASS.
Store enumeration/selection/creation: NOT_RUN (operator authentication required).
Existing-object check, upload and remote retrieval: NOT_RUN.
Remote-derived provisioning, startup/readiness, five-scenario verification,
historical replay and post-execution hashing: NOT_RUN.
Full Python/frontend gates: NOT_RUN for this early-stop documentation-only turn;
no current full-suite PASS is claimed from the previous D2 run.
No scientific/application code changes, artifact regeneration, deployment,
provider mutation, Git staging, commit or push occurred.
