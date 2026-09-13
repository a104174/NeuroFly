# NeuroFly

NeuroFly is a planned experimental platform for studying connectome-based
digital agents inspired by the MaleCNS *Drosophila melanogaster* connectome.

The repository is currently in **Phase 5E: MaleCNS spatialization feasibility
and coordinate contract**. Phase 3C provides deterministic experiment comparison, Phase 3B
provides portable experiment artifacts, Phase 3A provides the reproducible
experiment-run foundation, and Phase 2H-A
provides the empirical constraint infrastructure. Phase 2B provides the narrow
offline 313-node/311-edge
deterministic LIF execution slice, Phase 2E implements the E1 encoder, and
Phase 2F characterizes their complete production path. Phase 2G pre-registers
source provenance, measurement/model comparability, and fit-versus-held-out
roles; Phase 2H-A validates that metadata boundary offline without parameter
fitting. Phase 4A provides a read-only, transport-neutral artifact/application
boundary. Level C, visual-angle mapping, motor modelling, and behaviour remain
unimplemented. Phase 4B adds a thin FastAPI GET-only adapter
over the Phase 4A boundary; Phase 5A adds a read-only Next.js/React/TypeScript
browser over that API. Phase 5B adds presentation-only React Three Fiber
playback of persisted timelines. Phase 5C replaces the normal procedural fly
path with a versioned project-created GLB while retaining the procedural
fallback. Phase 5D adds a centralized presentation-space layout, abstract
pathway overlays, current scientific readouts, and explicit visual provenance.
Phase 5E preserves that scene while defining an immutable raw-skeleton contract
and auditing a fixed six-body MaleCNS sample. None of these layers runs
simulations or adds write routes.

Scientific integrity is a project constraint: future code must distinguish
biological/connectomic data from NeuroFly modelling assumptions. The detailed
project intent and scientific brief are maintained in
[`docs/NeuroFly_Project_Context.md`](docs/NeuroFly_Project_Context.md).

## Development setup

Use Python 3.12.x. From the repository root, create or activate a virtual
environment and install the project with its development tools:

```bash
python -m venv .venv
python -m pip install --editable ".[dev]"
```

The canonical quality commands are:

```bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

## MaleCNS Phase 1A

The versioned candidate `looming_giant_fiber_v1` selects every typed `:Neuron`
body with type `LC4`, `LPLC2`, or `DNp01` from the official endpoint
`https://neuprint.janelia.org`, pinned to dataset `male-cns:v1.0`. Acquisition
preserves the complete body-level chemical `ConnectsTo` induced subgraph among
all selected bodies—including reverse, recurrent, same-type, and cross-type
edges—not merely the primary LC4/LPLC2 to DNp01 motif.

Get application credentials from neuPrint and inject them through the normal
environment:

```bash
export NEUPRINT_APPLICATION_CREDENTIALS='your credential from neuPrint'
```

Never commit, print, or serialize this value. The code does not load `.env`
files, and `.env` remains ignored.

Check authentication and the pinned dataset without downloading the circuit:

```bash
python -m neurofly.malecns check-access
```

Acquire, validate, and export the candidate:

```bash
python -m neurofly.malecns snapshot
```

The default output is
`data/derived/malecns/looming_giant_fiber_v1/`, containing deterministically
ordered `neurons.jsonl`, `connections.jsonl`, and `manifest.json`. This derived
path is ignored by Git. Export validates all pinned scientific invariants
before writing, stages all files in a temporary sibling directory, and then
finalizes atomically. It fails if the target already exists; remove the target
explicitly before regenerating so snapshots are never silently mixed or
replaced.

Normal tests remain offline. The authenticated smoke test is opt-in:

```bash
python -m pytest -m integration
```

It skips if `NEUPRINT_APPLICATION_CREDENTIALS` is absent. The ordinary
`python -m pytest` command excludes integration tests.

## Offline circuit contract

Phase 1B separates network-based acquisition from offline consumption. Validate
the default ignored snapshot and print its deterministic structural summary:

```bash
python -m neurofly.malecns inspect-snapshot
```

An alternate snapshot directory can be supplied as the positional argument.
This command requires neither network access nor neuPrint credentials. It
verifies the supported candidate and dataset, required files, SHA-256 hashes,
record counts, biological records, edge endpoints and types, unique body-level
edges, the complete type-pair summary, and the primary LC4/LPLC2 to DNp01
invariants before constructing the circuit contract.

Nodes are ordered by biological `body_id`. Contiguous node indices `0..312`
are a deterministic project implementation convenience; they are not MaleCNS
identifiers. The contract retains all chemical structural edges, including
same-type, reverse-direction, low-weight, and DNp01-originating connections.

