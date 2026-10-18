# Visual Stimulus Comparison v5.1

A matched visual-program counterfactual, reconstructed locally in the browser.
Both conditions apply neural steering. The controlled difference is the external
landmark program, not neural ablation. This feature introduces no neural,
observation, body or boundary-controller equations.

## Reproduction and matching

Open `/visual-lab/arena` → **Visual Stimulus Comparison** → generate synchronized
P versus opposing Q. Alternatively, open **My Experiments** in v5, choose
**Compare Visual Programs** on a saved session, select another saved v5 session,
and generate. Each source is semantically reconstructed before comparison;
imported positions are never authoritative.

The complete initial configuration must match except `initial_preset` and
`initial_controls`. Both modes must be `neural`. Initial body/neural states,
source identities, phases, anchors, physics/engineering parameters, geometry and
clocks remain pinned by the existing v5 validator. Rehashed contradictory inputs
are rejected. Same-session, identical-program, Neural OFF and incompatible pairs
are rejected with the original sessions and prior displayed result preserved.

P and Q independently run the unchanged `IndependentVisualEngine`. Each observes
its own resulting body pose and landmark geometry. External programs may differ;
sensory histories are not forced to match after divergence. Neural timestep is
0.1 ms, body timestep 20 ms, exactly 200 neural substeps per body interval.

The common observation window is `[0, min(P.stop_step, Q.stop_step) × 0.02]`.
At least one completed interval is required. Only applied events with
`step < common stop_step` affect reconstruction; pending requests and later events
are retained in source provenance but not applied or plotted as interventions.
There is no extrapolation. The complete parent identities and original durations
are preserved.

## Timing, metrics and rendering

One playback clock selects recorded 20 ms boundaries. Pose, landmarks, inspector,
markers and cursor share that boundary. Seeking, focus changes and playback do
not run neural dynamics. One GLB represents the focus; P/Q use solid/dashed trails,
distinct marker shapes and explicit labels. Focused landmarks belong only to the
focused world. Positions are not visually magnified.

The existing v4.1 Canvas renderer displays full-resolution telemetry in six lanes:
self-motion, external world-motion, combined input, HS/DNp15 readout, applied
neural/boundary rates, and heading. Each quantity uses a common signed scale across
P/Q. Geometric A/R and B/L proxies are not measured receptive fields; combined
input uses the existing observer's clipping, not an assumed linear biological sum.
Curves are cached; the scientific cursor does not redraw them.

Pose is boundary-valued. A neural readout/rate plotted at boundary `k+1` summarizes
the completed neural interval beginning at `k`. At time zero those aggregates are
unavailable. The v5 reference's outgoing-interval readout maximum at **21.50 s**
is therefore available at **21.52 s** in this inspector. Both times are recorded;
no reference or event was shifted retroactively.

Current spatial separation is Euclidean X/Z endpoint separation. Current heading
difference is signed wrapped P−Q in ±π. Whole-window maxima use all recorded
boundaries, including the final boundary; heading maximum uses absolute wrapped
separation. Traveled-distance difference is a separate quantity. Readout maxima
use completed interval aggregates, with first occurrence for ties. Contact and
recovery histories are independently computed, not synchronized between worlds.

## Verified reference case

Existing v5 Python manifest:
`docs/science/independent_visual_stimuli_v5_reference.json`, reference identity
`01b1758cb594c2dbad5740eb1bf982495e53deaa61c4b951a738c92a6fc9ac79`.
The selected fixture raw SHA-256 remains
`ef01f9854bfda1ddb044b7cfc521e4e06f763cb65c16fd6d3e5ea34b6ea74c7a`.
Parity tolerance remains `1e-8`; no solver or tolerance was changed.

For the full 30 s synchronized/opposing pair:

| Quantity | Value | Scientific time |
|---|---:|---:|
| Maximum spatial separation | 0.03380208824 presentation units | 22.64 s |
| Maximum absolute wrapped heading separation | 0.10005759499 rad | 20.72 s |
| Maximum absolute readout difference | 0.005892145287 yaw_drive_eq | 21.52 s completed / 21.50 s interval start |
| Final spatial separation | 0.008069365727 presentation units | 30 s |
| Traveled-distance P−Q | 0.003802566646 presentation units | 30 s |

