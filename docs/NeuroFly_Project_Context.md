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

## 57. Phase 9B — first exploratory G1-proxy electrical response

`passive_g1_proxy_electrical_model_v1` now computes independent fixture/body
trajectories from validated Phase 8W tokens in the Phase 8Y virtual G1 domain.
The explicit uncalibrated reference assumptions are 0 mV-equivalent reference,
1 ms effective tau and 2 mV-equivalent increment/token; grid remains 0.1 ms,
80 intervals. Zero input stays baseline, singles decay, repeated inputs sum
linearly and bilateral states remain distinct. These are model behavior gates,
not physiological validation. No release/current/conductance model, fitting,
comparison or upstream contract change exists; Phase 8U remains zero-ready.
Artifact `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f`
has config hash
`d3807d88f777e8f6754a8e3aab591e42b643974e7417451509771581d7c013d0`
and result hash
`fa11b093b1a3013d397bb459c3c1f39b1a96543b8380a792e89dc0bdfa8e91d8`.
Next: one bounded Phase 9C assumption sensitivity/identifiability experiment,
without fitting. See the
[Phase 9B model](science/g1_proxy_passive_electrical_response.md).

## 58. Phase 9C — G1-proxy model sensitivity and internal separability

The unchanged Phase 9B model now has a deterministic nine-cell sensitivity
experiment: tau 0.5/1/2 ms × event scale 1/2/4 mV-equivalent, with unchanged
reference coordinate, grid, six fixtures and causal/proxy identities. Scale
linearity and normalized invariance pass; tau controls retention and repeated
residual accumulation. Full model trajectories structurally separate scale
and tau, while reduced late-sample summaries confound them. Neither parameter
is currently biologically identifiable; Phase 8U remains zero-ready. The
reference cell exactly reproduces Phase 9B, with no best-cell selection or fit.
Artifact `dfe98ec90078124f4a66df825b552d05ed317fcb89d33e0f374b99c6bfd4bfa4`
has config hash
`58ec7a9fa8125b48ed62a4ca66f794e4a47c83a0d789e6fbd078a05555b80073`
and result hash
`bd24acf765556e8f0e2b2189ba5d6a0cf14824253c44ba951c07bd0d24d804f3`.
Decision: `G1_ELECTRICAL_SENSITIVITY_VALIDATED`; retain the exploratory baseline
and proceed to one read-only Phase 9D observation-compatibility assessment.
See [Phase 9C](science/g1_proxy_electrical_sensitivity.md).

## 59. Phase 9D — post-model observation compatibility

Phase 9D reassesses all nine pinned observations without comparison or fitting.
Baseline, evoked and repeated response scaffolds now exist in model-space
`mV_eq`, but no biological mV mapping, executable source-matched observation
operator or experimental protocol match exists. Miniature/quantal/spontaneous/
vesicle quantities remain absent; Kadas retains the full-path boundary mismatch.
Phase 8U remains an unchanged zero-ready historical snapshot. No parameter is
currently empirically identified. The next executable slice is one Phase 9E
model-space peak-deflection extractor with an explicit baseline/window helper,
not biological calibration. A separate empirical benchmark mode is recommended
for later protocol-aligned work, not implemented now. No model code, source
contract, artifact, unit conversion or observation comparison changes. See
[Phase 9D](science/g1_proxy_observation_compatibility.md).

## 60. Phase 9E — model-space peak-deflection extraction

One executable extractor observes persisted/replayed canonical Phase 9B output:
immediate pre-event boundary baseline, followed by maximum positive deflection
over event boundary through trajectory end, earliest peak on ties. Four isolated
peaks are 2 mV_eq at step 10 / 1 ms; four separate controls have stable baseline
0 mV_eq and zero maximum absolute deviation. Entire repeated-event fixtures are
excluded. No dynamics, biological voltage conversion, fitting or empirical
comparison is added. Phase 8U remains unchanged and zero-ready.
Operator `7a9cbf8f4341382757a118f3485780a1f49c6f810a5151f35112eb60286b1e19`;
artifact `2c775d6e00d74b3b3a3ca5a36bb84fd4032959d29f3c7d4c8b0bca934e2942b8`;
config hash `44be1b554dafc1c867f92ff1c50100157aa0787ea04cf2480e390cc7f0a778ca`;
result hash `766b98a29bd6343f3ba633cfa5a9de900f697ff93be8ac89da3f083e1325dba9`.
Empirical validation remains not ready. Proposed Phase 9F is one bounded
read-only isolated-G1 benchmark protocol/amplitude source-readiness assessment,
not a runner or calibration. See
[Phase 9E](science/g1_proxy_model_space_peak_deflection.md).
Decision: `FIRST_MODEL_SPACE_PEAK_DEFLECTION_OPERATOR_VALIDATED` (software and
extraction semantics only, not biological validation). Offline replay and
repository quality gates pass.

## 61. Phase 9F — isolated G1 benchmark protocol readiness

Required Phase 9E/9B/8S/8U sources replay unchanged; Phase 8U remains zero-ready.
The primary 2005 abstract and publisher-indexed 2007 Methods/Results were audited,
without claiming complete publisher access. The reused evoked record remains
`PRIOR_PRIMARY_RESULT_REUSED`; original preparation/stimulus and amplitude
baseline/window fields are not verified. A source-matched runner is therefore
not ready. Phase 9E is a valid model-space extractor but has no unchanged
admission path for a new empirical benchmark trajectory; no synthetic ancestry
may be fabricated. Biological unit mapping and all parameters remain unidentified.
Decision: `PRIMARY_SOURCE_PROTOCOL_RECOVERY_REQUIRED`; next phase:
`RECOVER_PRIMARY_2005_PROTOCOL_DETAILS`. One bounded Phase 9G should obtain and
audit lawful original Methods/amplitude sections, with a user-supplied copy if
needed, before a runner go/no-go decision. No code, contracts, artifacts,
parameters, unit mapping or comparison changed. See
[Phase 9F](science/g1_isolated_evoked_benchmark_readiness.md).
Assessment status: `PASS`; benchmark implementation remains not ready. All
repository quality gates pass.

## 62. Phase 9G — original 2005 protocol recovery gate

The clean committed Phase 9F baseline and Phase 9E/9B/8S/8U replays pass;
Phase 8U remains unchanged and zero-ready. Lawful publisher, bibliographic and
repository recovery found the authentic 2005 abstract but no full text or
project-supplied copy. Access is `ABSTRACT_ONLY`; the original 45 mV location,
amplitude/baseline/window operation and material stimulus/preparation/recording
fields remain unverified. Reused 2007 evidence is not original protocol recovery.
Phase 8S remains incomplete but valid; physical mV mapping and tau remain
unconstrained. Runner decision: `NO_GO_REQUIRE_USER_SUPPLIED_2005_FULL_TEXT`.
This completed negative gate stops benchmark implementation pending a lawful
2005 copy: Methods, G1 response Results, associated captions and amplitude
definitions. Resume Phase 9G only when supplied; do not create another recovery
phase. No implementation, fitting, digitization, parameter or contract changes.
See [Phase 9G](science/g1_2005_evoked_protocol_recovery.md).
Assessment status: `PASS` with definitive benchmark NO-GO. Full suite: 789 passed,
1 deselected; Python, frontend regression and diff gates pass. No commit/push.

## 63. Phase 10A — first electrical-to-activation model selection

