# Phase 29 — orientation-to-horizontal-motion observation contract

## Scope and staged decisions

Stage A classification:
`GEOMETRIC_OBSERVATION_REQUIRES_BOUNDED_EXPLORATORY_ASSUMPTIONS`.
Stage A decision: `ORIENTATION_TO_MOTION_OBSERVATION_IDENTIFIABLE`.
Stage B: **RUN**, geometric operator only.
Final decision: `OBSERVATION_OPERATOR_SPECIFIED_WITH_EXPLORATORY_NORMALIZATION`.

This phase defines a missing observation layer, **not** a course-control
experiment. No observation output is fed to HS/DNp15 or to an orientation
integrator. No frontend, API, v1 plant, frozen neural model, recurrent edge or
electrical coupling is changed. No biological gain is fitted or selected.

## Repository gate and actual architecture

Started clean on `main == origin/main` at committed Phase 28,
`bd440b5e35bedbf820f12ed71f9120507c980a79`.

The existing Phase 13B/18 world is a looming object with relative x/z distance
and angular-size projection. The v1 planar plant has fixed +Z heading and
common-mode forward motion. Neither supplies the missing rotational observation;
reusing that projection would invent a new retinal interpretation.

Phase 25 takes independent signed R/L `horizontal_motion_eq` descriptors in
[-1,1]. Positive input is qualitatively motivated by ipsilateral front-to-back
sensitivity, while equal negative tuning and type sharing are proxy conventions.
Phase 28 stores an **unwrapped orientation proxy, explicitly not radians**.
It supplies no visual geometry. These contracts remain frozen.

The authority table in the [machine-readable contract](orientation_to_horizontal_motion_contract.json)
pins v1 status, Phase 24 selection, Phase 25 preregistration/artifact/config/result,
Phase 26 context audit, Phase 27 integration-document bytes and Phase 28
evidence/preregistration/artifact/config/result. Checks use actual committed
records and canonical serialization, not prompt-only identities. All four
existing scenario payload hashes are captured before and after the phase.

## Stage A — geometry is not biological visual transduction

The audit inspected the actual frozen source, geometry, stepping and artifact
conventions. The new sign is derived mathematically from a declared coordinate
system, not inferred from MaleCNS laterality or from neural outputs. No new
physiological claim requires a literature-derived calibration in this phase.
The earlier biological claims/limits are preserved rather than extended.

The five layers are deliberately separate:

| Layer | Quantity | Meaning |
| --- | --- | --- |
| World geometry | `world_heading_eq` | Independent world-fixed heading marker |
| Body/view orientation | `yaw_orientation_eq` | Unwrapped Phase 28 proxy |
| Relative view | `relative_view_eq` plus its lift | World-minus-body geometry |
| Interval observation | shift and `relative_view_eq_per_ms` | Mean finite-difference view motion |
| Neural input descriptor | `horizontal_motion_eq`, R/L | Bounded side-basis coordinates, not neural execution |

A geometric observation is permissible without knowing photoreceptor,
ommatidial, motion-detector or HS transduction. The panorama interpretation,
reference scale and side bases therefore remain **exploratory assumptions**.
This does not establish an observation operator in biological assay units.

## World and coordinate convention

Use one world-fixed heading reference on an abstract periodic panorama. The
canonical reference is zero, independently declared—not computed to oppose the
body. A different fixed reference changes relative view position, not rotation
motion. No texture, distance, ray tracing or hemifield coverage is represented.
Position is fixed; x/z and translation are absent.

Zero body coordinate aligns with world heading zero. Positive body coordinate
is rightward model-course orientation, matching Phase 28's sign convention.
The new observation layer interprets **one orientation_eq per abstract cycle**,
period P=1. This is a new coordinate interpretation, not a modification of
Phase 28's unwrapped state and not physical angular calibration. No radians,
degrees or measured angular velocity are used.

Both body endpoints retain winding as unwrapped coordinates. The view
representation wraps to [-P/2,P/2). A body increment must be strictly smaller
than half a cycle. Equality, missing winding or larger jumps are rejected;
the operator does not guess a motion direction. Wrapping the view itself is
ordinary geometry, not an invalid state.

## Frozen observation equation

For a completed interval with held world reference w and body endpoints b0,b1:

```text
r0 = w - b0                         # unwrapped relative lift
r1 = w - b1
v0 = wrap(r0); v1 = wrap(r1)        # displayed/stored relative view
d = -(b1 - b0)                     # winding-aware view displacement
raw = d / (t1 - t0)                # interval-mean model-space rate
unclipped = 50 ms * raw / P
global = clip(unclipped, -1, +1)
right = global
left = -global
```

The implementation uses the body increment directly to preserve the continuous
relative lift, avoiding a naive subtraction across the wrapped view seam.
For finite floating-point data, coordinate/rate overflow is an explicit error.

### Absolute orientation is not motion

At a static nonzero offset, r and v may be nonzero, but d=0 and both descriptors
are exactly zero. This is not a positional-error controller such as
`horizontal_motion_eq = -yaw_orientation_eq`.

### Sign derivation

Let w=0, b0=0, b1=+0.01 over 1 ms. Then r changes from 0 to -0.01: increasing
rightward body orientation shifts the fixed reference toward decreasing view
coordinate. raw=-0.01 and global=-0.5; R=-0.5, L=+0.5. The opposite body
increment reverses these signs. This follows frame subtraction, not the names
“right neuron” and “left neuron.”

### Global normalization and clipping

The reference rate is one abstract cycle per **global 50 ms** window, chosen
before execution from declared coordinates and the frozen source horizon.
It was not derived from observed peaks, orientation outcomes or feedback
stability. There is no per-condition maximum normalization.

Clipping is explicitly reported; a value already exactly at ±1 is not marked
clipped. This is model-space bounding, not biological visual saturation. Invalid
NaN/Inf/overflow inputs are never clipped into valid scientific values.

### R/L projection

There is one global view-motion quantity, not two invented retinal images.
Its right-side descriptor basis increases with view coordinate; its left-side
basis decreases. Thus R=h and L=-h. The opposite bases are an explicit
exploratory proxy projection, **not measured tuning or receptive-field geometry**.
They satisfy Phase 25's signed range without changing its input semantics.
This is not the RIGHT_SIDE_MOTION condition, which intentionally activates only
one side; the new geometric observation normally supplies both side descriptors.

## Temporal and future causal boundary ordering

The operator takes finite consecutive endpoint times; dt must be positive.
It is not hard-wired to 0.1 ms. A rate-like descriptor divides displacement
by dt, so equal constant model-space rotation rates yield equal descriptors
under different sampling intervals, provided the half-cycle domain holds.
The displacement itself scales with interval duration. Neither is biological
angular velocity.

At boundary zero there is no completed observation interval: neutral R=L=0.
At boundary n>=1:

1. Accept the authoritative endpoints of completed interval [n-1,n].
2. Produce and latch the observation at n for the next interval [n,n+1].
3. A **future** experiment may update source and target states simultaneously
   using their old states and the frozen Phase 25 equations.
4. It may update orientation using old target states and the frozen Phase 28
   equation. Only the resulting endpoint becomes available for the next
   completed-interval observation.

No current-boundary algebraic loop is allowed. The final completed interval
can be observed, but its output is not consumed without a separately declared
next interval. No future experiment was run here.

## Preregistration and content identity

The combined contract also serves as
`orientation_to_horizontal_motion_preregistration_v1`. Its complete scientific
content was serialized, independently hash-validated and declared frozen
**before the operator module and numerical tests were executed**.

- Contract schema: `orientation_to_horizontal_motion_contract_v1`.
- Canonical SHA-256:
  `9e58649144a4cf3ca7cd913a6cf91dde116524906b0c600dd09f5e66ec5ffaad`.
- Canonical JSON: **11,708 bytes**; stored readable JSON: **12,507 bytes**.

Frozen fields include world/period, normalization, sign/side bases, interval
semantics, equations, initial neutral descriptor, synthetic cases and claim
limits. Numerical test results caused no change to these fields.

The dedicated `orientation_to_horizontal_motion` module uses typed immutable
`WorldReference`, `OrientationBoundary`, `ObservationInterval`,
`ObservationContract` and `HorizontalMotionObservation` records. The result
contains typed geometry, interval indices/times, relative lifts and wrapped
views, displacement/rate, unclipped/global/R/L values, clipping status,
model-space units and contract provenance. No opaque scientific blob, neural
identity or structural count is accepted. Serialization is deterministic.

## Analytical invariants and synthetic validation

For held w, d=-Δb. Zero change yields zero; negating change negates raw motion.
Symmetric clipping preserves oddness and bounds each descriptor in [-1,1].
Adding the same constant to w,b0,b1 leaves relative geometry unchanged. A
wrapped view seam changes representation, not the continuous difference.
These are mathematical properties, not biological response claims.

