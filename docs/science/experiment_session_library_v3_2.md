# Experiment Session Library v3.2

A browser-local product capability for continuous navigation v3 sessions and
v3.1 paired neural-output counterfactuals. No neural equation, source identity,
propulsion, boundary policy or historical artifact is changed. Persistence does
not imply simulated learning, biological memory or physiological validation.

## Contract and storage

IndexedDB `neurofly-experiment-library`, database version 1, store `sessions`
with UUID `id` key. No dependencies, server API, remote database or cloud sync.
Record schema `experiment_session_library_v3_2` contains:

- Stable local UUID, independent revision UUID, trimmed 1–100-character name,
  ISO creation/modification timestamps. Duplicate names and duplicate scientific
  runs are allowed; saves always insert a new record, never overwrite by name.
- Original validated import/session identity as `source_session_id`.
- Complete v3 initial configuration and event log (including pending request,
  stop boundary and termination), config/log/result hashes and logical identity.
  Initial HS/DNp15/body states and all source pins are in the existing config.
- Small duration/intervention/distance/mode summary, verified when saving and
  checked again when opening. Paused prefixes are labelled, never extended to 30 s.
- Optional comparison schema, parent identity, configuration and logical hashes.
  No stored poses, completed telemetry or full neural-state histories.
- SHA-256 of finite sorted-key canonical record content. Hashes detect accidental
  corruption, not authentication or proof of authorship.

A portable JSON import first passes the original v3 semantic validator, including
rehashed contradictory telemetry rejection. Its supplied trajectory is never
applied. The browser recalculates the run and stores its own exact deterministic
fingerprints, retaining the original import identity separately. This avoids
pretending cross-runtime rounding produces byte-identical identities.

Opening checks record version, fields, metadata, hashes and summary consistency,
then reconstructs from validated inputs using the actual pinned v3 simulator.
All config, log, result and logical identities must match the recorded local
reconstruction; distance must agree as well. A different runtime producing a new
identity fails closed, with JSON portability available; there is no speculative
migration or automatic identity replacement. Pending requests remain pending.

## Scientific time and cooperative replay

Existing fixed 0.1 ms neural transitions, exactly 200 per 20 ms body interval,
old-state updates, current-pose observation and geometric controller are reused.
The existing navigation replay validation/transition sequence is expressed once
as an internal generator. Historical callers consume it synchronously as before;
library operations can yield every 50 completed body intervals. The v3 semantic
validator has an optional cooperative scheduling flag, default false. This is
scheduling only: same events, order, model state, arithmetic and output identity.
No worker, alternative solver, rendering-time numerical step or new controller.

List rendering performs lightweight record/hash checks without neural replay.
Only a requested save, import, open, export or comparison reconstructs a run.
Save/rename/comparison-reference changes use one read-write transaction, and
success is announced after `oncomplete`. Quota/blocked/unavailable/aborted writes
produce an error, retain the current session and leave JSON export available.
Database version changes close old connections. Focus refreshes listings; a
revision comparison inside the write transaction prevents stale-tab overwrite.
Rename also checks the revision originally selected in the UI. Corrupted rows
remain visible as unavailable records and can be explicitly deleted.

## Comparisons and dependency policy

The published `generatePair` implementation reconstructs ON/OFF independently
from the stored parent log. It keeps all external interventions and parameters
matched and suppresses only the application of neural steering in OFF. Neural
computation and each world's own-pose observation remain active. No sensory trace
or computed contact history is prescribed. The comparison reference must agree
with its regenerated version if already saved.

Reference metadata lives inside the parent record, so there are no orphaned
comparison records. Delete requires an explicit confirmation explaining that
both the record and dependent reference will be removed. It never removes the
current live state or exported files. Comparison trajectories are regenerated,
not cached in IndexedDB. Portable full comparison exports retain the existing
v3.1 semantic-validation format. Returning from comparison restores the saved
original, and switching/reopening comparisons resets the comparison cursor safely
without mounting another GLB or changing the scientific timebase.

## User flow and limitations

`My Experiments` is a collapsible section in both live v3 and paired inspection.
Save with a name; reopen, compare, rename, export, import or confirm deletion.
Opening and saving pause live computation at its recorded boundary. Save while
inspecting a comparison stores its recoverable parent plus comparison reference.
The arena, fly, cameras and historical modes remain shared.

Storage is scoped to the exact browser origin. Different protected Vercel Preview
hostnames, browsers and devices have separate libraries. Clearing site data or
using private browsing can discard records. No cross-origin synchronization,
stable-domain change or protection setting change is implied. Exported v3 JSON
is the existing portable recovery mechanism and contains no browser credentials.

## Validation

Focused tests exercise compact inputs, exact deterministic reconstruction,
interventions/neural continuity, comparison references, OFF readouts, names,
UUIDs, atomic IndexedDB callbacks, quota/duplicate-key abort, revision conflict,
confirmed dependency deletion, unavailable storage, unknown schemas, malformed
records, rehashed contradictory model/result/summary metadata and cooperative
replay equality. A small test-only IDB event fixture covers transaction branches;
real browser IndexedDB and reload are separately exercised end to end.

Frontend lint, typecheck, tests and production build are mandatory. Python code
and tests are unchanged; the trustworthy baseline is 1692 passed, one existing
integration deselection and two dependency deprecation warnings. Read-only focused
Python reference checks and the 74 frozen D2.2 file hashes are revalidated. No
historical scientific output is regenerated. Protected Preview acceptance checks
a genuine intervened session, save/reload/open, comparison reconstruction and
identity, return, rename, portability, invalid import rejection, confirmation,
local storage errors and desktop/narrow layout. Deployment evidence is external.

Local final gates: 181 frontend tests, eight focused persistence tests, 14 focused
Python reference tests, lint/typecheck/build, Ruff and diff checks passed. A real
intervened browser session survived reload with exact final neural/body state,
source result identity and regenerated comparison identity. Real IndexedDB quota
abort, unavailable storage and unsupported record-version paths passed. Names,
portable import/export, rehashed false telemetry rejection, rename, comparison
reference persistence and explicit cascading deletion were exercised on desktop
and 390 px width. No runtime errors occurred.

A separate local 30 s run stored 4,011 bytes: import/semantic validation/save
875 ms, open/reconstruction 337 ms, ON/OFF reconstruction 1,069 ms, five-record
metadata refresh 49 ms. Five input records require roughly 20 KB, not five full
trace histories. JS heap samples 38→87 MB include the GLB, generated trajectories
and temporary validation/export objects before GC; these are not storage size or
proof of a leak. These measurements used concurrent headless SwiftShader browser
workloads and are not a physical-GPU benchmark. Protected Preview figures are
recorded separately after publication.
