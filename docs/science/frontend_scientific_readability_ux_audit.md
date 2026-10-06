# Phase 32 — Cross-Scenario Scientific Readability & UX Audit

## Outcome and scope

The product is scientifically honest and ready for a separately controlled visual
system redesign. It is not yet consistently easy to understand at first
inspection. The strongest existing features are explicit null-result copy,
model-space qualifiers, backend replay authority, working transport and secondary
provenance. The main weaknesses are result hierarchy, circuit visibility,
technical-label density and long mobile reading paths.

Decision: `FRONTEND_READY_FOR_VISUAL_SYSTEM_REDESIGN`.
Stage B: `NOT_RUN`. No CRITICAL/HIGH local semantic or blocking bug was located;
no frontend, transport, artifact or scientific-model correction was made.

[Machine-readable audit](frontend_scientific_readability_ux_audit.json):
`frontend_scientific_readability_audit_v1`, canonical Stage A ID
`3922ccf48edfcf10fc68b521573805f12a91a46909bdd044d8f704a5ee5c5157`.
This identity hashes the inner `audit` object using the repository's canonical
JSON convention. The findings were completed and frozen before any optional
correction; because Stage B did not run, the final audit has the same identity.

## Methodology and evidence limits

This is an **expert heuristic audit**, not a user study, comprehension-speed
measurement, usability score or comprehensive WCAG evaluation. The intended
reader is a technically literate newcomer without project documentation. Core
answers were assessed across the visible frontend without opening provenance;
first-fold visibility was evaluated separately. No fabricated numerical UX
score is used.

Source state: clean `main == origin/main` at
`c5ea8c35b757b7de5b70c78e86a6b4fba6b9cb40`; Phases 23–31 committed.
The audit records 18 implementation-file hashes, scientific document identities,
eight historical replay identities and both canonical/serialized hashes for all
five scenario payloads. Scientific values came from verified backend payloads,
not images or visual inference.

Real startup commands were used:

```sh
NEUROFLY_EXPERIMENT_ARTIFACT_ROOT=data/derived/experiments \
  uvicorn neurofly.http_api:create_app_from_env --factory --host 127.0.0.1 --port 8766
```

From `web`:

```sh
NEUROFLY_API_BASE_URL=http://127.0.0.1:8766 \
  npm run dev -- --hostname 127.0.0.1 --port 3005
```

Browser/verification skills guided scenario selection → actual API → canonical
replay → typed payload → rendered state checks. Desktop was 1440×1000 and mobile
390×844. Browser-controlled Chromium inspected all five desktop scenarios, the
library, both complex mobile scenarios, a looming mobile spot-check, expanded
provenance, loading and a genuine artifact-unavailable state. No scientific mock
data were used. No existing automated accessibility harness was found; keyboard,
native control labels, focus styles, dimensions, headings and overflow were
inspected without adding dependencies.

Home/End/PageUp scrubbing, play/pause, reset and native summary Enter controls
were exercised. Checks allowed React updates to complete before comparing DOM
values. A paused neural boundary remained stable. Final looming and course
boundaries matched authoritative values; course orientation retained its offset.

## Scientific authority gate

The v1 status, Phase 25 neural preregistration/artifact, Phase 26 network boundary,
Phase 28 evidence/orientation contract/artifact, Phase 29 observation contract,
Phase 30 preregistration/analysis/artifact and Phase 31 integration were verified
from repository state. Phase 30's authority loader validates referenced scientific
documents, including their correct inner-object or document-byte identities.

Phase 31 integration document byte hash:
`22e2a4b99e8324364f27529965a24989a5e6022b9e2249e904d0b341244441fa`.
Phase 30 artifact:
`f6ad13b9ba57d1ddb5e95cf91440c5b67f503a407f7330d4423ce7ab4340e581`.
The JSON audit contains the full authority chain and all five payload identities.

