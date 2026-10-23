import type { ReactNode } from "react";
import { SiteHeader, SiteFooter } from "../site/SiteChrome";

/** Shared presentation only. Data remains owned by the existing route loaders. */
export function DiscoveryShell({ active, children }: { active: "scenarios" | "experiments"; children?: ReactNode }) {
  return <div className="nf-site nf-discovery">
    <a className="nf-skip-link" href="#discovery-main">Skip to content</a>
    <SiteHeader activeHref={active === "scenarios" ? "/scenarios" : ""} />
    <main id="discovery-main" tabIndex={-1} className="nf-container">
      {children}
    </main>
    <SiteFooter />
  </div>;
}

export function DiscoveryState({ kind, title, children }: { kind: "error" | "empty" | "loading"; title: string; children?: ReactNode }) {
  return <section className={`discovery-state discovery-state--${kind}`} role={kind === "error" ? "alert" : kind === "loading" ? "status" : undefined} aria-busy={kind === "loading" || undefined}>
    <span className="discovery-state-mark" aria-hidden="true">{kind === "error" ? "!" : kind === "loading" ? "…" : "↗"}</span>
    <div><h2>{title}</h2>{children}</div>
  </section>;
}
