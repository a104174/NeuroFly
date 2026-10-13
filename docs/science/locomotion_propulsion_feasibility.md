# Locomotion propulsion feasibility — scientific consolidation

Assessment date: 2026-10-13. Source baseline: `main`,
`8b050b5f5bda9f3418a594a8ddd60a2b4d6ea734`.

## Executive decision

**PROPULSION_UPSTREAM_VALIDATION_REQUIRED.** No current NeuroFly circuit has a
validated mapping to sustained physical forward walking. The smallest meaningful
next implementation is one bounded **MaleCNS DNg100/BDN2 walking-route authority
audit**, with no neural simulation, motor application or body movement. Functional
walking evidence and a small published computational CPG candidate justify this
target; neither supplies ready-to-use MaleCNS dynamics or physical propulsion.

This document is a feasibility assessment, not an approved controller specification.
Planar Steering remains SHADOW_ONLY. Its independent review passed with limits:
two descriptors do not identify general planar motion; three HS states per side
are identical; sham/readout disconnection do not establish anatomical necessity;
the geometric retina and angular gain are uncalibrated; preregistration chronology
is not independently verified. No heading feedback or forward drive is added here.

## Actual implementation inventory

| Capability and source | Authority and current output | Propulsion boundary |
| --- | --- | --- |
| `hs_dnp15_neural_validation.py:40-140`, `exploratory_course_control.py:129-172` | Six MaleCNS HS inputs, DNp15 11215/R and 12069/L, six uniform ipsilateral chemical routes; signed source and target filters. Counts are source evidence, not gains. | No leg/VNC motor generator, forward channel or physiological velocity. |
| `planar_motion_observation.py:161-250`, `planar_steering_validation.py:175-232` | Engineering landmark bearing changes from prescribed poses; unchanged HS/DNp15 states and differential yaw proposal. | Readout SHADOW_ONLY; poses are immutable engineering inputs; no actuation. |
| `motor_pathway.py:321-378,641-690`, `sensory_dnp01_motor_adapter.py:158-225` | Same-run DNp01 events can be routed by identity to TTMn. DNp01 10001/R and 10010/L; TTMn 800146/R and 804642/L. Dimensionless TTMn event integrator: decay 10 ms, increment 0.25, both model assumptions. | Escape-related pathway, not sustained walking. Source events must actually exist; canonical scenarios do not supply a nonzero walking output. |
| `motor_neural_contract.py:49-217`, `synthetic_parallel_motor_branches.py`, `docs/science/motor_neuron_output_source_readiness.md` | Pinned 16-neuron/18-chemical-edge GF/TTMn/PSI/DLMn authority. PSI 802401/L and 903327/R; ten DLMn. DLM branch records graph-path receipts, not spikes; synthetic fixtures exercise interfaces. | No validated PSI/DLMn dynamics or identity-resolved leg-driving signal. Chemical edges omit electrical modality; counts are not efficacy. |
| `motor_neuron_muscle_contract.py`, `synthetic_motor_target_dispatch.py` | Literature-qualified muscle class/group associations; synthetic output-event dispatch. | Peripheral muscle targets are not MaleCNS central synapses; receipts are not muscle activation, contraction or force. |
| `muscle_activation.py:31-117`, `ttm_actuator.py:84-135` | Synthetic-source passive electrical deviations are rectified, normalized and capped into a dimensionless activation proxy, then routed to TTM actuator channels. | No physiological neural-to-muscle calibration, force, gait or ground contact. |
| `planar_body_plant.py:24-61,116-130,150-174` | Engineering common-mode commands produce fixed-heading model-space displacement, downstream of persisted synthetic actuator fixtures. | Explicitly not connectome-driven walking; no physical calibration or turning. |
| `scenario_playback_api.py:662-710`, frozen Course/world artifact loaders | Five replay-validated canonical scenarios; Course contains abstract orientation, translation NOT_MODELLED. | Frozen outputs must not be relabeled as new locomotion; new results require a separate versioned identity. |

No `DNp09`, `DNg100`, `BDN2`, `BPN` or `oDN1` dynamics/selected route implementation
was found in `src/` or `tests/`. This is absence from the current implemented
selection, not absence from the complete MaleCNS connectome.

## Primary biological evidence

Sources were checked directly on 2026-10-13. Publisher/PMC challenges prevented
some full-text requests; accessible author manuscripts were inspected in memory
using the existing PDF text tool. No paper, dataset or credentials were added to
Git. Structural, functional, causal and computational findings remain distinct.