Before browser review, canonical CLI replay passed for Phases 7O, 8C, 13B,
corrected 16, 18, 25, 28 and 30. All five product playback payloads validated.
After the audit, the same authorities/payloads are checked again; no scientific
state or presentation copy was changed.

## Screenshot inventory

Fourteen PNG captures remain outside Git in the local Phase 32 audit temporary
directory. The JSON contains portable basenames, purpose, viewport, byte size
and SHA-256; it does not require captures to exist in a fresh checkout. These
are UX evidence, never scientific authority.

| Capture | State/evidence |
| --- | --- |
| `library-desktop.png` | All five experiment cards |
| `baseline-desktop.png` | Boundary 14; intentional neutral control |
| `baseline-loading.png` | Actual pending scientific replay |
| `looming-circuit-desktop.png` | Boundary zero and whole-run interpretation |
| `looming-circuit-desktop-final.png` | Boundary 14; subthreshold/stationary |
| `looming-world-desktop.png` | Boundary 400; exposure growth and null output |
| `looming-world-mobile.png` | Mobile looming spot-check, boundary zero |
| `horizontal-motion-desktop.png` | Boundary 200; pulse off, neural response persists |
| `horizontal-motion-mobile.png` | Same boundary, long stacked mobile layout |
| `course-control-desktop.png` | Boundary 500; residual orientation |
| `course-provenance-desktop.png` | Same boundary with provenance expanded |
| `course-control-mobile.png` | Expanded mobile course-control page |
| `course-mobile-fold.png` | Mobile first fold, residual caption |
| `scientific-playback-unavailable.png` | Real absent-artifact HTTP 503, no canvas |

## Six newcomer questions

Columns below correspond to: **look**—what is shown; **input**—what is applied;
**path**—which circuit/model is active; **result**—what happened; **body**—why
there is/is not body output; **limits**—what this does not demonstrate.
`CLEAR` does not mean immediately above the fold or empirically tested on users.
`PARTIALLY_CLEAR` means accurate information exists but needs more assembly or
is less evident at first inspection. No answer was classified misleading.

| Scenario | Look | Input | Path | Result | Body | Limits |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline Control | CLEAR | CLEAR | CLEAR | CLEAR | CLEAR | CLEAR |
| Looming Circuit Validation | CLEAR | CLEAR | PARTIALLY_CLEAR | CLEAR | CLEAR | CLEAR |
| Looming World Experiment | CLEAR | CLEAR | PARTIALLY_CLEAR | CLEAR | CLEAR | CLEAR |
| Horizontal Motion Neural Validation | CLEAR | CLEAR | CLEAR | PARTIALLY_CLEAR | CLEAR | CLEAR |
| Exploratory Course Control | CLEAR | PARTIALLY_CLEAR | CLEAR | PARTIALLY_CLEAR | CLEAR | CLEAR |

### Scenario Library

Roles distinguish control, 1.4 ms micro-window, 40 ms world experiment,
neural-only validation and exploratory closed loop. “Start here” is helpful.
However, long cards repeat descriptions, previews, explanations and caveats;
duration and body-output metadata are inconsistent. Four non-control cards share
the same visual emphasis. The fifth experiment is below two large rows. This is
a comparison/hierarchy issue, not an incorrect catalog or science claim.

### BASELINE_CONTROL

The quiet specimen, no-stimulus caption and “A control, not a broken simulation”
explanation make neutrality intentional. Source states are zero, DNp01 remains at
its -52 mV_eq resting model coordinate, with no spikes, actuation or displacement.
Neutral does not mean the membrane coordinate itself equals zero.

Viewport is dominant; result appears below transport and causal cards. The
disabled sensory stage is understandable, but “No sensory response yet” suggests
an unnecessary expectation of future control activity. Time/control status are
essential; repeated no-object, exposure, actuator and body-zero cells add little.
Provenance is properly collapsed. Shared transport keyboard behavior/focus works;
navigation focus risk remains. Baseline mobile was not separately audited.

### LOOMING_CIRCUIT_VALIDATION

