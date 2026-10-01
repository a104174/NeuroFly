# Phase 18 — pre-registered exploratory looming world experiment

## Scope and freeze

`LOOMING_WORLD_EXPERIMENT` is separate from the unchanged Phase 13B
`LOOMING_CIRCUIT_VALIDATION` micro-window and `BASELINE_CONTROL`. It observes
longer pinned-model transients, not biological escape or calibrated behavior.
Phase 17's conclusions and corrected Phase 16 diagnosis remain unchanged.

The tracked [pre-registration](looming_world_experiment_preregistration.json)
was written and its canonical semantic SHA-256 printed **before the first new
scenario neural execution**:
`580e088d89b38f086689c39568bf38bd04f5edf7f0d05065abe2c076a0d16bed`.
No candidate neural run, spike search, alternate-duration run or optimizer
preceded this freeze. Subsequent executions are exact deterministic replay of
that same contract, not candidate selection. No frozen value changed after
observing the result. Runtime configuration is derived from the contract;
changed contract bytes with changed semantics fail its pinned hash check.

The contract pins the complete reused model-identity dictionary by SHA-256
`b8f641dbb4ad4cd502161c688f05d40e392ed818a7e4645528991ff2539d8f37`
and historical Phase 13B artifact
`55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b`.
Artifact configuration also persists the explicit model identities, not just
their aggregate digest. Phase 13B historical provenance validators are not
loosened to accept the new experiment.

## Predeclared design criterion

| Quantity | Frozen value | Selection rationale / classification |
|---|---|---|
| Horizon | 40 ms | Two existing 20 ms membrane time constants; exploratory model-transient observation, not biological latency |
| Numerical dt | 0.1 ms | Retained resolution, no new integration scheme |
| Intervals / boundaries | 400 / 401 | Exactly horizon / dt and initial boundary |
| Body initial x/z | 0 / 0 world_eq | Existing deterministic reset; fixed +Z heading |
| Object initial x/z | 0 / 4 world_eq | Retain prior initial geometry |
| Object radius | 1 world_eq | Retain prior model-space size |
| Object prescribed vx/vz | 0 / −0.05 world_eq/ms | Jointly choose endpoint z=2 after 40 ms, `(2−4)/40`; no physical velocity interpretation |
| Projection | R, hex(23,9), scale 10, FLOOR | Retain exploratory fixed-column assumptions |
| Safety margin | Strict forward separation > 1 object radius | Deterministic domain reserve, not collision physics |

All new design quantities are `MODEL_ASSUMPTION_EXPLORATORY_EXPERIMENT_DESIGN`.
Two membrane time constants is an explicit model-internal observation criterion,
not evidence for the biologically correct horizon. It neither guarantees a
spike nor identifies a calibrated natural looming stimulus. Duration / tau_m
is 2 rather than the micro-window's 0.07. Discrete sensory-to-membrane latency
remains two boundaries; it was not changed to strengthen the response.

## Geometry proof before execution

For a stationary reset body, `z_relative(t) = 4 − 0.05*t`, with `0≤t≤40`,
lies in `[2,4]`, strictly above the one-radius margin. No zero separation,
behind-body passage or singularity occurs. `atan2(1,d)` is finite, and
`floor(10*atan2(1,d))` ranges from 2 through 4; these integer radii are accepted
by the existing relative-column disk primitive. This proof uses geometry only,
not hypothetical neural, actuator or displacement outputs.

Actual body movement is unknown at freeze. Before each boundary's exposure,
the shared runner checks authoritative body/object geometry. Unsupported
geometry or forward separation at/below one radius deterministically stops
before exposure and downstream processing at that boundary, returning
`TERMINATED_GEOMETRY_DOMAIN`, reason, step/time and the attempted authoritative
body/object state. There is no clamping, padding, remaining synthetic trajectory
or fallback action. Previously integrated intervals remain recorded. Nonfinite
states fail explicitly because they cannot be canonical JSON.

