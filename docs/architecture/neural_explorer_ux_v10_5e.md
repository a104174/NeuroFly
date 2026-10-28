# Neural explorer presentation v10.5e

Simple and Detailed views consume the same validated interval-start proxy values.
The whole skeleton uses turquoise for positive, amber for negative, grey for zero
and opacity proportional to the absolute value capped at one; selection adds
brightness. This is a display encoding, not a biological measurement or a
branch-level activation. The recent chart reads the existing 256-sample telemetry
ring, updated roughly every ten ticks, using real interval-start timestamps. It
connects only consecutive valid intervals, and resets with the session. It is a
rolling window rather than a complete recording. Pause preserves it.

MaleCNS structural contact counts describe anatomy, not model gains. The HS to
DNp15 computational relationship and neural yaw motor projection are separately
identified; the boundary response and propulsion are engineering rules. A
selected cell does not independently explain a movement. Source identities,
coordinates and attribution are documented in the v10.5d architecture record.

## Implementation and acceptance checkpoint

Implementation status: `NEUROFLY_V10_5E_IMPLEMENTED`. Automated validation
previously passed: 399/399 frontend tests, 32/32 focused tests, ESLint,
typecheck, production build, and `git diff --check`.

Acceptance status remains `NEUROFLY_V10_5E_UX_PARTIAL`. Limited manual desktop
observations confirmed that the 3D view rendered and that a selected HS
structure and its computational details/history were displayed. Complete
selection and lifecycle interaction coverage, responsive visual checks at
390 px and 320 px, and comparable V10.5E performance measurements remain
deferred. Chrome reported the page hidden during the attempted interaction, so
the application paused under its existing visibility policy. No valid V10.5E
FPS regression result exists; the earlier V10.5D FPS observation is not a
V10.5E measurement. The user elected to publish this implementation and
continue development while these acceptance checks remain open.