The header correctly calls this a 1.4 ms circuit micro-window, not a biological
escape prediction. One object approaches; exposure increases 19→22 bodies.
Final DNp01 R is -51.933657842035174 mV_eq, L -52; spikes, actuation and movement
remain zero. The body stays stationary because the model produced no motor
command, not because the viewport failed.

The viewport, single sphere and specimen are clear. Five causal stages explain
world→sensory→DNp01→motor→body, but LC4/LPLC2 names are in details rather than the
primary narrative. Current subthreshold state and whole-run null outcome should
be easier to distinguish at boundary zero. Exact bilateral values/identities are
available in collapsed provenance. Keyboard boundary 14 and visible transport
focus were verified. Mobile was not separately reviewed for this micro-window.

### LOOMING_WORLD_EXPERIMENT

The separately preregistered 40 ms model-space experiment is distinct in copy,
although its scene resembles the micro-window. Exposure grows 19→26 bodies;
final DNp01 R is -48.733429620244685 mV_eq, L -52. The larger depolarization is
still subthreshold; zero motor/body output is canonical. The UI explicitly reports
completed horizon and stationary result without claiming physiological timing.

One authoritative sphere is present, not multiple historical objects. The fly
remains visible at final approach, although object/label placement, thin legs,
shadows and grid compete for detail. Causal clarity is good, but raw voltage does
not itself explain response growth; a concise current-result comparison would
help. Mobile has no observed horizontal overflow; labels and stacked panels are
small/long. Source identities, exact telemetry and preregistration remain secondary.

### HORIZONTAL_MOTION_NEURAL_VALIDATION

The selected right-side descriptor drives three right HS proxies and DNp15 R;
left proxies/target remain neutral. At the reviewed 20 ms boundary, the pulse is
off while DNp15 R still reads 0.746469 rounded, L 0. This is a continuing neural
response, not a zero-input failure. DNp15 states are continuous proxies; R−L is
diagnostic only. No body mapping or event semantics exist.

The two labelled stripe panels explicitly disclaim retinal calibration and
simulated body output. They dominate the viewport, but do not visualize the
selected eight-node/six-route motif. The result begins around desktop y=1340;
source cards around y=1953. Five telemetry cells leave an empty grid slot. Six
source identities and all active routes are preserved without opening provenance,
but far down the page. Native keyboard controls work. Mobile is overflow-free,
yet approximately 4339 px tall with six stacked source cards.

### EXPLORATORY_COURSE_CONTROL

The full frozen causal loop is explained correctly: external +0.001 eq kick,
completed view-motion observation, HS→DNp15 response and exploratory orientation
integration. Subsequent counter-motion and small reversals leave final orientation
+0.00033277101655776 eq; clipping is 0/500 intervals. This is not heading-error
control. No translation, physical yaw, force or recurrent/electrical network is
present.

The fixed reference is explicitly “not a goal direction.” Direct orientation
rendering is honestly tiny; the caption preserves the residual rather than
resetting it. Geometric change alone is difficult to perceive, so truthful
trend/annotation readouts would help without increasing any gain. Six causal
cards and a return glyph convey delayed feedback, but row/column reading takes
effort. “MARGINAL ORIENTATION MODE” is explanatory, not an error.

Current orientation is inside the viewport, while the full interpretation begins
around desktop y=1450 and mobile y=1844. Expanded mobile provenance produces a
page about 5640 px tall, without overflow. All six HS identities, both DNp15
targets, raw observation, exclusions and full authorities remain available.
Pause/reset/scrub and native provenance Enter were verified. There is no claim
that feedback reduces motion relative to the already stationary open-loop
control; it introduces subsequent counter-motion.

## Cross-scenario readiness matrix

`C` = CLEAR, `P` = PARTIALLY_CLEAR, `N` = NOT_AUDITED.
These are qualitative categories, not a numerical UX score. Claim safety means
no unqualified prohibited positive claim was located in the reviewed scenario UI;
it is not a completeness guarantee for all application copy.

