# DNg100 T1 sign-uncertainty dynamics V0

## Decision

**DNG100_T1_DYNAMICS_NUMERIC_ONLY**; scientific result
**RHYTHM_RESULT_INCONCLUSIVE**. Method and mathematical tests pass, and the
275-run artifact reproduces exactly. However, one of 90 paired timestep checks
exceeds the preregistered trajectory-error tolerance. Gate B is therefore
partial, not fully passed. Publication is withheld. No threshold, parameter,
step size or outcome definition was changed after inspecting the sweep.

This is a counterfactual rate-model experiment. All fifteen biological
connection signs remain UNKNOWN. There is no validated CPG, motor command,
walking, body feedback or physical propulsion.

Initial main/remote main: a5d6eba840486439de847138133ad17ffc59c0a2; worktree
clean. No existing tracked file was edited. The new scientific files remain
local and unstaged pending resolution of the numerical gate.

## Method authority and reduced-model differences

Primary publication: Pugliese et al., *Connectome simulations identify a central
pattern generator circuit for fly walking*, revised 30 April 2026 preprint,
DOI [10.1101/2025.09.12.675944](https://doi.org/10.1101/2025.09.12.675944).
[Retrieved full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13142387/fullTextXML)
SHA-256: 8601d675a0284d631dfbd65bae9e834c3332e0f11808b81a5136ff2d75078143.

[Research code](https://github.com/smpuglie/Pugliese_2026/tree/10e7661bf414ba7b4c2edf795cd36d0f878c17c0)
was read at commit 10e7661bf414ba7b4c2edf795cd36d0f878c17c0.
The preregistration records immutable URLs and raw hashes for the ODE,
connectivity/size utilities and neuron/simulation/input configurations.
No external code, dataset or JAX dependency is incorporated into NeuroFly.

The source uses rectified half-tanh rate dynamics, adaptive Dopri5, randomly
sampled cell parameters and relative-cell-size scaling. Synaptic signs are
assigned from transmitter predictions; that rule is not physiology. The source
configuration includes autocorrelation-based oscillation scoring and a 0.5
screen threshold. Our engineering detector is separately specified, not a
replication of that score. Behavioral descending-neuron activation does not
measure the selected motif's postsynaptic signs.

This experiment retains the rate equation and central parameter values but
uses six MaleCNS T1 interneurons, uniform deterministic parameters, fixed-step
float64 RK4 and prescribed DNg100 source states. It omits size normalization,
the broader VNC network, motor neurons, parameter randomness and biology-based
actuation. Invalid numerical states terminate explicitly rather than being
replaced by zero or silently clipped.

## Preregistered equations and configuration

The complete contract is `dng100_t1_dynamics_preregistration.json`, canonical
identity 80e57ffdc0756c1afdbd57db6d066bc4e99b250dcd9ec1a9b112494be5a59a2b.
It was written before the scientific sweep; no independently verified
prospective timestamp is claimed.

For model rate R_i:

    tau * dR_i/dt = max(200*tanh((a/200)*(sum_j W_ij*R_j
                         + sum_d B_id*D_d(t) - theta)),0) - R_i
    W_ij = b * count(pre=j,post=i) * hypothetical_source_sign(j)

Matrices use row=post, column=pre. B uses exactly the three DNg100 input edges.
Raw counts remain recorded unchanged; b converts them to counterfactual model
weights, not measured efficacies. There is no count normalization or conduction
delay. Parameters: a=1, theta=7.5, cap=200 source-model rate units. These units
are Hz in the source formulation but not calibrated firing rates of these cells.

Five parameter points were fixed: (b,tau_s)=(.03,.020), (.015,.020),
(.06,.020), (.03,.018), (.03,.022). The source central weight multiplier is.03;
factor-two weight changes are engineering sensitivity. Tau endpoints are the
source mean +/- one parameter-distribution SD, not measured confidence bounds.
Gain, threshold and cap uncertainties remain; they were not exhaustively swept.

| Hypothesis | E1 sources | E2 sources | I1 sources | DNg100 sources |
| --- | ---: | ---: | ---: | ---: |
| A published-like | +1 | +1 | -1 | +1 |
| B alternative I1 | +1 | +1 | +1 | +1 |
| C I1 feedback zero | +1 | +1 | 0 | +1 |
| D E1 alternative | -1 | +1 | -1 | +1 |
| D E2 alternative | +1 | -1 | -1 | +1 |
| D source alternative | +1 | +1 | -1 | -1 |

Every assignment is COUNTERFACTUAL_MODEL_ASSUMPTION. Source grouping does not
identify independent signs on all 15 edges. C is an in-silico contribution
removal, not a biological ablation. Negative DNg100 interaction is also only a
counterfactual, despite its presynaptic acetylcholine evidence.

Prescribed sources are20 model-rate units each (0.1of cap) during active input;
this is an engineering amplitude, not a physiological fit or a brain-generated
DNg100 response. Schedules are zero, constant [.02,2)s and pulse [.02,.5)s.
No periodic input is applied. Source-off uses zero source activity; sham repeats
the intact constant condition. Feedback-disabled retains source input but zeros
all recurrent model weights.

Duration2s; output every1ms; RK4 integration.25ms and paired.125ms refinement.
Each integration interval holds its old-boundary input while all six states
update simultaneously. Initial states are zero; a uniform2-unit perturbation
is tested separately for every primary configuration. Both interval and boundary
source states are recorded. At2s, constant boundary input has been withdrawn;
fixed-point residual uses the last completed interval's drive (the2s left
limit). Finer RK4 stages are integration operations, not additional experimental
measurements; they are recoverable by deterministic replay.

## Structural/evidence identities

MaleCNS v1.0 UUID4b2087c0fbe046bfaf0d60bc970e3e5d.
L ordered states:800173/IN17A001,800863/INXXX466,801884/IN16B036.
R:800288/IN17A001,903216/INXXX466,803183/IN16B036.
DNg100 L10045, R10056. All IDs/types/sides and15 directed edges are verified
through the frozen NT authority, which semantically validates source structure.
No cross-side recurrent connection is fabricated; the two recurrent blocks are
independent. Common prescribed drive is not evidence of interhemispheric coupling.

| Source | Identity |
| --- | --- |
| Annotation raw SHA | 2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2 |
| Recurrent scoped snapshot SHA | def753409faa5daa7932ad5c256c644b2b426f44c053b2c40a5b89a17d6b024e |
| Recurrent logical artifact | baae20599455c2a7acb3271e6eeb6b73326d17185b6e705022b74818ff0f8934 |
| NT source SHA | 95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621 |
| NT logical artifact | 38dc667d74acc3c6691b95659f38a1beab2f6208b5c592341f024f61d31bc526 |
| Postsynaptic evidence review | 4c29057f3a069e26ac5604754c304408c48bc511a564c3dc5595e7ac305cacf9 |

The complete edge records, counts, ROIs and recoverable source references are
embedded in the preregistration. Input counts are10045->800288:100;
10056->800173:155;10056->800863:1. L/R asymmetries, including I1->E1 counts
526/439, remain intact. These scoped identities are not full-connectome checksums.

## Outcome rules and observed results

The final1s window must have at least five complete cycles, periods10–200ms,
period CV<=.1, late/early tail-half amplitude ratio.8–1.25, peak-bin-plus-adjacent
spectral fraction>=.6 and period-lag correlation>=.7. Amplitude floor1e-4
is a numerical threshold, not a minimum biological rhythm. All requirements apply
to a cell; any qualifying cell supplies the network/side numerical label.
Other cells may fail a criterion even if the side qualifies. Stable fixed point
requires small tail amplitudes and residual<=.01; TRANSIENT uses the declared
relative-decay criterion. Nonqualifying activity is INCONCLUSIVE. Nonfinite or
out-of-invariant-range solutions are NUMERICAL_DIVERGENCE. These finite-window
labels cannot establish eventual asymptotic behavior or rhythms outside the band.

| Primary hypothesis, five parameter points each | Zero input | Constant input | Pulse then withdrawal |
| --- | --- | --- | --- |
| A | 5 fixed | 5 oscillation candidates | 5 fixed |
| B | 5 fixed | 5 fixed | 5 fixed |
| C | 5 fixed | 5 fixed | 4 fixed,1 transient |
| D E1 | 5 fixed | 5 fixed | 5 fixed |
| D E2 | 5 fixed | 5 fixed | 5 fixed |
| D source | 5 fixed | 5 fixed | 5 fixed |

Across all 275 runs:256 fixed-point classifications,16 oscillation candidates,
3 transients and zero divergences. Fifteen candidates are A/constant across
primary/refined/initial-state roles; the additional candidate is matched sham.
These counts describe detector labels, not fully accepted robust rhythms.

Matching classification does not mean matching states: at central B/zero input,
zero initial rates remain silent, whereas the declared uniform2-unit initial
perturbation reaches a high nonzero fixed-point candidate (E1/E2 approximately
200 units by2s). This is finite-window model initial-condition sensitivity,
not evidence of biological autonomy or global stability.

At central A/constant, L E1 has tail amplitude8.716762 and period68.071429ms;
R E1 amplitude9.270379 and period68.928571ms. Fourteen complete cycles per
cell are detected; period CV~.0038 and lag correlation~.9999. The sides differ
according to retained structure. Central A/pulse relaxes to zero after withdrawal.
B/pulse retains a nonzero fixed point, demonstrating that sustained activity
need not be oscillatory. C/pulse at the central point retains nonzero L activity
but R relaxes to zero. Thus a fixed-point label is not equivalent to silence.

Sham telemetry/metrics are exactly identical to the matching primary run.
Source-off and all feedback-disabled controls reach fixed points. All 90
initial perturbations preserve their matching primary classification; this does
not prove global independence from arbitrary initial states.

### Unresolved refinement gate

Preregistered maximum trajectory difference is.001*cap=.200 units; rhythm
period/amplitude relative tolerances are5%, with classification agreement also
required. **89/90 paired configurations meet the full criterion.**
A/constant/double_weight (b=.06,tau=.02) has max error.28221829111123853.
Both step sizes still yield the same detector classification, but that does not
waive the trajectory criterion. No parameter tuning or additional post-hoc
refinement is folded into V0. The aggregate result stays
RHYTHM_RESULT_INCONCLUSIVE, and this failed numerical criterion prevents a
fully validated sensitivity/publication claim.

## Reproduction and validation

Artifact logical identity:
f73fe0f167f5ef2a2a90c4142017f39ee4b9138ecf7ab5347395d79f13fabfb4.
Config SHA:a938c56f7eeb7339f69cf29d93d8b495540fc78d6ab9855d9d1d9afda6676e18.
Result SHA:ec37fee0a6097d98f94560a3e17986872e7ac0ecb1a23c585385c3a13ea5f225.
The small reference manifest distinguishes these logical hashes from raw bytes.
Full telemetry is58,193,411bytes, stored outside Git in a content-addressed
scientific-work directory. It contains275x2001 sampled six-state boundaries,
source rates, matrices, metrics, complete configuration and software identities.
No large run file or upstream source enters Git.

With genuine pinned local authorities available:

```bash
.venv/bin/python -m neurofly.dng100_t1_dynamics_sensitivity generate --path <NEW_EXTERNAL_OUTPUT_ROOT>
.venv/bin/python -m neurofly.dng100_t1_dynamics_sensitivity replay --path <EXTERNAL_OUTPUT_ROOT>/f73fe0f167f5ef2a2a90c4142017f39ee4b9138ecf7ab5347395d79f13fabfb4
```

Generation refuses existing output identities. Replay checks canonical bytes,
manifest, current implementation/parameter identities, full configuration/run
inventory, all 275 re-integrated traces/metrics and the recomputed summary.
All275 reproduced exactly, including the unresolved timestep result.

Thirty focused tests cover independent exponential decay (fourth-order
convergence), closed-form constant/pulse response, sign/orientation, genuine
source edges, invalid policy/configuration, sham separation, numerical failure,
sine-wave detection, decaying/isolated transient rejection and contradictory
rehash metadata. A sine-reference failure exposed tied sampled peaks; the
plateau detector was corrected before any scientific sweep, without changing
the reference or preregistered thresholds. Deterministic replay is not an
independent biological validation; analytic tests address numerical code only.

Published route/motif/NT and postsynaptic evidence validators pass. Planar
SHADOW_ONLY semantic reproduction and its original raw checksum pass. All five
canonical playback hashes and VALIDATED_CANONICAL_REPLAY provenance match.
The D2.2 archive, manifest and inventory verify unchanged. The recovered full Python suite completed successfully: **1516 passed, 1
deselected, 2 dependency-deprecation warnings**, in 1076.43 seconds; its process
exit status was 0. Source/module hashes and unchanged test-file modification
times agree with the completed execution. The suite was not rerun. Current
Ruff check and format check pass, as does the tracked diff check. Since all six
new files are untracked, an additional direct trailing-whitespace/EOF check
is used without staging. No existing kernel,
scientific API, frontend or provider configuration is changed.

## Resume validation and POST-HOC DIAGNOSTICS

The initial reported preregistration identity is
13e9b2da6c2acf23201ac944fd651f6c4ba24413e615f8c07249e2c34cc37bb2.
The adopted identity is80e57ffdc0756c1afdbd57db6d066bc4e99b250dcd9ec1a9b112494be5a59a2b.
Their sole difference is `metrics.residual_time_semantics`, added before model
implementation and the sweep to specify the final input left-limit. No tolerance,
parameter, equation, hypothesis or run grid changed. Removing that field recovers
the initial identity exactly. The small reference now preserves its complete
initial definition, the adopted file reference and the explicit difference,
so both definitions are recoverable beyond temporary storage. This does not
establish independently verified prospective chronology.

The failed comparison's complete condition is A_PUBLISHED_LIKE / double_weight /
constant / primary, b=.06, tau=.02, zero initial rates, prescribed20-unit bilateral
DNg100 rates on [.02,2)s. Integration steps are.00025 and.000125s; output grids,
source telemetry, W/B matrices and initial states match exactly. Independent
array subtraction reproduces the preregistered maximum absolute difference over
all sampled times and six components: **.28221829111123853**, at **t=1.922s**,
**body903216 (right INXXX466)**. Coarse state13.96653208362032 versus refined
13.684313792509082. The criterion is unchanged at.200.

| Component | Maximum sampled absolute difference |
| ---: | ---: |
| 800173 | .0501127099095493 |
| 800863 | .16460106923063478 |
| 801884 | .05736850178013597 |
| 800288 | .08546300430060327 |
| 903216 | .28221829111123853 |
| 803183 | .09624677149457916 |

A **post-hoc diagnostic only** searched interpolation shifts from-200 to+200
microseconds in1-microsecond increments, minimizing squared discrepancy across
each side's three states over1.5–1.999s. Best shifts were+11microseconds L and
+54microseconds R. L RMS fell from.0146731484 to.0105120483; R from.0463910492
to.0103923400. This supports a substantial accumulated phase component, not proof
that all error is pure phase. No shift is applied to primary data, criteria or
classification. The right E2 detected period agrees at.06914285714285714s;
its amplitude-relative difference is.0003035136547331341. Those agreements do
not waive the trajectory-error criterion.

The implementation uses ordinary simultaneous RK4 with correctly aligned held
inputs. Independent decay and closed-form input tests already passed. Stronger
recurrent weights increase numerical sensitivity; rectification is nonsmooth at
threshold, so smooth-system fourth-order error behavior need not hold at every
crossing. These are plausible mechanisms, not a proven exclusive explanation.
No timing, indexing or update defect was demonstrated; no code was changed on
resume. Without an independently converged reference, the exact trajectory-error
mechanism and absolute accuracy remain unresolved.

All275 runs are complete, each with2001 ordered sampled boundaries; configurations,
implementation hashes, raw file checksum and the prior completed exact semantic
replay agree. The resumed checks reuse those valid results rather than rerunning
the sweep. Two post-hoc negative controls alter an initial state or body-actuation
metadata **in memory** and recompute hashes. Both are rejected by semantic/config
validation. The original artifact is unchanged. Logs and diagnostic definitions
are preserved in external `validation-evidence`, with recoverable content hashes
in the small reference manifest; no bulk telemetry is added to Git.

Raw dynamics.json SHA-256:
04623387c16c36ddff45d94d1e25b7935d52ca66951d29d6e89e21b4be3aa65c.
The logical artifact/config/result identities above remain unchanged.

**Publication NO-GO:** the original numerical gate requires refinement acceptance;
89/90 is not full acceptance. The preregistration classifies the aggregate result
as inconclusive but does not explicitly authorize bypassing a failed numerical
acceptance criterion. Valid software, exact reproduction and an honest inconclusive
finding are distinct from passing that gate. No commit, push, branch, tag,
deployment or provider operation is performed. Work remains local and unstaged.

## One smallest next slice

A **separately preregistered single-condition timestep-convergence V1** for
A/constant/b=.06/tau=.02, retaining exact graph, signs, input, initial state,
duration and outcome thresholds. Compare a declared finer-step sequence against
an independently implemented numerical reference, quantify phase/trajectory
error and retain an unresolved outcome if convergence fails. Do not reclassify
V0 retrospectively or tune the circuit for oscillations. First resolve this
numerical gate; no motor/body feedback or biological-sign claim follows even
if it passes. Receptor/paired physiological evidence remains necessary for
biological interpretation.
