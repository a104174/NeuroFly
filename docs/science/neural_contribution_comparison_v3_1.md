# Neural Contribution Comparison v3.1

This is an on-demand paired computational intervention within Continuous Arena
Navigation v3. Both worlds use the same actual deterministic v3 simulator.
Only `NEURAL_TO_HEADING_ENABLED` differs: ON maps to `neural`, OFF maps to
`output_disabled`. OFF still advances all six HS and both DNp15 states with the
same equations. Propulsion and geometric boundary recovery remain enabled.
No biological lesion, muscle actuation, learning or calibrated gait is implied.

## Matched experiment and preserved source

The input is a semantically validated v3 session, including its original logical
identity, configuration, event log and supplied trace for verification. Neither
condition reads imported positions or neural states to construct a trajectory.
Both start at the declared initial pose and zero neural state. The source
MaleCNS/neural authority, initial visual plane, engineering parameters, arena,
randomness policy NONE and external events match. The only implementation
configuration difference is `mode`, representing the output-application switch.
Each world recalculates observations from its own evolving pose. Later sensory
readouts, geometric steering and contact histories can consequently differ.

The comparison reconstructs **only the completed recorded prefix**, ending at
`parent.log.stop_step * 0.02` seconds. No unstated future stimulus is supplied.
A pending request at the stopped boundary is retained in the original parent
but not applied in either comparison. The live session is suspended before
capture and retains its engine, state, pending requests and identity. Returning
from comparison resumes the original session only when the user presses Play.
A validated imported source identity is preserved until the live session changes.

Each condition executes exactly 200 substeps of 0.1 ms per 20 ms body interval.
The same existing neural, sensory, propulsion and boundary methods are called.
Initial configuration comes from the source log, not its final state. Calculation
is chunked in 50 body intervals with UI yields; those yields do not affect the
scientific clock. The source's semantic validation also reconstructs its prefix
separately. No new solver, controller or model parameter is introduced.

## Sampling and numerical interpretation

Complete boundaries are recorded, including old HS/DNp15 states and outgoing
interval readouts. The final boundary is inspected without another neural or
body update; it has no outgoing readout. The inspector holds readout and applied
angular contributions over their declared interval, while interpolating position,
heading and accumulated traveled distance for display. Heading interpolation uses
the shortest local angular increment; no full rotation is inserted at wrapping.
No pose is extrapolated beyond the prefix.

Current position separation is Euclidean X/Z separation. Current angular
difference is `atan2(sin(theta_ON-theta_OFF),cos(theta_ON-theta_OFF))` in ±π.
The maximum is the maximum **absolute wrapped** difference, not accumulated
rotations. The algorithm also checks crossings of odd multiples of π between
boundaries: the interpolated maximum can occur between samples. Spatial separation
of linearly interpolated segments is convex, so its maximum occurs at a boundary.
Maxima over the whole prefix are labeled separately from current cursor values.

Contact events are reconstructed from computed boundary states. A wall-label
change while still stopped is `WALL_CHANGE`, not a recovery. `RECOVERY` means
contact-to-free, consistent with the v3 contact episodes. Counts and actual event
timestamps are displayed separately for ON/OFF; they are never synchronized
artificially. Total paired effects include pose-mediated changes to sensory input
and engineering recovery. They are not the integral of the neural term alone.

## Independent reference and controls

A small Python wrapper calls the unchanged v3 reference twice and independently
calculates paired metrics/contact transitions. Existing frozen kernels and all
historical artifacts remain unchanged. Reference regeneration:

```sh
mkdir -p /tmp/neurofly-paired-reference
.venv/bin/python -m neurofly.neural_contribution_comparison_reference \
  --output /tmp/neurofly-paired-reference/reference.json
```

Full traces remain external. The committed fixture contains selected complete
boundaries plus source pins and event/metric evidence. Its canonical reference ID
is `cd4f1b6b5acd8e1d8c381bd98f7376139245f22fc03fa52d66b5be3d5dfab67e`.
Every one of the 1501 boundaries per condition was compared against Python for
both reference cases; maximum model-space discrepancy was
4.971578704271451e−13 versus the unchanged absolute tolerance 1e−8.

