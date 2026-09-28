# Phase 8F — PSI/DLMn event-model readiness

**Assessment:** `READY_FOR_SYNTHETIC_PSI_DLMN_EVENT_RELAY`;
`STRUCTURAL_ONLY_EXCLUDED_FROM_FIRST_MODEL` for supplemental PSI↔PSI;
`ZERO_ADDED_DELAY_EXPLORATORY_ASSUMPTION`; `EVENT_RELAY_NO_LATENT_STATE`.
This is a design decision. No PSI or DLMn dynamics, artifacts, or route
implementation were added.

## Audited source and existing event boundary

The immutable Phase 8E `motor_neural_pathway_contract_v1` replays offline with
contract ID
`a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c`,
canonical query-response SHA-256
`845c1c1ddc60183fd02f8ac2ceaac5e1a16cba34c803707fb974e7b52861e43e`,
and annotation SHA-256
`2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`.
It supplies exact body/type/side identities and VNC chemical `ConnectsTo`
counts. It contains 2 DNp01, 2 TTMn, 2 PSI, and 10 DLMn nodes. Its 18
chemical edges comprise 16 historical pathway edges and two separately
labeled supplemental PSI↔PSI edges. The counts are structural metadata.

Phase 8A chose `DNp01_SPIKE_EVENT_ONLY` for the motor input boundary. A
`SpikeEvent` has body ID, graph node index, neuron type, integer boundary
`step`, and `time_ms`; the DNp01 LIF emits it at the end of an integration
interval. Phase 8B validates explicitly synthetic DNp01 events with
`SYNTHETIC_MOTOR_INTERFACE_TEST` provenance. Phase 8C accepts only genuine
spike records from one selected persisted Phase 7O condition and labels the
source `SIMULATED_FROM_SENSORY_EXPERIMENT`. The canonical Phase 7O conditions
contain no DNp01 spikes, so the production TTMn state remains zero. No
subthreshold DNp01 voltage, external drive, or filtered state becomes a motor
event.

The first PSI/DLMn slice should use the existing Phase 8B synthetic source
boundary. A later production adapter may accept genuine persisted DNp01
events under its own provenance checks; it is outside this first slice.

## Exact candidate graph from the pinned contract

The proposed Phase 8G active route groups are exactly `dnp01_to_psi` and
`psi_to_dlmn`. Each row below is a directed chemical source observation, not
a calibrated functional connection. Sides are taken from source nodes, not
inferred from route direction.

| Route group | Source → target | Source/target sides | Structural count |
| --- | --- | :---: | ---: |
| DNp01→PSI | 10001 → 802401 | R→L | 3 |
| DNp01→PSI | 10001 → 903327 | R→R | 2 |
| DNp01→PSI | 10010 → 802401 | L→L | 9 |
| DNp01→PSI | 10010 → 903327 | L→R | 2 |
| PSI→DLMn | 802401 → 801970 | L→L | 17 |
| PSI→DLMn | 802401 → 801998 | L→R | 40 |
| PSI→DLMn | 802401 → 802544 | L→R | 67 |
| PSI→DLMn | 802401 → 803048 | L→R | 35 |
| PSI→DLMn | 802401 → 1050014552 | L→R | 64 |
| PSI→DLMn | 903327 → 800718 | R→L | 68 |
| PSI→DLMn | 903327 → 800890 | R→L | 24 |
| PSI→DLMn | 903327 → 801295 | R→R | 26 |
| PSI→DLMn | 903327 → 801895 | R→L | 58 |
| PSI→DLMn | 903327 → 803013 | R→L | 50 |

The Phase 6C DNp01→TTMn branch stays parallel and unchanged: 10001/R →
800146/R (count 70) and 10010/L → 804642/L (count 20). The supplemental
PSI↔PSI chemical rows, 802401→903327 (count 5) and 903327→802401
(count 17), remain in the source contract but are inactive in Phase 8G.
No direct chemical DNp01→candidate-DLMn edge was returned in the bounded
Phase 8E query.

## Sign and transmission evidence

For **all four DNp01→PSI pairs**, the appropriate classification is
`PATHWAY_POSITIVE_PAIR_UNRESOLVED`. Giant Fiber excitation drives the
classical PSI/DLM pathway, and electrical GF–PSI coupling has experimental
support, but no reviewed experiment measures the postsynaptic sign or
conductance of each of these four exact MaleCNS chemical pairs. The two
cross-side chemical rows in particular must not be assigned a measured
functional sign from a classic ipsilateral pathway diagram. Structural
counts 3/2/9/2 provide neither sign nor efficacy.

