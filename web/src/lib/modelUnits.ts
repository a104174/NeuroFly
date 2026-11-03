/**
 * Units a model-state readout may carry (Phase 0 decision 4): dimensionless values, model
 * time, angles in the model world, and model-equivalent units that end in "_eq" such as mV_eq.
 * A bare "mV", "Hz" and similar are biological units and are not allowed on model output.
 */
export type ModelUnit = "dimensionless" | "rad" | "ms" | "s" | `${string}_eq`;

export function isModelEquivalentUnit(unit: string): unit is `${string}_eq` {
  return unit.endsWith("_eq");
}
