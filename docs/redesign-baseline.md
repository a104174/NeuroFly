# Redesign baseline (phase 0)

Recorded 2026-11-03 on branch `redesign/phase-0-baseline`, from `main` at `2f7aa48`.
This file records the site before the redesign. It checks the diagnosis in
`docs/redesign-brief.md` section 1 against the code, and it answers open
questions 1 and 2 from the code. No application code was changed.

## How this was measured

- **Build and checks.** `npm run typecheck`, `npm run lint`, `npm test` and
  `npm run build` were run in `web/`.
- **Servers.** A production server (`next start`) ran against the local
  read-only FastAPI app (`uvicorn neurofly.http_api:create_app_from_env --factory`).
- **Local data workaround.** `data/derived/experiments` mixes the flat Phase 3B
  artifact with other artifact families, so `/api/v1/experiments` answers
  `409 artifact_integrity_failure` (the README describes this behaviour). The
  API also rejects symlinks. The audit therefore pointed
  `NEUROFLY_EXPERIMENT_ARTIFACT_ROOT` at a scratch folder holding a copy of
  `4481c8c2…` only. No repository data was changed.
- **Browser audit.** Playwright 1.52 with Chrome for Testing 149, using
  SwiftShader WebGL, ran each route at 390×844 and 1440×900, with
  `prefers-color-scheme` set to light and then dark. axe-core 4.10 used the WCAG
  2.0/2.1/2.2 A and AA tags. The script is in
  `redesign-baseline/reports/audit-script.mjs`.
- **WebGL off.** The 3D routes were rerun with `--disable-webgl --disable-3d-apis`.
- **Lighthouse.** Lighthouse 12.6 ran with the default mobile settings, on a
  local machine under WSL2. Performance numbers are relative and are not field
  data.

Artifacts committed with this file:

| Path | Contents |
| --- | --- |
| `redesign-baseline/reports/audit-script.mjs` | The Playwright script that produced the audit files below |
| `redesign-baseline/reports/page-audit*.json` | Title, h1, nav links, overflow, disabled controls, numeric-text count, console errors and non-GET requests, for each route, width and theme |
| `redesign-baseline/reports/axe.json` | axe violations for each route, width and theme |
| `redesign-baseline/reports/lighthouse-mobile.json` | Lighthouse scores and lab metrics |

## Checks at baseline

| Check | Result |
| --- | --- |
| Type check | Pass |
| Lint | Pass, with no warnings |
| Tests | **512 of 512 pass**, but only with `.venv/bin` on `PATH`. Under plain `npm test`, 5 tests fail with `spawnSync python ENOENT`, because the tests call `python` and this machine only has `python3` |
| Build | Pass, 14 app routes |
| Routes | All 14 routes, plus not-found, resolve (see the defects below) |

Screenshots (every route at 390 px and 1440 px, and the 3D routes with WebGL off, about 5 MB)
were taken but are **not committed**. They stay on the author's machine. The audit JSON files
name each screenshot in a `shot` field, and the evidence column below refers to them as
"local screenshots". Regenerate them with `audit-script.mjs`.

### Route inventory

| Route | Title | h1 | Header |
| --- | --- | --- | --- |
| `/` | NeuroFly — A digital fly. A new way to explore behaviour. | A digital fly. A new way to explore behaviour. | `SiteHeader` |
| `/scenarios` | Explore · NeuroFly | Explore the possibilities. | `SiteHeader` |
| `/scenarios/[id]` | NeuroFly · Experiment Browser (root default) | Scenario API title, such as "Looming Circuit Validation" | `AppHeader` |
| `/experiments` | Recorded experiments · NeuroFly | Return to the evidence. | `SiteHeader`, with no current item |
| `/experiments/[id]` | Root default | `looming_giant_fiber_v1` | `AppHeader` |
| `/experiments/[id]/cockpit` | Root default | Persisted experiment looming_giant_fiber_v1 | `AppHeader` |
| `/morphology` | Root default | Raw bounded morphology samples | `AppHeader` |
| `/morphology/[id]` | Root default | MaleCNS morphology inspection | `AppHeader` |
| `/visual-lab/arena` | Explore · NeuroFly Lab | Explore. | Own Lab header |
| `/visual-lab/arena/research` | Laboratory research tools · NeuroFly | Laboratory research tools. | `AppHeader` |
| `/visual-lab/fly` | Fly · Visual Lab · NeuroFly | A closer look. | `AppHeader` |
| `/science` | Science & Project · NeuroFly | The science behind a digital organism. | `SiteHeader` |
| Not found | Root default | That artifact is unavailable. | `AppHeader` |

Every page has exactly one visible `h1` and one `main`. The site has **three
different headers**, with different link sets. Pages that use `AppHeader` have
no skip link, so the first focusable element is the logo.

