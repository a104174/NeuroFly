# V10.8I — Versioned initial-flight landing-clearance recovery

## Declared treatment and root cause

Reference revision: `c84e34f221f937517f2f25580f54811b04827c94`. Controller/protocol: `mixed_ground_flight_landing_recovery_v1`, version 1. Verification: `mixed_landing_recovery_verification_v1`.

The published sustained-v2 coordinator applied an override only inside the `flight_resumed` branch of `MixedGroundFlightSession.advance()`. Its initial episode instead called `TouchAndGoSession.advance()`, whose original `decideTouchAndGo()` braking branch issues zero forward/turn input until landing eligibility holds. At heading 0, lateral clearance falls below 0.06 during braking. Once stationary, the unchanged controller cannot restore that clearance. This is an engineering policy applicability failure, not a neural/connectome defect.

The existing resumed override is extracted unchanged into `decideTouchAndGoWithLandingRecovery()`: evaluate the original decision; if its proposed next phase is `braking` and minimum forward/left/right ray clearance is **strictly below 0.06**, invoke `decideReactiveFlight({phase:'exploring',avoidance_turn:0}, observation)`, use that command, and return to `exploring` with the resulting reactive state. The original decision function remains unchanged. Historical resumed flight now calls this shared function without new telemetry. The new version also opts initial flight into the same function.

This is a one-interval abort-braking override, not a new physical state or continuously latched recovery integrator. The next interval resumes existing reactive hysteresis. Another abort can occur after another avoidance release if clearance is still unsafe. Existing approach/release thresholds 0.34/0.50, turn command 0.85, altitude feedback, normalized motor bounds, plant integration and collision envelopes are untouched. There is no new epsilon: clearance exactly 0.06 remains admissible; lower values remain inadmissible. Landing additionally requires flying state, no contacts, horizontal speed ≤0.01, absolute vertical speed ≤0.02 and altitude within 0.02 of the existing 0.3 target.

## Frozen verification

Before the first corrected execution, heading 0 recovery/landing was required within the unchanged initial-flight cap of 1,500 intervals / 30 s. A separate continuation window of 3,000 global intervals / 60 s was declared simultaneously, plus the original π/2 heading robustness check. The same grounded initial position [0, 0.11032208074629306, 0.12187743186950682], zero velocity, standard chamber, 20 ms interval, plant and ground neural policy are retained. No randomness, seed null. Only initial recovery applicability is the treatment relative to the historical heading-0 condition. No parameter was changed after execution.

Each corrected heading was executed twice, comparing the complete canonical configuration, observations, decisions, recovery metadata, commands, accepted states, active engines, contacts, handoffs, neural initialization, metrics and termination. All repeated evidence matched exactly.

| Scientific result | Historical heading 0 | Corrected heading 0 | Corrected π/2 |
|---|---:|---:|---:|
| Actual duration | 30 s | 60 s | 60 s |
| Outcome | FAILED: landing_not_reached | DURATION_WINDOW_COMPLETED | DURATION_WINDOW_COMPLETED |
| First initial recovery | unavailable | 2.88 s | not needed |
| First LAND request | none | 7.54 s | 9.16 s |
| First accepted floor landing | none | 10.22 s | 11.84 s |
| First resumed accepted flying state | none | 11.74 s | 15.92 s |
| Takeoffs / landings | 1 / 0 | 5 / 4 | 5 / 4 |
| Walking duration / path | 0 / 0 | 8.88 s / 1.5984 units | 9 s / 1.62 units |
| Total horizontal path | 0.2443806824 | 6.6329100016 | 6.6429199986 |
| Flying/landing start-state duration | 29.48 s | 48.52 s | 48.4 s |
| Altitude above floor | existing failed run | 0–0.3004543989 | 0–0.2997485800 |
| Wall / ceiling contacts | 0 / 0 | 0 / 0 | 0 / 0 |
| FLOOR contacts | 0 | 4 | 4 |
| Bounds violations / rejected commands | 0 / 0 | 0 / 0 | 0 / 0 |
| Maximum handoff position / heading / global-time discrepancy | no handoffs | 0 / 0 / 0 | 0 / 0 / 0 |

