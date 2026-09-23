import type {
  BodyTelemetry,
  ExperimentTimeline,
} from "./neuroflyClient";

export const PLAYBACK_RATES = [0.25, 0.5, 1, 2, 4] as const;

export type PlaybackRate = (typeof PLAYBACK_RATES)[number];

export interface PlaybackClockState {
  currentTimeMs: number;
  isPlaying: boolean;
  playbackRate: PlaybackRate;
}

export interface TimelineSelection {
  playbackTimeMs: number;
  boundaryIndex: number;
  boundaryTimeMs: number;
  intervalIndex: number;
  intervalStartMs: number;
}

export interface SceneBodyState {
  bodyId: 10001 | 10010;
  membraneMv: number | null;
  synapticStateMveq: number | null;
  presentationLevel: number;
  spikedAtSelectedBoundary: boolean;
}

export interface ScenePresentationContext {
  thetaPeakRad: number;
  dnp01SynapticRanges: Readonly<
    Record<10001 | 10010, readonly [number, number] | null>
  >;
}

export interface ExperimentSceneState {
  playbackTimeMs: number;
  boundaryIndex: number;
  boundaryTimeMs: number;
  intervalIndex: number;
  intervalStartMs: number;
  thetaRad: number;
  angularExpansionVelocityRadS: number;
  lc4NormalizedFeature: number;
  lplc2NormalizedFeature: number;
  lc4DriveMveq: number;
  lplc2DriveMveq: number;
  lc4PresentationLevel: number;
  lplc2PresentationLevel: number;
  stimulusPresentationLevel: number;
  dnp01: Readonly<Record<10001 | 10010, SceneBodyState>>;
}

export class PlaybackDataError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PlaybackDataError";
  }
}

function finite(value: number, name: string): number {
  if (!Number.isFinite(value)) {
    throw new PlaybackDataError(`${name} must be finite.`);
  }
  return value;
}

export function clampPlaybackTime(
  requestedTimeMs: number,
  startMs: number,
  endMs: number,
): number {
  finite(requestedTimeMs, "requestedTimeMs");
  finite(startMs, "startMs");
  finite(endMs, "endMs");
  if (endMs < startMs) {
    throw new PlaybackDataError(
      "endMs must be greater than or equal to startMs.",
    );
  }
  return Math.min(endMs, Math.max(startMs, requestedTimeMs));
}

function floorIndex(values: readonly number[], value: number): number {
  if (values.length === 0) {
    throw new PlaybackDataError("A persisted time series cannot be empty.");
  }
  let low = 0;
  let high = values.length - 1;
  while (low < high) {
    const middle = Math.ceil((low + high) / 2);
    if (values[middle] <= value) {
      low = middle;
    } else {
      high = middle - 1;
    }
  }
  return low;
}

function decimalPlaces(value: number): number {
  const [coefficient, exponentText] = value.toString().toLowerCase().split("e");
  const exponent = exponentText === undefined ? 0 : Number(exponentText);
  const fractionalPart = coefficient.split(".")[1] ?? "";
  return Math.max(0, fractionalPart.length - exponent);
}

function scaledDecimalInteger(value: number, decimalScale: number): number | null {
  const [coefficient, exponentText] = value.toString().toLowerCase().split("e");
  const exponent = exponentText === undefined ? 0 : Number(exponentText);
  const negative = coefficient.startsWith("-");
  const unsigned = negative ? coefficient.slice(1) : coefficient;
  const [integerPart, fractionalPart = ""] = unsigned.split(".");
  const digits = `${integerPart}${fractionalPart}` || "0";
  const additionalZeros = decimalScale - (fractionalPart.length - exponent);
  if (additionalZeros < 0) return null;
  const scaled = Number(`${negative ? "-" : ""}${digits}${"0".repeat(additionalZeros)}`);
  return Number.isSafeInteger(scaled) ? scaled : null;
}

function exactGridStepIndex(
  timeMs: number,
  startMs: number,
  dtMs: number,
): number | null {
  // The range control emits decimal grid values (for example 45.3), while
  // persisted times can serialize the same step as an adjacent float
  // (45.300000000000004). Match exact decimal grid identity without epsilon;
  // non-grid playback times continue through the persisted floor lookup.
  const decimalScale = Math.max(
    decimalPlaces(timeMs),
    decimalPlaces(startMs),
    decimalPlaces(dtMs),
  );
  const timeUnits = scaledDecimalInteger(timeMs, decimalScale);
  const startUnits = scaledDecimalInteger(startMs, decimalScale);
  const dtUnits = scaledDecimalInteger(dtMs, decimalScale);
  if (timeUnits === null || startUnits === null || dtUnits === null || dtUnits <= 0) {
    return null;
  }
  const offsetUnits = timeUnits - startUnits;
  if (!Number.isSafeInteger(offsetUnits) || offsetUnits % dtUnits !== 0) {
    return null;
  }
  return offsetUnits / dtUnits;
}

