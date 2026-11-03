# Redesign progress

Working log for the redesign described in `redesign-brief.md`. Decisions in the brief's
"Phase 0 decisions" section override the brief. Update this file with every phase commit.

**Branch:** `redesign/site-implementation`. One commit per phase, pushed after each, with a single
pull request to `main` opened at the end (not merged by the agent).

## Status

| Phase | Goal | State | Commit |
| --- | --- | --- | --- |
| 0 Baseline | Record the current site and check the diagnosis | Merged to `main` (PR #1, #2) | `5c91c26`, `dfc9582` |
| 1 Tokens | Colour, type, spacing, motion tokens; Geist; pre-paint theme | Merged to `main` (PR #3) | `db39c20` |
| 2 Honesty primitives | `KindBadge`, `Readout`, `ProvenanceLabel`, `Tooltip`, `StatePanel`, copy file | Merged to `main` (PR #4) | `1c14c53` |
| 3 Shell | Header, navigation, footer, status pill, skip link, route focus | Committed and pushed | `89acf27` |
| 4 Content pages | Science, Status and limits, Glossary | Committed and pushed | `79c1f8b` |
| 5 Home | Hero, status strip, explainer, gallery | Committed and pushed | `e690fdc` |
| 6 Lists and details | Scenarios and Experiments pages, plus the two detail pages | Committed and pushed (lists `937ab5b`; detail pages in the next commit, see "Phase 6b") | see `git log` |
| 7 3D frame and Neurons | `Viewport3D` and the Neurons pages | Committed and pushed (see `git log`) | see `git log` |
| 8 Cockpit and Lab | Layers, shared clock, responsive strategy, Lab overview | In progress: 8a Lab text in English done | |
| 9 Polish and removal | Transitions, audit, delete old CSS | Not started | |

Phases 0 to 2 were merged to `main` before the plan changed to a single branch. Each merge to
`main` triggered a Vercel **production** deployment (see "Deployments").

## Rules in force

- The frontend is read-only: no writes to the API or server data, no new simulation, no change to the
  API, simulation code or data contracts. **Narrow exception (decision 2):** only the Lab runs the
  model in the browser. Experiments, scenarios and the Cockpit play back stored data. Browser
  execution is not extended without the owner's approval.
- Never present model output as biological truth. Keep Structural, Model assumption, Model state,
  Not evaluated and Unavailable visibly distinct (brief sections 3 and 7).
- No invented scientific claims, citations, reasons for disabled features or data values. Missing
  facts are listed under "Needs owner input".
- Wording: "Circuit check", not "Validation"; "Integrity-checked", not "verified"; `mV_eq` with
  "model-equivalent, not measured", never a bare "mV"; "dimensionless" only for unitless values; no
  "digital organism" or "digital fly" in the interface; never call the Lab "Replay".
- Navigation: Scenarios, Neurons, Lab, Science. Home is the logo. Experiments is not in the main
  navigation and is labelled "Engineering test, not a scientific experiment".
- Old CSS is not deleted until its page has migrated (phase 9), apart from dead rules whose component
  was replaced.

## Constraints discovered

- **Frozen files.** `scripts/frozen-contribution.ts` pins the bytes of `web/package.json`,
  `web/package-lock.json` and `web/tsconfig.json`, and a list of runtime sources. Five tests fail if
  they change. **No phase can add a dependency or an npm script.** Phase 9 wants Playwright, axe and
  Stylelint in CI; plan to keep that tooling in a separate folder with its own `package.json`, or
  ask the owner to approve re-freezing the protocol.
- **CSS Modules in tests.** Node cannot import `.module.css`. Test files that reach components with
  CSS Modules register `tests/support/css-hooks.mjs` and import those modules dynamically.
- **Tests need the project's Python.** Run `PATH="$PWD/../.venv/bin:$PATH" npm test` from `web/`.
- **Local API data.** `data/derived/experiments` mixes artifact families, so the API answers
  `409 artifact_integrity_failure`. For browser checks the API was pointed at a scratch folder holding
  a copy of the one flat artifact. The API also rejects symlinked artifact folders. This is a backend
  follow-up and was not changed.
- **`gh` on this machine** needs `GODEBUG=netdns=cgo`.
- **Dark scope.** Pages not yet migrated stay dark in every theme. New chrome and components placed on
  them use `data-theme-scope="dark"`. A migrated page passes `tone="auto"` to the header and footer,
  which then follow the theme and show the theme switch.

## Phase 3: Shell (details)

- New `SiteHeader` (default, tool and over-stage variants), `SiteNavigation` (desktop links; mobile
  full-height sheet built on a native `<details>`, so it works without JavaScript, plus Escape, focus
  trap, scroll lock), `StatusPill`, `ThemeSwitch`, `SiteFooter`, `RouteFocus`. `AppHeader` and the
  Lab's own header were replaced, so every route has one header with a skip link as its first
  focusable element and one `<main id="main-content">`.
- The Cockpit and Lab use the 48 px tool bar. The Cockpit layout now derives from
  `--toolbar-height`.
- Status pill reads "Model · Not evaluated" and links to the Status page (`/science/status`, added in
  phase 4).
- The approved white emblem is inverted to black on light surfaces with a `--logo-filter` token.
- Dead header and footer CSS was removed from `product.css`, `globals.css`, `scenarios.css`,
  `lab.css` and `cockpit.css` (about 120 rules). `.status-dot` stays: two components use it.
- Tests changed for owner decisions (not weakened): primary link list; mobile menu markup; Experiments
  moved to the footer with the owner's label; Lab home link now comes from the shared header; the
  homepage import-tree guard now allows `useEffect` and `lib/theme` only in `SiteNavigation` and
  `RouteFocus`, and still forbids engines, WebGL, animation loops, fetching and unprefetched links.

Verified: type check, lint, build, 545 tests. Browser, 15 routes (including the themed preview) at
390 and 1440 px: skip link first, visible 2 px ring on every header stop, tab order correct, 13 of 13
phone menus open, trap focus, close on Escape and return focus; axe on header and footer 0 findings;
no horizontal overflow. Theme: system, stored choice before first paint, switch, reload. Route focus
moves to the `h1` after client navigation.

## Phase 4: Content pages (details)

- `/science` rebuilt as a long-form article on the tokens (light and dark), with a contents list that is
  sticky from 1024 px. New pages `/science/status` (capability, kind, reason, source) and
  `/science/glossary`. Shared `ArticleShell`, `StageFigure`, `Article.module.css`.
- **The reviewed Science copy was kept verbatim.** A test maps each `data-claim` group to a row in
  `docs/architecture/product_experience_v10_3b.md`. The 17 existing groups are unchanged. Four new
  groups were added, each with an evidence row: `scope` (two circuits, 313 and 8 bodies, not added),
  `kinds`, `open` (the eight unresolved questions from the v1 status) and `circuitcheck`. The Status
  table has a fifth, `capabilities`.
- All status and glossary copy lives in `src/content/science-copy.ts`. Every capability cites a
  repository report; a test checks that each cited file exists. Level C's reason is quoted from
  `docs/science/sensory_consumption_boundary.md`. The Lab row states what was compared (the browser
  neural update against the recorded Python run) and the tolerance (1e-8 per model-space quantity over
  eight seconds), from `docs/science/interactive_neural_locomotion_v2.md`.
- "Neural-only validation" is now "Neural-only circuit check" (`scenarioPresentation.ts`), with the
  explanation that a circuit check is not biological validation. The retired-term rule allows the
  word "validation" only in that explanation.
- Removed `science.css` and the Science layout, now unused. `ScienceArchitecture` keeps its text and
  moved to the module CSS.
- `themed-page.css` makes the page's backdrop, scrollbars and native controls follow the theme.
  Pages opt in with `data-themed-page`; it goes away with the legacy CSS in phase 9.
- Found and fixed in verification: legacy global `a`, `dt` and `dd` rules (no underline; dark-theme grey
  at 10 to 12 px) leaked into the new pages. New components now set these explicitly.

Verified: type check, lint, build, 556 tests. Browser, three pages x phone/desktop x light/dark: axe 0
violations, no horizontal overflow, no console errors, sticky contents, anchors land below the header,
tables keyboard-scrollable on phones, figures load. Lighthouse mobile: performance 99, accessibility
100, best practices 100, SEO 100 on all three (Science LCP 2.3 s, was 2.8 s). three.js is not loaded.
Contrast of the tokens is computed in `tests/tokens.test.ts`.

**Could not verify:** a scientific review of the new copy (see below), and screen-reader behaviour.
"Copy has been reviewed" in the phase 4 Done-when column is therefore **not met** and needs the owner.

## Phase 5: Home (details)

- New Home on the tokens (light and dark, theme switch shown): hero with the owner's headline and
  statement, a status strip directly under it (real text, the four owner-worded facts, kind glyphs), a
  three-layer explainer (Structural, Model assumption, Model state), a gallery of three canonical
  scenarios plus the Lab, and a "choose your path" section. It is static and makes no API request.
- The Lab card says "Runs in your browser" and "no muscle or wing physics" (decision 2) and never uses
  the word Replay.
- **LCP.** The root `app/loading.tsx` wrapped every route, so every page, including the static Home,
  first showed a "Loading scientific data" screen and kept its real content in a `hidden` div until a
  script swapped it in. That was the render delay. The root fallback was removed and moved to
  `morphology/loading.tsx` (the other data routes already had their own). Home's content is now in the
  initial HTML. Measured: real Chromium under slow 4G and 4x CPU throttling, six runs: LCP 0.82 s
  (p75 0.82 s); Lighthouse mobile (simulated): LCP 2.5 s, performance 98, accessibility 100. The
  simulated figure sits on the 2.5 s line; the old Home measured 2.1 s in the same simulation, with
  its own hero image, before the redesign changed the layout. Poster decoding is synchronous.
- Removed dead code: `SpecimenVisual`, `FeatureIcon`, `SectionHeading`, and 204 Home-only rules from
  `product.css` (21.9 KB to 4.2 KB). `discoveryCopy` moved to `scenarioPresentation.ts` (re-exported).
- `README.md` no longer says Home "explores the verified canonical scenario catalogue".
- Tests changed for the redesign (intent kept): the Home-specific copy and structure assertions, the
  link-resolution test (dynamic scenario routes), the Science navigation test (Home has no Science
  teaser now), the loading test (fallback now lives with the data routes), and the import-tree guard
  (allow-list: the theme helper and `scenarioPresentation`, plus type-only imports; engines, WebGL,
  animation loops and fetching are still forbidden).

Small choices (brief's recommendation or closest fit):

- The primary action reads "Watch the looming scenario", not the brief's "Watch a looming response".
  In the canonical looming scenarios the DNp01 model stays below its spike threshold and the body does
  not move, so "response" could read as the fly responding. It opens the scenario ready to play
  (`?replay=canonical`). Change it back if you prefer the brief's wording.
- No rotating circuit and no video loop: there is no asset of a real run, and a rotating 3D circuit
  needs three.js on Home. The hero uses the existing artistic specimen render, captioned as such.

Verified: type check, lint, build, 559 tests. Browser: Home at 390 and 1440 px in light and dark: axe 0,
no overflow, no console errors, no non-GET requests; Scenarios and Experiments lists (which share the
pruned CSS) unchanged and clean; keyboard path 28 of 28 routes. Lighthouse mobile (Home): performance 98,
accessibility 100, best practices 100, SEO 100.

## Phase 6: Lists and details (details)

**Done**

- `/scenarios` rebuilt: a shared `Card` per scenario (title is the one stretched link), a stimulus
  filter that lives in the URL (`?stimulus=`), a live result count, and each card keeps its limit and
  the API's scientific caveat under "What this does not show". `/experiments` rebuilt: a real
  `DataTable` (caption, scoped headers, `aria-sort`, stacked rows below 600 px), sorting
  (`?sort=&dir=`), search (`?q=`, a plain GET form), and a dismissible, restorable note ("No experiment
  has been evaluated against biological data yet"). The recorded run carries the owner's label,
  "Engineering test, not a scientific experiment". Filters, sorting and search work **with JavaScript
  off** (checked); the shared `PageShell` reveals streamed content under `<noscript>`.
- New shared pieces: `Card`, `DataTable`, `SegmentedLinks`, `ButtonLink`, `PageShell`, `NoticeBanner`,
  an `integrity-failure` state for `StatePanel`, and `src/lib/listing.ts` (pure filter/sort/search/URL
  logic with its own tests).
- **Not recorded, not invented.** The API's experiment summary has no scenario and no date, so those
  columns read "Not recorded". The scenario filter the brief asks for is omitted for the same reason.
- **Real 404s.** Unknown or malformed IDs now return HTTP 404 for `/experiments/[id]`,
  `/experiments/[id]/cockpit` and `/scenarios/[id]` (they returned 200 before). A layout above each
  detail route decides this before the page streams; the list pages moved into `(list)` route groups so
  their loading screens no longer wrap the detail routes (URLs are unchanged). The 404 pages show the
  unknown ID and a link back.
- Vocabulary on the detail pages: back links "← Scenarios" and "← Experiments"; "Replay canonical
  scenario" (decision 3); "Integrity-checked replay" (was "Replay verified"); "Evaluation: Not
  evaluated" (was "Empirical validation"); "Cockpit" (was "Scientific Cockpit"); scenario kinds read
  "...scenario", not "...experiment". The purpose sentence of the recorded run now says "No comparison
  with real fly data has been made".
- `tests/read-only.test.ts`: no source file sends a write request, and the only Server Action is
  `loadScenarioPlayback`, which performs a GET read (decision 3). The full browser network assertion is
  phase 9.
- Removed: `DiscoveryShell`, `ScenarioDiscovery`, `RecordedExperiments`, `ExperimentList`, `discovery.css`
  and the two list layouts.
- Real Chromium under slow 4G and 4x CPU throttling, six runs each: LCP 0.74 s (Experiments), 0.75 s
  (Scenarios). Lighthouse mobile: performance 99 and 96, accessibility 100 and 100. (Lighthouse's
  simulation puts Experiments LCP at 2.7 s; the throttled-browser figure above is what a browser sees.)
- Verified: type check, lint, build, 571 tests. Browser: seven page variants at 390 and 1440 px in light
  and dark: axe 0, no overflow, no console errors, no non-GET requests; filter, sort, search, note
  dismiss/restore and reload persistence; keyboard path 28 of 28 routes; the scenario Replay button
  works (its one POST is the named Server Action).

**Deferred from the brief's phase 6 detail pages (done later, see Phase 6b)**

- Scenario detail: the full-width stage with timeline below and the two-column "what happens / what to
  notice" and provenance area; **guided mode** (3 to 4 skippable captions tied to the timeline); the
  "See the published experiments for this scenario" next step. The page still uses the legacy dark
  playback UI (`scenarios.css`), with the vocabulary fixes above.
- Experiment detail: the brief's seven-section reading order (summary, setup with kind glyphs, results
  labelled "Model state", "What this does not show", Data with copy button). Still the legacy layout.
- `PlaybackWorkspace`, `TimelineInspector`, `CurrentResult` keep their legacy styling; their 3D parts
  move with phase 7, and the Cockpit with phase 8.
- Scenario cards have **no poster**: no scenario poster images exist in the repository.
- The `Timeline` component (`role="slider"`, `aria-valuetext`) is not built yet.

**Trade-offs and small choices**

- `loading.tsx` still exists for each list and detail route. The list-level loading screen is a plain
  status panel, not a skeleton that matches the final layout.
- Search matches name, artifact id, config id and model only (there is no scenario field).

## Phase 6b: Scenario and Experiment detail pages (details)

- **Experiment detail** (`components/experiment/ExperimentDetail.tsx`) now follows the brief's order:
  title and summary, status badge, scenario ("Not recorded"), "Open Cockpit"; Replay (the legacy 3D
  workspace in a dark stage frame until phase 7); Setup with kind glyphs (circuit = Structural,
  encoder and neuron model = Model assumption, body model = "Not recorded in this experiment summary");
  free parameters; Results, every value a `Readout` of kind Model state (counts "dimensionless", `mV_eq`,
  `ms`); "What this does not show"; Data (`ProvenanceLabel` card with a copy button, config and result
  IDs, checksum).
- Fixed a bare "mV" on "Peak membrane": it is now `mV_eq`.
- **Not added:** an API link in Data. The API base URL is a server-only setting, so no browser-safe link exists.
- **Scenario detail** is on `PageShell`. Stage stays in a dark frame (legacy playback), with a
  **guided tour** (3 captions: start, stored model state, end; skippable, restartable, stored only in
  this browser), a two-column "What happens / What to notice" and provenance card, and the next-step
  link. The link goes to all experiments: there is no scenario field to filter by.
- Guide captions are generic or reuse existing scenario text; no new scientific claims.
- Verified: tsc, lint, tests; axe 0 on 12 variants (3 pages x 2 widths x 2 themes).

## Phase 7: 3D frame and Neurons (details)

- **`Viewport3D`** (`components/ui/Viewport3D.tsx`): frame with title, kind label, reserved aspect ratio,
  legend, controls and a text description. States: loading, ready, degraded, no-webgl, context-lost,
  missing-data (the `paused` and `poster` states are not used yet). Pauses rendering offscreen and in a
  hidden tab (`frameloop="never"`), catches `webglcontextlost` and offers "Restart 3D view". Three tiers
  (`lib/viewportTier.ts`), dpr cap, and a frame-rate watch that drops a tier after 3 s under 30 fps
  and says so. The watch only runs when `playing` is set; the Neurons view renders on demand, so
  the tier drop is exercised in phase 8.
- **Neurons** (`/morphology`, `/morphology/[id]`) on `PageShell`: cards, a Structural badge, the intro
  "This is the reconstructed shape of real neurons, not a simulation", the stage in `Viewport3D`, Reset
  view, **Save image** (PNG with a provenance footer drawn into it), and Isolate selected body / Show all.
  Unknown IDs return a real 404 (`(list)` route group, layout, not-found with the ID).
  The legacy `.morphology-*` rules moved from `globals.css` to `styles/morphology.css`, tokenised. The
  compact Cockpit inspector still uses its old shell.
- **WebGL off:** the scenario stage and the experiment replay no longer render blank. `WebGLGate` shows
  "3D isn't available on this device" (the numbers below are the data alternative).
- Wording: "Verified CircuitContract" became "Integrity-checked". New `StatePanel` state `context-lost`.
- Not done: "toggle synapses" (the data has only schematic connectors, shown by the existing toggle);
  Web Worker parsing of large geometry (the geometry is small and built in the main thread); a poster
  state.
- Verified: tsc, lint, 577 tests (6 new), build. Playwright (`scratchpad` script, 11 checks): WebGL off
  message, canvas drawn, PNG download, context loss then restart, unknown ID 404, reduced motion tokens.
  axe 0 on the Neurons pages (light/dark, phone/desktop) and with WebGL off.

## Phase 8a: Lab text in English (details)

- All Portuguese interface text in the Lab components and in their non-frozen libraries was translated
  to English (about 250 strings in 20 files). The wording keeps the technical meaning; no claim was
  added or removed. `tests/lab-english.test.ts` fails if Portuguese text returns.
- Tests that asserted the old Portuguese error messages now assert the English ones.
- **Frozen files.** `experimentalLocomotion.ts`, `neuralLocomotion.ts` and `neuralSteeringComparison.ts`
  are pinned by `scripts/frozen-contribution.ts`, so their six Portuguese strings (two scenario labels
  and four error messages) were not edited. `lib/frozenText.ts` translates them when they are shown.
  Open item for the owner: if the freeze is lifted, move the English text into those files.
- The Lab also still shows legacy engineering vocabulary (for example `ENGINEERING_PROPULSION`); those
  are identifiers, not Portuguese, and are kept as written.

## Backend requests (not done here)

- Add the **scenario** and a **creation date** to the experiment summary, so the Experiments table can
  fill those two columns and offer the scenario filter. Until then they read "Not recorded".
- Handle a mixed artifact folder, and symlinked artifact folders (see Constraints).

## Handoff for phases 7 to 9

- **Phase 7 (3D frame and Neurons).** Build `Viewport3D` with the states in brief section 6 and migrate
  `/morphology` and `/morphology/[id]` first. Known issues to fix there: the Neurons pages still have
  the legacy chrome content; `/morphology/[id]` has 3 axe findings (`aria-prohibited-attr` on the
  canvas shell, `target-size` on source links); the scenario playback stage is **blank with WebGL off**
  (decision: fix in phase 7); WebGL-off and context-lost handling; the three detail tiers.
- **Phase 8 (Cockpit and Lab).** The Cockpit shows about 143 numbers at load against a target of 6 or
  fewer, and has axe `color-contrast` findings on future event rows and `target-size` on summaries.
  Translate the Lab's Portuguese strings to English (15 files, listed by searching for "A verificar",
  "indisponível", "incompatível"). The Lab must say "Runs in your browser", state the 1e-8 comparison
  (see `CAPABILITIES`), and tell users that saved runs stay in this browser. Add the Lab overview page
  at `/visual-lab` and point the header's Lab link there.
- **Phase 9 (polish).** Delete the remaining legacy CSS (`globals.css`, `cockpit.css`, `scenarios.css`,
  `lab.css`, `viewer.css`, most of `product.css`) and `themed-page.css`; remove the `noscript` reveal
  blocks that Home and Science still carry (root loading is gone, so they are no longer needed);
  convert `error.tsx` and the loading screens to the themed `StatePanel` pattern; make `tone="auto"`
  the default and remove the `data-theme-scope="dark"` pinning on the chrome. **Tooling:** Playwright,
  axe and Stylelint cannot go in `web/package.json` (frozen). Put them in a separate folder with its own
  `package.json` (for example `web-quality/`), or ask the owner to approve re-freezing. The audit
  scripts used in this project are in `docs/redesign-baseline/reports/audit-script.mjs`.
- **Open at the end:** the final report against section 11, the one pull request to `main`, and the
  items under "Needs owner input".

## Deployments

Every merge to `main` deploys to Vercel production (`vercel.json` enables it for `main`). The branch
`redesign/site-implementation` produces Preview deployments only.

| Commit on `main` | What | Production deployment |
| --- | --- | --- |
| `5c91c26` | PR #1: baseline docs (also carried the two local brand commits) | success |
| `dfc9582` | PR #2: morphology crash fix | success |
| `db39c20` | PR #3: tokens, Geist, theme script | success |
| `1c14c53` | PR #4: honesty primitives | success |

## Needs owner input

- **Detail pages.** Confirm that the deferred scenario and experiment detail redesign (guided captions,
  two-column layout, seven-section experiment page) should happen after phases 7 to 9, or in a
  dedicated pass.
- **Hero asset.** A poster image or short muted loop taken from a real run, labelled as model output
  (brief question 6). Until then the hero shows the artistic specimen render.
- **Roadmap.** The brief's plain-list roadmap (what is planned) is omitted: no plan is recorded in the
  repository. Please supply it, or say the section should stay out.
- **Scientific review of the phase 4 copy.** The reviewed Science text is unchanged. New wording to
  review: the `scope` paragraph, the `kinds` section, `open`, `circuitcheck`, the twelve capability
  reasons (paraphrased from the cited reports) and the glossary definitions.
- The Science page has **no "How to cite" block** and names **no author**, because neither the exact
  citation nor the author is in the repository. The MaleCNS link is the existing one.
- Exact **citation and data licence** wording for MaleCNS (brief question 10).
- A **named author or lab** for the Science page (question 12).
- The **reason for each unavailable capability** is taken from the repository where it exists (for
  example Level C: `docs/science/sensory_consumption_boundary.md`). Anything else is left out, not
  guessed.
- Whether the glossary relationships in brief section 3 match the backend model (question 11).
- Which **reference laptop** the 30 fps target is measured on (section 11).

## Brief recommendations relied on

Questions 3 (stage always dark), 4 (follow system, manual switch), 5 (keep URLs, change labels), 6
(poster, then a muted loop labelled as model output), 7 (English, one copy file), 8 (Geist), 9
(simplified replay on phones), as recommended in section 12, unless a Phase 0 decision says otherwise.

## Out of scope / backend follow-ups

- The API's handling of a mixed artifact folder, and its rejection of symlinks (see above).
- `README.md:419` still says Home explores the "verified canonical scenario catalogue". It is fixed in
  phase 5 together with the Home changes.
