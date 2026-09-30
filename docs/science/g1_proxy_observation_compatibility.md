# Phase 9D — post-model G1-proxy observation compatibility

## Decision and scope

Voltage-like quantities now exist, but **no formal numerical validation subset
is ready**. The smallest useful executable next step is a model-space peak
evoked-deflection extractor with an explicit baseline/window helper. It must
remain separate from physical-unit calibration and biological comparison.

This assessment implements no operator, protocol runner, unit transformation,
fit, empirical comparison or model dynamics. No model output is subtracted
from, scored against or otherwise numerically compared with a Phase 8S value.
The following candidate operators are proposals, not executions or claims of
recovered source measurement semantics.

## Repository findings and audit

Initial worktree was clean at committed Phase 9C HEAD
`e4365e131f17cedb4f2235ecc86159b9f12a036b`, matching `origin/main`.
The required phases were committed and these artifacts replayed unchanged:

| Source | Artifact/contract ID |
|---|---|
| Phase 9C | `dfe98ec90078124f4a66df825b552d05ed317fcb89d33e0f374b99c6bfd4bfa4` |
| Phase 9B | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` |
| Phase 8U | `f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f` |
| Phase 8S | `5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f` |
| Phase 8Y | `030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8` |

The audit inspected the Phase 9B state/config, persisted trajectory semantics,
Phase 9C sensitivity analysis, all nine loaded Phase 8S records and Phase 8U
mappings, Phase 8Y proxy definition, Phase 9A decision, and the earlier
electrophysiology/protocol assessments. This phase uses pinned evidence, not
new biological research or stronger source-access claims. Source locations,
uncertainty and verification limits remain solely under Phase 8S authority.
Phase 8U remains an immutable historical readiness snapshot with zero formally
ready mappings; this document describes subsequent compatibility separately.

Evidence/protocol authority is the
[Phase 8S contract](ttm_g1_electrophysiology_observation_contract.md); historical
comparability is the [Phase 8U contract](ttm_g1_observation_mapping_contract.md).
Domain assumptions remain in the
[Phase 8Y contract](ttm_g1_proxy_mapping_contract.md), and model-space output
meaning remains in the [Phase 9B model](g1_proxy_passive_electrical_response.md).

## What exists, and what does not

The executable passive model reports independent fixture/body arrays:
`proxy_voltage_mV_eq`, `voltage_deviation_mV_eq`, boundary/time and token-count
columns, source-token ancestry and model peak/final summaries. Phase 9C
demonstrates model sensitivity and internal scale/tau separability. These
provide mathematical model quantities, not empirical observations.

`mV_eq` is **NUMERICALLY_DIMENSIONED_UNCALIBRATED_MODEL_SPACE_COORDINATE**.
It is a voltage-shaped proxy coordinate, not a physically established membrane
voltage unit. No biological scale or offset has been established, and the
passive form does not supply that mapping automatically. In particular:

- One model mV-equivalent is not asserted to equal one biological mV.
- Reference 0 is a neutral coordinate origin, not the reported resting value.
- Effective scale 2 per abstract token is not a measured 2 mV response.
- No comparison of model baseline 0 with approximately −95 mV is performed.
- No comparison of model peak 2 with the reused 45 mV response is performed.

Readiness has six separate gates: quantity availability, unit/measurement
semantics, executable operator, protocol match, valid numerical comparison and
justified calibration. Passing the first does not pass any of the others.

## Observation-by-observation compatibility

All protocol statuses below are **NOT_MATCHED / UNRESOLVED**, never implicitly
matched. `MODEL_QUANTITY_NOW_AVAILABLE_BUT_NOT_COMPARABLE` denotes only an
appropriate model-space scaffold, not biological quantity identity.
`PHYSICAL_UNIT_MAPPING_UNDEFINED` and `PHYSICAL_RESPONSE_SEMANTICS_UNCALIBRATED`
are newly explicit documentation labels, not changes to Phase 8U taxonomy.

| Phase 8S observation ID / empirical quantity | Required model quantity exists? / current quantity | Unit and semantic compatibility | Candidate operator only | Protocol requirement/status | Remaining blockers | Current classification |
|---|---|---|---|---|---|---|
| `ttm-g1-obs-21076e7816c87359e80f` — approximate G1 resting potential, descriptive measured value | Yes, model-space baseline in `proxy_voltage_mV_eq`; no measured membrane baseline | Uncalibrated coordinate origin, not biological mV | Equilibrated or prestimulus baseline sample/summary | G1 intracellular scope, four-day-old female preparation; record-level genotype/temperature unresolved; no fixture match | Unit/offset mapping, operator and equilibration, source incompleteness, descriptive-source numerical-rule limitation, protocol match | `MODEL_QUANTITY_NOW_AVAILABLE_BUT_NOT_COMPARABLE` |
| `ttm-g1-obs-0e8110027289e2606870` — 45 mV evoked junction potential, prior primary result reused | Yes, event-aligned `voltage_deviation_mV_eq` and proxy trace | Model deviation is not measured EJP deflection or biological mV | Peak deflection relative to declared prestimulus baseline, with explicit poststimulus window | Original 2005 protocol and threshold-level response, including reported medium context; many dimensions unverified; no fixture match | Unit mapping, input-response calibration, operator/window, original amplitude operation, source protocol, protocol match | `MODEL_QUANTITY_NOW_AVAILABLE_BUT_NOT_COMPARABLE` |
| `ttm-g1-obs-00171dce33f34d595a05` — approximate miniature potential, descriptive measured value | No; generic evoked proxy traces are not miniature/quantal electrical events | Missing event semantics, as well as physical units | Miniature-event selection and amplitude summary | G1 intracellular, four-day-old female `shi`, 19 °C; no miniature process or protocol match | Required quantity, release/quantal semantics, miniature detector, operator, unit/measurement mapping, protocol match | `ADDITIONAL_PHYSIOLOGY_MODEL_REQUIRED` |
| `ttm-g1-obs-87c7df503a4c6d752ea0` — −10 mV equilibrium input from prior source | No direct model quantity intended; passive model has no reversal state | Prior analysis input, not a voltage validation target | `CONTEXT_ONLY`; no comparison path | Source-specific Martin correction context; original applicability incomplete | No direct comparison intended; prior-source verification/applicability | `CONTEXT_ONLY` |
| `ttm-g1-obs-cade4bdd5192612a0423` — approximate 191 quanta, derived quantity | No release/quantal output or source-matched correction inputs | Token count and proxy voltage do not represent quanta | Source-compatible derived quantal-content operation, only if prerequisites exist | G1 single-stimulus/no-prior-activity correction context; genotype/temperature unresolved; no match | Required quantity, release/quantal semantics, matched correction pipeline, operator, protocol match | `ADDITIONAL_PHYSIOLOGY_MODEL_REQUIRED` |
| `ttm-g1-obs-399d70f32a656dea7a85` — 7 ± 3 spontaneous events/s, summary statistic | No spontaneous miniature-event process | Lack of process is not a prediction of biological zero frequency | Event detector/rate over a declared interval | Four-day-old female WT Oregon-R G1 at 19 °C; observation interval unresolved; no match | Required quantity, spontaneous process, event detector/interval, operator, protocol match | `ADDITIONAL_PHYSIOLOGY_MODEL_REQUIRED` |
| `ttm-g1-obs-745604f564d9f4c315d4` — categorical no observed depression under the specified 1-Hz protocol | Yes, model-space repeated response series; no physiological depression/release mechanism | Linear summation/equal input increments are not a biological depression outcome | Per-stimulus response series plus source-matched operational depression definition | Four-day-old female `shi`, G1 intracellular, 19 °C, recycling permitted, 1 Hz / 1,500 stimuli; canonical fixtures do not match | Physical response semantics, depression/release/history capability, definition, operator, protocol match | `ADDITIONAL_PHYSIOLOGY_MODEL_REQUIRED` |
| `ttm-g1-obs-61e331f15399e1627634` — 0.24 vesicle/AZ/s, derived rate | No vesicle, active-zone or recycling outputs | Neither passive decay nor effective tau is vesicle recovery | Matched derived recycling-rate analysis | Specified `shi` G1 train/recycling comparison and active-zone denominator; no match | Required quantity, vesicle/recycling and history semantics, denominator/correction, operator, protocol match | `ADDITIONAL_PHYSIOLOGY_MODEL_REQUIRED` |
| `ttm-g1-obs-24852cd49c1395db8e8c` — Kadas composite stimulation-to-TTM onset, summary statistic | No full required subpath; only post-token proxy trace/timing exists | Token reference omits preceding axonal conduction; model onset is not extracellular TTM onset | Initial-potential-onset latency with matched start and endpoint | 24hPE control, both sexes, thoracic-region stimulation to extracellular initial TTM potential; G1 not identified/test temperature unresolved; no match | Full-path quantity, system boundary, onset detector, physical/recording semantics, source protocol, protocol match | `SYSTEM_BOUNDARY_MISMATCH` |

## Phase 8U blocker diff, without editing Phase 8U

Historical exact blocker codes remain in the canonical Phase 8U artifact. The
post-model assessment is narrower than simply toggling its readiness flags:

| Observation | Resolved or narrowed since Phase 8U | Still active | Newly exposed or refined |
|---|---|---|---|
| Resting | Model-space baseline quantity available; G1 proxy domain selected | `MISSING_OBSERVATION_OPERATOR`, `PROTOCOL_MATCH_UNRESOLVED`, `SOURCE_PROTOCOL_INCOMPLETE`, `DESCRIPTIVE_SOURCE_NO_NUMERICAL_COMPARISON_RULE` | Physical unit/offset mapping; equilibrated biological versus initialized model baseline |
| Evoked | Model-space response trace available; abstract admission and effective model drive defined | Operator, protocol/source incompleteness, `SOURCE_AMPLITUDE_OPERATION_UNRESOLVED` | `PHYSICAL_UNIT_MAPPING_UNDEFINED`; historically undefined input semantics now defined only in model space, not calibrated physical response semantics |
| Miniature | Proxy domain selected only; required miniature quantity still absent | `MODEL_QUANTITY_ABSENT`, release semantics, miniature detector, operator, protocol | A voltage-shaped response does not supply a single-quantum interpretation or physical mapping |
| Equilibrium input | None needed for direct comparison | `NO_DIRECT_COMPARISON_INTENDED`, source applicability incompleteness | No reversal mechanism selected; do not manufacture a validation mapping |
| Quantal content | Proxy domain selected only | Required quantity, release semantics, source correction pipeline, operator, protocol | Available proxy voltage is not sufficient for the source's correction inputs |
| Spontaneous rate | Proxy domain selected only | Required quantity, spontaneous process, miniature detector, observation interval, operator, protocol | No-process limitation must not become a predicted biological zero |
| Depression | Model-space repeated response series exists; effective event input is defined | Operator, depression definition, protocol match, `HISTORY_DYNAMICS_ABSENT` in its depression/release sense | Passive retained state is history but is not release/depression history; physical response transfer remains uncalibrated |
| Recycling | No required quantity resolved | Required quantity, vesicle/history model, operator, protocol match | Effective electrical tau cannot replace vesicle recovery or recycling output |
| Kadas latency | Post-token response trace exists only; required full-path quantity remains absent | `SYSTEM_BOUNDARY_TOO_NARROW`, onset detector, operator, source protocol, protocol match | Model clock origin and voltage-equivalent jump do not reproduce stimulation reference, extracellular onset or age-dependent conduction |

For rows 1, 2 and 7, `MODEL_QUANTITY_ABSENT` is resolved **only at the
model-space scaffold level**. It is not evidence of physical measurement
equivalence. For rows 3, 5, 6, 8 and 9 it remains active for the required
quantity; row 4 has no direct quantity requirement. None is formal-ready.
The generic G1 domain mismatch is reduced by Phase 8Y, but exact anatomy,
empirical laterality and protocol-specific physiology are still not asserted.

## Resting and evoked compatibility

A baseline operator can summarize a declared equilibrated/prestimulus part of
the proxy trace. The initialization is already a chosen reference coordinate;
it does not establish biological equilibration. For the current zero-start
fixtures, a baseline-only operator would mostly return that arbitrary origin.
It is useful as a helper and provenance/consistency check, not the first
independent biological validation target. The approximate resting observation
has no pinned distribution, sample size or numerical acceptance rule.

The evoked trace is a stronger operator-development candidate: extract a
peak deflection relative to an explicitly defined baseline, using declared
windows and isolated-event context. It can be implemented mathematically in
model units before physical calibration. Neither source peak-versus-baseline
operation nor original source observation window is fully resolved; a model
operator's definition must be labelled **model-space extraction semantics**,
not purported experimental measurement reconstruction.

Phase 9B already stores a whole-fixture maximum of deviation. A future bounded
extractor must add more than a renamed summary: independently validate a
persisted trace, explicit baseline and post-input windows, grid alignment,
source/event/instance linkage, output units and operator provenance. It must
exclude or flag multiple inputs/residual-state situations rather than silently
turning a repeated-fixture maximum into a single EJP amplitude.

## Miniature, quantal, spontaneous, depression and recycling limits

An abstract token is neither one miniature event nor one quantum. No release,
miniature detector or source correction pipeline exists. The approximate 0.5 mV
and derived 191-quanta records therefore remain inaccessible to this model.
The −10 mV prior-source correction input remains context only; it is not made
an `E_rev`, validation target or operator input.

No spontaneous process means this model cannot produce the required biological
event-rate observable—not that it predicts zero spontaneous events/s. The
published uncertainty kind for 7 ± 3 remains `UNKNOWN_NOT_ESTABLISHED`, not SEM
or SD. It is not an empirical acceptance interval.

Two repeated tokens at 1 and 3 ms are not 1-Hz stimulation of 1,500 responses.
The model has passive state retention but no release efficacy/depression state.
Fixed increment plus residual voltage is not a source-defined depression
statistic or validation of no depression. No vesicle/AZ output exists, and
the derived recycling rate cannot identify the effective electrical tau.

## Kadas composite latency

The model clock begins at abstract-input admission downstream of motor output;
Kadas starts at thoracic motor-neuron-region stimulation and ends at an initial
extracellular TTM potential. The preceding axonal conduction and the measured
recording endpoint are not implemented. A model voltage-equivalent boundary
jump with `ZERO_ADDED_MODEL_DELAY_ASSUMPTION` is not a prediction of that
latency, an NMJ delay or a biologically detectable onset.

Even a future post-token onset extractor would measure a different interval.
No onset detector/threshold, age-specific conduction, extracellular observation
transform or protocol match is available. The 24hPE record stays distinct from
four-day-old G1 preparations; rearing temperature is not test temperature.

## Physical-unit mapping and parameter identifiability

An illustrative future affine map could be `V_bio = b + s*V_model`; it is not
defined or fitted here. It would require justified biological/recording meaning
for the proxy, offset/scale, matched protocol and source-compatible extraction.
Writing this formula does not demonstrate that a global affine map is adequate
for biological membrane response, electrode geometry or nonlinear potentials.

At fixed model form, deflection depends on the product `s*event_scale`; freeing
both creates a scale degeneracy. Baseline depends on `b+s*reference`, so freely
varying reference and offset also creates nonidentifiability. Unit mapping and
model parameter estimation must not be disguised as independent evidence.
With present reference fixed at zero, a future offset still needs evidence;
it is not supplied by naming the output voltage-equivalent.

The resting and evoked records are not a legitimate two-point calibration set:
one is approximate preparation context and the other a reused prior result with
incomplete original protocol. They must not be combined into a fictional common
experiment. Changing labels to physical mV or redesigning the state variable
would not resolve that evidence/protocol gap by itself.

| Parameter | Current empirical status | Possible later constraint, conditional only |
|---|---|---|
| Effective event scale | Not identifiable | Matched evoked-amplitude semantics could constrain an effective response magnitude or scale product after operator/unit/protocol work; not necessarily the token transformation itself |
| Effective tau | Not identifiable | Requires a relevant source-verified response time course and matched temporal operator; the pinned nine records do not supply an evoked decay trace |
| Reference/physical offset | Not identifiable | A properly matched resting measurement could constrain baseline/offset, not scale or tau by itself; descriptive context is not current calibration data |

The reused 45 mV amplitude alone does not identify tau. The approximate resting
value alone does not identify event scale or tau. Phase 9C's structural
separability establishes only properties of the known model and its own
trajectories, not empirical parameter values. No best sensitivity cell, fitted
offset, biological conversion factor or parameter revision is selected.

The model should retain the name **electrical-response proxy**, not measured
or calibrated membrane-voltage model. It may remain useful in that role even
if no literal biological-mV calibration is ever established.

## Protocol matching and benchmark architecture

Current fixtures derive from synthetic DNp01/motor-interface ancestry. Source
body/side, target class, virtual domain, token timing and numerical config are
known. Experimental age, sex, genotype, bath, test temperature, electrode and
stimulation protocol are not represented as matched preparation conditions.
Unknown source fields and absent model fields are never wildcard matches.

| Protocol dimension | Pinned evidence requirement | Present model/fixture status |
|---|---|---|
| Biological domain/recording fiber | Intracellular G1 for G1 records; Kadas fiber not identified as G1 | Explicit virtual G1 domain type only; no exact anatomy or electrode model |
| Age/sex | Record-specific four-day-old female G1 context; Kadas 24hPE/both sexes; reused 2005 record incomplete | Not matched; do not merge preparations |
| Genotype | WT Oregon-R spontaneous protocol versus `shi` miniature/train protocols; other record-level unknowns | No genotype-dependent dynamics or matched experimental condition |
| Temperature/recycling | 19 °C and specified permitted/blocked comparison where pinned; other temperatures unresolved | No temperature/recycling model or matching declaration |
| Stimulation site/pulse | Record-specific neck electrode versus thoracic motor-neuron region | Abstract token admission, not an experimental electrode stimulus; numerical dt is not a pulse width |
| Frequency/count/history | Single-stimulus context or 1-Hz/1,500-stimulus train where pinned | Six 8-ms model-behavior fixtures; repeated tokens separated by 2 ms, not the train protocol |
| Recording mode and measurement definition | Intracellular potential versus extracellular initial TTM potential; source-specific amplitude/correction | Voltage-equivalent arrays, no observation/recording transform or source-matched operator |

Canonical fixtures are currently suitable for **model-behavior tests only**,
not empirical validation. Eventually distinguish two execution purposes:

- Connectome-driven causal mode preserves neural/input ancestry and explores
  downstream response, without claiming experimental stimulation equivalence.
- A separate isolated empirical benchmark mode supplies a source-defined
  stimulus schedule at an explicitly declared model boundary. It must preserve
  experimental protocol identity and all assumptions translating that stimulus
  to effective model drive; it must not pretend the connectome generated it.

A benchmark schedule by itself does not remove unknown unit, source or input
efficacy semantics and does not add omitted axonal conduction. Implementing a
published long train while retaining no release/history capability would not
create depression validation. This architecture is recommended for future
empirical work, but is not the immediate implementation phase: current peak
source semantics/protocol and physical mapping are not ready to define a valid
comparison benchmark. No benchmark runner is implemented here.

## Next-step options and smallest useful slice

| Option | Assessment |
|---|---|
| Model-space peak extraction with baseline/window helper | Selected: executable measurement boundary for existing persisted trajectories, without physical calibration or experimental comparison |
| Empirical benchmark runner | Scientifically cleaner separation for future protocol-aligned testing, but currently missing source/transfer/unit semantics; premature as a biological benchmark |
| Recover time-course/original protocol evidence | Needed before tau identification or biological amplitude comparison, not required for explicitly model-space extraction |
| Revise physical-unit/model semantics | Renaming units is not evidence; no model equation revision needed for the selected proxy capability |
| Muscle activation next | Not selected; skips the unresolved electrical measurement and interpretation boundary |

An **operator-development subset only** exists: isolated evoked model-space
response, with baseline support. No formal numerical validation subset is ready.
The first family is peak evoked deflection, not baseline-only calibration.

Exactly one Phase 9E: implement a deterministic, offline-replayable **model-space
peak-deflection extractor with a baseline/window helper** over validated Phase
9B persisted trajectories. Require explicit model-space baseline/post-input
windows and event/instance identity; start with isolated single-event contexts
and zero controls; distinguish bilateral instances without merging. Reject
nonfinite/invalid windows and unsupported overlapping/multiple-input contexts.
Preserve source/model/operator/config provenance, `mV_eq` units and
`NO_EMPIRICAL_COMPARISON`. Test deterministic extraction, translation behavior,
event alignment, source integrity and replay. The future window policy is a
declared model-analysis assumption, not a recovered experimental window.

No scale/offset conversion, fitting, 45 mV comparison, empirical benchmark,
source contract mutation, onset/depression/quantal operator or activation is
authorized by this recommendation. Reuse numerical primitives only where their
semantics fit; no chain of new metadata-only contracts is proposed. No part of
Phase 9E is implemented in Phase 9D.

## Decision snapshot

- Model quantity compatibility: `VOLTAGE_LIKE_MODEL_QUANTITIES_NOW_AVAILABLE`.
- Formal validation readiness: `OBSERVATION_OPERATOR_DEVELOPMENT_READY_ONLY`.
- First observation target: `PEAK_EVOKED_DEFLECTION_FIRST` (model-space only).
- Empirical parameter readiness: `EMPIRICAL_PARAMETER_IDENTIFICATION_STILL_NOT_READY`.
- Benchmark architecture: `SEPARATE_EMPIRICAL_BENCHMARK_RUNNER_RECOMMENDED` (future, not the next phase).
- Next phase: `IMPLEMENT_FIRST_MODEL_SPACE_OBSERVATION_OPERATORS`.

No current model is physiologically validated against G1 evidence. There is no
biological release, miniature process, calibrated membrane voltage, whole-TTM
activation, force, mechanics, behavior, LLM control or numerical empirical
comparison. Phase 8S/8U/8Y and Phase 9B/9C identities are unchanged.

## Verification and Phase 9D status

Phase 9D: **PASS** for this read-only compatibility assessment, not empirical
model validation. No new behavioral tests are needed or added.

- Required Phase 9C/9B/8U/8S/8Y offline replays passed unchanged.
- `python -m pytest`: 747 passed, 1 deselected, 2 existing deprecation warnings
  in 529.89 seconds.
- `python -m ruff check .`, `python -m ruff format --check .` and
  `git diff --check`: passed.
- Frontend: 38 tests passed; lint, typecheck and build passed. The build-generated
  import rewrite was restored; frontend source is unchanged.
- Only this document and the minimal Project Context update are changed. No
  production code, new artifact/schema/operator, model revision, numerical
  empirical comparison, calibration or protocol runner was implemented.

No commit or push was performed.
