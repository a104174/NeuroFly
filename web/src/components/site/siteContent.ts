/** Public website destinations. Scientific routes and runtime remain independent. */
export const LAB_HREF = "/visual-lab/arena";
export const SCIENCE_PAGE_HREF = "/science";
/** Becomes /science/status when that page exists (phase 4). */
export const STATUS_HREF = "/science#limits";
export const EXPERIMENTS_HREF = "/experiments";
export const REPOSITORY_HREF = "https://github.com/a104174/NeuroFly";
export const SCIENCE_HREF = "https://github.com/a104174/NeuroFly/tree/main/docs/science";
export const MALECNS_HREF = "https://male-cns.janelia.org/download/";

/**
 * Primary navigation (Phase 0 decisions). Home is the logo. Experiments leaves the main
 * navigation until a real scientific experiment exists; it stays reachable from the footer,
 * Scenarios and Science. `match` is the path prefix that marks the item as current.
 */
export const SITE_LINKS = [
  { label: "Scenarios", href: "/scenarios", match: "/scenarios" },
  { label: "Neurons", href: "/morphology", match: "/morphology" },
  { label: "Lab", href: LAB_HREF, match: "/visual-lab" },
  { label: "Science", href: SCIENCE_PAGE_HREF, match: "/science" },
] as const;

/** Label fixed by the owner for the one recorded run, which is an engineering smoke test. */
export const EXPERIMENTS_LABEL = "Engineering test, not a scientific experiment";

export function isCurrent(match: string, pathname: string | null | undefined): boolean {
  if (!pathname) return false;
  return pathname === match || pathname.startsWith(`${match}/`);
}
