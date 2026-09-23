# Validated activity-to-structure mapping (Phase 6A)

Phase 6A adds a read-only presentation mapping from the persisted
`looming_giant_fiber_v1` experiment to the existing six-body MaleCNS
morphology/connectivity view. It adds no scientific artifact and does not
change the experiment, raw morphology, CircuitContract, structural weights,
simulation, or playback clock. The current experiment remains
`NOT_EVALUATED`; this mapping is not empirical calibration.

## Persisted signal audit

The audit uses experiment artifact
`63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656`, dataset
`male-cns:v1.0`, candidate `looming_giant_fiber_v1` v1, and the persisted
`experiment_artifact_v1` configuration/result validated by the local artifact
loader.

| API source field | Granularity | Unit | Stored time semantics | Identity evidence |
| --- | --- | --- | --- | --- |
| `theta_rad` | GLOBAL stimulus | rad | interval value on `[t_n,t_n+dt)` | One artifact-level stimulus series |
| `angular_expansion_velocity_rad_s` | GLOBAL stimulus | rad/s | interval value on `[t_n,t_n+dt)` | One artifact-level stimulus series |
| `lc4_drive_mveq` | TYPE_LEVEL encoder output | mV_eq | interval value on `[t_n,t_n+dt)` | Persisted encoder ID/version and `bilateral_type_broadcast_v1` population mapping |
| `lplc2_drive_mveq` | TYPE_LEVEL encoder output | mV_eq | interval value on `[t_n,t_n+dt)` | Persisted encoder ID/version and `bilateral_type_broadcast_v1` population mapping |
| `membrane_mv` | BODY_SPECIFIC DNp01 point-neuron model state | mV | exact stored boundary | Telemetry record body ID, type, and source side, joined to the validated CircuitContract sample |
| `synaptic_state_mveq` | BODY_SPECIFIC DNp01 point-neuron model state | mV_eq | exact stored boundary | Same validated body-keyed telemetry record |
| persisted spike event / `spike_times_ms` | EVENT | ms | exact persisted event boundary/step | Event body ID, node index, neuron type, timestamp, and step; body record also retains spike times |

The timeline has 800 intervals and 801 state boundaries (`dt_ms=0.1`, 0–80
ms). The API's selected body telemetry contains only DNp01 10001 and 10010;
there is no body-specific LC4/LPLC2 drive or state in this artifact. Encoder
drives are therefore never colored onto or apportioned among the four sensory
morphologies.

## Identity validation

Before body state is eligible for morphology presentation, the activity view
checks that the experiment and timeline artifact IDs match, the dataset and
candidate are the pinned run, the experiment's two CircuitContract file hashes
match the pinned Phase 5I hashes, and the connectivity payload reports verified
hashes/record counts plus the exact fixed projection and six-body set. It then
checks the Contract identities:

| Body | node_index | Type | Contract source side |
| ---: | ---: | --- | --- |
| 10001 | 0 | DNp01 | R |
| 10010 | 1 | DNp01 | L |

Body telemetry is keyed by body ID and must agree on type, side, exact boundary
array, lengths, and stored spike times. The node index is taken from the
validated CircuitContract identity, not telemetry array position, morphology
coordinates, or a frontend array-order guess. Wrong provenance, incomplete or
duplicate identities, incompatible summaries, or malformed times fail closed
for BODY_SPECIFIC projection. Type-level encoder values are independently
gated by the persisted encoder ID/version and population mapping.

## Derived activity contract

`web/src/lib/activityStructure.ts` defines two discriminated source states:

- `TYPE_LEVEL`: neuron type, persisted drive field/value, and interval bounds;
  it intentionally has no body ID.
- `BODY_SPECIFIC`: validated DNp01 body ID, Contract node index/type/side,
  boundary time, exact membrane and filtered state, optional normalized model
  presentation value, and exact stored spike-at-boundary state.

When a sensory body is selected, the panel can show its type-level drive as
context, labelled `TYPE-LEVEL`, and says that the artifact has no
body-specific trace. The body-to-overlay helper emits only the two validated
DNp01 body states. It cannot distribute type-level drive to LC4/LPLC2 bodies.
An unknown encoder mapping yields no type-level display. If CircuitContract
identity is unavailable, body-specific projection is omitted while the raw
morphology remains inspectable. If model references/model identity are not
valid, exact membrane and filtered values/events remain available, but visual
normalization is omitted.

The read-only experiment summary now exposes the persisted encoder population
mapping and the run's membrane rest/threshold references. These are loaded
from the validated run configuration; they do not alter its identity.

## Body-level membrane presentation

The persisted model configuration identifies `lif_filtered_synapse`
`phase2b_v1`, with `V_rest=-52 mV` and `V_threshold=-45 mV`. Only for this exact
model/version and a valid range, the view derives:

```text
p = clamp((V_m - V_rest) / (V_threshold - V_rest), 0, 1)
```

The value is labelled **normalized model membrane position**. It is not an
activation percentage, firing probability, biological voltage measurement, or
likelihood of behavior. The cockpit may render a restrained, constant-color
secondary line overlay whose opacity is `0.36 * p`, further multiplied by the
existing presentation selection opacity. It reuses the same transformed raw
component positions; it does not change source coordinates, node/link
topology, component identity, shared transform, or base type/body color. The
text readout keeps exact membrane `mV` and filtered
`mV_eq` authoritative. The overlay toggle is presentation state, defaults on
in the experiment cockpit, and does not hide the source skeleton. The
standalone morphology inspector receives no activity context and stays
structural-only.

DNp01 is a point-neuron model. Its one body-level model value is shown uniformly
over that body's morphology solely to associate a point-neuron state with its
source identity. It is not spatially resolved voltage along neurites, a
compartment model, local current, or dendritic/axonal propagation.

## Spike events and playback

Spike indication uses the persisted event/body spike-time records, not
threshold-testing a rendered trace. The Phase 5I-validated body identity
provides the corresponding node index. A spike is indicated only at its exact
selected stored boundary; the event log, selected-neuron readout, and body
state projection use the same event/body/time. No arbitrary flash decay,
propagation trail, pulse, or moving marker is added.

The existing canonical experiment playback clock remains the sole time source.
Type-level drive uses the established floor-selected interval; membrane and
filtered state use the exact floor-selected stored boundary; spikes use exact
stored timestamps. Scientific values are not interpolated or extrapolated.
Play, pause, reset, event seek, timeline seek, and rate control only change the
existing playback time. Rendering FPS and Three.js clocks do not drive this
mapping, and no API request occurs on a playback tick.

## Structural and scientific boundaries

The four Phase 5I LC4/LPLC2 → DNp01 structural edges, source direction,
structural weights, schematic connector endpoints/path, and fixed line-width
semantics remain static. No drive or weight is applied to connectors; no
edge-specific dynamic state or synapse coordinates exist. LPLC2 body 11498
retains its 9-node and 2,112-node disconnected raw components; neither gets
body- or component-level sensory activity.

Source data are MaleCNS morphology and CircuitContract identities/edges.
Simulated results are the persisted encoder values, point-neuron state, and
spike events. Color, opacity, overlay visibility, selection, and camera remain
presentation state. This phase makes the mapping explicit; it does not improve
the underlying model's biological validity.

Not represented: empirical calibration, measured neural activity,
body-specific LC4/LPLC2 state, local/compartment voltage, edge-specific
current, synapse-level activity, action-potential propagation, full-connectome
activity, motor behavior, or activity in the fly visual asset.
