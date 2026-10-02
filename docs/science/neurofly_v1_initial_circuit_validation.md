# NeuroFly v1 — Initial Connectome-Based Circuit Validation

## Scientific freeze and authority

Phase 23 closes the initial selected-circuit milestone. The authoritative
[scientific-status manifest](neurofly_v1_scientific_status.json) has schema
`neurofly_v1_scientific_status_v1` and canonical status ID
`1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6`.
Its ID hashes the inner `status` object, using the repository's canonical JSON
serialization: sorted keys, ASCII escapes, compact separators, finite numbers,
UTF-8 and SHA-256. The enclosing ID is excluded from its own hash. Formatting
the document does not change its semantic identity. This is scientific
governance, not a simulation artifact or runtime dependency.

**Freeze means stable for reproducibility, not biologically validated.**
The baseline is committed `e233b8f447f64d9c4040266dc812a959d0691ad4`:
clean `main == origin/main`, with Phase 22/21/20/19/18/17, corrected 16,
15 and 13B committed. No model, scientific parameter, scenario, historical
artifact, frontend behavior or source dataset is changed by this closure.

Completion decision: `NEUROFLY_V1_INITIAL_CIRCUIT_VALIDATION_COMPLETE`.
This is neither whole-fly emulation nor a complete biological escape model.

## What has actually been demonstrated

MaleCNS identities and structural routing support a selected LC4/LPLC2→DNp01
circuit. All 311 sensory identities (126 LC4 and 185 LPLC2) and two DNp01
point-neuron states execute deterministically. Ordered identity-resolved
contributions feed the existing model dynamics; genuine model spikes alone
are eligible to enter the composed downstream pathway.

The backend closes the causal loop:

`world/body → relative geometry → exposure → sensory state → DNp01 → TTMn →
output/dispatch/receipt → electrical proxy → activation → actuator → body →
next relative geometry`.

At boundary n, available spikes propagate downstream at n. Sensory state
`s[n]` drives the DNp01 interval update while exposure `e[n]` updates
`s[n+1]`. Commands at n drive body interval n→n+1. Object state advances by
its prescribed velocity. The next projection reads the updated authoritative
body and object, never a frontend transform. No outgoing interval follows the
final boundary. Initial exposure first affects membrane state at boundary 2.

The null canonical outcomes do not demonstrate realized movement-dependent
sensory change. They demonstrate successful causal execution and feedback
**wiring**. Test-only noncanonical cases independently exercise nonzero
downstream propagation and body-position-sensitive projection; they are not
canonical scientific results. Closed-loop completion and body movement are
separate statuses.

## Empirical structure versus model assumptions

| Component | Empirical/structural authority | NeuroFly assumption or limitation |
| --- | --- | --- |
| Identities and types | MaleCNS body IDs and annotations | Selected circuit, not whole connectome |
| Sides | Source-side annotations | Ipsilateral model routing follows audited identities |
| Connectivity | Directed structural edges/topology | Structural presence does not establish dynamic efficacy |
| Contact counts | MaleCNS `ConnectsTo.weight` structural count | Routing metadata only; never physiological gain, conductance or probability |
| Relative-column topology | Source column associations | No verified absolute world-bearing→retinal registration |
| World→column projection | No calibrated biological transform | Fixed R / hex(23,9); `floor(10*atan2(radius,distance))` |
| Exposure | Existing source-column disk overlap | Fractional model exposure, not measured photoreceptor input |
| Sensory state | Identity-resolved LC4/LPLC2 membership | Dimensionless x, gain 1, tau 1 ms, zero reset; not calcium, spikes or voltage |
| Sensory→DNp01 transfer | Structural route existence | Shared k=1; unnormalized additive model-space drive |
| DNp01 LIF | DNp01 identities 10001/R and 10010/L | Pinned membrane/reset/refractory dynamics; rest −52, threshold −45 mV_eq, tau_m 20 ms |
| Motor pathway | Audited DNp01/TTMn identities and structural routes | Event integrator and output threshold are exploratory abstractions |
| Muscle target | Qualified TTM-class association | Not exact peripheral fiber tracing or empirical G1 assignment |
| Electrical/G1 proxy | Explicit observation/mapping reviews | Distinct 800146/R and 804642/L passive proxy states, uncalibrated |
| Activation | No established physiological operator | Static normalized proxy mapping, not measured contraction |
| Actuator | Side-preserving model channel association | Dimensionless command, not force |
| Body plant | No validated biomechanical mapping | Common-mode planar kinematics, fixed +Z |
| World geometry/trajectory | No physical length/velocity calibration | Deterministic `world_eq` object and body state |

