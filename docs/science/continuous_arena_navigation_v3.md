# Continuous Arena Navigation v3

A separate live-browser mode adds deterministic **engineering boundary recovery**
to the existing HS/DNp15 model and engineering propulsion. This is
`CONNECTOME_INFORMED_NEURAL_STEERING_WITH_ENGINEERING_BOUNDARY_NAVIGATION`, not a
biological wall reflex, validated walking, learning or motor-neuron actuation.
The v2 mode retains its original eight-second latched-contact behaviour.

## Model and time

The TypeScript v3 engine subclasses the validated v2 engine. Its private neural
state, geometric observation and 200 old-state neural transitions are reused;
only plant/contact hooks and the versioned duration are extended. Python reuses
the frozen v1 observation, neural adapter and body position integrator. MaleCNS
v1.0 UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`, HS R 10015/10016/10023,
HS L 10034/10181/10419, DNp15 R 11215 and L 12069 remain pinned. No DNg100
signal is used for propulsion or recovery.

Every 20 ms body interval performs exactly 200 neural substeps of 0.1 ms.
Observation of the preceding completed pose interval is held through those
substeps. Neural state persists across intervals and visual interventions.
The neural yaw-rate contribution retains the engineering gain 2.5 and clamp
±0.5 rad/s. Propulsion remains 0.18 presentation units/s, not biological speed.

Boundary policy `GEOMETRIC_INWARD_NORMAL_V1`:

- Admissible anchor half-extents: X 0.9654288893949121, Z 0.37542888939491215;
  inherited footprint and fixed altitude 0.11032208074629306.
- Proximity margin `m=0.06` presentation units; gain `k=2/s`;
  maximum engineering contribution `1.2 rad/s`.
- Distances to +X, −X, +Z, −Z walls are respectively
  `(Lx−x, Lx+x, Lz−z, Lz+z)`.
- Proximity weights are `w=max(0,1−distance/m)`.
  Inward vector `(nx,nz)=(w_−X−w_+X,w_−Z−w_+Z)`.
- With heading zero toward +Z and positive yaw toward +X, desired heading is
  `atan2(nx,nz)`. Error is wrapped with `atan2(sin(error),cos(error))`.
  At an antipodal tie within 1e−12 rad, choose positive π deterministically.
- `omega_boundary=clip(k*error*max(w),−1.2,+1.2)`; zero outside the band.
- `omega_total=omega_neural+omega_boundary`. No additional combined clamp masks
  either term. Both terms and their integrated signed heading changes are
  recorded separately; total magnitude is at most 1.7 rad/s.
- Translation uses old heading, then heading advances by `omega_total*0.02`.
  Position is clamped to the inherited admissible bounds.
- At a boundary, any outward velocity component greater than 1e−12 presentation
  units/s stops all translation. Contact is re-evaluated each boundary; inward
  or tangent headings release it. X takes precedence over Z at simultaneous
  contacts. There is no teleport, direct heading reset or random turn.

The 0.0036-unit free step is 6% of the proximity margin. The maximum heading
step is 0.034 rad. Boundary steering can overcome the bounded neural contribution
at an outward contact; the chosen parameters are engineering stability choices,
not physiological measurements. Near-wall correction can begin before contact.
A 30-second limit bounds telemetry and replay cost. Five body intervals per
render callback remain the catch-up cap; slow rendering discards excess wall-time
debt and slows simulated time, never changes either scientific timestep.

## Controls and numerical evidence

A is the unchanged v2 mode. B is v3 neural-active, C disables only neural-to-heading
application while continuing neural computation, and D switches the visual plane
at body boundary 100 (2.0 s). Initial conditions, propulsion and other parameters
are matched. C is selectable in the v3 UI; changing that checkbox explicitly
starts a new session. Live plane changes do not reset state.

| 30 s case | Distance | Contacts / releases | Contact seconds | Longest stall |
|---|---:|---:|---:|---:|
| B neural active | 4.39112 | 3 / 3 | 5.60 | 2.52 s |
| C neural output disabled | 5.17504 | 2 / 2 | 1.24 | 1.02 s |
| D plane switched at 2 s | 4.36926 | 4 / 4 | 5.70 | 1.80 s |
| Initial outward corner | 4.21083 | 3 / 3 | 6.60 | 3.36 s |
| Initial head-on wall | 4.32842 | 5 / 5 | 5.94 | 2.24 s |

Distance is accumulated actual clamped translation, not commanded speed times
elapsed time. A release count is a contact-to-free transition, not proof of
subsequent displacement; tests separately require more than 0.05 units of
movement within 100 subsequent steps. Contacts are counted at right boundaries;
contact duration sums intervals in which translation was blocked.

All 1501 boundaries of all five Python reference cases were independently
compared to the TypeScript model, including six HS/two DNp15 states, sensory
inputs, contact and both angular terms. Maximum absolute discrepancy was
4.971578704271451e−13, against the unchanged 1e−8 model-space tolerance.
At 4 s, B versus C heading differs by −0.439899 rad and endpoint separation is
0.110269 units. B versus D heading differs by −0.482682 rad and separation is
0.076218 units; their neural readout difference is −0.00592437 yaw_drive_eq.
These are model outcomes, not measured biological behaviours.

## Reproduction and integrity

`continuous_arena_navigation_event_log_v3` records the entire initial configuration,
source artifact/config/raw identities, geometry, exact boundary policy, zero
neural initial state, mode, stimulus changes and stopped boundary. The nested `body_model` is the unchanged pinned v0 plant reference, including
its historical eight-second metadata. `body_model_role` explicitly distinguishes
that source reference from the active v3 `duration_s=30` run schedule. Only stimulus
interventions are replay inputs. Computed contacts/recoveries are telemetry and
are regenerated; no collision or recovery commands are replayed.

`continuous_arena_navigation_session_v3` hashes configuration, event log, result
and logical artifact separately, using the existing finite sorted-key JSON
convention. Import checks metadata, fixed policy, hashes and recomputed telemetry;
computed floating values allow absolute 1e−8 libm variation, while identities,
time, substep counters and discrete outcomes are exact. Supplied poses are never
applied directly. v2 envelopes cannot be exported from the v3 engine.

```sh
mkdir -p /tmp/neurofly-navigation-reference
.venv/bin/python -m neurofly.continuous_arena_navigation_reference \
  --output /tmp/neurofly-navigation-reference/reference.json
