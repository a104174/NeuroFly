# Portable experiment-artifact contract (Phase 3B)

Phase 3B persists a completed Phase 3A `ExperimentResult` as a small,
portable, offline scientific artifact. It is an observation/persistence
boundary only: it does not change the LoomingStimulus geometry, Level P E1
encoder, Phase 2B equations, graph scope, or empirical status.

## Artifact layout

`export_experiment_artifact(result, destination)` creates a new directory
containing exactly:

```text
manifest.json
telemetry.json
spikes.jsonl
delivered_events.jsonl
summary.json
```

The artifact schema is `experiment_artifact_v1`. The exporter stages all
files in a temporary sibling directory, validates the complete staged
artifact, and then atomically renames it into place. Existing directories
are never overwritten or merged. Generated artifacts belong under
`data/derived/experiments/`, which is ignored by Git; the tracked
`data/reference/` hierarchy remains reserved for project-owned scientific
metadata.

## Identity and provenance

The manifest contains the complete canonical `ExperimentConfig`, its SHA-256
configuration identity, the Phase 3A result identity, the Level P and LIF
model identities, candidate/dataset/source snapshot references, graph-scope
identity, selected telemetry profile, all five free model parameters, and
optional empirical-protocol context. `artifact_id` is deterministic from the
artifact schema, config/result identities, and payload file records. Export
time, hostname, absolute paths, credentials, and other execution metadata do
not enter scientific identity.

`validation_status` remains `NOT_EVALUATED`. Presence of an empirical
protocol ID is provenance context, not an empirical validation claim.

## Telemetry and events

`telemetry.json` is a UTF-8 JSON object with explicit `ms` time units,
`dt_ms`, boundary times, interval convention, stimulus samples, normalized
LC4/LPLC2 features, population drives, and exactly the selected Phase 3A body
telemetry. State arrays are boundary-valued at `times_ms`; interval arrays
apply over `[t_n, t_n + dt_ms)`. Both DNp01 bodies are always retained by the
validation profile, while selected visual bodies are included only when
requested.

`spikes.jsonl` records fixed-step spike events with time, step, body ID, node
index, and neuron type. `delivered_events.jsonl` records delivery time/step,
source and target IDs/indices, `structural_weight`, `model_sign`, and
`event_increment_mV_eq`. `structural_weight` remains the MaleCNS structural
contact count; `event_increment_mV_eq` is the separate NeuroFly model
transform and is checked against `k_syn` during loading.

`summary.json` contains only deterministic Phase 3A summaries: population
spike counts/times, per-DNp01 delivered-event counts and model-increment sums,
first-spike times, counts, result/config identities, and replay/status flags.
It contains no biological score, escape label, or fitness value.

## Integrity and offline loading

The manifest records SHA-256, byte counts, schemas, and record counts for all
payload files, plus a manifest digest that excludes itself to avoid a circular
hash. `load_experiment_artifact(path)` rejects unknown schemas, missing or
extra files, malformed JSON/JSONL, digest/count/time-base mismatches, invalid
body/event identities, non-finite values, altered model increments, and any
status other than `NOT_EVALUATED`.

Loading uses only the package and artifact files. It does not require
neuPrint, credentials, Git, the original process, stimulus evaluation,
encoding, graph construction, or neural simulation. It returns an immutable
loaded view with the reconstructed selected `ExperimentResult`.

## Replay

`replay_experiment_artifact(path, circuit_contract)` is separate from ordinary
inspection. It loads the persisted configuration, reruns the existing
`ExperimentRunner` with an explicitly supplied local contract, and reports
which deterministic layer differs (configuration, stimulus, encoder drive,
spikes, delivered events, DNp01 telemetry, or result digest). It never
silently substitutes a contract or downloads source data.

The artifact is designed for future TypeScript/backend consumers: UTF-8 JSON
and JSONL, explicit units, stable body IDs, no pickle or NumPy object arrays,
and no frontend/runtime dependency. It is a portable run observation, not an
empirical validation result.
