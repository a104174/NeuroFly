# Phase 7N — all-311 sensory population readiness (dry run)

Phase 7N validates the source-defined target population and prepares a
replayable execution manifest for a future 311-body experiment. It deliberately
stops before sensory-state integration, transfer calculation, or DNp01
simulation. Its results are architecture/readiness evidence, not visual or
physiological validation.

## Repository and source identity

The phase began on clean `main` at `2d11793d26dd78a99f9b6e07d3f94b4f015c81c6`
(Phase 7M, matching `origin/main`). The canonical 128-body Phase 7M experiment
was replayed before changes: artifact
`3d0ec7e8ddf5baf00449f6452d538d995978b571da5ea9efc632b91228d5dcc6`,
31,446,708 bytes including manifest, 23 stimuli, 56 conditions, and 85,760
source-contribution ledger entries. Replay succeeded. No Phase 7M artifact was
modified.

The population identity is taken directly from the pinned MaleCNS
`looming_giant_fiber_v1` CircuitContract, not reconstructed from samples A–H.
The paired `body_column_input_v1` contract is checked body-by-body for ID,
type, side, records, assigned-site totals, and source coordinate validity.

| Source | Identity/version | Pinned identity |
| --- | --- | --- |
| CircuitContract | `male-cns:v1.0`, `looming_giant_fiber_v1` v1 | `neurons.jsonl` SHA-256 `00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e`; `connections.jsonl` SHA-256 `f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a` |
| Body-column contract | `body_column_input_v1`, same dataset/candidate | summaries SHA-256 `ed3b56a403c02256048fffdfd1d165c667360265e95e75f307ae8eb210c10e2b`; input records SHA-256 `4d235b382e4cb317ebb77f9248a58cb1332e942b8a1a0eafb5c5526f2bed598e`; contract identity `874ebe99439d3096409371481cbe4fe48c5cf3011e039c93128d2719615f6b21` |
| Column classification workbook | official `optic-column-type-assignments-v1.0.xlsx` from `flyconnectome/2025malecns` | commit `67767d2233657983993ff6c2be48e836a935863c`; SHA-256 `d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3` |

## Fixed-size assumption audit

Historical size limits are retained where they protect already-published
artifact meanings. They are not silently widened.

| Component | Current fixed assumption | Classification | Phase 7N action |
| --- | --- | --- | --- |
| `relative_column_assignment.py` and `relative_column_sensory_dynamics.py` | Four Phase 7A sentinel identities and four-body result layout | A — historical compatibility | Kept unchanged; 7D/7E artifacts remain four-body artifacts. |
| `relative_column_dnp01_transfer.py` | Four exact 7F routes and four-body source artifact validator | A — historical compatibility | Kept unchanged; its numerical `route_population_drive` primitive accepts an explicit route set of arbitrary length and is tested with 311 sources. |
| `bounded_sensory_coverage.py` | Canonical 16-body Phase 7I wrapper and artifact | A — historical compatibility | Kept unchanged. Phase 7N calls only its source-column/radius-bounded set-cover primitive. |
| `bounded_sensory_population.py` | 16-body selection and historical conditions; old named masks `all16`, `all32`, `all64`, `all128`; four sentinel comparisons | A — versioned historical wrapper | Kept unchanged in its 16-body artifact semantics. Its source assignment/state/route/transfer primitives iterate explicit body collections. The route builder now checks exactly one route per supplied identity instead of requiring 16, and generic `all_population` masking uses the supplied collection. |
| `bounded_sensory_scale64.py` / `bounded_sensory_scale128.py` | Four-/eight-parent sample unions, their named sample masks, condition sets, and schemas | A — historical compatibility | Kept unchanged. The all-311 plan does not inherit those parent chains. |
| Phase 7N readiness module | Exact target is 311, with exact source type/side/route counts | B — target-population contract | This is an intentional target identity validator, not an execution-size dispatch. It has no branches for 16/32/64/128. |
| Future full experiment artifact/orchestrator | Existing complete experiment wrappers encode historical cohorts and condition manifests | C — must use a new explicit population artifact/orchestrator before 311 results are produced | No old schema is broadened. The existing generic assignment/state math, transfer summation, and DNp01 readout can be composed under a new versioned runner in Phase 7O. Phase 7N defines and validates its inputs, but does not execute them. |

