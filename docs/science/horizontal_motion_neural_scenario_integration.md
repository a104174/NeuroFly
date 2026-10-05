# Phase 27 — Horizontal Motion Neural Scenario Integration

## Scientific role and frozen boundary

`HORIZONTAL_MOTION_NEURAL_VALIDATION` exposes the frozen Phase 25
HSN/HSE/HSS → bilateral DNp15 chemical feedforward experiment through the
existing scenario catalog and playback endpoint. It is `NEURAL_ONLY_VALIDATION`,
not an embodied world experiment or a demonstration of steering/navigation.
No scientific parameters, model equations, conditions, identities or artifacts
are changed. The three v1 scenarios retain their identifiers and scientific
semantics.

The one product condition is **RIGHT_SIDE_MOTION**. Its unilateral descriptor
makes input, identity-resolved source response and bilateral continuous readout
easy to distinguish. This is a presentation choice among existing preregistered
conditions, not a parameter selection or new scientific execution. Other
conditions remain available through Phase 25 artifact inspection/replay.

## Authorities

| Authority | Canonical identity |
| --- | --- |
| v1 scientific status | `1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6` |
| Phase 24 selection | `435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41` |
| Phase 25 preregistration | `371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074` |
| Phase 25 canonical artifact | `2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113` |
| Phase 25 config | `8ffc6263d1a70948d9a69ffa0ff066c9dcbb894d5766b72520e209ace60b452d` |
| Phase 25 result | `35b9bf6bb72f2d92522df25de020cc5e3d369ec0d257997d8cd7746a55e54864` |
| Phase 26 context audit | `04116360164262de5a2572f33e12cc90351869567c3202811807be576f1d03be` |

Phase 26 constrains interpretation, not execution: its decision remains
`FEEDFORWARD_MOTIF_REMAINS_CURRENT_VALIDATED_BOUNDARY`. Seven additional
chemical edges and broader electrical context remain excluded. No new recurrent
operator, electrical substitute, spikes, motor output or body mapping exists.

## Backend transport and compatibility

The existing `GET /api/v1/scenarios` returns four presets; the existing
`GET /api/v1/scenarios/{scenario_id}/playback` serves the new scenario.
`scenario_playback_v1` gains an explicit typed neural-only variant, identified
by `presentation_kind: NEURAL_ONLY_VALIDATION`. The old world result shape is
unchanged; it is not weakened by making its required world fields nullable.
Existing clients that only recognize three scenario kinds fail closed rather
than interpreting neural data as a world scenario. No destructive migration or
parallel endpoint is introduced.

Pydantic and TypeScript explicitly describe the same variant. The adapter
validates Phase 26's committed audit hash and numerically replays the canonical
Phase 25 artifact with its existing offline validator before serving data.
It copies the selected run's time, input descriptors, six source states, two
target states and persisted R−L diagnostic without recomputing neural dynamics
in presentation code. The transport run identity hashes the source artifact ID
and selected condition ID; it is not a new scientific result artifact.

Identity order is preserved, not inferred from morphology:

| Source body | Type | Side | Active target |
| --- | --- | --- | --- |
| 10015 | HSN | R | 11215 DNp15 R |
| 10016 | HSE | R | 11215 DNp15 R |
| 10023 | HSS | R | 11215 DNp15 R |
| 10034 | HSE | L | 12069 DNp15 L |
| 10181 | HSN | L | 12069 DNp15 L |
| 10419 | HSS | L | 12069 DNp15 L |

All six active routes and seven excluded routes remain typed provenance.
Structural counts are displayed only as contacts, never as efficacy or rendered
signal weights. Source identities and sides come from the canonical artifact.

No body/object/actuator/DNp01 fields or spike counts are populated with fake
zeros. `event_semantics` and `body_mapping` are `NOT_DEFINED`. Missing, corrupt
or mismatched authority produces the existing typed HTTP 503
`scenario_unavailable` error; unsupported scenario IDs produce HTTP 404.
The client renders an explicit error, never a substitute trajectory.

## Product presentation and time

The existing scenario routes, Run action, Play/Pause/Reset/Scrub controls and
six-second presentation clock are reused. The scientific horizon stays
**50 ms**, dt **0.1 ms**, with **501 boundaries**. The client selects exact
boundary data for explanation and telemetry; only the display stripe phase
interpolates between neighboring backend samples. Reset selects boundary zero;
scrubbing is stateless and cannot retain a hidden neural simulation.

The backend adds a declared render-only stripe phase `min(t, 20 ms) / 10 ms`.
It freezes at pulse end and never enters the scientific model. Two labelled
L/R panels illustrate `horizontal_motion_eq`; they are not calibrated optic
flow or retinal imagery. Demand rendering has no autonomous stimulus loop.
An orthographic camera fits both panels on compact viewports. WebGL failure
leaves authoritative controls and telemetry available.

