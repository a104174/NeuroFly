# Phase 8B — synthetic DNp01 event to TTMn model-state interface

## Scope and provenance

Phase 8B is a deterministic neural-interface test, not a sensory experiment.
Its only event source kind is `SYNTHETIC_MOTOR_INTERFACE_TEST`; each fixture
has a content-derived synthetic run identity. No Phase 7O artifact or event is
an input, and the Phase 7O result remains evidence that its reference and
tested sensitivity runs had zero simulated DNp01 events.

The chain is:

`synthetic fixture config → synthetic DNp01 event → MaleCNS-routed Phase 6C input → Phase 6C TTMn exploratory state`

The fixture records no sensory source artifact, voltage amplitude, synaptic
conductance, or biological efficacy. This validates identity, routing, timing,
replay, and the existing motor state update only.

## Existing Phase 6C contract preserved

Phase 6C's production `MotorPathwayExperimentResult` still requires its source
DNp01 events to equal the DNp01 events in its attached upstream
`ExperimentResult`; its artifact loader also checks that parent/event
relationship. Phase 8B does not construct a fake `ExperimentResult`, modify the
Phase 6C result or artifact schema, add an external-events flag, or loosen that
same-run invariant. Instead, a narrow synthetic fixture contract validates its
own provenance and converts only its validated events to the existing
`SpikeEvent` representation before reusing the existing Phase 6C route mapper
and TTMn integrator. It is not a generic arbitrary-event injection API.

The validated source identities and routes are:

| Synthetic DNp01 identity | Phase 6C TTMn target | MaleCNS chemical structural count |
| --- | --- | ---: |
| DNp01 10001 R, node 0 | TTMn 800146 R | 70 |
| DNp01 10010 L, node 1 | TTMn 804642 L | 20 |

Targets are resolved from the pinned motor evidence contract. Counts are
source structural metadata only and never enter the numerical update. The
contract also records literature support for electrical coupling, but no
MaleCNS pair-specific conductance value.

## Event and time semantics

The fixture battery uses `dt_ms = 0.1` and 80 intervals. Events are represented
at integer state boundaries, with strict `time_ms == step * dt_ms` validation.
The reference single events occur at step 10 (`1.0 ms`); repeated events occur
at steps 10 and 30 (`1.0` and `3.0 ms`). The event enters the TTMn state at the
same stored boundary. There is no separately modeled DNp01-to-TTMn delay.

`SpikeEvent` carries time, step, body ID, node index, and neuron type; its
containing synthetic fixture/artifact carries the synthetic provenance. Event
IDs also retain source body and step. No side or identity is inferred from
array position: the fixture validates DNp01 10001/R/node 0 and
10010/L/node 1, then the evidence contract maps their targets.

## Existing exploratory TTMn model

No Phase 6C parameter or integration code changed. With zero initial state the
existing exact update is:

```text
x[0] = 0
x[n] = x[n-1] * exp(-dt_ms / tau_motor_ms)
       + event_count[n] * event_gain
```

The existing reference assumptions are `tau_motor_ms = 10` and
`event_gain = 0.25`; they remain `MODEL_ASSUMPTION`. The state is
dimensionless and is not muscle activation, force, torque, an escape command,
or behavior. Events are counts, not amplitudes.

## Fixed fixture battery and model outputs

The persisted battery is intentionally small:

| Fixture | Synthetic DNp01 events | TTMn model result |
| --- | --- | --- |
| `ZERO_EVENT_CONTROL` | none | both states remain exactly zero |
| `RIGHT_SINGLE_EVENT` | 10001/R at step 10 | 800146 receives one event; peak 0.25 at step 10; final state 0.12414632594785285 |
| `LEFT_SINGLE_EVENT` | 10010/L at step 10 | 804642 receives one event; peak 0.25 at step 10; final state 0.12414632594785285 |
| `BILATERAL_SIMULTANEOUS_EVENT` | both bodies at step 10 | each target updates independently to peak 0.25 at step 10 |
| `RIGHT_REPEATED_EVENTS` | 10001/R at steps 10, 30 | 800146 receives two; peak 0.45468268826949565 at step 30; final state 0.27577899087601165 |
| `LEFT_REPEATED_EVENTS` | 10010/L at steps 10, 30 | same trajectory on 804642; opposite target remains zero |

These values are consequences of the committed equation, grid, and test event
times—not fitted or physiological response values. In repeated fixtures, the
second event follows one event contribution decayed for 20 intervals:
`0.25 + 0.25 * exp(-(20 * 0.1) / 10)`.

## Immutable artifact and replay

Schema: `synthetic_dnp01_ttmn_interface_artifact_v1`, containing canonical
fixture config, result, and manifest files. The configuration pins the
CircuitContract hashes and motor evidence identity; the result records all
synthetic events, mapped target inputs, and TTMn state trajectories. Content
identity covers configuration and result hashes. Replay is offline and checks
source identity, exact fixture definition, results, and hashes.

The generated artifact ID is
`4321adeee0412a79632ce4e008a1b8eaad22ee167f97f4a98521a9e71d9ef936`, with
config SHA-256
`13b2cc3c33af1c3fba8d918da6d33bd8225a077a8cc0bc7fd383f63a595a1863`, result
SHA-256
`a3c9cdc02ec02211059411ab5819c1bba318e2b58c866663162ae85a852670d5`, and
43,317 bytes across config, result, and manifest.

Historical Phase 6C and Phase 7O artifacts retain their original schemas and
semantics. A Phase 8B synthetic event is never labeled
`SIMULATED_FROM_SENSORY_EXPERIMENT` and is never inserted into Phase 7O.

## Scientific boundary

MaleCNS contributes body identities, the bounded structural routes, and
chemical contact-count metadata. The DNp01 event is a synthetic test fixture.
The dimensionless TTMn state is NeuroFly model output from the unchanged Phase
6C assumptions. Electrical-coupling literature does not identify a
pair-specific MaleCNS conductance, and Phase 8B does not treat `event_gain` or
structural counts as one. No muscle, PSI, DLMn, motor behavior, or sensory-to-
motor causal claim is added.

The next useful step is a separately provenance-typed adapter from a genuine
Phase 7O DNp01 event artifact to the unchanged Phase 6C event contract, with a
zero-event case that remains zero. It should proceed only when that causal
composition can be tested without changing sensory or DNp01 assumptions.
