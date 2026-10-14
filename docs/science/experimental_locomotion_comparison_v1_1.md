# Experimental Locomotion v1.1 — synchronized evidence inspection

This is a presentation of the published Python v1 experiment, not a new neural
experiment. `/visual-lab/arena` → **Neural Steering Comparison** loads the same
byte-verified artifact as single-run v1. One clock controls B, C and D; changing
the focus fly preserves playback time. A baseline, single v1, v0 and canonical
Course playback remain separate options.

One V2-F GLB represents the focus condition. B uses a cyan circle/solid trail,
C an amber square/dashed trail, D a lavender diamond/short-dashed trail. Markers
are floor projections of recorded X/Z positions; arrows use recorded heading.
Trail geometry is created once and reveals completed sampled segments. The
marker/fly interpolates between adjacent boundaries; no extrapolation occurs.
The source stores unwrapped headings with small adjacent increments, so its
existing linear interpolation preserves the intended rotation. No angle is
normalized in the scientific trajectory. Current **B minus C/D** angular
comparison uses `atan2(sin(delta), cos(delta))`, a signed shortest separation
within ±π. Whole-run heading maxima use absolute **unwrapped** differences at
stored boundaries. Spatial separation is X/Z endpoint separation, distinct from
the difference in accumulated traveled distances. Neural readout, speed and
contact are from the preceding boundary; final-boundary outgoing readout remains
unavailable rather than invented zero.

B/C share landmarks at X=±0.6, Z=+0.4. C computes the neural model but disables
only its contribution to heading. D enables steering with Z=−0.4. Both stimulus
geometries are drawn from the validated configuration. Propulsion is unchanged
at 0.18 presentation units/s. This is precomputed Python simulation replay with
connectome-informed neural steering and engineering propulsion, not live browser
neural execution, biological walking, calibrated speed, muscle forces or
spontaneous exploration.

Independent stored-boundary checks at four seconds:

| Condition | X | Z | Heading rad |
|---|---:|---:|---:|
| B | 0.7062456690702007 | 0.23128556782922474 | 1.130897108380308 |
| C | 0.7200000000000022 | 0.12187743186950682 | 1.5707963267948966 |
| D | 0.7087699494066295 | 0.015621730315911193 | 1.9052698814015008 |

B−C maximum absolute unwrapped heading difference is 0.6766798814084118 rad at
5.52 s. B−D is 1.1783775624855197 rad at 5.60 s; maximum planar endpoint separation
is 0.4764494359566599 units at 5.58 s. These are whole-record maxima, not current
values. First contacts: C X wall 5.38 s, B Z wall 5.50 s, D X wall 5.58 s.
Recorded translation stops while modeled heading may continue.

Unchanged source identities:

- Logical artifact: `4d7c791224f21ecf677df81d2127a6f8b753974694b6b324afc1948da3fb9064`.
- Raw JSON SHA-256: `17d335358a4f5cf4ed98b9682b103a81419cf82504203ce1bc72a7d76285d748`.
- Configuration: `a916769c730174b3d631ccda9df0dd89479cd1b12f43be250b856c1782736e2d`.
- Result: `b4b1ac2737cfca5f5e1d2d06050e5b0ab063d22f14f59bae0115e7fe368c95aa`.

Validation uses the existing strict TypeScript artifact parser plus focused
comparison tests with independently recorded values. Browser checks exercise
Play/Pause/Resume/Reset/Seek/end, focus switching, four-second telemetry, actual
Three.js marker positions, contacts, corrupt-data rejection, single-run controls,
and desktop/narrow layouts. Lint, typecheck, frontend tests, build and diff checks
are required. Scientific source files and original JSON remain byte-identical;
existing canonical/frozen identities are checked without repeating neural runs.
No Python models or biological authority were changed.

Final local gates: 140 frontend tests passed (six new focused comparison tests),
lint, typecheck, production build and diff checks passed. Desktop and 390-pixel
browser checks passed with no execution errors, including actual Three.js marker
positions. SwiftShader was used; these measurements do not establish hardware
GPU performance. Existing Python validation is reused because Python and the
scientific artifacts are unchanged; no new neural simulation was executed.
