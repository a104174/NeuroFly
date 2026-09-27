# Phase 8A — DNp01-to-motor interface assessment

**Assessment: `DNp01_SPIKE_EVENT_ONLY`. Next vertical slice:
`SYNTHETIC_EVENT_TO_TTMN_VERTICAL_SLICE`.** This is a read-only architecture
and evidence assessment. No production model, event schema, artifact, API, or
frontend behavior was changed.

Phase 7O established 311 exploratory sensory model states routed into the two
existing DNp01 LIF model readouts. It did not establish sensory physiology,
transfer efficacy, motor output, or behavior. Phase 6C separately established
an event-driven, dimensionless TTMn model-state integrator. There is currently
no production adapter from the Phase 7O artifact schema into the Phase 6C
runner: Phase 6C consumes same-run `ExperimentResult.spike_events`, whereas
Phase 7O stores a separate all-311 artifact with serialized simulated-spike
records.

## Phase 7O DNp01 output contract

The immutable Phase 7O result is
`sensory_population_311_experiment_artifact_v1`, artifact
`99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5`. Its
two target records preserve identity and separate interval inputs, boundary
states, and events:

| Field | Contract | Interpretation |
| --- | --- | --- |
| `body_id`, `side` | DNp01 10001/R and 10010/L | Identity comes from the pinned source contract; the simulation graph uses node indices 0 and 1 respectively. |
| `drive_mveq_by_interval` | One external model-drive value per interval | Phase 7E state routed through the shared Phase 7F assumed transfer; not a measured synaptic current. |
| `membrane_mv_by_boundary` | LIF membrane model state at integer time-grid boundaries | Simulated model state in mV; not a measured GF waveform or a validated biological membrane trace. |
| `filtered_synaptic_mveq_by_boundary` | The LIF simulator's filtered incoming chemical-event state | It is separate from the external-drive path. The Phase 7O two-readout graph has no incoming edges, so this state is zero throughout the persisted run. |
| `simulated_spikes` | Body-specific records with `body_id`, `step`, `time_ms`, and `SIMULATED_DNP01_MODEL_SPIKE` semantics | Model events emitted when the existing LIF threshold rule is crossed. |

The underlying `SpikeEvent` is `(time_ms, step, body_id, node_index,
neuron_type)`. `step` is the integer boundary at which the threshold crossing
is recorded: the simulator evaluates the interval and stores a crossing at
`step = interval + 1`, `time_ms = step * dt_ms`. The Phase 7O reference
configuration uses `lif_filtered_synapse/phase2b_v1`, `dt_ms=0.1`,
`tau_m_ms=20`, `tau_s_ms=5`, rest/reset `−52 mV`, threshold `−45 mV`,
refractory `2.2 ms`, and the existing configured delay `1.8 ms`. The
Phase 7O graph is a two-readout graph with no chemical edges; its continuous
external-drive path is kept distinct from filtered chemical state.
Its positive sensory-to-DNp01 direction is explicitly identified by the
existing `direct_visual_dnp01_depolarizing_assumption_v1` sign policy; that
policy is a model assumption and does not constitute a measured sign/gain for
each MaleCNS sensory connection. Phase 8A does not alter it.

In the persisted `reference_bilateral` condition, DNp01 10001 has peak drive
1.025669 mV-equivalent and membrane range `−52` to `−51.962796 mV`; DNp01
10010 has peak drive 1.410652 mV-equivalent and membrane range `−52` to
`−51.948753 mV`. Both have zero filtered synaptic state and zero simulated
spikes. The persisted artifact has no DNp01 spikes in any of its 35
conditions; the tested transfer values `k=0, 1, 2` produce none. This is the
observed result under those assumptions, not a defect. No parameter or
stimulus was changed to force an event.

## Phase 6C motor input contract

Phase 6C's `MotorPathwayExperimentRunner` runs one upstream `ExperimentRunner`
result, selects only its exact DNp01 `SpikeEvent` objects, validates them,
and maps them through the pinned
`malecns_dnp01_ttmn_evidence_v1` contract. It does not accept voltage, filtered
state, sensory drive, or an unprovenanced event count as input.

The source-derived routes are:

| DNp01 source | TTMn target | MaleCNS chemical `ConnectsTo` count |
| --- | --- | ---: |
| 10001/R | 800146/R | 70 |
| 10010/L | 804642/L | 20 |

