# Phase 6C — bounded DNp01→TTMn model-state slice

**Status: PASS — reproducible exploratory model slice; not biological
validation.** This phase appends a dimensionless TTMn model state to a new
versioned artifact. The upstream sensory/DNp01 CircuitContract and existing
experiment artifacts are unchanged. There is no TTMn physiology fit, muscle,
body mechanics, jump, takeoff, or escape output.

## Evidence contract and provenance

`malecns_dnp01_ttmn_evidence_v1` (`malecns_dnp01_to_ttmn_v1`) is a separate,
read-only evidence contract. It references, but does not amend, the existing
313-body `looming_giant_fiber_v1` contract. The upstream source files are
identified by their pinned SHA-256 values:

| Source | SHA-256 |
| --- | --- |
| `connections.jsonl` | `f7e55419d8f18a885f5ebcffa99ec8bf117d055593c0285c61def47020ae340a` |
| `neurons.jsonl` | `00fcba6a1cb3ccd650610bce61de6ce017f4b7ab472cfc9339c5d5247cad264e` |

The canonical upstream identity hash is
`3af274ecbf6ba4025b9e6ef0d038716446b0b9c03d9dd4f97c0151d280ebb8a5`; the
complete downstream evidence-contract hash is
`e65b8aae96115a0cc6ac875bdc3eeda69e11bfbd1ecb6495f75cdbe8f003dcd2`.
Construction and artifact loading validate the upstream candidate, version,
dataset, endpoint, source hashes, and DNp01 records. TTMn identities and the
two downstream edge records are pinned from the Phase 6B audit and official
MaleCNS v1.0 annotation provenance; they are not inserted into the upstream
313-body graph.

| Role | MaleCNS body | Identity | Side | Status / annotation |
| --- | ---: | --- | :---: | --- |
| DNp01 source | 10001 | `DNp01(GF)_R`, node index 0 | R | Traced / Roughly traced; descending neuron |
| DNp01 source | 10010 | `DNp01(GF)_L`, node index 1 | L | Traced / Roughly traced; descending neuron |
| TTMn target | 800146 | `TTMn_R` | R | Traced / Reviewed; VNC motor, subclass `wm`, T2 |
| TTMn target | 804642 | `TTMn_L` | L | Traced / Reviewed; VNC motor, subclass `wm`, T2 |

The two recorded `CHEMICAL_CONNECTOME_EDGE` observations are:

| Pre → post | Structural weight | Meaning |
| --- | ---: | --- |
| 10001 R → 800146 R | 70 | MaleCNS v1.0 chemical `ConnectsTo` structural count |
| 10010 L → 804642 L | 20 | MaleCNS v1.0 chemical `ConnectsTo` structural count |

The contract separately records literature-backed `ELECTRICAL_COUPLING`
evidence and `MIXED_CONNECTION` links for the GF→TTMn pairs. Pair-specific
electrical strength and combined mixed weight are `null`. No number is
invented for the missing electrical component. The model update does not read
either structural weight; both remain source connectome data only.

The annotation-table source and SHA-256, bounded neuPrint query provenance,
and literature basis are recorded in the evidence contract and
[`motor_escape_feasibility.md`](motor_escape_feasibility.md). The annotation
file was 14,483,314 bytes with SHA-256
`2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`. Phase
6C does not repeat a live query or download bulk MaleCNS data.

## Model boundary and equation

The existing `ExperimentRunner` first produces the persisted upstream result.
The motor layer then consumes only that same run's exact `DNp01` `SpikeEvent`
records. Source body ID, source graph node index, integer step, and stored time
are validated against the evidence contract and experiment grid. The mapping
is derived from the contract's directed chemical edge records:

```text
DNp01 10001 / node 0 / R → TTMn 800146 / R
DNp01 10010 / node 1 / L → TTMn 804642 / L
```

No mapping is inferred from array position, coordinate, side alone, stimulus,
or structural-weight ratio. A body/node identity mismatch or unsupported
source event fails closed.

For each target, the exploratory dimensionless state uses exact exponential
decay on the upstream simulation grid, followed by input at the stored event
boundary:

```text
x[n] = x[n−1] · exp(−dt_ms / tau_motor_ms) + event_count[n] · event_gain
```

`dt_ms` is inherited from the experiment; it is not a biological delay. Event
injection occurs at the same stored boundary as the DNp01 event, with no
additional transmission delay. This timing convention is a software/model
simplification, not a measured GF→TTMn latency. There is no stochastic
component or random seed. Reproducibility comes from the upstream config,
evidence contract, model config, and deterministic equations.

The reference configuration is
`phase6c_reference_model_assumptions_v1`:

| Parameter | Reference value | Classification | Interpretation |
| --- | ---: | --- | --- |
| `tau_motor_ms` | 10 ms | `MODEL_ASSUMPTION` | Abstract state-retention time; not measured TTMn membrane tau |
| `event_gain` | 0.25 dimensionless | `MODEL_ASSUMPTION` | Abstract same-boundary increment; not conductance, efficacy, or structural count |

