# Phase 7G — sensory-to-DNp01 sign, magnitude, and scaling assessment

**Scope:** evidence review and roadmap decision only. No production model,
artifact, parameter, or frontend behavior is changed by this assessment.

## Repository and model baseline

The assessment began at committed `main` (`8e1775b9af1d96b0a1cc60202621c3a721b36b68`),
with a clean worktree aligned to `origin/main`. Phase 7F is commit `8e1775b`
and Phase 7E is `5ae7529`.

Phase 7F consumes only the replay-verified Phase 7E dimensionless exploratory
sensory states (`09a3d3ddc02c81bb5ea229bf48b76811123ebd2e20cfce17f45e72442dcb8b15`).
Its immutable `relative_column_sensory_to_dnp01_artifact_v1` reference is
`4a000add359e60c0c0c654881a4659652d749c548af0e167469d210035c20213`.
It applies one shared positive conversion assumption,
`k_transfer_mveq_per_state = 1.0`, and routes by four exact MaleCNS chemical
edges. The counts 2, 62, 21, and 65 are validated and retained as structural
routing metadata, but are absent from the transfer calculation. The input
contract is explicitly restricted to the four Phase 7F sensory bodies and two
DNp01 readouts. The persisted sign policy is
`direct_visual_dnp01_depolarizing_assumption_v1`; Phase 7G evaluates its
pathway-level evidence without changing it.

## Sign evidence

The classification used here is deliberately conservative:

- `DIRECTLY_MEASURED_POSITIVE` would require a pair-resolved or otherwise
  isolated physiological measurement that establishes positive postsynaptic
  sign for the connection at issue.
- `SUPPORTED_POSITIVE` means anatomy plus functional activation/perturbation
  evidence supports a depolarizing positive contribution at the pathway or
  population level, without establishing a unitary per-body synaptic sign.
- `AMBIGUOUS` or `UNRESOLVED` would apply if that convergent pathway evidence
  were absent or materially conflicting.

| Pathway | Anatomy | Functional sign evidence | Direct unitary sign measurement located? | Phase 7G classification |
| --- | --- | --- | --- | --- |
| LC4 → DNp01/GF | LC4 directly synapses onto GF in the published adult-brain reconstruction; MaleCNS v1.0 separately has 126 direct chemical edges. | LC4 activation is reported to evoke GF output; LC4 silencing removes a component of the GF looming response, and the LC4 component is treated as excitatory in the population decomposition. | No paired LC4–GF or single-cell EPSP measurement found in the bounded reviewed set. | `SUPPORTED_POSITIVE` |
| LPLC2 → DNp01/GF | LPLC2 directly synapses onto GF in the published adult-brain reconstruction; MaleCNS v1.0 separately has 185 direct chemical edges. | Optogenetic population activation of LPLC2 produces a large, rapid GF depolarization; silencing removes the GF looming size component and reduces GF-mediated short-mode outcomes. | No paired LPLC2–GF or unitary EPSP measurement found in the bounded reviewed set. | `SUPPORTED_POSITIVE` |

Ache et al. identify LC4 and LPLC2 as direct visual inputs to GF and report
complementary visual feature contributions: LC4 is associated with angular
expansion velocity, while LPLC2 supplies a looming-size component. Their
whole-cell GF recordings under looming and cell-type silencing support a
positive population contribution from both pathways. The LPLC2 activation
experiment in Klapoetke et al. is especially direct at the pathway level:
GF whole-cell voltage depolarized following LPLC2 population optogenetic
stimulation. This was not a paired recording and does not estimate one
presynaptic cell’s transfer.

For LC4, von Reyn et al. and the later Ache analysis support an excitatory
velocity-related contribution to GF response; activation can evoke GF output,
and the LC4-silenced/remaining-component comparison contributes to the
population response reconstruction. Dombrovski et al.’s visuomotor work is
adjacent evidence about LC4 spatial wiring and downstream visual-to-action
organization, not an LC4-body-to-DNp01 unitary efficacy measurement. These
results support the direction of the Phase 7F pathway assumption, not its
constant gain under every stimulus or the sign of every individual synapse.

Primary sources:

