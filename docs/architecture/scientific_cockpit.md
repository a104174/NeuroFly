# Scientific Cockpit v1 (Phase 5J)

The read-only route `/experiments/[artifactId]/cockpit` composes one persisted
experiment with the validated six-body MaleCNS morphology sample and Phase 5I
structural projection. It is an inspection workspace, not a simulation runner
or new scientific artifact. The experiment catalogue links to the route; the
standalone playback and dedicated morphology inspector remain available.

## Sources and association

The experiment summary and timeline are the dynamic authority. The server
checks their shared artifact ID, dataset `male-cns:v1.0`,
`looming_giant_fiber_v1` candidate/version, direct-visual-to-DNp01 graph scope,
committed circuit-file integrity hashes, exact time grid, and DNp01 identities.
The morphology association is pinned to artifact
`a3f090d5309d9ede0e9e0f78343a618a4bafba3fea91e5a27d37927d5ec55f79`,
official bulk SWC RAW source mode, candidate/dataset, and the six audited body
identities. The structural layer must match the Phase 5I projection ID, those
six body mappings, dataset/candidate, and the same circuit integrity hashes.
Association is not inferred from filenames, side, or geometric proximity.

The experiment is mandatory: an unavailable or incompatible run prevents the
cockpit from opening. Morphology and connectivity are independently read-only
optional layers: failure produces an explicit unavailable message, never mock
structure. Each static source is requested once per page load, not on playback
ticks. No opening action invokes `ExperimentRunner`, neuPrint, or SWC acquisition.

## One experiment clock

`ScientificCockpit` owns the existing `useExperimentPlayback` hook, shared body
and component selection, body visibility, and structural-layer toggle, and passes
its derived `sceneState` to the existing `PlaybackCanvas`. The same playback
time in milliseconds drives the world scene, plot cursors/readouts, selected
DNp01 boundary data, and event position. Seek, pause, play, reset, and existing
presentation playback rates use that one hook. Browser render frames do not
become simulation steps; recorded interval values use the established floor
selection and recorded boundary values use their stored boundary index.

## Scientific meaning

- Source structure: body IDs, types, sides, raw SWC nodes/components and native
  frame/unit; four directed CircuitContract LC4/LPLC2 → DNp01 relations and
  their exact structural contact-count weights. Straight connectors remain
  schematic body-bound-center presentation paths, not synapse locations.
- Simulation assumptions: the existing LIF model and sensory encoder, shown
  only by their recorded IDs and the outputs already persisted in the run.
- Experiment results: angular size `theta_rad` (rad) and LC4/LPLC2 type-level
  drive (`mV_eq`) at stored intervals; exact DNp01 10001/10010 membrane (`mV`),
  synaptic state (`mV_eq`), and spike times at stored boundaries where present.
  Visual-type drives are not body traces for the four selected LC4/LPLC2 cells.
- Presentation state: body/component selection, visibility, structural toggle,
  highlighting, camera focus, plot cursor, and panel layout. Morphology and
  connectivity geometry stay static during playback; the fly scene is not
  aligned to MaleCNS source coordinates or a claim of motor behavior.

The event list is a deterministic presentation derivation of experiment
start/end boundary times and persisted selected-DNp01 spike times. Ordering is
time, then boundary/spike kind, then body ID. “Current” means the event matches
the selected stored boundary. These rows do not assert threat detection,
decisions, behavior, or other unrecorded events.

The cockpit deliberately has no whole-brain activity, body-specific LC4/LPLC2
trace, activity-colored skeleton, synapse coordinates, live streaming, reward,
learning, policy, motor control, or fly-to-connectome alignment. Future cockpit
polish can improve navigation and layout without changing these contracts.
