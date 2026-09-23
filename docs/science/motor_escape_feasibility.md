# Phase 6B — bounded motor / escape-pathway feasibility assessment

**Status: PASS — bounded literature and MaleCNS v1.0 audit complete.** This
phase is an evidence assessment only. It adds no neural simulation, motor
state, body mechanics, or behavior. The recommendation for Phase 6C is a
two-body DNp01→TTMn neural-state extension only. That scope is not a complete
short-mode takeoff model.

## Decision and scope

The evidence supports a minimal downstream model experiment ending at TTMn
state:

```text
existing looming / LC4-LPLC2 type-level model / DNp01 point-neuron state
                         ↓ persisted DNp01 body-specific event/state
          explicit DNp01→TTMn mixed-connection evidence
                         ↓
                TTMn model state only
```

MaleCNS v1.0 confirms chemical `ConnectsTo` edges from the two DNp01/GF
bodies to two ipsilateral TTMn bodies. Primary literature independently
describes a mixed chemical/electrical GF→TTMn connection and fast TTM motor
output. MaleCNS does not provide an electrical-coupling adjacency or its
conductance. The chemical contact count must not be substituted for that
missing coupling or called a physiological gain.

TTMn-only is a bounded motor-neuron experiment, not a sufficient basis to say
“short-mode takeoff,” “escape,” or “jump.” The complete canonical short-mode
output also involves GF→PSI→DLMn and likely other downstream cells. The
evidence supports a later separate PSI/DLMn extension, but not expanding the
smallest next implementation to that branch.

## Repository and implementation audit

The audit began on clean `main`, HEAD
`5506557b7c8d9dd3f51b4432804560d3d5a85a1c`, aligned with `origin/main`.
Phase 6A and the temporal-boundary fix are committed. `git diff --check` was
clean before research began.

The local `CircuitContract` is the offline 313-body
`looming_giant_fiber_v1`, MaleCNS `male-cns:v1.0` slice: LC4, LPLC2, and
DNp01 only; its 20,607 edges are chemical `ConnectsTo` records and its
`structural_weight` is the source contact count. It verifies the DNp01
identities and contains the 311 LC4/LPLC2→DNp01 edges used by the current
simulation, but contains no TTMn, PSI, DLMn, or downstream edge. This is a
selection boundary, not evidence of absence elsewhere in MaleCNS.

The existing simulator is deterministic `lif_filtered_synapse/phase2b_v1`;
its active graph ends at DNp01. Current results persist DNp01 body-keyed
membrane and filtered-synaptic state plus body/node-index/step-keyed spike
events. The experiment artifact is `NOT_EVALUATED`. Phase 6A joins those
states to validated DNp01 identities; it does not supply motor state. There
is no current downstream neural model or body adapter.

The real Phase 6A experiment remains
`63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656`.
Its persisted DNp01 spike events include body 10010 at step 453 (45.3 ms),
body 10001 at step 693 (69.3 ms), and body 10010 at step 693 (69.3 ms).
Those are NeuroFly model results, not MaleCNS activity or observed takeoffs.

Relevant current boundaries are documented in
[`circuit_contract.md`](circuit_contract.md),
[`neural_simulation_core.md`](neural_simulation_core.md),
[`activity_structure_mapping.md`](../architecture/activity_structure_mapping.md),
and [`experiment_artifact_contract.md`](experiment_artifact_contract.md).
No tracked source, simulation configuration, artifact, or test was changed
for this audit.

## Evidence layers

These layers are deliberately not collapsed:

1. **Documented biology:** published anatomy, physiology, and behavior of the
   Drosophila Giant Fiber System (GFS), measured in specific preparations.
2. **MaleCNS v1.0 source evidence:** current body identities and chemical
   `ConnectsTo` edges verified from the official annotation table and a
   bounded live neuPrint query.
3. **NeuroFly modeling assumptions:** LIF state, electrical/chemical
   transmission dynamics, any gain, delay, threshold, and the choice to
   connect a persisted point-neuron output to a downstream target.
4. **Presentation/body-adapter assumptions:** any later mapping from TTMn
   model output to a muscle or fly movement. Phase 6B defines none.

