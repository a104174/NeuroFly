# V10.8B-P — V10.6B frozen dependency boundary

V10.6B's authoritative protocol is commit
`e8ed01f32d4651871d43c4105eb929317325e249`. Its complete configuration remains
byte-pinned by SHA-256
`dbc0f37db7a614c1a1076041f6319999bb86e7414b17a21992a8797e43f4a392`. The
execution wrapper was added later, with the V10.6B results at
`31b8085f0a7e27137d665360246d9823050483d6`; a current reproduction records its
actual execution commit and wrapper hash.

## Protected inputs

The frozen runner's runtime import closure contains the continuous navigation,
interactive neural locomotion, neural contribution comparison, causal report,
experimental locomotion, neural locomotion, neural steering comparison, arena,
fly viewer, visual manifest parser/instance and node-identity modules listed in
`web/scripts/frozen-contribution.ts`. Their complete file bytes are compared
with the protocol commit. The closure also pins `web/src/assets/fly_visual_v2f.json`
to the protocol bytes and SHA-256
`6a3d05441afd0c25ed8c2a98472acc35601f6e525db6f74d4eb16b0e32ab3b9e`.
The package manifest, lockfile and TypeScript resolution configuration are
also pinned because they define the installed and aliased module environment.
The protocol document, frozen configuration and locomotion authority artifact
remain pinned. Runtime v3, the MaleCNS morphology manifest and all eight SWCs
retain their existing expected-hash checks.

The closure was traced from the wrapper's five explicit runtime entry imports,
then checked through literal runtime imports with the repository TypeScript
resolver. Type-only imports are excluded from the runtime closure. The
locomotion bounds check reads the fly visual manifest's anchor and bounds;
this is why the manifest is now checked in full. `engineeringFlight.ts` is not
reachable from these imports and is not part of the protected file list.

## Guard behavior

Before loading the frozen scientific modules, `--check` and normal execution
compare every listed file's historical bytes with both the Git index and the
working tree. A changed or deleted staged file, unstaged file, configuration,
asset or dependency therefore fails with a file-specific diagnostic. The
runner verifies its explicit delayed-import list and resolves each protected
module's local runtime imports. An untracked or newly tracked same-specifier
candidate that could shadow a frozen import is rejected unless that candidate
already existed with identical bytes at the protocol checkpoint. A new
unrelated source file, including an independent flight controller, is allowed.

The check rejects `TSX_TSCONFIG_PATH`, `NODE_PATH`, and Node loader hooks in
`NODE_OPTIONS`. Scientific modules are dynamically loaded only after these
ordinary preflight checks; this ordering makes drift failures actionable. It
is not a Node security sandbox. It does not claim protection against a
deliberately compromised runtime, arbitrary loader manipulation, modified
installed package contents, or hostile code changing the guard itself.
Resolution verification is a bounded static check using the pinned TypeScript
configuration and installed resolver, not a formal proof of all possible
runtime behavior.

## Regression and future changes

The frozen runner's `--check` command is exercised in disposable Git clones.
Tests cover unchanged inputs, neural/locomotion/intervention drift, changed,
malformed and deleted visual manifest, index-only and working-tree changes,
configuration drift, new shadow candidates, protocol-reference substitution,
and simultaneous protected plus independent-flight changes. They also verify
that edits to `engineeringFlight.ts` and unrelated files pass.

A future change to a frozen dependency should be made only as a separately
reviewed scientific protocol revision with new provenance and validation. Do
not update the V10.6B reference commit or expected hashes to make a changed
implementation pass. A newly required local runtime import must be reviewed,
added to the explicit closure, and accompanied by updated integrity tests;
until then the guard rejects it.
