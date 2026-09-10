# Phase 1E — full MaleCNS body-to-column contract

**Acquisition date (UTC):** 2026-09-10/11

**Candidate:** `looming_giant_fiber_v1`  
**Dataset:** `male-cns:v1.0`  
**Endpoint:** `https://neuprint.janelia.org`

Phase 1D established D3 independently for LC4 and LPLC2: body-specific
visual-input/optic-column topology is reproducible, but no provenance-verified
MaleCNS column-to-angular-visual-space transform is available. Phase 1E
therefore stores body-specific **column-space input topology only**. It is not a
receptive-field dataset, visual-angle map, encoder, physiological model, or
neural simulation.

## Contract and selection rule

`BodyColumnInputContract` is a separate immutable object linked to the existing
`CircuitContract` by `body_id`. A sparse `ColumnInputRecord` contains:

| Field | Meaning |
| --- | --- |
| `body_id` | MaleCNS body ID |
| `neuron_type` | `LC4` or `LPLC2` |
| `eye_side` | matching `L`/`R` soma side |
| `neuropil` | source optic territory (`ME`, `LO`, or `LOP`) |
| `ol_hex1`, `ol_hex2` | MaleCNS integer column indices |
| `input_count` | postsynaptic input-site count under this rule |

The direct ROI-style `column_id` retains the neuropil and side, for example
`LOP_R_col_12_34`. Per-body summaries retain relevant, assigned, and
unassigned counts, assignment fraction, occupied-column count, neuropil
contributions, and malformed/multiple/unknown assignment counts.

The deterministic NeuroFly selection rule is
`matching_side_optic_primary_post_v1`: postsynaptic synapses, primary-only ROI
semantics, under the matching-side `Optic(L)`/`Optic(R)` hierarchy, with no
geometric or compartment threshold. Missing `olHex1`/`olHex2`, absent or
unknown column keys, side/neuropil/hex mismatches, and multiple column keys are
reported as unassigned rather than fabricated.

## Provenance

- **`malecns_direct`** — body identity, postsynaptic site, primary ROI, side,
  `olHex1`, `olHex2`, and dataset.
- **`published_derived`** — the official MaleCNS optic-column definitions and
  assignments in
  [`optic-column-type-assignments-v1.0.xlsx`](https://github.com/flyconnectome/2025malecns/blob/67767d2233657983993ff6c2be48e836a935863c/supplemental_data/optic-column-type-assignments-v1.0.xlsx),
  inspected at commit `67767d2233657983993ff6c2be48e836a935863c` (SHA-256
  `d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3`).
- **`neurofly_derived`** — sparse counts, summaries, deterministic ordering,
  and coverage statistics.

The workbook uses bilateral `ME_L_col_<hex1>_<hex2>` and
`ME_R_col_<hex1>_<hex2>` identifiers and reference-cell annotations. Its L1/R7/R8
body IDs annotate columns; they are not LC4/LPLC2 receptive-field coordinates.
ME, LO, and LOP source neuropils remain distinct in this contract.

## Method-equivalence gate

Before scaling, the server-side grouped query was run on the frozen Phase 1D
16-body sample and compared with the prior raw `fetch_synapses` result. The
aggregate reproduced **exactly for every body** the relevant, assigned,
unassigned, and sparse `(neuropil, side, hex1, hex2)` count distribution:

| Population | Relevant | Assigned | Unassigned | Result |
| --- | ---: | ---: | ---: | --- |
| LC4 sample | 16,338 | 16,327 | 11 | exact match |
| LPLC2 sample | 14,455 | 14,406 | 49 | exact match |

The equivalence query returned 1,291 grouped rows and the raw query returned
36,072 postsynaptic records. No full-population raw synapse table was used.

## Full live acquisition

All 311 visual bodies from the validated CircuitContract were identity-checked
live (`bodyId`, type, instance, soma side, status, and superclass): 126 LC4 and
185 LPLC2. The full server-side aggregate returned 25,717 grouped rows and
produced 25,438 sparse records. Query counts are recorded in the manifest;
skeletons, meshes, EM volumes, and bulk downloads were zero.

| Population | Bodies | Relevant inputs | Assigned | Unassigned | Assignment fraction | Occupied columns/body |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LC4 | 126 | 277,762 | 277,307 | 455 | 0.998361907 | 36–85 |
| LPLC2 | 185 | 299,773 | 297,438 | 2,335 | 0.992210773 | 54–146 |
| Total | 311 | 577,535 | 574,745 | 2,790 | 0.995169124 | — |

LC4 relevant inputs were almost entirely LO (277,290), with 17 LOP, 2 AME,
and 453 `Optic-unspecified` sites. LPLC2 inputs were 136,730 LO, 159,999
LOP, 709 ME, and 2,335 `Optic-unspecified` sites. All sparse assigned entries
were in ME/LO/LOP; no malformed, multiple-key, or unknown-key assignment was
observed. Unassigned inputs remain legitimate missing data. The largest
descriptive gaps were LC4 body `512366` (58 unassigned; 0.971596 fraction)
and LPLC2 body `31563` (86 unassigned; 0.935435 fraction); neither was
dropped or replaced.

These are column-space topology statistics, not sensory strength, activation,
weights, receptive-field centers, or visual angles. Body-to-body differences
in occupied-column distributions are preserved for future research without
claiming an angular interpretation.

## Offline data product

The ignored artifact is
`data/derived/malecns/looming_giant_fiber_v1/body_columns_v1/`:

- `column_inputs.jsonl` — 25,438 deterministic sparse records;
- `column_body_summaries.jsonl` — 311 deterministic body summaries;
- `column_manifest.json` — schema/provenance/query counts and SHA-256 hashes.

Schema version is `body_column_input_v1`. The recorded file sizes are 3,634,995
bytes and 122,810 bytes; hashes are:

```text
column_inputs.jsonl          4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e
column_body_summaries.jsonl  ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b
```

The artifact is loadable and hash-validated without credentials or network:

```bash
python -m neurofly.malecns inspect-column-snapshot
```

No angular transform was found. The future sensory boundary is therefore **B**:
body-specific column-space encoding may be studied later, but visual-angle
encoding is not currently justified. This phase adds no encoder, neural
dynamics, structural-to-physiological transformation, or DNp01 column data.
