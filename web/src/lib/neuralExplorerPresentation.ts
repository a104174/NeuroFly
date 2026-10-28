import { neuralActivityTrace } from './neuralActivityTrace';
import type { LiveSample } from './liveGroundSession';

/** Actual left-boundary samples only. Invalid intervals remain gaps. */
export function activityHistory(samples: readonly LiveSample[], bodyId: number) {
  return samples.flatMap((sample) => {
    try {
      const trace = neuralActivityTrace(sample);
      const state = trace.states.find((entry) => entry.id === bodyId);
      return state ? [{ tick: trace.tick, time: trace.time_s, value: state.value }] : [];
    } catch { return []; }
  });
}

export function activitySign(value: number | null): string {
  if (value === null || !Number.isFinite(value)) return 'unavailable';
  return value > 0 ? 'positive' : value < 0 ? 'negative' : 'zero';
}
