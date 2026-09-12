# Deterministic experiment comparison (Phase 3C)

Phase 3C compares two integrity-validated `experiment_artifact_v1` NeuroFly
model runs.
It is not empirical validation, calibration, optimization, ranking, or a
biological correctness score. The comparison is directional: every numeric
difference is reported as **B minus A**, and swapping the inputs reverses
directional deltas.

## Input and compatibility

`compare_experiment_artifacts(a, b)` first uses the Phase 3B offline loader for
both inputs. Corrupt, incomplete, or unknown-schema artifacts therefore fail
before comparison. Valid runs are classified as:

- `EXACT_REPLAY_EQUIVALENT`: identical artifact/config/result identities and
  source provenance;
- `DIRECT_MODEL_COMPARISON`: same source/model identity with intentionally
  different scientific configuration and compatible selected telemetry/time
  base;
- `SUMMARY_ONLY_COMPARISON`: valid summaries can be compared, but source/model
  identity or time-base differences prohibit pointwise trajectories;
- `INCOMPATIBLE`: for example, equal configuration identity with different
  deterministic result identity.

Source identity includes the MaleCNS dataset, candidate/version, source
snapshot hashes, graph scope, encoder ID/version, and neural-model ID/version.
Differences are reported explicitly; they are never silently treated as a
parameter perturbation.

## Configuration differences

The result retains an ordered path/value diff for stimulus, duration and
`dt_ms`, every encoder field including `G_LC4`, `G_LPLC2`, `omega_half`, and
`theta_half`, every neural field including `k_syn`, pathway condition, and
telemetry selection. Source/model identity is reported separately. Execution
metadata and filesystem paths are not scientific differences.

## Time and telemetry policy

Pointwise trajectories are compared only when the persisted `times_ms`,
`dt_ms`, duration, and required body coverage match exactly. No interpolation,
peak alignment, first-spike alignment, time shift, or dynamic time warping is
implemented. Different timestep experiments remain useful through summary
metrics such as counts, first-spike states/times, peaks, and event totals.

When telemetry coverage differs, common bodies (always including DNp01 10001
and 10010) are compared and missing selected bodies are reported. Missing
arrays are never fabricated.

## Model-output metrics

LC4 and LPLC2 remain separate. Each population report contains body counts,
spike counts, first population spike semantics, peak normalized feature, and
peak drive. Each DNp01 report independently contains spike counts, first-spike
time, peak membrane and filtered synaptic state, delivered-event counts,
summed model increments, and pointwise membrane/synaptic errors when allowed.

`None` first-spike values are preserved. `None` versus `None` is
`NONE_BOTH`; only A or B firing is reported as `A_ONLY` or `B_ONLY`; a numeric
delta exists only when both runs spiked. No infinity or sentinel timing value
is manufactured.

Spike and delivered-event totals are reported, with exact sequence equality
used only when event identity is unambiguous. Events are not artificially
paired across changed configurations. `structural_weight` remains the MaleCNS
structural contact count; `event_increment_mV_eq` remains the separate
NeuroFly model transform. No metric calls either quantity physiological
strength.

## Identity and status

`ExperimentComparisonResult` is immutable and has deterministic
`experiment_comparison_v1` JSON-ready serialization and SHA-256 identity. The
summary contains artifact/config/result IDs, policy, compatibility, source and
configuration differences, telemetry compatibility, pathway labels, visual
and DNp01 summaries, event summaries, and limitations. It contains no full
duplicated telemetry and no biological score. Every comparison remains
`empirical_validation_status = NOT_EVALUATED`, even for exact deterministic
replays.

An offline CLI is available:

```bash
python -m neurofly.experiment_comparison <artifact-a> <artifact-b>
```

It emits the same JSON-ready comparison summary and performs no network or
simulation work.
