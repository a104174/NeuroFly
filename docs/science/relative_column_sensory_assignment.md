# Phase 7D — bounded relative-column sensory assignment

Phase 7D implements a reproducible **anatomical exposure assignment** for
four predeclared `male-cns:v1.0` sensory bodies. It is a separate experiment
domain from the angular looming encoder and from the neural/motor experiment
artifacts. The terminal output is which source columns are covered and the
resulting body-specific anatomical fractions. It produces no neural input,
neural state, or response.

## Source contract and identity

The input is the existing `body_column_input_v1` snapshot for
`looming_giant_fiber_v1`. The loader verifies its identity, the pinned source
file hashes, its manifest's official-resource identity, and the associated
CircuitContract identities before assignment. No body-column table is copied
into the Phase 7D artifact.

The fixed set is:

| Body | Type | Side |
| ---: | --- | :-: |
| 12032 | LC4 | L |
| 16128 | LC4 | R |
| 11498 | LPLC2 | L |
| 14465 | LPLC2 | R |

The source `column_inputs.jsonl` SHA-256 is
`4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e`; the
`column_body_summaries.jsonl` SHA-256 is
`ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b`. The
column manifest SHA-256 is
`6acc1a8266ed71d4f1373e5ab61a3bcd1a00e95045ab3ede870efa2f8d61f302`.
The corresponding pinned CircuitContract source hashes are recorded in the
artifact configuration. The fixed source-contract identity is
`874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21`.

