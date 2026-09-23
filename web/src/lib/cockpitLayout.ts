export type CockpitFocusPanel = "world" | "connectome" | "telemetry";

export type CockpitFocusState = CockpitFocusPanel | null;

export function toggleCockpitFocus(
  current: CockpitFocusState,
  panel: CockpitFocusPanel,
): CockpitFocusState {
  return current === panel ? null : panel;
}
