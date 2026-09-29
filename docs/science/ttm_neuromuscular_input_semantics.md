# Phase 8V — TTM neuromuscular-input semantics and contract readiness

**Assessment:** `PASS`, documentation-only readiness assessment. Recommend a bounded
abstract TTM-class electrical-input event, with no magnitude or release claim,
before any electrical-model implementation. A separate, explicit TTM-class
to G1 proxy mapping is required before a G1 model can consume that event.
Neither contract is implemented here.

## Repository gate and audited authority

The audit began on clean `main` at
`bd068cf998fd03848a1ae007b7e6ba913d1c5a5b`, equal to `origin/main`.
Phase 8U, 8S and 8Q were committed; `git diff --check` passed. Offline replays
passed with unchanged identities and hashes:

| Layer | Canonical artifact ID | Replay result |
| --- | --- | --- |
| Phase 8U mapping | `f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f` | Nine mappings; zero formal-ready comparisons. |
| Phase 8S observations | `5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f` | Nine observations, including their source/protocol classifications. |
| Phase 8Q receipts | `e04803f60304f58d0e6d27fdea5d15debb60358b46721caac09f10165c6df9c4` | Eight receipts; full Phase 8O/8N and target-contract ancestry verified. |

The audit inspected receipt construction/validation, the Phase 8P assessment,
Phase 8S definitions and scope, Phase 8T feasibility, Phase 8U mapping/blocker
definitions, Phase 8N generator semantics, and Project Context. Existing
`SpikeEvent`, `DeliveredSynapticEvent` and `TTMnInputEvent` types are neural
model-specific precedents, not NMJ electrical-input contracts. In particular,
their coupling/gain fields must not migrate into a muscle interface merely
because they already exist. Provenance is expressed by explicit strings in
the relevant modules, not a universal biological-event framework.

This assessment uses the already pinned evidence scope, not new physiological
claims. The [Phase 8S manifest](ttm_g1_electrophysiology_observation_contract.md)
identifies Koenig & Ikeda 2007 (DOI `10.1152/jn.01258.2006`), Koenig & Ikeda
2005 (DOI `10.1152/jn.00323.2005`, restricted verification), and Kadas et al.
2019 (DOI `10.1523/ENEURO.0181-19.2019`). No new release/transmitter/receptor
claim or parameter is needed to recommend a deliberately nonphysiological
token; therefore no new biological source research is required here.

## Exact current software and biological boundaries

`ttm_neuromuscular_input_receipt_v1` has provenance
`EXPLORATORY_NEUROMUSCULAR_INPUT` and semantics
`EXPLORATORY_TTM_NMJ_INPUT_HANDOFF_RECEIPT_ONLY`. Construction retains the
parent dispatch/output identities, source artifact/config/result hashes,
fixture/run ancestry, body/type/neural side, exact target association and its
qualified/unresolved fields, and integer `step`/`time_ms`. Its boundary is
`HANDOFF_RECORD_ONLY_NO_RELEASE_OR_MUSCLE_RESPONSE_CLAIM`.

Only `800146`/R and `804642`/L TTMn associations are accepted. `HIGH`
class/pathway confidence and qualified ipsilateral target-side inference are
not peripheral tracing. Exact fiber and endpoint are unresolved. The receipt
has no release probability, success, transmitter amount, amplitude, current,
conductance, voltage, transfer delay or quantal count. It copies dispatch time
as bookkeeping only. Eight canonical receipts across six independent fixtures
are four per body; these counts are not physiological reliability or rate.

Ancestry remains synthetic DNp01 fixture
(`SYNTHETIC_MOTOR_INTERFACE_TEST`) → Phase 6C dimensionless TTMn state →
Phase 8N `EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT` → Phase 8O
`EXPLORATORY_MUSCLE_TARGET_DISPATCH` → Phase 8Q receipt. Phase 8N's threshold
is an uncalibrated model assumption, not a biological TTMn action-potential
criterion. No downstream abstraction repairs that upstream uncertainty.

