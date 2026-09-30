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
Phase 7F now routes only these four replay-verified exploratory states to the
correct two DNp01 LIF bodies through
`exploratory_edge_routed_model_drive_v1`. The shared positive reference
`k_transfer_mveq_per_state = 1.0` is a model assumption; the four MaleCNS
chemical structural counts determine routing only. The separate immutable
artifact is
`4a000add359e60c0c0c654881a4659652d749c548af0e167469d210035c20213`.
The reference produces small subthreshold DNp01 model responses; no
physiological calibration, TTMn propagation, behavior, 311-body dynamics, or
frontend change follows. See the [Phase 7F transfer boundary](science/relative_column_sensory_to_dnp01.md).

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

## 24. Phase 7G — sensory-to-DNp01 evidence and scale gate

The committed Phase 7F four-body transfer remains an exploratory model. Primary
pathway activation/perturbation and GF recording evidence supports a positive
LC4→DNp01 and LPLC2→DNp01 population-level contribution, but no reviewed
evidence identifies a unitary body-specific transfer. MaleCNS v1.0 predicts
acetylcholine for all selected LC4/LPLC2 bodies; this is aggregate transmitter
prediction, not pair-specific efficacy. Phase 7E state has no observation
operator to measured sensory output, so the shared `k_transfer` remains
`NOT_IDENTIFIABLE` and a `MODEL_ASSUMPTION`; structural counts remain routing
metadata only. The selected next scale is a deterministic, balanced 16-body
architecture experiment—not biological calibration. The current Phase 7F
artifact remains four-body-specific and must not be silently widened.

Phase 7H adds a separately versioned, outcome-independent 16-body experiment:
four LC4/LPLC2 bodies in each type×side stratum, retaining the Phase 7F
sentinels. The persisted sample is
`18717531d02506fc988c9e70dcf916d62c6bbae3981827e16a4453821efb04d7`; the
replay-verified population experiment is
`385480b3c915b25536e1119d17effa15567bc0c1afcfe73037e5dd5d69102958`.
Phase 7D assignment semantics, Phase 7E's dimensionless `tau_sens_ms=1.0`,
`gain=1.0` assumptions, Phase 7F's shared `k_transfer=1.0 mV_eq/state`, and
the existing DNp01 LIF model are unchanged. The 16-body run demonstrates
identity-resolved architecture and deterministic replay only; structural
counts remain routing/selection metadata, and no biological calibration or
313-neuron simulation is claimed. The current scale gate is `HOLD_AT_16`.
See [the Phase 7H bounded population experiment](science/bounded_16_body_sensory_experiment.md).

Phase 7I retains that exact sample and its six stimuli, then adds four
anatomy-only radius-one relative-column disks centered on source columns to
cover the six bodies that had zero Phase 7H exposure. The separately versioned
coverage plan `2b73f7c7707942be2644c5dfc0fcbed41be682c4877457ac86b6411619e8cd34`
was persisted before new sensory or DNp01 outcomes were computed. The replayed
coverage experiment
`5d2953a0e20e471cdf26de0dae16ffff75b8cab159e3fbfcbb959a5349117e87` exercises
all 16 bodies through positive anatomical exposure, exploratory state, and
the source-derived transfer path (`16/16` for each software coverage metric).
Phase 7E/7F assumptions and the DNp01 readout are unchanged; no body spikes or
behavior are claimed. This closes Phase 7I software-path coverage only, not
functional receptive-field coverage or biological validation. The independent
Phase 7J sample robustness result is recorded below. See
[the Phase 7I coverage validation](science/bounded_16_body_coverage_validation.md).

## 25. Phase 7J — disjoint 16-body robustness