The contract and its scientific boundaries are documented in
[`docs/science/circuit_contract.md`](docs/science/circuit_contract.md).

## Sensory boundary and looming benchmark (Phase 1C)

Phase 1C specifies a deterministic, model-neutral looming stimulus using
physical radius, approach velocity, initial distance, visual center, time,
angular size, and angular expansion velocity. It also records literature-grounded
benchmarks for LPLC2 selectivity, LC4/LPLC2 feature separation, and combined
DNp01/Giant Fiber integration. These specifications do not generate neural
inputs or behaviour. See
[`docs/science/sensory_boundary_evidence.md`](docs/science/sensory_boundary_evidence.md).

## MaleCNS receptive-field feasibility (Phase 1D-B)

Phase 1D-B audited the 2026 MaleCNS visual-pathway work, official optic-column
and eye-map resources, and a deterministic sample of 16 real candidate bodies.
Credentialed live validation found reproducible body-specific input-column
topology for both populations (**D3**), but no provenance-verified
column-to-angular-visual-space transform. No visual-angle receptive-field
artifact was invented, and no morphology was needed or acquired. See
[`docs/science/receptive_field_feasibility.md`](docs/science/receptive_field_feasibility.md)
for the sample manifest, evidence ledger, limitations, safeguards, and smallest
next phase.

## MaleCNS body-specific column space (Phase 1E)

Phase 1E validates the exact frozen 16-body server aggregation against the raw
Phase 1D counts, then derives a separate immutable body-column contract for all
126 LC4 and 185 LPLC2 bodies in the validated `CircuitContract`. The sparse
records preserve source neuropil (`ME`, `LO`, `LOP`), side, MaleCNS hex indices,
and postsynaptic input-site counts; missing assignments remain explicit. The
ignored data product is under
`data/derived/malecns/looming_giant_fiber_v1/body_columns_v1/` and can be
verified offline with:

```bash
python -m neurofly.malecns inspect-column-snapshot
```

This is column space, not visual-angle space or a physiological input. No
sensory encoder or physiological neural-input mapping is implemented. See
[`docs/science/body_column_contract.md`](docs/science/body_column_contract.md)
for the schema, provenance, method-equivalence gate, and population coverage.

## Sensory-consumption boundary (Phase 1F)

Phase 1F defines two future capability levels without implementing either
encoder: **Level P** uses the Phase 1C population feature approximation (LC4
with angular-expansion-velocity-related input and LPLC2 with angular-size-
related input), while **Level C** preserves body-specific column topology but
remains disabled until an environment-to-column modelling contract is designed
and validated. See
[`docs/science/sensory_consumption_boundary.md`](docs/science/sensory_consumption_boundary.md).

## Neural-model selection (Phase 2A)

Phase 2A compares spiking LIF, continuous/rate, and propagation baselines and
selects **M1 — LIF with filtered synapses** for the first model hypothesis.
The initial validation graph is the explicit 311-edge LC4/LPLC2-to-DNp01
feed-forward subset; all 20,607 structural edges remain preserved in the
CircuitContract. Parameters, signs, contact-count scaling, deterministic
Level P drive, GF timing benchmarks, and the future Phase 2B implementation
boundary are documented in
[`docs/science/neural_model_selection.md`](docs/science/neural_model_selection.md).

## Deterministic simulation core (Phase 2B)

`neurofly.simulation` implements the explicit M1 equations, validated central
LC4/LPLC2-to-DNp01 graph view, deterministic caller-supplied
`external_drive`, filtered synaptic state, delayed events, threshold/reset/
refractory behavior, and in-memory telemetry. It does not implement a looming
encoder or simulate the full induced graph. Details are documented in
[`docs/science/neural_simulation_core.md`](docs/science/neural_simulation_core.md).

## Parameter sensitivity benchmark (Phase 2C)

`neurofly.sensitivity` defines deterministic `ZERO`, `LC4_ONLY`, `LPLC2_ONLY`,
and `COMBINED` synthetic population-drive probes, bounded parameter sweeps,
compact per-DNp01 summaries, configuration hashes, and exact replay checks.
The benchmark demonstrates sensitivity and parameter degeneracy; its drive and
coupling values are not biological calibration results. See
[`docs/science/parameter_sensitivity.md`](docs/science/parameter_sensitivity.md).

## Level P encoder selection (Phase 2D)

Phase 2D selects **E1 — direct bounded-normalized instantaneous feature
drive** as the next implementation contract. It specifies explicit LC4
expansion-velocity and expansion-gated LPLC2 size channels, separate free
normalization scales and `mV_eq` gains, zero baseline, deterministic bilateral
population broadcast, and no added filter or latency. These are documented
NeuroFly assumptions; no encoder or biological calibration is implemented.
See
[`docs/science/level_p_encoder_selection.md`](docs/science/level_p_encoder_selection.md).