Keep five objects distinct: motor-neuron output event, NMJ-input receipt,
biological release, postsynaptic conductance/current, and membrane response.
The proposed abstract-input branch is a deliberate software abstraction; it
does not assert traversal of the latter three biological steps.

## Candidate semantics, evidence and risk

Here, “constraints” means applicability of pinned evidence, not permission to
use a published observation as a model coefficient. No numerical choice is
made. “Resolved” is conditional on a future contract/model, not a change to
the immutable Phase 8U blocker records.

| Candidate | Biological claim / receipt implies successful transmission? | Free assumptions and evidence needed | Phase 8S constraints | Phase 8U blockers potentially addressed / remaining | Neutrality and scientific risk |
| --- | --- | --- | --- | --- | --- |
| A. Abstract electrical-input token | No release or response claim; **NO**. Means admission to a future model-input boundary only. | One-to-one input-admission convention; same-boundary model timing. Physical transformation remains unspecified. No physiological parameter evidence needed for these software conventions. | None supplies token magnitude or success. All nine retain their original meanings. | Narrows interface ambiguity only; `INPUT_SEMANTICS_UNDEFINED` remains for physical response mapping until a downstream transformation is declared. All model-quantity, release, protocol, operator and system-boundary blockers remain. | Model-family-neutral. Low claim burden, but redundant unless distinct from receipt delivery and explicitly free of physical magnitude. Recommended contract direction. |
| B. Fixed current pulse/kernel | **YES_AS_MODEL_ASSUMPTION** for a biological-inspired current transfer, not demonstrated biological success. | Event always contributes prescribed current; amplitude/unit, shape/duration, placement, timing and history policy. Would need matching electrical measurements or explicit free model assumptions. | No pinned injected-current waveform, current magnitude or membrane transfer parameters. Evoked voltage cannot isolate them. | A future explicit convention could define input semantics, but does not identify parameters. Release, protocol/operator, miniature/history and Kadas-boundary blockers remain. | Selects current-input capability and substantial assumptions. Not ready as an empirically parameterized contract. |
| C. Conductance transient | **YES_AS_MODEL_ASSUMPTION** that each event induces the chosen conductance, not known release success. | Peak conductance, reversal, kinetics, placement, timing, successful coupling and history policy; matched membrane/input evidence needed. | Prior equilibrium correction input is not a verified model reversal; response amplitude does not identify conductance. | Could define conductance semantics only after choices; release validation, model outputs, protocol/operator and wider timing blockers remain. | Requires conductance-compatible model. Greater mechanistic appearance than current evidence supports. Defer. |
| D. Explicit release/quantal event | **UNRESOLVED** until attempted versus successful release is separately defined; receipt alone says neither. | Release probability/sites/count, availability, spontaneous process, recycling/depression and quantal-to-electrical mapping. | Quantal/miniature/rate records are protocol-specific observations, not a coherent calibrated release model. | A genuine release model might address release/vesicle/history blockers, but a contract label alone does not. Protocol, measurement operators, parameter identifiability and Kadas scope remain. | Forces release-capable structure; highest assumption burden and premature for this slice. |
| E. Separate biological release interface | **UNRESOLVED**; an attempted-release instruction is not successful release. | Must define a generator and the exact biological quantity represented. Claiming measured release would require evidence/model capability not supplied by the receipt. | Observation metadata does not provide that generator. | No blockers resolved by an empty release envelope; useful only after release semantics exist. All current blockers remain. | Can modularize a later release model, but risks giving unsupported biology a formal label now. Defer. |
| F. Keep receipt non-electrical; hold | **NOT_APPLICABLE**. | No new model assumptions; future electrical-input contract still required. | Evidence unchanged. | Resolves none; preserves all blockers. | Neutral, scientifically safe, but adds no capability. Fall back if A cannot enforce its admission-only meaning. |

