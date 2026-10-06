# Phase 33 — Visual System & Scientific Cockpit Redesign

## Outcome and authority

Decision: `REDESIGN_COMPLETE_WITH_DEFERRED_ASSET_LIMITATIONS`.
Phase 33 is presentation-only. The five scenario identifiers, scientific transport
variants and numerical results remain unchanged. No backend, scientific kernel,
model parameter, canonical artifact, actuator, body plant or fly asset changed.
No dependencies were added. No commit or push was performed.

Requirements authority: the committed [Phase 32 audit](frontend_scientific_readability_ux_audit.md)
and [machine-readable audit](frontend_scientific_readability_ux_audit.json).
The inner audit hashes to
`3922ccf48edfcf10fc68b521573805f12a91a46909bdd044d8f704a5ee5c5157`;
the JSON is 72,165 bytes. Both frozen files remain byte-identical.
Initial repository: clean `main == origin/main`,
`ae5a469c7c517226cad413895956a52c32aa76ad`; Phases 23–32 committed.
No repository Stitch exports, mockups or reference images were located. The
audit's restrained immersive scientific direction—not an invented mockup—guided
the design. Browser and React/Next.js skill reviews informed streaming,
code-splitting, immutable playback data, keyboard and responsive verification.

## Design principles and architecture

The application uses the existing Next.js App Router, React, TypeScript and R3F
architecture. `scenario_playback_v1` remains an unchanged typed union; its parsers,
server action, backend adapter and all transport payloads are untouched.

Reading order on desktop: experiment identity/input → dominant viewport with
adjacent current result → compact causal explanation → scientific transport →
essential telemetry → secondary data/provenance. On tablet/mobile the same view
and result come first, followed by transport, causal explanation and telemetry.
Native disclosures avoid stacking all expert information by default.

Reusable presentation components are deliberately small:

- `ScenarioCard`: comparable experiment metadata and accessible route link.
- `CurrentResult`: separate whole-run outcome, selected/final boundary and limits.
- `CausalChain`: typed named stages, states, linear flow or delayed loop return.
- `TelemetryValue`, `EvidenceGrammar`, `UnitHelp`: consistent readout semantics.
- `AuthorityIds`: grouped native disclosures with shortened summary/full ID reveal.
- `ScientificPlaybackLoading` / `ScientificPlaybackUnavailable`: explicit states,
  never fake scientific values, neutral placeholders or fallback visualizations.
- `NeuralMotif`: backend identities/states and exactly six active chemical routes.
- `ScientificTrace`: memoized SVG formatting of backend orientation samples.

The three viewport components remain distinct. World and course views retain
dynamic loading and on-demand R3F rendering. No browser observation, neural,
embodiment or feedback equation was added. The existing playback clock selects
exact floor boundaries for telemetry and interpolates only presentation geometry.

## Implementation tokens

Tokens live in `web/src/app/scenarios.css`: graphite background `#101416`, surface
`#171d20`, raised surface `#20282b`, fine border `#333e42`, primary text `#e1e5e2`,
secondary `#a9b5b4`, muted `#81908f`, stimulus `#ccb18c`, neural `#a3c5b4`, negative
`#b8bed7`, focus `#e0c392`, error `#dfaaa0`. Text/signs—not color alone—identify
R/L, positive/negative and active/neutral states. No neon/glow or animated backdrop.

The existing Arial/Helvetica neutral sans stack remains. Experiment titles use
27–42 px, prominent results 24–27 px, section headings 14–22 px and explanations
13–16 px. Monospace is limited primarily to numeric values, exact units and IDs.
Spacing tokens are 4/8/12/16/24/32 px; fine borders and 4–6 px radii replace a
dashboard of equally weighted rounded cards. Shared navigation/header treatment
remains small; other experiment/morphology routes retain their architecture.

## Scenario patterns

