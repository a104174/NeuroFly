# Phase 2H-A — empirical constraint infrastructure

Phase 2H-A implements the metadata and provenance boundary defined by the
Phase 2G protocol. It does not contain experimental arrays, download logic,
calibration, fitting, or an observation model.

## Registry and identity

The tracked metadata-only registry is:

`data/reference/empirical_constraints/constraint_registry_v1.json`

It contains the 14 Phase 2G constraint records and no third-party source
traces. `neurofly.empirical_constraints.ConstraintRegistry` loads it offline,
validates the closed vocabularies and the exact Phase 2G roles, orders records
by `constraint_id`, and exposes two deterministic SHA-256 identities:

- `protocol_sha256`: the locked protocol version, partition, roles, and
  transform declarations;
- `registry_sha256`: the canonical protocol plus all metadata records.

The registry is immutable in memory. It never stores a numerical payload. A
future `PayloadReference` stores only a project-relative path, checksum,
format, parser identifier, receipt timestamp, and neutral source-contact
reference.

Inspect it without network access:

```bash
python -m neurofly.empirical_constraints inspect
```

The current registry reports 14 constraints and three qualitative records
that are comparison-ready. All three numeric fit constraints remain
`PENDING_SOURCE_DATA`.

## Scientific state model

`ConstraintRole` is intentionally independent of `AvailabilityStatus`.
Therefore a future fit record can remain `FIT_CONSTRAINT` while its data are
`PENDING_SOURCE_DATA`.

- `PENDING_SOURCE_DATA`: requested/expected source data are not locally
  usable; no payload reference is allowed.
- `PENDING_REVIEW`: a received file is represented, but identity, schema,
  units, timing, normalization, uncertainty, checksum, and reuse terms are
  not all verified. It cannot be comparison-ready.
- `FIGURE_ONLY_NOT_EXTRACTED`: published visual evidence is deliberately not
  digitized; a payload reference is rejected.
- `AVAILABLE_VERIFIED`: numerical fit/held-out records require a payload
  reference, checksum, and `PERMITTED` or `RESTRICTED` reuse status. This
  status does not itself imply biological validity.
- `UNAVAILABLE` and `WITHDRAWN_OR_UNUSABLE`: the record remains in the
  protocol but cannot enter comparison.

`ReuseStatus` is separate from scientific availability. `UNKNOWN` and
`PENDING_CONFIRMATION` prevent payload redistribution or comparison-ready
use. `RESTRICTED` permits local validated use without implying that the file
may be committed or redistributed.

`is_comparison_ready()` is a gate, not a fitting API. Numeric fit/held-out
records require verified payload metadata and a comparable modality. A
qualitative record can be ready with a declared qualitative relation and no
numeric array. Context-only and not-directly-comparable records are never
ready for numeric comparison.

## Locked Phase 2G partition

The protocol identifier is `empirical_constraint_protocol_v1` and its version
is `phase_2g_v1`. The loader rejects missing, extra, overlapping, or
role-mismatched IDs. The canonical protocol identity includes every ID and
role, so changing a role changes the hash. The production loader also rejects
any registry that differs from the Phase 2G inventory.

Fit constraints:

- `ACHE19_LC4_GF_ISOLATED_WAVEFORM`
- `ACHE19_LPLC2_GF_ISOLATED_WAVEFORM`
- `KLAP17_LPLC2_DARK_LOOM_SPEED_SERIES`

Held out:

- `ACHE19_ISOLATED_PEAK_TIMING`
- `ACHE19_COMBINED_GF_WAVEFORM`
- `VREYN14_GF_FIRST_SPIKE`

The qualitative, context-only, and not-directly-comparable groups are encoded
as their Phase 2G roles; no qualitative null is promoted into a numeric fit.
The isolated Ache 10 ms condition remains part of the held-out timing record,
as specified by Phase 2G, rather than becoming a new mutable record.

## Observation-transform boundary

The registry represents only narrowly declared transforms:

- source-declared baseline subtraction;
- source-matched normalization;
- declared smoothing, including Ache's 10 ms waveform and 1 ms peak-timing
  declarations;
- semantic time-reference conversion.

Transform declarations are immutable, versioned, and included in protocol
identity. Numerical execution is intentionally deferred where source edge
semantics or observation models are incomplete. Raw data, when eventually
received, must remain separate from transformed comparison data.

The transform validator rejects free time shifts, free per-trace amplitude
scales, figure digitization, guessed calcium-to-voltage conversion, and
normalization against a model-derived maximum. No generic “best alignment” is
available.

The Ache approximately 19 ms record is registered as
`GF_RESPONSE_LATENCY` with `NOT_DIRECTLY_COMPARABLE`. It cannot be converted
automatically into an E1 latency, chemical delay, or LIF parameter.

## Future author-data workflow

1. Register the source metadata and received file as `PENDING_REVIEW`.
2. Verify DOI/source identity, exact experiment and figure relation, format,
   columns, units, time reference, replicate identity, normalization,
   uncertainty semantics, reuse terms, and SHA-256.
3. Store third-party raw files locally/ignored by default. Do not commit them
   unless redistribution permission is explicit.
4. Promote the record to `AVAILABLE_VERIFIED` only when the payload reference
   and checksum are complete and reuse status is compatible.
5. Run deterministic comparison only through the locked role and transform
   declarations.

No email ingestion, external download, calibration, optimizer, or fitting is
implemented.

