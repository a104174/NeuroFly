# Empirical HS/DNp15 response benchmark v9.2

Phase decision: `EMPIRICAL_HS_DNP15_RESPONSE_BENCHMARK_V9_2_STIMULUS_INCOMPATIBLE`.
The offline inventory/diagnostic implementation passes local validation; a
direct empirical model comparison is blocked by stimulus and observable
incompatibility, so no model-agreement milestone is asserted.

## Scope and scientific outcome

This offline benchmark validates a small published source artifact, extracts its
available descriptive results, and executes the frozen NeuroFly observer and
neural model as explicitly labelled model-side diagnostics. It does not fit or
modify the model. It does not implement a visual-stimulus encoder, a calcium
forward model, a neural solver or a flight plant.

The empirical outcome is `STIMULUS_AND_OBSERVABLE_INCOMPATIBILITY`. Execution of
the benchmark can succeed while all direct model/data comparisons are refused.
This is not a claim that the biological model agrees or disagrees with calcium
measurements. The source provides a relevant observed selectivity result, but
the current sensory and response contracts do not support an equivalent model
selectivity index. No model DI, calcium reconstruction, significance test,
confidence interval or airborne gain calibration is produced.

Baseline: `main`, local and remote
`aad4ea60251c1b811046e18834ef56819835bcb6`, initially clean. This phase adds only
the benchmark module, source manifest, focused tests and this report. Existing
neural equations, visual encoder, flight model, reference hashes, browser code,
wing presets and persistence schemas remain unchanged.

## Primary sources and rights

- Erginkaya et al. (2025), *A competitive disinhibitory network for robust optic
  flow processing in Drosophila*, Nature Neuroscience 28, 1241–1255.
  DOI: <https://doi.org/10.1038/s41593-025-01948-9>.
  Figure 1g/h, Extended Data Figure 1 and Methods sections “Calcium responses to
  visual motion” and “Optic flow response and discrimination indices”.
- Official Figure 1 source XLSX:
  <https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-025-01948-9/MediaObjects/41593_2025_1948_MOESM6_ESM.xlsx>.
  Accessed 2026-10-22. Size: 9,402 bytes. SHA-256:
  `b5a36e2363279a1bf908bcdcc9da7dda93ce6710487ceb31add0a284d9db9488`.
  A fresh official retrieval matched the earlier temporary workbook byte for byte.
- Authors' code:
  <https://github.com/ChiappeLab/Erginkaya_et_al_2025>, inspected commit
  `b1b59653a9758335cfff28a81d42010ea6ff082a`.
  `scripts/matlab/PaperFiguresImaging.m`, SHA-256
  `19983ab9378bce5ec975be07fe11dfd08ae246c52dd4213338b5e6817b9f7d17`.
  Relevant blocks: hemisphere alignment near line 1078, normalization near 1589,
  peak configuration near 2235–2255, peak window near 2383, YawFlipped-Yaw DI
  near 2416–2437. This code was inspected outside the repository, not copied.
- Zenodo <https://doi.org/10.5281/zenodo.14967806> lists `data.zip` at
  23,534,730,237 bytes and a 2,469-byte README. Only the README and record metadata
  were retrieved; the archive was not downloaded. Its README identifies
  preprocessed imaging and behavior data directories, without individually
  downloadable response records in the top-level listing. No inference is made
  about which individual traces could be recovered from the uninspected archive.

The article states CC-BY-NC-ND-4.0, the authors' software is MIT, and the Zenodo
record/README declares CC-BY-4.0 for that dataset. These are separate grants. No
separate license statement was found inside the publisher XLSX. The repository
therefore contains no workbook, extracted individual measurement rows, copied
figures or authors' code. It contains original extraction code, provenance and
factual aggregate findings. Source files and generated analysis remain external.
No article/data license is inferred merely from open access.

## Source inventory

The actual workbook contains a single sheet, `1h`, with four populated rows and
28 populated cells. It is a statistical figure-source table, not an imaging
recording. It has no conventional column-header row identifying animals.

| Cells | Content | Interpretation |
|---|---|---|
| A1 | `bFtoB-Yaw Discrimination index` | Published metric label |
| A2, B2:H2 | DNp15; seven numbers | Individual derived ROI indices |
| A3, B3:R3 | HS; seventeen numbers | Individual derived ROI indices |
| A4 | `p = 0.00076248` | Published statistic; not recalculated |

There are no missing entries inside those declared numerical ranges. Empty
cells beyond H2 are unused layout, not imputed DNp15 observations. There are no
time coordinates, response traces, trial repetitions, named ROI IDs, fly IDs,
hemisphere labels, raw fluorescence, component OF response values, group means,
SEM, SD or CI values. Spreadsheet coordinates are source locations, not
biological identifiers.

