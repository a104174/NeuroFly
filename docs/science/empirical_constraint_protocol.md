# Phase 2G — empirical constraint and validation protocol

## Scope and decision

Phase 2G pre-registers the evidence boundary for the first NeuroFly circuit.
It does not fit a parameter, change the E1 encoder, change the LIF model, or
digitize a figure. The current free quantities remain:

- E1 encoder: `G_LC4`, `G_LPLC2`, `omega_half`, and `theta_half`;
- neural coupling: `k_syn`.

The readiness decision is **G2**: the audited public evidence supports
relative, normalized, qualitative, and downstream constraints, but it does
not provide a machine-readable set that identifies the four encoder
parameters and `k_syn` in their NeuroFly units. An observation-model/data
ingestion phase must precede physiological fitting.

No repository-owned numeric dataset is added in this phase. The waveform data
needed for a defensible initial fit are presented in figures and are described
by the papers as available from the authors on request. Copying plotted pixels
would manufacture precision, while committing third-party traces before their
license and semantics are confirmed would be premature.

## Source hierarchy and audit method

The audit used, in order, machine-readable primary source material,
supplementary tables, article text/methods, and explicitly published model
coefficients. A plotted value without source data is recorded as
`FIGURE_ONLY_NOT_EXTRACTED`. No pixel digitization was performed.

Primary sources:

