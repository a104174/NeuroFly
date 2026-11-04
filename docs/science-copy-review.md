# Scientific copy review

All new scientific wording written for the redesign, in one place, with where it appears and the repository
source it relies on. **None of it has been reviewed by a scientist.** Wording that was already on the site
before the redesign (the reviewed Science text) is unchanged and not listed. Where a row says "no
repository source", the wording is mine and needs your decision, not just a check.

How to use: read each row, compare with the cited source, and mark it OK, change it, or remove it. Rules
the wording follows are in the header of `web/src/content/science-copy.ts` and in `docs/redesign-brief.md`
(sections 3 and 7, Phase 0 decisions).

Generated parts (section A) are produced from `science-copy.ts`, so they match what visitors read.

## A. Central copy file (`web/src/content/science-copy.ts`)

### A1. The five kinds (`KIND_COPY`)

| Kind | Label | Tooltip text | Repository source |
| --- | --- | --- | --- |
| structural | Structural | From the MaleCNS v1.0 connectome. Describes physical wiring, not signal strength. | docs/redesign-brief.md section 3 and 7 (owner's definitions); MaleCNS description in docs/science/ |
| model-assumption | Model assumption | Chosen for the model; not validated here. | docs/redesign-brief.md section 3 and 7 |
| model-state | Model state | Simulation output in model units. Not a biological measurement. | docs/redesign-brief.md section 3 and 7; Phase 0 decision 4 (units) |
| not-evaluated | Not evaluated | No comparison with real fly data has been made for this result. This is not a failure. | docs/science/neurofly_v1_scientific_status.json (no empirical validation) |
| unavailable | Not available yet | Deliberately off or not built yet. The reason is on the Status and limits page. | docs/redesign-brief.md section 7 |

### A2. Units and provenance wording

| Item | Text | Source |
| --- | --- | --- |
| model-equivalent note | model-equivalent, not measured | Phase 0 decision 4 |
| model-equivalent explanation | A model-equivalent unit. The simulation produces this number; it was not measured in a fly. | Phase 0 decision 4 |
| dimensionless | dimensionless | Phase 0 decision 4 |

### A3. Capabilities on the Status and limits page (`CAPABILITIES`)

Each reason is paraphrased from the cited report. **Please check each against its report.**

| Group | Capability | Text shown to visitors | Report cited |
| --- | --- | --- | --- |
| Available | Selected MaleCNS connectivity | Identified neurons, their sides and the directed routes between them for the selected circuits, pinned to male-cns:v1.0. Contact counts are routing metadata, not signal strength. | `docs/science/neurofly_v1_scientific_status.json` |
| Available | Neuron shape samples | Raw skeletons for two DNp01 bodies and a fixed six-body sample, taken from the official MaleCNS release. They are shown as stored, not simulated. | `docs/architecture/malecns_morphology_inspector.md` |
| Available | Canonical scenario replays | Five preset scenarios, recorded in advance and reconstructed offline with hash checks. The browser plays them back from stored data; it does not run them again. | `docs/science/experiment_artifact_contract.md` |
| Model only | Looming circuit (LC4 and LPLC2 to DNp01) | Runs deterministically. In the canonical presets the DNp01 model stays below its spike threshold and the body does not move. Zero model output is not evidence of a biological failure to respond. | `docs/science/neurofly_v1_scientific_status.json` |
| Model only | HS to DNp15 steering readout | Continuous, dimensionless proxy states from six HS sources to two DNp15 targets. They are not measured membrane voltages, and no spike or event model is defined. | `docs/science/hs_dnp15_neural_validation.md` |
| Model only | Movement in the Lab | Runs in your browser. The walking neural update is a reimplementation of the pinned Python model; it agrees with the recorded Python run to within 1e-8 in each model-space quantity over eight seconds. Forward propulsion, boundary response and flight are engineering rules, not biology. | `docs/science/interactive_neural_locomotion_v2.md` |
| Not available yet | Level C visual-angle mapping | The column-space structure is kept but switched off. No validated mapping from a world object to MaleCNS columns exists, so it is not presented as calibrated vision. | `docs/science/sensory_consumption_boundary.md` |
| Not available yet | Comparison with real fly data | Not done. A direct comparison with published calcium responses was refused because the published stimulus and observable are incompatible with what the model supports. No agreement or disagreement is claimed. | `docs/science/empirical_hs_dnp15_response_benchmark_v9_2.md` |
| Not available yet | Calibrated DNp01 voltage and transfer gain | The transfer magnitude cannot be identified numerically from current evidence, and calibration readiness is recorded as needing additional assay mapping. | `docs/science/neurofly_v1_scientific_status.json` |
| Not available yet | Muscle and wing physics | Not modelled. Body motion and leg animation are engineering rules. They do not establish biological muscle control or physiological flight, and validated biomechanics is listed as an open question. | `docs/science/neurofly_v1_scientific_status.json` |
| Not available yet | DNg100 and T1 as the movement controller | Kept as a shadow pathway. It is not the controller that drives movement in the Lab. | `docs/science/dng100_t1_motor_response_shadow.md` |
| Not available yet | Whole-brain simulation | Not attempted. Only the selected circuits run; the rest of the MaleCNS nervous system does not. | `docs/science/neurofly_v1_scientific_status.json` |

### A4. Open questions (`OPEN_QUESTIONS`)

Source: the unresolved list in `docs/science/neurofly_v1_scientific_status.json`.

- How a sensory state should be observed (the observation transform)
- The physiological size of the sensory-to-DNp01 transfer
- The relative per-body efficacy of LC4 and LPLC2
- Calibrated DNp01 electrophysiology
- Absolute retinal registration
- Physical world scale
- Validated biomechanics
- Broader behavioural circuits

### A5. Glossary definitions (`GLOSSARY`)

Relationships follow redesign brief section 3. **Open question 11: do they match the backend model?**

| Term | Definition | Group |
| --- | --- | --- |
| Scenario | A defined situation: which stimulus, which circuit, which settings. Like a recipe. NeuroFly offers five canonical scenarios, recorded in advance. | objects |
| Run | One execution of the model. The model is deterministic, so the same inputs give the same run. A run is a model run, not a trial with a real fly. | objects |
| Experiment | A completed run published here with its status and provenance. Publishing does not mean evaluated: today's recorded run is an engineering test, not a scientific experiment. | objects |
| Artifact | The stored data package behind an experiment or a neuron. It appears only as an identifier and a link. | objects |
| Cockpit | The synchronised view of the world, the connectome and the telemetry for one experiment. It plays back a completed run; it does not control a live simulation. | objects |
| Structural | Taken from the MaleCNS v1.0 connectome, which maps the physical wiring. Examples: neuron shape, which neurons connect. | kinds |
| Contact count | How many synaptic contacts were mapped between two neurons. It does not measure signal strength. | kinds |
| Model assumption | A value or rule chosen for the model; not validated here. Some are starting values taken from published models and general fruit fly electrophysiology. Examples: the gain settings G_LC4 and G_LPLC2, and neuron-model parameters such as resting potential and threshold. | kinds |
| Model state | A number the simulation produces, in model units such as mV_eq. It is not a biological measurement. | kinds |
| Not evaluated | No comparison with real fly data has been made for this result. It is not a failure. All current experiments have this status. | kinds |
| Not available yet | A capability that is deliberately off or not built yet. The Status and limits page gives the reason for each. | kinds |
| Connectome | A map of a nervous system's neurons and their connections. | science |
| Body | One reconstructed neuron in the connectome. The looming circuit has 313 bodies: 126 LC4, 185 LPLC2 and 2 DNp01. | science |
| Morphology | The 3D shape of a neuron. | science |
| LC4 and LPLC2 | Visual projection neurons. In the looming circuit there are 126 LC4 and 185 LPLC2. | science |
| DNp01 | A descending neuron, which carries signals from the brain towards the body. The looming circuit has two, one on each side. | science |
| HS and DNp15 | The neurons selected for the horizontal-motion circuit: three HS neurons on each side feed the DNp15 neuron on that side, six HS and two DNp15 in all. | science |
| Looming | A visual stimulus in which an object appears to approach. | science |
| Leaky integrate-and-fire | A simple neuron model: input accumulates, leaks away over time, and triggers a spike at a threshold. NeuroFly uses it for the looming circuit. The HS to DNp15 path uses continuous proxy states and defines no spikes. | science |
| Kinematic | Movement is computed from rules, without simulating muscles or wing physics. | science |
| Deterministic | The same inputs always give the same output. NeuroFly's current runs use no random drive. | science |

### A6. Home page copy (`HOME_COPY`)

Headline, statement and the four status facts are the owner's wording (Phase 0 decision 5). The rest is new.

| Field | Text |
| --- | --- |
| headline | Selected fruit fly circuits, modelled from the connectome. |
| statement | NeuroFly is a research model of selected fruit fly neural circuits, built from the MaleCNS connectome and connected to a simplified simulated body. |
| poster caption | The visible specimen is an artistic 3D asset, not anatomy reconstructed from MaleCNS. |
| status fact (structural) | Two selected circuits: looming (313 bodies) and HS → DNp15 (8 bodies). Not a whole brain. |
| status fact (structural) | Wiring from MaleCNS v1.0 |
| status fact (model-assumption) | Kinematic body, no muscle or wing physics |
| status fact (not-evaluated) | Not yet evaluated against real flies |
| layer: The connectome (structural) | Which identified neurons connect, taken from the MaleCNS v1.0 connectome. It describes wiring, not signal strength. |
| layer: The neuron model (model-assumption) | Explicit rules for how each neuron's state changes over time. They are chosen for the model, and some follow published models. They are not validated here. |
| layer: The output (model-state) | What the simulation produces, in model units such as mV_eq. It is a model result, not a measurement from a fly. |
| Lab card | Explore the Lab. Walking and flight modes in a 3D enclosure. Movement follows engineering rules with a neural steering influence, and there is no muscle or wing physics. (Runs in your browser) |

### A7. State messages (`STATE_COPY`)

| State | Text |
| --- | --- |
| API down | The data service isn't responding. Nothing on this page has been lost. |
| Integrity failure | The stored results failed their integrity check. No results are shown, and none are substituted. Nothing on this page has been lost. |
| WebGL off | 3D isn't available on this device. The data below is the same. |
| Context lost | The 3D view stopped. The browser released the graphics context. Nothing on this page has been lost. |
| Low power | Showing simplified shapes for smoother playback. |

## B. Science page (`web/src/app/science/page.tsx`)

| Where | Wording | Source |
| --- | --- | --- |
| Scope paragraph (`data-claim="scope"`). "Separate models" confirmed: `docs/science/hs_dnp15_neural_validation.md` says the HS → DNp15 model is "an isolated signed continuous-proxy kernel, not a copy of the looming exposure model or a relabelled DNp01 LIF"; the looming model is a spiking LIF (`docs/science/neural_simulation_core.md`). | "NeuroFly models two selected circuits from the MaleCNS v1.0 connectome: the looming circuit, where the visual neurons LC4 and LPLC2 feed DNp01 (313 bodies), and the HS → DNp15 steering circuit (8 bodies). They are separate models with their own states and outputs, so their counts are not added together. Neither is a whole brain, and no result has been compared with data from real flies." | Body counts and circuits: Phase 0 decision 5 (owner's wording for the status strip); `docs/science/neurofly_v1_scientific_status.json`. The sentence "separate models ... not added together" is the owner's rule that counts are never added. |
| Kinds paragraph (`data-claim="kinds"`) | "Where a value is labelled by kind, the label comes with a shape. Some older panels (scenario playback, parts of the Cockpit and the Lab tools) do not carry kind labels yet." **Your requested sentence ("Scientific values on this site are labelled by kind, with a label and a shape.") could not be confirmed**: see "Kind labelling audit" below. | Brief section 7. No repository report. |
| Circuit-check note (`data-claim="circuitcheck"`) | "A "circuit check" runs the model through the selected circuit and confirms that it executes as specified. Some circuit checks are preregistered, such as the HS → DNp15 check. A circuit check is not biological validation: it does not compare the result with real fly data." **"A circuit check is a preregistered test" could not be confirmed for all checks.** Preregistered: the HS → DNp15 check (`docs/science/hs_dnp15_neural_validation.md`, `hs_dnp15_neural_validation_preregistration.json`) and the 40 ms looming world experiment (`looming_world_experiment_preregistration.json`). Not preregistered: the 1.4 ms looming circuit micro-window and the baseline control (`docs/science/neurofly_v1_initial_circuit_validation.md` lists only the world experiment as preregistered). | Phase 0 decision 1 (owner: "Circuit check", not "Validation"). |
| Open questions lead-in | "The project's own v1 status records these as unresolved:" followed by the list in A4 | `docs/science/neurofly_v1_scientific_status.json` |
| Status and limits lead | "NeuroFly is a research model. This page lists what it can and cannot do, and why. Anything switched off is deliberate, not a fault, and each reason comes from a project report that you can open." | Brief section 5. "Deliberate, not a fault" is my wording. |

## C. Scenario detail pages (`web/src/components/ScenarioCockpit.tsx`, `GuidedCaptions` data in `Playback`)

The guided tour has three captions. Two reuse existing text; one is new.

| Caption | Wording | Source |
| --- | --- | --- |
| Start of the run | The scenario's existing `observation` text (`web/src/lib/scenarioPresentation.ts`, `scenarioCopy`), which is the text the old page already showed | Existing, unchanged |
| Stored model state | "Every frame is a stored model state with its model time. Scrubbing replays the record; nothing is computed in your browser." | New. Describes how the page works (checked in `tests/read-only.test.ts`). |
| End of the run | "Recorded outcome: {outcome}. {limit}" using the existing `experimentMetadata` outcome and limit strings | Existing strings, new sentence frame |

Other new sentences on the page: "Everything on the stage is stored model state, not a measurement of a fly." (new); "What to notice" repeats the existing purpose and limit strings; the next step reads "See the published experiments. The list cannot be filtered by scenario yet." (true: the API has no scenario field).

## D. Experiment detail pages (`web/src/components/experiment/ExperimentDetail.tsx`)

| Where | Wording | Source |
| --- | --- | --- |
| Summary | "This run applied the {condition} condition to the selected LC4 and LPLC2 → DNp01 circuit, for {duration} ms in steps of {dt} ms." followed by the existing recorded-run purpose, or "It has not been compared with real fly data." | Built from the experiment summary fields (`pathway_condition`, `duration_ms`, `dt_ms`); purpose text exists in `recordedExperimentPresentation.ts` |
| Setup labels | "Circuit (structural)", "Stimulus encoder (model assumption)", "Neuron model (model assumption)", "Body model: Not recorded in this experiment summary." | Kind assignments follow brief section 3. **Check that the encoder and the neuron model are correctly called Model assumption.** |
| Results note | "Every number below is model state. Counts are dimensionless. Units ending in _eq are model-equivalent, not measured." | Phase 0 decision 4 |
| What this does not show | 1. "These are model readouts. They are not motor output or behavioural predictions." 2. "No comparison with real fly data has been made, so the result is Not evaluated." 3. "Structural contact counts are connectome metadata. They are not measured synaptic strength." 4. "Units ending in _eq are model-equivalent. They were not measured in a fly." | 1 and 3 are from the old page's note ("These are model readouts, not motor output or behavioural predictions. Structural contact counts remain connectomic metadata, not measured physiological synaptic efficacy."). 2 and 4: `neurofly_v1_scientific_status.json` and decision 4. |
| Unit change | The "peak membrane" values were labelled "mV"; they are now "mV_eq" (model-equivalent). **Please confirm these values are model quantities, not measured voltages** (the API field is named `peak_membrane_mv`). | `web/src/lib/neuroflyClient.ts` (field name), decision 4 |

## E. Neurons pages (`web/src/app/morphology/`, `MorphologyInspector.tsx`)

| Where | Wording | Source |
| --- | --- | --- |
| Intro | "This is the reconstructed shape of real neurons, not a simulation." | Brief section 5 (suggested sentence) |
| Page label | Structural badge; "{n} source skeletons share one native-frame view. It is separate from experiment playback and is not aligned to the fly visual asset." | Old inspector text, shortened |
| Viewport description | "{n} source skeletons of real neurons in one shared native-frame view. Orbit with the mouse or touch. The same body details are listed below." | New |
| Saved image footer | "NeuroFly. Reconstructed shapes of real neurons (Structural), not a simulation. Source: MaleCNS v1.0. Artifact {id}. Raw source skeletons in native voxel axes. Camera, colours and scale are presentation only." | New. "Native voxel axes" and "presentation only" come from the old inspector notes. |
| Connectivity source line | "...integrity-checked `neurons.jsonl` and `connections.jsonl` SHA-256 provenance..." (was "verified") | Old text, one word changed (decision 1) |

## F. Lab (`web/src/components/lab/labClaims.ts`, `/visual-lab`)

This section changed after your review request: each Lab tool now states only what its own evidence supports. The notice, the evidence paths, and the reasoning are below.

| Tool | Claim shown | Evidence in the repository |
| --- | --- | --- |
| Explore | "The walking model runs in your browser." The neural update is a TypeScript reimplementation of the pinned Python model; for the first 1,500 steps (30 s) a live session equals the finite navigation model step for step, and that model agrees with five recorded Python runs within 1e-8 (largest difference 4.97e-13). Longer sessions have no Python comparison. Propulsion, boundary response and flight are engineering rules; flight is not covered by the comparison. Live sessions are not saved or exported. | `web/tests/live-ground.test.ts`; `web/tests/continuous-navigation.test.ts`; `docs/science/continuous_arena_navigation_v3.md` (1,501 boundaries, five cases); `docs/science/interactive_neural_locomotion_v2.md` (401 boundaries, 1.68e-14); the page text "Complete live-session recording and export are not available." |
| Research tools | "Some modes run the model in your browser; others play back recorded Python runs and compute nothing." Saved runs in My Experiments stay in this browser (IndexedDB), under this address, and are not sent to a server. | `web/tests/experiment-library.test.ts`; `web/tests/read-only.test.ts`; same parity evidence as Explore for the browser modes. **Not proven:** which individual research modes are browser-computed versus replayed; the text says "some" for that reason. |
| Fly viewer | "A visual model of the fly body. It shows no simulation and no neural activity." No 1e-8 or "saved runs" claim. | Page description in `web/src/app/visual-lab/fly/page.tsx` ("No scientific simulation") |
| Overview | "Explore and the research tools run model code in your browser; the fly viewer only shows a body model." (The earlier "Nothing is sent to a server" was removed: the tools do fetch recorded data from the server.) | Same as above |
| Capability row "Movement in the Lab" (A3) | "Runs in your browser. The walking neural update ... within 1e-8 ... over eight seconds. Forward propulsion, boundary response and flight are engineering rules, not biology." | `docs/science/interactive_neural_locomotion_v2.md` |
| Scenarios page | "Explore runs in your browser: walking and flight modes with engineering movement and no muscle or wing physics." | As Explore |

## G. Cockpit (`web/src/components/ScientificCockpit.tsx`)

| Where | Wording | Source |
| --- | --- | --- |
| Toolbar | "Replay of a completed run" | Brief section 5 (live-control safeguard) |
| Phone note | "This is a simplified replay. The connectome view and raw values need a larger screen." | Brief section 5 |
| Raw table caption | "Values at the current stored boundary. Units ending in _eq are model-equivalent, not measured." | Decision 4 |
| Provenance row | "{rest} mV_eq rest, {threshold} mV_eq threshold (model references, not measured)" (was "mV") | `membrane_state_references` in the experiment summary. **Please confirm these are model reference constants.** |
| Detail panel groups | System, Body, Stimulus and neural signals, Events | Brief section 5 (Stimulus, Neural, Body, System) merged into four groups |

## H. Lists and stage states

| Where | Wording | Source |
| --- | --- | --- |
| Experiments banner | "No experiment has been evaluated against biological data yet." | Brief section 5 (suggested wording) and `neurofly_v1_scientific_status.json` |
| Recorded run tag | "Engineering test, not a scientific experiment" | Phase 0 decision 5 (owner's label) |
| Scenario cards | Each shows its existing scientific caveat under "What this does not show" | Existing API text (`scientific_caveat`) |
| Viewport states | "3D isn't available on this device.", "The 3D view stopped.", "{what} not included in this artifact." | New, factual |
| Not recorded | "Not recorded" for the experiment scenario and date, and for the body model | The API has no such fields (backend request in `redesign-progress.md`) |

## I. Where the model parameters come from (traced)

Source: `docs/science/neural_model_selection.md`, section "Parameter provenance and identifiability" (a table
with an evidence class per parameter). The repository itself says the values are "starting points ... not
frozen biological truths".

| Parameter | Value | Evidence class in the repository | Accurate wording |
| --- | --- | --- | --- |
| Resting potential, reset potential | −52 | `PUBLISHED_MODEL_ASSUMPTION` (Shiu and Kakaria precedent; Drosophila electrophysiology priors) | Taken from published models and general fly electrophysiology; not measured for these cells |
| Threshold | −45 | `DROSOPHILA_PRIOR` (Gouwens, Wilson and Shiu precedent) | Same |
| Membrane time constant (20 ms), filter decay (5 ms) | | `PUBLISHED_MODEL_ASSUMPTION` | Same |
| Refractory interval (2.2 ms), chemical delay (1.8 ms), edge sign | | `DROSOPHILA_PRIOR` | Same |
| Gains G_LC4, G_LPLC2 and the synapse-count scale `k_syn` | configured | `NEUROFLY_FREE_PARAMETER` (no MaleCNS physiological conversion) | Chosen for the model |
| Baseline drive | 0 | `PUBLISHED_MODEL_ASSUMPTION`, "not measured here" | Chosen for the model |
| Resistance and capacitance | | `UNRESOLVED` | Not used |
| Gain settings exist? | | **Yes**: `G_LC4` and `G_LPLC2` are free parameters in the experiment summary (`lc4_gain_mv_eq`, `lplc2_gain_mv_eq`) | The "gain settings" example is kept |

So some parameters are drawn from published modelling work and fly electrophysiology priors. The words "not
measured from the fly" were removed from the Model assumption tooltip, glossary entry, Home layer text and
Cockpit provenance row. The unit note "model-equivalent, not measured" (owner's decision 4) stays, because it
describes the output values. Peak membrane values keep `mV_eq`.

## J. Kind labelling audit (item 1)

The sentence "Scientific values on this site are labelled by kind, with a label and a shape" is **not true
everywhere**. A browser audit of 17 routes, plus reading the panels, finds values without a kind label and
glyph in these places:

- Scenarios list: the horizon of each scenario ("1.4 ms", "40 ms", "50 ms").
- Scenario playback panels (current result, telemetry, explanation, trace): numbers carry text tags such as
  "mV_eq", but no kind label or shape.
- Experiment page: the replay overlay (time, angular size) and the timeline inspector.
- Cockpit: Run identity numbers, selected-neuron values, plot readouts and event times use older "SIMULATED"
  tags, not kind labels with shapes. The Overview readouts and the Raw table do have kinds.
- Lab Explore live readouts (for example propulsion, heading) and every Lab research tool panel.
- Neurons detail source-data numbers (node counts and coordinates): the page carries one Structural label,
  not one per value.

Decision needed: either add kind labels to those panels (a re-skin of the legacy panels, not done), or keep
the narrower sentence now on the Science page.
