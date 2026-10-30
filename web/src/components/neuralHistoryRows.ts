import { activityHistory } from '@/lib/neuralExplorerPresentation';
import type { LiveSample } from '@/lib/liveGroundSession';

/** Retain unavailable intervals while reusing the chart's validated samples. */
export function activityHistoryRows(samples: readonly LiveSample[], bodyId: number) {
  return samples.map((sample) => {
    const [point] = activityHistory([sample], bodyId);
    if (point && Number.isSafeInteger(point.tick) && Number.isFinite(point.time)) return point;
    return { tick: Number.isSafeInteger(sample.interval?.step) ? sample.interval.step : null, time: Number.isFinite(sample.interval?.time) ? sample.interval.time : null, value: null };
  });
}
