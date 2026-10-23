# NeuroFly product foundation and homepage v10.0 / v10.1

Presentation-only implementation on baseline `2b9c0c7033647d0d091fc67200738aaaf28b168f`.
The homepage introduces the existing product; it does not add simulation capabilities.

## Public entry and preserved routes

`/` is a static product homepage, independent of the scientific API. The canonical
catalogue previously shown at `/` remains available at the existing `/scenarios`
route. Its real API, error handling and catalogue tests are preserved. `/experiments`
continues to expose persisted experiments. No existing route is moved or renamed.

The primary destination is the unchanged `/visual-lab/arena`. The specimen showcase
links to `/visual-lab/fly`. Science navigation links to `/#science`, with a further
link to the repository's public `docs/science` directory. No placeholder pages,
redirects, accounts, analytics or external services are introduced.

## Design foundation

`web/src/app/product.css` scopes website styling and custom properties to `.nf-site`.
The existing laboratory, experiment, cockpit and scientific styling remain intact.
The root layout adds only this stylesheet import. Existing global metadata remains
the fallback for established routes; the homepage defines its own title, description
and Open Graph text. The browser icons and shared header/footer emblem use the approved user-supplied
NeuroFly mark. The canonical white PNG has real alpha transparency and no backing
square. Shared navigation renders it directly on dark surfaces. Genuine PNG/ICO
browser icons replace the former monogram/embedded-raster SVG. See
[`neurofly_white_branding.md`](neurofly_white_branding.md) for source authentication,
derivation and the small favicon contour used for light-tab legibility.

| Token | Value / role |
| --- | --- |
| `--nf-bg` | `#08131f`, deep navy canvas |
| `--nf-surface` | `#102231`, elevated surface |
| `--nf-surface-soft` | `#172c3b`, muted surface |
| `--nf-text` | `#f1f7fa`, primary text |
| `--nf-muted` | `#a7bbc8`, secondary text |
| `--nf-cyan` | `#86e5de`, actions and highlights |
| `--nf-turquoise` | `#63cdba`, complementary accent |
| `--nf-warm` | `#f1b776`, selective warm detail |
| `--nf-radius` | 18 px feature surfaces; actions use 6 px |
| `--nf-space` | Responsive section rhythm, 68–120 px |

System Arial/Helvetica typography makes no font requests. A 1280 px container,
responsive display type, editorial feature layout and a light process section
provide hierarchy and contrast. No decorative quantitative charts are used.

Reusable components live in `web/src/components/site`: `SiteHeader`, `SiteFooter`,
`MobileNavigation`, `ActionLink`, `SectionHeading`, `FeatureIcon`, `Arrow` and
`SpecimenVisual`. Shared public destinations are explicit in `siteContent.ts`.
The existing `AppHeader` and laboratory components are untouched.

## Static specimen imagery and attribution

Both homepage images are camera/light renders of the approved artistic V2-F GLB,
not photographs, experimental observations or screenshots of laboratory features.
The chamber composition is explicitly labelled a static illustration.

- Original work: *Wildtype Male Drosophila Melanogaster*, mlykouretzos.
- Source: https://sketchfab.com/3d-models/wildtype-male-drosophila-melanogaster-0affd20207ca4c889bd7e1e513e04dfa
- Licence: https://creativecommons.org/licenses/by/4.0/
- Existing NeuroFly model: `web/public/assets/fly/fly_visual_v2f.glb`.
- Source SHA-256: `0502cb995d25b2f9d7b57eff0cf95a0c9cfd7f838e212e95b3895bb69c7e5238`.
- Source geometry, authored materials, GLB bytes and Blender assets are unchanged.
- New modifications: static camera, studio lighting, transparent raster rendering,
  resizing and WebP compression. Attribution and source/licence links appear in the footer.

The render used Blender 4.0.2, Cycles CPU, 48 samples, transparent film, AgX and no
denoising. In Blender coordinates, the orthographic camera is `(1.15, -1.55, 1.15)`,
aimed at `(0, .015, .015)`, scale 1.18. Disk lights: key `(1,-1,2)` / 170 W /
RGB `(1,.84,.64)` / size 2; fill `(-1,-.5,.9)` / 90 W / `(.6,.86,1)` / size 1.4;
rim `(.2,1,1.3)` / 190 W / `(.4,1,.9)` / size 1.3. The source is imported without
geometry or material edits. Raster conversion used Pillow 10.2.0, WebP method 6.

