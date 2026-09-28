# Phase 8J — motor-neuron output and neural→muscle boundary readiness

**Assessment:** `PIN_MOTOR_NEURON_MUSCLE_TARGET_CONTRACT`.
**DLMn state:** `NOT_REQUIRED_YET` for a structural contract (dynamic muscle
drive remains unready). **TTMn→muscle:** `READY_FOR_STRUCTURAL_TARGET_CONTRACT`.
**DLMn→muscle:** `READY_FOR_STRUCTURAL_TARGET_CONTRACT`, at class/group level
only. No muscle or additional neural dynamics are authorized by this assessment.

## Repository and replay gate

Assessment began on clean `main` at
`f43378d2d1ba708b282cffd54c5360dc2f74ca95`, matching `origin/main`;
Phase 8I is committed. Offline replay validated the pinned
`motor_neural_pathway_contract_v1` ID
`a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c`
(16 nodes, 18 chemical edges), and the Phase 8I parallel-composition artifact
ID `f4225f3f24bcf3a3ed27d5c0d313700426e788d6af232b2c57b9d77e3ae63bbf`.
The latter replayed all six synthetic fixtures with exact child identity. The
Phase 8C and 8H production adapters remain separate; the canonical Phase 7O
condition has no DNp01 spikes and therefore no TTMn activity or PSI/DLMn
receipts. Synthetic Phase 8I events are not sensory-derived events.

## Current outputs and the missing boundary

Phase 6C TTMn uses `ttmn_dimensionless_event_integrator/phase6c_v1`:
`x[n] = x[n−1] exp(−dt_ms/10 ms) + event_count[n] × 0.25`. The 10 ms decay
and 0.25 increment are **model assumptions**. `x_TTMn` is a dimensionless
exploratory neural state, not measured membrane voltage, a TTMn spike,
firing probability, neuromuscular release, or muscle activation. Phase 6D/6E
found no equivalent adult identity-resolved TTMn neuronal observation with
which to identify those parameters. It can be named in a structural target
contract; it cannot directly drive a defensible muscle model.

Phase 8G `dlmn_routed_event_v1` is a deterministic *graph-path receipt*: one
origin DNp01 event can yield ten DLMn receipts across distinct paths. A
receipt does not assert that the PSI fired, that the DLMn depolarized or
spiked, or that a neuromuscular junction transmitted. Phase 8I preserves this
distinction rather than merging TTMn state and DLMn path counts. A DLMn
receipt cannot be promoted into a muscle-driving event.

## Identity and innervation evidence