Figure 1g/h reports HS: 13 flies/17 ROIs; DNp15: 6 flies/7 ROIs. The caption
describes grand-mean z-scored traces with SEM, derived from 5–10 repetitions.
Those traces and repetition records are not in this workbook. More ROIs than
flies prevents interpreting each ROI as an independent animal. No new
significance test, SEM or CI is justified without the grouping.

Extended Data Figure 1 source data were not retrieved: the selected extraction
target is the Figure 1h DI, and additional figure summaries would not solve
the frozen encoder and observable mismatch. Unilateral and temporal comparisons
are explicitly marked unavailable rather than inferred from figure drawings.

## Measurement-processing audit

The Methods describe fluorescence change relative to the last prestimulus
second, z-normalization, imaging downsampled to 12.2 Hz, hemisphere alignment,
and repetitions averaged per ROI. Preferred/nonpreferred direction is defined
using right HS. OF summaries elsewhere use either 2-second AUC or the final
500 ms of stimulation; these are not interchangeable metrics.

The matching authors-code `YawFlipped-Yaw` block selects the immobilized
preparation, z-scored response traces, a 500-ms peak bin, and time samples
strictly between 3.5 and 4 seconds. It takes direction-epoch mean differences
with direction-dependent signs and divides their difference by the sum of
their absolute values. `YawRightFlipped` denotes the symmetric bFtoB/bBtoF
stimulus condition in that script. Code comments about session normalization
or side-flipping do not substitute for the executed branches and Methods.

This identifies the applicable processing family; the exact generation of the
published workbook cannot be rerun or independently certified from the XLSX.
It omits the component responses, trial metadata and generation settings.
Consequently, the benchmark extracts the published DI and does not claim to
recompute it from calcium data.

```text
DI = (OF_bFtoB - OF_yaw) / (abs(OF_bFtoB) + abs(OF_yaw))
```

Negative DI indicates the yaw OF response exceeds the bFtoB OF response under
that operational definition. Signed values must be preserved. The standalone
arithmetic helper rejects non-finite responses and denominators <= 1e-12; the
benchmark does not call it on neural proxies. Source DI values are finite and
inside [-1, 1].

## Authentic extracted results

| Cell type | ROIs | Flies from caption | Mean DI | Median DI | Range | Negative indices |
|---|---:|---:|---:|---:|---|---:|
| DNp15 | 7 | 6 | -0.640923491691 | -0.689795391032 | [-0.903084551934, -0.213101528000] | 7 |
| HS | 17 | 13 | -0.104303866181 | -0.124047013381 | [-0.653323721047, +0.812582527181] | 14 |

These are descriptive aggregates recalculated from the published derived ROI
indices. They support the factual observation that this source has more
negative DNp15 indices on average. They do not establish a new fly-level effect
size or statistical significance. The workbook's p-value is preserved as a
published value, never as a NeuroFly inference.

## Model and source authority

`neural_flight_reference.neural_reference` supplies the existing observer and
neural reference. It verifies the raw source artifact against
`17d335358a4f5cf4ed98b9682b103a81419cf82504203ce1bc72a7d76285d748`, loads the
frozen composed components, and checks the neural contract identity. The report
records the contract identity returned by that verified call. The selected
MaleCNS neurons remain right HS 10015/10016/10023, left HS
10034/10181/10419, right/left DNp15 11215/12069.

Six same-side structural HS→DNp15 routes support this selected motif. Contact
counts are provenance, not calibrated physiological weights. The model has
three same-side HS proxy states per target and uses their mean. It lacks H2,
bIPS, uLPTCrn/H2rn, recurrent inhibition, lateral disinhibition and electrical
network interactions implicated by the paper. Bilateral output subtraction
does not implement those binocular computations.

The observer calculates changes in the bearings of two static landmarks at
XZ=[+0.6,+0.4] and [-0.6,+0.4], subtracts heading change, normalizes by the
frozen 50-ms convention, applies side bases and clips to [-1,+1]. Y is excluded.
Heading zero is +Z; positive yaw is toward +X. Channel labels are landmark-side
descriptors, not independently controlled eyes. The output has no validated
conversion to fluorescence, voltage or spike rate.

## Compatibility gate

| Publication condition/measurement | Benchmark classification | Reason |
|---|---|---|
| Binocular yaw-like LED visual motion | MODEL_SIDE_SURROGATE_ONLY | Imposed body yaw alters two landmark bearings, without matching a retinal field or LED speed |
| Binocular symmetric bFtoB LED motion | MODEL_SIDE_SURROGATE_ONLY | Self-translation in finite landmark geometry is not an equivalent visual-field stimulus |
| Unilateral left/right FtoB/BtoF | NOT_COMPARABLE | Encoder cannot independently move one visual field |
| Directional calcium traces/amplitudes | SOURCE_DATA_UNAVAILABLE | No such measurements in this workbook |
| Published DI versus a model DI | NOT_COMPARABLE | Stimulus and measurement operations differ; no calcium observation model |

