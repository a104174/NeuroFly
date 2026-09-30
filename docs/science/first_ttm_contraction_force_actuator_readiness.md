# Phase 11A — first TTM mechanics-facing boundary

## Outcome and repository gate

Select an executable, side-preserving **exploratory actuator-command adapter**
for Phase 11B. Consume activation directly, with no intervening contraction
state or force gain. The new capability is functional routing to two distinct
mechanics-facing channels, not a new muscle equation or a renamed force scalar.
Stop at commands; no movement in 11B.

The starting worktree was clean on `main`; HEAD and local `origin/main` both
equaled `083c95564f9c1a6633076663a8fbc13c1226fe7f`. The log contains committed
10C (`083c955`), 10B (`f287ea8`), 10A (`7351954`), and 9B (`954c4c0`). Initial
`git diff --check` passed. This checks the local remote-tracking reference,
not a newly fetched server state. No commit/push is authorized.

Offline replay passed for:

| Source | Canonical artifact identity |
| --- | --- |
| 10B activation | `4e4a3e0528500cd87c49a272f01891e8cf24c5232e5c11588d6f1c25887e06fb` |
| 10C sensitivity | `b605e51e4ed42813d2562d61aa58129ed3d5b43e875ab1fd0de98ca0360c9a6e` |
| 9B electrical | `72636cc94c1508c074950b1d5b3847a9e0283ecb0cde04f3f85a36b2c62d2e0f` |

These established replay paths recursively validate their motor-input and
proxy ancestry, including Phase 8Y and its Phase 8K target source; the target
contract was also replayed explicitly. No source migration or readiness change.
The Phase 9 external Koenig–Ikeda 2005 protocol blocker remains; no attempt to
reopen that source-recovery path was made.

## Current activation interface

`static_normalized_muscle_activation_model_v1` produces
`static_normalized_muscle_activation_result_v1` from persisted Phase 9B samples:

```text
a[n] = min(1, max(0, voltage_deviation_mV_eq[n]) / 10.0)
```

The dimensionless `[0,1]` value is an uncalibrated activation proxy. It has no
activation-specific memory, lag, threshold or physical-force semantics.
Six fixtures contain 12 distinct trajectories, each with 81 boundaries at
0.1 ms spacing (80 intervals, 8 ms). Body/side `800146/R` and `804642/L` remain
distinct; both reference the side-agnostic G1 proxy domain type
`ttm-g1-proxy-domain-057e09a9a9c5b054f7ce`.

Phase 10C found inverse-scale behavior and preserved positive temporal shape
at scales 5/10/20, with no canonical clipping. This is model behavior, not
biological activation validation. Full trajectories, not Phase 9E scalar
peaks or Phase 9 electrical values, are the direct Phase 11 input.

## Existing mechanics, rendering and rig audit

Inspection covered `src/neurofly`, frontend playback/scene components,
`tools/blender/export_fly_visual.py`, the visual manifest, the actual GLB JSON,
and the asset/composition architecture documents. No existing runtime
contraction, force, actuator, locomotion controller, rigid-body/world solver,
collision engine, joint state, or body pose/velocity integration was found.
The morphology inspector's skeleton lines are neural morphology, not a fly rig.
Backend experiment telemetry and `ExperimentSceneState` carry persisted neural
and sensory playback data, not an embodied mechanics-state contract.

`fly_visual_v1.glb` has 14 nodes, 13 meshes, zero skins and zero animations.
Its named left/right front/middle/rear leg objects are static simplified meshes,
not articulated joint segments or validated pivots. There is no skeletal rig,
bone hierarchy or biomechanical attachment provenance. Asset units are
normalized presentation units, not measured body dimensions. The stationary
fly transform, looming corridor and neural overlay are presentation mappings.
See [asset pipeline](../architecture/blender_asset_pipeline.md) and
[scene composition](../architecture/scientific_scene_composition.md).

Thus geometry is **not ready**, rather than “a validated visual rig exists.”
Named meshes alone cannot supply origins, insertions, moment arms, joint angles,
body-space directions or a force-to-motion relationship. No conflicting
mechanics implementation was found.

## Bounded primary evidence audit

Only primary research or its official primary abstract was used for biological
claims. Source access limitations are distinct from model assumptions.

