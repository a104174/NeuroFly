# Phase 8W — TTM-class abstract electrical-input contract

**Status:** `PASS` — `ABSTRACT_TTM_ELECTRICAL_INPUT_CONTRACT_PINNED`.

Phase 8W adds an admission-only interface downstream of the persisted Phase
8Q receipt ledger. `ttm_abstract_electrical_input_event_v1` means: one validated
TTM neuromuscular-input receipt has been admitted as one abstract input token
for a future electrical model. This grants no implicit physical input
transformation and executes no electrical state. It implements the bounded
direction recommended by the [Phase 8V assessment](ttm_neuromuscular_input_semantics.md).

## Repository and source gate

Work began on clean `main` at
`dbf53e2c9f9981e561ed487aa3a92933f4117f5f`, matching `origin/main`.
Phase 8V, 8U and 8Q were committed. Before edits, canonical Phase 8Q, 8U and
8S artifacts replayed unchanged. Phase 8Q replay recursively verifies its
Phase 8O/8N ancestry and Phase 8K target association. No historical code or
artifact is modified.

The only input authority is the persisted
`ttm_neuromuscular_input_receipt_artifact_v1`, ID
`e04803f60304f58d0e6d27fdea5d15debb60358b46721caac09f10165c6df9c4`;
config hash
`826e326e98dda35113f776867561a9bb777f52035cacba104d49eacccd55a8f3`;
result hash
`a243de98a5f67c4a7dd77313524b979f3165812f53f0c4f2b7c3c52288a667dc`.
Admission uses its fully replayed exact receipt content. It does not recreate
receipts from Phase 8O, detect thresholds, or resolve a second target table.

## Token envelope and semantics

The versioned contract is `ttm_abstract_electrical_input_contract_v1`, with
event schema `ttm_abstract_electrical_input_event_v1`. Each event retains:

- Deterministic event ID, parent receipt ID and Phase 8Q artifact reference.
- Origin output-event identity, fixture/run identity and provenance chain.
- Motor-neuron body/type/neural side and pinned target-association/contract IDs.
- TTM class, target granularity, qualified side status/basis and class-level
  mapping confidence copied from the validated parent.
- Exact integer boundary and model time; categorical input/timing/success and
  model-family-neutral semantics; explicit scientific exclusions.

Exact source equality rejects changed or additional fields before admission,
including fabricated fibers/endpoints or magnitude fields. Canonical JSON
comparison distinguishes changed numeric representations from exact persisted
source content. Duplicate/conflicting parent IDs fail closed. Public admission
can select a validated subset, including empty input, but always emits in
canonical source order; reference artifact generation covers all six fixtures.
The full contract validator reconstructs the expected admission and rejects
semantic drift even if a caller recalculates IDs and hashes.

`input_semantics_kind = ABSTRACT_ELECTRICAL_INPUT_TOKEN` grants admission only.
It does not mean current, conductance, release, depolarization, junction
potential, activation, contraction or force. No amplitude, unit-bearing
electrical magnitude, weight, waveform, gain or default `1.0` is present.
One record is one categorical token, not one quantum or physical unit.

`success_semantics = ONE_RECEIPT_ONE_INPUT_WITHOUT_RELEASE_CLAIM` and
`biological_transmission_success = UNREPRESENTED_NOT_ASSERTED` do not assert
either successful transmission or failure. Target confidence affects neither
existence nor multiplicity. Structural counts have no role.

## Reference accounting and timing

| Persisted Phase 8Q fixture | Receipts | Tokens | Body / stored boundaries |
| --- | ---: | ---: | --- |
| `ZERO_EVENT_CONTROL` | 0 | 0 | No background token. |
| `RIGHT_SINGLE_EVENT` | 1 | 1 | 800146/R; step 10, 1.0 ms. |
| `LEFT_SINGLE_EVENT` | 1 | 1 | 804642/L; step 10, 1.0 ms. |
| `BILATERAL_SIMULTANEOUS_EVENT` | 2 | 2 | Both distinct bodies at step 10, 1.0 ms. |
| `RIGHT_REPEATED_EVENTS` | 2 | 2 | 800146/R; steps 10 and 30, 1.0 and 3.0 ms. |
| `LEFT_REPEATED_EVENTS` | 2 | 2 | 804642/L; steps 10 and 30, 1.0 and 3.0 ms. |
| Total across independent fixtures | 8 | 8 | Four per TTMn body; fixture accounting only. |

Every token has one unique parent; every canonical parent has one token.
Bilateral records are not deduplicated by class/time. Repeated records are not
coalesced and undergo no history, depression, saturation or refractory rule.
Multiple attempted inputs imply no equal biological responses.

Token step/time equals the receipt boundary exactly.
`added_delay_semantics = ZERO_ADDED_MODEL_DELAY_ASSUMPTION` is an explicit
software scheduling assumption, **not zero biological NMJ delay**. There is no
numeric delay field, interpolation or Kadas-latency offset.

## TTM class, G1 exclusion and future transformation

Target semantics are copied, not inferred from body/side. Phase 8K's two TTM
class associations retain their qualified ipsilateral side status and `HIGH`
class/pathway confidence. This is not exact MaleCNS peripheral tracing or
side-specific electrical physiology. Exact fiber/peripheral endpoint remain
unresolved in the parent; no receiving-fiber or endpoint field is added to the
token. G1 destinations and DLM targets are rejected.