### Frozen transfer and normalization

`d_i[n] = active_i × k × x_i[n]`,
`D_j[n] = Σ d_i[n]` over the canonically ordered identities structurally routed
to target j; `k = 1.0 mV_eq/state`.

`active_i` denotes source selection, not a structural-count multiplier.
LC4 and LPLC2 share this coefficient; per-body state and exposure need not be
equal. There is no population/type normalization. Both state magnitude and
active population cardinality affect aggregate drive. Expansion to materially
different sensory populations therefore requires explicit contract review.

Classification: `EXPLORATORY_UNCALIBRATED_MODEL_ASSUMPTION`.
Phase 19 retains the contract as internally coherent and reproducible, with
`CURRENT_NORMALIZATION_ACCEPTABLE_EXPLORATORY_ASSUMPTION` and
`EQUAL_TRANSFER_MAGNITUDE_ACCEPTABLE_SIMPLIFICATION`. Magnitude is
`QUALITATIVELY_CONSTRAINED_BUT_NOT_NUMERICALLY_IDENTIFIABLE`.
None of these findings validates equal biological per-body efficacy or k=1.

## Canonical scenarios and honest null results

| Quantity | Baseline Control | Looming Circuit Validation | Looming World Experiment |
| --- | --- | --- | --- |
| Role | Explicit zero-stimulus control | Bounded causal micro-window | Preregistered exploratory model-space world experiment |
| dt / intervals / boundaries | 0.1 ms / 14 / 15 | 0.1 ms / 14 / 15 | 0.1 ms / 400 / 401 |
| Scientific horizon | 1.4 ms | 1.4 ms | 40 ms |
| Object | Absent; active set empty | Radius 1, z=4→2.6 | Radius 1, z=4→2 |
| Object vz | Not applicable | −1 world_eq/ms | −0.05 world_eq/ms |
| Projection radius | Absent | 2→3 | 2→4 |
| Exposed bodies | 0 | 19→22 | 19→26 |
| R DNp01 peak | −52 mV_eq | −51.933657842035174 mV_eq | −48.733429620245 mV_eq (rounded) |
| L DNp01 peak | −52 mV_eq | −52 mV_eq | −52 mV_eq |
| Threshold | −45 mV_eq | −45 mV_eq | −45 mV_eq |
| DNp01 spikes / motor output events | 0 / 0 | 0 / 0 | 0 / 0 |
| Nonzero actuator commands | 0 | 0 | 0 |
| Body displacement | 0 world_eq | 0 world_eq | 0 world_eq |
| Environmental sensory change | No | Yes | Yes |
| Closed loop / feedback wired | Yes / yes | Yes / yes | Yes / yes |
| Feedback realized / movement | No / no | No / no | No / no |

The micro-window is not a complete looming-response or behavioral experiment.
The 40 ms horizon was selected before neural execution using two existing
membrane time constants, jointly with a safe prescribed trajectory; it is not
biologically calibrated timing. The frozen world run reached
`COMPLETED_VALID_HORIZON`. Its geometry-domain termination policy remains
pinned, with no silent clamping or padding. Neither scenario was strengthened
after observing zero output. Numerical endpoints reflect floating-point
integration; table endpoints are nominal model-space values.

Longer observation yielded larger depolarization, but still zero genuine
spikes, actuation and movement. This is an outcome of the pinned model, not
evidence that a biological fly would fail to respond.

## Canonical scientific authorities

The manifest records these IDs and links to their committed scientific
documents. They retain their original schemas and ancestry.

