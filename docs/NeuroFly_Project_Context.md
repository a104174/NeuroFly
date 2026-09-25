# NeuroFly — Project Context / Source of Truth

> **Working title:** NeuroFly  
> The name is provisional and may change later.  
> **Document purpose:** provide persistent context to ChatGPT Project chats, Codex-oriented implementation chats, architecture discussions, scientific reasoning and future documentation.  
> **Current status:** Phase 6C adds a reproducible exploratory DNp01→TTMn
> dimensionless model-state slice from exact same-run DNp01 events. It does not
> model TTMn physiology, muscle mechanics, takeoff, or behavior. MaleCNS v1.0
> chemical edges and literature-supported electrical/mixed evidence remain
> separate; structural weights 70/20 are never model gains. Phase 6B verified
> those identities/edges and established the evidence boundary. Phase
> 6A remains the existing validated, read-only activity-to-structure mapping:
> sensory encoder drives are type-level, and only CircuitContract-validated
> DNp01 point-neuron state is associated with individual body morphologies.
> Phase 5K refines the Scientific Cockpit's viewport layout, compact controls,
> readable telemetry, and presentation-only panel focus.
> Phase 5J composes a persisted experiment, the six-body
> raw morphology inspector, and the Phase 5I structural projection in one
> read-only Scientific Cockpit. One canonical experiment clock coordinates the
> world, stored telemetry, selected DNp01 dynamics, and deterministic event
> positions; structure and presentation state remain separate. Phase 5I adds a bounded structural-connectivity projection
> to the S1-bounded raw morphology inspector. The six-body sample displays only
> actual LC4/LPLC2 → DNp01 CircuitContract edges; connectors remain schematic.
> Phase 5H makes the separate raw morphology inspector selectable and camera-focusable at body/component level for the
> audited six-body LC4/LPLC2/DNp01 sample. Source coordinates
> remain preserved behind `malecns_morphology_artifact_v1`; one shared browser
> view transform does not alter scientific identity. Phase 5D provides a controlled,
> versioned Blender/glTF
> presentation-asset pipeline for Phase 5B's React Three Fiber playback
> surface over Phase 5A's read-only Next.js/React/TypeScript browser,
> Phase 4B's minimal GET-only HTTP adapter, and
> Phase 4A's transport-neutral application boundary for portable model-run
> artifacts. Phase 3C implements
> deterministic, directional comparison. Phase 3B implements the portable,
> integrity-checked artifact contract for completed deterministic runs. Phase
> 3A implements the deterministic, replay-verified offline experiment-run
> foundation. Phase 2H-A implements the metadata-only empirical constraint
> registry for the Phase 2G protocol. The evidence audit remains
> G2: only relative, normalized, qualitative, and downstream constraints are
> currently usable; source-data ingestion and an observation bridge must
> precede physiological fitting. No gain, normalization scale, coupling, or
> biological latency is fitted.
> Phase 5D adds a centralized presentation-space scene layout and abstract
> spatial overlays without introducing anatomical coordinates or behavior.
> Phase 5E does not alter that scene: it preserves native MaleCNS 8 nm voxel
> coordinates, disconnected raw components, exact body-ID provenance, and
> explicit raw/artificial link provenance. Native axis names and origin remain
> unresolved and must not be given anatomical labels.
> Phase 5F likewise does not alter the playback scene. It adds raw-only
> acquisition, offline integrity, GET-only transport, and a separate static
> morphology inspector without fly alignment or activity semantics. The real
> DNp01 artifact uses the official MaleCNS bulk SWC source with explicit URL
> and SHA-256 provenance because neuPrint is unreachable in the current
> environment; no healing, smoothing, repair, or inferred structure is added.
> Phase 5G preserves the two disconnected raw components of LPLC2 body 11498,
> uses one shared six-body presentation transform, and adds only visibility and
> provenance controls. It does not align morphology to the Blender fly.
> Phase 5H adds local body/component selection, source-coordinate bounds,
> presentation-only highlighting, and camera-only focus. Selection does not
> enter source artifacts, experiment identity, or playback.
> Phase 5I derives a fixed six-body LC4/LPLC2 → DNp01 projection from the
> integrity-validated local CircuitContract. Structural weights remain source
> connectome counts. Straight 3D connectors use transformed body-bound centers
> only as schematic presentation anchors; they do not claim synapse locations,
> efficacy, or neural activity. Runtime needs no neuPrint or network access.
> Phase 1D/1E's D3 conclusion remains in
> force: no provenance-verified body-level
> LC4/LPLC2 column-to-angular-visual-space
> transform is available for `male-cns:v1.0`. Level P is the documented
> population-feature boundary; Level C remains disabled, and no biological
> calibration, behavior, or muscle/body mechanics are implemented. Phase 6C's
> TTMn state is explicitly exploratory, not biological motor-neuron dynamics.
> **Date of this context:** 2026-09-24.

