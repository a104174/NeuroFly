# Phase 25 — preregistered HS→DNp15 neural-only validation

## Scientific boundary

`HS_DNP15_NEURAL_VALIDATION_COMPLETE`: deterministic, identity-resolved
propagation through the selected six-route MaleCNS chemical motif. This is a
neural foundation relevant to horizontal-motion course control, **not steering,
navigation, yaw, calibrated optic flow or complete DNp15 physiology**.

No threshold or spike model is defined. Target events are explicitly null with
`NOT_DEFINED` semantics, not a claim of zero biological/model spikes. No motor,
actuator, body, scenario catalog, API or frontend integration exists.

## Authorities and structural revalidation

Started clean on `main == origin/main` at committed Phase 24
`0d33475cd19cebef6f7466c1f36c44250d9e845e`. The offline committed evidence authority
was used, not a new network acquisition or mock connectome:

- v1 scientific-status ID:
  `1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6`.
- Phase 24 selection ID:
  `435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41`.
- Candidate: `hs_dnp15_horizontal_motion`,
  `READY_FOR_BOUNDED_VALIDATION_DESIGN`, dataset `male-cns:v1.0`.

The loader verifies both authority hashes, selected classification, the exact
source/target identity records, routes and omissions, plus all stored query
response hashes. Canonical order is ascending body ID; route contributions are
ordered by source/target ID. Laterality is metadata, never morphology geometry.

| Source | Type/side | Target | Type/side | Structural contact count |
| --- | --- | --- | --- | --- |
| 10015 | HSN/R | 11215 | DNp15/R | 138 |
| 10016 | HSE/R | 11215 | DNp15/R | 122 |
| 10023 | HSS/R | 11215 | DNp15/R | 23 |
| 10034 | HSE/L | 12069 | DNp15/L | 78 |
| 10181 | HSN/L | 12069 | DNp15/L | 126 |
| 10419 | HSS/L | 12069 | DNp15/L | 14 |

These counts are provenance only. They never scale input, state, contribution,
drive or neural increment. Tests multiply all counts by 1,001 while retaining
topology and reproduce all numerical condition trajectories. A changed count
would change provenance identity, not physiological efficacy.

The full eight-node induced query has 13 edges. The seven non-selected edges
remain frozen in the preregistration and artifact config:

| Omitted source→target | Structural count |
| --- | --- |
| 10015→10016 | 4 |
| 10016→10015 | 2 |
| 10016→10023 | 1 |
| 10034→10181 | 1 |
| 10034→10419 | 1 |
| 10419→10034 | 2 |
| 12069→10419 | 1 |

They are not active model edges. The wider H2/inhibitory/recurrent network and
electrical coupling remain outside `BOUNDED_CHEMICAL_FEEDFORWARD_MOTIF`.
No approximation to electrical coupling is introduced.

## Functional evidence and neutral directional representation

