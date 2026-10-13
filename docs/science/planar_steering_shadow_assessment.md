# Planar steering v0 — scientific assessment

## Identity and scope

Initial source: clean `main`, local/remote
`8b050b5f5bda9f3418a594a8ddd60a2b4d6ea734`.
Experiment: `HS_DNP15_PLANAR_STEERING_VALIDATION`.
Preregistration canonical SHA-256:
`49e91a10fa49c5d7004f28249b63f334a0e23767c20108f5578a0e2586c9767a`.
The operator reports recording the preregistration before implementing the new
operator; independent prospective chronology is not verified. The declaration
flags and uncommitted file identities cannot prove this ordering. No
observation parameters, geometries, trajectories or effect expectations were
retuned after outputs. See `planar_steering_shadow.md` for the analytical gate.

This is an offline engineering-geometry / frozen neural-proxy experiment.
It does not establish autonomous movement, biological steering efficacy,
walking, calibrated retinal sampling or physical yaw velocity.

Selected MaleCNS sources: R 10015/10016/10023; L 10034/10181/10419.
Targets: DNp15 R 11215, L 12069. All six routes, structural counts and the
original source/target kernels remain unchanged. Structural counts are
provenance, not gains. Four original kernel file hashes are pinned and checked.

## Operator and protocol

World: +X right, +Z forward, arbitrary `world_eq`. Heading uses one abstract
cycle per model revolution. The fixed reference bearing is `atan2(X,Z)`.
For a completed interval:

`shift_eq = shortest_world_bearing_change/(2*pi) - delta_heading_eq`

`descriptor_side = clip(side_basis * 50 ms * shift_eq / dt_ms, -1, 1)`

The R/L bases are +1/-1, reused from the frozen Course observation convention.
Full raw motion, normalization, clipping and prescribed cause are retained.
No biology-derived length or gain is claimed. Swept landmark singularities,
ambiguous half-cycle intervals and invalid values fail explicitly.

Twelve conditions each contain 501 boundaries, dt=0.1 ms, duration 50 ms.
Initial x/z/heading are zero. A linear prescribed excursion occupies the first
20 ms, followed by 30 ms held pose: +/-0.1 world_eq for translation or
+/-0.001 heading_eq for rotation. Every expanded pose is stored as
`ENGINEERING_PRESCRIBED_POSE` in configuration and telemetry.

Symmetric references are R=(2,4), L=(-2,4). Asymmetric references are R=(2,2),
L=(-2,4). The mirrored condition swaps these depths and mirrors X.

Observation [n-1,n] is available at boundary n. HS and DNp15 update from old
states, so the first motion observation is at n=1, HS response at n=2 and
DNp15/readout response at n=3. This is model indexing, not measured latency.
The final observation is stored but not consumed. Final outgoing increments,
route contributions and target drives are null. No output is integrated into
the prescribed body pose and no forward-speed channel exists.

## Results

No prescribed interval clipped in any of the twelve conditions. Independent
tests exercised saturation and verified explicit raw/bounded metadata.

| Condition | Peak absolute HS | Peak absolute DNp15 | Signed differential extremum |
| --- | ---: | ---: | ---: |
| Stationary symmetric | 0 | 0 | 0 |
| Positive rotation | .002454210903 | .001904025990 | -.003808051981 |
| Negative rotation | .002454210903 | .001904025990 | +.003808051981 |
| Positive X translation, symmetric | .007931542474 | .006126395839 | -.012120962818 |
| Negative X translation, symmetric | .007931542474 | .006126395839 | +.012120962818 |
| Positive Z translation, symmetric | .004028868689 | .003097611583 | 0 |
| Negative Z translation, symmetric | .003788579566 | .002965615308 | 0 |
| Positive Z translation, asymmetric | .010148022631 | .007785768701 | +.004688157118 |
| Negative Z translation, asymmetric | .009397437894 | .007373290431 | -.004407675123 |
| Mirrored positive Z, asymmetric | .010148022631 | .007785768701 | -.004688157118 |
| Sham positive Z, asymmetric | .010148022631 | .007785768701 | +.004688157118 |
| Readout disabled positive Z, asymmetric | .010148022631 | .007785768701 | +.004688157118 computed; enabled readout 0 |