Each condition has three contacts and three recoveries. These are model results,
not biological visual preferences or evidence that greater distance is better
navigation. Reference results were checked before assertions were added.

## Provenance, library and portability

`visual_stimulus_comparison_v5_1` stores two compact authoritative parent input
contracts, verified shared configuration and source hashes, controlled-difference
declaration, common window, recomputed tracks/metrics, configuration/result hashes
and logical artifact identity. Computation timings are excluded from scientific
identity. Comparison import recalculates both parents and tracks; recalculated
superficial hashes do not authorize contradictory output. Hashes detect
corruption; they do not authenticate an author.

Comparisons are in memory and exportable as JSON, not persisted as duplicate
histories in IndexedDB. Original sessions remain unchanged. Library selection uses
stable record UUIDs; portable comparison provenance uses scientific session IDs.
Opening a parent rechecks its identity. A deleted parent cannot be reopened or
regenerated from the library; an already reconstructed comparison remains
inspectable and its exported inputs remain reproducible. No storage migration or
cascade deletion is introduced. Browser libraries remain origin-specific.

## Validation and limits

Run the canonical frontend lint, typecheck, tests and production build. The added
tests cover selected independent Python fixtures, controls, exact clocks,
common-prefix/event boundaries, extrema and timestamps, shared scales, preserved
sources, deterministic reconstruction and semantic tampering. Browser acceptance
must also check actual Three.js marker/body/landmark transforms, playback,
focus/seek, saved-session reconstruction, original-session return, import rejection,
reload persistence and narrow layout. Build success alone is not acceptance.

No Python model is modified. Preserve the published 1707-test Python baseline and
run focused v5/moving-stimulus, HS/DNp15 and D2.2 integrity checks. Frozen source
and external artifact checks remain required. Bulk browser telemetry and test
screenshots belong outside Git in the science-work validation-evidence directory.

Classification: `MATCHED_VISUAL_STIMULUS_COUNTERFACTUAL`,
`CONNECTOME_INFORMED_NEURAL_STEERING`, `ENGINEERING_PROPULSION`,
`ENGINEERING_BOUNDARY_RECOVERY`, `RECONSTRUCTED_BROWSER_MODEL_SIMULATION`.
The selected structural circuit and proxy response do not validate a complete fly
visual system, physiological optomotor magnitude, muscle-driven gait, preference,
learning, or whole-connectome locomotion. The small differences are shown at their
actual scale. No LLM controls the fly.

### Implementation verification record

The final frontend gate contains **227 passing tests**, including ten new matched
comparison tests. Lint, TypeScript, production build and diff checks pass. Focused
Python reference/HS-DNp15/runtime-bundle checks: **63 passed**, two existing
dependency deprecation warnings. Ruff check and format check pass. The unchanged
full Python baseline is **1707 passed, one policy deselection**, preserved with
published v5 evidence; it was not unnecessarily rerun.

Independent verification of all completed frames from a local browser export of
both full 30 s tracks compared 105,022 numerical values per condition against the
unchanged Python reference. Maximum absolute error was `3.637978807091713e-12`
(interval-duration floating arithmetic), below `1e-8`. Actual user-intervention
sessions were also reconstructed and checked independently at their common
recorded prefix. No tolerances or authoritative fixtures were changed.

The browser acceptance script checks numerical inspector values against exported
telemetry and actual Three.js transforms, not screenshots alone. It also checks
zero cached-curve redraws during seeking, focus/time continuity, transport/end,
parent preservation, semantic rejection of rehashed output, library reload and
historical ON/OFF functionality. Logs, parity reports, exports and screenshots
are external under `../neurofly-science/work/visual-stimulus-comparison-v5-1/`.
Protected deployment acceptance is recorded there against the exact published
commit; no deployment credentials or browser authentication state are retained.
