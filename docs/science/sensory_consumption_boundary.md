# Phase 1F — sensory-consumption boundary specification

**Status:** specification only; no sensory encoder, neural simulator, or
experiment runtime is implemented.

NeuroFly now has two validated structural products: the offline
`CircuitContract` for the selected MaleCNS chemical graph and the separate
`BodyColumnInputContract` for body-specific optic-column input topology. Phase
1D/1E classified LC4 and LPLC2 as D3: column topology is reproducible, but no
provenance-verified bilateral `male-cns:v1.0` transform from optic-column IDs
to angular visual coordinates is available.

The current sensory boundary is therefore a population feature approximation.
Column-space metadata is preserved for a future, more spatially detailed mode;
it is not silently converted into visual angles or physiological input.

## Boundary diagram

```text
environment / stimulus state
        │  physical and visual descriptors
        ▼
future sensory encoder
        │  NeuroFly modelling assumptions
        │  produces neutral model-facing external_drive records
        ▼
future neural simulator
        │  selected state equations and coupling assumptions
        ▼
future neural outputs
        ▼
future motor / behaviour mapping → environment
```

Structural MaleCNS data are consulted by the future encoder as biological
context; they are not an implicit arrow from the environment into neuron state.
A renderer may display the environment, but it must not mutate neural state.
Rendering frame rate and a future simulation tick are independent concerns.

## Four ownership layers

| Layer | Owns | Does not own |
| --- | --- | --- |
| **Environment / stimulus state** | Object radius, distance, approach velocity, time, stimulus center, angular size, and angular expansion velocity. | MaleCNS identity, synapse counts, neural amplitudes, or neuron state. |
| **Sensory encoder** *(future)* | Feature scaling, spatial overlap, gain, normalization, population broadcast, temporal filtering, and any mapping from an observation to model-facing input. | Biological claims that are not supported by the selected evidence and the structural records themselves. |
| **Biological structural data** | `CircuitContract` body IDs, annotations, chemical `ConnectsTo.weight`, `BodyColumnInputContract` topology, and neurotransmitter annotations. | Input amplitude, receptor sensitivity, neural sign, firing rate, membrane state, or behaviour. |
| **Neural simulator** *(future)* | State equations, timestep, thresholds, time constants, physiological coupling, delays, and neural state updates. | Environment geometry, visual-angle calibration, or an assumption that structural counts are already physiological values. |

The `LoomingStimulus`/`LoomingSample` fields are model/world descriptors. In
particular, `center.azimuth_rad` and `center.elevation_rad` describe the
stimulus specification; they do not locate a MaleCNS body or column.

## Level P — population feature mode

Level P is the only currently operationally justified sensory boundary for an
early neural-model experiment. It is a NeuroFly modelling approximation,
informed by the Phase 1C literature, not MaleCNS metadata and not an
individual-neuron receptive-field model.

```text
looming stimulus
    → angular_size_rad and angular_expansion_velocity_rad_s
    → explicit NeuroFly population-feature assumption
    → LC4/LPLC2 model-facing external_drive records
```

The documented population associations are:

- LC4 population ↔ angular-expansion-velocity-related feature;
- LPLC2 population ↔ angular-size-related feature.

The approximation may broadcast or otherwise assign a feature to all neurons
of a selected type only when that choice is explicitly recorded as an encoder
assumption. The existing repository does not implement that broadcast or any
neural dynamics.

Level P is useful because it is immediately testable against the Phase 1C
looming vocabulary and published qualitative pathway evidence. It loses:

- each body's column distribution and neuropil contribution;
- individual visual-space centers, tiling, and overlap;
- local outward-motion structure and directional tuning;
- body-to-body heterogeneity, laterality, and missing assignments;
- any validated mapping from a world-object position to a particular body;
- any basis for claiming spatially accurate per-neuron looming encoding.

Consequently, Level P results must be described as population-feature model
experiments, not as a reconstruction of individual MaleCNS receptive fields.

## Level C — column-space mode

Level C retains the body-specific topology available in the Phase 1E artifact:

```text
body_id
    → neuropil
    → eye_side
    → ol_hex1, ol_hex2
    → postsynaptic input-site count
```

This supports future reasoning about relative column-space topology. It does
not provide neural sensitivity or an environment-to-column projection:

- `input_count` is a postsynaptic input-site count, not sensitivity, gain, or
  neural drive;
- column occupancy is not firing rate or activation;
- a column centroid is not a receptive-field center;
- `ol_hex1`/`ol_hex2` are not azimuth/elevation or visual degrees;
- identical hex pairs in different neuropils must remain distinct;
- no validated world-object → MaleCNS column mapping currently exists.

