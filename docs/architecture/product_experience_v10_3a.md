# NeuroFly v10.3a — Explore and recorded experiments

Local presentation work on `3497f9fbd62eec22a03e0ffcfba3ebcaf3c176e5`.
The discovery journey is Home → Explore → experiment details or Lab. Completed
scientific runs remain a separate collection. No scientific execution, schema,
storage, replay, parameter, asset or deployment configuration is changed.

## Route ownership and inventory

`/scenarios` still calls `listScenarios()` once through the existing no-store,
validated API contract. Five IDs in the established order remain authoritative.
Friendly labels only describe them; backend titles and caveats stay available in
Model context. The source catalog must be complete and valid before any cards
are shown. Unavailable/empty/malformed catalogs remain errors, with a Lab link.

| ID | Discovery title | Existing action and scope |
| --- | --- | --- |
| `BASELINE_CONTROL` | Begin with stillness | Open preset details; 1.4 ms neutral control, stationary body |
| `LOOMING_CIRCUIT_VALIDATION` | An approaching object | Open preset details; 1.4 ms visual-circuit probe, subthreshold canonical output |
| `LOOMING_WORLD_EXPERIMENT` | A changing field of view | Open preset details; 40 ms prescribed model-space approach |
| `HORIZONTAL_MOTION_NEURAL_VALIDATION` | Motion into neural activity | Open preset details; 50 ms HS/DNp15 neural-only response, no body mapping |
| `EXPLORATORY_COURSE_CONTROL` | A turn through feedback | Open preset details; 50 ms orientation feedback, no translation |

All links retain `/scenarios/{id}`. The unchanged details page explicitly loads
and validates a canonical replay on request. Existing `?replay=canonical` refresh
semantics remain. The catalog itself runs no solver, playback or WebGL scene.
Interactive ground exploration is a separately labelled Lab feature, not a sixth
canonical scenario or a relabelled prerecorded experience.

`/experiments` still calls `listExperiments()` with the existing parser and error
mapping. It lists scientific-core artifacts exposed by the configured read-only
API, not a user's cloud account or the browser's IndexedDB session library.
There are no timestamps in the summary contract; none are invented. API ordering,
artifact IDs, candidate identifiers/versions, duration, dataset, integration
interval and `NOT_EVALUATED` validation status are preserved. Candidate labels
are humanized for display; source strings remain in Run identity.

Inspect run and Scientific cockpit retain their existing URLs. Their four
back-to-collection links now return to `/experiments`, correcting the older
links to the homepage. Replay, timeline, export and invalid-ID handlers are not
changed. `ExperimentList` and all historical scientific presentation components
remain available. The 15-mode research archive is unchanged.

## Presentation boundaries

`DiscoveryShell` composes existing `SiteHeader`/`SiteFooter`, white `BrandLogo`
and skip link. Explore remains the primary discovery destination; `/experiments`
is linked from the footer as a secondary route. Existing detail and cockpit links
remain intact. `discovery.css` uses only `.nf-discovery` selectors. Two small
route layouts load it without editing global CSS or the pre-existing changed
`scenarios.css`. Nested research/detail pages do not have the scope class.

`ScenarioDiscovery` uses the existing `LabPreview` static WebP and its image-error
fallback. The approved image and original attribution remain unchanged (Lab Table
by zeeshanfareed and fly by mlykouretzos, CC BY 4.0; see the existing homepage
asset documentation). No new raster assets or downloads are introduced.
The five inline SVG marks are labelled conceptual diagrams, not data or measured
neural traces. They illustrate neutral input, approach, a pathway and feedback;
they are not anatomical connectivity diagrams or scientific results.

`RecordedExperiments` keeps empty and failure states separate. A valid zero-item
response explains that Lab activity is not automatically saved here. Integrity,
network and schema failures produce an explicit alert, never an empty collection
or substitute records. The unavailable state points visitors to the Lab and
keeps the safe mapped diagnostic in a closed `Technical details` disclosure.
Loading uses a distinct native status and busy state. Browser-local saved sessions
remain in the research tools' existing library.

