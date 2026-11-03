# NeuroFly Website Redesign Brief

Nov 3, 2026 · @Hélder

Redesign NeuroFly as a calm product site with one dark 3D stage, where every number says what kind of number it is. The status of the science is part of the interface, not a footnote.

**Three decisions carry the brief:**

- **One vocabulary, one path.** A scenario is a setup, a run is one execution, and an experiment is a published run. Navigation follows those words.
- **Three layers of depth.** Each screen opens at *Overview*, then *Detail*, then *Raw*. Depth is chosen by the reader and kept in the URL.
- **A provenance grammar.** Each value carries a kind: Structural, Model assumption, Model state, Not evaluated or Unavailable. Each kind has its own label and glyph, so none depends on colour.

**Basis and limits**

- This brief is based on your written description only. I did not inspect the code or the running site, so section 1 is inference to verify.
- Anything not stated in your description is marked **Assumption**.
- Contrast ratios were computed with the WCAG 2.x formula. They were not measured in a browser.
- Several lines of your request were cut off at the right edge. Affected items are the morphology route, brand description, known issues, and the sections on 30-second orientation, Home status, Cockpit disclosure, data-unavailable states, reduced motion and open questions. I completed them from context, so check those against your original.

## 1. Diagnosis

The largest risk is a visitor leaving with a false belief about the science, so honesty problems outrank polish problems. All ten items are inferred from your description. Verify each one with the check in the last column before fixing it.

| # | Problem | Why it matters | How to verify |
| --- | --- | --- | --- |
| 1 | The homepage is described as exploring "verified" scenarios, while experiments are `NOT_EVALUATED`. | A lay reader takes "verified" to mean biologically proven. This is the most direct conflict with the integrity rule. | Search the UI copy for "verified", and find out what is actually being verified. |
| 2 | The "Experiments" nav item points to `/scenarios`, while `/experiments` is a separate route that is not in the nav. | The label promises one thing and delivers another, and completed experiments lose their main entry. | Click every nav item and compare label, URL and page title. |
| 3 | "Experiment", "scenario" and "artifact" are used inconsistently. | Readers cannot tell whether two pages show the same thing, and experts cannot cite precisely. | List every use of the three words in `src/`. |
| 4 | Model state and structural data can look the same in dense panels. | Synaptic contact counts could be read as gains, and dimensionless values as measurements. | Screenshot every numeric readout. Can you name its kind without hovering? |
| 5 | There is no quick answer to "what am I looking at?". | A first-time visitor sees a 3D fly and may assume a whole-brain simulation, not a 313-body circuit. | Five-second test with three people who do not know the project. |
| 6 | The Cockpit shows many telemetry values at the same visual level. | Nothing tells the reader where to look, and experts lose the signal too. | Count values visible at load. The target is 6 or fewer at Overview. |
| 7 | 3D views lack clear loading and empty explanations. | A blank canvas cannot be told apart from a failed fetch, a missing optional source or a slow GPU. | Throttle the network, block each API route, and disable WebGL. |
| 8 | Disabled capabilities such as Level C may read as bugs, or may not be explained at all. | Deliberate scientific restraint is a strength, but it looks like breakage if unexplained. | List every disabled control and check that it states its reason. |
| 9 | Phones have no stated strategy for the Cockpit and labs. | A squeezed multi-panel view is unusable, and mobile GPUs may crash on heavy scenes. | Test at 390 px on a mid-range Android device. |
| 10 | Styling is split across eight CSS files with an Arial default. | Fixes drift between pages, and the current type is a poor fit for dense numbers. | Count hard-coded colours and duplicate selectors outside the token file. |

## 2. Information architecture

The header gets five items, each matching what its page contains. This fixes the mislabelled Experiments link and brings Neurons into the nav, without removing any route.

&#91;embedded content: Proposed sitemap · five sections under Home\]

Experiments is reached from Scenarios as well as from the nav, because each experiment is a published run of a scenario.

### Route map

| Section | Page | Route | Change |
| --- | --- | --- | --- |
| Home | Home | `/` | Redesigned |
| Scenarios | List and detail | `/scenarios`, `/scenarios/[scenarioId]` | Nav label changes from "Experiments" to "Scenarios" |
| Experiments | List, detail, Cockpit | `/experiments`, `/experiments/[artifactId]`, `.../cockpit` | Added to the nav |
| Neurons | List and inspector | `/morphology`, `/morphology/[artifactId]` | Added to the nav. The public label becomes "Neurons" |
| Lab | Overview | `/visual-lab` | **New page** |
| Lab | Arena, research, fly | `/visual-lab/arena`, `.../arena/research`, `/visual-lab/fly` | Routes unchanged |
| Science | Overview | `/science` | Redesigned |
| Science | Status and limits | `/science/status` | **New page**, built from the capability list in section 7 |
| Science | Glossary | `/science/glossary` | **New page**, built from section 3 |

The footer holds the docs repository, MaleCNS data source, status link and data release version.

### First-time visitor: under 30 seconds

1. **0 to 5 s.** The hero states what NeuroFly is, while a looping preview of the looming scenario plays.
2. **5 to 15 s.** The status strip gives the scope: 313 bodies, not a whole brain, and not validated against biology.
3. **15 to 30 s.** "Watch a fly respond to a looming object" opens one scenario in guided playback. It needs no setup and uses no jargon before the first frame.

### Expert: three clicks or fewer

- **Cockpit:** Home, then Experiments, then the row's "Open Cockpit" action. Two clicks from any page.
- **Data:** each experiment detail page has a Data section with the identifier, source release and API links.
- **Shareable state:** the Cockpit URL carries `?t=`, `?layer=` and `?body=`, so a precise view can be cited.
- **Later, optional:** a `Cmd/Ctrl+K` jump menu across scenarios, experiments and neurons, in phase 9.

### Navigation behaviour

- **Desktop, 1024 px and up:** logo left, five links centred, status pill and theme switch right.
- **Below 1024 px:** logo, status pill and a menu button that opens a full-height sheet.
- **Current page:** `aria-current="page"` plus a 2 px underline, so the state does not depend on colour.
- **Cockpit and Lab:** the header collapses to a 48 px tool bar with the logo, a back link and the page title.

## 3. Vocabulary

