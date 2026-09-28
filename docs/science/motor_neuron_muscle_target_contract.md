# Phase 8K — pinned motor-neuron to muscle target contract

**Decision: `MOTOR_NEURON_MUSCLE_TARGET_CONTRACT_PINNED`.** This is an
offline, no-dynamics identity/evidence contract. It associates the 2 TTMn and
10 DLMn identities from the pinned Phase 8E motor contract with literature-
supported muscle classes/groups. It adds no peripheral MaleCNS edge, output
event, muscle state, or behavior.

## Source identity and artifact

The neural source was reloaded and validated from
`motor_neural_pathway_contract_v1`:

| Source | Identity |
| --- | --- |
| Contract ID | `a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c` |
| Contract SHA-256 | `654af1bf91e2ae7226d454ba714a5eae1a9bba9b8bfc684b0069a8f1ffe0e068` |
| Dataset | `male-cns:v1.0` |
| Canonical query-response SHA-256 | `845c1c1ddc60183fd02f8ac2ceaac5e1a16cba34c803707fb974e7b52861e43e` |
| Annotation-source SHA-256 | `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2` |

The generated target contract is
`motor_neuron_muscle_target_contract_v1`, artifact ID
`5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0`.
Its `contract_sha256` is
`9816a180acc845c202f70e374a4de951536296fed979c21c12d796792b8bac1f`; its
`source_identity_sha256` is
`942749ad63e5d6f945022551cb9a996e663ecf5e76cfe77b5cf6e601064896cf`.
Artifact size is 26,974 bytes. It is stored in the ignored derived-data
directory:

```text
data/derived/malecns/looming_giant_fiber_v1/
  motor_neuron_muscle_target_contract_v1/<artifact-id>/
```

The contract contains 12 target-association records: 2 TTMn, 2 DLMn a,b,
and 8 DLMn c-f. All identities and sides are copied from the validated
source motor contract; the target records are sorted by body ID.

## Mapping records

| Motor-neuron body IDs | MaleCNS type; neural side | Literature-supported target | Muscle side | Granularity; confidence |
| --- | --- | --- | --- | --- |
| 800146; 804642 | TTMn; R; L | TTM class | R; L, explicitly qualified as literature-supported ipsilateral class inference | `MUSCLE_CLASS`; `HIGH` for class/pathway correspondence |
| 801295; 801970 | DLMn a,b; R; L | DLM a,b group | `null`; unresolved | `MUSCLE_GROUP`; `MODERATE` |
| 800718; 800890; 801895; 803013; 801998; 802544; 803048; 1050014552 | DLMn c-f; source sides retained per body | DLM c-f group | `null`; unresolved | `MUSCLE_GROUP`; `MODERATE` |

The TTM side association uses an explicit ipsilateral pathway rule supported
by the literature cited below. Its status says that this is an inference at
class/pathway level, not a body-specific peripheral tracing result. For DLM,
neural side never fills `muscle_target_side`: each record keeps it `null` and
lists the uncertainty. This is important for the historical MN5-like a,b
group, whose target is contralateral to its soma, while the exact mapping to
these MaleCNS bodies is unresolved. No exact fiber or peripheral endpoint is
assigned to any record.

Mapping confidence describes literature-to-MaleCNS identity correspondence.
It is not a probability, pathway strength, or efficacy. The contract retains
evidence references for each row and distinguishes `MALECNS_NEURAL_IDENTITY`
from `PRIMARY_LITERATURE_TARGET_EVIDENCE`. It records
`LITERATURE_SUPPORTED_MUSCLE_TARGET_ASSOCIATION` as a separate relation and
explicitly states `malecns_peripheral_muscle_edge_present: false`.

## Evidence references

The immutable evidence catalog carries bibliographic identity and scoped
claims; it does not copy full papers into the artifact.

| Evidence ID | Primary source | Use in this contract |
| --- | --- | --- |
| `king_wyman_1980` | [King & Wyman (1980), DOI 10.1007/BF01205017](https://doi.org/10.1007/BF01205017) | Giant-fiber pathway anatomy and the ipsilateral TTM motor-neuron branch, at pathway/class level. |
| `augustin_2017` | [Augustin et al. (2017), DOI 10.1371/journal.pbio.2001655](https://doi.org/10.1371/journal.pbio.2001655) | TTMn→TTM and DLM motor-neuron→DLM pathway classes; pathway-level NMJ description. |
| `coggshall_1978` | [Coggshall (1978), DOI 10.1002/cne.901770410](https://doi.org/10.1002/cne.901770410) | DLM motor-neuron innervation at group level; not an exact MaleCNS ID crosswalk. |
| `kuehn_duch_2013` | [Kuehn & Duch (2013), DOI 10.1111/ejn.12104](https://doi.org/10.1111/ejn.12104) | Historical MN5 dorsal DLM association and contralateral target context. |
| `hurkey_2023` | [Hürkey et al. (2023), DOI 10.1038/s41586-023-06099-0](https://doi.org/10.1038/s41586-023-06099-0) | DLM motor-neuron class organization and MN5 laterality context. |

No source here establishes a MaleCNS body-to-individual-fiber mapping,
body-specific motor-neuron output, synaptic efficacy, delay, activation,
contraction, or force. The target records contain no dynamic parameters.

## Schema and replay

The contract schema contains source identity/hash references, the mapping
policy and confidence vocabulary, bibliographic records, counts, and the 12
association records. It declares `NO_DYNAMICS`; there are no gain, delay,
time-constant, threshold, state, voltage, spike-conversion, calcium,
activation, contraction, force, or torque fields.

Offline generation, inspection, and full source replay use:

```bash
python -m neurofly.motor_neuron_muscle_contract_cli generate
python -m neurofly.motor_neuron_muscle_contract_cli inspect \
  data/derived/malecns/looming_giant_fiber_v1/motor_neuron_muscle_target_contract_v1/<artifact-id>
python -m neurofly.motor_neuron_muscle_contract_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/motor_neuron_muscle_target_contract_v1/<artifact-id>
```

Replay validates the pinned Phase 8E artifact, reselects the 12 motor-neuron
identities from it, rebuilds the literature mapping records and hashes, and
compares the complete contract. No live query or network is needed. Unknown
types, changed source identity, missing or extra motor bodies, confidence or
evidence mutation, invented laterality, and exact-fiber assignments fail
closed.

## Scientific boundary and next step

The source contract establishes MaleCNS neural identity. Primary literature
supports the target classes/groups. The mapping between them retains its
stated confidence and unresolved fields. The contract does not turn Phase 6C
TTMn state or Phase 8G DLMn route receipts into motor-neuron output events and
cannot drive a muscle model.

The next bounded step may test a **synthetic motor-neuron-output interface**
that resolves an explicitly synthetic output-event identity to one of these
contracted target classes/groups. It must remain a target-selection/receipt
test, not muscle activation or a conversion from the existing TTMn or DLMn
outputs.
