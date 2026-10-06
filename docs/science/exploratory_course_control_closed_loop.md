# Phase 30 — preregistered exploratory course-control composition

## Scope and decisions

Stage A: `CLOSED_LOOP_COMPOSITION_MARGINAL_BUT_BOUNDED_FOR_FINITE_HORIZON_TEST`.
Stage B: **RUN**, first frozen results accepted unchanged.
Scientific decision: `CLOSED_LOOP_VALIDATED_WITH_MARGINAL_DYNAMICS`.

“Validated” means explicit causal composition, analytical admission,
preregistration, numerical consistency, controls and deterministic replay.
It does not mean biological steering, optomotor stabilization, calibrated yaw,
heading restoration, navigation or a complete HS/DNp15 network.

The experiment is backend-only. It changes no frozen component, v1 plant,
scenario, API or frontend. No translation, physical mechanics, electrical
coupling or excluded chemical-context edge is introduced. The only new loop
is world/view observation → neural proxies → exploratory orientation.

## Repository and authority gate

Started clean at committed Phase 29,
`9491bb40981c76f813fafb12ecf1bc033d26bbba`, `HEAD == origin/main`.
Before design/execution, canonical replays passed for Phases 7O, 8C, 13B,
corrected 16, 18, 25 and 28; the four Phase 27 payload hashes were captured.

The [preregistration](exploratory_course_control_closed_loop_preregistration.json)
pins the actual v1/Phase 24/25/26/27/28/29 authorities, including both source
artifacts' config/result identities. Source document identities are validated
offline; context metadata are not used to select any numerical parameter.
The six active routes and source/target identity order come from Phase 25's
validated structural contract. The surrounding seven chemical edges remain
excluded. The existing source artifacts are replayed, not rewritten.

## Frozen component interfaces

| Component | Public interface used | Scientific role |
| --- | --- | --- |
| Phase 29 | Typed world/boundaries, `observe_interval`, neutral initial descriptors | Completed-interval geometric observation |
| Phase 25 | `route_contributions`, `proxy_step`, validated preregistration | Six sources, two targets, three-channel means and old-state exponential stepping |
| Phase 28 | `integrate_orientation`, validated preregistration | Old-target differential drive and horizon-normalized orientation increment |

The Phase 28 integrator is invoked on local `[0, actual_interval_dt]` with the
old target pair held. Its neutral-origin increment is accumulated in the
authoritative experiment orientation. This is valid for the frozen additive,
non-leaky integrator; it does **not** reset body orientation each interval.
The external perturbation and open-loop disconnection are explicit experiment
interventions, not new component coefficients.

## Complete state and causal order

State coordinates are six identity-resolved HS proxies, two DNp15 proxies,
orientation, previous orientation and latched R/L descriptors: 12 coordinates
with latch/history consistency constraints. Geometric telemetry and per-route
contributions are derived readouts, not extra dynamic state.

At boundary n:

1. Orientation and old neural states are authoritative.
2. For n>=1, observe completed interval [n-1,n]; at n=0 latch neutral R=L=0.
3. Route **old** source states to the targets.
4. Compute the orientation increment from **old** target states.
5. Compute source and target updates simultaneously from old states.
6. Apply the connected neural orientation increment and the declared external
   increment; commit all new states to n+1.
7. Only then can the next completed interval be observed.

There is no same-boundary algebraic feedback. Final-boundary observation exists
but is not consumed; no extra integration or perturbation occurs.
Neural dt remains the frozen 0.1 ms parameter. Phase 28/29 use actual endpoint
differences of `n*dt`, matching their existing floating-point time semantics.

## Composed equations and initialization

With old-state variables, dt=0.1 ms and H=50 ms:

```text
u_R[n],u_L[n] = Phase29(theta[n-1],theta[n])   # neutral at n=0
D_j[n] = mean(three eligible HS states[n])
s_i[n+1] = u_side[n] + (s_i[n]-u_side[n])*exp(-dt/5 ms)
y_j[n+1] = D_j[n] + (y_j[n]-D_j[n])*exp(-dt/10 ms)
delta[n] = y_R[n]-y_L[n]
proposed_increment[n] = actual_dt/50 ms * delta[n]
theta[n+1] = theta[n] + connected_increment[n] + external_increment[n]
```

All source/target/orientation states start at zero. Previous orientation is
undefined until the first interval completes. No permanent bias exists.

The externally imposed increment is applied only over interval 0→1. Magnitude
**0.001 orientation_eq** is half one descriptor-reference displacement:
`0.5 * (0.1 ms / 50 ms) * period_eq`. It was chosen before outputs, not from
neural peaks, desired visible angle or settling time. The perturbation exists
independently of neural activity. A static offset alone would not stimulate
this motion-only sensor.

