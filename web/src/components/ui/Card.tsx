import Link from "next/link";
import type { ReactNode } from "react";
import styles from "./Card.module.css";

export interface CardProps {
  /** Small label above the title, for example the kind of scenario. */
  eyebrow?: string;
  title: string;
  /** With an href, the title is the card's single link, stretched over the whole card. */
  href?: string;
  titleLevel?: 2 | 3;
  /** 16:9 poster area. Omit when there is no poster; never fake one. */
  poster?: ReactNode;
  variant?: "default" | "interactive" | "unavailable";
  /** Rows of label and value, for example stimulus and duration. */
  meta?: readonly { label: string; value: ReactNode }[];
  children?: ReactNode;
  className?: string;
}

/**
 * The shared card (brief section 6): 16 px radius, hairline border, one link per card.
 * Hover darkens the border; nothing lifts.
 */
export function Card({ eyebrow, title, href, titleLevel = 3, poster, variant, meta, children, className }: CardProps) {
  const Heading = `h${titleLevel}` as "h2" | "h3";
  const kind = variant ?? (href ? "interactive" : "default");
  return (
    <article className={`${styles.card} ${className ?? ""}`} data-variant={kind}>
      {poster ? <div className={styles.poster}>{poster}</div> : null}
      <div className={styles.body}>
        {eyebrow ? <p className={styles.eyebrow}>{eyebrow}</p> : null}
        <Heading className={styles.title}>
          {href ? <Link prefetch={false} href={href} className={styles.link}>{title}</Link> : title}
        </Heading>
        {children ? <div className={styles.text}>{children}</div> : null}
        {meta?.length ? (
          <dl className={styles.meta}>
            {meta.map((row) => <div key={row.label}><dt>{row.label}</dt><dd>{row.value}</dd></div>)}
          </dl>
        ) : null}
      </div>
    </article>
  );
}
