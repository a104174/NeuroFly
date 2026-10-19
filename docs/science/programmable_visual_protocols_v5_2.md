# Programmable Visual Protocols v5.2 — local implementation

This phase is an experiment-authoring interface, not a new neural or locomotion
model. The initial implementation was validated locally without publication. A
subsequent operator instruction authorizes one scoped commit, non-force push and
protected Preview deployment, followed by authenticated acceptance. Local evidence
below is historical; Preview acceptance must be verified separately.

## Contract and scientific execution

`visual_protocol_v5_2` contains exactly `schema`, the complete pinned v5 initial
`config`, `stop_step`, canonical `events`, and `protocol_id`. Each event contains
`id`, `sequence`, `step`, `time`, `stimulus_id`, and `kind`. The identity is the
existing canonical SHA-256 of the contract excluding `protocol_id`. Stable event
IDs survive edits; UUIDs identify editor records and introduce no simulation
randomness. Source configuration retains MaleCNS dataset/model hashes, initial
body/neural states, A/B identities/anchors/phases, motion preset/controls, units,
clocks, propulsion and boundary policy. Randomness remains NONE.

Scientific clocks are unchanged: 0.1 ms neural, 20 ms body, 200 substeps per body
interval. An authored event uses an integer step in `[1, stop_step)`, with
`time = step × 0.02`. Duration is 1–1500 intervals (0.02–30 s). Decimal UI times
are parsed as exact integer milliseconds and must be divisible by 20; off-grid
values are rejected without rounding. Initial state is defined at zero; a
terminal-boundary event is rejected because it has no outgoing interval.

Canonical order is step then landmark A/B. One event per landmark per boundary;
simultaneous events on distinct landmarks are valid. Redundant Start/Stop events
are rejected prospectively, including contradictions later in the schedule.
Reverse while stopped retains the inherited behavior: phase remains fixed and
future direction changes. No new event semantics or conflict arbitration exists.

`ScheduledVisualEngine` subclasses the existing `IndependentVisualEngine` solely
to dispatch due requests through `super.requestStimulus` immediately before its
existing `advance`. A monotonically advancing event index prevents duplicate
execution. The inherited observer, neural solver, engineering steering/propulsion,
plant, contact/recovery controller and phase evolution perform every scientific
update. Manual stimulus requests are rejected in this mode. No output pose or
neural readout is prescribed, interpolated into a new trajectory, or loaded as
an authoritative state. Timers used for cooperative replay yielding do not
schedule scientific events.

The inherited v5 order remains intact: due controls are applied at boundary k;
the completed relative-geometry interval supplies input held through 200 neural
substeps; body and world advance to k+1. Start/Stop/Reverse never change the
landmark position at the event boundary. Neural/body initial values are neither
reset nor assigned by an event. A readout for the outgoing interval becomes
available at its right boundary; an intervention marker does not imply an
instantaneous physiological response.

## Editor and lifecycle

Select **Visual Protocol Scheduler** in `/visual-lab/arena`. Draft supports preset,
bounded duration, add/edit/remove events and chronological review. **Validate
draft** computes the input identity without advancing the neural/body model.
The supplied synchronized example has A Reverse at 2 s, B Stop at 4 s, B Start
at 6 s, and B Reverse at 8 s, over the existing 30 s window.

**Run Protocol / Play** freezes the contract and starts actual browser numerical
execution. The editor is locked while an execution exists, including Pause.
Pause/Resume preserve state. Reset reconstructs the same initial state and reuses
the same protocol. **New draft from beginning** explicitly discards the current
unsaved execution and unlocks editing; save/export first to preserve it.

Saving/exporting requires a completed protocol or **Terminate recorded prefix**.
A pause is not falsely presented as completion. Early termination keeps the
entire authored program, with later events marked PENDING_UNEXECUTED. They do not
appear as applied events in the underlying v5 log. New controls are scoped to
this mode; existing manual A/B modes retain their original semantics.

## Timeline and persistence

