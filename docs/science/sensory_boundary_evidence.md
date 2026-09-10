# Phase 1C — sensory boundary evidence and looming benchmark

This document defines the evidence boundary for a future NeuroFly sensory
encoder. It does not claim that NeuroFly currently simulates vision, looming,
neural dynamics, or escape behavior.

## Evidence base

### Klapoetke et al. (2017), Nature

[*Ultra-selective looming detection from radial motion opponency*](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457385/), DOI
[`10.1038/nature24626`](https://doi.org/10.1038/nature24626), establishes that
individual LPLC2 neurons are local looming detectors. Their dendritic fields
form a four-arm arrangement aligned with directionally selective lobula-plate
inputs; individual receptive fields tile visual space with overlap. In the
reported experiments, LPLC2 responded strongly to focal outward expansion but
not to dark receding looming, motion-free darkening, or wide-field motion. The
paper also reports an upper bound of about 60° for an individual receptive
field and maps single-cell receptive-field centers with a dense visual grid.

This establishes a biological and experimental organization to test. It does
not provide a lookup from the 313 MaleCNS `body_id` values to visual-field
coordinates, nor does it justify assigning one identical scalar to every
MaleCNS LPLC2 neuron. Its imaging preparations and source data are not the
NeuroFly `male-cns:v1.0` snapshot.

### Ache et al. (2019), Current Biology

[*Neural Basis for Looming Size and Velocity Encoding in the Drosophila Giant
Fiber Escape Pathway*](https://www.sciencedirect.com/science/article/pii/S0960982219301381), DOI
[`10.1016/j.cub.2019.01.079`](https://doi.org/10.1016/j.cub.2019.01.079), reports
that LPLC2 and LC4 are direct visual inputs to the Giant Fiber (GF; DNp01 in
the NeuroFly candidate). The experiments associate the LPLC2→GF component with
looming angular size and the LC4→GF component with angular velocity. LPLC2
silencing removes the size component of the recorded GF response, and the
authors show that a combined model of size and velocity reproduces the observed
GF response dynamics. The combined response is therefore a benchmark for
future evaluation; it is not a rule that has been implemented here.

The paper's electrophysiology, perturbations, and EM reconstruction are
published experimental evidence, not MaleCNS v1.0 records. It does not supply
NeuroFly's per-body receptive-field coordinates or choose NeuroFly's future
neural equations, input amplitudes, signs, or motor mapping.

### Moreno-Sanchez et al. (2024), eLife

[*Morphology and synapse topography optimize linear encoding of synapse numbers
in Drosophila looming responsive descending neurons*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11071487/), DOI
[`10.7554/eLife.99277`](https://doi.org/10.7554/eLife.99277), uses the FAFB
electron-microscopy dataset and morphology-based analyses of visual projection
neuron inputs and descending neurons. It provides a plausible methodology for
relating morphology and synapse locations to dendritic organization and reports
that VPN synapses onto descending neurons do not form a simple retinotopic map
along the DN dendrites, despite retinotopic organization in VPN arbors.

FAFB is not MaleCNS. The study's coordinates, cell identities, skeletons, and
synapse locations must not be copied into the NeuroFly snapshot. Its methods
can inform a future MaleCNS feasibility study only after dataset-specific
retrieval and coordinate registration.

## Model-neutral looming stimulus

The executable specification in `neurofly.malecns.sensory` represents a
spherical/disk object approaching an observer on a straight line of sight.
All units are explicit:

- `object_radius_m`: physical radius (metres), strictly positive;
- `approach_velocity_m_s`: signed line-of-sight velocity (metres/second),
  positive toward the observer, negative when receding;
- `initial_distance_m`: distance at time zero (metres), strictly positive;
- `center.azimuth_rad`, `center.elevation_rad`: visual center (radians);
- `time_s`: non-negative time (seconds);
- `angular_size_rad`: full angular diameter (radians);
- `angular_expansion_velocity_rad_s`: signed time derivative of angular size
  (radians/second), before collision.

For pre-collision time, with `r` the radius, `d₀` the initial distance, and
`v` the signed approach velocity:

```text
d(t) = d₀ − v t
θ(t) = 2 atan2(r, d(t))
dθ/dt = 2 r v / (d(t)² + r²)
```

For `v > 0`, time to collision is `d₀ / v`. At and after that time the
specification returns an explicit terminal state (`distance_m = 0`,
`angular_size_rad = π`, `collided = true`) and leaves post-collision angular
expansion undefined (`None`). For `v = 0`, there is no collision and expansion
is zero. For `v < 0`, there is no collision and expansion is negative. Invalid
or non-finite physical parameters and negative times are rejected. Off-center
stimuli are represented by their visual center and are not silently moved to
the optical axis.

These variables remain visual/physical descriptors. They are not currents,
spikes, rates, membrane potentials, or actions.

## Benchmark specification

The executable `BENCHMARKS` constant records three future evaluation targets:

1. **LPLC2 localized outward selectivity:** compare focal dark looming with
   receding, motion-free darkening, wide-field translation, and contraction
   controls. The expected result is qualitative selectivity, not an invented
   amplitude threshold.
2. **LC4/LPLC2 feature separation:** compare angular-velocity and angular-size
   conditions, including pathway-isolated controls, while preserving the
   distinction as published feature evidence rather than a per-cell encoder.
3. **DNp01/GF combined integration:** compare LC4-only, LPLC2-only, and combined
   conditions. Evaluate the combined response against the reported integration
   phenomenon, including the supralinear target described by Ache et al.; do not
   implement supralinearity in Phase 1C.

The benchmark vocabulary does not assign synaptic signs, structural-weight
scales, model time steps, or behavioural actions. A future population-level
approximation must state that it discards individual receptive-field centers,
tiling/overlap, directional tuning, and cell-to-cell heterogeneity.

## MaleCNS mapping feasibility and decision

The local Phase 1B snapshot contains normalized annotations and chemical body-
level connectivity only. It does not contain skeleton morphology, dendritic
coordinates, synapse coordinates, optic-lobe ROI assignments, or a registered
visual reference frame. `soma_side` is an annotation, not a visual-field
coordinate, and body-ID/order is not spatial evidence. Credentials were absent
during this phase, so no live morphology query was made and no morphology was
downloaded.

**Decision: Option B — per-neuron spatial mapping is not yet defensible.**

The smallest defensible first sensory boundary is therefore a documented,
population-level feature vocabulary: looming geometry exposes angular size and
angular expansion velocity, while the literature associates those features
with the LPLC2 and LC4 pathways respectively. If a future NeuroFly encoder uses
that simplification, it must be labelled a NeuroFly modelling approximation,
not MaleCNS metadata or a per-cell biological map. It necessarily discards
LPLC2 receptive-field tiling and overlap, local outward-motion structure,
individual LC4/LPLC2 spatial organization, and any dataset-specific
laterality/heterogeneity.

The next smallest phase is a bounded MaleCNS morphology feasibility study—not
full 311-cell acquisition—with a deterministic several-per-side LC4/LPLC2
sample. It must establish dendritic/ROI consistency, a coordinate/reference
transform, and a validation plan before any per-body receptive-field mapping is
implemented. It must not transfer FAFB/FlyWire identities or coordinates.

The known electrical/gap-junction contributions in downstream Giant Fiber
circuitry remain outside this chemical-connectome sensory boundary.
