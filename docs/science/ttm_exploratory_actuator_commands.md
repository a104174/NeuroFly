# Phase 11B — side-preserving exploratory TTM actuator commands

## Capability and source gate

`ttm_exploratory_actuator_command_v1` implements functional addressing:
persisted Phase 10B activation → two virtual TTM-associated actuator channels.
There is no new physiological transformation or equation of motion.

Started clean on `main` at `934d0d5542a7828b135cf8d471dd682385583d46`, equal
to local `origin/main`. Phase 11A, 10C and 10B were committed. Required offline
replays passed for 10B, 10C and explicit 8K target contract
`5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0`.
Activation replay recursively validates electrical, proxy and motor-input
ancestry. No existing actuator runtime was found; no parallel framework added.

Direct source is the canonical
`static_normalized_muscle_activation_result_v1` artifact
`4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb`.
Only its full `activation_proxy` arrays are runtime drivers. Electrical state,
tokens, observation peaks and frontend state are not read as actuator input.
Source replay is validation; the adapter itself never reruns electrical or
activation dynamics. No historical artifact or schema changed.

## Exact rule and routing

For every stored boundary, `actuator_command[n] = activation_proxy[n]` exactly.
Units stay dimensionless `[0,1]`; no gain, threshold, lag, interpolation, filter,
integration, new clipping or numerical free parameter exists. Ceiling 1 retains
the source's model-normalization meaning, not maximal physiological force.

| Source body / neural side | Virtual actuator / side | Routing ID |
| --- | --- | --- |
| 800146 / R | RIGHT_TTM_ACTUATOR / R | `6cf14bc3b7dfefa77cdca953459499c6c78d0a1a0329dfd46a2178f027022ce5` |
| 804642 / L | LEFT_TTM_ACTUATOR / L | `a77193428fc74b9de95306b195a6615f751a38f4f6cfee143133af086356c58f` |

Action kind: `TTM_ASSOCIATED_FEMUR_EXTENSION_DRIVE`.
Classification: `EXPLORATORY_FUNCTIONAL_ACTUATOR_MAPPING`, `MODEL_ASSUMPTION`.
Config contains source schema/reference, these two fixed routing records,
passthrough/time/unit semantics and exclusions only. Exact source identities,
not arbitrary runtime side strings, select the channels. Cross-routing,
merged channels, missing/extra routes and semantic drift are rejected.

The functional association is supported by the bounded primary-source audit
in [Phase 11A](first_ttm_contraction_force_actuator_readiness.md), including
Trimarchi & Schneiderman (1993), DOI 10.1242/jeb.177.1.149. Its TTM/femur-extension
scope is not a tibial-extension axis, anatomical attachment map or complete jump.
No additional literature research or biological parameter transfer in 11B.
The selection of a virtual action consumer remains an explicit model assumption.

## Results and provenance

Result schema: `ttm_exploratory_actuator_command_result_v1`.
Shared `boundary_indices`/`time_ms` preserve the source grid: 0.1 ms, 80
intervals, 81 boundaries. Each output retains fixture, exact activation
trajectory ID/hash, source body/side, proxy domain/mapping ancestry, routing
ID, actuator identity/side, action kind and config identity. The source
provenance chain is extended by `EXPLORATORY_TTM_ACTUATOR_COMMAND`.

Canonical ordering is the source's six-fixture order and ascending source-body
order: right 800146 then left 804642. Six fixtures × two channels × 81 boundaries
= 12 trajectories and 972 commands. Inactive channels are retained explicitly.