The existing v4.1 Timeline supplies actual model signals and one shared scientific
cursor. Scheduled-but-unapplied events are separately shown as grey dashed
markers; applied events retain the existing markers. Future markers contain no
future neural samples. Seeking inspects cached completed telemetry and never
runs the solver. Play/Resume returns to the latest actual execution state.

Portable `visual_protocol_execution_v5_2` contains exactly `schema`, `protocol`,
`session` (an unchanged semantically validated v5 result), `status`, and
`artifact_id`. Status is PROTOCOL_COMPLETED or OPERATOR_TERMINATED. The identity
hashes protocol ID, underlying session ID and status. Import validates both
contracts, recomputes v5 science, and checks that the applied v5 event log exactly
matches all scheduled events with `step < actual stop_step`. Rehashed conflicting
schedules, initial configurations or computed output claims are rejected.

IndexedDB stays at version 1 in the existing sessions store. New records use
`experiment_session_library_v5_2`; inputs add only `protocol` and
`protocol_status` to the existing input-only v5 fields. No neural/body histories
are stored. The new record source ID binds the protocol, locally reconstructed
scientific session and termination status; rehashing only outer metadata cannot
substitute another source identity. Numerically equivalent portable imports are
semantically validated and pinned to this browser's reconstructed execution. Restore re-executes the schedule and checks all saved scientific
identities and distance. Old v3/v4/v5 schemas, hashes and reproduction meanings
are preserved; no migration rewrites existing records. Local storage remains
browser-origin-specific and portable JSON remains available. Hashes do not
authenticate an author.

The v5.1 comparator accepts restored v5.2 library parents through their underlying
validated v5 session. Both worlds independently calculate pose-dependent inputs.
Matching rules and comparison algorithms remain unchanged. Comparison exports keep
the existing v5 scientific parent IDs and recorded events; complete authored
programs, including unapplied future events, remain in the parent library/export. Common-window
comparison applies only the events recorded within that window; unexecuted future
schedule differences cannot masquerade as observed trajectory differences.

## Verification

Tests cover exact decimal/grid handling, ordering, stable editor identities,
redundancy/conflicts, initial contracts, no authoring solver calls, immutable
execution inputs, exact dispatch, old-state continuity, fixed substeps, clock and
pause/resume semantics, replay, full-window Python parity, early termination,
portable and library semantic tampering, and existing P/Q and ON/OFF controls.
The unchanged Python v5 reference is executed for the complete 30 s example and
focused simultaneous A/B and Neural OFF cases. Absolute tolerance stays `1e-8`.
No historical fixture is regenerated or replaced.

Canonical frontend lint, typecheck, tests and production build are required, as
are diff and read-only science-integrity checks. No Python source is changed;
targeted Python reference, HS/DNp15 and D2.2 tests supplement the trustworthy
unchanged full-suite baseline. Local browser acceptance checks automatic events,
actual scene transforms, timeline alignment, pause/resume, save/reload/import,
comparison, early termination, old manual mode and desktop/390 px presentation.
Bulk exports and screenshots belong outside Git under
`../neurofly-science/work/programmable-visual-protocols-v5-2/`.

## Limits

The prescribed input is a visual protocol, never a fly route. HS/DNp15 readouts
remain model proxies; neural-to-heading conversion, propulsion and boundary
recovery remain engineering assumptions. No new physiological signs, retinal
calibration, motor/gait validation, learning or LLM control is claimed. Completion
of a shortened protocol is distinct from the historical v5 30 s numerical
contract. A local validation is not a published protected-Preview validation.

## Local acceptance results

Baseline: clean `main`, local/remote
`9a0341249b314ce7fb4c1c8d53106fa2afb68e5a`. At the local acceptance gate the feature was uncommitted and
unpublished, with an empty Git index. No Preview or Production deployment had been
created. Local production-build browser acceptance used
`http://localhost:3010/visual-lab/arena` on desktop and 390 px.