| Canonical condition | External increment | Neural orientation connection |
| --- | ---: | --- |
| NO_PERTURBATION_CONTROL | 0 | Connected |
| OPEN_LOOP_PERTURBATION | +0.001 | Disconnected |
| CLOSED_LOOP_PERTURBATION | +0.001 | Connected |
| SIGN_REVERSED_PERTURBATION | -0.001 | Connected |

The open-loop condition still computes observation, all neural states and the
proposed Phase 28 increment; only its application to orientation is disconnected.
All four conditions share exactly the same scientific coefficients.

## Stage A — analytical admission before execution

Let a=exp(-0.1/5), b=exp(-0.1/10), S=mean_R_HS−mean_L_HS and Y=DNp15_R−DNp15_L.
After the external perturbation ends, the unsaturated observation gives
`u_R[n]=-Y[n-1]`, `u_L[n]=+Y[n-1]`. Thus the reduced motion system is:

```text
[S[n+1]]   [a     0     -2(1-a)] [S[n]  ]
[Y[n+1]] = [1-b   b      0     ] [Y[n]  ]
[Y[n]  ]   [0     1      0     ] [Y[n-1]]
```

Characteristic polynomial: `lambda*(lambda-a)*(lambda-b)+2*(1-a)*(1-b)`.

Eigenvalues:

- `0.9853271132380736 ± 0.019379013304609324 i`;
- `-0.0004057194202238363`.

Motion spectral radius: **0.985517664092702**, strictly below one. The full
12-coordinate system additionally has one simple orientation eigenvalue 1,
a with multiplicity five, b once and two zero bookkeeping/latch modes.
The unit mode is semisimple: fixed orientation offsets are neutral equilibria.
The full system is **marginal**, not asymptotically heading-restoring; its motion
subsystem has decaying oscillatory modes. Negative feedback includes the
completed-interval delay, old-source target update and old-target orientation
update. No zero-delay or updated-target shortcut is used.

Clipping is not needed to stabilize the local poles. The global frozen input
bound provides a finite-horizon guarantee: convex updates and three-channel
means keep HS/targets in [-1,1], |drive|<=2, and total neural orientation change
within 2 over 50 ms. Add at most .001 external displacement. Each neural
increment is at most .004; even the conservative perturbed-interval bound .005
is below Phase 29's .5-cycle limit. No unstable mode was hidden by shortening
duration, clipping or changing any coefficient.

Horizon **50 ms** was selected before execution: five target time constants,
ten source time constants and the existing orientation validation horizon.
No longer-horizon or global nonlinear-stability claim follows.

## Preregistration and freeze chronology

The analytical matrix/eigenspectrum were computed without any time-domain
candidate execution. Stage A explicitly admitted the marginal finite-horizon
probe. Complete composition, controls, runtime policy, metrics and source
identities were serialized and hash-validated before the module's first run.
Then the CLI generated all four conditions once; staging checked serialization
without another closed-loop execution. Subsequent tests/replays use the same
frozen assumptions. No scientific parameter changed after first output.

- Preregistration schema: `exploratory_course_control_closed_loop_preregistration_v1`.
- ID: `efc27a18e1d19119b8eebc5d0f8b91e61a47337dbb9f60e2518fabc42672cd0f`.
- Canonical bytes: **11,422**; readable stored bytes: **12,099**.
- Analysis schema: `exploratory_course_control_composition_analysis_v1`.
- Analysis ID: `a8e82f1561df6deb05216d795f7d61067c9338fefffb5cb7d2a415f6a3464586`.

The analysis is embedded in the preregistration and artifact. Material equation,
ordering, parameter, intervention or authority changes invalidate identity.

## First frozen numerical results

All conditions completed 500 valid intervals / 501 boundaries.

| Condition | Max abs orientation | Final orientation | Max abs descriptor | Peak abs DNp15 differential | Final abs differential |
| --- | ---: | ---: | ---: | ---: | ---: |
| Neutral | 0 | 0 | 0 | 0 | 0 |
| Open-loop + | .001 | .001 | .5 | .005000033653048 | .000136538472044 |
| Closed-loop + | .001 | .000332771016558 | .5 | .004086408549839 | .000002560801061 |
| Closed-loop − | .001 | -.000332771016558 | .5 | .004086408549839 | .000002560801061 |

All values are model-space. No physical angular state/rate is introduced.
Neutral states remain exactly zero. Opposite perturbations produce exact odd
symmetry in neural states, orientation and side descriptors under these frozen
model assumptions—not measured bilateral fly symmetry.