Phase 6E selected sensory individualization as the next scientific focus.
Phase 7A's [bilateral retinotopy feasibility audit](science/bilateral_retinotopy_feasibility.md)
finds body-specific MaleCNS input-column topology for all 126 LC4 and 185
LPLC2 neurons, but no audited, provenance-verified bilateral column-to-degree
registration. Its decision is `RETINOTOPY_ONLY_NO_ABSOLUTE_VISUAL_ANGLE`:
column indices and structural input counts are not functional RFs or
physiological gain. Phase 7B's [optical registration
assessment](science/bilateral_optical_registration_assessment.md)
found bilateral optical rays from a separate female µCT specimen and a
right-FAFB registration method, but no released, independently testable
MaleCNS v1.0 L/R column-key-to-ray correspondence. Its decision is
`COLUMN_SPACE_ONLY`: no angular centres were assigned to MaleCNS bodies.
Phase 7C's [relative column-space assessment](science/relative_column_sensory_feasibility.md)
finds reproducible six-neighbour anatomical addressing for all 311 bodies and
synthetic body-specific exposure, but no measured RF, gain, or individual
neural state. Decision: `RELATIVE_COLUMN_INPUT_FEASIBLE` only as an explicitly
synthetic, assumption-labelled bounded model. Phase 7D may test a small
predeclared subset with a distinct relative-column stimulus/assignment
contract. Phase 7D now persists and replay-verifies ten samples for four
predeclared LC4/LPLC2 bodies under synthetic unilateral relative-column disk
stimuli. Its outputs are record-overlap and structural-input-site-overlap
fractions only; those are anatomical exposure, not neural input or response.
Absolute visual angle and functional RF semantics remain unavailable. The
existing angular looming encoder remains type-level and unchanged. See the
[Phase 7D assignment contract](science/relative_column_sensory_assignment.md).
Phase 7E now derives four body-specific, dimensionless exploratory sensory
model states from that replay-verified assignment using the separate
`relative_column_exploratory_sensory_state_v1` model. Its shared
`tau_sens_ms = 1.0` and `gain = 1.0` are explicit model assumptions, with
deterministic replay and sensitivity coverage. It adds no spikes, physiological
interpretation, DNp01 input, or frontend visualization; the 311/313-neuron
dynamics milestone remains incomplete. See the
[Phase 7E sensory-state assessment](science/relative_column_sensory_dynamics.md).

The Phase 1D-B evidence ledger is maintained in
[`docs/science/receptive_field_feasibility.md`](science/receptive_field_feasibility.md).
It records the deterministic 16-body sample and its independent D3 decisions.
The resulting full body-to-column contract is documented in
[`docs/science/body_column_contract.md`](science/body_column_contract.md). This
contract stops at source neuropil and MaleCNS column indices; it does not claim
angular receptive fields or implement an encoder.

The Phase 1F sensory-consumption boundary is documented in
[`docs/science/sensory_consumption_boundary.md`](science/sensory_consumption_boundary.md).

The Phase 2A neural-dynamics evidence audit and model-selection specification
is documented in
[`docs/science/neural_model_selection.md`](science/neural_model_selection.md).

The Phase 2B deterministic LIF simulation core is documented in
[`docs/science/neural_simulation_core.md`](science/neural_simulation_core.md).

The Phase 2C parameter-sensitivity and identifiability benchmark is documented
in [`docs/science/parameter_sensitivity.md`](science/parameter_sensitivity.md).

The Phase 2D Level P evidence audit and selected future encoder contract are
documented in
[`docs/science/level_p_encoder_selection.md`](science/level_p_encoder_selection.md).

The Phase 2E deterministic E1 implementation is provided by
`neurofly.sensory_encoder` and is covered by focused offline tests in
`tests/test_sensory_encoder.py`.

The Phase 2F end-to-end operating-regime and timestep characterization is
documented in
[`docs/science/looming_trajectory_characterization.md`](science/looming_trajectory_characterization.md).

The Phase 2G primary-evidence inventory and pre-registered fit/held-out
validation protocol are documented in
[`docs/science/empirical_constraint_protocol.md`](science/empirical_constraint_protocol.md).

The Phase 2H-A immutable constraint metadata registry and pending-source-data
workflow are documented in
[`docs/science/empirical_constraint_infrastructure.md`](science/empirical_constraint_infrastructure.md).

Phase 3A's immutable `ExperimentConfig`, selected telemetry, source
provenance, deterministic replay, and small manifest boundary are documented
in
[`docs/science/reproducible_experiment_runs.md`](science/reproducible_experiment_runs.md).
Runs remain `NOT_EVALUATED`: no empirical fitting, behaviour, Level C, or
runtime networking is implemented.

Phase 3B's portable `experiment_artifact_v1` directory, JSON/JSONL telemetry
and event files, SHA-256 integrity manifest, atomic export, strict offline
loader, and explicit replay operation are documented in
[`docs/science/experiment_artifact_contract.md`](science/experiment_artifact_contract.md).
Generated artifacts are ignored under `data/derived/experiments/`; they do not
contain third-party empirical source data and do not change the run's
`NOT_EVALUATED` status.

Phase 3C's immutable comparison result, source/model compatibility classes,
configuration-difference report, exact-time-base trajectory metrics, event and
DNp01 summaries, and no-interpolation policy are documented in
[`docs/science/experiment_comparison.md`](science/experiment_comparison.md).
Comparisons remain model-versus-model and `NOT_EVALUATED`; they do not rank
experiments or perform calibration.

Phase 4A's read-only `ExperimentArtifactStore` and JSON-safe application DTOs
are documented in
[`docs/architecture/read_only_experiment_api.md`](architecture/read_only_experiment_api.md).
Phase 4B's FastAPI GET-only adapter, explicit artifact-root configuration,
stable error contract, and local launch procedure are documented in
[`docs/architecture/http_experiment_api.md`](architecture/http_experiment_api.md).
The adapter consumes completed artifacts only; it does not execute the
simulator, add write routes, or make the scientific core depend on HTTP.

