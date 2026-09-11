# Phase 2C — parameter sensitivity and identifiability benchmark

**Status:** implemented as a deterministic, synthetic simulator-validation
layer. No biological calibration, sensory encoder, optimizer, visual-angle
mapping, or additional simulation graph is introduced.

## Scientific boundary

Phase 2C asks how the existing Phase 2B model responds to its free parameters;
it does not ask which values are biologically correct. The provenance layers
remain separate:

- `structural_weight` is the MaleCNS `ConnectsTo.weight` contact count;
- filtered LIF dynamics, zero baseline, common delay, and direct-edge
  `model_sign=+1` are declared NeuroFly modelling assumptions or published
  modelling priors;
- `k_syn_mv_per_contact` and external-drive amplitude/timing are NeuroFly free
  parameters; and
- all Phase 2C population step drives are labelled
  `NEUROFLY_SYNTHETIC_BENCHMARK`.

The benchmark uses the validated `build_phase2b_graph` result: all 313 candidate
nodes remain present and exactly 126 LC4 → DNp01 plus 185 LPLC2 → DNp01 edges
are active. The other 20,296 induced chemical edges remain in the immutable
`CircuitContract` and are not simulated.

## Benchmark API

`neurofly.sensitivity` adds a small layer over `LIFSimulator`:

- `SensitivityScenario` defines `ZERO`, `LC4_ONLY`, `LPLC2_ONLY`, and
  `COMBINED`;
- `SensitivityPoint` holds one explicitly supplied parameter combination and
  validates finite values, scenario semantics, positive `k_syn`, fixture
  timing, and compatibility with the Phase 2B timestep contract;
- `SensitivitySweep` rejects empty or duplicate-ID grids and sorts points by a
  deterministic canonical key;
- `build_synthetic_drive_schedule` broadcasts a piecewise-constant model probe
  to the selected visual population while preserving every body ID;
- `SensitivityRunSummary` records visual spike counts/times, delivered-event
  count and model increment, both DNp01 responses, and a SHA-256 configuration
  identity; and
- `run_sensitivity_point` performs an exact replay and rejects a mismatch before
  returning a summary. `run_sensitivity_sweep` retains deterministic point
  order.

The API does not accept arbitrary target body IDs. Fixture targets are derived
only from the validated graph's LC4/LPLC2 type membership. DNp01 external drive
therefore cannot be requested through this layer, and the underlying simulator
continues to reject it.

Results are compact in-memory objects. Their deterministic dictionaries carry
benchmark/model/candidate/graph identity, parameter values, fixture identity,
and provenance classification. No benchmark data file or credential is
written.

## Synthetic probe used for this audit

The bounded audit used a drive onset of `0 ms`, duration of `1 ms`, total run
duration of `10 ms`, and normally `dt=0.1 ms`. It examined:

- `k_syn_mv_per_contact`: `0.005`, `0.01`, and `0.02`;
- equal per-neuron population drive amplitudes: `100`, `150`, and
  `300 mV_eq`; and
- `dt`: `0.05`, `0.1`, and `0.2 ms` for one representative combined point.

An additional pair, `(k_syn=0.018, drive=180 mV_eq)`, was used only to expose
an identifiability collision. Every number in this section is a
`SYNTHETIC_BENCHMARK_VALUE`, not a default, fitted value, MaleCNS measurement,
or physiological estimate.

## Zero and isolated-population results

`ZERO` preserved all nodes at rest: no visual spikes, no delivered events, and
no DNp01 spikes. With `150 mV_eq` applied for 1 ms, every targeted visual neuron
spiked once at `1.0 ms`, and events arrived at `2.8 ms` after the declared
`1.8 ms` model delay.

### LC4-only (`150 mV_eq`, `dt=0.1 ms`)

| `k_syn` | LC4 spikes | events | total model increment (`mV_eq`) | DNp01 10001 | DNp01 10010 |
|---:|---:|---:|---:|---|---|
| 0.005 | 126 | 126 | 31.81 | no spike; peak `v=-50.018781` | no spike; peak `v=-49.095748` |
| 0.01 | 126 | 126 | 63.62 | no spike; peak `v=-48.037562` | no spike; peak `v=-46.191496` |
| 0.02 | 126 | 126 | 127.24 | first spike `7.7 ms` | first spike `5.4 ms` |

### LPLC2-only (`150 mV_eq`, `dt=0.1 ms`)

| `k_syn` | LPLC2 spikes | events | total model increment (`mV_eq`) | DNp01 10001 | DNp01 10010 |
|---:|---:|---:|---:|---|---|
| 0.005 | 185 | 185 | 24.31 | no spike; peak `v=-50.295230` | no spike; peak `v=-49.971170` |
| 0.01 | 185 | 185 | 48.62 | no spike; peak `v=-48.590461` | no spike; peak `v=-47.942341` |
| 0.02 | 185 | 185 | 97.24 | no spike; peak `v=-45.180921` | first spike `7.5 ms` |

These differences follow the actual active structural totals, not population
size alone. LC4 contributes structural weight 6,362 and LPLC2 contributes
4,862 across the two DNp01 targets. That ordering becomes model-increment
ordering only because Phase 2B explicitly chose the linear free-parameter
transform.

## Combined results

With both populations driven at `150 mV_eq`:

| `k_syn` | visual spikes LC4/LPLC2 | events | total increment (`mV_eq`) | DNp01 10001 | DNp01 10010 |
|---:|---:|---:|---:|---|---|
| 0.005 | 126 / 185 | 311 | 56.12 | no spike; peak `v=-48.314011` | no spike; peak `v=-47.066919` |
| 0.01 | 126 / 185 | 311 | 112.24 | first spike `8.8 ms` | first spike `6.1 ms` |
| 0.02 | 126 / 185 | 311 | 224.48 | first spike `4.7 ms` | first spike `4.1 ms`; 2 spikes |

