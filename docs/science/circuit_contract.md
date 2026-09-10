# Model-neutral circuit contract

Phase 1B defines the stable offline boundary between the derived MaleCNS
snapshot and any future NeuroFly simulator. `CircuitContract` reuses the Phase
1A `NeuronRecord`, `ConnectionRecord`, and `CandidateDefinition`; it does not
duplicate biological records or expose neuPrint/pandas/JSONL details to future
consumers.

## Scientific layers

The contract keeps three layers distinct:

1. **MaleCNS-derived facts:** biological body IDs and annotations, chemical
   `ConnectsTo` edges, structural contact counts, and dataset provenance.
2. **NeuroFly experimental decisions:** the
   `looming_giant_fiber_v1` selection, LC4/LPLC2 as the selected sensory-side
   boundary, and DNp01 as the descending/readout boundary. These boundary roles
   are not fields supplied by MaleCNS and assign no stimulus or action.
3. **Future model assumptions:** equations, signs, thresholds, time constants,
   delays, encoding, scaling, plasticity, and behavioural mappings. None are
   present in this phase.

## Integrity, provenance, and content

These are independent concepts. Provenance records where and when acquisition
occurred. Integrity verification recomputes SHA-256 hashes and checks that local
files and record counts match the manifest. Biological validation then checks
the records, endpoints, type annotations, and pinned circuit invariants. A
matching checksum establishes local file integrity; it is not evidence that a
biological interpretation is true.

Loading accepts only candidate `looming_giant_fiber_v1` version 1 from
`male-cns:v1.0`. It requires 313 unique neurons and all 20,607 unique
body-level chemical edges, with total structural weight 79,112. Source and
target types must agree with their neuron records. Same-type, reverse-direction,
DNp01-originating, and genuine self-edges are permitted and preserved. The
current snapshot happens to contain no self-edges; its two DNp01-to-DNp01 edges
connect the two distinct bodies.

`structural_weight` comes from neuPrint `ConnectsTo.weight`. It remains a
structural connectomic contact-count/connectivity value—not a signed weight,
conductance, firing probability, physiological efficacy, or simulation
parameter. Predicted and consensus neurotransmitter annotations remain separate
biological metadata and are not converted into excitatory/inhibitory signs.
Missing optional annotations remain `None`.

## Deterministic access

Neurons are sorted by `body_id`, producing a stable contiguous node index from
0 through 312. `body_id` remains the biological identity; `node_index` is only
an implementation convenience. The immutable contract exposes both directions
of the mapping and constant-time neuron lookup by body ID. It does not allocate
simulation state or require NumPy.

Run the complete offline gate with:

```bash
python -m neurofly.malecns inspect-snapshot
```

The command does not contact neuPrint or inspect credentials. It prints only
descriptive neuron counts, chemical-edge counts, and structural-weight sums.

The candidate covers chemical `ConnectsTo` structure only. It is not a complete
visual or escape circuit and does not represent the known electrical/gap-junction
contributions in downstream Giant Fiber circuitry involving structures such as
TTMn and PSI. No neural dynamics, sensory encoding, physiological coupling, or
behaviour is implemented.
