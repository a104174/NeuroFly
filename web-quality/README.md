# NeuroFly web quality checks

Automated checks for the redesign acceptance criteria (`docs/redesign-brief.md`, section 11). They live
here, outside `web/`, because `web/package.json` and `web/package-lock.json` are pinned by the frozen
scientific protocol (`scripts/frozen-contribution.ts`): adding a dependency there fails five tests.

```bash
cd web-quality
npm install
npm run install:browsers        # downloads Chromium once, or set CHROME to an existing binary
# start the API and the web app (see the repository README), then:
BASE=http://localhost:3000 npm run check          # routes, a11y, read-only, keyboard, motion, resilience, bundle
BASE=http://localhost:3000 npm run check:lighthouse
npm run lint:css                                   # hard-coded colours outside tokens.css
```

What each group checks, and which section 11 row it covers:

| Group | Section 11 row |
| --- | --- |
| `routes` | Regression: all existing routes resolve; unknown IDs are real 404s |
| `a11y` | Automated accessibility (serious or critical, both themes); Responsive (no page-level horizontal scroll at 360, 390, 768, 1024, 1440, 1920) |
| `readonly` | Read-only: only GET, HEAD or OPTIONS during a full run (the one named Server Action is allowed) |
| `keyboard` | Keyboard: skip link, Cockpit slider by keyboard, visible focus |
| `motion` | Reduced motion: no autoplay, motion tokens zero |
| `resilience` | 3D resilience: WebGL off, context lost and restart |
| `bundle` | Bundle: three.js not loaded on pages without 3D |
| `lighthouse.mjs` | Lighthouse mobile: accessibility 95+, performance 90+ on Home, lists and Science |
| `check:unconfigured-morphology` | Optional: run against an API with no morphology root (like production today). Neurons and the Cockpit must say "Neuron shape data is not available on this deployment.", not that the data service is down |
| `lint:css` | Tokens: hard-coded colours outside the tokens file. Legacy files still fail; see `docs/redesign-progress.md` |

Not automated (need a person): screen reader paths, frame rate on the reference laptop, greyscale review,
device test of the phone Cockpit.
