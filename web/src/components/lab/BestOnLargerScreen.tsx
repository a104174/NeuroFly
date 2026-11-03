"use client";

import Link from "next/link";
import { useSyncExternalStore, type ReactNode } from "react";

const QUERY = "(max-width: 599px)";
function subscribe(listener: () => void) {
  const m = window.matchMedia(QUERY);
  m.addEventListener("change", listener);
  return () => m.removeEventListener("change", listener);
}

/** Below 600 px the research tools show a short note instead of the instrument (brief section 5, Lab). */
export function BestOnLargerScreen({ children }: { children: ReactNode }) {
  const small = useSyncExternalStore(subscribe, () => window.matchMedia(QUERY).matches, () => false);
  if (!small) return <>{children}</>;
  return (
    <section role="note" style={{ margin: "var(--space-5) var(--gutter)", padding: "var(--space-5)", border: "1px solid var(--color-hairline)", borderRadius: "var(--radius-lg)", background: "var(--color-surface)", color: "var(--color-ink)" }}>
      <h2 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-h3-size)" }}>Best on a larger screen</h2>
      <p style={{ margin: "0 0 var(--space-3)", color: "var(--color-ink-2)" }}>The research tools need more room for their controls and plots.</p>
      <p style={{ margin: 0 }}>
        <Link href="/visual-lab/arena" style={{ color: "var(--color-accent)", textDecoration: "underline", textUnderlineOffset: 3, display: "inline-block", minBlockSize: 24 }}>Try Explore instead</Link>
        {" or "}
        <Link href="/scenarios" style={{ color: "var(--color-accent)", textDecoration: "underline", textUnderlineOffset: 3, display: "inline-block", minBlockSize: 24 }}>watch a scenario</Link>.
      </p>
    </section>
  );
}
