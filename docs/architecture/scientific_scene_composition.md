# Scientific spatial overlay and 3D scene composition (Phase 5D)

Phase 5D makes the persisted-experiment scene easier to read without adding
biological spatial data. The fly, looming corridor, pathway lines, activity
nodes, camera, colors, and scale all occupy a versioned presentation space:
`neurofly_scene_layout_v1`. Its coordinate-space identifier is
`NEUROFLY_PRESENTATION_MAPPING`.

These coordinates are not MaleCNS, soma, neuropil, or anatomical coordinates.
They must not be used as evidence about biological location or distance.

## Layout contract

`web/src/lib/sceneLayout.ts` is the single presentation-layout definition. It
contains immutable camera and grid settings, the fly presentation origin, the
looming proxy corridor, separate LC4 and LPLC2 anchors, and separate DNp01
10001 and 10010 anchors. Coordinates no longer live as unrelated literals in
scene components.

The layout identifier is presentation provenance only. It has no role in an
experiment config, result, artifact, comparison, or empirical-protocol
identity.

## Abstract pathway overlay

Four restrained aggregate lines show the permitted explanatory direction:

```text
LC4   -> DNp01 10001 / DNp01 10010
LPLC2 -> DNp01 10001 / DNp01 10010
```

The lines are not axons, skeletons, synapses, repaired neurites, or anatomical
routes. They do not instantiate fake neuron populations. LC4 and LPLC2 keep
different anchors, colors, labels, raw feature/drive values, and bounded
presentation intensities. DNp01 bodies 10001 and 10010 keep different anchors,
IDs, raw membrane/synaptic values, and persisted-boundary spike flags.

`derivePresentationOverlayState()` is pure and consumes the existing
`ExperimentSceneState`. It retains every raw value unchanged. Existing bounded
pathway/DNp01 presentation levels are mapped monotonically into opacity in the
fixed range `[0.16, 0.82]`; this is visual contrast, not firing probability,
biological efficacy, or a new scientific activity transform. Persisted spike
timestamps remain authoritative. The visible ring is still a presentation
hold at the selected persisted boundary, not an action-potential waveform.

## Looming presentation

Persisted `theta_rad` and
`angular_expansion_velocity_rad_s` remain the scientific readouts. The scene
uses the Phase 5B bounded looming presentation level to position and size a
sphere along a subtle presentation corridor. It does not recompute physical
distance, rerun `LoomingStimulus`, or assert that the corridor is an anatomical
line of sight. The corridor, sphere scale, material, and scene coordinates are
visual assumptions.

## Current-value overlay and provenance

At the selected playback time, readable UI exposes:

- playback time, exact selected state-boundary time, and exact interval start,
  all in milliseconds;
- theta in radians and angular expansion in radians per second;
- separate LC4 and LPLC2 normalized features;
- separate DNp01 10001 and 10010 membrane values in millivolts;
- the artifact's empirical status, including `NOT_EVALUATED`.

The visual-asset provenance block separately displays
`neurofly_fly_visual_v1`, asset version, a GLB SHA-256 prefix, Blender version,
and `PRESENTATION ONLY`. It is explicitly separate from the experiment
provenance elsewhere on the page. Changing a visual asset or scene layout does
not change scientific identity.

The adjacent legend divides the scene into:

- **Persisted data:** simulation time, theta, angular expansion, LC4/LPLC2
  model values, and DNp01 state/spikes.
- **Presentation mapping:** fly/pathway placement, looming corridor, colors,
  bounded intensity, camera, and normalized scene scale.

All unique scientific information remains textual and does not rely on color
or WebGL.

## Preserved playback boundary

Phase 5D does not change `web/src/lib/playback.ts`, its wall-clock-driven
playback controller, boundary/interval floor lookup, or `ExperimentSceneState`.
There is no interpolation, time shifting, resampling, or frame-per-neural-step
assumption. The R3F scene observes the selected persisted state and never steps
the model.

The controlled GLB fly remains stationary. No DNp01 value causes movement,
wing motion, escape, or motor output. The scene adds no physics,
postprocessing, full graph, connectome rendering, or empirical validation.

## Future biological spatialization boundary

Rendering actual MaleCNS neurons or skeletons is a separate scientific phase.
It would require verified coordinate data, coordinate-frame provenance,
body-ID mapping, a skeleton-fragmentation policy, and explicit handling of any
repair geometry. Those future biological coordinates must remain clearly
distinguished from `NEUROFLY_PRESENTATION_MAPPING`.