| Fixture | Right peak | Left peak | Active peak boundary | Active final command |
| --- | --- | --- | --- | --- |
| ZERO_EVENT_CONTROL | 0 | 0 | none; zero-summary tie uses step 0 | 0 |
| RIGHT_SINGLE_EVENT | 0.2 | 0 | 10 / 1 ms | 0.00018237639311090254 |
| LEFT_SINGLE_EVENT | 0 | 0.2 | 10 / 1 ms | 0.00018237639311090254 |
| BILATERAL_SIMULTANEOUS_EVENT | 0.2 | 0.2 | 10 / 1 ms, separately | 0.00018237639311090254 per channel |
| RIGHT_REPEATED_EVENTS | 0.22706705664732252 | 0 | 30 / 3 ms | 0.0015299657929279914 |
| LEFT_REPEATED_EVENTS | 0 | 0.22706705664732252 | 30 / 3 ms | 0.0015299657929279914 |

Each active trajectory has 71 nonzero samples; inactive trajectories have zero.
Repeated responses retain only the source activation history: no actuator state.
Equal unilateral results under shared source assumptions are model symmetry,
not independent bilateral physiological measurements. No sum/average/jump
channel exists.

## Artifact, CLI and offline replay

Artifact schema: `ttm_exploratory_actuator_command_artifact_v1`.

- Artifact ID: `478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40`.
- Config hash: `94da685537241558bf1cc64ae9a8c051fce5a651f02bab871f192d518406b974`.
- Result hash: `78f277a4714f983d35212cd4314ec3a257664356426e1caf7cc3ce9214bf8c9f`.
- Size: 27,548 bytes, including `commands.json` and `manifest.json`.

Generated under the existing ignored `data/derived/malecns/looming_giant_fiber_v1`
root. Canonical JSON, content hashes and immutable directory identity follow
existing artifact conventions. No clocks, network or randomness.

```bash
python -m neurofly.ttm_actuator_cli generate
python -m neurofly.ttm_actuator_cli inspect ARTIFACT_DIRECTORY
python -m neurofly.ttm_actuator_cli replay ARTIFACT_DIRECTORY
```

Inspect explicitly labels exploratory functional commands, no physical force
and no joint motion, and shows source/config/routing, per-fixture channel
summaries and exclusions. Replay validates the persisted activation source,
recreates routing, commands/order/summaries/hashes and compares canonical bytes.
It rejects source identity/sample/body/side, routing/action, timing, command,
config and artifact mutations, including rehashed result tampering.

## Scientific boundary and Phase 12 handoff

No physical force, contraction state, geometry, joint target, strain, torque,
body impulse, velocity, gravity, collisions, contact, movement or scenario.
No visual asset is driven. Proxy ancestry is not exact G1 tracing or whole-TTM
homogeneous physiology. Existing gain confounds and external empirical-source
limitations remain unchanged. No fitting, scoring or empirical actuation claim.

NeuroFly still has no interactive scenario after 11B. It now has explicitly
addressed model-space motor-command trajectories ready for a future plant.

Exactly one next Phase 12A must decide **body/world plant and closed-loop
mechanics architecture**: kinematic versus dynamic first plant; coordinate
system; actuator-to-pose/body mapping; ground/contact assumptions; backend-owned
simulation state; and R3F rendering/interpolation with render FPS decoupled
from simulation ticks. No scripted looming→jump rule or LLM fly controller.
Physical calibration/geometry, if pursued, requires its own justified evidence
or explicit model assumptions. Do not add another Phase 11 metadata phase.

## Verification and decision

Focused final actuator suite: 42 passed. Combined actuator/10B/10C/8K regression:
117 passed. Full `python -m pytest` invocation: 895 passed, 1 deselected, two
existing dependency deprecation warnings. Four identity/semantic tests were
added after that invocation collected its cases; all four passed in the final
focused and combined regression runs (899 distinct passing cases overall).
Ruff check and format check pass; `git diff --check` passes. Frontend regression:
38 tests pass; lint, typecheck and build pass. The build-generated Next type
reference change was restored; no frontend changes remain.

Decision: `FIRST_EXPLORATORY_TTM_ACTUATOR_LAYER_VALIDATED`.
Phase 11B status: `PASS` for model/software routing, not biological actuation.
No commit/push. Only Phase 11B implementation, tests and documentation changes;
generated artifact is ignored.