| Primary source | Dataset, sex, stage and preparation | Finding and intervention | Limit for NeuroFly |
| --- | --- | --- | --- |
| Bidaye et al., *Neuron* 108, 469-485.e8 (2020), [10.1016/j.neuron.2020.07.032](https://doi.org/10.1016/j.neuron.2020.07.032), [accessible author manuscript](https://escholarship.org/content/qt3xn046hw/qt3xn046hw_noSplash_d8d44e8de25c2f9f70699bb6ba98b1b0.pdf) | Adult Drosophila; free-walking activation includes grooming/coupled females, male courtship; male tethered-ball imaging. Female brain EM and male functional measurements are distinct. | Optogenetic P9 initiates forward walking with ipsilateral turning; BPN activation initiates straight walking, with activity/silencing evidence for fast prolonged bouts. Functional and causal context-specific evidence. | BPN is a higher brain population, not a forward-speed scalar. No exact MaleCNS dynamical calibration. |
| Sapkal et al., *Nature* 634, 191-200 (2024), [10.1038/s41586-024-07854-7](https://www.nature.com/articles/s41586-024-07854-7), Fig. 3 and Methods | Adult Drosophila; untethered activation uses 6-9-day females; BDN2 imaging uses tethered females, separate male halt-kinematics assays. Brain/VNC EM and manipulation datasets are not MaleCNS v1.0. | Activation of oDN1/BDN2 and severed descending axons evokes forward walking. BDN2 inhibition reduces forward speed; calcium correlates with forward rather than angular velocity. | Causal walking-promotion evidence; no instantaneous activity-to-speed transfer function or body-ID calibrated force. |
| Braun et al., *Nature* 630, 686-694 (2024), [10.1038/s41586-024-07523-9](https://doi.org/10.1038/s41586-024-07523-9), [published PDF](https://d-nb.info/1341591042/34) | Adult Drosophila, female brain/VNC preparation; tethered behavioural/optogenetic population recordings and intact versus decapitated manipulation; FlyWire brain connectivity. | DNp09/P9 recruits a descending population; complete behaviours can require that population instead of isolated VNC output. Causal network-level evidence. | A single DNp09-to-speed shortcut omits experimentally relevant partners. Female network IDs cannot be copied to MaleCNS. |
| Cheong et al., *eLife*, reviewed analysis (2025), [10.7554/eLife.96084.2](https://doi.org/10.7554/eLife.96084.2), [official Janelia record](https://www.janelia.org/publication/transforming-descending-input-into-motor-output-an-analysis-of-the-drosophila-male-adult) | MANC, adult male VNC EM, not MaleCNS; structural circuit analysis, no walking animal actuation in this analysis. | DN-to-MN contacts are uncommon; intermediary networks and motor-system organization support hypotheses about walking/flight pathways. | Structural hypotheses do not identify gains, rhythms, muscle forces or physical speed. |
| Pugliese et al., *bioRxiv*, initial 2025 preprint, indexed revision 2026-04-30, [10.1101/2025.09.12.675944](https://doi.org/10.1101/2025.09.12.675944), [revision metadata/abstract](https://pubmed.ncbi.nlm.nih.gov/42094485/), [updated methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC13142387/), [author manuscript](https://faculty.washington.edu/tuthill/docs/Pugliese_cpg_2025.pdf) | Original manuscript: male MANC/female FANC adult VNC models and headless spherical-treadmill optogenetics. Updated abstract/methods additionally report male CNS and female BANC; exact version/body-ID crosswalk remains to audit. Experimental sex not independently resolved here. | Computational DNg100 activation and pruning isolate a two-excitatory/one-inhibitory rhythm motif; original E1/E2/I1 candidates include IN17A001, INXXX466, IN16B036. DNg100 is identified as BDN2. Motor-rhythm necessity is computational; manipulation measures stepping/velocity. | Preprint, not verified peer-reviewed physiological necessity of the complete motif. Recurrent model assumptions differ from current frozen HS kernels. No direct import of weights or cross-dataset IDs. |
| Lobato-Rios et al., *Nature Methods* 19, 620-627 (2022), [10.1038/s41592-022-01466-7](https://doi.org/10.1038/s41592-022-01466-7), [author manuscript](https://gizemozd.github.io/assets/pdf/2022_nmeth_neuromechfly.pdf) | Adult female micro-CT body; measured tethered leg kinematics and neuromechanical simulations. | Replaying kinematics permits biomechanical force/contact inference; separate optimized controller/muscle models generate walking. | A biomechanical demonstration, not a MaleCNS-derived motor controller. No engine or parameter import is proposed. |

The existing GF evidence boundary is also consistent with primary adult flight
motor research: Hürkey et al., *Nature* 618, 118-125 (2023),
[10.1038/s41586-023-06099-0](https://www.nature.com/articles/s41586-023-06099-0),
studies flight motor coordination, not sustained terrestrial propulsion. Current
TTMn/DLMn contracts explicitly retain escape/flight interpretation and unresolved
exact-body neuromuscular calibration.

## Verified local source identities and missing routes

The official [MaleCNS v1.0 annotation source](https://male-cns.janelia.org/download/)
was read in memory (14,483,314 bytes). SHA-256:
`2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`,
equal to the historical pin in `motor_neural_contract.py:33-35`.

| Candidate | Verified type/side annotations | Missing evidence |
| --- | --- | --- |
| DNp09/P9 | `10783/DNp09_L`, `11177/DNp09_R`; Traced, Roughly traced | No pinned walking recruitment or VNC route graph in NeuroFly. P9 class naming is supported by Sapkal; functional identity in another specimen is not an exact-cell recording. |
| DNg100/BDN2 | `10045/DNg100_L`, `10056/DNg100_R`; Traced, Prelim Roughly traced | BDN2 class correspondence is explicit in the Pugliese primary manuscript. Current NeuroFly lacks exact downstream routes, functional parameters and muscle calibration. Annotation status requires scrutiny. |
| Putative front-leg CPG classes | Left T1 annotation candidates: `800173/IN17A001`, `800863/INXXX466`, `801884/IN16B036`; Right T1: `800288`, `903216`, `803183`, respectively; Reviewed | Class/neuromere matches only. Multiple homologues exist across legs; these IDs are not certified as a dynamically sufficient MaleCNS motif by this audit. Edges and literature correspondence require verification. |

No type-string matches for BPN, BDN2 or oDN1 were returned by that bounded
annotation search. That does not establish biological absence: aliases differ.
The DNg100/BDN2 correspondence has a literature source; other mappings remain
unresolved here. A `mancBodyid`/alias or morphology match must itself be inspected,
versioned and qualified before it can support a cross-dataset assertion.

The pinned existing motor authority was replayed successfully:
`a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c`
(16 nodes, 18 chemical edges, canonical source and manifest valid). This validates
the escape-related source contract, not the new walking candidates. The full
MaleCNS connection graph is approximately 1.1 GB; it was not downloaded. No
candidate walking edges or neurotransmitter predictions were fabricated.

The production sensory-to-motor adapter is not the synthetic fixture pipeline.
The recorded Phase 7O reference has no DNp01 spikes, and hence no TTMn input or
PSI/DLMn receipt under that condition (`motor_neuron_muscle_boundary_readiness.md`).
Nonzero synthetic dispatch/activation/plant examples do not demonstrate an intact
sensory-driven walking output.

## Motor-model alternatives and current planar plant

| Alternative | Evidence/reuse | Assumptions, complexity and readiness |
| --- | --- | --- |
| A. Prescribed engineering propulsion | Existing plant integration/replay fixtures are reusable numerical checks. | Low cost, identifiable as an imposed input. Does not demonstrate neural propulsion; repeating a constant speed is not the next missing scientific gate. |
| B. Neural modulation of a separately declared walking generator | DNg100/BDN2 walking-promotion evidence and candidate CPG structure justify upstream investigation. Existing hashing/configuration can be reused. | Requires exact circuit selection, recurrent dynamics, motor/muscle and contact mapping, physical units and calibration. No current implemented controller; preferred research direction only after authority validation. |
| C. Explicit VNC motor/gait/biomechanical model | Primary CPG and neuromechanics studies provide tractable examples. | High cost: bilateral/segmental coordination, proprioception, neural-to-muscle gains, morphology, force/contact and friction. Rhythms need not create net translation. Not ready for first body integration. |
| D. No ready implemented route | Present HS steering and GF escape boundaries are insufficient for sustained walking. | This is the current execution decision, with a supported upstream candidate rather than a claim that biology has no pathway. |

The plant calculates `v = g*(a_R+a_L)/2`, `x[n+1]=x[n]`,
`z[n+1]=z[n]+dt*v[n]`, with left-boundary command held over the interval.
`g=1 world_eq/ms` is a normalization assumption. No mass, force, inertia, limb
stance, ground reaction, heading integration or sensory inference is present.
Its synthetic TTM actuator ancestry cannot be silently converted into sustained
walking. A real motor generator and physical calibration remain absent.

The required future chain is: justified sensory/state input -> selected neural
response -> explicit locomotor generator -> motor/muscle action -> limb/contact
mechanics -> body state -> justified sensory feedback. Current landmark geometry
tests only a bounded visual descriptor; it neither senses chamber walls nor
replaces proprioceptive/contact feedback. Arena scale 0.30 and acrylic dimensions
are presentation conventions, never physical body or world parameters.

## Exactly one next implementation slice

**Proposed identity:** `DNG100_WALKING_ROUTE_AUTHORITY_V1` (future, not implemented).
Objective: build and validate a small recoverable MaleCNS structural evidence
contract for DNg100 and its candidate front-leg premotor/motor boundary.

1. **Hypothesis:** the pinned MaleCNS snapshot supports an unambiguous same-dataset
   DNg100-to-premotor-to-front-leg-motor selection consistent with the published
   class-level walking/CPG candidate. A null or ambiguous selection is a valid NO-GO.
2. **Dependencies/data:** official pinned annotations; bounded official directed
   connectivity responses; transmitter predictions with independent provenance;
   paper/version/supplementary identity definitions. Reuse existing source-manifest,
   canonical hashing and offline source-replay patterns, not the HS route inventory.
3. **Selection:** start with DNg100 10045/L and 10056/R; inspect the named T1 class
   candidates above and their front-leg MN outputs, preserving laterality and
   alternative homologues. Preregister exact query scope/ROI/quality policies and
   exclusions before selecting on model outcomes. Include candidate recurrence;
   do not require a physiologically complete pathway to be feedforward.
4. **Input contract:** version, experiment identity, dataset/version, source URLs,
   raw/canonical hashes, literal query definitions, requested IDs/classes/neuromeres,
   quality policy, random policy NONE and software identity. No invented timestep:
   this stage has no neural dynamics or simulation time.
5. **Output/evidence contract:** complete recoverable identity rows, raw directed
   chemical counts and ROI evidence, transmitter predictions with their confidence,
   missing/excluded routes, morphology/crosswalk evidence and unresolved fields.
   Output classification `STRUCTURAL_AUTHORITY_ONLY`; speed/force/dynamics remain
   NOT_DEFINED. No simulation telemetry or walking replay is generated.
6. **Controls/tests:** repeat source replay; left/right and T1/T2/T3 disambiguation;
   raw-versus-normalized query parity; absent and reversed-edge tests; duplicate,
   wrong-dataset/side, ambiguous homologue and rehashed-tampering rejection. Frozen
   GF and HS inventories remain unchanged. Reciprocity/asymmetry is reported,
   never normalized to force bilateral equivalence.
7. **Causal limits:** structural graphs cannot test physiological necessity. No
   sham neural response or route-ablation outcome is fabricated in this stage.
   A later separately registered dynamical experiment would need identical input
   schedules with intact, disconnected-route, sham and zero-drive controls, and
   outputs retained as neural/model quantities before any body application.
8. **Reproducibility:** persist only the small recoverable source contract and
   manifest under the established external/ignored scientific artifact policy;
   source/test/docs remain small. Deterministic offline replay must reproduce all
   records and IDs without a live service. Do not add raw connectome tables to Git.
9. **Measurable gate:** every selected ID resolves uniquely in the pinned dataset;
   every retained edge is recoverable from the recorded query, with counts/ROIs
   unchanged; class crosswalk assertions have explicit evidence; all unverified
   identities/parameters remain unresolved; semantic replay and canonical gates
   pass. This qualifies a bounded candidate for subsequent neural validation only.
10. **Stop:** no authoritative connectivity access, unresolved homologue mapping,
    inadequate tracing, contradictory paper/annotation correspondence, missing
    transmitter information essential to a claimed sign, source drift or hashes
    failing. Stop rather than import MANC IDs, choose convenient weights, claim
    absent data are zero or retune the existing kernels.

Future authorized scope should be an isolated source extractor/validator, tests,
small authority records and assessment. Non-goals: neural controller, CPG port,
forward speed, physical body plant, heading feedback, new API, frontend, deployment
or any canonical scenario modification. Report source/manifest IDs, complete
selection and exclusions, controls, uncertainties and a GO/NO-GO for a subsequent
neural-only validation. Canonical commands are `.venv/bin/python -m pytest`,
`.venv/bin/python -m ruff check .`, `.venv/bin/python -m ruff format --check .`,
and `git diff --check`; preserve frozen replay hashes. No frontend gates for this
isolated source contract.

Afterward, NeuroFly could demonstrate an auditable walking-related structural
selection. It still could not demonstrate motor rhythms, forward propulsion,
closed-loop locomotion or biological calibration. This is the smallest meaningful
step because the exact new route authority is absent now and is a prerequisite
for testing any proposed neural motor contribution.

## Remaining uncertainty

- DNg100 identity evidence is stronger than current tracing quality and does not
  certify every selected VNC edge. Primary physiological results concern other
  specimens and preparations; preprint revisions require version-specific review.
- Published rhythmicity and simulated necessity do not establish a physical speed
  law, a sufficient six-leg gait or empirical necessity in this MaleCNS individual.
- Gain/sign assignment, electrical modality, proprioception, muscle dynamics and
  contact mechanics are independent missing contracts. Synaptic counts cannot
  identify them. Seeded variability is not learning or autonomous intention.
- No source claims full biological emulation for the implemented NeuroFly pipeline.
  A future stationary or negative result must remain publishable and interpretable.
