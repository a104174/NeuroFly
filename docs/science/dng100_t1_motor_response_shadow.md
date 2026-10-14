# DNg100 T1 isolated counterfactual receiver response V0

## Method preflight and scientific scope

Experiment: `DNG100_T1_SINGLE_MOTOR_RESPONSE_SHADOW_V0`.
Initial main/local/remote: `4fd52eb1d47c6b67c3516dacda5fb598ee175618`, clean.
The question is temporal sensitivity of one assumed receiver to an immutable
recorded engineering input, not identification of motor-neuron physiology.

**Method preflight GO: engineering temporal-response experiment only.** A stable
one-state linear relaxation model has a closed-form solution for each held input
interval. It can falsify incorrect timing, sign handling, decay and provenance,
and quantify dependence of finite-window response descriptors on timescale.
It cannot identify the true equation or time constant of motor neuron 804257.
No result of this experiment will establish biological plausibility by itself.

The existing `g1_proxy_passive_electrical.py` computes exponential decay followed
by event-boundary increments in an explicitly uncalibrated virtual G1 domain.
Its token, voltage-proxy, parameter and anatomical mappings are inapplicable here.
`muscle_activation.py` is memoryless, rectified and tied to that domain. The TTM
receipt/actuator contracts address other identities and neither defines the
selected Ti-extensor receiver. Their kernels remain unchanged; only canonical
serialization/metadata and the validated input replay conventions are reused.

Primary mathematical context:

