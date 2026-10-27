# Continuous ground session v10.5b

Explore uses a browser-local `live_ground_session_v1` with the existing verified HS/DNp15 kernel, 20 ms body intervals, 200 neural substeps and the v3 engineering propulsion and wall recovery. The default pose is unchanged; the session has no random input or seed. A session ID identifies the session and does not enter the model. An explicit valid initial pose is supported by the session contract.

The live engine uses the finite navigation calculations with history retention disabled. Historical v2/v3 engines keep their full histories and existing export/replay contracts. The live session retains at most 512 trajectory positions, 256 left-boundary/accepted-boundary telemetry samples and 128 events by default; capacities are validated and configurable. The leg presentation retains one accepted gait state and advances from the next accepted body pose. The trajectory is a rolling window and is not a complete recording. Complete live export is unavailable; historical finite recording remains in the research tools.

Play starts or resumes; Pause freezes the scientific state; Stop releases the engine while retaining bounded recent diagnostics; Reset reconstructs the initial configuration. A hidden page pauses and requires an explicit resume. The fixed clock schedules at most five 20 ms intervals per animation frame and drops excess wall-time debt. Simulated time counts accepted intervals only. Invalid neural or body state stops the session and leaves the last accepted snapshot available for diagnosis.

The selected neural model influences yaw only. Propulsion, boundary steering, body integration and gait are engineering mechanisms; landmarks are geometric model inputs. This is not a validated biological walking controller. The deterministic dynamics may revisit a path; there is no random walk, obstacle policy or autonomous decision to pause. Sessions do not continue after reload or page closure.

The normal frontend suite includes focused live and finite parity tests. Run the explicit 1,800-second simulated-duration gate separately from `web/`:

```sh
node --expose-gc --import tsx scripts/live-ground-long.ts
```

This measures headless computation, sampled post-GC heap, rolling-buffer sizes and boundary events. It is not a 30-minute real-time browser observation or a biological validation.
