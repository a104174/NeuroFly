# Phase 28 — evidence-gated exploratory DNp15 → orientation embodiment

## Scope and decision

Stage A: **`EXPLORATORY_YAW_MAPPING_IDENTIFIABLE`**.

Identity: `TARGET_IDENTITY_COMPATIBLE_WITH_LIMITATIONS`.
Direction: `BILATERAL_DIRECTIONAL_RELATION_QUALITATIVELY_SUPPORTED`.
Body readiness: `QUALITATIVE_YAW_MAPPING_JUSTIFIED`.

Stage B **RUN**, with the first frozen results accepted unchanged.
Phase decision: **`EXPLORATORY_DNP15_YAW_EMBODIMENT_VALIDATED`**.
Here “validated” means deterministic execution, provenance, preregistration,
invariants and replay of an explicitly exploratory downstream model. It does
not validate physiological gain, instantaneous DNp15-to-yaw dynamics or a
biological turning angle.

The new model consumes frozen Phase 25 bilateral neural trajectories. V1,
Phase 25 feedforward dynamics, Phase 26 exclusions and Phase 27 neural-only
product semantics remain unchanged. No existing plant, API, playback schema
or frontend is modified. There is no browser, rendered fly or visual tuning.

## Stage A — bounded primary evidence

The audit rechecks original/public sources already relevant to the selected
motif. No author contact, broad literature expansion, data fitting, trace
digitization or new raw-data acquisition was needed.