Use one word for each concept, everywhere: nav, headings, API labels and error messages. **Assumption:** the relationship between scenario, run, experiment and artifact below is my reading of your description, so correct it if the backend models them differently.

### Core objects

| Term | Plain-language meaning | Use it for | Do not use it for |
| --- | --- | --- | --- |
| **Scenario** | A defined situation: which stimulus, which circuit, which settings. Like a recipe. | The catalogue and playback pages | A finished result |
| **Run** | One execution of a scenario. The simulation is deterministic, so the same inputs should give the same run. | Timeline, playback, "this run" | A real fly trial |
| **Experiment** | A completed run published here with its status and provenance. | The list, detail page and Cockpit | Any scientific claim of validation |
| **Artifact** | The stored data package behind an experiment or neuron. | Provenance panels, IDs and API links only | Page titles or navigation |
| **Cockpit** | The synchronised view of world, connectome and telemetry for one experiment. | The tool's name. Drop "Scientific" from the label | Live control of a simulation |

### Data kinds

| Term | Plain-language meaning | Example |
| --- | --- | --- |
| **Structural** | Taken from the MaleCNS connectome, which maps the physical wiring. | Neuron morphology, connections |
| **Contact count** | How many synaptic contacts were mapped between two neurons. It does not measure signal strength. | Connectome edge weight |
| **Model assumption** | A value or rule chosen to make the model work, not measured from the fly. | Gain settings, integrate-and-fire parameters |
| **Model state** | A dimensionless number the simulation produces. It is not a biological measurement. | Membrane-like state, telemetry values |
| **Not evaluated** | Nobody has compared this result with real fly data yet. It is not a failure. | All current experiments |
| **Unavailable** | A capability that is deliberately off or not yet built. | Level C visual-angle mapping |

### Science terms for newcomers

| Term | Plain-language meaning |
| --- | --- |
| **Connectome** | A map of a nervous system's neurons and their connections. |
| **Body** | One reconstructed neuron in the connectome. NeuroFly's selected circuit has 313. |
| **Morphology** | The 3D shape of a neuron. |
| **LC4, LPLC2** | Visual projection neurons. This circuit has 126 LC4 and 185 LPLC2. |
| **DNp01** | A descending neuron, which carries signals from the brain towards the body. This circuit has 2. |
| **Looming** | A visual stimulus in which an object appears to approach. |
| **Leaky integrate-and-fire** | A simple neuron model: input accumulates, leaks away over time, and triggers a spike at a threshold. |
| **Kinematic** | Movement is computed from rules, without simulating muscles or wing physics. |

### Retire these words

| Avoid | Replace with | Reason |
| --- | --- | --- |
| Verified (for scenarios) | "Reproducible" or "Checked by project tests", if that is what it means | Reads as biological proof. See question 1 in section 12 |
| Weight, strength (for edges) | Contact count | Implies physiological gain |
| Activity, firing rate (without a qualifier) | Model activity, model spikes | Implies a recording |
| Simulated brain, digital fly (present tense) | Selected circuit, model | Overstates the current scope |
| Disabled, error (for planned features) | Not available yet | Reads as a fault |
| Bio-accurate, realistic, lifelike | Remove | No validation supports these |

Machine values such as `NOT_EVALUATED` and `MODEL_ASSUMPTION` appear only in the Raw layer. Everywhere else they display their human label.

## 4. Visual system

Neutral surfaces, one cobalt accent and one reserved hue per data kind give the site its restraint. Teal leaves the interface, because here colour should mean something scientific rather than decorate.

### Palette

**Why this palette:** near-black and soft white read as a product stage. Cobalt is reserved for actions, so it is never confused with a data kind. The semantic hues stay muted enough that a page of badges does not look like an alarm. All text pairs below pass AA (4.5:1); the lowest is 4.71:1.

**Surfaces and lines**

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--color-canvas` | `#F7F8F7` | `#0A0C0D` | Page background |
| `--color-surface` | `#FFFFFF` | `#131618` | Cards, panels |
| `--color-raised` | `#EEF0EF` | `#1C2023` | Hover, wells, segmented controls |
| `--color-hairline` | `#DDE1E0` | `#2A2F32` | Decorative dividers only (about 1.3:1) |
| `--color-border-control` | `#7A8387` | `#7A8387` | Input and control borders, 3:1 or more on all surfaces |

**Text and semantic colours, with contrast ratios**

| Token | Light hex | Light on canvas / surface / raised | Dark hex | Dark on canvas / surface / raised |
| --- | --- | --- | --- | --- |
| `--color-ink` | `#14191B` | 16.65 / 17.73 / 15.49 | `#F2F4F4` | 17.76 / 16.46 / 14.86 |
| `--color-ink-2` | `#4A5457` | 7.31 / 7.79 / 6.80 | `#B4BCBF` | 10.16 / 9.42 / 8.50 |
| `--color-ink-3` | `#626C70` | 5.06 / 5.39 / 4.71 | `#8F999D` | 6.73 / 6.24 / 5.63 |
| `--color-accent` | `#0B5FCC` | 5.60 / 5.96 / 5.21 | `#7FB2FF` | 9.07 / 8.41 / 7.59 |
| `--color-structural` | `#0A6B5F` | 6.01 / 6.40 / 5.59 | `#5FD0BC` | 10.49 / 9.72 / 8.78 |
| `--color-model` | `#8A4B00` | 6.39 / 6.80 / 5.94 | `#F0B46A` | 10.68 / 9.90 / 8.94 |
| `--color-not-evaluated` | `#5B4AB0` | 6.46 / 6.88 / 6.01 | `#B7ABFF` | 9.60 / 8.90 / 8.03 |
| `--color-unavailable` | `#5C666A` | 5.53 / 5.89 / 5.15 | `#9AA4A8` | 7.70 / 7.14 / 6.44 |
| `--color-danger` | `#B3261E` | 6.14 / 6.54 / 5.71 | `#FF9C94` | 9.74 / 9.03 / 8.15 |
| `--color-success` | `#1B6E3C` | 5.90 / 6.28 / 5.49 | `#74D49A` | 10.85 / 10.06 / 9.08 |

Text on the accent button: white on `#0B5FCC` is 5.96:1, and `#0A0C0D` on `#7FB2FF` is 9.07:1.

