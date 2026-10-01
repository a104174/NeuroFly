# Phase 20 — observation operators and assay compatibility

## Outcome and scope

`OBSERVATION_OPERATOR_SPECIFIED_CALIBRATION_NOT_READY`.

An observation operator predicts an **assay-space observable** from a model
state, including the measurement process. It is not a parameter estimator.
This specification introduces no observation runtime, fitting, digitization,
parameter values, simulation changes or production dependency.

Decisions:

- `DNp01_VOLTAGE_RELATIVE_DEFLECTION_POTENTIALLY_COMPARABLE_WITH_CALIBRATION`.
- `SENSORY_STATE_ONLY_QUALITATIVELY_COMPARABLE`.
- `ADDITIONAL_ASSAY_MAPPING_REQUIRED`.

Current sensory transfer remains the Phase 19 shared `k=1 mV_eq/state`,
unnormalized, identity-resolved ipsilateral sum. Nothing in this specification
recommends a replacement gain or infers one from Phase 18's model response.

## Repository gate and authority

Started clean at `49ac64824b042e288f86305dffc57f264c781bbd`, Phase 19,
with `main == origin/main`. Required 18/17/corrected-16/13B commits exist.
Offline replays reproduced the existing identities/results:

| Source | Artifact ID |
| --- | --- |
| Phase 18 | `ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c` |
| Corrected Phase 16 | `bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b` |
| Phase 13B | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` |
| Full numerical Phase 7O | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` |
| Genuine Phase 8C | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` |

Audit authorities: relative-column assignment/exposure and sensory stepping;
`route_population_drive`; `lif_interval_step`, spike stamping/reset;
`ttmn_boundary_step` and the model crossing output; abstract electrical tokens;
`electrical_boundary_step`; `activate_samples`; actuator routing;
`body_interval_step`; scenario runtime and `scenario_playback_api.py` DTOs.
Also reviewed Phase 19 and the existing 8S/8U/9D G1 observation boundaries.
No runtime/documentation semantics contradiction was found.

## Taxonomy and comparison gates

Keep separate: **MaleCNS structural data**, **NeuroFly model state**,
**derived model diagnostic**, **primary physiological measurement**,
**calcium-imaging measurement**, **optogenetic manipulation**,
**behavioral observation**, and **model-space presentation value**.
An optical manipulation is an input intervention, not an amplitude observable;
its voltage/calcium/behavioral readout has its own measurement operator.

Every numerical biological comparison is currently denied. A future comparison
must explicitly pass cell/preparation, source-population/ROI, stimulus-reference,
baseline/unit, observation-transform, temporal-filter/alignment, aggregation/
uncertainty, and data-sufficiency/identifiability gates. Unknown metadata is
**not matched**. A proposed transform is not an established one. Tests protect
these declarations; this is not an implemented runtime comparison service.

## Actual variables and per-variable contract

The JSON records full temporal/population semantics, allowed/forbidden claims,
evidence, assays and identifiability for all twelve required variables plus
structural counts, threshold-margin diagnostics and display coordinates.

| Variable | Current semantics and units | Candidate observable / status | Calibration |
| --- | --- | --- | --- |
| Relative-column exposure | dimensionless record-overlap fraction, not RF activation | registered retinal/RF coverage; unknown transform | uncalibrated |
| Sensory `x_i` | dimensionless leaky state, 311 bodies | source activity via a type-specific assay operator; unknown transform | uncalibrated |
| Per-body `d_i` | `active_i*k*x_i`, mV_eq ledger | controlled identified-source GF effect; no valid operator defined | not calibratable from current assay |
| Aggregate `D_j` | sum of per-body contributions, mV_eq held external drive | physiological population input; no valid operator defined | not calibratable from current assay |
| DNp01 membrane | LIF coordinate, mV_eq, not biological mV | intracellular GF voltage; unknown transform | uncalibrated |
| DNp01 spikes | target-identified model crossing events | GF AP occurrence/time; qualitative comparison only currently | not calibratable from current assay |
| TTMn state | dimensionless decay plus event injection | motor physiological state would require a new observation mapping | not calibratable from current assay |
| Electrical-input token | receipt-derived causal software token | not a biological observable; not a released quantum | not applicable |
| G1 proxy | passive deviation/reference coordinate, mV_eq | matched intracellular G1 evoked deflection; unknown transform | uncalibrated |
| Activation proxy | rectified/clipped static normalization [0,1] | no valid biological activation operator defined | not calibratable from current assay |
| Actuator command | exact side-preserving activation passthrough | virtual functional command, not a biological observable | not applicable |
| Planar body | fixed-heading x/z in world_eq | matched tracked body position; unknown spatial/mechanical transform | uncalibrated |

Exposure at boundary n produces sensory state n+1; state n drives the DNp01
interval n→n+1. First membrane effect is therefore n+2. Threshold crossing in
interval n stamps a spike at n+1; stored membrane is reset after a crossing,
not an AP waveform. TTMn and G1 each decay then receive same-boundary input.
Activation and actuator routing add no temporal state. Body commands at n
drive the outgoing interval only. These software conventions are not measured
biological latencies.

The compact playback DTO copies model membrane/state sums, events, commands
and authoritative positions; it does not create an assay. Its model field
names containing `mv` still mean mV_eq here. Render interpolation and six-second
presentation timing are not scientific samples, physiological time or sensory
feedback. Detailed identity-resolved arrays remain in scientific artifacts.

## Assay compatibility matrix

D = DIRECT; T = TRANSFORM_REQUIRED; Q = QUALITATIVE_ONLY;
I = INCOMPATIBLE; N = NOT_APPLICABLE. **T is conditional, not numeric-ready**:
it may require an unavailable assay/operator and new data. D applies only to
lookup in the same pinned reconstruction, not physiology. Q denotes limited
type/pathway context, never per-body amplitude equivalence.

| Variable | Anatomy | Calcium | Intracellular voltage | Extracellular spikes | Optogenetic manipulation | Muscle ephys | High-speed behavior |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Structural count | D | I | I | I | N | I | I |
| Exposure | Q | T | I | I | Q | I | I |
| Sensory state | I | T | T | I | Q | I | I |
| Per-body contribution | I | I | T | I | Q | I | I |
| Aggregate drive | I | I | T | I | Q | I | I |
| DNp01 membrane | I | I | T | I | Q | I | I |
| DNp01 spikes | I | I | Q | Q | Q | I | I |
| TTMn state | I | I | I | I | Q | I | I |
| Electrical token | N | N | N | N | N | N | N |
| G1 proxy | I | I | I | I | I | T | I |
| Activation proxy | I | I | I | I | I | I | I |
| Actuator command | N | N | N | N | N | N | N |
| Planar body | I | I | I | I | Q | I | T |
| Threshold margin | I | I | T | I | I | I | I |
| Presentation position | N | N | N | N | N | N | N |

Muscle ephys is separated from the neuronal intracellular-voltage column.
Recorded muscle potentials cannot substitute for TTMn state or GF spikes.

## Primary assays, preparation and accessible evidence

Bounded verification used existing project references and original/official
sources. No broad parameter search, trace extraction or figure digitization.
Every assay record distinguishes published traces, summaries and raw-data
availability. Raw synchronized trial/source-population data were not acquired.

| Assay / evidence | Observable and measurement context | Availability and applicability |
| --- | --- | --- |
| [Ache 2019](https://www.researchgate.net/publication/331408732_Neural_Basis_for_Looming_Size_and_Velocity_Encoding_in_the_Drosophila_Giant_Fiber_Escape_Pathway) | right GF soma current clamp, tethered 3–5-day D. melanogaster females; visual 10°→90° looming and LC4/LPLC2 perturbations; biological mV, 20 kHz digitization/10 kHz filtering, 360 Hz projector | published waveforms/component summaries; useful for operator design, not current calibration; stimulus clock and per-trial baseline/source mapping required |
| [Klapoetke 2017 GF optogenetics](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457385/) | tethered 3–5-day females; LPLC2 population activation, GF current clamp; 50 ms optical pulses, 40 kHz samples/10 kHz filtering | population GF response and peaks; qualitative connectivity/sign, not per-body efficacy |
| Same source, LPLC2 calcium | mounted 2–5-day females; axon/terminal ROIs; ΔF/F or peak-normalized ΔF with distinct baseline definitions; 300 ms peak-window averaging | imaging curves/methods support operator design; not direct x_i or membrane timing |
| [von Reyn 2017](https://www.sciencedirect.com/science/article/pii/S0896627317304749) | LC4-associated GF responses after pathway manipulation, biological voltage/behavioral features | primary publisher summary plus Ache reanalysis context; not a located source-cell x_i measurement; do not inherit LPLC2 optical operators |
| [Koenig–Ikeda 2007](https://pubmed.ncbi.nlm.nih.gov/17392409/) | adult Drosophila TTM G1 intracellular recording and release/recycling assays | primary abstract/indexed passages and prior 8S curation; full publisher retrieval failed again; no new complete protocol/trace claim |
| [Kadas 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6709211/) | age-specific, both-sex motor-region stimulation→TTM potential onset; 300 Hz–10 kHz acquisition band | open methods/table/traces; composite latency, not isolated NMJ delay, G1 voltage or motor-state measurement |
| Ache high-speed behavior | whole-fly looming trials, 6000 Hz video, takeoff sequences/trial outcomes | behavioral consequences, incompatible with current transfer calibration and uncalibrated planar mechanics |

Recorded GF rest and electrode conventions matter: the reviewed GF recordings
did not apply the approximately 13 mV junction correction. Absolute rest cannot
be identified with model rest. G1's single-fiber scope and miniature/evoked
distinction remain under 8S authority; no reused historical amplitude is treated
as a fresh measurement or proxy calibration target.

## GF/DNp01 and source identity compatibility

[Namiki 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6019073/) explicitly
identifies Giant Fibers as DNp01. This establishes terminology/type-level
compatibility with pinned DNp01 10001/R and 10010/L, not identity of experimental
animals, sex/preparation or recording location. MaleCNS is a male reconstruction;
the reviewed GF voltage preparations are female. Type correspondence does not
remove these assay-compatibility requirements. A vaguely labelled descending
neuron without type/anatomical confirmation does not pass the identity gate.

LC4 evidence concerns an LC4-associated GF feature component, anatomical input,
manipulation and behavior. It is not automatically a source LC4 voltage trace.
LPLC2 has separate source calcium and population-opto/GF assays. They neither
measure the same quantity nor justify identical LC4/LPLC2 observation operators.
No matched LC4 source-state dataset was established in this bounded audit.

MaleCNS/neuPrint counts remain [reconstructed postsynaptic-density counts](https://github.com/connectome-neuprint/neuPrint/blob/master/pgmspecs.md).
They cannot weight ROI averages, calcium fluorescence or source efficacy.
Same-source structural overlap can be audited numerically as anatomy; it does
not establish registered retinal illumination or physiological exposure.

## Candidate operator forms — proposals only

All symbols below are unknown quantities or declared processing operations,
not fitted parameters or newly chosen numerical values.

| Mapping | Minimal conceptual form | Missing information |
| --- | --- | --- |
| Exposure→coverage | world/retina/RF registration plus declared coverage operation | retinal calibration, per-body RF/ROI crosswalk |
| x_i→calcium | `sample(normalize(indicator(calcium(activity_map_type(x_i)))))` | source-activity meaning, nonlinear indicator, calcium/filter kinetics, gain/baseline, ROI, timestamps |
| x_i→source voltage | type-specific activity/voltage map followed by electrode/filter/sample operator | compatible source recording and state scale; target GF assay cannot supply it |
| d_i→unitary effect | controlled source-activity and target-measurement operators | identified source activation, circuit context, target transform; no valid current operator |
| D_j→physiological input | population activation operator and physiological-input map | activated-body membership/magnitudes, input mechanism; GF voltage is an output, not D_j |
| GF relative voltage | `y=sample(filter(a*(V_eq(aligned_t)-B_eq)))` relative to measured baseline | scale a, soma/point-state compatibility, stimulus alignment and trial traces |
| GF absolute voltage | relative operator plus independently determined biological baseline/offset b | all relative prerequisites plus electrode/junction/reference conventions |
| GF events | detected event occurrence/time after common stimulus-clock alignment | event detection/identity, trials, stochasticity, time-zero, dt uncertainty |
| G1 deflection | baseline-relative proxy plus fiber-specific scale/filter/sample operator | fiber and protocol match, input-token mapping, trace/window, voltage scale |
| Body→tracking | spatial map followed by camera/landmark projection | world_eq scale, orientation, contact/behavior/mechanical applicability |

There is no current biological operator for tokens, virtual commands or render
coordinates. TTMn state and normalized activation require separately justified
biological definitions before an assay can be assigned. Diagnostic threshold
margin additionally requires a matched physiological threshold definition.

### Absolute voltage, relative deflection, peak, shape and events

Absolute GF potential has unknown reference/scale and measurement offsets.
Baseline subtraction can remove a constant offset, but not scale, drift,
preparation effects or state mismatch. Thus relative deflection is a promising
**conditional** target, not already calibrated mV_eq. Peak requires a declared
window and spike handling. Waveform shape requires matched stimulus, filtering,
sampling and latency; normalizing curves does not identify absolute gain.
Threshold crossings compare an event class, not the LIF reset shape to an AP.
None permits a numeric comparison with the current exploratory world stimulus
without a compatible experimental stimulus reference.

### Calcium and population processing

Calcium comparison needs activity→calcium kinetics, nonlinear/saturating
indicator response, optical/background/bleaching handling, baseline definition,
sampling/integration rate and independently defined ROI membership/weights.
Do not compare slow optical waveforms directly with membrane time or equate
peak-normalized fluorescence with x_i. Each population needs its own evidence.

Observation-side sum, mean, active fraction, weighted mean, peak and temporal
integral are alternatives, not production changes. Fix the membership and
denominator, units and missing-cell policy before use. A peak of the population
mean differs from the mean of individual peaks. Weighted means require optical
or sampling justification; contact counts are not such weights. Active fraction
requires a declared detector. Population integration adds time to the units.
Population optogenetics also requires driver-expression/illumination mapping
to per-body activity; dividing GF response by neuron count is not efficacy.

### Spike timing and behavior

GF event occurrence is closer to an observable class than mV_eq amplitude, but
current scenario times are not calibrated biological latency. Future comparison
requires common onset/TTC definitions, synchronized clocks, identified units,
detector/sorting rules, repeated trials and uncertainty. Deterministic model
events do not represent the biological trial distribution. Do not fit an
arbitrary time shift to manufacture agreement.

Behavioral probability, takeoff latency or displacement cannot identify sensory
transfer. Body tracking would require a calibrated coordinate and biomechanical
mapping; current fixed-heading, no-contact planar displacement is not a jump.
At most, carefully matched future qualitative event comparisons are possible.

## Identifiability and data sufficiency

| Arrow | Status | Limit |
| --- | --- | --- |
| x_i→presynaptic biological activity | `UNKNOWN_TRANSFORM` | source-state observation scale/modality absent |
| Presynaptic activity→postsynaptic effect | `QUALITATIVELY_CONSTRAINED` | pathway excitation, not body-specific magnitude |
| Identified source activity→unitary GF effect | `NOT_MEASURED` | matched dataset not located in bounded audit, not proof of universal absence |
| Physiological voltage→electrode sample process | `KNOWN` | reviewed modality/filter/acquisition described; trial baselines/timestamps still required |
| Current D_j→measured GF voltage | `UNKNOWN_TRANSFORM` | input mechanism, population mapping and target scale unresolved |

LC4:LPLC2 per-body relative efficacy remains non-identifiable. Feature-component
amplitudes can differ through source states, recruitment, temporal/spatial
properties or circuit context; they cannot supply efficacy ratios without a
valid population operator. Production sum semantics remain unchanged.

GF visual voltage and LPLC2 calcium records are
`SUFFICIENT_FOR_OPERATOR_DESIGN_ONLY`; population optogenetic and LC4 functional
records are `QUALITATIVE_ONLY` for the current mapping. G1 evidence remains
qualitative/unmatched. Connectome, composite muscle latency and behavior are
`INCOMPATIBLE` with current transfer calibration. No assay is currently
`SUFFICIENT_FOR_CALIBRATION`. Published curves may be digitizable in future but
were not digitized; figures/summary statistics are not raw synchronized trials.

## Calibration readiness and next action

Readiness is `ADDITIONAL_ASSAY_MAPPING_REQUIRED`, not numerical calibration or
an approved fitting protocol. The state definitions need not be redesigned to
write this specification, but no evidence yet establishes a usable transform.
No training split, loss, eligible fitting parameters or coefficients are
selected. A future objective must be assay-based, never spike/movement/escape
targeting; it also needs held-out validation and identifiability checks.

Exactly one next scientific action: locate and audit a synchronized GF voltage
dataset with stimulus and source-population activation metadata against these
compatibility gates. Inventory what is available/missing; do not fit, digitize
or retune in that audit.

## Machine-readable contract and verification

The adjacent JSON uses `neurofly_observation_operator_contract_v1`, with 15
variable records, 8 assay records, 17 mappings and a 15×7 compatibility matrix.
`contract_id` is canonical SHA-256 of the `contract` object, including schema,
policy, evidence, classifications and operator forms. It is an auditable
scientific specification, not a simulation artifact or runtime input.

Identity: `ae50e1faad223cdde63125a6216ce0993523f9933025fe1f04e9265450dec824`.
Focused tests validate canonical identity/mutation, required variables, unique
IDs, references, metadata, classifications, matrix completeness and prohibitions
on silent calibration. Numerical replay remains under historical authorities.

Phase 20 verification: four focused tests passed; the full Python suite passed
1,022 tests with one existing deselection and two dependency deprecation warnings
(548.54 s). All five required historical replays passed unchanged. Frontend
regression tests passed (53); frontend lint/typecheck/build, Python Ruff check,
Ruff format check and Git diff check passed. Only this specification, its JSON,
the isolated contract tests and the minimal Project Context update changed.
No commit or push.