The official MaleCNS optic-column workbook is pinned to
[flyconnectome/2025malecns commit
67767d2233657983993ff6c2be48e836a935863c](https://github.com/flyconnectome/2025malecns/blob/67767d2233657983993ff6c2be48e836a935863c/supplemental_data/optic-column-type-assignments-v1.0.xlsx),
SHA-256 `d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`.
It classifies 880 left and 892 right medulla columns. The two valid source-only
left LO/LOP coordinates `(17,34)` and `(19,35)` remain in the source grid but
unclassified; the calculation neither drops them nor invents a class.

## Synthetic stimulus and lattice

The distinct model identity is `relative_column_expanding_disk_v1`, with
stimulus schema `relative_column_stimulus_v1`. The spatial domain is integer
`MaleCNS_hex_lattice_steps`; there are no degrees, radians, distance, object
size, or physical angular expansion rate. For `hex1=q`, `hex2=p`, lattice
distance is

```text
max(abs(delta_p), abs(delta_q), abs(delta_p - delta_q))
```

This gives the six published neighboring offsets
`±(1,0), ±(0,1), ±(1,1)`. A disk is the set of valid source/workbook
coordinates on its explicitly named side whose lattice distance from its
center is no greater than the integer radius. Left and right are independent
coordinate systems: a unilateral stimulus activates only the grid for its
declared side. No mirror or cross-eye alignment is applied.

The fixed experiment contains four stimulus configurations and ten stored
samples:

| Stimulus | Side | Center `(hex1,hex2)` | Radius schedule | `dt_ms` |
| --- | :-: | --- | --- | ---: |
| `left_expand_33_29` | L | `(33,29)` | 1, 2, 3, 4 | 0.1 |
| `left_lplc2_11498_18_04` | L | `(18,4)` | 2 | 0.1 |
| `right_expand_23_09` | R | `(23,9)` | 1, 2, 3, 4 | 0.1 |
| `right_translate_23_11` | R | `(23,11)` | 2 | 0.1 |

The expansion is a discrete synthetic schedule, not a calibrated looming
trajectory. Each stored integer step is authoritative; `time_ms` is derived
from `step * dt_ms`, not used to select a sample. The translated center is a
separate stimulus, not an eye-to-eye transform.

## Anatomical exposure calculation

For one body's source records `R`, active same-side coordinate set `S`, and
source `input_count` values `w_r`, the result stores:

```text
column_overlap_fraction
  = count(records r in R whose (hex1,hex2) is in S) / count(R)

structural_input_site_overlap_fraction
  = sum(w_r for matching records) / sum(w_r for all assigned records)
```

The first is record-based: source records retain their neuropil identity, so
the same coordinate in different neuropils remains more than one record. The
result also contains `unique_hex_overlap_fraction` as a separate location-
based summary. The second fraction uses exact assigned MaleCNS source-site
counts; the number of unassigned relevant sites is reported separately and
is not silently allocated. Both fractions are dimensionless anatomical
summaries in `[0,1]`. Source counts are structural/anatomical weights only,
never synaptic efficacy, response gain, firing probability, or physiology.

At every sample each of the four body identities is present. Bodies on the
other side of a unilateral stimulus receive exact zero exposure by the
explicit side rule. A malformed side/type/count, invalid or unknown stimulus
coordinate, invalid time/radius, source hash/identity mismatch, or zero
denominator fails closed. The fixed experiment cannot be changed to add
bodies or substitute a different stimulus schedule under the same identity.

## Artifact and replay

The new immutable artifact schema is
`relative_column_sensory_assignment_artifact_v1`; it does not modify
`experiment_artifact_v1` or `motor_pathway_experiment_artifact_v1`. The
artifact contains canonical `config.json`, `assignment_result.json`, and
`manifest.json` files. Configuration records the exact four bodies, source
and workbook identities, per-stimulus config hashes, discrete sample grids,
and semantic limitations. The result stores each active column set and its
hash, plus per-body source coverage/counts and exposure at each sample. It
does not duplicate the 311-body source contract.

Content identity is deterministic: canonical JSON payload hashes feed the
artifact ID and manifest. Export is atomic and refuses to replace an existing
artifact. `load` checks file set, canonical encoding, payload lengths/hashes,
manifest, and artifact identity. `replay` reloads the pinned local source and
workbook, regenerates the exact config/result, and requires equality. These
operations require no network access once the ignored local source files are
present.

```bash
python -m neurofly.relative_column_assignment_cli generate
python -m neurofly.relative_column_assignment_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/relative_column_assignment_v1/<artifact-id>
python -m neurofly.relative_column_assignment_cli inspect \
  data/derived/malecns/looming_giant_fiber_v1/relative_column_assignment_v1/<artifact-id>
```

The generated artifact is ignored under `data/derived/malecns/`; the
official workbook is ignored under `data/raw/malecns/`. Neither is staged or
committed.

## Bounded result

The generated run is
`404473c66c36b9f0332a203928200552c6c2e5490af446caae6c3d7475daafbe`, with
schema `relative_column_sensory_assignment_artifact_v1` and ten samples. The
left and right expanding disks each have four samples; the left LPLC2-centered
and right translated disks each have one. The active-set sizes are 7 and 56
for left radii 1 and 4; 7 and 44 for right radii 1 and 4; 13 for the left
LPLC2-centered disk; and 19 for the translated right disk.

The following values are the record-overlap / structural-site-overlap
fractions. Phase 7C's reported values were rounded; this table gives the
Phase 7D recomputation from the pinned source.

| Stimulus sample | LC4 12032 L | LC4 16128 R | LPLC2 11498 L | LPLC2 14465 R |
| --- | ---: | ---: | ---: | ---: |
| L `(33,29)`, radius 1 | .093333 / .161330 | 0 / 0 | 0 / 0 | 0 / 0 |
| L `(33,29)`, radius 4 | .626667 / .756979 | 0 / 0 | 0 / 0 | 0 / 0 |
| L `(18,4)`, radius 2 | 0 / 0 | 0 / 0 | .210526 / .389952 | 0 / 0 |
| R `(23,9)`, radius 1 | 0 / 0 | .106061 / .198706 | 0 / 0 | .095238 / .119202 |
| R `(23,9)`, radius 4 | 0 / 0 | .651515 / .822054 | 0 / 0 | .533333 / .669903 |
| R `(23,11)`, radius 2 | 0 / 0 | .287879 / .468320 | 0 / 0 | .352381 / .534520 |

Artifact file SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `config.json` | `ed079b55dcff3ceabe31db5c130a4d230830d29e7dcd1d970aee6b274544049e` |
| `assignment_result.json` | `788722537019c5dc501892e63141c5ab2df5c1ba383090c253c049c23b997b46` |
| `manifest.json` | `5ab77fb3fd94b598441c22134768e5f90698a2086e260e1ed35eafddee5c0c14` |

## Scientific boundary and next gate

**Source:** MaleCNS body/type/side, neuropil-column records, and assigned
input-site counts.

**Model assumption:** the synthetic relative-column disk centers, side,
integer radii, and sample schedule.

**Derived anatomy:** active column membership, record overlap, unique-hex
overlap, and structural-site overlap.

**Unknown:** absolute visual angle, functional LC4/LPLC2 receptive-field
centers and widths, sensitivity/gain, response transfer, and individual
neural dynamics.

The result demonstrates body-specific input addressing only. It does not
modify the current type-level `lc4_drive_mveq` or `lplc2_drive_mveq`, combine
them with exposure, or feed a neural model. It adds no threshold, event gain,
voltage, spike, DNp01 effect, or biological response claim. The angular
looming encoder, DNp01, TTMn, existing experiment artifacts, and frontend are
unchanged. The 313-neuron individual-dynamics milestone is not achieved.

The bounded Phase 7E question is whether and how an anatomical exposure could
be transformed into an explicitly exploratory body-specific neural input for
these same four bodies, with an explicit model-assumption contract and
sensitivity; exposure itself must not be renamed as neural input or response.