Ground states are checked against the existing ground envelope; flight states against conservative flight bounds. The distinct ground envelope can legitimately permit wider Z travel. No envelope is reduced or silently substituted.

## Interval-correct recovery and landing timeline

The first policy decision and motor difference from historical heading 0 occurs at interval 144, observation time **2.88 s**, clearance **0.059964052629866205**. The override applies HOLD, forward **0.85**, turn **0**, vertical **0.2431696390977474**. FlightEngine accepts the first changed XYZ at boundary **145, 2.90 s**. The first changed accepted heading is boundary **206, 4.12 s**, from command interval **205, 4.10 s**. Both versions have identical accepted initial state; metadata alone is not counted as a policy or motor difference.

The single-interval override releases to normal reactive exploration on the next boundary, 2.90 s. A second state-dependent override occurs at interval **208, 4.16 s**, with clearance **0.03847393001063502**; normal exploration resumes at 4.18 s. The first sufficient observed minimum clearance after activation occurs at interval **308, 6.16 s**, **0.0607585847434126**. Sufficient clearance alone does not issue LAND: avoidance recovery and braking must also complete.

LAND is requested at interval **377, 7.54 s**, with minimum clearance **0.16998257566892744**, valid speed/altitude and no contacts. Its accepted result is boundary **378, 7.56 s**, in physical `landing`; the plant's transition event is timestamped at command boundary 7.54 s. Actual FLOOR contact and `landing->grounded` are accepted at boundary **511, 10.22 s**. There is one LAND request for this episode, not repeated requests while descending.

Accepted landing pose: **[0.753747717288, 0.11032208074629306, 0.129366426299]**, heading **2.8016**, zero velocity. The ground solver initializes from exactly that pose. The first ground sensory summary is null, with explicit fresh-zero HS/DNp15 initialization; no airborne neural continuity is claimed.

The first walking episode is **10.22–11.22 s**, accepted path **0.18**. Ground-to-flight handoff / TAKEOFF request occurs at **11.22 s**, position **[0.8104281566535579, 0.11032208074629306, -0.04146421911558272]**, heading **2.840346328846476**. The supported flight initializer retains that position, heading and accepted planar velocity, with zero vertical velocity. The second flying state is accepted at **11.74 s**. No body reset or position/heading teleport occurs.

Further ground episodes: **27.50–28.50 s** (0.18 units), **35.34–38.82 s** (0.6264), **52.22–55.62 s** (0.6120). The run ends flying at 60 s. Each episode uses the real existing ground solver and a new explicitly initialized neural episode.

## Provenance, failure and historical compatibility

Only the new result schema `mixed_ground_flight_landing_recovery_result_v1` contains `mixed_landing_recovery_evidence_v1` interval records. They identify the controller, initial/resumed/ground context, applicability, global observation index/time, source-local observation index and resulting accepted index/time. Policy metadata records observed/required clearance, base proposed phase, eligibility and the active override. `previous_interval_active` identifies return from the preceding override; active means the actual one-interval motor override, not a hidden continuous recovery state. Landing eligibility refers explicitly to observation n. Ground neural fields remain null in flight. Contacts, ground eligibility and handoffs remain in native accepted evidence.

The global accepted history has one authoritative body engine per interval. Pause adds no intervals; reset and mode switching create fresh owners. Recovery has no independent mutable state to leak across handoffs. The unchanged initial 30 s cap still produces explicit unsuccessful outcomes; the new version propagates its actual inner failure if it cannot land. The 60 s continuation cutoff is a finite evaluation boundary, not a behavioral landing request.

Historical canonical hashes remain:

- V10.8G / H baseline: `92c034ca11d507d9e2759ed5c3241ecb6510a17737388cdfe5f8d3fa96bd272b`.
- V10.8H heading-0 failure: `51d898df0ead8c73520928f9770516b65a1497a784803eb199b8ed816fab0fea`.
- V10.8H pair: `d8d8f34983dabb4c5892df450d27ed54b47a56bf7a95908c02429321ad02151f`.
- V10.8F mixed: `e630d4278fb9fc94e8dd736726a7049af9d85af5df28dcfb80be864b0f1282d5`.
- V10.8E touch-and-go: `b9636f67ee6fe70559015399d1df9f60c3eef048e96793a3c840d1e135264894`.