### Abstract event: useful distinction, not a receipt rename

Phase 8Q certifies that a validated output was presented to a supported TTM
interface. Proposed A records a **separate, explicit decision to admit that
handoff as a forcing token for future electrical-model experiments**. A
receipt does not implicitly grant that admission. The later model-specific
adapter would be required to declare how the token affects a state before it
can run. This separates stable causal ancestry from variable electrical-input
assumptions and permits independent model experiments without changing Phase
8Q. It adds no observed biology or numerical information.

The distinction is useful only with these enforceable exclusions: no electrical
state executes merely by emitting a token; no physical magnitude is attached;
no G1 destination is inferred; no token implies successful release or response;
and consumers cannot use it without separately identified input-transform
semantics. If a future implementation only changes a name while treating the
receipt as implicit current, reject it. “Electrical input” denotes intended
consumer domain, not measured electrical activity. Do not assign an amplitude
of `1.0`; one record is categorical event multiplicity, not one physical unit.

### Current, conductance and release options

Current and conductance are possible future modelling forms, not selected
families. Their amplitudes/waveforms, membrane coupling and input location
remain unidentifiable from Phase 8S alone. The 45 mV response is not current
or a voltage increment; the prior −10 mV correction input is not automatically
`E_rev`; the derived quantal estimate is not quanta per receipt. A separate
release-event envelope would add little until an attempted/successful-release
generator exists. A release-aware model could eventually address additional
observations but is not necessary for the abstract-token boundary.

## Timing, success, repeated events and laterality

Recommend `SAME_BOUNDARY_ZERO_ADDED_MODEL_DELAY`, explicitly labelled
`ZERO_ADDED_MODEL_DELAY_ASSUMPTION`. Proposed token `step`/`time_ms` copies
the receipt boundary exactly, without interpolation or a free delay parameter.
This is software scheduling, **not zero biological neuromuscular delay**.
Kadas composite stimulation-to-potential latency is not a token offset or an
isolated NMJ delay. Any later current/conductance waveform onset must be
separately declared in model-transform config; it must not silently shift the
source token's timestamp. Delay identification remains unresolved.

Recommend one valid receipt → one abstract input event, without a release
claim. Biological success is **not represented**, rather than `success=false`
(which would assert failure). Do not manufacture a success probability.
Discrete counts may index future forcing events; they do not encode current,
conductance, quanta or efficacy. Structural weights and target confidence have
no numerical role. Exact duplicate parents should fail closed; distinct
same-time parents must remain distinct, not coalesced.

Repeated receipts remain separate tokens and preserve history as ancestry,
without modelling history-dependent efficacy. They assert neither equal
responses nor absence of depression. Any history model belongs downstream
and must be explicit before repeated biological-response claims. Bilateral
tokens retain the two pinned target associations and qualified side status;
no side-specific physiology or new fiber identity is inferred.

## TTM class versus G1 proxy

The Phase 8Q receiving target is TTM **class**, not G1. Phase 8S G1
observations describe a fiber-specific preparation; they do not supply a
MaleCNS body-to-G1 crosswalk. Thus a class token can be pinned now, but cannot
automatically become G1 stimulation. Fiber selection and receiving location
remain unresolved. Even a lumped G1 voltage model must declare its receiving
compartment/proxy convention; a spatial model would need more location detail.

