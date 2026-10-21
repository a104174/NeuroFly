# Experimental Neural Flight Steering v9

Status: implementation and local acceptance only. No publication authorization.

## Authority and classification

`experimental_neural_flight_steering_v9` separates:

1. `MALECNS_CONNECTOME_EVIDENCE`: male-cns:v1.0, UUID
   `4b2087c0fbe046bfaf0d60bc970e3e5d`. Right HSN/HSE/HSS
   10015/10016/10023 → DNp15 11215, structural counts 138/122/23.
   Left HSE/HSN/HSS 10034/10181/10419 → DNp15 12069, counts 78/126/14.
   Directed counts and identities are verified by the existing source validator.
   Counts alone do not establish physiological signs, transfer weights or recruitment.
2. `MODELED_NEURAL_DYNAMICS`: the existing HS/DNp15 proxy model, not a
   measured muscle/yaw signal. Six HS states, two DN states, zero initialization,
   held side descriptors, unit mean transfer, existing assumed signs and exact
   exponential old-state simultaneous updates (HS tau 5 ms, DN tau 10 ms).
3. `ENGINEERING_FLIGHT_CONTROL_PROJECTION`: a separately identified bounded
   conversion of integrated neural readout to normalized turn.
4. `ENGINEERING_FLIGHT_PLANT`: the existing v8 fixed-step kinematic plant.

Required disclosure:

> Experimental connectome-informed visual steering; airborne yaw mapping is an engineering hypothesis, not a validated physiological flight controller.

Pinned original neural artifact:
`4d7c791224f21ecf677df81d2127a6f8b753974694b6b324afc1948da3fb9064`.
Raw `experimental_locomotion_v1.json` SHA-256:
`17d335358a4f5cf4ed98b9682b103a81419cf82504203ce1bc72a7d76285d748`.
Neural contract: `371926570df00d88efb8e40aa8f6c64b757a420364143d42c9fb727722bfe074`.
Observer contract: `49e91a10fa49c5d7004f28249b63f334a0e23767c20108f5578a0e2586c9767a`.
Existing yaw contract: `1be0f6364070a5a5536f4c772bd47abb3be2f08357b439a51e03f034f8b2a654`.
Runtime source loading retains the existing byte/semantic verification. The new
config additionally records the complete pinned neural model and source hashes.

## Reuse and horizontal observation contract

`FlightPoseNeuralAdapter` inherits the actual protected `observation` and
`calculateBoundary` implementations of `InteractiveNeuralEngine`. No neural
kernel is copied. Its planar `advance` is prohibited, and planar velocity is
unused. The inherited HS/DNp15 state persists across all 600 intervals.

`ENGINEERING_HORIZONTAL_VISUAL_PROJECTION_V9` passes accepted flight XZ and
unwrapped yaw directly to the existing observer. Both systems are Y-up, heading
zero toward +Z, positive heading toward +X; one scene unit is explicitly taken
as one abstract observer world unit. Right/left source labels are retained:
landmarks X=+0.6 / −0.6 at Z=+0.4. The observer calculates the bearing change from
previously completed motion, subtracts yaw change, applies existing side signs,
50 ms normalization and clipping. This is a geometric motion proxy, not an
instantaneous image, retinal simulation or full airborne optic-flow model.
Altitude is deliberately excluded. Camera changes have no sensory effect.

The optional fourth condition uses the already validated static landmark plane
Z=−0.4 from the original v1 intervention. It changes the declared world at run
initialization, not the engineering turn schedule. Static landmarks stay static.

## Causal ordering and equations

At interval i (20 ms):

1. Read own accepted body poses i−1 and i; at zero there is no preceding motion.
2. Reuse the observer for that completed motion. Never access i+1.
3. Hold that observation and advance the persistent existing neural model by
   200 substeps of 0.1 ms. Old-state DN right−left readout is accumulated using
   the existing 50 ms normalization; no new instantaneous-readout convention.
4. Supply that integrated readout to the turn adapter for body interval i→i+1.
5. Reuse the existing v8 plant exactly once and commit pose i+1 and telemetry.

This preserves the existing one-completed-motion-interval observation timing.
The computed neural interval is only exposed once body boundary i+1 is accepted.
Telemetry at cursor k shows at most intervals 0..k−1; seeking never reveals a
future neural interval. The source timestamp, output availability, before/after
HS/DN states, readout, original controls, applied controls and clamps are recorded.

Projection identity: `existing_planar_omega_to_normalized_flight_turn_v9`.

```
Δq = sum(existing kernel orientation increments over 200 substeps)
raw_omega = 2.5 × Δq / 0.020                     # rad/s
omega = clamp(raw_omega, −0.5, +0.5)            # rad/s
potential_neural_turn = omega / 0.8             # normalized
neural_turn = potential_neural_turn             # ON / perturbation
neural_turn = 0                                 # OFF / projection-zero
applied_turn = clamp(engineering_turn + neural_turn, −1, +1)
```

