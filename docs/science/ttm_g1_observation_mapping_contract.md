# Phase 8U — TTM G1 observation-mapping contract

Phase 8U pins `ttm_g1_observation_mapping_v1`: metadata describing the future
model quantity, candidate measurement semantics, protocol requirements, role,
and blockers for each of the nine Phase 8S observations. This records the
[Phase 8T assessment](ttm_g1_observation_model_feasibility.md) without executing
an observation operator or comparison. It does not select an electrical model.

## Repository and source gate

The work began on clean `main` at
`c4464feb4d90a24e90b2fc9b7cad5fc0b6a4e8e4`, equal to `origin/main`.
Phase 8T, 8S, and 8Q were committed. Offline replays passed for the Phase 8S
contract (nine observations), Phase 8Q artifact (eight receipts), and Phase 8K
target contract (12 associations). Phase 8Q recursively verifies Phase 8O/8N
ancestry. None of those historical artifacts or implementations is modified.

The empirical authority remains
`ttm_g1_electrophysiology_observation_contract_v1`, ID
`5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f`.
Its config hash is
`4c389614939cdf77c1aa545d25734eb810e829dae43c0c72aa1a18cbc378a48e`;
its result hash is
`fb45ac6689c411774dc2e1c2ea6d2ac6f4fa324388b24ecb010df795560fa58b`.
The source's values, classifications, uncertainty, protocols and exclusions
remain solely in [Phase 8S](ttm_g1_electrophysiology_observation_contract.md).
Generation replays the persisted source and rejects any different identity,
population, order, or observation semantics. There is no literature lookup.

## Nine mappings in source order

All records have `operator_executable = false`,
`current_model_produces_quantity = false`, and
`formal_comparison_ready = false`. Candidate operators are labels only.
The terms below are the exact serialized vocabularies.

