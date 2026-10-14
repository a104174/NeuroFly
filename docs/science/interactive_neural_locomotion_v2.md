# Interactive Neural Locomotion v2

This mode computes new states locally in the browser. It does not select or
interpolate among prerecorded B/D trajectories. The existing V2-F GLB, arena,
cameras, contact plant and historical replay/comparison modes are preserved.

## Source and mathematical contract

Authority/configuration comes from the byte-verified published v1 JSON at
`/experiments/experimental_locomotion_v1.json`. Its raw SHA-256 is
`17d335358a4f5cf4ed98b9682b103a81419cf82504203ce1bc72a7d76285d748`;
logical artifact is
`4d7c791224f21ecf677df81d2127a6f8b753974694b6b324afc1948da3fb9064`.
The runtime uses its configuration only, never its recorded trajectories.
Missing/corrupt authority stops initialization; no synthetic steering fallback.

MaleCNS v1.0 UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`. State order:
HS R 10015/10016/10023, HS L 10034/10181/10419; DNp15 R 11215, L 12069.
The six directed routes and structural counts are checked unchanged. Counts are
provenance, not numeric gains. The model equations and parameters are those of
Python v1, including its established exploratory assumptions:

- Source update: `s' = u + (s-u)*exp(-0.1/5)`, milliseconds.
- Target drive: sum of three eligible **old** HS states divided by three.
- Target update: `d' = D + (d-D)*exp(-0.1/10)`, milliseconds.
- Both updates are simultaneous. Readout uses **old** bilateral DNp15 difference.
- Each neural substep contributes `(0.1/50)*(DN_R-DN_L)` orientation_eq.
- Exactly 200 substeps per body interval; state persists across intervals.
- `omega = clip(2.5*sum(increment_eq)/0.02, -0.5, +0.5)` rad/s.
- Translation uses left-boundary heading: `dx=0.18*sin(theta)*0.02`,
  `dz=0.18*cos(theta)*0.02`; then `theta += omega*0.02`.
- The existing footprint bounds clamp position. Outward boundary contact latches
  translation to zero; neural/heading computation continues without wall reflex.

The geometric observer evaluates the preceding completed pose interval using
current world landmarks `(X,Z)=(+0.6,plane),(-0.6,plane)`. Bearing shift is
`atan2(bz*ax-bx*az, bx*ax+bz*az)`. Relative shift in orientation_eq subtracts the
unwrapped heading increment divided by `2*pi`; side descriptors multiply by
`50/interval_ms`, reverse the left sign, and clip explicitly to [-1,1]. The
observation is held throughout all 200 substeps. Initial observation and neural
states are zero. Singular swept landmark geometry and ambiguous/non-finite
observations are rejected. The observer is an engineering geometric construction,
not a calibrated retina.

## Events, time and display

The only live stimulus intervention switches Z=+0.4 / −0.4. A request takes effect
at the next **uncomputed** body interval's left boundary. At displayed boundary n,
interval n−1 has finished; the event applies before observation for interval n.
When paused it waits for the next advance. Requests for the same plane are
coalesced; the last request before computation wins, and cancelling back to the
active plane produces no event. Applied events record step, time, old/new plane.
No old state is rewritten, no neural state is reset, and no turn is injected.
The new geometry evaluates both endpoints of the completed motion; this models a
parameter intervention, not a retinal flash caused by moving landmarks.

The scientific body clock is 20 ms, neural clock 0.1 ms, duration eight seconds.
A bounded accumulator executes at most five intervals per animation frame.
Excess wall-time debt is discarded explicitly, never absorbed into a larger dt;
simulation can run slower than real time. Pause discards wall-clock debt only.
Reset restores original pose, zero neural state, Z=+0.4 and an empty event log.
Rendering uses the last complete boundary without extrapolation. Its current
neural states are right-boundary states; displayed drive/omega summarize the last
completed interval. Exported interval telemetry retains Python's left-boundary
state/outgoing-readout convention. These are different, declared timestamps.
The live trajectory has a fixed-capacity geometry, not a rebuilt spline.

## Reproducibility and integrity

Runtime version: `INTERACTIVE_NEURAL_LOCOMOTION_V2`. Event-log schema:
`interactive_neural_locomotion_event_log_v2`. Session schema:
`interactive_neural_locomotion_session_v2`. The configuration includes complete
body geometry/units, initial pose/neural state, source URL and hashes, model pins,
mode, gains, both clocks, duration and randomness policy NONE. Events and stopped
boundary fully determine the run. A pending paused request is stored separately.
`PAUSED` in the exported log means a reconstructable prefix/checkpoint; it does
not encode a wall-clock pause duration, which cannot affect scientific state.