The edge counts are chemical structural metadata only. The evidence contract
separately records literature-supported electrical coupling and mixed
connections, but pair-specific electrical strength and a combined mixed
weight are null. The counts 70 and 20 are not used in the event mapping's
numerical update or as a gain.

For each mapped event, Phase 6C verifies neuron type, source body ID, source
graph node index, integer step, and `time_ms == step * dt_ms` (within its
declared representation tolerance). It validates the target body from the
contract rather than inferring it from side or array position. The event is
delivered to the TTMn model at the same stored boundary, with no additional
modeled transmission delay. On boundary `n`, the recurrence is:

```text
x[n] = x[n−1] * exp(−dt_ms / tau_motor_ms)
       + event_count[n] * event_gain
```

The reference is `ttmn_dimensionless_event_integrator/phase6c_v1`, with
`tau_motor_ms=10 ms` and `event_gain=0.25` dimensionless; both are
`MODEL_ASSUMPTION`. The output is a dimensionless exploratory TTMn model
state, not membrane voltage, a biological TTMn spike, muscle activation,
force, jump, takeoff, or escape. With zero events and initial state zero,
the state remains zero. The implementation requires a positive increment;
that is the model's state-update convention, not a measured TTMn voltage
response or an efficacy value inferred from MaleCNS edge counts.

## Biological evidence and limits

The primary literature supports a fast GF-to-motor pathway and an event-based
model boundary, but does not identify the current model's numerical transfer
parameters:

| Evidence class | Relevant evidence | What it does not establish here |
| --- | --- | --- |
| Anatomy | King & Wyman describe each giant fibre contacting an ipsilateral large motor axon and an interneuron; the interneuron participates in the flight-muscle branch. | Not a trace of the current MaleCNS specimen or a physiological transfer value. |
| Electrical / mixed transmission | Phelan et al. link Shaking-B to electrical synapse formation and GF-system function. Allen & Murphey show functional electrical and chemical components at the adult GF–TTMn mixed synapse; the chemical component is cholinergic and can support a delayed residual response when the electrical component is disrupted. | Does not make a DNp01 model spike equivalent to a measured TTMn response, and does not supply a pair-specific MaleCNS coupling coefficient. An event-only integrator is a bounded abstraction of the fast route, not a complete mixed-synapse mechanism. |
| Electrophysiology / timing | Tanouye & Wyman electrically stimulated the GF, recorded its axon intracellularly, and found that a single GF spike drives short, constant-latency TTM and DLM muscle potentials. Augustin et al. (2017) measured age- and condition-dependent brain-stimulation-to-muscle response latency. | These are pathway/muscle endpoints, not DNp01-to-TTMn continuous-voltage transfer measurements or a Phase 6C state time constant. |
| Computational fit | Augustin, Zylbertal & Partridge (2019) model a multi-cell, conductance-based pathway and use estimated/fitted gap-junction conductance settings to reproduce published end-to-end latency observations. | The reported fit parameters (including 135 and 34.5 µS settings) are not direct MaleCNS pair measurements and must not be imported as NeuroFly coupling values. |