State unit is `dimensionless`; model identity is
`ttmn_dimensionless_event_integrator`, version `phase6c_v1`. The gain is not
derived from weights 70/20, LIF parameters, or a desired takeoff result. This
is not a membrane-voltage model and has no threshold, biological TTMn spike,
muscle output, or response-classification layer.

## Same-run event provenance and integration

The runner executes the existing upstream `ExperimentRunner` once per new
condition, filters the exact persisted events whose type is `DNp01`, validates
their body/node/step/time identities, maps them through the evidence contract,
and integrates the two TTMn state series. The source events are retained
unchanged in the downstream result alongside the exact delivered input
records. The browser is not a controller; replay and the GET API do not run a
simulation.

For the reference 0.1 ms, 80 ms combined looming run, the DNp01 events are:

| DNp01 body | Step | Stored time | Target TTMn |
| ---: | ---: | ---: | ---: |
| 10010 | 453 | 45.300000000000004 ms | 804642 L |
| 10001 | 693 | 69.3 ms | 800146 R |
| 10010 | 693 | 69.3 ms | 804642 L |

At step 453, left TTMn state is 0.25. At step 693, right TTMn peaks at 0.25;
left TTMn peaks at 0.27267948832235345 after decay of its earlier event and
addition of the second event. Both peak times are 69.3 ms. These are
exploratory model-state summaries, not physiological response magnitudes.

## Controls and causal interpretation

The generated suite uses the verified Phase 6A artifact
`63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656` as the
configuration source. Each Phase 6C condition has new immutable upstream and
motor artifacts; the source artifact is not overwritten.

| Condition | Upstream DNp01 events | Delivered motor inputs | TTMn model-state result |
| --- | --- | ---: | --- |
| Combined looming reference | 10010 at 45.3 and 69.3 ms; 10001 at 69.3 ms | 3 | 800146 peak 0.25 at 69.3 ms; 804642 peak 0.27267948832235345 at 69.3 ms |
| Static far-field no-loom | none; both type drives are zero | 0 | both states remain zero |
| DNp01→TTMn output-silenced | source run retains the reference's 3 events | 0 | both states remain zero |
| LC4-only | 10010 at 59.900000000000006 ms | 1 | 804642 peaks at 0.25 at 59.9 ms; 800146 remains zero |
| LPLC2-only | none in this configured run | 0 | both states remain zero |

The silencing intervention is explicitly an **output-boundary** block: the
upstream experiment is preserved and its DNp01 events remain auditable, but no
event is delivered to the TTMn model. It establishes the code-level causal
gate “no delivered GF event → no GF-mediated TTMn model state” without
rewriting the upstream experiment. It should not be described as an
experimentally observed DNp01 ablation. LC4-only, LPLC2-only, and combined
conditions reach TTMn only through whatever exact DNp01 events the existing
upstream model produces; there is no direct sensory-to-TTMn path.

The no-loom control is a static far-field scene (`approach_velocity_m_s=0`,
`initial_distance_m=1,000,000`) passed through the ordinary encoder and
simulator. It is not special-cased in the downstream integrator.

## Sensitivity characterization

The deterministic nine-point sweep varies every free downstream parameter:

- `tau_motor_ms ∈ {5, 10, 20}`;
- `event_gain ∈ {0.1, 0.25, 0.5}`.

Across all nine points, event count, target mapping, and peak step remain
unchanged. The one-event right target peaks at its input increment (equal to
`event_gain`), so its peak is independent of `tau_motor_ms`; its post-event
decay changes with tau. The two-event left target's peak at step 693 increases
with both parameters. For `event_gain=0.25`, its peak is 0.252057436762,
0.272679488322, and 0.325298552978 at tau 5, 10, and 20 ms respectively.
Changing gain from 0.1 to 0.5 scales state magnitude fivefold. Thus the
qualitative presence and timing of this model response is stable across the
tested positive assumptions, while its magnitude remains assumption-sensitive
and uncalibrated. Sensitivity is a characterization, not optimization.

## Artifact and API

Phase 6C uses outer schema `motor_pathway_experiment_artifact_v1`; the nested
upstream remains the unchanged `experiment_artifact_v1`. Its motor result
schema is `motor_pathway_result_v1`. The outer immutable artifact contains:

- the original upstream experiment artifact and identity;
- pinned evidence contract and SHA-256;
- model/run config and SHA-256;
- exact source DNp01 events and mapped TTMn input records;
- both TTMn state traces and peak summaries;
- the nine-point sensitivity characterization;
- integrity hashes and `NOT_EVALUATED` validation status.

Old Phase 3–6A artifacts continue through the original loader/API without
rewriting. Local derived output is ignored at
`data/derived/motor_experiments/`. Generate the five reference/control
artifacts offline with:

