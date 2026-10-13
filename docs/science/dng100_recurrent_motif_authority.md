# DNg100 recurrent motif structural authority v1

## Scientific decision

`DNG100_RECURRENT_MOTIF_AUTHORITY_VERIFIED`, strictly for the preregistered
**structural** criteria of `DNG100_RECURRENT_MOTIF_AUTHORITY_V1`.
The selected concrete T1 neurons have same-side, three-type directed cycles,
matching segment ROI evidence, reviewed annotations, DNg100 input reachability
and front-leg motor output reachability. Contextual paths with incomplete or
ineligible anatomical evidence remain unresolved. This does not upgrade the
previous broad route-authority PARTIAL result or change its evidence.

No neural dynamics, transmitter-dependent sign, gain, conduction delay, simulated
rhythm, motor recruitment, gait, muscle force or body movement is implemented.
These graphs do not establish physiological oscillation, CPG sufficiency or
walking. The literature roles E1/E2/I1 are labels, not assigned synaptic effects.

## Read-only preflight and authorities

The clean `main` baseline was `eea0a906672f64c1a2c9c9bb812b26c0b15eacad`.
The previous [route authority](dng100_walking_route_authority.md) was replayed
semantically against its external evidence. Its connectivity identity
`4d01c1588a82dde83a17e569861a835bd205c1e068f7b1fb50fdf97b9a246819`
is a **scoped snapshot**, not the checksum of a complete MaleCNS connectome.
It covers all DNg100 Neuron outputs and their neighbors' edges into selected
front-leg motors. Its missing motif-to-motif edges were unqueried, not proven
absent. The new extractor requests the full induced candidate graph separately.

Dataset selector remains `male-cns:v1.0`, official endpoint
`https://neuprint.janelia.org`, native UUID
`4b2087c0fbe046bfaf0d60bc970e3e5d`, native dataset/tag `male-cns`/`v1.0`.
Initial and final source metadata match the preceding authority, including
mutation ID `1006591300` and the recorded database edit label. No release upgrade,
cross-connectome IDs, bulk graph download or new credentials were used.

