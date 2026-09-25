# Phase 7H — deterministic 16-body sensory architecture experiment

Phase 7H generalizes the existing bounded 4-body pipeline to an outcome-blind,
preselected sample of exactly 16 sensory bodies. It demonstrates reproducible
identity, anatomical assignment, exploratory state, structural routing, and
DNp01-model integration. It is an **architecture/reproducibility experiment**,
not a biological or physiological validation.

The earlier Phase 7D/7E/7F four-body schemas remain four-body contracts. Phase
7H uses separately versioned `bounded_sensory_sample_artifact_v1` and
`bounded_sensory_population_artifact_v1` artifacts; it neither widens nor
rewrites the old artifacts.

## Pinned source and outcome-independent selection

The source is MaleCNS `male-cns:v1.0`, candidate
`looming_giant_fiber_v1`, the existing `body_column_input_v1`, and its pinned
official column workbook. Source identities/hashes are:

| Source | Identity | SHA-256 |
| --- | --- | --- |
| Body-column `column_inputs.jsonl` | `body_column_input_v1` | `4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e` |
| Body-column `column_body_summaries.jsonl` | `body_column_input_v1` | `ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b` |
| CircuitContract `neurons.jsonl` | `male-cns:v1.0` | `00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e` |
| CircuitContract `connections.jsonl` | `male-cns:v1.0` | `f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a` |
| Phase 7D official column workbook | flyconnectome/2025malecns pinned v1.0 source | `d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3` |

The body-column contract identity is
`874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21`. The
loader validates source dataset/version, body/type/side identities, source
hashes, and the one-direct-DNp01-edge-per-sensory-body property before sample
selection.

There are four fixed strata: LC4-L, LC4-R, LPLC2-L, and LPLC2-R. Each retains
its Phase 7F sentinel. Three additional bodies per stratum are chosen without
reading Phase 7E/7F outcomes:

1. Exclude the sentinel; sort candidates by `(structural_weight, body_id)`.
2. Assign zero-based candidate rank `r` to one of three balanced rank bands
   with `min(2, floor(3*r/N))`. Thus ties/discrete counts do not create empty
   numeric-threshold bands; body ID deterministically orders tied counts.
3. In low, middle, then high band order, choose the body maximizing minimum
   continuous hex-lattice centroid distance from the sentinel and bodies
   already selected in that stratum. Exact distance ties use the smallest body
   ID.

The centroid is the unweighted mean of source body-column records in relative
hex coordinates. It is an anatomical sampling descriptor, not an RF centre.
Structural edge count is only a descriptive selection stratum and remains
source metadata; it is never a physiological weight.

| Body | Type/side | DNp01 target | Structural count | Record centroid `(hex1,hex2)` | Band / zero-based rank | Sentinel |
| ---: | --- | ---: | ---: | ---: | --- | :---: |
| 12032 | LC4 L | 10010 L | 62 | (32.89, 31.24) | sentinel | yes |
| 16809 | LC4 L | 10010 L | 40 | (6.27, 15.82) | low / 11 | no |
| 14888 | LC4 L | 10010 L | 55 | (17.14, 6.97) | middle / 39 | no |
| 514956 | LC4 L | 10010 L | 60 | (16.69, 31.00) | high / 51 | no |
| 16128 | LC4 R | 10001 R | 65 | (22.18, 10.23) | sentinel | yes |
| 38065 | LC4 R | 10001 R | 36 | (17.76, 31.98) | low / 7 | no |
| 21804 | LC4 R | 10001 R | 48 | (4.52, 8.57) | middle / 33 | no |
| 19634 | LC4 R | 10001 R | 56 | (26.06, 23.97) | high / 42 | no |
| 11498 | LPLC2 L | 10010 L | 2 | (15.22, 6.74) | sentinel | yes |
| 40811 | LPLC2 L | 10010 L | 17 | (18.56, 33.49) | low / 23 | no |
| 29815 | LPLC2 L | 10010 L | 27 | (10.38, 17.18) | middle / 42 | no |
| 515971 | LPLC2 L | 10010 L | 45 | (32.19, 25.60) | high / 82 | no |
| 14465 | LPLC2 R | 10001 R | 21 | (23.31, 12.16) | sentinel | yes |
| 37925 | LPLC2 R | 10001 R | 9 | (13.10, 29.74) | low / 16 | no |
| 21045 | LPLC2 R | 10001 R | 27 | (27.55, 26.96) | middle / 51 | no |
| 22261 | LPLC2 R | 10001 R | 37 | (17.59, 18.51) | high / 69 | no |

