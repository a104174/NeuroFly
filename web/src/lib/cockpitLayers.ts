import type { CockpitFrame } from "@/lib/cockpitModel";
import type { ModelUnit } from "@/lib/modelUnits";

/** Cockpit layers (brief section 5): Overview for everyone, Detail for researchers, Raw for experts. */
export const COCKPIT_LAYERS = ["overview", "detail", "raw"] as const;
export type CockpitLayer = (typeof COCKPIT_LAYERS)[number];

export function parseLayer(value: string | string[] | undefined): CockpitLayer | null {
  const text = Array.isArray(value) ? value[0] : value;
  return COCKPIT_LAYERS.find((layer) => layer === text) ?? null;
}

/** Keys 1, 2, 3 change layer. */
export function layerFromKey(key: string): CockpitLayer | null {
  return key === "1" ? "overview" : key === "2" ? "detail" : key === "3" ? "raw" : null;
}

/** Width classes of brief section 5: wide (1920+), standard (1024 to 1919), tablet (600 to 1023), phone (below 600). */
export type CockpitWidth = "wide" | "standard" | "tablet" | "phone";
export function widthClass(px: number): CockpitWidth {
  return px >= 1920 ? "wide" : px >= 1024 ? "standard" : px >= 600 ? "tablet" : "phone";
}

/** At 1920 px and up the Detail panel is always open; otherwise the reader chooses when to add density. */
export function effectiveLayer(chosen: CockpitLayer | null, width: CockpitWidth): CockpitLayer {
  if (width === "phone") return "overview";
  return chosen ?? (width === "wide" ? "detail" : "overview");
}

export interface OverviewReadout {
  readonly id: string;
  readonly label: string;
  readonly value: number;
  readonly digits: number;
  readonly unit: ModelUnit;
}

/** Overview shows at most six readouts, and the phone shows the first three. All are model state. */
export const OVERVIEW_MAX = 6;
export const PHONE_MAX = 3;

export function overviewReadouts(frame: CockpitFrame, stepCount: number): OverviewReadout[] {
  const all: OverviewReadout[] = [
    { id: "time", label: "Experiment time", value: frame.playbackTimeMs, digits: 2, unit: "ms" },
    { id: "step", label: `Step of ${stepCount}`, value: frame.boundaryIndex + 1, digits: 0, unit: "dimensionless" },
    { id: "theta", label: "Angular size θ", value: frame.thetaRad, digits: 4, unit: "rad" },
    { id: "lc4", label: "LC4 drive", value: frame.lc4DriveMveq, digits: 4, unit: "mV_eq" },
    { id: "lplc2", label: "LPLC2 drive", value: frame.lplc2DriveMveq, digits: 4, unit: "mV_eq" },
  ];
  return all.slice(0, OVERVIEW_MAX);
}
