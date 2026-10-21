# Programmable Flight Controls v8.1

Engineering-only authoring over `engineering_3d_kinematic_flight_v8`. This layer
adds no flight equations, neural input, aerodynamic forces, rendering rig,
dependencies or backend. The approved Normal 12 Hz and Slow Inspection 2 Hz
wing presets are unchanged. Original scientific sessions never enter this library.

## Authority and timing

`FlightProgramEditor` edits a `FlightDraft`. The sole normalization path is
`normalizeFlightDraft` in `flightProgram.ts`. Rows reuse v8's exact command fields:
`id, step, forward, turn, vertical, intent`. UI seconds must already lie on the
20 ms grid (floating-point representation tolerance 1e-8 of a step); other times
are rejected, not rounded onto a different boundary. Valid rows are sorted by
integer step. Duplicate boundaries are rejected rather than assigned a priority:
one row specifies the entire control vector and one intent. Stable row IDs
survive edits and sorting. Duplicating a row creates a new ID; the resulting
same-time conflict remains visible until the user edits or removes it.

Controls are finite in [-1,1]. TAKEOFF/LAND are one-shot intents; scalars hold
until the next row. Before the first row, the existing zero/HOLD command applies.
A command at boundary k controls [k*.02,(k+1)*.02). Outputs are available at the
completed boundary k+1; original event timestamps remain unchanged. Commands
at the terminal boundary cannot affect the run and are rejected. Programs have
1–100 rows and a duration on the 20 ms grid, greater than zero and at most 12 s.
No duration extension or implicit landing command is introduced.

Static normalization never runs dynamics on edits. Explicit Validate reconstructs
through the existing `FlightEngine` to diagnose actual REJECTED_COMMAND events
(ineligible TAKEOFF, LAND or grounded motion). Errors identify the row. Contacts
and a program ending airborne are valid modeled outcomes; an airborne ending
shows a warning instead of fabricated landing or altered controls. Validation
reconstruction is diagnostic only: Run starts a fresh engine from the normalized
immutable trial and advances through the existing fixed-step clock.

## Draft and execution lifecycle

Reference Flight v8 is read-only and retains the original input/result identities.
Duplicate Program creates a new program ID with its declared parent ID. New
Flight Program creates an empty, nonexecutable draft. Row edits invalidate
validation and clear the current displayed run; no previous telemetry is shown
as belonging to new inputs. Saved earlier snapshots are retained. Controls are
locked during execution. Paused editing starts a new run from the initial state,
never patches the running plant. Run collapses the editor to keep the fly visible.

The current frozen run is identified by name and input SHA-256. Reset uses that
snapshot. Pause/resume/seek/replay reuse the v8 clock and recorded-boundary APIs.
Seeking does not execute the plant. Current metrics (distance, maximum altitude,
contacts) include only boundaries through the inspected time. Future transitions
are excluded from the current event inspector. The wing selector remains a
presentation inspection control; v8.1 run provenance retains the preset in its
validated program snapshot. Existing v8 JSON replay remains separately supported,
including legacy valid trials outside the smaller v8.1 authoring limits.

## Versioned artifacts

`engineering_flight_program_v8_1` contains exactly:

- `schema`, classification `ENGINEERING_ONLY_NOT_A_NEURAL_EXPERIMENT`;
- `id`, `name`, nullable `source_program_id`;
- the full existing v8 `trial` (model, initial state, stop step, command log,
  timestep, randomness policy and wing presentation identity/preset);
- `content_sha256`, SHA-256 of the canonical v8 trial.

Display name and program lineage are metadata. Renaming does not alter numerical
identity or trajectory. A new ID distinguishes a duplicate even before a control
is edited. Reference ID `reference-flight-v8` is reserved: import and validation
require the original name, lineage and numerical identity for this ID.

`engineering_flight_run_v8_1` contains exactly `schema, program, result`.
`result` is the existing `engineering_flight_result_v8` export, including recorded
frames/events, termination and input/result hashes. Import validates the program,
replays actual commands with v8, compares every imported result field, and checks
that result inputs match the immutable program. Recomputing a checksum cannot
legitimize invented positions, changed model parameters or impossible intents.
Recorded prefixes can be exported/imported; only completed runs can be saved in
the local completed-run library. Files are capped at 4 MB.

## Origin-local persistence

`FlightProgramLibrary` uses a separate localStorage key
`neurofly.engineering-flight-library.v8_1`, with wrapper schema
`engineering_flight_library_v8_1`. Scientific IndexedDB and My Experiments are
untouched. Program records contain the validated program. Completed-run records
contain only the program, terminal step and expected result SHA-256, not duplicate
trajectory arrays. Opening reconstructs and verifies those outputs with v8.

Keys include content type, stable program ID and numerical content hash. Saving a
changed numerical revision adds a record; earlier revisions and completed runs
are preserved. Saving the same numerical program may update its display name.
The built-in reference cannot be overwritten. The library is bounded to 40
snapshots / 2 MB. Quota or unavailable storage errors are visible. Corrupt root
or ambiguous duplicate identities prevent writes; individually invalid records
are isolated with a diagnostic and retained in storage. Missing records are
rejected on open. No destructive migration, eviction or cloud persistence.

## Reference and causal control example

The original 12 s / 601-boundary reference remains:

