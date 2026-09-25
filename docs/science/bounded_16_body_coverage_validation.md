# Phase 7I — coverage-complete 16-body stimulus battery

Phase 7I closes a software-path coverage gap in the canonical Phase 7H
16-body sample. It retains the sample and all six Phase 7H stimuli, adds a
small source-anatomy-derived relative-column battery, and replays the full
assignment → exploratory state → source-routed DNp01 model path. The result is
**software/experiment coverage**, not receptive-field or biological-response
coverage.

## Pinned inputs and initial coverage

The run uses the unchanged `bounded_sensory_sample_artifact_v1`
`18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7` and
Phase 7H `bounded_sensory_population_artifact_v1`
`385480b3c915b25536e1119d17effa15567bc0c1afcfe73037e5dd5d69102958` (result
SHA-256 `22cfba7705d0989d764934f80e13e73febe6c9904a76a8078b143699464dd792`).
Phase 7H full-source replay succeeded before stimulus design. Source identities
remain MaleCNS `male-cns:v1.0`, the pinned `looming_giant_fiber_v1`
`body_column_input_v1`, and the official v1.0 column grid. Phase 7I adds no
source records and does not modify either Phase 7H artifact.
The body-column contract identity is
`874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21`; source
file hashes are `column_inputs.jsonl`
`4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e` and
`column_body_summaries.jsonl`
`ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b`. The
CircuitContract pins `neurons.jsonl`
`00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e` and
`connections.jsonl`
`f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a`; the
column workbook SHA-256 is
`d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`.

`BODY_STIMULUS_COVERED` means `column_overlap_fraction > 0` for at least one
stored stimulus/sample. In the six-stimulus Phase 7H battery, 10/16 bodies had
positive exposure and 6/16 did not. Ten bodies also had positive 7H sensory
state. The persisted 7H all-source/reference-k DNp01 conditions delivered a
positive source contribution for 8/16 bodies. Two bodies (LC4 14888 and LPLC2
11498) had a positive state under a retained 7H stimulus, but that stimulus
was not among the 7H conditions sent through the 16-body transfer readout.
For clarity, the “trajectory-derived `k*x`” column below is the arithmetic
source contribution if the unchanged reference transfer is applied to each
stored state trace; “persisted 7H contribution” refers only to contributions
actually stored in 7H reference conditions.

| Body | Type/side → DNp01 | 7H max exposure | 7H peak state / trajectory `k*x` | 7H persisted reference contribution |
| ---: | --- | ---: | ---: | ---: |
| 12032 | LC4 L → 10010 | 0.626667 | 0.123839822 | 0.123839822 |
| 16809 | LC4 L → 10010 | 0 | 0 | 0 |
| 14888 | LC4 L → 10010 | 0.186441 | 0.017742176 | 0 |
| 514956 | LC4 L → 10010 | 0 | 0 | 0 |
| 16128 | LC4 R → 10001 | 0.651515 | 0.124894930 | 0.124894930 |
| 38065 | LC4 R → 10001 | 0 | 0 | 0 |
| 21804 | LC4 R → 10001 | 0 | 0 | 0 |
| 19634 | LC4 R → 10001 | 0.152778 | 0.021600476 | 0.021600476 |
| 11498 | LPLC2 L → 10010 | 0.210526 | 0.020034228 | 0 |
| 40811 | LPLC2 L → 10010 | 0 | 0 | 0 |
| 29815 | LPLC2 L → 10010 | 0.470588 | 0.082311592 | 0.082311592 |
| 515971 | LPLC2 L → 10010 | 0.581633 | 0.121790550 | 0.121790550 |
| 14465 | LPLC2 R → 10001 | 0.533333 | 0.107180504 | 0.107180504 |
| 37925 | LPLC2 R → 10001 | 0 | 0 | 0 |
| 21045 | LPLC2 R → 10001 | 0.025641 | 0.002440066 | 0.002440066 |
| 22261 | LPLC2 R → 10001 | 0.671756 | 0.133686566 | 0.133686566 |