| Scenario | Input | Circuit | Result | Body | Causal | Units | Playback | Provenance | Mobile | Claim safety |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline | C | C | C | C | C | P | C | P | N | C |
| Circuit looming | C | P | C | C | C | P | C | P | N | C |
| World looming | C | P | C | C | C | P | C | P | P | C |
| Horizontal neural | C | C | P | C | C | P | C | P | P | C |
| Course loop | P | C | P | C | P | P | C | P | P | C |

## Findings frozen for Phase 33

Severity: CRITICAL means incorrect/fake scientific state or misleading behavioral
claim; HIGH materially misleads or prevents understanding; MEDIUM is substantial
readability/usability friction; LOW is polish/consistency/minor accessibility.
No CRITICAL or HIGH finding was located. Every finding has a remedy and explicit
change layer in the JSON; no recommendation requires a scientific model change.

| ID | Scope | Severity / category | Current behavior; scientific risk and UX impact | Phase 33 remedy / change layer |
| --- | --- | --- | --- | --- |
| UX01 | All/library | MEDIUM / INFORMATION_HIERARCHY | Repeated card copy, uneven duration/scope metadata; accurate classes require lengthy comparison. | Compact consistent type/input/duration/output/result metadata. FRONTEND_ONLY. |
| UX02 | All | MEDIUM / INFORMATION_HIERARCHY | Result below controls/causal cards; correct null/subtle outcomes may be missed initially. | Current-result summary beside dominant viewport; distinguish current boundary/full run. FRONTEND_ONLY. |
| UX03 | Neural | MEDIUM / VISUALIZATION | Stripe-only viewport; motif assembled from distant cards, not false topology. | Identity-labelled six-route readout paired with descriptor; no active excluded edges. FRONTEND_ONLY. |
| UX04 | Course | MEDIUM / VISUALIZATION | Tiny honest rotation; counter-motion/residual unclear geometrically. Increasing gain would violate science. | Truthful model-space trend/annotation; preserve direct specimen orientation. FRONTEND_ONLY. |
| UX05 | All | MEDIUM / PLAYBACK | Boundary range lacks consistent phase markers; course text concatenates time/interval captions. Timing is correct but harder to interpret. | Authoritative phase annotations and distinct scientific/presentation time. FRONTEND_ONLY. |
| UX06 | All | MEDIUM / TELEMETRY | Repeated outcome/time cells, empty neural grid slot, drive/clipping combined; no incorrect values. | Essential primary readouts, paired targets, secondary disclosure. FRONTEND_ONLY. |
| UX07 | All | MEDIUM / TELEMETRY | Technical tokens/precision and hidden definitions increase unit-reading effort; physical misreading remains a risk despite qualifiers. | Plain-language labels plus exact tokens and model-space glossary. FRONTEND_ONLY. |
| UX08 | Active experiments | MEDIUM / SCIENTIFIC_SEMANTICS | Structure/assumption/result distinctions rely on prose; looming source names secondary. No count-efficacy claim found. | Common evidence grammar and named LC4/LPLC2 pathway. FRONTEND_ONLY. |
| UX09 | Complex mobile/world | MEDIUM / RESPONSIVE | Overflow-free but very long vertical stacks; delayed access to interpretation. | Result-first mobile reading path; group secondary details without deleting identities. FRONTEND_ONLY. |
| UX10 | All | MEDIUM / ACCESSIBILITY | Navigation focus is color-only; transport has an outline. No scientific change implicated. | Non-color-only link/control focus and logical tab order. FRONTEND_ONLY. |
| UX11 | All | LOW / ACCESSIBILITY | Controls measured 40 px high; some labels 9–13 px. Potential touch/low-vision friction, not a demonstrated conformance failure. | Review target areas and label legibility. FRONTEND_ONLY. |
| UX12 | All/provenance | LOW / PROVENANCE | Secondary provenance is correct but expanded hashes/machine terms are verbose. | Group structure/models/run identities and explain them; retain full hashes. FRONTEND_ONLY. |
| UX13 | Baseline/looming | LOW / SCIENTIFIC_COPY | Disabled baseline says “yet”; “genuine” model output is unexplained. No fake response occurs. | Control-neutral wording and consistent recorded-model language. FRONTEND_ONLY. |
| UX14 | Looming | LOW / VISUALIZATION | Static labels detach from the sphere; grid/shadows compete with thin legs. Scene guide limits physical interpretation. | Clear anchored labels and restrained guide/environment detail. FRONTEND_ONLY. |
| UX15 | Baseline/looming | MEDIUM / PERFORMANCE | Multi-second replay/restoration waits create uncertainty; not a production benchmark or numerical bug. | Honest persistent validation shell; separately profile authority-preserving adapter work before optimization. PRESENTATION_ADAPTER_ONLY. |
| UX16 | All/errors | MEDIUM / ERROR_STATE | Real 503 removes canvas; only course copy explicitly assures no synthetic fallback. | Consistent plain-language artifact error, no-fallback assurance, contextual retry/back. FRONTEND_ONLY. |
| UX17 | Specimen scenarios | LOW / ASSET_LIMITATION | Simplified body/legs/wings limit visual realism; labels correctly separate the asset from science. | Preserve asset disclaimer and separate any asset project from redesign; do not add mechanics. FRONTEND_ONLY. |

