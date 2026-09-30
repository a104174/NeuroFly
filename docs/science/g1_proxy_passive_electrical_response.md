# Phase 9B — exploratory passive G1-proxy electrical response

## Scope and decision

Phase 9B implements the Phase 9A selected family
`PASSIVE_G1_ELECTRICAL_RESPONSE` with transformation
`ABSTRACT_EVENT_TO_EFFECTIVE_MODEL_DRIVE`. This is the first deterministic
executable response downstream of Phase 8W. It is **exploratory and
uncalibrated**, not physiological NMJ validation.

The initial repository gate was clean at
`95d93f0d45d6d00abaa1db055aadcef8affcbab1`, identical to `origin/main`.
Phase 9A was committed. Required source replay succeeded before implementation;
Phase 8Y recursively replays Phase 8K/W/S/U, and Phase 8W replays its upstream
receipt/dispatch/output ancestry. No historical contract was modified.

## Sources and virtual domain

Direct inputs are only the replayed canonical Phase 8W artifact
`1a4a0e80a86945f10126ae5316b39332c55e7d2280fd0bda98c19544d69ec6fa`.
Inputs are not reconstructed from Phase 8Q/O/N. Eight source tokens across six
independent fixture runs retain their exact identities and boundary times.

The replayed Phase 8Y artifact
`030a9d22a27e4017f38d6bda166ba41515ea654c59d571f44bed2d37c7d3e3d8`
supplies proxy domain type `ttm-g1-proxy-domain-057e09a9a9c5b054f7ce`, with
kind `G1_EXPLORATORY_OBSERVATION_DOMAIN`. Its two source-association mappings
qualify the separate causal instances `800146/R` and `804642/L`.

There are two independent model instances per fixture, including inactive
controls: 12 instances and 972 stored boundaries total. Their same domain type
does not denote one shared physical fiber. Empirical observation laterality is
unresolved; model configuration sharing is
`SHARED_MODEL_ASSUMPTION_CONFIG`, not measured bilateral physiological equality.
No anatomical MaleCNS-to-G1 destination or whole-TTM state is asserted.

## Equation, state and input transformation

Model schema: `passive_g1_proxy_electrical_model_v1`.
Result schema: `g1_proxy_passive_electrical_response_v1`.
Provenance: `EXPLORATORY_G1_PROXY_ELECTRICAL_MODEL`, downstream of the source
abstract-input ancestry, with persisted Phase 8W/8Y identity and hash references.
Zero-input instances have no fabricated neural event ancestry.

For each instance, deviation `u` is `voltage_deviation_mV_eq`; reported model
coordinate `reference_voltage_mV_eq + u` is `proxy_voltage_mV_eq`.
These are voltage-equivalent **model-space quantities**, not measured membrane
voltage. No physical current, conductance or release quantity is represented.

For boundaries after zero:

```text
alpha = exp(-dt_ms / tau_effective_ms)
u[n] = alpha * u[n-1] + token_count[n] * event_scale_effective_mV_eq
proxy_voltage_mV_eq[n] = reference_voltage_mV_eq + u[n]
```

Exact exponential passive decay precedes application of all distinct tokens at
the boundary. Samples are post-input. There is no Euler approximation, neural
threshold, reset or refractory state. Before boundary zero, deviation is zero;
at boundary zero any supplied count is applied without preceding decay. The
canonical source contains no boundary-zero tokens; the numerical primitive's
zero-boundary behavior is tested independently, not represented as new source
evidence.

One valid abstract token adds one effective increment as `MODEL_ASSUMPTION`.
Count is discrete token multiplicity, not quanta, structural connectivity,
confidence, physical amplitude or release efficacy. Passive retained state is
the only history: no depression, saturation, depletion or spontaneous activity.

## Explicit reference configuration

`PassiveConfig` requires all fields explicitly. `reference_config()` constructs
the following visible reference scenario; there is no observation-derived
parameter export or hidden physiological default.

