# GET-only experiment HTTP API (Phase 4B)

Phase 4B adds a small FastAPI adapter over the transport-neutral Phase 4A
application boundary.  The adapter reads completed `experiment_artifact_v1`
directories and exposes JSON-safe summaries, selected telemetry, events, and
Phase 3C model comparisons.  It never starts `ExperimentRunner`, the encoder,
or the LIF simulator.

The dependency direction is deliberately one way:

```text
neurofly.http_api
    -> neurofly.experiment_api
    -> experiment_artifacts / experiment_comparison
    -> the scientific core
```

Scientific modules do not import FastAPI or any HTTP module.  The HTTP API
version (`v1`) is distinct from the `experiment_api_v1` application DTO
contract and the `experiment_artifact_v1` persisted artifact schema.

## Application and artifact root

`create_app(root, morphology_artifact_root=None)` receives one explicit
experiment-artifact root and an optional, separate morphology-artifact root. It accepts
only stable artifact identities below that root; callers cannot provide a
filesystem path.  Direct-child artifacts and internal symlinks are rejected,
and every artifact is loaded through the Phase 3B integrity validator.

For local development, the zero-argument Uvicorn factory reads only:

```text
NEUROFLY_EXPERIMENT_ARTIFACT_ROOT=/path/to/data/derived/experiments \
NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT=/path/to/data/derived/morphology_artifacts_v1 \
  uvicorn neurofly.http_api:create_app_from_env --factory
```

The environment variable is server configuration, not experiment identity.
No neuPrint credential is read or required.  CORS is intentionally not
enabled; frontend integration can add an explicit policy later.

## Routes

All scientific routes are `GET` only:

| Method | Path | Meaning |
| --- | --- | --- |
| GET | `/health` | Process/API availability (`status: ok`) |
| GET | `/api/v1` | API and application-contract versions |
| GET | `/api/v1/experiments` | Deterministic experiment summaries |
| GET | `/api/v1/experiments/{artifact_id}` | One Phase 4A summary |
| GET | `/api/v1/experiments/{artifact_id}/timeline` | Exact simulation-time timeline; optional aligned `start_ms`/`end_ms` |
| GET | `/api/v1/experiments/{artifact_id}/bodies/{body_id}` | Persisted telemetry for one body |
| GET | `/api/v1/experiments/{artifact_id}/spikes` | Persisted spike events |
| GET | `/api/v1/experiments/{artifact_id}/events` | Persisted delivered neural events |
| GET | `/api/v1/comparisons?artifact_a=A&artifact_b=B` | Phase 3C comparison, with directional delta `B - A` |
| GET | `/api/v1/morphology` | Validated raw morphology summaries |
| GET | `/api/v1/morphology/{artifact_id}` | One raw morphology summary |
| GET | `/api/v1/morphology/{artifact_id}/bodies/{body_id}` | One source-coordinate raw skeleton |

The OpenAPI document is provided by FastAPI at `/openapi.json`.  It describes
transport routes; the Phase 4A DTOs remain the scientific content source of
truth.

## Scientific semantics

Summaries retain dataset/candidate/graph/model identities, all five free
parameters (`G_LC4`, `G_LPLC2`, `omega_half`, `theta_half`, and `k_syn`),
separate LC4 and LPLC2 population summaries, and separate DNp01 bodies 10001
and 10010.  `validation_status` remains `NOT_EVALUATED`.

Timeline values use simulation time in milliseconds.  State samples are the
neural boundaries `t_n`; step features and drives apply on
`[t_n, t_n + dt)`.  Ranges are inclusive at `start_ms` and exclusive at
`end_ms`, and both endpoints must already be on the stored grid.  The HTTP
adapter never interpolates, resamples, or shifts time.

Delivered event responses preserve the two distinct meanings:

- `structural_weight`: MaleCNS structural contact count;
- `event_increment_mV_eq`: NeuroFly model transform output.

They are not exposed as a generic physiological synaptic-strength field.
Comparisons reuse Phase 3C compatibility classes and source-mismatch policy;
valid `SUMMARY_ONLY_COMPARISON` or `INCOMPATIBLE` results remain visible in a
successful response rather than being reinterpreted by HTTP.

## Error contract

Mapped failures use:

```json
{
  "schema": "experiment_http_error_v1",
  "code": "...",
  "message": "..."
}
```

Malformed IDs/ranges are `400`; missing artifacts or unpersisted body
telemetry are `404`; integrity, unsafe-path, and unsupported-schema failures
are `409`; unexpected store/application failures are `500`.  Error messages
are fixed and do not expose local paths, tracebacks, credentials, or
environment values.  A scientifically valid comparison that is only
summary-compatible still returns `200` with its Phase 3C result.

There are no write routes, execution routes, uploads, authentication,
databases, queues, WebSockets, or frontend dependencies in this phase.

## Future consumer

The intended future mapping is:

```text
Python HTTP transport contract -> TypeScript types -> React/Three.js view
```

The future UI consumes completed artifacts; it does not infer scientific
metadata from filenames or ask the HTTP layer to rerun a simulation.