Required Phase 9B/9C/9E and Phase 8Y/8W artifacts replay unchanged from a clean
committed Phase 9G baseline. No existing activation or muscle/body mechanics
implementation was found; frontend intensity is presentation-only. Select
`STATIC_NORMALIZED_ACTIVATION_PROXY`: full persisted electrical deviation
trajectory → `min(1, max(0, u) / activation_scale_mV_eq)` per causal instance.
One explicit uncalibrated scale, fixed model normalization ceiling, no additional
activation tau/threshold/lag. Scale value is deferred to an independently
declared Phase 10B reference config, never derived from empirical or peak data.
Both causal bodies remain independent under shared exploratory assumptions;
output is dimensionless [0,1], not calcium, contraction or force. Phase 9's
external 2005-source validation blocker remains but does not block this slice.
Next: one executable Phase 10B model/runner/artifact/replay, all six electrical
fixtures; later Phase 10C tests scale sensitivity and mechanics-facing suitability.
No implementation or new metadata contract in 10A. See
[Phase 10A](science/ttm_g1_first_muscle_activation_model_readiness.md).
Assessment status: `PASS`; ready for the first executable activation proxy.
Full tests: 789 passed, 1 deselected; all Python/frontend regression and diff
gates pass. Documentation only; no commit/push.

## 64. Phase 10B — executable static activation proxy

`static_normalized_muscle_activation_model_v1` consumes persisted/replayed
Phase 9B deviations, not tokens or peak observations:
`activation_proxy = min(1, max(0, u) / 10.0)`. Scale 10 mV_eq, rectification,
ceiling and shared config are explicit uncalibrated `MODEL_ASSUMPTION`s.
No activation tau/threshold/delay; source grid and both causal identities are
preserved. Six fixtures yield 12 trajectories × 81 boundaries: zero controls
remain zero, singles/bilateral peak at 0.2 per active instance, repeated peaks
at 0.22706705664732252; no canonical ceiling occupancy. No contraction, force,
calcium, whole-TTM aggregation, physical calibration or empirical comparison.
Artifact `4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb`;
config hash `be33c72048caeae4227a504aa251d10acec454ef283a73adf77104d0a4c424c9`;
result hash `288b67f791f66765a17d6bdd6cadd30b9c98f4480dd23434bd4c6e9ae5667fce`.
Generated data remains ignored. Phase 8U stays zero-ready; historical sources
remain unchanged. Next: one Phase 10C scale sweep at 5/10/20 mV_eq with fixed
electrical trajectories plus mechanics-interface suitability assessment.
See [Phase 10B](science/ttm_g1_static_muscle_activation.md).
Decision: `FIRST_EXPLORATORY_MUSCLE_ACTIVATION_MODEL_VALIDATED`; status `PASS`
for exploratory model/software behavior only. Focused tests: 41 passed; full
suite: 830 passed, 1 deselected. Replay, Python, frontend regression and diff
gates pass. No frontend/API changes or commit/push.

## 65. Phase 10C — activation sensitivity and downstream interface

Fixed persisted Phase 9B samples drive the unchanged Phase 10B transform at
scales 5/10/20 mV_eq: three cells, 18 fixture runs, 36 independent trajectories.
Inverse scale, normalized reconstruction, zero control, temporal shape and
bilateral/source independence are verified. All canonical samples remain
unclipped; clipping and rectification still intentionally lose information
outside that regime. Scale 10 remains reference-by-history, never calibrated.
Artifact `b605e51e4ed42813d2562d61aa58129ed3d5b43e875ab1fd0de98ca0360c9a6e`;
config hash `7b3826904b71182fe1dab3cbca9d2897e1c02ff23c2c2a2c448139599721d88e`;
result hash `7f6e580b770741967f0dda3e87dcb3c9b1288575ccb2b872035751ed562d36dc`.
Full activation trajectories are ready as exploratory downstream model inputs,
not physical actuator commands. Activation scale is confounded with upstream
magnitude and a hypothetical future force gain. Physical force scale, actuator/
attachment geometry and contraction kinetics remain undefined; no mechanics
are implemented. Phase 10 activation layer is complete as a model/software
milestone. Next: exactly one Phase 11A first contraction/force-model decision,
favoring assessment of a dimensionless proxy before uncalibrated physical force.
See [Phase 10C](science/muscle_activation_scale_sensitivity_and_mechanics_interface.md).
Decision: `ACTIVATION_SCALE_SENSITIVITY_VALIDATED`; status `PASS`.
Completion: `PHASE10_ACTIVATION_LAYER_COMPLETE` (exploratory only). Focused tests
27 passed; full suite 857 passed, 1 deselected. Replay, Python, frontend
regression and diff gates pass; generated data ignored; no commit/push.

## 66. Phase 11A — select the first mechanics-facing actuator boundary

Clean committed Phase 10C baseline `083c955` matches local `origin/main`.
Phase 10B/10C/9B and motor-target ancestry replay unchanged. No body physics,
actuator runtime or articulated biomechanical rig exists: the presentation GLB
has static leg meshes, zero skins/animations and no physical scale/attachments.
Primary evidence supports TTM-associated femur extension, not complete jump
prediction; skinned-bundle and tethered-fly force measurements do not calibrate
the current G1 proxy. Physical force and actuator geometry remain not ready.

Select `DEFINE_EXPLORATORY_TTM_ACTUATOR_MAPPING`: one executable Phase 11B
adapter consuming full persisted 10B activation trajectories and routing them
to distinct right/left virtual mesothoracic femur-extension command channels.
Magnitude remains dimensionless and unchanged; same-boundary, no gain, new
temporal state, force, shortening, geometry, aggregation or movement. Added
value is explicit functional actuator addressing/consumer semantics, not a
renamed contraction/force scalar. Redundant proxy layers are rejected; existing
electrical/activation/future-gain confounding remains explicit.
Decision: `READY_FOR_FIRST_EXECUTABLE_ACTUATOR_LAYER`;
`PHASE11B_OUTPUT_CAN_FEED_FUTURE_WORLD_MECHANICS`. Phase 12 must separately
decide actuator-to-plant mapping/contact/state; rendering observes simulation
state, never scripts escape or controls the fly through an LLM.
See [Phase 11A](science/first_ttm_contraction_force_actuator_readiness.md).
Status `PASS`, documentation only. Full suite: 857 passed, 1 deselected,
two existing deprecation warnings; Ruff check/format, diff check and frontend
test (38)/lint/typecheck/build pass. No implementation, new artifact or
commit/push; Phase 9 external validation blocker remains unchanged.

## 67. Phase 11B — executable functional TTM actuator commands

