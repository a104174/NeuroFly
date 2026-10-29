# V10.6A — matched closed-loop neural motor contribution protocol

Question: what total behavioural effect does the existing applied neural yaw
contribution have in this computational arena? Hypothesis: disabling application
can change heading and, through pose-dependent observation, subsequent movement.
A nonzero effect is not required for a valid experiment.

## Feasibility and existing contracts

An equivalent comparison already exists: `neural_contribution_comparison_v3_1`
(`generatePair` / `validatePair`). This phase adds a bounded reproducible command
and explicit motor-boundary report; it does not introduce another comparison
configuration, solver or intervention. `NEURAL_TO_HEADING_ENABLED` selects the
existing `neural` versus `output_disabled` modes. The latter still computes all
HS/DNp15 substeps before zeroing only the applied yaw. Finite v3 navigation is
the v10.5b live baseline prefix; engineering exploration is not tested here.

`InteractiveNeuralEngine.observation` derives signed landmark-bearing shifts
from the previous and current accepted poses (first observation is null).
`calculateBoundary` uses this observation for 200 neural substeps of 0.1 ms.
It returns interval-start HS/DNp15 states and the integrated model orientation
increment. The unchanged motor projection is clip(2.5 * increment / 0.02,
−0.5,+0.5) rad/s. `output_disabled` sets its application to zero AFTER this
calculation. `ContinuousNavigationEngine.calculateBoundary` adds the unchanged
geometric boundary yaw (up to ±1.2 rad/s), without a further summed clamp.
`advance` integrates heading with this total over 20 ms and translates with the
old heading, engineering speed 0.18 units/s and existing collision constraints.
The accepted pose feeds the next observation. Structural contacts identify the
MaleCNS motif; the solver uses the frozen equal-source modelling assumptions,
not contact counts as dynamic gains.

## Protocol and provenance

Run from `web`:
`node --import tsx scripts/causal-contribution.ts EXISTING_EXTERNAL_DIRECTORY 1500`
The command rejects output directories within the repository and refuses to
overwrite evidence. `pair.json` is the existing complete v3.1 artifact, including
its validated parent, matched configuration, source identities/hashes, events,
full two-track trajectories and final states. `report.json` adds explicit computed,
applied, boundary and total yaw with interval-start/accepted tick semantics;
stdout is a compact comparison. Computed yaw is derived from the recorded
orientation increment using the verified existing gain and bound. It is not a
fabricated upstream neural state. SHA identities use existing navigation hashing.
`validatePair` reconstructs both tracks before the command writes them.

Both conditions use default pose, zero initial HS/DNp15, plane +0.4, identical
arena/model configuration and 1500 steps (30 simulated seconds). Seed is null;
random policy is NONE, so there is no seed selection or behavioural noise. Run
IDs are artifact ID plus ON/OFF and do not influence dynamics. The only changed
runtime configuration field is mode; the existing condition flag records it.

## Observed deterministic result

Evidence: `/tmp/neurofly-v106a-20261029/{pair,report}.json`; an independent command
repeat in `/tmp/neurofly-v106a-repeat-20261029/` produced identical file bytes.
Pair ID: `fda22e1847bd6e40429288a8dbc04a0e6672c1f099621741be2a5be99594d758`.
Report hash: `0249a02315b47a8f915c740481f01e2b24311d4250ccf328d35f1b7fca8660f7`.

| Quantity | Control | Applied-yaw ablation |
|---|---:|---:|
| Mean absolute computed neural yaw, rad/s | 0.2226262705 | 0.2143029376 |
| Mean absolute applied neural yaw, rad/s | 0.2226262705 | 0 |
| Mean absolute boundary yaw, rad/s | 0.3837248206 | 0.2960548049 |
| Travelled distance, presentation units | 4.3911168540 | 5.1750434006 |
| Contact episodes (interval-start event definition) | 3 | 2 |
| Final heading, rad | 2.0862673689 | 1.2270289533 |

Final separation is 0.8355999781 presentation units; wrapped final heading
difference is 0.8592384155 rad. Maximum wrapped heading difference reaches pi
under the existing between-boundary interpolation metric. First interval neural
yaw is zero in both conditions: the one-step protocol is a genuine null result.

These are model-internal total closed-loop effects. After divergence, sensory
inputs, calculated neural activity and boundary contributions differ because
poses differ. This does not mean the neural equations or wall rules changed.
No biological causal validation, measured firing/fluorescence, learning or
whole-fly emulation is established. Historical scientific artifacts, runtime v3
and public API/replay schemas remain unchanged. Full live-session recording is
not implied by this complete finite experiment.

Tests verify baseline equality, immediate matched neural computation, applied
ablation, determinism, existing semantic replay, invalid horizons, missing and
contradictory telemetry, and the one-interval null outcome. Next: a separately
specified bounded alternate initial-pose protocol, without gain tuning or a
claim of statistical generalisation.

Validation: 412/412 frontend tests, no skips, including the two protocol tests;
ESLint, typecheck, production build and diff checks passed. No Python source or
scientific runtime module was changed; existing frontend Python-parity checks
ran as part of the canonical suite. Legacy OFF frame `model_mode` labels remain
unchanged for compatibility; the explicit condition and real neural telemetry
establish that computation continues while only motor application is disabled.
