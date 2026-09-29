# Phase 8M — motor-neuron output-source readiness

**Assessment:** TTMn output rule is possible only as an explicitly
`EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT`, and remains uncalibrated;
DLMn output is not derivable from the current path records and requires a
separate neural-input/state model before a model-derived output rule can be
considered. A common output-event envelope is suitable for future use, but
does not imply a common generator. The next bounded phase is a TTMn-only
exploratory threshold-rule definition and test. This is a read-only assessment;
no model, event schema, artifact, or production path was changed.

## Repository and replay gate

The audit began at clean `main`, HEAD
`3f77f1d79fea954d1e4e6e63750c418d08a31199`, matching `origin/main`; the latest
commit contains the Phase 8L code, tests, and assessment despite its misleading
commit subject. `git diff --check` passed. Offline replays passed for:

| Source | Identity | Replay finding |
| --- | --- | --- |
| Phase 8L synthetic output/target dispatch | Artifact `8e53c6bd224a82c9cbef2b51a82fc917fe993da73ff64cc4c894870dfc4abff8` | 8 fixtures; 18 synthetic origins and 18 target-dispatch receipts; integrity passed |
| Phase 8K target contract | Contract `5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0` | 12 no-dynamics target associations; replay passed |
| Phase 8E motor pathway contract | Contract `a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c` | MaleCNS v1.0 source and 18 structural chemical edges validated; replay passed |

Phase 8I and Phase 8C/8H remain committed context. The canonical Phase 7O
condition remains silent; Phase 8M does not change or reinterpret it.

## Current TTMn representation

The implementation in `src/neurofly/motor_pathway.py` declares
`ttmn_dimensionless_event_integrator/phase6c_v1`. It accepts only validated
DNp01 `SpikeEvent`s from the same upstream run, maps each event by the pinned
body identity, and updates the target TTMn state on the stored boundary:

```text
x[n] = x[n−1] * exp(−dt_ms / tau_motor_ms)
       + event_count[n] * event_gain
```

The reference `tau_motor_ms=10.0` and `event_gain=0.25` are explicitly
`MODEL_ASSUMPTION`s. The state unit is `dimensionless`; it is not Vm, firing
rate/probability, calcium, neurotransmitter release, a TTMn action potential,
or muscle activation. The route's MaleCNS structural counts (70 and 20) are
not used numerically. The Phase 6C result serializes
`SIMULATED_EXPLORATORY_TTMN_MODEL_STATE` and contains no TTMn output-event
generator or refractory/spiking semantics.

### TTMn output options

| Option | Assumptions required | Assessment |
| --- | --- | --- |
| Any `x > 0` emits an event | One categorical state-to-output assertion and a sampling rule | Reject. Since positive impulses decay rather than reset, this can emit at every positive sampled boundary; it is not a one-event-per-neural-response rule. |
| Threshold `x ≥ θ` emits an event | A dimensionless free `θ`, interpretation of `x` as an output proxy, crossing/re-arm rule, and boundary convention | A transparent exploratory rule is definable, but not calibrated. `θ` cannot be inferred from 0.25, structural count, or physiology. Repeated output requires an explicit crossing rule rather than firing on every above-threshold sample. |
| Each incoming DNp01 event directly implies one TTMn output event | One-for-one transfer/reliability and same-boundary timing assertions | Not a conversion from the Phase 6C state: it bypasses `x` and effectively replaces the integrator's output semantics. The fast pathway literature makes this a conceivable separate abstraction, not a validated consequence for these exact MaleCNS bodies. |
| Add TTMn spiking dynamics | Membrane/input model, rest, threshold, reset, refractory period, time constants, coupling/sign and timing choices | Not justified by the current state or identity-bound evidence; substantially more free parameters. |
| No output derivation | None | Safest production interpretation; canonical sensory output stays silent. |

