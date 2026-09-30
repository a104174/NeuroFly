# Phase 8X — TTM-class to G1 observation-domain proxy readiness

Assessment: `PASS`. An explicit **exploratory G1 observation-domain proxy**
is defensible for a bounded future single-fiber model. It is a deliberate
model-domain choice, not anatomical resolution of a MaleCNS target. No proxy
mapping, electrical model, observation operator or comparison is implemented.

## Repository and immutable source gates

Work began on clean `main` at
`ac606f638f8bb75b86bcb041e12b3ebfb0f6c17b`, equal to `origin/main`.
Phase 8W, 8V, 8U and 8S were committed; `git diff --check` passed. Offline
replays reproduced the following canonical sources without migration:

| Source | Identity | Accounting / readiness |
| --- | --- | --- |
| Phase 8W abstract-input artifact | `1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa` | Eight tokens; four per TTMn body. |
| Phase 8U mapping artifact | `f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f` | Nine mappings; **zero** formally ready. |
| Phase 8S observation artifact | `5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f` | Nine protocol-specific observations. |
| Phase 8K target contract | `5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0` | Twelve associations; two TTM-class associations relevant here. |

Phase 8W replay also recursively validates Phase 8Q/8O/8N ancestry. Audit
sources include the [8W contract](ttm_abstract_electrical_input_contract.md),
[8V assessment](ttm_neuromuscular_input_semantics.md),
[8U mappings](ttm_g1_observation_mapping_contract.md),
[8S observations](ttm_g1_electrophysiology_observation_contract.md),
[8K target contract](motor_neuron_muscle_target_contract.md),
[8P assessment](ttmn_ttm_neuromuscular_readiness.md),
[8R source audit](ttm_g1_electrophysiology_observation_readiness.md), and
Project Context. Their implementations, curated facts and hashes are unchanged.

## Present causal boundary

Phase 8Q records an exploratory neuromuscular-input handoff. Phase 8W admits
one such receipt as one `ABSTRACT_ELECTRICAL_INPUT_TOKEN`, with
`EXPLORATORY_ABSTRACT_ELECTRICAL_INPUT` provenance,
`ONE_RECEIPT_ONE_INPUT_WITHOUT_RELEASE_CLAIM` success semantics, and the
`ZERO_ADDED_MODEL_DELAY_ASSUMPTION`. The token carries ancestry, identity and
model timing, not physical magnitude, release, current, conductance or voltage.

Its destination is the pinned **TTM muscle class** association for TTMn
`800146/R` or `804642/L`. `HIGH` confidence refers to class/pathway
correspondence; target side is qualified ipsilateral class inference. Exact
fiber, peripheral contact and exact-body-to-fiber tracing remain unresolved.
These source semantics are not changed by approving a proxy.

## Primary anatomy: verification level and claim limits

The architecture-driving biological claims below were rechecked against
primary publisher content, not inferred from prior NeuroFly summaries.

| Claim | Primary source and location / granularity | Supports | Does not support | Architecture consequence |
| --- | --- | --- | --- | --- |
| GF contacts a large motor axon innervating ipsilateral TTM; GF itself is not the motor axon. | King DG, Wyman RJ (1980), *Anatomy of the giant fibre pathway in Drosophila. I. Three thoracic components of the pathway*, J Neurocytol 9:753–770, DOI `10.1007/BF01205017`; publisher Summary, pathway anatomy. | GF–motor–TTM pathway association. | G1 destination, exact MaleCNS crosswalk, electrical parameters. | Keep pathway identity separate from proxy selection. |
| TTM contains 23 fibers; G1–G19 share giant-motor-axon branches; F1–F4 receive two fine axons. | Koenig JH, Ikeda K (2007), *Release and Recycling of the Readily Releasable Vesicle Population in a Synapse Possessing No Reserve Population*, J Neurophysiol 97:4048–4057, DOI `10.1152/jn.01258.2006`; Results anatomy and Figures 1/2 captions. | G1 belongs to the giant-axon-innervated subgroup. | All 23 sharing that innervation or identical physiology. | Proxy scope is one G1-based fiber, never whole TTM. |
| G1 was used exclusively because its position was readily identifiable; representativeness is justified by similar innervation pattern. | Koenig–Ikeda 2007, Results anatomy. | Technical selection and innervation-pattern precedent. | Equal responses, membrane properties, release dynamics or geometry across G fibers. | Label reduced-domain choice as an assumption. |
| G1 geometry/distributed synapses motivate the recording/correction analysis. | Koenig–Ikeda 2007, Methods, Results and Discussion. | Fiber-specific observation context. | Geometry-free universal muscle model. | Any later geometric use requires explicit G1 scope and source-matched analysis. |