This view intentionally contains **no simulated fly/body**. It avoids implying
that absent motor/body mappings were executed and measured as zero. It adds no
yaw, translation, wings, legs or response-driven animation.

The main causal narrative is:

`MOTION INPUT → HS SOURCES → VERIFIED CHEMICAL MOTIF → DNp15 BILATERAL READOUT → DIAGNOSTIC ONLY`

Signed source and target rulers preserve a neutral zero and numerical/textual
labels; they are not firing-rate bars or thresholds. Six identity-labelled
source cards show their selected target routes. Telemetry shows scientific
time, input R/L, separate target R/L and the centered signed bilateral
diagnostic. Collapsible provenance provides source authorities, excluded edges,
structural contacts and model limitations. Scenario copy is centrally typed;
the new scenario does not inherit looming-specific explanations.

## Observed frozen condition

The right descriptor is 1 during the first 20 ms and then zero for the remaining
30 ms recovery; the left descriptor is zero. Three right HS proxies respond,
while all left HS proxies remain neutral. DNp15 R reaches
`0.7616103961114459 dnp15_state_eq` at 21.3 ms and ends at
`0.08407308575658057 dnp15_state_eq`; DNp15 L remains neutral. These values are
copied from Phase 25, not UI literals or new outcomes. R−L is a bilateral
**neural-state diagnostic only**, never a yaw/steering/motor command. Events
are undefined, not “zero spikes”. No body result is claimed.

## Performance and verification

Five local validated adapter calls: 0.1471, 0.1487, 0.1333, 0.1346 and 0.1440 s;
median **0.1440 s**. Compact JSON is **138,336 bytes** for all 501 boundaries.
The unchanged source artifact remains 714,329 bytes. Measurements are local,
not latency guarantees; no caching/runtime redesign was required.

Backend tests compare every transported scientific frame with the existing
Phase 25 replay, require exact identity/route/unit semantics, deterministic
payloads and typed missing/corrupt/authority errors. A frontend test obtains the
real Pydantic payload via offline replay and parses it in TypeScript, preserving
explicit cross-language parity. Other tests cover signed display, causal copy,
provenance, forbidden claims, stateless scrub/reset, play/pause and unavailable
data. The original scenario transport/presentation tests remain in place.

Historical Phase 7O/8C/13B/16/18/25 artifacts and v1/24/25/26 evidence authorities
must remain unchanged before and after integration. Generated scientific
artifacts are not rewritten or committed. This is a product adapter, not a new
simulation or a calibration phase.

Manual production-browser checks covered the four-card catalog, all three
existing scenario playback pages and the new neural view. The new view reached
boundary 500; pause held a selected boundary; scrub to boundary 213 synchronized
21.3 ms, the persisted target peak and the causal explanation; reset restored
boundary zero. At 390 px and desktop widths there was no horizontal overflow
or application error. A deliberately stopped local backend produced an explicit
unavailable state with no canvas/timeline fallback; restart/retry recovered the
validated result. Screenshots were reviewed locally under `/tmp`, not committed.

The original three catalog definitions and serialized playback payloads were
also compared with the HEAD implementation and were byte-identical. The narrow
Phase 26 static test now permits only the read-only playback adapter to consume
the context audit; scientific model modules remain forbidden from depending on
it. No scientific evidence record or model was changed for that allowance.

Final gates: 1,081 Python tests passed (one integration test deselected by the
repository's canonical configuration; two existing Starlette deprecation
warnings), 59 frontend tests passed; Ruff, format, diff, frontend lint,
typecheck and production build passed. The combined transport/context focused
run passed 23 tests. Both six-artifact replay rounds passed with unchanged IDs.
The build-generated `next-env.d.ts` path change was restored, then typechecked;
local verification servers/browser were stopped. No commit or push was made.

## Claim limits and next boundary

Allowed: MaleCNS-structured feedforward motif; exploratory horizontal-motion
neural proxy; identity-resolved bilateral DNp15 readout; deterministic frozen
playback; neural foundation relevant to course-control circuitry.

Forbidden: steering demonstrated; calibrated optic flow or DNp15 physiology;
yaw command/torque/turn rate; navigation; complete HS/DNp15 network; electrical
or recurrent execution; structural-contact physiological efficacy.

Next bounded action: audit publicly available chemical-isolating HS–HS
physiology for the verified HSN/HSE reciprocal pair, preserving Phase 26's
evidence gate; no author contact, recurrent implementation or output tuning.
