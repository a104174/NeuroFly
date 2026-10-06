# Deployment Gate D1 — Staging architecture audit and provisioning handoff

## Decision and execution boundary

Stage A: `ARTIFACT_PROVISIONING_REQUIRES_EXPLICIT_STORAGE_DESIGN`.
Final decision: `ARTIFACT_PROVISIONING_REQUIRES_EXPLICIT_STORAGE_DESIGN`.
Deployment status: `BLOCKED`. Stage B: `NOT_RUN`.

The Git-backed cloud build has no configured trusted source from which to obtain
the ignored canonical files. No deployment, project creation, artifact upload,
container build, source-data commit, Git commit or push was performed. Vercel
authenticated team access is available; a read-only search found no NeuroFly
project. This is not a credential blocker or a demonstrated Vercel runtime
incompatibility. An artifact-location/provisioning decision is required first.

## Repository and scientific gate

Initial clean `main == origin/main`:
`8f1c347f35026047bb96ccef5ebc7e1703031ba3`.
Phase 33 and all required previous phases are committed.
`git diff --check` passed.

Fresh offline canonical CLI replays passed for Phase 7O, 8C, 13B, corrected 16,
18, 25, 28 and 30. All five serialized playback hashes match the frozen product.
The Phase 30 preregistration validated source authority records for v1 status,
Phase 24 selection, Phase 25 preregistration, Phase 26 audit, Phase 27 integration,
Phase 28 evidence/preregistration and Phase 29 observation. Phase 31 integration
document hash was also checked. No frozen file was edited.

## Current runtime architecture

Frontend: Next.js under `web/`, React/TypeScript/R3F; canonical npm lockfile.
Production command: `npm ci`, then `npm run build`. No framework migration needed.
The scenario library is server-rendered; playback is requested by a Server
Action. `NEUROFLY_API_BASE_URL` is server-side, mandatory, HTTP/HTTPS validated,
and has no localhost default. Requests explicitly use `cache: "no-store"`.
Use HTTPS for staging. No new cache or scientific optimization was introduced.

Backend: Python >=3.12,<3.13, FastAPI/Uvicorn factory
`neurofly.http_api:create_app_from_env`, packaged through `pyproject.toml`.
Only neuprint-python is exactly pinned; other dependencies have bounded ranges.
There is no Python lockfile. The 509 MiB local site-packages directory includes
development dependencies and is NOT a measured production function bundle.

Several replay loaders use repository-relative `data/...` paths; committed
scientific JSON/Markdown authorities are resolved relative to the source tree.
An installed wheel alone does not contain those authorities. Preserve the source
checkout layout and working directory when assembling a cloud release. Setting
the experiment-root variable does not relocate every frozen scenario dependency.

## Current official Vercel platform audit

Checked official documentation on 2026-10-06:

- [FastAPI](https://vercel.com/docs/frameworks/backend/fastapi): supported; exports
  a FastAPI instance as an entrypoint, deployed as one Function. The existing
  factory would need a small deployment entrypoint, not a scientific rewrite.
- [Functions limits](https://vercel.com/docs/functions/limitations): Python
  standard bundle limit 500 MB; large-functions beta up to 5 GB; Fluid duration
  300 seconds on Hobby, up to 800 on Pro/Enterprise, extended beta 1800.
  Standard request/response body cap is 4.5 MB.
- [Services](https://vercel.com/docs/services): beta on all plans; Next.js and
  FastAPI can ship together, with private service bindings and shared ingress.
- [Monorepos](https://vercel.com/docs/monorepos): separate frontend project can
  use `web/` as Root Directory; no need to move the frontend.
- [Environment variables](https://vercel.com/docs/environment-variables):
  isolate Preview/staging values from future production values.

These constraints do not establish incompatibility here. Measured transport
payloads are below 4.5 MB; internal artifact size is not response size. Actual
production dependency bundle, memory, cold starts and cloud request durations
remain unmeasured. Local replay observations are not cloud guarantees.

## Architecture A assessment — one Vercel project

Plausible after provisioning: Services beta, Next.js service and FastAPI service,
server-only binding named `NEUROFLY_API_BASE_URL`, immutable artifact bundle
verified during build. Advantages: one deployment/rollback and private backend
communication. Risks to verify: beta acceptance, Python packaging/source layout,
bundle size, CPU/memory/concurrency and cold start. Not selected or configured.

## Architecture B assessment — split runtime

Plausible after provisioning: Vercel frontend rooted at `web/`; separate
Python 3.12 container runtime with immutable verified artifacts in a read-only
release image/mount. Advantages: explicit artifact layout and independently
measurable scientific runtime. Costs: second host/release and HTTPS operational
surface. No backend provider has been selected. No alternative Dockerfiles or
provider configs were created speculatively.

## Artifact inventory and size

The accompanying [runtime inventory](deployment_gate_d1_runtime_inventory.json)
records all **66 observed data files**, exact relative locations, byte counts and
SHA-256 values: **84,575,845 bytes** (80.66 MiB), uncompressed file contents.
This is an observed read dependency set, not a built archive or final release
manifest. Directory scanners may require directories/layout beyond file reads;
validate an isolated provisioned release before accepting closure.

All observed data files are ignored, not tracked. All committed `docs/science`
authorities read by these components must accompany the checkout too. The runtime
does require the pinned 111,565-byte optic-column assignment XLSX under
`data/raw`; excluding all source files blindly would break validation.
No morphology/SWC files were observed for these five scenario playbacks.
Other morphology/API pages are outside this five-scenario runtime inventory.

Largest required artifact: Phase 7O population experiment, 59,305,871 bytes.
Phase 13B: 1,137,837 bytes; Phase 18: 11,074,494 bytes; Phase 25: 714,329 bytes;
Phase 28: 225,004 bytes; Phase 30: 4,354,437 bytes.
The entire local derived directories (~360 MiB disk usage) should NOT be shipped.

Each group below contains authority/manifest or source records needed by existing
offline validation. Numerical, geometry and provenance roles remain unchanged;
the inventory does not redefine any scientific authority.

| Current runtime location | Observed bytes | Deployment requirement |
| --- | ---: | --- |
| `data/derived/experiments/dnp15_exploratory_yaw_artifact_v1/243914905c17ceb1285c645aa9e9700b602a9e22c8703c9f9ce4c7fe4f7e935d` | 225,004 | Required observed read; retain exact bytes/path |
| `data/derived/experiments/exploratory_course_control_closed_loop_artifact_v1/f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581` | 4,354,437 | Required observed read; retain exact bytes/path |
| `data/derived/experiments/hs_dnp15_neural_validation_artifact_v1/2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113` | 714,329 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/body_columns_v1/column_body_summaries.jsonl` | 122,810 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/body_columns_v1/column_inputs.jsonl` | 3,634,995 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/body_columns_v1/column_manifest.json` | 3,065 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/closed_loop_scenario_artifact_v1/55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` | 1,137,837 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/connections.jsonl` | 2,866,971 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/exploratory_planar_body_plant_artifact_v1/bb3696faae558778555601991de3fd36081d5853c889fcb7aac5ffd79593eba3` | 41,816 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/full_sensory_coverage_plan_v1/0331ff3d309892ac5284e0da3898683df7b5fb8fd06055090b6100dcea4a6e56` | 131,824 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/full_sensory_population_plan_v1/0db2b29f168039e23858db9831e345cc25fdec8c06775e2f23a7d8d681544356` | 181,328 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/g1_proxy_passive_electrical_response_artifact_v1/72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` | 37,535 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/looming_world_experiment_artifact_v1/ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c` | 11,074,494 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/manifest.json` | 1,124 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/model_derived_ttmn_target_dispatch_artifact_v1/3bc011f9a8831f5291b6078d6132ef0dc6d6d7e87cc45ecfaa957ec80b8af360` | 47,480 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/motor_neural_pathway_contract_v1/a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c` | 24,490 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/motor_neuron_muscle_target_contract_v1/5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0` | 26,974 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/neurons.jsonl` | 124,300 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/sensory_dnp01_ttmn_adapter_v1/5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` | 14,986 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/sensory_population_execution_311_v1/a7d828993674634875b8b8862d40083690e77bb8aa748ad7079135cc8e10725f` | 79,291 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/sensory_population_experiment_311_v1/99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` | 59,305,871 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/static_normalized_muscle_activation_artifact_v1/4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb` | 35,407 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/synthetic_dnp01_ttmn_interface_v1/4321adeee0412a79632ce4e008a1b8eaad22ee167f97f4a98521a9e71d9ef936` | 43,317 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/synthetic_ttmn_output_rule_v1/1c8aeac685646dac16fbb66f163743b662a3cd9a0e8f9f7582210fd7b39b9ab3` | 68,988 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/ttm_abstract_electrical_input_artifact_v1/1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa` | 23,513 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/ttm_exploratory_actuator_command_artifact_v1/478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40` | 27,548 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/ttm_g1_electrophysiology_observation_artifact_v1/5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f` | 40,012 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/ttm_g1_observation_mapping_artifact_v1/f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f` | 26,552 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/ttm_g1_proxy_mapping_artifact_v1/030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8` | 9,322 | Required observed read; retain exact bytes/path |
| `data/derived/malecns/looming_giant_fiber_v1/ttm_neuromuscular_input_receipt_artifact_v1/e04803f60304f58d0e6d27fdea5d15debb60358b46721caac09f10165c6df9c4` | 38,660 | Required observed read; retain exact bytes/path |
| `data/raw/malecns/optic-column-type-assignments-v1.0.xlsx` | 111,565 | Required observed read; retain exact bytes/path |

## Recommended smallest provisioning design — not implemented

Publish ONE immutable release bundle at a controlled, approved release/object
location; do not add ignored files to Git. Pin the bundle by content hash and
application commit, not `latest/`. During build, retrieve it once using scoped
server-side credentials where necessary; verify archive hash and every file hash;
reject traversal/symlinks or unexpected layout; retain repository-relative paths.
Validate every canonical authority and replay in the assembled release, then
bundle/mount read-only. No network retrieval during scientific requests and no
browser artifact authority.

The missing operator decision is the controlled destination and its release
ownership/access policy. No existing remote artifact release/bucket was found
in repository configuration. Vercel account access alone does not resolve this.

## Environment contract

| Variable | Consumer | Current meaning / staging requirement |
| --- | --- | --- |
| NEUROFLY_API_BASE_URL | Next.js server only | Required; HTTPS backend or private service binding; no NEXT_PUBLIC exposure |
| NEUROFLY_EXPERIMENT_ARTIFACT_ROOT | FastAPI factory | Required existing experiment store root |
| NEUROFLY_SCENARIO_ARTIFACT_PATH | FastAPI | Optional override for pinned Phase 13B artifact; not a global relocation mechanism |
| NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT | FastAPI | Optional morphology API store; not needed by observed five-scenario playback |
| NEUROFLY_CIRCUIT_CONTRACT_ROOT | FastAPI | Optional structural API store |
| NEUROFLY_MOTOR_EXPERIMENT_ARTIFACT_ROOT | FastAPI | Optional motor experiment API store |

Do not commit credential values. Existing local env files and data roots are
ignored. Root `.env` is ignored; arbitrary new `.env.*` names are not uniformly
protected, so do not create such files for deployment.

## Local / Preview / future Production matrix

| Environment | Frontend / backend | Artifacts | API / CORS / readiness |
| --- | --- | --- | --- |
| Local | Local Next.js + local Uvicorn | Existing ignored canonical paths | Explicit local API URL; server fetch; /health is liveness only |
| Preview / staging | Vercel + host pending architecture decision | Approved immutable verified bundle REQUIRED | HTTPS/binding URL; no wildcard CORS; scientific readiness not yet implemented |
| Future Production | Not provisioned or authorized by D1 | Independently pinned immutable release | Separate environment values and release gate; not implied ready by staging |

## HTTPS / CORS / preview origins

Current scenario browser interaction calls its own Next.js Server Action; the
Next server fetches FastAPI. Browser CORS is therefore not needed for that path.
Do not add wildcard CORS to solve a server-to-server request. Services could keep
the scientific backend private. A separately public backend requires HTTPS.
If later browser-direct API access is introduced, allow only approved origins;
do not broadly allow arbitrary vercel.app previews.

## Health, readiness, security and failure semantics

Existing `GET /health` returns process status/read-only metadata. It is NOT a
scientific readiness check. Before deploying, add a bounded readiness contract
that checks the expected release manifest, required files and pinned authorities,
without expensive full numerical replay on every probe. Missing/mismatched
authority must yield non-ready. This has not been implemented past the gate.

Inspected FastAPI application routes are GET-only. Artifact-store path/integrity
failures have typed errors; scenario validation failures return sanitized 503.
Unsupported scenario returns typed 404. No write endpoints or arbitrary
user-supplied filesystem-path scenario selector were located. Existing health,
OpenAPI/docs and generic artifact listings should be reviewed when deciding the
public ingress scope. No CORS wildcard was introduced. This is a bounded source
review, not a penetration test.

Scenario replay failures currently produce sanitized user errors but the route
does not log the caught validation exception. Add safe server observability
before online staging without exposing paths/secrets. Replay-heavy public
endpoints present CPU/abuse risk: consider provider protection before public beta,
not a new authentication or caching architecture in D1.

Keep existing frontend unavailable/no-synthetic-fallback behavior.
For staging, configure no-index response headers at the hosting layer after
selecting the deployment configuration. No UI claim scope changed.

## Fresh local baseline — not HTTP/cloud cold/warm measurements

Two sequential in-process playback adapter calls per scenario were measured.
Another historical replay process ran concurrently. These observations include
validation and serialization, are not isolated benchmarks, HTTP response times,
frontend readiness times or evidence of cloud cold starts. No cache was added.

| Scenario | First call seconds | Second call seconds | Transport bytes |
| --- | ---: | ---: | ---: |
| BASELINE_CONTROL | 8.454 | 8.346 | 10,290 |
| LOOMING_CIRCUIT_VALIDATION | 8.521 | 8.337 | 12,021 |
| LOOMING_WORLD_EXPERIMENT | 21.507 | 20.618 | 283,219 |
| HORIZONTAL_MOTION_NEURAL_VALIDATION | 0.140 | 0.136 | 138,336 |
| EXPLORATORY_COURSE_CONTROL | 0.704 | 0.700 | 453,262 |

All raw transport hashes equal the committed Phase 32 audit's regression pins.
The complete corpus of authority hashes remains in the existing committed
science contracts; this handoff does not create replacement scientific authority.

## Deployment status, checks and rollback

No frontend/backend deployment configuration added; no provider project created.
No online URL or deployed commit exists for this gate. Thus all online route,
direct-refresh, WebGL, mobile, playback-control, online-error and cold/warm smoke
checks are NOT_RUN. No screenshots or synthetic playback data generated.

Executed: eight historical CLI replay gates, five payload identity checks, two
per-scenario adapter loads, artifact read inventory, ignore checks, Ruff check,
Ruff format check and diff check. Full pytest/frontend test/lint/typecheck/build
pre-deployment gates remain NOT_RUN in D1 after the Stage A provisioning stop.
Previous Phase 33 results are not claimed as fresh D1 gate results.

Resume procedure:
1. Approve the immutable artifact release destination and provisioning policy.
2. Implement exactly one selected architecture, bounded readiness and safe logs.
3. Run full canonical quality/replay gates and isolated release validation.
4. Obtain any required explicit commit/push authorization for Git-backed config.
5. Deploy dedicated staging, then verify all five online payload hashes and
   browser interactions, HTTPS/static assets/mobile/direct refresh/error states.

Rollback after an eventual deployment: revert/promote the previous tested Vercel
deployment and previous backend release if split; retain and pin its matching
immutable artifact version. No mutable scientific data edits.

## Phase 34 inputs and next bounded action

Measure production-build and deployed request CPU/memory, replay vs adapter vs
network/SSR time, first vs repeat requests, genuine cold/warm behavior, payload
bytes, WebGL startup, scrub responsiveness and no-fallback error behavior.
Do not optimize or introduce scientific caching before those baselines.

**Next bounded action:** approve a controlled immutable release location for the
66-file runtime data bundle, with commit/hash pinning and read-only consumption.
