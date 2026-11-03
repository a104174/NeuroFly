/**
 * Theme preference. Stored only in this browser. "system" removes the
 * attribute so tokens.css follows prefers-color-scheme, and dark when the
 * browser gives no signal (Phase 0 decisions, question 4).
 */
export const THEME_STORAGE_KEY = "neurofly-theme";
export const THEME_PREFERENCES = ["system", "light", "dark"] as const;
export type ThemePreference = (typeof THEME_PREFERENCES)[number];

export function parseThemePreference(value: unknown): ThemePreference {
  return value === "light" || value === "dark" ? value : "system";
}

/** Apply a preference to the document. Safe to call with storage unavailable. */
export function applyThemePreference(
  preference: ThemePreference,
  root: { setAttribute(name: string, value: string): void; removeAttribute(name: string): void },
  storage?: Pick<Storage, "setItem" | "removeItem">,
): void {
  if (preference === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", preference);
  try {
    if (preference === "system") storage?.removeItem(THEME_STORAGE_KEY);
    else storage?.setItem(THEME_STORAGE_KEY, preference);
  } catch {
    // Storage can be blocked. The choice then lasts until the page is closed.
  }
}

/**
 * Runs in <head>, before first paint, so the stored choice never flashes the
 * wrong theme. It must stay self-contained: it is serialised into the page.
 */
export const THEME_INIT_SCRIPT = `(function(){try{var t=localStorage.getItem(${JSON.stringify(THEME_STORAGE_KEY)});if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}catch(e){}})();`;