## Literature baseline

| Primary source | Preparation and result relevant here | Relevance to NeuroFly | Limitation |
| --- | --- | --- | --- |
| [King & Wyman (1980), *Anatomy of the giant fibre pathway in Drosophila. I.*](https://doi.org/10.1007/BF01205017) | Anatomical analysis of thoracic GFS components: each GF contacts an ipsilateral TTM motor neuron and an interneuron; the interneuron makes output contacts with DLM motor neurons. | Supports the TTMn / PSI / DLMn branch organization and separates the direct leg-motor branch from the indirect wing-motor branch. | This is classic fly anatomy, not an annotation of the current MaleCNS v1.0 specimen or its IDs. |
| [Tanouye & Wyman (1980), *Motor outputs of giant nerve fiber in Drosophila*](https://doi.org/10.1152/jn.1980.44.2.405) | Electrically stimulated GF spikes and recorded axonal/muscle outputs. A single GF spike produced short, constant-latency TTM and DLM muscle potentials; the TTM branch followed higher stimulus frequencies than the DLM branch. | Establishes a fast GF-mediated motor pathway and provides historical response constraints. | Brain stimulation and muscle output are not a looming-to-TTMn model; frequency following is not a takeoff decision rule. |
| [Phelan et al. (1996), *Mutations in shaking-B prevent electrical synapse formation in the Drosophila giant fiber system*](https://doi.org/10.1523/JNEUROSCI.16-03-01101.1996) | Genetic and dye-coupling evidence links Shaking-B to functional electrical synapses in the GFS. | Supports treating electrical coupling as a distinct transmission mechanism rather than a chemical edge weight. | Does not provide a MaleCNS v1.0 body-pair conductance or an individualized motor-model parameter. |
| [von Reyn et al. (2014), *A spike-timing mechanism for action selection*](https://doi.org/10.1038/nn.3741) | High-speed behavioral analysis and head-fixed intracellular GF recording during looming. GF spike timing relative to parallel escape circuitry distinguished short and long response modes in the study; GF activation drove short-mode outputs, while GF-silenced flies retained long-mode behavior. A GF spike was followed by middle-leg extension at `0.9 ± 0.2 ms` and flight initiation at `2.0 ± 0.1 ms` (27 trials in 5 flies). | Supports precise GF timing as relevant to a fast short-mode pathway and directly rejects “GF silence means no escape.” | A GF spike alone does not label generic escape or determine mode without parallel-circuit timing. The measured behavioral latencies are not a TTMn membrane or synaptic delay. |
| [Ache et al. (2019), *Neural Basis for Looming Size and Velocity Encoding in the Drosophila Giant Fiber Escape Pathway*](https://doi.org/10.1016/j.cub.2019.01.079) | Looming physiology, pathway perturbations, and EM reconstruction support direct LC4 and LPLC2 visual inputs to GF; the study associates their contributions with angular velocity and size. | Connects the existing NeuroFly upstream pathway to GF in literature and motivates retaining the upstream boundary as a model, not a motor observation. | Does not specify MaleCNS v1.0 downstream body identities or motor transmission parameters. |
| [Augustin et al. (2017), *Reduced insulin signaling maintains electrical transmission in a neural circuit in aging flies*](https://doi.org/10.1371/journal.pbio.2001655) | Adult-fly GFS stimulation/recording across age and genetic conditions; response latency increased with age in TTM and DLM branches and Shaking-B-associated electrical-synapse measures changed. | Shows that pathway latency/reliability can depend on preparation and age; cautions against one universal fixed delay. | Stimulation and tissue preparation differ from the NeuroFly experiment; these measurements do not identify a MaleCNS pair-specific coupling parameter. |
| [Augustin et al. (2019), *A Computational Model of the Escape Response Latency in the Giant Fiber System*](https://doi.org/10.1523/ENEURO.0423-18.2019) | Four-cell, conductance-based GF/TTMn/PSI/DLMn model. Estimated gap conductance settings of 135 μS (young-fit) and 34.5 μS (old-fit) reproduced published end-to-end muscle response latencies of 0.93/1.44 ms and 1.22/1.85 ms for TTM/DLM, respectively. | Supplies a named literature prior and shows anatomy/electrical coupling matter to response timing. | The conductances are model estimates, not direct measurements or MaleCNS values; the model uses compartments, ion channels, and preparation-specific assumptions absent from NeuroFly. Do not import them as validated constants. |
| [Cheong et al. (2026), *Organization of circuits linking descending input to motor output in the Drosophila Male Adult Nerve Cord connectome*](https://doi.org/10.7554/eLife.96084) | Primary analysis of the separate MANC dataset describes GF outputs to TTMn and PSI, PSI→DLMn, other GF-coupled/premotor groups, coordinated leg/wing actions, and non-GF long-mode pathways. | Useful contemporary pathway context and a warning that even the canonical pair of branches is not the whole downstream circuit. | MANC is not MaleCNS. Its identifiers, edges, and weights were not imported or treated as MaleCNS evidence. |
| [Berg et al. (2026), *Sexual dimorphism in the complete Drosophila male central nervous system connectome*](https://doi.org/10.1016/j.cell.2026.08.015) and [official MaleCNS project/download documentation](https://male-cns.janelia.org/download/) | Official MaleCNS v1.0 release and data-resource documentation. The v1.0 annotation table identifies the candidate motor cells; the connectome exposes chemical connectivity through `ConnectsTo`/connectome-weight resources. | Provides the authoritative dataset/version context for the live identity and chemical-edge audit below. | The public v1.0 resource inventory provides no explicit gap-junction adjacency/strength table. Chemical edges cannot complete the mixed GFS connection. |

## MaleCNS v1.0 identity audit

The authoritative identity source was the official
[`body-annotations-male-cns-v1.0-minconf-0.5.feather`](https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather)
file (`bodyId`, `type`, `instance`, `somaSide`, `status`, `statusLabel`,
`superclass`, `subclass`, and `somaNeuromere`). The `bodyId` column is the
MaleCNS ID. The annotation table also has `mancBodyid`; that cross-dataset
field was not used as a MaleCNS identifier.

| Role | MaleCNS bodyId | Type / instance | Side | Status / label | Additional annotation | Verification |
| --- | ---: | --- | --- | --- | --- | --- |
| Existing GF source | 10001 | DNp01 / `DNp01(GF)_R` | R | Traced / Roughly traced | `descending_neuron`; subclass `lt` | Official v1.0 table, agrees with pinned NeuroFly CircuitContract (`node_index=0`). |
| Existing GF source | 10010 | DNp01 / `DNp01(GF)_L` | L | Traced / Roughly traced | `descending_neuron`; subclass `lt` | Official v1.0 table, agrees with pinned NeuroFly CircuitContract (`node_index=1`). |
| Candidate jump motor neuron | 800146 | TTMn / `TTMn_R` | R | Traced / Reviewed | `vnc_motor`; subclass `wm`; neuromere T2 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate jump motor neuron | 804642 | TTMn / `TTMn_L` | L | Traced / Reviewed | `vnc_motor`; subclass `wm`; neuromere T2 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate interneuron | 802401 | PSI / `PSI_L` | L | Traced / Reviewed | `vnc_efferent`; neuromere T2 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate interneuron | 903327 | PSI / `PSI_R` | R | Traced / Reviewed | `vnc_efferent`; neuromere T2 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 801295 | DLMn a, b / `DLMn a, b_R` | R | Traced / Reviewed | `vnc_motor`; subclass `wm`; T2 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 801970 | DLMn a, b / `DLMn a, b_L` | L | Traced / Reviewed | `vnc_motor`; subclass `wm`; T2 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 800718 | DLMn c-f / `DLMn c-f_L` | L | Traced / Reviewed | `vnc_motor`; subclass `wm`; T1 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 800890 | DLMn c-f / `DLMn c-f_L` | L | Traced / Reviewed | `vnc_motor`; subclass `wm`; T1 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 801895 | DLMn c-f / `DLMn c-f_L` | L | Traced / Reviewed | `vnc_motor`; subclass `wm`; T1 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 803013 | DLMn c-f / `DLMn c-f_L` | L | Traced / Reviewed | `vnc_motor`; subclass `wm`; T1 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 801998 | DLMn c-f / `DLMn c-f_R` | R | Traced / Reviewed | `vnc_motor`; subclass `wm`; T1 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 802544 | DLMn c-f / `DLMn c-f_R` | R | Traced / Reviewed | `vnc_motor`; subclass `wm`; T1 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 803048 | DLMn c-f / `DLMn c-f_R` | R | Traced / Reviewed | `vnc_motor`; subclass `wm`; T1 | Official v1.0 table and bounded neuPrint body lookup. |
| Candidate wing motor neuron | 1050014552 | DLMn c-f / `DLMn c-f_R` | R | Traced / Reviewed | `vnc_motor`; subclass `wm`; T1 | Official v1.0 table and bounded neuPrint body lookup. |

Types and sides above come from the current MaleCNS `bodyId` records, not
coordinates, MANC IDs, v0.9 IDs, or a bilateral symmetry rule. The DLMn
annotation query returned two `DLMn a, b` and eight `DLMn c-f` bodies matching
the candidate type names; it is a bounded target set, not a statement about
every possible cell involved in wing behavior.

## MaleCNS v1.0 connectivity audit

After validating the identities above, authenticated live access to
`https://neuprint.janelia.org`, dataset `male-cns:v1.0`, was available. On
2026-09-23 UTC, `fetch_adjacencies` was called only for these body-ID sets,
with `min_total_weight=1`, `rois=["VNC"]`, and
`include_nonprimary=True`. The returned VNC aggregate `weight` was recorded
once per directed body pair; sub-ROI values were not added to the VNC total.
The query did not fetch all partners, run a simulator, or download the full
connectivity table.

### DNp01 → TTMn

| Pre body | Pre identity | Post body | Post identity | Direction | VNC `ConnectsTo.weight` |
| ---: | --- | ---: | --- | --- | ---: |
| 10001 | DNp01 / R | 800146 | TTMn / R | 10001 → 800146 | 70 |
| 10010 | DNp01 / L | 804642 | TTMn / L | 10010 → 804642 | 20 |

The queried TTMn set contained both annotated TTMn bodies; only the two
ipsilateral chemical pairs above were returned at the query threshold.

### DNp01 → PSI

| Pre body | Pre identity | Post body | Post identity | Direction | VNC `ConnectsTo.weight` |
| ---: | --- | ---: | --- | --- | ---: |
| 10001 | DNp01 / R | 802401 | PSI / L | 10001 → 802401 | 3 |
| 10001 | DNp01 / R | 903327 | PSI / R | 10001 → 903327 | 2 |
| 10010 | DNp01 / L | 802401 | PSI / L | 10010 → 802401 | 9 |
| 10010 | DNp01 / L | 903327 | PSI / R | 10010 → 903327 | 2 |

These are the chemical edges returned for both annotated PSI bodies. Their
side pattern is reported, not used to infer or force a physiological
laterality rule.

### PSI → DLMn

| Pre body | Pre identity | Post body | Post identity | Direction | VNC `ConnectsTo.weight` |
| ---: | --- | ---: | --- | --- | ---: |
| 802401 | PSI / L | 801970 | DLMn a, b / L | 802401 → 801970 | 17 |
| 802401 | PSI / L | 801998 | DLMn c-f / R | 802401 → 801998 | 40 |
| 802401 | PSI / L | 802544 | DLMn c-f / R | 802401 → 802544 | 67 |
| 802401 | PSI / L | 803048 | DLMn c-f / R | 802401 → 803048 | 35 |
| 802401 | PSI / L | 1050014552 | DLMn c-f / R | 802401 → 1050014552 | 64 |
| 903327 | PSI / R | 800718 | DLMn c-f / L | 903327 → 800718 | 68 |
| 903327 | PSI / R | 800890 | DLMn c-f / L | 903327 → 800890 | 24 |
| 903327 | PSI / R | 801295 | DLMn a, b / R | 903327 → 801295 | 26 |
| 903327 | PSI / R | 801895 | DLMn c-f / L | 903327 → 801895 | 58 |
| 903327 | PSI / R | 803013 | DLMn c-f / L | 903327 → 803013 | 50 |

The direct query from DNp01 bodies 10001 and 10010 to the ten annotated DLMn
candidate bodies returned zero chemical edges. This is consistent with the
literature-described indirect PSI branch; it is a result for the bounded
body/type query, not proof that no other GFS-associated cells contribute.

All queried weights are MaleCNS v1.0 chemical `ConnectsTo.weight` structural
counts. They are neither conductance nor the total strength of mixed
electrochemical coupling, and no weight was transformed into a motor-model
parameter.

## Chemical versus electrical / mixed transmission

The official MaleCNS download inventory describes curated annotations,
connectome weights, synaptic points/partners, and skeleton resources. The
weights are segment-to-segment synaptic-connectivity data; neuPrint
`fetch_adjacencies` returned chemical `ConnectsTo` edge weights. The selected
body records exposed no electrical-transmission annotation. No dedicated
MaleCNS v1.0 gap-junction adjacency table or per-pair electrical conductance
was found in the official inventory or in the queried records. This audit
therefore treats electrical connectivity as **not represented in the
inspected MaleCNS v1.0 connectivity resources**, not as biologically absent.

| Relationship | MaleCNS v1.0 evidence | Literature evidence | Consequence |
| --- | --- | --- | --- |
| GF/DNp01 → TTMn | Chemical `ConnectsTo` pair weights 70 (R→R) and 20 (L→L). No electrical partner/strength field. | GF→TTMn is a mixed electrochemical connection; electrical coupling is functionally important for rapid output. | Preserve the chemical edge/count as one source component. If modeled, encode electrical coupling separately and label it literature-prior/model-assumption. Never derive it from 70/20. |
| GF/DNp01 → PSI | Four chemical pairs, weights 3, 2, 9, and 2. No electrical partner/strength field. | Literature describes mixed GF→PSI connection; PSI is downstream of GF in the flight-muscle branch. | Same separation: chemical structural edge and any assumed electrical mechanism must be distinct. |
| PSI → DLMn | Ten directed chemical pairs in this bounded set, weights 17–68 as listed. | PSI→DLMn is described as a chemical connection in the classic pathway. | A future model needs an explicit chemical transmission rule/sign/gain; MaleCNS `weight` alone does not determine it. |

Do not report a “MaleCNS electrical weight,” infer a gap junction from a
chemical edge, or fuse chemical and electrical values into one undifferentiated
`structural_weight`. A future connection contract should retain at least
`CHEMICAL_CONNECTOME_EDGE` and `ELECTRICAL_COUPLING` as distinct evidence
records. `MIXED_CONNECTION` may link those two records as a literature-backed
composite relation, but must not create a synthetic total weight. For these
GFS electrical links, direction/rectification is a literature-supported
mechanism, not an adjacency or conductance supplied by MaleCNS.

## Motor-output biology and action semantics

- **TTMn:** the TTMn is the excitatory motor neuron for the tergotrochanteral
  jump muscle; GF activation can drive rapid middle-leg extension. A TTMn
  model event may be called `TTMn model spike` or `TTMn model state`, not a
  jump observation.
- **PSI:** the peripherally synapsing interneuron carries the indirect branch
  from GF to DLM motor neurons. The PSI/DLM branch contributes to wing
  depression/tuck in the classic short-mode circuit. A PSI/DLM model is a
  larger coordinated branch, not a synonym for TTMn.
- **DLMn:** DLM motor neurons innervate dorsal longitudinal wing muscles.
  Muscle activation/flight is outside the present data/model boundary.
- **Short versus long mode:** GF-mediated fast outputs are associated with
  short-mode takeoff, but looming can also elicit parallel GF-independent
  long-mode responses. A GF spike can occur during both modes; relative timing
  with parallel circuits matters. Thus `DNp01 spike == escape`, `DNp01
  silence == no escape`, and `DNp01 spike == complete takeoff program` are all
  invalid mappings here.
- **No body physics:** no force, jump impulse, thrust, gravity, pose, muscle
  contraction, or trajectory follows from any result in this audit.

The Male Adult Nerve Cord paper is a separate connectome dataset and describes
additional GF-coupled and premotor cells beyond TTMn and PSI. It supports the
warning against calling a two-branch model the entire motor program, but its
IDs and edges are not evidence about MaleCNS v1.0.

## Empirical constraints and future parameters

| Quantity | Reported evidence | Classification for NeuroFly | Applicability and limit |
| --- | --- | --- | --- |
| GF spike → middle-leg extension | `0.9 ± 0.2 ms`, 27/27 observations across 5 flies in von Reyn et al. 2014. | **EMPIRICALLY CONSTRAINED** as a behavior-level timing target in that assay. | Not a GF→TTMn synaptic delay or a TTMn spike latency. Preparation, behavior, and timing landmarks must be matched before quantitative validation. |
| GF spike → flight initiation | `2.0 ± 0.1 ms`, same 27-trial/5-fly subset. | **EMPIRICALLY CONSTRAINED** in that assay. | Does not justify a wing trajectory, muscle force, or complete short-mode model in Phase 6C. |
| Brain stimulation → TTM/DLM muscle response | Augustin et al. 2019 report measured comparison targets of 0.93/1.44 ms in 5–7-day flies and 1.22/1.85 ms in 45–50-day flies, TTM/DLM. | **EMPIRICALLY CONSTRAINED** for those stimulation/age conditions; corresponding modeled `g_gap` settings are **LITERATURE PRIOR**. | Brain stimulation bypasses the looming encoder. End-to-end muscle latency is not a TTMn membrane constant or isolated synapse delay. |
| GF→TTMn and GF→PSI electrical coupling | Mixed/rectifying electrical mechanisms supported by classic GFS physiology and anatomy. | **SUPPORTED_LITERATURE**; any numeric NeuroFly coupling is **LITERATURE PRIOR** or **UNKNOWN / MODEL ASSUMPTION**. | No pair-specific MaleCNS conductance. Augustin's 135 μS and 34.5 μS are estimated model settings for young/old conditions, not measured MaleCNS values. |
| TTMn LIF membrane parameters | Existing DNp01 LIF model has configured values, but its DNp01 parameters are not TTMn measurements. | **UNKNOWN / MODEL ASSUMPTION** if reused or replaced. | A downstream cell needs its own explicit model identity and assumptions; do not relabel DNp01 parameters as motor-neuron biology. |
| Chemical GF→TTMn/PSI or PSI→DLMn gain/sign | MaleCNS provides structural contact counts; pathway literature provides qualitative chemical/electrical context. | **UNKNOWN / MODEL ASSUMPTION** unless a model-specific observation bridge is registered. | Do not reuse visual `k_syn` or structural count directly as efficacy. Separate parameters and sensitivity tests are required. |
| Motor-neuron-to-muscle output mechanics | Classic anatomy/physiology identifies target muscles and output timing. | **SUPPORTED_LITERATURE** for qualitative path; numeric force/kinematics are **UNKNOWN / MODEL ASSUMPTION**. | No body adapter is specified or implemented here. |

The existing `dt_ms=0.1` is NeuroFly's numerical step, not a measured GFS
transmission interval. Published stimulus-to-muscle values are end-to-end
constraints for carefully matched validation only; they must not be copied as
per-edge delay constants. No motor-specific numeric parameter is selected in
Phase 6B.

## Evidence matrix

| Relationship | Literature evidence | MaleCNS v1.0 evidence | Model requirement / uncertainty | Status |
| --- | --- | --- | --- | --- |
| LC4/LPLC2 → DNp01 | Ache et al. support direct visual pathway inputs and distinct looming-feature contributions. | Current pinned 313-body contract verifies 126 LC4→DNp01 and 185 LPLC2→DNp01 chemical edges. | The existing Level P encoder/LIF mapping remains an explicit NeuroFly model, not a per-cell physiological fit. | `VERIFIED_MALECNS`; `SUPPORTED_LITERATURE`; model remains an assumption. |
| DNp01 → TTMn | Classic anatomy/physiology supports direct mixed GF→TTMn output and rapid TTM response. | Two directed chemical edges: 10001→800146 weight 70; 10010→804642 weight 20. | A separate electrical-coupling mechanism and TTMn state model are needed; neither is determined by `structural_weight`. | `VERIFIED_MALECNS` for chemical edges; `SUPPORTED_LITERATURE`; `MODEL_ASSUMPTION_REQUIRED`. |
| DNp01 → PSI | Literature supports a GF→PSI mixed connection. | Four directed chemical edges to the two annotated PSI bodies. | Electrical coupling and any chemical transfer/gain must be explicit; not encoded as one edge weight. | `VERIFIED_MALECNS` for chemical edges; `SUPPORTED_LITERATURE`; `MODEL_ASSUMPTION_REQUIRED`. |
| PSI → DLMn | Classic literature supports the indirect chemical PSI→DLMn branch. | Ten directed PSI→DLMn chemical edges to annotated DLMn bodies; no direct DNp01→DLMn chemical edge in the bounded query. | DLMn state dynamics and transmission signs/gains require explicit assumptions; a full short-mode model also needs coordinated output. | `VERIFIED_MALECNS` for chemical edges; `SUPPORTED_LITERATURE`; `MODEL_ASSUMPTION_REQUIRED`. |
| Motor neuron → muscle function | TTMn→TTM and DLMn→DLM function is established in classic anatomy/physiology. | The audited neuron-to-neuron query does not provide muscle nodes or a modeled muscle contract. | Any muscle dynamics/body output is a separate model and adapter boundary. | `SUPPORTED_LITERATURE`; `MODEL_ASSUMPTION_REQUIRED`; no MaleCNS muscle edge. |
| GF spike timing → short-mode selection | von Reyn et al. show timing relative to parallel circuitry matters; other pathways retain long-mode responses. | A static connectome contains no motor mode or behavioral events. | NeuroFly lacks parallel long-mode pathways and measured behavior; GF spikes cannot select a generic escape label. | `SUPPORTED_LITERATURE`; `UNRESOLVED` for NeuroFly behavior; `MODEL_ASSUMPTION_REQUIRED` for any future selector. |

## Phase 6C options

| Option | Scientific strength | Required assumptions | Size / validation opportunity | Main risk |
| --- | --- | --- | --- | --- |
| **A. DNp01→TTMn only** | Tests the smallest verified GF-to-motor-neuron branch and stops before body mechanics. | Explicit electrical-coupling hypothesis; separate optional chemical component; TTMn model identity/parameters; no use of structural count as efficacy. | Two source-target pairs and two TTMn states. Can test reproducibility, body mapping, and causal dependence on persisted DNp01 events. | Can be over-described as a jump or short-mode takeoff; TTMn state has no direct body movement semantics. |
| **B. DNp01→TTMn plus DNp01→PSI→DLMn** | Represents both canonical GF motor branches and the basic coordinated leg/wing output hypothesis. | All Option A assumptions plus PSI/DLMn state, chemical PSI→DLM transmission, bilateral/nontrivial pairing, and branch coordination. Additional GF-coupled/premotor nodes remain omitted. | Larger neural core. Can test branch-specific ablations, but cannot claim a complete takeoff program or flight. | Looks behavior-complete despite omitted downstream neurons, parallel long-mode circuits, and body mechanics. |
| **C. Block motor implementation** | Avoids unsupported transfer if identities/edges or connection types are unavailable. | No assumptions. | No downstream experiment until new evidence access. | Not required by this audit: current v1.0 identities and chemical edges were verified, while missing electrical coupling is now a clearly bounded model input rather than ambiguous chemical weight. |

## Recommended Phase 6C and its gate

**Recommendation: Option A — DNp01→TTMn neural extension only.** Use the two
verified source-target pairs. Preserve the current 313-body sensory
`CircuitContract` identity and its hashes; create a separately versioned,
read-only downstream motor-pathway evidence contract that references that
upstream source rather than silently redefining the old candidate. The future
contract should carry:

- dataset/version and upstream `CircuitContract` provenance/hash;
- exact DNp01 and TTMn `bodyId`, type, side, annotation/status, and directed
  chemical-edge reference/structural count;
- transmission-kind distinction: `CHEMICAL_CONNECTOME_EDGE`,
  `ELECTRICAL_COUPLING`, and a literature-backed `MIXED_CONNECTION` link;
- exact source DNp01 persisted event/state identity and step/time;
- target TTMn model-state record and model/config identity;
- per-connection electrical and chemical model parameters (or parameter-sweep
  identity), all labelled as assumptions/priors;
- provenance for each non-connectome mechanism and no muscle/behavior field.

The Phase 6C pass gate should be: the reference looming experiment produces a
deterministic TTMn **model-state** result downstream of the exact persisted
DNp01 event identities; reruns match; disabling/silencing DNp01 input removes
the GF-mediated TTMn response under the declared model; connection types and
source weights remain separate; and a parameter sensitivity report shows
which outcomes depend on unknown assumptions. A pass means a reproducible
motor-neuron model experiment, not a biological validation or behavior.

Suggested bounded conditions are the existing reference looming run, a
no-loom/rest baseline, DNp01-silenced condition, and existing LC4-only,
LPLC2-only, and combined pathway masks. These test model causality and
reproducibility only. If Option B is considered later, add PSI/DLMn states and
branch ablations as a separate gate. Quantitative comparison to the published
GF-to-leg/muscle timing requires matching the experimental landmark and
preparation; it is not a direct criterion for TTMn membrane values.

Not part of Phase 6C: a rendered jump, force/velocity, flight, escape
classification, or fly-pose change. Use intermediate labels such as
“TTMn model spike” or “GF-mediated TTMn pathway state.” A later muscle/body
adapter must be explicitly identified as a new model layer, with any
takeoff event classified as a model output rather than an observed biological
event.

## Data acquisition and reproducibility

- Local source first: existing ignored NeuroFly contract and experiment; no
  external files were needed to re-check their identities.
- Official v1.0 annotation table downloaded from the URL linked above to
  `/tmp/body-annotations-male-cns-v1.0-minconf-0.5.feather` because the local
  three-type snapshot does not contain motor targets. Download size:
  14,483,314 bytes. SHA-256:
  `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`.
- Authenticated neuPrint access to `male-cns:v1.0` succeeded. Credentials were
  used only through the existing client and were never printed or serialized.
  Queries were restricted to the listed 2 DNp01, 2 TTMn, 2 PSI, and 10 DLMn
  bodies and the VNC ROI.
- No full connectivity, synapse-point, partner, or database file was
  downloaded. In particular, the official 1.1 GB
  `connectome-weights-male-cns-v1.0-minconf-0.5.feather` file and 6.8 GB /
  12.7 GB synapse resources were not needed. The bounded authenticated
  neuPrint query was the smaller authoritative alternative.
- No downloaded source, generated data, or credentials are in the repository
  or staged.

## Scientific limitations

1. The selected NeuroFly CircuitContract itself ends at DNp01; downstream
   evidence is an audit result, not a production graph or simulation.
2. MaleCNS v1.0 evidence inspected here represents chemical `ConnectsTo`
   edges. It does not give the GFS electrical coupling identity, direction,
   conductance, or efficacy as an explicit per-edge dataset.
3. The official v1.0 target annotation and live query establish current
   identity/connectivity but do not establish a validated motor-neuron model.
4. TTMn model parameters and chemical/electrical transmission rules are not
   measured for these exact MaleCNS cells. Published values are priors or
   end-to-end constraints from other preparations.
5. TTMn-only is not both canonical GF branches, the extended GFS network, all
   escape pathways, or a complete short-mode motor program.
6. Parallel/GF-independent long-mode pathways exist; this audit does not
   identify or model them.
7. No muscle dynamics, body physics, stimulus-evoked behavior, or empirical
   validation is added. Current experiment status remains `NOT_EVALUATED`.