At `k_syn=0.005`, the isolated subthreshold voltage deflections add to the
combined deflection under the linear LIF state equation. At higher coupling,
threshold/reset/refractory behavior makes the spike output nonlinear without
adding a special supralinear term. This is model behavior, not evidence that
the biological GF implements the same mechanism.

DNp01 body 10001 (`DNp01(GF)_R`) and body 10010 (`DNp01(GF)_L`) remain separate.
Their unequal responses reflect their unequal active structural inputs: 4,800
and 6,424 contacts respectively across the combined slice.

## Drive-amplitude sensitivity

At fixed `k_syn=0.01` in `COMBINED`:

| drive (`mV_eq`) | visual spikes LC4/LPLC2 | first visual spike | events | first DNp01 spike 10001 / 10010 |
|---:|---:|---:|---:|---:|
| 100 | 0 / 0 | none | 0 | none / none |
| 150 | 126 / 185 | `1.0 ms` | 311 | `8.8 / 6.1 ms` |
| 300 | 126 / 185 | `0.5 ms` | 311 | `8.3 / 5.6 ms` |

The `150` and `300 mV_eq` points produce identical event counts, total model
increment, DNp01 peak filtered state, and peak membrane value; the stronger
drive only advances the visual spikes and every downstream time by `0.5 ms`.
Thus drive amplitude above the one-spike threshold is not identifiable from
DNp01 peak or spike-count observables in this 1 ms fixture. Visual spike timing
or known drive timing is required.

## Identifiability assessment

`k_syn` and drive amplitude are not jointly identifiable from DNp01 first-spike
time alone. At `dt=0.1 ms`, two combined points produced exactly the same first
DNp01 spike times (`4.7 ms` for 10001 and `4.1 ms` for 10010):

- `k_syn=0.02`, drive `150 mV_eq`, first visual spike `1.0 ms`, total delivered
  increment `224.48 mV_eq`; and
- `k_syn=0.018`, drive `180 mV_eq`, first visual spike `0.8 ms`, total delivered
  increment `202.032 mV_eq`.

The collision is resolved if visual-neuron spike timing and delivered model
increment or subthreshold DNp01 state are also observed. Other limitations are:

- below the visual threshold, no event is emitted, so `k_syn` is completely
  unobservable;
- once every targeted visual neuron emits one spike, event count no longer
  identifies drive amplitude;
- fixed-step thresholding makes nearby drive amplitudes indistinguishable when
  their visual spikes fall in the same timestep; and
- without measured visual-neuron and DNp01 waveforms, the sweep only describes
  a response surface and cannot identify biological parameter values.

Potential future constraints are therefore deliberately separated:

| Free parameter | Potential constraining observables | Present limitation |
|---|---|---|
| visual drive amplitude/timing | visual spike count and first-spike time relative to drive onset | Level P scaling and temporal filtering do not exist |
| `k_syn` | DNp01 subthreshold waveform/peak after known presynaptic events; DNp01 threshold time | no circuit-specific physiological conversion from contacts to efficacy |
| both jointly | visual spike timing plus DNp01 subthreshold and spike telemetry | DNp01 first-spike time alone is degenerate |

## Timestep sensitivity

The representative combined point used `k_syn=0.01`, `150 mV_eq` for 1 ms, and
a 10 ms run:

| `dt` (`ms`) | first visual spike | first event | 10001 first spike | 10010 first spike | 10001 peak `v` | 10010 peak `v` |
|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 1.0 | 2.8 | 8.75 | 6.05 | -45.003954 | -45.043849 |
| 0.1 | 1.0 | 2.8 | 8.8 | 6.1 | -45.003954 | -45.043849 |
| 0.2 | 1.0 | 2.8 | 8.8 | 6.2 | -45.043562 | -45.043849 |

Visual spike counts (`126/185`), event count (`311`), total model increment
(`112.24 mV_eq`), and physical event-delivery time were unchanged. The maximum
first-spike spread was `0.05 ms` for 10001 and `0.15 ms` for 10010, within the
tested fixed-step resolution. The maximum recorded peak-membrane spread was
about `0.040 mV`; no numerical instability or replay difference was observed.

Peak filtered-state samples vary with `dt` because the first recorded boundary
after an event is farther from delivery at a coarser step. They must not be
compared as though sampled at identical post-event offsets. Phase 2B's aligned
physical-time network test remains the stronger trajectory-convergence check.

`peak_membrane_mv` is the maximum recorded boundary state after the simulator's
threshold/reset rule. In a spiking run it is not an unobserved pre-reset
overshoot and must not be interpreted as one.

## Biological latency boundary

The benchmark records four distinct simulator times:

```text
external-drive onset
    → visual-neuron threshold/spike
    → delayed DNp01 input event
    → DNp01 threshold/spike (if any)
```

There is no biological stimulus time in these fixtures. Applying external
drive directly to LC4/LPLC2 omits upstream visual transduction and processing.
Consequently, no parameter was fitted to the approximately 19 ms experimental
stimulus-to-GF latency, and drive-onset-to-DNp01 timing must not be presented as
that biological latency. The published latency remains a future reference
until a Level P encoder defines temporal semantics and suitable measurements
can constrain the model.

## Remaining limitations

- The probes broadcast equal model drive within a selected type and discard
  biological heterogeneity.
- There is no Level P feature-to-drive mapping and Level C remains disabled.
- The direct-edge sign and linear contact-count transform remain assumptions.
- No automatic fitting, stochasticity, full induced graph, receptor dynamics,
  electrical coupling, plasticity, motor output, or behavior is present.
- The response surface demonstrates numerical/model identifiability properties;
  it does not validate the model against physiology.