`ttm_exploratory_actuator_command_v1` consumes replay-validated persisted Phase
10B activation arrays. Exact same-boundary passthrough, no numerical gain,
threshold, delay or dynamics: `actuator_command = activation_proxy`.
Two fixed `MODEL_ASSUMPTION` routing records preserve 800146/R →
RIGHT_TTM_ACTUATOR and 804642/L → LEFT_TTM_ACTUATOR, with action kind
`TTM_ASSOCIATED_FEMUR_EXTENSION_DRIVE`. These are virtual functional channels,
not anatomical attachments, physical joints or force vectors.
Routing IDs: `6cf14bc3b7dfefa77cdca953459499c6c78d0a1a0329dfd46a2178f027022ce5`
(right), `a77193428fc74b9de95306b195a6615f751a38f4f6cfee143133af086356c58f`
(left). All six fixtures preserve 12 independent trajectories and 972 samples;
zero/inactive channels remain zero, singles/bilateral peak at 0.2 per active
channel, repeated peaks at 0.22706705664732252. No whole-body command/aggregation.
Artifact `478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40`;
config hash `94da685537241558bf1cc64ae9a8c051fce5a651f02bab871f192d518406b974`;
result hash `78f277a4714f983d35212cd4314ec3a257664356426e1caf7cc3ce9214bf8c9f`.
Generated artifact remains ignored; canonical offline replay and tamper
rejection protect source/routing/value/time identities. No empirical
calibration, force, contraction, geometry, body movement or frontend changes.
Interactive scenarios still do not exist. Next: exactly one Phase 12A
body/world plant and closed-loop mechanics architecture decision, covering
kinematic vs dynamic modeling, coordinates, actuator-to-state mapping,
contact and backend simulation ownership versus rendering/interpolation.
See [Phase 11B](science/ttm_exploratory_actuator_commands.md).
Decision: `FIRST_EXPLORATORY_TTM_ACTUATOR_LAYER_VALIDATED`; status `PASS`
for exploratory functional routing only. Focused tests 42 passed; combined
historical regression 117 passed. Full invocation 895 passed, 1 deselected,
two existing warnings; four subsequently added cases also passed in focused
runs. Ruff, format, diff and frontend test/lint/typecheck/build gates pass.
Only Phase 11B changes remain; generated data ignored; no commit/push.

## 68. Phase 12A — select the first body/world plant

Clean committed 11B baseline `68e3de4` equals local `origin/main`; 11B/10B/9B
and genuine 7O/8C artifacts replay unchanged. Audit confirms no body/world plant,
physics/contact solver or live scenario transport. GLB legs remain static,
without skin/animation/validated joints; frontend owns presentation, not motion.

Select `EXPLORATORY_KINEMATIC_BODY_PLANT`, `PLANAR_2D`: full 11B right/left
commands → arithmetic common-mode mean → assumed +Z world_eq speed → integrated
position. One positive model-space speed gain (proposed unit reference 1.0
world_eq/ms), reset position [0,0], fixed heading, source 0.1 ms tick and
left-boundary interval hold. No steering, inertia, gravity, contact, physical
force/geometry or frontend implementation. Backend state is authoritative;
future rendering interpolation never drives sensor feedback.

Full 7O replay verifies zero DNp01 events in all 35 conditions; 8C has zero
inputs and exactly zero TTMn states. Crucially, later fixture-pinned electrical/
activation/actuator artifacts descend from synthetic 8B ancestry, not 8C:
`PRODUCTION_PATH_NOT_CONNECTED_TO_ACTUATOR`. No persisted genuine downstream
activation/actuator result is asserted. Synthetic fixtures can validate 12B
mechanics but cannot demonstrate connectome-driven movement. No neural retuning.

Decision: `READY_FOR_FIRST_EXECUTABLE_BODY_PLANT`; physical mechanics not ready;
`ADDITIONAL_MAJOR_BLOCKERS_REMAIN` for a scenario. World/body/object→relative-
column sensory mapping, causal runtime/production composition, nonzero neural
output and frontend integration remain separate gaps. Exactly one next 12B
implements six body trajectories from the six actuator fixture pairs, with
deterministic reset/artifact/replay. Phase 13 then addresses world/scenario
runtime and explicit sensory feedback; no additional mechanics metadata phase.
See [Phase 12A](science/first_body_world_plant_readiness.md).
Status `PASS`, documentation only; no plant/schema/artifact implemented.
Full tests: 899 passed, 1 deselected, two existing dependency warnings.
Ruff check/format, diff check and frontend test (38)/lint/typecheck/build pass.
Only intended documentation changes remain; no commit/push.

## Phase 12B — executable synthetic planar body plant

`exploratory_planar_body_plant_v1` consumes persisted Phase 11B commands only.
Common mode is (R+L)/2; gain 1.0 world_eq/ms and initial x/z 0 are explicit
MODEL_ASSUMPTIONs. Fixed +Z heading, no steering/contact/inertia/physical units.
Boundary n drives interval n→n+1: 80 intervals, 81 stored boundaries, no final
extra interval. Six body trajectories contain 486 samples; x remains zero.
Final z: zero 0; either single 0.10498749586386545; bilateral
0.2099749917277309; either repeated 0.209362769474689 world_eq.

Artifact `bb3696faae558778555601991de3fd36081d5853c889fcb7aac5ffd79593eba3`;
config hash `88df5840456eaa2a9df92cd60cbe1555e3365cd4e8f87434d06bed6013272cd0`;
result hash `4b8b462ebe703c92e68f24d10f8f49784d0087dd27f919b0ce5650320874728e`.
Generated data remains ignored, offline replayable and uncalibrated.
This is synthetic mechanics validation, not autonomous connectome-driven
movement. Genuine 7O/8C replays remain zero; no production actuator composition
was added. World→sensory geometry, causal runtime/composition, nonzero neural
output and later frontend integration remain Phase 13 blockers.
Next exactly Phase 13A decides first world/scenario closed-loop architecture;
no Phase 12C. See [Phase 12B](science/exploratory_planar_body_plant.md).
Decision `FIRST_EXPLORATORY_BODY_PLANT_VALIDATED`; Phase 12B `PASS`.
Focused tests: 37 passed. Full tests: 936 passed, 1 deselected, two existing
dependency warnings. Ruff check/format and diff check pass; frontend regression
tests (38), lint, typecheck and build pass. No commit/push.

## Phase 13A — first closed-loop scenario architecture

Select `LOOMING_CIRCUIT_VALIDATION` as an initial circuit-validation scenario,
not a replacement for Baseline / Light-Dark / Obstacle / Resource / Adversity /
Changing World taxonomy. Same runner includes an object-disabled Baseline.
Backend causal ticks preserve all 311 sensory identities and fixed model
parameters. A declared R/(23,9) relative-column centre receives exploratory
distance-derived expansion; no absolute retinal registration is asserted.
Proposed unit model object radius 1 at (0,4), prescribed z velocity -1 world_eq/ms,
projection radius floor(10*atan2(radius,distance)), fixed 1.4 ms / 0.1 ms grid.
All world/projection quantities are explicit uncalibrated model assumptions.

13B must compose genuine DNp01→TTMn→output→target→receipt→abstract token→G1→
activation→actuator→plant with actual event ancestry and body feedback.
Historical artifact wrappers remain synthetic/pinned; bounded shared-kernel
extraction and scenario provenance adapters are required, not fabricated IDs.
Sensory s[n] drives neural interval n→n+1; resulting spikes belong to n+1,
whose actuator commands drive the subsequent body interval. No final extra tick.
Required historical source replays pass; all 35 genuine 7O conditions and 8C
remain zero. Zero movement is expected and valid; capability of feedback is
tested separately from actual canonical movement-driven sensory change.

Decisions: `PRODUCTION_CHAIN_ADAPTER_REQUIRED_BUT_BOUNDED`,
`SINGLE_BACKEND_CAUSAL_TICK_RUNNER`,
`READY_FOR_FIRST_EXECUTABLE_CLOSED_LOOP_SCENARIO`.
Next exactly executable Phase 13B: deterministic world/projection, complete
causal composition, body feedback, integrated artifact/replay and tests; no
frontend/API, retuning, scripted fallback or metadata-only intermediate phases.
Phase 14 renders authoritative snapshots and adds scenario selection/transport.
See [Phase 13A](science/first_closed_loop_scenario_readiness.md).
Phase 13A `PASS`, documentation only. Full tests: 936 passed, 1 deselected,
two existing dependency warnings; Ruff check/format and diff check pass.
Frontend regression tests (38), lint, typecheck and build pass. No commit/push.