| 30 s reference | ON / OFF distance | ON / OFF contacts and recoveries | Maximum separation | Final separation |
|---|---:|---:|---:|---:|
| No intervention | 4.39112 / 5.17504 | 3/3 / 2/2 | 0.83560 at 30 s | 0.83560 |
| Switch Z at 2 s | 4.36926 / 5.17504 | 4/4 / 2/2 | 0.80462 at 23.96 s | 0.66252 |

Both reference cases reach maximum wrapped angular separation π; the first
crossings occur at approximately 21.51303 and 21.68189 seconds. Their final
wrapped differences are 0.85924 and 1.17117 rad respectively. More distance in
OFF does not establish better biological navigation. OFF's body trajectory is
unchanged by visual-plane changes because neural output application is disabled,
but its computed sensory and neural trajectories do change.

Before the first heading divergence, sensory inputs and neural states/readout
match and the geometric contribution is zero; the only angular difference is
the applied neural term. Later observations and contact histories diverge as
expected. Tests also cover multiple external switches, source preservation,
strict event timing, arbitrary JSON key order, finite values, prefix endpoints,
independent analytical interpolation/wrapping cases and semantic tampering.

## Contract, import and visualization

Schema `neural_contribution_comparison_v3_1` includes the validated parent session,
compact matched configuration, condition definitions, event identity, model/source
pins, timebase, complete bounded results and independent config/result/logical
hashes. The logical ID is not the raw JSON checksum. The hashing convention reuses
v3's finite sorted-key canonical serialization.

Import verifies hashes, semantically validates the parent, reconstructs both
worlds and compares all telemetry and metrics. Recomputed superficial hashes
cannot validate fabricated poses, applied neural terms or condition metadata.
Computed numerical differences up to 1e−8 permit libm rounding; model parameters,
clock, event and discrete-state metadata remain exact. The displayed and exported
result after import is the recalculated result with its proper canonical identity;
the original imported file identity is shown as a verified reference. Parent
identity remains preserved. Source and bulk outputs are not committed.

One existing high-quality GLB and canvas are reused. ON uses cyan/ring/solid trail,
OFF gold/square/dashed trail. A single playback clock drives both markers and the
focused fly. Focus preserves time; Play/Pause/Reset/Seek and event jumps are
presentation controls only. Landmark geometry follows the same external visual
plane at each shared timestamp. Returning does not reset the source simulation.
The historical B/C/D scientific contract is unchanged; only the common rendering
shape accepts additional condition keys.

Local acceptance used a real recorded 15.3-second v3 session with external switches
at 2.20 and 8.30 seconds. ON/OFF were reconstructed deterministically, with peak
separation 0.29739 at 12.02 s and peak wrapped heading 1.09712 rad at 10.86 s.
ON had two recoveries, OFF one. Every recorded paired boundary agreed with Python
to 1.8189894035458565e−12. Play/Pause/Reset/Seek, focus, actual Three.js marker/body
alignment, rehashed false-neural-output rejection, exact original-session identity
on return and deterministic re-import/regeneration passed. Desktop and 390 px
layouts passed, with one full GLB and no runtime errors. Initial shader warm-up
and SwiftShader rendering stalls are distinct from simulation cost; software
rendering is not a physical GPU benchmark.

The underlying v3 neural model and engineering gains remain uncalibrated.
The observation model is not a complete retina, and this output intervention
does not establish biological synaptic necessity or physiological motor effects.
All historical biological-sign UNKNOWN evidence remains unchanged.

Quality checks completed: 1,692 Python tests passed, one authenticated integration
was deselected under the existing policy, and two dependency deprecation warnings
remained. The final affected reference tests were also checked independently.
All 173 frontend tests, lint, typecheck, production build, Ruff lint/format and
diff checks passed. D2.2 archive identity and historical scientific artifact/source
identities were verified unchanged. Protected Preview acceptance is checked
separately after deployment; the browser figures above describe local validation.
