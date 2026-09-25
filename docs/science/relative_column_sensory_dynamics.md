# Phase 7E — bounded relative-column sensory model states

Phase 7E derives four individual, reproducible **exploratory dimensionless
model states** from the replay-verified Phase 7D anatomical-exposure artifact.
It is a separate model/artifact domain. Its output is not a biological sensory
response.

## Scope and source boundary

The only input is Phase 7D artifact
`404473c66c36b9f0332a203928200552c6c2e5490af446caae6c3d7475daafbe`, schema
`relative_column_sensory_assignment_artifact_v1`. The artifact is replayed
against its pinned local source and workbook before generation. Phase 7D source
contract identity is
`874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21`; column
grid SHA-256 is
`d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`.
Phase 7D config/result payload hashes are captured in the Phase 7E config.
The model additionally checks that the in-memory Phase 7D payload still
matches its manifest hashes before using it.

The exact scope is:

| Body ID | Type | Side |
| ---: | --- | :-: |
| 12032 | LC4 | L |
| 16128 | LC4 | R |
| 11498 | LPLC2 | L |
| 14465 | LPLC2 | R |

No other sensory body, DNp01 state, TTMn state, or downstream connection is
included. Each condition uses the Phase 7D grid (`dt_ms = 0.1`) and its stored
integer sample order. The model never reads angular looming signals, type-level
encoder drives, source structural counts directly, morphology, or playback
state.

## Model and temporal semantics

The model identity is
`relative_column_exploratory_sensory_state_v1`, configuration schema
`relative_column_sensory_state_config_v1`, and result schema
`relative_column_sensory_state_result_v1`. For each body and each stimulus,
the scalar `x` is dimensionless and starts at `x[0] = 0`.

For the Phase 7D anatomical exposure `e[n]` held constant on
`[n·dt, (n+1)·dt]`, the exact zero-order-hold update is:

```text
alpha = exp(-dt_ms / tau_sens_ms)
x[n+1] = alpha * x[n] + gain * e[n] * (1 - alpha)
```

The timeline stores `state_step = 0` at time zero; assignment sample `n`
produces state boundary `n+1`, with display time derived as
`(n+1) * dt_ms`. Integer step is authoritative. The fixed ten-step
zero-input recovery tail is an inspection horizon, not a fitted decay window
or physiological parameter. No state is interpolated, thresholded, reset, or
converted to spikes.

The shared reference set is named `phase7e_reference_assumptions_v1`:

| Parameter | Reference | Classification | Meaning here |
| --- | ---: | --- | --- |
| `tau_sens_ms` | 1.0 ms | `MODEL_ASSUMPTION` | decay/smoothing time of the dimensionless hidden state |
| `gain` | 1.0 | `MODEL_ASSUMPTION` | scale from the selected anatomical exposure fraction to the dimensionless state |
| initial state | 0 | `MODEL_ASSUMPTION` | deterministic initial condition |

The same values apply to all four bodies and both cell types. They were not
fitted to LC4/LPLC2 physiology, DNp01 events, or behavior and are not
physiological parameters. The DNp01 LIF parameters are not reused.

## Input metric

The reference input is `column_overlap_fraction`, the Phase 7D record-based
fraction in `[0,1]`: every source body/neuropil column record contributes
equally. This is the least committal available exposure fraction; it does not
promote anatomical site counts into a biological weighting.

The alternate `structural_input_site_overlap_fraction` is evaluated in a
separate sensitivity grid. It weights active records by exact MaleCNS assigned
input-site counts, so it remains a **structural/anatomical exposure** metric.
It is not efficacy, gain, conductance, sensitivity, or response probability.
The existing `unique_hex_overlap_fraction` is not selected as an input metric
in this version.

## Conditions and control interpretation

The four Phase 7D timelines are reused without changing their source artifact:

| Stimulus | Side | Relative-column schedule | Phase 7E use |
| --- | :-: | --- | --- |
| `left_expand_33_29` | L | center `(33,29)`, radii 1, 2, 3, 4 | expanding synthetic disk |
| `left_lplc2_11498_18_04` | L | center `(18,4)`, radius 2, one sample | fixed one-sample disk |
| `right_expand_23_09` | R | center `(23,9)`, radii 1, 2, 3, 4 | expanding synthetic disk |
| `right_translate_23_11` | R | center `(23,11)`, radius 2, one sample | translated-center disk |

The radius-1 and radius-4 values in each expanding timeline are also
small-/larger-disk **single assignment intervals**: Phase 7D holds each sample
for one `dt` interval. They are not separate sustained fixed-radius trials.
Phase 7E does not fabricate new exposure schedules or active-column sets.
The zero-exposure control uses the left expansion's stored sample count and
grid but supplies exactly zero model input for every body; it is explicitly a
numerical inactive-input control, not an additional optical stimulus.

Each unilateral timeline gives exact zero input to opposite-side bodies. There
is no mirroring or bilateral registration.

## Reproducible reference result

The generated artifact is
`09a3d3ddc02c81bb5ea229bf48b76811123ebd2e20cfce17f45e72442dcb8b15`, schema
`relative_column_sensory_state_artifact_v1`. It contains four conditions, ten
Phase 7D assignment samples, 216 reference state rows (including recovery),
and 60 zero-control state rows. The peak summaries below use the reference
column-overlap metric, `tau_sens_ms = 1.0`, `gain = 1.0`; state values are
dimensionless model outputs.

