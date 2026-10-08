# D3R-SDK-DEPLOY — authorized single commit/push preflight

Date: 2026-10-08. This continuation authorizes exactly one additional focused
SDK-fix commit on d3r-preview and one push; no manual deployment/redeployment,
Production action, main change or fix-and-redeploy loop. Outcome pending the
fresh full Python gate and the authorized Git-triggered Preview.

Read-only Git audit confirms HEAD/local/remote d3r-preview at
0fac819d68d439fdac1dabd42bf3e7c321a4247f and local/remote main at
521769960d0730f45faec35aa669f91f5fd48d8b; exact origin a104174/NeuroFly.
Only the ten intended SDK-correction files are pending, nothing staged. Entire
implementation, tests, public-registry lock entries and retained history reviewed;
no blocking defect or implementation edit was required in this continuation.

Fresh authenticated provider reads: hcruz, hd-dev / HC, Hobby, exact neurofly
project prj_W1e15xknFkEC4NYH0OT4JENgBN4i; github link a104174/NeuroFly,
Production Branch main, project nodeVersion 24.x. Thus remote Node compatibility
is established from provider configuration, not merely the local Node version.
Official provider documentation supports Node 24 for builds/functions. Exact
running version/SDK installation remain cloud build observations to capture.
Protection all persisted, no observed bypass/exception, OIDC enabled/team issuer.
Only Preview BLOB_STORE_ID/BLOB_WEBHOOK_PUBLIC_KEY env records, zero Production
records. Existing store remains private/available/not quota exceeded and connected
only to Preview on this project. Only the two historical ERROR deployments exist.

Candidate uses exact @vercel/blob 2.8.0 with a complete npm lock, explicit backend
npm ci before provisioning, ESM package-relative SDK resolution and no frontend
node_modules dependency. Installed 2.8.0 signatures match get/private/OIDC/store/
stream/abort/cache options. Store/pathname and D2 verifier authority unchanged.
Preview-only guards, bounded streaming, owned partial cleanup, no overwrite,
finite diagnostics, no CLI login/static token/local fallback/runtime retrieval
were reconfirmed. Scientific source and D2 manifest/inventory diff remain empty.

Fresh local gates so far: 23 Node tests passed; isolated clean install and its
23 tests passed; focused deployment/D2 suite 61 passed (55.41s, two existing
warnings); Ruff check/format passed (354 files); frontend 76 passed (49.117s),
lint/typecheck/build passed. Full Python: 1,300 passed, 1 integration test deselected, two existing
deprecation warnings, 920.54s (15:20).
Only generated Next type-import lines restored to baseline after build.

Fresh supported read-only source dry-run passed: 464 entries, 7,372,701 bytes,
22 ignored. SDK helper/package/lock, Python integration/dependencies, frontend
and ten required science documents included; no env/auth, node_modules, raw/
derived data, archive/runtime tree or build output included. No deployment object
was created by dry-run. No provider settings or store connections were changed.

All mandatory local gates completed. Final security scans found no credential
values in candidate files or frontend static output. Existing D2 file-scoped
verification confirms all 74 manifest-listed checkout files; five fresh canonical
DTO fingerprints were captured for remote comparison. An initial strict release-
tree check was unsuitable for the checkout with expected extra data; the existing
verifier exact=False mode passed. No scientific identity differs. Final staged
review and provider/remote branch recheck precede the single authorized commit. Actual remote results will be a local-only report update
after the single push; no second commit/amend/push is authorized.
All historical outcomes and diagnostic uncertainty remain below unchanged.

---

# D3R-SDK-FIX — local build-only retrieval correction

Date: 2026-10-08. Final decision: **D3R_SDK_FIX_LOCAL_VERIFIED**. All mandatory
local gates passed. No commit, push, deployment or provider mutation. This is
local verification only; actual remote SDK access/scientific staging is unverified.
The historical D3/D3R outcomes, genuine failed Preview and diagnostic uncertainty
remain below unchanged.

## Baseline and scope

Read-only entry audit: d3r-preview at pushed commit
0fac819d68d439fdac1dabd42bf3e7c321a4247f, main/origin/main at
521769960d0730f45faec35aa669f91f5fd48d8b. Only the existing 347-line report update
was pending. Existing CLI defect is preserved: the pinned CLI account-login gate
runs before Blob's OIDC handler. Lost cloud stderr still prevents proving that
this was the only failure in the historical Preview.

## SDK and deterministic build dependency

Selected @vercel/blob 2.8.0, verified against installed TypeScript signatures,
package engines and current official SDK/private-storage documentation. Supports
get(pathname, {access:'private', oidcToken, storeId, useCache:false, abortSignal}),
200/304 discriminated responses, null missing object and Web ReadableStream.
Node >=20 is required; local verification uses Node 24.11.1 / npm 11.21.0.
No Vercel CLI login or credential file is needed for direct SDK calls.

A private build-only tools/vercel_blob/package.json declares exact 2.8.0;
package-lock.json resolves all transitive dependencies with integrity hashes.
There is no new root package-manager architecture or frontend SDK dependency.
Backend Services root remains '.', with build command:
`npm ci --prefix tools/vercel_blob --ignore-scripts --no-audit --no-fund &&
python tools/vercel_runtime_build.py`.
The helper's ESM import resolves its own adjacent node_modules independently of
cwd and frontend installation. Ignore rules exclude that generated dependency
folder from Git and source upload. No package install lifecycle scripts run.
The archive retrieval operation itself uses no dynamic npx package resolution.

## Retrieval, safety and integration

Python retains all existing release pins, manifest checks, D2 provisioning,
archive bytes/SHA, safe extraction, exact inventory/manifest and runtime layout.
Only retrieve() changes to deterministic `node <absolute-helper> <temporary-file>
<pinned-pathname> <pinned-store-id>`. Tokens are inherited environment values,
never arguments. Preview environment is now checked explicitly in Python and
Node, alongside required OIDC, exact store metadata and static-token prohibition.

The Node helper checks the trusted destination: absolute runtime.tar.gz inside a
real, non-symlink neurofly-build-* directory immediately below the system temp
root. Pathname must have the canonical release-path shape; Python supplies the
exact immutable pathname/store constants. No listing, put, delete, public URL,
local data, scientific generation, extraction or application route exists.

The SDK receives explicit private access, inherited OIDC and the exact supplied
store ID. It returns bytes through Web stream -> Node pipeline with backpressure.
No full-file arrayBuffer/buffer conversion. An exclusive mode-0600 .part file is
closed on completion/failure. Transport-byte count must equal SDK metadata size;
this is supplementary transfer-completeness evidence, not scientific validation
or a substitute for the pinned Python count/SHA. After complete transfer, an
atomic no-overwrite hard link publishes the destination and removes the owned
partial. Existing destination/partial files are never overwritten/deleted.
Owned partial/completed files are removed on failures; cleanup errors fail closed.
Transfer/request timeout is 120 seconds; Python outer subprocess timeout is 180.

Diagnostics use a finite category allowlist, typed SDK errors, known structured
network error codes and controlled operation stages. No SDK exception messages,
headers, URLs, bodies or environment values are printed. Success emits no output;
failure emits only `NEUROFLY_BLOB_FAILURE <category>` and exit 1.
Python accepts only that entire exact failure protocol with empty stdout/exit 1;
extra/unknown output becomes UNKNOWN_REDACTED_FAILURE without forwarding content.
Missing executable/timeouts/OS failures are sanitized and suppress exception
chaining. No successful child result substitutes for D2 archive verification.
No runtime request-time retrieval or factory/readiness/API change was introduced.

## Focused and clean-install evidence

- Node helper: 23 tests passed on the final implementation, including exact
  bytes/pins/options, Preview-only guards, missing auth/store, static rejection,
  null/not-found/access, network, unknown errors, dependency absence, non-200,
  timeout, interrupted/truncated/stalled streams, filesystem failure, invalid
  destination, no overwrite and sanitized child-process protocol.
- Child-process test runs the real helper from an isolated directory with a
  synthetic mocked SDK and no Vercel account credentials. No actual Blob request.
- Fresh temporary package/source directory, empty HOME/cache and no developer
  node_modules: npm ci succeeded, SDK 2.8.0 installed; all 23 tests passed there.
- Python deployment + D2 bundle tests: 61 passed, two existing warnings, 39.47s.
  Covers wrapper arguments, finite diagnostics, uncontrolled output, spawn errors,
  no extraction after retrieval failure, original byte/SHA/safe archive checks,
  provisioned readiness failure and isolated five canonical local playback routes.
- Node/Python finite protocol parity verified independently.
- Initial stream cleanup tests exposed a file-handle issue; corrected locally
  using FileHandle-owned auto-closing stream. Final tests above pass.

## Current complete gates and source packaging

Ruff check and format check pass (354 Python files).
Full Python suite: 1,300 passed, 1 deselected, two existing dependency warnings,
809.41s (13:29), on the final implementation. Includes 36 deployment tests and
existing complete scientific/D2 coverage.
Final frontend with the repository Python environment activated: 76 tests passed,
lint/typecheck/build passed. Initial unactivated frontend attempt failed because
its subprocesses could not find python; this is recorded, not counted as a pass.
Next regenerated tracked type imports; only those generated lines were restored
to baseline after the build. No frontend source change remains.

Pinned supported read-only dry-run passed without deployment creation:
464 entries, 7,372,701 bytes, 22 ignored. All four helper/package/lock/test files,
Python entrypoints/tools, Services config, dependencies, 151 Python source modules
and all ten manifest-listed scientific documents are included. No raw/derived
scientific data, runtime/archive, env/credential, node_modules, .vercel or build
output entered the source manifest. Final native cloud Function layout and actual
Preview SDK authentication remain future remote acceptance evidence.

## Files and remaining boundary

Intended local files: .gitignore, .vercelignore, vercel.json,
tools/vercel_runtime_build.py, tests/test_vercel_runtime.py,
tools/vercel_blob/package.json, tools/vercel_blob/package-lock.json,
tools/vercel_blob/retrieve.mjs, tools/vercel_blob/retrieve.test.mjs,
docs/deployment_gate_d3_staging.md. Nothing staged, committed or pushed.
Scientific source/data/docs/science and D2 identity authorities remain unchanged.
No credential value, signed private URL, root env file or runtime tree is added.
No real local private Blob request or provider configuration mutation occurred.
Existing protection/Preview-only store configuration is not changed by this task.

A future separately authorized Preview is required to verify actual SDK OIDC/store
access, remote D2 bytes/SHA/inventory/manifest, native packaging, readiness,
canonical payload identities and product smoke. Local acceptance does not erase
DEPLOYMENT_BUILD_FAILED or establish scientifically verified online staging.
No automatic commit/push/deploy is authorized or performed here. Final Git
review: six modified tracked files plus the four new helper/package files;
nothing staged. HEAD remains 0fac819d68d439fdac1dabd42bf3e7c321a4247f and
main/origin/main remain the starting SHA. Scientific diff is empty; no root
credential file, runtime tree/archive, SDK dependency tree or frontend build
output enters Git. Pending file sizes and credential-value scans were reviewed;
27 frontend static JS files contain no matching Blob/GitHub/JWT credential value.
The helper test includes only an explicit synthetic example.invalid error URL,
not an actual signed private Blob URL or credential.

Official SDK references:
https://vercel.com/docs/vercel-blob/using-blob-sdk
https://vercel.com/docs/vercel-blob/private-storage

---

# D3R-BLOB-DIAG — credential-safe retrieval investigation

Date: 2026-10-08. Diagnostic decision: **ROOT_CAUSE_IDENTIFIED** for a
reproduced build-authentication contract defect: pinned Vercel CLI 62.7.0 requires
CLI account authentication before its OIDC-capable Blob handler can execute.
This establishes a concrete incompatibility with the selected OIDC-only build
contract. The historical child's discarded output is unavailable, so it does
not establish that this was the sole error emitted in the failed cloud process;
an earlier npm/dependency failure cannot be excluded retrospectively.
No diagnostic instrumentation or retrieval replacement was implemented. No new
commit, push, deployment, object access/mutation or provider configuration change.
All previous reports and outcomes below are preserved.

## Starting Git state and existing evidence

Branch d3r-preview tracks origin/d3r-preview at
`0fac819d68d439fdac1dabd42bf3e7c321a4247f`.
Local main/origin/main remain `521769960d0730f45faec35aa669f91f5fd48d8b`.
Only the preceding 194-line post-deployment report update was dirty at entry;
no unrelated/scientific modifications were found. This investigation extends
that same report without discarding its contents.

Independent GETs confirm existing deployment
`dpl_98hZtMqD1tx2K9oWr5ZR8rfFzwzx`, exact existing project,
Preview target null, ERROR, BUILD_UTILS_SPAWN_1, backend build command exit 1.
Allowlisted log milestones confirm one Git clone, cloud builder CLI invocation,
Python 3.12, uv dependency installation, backend command, wrapper failure.
Metadata timestamps: createdAt 1791424744732, buildingAt 1791424746389,
ready 1791424806357. Backend command log at 1791424777415 and wrapper failure
at 1791424805094: about 27.7 seconds, not an observed 180-second timeout.
This interval alone is not an authentication diagnosis.

## Exact implementation and process contract

`build()` in tools/vercel_runtime_build.py validates committed manifest/archive
pins, creates a temporary archive pathname and calls `retrieve(archive)`.
Retrieval uses Python subprocess -> npx -> pinned Vercel CLI, not a Python SDK:
`npx --yes vercel@62.7.0 blob get <exact-pinned-pathname> --access private
--output <temporary-archive> --non-interactive`.
The pinned pathname is correct and unchanged. Tokens are not command arguments.