No condition is promoted to DIRECTLY_COMPARABLE or QUALITATIVELY_COMPARABLE
solely because both domains use words such as yaw or translation.

## Supported model-side diagnostics

Seven independent conditions use one second of imposed diagnostic poses: static,
positive/negative yaw, forward/reverse translation, positive/negative lateral
translation. Poses start at [0,0.2,0], yaw zero. Movement occurs over 0.1–0.5 s;
the remaining period is held still. Rates are fixed before comparison:
0.5 rad/s yaw or 0.18 scene units/s translation. These are diagnostic model
parameters, not the paper's visual-stimulus speeds. No per-condition input gain
is introduced.

Each condition resets the real six-HS/two-DNp15 model state to zero. Within a
condition, state is continuous: 50 outgoing 20-ms intervals, 200 neural
substeps each, 0.1-ms neural timestep. Total: 70,000 neural substeps. No
solver resampling, noise or browser clock is involved. Channels and bilateral
neural proxies are recorded at every interval.

`time_s` denotes the input-availability/outgoing-interval start boundary.
`hs_*` and `dnp15_*` values are after integration through
`neural_after_time_s`; readout is the outgoing interval mean. The first
nonzero observation occurs at 0.12 s because motion from 0.10–0.12 s must
complete first. The summary at step 25 is the observation at 0.50 s and neural
response over 0.50–0.52 s. This avoids labelling a future response as a boundary
measurement.

Representative authentic model outputs at that interval:

| Probe | Right input | Left input | DNp15 R proxy | DNp15 L proxy | Mean R−L readout |
|---|---:|---:|---:|---:|---:|
| Static | 0 | 0 | 0 | 0 | 0 |
| Positive yaw | -0.003978873577 | +0.003978873577 | -0.003978873577 | +0.003978873577 | -0.007957747155 |
| Negative yaw | +0.003978873577 | -0.003978873577 | +0.003978873577 | -0.003978873577 | +0.007957747155 |
| Forward | +0.001833394082 | +0.001833394082 | +0.001830646051 | +0.001830646051 | 0 |
| Reverse | -0.001479014310 | -0.001479014310 | -0.001481569547 | -0.001481569547 | 0 |
| Lateral +X | -0.001300148668 | +0.000940561122 | -0.001296843325 | +0.000942780166 | -0.002237942326 |
| Lateral -X | +0.000940561122 | -0.001300148668 | +0.000942780166 | -0.001296843325 | +0.002237942326 |

The yaw probes reverse exactly; symmetric forward/reverse geometry cancels in
the differential readout. Lateral translation produces cross-talk, so the
differential is not inherently rotation-selective. These diagnostics establish
internal mathematical properties. They neither validate biological preferred
direction nor reproduce the paper's neuronal discrimination index.

Zero differential readout under forward motion does not mean DNp15 is silent:
both DNp15 proxy states are nonzero in the table. A downstream bilateral
difference cannot be substituted for the paper's single-ROI OF response.
For constant same-side descriptors, the frozen feedforward equations converge
to HS=input and DNp15=mean(same-side HS). This is an analytical property of
those equations, not a new biological observation. It provides no separate
steady-state network mechanism for enhancing DNp15 selectivity over HS;
transient differences can arise from the different frozen proxy time constants.

## Evaluation and unanswered questions

- Directionality: `MODEL_SIDE_ONLY`. The sign chain is internally consistent;
  this workbook supplies no directional calcium traces for comparison.
- Rotation selectivity: `NOT_COMPARABLE`. There is no legitimate common
  stimulus/measurement operation for a model-versus-paper DI.
- Binocular interactions: `INSUFFICIENT_DATA` for the selected artifact; the
  reduced model additionally omits the paper's important network mechanisms.
- Airborne mapping: `NOT_COMPARABLE`. Immobilized calcium DI cannot calibrate
  the v9 gain, sign or saturation against free-flight angular velocity.

There is no empirically justified compatibility or contradiction classification
for the full reduced model from this source alone. No arbitrary arrays are
presented as the paper's stimuli. No model variability is manufactured.

## Reproduction

Use the existing Python 3.12 environment; no new dependencies are required.
Keep external inputs and outputs outside the repository. The CLI is offline;
it never downloads data or overwrites an existing output. A successful
scientific-incompatibility report exits 0. Invalid source, failed computation
or failed output writes exit 2 with `COMPUTATION_FAILED` and no fabricated result.

