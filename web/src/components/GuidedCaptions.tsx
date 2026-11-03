"use client";

import { useState, useSyncExternalStore } from "react";
import styles from "./GuidedCaptions.module.css";

export interface Caption { readonly title: string; readonly text: string; readonly step: number }

const KEY = "neurofly-guide-dismissed";
const EVENT = "neurofly-guide-change";

function subscribe(listener: () => void) {
  window.addEventListener(EVENT, listener);
  window.addEventListener("storage", listener);
  return () => { window.removeEventListener(EVENT, listener); window.removeEventListener("storage", listener); };
}
/** Whether this viewer skipped the guide before. Stored only in this browser; failures read as "not skipped". */
function dismissedNow(): boolean {
  try { return localStorage.getItem(KEY) === "1"; } catch { return false; }
}
function setDismissed(value: boolean) {
  try { if (value) localStorage.setItem(KEY, "1"); else localStorage.removeItem(KEY); } catch { /* blocked storage: lasts until reload */ }
  window.dispatchEvent(new Event(EVENT));
}

/**
 * First-visit guide: three captions tied to moments of the stored run. Skippable and restartable.
 * Captions describe what the model recorded, never what a fly does.
 */
export function GuidedCaptions({ captions, onGoTo }: { captions: readonly Caption[]; onGoTo: (step: number) => void }) {
  const dismissed = useSyncExternalStore(subscribe, dismissedNow, () => false);
  const [index, setIndex] = useState(0);
  const [local, setLocal] = useState(false);
  const hidden = dismissed || local;
  if (hidden) {
    return (
      <div className={styles.restart}>
        <button type="button" onClick={() => { setLocal(false); setIndex(0); setDismissed(false); onGoTo(captions[0].step); }}>Restart the guide</button>
      </div>
    );
  }
  const caption = captions[index];
  const last = index === captions.length - 1;
  return (
    <section className={styles.guide} aria-label="Guided tour">
      <p className={styles.step}>Guide, step {index + 1} of {captions.length}</p>
      <h2>{caption.title}</h2>
      <p>{caption.text}</p>
      <div className={styles.actions}>
        <button type="button" onClick={() => onGoTo(caption.step)}>Show this moment</button>
        {last ? (
          <button type="button" onClick={() => { setLocal(true); setDismissed(true); }}>Finish</button>
        ) : (
          <button type="button" onClick={() => { const n = index + 1; setIndex(n); onGoTo(captions[n].step); }}>Next</button>
        )}
        {index > 0 ? <button type="button" onClick={() => { const n = index - 1; setIndex(n); onGoTo(captions[n].step); }}>Back</button> : null}
        <button type="button" className={styles.skip} onClick={() => { setLocal(true); setDismissed(true); }}>Skip the guide</button>
      </div>
    </section>
  );
}