| Authority | Canonical identity |
| --- | --- |
| Phase 7O, full 311-body execution | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` |
| Phase 8C, genuine persisted-spike composition | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` |
| Motor neural pathway contract | `a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c` |
| Target contract | `5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0` |
| Abstract electrical input | `1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa` |
| G1 proxy mapping | `030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8` |
| Electrical response | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` |
| Activation | `4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb` |
| Actuator | `478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40` |
| Body plant | `bb3696faae558778555601991de3fd36081d5853c889fcb7aac5ffd79593eba3` |
| Phase 13B closed loop | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` |
| Corrected Phase 16 diagnostic | `bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b` |
| Phase 18 preregistration | `580e088d89b38f086689c39568bf38bd04f5edf7f0d05065abe2c076a0d16bed` |
| Phase 18 world experiment | `ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c` |
| Phase 19 transfer review | `f7d278372f3527393bb041e4db3b45126668a5ec904ce65cb1f9f3546b28d267` |
| Phase 20 observation contract | `ae50e1faad223cdde63125a6216ce0993523f9933025fe1f04e9265450dec824` |
| Phase 21 dataset audit | `219622b71f1fd79caabe83665ddc859699875177883e7810c1b2bea4676e627d` |
| Phase 22 metadata resolution | `b40c260a4a37ef99853425dfb927aa2729c6f93da8abd6de66d6c7ead2654ee4` |

Historical downstream fixture artifacts validate synthetic model mechanics,
not connectome-driven movement. Phase 13B/18 compose those same scientific
semantics with genuine runtime output and scenario-specific provenance; they
do not substitute historical synthetic events or spoof fixture ancestry.

## Calibration and dataset branch: closed for v1

Status: `PHYSIOLOGICAL_TRANSFER_CALIBRATION_NOT_ESTABLISHED`.

The source-state→biological LC4/LPLC2 activity transform is unresolved. Public
GF numerical recordings were located and informed observation-operator design,
but stored target voltage scale and filtering/export provenance remain
incomplete. No current dataset passes the full calibration gates. The best
audited candidate remains `METADATA_INSUFFICIENT`.

Phase 20 permits **potential** baseline-relative DNp01/GF voltage comparison
with calibration, not direct mV_eq→mV equivalence. Sensory state remains only
qualitatively comparable. Population optogenetics, calcium amplitudes and
behavioral probabilities do not numerically identify per-body transfer.

The Phase 21/22 dataset/acquisition branch is formally **closed for v1**.
No author contact, unpublished metadata request, further acquisition or dataset
search is planned. Their historical next-action recommendations are superseded
by this closure, not rewritten. Future calibration may reopen only when new
public compatible data become available and pass explicit evidence/operator
review. It is not an imminent calibration TODO.

## Embodiment, units and scientific presentation

`mV_eq` is an uncalibrated model-space voltage-equivalent coordinate, never
biological millivolts. `world_eq` is an exploratory spatial coordinate, never
physical length without calibration; its velocity is not natural predator speed.

The body plant uses `c=(R+L)/2`, speed `v=g*c` with pinned model gain 1,
`x[n+1]=x[n]`, `z[n+1]=z[n]+dt*v[n]`, fixed +Z heading and zero reset.
It has no articulated joint mechanics, contact, gravity/inertia, calibrated
force, moment arms, steering or validated physical scale. It is not jump,
takeoff or locomotor biomechanics.

The visual specimen asset is **not** the body plant and **not** MaleCNS
morphology. Materials, shadows and visual scale establish presentation quality,
not anatomical or biomechanical validation.

The frontend exposes exactly `BASELINE_CONTROL`, `LOOMING_CIRCUIT_VALIDATION`
and `LOOMING_WORLD_EXPERIMENT`. It presents backend-authoritative snapshots,
with render-only adjacent-frame interpolation and exact-boundary telemetry.
Slowed display playback is not scientific duration. It neither decides
behavior nor integrates scientific motion. Current scenario labels and
interpretation panels preserve these limits; no frontend changes are needed.

## Negative findings and remaining unknowns

The 1.4 ms horizon alone is not a sufficient sole explanation of silence:
the separate preregistered 40 ms design also did not spike. This comparison is
not an isolated causal duration intervention; trajectory/exposure differ.
Full exposure of all 311 bodies on both sides in the same 14 intervals also
remained subthreshold. Corrected Phase 16 therefore calls projection a
**material**, not independently dominant limiter. Spatial exposure, sensory
dynamics, membrane integration, observation horizon and causal latency are
coupled effects, not statistically or causally independent factors.

No missing-drive/composition bug was found in the audited canonical chain;
that is not a general proof of bug absence. Structural counts are not justified
as efficacy. Existing evidence cannot identify k numerically, and current GF
data do not support calibration. None of these results establishes biological
inadequacy of a parameter or a biological failure to respond.

