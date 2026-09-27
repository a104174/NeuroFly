# Phase 7L — four-sample simultaneous 64-body composition

Phase 7L composes the two persisted 16-body samples from Phases 7H/7J with two
new outcome-blind samples, then exercises the exact 64-body union. This is an
architecture, reproducibility, and offline performance gate—not biological
population validation.

## Immutable parents and outcome-blind selection

Sample A (`18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7`)
and Sample B (`873d6e9e32ce08916fb69462548af11f2cbadf394d91966641e6bc17839bcf33`)
were loaded from their persisted artifacts and replayed with the Phase 7K
composition/experiment before selecting C. Neither was reconstructed from its
selection algorithm. C was selected and persisted, then replayed, before D was
selected and persisted. No sensory-state, transfer, DNp01, or spike output was
available to either selection.

The rank-quartile/maximin algorithm is
`rank_quartile_centroid_maximin_prior_samples_v1`. Within each type×side
stratum it excludes every earlier sample, sorts remaining bodies by structural
DNp01 edge-count descriptor and body ID, assigns balanced quartile groups by
`floor(rank * 4 / candidate_count)`, then selects one candidate from each
group maximizing its minimum relative hex-centroid distance from all earlier
same-stratum bodies and already-selected bodies in the new sample. Exact ties
use the smallest body ID. Structural edge count is a rank-partition descriptor
only; it is not an efficacy estimate or a numerical model input.

Sample C (`bd10225993d0101d9a2338e7d18dac772fa4ab9096938de14930ea14df47c301`)
excludes A/B. Sample D
(`3609c165476f524b8187aed5400421cdd1ca1862fd5b3ab0e5cba2d90a95abe2`)
excludes A/B/C. Both have `model_outcomes_used=false`, four bodies in each
stratum, and `sentinel=false` for all selected bodies.

| Sample | Type | Side | Body ID | DNp01 target | Structural count descriptor | Anatomical column centroid | Rank group |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: |
| C | LC4 | L | 111787 | 10010 | 30 | (14.72, 21.81) | 1 |
| C | LC4 | L | 518730 | 10010 | 51 | (10.10, 13.08) | 2 |
| C | LC4 | L | 12824 | 10010 | 58 | (19.76, 14.41) | 3 |
| C | LC4 | L | 20859 | 10010 | 81 | (24.21, 12.60) | 4 |
| C | LC4 | R | 17987 | 10001 | 39 | (9.59, 3.89) | 1 |
| C | LC4 | R | 20673 | 10001 | 44 | (19.82, 26.46) | 2 |
| C | LC4 | R | 17266 | 10001 | 47 | (32.77, 30.96) | 3 |
| C | LC4 | R | 22966 | 10001 | 61 | (11.29, 27.51) | 4 |
| C | LPLC2 | L | 25136 | 10010 | 15 | (9.89, 25.30) | 1 |
| C | LPLC2 | L | 134521 | 10010 | 18 | (15.80, 15.41) | 2 |
| C | LPLC2 | L | 536444 | 10010 | 36 | (25.39, 28.13) | 3 |
| C | LPLC2 | L | 23349 | 10010 | 41 | (23.65, 20.17) | 4 |
| C | LPLC2 | R | 19249 | 10001 | 1 | (11.67, 3.93) | 1 |
| C | LPLC2 | R | 27471 | 10001 | 17 | (12.44, 12.44) | 2 |
| C | LPLC2 | R | 18672 | 10001 | 36 | (30.58, 20.31) | 3 |
| C | LPLC2 | R | 20471 | 10001 | 43 | (31.57, 34.29) | 4 |
| D | LC4 | L | 532254 | 10010 | 34 | (30.90, 34.29) | 1 |
| D | LC4 | L | 37587 | 10010 | 51 | (8.28, 22.28) | 2 |
| D | LC4 | L | 18478 | 10010 | 58 | (32.13, 24.04) | 3 |
| D | LC4 | L | 12349 | 10010 | 62 | (5.15, 7.10) | 4 |
| D | LC4 | R | 17548 | 10001 | 35 | (15.97, 8.15) | 1 |
| D | LC4 | R | 19794 | 10001 | 44 | (7.75, 6.88) | 2 |
| D | LC4 | R | 17364 | 10001 | 48 | (31.80, 23.44) | 3 |
| D | LC4 | R | 23392 | 10001 | 56 | (19.07, 19.59) | 4 |
| D | LPLC2 | L | 29319 | 10010 | 17 | (16.13, 23.92) | 1 |
| D | LPLC2 | L | 14102 | 10010 | 27 | (18.03, 11.87) | 2 |
| D | LPLC2 | L | 26528 | 10010 | 38 | (23.99, 32.90) | 3 |
| D | LPLC2 | L | 20240 | 10010 | 41 | (27.89, 19.23) | 4 |
| D | LPLC2 | R | 19549 | 10001 | 1 | (7.58, 6.14) | 1 |
| D | LPLC2 | R | 20334 | 10001 | 14 | (18.41, 13.55) | 2 |
| D | LPLC2 | R | 29287 | 10001 | 29 | (24.82, 29.82) | 3 |
| D | LPLC2 | R | 24401 | 10001 | 47 | (23.03, 21.23) | 4 |

