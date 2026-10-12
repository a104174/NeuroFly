# Arena A+C v0.2 — canonical orientation-only replay

The static arena remains the default. Course Replay explicitly loads only
EXPLORATORY_COURSE_CONTROL through the existing server action and strict Course
parser. Frozen Phase30 validation remains in the backend. Missing/invalid data
shows an error and a clearly labelled static specimen, never fallback motion.

One parent cursor drives courseScene, the timeline and exact lower-boundary
telemetry. The existing six-second presentation helper advances it; no physics,
yaw integration, speed selector or second scientific clock exists. Pause freezes,
seek pauses at an integer boundary, Reset Replay returns to zero and completion
stops without looping. Switching modes cancels playback and invalidates pending
requests. Camera presets and Reset View affect only the camera.

For runtime asset anchor a, arena offset o and approved scale s=.30:
c=o+s*a; p=c+Ry(courseScene.renderRotation)*s*(q-a).
The existing asset fit is identity for this approved GLB and is checked before
playback. The presentation anchor stays fixed. Positive yaw rotates +Z toward
+X. One abstract cycle means 2π render radians; no magnification. Peak angle is
only .36 display degrees and the final residual is retained. A conservative
horizontal bounding circle plus vertical bounds covers all rotations, including
interpolated poses. Incompatible chamber/asset configurations fail explicitly;
no clamping, model resizing or frame relocation.

Visible Portuguese qualification: replay canónico de orientação de modelo,
apresentado numa visualização laboratorial; posição fixa de apresentação;
translação não modelada; a câmara não participou na simulação; sem colisões.
The orientation and yaw drive are abstract model coordinates, not calibrated
biological angles or angular velocity. MaleCNS structural evidence, modelling
assumptions, frozen outputs and third-party visual geometry remain distinct.
No wall stimuli, locomotion, wingbeat, retinal imagery or new scientific state.
Initial observation=null and final external increment=null remain unavailable,
never converted to zero. The standalone fly viewer and scientific pages retain
their defaults. No backend/API, canonical data or runtime asset changes.