Both pages have one H1, progressive native disclosures, keyboard navigation,
visible focus, touch targets, reduced-motion rules and descriptive image text.
The layout adapts at tablet/mobile widths; there is no search/filter mechanism
for five items, extra client store, animation library or new dependency.

## Validation and practical limits

Canonical commands from `web`:

```sh
PATH="/path/to/NeuroFly/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 npm test
node --import tsx --test tests/discovery.test.ts tests/homepage.test.ts tests/branding.test.ts
npm run lint
npm run typecheck
npm run build
```

Focused tests cover ID/route identity, immutable presentation, real API parsing,
zero/one/multiple transport cases, ordering and run links, failed integrity,
branding/navigation, loading and corrected return paths.
Transport fixtures reuse the established API test shape; they are not biological
observations. Existing homepage/catalog and branding expectations track the new
presentation while retaining all invalid/empty/incomplete/network/integrity
rejection assertions. No scientific tests are weakened.

Final local frontend suite: 357 passing tests, including the focused tests.
ESLint, typecheck, production build and whitespace checks passed. One intermediate full run reproduced the previously observed local-library metadata flake (356/357). The unchanged library suite then passed 8/8 in isolation, and the final full rerun passed 357/357. No test was changed, skipped or weakened to suppress that failure; its underlying cause is not established by this UI phase. The full Python
suite is not required or claimed for these presentation-only changes; existing
frontend tests also exercise Python neural/observer parity and canonical replays.

Chromium/CDP used 320/390/768/1024/1440 px for both pages, with no horizontal
overflow. All five actual scenario links opened their preserved details. The
canonical course replay loaded and survived refresh. Menu Enter/Tab/Escape and
focus restoration, native disclosures, reduced motion and image-error fallback
passed. The Lab link reached the same single-canvas Explore runtime and its
Play/Pause/Reset controls. Research still displayed all 15 selectors.

The configured local artifact API and the authenticated Vercel Preview both
return the pre-existing HTTP 409 `artifact_integrity_failure` for
`GET /api/v1/experiments`. The updated page explains that the collection could
not be verified and keeps the safe mapped message in a closed disclosure. The
endpoint calls `ExperimentArtifactStore.list_experiment_summaries()`, which
loads every artifact directory through the Phase 3B loader before returning a
list. `_load_error` maps validation failures to `CorruptedArtifactError`, and the
HTTP handler returns only the generic 409 code/message. The response does not
identify the artifact or distinguish a payload/manifest hash mismatch from
another schema or integrity failure. This issue is present in the current
Preview data environment, not only local development; its precise artifact-level
cause remains unresolved. The smallest follow-up is a read-only inventory of the
deployment's existing artifact files against their manifests, followed by a
separately reviewed repair from authoritative source data if a specific defect
is confirmed. This release does not alter the validator or archive.
An independent instance of the same API factory over a genuinely empty disposable
artifact directory returned HTTP 200 with zero records; its real empty-state page
was inspected in Chromium. No artifacts were created. One/multiple populated
collections are verified by parser/route/render tests, not claimed as successful
real-data browser runs. Repairing the old artifacts is outside this UI phase.

Screenshots and browser evidence are external QA outputs, not runtime inputs.
Visual checks use software Chromium and do not claim hardware GPU performance,
Safari/Firefox acceptance or a formal accessibility certification. The existing
Three.js clock deprecation warning may appear in scientific 3D views.

Preservation checks retain the five pre-existing local paths, 218 frozen
scientific/library/asset identities, 74 pinned D2.2 file identities, all scientific
engines, approved imagery and the GLB. The finalization change is presentation-only:
it preserves the API, validator, artifact schemas, historical research tools and
scientific execution paths. The precise integrity-failure cause remains for a
separate data-provenance investigation.
