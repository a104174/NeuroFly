# Phase 8Q — TTMn-only neuromuscular-input receipt ledger

**Status:** `PASS` — `TTM_NMJ_INPUT_RECEIPT_INTERFACE_VALIDATED`. Phase 8Q
adds a discrete, provenance-explicit bookkeeping boundary downstream of the
canonical Phase 8O dispatch. It adds no physiological NMJ mechanism or muscle
state.

## Boundary and source authority

Phase 8Q consumes the persisted
`model_derived_muscle_target_dispatch_v1` records in Phase 8O artifact
`3bc011f9a8831f5291b6078d6132ef0dc6d6d7e87cc45ecfaa957ec80b8af360`
(config SHA-256
`79624d65a8aba4885c66791b4f40fe4f31e050e4fc70e794ea475af2e3881261`, result
SHA-256
`0d3826ffc4ef35246d48da9bbe586afc82b1cebb64beebbb1618e8f01f81fbcc`). Full
offline replay verifies Phase 8O, its Phase 8N output-event source, and the
Phase 8K target contract before receipts are constructed. Phase 8Q does not
recompute TTMn state, detect threshold crossings, generate output events, or
resolve a second body-to-target table.

The only accepted branch is TTMn body `800146`/R or `804642`/L and its exact
Phase 8K `TTM` muscle-class association. The association retains `HIGH`
class/pathway mapping confidence and the qualified literature-supported
ipsilateral class-side inference. Exact muscle fiber and peripheral endpoint
remain unresolved. These are literature-supported target associations, not
MaleCNS peripheral synapse edges.

## Receipt semantics

`ttm_neuromuscular_input_receipt_v1` with provenance
`EXPLORATORY_NEUROMUSCULAR_INPUT` means only:

> One validated exploratory model-derived TTMn output event was handed to its
> supported TTM neuromuscular target interface.

The receipt carries a deterministic identity derived from its Phase 8O parent
dispatch, target-association identity, originating Phase 8N output-event ID,
boundary, and source artifact. It retains the body/type/side, target contract
and association semantics, fixture/run ancestry, generator and source hashes,
and exact `step`/`time_ms`. It has no release-success or response field.

The complete ancestry is preserved:

`SYNTHETIC_MOTOR_INTERFACE_TEST`
→ Phase 6C dimensionless exploratory TTMn state
→ `EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT`
→ `EXPLORATORY_MUSCLE_TARGET_DISPATCH`
→ `EXPLORATORY_NEUROMUSCULAR_INPUT`.

The Phase 8L `SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST` path is separate and is not
accepted as Phase 8Q input. Production Phase 7O sensory data are not part of
this artifact's causal chain.

## Canonical battery and artifact

Phase 8Q applies one receipt per valid Phase 8O dispatch. It preserves
coincident bilateral events as distinct parent-linked records and retains the
two repeated events at steps 10 and 30 independently.

| Phase 8O fixture | TTMn dispatches | Phase 8Q receipts |
| --- | ---: | ---: |
| `ZERO_EVENT_CONTROL` | 0 | 0 |
| `RIGHT_SINGLE_EVENT` | 1 | 1 |
| `LEFT_SINGLE_EVENT` | 1 | 1 |
| `BILATERAL_SIMULTANEOUS_EVENT` | 2 | 2 |
| `RIGHT_REPEATED_EVENTS` | 2 | 2 |
| `LEFT_REPEATED_EVENTS` | 2 | 2 |
| **Total** | **8** | **8** |

There are four records for body `800146` and four for `804642` across these
independent synthetic fixtures. This is fixture accounting, not a firing rate,
NMJ reliability, or evidence of repeated biological responses.

The content-addressed artifact uses schema
`ttm_neuromuscular_input_receipt_artifact_v1`, ID
`e04803f60304f58d0e6d27fdea5d15debb60358b46721caac09f10165c6df9c4`, config
SHA-256
`826e326e98dda35113f776867561a9bb777f52035cacba104d49eacccd55a8f3`, result
SHA-256
`a243de98a5f67c4a7dd77313524b979f3165812f53f0c4f2b7c3c52288a667dc`, and
size 38,660 bytes. It is generated under the ignored `data/derived/` tree.
The CLI supports offline `generate`, `inspect`, and full `replay` operations:

```sh
python -m neurofly.ttm_neuromuscular_input_receipt_cli generate
python -m neurofly.ttm_neuromuscular_input_receipt_cli inspect <artifact-path>
python -m neurofly.ttm_neuromuscular_input_receipt_cli replay <artifact-path>
```

## Scientific boundary

Receipt time copies the Phase 8O dispatch boundary exactly; there is no NMJ
delay parameter or assertion of instantaneous biological transmission. One
dispatch creates one attempted software handoff record, not a release event.
The ledger does not imply transmitter release, junction potential, muscle
electrical response, activation, or equal responses on repetition. There is no
vesicle/depression/recovery model, muscle voltage or activation state, gain,
amplitude, calcium, contraction, force, mechanics, or behavior. Structural
counts and target confidence do not affect receipt existence, multiplicity,
timing, or magnitude. The physiological limitations and evidence basis remain
those audited in the [Phase 8P assessment](ttmn_ttm_neuromuscular_readiness.md).