Phase 7J selected an independent, outcome-blind Sample B of 16 sensory bodies
(four per LC4/LPLC2 × side stratum), disjoint from immutable Phase 7H Sample A.
The persisted sample is
`873d6e9e32ce08916fb69462548af11f2cbadf394d91966641e6bc17839bcf33`; its
anatomy-only coverage plan is
`b718607e0cf671cc06454a6422ea7c3b48107516c59291b2fe01f9a244a9079f`, and its
replay-verified experiment is
`f5fd68c1ea8b248f206af9be58fd9adeef604cd2e770289d8f32711ccbba6026`. Four
source-column radius-one disks extended the retained Phase 7I battery and
exercised 16/16 bodies through positive anatomical exposure, exploratory
sensory state, and structural-route transfer. The Phase 7E state assumptions,
Phase 7F shared transfer coefficient, and DNp01 LIF configuration were
unchanged; structural counts remain descriptive metadata and do not scale
transfer. This demonstrates deterministic architecture/replay robustness for
one disjoint sample only—not biological population validation, 32-/311-body
simulation, or a completed 313-neuron circuit. The result supports a bounded
Phase 7K 32-body architecture experiment as the next scale gate; that run has
not been implemented. See
[the Phase 7J robustness assessment](science/disjoint_16_body_robustness.md).

## 26. Phase 7K — simultaneous 32-body composition

Phase 7K composes the persisted, disjoint Phase 7H Sample A and Phase 7J
Sample B into exactly 32 bodies (eight per LC4/LPLC2 × side stratum), without
new selection. The immutable composition artifact is
`82ebef1acef2415fd57b9922e815e87e2d60fd76070a93e67103e2f3924198bf`; its
experiment artifact is
`b6be84a66d3cecde3e7bf05992515dc31521a8ebc5e8feebadf9b5f0560d9405`. The
existing Sample B 14-stimulus relative-column battery covered 32/32 bodies
through anatomical exposure, exploratory state, and transfer. Nested A/B
regressions, same-side CircuitContract routing, per-step source accounting,
and target-drive additivity passed. Phase 7E state assumptions, Phase 7F
shared `k_transfer`, and DNp01 LIF semantics remain unchanged; structural
counts remain routing metadata only. Decision: `SCALE_TO_64` for another
bounded architecture experiment, not biological validation or readiness for
311/313-neuron execution. See
[the Phase 7K composition assessment](science/simultaneous_32_body_composition.md).

## 27. Phase 7L — simultaneous 64-body composition

Phase 7L keeps the persisted 7H/7J samples A/B immutable, then selects and
persists outcome-blind, disjoint samples C/D before model execution. The exact
union contains 64 bodies (16 in each LC4/LPLC2 × side stratum), with all six
pairwise overlaps empty. Its composition, anatomy-only 19-stimulus coverage
plan, and experiment artifacts are respectively
`db5df9b639f5ed834a4e2f408e39bec264552427260eadd8eb8789bcdf431436`,
`d92627cb1787b2b566e37d333064d259e5347aae6781b8381558dda233561536`, and
`5095eddbf35c363cf4ae47ef875420ecad725eb0c837767ec8789e65bd68ab02`. All
64 bodies pass software-path stimulus/state/transfer coverage, source-derived
routing, per-step source accounting, A+B+C+D additivity, nested Phase 7K
regression, and full deterministic replay. The Phase 7E state assumptions,
shared Phase 7F `k_transfer`, and DNp01 LIF remain unchanged; structural
counts remain metadata only. The 14.85 MB experiment replayed in about 24.6 s
in the current environment. Decision: `SCALE_TO_128`, as a next bounded
architecture/performance observation only; this is not biological validation,
311-body dynamics, or a completed 313-neuron circuit. See
[the Phase 7L composition and scaling assessment](science/four_sample_64_body_composition.md).

## 28. Phase 7M — simultaneous 128-body composition

Phase 7M preserves A–D and selects/persists outcome-blind, disjoint samples
E–H before planning anatomy-only coverage or computing model outputs. The
exact A–H union has 128 bodies (32 per LC4/LPLC2 × side stratum), four added
radius-1 source-column stimuli, and 128/128 software-path stimulus/state/
transfer coverage. Source-derived routing, per-step accounting, A–D-only
regression to Phase 7L, and deterministic full replay pass. Phase 7E/7F
parameters and DNp01 dynamics remain unchanged; structural counts remain
metadata only. The 31.45 MB artifact replays in about 27.3 s in this
environment. Decision: `PREPARE_311_EXECUTION_ARCHITECTURE`—prepare arbitrary-N
and dry-run evidence only; do not execute 311 bodies yet. This is not biological
validation or a completed 313-neuron circuit. See
[the Phase 7M scaling assessment](science/eight_sample_128_body_scaling.md).