All six pairwise sample intersections are empty. The 64-body composition
`db5df9b639f5ed834a4e2f408e39bec264552427260eadd8eb8789bcdf431436`
records the exact A/B/C/D artifact references, source identities, disjointness,
and all 64 source-derived routes. Its composition is 16 LC4-L, 16 LC4-R,
16 LPLC2-L, and 16 LPLC2-R. CircuitContract resolution gives 32 sources to
DNp01 10010 and 32 to DNp01 10001; no target was inferred from side alone.

## Coverage plan, fixed before dynamics

The starting stimulus battery is the unchanged 14-condition Phase 7K battery.
Anatomical overlap alone found 52/64 bodies covered and 12 uncovered. Before
any new sensory or DNp01 result was calculated, the existing deterministic
source-column set-cover planner selected five side-specific disks using binary
`column_overlap_fraction > 0`, bounded integer radii 1–4, and the objective
order: minimum added count, minimum total radius, then deterministic
lexicographic tie-break. All centres are actual MaleCNS source-column sites;
all radii were 1 except the final right-side disk at radius 3.

| Added stimulus | Side | Centre (hex indices) | Radius (lattice steps) | Newly covered sample bodies |
| --- | --- | --- | ---: | --- |
| `coverage64_l_05_16_r1` | L | (5, 16) | 1 | 37587 |
| `coverage64_l_18_28_r1` | L | (18, 28) | 1 | 26528 |
| `coverage64_l_19_11_r1` | L | (19, 11) | 1 | 12824, 20859 |
| `coverage64_r_02_05_r1` | R | (2, 5) | 1 | 17987, 19549, 19794 |
| `coverage64_r_30_27_r3` | R | (30, 27) | 3 | 17266, 17364, 18672, 20471, 29287 |

The resulting 19-stimulus plan is
`d92627cb1787b2b566e37d333064d259e5347aae6781b8381558dda233561536`.
The battery remains in `RELATIVE_COLUMN_SPACE`; it contains no absolute
optical coordinates or physical/angular looming values. Plan metadata records
`model_outcomes_used_for_battery_design=false` and
`neural_dynamics_computed=false`.

## Experiment and numerical invariants

The experiment reuses the committed models without alteration:

- Sensory state: `relative_column_exploratory_sensory_state_v1`,
  `tau_sens_ms=1.0`, `gain=1.0`, `x0=0`,
  `column_overlap_fraction`, exact exponential update on integer steps.
- Transfer: `d_i[n] = 1.0 * x_i[n]` under the shared
  `k_transfer=1.0 mV_eq/state` `MODEL_ASSUMPTION`.
- Readout: the same two existing DNp01 LIF neurons/configuration as Phase 7K.
- Population normalization: none.

All 64 direct routes were revalidated against the pinned CircuitContract.
Structural edge counts are retained as provenance only and do not enter the
exposure, state, transfer, or DNp01 drive equations. The experiment stores the
per-source state/contribution/target ledger and verifies its sum against each
target interval with absolute tolerance `1e-15`.

