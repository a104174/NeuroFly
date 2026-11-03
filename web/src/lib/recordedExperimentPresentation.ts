/** Presentation of the persisted experiment_config_id; no result reclassification. */
export function recordedRunPurpose(experimentConfigId: string): string | null {
  return experimentConfigId === "ui_smoke_phase2f_reference_v1"
    ? "Engineering / UI smoke reference. No comparison with real fly data has been made."
    : null;
}

/** Readable name for a run from its candidate identifier, for example "Looming giant fiber v1". */
export function experimentName(identifier: string): string {
  const words = identifier.replace(/_v\d+$/, "").replaceAll("_", " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** The one recorded run is an engineering smoke reference, not a scientific experiment. */
export function isEngineeringTest(experimentConfigId: string): boolean {
  return experimentConfigId === "ui_smoke_phase2f_reference_v1";
}