The full example executed without manual A/B actions at steps 100/200/300/400
(2/4/6/8 s). Pausing before the first event and resuming preserved the network;
seeking inspected cached states and Resume continued from the actual last state.
Actual Three.js body/landmark transforms agreed with computed telemetry.
At 30 s: 1500 body intervals, 300,000 neural substeps, distance
4.340179039689889 presentation units, three contacts and three recoveries,
5.86 s contact time. Final X/Z were −0.4017863441254517 / −0.20536827158224602,
heading 2.0987753944735217 rad. Accumulated neural and engineering boundary heading
contributions were −0.19233308430202736 / +0.7203121519806839 rad, respectively.

Content identities:

- Protocol: `1021cae10bfcbee7f9d2fbf377c31be4eea63acf94087850dd9d69380486e7c5`.
- Underlying v5 session: `e9f7225b7df71dfd5a47694a14329872dfefce6f16fd74e10f707ddfb4c1de55`.
- Protocol execution: `37c10f1b1f78e424d9ac64d3873e12995b1cbac6bcdebccb40b4f82659d69e0b`.
- Example versus opposing comparison: `5b00f8348cb3007b4522013b39dea0fc47f473cac757aeb2eb0cba78361fcbd1`.

The actual browser export was independently checked against Python over all
completed frames (105,010 numerical values); maximum absolute error was
`3.637978807091713e-12`, below the unchanged `1e-8` limit. Both 30 s comparison
tracks also passed full-frame Python checks. Example-versus-opposing maxima were
0.10586122618223158 spatial units at 25.38 s, 0.44587670637842214 rad wrapped heading
at 25.42 s, and 0.017106595424432054 yaw_drive_eq at the 21.26 s completed boundary
(interval start 21.24 s). These are deterministic model differences, not a
biological preference or a claim of better navigation.

Browser checks passed for editor validation/edit/remove, locked execution,
automatic events, phase/neural continuity, pause/resume/reset, pending/applied
Timeline markers, save/reload, portable import, rehashed semantic tampering,
v5.1 comparison and return to the original, explicit early termination with
future events retained, historical v4 import and manual v5 behavior. A separate
final-build persistence check verified source-identity binding, atomic storage,
exact reconstruction after reload, rejection of a rehashed contradictory source
ID, and narrow layout. Its input-only record was 9328 bytes. No browser errors
were reported. Switching from a running manual session to a saved protocol and
back also resumed the correct model without a hidden parallel simulation.

Final gates: **237 frontend tests passed**, lint/typecheck/production build and
`git diff --check` passed. **63 targeted Python tests passed**, with two existing
dependency deprecation warnings; Ruff lint and format passed. The unchanged
1707-test full Python baseline was retained rather than rerun. D2.2's 74 pinned
files, existing v5 policy/fixture and historical DNg100/Planar raw artifacts were
verified without regeneration; Python, frozen numerical runtimes, source
identities and historical public outputs are unchanged.

Measured local browser validation was approximately 3.3 ms; a bounded batch of
up to five body intervals cost up to 3.9 ms in the observed run. A seven-run Node
CPU profile excluding rendering measured median 69.57 ms for all 1500 scheduled
intervals versus 67.61 ms for the same v5 inputs manually dispatched by step,
with exactly equal outputs: approximately 1.96 ms total dispatch overhead.
Median authoring validation was 0.30 ms. Browser save/reconstruction took about
1.36 s and v5.1 comparison preparation 4.47 s including validation/replay.
SwiftShader rendered about 3 FPS, with bounded catch-up active; simulated time
therefore progressed more slowly than wall time. These are software-rendering
measurements, not physical GPU performance. Observed JavaScript heap was about
55.5 MB. No new worker, library or service was needed.

The final Timeline microprofile used 1501 reconstructed boundaries in five lanes:
768 ms from opening to ready (including UI/scroll/render scheduling), ten initial
Canvas stroke calls totaling approximately 0.10 ms CPU, and an 18 ms seek/inspector
update with zero additional curve strokes. These distinguish chart drawing from
the much slower software-rendered Three.js scene.
