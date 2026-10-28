# Explicit neural morphology framing — v10.5f-c

The shared eight-body display normalization and fixed overview leave individual
HS bodies relatively small in the initial projection. Focus selected now moves
only the camera and OrbitControls target, on explicit request. Overview restores
position (0, 5.8, 13.5), target (0, 0, 0), Y-up and zoom 1. Selection does not move
the camera. Both actions preserve the session, inspector and history.

The pure fit helper transforms stored source bounds with the existing shared
center/scale. For each of eight box corners relative to its center, camera-frame
coordinates (x,y,z) constrain distance d by:
`d >= |x|/tx - z`, `d >= |y|/ty - z`, and `d + z > near`.
Here ty = tan(fov/2)/zoom * (1-margin), tx = ty * aspect; margin is 0.12 of NDC
half-extent. All corners must also lie before far and within the live controls
limits. The current viewing direction and up define the frame. An invalid
view direction falls back to the canonical overview direction; a degenerate up
frame, invalid input, point bounds or impossible constrained fit fails explicitly.
Planar and linear boxes can be valid. A failure leaves the camera untouched.

Only eight corners are examined on an explicit action. No SWC buffers or
normalization are modified; no per-frame bounds traversal, animation, extra
canvas or neural computation is introduced. Resize updates the existing R3F
projection without refocusing; a subsequent click reads the current camera
aspect. The controls registration is cleaned up at unmount. Context loss disables
actions under the existing reload policy. Loading/error views retain their
existing truthful states. Other bodies may be outside the focused view.

Tests project fitted corners through Three.js for multiple directions, aspects,
zoom, depth and degenerate/error cases; all eight real morphology bounds are
included. UI wiring checks complement pure tests but do not establish browser
interaction acceptance. Canonical full frontend tests, lint, typecheck, build and
protected hash checks passed before the local commit: 405/405 full-suite tests,
4/4 focused framing tests, no skips, ESLint, typecheck and production build.

VISUAL_ACCEPTANCE_DEFERRED. PERFORMANCE_REGRESSION_NOT_VERIFIABLE.
Picking thresholds and drag/click semantics remain unchanged; no browser or FPS
campaign is included in this phase.
