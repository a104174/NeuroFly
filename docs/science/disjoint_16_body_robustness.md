# Phase 7J — independent disjoint 16-body robustness experiment

Phase 7J reruns the bounded sensory pipeline on a second 16-body sample that
is disjoint from canonical Phase 7H Sample A. Its purpose is architecture,
coverage-planning, routing, and replay robustness. It is not biological
population validation and it does not compare neural outputs as though Sample
A and B were biological replicates.

## Pinned sources and Sample A

Sample A remains the immutable
`bounded_sensory_sample_artifact_v1`
`18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7`. Its
strata are LC4 L `[12032, 16809, 14888, 514956]`, LC4 R
`[16128, 38065, 21804, 19634]`, LPLC2 L `[11498, 40811, 29815, 515971]`, and
LPLC2 R `[14465, 37925, 21045, 22261]`. This is the complete Phase 7H/7I
canonical sample; the four original Phase 7F sentinel bodies are preserved
there and deliberately not forced into Sample B.

The run replays the MaleCNS `male-cns:v1.0` `looming_giant_fiber_v1` circuit,
the pinned `body_column_input_v1` topology, and the official v1.0 column
workbook before selecting or simulating Sample B. The body-column contract
identity is
`874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21`; its
`column_inputs.jsonl` and `column_body_summaries.jsonl` SHA-256 values are
`4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e` and
`ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b`. Circuit
`neurons.jsonl` / `connections.jsonl` hashes are
`00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e` /
`f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a`; the
column workbook SHA-256 is
`d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`.

## Outcome-blind Sample B selection

The immutable sample-selection contract is
`bounded_independent_sensory_sample_artifact_v1`, method
`rank_quartile_sample_a_excluded_centroid_maximin_v1`. Within each type × side
stratum it excludes all Sample A identities, sorts the remaining candidates
by source structural edge count then body ID, and partitions sorted ranks with
`min(3, floor(rank * 4 / candidate_count))`. It selects one body from each
quartile in order, maximizing minimum continuous hex-centroid distance to all
Sample A bodies in that stratum and previously selected Sample B bodies in the
same stratum; exact distance ties choose the smallest body ID. The per-stratum
candidate counts by quartile are LC4 L `17/17/17/16`, LC4 R `13/13/13/12`,
LPLC2 L `23/22/23/22`, and LPLC2 R `22/22/22/21`.

Structural counts only partition candidates and are retained as provenance.
The selection artifact is written before the coverage plan or any sensory or
DNp01 dynamics. No model state, transfer, DNp01 voltage, or spike value is an
input to selection. Centroids are unweighted anatomical summaries in the
MaleCNS relative hex grid; they are not visual angles or functional RF
centres.

| Type / side | Body ID → DNp01 | Structural count¹ | Column centroid `(hex1, hex2)` | Selected rank / quartile |
| --- | --- | ---: | ---: | ---: |
| LC4 L | 31308 → 10010 | 43 | (22.98, 24.44) | 15 / Q1 |
| LC4 L | 516909 → 10010 | 47 | (27.06, 20.66) | 21 / Q2 |
| LC4 L | 81112 → 10010 | 55 | (8.61, 4.03) | 39 / Q3 |
| LC4 L | 518439 → 10010 | 82 | (27.43, 35.72) | 64 / Q4 |
| LC4 R | 19954 → 10001 | 38 | (14.33, 13.61) | 9 / Q1 |
| LC4 R | 20808 → 10001 | 42 | (14.56, 22.20) | 14 / Q2 |
| LC4 R | 26112 → 10001 | 53 | (26.68, 33.91) | 38 / Q3 |
| LC4 R | 23929 → 10001 | 56 | (6.84, 20.42) | 41 / Q4 |
| LPLC2 L | 111903 → 10010 | 6 | (6.50, 7.38) | 4 / Q1 |
| LPLC2 L | 27399 → 10010 | 25 | (19.72, 21.94) | 37 / Q2 |
| LPLC2 L | 29702 → 10010 | 33 | (30.19, 35.19) | 53 / Q3 |
| LPLC2 L | 18936 → 10010 | 40 | (24.39, 13.56) | 69 / Q4 |
| LPLC2 R | 25316 → 10001 | 6 | (4.48, 8.84) | 11 / Q1 |
| LPLC2 R | 29598 → 10001 | 14 | (7.17, 20.80) | 25 / Q2 |
| LPLC2 R | 24268 → 10001 | 29 | (24.01, 35.14) | 52 / Q3 |
| LPLC2 R | 33185 → 10001 | 41 | (16.55, 25.73) | 72 / Q4 |

