"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import type { ExperimentTimeline } from "@/lib/neuroflyClient";
import {
  advancePlayback,
  createPlaybackClock,
  createScenePresentationContext,
  deriveSceneState,
  pausePlayback,
  playPlayback,
  resetPlayback,
  seekPlayback,
  setPlaybackRate as updatePlaybackRate,
  type PlaybackRate,
} from "@/lib/playback";

export function useExperimentPlayback(timeline: ExperimentTimeline) {
  const [clock, setClock] = useState(() => createPlaybackClock(timeline.start_ms));
  const presentationContext = useMemo(
    () => createScenePresentationContext(timeline),
    [timeline],
  );

  useEffect(() => {
    if (!clock.isPlaying) return;
    let animationFrame = 0;
    let previousWallTimeMs: number | null = null;

    const tick = (wallTimeMs: number) => {
      if (previousWallTimeMs !== null) {
        const elapsedWallTimeMs = wallTimeMs - previousWallTimeMs;
        setClock((current) =>
          advancePlayback(
            current,
            elapsedWallTimeMs,
            timeline.start_ms,
            timeline.end_ms,
          ),
        );
      }
      previousWallTimeMs = wallTimeMs;
      animationFrame = requestAnimationFrame(tick);
    };

    animationFrame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animationFrame);
  }, [clock.isPlaying, timeline.end_ms, timeline.start_ms]);

  const play = useCallback(
    () => setClock((current) => playPlayback(current, timeline.end_ms)),
    [timeline.end_ms],
  );
  const pause = useCallback(
    () => setClock((current) => pausePlayback(current)),
    [],
  );
  const reset = useCallback(
    () => setClock((current) => resetPlayback(current, timeline.start_ms)),
    [timeline.start_ms],
  );
  const seek = useCallback(
    (timeMs: number) =>
      setClock((current) =>
        seekPlayback(current, timeMs, timeline.start_ms, timeline.end_ms),
      ),
    [timeline.end_ms, timeline.start_ms],
  );
  const setPlaybackRate = useCallback(
    (rate: PlaybackRate) =>
      setClock((current) => updatePlaybackRate(current, rate)),
    [],
  );
  const sceneState = useMemo(
    () => deriveSceneState(timeline, clock.currentTimeMs, presentationContext),
    [clock.currentTimeMs, presentationContext, timeline],
  );

  return {
    currentTimeMs: clock.currentTimeMs,
    durationMs: timeline.end_ms - timeline.start_ms,
    isPlaying: clock.isPlaying,
    playbackRate: clock.playbackRate,
    sceneState,
    play,
    pause,
    reset,
    seek,
    setPlaybackRate,
  };
}
