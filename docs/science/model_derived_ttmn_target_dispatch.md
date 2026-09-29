# Phase 8O — model-derived TTMn output to pinned target dispatch

**Status:** `PASS` — the canonical Phase 8N model-derived TTMn output events
resolve to the unchanged Phase 8K target associations. This is target
association bookkeeping only; it is not a muscle response model.

## Pinned inputs and shared resolution

Phase 8O consumes the replayed Phase 8N artifact
`synthetic_ttmn_output_rule_artifact_v1`, ID
`1c8aeac685646dac16fbb66f163743b662a3cd9a0e8f9f7582210fd7b39b9ab3`
(config SHA-256 `43ddd7fba90235f7331c4c53ee774810956b9b55a9dc4c3ddc94bb4887283ea8`,
result SHA-256
`de54e2657560ae77a83b46174e029f7449008f968b0e0f4391cea8ec7a07c7b5`). Full
Phase 8N replay also validates its Phase 8B synthetic source. The output
events use `TTMN_THRESHOLD_CROSSING_V1` at the pinned reference configuration
and have provenance `EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT`; the
upstream fixture provenance remains `SYNTHETIC_MOTOR_INTERFACE_TEST`.

Targets come only from the replayed Phase 8K
`motor_neuron_muscle_target_contract_v1`, ID
`5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0`
(contract SHA-256
`9816a180acc845c202f70e374a4de951536296fed979c21c12d796792b8bac1f`).
Phase 8O reuses Phase 8L's pure identity-to-association resolver. Phase 8L's
public input remains restricted to `SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST`; its
artifact, config hash, result hash, and fixture semantics are unchanged.

Phase 8O has a distinct `model_derived_muscle_target_dispatch_v1` record
schema. This avoids placing model-derived ancestry into Phase 8L's
synthetic-fixture fields. Each record preserves its source Phase 8N event ID,
Phase 8N artifact/result/config identities, generator identity/config hash,
Phase 8B fixture/run identity, upstream synthetic provenance, target
association identity, and exact step/time. The complete originating Phase 8N
event is also retained in the result ledger.

## Reference results

| Phase 8N fixture | Model-derived events | Target dispatches | Event boundaries |
| --- | ---: | ---: | --- |
| `ZERO_EVENT_CONTROL` | 0 | 0 | — |
| `RIGHT_SINGLE_EVENT` | 1 | 1 | `800146`, step 10 / 1.0 ms |
| `LEFT_SINGLE_EVENT` | 1 | 1 | `804642`, step 10 / 1.0 ms |
| `BILATERAL_SIMULTANEOUS_EVENT` | 2 | 2 | `800146` and `804642`, step 10 / 1.0 ms |
| `RIGHT_REPEATED_EVENTS` | 2 | 2 | `800146`, steps 10 and 30 / 1.0 and 3.0 ms |
| `LEFT_REPEATED_EVENTS` | 2 | 2 | `804642`, steps 10 and 30 / 1.0 and 3.0 ms |

Across the six independent fixtures, all 8 events are dispatched exactly
once: 4 for `800146/R`, 4 for `804642/L`. Every target is the Phase 8K `TTM`
muscle class association, with its `HIGH` class/pathway mapping confidence,
qualified ipsilateral class inference, and unresolved exact peripheral
endpoint/fiber preserved. No DLM target is accepted. Dispatch step/time are
copied exactly from the Phase 8N event; this is bookkeeping, not an NMJ delay
assumption.

## Artifact and replay

The immutable artifact schema is
`model_derived_ttmn_target_dispatch_artifact_v1`:

- Artifact ID: `3bc011f9a8831f5291b6078d6132ef0dc6d6d7e87cc45ecfaa957ec80b8af360`
- Config SHA-256: `79624d65a8aba4885c66791b4f40fe4f31e050e4fc70e794ea475af2e3881261`
- Result SHA-256: `0d3826ffc4ef35246d48da9bbe586afc82b1cebb64beebbb1618e8f01f81fbcc`
- Size: 47,480 bytes

It is stored in the ignored path
`data/derived/malecns/looming_giant_fiber_v1/model_derived_ttmn_target_dispatch_v1/<artifact-id>`.
Offline commands are:

```sh
python -m neurofly.model_derived_ttmn_target_dispatch_cli generate
python -m neurofly.model_derived_ttmn_target_dispatch_cli inspect <artifact-path>
python -m neurofly.model_derived_ttmn_target_dispatch_cli replay <artifact-path>
```

Full replay reloads and fully replays Phase 8N and Phase 8B, replays Phase 8K,
extracts the existing events without applying the threshold rule, reruns only
target dispatch, and verifies config/result/artifact identities. No network or
randomness is used.

## Scientific boundary

Phase 8O does not generate a neural event. The Phase 8N input is an exploratory
model-derived TTMn output event, not a biologically observed or calibrated
action potential. The dispatch states only that this event resolves to the
pinned literature-supported TTM target class. It does not establish
neuromuscular transmission, muscle activation, contraction, force, or behavior.
There is no DLMn output generator, NMJ delay/gain, muscle state, or production
sensory source in this phase.