## 29. Phase 7N — all-311 architecture readiness (dry run)

Phase 7N derives the complete 126 LC4 + 185 LPLC2 identity set directly from
the pinned MaleCNS contracts, validates all 311 column topologies and direct
DNp01 routes, and extends the inherited synthetic relative-column battery to
311/311 anatomy-only coverage. A deterministic dry-run manifest records the
unchanged Phase 7E/7F/DNp01 configurations and expected future dimensions;
no 311 sensory states, transfer ledger, or DNp01 dynamics were executed.
Historical fixed-size artifacts remain unchanged and replayable. Decision:
`READY_FOR_311_BOUNDED_EXECUTION`. This is an architecture/readiness result,
not biological validation or a completed 313-neuron circuit. See
[the Phase 7N readiness assessment](science/all_311_sensory_population_readiness.md).

## 30. Phase 7O — complete exploratory 313 model-state milestone

Phase 7O executed the committed 311-body population and 27-stimulus battery:
311/311 sensory states and identity-resolved transfer paths fed the two existing
DNp01 LIF model neurons. The 130,931-row contribution ledger, Phase 7E
sentinels, Phase 7M 128-body subset, source accounting and deterministic replay
passed. The immutable result artifact ID is
`99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5`.
The shared transfer coefficient and sensory/DNp01 parameters were unchanged;
MaleCNS structural counts remain metadata. This completes **313 explicit
exploratory model states**, not calibrated visual physiology or biological
looming validation. Phase 8A should bound the next neural→motor interface
question. See [the Phase 7O execution assessment](science/all_311_sensory_population_execution.md).

## 31. Phase 8A — DNp01-to-motor interface assessment

Phase 8A audited the Phase 7O output and Phase 6C event-driven TTMn contract.
The existing `DNp01_SPIKE_EVENT_ONLY` boundary remains the smallest
defensible exploratory interface: Phase 7O produced no simulated DNp01 spikes
in its reference run or tested `k=0,1,2` conditions, so its event-driven TTMn
input is correctly zero. No sensory transfer or DNp01 threshold was retuned.
MaleCNS chemical DNp01→TTMn counts remain structural metadata; electrical
coupling evidence does not provide pair-specific conductance. Phase 6C's
dimensionless TTMn state remains exploratory and is not muscle/behavior.
Decision: validate the motor interface next using a provenance-separated
`SYNTHETIC_MOTOR_INTERFACE_TEST`, not a fabricated Phase 7O event. No
production code, API, or frontend changed. See
[the Phase 8A DNp01-to-motor interface assessment](science/dnp01_motor_interface_assessment.md).

## 32. Phase 8B — synthetic DNp01 event to TTMn interface

Phase 8B validates six deterministic `SYNTHETIC_MOTOR_INTERFACE_TEST`
fixtures (zero, unilateral, bilateral, and repeated events) through the exact
Phase 6C DNp01 identity routes and unchanged TTMn exploratory integrator. The
synthetic event config/result are separately content-addressed; the Phase 6C
same-upstream-run invariant was not weakened, and no synthetic event was
inserted into Phase 7O. Artifact ID:
`4321adeee0412a79632ce4e008a1b8eaad22ee167f97f4a98521a9e71d9ef936`. A
zero-event fixture leaves both dimensionless TTMn
states at zero; one event routes only to its identity-matched target. Structural
counts remain metadata and `tau_motor_ms=10`, `event_gain=0.25` remain
`MODEL_ASSUMPTION`. This is an architecture/timing test, not sensory-derived
motor activation, muscle output, behavior, or physiological validation. See
[the Phase 8B synthetic motor-interface assessment](science/synthetic_dnp01_ttmn_interface.md).

## 33. Phase 8C — persisted Phase 7O event to TTMn adapter

