# Making Neurons and the Cockpit connectome work in production

Status: investigation only. Nothing in Vercel settings, the API, data contracts or stored data was changed.

## What happens today

On production (`neurofly-liard.vercel.app`) `/api/v1/morphology` answers 503 `morphology_store_unavailable`
("morphology artifact root is not configured"). The Neurons pages and the Cockpit's connectome panel therefore
show their unavailable states. The structural connectivity API works (200), and so do scenarios and
experiments.

## Why (evidence)

| Fact | Where |
| --- | --- |
| The API only starts a morphology store when `NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT` is set | `src/neurofly/http_api.py` (`create_app_from_env`) |
| The Vercel entrypoint **removes** that variable on purpose ("optional local overrides must never redirect a deployment to local data") and never sets it | `tools/vercel_runtime_entrypoint.py` |
| So **setting the variable in Vercel does nothing**. A code change in the deployment glue is needed | same |
| The release is built from a pinned runtime bundle (v3: 79 files, 117 MB uncompressed, 3.8 MB compressed) plus Git-copied `src/neurofly` and `data/reference`. Morphology is not in the bundle: the deployment inventory called it `NOT_REQUIRED_FOR_DEPLOYMENT` | `tools/vercel_runtime_build.py`, `docs/deployment_runtime_dependency_closure.md` |
| The morphology data is 10 files, 3.1 MB (two artifacts: 2 bodies and 6 bodies), under `data/derived/malecns/…/morphology_artifacts_v1/`, which is **ignored by Git**, so it is not in the repository at all | `.gitignore` (`data/derived/malecns/`) |
| When a morphology root is set in provisioned mode, readiness requires it to exist and to be inside the release | `src/neurofly/runtime_readiness.py` |
| The store checks every artifact's integrity when it loads (hashes, no symlinks, no escaping the root) and keeps no cache: about 0.3 s per request locally. A six-body Neurons page makes about 8 requests, so roughly 2 s of API time per page view | `src/neurofly/morphology_api.py`, measured |
| The Cockpit needs the six-body artifact `a3f090d5…` plus the structural projection (which already works) | `web/src/lib/cockpitModel.ts` |
| Limits already in use: function `maxDuration` 300 s, `includeFiles .neurofly-release/**`. Adding 3.1 MB to a 117 MB release is small; check Vercel's current function size limit before relying on that | `vercel.json` |
| The repository is public and already contains MaleCNS-derived data (the tracked runtime archive). The MaleCNS data licence wording is still an open follow-up | `runtime-distributions/v3/…tar.gz`, `redesign-progress.md` |

## Options

### A. Ship the artifacts with the Git-delivered part of the release (recommended)
Track the two artifact folders (for example under `data/reference/morphology/`), copy them into the release in
`vercel_runtime_build.py` after the bundle is verified (the same way `data/reference` is copied), and make the
entrypoint set `NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT` to that in-release path instead of removing it.

- **Cost:** about one day. Adds 3.1 MB to the repository and to the function. No new infrastructure, no recurring cost.
- **Risk:** low to medium. Affects the production build of every deploy (a mistake breaks the build, not the data). Pinned bundle identities do not change. It sits outside the pinned inventory, so integrity rests on the store's own checks plus Git. The data is MaleCNS-derived and the repository is public (licence follow-up). Latency of about 2 s per Neurons page.
- **Changes:** `.gitignore` exception, the two artifact folders, `tools/vercel_runtime_build.py`, `tools/vercel_runtime_entrypoint.py`, `tests/test_vercel_runtime.py` (add a test that the in-release root is set and exists; no current test asserts the variable is removed), docs. No API, data-contract or stored-data change.

### B. Put the artifacts in a new pinned runtime bundle (v4)
New inventory listing the 10 files, new deterministic archive, new manifest and archive hash, update the pinned
constants (`vercel_runtime_build.py`, `runtime_bundle.py`, tests and docs), and set the root in the entrypoint.

- **Cost:** 2 to 4 days. Repository grows by one more archive (about 4 MB).
- **Risk:** medium. Strongest integrity story (every file hashed in the pinned manifest) but a lot of identity churn: the v3 identities are referenced in several tests and records, and the five canonical identities must be proven unchanged.
- **Changes:** everything in A, plus new inventory, manifest and archive, and the pinned IDs.

### C. Host the artifacts in Vercel Blob (or other storage) and download at start-up
- **Cost:** 2 to 3 days plus an operator step (store, credentials). Small recurring storage cost.
- **Risk:** highest. Needs secrets (OIDC token, store ID), adds a start-up network dependency and failure modes, and the earlier storage handoff (`deployment_gate_d22_storage_handoff.md`) was left at "operator action required". Not proportionate for 3 MB.

### D. Serve the JSON from the Next.js app (`web/public`) and bypass the API
- **Cost:** about 1 day. **Risk:** high. It duplicates the integrity validation in TypeScript, splits the source of truth, and breaks the rule that the frontend only reads what the API serves. Not recommended.

### E. Leave it unavailable, with an accurate message
- **Cost:** none. This PR does that: the Neurons pages and the Cockpit say "Neuron shape data is not available on this deployment." instead of "The data service isn't responding."

## Recommendation

Do **E now** (this PR) and **A next**, once the owner confirms that publishing the 3.1 MB of MaleCNS-derived
skeletons in the public repository is acceptable under the (still unwritten) data licence. Fold the files into a
v4 bundle (option B) the next time the runtime bundle is rebuilt for another reason, rather than as its own project.
Option A does not need a Vercel settings change. It does need a production redeploy, which should be done on a
preview first and checked with the `web-quality` suite.

Not verified: the live Vercel preview (behind Vercel Authentication) and Vercel's current function size limits.