¹MaleCNS direct structural edge count, used as a sampling descriptor only—not
as efficacy, gain, or a transfer multiplier.

Sample B has 16 distinct identities, four in each of the four strata, zero
overlap with A, and no forced sentinels. Each selected body resolves to one
direct same-side DNp01 route in the committed CircuitContract. The target
mapping is read from that contract, not inferred from row position.

## Anatomy-only coverage plan

The existing Phase 7I ten-stimulus relative-column battery first covered 10/16
Sample B bodies. Its uncovered set was `31308`, `516909`, `81112`, `26112`,
`23929`, and `24268`. Planning used only these identities, their source-column
occupancy, side, and binary `column_overlap_fraction > 0` coverage. It
enumerated source columns as candidate disk centres and radii 1–4 on the
validated MaleCNS hex lattice, then minimized disk count, total radius, and
lexicographic radius/centre. No exposure magnitude beyond nonzero membership,
model outcome, or DNp01 output informed the plan.

Four radius-one source-column disks completed the cover:

| Added stimulus | Side | Centre `(olHex1, olHex2)` | Newly covered bodies |
| --- | :-: | ---: | --- |
| `coverage_b_l_03_05_r1` | L | (3, 5) | 81112 |
| `coverage_b_l_22_21_r1` | L | (22, 21) | 31308, 516909 |
| `coverage_b_r_03_14_r1` | R | (3, 14) | 23929 |
| `coverage_b_r_21_32_r1` | R | (21, 32) | 24268, 26112 |

The battery retains every Phase 7I stimulus unchanged: 14 stimulus identities,
26 assignment samples, four additional stimuli. Each added stimulus has its
own side and independent lattice centre; there is no mirroring or optical
registration. This is software-path coverage, not visual-field/RF coverage.

| Body | Type / side → target | Max exposure | Peak exploratory state | Peak `k*x` (mV-equivalent model drive) | First positive stimulus |
| ---: | --- | ---: | ---: | ---: | --- |
| 31308 | LC4 L → 10010 | 0.088889 | 0.008458896 | 0.008458896 | `coverage_b_l_22_21_r1` |
| 516909 | LC4 L → 10010 | 0.016129 | 0.001534880 | 0.001534880 | `coverage_b_l_22_21_r1` |
| 81112 | LC4 L → 10010 | 0.049180 | 0.004680127 | 0.004680127 | `coverage_b_l_03_05_r1` |
| 518439 | LC4 L → 10010 | 0.013889 | 0.001321703 | 0.001321703 | `left_expand_33_29` |
| 19954 | LC4 R → 10001 | 0.148148 | 0.018881864 | 0.018881864 | `sample_r_centroid_expand` |
| 20808 | LC4 R → 10001 | 0.218182 | 0.035971550 | 0.035971550 | `sample_r_centroid_expand` |
| 26112 | LC4 R → 10001 | 0.030303 | 0.002883715 | 0.002883715 | `coverage_b_r_21_32_r1` |
| 23929 | LC4 R → 10001 | 0.088889 | 0.008458896 | 0.008458896 | `coverage_b_r_03_14_r1` |
| 111903 | LPLC2 L → 10010 | 0.044248 | 0.004210734 | 0.004210734 | `coverage_b_l_03_10_r1` |
| 27399 | LPLC2 L → 10010 | 0.252632 | 0.041486968 | 0.041486968 | `sample_l_centroid_expand` |
| 29702 | LPLC2 L → 10010 | 0.060000 | 0.006570822 | 0.006570822 | `left_expand_33_29` |
| 18936 | LPLC2 L → 10010 | 0.009709 | 0.000923909 | 0.000923909 | `left_lplc2_11498_18_04` |
| 25316 | LPLC2 R → 10001 | 0.058824 | 0.005597799 | 0.005597799 | `coverage_b_r_01_07_r1` |
| 29598 | LPLC2 R → 10001 | 0.026667 | 0.002537669 | 0.002537669 | `coverage_b_r_12_27_r1` |
| 24268 | LPLC2 R → 10001 | 0.067961 | 0.006467360 | 0.006467360 | `coverage_b_r_21_32_r1` |
| 33185 | LPLC2 R → 10001 | 0.064516 | 0.008917156 | 0.008917156 | `sample_r_centroid_expand` |