Required names: VERCEL_OIDC_TOKEN must be nonempty; BLOB_STORE_ID must equal the
pinned store; BLOB_READ_WRITE_TOKEN must be absent/nonempty-rejected.
No subprocess env/cwd override is supplied: parent environment and working
directory are inherited. Services backend root is '.', and cloud traceback
locates the helper at /vercel/path0/tools/vercel_runtime_build.py; the expected
checkout working directory is /vercel/path0, although logs do not print cwd.
The Python package/dependencies are installed from pyproject.toml before the
custom command. Node/npm are evidenced by successful frontend installation/build;
the child relies on npx/PATH and on package download availability. Logs do not
prove that the child CLI package successfully downloaded/started.

`capture_output=True`, `check=False`, timeout=180. A nonzero child result becomes
the fixed RuntimeError at helper line 42, discarding stdout/stderr. This exact
branch proves subprocess.run returned a nonzero result, not FileNotFoundError
or TimeoutExpired. Those exceptions would escape separately; no classifier exists.
D2 provision() is called only after retrieval returns successfully. Existing D2
byte/SHA, canonical archive/safe-path/member checks, inventory and manifest logic
is reused unchanged. No failed retrieval continues to provisioning/readiness.
The earlier D2.2 local round trip used an authenticated operator CLI environment,
which does not establish account-free CLI behavior in a clean cloud build.

## Pinned CLI and SDK compatibility proof

The installed package manifests independently identify Vercel CLI 62.7.0 with
exact dependency @vercel/blob 2.8.0; Blob SDK engines require Node >=20.
The cloud builder reports CLI 62.1.0, but the retrieval helper explicitly requests
62.7.0. The child version is not printed in historical logs. Current official
documentation confirms OIDC support; no precise minimum CLI/SDK version is
specified by the consulted documentation, so no minimum is guessed.

Installed pinned CLI dist/index.js declares SUBCOMMANDS_WITHOUT_TOKEN without
'blob'. Before command dispatch, absent account authConfig.token / --token causes
promptMissingCredentials(). In CI that function returns exit 1 for missing CLI
account credentials. This guard does not consult VERCEL_OIDC_TOKEN/BLOB_STORE_ID.
Only later, in commands-bulk.js, getBlobRWToken() resolves that OIDC pair and
get2() calls @vercel/blob.get(..., {oidcToken, storeId, access:'private'}).
The Blob handler itself therefore supports private OIDC, but its outer CLI gate
still requires a separate account session. A build OIDC token is not an account
login token and must not be supplied as --token or persisted as a CLI session.

Two isolated local reproductions used only synthetic inputs and empty temporary
HOME/XDG/global-config directories, CI=1, VERCEL=1, VERCEL_ENV=preview and telemetry
disabled. One exercised dist/index.js, the second the actual bin dist/vc.js.
Both returned exit 1 with the known login-required condition, produced no archive,
and created no auth.json/.env.local. Captured output was never printed/persisted;
only booleans and exit code were reported. No actual token or developer auth file
was read, copied or decoded. Synthetic strings are not real token-shaped values.
The CLI source shows this exit happens before Blob handler/API invocation.

Provider read-back confirms OIDC enabled/team issuer and only Preview store-ID /
webhook-key env records. No configured VERCEL_TOKEN or static Blob token exists.
No credential values or hidden child environment were inspected. Build-time OIDC
availability is documented; CLI account login is not part of the selected build
contract. Thus the account prerequisite is a proven implementation/tool-choice
mismatch. It is not evidence that Blob rejected OIDC, that store permissions are
wrong, or that the immutable object is absent.

Failure category for the reproduced mechanism: DEPENDENCY_OR_CLI_FAILURE,
reason CLI_ACCOUNT_AUTH_REQUIRED. The historical unobserved child output remains
UNKNOWN_REDACTED_FAILURE; do not label it OIDC_AUTHENTICATION_REJECTED or infer a
specific HTTP status. No child text parser/classifier was added.

## Smallest supported correction — proposed, not implemented

Replace only the authenticated-account CLI download layer with a small build-only
Node helper using pinned @vercel/blob 2.8.0 directly. The SDK supports private
get(pathname, {access:'private'}) using inherited short-lived OIDC/store envs;
it has no Vercel CLI command-dispatch/account-login gate. Declare the build
dependency explicitly rather than depend on the developer's cached package.
Stream the result to the existing temporary archive, then keep the complete D2
verifier/provisioner and all pins unchanged. Reject missing result/status/stream.

Typed SDK errors permit a small fixed diagnostic allowlist without printing
messages, headers, bodies, URLs or tokens; unknown failures stay sanitized.
Do not add VERCEL_TOKEN, a static Blob credential, CLI login, env pull, a local
science fallback or Production metadata. A valid Preview-scoped token accepted
by the existing store still needs verification in a future authorized build.
No network/object retrieval is needed to prove the current CLI prerequisite.

Official sources consulted:
- https://vercel.com/changelog/vercel-blob-now-supports-oidc-authentication
- https://vercel.com/docs/vercel-blob/using-blob-sdk
- https://vercel.com/docs/environment-variables/system-environment-variables
- https://vercel.com/docs/cli/blob (older static-token description is incomplete
  relative to the June 2026 announcement and installed pinned code).

## Tests, security, science and final boundary

Current focused tests: 10 passed, two existing warnings, 32.60s.
Ruff check passed; Ruff format check passed, 354 files. Offline pinned-CLI
reproductions passed their expected exit/account-auth/no-file assertions.
No implementation or persistent test code changed, so complete Python/frontend
suites were not rerun and no new deployment candidate is proposed as validated.
The preceding full gate results remain historical, not new diagnostic-run results.
No new classifier exists, so synthetic classifier scenario tests are not claimed.

Only docs/deployment_gate_d3_staging.md changed. Scientific source, D2 metadata,
archive SHA/size/inventory/manifest, canonical payloads and mappings remain
unchanged. All Deployments protection remains all. No credentials/raw child
output/signed URLs were written into docs or Git, and no root credential file
was created. No provider mutation, Blob download/reconnection/object mutation,
Production change, paid activation, commit or push occurred.

Another deployment is not necessary for this diagnosis. The next smallest step
is a separately scoped local implementation/test change for the direct SDK layer,
with focused synthetic error tests and full canonical gates before any future
candidate authorization. A future deployment is needed only to verify corrected
Preview OIDC/store access and complete scientific/online acceptance, not to
reproduce the existing account-login prerequisite. Stop here; do not start Phase 34.

---

# D3R-PROTECTED — GitHub App recovery final result

Date: 2026-10-08. Decision: **DEPLOYMENT_BUILD_FAILED**.
The first genuine protected Git Preview was created from the one authorized
staging commit/push. Its build failed closed at private archive retrieval.
No further commit, push, deployment, Production repair or promotion was attempted.
The complete earlier chronology remains below, including the pre-push snapshot
committed with this candidate. This final evidence update is intentionally left
uncommitted because authorization permitted only one commit and push.

## 1. Repository and Git authority

Starting main/HEAD/origin/main/remote main were exactly
`521769960d0730f45faec35aa669f91f5fd48d8b`; origin is
`https://github.com/a104174/NeuroFly.git`. Only eight intended files were pending.
No unrelated/scientific changes, credential files in Git, runtime/archive trees
in Git, unresolved Git operation or conflicting staging branch were found.
Final remote main and local main still have that same SHA.

## 2. Vercel authority and protection

Pinned local CLI 62.7.0 authenticated as hcruz; team hd-dev / HC,
`team_9xOi3efW7pKf7C6OU0JMwy9r`, remains Hobby. Existing project is
`neurofly`, `prj_W1e15xknFkEC4NYH0OT4JENgBN4i`.
Independent initial, post-connection and final provider reads consistently show
`ssoProtection.deploymentType="all"`, no project bypass configured, and no
observed public exception. No protection PATCH, upgrade or protection weakening
was performed. Authentication remained usable throughout this recovery.

## 3. GitHub App and connection

GitHub CLI identity a104174 has ADMIN access to a104174/NeuroFly; default main.
An installation-list diagnostic was inconclusive and was not treated as denial.
One supported connection POST via pinned CLI API succeeded:
`/v9/projects/prj_W1e15xknFkEC4NYH0OT4JENgBN4i/link`, github,
a104174/NeuroFly. Independent read-back confirms repoId 1364434373, exact
repository and Production Branch main. This establishes effective App access.
The project was reused; no replacement project or GitHub permission change.

## 4. Historical incidents and revised boundary

D2.2 remains verified; D3 remains SECURITY_BOUNDARY_FAILED; D3R and D3R-GIT
remain BLOCKED. The prior protected attempt stopped on App access. The operator
explicitly permitted protected automatic Production initialization only with
All Deployments authentication, no Production science credentials and no deliberate
Production deployment/promotion. This execution did not create an initialization
deployment: after connection the list still had only historical
`dpl_DShTisiRfUpNSyPBb92LnkHAnLsP`, Production/ERROR, no assigned alias.
No historical conclusion was rewritten.

## 5. Packaging, authorities and changes

The existing D2 isolated layout is reused: immutable release plus tracked src,
docs/science and data/reference metadata. Runtime imports from release/src before
scientific imports, so five source-relative authority paths resolve within the
release. A fresh isolated Python process exercises authority loaders, network
context documents, readiness and all five local playbacks without importing the
developer checkout. All ten manifest-listed scientific documents match bytes/SHA.
Final native cloud Function layout remains unverified because provisioning failed
before packaging could complete.

Only new implementation correction in this recovery: replace branch deny `*`
with documented minimatch `**`, covering nested branch names, and update the
focused configuration assertion. The explicit staging allow is retained. This
branch-local policy does not claim to protect remote main's absent configuration.
No scientific source/content or frontend source was edited.

## 6. Tests and complete current gates

- Final full `.venv/bin/python -m pytest`: 1,274 passed, 1 deselected,
  two existing dependency deprecation warnings, 836.79s. Includes all ten D3 tests.
- Focused deployment suite: 10 passed in 33.42s before the wildcard-only edit;
  updated config test separately passed; final full suite validates the final edit.
- `.venv/bin/python -m ruff check .`: passed.
- `.venv/bin/python -m ruff format --check .`: passed, 354 files.
- Final web `npm test`: 76 passed; `npm run lint`, `npm run typecheck`,
  `npm run build`: all passed. Generated Next type imports restored to baseline.
- `git diff --check` and staged diff check passed.
- Read-only source dry-run: 460 entries, 7,339,100 bytes, 21 ignored at the
  recorded pre-normalization snapshot; required source/authorities included,
  no raw/derived data, release/archive, credential, node_modules or build output.

The initial full Python run was intentionally stopped at 3% before the policy
correction; it is not counted as a pass. No historical pass substitutes for the
current full results.

## 7. Authorized Git operations

One branch: d3r-preview. One commit:
`0fac819d68d439fdac1dabd42bf3e7c321a4247f`.
Message: `chore(deploy): prepare protected NeuroFly D3R staging`.
One successful push: origin/d3r-preview. No main push, merge, force-push,
PR creation, tag or release. Exact eight committed paths:
`.gitignore`, `.vercelignore`, `app.py`, `vercel.json`,
`tools/vercel_runtime_build.py`, `tools/vercel_runtime_entrypoint.py`,
`tests/test_vercel_runtime.py`, `docs/deployment_gate_d3_staging.md`.
Committed diff: 8 files, 2,135 insertions. Explicit staging/checks and credential
scan passed. Only this post-deployment report update is pending after the commit.

## 8. Preview source and classification

Deployment: `dpl_98hZtMqD1tx2K9oWr5ZR8rfFzwzx`.
URL: https://neurofly-breqgi5g1-hd-dev.vercel.app
Source git, a104174/NeuroFly, ref d3r-preview,
SHA `0fac819d68d439fdac1dabd42bf3e7c321a4247f`, exact existing project.
Provider target is null: actual Preview, observed immediately while BUILDING.
Final readyState ERROR; aliasAssigned false. Alias API nevertheless lists branch
alias `neurofly-git-d3r-preview-hd-dev.vercel.app` against this Preview; that
record is reported separately from the deployment's aliasAssigned field.
No new Production deployment or Production alias/promotion was created.

## 9. Preview Blob/OIDC and frozen D2.2

Store store_S3zkyGCIjHi3p79M remains private, available, not quota-exceeded.
Connection spc_oOQLjCdMzHYshRF6 is only ['preview'], prefix BLOB, exact project.
Env records remain only Preview BLOB_STORE_ID and BLOB_WEBHOOK_PUBLIC_KEY;
zero Production env records and no static BLOB_READ_WRITE_TOKEN.
Build reached retrieval after checking nonempty build OIDC, exact store metadata
and absence of static Blob token. This proves those guards passed, not that the
token was accepted by Blob or the download completed.

Frozen archive remains 3,674,299 bytes, SHA
`12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`;
inventory `cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`;
manifest `e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`.
Canonical pathname remains pinned in the helper and committed authority.
No other object or local scientific fallback was used.

## 10. Remote build failure and logs

Cloud builder CLI was 62.1.0 (local/retrieval CLI pin remains 62.7.0), Python 3.12,
uv 0.10.11, iad1, 2 cores/8 GB. Git clone matched exact branch/commit; .vercelignore
removed 29 ignored files. Next.js 16.3.5 compiled and typechecked successfully.
The Python build then failed in retrieve(), tools/vercel_runtime_build.py:42:
`RuntimeError: pinned private release retrieval failed`.
Provider errorCode BUILD_UTILS_SPAWN_1; build command exited 1.
The helper intentionally captured and suppressed child stdout/stderr to avoid
leaking private URLs or credentials. Consequently the underlying CLI/Blob failure
is unresolved: logs cannot distinguish authentication, provider permission,
network/package retrieval, or object retrieval errors. No cause is invented.

No successful remote bytes/SHA check, D2 verifier, safe extraction, inventory/
manifest verification or runtime provisioning evidence exists. The build stopped
before those operations could complete. No build success or scientific readiness
is claimed. No corrective cloud operation/retry occurred.

## 11. Backend, scientific and product verification