Phase 5A's first read-only Next.js/React/TypeScript browser, typed Phase 4B
client, runtime response guards, experiment catalogue, detail route, and
timeline inspector are documented in
[`docs/architecture/frontend_foundation.md`](architecture/frontend_foundation.md).
The Phase 5A slice has no mock production fallback, live simulation, parameter
editing, or empirical-validation claim.

Phase 5B's simulation-time playback clock, deterministic boundary/interval
lookup, pure scene-state derivation, procedural fly placeholder, looming
proxy, and separate pathway/output indicators are documented in
[`docs/architecture/3d_playback_foundation.md`](architecture/3d_playback_foundation.md).
The R3F renderer consumes persisted telemetry only. It does not step the
model, interpolate scientific values, infer behavior, or change the run's
`NOT_EVALUATED` status.

Phase 5C's project-created Blender source, controlled static GLB export,
versioned manifest, SHA-256 integrity check, normalized axes/scale/origin, R3F
loader, and procedural fallback are documented in
[`docs/architecture/blender_asset_pipeline.md`](architecture/blender_asset_pipeline.md).
The visual asset remains stationary and presentation-only. Its identity does
not participate in scientific experiment, result, artifact, or comparison
identity, and it is not MaleCNS morphology or measured anatomy.

Phase 5D's `neurofly_scene_layout_v1` centralizes the presentation camera,
grid, looming corridor, and distinct LC4/LPLC2/DNp01 anchors. Abstract pathway
lines communicate only the model graph direction; they are not axons or
anatomical coordinates. A current-value overlay, separate visual-asset
provenance, and explicit persisted-data versus presentation-mapping legend are
documented in
[`docs/architecture/scientific_scene_composition.md`](architecture/scientific_scene_composition.md).
The fly remains stationary and playback/timeline semantics are unchanged.

Phase 5E's immutable `malecns_neuron_spatial_v1` contract, authoritative
coordinate evidence, fixed bilateral six-body raw-skeleton audit,
fragmentation policy, raw-versus-healed boundary, and source-to-view transform
separation are documented in
[`docs/science/malecns_spatialization_contract.md`](science/malecns_spatialization_contract.md).
The decision is S1 for a bounded separate inspection view, not for mixing
anatomical geometry into `neurofly_scene_layout_v1` or rendering all 313
candidate bodies.

Phase 5F realizes only that bounded view. It preserves both DNp01 bodies and
raw components under one uniform `dnp01_morphology_view_v1` transform. Native
axes remain unnamed, source radius is not rendered as calibre, and root/link
ordering carries no signal semantics. The acquisition mode is
`OFFICIAL_MALECNS_BULK_SWC`; neuPrint access is not required for this artifact.
See
[`docs/architecture/malecns_morphology_inspector.md`](architecture/malecns_morphology_inspector.md).

Phase 5G reuses `malecns_morphology_artifact_v1` for the fixed six-body audit
sample: LC4 12032/16128, LPLC2 11498/14465, and DNp01 10001/10010. A new
presentation-only `malecns_six_body_morphology_view_v1` transform is computed
once across every source node. LPLC2 11498 remains two independent components
(9 and 2,112 nodes in canonical root order); no bridge or healed edge is added.

Phase 5I adds a GET-only structural projection for this same sample from the
committed CircuitContract. It validates all six body identities and integrity
hashes, preserves directed edge weights, and exposes no simulation values. The
projection is documented in
[`docs/architecture/structural_connectivity_inspector.md`](architecture/structural_connectivity_inspector.md).

Phase 5J adds `/experiments/[artifactId]/cockpit` as a read-only composition of
the validated experiment artifact, pinned six-body morphology artifact, and
Phase 5I projection. Compatibility checks use dataset, candidate, circuit
integrity, time grid, source modes, and body identities rather than filenames.
Only persisted DNp01 body data receive selected-neuron dynamic readouts;
LC4/LPLC2 encoder drives remain labelled type-level. The event list derives
only timeline boundaries and stored DNp01 spikes. No new biology, simulation,
source geometry, or scientific artifact is created. See
[`docs/architecture/scientific_cockpit.md`](architecture/scientific_cockpit.md).

Phase 5K keeps this source composition and one experiment clock while placing
World, Connectome, Telemetry, selected-neuron data, and the event log in a
viewport-sized desktop workspace. Panel expansion, disclosure controls, and
responsive layout are presentation state only. The dedicated morphology and
standalone playback routes remain available.

Phase 6A adds a cockpit-only activity projection from the persisted experiment
and validated CircuitContract identities. `lc4_drive_mveq` and
`lplc2_drive_mveq` are explicitly type-level under the artifact's
`bilateral_type_broadcast_v1` mapping; they are never assigned to individual
sensory bodies. DNp01 10001/node 0/R and 10010/node 1/L membrane state,
filtered state, and persisted spike events are body-specific point-neuron
results. Where the persisted LIF model and its `-52 mV` rest/`-45 mV` threshold
references match, a normalized model membrane position may modulate a separate
uniform presentation overlay on the corresponding body morphology. It is not
spatial voltage, empirical activity, synapse activity, or propagation. The
dedicated morphology inspector remains static. Details and signal audit are in
[`docs/architecture/activity_structure_mapping.md`](architecture/activity_structure_mapping.md).