```sh
mkdir -p /tmp/neurofly-v9-2
curl -fsSL 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-025-01948-9/MediaObjects/41593_2025_1948_MOESM6_ESM.xlsx' \
  -o /tmp/neurofly-v9-2/official-fig1.xlsx
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B \
  -m neurofly.empirical_hs_dnp15_benchmark \
  --source /tmp/neurofly-v9-2/official-fig1.xlsx \
  --output /tmp/neurofly-v9-2/benchmark.json
NEUROFLY_FIG1_SOURCE=/tmp/neurofly-v9-2/official-fig1.xlsx \
  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest \
  -p no:cacheprovider -q tests/test_empirical_hs_dnp15_benchmark.py
```

The JSON contains a canonical `result` and its SHA-256. Retrieval date, runtime
version and timings are metadata outside that hash. Paths are not scientific
identity. Repeated runs must have identical `result` content; timing metadata
may differ. The CLI also writes a readable `.md` sibling. Neither geometry nor
flight/neural presentation artifacts are empirical source authorities.

The parser is intentionally source-specific. It validates checksum, sheet,
literal labels, exact cells and finite/ranged data. It rejects corrupt ZIP/XML,
oversized members, duplicate addresses, external links, formulas, merged cells,
rich strings, unsupported cell types and hidden sheets. Source SHA verification
prevents silent workbook replacement. Synthetic XLSX fixtures test parser
mechanics only and can never pass the scientific-source checksum gate.

## Local validation and resources

Two independent complete executions produced identical scientific content and
result SHA-256:
`cab52265aab1282d95d30136374a94c46b26e12458776dfff4b36aa3d7a6aca6`.
Timing metadata differs intentionally. The JSON was approximately 130 kB and
the readable report approximately 3.6 kB. Source input was 9,402 bytes. No
large experimental archive or new package dependency was introduced.

Fresh source loading took approximately 0.016 ms; extraction took 1.06–1.08 ms;
seven real-model probes took 1.45–1.46 s. A traced parser run used approximately
145 kB peak Python allocation (3.2 ms with tracing). A whole CLI measurement
took 1.91 s and 43,748 KiB maximum process RSS; this includes Python/NumPy
initialization and the real model, not just parser memory. Readable report
generation took approximately 0.04 ms. These are local observations, not
hardware-independent latency targets.

Validation executed:

- Final benchmark tests with the authentic external workbook: 44 passed.
  Parser synthetic fixtures are never used as scientific inputs. Tests cover
  corruption/unsupported constructs, source replacement, label/layout faults,
  signed values/undefined DI, model determinism and reset, mirror signs,
  unsupported comparisons, external-only output and execution failure.
- Focused Python scientific/regression batch: 212 passed. This batch included
  the initial 32 benchmark cases; the final 44-case benchmark run supersedes
  that subset. Do not add these counts as unique tests. No full Python-suite
  pass is claimed and no missing biological fixture was fabricated.
- `PATH="$PWD/../.venv/bin:$PATH" npm test` from `web`: 304 passed. This covers
  the existing v3/v4/v5/v5.2, gait/motor/wing, flight/program/trajectory and
  neural-flight regression contracts, including Python neural parity.
- From `web`: `npm run lint`, `npm run typecheck`, `npm run build`: passed.
  The build-generated `next-env.d.ts` route import change was restored to its
  original bytes; no frontend file is part of this change.
- `.venv/bin/python -m ruff check .` and
  `.venv/bin/python -m ruff format --check .`: passed (429 files formatted).
- `git diff --check`: passed. No tracked baseline file changed.
- Existing immutable runtime bundle verification: passed, 74 pinned files;
  archive ID `12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`.
- Existing isolated `tools/provisioned_runtime_validation.py`: passed all eight
  historical replay gates, five canonical playback identities, HTTP checks,
  readiness and invalid-pin no-fallback checks. Runtime writes/network were
  denied. The historical release remained read-only.

Scientific-integrity commands used the existing archive and manifest:

```sh
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

The historical v8 input and result identities remained exact:

- Input: `25af17966a60f9ed17267d6143cac86b783fd370ca09fef33ee49313177c9f61`.
- Result: `8c8fc14e028a40fbc1aea526f253306bafc827b858a52495f0751168655528b7`.

Nothing was staged, committed, pushed or deployed. Production and Preview
configuration were untouched. This offline feature requires no browser UI or
renderer changes; no new browser visual acceptance is claimed.

## Smallest next falsifiable follow-up

Obtain an individually accessible Figure 1 stimulus/response subset from the
authors, including fly/ROI grouping, hemisphere, exact LED motion definitions,
and preferred/nonpreferred traces. Before changing any model, specify one
rotation-versus-symmetric-translation benchmark with the authors and test
whether the frozen observer has a defensible mathematical input mapping to
those stimuli. The gate is explicit: if the same mapping cannot produce both
stimuli with common units, side conventions and a declared observable, refuse
the DI comparison. If it can, preregister a qualitative response-ranking test
without fitting; a reversed ranking falsifies that limited prediction. This
does not authorize a new encoder, solver or physiological flight calibration.
