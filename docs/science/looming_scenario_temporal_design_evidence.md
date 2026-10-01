# Phase 17 — looming scenario temporal-design evidence review

## Outcome and unchanged boundary

Temporal provenance: `TEST_FIXTURE_INHERITANCE`.
Current scenario role: `MICRO_WINDOW_CIRCUIT_EXECUTION_TEST`.
Current-design decision:
`KEEP_1P4_MS_FOR_CURRENT_CIRCUIT_VALIDATION_ROLE`.
Next-design decision:
`SEPARATE_CIRCUIT_VALIDATION_FROM_BEHAVIOR_SCALE_SCENARIO`.

Keep the existing canonical artifact and its narrowly stated circuit-execution
role. It is not a complete looming-response or behavioral experiment. No exact
replacement duration is identified. A separate future world-experiment design
must assess trajectory and horizon together, before any implementation.

This review changes documentation only. No alternate-duration execution,
parameter fitting, spike search, new scenario, frontend change or model revision
was performed. Longer accumulation is a mathematical possibility, not evidence
that a longer horizon is scientifically appropriate or sufficient for spiking.

## Repository and immutable source gate

Started clean on `main`, equal to `origin/main`, at
`4599c96b131ca44095546f83561fd7daf4c10a11` (corrected Phase 16).
Phase 15 `ee93c4c`, Phase 14 `e7bb923` and Phase 13B `5d58fd7` are committed.
Initial diff check passed. Required offline source replays passed unchanged:

| Phase | Canonical artifact ID | Verification |
| --- | --- | --- |
| 16 | `bb1d227dd3dc56d74939c37e231ca0f8aa02f8d0140964eef7f1fb31e00b101b` | corrected diagnostic recomputation, including material projection classification |
| 13B | `55e2f4d37bc6f8fb81aee67886d8680a76646a0317961bd90cf0e3fbabb2c46b` | both genuine closed-loop runs and source ancestry |
| 7O | `99eeea47542abd5f9af2c1918e6e0514fa2c4b8f04d9a3f14a75ac1f8dbbcaa5` | full numerical 311-body / 35-condition replay |
| 8C | `5f57cbc6c0ac770d65582ffe97c0c690e539bab33fef549da15d5273912279bf` | genuine persisted sensory-output/motor replay |

Canonical Baseline and Looming remain 0.1 ms, 14 intervals, 15 boundaries,
1.4 ms. Both have zero DNp01 spikes, downstream events/commands and body
movement. Looming changes radius 2→3 and exposed bodies 19→22; right DNp01
peaks at -51.933657842035174 mV_eq, left stays -52 mV_eq. Baseline has explicitly
empty exposure and both targets at rest. These are unchanged model results.

## Git/code provenance: why fourteen intervals exist

| Introduction / inheritance | Repository evidence | Original role |
| --- | --- | --- |
| Phase 2A, `f301b76`; implemented Phase 2B, `5aa3350` | `neural_model_selection.md`, temporal-resolution decision; `LIFConfig.dt_ms=0.1` | Numerical resolution for discrete delays/refractory behavior and GF event timing; not measured biological sampling |
| Phase 7D, `435e784` | `relative_column_assignment.py`: left/right expanding disks `(1,2,3,4)`, `dt_ms=0.1` | Four synthetic anatomical exposure samples, each held for one interval; no physical looming timecourse |
| Phase 7E, `5ae7529` | `RECOVERY_TAIL_STEPS=10`; `relative_column_sensory_dynamics.md` explicitly calls the tail an inspection horizon | Four driven intervals + ten zero-input recovery intervals = fourteen; first documented 1.4 ms endpoint |
| Population scaling through Phase 7O, `e84fa63` | `bounded_sensory_population._condition_states` derives interval count from stored state-timeline length; 7O uses that bilateral reference | Inherited numerical fixture horizon, not newly chosen biological duration |
| Phase 13A, `8f06a8e` | `first_closed_loop_scenario_readiness.md`, “Proposed minimal canonical world and projection” | Explicitly reuses 7O's 1.4 ms window for a short circuit-validation run, not a behavioral timescale; avoids multirate scheduling |
| Phase 13B, `5d58fd7` | `ScenarioConfig.interval_count=14`; config validation requires fourteen; tests/replay preserve fifteen boundaries | Deliberate bounded closed-loop fixture, not an off-by-one/configuration accident |

The exact ten-step recovery-tail length is an engineering inspection convention,
not a fitted or evidenced biological decay interval. Phase 13 inherits the
**length**, not the old exposure sequence: its approaching world object drives
sensory exposure throughout the run rather than switching to ten recovery
intervals. Thus calling the current scenario a recovery assay would also be
incorrect. Engineering rationale exists, but the origin of the horizon is
specifically `TEST_FIXTURE_INHERITANCE`, not biological evidence or unresolved
history. No implementation bug was discovered.