```

Full reference traces remain external. The committed compact fixture holds
complete selected boundaries near first contact/release and across 30 s for each
case, with canonical reference identity
`65c159b935570737ed03550f4e54799a032d6730bd31c376df74fd667ee83b81`.
The standalone D model-session logical artifact is
`3a1e10cd7874088856b64f51310e8bde2bf04887708d43f5e87f3931bf18fd14`.
See the implementation-generated session for its recoverable log and telemetry;
a logical identity is not a raw file checksum.

## Product acceptance and limits

The local browser encountered a wall, rotated continuously and resumed actual
translation. A visual intervention after recovery preserved neural state;
recalculation, export/import, invalid-import rejection, pause/resume/reset,
30-second completion, v2 and B/C/D regression, desktop and 390 px layout passed.
An existing `/favicon.ico` 404 is unrelated to model execution. Actual rendered
body pose matched live telemetry. SwiftShader rendered about 5 FPS; this does
not characterize physical GPU performance. Catch-up limitation was explicit.

The controller is geometry-only; it does not establish biological wall avoidance,
exploration, receptor signs, muscle recruitment, gait or propulsion calibration.
It may spend seconds rotating at contact and has no guarantee for arbitrary
future obstacles or geometry. Acceptance applies to the bounded rectangle and
specified tested conditions. Previous scientific outputs and UNKNOWN biological
sign evidence remain unchanged.

Completed publication checks: 1,686 Python tests passed, one authenticated
integration deselected under existing policy, two dependency deprecation warnings;
165 frontend tests passed. Ruff lint/format, frontend lint/typecheck/production
build and diff checks passed. The frozen D2.2 archive, historical raw artifacts,
structural authorities, official NT source and all fifteen UNKNOWN signs were
verified unchanged. A separately replayed local 30-second intervention session
agreed with Python to 3.637978807091713e−12 across every completed interval;
its old neural state and geometry-only steering at intervention remained matched
while the neural readout changed. Protected Preview acceptance is a separate
post-deployment check; these recorded checks describe the local candidate.
