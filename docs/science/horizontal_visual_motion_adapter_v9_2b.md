# Horizontal visual-motion adapter v9.2b: contract-only result

Decision: `HORIZONTAL_VISUAL_MOTION_ADAPTER_V9_2B_CONTRACT_ONLY`.

## Gate A and scope

The authenticated artifacts establish nominal stimulus families, acquisition
timing and speed, but not the modified G3 display controller's anatomical
polarity and exact spatial/temporal masks. No experimental angular-motion
conversion is authorized by this evidence. Gate A stays closed. Gate B contains
only an offline typed descriptor, strict validation, source-byte authentication,
deterministic refusal reports and a CLI. There is no numerical normalizer,
solver execution, body-pose construction or production import.

This is a scientific metadata obstruction, not proof that a bilateral reduction
is mathematically impossible. The prior v9.2a result was partial compatibility:
two sampled angular velocities can be represented by the frozen observer under
virtual geometry, but that neither reproduces a retinal field nor licenses
inventing body poses. That route is deliberately absent here.

The four v9.2 files remain unchanged. Their surrogate/non-comparability
classifications have not been upgraded. No neural agreement, calcium equivalence,
physiological yaw calibration or successful empirical mapping is asserted.

## Baseline and authorities

Repository `a104174/NeuroFly`, branch `main`, local, origin and live remote
`aad4ea60251c1b811046e18834ef56819835bcb6`. Initial state: zero tracked changes,
nothing staged, exactly four intentional untracked v9.2 files. No applicable
AGENTS.md was found in the repository or ancestor directories.

| Preserved v9.2 file | SHA-256 |
|---|---|
| `src/neurofly/empirical_hs_dnp15_benchmark.py` | `947a42774b710d3c46d7df8caf57084286608f6949bf7f9c9e39e00e1db20bfd` |
| `tests/test_empirical_hs_dnp15_benchmark.py` | `ffbb45282061afbe734d979bbffb0b64ad978384b989a353a6d7fbd2b10a2d49` |
| `docs/science/empirical_hs_dnp15_v9_2_source.json` | `0186d88c281119c14f52a1971920ecfbcc4ea24d7315afa5e63f39fefa72b7cd` |
| `docs/science/empirical_hs_dnp15_response_benchmark_v9_2.md` | `a01d12e6896215ddb5c0615a53dc8756c27735fd334a35db9b574143f128ca1b` |

## Experimental source evidence

