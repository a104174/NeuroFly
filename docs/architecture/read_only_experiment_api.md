# Read-only experiment application boundary (Phase 4A)

Phase 4A defines a transport-neutral Python boundary for completed
`experiment_artifact_v1` runs.  Phase 4A itself intentionally adds no web
framework; Phase 4B now provides the separate FastAPI adapter documented in
[`http_experiment_api.md`](http_experiment_api.md).  Future
TypeScript/React/Three.js layers can consume the same JSON-safe DTOs without
importing scientific dataclasses or learning the artifact directory layout.

## Dependency direction

The application boundary is `neurofly.experiment_api`.  It depends on the
Phase 3B artifact loader and the Phase 3C comparison API:

```
application DTO/service
        -> experiment_artifacts
        -> experiments / simulation / sensory
```

The scientific modules do not import this application layer.  Store requests
only load completed artifacts; they never call `ExperimentRunner`, create a
stimulus, encode a drive, or run the LIF simulator.

## Version and JSON policy

Every DTO uses `experiment_api_v1` and a stable `kind`.  `to_dict()` returns
only dictionaries, lists, strings, finite numbers, booleans, and nulls;
`to_json()` uses sorted keys and deterministic JSON serialization.  Internal
dataclasses, enums, `Path` values, NumPy arrays, and Python-specific reprs are
not exposed.

The DTOs preserve units in field names and unit fields: `time_ms`, `theta_rad`,
`angular_expansion_velocity_rad_s`, `membrane_mv`, and `*_mveq`.

## Artifact store

`ExperimentArtifactStore(root)` is explicitly configured with one local,
read-only root.  It discovers direct child artifact directories and validates
each through `load_experiment_artifact()`.  Stable lookup accepts only a
lowercase 64-character SHA-256 artifact identity; raw paths, `..`, absolute
paths, and symlink entries are rejected.  Corrupt or unsupported artifacts
remain errors rather than being silently skipped.

The store provides:

- `list_experiments()` / `get_experiment(artifact_id)`;
- `get_experiment_by_config_id(config_sha256)` and
  `get_experiment_by_result_id(result_sha256)`;
- `get_timeline(artifact_id, start_ms, end_ms)`;
- `get_body_telemetry(artifact_id, body_id)`;
- `get_events(artifact_id)`;
- `get_comparison(artifact_a_id, artifact_b_id)`.

No database, cache, upload, or write operation exists.

## Experiment summary

`ExperimentSummary` exposes artifact/config/result identities, dataset and
candidate provenance, CircuitContract integrity, graph scope, encoder/neural
model identities, pathway, duration and `dt`, telemetry profile, all five
free parameters, independent LC4/LPLC2 summaries, and independent DNp01
10001/10010 summaries. The summary includes the persisted encoder population
mapping and the LIF membrane rest/threshold references, used by the Phase 6A
activity projection to validate signal granularity and optional model-state
normalization. These values are copied from the validated run configuration;
the application does not alter or re-identify the artifact.
`validation_status` is preserved as
`NOT_EVALUATED`; execution success is not empirical validation.

## Timeline and body telemetry

`ExperimentTimeline.times_ms` contains persisted neural state boundaries
(`steps + 1`).  `step_times_ms` contains interval starts (`steps`), and
feature/drive arrays apply on the left-closed, right-open interval
`[t_n, t_n + dt)`.  Body membrane/synaptic states use boundary samples;
external-drive and incoming-coupling arrays use `step_times_ms`.

Optional ranges are exact grid selections: `start_ms` is inclusive and
`end_ms` is exclusive for step values, with the end boundary retained for
state trajectories.  Non-aligned ranges are rejected; no interpolation is
performed.

Body views preserve stable body IDs, neuron type, soma side, state arrays,
and persisted spike times.  Missing or unrecorded bodies raise an explicit
`BodyTelemetryUnavailableError`; no trajectory is fabricated.

## Events and structural semantics

Spike views expose time, body ID, node index, neuron type, and step.  Delivered
events expose delivery time, source/target body IDs, structural contact count,
model sign, and `event_increment_mV_eq`.

`structural_weight` remains the MaleCNS structural contact count.  The model
increment remains the NeuroFly transform output.  Neither is relabelled as
physiological synaptic strength.

## Comparison boundary

`get_comparison()` delegates to Phase 3C without reinterpretation.  It
preserves directional `B - A` differences, compatibility classes, source and
configuration differences, exact-time-base limitations, LC4/LPLC2 metrics,
both DNp01 bodies, event summaries, and `NOT_EVALUATED` status.  A valid
`SUMMARY_ONLY_COMPARISON` is returned as a result; the service does not turn
it into a dense comparison for presentation convenience.

## Errors and HTTP mapping

The service distinguishes invalid IDs, not-found artifacts, path escapes,
corrupted/unsupported artifacts, unavailable body telemetry, invalid aligned
ranges, and comparison failures.  Phase 4B maps these to stable
`experiment_http_error_v1` responses and GET-only routes such as
`/api/v1/experiments`, `/timeline`, `/bodies/{id}`, `/events`, and
`/comparisons`.

Phase 4A itself has no write routes, authentication, simulator control,
calibration, or empirical scoring.  The separate Phase 4B HTTP adapter adds
GET-only transport routes; it does not change this scientific boundary.