export function selectTimelineSample(
  timeline: ExperimentTimeline,
  requestedTimeMs: number,
): TimelineSelection {
  if (timeline.times_ms.length !== timeline.step_times_ms.length + 1) {
    throw new PlaybackDataError(
      "Timeline boundary and interval counts are inconsistent.",
    );
  }
  if (timeline.step_times_ms.length === 0) {
    throw new PlaybackDataError(
      "Timeline must contain at least one persisted interval.",
    );
  }
  if (!Number.isFinite(timeline.dt_ms) || timeline.dt_ms <= 0) {
    throw new PlaybackDataError("Timeline dt_ms must be positive and finite.");
  }
  const playbackTimeMs = clampPlaybackTime(
    requestedTimeMs,
    timeline.start_ms,
    timeline.end_ms,
  );
  const gridStepIndex = exactGridStepIndex(
    playbackTimeMs,
    timeline.start_ms,
    timeline.dt_ms,
  );
  const isStoredGridStep = gridStepIndex !== null &&
    gridStepIndex >= 0 && gridStepIndex < timeline.times_ms.length;
  const boundaryIndex = isStoredGridStep
    ? gridStepIndex
    : floorIndex(timeline.times_ms, playbackTimeMs);
  const intervalIndex = isStoredGridStep
    ? Math.min(gridStepIndex, timeline.step_times_ms.length - 1)
    : Math.min(
      floorIndex(timeline.step_times_ms, playbackTimeMs),
      timeline.step_times_ms.length - 1,
    );
  return {
    playbackTimeMs,
    boundaryIndex,
    boundaryTimeMs: timeline.times_ms[boundaryIndex],
    intervalIndex,
    intervalStartMs: timeline.step_times_ms[intervalIndex],
  };
}

export function createPlaybackClock(
  startMs: number,
  playbackRate: PlaybackRate = 1,
): PlaybackClockState {
  return {
    currentTimeMs: finite(startMs, "startMs"),
    isPlaying: false,
    playbackRate,
  };
}

export function playPlayback(
  state: PlaybackClockState,
  endMs: number,
): PlaybackClockState {
  return state.currentTimeMs >= endMs
    ? { ...state, isPlaying: false }
    : { ...state, isPlaying: true };
}

export function pausePlayback(state: PlaybackClockState): PlaybackClockState {
  return state.isPlaying ? { ...state, isPlaying: false } : state;
}

export function resetPlayback(
  state: PlaybackClockState,
  startMs: number,
): PlaybackClockState {
  return {
    ...state,
    currentTimeMs: finite(startMs, "startMs"),
    isPlaying: false,
  };
}

export function seekPlayback(
  state: PlaybackClockState,
  requestedTimeMs: number,
  startMs: number,
  endMs: number,
): PlaybackClockState {
  const currentTimeMs = clampPlaybackTime(requestedTimeMs, startMs, endMs);
  return {
    ...state,
    currentTimeMs,
    isPlaying: currentTimeMs === endMs ? false : state.isPlaying,
  };
}

export function setPlaybackRate(
  state: PlaybackClockState,
  playbackRate: PlaybackRate,
): PlaybackClockState {
  if (!PLAYBACK_RATES.includes(playbackRate)) {
    throw new PlaybackDataError(
      "playbackRate is not an allowed presentation rate.",
    );
  }
  return { ...state, playbackRate };
}

export function advancePlayback(
  state: PlaybackClockState,
  elapsedWallTimeMs: number,
  startMs: number,
  endMs: number,
): PlaybackClockState {
  finite(elapsedWallTimeMs, "elapsedWallTimeMs");
  if (elapsedWallTimeMs < 0) {
    throw new PlaybackDataError("elapsedWallTimeMs cannot be negative.");
  }
  if (!state.isPlaying || elapsedWallTimeMs === 0) {
    return state;
  }
  const currentTimeMs = clampPlaybackTime(
    state.currentTimeMs + elapsedWallTimeMs * state.playbackRate,
    startMs,
    endMs,
  );
  return {
    ...state,
    currentTimeMs,
    isPlaying: currentTimeMs < endMs,
  };
}