The pinned MaleCNS motor contract is **source evidence** for the listed
neural body IDs, neuron types, sides, and *central chemical* edges. It does
not contain muscle nodes or motor-neuron→muscle connections. The muscle
targets below are **literature-supported class correspondences**, not
MaleCNS source edges. The classic giant-fibre anatomy supports the GF→TTMn
and GF→PSI→DLMn branch organization [King & Wyman (1980)](https://doi.org/10.1007/BF01205017).
Adult pathway experiments identify TTMn innervation of TTM and DLMn
innervation of DLM, and describe their neuromuscular junctions as chemical
and glutamatergic [Augustin et al. (2017)](https://doi.org/10.1371/journal.pbio.2001655).
That transmitter statement is at pathway/class level, not a measured
MaleCNS body-to-muscle efficacy.

The `TTMn_R` and `TTMn_L` source annotations support the **TTM muscle class**
for bodies 800146/R and 804642/L; the classic branch is ipsilateral. The
specific right/left muscle endpoint should be treated as a high-confidence
literature-to-annotation inference, not as an imaged peripheral axon from
these exact MaleCNS body IDs.

For DLM, the pinned annotations support `DLMn a, b` (one body per side) and
`DLMn c-f` (four per side) **target groups**. Classical labeling found one
motor neuron to the dorsal DLM fibers and four neurons to the other fibers
[Coggshall (1978)](https://doi.org/10.1002/cne.901770410); modern primary
work describes MN5 innervating the two dorsal fibers *contralateral* to its
soma, and MN1–4 innervating more ventral fibers ipsilateral to their somata
[Kuehn & Duch (2013)](https://doi.org/10.1111/ejn.12104),
[Hürkey et al. (2023)](https://doi.org/10.1038/s41586-023-06099-0).
Thus a MaleCNS DLMn `side` must **not** automatically become the muscle side,
especially for the `a,b`/MN5-like class. Exact MaleCNS-body↔historical-MN5
and `a` versus `b`, or `c` versus `d/e/f`, fiber crosswalks remain unresolved;
fiber-number/letter nomenclature also varies among studies. The Phase 8K
contract should pin class/group targets and leave unsupported exact fiber and
side assignments explicitly unresolved.

| MaleCNS motor body | Class; source side | Proposed target | Identity/innervation evidence | Output-event evidence | Delay; gain/force | Mapping confidence | Structural / dynamic readiness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 800146 | TTMn; R | TTM class; R endpoint candidate | Pinned `TTMn_R`; ipsilateral TTMn→TTM class in primary anatomy | TTM muscle potential after GF/motor stimulation, **not** this body's recorded spike | Pair-specific NMJ delay, gain and force unidentified | High class; inferred side | Ready at class/qualified-side level / not ready |
| 804642 | TTMn; L | TTM class; L endpoint candidate | Pinned `TTMn_L`; same class evidence | Same limitation | Same limitation | High class; inferred side | Ready at class/qualified-side level / not ready |
| 801295, 801970 | DLMn a,b; R, L | DLM a,b group; muscle side unresolved in exact-body mapping | Pinned class annotation; MN5-like dorsal-fiber innervation in literature | MN5-class action potentials exist; no exact MaleCNS-ID output mapping | Pair-specific NMJ delay, gain and force unidentified | Moderate group; exact body/fiber unresolved | Ready at group level / not ready |
| 800718, 800890, 801895, 803013 | DLMn c-f; L | DLM c-f group; exact fiber unresolved | Pinned class annotation; MN1–4-like ventral-fiber innervation in literature | Class-level motor AP evidence, not these exact IDs | Same limitation | Moderate group | Ready at group level / not ready |
| 801998, 802544, 803048, 1050014552 | DLMn c-f; R | DLM c-f group; exact fiber unresolved | Same source and class evidence | Same limitation | Same limitation | Moderate group | Ready at group level / not ready |

The table's “ready” means a **qualified structural association** can be
recorded with its evidence class and uncertainty, not that a MaleCNS
motor-neuron→muscle edge has been observed. A Phase 8K source audit should
fail closed if even the group-level labels cannot be reproduced.

## Motor output and timing evidence

Discrete motor-neuron action potentials are a meaningful physiological
concept: adult MN1–5 firing has been recorded, and DLM muscle response can
be recorded after motor-neuron stimulation
[Hürkey et al. (2023)](https://doi.org/10.1038/s41586-023-06099-0),
[Giant Fiber recording protocol (2011)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2946074/).
That supports considering a *separately named* exploratory output-event
interface in a later phase. It does **not** make a Phase 6C latent value or a
Phase 8G receipt into a physiological action potential. The identified
PSI→MN5 excitatory postsynaptic recording concerns an historical cell/class,
not an exact MaleCNS DLMn body or its muscle output
[Fayyazuddin et al. (2006)](https://doi.org/10.1371/journal.pbio.0040063).

GF/brain-stimulus→TTM or DLM muscle latencies combine central transmission,
motor-axon propagation, the neuromuscular junction and muscle electrical
response; later contraction and movement add further processes
[Tanouye & Wyman (1980)](https://doi.org/10.1152/jn.1980.44.2.405),
[Thomas & Wyman (1984)](https://doi.org/10.1523/JNEUROSCI.04-02-00530.1984),
[Augustin et al. (2017)](https://doi.org/10.1371/journal.pbio.2001655).
Even direct thoracic motor stimulation→muscle potential is not an isolated
NMJ delay. Augustin, Zylbertal & Partridge's 2019 0.35 ms NMJ term is a
**model-derived estimate** after subtracting a simulated motor-neuron spike
time from an approximately 0.65 ms composite latency, not a measured
MaleCNS body/muscle-pair delay
[Augustin et al. (2019)](https://doi.org/10.1523/ENEURO.0423-18.2019).
No exact-body axonal delay, NMJ delay, activation gain, calcium response,
contraction amplitude, or force parameter is identified here. Structural
MaleCNS `ConnectsTo` counts describe central chemical connectivity only and
cannot fill any of these gaps.

## Options and assumption budget

| Candidate next capability | New free assumptions before a meaningful output | Assessment |
| --- | --- | --- |
| Current TTMn state and DLMn receipt directly drive muscle | At least two incompatible conversion rules, delay, gain, muscle response rule | Reject: silently changes the meaning of both current outputs. |
| Explicit exploratory motor-neuron output event | At least one TTMn state→event rule and one DLMn receipt→event rule, including thresholds/deduplication or equivalent choices | Conceptually testable only with **synthetic** output events; cannot be derived from current representations without added assumptions. |
| DLMn/TTMn latent spike models | Rest, time constants, input coupling, threshold, reset, refractory, output-site semantics, plus NMJ model | More unidentified parameters; exact-body evidence does not justify this as the next step. |
| No-dynamics motor-neuron→muscle target contract | **Zero numerical/dynamic parameters**; qualified class/group correspondence and provenance labels | Preferred next gate. Pins what target class can be named without claiming an output signal. |
| Hold for new physiology | Zero model assumptions, but no identity-boundary progress | Necessary before calibration, not before a qualified class/group contract. |

A structural contract does not require DLMn latent state. A later synthetic
motor-neuron-output-event fixture could test identity→target dispatch without
deriving an event from Phase 6C or Phase 8G; it must carry
`SYNTHETIC_MOTOR_OUTPUT_INTERFACE_TEST`-like provenance distinct from genuine
model output. A dynamic muscle model would additionally need an explicit
output operator, NMJ/muscle response assumptions and validation. A receipt-
only muscle endpoint could be used strictly as an interface test, **not** as
activation; a dimensionless activation model adds gain/decay, contraction
adds mechanics, and an actuator adds geometry/force. None is Phase 8J work.

## Bounded Phase 8K proposal and scientific boundary

Pin a versioned **no-dynamics** `motor_neuron_muscle_target_contract_v1` for
the two TTMn and ten DLMn body IDs, sourced from the replayed MaleCNS motor
neural contract plus separately cited primary innervation evidence. Store
body/type/side, target **muscle class or group**, mapping confidence,
unresolved exact fiber/laterality fields, evidence identity, and an explicit
`no_output_or_muscle_dynamics` boundary. Verify deterministic identity/replay
and fail on unsupported one-to-one fiber assignments. Do not create a
muscle response, spike converter, output-event fixture, gain, delay, force,
or production adapter in Phase 8K.

MaleCNS supplies central identities and chemical edges; the literature
supplies class-level muscle innervation and physiology. NeuroFly's TTMn state
and PSI/DLMn receipts remain model artifacts. There is no observed biological
motor-neuron output in the canonical sensory experiment, no calibrated
neuromuscular transfer, and no behavior inference.
