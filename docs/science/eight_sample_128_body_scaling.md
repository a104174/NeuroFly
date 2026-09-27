# Phase 7M — deterministic eight-sample 128-body composition

Phase 7M composes four existing samples (A–D) with four new deterministic
samples (E–H) into one simultaneous 128-body exploratory experiment. It is a
final bounded doubling and architecture/performance gate, not a new selection
study after model outcomes and not biological validation.

## Gate and immutable parents

The repository began clean on `main` at `6fc85d721cf9234baa8bced8826e312ae7db8bc4`,
matching `origin/main`. Before selecting E, the canonical Phase 7L full replay
returned the unchanged 64-body artifact
`5095eddbf35c363cf4ae47ef875420ecad725eb0c837767ec8789e65bd68ab02`, with
64/64 software-path coverage, 19 stimuli, and a 14,848,847-byte artifact.
Phase 7L's A–D selection, composition, 19-stimulus battery, and 64-body
experiment remain immutable.

The source identity remains the Phase 7L-pinned MaleCNS v1.0 body-column
contract SHA-256 `874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21`.
Its column-input and summary file hashes are
`4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e` and
`ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b`; the
CircuitContract neuron/connection hashes are
`00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e` and
`f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a`. No
source data were downloaded or committed in Phase 7M.

Samples A and B are the persisted Phase 7H and 7J artifacts. C and D are the
persisted Phase 7L artifacts. Phase 7M does not reconstruct any of them:

| Parent | Artifact ID | Bodies |
| --- | --- | ---: |
| A | `18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7` | 16 |
| B | `873d6e9e32ce08916fb69462548af11f2cbadf394d91966641e6bc17839bcf33` | 16 |
| C | `bd10225993d0101d9a2338e7d18dac772fa4ab9096938de14930ea14df47c301` | 16 |
| D | `3609c165476f524b8187aed5400421cdd1ca1862fd5b3ab0e5cba2d90a95abe2` | 16 |

## Outcome-blind sample selection

E, F, G, and H were selected and persisted in that order. Each was replayed
before selecting the next one. Each stratum excludes all earlier samples,
sorts remaining candidates by MaleCNS structural DNp01 edge-count descriptor
then body ID, partitions the ordered list into four balanced groups using
`floor(rank * 4 / candidate_count)`, and selects one body in each group by
maximum minimum relative hex-centroid distance from prior allocations. Exact
distance ties use the smallest body ID. The persisted source/anatomical
descriptors include each body's type, side, target route, structural count,
anatomical centroid, rank, and maximin-distance metadata. Structural counts
are used for rank stratification only, never as efficacy.

No sensory-state, transferred-drive, DNp01 membrane, or spike result is an
input to sample selection. Every new sample records
`model_outcomes_used=false`.

| Sample | LC4-L | LC4-R | LPLC2-L | LPLC2-R | Artifact ID |
| --- | --- | --- | --- | --- | --- |
| E | 518016, 17608, 20976, 512366 | 31262, 28945, 19543, 18127 | 19830, 531014, 29753, 520764 | 27566, 33396, 24118, 21808 | `311ebc053a677618d0155812395d04a4995e39a06b93a9c67ecbefca3e512b92` |
| F | 107513, 28980, 511914, 17478 | 21165, 22034, 16628, 17668 | 17544, 24308, 27355, 34407 | 35632, 34681, 19146, 24187 | `915b7a1a1fd3d1072f760e7b52400f19e1fcfcbaf81d516abba3f797c7aef9ee` |
| G | 20440, 30087, 517752, 515476 | 21151, 20917, 21225, 22847 | 13764, 25209, 33406, 19787 | 20584, 29216, 17551, 23497 | `4fc1f3a6f25b06d240ed0fad87e16bbc6825f176f5212992dd5558caf8fe7e5a` |
| H | 520449, 31429, 31301, 17653 | 19260, 19420, 16138, 21336 | 32223, 32237, 27716, 22253 | 34372, 31257, 26393, 20162 | `5dea356903c85950e1f87729c6bedbb591419bb4ba9ae689761f24add1d0d754` |