| Committed derivative | Dimensions | Encoding | SHA-256 |
| --- | --- | --- | --- |
| `web/public/assets/site/fly-specimen.webp` | 1500×1400 | quality 88 | `005578d9d07a8af39846321c017ae6d89893b8929c8612a3e78ac6d866ed4859` |
| `web/public/assets/site/fly-specimen-small.webp` | 768×717 | Lanczos resize, quality 86 | `d87ee1d7fe3b2fcb8d9cbc5b71081d957a6576babec3afe059af40beb514be4a` |

## Accessibility, progressive enhancement and performance

The document has one meaningful H1, section headings, labelled navigation,
meaningful image alternatives, visible focus and a skip link. Mobile navigation is
a native `details` disclosure: Enter/Space opens it; JavaScript adds Escape dismissal,
focus return and dismissal on link activation. It has no modal focus trap.

The inherited root `loading.tsx` is preserved. A homepage-only `noscript` stylesheet
reveals its completed server content from React's hidden streaming container and
hides the corresponding legacy loading fallback. Its selectors require `.nf-site`;
they do not change scientific routes. The no-JavaScript path is tested in Chromium.

Images have reserved layout space, responsive source sizes, high priority for the
hero and lazy loading for the lower preview. The two committed derivatives total
about 247 KiB; an ordinary DPR-1 mobile viewport selects the approximately 64 KiB
image. Native image failure is handled both at load-error time and on hydration of
an already-failed image. The hero retains its copy, actions and a specimen-viewer
fallback. There are no image-optimizer service requirements.

Page content, shell and primitives render on the server. Only the native menu
enhancement and image fallback are small client components. There are no homepage
GLB, Three.js, WebGL, neural-engine, scientific API or telemetry imports. Internal
links disable speculative prefetch, avoiding scientific-route downloads before an
explicit navigation. There are no added dependencies, continuous animations,
scroll handlers or simulation clocks. Reduced motion disables entrance/hover motion.

Measured token contrast ratios: primary/navy 17.29:1, secondary/muted surface 7.25:1,
CTA 10.61:1, light-section body 5.78:1 and light-section label 5.70:1. These are
token checks, not a claim of a comprehensive third-party accessibility certification.

## Scientific scope

Copy distinguishes MaleCNS structural connectivity from selected simulated circuits,
proxy neural dynamics and engineering movement projections. It makes no claim of
whole-fly emulation, physiological yaw calibration, biological learning, or reproduction
of laboratory G3 stimuli. Articulated limbs are described as presentation. The
homepage never mounts the scientific simulation as decoration.

## Local verification

Canonical commands from `web`:

```sh
PATH="/path/to/NeuroFly/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 npm test
npm run lint
npm run typecheck
npm run build
```

The virtualenv supplies the `python` executable used by existing cross-language
tests. No dependency is installed for this phase. Focused homepage coverage is
`./node_modules/.bin/tsx --test tests/homepage.test.ts`; catalogue transport tests
now explicitly exercise the preserved `/scenarios` route. Simulation tests are
unchanged. `git diff --check` and explicit scientific-path preservation checks apply.

Browser acceptance uses the already-installed headless Chromium through CDP,
without adding a browser-testing dependency. Review captures and temporary scripts
stay outside Git; they are not runtime inputs or permanent scientific authorities.
Validation outcomes and limitations are reported with the local implementation.

Final local results: 331 frontend tests passed, including the 17 homepage/catalogue
tests; lint, typecheck, production build and whitespace checks passed. The build
prerenders `/` and retains every existing application route. The production build
was exercised in Chromium at 1440, 1024, 768, 390 and 320 px without horizontal
overflow. Screenshots were inspected at desktop and mobile sizes. Keyboard menu
open/Tab/Escape/focus return, link dismissal, reduced motion, blocked-image fallback
and no-JavaScript server content/native navigation passed. Normal homepage loading
had no console errors, canvas, GLB request or scientific API request. The actual CTA
opened the laboratory; selecting v3, Play, Pause and Reset advanced/froze/reset the
existing model as expected.

One repeated suite run reported an intermittent metadata-validation failure in the
unchanged `independent-visual.test.ts` library comparison test. Its isolated rerun
and the final complete 331-test suite passed without changing scientific code or
tests. The underlying cause was not established. No full Python suite, Lighthouse
score, Safari or Firefox acceptance is claimed for this presentation-only phase.