The sample artifact is created and replay-validated before the experiment
runner reads model outcomes. Its configuration records the exact bodies,
targets, counts, centroids, band/rank, selection method, sentinel flag, and
pinned contract identities. Replay recomputes selection from those sources and
requires canonical equality.

## Stimuli and assignment

The assignment reuses Phase 7D's exact `column_overlap_fraction` semantics on
the MaleCNS hex lattice. Left and right are independent; no mirroring,
cross-eye registration, or absolute visual angle is introduced. The original
four Phase 7D sentinel stimuli are unchanged. Two additional bilateral
coverage stimuli are predeclared from the selected bodies' side-wise mean
anatomical centroids: choose the nearest occupied column in hex distance, with
lexicographic coordinate tie-break, then use radii 1–4.

| Stimulus | Side | Center | Radius schedule | Purpose |
| --- | :-: | ---: | --- | --- |
| `left_expand_33_29` | L | (33,29) | 1, 2, 3, 4 | original sentinel expansion |
| `left_lplc2_11498_18_04` | L | (18,4) | 2 | original sentinel disk |
| `right_expand_23_09` | R | (23,9) | 1, 2, 3, 4 | original sentinel expansion |
| `right_translate_23_11` | R | (23,11) | 2 | original translated disk |
| `sample_l_centroid_expand` | L | (14,19) | 1, 2, 3, 4 | sample anatomy coverage |
| `sample_r_centroid_expand` | R | (19,20) | 1, 2, 3, 4 | sample anatomy coverage |

All use `dt_ms=0.1`, integer steps, and `relative_column_expanding_disk_v1`.
The resulting 18 stored assignment samples contain all 16 identities at every
sample. The only output is anatomical exposure; it is not visual sensitivity,
functional RF, or neural response.
All 16 selected bodies have nonempty pinned column distributions. Their source
assigned-site coverage fractions range from `0.980313` to `1.0`; the exact
assigned, relevant, and unassigned source-site counts remain attached to each
selected identity. The 18 samples therefore contain 288 body/sample assignment
rows, with the opposite-side bodies receiving exact zero anatomical exposure
for every unilateral stimulus.

The nonzero body/stimulus peaks in the reference `column_overlap_fraction`
run are below; omitted body/stimulus pairs have exactly zero exposure and
zero state. Peak state time is an integer boundary on the `0.1 ms` grid.

| Stimulus | Body | Peak anatomical exposure | Peak exploratory state | Peak state step / time |
| --- | --- | ---: | ---: | --- |
| left expansion | LC4 12032 L | 0.626667 | 0.123839822 | 4 / 0.4 ms |
| left expansion | LPLC2 515971 L | 0.581633 | 0.121790550 | 4 / 0.4 ms |
| left LPLC2-centred disk | LC4 14888 L | 0.186441 | 0.017742176 | 1 / 0.1 ms |
| left LPLC2-centred disk | LPLC2 11498 L | 0.210526 | 0.020034228 | 1 / 0.1 ms |
| right expansion | LC4 16128 R | 0.651515 | 0.124894930 | 4 / 0.4 ms |
| right expansion | LPLC2 14465 R | 0.533333 | 0.107180504 | 4 / 0.4 ms |
| right translated disk | LC4 16128 R | 0.287879 | 0.027395289 | 1 / 0.1 ms |
| right translated disk | LPLC2 14465 R | 0.352381 | 0.033533481 | 1 / 0.1 ms |
| left sample-centred expansion | LPLC2 29815 L | 0.470588 | 0.082311592 | 4 / 0.4 ms |
| right sample-centred expansion | LC4 19634 R | 0.152778 | 0.021600476 | 4 / 0.4 ms |
| right sample-centred expansion | LPLC2 21045 R | 0.025641 | 0.002440066 | 4 / 0.4 ms |
| right sample-centred expansion | LPLC2 22261 R | 0.671756 | 0.133686566 | 4 / 0.4 ms |