| Scenario | Applied input / scientific horizon | Prominent interpretation / viewport |
| --- | --- | --- |
| `BASELINE_CONTROL` | No effective stimulus / 1.4 ms | Intentional neutral control; quiet specimen, DNp01 at resting coordinate, stationary output. Neutral is not a zero membrane coordinate. |
| `LOOMING_CIRCUIT_VALIDATION` | Prescribed approach / 1.4 ms | Named LC4/LPLC2→DNp01 micro-window; subthreshold and stationary, not behavior-scale escape. |
| `LOOMING_WORLD_EXPERIMENT` | Model-space approach / 40 ms | Exposure 19→26 and DNp01 R -52→-48.733429620244685 mV_eq; still subthreshold, no motor/body output. One authoritative object only. |
| `HORIZONTAL_MOTION_NEURAL_VALIDATION` | Frozen `RIGHT_SIDE_MOTION` / 50 ms | Controlled input panels and identity-resolved eight-node/six-route motif in one view. Right proxy response, left neutral; differential diagnostic only, no body mapping. |
| `EXPLORATORY_COURSE_CONTROL` | Frozen `CLOSED_LOOP_PERTURBATION` / 50 ms | Fixed reference, direct specimen rotation, orientation trace and residual annotation. Counter-motion and decaying motion modes, marginal absolute orientation. |

The library presents class, purpose, duration, input, output scope, canonical
outcome and replay availability with one consistent compact metadata grammar.
Preset descriptions/limits are presented concisely; full scientific limitations
remain available in each cockpit. Availability is not labelled biological validity.

### Current result and scientific grammar

Whole-run summaries do not assert that the current boundary already contains the
final response. At neural boundary zero the target diagnostic is neutral even
though the canonical whole run contains a response. At course boundary zero the
external perturbation has not yet occurred. Final states are preserved, not
automatically reset. Unavailable data has an alert, not a numeric zero; DNp15
event semantics and neural-only body mapping remain explicitly not defined.

DATA means structural/qualitative evidence, MODEL means exploratory contracts,
and RESULT means replayed model states. For course control the qualitative
DNp15/course relationship does not supply physical gain. `Replay verified` means
transport/authority verification, never biological validation.

### Neural motif

R: HSN 10015, HSE 10016, HSS 10023 → DNp15 11215.
L: HSN 10181, HSE 10034, HSS 10419 → DNp15 12069.
Laterality and identity ordering are taken from the validated payload. The SVG
positions are schematic, not morphology. Signed values are backend states;
uniform route strokes do not use structural counts. Source/target IDs remain
visible, with type and side leading the label hierarchy. All seven additional
chemical edges and electrical coupling remain excluded in detailed provenance.
No fly/body, threshold, spike display or fabricated signal particles are added.

### Course trace and orientation

The existing specimen transform remains exactly one declared abstract cycle to
2π render radians; no visual gain was added. The SVG trace is a labelled plot of
every backend orientation sample, with zero reference, perturbation, selected
scientific-time marker and final residual. Its chart coordinate scale is not a
specimen magnification or a biological orientation mapping. Final residual is
`+0.00033277101655776 yaw_orientation_eq`; clipping is 0/500 intervals.

The world-fixed reference is not a target. The model senses visual-motion changes,
not absolute heading error; orientation need not return to zero. Local motion
spectral radius is 0.985517664092702, with orientation eigenvalue 1. The marginal
mode is a model property, not an error. Feedback introduces subsequent
counter-motion; it is not claimed to reduce motion versus an already stationary
open-loop body. No translation, torque, physical yaw or network recurrence.

### Timeline, telemetry, units and provenance

Transport keeps Play/Pause/Reset/Scrub and scientific boundary/time. Annotations
use existing data: neural pulse 0–20 ms/recovery to 50 ms; course external interval
0→1/feedback evolution/end at 50 ms; looming prescribed approach/actual horizon.
No inferred physiological events are added. The six-second presentation clock
remains explicitly different from scientific time.

Primary telemetry pairs R/L and keeps current neural/observation/orientation
values comparable. Clipping and yaw drive are separate readouts. Exact HS states,
raw observation, object/body coordinates and source metadata remain in disclosures.
World event counts are defined LIF outputs; DNp15 does not inherit them.

