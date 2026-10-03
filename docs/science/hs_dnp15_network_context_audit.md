# Phase 26 — HS–DNp15 network-context evidence gate

## Decision and scientific boundary

Stage A: **`RECURRENT_SIGN_OR_DYNAMICS_NOT_IDENTIFIABLE`**.

Phase 26: **`FEEDFORWARD_MOTIF_REMAINS_CURRENT_VALIDATED_BOUNDARY`**.

This is a completed evidence audit, not a failed neural experiment. No Stage B
preregistration, recurrent parameters, stability trials, neural execution or
extended simulation artifact were created. The Phase 25
`BOUNDED_CHEMICAL_FEEDFORWARD_MOTIF` remains unchanged.

The evidence supports **putative excitatory chemical signs**, rather than no
sign information at all. It does not identify the recurrent chemical operator
on the existing signed proxy states, particularly its relation to electrical
interactions and the target-to-source return. The decision is about effective
**dynamics**, not a claim that transmitter evidence is absent.

The gate does not require every gain to be physiologically calibrated: unknown
magnitude alone could be represented by a declared exploratory scale. Here,
however, choosing an arbitrary positive leaky recurrence would also choose an
unestablished proxy-to-chemical-effect transformation and network isolation.
Mathematical stability would not resolve that scientific gap. No such candidate
was run, and no output was inspected to select parameters.

Electrical context is material, but the audit does **not** establish that every
possible partial chemical model requires a calibrated electrical model first.
Consequently the stronger electrical-indispensability gate is not selected.
This finding does not rule out biological chemical recurrence or feedback.

## Repository and immutable authorities

Started clean on `main == origin/main`, committed Phase 25 HEAD
`c7a42427e4a3e9e97c14f9153b0c17d32c79d53c`. Phase 24 and the Phase 23 v1
freeze are committed ancestors. No production, API, frontend, neural kernel,
body plant, historical evidence or canonical artifact is changed.

| Authority | Canonical identity |
| --- | --- |
| v1 status | `1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6` |
| Phase 24 selection | `435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41` |
| Phase 25 preregistration | `371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074` |
| Phase 25 artifact | `2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113` |
| Phase 25 config | `8ffc6263d1a70948d9a69ffa0ff066c9dcbb894d5766b72520e209ace60b452d` |
| Phase 25 result | `35b9bf6bb72f2d92522df25de020cc5e3d369ec0d257997d8cd7746a55e54864` |
| Committed induced-query response | `e8034056dc8e9e17345fc014358993f7f91d4ad69acc6430004bfd9af62a5056` |

Offline loaders rehash the committed authorities and compare identities,
selected routes and omissions. Structural revalidation uses the actual Phase
24 query response for `male-cns:v1.0`, not a mock, morphology-derived topology
or inferred mirrored network. Public annotation enrichment is a separate
read-only query, not replacement of the frozen structural source.

## All eight nodes and all thirteen chemical edges

Laterality is `somaSide` metadata:

| Side | HS identities | Target |
| --- | --- | --- |
| R | 10015 HSN, 10016 HSE, 10023 HSS | 11215 DNp15 |
| L | 10181 HSN, 10034 HSE, 10419 HSS | 12069 DNp15 |

The six Phase 25 active routes remain:

| Source → target | Type/side → type/side | Structural contacts |
| --- | --- | --- |
| 10015 → 11215 | HSN/R → DNp15/R | 138 |
| 10016 → 11215 | HSE/R → DNp15/R | 122 |
| 10023 → 11215 | HSS/R → DNp15/R | 23 |
| 10034 → 12069 | HSE/L → DNp15/L | 78 |
| 10181 → 12069 | HSN/L → DNp15/L | 126 |
| 10419 → 12069 | HSS/L → DNp15/L | 14 |

All seven context edges are structurally verified. “Recurrence” below means a
directed cycle in this bounded chemical graph, not measured physiological
feedback. The reciprocal pairs differ across sides; the one-way tails and left
target return are not synthesized into a symmetric network.

