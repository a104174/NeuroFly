# Phase 8E — pinned MaleCNS motor neural structural contract

**Decision: `MOTOR_STRUCTURAL_CONTRACT_PINNED`.** This phase pins source
identity and bounded chemical-connectivity evidence only. It adds no PSI,
DLMn, electrical-coupling, muscle, or behavior dynamics.

## Scope and source provenance

The existing `looming_giant_fiber_v1` CircuitContract ends at the two DNp01
bodies and does not contain TTMn, PSI, or DLMn. Phase 6B's
[`motor_escape_feasibility.md`](motor_escape_feasibility.md) records the
historical bounded motor query and its expected identities/counts, but no
independent canonical-response digest. Phase 8E reconstructed that bounded
query against official neuPrint `https://neuprint.janelia.org`, dataset
`male-cns:v1.0`, using the repository-configured authenticated client and
`neuprint-python 0.6.3`.

The historical record explicitly specifies directed `fetch_adjacencies`
queries for exact body-ID sets, VNC ROI, `min_total_weight=1`, and
`include_nonprimary=True`; it documents no annotation-status filter. Identity
and side were re-read from the official MaleCNS v1.0 body-annotation table,
then used to construct exact-ID query criteria. Phase 8E also pins the
effective `min_roi_weight=1` setting explicitly (the neuprint-python 0.6.3
default), together with `batch_size=200`, `weight_props="all"`,
`omit_rois=False`, and `threads=4`, so a later refresh cannot silently inherit
different client defaults. No query is inferred from laterality.

The historical query was not available as executable Phase 6B source code;
its recorded identity sets, direction, ROI, threshold, and inclusion settings
were reconstructed from the committed Phase 6B document. The explicit
Phase 8E query configuration and complete bounded response now close the
missing content-hash gap. The historical expected rows for the three
Phase 6B route groups were checked exactly before pinning.

| Pinned source | Identity |
| --- | --- |
| Dataset / endpoint | `male-cns:v1.0` / `https://neuprint.janelia.org` |
| Official annotation snapshot | `body-annotations-male-cns-v1.0-minconf-0.5.feather`; 14,483,314 bytes; SHA-256 `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2` |
| Canonical query-response SHA-256 | `845c1c1ddc60183fd02f8ac2ceaac5e1a16cba34c803707fb974e7b52861e43e` |
| Query-definition SHA-256 | Recorded in `source_manifest.json` and the contract provenance |
| Contract ID / content hash | `a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c` |
| Schemas | `motor_neural_query_response_v1`, `motor_neural_query_source_manifest_v1`, `motor_neural_pathway_contract_v1` |

The official Feather itself is not copied into the repository. The canonical
normalized response (the 16 selected annotation rows plus bounded directed
edge rows), source manifest, contract, and file-integrity manifest are stored
under the ignored derived-data path:

```text
data/derived/malecns/looming_giant_fiber_v1/
  motor_neural_pathway_contract_v1/<contract-id>/
```

The response uses canonical UTF-8 JSON with sorted keys, compact separators,
no trailing newline, and stable sorting of identities and edges. The query
response hash identifies that complete representation, including query
parameters and the annotation source hash. Creation timestamp and runtime
versions are source-manifest provenance, not part of the contract identity.

## Verified identities

The following exact MaleCNS `bodyId` rows were returned by the official
annotation snapshot. All are marked `Traced`; the DNp01 rows have
`statusLabel=Roughly traced`, and the other rows have `statusLabel=Reviewed`.

| Body ID | Type / instance | Side | Annotation details |
| ---: | --- | :---: | --- |
| 10001 | DNp01 / `DNp01(GF)_R` | R | `descending_neuron`, subclass `lt` |
| 10010 | DNp01 / `DNp01(GF)_L` | L | `descending_neuron`, subclass `lt` |
| 800146 | TTMn / `TTMn_R` | R | `vnc_motor`, subclass `wm`, T2 |
| 804642 | TTMn / `TTMn_L` | L | `vnc_motor`, subclass `wm`, T2 |
| 802401 | PSI / `PSI_L` | L | `vnc_efferent`, T2 |
| 903327 | PSI / `PSI_R` | R | `vnc_efferent`, T2 |
| 801295 | DLMn a, b / `DLMn a, b_R` | R | `vnc_motor`, subclass `wm`, T2 |
| 801970 | DLMn a, b / `DLMn a, b_L` | L | `vnc_motor`, subclass `wm`, T2 |
| 800718 | DLMn c-f / `DLMn c-f_L` | L | `vnc_motor`, subclass `wm`, T1 |
| 800890 | DLMn c-f / `DLMn c-f_L` | L | `vnc_motor`, subclass `wm`, T1 |
| 801895 | DLMn c-f / `DLMn c-f_L` | L | `vnc_motor`, subclass `wm`, T1 |
| 803013 | DLMn c-f / `DLMn c-f_L` | L | `vnc_motor`, subclass `wm`, T1 |
| 801998 | DLMn c-f / `DLMn c-f_R` | R | `vnc_motor`, subclass `wm`, T1 |
| 802544 | DLMn c-f / `DLMn c-f_R` | R | `vnc_motor`, subclass `wm`, T1 |
| 803048 | DLMn c-f / `DLMn c-f_R` | R | `vnc_motor`, subclass `wm`, T1 |
| 1050014552 | DLMn c-f / `DLMn c-f_R` | R | `vnc_motor`, subclass `wm`, T1 |

These are source identities, not assignments inferred from a pathway diagram.
The `PSI_L`/`PSI_R` labels and observed cross-side chemical edges are retained
as returned; no same-side rule is imposed.

## Verified chemical routes

Counts below are the official VNC aggregate `ConnectsTo` structural counts.
The arrows are query direction, not a model transmission rule.

