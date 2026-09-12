# Immersive 3D playback foundation (Phase 5B)

Phase 5B adds a presentation-only React Three Fiber surface to an existing
experiment detail page. The persisted Phase 4A timeline remains the sole
scientific input. The browser does not execute `ExperimentRunner`, encode a
stimulus, step the LIF model, or create neural values.

## Architecture and client boundary

```text
Next.js experiment page (server component)
    -> validated ExperimentSummary + ExperimentTimeline
    -> PlaybackWorkspace (client playback clock and controls)
    -> pure timeline lookup / SceneState derivation
    -> dynamically loaded PlaybackCanvas
    -> React Three Fiber / Three.js presentation
```

The existing server page performs the same parallel summary/timeline HTTP
fetches as Phase 5A and passes the validated JSON-safe timeline into the
client boundary. The Canvas neither fetches data nor imports scientific
Python code. It is dynamically loaded with server-side rendering disabled so
WebGL remains confined to the browser.

## Playback clock and render time

The playback clock stores absolute simulation time in milliseconds, a playing
flag, and a presentation playback rate. Browser `requestAnimationFrame`
timestamps provide elapsed wall-clock milliseconds. Progression is:

```text
next_playback_time_ms =
    current_playback_time_ms + elapsed_wall_time_ms * playback_rate
```

The result is clamped to the persisted timeline's `start_ms` and `end_ms`.
Reaching `end_ms` pauses playback and preserves the final state. Reset returns
to `start_ms`; seeking clamps to the same interval. The fixed rates 0.25x,
0.5x, 1x, 2x, and 4x are playback presentation rates, not neural-simulation
or biological-speed parameters.

Render frequency is independent of neural `dt_ms`. There is no frame counter,
no “one render frame equals one neural step” rule, and no browser model step.
Every rendered scientific value is selected from the timeline using the
current playback time.

## Exact timeline lookup

Phase 4A provides both time bases explicitly:

- `times_ms` identifies persisted state boundaries. DNp01 membrane and
  filtered-synaptic values use the latest boundary at or before playback time.
- `step_times_ms` identifies the starts of intervals governed by
  `step_values_apply_on_[t_n,t_n+dt)`. Theta, angular-expansion velocity,
  LC4/LPLC2 normalized features, and LC4/LPLC2 drives use the interval
  containing playback time.

Both selections use deterministic floor lookup. At exactly `end_ms`, the
state boundary is the final boundary and interval quantities retain the final
valid interval. Requests outside the persisted bounds are clamped. No
membrane, synaptic, feature, drive, theta, or spike value is interpolated,
shifted, smoothed, or resampled.

## Scene-state derivation

`web/src/lib/playback.ts` contains pure, WebGL-independent functions for the
clock, lookup, and `ExperimentSceneState`. The scene state retains the exact
selected time/index and values for:

- theta and angular-expansion velocity;
- LC4 normalized feature and drive;
- LPLC2 normalized feature and drive;
- DNp01 body 10001 membrane/synaptic state and exact-boundary spike flag;
- DNp01 body 10010 membrane/synaptic state and exact-boundary spike flag.

An exact-boundary spike flag is true only when a persisted spike timestamp is
equal to the selected state-boundary time. The scene does not synthesize a
spike waveform or biological pulse duration. Its presentation ring remains
visible only while that persisted boundary is the current floor-selected
state; this hold is a browser visibility convention, not spike shape.

## Scientific data and presentation assumptions

Persisted scientific values are retained unchanged in scene state and the 2D
overlay. The following visual properties are explicitly presentation-only:

- the procedural fly's dimensions and position;
- camera position, field of view, grid, fog, and lighting;
- the looming proxy's mesh scale and scene position;
- colors, emissive intensity, and indicator sizes;
- per-run contrast normalization used for DNp01 indicator brightness.

The looming object is an angular-size proxy. Its bounded presentation level is
`abs(theta_rad)` relative to the largest persisted absolute theta in that run.
This does not reconstruct physical object distance or repeat the
`LoomingStimulus` equations. LC4 and LPLC2 indicator intensity uses their
already persisted bounded normalized features. Each DNp01 indicator uses a
bounded per-trace contrast mapping from its persisted filtered-synaptic state;
brightness is not firing probability or physiological efficacy.

## Scene and accessibility

The first scene contains a fixed camera, minimal lights, a reference grid, a
stationary procedural fly-like placeholder, one looming proxy, and four
abstract pathway indicators. LC4, LPLC2, DNp01 10001, and DNp01 10010 remain
visually and textually distinct. The 2D overlay exposes current simulation
time, selected boundary/interval times, playback status, exact current values,
and `NOT_EVALUATED` empirical status.

The 3D view contains no unique scientific information: the existing readable
summary and timeline inspector remain authoritative. Controls are ordinary
keyboard-accessible buttons, a labelled range input, and a labelled playback
rate select. WebGL detection and a local render error boundary show “3D
playback is unavailable in this browser” without removing the experiment
summary.

## Explicit limitations and future boundaries

The placeholder fly is not an anatomical reconstruction. Its wings remain
static, and DNp01 activity does not make it jump, turn, fly, or otherwise
behave. A future motor phase must define and validate:

```text
neural output -> motor command -> body/environment update
```

before activity can drive movement. A future controlled Blender pipeline may
replace the primitive mesh with an optimized fly asset and, only where
scientifically justified, rigging or animation. No Blender file, final asset,
connectome geometry, physics engine, behavior, Level C, or empirical
validation is introduced in Phase 5B.