Phase 6B is documented in
[`docs/science/motor_escape_feasibility.md`](science/motor_escape_feasibility.md).
The bounded v1.0 audit verified MaleCNS identities and chemical
DNp01→TTMn, DNp01→PSI, and PSI→DLMn edges. Literature-supported electrical
coupling remains a separate, unquantified mechanism; structural contact counts
are not motor efficacy. The recommended Phase 6C target is a reproducible
TTMn model-state extension only, with no muscle mechanics, takeoff label, or
escape behavior.

Phase 6C implements that bounded extension in `neurofly.motor_pathway`: a
separate pinned evidence contract references (without modifying) the existing
313-body `looming_giant_fiber_v1` CircuitContract. Exact persisted DNp01 events
map 10001/R→800146/R and 10010/L→804642/L into a deterministic dimensionless
event integrator. Its `tau_motor_ms=10` and `event_gain=0.25` reference values
are explicit `MODEL_ASSUMPTION`s, not biological or MaleCNS parameters. A
portable nested artifact preserves the original experiment schema and is
served only through an optional GET-only route. The five real reference and
control outputs live under ignored `data/derived/motor_experiments/`. No TTMn
morphology, muscle, fly motion, jump, takeoff, escape, or empirical validation
is added. See
[`docs/science/motor_pathway_model.md`](science/motor_pathway_model.md).

Phase 6D assessed whether the dimensionless Phase 6C parameters can be
physiologically parameterized. The review found no observation operator or
TTMn-specific adult measurement that identifies `tau_motor_ms` or
`event_gain`; Augustin et al.'s 135/34.5 µS gap values are estimated model-fit
values for an end-to-end latency model, not MaleCNS pair conductances. The
recommendation is to retain Phase 6C only as an exploratory causal state and
require an identity-resolved equivalent TTMn observation before quantitative
calibration. Empirical validation remains unchanged. See
[`docs/science/ttmn_parameterization_assessment.md`](science/ttmn_parameterization_assessment.md).

Phase 6E's bounded historical citation-chain audit found no suitable
identity-resolved adult TTMn neuronal observation equivalent to the Phase 6C
dimensionless state. The TTMn quantitative-calibration path is therefore
closed for the reviewed source set, not disproven universally; Phase 6C
remains exploratory with `tau_motor_ms` and `event_gain` as assumptions.
The next scientific focus is evidence-only LC4/LPLC2 sensory-input
individualization feasibility, beginning with a provenance-verified bilateral
MaleCNS column-to-visual-angle mapping gate. No new encoder, motor model,
body mechanics, or empirical validation is implied. See
[`docs/science/ttmn_evidence_closure.md`](science/ttmn_evidence_closure.md).

---

## 1. Project vision

The project aims to build an immersive, scientifically grounded **digital organism / connectome-based agent** inspired by the recently published **MaleCNS Drosophila melanogaster connectome**.

The central idea is to place a digital fly inside interactive 3D environments and observe, measure and compare its behaviour under controlled experimental conditions.

The project should combine two qualities that must remain equally important:

1. **Scientific/technical substance**
   - behaviour must be linked as directly as realistically possible to neural activity derived from the MaleCNS connectome;
   - experiments should have explicit variables, hypotheses and measurable outcomes;
   - the system must distinguish biological data from modelling assumptions introduced by the software;
   - results must be reproducible and inspectable.

2. **Immersive visual experience**
   - the user should be able to watch the fly moving through a 3D world in real time;
   - camera, lighting, environmental effects, animation and UI should make the experience visually strong enough for a portfolio/showcase;
   - neural activity, sensory state and behavioural metrics should be visible while the experiment runs;
   - the experience should feel like a scientific simulation product, not a basic graph demo.

The intended result is not merely “a fly playing a game”. It is an **experimental platform for studying behaviour in connectome-based digital agents**.

A possible long-term positioning statement is:

> “An experimental platform for studying emergent behaviour, adaptation and digital individuality in connectome-based agents.”

This wording does **not** claim consciousness.

---

## 2. Scientific foundation

### 2.1 MaleCNS

The project is based on the public MaleCNS connectome of an adult male fruit fly (*Drosophila melanogaster*).

Relevant characteristics already identified during project exploration:

- approximately 166,691 neurons;
- brain plus ventral nerve cord / central nervous system coverage;
- very large synaptic connectivity dataset;
- neuron morphology, annotations, connectivity and other metadata are publicly available;
- access is possible through official downloadable datasets and neuPrint tooling/API;
- the dataset can be used as a structural graph of biological neural connectivity.

Official project/data source:
- MaleCNS / HHMI Janelia
- Google Research was involved in the connectomics reconstruction pipeline.

### 2.2 Critical scientific distinction

The MaleCNS dataset is primarily a **connectome / structural wiring diagram**.

It does not automatically provide a complete executable biological brain.

The software therefore must distinguish between:

#### Biological data
Examples:
- neuron identities;
- neuron morphology;
- connectivity;
- synapse counts/locations where available;
- cell/neuron types;
- predicted neurotransmitters where available;
- anatomical regions.

#### Model assumptions introduced by us
Examples:
- neural dynamics model;
- membrane thresholds;
- time constants;
- input encoding;
- mapping neural outputs to movement;
- reward signals;
- plasticity rules;
- sensor design;
- environmental interpretation.

Any UI, documentation or portfolio description should make this distinction explicit.

