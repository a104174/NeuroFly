# Neural Response Timeline v4.1

This presentation layer inspects the existing Moving Visual Stimuli v4 model.
Baseline: `9e7e0e5bc908233f36927633ed591fd8cb825caa`. It adds no neural,
observation, propulsion or boundary-policy equation and changes no session schema.
The v4 engine exposes a defensive copy of its already recorded completed intervals.
IndexedDB still stores validated inputs, not a second authoritative signal history.
Saved/imported data enter through the existing semantic reconstruction validator;
a recomputed hash alone does not authorize fabricated signal values.

## Scientific time contract

The clocks remain 0.1 ms neural, 20 ms body, 200 neural updates per interval.
At body boundary n, v4 observes the completed body/world interval n−1 → n.
That observation is held while the neural solver advances n → n+1. The mean
`yaw_drive_eq` readout and applied angular rates for this interval are available
only when boundary n+1 has completed.

The timeline places **all interval-derived signals at their completion boundary**
n+1. Its inspector explicitly reports the observation's earlier availability time
n. Pose, world geometry, HS/DNp15 states and contact correspond to boundary n+1;
readout, input and rates describe the interval just completed. No outgoing
aggregate is exposed before it has been computed. At time zero these interval
signals are unavailable, not invented zeros. The first observation is unavailable
at 20 ms because no completed body/world interval existed at the initial boundary.

An event effective at boundary n changes world evolution starting there without
moving its position instantaneously. The observation used during n → n+1 still
reflects the earlier world interval. The changed world motion first enters the
observation at n+1, and its corresponding neural aggregate becomes available at
n+2. Event markers remain at n, not at the later response timestamp.

Every cursor position snaps down to a completed 20 ms boundary. This is sample
inspection, not interpolation of unrecorded neural states. Moving the cursor
pauses playback, changes the displayed fly/world/inspector together, and never
runs the solver or rewinds the preserved engine. Play returns to the latest
computed boundary and resumes that live state; “Voltar ao último boundary” does
so without advancing. Reset clears both the engine and timeline. Comparison
playback retains its previously published interval/pose conventions; the new
instrument is attached to the original v4 session, not to a different clock.

## Signal contract

- Self-motion R/L: `self_motion_raw`, signed normalized geometric proxy, computed
  with previous world landmarks fixed as the body changes pose.
- External motion R/L: `external_motion_raw`, additional bearing change evaluated
  at the body's final pose. The attribution is ordered, not two independent
  physiological channels. Raw normalization is the existing 50 ms convention.
- Combined R/L: the actual `right`/`left` input, clipped to [−1,1]. Clipped
  components cannot be added to reconstruct it.
- Neural readout: `mean_yaw_drive_eq`, the actual interval average from the HS R
  10015/10016/10023 and L 10034/10181/10419 → DNp15 11215/12069 model.
- Applied angular rates: `boundary_summary.neural_omega` and `.omega`, rad/s,
  displayed separately. OFF preserves the raw neural computation while applying
  exactly zero neural angular contribution. Boundary steering is engineering.
- Context: unwrapped body heading in rad, in its own lane. This is not wrapped
  angular separation and does not imply biological frequency or muscle action.

The SVG has five aligned lanes, explicit signed scales, zero references, distinct
colors and line patterns, event tooltips and boundary-contact markers. Scales
are numeric in original model units, never per-signal amplitude normalization.
Paths preserve all completed samples, use steps without smoothing, and are
memoized independently of cursor movement. The instrument is collapsible and
uses no chart dependency, second GLB, neural-substep React update or chart clock.

## Validation and interpretation

Focused tests compare selected plotted values against the existing independent
Python v4 fixture at the unchanged 1e-8 tolerance. They check interval availability,
initial missing signals, signs, readout/rate separation, cursor pose/world/neural
states, intervention latency, OFF semantics, defensive-copy isolation, deterministic
reconstruction and rejection of recomputed-hash contradictory telemetry.
Historical source/artifact identities and numerical models remain unchanged.
Browser checks additionally compare actual Three.js transforms, inspector values
and timeline samples with exported, semantically validated session telemetry;
save/reload, pause/resume, reset, comparison and narrow layout are exercised.

These are uncalibrated geometric and neural-model quantities. They are not
measured retinal channels, biological firing rates, muscle activation or
physiological wall avoidance. Forward propulsion and boundary recovery remain
engineering assumptions. The chart creates no new scientific evidence about
biological locomotion; it makes the existing computational causal chain inspectable.

Pre-publication gates passed: 201 frontend tests, frontend lint/typecheck/production
build, Ruff lint/format and diff checks. With no Python model changes, the existing
1702-test full baseline was supplemented by 192 targeted Python checks rather
than another full scientific sweep. All 74 frozen D2.2 files and the raw external
DNg100 dynamics/convergence, motor-input/response and Planar SHADOW_ONLY files
retain their published hashes. The existing frontend parity fixtures also pass.

An isolated 1501-boundary profile measured ~12.8 ms for a one-time full defensive
copy, ~0.042 ms for a live five-interval incremental copy, ~0.319 ms for the full
view-model, and ~0.0083 ms per historical state lookup. These are Node timings,
not renderer FPS measurements. Browser rendering remains hardware dependent;
SwiftShader results must not be presented as physical-GPU performance.
Saving/exporting while inspecting history preserves the complete live session
prefix; seeking does not truncate or create a new experimental run.

Local production-browser acceptance passed with an actual 8.70 s prefix: stop at
2.10 s, reverse at 3.30 s, 87000 neural substeps, one contact and one recovery.
Ten selected boundaries (including zero, initial missing input, wall contact and
post-contact history) matched exported telemetry and actual Three.js body/world
transforms. The timeline readout and angular rates matched the live inspector.
Import, save/reload, ON/OFF comparison, resume and reset passed on desktop and
390 px viewport, with no runtime errors. SwiftShader remained approximately
4 FPS; diagnostic-transform sampling itself updates at 1 Hz and was awaited
separately from scientific cursor/inspector updates. Browser evidence is external
to Git; the protected deployment is verified independently after publication.
