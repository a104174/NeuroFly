# Phase 12B — exploratory planar body plant

## Capability and scientific boundary

NeuroFly computes deterministic exploratory body-position trajectories from
persisted synthetic Phase 11B actuator fixtures. This is not predicted fly
displacement, biological jump distance, physical takeoff or autonomous
connectome-driven escape. No frontend, scenario, transport or upstream tuning
is introduced. Backend simulation owns state; future rendering may only
interpolate authoritative snapshots.

The direct source is replay-validated Phase 11B artifact
`478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40`,
schema `ttm_exploratory_actuator_command_result_v1`. Its six fixtures preserve
12 actuator trajectories and 972 command samples, including inactive sides.
Source identities remain 800146/R → RIGHT_TTM_ACTUATOR and
804642/L → LEFT_TTM_ACTUATOR, with proxy ancestry retained. Electrical dynamics
and activation are neither bypassed nor rerun within the plant.

## Model and assumptions

Model: `exploratory_planar_body_plant_v1`.
Result: `exploratory_planar_body_plant_result_v1`.
Provenance: `EXPLORATORY_PLANAR_BODY_PLANT`, downstream of
`EXPLORATORY_TTM_ACTUATOR_COMMAND`.

For source boundaries n = 0…79:

```text
common[n] = (right[n] + left[n]) / 2
speed[n] = motion_gain_world_eq_per_ms * common[n]
x[n+1] = x[n]
z[n+1] = z[n] + (time[n+1] - time[n]) * speed[n]
```

The canonical gain is 1.0 world_eq/ms: a simple normalization selected without
fitting, biological velocity, force, mass or visual asset scale. Initial x/z
are 0.0 world_eq, deterministic reset coordinates. These values, arithmetic
common-mode mapping and fixed +Z heading are explicit MODEL_ASSUMPTIONs.
Coordinates are +X world right, +Z world forward; world_eq is not meters or mm.
Only gain and initial coordinates are configurable numerical quantities; gain
must be finite positive and coordinates finite. Semantic drift is rejected.

No differential term or steering exists. Unilateral input contributes half
the drive of equal bilateral input, by assumption—not leg biomechanics.
There is no velocity state, inertia, acceleration, damping, gravity, vertical
axis, contact, floor, arena bound, orientation change or articulated geometry.
Zero command stops prescribed speed immediately; integrated position remains.

## Boundary semantics and representation

The source 0.1 ms grid has 81 boundaries and 80 intervals. Boundary n drives
interval n→n+1, not the position at n. The final command at boundary 80 is
validated but never integrated. Body x/z columns have 81 samples each;
common-mode and speed diagnostics have 80 elements, explicitly indexed by
interval-start boundary. Shared boundary/time arrays avoid redundant samples.
There is one body per fixture, not separate bodies per side. Both source
actuator identities and hashes are retained on each body trajectory.

## Canonical outputs

All x values remain exactly zero; all z trajectories are nondecreasing.

| Fixture | Final z (world_eq) | Maximum speed (world_eq/ms) | Nonzero intervals |
|---|---:|---:|---:|
| ZERO_EVENT_CONTROL | 0 | 0 | 0 |
| RIGHT_SINGLE_EVENT | 0.10498749586386545 | 0.1 | 70 |
| LEFT_SINGLE_EVENT | 0.10498749586386545 | 0.1 | 70 |
| BILATERAL_SIMULTANEOUS_EVENT | 0.2099749917277309 | 0.2 | 70 |
| RIGHT_REPEATED_EVENTS | 0.209362769474689 | 0.11353352832366126 | 70 |
| LEFT_REPEATED_EVENTS | 0.209362769474689 | 0.11353352832366126 | 70 |

Six trajectories retain 81 boundaries each: 486 body samples. Repeated input
integrates the full stored actuator history without additional dynamics.
The first nonzero command at boundary 10 changes position at boundary 11.

## Artifact, replay and validation

Artifact schema: `exploratory_planar_body_plant_artifact_v1`.

- ID: `bb3696faae558778555601991de3fd36081d5853c889fcb7aac5ffd79593eba3`
- Config SHA-256: `88df5840456eaa2a9df92cd60cbe1555e3365cd4e8f87434d06bed6013272cd0`
- Result SHA-256: `4b8b462ebe703c92e68f24d10f8f49784d0087dd27f919b0ce5650320874728e`
- Canonical generated size: 41,816 bytes including manifest.

Generated data stays under ignored data/derived conventions. Canonical JSON,
file manifest, semantic/config/result hashes and directory identity follow
existing immutable artifact conventions. Replay validates Phase 11B and its
ancestry offline, rebuilds all interval integrations and rejects mismatches.
No network or randomness is required.

CLI: `python -m neurofly.planar_body_plant_cli generate`, `inspect ARTIFACT`,
`replay ARTIFACT`. Inspection labels exploratory model-space kinematics.

Focused tests protect analytic summed displacement, common mode, symmetry,
timing, final-boundary exclusion, deterministic reset, finite validation,
source/config/result/manifest tampering and absence of physical state fields.

## Genuine production path and Phase 13 handoff

The full canonical Phase 7O numerical replay remains unchanged:
`99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5`.
All 35 conditions have zero DNp01 spikes. Genuine Phase 8C replay
`5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf`
has zero motor events and zero TTMn state. There is no canonical genuine
Phase 11B actuator artifact: production composition remains absent. Synthetic
plant movement does not resolve neural silence or demonstrate causal behavior.

Exactly one Phase 13A should decide the first deterministic world/scenario
closed-loop architecture: world and looming-object state, body-relative
geometry, explicit conversion to existing sensory-column input, causal tick
scheduling and genuine production-path composition. It must retain honest
stationary behavior if neural output remains zero. World/body geometry does
not yet drive sensory input. Future frontend snapshots may expose step/time,
x/z world_eq and fixed heading; rendering cannot own or feed back movement.
No Phase 12C is proposed.
