# Neural Explorer spatial layout refinement — v10.5f-a

The V10.5E explorer gave the morphology viewer most of the row while capping
its inspector at 285 px. At intermediate viewport widths, a fixed 245 px
inspector could also remain cramped inside the Lab's narrower content column.

V10.5F-A keeps the existing explorer component and single React Three Fiber
canvas. On wide containers, the layout now allocates space flexibly at roughly
63:37, with a 320 px minimum inspector track. The named inline-size container
makes the layout respond to the explorer's actual Lab column: below 820 px the
viewer and inspector stack, and the selected-structure list remains available
in two columns. Below 480 px, metadata fields stack and identifiers wrap; the
canvas height follows available container width with a usable minimum. These
rules also cover 390 px and 320 px content widths without a separate mobile
component tree.

Selection ownership, session telemetry, chart history, the 3D scene and
scientific values are unchanged. React Three Fiber observes its canvas wrapper
resize, so the existing canvas remains mounted through CSS reflow. MaleCNS
anatomy, HS/DNp15 computational proxies, neural motor projection and engineering
responses retain their existing meanings.

The automated frontend suite, lint, typecheck and production build are the
validation gates for this layout-only change. Full visible-browser acceptance
at desktop, 390 px and 320 px remains deferred; this note does not claim visual
acceptance or a new performance measurement. The next small UX slice can refine
information hierarchy, morphology framing and activity-chart readability.