| Candidate edge | Contacts | Structural role | Sign evidence | Timing | Magnitude | Eligibility / limitation |
| --- | --- | --- | --- | --- | --- | --- |
| 10015 HSN/R → 10016 HSE/R | 4 | `SOURCE_SOURCE_RECURRENCE` | NT-inferred putative excitation | `UNKNOWN` | `NOT_IDENTIFIABLE` | Excluded: recurrent operator not identified |
| 10016 HSE/R → 10015 HSN/R | 2 | `SOURCE_SOURCE_RECURRENCE` | NT-inferred putative excitation | `UNKNOWN` | `NOT_IDENTIFIABLE` | Excluded: recurrent operator not identified |
| 10016 HSE/R → 10023 HSS/R | 1 | `SOURCE_SOURCE_FEEDFORWARD` | NT-inferred putative excitation | `UNKNOWN` | `NOT_IDENTIFIABLE` | Excluded: chemical context cannot inherit a recurrence kernel |
| 10034 HSE/L → 10181 HSN/L | 1 | `SOURCE_SOURCE_FEEDFORWARD` | NT-inferred putative excitation | `UNKNOWN` | `NOT_IDENTIFIABLE` | Excluded: chemical context cannot inherit a recurrence kernel |
| 10034 HSE/L → 10419 HSS/L | 1 | `SOURCE_SOURCE_RECURRENCE` | NT-inferred putative excitation | `UNKNOWN` | `NOT_IDENTIFIABLE` | Excluded: recurrent operator not identified |
| 10419 HSS/L → 10034 HSE/L | 2 | `SOURCE_SOURCE_RECURRENCE` | NT-inferred putative excitation | `UNKNOWN` | `NOT_IDENTIFIABLE` | Excluded: recurrent operator not identified |
| 12069 DNp15/L → 10419 HSS/L | 1 | `TARGET_TO_SOURCE_FEEDBACK` | NT-inferred putative excitation | `UNKNOWN` | `NOT_IDENTIFIABLE` | Excluded: functional feedback law not identified |

Machine-readable sign status for each is
`NEUROTRANSMITTER_INFERRED_WITH_SUPPORT`, **not** `DIRECTLY_ESTABLISHED`.
`implemented_sign` is null and implementation eligibility is false for every
candidate. No +1/−1 is assigned to execution. Missing temporal evidence remains
unknown; hypothetical implementation would require new timing assumptions,
not automatic reuse of Phase 25 dt, source tau or target tau as synaptic latency.

No compatible isolated per-edge functional response, chemical delay or
magnitude was located in the bounded evidence set. This is not proof that no
such measurements exist. The small counts are not a rejection threshold or an
efficacy estimate. Every verified edge remains in provenance.

## Primary evidence and transmitter inference

Evidence access and locators are recorded in the JSON. The search is bounded to
the existing HS/DNp15 literature, its relevant original network/coupling papers,
and official MaleCNS annotations; no broad dataset search or author contact.