1. Ache et al. (2019), *Neural Basis for Looming Size and Velocity Encoding in
   the Drosophila Giant Fiber Escape Pathway*,
   [doi:10.1016/j.cub.2019.01.079](https://doi.org/10.1016/j.cub.2019.01.079).
2. Klapoetke et al. (2017), *Ultra-selective looming detection from radial
   motion opponency*,
   [doi:10.1038/nature24626](https://doi.org/10.1038/nature24626), with its
   [primary author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457385/).
3. von Reyn et al. (2014), *A spike-timing mechanism for action selection*,
   [doi:10.1038/nn.3741](https://doi.org/10.1038/nn.3741), with the
   [author-hosted article PDF](https://www.janelia.org/sites/default/files/Library/nn.3741.pdf).

### Ache et al. 2019

- **Measurement:** whole-cell patch-clamp voltage from the GF during looming.
  Silencing LPLC2 exposes an LC4-associated, velocity-like GF component
  (`N=5`); silencing LC4 exposes an LPLC2-associated, size-like GF component
  (reanalyzed data, `N=7`). Controls were `N=6`.
- **Stimulus:** looming disks parameterized by radius/velocity (`r/v`). Figure
  3 uses 10, 20, 40, and 80 ms; methods also describe a wider 10, 40, 70, 100,
  and 140 ms set for other experiments.
- **Processing:** mean GF traces are shown with SEM; responses were smoothed
  with a 10 ms sliding window, while peak timing used 1 ms smoothing.
- **Reported model:** a shifted angular-velocity term plus a shifted Gaussian
  angular-size term describes GF-level voltage. Published constants are
  auditable context, not upstream encoder measurements: `C1=0.0002567`,
  `d1=0.019 s`, `C2=1.7`, `C3=42 degrees`, `C4=0.52`, and `d2=0.019 s`.
- **Combination:** the weighted sum of isolated components explains the mean
  combined response well (`R²=0.93 ± 0.03` across the reported `r/v`
  conditions). The component weights were 1.5 for the LC4-associated trace
  (LPLC2-silenced) and 1.1 for the LPLC2-associated trace (LC4-silenced).
  Residual structure is consistent with omitted inhibition and/or nonlinear
  integration, but does not identify its mechanism.
- **Availability:** figures and a figure supplement are public. The article
  directs data requests to the authors and says the GF input model would be
  deposited in ModelDB; the public ModelDB citation record does not expose the
  needed raw traces. No machine-readable voltage traces or uncertainty arrays
  were located.
- **What it supports:** pathway roles, stimulus protocol, downstream GF
  waveform semantics, sample sizes, uncertainty display, and candidates for
  pathway-isolated and combined validation.
- **What it does not support:** direct LC4/LPLC2 external drive in `mV_eq`, a
  unique `k_syn`, an encoder-only latency, or copying the GF phenomenological
  equation into E1.

### Klapoetke et al. 2017

- **Measurement:** in-vivo two-photon GCaMP calcium signals from LPLC2
  population axon terminals and individually resolvable axons. Population
  traces average three trials (`N=8` flies) and peak summaries report mean and
  95% confidence intervals. Common single-cell experiments use `n=10`
  neurons from `N=7` flies.
- **Stimulus:** dark and bright looming over several speeds, constant-edge-
  velocity expansion, dark receding, motion-free darkening, contraction, and
  wide-field motion. Population stimuli were presented to the right eye; the
  article reports detectable LPLC2 population response within the first 5
  degrees of expansion.
- **Sampling/normalization:** volumetric calcium sampling was approximately
  5.6–7.4 Hz. Population axon-terminal data use a two-second prestimulus
  baseline for delta-F/F. Several single-cell analyses instead normalize each
  trace to that neuron's peak response to a defined dark loom (commonly 5 to
  60 degrees, `r/v=40 ms`). Peak fluorescence may be an average over a 300 ms
  window around the maximum.
- **Availability:** the manuscript says imaging data and analysis code are
  available on reasonable request. Public supplements contain methods,
  genotype/anatomy tables, and video rather than numeric calcium traces.
- **What it supports:** LPLC2 selectivity and response ordering, source
  normalization semantics, uncertainty representation, and qualitative/null
  validation for expansion, receding, contraction, darkening, and
  translation.
- **What it does not support:** direct equivalence between calcium and E1
  `mV_eq`, millisecond LIF timing, a body-specific MaleCNS response, or an
  absolute `G_LPLC2`.

### von Reyn et al. 2014

- **Measurement:** whole-cell intracellular recordings from GF soma during a
  head-fixed looming assay, synchronized with high-speed behavior. Looming
  elicited one or two GF spikes in a subset of flies (10 of 33). First-spike
  rasters comprise 27 trials from 10 flies.
- **Stimulus:** expanding looming objects with reported `r/v` conditions;
  Figure 4 compares GF spike timing with free-behavior takeoff for 14, 40, and
  70 ms `r/v` values. Timing is referenced to stimulus onset and theoretical
  time of contact as specified by the figure/protocol.
- **Timing result:** a GF spike was followed by middle-leg extension in
  `0.9 ± 0.2 ms` and flight initiation in `2.0 ± 0.1 ms` across 27 trials in
  five flies. GF spike timing relative to parallel escape circuitry, not a
  single voltage amplitude, distinguished short and long action sequences.
- **Availability:** article figures provide rasters and distributions, not a
  machine-readable first-spike table located by this audit.
- **What it supports:** GF spike time is biologically meaningful and should
  be held out from fitting; source time references, trial counts, and
  downstream behavioral context are auditable.
- **What it does not support:** fitting the current DNp01-only model to motor
  latency, because TTMn/PSI, gap junctions, muscles, and behavior are outside
  its boundary. Escape-mode outcome is `CONTEXT_ONLY` for Phase 2G.

## Constraint schema

Any future machine-readable constraint record must have these fields:

| Field | Required semantics |
| --- | --- |
| `constraint_id` | stable, unique project identifier |
| `citation_doi` | primary-source DOI |
| `source_location` | exact figure, table, supplement, methods/text, or source file |
| `source_data_status` | machine-readable, tabulated, text-exact, or `FIGURE_ONLY_NOT_EXTRACTED` |
| `experimental_population` | measured/manipulated cell population |
| `pathway_condition` | control, pathway isolation, combined, or intervention |
| `stimulus_definition` | geometry, timing, contrast, and `r/v`/speed where supplied |
| `measured_observable` | source measurement, not a NeuroFly reinterpretation |
| `units` | source units or `normalized_dimensionless` |
| `time_reference` | stimulus onset, disk appearance, time-to-contact, or other exact reference |
| `value` / `range` | only directly reported values; nullable for figure-only records |
| `uncertainty` | SEM, SD, CI, individual data, or explicitly unavailable |
| `sample_size` | source `n`/`N` definition |
| `measurement_modality` | GF voltage, GF spike, calcium, or behavior |
| `source_normalization` | exact baseline/reference operation |
| `neurofly_observable` | legitimate comparable telemetry or `none` |
| `observation_transform` | predeclared transform or `none` |
| `input_vocabulary` | `SUPPORTED_BY_CURRENT_INPUT_VOCABULARY` or `REQUIRES_RICHER_SENSORY_MODEL` |
| `intended_role` | one allowed role below |
| `limitations` | modality, availability, and model-boundary caveats |

Allowed roles are exactly `FIT_CONSTRAINT`, `HELD_OUT_VALIDATION`,
`QUALITATIVE_VALIDATION`, `CONTEXT_ONLY`, and
`NOT_DIRECTLY_COMPARABLE`.

## Curated constraint inventory

No-null `value` below means a number was explicitly reported in text/methods.
Waveforms remain unextracted until author/source data are obtained.

| ID | Source/location | Modality and units | Available value/uncertainty | NeuroFly comparator | Role |
| --- | --- | --- | --- | --- | --- |
| `ACHE19_LC4_GF_ISOLATED_WAVEFORM` | Ache Fig. 3A/B; methods | GF whole-cell voltage, mV; LPLC2 silenced; disk appearance/TOC | Figure-only mean ± SEM; `N=5`; 10 ms smoothing | equivalently filtered/normalized DNp01 voltage for LC4-only protocol | `FIT_CONSTRAINT` |
| `ACHE19_LPLC2_GF_ISOLATED_WAVEFORM` | Ache Fig. 2H, Fig. 3C/D; methods | GF whole-cell voltage, mV; LC4 silenced | Figure-only mean ± SEM; `N=7`; 10 ms smoothing | equivalently filtered/normalized DNp01 voltage for LPLC2-only protocol | `FIT_CONSTRAINT` |
| `ACHE19_ISOLATED_PEAK_TIMING` | Ache Fig. 3E/F; methods | GF peak time relative to contact, ms | Figure-only mean ± SEM; 1 ms smoothing | DNp01 subthreshold peak time under matched isolated protocols | `HELD_OUT_VALIDATION` |
| `ACHE19_COMBINED_GF_WAVEFORM` | Ache Fig. 2H/L and Fig. 4 | GF whole-cell voltage, mV | Figure-only mean ± SEM; control `N=6` | combined DNp01 voltage after identical observation transform | `HELD_OUT_VALIDATION` |
| `ACHE19_WEIGHTED_COMPONENT_MODEL` | Ache Results/Methods | GF-level phenomenological model, mixed published units | weights 1.5 LC4-associated / 1.1 LPLC2-associated; `R²=0.93 ± 0.03` | none: diagnostic context only | `CONTEXT_ONLY` |
| `ACHE19_TRANSIENT_LATENCY_19MS` | Ache Methods, GF input model | disk appearance to transient GF response, ms | `19 ms`; uncertainty not reported | none in current pipeline | `NOT_DIRECTLY_COMPARABLE` |
| `KLAP17_LPLC2_DARK_LOOM_SPEED_SERIES` | Klapoetke Fig. 2D/E | population GCaMP delta-F/F, source-normalized | Figure-only; mean ±95% CI; `N=8`, 3 trials/trace | normalized E1 LPLC2 feature or normalized visual output only through a declared calcium observation model | `FIT_CONSTRAINT` |
| `KLAP17_LPLC2_EARLY_EXPANSION` | Klapoetke text/Extended Data Fig. 3C–E | population calcium; angular diameter | detectable within first `5 degrees`; no numeric detection criterion | ordering/onset diagnostic only | `QUALITATIVE_VALIDATION` |
| `KLAP17_LPLC2_RECEDING_NULL` | Klapoetke Fig. 2E | population calcium, source-normalized | figure-only, `N=8` | current E1 receding zero-drive direction | `QUALITATIVE_VALIDATION` |
| `KLAP17_LPLC2_CONTRACTION_NULL` | Klapoetke Fig. 4/Extended Data | single-cell calcium, dark-loom normalized | figure-only, commonly `n=10`, `N=7` | E1 negative-expansion gate only; spatial opponency is absent | `QUALITATIVE_VALIDATION` |
| `KLAP17_LPLC2_DARKENING_NULL` | Klapoetke Fig. 2E | population calcium, source-normalized | figure-only, `N=8` | none: stimulus cannot be represented by scalar E1 geometry | `NOT_DIRECTLY_COMPARABLE` |
| `KLAP17_LPLC2_TRANSLATION_NULL` | Klapoetke Fig. 2F/G | population calcium, delta-F/F | figure-only, `N=8`; 20 deg/s wide-field motion | none: current input vocabulary lacks translation | `NOT_DIRECTLY_COMPARABLE` |
| `VREYN14_GF_FIRST_SPIKE` | von Reyn Fig. 4A/B | intracellular GF first-spike time, ms | figure-only raster; 27 trials/10 flies | per-DNp01 first spike only under a reconstructable matched protocol | `HELD_OUT_VALIDATION` |
| `VREYN14_GF_TO_MOTOR_LATENCY` | von Reyn Results/Fig. 4C | GF spike to behavior, ms | leg `0.9 ± 0.2`; flight `2.0 ± 0.1`; 27 trials/5 flies | none: downstream circuit absent | `CONTEXT_ONLY` |

### Current-input vocabulary classification

- Receding and the sign of contraction are
  `SUPPORTED_BY_CURRENT_INPUT_VOCABULARY`; E1 predicts zero drive by its
  versioned positive-expansion policy. This tests model direction only, not
  the biological radial-opponency mechanism.
- Motion-free darkening and wide-field translation are
  `REQUIRES_RICHER_SENSORY_MODEL`. They must not be scored against the LIF
  dynamics.
- Body-specific/off-center LPLC2 responses require Level C or another spatial
  input model and are outside this calibration protocol.

## Non-usable or deferred evidence

- No plotted trace, point, error bar, or raster was digitized. Relevant Ache,
  Klapoetke, and von Reyn plots remain `FIGURE_ONLY_NOT_EXTRACTED`.
- Ache's GF-level angular-velocity-plus-Gaussian-size equation is not an
  LC4/LPLC2 encoder equation. Its coefficients and component weights are
  `CONTEXT_ONLY`.
- Klapoetke calcium amplitude is not LIF voltage or `mV_eq`. The indicator,
  imaging rate, baseline, and normalization prevent direct amplitude or
  millisecond timing comparison.
- Individual LPLC2 receptive-field maps are not transferred to MaleCNS bodies
  and do not unlock Level C.
- von Reyn behavioral latency cannot validate a simulator that stops at
  DNp01. It requires downstream electrical/chemical circuitry and mechanics.
- The public supplements located in this audit do not contain the raw numeric
  traces. Author-request data must be licensed and semantically verified
  before a tracked dataset is created.

## Timing semantics

The approximately 19 ms value in Ache is `d1`, the latency from **disk
appearance** to the transient GF response in LPLC2-silenced GF recordings—the
condition retaining the LC4-associated component. It is used as the shift of
the angular-velocity term. The size-component shift `d2` was set equal to 19
ms, not independently measured for LPLC2.

The current NeuroFly chain is different:

```text
stimulus sample time
  -> same-step E1 external drive (no visual latency model)
  -> LC4/LPLC2 threshold crossing
  -> configured chemical event delay
  -> DNp01 membrane response and spike
```

Consequently 19 ms must not be inserted as E1 latency, chemical delay, or GF
delay, and drive-onset-to-DNp01 time must not be fitted to it. A future matched
comparison needs a separately justified upstream visual-processing observation
bridge and must retain these clocks:

1. paper stimulus onset/disk appearance and theoretical contact;
2. reconstructed NeuroFly stimulus time;
3. E1 output time (currently same step);
4. visual-neuron spike time;
5. delivered-event time;
6. DNp01 voltage/spike time.

No generic free shift is allowed. Any future offset must name the stages it
represents and have evidence/provenance independent of the held-out data.

## Parameter-to-observable identifiability matrix

| Observable | `G_LC4` | `G_LPLC2` | `omega_half` | `theta_half` | `k_syn` |
| --- | --- | --- | --- | --- | --- |
| LC4 relative timing/response curve | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` | `PRIMARY_CONSTRAINT` | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` |
| LPLC2 relative calcium response/profile | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` | `PRIMARY_CONSTRAINT` | `NOT_IDENTIFIABLE` |
| isolated GF LC4-associated subthreshold waveform | `SECONDARY_CONSTRAINT` | `NOT_IDENTIFIABLE` | `SECONDARY_CONSTRAINT` | `NOT_IDENTIFIABLE` | `SECONDARY_CONSTRAINT` |
| isolated GF LPLC2-associated subthreshold waveform | `NOT_IDENTIFIABLE` | `SECONDARY_CONSTRAINT` | `NOT_IDENTIFIABLE` | `SECONDARY_CONSTRAINT` | `SECONDARY_CONSTRAINT` |
| combined GF waveform | `VALIDATION_ONLY` | `VALIDATION_ONLY` | `VALIDATION_ONLY` | `VALIDATION_ONLY` | `VALIDATION_ONLY` |
| GF first-spike timing | `VALIDATION_ONLY` | `VALIDATION_ONLY` | `VALIDATION_ONLY` | `VALIDATION_ONLY` | `VALIDATION_ONLY` |
| LPLC2 receding/contraction selectivity | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` | `NOT_IDENTIFIABLE` |
| darkening/translation nulls | `NOT_DIRECTLY_COMPARABLE` | `NOT_DIRECTLY_COMPARABLE` | `NOT_DIRECTLY_COMPARABLE` | `NOT_DIRECTLY_COMPARABLE` | `NOT_DIRECTLY_COMPARABLE` |

The secondary classifications for isolated GF voltage are joint rather than
independent constraints. Downstream GF voltage constrains a product of encoder
gain, thresholded presynaptic events, structural count, and `k_syn`; without
an independently observed visual spike/event process, it does not identify a
gain or `k_syn` alone. Normalization removes absolute gain information. This
agrees with the Phase 2C/2F response surface.

## Pre-registered fit and validation partition

This partition applies only after source traces and their reuse terms have
been obtained. It must be frozen before fitting begins.

### Fit/constraint set

1. `KLAP17_LPLC2_DARK_LOOM_SPEED_SERIES`: use only source-equivalent
   normalized response shapes/order to constrain `theta_half`; use a declared
   calcium observation transform, not raw voltage matching.
2. `ACHE19_LC4_GF_ISOLATED_WAVEFORM` and
   `ACHE19_LPLC2_GF_ISOLATED_WAVEFORM`: use the 20, 40, and 80 ms `r/v`
   conditions for normalized temporal shape. Absolute GF voltage may constrain
   pathway products only after feature shape and presynaptic timing are fixed.
3. Qualitative sign/order constraints from the LPLC2 receding/contraction
   controls may reject an encoder policy but do not determine a gain.

The 10 ms `r/v` isolated condition is reserved as the untrained looming
trajectory/extreme-speed check.

### Held-out validation set

1. `ACHE19_ISOLATED_PEAK_TIMING`, including the held-out 10 ms `r/v`
   condition;
2. `ACHE19_COMBINED_GF_WAVEFORM` for all available matched conditions;
3. `VREYN14_GF_FIRST_SPIKE` under a reconstructable matched protocol;
4. combined-versus-isolated response ordering/residual structure.

No held-out result may trigger retuning. A revised model or observation model
requires a new protocol version and a fresh held-out partition.

### Qualitative and context-only set

- LPLC2 looming/receding/contraction direction and early-expansion detection
  are qualitative validation.
- Darkening and translation document a known E1 vocabulary failure and are
  not neural-model scores.
- von Reyn motor latencies/action modes and Ache phenomenological constants
  remain context only.

## Observation transforms and amplitude policy

Phase 2G selects **relative/normalized shape first; defer absolute encoder
gains and physiological coupling**.

- For a source normalized to baseline and peak, apply the exact same baseline
  window and peak/reference normalization to the corresponding NeuroFly trace.
- For Ache voltage traces, reproduce the stated 10 ms smoothing for waveform
  comparison and 1 ms smoothing for peak timing; retain unsmoothed NeuroFly
  telemetry as the primary simulation record.
- A calcium comparison requires a predeclared calcium observation model or a
  deliberately coarse relative metric. Phase 2G does not invent an indicator
  kernel. Until one is justified, use peak ordering and normalized waveform
  shape at the source sampling grid, not voltage amplitude or millisecond
  phase.
- Resample only onto explicitly documented paper time points with a declared
  interpolation rule. Never shift curves to maximize similarity.
- Do not introduce one nuisance amplitude per trace. Such factors would absorb
  the parameters intended to be constrained. Absolute `G_LC4`, `G_LPLC2`, and
  `k_syn` remain unresolved until an independent visual activity scale or
  presynaptic timing measurement supplies the missing bridge.

## Uncertainty policy

- Preserve individual observations when supplied; otherwise retain reported
  mean plus its named SEM, SD, CI, or percentile interval.
- Keep biological replicate (`N`), cell (`n`), trial, and fly counts distinct.
- Preserve covariance across a time series when individual traces permit it;
  do not treat each time point as an independent replicate.
- Preserve source normalization before averaging. Do not convert SEM to SD
  without the exact sample definition.
- Figure-only results retain `value=null` and their displayed uncertainty type;
  no coordinates or error values are guessed.
- The 19 ms result has no reported uncertainty in the fitted constant and must
  not be converted into an exact deterministic target.

## Future validation procedure

1. Acquire author/source data and verify license, files, protocol labels,
   units, normalization, and subject/trial identifiers.
2. Materialize the versioned constraint schema and freeze its hashes and the
   partition above.
3. Construct the exact supported stimulus protocols with existing
   `LoomingStimulus`; mark any unreconstructable protocol as non-comparable.
4. Declare one parameter configuration and all observation transforms before
   evaluation.
5. Generate deterministic model telemetry and apply only those transforms.
6. Evaluate fit constraints: source-normalized waveform similarity and
   qualitative ordering; use uncertainty-aware metrics where source data
   permit them.
7. Freeze fitted parameters and configuration identity.
8. Evaluate held-out isolated timing, the 10 ms `r/v` condition, combined GF
   waveform, and GF first-spike timing without retuning.
9. Publish successes and failures, including unsupported controls.

No arbitrary pass percentage is registered. Direction/order tests use their
predeclared qualitative sign. Numeric waveform or timing thresholds remain
unresolved until the actual source sampling grid and uncertainty are present;
then they must be grounded in confidence intervals and combined experimental
plus fixed-step timing resolution.

## Falsification criteria

The following outcomes count against the current E1 + homogeneous LIF model;
they are not opportunities to redefine success after observing validation:

- no single `omega_half` or `theta_half` preserves isolated pathway response
  ordering across the fit and held-out `r/v` conditions;
- matched visual activity timing still requires incompatible `k_syn` values
  for LC4- and LPLC2-isolated GF subthreshold voltage;
- held-out combined GF voltage systematically exceeds or differs in shape from
  the model beyond source variability, indicating a missing interaction,
  inhibition, or intrinsic mechanism;
- encoder scales that fit isolated traces destroy held-out GF first-spike
  ordering/timing;
- the homogeneous population produces synchronized spike structure
  incompatible with available population or GF waveforms;
- receding/contraction direction fails even though those signs are supported
  by E1's vocabulary;
- an observable needed for success depends on darkening, translation, or
  body-specific visual space that E1 cannot represent.

The final case falsifies the adequacy of the present sensory boundary for that
experiment, not necessarily the LIF integrator.

## G2 readiness and smallest Phase 2H specification

**Decision: G2 — only relative/normalized constraints are presently usable;
observation-model calibration must precede physiological fitting.**

The evidence is sufficient to pre-register roles, protocols, transformations,
and falsification. It is insufficient to identify all five free quantities:
public raw traces are absent, calcium and LIF states have different modality
and bandwidth, LC4 activity is observed mainly through downstream GF voltage,
and the current model omits upstream visual latency.

The smallest supported Phase 2H is therefore an empirical-data ingestion and
observation-transform slice, not a five-parameter optimizer:

1. request/obtain the Ache isolated/combined voltage traces and Klapoetke
   population calcium traces with reuse permission;
2. add a small versioned constraint file conforming to this schema, storing
   source data or immutable references/checksums as licensing permits;
3. implement a deterministic loader with schema, units, role, duplicate-ID,
   provenance, and partition validation;
4. implement only source-declared baseline, normalization, smoothing, and
   sampling transforms;
5. expose deterministic normalized-shape/order metrics on the fit subset and
   locked evaluation on held-out records;
6. demonstrate parameter sensitivity without selecting calibrated gains or
   `k_syn` until an independent amplitude/timing bridge exists.

No black-box optimizer, graph change, Level C mapping, or neural/encoder
equation change is justified by this audit.

## Scientific safeguards

- No parameter was fitted or manually tuned.
- No figure pixels were reverse-engineered.
- No uncertainty was invented.
- The 19 ms GF response offset was not used as encoder or synaptic latency.
- Calcium, GF voltage, GF spikes, and behavior remain distinct modalities.
- No Level C mapping or body-specific receptive field was introduced.
- No E1 encoder, LIF model, active graph, or structural-weight semantics
  changed.