### Accessibility (axe, serious or critical)

These results are the same in both themes. Every other route has 0 violations.

| Route | Width | Violations |
| --- | --- | --- |
| `/experiments/[id]` | Both | `aria-prohibited-attr` ×1 (`.playback-canvas-shell`) |
| `/experiments/[id]/cockpit` | Desktop | `aria-prohibited-attr` ×1, `color-contrast` ×8 (future event rows) |
| `/experiments/[id]/cockpit` | Phone | The same, plus `target-size` ×2 (`summary` elements) |
| `/morphology/a3f0…` (six-body) | Both | `aria-prohibited-attr` ×1, `target-size` ×6 (source links) |

### Lighthouse, mobile

| Route | Perf | A11y | Best practice | SEO | LCP | TBT | CLS |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/` | 99 | 100 | 100 | 100 | 2.1 s | 20 ms | 0 |
| `/scenarios` | 98 | 100 | 100 | 100 | 2.4 s | 20 ms | 0 |
| `/experiments` | 99 | 100 | 100 | 100 | 2.2 s | 60 ms | 0 |
| `/science` | 96 | 100 | 100 | 100 | **2.8 s** | 20 ms | 0 |
| `/morphology` | 99 | 100 | 100 | 100 | 2.2 s | 30 ms | 0 |
| `/visual-lab/arena` | 59 | 100 | 100 | 100 | 3.4 s | 163 s* | 0 |
| Cockpit | 65 | 89 | 96 | 100 | 5.2 s | 460 ms | 0.001 |

\* The Lab's TBT comes from continuous rendering in software WebGL
(SwiftShader). It is not representative of a GPU device. Re-measure on the
reference laptop named in section 11.

three.js was **not** loaded on `/`, `/scenarios`, `/experiments`, `/science`
or `/morphology`: no chunk on those pages contains `WebGLRenderer`.

No route overflows horizontally at 390 px or 1440 px.

### Read-only check

- **Page loads.** On every route, page loads made only `GET` requests.
- **One `POST`.** Clicking **"Run canonical preset"** on `/scenarios/[id]`
  sends **one `POST` to the Next server**. This is the Server Action
  `loadScenarioPlayback` in `web/src/app/scenarios/actions.ts`. It only
  performs a `GET /api/v1/scenarios/{id}/playback`, but under the section 11
  criterion as written, "Only GET, HEAD or OPTIONS", it fails.
- **API.** The FastAPI app registers only `GET` routes.

## Section 1 diagnosis, checked

| # | Brief's claim | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | The homepage describes "verified" scenarios | **Not as stated, but the risk is real.** No page says "verified scenarios". The phrase comes from `README.md:419` ("explores the verified canonical scenario catalogue"), which is out of date: Home no longer lists scenarios. The scientifically loaded word in the UI is **"Validation"** (see question 1) | Scenario API titles "Looming Circuit Validation" and "Horizontal Motion Neural Validation"; the label "Neural-only validation"; `CurrentResult` shows a **"Replay verified"** badge; the scenario button reads "Preparing validated replay…"; the Cockpit shows "VALIDATION · NOT EVALUATED"; "verified" also appears about 15 times in Lab copy ("Verified MaleCNS morphology", "Vertical flight verification", "Landing verified") |
| 2 | The "Experiments" nav item points to `/scenarios` | **Confirmed, and worse.** `SiteHeader` has Home, Lab, "Experiments" → `/scenarios` and Science. `AppHeader` has Experiments → `/experiments`, Scenarios, Morphology and Visual Lab → `/visual-lab/fly`. So the same label leads to two different pages depending on the header. The Lab header's "Research archive" also links to `/scenarios`. `/experiments` appears only in the footer, as "Recorded experiments". `/morphology` is missing from `SiteHeader` | `web/src/components/site/siteContent.ts:8`, `web/src/components/AppHeader.tsx:15-18`, `web/src/app/visual-lab/arena/page.tsx` |
| 3 | Inconsistent use of experiment, scenario and artifact | **Confirmed.** `/scenarios` is titled "Explore", its cards say "View experiment" and it calls itself "Five controlled experiments". The scenario back link reads "← All experiments". The not-found page says "That artifact is unavailable". The scenario button says "Run" although it retrieves a stored replay | `ScenarioDiscovery.tsx`, `scenarios/[scenarioId]/page.tsx`, `not-found.tsx`, `ScenarioCockpit.tsx:81` |
| 4 | Model state and structural data look alike | **Partly confirmed.** Many panels already label values ("SIMULATED", "structural", "Concept diagram · not measured data"), but with ad hoc words and colours rather than one system. Model values carry **`mV_eq`** and, in four places, a bare **`mV`** (`ScientificCockpit.tsx:49`, `ExperimentSummaryView.tsx:73`, `MorphologyInspector.tsx:461`). This conflicts with the brief's rule that model state is dimensionless (see conflict C3) | Local screenshots of the Cockpit and scenario replay pages |
| 5 | No quick answer to "what am I looking at?" | **Confirmed by inspection.** The hero says "A digital fly. A new way to explore behaviour.", with an artistic fly render and no scope statement. The project's own status file forbids the claim "Living fly or digital organism". The five-second user test was not run | `docs/science/neurofly_v1_scientific_status.json` → `claims.forbidden`; 14 uses of "digital fly" or "digital organism" in `web/src` |
| 6 | Cockpit shows too many values at once | **Confirmed.** 143 visible numeric text nodes at load (a proxy count), against a target of 6 or fewer. At 390 px the Cockpit stacks every panel into a 2,582 px page, and the `AppHeader` nav wraps and overlaps the "Standalone playback" link | `page-audit.json`, a local phone screenshot |
| 7 | 3D lacks loading and empty explanations | **Mixed.** Cockpit, Lab, Fly viewer and Morphology show clear WebGL-off messages. **Scenario playback shows a blank stage with no message.** The DNp01-only morphology artifact **crashes** into the generic route error (see defects) | Local screenshots with WebGL off |
| 8 | Disabled capabilities are unexplained, for example Level C | **Not applicable as stated.** Level C does not appear in the frontend at all. Its reason is documented in `docs/science/sensory_consumption_boundary.md:113`. At load, only one disabled control was found (on `/visual-lab/arena/research`, with no accessible name). There are 77 `disabled=` props in components, mostly state-dependent playback buttons | `page-audit.json` |
| 9 | No phone strategy for the Cockpit and Lab | **Confirmed for the Cockpit**: everything is stacked. The Lab reflows reasonably. Not tested on a real Android device | Screenshots |
| 10 | Eight CSS files with an Arial default | **Confirmed.** There are 8 files and 1,794 lines, but the lines are long. About 352 hex colours and 25 `rgb[a]` values sit outside any token file. Arial is set in `globals.css`, `product.css` and `lab.css`. There is **no light theme at all**: no `prefers-color-scheme` anywhere, so light and dark render identically. Some text is 9–10 px | `web/src/app/**/*.css` |

### Found during the audit, not in the brief

- **Defect: the DNp01-only morphology page crashes.** `/morphology/719426f0…`
  throws "Connectivity endpoint is outside the loaded morphology sample"
  (`web/src/lib/connectivityView.ts:48`) and shows the generic error page. The
  shared six-body connectivity projection has edges to bodies that this
  2-body artifact does not include. The artifact is linked from `/morphology`.
- **Unknown IDs return HTTP 200.** A well-formed unknown ID renders "That
  artifact is unavailable" with status 200, because streaming starts before
  `notFound()`. A malformed ID (`abc123`) shows "This experiment could not be
  read", also with 200.
- **Portuguese UI strings in an English site.** They appear in 15 Lab and
  research files, for example "A verificar a simulação Python…" and "Replay
  neural incompatível ou corrompido…".
- **The only recorded experiment is a UI smoke reference.** It is
  `ui_smoke_phase2f_reference_v1`, classified as
  `ENGINEERING_UI_SMOKE_REFERENCE` (`docs/recorded_experiments_reference_v1.json`).
  The Experiments section, which the brief makes a primary nav item, currently
  lists one engineering run.
- **Root `loading.tsx` uses the old `AppHeader` shell.** Every route streams
  inside a `hidden` wrapper, and Home and Science carry `<noscript>` CSS
  workarounds for this.
- **The project has two circuits, not one.** The looming circuit is LC4/LPLC2
  → DNp01 (311 sensory + 2 = 313 bodies, which matches the brief). The Lab,
  Explore, course control and the horizontal-motion scenario use **HS → DNp15**
  (6 + 2 bodies). The brief's status strip, "313 bodies", describes only the
  first.

## Open questions 1 and 2, investigated

### Question 1: what does "verified" or "validation" mean?

There are three different senses in the code. None of them is biological
validation:

1. **"Validation" in scenario names** means computational circuit validation:
   a preregistered, deterministic check that the model executes through the
   identity-resolved MaleCNS motif. `docs/science/closed_loop_looming_scenario.md`
   calls it "exploratory model-space circuit validation, not physiological
   visual registration, biological escape or calibrated mechanics".
   `docs/science/hs_dnp15_neural_validation.md` calls it "deterministic,
   identity-resolved propagation… not steering, navigation… or complete DNp15
   physiology". The v1 status record says: "Stable for reproducibility; not
   biologically validated."
2. **"Verified" on data** means integrity checks. SHA-256 and record-count
   checks run on artifacts, morphology bundles and assets, both in the client
   parsers and in the API.
3. **"Replay verified"** means the stored canonical replay passed those
   integrity checks and its schema checks.

`validation_status` is always `NOT_EVALUATED`. The client rejects any other
value (`web/src/lib/neuroflyClient.ts:545`).

Proposed answer: display "validation" in sense 1 as **"Circuit check"** or
**"Reproducible circuit run"**, and "verified" in senses 2 and 3 as
**"Integrity-checked"**. Keep the scenario IDs and API titles unchanged, and
relabel only in the frontend, as `discoveryCopy` already does.

### Question 2: do Lab controls replay data, request data or compute?

**They compute in the browser.** This conflicts with the brief's assumption.

- **`/visual-lab/arena` (Explore).** `LiveGroundSession` and
  `InteractiveNeuralEngine` (`web/src/lib/interactiveNeuralLocomotion.ts`) are a
  "fixed-step browser implementation of the pinned Python v1 model". They
  integrate the HS/DNp15 neural model at 200 substeps per 20 ms body step, plus
  engineering locomotion, live. Parity with the recorded Python artifact is
  checked to 1e-8. The source authority is the static
  `public/experiments/experimental_locomotion_v1.json`, which is hash-pinned.
  No backend API is called.
- **Flight modes** (vertical, reactive, mixed). These are deterministic
  engineering simulations in TypeScript, in the browser.
- **Research tools.** These also compute in the browser. They **write to browser
  storage**: `localStorage` for the flight library and neural flight, and
  IndexedDB for the session library. They also import and export JSON files.
  Nothing writes to the API.
- **Scenario pages** do not compute. They fetch stored canonical replays
  through the Server Action.

Proposed answer: the redesign must not change these engines. Calling the Lab
"Replay" would be false. It should be labelled for what it is, for example
"Runs in your browser: a reimplementation of the pinned model, checked
against the recorded Python run". **This needs the owner's decision.**

## Conflicts between the brief and the code

| # | Conflict | Recommendation |
| --- | --- | --- |
| C1 | The brief and the hard rules assume the frontend never runs the simulation, but the Lab already does (see question 2) | Leave the engines untouched. Treat "read-only" as "no writes to the API or server data". Label the Lab honestly as browser computation |
| C2 | Section 11 requires only `GET`, `HEAD` or `OPTIONS`, but the scenario replay uses a Server Action (`POST` to Next) that only reads | Scope the CI assertion to requests to the API origin, and allow-list this action. Optionally, replace it later with a `GET` route handler. That is a frontend-only change, but it is out of scope until approved |
| C3 | The brief says model state is "dimensionless" and that no "mV" may appear, but DNp01 values are stored in **`mV_eq`**, a model-equivalent unit, and 4 places show a bare `mV` | Show "mV_eq (model-equivalent, not measured)" with the Model state kind, and replace bare "mV" with "mV_eq". Do not call these values dimensionless |
| C4 | The brief's circuit facts (313 bodies, LC4/LPLC2/DNp01) cover only the looming circuit. The Lab and two scenarios use HS → DNp15 | Make the status strip cover both, or name the circuit for each page. The copy needs the owner's input |
| C5 | The brief's proposed Home statement ("building a digital model of a fruit fly's nervous system and movement") and the current copy ("digital fly", "digital organism") are close to the project's own forbidden claims | Use the allowed vocabulary from `neurofly_v1_scientific_status.json`, such as "connectome-based selected-circuit simulation". The final wording needs the owner's input |
| C6 | The brief says "Level C" is a disabled control to explain, but it is not in the UI | Mention it only on the Status and limits page, citing `sensory_consumption_boundary.md` |
| C7 | The brief assumes "Experiments" is a rich, primary section, but only one engineering smoke run exists | Keep it in the nav, as the brief proposes, but give it an honest empty-ish framing. Owner's call |

## Resolved on 2026-11-03

The owner answered the questions above. The decisions are recorded in the
"Phase 0 decisions" section of `redesign-brief.md` and override the brief.

## Backend follow-ups (out of scope for the frontend redesign)

- `/api/v1/experiments` answers `409 artifact_integrity_failure` when
  `NEUROFLY_EXPERIMENT_ARTIFACT_ROOT` points at `data/derived/experiments` as
  it is checked out, because that folder mixes the flat Phase 3B artifact with
  other artifact families. The README's Cockpit instructions use that path. The
  API's handling of mixed folders is unchanged and needs a backend decision.
- The API rejects symlinked artifact folders (`unsafe_artifact_path`).