None of these findings qualifies for the permitted Phase 32 micro-fix stage.
There was no incremental cleanup, typography/color adjustment, new chart,
viewport change, asset replacement, schema migration or design-system work.

## Hierarchy, density, causal understanding and telemetry

Current common reading order: identity → viewport → playback → causal panels →
result → telemetry → provenance. Desired order: card → experiment identity/type
→ applied input → dominant visualization → current scientific result → causal
explanation → temporal controls → detailed telemetry → provenance.

All five desktop viewports are DOMINANT, around 570 px high. This strength should
be retained; it does not mean their causal/result content is equally effective.
Neural and course viewports need different patterns from looming worlds, not a
generic universal graph/dashboard. Long causal rows are readable but currently
weaker than the central visualization and can delay access to the outcome.

| Telemetry class | Recommended role/examples |
| --- | --- |
| ESSENTIAL | Scientific boundary/time; outcome/output scope; looming exposure and DNp01/subthreshold; R/L motion and DNp15/differential; course orientation/residual and clipping |
| USEFUL_SECONDARY | Distance, LC4/LPLC2 sums, exact bilateral DNp01, six HS states, yaw drive, relative view/raw observation, analysis explanation |
| PROVENANCE_ONLY | Full hashes, structural contact counts, authority phases and excluded context |
| REDUNDANT | Multiple separate stationary/no-command/time statements; constant zero positions as large KPI cells; empty neural grid slot |
| CONFUSING | Yaw-drive magnitude combined with clipping YES/NO in the same value line |

Neuron identities are preserved correctly. They should remain discoverable for
experts without requiring newcomers to decode body IDs first. Existing R/L text,
signed numbers and neutral-zero ruler labels do not depend solely on color.
Contact counts are provenance, never signal strength, neural gain or edge width.

Model-space terminology is largely consistent. Drift exists between “signed
proxy” and `dimensionless_signed_proxy`, “genuine” and recorded model outputs,
and preregistration spellings. Orientation-only output should not inherit generic
locomotion/body-movement wording. `mV_eq`, `world_eq`, `horizontal_motion_eq`,
`dnp15_state_eq`, `yaw_drive_eq`, `yaw_orientation_eq`, `relative_view_eq` must
remain explicit uncalibrated/model-space coordinates, not biological unit aliases.

The claim search covered rendered scenario copy and catalog/cockpit/viewport/
explanation/provenance source. No unqualified positive claim of calibrated
biology, real steering/yaw, navigation, decision-making, learning, consciousness,
complete network or physiological contact-count efficacy was located. Negated
terms such as “not biological voltage” are not false-positive violations.

