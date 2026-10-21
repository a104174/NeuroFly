# 3D Flight Trajectory Visualization v8.2

The v8.2 trajectory is a read-only rendering of validated `FlightEngine` boundary frames. It does not change the v8 flight plant, the v8.1 program/run schemas, replay inputs, result hashes, or scientific experiment records.

## World-space source

`FlightFrame.position` is the authoritative `[x, y, z]` body-anchor position in the arena's Y-up coordinate system. `flightScene(frame)` places the rendered body at that same anchor. The trajectory line writes those three recorded values directly into a Three.js `BufferGeometry`; it does not flatten, offset, smooth, or resample them. Frame index and time are checked against the fixed 20 ms boundary convention before positions are exposed to the renderer.

The line and marker buffers are allocated per selected run/layer and updated in place. Their geometry uses the same world coordinates as the body transform. Hiding the layer unmounts and disposes its owned geometry and material. Cursor movement only changes `drawRange`.

## Playback and future-data visibility

Progressive mode draws boundaries `0..cursorStep`, limited to frames already recorded by the selected engine. Pause leaves the range stable. Backward/forward seek changes the range over the same validated frame history; reset returns it to the initial boundary. The cursor never advances the plant by itself.

`Full Recorded Trajectory` is disabled until the selected program has reached its configured terminal boundary. It then displays the completed/reconstructed record by explicit user choice. The same rule applies to event markers. While a run is incomplete, neither its line nor its markers disclose later frames.

## Events and comparison

Markers are derived from actual frame `TRANSITION` and `CONTACT` records. Marker positions are looked up at each event's recorded boundary. The final-position marker appears only when the selected engine has recorded its configured terminal boundary; it is not a landing marker. A run that ends airborne therefore has no fabricated landing/contact event.

The optional reference overlay uses a separately reconstructed `createFlightTrial()` reference through the existing `FlightEngine`. It is hidden when the current program is the reference itself. Both layers use their original XYZ positions and the same 20 ms cursor. Current and final separation are computed directly from corresponding recorded frame positions, never from screen-space vertices.

## Classification and limits

This is `ENGINEERING_3D_FLIGHT_TRAJECTORY`, viewed from `ENGINEERING_3D_KINEMATIC_FLIGHT_PLANT` output. Trajectory display options have no input to the flight plant and do not alter its numerical identity. They are not neural events, aerodynamic evidence, or biological flight telemetry.