Phase 8C adds a condition-explicit, provenance-preserving adapter from the
immutable Phase 7O artifact to the unchanged Phase 6C event mapper and TTMn
integrator. It accepts only persisted `SIMULATED_DNP01_MODEL_SPIKE` records,
never infers events from voltage/drive/state, and keeps provenance distinct
from Phase 8B's `SYNTHETIC_MOTOR_INTERFACE_TEST`. The canonical Phase 7O
`reference_bilateral` condition and all 35 persisted conditions contain zero
events; the resulting Phase 8C artifact therefore has zero mapped inputs and
exactly zero TTMn state on both sides. Artifact ID:
`5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf`.
Phase 6C's same-upstream-run invariant, motor parameters, and routes remain
unchanged; structural counts remain metadata. This validates truthful
zero-event composition and deterministic replay, not sensory-driven motor
activation, TTMn physiology, muscle output, or behavior. See
[the Phase 8C end-to-end adapter assessment](science/sensory_dnp01_ttmn_end_to_end_adapter.md).

## 34. Phase 8D — PSI/DLMn motor-branch evidence assessment

Phase 8D revalidated the scope of the pinned `looming_giant_fiber_v1`
CircuitContract: it remains LC4/LPLC2/DNp01 only. A separate committed Phase
6B audit records a bounded MaleCNS v1.0 query for DNp01→TTMn, DNp01→PSI, and
PSI→DLMn chemical routes, with candidate PSI/DLMn identities; its query
response has no independent content hash and is not an expanded CircuitContract.
Primary literature supports mixed electrical/chemical GF→TTMn and GF→PSI
pathway organization and positive cholinergic PSI→DLMn transmission. Fayyazuddin
et al. report a class-level MN5 EPSP, but it does not identify gains for exact
MaleCNS edges. Structural counts remain metadata; delay, pair conductance, and
per-edge efficacy remain unresolved. Decision: add a separately versioned,
no-dynamics motor identity/route contract only; PSI/DLMn dynamics are not
approved. No code, source artifact, motor model, muscle, or behavior changed.
See [the Phase 8D branch assessment](science/psi_dlmn_motor_branch_assessment.md).

## 35. Phase 8E — pinned motor neural structural contract

Phase 8E reconstructed the bounded Phase 6B MaleCNS v1.0 query against the
official annotation snapshot and live neuPrint source. The immutable
`motor_neural_pathway_contract_v1` has 16 source-identified nodes, 16
historical DNp01/TTMn/PSI/DLMn chemical pathway edges, and two separately
labeled supplemental PSI↔PSI chemical edges. The bounded direct
DNp01→candidate-DLMn query returned zero edges. Query-response SHA-256:
`845c1c1ddc60183fd02f8ac2ceaac5e1a16cba34c803707fb974e7b52861e43e`;
contract ID:
`a12b0115c7e50fac3df92bf66d151b3a145aa630f472277226a7d05dc915b22c`.
Offline replay is deterministic and explicit live refresh returned `MATCH`.
The contract preserves chemical structural counts as metadata, keeps
literature electrical/mixed evidence separate, and contains no dynamics.
Phase 6C/8C DNp01→TTMn identities/counts remain an exact compatible subset;
historical artifacts were not migrated. Decision:
`MOTOR_STRUCTURAL_CONTRACT_PINNED`. No PSI/DLMn dynamics, API, or frontend
changes. See [the Phase 8E motor structural contract assessment](science/motor_neural_pathway_contract.md).

## 36. Phase 8F — PSI/DLMn event-model readiness

Phase 8F replayed the pinned Phase 8E contract and assessed a minimal
synthetic DNp01 event→PSI→DLMn vertical slice. The proposed first model is an
identity-resolved, zero-added-delay exploratory event relay with no PSI/DLMn
latent state, gain, or structural-count scaling. It includes the four
DNp01→PSI and ten PSI→DLMn routes; the two supplemental reciprocal PSI edges
remain structural-only to avoid undefined event recurrence. Phase 6C's
parallel DNp01→TTMn branch is unchanged. Pair-specific sign, delay and
efficacy remain unresolved despite class/pathway-level positive evidence.
Decision: `READY_FOR_SYNTHETIC_PSI_DLMN_EVENT_RELAY`; no dynamics were
implemented and canonical sensory-derived zero events remain zero. See
[the Phase 8F event-model readiness assessment](science/psi_dlmn_event_model_readiness.md).

## 37. Phase 8G — synthetic PSI/DLMn routed-event ledger