## Exploratory state, routing, and DNp01 model

The unchanged Phase 7E reference input is `column_overlap_fraction` and the
unchanged exact zero-order-hold update is

```text
alpha = exp(-dt_ms / tau_sens_ms)
x[n+1] = alpha*x[n] + gain*exposure[n]*(1-alpha)
```

with shared `tau_sens_ms=1.0 ms`, `gain=1.0`, `x[0]=0`, and the original
recovery-tail rule. `x` is a dimensionless exploratory model state. Both
parameters and the state transfer have `MODEL_ASSUMPTION` semantics; there are
no per-body/type parameters, thresholds, spikes, or membrane-voltage claims.
The alternate structural-input-site exposure is not used as the reference
input and is not promoted to efficacy.

All 16 targets are resolved from the pinned `CircuitContract`, with exactly
one same-side direct DNp01 edge per selected body. The transfer and existing
DNp01 readout are unchanged from Phase 7F:

```text
d_i[n] = 1.0 mV_eq/state * x_i[n]
D_target[n] = sum(d_i[n] for selected, unmasked sources routed to target)
```

The shared `k_transfer=1.0 mV_eq/state` remains an unidentifiable
`MODEL_ASSUMPTION`. Structural counts do not enter exposure, `x`, transfer,
LIF parameters, or target summation. There is no normalization for sample
size. The existing two-body DNp01 LIF readout is unchanged; angular stimulus
and type-level LC4/LPLC2 drives are absent. No TTMn/muscle/body output follows.

## Result and scale comparison

The fixed reference run is `all16_reference`, with the left and right original
expanding-disk inputs as independent relative-column conditions. The two
sample-centroid stimuli provide the second paired comparison. Phase 7E
trajectories for each sentinel match the old four-body artifact exactly on
all four original stimuli (16 body/stimulus comparisons); the sentinel-only
DNp01 drive, membrane, filtered-state, and event outputs also match the old
Phase 7F reference exactly.

| Comparison / target | Sensory states | Peak source-state sum (side) | Peak drive (`mV_eq`) | DNp01 Vm range (mV) | Model spikes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original stimuli, 4 sentinels → 10001 R | 4 total; 2 R | 0.232075 (R) | 0.232075 | −52 to −51.991499 | 0 |
| Original stimuli, 4 sentinels → 10010 L | 4 total; 2 L | 0.123840 (L) | 0.123840 | −52 to −51.995474 | 0 |
| Original stimuli, 16 bodies → 10001 R | 16 total; 8 R | 0.232075 (R) | 0.232075 | −52 to −51.991499 | 0 |
| Original stimuli, 16 bodies → 10010 L | 16 total; 8 L | 0.245630 (L) | 0.245630 | −52 to −51.990985 | 0 |
| Sample-centred stimuli, sentinels → 10001 R | 4 total; 2 R | 0 | 0 | −52 to −52 | 0 |
| Sample-centred stimuli, sentinels → 10010 L | 4 total; 2 L | 0 | 0 | −52 to −52 | 0 |
| Sample-centred stimuli, 16 bodies → 10001 R | 16 total; 8 R | 0.157727 (R) | 0.157727 | −52 to −51.994291 | 0 |
| Sample-centred stimuli, 16 bodies → 10010 L | 16 total; 8 L | 0.082312 (L) | 0.082312 | −52 to −51.997039 | 0 |

For the original stimulus, the added selected left LC4 body 515971 contributes
to the left target while the other newly selected bodies have zero exposure
under that particular disk. The left source-state sum/target drive therefore
increases from 0.123840 to 0.245630; the right sum remains exactly 0.232075
because the additional right bodies have zero exposure under that disk. This
is the unnormalized arithmetic consequence of the selected sample and
stimulus, not evidence that the larger sample is more biologically realistic.