Phase 8V's `G1_PROXY_REQUIRES_EXPLICIT_MAPPING_CONTRACT` still holds. No G1
proxy is adopted by a TTM-class token. A future G1 model needs a separately
justified, identified scope mapping before consumption.

`NEUTRAL_REQUIRES_SEPARATE_TRANSFORMATION` selects no kernel, passive membrane,
conductance or quantal family. A future model-specific input transformation
must explicitly map tokens to its quantities before electrical-model execution.
Its magnitude, waveform, membrane coupling, lag and history assumptions belong
in future electrical-model/transformation configuration—not Phase 8Q, 8W,
8S evidence or 8U mappings. The same token can later be consumed under different
identified transformations without changing its causal identity. None of
those transformations is implemented here.

## Provenance and remaining blockers

Derived provenance is `EXPLORATORY_ABSTRACT_ELECTRICAL_INPUT`, distinct from
parent `EXPLORATORY_NEUROMUSCULAR_INPUT`. Preserved ancestry is:

`SYNTHETIC_MOTOR_INTERFACE_TEST` → Phase 6C dimensionless TTMn state →
`EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT` →
`EXPLORATORY_MUSCLE_TARGET_DISPATCH` → `EXPLORATORY_NEUROMUSCULAR_INPUT` →
`EXPLORATORY_ABSTRACT_ELECTRICAL_INPUT`.

The uncalibrated Phase 8N event remains exploratory. Phase 8L synthetic-output
dispatches, production sensory events and arbitrary records are not substituted
for persisted Phase 8Q receipts. No production artifact or adapter is added.

Phase 8W establishes **input admission only**, not physical input semantics.
Phase 8U is unchanged and remains zero-ready. `INPUT_SEMANTICS_UNDEFINED`
still applies to model-specific electrical response mapping;
`MODEL_QUANTITY_ABSENT`, missing operators, release/protocol/history/vesicle
blockers and the Kadas system-boundary mismatch remain. No observation
comparison, tolerance, calibration or model-family selection is introduced.

Persisted exclusions include no release claim, physical amplitude, current,
conductance, quantal semantics, G1 mapping, exact endpoint, muscle state,
model-family selection, observation comparison or biological zero-delay claim.

## Artifact, identity and offline replay

Artifact schema: `ttm_abstract_electrical_input_artifact_v1`.
Canonical contract/artifact ID:
`1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa`.
Config hash:
`30f3eccd8d30b36895472abba80351fc2750f244c7685b2d8626314499f1bc81`.
Result hash:
`f61f963bc889c4180882479bffeb8856e514d0cbf954749e4f4747801f3479db`.
The two-file artifact (`input_contract.json`, `manifest.json`) is 23,513 bytes
and remains ignored under `data/derived/malecns/looming_giant_fiber_v1/`.
It stores compact source references, ordered parent IDs and tokens rather than
embedding full historical artifacts.

Event identity hashes its semantic envelope, including parent, source,
boundary and semantic policy. Config/result hashes cover policies/source
references and the ordered fixture ledger; the contract/artifact ID covers
those hashes and version identities. Export refuses existing destinations and
validates staged canonical bytes. Generation replays an existing artifact
instead of overwriting it. Load/replay reject extra files, manifest drift and
rehashed semantic tampering by exact source-derived reconstruction.

```sh
python -m neurofly.ttm_abstract_electrical_input_cli generate
python -m neurofly.ttm_abstract_electrical_input_cli inspect <artifact>
python -m neurofly.ttm_abstract_electrical_input_cli replay <artifact>
```

All commands accept an explicit `--source-receipt-artifact` (pinned Phase 8Q
default). There are no physical parameter or model options. Inspect displays
the token/parent IDs, target/body/boundary, ancestry and semantic exclusions.
Normal generation and replay use no network, source papers, randomness or
identity-changing timestamps.

Focused tests cover counts/identity/order, exact timing and qualified targets,
duplicates, wrong kinds/provenance, DLM/G1 rejection, no physical fields,
rehashed semantic tampering, source/manifest mutation, offline byte-equivalent
replay, pinned hashes and source receipt/event-ID snapshots, and Phase 8U/8S
immutability. Historical production adapters remain regression-only.

## Scientific boundary and exactly one next phase

Phase 8W provides replayable abstract admission only. It implements no
electrical dynamics, release model, observation operator, comparison, fitting,
force, mechanics or behavior. Upstream production remains untouched.

Exactly one bounded Phase 8X is recommended: a **read-only TTM-class-to-G1
proxy-mapping readiness assessment**. Determine the explicit scope,
compartment/location and assumption metadata required before a TTM-class token
could be consumed by a future G1 proxy. Do not implement a proxy, physical
transformation, electrical dynamics or comparisons in that assessment.

## Quality gates

Focused Phase 8W tests: 56 passed. Full `python -m pytest`: 630 passed,
one deselected, two existing dependency deprecation warnings. Ruff check and
format check, `git diff --check`, and frontend tests (38), lint, typecheck and
build passed. The build-generated frontend type-reference change was restored;
no frontend source change remains. Canonical Phase 8Q/8U/8S and Phase 8W
offline replays passed; source receipt IDs and hashes are snapshot-protected.
No historical artifact migration, commit or push occurred.
