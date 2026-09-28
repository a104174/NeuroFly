# Phase 8H — condition-explicit sensory-to-PSI/DLMn event adapter

**Status:** `PASS` — the persisted Phase 7O event boundary composes through
the shared Phase 8G relay, including a valid deterministic empty result for
the canonical sensory condition. No PSI/DLMn state dynamics are introduced.

## Source and condition contract

The adapter loads and validates the immutable Phase 7O artifact
`sensory_population_311_experiment_artifact_v1`:

- Upstream artifact ID:
  `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5`
- Config SHA-256:
  `e3fcd5c9c2155d5696b55d72aeef752dfb9d2448d3b7527b64fd6f9a4e838105`
- Result SHA-256:
  `2b4569acd1e2ae349bfadef646ddea1d14cbf82f13dfb0d467297f34e38a39cf`

Generation and replay require both an explicit source artifact and an exact
condition ID. The selected canonical condition is `reference_bilateral`.
Only its persisted `simulated_spikes` records with semantics
`SIMULATED_DNP01_MODEL_SPIKE` are eligible. The adapter reopens the
content-addressed source, validates its manifest and source-contract
identities, resolves node/type/side against the pinned CircuitContract, and
preserves body, node, condition, step and time. Event IDs are deterministic
hashes over the source artifact, condition, stored spike record and resolved
identity.

The adapter never infers events from membrane voltage, external drive,
filtered synaptic state, or distance to threshold. It has no synthetic
fallback. The canonical reference has positive external DNp01 drive and
subthreshold membrane movement, but no persisted spike events; the filtered
state is zero. Those non-event fields do not enter the motor relay.

## Shared relay and provenance

Phase 8H reuses the Phase 8G active-edge policy and single two-layer relay
primitive. The active edges are the four pinned DNp01→PSI routes followed by
the ten pinned PSI→DLMn routes. The two supplemental PSI↔PSI edges remain in
the source contract but inactive. The parallel Phase 6C/8C DNp01→TTMn branch
is not run or changed here.

The upstream kind is `SIMULATED_FROM_SENSORY_EXPERIMENT`; its meaning is a
NeuroFly DNp01 LIF model event, not an observed biological Giant Fiber spike.
Downstream records reuse the Phase 8G schemas `psi_routed_event_v1` and
`dlmn_routed_event_v1`, with provenance `EXPLORATORY_ROUTED_MOTOR_EVENT` and
the upstream artifact/condition included in record identity. Phase 8B/8G
synthetic fixture provenance remains separate, and the Phase 8G synthetic
artifact ID and hashes remain unchanged.

The model copies the source integer step and `time_ms` through both route
layers under the declared zero-added-delay exploratory assumption. Every
structural count is metadata only: one traversed edge produces one route
record. No gain, amplitude, PSI/DLMn `SpikeEvent`, latent state, recurrence,
muscle output, or behavior is modeled.

## Canonical result and all-condition audit

The selected `reference_bilateral` source condition contains 0 DNp01 events,
therefore the result contains 0 PSI routed records and 0 DLMn path records.
This empty ledger is a valid result. All 35 persisted Phase 7O conditions were
audited independently; each has 0 DNp01 events, 0 PSI records and 0 DLMn
records. No condition is aggregated with another.

The existing Phase 8C adapter was also replayed for `reference_bilateral`:
its two TTMn state trajectories remain exactly zero. The two downstream
branches are therefore consistent for this source condition without merging
their model semantics.

## Artifact and replay

The immutable Phase 8H artifact is stored under the ignored derived-data root:

`data/derived/malecns/looming_giant_fiber_v1/sensory_psi_dlmn_event_relay_artifact_v1/b13813300a8be7ffa644393d01e78f032705fd4e155665bc60f50f7abee45803`

- Schema: `sensory_psi_dlmn_event_relay_artifact_v1`
- Artifact ID: `b13813300a8be7ffa644393d01e78f032705fd4e155665bc60f50f7abee45803`
- Config SHA-256: `f841d1dd298fcee4085a338fbfa5fe97ffb5855e323188c76eebad565223243f`
- Result SHA-256: `c52e36164fc16495b16a11a60f50367daae3c4890293487b537c6c7ef9a79c83`
- Size including manifest: 20,817 bytes

Full replay reloads the Phase 7O artifact, selected condition, local source
contracts and pinned motor contract; re-extracts only that condition's
persisted spikes; reruns the shared relay; and requires exact config, result
and artifact identity. Offline replay makes no network request. The Phase 8G
synthetic artifact was separately replayed before and after the shared-core
extraction with its original identity unchanged.

```sh
python -m neurofly.sensory_psi_dlmn_event_adapter_cli generate \
  data/derived/malecns/looming_giant_fiber_v1/sensory_population_experiment_311_v1/99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5 \
  reference_bilateral
python -m neurofly.sensory_psi_dlmn_event_adapter_cli inspect \
  data/derived/malecns/looming_giant_fiber_v1/sensory_psi_dlmn_event_relay_artifact_v1/b13813300a8be7ffa644393d01e78f032705fd4e155665bc60f50f7abee45803
python -m neurofly.sensory_psi_dlmn_event_adapter_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/sensory_psi_dlmn_event_relay_artifact_v1/b13813300a8be7ffa644393d01e78f032705fd4e155665bc60f50f7abee45803 \
  data/derived/malecns/looming_giant_fiber_v1/sensory_population_experiment_311_v1/99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5 \
  reference_bilateral
```

Focused tests use a separate temporary, content-addressed Phase 7O-shaped
fixture containing a valid-format stored event to verify future nonzero
compatibility (1 origin → 2 PSI route records → 10 DLMn path records) and a
bilateral case. They do not edit or re-label the canonical Phase 7O artifact.

## Scientific boundary

MaleCNS and Phase 7O source manifests provide identity and provenance;
MaleCNS provides the structural routes. The upstream DNp01 spike is a
simulated LIF event. PSI/DLMn records are exploratory software route receipts,
not biological spikes. The zero-added-delay routing is a model assumption.
This result does not establish PSI/DLMn dynamics, physiological transmission,
muscle activation, flight, takeoff, escape, or behavior.