New complete canonical result hashes:

- Corrected heading 0: `75924ccb594bd49efa1d697d75b13cb9638be319f895047005f0da9f2bf40048`.
- Corrected π/2: `fcfd8d492f8c3f2ca15a0c12b0095892087e29b7c84cd2e8350b6131ea07b43e`.

The corrected π/2 accepted frames are also exactly equal to the historical baseline frames; its different result hash reflects the new version, declared heading and telemetry. No historical hash or result was regenerated to approve changed behavior. Scientific source identity is the implementing Git revision; the protocol reference revision remains the historical comparison source.

## UI, testing and limitations

The primary Lab adds the opt-in **Mixed exploration — landing recovery** choice with the predeclared heading 0. Default ground mode, continuous reactive flight, touch-and-go, mixed-v1 and sustained-v2 remain available. Existing viewer, FlightClock, GLB, wings and ground gait consume accepted states. No renderer/body integration code changes.

Focused tests cover historical hashes/root failure, equivalence to the existing resumed recovery, actual below/exact/above-threshold geometry, invalid observations/state/phase, local duration-cap refusal, complete real-engine recovery/continuation, repeated evidence, command/observation timing, no repeated LAND spam, finite states, path continuity, real ground replay, neural initialization and opt-in/reset/pause contracts. The first focused run had one test-only error-message expectation mismatch (non-finite input was rejected as `Non-finite flight value`); the assertion was corrected to the existing diagnostic without changing runtime behavior.

This is engineering model robustness for two headings in the existing rectangular chamber, not proof of general safe landing or biological autonomy. The reused override can require multiple attempts, and finite timeout remains possible for other states. No learning, randomness, new sensor, new obstacle, neural lift or biological landing motivation is introduced.

A local desktop Chromium check reused the cached browser and native debugging protocol against `/visual-lab/arena`. It selected the new option and captured accepted flight at 2.34 s, recovery/exploration at 3.10 s, landing at 8.26 s, genuine walking at 10.26 and 10.98 s, and second flight at 12.30 s. The two walking screenshots correspond to distinct accepted X/Z positions. Pause retained the same accepted step; Reset and mode switching restored the canonical grounded position at step 0. One canvas and zero uncaught page exceptions were recorded. The route returned HTTP 200; the browser/server log contained the existing `THREE.Clock` deprecation warning. No new confirmed rendering defect was observed in these sampled frames. This is software-rendered Chromium sampling, not cross-browser/device, continuous-motion or measured GPU/FPS acceptance. Screenshots and full generated evidence remain outside Git in temporary local files, not permanent hosted artifacts.

Validation: focused recovery/H/G tests **10 passed, 0 failed, 0 skipped** after correcting the diagnostic assertion; full frontend suite **499 passed, 0 failed, 0 skipped**. Lint, typecheck, build and Git whitespace checks passed. The frozen V10.6B preflight passed against its unchanged protocol source, including all eight protected SWCs and these established pins:

- Runtime v3: `c5edf9edb0b1f08a0eb3e36808dd6ec25771be1bc575ce07e9cc3063aa6586cf`.
- Frozen configuration: `dbc0f37db7a614c1a1076041f6319999bb86e7414b17a21992a8797e43f4a392`.
- Frozen visual manifest: `6a3d05441afd0c25ed8c2a98472acc35601f6e525db6f74d4eb16b0e32ab3b9e`.
- Neural morphology manifest: `c538f94a6a3ea02390bfcb09ee77226fe6f0418455c0794cdfedd64593070697`.

Exactly one next improvement is recommended: evaluate a small predeclared set of additional admissible headings against this new version's unchanged recovery policy to quantify remaining timeout or near-wall cases. Do not tune the controller or implement that next phase here.