| Field | Value | Units/semantics | Classification and rationale |
|---|---:|---|---|
| `reference_voltage_mV_eq` | 0 | model-space mV-equivalent | `MODEL_ASSUMPTION`: neutral coordinate origin, not a biological resting potential |
| `tau_effective_ms` | 1 | model time, ms | `MODEL_ASSUMPTION`: simple decay spanning ten grid intervals, not a measured membrane tau or copied neural default |
| `event_scale_effective_mV_eq` | 2 | model-space mV-equivalent per token | `MODEL_ASSUMPTION`: simple positive test increment, not a published response amplitude |
| `dt_ms` | 0.1 | model time, ms | unchanged canonical source grid |
| `interval_count` | 80 | grid intervals | unchanged canonical fixture extent |
| derived `duration_ms` | 8 | model time, ms | `dt_ms * interval_count`; no independent duration ambiguity |

Initialization, positive event direction, linear summation and shared parameter
configuration are also explicit model assumptions. All three principal numeric
parameters carry serialized `MODEL_ASSUMPTION` labels. No value was fitted or
copied from Phase 8S: not −95 mV, 45 mV, 0.5 mV, 191 quanta, −10 mV or Kadas'
0.84 ms. The reference coordinate may be any finite value. Tau, event scale and
dt must be finite and positive; interval count must be a positive bounded
integer, not boolean or fractional. Serialized configuration rejects unknown
fields, inconsistent duration and changed update/assumption semantics.

The canonical runner requires exactly 0.1 ms and 80 intervals. The numerical
primitive permits valid explicit grids for equation-level testing, but source
fixtures are not retimed, interpolated or truncated. Nonfinite outputs are
rejected. Computation uses Python binary64 floats and fixed iteration order;
bitwise replay is protected on the repository runtime. No stochastic process,
random initialization or seed exists; cross-runtime math-library differences
would require explicit reproducibility review, not silent hash acceptance.

## Timing and instance accounting

All token steps and times must match the source grid and proxy association.
The existing `ZERO_ADDED_MODEL_DELAY_ASSUMPTION` is preserved. This does not
assert zero biological neuromuscular delay; no numerical NMJ-delay parameter
exists. Kadas' composite interval is not used.

| Fixture | Token boundaries | Model outcome |
|---|---|---|
| `ZERO_EVENT_CONTROL` | none | both instances exactly at reference for all 81 boundaries |
| `RIGHT_SINGLE_EVENT` | R: 10 / 1 ms | R peaks at 2, then decays; L stays at baseline |
| `LEFT_SINGLE_EVENT` | L: 10 / 1 ms | L peaks at 2, then decays; R stays at baseline |
| `BILATERAL_SIMULTANEOUS_EVENT` | R/L: 10 / 1 ms | independent instances each peak at 2; no merging or coupling |
| `RIGHT_REPEATED_EVENTS` | R: 10, 30 / 1, 3 ms | residual plus second increment; L stays at baseline |
| `LEFT_REPEATED_EVENTS` | L: 10, 30 / 1, 3 ms | residual plus second increment; R stays at baseline |

Peaks and final deviations are in model-space mV-equivalent. Single-event final
deviation is `0.0018237639311090255`; repeated-event peak at step 30 is
`2.270670566473225`, with final deviation `0.015299657929279913`. The finite
8 ms window is not forced to reach baseline and no tail clamp/reset is applied.
Aggregate counts are 8 tokens, 4 per body across independent fixtures—not a
biological firing rate or transmission reliability estimate. Repeated inputs
spaced 2 ms are not the literature's 1-Hz protocol.

## Behavior tests, not biological validation

Focused gates cover exact zero/baseline, closed-form single response
`q * alpha**k`, monotonic post-event decay, linear repeated-event superposition,
no left/right leakage, distinct source/instance identities, exact token timing,
boundary zero, multiple events at one boundary, scale proportionality and
slower decay with larger tau. Equation-level sensitivity tests are not the
Phase 9C experiment and do not compare against biological observations.

