# Screen-space morphology picking — v10.5f-d

The default Three.js Line threshold of one shared presentation unit admitted
segments far from the pointer, especially after Focus. Each existing skeleton
now supplies a local raycast implementation. It uses a 6 CSS-pixel radius, an
engineering interaction affordance rather than anatomical thickness. R3F still
owns pointer-down/click eligibility, depth ordering and propagation; exact body
IDs and the single selectedId remain unchanged.

Candidate generation examines the existing segment endpoints on raycast requests.
Homogeneous six-plane clipping removes invisible portions before perspective
division. Trivial clip rejection and an inflated projected segment AABB form a
conservative broad phase; no world-radius raycast can discard valid candidates.
The narrow phase measures pointer distance to the visible projected segment.
Perspective-correct interpolation recovers its 3D point and view depth. The
frontmost eligible segment per body is returned; equal depths retain stable
segment order. R3F retains its normal object ordering for remaining exact ties.
Current camera matrices, world matrix and actual R3F CSS dimensions are used;
DPR is deliberately absent. Invalid inputs produce no selection, without an
unsafe fallback. No geometry, camera, model or scientific contract changes.

The real regression reproduces the old first hit on body 11215 while pointing
at a body-10015 vertex. That old winning segment is outside 6 px and is rejected.
In Overview a different 11215 segment is legitimately within 4.70 px and remains
frontmost; forcing 10015 would violate the chosen overlap policy. After Focus,
11215 is ineligible and 10015 wins. Real probes (12 vertices/body, visible only):
Overview 96 rays, 80 with multiple eligible bodies, 28 old winning body IDs
rejected; Focus 44 rays, 33 overlaps, 23 old winning IDs rejected. These are
geometric probes, not human misclick rates. Diagnostic loops include old and
new picking plus assertions; timings do not isolate renderer/FPS overhead.

Work is O(35,457 segments) per complete raycast request. Existing click-only
handlers mean R3F filters these objects out of ordinary pointer-move raycasts.
There is no simulation-tick/frame scan, extra canvas, parsing, polling or GPU
pass. Pointer-down, pointer-up and click may each request raycasts. Broad-phase
rejection is per segment; no incomplete world-threshold candidate set is used.

The existing drag/pan/touch click risk remains outside this slice. List selection
remains available for true projected overlaps. VISUAL_ACCEPTANCE_DEFERRED.
PERFORMANCE_REGRESSION_NOT_VERIFIABLE. Unit geometry and real-data probes do not
establish browser usability or human interaction acceptance.

Automated validation: 410/410 full frontend tests, 5/5 focused picking tests,
zero skips; ESLint, TypeScript, production build and diff checks passed. Protected
runtime/manifest hashes and all eight SWC hashes remain unchanged. One diagnostic
run took about 372 ms for 96 Overview probes and 218 ms for 44 Focus probes,
including both old/new picking and assertions; these are not isolated latency
benchmarks or FPS measurements.