Replay recalculates that prefix from the initial state. Import recomputes every
interval and rejects contradictory content even if supplied hashes were
recalculated. The UI imports only neural-active sessions; engineering-only and
output-disabled engine modes exist for parity/control tests. JSON hashes use
sorted object keys, ordered arrays, finite ECMAScript JSON numbers and UTF-8;
Python float serialization need not be byte-identical. Session identities hash
complete recoverable content and distinguish config, event log, result and
logical artifact; the latter is not a raw file checksum. Large trajectories and
source datasets are not committed.

## Python parity and causal controls

Absolute parity tolerance is 1e-8 in each model-space quantity over eight seconds,
well below displayed precision and relative to the bounded proxy scale. Tests
compare all 401 boundaries of published Python A/B/C/D, including geometry,
six HS/two DNp15 states, aggregate readout, heading, position and contacts. A new
small Python reference uses the original frozen functions, switches at boundary
100 (2.0 s), and continues state. Its full output remains external; the committed
19.7 kB fixture contains 17 complete selected boundaries and a content hash,
not a replay trajectory. Generation:

```sh
.venv/bin/python -m neurofly.interactive_neural_locomotion_reference --compact \
  --output web/tests/fixtures/interactive-neural-reference-v2.json
```

The fixture is checked against genuine pinned source and regenerated in tests.
No historical artifact is overwritten. Python tests assert unchanged state before
the intervention and changed subsequent observation/readout/heading. Browser
runtime tests also cover clocks, pause/reset, event replay, controls, finite
inputs, contradictory provenance and semantic tampering.

## Interpretation and gates

Labels are `LIVE_BROWSER_MODEL_SIMULATION`,
`INTERACTIVE_CONNECTOME_INFORMED_NEURAL_STEERING`, `ENGINEERING_PROPULSION`.
Neural states and gains are uncalibrated model quantities. Propulsion is an
engineering assumption in presentation units/s. No biological gait, muscles,
receptor sign, learning, consciousness or complete-brain emulation is established.
All preceding biological-sign UNKNOWN authorities remain unchanged.

Publication requires Python/browser parity, live causal intervention, unchanged
historical scientific identities, complete event replay, full Python/frontend
quality gates and protected desktop/narrow browser acceptance. No worker or
remote Python service is required unless measured model cost warrants it.

## Recorded local validation

Full Python suite: 1,680 passed, one authenticated integration deselected under
existing policy, two dependency deprecation warnings. Frontend tests, lint/typecheck/build, Ruff and diff checks passed. Browser
checks cover desktop and 390-pixel layouts.
All 401 boundaries of each A/B/C/D control agree within 1e-8; measured maximum
absolute error is 1.6806001035263307e-14. The original Python kernels and historical
artifacts remain byte-identical. D2.2 archive and 74 pinned runtime files were
verified, with the five canonical identities preserved.

Local browser intervention at 2.20 s retained state. At 4.30 s it differed from
no-intervention B by 0.5312467291698886 rad and 0.09032678497504809 presentation
units. An independent Python run with the exported effective event checked all
215 completed intervals; maximum discrepancy was 4.547473508864641e-13 (interval
milliseconds). The actual Three.js body position/heading matched runtime state.
Pause/resume/reset, recalculation, JSON export/import, final contact, missing
source rejection, existing comparison and narrow layout passed without execution
errors. These numbers describe this particular recorded interaction, not every
possible stimulus history.

Available WebGL used SwiftShader: approximately 5 renderer FPS, not a physical-GPU
benchmark. Model computation cost was at most 1.2 ms per capped update of up to
five body intervals; catch-up activated 43 times before the paused sample. The
scientific model still executes 10,000 neural substeps per simulated second.
JavaScript heap samples were about 30.9 MB before and 32.0 MB after the test;
renderer reported 314 geometries/seven textures. Model cost does not justify a
worker in this slice; software rendering determines the observed slow clock.

The nested `body_model` in the event configuration preserves the unchanged v0
plant-only contract. The enclosing runtime config separately specifies neural
steering; the nested plant label does not describe the whole interactive mode.

Session import uses 1e-8 tolerance for computed floating state quantities to
permit cross-engine libm rounding. Configuration, identities, event times,
counters and model labels remain exact; hashes must match the original supplied
content. The recalculated state, never supplied telemetry, resumes simulation.