## Phase 13B — executable genuine closed-loop scenario runtime

`closed_loop_scenario_config_v1` / `closed_loop_scenario_result_v1` execute
Baseline Control and Looming Circuit Validation through one backend causal
runner. Preserves all 311 identities and fixed neural/motor parameters.
Looming: (0,4), radius 1, velocity (0,-1) world_eq/ms; R / hex(23,9),
floor(10*atan2(radius,current body-relative distance)), all MODEL_ASSUMPTIONs.
0.1 ms dt, 14 intervals / 15 boundaries; body reset (0,0), heading +Z.
Baseline has an explicitly empty stimulus, not radius zero. Strategic world
taxonomy is unchanged; Looming remains an initial circuit-validation scenario.

Shared kernels preserve historical batch replay. Scenario-owned parent-event
envelopes compose genuine DNp01→TTMn→crossing→target→receipt→abstract token→
G1→activation→actuator→body, without spoofing synthetic artifacts. Updated
body/object state drives the next projection. Canonical Baseline/Looming both
produce zero genuine spikes, downstream events, commands and movement.
Looming exposure changes (19→22 bodies, radius 2→3); maximum DNp01 membrane
-51.933657842035174. Feedback is wired, not realized by canonical body movement.
TEST_ONLY_NONCANONICAL events prove full nonzero composition and future exposure
change; no injection option or synthetic event enters canonical results.

Artifact `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b`;
config `3145673ad2bb6345fa9287adab37eee859861b7b029c40989a9a0fc352dff7c6`;
result `e33d5d8163b4b24755ea8479475258c28c44f8d8f351de2444a1693629435242`.
Ignored artifact 1,137,837 bytes. Measured two-run tick execution 0.113 s;
source validation 5.89 s and offline replay 6.42 s during regressions.
Scientific state/telemetry is sufficient for Phase 14 scenario selection and
backend-authoritative 3D playback/live presentation; transport/render adapters
remain Phase 14 work. No frontend/API, retuning or scripted behavior added.
See [Phase 13B](science/closed_loop_looming_scenario.md). No Phase 13C.
Decision `FIRST_CLOSED_LOOP_SCENARIO_RUNTIME_VALIDATED`; movement
`CANONICAL_GENUINE_MOVEMENT_ZERO`; handoff
`READY_FOR_PHASE14_SCENARIO_FRONTEND_INTEGRATION`; Phase 13B `PASS`.
Focused scenario tests 39 passed; full tests 975 passed, 1 deselected, two
existing dependency warnings. Ruff check/format, diff check and frontend
regressions (38 tests, lint, typecheck, build) pass. No commit/push.

## Phase 14 — scenario selection and authoritative scientific 3D playback

Existing product navigation now includes `/scenarios` and two backend-owned
canonical presets: Baseline Control / Looming Circuit Validation. A compact
`scenario_playback_v1` Pydantic/TypeScript contract is exposed through existing
FastAPI GET routes `/api/v1/scenarios` and `/api/v1/scenarios/{id}/playback`.
Every playback request fully numerically replays Phase 13B and validates
historical provenance; no scientific parameter or artifact identity changed.
Next server action loads the result; completed preset URLs support
`?replay=canonical` restoration. No database, streaming service or model editor.

R3F reuses the existing fly asset and renders authoritative body/object
snapshots only. Six-second display playback leaves 0.1 ms dt / 1.4 ms scientific
time unchanged; neighbor-only visual interpolation never affects discrete
telemetry. Play/pause/reset/scrub are independent of scientific execution.
Baseline has no object/exposure. Looming approaches (4→2.6 world_eq), exposure
19→22 and lattice radius 2→3; genuine spikes/actuation/movement remain zero.
Closed-loop completion, sensory change, feedback wiring/realization, actuation
and movement are separately visible. No fly jiggle, physics or escape fallback.

Compact responses measured 10,216 / 11,947 bytes; requests 8.99 / 9.84 s during
parallel regression work (full source validation retained). Real browser smoke
covered both presets, controls, deep links, desktop/mobile layout and errors;
no rendering errors observed. See
[Phase 14 integration](architecture/scenario_scientific_playback.md).
Remaining limitation: no nonzero genuine movement or calibrated retinotopy /
biomechanics. Next milestone is evidence-backed characterization of the silent
canonical sensory→DNp01 response, not fake movement or another metadata chain.
Phase 14 `PASS`: full Python 979 passed / 1 deselected, frontend 46 passed;
Ruff, diff check, lint, typecheck and build pass. Browser verification passed;
render dependency emitted a nonblocking Clock deprecation warning. No
commit/push; only intended Phase 14 transport/UI/tests/docs changes remain.

## Phase 15 — explainable scenario and scientific 3D presentation

Scenario catalog now foregrounds Looming Circuit Validation and labels Baseline
as an intentional zero-stimulus control. Scenario playback uses one current
looming object, a faint dashed approach guide, backend exposure inset and
prominent fixed fly; cloned scenario-only materials, lighting and cameras
improve the existing simplified GLB without changing geometry or historical
cockpit assets. No rigging, idle motion, physics or fake escape.

Selected-boundary WORLD→SENSORY→DNp01→MOTOR→BODY explanation shows the genuine
subthreshold response and why no actuator command/body movement occurs.
Compact telemetry and full-run interpretation lead; exact records/provenance
remain in details. Phase 14 DTO, scientific models/configs/timestamps and Phase
13B artifact identity remain unchanged. Scientific 1.4 ms is still presented
over six seconds; 390 px layout and desktop browser controls verified.

See [Phase 15 presentation](architecture/scenario_explainability_and_specimen_presentation.md)
for asset audit, bounded future Blender requirement, browser evidence and
limitations. Full Python 979 passed / 1 deselected; frontend 52 passed; Ruff,
lint/typecheck/build and diff check pass. Phase 15 `PASS`, no commit/push.
R3F's upstream nonblocking Clock deprecation remains; no dependency patch.
Next: characterize genuine subthreshold DNp01 looming response without
visually motivated retuning. No scientific nonzero movement claim.

## Phase 16 — genuine subthreshold DNp01 looming diagnosis

Read-only scientific response accounting consumes the unchanged Phase 13B
artifact. New result `dnp01_subthreshold_diagnostic_v1` / generated ignored
artifact `bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b`
(91,070 bytes); config hash
`6740139521b4d39c49400faf0a0f4811ee1a9ece38bff655e5642e35a8f7993a`, result hash
`3166abdb1f2dd072b26d40aba869c6a9d49bc45c85672f478180e685bf3fb39c`.
Semantic correction changes only the projection classification/explanation;
direct comparison verifies unchanged numerical results, config and config hash.

Right DNp01 10001 peaks at boundary 14 / 1.4 ms, -51.933657842035 model
coordinate, threshold -45, margin 6.933657842035; rest displacement
0.066342157965 (0.009477451138 of the 7-unit threshold excursion). Left 10010
remains -52 with margin 7. LC4/LPLC2 integrated-drive fractions are
0.274948417515 / 0.725051582485. Exposure 19→22, radius 2→3; initial exposure
affects membrane at n+2. Duration/tau_m=0.07. No missing drive, routing or
integration contradiction was found.

