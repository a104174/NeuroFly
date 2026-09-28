# Phase 8D — PSI/DLMn motor-branch evidence and identity assessment

**Circuit decision: `ADD_PSI_IDENTITY_CONTRACT_ONLY`. Dynamics readiness:
`READY_FOR_STRUCTURAL_CONTRACT_ONLY`.** This is a documentation-only evidence
closure. No motor dynamics, parameters, source contracts, artifacts, frontend,
or API were changed. The assessment separates the committed sensory
`CircuitContract`, the distinct prior MaleCNS motor query recorded in Phase
6B, primary physiology, and future NeuroFly model assumptions.

## Repository and source boundary

The assessment began on clean `main`, HEAD
`39c6f512c6eba91bd3ba6e78290bb612c0d2568f`, equal to `origin/main`; Phase 8C,
8B, 8A, and 7O were committed. `git diff --check` passed before the review.

The offline `looming_giant_fiber_v1` MaleCNS v1.0 `CircuitContract` was
reloaded and verified. It contains 313 bodies of types LC4, LPLC2, and DNp01
and 20,607 chemical `ConnectsTo` records. Its pinned files are:

| Source | SHA-256 |
| --- | --- |
| `neurons.jsonl` | `00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e` |
| `connections.jsonl` | `f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a` |
| `manifest.json` | `bf4aea0745a875ab4ca1927af71ce4d78f09d462559d6ab2aa1d552c98a4fe2c` |
| Canonical circuit identity | `3af274ecbf6ba4025b9e6ef0d038716446b0b9c03d9dd4f97c0151d280ebb8a5` |

This contract has no TTMn, PSI, or DLMn identity and no downstream motor edge.
That is the contract's selected boundary, not evidence that the cells or
connections are absent in MaleCNS. The separate Phase 6C evidence contract
contains only the two DNp01→TTMn chemical edges and literature modality
records. The broader Phase 6B assessment records a bounded official MaleCNS
v1.0 query made on 2026-09-23: 2 DNp01, 2 TTMn, 2 PSI, and 10 DLMn bodies;
VNC ROI; `min_total_weight=1`; `include_nonprimary=true`. Its identity source
was the official body-annotation Feather file, 14,483,314 bytes, SHA-256
`2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`.

The prior assessment preserves the bounded query output but not a content
hash of the response payload. Therefore, the motor identities and chemical
edges below are **documented prior source-query evidence**, not records
reloaded from the pinned CircuitContract. Phase 8D does not silently merge
them into that contract or claim a fresh query. A follow-on identity contract
should pin a reproduced query and canonical response/result hash before any
dynamic use.

## Existing model and evidence state

Phase 6C's production event mapper validates same-run DNp01 `SpikeEvent`s and
uses the exact source-to-target entries in its separate
`malecns_dnp01_ttmn_evidence_v1` contract:

| Source | Target | MaleCNS chemical structural count |
| --- | --- | ---: |
| DNp01 10001 / `DNp01(GF)_R` | TTMn 800146 / `TTMn_R` | 70 |
| DNp01 10010 / `DNp01(GF)_L` | TTMn 804642 / `TTMn_L` | 20 |

The two rows are chemical MaleCNS `ConnectsTo` evidence only. The evidence
contract keeps literature-supported electrical coupling separate, with no
pair-specific value and no combined mixed weight. Its unchanged TTMn equation
is `x[n] = x[n−1] exp(−dt/tau_motor) + event_count[n] event_gain`, with
`tau_motor_ms=10` and `event_gain=0.25`; these remain `MODEL_ASSUMPTION`s
(tau is in ms; event_gain is dimensionless). TTMn output is not membrane
voltage, muscle activation, force, or behavior.

The current MaleCNS source records for DNp01 10001 and 10010 annotate
acetylcholine as predicted and consensus transmitter (prediction confidence
0.5004955530166626 and 0.5571407079696655, respectively). This type/body
annotation does not measure transmitter release at any particular edge. The
bounded motor query did not persist PSI/DLMn transmitter fields, and those
bodies are outside the pinned CircuitContract. Literature transmitter
findings below remain pathway-level, not a substitute for the missing
per-body source records.

