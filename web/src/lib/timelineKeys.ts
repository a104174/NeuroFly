/** Keyboard model of the Timeline slider: arrows step 1, Shift+arrows step 10, Home and End jump. */
export function timelineStepFromKey(key: string, shift: boolean, current: number, last: number): number | null {
  const big = shift ? 10 : 1;
  const next = key === "ArrowRight" || key === "ArrowUp" ? current + big
    : key === "ArrowLeft" || key === "ArrowDown" ? current - big
    : key === "Home" ? 0
    : key === "End" ? last
    : null;
  return next === null ? null : Math.max(0, Math.min(last, next));
}

export function timelineValueText(step: number, total: number): string {
  return `Step ${step + 1} of ${total}`;
}
