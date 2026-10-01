# Phase 14 — authoritative scenario selection and 3D playback

## Product boundary

`/scenarios` is linked from the existing NeuroFly product header beside
Experiments and Morphology. It lists exactly Baseline Control and Looming
Circuit Validation from the backend catalog. `/scenarios/[scenarioId]` uses
the same application shell and existing `FlyVisualAsset`; the historical
experiment cockpit and connectome visualization are unchanged. The scenario
view is deliberately separate from their incompatible experiment-timeline
contract, not a second frontend application.

Choose a preset, then **Run canonical preset**. This is explicitly canonical
replay, not a new configurable experiment. The scientific backend recomputes
the complete Phase 13B battery and validates pinned source provenance on every
playback request. Source validation can take several seconds. The UI reports
pending and failed validation states; there is no substitute synthetic result.
After loading, the URL gains `?replay=canonical`; reloading that deep link
validates and restores the same canonical preset. Reset only resets playback.

## Transport and authority

The existing GET-only FastAPI adapter adds:

- `GET /api/v1/scenarios`: typed `ScenarioDefinition[]`, with ID, scientific
  kind, title, description, availability, caveat and preset-only status.
- `GET /api/v1/scenarios/{scenario_id}/playback`: Pydantic
  `ScenarioPlaybackResult` / `ScenarioPlaybackFrame`, serialized as
  `scenario_playback_v1`. Unknown presets return 404 `unsupported_scenario`;
  unavailable/invalid scientific sources return 503 `scenario_unavailable`.
  Both use the existing `experiment_http_error_v1` envelope.

The Next server action delegates to this adapter using the existing
`NEUROFLY_API_BASE_URL`, no-store fetch and error handling. It validates the
input kind and checks the returned scenario identity. A strict TypeScript
parser rejects unsupported schema/kind, bad IDs, mismatched grids, nonfinite
coordinates, malformed neural arrays and commands outside [0,1]. There is no
browser-to-Python filesystem access, database, new job service or WebSocket.

`NEUROFLY_SCENARIO_ARTIFACT_PATH` optionally points at the canonical Phase 13B
directory; otherwise the existing derived-data root is used. Requests remain
read-only: numerical replay executes but writes neither artifacts nor model
parameters. Historical experiment endpoints retain their original behavior.
Deployment needs the pinned local historical sources and the generated
canonical scenario artifact, not just the compact transport module.

The playback result carries artifact/run identity, backend scenario metadata,
dt/duration, six separate scientific statuses, DNp01 identities/spike count,
ordered frames, scientific limitations and `VALIDATED_CANONICAL_REPLAY`.
Frames contain exact step/time, body position/fixed heading, optional object
position/radius, distance, lattice radius, exposed-body count, LC4/LPLC2
side-specific state sums, DNp01 model membrane/spike data, TTMn state and
independent right/left actuator commands. Object radius comes from the pinned
scientific configuration, not a client constant. Baseline object/geometry
fields remain null. Detailed 311-body arrays and event ancestry remain in the
scientific artifact; the UI never parses the full artifact.

## Rendering and playback

Remote scientific results, UI playback cursor and render interpolation are
distinct. The client does not compute looming geometry, lattice exposure,
neural activity, actuator output or body integration.

Scientific timing remains dt = 0.1 ms, 14 intervals / 15 boundaries, 1.4 ms.
The presentation clock spreads that entire record over six display seconds.
Play advances only the presentation cursor; Pause freezes it; Reset chooses
boundary zero; the keyboard-accessible scrubber selects a discrete boundary.
Playback stops at the final boundary without looping. All telemetry is taken
from the exact selected authoritative boundary (floor of the visual cursor).
No interpolated membrane voltage is displayed as scientific data.