Backend startup, /health, /ready and catalogue functional checks were not reached.
All five remote products remain unverified: BASELINE_CONTROL,
LOOMING_CIRCUIT_VALIDATION, LOOMING_WORLD_EXPERIMENT,
HORIZONTAL_MOTION_NEURAL_VALIDATION, EXPLORATORY_COURSE_CONTROL.
Local relocated tests pass, but no remote payload identity/hash comparison was
possible. Frontend cloud build passed; online frontend/same-origin catalogue,
playback, browser/WebGL and mobile functional smoke were not reached.
No runtime logs from an operational backend exist. No latency/performance claim.

## 12. Anonymous-access, security and cost

Without cookies/credentials, Preview root and /ready returned 302 to
vercel.com/sso-api; historical Production URL also returned that challenge.
Configured unassigned Production domain neurofly-liard.vercel.app returned 404;
this is not an end-to-end protection test of a functioning Production domain.
Authoritative all scope covers Production domain and existing/future URLs.
No app/scientific response was exposed by the checks.

No root .env.local or other root credential file was created. .vercel remains
ignored non-secret project.json/README only. Existing ignored web/.env.local
contains only the local development API-base key and was preserved/excluded.
Candidate/staged scans found no credential values, JWTs or signed private URLs;
frontend static output scan found no Blob credential/JWT value. No runtime/
archive/generated-data file entered Git. No env pull, link, automation bypass,
share link, exception, public domain change or protection disabling occurred.
No Production scientific config was added. Existing private store was not altered.
Hobby remained unchanged; no paid feature/plan/infrastructure enabled.

## 13. Final boundary and smallest next action

Final branch tracks origin/d3r-preview; local/remote main unchanged. One authorized
commit/push consumed. Final evidence remains a report-only uncommitted update;
no second commit/push is authorized. Frozen scientific files remain unchanged.
The task stops at DEPLOYMENT_BUILD_FAILED, not a scientific staging pass.
No cleanup is required: retained project/Git link/protected failed Preview and
historical failure are safe to leave under observed protection/no science config.

Smallest next step: authorize a separate, narrowly scoped follow-up to obtain
credential-safe failure classification for the captured private retrieval command
(e.g. only allowlisted error codes, never full child stderr/URLs/tokens), then
review the evidence and propose the minimal fix. Any new commit/push/deployment
needs fresh explicit authorization; none is performed here. Do not change release
identities, enable static credentials, repair Production or weaken authentication.

---

# D3R-PROTECTED — resumed after GitHub App repository authorization

Date: 2026-10-08. The operator reports authorizing the Vercel GitHub App for
`a104174/NeuroFly`. This execution resumes the existing candidate and retains
every previous report below; App access is not inferred from that report alone.

Initial read-only checks reconfirmed main/HEAD/origin/main/remote main at
`521769960d0730f45faec35aa669f91f5fd48d8b`, exact origin, eight intended pending
files, no staging branch/commit/push, no science diff, no root env file or release
tree. GitHub CLI reports active `a104174`, ADMIN on the exact repository and
default branch main. Vercel independently reports `hcruz`, hd-dev / HC, Hobby,
project `prj_W1e15xknFkEC4NYH0OT4JENgBN4i`, persisted protection `all`, no
project bypass/exception config, link null, zero Production env records, and
existing private/available Preview-only Blob connection. Deployment list still
contains only the historical D3 Production/ERROR record.

Existing build/runtime helpers and relocated authority-path proof were reviewed
without architectural changes. All frozen manifest/inventory/archive cross-checks
and ten science-document byte/SHA checks match. No scientific release is rebuilt
for deployment; existing test-only D2 fixtures remain test inputs.

One minimal policy correction was demonstrated using the documented minimatch
syntax: `*` does not match `feature/example`, while `**` matches nested branch
names and the staging branch. `vercel.json` now denies `**` and explicitly allows
`d3r-preview`; the existing focused config assertion was updated. This preserves
the documented any-true-match precedence and does not purport to alter remote
main's absent configuration. No source/scientific contract changed.

The first current full Python run was intentionally interrupted at 3% before
this configuration edit, with no failure reported; a fresh full run on the final
candidate is required. Focused deployment tests passed 10/10 in 33.42s before
the wildcard edit; the updated route/policy test then passed separately. Full
final Python suite passed: 1,274 passed, 1 deselected, 2 existing dependency
deprecation warnings, 836.79s. The full run includes all ten deployment tests. Ruff check/format pass (354 files). Final frontend
run passed 76 tests, lint, typecheck and build. Generated Next type imports were
restored to baseline; existing local development configuration is preserved.

Read-only dry-run passed: 460 entries, 7,339,100 bytes, 21 ignored at that snapshot;
all required backend/config/tools/source/frontend files and science authorities
were present, and no local derived/raw/runtime/archive/credential/build files
were included. Final source review follows normalization of Next's generated
type imports. No blind Git connection retry has been made in this execution.

A GitHub installation-list diagnostic produced a transport error, not an App
permission verdict. The documented endpoint is scoped to a GitHub App user token;
GitHub CLI OAuth access does not establish Vercel App access. No token was read,
requested or substituted. The supported Vercel connection/read-back is the
decisive integration verification, subject to the confirmed protection boundary.

Current Git connection: the single supported POST `/v9/projects/
prj_W1e15xknFkEC4NYH0OT4JENgBN4i/link` succeeded using the pinned CLI API
with github / a104174/NeuroFly. Provider returned repository ID 1364434373
and Production Branch main. This establishes effective Vercel GitHub App access
after operator authorization. Independent read-back and initialization audit
precede the authorized staging branch/commit/push; those remain unused here.

Independent post-connection read-back confirms exact github link and main,
protection all, no bypass and zero Production env records. No initialization
deployment was created: list still contains only the historical D3 ERROR record.
The private store remains available. No root credential file was generated.
All mandatory local gates pass; one staging commit/push is now prepared.

---

# D3R-PROTECTED — resumed after dashboard and GitHub authentication recovery

Date: 2026-10-08. Final decision:
`GIT_INTEGRATION_OPERATOR_ACTION_REQUIRED`. Local gates passed; the protected
Git connection was refused by Vercel's repository-access check.
All previous reports below remain historical and unchanged.

### Current authority and protection audit

Read-only Git audit confirms `main`, HEAD/origin/main/remote main all
`521769960d0730f45faec35aa669f91f5fd48d8b`, exact origin
`https://github.com/a104174/NeuroFly.git`, eight intended pending D3 files,
no conflicting `d3r-preview` branch and no unresolved Git operation.

Pinned Vercel CLI 62.7.0 `whoami` returned `hcruz`. Independent project/team APIs
confirm `hd-dev / HC`, Hobby, team `team_9xOi3efW7pKf7C6OU0JMwy9r`, existing
project `prj_W1e15xknFkEC4NYH0OT4JENgBN4i`. Root-linked `project inspect` also
confirms the exact project/owner/root. Dashboard recovery is independently
verified: `ssoProtection.deploymentType="all"`. No protection PATCH was issued.
Initial project response has no bypass, exception-config, OPTIONS allowlist,
trusted IP/source override; historical deployment has no bypass and aliases
remain empty. Existing/future Preview and Production URLs are covered by the
documented All Deployments scope. Team settings were not changed.

Anonymous GET to `neurofly-95mm68hhm-hd-dev.vercel.app/` returned 302 with a
redirect to `vercel.com/sso-api`. Configured but unassigned Production domain
`neurofly-liard.vercel.app/` returned 404. That 404 is not a functioning-domain
authentication test; Production-domain coverage is established by persisted
`all` and official configuration semantics until a new operational URL exists.

GitHub CLI confirms active user `a104174`; exact repository access read-back
reports `viewerPermission=ADMIN`, default branch `main`. The configured HTTPS
Git helper uses `gh auth git-credential`. Public branch API independently
confirms main's baseline SHA and `protected=false`; no branch protection or
repository visibility/default changed. GitHub API connection errors in the
sandbox were retried read-only with permission; no alternate credentials or
push dry-run were used in this resumed execution.

Initial provider audit still lists only `dpl_DShTisiRfUpNSyPBb92LnkHAnLsP`,
Production/ERROR, no alias; `link=null`, `live=false`. Existing private store
`store_S3zkyGCIjHi3p79M` is available/not quota-exceeded, connected only to
Preview on this project. Env records are only Preview `BLOB_STORE_ID` and
`BLOB_WEBHOOK_PUBLIC_KEY`; zero Production env records, no static Blob token.
Environment/authentication values were not printed or persisted.

### Package-layout correction and scientific path proof

The source-relative scientific contract is preserved, not replaced: scientific
modules still compute `Path(__file__).resolve().parents[2]/docs/science` directly
or through imported `SCIENCE_ROOT`. D2's existing isolated validation already
delivers tracked application `src/`, science documents and `data/reference`
beside the extracted release. The native deployment now uses that same layout.

`tools/vercel_runtime_build.py` still downloads only the immutable pinned Blob,
reuses D2 byte/SHA/archive safety/provision/manifest/inventory verification, and
stages the same verified science documents. It additionally copies application
source and Git-delivered reference metadata into the release, excluding caches.
The D2-sealed `data/` parent is writable only during build assembly of reference
metadata and restored to mode 0555 in `finally`; copied files/directories are
0444/0555. No scientific artifact is regenerated, copied from checkout-derived
data or changed. The exact 74-file data inventory remains unchanged.

`tools/vercel_runtime_entrypoint.py` now selects release `src/` before importing
scientific modules/factory. Missing provisioned source fails closed. The build
helper's scientific import is deferred to its build function so importing pins
cannot preload checkout/vendor scientific modules during runtime bootstrap.
Existing FastAPI factory and local development entrypoints are unchanged.

Installed `@vercel/python` builder reads function `includeFiles` into initial
bundle files; existing `.neurofly-release/**` explicitly carries this complete
layout. Provider-generated final bundle is still subject to remote verification.
This does not claim that upload inclusion alone proves runtime layout.

The updated focused test launches a fresh `python -I -B` subprocess from a
relocated package directory, with no checkout path injected and no scientific
module preloaded. It loads all five path-dependent authorities, verifies the
science root is inside the release, checks network-context document presence,
then verifies `/ready` and all five canonical playback routes. This passed.
The existing missing/corrupt release and no-fallback checks remain in place.

### Git policy and source inclusion

`vercel.json` now uses documented branch rules `"*": false` and
`"d3r-preview": true`; the focused configuration check covers the exact policy.
This permits the intended branch under documented any-true-match precedence.
It does not assert protection of existing remote main, which has no config.
No main contents are changed. Automatic protected initialization is permissible
under the revised boundary; future unrelated main pushes are outside this gate.

Read-only CLI dry-run passed: 460 entries, 7,338,645 bytes, 21 ignored (snapshot
before final minor helper/test edits; final dry-run is repeated before mutation).
Final dry-run passed after all code edits: 457 entries, 7,339,106 bytes, 21
ignored, no required file missing and no unexpected runtime/data/credential/build
inclusion. The three removed entries are only the empty local `.agents`, `.aws`
and `.codex` directories; no required source was removed.
Backend entrypoint/config/tools/source/frontend and all ten pinned science docs
are included. No derived/raw data, archive, extracted release, node_modules,
build output or credential file is included. Three local tooling directories
appear only as empty entries. Existing tracked Blender source is 1,139,464 bytes;
it is not required by the web runtime, but retained to avoid unrelated asset
cleanup. Scientific authorities' local bytes/hashes match the committed manifest.

### Current quality gates and scope

Focused deployment tests: 10 passed, two existing deprecation warnings, 32.97s.
The first development iteration detected a build-only reference-parent permission
issue; corrected before candidate gates. A test-string line-length issue was
also corrected. Full Ruff check/format subsequently passed (354 files).

Frontend: 76 passed; lint, typecheck and build passed. Test PATH includes `.venv`
Python. Existing ignored `web/.env.local` contains only the development API-base
key, no OIDC/Blob key; it is excluded and preserved. Next build rewrote generated
type-reference imports; only those generated changes were restored to baseline.
No frontend source or scientific contract changed.

Full current Python suite: 1,274 passed, one integration test deselected by the
canonical repository configuration, two existing deprecation warnings; 849.93s
(14m09s). Full Ruff check/format and `git diff --check` passed after this run.

Local reference playback fingerprints were computed without changing or
regenerating scientific artifacts. Serialization is JSON with sorted keys,
compact separators and non-finite values forbidden; remote comparison remains
pending. These hashes supplement the payload's authoritative identity fields.

| Canonical product | Local complete payload SHA-256 |
|---|---|
| BASELINE_CONTROL | `75d1f2856f0d896589a8b1f62fb61016d701045b760e216b7cb5fa70daa30668` |
| LOOMING_CIRCUIT_VALIDATION | `c3387396dcffa6372287df1a7d4680bb7ba605df319af4cf10f140cfc3a4d223` |
| LOOMING_WORLD_EXPERIMENT | `d06ef32aaf054b981464948916e5687951b40f571be5286513dad8ae440f26df` |
| HORIZONTAL_MOTION_NEURAL_VALIDATION | `52554962f3e9c85c6866b5e3ec56f8a12d24340db2236ec52c7809c6ece8d404` |
| EXPLORATORY_COURSE_CONTROL | `7fddc1109495023d8f64744237796d5d8e86852abef80b6979f1994088d46806` |

Pending reviewed scope remains exactly `.gitignore`, `.vercelignore`, `app.py`,
`vercel.json`, `tools/vercel_runtime_build.py`,
`tools/vercel_runtime_entrypoint.py`, `tests/test_vercel_runtime.py`, and this
report. No scientific source/authority diff; no credential-value/JWT/signed URL
matches found in reviewed pending files; no root environment file or generated
release tree. No branch/commit/actual push/Git connection yet in this execution.

### Cloud recovery outcome