Phase 8G implements an offline, content-addressed two-layer relay using the
pinned motor contract's four DNp01→PSI and ten PSI→DLMn chemical edges. Six
Phase 8B synthetic fixtures preserve source identity, provenance and exact
integer event boundaries. The relay produces path records only; reciprocal
PSI edges remain excluded, structural counts remain metadata, and Phase 6C
TTMn is unchanged. Artifact ID:
`1da8963e9097c570d67a2683f71744c2dee8c59662faa253cdc56ad32ee5e5b3`.
Offline full replay passed. No sensory-derived event, PSI/DLMn latent state,
muscle or behavior was added. See
[the Phase 8G routed-event ledger assessment](science/synthetic_psi_dlmn_event_relay.md).

## 38. Phase 8H — production Phase 7O event to PSI/DLMn adapter

Phase 8H adds a condition-explicit production adapter from genuine persisted
Phase 7O `SIMULATED_DNP01_MODEL_SPIKE` records into the shared Phase 8G
two-layer route core. It reuses the pinned motor contract and exact active
DNp01→PSI→DLMn policy; reciprocal PSI edges remain excluded, and Phase 6C/8C
TTMn remains a separate parallel branch. The canonical Phase 7O
`reference_bilateral` condition and all 35 conditions contain no DNp01 events,
so the valid Phase 8H result has no PSI or DLMn route records. No event is
inferred from Vm, drive or filtered state, and no synthetic fallback is
allowed. Artifact ID:
`b13813300a8be7ffa644393d01e78f032705fd4e155665bc60f50f7abee45803`.
Full offline replay passed; the Phase 8G synthetic artifact identity remains
unchanged. This validates provenance-preserving zero-event composition and
test-local future nonzero compatibility, not sensory-driven motor activity,
PSI/DLMn physiology, muscle output, or behavior. See
[the Phase 8H production event adapter assessment](science/sensory_psi_dlmn_event_adapter.md).

## 39. Phase 8I — synthetic parallel motor-branch composition

Phase 8I composes the same immutable six-fixture synthetic DNp01 event
battery through the unchanged Phase 6C TTMn integrator and Phase 8G PSI/DLMn
relay. The artifact preserves common origin identities and separate output
semantics: dimensionless TTMn exploratory state versus discrete
`EXPLORATORY_ROUTED_MOTOR_EVENT` records. Per origin, software accounting is
one TTMn input, two PSI receipts, and ten DLMn path records; these are not
biological strength ratios. PSI↔PSI remains excluded, structural counts remain
metadata, and no new parameter, production sensory input, muscle, or behavior
is introduced. Artifact ID:
`f4225f3f24bcf3a3ed27d5c0d313700426e788d6af232b2c57b9d77e3ae63bbf`.
Deterministic replay and exact Phase 8B/8G child-result equality passed. See
the [Phase 8I composition assessment](science/synthetic_parallel_motor_branch_composition.md).

## 40. Phase 8J — motor-neuron output / neural→muscle readiness

Phase 8J replayed the pinned motor contract and Phase 8I composition, then
assessed the neural→muscle boundary without adding dynamics. Phase 6C TTMn
output is a dimensionless exploratory neural state, not a spike or muscle
activation; Phase 8G DLMn receipts are graph-path records, not DLMn output
events. Primary evidence supports TTM and DLM target *classes/groups*, but
not exact MaleCNS body-to-fiber mapping or pair-specific delay/gain/force.
Decision: `PIN_MOTOR_NEURON_MUSCLE_TARGET_CONTRACT` next; DLMn latent state is
not required for that no-dynamics contract. See the
[Phase 8J boundary assessment](science/motor_neuron_muscle_boundary_readiness.md).

## 41. Phase 8K — motor-neuron muscle-target contract

Phase 8K pins a deterministic no-dynamics association contract for the 2
source-verified TTMn and 10 DLMn bodies. It links MaleCNS neural identity to
literature-supported TTM or DLM muscle class/group evidence, while preserving
explicit confidence, unresolved exact fibers, and uncertain DLM target sides.
Only the TTM mapping uses a qualified literature-supported ipsilateral side
inference. The contract creates no MaleCNS peripheral edge and defines no
output conversion or muscle dynamics. Artifact ID:
`5f02960bb5bdd81bcd622334a93199bc6973749f233dbc7aa5fd15481a5eddf0`.
Offline replay passed. See the
[Phase 8K target contract assessment](science/motor_neuron_muscle_target_contract.md).