The six zero-exposure bodies were `16809`, `514956`, `38065`, `21804`, `40811`,
and `37925`. These were identified from anatomy only. Phase 7H sensory-state
values, transfer contributions, DNp01 voltage, and spikes were not used to
design or select the extension battery.

## Anatomy-only battery construction

The plan considers only initially uncovered bodies’ actual source columns,
their side, and binary `column_overlap_fraction > 0`. It enumerates centers at
those source coordinates with integer radii 1–4 on the validated MaleCNS hex
lattice. It evaluates 464 left-side and 520 right-side candidate disks, reduces
them to four nonempty unique body-coverage masks per side, then uses exact
dynamic-programming set cover. Objective order is: fewest disks, lowest total
radius, then lexicographic `(radius, centre_hex1, centre_hex2)`. The maximum
search radius is bounded at four lattice steps. This yields the minimum
two-disk cover on each side; all selected disks use radius one and source
column centers:

| Stimulus | Side | Center `(olHex1, olHex2)` | Radius | Newly covered bodies |
| --- | :-: | ---: | ---: | --- |
| `coverage_l_03_10_r1` | L | (3,10) | 1 | LC4 16809 |
| `coverage_l_12_31_r1` | L | (12,31) | 1 | LC4 514956; LPLC2 40811 |
| `coverage_r_01_07_r1` | R | (1,7) | 1 | LC4 21804 |
| `coverage_r_12_27_r1` | R | (12,27) | 1 | LC4 38065; LPLC2 37925 |

The four additions are unilateral, independent relative-column stimuli; no
hemisphere is mirrored or aligned to an optical angle. Each has one exposure
sample at `dt_ms=0.1`, followed by the unchanged Phase 7E recovery tail. The
six original Phase 7H stimulus configurations remain byte-for-byte identical
and are replayed alongside the four additions, giving 10 stimulus identities
and 22 assignment samples total. Structural input-site counts are not used in
candidate scoring or as neural efficacy.

The plan is persisted before sensory-state and DNp01 computation as
`bounded_sensory_coverage_plan_artifact_v1`:

- artifact ID: `2b73f7c7707942be2644c5dfc0fcbed41be682c4877457ac86b6411619e8cd34`
- config SHA-256: `da636414772d95c835b6e6021f8573434f8de83087a0f05f02efdc91f05922f6`
- result SHA-256: `97e2fc29be4d07eea8d7fd6c22e4435f5b7bcc19a3299031beb65585e20d4034`
- config/result/manifest total: 14,401 bytes

## Per-body Phase 7I coverage

The unchanged model configuration is `tau_sens_ms=1.0`, `gain=1.0`, `x0=0`,
`column_overlap_fraction`, and shared `k_transfer=1.0 mV_eq/state`. All remain
model assumptions. Peak transfer contribution below is the maximum actual
per-source contribution in the Phase 7I all-source conditions.