| Stimulus | Body | Peak exposure | Peak state | Peak state step / time |
| --- | ---: | ---: | ---: | --- |
| left expansion | LC4 12032 L | 0.626667 | 0.123840 | 4 / 0.4 ms |
| left expansion | LC4 16128 R | 0 | 0 | 0 / 0 ms |
| left expansion | LPLC2 11498 L | 0 | 0 | 0 / 0 ms |
| left expansion | LPLC2 14465 R | 0 | 0 | 0 / 0 ms |
| left LPLC2-centered disk | LC4 12032 L | 0 | 0 | 0 / 0 ms |
| left LPLC2-centered disk | LC4 16128 R | 0 | 0 | 0 / 0 ms |
| left LPLC2-centered disk | LPLC2 11498 L | 0.210526 | 0.020034 | 1 / 0.1 ms |
| left LPLC2-centered disk | LPLC2 14465 R | 0 | 0 | 0 / 0 ms |
| right expansion | LC4 12032 L | 0 | 0 | 0 / 0 ms |
| right expansion | LC4 16128 R | 0.651515 | 0.124895 | 4 / 0.4 ms |
| right expansion | LPLC2 11498 L | 0 | 0 | 0 / 0 ms |
| right expansion | LPLC2 14465 R | 0.533333 | 0.107181 | 4 / 0.4 ms |
| right translated center | LC4 12032 L | 0 | 0 | 0 / 0 ms |
| right translated center | LC4 16128 R | 0.287879 | 0.027395 | 1 / 0.1 ms |
| right translated center | LPLC2 11498 L | 0 | 0 | 0 / 0 ms |
| right translated center | LPLC2 14465 R | 0.352381 | 0.033533 | 1 / 0.1 ms |

Zero-exposure control remains exactly zero for all four bodies. The state at
recovery end is lower than the state at the end of assignment input; for
example, after the left expansion LC4 12032 is 0.045558 at 1.4 ms. These
differences are direct consequences of the model equation and source exposure,
not evidence of biological response.

## Sensitivity

The fixed 18-case deterministic grid crosses `tau_sens_ms = 0.5, 1.0, 2.0`
with `gain = 0.5, 1.0, 2.0` and both exposure metrics. It is a sensitivity
characterization, not an optimization. At gain 1, maximum state over the four
conditions/bodies for the record-based metric is approximately 0.221070,
0.124895, and 0.066606 for tau 0.5, 1.0, and 2.0 ms respectively. Over the
same condition/body set, the structural-site metric gives maxima 0.315564,
0.180572, and 0.096947. These extrema are descriptive and do not rank the
metrics as biologically preferable.

From the zero initial condition the equation is linear in gain, so halving or
doubling gain halves or doubles each trajectory. Increasing tau smooths the
short input sequence and lowers its observed peak here, while slowing decay:
after the one-millisecond recovery horizon, the retained fraction of a state
is `exp(-1/tau_sens_ms)` (about 0.1353, 0.3679, and 0.6065 for the three tau
values). These are mathematical sensitivity properties of the assumed model.

## Artifact, replay, and commands

The artifact is a separate immutable domain with config schema
`relative_column_sensory_state_config_v1` and result schema
`relative_column_sensory_state_result_v1`; Phase 7D assignment and existing
experiment artifacts are unchanged. Phase 7E config SHA-256 is
`ece7eccd1ee128ffdf0ec7c7262d4f8a9182ac237069590128683fcdcc767be7` and
result SHA-256 is
`91b785ec9de1509a40e14ad4096cc75282e75a8c80b46985a7bf61b54939a031`.
Canonical payload hashes determine the content identity. Generation refuses
to replace an existing artifact; replay replays Phase 7D, recomputes Phase 7E,
and requires exact config/result equality.

```bash
python -m neurofly.relative_column_sensory_cli generate
python -m neurofly.relative_column_sensory_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/relative_column_sensory_state_v1/<artifact-id>
python -m neurofly.relative_column_sensory_cli inspect \
  data/derived/malecns/looming_giant_fiber_v1/relative_column_sensory_state_v1/<artifact-id>
python -m neurofly.relative_column_sensory_cli sensitivity \
  data/derived/malecns/looming_giant_fiber_v1/relative_column_sensory_state_v1/<artifact-id>
```

Generated artifacts remain ignored under `data/derived/malecns/`; no API,
network lookup, frontend, or new dependency is used.

## Scientific boundary and next gate

**Source:** Phase 7D's MaleCNS body identity and persisted body-specific
anatomical exposure timelines.

**Derived:** the chosen exposure input row and deterministic dimensionless
state trajectory.

**Model assumption:** reference tau, gain, zero initial condition, and the
leaky transfer equation. The alternate structural-site input metric is a
separate anatomical/model-input assumption.

**Unknown:** absolute visual angle; functional receptive-field center/width;
per-body sensitivity or gain; membrane properties; voltage, firing, spikes,
or biological response transfer.

No LC4/LPLC2 activity is sent to DNp01. The known Phase 5I sensory-to-DNp01
structural edges remain unused and their weights do not enter the equation.
There is no threshold, spike, adaptation, behavior, muscle, or body output.
Phase 7E establishes four body-specific **exploratory model states** only; it
does not achieve the 311-sensory/313-neuron dynamics milestone and does not
empirically validate biological responses. A next phase may assess an explicit
four-body sensory-to-DNp01 model boundary, keeping structural counts separate
from any assumed efficacy.
