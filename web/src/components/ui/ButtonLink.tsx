import Link from "next/link";
import type { ReactNode } from "react";
import styles from "./ButtonLink.module.css";

/** A link that looks like a button. Real navigation, so it works without JavaScript. */
export function ButtonLink({ href, children, variant = "primary", ariaLabel }: { href: string; children: ReactNode; variant?: "primary" | "quiet"; ariaLabel?: string }) {
  return <Link prefetch={false} href={href} className={styles.button} data-variant={variant} aria-label={ariaLabel}>{children}</Link>;
}
