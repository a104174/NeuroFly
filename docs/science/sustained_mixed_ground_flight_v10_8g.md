# V10.8G — Sustained mixed exploration

## Audit and predeclared conditions

V10.8F's 0.05-unit path threshold permits re-takeoff after 14 ground intervals (0.28 s at the existing 0.18 units/s forward drive). Its trial then stops after second-flight confirmation. This is coordinator policy, not a ground-engine limitation.

The new sustained protocol declares 0.18 units of cumulative accepted ground travel and at least 50 accepted walking intervals, plus the existing 0.06-unit takeoff ray-clearance and 0.36-unit ceiling-clearance requirements. The duration requirement is an additional minimum; elapsed time alone never permits takeoff. The finite global horizon is 3,000 intervals / 60 s. Each underlying flight episode retains the existing 1,500-interval local limit. These values were selected before running the first sustained trial. No neural parameters, plant coefficients, chamber dimensions, random policy or existing controller equations were tuned.

Ground intervals use the real ground collision envelope (X/Z ±0.9654288894 / ±0.3754288894). Flight intervals use the unchanged conservative flight envelope (±0.914 / ±0.324). Both use the same standard chamber and floor anchor. The destination flight envelope is revalidated separately at every takeoff. An unsafe destination postpones takeoff; it does not clamp or move the body. Ground wall contacts remain actual ground-model contacts, not fake flight contacts.

## Initial failure and bounded correction

The first declared sustained-v1 trial completed two walking episodes and three takeoffs, but failed at 57.58 s with `duration_limit_reached`. Its third flight had entered braking where a lateral ray clearance was below the existing 0.06 landing threshold. Zero horizontal input could never restore clearance; the unchanged touch-and-go controller remained braking until its local horizon expired. The failed run had zero bounds violations and rejected commands. Its canonical result hash was `0f860741067a2a7eb129b3befa6eae5fcc89afd90bb5b104a3e0e2b2d9e8658b`; it is not presented as successful evidence.

The final protocol/result are explicitly `mixed_ground_flight_sustained_v2` / `mixed_ground_flight_sustained_result_v2`. Before rerunning, the coordinator added one clearance-based recovery rule: when a resumed flight's proposed braking state has any existing landing ray clearance below 0.06 units, return to unchanged reactive exploration. The actual recovery command, reason and phases are recorded. Walking thresholds and all existing controller coefficients remain as first declared. Recovery occurred at 28.66, 30.12 and 31.98 s in the final run. No pose, clock or plant reset is involved in these recoveries.

## Ownership, lifecycle and neural interpretation

Only one existing engine integrates each global interval. Initial flight uses the original touch-and-go session; subsequent episode-local FlightEngines start from accepted walking XYZ, heading and planar velocity. The coordinator composes the existing touch-and-go decisions for repeated state-dependent landings, with the recovery rule above. Every accepted landing initializes a new LiveGroundSession at exactly the landed pose. Each fresh ground episode records six zero HS states, two zero DNp15 states and a null first sensory summary. Ground samples and motor computations come from the existing model; neural values are explicitly unavailable in flight.

Global timestamps remain monotonic while native episode-local indices and evidence remain separately recorded. Handoffs carry source/destination identity, exact pose, velocity, reason and neural initialization. Sustained intervals add episode identity, cumulative ground path since landing, re-takeoff eligibility, landing eligibility where supplied by the flight controller, and native neural summaries only during walking. Per-episode summaries include source ownership, duration, path length, heading change, contacts, completion, controller transitions and neural initialization.

The existing V10.8F constructor default, result schema and canonical evidence remain unchanged. The sustained mode is opt-in. No underlying integration engine, historical controller, frozen scientific source or asset was modified in this phase. The reference checkout before additive implementation was `b76481accc006c4665c93db1af4fc1f67ef14083`; reproduce final evidence using this phase's committed sources.

## Canonical v2 results

| Flight episode | Takeoff request | Accepted flying | Landing request | Accepted landing | Episode distance |
|---|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.52 | 9.16 | 11.84 | 1.1641798574 |
| 2 | 15.40 | 15.92 | 23.86 | 26.56 | 1.1518792524 |
| 3 | 27.58 | 28.10 | 35.32 | 38.00 | 1.0802817641 |
| 4 | 39.00 | 39.52 | 43.26 | 45.84 | 0.4336298162 |
| 5 | 49.26 | 49.78 | 57.98 | not reached by 60 s | 1.1929493084 |