Closed-loop differential sign changes/zero-crossing brackets: **3**;
descriptor transitions: **4**; orientation crossings: **0**. Open-loop and
neutral counts are zero. Counts skip exact zero samples and count successive
nonzero sign transitions; no fitted zero-crossing times or tolerance is used.

The perturbation is observed at .1 ms; source response first appears at .2 ms,
target response at .3 ms, and neural-mediated orientation change at .4 ms.
These are composition indices, not biological latency measurements.

### Open vs closed — do not overinterpret

Both conditions receive precisely the same external pulse and reach the same
maximum descriptor .5 and maximum orientation .001. Open loop stops changing
orientation immediately after the imposed step. Closed loop introduces a
counter-rotation of net -.00066722898344224 eq, with small decaying reversals,
and retains a nonzero offset. Post-pulse descriptor magnitude is zero in open
loop and peaks at .004086408549838547 in closed loop: feedback **creates** that
counter-motion rather than lowering motion relative to an already stationary
open-loop body. No inertia or continuing imposed motion exists here.

The local motion/neural modes decay and the observed late differential is
small, but orientation does not restore world heading zero. This is a motion
perturbation response, not a positional-error controller, biological reflex or
claim that feedback is behaviorally superior.

### Saturation and validity

Each condition has **0/500 clipped observed intervals**, fraction 0, positive/
negative counts 0, duration 0 ms. The final observation is included but not
consumed. There is no reliance on clipping in these canonical outcomes.
Synthetic unit tests verify that genuine clipping is counted with its sign,
duration and frozen Phase 29 semantics.

Non-finite/domain-invalid states terminate deterministically with a reason and
last valid trajectory; authority mismatch prevents execution. No invalid values
are silently clamped or remaining samples fabricated. Finite unexpected or
oscillatory output is not an invalid state. All canonical statuses are
`COMPLETED_VALID_HORIZON`.

## Artifact, replay and performance

- Schema: `exploratory_course_control_closed_loop_artifact_v1`.
- ID: `f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581`.
- Config: `a87bbae9566430d87f2f7893001d4824ff8006bfcb979510af352cab2f7c7df3`.
- Result: `3837bae425878c6b4696cd561d7465dd5d5ce073fae56fa4746a1251e0ba5ae9`.
- Size including manifest: **4,354,437 bytes**.
- First generation: **0.6708 s**; measured replay: **0.5523 s**.

Stored in the existing ignored `data/derived/experiments` hierarchy. The artifact
retains complete per-boundary geometry, old/new temporal context, six source
and two target states, selected-route contributions, proposed/applied/external
increments, clipping flags, diagnostics, validity, analysis and source IDs.
It is scientific source data, not a frontend payload.

CLI: `python -m neurofly.exploratory_course_control_cli generate`,
`inspect ARTIFACT`, `replay ARTIFACT`. No gain/sign/duration override is offered.
Replay validates all source document and numerical artifact identities,
preregistration, analysis and reconstructed trajectories, then compares canonical
bytes/hash offline. No network or randomness is required. Rehashed authority,
ordering, perturbation, condition, observation, source/target, drive, orientation,
clipping, termination and analysis tampering is rejected.

## Verification closure

Before/after replay passed unchanged for Phases 7O, 8C, 13B, corrected 16, 18,
25 and 28. All four Phase 27 scenario payload hashes matched; v1 and Phase
24–29 authorities remained unchanged. Focused composition tests: **32 passed**.
Full Python suite: **1,197 passed**, one integration test deselected and two
dependency deprecation warnings (557.76 s). Ruff check/format and
`git diff --check` passed. Frontend regression: **59 tests passed**, plus lint,
typecheck and build; generated type-file changes were restored and typecheck
rerun. No API/frontend changes remain. Source and new artifacts remain ignored.
Phase 30 status: **PASS**. Nothing was staged, committed or pushed.

## Claim budget and next boundary

Allowed: exploratory connectome-structured model-space motion feedback;
identity-resolved neural mediation; deterministic finite-horizon composition;
marginal absolute orientation with decaying local motion modes.

Forbidden: biological optomotor stabilization, calibrated course control/yaw,
fly navigation or heading control, physical torque/optic flow and a complete
HS/DNp15 network. The v1 freeze and Phase 27 neural-only product remain intact.

Exactly one next bounded action: **specify a separate backend-authoritative
course-control playback contract for this frozen artifact, preserving the
Phase 27 neural-only scenario and the motion-versus-heading limitations**.