Erginkaya et al. (2025), *A competitive disinhibitory network for robust optic
flow processing in Drosophila*, DOI
[10.1038/s41593-025-01948-9](https://doi.org/10.1038/s41593-025-01948-9).
Relevant: Figure 1f–h, Extended Data Figure 1, Methods “Visual display and visual
stimuli”, “Visual stimuli design”, “Calcium-imaging data analysis” and
“Optic flow response and discrimination indices”.

Sources inspected again on 2026-10-22; files recovered from the existing external
`/tmp/neurofly-v9-2a` audit directory, with checksums recomputed:

| Artifact | SHA-256 | Evidence used / limits |
|---|---|---|
| Figure 1 XLSX, 9,402 bytes | `b5a36e2363279a1bf908bcdcc9da7dda93ce6710487ceb31add0a284d9db9488` | Sheet 1h: derived ROI DI values, no stimulus masks or polarity |
| `PaperFiguresImaging.m` | `19983ab9378bce5ec975be07fe11dfd08ae246c52dd4213338b5e6817b9f7d17` | Analysis/hemisphere alignment, not the visual controller |
| HS horizontal preprocessed MAT, 4,452,855 bytes | `a50a3c5db2ba993ea9cce8167f646b3189714d8f0b27945aa4991a442a11ef2c` | Pattern labels, 20 px/s, trial timing and processed F/DFF; no compiled pattern raster |

Official workbook:
<https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-025-01948-9/MediaObjects/41593_2025_1948_MOESM6_ESM.xlsx>.
Authors' software at commit `b1b59653a9758335cfff28a81d42010ea6ff082a`:
<https://github.com/ChiappeLab/Erginkaya_et_al_2025>.
MAT source: <https://doi.org/10.5281/zenodo.14967806>, archive member
`data/Preprocessed Data/HS/R27B03AD R39E01DBD sytGC7f 20xUAS6xmCherry/210413/1/t4_concat_responses_OF.mat`.
The prior audit retrieved only selected members using byte ranges; no new archive
download was needed. The full archive is 23,534,730,237 bytes.

The article license is CC-BY-NC-ND-4.0, author software MIT, and Zenodo data
CC-BY-4.0. No separate workbook license is inferred. No source binaries, author
code, calcium records or publisher images are redistributed by this change.

### Verified versus missing stimulus information

Methods specify 216° azimuth, 72° elevation, 2.25°/pixel and a 74° display tilt.
Uniform horizontal rotation is `U = a * omega`, `V = 0`, `a = ±1`.
This does not itself assign anatomical clockwise polarity to stored controller
indices. Figure 1 bFtoB is symmetric horizontal motion; it must not be replaced
with the paper's distinct radial/compound translation equation.

The selected record has 13 conditions, 5 repetitions each, 2 ROIs, 158 samples,
65 trials, F and DFF arrays and explicit left recording hemisphere. It supplies
`DotYaw`, `DotYawRightFlipped`, and Left/Right pattern names. The position-function
filename and `TimeMatSec` describe 2–2–5–2–2-second phases, with 5-second ISI.
Nominal 20 px/s corresponds to 45°/s using display pixel size. Filenames alone do
not establish the physical sign of each epoch or exact unilateral sector edges.
Processed fluorescence is not automatically the publication's z-scored response.
The complete published ROI-to-fly cohort assignment remains unavailable here.

Essential missing evidence: actual study-specific modified G3 generation and
position-function definitions (or compiled pattern plus anatomical calibration),
including exact hemisphere masks, timing of mask changes and angular polarity.
The linked generic Motion_Maker_G4 code is not a substitute for those files.
Measured calcium responses cannot be used to infer these missing stimulus inputs.

## Frozen solver and observer contracts

`experimental_neural_locomotion.advance_neural(state, sides, duration_ms,
components)` is the existing public integration function. `NeuralState` holds six
HS and two DNp15 model states. `SideDescriptors(right, left)` contains bounded,
finite dimensionless proxies in [-1,1], not degrees/s or retinal fields.
`exploratory_course_control.compose_neural_interval` validates them and performs
old-state simultaneous updates. Neural dt is 0.1 ms; a 20-ms interval means 200
substeps; state persists between intervals. This contract-only module never
calls it. No new neuron-specific input is introduced.

`planar_motion_observation.observe_interval` computes two fixed-landmark bearing
changes minus heading change. The normalization is a 50-ms reference window and
hemisphere bases R=+1, L=-1. v9 supplies XZ and yaw, excluding altitude. This is
an engineered geometric observer, not a calibrated binocular retinal estimator.

Pinned source identities remain HS R 10015/10016/10023, HS L
10034/10181/10419, DNp15 R/L 11215/12069. These are structural MaleCNS identities,
not the IDs of the imaged cells. Existing neural contract identity:
`371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074`.
The source artifact raw hash remains
`17d335358a4f5cf4ed98b9682b103a81419cf82504203ce1bc72a7d76285d748`.

## Declarative schema and validation

Implementation: `src/neurofly/horizontal_visual_motion_contract.py`.
`Stimulus` schema: `horizontal_visual_motion_stimulus_v9_2b`.
Adapter identity: `horizontal_visual_motion_contract_v9_2b`.

Required JSON keys (no defaults): `schema`, `adapter`, `source_id`, `source_doi`,
`source_sha256`, `condition`, `original_label`, `coordinates`, `hemisphere`,
`angular_velocity`, `units`, `start_ms`, `end_ms`, `timing_rule`, `mask`,
`aggregation`, `evidence`.

The anatomical declaration is zero azimuth forward, positive toward anatomical
right, radians. This is an explicit engineering coordinate contract, **not a
verified conversion from the source display**. Hemisphere is L, R, bilateral B,
or null. Velocity is a signed scalar for a documented uniform sector/interval,
or null; this limited descriptor cannot yet express a general spatial field.
Units are rad/s or deg/s; neither is converted in this phase.

Optional `Sector(hemisphere,start_rad,end_rad,visible)` entries describe only
known angular intervals. Endpoints lie in [-pi,pi], increasing without wrapping;
L sectors are nonpositive, R nonnegative. Overlaps, side contradictions and
implicit wrap are rejected. Unknown masks remain null. Gaps are unspecified,
never assumed visible. Mask entries preserve false visibility explicitly.

Known time boundaries must lie on the existing 0.1-ms grid. Only half-open
constant hold `[start,end)` without interpolation is declared; unknown boundaries
remain null. This does not claim source events were aligned to that grid.
Unaligned events are refused, rather than silently rounded.

Exactly one `Evidence(field,status,reference)` is required for coordinates,
hemisphere, polarity, velocity, timing and visibility. Statuses are
SOURCE_VERIFIED, DERIVED_FROM_VERIFIED_GEOMETRY, ENGINEERING_ASSUMPTION,
UNRESOLVED or UNAVAILABLE. Caller claims do not authorize execution. `assess`
checks the artifact's actual size and SHA-256 against a small approved identity
registry, then still refuses because those artifacts do not establish Gate A.
Authenticating a workbook does not authenticate a caller's stimulus interpretation.

Only `UNRESOLVED_NO_REDUCTION` is accepted for aggregation. A future bilateral
spatial reduction requires a separate justified contract. All other aggregation
rules are rejected; there is no implicit equal-area or two-point sampling.

### Proposed normalization, not implemented

Matching the frozen observer's mathematical scale would suggest
`u_R = clip(0.050 * omega_R / (2*pi), -1, 1)` and
`u_L = clip(-0.050 * omega_L / (2*pi), -1, 1)` for signed rad/s samples.
This is dimensional engineering reasoning (rad/s to turns per 50 ms), not a
physiological calibration or an approved retinal-field reduction. Source polarity,
visibility and spatial aggregation have not been certified. Therefore there is
no callable conversion, clipping operation or neural execution in this phase.
Neither gain fitting nor source-response normalization is performed.

## Supported and rejected subset

| Condition | Metadata contract | Experimental execution | Reason |
|---|---|---|---|
| Zero motion | supported, velocity may be 0 | SOURCE_METADATA_INCOMPLETE | zero velocity does not establish visibility or presentation baseline |
| Yaw CW/CCW | supported | SOURCE_METADATA_INCOMPLETE | absolute controller polarity and mask not verified |
| bFtoB | supported | SOURCE_METADATA_INCOMPLETE | anatomical field/mask reduction unresolved |
| Left/right unilateral | supported | SOURCE_METADATA_INCOMPLETE | exact side mask boundaries unavailable |

No conditions are source-grounded executable. None produce neural responses or
surrogate traces. Reversal and matched-speed conversion results are not available.
Sector reflection is independently checked analytically: `[a,b] -> [-b,-a]`
and R↔L. This is schema geometry, not proof of a neural sign transformation.
Zero neural substeps is an execution count, not a claim of zero neural activity.
Clipping counts, normalized inputs and model output remain null, not fabricated
zeros. No experimental DI or calcium comparison is produced.

## Reproducibility and CLI

Use an explicit descriptor JSON and the actual approved artifact, kept external:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B \
  -m neurofly.horizontal_visual_motion_contract \
  --stimulus /tmp/stimulus.json \
  --source /tmp/neurofly-v9-2a/figure1.xlsx \
  --output /tmp/stimulus-validation.json
```

The descriptor must supply all required keys; test mechanics examples are in
`tests/test_horizontal_visual_motion_contract.py::descriptor`, clearly labelled
TEST_ONLY. They are not experimental source descriptors. A valid authenticated
scientific refusal exits 0 with SOURCE_METADATA_INCOMPLETE; invalid input,
unsupported identity, corrupt source or output failure exits 2. No refusal is
reported as an empirical match. Output must be outside the repository, is created
exclusively (no overwrite) and contains canonical result content plus SHA-256.
Paths, retrieval date and timings are excluded from scientific identity. No
volatile timestamp or randomness is used. Repeated same-input reports match.

## Validation and limits

New tests cover required fields, unsupported versions/source identities, units,
finite values, timing, sector signs/reflection/overlap, missing masks, evidence
records, deterministic refusal, artifact replacement, existing classification
preservation, no solver call, CLI failures and no overwrite. Synthetic descriptors
test mechanics only. Authentic source bytes are independently hash checked.
Existing benchmark tests exercise actual frozen neural integration separately;
those responses are not attributed to this unimplemented adapter.

No frontend integration exists. Full frontend build/lint/typecheck and full
Python suite are unnecessary for this isolated contract; no such pass is claimed.
Relevant Python reference/provenance checks, v9 TypeScript/Python parity, frozen
runtime verification and canonical replay checks are run separately. No historical
fixtures are regenerated. The original v8 hashes remain the regression authority:
input `25af17966a60f9ed17267d6143cac86b783fd370ca09fef33ee49313177c9f61`,
result `8c8fc14e028a40fbc1aea526f253306bafc827b858a52495f0751168655528b7`.

Fresh local results:

- Final new contract tests: **62 passed** (supersedes initial 61-case run).
- Focused batch: **234 passed**, including the earlier 61-case new-test subset,
  existing 44 benchmark cases, neural-flight reference, neural locomotion,
  HS/DNp15 validation, orientation mapping and composed course control. Counts
  overlap; they are not additive unique-test totals.
- Existing `web/tests/neural-flight.test.ts`: **10 passed**. OFF/projection-zero
  matched all 601 historical boundaries and exact hashes. Independent Python
  neural/observer maximum error: `2.6020852139652106e-18`. This is not independent
  Python validation of a 3D flight plant.
- Repository Ruff check and format verification: passed, 432 Python files.
- Frozen runtime bundle: verified; manifest
  `e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`,
  74 pinned runtime files. Existing isolated provisioned runtime validation:
  eight historical replay gates, five canonical playbacks and HTTP/no-fallback
  checks passed; network and original-checkout writes denied. This preserves
  evidence boundaries, not biological calibration of the new descriptor.
- Whitespace and final Git/preservation checks passed.

Commands (existing environment, no new dependencies):

```sh
NEUROFLY_FIG1_SOURCE=/tmp/neurofly-v9-2a/figure1.xlsx \
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -p no:cacheprovider -q \
  tests/test_horizontal_visual_motion_contract.py \
  tests/test_empirical_hs_dnp15_benchmark.py \
  tests/test_neural_flight_reference.py \
  tests/test_experimental_neural_locomotion.py \
  tests/test_hs_dnp15_neural_validation.py \
  tests/test_orientation_to_horizontal_motion.py \
  tests/test_exploratory_course_control.py
# From web/:
PATH="/home/l1tren/projetos/NeuroFly/.venv/bin:$PATH" \
  PYTHONDONTWRITEBYTECODE=1 node --import tsx --test tests/neural-flight.test.ts
# From repository root:
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m neurofly.runtime_bundle_cli verify \
  --inventory docs/deployment_runtime_inventory_v2.json \
  --manifest docs/neurofly_runtime_bundle_manifest_v1.json \
  --expected-manifest-id e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882 \
  --archive data/derived/runtime_bundles/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B tools/provisioned_runtime_validation.py \
  --manifest docs/neurofly_runtime_bundle_manifest_v1.json \
  --expected-manifest-id e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882 \
  --archive data/derived/runtime_bundles/neurofly-runtime-v2-12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5.tar.gz
```

The external mechanics-only descriptor was obtained with `runpy.run_path` on
`tests/test_horizontal_visual_motion_contract.py`, calling `descriptor()` and
serializing it to `/tmp/neurofly-v9-2b/stimulus-mechanics-only.json`. It never
constitutes measured stimulus evidence. The CLI produced an authenticated refusal
with deterministic identity
`a9fb083eee5275e51f162331727cb2ae2267df5e32549aebeade110fd2ca6ec9`.
Result size: 2,387 bytes, including formatting. Repeated assessment matched.
All six declared conditions were refused; no neural or clipping samples exist.

Over 100 mechanics-only iterations, parsing averaged 0.0146 ms; authenticated
assessment/hash serialization averaged 0.1692 ms with Python allocation tracing.
Peak traced allocation was 81,290 bytes (not process RSS). Neural integration,
normalization and clipping costs are not measured because none execute.
External outputs are under `/tmp/neurofly-v9-2b`; existing source/audit artifacts
remain under `/tmp/neurofly-v9-2a`. No new experimental download was required.

## Smallest falsifiable next step

Acquire and inspect the **actual modified G3 horizontal pattern and position
function** identified by the selected HS record, with anatomical display
calibration. Independent variable: signed frame advance at the documented speed,
under yaw, flipped-yaw and unilateral masks. Reuse this descriptor validator and
the existing solver only after the metadata gate passes. Observable outputs:
signed pixel/angular motion and visible angular sectors, before neural responses.
Controls: zero advance, reversed advance and anatomical reflection. Gate: one
fixed coordinate transformation must predict all three stimulus families'
directions and masks without condition-specific gains or hemisphere changes.
If it cannot, reject the mapping. Do not infer source polarity from calcium or
claim calcium/airborne control calibration even if this geometric gate passes.

No tracked source, model parameters, existing benchmark files, schemas, datasets,
historical hashes, UI, infrastructure or deployments are modified. Only the new
contract module, focused tests and this document are added, unstaged.
