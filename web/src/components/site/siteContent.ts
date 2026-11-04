/** Public website destinations. Scientific routes and runtime remain independent. */
export const LAB_HREF = "/visual-lab";
export const SCIENCE_PAGE_HREF = "/science";
/** The page that gives the reason for every capability. */
export const STATUS_HREF = "/science/status";
export const EXPERIMENTS_HREF = "/experiments";
export const REPOSITORY_HREF = "https://github.com/a104174/NeuroFly";
export const SCIENCE_HREF = "https://github.com/a104174/NeuroFly/tree/main/docs/science";
/** The author credit shown in the footer and on the Science page. */
export const AUTHOR_NAME = "Hélder Cruz";
export const AUTHOR_HREF = "https://heldercruz.dev/pt";
export const MALECNS_HREF = "https://male-cns.janelia.org/download/";
/** Official release page; it states "The Male CNS dataset is licensed under CC-BY." */
export const MALECNS_RELEASE_HREF = "https://male-cns.janelia.org/release/";
export const CC_BY_HREF = "https://creativecommons.org/licenses/by/4.0/";
export const DATA_CREDIT_HREF = "/science#data-credit";
/**
 * The MaleCNS paper, as given by the DOI registry (Crossref) and the bioRxiv page: title, first author and
 * DOI. The full author list differs slightly between the two sources, so it is left to the DOI link.
 */
export const MALECNS_PAPER = {
  title: "Sexual dimorphism in the complete connectome of the Drosophila male central nervous system",
  authors: "Berg S et al.",
  venue: "bioRxiv",
  year: 2025,
  doi: "10.1101/2025.10.09.680999",
  href: "https://doi.org/10.1101/2025.10.09.680999",
} as const;

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