Zero baseline; fixed gain, fixed normalization and fixed bounds. Positive
DN right−left increases heading toward +X. Authority is at most ±0.625 normalized
turn. Gain and angular bound are inherited from the established planar engineering
projection, converted by the existing flight maximum yaw rate, rather than fitted
per condition. A pre-coupling probe of the unmodified reference pose history gave
maximum absolute mean neural readout about 0.01098 yaw_drive_eq and raw omega
about 0.549 rad/s; the existing 0.5 rad/s limit is retained. No dramatic-effect
amplification or per-run calibration is used. Both saturation stages are explicit.

Only turn is adapted. Forward, vertical, intents, acceleration, contacts, bounds,
wingbeat, legs and flight-state transitions stay under their original contracts.
Landing retains v8's intentional yaw suppression. The small `advanceWithTurn`
seam enters the same private integrator as legacy `advance`; externally steered
runs cannot be exported as legacy v8 artifacts.

## Conditions, replay and UI

OFF, ON, projection-zero and static-plane perturbation each own independent body
and neural state. All four run on the same accepted fixed-step cursor, with their
own pose-derived observations. OFF still computes the neural model; only its
engineering influence is disabled. Projection-zero keeps that computation and
sets influence to zero. Each requires 120,000 neural substeps over 12 seconds.

The arena reuses `FlightClock`, `flightScene`, 12 Hz Normal Wingbeat, stable airborne
leg posture, Inspect Fly and the v8.2 world-space trajectory renderer. Cyan is the
selected condition, gold its independently computed OFF control. Comparison
uses authoritative doubles, never GPU Float32 vertices. The neural timeline is
only the accepted prefix. Pause, seek and replay read stored history; reset starts
all four conditions from the same original initial state. Seeking is limited to
accepted boundaries. A bounded scheduler limits catch-up work, never changes dt.

The separate v9 JSON artifact contains verified config/initial states, sources,
visual-world assumptions, projection, original program, body history, interval
neural/sensory/control telemetry, events and input/result/artifact hashes.
The new v9 artifact declares `NEURAL_INTERVALS_ROUND_1E_MINUS_10_BODY_AND_CONFIG_EXACT`.
Only serialized neural interval telemetry is rounded to 1e-10 to remove platform
math noise (observed Chromium/Node difference up to 1.82e-12 in interval-ms
subtractions, and about 1e-14 in projected yaw). Configuration and body records
remain exact, including legacy 1e-12 body integration and its initial anchor.
Live neural computation retains double precision and is independently checked
at the unchanged 1e-8 Python parity tolerance. These rounded artifact values
never feed back into either solver. Semantic replay still reconstructs all steps. Import
reconstructs all neural and body steps and compares the entire canonical artifact.
Rehashing contradictory outputs cannot bypass that check. No legacy v8/v8.1
schema changes, trail geometry persistence or scientific-session migration.

Separate localStorage key `neurofly.experimental-neural-flight.v9` holds at most
one completed, compact input/hash snapshot per fixed condition. No whole trajectory
is stored there. Reopening reconstructs and verifies it. Existing differing or
corrupt snapshots are retained with an error, never silently replaced. JSON export
supports recorded prefixes and transfer between origins. This is origin-local
storage, not cloud synchronization. No scientific My Experiments store is touched.

## Numerical authority and reproducible observations

`python -m neurofly.neural_flight_reference` consumes the exact recorded flight
poses, independently reruns the frozen Python observer and neural equations,
and emits before/after states and readouts. It consumes no TypeScript neural
expected values. It checks the pinned source and Python contract. This is neural
and observation parity, **not** an independent Python flight plant or full coupled
Python/TypeScript flight parity. Heading steps are independently checked against
the unchanged v8 integration equation and its 10^-12 quantization.

The focused test compares all 600 intervals for OFF, ON and perturbation; observed
maximum error 2.6020852139652106e−18, within the unchanged 1e−8 tolerance.
OFF and projection-zero match all 601 historical v8 body states exactly:

- Input: `25af17966a60f9ed17267d6143cac86b783fd370ca09fef33ee49313177c9f61`.
- Result: `8c8fc14e028a40fbc1aea526f253306bafc827b858a52495f0751168655528b7`.

Locally calculated final XYZ (engineering units):

| Condition | X | Y | Z | Heading rad |
|---|---:|---:|---:|---:|
| OFF / zero | 0.639532893281 | 0.11032208074629306 | −0.168962575892 | 2.050796326795 |
| ON | 0.743203454314 | 0.11032208074629306 | 0.061665339708 | 1.462534878738 |
| Perturbed plane | 0.666279320461 | 0.11032208074629306 | −0.155177159005 | 2.186966175103 |