| Source | What it supports | What it does not establish |
| --- | --- | --- |
| [Schnell et al. 2010](https://pubmed.ncbi.nlm.nih.gov/20089816/) | Identified HSN/HSE/HSS graded horizontal-motion responses | Signs or kernels of the seven chemical contacts |
| [Suver et al. 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5125229/) | HS/DNHS1 association in the committed Phase 24 evidence | Dye coupling is not unitary chemical efficacy; this audit encountered a PMC browser challenge and does not derive a new sign from that inaccessible page |
| [Zhao et al., original preprint underlying eLife reviewed-preprint v1](https://pmc.ncbi.nlm.nih.gov/articles/PMC10614863/) | HS/VS cholinergic predictions, regional ChAT corroboration, qualified excitatory expectation | Exact-body receptor/contact physiology; its ≥10-contact graph does not independently verify these 1–4-contact edges |
| [Raghu et al. 2011](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0019472) | Historical tentative HSS glutamatergic driver labeling | Authors qualify ectopic labeling; not definitive transmitter release or inhibitory sign |
| [Pokusaeva et al. 2024, authentic institutional full text](https://research-explorer.ista.ac.at/download/18444/18459/2024_NatureComm_Pokusaeva.pdf) | HS electrical-network perturbations, HS–HS and HS–descending dye coupling | Individual chemical effects or conductance of the selected contacts |
| [Erginkaya et al. 2025](https://www.nature.com/articles/s41593-025-01948-9) | DNp15/DNHS1 correspondence, broader recurrent/inhibitory network and binocular integration | Its GABAergic LPTCrn findings do not assign HS–HS or DNp15→HSS chemical physiology |

The verified Zhao full text is the **2023 original preprint**; the 2024 eLife
reviewed-preprint DOI is `10.7554/eLife.93659.1`. Its publication/version status
is not silently upgraded. The old HSS driver-label finding is retained as a
qualified caveat, not treated as a definitive contradiction requiring a new
negative model sign. No exact tuning curves or measured bilateral equality are
imported. Soma recordings, calcium kinetics and behavioral effects cannot be
substituted for a chemical-edge kernel.

A live official neuPrint query on 2026-10-02 returned `predictedNt`,
`celltypePredictedNt` and `consensusNt = acetylcholine` for all eight selected
identities. Body prediction confidences range from 0.769 to 0.956. These are
annotation values, **not** edge-sign confidence, release probability or gain.
The exact query, eight rows and response hash are preserved:

`5441908babbc10e4e657805e51624ae11eabb0dfd63e9096c4cee883ab7c24da`.

The [prediction-pipeline source](https://github.com/funkelab/synister_malecns)
documents prediction methodology, not postsynaptic receptor physiology.
Receptor/compartment evidence for these exact contacts was not located. A
putative excitatory sign is defensible as inference, but an identified
presynaptic-release/postsynaptic-response transform is still missing.

## Electrical coupling and feedback special gate

Pokusaeva et al., Fig. 7 and electrophysiology, provide type-level evidence for
HS–HS and HS–descending electrical context, including HSN–DNp15/DNHS1. Their
ShakB perturbation alters lateral coupling and HS passive/response properties;
some descending coupling persists. Dye intensity cannot be imported as
conductance. Coupling is not thereby established as a symmetric numerical
diffusion term: pairwise strength, rectification, effective delay and exact
MaleCNS junction identities remain unidentified here.

Erginkaya et al. distinguish chemical connectivity from electrical context and
explicitly note that their EM datasets do not resolve gap junctions. Broader
H2, bIPS and inhibitory recurrent partners matter to interpretation. That
paper's female-brain datasets and male VNC reconstructions are not an
independent measurement of these exact MaleCNS chemical contacts.

`ConnectsTo` does not encode any of that electrical coupling. None is modelled
or replaced by a hidden “equivalent” chemical term. Any later eligible extension
would remain a **`PARTIAL_CHEMICAL_CONTEXT_MODEL`**, not the complete HS/DNp15
network.

The special return `12069→10419` has verified direction and a cholinergic source
annotation, but no established functional feedback law in this evidence set.
Neither a positive transmitter prediction nor graph-return direction identifies
what the target state should feed back to HSS. It remains separately excluded
as `FEEDBACK_NOT_IDENTIFIABLE`; no right-side counterpart is added.

## Why the existing proxy does not resolve recurrence

Phase 25 source state is a signed dimensionless explanatory proxy, not membrane
voltage, firing rate, calcium or transmitter release. Its target coordinate is
`dnp15_state_eq`, not biological voltage. The frozen six-route proxy transfer
defines a reproducible feedforward experiment; it is not empirical justification
for source-source or target-source transfer.

The missing chain is: signed model proxy → presynaptic chemical activity →
postsynaptic effect at the relevant compartment → altered HS proxy dynamics.
Transmitter annotations constrain a candidate sign, not this entire chain.
Primary network evidence does not isolate chemical and electrical components
for the selected reciprocal pairs. Shared scales, kernels or latency would
therefore introduce additional semantic assumptions, not merely reuse numerical
machinery. No threshold, spikes, yaw, actuator or motor mapping is needed or
permitted to answer this gate.

## Counts, reproducibility and tests

Counts remain structural provenance only for all thirteen routes. Existing
Phase 25 execution uses the six eligible source states, a three-channel mean
and its separately frozen proxy scale; it never reads contact counts as a
numerical multiplier. The new audit test materially mutates feedforward counts
and reproduces the same contributions. No recurrent trajectories exist to
subject to a count-mutation test. Count mutation changes evidence identity,
not numerical physiology.

The evidence record is [hs_dnp15_network_context_audit.json](hs_dnp15_network_context_audit.json):

- schema: `hs_dnp15_network_context_audit_v1`;
- canonical inner-record SHA-256/ID:
  `04116360164262de5a2572f33e12cc90351869567c3202811807be576f1d03be`;
- canonical inner JSON: 30,092 bytes; stored readable wrapper: 39,416 bytes;
- no runtime dependency, raw-data paths, source trace values or simulation payload.

Tests rehash the record and unchanged authorities, reproduce query hashes,
validate all eight nodes/thirteen edges, metadata sides, seven role/sign/timing
records, NT provenance, feedback/electrical exclusion and absence of invented
mirror edges. Mutated activation, sign, evidence status, authority, gate,
feedback or electrical status fails the pinned canonical-identity check.
These are evidence integrity tests, not an invented recurrent replay API.

Historical offline numerical replays are run before the audit and again at
closure: 7O, 8C, 13B, corrected 16, 18 and 25. Phase 25 remains
`2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113`.
First replay round wall times: 5.737, 3.187, 6.635, 15.042, 16.339 and 0.140 s,
respectively. No new neural execution/artifact/performance comparison is
reported, because Stage B did not occur.

## Claim budget and next boundary

Allowed: verified chemical network context; qualified transmitter-based sign
inference; documented recurrent-operator uncertainty; unchanged deterministic
Phase 25 neural-only validation. Forbidden: validated recurrent physiology,
complete HS/DNp15 or optomotor network, calibrated electrical coupling,
contact-count efficacy, steering, yaw command or navigation. Missing evidence
is not proof of absent biological recurrence.

Exactly one next bounded action: **audit public chemical-isolating or
edge-resolved HS–HS physiological evidence for the verified HSN/HSE reciprocal
pair (10015/10016 at neuron-type level), to specify a chemical observation/transfer
operator distinct from electrical coupling**. No author contact, neural
simulation, model fitting or motor/body implementation is part of that action.

## Closure verification

Fourteen focused audit tests passed; the combined audit/Phase 25/selection run
passed 42 tests. Full Python regression: **1,077 passed**, one existing
deselection and two existing dependency deprecation warnings, in 535.02 s.
All **53 frontend tests**, lint, typecheck and production build passed. Python
Ruff check/format and Git diff checks passed. Build-generated Next.js type
imports were restored to their initial form and typecheck passed again; no
frontend source change remains.

The closing replay round passed unchanged: 7O 5.665 s, 8C 3.130 s, 13B
6.487 s, corrected 16 15.107 s, 18 16.322 s and 25 0.140 s. V1 and Phase 24
manifests were independently rehashed again, and Phase 25 preregistration,
config/result and artifact identities remain unchanged. No new scientific
artifact or raw dataset was generated/downloaded. Existing artifacts remain
Git-ignored. Only this document, its JSON evidence record, the focused audit
test and the minimal Project Context addition change. No commit or push.

Phase 26 **PASS** is an evidence-audit completion, not recurrent-model
validation; Stage B remains prohibited by the recorded gate.
