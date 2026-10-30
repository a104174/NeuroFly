# V10.8D — Controlled chamber width perturbation

## Protocol and assurance boundary

The headless `reactive_flight_environment_pair_v1` compares baseline chamber width 2.4 with width 2.0 presentation units. This choice was declared before either canonical run: it reduces forward clearance at the unchanged initial heading while retaining admissible conservative bounds. Depth 1.22, height 0.86, wall thickness 0.012, floor thickness 0.025, initial accepted pose/velocity, controller, timestep, plant coefficients, duration and randomness policy remain identical.

Reference implementation revision: `6e3295b10526cf4d1fdf784dec99fc99c2d64e4a`. Execution uses the V10.8D committed sources; it does not claim historical byte identity for those additive adapters. The protocol records the complete configurations, plant identity, observation version, controller identity, initial state, 20 ms interval, 1,500 interval horizon, termination policy and seed null/randomness NONE.

The original plant read global bounds for every collision interval. An additive, validated chamber argument now supplies those same bounds equations. Existing callers retain exact defaults. Each reactive session passes its configured chamber to the plant and derives observations from `flightBounds(chamber)`. Baseline X bounds are ±0.914; variant X bounds are ±0.714. Both retain Y [0.11032208074629306, 0.614] and Z ±0.324. The 0.28 horizontal and 0.24 upper clearances are unchanged. Constructors reject inadmissible initial poses; alternate environments cannot export as legacy v8 artifacts.

This is a headless scientific comparison. No alternate environment selector or rendered chamber was introduced. Existing Lab modes still render and simulate the original chamber. No protected arena source, manifest, neural equations, ground model or historical protocol changed.

## Control and analysis

The controller remains `engineering_reactive_flight_v1`, including all coefficients, hysteresis, takeoff and altitude mathematics. Only configuration plumbing changed. Interval ordering remains accepted state n → geometric observation n → command n → integration → accepted state n+1. There are no scheduled turns or spatial waypoints.

First-event comparisons use tolerance 1e-8 for geometric readings, motor scalars, wrapped heading and XYZ Euclidean position separation. This tolerance is numerical, not a biological significance threshold. Initial changed fields use exact inequality. Contact comparison uses complete recorded contact events. All results retain full observations, decisions, commands, accepted snapshots, events, configurations and termination, and reconstruction validation rejects altered or mismatched evidence.

## Measured results

Both conditions were executed twice; each produced identical canonical scientific results across repetitions.

| Metric | Baseline | Width variant |
|---|---:|---:|
| Airborne duration | 29.48 s | 29.48 s |
| Horizontal distance | 4.2889199485 | 4.3365526363 |
| X extent | 1.6083132667 | 1.1651751714 |
| Z extent | 0.6356502624 | 0.6036186182 |
| Altitude above floor, initial ground included | 0–0.3004906661 | 0–0.3004906661 |
| Minimum observed horizontal ray clearance to conservative bounds | 0.0057529662 | 0.0130803778 |
| Boundary steering responses | 12 | 11 |
| Wall / floor / ceiling contacts | 0 / 0 / 0 | 0 / 0 / 0 |
| Rejected commands / accepted bound violations | 0 / 0 | 0 / 0 |
| Termination | duration limit, flying at 30 s | duration limit, flying at 30 s |

Only forward wall clearance differs at initial accepted state 0: 0.914 versus 0.714 units. The first observation difference is index 0 at 0 s. The first feedback command difference is index 157 at 3.14 s; heading and position first differ at accepted index 158 at 3.16 s. This one-interval delay is consistent with command application. Maximum XYZ separation is 1.0180352518 units at index 1120 (22.40 s); final separation is 0.8525930719 units at 30 s. Contact histories remain identical and empty.

The baseline result hash exactly reproduces the V10.8C reference:
`9e0bc37b5f0e15407fcb9a37ca32b55602a67c3212b97e52d56c505c1f93b019`.
Variant input/result SHA-256:
`2775e13f06f7354bd4b00e57bbbbdbd84e8546521cbfeb7f57723be9e70b16e0` /
`92e486fafee3f7f832826b387d8cc6f89ef41e157abf635f7cc84ae138d5ec4c`.
Complete canonical pair SHA-256:
`be112200cea234476085b36ce63d30ab602960baf13a3ac2ad2842793684dda5`.

## Reproduction and limitations

From `web/`:

```sh
node --import tsx --input-type=module -e 'import {runReactiveFlightEnvironmentPair,environmentPairHash} from "./src/lib/reactiveFlightEnvironmentPair.ts"; const p=runReactiveFlightEnvironmentPair(); console.log(JSON.stringify({comparison:p.comparison,baseline:p.baseline.metrics,variant:p.variant.metrics,sha256:await environmentPairHash(p)},null,2));'
```

No trajectory files or storage service are required. Tests compare actual plant runs, repeated canonical evidence, the exact historical baseline hash, collision response against the variant wall, interval alignment, finite states, motion continuity, malformed evidence and legacy scheduled parity.

This controlled width change demonstrates environmental sensitivity within an engineering controller and body plant. It establishes no biological sensory validity, learning, neural lift, mediation fractions, population robustness or arbitrary obstacle avoidance. Clearances are geometric engineering queries in presentation units. No alternate-chamber browser rendering or real-device validation was performed.
