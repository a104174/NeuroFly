# DNg100 T1 postsynaptic evidence V1

## Fixed evidence policy

Experiment: DNG100_T1_POSTSYNAPTIC_EVIDENCE_V1. Evidence contract:
dng100_t1_postsynaptic_evidence_v1. Policy was written after read-only source
preflight and before final evidence classification. No independently verified
prospective timestamp is claimed.

Primary scope is exclusively 801884/IN16B036_L -> 800173/IN17A001_L (526
structural synapses) and 803183/IN16B036_R -> 800288/IN17A001_R (439), both T1.
MaleCNS v1.0 UUID 4b2087c0fbe046bfaf0d60bc970e3e5d and all published structural
and transmitter authorities remain frozen. No broad graph extraction.

Evidence levels are separate:

| Level | Required resolution | Permitted interpretation |
| --- | --- | --- |
| A | Identified pre/post pair, direct physiological response, independently supported correspondence to selected male adult T1 cell types | Potential connection-sign support, limited to measured preparation/state |
| B | Experimentally identified target neuron with controlled receptor expression assay | Target receptor evidence; sign still UNKNOWN without applicable pair physiology |
| C | Explicitly validated matching target cell type with receptor assay | Type-level receptor context; not individual EM body/synapse evidence |
| D | Other fly/VNC populations, hemilineages, unmatched clusters or preparations | General biological context only |
| E | Assigned simulation signs, model effects, fitted/selected parameters | Model hypothesis only |
| F | No applicable evidence identified within declared search | UNKNOWN; not biological absence |

Default functional_sign_status=UNKNOWN. A supported sign requires Level A
matched adult T1 pair evidence, demonstrably direct causal response, controls
excluding indirect network effects, documented voltage/current effect and
explicit dataset/cell-type correspondence. Receptor expression alone cannot
establish the sign or compartment of these contacts. Context dependence requires
measured dependence on conditions, not speculation about chloride potential.

Confidence is qualitative evidence resolution, not a newly invented numeric
score. Missing sex/segment/type mapping lowers applicability; it is never filled
from another connectome. Conflicting findings are preserved. A publication's
letters E/I, presynaptic glutamate, transcript detection alone or structural
counts cannot supply functional sign. No conductance, gain, delay or reversal
potential is assigned.

Discovery is timeboxed to a focused set: official MaleCNS annotations/property
schemas; revised Pugliese full text and original author manuscript if necessary;
primary adult VNC transcriptomic/receptor resources; exact IN17A001/IN16B036
physiology/receptor queries; and selected primary glutamate physiology controls.
No broad omics or synapse download. At most eight directly relevant publications
will be assessed; newly encountered unrelated pathways will not be extracted.

External sources record version/DOI/URL, retrieval date, method, preparation,
sex/stage/segment, target correspondence and evidence/compartment resolution.
Same type spelling or a genetic driver is insufficient without anatomical
matching. A verified type mapping transfers only the stated type-level finding.

Publication requires both original edges and glutamate source verified, useful
recoverable evidence records, honest resolution/uncertainty and unchanged frozen
science. Documentation-only work uses source/integrity and diff checks rather
than rerunning an unchanged full scientific suite.

## Decision and exact authority

**DNG100_T1_POSTSYNAPTIC_SIGNS_UNKNOWN**, independently for both sides. No
applicable Level A, B or C evidence was identified in this bounded search.
This is absence of identified evidence, not evidence that the receptors are absent.

Initial main and remote main were ffad7a4ee077bc3fa5e1b8163875ae23451f80f3,
with a clean worktree. Published authority was loaded through
`dng100_nt_sign_authority.load_artifact`, including semantic reproduction against
its genuine source and structural authority. The new assessment does not revise
that artifact or any prior classification.

| Side | Directed MaleCNS T1 edge | Structural count | Presynaptic authority | Postsynaptic receptor / physiological sign |
| --- | --- | ---: | --- | --- |
| L | 801884 / IN16B036 -> 800173 / IN17A001 | 526 | Glutamate | Unresolved / UNKNOWN |
| R | 803183 / IN16B036 -> 800288 / IN17A001 | 439 | Glutamate | Unresolved / UNKNOWN |

