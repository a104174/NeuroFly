# Phase 13B — deterministic closed-loop circuit-validation scenarios

## Executable scope

One backend runner executes exactly `BASELINE_CONTROL` and
`LOOMING_CIRCUIT_VALIDATION`. World/body geometry drives all 311 pinned sensory
states, the existing DNp01 model and the complete downstream motor path.
Actuator commands drive the planar plant, whose updated authoritative position
participates in the next sensory projection. Canonical runs contain no injected
events. Stationarity is a valid computed result, not a failure or fallback.

This is exploratory model-space circuit validation, not physiological visual
registration, biological escape or calibrated mechanics. The strategic worlds
Baseline, Light/Dark, Obstacle Course, Resource Search, Adversity/Avoidance and
Changing World remain unchanged. Looming is an initial circuit-validation
scenario, not a replacement taxonomy. No frontend/API/database was added.

Config schema: `closed_loop_scenario_config_v1`.
Integrated result schema: `closed_loop_scenario_result_v1`.
Provenance: `EXPLORATORY_GENUINE_CLOSED_LOOP_SCENARIO`.

## Reference configurations

Both runs use dt 0.1 ms, 14 intervals, 15 boundaries, duration 1.4 ms. This
matches the existing Phase 7O reference window and was not extended to obtain
spikes. Historical electrical config references retain their original 80-interval
artifact horizon; scenario stepping uses the separate 14-interval grid without
changing the referenced scalar parameters or migrating the old artifact.
Body reset is x=z=0 world_eq, heading fixed +Z; +X is world right.
No steering, gravity, inertia, contacts or arena bounds exist.

Baseline explicitly disables the stimulus: object and projection observations
are null, active columns empty, exposure exactly zero. It is **not** a
radius-zero disk, which could expose a centre column. It does not demonstrate
baseline locomotion.

Looming object: initial (x,z)=(0,4) world_eq, radius 1 world_eq, prescribed
velocity (0,-1) world_eq/ms. All are MODEL_ASSUMPTIONs. Object position advances
by dt times prescribed velocity at each interval; no physical object dynamics
or collision response is asserted.

At every boundary use object minus **current authoritative body** position.
Store relative x/z/distance and require positive forward separation. Reject
nonfinite coordinates, nonpositive object radius and unsupported behind-body
geometry. Never wrap, mirror or introduce contact behavior.

```text
half_angle = atan2(radius_world_eq, relative_distance_world_eq)
lattice_radius = floor(10 * half_angle)
```

The unit-neutral half-angle primitive is shared with existing analytic looming
geometry, without labelling world_eq as m. Projection side R and centre hex
(23,9), scale 10 and floor discretization are explicit MODEL_ASSUMPTIONs:
FIXED_RELATIVE_COLUMN_CENTRE_ASSUMPTION, FIXED_RIGHT_SIDE_ASSUMPTION,
HALF_ANGLE_TO_LATTICE_RADIUS_SCALE_ASSUMPTION and
INTEGER_FLOOR_DISCRETIZATION_ASSUMPTION.

Existing `active_column_set` and `compute_body_exposure` supply the disk and
column-overlap exposure. No new lattice algorithm, structural-contact weighting,
population normalization or absolute bearing-to-retinotopy mapping exists.
All 311 identities retain exposure/state at all 15 boundaries, including
unexposed left-side cells. Mathematical angular ratios are not calibrated
receptive fields. Positive +Z body motion approaches this object; it is not an
escape-direction model.

## Shared model authorities and historical preservation

| Batch authority | Shared kernel/semantic operation | Regression |
|---|---|---|
| analytic LoomingStimulus.sample | angular_half_size | existing geometry tests unchanged |
| integrate_exposure_values | sensory_state_step | exact scenario/batch parity and full 7O replay |
| LIFSimulator.run | lif_interval_step, make_spike_event, apply_spike_reset | full 7O identical; controlled nonzero/refractory parity |
| motor _integrate_ttmn | ttmn_boundary_step | 8C unchanged; test-local event/batch parity |
| Phase 8N _crossing_steps | threshold_crossed | existing crossing threshold/order unchanged |
| Phase 8O target dispatch | scenario-owned dispatch_runtime_output using existing association resolution/fields | historical dispatch loader unchanged |
| Phase 8Q receipts | receipt_target_semantics and scenario-owned receipt_runtime_dispatch | historical receipt bytes unchanged |
| Phase 8W tokens | abstract_input_semantics and token_runtime_receipt | historical pinned admission unchanged |
| Phase 9B integrate_counts | electrical_boundary_step | historical replay and controlled numerical parity |
| Phase 10B activation | existing activate_samples | unchanged scale/equation |
| Phase 11B routing | actuator_channel | existing body/side guards and historical replay |
| Phase 12B integrate_commands | common_mode_speed, body_interval_step | historical body replay and interval tests |