No blocking fixed-size assumption was found in the source identity, route,
coverage-planning, transfer-summation, or DNp01 readout primitives. The fixed
historical replay wrappers remain valuable regression gates and are not a
reason to make the all-311 population depend on A–H.

## Full target population and body-column completeness

The dry-run population contains exactly 311 unique sensory IDs:

| Type / side | Bodies |
| --- | ---: |
| LC4 L | 71 |
| LC4 R | 55 |
| LPLC2 L | 94 |
| LPLC2 R | 91 |
| **LC4 total** | **126** |
| **LPLC2 total** | **185** |
| **Total** | **311** |

Every CircuitContract sensory body has a matching body-column summary and at
least one source record. All 25,438 body/column records have valid relative
hex coordinates on their source side. Across the population there are 574,745
assigned input sites and 2,790 unassigned sites. Per-body record count ranges
from 36 to 146 (median 78); unique source columns range from 36 to 99 (median
62); assigned-site fraction ranges from 0.9354 to 1.0 (median 0.9976).
These are source coverage descriptors, not physiological weights.

The official workbook has no classification for left source columns `(17,34)`
and `(19,35)`. They remain valid source coordinates but are not assigned
invented edge/DRA classes. Nine sensory bodies use one or more such coordinates:
15018, 17608, 18396, 27355, 31105, 32237, 40811, 514956, and 518439. There are
no corresponding right-side unclassified coordinates. This does not prevent
relative-column coverage.

## Route completeness

Every one of the 311 sensory bodies resolves to exactly one direct chemical
route in the source CircuitContract, with a valid DNp01 target. Targets are
counted from the actual edges, not inferred from side:

| DNp01 target | Source bodies |
| --- | ---: |
| 10001 R | 146 |
| 10010 L | 165 |

All source and target side identities agree; there are no missing, duplicate,
unsupported, or cross-side routes. Each source's structural edge count is
retained in the population record as `SOURCE_STRUCTURAL_COUNT_METADATA_ONLY`.
It is not used as exposure, sensory gain, transfer coefficient, or numerical
drive.

## Anatomy-only coverage planning

The starting stimulus battery is the exact persisted Phase 7M 23-stimulus
plan `2e0750448f72640b0231c3efe5638235ceddada459821cb31ccc9ce7795d922d`.
Its normalized `(stimulus config, stimulus hash)` list is pinned by SHA-256
`93cf3de37b21906535fbb61c2e6012f2da6909637bf026fe594a729e8b967fb4`.
Applying binary `BODY_STIMULUS_COVERED` to all source column distributions
covered 299/311. Initial coverage was:

| Type / side | Covered / total | Uncovered |
| --- | ---: | ---: |
| LC4 L | 65 / 71 | 6 |
| LC4 R | 53 / 55 | 2 |
| LPLC2 L | 91 / 94 | 3 |
| LPLC2 R | 90 / 91 | 1 |

Uncovered IDs were `12384, 18189, 18396, 19550, 22677, 23226, 23919, 32597,
33137, 518983, 524366, 533129`. The existing side-specific exact set-cover
planner was run on those bodies only. Candidate centres were actual source
columns, candidates were integer-radius disks 1–4, and the objective was
minimum disk count, then minimum total radius, then deterministic
radius/coordinate lexicographic order. It evaluates binary column overlap;
it does not read structural site weights or any model output. Search examined
1,376 left and 480 right centre/radius disks before deduplicating non-empty
coverage masks (22 left and 6 right masks).

Four added stimuli yield 311/311 anatomical coverage:

