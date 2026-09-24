# Phase 7B — bilateral column-to-optical-ray registration assessment

**Audit:** 2026-09-24. **Target:** `male-cns:v1.0`,
`looming_giant_fiber_v1`, `body_column_input_v1`.
**Decision:** `COLUMN_SPACE_ONLY`.

This is a bounded, read-only source audit, not an angular registration or an
encoder. The [Phase 7A contract](bilateral_retinotopy_feasibility.md) supplies
body-specific **anatomical column-input topology** for all 126 LC4 and 185
LPLC2 bodies. None of those indices is a visual angle. The source audit below
found optical rays and a published registration *method*, but no reproducible,
independently validated pairing from either MaleCNS v1.0 column lattice to
those rays. Thus no MaleCNS body is assigned an angular anatomical centre.

## Source inventory and reproducibility

All downloaded research files were kept in the untracked temporary directory
`/tmp/neurofly-phase7b.AzkSCa/`, not in the repository. URLs identify the
exact bytes inspected on 2026-09-24; repository revisions are pinned where
available.

| Source | Specimen/dataset and side | File, size, SHA-256 | Meaning |
| --- | --- | --- | --- |
| [MaleCNS bilateral workbook](https://raw.githubusercontent.com/flyconnectome/2025malecns/67767d2233657983993ff6c2be48e836a935863c/supplemental_data/optic-column-type-assignments-v1.0.xlsx), commit `67767d2233657983993ff6c2be48e836a935863c` | adult male `male-cns:v1.0`, L and R | `optic-column-type-assignments-v1.0.xlsx`, 111,565 B, `d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3` | Column identities, photoreceptor references and column classes; no optical rays. |
| [Zhao et al. 2025](https://www.nature.com/articles/s41586-025-09276-5), [released code/data](https://github.com/reiserlab/eyemap_T4/tree/99d2a43123db636cedb55af9ff31a59657e7d17e), tree `99d2a43123db636cedb55af9ff31a59657e7d17e` | adult female µCT, **both eyes**; adult female FAFB EM, **right** medulla | `lens.csv`, 82,071 B, `477fbef0bd60c0a340aded55770c73ddae9fb4a5baf73738bf7ea9c128599c0f`; `cone.csv`, 84,009 B, `a2d1b6f5b8296e6fb6a26a7d0bdf96ccba1260923ca2a81fb0b1123f2557c355` | 1,709 lens positions and 1,709 photoreceptor-tip positions across the two µCT eyes, **not** MaleCNS column keys. |
| [Zhao analysis source](https://github.com/reiserlab/eyemap_T4/tree/99d2a43123db636cedb55af9ff31a59657e7d17e) | same specimens | `proc_uCT.R`, 11,235 B, `ba96990c55887a5e046323f5ea6e58e676f92de5909c0ef08ba10a4bc9acf65f`; `proc_eyemap.R`, 16,098 B, `35c0d8d48a67ea6bd11237464f01a6e87f13146e07baef7ad863ec1e8795df6d`; `eyemap_func.R`, 27,327 B, `d139cd26ef5aa2ef60b54236b399a1eaef8cc3ce0c95d7026884d34c68d948ac` | Optical-axis and right FAFB Mi1↔µCT lens correspondence workflow; no MaleCNS key join. |
| [LPLC2 study](https://www.nature.com/articles/s41586-025-09037-4), [source-data archive](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-025-09037-4/MediaObjects/41586_2025_9037_MOESM4_ESM.zip) | visual assays and right male optic-lobe EM subset of the MaleCNS specimen | ZIP, 1,359,082 B, `252406a8b7b3f8f3c7811651739c895102d9816f56976cc0949b76c1c31424ca` | Figure source-data workbooks; no keyed position-16/40 column/ray correspondence was found in the archive. |
| [Nern et al. 2025](https://www.nature.com/articles/s41586-025-08746-0) and [MaleCNS publication](https://doi.org/10.1016/j.cell.2026.08.015) | right male optic-lobe v1.1 and bilateral MaleCNS v1.0; optic-lobe subset is the same EM specimen | publication/official project, not a downloaded data file | Column-lattice and population eyemap methods, not released v1.0 bilateral optical-ray table. |
| [Official `ol_annotations`](https://github.com/flyconnectome/ol_annotations) and [visual-pathways analysis](https://github.com/reiserlab/visualpathways/tree/23f6ac131529b5f56894c6eeb9b88b17894fc00d), tree `23f6ac131529b5f56894c6eeb9b88b17894fc00d` | cross-dataset type matches; MaleCNS relative optic-lobe coordinates | read-only small text/source files (inventory in temporary directory) | Type/group matching and relative H/V coordinates, not a one-to-one MaleCNS column→optical-ray release. |

No released file inspected here supplies a table whose rows pair
`ME_L/R_col_h1_h2` with an ommatidium optical unit vector. The µCT lens and
tip positions are an optical source, not such a pairing. A browser SVG or a
figure image is not a machine-readable key/angle contract. No full synapse or
connectivity dataset was downloaded.

The six additional `visualpathways` source files inspected under the pinned
tree above have raw-URL prefix
`https://raw.githubusercontent.com/reiserlab/visualpathways/23f6ac131529b5f56894c6eeb9b88b17894fc00d/`:

| Relative path | Bytes | SHA-256 |
| --- | ---: | --- |
| `docs/coordinate-systems.md` | 1,025 | `3537f9d2d909731b448c1b00e7f149bdea2e9d3a12ef818abfb4a1667145494c` |
| `src/setup_data/malecns.py` | 22,210 | `e134458bc16c26ca7db6edd324dda715c480cad03694738ffe6620d7e4b90a20` |
| `src/utils/external_rf.py` | 5,080 | `0533e62df97d9c0cbbaf624f1f3b37dfefa758164035b3813780ef41e8fc9bff` |
| `src/utils/hex_hex.py` | 2,829 | `a7b21cecf332cd941c8c834c2fe92c2b1297bc3bd09a9419e31cdb3f9c951df5` |
| `src/utils/ol_data.py` | 38,522 | `2b9a300a01674cfaea117fb7d553ea8eb9df29ddd5b9f7e44c49e52076672abd` |
| `src/utils/ol_rf.py` | 45,800 | `ef698065770b6a8e262e613b49f97d3eb1bcab9f53c0a8fc68f24f73480e09ff` |

## Published eye-map method and coordinate conventions

[Zhao et al.](https://www.nature.com/articles/s41586-025-09276-5) identify a
µCT lens centre and photoreceptor-tip position per ommatidium. Their released
`proc_uCT.R` pairs these points, normalizes lens-minus-tip into a viewing ray,
and orients the head from bilateral lenses and photoreceptor chirality. In its
canonical frame, +X is forward, +Y is left, and +Z is up; the released
`eyemap_func.R` expresses elevation above the equator and azimuth with left
positive. This convention is **for that optical specimen and analysis**;
NeuroFly does not assign it to MaleCNS columns.

The EM-side equator is identified from lamina cartridges with seven/eight
photoreceptors rather than the usual six; µCT chirality identifies its
counterpart. The approximate central meridian bisects the hex map and is
associated with the optic chiasm. Paper/code align lattices using those
landmarks and discrete hex-neighbour correspondence, then interpolate missing
locations on the unit sphere. Their `proc_eyemap.R` explicitly restricts the
lens set to the **right** µCT eye before joining with FAFB Mi1 locations; its
Mi1/lens indices do not designate MaleCNS columns. The optical source has
bilateral facets, but a bilateral *EM-column correspondence* is not released.

The authors report residual/model agreement for their own matched FAFB map,
not a held-out error for MaleCNS v1.0. Equator-row ambiguity, peripheral
unmatched columns, differing specimen geometry/sex, and potential eye
orientation changes prevent treating their fit precision as a MaleCNS
uncertainty bound. `ol_annotations` matches cell types/groups across datasets,
not individual column or LC4/LPLC2 body identities. No FAFB body or lattice
index was substituted for a MaleCNS one.

## MaleCNS grid and male-specific anchors

The pinned bilateral workbook has **892 right** and **880 left** unique
`ME_<side>_col_<olHex1>_<olHex2>` keys. Both coordinate fields range from 1 to
36/39 respectively. These are axial/topographic column indices, not degrees.
The R sheet contains 79 `edge` and 42 `DRA` columns; L has 74 and 40. The
reference IDs `L1`, `R7`, `R8` can be `-99` when missing; R has 0/201/188
missing and L has 8/272/255 respectively. The workbook does not contain an
equator/central-meridian field or optical unit vectors. Edge/DRA labels are
useful potential landmarks but do not fix the sign, origin or angular scale
of a MaleCNS-to-eye correspondence. The two sides have different coverage;
their keys are handled independently, never by an unverified mirror.

The [LPLC2 male optic-lobe study](https://www.nature.com/articles/s41586-025-09037-4)
uses stimulus positions **16** (dorsal) and **40** (ventral), matched to
ommatidia on a Mollweide map and male optic-lobe columns through T4 input.
It nominates right-side LPLC2 bodies **28871** and **30207** respectively;
both exact IDs are present in NeuroFly's MaleCNS `body_column_input_v1` and
313-body circuit. This is a valuable same-specimen *body identity* clue, not
a calibrated anchor row: the inspected paper/supplement/source-data archive
did not provide a recoverable pair `(MaleCNS column key, numerical ray)` for
either position. A stimulus-grid number alone does not define a viewing ray.
The right-only pair also supplies no independent left-side validation.

## Registration attempt, validation, and uncertainty

The preferred algorithm would be: (1) retain each MaleCNS side's discrete
column lattice and source IDs; (2) use directly documented equator/meridian
and column↔ommatidium anchors to choose a topology-preserving lattice
correspondence, separately on L and R; (3) look up the released µCT unit ray
of each *matched* ommatidium; (4) reserve independent keyed anchors to measure
great-circle angular error; (5) propagate edge, missing-site,
inter-specimen, handedness and registration residual uncertainty. Continuous
interpolation would apply only after discrete identity is justified. An
arbitrary affine fit of hex coordinates, raw EM XYZ→angle projection, or
unverified L/R mirror is not an acceptable replacement.

**Execution stopped before step 2.** The required MaleCNS column↔µCT
ommatidium correspondences and numeric male-study anchor pairs are absent
from the inspected release. There are **0 fit anchors and 0 independent
held-out anchors** per side. Per-anchor, median and maximum angular errors
are therefore **not estimable**, not zero. An angular uncertainty interval
cannot be honestly bounded; the mapping is unresolved. The known optical
source's own error does not fill this missing cross-specimen registration
error.

| Side | MaleCNS columns | `DIRECT_SOURCE_RAY` | `VALIDATED_DERIVED_RAY` | `ASSUMPTION_DEPENDENT_RAY` assigned | `UNRESOLVED` | Held-out anchors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| L | 880 | 0 | 0 | 0 | 880 | 0 |
| R | 892 | 0 | 0 | 0 | 892 | 0 |

No assumption-dependent ray is *assigned*: a proposed mirror or guessed
translation would be an unevaluated assumption, not a useful derived result.
The source-to-optical-ray mapped coverage is zero on both sides, although
body-to-column topology remains complete for all 311 sensory bodies.

### Four-body bounded proof

The fixed body-column snapshot was joined by exact body ID. A source column
means a distinct neuropil/side/hex key. `mapped` counts columns with a
validated optical-ray pairing, **not** columns in the official workbook.

| Body | Side/type | Source columns | Input sites assigned/relevant | Optical-ray mapped columns | Mapped structural sites | Anatomical angular centre/spread | Tier |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 12032 | L / LC4 | 75 | 2,436 / 2,477 | 0 / 75 | 0 / 2,436 | not estimable | `UNRESOLVED` |
| 16128 | R / LC4 | 66 | 3,709 / 3,710 | 0 / 66 | 0 / 3,709 | not estimable | `UNRESOLVED` |
| 11498 | L / LPLC2 | 95 | 1,254 / 1,263 | 0 / 95 | 0 / 1,254 | not estimable | `UNRESOLVED` |
| 14465 | R / LPLC2 | 105 | 1,854 / 1,859 | 0 / 105 | 0 / 1,854 | not estimable | `UNRESOLVED` |

Mapped structural-site fraction is **0** for each body. Neither an
unweighted spherical mean nor a `STRUCTURAL_INPUT_WEIGHTED_ANATOMICAL_CENTRE`
was calculated: both require mapped unit rays. Were they available, the
former would average one unit vector per distinct column and the latter would
weight each ray by the body's source input-site count, normalize the vector
sum, and report spherical angular spread and missing-site coverage. Averaging
azimuth values directly would be wrong at the ±180° seam. Structural counts
would describe anatomical input distribution only, never sensitivity, synaptic
efficacy, or physiological response gain. No estimator was selected to make
an unsupported centre appear plausible.

## Decision, future contract, and 313-neuron gate

**`COLUMN_SPACE_ONLY`.** The original MaleCNS topology is robust, and the
Zhao method demonstrates that optical rays and discrete lattice registration
are scientifically possible in another specimen/dataset. The audited release
does not provide a reproducible, bilateral, independently testable MaleCNS
v1.0 key→ray transform. This is a bounded **source-availability conclusion**,
not proof that such a registration can never be produced.

A future `VisualColumnRayV1` is justified **only as a proposed contract**:
dataset/version, side, exact neuropil/column key and hex indices, optical
specimen, unit ray, azimuth/elevation convention, mapping tier, landmark
set, per-side residual/uncertainty, missingness, transfer assumptions, and
source hashes. A separate `NeuronAnatomicalVisualFieldV1` would retain exact
body/type/side, source columns/site counts, mapped fraction, unweighted and
structural-weighted spherical summaries, angular spread, and uncertainty.
Neither is created or populated in Phase 7B. Anatomical centre is not a
functional receptive-field centre or gain.

The **smallest Phase 7C** is an official-source/author-data recovery gate:
obtain a machine-readable, keyed MaleCNS L/R column↔ommatidium correspondence
or sufficient named, numeric anchors, with explicit orientation and held-out
validation. If unavailable, retain column-space-only semantics and do not
individualize the encoder. Only after (1) validated column→ray registration
may NeuroFly derive (2) body anatomical visual fields, then separately
validate (3) functional RF/input model, (4) individual neural dynamics, and
(5) circuit-level results. The current 126 LC4 + 185 LPLC2 remain type-drive
consumers; the two DNp01 bodies remain individually simulated. **313 explicit
sensory/descending dynamics are not achieved.** No source, model, artifact,
frontend, or experiment behavior was changed; the model remains not
empirically validated.