### 2.3 Claims we must NOT make without evidence

Do not claim that the project:
- recreates a living fly;
- reproduces the complete biological dynamics of a fly;
- creates consciousness;
- proves consciousness;
- creates “a conscious digital organism”;
- proves real memory or learning merely because behaviour changes;
- perfectly simulates all 166k neurons unless that has actually been implemented and validated.

Preferred language:
- “connectome-based simulation”;
- “biologically inspired neural dynamics”;
- “structural connectivity derived from MaleCNS”;
- “adaptive behaviour” only after suitable experimental evidence;
- “digital individuality” as an experimental concept, not consciousness.

---

## 3. Core research question

The broad question is:

> **What behaviour emerges when neural connectivity derived from a real biological connectome is placed inside an artificial closed-loop environment?**

The platform should eventually make it possible to investigate questions such as:

- How does the digital organism respond to different visual stimuli?
- How do obstacle layouts change its trajectory and neural activity?
- Can selected neural circuits produce consistent sensory-to-motor behaviour?
- What happens when the environment changes during a run?
- Can biologically plausible plasticity mechanisms produce measurable adaptation?
- If two initially identical agents experience different environments, do their later behaviours diverge when they are returned to the same environment?
- Which neural pathways correlate with specific observable actions?
- How robust is behaviour to perturbations, sensory noise or selected circuit disruptions?

These are experimental questions. The product should help measure them rather than predetermine the answers.

---

## 4. Closed-loop simulation model

The fundamental runtime loop is:

```text
3D ENVIRONMENT
      ↓
sensory state
      ↓
sensory encoding
      ↓
connectome-derived neural simulation
      ↓
descending / motor outputs
      ↓
movement / actions
      ↓
environment changes
      ↓
new sensory state
      ↺
```

The fly must not be controlled by a conventional LLM or manually scripted policy if the experiment is intended to measure connectome-derived behaviour.

The aim is that observable movement is causally connected to the neural simulation as much as practical.

---

## 5. Experimental “worlds”

The project should support multiple controlled worlds/arenas.

Each world is an **experiment**, not just a level.

Each experiment should define:

- hypothesis/question;
- independent variables;
- controlled variables;
- environmental configuration;
- initial fly/neural state;
- duration / termination conditions;
- repeated trials if appropriate;
- metrics;
- expected data capture;
- replay support.

Potential initial worlds:

### World 0 — Baseline
Simple neutral arena.

Purpose:
- establish baseline locomotion;
- detect biases and instability;
- benchmark simulation.

Possible metrics:
- total distance;
- average speed;
- turn distribution;
- time stationary;
- trajectory entropy;
- neural activity by region/circuit.

### World 1 — Light / Dark
Arena with controlled illumination zones.

Purpose:
- examine visual input and spatial preference;
- relate visual activation to movement.

Possible metrics:
- time per zone;
- transition frequency;
- reaction latency;
- sensory activity;
- descending/motor activity.

### World 2 — Obstacle Course
Obstacles of known geometry.

Purpose:
- analyse navigation;
- measure sensory-to-motor response;
- study repeated collision/avoidance patterns.

Possible metrics:
- collisions;
- path length;
- turning behaviour;
- time to goal;
- neural activity around obstacle encounters.

### World 3 — Resource Search
Introduce a target/reward/resource.

Purpose:
- study exploration and target-directed behaviour;
- later serve as a foundation for plasticity experiments.

### World 4 — Adversity / Avoidance
Introduce controlled aversive zones or stimuli.

Purpose:
- evaluate avoidance;
- later test whether previous adverse experience changes future behaviour.

### World 5 — Changing World
Modify environmental conditions during the same experiment.

Purpose:
- test robustness and adaptation;
- compare behaviour before and after a controlled environmental change.

These worlds are a starting taxonomy, not a final fixed list.

---

## 6. Long-term individuality experiment

One of the most interesting later experiments is:

```text
SAME INITIAL CONNECTOME / SAME INITIAL PARAMETERS
                    │
             ┌──────┴──────┐
             ↓             ↓
           Fly A         Fly B
             │             │
       Experience A   Experience B
             │             │
       plastic changes / state changes
             │             │
             └──────┬──────┘
                    ↓
              SAME TEST WORLD
                    ↓
          compare later behaviour
```

Goal:

Investigate whether different histories lead to persistent behavioural differences when both agents later face the same environment.

This may be described as studying **digital individuality** or **experience-dependent divergence**.

It must not be presented as proof of consciousness or personal identity.

---

## 7. Visual experience

The project should look like an immersive scientific simulation.

The user should be able to:

- watch the fly move in real time;
- orbit/free-camera around the arena;
- optionally follow the fly;
- switch to top-down or analysis cameras;
- pause/resume;
- change simulation playback speed;
- reset a run;
- view the trajectory/path;
- inspect current sensory input;
- inspect neural activity;
- inspect selected circuits/regions;
- view live behavioural metrics;
- replay previous runs;
- compare multiple runs.

Possible UI structure:

```text
┌──────────────────────────────────────────────────────────────┐
│ Experiment / world / run state                               │
├─────────────────────────────────┬────────────────────────────┤
│                                 │                            │
│          3D WORLD               │     LIVE INSPECTOR         │
│                                 │                            │
│        digital fly              │ sensory state              │
│        environment              │ neural activity            │
│        trajectory               │ motor state                │
│                                 │ behavioural metrics        │
│                                 │                            │
├─────────────────────────────────┴────────────────────────────┤
│ Play | Pause | Speed | Reset | Timeline | Replay             │
└──────────────────────────────────────────────────────────────┘
```