`COMPLETED_VALID_HORIZON` instead records boundary 400 / 40 ms. A termination
record is separate from closed-loop, actuation and movement statuses. If a
geometry stop follows actual movement, that movement is still reported; the
attempted invalid boundary is not fabricated into a valid sensory frame.

## Shared causal authority

No model equation was duplicated. The existing Phase 13B runner accepts an
opt-in new-experiment guard/result version; historical configurations remain
strictly limited to their two original kinds and 14 intervals. Enabled-object
handling reads the configuration's existing stimulus-enabled semantic rather
than assuming there can only be one looming scenario kind.

At valid boundary n: authoritative body/object → relative geometry → existing
disk/exposure primitive → all 311 identity-resolved states. Boundary-n spikes
propagate through unchanged TTMn integration, threshold crossing, target
dispatch, NMJ receipt, abstract electrical input, G1 electrical response,
activation and side-preserving actuator routing. Sensory state s[n] drives the
DNp01 interval update, while exposure e[n] updates s[n+1]. Commands at n drive
the existing common-mode body interval n→n+1. The prescribed object then
updates by dt*velocity. Boundary n+1 recomputes geometry using that updated
authoritative body and object. There is no outgoing interval after boundary
400. MaleCNS contact counts remain structural evidence, never current gains.

All reused gains, time constants, thresholds, reset/refractory semantics,
activation normalization and body gain remain pinned. No historical fixture
ancestry is spoofed. Test-local changed body states test feedback and domain
termination only; they never enter canonical artifacts or production options.

## First observed frozen result

The first run completed the full valid horizon and its result hash exactly
matches the generated/replayed artifact. Zero output was accepted without
stronger, longer or faster reruns.

| Observation | Micro-window circuit validation | New world experiment |
|---|---|---|
| Scientific role | Bounded circuit execution test | Longer exploratory pinned-model observation |
| Horizon / intervals | 1.4 ms / 14 | 40 ms / 400 |
| Object z / velocity | 4→2.6; −1 world_eq/ms | 4→2; −0.05 world_eq/ms |
| Projection radius | 2→3 | 2→4 |
| Exposed bodies | 19→22 | 19→26 |
| R DNp01 peak | −51.933657842035 mV_eq | −48.733429620245 mV_eq |
| L DNp01 peak | −52 mV_eq | −52 mV_eq |
| DNp01 spikes | 0 | 0 |
| Motor input/output, dispatch/receipt/electrical tokens | All 0 | All 0 |
| Activation / actuator commands | All 0 | All 0 |
| Body displacement | 0 world_eq | 0 world_eq |
| Termination | Original full micro-window | COMPLETED_VALID_HORIZON |

The new object's endpoint is approximately 2 due to ordinary floating-point
integration. Half-angle changes 0.244978663127→0.463647609001 radians
(dimensionless model geometry, not calibrated retinal field registration).
Final right-side LC4 state sum is 1.668851474100; LPLC2 is 3.854206107607.
Left-side sums remain zero. Final consumed external drive is
5.522911908887 mV_eq on R and zero on L. DNp01 depolarizes but stays below the
pinned −45 mV_eq threshold; its R peak margin is 3.733429620245 mV_eq.

Closed-loop execution, environmental sensory change and feedback wiring are
true. Feedback realization, genuine nonzero actuation and body movement are
false. A longer run's stronger depolarization is descriptive model behavior,
not evidence that it is biologically better or that duration alone explains
silence. The Phase 16 limitations remain coupled rather than independent.

## Artifact, replay and transport

New immutable artifact schema: `looming_world_experiment_artifact_v1`.
Scientific result: `looming_world_experiment_result_v1`; configuration:
`looming_world_experiment_config_v1`. Historical Phase 13B schema/bytes/identity
remain unchanged.

- Artifact ID: `ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c`
- Config hash: `daca5f023b9d31ac445340e0938ecda153439f0463b858c421b71d72bbe4ee12`
- Result hash: `7a7b35431c43f65501e298e187c97f042e90e0e3d3496cf9f44531a9544e3e42`
- Size including manifest: 11,074,494 bytes, Git-ignored under existing derived data.

