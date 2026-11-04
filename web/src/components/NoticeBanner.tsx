"use client";

import { useSyncExternalStore } from "react";
import styles from "./NoticeBanner.module.css";

const KEY = "neurofly-notice-experiments";
function subscribe(onChange: () => void) {
  window.addEventListener("storage", onChange);
  window.addEventListener("neurofly-notice", onChange);
  return () => { window.removeEventListener("storage", onChange); window.removeEventListener("neurofly-notice", onChange); };
}
const read = () => { try { return window.localStorage.getItem(KEY) === "dismissed"; } catch { return false; } };
const serverSnapshot = () => false;

/**
 * A one-line note that can be dismissed and brought back. The choice is a convenience kept in this
 * browser only; if storage is blocked the note simply shows.
 */
export function NoticeBanner({ children, restoreLabel }: { children: React.ReactNode; restoreLabel: string }) {
  const dismissed = useSyncExternalStore(subscribe, read, serverSnapshot);
  const set = (value: boolean) => {
    try { if (value) window.localStorage.setItem(KEY, "dismissed"); else window.localStorage.removeItem(KEY); } catch { /* blocked: the note stays as it is */ }
    window.dispatchEvent(new Event("neurofly-notice"));
  };
  return dismissed ? (
    <button type="button" className={styles.restore} onClick={() => set(false)}>{restoreLabel}</button>
  ) : (
    <div className={styles.banner} role="note">
      <p>{children}</p>
      <button type="button" onClick={() => set(true)} aria-label="Dismiss this note">Dismiss</button>
    </div>
  );
}