Unknowns remain: the sensory-state observation transform, physiological
transfer magnitude, LC4:LPLC2 per-body efficacy, calibrated DNp01 voltage,
absolute retinal registration, physical world scale, validated biomechanics
and broader behavioral circuits. Consciousness, memory and learning have not
been demonstrated and are outside this milestone.

## Allowed claims

- Connectome-based **selected-circuit** simulation with MaleCNS structural routing.
- Biologically inspired, explicitly uncalibrated neural dynamics.
- Identity-resolved sensory population and deterministic content-addressed replay.
- Exploratory closed-loop model with authoritative body-feedback wiring.
- Model-derived subthreshold response and honest zero-output outcomes.
- Preregistered exploratory model-space world experiment.

## Forbidden claims

- Complete fly emulation, whole-fly or whole-connectome neural simulation.
- Living fly, digital organism, consciousness or sentience.
- Biologically calibrated DNp01 voltage, retinal geometry or physical world.
- Calibrated jump/escape behavior, validated escape model or predicted biological escape probability.
- Genuine memory or genuine learning.

## Next-direction review

The criteria are evidence availability, MaleCNS compatibility, new capability,
arbitrary-assumption risk, implementation complexity, testability and long-term
contribution. These are qualitative judgments, not numerical rankings or
evidence that an unselected circuit is already implementation-ready.

| Option | Evidence / MaleCNS compatibility | New capability / assumption risk | Complexity / testability / long-term value |
| --- | --- | --- | --- |
| A: expand looming populations | Existing pathway evidence helps; additional identities/functional roles still need audit | Potential circuit detail; more uncalibrated inputs and cardinality-sensitive aggregation | Bounded extensions can be replayed; risks deepening one silent slice without a new behavior dimension |
| B: second bounded circuit | Require explicit primary functional evidence and MaleCNS identity/routing audit before selection | Can add a genuinely new circuit dimension; no guarantee of movement | More integration work, but scope can be bounded with deterministic genuine-path tests; diversifies scientific capability |
| C: improve embodiment | Current validated kinematics do not supply biomechanics evidence | Physical interactions would add capability but need force/scale/contact assumptions | High complexity and validation burden; valuable later, not a fix for missing neural physiology |
| D: richer worlds | Existing world runtime is compatible; no new neural evidence follows from scenery | Product variation, limited genuinely new neural capability | Relatively tractable scenario tests; risks presenting more worlds than the selected circuit can explain |

Recommend exactly one next major milestone: **evidence-gated selection and
validation of a second bounded MaleCNS circuit adding a genuinely new circuit
capability**. Do not casually name a candidate. First establish identities,
sides, directed structural routes, primary functional evidence, state/observable
semantics, compatible downstream embodiment and testable causal boundaries.
Then implement one bounded vertical slice only if that audit supports it.
Acceptance must not require a spike, displacement or desired behavior. The
frozen looming circuit remains its reproducible control; no gain tuning is
recommended.

## Reproducibility and validation

Before edits, all five required offline replays passed unchanged: full Phase
7O numerical recomputation, genuine Phase 8C production replay, Phase 13B,
corrected Phase 16 and Phase 18. Their respective measured CLI wall times
were 6.368, 3.699, 7.246, 15.720 and 17.137 seconds; timings are not hashed.
The Phase 19–22 inner-object hashes were recomputed against their stored IDs.
All 18 manifest authority IDs occur in their actual committed source documents.

Five isolated governance tests protect canonical hashing/tamper detection,
documented authorities and immutable evidence IDs, uncalibrated units/contracts,
the three honest null results, backend authority, closed dataset branch,
claim budget and absence of raw dataset paths. Where local canonical artifacts
are available, the tests also compare peaks, exposure, statuses, events and
stationary body/actuator records directly with their hash-verified results.

Validation passed: five focused tests; **1,035 full Python tests**, one existing
deselection and two dependency deprecation warnings, in 561.34 seconds;
**53 frontend tests**; Ruff check, Ruff format (307 files), diff check, frontend
lint/typecheck/build. The post-edit five-artifact replay round also passed with
unchanged identities/results. Status document size is 18,965 bytes; canonical
inner status is 14,897 bytes. No model equation, parameter, dataset, historical
artifact or frontend source is modified. Only the four intended Phase 23 files
remain visible. No commit or push.
