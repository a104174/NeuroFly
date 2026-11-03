/**
 * Filtering, sorting and URL building for the Scenarios and Experiments lists. The state lives
 * in the URL (?stimulus=, ?q=, ?sort=, ?dir=), so a filtered view can be shared and reloaded.
 * Pure functions, so they are tested without a browser.
 */
import { discoveryCopy, experimentMetadata } from "./scenarioPresentation";
import { experimentName } from "./recordedExperimentPresentation";
import type { ScenarioKind } from "./scenarioPlayback";
import type { ExperimentSummary } from "./neuroflyClient";

export type StimulusKey = "none" | "looming" | "horizontal-motion" | "orientation";
export const STIMULUS_FILTERS: ReadonlyArray<{ key: StimulusKey; label: string }> = [
  { key: "none", label: "No stimulus" },
  { key: "looming", label: "Looming" },
  { key: "horizontal-motion", label: "Horizontal motion" },
  { key: "orientation", label: "Orientation" },
];
/** The stimulus type of each canonical scenario, from its recorded input. */
export const STIMULUS_OF: Readonly<Record<ScenarioKind, StimulusKey>> = {
  BASELINE_CONTROL: "none",
  LOOMING_CIRCUIT_VALIDATION: "looming",
  LOOMING_WORLD_EXPERIMENT: "looming",
  HORIZONTAL_MOTION_NEURAL_VALIDATION: "horizontal-motion",
  EXPLORATORY_COURSE_CONTROL: "orientation",
};

/** Anything unknown means "all", so a stale or edited URL still shows the full list. */
export function parseStimulus(value: string | string[] | undefined): StimulusKey | null {
  const v = Array.isArray(value) ? value[0] : value;
  return STIMULUS_FILTERS.some((f) => f.key === v) ? (v as StimulusKey) : null;
}
export function filterScenarios<T extends { id: ScenarioKind }>(scenarios: readonly T[], stimulus: StimulusKey | null): T[] {
  return scenarios.filter((s) => stimulus === null || STIMULUS_OF[s.id] === stimulus);
}
export function scenariosHref(stimulus: StimulusKey | null): string {
  return stimulus ? `/scenarios?stimulus=${stimulus}` : "/scenarios";
}
/** Sanity check used by tests: every canonical scenario has a card title and a stimulus. */
export function scenarioIsPresentable(id: ScenarioKind): boolean {
  return Boolean(discoveryCopy[id] && experimentMetadata[id] && STIMULUS_OF[id]);
}

export type ExperimentSortKey = "name" | "model";
export type Direction = "asc" | "desc";
export interface ExperimentQuery { q: string; sort: ExperimentSortKey; dir: Direction }
export const DEFAULT_EXPERIMENT_QUERY: ExperimentQuery = { q: "", sort: "name", dir: "asc" };

const first = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
export function parseExperimentQuery(params: Record<string, string | string[] | undefined>): ExperimentQuery {
  const sort = first(params.sort), dir = first(params.dir);
  return {
    q: (first(params.q) ?? "").trim().slice(0, 100),
    sort: sort === "model" ? "model" : "name",
    dir: dir === "desc" ? "desc" : "asc",
  };
}
export function experimentsHref(query: Partial<ExperimentQuery>): string {
  const merged = { ...DEFAULT_EXPERIMENT_QUERY, ...query };
  const search = new URLSearchParams();
  if (merged.q) search.set("q", merged.q);
  if (merged.sort !== DEFAULT_EXPERIMENT_QUERY.sort) search.set("sort", merged.sort);
  if (merged.dir !== DEFAULT_EXPERIMENT_QUERY.dir) search.set("dir", merged.dir);
  const text = search.toString();
  return text ? `/experiments?${text}` : "/experiments";
}
export function modelVersion(experiment: ExperimentSummary): string {
  return `${experiment.neural_model.id} · ${experiment.neural_model.version}`;
}
/** Matches the name, the artifact id, the config id or the model, ignoring case. */
export function searchExperiments(experiments: readonly ExperimentSummary[], q: string): ExperimentSummary[] {
  const needle = q.trim().toLowerCase();
  if (!needle) return [...experiments];
  return experiments.filter((e) => [experimentName(e.candidate.identifier), e.candidate.identifier, e.artifact_id, e.experiment_config_id, modelVersion(e)].some((field) => field.toLowerCase().includes(needle)));
}
export function sortExperiments(experiments: readonly ExperimentSummary[], sort: ExperimentSortKey, dir: Direction): ExperimentSummary[] {
  const key = (e: ExperimentSummary) => (sort === "model" ? modelVersion(e) : experimentName(e.candidate.identifier));
  const sign = dir === "desc" ? -1 : 1;
  // Stable: ties keep the API order, which is the artifact order.
  return experiments.map((e, index) => ({ e, index })).sort((a, b) => sign * key(a.e).localeCompare(key(b.e), "en", { numeric: true }) || a.index - b.index).map(({ e }) => e);
}