First asymmetric positive-Z descriptors: R=.009948427444851764,
L=.003979271501132434. Its final differential is .0005257579794051543.
Magnitude has no calibrated biological interpretation or arbitrary pass threshold.

Sham telemetry is exactly identical to intact. Readout-disabled retains exactly
the same poses, observations, HS/DNp15 states and computed proposal; only the
exposed enabled shadow readout is zero. Mirror swaps targets and reverses the
differential exactly under the existing proxy symmetry. All nine runtime
control checks pass, including per-boundary equality to prescribed pose input.

Selected neural-route interruption is **unavailable** with the unchanged kernel,
which rejects altered route inventories. No route ablation was implemented and
readout disconnection is not described as neural ablation.

### Negative findings and interpretation limits

Symmetric longitudinal motion is observable but gives exactly zero steering
differential. This is a required negative control, not absence of all neural
response. Backward/forward translation magnitudes need not be equal because
bearing sensitivity depends on depth.

An independent test constructs a translation interval and a rotation interval
with the same two descriptors. Causes are recorded from prescribed poses;
the operator does not generally identify motion type from output. The experiment
therefore validates traceability in this restricted model, not a complete
optic-flow decoder, biological motor law or autonomous locomotion.

The independent review found maximum full-record reconstruction discrepancies
below 2.5e-14 for descriptors and below 2.2e-15 for neural states, against the
declared 1e-12 tolerance. This verifies numerical/model behaviour, not physiology.
The observation is an engineering geometric construction, not a calibrated fly
retina. All three HS states within each hemisphere were identical; the current
protocol does not establish distinct anatomical-route contributions.

Two descriptors generally cannot identify three unknown planar motion components.
Symmetric geometry admits exactly equivalent rotation/translation observations;
asymmetric geometry does not generically solve this information deficit. Clipping
adds ambiguity while preserving raw values and flags. Cause labels come from
prescribed inputs, not neural inference. Biological anatomical-route necessity,
physical angular velocity, forward propulsion and autonomous locomotion remain
unestablished. Sham and readout-disabled controls do not establish motor actuation.

## Reproducibility

Python 3.12.3, NumPy 2.5.3. Configuration contains the full preregistration,
expanded pose arrays, geometry, frozen component contracts, authority document
contents, existing source-artifact configurations/paths/identities and exact
source software hashes. Random policy NONE, seed null.

Canonical JSON uses the repository helper: sorted compact keys, default ASCII
escaping, `allow_nan=False`. Artifact files add the declared terminal newline;
config/result hashes do not. Complete replay, not merely rehashing, rejects
semantically modified records, even if their envelope is rehashed.

External artifact directory:

`/home/l1tren/projetos/neurofly-science/work/planar-steering-v0/a9b2924f432e6faceafb3b7e995d762c2123747165707ed2ce7f97855f981abd/`

| Identity | SHA-256 |
| --- | --- |
| Artifact ID | `a9b2924f432e6faceafb3b7e995d762c2123747165707ed2ce7f97855f981abd` |
| Configuration | `6a372a958673046e2a7f718e089fd6ca1de3cdfa07b49bf0d8639b23fa0d8b13` |
| Result | `3cfb9e7dadb4614819f2fb9456cb16226bce433ddf1ef84ceafa997653727d80` |
| `shadow.json` file, including newline | `ab4f53939fe15fc9efcd68e60f04ef58b73e366ad1a31435f345204b29539edc` |

Files: `shadow.json` (13,425,357 bytes) and `manifest.json`; total 13,425,771
bytes. They remain outside Git and outside the frozen D2.2 runtime. No prior
artifact was overwritten. The exporter rejects repository-internal output roots.

From the repository root:

```bash
.venv/bin/python -m neurofly.planar_steering_validation \
  --output-root /home/l1tren/projetos/neurofly-science/work/planar-steering-v0
.venv/bin/python -m neurofly.planar_steering_validation \
  --replay /home/l1tren/projetos/neurofly-science/work/planar-steering-v0/a9b2924f432e6faceafb3b7e995d762c2123747165707ed2ce7f97855f981abd
```

## Gates and preservation

Focused tests: 37 passed. Analytical signs, Course rotation reduction, rigid
coordinate invariance, branch seam, singular geometry, finite values, ordering,
clipping, kernel parity, old-state timing, control comparisons, complete input
recovery, deterministic replay and tamper rejection are covered.