LIF deliveries and graph event queues remain under the original batch authority;
the scenario uses its validated two-DNp01 edge-free readout graph, as Phase 7O
does. No broad simulator rewrite occurred. Historical loaders still reject
noncanonical fixture/provenance data. Canonical Phase 7O full numerical replay,
8C replay and the 12B recursive downstream replays passed after extraction.

Parameters remain unchanged: sensory tau/gain 1/1, transfer k=1, existing DNp01
LIF parameters and refractory semantics, motor tau 10 ms/gain 0.25, output
crossing threshold 0.25, electrical reference 0 mV_eq/tau 1 ms/event scale
2 mV_eq, activation scale 10 mV_eq, body gain 1 world_eq/ms. Scenario horizon
does not alter those parameters. No tuning, fitting or visual-distance matching.

## Causal tick semantics

At boundary n:

1. Read authoritative body/object geometry and DNp01 spikes stamped n from the
   preceding neural interval (none initially).
2. Derive current geometry, relative-column disk and all exposure values e[n].
3. Route only those DNp01 spikes into the audited ipsilateral TTMn identities.
   Decay then inject input at n; compare previous/current stored motor state
   using the existing crossing rule.
4. Validate target association; produce scenario-owned dispatch→receipt→
   abstract token at n, with ZERO_ADDED_MODEL_DELAY_ASSUMPTION.
5. Decay electrical state then apply boundary tokens; compute static activation
   and exact side-preserving commands. Persist boundary state/telemetry.
6. For n<14, drive DNp01 over n→n+1 from sensory **s[n]**, emitting real
   SpikeEvents at n+1. Exposure e[n] separately produces s[n+1]. No instantaneous
   exposure→DNp01 shortcut.
7. Integrate the body over n→n+1 from commands[n], then advance the prescribed
   object. Next iteration uses these updated positions, not cached separation.

Boundary 14 is recorded and its downstream events processed, but has no
outgoing neural/body/object interval. The body uses actual shared timestamp
differences, preserving Phase 12 semantics. Backend simulation owns this order;
render FPS and browser clocks are irrelevant.

## Genuine production composition and ancestry

Runtime composition is DNp01 SpikeEvent→audited motor input→TTMn state→model-
derived crossing output→target dispatch→NMJ handoff receipt→abstract electrical
input→G1 electrical state→activation→functional actuator→body.

Scenario event envelopes have distinct versioned schemas. Event content IDs
retain the scenario execution identity, parent event IDs, source body/side and
exact boundary/time. Dispatch retains the pinned Phase 8K association. Receipts
assert bookkeeping handoff, not release success; tokens have no physical
amplitude/current/conductance/quantal interpretation. G1 ancestry retains the
Phase 8Y virtual domain and distinct 800146/R and 804642/L instances.

Historical artifact IDs are config-authority references, not runtime event
sources. No scenario is labelled a historical 8O/Q/W/11B fixture; no synthetic
run ID is fabricated. Historical loaders and artifact identities stay pinned.
The runner exposes no force-spike/override-actuator configuration or CLI option.

## Canonical computed results

| Quantity | Baseline | Looming |
|---|---:|---:|
| sensory identities / boundaries | 311 / 15 | 311 / 15 |
| exposed-body count | 0 | 19→22 |
| lattice radius | absent | 2→3 (first radius-3 boundary: 8) |
| object z (world_eq) | absent | 4→approximately 2.6 |
| maximum sensory state | 0 | 0.2763424516881957 |
| maximum DNp01 membrane value | -52 | -51.933657842035174 |
| DNp01 spikes | 0 | 0 |
| motor inputs / outputs | 0 / 0 | 0 / 0 |
| dispatches / receipts / electrical tokens | 0 / 0 / 0 | 0 / 0 / 0 |
| TTMn/electrical/activation/actuator state | exactly zero | exactly zero |
| final body x/z (world_eq) | 0 / 0 | 0 / 0 |

Zero output is computed through each stage, not hard-coded. Both bodies remain
stationary. A stationary model is not evidence of biological nonresponse.