Desired visual direction:
- scientific laboratory + digital terrarium;
- immersive but clean;
- modern, minimal UI;
- strong lighting and camera work;
- subtle sci-fi feeling without turning the project into fiction;
- scientific data remains readable and credible.

---

## 8. 3D and rendering architecture

Blender is **not** intended to be the runtime engine.

### Blender responsibilities
Use Blender for:
- creating/editing the fly model;
- rigging/animation if needed;
- environmental assets;
- exporting `.glb` / `.gltf`.

### Browser runtime
Use:
- **Three.js**
- **React Three Fiber**
- **@react-three/drei**
- potentially **Rapier / @react-three/rapier** for collisions/physics.

The browser is responsible for:
- rendering;
- interpolation between simulation states;
- camera;
- lighting;
- animation;
- effects;
- UI/interaction.

The graphics renderer may run at ~60 FPS even if neural simulation ticks are slower.

Example separation:

```text
NEURAL / BEHAVIOURAL SIMULATION
10–30+ simulation updates per second
            ↓
state snapshots
            ↓
       WebSocket
            ↓
3D RENDERER
~60 frames per second
            ↓
interpolation / animation
```

Do not force neural simulation frequency to equal display FPS.

---

## 9. Current proposed technology stack

### Frontend / product UI
- Next.js
- React
- TypeScript
- React Three Fiber
- Three.js
- @react-three/drei
- optional @react-three/rapier
- Tailwind CSS for application UI if appropriate

### Simulation / scientific backend
- Python
- FastAPI
- NumPy
- SciPy / sparse matrices
- NetworkX initially where convenient for graph exploration
- neuPrint Python tooling for MaleCNS access
- possible Numba/Cython/Rust optimisation later if profiling justifies it

### Realtime communication
- WebSockets between simulation service and frontend.

### Data / persistence
Potentially:
- PostgreSQL / Supabase for experiment metadata;
- object/file storage for larger run/replay files;
- simple local files during earliest prototypes.

Do not add database infrastructure before it is needed.

### 3D asset creation
- Blender
- export GLB/GLTF.

### Deployment
Early development:
- simulation runs locally;
- frontend locally.

Public portfolio version:
- frontend can be deployed separately;
- recorded experiment/replay data can be served cheaply;
- heavy live simulation does not need to be publicly hosted initially.

Potential public split:

```text
RESEARCH MODE
live simulation
local workstation
        +
SHOWCASE MODE
recorded/replay experiments
public website
```

Possible future optimisation:
- WebAssembly;
- Web Workers;
- TypedArrays;
- SharedArrayBuffer where applicable;
- run some simulation workload on the visitor's device.

This is an optimisation/research phase, not an MVP requirement.

---

## 10. Cost constraints

Goal for initial development: **approximately €0 infrastructure cost**.

Avoid introducing paid services unless:
- profiling proves they are needed;
- deployment requirements justify them;
- the user explicitly approves the expense.

No paid LLM API is required for the core simulation.

An LLM must NOT control the fly.

A future optional AI layer may be used for:
- querying the connectome in natural language;
- explaining experimental results;
- generating summaries;
- assisting analysis.

That is secondary to the scientific simulation.

---

## 11. Data model: experiment/run concept

A useful conceptual hierarchy is:

```text
Project
  └── World / Experiment Definition
       ├── hypothesis
       ├── environment parameters
       ├── neural configuration
       ├── simulation configuration
       └── Runs
            ├── seed
            ├── initial state
            ├── timeline
            ├── sensory data
            ├── neural summaries
            ├── motor outputs
            ├── transforms / trajectory
            ├── events
            └── metrics
```

Runs should become reproducible where possible.

Store enough information to:
- replay them;
- compare them;
- analyse them offline;
- reproduce them from seed/config when deterministic behaviour is intended.

---

## 12. Telemetry and replay

Replay is a major part of the product, not an afterthought.

A run should eventually capture data such as:

- timestamp / simulation tick;
- fly position;
- fly rotation;
- velocity;
- sensory inputs;
- motor outputs;
- selected neural state or aggregate activity;
- collisions;
- events;
- environment changes;
- reward/aversive events if applicable;
- experiment metrics.

The public website may replay precomputed experiments without rerunning expensive neural simulation.

This preserves:
- strong visuals;
- inspectability;
- low hosting costs.

---

## 13. Neural inspection / explainability

A later major feature should allow the user to inspect the neural side of behaviour.

Examples:

- click a region/circuit;
- inspect activity over time;
- show relevant upstream/downstream connectivity;
- select a behaviour event and inspect neural activity around it;
- compare activation between trials.

Possible conceptual feature:

> “Why did the fly turn left here?”

The UI could trace:

```text
environmental event
      ↓
sensory encoding
      ↓
relevant neural activity
      ↓
descending/motor outputs
      ↓
observed behaviour
```

This should be based on recorded simulation data and known graph structure, not fabricated explanations.

---

## 14. Performance philosophy

Do not attempt the full 166k-neuron simulation on day one.

Start with:
- data access;
- selected circuits;
- reduced subgraphs;
- simplified neural dynamics;
- measurable closed-loop behaviour.

Scale only after the architecture is validated.

