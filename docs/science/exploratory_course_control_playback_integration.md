# Phase 31 — Exploratory Course-Control Playback & Product Integration

The fifth canonical scenario, `EXPLORATORY_COURSE_CONTROL`, presents the frozen
Phase 30 `CLOSED_LOOP_PERTURBATION` result. Its scientific role is
`EXPLORATORY_CLOSED_LOOP_MODEL`. It does not modify any scientific kernel,
preregistration, artifact, or existing scenario result.

## Repository and scientific authorities

The initial repository gate was clean `main == origin/main` at
`2e53f9ecb51374faa7d540222c98494b992d8af6`. Phases 23–30 were committed.
The following identities were verified from the actual repository and offline
replay, not copied into a replacement experiment:

| Authority | Canonical ID |
| --- | --- |
| v1 scientific status | `1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6` |
| Phase 24 selection | `435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41` |
| Phase 25 neural preregistration | `371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074` |
| Phase 25 neural artifact | `2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113` |
| Phase 26 context audit | `04116360164262de5a2572f33e12cc90351869567c3202811807be576f1d03be` |
| Phase 28 evidence gate | `42d46ef3e5deed0c36da518cc1523cfe3d0978e5cbed2aac85a9738fcdeadf2f` |
| Phase 28 orientation preregistration | `1be0f6364070a5a5536f4c772bd47abb3be2f08357b439a51e03f034f8b2a654` |
| Phase 28 orientation artifact | `243914905c17ceb1285c645aa9e9700b602a9e22c8703c9f9ce4c7fe4f7e935d` |
| Phase 29 observation contract | `9e58649144a4cf3ca7cd913a6cf91dde116524906b0c600dd09f5e66ec5ffaad` |
| Phase 30 preregistration | `efc27a18e1d19119b8eebc5d0f8b91e61a47337dbb9f60e2518fabc42672cd0f` |
| Phase 30 analytical result | `a8e82f1561df6deb05216d795f7d61067c9338fefffb5cb7d2a415f6a3464586` |
| Phase 30 artifact | `f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581` |
| Phase 30 config | `a87bbae9566430d87f2f7893001d4824ff8006bfcb979510af352cab2f7c7df3` |
| Phase 30 result | `3837bae425878c6b4696cd561d7465dd5d5ce073fae56fa4746a1251e0ba5ae9` |

The Phase 27 integration and neural-only presentation remain unchanged in
meaning. The Phase 30 loader validates its source document identities,
analytical authority, source artifacts, and complete numerical replay before
the new adapter serves data. No canonical artifact is generated or overwritten.

## Transport architecture and compatibility

The existing GET catalog and `/api/v1/scenarios/{scenario_id}/playback` routes
remain the only scenario endpoints. `scenario_playback_v1` gains an additive,
explicit Pydantic/TypeScript variant with
`presentation_kind = EXPLORATORY_CLOSED_LOOP_MODEL`. The old world and
neural-only variants have no new fields or changed serialization. There is no
destructive migration, generic scientific blob, or fake body-state structure.

`load_course_playback` performs Phase 30 replay and selects exactly
`CLOSED_LOOP_PERTURBATION`. Selection is justified by its complete causal loop,
not by visual amplitude. It copies scientific values into a reduced typed DTO.
Provenance and fixed world metadata occur once rather than at every boundary.
The frontend validates identity order, topology, units, boundary grid, delayed
observation intervals, status exclusions and readout consistency before use.

