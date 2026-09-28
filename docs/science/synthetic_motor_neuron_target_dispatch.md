# Phase 8L — synthetic motor-neuron output to target dispatch

**Status:** `PASS` — deterministic synthetic interface dispatch validated.
This is a target-selection receipt test only. It does not turn a TTMn state or
DLMn routed path record into an output event, and it does not model muscle
activation.

## Pinned source and contracts

The runner replays the immutable Phase 8K
`motor_neuron_muscle_target_contract_v1` before constructing fixtures or
dispatching an event. Target contract ID:
`5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0`;
contract SHA-256:
`9816a180acc845c202f70e374a4de951536296fed979c21c12d796792b8bac1f`.
Its source remains the Phase 8E pinned MaleCNS motor contract. The dispatch
code selects target records by body identity from the replayed contract; it
contains no independent body-to-muscle lookup table.

The two explicit schemas are `synthetic_motor_neuron_output_event_v1` and
`muscle_target_dispatch_v1`. An input event is a synthetic test assumption
that one identified motor neuron emitted one abstract event at a stored
integer boundary. Its provenance is `SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST`.
Each output is an `EXPLORATORY_MUSCLE_TARGET_DISPATCH` receipt, not a muscle
event, spike, or activation. It copies the Phase 8K target association,
confidence, qualified/unresolved laterality, evidence references, and
unresolved fields without filling missing values.

## Fixture battery and results

The deterministic battery contains eight fixtures:

| Fixture | Synthetic outputs | Target dispatches |
| --- | ---: | ---: |
| `ZERO_EVENT_CONTROL` | 0 | 0 |
| `TTMN_RIGHT_SINGLE` | 1 | 1 |
| `TTMN_LEFT_SINGLE` | 1 | 1 |
| `DLMN_AB_RIGHT_SINGLE` | 1 | 1 |
| `DLMN_AB_LEFT_SINGLE` | 1 | 1 |
| `DLMN_CF_LEFT_SINGLE` | 1 | 1 |
| `DLMN_CF_RIGHT_SINGLE` | 1 | 1 |
| `ALL_12_SIMULTANEOUS` | 12 | 12 |

The representative c-f fixture uses the smallest body ID on each source side
from the pinned contract (`800718` L and `801998` R); all eight c-f identities
are exercised independently by the all-12 case. TTMn dispatch preserves the
contract's qualified ipsilateral class inference. DLMn a,b and c-f dispatches
remain group-level, with muscle side and individual fiber unresolved. Each
input produces exactly one target-association receipt. Event and receipt keep
the same step/time (step 10, 1.0 ms on the 0.1 ms fixture grid); this is
bookkeeping, not an NMJ delay statement.

The total across the battery is 18 origin events and 18 dispatch records.
There is no cross-fixture aggregation or background dispatch. No Phase 6C,
8G, 8I, or 7O output artifact is an input or causal parent. Such output
objects fail the fixture schema/identity check rather than being converted.

## Artifact and replay

The immutable artifact schema is
`synthetic_motor_neuron_target_dispatch_artifact_v1`:

- Artifact ID: `8e53c6bd224a82c9cbef2b51a82fc917fe993da73ff64cc4c894870dfc4abff8`
- Config SHA-256: `736371154db08e2f587b2c7f2484be6ce9c249b5098bd7ac2e7d8196c207edb0`
- Result SHA-256: `ac57f2c7385869a6954b4aac2578afb6857333d1ea47a75541b29811c5a21462`
- Size: 86,115 bytes

It is stored in the ignored derived-data path
`data/derived/malecns/looming_giant_fiber_v1/synthetic_motor_target_dispatch_v1/<artifact-id>`.
Offline generation, inspection, and full replay use:

```sh
python -m neurofly.synthetic_motor_target_dispatch_cli generate
python -m neurofly.synthetic_motor_target_dispatch_cli inspect <artifact-path>
python -m neurofly.synthetic_motor_target_dispatch_cli replay <artifact-path>
```

Replay verifies the Phase 8K artifact, rebuilds the fixed fixtures from its
12 associations, recomputes event and dispatch IDs, and compares canonical
config/result hashes and artifact identity. No network or random IDs are
used. Artifact tampering, identity/provenance/timing mutation, and altered
target fields fail closed.

## Scientific boundary

MaleCNS supplies the neural identities. The Phase 8K evidence contract
supplies qualified literature-supported target classes/groups. The Phase 8L
input is synthetic, and the output is a NeuroFly target-resolution receipt.
No motor-neuron output was inferred from current model state or path records.
There is no neuromuscular delay, gain, release, activation, contraction,
force, or behavior in this phase.

The next gate should assess what independent motor-neuron output and
neuromuscular evidence would be required before any model-derived
output-to-muscle interface is considered. This phase does not authorize that
interface or muscle dynamics.
