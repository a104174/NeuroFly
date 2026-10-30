# V10.6C-1R — reproduced temporal divergence analysis

## Evidence and fresh reproduction

The original temporary A/B files disappeared. This phase executed exactly one
fresh paired reproduction of each published condition, not new conditions and
not recovery of the lost originals. Existing semantic validation includes
reconstruction of these same conditions. No scientific runtime source changed.

Execution revision: `31b8085f0a7e27137d665360246d9823050483d6`, Node 24.11.1.
V10.6A publication: `04ebca9e87b2edc0d842d9a9ee4a12bc53b88443`;
its historical execution Git revision remains unknown.
V10.6B protocol: `e8ed01f32d4651871d43c4105eb929317325e249`;
results publication: `31b8085f0a7e27137d665360246d9823050483d6`.
The historical protocol lock was local, not independent public preregistration.

Before adding the analyzer, from `web`:

```sh
mkdir /tmp/neurofly-V10.6A_REPRODUCTION-20261030
node --import tsx scripts/causal-contribution.ts /tmp/neurofly-V10.6A_REPRODUCTION-20261030 1500
node --import tsx scripts/frozen-contribution.ts /tmp/neurofly-V10.6B_REPRODUCTION-20261030
```

Both commands passed existing `validatePair` semantic replay. B verified its
frozen canonical configuration SHA-256 before advancing:
`dbc0f37db7a614c1a1076041f6319999bb86e7414b17a21992a8797e43f4a392`.
Initial position is `[0,0.11032208074629306,0.12187743186950682]`;
heading is pi/2 for A and zero for B. Both pairs use zero neural initial states,
plane +0.4, 1500 body intervals of 20 ms, 200 neural substeps of 0.1 ms,
30 s, seed null and random policy NONE. Within each pair only application of
computed neural yaw differs: `neural` versus `output_disabled`.

Fresh output hashes (raw file bytes, not canonical configuration hashes):

- `/tmp/neurofly-V10.6A_REPRODUCTION-20261030/pair.json`: 6156685 bytes, SHA-256 `81f15bc71ef6acf968c3da46bc1ee931bf2569c841b25d9f5fc2e2f3a5131a8c`.
- `/tmp/neurofly-V10.6A_REPRODUCTION-20261030/report.json`: 1234316 bytes, SHA-256 `24dabe13611238945155a6268bccf597b8871bbf498e39870ed2de53083f7997`.
- `/tmp/neurofly-V10.6B_REPRODUCTION-20261030/pair.json`: 6106125 bytes, SHA-256 `4b5d0b287e4763ff6a204dbb4bd8760c0dc0bf3abc1d464e5d105f6d0dadd6e3`.
- `/tmp/neurofly-V10.6B_REPRODUCTION-20261030/report.json`: 845002 bytes, SHA-256 `23d370c3c808075d95c8267bc8ad5d834f5b98c2ec0303223d5682007e77b3e4`.

The new pair hashes equal the historical recorded hashes; this does not recover
the original files or establish their custody. B report bytes differ because
execution-revision provenance is recorded honestly. No metadata was rewritten.
The reproduction labels and comparison checks are external in
`/tmp/neurofly-reproduction-validation-20261030.json`. All full trajectories remain
outside Git and are temporary evidence, not a durable archive.

## Read-only analytical method

```sh
cd web
node --import tsx scripts/temporal-divergence.ts /path/to/A/pair.json /path/to/B/pair.json
```

The CLI reads explicit local paths and prints deterministic JSON to stdout only.
It cannot overwrite inputs or write results. The reusable module has only a
TypeScript type import from runtime code; it does not load a solver or call
`validatePair`, whose semantic reconstruction executes simulation.

Input schema is `neural_contribution_comparison_v3_1`. Checks include canonical
SHA identities of pair and parent, matched configuration/provenance, ON/OFF
conditions, finite values, complete aligned interval count, terminal record,
initial/final pose consistency, observation timing and recorded yaw/heading
algebra. This is not an independent replay or neural-equation validation.
Malformed or contradictory evidence fails; absent sensory observations are
reported UNAVAILABLE, never replaced by zeros.