## MaleCNS identity and chemical-edge audit

The exact candidate identities below are reported by the prior official
annotation/query audit; no side was inferred from an array position or
symmetry. Body status was reported as `Traced`; PSI/TTMn/DLMn annotation labels
were `Reviewed`, while DNp01's label was `Roughly traced`.

| Body ID | MaleCNS type / instance | Side | Reported source annotation |
| ---: | --- | :---: | --- |
| 10001 | DNp01 / `DNp01(GF)_R` | R | descending neuron; `node_index=0` in the pinned contract |
| 10010 | DNp01 / `DNp01(GF)_L` | L | descending neuron; `node_index=1` in the pinned contract |
| 800146 | TTMn / `TTMn_R` | R | VNC motor, subclass `wm`, T2 |
| 804642 | TTMn / `TTMn_L` | L | VNC motor, subclass `wm`, T2 |
| 802401 | PSI / `PSI_L` | L | VNC efferent, T2 |
| 903327 | PSI / `PSI_R` | R | VNC efferent, T2 |
| 801295 | DLMn a,b / `DLMn a, b_R` | R | VNC motor, subclass `wm`, T2 |
| 801970 | DLMn a,b / `DLMn a, b_L` | L | VNC motor, subclass `wm`, T2 |
| 800718 | DLMn c–f / `DLMn c-f_L` | L | VNC motor, subclass `wm`, T1 |
| 800890 | DLMn c–f / `DLMn c-f_L` | L | VNC motor, subclass `wm`, T1 |
| 801895 | DLMn c–f / `DLMn c-f_L` | L | VNC motor, subclass `wm`, T1 |
| 803013 | DLMn c–f / `DLMn c-f_L` | L | VNC motor, subclass `wm`, T1 |
| 801998 | DLMn c–f / `DLMn c-f_R` | R | VNC motor, subclass `wm`, T1 |
| 802544 | DLMn c–f / `DLMn c-f_R` | R | VNC motor, subclass `wm`, T1 |
| 803048 | DLMn c–f / `DLMn c-f_R` | R | VNC motor, subclass `wm`, T1 |
| 1050014552 | DLMn c–f / `DLMn c-f_R` | R | VNC motor, subclass `wm`, T1 |

The documented bounded chemical query returned these directed pairs. Counts
are structural source metadata, not signed weights or functional strengths.