The 64-body experiment artifact is
`5095eddbf35c363cf4ae47ef875420ecad725eb0c837767ec8789e65bd68ab02`
(`bounded_sensory_population64_artifact_v1`). It contains 31 assignment
samples (1,984 body/sample assignment rows), 19 stimulus identities, 53
conditions, 1,304 target-step source-accounting comparisons, and 1,304
A/B/C/D per-step additivity comparisons. The 14 original stimulus conditions
are retained; no extra disk was added beyond the five listed above.

Coverage is complete as an experiment/software-path property:

| Measure | Result |
| --- | ---: |
| `BODY_STIMULUS_COVERED` | 64/64 |
| `BODY_STATE_EXERCISED` | 64/64 |
| `BODY_TRANSFER_EXERCISED` | 64/64 |

The A+B-only mask reproduces the Phase 7K per-source contributions and DNp01
drive/membrane/events for all 14 shared stimuli. The A-only and B-only
reference masks reproduce their canonical 16-body outputs. C and D sensory
trajectories also match their standalone recomputation. The zero-k and
no-source controls have zero drive and preserve the -52 mV baseline. LC4,
LPLC2, left/right, A/B/C/D, A+B, and C+D masks are present. The k sensitivity
values are exactly 0, 0.5, 1, and 2; no value was optimized. There were no
simulated DNp01 model spikes in the persisted experiment.

For the reference bilateral expansion condition, peak drive was
0.273738 mV-equivalent at 10001 and 0.388303 mV-equivalent at 10010; their
maximum modeled voltages were -51.990044 mV and -51.985840 mV. Across the
experiment’s sensitivity conditions, the largest drives were 0.547476 and
0.776606 mV-equivalent at k=2, with maxima -51.980087 mV and -51.971681 mV.
These are outputs of the exploratory transfer assumption and unchanged LIF
model, not biological response estimates.

## Artifact identities and replay

All newly generated artifacts remain ignored beneath
`data/derived/malecns/looming_giant_fiber_v1/`.

| Artifact | Schema | ID | Config SHA-256 | Result SHA-256 | Bytes incl. manifest |
| --- | --- | --- | --- | --- | ---: |
| Sample C | `bounded_sensory_scale64_sample_artifact_v1` | `bd10225993d0101d9a2338e7d18dac772fa4ab9096938de14930ea14df47c301` | `abcd185bf0159f5bca83513ca3a87f1fcf1a3708cb3d888726357d6debd8c410` | `1ff2635a26e2bae66b92786a37b49371dbfa2f2eedd2e822dadf0532591114bc` | 21,527 |
| Sample D | `bounded_sensory_scale64_sample_artifact_v1` | `3609c165476f524b8187aed5400421cdd1ca1862fd5b3ab0e5cba2d90a95abe2` | `61d1b2a0a9cba8b7cef84909b3e9e3870bf63593536016041b9efc74d4012d0a` | `49a1be3afd8df235424fc78cfed0d231d82147ceefacaf592cc445fb054b29f8` | 23,170 |
| A/B/C/D union | `bounded_sensory_composition64_artifact_v1` | `db5df9b639f5ed834a4e2f408e39bec264552427260eadd8eb8789bcdf431436` | `ec4e0129b2634ef95d8a526eaa080f6ca30c11bb6d52c1b7d3d83059cceed8ae` | `2abff2281113ef50bd86088174822b4a9498224a1eeb5cf24c0e81efc81096a2` | 55,950 |
| Coverage plan | `bounded_sensory_coverage64_plan_artifact_v1` | `d92627cb1787b2b566e37d333064d259e5347aae6781b8381558dda233561536` | `09c39afd41bcf37920d8041e91283ec33216cf49872369b1ac7d6c07c7cb861c` | `ae498b777d8818409b4da5940fe519bc984623c1e30e27b47bbdc09bdb1c6ec1` | 50,330 |
| 64-body experiment | `bounded_sensory_population64_artifact_v1` | `5095eddbf35c363cf4ae47ef875420ecad725eb0c837767ec8789e65bd68ab02` | `8e58797693296e7c097d31d6e4e32088cd242bc5f112fc225e45816e706b2fbc` | `0040f79be38dc533d073ff13a46da96864e0d90753b598acd6f7f3b2038e8c60` | 14,848,847 |