Git checks confirmed unchanged scientific source, model/observer/navigation/flight
libraries, fixtures, GLB, dependencies and deployment settings. Next's regenerated
`next-env.d.ts` was restored byte-for-byte to baseline after the build; it is not an
intended change.

The original v10.0/v10.1 local phase performed no publication. The subsequent
v10.1a instruction authorizes one scoped Git commit/push and a protected Preview
after its validation and deployment-safety gates, with no Production promotion.

## v10.1a visual polish

The approved identity, section order, hero specimen and scientific claims are
preserved. The abstract capability-card arena and lower illustrative chamber are
replaced with the same authentic static Lab viewport capture. `LabPreview` is a
small presentation-only client component with a reserved image area, lazy loading,
explicit static-capture caption and an image-failure fallback. The homepage still
imports no renderer or simulation runtime. Both placements reuse one cacheable URL.

Capture provenance:

- Source: the actual `/visual-lab/arena` implementation at the published baseline
  `2b9c0c7033647d0d091fc67200738aaaf28b168f`, served from a local production build.
- State: existing **Arena estática**, approved **Overview** camera, followed by ten
  ordinary OrbitControls wheel-zoom events. No simulation is run to create the image.
- Method: Chromium/CDP screenshot clipped to the real canvas bounds, 1294×718 px.
  Only HTML toolbar/caption/diagnostic overlays were hidden during capture. No scene
  geometry, lighting, materials, fly scale, model parameters or scientific output
  was changed. The image is a viewport crop, not a reconstructed or generated lab.
- Original PNG SHA-256: `5aaed584171c935068240ab2e1aa478740f89aa65b174b292aef016fafb2f0db`.
- Committed asset: `web/public/assets/site/neurofly-lab-preview.webp`, 1294×718 px,
  **20,720 bytes**, Pillow 10.2.0 WebP quality 86 / method 6, without retouching.
- WebP SHA-256: `961d0bb50e299477dc394148a86c592bd5f29c65a1db925f8a3802dde27fa109`.
- Enclosure/backdrop: original NeuroFly presentation geometry. The fly retains the
  mlykouretzos attribution above. The lab table is *Lab Table*, zeeshanfareed,
  https://sketchfab.com/3d-models/lab-table-a6585466b3bb4417bd0338c74328b209,
  CC BY 4.0. Both third-party credits and licence links appear in the footer.

Targeted readability changes raise feature descriptions to 15 px, scientific-note
copy to 14 px, footer navigation to 14 px and attribution to 12 px. Mobile labels
and secondary actions are adjusted selectively. Colours preserve AA text contrast;
contextual feature links gain an underline on card hover/focus. The hero and final
invitation retain the filled primary CTA; the lower Laboratory link becomes a
subordinate contextual action. All existing destinations remain available.

QA captures and logs are stored outside the repository in the local product-assets
work area. They are review evidence, not runtime inputs or biological measurements.

### v10.1a local acceptance

The complete frontend suite passed **332 tests** (75.7 s); the focused homepage
suite passed **18 tests**. ESLint, standalone TypeScript checking, the production
build and Git whitespace checks passed. An ES2017-incompatible regex flag in the
new asset test was corrected before the final successful build. The earlier
scientific-library metadata intermittency did not recur in this complete run.

Chromium/CDP acceptance used the production build at 1440, 1024, 768, 390 and
320 px. There was no horizontal overflow. Actual desktop/mobile screenshots were
reviewed, including the authentic Lab crop. Keyboard Enter/Tab/Escape, focus return,
anchor dismissal, reduced motion, disabled-JavaScript navigation and failed-image
fallbacks passed. Homepage inspection found one H1, no canvas, no GLB or scientific
API requests and no console errors or uncaught exceptions. The Lab CTA opened the
existing arena; v3 Play advanced, Pause froze and Reset restored step zero.
The existing `/scenarios` route also rendered all five canonical scenarios from
the real local read-only API, without substitute fixtures.

These checks concern presentation and existing UI accessibility; they add no
physiological calibration or new simulation capability. No Safari/Firefox or
formal WCAG certification is claimed. Deployment protection and Production
configuration must remain unchanged during the separately authorized Preview.
