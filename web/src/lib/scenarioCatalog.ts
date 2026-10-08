/** Shared catalogue request. Empty is unavailable, never a valid canonical set. */
import { requestJson } from "./neuroflyClient";
import { parseScenarioCatalog } from "./scenarioPlayback";

export class EmptyScenarioCatalogueError extends Error {
  constructor() {
    super("No canonical scenarios are available through the configured API.");
    this.name = "EmptyScenarioCatalogueError";
  }
}

export function listScenarios() {
  return requestJson("/api/v1/scenarios", (value) => {
    if (Array.isArray(value) && value.length === 0) {
      throw new EmptyScenarioCatalogueError();
    }
    return parseScenarioCatalog(value);
  });
}
