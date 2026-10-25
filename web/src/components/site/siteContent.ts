/** Public website destinations. Scientific routes and runtime remain independent. */
export const LAB_HREF = "/visual-lab/arena";
export const SCIENCE_PAGE_HREF = "/science";
export const SCIENCE_HREF = "https://github.com/a104174/NeuroFly/tree/main/docs/science";
export const SITE_LINKS = [
  { label: "Home", href: "/" },
  { label: "Lab", href: LAB_HREF },
  { label: "Experiments", href: "/scenarios" },
  { label: "Science", href: SCIENCE_PAGE_HREF },
] as const;