| Data | Playback semantics |
| --- | --- |
| Boundary | 501 exact states, 0–50 ms, dt 0.1 ms |
| World reference | `WORLD_FIXED_HEADING_ZERO`, heading 0, abstract period 1; not a goal |
| Orientation/view | `yaw_orientation_eq`, previous orientation, `relative_view_eq` |
| Observation | Completed interval, raw view motion, unclipped descriptor, bounded global descriptor, clipping flag |
| Inputs | Separate R/L `horizontal_motion_eq` |
| Sources | Six signed HS states, identity order from the scientific result |
| Targets | DNp15 11215 R and 12069 L, `dnp15_state_eq` |
| Differential | R−L bilateral neural-state diagnostic, not inherently a body command |
| Embodiment | Explicit Phase 28 exploratory `yaw_drive_eq` |
| Perturbation | Outgoing external increment, or null when no outgoing interval remains |
| Exclusions | Translation NOT_MODELLED; events NOT_DEFINED; recurrence/electrical coupling inactive |

At boundary zero, observation and previous orientation are null: no interval
has yet completed. Later observations describe interval n−1→n and are latched
for the next neural interval. The final boundary is a readout/observation,
not an additional scientific tick. No client computation creates a new
observation from a rendered orientation.

## Canonical result and interpretation

The externally imposed +0.001 eq orientation increment occurs in interval
0→1. The model then generates neural-mediated counter-motion, followed by small
decaying reversals. Final orientation is +0.00033277101655776 eq. Observation
clipping is 0/500 intervals, duration 0 ms.

Local motion spectral radius is 0.985517664092702; the orientation-offset
eigenvalue is 1. The UI labels this **MARGINAL ORIENTATION MODE**, a model
property rather than a warning. It explains that motion-only observation
contains no absolute heading-error signal. Activity can decay while orientation
remains offset. No return to an original/desired heading is promised.

The open-loop control is already stationary after its imposed step. Therefore
the correct comparison is that neural feedback introduces subsequent
counter-motion—not that it reduces motion relative to that stationary control.

## Presentation and controls

The viewport combines a fixed-position visual specimen, world-fixed reference,
body orientation marker and abstract stripe cue. The specimen remains a visual
asset, not MaleCNS morphology or a biomechanical plant. Stripes illustrate
relative view in an inset; they are not calibrated retinal imagery.

Presentation uses exactly `render_rotation = yaw_orientation_eq / period_eq × 2π`
around Three.js +Y, with native specimen forward aligned to +Z. One abstract
cycle corresponds to one display revolution. There is no visual multiplier or
gain chosen for readability. The small canonical displacement stays small.
The world-reference marker uses the same geometric coordinate convention and
is independent of body orientation.

Render-only interpolation uses neighboring authoritative orientations and
relative-view coordinates. Telemetry selects an exact boundary. Rendering
cannot integrate neural/orientation state, alter clipping, or feed back into
science. The 50 ms horizon is presented over the existing 6 s playback clock.

Play/Pause/Reset/Scrub reuse the shared transport. Pause preserves the cursor;
scrub selects deterministic states without a client integrator; Reset restores
boundary zero and presentation orientation zero. At the end the residual offset
is preserved until the user explicitly resets or starts playback again.

The delayed causal-loop panel is World/View → Motion Observation → HS Sources
→ DNp15 → Orientation → Next View ↺. Newcomer copy explains the perturbation,
neural response, exploratory counter-motion and absent heading-error sensor.
Primary telemetry displays scientific time, model-space orientation, R/L input,
R/L DNp15, neural differential, yaw drive and clipping. Expandable panels retain
all six HS identities, raw observation and full authority/analysis provenance.
R/L and signed values have text labels; color is never the only distinction.

Six chemical routes remain active. Structural counts appear only in provenance.
The seven verified context edges and electrical coupling are explicitly excluded
from active dynamics; no recurrent signal paths are displayed.

## Errors and scientific claim budget

Missing/corrupt artifacts, identity mismatch or invalid analytical authority
produce existing typed `scenario_unavailable` HTTP 503 errors. Unsupported IDs
remain HTTP 404. Malformed transport fails frontend validation. The UI clears
old results before loading and displays:

> Experiment playback unavailable. The canonical scientific artifact could not
> be validated. No synthetic fallback has been substituted.