| Proposed edge (source → target) | Chemical count | Literature/transmission evidence | Sign evidence | Neural delay | Magnitude | Readiness |
| --- | ---: | --- | --- | --- | --- | --- |
| 10001 DNp01/R → 800146 TTMn/R | 70 | GF→TTMn mixed electrical/chemical pathway; MaleCNS records only chemical connectivity. | Positive fast pathway output; no pair-resolved TTMn EPSP trace. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 10010 DNp01/L → 804642 TTMn/L | 20 | Same pathway class; chemical record omits electrical component. | Positive fast pathway output; no pair-resolved TTMn EPSP trace. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 10001 DNp01/R → 802401 PSI/L | 3 | Chemical edge; literature supports GF–PSI electrical coupling/mixed branch, not exact-pair modality. | Positive transmission supported at GF-driven DLM branch level only. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 10001 DNp01/R → 903327 PSI/R | 2 | Chemical edge is not a complete mixed-synapse description. | Branch-level support; no exact-pair postsynaptic recording. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 10010 DNp01/L → 802401 PSI/L | 9 | Chemical edge is not a complete mixed-synapse description. | Branch-level support; no exact-pair postsynaptic recording. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 10010 DNp01/L → 903327 PSI/R | 2 | Chemical edge is not a complete mixed-synapse description. | Branch-level support; no exact-pair postsynaptic recording. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 802401 PSI/L → 801970 DLMn a,b/L | 17 | Chemical edge; cholinergic/excitatory transmission supported at cell-class/pathway level. | Positive/depolarizing MN5-class EPSP; not mapped to this MaleCNS pair. | `NOT_IDENTIFIABLE` per pair | `PARTIALLY_SUPPORTED` at pathway level; edge gain `NOT_IDENTIFIABLE` | Structural contract only |
| 802401 PSI/L → 801998 DLMn c–f/R | 40 | Chemical edge; literature correspondence is pathway-level, not body-ID mapped. | Positive pathway sign; not exact-pair resolved. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 802401 PSI/L → 802544 DLMn c–f/R | 67 | Chemical edge; literature correspondence is pathway-level, not body-ID mapped. | Positive pathway sign; not exact-pair resolved. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 802401 PSI/L → 803048 DLMn c–f/R | 35 | Chemical edge; literature correspondence is pathway-level, not body-ID mapped. | Positive pathway sign; not exact-pair resolved. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 802401 PSI/L → 1050014552 DLMn c–f/R | 64 | Chemical edge; literature correspondence is pathway-level, not body-ID mapped. | Positive pathway sign; not exact-pair resolved. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 903327 PSI/R → 800718 DLMn c–f/L | 68 | Chemical edge; literature correspondence is pathway-level, not body-ID mapped. | Positive pathway sign; not exact-pair resolved. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 903327 PSI/R → 800890 DLMn c–f/L | 24 | Chemical edge; literature correspondence is pathway-level, not body-ID mapped. | Positive pathway sign; not exact-pair resolved. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 903327 PSI/R → 801295 DLMn a,b/R | 26 | Chemical edge; literature correspondence is pathway-level, not body-ID mapped. | Positive pathway sign; not exact-pair resolved. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 903327 PSI/R → 801895 DLMn c–f/L | 58 | Chemical edge; literature correspondence is pathway-level, not body-ID mapped. | Positive pathway sign; not exact-pair resolved. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |
| 903327 PSI/R → 803013 DLMn c–f/L | 50 | Chemical edge; literature correspondence is pathway-level, not body-ID mapped. | Positive pathway sign; not exact-pair resolved. | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair | Structural contract only |

The same bounded query returned **zero direct chemical DNp01→DLMn edges** for
10001/10010 against these ten annotated DLMn candidates. This is not a claim
that no other cell or route exists outside the bounded target set. The
reported PSI outputs include both same-side and cross-side targets; the
contract must preserve those observed body identities rather than impose
ipsilateral routing.

## Primary literature and transmission evidence