Statuses are separate: closed_loop_execution_completed=true and
body_state_feedback_wired=true for both; environment_affected_sensory_input is
true only for Looming. body_state_feedback_realized,
genuine_nonzero_actuation_occurred and body_movement_occurred are false for both.
Thus the canonical runtime demonstrates wiring but not realized movement-driven
feedback or escape. No exceptional fallback is applied.

## TEST_ONLY_NONCANONICAL integration proof

Focused tests send an isolated test-local DNp01 event into the downstream
composition at boundary 1. It produces TTMn state 0.25, exactly one crossing,
dispatch, receipt and token; electrical deviation 2 mV_eq; activation and
appropriate side actuator command 0.2, opposite side zero. Common-mode speed
0.1 world_eq/ms integrates a 0.01 world_eq forward displacement.

A controlled object position straddling a lattice-radius boundary then yields
different next relative geometry, radius 2→3 and changed exposure from that
updated body state. Both sides are tested. Parent IDs and same-boundary timing
are checked throughout, along with motor/electrical batch parity. This proof
exists only in tests, not scenario configs or generated scientific artifacts.

## Artifact, replay, telemetry and performance

One ignored canonical artifact contains both runs, shared grids, identity-
resolved sensory/exposure arrays, ordered contribution ledgers, two DNp01
state traces/spikes, two downstream streams, event ledgers, body interval
diagnostics and lightweight telemetry. Metadata is static/versioned; no database.

Artifact schema: `closed_loop_scenario_artifact_v1`.

- ID: `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b`
- Config hash: `3145673ad2bb6345fa9287adab37eee859861b7b029c40989a9a0fc352dff7c6`
- Result hash: `e33d5d8163b4b24755ea8479475258c28c44f8d8f351de2444a1693629435242`
- Size including manifest: 1,137,837 bytes.

Replay validates pinned population/column/target/proxy/model references and
historical source artifacts, reconstructs both initial states and all ticks,
and compares canonical config/result bytes, hashes and manifest. No network or
randomness. Tamper tests cover world/config/projection, source identity,
sensory/DNp01 state/spikes, downstream ancestry, commands/body, tick order,
statuses and artifact hashes. Repeated reset/replay is byte-identical.

Measured on this workspace alongside full regression execution: source
validation 5.89 s; two scenario tick runs with validated sources 0.113 s;
complete offline replay 6.42 s. Measurements are diagnostic and excluded from
scientific hashes. Source validation dominates, not the 14-interval loop;
no speculative optimization was introduced.

CLI: `python -m neurofly.closed_loop_scenario_cli generate`,
`inspect ARTIFACT`, `replay ARTIFACT`. Inspect also performs replay, labels the
exploratory/non-escape boundary and shows distinct runtime/movement statuses.

## Phase 14 handoff and scientific claims

Telemetry provides scenario/run IDs, step/time, body x/z and fixed heading,
object state, relative distance/disk radius, sensory type/side summaries,
DNp01 states/spikes, TTMn state and two commands. Result-level status retains
completion, feedback, genuine actuation and movement distinctions. Detailed
311-body data remains available for scientific inspection, not every visual
frame. Phase 14 may derive a transport/presentation adapter and scenario picker
from these records; no transport or rendering is implemented here.

Allowed: deterministic exploratory closed causal loop through identity-resolved
sensory/neural/motor models and model-space body plant; current assumptions
produce zero spikes and movement. Not allowed: escape, biological retinal
calibration, physical displacement prediction or biological lack of response.
The externally blocked Koenig benchmark and mV_eq calibration are untouched.

Next exactly one Phase 14 implementation: scenario selection, authoritative
3D state playback/live presentation and bounded scientific telemetry. Frontend
only renders/interpolates backend snapshots; no scripted animation substitutes
for neural output. No Phase 13C.

## Acceptance and quality gates

Decision: `FIRST_CLOSED_LOOP_SCENARIO_RUNTIME_VALIDATED`.
Movement: `CANONICAL_GENUINE_MOVEMENT_ZERO`.
Handoff: `READY_FOR_PHASE14_SCENARIO_FRONTEND_INTEGRATION`. Phase 13B **PASS**.
Focused scenario tests: 39 passed; initial kernel regressions: 80 passed.
Full tests: 975 passed, 1 deselected, two existing dependency deprecation
warnings. Ruff check/format and git diff check pass. Frontend regression tests
(38), lint, typecheck and build pass; no frontend changes remain. Generated
canonical artifact remains ignored. No commit or push.
