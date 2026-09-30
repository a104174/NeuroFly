# Phase 9E — model-space G1-proxy peak deflection

This phase implements one deterministic observation extractor, not physiological
validation. It observes persisted Phase 9B samples; it does not integrate the
electrical model. The production entry point first replays the canonical source
artifact with Phase 9B's existing validation machinery. That replay reconstructs
the model solely to validate the persisted source. Extraction then reads samples.

## Source and scientific boundary

Source schema: `g1_proxy_passive_electrical_response_artifact_v1`.
Source ID:
`72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f`.
The source remains unchanged, as do Phase 9C and Phase 8W/8Y/8U.

All voltage quantities retain `mV_eq`: uncalibrated model-space voltage-equivalent
coordinates, **not biological mV**. No empirical observation value enters an
extraction calculation. There is no scale/offset conversion, empirical target,
error, acceptance band, fitting, or numerical comparison. Protocol match status
is `NOT_EVALUATED`. These are synthetic model-behavior fixtures, not published
stimulation protocols. G1 remains a virtual observation-domain proxy, not an
anatomically traced fiber or whole-TTM response. Equal left/right model outputs
under a shared config are not bilateral physiological evidence.

## Operator semantics

Schema: `g1_proxy_model_space_peak_deflection_operator_v1`.
Operator ID:
`7a9cbf8f4341382757a118f3485780a1f49c6f810a5151f35112eb60286b1e19`.

For exactly one input token at boundary `n > 0`:

- Baseline: source proxy voltage at `n - 1`, labelled
  `IMMEDIATE_PRE_EVENT_BOUNDARY_BASELINE`, not experimental resting potential.
- Window: `EVENT_BOUNDARY_THROUGH_TRAJECTORY_END_INCLUSIVE`.
- Peak: maximum stored proxy voltage in that window, with the earliest stored
  boundary chosen for ties. No absolute-value peak or interpolation.
- Deflection: peak minus the pre-event baseline, required finite and positive.

The window is deliberately model-space-only. It introduces no guessed experimental
recording duration. For the isolated positive passive response, the peak is at
the event boundary. Boundary-zero events are rejected because there is no stored
pre-event baseline. Two or more tokens are unsupported.

Zero-input trajectories produce `NO_EVENT_BASELINE_CONTROL`, never an evoked
observation with deflection zero. The initial/reference coordinate is the control
baseline. The extractor checks every sample for equality and reports
`baseline_stable` plus maximum absolute deviation. Controls contain no source
event ID or peak-deflection field. An unstable local control would report false;
canonical Phase 9B replay prevents publishing an inconsistent model trajectory.

The other result kind is `ISOLATED_EVENT_PEAK_DEFLECTION`. Both retain source
artifact, fixture, trajectory ID/hash, body/side, proxy-domain ID, operator ID,
units and scientific boundaries. Only event results retain the Phase 8W token
ID and baseline/event/window/peak steps and times. Result IDs hash their full
semantic payload. Provenance is `EXPLORATORY_MODEL_SPACE_OBSERVATION`, downstream
of `EXPLORATORY_G1_PROXY_ELECTRICAL_MODEL`; it is not empirical provenance.

## Canonical accounting

| Fixture | 800146/R | 804642/L |
| --- | --- | --- |
| ZERO_EVENT_CONTROL | Baseline control | Baseline control |
| RIGHT_SINGLE_EVENT | Isolated peak | Baseline control |
| LEFT_SINGLE_EVENT | Baseline control | Isolated peak |
| BILATERAL_SIMULTANEOUS_EVENT | Isolated peak | Isolated peak |

Exactly eight records: four isolated peaks and four stable controls. Each peak
has baseline 0 mV_eq at step 9 / 0.9 ms, event and peak at step 10 / 1.0 ms,
absolute peak and deflection 2 mV_eq, and window steps 10–80 / 1.0–8.0 ms.
Each control has baseline 0 mV_eq and maximum absolute deviation 0 mV_eq.
These are equation/operator regression facts, not empirical agreement.

`RIGHT_REPEATED_EVENTS` and `LEFT_REPEATED_EVENTS` are explicitly excluded in
their entirety, including their inactive trajectories. The v1 operator does not
choose a target event, residual baseline, second peak or depression metric.
Canonical ordering is source fixture order then source body order.

## Artifact and offline replay

Artifact schema: `g1_proxy_model_space_peak_deflection_artifact_v1`.
Artifact ID:
`2c775d6e00d74b3b3a3ca5a36bb84fd4032959d29f3c7d4c8b0bca934e2942b8`.
Config hash:
`44be1b554dafc1c867f92ff1c50100157aa0787ea04cf2480e390cc7f0a778ca`.
Result hash:
`766b98a29bd6343f3ba633cfa5a9de900f697ff93be8ac89da3f083e1325dba9`.
The two-file artifact is 18,564 bytes under the existing ignored
`data/derived/malecns/looming_giant_fiber_v1/` schema directory.

```sh
python -m neurofly.g1_proxy_peak_deflection_cli generate
python -m neurofly.g1_proxy_peak_deflection_cli inspect ARTIFACT_DIRECTORY
python -m neurofly.g1_proxy_peak_deflection_cli replay ARTIFACT_DIRECTORY
```

No network, randomness, external papers or timestamps are needed. Replay validates
the exact canonical Phase 9B source, re-extracts records, reproduces IDs/order and
config/result hashes, and checks canonical file bytes, manifest and directory ID.
Rehashed semantic tampering is rejected by comparison to fresh offline extraction.
Generation uses staged exclusive writes and does not overwrite an existing artifact.

Focused tests protect coordinate-offset independence, scale proportionality,
tau-invariant immediate peaks, independent bilateral ancestry, zero controls,
boundary-zero/repeated rejection, malformed grids/identities, result/source/hash
tampering and network-disabled byte-equivalent replay. Extraction remains usable
for already validated test-local Phase 9B outputs without running dynamics itself;
only the canonical source is accepted for this published artifact.

## Remaining limitations and next step

Phase 8U remains unchanged with zero formally ready mappings. This operator does
not make the published 45 mV observation ready for numerical validation. Physical
unit mapping, source amplitude/window semantics, experimental protocol matching,
and input-transformation interpretation remain unresolved. No miniature,
spontaneous, quantal, recycling, repeated-response or Kadas-onset operator exists.

Exactly one proposed Phase 9F: a bounded read-only isolated-G1 empirical benchmark
readiness assessment recovering source-supported evoked amplitude and protocol
semantics from the original 2005 evidence chain. Determine whether an isolated
benchmark runner can be specified without guessing source fields; keep unknowns
explicit and do not fit, convert units, implement a runner, or compare values.
A future benchmark can reuse this extractor only after explicitly deciding its
protocol-specific baseline/window and physical-unit interpretation.
