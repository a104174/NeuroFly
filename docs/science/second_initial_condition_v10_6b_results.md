# V10.6B-1 — frozen second initial-condition comparison

## Protocol and execution

Executed on 2026-10-29 after protocol lock
`e8ed01f32d4651871d43c4105eb929317325e249`, whose parent is V10.6A
`04ebca9e87b2edc0d842d9a9ee4a12bc53b88443`. The two frozen files were
compared byte-for-byte with that commit before either execution. They remain
unchanged; this is local pre-specification, not independent public preregistration.

Canonical control configuration SHA-256:
`dbc0f37db7a614c1a1076041f6319999bb86e7414b17a21992a8797e43f4a392`.
The protocol document SHA-256 is
`d8a87dcc577208850b621da89689cfd301145c777fd3f1536f87d20d928d4477`.

The exact initial position is `[0, 0.11032208074629306, 0.12187743186950682]`,
heading `0` rad (+Z), instead of V10.6A's heading pi/2 (+X). Position is in arena
presentation units, not metres. The sole initial-condition change is orientation.
The control and intervention start at identical poses and zero HS/DNp15 state.
Control is `neural`; intervention is `output_disabled`, computing neural activity
normally but removing only applied neural yaw. All other settings remain frozen:
plane +0.4, 1500 intervals of 20 ms, 200 neural substeps of 0.1 ms per interval,
30 s, seed null, random policy NONE. Null is not a PRNG seed.

From `web`, reproduce into a NEW directory whose parent already exists:

```sh
node --import tsx scripts/frozen-contribution.ts /tmp/neurofly-v106b-reproduction
```

Actual independent command invocations used
`/tmp/neurofly-v106b-20261029` and `/tmp/neurofly-v106b-repeat-20261029`.
The wrapper verifies the committed protocol, exact canonical hash, existing
constructor-derived complete configuration, static pose admissibility, unchanged
non-pose controls, and OFF equality except mode BEFORE advancing. It verifies
source authority, runtime archive, manifest and eight SWCs. Output parents are
resolved through symlinks; repository paths and existing destinations are rejected.
The destination is reserved atomically before execution. No implicit experiment
runs on import, test discovery, build or application load.

No solver, locomotion, wall rule, gain, sensory encoding or replay contract was
changed. The wrapper advances the existing ContinuousNavigationEngine, exports
the parent, calls existing `generatePair` and `validatePair`, and derives motor
measurements with existing `contributionReport`. Parent reconstruction and paired
semantic replay intentionally repeat the same conditions for validation; they
are not new experimental conditions. The underlying contracts remain
CONTINUOUS_ARENA_NAVIGATION_V3 / neural_contribution_comparison_v3_1.
Both validated tracks contain 1500 outgoing intervals plus a terminal sample,
300000 neural substeps and a duration-completed parent. Interval means exclude
the terminal no-outgoing sample. Report metadata explicitly labels V10.6B.

## Observed results and reference comparison

V10.6A columns below are the rounded published values from
`closed_loop_contribution_v10_6a.md`; no new full V10.6A experiment was run.
V10.6B columns are derived from the actual validated report.

| Quantity | A control | A ablation | B control | B ablation |
|---|---:|---:|---:|---:|
| Mean absolute computed neural yaw, rad/s | 0.2226262705 | 0.2143029376 | 0.2545868141 | 0.2310862615 |
| Mean absolute applied neural yaw, rad/s | 0.2226262705 | 0.0000000000 | 0.2545868141 | 0.0000000000 |
| Mean absolute engineered wall yaw, rad/s | 0.3837248206 | 0.2960548049 | 0.5152491893 | 0.3866670702 |
| Travelled distance, presentation units | 4.3911168540 | 5.1750434006 | 4.1559757845 | 5.0088035903 |
| Wall-contact episodes | 3.0000000000 | 2.0000000000 | 5.0000000000 | 3.0000000000 |
| Final heading, rad | 2.0862673689 | 1.2270289533 | 2.4027906969 | 2.3062576164 |

| Paired metric | V10.6A reference | V10.6B |
|---|---:|---:|
| Final position separation, presentation units | 0.8355999781 | 0.6424853668 |
| Signed wrapped final heading difference (ON minus OFF), rad | 0.8592384155 | 0.0965330804 |

B maximum separation is 0.7541868309 units at
22.38 s. Maximum absolute wrapped heading difference is pi,
with the existing between-boundary interpolation time
10.486453179557 s. Control minus intervention travelled
distance is -0.8528278058 units.

The first interval is a genuine immediate null: computed, applied and wall yaw
are zero in both conditions, and the accepted first poses coincide. The complete
30-second comparison has a nonzero total effect. Ablated applied neural yaw
remains exactly zero while its computed neural yaw remains nonzero later.
No condition was changed, shortened or extended after results were observed.