Performance work must be profiling-driven.

Potential future steps:
- compact neuron indexing;
- sparse adjacency structures;
- vectorised simulation;
- NumPy/SciPy sparse;
- Numba;
- multiprocessing where suitable;
- Rust native module / PyO3 if justified;
- WASM for browser-side simulation experiments.

Do not optimise prematurely.

---

## 15. Implementation roadmap

This roadmap is a working plan. Each phase should have an explicit gate and acceptance criteria.

### Phase 0 — Repository foundation and scientific brief
Goals:
- create repository/monorepo structure;
- establish README and architecture docs;
- document biological vs model assumptions;
- define code quality gates;
- define experiment terminology;
- keep implementation minimal.

Gate:
- build/lint/typecheck/test skeleton green;
- clear project docs;
- no unnecessary architecture.

### Phase 1 — MaleCNS data access
Goals:
- connect to/download a manageable official data subset;
- create reproducible data ingestion/query tooling;
- inspect neurons/connectivity;
- define internal graph representation;
- cache only what is needed.

Gate:
- a documented script/query retrieves real MaleCNS data;
- tests validate parsing/normalisation;
- no fake connectome data in production path.

### Phase 2 — Neural simulation core
Goals:
- implement a small selected circuit/subgraph;
- implement an explicit neural dynamics model;
- make all assumptions configurable/documented;
- deterministic seeded runs where possible;
- unit tests around the simulation.

Gate:
- neural state evolves correctly under controlled test inputs;
- outputs are reproducible;
- simulation does not yet need 3D.

### Phase 3 — Immersive 3D vertical slice
Goals:
- Next.js/React Three Fiber app;
- simple arena;
- fly model or temporary high-quality placeholder;
- follow/orbit camera;
- lighting/shadows;
- simple collision system;
- realtime state interpolation.

The fly may initially use synthetic movement solely to validate the visual pipeline, but this must be clearly temporary.

Gate:
- visually polished 3D fly/arena runs smoothly;
- UI and camera usable;
- architecture ready to receive backend state.

### Phase 4 — Closed-loop sensory → neural → motor
Goals:
- define first environment sensor(s);
- encode sensory input into selected MaleCNS circuit;
- neural simulation produces motor outputs;
- motor outputs control the 3D fly;
- close the loop.

Gate:
- the fly's movement is generated from the neural simulation;
- a controlled environmental change causes measurable neural/motor/behavioural response;
- manual/scripted movement is removed from experimental mode.

### Phase 5 — Experiment framework / first worlds
Goals:
- experiment definitions;
- Baseline;
- Light/Dark;
- Obstacle Course;
- metrics;
- seeds;
- repeated runs.

Gate:
- same experiment can be repeated;
- metrics are generated;
- results can be compared.

### Phase 6 — Telemetry, timeline and replay
Goals:
- record run data;
- replay without neural recomputation;
- timeline;
- trajectory visualisation;
- live metrics;
- selected neural activity panel.

Gate:
- completed experiment can be replayed accurately;
- public showcase can display recorded experiments.

### Phase 7 — Plasticity / adaptation
Goals:
- research suitable biologically motivated learning/plasticity rule;
- implement behind explicit configuration;
- compare control vs plasticity conditions;
- run repeated trials;
- avoid calling changes “learning” without evidence.

Gate:
- statistically/experimentally meaningful behaviour comparison;
- reproducible protocol;
- documentation separates observed result from interpretation.

### Phase 8 — Digital individuality experiment
Goals:
- identical starting agents;
- different experience histories;
- later common test environment;
- compare behavioural divergence;
- inspect neural/state differences.

Gate:
- experiment methodology and results are reproducible;
- conclusions remain conservative.

### Phase 9 — Scaling / whole-connectome performance research
Goals:
- profile real bottlenecks;
- expand subgraphs/circuit coverage;
- investigate larger-scale MaleCNS simulation;
- optimise only where measured.

Gate:
- benchmarks documented;
- memory/CPU requirements measured;
- no claim of full MaleCNS execution unless demonstrated.

### Phase 10 — Public portfolio release
Goals:
- polished landing/project narrative;
- immersive live/replay experience;
- methodology;
- architecture;
- scientific limitations;
- GitHub documentation;
- selected benchmark/results;
- CV/LinkedIn-ready project description.

---

## 16. Repository architecture direction

Do not force this exact layout before inspecting implementation needs, but the intended separation is:

```text
neurofly/
├── apps/
│   └── web/                  # Next.js / R3F product + visualisation
├── services/
│   └── simulation/           # Python / FastAPI / neural simulation
├── packages/
│   └── contracts/            # optional shared schemas/contracts
├── data/
│   └── ...                   # local/cache strategy; large data ignored
├── docs/
│   ├── architecture/
│   ├── science/
│   ├── experiments/
│   └── decisions/
├── scripts/
└── README.md
```

Important:
- large MaleCNS datasets must not accidentally be committed to Git;
- data acquisition should be reproducible;
- contracts between frontend/backend should be explicit;
- avoid premature microservices.

---

## 17. Development principles

1. **Scientific integrity over spectacle**
   - the visuals may be impressive, but behaviour must not be falsely presented as biological if it is scripted.

2. **Visual quality still matters**
   - this is intended to be a flagship portfolio project.

3. **Vertical slices**
   - build thin end-to-end functionality instead of large disconnected systems.

4. **Small circuit before full connectome**
   - prove the pipeline first.