The L edge has 525 postsynaptic contacts in LegNp(T1)(L) and one
VNC-unspecified contact; the R edge has 439 in LegNp(T1)(R). Counts are
structural evidence, not functional efficacy. Both neurons of each pair are
Traced/Reviewed, T1, ipsilateral VNC intrinsic types in the pinned annotations.

Source identities (scoped authorities, not full-connectome checksums):

- Annotations: 2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2.
- Recurrent snapshot: def753409faa5daa7932ad5c256c644b2b426f44c053b2c40a5b89a17d6b024e.
- Recurrent logical artifact: baae20599455c2a7acb3271e6eeb6b73326d17185b6e705022b74818ff0f8934.
- Official NT Feather: 95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621.
- NT logical artifact: 38dc667d74acc3c6691b95659f38a1beab2f6208b5c592341f024f61d31bc526.

## Official annotation and property discovery

The pinned annotations have null `receptorType` for all four target neurons.
Elsewhere, that field contains sensory receptor labels; its name cannot justify
interpreting it as a postsynaptic glutamate-receptor measurement. The published
NT table aggregates transmitter predictions/consensus; it does not measure target
receptors. Its `ground_truth` associations are cell-type evidence, not recordings
from these individual EM bodies.

A bounded official neuPrint query inspected property keys on synapses belonging
only to the two IN17A001 bodies:

```cypher
MATCH (n:Neuron)-[:Contains]->(:SynapseSet)-[:Contains]->(s:Synapse)
WHERE n.bodyId IN [800173,800288]
RETURN DISTINCT keys(s) AS properties
```

Returned keys include geometry, compartment, ROI, confidence and, for some
presynaptic records, `nt*Prob` transmitter predictions. No receptor-expression,
localization or physiological-response property was returned. This describes
exposed properties in the selected source, not molecular absence. No full
synapse table was downloaded. The evidence record preserves the query and
small response with its hash.

## Primary evidence assessed

Retrieval date: 2026-10-13. The small XML/PDF documents were read outside Git;
no omics dataset or new connectome was imported. Exact source versions and
retrieved-file hashes are recorded in the companion JSON where available.