| Body | Type/side → target | Phase 7I max exposure | Peak exploratory state | Peak transfer contribution | First/peak exercising stimulus |
| ---: | --- | ---: | ---: | ---: | --- |
| 12032 | LC4 L → 10010 | 0.626667 | 0.123839822 | 0.123839822 | `left_expand_33_29` |
| 16809 | LC4 L → 10010 | 0.072727 | 0.006920915 | 0.006920915 | `coverage_l_03_10_r1` |
| 14888 | LC4 L → 10010 | 0.186441 | 0.017742176 | 0.017742176 | `left_lplc2_11498_18_04` |
| 514956 | LC4 L → 10010 | 0.037037 | 0.003524540 | 0.003524540 | `coverage_l_12_31_r1` |
| 16128 | LC4 R → 10001 | 0.651515 | 0.124894930 | 0.124894930 | `right_expand_23_09` |
| 38065 | LC4 R → 10001 | 0.019608 | 0.001865933 | 0.001865933 | `coverage_r_12_27_r1` |
| 21804 | LC4 R → 10001 | 0.053571 | 0.005097995 | 0.005097995 | `coverage_r_01_07_r1` |
| 19634 | LC4 R → 10001 | 0.152778 | 0.021600476 | 0.021600476 | `sample_r_centroid_expand` |
| 11498 | LPLC2 L → 10010 | 0.210526 | 0.020034228 | 0.020034228 | `left_lplc2_11498_18_04` |
| 40811 | LPLC2 L → 10010 | 0.050847 | 0.004838775 | 0.004838775 | `coverage_l_12_31_r1` |
| 29815 | LPLC2 L → 10010 | 0.470588 | 0.082311592 | 0.082311592 | `sample_l_centroid_expand` |
| 515971 | LPLC2 L → 10010 | 0.581633 | 0.121790550 | 0.121790550 | `left_expand_33_29` |
| 14465 | LPLC2 R → 10001 | 0.533333 | 0.107180504 | 0.107180504 | `right_expand_23_09` |
| 37925 | LPLC2 R → 10001 | 0.080645 | 0.007674402 | 0.007674402 | `coverage_r_12_27_r1` |
| 21045 | LPLC2 R → 10001 | 0.025641 | 0.002440066 | 0.002440066 | `sample_r_centroid_expand` |
| 22261 | LPLC2 R → 10001 | 0.671756 | 0.133686566 | 0.133686566 | `sample_r_centroid_expand` |

All three coverage metrics pass 16/16. Each opposite-side body remains exactly
zero for a unilateral stimulus. At every interval, the eight source
contributions to each DNp01 target sum to its stored drive within the existing
`1e-15` absolute tolerance.

## DNp01 model readout and artifact

The 10 conditions independently run each retained/additional stimulus through
the existing DNp01 LIF readout using `x[n]` over interval `[n,n+1)`. The
maximum reference-condition drive is `0.245630372 mV_eq` to DNp01 10010 L and
`0.232075434 mV_eq` to DNp01 10001 R. Both membranes remain at or above the
existing −52 mV rest value and below threshold; no simulated model spikes
occur. Spike production was neither required nor a battery-selection target.

The immutable
`bounded_sensory_coverage_artifact_v1` is:

- artifact ID: `5d2953a0e20e471cdf26de0dae16ffff75b8cab159e3fbfcbb959a5349117e87`
- config SHA-256: `05da11921f4ae4006931069b6e12bef96242900e95bcb59b1e4e669f75b1f898`
- result SHA-256: `9d2d9f1e83e31507b18867fd4b87345ddd88e69b3c1f6d1091085614ff1e5aa6`
- payload plus manifest: 784,421 bytes

Full replay validates the pinned body-column/circuit sources, the unchanged
sample, Phase 7H assignment and sensory trajectories, then regenerates Phase
7I assignments, states, transfer contributions, and DNp01 output. The replayed
artifact ID is identical. Phase 7H’s stored artifact remains the canonical
`385480…02958`; Phase 7I does not rewrite it. The existing 7H replay path also
replays the pinned Phase 7D, 7E, and 7F dependencies. No external data were
downloaded.

Commands:

```bash
python -m neurofly.bounded_sensory_coverage_cli plan-generate
python -m neurofly.bounded_sensory_coverage_cli plan-replay <plan-artifact>
python -m neurofly.bounded_sensory_coverage_cli experiment-generate <plan-artifact>
python -m neurofly.bounded_sensory_coverage_cli experiment-replay <experiment-artifact> <plan-artifact>
python -m neurofly.bounded_sensory_coverage_cli coverage-summary <experiment-artifact>
```

Artifacts are stored below ignored `data/derived/malecns/` paths. The reference
state remains a dimensionless exploratory model state; exposure remains an
anatomical summary; transfer remains an assumption. Phase 7I establishes only
that the canonical 16 identities traverse the software path non-trivially.
There is no functional RF, biological response, calibrated visual angle,
biological DNp01 response, TTMn propagation, muscle model, or behavior claim.
