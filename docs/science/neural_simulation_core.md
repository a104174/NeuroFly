# Phase 2B — deterministic LIF simulation core

**Status:** implemented as a narrow offline execution slice. This module does
not implement a sensory encoder, looming-to-drive mapping, column-space
projection, visual-angle mapping, behaviour, or motor dynamics.

## Scope and provenance

`neurofly.simulation` builds an immutable simulation view from the validated
`CircuitContract` and runs the Phase 2A central feed-forward experiment:

- 313 candidate nodes remain present;
- exactly 126 LC4 → DNp01 and 185 LPLC2 → DNp01 chemical edges are active;
- all other 20,296 structural edges remain in `CircuitContract` but are not
  simulated by this view; and
- both DNp01 bodies remain distinct.

The graph adapter selects edges by candidate type semantics, never by
neurotransmitter identity. Each active edge retains its MaleCNS
`structural_weight` (the `ConnectsTo.weight` contact count) and carries a
separate explicit `model_sign=+1` assumption. No generic transmitter-to-sign
resolver exists.

## Public execution objects

- `LIFConfig` is an immutable, unit-explicit configuration. Its defaults are
  the Phase 2A published Drosophila modelling priors; callers must provide
  `k_syn_mv_per_contact` because it is a NeuroFly free parameter.
- `SimulationGraph` is an immutable contract-derived view. Use
  `build_phase2b_graph` for the strict 313-node/311-edge scope.
- `ExternalDriveSchedule` contains deterministic, piecewise-constant values
  supplied by the caller, addressed by body ID or node index.
- `LIFSimulator.run` accepts a schedule, body-ID mapping, or a `(steps,
  node_count)` NumPy array. It does not accept `LoomingStimulus`, angular
  features, `BodyColumnInputContract`, or a visual encoder.
- `SimulationResult` keeps read-only in-memory state arrays, spike events,
  delivered events, body/type/side indexing, DNp01 first-spike times, and
  reproducibility metadata.

An ordinary external drive targeting DNp01 is rejected. A zero all-node drive
is valid; no direct environmental input is fabricated for either DNp01 body.

## Equations and units

For each node, the implemented normalized M1 equations are:

```text
tau_m * dv_i/dt = -(v_i - rest_mv) + s_i + external_drive_i
tau_s * ds_i/dt = -s_i
```

`v`, `rest_mv`, `reset_mv`, and `threshold_mv` are mV. `s` and
`external_drive` are voltage-equivalent `mV_eq` model quantities, not measured
currents, conductances, or MaleCNS amplitudes. `tau_m`, `tau_s`, delay,
refractory, and `dt` are ms. `structural_weight` is a dimensionless MaleCNS
contact count. `k_syn_mv_per_contact` is a NeuroFly model scale.

At a delivered edge event:

```text
s_target <- s_target + model_sign * k_syn_mv_per_contact * structural_weight
```

The implementation never substitutes Shiu's fitted `W_syn` value. The
per-edge event increment is exposed separately from the structural count in
`DeliveredSynapticEvent` telemetry.

## Deterministic update semantics

The state at boundary `t_n` is advanced over `[t_n, t_n + dt)` as follows:

1. Deliver all events scheduled for integer step `n`, ordered by source index,
   target index, and edge index.
2. Apply the caller's drive row for the interval.
3. Decay `s` exponentially.
4. Advance every non-refractory membrane state using the exact first-order
   solution for constant drive and exponentially decaying `s`. The equal
   `tau_m == tau_s` limit is handled analytically.
5. Hold refractory membranes at `reset_mv`; their filtered synaptic state still
   decays and incoming events still accumulate.
6. At the interval end, threshold non-refractory states. Timestamp spikes at
   `t_n + dt`, so first-spike precision is bounded by `dt`.
7. Reset spiking states, set the integer refractory countdown, and schedule
   outgoing events at the integer delayed step.

The initial state is `v=rest_mv`, `s=0`, no pending events, no refractory
state, and zero drive unless supplied. Refractory countdown resumes on the
first step after the declared number of held intervals; accumulated `s` is
not cleared. Equal-time events are additive but still processed in stable
order. No wall-clock time or random generator is used.

The configuration rejects non-positive time constants, non-finite values,
non-positive `k_syn`, invalid threshold/reset ordering, and delay or
refractory durations that are not integral multiples of `dt` within a strict
floating-point tolerance.

## Telemetry and limitations

`SimulationResult` exposes boundary-time membrane and filtered-state arrays,
per-interval external drive and delivered coupling, spike timestamps, each
DNp01 body's first-spike time, and metadata containing model/config identity,
graph scope, candidate/dataset, CircuitContract integrity references, timing,
gain, sign policy, baseline/stochastic policy, and input-drive provenance.

The result is in memory; no database or bulk telemetry export is created.
States are model outputs, not observed MaleCNS voltages or conductances.

The graph ends at DNp01. Electrical GF propagation to TTMn/PSI, receptor
kinetics, morphology-derived delays, stochastic input, adaptation,
plasticity, and behaviour remain outside this phase.

## Validation

Focused tests cover configuration and unit-boundary rejection, exact passive
and synaptic decay, threshold/reset/refractory behavior, delayed events,
structural ordering, body/index addressing, deterministic replay, timestep
convergence, LC4-only/LPLC2-only/combined feed-forward propagation, graph
scope, and contract immutability. Synthetic drives in tests are labelled
fixtures and are never used as a production MaleCNS fallback.