`--color-success` is for system states only, such as "loaded". It must never mark a scientific result, because a green tick next to an experiment would imply validation.

**Badge tints, with the matching text colour**

| Token | Light tint | Ratio | Dark tint | Ratio |
| --- | --- | --- | --- | --- |
| `--tint-structural` | `#E3F2EF` | 5.55 | `#10302B` | 7.59 |
| `--tint-model` | `#F8ECDD` | 5.84 | `#33261A` | 7.98 |
| `--tint-not-evaluated` | `#ECE9FA` | 5.77 | `#241F45` | 7.58 |
| `--tint-unavailable` | `#EEF0EF` | 5.15 | `#1C2023` | 6.44 |
| `--tint-danger` | `#FBE9E7` | 5.58 | `#3A1A18` | 7.78 |
| `--tint-accent` | `#E6EFFB` | 5.14 | `#14263F` | 7.05 |

**3D stage:** the stage stays `#0A0C0D` in both themes, so each scene needs only one set of colours and lighting. See question 3 in section 12.

| Neuron class | Colour | Ratio on stage | Non-colour cue |
| --- | --- | --- | --- |
| LC4 | `#7FB2FF` | 9.07 | Thin line, labelled in legend |
| LPLC2 | `#F0B46A` | 10.68 | Thin line, labelled in legend |
| DNp01 | `#F2F4F4` | 17.76 | Line 2x as thick, with a callout label |

The legend's Isolate buttons show one class at a time, which gives a colour-independent way to separate them. Model activity is shown by brightness, with a labelled scale that always reads "Model state, dimensionless".

**Glass:** panels over the stage use `rgba(19,22,24,0.82)` with `backdrop-filter: blur(16px)`. Do not go below 0.82 opacity, which keeps `--color-ink-2` above 5:1 even over a white background. Fall back to solid `--color-surface` under `prefers-reduced-transparency` or when `backdrop-filter` is unsupported.

### Typography

Use **Geist Sans** and **Geist Mono** through `next/font`, with self-hosted files and `font-display: swap`. Their numerals align in tables, and Apple's SF Pro cannot be licensed for general web use. Use `font-variant-numeric: tabular-nums` on all readouts. See question 8 in section 12.

| Token | Size / line height | Weight | Tracking | Use |
| --- | --- | --- | --- | --- |
| `display` | `clamp(2.75rem, 6vw, 5rem)` / 1.05 | 600 | -0.03em | Home hero only |
| `h1` | `clamp(2rem, 4vw, 3rem)` / 1.1 | 600 | -0.02em | Page titles |
| `h2` | 1.75rem / 1.2 | 600 | -0.015em | Sections |
| `h3` | 1.25rem / 1.3 | 600 | -0.01em | Cards, panels |
| `body-lg` | 1.125rem / 1.55 | 400 | 0 | Lead paragraphs |
| `body` | 1rem / 1.55 | 400 | 0 | Default text |
| `small` | 0.875rem / 1.45 | 400 | 0 | Secondary text, panel text |
| `caption` | 0.75rem / 1.35 | 500 | 0.01em | Labels and badges. This is the minimum size |
| `readout-lg` | 1.75rem / 1.1 | 500, mono | -0.01em | Primary readout |
| `readout` | 0.875rem / 1.3 | 400, mono | 0 | Telemetry rows, IDs |

Limit prose to 68 characters per line. Avoid all-caps except in the NEUROFLY wordmark.

### Spacing, layout and radii

- **Spacing, on a 4 px base:** 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 160 px, as `--space-1` to `--space-11`.
- **Section rhythm:** 96 px on phones, 128 px on tablets, 160 px on desktop.
- **Page gutters:** 16 px below 600 px, 32 px up to 1024 px, 48 px above.
- **Content width:** 1200 px maximum, with 720 px for prose.
- **Breakpoints:** 600, 1024, 1440 and 1920 px.
- **Radii:** 6 px for badges and inputs, 10 px for buttons, 16 px for cards and panels, 24 px for hero stages, and full for pills.

### Elevation

Prefer borders to shadows. Dark mode relies on the surface colour and a hairline, with shadow only at level 3.

| Level | Light | Dark | Use |
| --- | --- | --- | --- |
| 0 | Hairline border | Hairline border | Cards, panels |
| 1 | `0 1px 2px rgba(20,25,27,.06)` | Raised colour | Hovered cards |
| 2 | `0 8px 24px rgba(20,25,27,.08)` | Raised colour | Sticky bars, tooltips |
| 3 | `0 24px 64px rgba(20,25,27,.14)` | `0 24px 64px rgba(0,0,0,.5)` | Sheets, dialogs |

### Iconography

Use `lucide-react` with a 1.5 px stroke, at 16 px in dense areas and 20 px elsewhere. Icons in buttons without text need an `aria-label` and a tooltip. Data kinds use custom glyphs defined in section 7, so they never overlap with a general-purpose icon.

### Motion tokens

