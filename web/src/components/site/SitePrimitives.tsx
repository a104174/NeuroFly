import Link from "next/link";
import type { ReactNode } from "react";

export function Arrow() {
  return <svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

export function ActionLink({ href, children, variant = "primary" }: { href: string; children: ReactNode; variant?: "primary" | "quiet" }) {
  return <Link prefetch={false} className={`nf-button nf-button--${variant}`} href={href}>{children}<Arrow /></Link>;
}

export function SectionHeading({ label, id, children }: { label: string; id: string; children: ReactNode }) {
  return <div className="nf-section-heading"><p className="nf-eyebrow">{label}</p><h2 id={id}>{children}</h2></div>;
}

export function FeatureIcon({ kind }: { kind: "space" | "circuit" | "replay" | "movement" }) {
  return <svg className="nf-feature-icon" viewBox="0 0 40 40" width="40" height="40" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {kind === "space" ? <><path d="m20 4 14 8v16l-14 8-14-8V12l14-8Z" /><path d="m6 12 14 8 14-8M20 20v16M13 8l14 8v16" /></> : kind === "circuit" ? <><path d="m10 11 19 6M10 11l5 20m14-14L15 31m14-14 4 15" /><circle cx="10" cy="11" r="4" /><circle cx="29" cy="17" r="4" /><circle cx="15" cy="31" r="3" /><circle cx="33" cy="32" r="2" /></> : kind === "replay" ? <><path d="M8 13a14 14 0 1 1-1 13M8 6v8h8" /><path d="m17 14 10 6-10 6V14Z" /></> : <><path d="M5 31c8 0 5-20 15-20s5 18 15 7M29 15l6 3-3 6" /><circle cx="6" cy="31" r="2" /></>}
  </svg>;
}