## Six distinct temporal quantities

| Quantity | Pinned meaning | Status |
| --- | --- | --- |
| Integration timestep | 0.1 ms, discrete held-input interval | Numerical choice |
| Observation horizon | 1.4 ms, fourteen updates | Inherited fixture / bounded execution choice |
| Object trajectory | z starts at 4, velocity -1 world_eq/ms, radius 1 world_eq | Uncalibrated model-space scenario assumption |
| Sensory tau | 1 ms for dimensionless filtered exposure | Model assumption, not measured LC4/LPLC2 calcium/spike kinetics |
| Membrane tau | 20 ms for exploratory DNp01 LIF | Model prior/assumption, not identified MaleCNS DNp01 measurement |
| Biological response timing | Endpoint- and preparation-specific observations below | Evidence, not interchangeable model parameters |

The frontend's six-second slowed playback is presentation time only. It neither
lengthens the scientific horizon nor establishes biological timing adequacy.

### dt: numerical accuracy versus experiment duration

The existing sensory and LIF kernels use exponential held-input updates, not
unstable forward-Euler integration. dt/tau_sens=0.1; dt/tau_m=0.005.
`test_simulation.py` already checks passive-decay and delayed-network convergence
at 0.05/0.1/0.2 ms. Those tests are numerical evidence, not universal convergence
of every possible world projection or threshold event. Integer boundary
sampling still quantizes exposure transitions and spike timestamps.
No numerical instability or accuracy evidence found here requires changing dt
or duration. A longer observation window would answer a different design
question; it is not an integration-stability fix. No new dt trial was executed.

## Phase 16: effective usable response windows

At boundary n, exposure e[n] updates sensory state s[n+1]. DNp01 uses s[n] over
interval n→n+1. Therefore changed exposure first affects membrane at n+2.
This is deliberate simultaneous-update ordering, not missing drive.

| Event | State/drive availability | First affected membrane | Usable intervals before final boundary |
| --- | --- | --- | --- |
| Initial exposure, n=0 / 0 ms | n=1 / 0.1 ms | n=2 / 0.2 ms | thirteen DNp01 intervals, n=1…13, spanning 1.3 ms; stored post-effect window 0.2…1.4 ms = 1.2 ms |
| Radius 2→3, n=8 / 0.8 ms | n=9 / 0.9 ms | n=10 / 1.0 ms | five DNp01 intervals, n=9…13, spanning 0.5 ms; stored post-effect window 1.0…1.4 ms = 0.4 ms |
| Final exposure/state, n=14 / 1.4 ms | no outgoing canonical interval | no subsequent stored membrane | zero further intervals |

The expanded footprint supplies six sensory updates (n=8…13) but only five
DNp01 intervals can consume its resulting state before the run ends. The final
available drive is not consumed. Sensory accumulation, membrane filtering and
discrete latency are coupled to the observation horizon, not independent
limiting causes.

Duration/tau_sens=1.4; duration/tau_m=0.07. The existing diagnostic's constant
held-drive membrane fraction is 0.067606180094, but actual drive grows from zero
and is not constant. Right peak rest excursion is 0.066342157965 mV_eq against
a 7 mV_eq rest-to-threshold excursion; remaining margin is 6.933657842035.
The same-horizon all-311/both-side/full-exposure audit gives R/L peaks
-47.66741697736826 / -47.103587679902496 mV_eq and zero spikes. It supports
joint-limit interpretation, not a sufficient-duration prescription. Projection
remains `MATERIAL_MODEL_LIMITER`, not dominant. No alternate exposure or
duration scenario was executed for this review.

## Object trajectory and validity: analytical audit only

For the unchanged canonical stationary body and t in model ms:

```text
object_z(t) = 4 - t
body_z(t) = 0
relative_z(t) = relative_distance(t) = 4 - t   [while t < 4]
half_angle(t) = atan2(1, relative_distance(t))
lattice_radius(t) = floor(10 * half_angle(t))
```

At 1.4 ms separation is 2.6 world_eq. `project_world` requires finite geometry,
positive distance and strictly positive relative_z. Continuing the same
stationary-body trajectory reaches rejected geometry at **4 ms**, including
the zero-separation boundary; later it is behind the body. This is a domain
limit, not a proposed duration. With forward body displacement, separation is
`4-t-body_z(t)` and may fail earlier; 4 ms is not a universal safe horizon.
Body feedback must remain in any future validity/termination check.

There is no contact solver. Interpreting radius as a solid sphere would place
its near surface at the body point at 3 ms in the stationary analytical case,
but the current projection does not define surface contact or a collision
outcome there. Neither 3 nor 4 ms is a biological time-to-impact measurement.
The separate physical `LoomingStimulus` terminal-collision contract must not be
silently imported into this model-space scenario.

