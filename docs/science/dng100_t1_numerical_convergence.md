# DNg100 T1 numerical convergence V1

## Numerical decision and scope

**DNG100_T1_CONVERGENCE_VERIFIED** for exactly the selected counterfactual
configuration over the declared 2 s observation window. This is numerical
agreement of the reduced model, not biological sign authority or a validated CPG.

Original V0 results remain **DNG100_T1_DYNAMICS_NUMERIC_ONLY** and
**RHYTHM_RESULT_INCONCLUSIVE**. Its failed 0.200 criterion and historical
publication NO-GO are unchanged. The new V1 scope permits publication of these
historical source files together with a separately validated convergence result;
it does not retrospectively reverse V0's outcome.

Baseline main/remote main: a5d6eba840486439de847138133ad17ffc59c0a2, with the
six expected untracked, unstaged V0 files and no unrelated changes. All six were
hashed before V1 work and are preserved byte-for-byte. No original grid was rerun.

## Prospective V1 contract

`dng100_t1_convergence_preregistration.json` was defined before calculating any
new finer-step or reference trajectory. Canonical identity:
ab20411d2abd16d728b3b5eacb3d94c2fe01da772f0056acc955640e8f285254.
No independently certified prospective chronology is claimed. V1 is informed by
the known V0 failure; its new numerical results were not used to choose thresholds.

Target: double_weight / A_PUBLISHED_LIKE / constant / primary; b=0.06,
tau=0.02 s, gain=1, threshold=7.5, cap=200, zero initial states. Ordered MaleCNS
T1 states are L[800173,800863,801884] and R[800288,903216,803183]. DNg100 sources
are [10045,10056], externally prescribed at 20 model-rate units on [0.02,2) s.
All fifteen biological signs remain UNKNOWN. E1/E2/DNg100 positive and I1
negative interactions are COUNTERFACTUAL_MODEL_ASSUMPTION.

The unchanged model is:

    dR_i/dt = (max(200*tanh((sum_j W_ij*R_j + sum_d B_id*D_d - 7.5)/200),0)
               - R_i) / 0.02
    W_ij = 0.06 * structural_count(pre=j,post=i) * hypothetical_source_sign(j)

Rows are postsynaptic, columns presynaptic. The fifteen directed structural
records, weights and L/R asymmetries are retained; no normalization, missing
connection, delay or biological parameter is introduced. Independent matrix
reconstruction agrees exactly with the stored V0 matrices.