The canonical source identities are those already pinned by Phase 7K:
MaleCNS `male-cns:v1.0` / `looming_giant_fiber_v1`; `body_column_input_v1`
contract SHA-256
`874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21`;
column-input/summary SHA-256 values
`4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e` /
`ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b`; and
CircuitContract neuron/connection hashes
`00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e` /
`f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a`.

Full experiment replay rechecks the pinned sources, A/B and Phase 7K parents,
C/D selections, composition, anatomy-only plan, states, transfer, and DNp01
output. Replay returned the same experiment ID and config/result hashes. The
current full replay took 24.634 s; full generation took 24.492 s, including
approximately 20.939 s of canonical-parent replay. C/D selection/persist took
0.019/0.017 s and their deterministic replays took 0.013/0.014 s. The
coverage-plan generate/replay commands took 21.924/22.098 s wall time,
including canonical-parent replay; the anatomy-only planner itself is a small
fraction of that time. Phases 7D–7K remain unchanged and replayable.

The offline workflow is:

```bash
python -m neurofly.bounded_sensory_scale64_cli samples-generate
python -m neurofly.bounded_sensory_scale64_cli composition-generate <sample-c> <sample-d>
python -m neurofly.bounded_sensory_scale64_cli coverage-plan-generate <composition> <sample-c> <sample-d>
python -m neurofly.bounded_sensory_scale64_cli experiment-generate <composition> <coverage-plan> <sample-c> <sample-d>
python -m neurofly.bounded_sensory_scale64_cli experiment-replay <composition> <coverage-plan> <sample-c> <sample-d> <experiment>
```

## Scaling and performance interpretation

The artifact sizes below are from the committed Phase 7I/J/K records, plus the
Phase 7L artifact measured in this run. Replay durations were remeasured with
the corresponding full-replay CLIs in the current environment; these are
wall-clock characterizations, not a controlled benchmark. The Phase 7J–7L
replay paths validate progressively broader parent chains.

| Sensory bodies | Experiment artifact bytes | Full replay duration | Notes |
| ---: | ---: | ---: | --- |
| 16 (Sample A, 7I) | 784,421 | 6.583 s | 10-stimulus covered Sample A pipeline |
| 16 (Sample B, 7J) | 1,185,000 | 20.734 s | Independent 14-stimulus sample; replays A/7H/7I parents |
| 32 (7K) | 4,269,739 | 19.575 s | 14 stimuli; simultaneous ledger and A+B regression |
| 64 (7L) | 14,848,847 | 24.634 s | 19 stimuli; 53 conditions and nested checks |

The 32→64 experiment artifact grew 3.48× for a 2× population increase, so
payload growth is super-linear in this small comparison. The experiment now
stores 53 conditions, including per-stimulus full-population and A+B nested
ledgers; this is a likely structural reason, not a measured general law.
Replay grew only 1.26× from 32 to 64 on this run, and the 14.85 MB artifact,
31 assignment samples, and approximately 25-second full replay remain
manageable for an offline research gate. No material runtime bottleneck,
memory pressure, or need for performance technology was observed. The next
doubling to 128 would provide a useful second simultaneous-population scaling
point before implementation preparation for all 311 bodies; it must remain a
separate architecture experiment and cannot be interpreted biologically.

## Scientific boundary and decision

MaleCNS provides source body identities, relative column topology, and
structural route metadata. Column overlap is derived anatomical exposure.
Relative-column stimulus shape, the dimensionless sensory state, and the
shared transfer coefficient are explicit model assumptions. DNp01 voltage
and any spikes are NeuroFly model outputs. Structural count is not efficacy;
exposure is not a functional receptive field; no absolute visual angle,
physiological gain, or calibrated population response is available. `64/64`
is software-path coverage only.

**Decision: `SCALE_TO_128`.** The exact four-sample composition, complete
coverage, nested regressions, per-step contribution accounting/additivity,
source replay, and manageable replay/runtime pass. Artifact growth is
super-linear and should be monitored at 128, but it does not yet justify a
storage redesign or a hold at 64. Phase 7L does not run 128 and does not claim
311 sensory dynamics or a completed 313-neuron circuit.
