# Planar steering v0 — preregistered shadow experiment

## Stage A, before operator implementation

Baseline: `main`, `8b050b5f5bda9f3418a594a8ddd60a2b4d6ea734`, clean.
The operator reports that the versioned JSON preregistration was written before
the observation operator or any new numerical experiment. Independent prospective
chronology is not established by the uncommitted files or their declaration flags.
The preregistration is preserved byte-for-byte; its canonical ID is
`49e91a10fa49c5d7004f28249b63f334a0e23767c20108f5578a0e2586c9767a`.
This is a new engineering observation contract, not a change to Course or D2.2.

Question: can prescribed planar pose changes produce traceable sensory and
HS/DNp15 responses and a shadow differential through the unchanged six routes?

### Geometry and analytical gate

Use +X right, +Z forward and unwrapped heading `h` in abstract cycles. Define
`theta = 2*pi*h` as a geometric embedding, not measured biological yaw. Two
fixed named landmarks sample channels R/L. For a landmark relative vector
`(X,Z)`, world bearing is `atan2(X,Z)` and body-relative bearing is
`beta = atan2(X,Z) - theta`.

Over a completed interval, use the shortest signed world-bearing difference
and subtract the continuous heading increment. Divide by `2*pi*dt_ms`,
normalize with the existing 50 ms reference window, then multiply by +1 for R
or -1 for L. Clip only these finite normalized descriptors to [-1,1], recording
the raw quantities and individual clipping flags. A stationary rotation thus
reduces exactly to the existing Course side-basis convention. Translation is
new geometry, not a copied Course input.

For infinitesimal translation, `dphi = (-Z*dx + X*dz)/(X^2+Z^2)`.
This proves the expected signs before neural execution:

* Symmetric forward references (+/-2,4) produce equal positive side descriptors
  for forward translation; differential steering is zero despite neural response.
* Depth asymmetry, R=(2,2), L=(-2,4), gives sensitivities 1/4 and 1/10 to forward
  motion before normalization. A signed differential is therefore testable.
* Mirroring X and heading and swapping channel labels swaps descriptors and
  targets. A common rigid frame change leaves descriptors invariant.

These are mathematical properties of the chosen model, not physiological
calibration. The operator is not generally able to identify translation versus
rotation from two descriptors. Prescribed pose increments record the cause;
they are never inferred from a neural differential.

Reject landmark coincidence, a straight swept pose segment within 1e-9 world_eq
of a landmark, non-finite values, nonpositive time intervals, unordered boundaries
and half-cycle/ambiguous bearing or heading changes. The distance threshold is
a numerical domain exclusion, not body size or contact sensing.

### Frozen protocol

The JSON contains complete landmark geometry and deterministic pose recipes.
Each of 12 conditions has 501 boundaries at dt=0.1 ms: a linear prescribed
excursion during the first 200 intervals, then 30 ms held pose. Translation is
0.1 world_eq; rotation is 0.001 heading_eq. These are engineering inputs.
No values were selected from new neural outcomes. Expanded poses must be
included in each recoverable run configuration.

Observe [n-1,n] at boundary n; boundary zero has no observation and neutral
input. Update HS and DNp15 simultaneously from old states. The final observation
is stored but not consumed. All readouts are `SHADOW_ONLY`; outgoing increments
are null at the final boundary and never added to a pose.

Intact and sham use the identical pipeline. Readout-disabled retains computed
states/drive/proposal but disconnects the exposed enabled readout. This is a
software readout control, not biological ablation. Selected neural-route
interruption is unavailable without changing the frozen kernel, which rejects
altered inventories; no such alteration is authorized or implemented.

### Gates and falsifiability

A: independent analytical geometry, signs, zeros, symmetry, rigid-frame
invariance, invalid domains and explicit saturation pass.

B: all states/readouts follow the frozen kernels and old-state causality;
prescribed poses remain identical across interventions. Asymmetric conditions
must yield a nonzero model differential with the preregistered sign for the
shadow hypothesis to pass. A zero result must be reported, not retuned.

C: recoverable configuration, complete telemetry, pinned authorities/source
code, canonical hashes, same-environment deterministic replay and unchanged
five frozen scenario payload hashes pass.

Numerical tolerance 1e-12 is a float64 comparison allowance, not a biological
effect threshold. Exact zero/identity cases use exact comparison where valid.
No significance, locomotion, retinal calibration, force, speed, collision,
autonomous behaviour or complete biological-network claim follows from PASS.

### Independent review and consolidation limits

For symmetric references, the local equations are
`u_R=K*(-0.2*v_x+0.1*v_z-omega)` and
`u_L=K*(+0.2*v_x+0.1*v_z+omega)`, where `K=50/(2*pi)`, velocities
use world_eq/ms and `omega` is the geometric heading rate in radians/ms.
Two descriptors cannot generally identify three unknown planar motion components.
Depth asymmetry changes coefficients, not the number of observations; clipping
also makes different raw observations indistinguishable at the neural input.

The three HS states within each hemisphere are identical in this protocol.
The experiment does not resolve individual route necessity. Sham demonstrates
deterministic equivalence; disabling an unapplied readout demonstrates software
isolation, not locomotor causality or anatomical necessity. Model-update delays
are not measured biological latencies. Forward propulsion remains NOT_DEFINED.

Permanent regression tests now include independent mixed endpoint-bearing
calculations, independently specified rotation/translation equivalence, clipping
ambiguity, prescribed-pose isolation and rehashed contradictory metadata rejected
by the full artifact validator. Test-only analytical cases do not change the
twelve registered runs, preregistration, frozen kernels or existing artifact.

Results and the reproducibility command are recorded in
`planar_steering_shadow_assessment.md` after execution.