Replay rejects source identity/schedule changes, proxy mutation, invalid
configuration/order, altered trajectory/fixture/token linkage, hashes and
artifact IDs. Even a trajectory mutation with freshly recomputed result hashes
fails reconstruction. Canonical identities and ordering are pinned in tests.
No observation operator, comparison metric, acceptance tolerance or fit exists.

## Artifact and offline CLI

Artifact schema: `g1_proxy_passive_electrical_response_artifact_v1`.

- ID: `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f`
- Config hash: `d3807d88f777e8f6754a8e3aab591e42b643974e7417451509771581d7c013d0`
- Result hash: `fa11b093b1a3013d397bb459c3c1f39b1a96543b8380a792e89dc0bdfa8e91d8`
- Size: 37,535 bytes, including manifest.

Generated data is Git-ignored under
`data/derived/malecns/looming_giant_fiber_v1/` plus artifact schema and ID.
`response.json` stores shared grid columns, independent instance trajectories,
source-token references, config/source identity and deterministic summaries.
`manifest.json` pins file length and SHA256. Identity depends on model/config,
source tokens/proxy and resulting trajectory. The source-authority runner only
accepts the pinned canonical input/domain identities; a changed source requires
an explicit later version, not a permissive import.

```sh
python -m neurofly.g1_proxy_passive_electrical_cli generate
python -m neurofly.g1_proxy_passive_electrical_cli inspect ARTIFACT_DIRECTORY
python -m neurofly.g1_proxy_passive_electrical_cli replay ARTIFACT_DIRECTORY
```

The CLI generates the explicit reference scenario, not an unspecified default
parameter search. Programmatic configuration is explicit. No fitting or
comparison command exists. Inspect shows assumptions, source identities,
token boundaries, peak/final model deviation and scientific limitations.
Generation stages files, verifies reconstruction, then publishes an immutable
content-addressed directory; existing destinations must replay rather than be
overwritten. Replay checks canonical bytes, manifest, directory identity,
Phase 8W/8Y replay and exact model reconstruction. No network, PDFs or literature
lookup is required. Offline behavior is tested with network connections denied.

## Historical and scientific boundaries

Phase 8W remains class-level/amplitude-free; Phase 8Y remains metadata-only and
side-agnostic. Its historical no-model snapshot is not changed by this later
implementation. Phase 8S remains empirical authority, not a model parameter
source. Phase 8U remains zero formal-ready mappings: a model-space trajectory
does not supply an observation operator, protocol match or calibration.

There is no production sensory composition or upstream retuning, DLM work,
current/conductance/release/vesicle model, exact anatomy, whole-TTM activation,
contraction, force, mechanics, behavior, frontend or HTTP API change.

Permitted claim: NeuroFly computes deterministic exploratory G1-proxy
electrical trajectories from abstract TTM input tokens using explicit
uncalibrated model assumptions. It does not simulate validated biological NMJ
transmission or establish G1 physiological agreement.

## Next bounded Phase 9C

Run one model-assumption sensitivity/identifiability experiment: sweep event
scale and effective tau at 0.5×, 1× and 2× the reference values (nine cells),
holding reference coordinate, inputs, domain and grid fixed. Report reproducible
model trajectories, superposition, peak/final deviations and qualitative
parameter degeneracies—not empirical errors, fitted parameters or biological
acceptance. No such sweep is implemented in Phase 9B.

## Verification and final decision

- Focused Phase 9B suite: 45 passed.
- Full `python -m pytest`: 726 passed, 1 deselected, 2 existing deprecation
  warnings, in 315.43 seconds.
- `python -m ruff check .`, `python -m ruff format --check .` and
  `git diff --check`: passed.
- Frontend regression: 38 tests passed; lint, typecheck and build passed.
  The build-generated type-import rewrite was restored; frontend source is
  unchanged.
- Canonical artifact offline replay passed; generated files remain Git-ignored.
- Historical Phase 8W/Y/U/S replays passed unchanged. Phase 8U remains zero-ready.

Decision: `FIRST_EXPLORATORY_G1_ELECTRICAL_MODEL_VALIDATED`.
Phase 9B: **PASS**, meaning software/model-form validation only, not empirical
G1 validation. No commit or push was performed.
