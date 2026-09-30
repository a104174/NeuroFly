# Phase 13A — first deterministic closed-loop scenario architecture

## Decision and scope

Select `LOOMING_CIRCUIT_VALIDATION`: one backend causal tick runner, an explicit
unregistered world→relative-column projection, all 311 identity-resolved
sensory states, genuine downstream production composition and authoritative
planar body feedback. Include an object-disabled Baseline control in the same
Phase 13B implementation. Do not require nonzero movement for success.

This document is a decision, not a scenario implementation. Phase 13A adds no
code, schema, artifact or API. No neural tuning, biological research, scripted
escape, LLM control, physical calibration or frontend changes are authorized.

The Project Context strategic taxonomy remains unchanged: Baseline; Light /
Dark; Obstacle Course; Resource Search; Adversity / Avoidance; Changing World.
Looming is an initial **circuit-validation scenario**, not a replacement for
those product worlds. Baseline is a zero-stimulus control, not an additional
phase or a claim of baseline biological locomotion.

## Repository gate and verified history

Started clean at `8b269747761f5eb480543116ea5457a6c92b03d2`, main equal to
origin/main. Phase 12B, 11B, 10B, 9B, 8C and 7O are committed.

Required source validation succeeded:

| Phase | Artifact ID | Verification |
|---|---|---|
| 12B | `bb3696faae558778555601991de3fd36081d5853c889fcb7aac5ffd79593eba3` | numerical offline replay |
| 11B | `478b4a9d4b089dc0a0fffdb699f8bbab1c7483eddf2eed0a8b06185b48b04d40` | recursive replay through 12B |
| 10B | `4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb` | recursive replay through 11B |
| 9B | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` | recursive replay through 10B |
| 7O | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` | full execute_311 recomputation equals persisted config/result |
| 8C | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` | genuine persisted 7O source and motor replay |

All 35 Phase 7O conditions have zero DNp01 spikes. Phase 8C has zero inputs and
zero states for 800146/R and 804642/L. Later canonical motor-output,
electrical, activation, actuator and body fixtures have synthetic ancestry.
There is no genuine production actuator/body artifact. Validating synthetic
body movement did not compose or activate the genuine path.

## Actual runtime and infrastructure audit

| Existing implementation | Capability | Phase 13B reuse boundary |
|---|---|---|
| `malecns/sensory.py` | LoomingStimulus.sample is pointwise analytic geometry | Its existing API labels distances in m and velocity in m/s; do not feed world_eq into those fields |
| `sensory_encoder.py` | Level P angular-size/expansion encoding into graph drive schedules | Different path; not selected as a replacement for 311 relative-column states |
| `relative_column_assignment.py` | RelativeColumnStimulus plus active_column_set and compute_body_exposure | Reuse spatial primitives at each boundary with pinned columns/body records |
| `relative_column_sensory_dynamics.py` | integrate_exposure_values is a batch exact-decay held-exposure filter | Extract its pure state transition and use it from both old batch and scenario tick execution |
| `relative_column_dnp01_transfer.py` | route_population_drive is pointwise, source-order routing | Reuse all 311 anatomical routes; no structural-contact multiplier or population normalization |
| `bounded_sensory_population.py`, `sensory_population_execution.py` | Batch assignment/filter/transfer/LIF manifests | Load pinned population/routing/configs, not precomputed sensory trajectories as scenario drive |
| `simulation.py` | LIFSimulator.run owns an interval loop, event queue, refractory state and SpikeEvent generation | Expose an initialized stepping core retaining the exact arithmetic/order and have run use it; no rewritten LIF equation |
| `motor_pathway.py` | event conversion and batch _integrate_ttmn | Reuse source/target identity and extract decay-then-boundary-event transition |
| `synthetic_ttmn_output_rule.py` | _crossing_steps uses previous < 0.25 <= current | Extract the same pairwise crossing predicate; no new threshold or generator policy |
| `model_derived_ttmn_target_dispatch.py` | Phase 8K association lookup, dispatch payloads | Reuse association validation and semantic record construction; historical entry point stays fixture-pinned |
| `ttm_neuromuscular_input_receipt.py`, `ttm_abstract_electrical_input.py` | validated dispatch→receipt→token semantics | Factor source-identity-aware constructors; old wrappers remain pinned to old artifacts |
| `g1_proxy_passive_electrical.py` | integrate_counts exact decay then token increment | Extract its boundary update; retain reference 0/1 ms/2 mV_eq and 8Y proxy |
| `muscle_activation.py` | activate_samples is already a pure static transformation | Reuse with scale 10 mV_eq, no activation kinetics |
| `ttm_actuator.py` | two side-preserving passthrough routes, canonical artifact guards | Factor functional routing from fixed-artifact validation, preserving exact identity and command |
| `planar_body_plant.py` | pure integrate_commands plus synthetic canonical-source guards | Factor/reuse its interval transition; preserve common mean, gain 1, fixed x and heading |

Existing public artifact runners generally are **not** generic production APIs.
For example Phase 8W admission accepts only a pinned receipt subset, its token
constructor embeds a historical source ID, and 11B/12B guards require fixed
synthetic identities/grids. Passing a scenario through these wrappers would
either fail correctly or fabricate ancestry. Do not disable those guards.

The bounded adapter work belongs inside the one executable 13B slice: separate
pure semantic/numerical kernels from historical batch envelopes; add new
scenario-owned provenance envelopes with real event parents. Historical
wrappers retain exact payloads, source restrictions and artifact IDs. Do not
populate `source_synthetic_run_id` with a genuine scenario ID or claim a new
token belongs to the old Phase 8W artifact. No generic event/plugin framework
or simulator rewrite is needed. Stop if extracting kernels cannot preserve
historical replay exactly.

FastAPI currently serves persisted experiments, timeline/body/spike/event data,
motor experiments, morphology and connectivity; no world runtime or WebSocket/
SSE scenario transport was found. ExperimentRunner and LIFSimulator are batch
scientific execution, not a live world scheduler. Canonical artifacts already
provide deterministic JSON/hash/manifest/replay conventions.

The frontend experiment/cockpit routes fetch persisted run data. Playback uses
requestAnimationFrame to advance a presentation clock over stored timelines;
it is not neural integration. FlyVisualAsset uses static presentation transforms.
There is no authoritative frontend body plant to replace. Scenario/body/object
data is not currently part of the client contract.

## Alternatives

| Candidate | Assessment |
|---|---|
| BASELINE_NEUTRAL_ARENA | Valuable zero control but does not exercise looming; include object-disabled control with selected runner |
| LOOMING_CIRCUIT_VALIDATION_ARENA | Selected: relevant to LC4/LPLC2→DNp01(GF), small world state and testable body-relative expansion |
| LIGHT_DARK | Strategic world retained; no equivalent validated illumination-to-311 model exists |
| PREDECLARED_RELATIVE_COLUMN_STIMULUS_SCENARIO | Replays neural input but remains open loop if body cannot alter future stimulus |
| HOLD_UNTIL_WORLD_TO_SENSORY_REGISTRATION | Required for calibrated retinotopy, not for explicitly exploratory fixed-centre projection |

World→sensory options:

- Existing angular encoder: bounded size/expansion features drive selected
  visual graph nodes and then LIF, not the validated 311-body anatomical-
  exposure/filter/transfer path. Easier composition does not justify this bypass.
- Absolute bearing-to-column registration: not verified; cannot be asserted.
- Fixed schedule: not closed-loop body feedback.
- Selected fixed-column projection: source-valid centre/side are declared;
  world-relative distance determines angular ratio and discrete lattice radius.
  Bearing-to-retinotopy is deliberately absent. No claim of biological receptive
  fields. All 311 states exist even when the other side receives zero exposure.

Existing analytic geometry computes full angular diameter `2*atan2(radius,
distance)`, angular expansion velocity, approach/collision status and time to
collision for a prescribed line-of-sight object. It is physically named and
already connected to Level P encoding, **not** to the 311 path. A dimensionless
size/distance ratio is valid in world_eq without making those coordinates m.
13B should factor/reuse a unit-neutral angular geometry primitive as appropriate,
leaving the physical LoomingStimulus interface and historical behavior intact.
No time-to-contact or physical expansion calibration is needed by this projection.

## Proposed minimal canonical world and projection

One object, planar fixed-heading body, no walls, gravity, contacts or steering.
Use 14 intervals, 15 boundaries, dt 0.1 ms: the existing 7O reference bilateral
window (1.4 ms), not the synthetic downstream fixtures' 8 ms window. This is
a short circuit-validation run, not a behavioral timescale or duration tuned
until movement appears. The common dt avoids multirate scheduling.

Proposed explicit reference MODEL_ASSUMPTIONs for 13B:

| Quantity | Reference | Rationale |
|---|---|---|
| Initial body x/z | 0/0 world_eq, heading +Z | unchanged plant reset |
| Object x/z | 0/4 world_eq | a simple positive, pre-contact forward separation |
| Object radius | 1 world_eq | unit model-space size, not fly/object physical dimensions |
| Prescribed object x/z velocity | 0/-1 world_eq/ms | unit normalized approach, no object dynamics |
| Projection side/centre | R, hex (23,9) | reuse existing `right_expand_23_09` centre, not outcome-dependent selection |
| Half-angle→lattice scale | 10 lattice steps per radian | explicit round-number projection assumption, not measured retinotopic spacing |
| Radius discretization | floor, nonnegative integer | deterministic quantization, not biological sampling |

At boundary n, object position is prescribed from initial position plus
velocity times `n*dt_ms`; it is independent of the fly. Relative dx/dz are
object minus authoritative body position; distance d is hypot(dx,dz).
Require finite geometry with object ahead and positive separation throughout
the run; stop/classify unsupported geometry on violation, never add collision
or scripted motion. With canonical stationary body, separation stays positive
(4→2.6). No inferred retinal bearing or side switch.

Let `half_angle = atan2(radius_world_eq, d_world_eq)` and
`radius_lattice_steps = floor(10 * half_angle)`. The ratio is dimensionless;
angles are mathematical geometry, not a calibrated retina. The canonical
stationary trace changes disk radius 2→3 as the object approaches. This is
not selected from neural outcomes. Body motion toward +Z reduces forward
separation and may increase expansion—**not escape/avoidance semantics**.

For the selected side use existing active_column_set and column-overlap-
fraction exposure (not structural input-site weighting). Other-side exposure
is zero. Baseline uses an explicitly empty active set/no stimulus, **not**
radius zero, which could still expose the centre column. No changes to sensory
gain/tau, transfer or threshold. Discretization can leave adjacent projected
radii equal despite changing geometry; report this rather than inventing
continuous exposure or pretending every body shift changes retinal input.

## Exact causal boundary semantics

The naive order “advance sensory, advance DNp01, then use the new spike for the
current body interval” would move spikes backwards in time. Existing sensory
boundary s[n] drives DNp01 interval n→n+1; new sensory exposure e[n] produces
s[n+1], and new DNp01 spikes occur at n+1. Preserve both contracts.

Initialize at boundary 0: body/object reset, sensory states zero, DNp01 at its
existing initial membrane/synaptic/refractory state, motor/electrical zero.
No startup spike, crossing or token is invented.

For each boundary n:

1. Read authoritative body[n], prescribed object[n], sensory s[n] and DNp01
   state/spikes[n] emitted by the preceding neural interval (none at zero).
2. Compute/store relative geometry, projected disk and all 311 exposure e[n].
3. Route only genuine DNp01 spikes[n] through the existing ipsilateral motor
   identities. Decay TTMn from n-1 then inject boundary n input; emit only
   previous-below/current-at-or-above 0.25 threshold crossings (n>0).
4. Validate Phase 8K target association; make dispatch, receipt and abstract
   token with real scenario/event ancestry and zero added model delay.
5. Decay electrical state from n-1 then apply boundary n tokens. Rectify/
   normalize activation, route exact side-preserving actuator commands[n].
6. Persist boundary n neural/motor/electrical/activation/actuator/world/body
   state and event-parent records.
7. If n<N, route s[n] to DNp01 using pinned ordered 311 routes. Advance the
   existing LIF kernel over n→n+1, producing SpikeEvents at n+1. Separately
   advance sensory s[n+1] using held e[n]; never substitute s[n+1] as drive[n].
8. Integrate the existing plant over n→n+1 using commands[n] and actual shared
   timestamp difference. Advance prescribed object to n+1. Next iteration
   reads this updated body/object state to derive e[n+1].

At final boundary N, process genuine spikes and downstream states at N and
record geometry, but perform no extra neural, object or body interval. Every
sample is labelled by its boundary or interval. Neural dt stays fixed 0.1 ms;
body integration retains timestamp-difference semantics from 12B.

The numerical kernels must be shared between historical batch and scenario
code; do not duplicate LIF/filter/integrator equations in a scenario simulator.
No prefix reruns or composed batch approximation, no future stimulus access.
TTMn uses tau_motor 10 ms/event_gain 0.25; electrical reference 0/1 ms/2 mV_eq;
activation scale 10; body gain 1. Existing DNp01 LIF config, source routes and
delay/refractory semantics are unchanged. Structural counts remain metadata.

## Zero output, feedback and tests

Zero spikes→zero motor crossings→zero tokens→zero activation/commands→stationary
body is valid. No placeholder event, scripted response or visual fallback.

An additional read-only bounding diagnostic used existing sensory integration
and DNp01 batch functions: all 311 exposures held at 1 for all 14 intervals,
gain/tau/k unchanged. Maximum DNp01 membrane values were -47.66741697736826
(10001/R) and -47.103587679902496 (10010/L), below threshold -45, zero spikes.
For bounded exposures and this fixed initial state/horizon, monotone filter/
transfer/LIF subthreshold updates support zero canonical scenario output.
This diagnostic is not a 13B scenario result or a parameter selection.

Required integrated statuses remain distinct:

- CLOSED_LOOP_EXECUTED: causal runtime completed, independent of movement.
- NONZERO_BODY_MOVEMENT_OCCURRED: measured from this model's body trajectory.
- ENVIRONMENT_AFFECTED_SENSORY_INPUT: report actual geometry/projection/exposure
  changes separately, not merely object displacement.
- BODY_STATE_AFFECTED_FUTURE_SENSORY_INPUT: canonical causal influence must not
  be marked observed if the body stayed fixed; report feedback capability
  separately, established by controlled integration tests.

A stationary canonical run executes the closed-loop architecture but does not
demonstrate realized movement-driven sensory change. The runner must prove
capability with a clearly synthetic nonzero integration test: inject a test
DNp01 event at a known boundary, propagate **every downstream stage**, integrate
body position, recompute next relative geometry/projection, and demonstrate a
changed future exposure using a test-local geometry straddling a lattice-radius
boundary. No synthetic injection is allowed in canonical scenario results.
Test baseline, zero propagation, step/batch parity, side identity, source
ancestry, off-by-one latency, final-boundary handling, deterministic reset,
finite/pre-contact validation and replay/tamper rejection. Check all historical
artifacts unchanged, including synthetic 8B/N/O/Q/W, 9B/C/E, 10B/C, 11B, 12B.

## One executable Phase 13B boundary

Implement one versioned scenario config and causal runner, fixed-centre
projection, bounded production adapters/shared kernels, genuine complete
downstream chain, plant feedback, integrated result and ignored immutable
artifact with offline replay. Include object-disabled Baseline control and
focused tests. No API/frontend/database, unrelated refactor or separate
mapping/composition metadata phases. Kernel extraction is authorized only
where required for this slice and must preserve historical payloads exactly.

Config includes scenario ID/version, body/object reset and prescribed motion,
dt/interval count, projection side/centre/scale/rounding, pinned anatomical
contracts and population, fixed numerical model/config identities, scheduling
semantics, assumption labels and exclusions. No randomness/seed is needed.
Reference parameters are pinned before outcome inspection; no tuning for motion.

Integrated result shares boundary/time arrays and stores body/object state,
relative geometry, derived disk radius/active-set identity, 311 identity-indexed
sensory-state/exposure columns, ordered transfer summaries, two DNp01 traces/
spikes, two TTMn traces/output events, dispatch/receipt/token parent records,
two electrical/activation/actuator streams and body interval diagnostics.
Compact neural arrays remain scientifically inspectable; frontend snapshots
need summaries, not all 311 values. Empty event streams are explicit.

New scenario-owned content IDs refer to real scenario execution/parent events,
not fixed synthetic artifact IDs. Artifact identity includes world/projection,
all fixed model configs, source contracts, tick semantics and result. Replay
recreates the causal run offline; tampering with world/body feedback, stimulus,
event ancestry, step/timing, config or output/hash must be rejected. Timing/
performance diagnostics remain outside scientific hashes. No large source
contracts or duplicate manifests need copying into each result.

## Phase 14 handoff and claim budget

13B should provide enough stable scientific state for Phase 14 frontend
integration. Transport is deliberately deferred, not presumed already present.
Future snapshot: run/scenario ID, boundary/time, body x/z world_eq and fixed
heading, object state, relative geometry/projected stimulus summary, LC4/LPLC2
activity summary, two DNp01 states/spike flags, motor and two actuator commands,
completion and distinct movement/feedback statuses. Frontend interpolates only
for visual playback; scientific sensory feedback never reads render transforms.

Static versioned scenario definitions suffice for a picker: ID, title,
scientific description, availability, bounded configurable parameters and
caveats. Results and definitions are distinct. No database/CMS or streaming
requirement is added merely for selection. Existing taxonomy stays intact.

Permitted: “an explicit model-space projection maps deterministic world-
relative looming state into the identity-resolved relative-column sensory
representation; the genuine downstream chain executes with body feedback.”
Not permitted: biologically correct retinal registration, physiological
force/displacement, escape success or autonomous movement when outputs are zero.
Koenig 2005 and mV_eq calibration blockers remain separate and unopened.

## Decisions

| Decision | Selected value |
|---|---|
| First scenario | LOOMING_CIRCUIT_VALIDATION_FIRST |
| World→sensory | EXPLORATORY_WORLD_TO_RELATIVE_COLUMN_PROJECTION |
| Feedback | BODY_STATE_FEEDS_NEXT_SENSORY_SAMPLE |
| Production composition | PRODUCTION_CHAIN_ADAPTER_REQUIRED_BUT_BOUNDED |
| Runtime | SINGLE_BACKEND_CAUSAL_TICK_RUNNER |
| Canonical movement | ZERO_MOVEMENT_EXPECTED_BUT_CLOSED_LOOP_VALID |
| 13B readiness | READY_FOR_FIRST_EXECUTABLE_CLOSED_LOOP_SCENARIO |
| 14 forecast | PHASE13B_WILL_PROVIDE_SUFFICIENT_STATE_FOR_FRONTEND_SCENARIO_INTEGRATION |

Phase 13A assessment: **PASS**. Full tests: 936 passed, 1 deselected, two existing
dependency deprecation warnings. Ruff check/format and git diff check pass.
Frontend regression: 38 tests passed; lint, typecheck and build pass. Only the
two intended documentation files changed; no implementation, commit or push.
Next exactly executable Phase 13B as specified above, not another metadata-only
phase.
