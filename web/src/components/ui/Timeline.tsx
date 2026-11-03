"use client";

import { useRef } from "react";
import { timelineStepFromKey, timelineValueText } from "@/lib/timelineKeys";
import styles from "./Timeline.module.css";

export interface TimelineMarker { readonly id: string; readonly step: number; readonly label: string }

/**
 * Playback timeline (brief section 6). A slider with `aria-valuetext`, a play button, the time in
 * mono, a speed menu, and labelled event markers that are real buttons. The step is the one
 * playback clock: every panel reads the same step.
 */
export function Timeline({ step, steps, timeLabel, playing, ended, noData, onPlayPause, onStep, rate, rates, onRate, markers = [], onMarker }: {
  step: number;
  steps: number;
  timeLabel: string;
  playing: boolean;
  ended?: boolean;
  noData?: boolean;
  onPlayPause: () => void;
  onStep: (step: number) => void;
  rate: number;
  rates: readonly number[];
  onRate: (rate: number) => void;
  markers?: readonly TimelineMarker[];
  onMarker?: (marker: TimelineMarker) => void;
}) {
  const track = useRef<HTMLDivElement>(null);
  const last = Math.max(0, steps - 1);
  const fraction = last === 0 ? 0 : step / last;
  const fromPointer = (clientX: number) => {
    const box = track.current?.getBoundingClientRect();
    if (!box || box.width === 0) return;
    onStep(Math.round(Math.max(0, Math.min(1, (clientX - box.left) / box.width)) * last));
  };
  if (noData) return <div className={styles.timeline} data-state="no-data"><p className={styles.empty}>No timeline data is available for this run.</p></div>;
  return (
    <div className={styles.timeline} data-state={ended ? "ended" : playing ? "playing" : "paused"}>
      <button type="button" className={styles.play} onClick={onPlayPause} aria-label={ended ? "Replay from the start" : playing ? "Pause" : "Play"}>
        {ended ? "Replay" : playing ? "Pause" : "Play"}
      </button>
      <div className={styles.trackWrap}>
        <div
          ref={track}
          className={styles.track}
          role="slider"
          tabIndex={0}
          aria-label="Experiment time"
          aria-valuemin={0}
          aria-valuemax={last}
          aria-valuenow={step}
          aria-valuetext={timelineValueText(step, steps)}
          onKeyDown={(event) => {
            const next = timelineStepFromKey(event.key, event.shiftKey, step, last);
            if (next !== null) { event.preventDefault(); onStep(next); }
          }}
          onPointerDown={(event) => { event.currentTarget.setPointerCapture(event.pointerId); fromPointer(event.clientX); }}
          onPointerMove={(event) => { if (event.currentTarget.hasPointerCapture(event.pointerId)) fromPointer(event.clientX); }}
        >
          <span className={styles.rail} aria-hidden="true" />
          <span className={styles.fill} aria-hidden="true" style={{ inlineSize: `${fraction * 100}%` }} />
          <span className={styles.thumb} aria-hidden="true" style={{ insetInlineStart: `${fraction * 100}%` }} />
        </div>
        <div className={styles.markers}>
          {markers.map((marker) => (
            <button key={marker.id} type="button" className={styles.marker} style={{ insetInlineStart: `${last === 0 ? 0 : (marker.step / last) * 100}%` }} aria-label={marker.label} title={marker.label} onClick={() => onMarker?.(marker)} />
          ))}
        </div>
      </div>
      <span className={styles.time} aria-live="off">{timeLabel}</span>
      <label className={styles.rate}>
        <span>Speed</span>
        <select value={rate} onChange={(event) => onRate(Number(event.currentTarget.value))}>
          {rates.map((r) => <option key={r} value={r}>{r}×</option>)}
        </select>
      </label>
    </div>
  );
}