| Primary source | Observation and applicability | Limits |
| --- | --- | --- |
| [Erginkaya et al. 2025](https://www.nature.com/articles/s41593-025-01948-9), Results/Figs. 1 and 7, Extended Data Fig. 10, Methods | Explicit DNp15/DNHS1 correspondence. Unilateral Kir2.1 silencing causes contralateral forward-path drift; ricin A ablation replicates this. Intact/bilateral conditions have no systematic bias. Saccades are not affected. | Chronic causal perturbation, not an isolated transient bilateral activity-to-yaw measurement. |
| [Suver et al. 2016, primary PubMed](https://pubmed.ncbi.nlm.nih.gov/27852783/), abstract/Figs. 2–4 and 7 | Historical DNHS1 morphology, HS association and rotational responses; motor correlations during tethered flight. | Flight head/wing/abdomen observables and correlations do not establish walking yaw causality. PMC/publisher challenged; Caltech publication metadata was accessible, but its PDF download failed. |
| [Pokusaeva et al. 2024, authentic primary PDF](https://research-explorer.ista.ac.at/download/18444/18459/2024_NatureComm_Pokusaeva.pdf), Fig. 7 and Discussion | HS–descending coupling including DNp15/DNHS1; chemical/electrical and stimulus-dependent course-control context. | No DNp15-specific yaw gain or justification for a complete linear optomotor model. |

The decisive walking experiment used male D. melanogaster with clipped wings,
moving freely in a heated-wall arena with tracked random-dot feedback.
Imaging used immobilized females. The behavioral quantity is angular path
deviation per forward distance, not a measured yaw transfer kernel. Suver's
accessible excerpts do not resolve sex for this audit; they do not set the sign.

### What the sign evidence permits

Left silencing → rightward drift; right silencing → leftward drift. Thus a
remaining-side dominance interpretation supports a **qualitative inference**
of ipsilateral course bias. This is stronger than topology or stimulus tuning
alone, but weaker than a measured graded bilateral subtraction rule.
Overall evidence is `MIXED_CAUSAL_AND_CORRELATIONAL`; the decisive intervention
record is `DIRECT_CAUSAL_MANIPULATION`.

A signed exploratory orientation abstraction is therefore justified **within
the walking-course interpretation**, without adopting a physical gain. The
positive orientation convention is rightward model course orientation. This
sign is not inferred from names or morphology coordinates. Exact experimental
cells are not asserted to equal MaleCNS bodies 11215/R and 12069/L.

The signed Phase 25 proxy is not biological activity. Its negative values,
linear amplitude interpretation and reversal symmetry remain explicit model
extensions, not measured negative firing or inhibitory motor effects. The
experimental network contains partners/electrical interactions absent from the
six-edge motif. None is activated or silently approximated here. The paper's
fitted model-agent parameters/equations are not adopted as biological evidence.

## Frozen scientific authorities and gate

Started clean at committed Phase 27, `HEAD == origin/main`:
`8ee08874f276b6ab85e195a46dfd37b7e8d49905`.

| Authority | Canonical identity |
| --- | --- |
| v1 scientific status | `1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6` |
| Phase 24 selection | `435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41` |
| Phase 25 preregistration | `371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074` |
| Phase 25 artifact | `2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113` |
| Phase 26 context audit | `04116360164262de5a2572f33e12cc90351869567c3202811807be576f1d03be` |
| Phase 27 integration document byte hash | `67612c85713d731929c466b4c8adb0eb0ad59786a97341289e006a26c277320d` |
| Phase 27 neural playback canonical hash | `52554962f3e9c85c6866b5e3ec56f8a12d24340db2236ec52c7809c6ece8d404` |

[Evidence record](dnp15_yaw_mapping_evidence_gate.json), schema
`dnp15_yaw_mapping_evidence_gate_v1`, canonical inner-record ID:
`42d46ef3e5deed0c36da518cc1523cfe3d0978e5cbed2aac85a9738fcdeadf2f`.
Canonical inner JSON: **8,337 bytes**; readable stored wrapper: **10,029 bytes**.
It records source/access limitations, identity, causal status, directional
inference, preparation, readiness, admission and exclusions. Stage A permits
only an explicitly uncalibrated orientation model.

## Stage B — preregistration and chronology

The gate was written, finalized and hash-validated before creating the new
model module. The [preregistration](dnp15_exploratory_yaw_preregistration.json)
was then written and independently hash-validated before any yaw execution:

- schema: `dnp15_exploratory_yaw_preregistration_v1`;
- ID: `1be0f6364070a5a5536f4c772bd47abb3be2f08357b439a51e03f034f8b2a654`;
- canonical JSON: **4,853 bytes**; readable stored file: **5,577 bytes**.

Before execution, checks compared the declared conditions/grid with the frozen
source contract and verified analytical bounds without running neural/yaw
candidates. Only then was the implementation created, statically checked and
the CLI `generate` invoked once for the first frozen execution. It executed
all six conditions; staging checked serialization without a second yaw run.
Subsequent replay/tests rerun only the same frozen assumptions. No parameter
changed after inspecting the first result. Regression tests mutating parameters
test identity/rejection, not alternate-parameter trajectory searches.

The interrupted initial pre-gate replay session was not assumed successful:
the complete gate was rerun and logged before Stage A. Scratch regression and
first-execution logs remain local under `/tmp`, not scientific runtime inputs.

## New neural-to-orientation contract

Model: `exploratory_yaw_orientation_plant_v1`.
Role: `EXPLORATORY_NEURAL_TO_ORIENTATION_MODEL`.

```text
delta[n] = DNp15_R[n] - DNp15_L[n]
drive[n] = directional_sign * dnp15_to_yaw_proxy_scale * delta[n]
orientation[n+1] = orientation[n] + (time[n+1]-time[n])/H * drive[n]
```

Frozen sign **+1**, scale **1**, initial orientation **0**, global H **50 ms**,
dt **0.1 ms**, horizon **50 ms**, **500 intervals / 501 boundaries**. Conditions
consume exactly the frozen 20 ms input pulse and 30 ms recovery source outputs.
No per-condition normalization, decay, saturation, inertia or yaw-rate state.

Scale 1 defines a model-coordinate passthrough, not physiological magnitude.
H is the shared source horizon: one held drive unit over that whole window
adds one orientation unit. It is neither a biological time constant nor a
duration chosen to produce a visible turn. Selection used no source peak or
yaw outcome. No radians or physical angular velocity are used internally.

| Quantity/assumption | Units/semantics | Classification |
| --- | --- | --- |
| DNp15 inputs | Frozen `dnp15_state_eq`, identities 11215/R and 12069/L | Source-authority constrained; biologically uncalibrated |
| Qualitative direction | Remaining-side course-bias inference | `QUALITATIVELY_EVIDENCE_CONSTRAINED` |
| Linear odd transform and bilateral symmetry | Explicit proxy-to-orientation assumption | `EXPLORATORY_BOUNDED_ASSUMPTION` |
| Drive scale | 1 `yaw_drive_eq` per `dnp15_state_eq` | `EXPLORATORY_BOUNDED_ASSUMPTION` |
| Orientation integration | `yaw_orientation_eq`; signed unwrapped proxy, not radians | `EXPLORATORY_BOUNDED_ASSUMPTION` |
| Grid and held-drive boundary order | Numerical time; final sample has no outgoing interval | `REPOSITORY_NUMERICAL_CONVENTION` |
| Physical gain, forces, inertia | Not modelled | `NOT_IDENTIFIABLE_AND_EXCLUDED` |
| Recurrence/electrical coupling/sensory feedback | Not modelled | `NOT_IDENTIFIABLE_AND_EXCLUDED` |

The plant owns only orientation. Translation is **NOT_MODELLED**, not a
fabricated measured zero x/z output. No motor/actuator/body-plant dependency
or environment→optic-flow feedback exists. Phase 27 remains neural-only.

### Analytical bound and boundary semantics

Frozen signed descriptors lie in [-1,1]. Neutral initial states and exact
exponential convex updates keep all six HS and both DNp15 states within that
range. Therefore |delta|≤2 and, with unit scale, |drive|≤2. Since sum(dt/H)=1
over the finite horizon, |orientation−initial|≤2. This is a finite-horizon
bound on an integrator, **not asymptotic stability** or permission to extend
the horizon. No clamp is used; invalid inputs/domains fail explicitly.

At boundary n, the declared drive acts over n→n+1. The final drive is stored
as a diagnostic but never integrated without an outgoing interval. Equal
bilateral targets yield zero drive and unchanged orientation. First nonzero
source target state is at boundary 2; first orientation change is at boundary
3 (0.3 ms), a discrete model latency, not biological latency.

## First frozen results

All source rows and persisted R−L arrays match canonical Phase 25 exactly.
The extrema below are signed neural extrema; for bilateral matching the two
neural extrema are nonzero despite the differential remaining zero throughout.

| Condition | DNp15 R extremum | DNp15 L extremum | R−L / drive extremum | Final orientation |
| --- | --- | --- | --- | --- |
| NO_MOTION_CONTROL | 0 | 0 | 0 | 0 |
| BILATERAL_MATCHED_MOTION | +0.761610396111446 | +0.761610396111446 | 0 | 0 |
| RIGHT_SIDE_MOTION | +0.761610396111446 | 0 | +0.761610396111446 | +0.382855392953294 |
| LEFT_SIDE_MOTION | 0 | +0.761610396111446 | −0.761610396111446 | −0.382855392953294 |
| SIDE_SWAPPED_EQUIVALENT | 0 | +0.761610396111446 | −0.761610396111446 | −0.382855392953294 |
| DIRECTION_REVERSED | −0.761610396111446 | 0 | −0.761610396111446 | −0.382855392953294 |

Nonzero neural/drive absolute peaks are at 21.3 ms; nonzero orientation
absolute peaks are the final 50 ms boundary. No yaw-rate state/peak is defined.
Zero trajectories have a tied peak at every boundary (summary selects the first).
Unilateral and reversed orientations are model-symmetric negatives, not
measured biological symmetry. Persistent final orientation follows from the
preregistered integrator, not a fitted persistence mechanism or desired angle.

## Artifact, replay and performance

Schema: `dnp15_exploratory_yaw_artifact_v1`.

| Identity | SHA-256 |
| --- | --- |
| Artifact | `243914905c17ceb1285c645aa9e9700b602a9e22c8703c9f9ce4c7fe4f7e935d` |
| Config | `450f885f09450242351f90f9c5e923711d36a4db4a513debd2b075a95ba78758` |
| Result | `ac0bd5bf36b5f1c60c96a212f7b5f28d5a30f49c470902d543ec15174af394f0` |

Size including manifest: **225,004 bytes**, stored under existing ignored
`data/derived/experiments/dnp15_exploratory_yaw_artifact_v1` conventions.
First generation: **0.1384 s**; five replay times 0.1268, 0.1238, 0.1241,
0.1218 and 0.1253 s; median **0.1241 s**. Times are local diagnostics, not hashed.

CLI: `python -m neurofly.dnp15_exploratory_yaw_cli generate`,
`inspect ARTIFACT`, `replay ARTIFACT`. Production accepts no sign/gain/condition
overrides. Offline replay validates the frozen evidence gate and preregistration,
replays the canonical Phase 25 source and checks its identities/config/result,
reconstructs exact inputs, reexecutes all conditions and compares canonical
bytes. Serialization manifest/directory identities are checked separately.
No network, randomness, new source model or simulated feedback is used.

Tests cover gate blocking before execution/storage, authority/units, neutral
and matched behavior, side/reversal identities, exact source inputs, first/final
boundary semantics, invalid domains and unchanged outputs under test-local
contact-provenance mutation. Sign/gain/authority/condition/input/differential/
drive/orientation/time/hash tampering is rejected, even with self-consistent
rewritten envelopes. Changed source traces invalidate source replay.

## Verification closure

Before/after canonical replay passed for Phases 7O, 8C, 13B, corrected 16,
18 and 25. All four existing playback payload hashes and frozen authority
file hashes matched exactly. Focused embodiment/Phase 25/Phase 26 tests:
**70 passed**. Full Python suite: **1,114 passed, 1 integration test deselected**,
with two dependency deprecation warnings (548.91 s). Ruff check and format
check and `git diff --check` passed. Frontend regression: **59 tests passed**;
lint, typecheck and build passed. Generated Next.js type-path changes were
restored; no frontend change is retained. Phase 28 status: **PASS**.

## Claim budget and remaining limits

Allowed: exploratory DNp15-linked model-space orientation; an evidence-gated
neural-to-embodiment proxy; deterministic downstream response and bilateral
model invariants. Forbidden: biological yaw prediction, calibrated turn rate,
torque, aerodynamic steering, measured DNp15 motor command, navigation,
complete optomotor behavior or closed-loop course stabilization.

No transfer calibration was performed. Unknowns include proxy→biological
activity, graded motor transfer, physical scale/dynamics, preparation dependence,
recurrent/electrical processing and orientation→visual-feedback geometry.
Neither source contact counts nor published fitted agent parameters resolve
these unknowns. The v1 plant remains frozen; all seven excluded chemical
context edges and electrical coupling stay inactive.

Exactly one next bounded action: **specify and analytically audit an exploratory
orientation→horizontal-motion world observation contract before any closed-loop
course-control experiment**, preserving a separate neural-only Phase 27 scenario
and keeping physical optic-flow calibration out of scope.