## 42. Phase 8L — synthetic motor-neuron output target dispatch

Phase 8L validates explicit `SYNTHETIC_MOTOR_NEURON_OUTPUT_TEST` events
against the replayed Phase 8K target contract. Each event creates one
`EXPLORATORY_MUSCLE_TARGET_DISPATCH` receipt that preserves target class/group,
confidence, qualified TTM laterality, and unresolved DLM sides/fibers. The
eight-fixture artifact covers zero, both TTMn sides, DLMn a,b sides, one c-f
identity per side, and all 12 target associations; full offline replay is
deterministic. Phase 6C states and Phase 8G path receipts are not converted
into output events. No muscle dynamics, NMJ parameters, force, or behavior
are introduced. See the
[Phase 8L dispatch assessment](science/synthetic_motor_neuron_target_dispatch.md).

## 43. Phase 8M — motor-neuron output-source readiness

Phase 8M audited the current TTMn state and DLMn route-receipt semantics
without changing models. A dimensionless TTMn threshold-crossing output rule
is possible only as an explicit, uncalibrated model assumption; a DLMn path
receipt cannot be treated as an output event and requires a neural
input/state model first. A shared future output-event envelope can preserve
identity and provenance without forcing shared dynamics. The next bounded
step is a TTMn-only exploratory threshold-rule definition/test, using only
synthetic fixtures and no muscle interface. Canonical Phase 7O remains silent.
See the [Phase 8M readiness assessment](science/motor_neuron_output_source_readiness.md).

## 44. Phase 8N — TTMn exploratory threshold-crossing output rule

Phase 8N adds a TTMn-only output operator over the exact replayed Phase 8B /
Phase 6C dimensionless trajectories. At the explicit uncalibrated
`MODEL_ASSUMPTION` threshold 0.25, the strict upward crossing rule is
`x_prev < threshold <= x_current`; equality at the new boundary counts and
re-arming occurs only after state is below threshold. The six-fixture reference
battery yields 8 `EXPLORATORY_MODEL_DERIVED_MOTOR_NEURON_OUTPUT` records; the
0.20 / 0.25 / 0.30 / 0.50 sensitivity probes yield 6 / 8 / 2 / 0 without
changing Phase 6C trajectories. Upstream provenance remains
`SYNTHETIC_MOTOR_INTERFACE_TEST`; no biological spike claim, Phase 8L dispatch,
DLMn generator, muscle dynamics, or production adapter was added. Artifact
`1c8aeac685646dac16fbb66f163743b662a3cd9a0e8f9f7582210fd7b39b9ab3` replays
offline. See the [Phase 8N output-rule assessment](science/synthetic_ttmn_output_rule.md).

## 45. Phase 8O — model-derived TTMn target dispatch

Phase 8O consumes the canonical, fully replayed Phase 8N TTMn output events
and resolves each through the unchanged Phase 8K target contract. It reuses
the Phase 8L identity-only target resolver while retaining a distinct
model-derived dispatch schema; Phase 8L remains synthetic-output-test-only.
The six Phase 8N fixtures contain 8 model-derived events and produce exactly
8 target-association receipts (4 per TTMn body), with step/time and the full
Phase 8B fixture → Phase 6C TTMn trajectory → Phase 8N event ancestry
preserved. No threshold is reapplied, no DLMn output is accepted, and no
muscle/NMJ dynamics or production sensory path is added. Artifact
`3bc011f9a8831f5291b6078d6132ef0dc6d6d7e87cc45ecfaa957ec80b8af360`
replays offline. This establishes only event-to-target association, not
neuromuscular transmission or muscle activation. See the
[Phase 8O target-dispatch assessment](science/model_derived_ttmn_target_dispatch.md).

## 46. Phase 8P — TTMn→TTM neuromuscular readiness