- input `25af17966a60f9ed17267d6143cac86b783fd370ca09fef33ee49313177c9f61`;
- result `8c8fc14e028a40fbc1aea526f253306bafc827b858a52495f0751168655528b7`;
- final `[.639532893281,.11032208074629306,-.168962575892]`, zero velocity.

Duplicating it and changing only `climbing-turn` at 5 s from turn .65 to .30:

- leaves initial state, all other commands and all plant parameters matched;
- final `[.734186787114,.11032208074629306,.012063823709]`, zero velocity;
- final heading `1.490796326795` versus reference `2.050796326795`;
- final/max separation `.2042790174497855` units; heading delta `-.56` rad;
- both land at 11.44 s, reach .368 units altitude, and have one floor contact;
- custom input `aba0d2b5722be2df9d3fccc6c0a8853dc7681709f0658b833f11067edc5d87b4`;
- custom result `9fe3482ee18812120deb686dfb4231e6af35c666b216c2df5ff6fd590fc60db1`.

These differences arise from integrated engineering commands and establish no
neural adaptation or biological flight behavior.

## Local acceptance (2026-10-21)

Initial `main` and remote `main` matched
`5e858aa4952e378941467e937a79149855aef971`, with a clean worktree/index.
The v8 plant source, all wing/gait configurations and scientific Python sources
remain unchanged. No staging, commit, push or deployment is part of this phase.

Canonical frontend gates passed: 290 tests, lint, typecheck and production build.
Python: 55 focused wing/motor-reference/runtime/HS-DNp15/scientific-status tests
plus 29 deployment-inventory/canonical-playback tests passed. Those include real
historical replay adapters and all 74 pinned D2.2 files. This was not the full
Python suite. Ruff lint/format and `git diff --check` passed. Four DNg100/T1
canonical `reference_id` values were reproduced (distinct from raw-file SHA-256),
and relevant runtime/GLB/gait/wing/motor source bytes matched the published HEAD.
No external scientific fixture was invented or regenerated.

The actual production build at localhost:3010 passed desktop 1440x1050 and
390x844 browser acceptance with no JavaScript errors. The reference was duplicated,
its 5 s turn edited to .30, validated and executed live through FlightEngine.
Browser exports matched the independent Node calculation at all 601 boundaries.
The program and compact completed run survived a full same-origin reload; running
the reopened program reproduced the same artifact exactly. Program and run JSON
imports verified their inputs and results. Invalid program identity and modified
trajectory with a recomputed result hash were rejected without replacing the
current run. Off-grid timing, duplicate rows, empty schedules, running-state
edit locks and add/remove/duplicate actions were exercised through actual controls.
Pause froze body and wing matrices; reset and repeated seek reproduced the same
states without extending the simulation frontier. Restoring the reference
reproduced both original hashes. Narrow document width was 390 and stage width
320, including the expanded editor and long identities. Run collapses the editor
so the viewer remains central. Screenshots and numerical browser evidence are
retained outside Git under `/tmp/neurofly-v8_1`.

V3/v6 advanced 45 body intervals / 9000 neural substeps with 18 gait bones and no
flight wing activity. V7 at 1.94 s retained foot elevation delta
`.0007857500410935088` and knee delta `.018372605582471557` rad; route-off=Base,
sham=ON, other five limbs and body matched. V7.1 retained its 2 Hz reference.
The browser assertion waits for the actual rendered foot to agree with the
scientific inspector after a same-timestamp condition switch, rather than sampling
the previous frame. No historical code or numerical tolerance changed.

Node timings (local environment, means): static normalization .072 ms for 5 rows,
.311 ms for 100 rows; explicit dynamic validation 3.71 / 4.06 ms respectively;
601-boundary reconstruction 3.30 ms; full run import verification 15.0 ms.
Saving a program plus compact completed run took 37.5 ms and used 4099 bytes in
the controlled storage measurement; listing/revalidating them took 21.7 ms.
Browser interactions, including Playwright scrolling/render waits: save program
960 ms, save run 613 ms, program import 50 ms, run import 71 ms. These interaction
latencies are not isolated storage CPU costs.

SwiftShader rendered approximately 4–5 FPS for v8.1. Across three v7.1/v8.1
switches, counters stayed at 313 draw calls, 311 geometries and seven textures;
the editor adds no render geometry, skeletons or textures. Collected JS heap
increased from 13.38 to 15.74 MB during complete mode remounts. Similar remount
growth was already observed in the control; this short test does not establish
leak-free behavior or a v8.1-specific unbounded leak. Low-FPS rendering can alias
the preserved 12 Hz phase. The operator approved its appearance on their own
computer; local evidence here uses software rendering, not a physical-GPU benchmark.

No new 3D trail renderer is introduced: existing generic trails flatten Y onto
the floor. The current viewer follows the actual integrated XYZ body pose, and
the inspector reports the authoritative recorded-boundary metrics. A future
small presentation improvement could render an explicitly three-dimensional
recorded path without changing the plant.

Focused production-browser profiling also rendered/validated all 100 command
cards: internal validation 6.30 ms for five rows and 27.90 ms for 100. Both
schedules imported successfully; at 390 px, even the 100-row editor retained
390 px document width. The original Normal preset remained selected. A sampled
wing application took .3 ms; no new wing mathematics or resources were added.
