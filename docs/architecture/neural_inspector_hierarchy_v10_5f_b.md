# Neural Inspector information hierarchy — v10.5f-b

The inspector previously led with the structure list and gave identity, current
activity and metadata similar emphasis. It now leads with the selected type,
side, exact body ID and model-state field, followed by a prominent signed,
dimensionless computational value. Missing and non-finite values are unavailable.
The same primary component is used in Simple and Detailed presentations.

Recent history follows the current state, names the selected body and uses a
120 px display height. Its existing coordinates, clipping range, sample values,
interval-start times and gap rules are unchanged. Simple retains a brief source
and model qualification; Detailed retains morphology metadata, structural routes
and computational/engineering distinctions. Selection controls remain in the
same inspector, below the selected entity. Existing help and provenance remain.

No new selection/history state, canvas, timers or simulation calculations were
introduced. The V10.5F-A container layout, morphology and neural solver remain
unchanged. Focused rendering tests cover identity, sign, unavailable values,
history labels and missing-interval gaps; the full frontend suite, lint,
typecheck and production build are the automated acceptance gates. Validation
passed: 401/401 frontend tests (including two new rendering tests), ESLint,
typecheck, production build and git diff --check.

VISUAL_ACCEPTANCE_DEFERRED. PERFORMANCE_REGRESSION_NOT_VERIFIABLE.
Desktop/mobile interaction and comparative FPS have not been measured in this
phase. A next small slice can assess morphology framing within the existing
viewer without changing source geometry or scientific values.