The [original Erginkaya et al. 2025 paper](https://www.nature.com/articles/s41593-025-01948-9)
was inspected before selecting semantics. Its Results and Fig. 1 identify
DNp15/DNHS1, HS ipsilateral horizontal-motion sensitivity and broader binocular
network effects. This supports pathway relevance, not calibrated per-type
curves or isolated chemical efficacy. [Suver et al. 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5125229/)
is retained through the Phase 24 evidence authority for HS/DNHS1 association.

No exact HSN/HSE/HSS tuning magnitudes are adopted. A positive side descriptor
is qualitatively motivated by front-to-back motion sensitivity; its magnitude
and sign-to-proxy mapping are model conventions. Negative input means the
opposite signed descriptor. Equal opposite response is explicitly **not** an
empirical claim about biological reverse-direction tuning or hyperpolarization.
HSN, HSE and HSS share a minimal proxy rule but remain six distinct states;
neither spatial receptive-field differences nor measured physiological equality
are asserted. Existing literature preparation/sex and MaleCNS specimen identity
are not treated as exact biological calibration matches.

## Preregistration and chronology

[Frozen preregistration](hs_dnp15_neural_validation_preregistration.json), schema
`hs_dnp15_neural_validation_preregistration_v1`, was written and independently
canonical-hashed **before the new neural module existed or any candidate neural
execution occurred**:

`371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074`

The recorded tool sequence is structural/history replay and primary evidence
inspection → serialize contract → print frozen hash → implement model → first
`generate`. No candidate gain/duration tests preceded the freeze. First generation
executed each condition once; staging checked bytes/integrity without rerunning
the model. Subsequent executions are explicit replay, regression or performance
checks of the same contract. No scientific parameter was changed after output.
The chronology is an auditable work record, not an external timestamp signature.

## Frozen assumptions

| Assumption | Frozen design | Classification/rationale |
| --- | --- | --- |
| Pathway relevance | HS horizontal motion; DNp15 neural readout | `PRIMARY_EVIDENCE_CONSTRAINED`, qualitative only |
| Input | Signed side descriptors in [−1,1], `horizontal_motion_eq` | `EXPLORATORY_BOUNDED_ASSUMPTION`; no deg/s or retinal registration |
| Direction/identity sharing | All three identities on a side receive its descriptor | `EXPLORATORY_BOUNDED_ASSUMPTION`; no tuning curve or physiological equality |
| Source state | Signed dimensionless proxy; neutral 0; unit input mapping; tau 5 ms | `EXPLORATORY_BOUNDED_ASSUMPTION`; standalone simple proxy timescale |
| Transfer | `hs_to_dnp15_proxy_scale = 1`, mean of three eligible sources | `EXPLORATORY_BOUNDED_ASSUMPTION`; defines proxy scale, not v1 k |
| Target state | `dnp15_state_eq`; neutral 0; tau 10 ms; no threshold/events | `EXPLORATORY_BOUNDED_ASSUMPTION`; continuous smoothing, not LIF calibration |
| Timing | 50 ms = five target taus; 20 ms pulse + 30 ms recovery | `EXPLORATORY_BOUNDED_ASSUMPTION`; observe declared transients, no response target |
| Grid/kernel | dt 0.1 ms; exact exponential held-drive integration | `REPOSITORY_NUMERICAL_CONVENTION`; numerical reuse, not biological resolution |

The new coefficient is **not** `1 mV_eq/state`: its units are
`dnp15_state_eq/source_state`. No model-space voltage coordinate is used here.
Mean aggregation describes a target's three-channel average; it is independent
of contact multiplicity and explicitly differs from v1's unnormalized sum.
Expansion to a different population would require a new contract, not silent
renormalization. These choices were selected for bounded simplicity and scale
definition, not spikes, asymmetry or movement. Randomness and seeds are absent.

The 5/10 ms timescales are standalone modelling choices, not inherited sensory
tau or DNp01 membrane parameters. The dt/tau ratios are 0.02 and 0.01. Exact
zero-order-hold updates avoid an Euler stability restriction; no model retuning
or empirical temporal calibration follows from that mathematical property.

## Equations and causal order

For each source identity i on side q:

`s_i[n+1] = u_q[n] + (s_i[n] − u_q[n]) exp(−dt/tau_source)`.

For each eligible selected route:

`c_i[n] = hs_to_dnp15_proxy_scale × s_i[n] / 3`;
`D_j[n] = sum(c_i[n])` for that target's three verified inputs.

`y_j[n+1] = D_j[n] + (y_j[n] − D_j[n]) exp(−dt/tau_target)`.

At boundary n, route **s[n]**, store current states/drives/contributions, then
update source and target simultaneously. Input at n first changes s[n+1],
then can affect y[n+2]. No target update uses newly computed source state at
the same interval. No integration occurs after the final boundary.

The implementation is an isolated signed continuous-proxy kernel, not a copy
of the looming exposure model or a relabelled DNp01 LIF. Target coordinates are
stored separately for 11215/R and 12069/L. `R−L` is a derived model diagnostic,
never a yaw or actuator command.

## Canonical conditions and first accepted results

All conditions have 500 intervals / 501 boundaries. Input is active at
boundaries 0–199 (0–20 ms intervals), then disabled for recovery. Side swap is
an explicit provenance/control condition intentionally equivalent to left-only,
not an additional parameter candidate.

| Condition | Pulse R/L | Source result | R target peak | L target peak | Final R−L |
| --- | --- | --- | --- | --- | --- |
| `NO_MOTION_CONTROL` | 0/0 | All remain neutral | 0 | 0 | 0 |
| `BILATERAL_MATCHED_MOTION` | +1/+1 | Six positive proxy trajectories | 0.761610396111446 | 0.761610396111446 | 0 |
| `RIGHT_SIDE_MOTION` | +1/0 | Three R trajectories; L neutral | 0.761610396111446 | 0 | 0.084073085756581 |
| `LEFT_SIDE_MOTION` | 0/+1 | R neutral; three L trajectories | 0 | 0.761610396111446 | −0.084073085756581 |
| `SIDE_SWAPPED_EQUIVALENT` | 0/+1 | Explicit swap of right-only | 0 | 0.761610396111446 | −0.084073085756581 |
| `DIRECTION_REVERSED` | −1/0 | Three negative R proxy trajectories | −0.761610396111446 | 0 | −0.084073085756581 |

Peak means signed state at the maximum absolute excursion. Active source
identities reach absolute peak 0.981684361111266 at 20 ms; final magnitude
0.002433352246904. Active targets peak at boundary 213 / 21.3 ms, then end at
signed magnitude 0.084073085756581. Unstimulated identities remain neutral.
No events are defined for **any** condition. All output is accepted unchanged;
neither nonzero response nor response magnitude is an acceptance target.

Neutral, side-swap and signed-reversal invariants follow from the preregistered
linear/symmetric model. They do not imply exact biological symmetry. The test
suite protects individual identities, eligible routes, omitted-edge exclusion,
two-boundary causal latency, final-boundary handling and query-order independence.

## Artifact, replay and CLI

| Identity | Value |
| --- | --- |
| Artifact schema | `hs_dnp15_neural_validation_artifact_v1` |
| Artifact ID | `2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113` |
| Config hash | `8ffc6263d1a70948d9a69ffa0ff066c9dcbb894d5766b72520e209ace60b452d` |
| Model hash | `fc566520c3257451b9bebe1ed9707731456739d52238c1a885cb3cd182e60728` |
| Result hash | `35b9bf6bb72f2d92522df25de020cc5e3d369ec0d257997d8cd7746a55e54864` |
| Total artifact bytes, including manifest | 714,329 |

Config embeds the preregistration including all omitted edges and authority
references. Result includes a shared time grid, input descriptors, six-source
states, six-route contributions, two-target drives/states, diagnostics and
explicit absent-event semantics. Canonical JSON bytes and file hashes are
validated; offline replay revalidates authorities and reruns every condition.
Rehashing a tampered payload/manifest does not bypass reconstruction.

```sh
python -m neurofly.hs_dnp15_neural_validation_cli generate
python -m neurofly.hs_dnp15_neural_validation_cli inspect ARTIFACT_DIRECTORY
python -m neurofly.hs_dnp15_neural_validation_cli replay ARTIFACT_DIRECTORY
```

Generated files reside under Git-ignored
`data/derived/experiments/hs_dnp15_neural_validation_artifact_v1/`.
Ignore coverage was checked before generation and source datasets were not
downloaded. Production execution accepts only the hash-validated frozen
contract; no gain override, output injection or motion-target interface exists.

Tamper coverage includes source/target identity, route, authority, parameter,
condition, source/target state, result hash and omitted-edge activation. Pure
test-local count mutation verifies identical numerical execution without
weakening canonical provenance validation. Performance observed: first
generation 0.146 s; complete execution 0.054 s; offline replay about 0.114 s.
Timings are not scientific parameters or identity inputs; no optimization needed.

## V1 preservation, tests and next boundary

Before implementation, 7O full numerical, 8C genuine production, 13B, corrected
16 and 18 replays all passed unchanged. Both the v1 status manifest and Phase
24 selection record are immutable. No v1 scientific kernel was edited.

The Phase 24 static dependency guard is narrowly extended to permit this new
science module's **offline structural-authority validation**. Existing v1,
scenario and API modules still cannot depend on the Phase 24 record. No Phase
24 simulation parameters exist to inherit. This is not a change to historical
evidence, classifications or numerical results.

Twenty-three focused neural tests and five selection-authority tests pass.
Full validation: **1,063 Python tests passed**, one existing deselection and
two dependency deprecation warnings in 570.74 s; **53 frontend regressions**
passed, as did Python Ruff check/format, diff check and frontend
lint/typecheck/build. No frontend source remains modified after restoring
build-generated route-type imports. Only eight intended Phase 25 files change,
including the narrowly scoped Phase 24 test adjustment; no commit or push.

The post-implementation replay round passed with unchanged IDs/results: 7O
5.918 s, 8C 3.322 s, 13B 7.196 s, corrected 16 16.352 s and 18 17.887 s.
The preregistration and both committed scientific authorities were independently
rehashed again after execution and match their original identities.

Allowed claims: MaleCNS-structured motif; exploratory horizontal-motion model;
identity-resolved bilateral neural readout; deterministic model response;
neural foundation relevant to course-control circuitry. Forbidden: biological
voltage/optic-flow calibration, complete optomotor network, per-contact efficacy,
steering, navigation, yaw, motor or body behavior. Null results remain valid.

Exactly one next action: preregister a bounded neural-only comparison of the
selected feedforward motif with the already-verified seven additional chemical
edges, reviewing their signs/dynamics before execution and without motor mapping.