After all local gates, the final provider preflight independently reconfirmed
the exact project/team, persisted `all`, no bypass, Preview-only store env
records, zero Production env records and the sole historical ERROR deployment.
The one supported Git connection attempt was:

```text
NPM_CONFIG_CACHE=/tmp/neurofly-npm-cache npx --yes vercel@62.7.0 git connect
  https://github.com/a104174/NeuroFly.git --scope hd-dev --yes --non-interactive
```

It ran outside the filesystem sandbox so existing CLI login metadata could
refresh normally; no credential was supplied as an argument. CLI exit 1:

```text
Retrieving project…
> Connecting GitHub repository: https://github.com/a104174/NeuroFly
Error: Failed to connect a104174/NeuroFly to project. Make sure there aren't any typos and that you have access to the repository if it's private.
```

The exact repository URL, authenticated GitHub ADMIN permission and correct
Vercel project authority were already independently established. GitHub CLI
access is distinct from the Vercel account's Git login connection and the
Vercel GitHub App's repository installation/access. Installed CLI's handler
maps both `Install GitHub App` and `repo_not_found` provider errors to this
same generic text; the observed output cannot distinguish those cases.
No exact missing installation/account permission is asserted without evidence.
No second POST/retry, credential workaround or unrelated integration was made.

Independent post-attempt GETs confirm `link=null`, protection still `all`,
`live=false`, no bypass, zero aliases, Preview-only two env records and no new
deployment. The sole retained deployment is still the historical D3 ERROR.
No root credential/environment file was generated. Final `whoami` is `hcruz`:
Vercel authentication remained available throughout this resumed attempt.
The stop is a provider Git integration prerequisite, not an authentication loss
or the superseded zero-Production-object restriction.
Final credential-value scan of 27 generated frontend static JavaScript files
found no static Blob-token or JWT-value matches. These ignored build files were
not staged/uploaded as local output; online exposure checks remain pending.

### Complete resumed final report

| Required finding | Result |
|---|---|
| 1. Git/repository baseline | Authoritative main/origin/main/remote main remain `521769960d0730f45faec35aa669f91f5fd48d8b`; exact origin verified; eight intended pending paths only. |
| 2. Vercel auth/project | CLI 62.7.0, hcruz, hd-dev / HC, Hobby, exact existing project; initial/final auth and provider reads succeeded. |
| 3. All Deployments protection | Independently persisted `ssoProtection.deploymentType="all"` before and after connection attempt; no PATCH issued. |
| 4. GitHub auth/permissions | Active a104174, exact repo ADMIN, helper configured, main baseline/unprotected verified. Git author email matches baseline GitHub-author a104174. No permission/default/visibility changes. |
| 5. History | All previous outcomes preserved; revised protected initialization boundary explicitly honored. |
| 6. Package/science paths | Release source/reference layout matches existing D2 isolated contract; fresh relocated process proves authority roots/readiness/five routes. Cloud native Function layout remains a remote acceptance item. |
| 7. Implementation changes | Build helper stages tracked source/reference without caches and restores read-only data parent; runtime imports release source first; Git rules allow only staging where that config is read; focused tests/report updated. Other existing D3 files preserved. |
| 8. Tests | Updated existing focused fixture/readiness test with relocated fresh-process authority and five-product checks; Git configuration policy asserted. Existing auth/integrity/no-fallback tests retained. |
| 9. Full gates | Python 1,274 passed, one integration deselected, two existing warnings, 849.93s; focused 10 passed in 32.97s; Ruff check/format 354 files passed; frontend 76 passed, lint/typecheck/build passed; diff-check passed. |
| 10. Git Integration | One connection attempt refused by repository-access check; independent `link=null`. Exact GitHub App vs login/repo access cause unresolved by generic CLI error. |
| 11. Automatic Production initialization | None created; post-attempt deployment list unchanged. |
| 12. Branch/commit/push | None created, staged or actually pushed; conditional one-commit/one-push authorization remains unused. |
| 13. Main unchanged | Local/remote baseline unchanged; no history rewrite, merge, main push or branch/default setting change. |
| 14. Preview ID/URL/branch/SHA | None. Historical ERROR URL is not Preview evidence. |
| 15. Preview classification | Not reached; no new deployment. |
| 16. Blob/OIDC/D2.2 | Existing private available Preview-only store/config preserved; pinned committed metadata cross-checks passed; no new remote archive retrieval or byte/SHA/extraction/runtime verification. |
| 17. Health/readiness/scenarios | Local relocated ready and all five routes pass; no remote backend, readiness or scenario verification. |
| 18. Payload identities | Local frozen reference identity fields/full payload hashes prepared above; remote comparison not reached. No remote equality claimed. |
| 19. Frontend/WebGL/mobile | Full local frontend gates pass; online/browser/WebGL/mobile smoke not reached. |
| 20. Anonymous security | Historical URL redirects 302 to Vercel SSO; unassigned Production domain 404 is inconclusive as a live-domain auth test. Persisted all coverage independently confirmed; no new URL for final anonymous check. |
| 21. Logs | No new build/runtime logs. Safe Git-connection failure recorded. No provisioning success inferred from local tests. |
| 22. Cost/science regression | Hobby maintained, no upgrade/paid activation/new infrastructure; full current suite passes and no scientific source/authority/data diff. No release regeneration outside existing test fixtures. |
| 23. Final Git | Expected eight pending files; nothing staged; main baseline unchanged; final status/diff-check/log/branch/size/security review performed. |
| 24. Decision | `GIT_INTEGRATION_OPERATOR_ACTION_REQUIRED`. |
| 25. Limitations | Vercel Git App/login access unresolved; no Git connection/staging commit/push/deployment; cloud packaging/provisioning/remote identity/product acceptance pending. |
| 26. Operator action | In Vercel account hcruz, verify GitHub login connection is a104174 and the Vercel GitHub App is authorized for the exact a104174/NeuroFly repository. Review project hd-dev/neurofly Git settings and GitHub installed applications; authorize only this repository if access is missing. Do not create a replacement project, broaden repository permissions or deliberately deploy main. Then resume this gate for connection/read-back and the one staging commit/push. |
| 27. Smallest next step | Resolve Vercel's repository access, preserving All Deployments protection and Preview-only Blob; then resume the existing candidate. No speculative retries or alternative credentials. |