The same annotation file from the [official MaleCNS distribution](https://male-cns.janelia.org/download/)
is reused byte-for-byte:
`body-annotations-male-cns-v1.0-minconf-0.5.feather`, 14,483,314 bytes, SHA-256
`2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`.
Body ID, exact type, instance, soma side, superclass, soma neuromere, status and
status label provide recoverable classification evidence. Unavailable fields
remain null; subtype names or anatomical proximity cannot repair them.

Source roots are again `10045/DNg100_L/L`, `10056/DNg100_R/R`; their Traced /
Prelim Roughly traced labels remain visible. Motor targets use the preceding
135-body authority: `vnc_motor`, `fl`, `T1`, not name substrings. The new module
reuses existing identity, annotation, directed-row and hashing helpers, without
editing the prior extractor or its artifacts.

## Extraction policy and completeness

[dng100_recurrent_motif_policy.json](dng100_recurrent_motif_policy.json) was
written before querying the selected body-level graph, with canonical hash
`1b71c798cb291e76378fa5ec3e03e836b6a1910e4b07ac0e9b68f4537e96f4a8`.
This records a local ordered workflow, not independently timestamped prospective
registration. No threshold or acceptance rule was tuned after graph inspection.

* Select **all** exact annotation matches for IN17A001, INXXX466 and IN16B036.
  A type/side label is not a unique neuron ID; no one-cell cardinality is assumed.
* Analyze soma-side L/R and segments T1/T2/T3 separately. Unknown anatomy/tracing
  is preserved and prevents a positive or complete-negative selection decision.
* Fetch all ordered selected pairs, including self, cross-side and cross-segment
  pairs, without a count threshold in the source query. Verify all 155 required
  Neuron-presence rows (18 candidates, two roots, 135 motors) against annotations.
* An independent count query confirms the 36 induced edges. Both query text and
  ordered response rows are stored. Absence requires complete requested coverage
  and verified node presence; it means absence in this Neuron ConnectsTo chemical
  aggregate scope, not absolute biological absence, electrical absence or proof
  that tracing is complete at individual-synapse resolution.
* Require positive integer native counts. Primary minimum is 1 per edge;
  sensitivity at 5 and 10 is reported separately. Native confidence metadata
  remains postHighAccuracyThreshold 0.5, postHPThreshold 0.699999988079071 and
  preHPThreshold 0. No additional per-synapse confidence filter is invented.
* Enumerate simple directed cycles of lengths two and three. Canonicalize cyclic
  rotation; preserve reverse direction. Self-edges and repeated-node walks are
  not counted as such cycles. Ordering is lexicographic, not functional ranking.
* Qualifying three-type motifs have one member of each literature type, one side,
  one segment, reviewed Traced members and positive postsynaptic count in the
  declared segment's LegNp on every cycle edge. Overlapping ROI counts are not
  added together or substituted for the native global edge count.
* Input context is direct DNg100-to-member and one-intermediate reachability using
  the pinned all-DNg-output snapshot plus a new neighbors-to-member query.
* Output context is direct all-members-to-T1-motor and one-intermediate routes
  from T1 members only. T2/T3 indirect motor context is **NOT_QUERIED**, not zero.
* Intermediates require actual `vnc_intrinsic`, nonempty type and L/R identity to
  be resolved structural candidates; final-edge segment ROI must be explicit.
  Cross-side/segment context remains recorded, never normalized or reclassified.

VERIFIED requires qualifying T1 motifs on both sides, reviewed identities, input
and output structural context for both groups, and both DNg100 roots reaching T1.
PARTIAL preserves recurrence or anatomical uncertainty when those criteria fail.
NO_SUPPORTED_CYCLE requires complete primary anatomy/coverage and absence of
same-side T1 two/three-node cycles. Integrity/coverage failure is an error, not a
negative biological finding.

## Concrete selected identities

All 18 members have `vnc_intrinsic`, Traced / Reviewed annotations; official
Neuron presence agrees on body/type/side/neuromere/superclass.

| Segment | Soma side | IN17A001 (E1 label) | INXXX466 (E2 label) | IN16B036 (I1 label) |
| --- | --- | ---: | ---: | ---: |
| T1 | L | 800173 | 800863 | 801884 |
| T1 | R | 800288 | 903216 | 803183 |
| T2 | L | 800009 | 801728 | 903139 |
| T2 | R | 818556 | 802025 | 904079 |
| T3 | L | 800003 | 801149 | 801257 |
| T3 | R | 800114 | 801429 | 801916 |

## Complete induced directed-edge inventory

Each table row names concrete IDs through the preceding table. Values are native
synapse counts, not effective weights. All six directions exist in each group.
The reference manifest additionally carries exact IDs, ROI counts and source-row
references for every observed edge, plus all 324 ordered pair statuses.

| Group | E1→E2 | E2→E1 | E1→I1 | I1→E1 | E2→I1 | I1→E2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T1 L | 465 | 11 | 6 | 526 | 38 | 121 |
| T1 R | 328 | 5 | 1 | 439 | 27 | 96 |
| T2 L | 511 | 25 | 5 | 658 | 121 | 313 |
| T2 R | 397 | 16 | 5 | 508 | 129 | 211 |
| T3 L | 505 | 20 | 14 | 847 | 65 | 316 |
| T3 R | 527 | 12 | 12 | 727 | 65 | 204 |

At threshold 1 each group has three reciprocal two-node cycles and both directed
three-node cycles: E1→E2→I1→E1 and E1→I1→E2→E1. Across all groups: **18 two-node
and 12 three-node cycles**. Each T1 side therefore has two qualifying three-type
motifs under the policy. This is structural recurrence, not oscillation.

No self-edges or cross-side/cross-segment edges were observed among the 18
candidates. The other **288** ordered pairs are source-complete absent within
this snapshot/query scope. This says nothing about other cell types, longer
loops, electrical coupling, or untraced synapses.

ROI evidence is retained separately. For example, `801884→800173` has native
count 526, LegNp(T1)(L) post 525 and VNC-unspecified post 1; `904079→818556`
has count 508, LegNp(T2)(R) post 504 and VNC-unspecified post 4. VNC parent totals
overlap child ROIs and are never summed to manufacture a different count.

| Group | Cycles 2/3 at ≥1 | Cycles 2/3 at ≥5 | Cycles 2/3 at ≥10 |
| --- | --- | --- | --- |
| T1 L | 3 / 2 | 3 / 2 | 2 / 1 |
| T1 R | 3 / 2 | 2 / 1 | 1 / 1 |
| T2 L | 3 / 2 | 3 / 2 | 2 / 1 |
| T2 R | 3 / 2 | 3 / 2 | 2 / 1 |
| T3 L | 3 / 2 | 3 / 2 | 3 / 2 |
| T3 R | 3 / 2 | 3 / 2 | 3 / 2 |

Total cycles are 30, 28 and 21. One qualifying three-type T1 cycle survives on
each side at threshold 10, without changing the primary threshold. The weak
T1 R E1→I1 edge (count 1) is preserved, not repaired to match the left side.

## DNg100 input and front-leg output context

Thirteen of 36 direct DNg-to-member pairs are observed. All observed direct
targets have soma side opposite their source DNg100. Soma side is not a verified
axon-side mapping; no sign or laterality repair is applied.

| DNg100 source | Target body IDs (native counts) |
| --- | --- |
| 10045 L | 800288 (100), 818556 (135), 800114 (121), 802025 (2), 801429 (2), 904079 (1), 801916 (9) |
| 10056 R | 800173 (155), 800009 (167), 800003 (140), 800863 (1), 801149 (1), 903139 (1) |

T1 direct context is consequently `10045→800288` and `10056→800173,800863`.
There is no direct T1 I1 input from either root in this scoped source, but bounded
indirect paths exist. DNg100 does not contact only E1 across all segments.

Input enumeration yields 1,964 paths: 13 direct and 1,951 one-intermediate;
1,302 resolved, 662 unresolved. Overlapping unresolved reasons are 644
non-vnc-intrinsic intermediates, 57 identity/side uncertainties and four missing
final-segment ROI records. These candidates are retained without functional
premotor promotion.

All 119 observed direct motor edges originate in T1 members. Direct edge counts
per member are L: E1 23, E2 33, I1 11; R: E1 16, E2 24, I1 12. The bounded output
enumeration adds 20,810 one-intermediate paths, for 20,929 total. Of those, 18,374
are resolved structural reachability and 2,555 unresolved. Overlapping reasons
are 2,186 ineligible intermediate classes, 509 identity/side uncertainties and
35 missing final T1 ROI records. No route is called physiologically recruited.

| T1 group | Resolved DNg input paths | Unresolved input paths | Resolved motor output paths | Unresolved output paths |
| --- | ---: | ---: | ---: | ---: |
| L | 212 | 129 | 10,734 | 1,515 |
| R | 143 | 123 | 7,640 | 1,040 |

The 2,430 direct member-to-motor pair statuses are explicit in the full artifact.
Zero direct T2/T3 edges into this **front-leg T1 pool** does not establish absence
of their own segment's motor outputs. Their indirect motor paths and T2/T3 motor
pools were not queried. Input/output context is separate from motif verification.

## Literature and transmitter boundary

[Pugliese et al., bioRxiv, DOI 10.1101/2025.09.12.675944](https://doi.org/10.1101/2025.09.12.675944),
*Connectome simulations identify a central pattern generator circuit for fly
walking*, motivates the type-level candidate. The [PubMed preprint record](https://pubmed.ncbi.nlm.nih.gov/42094485/)
lists the revised work. This experiment does not establish exact equivalence to
the paper's experimental cells, MANC/FANC identities, parameters or dynamical
preparation. No physiological or simulated result is reproduced here.

Independent Cell Type Explorer cross-checks were read for
[IN17A001](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/IN17A001.html),
[INXXX466](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/INXXX466.html)
and [IN16B036](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/IN16B036.html).
They agree on type-level bilateral T1/T2/T3 occurrence. Their displayed transmitter
summaries are ACh for IN17A001 (97.1% CL), ACh for INXXX466 (96.8% CL) and Glu for
IN16B036 (82.9% CL). Those are **unpinned type-level cross-checks**, not imported
body-level prediction authority. The INXXX466 page required a standard-library
HTTP read after browser retrieval failed; no dependency was installed.

The pinned curated annotation file contains no neurotransmitter prediction or
confidence columns. Machine-readable predictions remain UNAVAILABLE; synaptic
receptor identity, physiological sign, gain and delay remain unestablished. The
annotation field named receptorType is not silently interpreted as a molecular
postsynaptic receptor measurement. No glutamate-to-inhibition inference is made.

## Recoverable artifacts and verification

[dng100_recurrent_motif_reference.json](dng100_recurrent_motif_reference.json)
is the small tracked reference: policy/source/config/result identities, all
selected annotations, induced observed edges, complete pair inventory and group
sensitivity summaries. Full context graphs and recoverable raw inputs stay in
the external scientific workspace, not Git or the frozen runtime bundle.

| Identity | SHA-256 |
| --- | --- |
| New scoped source | `def753409faa5daa7932ad5c256c644b2b426f44c053b2c40a5b89a17d6b024e` |
| Complete configuration | `3c03dde27f8d4884beabaa8494285c3057a05bcc4d984d6a50af2a0b61a16b65` |
| Structural result | `06b886c0c2a13a41d4e2af96b7229037f16e1501e3842d8ba124227c0f55f68e` |
| Logical artifact | `baae20599455c2a7acb3271e6eeb6b73326d17185b6e705022b74818ff0f8934` |
| Raw contract | `266bb2e8b832a4d6881bf22f46db3de406c685d4f76c17acfbd7d5026f37f861` |

External contents: source.json (1,272,633 bytes), prior_source.json (979,436),
annotations.feather (14,483,314), contract.json (18,805,117) and manifest.json.
The local store convention is the external sibling
`neurofly-science/work/dng100-recurrent-motif-v1/<artifact-id>/`, not a public
portable artifact address. Use an explicit controlled location elsewhere:

```bash
.venv/bin/python -m neurofly.dng100_recurrent_motif_authority --replay /external/path/<artifact-id>
.venv/bin/python -m neurofly.dng100_recurrent_motif_authority --acquire /external/output/root
```

Canonical serialization reuses sorted compact ASCII JSON and existing hashing.
Configuration includes complete fixed policy, all source pins, schema/extractor
version and actual implementation checksum; source metadata records SDK 0.6.3.
Every edge has dataset, native confidence convention, annotation evidence and
exact file/query/row/hash references. Observed context contradicting an induced
absence is rejected. Atomic content-addressed output cannot be placed in the
repository, overwrite existing evidence or silently replace source pins.

Semantic replay rebuilds the complete result from pinned annotations and both
source snapshots. Recomputed hashes cannot legitimize changed identities, edge
direction, cycle summaries, reachability, physiology or policy. Real-source tests
are mandatory and do not silently skip or replace missing data with fixtures.
Independent tests close cycles directly from raw adjacency, verify the T1
matrix's recorded counts and exercise known small graphs, negative coverage,
ROI/classification uncertainty, overlapping-source contradiction, threshold
sensitivity and fake-fixture rejection by the production builder.

Final validation on 2026-10-13: the canonical Python suite passed **1,429 tests**
in 911.79 seconds, including all 41 motif-authority cases. One existing
authenticated integration test was deselected by repository configuration;
two existing dependency deprecation warnings remain. Ruff lint and format checks
and `git diff --check` passed. The five canonical payload hashes and validated
provenance, frozen D2.2 archive/manifest/inventory/source files, previous DNg100
authority, GF motor authority and Planar SHADOW_ONLY semantic replay passed.
Existing kernels, policies and external prior artifacts remained byte-identical.
No frontend build, source migration, dependency installation or provider setting
operation was performed. Removing redundant policy-file reads changed only the
implementation/configuration identity; the scientific result hash stayed exact.

## Smallest next scientific slice

**A versioned body-level transmitter/receptor and sign-readiness authority audit
for the six T1 members and DNg100 inputs.** Pin official prediction records and
their confidence for these exact MaleCNS bodies; investigate independently
supported receptor/effect evidence and explicitly leave missing physiological
effects unresolved. No dynamics, fitted gains, rhythms or body actuation.
Passing that slice would make a later preregistered neural-only model hypothesis
more traceable; it would not provide biological calibration or walking.
