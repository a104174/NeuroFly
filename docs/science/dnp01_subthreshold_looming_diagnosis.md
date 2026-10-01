# Phase 16 — genuine subthreshold DNp01 looming diagnosis

## Outcome and scope

`SUBTHRESHOLD_RESPONSE_CHARACTERIZED_TARGETED_MODEL_REVIEW_JUSTIFIED`.
The one review target is the scientific justification for the **scenario's
1.4 ms observation horizon**, not a new duration or parameter selection.
No retuning, optimizer, spike-seeking sweep, synthetic event injection, new
biological research or frontend change was performed.

The canonical right DNp01 excursion is 0.066342157965 model voltage units,
only 0.009477451138 of its 7-unit rest→threshold excursion. The remaining margin
is 6.933657842035. Left DNp01 remains at rest. Routing, sensory stepping,
transfer and membrane accounting agree with their existing authorities; no
implementation/composition bug was revealed.

Two scoped mathematical bounds explain why there is no unique culprit:

- With the recorded per-body exposure envelope and pinned gain/k, total right
  drive cannot exceed 3.474071129128 units, less than the threshold excursion
  even without finite-horizon attenuation. This is not a claim about a continued
  approaching object, larger future footprints or all possible stimuli.
- Even the pre-existing Phase 13A **all-311 full-exposure** audit remains below
  threshold under the same 14-interval horizon and membrane dynamics. Thus
  replacing sparse exposure with that mathematical upper bound would not alone
  produce a spike during the current window.

## Repository and replay gate

Started clean at `ee93c4cfc22d7bbb154ff9346162935e14767827`, equal to
`origin/main`. Phase 15 (`ee93c4c`), Phase 14 (`e7bb923`) and Phase 13B
(`5d58fd7`) are committed. Initial diff check passed. Required pre-edit replays:

| Source | Identity | Verification |
| --- | --- | --- |
| 13B | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` | full numerical two-run replay; unchanged |
| 7O | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` | full numerical recomputation, exact config/result and artifact identity |
| 8C | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` | genuine persisted 7O source/event/motor replay |

Phase 7O still has zero spikes across all 35 conditions. Phase 8C has no genuine
motor events and zero right/left TTMn state. Both Phase 13B scenarios retain
zero spikes, downstream events, activation, actuator commands and movement.
The body remains at x=z=0; feedback is wired but not realized by movement.

## Evidence versus assumptions

MaleCNS/pinned contracts establish the 311 identities, types, sides, direct
source→target routing and source-column topology. Population: 126 LC4 (71 L,
55 R) and 185 LPLC2 (94 L, 91 R); 146 sources route to 10001/R and 165 to
10010/L. Structural `ConnectsTo.weight` counts are routing metadata only,
never efficacy, conductance, release probability or drive multipliers.

World geometry, projection, duration, sensory dynamics and transfer magnitude
are explicit model assumptions. LIF parameters are pinned modelling coordinates
/priors, not DNp01-specific empirical calibration. This phase does not infer
biological adequacy from a silent exploratory model.

| Quantity | Pinned value | Interpretation |
| --- | --- | --- |
| dt / intervals / stored boundaries | 0.1 ms / 14 / 15 | simulation grid; no extension |
| World object | x=0, z=4, radius=1; vz=-1 world_eq/ms | model-space prescribed approach |
| Projection | R, hex(23,9), floor(10×atan2(radius,distance)) | unregistered fixed-column assumption |
| Sensory gain / tau | 1 / 1 ms | dimensionless filter assumptions |
| Shared transfer k | 1 mV_eq/state | uncalibrated held external-drive conversion |
| DNp01 rest / reset | -52 / -52 | original model coordinates labelled mV_eq, not biological mV |
| DNp01 threshold | -45 | pinned model threshold; excursion 7 |
| tau_m / tau_s | 20 / 5 ms | membrane / synaptic-filter parameters |
| Refractory | 2.2 ms / 22 intervals | only installed on a spike; never engaged here |
| Edge delay / k_syn | 1.8 ms / 0.01 | inactive in the empty-edge DNp01 readout graph |

The 1.8 ms graph-delivery delay does **not** delay this external-drive path.
No synaptic graph deliveries occur; synaptic state remains exactly zero.

## Decomposition authority and equations

Diagnostic code consumes the persisted Phase 13B arrays after full source
replay. No historical model is modified. It reuses:

- `route_population_drive`: sorted per-identity contribution ledger and sums;
- `integrate_exposure_values`: verifies each of the 311 sensory traces;
- `LIFSimulator` / `lif_interval_step`: membrane replay, additive population
  response accounting and difference-based leak/drive/synaptic term isolation.

The existing equations, stated here for interpretation rather than implemented
again in the diagnostic, are:

```
s_i[n+1] = alpha_s*s_i[n] + gain*e_i[n]*(1-alpha_s)
drive_j[n] = sum_{i routed to j}(k*s_i[n])
v[n+1] = rest + alpha_m*(v[n]-rest) + (1-alpha_m)*drive[n]
         + existing filtered-synaptic term       (zero in these runs)