Primary evidence supports a fast, reliable *pathway output*: Tanouye and Wyman
recorded GF axon action potentials and TTM/DLM muscle potentials, and reported
stable short-latency responses and high-frequency following. Allen and Murphey
demonstrated that the adult GF–TTMn connection has functional electrical and
cholinergic chemical components; thoracic motor-neuron stimulation evoked
muscle responses in their preparation. These findings establish pathway and
class physiology, not a calibrated relationship between Phase 6C's
dimensionless `x` and an action potential of MaleCNS body 800146 or 804642.
The Phase 6C direct-event pass-through would also discard the state model
rather than derive output from it. [Tanouye & Wyman (1980), DOI
10.1152/jn.1980.44.2.405](https://doi.org/10.1152/jn.1980.44.2.405); [Allen &
Murphey (2007), DOI 10.1111/j.1460-9568.2007.05686.x](https://doi.org/10.1111/j.1460-9568.2007.05686.x).

## Current DLMn representation

Phase 8G's `dlmn_routed_event_v1` means that a deterministic software path
through the selected, pinned `DNp01→PSI→DLMn` edges was traversed. It is an
`EXPLORATORY_ROUTED_MOTOR_EVENT` record, not a PSI or DLMn `SpikeEvent`, EPSP,
membrane state, input-current estimate, or motor-neuron output. The active
relay has 4 DNp01→PSI and 10 PSI→DLMn edges, zero added software delay, no
synaptic gain, no state, and no PSI↔PSI propagation. Structural edge counts
remain metadata. Phase 8I composes these discrete path records beside—not
into—the continuous Phase 6C TTMn state. Phase 8L remains an independent,
synthetic-only motor-neuron-output target-dispatch fixture.

### DLMn output options and path multiplicity

| Option | Assumptions required | Assessment |
| --- | --- | --- |
| Every DLMn path receipt becomes an output event | Assert that software path traversal means a DLMn fired | Reject. This relabels routing as physiology and makes the number of traversed graph paths look like spike count. |
| Collapse coincident receipts into one output | Define coincidence window, deduplication key, and how distinct origins/routes combine | Reject as a shortcut. It can erase origin/path identity or merge unrelated events; no such biological integration rule is in Phase 8G. |
| Dimensionless DLMn integrator | Define what constitutes neural input, PSI output semantics, sign, event aggregation, a gain and decay constant; then define a DLMn output rule | Not identifiable from path records. It would add free parameters and assumptions at both PSI and DLMn stages. |
| DLMn LIF/spiking model | Above input semantics plus rest, membrane/synaptic time constants, threshold, reset, refractory period, coupling and timing | Not ready. DLMn class-level physiology does not identify these for the ten MaleCNS bodies or the Phase 8G records. |
| No output derivation yet | None | Required at the current interface. Keep the ledger as a path ledger. |

One DNp01 origin produces two PSI receipts and ten DLMn *path records across
ten target bodies*. Thus ten is not a DLMn spike count or a strength value.
For simultaneous bilateral origins, records at the same target and boundary
remain origin-distinct; that does not imply two spikes without a DLMn response
model. In the current pinned active topology, the two PSI branches target
disjoint DLMn body sets. Repeated or bilateral origins can still produce
multiple receipts at the same DLMn over time or at a shared boundary. Any
future DLMn state would need explicit pre-synaptic event semantics and a
rule for combining inputs; it must not infer current or spike multiplicity
from route count. A future model-derived output needs a DLMn neural
representation first, but a latent state alone is not sufficient until its
input/operator and output rule are defined.

## Biological output evidence versus MaleCNS identities

The pinned MaleCNS motor contract establishes the 2 TTMn, 2 PSI and 10 DLMn
body identities, sides, annotations, and central chemical structural edges.
It does not measure membrane traces, firing thresholds, input-output gains,
or body-specific action potentials. Literature labels and cell classes do
not provide an automatic one-to-one crosswalk to every pinned body.

For DLM motor neurons, Hürkey et al. recorded adult MN1–5 output during
tethered flight through identified target muscle fibers and reported tonic
firing, current/frequency relationships, and firing rates. This is direct
class-level evidence that DLM motor neurons can produce action potentials,
but it concerns flight-motor patterns—not PSI route receipts—and does not
identify a generator for the ten MaleCNS `DLMn a,b`/`c-f` bodies. Fayyazuddin
et al. reported a GF/PSI-pathway excitatory response in the historical MN5
preparation; that is not a body-resolved conversion rule for the pinned
contract. [Hürkey et al. (2023), “Gap junctions desynchronize a neural circuit
to stabilize insect flight,” DOI
10.1038/s41586-023-06099-0](https://doi.org/10.1038/s41586-023-06099-0);
[Fayyazuddin et al. (2006), DOI
10.1371/journal.pbio.0040063](https://doi.org/10.1371/journal.pbio.0040063).

These studies support the biological relevance of action-potential output as
a concept, not the mapping from `dlmn_routed_event_v1` to a DLMn action
potential. The historical four-cell computational GFS model is precedent for
conductance-based modelling, not a source of measured MaleCNS pair parameters;
its fitted/estimated conductances and delays must not be imported as direct
measurements. [Augustin, Zylbertal & Partridge (2019), DOI
10.1523/ENEURO.0423-18.2019](https://doi.org/10.1523/ENEURO.0423-18.2019).

## Timing, provenance, and parameter identifiability

For a future TTMn threshold operator, the reproducible timestamp would be the
first integer boundary `n` at which the declared threshold-crossing condition
is met. That is a model detection boundary, not a measured TTMn spike time or
an axonal/NMJ delay. Directly copying the DNp01 input time would instead be a
separate same-boundary transmission assumption. Phase 8G's same-boundary
route timestamp remains software bookkeeping, not instantaneous biological
transmission. Do not substitute composite stimulus-to-muscle latency or
contraction/behavior timing for a neural output delay.

If a later generator is approved, distinguish its model-derived event
provenance (proposed `EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT`) from
`SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST`,
`SIMULATED_FROM_SENSORY_EXPERIMENT`, and
`EXPLORATORY_ROUTED_MOTOR_EVENT`. It must reference the source model/result,
model/config identity, neuron body, rule identity, integer boundary, and
originating evidence/state. It may not claim an observed biological action
potential. Phase 8L's synthetic fixture must remain synthetic and must not be
populated from either current model output.

| Parameter / meaning | TTMn status | DLMn status |
| --- | --- | --- |
| Existing state meaning | Defined only as a dimensionless model state; physiological mapping `NOT_IDENTIFIABLE` | No DLMn state exists; route record is not a neural quantity |
| State/input-to-output threshold | `NOT_IDENTIFIABLE`; any `θ` is a free model assumption | `NOT_IDENTIFIABLE`; no neural state or validated input exists |
| Input integration / gain | Existing Phase 6C `tau=10 ms`, `gain=0.25` are model assumptions, not output calibration | `NOT_IDENTIFIABLE`; routed receipts have no numerical input semantics |
| Reset / refractory period | `NOT_IDENTIFIABLE`; not part of Phase 6C | `NOT_IDENTIFIABLE`; no DLMn model |
| Output delay | `NOT_IDENTIFIABLE` for an exact body/operator; same-boundary is only an explicit software assumption | `NOT_IDENTIFIABLE`; relay zero-added-delay is not neural timing evidence |
| State-to-output gain / event amplitude | `NOT_APPLICABLE` to a unitary threshold-crossing record; physiological efficacy remains `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE`; must not derive from counts or route multiplicity |
| Event meaning | Possible only as a declared exploratory output abstraction, not a biological AP | Not currently defined; path receipts cannot be promoted to output events |

## Evidence table and assumption budget

| Branch | Current representation / biological quantity | Output-event and threshold evidence | Timing / convergence | New assumptions and identifiability | Readiness |
| --- | --- | --- | --- | --- | --- |
| TTMn | `x_TTMn`, dimensionless exploratory state; no physiological quantity calibrated | Fast GF→TTMn pathway and muscle responses support the class pathway; no evidence maps `x` or a threshold to exact-body TTMn firing | Current state update is same-boundary; no output timestamp rule exists | Threshold route: one free dimensionless threshold plus crossing/re-arm semantics; threshold and refractory are `NOT_IDENTIFIABLE`. LIF adds multiple unidentified parameters. | `TTMN_EXPLORATORY_OUTPUT_RULE_POSSIBLE_BUT_UNCALIBRATED` |
| DLMn | Discrete `dlmn_routed_event_v1` graph/path record; no neural state quantity | DLM MN1–5 action potentials are documented at class level, but no evidence makes a Phase 8G route receipt a DLMn output | Multiple origins may coincide at target/time; no DLMn input summation or deduplication semantics | Must first define PSI neural-output/input semantics and DLMn integration; gain, time constant, threshold/reset, refractory, delay and any route aggregation are `NOT_IDENTIFIABLE`. | `DLMN_LATENT_NEURAL_STATE_REQUIRED` |

For TTMn, the smallest possible output generator is a threshold-crossing rule
over `x`, with a required explicit dimensionless threshold and deterministic
crossing/re-arm semantics. It has one numeric free parameter, plus categorical
semantics. This is a model hypothesis, not a calibrated physiological model.
The direct DNp01-to-TTMn pass-through uses no numeric parameter but assumes a
one-for-one transfer and bypasses the existing TTMn state; it is not the
selected conversion. A new LIF layer would add at least rest, threshold,
reset, refractory period, membrane time constant, input coupling/gain, and
potential synaptic time constant/delay.

For DLMn, receipt-to-event conversion could appear to have zero numeric
parameters, but would make an unsupported path-to-spike assertion and needs
path deduplication/convergence semantics. A latent-state model would require
an explicit PSI-to-DLMn model input, event/sign/aggregation policy, at least
an input gain and decay constant (if integrating), and an output threshold or
spiking rule. A LIF adds membrane, reset and refractory parameters. These are
not identified by the cited class-level recordings or MaleCNS counts.

## Decisions and bounded next phase

**TTMn output source:** `TTMN_EXPLORATORY_OUTPUT_RULE_POSSIBLE_BUT_UNCALIBRATED`.
**DLMn output source:** `DLMN_LATENT_NEURAL_STATE_REQUIRED`.
**Output-event schema:** `SHARED_OUTPUT_EVENT_SCHEMA_READY`. A future common
envelope can carry neuron identity, model/result/config identity, output-rule
identity, integer step/time, and provenance while allowing distinct
TTMn/DLMn generators. Shared serialization does not imply shared dynamics.
**Next boundary:** `DEFINE_TTMN_EXPLORATORY_OUTPUT_RULE`.

Bounded Phase 8N proposal: specify and test a TTMn-only threshold-crossing
operator over the existing Phase 6C dimensionless state, using an explicit,
required threshold config value classified `MODEL_ASSUMPTION` and no default
presented as calibrated. Use only Phase 8B/8I synthetic fixtures for the
nonzero test path; keep the Phase 7O/8C production result unchanged and silent.
Persist model-derived exploratory output events with source state/run and
rule provenance, and verify integer boundary/re-arm semantics and replay. Do
not add DLMn dynamics, derive events from Phase 8G receipts, connect to Phase
8L target dispatch, or add muscle, NMJ, force, or behavior. Phase 8N must not
choose a threshold to obtain a preferred downstream or visible response.

The MaleCNS contract supplies neural identity and central chemical topology;
literature supplies pathway and cell-class physiology; the proposed threshold
operator would be a NeuroFly model assumption. None of the three categories
can substitute for another. The canonical sensory experiment's zero DNp01
events remain zero TTMn state and zero PSI/DLMn receipts. No motor-neuron
output conversion or physiological output event is demonstrated by Phase 8M.