The [King–Wyman official publisher Summary](https://link.springer.com/article/10.1007/BF01205017)
was accessible; the full paper was subscription-restricted. It is used only
for its pathway-level statement. The [Koenig–Ikeda official primary text](https://journals.physiology.org/doi/full/10.1152/jn.01258.2006)
returned HTTP 403 on direct opening, but publisher-indexed Methods, Results,
Discussion and figure-caption passages were recoverable and directly checked,
as in the Phase 8R recovery. This is **indexed primary-text verification**, not
a claim of unrestricted full-article access. No secondary reconstruction,
figure digitization, source-paper storage or quantitative geometry import was
performed.

## Proxy is not anatomical destination

The proposed inference is explicitly architectural:

`TTM-class causal context → MODEL_ASSUMPTION → virtual G1 observation domain`.

It is **not** `MaleCNS TTMn body → traced G1 fiber`. The common innervation
evidence supports considering a G1-based reduced domain, but does not determine
that abstraction uniquely. The empirical advantage is the availability of
fiber-specific observations, not proof that G1 is the Phase 8W destination.

The permissible claim is: NeuroFly chooses an exploratory G1-based domain to
model one giant-motor-axon-innervated TTM fiber. It may not claim exact body
tracing, complete TTM representation, or bilateral physiological equivalence.
An eventual G1 proxy response is not whole-TTM electrical response, activation,
contraction, force or behavior. Observations remain observations, not parameters.

## Alternatives and scientific risk

| Alternative | Evidence support / empirical comparability | Overclaim risk | Assumptions | Flexibility / complexity | Readiness |
| --- | --- | --- | --- | --- | --- |
| A. Explicit virtual G1 proxy | Direct scope match to selected G1 observations, conditional on future operators and protocols. | Mistaking proxy for exact destination or representative whole muscle. | Deliberate reduced-domain selection; no physiological identity assumption. | Model-family neutral; one domain type and evidence references. | Preferred bounded domain choice. |
| B. Generic giant-axon-innervated G-fiber proxy | Innervation-class precedent; G1 data are one member's evidence. | Silently transferring G1 physiology to an unspecified fiber. | Extra member-to-generic transfer assumption for numeric use. | Broad but requires an additional G1 observation mapping. | Class context is honest; direct G1 comparison is not established. |
| C. Whole-TTM class state | Existing causal target class, but no aggregate observable from the pinned single-fiber data. | Highest: equating G1 with the whole muscle. | Aggregation, heterogeneity, additional innervation and geometry. | More complex and empirically unconstrained here. | Not supported by this observation set. |
| D. Hold / collect exact peripheral tracing | Avoids reduced-domain assumptions. | Low. | None now. | Delays electrical-domain work. | Required for exact-body destination claims, not for explicitly exploratory G1 scope. |

Option B does not improve direct numerical comparability: its generic domain
would need an explicit transfer to the G1 measurement domain anyway. Option A
makes that choice visible without assuming all G fibers are physiologically
interchangeable. No model family or first electrical dynamics is selected.
Additional peripheral anatomy is unnecessary for this narrow proxy goal;
body-resolved peripheral anatomy or mechanics would be a different goal.

## Laterality: domain type, not a shared physical instance

Recommend **`SIDE_AGNOSTIC_PROXY_DOMAIN_ONLY`** at the next metadata boundary.
Both pinned TTMn associations may reference the same evidence-defined
`G1_PROXY_DOMAIN_TYPE`, while retaining distinct body, neural side, target-side
qualification, token and receipt identities. This does not merge bilateral
tokens or map two bodies to one physical G1 fiber.

Koenig–Ikeda's anatomical dissection identifies a right-side preparation;
that procedural side is not a paired left/right physiology dataset or a
crosswalk to the MaleCNS bodies. Thus proxy observation laterality remains
`OBSERVATION_PROXY_SIDE_UNRESOLVED`. Source preparation metadata is preserved,
not erased or duplicated as two measurements.

A future model could create separate per-causal-context proxy instances, but
that is not approved or implemented as a physical-fiber mapping here. Right/left
instance labels would denote causal ancestry; shared evidence or parameters
would be an additional model assumption, not physiological mirroring. Type
sharing alone authorizes neither parameter sharing nor coupled state.

## Phase 8S use and Phase 8U blockers

Proxy selection makes the following records semantically addressable as
G1-domain evidence, not executable validation targets:

| Phase 8S record (canonical order) | Effect of explicit G1 proxy | Requirements still absent |
| --- | --- | --- |
| Resting-potential context | Same intended fiber scope. | Voltage, equilibration/baseline operator, protocol matching; descriptive value has no numerical comparison rule. |
| Reused evoked-potential input | Conditional future G1 validation evidence. | Electrical input transformation, voltage, verified source protocol and amplitude/window operator. |
| Miniature-potential observation | Relevant to a future miniature-response domain. | Release/quantal semantics and miniature detector; receipts are not miniature events. |
| Prior equilibrium analysis input | Analysis context only. | Prior-source applicability; no direct validation or automatic reversal parameter. |
| Derived quantal content | Relevant only to a matching release/correction model. | Quantal outputs or justified correction pipeline; tokens are not quanta. |
| Spontaneous frequency | Relevant only to a matching spontaneous model. | Stochastic process, interval/detection semantics and protocol matching; uncertainty stays as pinned. |
| Categorical repeated-response outcome | Relevant only to a response/history model. | Response amplitudes, history dynamics, depression definition and protocol matching. |
| Derived recycling rate | Relevant only to a vesicle/recycling model. | Vesicle and active-zone accounting, history and derivation semantics. |
| Kadas composite latency | No new G1 scope match: it is a different recording/subpath observation. | Full stimulation-to-muscle-onset boundary and onset detector; receipt timing cannot substitute. |

The proxy could eventually resolve a **declared domain-selection gap**, not an
existing physiology or comparison blocker. No new persisted Phase 8U blocker
code is invented and no existing code is erased. `MODEL_QUANTITY_ABSENT`,
`MISSING_OBSERVATION_OPERATOR`, `PROTOCOL_MATCH_UNRESOLVED`, release,
spontaneous, history, vesicle and system-boundary blockers remain. Phase 8W
already resolves abstract input admission only; `INPUT_SEMANTICS_UNDEFINED`
still applies to the missing physical/model-specific transformation. Formal
ready mappings remain **zero**. Age, genotype, temperature, preparation and
unknown protocol dimensions remain distinct; proxy selection is not a match.

## Separate future proxy contract: proposal only

Keep the Phase 8W token **TTM-class only**. Resolve the exploratory domain in
a separate downstream metadata contract, conceptually
`ttm_g1_proxy_mapping_v1`, with:

- Source Phase 8W contract identity and Phase 8K TTM association references.
- One G1 observation-domain **type**, biological scope and unresolved proxy
  observation side; distinct references for the two causal associations.
- `EXPLORATORY_OBSERVATION_DOMAIN_PROXY` mapping classification and explicit
  `MODEL_ASSUMPTION`, never anatomical mapping or peripheral tracing.
- Separate evidence roles/locations for pathway anatomy, G-group innervation
  and G1 characterization; Phase 8S/8U evidence/mapping references.
- Type-versus-instance semantics, permitted uses, prohibited interpretations,
  unresolved physical transformation, protocol and operator requirements.

No numerical suitability probability is necessary. Phase 8K's existing class
mapping confidence must not become confidence in a body-to-G1 connection.
No G1 geometric parameter, voltage, current, conductance, delay, release
probability or observation-derived model coefficient belongs in this contract.
It can remain neutral across future phenomenological, passive-membrane or
conductance families. Their input transformations and configurations remain
separate, and no such model is implemented now.

## Decisions

- Proxy readiness: `G1_EXPLORATORY_PROXY_READY`.
- Proxy instance: `SIDE_AGNOSTIC_PROXY_DOMAIN_ONLY`.
- Upstream token: `KEEP_PHASE8W_TOKEN_TTM_CLASS_ONLY`.
- Observation use: `G1_PROXY_CAN_REFERENCE_PHASE8S_OBSERVATIONS_AS_FUTURE_VALIDATION_EVIDENCE`.
- Next boundary: `PIN_TTM_TO_G1_PROXY_MAPPING_CONTRACT`.

## Exactly one bounded Phase 8Y

Pin and offline-replay a **metadata-only TTM-class to G1 observation-domain
proxy mapping contract**. Reference the unchanged Phase 8W/8K identities,
preserve both causal associations, define one side-unresolved domain type,
reference Phase 8S/8U evidence, and test assumption/prohibited-claim boundaries
and deterministic identity. Do not create runtime model instances, convert
tokens to physical inputs, add electrical dynamics, select a model family,
copy observations into parameters or change zero-ready comparison status.
Phase 8Y is defined here, not implemented.

## Verification and review scope

Full Python regression: **630 passed, 1 deselected, 2 dependency deprecation
warnings**. `python -m ruff check .`, `python -m ruff format --check .` and
`git diff --check` passed. Frontend regression: **38 tests passed**; lint,
typecheck and production build passed. The build's automatic declaration-file
rewrite was restored, leaving no frontend changes. Only this assessment and
the minimal Project Context entry are changed. No new artifact, schema,
production code, commit or push is introduced.
