# v10.5c — Exploratory Behavior and Neural Contribution Trace

## Purpose and boundaries

This change adds an optional, deterministic engineering speed controller to the existing continuous ground session. `baseline_v10_5b` remains the default and preserves the v10.5b frame and snapshot sequence. `engineering_exploration_v1` changes only translational propulsion. Both modes keep the same fixed 20 ms body step, 200 neural substeps of 0.1 ms, HS/DNp15 equations, neural yaw projection, geometric boundary yaw and collision semantics.

This is not a biological navigation mechanism. The circuit contributes to modeled yaw through the existing engineering projection. Clearance-based speed adjustment and geometric boundary steering are engineering rules. The changed body path can change later visual inputs and therefore later computed neural states through the existing closed loop; the solver itself is unchanged.

## Engineering speed policy

`web/src/lib/engineeringExploration.ts` measures ray distance from the current body anchor to the first edge of the existing rectangular arena, along the current heading (zero points toward +Z, positive heading turns toward +X). It adds no obstacle sensor or target.

The exploration command is piecewise linear in forward clearance `c`:

```text
c >= 0.18 units:       speed = 0.18 units/s
c <= 0.04 units:       speed = 0.045 units/s
otherwise:             linear interpolation between those endpoints
```

These are presentation-space engineering parameters. The low-clearance floor slows approach; it does not steer away from a wall or guarantee escape. At an existing wall contact, the established boundary/yaw and zero-outward-velocity behavior still applies, so accepted speed can be zero while the requested command remains 0.045 units/s.

The states `cruising`, `approaching_boundary`, `boundary_contact` and `recovering` describe the measured clearance/contact transition only. A bounded `BEHAVIOR` event records a state change, tick/time, clearance and trigger. They do not mean that the fly planned, feared, learned or decided to explore.

## Sample and trace semantics

Each bounded live sample contains:

- `interval`: the existing navigation frame at the interval's left boundary, including the exact neural and boundary yaw values used for this step;
- `accepted`: the body and neural snapshot after the interval;
- `engineering`: the mode, behavior state, forward clearance, baseline and commanded speed, accepted displacement divided by 20 ms, contact and transition trigger;
- `source`: the pinned neural authority artifact, dataset UUID, config hash and raw authority hash.

The historical baseline `interval` object is not augmented or reshaped. In exploration mode only, its established `propulsion_model_value` reports the engineering speed command. `engineering.actual_speed_units_s` is measured from the accepted position difference, so commanded and accepted movement remain distinct during contact/clamping.

The explanation panel reports angular velocity in rad/s, not heading change per interval. Its invariant is `angular_velocity = neural_yaw + boundary_yaw`. The displayed neural states are left-boundary model-space values; they are not calibrated calcium fluorescence or empirical measurements. `neuralActivityTrace` is presentation-only and does not execute the solver.

## Supported model entities and provenance

The existing runtime pins six HS source body IDs, ordered as `10015, 10016, 10023, 10034, 10181, 10419`, and two DNp15 target body IDs, `11215, 12069`. The verified selected structural routes are:

| HS model source | DNp15 model target | Pinned structural count |
|---:|---:|---:|
| 10015 | 11215 | 138 |
| 10016 | 11215 | 122 |
| 10023 | 11215 | 23 |
| 10034 | 12069 | 78 |
| 10181 | 12069 | 126 |
| 10419 | 12069 | 14 |

These identities/counts are checked against the existing MaleCNS-derived authority and source hashes. Runtime state values are the existing computational HS/DNp15 model states; the neural yaw is the existing signed DNp15 differential projection with its existing bounds. The trace does not infer additional connections, per-cell physiological activity, morphology, 3D coordinates or anatomical pathways. A future 3D consumer can safely use the eight IDs and current model-state values, tick/time, authority IDs/hashes and actual yaw contributions. It cannot safely position a neuron or draw extra edges from this trace alone.

## Deterministic A/B comparison

`compareExplorationModes` runs both modes with the same authority, initial pose, neural setting, body step and fixed tick horizon. Aggregates are updated incrementally; no full-session trace is retained. Reported boundary time means forward ray clearance at or below 0.18 units, not distance to any wall. The comparison also returns bounded-bin counts for accepted speed (`0`, `(0,0.045]`, `(0.045,0.09]`, `(0.09,0.135]`, `(0.135,0.18]`, `>0.18` units/s) and total angular velocity (`<-1`, `[-1,-0.5)`, `[-0.5,0)`, `[0,0.5)`, `[0.5,1)`, `>=1` rad/s), contact frequency per simulated minute and state durations. Results are engineering comparisons from the default initial condition, with neural influence on:

| Horizon | Mode | Path (units) | Mean commanded speed (units/s) | Mean accepted speed (units/s) | Contact events | Time near forward edge | Mean absolute neural yaw (rad/s) | Mean absolute boundary yaw (rad/s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 30 s | Baseline | 4.3911 | 0.1800 | 0.1464 | 3 | 8.68 s | 0.2226 | 0.3837 |
| 30 s | Exploration | 4.3348 | 0.1464 | 0.1445 | 1 | 9.86 s | 0.2208 | 0.3867 |
| 100 s | Baseline | 14.7052 | 0.1800 | 0.1471 | 11 | 29.62 s | 0.2210 | 0.3937 |
| 100 s | Exploration | 14.6700 | 0.1473 | 0.1467 | 1 | 36.36 s | 0.2114 | 0.4184 |
| 1,800 s | Baseline | 262.9337 | 0.1800 | 0.1461 | 211 | 530.26 s | 0.2200 | 0.3944 |
| 1,800 s | Exploration | 265.5562 | 0.1476 | 0.1475 | 1 | 672.08 s | 0.1987 | 0.4186 |

All six mode/horizon runs had zero non-finite states and zero arena-containment violations. The controller lowers its mean requested speed as designed and had fewer contact events in these runs, while measured time near the forward boundary increased. These results do not establish greater exploratory diversity or biological benefit. The changed path also produces downstream differences in neural yaw through the existing sensory feedback loop.

Reproduce fixed comparisons without writing artifacts from `web/`:

```sh
node --import tsx scripts/exploration-ab.ts
node --import tsx scripts/exploration-ab.ts 1500 5000 90000
```

## UI and future Neural Activity Explorer

The Lab selector chooses a mode before starting. It is disabled while running or paused; after Stop, the user can select a mode, which creates a new session at the original initial pose. Reset retains the chosen mode. The “Why did it turn?” panel pairs the selected interval's neural yaw, boundary yaw and resultant angular velocity with its clearance, behavioral state, speed command and accepted speed.

The trace is a bounded live snapshot contract, not a durable experiment record. Existing finite navigation/replay formats and Recorded Experiments are unchanged. Full neuron morphology, anatomical coordinates and a spatial neural renderer remain prerequisites for v10.5d.