| Proxy question | Evidence and modelling justification | Required label and limits | First exploration readiness |
| --- | --- | --- | --- |
| TTM-class handoff → G1 proxy input | Phase 8S supports G1 as a specific experimentally studied fiber; representative innervation is not identical all-fiber electrophysiology. Using its preparation as a reduced observation-model domain could be a deliberate exploratory choice, not inferred anatomy. | Future explicit `MODEL_ASSUMPTION` mapping, conceptually `G1_OBSERVATION_PROXY_FOR_TTM_CLASS`; identify selected model compartment, both source/target scopes, source contract and unresolved side/body correspondence. | `G1_PROXY_REQUIRES_EXPLICIT_MAPPING_CONTRACT`. Not adopted in Phase 8V or authorized implicitly by the abstract-input contract. |
| What proxy would permit | Experiments on an explicitly selected G1-like electrical abstraction after input transformation, model and observation operators are specified. | May claim a proxy model response only; no exact traced G1 endpoint, whole-TTM response or side-specific physiological calibration. | Conditional future use only; still zero formal-ready comparisons. |
| What proxy cannot repair | No pinned fiber-specific synaptic placement or exact-body parameters; observation protocol and operators are incomplete for several targets. | Must preserve unknowns; no force, whole-muscle equivalence, release-success inference or Kadas timing equivalence. | Additional mapping/input/model requirements remain independent. |

Class-level abstract-input identity should **not** depend on an invented G1
mapping. A later explicit proxy mapping would have its own identity and
provenance, permitting different model domains without rewriting receipts or
class tokens. This is why pinning the class interface need not wait for G1
mapping, while actual G1 consumption must wait.

## Assumption budget and parameter location

Counts below enumerate design categories for the stated options, not a count
of identifiable biological parameters. Shape/duration can be one declared
kernel specification; doing so fixes assumptions rather than measuring them.

| Option | Additional design categories beyond receipt | Count | Capability / claim budget |
| --- | --- | ---: | --- |
| Abstract token | Admission convention; zero-added model delay. | 2 | A validated handoff was admitted as one future model forcing token; no response or release. A G1 proxy is separate, not included. |
| Fixed current | Successful model coupling; magnitude/unit; waveform; duration; timing; placement; history policy. | 7 | A declared exploratory current input, not measured NMJ current or muscle depolarization. |
| Conductance | Successful model coupling; peak conductance; reversal; kinetics; timing; placement; history policy. | 7 | A declared model conductance transient; not measured transmitter release. |
| Quantal/release | Attempt/success law; sites/count; availability; spontaneous process; recycling/depression; quantal electrical mapping; timing; placement. | 8+ | Model-generated release/quantal output only after those mechanisms exist; no physiology validation from an envelope alone. |
| Separate release envelope | Biological quantity; generation/attempt-success semantics. | 2+ plus generator | No new quantitative capability without a generator; premature now. |
| Hold | None. | 0 | Handoff bookkeeping only. |

Amplitude, unit-bearing coupling, waveform, membrane properties, eventual
physical/model lag, and history laws belong in a **future electrical-model
input-transformation config**, identified with the model run. They belong
neither in Phase 8Q, nor in Phase 8S evidence, nor in the abstract token's
identity. Observation/calibration config cannot silently choose the input
rule. Changing transform parameters must change model/config identity, while
the same admitted token can remain the same causal input. No such config or
parameter values are defined here.

Model-family neutrality is therefore feasible: a future phenomenological
kernel, passive-current model or conductance model may each explicitly map
the same abstract event differently. The contract chooses no transformation
and guarantees no equivalence between those models. More mechanistic models
can later add an explicit release boundary without retroactively relabelling
the token as a release event.

## Consequences for the pinned mappings

Phase 8U remains unchanged. Phase 8V is not a blocker migration. A future
abstract input contract would establish event admission, but **would not by
itself eliminate** `INPUT_SEMANTICS_UNDEFINED` for electrical predictions:
the physical transform and G1 scope are still unspecified. All nine mappings
retain current-model comparability false and zero formal-ready status.

`MODEL_QUANTITY_ABSENT` requires an actual model output, not a token;
`RELEASE_SEMANTICS_ABSENT` requires genuine release/quantal semantics;
`PROTOCOL_MATCH_UNRESOLVED` and missing operators require separate source and
measurement work; spontaneous/history/vesicle blockers remain; Kadas
`SYSTEM_BOUNDARY_MISMATCH` requires the wider experimental start boundary.
The prior equilibrium-input record remains analysis context only. No voltage,
latency, miniature, quantal, depression or recycling comparison becomes ready.

