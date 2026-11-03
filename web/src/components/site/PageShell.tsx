import type { ReactNode } from "react";
import { SiteFooter, SiteHeader } from "./SiteChrome";
import styles from "./PageShell.module.css";

/**
 * Themed page frame for lists and tools that have migrated to the tokens: header and footer that
 * follow the theme, one main landmark, a title block and a content column up to 1200 px.
 */
export function PageShell({ eyebrow, title, lead, current, children }: {
  eyebrow?: string;
  title: string;
  lead?: ReactNode;
  /** Path that marks a primary navigation item as current; defaults to the real path. */
  current?: string;
  children: ReactNode;
}) {
  return (
    <div data-themed-page className={styles.page}>
      {/* Without JavaScript the streamed page stays in a hidden wrapper behind the loading screen.
          Reveal it and hide the loading screen, so filters, sorting and search (plain links and
          forms) work with scripts off. */}
      <noscript><style>{`body > [hidden]:has(> [data-themed-page]) { display: block !important; }
        body:has(> [hidden] > [data-themed-page]) > [data-themed-page] { display: none !important; }`}</style></noscript>
      <SiteHeader tone="auto" current={current} />
      <main id="main-content" tabIndex={-1} className={styles.main}>
        <header className={styles.hero}>
          {eyebrow ? <p className={styles.eyebrow}>{eyebrow}</p> : null}
          <h1>{title}</h1>
          {lead ? <div className={styles.lead}>{lead}</div> : null}
        </header>
        <div className={styles.content}>{children}</div>
      </main>
      <SiteFooter tone="auto" />
    </div>
  );
}
