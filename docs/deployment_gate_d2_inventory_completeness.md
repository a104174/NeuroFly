# Deployment Gate D2 — Runtime inventory completeness stop

## Decision

`D1_RUNTIME_INVENTORY_INCOMPLETE`; D2 status `BLOCKED`.

D2 requires both an exact D1-only bundle and all required historical replays
from a clean provisioned root. The corrected Phase 16 diagnostic artifact is
not in D1's 66-file inventory. These requirements cannot both pass without an
explicitly authorized inventory extension. No inventory was silently refreshed.

## Repository / authority gate

Initial clean `main == origin/main`, application commit
`17bc772d11214ca40b02868982f1c9b20295c42c`: D1 and Phase 33 committed.
Initial `git diff --check` passed.

Committed D1 inventory canonical SHA-256:
`edd7d36d4d4a9adcbc3df33a98dd5d474b8516f40074c8551faf8f4092ea82e2`.
Its stored-file SHA-256 is
`2e2719b09852164bdda97dac0f6ef3cd75f68670f6f531b1f70ae21bc1dc9b95`,
identical to the committed Git blob. All 66 listed inputs exist and match their
exact byte counts and hashes: 84,575,845 bytes. The required 111,565-byte
optic-column assignment XLSX is among them.

## Scope discrepancy, not a scientific mismatch

D1 explicitly describes its inventory as files observed while loading the five
product playbacks, not a complete cloud bundle specification. The Phase 16
diagnosis is a separate historical authority, not an active scenario input.
Its absence from the observed five-scenario inventory is therefore consistent
with D1's stated methodology, but insufficient for D2's broader historical
replay acceptance gate.

Corrected Phase 16 canonical artifact ID:
`bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b`.

Under repository-relative directory:

`data/derived/malecns/looming_giant_fiber_v1/dnp01_subthreshold_diagnostic_artifact_v1/bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b/`

| Omitted file | Bytes | SHA-256 |
| --- | ---: | --- |
| diagnostic.json | 90,631 | e24335e0d44486857222e1b76f4fb3dc7ca1e7e78862eaecf641db4a5839f208 |
| manifest.json | 439 | 592dee368d13ea694a3a9c9e4bc72f0e47750be531d05c41b64c654ce7a1aded |

The existing local files pass canonical diagnostic JSON serialization,
manifest/file-integrity equality, and config/result content-hash checks. They
were not regenerated or copied into the isolated inventory. Adding them would
require at least 68 data files and 84,666,915 bytes. That is a minimum candidate
extension, not a claim that the complete historical dependency closure has now
been proven.

## Isolated evidence

A new temporary working directory outside Git was populated by copying ONLY
paths enumerated by the committed D1 inventory, preserving relative paths.
An independent directory scan verified exactly 66 data files, no extras, all
84,575,845 bytes and all original hashes. No data symlinks or links to the
developer's data tree were added.

The existing Python package was supplied via PYTHONPATH for this diagnostic;
this was a dependency-completeness probe, not a completed standalone backend
release. The command ran with the isolated working directory, so its relative
data lookup could not fall back to the repository's data tree:

```sh
python -m neurofly.dnp01_subthreshold_diagnostic_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/dnp01_subthreshold_diagnostic_artifact_v1/bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b
```

Result: exit 2, `Subthreshold diagnostic error: unexpected diagnostic artifact
file set`. The existing replay helper requires `diagnostic.json` and
`manifest.json` at that directory before it can validate/replay the result.
The files are absent because neither is authorized by D1's inventory.

## Work deliberately not performed

No archive, bundle manifest, provisioning helper, readiness endpoint, container
image, storage object, upload or deployment was created. No scientific files,
source datasets, equations, parameters, replay semantics or authority IDs changed.
No provider selection, credentials or per-request downloads were introduced.
Existing `/health` liveness semantics remain unchanged; readiness work is pending.

All-five playback verification and the remaining historical replays in the
isolated release, deterministic archive/security tests, build/verify/extraction
benchmarks, and full Python/frontend quality gates are NOT_RUN after this stop.
No D2 PASS or completed provisioning claim is made. Focused inventory/hash and
isolation checks above were performed; lint/format/diff results are reported in
the final handoff. Full gates remain required on a subsequent successful D2 run.

Only this documentation file is added. D1 documents remain unchanged. Temporary
inventory-copy data lives outside Git; no generated scientific bundle is tracked.
No Git commit or push was performed.

## Next bounded action

Authorize a separately versioned supplemental deployment inventory covering the
corrected Phase 16 artifact and the complete required historical replay closure,
while preserving D1's frozen observed inventory. Then resume deterministic bundle
creation from the explicitly authorized union, with isolated replay validation.
