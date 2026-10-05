"use server";

import { requestJson } from "@/lib/neuroflyClient";
import { parseScenarioPlayback, SCENARIO_KINDS, type ScenarioKind, type ScenarioPlayback } from "@/lib/scenarioPlayback";

export async function loadScenarioPlayback(id: ScenarioKind): Promise<{ result: ScenarioPlayback } | { error: string }> {
  if (!SCENARIO_KINDS.includes(id)) return { error: "Unsupported scenario." };
  try {
    const result = await requestJson(`/api/v1/scenarios/${id}/playback`, parseScenarioPlayback);
    if (result.scenario.id !== id) throw new Error("Backend returned the wrong scenario.");
    return { result };
  } catch (error) {
    return { error: error instanceof Error ? error.message : "Scenario replay is unavailable." };
  }
}