Record n at n*0.02 s is the accepted START pose. Observation compares n-1 to n;
HS/DNp15 snapshots precede current substeps. Computed yaw is reconstructed from
recorded increment as clip(2.5*increment/0.02, -0.5, +0.5) rad/s.
Applied yaw and engineering wall yaw belong to interval n. The accepted resulting
pose is n+1. Translation uses the previous heading; heading integrates total yaw.
The terminal record has no outgoing interval and no computed increment.

Report exact inequalities AND differences exceeding absolute 1e-8 in native
field units. This adopts the existing parity tolerance as a reporting threshold,
not biological significance or a 30-second accuracy guarantee. Position uses
Euclidean X/Z distance; heading uses atan2(sin(delta),cos(delta)), ON minus OFF.
Ties for maximum separation retain the earliest sampled boundary. Contact spans
are half-open intervals from contact-state changes; null end means still active
at the recorded horizon. Checkpoints are boundaries at 0,5,... seconds and final.
The pure module also returns every sampled separation and heading difference.

## Newly measured results against historical findings

| First divergence | A index / seconds | B index / seconds |
|---|---:|---:|
| applied | 1 / 0.02 | 55 / 1.10 |
| heading | 2 / 0.04 | 56 / 1.12 |
| position | 3 / 0.06 | 57 / 1.14 |
| sensory | 2 / 0.04 | 56 / 1.12 |
| computed | 2 / 0.04 | 56 / 1.12 |
| neuralState | 3 / 0.06 | 57 / 1.14 |
| wall | 247 / 4.94 | 56 / 1.12 |
| contact | 269 / 5.38 | 122 / 2.44 |

All these onsets match the historical V10.6C audit; exact and above-tolerance
onsets coincide. At the first unequal applied yaw, computed yaw is STILL equal:
A -0.03434262167284544 rad/s; B -0.026659276426800018 rad/s in both branches.
Sensory and computed output can diverge in the same record. Stored pre-substep
neural states appear different one record later. Heading precedes position by
one accepted boundary, as required by the integration ordering.

| Aggregate | A control | A ablation | B control | B ablation |
|---|---:|---:|---:|---:|
| Computed yaw mean abs, rad/s | 0.2226262705 | 0.2143029376 | 0.2545868141 | 0.2310862615 |
| Applied yaw mean abs, rad/s | 0.2226262705 | 0.0000000000 | 0.2545868141 | 0.0000000000 |
| Wall yaw mean abs, rad/s | 0.3837248206 | 0.2960548049 | 0.5152491893 | 0.3866670702 |
| Distance, presentation units | 4.3911168540 | 5.1750434006 | 4.1559757845 | 5.0088035903 |
| Contact episodes | 3.0000000000 | 2.0000000000 | 5.0000000000 | 3.0000000000 |

Every aggregate above matches the published ten-decimal reference within 1e-8.
A final/max separation: 0.8355999781 at 30 s;
final wrapped heading difference 0.8592384155 rad.
B maximum: 0.7541868309 at 22.38 s;
final: 0.6424853668 at 30 s;
final wrapped heading difference 0.0965330804 rad.
These also match the published references. No parameter was tuned to match them.

## Interpretation and limitations

The direct intervention removes applied neural yaw. Immediate integration changes
accepted heading and then position. Later sensory, computed neural and wall
response differences are closed-loop consequences under unchanged equations.
Temporal ordering alone establishes no independent mediation fractions.
Trajectories separate and partially approach again; B final separation is smaller
than its maximum. Smaller spatial separation does not imply neural reconvergence.
Wall yaw is engineering, not MaleCNS neural activity. MaleCNS structural evidence
remains distinct from model assumptions. Two deterministic initial poses provide
no statistical generalization, living-fly causal validation, learning or consciousness.

Unit tests use explicit synthetic software fixtures, never scientific results.
Validation: focused analyzer tests 8/8; full frontend suite 426/426, zero failures/skips
(using existing .venv/bin on PATH); ESLint, typecheck, production build and diff
checks passed. Runtime archive, morphology manifest and eight SWCs passed hashes.
The generated next-env.d.ts route-import difference was inspected and reverted. No storage or authentication
integration, UI, rendering or camera change belongs to this phase.
Next: a read-only Neural Explorer frontend/3D audit of actual rendering, morphology,
camera controls, picking, activity presentation, responsiveness and browser performance.