Full canonical Python suite: **1341 passed, 1 deselected**, in 916.92 s.
The deselected authenticated integration test follows the existing default
pytest policy. Two dependency deprecation warnings concern Starlette/httpx
and the AnyIO portal alias; no dependencies or test expectations were changed.
Ruff check, format check and final diff check: **passed**.
No frontend gate is required: no frontend, API, visual or deployment files changed.

Independent read-only loader checks returned `VALIDATED_CANONICAL_REPLAY` and
the exact frozen hashes:

| Scenario | Boundaries | Canonical payload SHA-256 |
| --- | ---: | --- |
| BASELINE_CONTROL | 15 | `75d1f2856f0d896589a8b1f62fb61016d701045b760e216b7cb5fa70daa30668` |
| LOOMING_CIRCUIT_VALIDATION | 15 | `c3387396dcffa6372287df1a7d4680bb7ba605df319af4cf10f140cfc3a4d223` |
| LOOMING_WORLD_EXPERIMENT | 401 | `d06ef32aaf054b981464948916e5687951b40f571be5286513dad8ae440f26df` |
| HORIZONTAL_MOTION_NEURAL_VALIDATION | 501 | `52554962f3e9c85c6866b5e3ec56f8a12d24340db2236ec52c7809c6ece8d404` |
| EXPLORATORY_COURSE_CONTROL | 501 | `7fddc1109495023d8f64744237796d5d8e86852abef80b6979f1994088d46806` |

No existing scientific source, canonical scenario, API, arena, GLB or frontend
implementation was edited. No installation, staging, commit, push, deployment
or provider operation occurred.

Gates A (numerical operator), B (neural/control traceability) and C (reproducibility
and canonical preservation) pass. Final decision:
`PLANAR_STEERING_SHADOW_VALIDATED`.

The independent scientific review returned
`PLANAR_STEERING_SHADOW_REVIEW_PASS_WITH_LIMITATIONS`. The focused consolidation
adds independent mixed-motion and ambiguity regression tests, clipping ambiguity,
expanded contradictory-metadata checks and prescribed-pose isolation. None changes
the existing numerical experiment or authorizes body feedback.

The original 37-test and 1341-test results above describe the initial implementation
run. Consolidation verification is recorded below after the final gates.

Propulsion feasibility and the single next recommended scientific slice are in
`locomotion_propulsion_feasibility.md`; no controller is specified or implemented.
Propulsion remains NOT_DEFINED. This result is not autonomous walking or
biological validation. The six files were local and unstaged at the time of the
initial implementation assessment; publication is a separate consolidation gate.

## Scientific consolidation verification — 2026-10-13

The focused suite now has **45 passing tests** (eight additional cases), including
independent mixed-motion endpoint equations, independently specified equivalent
rotation/translation, saturation ambiguity, contradictory geometry/identity/grid/
random/readout metadata after rehashing, and independent prescribed-pose checks.
The registration test checks declarations and authority identity, not chronology.
Full suite: **1349 passed, 1 deselected**, 868.88 s; the default authenticated
integration-test exclusion remains unchanged. The two dependency deprecation
warnings above persist. Final targeted rerun: 45 passed. Ruff check and format
check passed; no tests, dependencies or existing scientific thresholds weakened.

Read-only semantic replay of the original external artifact passed with the same
artifact/configuration/result identities listed above. Its raw file and manifest,
the JSON preregistration, both new experiment modules and all four frozen kernels
remain byte-identical to the independently reviewed implementation. No observation
equation, experimental condition, output or body-actuation pathway was changed.

All five canonical playback payloads were loaded through the existing semantic
validation path, yielded VALIDATED_CANONICAL_REPLAY and matched the hashes above.
The existing 16-node/18-edge motor source authority and manifest replay passed.
The official annotation snapshot checked in memory matched its historical source
SHA-256. Read-only runtime bundle verification passed with manifest
`e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`.

Candidate inventory is exactly six existing scientific files plus the new
`locomotion_propulsion_feasibility.md`. All are small text files; no external
experiment artifact, raw dataset, credential, frontend/API/deployment change or
body controller is included. Publication requires final diff/index and remote
checks. Consolidation does not remove the independent review's scientific limits.