The maximin/rank descriptors are preserved in the immutable sample artifacts,
including all selected-body centroids and structural counts. All eight
samples are pairwise disjoint (28 pairwise checks, each overlap 0).

## 128-body composition and coverage plan

The composition artifact
`d77ed3bf0db9d09b66e047fc349cee1b29bff59459d5d6b5639f695ef2cc983c`
references exact parent artifacts A–H and contains 128 unique bodies: 32 each
for LC4-L, LC4-R, LPLC2-L, and LPLC2-R. CircuitContract resolves all 128 direct
routes, 64 to DNp01 10010 and 64 to DNp01 10001. No target is inferred from
array position or side alone.

Before sensory or DNp01 dynamics, the complete persisted Phase 7L battery
(19 stimuli) was audited against the 128 source body-column distributions.
It anatomically covered 119/128 bodies; the nine initial misses were
17478, 19543, 20917, 22847, 24187, 27355, 31257, 107513, and 515476. The
source-column set-cover planner used binary `column_overlap_fraction > 0`,
side-specific real source columns, and integer radii 1–4. It added four
radius-1 disks, minimizing stimulus count, then total radius, then using the
deterministic centre/radius tie-break:

| Added stimulus | Side | Centre `(olHex1, olHex2)` | Bodies covered |
| --- | --- | --- | --- |
| `coverage128_l_18_30_r1` | L | (18, 30) | 27355, 107513, 515476 |
| `coverage128_l_24_11_r1` | L | (24, 11) | 17478 |
| `coverage128_r_07_12_r1` | R | (7, 12) | 19543, 20917, 31257 |
| `coverage128_r_24_33_r1` | R | (24, 33) | 22847, 24187 |

Thus the persisted plan contains 23 stimuli (the original 19 unchanged plus
these four) and reaches anatomical stimulus coverage for all 128 bodies. Its
artifact ID is
`2e0750448f72640b0231c3efe5638235ceddada459821cb31ccc9ce7795d922d`.
The plan records that no model outcomes were used and no neural dynamics had
been computed.

## Experiment, models, and checks

The experiment artifact
`3d0ec7e8ddf5baf00449f6452d538d995978b571da5ea9efc632b91228d5dcc6`
uses the same reference assumptions as Phases 7E–7L:

- sensory state: `relative_column_exploratory_sensory_state_v1`,
  `tau_sens_ms=1.0`, `gain=1.0`, `x0=0`,
  `column_overlap_fraction`, with the same exact exponential update and
  integer-step timing;
- transfer: one shared `k_transfer=1.0 mV_eq/state` and
  `d_i[n] = k_transfer * x_i[n]`;
- DNp01: the existing two-neuron LIF configuration, unchanged;
- population normalization: none.

MaleCNS structural edge counts remain provenance only and do not enter
exposure, sensory state, gain, tau, transfer, or DNp01 drive. Every source
contribution is identity-resolved; target drive is checked against the sum of
per-source ledger entries at every stored interval. The experiment records
85,760 ledger rows and 1,340 per-step source-accounting plus 1,340 A–H
additivity comparisons.

The 128-body assignment has 35 samples over 23 stimulus identities. It
achieves 128/128 `BODY_STIMULUS_COVERED`, 128/128
`BODY_STATE_EXERCISED`, and 128/128 `BODY_TRANSFER_EXERCISED`. These are
software-path coverage facts, not biological RF coverage.

For the combined reference condition at `k=1`, DNp01 10001 has peak drive
0.462801 mV-equivalent and maximum model Vm −51.983209 mV; DNp01 10010 has
0.660487 mV-equivalent and maximum model Vm −51.976018 mV. Neither spikes.
The `k=0` condition has zero transfer drive and holds both modeled neurons at
−52 mV. At `k=2`, peak drives are 0.925602 and 1.320974 mV-equivalent,
respectively, with maximum Vms −51.966419 and −51.952036 mV; neither spikes.
These are assumed-model outputs, not physiological estimates.

