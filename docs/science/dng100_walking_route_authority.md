# DNg100 walking-route structural authority v1

## Decision and scope

`DNG100_ROUTE_AUTHORITY_PARTIAL` for experiment
`DNG100_WALKING_ROUTE_AUTHORITY_V1`. Both source identities and real directed
edges are verified. Resolved direct and one-interneuron routes exist bilaterally;
other short paths fail the declared intermediate classification, identity or
synapse-ROI requirements and remain `CLASSIFICATION_UNRESOLVED`.

This is structural authority, not a walking controller. No neural dynamics,
synaptic sign, functional gain, conduction delay, rhythm, muscle force, body
feedback or propulsion is computed. Existing canonical scenarios, kernels,
Planar Steering SHADOW_ONLY, API and frontend remain unchanged.

The earlier [propulsion feasibility assessment](locomotion_propulsion_feasibility.md)
distinguishes the DNg100/BDN2 literature hypothesis from exact MaleCNS evidence.
[Sapkal et al., Nature (2024)](https://doi.org/10.1038/s41586-024-07854-7)
and [Pugliese et al., revised bioRxiv preprint](https://doi.org/10.1101/2025.09.12.675944)
provide biological/model context, not authority to import another dataset's IDs
or a functional actuation mapping. No cross-dataset identity is substituted here.

## Successful read-only source preflight

The repository selector is `male-cns:v1.0`, accessed at
`https://neuprint.janelia.org` through the existing authenticated
`neuprint-python==0.6.3` client. Native Meta represents this as
`dataset=male-cns`, `tag=v1.0`, UUID
`4b2087c0fbe046bfaf0d60bc970e3e5d`. It was stable across the acquisition's
initial and final metadata reads. Recorded mutation ID is `1006591300`;
`lastDatabaseEdit` is
`2026-03-28 11:56:30.222612573-04:00 / 2026-06-08T01:31:39-04:00 (segment property update)`.

The [official MaleCNS download page](https://male-cns.janelia.org/download/)
documents the API and versioned annotation/connectivity sources. The annotation
file is `body-annotations-male-cns-v1.0-minconf-0.5.feather`, 14,483,314 bytes,
retrieved from the official URL already pinned by `motor_neural_contract.py`.
Its SHA-256 remains:

`2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`.

The pinned existing GF/motor authority does not contain the DNg100 route graph.
No complete connectivity table was available locally. Instead of downloading
the full connectome, two bounded read-only queries captured directed native
`Neuron-[:ConnectsTo]->Neuron` aggregates. Each response preserves the query,
columns, ordered rows, native weight and serialized ROI counts. These are
neuron-to-neuron aggregates, not individual synapse locations/confidences.

Native confidence metadata is recorded: `postHighAccuracyThreshold=0.5`,
`postHPThreshold=0.699999988079071`, `preHPThreshold=0`. The extractor uses
server-standard `ConnectsTo.weight` without an additional per-synapse filter.
The metadata thresholds are not invented edge confidences; weight and ROI counts
are preserved independently. Neurotransmitter predictions are not used.

## Policy declared before candidate extraction

[dng100_walking_route_policy.json](dng100_walking_route_policy.json) is immutable
under policy hash
`432bab639860f7778339871d203e9e4e26bdd576956ae54631e55b11a90d9ee5`.
Changing this policy requires a separately versioned selection, not an override
after inspecting outcomes.

* Source identity: `10045/DNg100_L/L` and `10056/DNg100_R/R`, both
  `superclass=descending_neuron`. Source labels are Traced / Prelim Roughly traced;
  these labels are retained and do not certify physiological function.
* Front-leg motor authority: exact annotation conjunction
  `superclass=vnc_motor`, `subclass=fl`, `somaNeuromere=T1`. It selects 135 bodies;
  motor names are supporting annotations, not a substring-based classifier.
  Wing/neck subclasses are excluded from this motor target set.
* Structural premotor candidate: annotated `vnc_intrinsic` intermediate with an
  actual directed edge to an annotated front-leg motor. No proximity criterion.
* Resolved route: all node types and L/R soma sides available, above intermediate
  requirement when applicable, and positive postsynaptic count in at least one
  of `LegNp(T1)(L)` or `LegNp(T1)(R)` on the final edge. These primary ROIs exist
  in the source metadata. Soma side does not determine axonal laterality.
* Paths: direct or exactly one intermediate (one/two edges). No repeated nodes;
  no longer-path, recurrence or individual-synapse search.
* Primary threshold: at least one native synapse per edge. Sensitivity thresholds
  5 and 10 were also declared; they do not replace the primary result.
* Retain all tracing labels, all queried edges and unresolved candidates.
  Candidate order is lexicographic body IDs, **not** functional ranking.

The first query captures all outgoing edges from the source pair (3,445 rows).
The second captures their neighbors' edges into all 135 motor targets (8,489
rows). Fifty-four edges occur in both queries; both row references are retained.
The merged bounded graph has 11,880 edges and 3,234 relevant neuron records.
The full annotation file remains recoverable; absence in this bounded Neuron
graph does not establish absence among all segments, synapses or longer paths.

## Results and asymmetric evidence

| Minimum count on each edge | Left direct resolved | Left indirect resolved | Left unresolved | Right direct resolved | Right indirect resolved | Right unresolved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 (primary) | 22 | 2,470 | 1,265 | 32 | 3,927 | 1,626 |
| 5 (sensitivity) | 10 | 430 | 166 | 12 | 606 | 225 |
| 10 (sensitivity) | 6 | 174 | 60 | 6 | 256 | 70 |

There are 9,342 candidate paths: 6,451 resolved and 2,891 unresolved. Resolved
indirect paths involve 487 distinct intermediates; resolved paths reach 132
distinct annotated motor bodies. These are path counts, not independent
functional circuits, equivalent gains or physiological confidence rankings.

Unresolved reasons overlap: 2,659 paths have an intermediate not annotated
`vnc_intrinsic`; 295 have missing/non-LR side or type; 45 lack positive final-edge
front-leg ROI evidence. The 2,659 intermediate-class failures comprise 1,897
descending-neuron, 612 ascending-neuron, 148 motor and 2 efferent-ascending paths.
Those known classes are not promoted to premotor interneurons. Separately, 2,553
source outgoing edges have no direct/one-interneuron route into the target set;
they are recorded as excluded with this bounded-search reason.

Resolved endpoint soma-side pairs are L→L 382, L→R 2,110, R→L 3,682 and R→R 277.
No symmetry repair, laterality flip or physiological interpretation is applied.

Representative **lexicographic examples**, not selected functional winners:

| Route | Annotation evidence |
| --- | --- |
| `10045 → 801469` | DNg100_L → Sternal anterior rotator MN, R |
| `10056 → 800061` | DNg100_R → Tergopleural/Pleural promotor MN, L |
| `10045 → 800030 → 1050268065` | DNg100_L → IN12B002, L → Acc. ti flexor MN, R |
| `10056 → 800001 → 802552` | DNg100_R → IN07B016, L → Tergotr. MN, L |

The literature-context candidate IN17A001 is present: `10045 → 800288` has
native count 100 and 16 resolved short motor paths; `10056 → 800173` has count
155 and 23. `10056 → 800863/INXXX466` has count 1 and 33 resolved short paths,
so that first edge does not survive the declared sensitivity threshold 5.
The other proposed motif members are not established as a recurrent motif by
these short-path queries. Missing first-hop edges are bounded negative evidence,
not proof of neuronal or longer-path absence.

## Recoverable provenance and reproduction

The small tracked [reference manifest](dng100_walking_route_authority_reference.json)
pins complete external evidence. It contains no credentials or private absolute
paths. External files are `source.json` (979,436 bytes), `annotations.feather`
(14,483,314 bytes), `contract.json` (9,802,461 bytes) and `manifest.json`.
Large source/derived files remain outside Git and outside frozen runtime archives.

| Identity | SHA-256 |
| --- | --- |
| Canonical source snapshot | `4d01c1588a82dde83a17e569861a835bd205c1e068f7b1fb50fdf97b9a246819` |
| Complete configuration | `c81b11e74df5b9520c30fb97874e6e7413b85189c6b4466aab877dde2ac7ef2f` |
| Structural result | `48eb3aae9d9f9680975db368a358c91eb2326d013125826f1740f983405a1e95` |
| Logical artifact | `5d6b0f678b9d3437bb66c7837218a46001d7b2217b27ec2cba81a7aaa4833e19` |
| Raw contract file | `7b8aebaf38dc15ce4354bd50ad7e080883e8eb8583048cdf34e205eb5fc29c55` |

Canonical serialization reuses repository sorted compact ASCII JSON. The logical
artifact hash covers schema/config/result identities; it is not a raw file hash.
Configuration includes complete policy, annotation/snapshot pins and the actual
extractor file checksum. Every edge has dataset/confidence policy and exact
query/row/hash references. Every relevant neuron has annotation evidence and an
explicit structural role; raw annotations remain recoverable for unresolved IDs.

The local workspace convention is the external sibling
`neurofly-science/work/dng100-route-authority-v1/<artifact-id>/`; it is not a public
artifact location. Supply a controlled explicit location on another machine:

```bash
.venv/bin/python -m neurofly.dng100_walking_route_authority --replay /external/path/<artifact-id>
.venv/bin/python -m neurofly.dng100_walking_route_authority --acquire /external/output/root
```

Replay checks exact file inventory, hashes, source pin and full semantic
re-extraction. Recomputed hashes do not legitimize contradictory route metadata.
Acquisition refuses drift from the committed snapshot. Output is atomic and
content-addressed, cannot be written inside the repository, and existing content
is validated rather than overwritten. Source credentials are never persisted.
Re-extraction depends on the matching versioned extractor, not future edited code.

## Validation and smallest next scientific slice

The focused suite has 39 cases: bilateral identities, version/UUID/source drift,
direction, malformed/count/ROI inputs, classification, missing authority,
cycles, empty results, deterministic ordering, asymmetry, invalid policy,
semantic tampering after rehashing and external-file integrity. The real-source
gate is strict: missing evidence fails rather than silently using fixtures.
An independent raw-pair enumeration checks all 9,342 paths without invoking the
extractor or its edge parser. Synthetic IDs occur only in isolated tests.
Run the full Python suite, Ruff checks, source authority replay, five canonical
payload replays, Planar SHADOW_ONLY reproduction and `git diff --check` before
publication. No frontend or provider operation is part of this work.

Validation completed on 2026-10-13: 39 focused tests passed; the canonical full
suite passed 1,388 tests in 900.07 seconds (one existing authenticated integration
test deselected by repository configuration, two dependency deprecation warnings).
Ruff lint/format checks passed. The five canonical payload hashes and
`VALIDATED_CANONICAL_REPLAY` provenance, frozen runtime inventory/archive/source
files, existing GF motor authority and external Planar Steering semantic replay
all passed. Preregistration, kernels, existing plant/API and external shadow
artifact checksums remained unchanged. No web build was needed for this slice.

The next single slice should be **a bounded recurrent-edge authority extraction
for the bilateral IN17A001/INXXX466/IN16B036 candidate set** under the same pins.
Verify each annotation and all directed edges among those candidate bodies,
their DNg100 inputs and identified front-leg motor outputs, including absent
edges and unresolved ROI/classification. Predeclare the bounded selection and
do not add rhythms or force a literature motif to appear. Passing that slice
would provide exact structural evidence for choosing a later neural validation;
it would still not establish neurotransmitter signs, CPG sufficiency, walking,
muscle force or body translation.
