"use client";

import { useSyncExternalStore } from "react";
import { applyThemePreference, parseThemePreference, THEME_PREFERENCES, type ThemePreference } from "@/lib/theme";
import styles from "./ThemeSwitch.module.css";

const LABELS: Record<ThemePreference, string> = { system: "System", light: "Light", dark: "Dark" };

// The data-theme attribute on <html> is the single source of truth, so the control also works
// when storage is blocked. It is set before first paint by the script in src/lib/theme.ts.
function subscribe(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  return () => observer.disconnect();
}
const getSnapshot = () => parseThemePreference(document.documentElement.getAttribute("data-theme"));
const getServerSnapshot = (): ThemePreference => "system";

/** System follows the device; Light and Dark are remembered in this browser only. */
export function ThemeSwitch({ className }: { className?: string }) {
  const preference = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  const choose = (next: ThemePreference) => {
    let storage: Storage | undefined;
    try { storage = window.localStorage; } catch { storage = undefined; }
    applyThemePreference(next, document.documentElement, storage);
  };
  return (
    <div role="group" aria-label="Colour theme" className={`${styles.switch} ${className ?? ""}`}>
      {THEME_PREFERENCES.map((option) => (
        <button key={option} type="button" aria-pressed={preference === option} onClick={() => choose(option)}>
          {LABELS[option]}
        </button>
      ))}
    </div>
  );
}
