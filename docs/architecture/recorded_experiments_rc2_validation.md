# v10.4b RC2 — validation gates and candidate source closure

Baseline: `a5aeea83722ea7fc8aa011b0d1e73065b99881c2`.
Local test-infrastructure verification only; no publication or scientific changes.

## Gate A: frontend dependency scope

The existing guard banned the Python proxy module name in every `web/**/*.ts`
file. `web/tests/science.test.ts` contains that name in a string identifying a
scientific evidence source, not an import or executed neural dependency. The
published baseline already contains this reference. No production frontend
dependency was found.

The narrow test-only correction separates `web/tests/*.test.ts`, the test entry
points selected by `web/package.json`, from frontend source. The original raw
reference ban still covers every other TypeScript file previously inspected,
including application source, scripts, source files named `*.test.ts` and
non-entry-point helpers under `web/tests`. The Python body/motor dependency guard
is unchanged. This is not a file-specific exception for the Science test.
Five additional regression cases accept evidence in a test entry point and
reject prohibited imports in each of those retained source categories.
No neural, motor, Science-page or runtime implementation is changed by RC2.

## Gate B: prospective tracked tree

The D2 validation helper intentionally copies Git-enumerated application source.
In the real, unchanged index, the newly authored
`src/neurofly/recorded_experiments_runtime.py` does not yet exist. Thus the old
helper's isolated application cannot import it. This is a pre-publication index
state, not evidence that the runtime archive lacks a scientific payload.

Validation uses an external `GIT_INDEX_FILE` and external object directory based
on HEAD plus an explicit candidate path manifest. No scientific payload or
excluded local file is added to that index. The normal index stays untouched.
The resulting tree is exported outside the checkout. Scientific inputs for its
tests are provisioned separately from the frozen v2 archive plus the authentic
five-file reference, never copied as part of Git source or regenerated.

The unmodified D2 clean-bundle test must pass with this complete source set,
including its existing deny-network, deny-checkout-data and deny-runtime-write
checks. The canonical suite uses the same candidate index for helpers enumerating
Git source. No production packaging change, path fallback, staging in the real
index or commit is needed to test the prospective release tree.

## External workbook coverage

Eight cases in `test_horizontal_visual_motion_contract.py` require the official
`/tmp/neurofly-v9-2a/figure1.xlsx`. Eleven cases in
`test_empirical_hs_dnp15_benchmark.py` require `NEUROFLY_FIG1_SOURCE`.
These are separate historical empirical/visual-input gates, not dependencies of
the recovered Recorded Experiments reference or its runtime inventory. Existing
fixtures explicitly skip when the workbook is absent; the canonical marker only
excludes authenticated integration tests. No workbook is fabricated, downloaded
or substituted, and no scientific fixture requirement is weakened.

## Results

Results and hashes are recorded outside Git under the sibling assets directory,
`work/v10-4b-rc2/`:

- Original Gate A plus its five new cases: six passed.
- Exported candidate source: 50 passed, no failures or skips, including the
  unchanged D2 clean-bundle test, v3 recovery, authentic replay, canonical
  playbacks and negative integrity cases. Package imports resolve inside the
  exported candidate; the native closure retains its existing offline/write
  guards.
- Complete canonical Python selection using the temporary candidate index:
  1,825 passed, zero failures, 19 existing external-workbook skips, one integration
  deselection. Eight disjoint module partitions account for all 1,844 selected
  cases; no selected case is omitted or counted twice. This does not claim that
  an ordinary run with the unchanged real index already enumerates new files.
- Full frontend: 367 passed, no failures/skips. Ruff check and format check,
  ESLint, Typecheck, production build and whitespace checks passed. The build's
  generated-only `next-env.d.ts` import rewrite was compared and its original
  bytes restored.

Runtime v2/v3 archives, inventories, manifests, scientific payloads and the
engineering/UI reference's `NOT_EVALUATED` classification remain immutable.
The only RC2 implementation change is the test guard and its regressions; this
document is the only additional RC2 file. The normal index still contains exactly
HEAD's paths, blob IDs and modes, with no staged changes. Git may refresh its
internal stat cache during inspection; no real-index staging operation occurs.
No application, packaging, Blob/OIDC, deployment or Production change is made.