The A–D-only mask reproduces all 19 corresponding Phase 7L per-source
contributions and DNp01 drive/membrane/events. Its combined bilateral
reference condition also matches the canonical Phase 7L `all64_reference`.
Samples A–D reproduce their sensory trajectories for all shared stimuli;
new samples E–H each match standalone sensory-state recomputation over all 23
stimuli (368 body/stimulus checks per sample). The per-step A–H ledger sum
matches the stored target drive. The `no_sources`, LC4-only, LPLC2-only,
left-only, right-only, A–D-only, E–H-only, all-128, and `k=0` controls are
present. The only sensitivity values are `k=0`, `1` (reference), and `2`.

## Artifact identities and reproducibility

Artifacts are content-addressed canonical JSON with separate config/result
hashes. All files are ignored under
`data/derived/malecns/looming_giant_fiber_v1/`.

| Artifact | Schema | ID | Config SHA-256 | Result SHA-256 | Bytes incl. manifest |
| --- | --- | --- | --- | --- | ---: |
| Sample E | `bounded_sensory_scale128_sample_artifact_v1` | `311ebc053a677618d0155812395d04a4995e39a06b93a9c67ecbefca3e512b92` | `81e0a7547b0f2ad241c023714e48f73e582d9cb025529e451b6ce786e37153a5` | `088f6da5cd7a8d5e62d887e829c07b9de4a544be8cb9111a5eb90d6a17919916` | 24,736 |
| Sample F | `bounded_sensory_scale128_sample_artifact_v1` | `915b7a1a1fd3d1072f760e7b52400f19e1fcfcbaf81d516abba3f797c7aef9ee` | `01384d58ba9a5c9df6ebb3536a46b0ba1a51699a032fd73846bec6a31a3ebbf2` | `5512362966c4bd98dd07ed4c3c28e0364b5bb17a8f15e64c3ddad32444d34cb4` | 26,384 |
| Sample G | `bounded_sensory_scale128_sample_artifact_v1` | `4fc1f3a6f25b06d240ed0fad87e16bbc6825f176f5212992dd5558caf8fe7e5a` | `5ffef59c3f63e0b8553918a78cea51c2c689e9f9da15ef1bf239e79ada50de78` | `5a9fff63985ebc5a1502d2e81e16f86ebf31ac64f7218c954ffe05562746b6d9` | 28,046 |
| Sample H | `bounded_sensory_scale128_sample_artifact_v1` | `5dea356903c85950e1f87729c6bedbb591419bb4ba9ae689761f24add1d0d754` | `d91e6ba169b1f0f1a0408f6f563557a04ed6657297d85a10c3fb2624870e6b5c` | `d059b0151e1d1e7c1c2b7403581256023595f9283e513770342d2a74dd3aa939` | 29,675 |
| A–H union | `bounded_sensory_composition128_artifact_v1` | `d77ed3bf0db9d09b66e047fc349cee1b29bff59459d5d6b5639f695ef2cc983c` | `18999e2a93b30bb1a55bddb256a0b4a933dbcfe6c631032d62cb66fb51a5b66a` | `5ebb85be2bc13c6b5746b18a77048de46d69c6ad6ea6359d5d32f96ccd2e25d9` | 130,474 |
| Anatomy-only plan | `bounded_sensory_coverage128_plan_artifact_v1` | `2e0750448f72640b0231c3efe5638235ceddada459821cb31ccc9ce7795d922d` | `d846df35f655e6a5912b58be56b52a3304d8253e90179e5b389e39e3afe52939` | `9e8e8412260bcaeba9c8c9b6f3f83745d35d6d2b2cf4b4facfd063c66b2fd142` | 86,620 |
| 128-body experiment | `bounded_sensory_population128_artifact_v1` | `3d0ec7e8ddf5baf00449f6452d538d995978b571da5ea9efc632b91228d5dcc6` | `ffdd914eb703aef94820632dbf3129c430519ca1e29b10e31e28269f2151e82a` | `f51903bba2911b1f74a712b5325730ec36f19108f176fcb06a5b6b8f8a2ce998` | 31,446,708 |