All source contributions are persisted at each interval. Their sum equals
each target drive within `1e-15` absolute tolerance. Descriptive LC4/LPLC2
contributions are separately stored; their ratio is not a biological pathway
weight. Left-only drives only DNp01 10010; right-only drives only DNp01
10001. LC4-only and LPLC2-only controls each retain four selected bodies per
side. `k=0` and `no_sources` produce exactly zero transfer and keep both model
readouts at −52 mV. `sentinels_only` reproduces Phase 7F. No condition produced
a simulated DNp01 model spike.

The bounded sensitivity values are `k=0, 0.5, 1, 2 mV_eq/state`; there is no
optimization. On the reference input, k=0.5 halves and k=2 doubles each
source/target drive. Peak drives are 0.116038 / 0.232075 / 0.464151 for
DNp01 R and 0.122815 / 0.245630 / 0.491261 for DNp01 L at k=0.5 / 1 / 2.
Neither trajectory spikes in this tested range. The range characterizes scale
interaction and numerical behavior only; it is not an efficacy prior.

## Artifact identity, replay, and commands

The persisted sample is
`18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7`
(`bounded_sensory_sample_artifact_v1`), config SHA-256
`7c5dcce20e96730b095d4b26a63378eaa3a27c3418f2d0139d3028e64c3f8f09`, result
SHA-256 `82fac8eb54f83b6d1e475cf744614ab7d080677886f43748d0384810f2ba4f0c`
(12,150 bytes including manifest).

The full experiment is
`385480b3c915b25536e1119d17effa15567bc0c1afcfe73037e5dd5d69102958`
(`bounded_sensory_population_artifact_v1`), config SHA-256
`0dd87150b462cba1c9f4d170c6f640952bc22e9d8b07d5241488f5fa3b813890`, result
SHA-256 `22cfba7705d0989d764934f80e13e73febe6c9904a76a8078b143699464dd792`
(659,326 bytes including manifest). Its config links the sample artifact,
source hashes, stimulus identities/hashes, unchanged 7E/7F model assumptions,
route contract, controls, and reference artifact identities. Full replay
recomputes the sample and assignment, replays canonical 7D/7E/7F artifacts,
then regenerates sensory states, source contributions, and DNp01 outputs.
The CLI reports `full-source-pipeline-replay-verified` for the current
artifact.

```bash
python -m neurofly.bounded_sensory_population_cli sample-generate
python -m neurofly.bounded_sensory_population_cli sample-replay <sample-artifact>
python -m neurofly.bounded_sensory_population_cli experiment-generate <sample-artifact>
python -m neurofly.bounded_sensory_population_cli experiment-replay <sample-artifact> <experiment-artifact>
python -m neurofly.bounded_sensory_population_cli experiment-inspect <experiment-artifact>
```

Generated artifacts remain ignored under
`data/derived/malecns/looming_giant_fiber_v1/`. No source data or generated
payload is tracked. An earlier superseded content-addressed exploratory
population artifact also remains in that ignored directory; the sample and
experiment IDs above are the reviewed canonical pair.

## Boundary and scale decision

MaleCNS provides body/type/side, column topology, and direct chemical
structural route/count evidence. Phase 7H derives relative-column anatomical
exposure and applies the unchanged exploratory 7E state equation. A shared
positive transfer into the unchanged DNp01 LIF model remains the 7F modeling
assumption. Absolute optical rays, functional receptive fields, neural
parameters, unitary synaptic efficacy, and biological validation remain
unknown. No motor pathway, behavior, or body mechanics is included.

The deterministic sample and replay pass at 16 bodies, but the 16-body sample
is still outcome- and selection-algorithm-specific and its total drive
depends on which anatomically exposed bodies are included. The scale decision
is **HOLD_AT_16**: do not run 32/311 yet. A next bounded phase should assess
sample/stimulus robustness or the evidence needed for the sensory transfer
before increasing population size; it must not tune `k` to produce spikes.