The adopted V0 formulation is a restricted deterministic six-cell model derived
from the half-tanh formulation documented by
[Pugliese et al., revised preprint](https://doi.org/10.1101/2025.09.12.675944)
and [research code](https://github.com/smpuglie/Pugliese_2026/tree/10e7661bf414ba7b4c2edf795cd36d0f878c17c0).
It is not reproduction of their full VNC simulations, size-scaled/random cell
parameters or biological experiments. V1 changes neither that model nor its gains.

## Independent numerical reference

SciPy **1.18.1 was already installed**; no dependency was installed or upgraded.
The reference uses adaptive DOP853 with its seventh-order dense interpolant.
The [official solver documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)
served version 1.18.0; the actual installed patch version and hashes of
`rk.py`, `ivp.py` and `dop853_coefficients.py` are pinned separately.

| Reference | rtol | atol | Maximum step |
| --- | ---: | ---: | ---: |
| Standard | 1e-10 | 1e-12 | 0.250 ms |
| Tight | 1e-12 | 1e-14 | 0.125 ms |

The reference RHS uses scalar accumulation and math.tanh independently of the
production NumPy derivative and RK4 kernel. Literal hand-checks and selected
real-source states, including zero and capped states, agree. Analytical tests
independently verify exponential decay, a coupled sine/cosine system and a
piecewise driven first-order response. A different solver alone is not proof
of correctness; these checks and the tighter-reference comparison are required.

Separate adaptive solves cover [0,0.02] and [0.02,2], carrying the continuous
endpoint state. Input is held within each interval. Dense interpolation is
restricted to its corresponding solve and never crosses the input discontinuity.
At t=2, state is continuous although the declared boundary input is withdrawn.
All comparisons use exactly the original 2001 timestamps, 0–2 s every 1 ms.
No missing, unordered or non-finite samples are accepted.

Existing RK4 steps 0.250/0.125 ms are **reused recorded V0 trajectories**.
Only 0.0625/0.03125 ms are newly integrated with the unchanged production kernel.
No changes to input, initial state, duration, weights or signs are made.

## Preregistered acceptance

Reference disagreement must be <=0.002 maximum and <=0.0005 RMS. These are
corroborative numerical requirements, not rigorous mathematical error bounds.
Both new fine steps must have <=0.050 maximum and <=0.010 RMS error against the
tight reference. The maximum limit is one quarter of the original 0.200 limit;
it does not relax V0. Errors must decrease with refinement, allowing only 0.002
reference-scale slack, and the two new steps must differ by <=0.200.

Final-1-s period and amplitude relative differences must be <=1%, with mean
state differences <=0.050. The unchanged V0 detector supplies cycle count,
persistence, spectral and recurrence checks. Both sides must have a qualifying
cell and detector masks must agree between both references and both fine steps.
Not every cell has to qualify: E1 traces do not meet the spectral criterion here.
Peak-derived periods have 1-ms sampling quantization; agreement is not a claim
of exactly equal continuous-time periods.

Phase interpolation is a prospectively declared **secondary diagnostic**, not
an acceptance metric. It cannot repair raw trajectory disagreement.

## Pointwise results

| RK4 step | Maximum error vs tight reference | RMS error | Worst cell | Time |
| ---: | ---: | ---: | ---: | ---: |
| 0.250 ms, reused | 0.2975289128 | 0.0212654121 | 903216 | 1.991 s |
| 0.125 ms, reused | 0.0700637902 | 0.0057731926 | 903216 | 0.816 s |
| 0.0625 ms, new | 0.0084168463 | 0.0008295220 | 800863 | 1.167 s |
| 0.03125 ms, new | 0.0029103176 | 0.0002920515 | 800863 | 1.236 s |

Standard/tight DOP853 difference: max **0.000031422862161178955**, RMS
**0.0000021175710652743656**. Both reference criteria pass. The new RK4 pair
has max difference **0.011324447389538861**, RMS **0.0008947063791592992**.
All new pointwise and refinement criteria pass, without phase alignment.

Maximum errors decrease monotonically. Their ratios do not establish a uniform
fourth-order global convergence law for this nonlinear rectified oscillator.
Threshold nonsmoothness and accumulated phase error remain plausible influences;
no single mechanism is asserted as exclusively responsible.

### Original V0 failure remains

Reused V0 pair: max **0.28221829111123853**, tolerance **0.200**, at 1.922 s,
903216/right INXXX466. States: 13.96653208362032 and 13.684313792509082.
The discrepancy is independently recovered from the original recorded arrays.
V1 does not shift those arrays, change the tolerance or update the V0 classification.

## Oscillation properties

Tight-reference representative qualifying cells:

| Cell | Final-1-s amplitude | Mean | Period | Complete cycles |
| ---: | ---: | ---: | ---: | ---: |
| 800863, L INXXX466 | 26.3509718318 | 9.7054467347 | 69.230769 ms | 13 |
| 903216, R INXXX466 | 27.3457486407 | 11.1019299735 | 69.142857 ms | 14 |

For 0.0625 ms, maximum relative amplitude difference across six cells is
0.0000300883 and maximum mean difference 0.0000562611. For 0.03125 ms those
are 0.0000088768 and 0.0000132994. Sampled peak-derived period differences are
zero at their recorded resolution. All property thresholds and sustained masks
agree; E2/I1 qualify bilaterally. The full result records each cell's amplitude,
mean, period, CV, cycle count, persistence, spectrum and autocorrelation.

This supports a numerically converged, sustained periodic model response during
constant input for this one configuration and finite window. It is not proof of
an asymptotic limit cycle, all-initial-state stability, parameter/sign robustness,
biological rhythmicity, walking or propulsion. Source activation is prescribed,
not generated autonomously by a brain model. Receptor/sign uncertainty is intact.

The optional per-side lag/RMS diagnostics are stored separately. Unlike the V0
post-hoc investigation, this V1 secondary diagnostic was specified before the
new reference/fine runs. Neither diagnostic affects raw acceptance.

## Artifacts and reproducibility

Original logical artifact:
f73fe0f167f5ef2a2a90c4142017f39ee4b9138ecf7ab5347395d79f13fabfb4.
Original raw dynamics.json SHA:
04623387c16c36ddff45d94d1e25b7935d52ca66951d29d6e89e21b4be3aa65c.
All six V0 file hashes are embedded in the V1 policy and checked on every load.
The previously completed 275-run semantic replay remains valid; it is not repeated.
Current source/config, raw bytes and inventory checks agree with that preserved
artifact. Both V0 UNKNOWN authorities and scientific interpretation remain frozen.

New logical artifact:
d0f441ad8e9ebdbf83812dcbf52e86326d76e093632dfe5cbe58607a48d525f8.
Config SHA: 8399d8f9f222128d49b7b8acc2ba0022ea626a574253c90b253af8e05e2adb36.
Result SHA: 90cb7d3dfc2c6f4ace3b34065a371a7796a5cbd9f3936868e1c5349d1dcb2e81.
The new external artifact contains six sampled trajectories (two reused, two
references, two fine), complete model/source/software configuration and all
numerical metrics. No bulk trajectory or upstream scientific dataset enters Git.
Logical identities are distinct from raw checksums in the small reference manifest.

```bash
.venv/bin/python -m neurofly.dng100_t1_numerical_convergence generate --path <NEW_EXTERNAL_ROOT>
.venv/bin/python -m neurofly.dng100_t1_numerical_convergence replay --path <EXTERNAL_ROOT>/d0f441ad8e9ebdbf83812dcbf52e86326d76e093632dfe5cbe58607a48d525f8
```

Reproduction requires the recorded scientific environment and genuine pinned
local authorities; unavailable/mismatched SciPy fails explicitly. Generation
refuses to overwrite prior outputs. Replay checks canonical bytes/manifest,
original source identities, full configuration and exact regeneration of only
the four new solves and their metrics; it never repeats the 275-run grid.

## Validation/publication checkpoint

Twenty-two focused tests cover analytical reference systems, real structural
identity/RHS, timing, raw/phase separation, mismatched samples, deterministic
refinement, nonconvergent toy signals and rehashed contradictory metadata.
Synthetic mathematical signals are confined to tests and never substitute the
real MaleCNS input or the reference trajectories.

The targeted method and V1 numerical criteria pass. Exact V1 semantic replay
passes. The full canonical Python suite passed **1538 tests**, with 1 deselected
and 2 existing dependency-deprecation warnings, in 972.37 seconds. Ruff check,
format check and diff/whitespace checks pass. Route/motif/NT/postsynaptic UNKNOWN,
Planar SHADOW_ONLY, all five canonical hashes/provenance and D2.2 verify unchanged.
An in-memory altered trajectory with recomputed hashes is rejected. The full
275-run grid is not repeated.

**SCIENTIFIC_CONVERGENCE_PUBLICATION_GO** for one combined scientific source
commit under the V1 authorization. The original six files remain byte-identical;
their historical V0 numerical failure, outcomes and NO-GO assessment are preserved.
No positive biological or locomotor claim follows. The compact V1 reference
records solver, source and result identities, metric tables and validation evidence.
Only source/tests/policies/reports/references enter Git; all trajectory artifacts
and upstream data remain external. No V0 decision is overwritten.

One smallest next step is scientific review of the combined V0/V1 model-assumption
and numerical evidence before authorizing any further experiment. Numerical
convergence supplies no motor-actuation permission or biological sign resolution.