- [King & Wyman (1980), “Anatomy of the giant fibre pathway in
  Drosophila. I.”, DOI 10.1007/BF01205017](https://doi.org/10.1007/BF01205017)
  report thoracic anatomy: GF contacts a large motor axon and an interneuron;
  the interneuron synapses onto DLM motor axons. This supports pathway
  organization, not MaleCNS body-ID identity or physiological transfer.
- [Tanouye & Wyman (1980), “Motor outputs of giant nerve fiber in
  Drosophila”, DOI 10.1152/jn.1980.44.2.405](https://doi.org/10.1152/jn.1980.44.2.405)
  electrically stimulated GF and recorded its axon intracellularly; single
  GF spikes produced short, stable-latency TTM and DLM muscle potentials.
  These are muscle endpoints, not isolated GF→TTMn/PSI synaptic delays.
- [Phelan et al. (1996), “Mutations in shaking-B prevent electrical synapse
  formation…”, DOI 10.1523/JNEUROSCI.16-03-01101.1996](https://doi.org/10.1523/JNEUROSCI.16-03-01101.1996)
  showed dye coupling from GF to TTMn and PSI during development and loss of
  that coupling in `shak-B` mutants. This supports electrical connectivity;
  developmental dye coupling is not a conductance or adult pair-specific
  postsynaptic voltage measurement.
- [Allen & Murphey (2007), DOI
  10.1111/j.1460-9568.2007.05686.x](https://doi.org/10.1111/j.1460-9568.2007.05686.x)
  experimentally separated the adult GF–TTMn mixed synapse: chemical release
  supports a long-latency residual TTM response when electrical transmission
  is impaired, and the chemical component is cholinergic. This evidence is
  for GF–TTMn, not a numeric GF–PSI conductance.
- [Fayyazuddin et al. (2006), “The nicotinic acetylcholine receptor Dα7 is
  required for an escape behavior in Drosophila”, DOI
  10.1371/journal.pbio.0040063](https://doi.org/10.1371/journal.pbio.0040063)
  used GF stimulation, DLM muscle responses, and whole-cell recordings from
  the identified DLM motor neuron MN5 that innervates DLM a,b. Their
  somatically measured PSI-pathway EPSP was `4.71 ± 0.35 mV` (`n=10`) in
  controls and `1.5 ± 0.32 mV` (`n=7`) in `gfA1` mutants. Dα7 perturbation
  impaired DLM responses while TTM following and direct DLMn-to-muscle
  responses remained, supporting a positive cholinergic PSI→DLMn pathway.
  This is a valuable **class-level/pathway-level physiological constraint**,
  not an isolated unitary release from any one of the ten MaleCNS PSI→DLMn
  pairs, and not a gain for the Phase 6C abstract state.
- [Augustin et al. (2017), DOI
  10.1371/journal.pbio.2001655](https://doi.org/10.1371/journal.pbio.2001655)
  measured age- and condition-dependent brain-stimulus→TTM/DLM muscle
  response latencies and associated pathway changes with Shaking-B/gap
  junctions. It does not isolate edge delays or pair conductances.
- [Augustin, Zylbertal & Partridge (2019), DOI
  10.1523/ENEURO.0423-18.2019](https://doi.org/10.1523/ENEURO.0423-18.2019)
  is a four-cell conductance-model precedent, not a MaleCNS measurement.
  Its 135/34.5 µS gap-junction settings, 80 µS PSI→DLM chemical peak
  conductance, and 0.15 ms chemical delay are estimated, fitted, or standard
  model values used to reproduce end-to-end latency targets. They must not be
  imported as measured pair-specific values.
- [von Reyn et al. (2014), DOI
  10.1038/nn.3741](https://doi.org/10.1038/nn.3741) related GF spike timing
  to rapid middle-leg extension and flight initiation in a specific looming
  assay. Its reported behavior latencies (`0.9 ± 0.2 ms` and
  `2.0 ± 0.1 ms`) are behavior/body endpoints, not neural synaptic delays.

The evidence therefore supports **mixed electrical/chemical GF→TTMn and
GF→PSI pathway organization**, and a **chemical, cholinergic, excitatory
PSI→DLMn pathway**. MaleCNS `ConnectsTo` records enumerate only the chemical
component. The presence of a chemical edge neither refutes the electrical
component nor measures its conductance. Literature labels correspond to cell
classes and pathway roles; they do not unambiguously map each historical
recording to a particular MaleCNS v1.0 body ID.

## Timing and parameter identifiability

| Quantity | DNp01→TTMn | DNp01→PSI | PSI→DLMn |
| --- | --- | --- | --- |
| Sign | `SUPPORTED` at pathway-output level; no exact-pair postsynaptic voltage trace | `PARTIALLY_SUPPORTED` at GF→PSI→DLM pathway level; no exact-pair voltage sign measurement | `SUPPORTED` for positive/depolarizing class-level EPSP; not exact MaleCNS pair-resolved |
| Event/continuous semantics | Fast GF-spike-mediated route is supported; Phase 6C event interface remains an abstraction of mixed transmission | GF spikes drive a pathway involving electrical coupling; exact MaleCNS transfer remains unresolved | Chemical EPSP and DLMn spike output are supported; no per-edge NeuroFly event rule identified |
| Neural transmission delay | `NOT_IDENTIFIABLE` per MaleCNS pair | `NOT_IDENTIFIABLE` per MaleCNS pair | `NOT_IDENTIFIABLE` per MaleCNS pair; Augustin's 0.15 ms is a model estimate |
| Gain / conductance | `NOT_IDENTIFIABLE` per pair | `NOT_IDENTIFIABLE` per pair, especially electrical coupling | `PARTIALLY_SUPPORTED` only by MN5/pathway somatic EPSP amplitude; `NOT_IDENTIFIABLE` per MaleCNS edge |
| Time constant | `NOT_IDENTIFIABLE` for the Phase 6C latent state | `NOT_IDENTIFIABLE` for a future PSI state | `NOT_IDENTIFIABLE` for a future DLMn state from this observation alone |
| Threshold | `NOT_IDENTIFIABLE` as a TTMn model parameter | `NOT_IDENTIFIABLE` for PSI model | DLMn can spike from pathway input, but the relevant local threshold is `NOT_IDENTIFIABLE` |
| Synapse class | Literature: mixed electrical/chemical; MaleCNS: chemical count only | Literature: electrical coupling and mixed branch; MaleCNS: chemical count only | Literature: chemical cholinergic PSI→DLMn; MaleCNS: chemical count only |

Three timing quantities must remain separate:

1. **Neural transmission:** order and rapid causal transmission are supported;
   no reviewed experiment isolates a per-edge DNp01→PSI or PSI→DLMn delay for
   these MaleCNS bodies. The Phase 8C same-boundary convention is software
   semantics, not a measured motor delay.
2. **Muscle response:** classic GF-stimulation work measures short-latency
   TTM/DLM muscle potentials; Augustin et al. measure brain-stimulus-to-muscle
   latency under specified ages/conditions. These combine multiple axons,
   synapses, motor-neuron conduction, neuromuscular transmission, and muscle
   recording landmarks.
3. **Behavior:** leg extension/flight-initiation timing is a body-level
   outcome. It cannot be substituted for a synaptic delay, state time
   constant, or edge gain.

## Minimal future structural contract

A separately versioned `motor_neural_pathway_contract_v1` is justified before
new neural dynamics. It should be an immutable, no-dynamics evidence artifact
that directly references:

- the existing `looming_giant_fiber_v1` identity/hash without broadening it;
- the official MaleCNS v1.0 annotation snapshot/hash for all candidate bodies;
- a reproduced bounded connectivity query with query parameters, source
  endpoint/dataset, record identities, and a canonical response/result hash;
- exact body IDs, instances, types, sides, and directed chemical edges/counts;
- literature modality evidence as separate records for electrical coupling,
  mixed connections, and PSI→DLMn cholinergic transmission;
- explicit literature-to-MaleCNS mapping confidence and `no_dynamics=true`.

Do not combine chemical and electrical evidence into one weight. Do not
numerically use structural counts as gain, probability, conductance, delay,
or event multiplier. The historical query's missing response digest must be
closed by source revalidation when creating this contract.

## Phase 8D boundary and decisions

- **MaleCNS source evidence:** current pinned contract ends at DNp01; separate
  prior official bounded query documents the TTMn/PSI/DLMn IDs and chemical
  edges, but is not itself a committed expanded `CircuitContract`.
- **Literature evidence:** named GF–TTMn/PSI electrical or mixed pathway
  evidence; PSI→DLMn cholinergic/EPSP evidence; pathway-output and timing
  observations from distinct preparations.
- **Model assumptions:** Phase 6C event-to-TTMn convention and parameters;
  any future PSI/DLMn state, event rule, edge gain, delay, threshold, or
  conductance.
- **Unresolved:** per-pair electrical coupling, complete mixed transmission,
  exact historical-cell-to-MaleCNS identity mapping, edge-specific
  physiological gains/delays, and equivalent state observation operators.

No PSI/DLMn dynamics, muscle model, force, torque, body mechanics, escape
command, or behavior is added. Phase 7O remains unchanged; its zero DNp01
events still imply zero sensory-derived Phase 6C motor input. Phase 8B
synthetic events are not part of this branch evidence.

**Circuit decision:** `ADD_PSI_IDENTITY_CONTRACT_ONLY`.

**Dynamics-readiness decision:** `READY_FOR_STRUCTURAL_CONTRACT_ONLY`.
This explicitly does not approve PSI/DLMn dynamics: current edge-specific
gains, delays, electrical conductances, cell dynamics, and observation
operators are not identified. The class-level PSI→MN5 EPSP is an important
constraint for a future matched model, not per-edge calibration.
