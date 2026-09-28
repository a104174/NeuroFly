# Phase 8C — persisted sensory DNp01 events to TTMn adapter

## Result and scope

Phase 8C adds a production, condition-scoped adapter from the immutable Phase
7O result into the unchanged Phase 6C TTMn event integrator. The adapter
accepts only `SIMULATED_DNP01_MODEL_SPIKE` records stored in a validated
Phase 7O artifact. It does not infer events from membrane voltage, external
drive, filtered state, or a second threshold operation. A missing event list
is a valid zero-input result, not a reason to use a Phase 8B fixture.

The composition is:

```text
MaleCNS source contracts
  → persisted Phase 7O artifact
  → explicitly selected Phase 7O condition
  → persisted DNp01 simulated spike records only
  → SIMULATED_FROM_SENSORY_EXPERIMENT adapter
  → existing Phase 6C route mapper and TTMn integrator
  → dimensionless exploratory TTMn state
```

Phase 8B's `SYNTHETIC_MOTOR_INTERFACE_TEST` artifact is not an input or parent
of this chain. The adapter does not construct a `MotorPathwayExperimentResult`
or change Phase 6C's same-upstream-`ExperimentResult` invariant. It uses the
existing Phase 6C pure event mapper and state integrator after the persisted
Phase 7O source, selected condition, identities, and event records have been
revalidated. There is no generic external-event bypass.

## Source artifact and condition boundary

The adapter was generated from Phase 7O artifact
`99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5`
(`sensory_population_311_experiment_artifact_v1`) and the explicit
`reference_bilateral` condition. The source artifact itself is unchanged.
Before extraction, replay checks its content hashes, then compares its pinned
CircuitContract and `body_column_input_v1` identities with locally loaded,
hash-verified source contracts. The Phase 7O condition manifest and result
condition list must agree exactly; condition events are never aggregated.

The persisted Phase 7O spike record contains `body_id`, integer `step`,
`time_ms`, and `SIMULATED_DNP01_MODEL_SPIKE` semantics. The record does not
store `node_index` or `neuron_type`; the adapter resolves those two identity
fields from the same pinned CircuitContract and validates the body and side
against it. It preserves the stored body, step, time, and event semantics.
The source artifact ID and condition ID remain attached to each adapted event.

For every event, validation requires one of the two audited DNp01 body IDs,
the matching source target row/side, the exact event-record schema, a unique
body/step pair, `1 <= step <= interval_count`, and exact
`time_ms == step * dt_ms`. The Phase 6C mapper then validates DNp01 type, body,
node index, step, and event time before routing. An 8B fixture record has a
different schema and provenance and is rejected by the Phase 7O record parser.

## Routing and unchanged model

The pinned Phase 6C evidence contract supplies these identity routes:

| DNp01 source | TTMn target | MaleCNS chemical count |
| --- | --- | ---: |
| 10001 / R / node 0 | 800146 / R | 70 |
| 10010 / L / node 1 | 804642 / L | 20 |

The counts are structural metadata only. They do not scale events, gain, or
state. The adapter reuses the committed `TTMnIntegratorConfig` unchanged:
`tau_motor_ms = 10 ms`, `event_gain = 0.25` dimensionless, and exact
exponential decay followed by event-count input at the same stored boundary.
No additional transmission delay is modeled. The TTMn output is a
dimensionless exploratory neural model state—not voltage, muscle activation,
force, or behavior.

## Canonical zero-event result

The selected Phase 7O `reference_bilateral` run stores no DNp01 spike events.
The result still has positive external DNp01 model drive and subthreshold
membrane movement (10001 peak drive `1.025669 mV_eq`, peak membrane
`-51.962796 mV`; 10010 peak drive `1.410652 mV_eq`, peak membrane
`-51.948753 mV`). Its filtered synaptic state is zero. None of these
non-event quantities is used by the adapter.

Phase 8C therefore records:

- 0 persisted DNp01 event records selected;
- 0 adapted events and 0 mapped Phase 6C event inputs;
- 0 event counts for TTMn 800146/R and 804642/L;
- 15 exact state boundaries (`0.0` through `1.4 ms`) with every state sample
  equal to `0.0` for both TTMn bodies;
- 35/35 Phase 7O conditions with zero DNp01 events in the deterministic audit.

This is the correct causal result for the current sensory experiment. No event
was synthesized, and the Phase 7O event list, sensory parameters, transfer
coefficient, and DNp01 LIF configuration were not changed. A generic future
Phase 7O artifact with genuine persisted events is not hard-coded to zero; a
test-local valid event record verifies identity, step/time preservation, and
routing through the existing Phase 6C primitives.

## Artifact and replay

Schema: `sensory_dnp01_ttmn_adapter_artifact_v1`, with separate config, result,
and manifest hashes. The reference artifact is:

- ID: `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf`
- config SHA-256: `367d4e34ca6e6286e70dda410aa009a8e3828f08f94a22fb710d41bf88d136c5`
- result SHA-256: `a140082b2714f880ea428367608dfe705caf377867781c07900eb2c883284e8a`
- size: 14,986 bytes including manifest
- path: ignored `data/derived/malecns/looming_giant_fiber_v1/sensory_dnp01_ttmn_adapter_v1/<artifact-id>/`

The result persists exact source spike records, adapted body/side/node/type/
step/time records, mapped route inputs, both state trajectories, and a
condition-by-condition event-count/hash audit. Full replay reopens the Phase
7O artifact, revalidates its hashes and local source identities, re-extracts
only the requested condition, reruns the existing Phase 6C primitives, and
requires byte-stable config/result identity. The offline CLI requires an
explicit source artifact and condition for generation and replay:

```bash
python -m neurofly.sensory_dnp01_motor_adapter_cli generate \
  data/derived/malecns/looming_giant_fiber_v1/sensory_population_experiment_311_v1/99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5 \
  reference_bilateral
python -m neurofly.sensory_dnp01_motor_adapter_cli inspect \
  data/derived/malecns/looming_giant_fiber_v1/sensory_dnp01_ttmn_adapter_v1/5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf
python -m neurofly.sensory_dnp01_motor_adapter_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/sensory_dnp01_ttmn_adapter_v1/5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf \
  data/derived/malecns/looming_giant_fiber_v1/sensory_population_experiment_311_v1/99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5 \
  reference_bilateral
```

## Scientific boundary and next gate

MaleCNS provides identities, source contract hashes, and the structural route
evidence. Phase 7O provides exploratory sensory/DNp01 model output and its
simulated event records. `SIMULATED_FROM_SENSORY_EXPERIMENT` identifies the
adapter provenance; it is not biological firing evidence. Phase 6C supplies
an assumed event-to-state rule. The canonical run establishes that a genuine
zero-event upstream result remains zero downstream. It does not establish a
nonzero sensory-driven motor response, GF-to-TTMn physiological efficacy,
TTMn physiology, muscle output, or behavior.

The next bounded step should assess the smallest additional identity-resolved
motor neural branch (PSI/DLMn) against the existing MaleCNS and literature
contracts before implementing dynamics. It must preserve TTMn as a neural
model state and stop before muscle or behavior semantics.