**Do not compare -1 world_eq/ms numerically with measured biological approach
velocities.** The model radius/speed ratio is 1 model ms; it has no calibrated
stimulus/preparation correspondence. Biological r/v protocols therefore do not
directly choose a scenario velocity, radius or observation horizon.

## Existing evidence audit and primary verification

Reviewed the existing sensory-boundary, neural-model-selection, encoder and
trajectory-characterization notes; Phase 7 sensory/population notes; motor
escape/interface, TTMn evidence-closure/parameterization and G1 observation
compatibility notes; and Phase 13/16 records. They establish different endpoints,
not a common physiological clock. Older physical/angular benchmarks have
explicit synthetic gains and pre-collision windows; they are not the current
311-body world scenario's parents or calibrated duration evidence. Structural
contact counts remain structural, never drive efficacy.

Primary publications were rechecked on 2026-10-01. Publisher/PMC browser access
was inconsistent: the original Ache paper was accessible as an author-uploaded
full text; the von Reyn published PDF was downloaded from Janelia; Klapoetke's
original full text was read from Europe PMC's XML service; Augustin's original
article was accessible at PLOS. No secondary summary supplies a design-driving
timing value. Temporary source copies are not tracked or new model artifacts.

### Evidence table

| Source / class | System/population | Stimulus/preparation | Measured timing quantity | Reported timing | Applicability / limitation |
| --- | --- | --- | --- | --- | --- |
| Phase 7E→7O→13A history — PROJECT_MODEL_ASSUMPTION | NeuroFly sensory and closed-loop runner | Four synthetic assignments plus ten inspection-tail intervals; later duration inherited, stimulus not inherited | Fixture horizon | 14×0.1=1.4 ms | Exact engineering provenance; no biological duration claim |
| Phase 16 — DERIVED_MODEL_DIAGNOSTIC | Two exploratory DNp01 states | Pinned world projection and causal loop | Exposure-to-membrane latency; window/tau ratio | 2 boundaries / 0.2 ms; 0.07 | Model scheduling/integration only; not sensory conduction latency |
| [Ache et al. 2019, DOI 10.1016/j.cub.2019.01.079, author-uploaded primary full text](https://www.researchgate.net/publication/331408732_Neural_Basis_for_Looming_Size_and_Velocity_Encoding_in_the_Drosophila_Giant_Fiber_Escape_Pathway), Fig.3A / STAR Methods “GF Model” — PRIMARY_BIOLOGICAL_EVIDENCE | D. melanogaster GF, LC4/LPLC2 pathway silencing | In-vivo current-clamp, 3–5-day females; projected disk, LPLC2×Kir, N=5 in Fig.3 | Disk appearance→transient GF response | 19 ms | Sensory-path onset observation, not LC4 membrane tau or isolated synaptic delay; LPLC2 model delay set equal to it, not independently measured. No value transferred |
| [Klapoetke et al. 2017, DOI 10.1038/nature24626](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457385/), Methods “Calculation of fluorescence”; [verified original XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7457385/fullTextXML) — PRIMARY_BIOLOGICAL_EVIDENCE | D. melanogaster LPLC2; calcium imaging, 2–5-day females | RF-centered expansion, 5°→60°, 10°/s edge speed or r/v=40 ms for the cited normalization assays | Fluorescence peak-analysis window, not neural onset latency | 300 ms averaging around peak; search extends to 500 ms after motion | Supports looming response assays and endpoint distinction; calcium/analysis times cannot set sensory tau or DNp01 horizon |
| [von Reyn et al. 2014, DOI 10.1038/nn.3741, Janelia published PDF](https://www.janelia.org/sites/default/files/Library/nn.3741.pdf), Fig.4 / Results — PRIMARY_BIOLOGICAL_EVIDENCE | D. melanogaster GF and leg/flight output | Head-fixed looming with GF recording; stock methods use 2–5-day males/females unless specified; 27/27 spike-associated trials, 5/5 flies | GF spike→middle-leg extension; GF spike→flight initiation | 0.9±0.2 ms; 2.0±0.1 ms | Post-spike behavioral endpoints, not visual-onset latency or a membrane constant; absent physical mechanics prevents direct calibration |
| von Reyn et al. 2014, Fig.5 — PRIMARY_BIOLOGICAL_EVIDENCE + source-derived timing fit | Same species; freely behaving escape groups | Projected looming; response-time versus r/v model | Extrapolated takeoff delay, not measured universal onset latency | 30.1 ms short-mode; 45.7 ms long-mode | Fit-intercept context only; cannot set current scenario duration or establish that a stationary model is biologically wrong |
| [Augustin et al. 2017, DOI 10.1371/journal.pbio.2001655](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.2001655), Fig.1 / Electrophysiology — PRIMARY_BIOLOGICAL_EVIDENCE | D. melanogaster adult female GF system; young/aged, 25°C | Brain stimulation, 40 V / 0.03 ms; intracellular TTM/DLM recording; at least five pulses separated by 5 s | Stimulus artifact→muscle EPSP onset | Age-dependent latencies shown in Fig.1; no new scalar estimate extracted here | Electrical circuit+muscle endpoint, not visual latency, TTMn tau, or looming observation window |

The original Ache methods specify a 360 Hz projector; its display cadence is
also not NeuroFly's integration dt. The source-specific 19 ms observation is
already longer than this run, supporting rejection of a **complete biological
response** interpretation. It does not require adding a 19 ms delay to the
current model or selecting any new duration. Per-body LC4/LPLC2 dynamics and
MaleCNS DNp01 temporal parameters remain uncalibrated. Existing notes cite
Tanouye/Wyman muscle latencies and Augustin's computational NMJ estimates;
those are distinct muscle endpoints/model estimates, not evidence for this
visual observation horizon. No new original-source verification or parameter
adoption for those older scalar values is claimed.

## Scenario role and alternative designs

Current 1.4 ms is sufficient to test deterministic causal execution, early
model transients and feedback wiring. It is insufficient to claim observation
of a complete biological LC4/LPLC2→GF response, escape decision or takeoff.
`EARLY_TRANSIENT_RESPONSE_WINDOW` describes the model trace, but the primary
role classification is `MICRO_WINDOW_CIRCUIT_EXECUTION_TEST`; it is more than
a numerical-only fixture because the genuine closed causal chain executes.

| Option | Assessment |
| --- | --- |
| A KEEP_1P4_MS_AS_EXPLICIT_MICRO_WINDOW | Retain immutable circuit-validation artifact and narrow claims. Selected for the current scenario |
| B EXTEND_SAME_OBJECT_TRAJECTORY | Not selected: geometry eventually invalid, and feedback can shorten the valid horizon; duration alone is not a justified repair |
| C REDESIGN_OBJECT_TRAJECTORY_AND_DURATION_TOGETHER | Viable future explicitly model-space design after selecting a separate experiment role, valid geometry and endpoint; no values chosen |
| D HOLD_STIMULUS_AFTER_SAFE_GEOMETRY | Adds hold semantics. Frozen relative-column input loses body feedback; a held world object could retain feedback but changes the scenario and requires declared assumptions |
| E USE_A_PREDECLARED_LOOMING_TIMECOURSE | Useful for a separately named open-loop sensory assay; not a replacement closed loop unless future input still depends on authoritative body state |
| F REQUIRE_VISUAL_GEOMETRY_CALIBRATION_BEFORE_LONGER_BEHAVIORAL_SCENARIO | Required for calibrated retinal/biological claims, not a prerequisite for an honestly uncalibrated model-space world experiment |

A single artifact should not serve both a bounded circuit-fixture role and a
behavior-scale world-experiment role. Keep `LOOMING_CIRCUIT_VALIDATION`;
assess a separate future `LOOMING_WORLD_EXPERIMENT` without adding or exposing
it now. Existing strategic world taxonomy remains unchanged.

## Future design specification and claim budget

Exactly one next action: a bounded design of the **separate model-space looming
world experiment**, jointly addressing:

- Role and measured endpoint: response trajectory and valid closed-loop
  execution, not a required spike, escape or movement.
- Horizon and prescribed object trajectory together, with documented rationale;
  no exact replacement is identifiable from this review.
- Positive-forward geometry over the selected observation window, including
  body feedback; explicit approach/overlap and termination policy.
- Unchanged fixed-centre projection limits; calibration required only before
  claiming biological retinal registration or calibrated behavioral prediction.
- Causal dt scheduling, latency accounting, no final extra interval and
  authoritative body→next geometry→sensory feedback.
- Validation metrics: deterministic replay, geometry validity, stimulus/state
  traces, genuine event/status accounting, and honest zero-output outcomes.

Any later implementation must preserve existing canonical identities and
model parameters, not retune to obtain spikes. Exact horizon, physical spatial
scale, biologically equivalent approach speed, receptive-field registration,
biological model constants and behavioral adequacy are not identifiable here.

Permitted: “The canonical 1.4 ms run validates a closed causal circuit
micro-window under explicit model assumptions.” Not permitted: “1.4 ms is a
complete biological looming experiment,” “longer duration solves the silent
response,” or “six-second playback represents six seconds of neural activity.”

## Verification

Phase 17 `PASS`. Required source replays passed unchanged. Full Python suite:
1,004 passed, 1 deselected, two existing dependency deprecation warnings
(778.83 s). Ruff check, Ruff format check and diff check pass. Frontend:
52 tests passed; lint, typecheck and production build pass. The build's generated
`next-env.d.ts` change was restored, leaving no frontend source diff. Only this
document and a minimal Project Context addition remain. No commit/push.
