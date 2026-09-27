# Phase 7O — complete 311-body exploratory sensory execution

Phase 7O executed the Phase 7N dry-run configuration without changing its
population, 27-stimulus relative-column battery, sensory equation, transfer
coefficient, or DNp01 LIF configuration. It establishes **313 explicit
identity-resolved model states** in this bounded experiment: 311 exploratory
sensory states and two DNp01 point-neuron states. It is not a calibrated visual,
synaptic, or biological looming model.

## Pinned inputs and exact scope

The committed Phase 7N population (`0db2b29f168039e23858db9831e345cc25fdec8c06775e2f23a7d8d681544356`), coverage plan (`0331ff3d309892ac5284e0da3898683df7b5fb8fd06055090b6100dcea4a6e56`), and execution manifest (`a7d828993674634875b8b8862d40083690e77bb8aa748ad7079135cc8e10725f`) were source-replayed before execution. The direct source chain is CircuitContract plus `body_column_input_v1` → population → anatomy-only coverage → dry-run config → result. Historical A–H samples are regression evidence, not population parents.

The population is 126 LC4 (71 L, 55 R) plus 185 LPLC2 (94 L, 91 R). Source-derived routes give 146 bodies to DNp01 10001 and 165 to DNp01 10010, exactly one direct edge per sensory body. The exact persisted 27-stimulus battery is the 23 Phase 7M stimuli plus four Phase 7N anatomical-coverage disks. No stimulus was added or moved for Phase 7O model outcomes. Its 39 assignment samples produce 12,129 body/exposure rows.

The Phase 7E model is unchanged: dimensionless `x`, `x0=0`, `tau_sens_ms=1`, `gain=1`, `column_overlap_fraction`, and exact exponential zero-order-hold update. State boundary `x[n]` drives DNp01 interval `[n,n+1)` through the Phase 7F assumption `d_i[n]=k*x_i[n]`, with one shared `k=1 mV_eq/state`. Structural edge counts are metadata, not numerical efficacy; no source-count normalization or angular/type-level drive participates. The existing DNp01 LIF configuration is reused. No TTMn or motor pathway is run.

## Execution and controls

All 311 bodies had nonzero anatomical column overlap, exploratory state, and reference transfer contribution under at least one stimulus; these are **software path-coverage** measures. Peak per-body exposure ranged 0.008065–0.913043, and peak per-body exploratory state 0.000767–0.184260. There are 130,931 identity-resolved contribution records over 35 persisted conditions and 421 model intervals. Every target/interval contribution sum matches stored target drive within a source-count/ULP floating-point bound. The bound handles Python's compensated `sum` versus source-order accumulation at 311; no transfer value or LIF parameter changed.

The reference bilateral control uses the persisted `left_expand_33_29` and `right_expand_23_09` schedules. Results below are simulated model quantities:

| DNp01 | Sources | Peak drive (mV_eq) | Vm range (mV) | Simulated model spikes |
| --- | ---: | ---: | ---: | ---: |
| 10001 R | 146 | 1.025669 | -52.000000 to -51.962796 | 0 |
| 10010 L | 165 | 1.410652 | -52.000000 to -51.948753 | 0 |

At the reference peak, the descriptive LC4/LPLC2 model-drive components are 0.299861/0.725808 mV_eq for 10001 and 0.596630/0.814022 mV_eq for 10010. Their ratios are **not** measured pathway strengths. `k=0` and no-source controls have zero drive and remain at -52 mV; LC4-only, LPLC2-only, left-only, and right-only masks route as specified, with no cross-side drive. At `k=2` both reference target-drive peaks double (2.051338 and 2.821304 mV_eq); neither DNp01 spikes. No coefficient was tuned to create or suppress a spike.

The four Phase 7E sentinel trajectories match their canonical artifact exactly (16 stimulus/body comparisons). All 128 Phase 7M bodies match on 23 shared stimuli (2,944 body/stimulus state trajectories, 33,920 per-source/interval contributions, 46 unilateral target timelines). A transient `Phase7M_128_only` bilateral control also reproduces the canonical Phase 7M DNp01 drive, membrane/filter traces and events exactly. It is a regression check, not an extra persisted scientific condition or population parent.

## Artifact and replay

The immutable result schema is `sensory_population_311_experiment_artifact_v1`, stored under ignored `data/derived/malecns/looming_giant_fiber_v1/sensory_population_experiment_311_v1/`. The final ID is `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5`; config SHA-256 is `e3fcd5c9c2155d5696b55d72aeef752dfb9d2448d3b7527b64fd6f9a4e838105`; result SHA-256 is `2b4569acd1e2ae349bfadef646ddea1d14cbf82f13dfb0d467297f34e38a39cf`. The artifact occupies 59,305,871 bytes. It persists exact source routes, assignment, per-body trajectories, per-source contributions, target drive, Vm/filter boundaries, model events and controls. Runtime measurements are in a separate ignored companion JSON, because nondeterministic wall times cannot be part of a content-addressed replay result.

```bash
python -m neurofly.sensory_population_execution_cli generate
python -m neurofly.sensory_population_execution_cli inspect data/derived/malecns/looming_giant_fiber_v1/sensory_population_experiment_311_v1/99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5
python -m neurofly.sensory_population_execution_cli replay data/derived/malecns/looming_giant_fiber_v1/sensory_population_experiment_311_v1/99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5
```

## Resource characterization

On the measured Linux process, source/config load took 0.88 s, anatomical assignment 0.45 s, sensory-state computation 0.14 s, transfer/ledger loop 0.14 s, DNp01 integration 0.012 s, nested regression 0.77 s, serialization/write and integrity reload 1.35 s, and total generation 5.43 s. The separately measured full replay took about 7 s. Baseline RSS was 39,200 KiB; process peak was 562,400 KiB, a 523,200 KiB increase (`/proc/self/status` baseline and `resource.ru_maxrss` peak). The peak is process-wide, not a phase-specific heap measure.

Phase 7N had estimated 40–90 MB, 8–20 s generation, 8–25 s replay (possibly one minute), and a 0.5–1.0 GiB dynamic object graph. Actual artifact bytes fall within that size range, generation/replay are faster, and peak process RSS is within the approximate memory range. Serialization plus provenance/source replay dominates measured runtime; scalar sensory and DNp01 arithmetic is small. No optimization technology was introduced. Artifact bytes divided by contribution records is about 453 bytes/record, but includes assignment/state/target/provenance payloads, so it is not an isolated ledger-row measurement.

## Scientific boundary and next gate

MaleCNS supplies body identities, column topology and routing; synthetic lattice disks are model assumptions; overlap is derived anatomy; sensory state and shared transfer are exploratory model assumptions; DNp01 Vm/spikes are NeuroFly model outputs. Structural contact counts are not synaptic efficacy. Absolute visual angles, functional RFs, presynaptic physiology, pair-specific efficacy and biological population responses remain unresolved.

Decision: `COMPLETE_313_EXPLORATORY_MODEL_STATE_MILESTONE`. The next bounded Phase 8A should assess a neural→motor interface using the already-modeled DNp01 and existing motor-pathway evidence, without treating the exploratory 311 sensory inputs as biologically validated or implementing closed-loop behavior yet.