Level C is therefore **disabled/not operational**. It must not be presented as
spatially calibrated vision until a separate modelling contract defines the
environment projection and validates its provenance. No rendered figure, SVG,
or cross-dataset coordinate system may be reverse-engineered to fill this gap.

| Capability | Status | Scientific claim allowed |
| --- | --- | --- |
| **P — population features** | Available as an explicitly labelled future encoder assumption | Population-level feature comparison against the Phase 1C benchmark vocabulary. |
| **C — column space** | Preserved but disabled | Body-specific structural topology in MaleCNS column space only. |

## Future model-facing input boundary

The future neural simulator should consume a small neutral record produced by a
sensory encoder, conceptually:

```text
simulation_time or simulation_step
body_id (or an explicitly named population target)
external_drive
input_channel / source
encoder_id
encoder_version
```

This is a documentation proposal, not a production type. `external_drive` is
deliberately neutral: its units and semantics must be defined jointly by the
selected encoder and neural model. It must not be called a current, firing
rate, conductance, probability, or synaptic weight until a future model
explicitly gives it that meaning.

The simulator must not need to know whether a record came from Level P,
column-space projection, or a future validated visual-angle mapping. The
encoder owns that provenance and its assumptions; the simulator owns only the
chosen neural dynamics. A future body-specific encoder may consult the
`BodyColumnInputContract`, but it must not mutate that biological data product.

## DNp01 and structural boundaries

Environmental sensory input enters the selected LC4/LPLC2 boundary. DNp01
receives no fabricated direct environmental sensory input. In a future
connectome-driven experiment it receives activity through the simulated
candidate graph, except where a benchmark explicitly declares a clamp or
injection as an experimental intervention rather than sensory biology.

The following distinctions remain invariant:

```text
ConnectsTo.weight / structural_weight
    ≠ sensory drive
    ≠ neural coupling
    ≠ physiological synaptic efficacy

BodyColumnInputContract.input_count
    ≠ neural coupling
    ≠ receptor sensitivity
    ≠ neural drive
```

`predicted_nt` and `consensus_nt` remain biological annotations. Phase 1F does
not convert acetylcholine, GABA, glutamate, or any other annotation into an
excitatory/inhibitory sign. Receptor, sign, coupling, and dynamics decisions
belong to a later evidence-based neural-model phase.

## Reproducibility metadata for future runs

Any future sensory/neural experiment should record at least:

- candidate circuit identifier and version;
- MaleCNS dataset version;
- CircuitContract schema/integrity information and source snapshot;
- BodyColumnInputContract schema/version and artifact hash when Level C is
  referenced;
- sensory level (`P` or `C`), mode identifier, encoder identifier, and encoder
  version;
- complete encoder parameters, including scaling, gain, normalization,
  broadcast, spatial, and temporal assumptions;
- complete stimulus parameters and sampled stimulus state;
- random seed and stochastic-policy/version information, if applicable;
- neural-model identifier/version and its declared input units/semantics.

This is a provenance requirement, not an experiment framework implementation.

## Relation to Phase 1C benchmarks

Future models should remain evaluable under the existing model-neutral
conditions:

- looming and receding;
- contraction where supported;
- motion-free darkening;
- wide-field translation;
- LC4-isolated contribution;
- LPLC2-isolated contribution;
- combined LC4+LPLC2 condition.

These conditions test qualitative feature separation and combined integration
without inventing firing rates, thresholds, amplitudes, or expected motor
responses. Level P can be used for an initial model study; Level C can become a
later spatial comparison only after its projection contract is designed and
validated.

## Phase 2 readiness decision

**Decision: YES — neural-model research may begin using Level P.**

This does not mean the sensory system is complete. Phase 2 can investigate
candidate neural equations because:

1. the population approximation is explicitly labelled and its assumptions are
   owned by a future encoder;
2. the CircuitContract and candidate structural graph are integrity-validated;
3. the richer 311-body column topology is preserved rather than discarded from
   the data products; and
4. the Phase 1C benchmark conditions define comparisons without requiring an
   invented angular receptive-field transform.

The limitations carried forward are explicit: Level P is not body-specific,
Level C is disabled, no bilateral column-to-angle transform is available, and
structural counts and annotations do not determine physiological dynamics.
Beginning Phase 2 must not be interpreted as claiming calibrated visual-angle
vision or a complete biological simulation.

## Explicit non-goals

Phase 1F adds no encoder, body or column activation, visual-angle transform,
receptive-field center, firing rate, current, spike, membrane state, LIF/rate
model, synaptic delay, neurotransmitter sign, structural-weight scaling,
behaviour, renderer, API, database, runtime loop, or telemetry.