Phase 8P is documentation-only. Primary adult *Drosophila* TTM NMJ studies
measure muscle electrical responses and activity-dependent depression; direct
TTMn stimulation constrains a motor-axon+NMJ+muscle-potential **subpath**, not an
isolated NMJ delay. None calibrates the uncalibrated Phase 8N model event to
exact-body release, whole-TTM activation or force. The next bounded boundary
is an exploratory **NMJ-input receipt only**, distinct from Phase 8O target
association and with no muscle state or transmission-success claim. See the
[Phase 8P assessment](science/ttmn_ttm_neuromuscular_readiness.md).

## 47. Phase 8Q — TTMn neuromuscular-input receipt

Phase 8Q consumes the fully replayed Phase 8O model-derived TTMn target
dispatches and emits one provenance-linked `ttm_neuromuscular_input_receipt_v1`
per dispatch (8 receipts across the six independent reference fixtures, 4 per
TTMn body). This records only an exploratory software handoff to the pinned
TTM target association: no successful release, biological NMJ timing, muscle
response, depression, or muscle state is modelled. Phase 8L remains a separate
synthetic-output test, and production Phase 7O data are not included. Artifact
`e04803f60304f58d0e6d27fdea5d15debb60358b46721caac09f10165c6df9c4` replays
offline. See the [Phase 8Q receipt assessment](science/ttm_neuromuscular_input_receipt.md).

## 48. Phase 8R — TTM G1 observation-contract readiness

Phase 8R is documentation-only. Directly verified publisher-indexed Koenig &
Ikeda 2007 Methods/Results and the open Kadas et al. 2019 article support a
bounded, protocol-specific **observation** contract for G1 electrical/context
values and a separately labelled composite TTMn-region stimulation→TTM
potential-onset latency. The Koenig & Ikeda 2005 abstract supports only a
qualitative depression comparison here; its quantitative curve is excluded.
None of these observations is a NeuroFly parameter, whole-TTM voltage,
exact-MaleCNS-body physiology, isolated NMJ delay, or evidence of Phase 8Q
release/response. The next bounded Phase 8S is to pin and replay the
observation-only contract before any observation model or electrical muscle
dynamics. See the [Phase 8R assessment](science/ttm_g1_electrophysiology_observation_readiness.md).

## 49. Phase 8S — TTM G1 electrophysiology observation contract

Phase 8S pins nine protocol-specific adult *Drosophila* TTM/G1 literature
observations in an offline, content-addressed contract. Descriptive, reused,
analysis-input, categorical, summary, and derived quantities retain distinct
classifications and source/protocol provenance; unknown uncertainty and
protocol fields remain explicit. G1 is not whole TTM or exact MaleCNS-body
physiology, and observations are not NeuroFly parameters. Quantitative Koenig
& Ikeda 2005 depression data, figure digitization, model calibration, and
muscle dynamics remain excluded. Contract
`5993f2915c2281b13bee35919cadeb261e42cbf60c10f514171a059ce318ff1f` replays
offline. See the
[Phase 8S observation contract](science/ttm_g1_electrophysiology_observation_contract.md).

## 50. Phase 8T — G1 observation-model feasibility

Phase 8T assessed all nine Phase 8S records against the Phase 8Q software
handoff and candidate future G1 electrical outputs. No Phase 8S record is yet
a formal protocol-matched numeric validation target: the approximately −95 mV
resting value is descriptive context, the reused 45 mV evoked value lacks
verified 2005 protocol/operator detail, miniature/quantal and recycling
observations require additional release/history models, and the Kadas latency
starts before the Phase 8Q boundary. Candidate electrical model families are
underdetermined by the pinned scalar evidence. The next bounded Phase 8U is a
metadata-only observation-mapping contract with explicit protocol and model
boundary gates; no muscle dynamics or comparison runner is authorized by this
assessment. See the [Phase 8T assessment](science/ttm_g1_observation_model_feasibility.md).

## 51. Phase 8U — TTM G1 observation-mapping contract