Full replay validates pinned MaleCNS contracts, A–D, E–H selection,
composition, the persisted anatomy-only plan, assignment, sensory state,
routing, transfer, DNp01 output, nested regression, and artifact identity.
Replay returned the same 128-body artifact ID and hashes. The CLI workflow is:

```bash
python -m neurofly.bounded_sensory_scale128_cli samples-generate
python -m neurofly.bounded_sensory_scale128_cli composition-generate
python -m neurofly.bounded_sensory_scale128_cli coverage-plan-generate <composition>
python -m neurofly.bounded_sensory_scale128_cli experiment-generate <composition> <coverage-plan>
python -m neurofly.bounded_sensory_scale128_cli experiment-replay <composition> <coverage-plan> <experiment>
```

## Scaling and performance

These are wall-clock observations from the existing phase workflows in the
current environment, not controlled benchmarks. Replay chains and stored
conditions differ by phase. The 128 run extends the 64 run with four stimuli
and three additional conditions; its source ledger scales from 41,728 to
85,760 rows as the body count doubles.

| Bodies | Artifact bytes | Stimuli | Conditions | Assignment samples | Full replay |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 (7I Sample A) | 784,421 | 10 | 10 | 22 | 6.583 s |
| 16 (7J Sample B) | 1,185,000 | 14 | 23 | 26 | 20.734 s |
| 32 (7K) | 4,269,739 | 14 | 25 | 26 | 19.575 s |
| 64 (7L) | 14,848,847 | 19 | 53 | 31 | 24.634 s |
| 128 (7M) | 31,446,708 | 23 | 56 | 35 | 27.292 s |

E–H selection/persistence took about 0.018–0.021 s per sample and each
selection replay about 0.013–0.014 s; those figures exclude the roughly 23.3 s
Phase 7L ancestry replay performed first. The 128 experiment generation took
26.855 s wall time (including 23.183 s parent replay); full replay took 27.292
s (including 23.921 s parent replay). Coverage planning adds four source disks
at radius one. The 64→128 increase is approximately 2.12× in artifact bytes,
2.06× in ledger rows, and 1.11× in full replay time while conditions increase
only 53→56. Earlier 32→64 payload growth was larger because the condition
ledger also grew substantially. Across the observed phases this is
**mildly-super-linear in stored artifact volume**, primarily condition and
provenance dependent; at 64→128 the computation/ledger growth is close to
linear. No performance redesign is justified by these measurements. No GPU,
Rust, WASM, multiprocessing, database, or compressed storage was added.

## Scientific boundary and decision

MaleCNS remains source evidence for body identity, relative column topology,
structural counts, and routes. Column overlap is derived anatomical exposure.
Stimulus geometry, the dimensionless sensory state, its fixed exploratory
parameters, and shared transfer coefficient remain model assumptions. DNp01
Vm and spikes are NeuroFly model outputs. No absolute visual angles,
functional receptive fields, physiological transfer efficacy, biological
population response, or behavior are established. `128/128` denotes only
software-path coverage.

**Phase 7M decision: `PREPARE_311_EXECUTION_ARCHITECTURE`.** The 128-body
composition, route verification, coverage, source accounting, A–D nested
regression, deterministic replay, and manageable measured growth pass. The
next phase should prepare an arbitrary-N/311 dry-run configuration and audit
fixed-size assumptions, artifacts, memory/runtime, coverage strategy, and all
311 source routes; it must stop before executing 311 dynamics. This does not
claim the 313-neuron circuit is simulated or biologically validated.