## Fly, stimulus and semantic color

Asset limitations: simplified segmented body forms, rod-like legs, broad wings,
faceted eyes and limited anatomical detail. These are not body-model bugs.
Presentation limitations: leg/shadow overlap, dense ground grid, occasional
label detachment, object dominance near the end and small direct course rotation.
These must not be “fixed” by changing scientific trajectories or inventing
biomechanics. The asset is not MaleCNS morphology or validation evidence.

Looming has one solid authoritative sphere and a dashed approach guide; no
history-sphere clutter. Neural stripes have explicit L/R input labels and disclaim
retinal calibration; during recovery both panels look similar while neural state
persists. Course reference/body lines are labelled independently; they are not a
goal-heading sensor. A truthful residual/readout annotation would improve this
distinction without pretending to restore heading.

Amber/brown marks emphasis/subthreshold states; green/cyan marks active inputs,
responses and neutral product status; error panels are red-toned. Textual state
labels preserve semantic meaning. Navigation focus is the observed exception:
only a color change marks it. The marginal orientation panel is not styled as an
error, appropriately.

## Accessibility and responsive review

Transport buttons, labelled range and native summaries are keyboard reachable.
Home/End/PageUp update exact boundaries; summary Enter toggles; transport focus
has a 2 px outline. Main H1 and interpretation H2 exist, with named telemetry and
causal regions. Scientific values have textual alternatives to the 3D canvas.
No obvious text/background contrast blocker was located in the brief inspection;
no full contrast matrix or screen-reader study was conducted.

Navigation/back links deliberately remove outlines and change color only; this
is a focus robustness risk. Mobile control height is 40 px, and small scientific
labels merit review. These observations do not establish WCAG compliance or a
specific standards failure. No accessibility dependency was installed.

Mobile complex and looming views had no observed horizontal overflow, including
expanded course provenance. The issue is content priority: large viewport plus
long sequential causal/telemetry/source stacks push the result far down. The
redesign should preserve identity/input, meaningful viewport and current result
early, keep transport reachable, then progressively disclose details. Baseline
and micro-window mobile remain unreviewed rather than implicitly scored clear.

## Loading, errors and performance experience

Interactive Run explicitly says that canonical replay/provenance validation is
pending, disables its button and does not show a fake empty experiment. This
distinguishes loading from loaded baseline/null results. Restored canonical URLs
can wait several seconds before playback, so a persistent shell/loading pattern
belongs in the Phase 33 brief.

For the error audit, the real backend was temporarily restarted with
`NEUROFLY_SCENARIO_ARTIFACT_PATH` pointing to an intentionally absent audit-temp
child. Baseline returned actual typed HTTP 503. The canvas disappeared, the alert
identified replay-validation/source-artifact failure, and Retry/Run and back
navigation remained available. No file was moved/corrupted and no fake dataset
was returned. Restoring canonical configuration and retrying recovered real
playback. The course-specific no-fallback message is clearer than the older
generic wording; this is UX16, not evidence that older scenarios use fallback.

Local development logs: library shell 498 ms, baseline ready shell 358 ms;
neural restored playback 222 ms, course 660 ms, micro-window about 6.6–6.8 s,
world 16.4–17.2 s, baseline Run 13.7 s during concurrent audit requests. These
are contextual observations, not isolated production benchmarks or promises.
The shell timings are server request-completion observations, not measured
browser first-paint, time-to-interactive or newcomer comprehension times.
Brief playback/scrub inspection found no obvious sustained jank; no FPS metric
was collected. Provenance opens immediately but produces long content.

The known upstream `THREE.Clock` deprecation warning occurred in R3F views.
No browser runtime error/framework overlay was found. No Three.js/R3F migration
or optimization was undertaken.

## Prioritized Phase 33 redesign requirements

The JSON carries 18 requirements with screen scopes, acceptance criteria and
exact priority classification:

### MUST_PRESERVE_SCIENCE