All bodies pass `BODY_STIMULUS_COVERED`, `BODY_STATE_EXERCISED`, and
`BODY_TRANSFER_EXERCISED`: 16/16 for each. These labels describe deterministic
software/experiment coverage only. The Phase 7E state and Phase 7F transfer
equations and reference assumptions are unchanged: dimensionless
`relative_column_exploratory_sensory_state_v1`, `tau_sens_ms=1`, `gain=1`,
`x0=0`, `column_overlap_fraction`, and shared `k_transfer=1.0
mV_eq/state`. For each integer sample, Phase 7E uses its exact exponential
update `x[n+1] = exp(-dt/tau)*x[n] + gain*exposure[n]*(1-exp(-dt/tau))`;
Phase 7F applies `d_i[n]=k_transfer*x_i[n]` over the corresponding
`[n,n+1)` interval and sums routed contributions by DNp01 target. Structural
edge counts remain route metadata only. The existing DNp01 LIF configuration
is reused without parameter changes.

## A/B comparison and controls

| Measure | Sample A | Sample B |
| --- | ---: | ---: |
| Bodies / stratum | 16 / 4 | 16 / 4 |
| A–B overlap | — | 0 |
| Stimuli / assignment samples | 10 / 22 | 14 / 26 |
| Coverage-extension stimuli | 4 | 4 |
| Nonzero-path bodies | 16/16 | 16/16 |
| Experiment artifact bytes incl. manifest | 784,421 | 1,185,000 |
| Max drive to DNp01 10001 across battery | 0.232075434 mV-equivalent | 0.063770569 mV-equivalent |
| Max drive to DNp01 10010 across battery | 0.245630372 mV-equivalent | 0.041486968 mV-equivalent |
| Maximum modeled Vm, DNp01 10001 | −51.991499 mV | −51.997799 mV |
| Maximum modeled Vm, DNp01 10010 | −51.990985 mV | −51.998533 mV |
| Simulated model spikes | 0 | 0 |

The structural-count values and mean anatomical column centroids by stratum
were:

| Stratum | Sample A structural counts | Sample B structural counts | Sample A mean centroid | Sample B mean centroid |
| --- | --- | --- | --- | --- |
| LC4 L | 40, 55, 60, 62 | 43, 47, 55, 82 | (18.25, 21.26) | (21.52, 21.22) |
| LC4 R | 36, 48, 56, 65 | 38, 42, 53, 56 | (17.63, 18.69) | (15.61, 22.54) |
| LPLC2 L | 2, 17, 27, 45 | 6, 25, 33, 40 | (19.09, 20.75) | (20.20, 19.52) |
| LPLC2 R | 9, 21, 27, 37 | 6, 14, 29, 41 | (20.39, 21.84) | (13.05, 22.63) |

For a directly matched source-state comparison under the retained
`left_expand_33_29` / `right_expand_23_09` conditions, peak summed states by
side are A L `0.245630372`, R `0.232075434`; B L `0.007892524`, R `0`. The B
right-hand stimulus does not overlap its selected source columns. The
right-side Sample B path is nevertheless exercised by the added right-side
coverage stimuli, whose contributions route only to DNp01 10001. These
differences are consequences of sample anatomy and the synthetic stimulus
battery, not a biological response comparison.

