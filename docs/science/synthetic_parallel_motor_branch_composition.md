# Phase 8I — synthetic parallel DNp01 motor-branch composition

Phase 8I composes the existing synthetic DNp01 event fixture with two
independently implemented motor branches:

```text
SYNTHETIC_MOTOR_INTERFACE_TEST DNp01 event
├── Phase 6C → identity-routed TTMn exploratory state
└── Phase 8G → PSI routed-event records → DLMn path records
```

This is an offline software-composition experiment. It adds no neural
parameters or equations, PSI/DLMn latent state, muscle model, body mechanics,
or behavior. The two branch outputs retain different meanings and are not
summed, normalized, ranked, or converted to a motor command.

## Shared source and child branches

The composer creates the six predeclared Phase 8B immutable fixture objects
once and passes that same tuple into both existing child executors. Both
children verify that the supplied fixture serialization exactly matches the
canonical battery. The Phase 6C mapper/integrator and Phase 8G two-layer relay
remain the only implementations of their respective branch semantics.

The child identities remain unchanged:

| Child | Artifact ID | Config SHA-256 | Result SHA-256 |
| --- | --- | --- | --- |
| Phase 8B TTMn | `4321adeee0412a79632ce4e008a1b8eaad22ee167f97f4a98521a9e71d9ef936` | `13b2cc3c33af1c3fba8d918da6d33bd8225a077a8cc0bc7fd383f63a595a1863` | `a3c9cdc02ec02211059411ab5819c1bba318e2b58c866663162ae85a852670d5` |
| Phase 8G PSI/DLMn | `1da8963e9097c570d67a2683f71744c2dee8c59662faa253cdc56ad32ee5e5b3` | `60ecb2e48c2ee5f6381999a7a8474076120e98ad2f185ef78b53b7da6791c16e` | `254fe04d09c1ba821892cedc2538e12c309b47a6e47d1e07030414bb51846dfd` |

Phase 8I references these child artifact/config/result identities. It embeds
only the per-fixture branch outputs needed for a self-contained parallel
result, not duplicate child manifests or source contracts. The originating
event identity is the fixture's `(synthetic_run_id, event_id)` pair; the
`event_id` string alone is intentionally not treated as globally unique
across separate fixtures.

## Results and accounting

All six Phase 8B fixtures are retained. Per fixture, one DNp01 origin maps to
one Phase 6C TTMn input, two PSI receipts, and ten DLMn path receipts. These
are software-path accounting counts, not biological pathway strengths.
Summed across the separate fixture battery, the artifact records 8 origin
events, 8 TTMn inputs, 16 PSI receipts, and 80 DLMn path records.

| Fixture | Origins | TTMn inputs | PSI receipts | DLMn path receipts |
| --- | ---: | ---: | ---: | ---: |
| `ZERO_EVENT_CONTROL` | 0 | 0 | 0 | 0 |
| `RIGHT_SINGLE_EVENT` | 1 | 1 | 2 | 10 |
| `LEFT_SINGLE_EVENT` | 1 | 1 | 2 | 10 |
| `BILATERAL_SIMULTANEOUS_EVENT` | 2 | 2 | 4 | 20 |
| `RIGHT_REPEATED_EVENTS` | 2 | 2 | 4 | 20 |
| `LEFT_REPEATED_EVENTS` | 2 | 2 | 4 | 20 |

The unilateral TTMn child outputs preserve Phase 6C's existing identities:
DNp01 `10001 R` routes to TTMn `800146 R`; DNp01 `10010 L` routes to TTMn
`804642 L`. The reference single-event peak is 0.25 dimensionless state.
Phase 8G fan-out is loaded from the pinned
`motor_neural_pathway_contract_v1` ID
`a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c` and uses
four DNp01→PSI plus ten PSI→DLMn routes. Reciprocal PSI→PSI evidence remains
excluded by the Phase 8G active-edge policy. Cross-side routes are preserved.

Every composite fixture stores a common-origin ledger. It links each exact
fixture origin to its matching Phase 6C input by body, node, step, and time;
then records the Phase 8G PSI and DLMn event IDs associated with that same
origin. Bilateral events at the same boundary remain distinct by origin.
TTMn remains a continuous dimensionless exploratory neural-state trajectory;
PSI/DLMn remain discrete exploratory route/path records.

The unchanged Phase 6C model uses `tau_motor_ms = 10` and
`event_gain = 0.25`, classified as model assumptions. Its integer-step update
and same-boundary event convention are unchanged. Phase 8G retains zero-added-
delay same-boundary routing, no latent state, and no recursive traversal.
Structural edge counts remain source metadata; they do not scale state or
event multiplicity. No new numerical parameter is introduced.

## Artifact and replay

The content-addressed artifact uses schema
`synthetic_parallel_motor_branch_artifact_v1`:

- artifact ID: `f4225f3f24bcf3a3ed27d5c0d313700426e788d6af232b2c57b9d77e3ae63bbf`
- config SHA-256: `918511790f726ca7e1f64e09bad2f277e87241a131cc2f48ec6dbc421bdc3e4b`
- result SHA-256: `d958c2dec0f98b405aa7772f6cb8c2d4130242c52e7e11abf135af631b9883e9`
- size: 188,878 bytes
- generated path: `data/derived/malecns/looming_giant_fiber_v1/synthetic_parallel_motor_branch_v1/<artifact-id>/`

The generated artifact is ignored derived data. Full offline replay reloads the
source CircuitContract and pinned motor contract, reconstructs one shared
fixture tuple, runs each unchanged child branch, checks common-origin
accounting and hashes, and reproduces the artifact identity. It does not load
Phase 7O as a causal parent.

```bash
python -m neurofly.synthetic_parallel_motor_branch_cli generate
python -m neurofly.synthetic_parallel_motor_branch_cli inspect \
  data/derived/malecns/looming_giant_fiber_v1/synthetic_parallel_motor_branch_v1/f4225f3f24bcf3a3ed27d5c0d313700426e788d6af232b2c57b9d77e3ae63bbf
python -m neurofly.synthetic_parallel_motor_branch_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/synthetic_parallel_motor_branch_v1/f4225f3f24bcf3a3ed27d5c0d313700426e788d6af232b2c57b9d77e3ae63bbf
```

As a separate production regression, canonical Phase 7O `reference_bilateral`
was replayed through Phase 8C and 8H. It still contains zero genuine DNp01
events and yields zero TTMn activity, PSI receipts, and DLMn path records.
That production result is not a parent or input to this synthetic experiment.

## Scientific boundary

MaleCNS provides body identity, source topology, and structural route evidence.
The Phase 6C TTMn equation and Phase 8G same-boundary event relay are NeuroFly
model assumptions. Phase 8I verifies software composition and deterministic
provenance only. Synthetic DNp01 events are test fixtures; they are not
sensory-derived events or observed Giant Fiber spikes. TTMn output is not
muscle activation, and PSI/DLMn path records are not biological spikes,
behavior, or motor commands.

Decision: `PARALLEL_MOTOR_BRANCH_COMPOSITION_VALIDATED`.