```bash
python -m neurofly.motor_pathway_cli
```

The optional read-only route is
`GET /api/v1/motor-experiments/{artifact_id}` and requires
`NEUROFLY_MOTOR_EXPERIMENT_ARTIFACT_ROOT` to point to the local generated
artifact root. Requests validate stored files and never run `ExperimentRunner`,
query neuPrint, or make write operations. There is no Phase 6C cockpit UI
integration in this slice; current cockpit and static morphology presentation
remain unchanged, and no TTMn morphology is rendered.

## Scientific boundaries and limitations

- **MaleCNS source:** body identities, sides/status, directed chemical edges,
  and structural counts 70/20.
- **Literature:** GF/TTMn electrical and mixed connection context. Literature
  priors are not pair-specific MaleCNS conductance values.
- **NeuroFly model:** dimensionless integrator, same-boundary event injection,
  `tau_motor_ms`, and `event_gain`, all exploratory assumptions.
- **Presentation:** any later plotting/coloring is presentation state; none is
  added here.

The result does not establish TTMn electrophysiology or validate the upstream
model. There is no TTMn membrane voltage, electrical-coupling parameter,
chemical efficacy, synapse-specific or edge-specific activity, PSI/DLMn
branch, muscle model, force, leg extension, fly movement, short-mode
selection, long-mode pathway, behavior, or empirical validation. In
particular, a TTMn model-state result is not a TTMn biological spike, jump,
takeoff, or escape event. The literature's GF-to-middle-leg and end-to-end
muscle latencies are not the model's same-boundary input time or a fitted
parameter.

## Generated real run identities

The artifacts below are reproducible local outputs, not tracked source data.
The upstream config hash changes across stimulus/pathway conditions; the
motor run config is shared for ordinary runs and differs for the
output-silenced intervention.

| Run | Motor artifact ID | New upstream artifact ID | Upstream config SHA-256 | Motor run config SHA-256 | Motor result SHA-256 |
| --- | --- | --- | --- | --- | --- |
| Combined reference | `cc4a9c3d4464891d1df72cf5e8b37ed4c46b7b74e16f1a7f548bb4879fb257b8` | `6be446e019b6bc2bf7ac27b2302d08bfd5742f252696c74fcd2fd5916c3a838e` | `c1d1b185aeb4614af9ede070279127185837f825abc56efb41add899304824eb` | `6d9e33b36d728461709e18fd8bff138186a5823c4d7b2fb0cf9f5d522e7060ab` | `55969e37a3d3ae2bd3d2790a36cb7eecff6fb74c7720479c033e76ffa3d0cbfd` |
| Static far-field no-loom | `d529e7fcf92e7eeb176a939934851aaf4d637fa4652956d7920a978091cd0e54` | `63f99add4cef47b681a7af041dffc03c2be6cb2db0c3bfdce44c5c604dca5887` | `d2713a11b38aee22067c33030b78833f0c7898899a9c014b57e38a8c42a40193` | `6d9e33b36d728461709e18fd8bff138186a5823c4d7b2fb0cf9f5d522e7060ab` | `db8703d1f4656a56503ae06acb7a069ad877ac936858d67151ea019fb354497f` |
| Output-silenced | `abec8daab814d68bcf4aae0e6655c25833e32ae84fd982e3053bf65b750c593f` | `2f0e2a2ff6674a2d7b7a8af7f7f7a796f6f45f316a3a842750945a135a4b277f` | `c9ebd333b3aa3a74bd8c6b2f1180b339c1fcbba66b1952b08a7b958678a89b71` | `b552edc57a623ca2604d463b9a69b5df13f9ea502fa61aeec88a385d34672a33` | `f7ae1479b2e305b4e4e8f3919c942229a8663d90c87a60c53a2b03a4598f2961` |
| LC4-only | `75802c78011166d924f07a37b51d2319112d1b8609d38b72989b6506341bcd0a` | `5b900b77829e1ffa0c3f01ef1857f0352b0ea902b071f3e80d914e528e905a6b` | `ba11b0eb1c4852685aee3dac69f8cb454266da0f99550347f30668ce07db06b2` | `6d9e33b36d728461709e18fd8bff138186a5823c4d7b2fb0cf9f5d522e7060ab` | `06b96995633e69b3cc842a5feee9a739db99bc8388516376162bb9d3c8510ded` |
| LPLC2-only | `6521d8a1200bb4c677dfc9871ad4937a8c90e807a036ea8628fa9232617662b1` | `1a5ba0b6b417dbae04028a6b1d725cf8547e3ce2dbf030e95abd8f25c580e485` | `f735ff3150bb98c8c69274e499b5624e5f44d969c3ba5537dd497163bf6f93f4` | `6d9e33b36d728461709e18fd8bff138186a5823c4d7b2fb0cf9f5d522e7060ab` | `18ad56661d69fdf95d8ad80c0c8b627fa5d3b048b863288d45c9274c7b489834` |