| Source and access | Verified scope/location | Architecture consequence and non-transfer |
| --- | --- | --- |
| King DG, Wyman RJ (1980), *Anatomy of the giant fibre pathway in Drosophila. I. Three thoracic components of the pathway*, J Neurocytol 9:753–770; [DOI 10.1007/BF01205017](https://link.springer.com/article/10.1007/BF01205017). Publisher Summary only; no full Methods audit. | Summary: GF contacts a motor axon innervating ipsilateral TTM. | Supports pathway/class and laterality context, not MaleCNS-body-to-G1 tracing, attachment geometry or force scale. |
| Trimarchi JR, Schneiderman AM (1993), *Giant fiber activation of an intrinsic muscle in the mesothoracic leg of Drosophila melanogaster*, J Exp Biol 177:149–167; [DOI 10.1242/jeb.177.1.149 / official primary abstract](https://pubmed.ncbi.nlm.nih.gov/8486998/). Abstract verified; publisher full text not accessed. | Abstract: TTM contraction extends the femur; femur–tibia joint extension is associated with TLM and acts synergistically during jumping. | Supports a functional mesothoracic femur-extension channel. Do not assign TTM a tibial-extension joint axis or claim it alone determines a jump. |
| Eldred CC, Simeonov DR, Koppes RA, Yang C, Corr DT, Swank DM (2010), *The Mechanical Properties of Drosophila Jump Muscle Expressing Wild-Type and Embryonic Myosin Isoforms*, Biophys J 98:1218–1226; [DOI 10.1016/j.bpj.2009.11.051, author-hosted published full text](https://static1.squarespace.com/static/543205c7e4b0e99376e323aa/t/5469f2eee4b02ed9bcbd884a/1416229614488/The%2BMechanical%2BProperties%2Bof%2BDrosophila%2BJump%2BMuscle%2BExpressing%2BWild-Type%2Band%2BEmbryonic%2BMyosin%2BIsoforms.pdf). Full text verified; PMC indexed primary passages also available. | pp.1218–1220, Abstract/Methods/Fig.1: chemically skinned bundles of 8–10 large TDT fibers from 2–3-day-old females; Tr-WT and embryonic myosin transgenic preparations. Calcium-solution activation, slack tests and force clamps at 15°C. Tr-WT abstract reports 37±3 mN/mm² isometric tension and 6.1±0.3 muscle-lengths/s unloaded shortening. | Real mechanics evidence, but bundle tension/shortening under chemical activation, not an intact G1 electrical-to-force calibration. No parameter adopted. Fiber-count descriptions differ from earlier G1 literature; do not use this study to revise pinned counts or infer all-fiber equivalence. |
| Zumstein N, Forman O, Nongthomba U, Sparrow JC, Elliott CJH (2004), *Distance and force production during jumping in wild-type and mutant Drosophila melanogaster*, J Exp Biol 207:3515–3522; [DOI 10.1242/jeb.01181 / primary abstract](https://pubmed.ncbi.nlm.nih.gov/15339947/). Abstract only. | Abstract: strain-gauge forces transmitted through mesothoracic legs of tethered flies; wild-type female Canton-S peak 101±4.4 µN, peak time 8.2 ms. Separate wing-removed jump-distance tests and modeled takeoff force are different measurements/derivations. | Whole-fly/leg-level loading, not isolated G1 fiber force. Age, detailed stimulation and temperature not verified here. Neither measured leg force nor calculated takeoff force transfers to the current proxy. |

The numerical values above describe source preparations only. They are **not**
NeuroFly config candidates. Neither source establishes a conversion from the
current activation proxy to newtons, an applicable contraction tau, or exact
physical actuator geometry. TTM/TDT terminology identifies jump-muscle context;
it does not establish complete jump mechanics or equal physiology across fibers.

## Candidate layers and redundancy test

| Candidate | Useful capability / assumption cost | Assessment and possible 11B demonstration |
| --- | --- | --- |
| A. Direct activation input | Retains timing and avoids another gain. Destination semantics still unspecified. | Best signal source; by itself no new executable capability beyond 10B. Use inside G's routed adapter. |
| B. Dimensionless contraction `c=f(a)` | Identity/rescaling adds neither shortening state nor mechanics meaning. | **REDUNDANT** if only a renamed scalar. A shortening interpretation would require a new unsupported mapping. Reject. |
| C. First-order contraction state | Adds memory via positive `tau_contraction`; could later represent a chosen actuator response filter. | Distinct dynamics but currently unidentified and unnecessary before an actuator consumer exists. Would demonstrate delayed/filtered state, not measured contraction; defer. |
| D. Model-space force `g*a` | Arbitrary gain changes amplitude but provides no direction, load or geometry. | **REDUNDANT** here; worsens gain confounding without useful mechanics semantics. Reject. |
| E. Physical force | Could expose newtons if preparation, area, length, activation and loading applicability were resolved. | Not ready. Published bundle/whole-fly measurements are not the current G1 proxy's force parameterization. No honest bounded physical-force 11B now. |
| F. Mechanistic Hill muscle | Adds length/velocity dependence, passive elasticity and parameterized force production. | Premature: no applicable geometry, length state, force calibration or excitation-to-contractile transfer. Hill mechanics is not an activation law. |
| G. Exploratory actuator mapping | Routes each activation stream to an explicitly side-qualified, functional femur-extension command channel. No extra scalar gain or dynamics. | **Select.** 11B demonstrates executable addressable actuator-command trajectories suitable for a later plant, not physical muscle force. |

G must not be implemented as `force_proxy = a` under another name. Its added
information is the explicit consumer/action domain and independently addressed
left/right actuator channels, with validated routing, source ancestry and no
aggregation. Command magnitude is intentionally unchanged. A bare copy with no
destination/action contract would fail the usefulness gate and be redundant.

## Parameter/evidence and assumption budget

Status describes applicability to NeuroFly, not whether some preparation has
ever measured the quantity. No candidate parameter is biologically identified
for the current proxy.

| Candidate / quantity | Role; units if applicable | Evidence status / identifiability | Needed in selected 11B? |
| --- | --- | --- | --- |
| A/G source activation | Existing normalized driver; dimensionless | MODEL_ASSUMPTION; historical config fixed, biologically NOT_IDENTIFIABLE | Yes, consume unchanged |
| G body/side → functional actuator channel | TTM-class-qualified routing, femur-extension action; no geometric vector | Biological function EVIDENCE_SUPPORTED; exact proxy-to-virtual-actuator selection MODEL_ASSUMPTION, not physical tracing | Yes |
| G magnitude passthrough, ceiling meaning, no lag | Reuse normalized command, same boundary | MODEL_ASSUMPTION; no additional fitted quantity | Yes |
| B shortening scale/transfer shape | Converts activation to an alleged contraction amount; model units or physical length | MODEL_ASSUMPTION / NOT_IDENTIFIABLE; physical units unsupported | No |
| C contraction time constant, initialization | Filter memory; time unit, model state | MODEL_ASSUMPTION / NOT_IDENTIFIABLE | No |
| D force gain | Rescaling; nonphysical force-equivalent units | MODEL_ASSUMPTION / NOT_IDENTIFIABLE; redundant here | No |
| E/F maximum force / area conversion | Physical force ceiling; N and applicable cross-sectional area | PARTIALLY_CONSTRAINED in other preparations, NOT_IDENTIFIABLE for this proxy | No |
| E/F optimal length, shortening scale | Length reference/excursion; physical length | PARTIALLY_CONSTRAINED in bundles only; applicable geometry NOT_IDENTIFIABLE | No |
| E/F velocity constant, force–velocity/length curve | Load/length dependence; length/time and dimensionless shape | PARTIALLY_CONSTRAINED in source preparations; present proxy NOT_IDENTIFIABLE | No |
| E/F contraction kinetics / passive elasticity | Time dependence and passive loading | MODEL_ASSUMPTION if introduced here; NOT_IDENTIFIABLE | No |
| Later plant damping/stiffness | Dissipation/elastic loading; requires chosen state and physical or explicit model units | MODEL_ASSUMPTION / NOT_IDENTIFIABLE | No |
| Later plant moment arm, anchors/orientation | Force-to-joint/body coupling; geometry | NOT_IDENTIFIABLE from current visual asset/target contracts | No |
| Selected gain, threshold, tau, force/length/velocity | Additional muscle parameters | NOT_REQUIRED | No |

## Force-scale confounding and boundaries

In the unclipped positive regime, activation magnitude is proportional to
`electrical_event_scale / activation_scale`. A hypothetical `F_gain*a` yields
`F_gain*electrical_event_scale/activation_scale`; amplitude alone cannot identify
these gains independently. Do not absorb activation scale into another gain,
select a sensitivity cell, or claim that command 1 defines maximal physical
force. The actuator adapter adds no gain and therefore preserves, rather than
solves, this confound.

Activation and actuator command contain no muscle length, shortening, strain,
velocity, work, force or torque. The virtual functional channel is not a G1
physical instance, whole-TTM homogeneous state or exact peripheral endpoint.
Shared routing semantics/config are modeling conventions, not bilateral
physiological equality. TTM contribution does not determine takeoff, direction,
velocity or escape success.

## Exactly one executable Phase 11B

Implement **side-preserving exploratory TTM actuator-command trajectories**.

Input: replayed persisted canonical 10B activation artifact, its full samples,
source trajectory identities and proxy ancestry. Do not compute input from 9B,
9E peaks, 8W events or connectome structural weights.

Output: one dimensionless normalized femur-extension-drive command trajectory
per causal activation trajectory, addressed to a virtual functional actuator:

| Source | Proposed actuator address | Action kind |
| --- | --- | --- |
| `800146/R` | `RIGHT_TTM_ACTUATOR` | `EXPLORATORY_MESOTHORACIC_FEMUR_EXTENSION_DRIVE` |
| `804642/L` | `LEFT_TTM_ACTUATOR` | `EXPLORATORY_MESOTHORACIC_FEMUR_EXTENSION_DRIVE` |

These are virtual action channels, not a resolved joint axis or visual-mesh
binding. At each boundary, `extension_drive_proxy[n] = activation_proxy[n]`;
retain source value/identity, step/time, body/side, proxy domain, activation
config, adapter identity and exploratory actuator provenance. Store shared
grids/metadata compactly following existing conventions. No command is a
binary jump request and there is no bilateral total.

Minimal config: versioned adapter identity, exact source schema requirement,
two fixed body/side-to-channel mappings, functional action kind, dimensionless
normalization/ceiling semantics, same-boundary passthrough, explicit
`MODEL_ASSUMPTION` classification and exclusions. No new numerical free gain,
time constant, physical units, geometry or generic actuator registry. New
runtime result/artifact/replay tooling belongs to 11B, not this document.

Reuse exactly ZERO_EVENT_CONTROL, RIGHT_SINGLE_EVENT, LEFT_SINGLE_EVENT,
BILATERAL_SIMULTANEOUS_EVENT, RIGHT_REPEATED_EVENTS and LEFT_REPEATED_EVENTS:
12 trajectories × 81 samples. Singles/bilateral active channels retain 0.2
peaks; repeated active channels retain 0.22706705664732252 under the historical
config. These are regression expectations, not biological targets.

Executable acceptance gates: exact source replay; two distinct channel addresses;
every sample routed once to its own side; zeros remain zero; finite bounded
monotonic magnitude passthrough; unchanged grid and timing; no coupling,
aggregation or hidden history; malformed/mismatched/duplicate sources rejected;
deterministic content-addressed outputs and tamper rejection. Inspect output
must say exploratory/unphysical, show action addresses and ancestry, and make
it impossible to interpret commands as force or body motion. Full regression
gates and ignored generated data follow repository conventions.

## Phase 12 handoff and closed-loop discipline

Phase 12 needs one explicit actuator-to-plant decision: exploratory kinematic
joint/body mapping versus physical dynamics. It must define joint/pose state,
coordinate/unit conventions, actuator response, timestep, ground contact and
how movement changes sensory input. A physical branch additionally needs
applicable geometry, force scale, mass/inertia and loading; none are provided
by 11B. An assumption-labeled kinematic plant can precede calibrated forces,
but it is not predicted biological mechanics.

Any future rig binding must be deliberately created/audited, not inferred from
static mesh names. Simulation state owns motion; R3F renders/interpolates it,
with render FPS decoupled from simulation ticks. No frontend behavior logic,
`if looming: jump()`, or LLM fly controller. The canonical fixture demonstrations
do not themselves establish a production closed sensory–motor–world loop.

## Scientific claim budget and decisions

Permitted after 11B: NeuroFly deterministically routes exploratory activation
trajectories to separate normalized TTM-associated femur-extension actuator
command channels under explicit modeling assumptions.

Not permitted: measured TTM force/contraction, exact G1 anatomical actuation,
all-fiber activation, maximal-force normalization, complete jump prediction or
biological bilateral equality. No muscle parameter fitting or empirical scoring.

| Decision | Selected value |
| --- | --- |
| Model layer | `DEFINE_EXPLORATORY_TTM_ACTUATOR_MAPPING` |
| Physical force | `PHYSICAL_FORCE_NOT_READY` |
| Geometry | `ACTUATOR_GEOMETRY_NOT_READY` |
| Phase 11B | `READY_FOR_FIRST_EXECUTABLE_ACTUATOR_LAYER` |
| Closed-loop progress | `PHASE11B_OUTPUT_CAN_FEED_FUTURE_WORLD_MECHANICS` |

Phase 11A is a documentation-only decision; no implementation or generated
artifact. Phase 10 remains complete; its evidence limitations are unchanged.

## Verification and status

`python -m pytest`: 857 passed, 1 deselected, two existing dependency
deprecation warnings. `python -m ruff check .` and
`python -m ruff format --check .`: pass (265 Python files already formatted).
`git diff --check`: pass. Frontend regression: `npm test` 38 passed;
`npm run lint`, `npm run typecheck`, `npm run build` pass. The build-generated
Next type-reference path change was restored; no frontend change remains.
Only this document and the minimal Project Context addition are intended
changes. No new generated data, implementation, commit or push.

Phase 11A status: `PASS` for architecture/readiness, not physical validation.