| Token | Value | Use |
| --- | --- | --- |
| `--dur-fast` | 120 ms | Hover, press, focus |
| `--dur-base` | 200 ms | Tooltips, tabs, badges |
| `--dur-slow` | 320 ms | Panels, sheets, page fade |
| `--dur-camera` | 800 ms | 3D camera moves |
| `--ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | Most transitions |
| `--ease-exit` | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving |

**Principles:** motion explains where something came from and is never decoration. Animate only `transform` and `opacity`. Nothing blocks input, and nothing bounces.

### Component tokens to define

- `--button-height-sm/md/lg`: 32 / 40 / 48 px. Touch targets are at least 44 px on touch devices.
- `--input-height`: 40 px. `--focus-ring`: 2 px solid accent, with 2 px offset.
- `--header-height`: 64 px. `--toolbar-height`: 48 px. `--timeline-height`: 72 px.
- `--panel-width`: 320 px, or 400 px at 1920 px and wider.
- `--card-padding`: 24 px. `--panel-padding`: 16 px. `--badge-height`: 22 px.
- `--stage-bg`, `--stage-grid`, `--neuron-lc4`, `--neuron-lplc2`, `--neuron-dnp01`, `--glass-bg`, `--glass-blur`.

## 5. Page-by-page redesign

Each page answers one question first and reveals depth on request. Marketing-style space is reserved for Home and Science; tools use their space for the instrument.

### Home

**Question it answers:** what is this, and can I trust it?

1. **Hero, full viewport.** A dark stage with a slowly rotating selected circuit, with the text placed above it, not over the neurons.
   - Eyebrow: "Research project"
   - Headline: "A fruit fly's neural circuit, modelled step by step."
   - Statement: "NeuroFly is building a digital model of a fruit fly's nervous system and movement, starting from a small circuit mapped in the real connectome."
   - Actions: primary "Watch a looming response", secondary "How much of this is real?", which links to Status and limits.
2. **Status strip, directly under the hero.** Four short facts, always visible:
   - "313 bodies: 126 LC4, 185 LPLC2, 2 DNp01"
   - "Wiring from MaleCNS v1.0"
   - "Kinematic body, no muscle or wing physics"
   - "Not yet evaluated against real flies"
3. **Three-layer explainer.** Connectome (Structural), Neuron model (Model assumption), Output (Model state). This teaches the distinction once, using the same glyphs as the rest of the site.
4. **Scenario gallery.** Up to four scenario cards: looming, horizontal motion, independent visual stimuli and arena navigation.
5. **Choose your path.** "I'm new" leads to guided playback. "I'm a researcher" leads to Experiments and the data.
6. **Roadmap, as a plain list.** What exists and what is planned. Plans are worded as plans, without dates unless you commit to them.

**Hero asset:** poster image first, 3D or video only after load, and never for reduced-motion users. See section 6 for the viewport frame.

### Scenarios list

- **Header:** one sentence defining a scenario, with a link to the glossary.
- **Cards in a grid:** 3 columns on desktop, 2 on tablet, 1 on phone. Each has a poster, name, plain description, stimulus type and duration if available.
- **Filter:** a segmented control by stimulus type, reflected in the URL.
- **Removed:** "verified" badges, until question 1 in section 12 is answered.

### Scenario detail and playback

- **Layout:** full-width stage, timeline below it, then a two-column area below the fold.
- **Left column:** what happens, in plain words, and what the viewer should notice.
- **Right column:** provenance card with stimulus, circuit, model version and status.
- **Guided mode:** on the first visit, 3 to 4 captions tied to timeline moments, skippable and restartable. Captions describe the model's behaviour, never the fly's.
- **Next step:** "See the published experiments for this scenario".

### Experiments list

- **Format:** a table on desktop, because experts compare. It collapses to stacked rows below 600 px.
- **Columns:** name, scenario, status, model version, date, and the action "Open Cockpit".
- **Sorting and filters:** sortable headers with `aria-sort`, a scenario filter and a text search, all kept in the URL.
- **Explainer banner:** one line, dismissible but restorable: "No experiment has been evaluated against biological data yet."

### Experiment detail

The sections run in reading order:

1. Title, status badge, scenario link and the primary "Open Cockpit" action.
2. Summary: what ran, in 2 to 3 sentences.
3. Poster or replay.
4. Setup: circuit, stimulus, neuron model and body model, each with a kind glyph.
5. Results: key readouts and charts, each labelled "Model state, dimensionless".
6. What this does not show: a short list specific to the experiment.
7. Data: artifact ID, source release, API links and a copy button.

### Scientific Cockpit

The Cockpit opens at Overview with one large view and up to six readouts. Only one area leads at a time, and the reader chooses when to add density.

&#91;embedded content: Cockpit layout at 1440 px, Overview layer\]

| Layer | Shows | Who it serves |
| --- | --- | --- |
| **Overview** (default) | World, small Connectome, up to 6 readouts, timeline | Everyone |
| **Detail** | Adds a 320 px right panel with grouped telemetry, per-class charts and a selected-body inspector | Researchers |
| **Raw** | Adds a bottom table of values at the current time, with machine status codes, IDs and API links | Experts checking data |

- **Telemetry grouping in Detail:** Stimulus, Neural, Body and System, as accordions. They open independently, and their state is remembered per viewer.
- **Panel swap:** Expand moves Connectome into the large area. World becomes the smaller panel, in a 200 ms crossfade.
- **Selection:** clicking a body highlights it in the connectome and pins its row. The selection appears in the URL as `?body=`.
- **Keyboard:** `Space` plays or pauses, left and right arrows step, `1` `2` `3` change layer, and `?` lists shortcuts.
- **Live-control safeguard:** the toolbar states "Replay of a completed run", so nobody thinks they are controlling a live simulation.

| Width | Cockpit strategy |
| --- | --- |
| 1920 px and up | Overview plus an always-open Detail panel |
| 1024 to 1919 px | Layout as drawn. Detail opens as a right panel |
| 600 to 1023 px | World on top, tabs for Connectome and Readouts, timeline pinned at the bottom |
| Below 600 px | **Simplified replay:** World only, in a 4:5 stage, 3 readouts, timeline. Connectome and Raw are replaced by a clear note, with "Copy link for desktop" |

### Neurons (morphology inspector)

- **List:** cards for DNp01 and the six-body sample. **Assumption:** the cut-off text meant "six-body sample".
- **Inspector:** a full stage with orbit controls, a compact legend and a left panel for body ID, type and source release.
- **Honesty:** the whole page carries the Structural label, since it shows connectome data. This is the page where the empirical data can speak plainly.
- **Controls:** reset view, isolate body, toggle synapses if the data exists, and a screenshot button that embeds provenance text.
- **Plain-language intro:** one sentence at the top: "This is the reconstructed shape of real neurons, not a simulation."

### Lab

- **Overview, new page:** three cards explain each tool, what it models and what it leaves out.
  - **Arena:** locomotion and flight on a course.
  - **Research arena:** more detailed controls and instrumentation.
  - **Fly viewer:** the body model and neural activity explorer.
- **Shared layout:** the same frame as the Cockpit, with a stage, a 320 px controls panel and a bottom timeline if the tool plays over time.
- **Scope notice:** a slim line stays above the stage: "Kinematic model. No muscle or wing physics. Output is model state."
- **Controls:** labelled sliders with numeric inputs, and a Reset button. Any unavailable control appears with its reason (section 7).
- **Read-only:** controls may only change the view or request existing data. See question 2 in section 12.
- **Phones:** Arena gets a simplified view with basic controls. Research arena shows "Best on a larger screen", a poster and a link to scenarios.

### Science

The page reads as a calm, long-form article with a sticky contents list from 1024 px up.

1. What NeuroFly models now, stated in a single paragraph with the 313-body count.
2. Where the data comes from: MaleCNS v1.0, with a link and citation.
3. How the model works: neuron model, synapses, body and determinism.
4. What each kind of number means, using the five glyphs.
5. What has not been done: no empirical validation, no biological calibration.
6. Capabilities table, summarised, linking to Status and limits.
7. Docs repository, glossary and how to cite. See question 10 in section 12.

**Status and limits, new page:** a table of capability, state and reason, grouped into "Available", "Model only" and "Not available yet".

### Global states

Every state names what happened and what still works. Keep the page frame in place, so a failure in one source does not blank the page.

| State | Pattern | Example copy |
| --- | --- | --- |
| **Page loading** | Skeleton matching the final layout, shown after 200 ms | No text needed |
| **3D loading** | Poster in the frame, a thin progress line, a stage label | "Loading 313 neuron shapes" |
| **Empty list** | One line and one link | "No experiments match these filters." Clear filters |
| **API down** | Inline panel with retry | "The data service isn't responding. Nothing on this page has been lost." Retry |
| **Route error** | Full-page panel, with a reference and a link home | "This page couldn't load." Try again, Go home |
| **Not found** | Plain page, with three section links | "We couldn't find that page." |
| **Unknown ID** | Page with the ID shown and a link to the list | "There is no experiment with the ID `abc123`." |
| **WebGL off or context lost** | Poster and a data table where possible | "3D isn't available on this device. The data below is the same." |
| **Low-power device** | Automatic lower detail, with a notice | "Showing simplified shapes for smoother playback." Use full detail |

**Data unavailable, per optional source.** **Assumption:** these are the likely optional sources, so match them to the real API response.

| Source missing | Panel shows | Rest of the page |
| --- | --- | --- |
| Morphology meshes | Bodies as a labelled point cloud, or a poster, with "Neuron shapes not included in this artifact" | Continues |
| Connectome edges | "Connection data not included in this artifact" | World and telemetry continue |
| Telemetry channel | The row stays, showing an em dash and "Not recorded" | Other rows continue |
| World replay | Poster, with "No world replay for this experiment" | Connectome and telemetry continue |
| Level C mapping | Unavailable badge with its reason | Continues, not treated as an error |

A missing value is never drawn as zero.

## 6. Component specs

Ten shared components cover most of the UI, and three of them (`KindBadge`, `Readout`, `ProvenanceLabel`) enforce the honesty rules in code. Their TypeScript props should make it impossible to render a value without a kind.

| Component | Anatomy and size | Variants and states | Rules |
| --- | --- | --- | --- |
| **`SiteHeader`** (replaces `AppHeader`) | 64 px high, logo left, nav centred, status pill and theme right | `default`, `tool` (48 px), `over-stage` (glass) | Sticky. Includes a "Skip to content" link as its first focusable element |
| **`SiteNavigation`** | Links at `small`/500, 16 px apart. Mobile sheet at 100% height | `current`, hover, focus | Uses `nav` with `aria-label`. The sheet traps focus and closes on `Esc` |
| **`Card`** (`ScenarioCard` builds on it) | 16 px radius, 24 px padding, poster at 16:9, hairline border | `default`, `interactive`, `selected`, `unavailable` | One link per card, stretched over it. Hover: border darkens and poster scales 1.02. No lift |
| **`Panel`** | 16 px radius, 16 px padding, a 40 px header with title and actions | `surface`, `glass`, `collapsible` | The header is a real `button` with `aria-expanded`. Scroll inside the body only |
| **`Readout`** | Label at `caption`, value at `readout` or `readout-lg`, unit, and kind glyph | `value`, `not-recorded`, `unavailable`, `loading` | `kind` is a required prop. Dimensionless values display "model state" and never a biological unit. Width stays fixed so digits do not shift |
| **`Timeline`** | 72 px high, play button 40 px, scrub track with 24 px hit area, time in mono, speed menu | `playing`, `paused`, `buffering`, `ended`, `no-data` | Uses `role="slider"` with `aria-valuetext`, such as "Step 120 of 800". Arrows step 1, `Shift`+arrows step 10, `Home`/`End` jump. Event markers are named buttons |
| **`KindBadge`** | 22 px high, 6 px radius, 12 px glyph, label at `caption` | The five kinds in section 7 | Glyph and text are shown together by default. Tint plus text meets the ratios in section 4. Glyph-only is allowed only inside a titled group (section 7), and still needs an accessible name |
| **`Viewport3D`** (frame for all canvases) | Stage background, 16 px or 24 px radius, title and kind label top left, controls bottom right, legend bottom left | `poster`, `loading`, `ready`, `paused`, `degraded`, `no-webgl`, `context-lost`, `missing-data` | Lazily mounted with `next/dynamic` and `ssr: false`. Reserves its aspect ratio to prevent layout shift. Has a text description and, where possible, a data alternative |
| **`Tooltip`** | Max 280 px wide, 8 px radius, `small`, level 2, opens at 400 ms on hover and immediately on focus | `plain`, `definition` | Dismisses on `Esc`, stays open when hovered (WCAG 1.4.13). Never the only place essential information appears. On touch, opens on tap |
| **`ProvenanceLabel`** | One line at `caption`: glyph, source, version, then a details button | `inline`, `card`, `raw` | Opens a popover with source, version, status and artifact ID, plus a copy button. Sits next to the data it describes |

**Also needed:** `Button`, `SegmentedControl`, `Table`, `Skeleton`, `StatePanel` (all error and empty states), `Legend` and `Dialog`.

**Shared 3D settings for `Viewport3D`:**

- `frameloop="demand"`, except during playback or camera moves.
- `dpr` capped at `[1, 1.5]` on phones and `[1, 2]` on desktop.
- Pause rendering when offscreen (`IntersectionObserver`) or when the tab is hidden.
- Three detail tiers. **High** is full meshes, **Medium** is reduced meshes or instanced lines, and **Low** is skeleton lines or a poster.
- Drop a tier when the frame rate stays under 30 fps for 3 seconds, and tell the reader.
- Handle `webglcontextlost` and offer a restart.
- Do parsing work for large geometry in a Web Worker.

## 7. Trust and scientific-honesty patterns

Every number on the site declares its kind, and restraint is presented as a feature. The aim is that a screenshot taken from any page still tells the truth without its surrounding text.

### The five kinds

| Kind | Glyph | Colour token | Label | Tooltip |
| --- | --- | --- | --- | --- |
| **Structural** | Solid square | `--color-structural` | Structural | "From the MaleCNS v1.0 connectome. Describes physical wiring, not signal strength." |
| **Model assumption** | Hollow diamond | `--color-model` | Model assumption | "Chosen for the model, not measured from the fly." |
| **Model state** | Half-filled circle | `--color-`ink-2, because accent is reserved for actions | Model state | "Dimensionless simulation output. Not a biological measurement." |
| **Not evaluated** | Dashed circle | `--color-not-evaluated` | Not evaluated | "Not yet compared with real fly data. This is not a failure." |
| **Unavailable** | Circle with slash | `--color-unavailable` | Not available yet | "Deliberately off. The reason is on the Status page." |

The square and diamond differ by shape, and the three circles differ by half fill, dashed outline and slash. Check all five in a greyscale screenshot before sign-off.

### Where each pattern appears

1. **Status pill in the header.** It reads "Model · Not evaluated" and links to Status and limits. It is present on every page, so no route can look more certain than the project is.
2. **Value-level kinds.** Every `Readout` has a glyph. In a group of one kind, the group title carries the full label and each row keeps a small glyph.
3. **Edge values.** The connectome tooltip reads "42 synaptic contacts (Structural). Not a physiological gain." The number is an illustration.
4. **Axis labels.** Charts read "Model state (dimensionless)" and never "mV", "Hz" or "firing rate".
5. **Screenshots and exports.** Any image from the screenshot button includes a footer with experiment ID, model version and "Model output, not biological data".
6. **What this does not show.** Each experiment detail page has this short list. It is written as useful information, not as a legal disclaimer.

### Provenance popover

| Field | Example | Shown when |
| --- | --- | --- |
| Kind | Structural | Always |
| Source | MaleCNS v1.0 | Always |
| Model version | From the artifact | Model values only |
| Status | Not evaluated | Experiments |
| Artifact ID | Copyable, in mono | Always |
| API link | Opens JSON in a new tab | Detail and Raw layers |

### Unavailable capabilities without looking like an error

- **Visual treatment:** neutral grey with the slash-circle glyph, a dashed border and no red or warning icon.
- **Copy format:** state what it is, why it is off and where to learn more. For example: "Level C visual-angle mapping. Not available yet, because the mapping has not been validated. About this limit." **Assumption:** confirm the true reason for each capability.
- **Interaction:** keep the control focusable with `aria-disabled="true"`, not the `disabled` attribute, so keyboard and screen-reader users can reach the explanation.
- **Grouping:** collect these items in their own "Not available yet" group rather than scattering them among working controls.

### Language rules

- Describe outputs with the model as the subject: "the model's DNp01 state rises". Never write "the fly's neuron fires".
- Do not use green ticks, percentage scores or "accuracy" near any result.
- Present limits next to the claim they limit, at the same type size as body text.
- Keep the disclosure copy in one file, `src/content/science-copy.ts`, so wording stays consistent and can be reviewed scientifically.

## 8. Interaction and motion

The product feel comes from continuity: the card a reader clicks becomes the stage they arrive at. Everything else stays quick and quiet.

| Moment | Behaviour | Duration | Reduced motion |
| --- | --- | --- | --- |
| Page change | Fade the content, keeping the header still. Use the View Transitions API where supported | 200 ms | Instant |
| Card to detail | The poster morphs into the stage where supported, otherwise a fade | 320 ms | Instant |
| Home hero | Slow rotation at 1 revolution per 60 s. Pauses on scroll away, and has a visible pause button | Continuous | Static poster |
| Section reveal on Home | Opacity 0 to 1, and 16 px upward, once only. Never used in tools | 320 ms | Visible at once |
| Play or pause | Icon swaps. The stage does not dim | 120 ms | Same swap, no fade |
| Scrubbing | All panels update on the next frame. The value does not animate | Immediate | Same |
| Buffering | Progress stripe on the timeline track, with "Loading frames" after 500 ms | Until ready | Static label |
| Run ended | Timeline stops at the end with a Replay button. No auto-loop in tools | 200 ms | Instant |
| Camera preset or focus | Eased move, cancelled immediately by any user input | 800 ms | Cut directly |
| Layer change | Panels slide 16 px and fade | 320 ms | Instant |
| Panel swap | Crossfade | 200 ms | Instant |
| Tooltip | Fade in after the delay | 120 ms | Instant |
| Hover and press | Colour change. Press scales buttons to 0.98 | 120 ms | Colour only |

**Playback feedback**

- The readouts, connectome and world always share the same frame index, from one playback clock.
- Show the current time and the step together. The frame shown at a given time should be identical on every replay, reflecting the deterministic model.
- Event markers on the timeline, such as stimulus onset, are labelled and clickable.

**Reduced motion:** honour `prefers-reduced-motion: reduce` in CSS with a global token override, and in JS with a shared `useReducedMotion` hook. Playback stays available because the reader starts it, but it never autoplays. Camera moves become cuts.

**Performance rules**

- Update telemetry text at 10 Hz at most, even if the 3D scene runs at 60 fps.
- Drive per-frame updates through refs in `useFrame`, not React state, so panels do not re-render on every frame.
- Virtualise Raw tables with more than 100 rows.
- Load three.js only on routes with a 3D view, and only after the first paint.

## 9. Accessibility checklist per page

WCAG 2.2 AA is the baseline for every page, and the hard cases are the 3D views. Each 3D view must have a useful non-visual equivalent, because a canvas alone exposes nothing to a screen reader.

### Every page

- [ ] A skip link is the first focusable element, and each page has one `h1` and `main`.
- [ ] Focus is visible, at least 2 px, and never hidden by sticky bars (2.4.11).
- [ ] Targets are at least 24 x 24 px (2.5.8), and 44 px on touch.
- [ ] Text reflows at 320 px wide and at 200% zoom, without horizontal scrolling. Tools may scroll inside their own panels.
- [ ] After a route change, focus moves to the `h1` and the new page title is announced.
- [ ] Reduced motion, forced colours and both themes have been tested.
- [ ] Status never depends on colour alone.

### Page by page

| Page | Specific checks |
| --- | --- |
| **Home** | The hero has a pause button (2.2.2). The canvas is decorative with `aria-hidden`, and the status strip is real text. Poster alt text states the scope. |
| **Scenarios list** | Filters are a labelled group with state announced through `aria-pressed` or radios. The result count is in an `aria-live="polite"` region. Cards have one clear accessible name. |
| **Scenario detail** | Playback controls work by keyboard. Captions are real DOM text. The text beside the stage describes what happens. Nothing autoplays with reduced motion on. |
| **Experiments list** | Uses real `table`, `th` and `scope`, with `aria-sort` on headers. Status badges have text. The row action names its experiment, such as "Open Cockpit for Looming 01". |
| **Experiment detail** | Headings run in order. Charts have a text summary and a data table. The copy button confirms through a live region. |
| **Cockpit** | The tab order is toolbar, world, connectome, readouts, timeline. Panels are named landmarks. Readouts are not announced on every frame, and a "Read current values" button gives a snapshot on demand. Shortcuts can be turned off (2.1.4). A single-pointer alternative exists for dragging, such as view preset buttons (2.5.7). |
| **Neurons** | Orbit has button alternatives: rotate, zoom, reset. A body list mirrors the 3D selection. Each neuron has a text description with its type and ID. |
| **Lab** | Sliders are native or follow the ARIA slider pattern, with typed input as an alternative. `aria-disabled` controls explain themselves. Scope notice is real text before the stage in reading order. |
| **Science** | The contents list is a `nav`. Tables have captions. Glossary terms use a description list with stable anchors. Long-form text keeps a 68-character measure. |
| **Error, empty, not found** | Errors move focus to the message or use `role="alert"`. Recovery actions are real buttons or links. Language describes what happened without blame. |

## 10. Implementation plan

Ship ten independent phases, in this order, each as its own reviewable pull request or small set. The old CSS stays until its page is migrated, so the site keeps working throughout.

**Assumption:** only the CSS files and routes come from your description. The folders for new components, such as `src/components/ui/`, are suggestions.

| Phase | Goal | Most likely files | Done when |
| --- | --- | --- | --- |
| **0. Baseline** | Record the current state and verify section 1 | New `docs/redesign-baseline.md`, screenshots, Lighthouse and axe reports | Diagnosis confirmed, question 1 in section 12 answered |
| **1. Tokens** | Add colour, type, spacing and motion tokens. Map old variables to new ones | `src/app/globals.css`, new `src/styles/tokens.css`, `src/app/layout.tsx` (fonts, theme) | No visual breakage, and the theme switch works without a flash |
| **2. Honesty primitives** | Build `KindBadge`, `Readout`, `ProvenanceLabel`, `Tooltip`, `StatePanel` and copy file | New `src/components/ui/*`, new `src/content/science-copy.ts` | Each component works in both themes, with tests |
| **3. Shell** | New header, nav, footer, status pill and skip link. Fix nav labels | `AppHeader`, `SiteChrome`, `SiteNavigation`, `BrandLogo`, `product.css` | Keyboard path through the header passes, on all routes |
| **4. Content pages** | Science, Status and limits, Glossary | `src/app/science/*`, `science/science.css` | Copy has been reviewed, and pages have no 3D dependency |
| **5. Home** | New hero, status strip, explainer, gallery | `src/app/page.tsx`, `discovery.css`, `ScenarioCard` | LCP target met with the poster |
| **6. Lists and details** | Scenarios and Experiments, with shared `Card` and `Table` | `src/app/scenarios/*`, `src/app/experiments/*`, `ExperimentList`, `PlaybackWorkspace`, `TimelineInspector`, `scenarios.css` | Vocabulary is consistent, and URL filters work |
| **7. 3D frame and Neurons** | `Viewport3D` with all states and tiers. Migrate the simplest 3D page first | `MorphologyInspector`, `PlaybackCanvas`, `src/app/morphology/*` | No-WebGL, context-loss and low-tier cases all pass |
| **8. Cockpit and Lab** | Layers, shared clock, responsive strategy, Lab overview | `ScientificCockpit`, `CockpitPanels`, `CockpitTelemetry`, `NeuralActivityExplorer3D`, `FlyViewer`, `ArenaCourseViewer`, `cockpit.css`, `lab.css`, `viewer.css` | Overview shows 6 or fewer readouts, and phones get simplified replay |
| **9. Polish and removal** | Route transitions, optional jump menu, final audit, delete old CSS | All remaining CSS files, `error.tsx`, `not-found.tsx`, `loading.tsx` | All of section 11 passes |

**Styling choice:** CSS Modules plus global tokens, since the project already uses plain CSS and has no component library. This keeps dependencies low. Move each legacy file's rules into its component's module as that component is migrated.

**Do not change in this project:** the API, the simulation code, or any data contract. If a label needs new data, record it as a backend request and show the "Not recorded" state until it exists.

## 11. Acceptance criteria

The redesign is done when each check below passes, ideally automated in CI. The performance targets are my proposals, so adjust them after the phase 0 baseline.

| Area | Check | Target | How to test |
| --- | --- | --- | --- |
| Contrast | Text, and non-text UI | 4.5:1 for text, 3:1 for controls | axe, plus a token contrast unit test |
| Automated accessibility | Serious or critical violations | 0 on every route, in both themes | `@axe-core/playwright` |
| Lighthouse (mobile) | Accessibility, on all routes | 95 or above | Lighthouse CI |
| Lighthouse (mobile) | Performance on Home, lists, Science | 90 or above | Lighthouse CI |
| Core Web Vitals | LCP, INP, CLS at the 75th percentile | 2.5 s or less, 200 ms or less, 0.1 or less | Lab tests, then field data if available |
| Bundle | three.js on pages without 3D | Not loaded | Bundle analyser, network log |
| 3D performance | Frame rate during Cockpit playback | 30 fps or above on a reference laptop you name, after tier drop | Manual test, with a logged trace |
| 3D resilience | WebGL off, context lost, mesh fetch fails | A useful message, and the page stays usable | Playwright with mocks |
| Keyboard | Home to playback, and list to Cockpit to scrub | Completed with no mouse, and focus always visible | Scripted Playwright test, plus one manual pass |
| Screen reader | Key paths on Home, an experiment and the Cockpit | Understandable with VoiceOver and NVDA | Manual test |
| Reduced motion | Autoplay and camera moves | None under `reduce` | Playwright emulation |
| Colour independence | Greyscale screenshot of each kind and neuron class | All can be told apart using glyph, label or thickness | Visual review |
| Responsive | Widths 360, 390, 768, 1024, 1440, 1920 px | No page-level horizontal scroll, and targets at least 24 px | Playwright screenshots |
| Mobile Cockpit | Below 600 px | Simplified replay, with its notice | Device test |
| Density | Cockpit Overview values | 6 or fewer | Component test |
| Honesty | Every numeric readout | Has a kind, and `kind` is required in the type | `tsc`, plus a route-by-route review |
| Honesty | Biological units on model output | 0 instances | Text search plus review |
| Honesty | "Verified", or a success colour, on a scientific result | 0 instances | Text search plus review |
| Vocabulary | Nav label, page title and URL for each section | They match section 2 | Test of the nav |
| Tokens | Hard-coded colours outside the tokens file | 0 | Stylelint in CI |
| **Read-only** | API methods during a full end-to-end run | Only `GET`, `HEAD` or `OPTIONS` | Playwright network assertion that fails on anything else |
| **Read-only** | Write calls in frontend source | 0 `POST`, `PUT`, `PATCH`, `DELETE`, and no Server Actions that write | Text search in CI |
| Regression | All existing routes | Resolve without an error | Route smoke test |
| Regression | Existing tests | All pass | Existing CI |

## 12. Open questions for the owner

Questions 1 and 2 should be answered before phase 1, because they affect scientific accuracy and the read-only rule. The others have a default, and work can proceed on the recommendation.

| # | Question | Recommendation | Why |
| --- | --- | --- | --- |
| 1 | What exactly does "verified" mean for canonical scenarios? | Use "Reproducible" or "Checked by project tests", and remove "verified" | It may imply biological validation |
| 2 | Do Lab controls replay stored data, request existing API results, or compute anything in the browser? | Say "Replay" or "Precomputed" in the UI, and keep every control view-only | The frontend must not run the simulation, yet the Lab is described as interactive |
| 3 | Should the 3D stage stay dark in light mode? | Yes, always dark | One set of scene colours and lighting to test, and neurons read best on black |
| 4 | Which theme should be the default? | Follow the system setting, with a manual switch. Use dark for the first visit if there is no signal | Fits both the brief and the project's current look |
| 5 | Can routes be renamed, such as `/morphology` to `/neurons`? | Keep URLs now, change labels only, and consider 308 redirects later | Protects existing links, and renames add risk with little gain |
| 6 | Which asset carries the hero: real-time 3D, or video? | Poster, then a short muted loop from a real run, labelled as model output | Faster than real-time 3D, and honest if it uses real output |
| 7 | Which language or languages? | English only for launch, but keep all copy in one file | Matches your scientific audience, and leaves translation possible |
| 8 | Is Geist acceptable, or do you want a more distinctive typeface? | Geist | Free, good numerals, and close to the requested feel |
| 9 | How much of the Cockpit should phones get? | Simplified replay only | A three-panel instrument will not be readable at 390 px |
| 10 | What credits and citation should appear? | Add a "How to cite" block and explicit MaleCNS credit | Researchers need it. Please supply the exact citation and data licence terms |
| 11 | Does the glossary in section 3 match the backend model? | Confirm, or correct the relationships | The whole site's language depends on it |
| 12 | Is a person or lab named as the author? | Name the project's author on the Science page | Trust increases when readers can see who is responsible |

## Phase 0 decisions (2026-11-03)

These decisions come from the owner after the phase 0 baseline
(`docs/redesign-baseline.md`). **They override any conflicting text in this
brief.**

1. **Vocabulary for checks.** In the interface, "Validation" becomes
   "Circuit check" and "verified" becomes "Integrity-checked". The API is
   unchanged. Each label has an explanation beside it that it is not
   biological validation.
2. **Read-only, narrowed.** "Read-only" means no writes to the API or to server
   data. Only the Lab may run the model in the browser. Experiments, scenarios
   and the Cockpit stay playback of stored data. Browser execution is not
   extended elsewhere without the owner's approval. The Lab is labelled "Runs
   in your browser", states exactly what was compared with the recorded Python
   run and at what tolerance, and does not imply wider validation. It tells
   users that runs saved in browser storage stay in this browser only. It is
   never called "Replay".
3. **Write test.** The end-to-end test fails on any write to the API. It allows
   one named Server Action (`loadScenarioPlayback`), which only reads stored
   data. "Run canonical preset" is renamed to "Replay canonical preset" or
   similar.
4. **Units.** Never show a bare "mV". Show "mV_eq" with "model-equivalent, not
   measured". "Dimensionless" is used only for values that have no unit.
5. **Wording.**
   - Status strip: "Two selected circuits: looming (313 bodies) and HS → DNp15
     (8 bodies). Not a whole brain." The counts are not added together.
   - Home headline: "Selected fruit fly circuits, modelled from the
     connectome."
   - Home statement: "NeuroFly is a research model of selected fruit fly
     neural circuits, built from the MaleCNS connectome and connected to a
     simplified simulated body."
   - "Digital organism" (and "digital fly") is removed from the interface.
   - Navigation becomes Scenarios, Neurons, Lab, Science. Experiments leaves
     the main navigation but its routes keep working and are linked from
     Scenarios and Science. The current item is labelled "Engineering test,
     not a scientific experiment". Experiments returns to the navigation when
     a real scientific experiment exists. This replaces the five-item header in
     section 2.
6. **Artifacts.** `docs/redesign-baseline.md` and its reports are committed.
   Screenshots stay local.

Scheduled work: translate the Lab's Portuguese text to English in phase 8;
fix the blank scenario stage with WebGL off in phase 7; return proper 404s for
unknown IDs in phase 6, or earlier if the fix is small. Backend follow-ups are
listed in the baseline.