| Synthetic case | Global descriptor | Interpretation |
| --- | ---: | --- |
| Zero orientation held | 0 | No view change |
| Static +0.25 offset | 0 | Position is not motion |
| +0.01 step / 1 ms | -0.5 | Opposite apparent view shift |
| -0.01 step / 1 ms | +0.5 | Sign reversal |
| +0.01 per 1 ms, two intervals | -0.5, -0.5 | Constant rate |
| +0.01 then return to zero | -0.5, +0.5 | Reversal |
| Body 0.49→0.51 / 1 ms | -1 | True shift -0.02; saturation at boundary |
| Same seam crossing / 10 ms | -0.1 | No false full-cycle impulse |
| +0.1 / 1 ms | -1, clipped | Explicit model-space saturation |

In the wrap case, relative views are -0.49 and +0.49, but displacement is
-0.02, not +0.98. An input 0.49→-0.49 without winding is rejected rather than
silently interpreted as a seam crossing.
Clipping flags report changes to the computed floating-point value, including
roundoff near a saturation boundary; there is no hidden clipping tolerance.

The Phase 28 compatibility test checks the stored canonical artifact/config/
result hashes and then mechanically accepts all six 501-boundary orientation
arrays (3,000 intervals) through the observation API. It does not optimize,
fit, compare biological waveforms or send any descriptor back to Phase 25.
Historical replay is separate and only reexecutes already frozen experiments.
Analytically, the frozen Phase 28 bound |drive|<=2 on its 0.1 ms grid implies
|body increment|<=0.004 eq, below the half-cycle limit. This bound uses declared
model assumptions, not observed peaks.

## Error, identity and dependency protection

Typed error codes cover invalid coordinates, invalid/nonpositive time intervals,
nonconsecutive boundaries, malformed world references, ambiguous/discontinuous
intervals and contract-authority mismatch. Immutable typed config cannot present
an altered normalization under the frozen ID. Semantic mutations change the
canonical hash and are rejected. Observation validation reconstructs from its
geometry, so changing output values and recomputing their hash is insufficient.

Focused tests cover all declared cases, sample-rate behavior, overflow and
non-finite rejection, canonical ordering, contract/result tampering, frozen
source identities and no neural/body execution. A dependency test verifies that
the only project import is the existing pure canonical-JSON utility; neural,
body, scenario and frontend kernels are not dependencies. Structural weights
and body IDs are not operator inputs. Rendering remains entirely separate.

## Verification closure

Before/after replays passed for Phases 7O, 8C, 13B, corrected 16, 18 and 25;
Phase 28 replay also reproduced its artifact/config/result identities. All
four Phase 27 scenario payload hashes and frozen authority records remained
unchanged. The focused suite passed **51 tests**. The full Python suite passed
**1,165 tests**, with one integration test deselected and two dependency
deprecation warnings (567.87 s). Ruff check/format check and `git diff --check`
passed. Frontend regression passed **59 tests**, lint, typecheck and build.
Generated Next.js type-file changes were restored and typecheck rerun; no
frontend change remains. No new simulation/validation artifact was generated.
Existing source artifacts remain ignored. Phase 29 status: **PASS**.

## Scientific claim budget and Phase 30 boundary

Allowed: a deterministic, bounded model-space geometric observation;
explicit sign, wrap, interval and side-basis semantics; compatibility with
the frozen signed neural input range.

Forbidden: calibrated optic flow, biological angular velocity, retinal
registration, measured HS transduction, physical yaw, steering prediction or
demonstrated closed-loop stabilization. A geometrically coherent operator does
not establish biological correctness or closed-loop stability.

A future Phase 30 interface can consume a completed orientation interval and
hold its descriptors for the next neural interval. It must be a **new**
preregistered experiment, declaring initialization/exogenous perturbation,
world reference, latched timing, invalid-state policy and result-agnostic
acceptance. It may reuse the frozen equations, but cannot rewrite the canonical
Phase 25 pulse experiment, Phase 28 open-loop artifact or Phase 27 neural-only
scenario. No dynamic feedback scenario has been created here.

Exactly one next bounded action: **preregister a backend-only course-control
experiment using this completed-interval observation contract and the frozen
Phase 25/28 equations, including controls and an analytical stability audit
before any closed-loop execution**.