- Ache et al. (2019), [“Neural Basis for Looming Size and Velocity Encoding in the Drosophila Giant Fiber Escape Pathway”](https://doi.org/10.1016/j.cub.2019.01.079).
- Klapoetke et al. (2017), [“Ultra-selective looming detection from radial motion opponency”](https://doi.org/10.1038/nature24626).
- von Reyn et al. (2017), [“Feature Integration Drives Probabilistic Behavior in the Drosophila Escape Response”](https://doi.org/10.1016/j.neuron.2017.05.036).
- Dombrovski et al. (2023), [“Synaptic gradients transform object location to action”](https://doi.org/10.1038/s41586-022-05562-8).

The result is not a claim that the two pathways have equivalent biology. Their
encoded stimulus features differ, and functional effects depend on stimulus
and circuit context. `SUPPORTED_POSITIVE` is a pathway-level sign judgment for
the bounded positive-transfer model, not evidence for a universal scalar
excitatory synapse model.

## MaleCNS neurotransmitter annotations

The pinned local MaleCNS v1.0 neuron snapshot contains per-body aggregate
predictions. All 126/126 LC4 bodies have both `predicted_nt` and `consensus_nt`
equal to acetylcholine; confidence min/median/max is 0.903621 / 0.962560 /
0.974733. All 185/185 LPLC2 bodies likewise predict acetylcholine; confidence
min/median/max is 0.827112 / 0.954378 / 0.971999. This is body-level
annotation of predicted transmitter identity, aggregated from synaptic
predictions, not measured transmitter release at the specific presynaptic
contacts onto DNp01. Confidence is not a postsynaptic response probability,
edge confidence, receptor identity, reversal potential, or efficacy.

The official [MaleCNS download page](https://male-cns.janelia.org/download/)
describes the v1.0 body-neurotransmitter table as aggregate neurotransmitter
predictions for each neuron. The associated visual-system study describes
neuron-level aggregation of presynaptic neurotransmitter classifier results
([Nern et al., 2025](https://doi.org/10.1038/s41586-025-08746-0)). ACh
prediction is consistent with the literature’s positive pathway evidence, but
does not itself establish the sign or magnitude of an individual
LC4/LPLC2→DNp01 connection.

## Direct electrophysiology search

The reviewed primary source set included Ache et al. 2019, Klapoetke et al.
2017, von Reyn et al. 2017 and 2014, the relevant LC4 visuomotor work, and
their cited GFS physiological context. It contains GF whole-cell recordings
under visual stimulation, cell-population activation/silencing, and GF spike
outputs. It did not yield the following pair-resolved quantities:

| Quantity searched | Result in reviewed source set | What the available evidence does measure |
| --- | --- | --- |
| LC4→GF unitary EPSP amplitude | Not found | Population optogenetic/looming response and GF output/voltage. |
| LPLC2→GF unitary EPSP amplitude | Not found | Population optogenetic/looming response and GF output/voltage. |
| Paired recording of one LC4 and GF | Not found | Cell-type-level perturbation and GF recording. |
| Paired recording of one LPLC2 and GF | Not found | Cell-type-level perturbation and GF recording. |
| Single-cell optogenetic source→GF voltage response | Not found | Population-targeted activation, not sparse identified single-cell transfer. |
| Pair-specific synaptic conductance, release probability, or per-cell gain | Not found | No quantitative pair-resolved efficacy in the reviewed evidence. |

“Not found” is bounded to the reviewed citation set; it is not proof that no
such experiment exists. The available GF recording is still strong functional
pathway evidence, but does not resolve one of the 311 MaleCNS bodies’ unitary
contributions.

## Published population-model coefficients

Ache et al.’s looming model fits constructed LC4- and LPLC2-associated
population components to measured GF membrane-response traces over multiple
looming conditions. The main model reports fitted component weights
`W_LPLC2 = 1.45` and `W_LC4 = 1.62` (with other terms for inhibitory or
additional components); the paper also reports a separate response-component
combination analysis with different optimal multipliers (1.1 and 1.5).
These are model-/analysis-specific dimensionless scaling multipliers in that
paper’s component equation, not measured synaptic constants. The inputs are
feature-derived and/or experimentally isolated population response
components; the fit endpoint is the measured GF looming membrane-response
trace across looming `r/v` conditions. The LC4/LPLC2 coefficients were fit at
population level; they do not apply to each cell, to MaleCNS structural
counts, or to Phase 7E state. Phase 7E `x_i` is generated from a synthetic relative-column
stimulus and an assumed leaky state equation; it is not LC4/LPLC2 voltage,
firing, or a measured population feature. Reusing these coefficients as
per-body `k_transfer` would therefore change both their input semantics and
scale without evidence.

## Transfer-magnitude identifiability

Phase 7F uses:

```text
d_i[n] = k_transfer_mveq_per_state × x_i[n]
```

`x_i` is dimensionless, but it is not an observed biological presynaptic
quantity. It is a deterministic exploratory state derived from synthetic
column-space anatomical exposure. No observation operator maps it to measured
LC4/LPLC2 membrane voltage, calcium, transmitter release, spike rate, or
population response. The output `mV_eq` is the simulator’s external-drive
interface unit, not a recorded synaptic EPSP or conductance.

Accordingly, even the existence of measured GF voltage responses cannot
identify `k_transfer` from the current model: there is no validated mapping
from Phase 7E `x_i` to the corresponding source signal or from Phase 7F
`mV_eq` drive to a pair-specific GF response. An aggregate GF response also
cannot disaggregate 311 source-body contributions without additional
observations and a source-state observation model. **`k_transfer` is
`NOT_IDENTIFIABLE`.** No structural count, ACh annotation, behavioral rate,
or old angular-experiment spike time changes that conclusion.

### Coefficient policy

One shared, free positive coefficient with explicit sensitivity is preferable
for exploratory model comparisons. It avoids presenting four unsupported
per-edge values, or separate `k_LC4` and `k_LPLC2`, as if they were measured.
The distinct LC4/LPLC2 stimulus features do not supply a quantitative mapping
from the arbitrary Phase 7E state scale to DNp01 input. Keep the reference
`k=1.0 mV_eq/state` unchanged as a software/model assumption. Do not fit it to
the angular-looming experiment or to behavioral outcome.

## Phase 7F sensitivity review

The committed deterministic grid is `k = 0, 0.5, 1, 2, 4 mV_eq/state`.
Across that grid, transfer contributions and subthreshold DNp01 membrane
changes scale with `k`; at `k=0` the model drive is zero and both readouts
remain at rest. No run in the committed grid produces a DNp01 spike. The
persisted reference result and sensitivity are:

| `k` (mV_eq/state) | DNp01 10001 R peak drive (mV_eq) | max `V_m` (mV) | spikes | DNp01 10010 L peak drive (mV_eq) | max `V_m` (mV) | spikes |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | -52.000000000 | 0 | 0 | -52.000000000 | 0 |
| 0.5 | 0.116037717 | -51.995749431 | 0 | 0.061919911 | -51.997737123 | 0 |
| 1 | 0.232075434 | -51.991498862 | 0 | 0.123839822 | -51.995474247 | 0 |
| 2 | 0.464150868 | -51.982997723 | 0 | 0.247679644 | -51.990948493 | 0 |
| 4 | 0.928301736 | -51.965995447 | 0 | 0.495359287 | -51.981896986 | 0 |

Membrane values are from the unchanged DNp01 model; these are model readouts,
not measured voltages. Route identity, side isolation, and exclusion of
structural weight are stable throughout.

As a read-only stress check, the Phase 7F calculation was evaluated over a
much broader assumption-space range without persisting a new artifact or
changing the reference. In the reference bilateral expansion, the first
integer coefficient producing an existing-model DNp01 event was `k=824`
(10001 R; step 14; 823 did not spike); for 10010 L it was `k=1547` (step 14;
1546 did not spike). Those values are hundreds to over a thousand times the
reference coefficient and are **model threshold locations in assumption
space**, not biological efficacy estimates or plausible fitted values. The
exercise confirms that spike/no-spike is threshold-sensitive at large assumed
gain, while the current 0–4 range is numerically uneventful. It does not
select a preferred coefficient.

The old angular experiment’s persisted spikes near 45.3/69.3 ms were not used
as targets. Its stimulus/input family is not equivalent to Phase 7D/7E’s
synthetic relative-column exposure.

## Structural weight boundary

The four Phase 7F counts—2, 62, 21, and 65—remain `male-cns:v1.0` chemical
connectome counts and routing metadata. The Phase 7F equation uses neither
these values nor any transform of them. No count is converted to transfer
gain, conductance, drive, probability, or sign. The asymmetry of these
structural counts does not establish an asymmetry in physiological efficacy.

Counts can contain information about anatomical contact number and, in some
systems, may be a general prior for contact area. For example, Barnes et al.
found count/contact-area correlation across a limited set of **larval** CNS
connections; they also emphasize that equal count-derived edge weights need
not imply equal physiological strengths because synapse sizes and
biophysical properties differ ([Barnes et al., 2022](https://doi.org/10.1371/journal.pone.0266064)).
That result is a `GENERAL_PRIOR`, not LC4/LPLC2→DNp01 pair-specific evidence,
and does not license using the 2/62/21/65 values as Phase 7F efficacy.

## 313-body connectivity and bounded scaling

The committed `looming_giant_fiber_v1` CircuitContract was loaded and
integrity-validated locally. Its source manifest identifies
`male-cns:v1.0`; hashes are:

- `neurons.jsonl`: `00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e`
- `connections.jsonl`: `f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a`

All 311 sensory bodies have exactly one direct chemical edge to one DNp01; no
source has multiple DNp01 targets in this selected projection, and no
source-target side mismatch was found. The fixed balanced routing counts are:

| Source type / side | Bodies and direct edges | Target |
| --- | ---: | --- |
| LC4 L | 71 | DNp01 10010 L |
| LC4 R | 55 | DNp01 10001 R |
| LPLC2 L | 94 | DNp01 10010 L |
| LPLC2 R | 91 | DNp01 10001 R |
| **Total** | **311** | **165 L / 146 R** |

The edges sum to 6,362 LC4 and 4,862 LPLC2 structural counts. Across all 311
edges, weights range 1–86, median 38, and nearest-rank quartiles are 21/38/48.
The bands 1–5, 6–20, 21–40, 41–60, and 61–86 contain 13, 61, 100, 111, and
26 edges, respectively. Per type/side min/median/max are LC4-L 30/53/86,
LC4-R 21/47/67, LPLC2-L 2/28.5/64, and LPLC2-R 1/21/59. These are
descriptive structural statistics only.

### Candidate sample sizes

| Option | Value | Limitation / decision |
| --- | --- | --- |
| 4 bodies | Retains the proven sentinel set and minimal review scope. | Too narrow to exercise body selection, larger sparse inputs, and broader column territories. |
| 16 bodies | Four per type×side stratum; enough to exercise a generalized artifact, balanced routing, and deterministic selection while retaining a small reviewable experiment. | Still exploratory; no biological calibration or population-response claim. **Recommended next scale.** |
| 32 bodies | Eight per type×side stratum; improves descriptive coverage and tests larger artifact/timeline size. | Twice the scope before the 16-body generalized path is verified; adds no sign or efficacy evidence. Defer until 16 passes. |
| 311 bodies | Uses all sensory identities and known direct edges. | Premature: it would scale arbitrary state/transfer assumptions across every sensory neuron and could be mistaken for a validated 313-neuron circuit. Do not run yet. |

For a 16-body experiment, use four predeclared strata—LC4-L, LC4-R,
LPLC2-L, LPLC2-R—with four bodies each. Retain the four Phase 7F bodies as
continuity anchors. Within each stratum, deterministically divide all bodies
into four structural-edge-count quantile bins (ties resolved by body ID),
keep the anchor in its bin, and select one body from each remaining bin. In
each bin, select the body maximizing separation from already selected
anatomical column centroids under the validated relative hex-lattice metric;
break ties by ascending body ID. This is a predeclared structure/coverage
sampling rule, not outcome selection. Report the selected structural counts
as descriptors only. Do not use them in transfer.

The current Phase 7F numerical path is **not yet a generic sample-size
contract**: body IDs, route pairs, and artifact identity are fixed to four
sources. A scale-up should therefore introduce an explicitly versioned,
generalized bounded-sample config/artifact while preserving Phase 7F artifacts
unchanged. Scaling is justified as an architecture/reproducibility experiment,
not a biological response simulation.

## Decisions and remaining limits

- **LC4→DNp01 sign:** `SUPPORTED_POSITIVE`.
- **LPLC2→DNp01 sign:** `SUPPORTED_POSITIVE`.
- **Magnitude:** `NOT_IDENTIFIABLE`; current 7F transfer remains a shared free
  `MODEL_ASSUMPTION` with sensitivity.
- **Structural counts:** routing/anatomy only; never physiological efficacy.
- **Transfer decision:** `SIGN_SUPPORTED_MAGNITUDE_FREE`.
- **Scale decision:** `SCALE_TO_16` as the next bounded architecture experiment.
- **Validation status:** NeuroFly has not empirically validated LC4/LPLC2→DNp01
  transfer. It has evidence-supported pathway sign and a reproducible
  exploratory causal implementation.

Unknowns include per-body presynaptic activity, functional RF and feature
transfer for MaleCNS bodies, source-to-state and state-to-drive observation
operators, pair-specific postsynaptic receptor/kinetic properties,
unitary EPSPs, synaptic conductance/release probability, and actual
LC4/LPLC2→DNp01 efficacy. The Phase 7F sign assumption is not a biological
calibration, and the dimensional simulator drive is not a measured synaptic
potential.

### Phase 7H gate proposal

Generalize the offline Phase 7F artifact/model boundary to one deterministic
16-body sample using the stated strata rule; preserve four sentinel routes;
keep a single shared positive free coefficient and perform sensitivity; prove
exact side/target routing, structural-count invariance, replay, artifact
identity, and deterministic results. Do not add new physiological parameters,
fit to angular-experiment events, add TTMn, or call the output biological
validation.