### DNp01 → TTMn (2 edges)

| Source | Target | Structural count |
| --- | --- | ---: |
| 10001 `DNp01(GF)_R` | 800146 `TTMn_R` | 70 |
| 10010 `DNp01(GF)_L` | 804642 `TTMn_L` | 20 |

### DNp01 → PSI (4 edges)

| Source | Target | Structural count |
| --- | --- | ---: |
| 10001 `DNp01(GF)_R` | 802401 `PSI_L` | 3 |
| 10001 `DNp01(GF)_R` | 903327 `PSI_R` | 2 |
| 10010 `DNp01(GF)_L` | 802401 `PSI_L` | 9 |
| 10010 `DNp01(GF)_L` | 903327 `PSI_R` | 2 |

### PSI → DLMn (10 edges)

| Source | Target | Structural count |
| --- | --- | ---: |
| 802401 `PSI_L` | 801970 `DLMn a, b_L` | 17 |
| 802401 `PSI_L` | 801998 `DLMn c-f_R` | 40 |
| 802401 `PSI_L` | 802544 `DLMn c-f_R` | 67 |
| 802401 `PSI_L` | 803048 `DLMn c-f_R` | 35 |
| 802401 `PSI_L` | 1050014552 `DLMn c-f_R` | 64 |
| 903327 `PSI_R` | 800718 `DLMn c-f_L` | 68 |
| 903327 `PSI_R` | 800890 `DLMn c-f_L` | 24 |
| 903327 `PSI_R` | 801295 `DLMn a, b_R` | 26 |
| 903327 `PSI_R` | 801895 `DLMn c-f_L` | 58 |
| 903327 `PSI_R` | 803013 `DLMn c-f_L` | 50 |

### Supplemental PSI candidate-subgraph check (2 edges)

A separately labeled Phase 8E supplemental query over the two candidate PSI
bodies returned `802401 → 903327` count 5 and `903327 → 802401` count 17.
These were not part of the Phase 6B historical three-route-group query and
are not presented as a historical route discrepancy. They are included in
the pinned response/contract as supplemental chemical structural records.

### Direct DNp01 → candidate DLMn audit

The exact-body directed query from DNp01 10001/10010 to the ten listed DLMn
bodies returned **zero direct chemical edges** at the pinned VNC threshold.
This is only a negative result for that bounded source/target set and query;
it does not establish absence of every Giant Fiber-to-flight-motor path or
other intermediary cells.

The contract therefore contains 18 returned chemical edges total: the 16
historical pathway edges above and two supplemental PSI↔PSI edges. The direct
DNp01→candidate-DLMn zero-result audit is explicit. There is no edge from a
literature diagram silently inserted into the source graph.

## Evidence interpretation and readiness

The structural contract records only MaleCNS identity/annotation and
chemical `ConnectsTo` rows. It does not claim those rows fully describe the
known mixed electrical/chemical GF motor connections. The prior
[Phase 8D assessment](psi_dlmn_motor_branch_assessment.md) reviews the
primary literature and separates that evidence from this MaleCNS snapshot.

| Correspondence | Evidence class | Mapping confidence | Boundary |
| --- | --- | --- | --- |
| MaleCNS `DNp01(GF)` and Giant Fiber pathway | Literature-to-class mapping | HIGH | The MaleCNS instance label includes GF; this is not a physiological edge calibration. |
| GF → TTMn pathway | Literature evidence | HIGH | Mixed electrical/chemical pathway class; the queried chemical count is not the electrical component. |
| GF → PSI pathway | Literature evidence | MODERATE | Pathway correspondence is supported, but historic physiology is not assigned to these exact MaleCNS body pairs. |
| PSI → DLM motor-neuron class | Literature evidence | MODERATE | Class-level route support; no exact historical-cell-to-MaleCNS-body mapping or edge efficacy. |
| Historical MN5 recording → a particular MaleCNS DLMn ID | UNRESOLVED | UNRESOLVED | Do not force an exact body mapping. |

MaleCNS chemical edge count is **structural metadata only**. It is not gain,
conductance, efficacy, probability, delay, event multiplier, or evidence of
electrical coupling. Literature reports of electrical/mixed transmission
remain separate evidence; published fitted conductances are not measurements
for these MaleCNS pairs.

The contract intentionally has no dynamics fields: no time constant, gain,
conductance, threshold, delay, voltage, spike-generation rule, or integrator.
It is suitable as source provenance for a future modelling decision, not as
authorization for calibrated PSI/DLMn dynamics.

## Compatibility and replay

The two Phase 6C DNp01→TTMn routes (10001→800146 count 70 and 10010→804642
count 20) are an exact subset of this contract. The Phase 8C production
adapter resolves the same two identities/counts. Neither historical artifact
schema is migrated, and neither downstream model uses structural count as a
numerical multiplier.

Offline validation/replay reads only the pinned canonical snapshot and
rebuilds hashes and contract identity:

```bash
python -m neurofly.motor_neural_contract_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/motor_neural_pathway_contract_v1/<contract-id>
python -m neurofly.motor_neural_contract_cli inspect \
  data/derived/malecns/looming_giant_fiber_v1/motor_neural_pathway_contract_v1/<contract-id>
```

An explicit `pin` operation runs the bounded official query and persists only
an exact historical match. An explicit `refresh <artifact-path>` performs a
live comparison and reports `MATCH` or `DRIFT`; it never overwrites the
snapshot. Phase 8E refresh returned `MATCH`: annotation identities, route
rows/counts, and canonical response hash all matched the newly pinned source.

The contract establishes structural provenance, not functional connectivity,
electrical coupling, identified pair-specific efficacy, motor state, muscle
activation, force, or behavior. Phase 8E stops before PSI/DLMn dynamics.