Preserve backend authority, all five scenario identities/payloads, model-space
units, selected topology/exclusions and frozen scientific contracts. Keep
baseline intentional, looming subthreshold/stationary, neural-only without body
mapping/events, and course orientation-only with no heading sensor. Preserve
empirical structure versus exploratory dynamics versus derived model results.
No gains, clipping, timing, body behavior or artifacts may be tuned for design.

### MUST_IMPROVE

Promote current results alongside a dominant experiment viewport. Give the
library compact consistent class/duration/input/output/result metadata. Define
separate world, neural-only and course-loop viewport patterns. Make the selected
motif and delayed loop intelligible, with truthful tiny-motion/residual readouts.
Improve mobile priority, non-color-only focus, and consistent loading/error/no-
fallback messaging. These are presentation requirements, not new scientific
capabilities.

### SHOULD_IMPROVE

Unify plain-language unit labels/glossary; group/collapse provenance; annotate
authoritative stimulus/recovery/perturbation phases; compact primary telemetry
and keep secondary expert identities accessible. Preserve signs, neutral zero,
full hashes and appropriate exact precision.

### OPTIONAL_POLISH

Use the existing Stitch direction only as visual inspiration: immersive viewport,
restrained dark palette, readable instrumentation and minimal clutter. Mockup
behavior is not scientific authority. Do not couple asset replacement, new
effects/chart libraries or a new world taxonomy to the redesign.

### Screen-specific brief

| Screen | Redesign requirements |
| --- | --- |
| Scenario Library | Five comparable experiment classes with consistent duration, input, output/body scope and canonical result; preserve identifiers and limits. |
| Baseline cockpit | Dominant quiet specimen plus persistent intentional-neutral result; control-specific disabled wording, no fake activity. |
| Circuit looming cockpit | Named LC4/LPLC2→DNp01 path, 1.4 ms micro-window role, one object and subthreshold/stationary conclusion. |
| World looming cockpit | Distinguish preregistered 40 ms role; show exposure/depolarization growth and canonical zero motor/body output. |
| Horizontal neural cockpit | Motion descriptor paired with bounded identity motif and comparable bilateral continuous target readout; no body/event visuals. |
| Course-loop cockpit | Fixed reference, truthful orientation/readout, delayed causal return and residual-offset/marginal-mode explanation; no goal heading. |
| Expanded provenance | Group structure, assumptions, exclusions and run identities; preserve complete hashes without mobile overflow. |
| Scientific unavailable | Plain-language artifact error, explicit no synthetic fallback, contextual retry/back, no fabricated visualization. |
| Mobile complex layouts | Compact result-first journey with dominant viewport, reachable transport and expandable identity/provenance detail. |

Acceptance must protect all scientific invariants, existing typed variants and
control behavior. Lack of biological calibration, biomechanics, absolute-heading
sensing, DNp15 events or a complete recurrent/electrical network is not a UI bug
and must not be repaired through copy, animation or new scientific logic.

## Deterministic record and tests

The audit is metadata-only and has no runtime dependency. Focused tests cover
canonical identity/order independence, exactly five scenarios/six questions,
valid severities/categories/change layers, unique findings/remedies, screenshot
portability, pinned source authorities, no fake numerical scores/user-study or
WCAG claims, frozen Stage A/no Stage B, complete Phase 33 screen requirements
and material tamper identity changes.

Final verification: 12 focused audit tests and 1,218 full-suite Python tests
passed; one configured integration test was deselected. All 65 unchanged
frontend tests, Ruff check/format, frontend lint/typecheck/build and
`git diff --check` passed. Before/after logs for eight historical replays and
all five playback payload identities match exactly. The 323 tracked scientific/
frontend files were byte-checked against source HEAD with no differences.
Stage A ID remained unchanged. Screenshots stayed outside Git; no commit/push.
Phase 32 status: `PASS`.

Next bounded action: create the Phase 33 visual-system redesign specification
for the five scenario screens using this frozen audit and scientific invariants.