Only body/object transforms interpolate neighboring backend snapshots. Shared
render-only scale is 1.5 scene units per world_eq. Body uses
`[scale*x, 0, scale*z]`; the existing fly asset retains its own presentation
offset/scale. Object uses the same x/z mapping with a display-only height of
1.6 and radius `scale*radius_world_eq`. Grid, camera, lights and object height
are visual presentation choices, not contact, geometry or physical units.
They never feed scientific state or future sensory samples. There is no
`useFrame` motion integration, local velocity law, fly jiggle, escape animation
or LLM controller. Failed WebGL leaves timeline/telemetry usable; failed GLB
loading uses the existing explicitly labeled visual placeholder, never an
invented scientific response.

## Canonical results and interpretation

Phase 13B artifact remains
`55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b`.
Config hash `3145673ad2bb6345fa9287adab37eee859861b7b029c40989a9a0fc352dff7c6`;
result hash `e33d5d8163b4b24755ea8479475258c28c44f8d8f351de2444a1693629435242`.
No scientific module, parameter, artifact or GLB changed.

| Preset | World/sensory | Genuine output | Body |
|---|---|---|---|
| Baseline Control | Object absent, stimulus disabled, zero exposed bodies | Zero DNp01 spikes and actuator commands | Stationary (0,0) |
| Looming Circuit Validation | Object z 4→2.6 world_eq; radius 2→3; exposed bodies 19→22; sensory sums change | Zero spikes and actuator commands; right DNp01 coordinate rises to approximately -51.933658 | Stationary (0,0) |

Both show closed-loop execution completed and feedback wired, while feedback
realized, nonzero actuation and movement are false. Environmental sensory
change is true only for Looming. These remain separate visible statuses, not
one success/failure flag. The interpretation banner describes a valid
stationary model result, not a failed escape or biological lack of response.
DNp01 values are labeled model membrane coordinates, not empirical biological
mV; world_eq and dimensionless actuator labels are retained.

Projection is exploratory and unregistered: fixed R / hex(23,9), not calibrated
retinal receptive fields. The compact caveat and expandable provenance area
preserve this limitation. Other strategic worlds remain future work; no
scientific config editor or extra executable scenario is exposed.

## Verification and measured performance

Backend tests perform real full source replay for both presets and verify
canonical facts, compact payloads, typed catalog, errors and absent Baseline
object. Frontend tests cover transport rejection, error handling, no artifact
dependency, exact telemetry, neighboring snapshot interpolation, authoritative
body/object transforms, cursor behavior and unchanged scientific timestamps.
Existing experiment/cockpit/asset tests remain intact.

Browser smoke used the real API and Next dev server: catalog/navigation,
Baseline no-object scene, approaching Looming object with stationary fly,
changing neural/sensory telemetry, play/pause/reset/keyboard scrub, completion,
pending state and completed-result deep link. No browser errors or framework
overlay were observed. A 390 px viewport has no horizontal overflow after the
header navigation was made wrapping; desktop scene and telemetry were visually
inspected. Diagnostic screenshots are in `/tmp`, not committed data.
The dev log did contain a nonblocking Three.js `Clock` deprecation warning
from the rendering dependency; there was no runtime error or scientific effect.

Final gates: Python 979 passed / 1 deselected (two pre-existing dependency
warnings); focused API tests 14 passed; frontend 46 passed; Ruff check and
format, diff check, ESLint, TypeScript and production build all passed. Phase
14 `PASS`. No commit/push; generated scientific data remains ignored.

Measured HTTP compact payloads: Baseline 10,216 bytes; Looming 11,947 bytes,
versus 1,137,837 bytes for the full scientific artifact. Requests took 8.99 s
and 9.84 s respectively while the full regression suite was also running.
Initial source replay took 6.41 s. No provenance validation was bypassed to
improve latency. Production build compiled in approximately 2.2 s, with
TypeScript approximately 3.2 s in the first measurement. There is no scientific
live stream; this first product slice is validated-result playback.

## Next milestone

One bounded scientific milestone: characterize why the pinned genuine
311-sensory→DNp01 pathway remains subthreshold in the canonical scenario,
using replayable evidence and without a scripted fallback or visually motivated
retuning. The present product already makes that silent outcome inspectable.