## Deterministic Level P encoder (Phase 2E)

`neurofly.sensory_encoder` implements the immutable E1 configuration and
memoryless bounded feature mapping. It consumes aligned pre-collision
`LoomingSample` values, broadcasts deterministic LC4/LPLC2 drives to the 311
visual bodies, and returns the existing Phase 2B `ExternalDriveSchedule`.
DNp01 remains excluded; no gain or normalization scale is biologically
calibrated. See
[`docs/science/level_p_encoder_selection.md`](docs/science/level_p_encoder_selection.md)
for the contract and provenance.

## Looming trajectory characterization (Phase 2F)

`neurofly.trajectory_characterization` runs deterministic pre-collision
`LoomingStimulus` trajectories through the production E1 encoder and Phase 2B
simulator. It compares LC4-only, LPLC2-only, and combined pathways, retains
both DNp01 outputs, reports structural asymmetry and timestep sensitivity, and
classifies model operating regimes. Every numeric configuration is an
explicit synthetic benchmark, not a biological calibration. See
[`docs/science/looming_trajectory_characterization.md`](docs/science/looming_trajectory_characterization.md).

## Empirical constraint protocol (Phase 2G)

Phase 2G audits primary LC4/LPLC2/GF evidence and pre-registers an empirical
constraint schema, measurement-specific observation transforms, fit and
held-out validation roles, uncertainty handling, and falsification criteria.
Its G2 decision permits only relative/normalized constraints until author
source data and an observation bridge are available; no biological parameter
was fitted. See
[`docs/science/empirical_constraint_protocol.md`](docs/science/empirical_constraint_protocol.md).

## Empirical constraint infrastructure (Phase 2H-A)

`neurofly.empirical_constraints` provides immutable metadata records, explicit
availability/reuse/comparability states, a locked Phase 2G partition, payload
checksum references, and deterministic registry/protocol hashes. The tracked
registry contains metadata only; no experimental trace or fabricated numeric
payload is included. Inspect it offline with
`python -m neurofly.empirical_constraints inspect`. See
[`docs/science/empirical_constraint_infrastructure.md`](docs/science/empirical_constraint_infrastructure.md).

## Reproducible experiment runs (Phase 3A)

`neurofly.experiments` composes the existing production stimulus, Level P E1
encoder, Phase 2B graph, and deterministic LIF simulator into one immutable,
replay-verified offline experiment result. All five free modelling parameters
remain explicit; runs are marked `NOT_EVALUATED` and do not perform empirical
fitting. See
[`docs/science/reproducible_experiment_runs.md`](docs/science/reproducible_experiment_runs.md).

## Portable experiment artifacts (Phase 3B)

`neurofly.experiment_artifacts` exports a completed Phase 3A result as an
atomic, ignored directory of UTF-8 JSON/JSONL files containing the complete
configuration, selected telemetry, spike and delivered-event records,
deterministic summaries, provenance, and SHA-256 integrity metadata. The
strict offline loader validates the artifact without neuPrint, credentials, or
simulation, while `replay_experiment_artifact` optionally reruns the persisted
configuration against an explicitly supplied local CircuitContract. Generated
artifacts belong under `data/derived/experiments/` and remain untracked. See
[`docs/science/experiment_artifact_contract.md`](docs/science/experiment_artifact_contract.md).

## Deterministic experiment comparison (Phase 3C)

`neurofly.experiment_comparison` compares two integrity-validated Phase 3B artifacts
offline. It reports source/model compatibility, explicit stimulus/encoder/
neural/pathway/telemetry differences, separate LC4/LPLC2 and DNp01 summaries,
event differences, and directional model-trajectory metrics only when exact
time bases permit them. It never interpolates, ranks runs, fits parameters, or
claims empirical validation. Inspect two artifacts with:

```bash
python -m neurofly.experiment_comparison <artifact-a> <artifact-b>
```

See [`docs/science/experiment_comparison.md`](docs/science/experiment_comparison.md).

## Read-only experiment application boundary (Phase 4A)

`neurofly.experiment_api` exposes JSON-safe summaries, exact neural-time
timelines, selected body telemetry, spike/delivered events, and Phase 3C
comparison summaries through an explicit local artifact root. It performs no
simulation or writes, and adds no HTTP dependency. See
[`docs/architecture/read_only_experiment_api.md`](docs/architecture/read_only_experiment_api.md).

## GET-only experiment HTTP adapter (Phase 4B)