Times are global simulation seconds; distances are presentation units. Flight ownership durations, including takeoff and landing, are 11.84, 11.16, 10.42, 6.84 and 10.74 s. The fifth episode is explicitly incomplete at the finite cutoff, with accepted plant state landing.

| Ground episode | Start–end (s) | Duration (s) | Accepted path | Heading change (rad) |
|---|---:|---:|---:|---:|
| 1 | 11.84–15.40 | 3.56 | 0.6408 | +0.2513092435 |
| 2 | 26.56–27.58 | 1.02 | 0.1836 | −0.1877040583 |
| 3 | 38.00–39.00 | 1.00 | 0.1800 | −0.0437246018 |
| 4 | 45.84–49.26 | 3.42 | 0.6156 | +0.2436090612 |

All four completed ground episodes exceed the previous 0.28 s and satisfy the declared minimum duration/path gates. Clearance can delay takeoff beyond those minima, explaining different durations without randomness.

Whole trial: five takeoffs, four accepted landings, four genuine walking episodes, eight handoffs, four neural initializations, and 19 physical flight transitions. Total walking is 9.00 s / 1.6200 units; total horizontal travel is 6.6429199986 units (flight ownership contributes 5.0229199986). Flying/landing start-state intervals total 48.40 s; takeoff intervals contribute the remaining 2.60 s of flight ownership. Altitude above floor ranges 0–0.2997485800 units. Eight boundary steering responses were recorded. There are four FLOOR events, zero wall/ceiling events, zero rejected commands and zero accepted violations of each active engine's conservative envelope. Maximum handoff position/heading and global timestamp discontinuities are zero.

Termination: `DURATION_WINDOW_COMPLETED`, with the predeclared acceptance gate passed. A completed finite window does not imply that its final landing completed.

Two runs match all canonical configurations, observations, commands, accepted poses, ownership, initialization records, events, episode metrics and termination.
Final result SHA-256:
`92c034ca11d507d9e2759ed5c3241ecb6510a17737388cdfe5f8d3fa96bd272b`.

V10.8F remains exactly
`e630d4278fb9fc94e8dd736726a7049af9d85af5df28dcfb80be864b0f1282d5`.
V10.8E remains
`b9636f67ee6fe70559015399d1df9f60c3eef048e96793a3c840d1e135264894`;
V10.8D pair remains
`be112200cea234476085b36ce63d30ab602960baf13a3ac2ad2842793684dda5`.
The V10.8C canonical hash remains covered by the paired regression test.

## Reproduction and UI validation

From `web/`:

```sh
node --import tsx --input-type=module -e 'import {readFileSync} from "node:fs";import {parseNeuralLocomotion} from "./src/lib/neuralLocomotion.ts";import {runSustainedMixedGroundFlight,mixedGroundFlightHash} from "./src/lib/mixedGroundFlight.ts";const a=parseNeuralLocomotion(JSON.parse(readFileSync("public/experiments/experimental_locomotion_v1.json","utf8")));const r=runSustainedMixedGroundFlight(a);console.log(JSON.stringify({acceptance:r.acceptance,metrics:r.metrics,termination:r.termination,failure:r.failure,sha256:await mixedGroundFlightHash(r)},null,2));'
```

Primary Lab → Reactive flight exploration → Sustained flight + ground exploration. All prior behavior options and the default ground mode remain. The existing viewer, body transform, wing and leg rigs, camera, clock and cleanup are reused. Scientific history is bounded to 3,000 global intervals; current ground gait uses only its episode's accepted samples.

A focused local Chromium check used the production build and existing cached Chromium via its debugging protocol, without installing browser dependencies. It checked first flight, landing, real walking displacement, re-takeoff, pause/resume, reset and behavior switching. Screenshots were inspected for flight/ground presentation and framing; one canvas and no uncaught page exceptions were observed. This is one desktop browser/software-rendering check, not real-device, cross-browser or GPU/FPS acceptance.

This remains deterministic engineering behavioral composition with model-computed ground neural activity. Fresh neural episodes are not a biological reset claim. There is no learning, biological motivation, continuous neural flight state, internal obstacle model, wingbeat aerodynamics or biological validation. A longer horizon or other initial states may expose further unsuccessful transitions; no universal behavioral robustness is established.