| Phase 8S observation ID | Required future model quantity | Candidate operator; status | Comparability; future role | Distinct blockers |
| --- | --- | --- | --- | --- |
| `ttm-g1-obs-21076e7816c87359e80f` | `G1_MEMBRANE_VOLTAGE_TRACE` | `PRE_STIMULUS_BASELINE`; `CANDIDATE_ONLY` | `MODEL_OBSERVABLE_WITH_OPERATOR`; `QUALITATIVE_SANITY_CONTEXT` | `SOURCE_PROTOCOL_INCOMPLETE`, `DESCRIPTIVE_SOURCE_NO_NUMERICAL_COMPARISON_RULE`; equilibration and baseline sampling unresolved. |
| `ttm-g1-obs-0e8110027289e2606870` | `G1_MEMBRANE_VOLTAGE_TRACE` | `PEAK_EVOKED_DEFLECTION`; `SOURCE_SEMANTICS_INCOMPLETE` | `UNRESOLVED`; `FUTURE_VALIDATION_CANDIDATE` | `SOURCE_PROTOCOL_INCOMPLETE`, `SOURCE_AMPLITUDE_OPERATION_UNRESOLVED`, `INPUT_SEMANTICS_UNDEFINED`; original 2005 protocol and amplitude/window unresolved. |
| `ttm-g1-obs-00171dce33f34d595a05` | `G1_SINGLE_QUANTAL_ELECTRICAL_EVENTS` | `MINIATURE_EVENT_AMPLITUDE`; `REQUIRES_ADDITIONAL_PHYSIOLOGY` | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL` | `RELEASE_SEMANTICS_ABSENT`, `MINIATURE_DETECTOR_UNRESOLVED`; receipts cannot substitute for miniature events. |
| `ttm-g1-obs-87c7df503a4c6d752ea0` | `NO_DIRECT_MODEL_QUANTITY` | `CONTEXT_ONLY`; `CONTEXT_ONLY` | `CONTEXT_ONLY`; `ANALYSIS_CONTEXT_ONLY` | `NO_DIRECT_COMPARISON_INTENDED`, `SOURCE_PROTOCOL_INCOMPLETE`; prior-source applicability unresolved. |
| `ttm-g1-obs-cade4bdd5192612a0423` | `RELEASE_QUANTAL_OUTPUT_OR_MATCHED_CORRECTION_INPUTS` | `DERIVED_QUANTAL_CONTENT`; `REQUIRES_ADDITIONAL_PHYSIOLOGY` | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL` | `RELEASE_SEMANTICS_ABSENT`, `SOURCE_CORRECTION_PIPELINE_ABSENT`; require genuine model quantal outputs or justified source-matched correction. |
| `ttm-g1-obs-399d70f32a656dea7a85` | `G1_SPONTANEOUS_MINIATURE_EVENTS` | `SPONTANEOUS_EVENT_RATE`; `REQUIRES_ADDITIONAL_PHYSIOLOGY` | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL` | `SPONTANEOUS_PROCESS_ABSENT`, `MINIATURE_DETECTOR_UNRESOLVED`, `OBSERVATION_INTERVAL_UNRESOLVED`. |
| `ttm-g1-obs-745604f564d9f4c315d4` | `STIMULUS_ALIGNED_RESPONSE_SERIES` | `REPEATED_RESPONSE_OUTCOME`; `REQUIRES_ADDITIONAL_PHYSIOLOGY` | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL` | `HISTORY_DYNAMICS_ABSENT`, `DEPRESSION_DEFINITION_UNRESOLVED`, `INPUT_SEMANTICS_UNDEFINED`; response-amplitude/history semantics absent. |
| `ttm-g1-obs-61e331f15399e1627634` | `VESICLE_RECYCLING_OUTPUT` | `DERIVED_RECYCLING_RATE`; `REQUIRES_ADDITIONAL_PHYSIOLOGY` | `REQUIRES_ADDITIONAL_PHYSIOLOGY_MODEL`; `NOT_COMPARABLE_WITH_FIRST_ELECTRICAL_MODEL` | `VESICLE_MODEL_ABSENT`, `HISTORY_DYNAMICS_ABSENT`; active-zone denominator and recycling accounting unresolved. |
| `ttm-g1-obs-24852cd49c1395db8e8c` | `FULL_TTMN_STIMULUS_TO_TTM_RESPONSE_PATH` | `INITIAL_TTM_POTENTIAL_ONSET`; `SYSTEM_BOUNDARY_MISMATCH` | `SYSTEM_BOUNDARY_MISMATCH`; `SYSTEM_LEVEL_VALIDATION_CANDIDATE` | `SYSTEM_BOUNDARY_TOO_NARROW`, `ONSET_DETECTOR_UNRESOLVED`, `SOURCE_PROTOCOL_INCOMPLETE`, `INPUT_SEMANTICS_UNDEFINED`. |

Every non-context mapping also carries `MODEL_QUANTITY_ABSENT`,
`MISSING_OBSERVATION_OPERATOR`, and `PROTOCOL_MATCH_UNRESOLVED`. These blocker
codes have definitions in the contract's bounded taxonomy and are supplemented
by human-readable unresolved requirements.

## Protocol requirements and unknowns

Each mapping references its source observation's `biological_scope`, source
locations, and exact `protocol.dimension_status` paths. It declares required
dimension names, not an independent copy of empirical values. G1 mappings
require species, age, sex, genotype, test temperature, preparation, recording
fiber/site and mode where relevant. Evoked mappings additionally require
stimulation site/pulse and stimulus history. Repeated-response/recycling
mappings additionally require frequency, count, and recycling condition.
The prior equilibrium-input mapping references correction method and recording
fiber as context only. Kadas requires age, genotype/control context,
stimulation and recording endpoints/method, and the complete time reference
and onset semantics.

`unknown_source_policy` is
`REQUIRES_SOURCE_CLARIFICATION_NEVER_WILDCARD`; `missing_model_policy` is
`UNRESOLVED_NEVER_COMPATIBLE_BY_DEFAULT`. Every protocol match is
`NOT_EVALUATED`. Validation checks metadata structure and exact definitions;
it does not match a simulation protocol. Source unknowns remain under Phase
8S authority, including the spontaneous-frequency uncertainty type. Inspect
joins source labels and protocol facts from replayed Phase 8S for readability;
the mapping artifact contains no observation values, units, uncertainty, or
copied protocol values.