| Stimulus | Side | Centre | Radius | Newly covered bodies |
| --- | --- | ---: | ---: | --- |
| `coverage311_l_07_07_r1` | L | (7,7) | 1 | 12384, 33137, 518983 |
| `coverage311_l_21_32_r4` | L | (21,32) | 4 | 18396, 23226, 23919, 32597, 524366 |
| `coverage311_l_22_14_r1` | L | (22,14) | 1 | 533129 |
| `coverage311_r_09_09_r1` | R | (9,9) | 1 | 18189, 19550, 22677 |

The radius-four disk is the largest selected, within the authorized bound. No
further geometry was introduced. The final 27-stimulus battery is a
synthetic `RELATIVE_COLUMN_SPACE` coverage plan, not visual-field/RF or
biological-stimulation coverage.

## Artifacts and direct provenance

The three content-addressed artifacts are stored under ignored derived-data
roots:

| Artifact | Schema | ID | Config SHA-256 | Result SHA-256 | Bytes incl. manifest |
| --- | --- | --- | --- | --- | ---: |
| Population | `full_sensory_population_plan_artifact_v1` | `0db2b29f168039e23858db9831e345cc25fdec8c06775e2f23a7d8d681544356` | `55206aa053c5cdf7b262132156abd175ddc3ec14792d98228053b3122853d307` | `eebe33ddf251a59416225f54dcb14928fe2b0b0482ddf35b433ab5e6683b2be5` | 181,328 |
| Coverage | `full_sensory_population_coverage_artifact_v1` | `0331ff3d309892ac5284e0da3898683df7b5fb8fd06055090b6100dcea4a6e56` | `f3e47dd552ee12f01e7b3ce637f055d0f51b1393b1770235ce686725ad40c3e3` | `082aedc328dcb442625c25edcbca924ee3695f0f6b44fa551867fb781230d52b` | 131,824 |
| Execution dry run | `sensory_population_execution_dry_run_artifact_v1` | `a7d828993674634875b8b8862d40083690e77bb8aa748ad7079135cc8e10725f` | `7e2c3d1168a631873e2206796c3ad53ce5cedfd7712676d799521e04451ee7c8` | `0ac4d79f1885c919ae86112db11229ab3dcc54b3c2f7a853158478190e5e6f22` | 79,291 |

The full-population provenance chain is directly:

`CircuitContract + body_column_input_v1 + relative column grid`
`→ complete population plan → anatomy-only coverage plan → dry-run config`.

The population plan has no A–H sample parent. The 23 inherited stimulus
configs are embedded and hash-pinned; the Phase 7M artifact ID is retained as
their historical source reference. Coverage replay revalidates the embedded
battery and deterministic planner without replaying the A–H chain. The exact
Phase 7E/7F/DNp01 settings are embedded in the execution config and pinned to
the Phase 7M model-config hash for comparison only, not as population
provenance.

CLI commands (local pinned data only):

```bash
python -m neurofly.sensory_population_readiness_cli prepare
python -m neurofly.sensory_population_readiness_cli inspect population <artifact-dir>
python -m neurofly.sensory_population_readiness_cli replay <population-dir> <coverage-dir> <execution-dir>
```

The dry-run manifest specifies 311 source bodies, two DNp01 targets, 27
stimuli, 39 assignment samples, 12,129 body/exposure assignment rows, 336
state boundaries per body (104,496 across the population if later executed),
35 planned conditions, 421 model intervals, and 130,931 expected
per-source/per-interval contribution records. These are dimensions only; no
state values, transfer ledger, DNp01 run, or dynamic result artifact exists.
The 311 dynamic conditions are a compact proposal: 27 single-stimulus
reference checks plus eight bilateral controls (`reference`, `k=0`, no
sources, LC4-only, LPLC2-only, left-only, right-only, and `k=2`). No
population-size normalization is configured.

## Model config and scientific boundary

The future config references unchanged Phase 7E settings:
`relative_column_exploratory_sensory_state_v1`, `tau_sens_ms=1`, `gain=1`,
`x0=0`, and `column_overlap_fraction`; it references the shared Phase 7F
`k_transfer=1.0 mV_eq/state` with no normalization and the existing
deterministic DNp01 LIF configuration. Configuration identity was compared
to the canonical Phase 7M artifact. None was executed for 311 bodies.

