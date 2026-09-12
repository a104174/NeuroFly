# Read-only frontend foundation (Phase 5A)

Phase 5A adds the first browser vertical slice without changing the Python
scientific core or the Phase 4B HTTP contract.  It is a small Next.js App
Router application under `web/`, using React and TypeScript.  It discovers
completed artifacts, links to an experiment detail route, displays provenance
and separate pathway/output summaries, and loads the persisted timeline.

## Dependency direction

```text
Next.js server components
    -> web/src/lib/neuroflyClient.ts
    -> Phase 4B GET /api/v1
    -> Phase 4A DTOs / Phase 3B artifacts
```

The browser does not import Python, NumPy, dataclasses, artifact paths,
CircuitContract files, simulator code, or encoder logic.  There is no Three.js,
React Three Fiber, charting library, state-management framework, or live
simulation in this phase.

## Runtime configuration and HTTP

The server-side client reads one setting:

```text
NEUROFLY_API_BASE_URL=http://127.0.0.1:8000
```

See `web/.env.example`.  The variable is server configuration, not scientific
identity.  Next.js server components fetch the FastAPI service with
`cache: "no-store"`, so Phase 5A does not require CORS or a permissive browser
proxy.  A missing or invalid URL is rendered as an explicit API error; the
application never switches to mock data.

The expected transport and application schemas are respectively
`experiment_http_v1` and `experiment_api_v1`.  Unknown schemas, invalid
required fields, altered validation status, and inconsistent timeline lengths
are rejected by the typed client runtime guards.

## Browser routes and states

- `/` loads `GET /api/v1/experiments`, showing a compact completed-run
  catalogue.  Empty results are an intentional empty state.
- `/experiments/[artifactId]` loads the summary and timeline for one artifact.
  Missing artifacts use a not-found state; unavailable/corrupt responses use
  a non-leaking error state.

Loading copy says “Loading experiments…” or “Loading experiment…”; it never
implies that a simulation is running.  The UI remains read-only and has no
parameter controls or POST path.

## Scientific fields preserved

The detail page keeps all five free quantities separate and unit-labelled:

- `G_LC4` (`mV_eq`);
- `G_LPLC2` (`mV_eq`);
- `omega_half` (`rad/s`);
- `theta_half` (`rad`);
- `k_syn` (`mV_eq/contact`).

LC4 and LPLC2 have independent population panels.  DNp01 bodies `10001` and
`10010` have independent output panels.  `NOT_EVALUATED` is displayed as
“Empirical validation — NOT EVALUATED”; it is never renamed to validated,
healthy, accurate, or biologically correct.

The page preserves `structural_weight` as a connectomic structural contact
count and `event_increment_mV_eq` as a NeuroFly model transform.  It does not
interpret either as physiological synaptic efficacy or behavior.

## Timeline boundary

The timeline inspector consumes the exact Phase 4A arrays: simulation
boundaries (`times_ms`), interval starts (`step_times_ms`), angular size and
expansion velocity, normalized LC4/LPLC2 features, and both drives.  It reports
sample/interval counts and unit-preserving peaks as presentation summaries.
State values remain boundary samples; drive/features apply on
`[t_n, t_n + dt)`.  No interpolation, time shifting, render-FPS resampling,
or browser-side scientific recomputation is introduced.

Future 3D playback may render these values at an independent frame rate, but
simulation time and render time must remain separate.  `requestAnimationFrame`
does not advance the scientific experiment in Phase 5A.

## Development

From `web/`:

```bash
npm install
npm run dev
npm run lint
npm run typecheck
npm test
npm run build
```

The committed `package-lock.json` fixes dependency resolution.  Generated
`node_modules`, `.next`, coverage, local environment files, and build output
are ignored.  The backend must be running separately with its configured
artifact root for a real experiment to appear.
