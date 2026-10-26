/** Presentation of the persisted experiment_config_id; no result reclassification. */
export function recordedRunPurpose(experimentConfigId: string): string | null {
  return experimentConfigId === "ui_smoke_phase2f_reference_v1"
    ? "Engineering / UI smoke reference. Empirical validation has not been evaluated."
    : null;
}