## Artifacts, identity and independent repeat

Pair artifact ID (ON/OFF run IDs append `:ON` / `:OFF`):
`4e5a943669531fdc7f21e4d0ec166d21063f4f4bdefcf8d0e2860d7ca878c1b0`.
Complete paired trajectories, parent, source identities and interval telemetry
are external in each directory's `pair.json`; `report.json` contains motor-boundary
intervals, summaries and protocol provenance. `provenance.json` records preflight
status; acceptance is indicated ONLY by successful `checksums.json`. Failures
instead retain `failure.json` and are not accepted scientific records.

Two fresh OS processes repeated the entire protocol. The COMPLETE bytes of all
four files matched, with no field exclusions. Verification record:
`/tmp/neurofly-v106b-repeat-verification-20261029.json`.

| File (same hash in both directories) | SHA-256 |
|---|---|
| `pair.json` | `4b5d0b287e4763ff6a204dbb4bd8760c0dc0bf3abc1d464e5d105f6d0dadd6e3` |
| `report.json` | `decfa869afcb4a784cc3758336a9b45f58549d0f2dbcd21d4dc37312bc26cf0b` |
| `provenance.json` | `bc6e9d82685678f296c5c06264a1df358144d9a3f82e0925c4283221d5f77de7` |
| `checksums.json` | `faf31b8ac88a2a364dde81b10d99d0ddf26ad3f51ecb42e4e038b941dbe75d23` |

Execution used Node v24.11.1 on linux/x64.
The tracked runtime revision was the protocol commit above; the execution wrapper
was not yet committed, so its exact source SHA-256 is independently recorded:
`6f087fbf5a17193cead9b0524ea8db20a73ed8d5b6d437d7c71b8274760eb8e2`.
The following implementation commit versions those wrapper bytes. Subsequent
reproduction records its own execution commit; this provenance field will differ
from these original files, even when scientific outputs agree. Preserve and
inspect that difference rather than claiming cross-revision byte identity.
Temporary evidence directories are not permanent archival storage. No generated
trajectory is committed.

## Interpretation, integrity and limits

Applying neural yaw has a nonzero total closed-loop causal effect inside this
model at the second, pre-specified pose. Final separation and heading difference
are smaller than in V10.6A; other summaries also change. After divergence,
sensory observations, computed neural activity and engineered wall responses may
differ even though their governing rules are identical. This does not isolate
the direct neural contribution at every subsequent instant. Two deterministic
initial conditions provide no statistical generalisation or biological causal
validation, measured firing, fluorescence, learning or complete living-fly emulation.
MaleCNS structural evidence remains distinct from modelling assumptions.

The runtime v3 archive remains SHA-256
`c5edf9edb0b1f08a0eb3e36808dd6ec25771be1bc575ce07e9cc3063aa6586cf`;
morphology manifest remains
`c538f94a6a3ea02390bfcb09ee77226fe6f0418455c0794cdfedd64593070697`.
All eight SWCs matched their manifest before both executions. No scientific
source geometry, body identity, normalization or historical result was modified.

## Automated evidence and next question

Focused input/orchestration tests cover valid complete frozen configuration,
independent parsing, changed/missing/malformed inputs, invalid pose, non-pose
parameter changes, unsupported runtime, non-mode intervention changes, unsafe
and existing output destinations, symlinks and separate failure records. Tests
never execute this second-pose experiment. Existing contribution-report tests
retain null, metric, incomplete/missing telemetry and motor-boundary checks.

Validation executed:
- `node --import tsx --test tests/frozen-contribution.test.ts`: 6/6 passed,
  zero failures/skips, with no second-pose advancement.
- `npm test` initially failed: 388 passed, 5 failures (393 discovered), zero skips;
  existing Python-backed test files could not find `python` on PATH. No source
  change was made to conceal this environment failure.
- `PATH="/home/l1tren/projetos/NeuroFly/.venv/bin:$PATH" npm test`: 418/418 passed,
  zero failures/skips, using the repository's existing Python environment.
- `npm run lint`, `npm run typecheck`, `npm run build`: passed.
- `git diff --check`: passed. The build-generated next-env.d.ts route-import
  change was inspected and only that generated difference was reverted.

Both real experiment invocations passed the existing complete semantic pair
validation. No Python source or cross-language contract changed; no separate
Python suite was run. Browser visual acceptance remains deferred and FPS regression comparison
is not verifiable from these scientific runs.

Next smallest scientific step: inspect the existing matched interval records to
locate the onset of closed-loop divergence, preserving this frozen experiment and
separating immediate motor manipulation from later feedback. Do not infer
biological validation or select additional initial conditions for stronger effects.