| Source | Method and preparation | Target correspondence | Level / what transfers |
| --- | --- | --- | --- |
| Pugliese et al., revised 30 April 2026 preprint, DOI [10.1101/2025.09.12.675944](https://doi.org/10.1101/2025.09.12.675944); [full XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13142387/fullTextXML) | Connectome simulations across male MANC/MaleCNS and female FANC/BANC; behavioral activation of descending neurons | Anatomical type correspondence; not a paired I1/E1 physiological assay | E: model-sign hypothesis |
| Allen et al., 2020, eLife 9:e54074, DOI [10.7554/eLife.54074](https://doi.org/10.7554/eLife.54074); [full XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7173974/fullTextXML) | Adult VNC single-cell RNA sequencing, males and females aged five days | Transcriptomic clusters; no verified IN17A001-to-receptor-cluster mapping established here | D: expression context |
| Fan, Tian and Han, 2025, Neuroscience Bulletin 41:1729–1742, DOI [10.1007/s12264-025-01397-1](https://link.springer.com/article/10.1007/s12264-025-01397-1) | Genetic GluClα depletion, calcium imaging after glutamate application; adult 23E10+ VNC cells | T3 sleep-related population, not matched IN17A001 T1 | D: receptor-function context |

Allen et al. report broad GluClα transcription and enrichment in cluster 103.
The available result does not establish IN17A001 expression, protein localization
or the response of either selected synapse. Hemilineage, transcriptomic cluster
and concrete cell type are different levels of identity.

Fan et al. identify GluClα-dependent inhibitory input in another VNC population.
Behavioral assays use males aged three to five days; imaging uses dissected
brain/VNC of that age, with imaging sex not separately specified in the inspected
methods. Application near cell bodies and calcium changes are not a paired
IN16B036-to-IN17A001 recording. No mapping of their T3 cells to these T1 targets
was established. Their result supplies context, not our connection signs.

Exact-type searches combined IN17A001/IN16B036 with receptor, GluCl and
physiology terms. They did not identify an applicable target assay. A newer
Sapkal et al. preprint (10.64898/2026.04.29.721658v2) appeared in indexed
walking-circuit results, but complete text was not recoverably inspected here;
no receptor or sign conclusion is based on it. Some publisher/PMC routes
returned browser challenges. The two full XML sources above were recovered
through Europe PMC. An attempted Liu/Wilson 2013 full-text retrieval failed;
that paper is not used as target evidence. These access and search limitations
prevent an exhaustive claim about all published or unpublished experiments.

GluClα, ionotropic and metabotropic glutamate receptors are candidate receptor
classes, not demonstrated properties of IN17A001. No selected-cell expression,
compartment localization, chloride reversal potential, current direction,
conductance or kinetics is assigned for any candidate.

## Pugliese interpretation and cross-dataset correspondence

The revised methods assign positive model weights to predicted cholinergic
sources and negative weights to predicted GABAergic/glutamatergic sources.
MaleCNS uses `consensusNt`; MANC uses `predictedNt`. Consequently, I1 inhibition
is a computational sign rule, not a receptor assay on these contacts.
Gain/threshold scales and other dynamics parameters are selected model values;
no pair-specific physiological calibration is established. The behavioral
experiments activate descending neurons in female, dewinged, decapitated,
tethered adults. They do not measure IN16B036 -> IN17A001 transmission.
The paper itself identifies direct electrophysiology as necessary further work.
The inspected revision remains a preprint.

The pinned MaleCNS annotations provide explicit curated `mancBodyid` matches:

| MaleCNS body | Type | Annotated MANC counterpart |
| ---: | --- | ---: |
| 800173 | IN17A001 L | 10707 |
| 800288 | IN17A001 R | 10690 |
| 801884 | IN16B036 L | 13905 |
| 803183 | IN16B036 R | 14096 |

The original author manuscript identifies MANC 10707/13905 as its left E1/I1
cells. This is useful anatomical correspondence, not an experimental sign
measurement or interchangeable body identity. No FANC, BANC, driver-line or
transcriptomic-cluster mapping is manufactured. A simulated matched type still
remains Level E; the letter I does not upgrade it to Level A.

## Evidence contract, gates and limitations

`dng100_t1_postsynaptic_evidence.json` follows the repository's small evidence
review convention. It contains the fixed policy, original authority references,
two separate edge assessments, raw inherited transmitter evidence, source
resolution, curated anatomical mappings and recoverable references.
`transmitter_prediction`, `postsynaptic_receptor_evidence`,
`physiological_sign_evidence` and `functional_sign_status` remain separate.
The review ID is SHA-256 of sorted compact ASCII JSON of the complete `review`
object; it is not the checksum of the formatted file. This is an evidence review,
not a new simulation artifact, an extractor or a receptor database.

Applicable gates are published-authority semantic validation, review content and
hash consistency, frozen replay checks and `git diff --check`. No algorithm,
Python code, tests or dependency changed, so an unchanged full Python suite and
frontend build are not rerun. Search-negative conclusions cannot be tested by
unit tests or upgraded by ordinary code correctness.

No new biological or numerical assumption is introduced. The evidence-resolution
policy is a conservative audit decision. UNKNOWN does not contradict glutamate
consensus or the recurrent structure; it prevents unjustified transfer of a
simulation sign rule. Existing kernels, authority outputs, canonical scenarios,
SHADOW_ONLY poses, APIs, frontend and providers remain unchanged.

## One smallest next experiment

Preregister an **identified adult T1 IN16B036 -> IN17A001 paired physiological
assay**, rather than another broad graph audit. First require experimentally
usable cell identification with morphology matched to the curated types; if
that cannot be achieved, stop rather than substitute a broad driver population.
Activate/record the presynaptic cell and measure postsynaptic voltage/current,
with sham stimulation and controls distinguishing direct transmission from
network effects. Record side, sex, preparation, state and anatomical matching.
Assess left and right independently. Receptor perturbation/localization may
then explain a measured effect, but must not supply an assumed effect in advance.
A reproducible direct response with documented polarity and suitable controls
could support Level A in that preparation; no response or conflicting effects
leave the claim unresolved. No magnitude, gain or latency threshold is invented
here. This requires experimental collaborators and is not claimed available in
NeuroFly. It does not authorize dynamics, oscillations, gait or movement.