MaleCNS body IDs, side, column topology, input-site counts, and route targets
are source evidence. Column overlap and coverage are derived anatomy.
Relative-column stimulus geometry and the future sensory/transfer parameters
are model assumptions. `structural_edge_count` is metadata only. The planned
sensory state and DNp01 Vm/spikes would be exploratory/model outputs; the
functional RF, absolute visual angles, physiological gain, and biological
response remain unknown.

## Scaling and resource estimates

Committed observations include different numbers of stimuli/conditions, so
the replay wall times are workflow measurements, not controlled benchmarks.

| Sensory bodies | Experiment bytes | Stimuli | Conditions | Full replay |
| ---: | ---: | ---: | ---: | ---: |
| 16 (7I A) | 784,421 | 10 | 10 | 6.583 s |
| 16 (7J B) | 1,185,000 | 14 | 23 | 20.734 s |
| 32 (7K) | 4,269,739 | 14 | 25 | 19.575 s |
| 64 (7L) | 14,848,847 | 19 | 53 | 24.634 s |
| 128 (7M) | 31,446,708 | 23 | 56 | 27.292 s |
| 311 (7N plan, not experiment) | 181,328 population + 131,824 coverage + 79,291 manifest | 27 | 35 planned | 2.232 s dry-run replay |

The 7N prepare completed in 2.19 s in the measured run (source load/validation
0.77 s, population plan build/persist 0.02 s, coverage plan build/persist
1.38 s, execution manifest build/persist 0.02 s). A separate replay
recomputed the population and coverage, validated the embedded model settings,
and matched all three artifact IDs in 2.14 s (coverage planning/replay 1.36
s). `/usr/bin/time -v` measured 78,900 KiB maximum RSS for source loading,
planning and dry-run artifact generation; that process did not construct
dynamic trajectories.

For a future 311 execution with the stated 35-condition design, 130,931
contribution records are 1.53× the 128 experiment's 85,760 recorded
contribution entries. Scaling the 128 artifact by that row ratio gives about
48 MB before differences in provenance/condition overhead. Use a rough
**LOW 40 MB / CENTRAL 50 MB / HIGH 90 MB** serialized-result estimate: low
assumes compact per-source rows and limited repeated metadata; central follows
the observed 128 bytes-per-ledger-entry plus 311-body metadata; high allows
roughly 1.8× central for verbose repeated condition/target traces. These are
planning ranges, not measurements.

With the 128 workflow's non-parent computation around 3–4 s and 1.53× as many
ledger rows, arithmetic alone suggests a few seconds. Allow **8–20 s for
generation and 8–25 s for full replay** under the direct 311 provenance chain;
allow up to roughly a minute if serialization or repeated validation dominates.
These ranges exclude any historical A–H replay. The full Phase 7N pytest
suite took 211.19 s (386 passed, one repository test deselected, with two
dependency deprecation warnings); a future dynamic artifact/replay test may
add tens of seconds depending on serialization.

The 7N planning process fits comfortably in the current Python process at
about 77 MiB RSS. A later dynamic run will materialize a much larger Python
object graph than its JSON file size suggests; a rough peak range of 0.5–1.0
GiB is plausible for the central artifact estimate, but has not been directly
measured and should be measured during Phase 7O. Likely scaling pressure is
the detailed per-source contribution ledger and JSON serialization, then
condition duplication/replay, not scalar sensory-state or two-neuron LIF
arithmetic. No storage/runtime optimization was introduced.

**Readiness decision: `READY_FOR_311_BOUNDED_EXECUTION`.** Population
identity, source hashes, body-column topology, all routes, 311/311
anatomical coverage, dry-run configuration and direct provenance are
deterministic. Historical artifact wrappers remain compatible. Phase 7O may
perform one explicitly bounded 311-body exploratory execution using the
listed unchanged model assumptions, with runtime/memory measured; it must not
claim physiological validation or a completed biologically calibrated
313-neuron circuit.
