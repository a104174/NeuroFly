import Link from "next/link";
import type { ReactNode } from "react";

export function Arrow() {
  return <svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

export function ActionLink({ href, children, variant = "primary" }: { href: string; children: ReactNode; variant?: "primary" | "quiet" }) {
  return <Link prefetch={false} className={`nf-button nf-button--${variant}`} href={href}>{children}<Arrow /></Link>;
}