margin[n] = threshold - stored_membrane[n]
```

The drive is a held model-space equilibrium-offset quantity, not measured
current, per-step additive voltage or conductance. Population decomposition
is additive because these verified runs remain subthreshold with no reset or
refractory activation. Each isolated population contribution is evaluated
through the **same** LIF authority, with rest subtracted, and their sum is checked
against the stored total excursion. Fractions describe model drive, not neural
activation percentages or biological efficacy.

Term accounting evaluates the actual kernel with (1) zero external/synaptic
input, (2) actual drive and zero synaptic input, (3) actual drive/synaptic state.
Differences isolate contributions without introducing a second LIF equation.
Each actual transition is checked against the persisted next boundary. A
contradiction raises `DiagnosticCompositionError`; it is not silently repaired.

## World, exposure, sensory and drive trajectory

Half-angle grows 0.244978663→0.367173834 radians as **dimensionless analytic
model geometry**, not calibrated visual registration. Radius changes at
boundary 8 (0.8 ms). Active **source columns** are 16→28, distinct from exposed
**sensory bodies** 19→22; the source-grid primitive is reused, not a full ideal
hex-grid count. Exposure is fractional column overlap, not binary full-body
stimulation.

All 311 states are retained. Left exposure/state/drive is exactly zero.
Right exposed LC4 count remains 6, while LPLC2 changes 13→16. Existing cells'
overlap fractions also increase when the radius changes. Sensory state remains
continuous across the step in exposure; growth/drive slope changes afterwards,
not an instantaneous voltage jump. No decay phase exists in this short,
monotonically approaching canonical run.

| Boundary | Time ms | Distance world_eq | Radius | Bodies exposed | LC4 state sum R | LPLC2 state sum R | Available drive R | DNp01 R coordinate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.0 | 4.0 | 2 | 19 | 0 | 0 | 0 | -52 |
| 1 | 0.1 | 3.9 | 2 | 19 | 0.048398946 | 0.133003393 | 0.181402339 | -52 |
| 2 | 0.2 | 3.8 | 2 | 19 | 0.092192123 | 0.253349839 | 0.345541963 | -51.999095252 |
| 7 | 0.7 | 3.3 | 2 | 19 | 0.256032783 | 0.703594429 | 0.959627212 | -51.983885819 |
| 8 | 0.8 | 3.2 | 3 | 22 | 0.280066989 | 0.769641959 | 1.049708948 | -51.979180028 |
| 9 | 0.9 | 3.1 | 3 | 22 | 0.349975399 | 0.930442113 | 1.280417513 | -51.974048423 |
| 10 | 1.0 | 3.0 | 3 | 22 | 0.413231145 | 1.075940110 | 1.489171255 | -51.967791748 |
| 13 | 1.3 | 2.7 | 3 | 22 | 0.569117744 | 1.434503392 | 2.003621136 | -51.943368493 |
| 14 | 1.4 | 2.6 | 3 | 22 | 0.611519339 | 1.532033615 | 2.143552954 | -51.933657842 |

Full 15-boundary geometry, column sets, exposure counts, means/maxima/sums,
nonzero-state counts, available drive and margins are in the diagnostic.
**Boundary 14's available drive is diagnostic only:** it has no outgoing
interval. Peak **used** drive is 2.003621135981 at boundary 13, not the final
available 2.143552953978. No 15th interval is integrated.

| Final sensory summary R | LC4 | LPLC2 |
| --- | --- | --- |
| All-side-R population count | 55 | 91 |
| Nonzero / exposed count | 6 | 16 |
| State mean over full type/side population | 0.011118533435 | 0.016835534231 |
| State maximum | 0.264677408239 | 0.276342451688 |
| State sum | 0.611519338938 | 1.532033615040 |
| Exposure sum | 1.014687774115 | 2.459383355014 |

Means include unexposed zero states. Incoming state sums equal pre-transfer
inputs for the corresponding type/side. Shared k=1 changes numerical units,
not source ranking, and neither type receives an independently invented weight.

## Population and identity contributions

Integrated used drive is a left-held `dt * sum(drive[0:14])`, unit mV_eq·ms;
it is not physical charge/work. Right total is 1.356914872298; left total is 0.

| Contribution R | LC4 | LPLC2 |
| --- | --- | --- |
| Integrated used drive, mV_eq·ms | 0.373081596841 | 0.983833275457 |
| Fraction of total integrated model drive | 0.274948417515 | 0.725051582485 |
| Contribution to terminal membrane excursion, mV_eq | 0.018247681624 | 0.048094476341 |

At every boundary each ledger entry is `k * source_state`. This supports a valid
identity-resolved additive decomposition. The artifact retains all nonzero
contributing bodies' exposure/state/drive traces and ranks the top five by used
drive integral, body ID as tie-breaker. Zero-total fractions are null, not
invented percentages. Largest right contributors:

| Body / type / side | Integrated used drive | Final exposure | Final state |
| --- | --- | --- | --- |
| 20749 / LPLC2 / R | 0.181454838917 | 0.436893203883 | 0.276342451688 |
| 18929 / LPLC2 / R | 0.177998556271 | 0.428571428571 | 0.271078785942 |
| 16128 / LC4 / R | 0.170353042079 | 0.424242424242 | 0.264677408239 |
| 14465 / LPLC2 / R | 0.160417798052 | 0.361904761905 | 0.235243091736 |
| 17551 / LPLC2 / R | 0.107025000382 | 0.262773722628 | 0.164885322743 |

This ranking reflects source overlap and filter history, not structural contact
counts or measured synaptic efficacy. A test multiplies all structural counts
by 1000 and verifies drive/ledger values are unchanged.

## Peak, threshold margin and Baseline comparison

| Scenario / DNp01 | Most depolarized boundary | Peak coordinate | Threshold | Margin | Rest displacement | Spikes |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline / 10001 R | 0 (all boundaries tied) | -52 | -45 | 7 | 0 | 0 |
| Baseline / 10010 L | 0 (all boundaries tied) | -52 | -45 | 7 | 0 | 0 |
| Looming / 10001 R | 14 / 1.4 ms | -51.933657842035 | -45 | 6.933657842035 | 0.066342157965 | 0 |
| Looming / 10010 L | 0 (all boundaries tied) | -52 | -45 | 7 | 0 | 0 |

All voltages/margins are model coordinates labelled mV_eq, not biological
millivolts. Matched-boundary Looming-minus-Baseline comparison isolates stimulus
change: terminal membrane delta R +0.066342157965 / L 0; margin delta R
-0.066342157965 / L 0; available drive delta R +2.143552953978 / L 0; sensory
state deltas LC4 R +0.611519338938 and LPLC2 R +1.532033615040; exposed-body
delta +22. At boundary zero exposure delta is already +19 but state/drive/
membrane deltas remain zero. Every matched-boundary delta is persisted.

Right interval term totals: external-drive increment +0.067676411593, leak
-0.001334253629, net +0.066342157965. Synaptic, reset and refractory effects
are exactly zero. Leakage from accumulated depolarization is small relative to
drive here; the important membrane attenuation is the finite-time drive factor,
not a large negative leak cancelling the input.

## Temporal accumulation and causal latency

Duration/tau_sens = 1.4; duration/tau_m = 0.07. A held constant external drive
would contribute `1-exp(-0.07)=0.067606180094` of its equilibrium offset by the
end. Actual drive starts at zero and grows, so this is not the actual trajectory
or a recommendation to extend time. Short sensory and membrane accumulation
jointly suppress terminal response; individual biological adequacy is unknown.

Existing simultaneous update order is correct, not an off-by-one defect:

```
boundary n:     geometry → exposure e[n]; stored state s[n] → drive[n]
interval n→n+1: drive[n] → membrane[n+1]; e[n] → sensory state s[n+1]
boundary n+1:   a threshold crossing, if any, is stamped/available here
```

Exposure at boundary 0 first changes sensory state/drive at boundary 1;
membrane first depolarizes at boundary 2 (0.2 ms). Radius expansion at boundary
8 changes sensory state and drive at 9, affecting membrane at 10. The final
exposure/state never drives an extra interval. No new motor/event delay is
inserted and no pinned delivery semantics are bypassed.

## Maximum-exposure and threshold-distance diagnostics

The [Phase 13A readiness document](first_closed_loop_scenario_readiness.md)
recorded a read-only upper-bound calculation, not a persisted canonical world
scenario. Phase 16 verifies it with existing sensory and LIF batch authorities:
all 311 bodies on **both sides**, exposure=1 for 14 intervals, zero initial
sensory state, unchanged gain/tau/k/LIF/grid. 146 sources feed R and 165 feed L.

| Full exposure audit | DNp01 R | DNp01 L |
| --- | --- | --- |
| Peak coordinate | -47.66741697736826 | -47.103587679902496 |
| Threshold margin | 2.667416977368262 | 2.103587679902496 |
| Spikes | 0 | 0 |

It is not the canonical right-only projection or a biological maximum-exposure
protocol. No larger stimulus or alternate model parameter was selected.

For the **recorded-footprint** analytical envelope, sensory filtering is a
positive convex combination from zero. Thus each state is bounded by gain
times its maximum recorded exposure; the existing positive additive transfer
gives a right drive bound 3.474071129128. With zero synaptic input, membrane
excursion cannot exceed that drive envelope. It falls short of the 7-unit
threshold excursion by at least 3.525928870872, even before temporal attenuation.
This does not predict continued approach into new footprints or recommend
different geometry, k or gain.

Additional peak depolarization to threshold is 6.933657842035; observed/required
rest excursion is 0.009477451138. These are distance diagnostics only. The
optional hypothetical crossing multiplier was **not computed**: explaining
the result does not require a spike-targeting counterfactual or gain target.

## Bottleneck classifications (model-scoped)

| Candidate | Classification | Basis / limitation |
| --- | --- | --- |
| A WORLD_TO_COLUMN_PROJECTION | MATERIAL_MODEL_LIMITER | Sparse fractional exposure materially limits drive with pinned gain/k. Full exposure also remains subthreshold over the same horizon; no dominant causal ranking is established. |
| B SENSORY_STATE_DYNAMICS | MATERIAL_MODEL_LIMITER | Zero initial state, 1 ms filter and delayed exposure growth reduce used drive during the short window. |
| C SENSORY_TO_DNP01_TRANSFER_MAGNITUDE | NOT_IDENTIFIABLE_FROM_CURRENT_EVIDENCE | k=1 sets overall magnitude but adequacy/independent ranking is confounded with sensory normalization and membrane/threshold assumptions. |
| D DNP01_MEMBRANE_DYNAMICS | MATERIAL_MODEL_LIMITER | 20 ms membrane tau against 1.4 ms observation means a small drive-to-membrane accumulation fraction; no inhibitory/synaptic/reset effect explains silence. |
| E SCENARIO_TEMPORAL_WINDOW | MATERIAL_MODEL_LIMITER | Even the full-exposure audit cannot cross threshold in this fixed horizon. Not a recommendation to lengthen it. |
| F DISCRETE_CAUSAL_LATENCY | MATERIAL_MODEL_LIMITER | Two boundaries from exposure to membrane; initial zero-drive interval and final unused state matter in 14 intervals. This is the intended ordering, not a bug. |

No predeclared quantitative definition supports a dominant-limiter designation.
The classification was corrected without introducing a retrospective ranking
criterion or changing any numerical diagnostic. Spatial exposure, sensory-state
dynamics, membrane integration, the short temporal window and discrete causal
latency are coupled effects, not statistically or causally independent factors.
The factors act jointly. Nothing establishes that threshold, gain, transfer or
duration is biologically wrong. Parameter adequacy and independent biological
identifiability remain `NOT_IDENTIFIABLE_FROM_CURRENT_EVIDENCE`. No efficacy
is inferred from MaleCNS contact counts. Existing historical sensitivity /
transfer diagnostics are not rerun as a search for a spike or adopted as values.

## Artifact and reproducibility

New result schema `dnp01_subthreshold_diagnostic_v1`; artifact schema
`dnp01_subthreshold_diagnostic_artifact_v1`. Semantic config contains source
identities/hashes, matched-boundary analysis, interval integration, term
accounting and identity-ranking choices only. Scientific parameters are
snapshots of the pinned source in the result, not alternate configuration.

- Artifact ID: `bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b`
- Config hash: `6740139521b4d39c49400faf0a0f4811ee1a9ece38bff655e5642e35a8f7993a`
- Result hash: `3166abdb1f2dd072b26d40aba869c6a9d49bc45c85672f478180e685bf3fb39c`
- Size including manifest: 91,070 bytes; generated under the existing ignored
  `data/derived/malecns/looming_giant_fiber_v1/` root.

The corrected artifact differs from the previous result only in the projection
classification and its explanation. Direct comparison verified that every other
result field and the complete config are exactly unchanged; the config hash is
therefore unchanged. No numerical diagnostic or canonical source was altered.

```
python -m neurofly.dnp01_subthreshold_diagnostic_cli generate
python -m neurofly.dnp01_subthreshold_diagnostic_cli inspect ARTIFACT_DIRECTORY
python -m neurofly.dnp01_subthreshold_diagnostic_cli replay ARTIFACT_DIRECTORY
```

Inspect/replay validate the exact Phase 13B identity, numerically replay both
canonical runs and historical source ancestry, recreate routing/kernel
decompositions and compare canonical bytes, hashes, manifest and directory ID.
No network/randomness. No historical artifact migration or loader relaxation.
Noncanonical/staging files are not accepted as canonical source identities.

Focused tests protect matched deltas, population/identity additivity, right/left
isolation, threshold margins, term reconstruction, intended latency, final
unused drive, full-exposure audit, the scoped analytical bound, count
independence, deterministic bytes and offline replay. Tamper cases include
source/model/scenario identity, membrane, threshold, timing, population and
identity contributions, bottleneck classifications, hashes and manifest,
including attackers recomputing internal hashes.

## Evidence required before any revision

Exactly one next action: a bounded **scenario temporal-design evidence review**
asking whether the current 1.4 ms window is a software fixture horizon or an
appropriate observation window for the intended LC4/LPLC2→DNp01 question.
Trace the existing timing provenance and require stimulus/recording-context
support before recommending any replacement. No new numeric duration, parameter
retuning, movement criterion or long sequence of metadata phases is selected.

This review is justified by the measured duration/tau relationships and the
unchanged all-exposure bound—not by a stationary frontend. It must also retain
the recorded-footprint amplitude limitation: duration alone is not identified
as a sufficient solution. No claim of biological nonresponse or escaped/failed
behavior follows from the model.

## Final verification / Phase 16 status

Phase 16 `PASS`. Focused diagnostic tests: 25 passed. Full `python -m pytest`:
1,004 passed, 1 deselected, two existing dependency deprecation warnings
(650.50 s on the semantic-correction rerun). Ruff check and format check,
diff check and frontend regressions
(52 tests, lint, typecheck, production build) pass. All historical source
replays remain unchanged. No existing scientific implementation or frontend
file differs from the committed source. Six intended Phase 16 files remain;
the canonical diagnostic is ignored. Two generated development-only diagnostic
drafts were removed (not recoverable from Git); no historical source artifact
was removed or changed. No commit or push.