Recorded-footprint drive bound is 3.474071129128 with pinned gain/k, already
below the threshold excursion: projection is a material model limiter, not a
demonstrated dominant limiter. Spatial exposure, sensory/membrane dynamics,
short window and causal latency are coupled material joint limiters, not
statistically or causally independent factors; transfer adequacy is not
identifiable. Verified existing
all-311 full-exposure bound stays subthreshold at the same horizon (-47.667417
R / -47.103588 L). No unique biological culprit or parameter target is inferred.

See [Phase 16 diagnosis](science/dnp01_subthreshold_looming_diagnosis.md).
Decision `SUBTHRESHOLD_RESPONSE_CHARACTERIZED_TARGETED_MODEL_REVIEW_JUSTIFIED`:
exactly one future question is evidence for the 1.4 ms scenario temporal
design, not a replacement duration or retuning. Canonical Baseline/Looming,
historical model identities, frontend and scientific parameters are unchanged.
Phase 16 `PASS`: focused 25 / full 1,004 tests passed, 1 deselected, two existing
dependency warnings; Ruff/diff check and frontend regressions (52 tests,
lint/typecheck/build) pass. Diagnostic offline replay/tamper rejection passes.
No commit/push; only intended Phase 16 files remain.

## Phase 17 — looming scenario temporal-design evidence review

Temporal provenance is `TEST_FIXTURE_INHERITANCE`: Phase 7D's four synthetic
0.1 ms exposure intervals plus Phase 7E's ten-step inspection/recovery tail
became the 7O reference horizon; Phase 13A deliberately inherited its length,
not its exposure schedule. It is not biological timing calibration or a bug.
The numerical 0.1 ms dt and six-second frontend playback are separate choices.

Current-design decision: `KEEP_1P4_MS_FOR_CURRENT_CIRCUIT_VALIDATION_ROLE`,
explicitly a `MICRO_WINDOW_CIRCUIT_EXECUTION_TEST`, not a complete biological
looming response or behavior experiment. Next-design decision:
`SEPARATE_CIRCUIT_VALIDATION_FROM_BEHAVIOR_SCALE_SCENARIO`.

