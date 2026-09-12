import assert from "node:assert/strict";
import { test } from "node:test";

import type {
  BodyTelemetry,
  ExperimentTimeline,
} from "../src/lib/neuroflyClient";
import {
  advancePlayback,
  createPlaybackClock,
  createScenePresentationContext,
  deriveSceneState,
  pausePlayback,
  playPlayback,
  resetPlayback,
  seekPlayback,
  selectTimelineSample,
  setPlaybackRate,
} from "../src/lib/playback";

function body(
  bodyId: 10001 | 10010,
  membraneMv: number[],
  synapticStateMveq: number[],
  spikeTimesMs: number[],
): BodyTelemetry {
  return {
    body_id: bodyId,
    neuron_type: "DNp01",
    soma_side: bodyId === 10001 ? "R" : "L",
    time_unit: "ms",
    times_ms: [0, 1, 2, 3],
    step_times_ms: [0, 1, 2],
    membrane_unit: "mV",
    membrane_mv: membraneMv,
    synaptic_state_unit: "mV_eq",
    synaptic_state_mveq: synapticStateMveq,
    external_drive_unit: "mV_eq",
    external_drive_mveq: [0, 0, 0],
    incoming_coupling_unit: "mV_eq",
    incoming_coupling_mveq: [0, 0.1, 0.2],
    spike_times_ms: spikeTimesMs,
  };
}

function timelineFixture(): ExperimentTimeline {
  return {
    schema: "experiment_api_v1",
    kind: "experiment_timeline",
    artifact_id: "a".repeat(64),
    time_unit: "ms",
    dt_ms: 1,
    duration_ms: 3,
    start_ms: 0,
    end_ms: 3,
    times_ms: [0, 1, 2, 3],
    step_times_ms: [0, 1, 2],
    interval_semantics: "step_values_apply_on_[t_n,t_n+dt)",
    theta_unit: "rad",
    theta_rad: [0.1, 0.2, 0.4],
    angular_expansion_velocity_unit: "rad/s",
    angular_expansion_velocity_rad_s: [1, 2, 4],
    lc4_normalized_feature: [0.1, 0.4, 0.8],
    lplc2_normalized_feature: [0.2, 0.5, 0.9],
    drive_unit: "mV_eq",
    lc4_drive_mveq: [1, 4, 8],
    lplc2_drive_mveq: [2, 5, 9],
    selected_body_telemetry: [
      body(10001, [-65, -61, -54, -50], [0, 0.2, 0.5, 0.7], [2]),
      body(10010, [-65, -60, -49, -47], [0, 0.3, 0.8, 1.0], [1, 3]),
    ],
  };
}

test("timeline selection uses floor semantics without interpolation", () => {
  const timeline = timelineFixture();
  assert.deepEqual(selectTimelineSample(timeline, 0), {
    playbackTimeMs: 0,
    boundaryIndex: 0,
    boundaryTimeMs: 0,
    intervalIndex: 0,
    intervalStartMs: 0,
  });
  assert.deepEqual(selectTimelineSample(timeline, 1), {
    playbackTimeMs: 1,
    boundaryIndex: 1,
    boundaryTimeMs: 1,
    intervalIndex: 1,
    intervalStartMs: 1,
  });
  assert.deepEqual(selectTimelineSample(timeline, 1.75), {
    playbackTimeMs: 1.75,
    boundaryIndex: 1,
    boundaryTimeMs: 1,
    intervalIndex: 1,
    intervalStartMs: 1,
  });
  assert.deepEqual(selectTimelineSample(timeline, 3), {
    playbackTimeMs: 3,
    boundaryIndex: 3,
    boundaryTimeMs: 3,
    intervalIndex: 2,
    intervalStartMs: 2,
  });
  assert.equal(selectTimelineSample(timeline, -10).playbackTimeMs, 0);
  assert.equal(selectTimelineSample(timeline, 10).playbackTimeMs, 3);
});

test("playback clock advances from wall time and stops exactly at the end", () => {
  let clock = createPlaybackClock(0);
  clock = playPlayback(clock, 3);
  clock = advancePlayback(clock, 0.5, 0, 3);
  assert.equal(clock.currentTimeMs, 0.5);

  clock = setPlaybackRate(clock, 2);
  clock = advancePlayback(clock, 0.75, 0, 3);
  assert.equal(clock.currentTimeMs, 2);

  clock = pausePlayback(clock);
  assert.strictEqual(advancePlayback(clock, 10, 0, 3), clock);

  clock = playPlayback(clock, 3);
  clock = advancePlayback(clock, 10, 0, 3);
  assert.equal(clock.currentTimeMs, 3);
  assert.equal(clock.isPlaying, false);

  clock = seekPlayback(clock, -4, 0, 3);
  assert.equal(clock.currentTimeMs, 0);
  clock = seekPlayback(clock, 9, 0, 3);
  assert.equal(clock.currentTimeMs, 3);
  assert.equal(clock.isPlaying, false);
  clock = resetPlayback(clock, 0);
  assert.deepEqual(clock, { currentTimeMs: 0, isPlaying: false, playbackRate: 2 });
});

test("scene state keeps pathways and DNp01 bodies distinct at exact samples", () => {
  const timeline = timelineFixture();
  const context = createScenePresentationContext(timeline);
  const scene = deriveSceneState(timeline, 1.75, context);

  assert.equal(scene.boundaryIndex, 1);
  assert.equal(scene.boundaryTimeMs, 1);
  assert.equal(scene.intervalIndex, 1);
  assert.equal(scene.intervalStartMs, 1);
  assert.equal(scene.thetaRad, 0.2);
  assert.equal(scene.lc4NormalizedFeature, 0.4);
  assert.equal(scene.lplc2NormalizedFeature, 0.5);
  assert.equal(scene.lc4DriveMveq, 4);
  assert.equal(scene.lplc2DriveMveq, 5);
  assert.equal(scene.dnp01[10001].bodyId, 10001);
  assert.equal(scene.dnp01[10001].membraneMv, -61);
  assert.equal(scene.dnp01[10010].bodyId, 10010);
  assert.equal(scene.dnp01[10010].membraneMv, -60);
  assert.equal(scene.dnp01[10001].spikedAtSelectedBoundary, false);
  assert.equal(scene.dnp01[10010].spikedAtSelectedBoundary, true);
  assert.equal("behavior" in scene, false);
});

test("final scene combines the final state boundary with the final valid interval", () => {
  const timeline = timelineFixture();
  const scene = deriveSceneState(timeline, 100);
  assert.equal(scene.playbackTimeMs, 3);
  assert.equal(scene.boundaryTimeMs, 3);
  assert.equal(scene.intervalStartMs, 2);
  assert.equal(scene.thetaRad, 0.4);
  assert.equal(scene.dnp01[10001].membraneMv, -50);
  assert.equal(scene.dnp01[10010].membraneMv, -47);
});