## Readiness and causal boundaries

The contract preserves `NO_VALIDATION_SUBSET_READY`,
`MODEL_FAMILY_PREMATURE`, `UNDERDETERMINED_MODEL_ASSUMPTIONS_REQUIRED`, and
`INPUT_SEMANTICS_REQUIRE_SEPARATE_CONTRACT`. Ready mappings: **zero**.
`MODEL_OBSERVABLE_WITH_OPERATOR` describes conditional future observability,
not current numerical comparison readiness.

Phase 8Q receipts expose no electrical input, voltage, quanta, spontaneous
activity, response history, or vesicle output. The Kadas experiment starts at
motor-neuron-region stimulation and includes preceding axonal conduction;
receipt-to-response timing cannot replace its composite interval. The prior
equilibrium analysis input has no direct validation operator. Event counts
cannot substitute for quanta; the categorical depression outcome supplies no
numeric dynamics coefficient; recycling evidence supplies no recovery tau.

Persisted boundaries include `METADATA_ONLY`,
`NO_EXECUTABLE_OBSERVATION_OPERATORS`,
`NO_FORMAL_NUMERICAL_COMPARISON_READY`, `NO_MODEL_FAMILY_SELECTED`,
`NO_MODEL_CALIBRATION`, `NO_ELECTRICAL_DYNAMICS`, and
`INPUT_SEMANTICS_UNRESOLVED`. No runtime dependency on Phase 8Q is introduced.
There is no observation execution, comparison, fitting, acceptance window,
model parameter export, electrical model, or DLM work.

## Identity, artifact and replay

The schema is `ttm_g1_observation_mapping_v1`; each
`ttm_g1_observation_mapping_record_v1` has a semantic hash-based `mapping_id`.
Config identity covers source hashes, taxonomy, vocabularies, readiness,
boundaries and exclusions. Result identity covers the nine ordered mappings.
The artifact/contract identity covers both hashes and schema identities.

The canonical `ttm_g1_observation_mapping_artifact_v1` is
`f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f`;
config hash
`5b7752ee0577a2f072fecc3b2713df116f7758a308825cd18ab1041d6c862f0e`;
result hash
`661cca4291351fc003fcc2ce0b1ec629047cc5e7ad9442a801e3cf9085eea1d0`.
The two-file artifact is 26,552 bytes, stored under ignored
`data/derived/malecns/looming_giant_fiber_v1/`.

```sh
python -m neurofly.ttm_g1_observation_mapping_cli generate
python -m neurofly.ttm_g1_observation_mapping_cli inspect <artifact>
python -m neurofly.ttm_g1_observation_mapping_cli replay <artifact>
```

All commands accept `--source-observation-artifact` with the pinned Phase 8S
artifact as the default. Replay validates/replays Phase 8S, verifies the exact
nine source IDs/order, rebuilds mappings, and requires semantic and byte/hash
equality. No network, paper files, randomness, or timestamps enter identity.
Artifacts reject unexpected files and canonical-definition drift even when a
caller recomputes hashes after a mutation. Export refuses existing targets.

Focused tests protect exact coverage/order/identities, protocol references,
unknown handling, status/blocker/role semantics, context-only and Kadas
boundaries, readiness snapshots, no empirical value duplication, deterministic
bytes, source mutation rejection, CLI inspection, and rehashed tampering.

## Next bounded phase

Exactly one Phase 8V is recommended: a read-only assessment of the semantics
needed between a Phase 8Q receipt and a future G1 electrical input. Compare
fixed electrical-response, current/conductance-event, and release-aware
assumptions against the pinned observation/mapping limitations, then recommend
one bounded input-contract direction. Implement no electrical dynamics or
comparison in that assessment.