`neurofly.http_api` exposes the Phase 4A contract under `/api/v1` for
completed artifacts: summaries, exact simulation-time timelines, persisted
body telemetry, spike/delivered events, and directional Phase 3C comparisons.
The app factory receives an explicit artifact root and never invokes the
simulator.  Launch a local read-only server with:

```bash
NEUROFLY_EXPERIMENT_ARTIFACT_ROOT=/path/to/data/derived/experiments \
  uvicorn neurofly.http_api:create_app_from_env --factory
```

See [`docs/architecture/http_experiment_api.md`](docs/architecture/http_experiment_api.md).

## Read-only browser foundation (Phase 5A)

The `web/` application is a small Next.js App Router slice. It consumes the
real Phase 4B API with a typed, runtime-checked client, lists completed
artifacts, and provides `/experiments/[artifactId]` detail pages with
provenance, separate LC4/LPLC2 and DNp01 summaries, and the persisted
simulation timeline. It has no mock production fallback, live simulation,
charting, or parameter controls; Phase 5A itself introduced no 3D dependency.
Configure the server-side API URL
with `web/.env.example`, then run `npm install && npm run dev` from `web/`.
See [`docs/architecture/frontend_foundation.md`](docs/architecture/frontend_foundation.md).

## Immersive 3D playback foundation (Phase 5B)

The experiment detail route now passes its already validated timeline into a
narrow client-side playback workspace. A wall-clock-driven presentation clock
selects exact persisted state boundaries and intervals in simulation
milliseconds; it never advances one neural step per frame and never
interpolates scientific values. The React Three Fiber scene contains a static
procedural fly placeholder, an angular-size-based looming proxy, and separate
LC4, LPLC2, DNp01 10001, and DNp01 10010 indicators. Play, pause, reset, seek,
and fixed playback-rate controls do not modify experiment identity or execute
the model. See
[`docs/architecture/3d_playback_foundation.md`](docs/architecture/3d_playback_foundation.md).

## Controlled Blender/glTF asset pipeline (Phase 5C)

The project-created `neurofly_fly_visual_v1` source is generated and saved by
a controlled Blender 4.0.2 script, exported as a small static GLB, and pinned
by a versioned presentation manifest and SHA-256. Its normalized scale, origin,
axes, one scene transform, budgets, and no-animation status are explicit. The
R3F loader uses the GLB only as stationary presentation geometry; the Phase 5B
procedural mesh remains the loading/error fallback. Asset identity does not
participate in experiment, result, artifact, or comparison identity. See
[`docs/architecture/blender_asset_pipeline.md`](docs/architecture/blender_asset_pipeline.md).

## Scientific 3D scene composition (Phase 5D)

The playback scene now uses the centralized, presentation-only
`neurofly_scene_layout_v1` contract. Abstract LC4 and LPLC2 pathway lines lead
to separately identified DNp01 bodies 10001 and 10010, while raw current values,
visual-asset provenance, and a data-versus-presentation legend remain readable
outside WebGL. These coordinates are explicitly not anatomical; the stationary
fly, playback clock, deterministic timeline lookup, and no-interpolation policy
are unchanged. See
[`docs/architecture/scientific_scene_composition.md`](docs/architecture/scientific_scene_composition.md).

## MaleCNS spatialization contract (Phase 5E)

`neurofly.malecns.spatial` defines an immutable, body-keyed raw morphology
contract with an explicit native coordinate frame/unit, disconnected
components, tree-link provenance, and deterministic identity. A bounded
credentialed audit retrieved two LC4, two LPLC2, and both DNp01 raw skeletons
by exact body ID; one sampled LPLC2 was fragmented and remains unhealed. Native
MaleCNS x/y/z are preserved separately from any browser transform, and no
anatomical rendering or scene-layout change is introduced. The readiness
decision is **S1** for a small, separate raw morphology inspection slice only.
See
[`docs/science/malecns_spatialization_contract.md`](docs/science/malecns_spatialization_contract.md).

### Scientific semantics and limitation

Neuron annotations and null values are retained as source data. In connection
records, `structural_weight` maps exactly to neuPrint `ConnectsTo.weight`: a
structural synaptic-contact/connectivity count, **not** a physiological or
NeuroFly simulation coupling parameter. Reconstruction statuses such as
`Traced` are database metadata, not physiological states, and predicted versus
consensus neurotransmitter annotations remain separate.

LC4 and LPLC2 are visual projection populations and DNp01/Giant Fiber is the
initial descending endpoint, but these three types are not claimed to be a
complete visual or escape circuit. The acquired `ConnectsTo` graph represents
chemical-connectome structure. Giant Fiber downstream biology also contains
electrical/gap-junction contributions (including circuitry involving TTMn and
PSI), which this snapshot neither invents nor represents.