```sh
python -m neurofly.looming_world_experiment_cli generate
python -m neurofly.looming_world_experiment_cli replay data/derived/malecns/looming_giant_fiber_v1/looming_world_experiment_artifact_v1/ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c
```

Generate uses immutable staging/manifest conventions. Replay validates the
freeze, historical/source identities, executes the actual causal runner,
compares canonical config/result bytes and checks all manifest hashes and
directory identity. Mutated pre-registration, duration, trajectory, source
model, telemetry, termination and hashes are rejected, including semantically
altered payloads with recomputed hashes. Network and randomness are absent.

First causal execution measured 3.663 s after 7.830 s source validation.
Complete offline replay measured 23.456 s and compact transport construction
23.095 s under concurrent regression load. Timing is diagnostic, never hashed.
The scientific artifact stores all 311 arrays and ancestry; compact typed
`scenario_playback_v1` contains 401 summary frames, 283,219 bytes, not the full
11.1 MB artifact. No premature optimization bypasses validation.

The existing catalog/API now exposes exactly three presets. New optional typed
transport fields carry termination, requested horizon and freeze identity.
Existing Phase 15 presentation, one current object, snapshot interpolation,
play/pause/reset/scrub and causal explanation are reused. Scientific duration
comes from backend timestamps (40 ms); six seconds remains display time only.
No frontend physics, local scientific projection, extra animation or new
scientific configuration editor was introduced.

## Verification

Focused backend tests: 57 passed, plus the explicit stop-after-authoritative-body
update regression. Tests protect frozen config derivation, geometry at every
reference boundary, no output-targeting options, feedback changing later
exposure, causal accounting and byte/hash/manifest tamper rejection. They
validate output consistency without requiring a nonzero spike count.

Historical corrected Phase 16, Phase 13B, full Phase 7O numerical recomputation
and Phase 8C genuine composition replays passed unchanged. The original
Phase 13B artifact remains `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b`.
Frontend 53 tests, lint, typecheck and production build passed; Ruff check,
format check and diff check passed.
Full `python -m pytest`: 1,018 passed, 1 deselected, two existing dependency
warnings in 687.76 s. An earlier non-PTY invocation ended externally with
exit 143 before completion; the fresh complete rerun above is the acceptance
gate. No failing test was suppressed or deselected for this phase.

Actual browser smoke used the real FastAPI adapter and Next application for
all three presets. Baseline has no object/exposure and reaches 1.4 ms;
micro-window Looming retains 19→22 exposure and stationary body. New world
playback reaches boundary 400 / 40.0 ms with distance 2, radius 4, exposure 26,
R DNp01 −48.733 mV_eq, zero commands and stationary body. Start/end screenshots
confirm one current object approaches while the fly remains still.
Play/pause/reset and keyboard scrubbing synchronize scene, telemetry and
termination. Pause held boundary 23 unchanged; final scrub selects boundary
400 and its exact projection metrics. The 390 px viewport has width 390 with
no horizontal overflow; screenshots were reviewed and remain in `/tmp`, not
tracked. No application errors or framework overlay occurred. The inherited
Three.js Clock deprecation warning remains a rendering dependency limitation.
The actual new-scenario server action took 21.139 s under regression load.
Phase 18: `PASS`; decision `EXPLORATORY_LOOMING_WORLD_EXPERIMENT_VALIDATED`.
No commit/push. Only intended Phase 18 changes remain; generated artifacts and
browser screenshots are not tracked.

React/Next skill review preserved the existing server/client separation,
serializable compact props, dynamic 3D import, and independent remote result,
playback cursor and render interpolation states. No new hooks or effects
change scientific execution.

## Claim budget and next question

This is a deterministic exploratory model-space closed causal loop with genuine
pinned-model output. It is not calibrated biological looming timing, natural
predator velocity, retinal registration, biological threshold adequacy,
escape probability, real-world displacement or jump biomechanics. Stationary
output is neither a failed scientific run nor biological non-response evidence.

Exactly one next bounded action: evidence review of the identity-resolved
sensory→DNp01 transfer magnitude/normalization contract, without proposing
replacement gains or targeting spikes.
