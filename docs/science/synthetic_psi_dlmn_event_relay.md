# Phase 8G — synthetic DNp01→PSI→DLMn routed-event ledger

**Status:** `PASS` — bounded synthetic event routing, deterministic artifact
and offline full replay validated. This phase adds event records only; it
does not add PSI/DLMn latent states or infer PSI/DLMn `SpikeEvent` objects.

## Pinned source and active topology

The runner loads and validates the committed
`motor_neural_pathway_contract_v1` artifact offline before routing any event.
Contract ID:
`a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c`;
query-response SHA-256:
`845c1c1ddc60183fd02f8ac2ceaac5e1a16cba34c803707fb974e7b52861e43e`.
The relay selects the four `dnp01_to_psi` and ten `psi_to_dlmn` edges from
that source contract. It rejects a changed contract identity, content hash,
edge-class inventory, or expected fan-out.

| Active edge class | Source → target | Sides | Structural count |
| --- | --- | --- | ---: |
| DNp01→PSI | 10001 → 802401 | R→L | 3 |
| DNp01→PSI | 10001 → 903327 | R→R | 2 |
| DNp01→PSI | 10010 → 802401 | L→L | 9 |
| DNp01→PSI | 10010 → 903327 | L→R | 2 |
| PSI→DLMn | 802401 → 801970 | L→L | 17 |
| PSI→DLMn | 802401 → 801998 | L→R | 40 |
| PSI→DLMn | 802401 → 802544 | L→R | 67 |
| PSI→DLMn | 802401 → 803048 | L→R | 35 |
| PSI→DLMn | 802401 → 1050014552 | L→R | 64 |
| PSI→DLMn | 903327 → 800718 | R→L | 68 |
| PSI→DLMn | 903327 → 800890 | R→L | 24 |
| PSI→DLMn | 903327 → 801295 | R→R | 26 |
| PSI→DLMn | 903327 → 801895 | R→L | 58 |
| PSI→DLMn | 903327 → 803013 | R→L | 50 |

The two supplemental reciprocal PSI↔PSI edges remain visible in the pinned
contract and are explicitly excluded by policy `psi_dlmn_event_relay_v1`.
The two DNp01→TTMn edges are also excluded from this runner; the Phase 6C
TTMn branch remains parallel and unchanged. No generic graph traversal is
used, so propagation stops after the PSI→DLMn layer.

## Fixture and event semantics

The relay reuses the six fixed Phase 8B fixtures and their validated
`SYNTHETIC_MOTOR_INTERFACE_TEST` inputs: zero, right single, left single,
bilateral simultaneous, right repeated, and left repeated. The timestep is
0.1 ms with 80 intervals. Single events occur at step 10 / 1.0 ms; repeated
events occur at steps 10 and 30 / 1.0 and 3.0 ms. Fixture source events
retain the original DNp01 body, side, graph node index, type, step, time,
fixture config hash and synthetic run ID.

Each valid source event produces one
`psi_routed_event_v1` record for each matching DNp01→PSI edge. Each PSI
receipt produces one `dlmn_routed_event_v1` record for each matching
PSI→DLMn edge. Both route layers copy the source event’s integer step and
time exactly under the declared `ZERO_ADDED_DELAY_EXPLORATORY_ASSUMPTION`.
That convention is a model assumption, not a biological instantaneous
transmission claim.

Every routed record is labelled
`EXPLORATORY_ROUTED_MOTOR_EVENT`, carries the origin source kind and event
identity, and includes the contract ID and route edge identity. DLMn records
retain both edge IDs and their parent PSI receipt ID. Deterministic record
IDs include the schema, synthetic run, origin event, route path, target,
step/time and contract ID. Coincident records from different DNp01 origins
remain separate.

Structural counts are copied as source metadata only. One traversed route
produces one receipt regardless of its count. There is no amplitude, gain,
state variable, threshold, decay, stochastic release, or count-based event
multiplicity. PSI and DLMn receipts are not biological spikes.

## Reference results

| Fixture | Source events | PSI receipts | DLMn path receipts | PSI targets | DLMn targets |
| --- | ---: | ---: | ---: | --- | --- |
| `ZERO_EVENT_CONTROL` | 0 | 0 | 0 | — | — |
| `RIGHT_SINGLE_EVENT` | 1 | 2 | 10 | 802401, 903327 | all 10 contracted DLMn |
| `LEFT_SINGLE_EVENT` | 1 | 2 | 10 | 802401, 903327 | all 10 contracted DLMn |
| `BILATERAL_SIMULTANEOUS_EVENT` | 2 | 4 | 20 | 802401, 903327 | all 10 contracted DLMn |
| `RIGHT_REPEATED_EVENTS` | 2 | 4 | 20 | 802401, 903327 | all 10 contracted DLMn |
| `LEFT_REPEATED_EVENTS` | 2 | 4 | 20 | 802401, 903327 | all 10 contracted DLMn |

For bilateral simultaneous input, each DLMn target has two same-boundary
records with distinct originating event IDs. The counts 10 and 20 describe
verified graph paths, not DLMn firing. Cross-side routes are preserved; no
laterality symmetry rule is imposed.

## Artifact and replay

The generated artifact uses schema
`synthetic_psi_dlmn_event_relay_artifact_v1` and is stored under the ignored
derived-data root:

`data/derived/malecns/looming_giant_fiber_v1/synthetic_psi_dlmn_event_relay_v1/1da8963e9097c570d67a2683f71744c2dee8c59662faa253cdc56ad32ee5e5b3`

- Artifact ID: `1da8963e9097c570d67a2683f71744c2dee8c59662faa253cdc56ad32ee5e5b3`
- Config SHA-256: `60ecb2e48c2ee5f6381999a7a8474076120e98ad2f185ef78b53b7da6791c16e`
- Result SHA-256: `254fe04d09c1ba821892cedc2538e12c309b47a6e47d1e07030414bb51846dfd`
- Artifact size: 159,177 bytes

The artifact references the motor contract identity and hashes rather than
copying its source snapshot. Full replay loads and revalidates that pinned
contract, rebuilds the Phase 8B fixture battery, reruns both bounded route
layers, then compares canonical config/result hashes and artifact identity.
No live neuPrint access is needed.

Offline commands:

```sh
python -m neurofly.psi_dlmn_event_relay_cli generate
python -m neurofly.psi_dlmn_event_relay_cli inspect \
  data/derived/malecns/looming_giant_fiber_v1/synthetic_psi_dlmn_event_relay_v1/1da8963e9097c570d67a2683f71744c2dee8c59662faa253cdc56ad32ee5e5b3
python -m neurofly.psi_dlmn_event_relay_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/synthetic_psi_dlmn_event_relay_v1/1da8963e9097c570d67a2683f71744c2dee8c59662faa253cdc56ad32ee5e5b3
```

## Validation and limits

Focused tests cover the exact 14-route policy, zero/unilateral/bilateral and
repeated fan-out, coincident origin preservation, cross-side identities,
same-boundary timing, structural-count independence, PSI↔PSI exclusion,
contract/config/result tampering, deterministic artifact identity and the
offline CLI. Existing Phase 6C, 8B, 8C and 8E regressions remain in the
repository suite.

MaleCNS provides structural identities and chemical route records. The
synthetic DNp01 events are test inputs. The PSI/DLMn path records are a
deterministic NeuroFly routing abstraction; they do not establish pairwise
physiological efficacy, electrical transmission, biological PSI/DLMn spikes,
muscle activation, force, behavior, or sensory-derived motor output.

