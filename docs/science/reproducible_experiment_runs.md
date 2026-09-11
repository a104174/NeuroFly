# Phase 3A — reproducible experiment runs

Phase 3A adds a small offline execution boundary around the existing NeuroFly
pipeline. It does not add scientific equations, calibration, validation, or a
runtime service.

## Pipeline and configuration

`neurofly.experiments.ExperimentConfig` is an immutable, complete description
of one run. It records the experiment schema and identifier, the MaleCNS
candidate/dataset/source endpoint and verified file hashes, the Phase 2B graph
scope, `LoomingStimulus`, duration and neural timestep, the complete
`LevelPEncoderConfig`, the complete `LIFConfig`, the optional pathway mask, the
`VALIDATION_TELEMETRY_V1` profile, and optional empirical-protocol identity.

The four Level P numbers (`G_LC4`, `G_LPLC2`, `omega_half`, and `theta_half`)
and `k_syn` remain explicit NeuroFly modelling parameters. The runner provides
no calibrated or biological defaults. A configuration is identified by a
canonical SHA-256 digest that excludes wall-clock, host, filesystem, and
credential information. Its `validation_status` is fixed to
`NOT_EVALUATED`; an optional protocol ID/version/hash is provenance context,
not an empirical pass claim.

## Execution boundary

`ExperimentRunner` builds the immutable Phase 2B graph with
`build_phase2b_graph`, samples the production `LoomingStimulus` on
`[0, duration)` neural-step boundaries, calls `encode_level_p`, applies the
existing pathway-condition mask, and calls `LIFSimulator`. The runner does
not reproduce looming, encoder, graph-selection, or LIF equations. The graph
is still exactly 313 nodes and 311 direct LC4/LPLC2 → DNp01 edges; no full
induced graph or Level C information is activated.

Terminal/collision samples are rejected by the existing trajectory sampler.
The encoder output is the piecewise-constant drive for the same neural
interval, with no added sensory latency. The simulator remains unaware of
stimulus or encoder semantics, and ordinary external drive cannot target
DNp01.

## Telemetry and replay

`TelemetrySpec.validation_profile()` always retains:

- stimulus theta and angular-expansion-velocity series;
- Level P normalized features and applied LC4/LPLC2 drives;
- LC4 and LPLC2 population spike counts and per-body first-spike times;
- both DNp01 membrane and filtered-synaptic trajectories;
- both DNp01 first-spike times;
- spike events and delivered-event records/summaries.

Callers may add selected visual body IDs without serializing every visual
trajectory. Body IDs and soma sides remain explicit.

The result is an immutable `ExperimentResult`. The runner executes the same
schedule twice and requires exact equality of deterministic simulator arrays,
spikes, delivered events, and first-spike maps. `verify_replay` compares the
result digest for two complete results. Full results remain in memory; an
explicit `write_manifest(path)` call writes a small deterministic JSON
manifest atomically. The manifest excludes full trajectories and contains no
machine-specific execution identity.

## Scientific status and data policy

An experiment run is reproducible software output, not empirical validation.
The pending Phase 2G author-held source data do not block running it, and no
constraint fitting or optimizer is called. Generated manifests are caller
outputs and should live under ignored derived experiment paths; no generated
run output is tracked by this phase. Biological source hashes and model
configuration are retained so future validation can consume selected DNp01
waveforms without changing the run contract.
