# NeuroFly v10.3b — Science & Project

Presentation-only work on `0c0e3f37fcbea544de7d5eda0a70c06e4e6b4bf9`.
The new static `/science` route explains the implemented system. The existing
homepage `/#science` section remains a valid bookmark. Global Science navigation
and the homepage hero CTA lead to the full explanation. Recorded experiments
remain secondary. No scientific configuration, data, API or runtime is changed.

## Claims audit (before page implementation)

Categories: **B** biological source information; **M** computational modelling
assumption; **E** engineering implementation; **O** observed computational result;
**I** integrity/reproducibility contract. “Verified” means supported within the
stated scope, never a blanket biological validation. Public `data-claim` markers
map the page's substantive groups to the following evidence.

| Claim ID / proposed public statement | Category | Documentation / primary authority | Supporting implementation | Assessment |
| --- | --- | --- | --- | --- |
| source: MaleCNS supplies neuronal annotations and reconstructed synaptic connectivity; NeuroFly pins selected records to `male-cns:v1.0` | B | [Official dataset access](https://male-cns.janelia.org/download/), checked 2026-10-25; README Phase 1A; `docs/science/hs_dnp15_neural_validation.md` | `src/neurofly/hs_dnp15_neural_validation.py:load_structural_authority`; `web/src/lib/interactiveNeuralLocomotion.ts` constructor | Verified source role; no whole-dataset execution or neuron-count claim |
| structure: Structural contacts identify selected routes, not measured physiological efficacy | B/M | `docs/science/hs_dnp15_neural_validation.md`, structural revalidation and frozen assumptions | Python `route_contributions`; TS `calculateBoundary` uses equal three-source mean, not contact multiplicity | Verified; counts remain provenance in this HS path |
| circuit: Six HS proxy states feed two DNp15 proxy states through a selected chemical feedforward motif | M | Same report and preregistration; `docs/science/hs_dnp15_network_context_audit.md` | Python `proxy_step`, `_execute`; TS `InteractiveNeuralEngine.calculateBoundary` | Verified selected implementation; broader inhibition, recurrence and electrical coupling excluded |
| sensory: Completed pose changes relative to geometric landmarks produce bounded signed model inputs | M/E | `docs/science/interactive_neural_locomotion_v2.md`; `docs/science/controlled_neural_steering_v9_3.md` | `InteractiveNeuralEngine.observation`; Python `experimental_neural_locomotion.py` | Verified; engineering visual reduction, not measured retinal optic flow |
| states: HS/DNp15 states use explicit smoothing rules and dimensionless coordinates | M | HS/DNp15 report equations and frozen timescales | Python `proxy_step`; TS old-state source/target updates | Verified; not measured voltage, calcium, spikes or physiological calibration |
| projection: The right-minus-left model readout contributes a bounded engineering yaw command | M/E | `docs/science/continuous_arena_navigation_v3.md`; v9 flight architecture | `InteractiveNeuralEngine.calculateBoundary`; `web/src/lib/neuralFlight.ts:projectFlightYaw` | Verified; not a calibrated biological motor mapping |
| navigation: Explore combines engineering forward propulsion, model steering and geometric boundary response over 30 s | E | Continuous navigation v3 report | `ContinuousNavigationEngine.velocity`, `calculateBoundary`, inherited `advance`; `NAVIGATION_POLICY` | Verified; contact stops outward translation, bounded pose integration and inward steering are engineering rules |
| gait: Articulated gait follows authoritative body movement; leg animation does not propel the body | E | `docs/architecture/articulated_fly_gait_v6.md` | `web/src/lib/articulatedGait.ts`; `ContinuousNavigationArena` gait frames | Verified presentation; no muscle-level dynamics |
| body: The rendered fly is an artistic asset, not an anatomy reconstructed from MaleCNS | E | `docs/architecture/product_experience_v10_0_v10_1.md`; asset manifest and CC BY 4.0 attribution | `web/src/assets/fly_visual_v2f.json`; `SpecimenVisual`, `LabPreview` | Verified; image is a static render/capture, not an experimental measurement |
| shadow: DNg100/T1 remains a shadow pathway, not Explore's applied ground motor controller | M/E | `docs/science/dng100_t1_motor_input_shadow.md`; motor-to-gait bridge v7 architecture | `web/src/lib/motorGaitBridge.ts`; Explore composition | Qualified to the current browser Explore path |
| flight: Existing experiments compose neural readout with an engineering flight plant | M/E | `docs/architecture/experimental_3d_flight_v8.md`; `experimental_neural_flight_steering_v9.md`; controlled v9.3 report | `web/src/lib/neuralFlight.ts`; `engineeringFlight.ts`; `controlledNeuralSteering.ts` | Verified implementation; neither aerodynamic nor physiological calibration claimed |
| experiments: Five canonical presets include neutral/looming controls, neural-only horizontal motion and orientation feedback | M/O | `docs/architecture/product_experience_v10_3a.md`; relevant scientific reports | Existing `SCENARIO_KINDS`, `experimentMetadata`, backend preset/playback contracts | Verified IDs/durations; page introduces three examples and links the existing catalogue, no new results |
| empirical: Existing empirical HS/DNp15 work does not establish model agreement with published calcium responses | O/limitation | `docs/science/empirical_hs_dnp15_response_benchmark_v9_2.md` (`STIMULUS_INCOMPATIBLE`); horizontal adapter v9.2b (`CONTRACT_ONLY`) | Existing empirical benchmark and declarative contract | Verified refusal; unavailable polarity/masks and incompatible observables remain limitations |
| reproducibility: Defined configurations, source identities, fixed timesteps and event logs support bounded deterministic reconstruction | I | `docs/science/reproducible_experiment_runs.md`; `experiment_artifact_contract.md`; continuous navigation report | Python `experiments.py`, `experiment_artifacts.py`; TS navigation replay/validation | Verified per versioned contract; current Explore has no randomness, no generic seed or universal cross-hardware bitwise claim |
| integrity: Hash checks and semantic reconstruction have distinct roles; integrity failure prevents substitute results | I | `docs/science/experiment_artifact_contract.md`; v10.3a report | `load_experiment_artifact`, `replay_experiment_artifact`; `validateNavigation`; `RecordedExperiments` | Verified scoped mechanisms; no promise that all archives are currently healthy |
| availability: Scientific source data and completed-run storage are separate from this static explanation | I | Official MaleCNS access page; artifact contract; v10.3a report | Existing API/store and public static Science composition | Qualified: some workflows need external source inputs; Lab sessions are not automatically recorded in the archive; known 409 not repaired |
| limits: No whole-CNS execution, complete biomechanical reconstruction, consciousness or demonstrated learning is established | Limitation | Above implemented scopes, scientific reports and current runtime | Selected models and engineering plant boundaries | Qualified scope statement; no inference about consciousness from simulated motion |

The [Erginkaya et al. primary paper](https://www.nature.com/articles/s41593-025-01948-9)
was checked at the publisher on 2026-10-25 as background on HS-associated optic-flow
processing. Its broader network and calcium findings are not claimed as NeuroFly's
implemented network or empirical validation. No figures, data tables or author
code are reproduced. Aspirational model-selection documents are not used as proof
of current implementation. No numerical efficacy or biological accuracy claim is
made.

## Information architecture and diagram semantics

Hero → conceptual closed loop → biological source versus explicit model → engineering
body and visual representation → three existing experiment examples → reproduction
and integrity → visible limitations → sources and further exploration.

The structural-source strip feeds circuit selection. It is outside the runtime
loop: static connectome evidence is not acquired on every tick. The loop is
observation → neural states → engineering projection → accepted body pose → next
observation. Rendering reads state; screen pixels and leg animation do not feed
the scientific observer. Stage order is conceptual, not a new timing contract.
CSS connections, arrows and labels are explanatory, not anatomical edges, measured
traces or a live monitor. The ordered list remains legible without CSS/animation.

## Assets, access and implementation boundaries

Reuse only the existing optimized fly WebP renders and real laboratory capture.
Source asset/derivative provenance, dimensions and licences remain in
`product_experience_v10_0_v10_1.md` and the shared footer: fly by mlykouretzos and
lab table by zeeshanfareed, CC BY 4.0, modified/rendered for NeuroFly. Original
GLB/image bytes are unchanged. Existing fallback components remain authoritative.

Sources link to the official MaleCNS site, the original paper and real GitHub
documentation. Public repository links may show the last published revision until
this local phase is separately authorized for publication. No local paths are
rendered to visitors. `/science` requires no scientific API, dataset, archive or
simulation. Native disclosures, one H1, skip navigation, visible focus, labelled
diagram stages and scoped reduced-motion styles support accessibility. No new
dependency, WebGL context, neural engine or telemetry is introduced.

## Validation

Commands run from `web`:

```sh
node --import tsx --test tests/science.test.ts tests/homepage.test.ts tests/branding.test.ts tests/discovery.test.ts
PATH="/path/to/NeuroFly/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 npm test
npm run lint
npm run typecheck
npm run build
```

- Focused tests: 38/38. Full frontend suite: 365/365 (8 new Science tests;
  focused tests overlap the full suite). No scientific test was modified.
  The previously reported metadata intermittency did not recur in the final run.
- ESLint, typecheck, production build and `git diff --check` passed. The build
  identifies `/science` as a prerendered static route. The first typecheck found
  stale generated `.next` route types; canonical build/development generation
  refreshed them, and the standalone typecheck subsequently passed. The generated
  `next-env.d.ts` was restored to its original bytes.
- Actual Chromium checks against the local production build at 320, 390, 768,
  1024 and 1440 px found no horizontal overflow or clipped diagram/reference text.
  Desktop/full/mobile, diagram, body, methodology, limitations and navigation
  screenshots were inspected. QA outputs are outside Git in the sibling
  `neurofly-assets/work/v10-3b-science-project/` directory, not source authorities.
- Keyboard menu Enter/Escape/focus restoration, skip navigation, native model
  disclosure, reduced motion and a 200% CSS-zoom layout stress check passed.
  This is not a claim of formal WCAG certification or native browser text-zoom
  coverage. Science loaded with scientific requests blocked: zero scientific
  requests, zero canvas and zero unexpected page-console errors. Intentional
  image failures exercised both existing fallbacks without losing content/links.
- A no-JavaScript browser test exposed the inherited root loading boundary hiding
  otherwise static content. A Science-scoped `noscript` reveal follows the
  existing homepage pattern. Retesting showed the Science heading/content visible,
  the inherited loader hidden, and the native mobile menu usable without scripts.
- Home → Science, the original `/#science` bookmark, Lab and research navigation
  passed. Lab reached Ready to explore with one canvas; Play/Pause/Reset worked.
  All 15 historical selectors remain in the research route. The local scenario API
  at `http://127.0.0.1:8000` is not running (`ECONNREFUSED`): Explore correctly shows
  its existing unavailable state. No substitute scenarios were supplied and no
  live scenario replay is claimed in this browser session. Catalogue IDs, metadata,
  deep links and replay contracts are covered by the passing existing tests.
- The 218 frozen scientific/library/asset entries and all 74 pinned D2.2 files
  matched their preservation identities. The five unrelated local paths retain
  their initial hashes, including the pre-existing `scenarios.css` edit. No model,
  fixture, image, GLB, dependency, deployment or source-data file changed.

React review retained server components for new presentation, static metadata,
stable list identities, native disclosures and the existing small client media
fallbacks. No new client store, effect, polling, WebGL or simulation was added.
Media reuse: desktop fly WebP 187,088 bytes; mobile fly WebP 64,818 bytes; Lab
capture 20,720 bytes, with existing attribution. No new asset files are required.

Next development automatically generated `web/AGENTS.md` and `web/CLAUDE.md` during
QA. Their framework origin was verified in Next's `generate-agent-files.js`; their
instructions and relevant bundled routing/metadata guides were read. Only these
new self-generated files were removed after stopping development, with copies
retained outside the repository. No pre-existing user file was removed.

Remaining limits: software-rendered Chromium only, no Safari/Firefox or hardware
GPU performance claim; external source availability is outside the page's control;
the existing recorded-artifact 409 is unchanged. Science itself does not depend on
either archive integrity or API availability. No staging, commit, push, deployment,
macOS or data-distribution work was performed.