function bodyById(
  timeline: ExperimentTimeline,
  bodyId: 10001 | 10010,
): BodyTelemetry | undefined {
  return timeline.selected_body_telemetry.find((body) => body.body_id === bodyId);
}

function range(values: readonly number[]): readonly [number, number] | null {
  if (values.length === 0) return null;
  let minimum = values[0];
  let maximum = values[0];
  for (let index = 1; index < values.length; index += 1) {
    minimum = Math.min(minimum, values[index]);
    maximum = Math.max(maximum, values[index]);
  }
  return [minimum, maximum];
}

function presentationLevel(
  value: number | null,
  valueRange: readonly [number, number] | null,
): number {
  if (value === null || valueRange === null) return 0;
  const [minimum, maximum] = valueRange;
  if (maximum === minimum) return 0;
  return Math.min(1, Math.max(0, (value - minimum) / (maximum - minimum)));
}

export function createScenePresentationContext(
  timeline: ExperimentTimeline,
): ScenePresentationContext {
  let thetaPeakRad = 0;
  for (const theta of timeline.theta_rad) {
    thetaPeakRad = Math.max(thetaPeakRad, Math.abs(theta));
  }
  return {
    thetaPeakRad,
    dnp01SynapticRanges: {
      10001: range(bodyById(timeline, 10001)?.synaptic_state_mveq ?? []),
      10010: range(bodyById(timeline, 10010)?.synaptic_state_mveq ?? []),
    },
  };
}

function deriveBodyState(
  timeline: ExperimentTimeline,
  bodyId: 10001 | 10010,
  boundaryIndex: number,
  context: ScenePresentationContext,
): SceneBodyState {
  const body = bodyById(timeline, bodyId);
  const membraneMv = body?.membrane_mv[boundaryIndex] ?? null;
  const synapticStateMveq = body?.synaptic_state_mveq[boundaryIndex] ?? null;
  return {
    bodyId,
    membraneMv,
    synapticStateMveq,
    presentationLevel: presentationLevel(
      synapticStateMveq,
      context.dnp01SynapticRanges[bodyId],
    ),
    spikedAtSelectedBoundary: body?.spike_times_ms.some(
      (timeMs) => timeline.times_ms.indexOf(timeMs) === boundaryIndex,
    ) ?? false,
  };
}

function boundedPresentationLevel(value: number): number {
  return Math.min(1, Math.max(0, value));
}

export function deriveSceneState(
  timeline: ExperimentTimeline,
  requestedTimeMs: number,
  context: ScenePresentationContext = createScenePresentationContext(timeline),
): ExperimentSceneState {
  const selection = selectTimelineSample(timeline, requestedTimeMs);
  const interval = selection.intervalIndex;
  const lc4NormalizedFeature = timeline.lc4_normalized_feature[interval];
  const lplc2NormalizedFeature = timeline.lplc2_normalized_feature[interval];
  const thetaRad = timeline.theta_rad[interval];
  const stimulusPresentationLevel =
    context.thetaPeakRad === 0
      ? 0
      : boundedPresentationLevel(Math.abs(thetaRad) / context.thetaPeakRad);
  return {
    playbackTimeMs: selection.playbackTimeMs,
    boundaryIndex: selection.boundaryIndex,
    boundaryTimeMs: selection.boundaryTimeMs,
    intervalIndex: interval,
    intervalStartMs: selection.intervalStartMs,
    thetaRad,
    angularExpansionVelocityRadS:
      timeline.angular_expansion_velocity_rad_s[interval],
    lc4NormalizedFeature,
    lplc2NormalizedFeature,
    lc4DriveMveq: timeline.lc4_drive_mveq[interval],
    lplc2DriveMveq: timeline.lplc2_drive_mveq[interval],
    lc4PresentationLevel: boundedPresentationLevel(lc4NormalizedFeature),
    lplc2PresentationLevel: boundedPresentationLevel(lplc2NormalizedFeature),
    stimulusPresentationLevel,
    dnp01: {
      10001: deriveBodyState(
        timeline,
        10001,
        selection.boundaryIndex,
        context,
      ),
      10010: deriveBodyState(
        timeline,
        10010,
        selection.boundaryIndex,
        context,
      ),
    },
  };
}
