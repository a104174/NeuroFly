# Phase 7K — simultaneous 32-body composition and replay

Phase 7K composes the immutable Phase 7H Sample A and Phase 7J Sample B
artifacts into one simultaneous experiment. It selects no bodies and adds no
stimuli. The question is whether the shared Phase 7D–7F pipeline remains
compositional when both independently validated samples are active together.
This is an architecture and reproducibility test, not biological population
validation.

## Persisted union and exact battery

Sample A is `18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7`;
Sample B is `873d6e9e32ce08916fb69462548af11f2cbadf394d91966641e6bc17839bcf33`.
Their identity sets are disjoint. Sample C is their exact union: 32 bodies,
eight in each LC4/LPLC2 × left/right stratum, with 16 CircuitContract routes
to each DNp01 target. The composition method is
`DISJOINT_ARTIFACT_UNION`; its artifact is
`82ebef1acef2415fd57b9922e815e87e2d60fd76070a93e67103e2f3924198bf`
(`bounded_sensory_composed_sample_artifact_v1`). It records both parent
artifact IDs/hashes, all 32 identities, source provenance, route metadata,
disjointness, and the absence of outcome-based filtering.

The source identities remain the Phase 7J pins: MaleCNS `male-cns:v1.0`,
`looming_giant_fiber_v1`; `body_column_input_v1` contract
`874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21`; column
input/summary file hashes
`4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e` /
`ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b`; Circuit
Contract neuron/connection hashes
`00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e` /
`f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a`; and
the bilateral column workbook hash
`d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`.
Phase 7K downloads no new source files.

The experiment takes the exact 14-stimulus battery from the persisted Phase 7J
Sample B coverage plan:

`left_expand_33_29`, `left_lplc2_11498_18_04`, `right_expand_23_09`,
`right_translate_23_11`, `sample_l_centroid_expand`,
`sample_r_centroid_expand`, `coverage_l_03_10_r1`, `coverage_l_12_31_r1`,
`coverage_r_01_07_r1`, `coverage_r_12_27_r1`, `coverage_b_l_03_05_r1`,
`coverage_b_l_22_21_r1`, `coverage_b_r_03_14_r1`, and
`coverage_b_r_21_32_r1`.

The first operation on Sample C is an anatomy-only assignment/coverage audit.
It found all 32 bodies covered by positive `column_overlap_fraction` under
the existing battery; consequently no stimulus was added. Only after that
32/32 check does the experiment compute states and DNp01 readout.

## Reused model and accounting

The model versions and parameters are identical to Phase 7H/7J:

- Phase 7E: `relative_column_exploratory_sensory_state_v1`,
  `tau_sens_ms=1.0`, `gain=1.0`, `x0=0`,
  `column_overlap_fraction`, exact exponential update.
- Phase 7F: `d_i[n] = k_transfer * x_i[n]`, shared
  `k_transfer=1.0 mV_eq/state`, with no population normalization.
- Readout: the existing two-body DNp01 LIF configuration, unchanged.

Every per-source interval row stores source body/type/side, its exploratory
dimensionless state, transfer contribution, and CircuitContract target. At
every target and interval, source contributions sum to stored target drive
within the established `1e-15` tolerance. There are 16 routes to DNp01 10010 L
and 16 to DNp01 10001 R. Structural edge counts remain metadata only; they do
not enter exposure, sensory-state gain/tau, transfer coefficient, or target
drive.

The separate experiment artifact is
`b6be84a66d3cecde3e7bf05992515dc31521a8ebc5e8feebadf9b5f0560d9405`
(`bounded_sensory_population_32_artifact_v1`). It contains 26 assignment
samples, 32 trajectories for each of 14 stimulus identities, 25 conditions
(14 stimulus runs, eight pathway controls, and two non-reference k
sensitivities plus the shared-k reference), source contributions, DNp01
model output, coverage, nested-regression checks, and additive-drive checks.

## Coverage, nested equality, and simultaneous output

All three software coverage criteria passed for the exact union:

| Coverage criterion | Result |
| --- | ---: |
| `BODY_STIMULUS_COVERED` | 32/32 |
| `BODY_STATE_EXERCISED` | 32/32 |
| `BODY_TRANSFER_EXERCISED` | 32/32 |

These are experiment/software-path measures only, not functional receptive
field or biological response classifications. The 16 Sample A trajectories
matched their prior trajectories on all ten shared stimuli; the 16 Sample B
trajectories matched on all 14. Assignment rows and per-source transfer
contributions also matched on the corresponding body/stimulus/step subsets.
The A-only and B-only masks reproduced their canonical bilateral reference
target drives and DNp01 traces.

For the common ten-stimulus subset, per-step target drive equalled Sample A
drive plus Sample B drive (244 target/step checks). This was tested on the
input drive—not by assuming peak, voltage, or spike additivity. In the
bilateral reference condition at `k=1`, the union produced:

| DNp01 target | A peak drive | B peak drive | C peak drive | C max Vm | simulated spikes |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10001 R | 0.232075 mV-equivalent | 0 | 0.232075 mV-equivalent | −51.991499 mV | 0 |
| 10010 L | 0.245630 mV-equivalent | 0.007893 mV-equivalent | 0.253523 mV-equivalent | −51.990726 mV | 0 |

The union's peak LC4/LPLC2 model contributions at that same condition were
0.124895/0.107181 mV-equivalent for target 10001 and
0.125162/0.128361 mV-equivalent for target 10010. These are contributions of
the declared exploratory model only. They are not pathway efficacy estimates.

The full 14-stimulus C battery had maximum per-run target drives of 0.232075
and 0.253523 mV-equivalent at `k=1` for 10001 and 10010 respectively. The
separate `k=0.5` and `k=2` controls scale input linearly; the `k=0` and
no-source controls remain at zero input and the −52 mV baseline. The
reference and sensitivity runs produced no simulated DNp01 model spikes.
Spike occurrence was not a design or selection criterion.

## Scale, replay, and boundaries

Persisted artifact sizes including manifests were 31,374 bytes for the union,
4,269,739 bytes for the 32-body experiment, 784,421 bytes for Sample A's
Phase 7I experiment, and 1,185,000 bytes for Sample B's Phase 7J experiment.
The 32-body payload is 2.17× the combined A+B experiment payload: it stores
the simultaneous per-source state/contribution ledger in addition to the
trajectories. This remains a small offline artifact; record-level payload
growth is a scaling metric to review before a larger run, not a reason to
remove provenance. Full Phase 7K replay took about 40 seconds on the current
development environment and reproduced the artifact identity.

The offline commands are:

```bash
python -m neurofly.bounded_sensory_composition_cli composition-generate
python -m neurofly.bounded_sensory_composition_cli experiment-generate <sample-c-artifact>
python -m neurofly.bounded_sensory_composition_cli experiment-replay <sample-c-artifact> <experiment-artifact>
```

Generated artifacts live under ignored
`data/derived/malecns/looming_giant_fiber_v1/` paths. Canonical 7D–7J inputs
remain read-only and replayable. No angular/degree/radian input, type-level
angular drive, physiological RF, transfer calibration, population
normalization, API, or frontend behavior was introduced.

Phase 7K establishes that the exact disjoint A∪B identities can coexist as 32
individual exploratory states and route deterministically through the same
two existing DNp01 model neurons. It does not establish biological sensory
dynamics, physiological synaptic strength, complete 311/313-neuron execution,
or a calibrated looming circuit. TTMn/motor output remains out of scope.

## Decision

`SCALE_TO_64`: the 32-body composition, coverage, nested regressions, additive
per-step accounting, controls, and full replay all pass with unchanged model
assumptions. The 4.27 MB result and approximately 40-second replay are
manageable for this offline scope; artifact size and replay growth should be
measured again at 64. This recommendation concerns architecture only and does
not imply biological validation or readiness for whole-connectome simulation.