Primary references: [King & Wyman (1980)](https://doi.org/10.1007/BF01205017),
[Tanouye & Wyman (1980)](https://doi.org/10.1152/jn.1980.44.2.405),
[Phelan et al. (1996)](https://doi.org/10.1523/JNEUROSCI.16-03-01101.1996),
[Allen & Murphey (2007)](https://doi.org/10.1111/j.1460-9568.2007.05686.x),
[Augustin et al. (2017)](https://doi.org/10.1371/journal.pbio.2001655), and
[Augustin, Zylbertal & Partridge (2019)](https://doi.org/10.1523/ENEURO.0423-18.2019).
This assessment uses these studies as anatomy, mechanism, pathway-output, or
model-fit evidence according to their actual endpoints; it does not conflate
those categories.

## Interface options

### A. DNp01 spike/event only — selected

This matches the actual Phase 6C API, preserves the existing LIF event
threshold semantics, and avoids inventing a voltage-to-TTMn conversion. Its
current sensory limitation is real but acceptable: Phase 7O emits no DNp01
event, therefore an event-only connection would deliver no TTMn input and
leave both zero-initialized TTMn model states at zero. That is a valid
zero-input result, not a reason to retune the sensory transfer or lower the
DNp01 threshold.

The existing motor runner is not itself a direct Phase 7O artifact adapter:
Phase 6C requires same-run `ExperimentResult.spike_events`, while Phase 7O
persists its own result schema. A future sensory-origin path must preserve
provenance and must only emit events actually present in the Phase 7O result.
It must not synthesize an event to make the real sensory run appear to drive
the motor path.

### B. Continuous DNp01 membrane — not selected

The Phase 7O `membrane_mv` is a model state, but no observation operator maps
that point-neuron trace to a biological GF terminal waveform or TTMn input.
The biological electrical junction makes continuous waveform transmission a
plausible mechanism for a future conductance-based model; it does not justify
directly reusing the current LIF voltage as TTMn drive. Doing so would bypass
the existing event abstraction and require new, presently unidentified
coupling and target-state semantics. The published detailed model does not
make those quantities available for the exact MaleCNS pairs.

### C. Filtered DNp01 state — not selected

The Phase 7O filtered synaptic state is zero because its readout graph receives
the exploratory sensory signal through external drive, not chemical edges.
That state does not encode the Phase 7O sensory signal or the missing
GF–TTMn electrical component. Routing it would repurpose an unrelated zero
state; making it nonzero would require changing upstream semantics.

### D. Synthetic motor-interface event — recommended test strategy

Keep Phase 7O as-is and validate the motor path separately with an explicitly
synthetic DNp01 event. This can test body/target identity, boundary timing,
state integration, artifact replay, and causal zero-event controls without
claiming that the sensory experiment produced the event. Synthetic and
sensory-derived provenance must be distinct, for example
`SYNTHETIC_MOTOR_INTERFACE_TEST` versus
`SIMULATED_FROM_SENSORY_EXPERIMENT`.

The current Phase 6C result constructor intentionally requires its source
events to equal events from its attached upstream run. A future test should
therefore use a separately versioned event-fixture/adapter contract (for
example, a `dnp01_motor_event_v1` input record) rather than weakening that
same-run invariant. Candidate record fields include source artifact, source
body ID, side, integer event step/time, event model/version, provenance class,
and contract-derived TTMn target. This is a design proposal, not implemented
in Phase 8A.

## Circuit scope and next boundary

The TTMn-only slice is appropriate for validating the narrow direct
DNp01/GF-event-to-TTMn model-state interface. PSI/DLMn are not needed for that
test. They are needed for a broader representation of the GF-to-flight branch
and its interactions; adding them would introduce another mixed GF–PSI
interface and a chemical PSI–DLMn interface, with additional unresolved
parameters. TTMn state alone remains a bounded motor-neural slice, not the
complete GFS or an escape decision.

The future contract must keep these separate:

- **DNp01 model event:** a threshold event emitted by a named model run, or an
  explicitly synthetic interface-test event.
- **TTMn exploratory model state:** the dimensionless Phase 6C integrator
  output, retaining TTMn body ID and side.
- **Not represented:** biological TTMn voltage/spikes, muscle state, force,
  body motion, escape probability, or behavior.

No motor event should be inferred from subthreshold `membrane_mv`, the
filtered-synapse state, Phase 7E sensory state, or a structural count. No LLM
is part of the neural/motor path.

## Phase 8A boundary and decision

- **Source evidence:** MaleCNS body IDs, side, and chemical structural routes;
  literature-supported electrical/mixed GF–TTMn mechanism.
- **Model assumptions:** Phase 7E/7F sensory-to-DNp01 transfer; existing
  DNp01 LIF parameters; Phase 6C same-boundary event convention, `tau_motor`,
  and `event_gain`.
- **Model outputs:** Phase 7O DNp01 membrane/event records and Phase 6C
  dimensionless TTMn state.
- **Unknown:** pair-specific electrical coupling, continuous biological GF
  waveform at the junction, equivalent TTMn response observation, and
  physiological Phase 6C parameter values.

**Interface decision:** `DNp01_SPIKE_EVENT_ONLY`.

**Next vertical-slice decision:** `SYNTHETIC_EVENT_TO_TTMN_VERTICAL_SLICE`.
Phase 8B should implement only a provenance-separated synthetic event fixture
through the existing body-specific event mapping and TTMn state integrator.
It should not connect Phase 7O directly while that experiment has no events,
change sensory or DNp01 parameters, add PSI/DLMn, or propagate into muscle or
behavior.