- [Pugliese et al., revised 2026 preprint](https://doi.org/10.1101/2025.09.12.675944),
  [pinned rate-equation code](https://raw.githubusercontent.com/smpuglie/Pugliese_2026/10e7661bf414ba7b4c2edf795cd36d0f878c17c0/src/simulation/vnc_sim.py):
  the published nonlinear rate equation contains first-order relaxation. This
  new receiver replaces its activation with a signed linear engineering input;
  it is neither a reproduction of that model nor a measured motor equation.
- Rotstein & Nadim, *Frequency preference in two-dimensional neural models: a
  linear analysis of the interaction between resonant and amplifying currents*,
  J Comput Neurosci 37:9–28 (2014), DOI
  [10.1007/s10827-013-0483-3](https://pubmed.ncbi.nlm.nih.gov/24254440/):
  the primary abstract documents amplitude/phase analysis of linearized models.
  This is context only. PMC full text was blocked and Europe PMC full-text
  retrieval returned HTTP 500 in this session. No equation, target correspondence
  or parameter is imported from inaccessible full text.

The adopted scalar equation and exact update are derived directly by integrating
factor; method integrity does not depend on unseen receptor or physiological data.
No cited resource supplies calibrated parameters or functional sign for 804257.

## Preregistered hypothesis and engineering parameters

Complete contract: `dng100_t1_motor_response_shadow_preregistration.json`.
Canonical identity:
`133ab02e77008fbf1720deaa40a746cbcbef6adef923271222023cecdbfff4b4`.
The contract was defined, hashed and captured before receiver trajectories.
No independently certified prospective timestamp is claimed. Nothing is retuned
from response outcomes, and all earlier preregistrations remain unchanged.

    tau * dy/dt = -y + gain * u(t)
    gain = 1; y(0) = 0
    y[n+1] = y[n] + (-expm1(-dt[n]/tau)) * (gain*u[n] - y[n])

The calculation is the analytic exact zero-order-hold update in floating point.
`expm1` avoids cancellation in small interval coefficients. State y is an
ENGINEERING_RECEIVER_STATE in uncalibrated input-model units, never voltage,
current, spikes, receptor activation, firing rate, muscle activation or force.
There is no threshold, saturation, rectification, plasticity, conduction delay,
noise or feedback. Negative inputs and states are retained.

The three timescales are 1, 10, 100 ms: three engineering decades based on the 1 ms
sampling interval, tau/dt=1,10,100. The largest tau leaves 20 response timescales
in 2 s and 10 in the final 1 s descriptor window. These are numerical design choices,
not physiology, and were not selected from the observed neural oscillation period.
Gain 1 is engineering normalization; structural count 23 is never a response weight.
The 2 s trace supports these declared finite-window comparisons, not asymptotic or
biological inference. All response properties are conditional on the input hold.

## Grounded identities and immutable input

MaleCNS v1.0 UUID: `4b2087c0fbe046bfaf0d60bc970e3e5d`.
Source 903216: INXXX466_R, T1. Target 804257: Ti extensor MN_R, T1, Traced/Reviewed.
The published authority verifies 903216→804257 with 23 structural synapses, all
assigned to LegNp(T1)(R). Its primary_outputs row 1544 and motor_inputs row 9592
agree, with canonical row hash:
`e5ff03ee94e0b46ba2827701c1533676b70af16f4d43000a7a29512002aacc6a`.
Motif authority:
`baae20599455c2a7acb3271e6eeb6b73326d17185b6e705022b74818ff0f8934`.
Scoped snapshot:
`def753409faa5daa7932ad5c256c644b2b426f44c053b2c40a5b89a17d6b024e`.
These are scoped identities, not complete-connectome checksums.

Parent motor-input shadow logical artifact:
`7f40609a28662d6b4f61e00e24b6aaed688322b4bbf716bda98bdaba5a93c988`.
Raw shadow.json:
`af6d2ee30cf45a9484d9f95a1c66d9d59705635fc7ca9924adf173e2780e94dc`.
The exact scalar parent replay validates complete structural/neural provenance.
The neural source remains the converged V1 artifact
`d0f441ad8e9ebdbf83812dcbf52e86326d76e093632dfe5cbe58607a48d525f8`,
raw SHA-256
`c6f95ae2b1300115492c6e8442867fd31ac47fabb8451bca2927c330595fbe1a`,
recorded RK4 trace 3.125e-05 (0.03125 ms integration), sampled every 1 ms.
Neither original neural experiment is regenerated or modified. No sinusoid or
invented spike train substitutes the scientific source.

The source is itself model-derived, conditional on hypothetical signs,
count-to-model-weight conversion and externally prescribed DNg100 drive. Its
finite recorded states are not measured firing. All fifteen original biological
signs, and the additional source→motor-target functional sign, remain UNKNOWN.

## Time semantics and controlled experiment

All 2001 original boundaries 0–2 s are preserved. Each input u[n] is held over
[t[n],t[n+1]). State y[n] is recorded before consuming u[n]. There are exactly
2000 completed intervals; u[2000] is recorded but has no outgoing interval.
The last outgoing_interval_input is null; the initial consumed-input step is
null. No interval beyond 2 s is manufactured, and no final state is forced to zero.

The parent supplies unchanged A positive, B negative, C route-off and D sham
inputs. All four are used at each timescale: 12 runs, 24,012 boundaries and 24,000
completed intervals. The source state/time stays identical across matched runs.
B is the exact signed opposite of A; C stays zero; D reproduces A exactly.
Route-off is a computational condition, not a lesion or anatomical ablation.

## Numerical reference and results

The independent reference sums all preceding held intervals directly:

    y(t_n) = exp(-t_n/tau)*y0
             + gain * sum(k<n) u[k] *
               (exp(-(t_n-t[k+1])/tau) - exp(-(t_n-t[k])/tau))

It uses independent exp evaluation and summation, not the production recurrence.
With zero initial state, linearity independently supplies the negative, zero and
sham references. All 24,012 boundary comparisons pass. Maximum absolute error is
1.4210854715202004e-14, below the preregistered 1e-10 allowance for floating-point
summation. This is exact agreement with the declared held-input model, not proof
of agreement with an unknown continuous physiological signal.

| Engineering tau | A maximum absolute state | A final state | A peak offset | Tail centered RMS ratio |
| --- | ---: | ---: | ---: | ---: |
| 1ms | 69.0129929911 | 28.7035872111 | 2ms | 0.9882798688 |
| 10ms | 48.5190017469 | 16.6336112859 | 9ms | 0.6685925920 |
| 100ms | 13.3693345749 | 10.9169801377 | 35ms | 0.0967892168 |

B has the opposite signed state and identical absolute metrics; D equals A;
C is identically zero. For C, attenuation ratio and input peak offset are
unavailable (null), not replaced with zero. The first absolute-maximum time
convention for a flat zero output is boundary 0; it is not a detected event.

Peak offset is the difference between the earliest global absolute output/input
peaks over the full window, including transients. It is not a unique periodic
phase delay or synaptic latency. Tail attenuation is centered RMS(output) divided
by centered RMS(input) over matched boundaries in [1,2] s. These observed descriptors
depend on the selected engineering timescale; no monotonicity or minimum response
threshold was introduced as a success criterion. The receiver is a stable forced
linear system: periodic input can yield periodic output without an endogenous
oscillator. No CPG, motor rhythm or physiological recruitment is inferred.

## Isolation, reproducibility and gates

Output: COUNTERFACTUAL_POSTSYNAPTIC_RESPONSE. Application: SHADOW_ONLY.
Physiological motor recruitment NOT_VALIDATED; motor spiking, molecular receptors,
muscle and body movement NOT_MODELLED; source feedback NONE. No motor plant,
membrane model or body state is instantiated. Tests forbid original neural solver
calls and check source immutability, exact field inventories and interval order.

    .venv/bin/python -m neurofly.dng100_t1_motor_response_shadow generate
    .venv/bin/python -m neurofly.dng100_t1_motor_response_shadow replay --path <external-root>/<artifact-id>

The default output is the external sibling scientific-work directory. Generation
refuses repository output and overwrite; atomic publication writes response.json
and its manifest. Replay validates genuine parent sources and regenerates only
this isolated engineering receiver. Complete recoverable configurations and
telemetry are recorded; a compact reference commits identities and summaries,
not large trajectories. Logical artifact/config/result hashes differ from the
raw file checksum. Rehashed contradictory metadata or states must be rejected.

Forty focused tests pass, including independent exponential/constant/piecewise
references, signed states, initial conditions, interval boundaries, extreme
engineering timescales, invalid inputs, deterministic controls and integrity.
**Full canonical Python regression: 1625 passed, 1 deselected under the existing
integration policy, 2 existing dependency-deprecation warnings; exit 0, 962.94 s.**
Ruff check, format check and diff/whitespace gates pass. The genuine parent input
shadow replay passes exactly, without neural regeneration. Original V0/V1 raw,
configuration and numerical-metric identities are unchanged; their preserved
complete semantic replay evidence remains verified. Route/motif/NT/postsynaptic
UNKNOWN, Planar SHADOW_ONLY exact semantic reproduction, all five canonical
playback hashes and VALIDATED_CANONICAL_REPLAY provenance pass. D2.2 strict
archive verification and all 74 authorized runtime member hashes pass.
Real-source altered states and physiological-recruitment claims with recalculated
hashes are rejected. External logs/scripts and complete identities are recorded
in the compact reference. No original scientific kernel, API, frontend, dataset
or provider configuration is modified.

**SCIENTIFIC_MOTOR_RESPONSE_SHADOW_PUBLICATION_GO** for one focused source commit,
limited to the isolated counterfactual receiver and its interpretation. There is
no positive biological recruitment, receptor or motor-actuation conclusion.

## One smallest subsequent experiment

A separately preregistered held-input reconstruction sensitivity experiment could
compare this ZOH assumption with a declared piecewise-linear reconstruction of
the same immutable boundary samples, keeping receiver equations, timescales and
controls fixed. Independent constant/ramp solutions would validate each method.
It would quantify which temporal conclusions depend on the input reconstruction,
without claiming new recorded neural samples or target physiology. No muscle,
spikes, body feedback or movement belongs in that next experiment. It is a
proposal only and is not implemented here.