Operator locations: [existing project Git settings](https://vercel.com/hd-dev/neurofly/settings/git),
[Vercel account authentication](https://vercel.com/account/settings/authentication),
[GitHub installed applications](https://github.com/settings/installations).
The operator should verify the actual missing authorization rather than assume
GitHub CLI login alone supplies Vercel's App installation/access.

No cleanup is required. No direct deployment, Production promotion, new project,
new store, billing upgrade, scientific refactor or Phase 34 work occurred.

---

# Deployment Gate D3R-PROTECTED — protection attempt and authentication stop

Current decision: `BLOCKED`. Date: 2026-10-08.

The operator explicitly revised the deployment security boundary: an automatic
Production initialization from Git connection is acceptable only after project-
wide authentication covers all URLs, with no Production scientific credentials
or runtime provisioning and no deliberate Production deployment/promotion.
The earlier zero-Production-object prohibition no longer blocks this gate.
Historical D3, D3R and D3R-GIT records below remain unchanged.

This attempt stopped because Vercel authentication became unavailable while
attempting the authorized project authentication change. No Git connection,
branch, commit, actual push, deployment or promotion was made. The requested
protection setting could not be read back, so its persisted state is unknown;
it must not be assumed active for any subsequent deployment-triggering action.

### Protection evidence and attempted change

The current official [September 9 announcement](https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan)
states that Vercel Authentication can protect all deployments, including
Production domains, at no additional cost on every plan. The current
[authentication documentation](https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/vercel-authentication)
maps API `ssoProtection.deploymentType="all"` to All Deployments and explains
coverage of existing and future deployments. The current public OpenAPI PATCH
request schema includes this exact enum. No paid feature or trial was requested.

Fresh initial provider reads confirmed Hobby and existing protection
`all_except_custom_domains`. Project-level bypass, password protection, trusted
IP/source overrides, OPTIONS allowlist and protection-config records were absent
in the inspected response; the historical deployment had no bypass record and
the project alias list was empty. No new bypass, exception or shareable link was
created. Final exception/anonymous access evidence was not reached.

The only attempted cloud configuration mutation was:

```text
npx --yes vercel@62.7.0 api /v9/projects/prj_W1e15xknFkEC4NYH0OT4JENgBN4i
  --method PATCH --input - --scope hd-dev --raw --non-interactive
```

Its stdin was only non-secret JSON:

```json
{"ssoProtection":{"deploymentType":"all"}}
```

The command was run with the existing `/tmp/neurofly-npm-cache`; response output
was captured in memory for whitelisted ID/protection fields. It returned exit 1:

```text
Error: Not able to create ~/.local/share/com.vercel.cli/auth.json (unknown error).
```

Because this was consistent with the filesystem sandbox preventing a CLI login
metadata refresh, an independent GET read-back was retried with elevated
execution permission. No second PATCH was attempted. The GET also returned
exit 1:

```text
Error: The request is missing an authentication token (403)
```

Authentication worked for the initial `whoami` and all nine audit requests, but
did not remain available for the entire attempt. The observed sequence does not
establish the exact CLI refresh/provider cause or whether the PATCH reached the
provider. No auth-file credential contents were inspected, no token was printed
or requested, and no login/env-pull/link command was run. No further cloud action
was attempted after this failure. Effective All Deployments protection remains
unconfirmed, which is a mandatory prerequisite to Git connection.

### GitHub authority evidence

Origin remains `https://github.com/a104174/NeuroFly.git`. Remote symbolic HEAD is
`main`, matching the baseline; `d3r-preview` is absent locally and remotely.
No GitHub authentication environment variable or Git credential helper was
available. `gh` remains unavailable. A read-only permission probe used
`git -c core.askPass= push --dry-run --no-verify origin HEAD:refs/heads/d3r-preview`,
with terminal/askpass prompting disabled. It returned exit 128:

```text
fatal: could not read Username for 'https://github.com': terminal prompts disabled
```

This was a dry-run, not an actual branch push. It created no Git ref and no
deployment. Authenticated GitHub identity, write access, branch-protection access
and Vercel App eligibility remain unverified. No credentials were guessed or
requested. Missing Git authentication is an additional prerequisite; the primary
stop is lost Vercel authentication and unconfirmed project-wide protection.

### Complete current-gate report

| Required finding | D3R-PROTECTED evidence/result |
|---|---|
| 1. Repository and Git audit | All requested initial commands passed: `main`, HEAD/origin/main `521769960d0730f45faec35aa669f91f5fd48d8b`; exact eight intended pending files, no unexpected change or unresolved Git marker. |
| 2. Original incident history | Complete prior records preserved below; none reclassified as passed. |
| 3. Revised security boundary | Protected automatic Production initialization is authorized; deliberate Production deployment/provisioning/promotion remains prohibited. |
| 4. Vercel identity/team/project | Initial CLI 62.7.0 `hcruz`; `hd-dev / HC`, team `team_9xOi3efW7pKf7C6OU0JMwy9r`; existing project `prj_W1e15xknFkEC4NYH0OT4JENgBN4i`. Authentication subsequently failed as documented above. |
| 5. Hobby protection capability | Current official documentation/schema supports free All Deployments authentication; actual persisted activation could not be confirmed because authentication failed. No payment requirement was observed. |
| 6. All Deployments configuration | Initially `all_except_custom_domains`; one PATCH of `all` attempted, failed locally; no successful response or read-back. Final provider setting unknown. |
| 7. Effective protection verification | Incomplete. Do not treat the requested configuration as persisted. |
| 8. Production domain protection | Configured default domain `neurofly-liard.vercel.app`; authoritative `all` read-back and fresh anonymous tests not completed. |
| 9. Historical Production deployment | Fresh initial API confirms sole deployment `dpl_DShTisiRfUpNSyPBb92LnkHAnLsP`, CLI source, Production target, ERROR, aliasAssigned false; live false, no project aliases. |
| 10. GitHub origin/access | Exact origin and remote main verified; dry-run reports missing Git authentication; authenticated user/write permissions and App eligibility incomplete. |
| 11. Git Integration | Not attempted; initial provider `link=null`. |
| 12. Automatic initialization deployment | None created by this attempt. |
| 13. Initialization protection | Not applicable; no initialization attempted. |
| 14. Production environment/Blob audit | Initial API has zero Production env records, only Preview `BLOB_STORE_ID`/`BLOB_WEBHOOK_PUBLIC_KEY`; existing private store connected only to Preview. No environment/storage change attempted. |
| 15. Package-layout findings | Existing candidate preserved; relocated/native package tests not performed in this stopped attempt. Prior source upload evidence does not prove final native layout. |
| 16. Scientific authority paths | Prior five-module module-relative path concern remains; no path or authority content changed. Existing entrypoint still selects provisioned release and existing factory. |
| 17. Files changed | This attempt changes only this report; seven prior D3 implementation/config/test files remain intact. |
| 18. Tests added/updated | None; no implementation/config changes. |
| 19. Full Python gates | Not run after the authentication stop; historical results below are not current gates. |
| 20. Full frontend gates | Not run after the authentication stop; historical results below are not current gates. |
| 21. Branch/commit | None created. Remain on main, baseline HEAD unchanged. |
| 22. Explicit committed files | None staged or committed. |
| 23. Push result | No actual push; read-only dry-run failed for missing authentication. Authorized push remains unused. |
| 24. Main unchanged | Local main/origin main/remote-advertised main match baseline; no merge/default-branch/history change. |
| 25. Preview ID/URL | None. Historical ERROR deployment URL is not a valid Preview. |
| 26. Preview classification | No new deployment to classify. |
| 27. Preview Blob/OIDC | Initial API confirms store `store_S3zkyGCIjHi3p79M`, private/available, Preview-only connection, OIDC project enabled/team issuer; no quota exceedance. No credential values printed. |
| 28. Remote archive bytes/SHA | No remote retrieval in this attempt; frozen D2.2 pins preserved. |
| 29. Inventory/manifest | Preserved committed authority; no fresh remote verification. |
| 30. Runtime provisioning | Not reached; no scientific release generated or substituted. |
| 31. Backend startup | Not reached. |
| 32. /health | Not remotely tested. |
| 33. /ready | Not remotely tested; semantics unchanged. |
| 34. Five scenarios | BASELINE_CONTROL, LOOMING_CIRCUIT_VALIDATION, LOOMING_WORLD_EXPERIMENT, HORIZONTAL_MOTION_NEURAL_VALIDATION, EXPLORATORY_COURSE_CONTROL: remote checks not reached. |
| 35. Payload comparison | Not reached; no matching remote identity claimed. |
| 36. Frontend/routing | Existing candidate preserved, no online verification. |
| 37. Browser/WebGL/mobile | Not reached; no usable Preview. |
| 38. Anonymous access | Not performed after failed protection activation/read-back; no end-to-end protection pass claimed. |
| 39. Deployment logs | No new deployment/build/runtime logs. Only safe CLI auth errors documented. |
| 40. Security | No local `.env*`, persisted workspace OIDC file, generated release tree, staged credentials or new bypass/exception. Final pending-file value-pattern and generated-scope scan completed. Protection remains unconfirmed, so connection is prohibited. |
| 41. Cost | Initial live API confirms Hobby; no upgrade/trial/paid infrastructure requested or enabled. |
| 42. Scientific regression | No science/source/canonical artifact modifications; no full current regression run claimed. |
| 43. Final Git | Expected eight pending files, nothing staged, main unchanged; final requested status/diff-check/log/branch review performed. No committed diff against baseline exists. |
| 44. Current decision | `BLOCKED`. |
| 45. Limitations | Vercel auth lost; `all` not independently confirmed; GitHub auth/write/App authority unavailable; packaging/gates and all staging acceptance checks remain pending. |
| 46. Exact operator action | Restore pinned Vercel CLI authentication locally without sharing tokens; authenticate Git access for `a104174/NeuroFly` using the operator's normal secure provider workflow. Then independently read back `ssoProtection` before any connection. If still not `all`, repeat only the documented project-scoped protection change and verify it. App installation necessity has not been established; do not install/connect speculatively. |
| 47. Smallest next step | Restore Vercel login and inspect effective protection. Preserve the current files/project/store; do not revisit the superseded zero-Production-object requirement. Resume Git authority, packaging, full gates and protected Git integration only after prerequisites pass. |

No cleanup/reset is required. No Phase 34, scientific refactor, deliberate
Production deployment, public release, merge, actual push or staging commit.

---

# Deployment Gate D3R-GIT — Git connection safety preflight

D3R-GIT decision: `BLOCKED`. Date: 2026-10-08.

This attempt performed read-only Git/provider/source/documentation inspection
and updated this report. It created no branch, commit, push, Git connection,
deployment, environment configuration, alias or storage connection. Conditional
authorization for one staging commit/push remains unused. Historical D3 and D3R
records below are preserved verbatim.

### Repository and Git findings

Initial `git status --short --branch`, HEAD/origin/main, remotes, branches,
last-five log, diff-stat and diff-check were inspected. `main`, HEAD and
origin/main remain `521769960d0730f45faec35aa669f91f5fd48d8b`.
Exactly eight intended D3 files are dirty; no unrelated change or unresolved
Git operation was observed. No generated release tree or root environment file
exists. Nothing was reset, cleaned, stashed, staged or discarded.

### Verified origin repository

Fetch/push origin: `https://github.com/a104174/NeuroFly.git`.
`git ls-remote --symref origin HEAD refs/heads/main refs/heads/d3r-preview`
confirmed remote HEAD points to `main`, the authoritative commit matches, and
`d3r-preview` does not exist remotely. No local staging branch exists either.
GitHub's public repository API confirms `a104174/NeuroFly`, public, not archived,
default branch `main`, owner type `User`. Public read access does not establish
authenticated write authority. `gh` is unavailable and no GitHub connector was
available; GitHub identity, write permissions and Vercel App installation access
remain unverified. No permission probe that writes to Git was attempted.

### Existing D3/D3R implementation

All eight candidate files were inspected. Native FastAPI entrypoint uses the
existing factory; the build wrapper requires OIDC, exact store ID and no static
Blob token, downloads only the pinned pathname, and reuses D2 manifest/archive/
provision/release verification. Runtime wiring selects the provisioned release
and removes optional checkout overrides. Services route `/health`, `/ready`
and `/api/v1/*` to the backend before the frontend catch-all; the frontend uses
the backend binding. No scientific source or authority was modified.
This is a source audit, not proof of final native packaging or remote behavior.

### Vercel identity/team/project

Pinned CLI `62.7.0`, `whoami=hcruz`; team API confirms `hd-dev / HC`,
`team_9xOi3efW7pKf7C6OU0JMwy9r`, Hobby. Project API confirms existing
`neurofly`, `prj_W1e15xknFkEC4NYH0OT4JENgBN4i`, owned by that team.
Local `.vercel/project.json` matches and contains only non-secret link metadata.
The project has `link=null`, `hasDeployments=true`, `live=false`,
`gitProviderOptions.createDeployments="enabled"`, no explicit deployment policy,
OIDC enabled with team issuer, and Vercel Authentication protection
`all_except_custom_domains`. No setting was changed.
Authentication remained available throughout this attempt; final pinned-CLI
`whoami` again returned `hcruz`, and every provider audit request succeeded.

### Historical Production incident

Fresh deployment API/listing confirms the sole retained deployment
`dpl_DShTisiRfUpNSyPBb92LnkHAnLsP`, `source=cli`, `target=production`,
`readyState=ERROR`, `aliasAssigned=false`. Project alias list is empty.
Configured default domain remains `neurofly-liard.vercel.app`; configuration
does not imply an assigned deployment alias. There is no functional Preview.
The historical fail-closed store mismatch and transient OIDC-file incident are
retained in the D3 record below. Nothing was deleted or retried.

### Git Integration safety findings

The required guarantee is prevention of **deployment creation**, including any
initial connection-triggered Production deployment. It is not satisfied by an
ignored build, failure/cancellation, disabled domain assignment or access
protection. These controls act at different stages and were not substituted.

Current official [Git configuration documentation](https://vercel.com/docs/project-configuration/git-configuration)
defines branch rules in repository configuration: unspecified branches default
to enabled; if multiple rules match, any true rule enables deployment. A
`"*": false, "d3r-preview": true` candidate would restrict branches only where
that configuration is actually read. Remote `origin/main` has no `vercel.json`.
An uncommitted or staging-only rule cannot protect existing remote `main`
during initial connection. No branch rule was added as a purported mitigation.

Installed CLI source
`vercel/dist/chunks/chunk-UKMRJIIZ.js`, `connectGitProvider`, sends
`POST /v9/projects/{projectId}/link` with only `{type, repo}`. Neither installed
`vercel git --help` nor the official [Git CLI documentation](https://vercel.com/docs/cli/git)
provides a connection-time no-deployment option. The absence of a separate
client-side deployment call does not establish server-side absence of effects.

The live project exposes `gitProviderOptions.createDeployments="enabled"`.
The current official [project update API](https://vercel.com/docs/rest-api/projects/update-an-existing-project)
and [OpenAPI schema](https://openapi.vercel.sh/) expose this property in responses,
but do not list `gitProviderOptions` in the PATCH request schema. Third-party
examples proposing a PATCH were not accepted as supported provider evidence.
No experimental PATCH was made. This is an unresolved support/semantics gap,
not a claim that the setting cannot ever be changed.

The documented `deploymentPolicy` request has environment-scoped Git-source
and deployment-source rules, but inspected provider documentation/schema did
not establish its precise deny/allow semantics, enforcement before deployment
object creation, Hobby availability, or coverage of initial Git connection.
No speculative policy mutation was attempted. A schema field alone does not
prove the required safety guarantee for this project.

### Initial Git-connection deployment risk

Unresolved. Inspected evidence does not prove that the exact connection call
cannot create a Production-target object, nor establish a supported control
effective before it. D3R-GIT sections 0/4/22 require stopping here. No connection
was attempted merely to observe its effects; no new security incident occurred.

### Production-branch protection evidence

Repository default/authoritative branch is verified as `main`. Vercel is not yet
Git-connected, so no linked production-branch setting was established. Official
[Git deployment documentation](https://vercel.com/docs/git) describes production
branch selection and normal non-production branch Preview deployments; it does
not close this project's initial connection safety gap. No Production settings,
repository defaults, protections or DNS were modified.

### Git repository connection result

Not attempted; provider `link=null`. Repository eligibility for the Vercel App
and authenticated Git-provider permissions remain incomplete. This decision is
`BLOCKED` for the earlier safety gate, not a claim that interactive installation
has been proven necessary.

### Native package-layout verification

Not completed. Current source audit confirms the prior unresolved native
Function layout concern. Historical CLI upload inclusion is not final Function
layout evidence and is not Git checkout/build evidence. No local native build,
new dry-run, remote build or generated scientific release was created here.

### Scientific authority-path verification

Fresh path audit confirms `looming_world_experiment`,
`hs_dnp15_neural_validation`, `dnp15_exploratory_yaw`,
`orientation_to_horizontal_motion`, and `exploratory_course_control` compute
authority paths at import from module location (directly or via imported
`SCIENCE_ROOT`). Loaders read the authorities during configuration/replay.
`scenario_playback_api` also reads `hs_dnp15_network_context_audit.json` through
that root during neural playback. `Path(__file__).resolve().parents[2]` rather
than working directory determines the docs location. The candidate copies
authorities into `.neurofly-release/docs/science`; alignment with native module
locations remains unverified. No scientific path semantics were changed.

All ten manifest-listed `docs/science` documents are tracked in Git, and fresh
local byte-count/SHA checks match their committed manifest entries. Required
Python/frontend source configuration, lockfile, inventory and manifest are
tracked. The six untracked implementation files must be explicitly included
in any later authorized commit; local presence is not remote availability.

### Changes implemented

This D3R-GIT attempt changed only `docs/deployment_gate_d3_staging.md` by adding
this section ahead of the preserved historical report. Existing seven other
pending files remain unchanged. No Git-specific configuration was guessed.

### Tests added/updated

None: no code/configuration change was made and the mandatory provider safety
gate stopped the candidate before branch preparation or deployment.

### Focused tests

Not run in D3R-GIT. Existing D3 tests were inspected; historical 10 passes below
are not current test evidence or native package-layout proof.

### Full Python gates

Not run in D3R-GIT after the stop gate. Canonical commands remain
`.venv/bin/python -m pytest`, `-m ruff check .`, and `-m ruff format --check .`.
The bare `python` executable is absent from the current shell PATH; `.venv`
Python is available. Historical 1,274 passes/Ruff results are preserved below
and are not counted as current gates. Full gates remain prerequisites to push.

### Full frontend gates

Not run in D3R-GIT after the stop gate. Canonical commands remain `npm test`,
`npm run lint`, `npm run typecheck`, `npm run build` under `web`, with `.venv/bin`
on PATH for Python-backed tests. Historical 76 passes/build results below are
not current gates. No new frontend build output was generated by this attempt.

### Branch created

None. Remain on `main`; authorized staging branch creation is unused.

### Commit created

None.

### Commit SHA

None for D3R-GIT. HEAD remains the baseline commit above.

### Exact staged/committed files

None. Expected pending scope remains `.gitignore`, `.vercelignore`, `app.py`,
`vercel.json`, `tools/vercel_runtime_build.py`,
`tools/vercel_runtime_entrypoint.py`, `tests/test_vercel_runtime.py`,
`docs/deployment_gate_d3_staging.md`.

### Push result

Not attempted; the one authorized push is unused.

### Production branch unchanged verification

Local `main` and remote advertised `main` match the baseline. No write to either
branch, default branch change, merge, protection change or history rewrite.

### Git-triggered deployment evidence

None. Sole retained provider deployment is the historical CLI ERROR record.

### Preview classification

No new deployment exists to classify. Preview API representation may be
`target=null`; branch naming alone would not be accepted as evidence.

### Blob/OIDC provisioning

Fresh API confirms existing private/available store `store_S3zkyGCIjHi3p79M`,
one connection to this project, environment `preview`, prefix `BLOB`;
`usageQuotaExceeded=false`. Project env records are only Preview-scoped
`BLOB_STORE_ID` and `BLOB_WEBHOOK_PUBLIC_KEY`; zero Production env records and
no static Blob-token env record. Values were not printed or written locally.
No new connection, credential, provisioning operation or Blob object request.

### Frozen D2.2 archive verification

Fresh committed manifest cross-check: inventory
`cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`,
manifest `e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`,
archive SHA `12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`,
3,674,299 bytes, 74 files, 116,239,303 uncompressed bytes. No remote download or
fresh archive verification occurred in D3R-GIT; D2.2 evidence remains historical.

### Runtime startup

Not reached; no new build/deployment.

### /health

Not tested remotely; no usable Preview.

### /ready

Not tested remotely; readiness meaning was not weakened.

### All five canonical scenarios

`BASELINE_CONTROL`, `LOOMING_CIRCUIT_VALIDATION`, `LOOMING_WORLD_EXPERIMENT`,
`HORIZONTAL_MOTION_NEURAL_VALIDATION`, `EXPLORATORY_COURSE_CONTROL`: all remote
playback checks not reached. None was changed or replaced with fallback data.

### Payload identity comparison

Not reached. No remote scientific identity equality is claimed.

### Frontend and same-origin routing

Existing source/configuration inspected; no online verification. Source route
ordering/binding is not evidence of functioning remote routing.

### Browser/WebGL/mobile smoke

Not reached; no Preview URL for operator smoke. Visual-readiness decision is
inapplicable because earlier machine/provider gates remain incomplete.

### Deployment logs

No new build/runtime logs exist. Historical logs below remain the D3 evidence;
no retry or new log-derived provisioning success is claimed.

### Security review

Read-only API responses were filtered in memory, without environment values or
auth tokens in output. No env pull/link command was used. Local root `.env*`
files are absent, `.vercel` contains only ignored project metadata/README, no
generated release tree exists, and no generated directory/archive/env file was
found in tracked Git scope. Reviewed pending files contain no matches for
static Blob credential values, JWT values or signed-token URL patterns; mentions
of credential variable names are guards/documentation, not values. Pattern scans
supplement source inspection and are not a proof against every possible secret.
No Production configuration, deployment, alias or promotion was created here.
No cleanup is required by D3R-GIT. Existing project/failed record/store were kept.

### Cost review

Fresh team API confirms Hobby, store is available and not quota-exceeded.
No upgrade, paid service, new storage/database/compute or other cloud provider.
Availability/entitlement of the missing creation-prevention control remains
unverified; no free or paid capability was inferred from a schema alone.

### Scientific regression review

No scientific/source/authority changes in D3R-GIT. Ten committed science-doc
identity checks passed. No fresh full regression suite or remote scientific
verification is claimed. Frozen release was not regenerated.

### Final Git status

Expected eight pending files only; nothing staged. Tracked diff-stat is
`.gitignore | 3 +++`; untracked files are not represented by that stat.
`git diff --check` passes. Final status, size and secret/generated-scope checks
were repeated after the report edit; file sizes are supplied in the final reply.

### D3 historical decision

The historical security failure remains unchanged; complete original record below.

### D3R historical decision

The historical read-only investigation remained blocked; complete record below.

### D3R-GIT final decision

`BLOCKED`.

### Remaining limitations

Supported creation suppression covering initial connection on this Hobby project
has not been established. GitHub authenticated identity/write permission/App
eligibility, Vercel linked Production Branch, final native authority layout,
current full gates and every remote staging acceptance criterion remain open.

### Exact operator action, if required

Obtain Vercel confirmation for project `prj_W1e15xknFkEC4NYH0OT4JENgBN4i`
under `hd-dev`, connecting `github.com/a104174/NeuroFly`: a supported procedure
available on Hobby that guarantees **no deployment object creation** on initial
Git connection, plus its exact control/endpoint, scope, read-back evidence and
behavior when later enabling only the non-production staging push. Specifically
clarify whether `gitProviderOptions.createDeployments="disabled"` is supported,
can be applied before linking, survives linking, and suppresses connection-time
initialization as well as push/PR events; alternatively document a supported
equivalent. Do not connect the repository as a test. No OAuth/App installation
is requested until that safety procedure is established.

### Next smallest recommended step

Resolve that provider guarantee read-only first. Then resume Git authority and
native-package verification and run full gates before using the conditional
one-commit/one-push authorization. Do not deploy directly via CLI or start Phase 34.

---

# Deployment Gate D3R — recovery preflight stopped before deployment

D3R decision: `BLOCKED`. Date: 2026-10-07.
D3 remains historically `SECURITY_BOUNDARY_FAILED`; its complete record below
is retained. D3R performed zero new deployment attempts and zero cloud mutations.

### Repository and Git findings

Read-only initial checks passed: `main`, HEAD and origin/main both
`521769960d0730f45faec35aa669f91f5fd48d8b`; last five commits unchanged.
Exactly the eight intended D3 files remain modified/untracked. All were inspected.
No unrelated tracked change, Git operation, new release tree or credential file.

### D3 historical incident retained

The original recovery/authentication, unexpected first Production target,
fail-closed missing store metadata, and transient CLI-created OIDC file remain
documented below. No historical failure was rewritten as success.

### D3R provider preflight

Pinned CLI 62.7.0 and identity/team/project checks passed. Read-only project,
deployment, env-record, domain, alias and private-store APIs were inspected.
Environment values were captured only in memory for equality/presence checks;
none were printed, persisted or documented. No link or env-pull command was used.

### Vercel identity/team/project

`hcruz`; `hd-dev / HC`, Hobby; team `team_9xOi3efW7pKf7C6OU0JMwy9r`;
existing project `neurofly`, `prj_W1e15xknFkEC4NYH0OT4JENgBN4i`.
The local link matches those IDs and contains only non-secret metadata.

### Existing failed Production-target deployment

Live API/listing confirmed `dpl_DShTisiRfUpNSyPBb92LnkHAnLsP`,
`target=production`, `readyState=ERROR`, `aliasAssigned=false`.
Deployment and project alias lists are empty. The project has one configured
default domain, `neurofly-liard.vercel.app`; a configured domain is not an assigned
deployment alias. Project `live=false`. Nothing was deleted or recreated.

### First-deployment behaviour analysis

Installed CLI still normalizes explicit Preview to an omitted creation target.
Its first-deployment notice describes automatic Production assignment. Current
[domain documentation](https://vercel.com/docs/domains/working-with-domains/deploying-and-redirecting)
confirms the first-deployment rule. The
[Vercel Labs Services example](https://github.com/vercel-labs/full-stack-service-previews/blob/main/README.md)
describes subsequent CLI deployments as Preview. A
[Vercel staff response](https://community.vercel.com/t/vercel-cli-ignores-target-preview-and-creates-production-deployment/46384)
confirms normal subsequent Preview behavior while an initial record is retained.
[Upstream issue 17069](https://github.com/vercel/vercel/issues/17069) reproduces
explicit Preview becoming Production with zero prior deployments.

None of those inspected sources explicitly establishes how a retained first
deployment in **ERROR**, rather than a completed baseline, participates in the
server's next-target classification. The inspected CLI does not implement the
server-side initialization predicate. No speculative second deployment was made.

### OIDC local-persistence analysis

Historical root `.env.local` is absent; no credential-bearing `.vercel/.env*`
or auth file was found in the local link. D3R did not run link, env pull, build
with pulled credentials, or any command intended to write environment values.
Read-only provider reads and dry-run did not create a local credential file.

### Current project initialization status

API reports `hasDeployments=true`; `latestDeployments` and `targets.production`
both reference the retained ERROR deployment. Thus it demonstrably counts as a
retained deployment and Production target record. This is **not** proof of the
unexposed initialization predicate that chooses the next request's environment.
No successful Production baseline, live release or assigned alias exists.

### Preview-target confidence evidence

General subsequent-Preview behavior and the nonzero deployment state are
established. The required specific ERROR-case guarantee remains unestablished.
Treating `hasDeployments=true` alone as that guarantee would infer the missing
condition. D3R section 6 explicitly prohibits doing so without sufficient
evidence. The gate stopped here; the one authorized attempt remains unused.

### Scientific package-layout audit

Source upload inspection includes the package, `data/reference` metadata and
all ten manifest-listed scientific documents. Installed-module/native Function
layout has not been built or tested in D3R. No source or scientific file was
changed, copied into a new release, rebuilt or regenerated.

### docs/science runtime-path audit

`looming_world_experiment`, `hs_dnp15_neural_validation`,
`dnp15_exploratory_yaw`, `orientation_to_horizontal_motion`, and
`exploratory_course_control` define authority paths at import using module
location, directly or through imported `SCIENCE_ROOT`; their loader functions
read bytes during configuration/replay. `scenario_playback_api` additionally
reads the network-context authority during neural playback. Paths depend on
`Path(__file__).resolve().parents[2]/docs/science`, rather than cwd alone.
The candidate stages verified copies under `.neurofly-release/docs/science`;
upload inclusion does not alone prove native runtime module-path alignment.
Existing isolated D2 tests copy source into the release and exercise a different
layout. This pre-existing integration concern remains unresolved at the stop.

### Vercel deployment dry-run

Read-only command:
`NPM_CONFIG_CACHE=/tmp/neurofly-npm-cache npx --yes vercel@62.7.0 deploy --dry --format=json --scope hd-dev --non-interactive`.
Exit 0; 460 entries, 7,335,614 bytes, 21 ignored entries. Manifest saved under
`/tmp/neurofly-d3r-dry.json`, outside Git; source names/metadata only.
This is an upload-manifest check, not a provider next-target simulation or proof
of a final native Function bundle. No deployment was created.

### Files included/excluded

Included: `app.py`, `vercel.json`, both integration tools, all 156 Python package
entries, frontend package/lock/source/assets, and all ten pinned science documents.
Excluded: `.git`, `.venv`, `.vercel`, data/derived, data/raw, `.env*`, frontend
node_modules/build output, caches and this report. No archive, release tree or
credential pathname was included. `.agents`, `.aws`, `.codex` appear only as
zero-byte directory entries; no child credential/config file was present in the
manifest. The tracked Blender source asset (1,139,464 bytes) is included but is
not a required deployed runtime asset; minimizing that upload remains pending.

### D3 implementation review

Reviewed all eight files. D2 verification/provisioning is reused, pinned bytes
and SHA are checked, OIDC and exact store metadata are required, static Blob
tokens are rejected, and no retrieval occurs in the request path. Factory,
readiness, local frontend behavior and specific-before-catch-all Services routes
are retained. Native package layout remains unproven; no code was modified
because the preceding Preview-confidence stop condition applies.

### D3R changes

Only this report was updated by D3R. Existing D3 integration files were retained
without additional implementation/config changes. No scientific authority changed.

### Tests added/updated

None; stopped on provider preflight before a packaging fix or deployment.

### Focused tests

Committed D2 metadata verifier PASS in D3R, matching all four frozen cross-checks.
No new focused test execution; previous D3's ten tests are historical only.

### Full Python gates

Current Ruff check PASS and Ruff format check PASS (354 files).
Full pytest NOT_RUN in D3R: no new code/config changes and no deployment candidate
could clear section 6. Historical D3 1274-pass result is not asserted as a current
D3R full-suite pass.

### Full frontend gates

NOT_RUN in D3R; no frontend changes or authorized deployment after the stop.
Historical 76 tests/lint/typecheck/build passes remain historical evidence only.

### New deployment command

NOT_EXECUTED. At most one attempt was authorized conditionally; zero were used.

### New deployment target verification

NOT_APPLICABLE; no new deployment object exists.

### Preview environment

Preview metadata exists; no Preview deployment or URL exists in this execution.

### Blob connection

Live private store available, owner matches HC; `projectsMetadata` confirms the
exact existing project connected only to `preview`, prefix BLOB, one connected
project. The Preview store ID was compared in memory and matches the pinned ID.
No Production env records and no static token record. No connection mutation.

### Build-time OIDC

System environment exposure is enabled; Preview OIDC connection metadata exists.
Actual build token issuance/use NOT_RUN. No token was obtained or persisted locally.

### Frozen D2.2 authority

Metadata verifier PASS:
inventory `cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`;
manifest `e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`;
archive SHA `12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`;
3,674,299 bytes. Canonical pathname below remains unchanged. No release rebuild.

### Remote archive retrieval

NOT_RUN; no object download/upload/delete/overwrite in D3R.

### Byte/SHA verification

Pinned metadata checked; cloud archive bytes NOT_VERIFIED in D3R.

### Inventory/manifest verification

Committed metadata PASS; no remote provisioned-release verification.

### Runtime provisioning

NOT_RUN; no archive extraction or runtime generation in D3R.

### No-local-fallback verification

No fallback path introduced or exercised. Remote proof NOT_RUN.

### Read-only runtime verification

NOT_RUN for a D3R runtime; none was created.

### Backend startup

NOT_RUN.

### /health

NOT_RUN remotely; no Preview backend.

### /ready

NOT_RUN remotely; no scientific-readiness claim.

### Same-origin routing

Existing route/binding configuration inspected; remote verification NOT_RUN.

### Five canonical scenario verification

NOT_RUN remotely for BASELINE_CONTROL, LOOMING_CIRCUIT_VALIDATION,
LOOMING_WORLD_EXPERIMENT, HORIZONTAL_MOTION_NEURAL_VALIDATION,
EXPLORATORY_COURSE_CONTROL. No canonical payload was changed.

### Payload identity comparison

NOT_RUN remotely; no equality claim from HTTP status or local metadata.

### Frontend online smoke

NOT_RUN.

### Browser/WebGL smoke

NOT_RUN.

### Mobile smoke

NOT_RUN.

### Deployment logs

No new build/runtime logs. Existing deployment API reconfirmed the backend-build
failure; historical D3 log evidence remains below.

### Security review

No new cloud mutation, Production deployment/promotion/alias, static Blob token,
persisted OIDC file or printed env value. Private store remained private.
Changed-file secret-pattern scan passed. Dry-run excluded credentials, archives
and local runtime/fallback data. No scientific archive/runtime tree enters Git.

### Cost review

Hobby freshly confirmed; store `usageQuotaExceeded=false`, status available.
No paid activation, billing change, DNS change or added infrastructure.
No cost-zero assertion based solely on missing usage data or an allowance.

### Timing observations

No D3R cold/warm/readiness/playback timing; no optimization or Phase 34 work.

### Scientific regression review

No scientific source/data/payload/authority change. Frozen metadata verifier passed.
No new full scientific replay result is claimed in D3R.

### Git diff/status

Final status/stat/check and all changed file sizes were inspected. Exactly eight
intended D3/D3R artifacts; only the report gained D3R edits. No staging/commit/push,
archive, extracted runtime, credentials, build output or unrelated source change.

### D3 historical status

`SECURITY_BOUNDARY_FAILED`, immutable historical result retained below.

### D3R decision

`BLOCKED`.

### D3R status

Stopped before implementation mutation and before the single conditional new
deployment attempt. Auth and ownership passed; ERROR-case Preview classification
could not be established to the required confidence.

### Limitations

`hasDeployments=true` and a retained Production target record establish nonzero
deployment state; they do not document the server predicate used for the next
target. Dry-run does not evaluate it. Native package layout and all current full
quality/remote/product gates remain incomplete. No acceptance criterion lowered.

### Exact operator action if required

Obtain Vercel confirmation, or a supported read-only target-preflight mechanism,
that the retained ERROR deployment on this project counts as initialization and
that CLI 62.7.0's next explicit Preview request will be classified Preview.
Provide only project/deployment IDs and safe state fields; no tokens/env values.
Do not create a Production placeholder or delete/recreate existing evidence.
No message to Vercel or another party was sent by this agent.

### Next recommended step

Resolve that specific provider condition, then resume D3R package-layout tests,
minimal packaging corrections if demonstrated, final dry-run and complete local
gates before considering the still-unused single Preview attempt. Do not start
Phase 34; do not commit or push.

---

The original D3 record follows unchanged. Its outcome remains historical.

# Deployment Gate D3 — resumed attempt stopped at deployment boundary

Current decision: `SECURITY_BOUNDARY_FAILED`.
Date: 2026-10-07. No successful staging deployment exists. The resumed attempt
created one project and connected the existing private store to Preview using
OIDC. The explicit Preview deployment command was assigned to Production by
the provider's first-deployment behavior and failed closed during build.
No further deployment, promotion, store reconnection, or cloud mutation was
attempted after that discrepancy was observed.

## Resumed recovery audit

`main == origin/main == 521769960d0730f45faec35aa669f91f5fd48d8b`.
The only starting change was this untracked previous preflight report; its
contents were inspected and accepted as the intended in-progress D3 artifact.
`git status --short --branch`, both revision checks, `git log -5 --oneline`,
and `git diff --check` passed. No unresolved Git operation was present.
No scientific authority, source, artifact, scenario, or replay was altered.

## Resumed authentication and account authority

Pinned invocation: `NPM_CONFIG_CACHE=/tmp/neurofly-npm-cache npx --yes vercel@62.7.0`.
`--version`, `whoami`, `teams list`, and scoped `project ls` succeeded.
Identity: `hcruz`; team: `hd-dev` / HC;
team ID: `team_9xOi3efW7pKf7C6OU0JMwy9r`; plan: `hobby`.
The team API independently confirmed these safe identity fields.
Initial projects were `heldercruz` and `chupz`; `project inspect neurofly`
returned `project_not_found`. Neither existing project was modified.
Authentication remained available through creation, connection, deployment,
and the subsequent read-only diagnostics; post-error `whoami` returned `hcruz`.

The previous creation failure is recorded below: session-refresh filesystem
denial followed by a provider missing-authentication-token error. The present
attempt succeeded without that error. The exact underlying cause of the
previous session loss cannot be established from these records.

## Corrected pricing and repeated architecture preflight

The prior categorical rejection of VCR as necessarily paid was incorrect.
[Public Vercel pricing](https://vercel.com/pricing) lists **10 GB/month included
VCR image storage** for Hobby. The registry documentation also lists metered
storage pricing; that rate alone does not prove Hobby requires payment.
[Container Functions](https://vercel.com/docs/functions/container-images) are
Beta on all plans and share Function compute limits/pricing.
[Services](https://vercel.com/docs/services/pricing) includes 1M service requests
on Hobby. Included usage is limited and is not an assurance of unlimited free
deployment or sufficient remaining account allowance.

Actual account evidence: Hobby confirmed by CLI and API; `usage` reported billing
cost data unavailable for 2026-10-01 through 2026-10-07, explicitly **not zero
usage**; `contract` found no contract commitments. Remaining VCR/compute quota
was not exposed by those reads. No billing, plan, VCR, or paid feature activation
was performed. Container compatibility with Hobby is supported in principle,
but this specific image size, registry consumption, and Docker build-auth path
were not proven remotely.

Both backend options were re-inspected against repository truth. The existing
Dockerfile requires a separately supplied named `runtime` context and port
adaptation; secure build-only retrieval/context integration would add work.
The selected implementation is native FastAPI with its documented post-install
[build command](https://vercel.com/docs/frameworks/backend/fastapi), retaining
Python 3.12 and calling the existing zero-argument factory unchanged. This avoids
Docker credential/context handling and registry operations. The 116,239,303-byte
runtime plus installed dependencies must fit the native Function bundle limit;
the remote builder installed dependencies, but final bundle size was not reached.

## Actual project, connection, and deployment state

- Project: `hd-dev/neurofly`, `prj_W1e15xknFkEC4NYH0OT4JENgBN4i`.
- Store: `neurofly-runtime`, `store_S3zkyGCIjHi3p79M`; API confirmed
  `access=private`, `ownerId=team_9xOi3efW7pKf7C6OU0JMwy9r`, region `iad1`.
- Store connection dry run and applied connection targeted **Preview only**,
  `--auth oidc`, with `BLOB_STORE_ID` and `BLOB_WEBHOOK_PUBLIC_KEY`.
  No `--add-rw-token`, replacement, upload, deletion, or Production connection.
- Explicit linked project inspection confirmed owner HC and the exact project ID.
- Requested command: `deploy --target preview --scope hd-dev --yes --non-interactive`.
- Actual deployment: `dpl_DShTisiRfUpNSyPBb92LnkHAnLsP`, **target `production`**,
  `readyState=ERROR`, `aliasAssigned=false`, independently confirmed by API.
- Failed deployment URL: `https://neurofly-95mm68hhm-hd-dev.vercel.app`.
  **This is not a verified Preview URL. No Preview identifier exists.**
- Inspector: `https://vercel.com/hd-dev/neurofly/DShTisiRfUpNSyPBb92LnkHAnLsP`.
- Provider build duration reported 35 seconds; basic machine, 2 cores, 8 GB.

Installed CLI code converts `deploymentOptions.target === "preview"` into
`undefined` before sending the creation request (chunk-RYMRVMGD.js). Its output
code describes assignment of the first deployment to Production when no target
is sent (chunk-YGMOJBSP.js). That behavior explains why the explicit flag did
not enforce the required boundary. No `--prod` or promotion command was used,
but a Production-target attempt **did occur**. This must not be described as
Preview success or as an attempt containing no Production deployment record.

## Implemented integration and fail-closed evidence

`vercel.json` defines native backend at root and Next.js frontend at `web`.
Specific `/health`, `/ready`, and `/api/v1/...` routes precede frontend ingress.
The frontend service binding supplies the existing server-only
`NEUROFLY_API_BASE_URL`; local-development API behavior requires no source change.
Services routing and bindings remain Beta; remote functional routing is unverified.

`tools/vercel_runtime_build.py` requires build OIDC and exact store metadata,
rejects static Blob credentials, retrieves only the pinned pathname with CLI
62.7.0, and delegates byte count, SHA, inventory, manifest, safe extraction, and
release verification to the committed D2 implementation. There is no local
archive/data fallback. Only science authority documents and inventory metadata
are copied alongside the provisioned release. No archive or extracted runtime
is uploaded from the checkout; upload exclusions explicitly remove derived data.

`app.py` and `tools/vercel_runtime_entrypoint.py` wire the built release's working
directory, pinned IDs and artifact roots into `create_app_from_env()` without
changing scientific code. Optional local path overrides are removed. The runtime
performs no Blob retrieval or regeneration. An absent release prevents startup;
a corrupted release fails `/ready` and playback in focused tests. No alternate
application or fake response is supplied to hide invalid state.

Remote build logs show the frontend completed, Python 3.12 dependencies installed,
and the backend build stopped with the exact safe error:

```text
ValueError: build store metadata does not match the pinned store
```

The Production build had no Preview-only connected store metadata. The guard
stopped **before Blob retrieval, extraction, provisioning, or backend startup**.
The guard was not relaxed and the store was not connected to Production.

## Resumed scientific identity and product verification

Committed D2 manifest/inventory metadata verification PASS; frozen IDs below
remain unchanged. Focused tests provisioned deterministic D2 fixture input and
verified `/ready` inventory/manifest identities locally. Those test fixtures are
not cloud release inputs or evidence of a cloud retrieval.

Remote archive bytes/SHA, inventory/manifest, `/health`, `/ready`, root product,
`/scenarios`, `/api/v1/scenarios`, all five canonical playback products and payload
hashes: **NOT_RUN**, because deployment failed before runtime creation.
There is no remote scientific identity equality claim. Browser/WebGL, desktop,
mobile, console/network, no-localhost and warm-runtime Blob checks: **NOT_RUN**.
Build logs were inspected; runtime logs do not exist for a functioning backend.
No `D3_READY_FOR_OPERATOR_VISUAL_SMOKE` or `D3_STAGING_VERIFIED` claim is made.

| Required remote gate | Evidence in this execution |
| --- | --- |
| Root product route and `/scenarios` | NOT_RUN; no usable Preview runtime |
| `/health`, `/ready`, `/api/v1/scenarios` | NOT_RUN remotely |
| `BASELINE_CONTROL` playback and payload identity | NOT_RUN remotely |
| `LOOMING_CIRCUIT_VALIDATION` playback and payload identity | NOT_RUN remotely |
| `LOOMING_WORLD_EXPERIMENT` playback and payload identity | NOT_RUN remotely |
| `HORIZONTAL_MOTION_NEURAL_VALIDATION` playback and payload identity | NOT_RUN remotely |
| `EXPLORATORY_COURSE_CONTROL` playback and payload identity | NOT_RUN remotely |
| No localhost/local process dependency, no repeated runtime Blob retrieval | Intended by code; remote proof NOT_RUN |
| WebGL/3D, real UI playback, desktop/mobile, loading/errors, console/network | NOT_RUN remotely |
| Deployment build logs | Inspected; metadata guard failure before retrieval |
| Runtime logs and cold/warm/readiness/playback timings | NOT_RUN; no functioning backend |

Pinned committed authority checked in the resumed attempt:
inventory `cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`,
manifest `e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`.
The manifest pins archive SHA
`12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`,
3,674,299 compressed bytes, 74 files / 116,239,303 uncompressed bytes.
These are metadata/local-test facts, not a D3 cloud archive or payload verification.

## Resumed security review

The CLI `link --yes` unexpectedly generated root `.env.local` containing a fresh
OIDC token. It was immediately removed **without reading or logging its contents**.
This is a transient credential-persistence incident, not a claim that a token
was never written. No token remains in that file, the change set, or report.
No static Blob token or signed private URL was added. Secret-value pattern
scanning of all eight changed files and 28 local frontend static build files
found none. Provider `env ls preview` confirmed only store metadata and the
public webhook key; `env ls production` found no project variables. A subsequent
team listing still confirmed Hobby. The local `.vercel` link contains project
metadata and is ignored. Existing unrelated local environments were not inspected
or modified. No credential pull was used after this incident.

The Production-target incident violates the requested deployment boundary;
the accurate gate decision is `SECURITY_BOUNDARY_FAILED`, even though the build
failed before the private release was retrieved. No subsequent cloud mutation
was attempted. No paid infrastructure or account upgrade was enabled.

## Resumed tests and quality gates

- Focused `pytest tests/test_vercel_runtime.py -q`: **10 passed**; repeated after
  test/environment cleanup. Covers missing OIDC/store metadata, wrong store,
  prohibited static credential, retrieval failure/no fallback, wrong bytes/SHA,
  pinned provisioning/readiness, corrupt readiness/playback, absent release, and
  Services ingress/binding configuration. Existing D2 extraction/authority tests
  remain the security verifier; extraction logic was not duplicated.
- `.venv/bin/python -m ruff check .`: PASS.
- `.venv/bin/python -m ruff format --check .`: PASS, 354 files.
  Initial focused Ruff checks reported one line-length issue and formatting in
  the new tests/build script; those files were formatted and checks repeated.
- `git diff --check`: PASS.
- Frontend `npm test`: first run failed because `python` was absent from PATH;
  repeated with the repository `.venv/bin` on PATH: **76 passed**.
- Frontend `npm run lint`, `npm run typecheck`, `npm run build`: PASS.
  Lint and typecheck were also repeated after interruption with individually
  observed exit code 0; the successful frontend test/build evidence was retained.
- Full `.venv/bin/python -m pytest`: **1274 passed, 1 deselected, 2 warnings**,
  exit code 0, 808.31 seconds. The deselected test is the authenticated integration
  test excluded by the repository's canonical default configuration. Warnings
  concern existing Starlette/httpx and AnyIO deprecations. The interrupted first
  full-suite run has no recovered final result and is not counted as PASS.
  The replacement complete run includes all 10 new D3 tests and the existing
  D2 bundle/extraction/isolated runtime closure gates.

## Resumed changed files and Git boundary

Intended files: `.gitignore`, `.vercelignore`, `app.py`, `vercel.json`,
`tools/vercel_runtime_build.py`, `tools/vercel_runtime_entrypoint.py`,
`tests/test_vercel_runtime.py`, and this report. Next's generated change to
`web/next-env.d.ts` was returned to its original content after local build.
No scientific runtime tree, archive, build output, node_modules or environment
file enters the Git change set. No staging, commit, push or Phase 34 work.

## Resumed stop decision and operator action

`SECURITY_BOUNDARY_FAILED`. The backend build also failed; this is evidence
supporting the stop, not a second current D3 decision.
Authentication recovery succeeded; the blocking issue is now first-deployment
target assignment, not missing authentication or an established paid-plan need.
Before any resumed deployment, establish a provider-supported, verifiable method
to create a deployment strictly as Preview and avoid the CLI's automatic
OIDC file generation. Do not solve this by deploying Production, broadening the
store connection, adding static credentials, or changing readiness. The project
and Preview-only OIDC connection are retained for review; no destructive cleanup
was performed. Visual smoke remains gated on a real successful Preview runtime.

## Consolidation after interruption

This continuation made **no provider calls, deployments, or cloud mutations**.
Provider identifiers, privacy, authentication, and deployment state below are
the observations obtained before interruption; they were preserved rather than
re-created. Local reinspection confirmed the same eight intended changed files
and unchanged `main == origin/main` revision. The prior Python process session
was unavailable, so its partial progress was not converted into a full-suite
PASS. The full local Python gate was restarted with an exit-status/log record
under `/tmp` and completed with 1274 passing tests. Already completed frontend
test/build gates were retained; lint/typecheck were independently reconfirmed.

### Exact failed boundary and attribution

The required boundary was **Preview/staging deployment only, never Production**.
The trigger was provider creation of `dpl_DShTisiRfUpNSyPBb92LnkHAnLsP` with
`target=production` in response to the explicitly Preview-targeted CLI command.
The failed build does not erase that Production-target deployment event.
CLI target normalization and the provider's first-deployment default are supported
by inspected installed CLI code and actual provider/API output. `vercel.json`
contains no Production target selector; no Production flag or promotion was
used. Our execution nevertheless failed to account for that first-deployment
behavior before making the call. The cause is not a scientific implementation
change or ambiguity about the observed target: that target was independently
confirmed. Native retrieval failed because the wrongly selected environment had
no Preview-only store metadata; that is the intended fail-closed guard working,
not grounds to broaden the connection or weaken the guard.

There was also a separate credential-persistence boundary incident: CLI link
reported downloading fresh OIDC and creating root `.env.local`. File creation
was verified, and the file was deleted without inspecting its credential values.
The token was therefore **transiently written to disk**, contrary to the requested
no-persistence boundary. No credential value was exposed in tool output, source,
documentation, Git, or the inspected frontend assets. This is evidence of no
observed disclosure, not forensic proof against every possible external access.
No long-lived Blob credential was requested or added. The remaining local
`.vercel/project.json` was inspected as metadata: only project/team identity,
no credential keys; `.vercel/README.txt` is explanatory CLI output. Both are ignored.

### Retained state and cleanup

It is reasonable to leave the created project and its intended Preview-only
OIDC connection in place based on the observed state: the sole deployment was
`ERROR`, `aliasAssigned=false`; no functioning scientific backend or successful
Production release was created, and no paid infrastructure was deliberately
enabled. Retention does not approve another deployment. No successful or failed
**Preview-target** deployment exists in this execution; the failed URL belongs
to the Production-target record and must not be offered as a Preview smoke URL.

The existing Blob store's **private access setting and stored objects were not
changed by this execution**. No archive was retrieved in D3 and no object was
uploaded, overwritten, or deleted. The store is not wholly unchanged at the
configuration level: the authorized Preview-only project connection was added.
No other connection was intentionally altered.

Required local credential cleanup already completed: the CLI-created root
`.env.local` was removed; only generated metadata remains in ignored `.vercel`.
No further credential-file cleanup is identified. No mandatory cloud deletion
is supported by the evidence. Removing the project, store connection, or failed
deployment would change retained evidence/provider state and is left for an
explicit operator decision; this continuation did not perform it. The failed
deployment record may safely remain for diagnosis. Do not delete the Blob store
or its objects. An operator may let the short-lived token expire, or invalidate
it through supported provider controls if desired; no leaked static secret was
identified that requires rotation here.

### Technical assessment and smallest next step

The implementation's tested local paths are coherent: exact D2 pinning,
authenticated-build preconditions, safe D2 extraction reuse, read-only data,
factory/root wiring, corrupt-release failure, and route/binding configuration.
That does **not** establish end-to-end deployment correctness. Actual OIDC Blob
retrieval in a Vercel build, final Python bundle size and hidden release inclusion,
ASGI runtime startup, Services binding/routing, five remote payload identities,
and browser/WebGL remain unverified. The implementation also lacks an independently
verified Preview-target enforcement mechanism; local test success cannot resolve
the failed boundary or qualify these files as a deployment-ready candidate.

Static review also identified an important unresolved packaging check: several
scientific modules resolve `docs/science` from `Path(__file__).parents[2]`, while
the new build copies verified authority documents into
`.neurofly-release/docs/science`. The new focused runtime test verifies readiness
and invalid playback rejection, not all five valid playbacks under the native
deployment's installed-module layout. Existing D2 closure tests copy application
source into the isolated release and therefore exercise a different layout.
The actual native bundle must demonstrate that module-relative authorities and
the verified release agree without an original-checkout dependency. This is a
specific unresolved integration concern, not proof of a deployed scientific
failure; deployment never reached that point. No implementation change was made
to address it during this local-only continuation.

The smallest next step is an operator review of the retained failed deployment
and a provider-supported way to **enforce and verify Preview targeting before any
new creation request**, together with linking that does not persist OIDC. No
new deployment command is recommended until that method is established. There
is no need to repeat login based on the successful authentication observations,
re-create the project, upgrade the plan, change scientific data, broaden Blob
access, or start Phase 34.

### Final local audit

Final `git status --short`, `git diff --stat`, and `git diff --check` were inspected.
The tracked diff is three ignore-rule additions; the seven untracked files are
the intended D3 entrypoint/config/build/test/report artifacts listed above.
All eight files were inspected, including their sizes and untracked content.
No secret-value patterns or trailing whitespace were found; no archive, derived
runtime tree, credentials, `.vercel` directory, frontend build output, or unrelated
source change enters the change set. Root `.env.local` and `.neurofly-release`
are absent. `web/next-env.d.ts` matches its original content. HEAD and origin/main
remain `521769960d0730f45faec35aa669f91f5fd48d8b`. No file was staged, committed,
or pushed. No new provider action occurred in the post-interruption continuation.

---

The following is the **historical previous blocked preflight**, preserved for
continuity. Its proposed architecture and next-login recommendation are not the
current provider state; the resumed record above supersedes them.

Decision: `BLOCKED`.
Status: stopped at authenticated project creation; no staging deployment exists
from this execution. Date: 2026-10-07.

## Repository and Git findings

Read-only starting audit passed. Branch `main`, clean worktree, and both HEAD
and origin/main were `521769960d0730f45faec35aa669f91f5fd48d8b`.
The latest commit is `docs: verify remote runtime release`.
`git diff --check` passed. No merge or rebase conflict was reported.

## Existing deployment implementation

The Python package requires Python 3.12 and includes the existing FastAPI
factory `neurofly.http_api:create_app_from_env`. Provisioned readiness verifies
the frozen release, requires the release as working directory, and validates
the artifact roots. Invalid provisioned state fails readiness and playback.

`runtime_bundle.py` and its CLI provide pinned manifest/inventory validation,
archive verification, safe extraction, and release verification. The existing
`tools/provisioned_runtime_validation.py` verifies isolated execution, eight
historical replays, five canonical HTTP playbacks, and post-run integrity.

`Dockerfile.backend` provisions an independently supplied named runtime build
context. It runs as a non-root user but currently uses fixed port 8000. It has
no cloud OIDC retrieval step. It was inspected and left unchanged.

The frontend is Next.js 16.3.5, React 19.2.4, with a server-side
`NEUROFLY_API_BASE_URL` abstraction. It currently requires an absolute HTTP(S)
URL. No Vercel configuration or local project link was present. Existing
ignore rules exclude derived scientific data, runtime archives, environments,
node_modules and Next build output. No AGENTS.md was found in the repository.

## Vercel CLI/account/team verification

CLI 62.7.0, Node.js 24.11.1, using `/tmp/neurofly-npm-cache`.
Initial `whoami` succeeded as `hcruz`; `teams list` confirmed `hd-dev` / HC,
Hobby. The successful scoped project list contained `heldercruz` and `chupz`,
and no `neurofly` project. Those existing projects were not modified.

The authorized `project create neurofly --scope hd-dev --non-interactive`
first failed because the sandbox prohibited writing the refreshed CLI session
to `~/.local/share/com.vercel.cli/auth.json`. The explicitly approved retry
outside the sandbox returned a provider error:

```text
reason: forbidden
message: The request is missing an authentication token
retryable: false
userActionRequired: true
```

A follow-up `whoami --non-interactive` reported `Logged out`. The subsequent
project listing started a device login despite `--non-interactive`; it was
canceled immediately. No login code, token or authentication file content is
recorded here. The post-failure project list did not complete.

## Vercel capability/plan audit

Current official documentation states that Services Beta, container Functions
Beta and OIDC are available on all plans. Services supports Next.js and FastAPI
in one project, with service-specific build commands and common ingress.
Hobby supports the proposed two-service structure. Large Python Functions are
eligible by default for new projects; account-specific eligibility was not
verified after the authentication failure.

Sources: [Services](https://vercel.com/docs/services),
[service configuration](https://vercel.com/docs/services/config-reference),
[FastAPI build commands](https://vercel.com/docs/frameworks/backend/fastapi),
[Function limits](https://vercel.com/docs/functions/limitations), and
[OIDC](https://vercel.com/docs/oidc).

## Selected D3 architecture

Provisional choice: one `neurofly` Services project, existing Next.js frontend
at `web`, existing Python/FastAPI backend at the repository root, and native
FastAPI build-time provisioning. No deployment configuration was written.

Native FastAPI has a documented build step after dependency installation. It
can orchestrate authenticated retrieval and the existing D2 verifier without
passing credentials into Docker build arguments or image layers. The backend
would retain the current factory and provisioned readiness contract.

## Architecture alternatives rejected

The previous preflight rejected VCR based only on its metered storage rate.
That conclusion is withdrawn: Hobby includes a limited registry allowance,
as established in the resumed pricing audit above. No registry was enabled
in the previous attempt.
Separate Vercel projects and external providers were not selected.

## Vercel project

The creation request was rejected; no successful creation, project ID or local
link was returned. Last successful listing had no NeuroFly project.

## Preview environment

NOT_RUN. No deployment ID or Preview URL. No Production deployment or promotion.

## Blob store connection

NOT_RUN. Installed `storage connect --help` supports an existing store,
explicit project, Preview-only targeting, and OIDC by default. Static read-write
credentials require a separate explicit opt-in, which was not used.
The existing store was not queried, connected, replaced or modified in D3.

## Authentication model

Proposed build authentication: connected store metadata plus short-lived
project OIDC, with presence checks and no static-token fallback. Runtime would
use only the baked verified release. Browser JavaScript must receive no Blob
credential. This remains unimplemented and unverified.

## Frozen D2.2 authority verification

The committed manifest and inventory passed the existing metadata verifier.
The frozen authorities match the user cross-checks:

- Inventory: `cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`.
- Manifest: `e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`.
- Archive SHA-256: `12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`.
- Archive bytes: 3,674,299; runtime files: 74.
- Store: `neurofly-runtime`, `store_S3zkyGCIjHi3p79M`, `hd-dev` / HC.

Canonical pathname:

```text
neurofly/runtime/v2/12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz
```

## Build-time remote retrieval

NOT_RUN. No local Blob credential handoff or local scientific data was used as
a deployment substitute.

## Cloud archive byte/hash verification

NOT_RUN in D3. Committed D2.2 results remain historical authority.

## Bundle/inventory verification

Committed metadata verification PASS. Cloud archive and provisioned release
verification NOT_RUN in D3.

## Runtime provisioning

NOT_RUN. No runtime archive or extracted release was generated by D3.

## No-local-fallback verification

NOT_RUN in D3; no implementation or deployed runtime exists.

## Read-only runtime verification

NOT_RUN in D3.

## Backend startup

NOT_RUN.

## /health

NOT_RUN remotely.

## /ready

NOT_RUN remotely.

## Same-origin routing

Proposed `/api/v1/...`, `/health` and `/ready` to backend, remaining paths to
frontend. No configuration or routing changes were made.

## Five canonical scenario verification

NOT_RUN online. All five existing scenario contracts remain unchanged.

## Payload identity comparison

NOT_RUN online. No scientific identity claim is made from HTTP status alone.

## Frontend online smoke

NOT_RUN.

## Browser/WebGL smoke

NOT_RUN.

## Mobile smoke

NOT_RUN.

## Deployment logs

NOT_RUN. There are no D3 build/runtime logs because deployment was not started.

## Security review

No credential files or values were inspected. No static Blob token, OIDC token,
private signed URL or secret was added to repository files. No frontend or
backend implementation was changed. No security protection was weakened.
The report is the sole intended change; final diff scanning and Git checks
confirm that no credential value or generated runtime is in the change set.

## Cost review

Account verified as Hobby before the session failure. No plan upgrade, paid
feature, registry, database, Redis, queue or persistent compute was enabled.
Native Function eligibility and actual build costs remain unverified.

## Timing observations

No online liveness, readiness, playback, cold or warm timings were collected.
No profiling or performance optimization was performed.

## Scientific regression review

No scientific source, data, authority, replay value or scenario payload changed.
Manifest and inventory metadata verification passed. D3 did not rerun scientific
replays or inherit a new full-suite PASS from D2.2.

## Files changed

Only `docs/deployment_gate_d3_staging.md`, this non-secret blocked preflight report.

## Tests added/updated

None: no deployment code was implemented before the authentication stop.

## Focused tests

Existing committed manifest/inventory metadata verifier PASS. No new tests.

## Full Python gates

NOT_RUN for this blocked documentation-only D3 attempt.

## Full frontend gates

NOT_RUN for this blocked documentation-only D3 attempt.

## Git diff/status

Starting worktree was clean. Final intended change is this report only.
No staging, commit or push was performed. No archive, extracted release,
node_modules, Vercel build output or environment file was added.

## D3 decision

`BLOCKED`.

## D3 status

Stopped before project creation succeeded, store connection or deployment.

## Limitations

The CLI authentication session is no longer available. Project creation,
project protection defaults, store connection, account-specific native build
eligibility and every online acceptance gate remain unverified.

## Next recommended step

The operator must restore the authenticated CLI session in this execution
environment as `hcruz` using the deliberate device/browser login:

```sh
NPM_CONFIG_CACHE=/tmp/neurofly-npm-cache npx --yes vercel@62.7.0 login
```

Then resume D3 with fresh read-only Git/identity/team/project checks. Inspect
whether `neurofly` exists before any creation retry, and continue only in
`hd-dev` / HC. Phase 34 remains gated on actual verified staging.