All finish grounded with zero velocity; landing is 11.44 s for this program.
These are test outcomes, never literal trajectory inputs. Subsequent differences
include accumulated pose-dependent sensory feedback, not just the initial yaw
intervention. No physiological flight-control conclusion follows.

## Local verification and limits

Run canonical frontend tests/lint/typecheck/build, focused Python tests, Ruff and
`git diff --check`. The v9 frontend test independently invokes the Python harness;
run frontend tests with the repository venv available. Existing frozen runtime
inventory and canonical replay tests remain mandatory. No large data regeneration
or fabricated external MaleCNS fixture is permitted.

The view allocates no new fly geometry, materials, wing surfaces or trajectories
beyond the existing bounded v8.2 lines/markers. Four histories and neural logs are
bounded at 601/600 entries per condition. Node observations: four-condition
construction about 106–142 ms, legacy flight alone about 3–7 ms, export about
27 ms and full semantic import about 73 ms in one local measurement. These are
environment observations, not universal performance claims. Software-rendered
FPS is separate from numerical clock correctness or physical-GPU quality.

Limitations: selected small proxy circuit; assumed transfer/signs; horizontal
geometric sensory proxy without altitude; inherited engineering yaw calibration;
kinematic rather than force/aerodynamic flight; commanded thrust/altitude/landing;
no muscle activation, neural flight recruitment, learning or full fly behavior.
A useful next scientific improvement would be a separately preregistered,
independent validation of the horizontal observation/sign and yaw-projection
assumptions against appropriate measured data, without retuning this reference.

### Completed local acceptance evidence

Production Chromium workflow passed desktop (1440 px) and narrow (390 px):
OFF/ON/zero/perturbed results, pause/resume, exact seek/restored wing matrices,
reset, paired 3D geometry, saved-condition reload, JSON import and corrupt-output
rejection. A separately rehashed contradictory trajectory was rejected in the
actual browser. All four Chromium exports reconstructed in Node with matching
v9 artifact identities. ON final OFF-separation: **0.2528573128839617** units.
At 6.24 s ON interval readout is approximately −0.0063894485 yaw_drive_eq,
neural turn −0.3993405302 and combined turn +0.2506594698 (engineering +0.65).
OFF has its own pose-derived readout, approximately −0.0108739483, and zero
applied neural contribution. This difference is feedback, not a shared trace.

Actual renderer body position matched the recorded frame, and trajectory endpoint
matched `Math.fround` of the same recorded XYZ. Two original wing matrices froze
and reconstructed exactly at 6.24 s, with analytical 12 Hz phase. At 390 px the
expanded source panel gave document width 390 px and stage width 320 px. Desktop
and Inspect Fly screenshots plus narrow-screen evidence are outside the repository
under `/tmp/neurofly-v9/` (ephemeral acceptance evidence, not runtime dependencies).

Fresh renderer samples: v8 control 313 geometries / 315 calls; selected v9 with
its visible existing landmarks 315 / 317; OFF overlay enabled 316 / 318; seven
textures throughout. Four repeated paired mode/comparison toggle cycles returned
to those counts. Sampled heap after collection fluctuated, and later control
samples also grew (about 39–43 MB); v9 samples about 40–52 MB. This short observation
does not establish absence of a leak or a wing-specific leak. No unbounded geometry
accumulation was observed. SwiftShader produced about 4–6 desktop FPS and 14 narrow
FPS; physical-GPU performance was not measured. Wing updates sampled 0.1–0.2 ms.
An isolated Node observer/neural pass took about 16–25 ms for 120,000 substeps;
legacy flight about 3–7 ms for 600 steps. Four coupled conditions took about
100–131 ms, full export 28 ms, semantic import 73 ms in one isolated measurement;
10,000 frame/interval reads took about 80 ms. Concurrent browser/test load increases
those timings. The browser reconstructs all four conditions when opening a run.

Canonical gates: 304 frontend tests, frontend lint/typecheck/production build,
88 focused Python authority/runtime/replay/new-harness tests, two additional
original wing/motor descriptor checks, touched-Python Ruff lint/format and
`git diff --check` passed. This is **90 focused Python tests**, not the whole
Python suite. All 74 pinned runtime files verified. Historical v8 hashes remained
exact. Actual browser v8.1 turn edit 0.65→0.30 reproduced final
[0.734186787114, 0.11032208074629306, 0.012063823709] and v8.2 reference separation
0.2042790174497855. Browser v6 retained 18 articulated bones; v7 at 1.94 s retained
foot delta 0.0007857500410935088 and knee delta 0.018372605582471557, with route-off
matching Base gait and sham matching ON; the v7.1 2 Hz preview remained intact.
No JavaScript runtime exception was observed. A pre-existing missing `/favicon.ico`
produced a resource 404, without affecting the experiment.

Verified ON v9 artifact identity:
`ecd555413f79d9ca076599418c567142af9d02ee9cdbca949e26f93843a668ba`.
No files were staged, committed, pushed or deployed during v9 implementation.
