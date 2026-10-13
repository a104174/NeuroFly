# DNg100 neurotransmitter and sign evidence authority V1

## Scientific decision

`DNG100_NT_SOURCE_VERIFIED_SIGNS_UNKNOWN`.

The official MaleCNS v1.0 body-level neurotransmitter table is pinned and eight
concrete identities are reconciled with the published recurrent-motif authority.
Fifteen directed structural edges preserve their counts and recoverable source
rows. All fifteen functional signs remain **UNKNOWN**. This is a successful
transmitter-evidence extraction, not a verified signed circuit.

No neural dynamics, receptor kinetics, functional weights, delays, oscillations,
walking, propulsion or body actuation are implemented. The prior structural and
Planar SHADOW_ONLY experiments are not revised.

## Preflight and policy

The initial repository was clean main at
`a29f0048c0075b2f72806b54064282efe03c4b72`; remote main matched.
The official neuPrint metadata still matched the previous pinned structural
snapshot, including dataset UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`.

[dng100_nt_sign_policy.json](dng100_nt_sign_policy.json) was fixed after the
required read-only schema/source preflight and before implementing final
classifications. Its canonical identity is
`80a851c9ddd55aa32ccbc75016ca289be723a38e16d447db7b9380841db8a78b`.
This is a versioned extraction/evidence policy, not a claim of independently
timestamped prospective biological preregistration. Its source pins, exact body
IDs, edge scope, conflict rules and sign criteria are not tuned after extraction.

There is no new graph search, fragment aggregation, confidence averaging,
categorical voting or transmitter-to-sign dictionary. Duplicate target rows,
including identical duplicates, fail rather than selecting the first match.
Exact integer body IDs and exact type/laterality/segment/instance/tracing labels
are required. T2/T3 and external-connectome body IDs cannot enter the primary scope.

## Official source and schema

The [official download page](https://male-cns.janelia.org/download/) links the
[body-neurotransmitters-male-cns-v1.0.feather](https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-neurotransmitters-male-cns-v1.0.feather)
table as aggregate predictions per neuron. The raw file was not cached and was
downloaded once into the external scientific workspace on 2026-10-13.
It contains 1,835,518 rows and ten columns, 43,282,834 bytes, SHA-256
`95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621`.
This checksum was computed from the retrieved official bytes, not copied from a
third-party report.

| Column | Preserved meaning |
| --- | --- |
| body | Exact reconstructed segment/body ID |
| cell_type | Official type label, checked against pinned annotations |
| total_nt_predictions | Body presynaptic prediction count |
| predicted_nt | Body aggregate label |
| predicted_nt_confidence | Raw body confidence, finite [0,1] or null |
| ground_truth | Source-reported cell-type ground truth joined onto body rows |
| celltype_total_nt_predictions | Pooled type prediction count |
| celltype_predicted_nt | Pooled type label |
| celltype_predicted_nt_confidence | Raw type confidence, finite [0,1] or null |
| consensus_nt | Official consensus/curated type-level assignment |

All eight targets have exactly one row. Source row positions and canonical raw
row hashes are recorded, retaining double precision and explicit nulls.
The full table contains segments/fragments as well as annotated neurons; its
presence is not proof of complete reconstruction or a cell-specific experiment.
The observed non-null source vocabulary is acetylcholine, dopamine, gaba,
glutamate, histamine, octopamine, serotonin, and unclear; ground_truth uses the
same seven transmitter labels without unclear. Missing values remain null.

The [MaleCNS manuscript methods](https://doi.org/10.1016/j.cell.2026.08.015)
describe per-body and pooled type predictions, source confidence filtering, and
experimental type-level overrides in consensus. The released source uses
`unclear` for unsupported predictions; the extractor does not silently replace
it. No additional NeuroFly confidence cutoff is applied. Confidence is an
aggregate model score, not receptor certainty or a measured synaptic effect.
The peer-reviewed page could not be retrieved in full in this session; indexed
methods and the [preprint methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC12636603/)
were accessible through search, while PMC full-page access presented a challenge.

A bounded authenticated neuPrint SDK query of the same eight bodies independently
matched labels. API confidence values equal float32 conversions of Feather
float64 values; both are retained rather than declaring a serializer-induced
conflict. The exact scoped response, query, property-key query, source metadata
and retrieval date remain recoverable in the external artifact.
The selected SDK nodes do not expose the Feather ground_truth field. A null
response to an absent queried groundTruth property must not erase the Feather
value or be presented as biological absence.

## Eight-neuron evidence

ACh denotes acetylcholine; Glu denotes glutamate. Displayed confidences are rounded
only in this table. Full values, counts, all source fields and SDK counterparts
are in the [reference manifest](dng100_nt_sign_reference.json).

| Body | Type / side / segment | Individual NT / confidence | Type NT / confidence | Consensus | Raw ground_truth |
| --- | --- | --- | --- | --- | --- |
| 10045 | DNg100 L / segment not annotated | ACh / 0.9529439618 | ACh / 0.9545301199 | ACh | null |
| 10056 | DNg100 R / segment not annotated | ACh / 0.9560235114 | ACh / 0.9545301199 | ACh | null |
| 800173 | IN17A001 L / T1 | ACh / 0.9685675891 | ACh / 0.9707315621 | ACh | ACh |
| 800288 | IN17A001 R / T1 | ACh / 0.9724390691 | ACh / 0.9707315621 | ACh | ACh |
| 800863 | INXXX466 L / T1 | ACh / 0.9727791577 | ACh / 0.9680064801 | ACh | null |
| 903216 | INXXX466 R / T1 | ACh / 0.9679892495 | ACh / 0.9680064801 | ACh | null |
| 801884 | IN16B036 L / T1 | Glu / 0.8619699966 | Glu / 0.8286996121 | Glu | Glu |
| 803183 | IN16B036 R / T1 | Glu / 0.8493499034 | Glu / 0.8286996121 | Glu | Glu |

DNg100 retains `Traced / Prelim Roughly traced`; the six T1 interneurons retain
`Traced / Reviewed`. Confidence in NT does not upgrade tracing status.
Type-level columns pool the official cell type, including other segment members;
they are not recomputed over the six T1 neurons. The recorded type prediction
counts are 14,507 (DNg100), 15,996 (IN17A001), 8,800 (INXXX466) and 7,860
(IN16B036). They are prediction counts, not receptor or synaptic-efficacy measures.

The machine records distinguish EXPERIMENTAL_GROUND_TRUTH, MALECNS_CONSENSUS,
MALECNS_NEURON_PREDICTION, MALECNS_CELLTYPE_PREDICTION, EXTERNAL_CONTEXT_ONLY and
UNKNOWN. EXPERIMENTAL_GROUND_TRUTH here qualifies the **source-reported training
cell-type assignment**, never a direct experiment on the selected EM body or
synapse. Every evidence entry explicitly sets direct_experiment_on_selected_body
to false. The four populated ground_truth values do not verify receptors or signs.

The official release file does not identify the underlying study on each row.
A separately pinned [curated context table](https://github.com/flyconnectome/drosophila_neurotransmitters/blob/a9417412c8a70fcc9f80a65ca5bc6064eba07be3/gt_data.csv)
lists IN17A001/17A ACh and IN16B036/16B Glu with FISH, confidence 3, attributed
to Lacin et al. (2019). This is evidence about adult D. melanogaster VNC
hemilineages/types, not an independently verified reconstruction of the exact
release's training input or body-specific measurement. Sex specificity of those
curated mappings is not established by this audit.

[Lacin et al., eLife 8:e43701 (2019), DOI 10.7554/eLife.43701](https://pubmed.ncbi.nlm.nih.gov/30912745/)
used genetic lineage identification and transmitter marker/RNA assays. Their
figures support cholinergic 17A and glutamatergic 16B. These assays address
presynaptic transmitter usage, not receptor localization or the fifteen
connection-specific physiological effects.

The upstream [export implementation](https://github.com/janelia-flyem/flyem-snapshot/blob/4dbfcb9ebcfa52a3660906d472aedc5bfc40d197/flyem_snapshot/inputs/neurotransmitters.py)
joins training ground truth on cell_type and duplicates pooled type columns onto
body rows. This explains field resolution; the inspected current code revision
is contextual, not asserted to be the exact code revision that generated v1.0.

All populated source NT labels agree for these eight records. Conflicting labels
in adversarial fixtures are retained and mark primary evidence UNKNOWN. Missing,
unclear and unfamiliar labels remain explicit; null confidence is never zero.
No categorical average or new confidence score is computed.

## Fifteen directed connections

All counts below come unchanged from the published motif authority, including
ROI counts and exact source file/query/row references. Direction is pre to post.
The presynaptic evidence refers to the corresponding neuron record above.

| Pre → post | Structural count | Presynaptic NT | Receptor status | Functional sign |
| --- | ---: | --- | --- | --- |
| 800173 → 800863 | 465 | ACh | unresolved | UNKNOWN |
| 800863 → 800173 | 11 | ACh | unresolved | UNKNOWN |
| 800173 → 801884 | 6 | ACh | unresolved | UNKNOWN |
| 801884 → 800173 | 526 | Glu | unresolved | UNKNOWN |
| 800863 → 801884 | 38 | ACh | unresolved | UNKNOWN |
| 801884 → 800863 | 121 | Glu | unresolved | UNKNOWN |
| 800288 → 903216 | 328 | ACh | unresolved | UNKNOWN |
| 903216 → 800288 | 5 | ACh | unresolved | UNKNOWN |
| 800288 → 803183 | 1 | ACh | unresolved | UNKNOWN |
| 803183 → 800288 | 439 | Glu | unresolved | UNKNOWN |
| 903216 → 803183 | 27 | ACh | unresolved | UNKNOWN |
| 803183 → 903216 | 96 | Glu | unresolved | UNKNOWN |
| 10045 → 800288 | 100 | ACh | unresolved | UNKNOWN |
| 10056 → 800173 | 155 | ACh | unresolved | UNKNOWN |
| 10056 → 800863 | 1 | ACh | unresolved | UNKNOWN |

The twelve within-side motif edges and three DNg inputs are the complete scope.
No motor-pool receptor search, new route search, or synaptic strength conversion
is performed. The previously documented 119 motor targets remain structural
context only.

## Postsynaptic evidence and sign criteria

The eight pinned annotations have receptorType=null. Across the annotation source,
non-null receptorType values occur in vnc_sensory records and include
putative_ppk25, putative_ppk23 and putative_IR52b. The field's molecular
postsynaptic meaning has not been established from a documented schema in this
audit; its name is therefore not accepted as neurotransmitter receptor evidence.
No sensory-gene label is converted into a receptor claim for the T1 motif.

Bounded searches recorded in the policy examined exact motif type names and
DNg100/BDN2 with receptor, nicotinic and GluCl terms, pinned annotation fields,
MaleCNS methods, the curated transmitter resource, Pugliese and relevant primary
physiology. No sufficiently specific evidence was identified for a receptor on
one of these selected postsynaptic bodies or at these selected compartments.
This is **POSTSYNAPTIC_RECEPTOR_UNRESOLVED**, not evidence that receptors do not
exist. No comprehensive transcriptomic dataset was downloaded.

| Primary/context evidence | Method and biological resolution | Permitted use |
| --- | --- | --- |
| MaleCNS v1.0 | EM of adult male D. melanogaster; predicted/curated presynaptic NT | NT source and identity authority; no receptor physiology |
| Lacin et al. 2019 | Adult VNC lineage/marker/FISH evidence; curated type correspondence; sex applicability not resolved here | Type/hemilineage transmitter context only |
| Liu & Wilson 2013 | Adult antennal-lobe in-vivo patch clamp, iontophoresis, pharmacology, GluClα RNAi; females 1–4 days, males for RNAi experiments | Receptor-dependent inhibition in another circuit; no T1/body-specific assignment |
| Pugliese et al., revised preprint | Connectome simulations and separate optogenetic headless walking experiments | Candidate E1/E2/I1 interpretation; no validated signs at selected MaleCNS synapses |

[Liu & Wilson, PNAS 110:10294–10299 (2013), DOI 10.1073/pnas.1220560110](https://pubmed.ncbi.nlm.nih.gov/23729809/)
and their [paper with SI methods](https://wilson.hms.harvard.edu/sites/g/files/omnuum8421/files/wilson-lab/files/liuwilson2013a.pdf)
demonstrate GluClα-dependent inhibitory responses in the antennal lobe.
This functional evidence concerns different targets/preparations and cannot
resolve the selected T1 edges. No cross-connectome body ID is imported.

For EXCITATORY_SUPPORTED, INHIBITORY_SUPPORTED or MODULATORY_SUPPORTED, the policy
requires a verified target identity/correspondence, receptor expression,
relevant synaptic-compartment localization and matched direct physiological
effect without conflicting evidence. MIXED_OR_CONTEXT_DEPENDENT likewise needs
actual target-specific evidence; it is not a fallback label for an unknown sign.
NT prediction, cell-wide receptor expression elsewhere, a type name or a model
role label alone never satisfies those criteria.

V1 has no accepted target-specific receptor claims. The validator rejects added
claims and non-UNKNOWN signs even if result/config hashes are recomputed.
New evidence requires a separately versioned policy and review.

[Pugliese et al., DOI 10.1101/2025.09.12.675944, revised preprint](https://pubmed.ncbi.nlm.nih.gov/42094485/)
provides the candidate IN17A001/E1, INXXX466/E2 and IN16B036/I1 motif.
Agreement of MaleCNS NT assignments with their transmitter/model labels does
not reproduce their sign assumptions, gains, delays, parameters or rhythmic
simulations. Structural recurrence plus transmitter prediction is not a CPG
validation.

## Recoverable provenance and reproduction

The complete small [reference](dng100_nt_sign_reference.json) contains the
versioned policy, eight raw records/row references, SDK values, fifteen structural
records, receptor audit, configuration, result and logical identities.
Raw official Feather and previous structural sources remain outside Git.

| Identity | SHA-256 |
| --- | --- |
| Official NT Feather | 95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621 |
| Official annotation Feather | 2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2 |
| Recurrent scoped structural source | def753409faa5daa7932ad5c256c644b2b426f44c053b2c40a5b89a17d6b024e |
| Recurrent motif logical artifact | baae20599455c2a7acb3271e6eeb6b73326d17185b6e705022b74818ff0f8934 |
| Scoped SDK source | 7a930b6eb5083b58976df1ce8cd0f82dc5b9b34a4aeb59622edce4decf2a9fd8 |
| Evidence configuration | fa2b375118fb5cd51aa7efdd60b4ce998f4b6b1bfb873e9274aa5a9a3e3a2ea9 |
| Evidence result | 1807b37dd825165680f44d24faa37633c7782f99429213857acadb3fdbc24cfa |
| Evidence logical artifact | 38dc667d74acc3c6691b95659f38a1beab2f6208b5c592341f024f61d31bc526 |

Canonical hashing uses sorted compact JSON, ASCII escaping and no NaN.
Logical artifact identity hashes schema/config/result identities; it is not the
raw contract checksum. The external manifest separately records byte counts and
raw SHA-256 for contract.json and sdk-source.json. Complete official source URLs,
pins and scoped responses enable recovery without publishing a private local
path as a portable source location.
The raw contract checksum is
`c511df8275f59a56a5434ca9518a0f6759222f92f15e375d352cbe2a3ab2b52c`.

Local store convention: external sibling neurofly-science/work/dng100-nt-sign-v1.
The content-addressed artifact directory has three files: contract.json,
sdk-source.json and manifest.json. Full NT input remains in the external source
cache, not copied into Git. Writes are atomic; existing evidence is not overwritten.

```bash
.venv/bin/python -m neurofly.dng100_nt_sign_authority \
  --extract /EXTERNAL/OUTPUT \
  --nt-source /EXTERNAL/body-neurotransmitters-male-cns-v1.0.feather \
  --motif-source /EXTERNAL/PINNED_MOTIF_ARTIFACT \
  --sdk-source /EXTERNAL/scoped-sdk-source.json