Phase 8U pins nine metadata-only mappings referencing the exact Phase 8S
observation IDs in source order. Candidate operators, protocol requirements,
comparison roles, and structured blockers remain explicit; all operators are
non-executable, all current-model comparability claims are false, and zero
mappings are formal-comparison-ready. The Phase 8T readiness snapshot,
unresolved electrical-input semantics, context-only prior analysis input, and
Kadas system-boundary mismatch are preserved. Contract
`f30f8ea3eaabb247b1c2999bf9b661c5eef1bf1b96ebfbd3d7f3826a0318b34f`
replays offline through the unchanged Phase 8S source. See the
[Phase 8U contract](science/ttm_g1_observation_mapping_contract.md).

## 52. Phase 8V — TTM neuromuscular-input semantics

Phase 8V recommends a model-family-neutral abstract TTM-class electrical-input
event downstream of Phase 8Q, not release, current, conductance or voltage.
One receipt may be admitted as one token under an explicit zero-added-model-
delay assumption, with no amplitude or biological-success claim. Model-specific
input transformations remain separate; using TTM-class input in a G1 model
requires an explicit proxy mapping contract. Phase 8U blockers and zero-ready
comparability remain unchanged. Exactly one bounded Phase 8W is recommended:
pin/replay the abstract class-level input contract, without a G1 mapping,
electrical dynamics or comparisons. See the
[Phase 8V assessment](science/ttm_neuromuscular_input_semantics.md).

## 53. Phase 8W — abstract TTM electrical-input admission

Phase 8W pins eight model-family-neutral abstract input tokens from the eight
canonical Phase 8Q receipts. Parent identity, timing and qualified TTM-class
target semantics are retained; same-boundary scheduling is explicitly a
zero-added-model-delay assumption. No physical magnitude, release success,
electrical state or G1 destination is represented. Contract
`1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa`
replays offline through unchanged Phase 8Q ancestry. Phase 8U remains
zero-ready; physical transformation and G1 proxy mapping require separate
work. See the [Phase 8W contract](science/ttm_abstract_electrical_input_contract.md).

## 54. Phase 8X — TTM-class to G1 observation-domain proxy readiness

Phase 8X recommends an explicitly exploratory G1 observation-domain proxy,
not an anatomically resolved MaleCNS destination or whole-TTM state. Primary
pathway and fiber-group evidence supports a bounded reduced-domain choice,
not identical physiology across fibers or independently measured bilateral
equivalence. The next metadata contract should define one side-unresolved
proxy domain type while preserving both distinct causal TTMn associations;
Phase 8W stays TTM-class only. Phase 8S observations remain evidence, and all
Phase 8U mappings remain zero-ready. Exactly one bounded Phase 8Y is proposed:
pin/replay that metadata-only proxy mapping without electrical dynamics,
physical input transformation or comparisons. See the
[Phase 8X assessment](science/ttm_g1_proxy_mapping_readiness.md).

## 55. Phase 8Y — pinned exploratory G1 proxy domain metadata

Phase 8Y pins one side-unresolved virtual G1 observation-domain type and two
distinct TTMn source-association links, preserving 800146/R and 804642/L.
The mapping is a modelling assumption, not tracing, a shared physical fiber,
bilateral physiological equivalence or whole-TTM representation. Phase 8W
remains class-only; Phase 8S remains empirical authority and Phase 8U stays
zero-ready. Contract
`030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8`
replays offline through all four unchanged sources. No runtime events,
electrical inputs/dynamics or comparisons are added. Exactly one bounded
Phase 8Z is proposed: assess model-specific input-transformation feasibility
without implementation. See the
[Phase 8Y contract](science/ttm_g1_proxy_mapping_contract.md).

## 56. Phase 9A — first exploratory G1 electrical model selection

Phase 9A selects passive voltage-valued relaxation with an effective
voltage-equivalent event jump driven by validated Phase 8W tokens under the
pinned Phase 8Y G1 proxy assumption. Baseline, effective tau and event scale
must be explicit uncalibrated model assumptions, not copied or fitted from
Phase 8S. Separate fixture/body trajectories may share config only as an
assumption; zero-added-model-delay timing is retained. Phase 8U remains
zero-ready, and no current, conductance, release, whole-TTM or physiological
validation claim is introduced. Exactly one Phase 9B is defined: implement
and replay that deterministic model on the existing six fixtures. Phase 9A
adds no model code, schemas, artifacts, operators or comparisons. See the
[Phase 9A assessment](science/ttm_g1_first_electrical_model_readiness.md).