No fabricated scientific trajectory or orientation animation is substituted.
WebGL/asset presentation failures may leave authoritative telemetry available;
this is distinct from unavailable scientific data. Existing specimen-loading
presentation behavior does not generate scientific state.

Allowed: deterministic exploratory model-space course-control playback;
connectome-structured neural mediation; evidence-gated exploratory orientation;
motion-related decay and residual offset in this finite frozen experiment.

Forbidden: biological steering, calibrated yaw/optic flow, navigation, heading
restoration, torque, biomechanics, physical turn-rate prediction, complete
HS/DNp15 network, or contact-count-derived efficacy. No translation, spikes,
recurrence, electrical coupling, heading sensor, tuning or new condition editor
is introduced.

## Verification and performance

Historical CLI replays before and after integration passed unchanged for
Phases 7O, 8C, 13B, corrected 16, 18, 25, 28 and 30. Their authority/result
identities and the four old playback canonical hashes match. The old adapter
loaded from committed HEAD also produced byte-identical serialized payloads;
focused tests pin both canonical and transport-byte identities.

| Existing payload | SHA-256 of unchanged serialized transport bytes |
| --- | --- |
| BASELINE_CONTROL | `475b550734133d6357fd5f8914549d9d1c5469ccfeaca8e1fb229311a9db5380` |
| LOOMING_CIRCUIT_VALIDATION | `743e475ec7ad41e4cb80492688491607a19ef31ce3389ddddf6281ee9f8d8510` |
| LOOMING_WORLD_EXPERIMENT | `cd9755131ecf6eb39ec26136f8d4bdadc1e65573ebfd387c4bbac25d3e53a060` |
| HORIZONTAL_MOTION_NEURAL_VALIDATION | `2d61227727a0708ed5635a0054c729f9664db4e6b883edfac417573eddaafa6b` |

One local measurement: scientific replay/validation 641.18 ms; adapter-only
conversion 4.17 ms (measured over the already validated payload, without adding
production caching). Transport is 453,262 UTF-8 bytes versus 4,354,003 bytes for
the source result file, roughly 10.4%. New transport-byte SHA-256:
`ff1d4bfd9e0ba312155d1ddea76f15f0f4aba5048c4ffb3bcaf52f23e5a67e63`.
These are machine-dependent timing observations, not performance guarantees.

Browser smoke at 1440×1000 and 390×844 verified catalog/navigation, real API
playback, Play/Pause, final scrub, exact reset, residual offset, expanded
provenance, no horizontal overflow, unavailable-data state and successful retry.
The Phase 27 scenario still presents neural-only playback. No framework/error
overlay or browser runtime error occurred. R3F emits the existing upstream
Three.Clock deprecation warning; no dependency migration is part of this phase.

Focused backend tests cover exact source-value mapping, typed failures,
determinism, identity/topology, units/exclusions, real HTTP serialization and
all four old payload identities. Frontend tests consume real Pydantic output
and protect variant parity, invalid payload rejection, stateless rendering,
controls, scientific language, error handling and residual state.

Quality gates passed: full Python suite 1,205 tests, one configured integration
test deselected, plus the later-added transport-byte regression in a successful
9-test focused rerun; 65 frontend tests; Ruff check/format; frontend lint,
typecheck and production build; `git diff --check`. The only Python warnings
were the existing Starlette/httpx and anyio deprecations. Browser and React
review skills guided end-to-end checking, lazy 3D loading and stateless
presentation; no wider architecture rewrite was required.

No dataset, scientific artifact, API parameter editor or runtime scientific
model was changed. Generated artifacts remain ignored. No commit/push.
Phase 31 decision: `EXPLORATORY_COURSE_CONTROL_SCENARIO_INTEGRATION_COMPLETE`.
Phase 31 status: `PASS`.

Next bounded action: conduct a five-scenario scientific-readability review
before considering a separately scoped UI redesign.