Exact unit tokens are preserved with plain-language meanings:
`mV_eq`, `world_eq`, `horizontal_motion_eq`, `dimensionless_signed_proxy`,
`dnp15_state_eq`, `yaw_drive_eq`, `yaw_orientation_eq`, `relative_view_eq`.
None is converted into measured physiological/physical units. Detailed authorities
are grouped as dataset/structure, experiment/model contracts, active circuit,
excluded context and units/claim limits. Full hashes remain selectable/revealable.

## UX01–UX17 resolution matrix

| Finding | Status | Implemented remedy | Remaining limitation |
| --- | --- | --- | --- |
| UX01 | RESOLVED | Compact five-row/card library with common metadata grammar. | Dense expert titles remain exact. |
| UX02 | RESOLVED | Adjacent `CurrentResult`, separate whole-run/boundary/limits. | A mobile result necessarily follows the viewport. |
| UX03 | RESOLVED | Input panels plus eight identities/six uniform feedforward routes. | Schematic, not anatomical morphology. |
| UX04 | RESOLVED | Authoritative orientation trace, selected marker and residual annotation. | Specimen rotation remains honestly tiny. |
| UX05 | RESOLVED | Pulse/recovery and perturbation/feedback/end phase labels. | No physiological phase inference. |
| UX06 | IMPROVED | Compact paired primary values, secondary disclosure, separate clipping. | Repeated explanatory status is retained where needed for safety. |
| UX07 | IMPROVED | Plain-language labels, exact tokens and shared glossary. | Expert unit names/precision remain technical. |
| UX08 | RESOLVED | DATA/MODEL/RESULT grammar; LC4/LPLC2 named prominently. | Physiology remains exploratory. |
| UX09 | IMPROVED | Result-first mobile priority, two-column compact data/stages, collapsed details. | Fully expanded scientific provenance remains long by design. |
| UX10 | RESOLVED | Non-color 2 px focus outline for links, buttons, range and summaries. | Not a comprehensive WCAG assessment. |
| UX11 | IMPROVED | 44 px buttons/navigation and 48 px disclosure targets; readable primary labels. | Secondary schematic/metadata text remains compact. |
| UX12 | IMPROVED | Grouped provenance and short/full native hash reveal. | Full scientific authority chain is intentionally retained. |
| UX13 | RESOLVED | Disabled/neutral control copy; recorded-model command language. | Exact backend status-key terminology is retained in details. |
| UX14 | IMPROVED | Projected current-object label, restrained grid, separated scene guide. | Existing specimen shadows/materials still limit leg clarity. |
| UX15 | IMPROVED | Persistent streaming/interactive validation shell with no fake values. | Backend replay performance DEFERRED; no optimization performed. |
| UX16 | RESOLVED | Shared canonical-artifact/no-fallback error with Retry/back. | Authority failures still require source/backend recovery. |
| UX17 | IMPROVED | Framing/environment restraint and preserved visual-asset disclaimer. | Asset replacement/anatomical/material work DEFERRED. |

All 17 findings remain accounted for; the Phase 32 record is not rewritten.

## Browser and accessibility verification

Expert visual review used actual FastAPI canonical playback and the existing
Next.js server, controlled Chromium through `agent-browser`; no scientific mock
data. Desktop 1440×1000, mobile 390×844. All five desktop cockpits, library,
neural/course mobile, a looming mobile spot-check, loading, error and expanded
provenance were reviewed. Temporary PNGs are outside Git; screenshots are UX
evidence only. No user-study or comprehensive WCAG-conformance claim is made.

At desktop the result rail begins around y=333 px alongside the dominant viewport,
rather than the audit's y≈1290–1450 result position. At neural mobile boundary
200 (20 ms), input is off, HS R remains +0.981684 rounded and DNp15 R +0.746469;
the viewport/result clearly preserve neural recovery rather than a fake zero.
Mobile neural height is 2,708 px with details collapsed versus about 4,339 px in
the audit; current result starts around y=932 px. Course collapsed height was
3,186 px; the audit's 5,640 px capture had provenance expanded, so those heights
are not a controlled like-for-like comparison. The new reading priority and
disclosures are directly observable regardless of that comparison.