5. **Measure before optimising**
   - profiling before Rust/WASM/GPU complexity.

6. **Reproducibility**
   - seeds, configs, experiment metadata and replay.

7. **Explicit assumptions**
   - every major modelling decision belongs in documentation.

8. **No hidden LLM brain**
   - an LLM must not secretly make behavioural decisions in an experiment presented as connectome-driven.

9. **Test important scientific logic**
   - especially dynamics, data transformation, experiment reproducibility and metrics.

10. **Keep public claims conservative**
    - interesting results do not justify claims of consciousness.

---

## 18. Role of Codex

Codex is expected to perform much of the repository implementation.

ChatGPT Project chats will be used to:
- reason about architecture;
- research approaches;
- define scientific scope;
- review Codex output;
- design implementation phases;
- generate detailed Codex prompts;
- analyse test/build results;
- decide next steps.

Prompts provided to Codex should normally be implementation-ready and single-pass.

Each significant Codex prompt should include:

- current phase and objective;
- repository context;
- required read-only inspection first;
- exact scope;
- non-goals;
- architectural invariants;
- scientific invariants;
- likely areas/files but instruction to inspect actual repo rather than assume paths;
- implementation requirements;
- data-contract requirements;
- error-handling expectations;
- test requirements;
- lint/typecheck/build commands or instruction to discover canonical project gates;
- acceptance criteria;
- stop conditions;
- restrictions on unrelated changes;
- Git/status/staging/commit instructions when appropriate;
- expected final report.

Codex must inspect the actual repository state before editing and must report discrepancies rather than blindly following stale assumptions.

---

## 19. Preferred Codex workflow

For non-trivial phases:

```text
1. Read repository / relevant docs
2. Report factual current state
3. Identify conflicts with requested phase
4. Implement only authorised scope
5. Add/update tests
6. Run relevant gates
7. Review diff
8. Report:
   - files changed
   - architecture decisions
   - tests/gates
   - limitations
   - next recommended step
9. Commit only when the prompt explicitly authorises it
```

Avoid:
- broad opportunistic refactors;
- dependency churn;
- rewriting unrelated working code;
- changing scientific semantics to make tests easier;
- silently substituting fake data.

---

## 20. Definition of a strong MVP

The first truly meaningful MVP is not simply a rendered fly.

A strong MVP demonstrates:

1. real MaleCNS-derived connectivity for a selected circuit/subgraph;
2. explicit neural dynamics;
3. environmental sensory input;
4. neural processing;
5. motor output;
6. autonomous movement in the 3D world;
7. live telemetry showing that chain;
8. at least one controlled experiment;
9. recorded/replayable run;
10. documentation of model assumptions and limitations.

In one sentence:

> **A user can watch a digital fly move autonomously through a polished 3D environment while real MaleCNS-derived neural connectivity participates in the sensory-to-motor loop, and the resulting neural and behavioural data can be measured and replayed.**

---

## 21. Portfolio objective

This project is intended to become a technically distinctive flagship project.

It should demonstrate a combination of:

- full-stack engineering;
- TypeScript/React;
- 3D web graphics;
- Python backend development;
- realtime systems;
- scientific computing;
- graph processing;
- neuroscience/connectomics;
- simulation;
- data visualisation;
- performance engineering;
- testing/reproducibility;
- technical communication.

A future CV description should focus on what was actually implemented and measured.

Do not list planned technologies/features as completed work.

---

## 22. Current decisions — concise summary

Already decided:

- build an immersive 3D digital-fly experimental platform;
- use MaleCNS as the biological structural foundation;
- behaviour should be connectome/neural-simulation driven;
- multiple worlds are controlled behavioural experiments;
- scientific metrics and neural inspection are first-class features;
- frontend: Next.js + React + TypeScript;
- 3D: Three.js + React Three Fiber;
- Blender for asset creation, not runtime;
- backend/simulation: Python + FastAPI;
- realtime: WebSockets;
- scientific computation: NumPy/SciPy, with NetworkX useful initially;
- persistence can use PostgreSQL/Supabase when needed;
- develop live simulation locally first;
- public site may replay precomputed runs to avoid hosting costs;
- potential later WASM/browser simulation;
- no LLM controlling the organism;
- no consciousness claims;
- start with selected circuits/subgraphs and scale progressively;
- first data-access candidate: `LC4` + `LPLC2` with `DNp01` as the initial
  endpoint, selected from `male-cns:v1.0` as `looming_giant_fiber_v1`;
- keep visual immersion and scientific credibility equally important.

Not yet decided/final:
- final project name;
- exact repository structure;
- exact circuit used for the later first closed-loop behavioural simulation;
- exact neural dynamics model;
- exact sensory encoding;
- exact motor mapping;
- exact physics model;
- exact hosting provider for simulation;
- whether/when to use Rust/WASM;
- detailed visual art direction/assets;
- plasticity mechanism;
- public release date.

These undecided items should be resolved through research, profiling and implementation evidence rather than guessed in advance.

---

## 23. Source-of-truth rule

When a future ChatGPT/Codex conversation conflicts with this document:

- prefer **the actual current repository state** for implementation facts;
- prefer **official MaleCNS/scientific sources** for biological facts;
- prefer **new explicit user decisions** over old design assumptions;
- update this context/document when a major decision changes.

This document describes project intent and current agreed direction. It must not be used as proof that a planned feature has already been implemented.