.venv/bin/python -m neurofly.dng100_nt_sign_authority \
  --replay /EXTERNAL/38dc667d74acc3c6691b95659f38a1beab2f6208b5c592341f024f61d31bc526 \
  --nt-source /EXTERNAL/body-neurotransmitters-male-cns-v1.0.feather \
  --motif-source /EXTERNAL/PINNED_MOTIF_ARTIFACT
```

The SDK acquisition is a bounded read-only preflight using existing
neuprint-python 0.6.3 credentials. The saved query is reproducible; a changed
source response cannot silently replace the pinned snapshot. No token is saved.
An inaccessible official source fails; there is no synthetic fallback.

## Validation and next scientific step

Focused tests independently fix the eight IDs, fifteen edge counts and a
representative raw confidence, then cover missing/duplicate/conflicting records,
wrong anatomy, invalid/non-finite confidences, nulls, unfamiliar labels,
ground-truth conflicts, altered source identity, reversed/missing edges, absent
provenance, fabricated receptors, model-role substitution and recomputed hashes
with contradictory content. Real official input is mandatory for the integrity
gate and complete semantic replay; it is not substituted by parser fixtures.
An additional independent diagnostic read the official table with pandas and
matched all eight source row positions/fields, then checked every selected edge
against its original structural query row and raw-row hash, without calling the
new extraction or classification helpers. No discrepancy was found.

Required publication gates are the full Python suite, Ruff check/format check,
git diff --check, previous DNg authorities, Planar SHADOW_ONLY semantic
reproduction, five canonical payload hashes and frozen D2.2 bundle verification.
The small source module, policy, reference, tests and this assessment are the
only new repository files; scientific APIs, kernels and frontend are unchanged.

Observed publication gates: 57 focused tests passed; the full canonical Python
suite passed 1,486 tests (one live integration test deselected, two dependency
deprecation warnings) in 882.74 seconds. Ruff check and format --check passed,
as did git diff --check. Both prior DNg100 authority artifacts and the original
Planar SHADOW_ONLY artifact reproduced their pinned semantic identities. All
five canonical payload hashes and VALIDATED_CANONICAL_REPLAY provenance matched;
the frozen D2.2 archive, manifest, inventory and runtime files also verified.
No frozen kernel, source pin, scientific API, frontend or visual asset changed.

The smallest next slice is a **versioned, targeted postsynaptic receptor/functional
evidence audit for IN16B036 → IN17A001 on both T1 sides**. It must establish target
matching, assay resolution and compartment relevance, or retain UNKNOWN. It
does not authorize a transmitter-to-sign guess, signed oscillator or walking
model. These two links close the proposed inhibitory feedback motif; resolving
their evidence gap is scientifically more informative than starting dynamics
with assumed signs.
