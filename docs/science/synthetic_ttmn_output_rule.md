# Phase 8N — TTMn exploratory threshold-crossing output rule

**Status:** bounded synthetic model extension; the output is uncalibrated and
is not a biological TTMn action potential. The implementation adds an output
operator over validated Phase 8B trajectories. It does not change or duplicate
the Phase 6C state equation.

## Source TTMn model and boundary

Phase 6C uses `ttmn_dimensionless_event_integrator/phase6c_v1` with reference
assumptions `tau_motor_ms = 10.0` and `event_gain = 0.25`. Its state is
dimensionless and follows the stored-boundary update

```text
x[n] = x[n-1] * exp(-dt_ms / tau_motor_ms)
       + event_count[n] * event_gain
```

The state is not membrane voltage, firing probability/rate, calcium,
neurotransmitter release, muscle activation, or a spike state. Both parameters
remain Phase 6C `MODEL_ASSUMPTION`s. Phase 8N reads the exact trajectories from
the canonical Phase 8B artifact and validates/replays that child before
processing it; it stores trajectory hashes rather than a second copy of all
samples.

Only the two pinned TTMn identities are authorized: body `800146` / R and body
`804642` / L. DNp01 identities, DLMn bodies, and Phase 8G route receipts are not
accepted as output-generator input.

## Generator and threshold assumption

The generator is `TTMN_THRESHOLD_CROSSING_V1`. Its pinned reference setting is
`threshold_dimensionless = 0.25`, explicitly classified as
`MODEL_ASSUMPTION`. This is an uncalibrated operator/test value, not a measured
TTMn firing threshold and not a voltage. It was not fitted to obtain an output.
Its equality with Phase 6C's `event_gain = 0.25` is incidental: the two are
separate config values, and changing the threshold changes generator identity
without changing the source model configuration or trajectory.

At integer state boundary `n`, the rule emits one record exactly when

```text
x[n-1] < threshold_dimensionless <= x[n]
```

Thus equality at the new boundary counts. The timestamp is the exact stored
`step` and `time_ms` of the first qualifying boundary; there is no interpolation
or added delay. This is model timing, not measured spike timing, axonal
propagation, synaptic delay, or neuromuscular delay. The rule is upward-edge
triggered: remaining above threshold emits nothing further, downward decay
does not emit, and another crossing is possible only after a stored value is
below threshold. There is no refractory parameter.

## Reference fixtures and threshold sensitivity

The six Phase 8B fixtures and their Phase 6C trajectories are unchanged.
At the reference threshold, the output records are:

| Fixture | Model-derived TTMn output records |
| --- | --- |
| `ZERO_EVENT_CONTROL` | 0 |
| `RIGHT_SINGLE_EVENT` | body 800146 / R at step 10, 1.0 ms (1) |
| `LEFT_SINGLE_EVENT` | body 804642 / L at step 10, 1.0 ms (1) |
| `BILATERAL_SIMULTANEOUS_EVENT` | bodies 800146 / R and 804642 / L at step 10, 1.0 ms (2) |
| `RIGHT_REPEATED_EVENTS` | body 800146 / R at steps 10 and 30 (2) |
| `LEFT_REPEATED_EVENTS` | body 804642 / L at steps 10 and 30 (2) |

The bounded sensitivity probes are operator-behavior checks, not candidate
biological parameters:

| Dimensionless threshold | Total records across the six fixtures | Illustrative result |
| ---: | ---: | --- |
| 0.20 | 6 | Each repeated trajectory crosses once at step 10; it remains above 0.20 before the second input boundary. |
| 0.25 | 8 | Equality at step 10 counts; repeated trajectories re-cross at step 30 after dropping below 0.25. |
| 0.30 | 2 | Single-event trajectories do not reach threshold; each repeated trajectory crosses at step 30. |
| 0.50 | 0 | No canonical trajectory reaches threshold. |

The input TTMn trajectories are identical across all threshold settings. Each
threshold has a distinct generator-config hash, and event identity includes
that config identity.

## Output event and provenance

The shared envelope schema is `motor_neuron_output_event_v1`, with generator
identity/config, TTMn body/type/side, integer boundary, source Phase 6C model
identity, source Phase 8B artifact/result, fixture/run identity, and source
trajectory hash. It contains no muscle target or physiological output
parameters.

Two provenance levels remain explicit:

- source DNp01 fixtures: `SYNTHETIC_MOTOR_INTERFACE_TEST`;
- derived TTMn records: `EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT`.

These records are not `SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST` events from Phase
8L and are not `SIMULATED_FROM_SENSORY_EXPERIMENT`. The canonical Phase 7O
artifact is not a causal source for this artifact and remains unchanged and
silent. Phase 8N does not connect outputs to the Phase 8L target dispatcher.

## Artifact and replay

The immutable artifact uses `synthetic_ttmn_output_rule_artifact_v1` and
references the replay-validated Phase 8B child artifact
`4321adeee0412a79632ce4e008a1b8eaad22ee167f97f4a98521a9e71d9ef936`.
Reference artifact ID:
`1c8aeac685646dac16fbb66f163743b662a3cd9a0e8f9f7582210fd7b39b9ab3`.
Config SHA-256:
`43ddd7fba90235f7331c4c53ee774810956b9b55a9dc4c3ddc94bb4887283ea8`.
Result SHA-256:
`de54e2657560ae77a83b46174e029f7449008f968b0e0f4391cea8ec7a07c7b5`.
The artifact is 68,988 bytes including its manifest. Offline replay loads and
fully replays the Phase 8B child, regenerates crossing events and sensitivity
records, and checks exact content identity. If the ignored Phase 8B child is
absent, generation/replay rebuilds that fixed child offline from the pinned
local CircuitContract, verifies its canonical identity, then performs the same
full replay.

```sh
python -m neurofly.synthetic_ttmn_output_rule_cli generate
python -m neurofly.synthetic_ttmn_output_rule_cli inspect \
  data/derived/malecns/looming_giant_fiber_v1/synthetic_ttmn_output_rule_v1/1c8aeac685646dac16fbb66f163743b662a3cd9a0e8f9f7582210fd7b39b9ab3
python -m neurofly.synthetic_ttmn_output_rule_cli replay \
  data/derived/malecns/looming_giant_fiber_v1/synthetic_ttmn_output_rule_v1/1c8aeac685646dac16fbb66f163743b662a3cd9a0e8f9f7582210fd7b39b9ab3
```

## Scientific boundary

Phase 8N validates deterministic software semantics for a threshold-crossing
operator over a dimensionless exploratory state. It does not validate a
physiological TTMn threshold or action potential, derive events from Phase 7O,
add DLMn dynamics, resolve muscle targets, or model neuromuscular transfer,
muscle activity, force, body mechanics, or behavior. A nonzero Phase 8N event
ledger is an exploratory model output only.