No horizontal overflow was located in the reviewed 390 px layouts. Buttons
measured 44 px. Keyboard Tab produced a visible solid 2 px navigation outline;
Enter opened provenance and a complete Phase 30 artifact ID. Play advanced,
Pause held boundary 54 during a subsequent wait, Reset restored exact orientation
zero, and Home/End/PageUp scrubbed authoritative states. No client integration.
The final course offset remained after End. Screen-reader/contrast conformance
was not comprehensively evaluated.

Production-server smoke additionally verified a direct restored looming URL:
the correctly titled authority-check shell was visible while canonical replay
was pending, with zero canvases. Expanded course provenance and the full artifact
hash also remained overflow-free at 390 px in the production build.

The actual unavailable-artifact review temporarily set a local backend path to
an absent temporary child—no source file was moved or corrupted. HTTP 503 showed
the no-fallback alert, Retry/back and no canvas/motif. Restoring the canonical
configuration and Retry recovered baseline playback. Pending replay displayed
an authority-check shell, not an empty canvas or model zeros. Route Suspense and
loading files also preserve the shell for restored/direct URLs.

## Scientific regression and tests

Before and after redesign, canonical offline CLI replay passed for Phases 7O,
8C, 13B, corrected 16, 18, 25, 28 and 30. All five canonical payload hashes and
raw serialized transport hashes equal the frozen audit. Full authority records
were validated from repository state, including v1, Phases 24–29 and Phase 31;
Phase 30 preregistration/analysis/artifact replay passed unchanged.

The main scientific authorities remain:

| Authority | Canonical ID |
| --- | --- |
| v1 status | `1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6` |
| Phase 25 artifact | `2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113` |
| Phase 26 context | `04116360164262de5a2572f33e12cc90351869567c3202811807be576f1d03be` |
| Phase 28 artifact | `243914905c17ceb1285c645aa9e9700b602a9e22c8703c9f9ce4c7fe4f7e935d` |
| Phase 29 contract | `9e58649144a4cf3ca7cd913a6cf91dde116524906b0c600dd09f5e66ec5ffaad` |
| Phase 30 artifact | `f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581` |

Eleven new frontend tests use real five-scenario Pydantic payloads, not generated
scientific artifacts. They protect comparable metadata, result boundary semantics,
six-route/eight-identity motif and contact-count independence, truthful trace,
authoritative phases, zero/undefined/unavailable distinctions, units/full IDs,
delayed causal return, responsive/focus/loading structure and immutable frozen
audit/parsers/backend. Existing copy tests were updated to include the separately
promoted result component; science assertions were retained.

Full gates: 1,218 Python tests passed, one configured integration test deselected;
76 frontend tests passed; Ruff check/format, frontend lint/typecheck/production
build and `git diff --check` pass. Existing upstream Three.Clock deprecation and
Python dependency deprecation warnings do not justify migrations in this phase.

## Performance and deferred work

No replay latency optimization, caching or new framework was introduced. Contextual
development observations: baseline validation about 7.2–7.7 s; circuit 7.1 s;
world 17.4 s; neural restored requests about 220–234 ms; course about 744–804 ms.
These are request/log observations under local review, not production benchmarks,
first-paint timings or claimed performance improvements. The loading treatment
addresses uncertainty, not the cost of scientific validation.

The final production build compiled in 1.088 s and TypeScript in 1.252 s.
The generated application has 24 JS chunks, approximately 1.76 MB raw / 505 KB
gzip in aggregate. This is all application chunks, not a per-route transfer
measurement; no baseline bundle delta was captured. Dynamic renderer imports
remain in place; no dependency was added. Brief playback/scrub checks found no
obvious sustained jank; no quantitative FPS/Web Vitals claim is made.

Deferred: anatomical/material fly asset replacement, profiling authoritative
backend replay latency and comprehensive accessibility/usability testing. None
is repaired by scientific tuning or altered transport.

Next bounded action: conduct a newcomer usability/readability validation of the
redesigned five canonical scenarios before further product expansion.