The artifact includes `k=0`, no-source, LC4-only, LPLC2-only, left-only,
right-only, all-source, and `k={0.5,1,2}` sensitivity conditions. The zero and
no-source cases produce zero transfer and leave both DNp01 models at their
−52 mV baseline. All reference conditions remain subthreshold. At each
target/step the persisted per-source contributions sum to stored target drive
within `1e-15`; unilateral stimuli produce exactly zero exposure/state on the
opposite side. The sensitivity values characterize assumption-space
scaling only; no coefficient was fit or normalized to produce a desired
response.

## Immutable artifacts and replay

The three separately versioned artifacts are stored under ignored
`data/derived/malecns/looming_giant_fiber_v1/` paths:

| Artifact | Schema | Artifact ID | Config SHA-256 | Result SHA-256 | Bytes |
| --- | --- | --- | --- | --- | ---: |
| Sample B | `bounded_independent_sensory_sample_artifact_v1` | `873d6e9e32ce08916fb69462548af11f2cbadf394d91966641e6bc17839bcf33` | `71a4e2596da5d860ee7991d2e6e2e56d1f45dea5060ad4a917e51fc7970358f2` | `21bd57e761fd46d0a5a7deb18b958e75d40e0676a88d7bd5cfa262a9e1646119` | 16,512 |
| Coverage plan B | `bounded_independent_sensory_coverage_plan_artifact_v1` | `b718607e0cf671cc06454a6422ea7c3b48107516c59291b2fe01f9a244a9079f` | `b12545ec7f299e69de3a0765022c9ebc17a69b2fbd36160e7a19c345e0850605` | `96618bf75ebd9bcc471e5ee9909bf5bd5d6f43e963f74e752d6b9f254dcf40e8` | 22,312 |
| Population B | `bounded_independent_sensory_population_artifact_v1` | `f5fd68c1ea8b248f206af9be58fd9adeef604cd2e770289d8f32711ccbba6026` | `d65e0cfebac3ad5e73d173e9621c42de49d1c002caaa63e0c9dce83c10c26389` | `f597ee42df596b961c7b47191016937cd6dd8dae8a7d67b4746915cb4c6e02ea` | 1,185,000 |

Replay is content-addressed and validates Sample A, the pinned MaleCNS
contracts, Phase 7H and 7I, then Sample B, the anatomy-only coverage plan,
assignment, sensory states, structural routing, transfer, and DNp01 output.
The canonical Phase 7D–7I artifacts are read-only inputs; none is rewritten.
The artifact is generated and replayed offline with:

```bash
python -m neurofly.bounded_sensory_robustness_cli sample-generate
python -m neurofly.bounded_sensory_robustness_cli plan-generate <sample-b-artifact>
python -m neurofly.bounded_sensory_robustness_cli experiment-generate <sample-b-artifact> <plan-b-artifact>
python -m neurofly.bounded_sensory_robustness_cli experiment-replay <experiment-b-artifact> <sample-b-artifact> <plan-b-artifact>
```

There is no individual RF calibration, visual angle, per-body gain, neural
parameter change, or 32-/311-body run. Phase 7J establishes that the existing
bounded architecture generalizes to one independent, disjoint sample with
anatomy-derived coverage and deterministic replay. It does not validate
biological population dynamics or justify an immediate whole-circuit claim.

## Decision

`ROBUST_16_READY_FOR_32`: the disjoint 16-body architecture selected and
replayed deterministically, reached 16/16 nonzero software-path coverage,
preserved all fixed model assumptions, routed every body through its pinned
CircuitContract edge, and left the Phase 7D–7I artifacts unchanged. Output
amplitudes need not agree between samples and are not a selection or pass
criterion. The next bounded gate may be a Phase 7K 32-body architecture and
replay experiment using the same outcome-blind, anatomy-first principles; it
must not be interpreted as biological calibration or whole-circuit readiness.