## Candidate input contract and provenance (proposal only)

A future `ttm_exploratory_electrical_input_v1` could contain only:

- Schema/version and deterministic input identity covering semantic content.
- Parent receipt ID and source Phase 8Q artifact/hash reference; source output,
  fixture/run and generator ancestry recoverable through that validated parent.
- Exact TTM target-contract/association references and qualified target scope,
  without new fiber/side inference.
- Integer step/time, an explicit same-boundary timing-policy identity, and
  `ZERO_ADDED_MODEL_DELAY_ASSUMPTION` (categorical, no delay parameter).
- Input semantics `ABSTRACT_MODEL_FORCING_TOKEN`, amplitude semantics
  `ABSENT_NOT_PHYSICAL_MAGNITUDE`, and biological-success semantics
  `NOT_REPRESENTED_NO_RELEASE_CLAIM`.
- Distinct proposed provenance `EXPLORATORY_ELECTRICAL_INPUT`, downstream of
  `EXPLORATORY_NEUROMUSCULAR_INPUT`, and no-release/no-response/no-G1-inference
  boundaries.

These are proposed fields, not a schema implementation. Parent/target/source
identity and policy must be validated; no generic physiological defaults or
amplitude `1.0` are permitted. The token adds consumer-admission provenance,
not empirical-observation provenance. It must reject wrong source kinds,
Phase 8L synthetic-output dispatch substitutes and DLM targets. A future
electrical-model run would additionally reference its transform config and,
for G1, the explicit proxy mapping. No runtime wiring occurs in Phase 8V.

## Decisions and exactly one next phase

- Input semantics: `DEFINE_ABSTRACT_TTM_ELECTRICAL_INPUT_EVENT`.
- Timing: `SAME_BOUNDARY_ZERO_ADDED_MODEL_DELAY`.
- G1 proxy: `G1_PROXY_REQUIRES_EXPLICIT_MAPPING_CONTRACT`.
- Success semantics: `ONE_RECEIPT_ONE_INPUT_WITHOUT_RELEASE_CLAIM`.
- Model-family neutrality: `INPUT_CONTRACT_CAN_REMAIN_MODEL_FAMILY_NEUTRAL`.
- Next boundary: `PIN_ABSTRACT_TTM_ELECTRICAL_INPUT_CONTRACT`.

**Exactly one bounded Phase 8W:** pin and offline-replay the TTM-class abstract
electrical-input token contract downstream of validated canonical Phase 8Q
receipts. Require one-to-one parent identity, copied timing under the explicit
model-delay assumption, full ancestry, no magnitude/release/response fields,
no inferred G1 destination, and immutable upstream replay. Test zero,
unilateral, bilateral and repeated-record identity and rejection/tampering.
Do not implement a G1 proxy mapping, electrical model, model-specific input
transformation, observation comparison, fitting, DLM path or production adapter.
This recommendation does not authorize implementation in Phase 8V.

**Scientific boundary:** this assessment defines no electrical dynamics,
successful release, muscle response, calibration or comparison. Phase 8Q
remains a receipt; Phase 8S remains empirical evidence; Phase 8U remains
blocked comparability metadata. Canonical production remains silent and
untouched. No amplitude/conductance/probability/delay is guessed; no force,
mechanics, behavior or DLM work occurs.

## Verification and handoff

Full `python -m pytest`: 574 passed, one deselected, two dependency deprecation
warnings. `python -m ruff check .`, `python -m ruff format --check .`, and
`git diff --check` passed. Frontend regression-only `npm test` (38 tests),
lint, typecheck and build passed; the build-generated type-reference edit was
restored, leaving no frontend source change. No new behavioral test, Python
implementation, schema, artifact, fitting run or comparison was introduced.
Only this assessment and the minimal Project Context update are left for
review. No commit or push was performed.