For **all ten PSI→DLMn pairs**, the appropriate classification is
`SUPPORTED_POSITIVE_AT_CLASS_LEVEL`, with exact-pair sign/efficacy unresolved.
[Fayyazuddin et al. (2006)](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.0040063)
identify a cholinergic PSI–DLM motor-neuron synapse and record an excitatory
postsynaptic potential in MN5 after Giant Fiber stimulation. MN5 supplies
DLM a,b; that preparation does not uniquely identify one of the two MaleCNS
`DLMn a, b` bodies, and it does not record the eight listed `DLMn c-f` pairs.
The c-f assignment therefore rests on pathway/class evidence rather than a
pair-resolved EPSP. No EPSP magnitude becomes a NeuroFly route gain.

[King and Wyman (1980)](https://doi.org/10.1007/BF01205017) establish the
Giant Fiber motor-neuron and interneuron branch anatomy;
[Phelan et al. (1996)](https://doi.org/10.1523/JNEUROSCI.16-03-01101.1996)
support electrical coupling in the Giant Fiber system. Those literature
observations are distinct from the MaleCNS chemical edge inventory. The
[Augustin et al. (2019)](https://doi.org/10.1523/ENEURO.0423-18.2019)
four-cell conductance model is a modelling precedent, not a measurement of
these MaleCNS pairs. Its fitted/estimated parameters are not imported.

The proposed relay uses neither a signed numerical transfer nor an
electrical-synapse model. A route token is a software trace of a selected
source path; its presence must not be reported as a measured PSI or DLMn
spike, a confirmed functional chemical synapse, or a biological response.

## Model alternatives and assumption budget

| Option | New numerical free parameters, minimum | New categorical/model rules | Assessment |
| --- | ---: | --- | --- |
| No PSI/DLMn model | 0 | None | Preserves evidence but cannot exercise the newly pinned identity and fan-out path. |
| Pure routed-event ledger at PSI and DLMn | 0 | One deterministic path-token rule; same-boundary/no-added-delay convention; active-group policy excluding PSI↔PSI | Preferred first architecture test. It yields records, not PSI/DLMn state or biological spikes. |
| Dimensionless PSI and DLMn event integrators | At least 4: a decay time and event gain for each node class | Needs an additional PSI-state→outgoing-event threshold/rule or a continuous PSI→DLMn coupling rule; at least one more free numeric mapping is likely | Phase 6C-like but its parameters and PSI output operator are unidentified. A PSI state without an output rule cannot causally feed DLMn. |
| PSI and DLMn LIF models | At least 12 cell parameters shared by the two classes (rest, threshold, reset, refractory, membrane tau, synaptic tau per class), plus at least two input coupling gains | Requires electrical/chemical input abstractions and spike-generation semantics | Disproportionate unmeasured parameter burden for a routing test. |

A DLMn-only event-receipt/count record is sufficient for the first slice.
It must be described as the number of routed *path records* arriving at a
named DLMn, not a physiological input count, latent neural state, or DLMn
spike count. An integrator or LIF could be assessed later against suitable
measurements and an explicit output operator.

## Proposed first relay semantics

One validated synthetic DNp01 source event at boundary `(step, time_ms)`
produces one `EXPLORATORY_ROUTED_MOTOR_EVENT` PSI receipt **per verified
DNp01→PSI edge**. Each PSI receipt then produces one named DLMn receipt per
verified outgoing PSI→DLMn edge. Both hops retain the originating DNp01
event ID and exact source-path IDs. Each emitted record carries the same
stored step/time under a declared zero-added-delay *software assumption*.
There is no gain, amplitude, structural-count multiplication, stochastic
release, threshold, state decay, or physiological PSI spike generation.

This is path-token propagation, not a claim that each input evokes a PSI
action potential. Distinct simultaneous DNp01 origins remain distinct:
there is no deduplication into one PSI spike, no merger by target/time, and
no extra fan-out beyond the source graph. Thus one 10001 or 10010 input event
would produce two PSI receipts and ten DLMn path receipts; simultaneous
bilateral inputs would produce four PSI and twenty DLMn path receipts. Those
numbers count graph paths, not biological output events. Zero source events
produce zero downstream records.

The relay has no new **numeric free parameter**. It makes two new model
assumptions: (1) deterministic one-token-per-selected-edge traversal and
(2) zero added time between validated source and routed records. Choosing
the 14 active edges while leaving the reciprocal PSI rows structural-only
is an explicit topology policy. It is not an efficacy inference.

### Delay decision

Pair-specific DNp01→PSI and PSI→DLMn neural transmission delays remain
`NOT_IDENTIFIABLE`. Muscle-potential or behavioral latencies combine several
steps and cannot be substituted. A shared delay would add at least one free
duration and a boundary-rounding rule without relevant calibration. For the
first path ledger, `ZERO_ADDED_DELAY_EXPLORATORY_ASSUMPTION` is the smallest
testable convention. Both routed records use the source DNp01 event boundary
exactly; this is not a claim of instantaneous biological transmission.

### Supplemental PSI↔PSI decision

The reciprocal PSI rows are `STRUCTURAL_ONLY_EXCLUDED_FROM_FIRST_MODEL`.
An immediate relay that traverses both could re-enter the originating PSI
indefinitely at the same boundary. A future recurrent model would have to
specify at least a finite hop policy, one-use-per-origin-edge policy, a
positive step transition, or refractory/deduplication semantics and justify
its biological interpretation. None is identified here. The first relay
is acyclic by construction and never reads the `psi_to_psi_supplemental`
group for event propagation; its source evidence remains intact.

## Proposed contracts for Phase 8G

These are schema proposals, not implemented records. Both reference the
exact pinned motor contract ID and resolve every node, side, type, and edge
from that contract. The originating fixture/source record remains immutable.

`psi_routed_event_v1` should store: its deterministic event ID; originating
DNp01 source-event ID, body, step and time; `origin_source_kind` equal to
`SYNTHETIC_MOTOR_INTERFACE_TEST` for the first slice; immediate DNp01 source
body; target PSI body/type/side; selected DNp01→PSI edge ID and query group;
source and routed step/time; motor contract ID and response hash; and
`event_semantics=EXPLORATORY_ROUTED_MOTOR_EVENT`. It should carry no PSI
`SpikeEvent` or new node index, because no PSI simulation graph exists.

`dlmn_routed_event_v1` should store: its deterministic event ID; parent PSI
receipt ID; originating DNp01 event ID/body and provenance; immediate PSI
source body/type/side; DLMn target body/type/side; both selected edge IDs as
the path identity; exact step/time; motor contract ID and response hash; and
the same exploratory routed-event semantics. No amplitude, physiological
EPSP, biological DLMn spike, or muscle result is implied.

Future source kinds must remain distinct. `SYNTHETIC_MOTOR_INTERFACE_TEST`
describes a Phase 8B-style test fixture;
`SIMULATED_FROM_SENSORY_EXPERIMENT` may describe only genuine persisted
upstream DNp01 spike records validated by a production adapter. The derived
`EXPLORATORY_ROUTED_MOTOR_EVENT` label describes the new path record, not its
origin. The Phase 7O canonical artifact remains a zero-event source and is
not altered or used as a synthetic fixture.

## Exact Phase 8G gate and test plan

Phase 8G should implement **only** the synthetic, provenance-explicit,
zero-added-delay routed-event ledger over the four `dnp01_to_psi` and ten
`psi_to_dlmn` chemical routes. It should load and validate the immutable
Phase 8E contract offline. Phase 6C's DNp01→TTMn integrator remains a
parallel, unchanged branch; no PSI↔PSI, LIF, latent PSI/DLMn state, muscle,
behavior, or production Phase 7O→PSI adapter is in the first slice.

The bounded fixtures/tests should cover zero input; one 10001 event; one
10010 event; bilateral events; the exact two-PSI/ten-DLMn path count per
single source event; all same-side and cross-side route identities; event
step/time and immutable origin/path IDs; one record per selected edge/path
without structural-count scaling; rejection of wrong contract ID, body/type/
side, source event, extra route, or tampered provenance; and deterministic
serialization/replay. Assert that supplemental PSI↔PSI causes no recursion
or extra record, and that Phase 8B synthetic events cannot masquerade as
Phase 7O events. No network is required during ordinary replay.

## Scientific boundary

MaleCNS supplies names, sides, directed chemical connections, and structural
counts. Primary literature supplies class/pathway anatomy, coupling evidence,
and PSI→DLMn excitatory physiology. The proposed event ledger supplies only
NeuroFly assumptions about which verified paths a test token traverses and
how its timestamp is copied. It does not represent pair-specific electrical
conductance, chemical efficacy, transmission latency, PSI/DLMn physiological
spikes, DLM muscle activation, force, wing motion, or behavior.
