/** Detail tiers for 3D views (brief section 6): High, Medium, Low. */
export const VIEWPORT_TIERS = ["high", "medium", "low"] as const;
export type ViewportTier = (typeof VIEWPORT_TIERS)[number];

export const TIER_LABEL: Readonly<Record<ViewportTier, string>> = { high: "Full detail", medium: "Reduced detail", low: "Simplified shapes" };

/** The frame rate that triggers a drop, held for the window below. */
export const MIN_FPS = 30;
export const DROP_WINDOW_MS = 3000;

export function nextLowerTier(tier: ViewportTier): ViewportTier {
  return tier === "high" ? "medium" : "low";
}

/** Device pixel ratio cap: [1, 1.5] on phones, [1, 2] on desktop; Low tier renders at 1. */
export function dprRange(tier: ViewportTier, phone: boolean): [number, number] {
  if (tier === "low") return [1, 1];
  return phone ? [1, 1.5] : [1, 2];
}

/**
 * Feeds frame timestamps (ms). Returns true once the average frame rate has stayed under MIN_FPS
 * for DROP_WINDOW_MS. Resets after reporting, so each tier gets its own window.
 */
export function createFrameRateWatch(minFps = MIN_FPS, windowMs = DROP_WINDOW_MS) {
  let windowStart: number | null = null;
  let frames = 0;
  return function onFrame(now: number): boolean {
    if (windowStart === null) { windowStart = now; frames = 0; return false; }
    frames += 1;
    const elapsed = now - windowStart;
    if (elapsed < windowMs) return false;
    const fps = (frames * 1000) / elapsed;
    windowStart = now; frames = 0;
    return fps < minFps;
  };
}