Phase 16 confirms exposure affects membrane at n+2; the radius change at n=8
first affects membrane at n=10, leaving five consuming intervals (0.5 ms).
At unchanged stationary-body trajectory, zero forward separation is reached
at 4 ms and rejected; forward body motion could invalidate geometry earlier.
This domain limit is not a proposed horizon. World_eq/ms is not physical speed.
Primary source verification distinguishes GF sensory onset (Ache's 19 ms),
LPLC2 calcium-analysis windows, post-GF leg/flight timing and electrical
stimulus-to-muscle latency; none identifies an exact replacement duration.

See [Phase 17 evidence review](science/looming_scenario_temporal_design_evidence.md).
Exactly one next action is a bounded joint trajectory/horizon design for a
separate model-space looming world experiment, preserving body feedback and
honest zero-output acceptance. No new scenario/duration, model retuning,
alternate execution, scientific artifact change or frontend change occurred.
Phase 17 `PASS`: Phase 16/13B/7O/8C replay unchanged; 1,004 Python tests passed
(1 deselected, two existing dependency warnings), 52 frontend tests passed,
Ruff/diff check and frontend lint/typecheck/build passed. Documentation only;
no commit/push.

## Phase 18 — pre-registered exploratory looming world experiment

Separate `LOOMING_WORLD_EXPERIMENT`; original Baseline and 1.4 ms circuit
micro-window configurations, scientific meanings and Phase 13B identity remain
unchanged. [Frozen design](science/looming_world_experiment_preregistration.json)
SHA-256 `580e088d89b38f086689c39568bf38bd04f5edf7f0d05065abe2c076a0d16bed`
was written/hashed before any new-scenario neural execution. No output-driven
parameter selection or post-result design change occurred.

Criterion: observe two pinned 20 ms membrane time constants, not biological
latency. Frozen duration 40 ms, dt 0.1 ms, 400 intervals / 401 boundaries.
Object radius 1, initial z=4, prescribed vz=-0.05 world_eq/ms, stationary-body
endpoint z=2; fixed R / hex(23,9), scale 10/FLOOR unchanged. Safety policy stops
before exposure if authoritative forward separation falls to/below one object
radius or geometry is unsupported; no clamping/padding. All reused scientific
models/gains/thresholds remain pinned, contact counts remain structural only.

New config/result/artifact schemas are `looming_world_experiment_config_v1`,
`looming_world_experiment_result_v1`, `looming_world_experiment_artifact_v1`.
Artifact `ee781bd8c7e903c5fab78aff02d916fe68d26998a7caf774806778cacd2b616c`;
config `daca5f023b9d31ac445340e0938ecda153439f0463b858c421b71d72bbe4ee12`;
result `7a7b35431c43f65501e298e187c97f042e90e0e3d3496cf9f44531a9544e3e42`.
Generated scientific artifact is 11,074,494 bytes and stays ignored.

First frozen run: `COMPLETED_VALID_HORIZON`, radius 2→4, exposed bodies 19→26;
R DNp01 peak -48.733429620245 mV_eq, L -52; zero spikes, motor events,
electrical input, activation, actuator commands and displacement. Closed loop,
environmental sensory change and feedback wiring true; realized body feedback
and movement false. The zero result was accepted without stronger reruns.
This is exploratory model-space behavior, not calibrated looming/escape.

Existing `/scenarios` experience now distinguishes three presets, uses compact
backend playback (283,219 bytes for the new run), displays actual 40 ms scientific
time and explicit termination, and retains six-second render-only playback.
First causal execution 3.663 s; full offline replay 23.456 s under concurrent
regression load. Full 311-identity science remains in the artifact, not the UI.

See [Phase 18 design and results](science/looming_world_experiment.md).
Exactly one next bounded action: evidence review of the identity-resolved
sensory→DNp01 transfer magnitude/normalization contract, without selecting a
new gain or targeting a spike.

Phase 18 `PASS`, decision `EXPLORATORY_LOOMING_WORLD_EXPERIMENT_VALIDATED`:
1,018 Python tests passed (1 existing deselection, two dependency warnings),
53 frontend tests passed; Ruff/check-format/diff and frontend lint/typecheck/build
passed. Historical 16/13B/full-7O/8C replays and all-three-preset real-browser
smoke passed, including 390 px and playback controls. No commit/push; only
intended Phase 18 changes remain. No scientific parameter changed after freeze.

### Phase 19 — sensory→DNp01 transfer evidence/contract review

The current contract is a deterministic ipsilateral unnormalized sum
`D_j[n] = sum(k*x_i[n])` over pinned source-body routes, with shared
`k=1.0 mV_eq/state` for LC4/LPLC2 and both sides. Phase 7F introduced it as
an explicit software/model assumption, not a fitted physiological coefficient.
Contact counts validate routing only and do not scale numerical contributions.

Normalization: `CURRENT_NORMALIZATION_ACCEPTABLE_EXPLORATORY_ASSUMPTION`.
Magnitude: `QUALITATIVELY_CONSTRAINED_BUT_NOT_NUMERICALLY_IDENTIFIABLE`;
positive population pathway evidence does not identify a numeric coefficient.
Equality: `EQUAL_TRANSFER_MAGNITUDE_ACCEPTABLE_SIMPLIFICATION`, not measured
equal efficacy. Direct population GF voltage evidence exists; a matched
observation operator for source states and mV_eq drive is absent.

Decision: `CURRENT_TRANSFER_CONTRACT_RETAIN_AS_EXPLORATORY_UNCALIBRATED_MODEL`.
Evidence-review schema `sensory_dnp01_transfer_evidence_review_v1`, identity
`f7d278372f3527393bb041e4db3b45126668a5ec904ce65cb1f9f3546b28d267`.
See [Phase 19 review](science/sensory_dnp01_transfer_evidence_review.md).
No production scientific/frontend changes, retuning, new sweep or required-gain
calculation. Historical 18/corrected-16/13B/full-7O/8C replays remain unchanged.
Exactly one next bounded action: specify source/target observation operators
and assay compatibility for LC4/LPLC2-associated GF physiology, without fitting
or selecting a replacement gain.

Phase 19 `PASS`: 1,018 Python tests and 53 frontend regression tests passed;
focused transfer tests (13), canonical review hash/mutation checks, Ruff,
format/diff checks and frontend lint/typecheck/build passed. No commit/push.

### Phase 20 — observation-operator and assay compatibility specification

Schema `neurofly_observation_operator_contract_v1`; canonical contract ID
`ae50e1faad223cdde63125a6216ce0993523f9933025fe1f04e9265450dec824`.
The isolated JSON/documentation specifies 15 variables, 8 assays, 17 mappings
and a 15×7 compatibility matrix; no production runtime depends on it.

DNp01 voltage: `DNp01_VOLTAGE_RELATIVE_DEFLECTION_POTENTIALLY_COMPARABLE_WITH_CALIBRATION`.
Sensory state: `SENSORY_STATE_ONLY_QUALITATIVELY_COMPARABLE`.
Readiness: `ADDITIONAL_ASSAY_MAPPING_REQUIRED`.
Decision: `OBSERVATION_OPERATOR_SPECIFIED_CALIBRATION_NOT_READY`.
GF/DNp01 type equivalence does not establish exact-body/preparation identity.
Source activity→x, calcium/indicator/ROI, mV_eq→GF voltage, population activation,
and world_eq→tracked body transforms remain unresolved. Relative voltage may
remove a constant reference offset but is not numerically calibrated.

See [Phase 20 specification](science/observation_operator_assay_compatibility.md).
No fitting, digitization, model changes, gain selection or frontend work.
Exactly one next bounded scientific action: locate/audit synchronized GF voltage,
stimulus and source-population metadata against the compatibility gates.

Phase 20 `PASS`: 1,022 Python tests (one existing deselection), four focused
contract tests, 53 frontend regression tests, all five historical replays,
Ruff/format/diff checks and frontend lint/typecheck/build passed. No commit/push.

### Phase 21 — GF voltage dataset compatibility/acquisition audit

Schema `gf_voltage_dataset_compatibility_audit_v1`; canonical audit ID
`219622b71f1fd79caabe83665ddc859699875177883e7810c1b2bea4676e627d`.
Phase 20 authority hash remains unchanged. Twelve candidate/source records;
zero calibration-ready datasets. Best available numerical GF candidate:
Zenodo `10.5281/zenodo.14983850` (Dombrovski), classified
`METADATA_INSUFFICIENT`. Two unmodified MAT files were inspected in the existing
Git-ignored audit cache, not committed. Array dimensions do not establish channel
identities, units, sampling or stimulus timestamps. The companion XLSX explicitly
supplies individual-file 20 kHz sampling, two-second onset, stimulus-column and
animal/trial mapping; voltage scale/filter/protocol and combined-array metadata
remain unresolved. A linked OSF LPLC2 processed
calcium dataset supports operator design but is not synchronized source/GF data.

Availability: `OPERATOR_DESIGN_DATA_ONLY`.
Readiness: `DATA_AVAILABLE_BUT_METADATA_INSUFFICIENT`.
Both file-level GF metadata and the sensory-state→biological source-activity
operator remain missing; obtaining a voltage dictionary alone cannot identify k.
No fitting, digitization, gain calculation, scientific/frontend model change or
author contact occurred. Historical 18/corrected-16/13B/full-7O/8C replay passed.

See [Phase 21 audit](science/gf_voltage_dataset_compatibility_audit.md).
Exactly one next action: obtain the authoritative stored-voltage scale/filtering,
recording metadata and combined-array/version dictionary for Zenodo 14983850,
confirming the known individual-file clock/trial mapping before ingestion or fitting.

Phase 21 `PASS`: four focused audit tests, 1,026 full Python tests (one existing
deselection; two dependency warnings), 53 frontend regression tests, all five
historical replays, Ruff/format/diff and frontend lint/typecheck/build passed.
Only documentation/metadata and isolated tests changed; no commit/push.

### Phase 22 — GF recording metadata resolution

New schema `gf_voltage_dataset_metadata_resolution_v1`, canonical ID
`b40c260a4a37ef99853425dfb927aa2729c6f93da8abd6de66d6c7ead2654ee4`.
References immutable Phase 21 audit
`219622b71f1fd79caabe83665ddc859699875177883e7810c1b2bea4676e627d`,
candidate `dombrovski_gf_zenodo_14983850`. Both local MAT hashes match; source
bytes remain ignored/unmodified. Complete workbook/inventory correspondence:
44 files, 22 animals, two trials each, four stimulus columns. Published group
counts corroborate the usable counting interpretation of the ambiguous workbook
wording; original source wording remains unchanged. The reporting summary
establishes female 3–7-day electrophysiology animals; panel-specific GF genotypes
are recorded separately from the undocumented combined array.

Stored voltage scale and file-specific acquisition/offline filtering remain
`UNKNOWN`; figure-summary mV labels are not a raw-export unit declaration.
`combined_T` axes/processing and per-trace/version mapping remain unresolved.
Candidate stays `METADATA_INSUFFICIENT`; decision
`TARGET_GF_METADATA_REMAINS_INSUFFICIENT`. No previously UNKNOWN target gate
was upgraded. Source-state observation mapping remains independently unresolved.
No fitting, gain calculation, source rewrite, scientific/frontend model change
or author contact. Phase 21/20 identities remain unchanged.

See [Phase 22 resolution](science/gf_voltage_dataset_metadata_resolution.md).
Exactly one next action: request an author-confirmed export/acquisition dictionary
for stored units/conversion/filtering and combined-array axes/processing, with
file-specific protocol/version mapping; no calibration.

Phase 22 `PASS`: four focused tests, 1,030 full Python tests (one existing
deselection; two dependency warnings), 53 frontend regressions, all five unchanged
historical replays, Ruff/format/diff and frontend lint/typecheck/build passed.
Only metadata/documentation and isolated tests changed; no commit/push.

### Phase 23 — NeuroFly v1 scientific freeze and milestone closure

**NeuroFly v1 — Initial Connectome-Based Circuit Validation** freezes the
selected MaleCNS-derived LC4/LPLC2→DNp01 closed-loop circuit, not a whole-fly
emulation or calibrated escape model. Authoritative scope, canonical IDs,
empirical/model distinctions, allowed/forbidden claims and unknowns are in
[the v1 scientific-status document](science/neurofly_v1_initial_circuit_validation.md)
and [manifest](science/neurofly_v1_scientific_status.json), schema
`neurofly_v1_scientific_status_v1`, canonical ID
`1aa1a39710ebc68030834b3a04ea202eb57fb25a0080f444db0ea19af64730a6`.
Freeze means reproducibility, not biological validation. Shared k=1 mV_eq/state
and unnormalized identity-resolved additive transfer remain unchanged;
structural contact counts never scale efficacy. mV_eq and world_eq remain
uncalibrated model-space coordinates. The visual specimen is neither MaleCNS
morphology nor validated biomechanics; the frontend presents authoritative
backend state without behavior decisions.

The 1.4 ms micro-window and preregistered 40 ms world experiment retain their
separate roles. R DNp01 peaks are respectively −51.933657842035174 and
approximately −48.733429620245 mV_eq, below −45 mV_eq. Both have zero genuine
spikes, motor output, actuation and movement; Baseline is an explicit empty
stimulus control. Closed-loop execution and feedback wiring pass, while
movement-dependent feedback realization is absent. Coupled limitations are
not independent causes; extending the horizon was not sufficient to spike.

`PHYSIOLOGICAL_TRANSFER_CALIBRATION_NOT_ESTABLISHED`: source observation
transform, target stored-voltage scale and filtering/export provenance remain
unresolved. Public GF data informed operator design but pass no full calibration
gate set. The Phase 21/22 dataset branch is **closed for v1**; their historical
author-contact/acquisition recommendations above are superseded, without
rewriting those records. No further contact, unpublished metadata request or
acquisition is planned. Reopening requires new public compatible evidence.

Completion decision: `NEUROFLY_V1_INITIAL_CIRCUIT_VALIDATION_COMPLETE`.
Exactly one next major milestone: evidence-gated selection and validation of
a second bounded MaleCNS circuit adding a genuinely new circuit capability.
No candidate is selected casually; primary functional evidence, identities,
directed routing, state/observable semantics and downstream compatibility must
be audited before one bounded implementation. No gain tuning is recommended.

All five required canonical replays passed unchanged; Phase 19–22 evidence
hashes were independently verified. Only governance documentation/manifest and
isolated tests change; no production model, scenario or frontend change.

Phase 23 `PASS`: five focused tests, 1,035 full Python tests (one existing
deselection; two dependency deprecation warnings), 53 frontend regressions,
both unchanged five-artifact replay rounds, Ruff/format/diff and frontend
lint/typecheck/build passed. Only the four intended Phase 23 files remain;
no commit/push.

## NeuroFly v2 — Phase 24 second-circuit selection

[Evidence gate](science/second_circuit_selection_gate.md) and its deterministic
[selection record](science/second_circuit_selection_gate.json) begin v2 without
altering the frozen v1 implementation or scientific-status identity.
`second_circuit_selection_gate_v1` ID:
`435ee01693ec0b4b1ad5a8547e77f865c43743cfa56d9c3dd2055a6a87b6ed41`.

Three candidates were checked against public primary evidence and actual
`male-cns:v1.0` queries: HS→DNp15 horizontal-motion readout, LC16→MDN backward
walking, and LPLC3/4→DNp07/DNp10 landing. Only the first is
`READY_FOR_BOUNDED_VALIDATION_DESIGN`. LC16's relay boundary and the nominated
landing source identity/state boundary remain unresolved; partial structural
support is not a complete circuit contract.

Decision: `SECOND_CIRCUIT_SELECTED_FOR_BOUNDED_VALIDATION`.
Selected capability: `VISUAL_COURSE_CONTROL`, restricted to a neural foundation,
not demonstrated steering. The selected motif has six HSN/HSE/HSS sources,
two DNp15 targets (11215/R, 12069/L) and six verified ipsilateral chemical
edges. The full eight-node induced query has 13 edges; seven links and the
larger recurrent/electrical network are explicitly excluded, not claimed absent.
Structural counts remain non-efficacy. HS input and DNp15 dynamics require
new bounded exploratory assumptions; no values, simulations or outputs were
selected/generated in Phase 24. Body yaw and complete course-control physiology
are outside the first neural validation. No author-contact dependency exists.

Exactly one next implementation milestone: a preregistered backend neural-only
HS→DNp15 feedforward validation slice with explicit controls, frozen assumptions
before execution, deterministic replay and result-agnostic acceptance.

Phase 24 `PASS`: five focused tests, 1,040 full Python tests (one existing
deselection; two dependency warnings), 53 frontend regressions, both unchanged
five-artifact replay rounds, Ruff/format/diff and frontend lint/typecheck/build
passed. Only four intended documentation/evidence/test files change; no
production implementation, candidate simulation, fitting, commit or push.

## NeuroFly v2 — Phase 25 preregistered HS→DNp15 neural slice

[Scientific specification](science/hs_dnp15_neural_validation.md) and
[frozen preregistration](science/hs_dnp15_neural_validation_preregistration.json)
define `BOUNDED_CHEMICAL_FEEDFORWARD_MOTIF`, not complete course control.
Preregistration schema `hs_dnp15_neural_validation_preregistration_v1`, ID
`371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074`, was
serialized/hash-frozen before neural implementation or execution. Six separate
HS sources feed bilateral DNp15 continuous model states through the six
verified routes; all seven omitted induced edges remain documented provenance.

New assumptions: signed `horizontal_motion_eq`, shared 5 ms HS proxy dynamics,
unit **proxy** transfer with a three-channel mean, 10 ms target smoothing,
dt 0.1 ms, 50 ms horizon (20 ms pulse plus 30 ms recovery). These are not
LC4/LPLC2 or DNp01 physiological equivalences; there is no threshold/spike
model, electrical coupling, motor/body mapping, API or frontend integration.
All numerical assumptions were accepted unchanged after first execution.

`hs_dnp15_neural_validation_artifact_v1` ID
`2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113`,
config hash `8ffc6263d1a70948d9a69ffa0ff066c9dcbb894d5766b72520e209ace60b452d`,
result hash `35b9bf6bb72f2d92522df25de020cc5e3d369ec0d257997d8cd7746a55e54864`.
Six conditions have 501 boundaries; neutral remains zero, matched readouts
match, unilateral propagation is ipsilateral, and declared signed reversal
reverses the proxy. Active targets peak at ±0.761610396111446 `dnp15_state_eq`
at 21.3 ms. Events are **not defined**, not measured absent spikes. R−L is a
model diagnostic, never yaw. Artifact: 714,329 ignored bytes; execution about
0.054 s, replay about 0.114 s. Frozen v1 and Phase 24 authorities are unchanged.

Next bounded action: preregister a neural-only comparison with the seven
already-verified additional chemical edges, first reviewing signs/dynamics;
no steering or motor mapping and no response-targeting parameter choice.

Phase 25 `PASS`, decision `HS_DNP15_NEURAL_VALIDATION_COMPLETE`: 23 focused
neural tests plus five selection tests, 1,063 full Python tests (one existing
deselection; two dependency warnings), 53 frontend regressions, both unchanged
five-artifact replay rounds, Ruff/format/diff and frontend lint/typecheck/build
passed. All preregistered parameters and first result identities remain fixed.
Only eight intended files change, including the narrow Phase 24 static-test
allowance for new-module offline authority validation; v1 production and
frontend source are unchanged. No commit/push.

## NeuroFly v2 — Phase 26 HS–DNp15 network-context gate

[Network-context audit](science/hs_dnp15_network_context_audit.md) and
[deterministic evidence record](science/hs_dnp15_network_context_audit.json),
schema `hs_dnp15_network_context_audit_v1`, ID
`04116360164262de5a2572f33e12cc90351869567c3202811807be576f1d03be`.
All eight identities and thirteen chemical edges are revalidated from the
committed male-cns:v1.0 authority. All seven additional edges remain excluded.
Official transmitter annotations and primary evidence support **putative
excitatory** signs, not measured per-contact recurrent effects. Chemical
timing/magnitude and the signed-proxy→chemical-effect operator remain
unidentified; HS electrical-network context is material and unmodelled.
The left DNp15→HSS return has a separate unresolved functional feedback gate.
No symmetric mirror edges or electrical substitutes are invented.

Stage A: `RECURRENT_SIGN_OR_DYNAMICS_NOT_IDENTIFIABLE`.
Phase 26 decision: `FEEDFORWARD_MOTIF_REMAINS_CURRENT_VALIDATED_BOUNDARY`.
No Stage B preregistration, recurrent parameter selection, execution, artifact,
spikes or motor/body/frontend mapping. This evidence-gate result does not
disprove biological chemical recurrence. V1, Phase 24 and Phase 25 authorities,
preregistration and canonical results remain frozen.

Next bounded action: public chemical-isolating/edge-resolved HS–HS physiology
audit for the verified HSN/HSE reciprocal pair, to specify a chemical
observation/transfer operator distinct from electrical coupling; no author
contact or simulation dependency.

Phase 26 evidence-only `PASS`: 14 focused audit tests (42 with frozen motif/
selection regressions), 1,077 full Python tests, 53 frontend tests, both six-
artifact replay rounds, Ruff/format/diff and frontend lint/typecheck/build pass.
Only four intended evidence/documentation/test files change; no commit/push.

## NeuroFly v2 — Phase 27 horizontal-motion neural playback

[Integration specification](science/horizontal_motion_neural_scenario_integration.md):
`HORIZONTAL_MOTION_NEURAL_VALIDATION` is the fourth product scenario,
`NEURAL_ONLY_VALIDATION`, exposing Phase 25's frozen `RIGHT_SIDE_MOTION`
condition (50 ms, 501 boundaries). Source artifact
`2ae44804fd570e6b64f219ee50b15bed923855e772a07b5cecc9d766ff6f4113`
and Phase 26's feedforward-boundary decision remain unchanged.

The existing catalog/playback API serves a typed additive `scenario_playback_v1`
neural variant. Six HS identities, both DNp15 identities and persisted R−L
diagnostics come from backend-validated replay. Signed continuous model-space
states, six active chemical routes and excluded recurrent/electrical context
are visible. Play/pause/reset/scrub change presentation time only. No events,
motor/body mapping, yaw, steering or scientific recalculation is added; the
motion-panel view contains no simulated body. V1's three scenarios remain frozen.

Next bounded evidence action: chemical-isolating/edge-resolved public physiology
audit for the verified HSN/HSE reciprocal pair, without author contact or
recurrent numerical execution.

Phase 27 integration `PASS`: 1,081 Python tests, 59 frontend tests, both six-
artifact replay rounds, Ruff/format/diff and frontend lint/typecheck/build pass.
Desktop/mobile and backend-unavailable/retry browser smoke pass. The original
three catalog entries and playback payloads remain byte-identical. Phase 26's
static dependency test permits only the read-only product provenance adapter,
not scientific model consumers. No canonical artifacts are regenerated; no
commit/push.

## NeuroFly v2 — Phase 28 exploratory downstream orientation

[Science specification](science/dnp15_exploratory_yaw_embodiment.md) and
[evidence gate](science/dnp15_yaw_mapping_evidence_gate.json):
`dnp15_yaw_mapping_evidence_gate_v1`, ID
`42d46ef3e5deed0c36da518cc1523cfe3d0978e5cbed2aac85a9738fcdeadf2f`.
Stage A: `EXPLORATORY_YAW_MAPPING_IDENTIFIABLE`, with type-level identity
compatibility limitations and **qualitative**, not measured graded, directional
transfer. Primary DNp15 perturbations support contralateral walking path drift
after unilateral silencing; remaining-side dominance motivates the explicitly
assumed orientation sign. Physical gain and instantaneous yaw dynamics are not
identified.

New preregistration ID
`1be0f6364070a5a5536f4c772bd47abb3be2f08357b439a51e03f034f8b2a654`
was frozen before yaw execution. Model `exploratory_yaw_orientation_plant_v1`
consumes unchanged Phase 25 outputs: unit signed differential drive,
global 50 ms horizon-normalized integration and initial orientation zero.
Units `yaw_drive_eq` / `yaw_orientation_eq` are uncalibrated model coordinates,
not radians, physical velocity or torque. There is no translation, inertia,
recurrence, electrical coupling, actuator mapping or sensory feedback.

First frozen artifact
`243914905c17ceb1285c645aa9e9700b602a9e22c8703c9f9ce4c7fe4f7e935d`:
neutral/matched orientation zero; right-only final +0.382855392953294 eq,
left-only/side-swapped/reversed negative counterpart. Parameters were not
changed after observing these results. Phase 27 remains neural-only; no API,
frontend or v1 plant changes. These are deterministic downstream proxy
responses, not biological steering predictions.

Next bounded action: specify and analytically audit an exploratory
orientation→horizontal-motion world observation contract before any closed-
loop course-control experiment; no physical optic-flow calibration claim.

## NeuroFly v2 — Phase 29 geometric observation boundary

[Observation specification](science/orientation_to_horizontal_motion_observation.md)
and [frozen contract/preregistration](science/orientation_to_horizontal_motion_contract.json):
`orientation_to_horizontal_motion_contract_v1`, canonical ID
`9e58649144a4cf3ca7cd913a6cf91dde116524906b0c600dd09f5e66ec5ffaad`.
Stage A: `ORIENTATION_TO_MOTION_OBSERVATION_IDENTIFIABLE`, classified
`GEOMETRIC_OBSERVATION_REQUIRES_BOUNDED_EXPLORATORY_ASSUMPTIONS`.

An independent world-fixed panoramic heading and unwrapped orientation
endpoints define relative-view geometry. Completed-interval change, not
absolute orientation, yields a rate-like descriptor. One orientation_eq per
abstract cycle, global 50 ms reference normalization, clipping to [-1,1] and
opposite R/L descriptor bases are explicitly exploratory assumptions. Wrapped
view seams retain continuous winding; ambiguous body jumps are rejected.
Observation at boundary n describes [n-1,n] and is available only for the next
neural interval, avoiding a same-boundary algebraic loop.

Units remain model-space (`yaw_orientation_eq`, `relative_view_eq`,
`horizontal_motion_eq`); no retinal, biological angular-velocity or HS
transduction calibration is established. Phase 25/28 equations/artifacts and
Phase 27 neural-only product remain unchanged. Operator tests use synthetic
geometry; stored Phase 28 traces are checked only for API/domain compatibility.
No descriptor is propagated to neurons, no feedback run occurs and no API,
frontend, translation or body-mechanics change is made.

Phase 29 decision: `OBSERVATION_OPERATOR_SPECIFIED_WITH_EXPLORATORY_NORMALIZATION`.
Next bounded action: preregister a backend-only course-control experiment with
this completed-interval observation and frozen Phase 25/28 equations, including
controls and analytical stability assessment before any closed-loop execution.

Phase 29 `PASS`: 51 focused tests, 1,165 full Python tests (one integration
test deselected), 59 frontend regression tests and all lint/format/typecheck/
build/diff gates pass. Required historical replay identities and all four
existing playback payload hashes remain unchanged. No commit/push.
