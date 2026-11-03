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
| 5 Home | Hero, status strip, explainer, gallery | Committed and pushed | see `git log` |
| 6 Lists and details | Scenarios and Experiments pages | Not started | |
| 7 3D frame and Neurons | `Viewport3D` and the Neurons pages | Not started | |
| 8 Cockpit and Lab | Layers, shared clock, responsive strategy, Lab overview | Not started | |
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
